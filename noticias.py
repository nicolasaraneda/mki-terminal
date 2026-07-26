# ============================================================
# Etapa 3 - Módulo de noticias + análisis con IA
#   1) Descarga titulares por RSS (Yahoo Finance + Google News)
#   2) Los guarda en SQLite, deduplicados por URL
#   3) Analiza con Claude (Haiku) los titulares nuevos y cachea
#      el resultado para nunca volver a pagar por el mismo titular
# ============================================================

import json
import os
import re
import sqlite3
from datetime import date, datetime, timezone

import feedparser

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "noticias.db")

MODELO_IA = "claude-haiku-4-5"
PRECIO_INPUT_POR_MTOK = 1.00   # USD por 1M tokens de entrada (Haiku 4.5)
PRECIO_OUTPUT_POR_MTOK = 5.00  # USD por 1M tokens de salida (Haiku 4.5)

# ------------------------------------------------------------
# Universo de empresas para buscar noticias (mismos tickers que app.py).
# Varios tickers pueden compartir la misma empresa (ej. TSM y 2330.TW),
# así que agrupamos por nombre para no repetir la misma búsqueda en Google News.
# ------------------------------------------------------------
EMPRESAS = {
    "NVDA": "NVIDIA",
    "AMD": "AMD",
    "INTC": "Intel",
    "QCOM": "Qualcomm",
    "AVGO": "Broadcom",
    "TXN": "Texas Instruments",
    "ARM": "Arm Holdings",
    "MU": "Micron",
    "005930.KS": "Samsung Electronics",
    "000660.KS": "SK Hynix",
    "TSM": "TSMC",
    "2330.TW": "TSMC",
    "UMC": "UMC",
    "ASML": "ASML",
    "8035.T": "Tokyo Electron",
    "6857.T": "Advantest",
    "IFX.DE": "Infineon",
    # Etapa 4.5: cadena vertical (minería, materiales, demanda final)
    "BHP": "BHP Group",
    "FCX": "Freeport-McMoRan",
    "4063.T": "Shin-Etsu Chemical",
    "3436.T": "SUMCO",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "META": "Meta Platforms",
}

# Búsquedas generales del sector, no atadas a un ticker específico
QUERIES_GENERALES = ["semiconductors DRAM", "semiconductor industry chip stocks"]

# Yahoo Finance mezcla noticias generales del mercado con las del ticker pedido, y
# Google News puede devolver ~100 resultados por búsqueda. Para no acumular miles de
# titulares viejos (y no pagarle a la IA por analizarlos todos), nos quedamos solo con
# los más recientes de cada fuente; el análisis de IA luego filtra cuáles son relevantes.
LIMITE_POR_FEED = 15

# ------------------------------------------------------------
# Filtro de relevancia (Etapa 4.5): un titular solo entra a la base si menciona
# una empresa del universo o un término del sector. Sin esto, el feed de Yahoo
# mete titulares de P&G, XRP o SpaceX que solo gastan dinero al analizarse.
# ------------------------------------------------------------
KEYWORDS_SECTOR = [
    "semiconductor", "semiconductors", "chip", "chips", "chipmaker", "chipmakers",
    "dram", "hbm", "nand", "foundry", "foundries", "fab", "fabs", "lithography",
    "euv", "wafer", "wafers", "silicon", "gpu", "gpus", "cpu", "cpus",
    "data center", "data centers", "datacenter", "datacenters",
    "copper", "silver", "smelter", "mining",
]
ALIAS_EMPRESAS = [
    "nvidia", "amd", "intel", "qualcomm", "broadcom", "texas instruments",
    "arm holdings", "micron", "samsung", "sk hynix", "hynix", "tsmc",
    "taiwan semiconductor", "umc", "united microelectronics",
    "asml", "tokyo electron", "advantest", "infineon", "bhp", "freeport",
    "shin-etsu", "shin etsu", "sumco", "microsoft", "alphabet", "google",
    "meta platforms",
]

