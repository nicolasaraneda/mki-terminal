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
    "arm holdings", "micron", "samsung", "sk hynix", "hynix", "tsmc", "umc",
    "asml", "tokyo electron", "advantest", "infineon", "bhp", "freeport",
    "shin-etsu", "shin etsu", "sumco", "microsoft",
]
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


def _guardar_titular(conn, fecha, fuente, titular, url, tickers) -> bool:
    """Devuelve True si el titular era nuevo (no estaba antes). Los titulares
    irrelevantes para el sector (filtro de keywords/empresas) no se guardan:
    analizar ruido con IA cuesta dinero y ensucia el sentimiento."""
    if not es_titular_relevante(titular):
        return False
    try:
        conn.execute(
            "INSERT INTO titulares (fecha, fuente, titular, url, tickers) VALUES (?, ?, ?, ?, ?)",
            (fecha, fuente, titular, url, ",".join(tickers)),
        )
        return True
    except sqlite3.IntegrityError:
        return False


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
    conn = get_connection()
    nuevos = 0

    for ticker in EMPRESAS:
        feed = feedparser.parse(_url_yahoo(ticker))
        for entrada in feed.entries[:LIMITE_POR_FEED]:
            if _guardar_titular(
                conn, _fecha_entrada(entrada), "Yahoo Finance",
                entrada.get("title", "").strip(), entrada.get("link", ""), [ticker],
            ):
                nuevos += 1

    for nombre, tickers in _tickers_por_nombre().items():
        feed = feedparser.parse(_url_google_news(nombre))
        for entrada in feed.entries[:LIMITE_POR_FEED]:
            if _guardar_titular(
                conn, _fecha_entrada(entrada), "Google News",
                entrada.get("title", "").strip(), entrada.get("link", ""), tickers,
            ):
                nuevos += 1

    for query in QUERIES_GENERALES:
        feed = feedparser.parse(_url_google_news(query))
        for entrada in feed.entries[:LIMITE_POR_FEED]:
            if _guardar_titular(
                conn, _fecha_entrada(entrada), "Google News",
                entrada.get("title", "").strip(), entrada.get("link", ""), [],
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
                    "explicacion": {"type": "string"},
                },
                "required": ["id", "sentimiento", "tickers_afectados", "impacto_estimado", "explicacion"],
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
        "la sugerida), impacto_estimado (alto/medio/bajo), y explicacion (1 línea en español)."
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
           (titular_id, sentimiento, tickers_afectados, impacto_estimado, explicacion, analizado_en)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            resultado["id"],
            resultado["sentimiento"],
            ",".join(resultado["tickers_afectados"]),
            resultado["impacto_estimado"],
            resultado["explicacion"],
            datetime.now(timezone.utc).isoformat(),
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
    """Titulares ya analizados donde la IA marcó este ticker específico como afectado."""
    todos = obtener_titulares_analizados(limite=1000)
    resultado = []
    for fila in todos:
        tickers_lista = [t.strip() for t in (fila["Tickers afectados"] or "").split(",") if t.strip()]
        if ticker in tickers_lista:
            resultado.append(fila)
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
    """Sentimiento por ticker con decaimiento temporal: promedio de los titulares
    analizados, ponderado por edad de cada noticia (hoy pesa 1.0; cada día le
    quita 30%; piso 0.1). Lo de esta mañana manda; lo del mes pasado apenas suma."""
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT a.tickers_afectados, a.sentimiento, t.fecha
        FROM analisis a JOIN titulares t ON t.id = a.titular_id
    """).fetchall()
    conn.close()
    suma: dict = {}
    peso_total: dict = {}
    for tickers_str, sentimiento, fecha_titular in filas:
        peso = _peso_por_antiguedad(fecha_titular)
        for ticker in filter(None, tickers_str.split(",")):
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
    valores = sentimiento_promedio_por_ticker()
    if not valores:
        return None
    return sum(valores.values()) / len(valores)
