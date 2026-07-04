# ============================================================
# Etapa 4 - Historial de señales y verificador de aciertos
#   1) Cada día (máx. 1 vez), guarda una foto: Puntaje v0, sentimiento IA,
#      Puntaje IA y la predicción del anticipador por acción.
#   2) Al día siguiente (o 5 sesiones después, según corresponda), compara
#      cada predicción contra lo que realmente pasó, usando yfinance.
# ============================================================

import os
import sqlite3
from datetime import date, datetime, timezone

import pandas as pd
import yfinance as yf

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "senales.db")

DIAS_FORWARD_PUNTAJE = 5  # sesiones hábiles para evaluar el Puntaje IA
MINIMO_OBSERVACIONES = 5  # bajo este umbral, mostramos "datos insuficientes"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            fecha TEXT PRIMARY KEY,
            creado_en TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS senales_ticker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            ticker TEXT NOT NULL,
            puntaje_v0 REAL,
            sentimiento_ia REAL,
            puntaje_ia REAL,
            apertura_estimada_pct REAL,
            confianza_r2 REAL,
            UNIQUE(fecha, ticker)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS verificacion_apertura (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_senal TEXT NOT NULL,
            ticker TEXT NOT NULL,
            apertura_estimada_pct REAL NOT NULL,
            retorno_real_pct REAL NOT NULL,
            acierto_direccion INTEGER NOT NULL,
            error_pp REAL NOT NULL,
            verificado_en TEXT NOT NULL,
            UNIQUE(fecha_senal, ticker)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS verificacion_puntaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_senal TEXT NOT NULL,
            ticker TEXT NOT NULL,
            puntaje_ia REAL NOT NULL,
            retorno_5d_pct REAL NOT NULL,
            verificado_en TEXT NOT NULL,
            UNIQUE(fecha_senal, ticker)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS divergencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            par TEXT NOT NULL,
            spread_20d_pct REAL NOT NULL,
            z_score REAL NOT NULL,
            explicacion TEXT NOT NULL DEFAULT '',
            UNIQUE(fecha, par)
        )
    """)
    # Migración suave (Etapa 4.5): columnas nuevas del snapshot. ALTER TABLE de
    # SQLite no tiene IF NOT EXISTS, así que se consulta el esquema primero.
    columnas_snapshot = {f[1] for f in conn.execute("PRAGMA table_info(snapshots)").fetchall()}
    if "regimen" not in columnas_snapshot:
        conn.execute("ALTER TABLE snapshots ADD COLUMN regimen TEXT")
    if "roca_chip" not in columnas_snapshot:
        conn.execute("ALTER TABLE snapshots ADD COLUMN roca_chip REAL")
    conn.commit()
    conn.close()


# ------------------------------------------------------------
# Snapshot diario
# ------------------------------------------------------------
def ya_existe_snapshot_hoy() -> bool:
    init_db()
    conn = get_connection()
    hoy = date.today().isoformat()
    existe = conn.execute("SELECT 1 FROM snapshots WHERE fecha = ?", (hoy,)).fetchone()
    conn.close()
    return existe is not None


def guardar_snapshot_diario(metricas_df: pd.DataFrame, sentimientos: dict,
                            df_apertura: pd.DataFrame, regimen: str = None,
                            roca_chip: float = None, divergencias: list = None) -> bool:
    """Guarda una foto del día (máximo 1 vez/día) con Puntaje v0, sentimiento IA,
    Puntaje IA y la predicción del anticipador, por acción — más el contexto del día:
    régimen de mercado, índice Roca→Chip y divergencias activas entre competidores.
    `metricas_df` debe cubrir TODO el universo de acciones (no solo la selección del
    sidebar). Devuelve True si guardó algo."""
    if ya_existe_snapshot_hoy() or metricas_df.empty:
        return False
    init_db()
    conn = get_connection()
    hoy = date.today().isoformat()
    ahora = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO snapshots (fecha, creado_en, regimen, roca_chip) VALUES (?, ?, ?, ?)",
        (hoy, ahora, regimen, roca_chip),
    )
    for div in divergencias or []:
        conn.execute(
            """INSERT OR IGNORE INTO divergencias (fecha, par, spread_20d_pct, z_score, explicacion)
               VALUES (?, ?, ?, ?, ?)""",
            (hoy, div["par"], div["spread"], div["z"], div.get("explicacion", "")),
        )

    apertura_por_ticker = {}
    if df_apertura is not None and not df_apertura.empty:
        for _, fila in df_apertura.iterrows():
            apertura_por_ticker[fila["Ticker"]] = (fila["Apertura estimada %"], fila["R2"])

    for _, fila in metricas_df.iterrows():
        ticker = fila["Ticker"]
        puntaje_v0 = float(fila["Puntaje v0"])
        sentimiento = sentimientos.get(ticker)
        puntaje_ia = None
        if sentimiento is not None:
            puntaje_ia = round(puntaje_v0 * 0.7 + ((sentimiento + 1) / 2) * 0.3, 4)
        apertura_pct, r2 = apertura_por_ticker.get(ticker, (None, None))
        conn.execute(
            """INSERT OR IGNORE INTO senales_ticker
               (fecha, ticker, puntaje_v0, sentimiento_ia, puntaje_ia,
                apertura_estimada_pct, confianza_r2)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (hoy, ticker, puntaje_v0, sentimiento, puntaje_ia, apertura_pct, r2),
        )
    conn.commit()
    conn.close()
    return True