# ------------------------------------------------------------
# Matching estricto por entidad (Etapa 4.6): un titular se asigna a un
# ticker SOLO si menciona a la empresa (o su ticker) de forma inequívoca.
# Los titulares sectoriales genéricos van al bucket "sector": alimentan el
# sentimiento sectorial, nunca el de una acción específica. Esta es la
# única vía por la que un titular puede aparecer en la ficha de una acción
# (el caso "XRP en la ficha de NVIDIA" queda estructuralmente imposible).
# ------------------------------------------------------------
ALIAS_POR_TICKER = {
    "NVDA": ["nvidia", "nvda"],
    "AMD": ["amd", "advanced micro devices"],
    "INTC": ["intel", "intc"],
    "QCOM": ["qualcomm", "qcom"],
    "AVGO": ["broadcom", "avgo"],
    "TXN": ["texas instruments"],
    "ARM": ["arm holdings"],
    "MU": ["micron"],
    "005930.KS": ["samsung electronics", "samsung"],
    "000660.KS": ["sk hynix", "hynix"],
    "TSM": ["tsmc", "taiwan semiconductor"],
    "2330.TW": ["tsmc", "taiwan semiconductor"],
    "UMC": ["united microelectronics", "umc"],
    "ASML": ["asml"],
    "8035.T": ["tokyo electron"],
    "6857.T": ["advantest"],
    "IFX.DE": ["infineon"],
    "BHP": ["bhp"],
    "FCX": ["freeport-mcmoran", "freeport"],
    "4063.T": ["shin-etsu", "shin etsu"],
    "3436.T": ["sumco"],
    "MSFT": ["microsoft", "msft"],
    "GOOGL": ["alphabet", "google"],
    "META": ["meta platforms", "facebook", "meta"],
}
_PATRONES_TICKER = {
    t: re.compile(r"\b(" + "|".join(re.escape(a) for a in alias) + r")\b", re.IGNORECASE)
    for t, alias in ALIAS_POR_TICKER.items()
}


def tickers_estrictos(titular: str) -> list:
    """Tickers cuya empresa está mencionada de forma inequívoca en el titular.
    Lista vacía = titular sectorial genérico (bucket 'sector')."""
    texto = titular or ""
    return [t for t, patron in _PATRONES_TICKER.items() if patron.search(texto)]


def _normalizar_titular(titular: str) -> str:
    """Normaliza para deduplicación: minúsculas, sin puntuación ni espacios extra."""
    limpio = re.sub(r"[^a-z0-9 ]", " ", (titular or "").lower())
    return re.sub(r"\s+", " ", limpio).strip()
_PATRON_RELEVANCIA = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in KEYWORDS_SECTOR + ALIAS_EMPRESAS) + r")\b",
    re.IGNORECASE,
)

# Sentimiento 2.0: decaimiento temporal. Una noticia de hoy pesa 1.0; cada día
# le quita 30% de peso, con un piso de 0.1 (lo viejo nunca desaparece del todo,
# pero pesa poco).
DECAIMIENTO_DIARIO = 0.7
PISO_PESO = 0.1

# Alto buzz: una acción con 3x su promedio diario de titulares está "en boca de todos"
FACTOR_BUZZ = 3.0
MINIMO_TITULARES_BUZZ = 3


def es_titular_relevante(titular: str) -> bool:
    """True si el titular menciona una empresa del universo o un término del sector."""
    return bool(_PATRON_RELEVANCIA.search(titular or ""))


def _tickers_por_nombre() -> dict:
    """Agrupa tickers que comparten el mismo nombre de empresa."""
    agrupado = {}
    for ticker, nombre in EMPRESAS.items():
        agrupado.setdefault(nombre, []).append(ticker)
    return agrupado


# ------------------------------------------------------------
# Base de datos
# ------------------------------------------------------------
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS titulares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            fuente TEXT NOT NULL,
            titular TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            tickers TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analisis (
            titular_id INTEGER PRIMARY KEY REFERENCES titulares(id),
            sentimiento REAL NOT NULL,
            tickers_afectados TEXT NOT NULL DEFAULT '',
            impacto_estimado TEXT NOT NULL,
            explicacion TEXT NOT NULL,
            analizado_en TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resumen_dia (
            fecha TEXT PRIMARY KEY,
            resumen TEXT NOT NULL,
            generado_en TEXT NOT NULL
        )
    """)
    # Migración 4.6: relevancia (0-1) asignada por la IA por titular. Las filas
    # antiguas quedan en NULL y se tratan como 1.0 (sin castigo retroactivo).
    columnas_analisis = {f[1] for f in conn.execute("PRAGMA table_info(analisis)").fetchall()}
    if "relevancia" not in columnas_analisis:
        conn.execute("ALTER TABLE analisis ADD COLUMN relevancia REAL")
    conn.commit()
    conn.close()


# ------------------------------------------------------------
# Descarga de titulares por RSS
# ------------------------------------------------------------
def _url_yahoo(ticker: str) -> str:
    return f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"


def _url_google_news(query: str) -> str:
    consulta = query.replace(" ", "+")
    return f"https://news.google.com/rss/search?q={consulta}&hl=en-US&gl=US&ceid=US:en"


def _fecha_entrada(entrada) -> str:
    if getattr(entrada, "published_parsed", None):
        return datetime(*entrada.published_parsed[:6], tzinfo=timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


UMBRAL_SIMILITUD_DUP = 0.85  # difflib ratio sobre titulares normalizados


def _es_duplicado(titular: str, titulares_recientes: list) -> bool:
    """True si el titular es esencialmente el mismo evento que uno ya guardado
    (mismo evento desde dos fuentes = una sola entrada)."""
    import difflib
    normalizado = _normalizar_titular(titular)
    if not normalizado:
        return False
    for existente in titulares_recientes:
        if difflib.SequenceMatcher(None, normalizado, existente).ratio() > UMBRAL_SIMILITUD_DUP:
            return True
    return False


def _guardar_titular(conn, fecha, fuente, titular, url, tickers_hint,
                     titulares_recientes=None) -> bool:
    """Devuelve True si el titular era nuevo. Tres filtros de entrada:
    (1) relevancia sectorial (keywords/empresas — el ruido no se guarda),
    (2) deduplicación por similitud (mismo evento desde dos fuentes),
    (3) la asignación a tickers es por MATCHING ESTRICTO de entidad en el
        texto del titular — el hint del feed de origen se ignora (Yahoo mete
        noticias ajenas en el feed de cualquier ticker). Sin match estricto,
        el titular queda en el bucket 'sector' (tickers='')."""
    if not es_titular_relevante(titular):
        return False
    if titulares_recientes is not None and _es_duplicado(titular, titulares_recientes):
        return False
    tickers = tickers_estrictos(titular)
    try:
        conn.execute(
            "INSERT INTO titulares (fecha, fuente, titular, url, tickers) VALUES (?, ?, ?, ?, ?)",
            (fecha, fuente, titular, url, ",".join(tickers)),
        )
        if titulares_recientes is not None:
            titulares_recientes.append(_normalizar_titular(titular))
        return True
    except sqlite3.IntegrityError:
        return False


def migrar_noticias_v2() -> dict:
    """Limpieza retroactiva Etapa 4.6 (idempotente):
    1) Regraba la columna tickers de TODOS los titulares con matching estricto
       de entidad (el hint del feed de origen deja de existir hacia atrás).
    2) Deduplica por similitud de titular (difflib > 0.85 sobre normalizados),
       conservando la entrada más antigua y borrando las réplicas con su análisis.
    Devuelve {"retagueados": n, "duplicados_borrados": m}."""
    import difflib
    init_db()
    conn = get_connection()

    retagueados = 0
    for id_, titular, tickers_viejos in conn.execute(
            "SELECT id, titular, tickers FROM titulares").fetchall():
        estrictos = ",".join(tickers_estrictos(titular))
        if estrictos != (tickers_viejos or ""):
            conn.execute("UPDATE titulares SET tickers = ? WHERE id = ?",
                         (estrictos, id_))
            retagueados += 1

    filas = conn.execute(
        "SELECT id, titular FROM titulares ORDER BY fecha ASC, id ASC").fetchall()
    vistos = []  # titulares normalizados ya aceptados — el más antiguo sobrevive
    duplicados = []
    for id_, titular in filas:
        normalizado = _normalizar_titular(titular)
        if not normalizado:
            continue
        es_dup = any(
            difflib.SequenceMatcher(None, normalizado, previo).ratio() > UMBRAL_SIMILITUD_DUP
            for previo in vistos
        )
        if es_dup:
            duplicados.append(id_)
        else:
            vistos.append(normalizado)
    for id_ in duplicados:
        conn.execute("DELETE FROM analisis WHERE titular_id = ?", (id_,))
        conn.execute("DELETE FROM titulares WHERE id = ?", (id_,))

    conn.commit()
    conn.close()
    return {"retagueados": retagueados, "duplicados_borrados": len(duplicados)}


def limpiar_titulares_irrelevantes() -> int:
    """Limpieza retroactiva de la base: borra titulares ya guardados que no pasan
    el filtro de relevancia — salvo los que la IA ya analizó marcando tickers del
    universo como afectados (esos demostraron ser relevantes aunque el titular no
    mencione keywords). Idempotente: correrla dos veces no borra nada nuevo.
    Devuelve cuántos titulares se eliminaron."""
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT t.id, t.titular, a.tickers_afectados
        FROM titulares t LEFT JOIN analisis a ON a.titular_id = t.id
    """).fetchall()
    universo = set(EMPRESAS.keys())
    a_borrar = []
    for id_, titular, tickers_afectados in filas:
        if es_titular_relevante(titular):
            continue
        afectados = {x.strip() for x in (tickers_afectados or "").split(",") if x.strip()}
        if afectados & universo:
            continue  # la IA lo vinculó a empresas del universo: se queda
        a_borrar.append(id_)
    for id_ in a_borrar:
        conn.execute("DELETE FROM analisis WHERE titular_id = ?", (id_,))
        conn.execute("DELETE FROM titulares WHERE id = ?", (id_,))
    conn.commit()
    conn.close()
    return len(a_borrar)