# ------------------------------------------------------------
# Verificador: compara predicciones guardadas contra la realidad
# ------------------------------------------------------------
def _historial_precios(ticker: str, desde: str) -> pd.DataFrame:
    """Descarga el historial de precios de un ticker desde una fecha (para verificar)."""
    datos = yf.download(ticker, start=desde, auto_adjust=True, progress=False)
    if datos.empty:
        return pd.DataFrame()
    cierre = datos["Close"]
    if isinstance(cierre, pd.DataFrame):
        cierre = cierre.iloc[:, 0]
    return cierre.dropna().to_frame(name="Close")


def verificar_apertura_pendientes() -> int:
    """Compara cada predicción de apertura contra el retorno real del día siguiente
    (la primera sesión disponible después de la fecha de la señal). Devuelve cuántas
    predicciones nuevas se verificaron."""
    init_db()
    conn = get_connection()
    pendientes = conn.execute("""
        SELECT s.fecha, s.ticker, s.apertura_estimada_pct
        FROM senales_ticker s
        LEFT JOIN verificacion_apertura v ON v.fecha_senal = s.fecha AND v.ticker = s.ticker
        WHERE s.apertura_estimada_pct IS NOT NULL AND v.id IS NULL
        ORDER BY s.fecha
    """).fetchall()

    verificados = 0
    for fecha_senal, ticker, apertura_pct in pendientes:
        precios = _historial_precios(ticker, fecha_senal)
        if precios.empty:
            continue  # todavía no hay datos nuevos para este ticker
        precios = precios[precios.index.strftime("%Y-%m-%d") >= fecha_senal]
        if len(precios) < 2:
            continue  # aún no ha pasado una sesión más desde la señal
        retorno_real = (precios["Close"].iloc[1] / precios["Close"].iloc[0] - 1) * 100
        acierto = 1 if (apertura_pct >= 0) == (retorno_real >= 0) else 0
        error_pp = abs(apertura_pct - retorno_real)
        conn.execute(
            """INSERT OR IGNORE INTO verificacion_apertura
               (fecha_senal, ticker, apertura_estimada_pct, retorno_real_pct,
                acierto_direccion, error_pp, verificado_en)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (fecha_senal, ticker, apertura_pct, round(retorno_real, 4), acierto,
             round(error_pp, 4), datetime.now(timezone.utc).isoformat()),
        )
        verificados += 1
    conn.commit()
    conn.close()
    return verificados


def verificar_puntaje_pendientes() -> int:
    """Compara el Puntaje IA contra el retorno real de los DIAS_FORWARD_PUNTAJE días
    hábiles siguientes a la señal. Devuelve cuántas predicciones nuevas se verificaron."""
    init_db()
    conn = get_connection()
    pendientes = conn.execute("""
        SELECT s.fecha, s.ticker, s.puntaje_ia
        FROM senales_ticker s
        LEFT JOIN verificacion_puntaje v ON v.fecha_senal = s.fecha AND v.ticker = s.ticker
        WHERE s.puntaje_ia IS NOT NULL AND v.id IS NULL
        ORDER BY s.fecha
    """).fetchall()

    verificados = 0
    for fecha_senal, ticker, puntaje_ia in pendientes:
        precios = _historial_precios(ticker, fecha_senal)
        if precios.empty:
            continue  # todavía no hay datos nuevos para este ticker
        precios = precios[precios.index.strftime("%Y-%m-%d") >= fecha_senal]
        if len(precios) < DIAS_FORWARD_PUNTAJE + 1:
            continue  # aún no han pasado suficientes sesiones desde la señal
        retorno_5d = (precios["Close"].iloc[DIAS_FORWARD_PUNTAJE] / precios["Close"].iloc[0] - 1) * 100
        conn.execute(
            """INSERT OR IGNORE INTO verificacion_puntaje
               (fecha_senal, ticker, puntaje_ia, retorno_5d_pct, verificado_en)
               VALUES (?, ?, ?, ?, ?)""",
            (fecha_senal, ticker, puntaje_ia, round(retorno_5d, 4),
             datetime.now(timezone.utc).isoformat()),
        )
        verificados += 1
    conn.commit()
    conn.close()
    return verificados


def verificar_pendientes() -> tuple:
    """Corre ambos verificadores. Devuelve (n_apertura, n_puntaje) verificados."""
    return verificar_apertura_pendientes(), verificar_puntaje_pendientes()


# ------------------------------------------------------------
# Consultas para el dashboard (honestas: nunca inventan precisión)
# ------------------------------------------------------------
def metricas_apertura(dias: int = 30) -> dict:
    """% de aciertos de dirección, error promedio (pp) y N evaluadas, de los
    últimos `dias`. Si hay pocas observaciones, señala 'datos insuficientes'."""
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT acierto_direccion, error_pp FROM verificacion_apertura
        WHERE fecha_senal >= date('now', ?)
    """, (f"-{dias} days",)).fetchall()
    conn.close()
    n = len(filas)
    if n < MINIMO_OBSERVACIONES:
        return {"suficiente": False, "n": n}
    aciertos = sum(f[0] for f in filas)
    error_prom = sum(f[1] for f in filas) / n
    return {
        "suficiente": True, "n": n,
        "pct_aciertos": round(100 * aciertos / n, 1),
        "error_promedio_pp": round(error_prom, 2),
    }