def actualizar_titulares() -> int:
    """Descarga RSS de Yahoo Finance (por ticker) y Google News (por empresa/sector).
    Guarda los titulares nuevos en SQLite. Devuelve cuántos titulares nuevos se agregaron."""
    init_db()
    migrar_noticias_v2()  # idempotente: asegura matching estricto y dedup retroactivos
    conn = get_connection()
    nuevos = 0

    # Titulares recientes normalizados (10 días) para deduplicar por similitud
    recientes = [
        _normalizar_titular(f[0]) for f in conn.execute(
            "SELECT titular FROM titulares WHERE fecha >= datetime('now', '-10 days')"
        ).fetchall()
    ]

    for ticker in EMPRESAS:
        feed = feedparser.parse(_url_yahoo(ticker))
        for entrada in feed.entries[:LIMITE_POR_FEED]:
            if _guardar_titular(
                conn, _fecha_entrada(entrada), "Yahoo Finance",
                entrada.get("title", "").strip(), entrada.get("link", ""), None,
                titulares_recientes=recientes,
            ):
                nuevos += 1

    for nombre, _tk in _tickers_por_nombre().items():
        feed = feedparser.parse(_url_google_news(nombre))
        for entrada in feed.entries[:LIMITE_POR_FEED]:
            if _guardar_titular(
                conn, _fecha_entrada(entrada), "Google News",
                entrada.get("title", "").strip(), entrada.get("link", ""), None,
                titulares_recientes=recientes,
            ):
                nuevos += 1

    for query in QUERIES_GENERALES:
        feed = feedparser.parse(_url_google_news(query))
        for entrada in feed.entries[:LIMITE_POR_FEED]:
            if _guardar_titular(
                conn, _fecha_entrada(entrada), "Google News",
                entrada.get("title", "").strip(), entrada.get("link", ""), None,
                titulares_recientes=recientes,
            ):
                nuevos += 1

    conn.commit()
    conn.close()
    # Mantiene la base limpia también hacia atrás (idempotente y barato)
    limpiar_titulares_irrelevantes()
    return nuevos


# ------------------------------------------------------------
# Análisis con Claude
# ------------------------------------------------------------
_ESQUEMA_ANALISIS = {
    "type": "object",
    "properties": {
        "resultados": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "sentimiento": {"type": "number"},
                    "tickers_afectados": {"type": "array", "items": {"type": "string"}},
                    "impacto_estimado": {"type": "string", "enum": ["alto", "medio", "bajo"]},
                    "relevancia": {"type": "number"},
                    "explicacion": {"type": "string"},
                },
                "required": ["id", "sentimiento", "tickers_afectados", "impacto_estimado", "relevancia", "explicacion"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["resultados"],
    "additionalProperties": False,
}


def obtener_titulares_sin_analizar(conn) -> list:
    filas = conn.execute("""
        SELECT t.id, t.titular, t.tickers FROM titulares t
        LEFT JOIN analisis a ON a.titular_id = t.id
        WHERE a.titular_id IS NULL
        ORDER BY t.fecha DESC
    """).fetchall()
    return [{"id": f[0], "titular": f[1], "tickers": f[2]} for f in filas]


def _costo_estimado(usage) -> float:
    return (usage.input_tokens / 1_000_000) * PRECIO_INPUT_POR_MTOK + (
        usage.output_tokens / 1_000_000
    ) * PRECIO_OUTPUT_POR_MTOK


def _analizar_lote(client, lote: list):
    lista_titulares = "\n".join(
        f"- id={item['id']}: \"{item['titular']}\" (tickers relacionados: {item['tickers'] or 'ninguno'})"
        for item in lote
    )
    prompt = (
        "Eres un analista financiero especializado en el sector de semiconductores. "
        "Para cada titular de noticias a continuación, evalúa su sentimiento e impacto "
        "para las acciones de semiconductores mencionadas o relacionadas.\n\n"
        f"{lista_titulares}\n\n"
        "Para cada titular, entrega: sentimiento (-1.0 muy negativo a +1.0 muy positivo), "
        "tickers_afectados (lista de tickers que consideres afectados, puede ser distinta a "
        "la sugerida), impacto_estimado (alto/medio/bajo), relevancia (0.0 a 1.0: cuán "
        "central es este titular para el sector de semiconductores y su cadena de valor — "
        "1.0 = noticia de núcleo del sector, 0.2 = mención tangencial), y explicacion "
        "(1 línea en español)."
    )
    response = client.messages.create(
        model=MODELO_IA,
        max_tokens=4096,
        output_config={"format": {"type": "json_schema", "schema": _ESQUEMA_ANALISIS}},
        messages=[{"role": "user", "content": prompt}],
    )
    texto = next(b.text for b in response.content if b.type == "text")
    resultados = json.loads(texto)["resultados"]
    return resultados, response.usage


def guardar_analisis(conn, resultado: dict) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO analisis
           (titular_id, sentimiento, tickers_afectados, impacto_estimado, explicacion,
            analizado_en, relevancia)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            resultado["id"],
            resultado["sentimiento"],
            ",".join(resultado["tickers_afectados"]),
            resultado["impacto_estimado"],
            resultado["explicacion"],
            datetime.now(timezone.utc).isoformat(),
            max(0.0, min(1.0, float(resultado.get("relevancia", 1.0)))),
        ),
    )


def analizar_pendientes(client, batch_size: int = 20) -> tuple:
    """Analiza con Claude todos los titulares sin analizar, en lotes.
    Devuelve (cantidad_analizada, costo_estimado_usd)."""
    init_db()
    conn = get_connection()
    pendientes = obtener_titulares_sin_analizar(conn)
    total_analizados = 0
    costo_total = 0.0

    for i in range(0, len(pendientes), batch_size):
        lote = pendientes[i : i + batch_size]
        resultados, usage = _analizar_lote(client, lote)
        for r in resultados:
            guardar_analisis(conn, r)
        conn.commit()
        total_analizados += len(resultados)
        costo_total += _costo_estimado(usage)

    conn.close()
    return total_analizados, costo_total