def evolucion_aciertos_apertura() -> pd.DataFrame:
    """Serie diaria del % de aciertos (promedio del día) para graficar en el tiempo."""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT fecha_senal AS Fecha, AVG(acierto_direccion) * 100 AS "% Aciertos", COUNT(*) AS N
        FROM verificacion_apertura GROUP BY fecha_senal ORDER BY fecha_senal
    """, conn)
    conn.close()
    return df


def ultimas_predicciones_apertura(limite: int = 50) -> pd.DataFrame:
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT fecha_senal AS Fecha, ticker AS Ticker,
               apertura_estimada_pct AS "Estimado %", retorno_real_pct AS "Real %",
               acierto_direccion AS Acierto, error_pp AS "Error (pp)"
        FROM verificacion_apertura ORDER BY fecha_senal DESC LIMIT ?
    """, conn, params=(limite,))
    conn.close()
    return df


def analisis_puntaje_ia(dias: int = 90) -> dict:
    """¿Las acciones con mejor Puntaje IA rindieron mejor en los siguientes
    DIAS_FORWARD_PUNTAJE días hábiles? Compara el promedio de retorno del tercio
    superior de Puntaje IA vs. el tercio inferior. Honesto: exige un mínimo de datos."""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT puntaje_ia AS puntaje, retorno_5d_pct AS retorno
        FROM verificacion_puntaje WHERE fecha_senal >= date('now', ?)
    """, conn, params=(f"-{dias} days",))
    conn.close()
    n = len(df)
    if n < MINIMO_OBSERVACIONES:
        return {"suficiente": False, "n": n, "datos": df}
    df = df.sort_values("puntaje")
    corte = max(1, n // 3)
    tercio_bajo = df.iloc[:corte]["retorno"].mean()
    tercio_alto = df.iloc[-corte:]["retorno"].mean()
    correlacion = df["puntaje"].corr(df["retorno"]) if n >= 3 else None
    return {
        "suficiente": True, "n": n, "datos": df,
        "retorno_tercio_alto": round(tercio_alto, 2),
        "retorno_tercio_bajo": round(tercio_bajo, 2),
        "correlacion": round(correlacion, 2) if correlacion is not None else None,
    }


def regimen_snapshot_anterior() -> str | None:
    """Régimen guardado en el snapshot más reciente ANTERIOR a hoy (para detectar
    cambios de régimen entre un día y el siguiente)."""
    init_db()
    conn = get_connection()
    fila = conn.execute("""
        SELECT regimen FROM snapshots
        WHERE fecha < date('now') AND regimen IS NOT NULL
        ORDER BY fecha DESC LIMIT 1
    """).fetchone()
    conn.close()
    return fila[0] if fila else None


def divergencias_del_dia() -> pd.DataFrame:
    """Divergencias activas guardadas en el snapshot de hoy."""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT par AS Par, spread_20d_pct AS "Spread 20d %", z_score AS "Z-score",
               explicacion AS "Explicación"
        FROM divergencias WHERE fecha = date('now') ORDER BY ABS(z_score) DESC
    """, conn)
    conn.close()
    return df


def historial_roca_chip(dias: int = 90) -> pd.DataFrame:
    """Serie histórica del índice Roca→Chip guardado en los snapshots."""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT fecha AS Fecha, roca_chip AS "Roca→Chip" FROM snapshots
        WHERE roca_chip IS NOT NULL AND fecha >= date('now', ?)
        ORDER BY fecha
    """, conn, params=(f"-{dias} days",))
    conn.close()
    return df