# ------------------------------------------------------------
# Resumen del día (lenguaje natural)
# ------------------------------------------------------------
def generar_resumen_dia(client) -> str:
    init_db()
    conn = get_connection()
    hoy = date.today().isoformat()

    filas = conn.execute("""
        SELECT t.titular, a.sentimiento, a.tickers_afectados, a.impacto_estimado, a.explicacion
        FROM analisis a JOIN titulares t ON t.id = a.titular_id
        WHERE date(a.analizado_en) = date('now')
        ORDER BY a.sentimiento ASC
    """).fetchall()

    if not filas:
        conn.close()
        return "Sin titulares analizados hoy. Presiona 'Actualizar y analizar noticias' para generar el resumen."

    contexto = "\n".join(
        f"- \"{f[0]}\" | sentimiento={f[1]:+.2f} | impacto={f[3]} | tickers={f[2] or 'sector general'} | {f[4]}"
        for f in filas
    )
    prompt = (
        "Eres un analista financiero. Con base en este listado de titulares ya analizados "
        "del sector de semiconductores de hoy, escribe un resumen del día en español, de 3 a 5 "
        "frases, en lenguaje natural: qué está moviendo al sector y por qué. No repitas los "
        "titulares palabra por palabra, sintetiza. Responde en texto plano puro, sin ningún "
        "formato markdown: sin título, sin encabezados ('#'), sin negritas ni cursivas "
        "('*', '**', '_'), y sin usar el símbolo '$' (escribe 'USD' en su lugar si mencionas "
        "montos).\n\n" + contexto
    )
    response = client.messages.create(
        model=MODELO_IA, max_tokens=500, messages=[{"role": "user", "content": prompt}],
    )
    resumen = next(b.text for b in response.content if b.type == "text").strip()

    conn.execute(
        "INSERT OR REPLACE INTO resumen_dia (fecha, resumen, generado_en) VALUES (?, ?, ?)",
        (hoy, resumen, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return resumen


def titulares_top_relevancia(n: int = 3) -> list:
    """Los titulares analizados HOY con mayor relevancia (para el reporte
    sellado de la Etapa 5.0). Solo lectura del cache — cero llamadas a IA.

    Con filtro de DIVERSIDAD en la selección: el mismo evento desde dos
    fuentes (que el dedup de guardado no atrapó por redacción distinta) no
    ocupa dos de los n cupos. Umbral más laxo que el de guardado (0.55 vs
    0.85) porque aquí descartar de más es barato: hay reemplazo."""
    import difflib
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT t.titular, a.sentimiento, COALESCE(a.relevancia, 1.0) AS relevancia
        FROM analisis a JOIN titulares t ON t.id = a.titular_id
        WHERE date(a.analizado_en) = date('now')
        ORDER BY relevancia DESC, ABS(a.sentimiento) DESC
        LIMIT ?""", (n * 4,)).fetchall()
    conn.close()
    def _parecidos(x: str, y: str) -> bool:
        # SequenceMatcher NO es simétrico (0.57 vs 0.49 en un caso real):
        # se evalúan ambos órdenes y decide el mayor.
        return max(difflib.SequenceMatcher(None, x, y).ratio(),
                   difflib.SequenceMatcher(None, y, x).ratio()) > 0.55

    elegidos = []
    for titular, sentimiento, relevancia in filas:
        norm = _normalizar_titular(titular)
        if any(_parecidos(norm, _normalizar_titular(e["titular"]))
               for e in elegidos):
            continue
        elegidos.append({"titular": titular, "sentimiento": sentimiento,
                         "relevancia": relevancia})
        if len(elegidos) == n:
            break
    return elegidos


def obtener_resumen_guardado() -> str | None:
    init_db()
    conn = get_connection()
    fila = conn.execute(
        "SELECT resumen FROM resumen_dia WHERE fecha = date('now')"
    ).fetchone()
    conn.close()
    return fila[0] if fila else None


# ------------------------------------------------------------
# Consultas para el dashboard
# ------------------------------------------------------------
def obtener_titulares_analizados(limite: int = 200):
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT t.fecha, t.fuente, t.titular, t.url, a.sentimiento, a.tickers_afectados,
               a.impacto_estimado, a.explicacion
        FROM analisis a JOIN titulares t ON t.id = a.titular_id
        ORDER BY t.fecha DESC LIMIT ?
    """, (limite,)).fetchall()
    conn.close()
    columnas = ["Fecha", "Fuente", "Titular", "URL", "Sentimiento", "Tickers afectados",
                "Impacto", "Explicación"]
    return [dict(zip(columnas, f)) for f in filas]


def obtener_titulares_por_ticker(ticker: str, limite: int = 30) -> list:
    """Titulares para la ficha de una acción — SOLO por matching estricto de
    entidad: el titular debe mencionar a la empresa de forma inequívoca.
    (Regla 4.6: un titular de XRP jamás puede aparecer en la ficha de NVIDIA.)
    Doble defensa: filtra por la columna tickers (regrabada con matching
    estricto en la migración v2) Y re-verifica el matching en vivo."""
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT t.fecha, t.fuente, t.titular, t.url, a.sentimiento,
               t.tickers, a.impacto_estimado, a.explicacion, a.relevancia
        FROM analisis a JOIN titulares t ON t.id = a.titular_id
        ORDER BY t.fecha DESC LIMIT 1000
    """).fetchall()
    conn.close()
    resultado = []
    for f in filas:
        tickers_col = {x.strip() for x in (f[5] or "").split(",") if x.strip()}
        if ticker not in tickers_col:
            continue
        if ticker not in tickers_estrictos(f[2]):
            continue  # defensa en vivo: la entidad DEBE estar en el texto
        resultado.append({
            "Fecha": f[0], "Fuente": f[1], "Titular": f[2], "URL": f[3],
            "Sentimiento": f[4], "Tickers afectados": f[5],
            "Impacto": f[6], "Explicación": f[7], "Relevancia": f[8],
        })
        if len(resultado) >= limite:
            break
    return resultado


def explicar_accion(client, ticker: str, nombre_empresa: str, metricas: dict, titulares: list) -> str:
    """Genera con Claude una explicación breve de por qué una acción está en su
    situación actual, combinando sus métricas cuantitativas y sus noticias recientes."""
    resumen_metricas = (
        f"Retorno del período: {metricas.get('retorno_pct', 0):+.1f}%, "
        f"Momentum 20 días: {metricas.get('momentum_pct', 0):+.1f}%, "
        f"Volatilidad anual: {metricas.get('volatilidad_pct', 0):.1f}%, "
        f"Puntaje v0 (ranking cuantitativo, 0 a 1): {metricas.get('puntaje_v0', 0):.2f}."
    )
    if metricas.get("sentimiento_ia") is not None:
        resumen_metricas += (
            f" Sentimiento IA de noticias: {metricas['sentimiento_ia']:+.2f} (de -1 a +1)."
        )

    if titulares:
        lista_titulares = "\n".join(
            f"- \"{t['Titular']}\" (sentimiento={t['Sentimiento']:+.2f}, impacto={t['Impacto']})"
            for t in titulares[:8]
        )
    else:
        lista_titulares = "(sin noticias analizadas recientes para esta acción)"

    prompt = (
        f"Eres un analista financiero. Con estos datos de {nombre_empresa} ({ticker}):\n"
        f"{resumen_metricas}\n\nTitulares recientes:\n{lista_titulares}\n\n"
        "Escribe una explicación breve (3 a 4 frases) en español de por qué esta acción "
        "está en su situación actual, combinando los datos cuantitativos y el contexto "
        "de noticias. Sé específico, evita frases genéricas. Responde en texto plano, "
        "sin ningún formato markdown (nada de '#', '*', '**', '_') y sin usar el símbolo "
        "'$' (escribe 'USD' en su lugar)."
    )
    response = client.messages.create(
        model=MODELO_IA, max_tokens=400, messages=[{"role": "user", "content": prompt}],
    )
    return next(b.text for b in response.content if b.type == "text").strip()


def _peso_por_antiguedad(fecha_titular: str) -> float:
    """Peso de una noticia según su edad: hoy = 1.0, cada día resta 30%
    (decaimiento 0.7^días), con piso de 0.1."""
    try:
        dias = (date.today() - date.fromisoformat(str(fecha_titular)[:10])).days
    except (ValueError, TypeError):
        dias = 7  # fecha ilegible: pesa como noticia de hace una semana
    return max(PISO_PESO, DECAIMIENTO_DIARIO ** max(0, dias))


def sentimiento_promedio_por_ticker() -> dict:
    """Sentimiento POR ACCIÓN con doble ponderación: edad de la noticia
    (decaimiento 0.7^días, piso 0.1) × relevancia asignada por la IA (0-1;
    filas pre-4.6 sin relevancia pesan 1.0).

    Regla 4.6 de asignación: un titular solo aporta al sentimiento de una
    acción si menciona a la empresa de forma INEQUÍVOCA (columna tickers,
    regrabada con matching estricto). Los titulares sectoriales genéricos
    alimentan el sentimiento del sector, no el de acciones."""
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT t.tickers, a.sentimiento, t.fecha, a.relevancia
        FROM analisis a JOIN titulares t ON t.id = a.titular_id
    """).fetchall()
    conn.close()
    suma: dict = {}
    peso_total: dict = {}
    for tickers_str, sentimiento, fecha_titular, relevancia in filas:
        peso = _peso_por_antiguedad(fecha_titular) * (relevancia if relevancia is not None else 1.0)
        if peso <= 0:
            continue
        for ticker in filter(None, (tickers_str or "").split(",")):
            suma[ticker] = suma.get(ticker, 0.0) + sentimiento * peso
            peso_total[ticker] = peso_total.get(ticker, 0.0) + peso
    return {t: suma[t] / peso_total[t] for t in suma if peso_total[t] > 0}


def buzz_por_ticker() -> dict:
    """Detecta acciones con volumen inusual de noticias: si los titulares de las
    últimas 24 horas son >= FACTOR_BUZZ x el promedio diario de los 14 días
    anteriores (y al menos MINIMO_TITULARES_BUZZ), la acción está en ALTO BUZZ.

    Honestidad estadística: si la base de noticias tiene menos de 7 días de
    historia, el "promedio diario" no significa nada y NO se declara buzz
    (de lo contrario, en una base recién creada todo aparecería en buzz).
    Devuelve {ticker: {"hoy": n, "promedio_diario": x, "buzz": bool}}."""
    init_db()
    conn = get_connection()
    # La edad de la base se mide por cuándo empezamos a CAPTURAR (analizado_en),
    # no por la fecha de publicación de los titulares (el RSS trae noticias con
    # fechas de semanas atrás el primer día, lo que haría parecer vieja una base
    # recién creada).
    fila_min = conn.execute("SELECT MIN(analizado_en) FROM analisis").fetchone()
    filas = conn.execute("""
        SELECT a.tickers_afectados, t.fecha
        FROM analisis a JOIN titulares t ON t.id = a.titular_id
        WHERE t.fecha >= datetime('now', '-15 days')
    """).fetchall()
    conn.close()

    historia_suficiente = False
    if fila_min and fila_min[0]:
        try:
            edad_base = (date.today() - date.fromisoformat(str(fila_min[0])[:10])).days
            historia_suficiente = edad_base >= 7
        except (ValueError, TypeError):
            pass

    hoy_conteo: dict = {}
    historico_conteo: dict = {}
    for tickers_str, fecha_titular in filas:
        try:
            dias = (date.today() - date.fromisoformat(str(fecha_titular)[:10])).days
        except (ValueError, TypeError):
            continue
        for ticker in filter(None, tickers_str.split(",")):
            if dias <= 1:
                hoy_conteo[ticker] = hoy_conteo.get(ticker, 0) + 1
            else:
                historico_conteo[ticker] = historico_conteo.get(ticker, 0) + 1
    resultado = {}
    for ticker in set(hoy_conteo) | set(historico_conteo):
        n_hoy = hoy_conteo.get(ticker, 0)
        promedio = historico_conteo.get(ticker, 0) / 14
        buzz = (historia_suficiente
                and n_hoy >= MINIMO_TITULARES_BUZZ
                and (promedio == 0 or n_hoy >= FACTOR_BUZZ * promedio))
        resultado[ticker] = {"hoy": n_hoy, "promedio_diario": round(promedio, 2),
                             "buzz": buzz}
    return resultado


def sentimiento_promedio_sector() -> float | None:
    """Sentimiento del SECTOR: media ponderada (edad × relevancia) de TODOS los
    titulares analizados — incluidos los del bucket 'sector' que no se asignan
    a ninguna acción específica."""
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT a.sentimiento, t.fecha, a.relevancia
        FROM analisis a JOIN titulares t ON t.id = a.titular_id
    """).fetchall()
    conn.close()
    suma, peso_total = 0.0, 0.0
    for sentimiento, fecha_titular, relevancia in filas:
        peso = _peso_por_antiguedad(fecha_titular) * (relevancia if relevancia is not None else 1.0)
        suma += sentimiento * peso
        peso_total += peso
    return suma / peso_total if peso_total > 0 else None
