# ============================================================
# Historial de señales y verificador de aciertos (Etapa 4.6)
#
# REGLA MAESTRA: una predicción solo es verificable si fue emitida ANTES
# de la apertura de la sesión que intenta anticipar, demostrable con
# timestamps UTC. Toda fila nueva lleva timestamp_utc (emisión), exchange,
# sesion_objetivo (la sesión local que intenta anticipar) y available_at
# (cuándo era conocible la información usada). El verificador descarta
# como "no_verificable_timing" lo emitido tarde, y las filas anteriores a
# la Etapa 4.6 quedan como "legacy_pre_4.6": se conservan para auditoría
# pero NUNCA entran a las métricas. El track record limpio empieza con la
# 4.6.
#
# Doble objetivo por predicción:
#   gap_apertura   = open(sesión objetivo) / close(sesión anterior) - 1
#   retorno_sesion = close(sesión objetivo) / close(sesión anterior) - 1
# El gap mide si la señal EXISTE; el retorno de sesión, si es CAPTURABLE.
# ============================================================

import os
import sqlite3
from datetime import date, datetime, timezone

import pandas as pd
import yfinance as yf

import calendarios
from version import (FEATURE_VERSION, MODELO_VERSION, PLATAFORMA_VERSION,
                     UNIVERSO_VERSION)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "senales.db")

DIAS_FORWARD_PUNTAJE = 5   # sesiones hábiles para evaluar el Puntaje IA
MINIMO_OBSERVACIONES = 5   # bajo este umbral: "datos insuficientes"

# Estados de una predicción de apertura
ESTADO_PENDIENTE = "pendiente"
ESTADO_VERIFICADA = "verificada"
ESTADO_NO_VERIFICABLE = "no_verificable_timing"
ESTADO_LEGACY = "legacy_pre_4.6"
# Etapa 5.0 WS2: estado TERMINAL para verificaciones atascadas — la fuente
# lleva ≥ SESIONES_LIMITE_SIN_DATOS sesiones sin publicar la sesión objetivo
# (caso real: XKRX del 17-jul jamás apareció en Yahoo). Auditable, fuera de
# TODAS las métricas (nunca entra a verificacion_apertura).
ESTADO_SIN_DATOS = "sin_datos_mercado"
SESIONES_LIMITE_SIN_DATOS = 5


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def _asegurar_columnas(conn, tabla: str, columnas: dict) -> None:
    """Agrega columnas que falten (migración suave; ALTER TABLE de SQLite no
    tiene IF NOT EXISTS)."""
    existentes = {f[1] for f in conn.execute(f"PRAGMA table_info({tabla})").fetchall()}
    for columna, tipo in columnas.items():
        if columna not in existentes:
            conn.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")


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

    # --- Migraciones Etapa 4.5 → 4.6 ---
    _asegurar_columnas(conn, "snapshots", {
        "regimen": "TEXT", "roca_chip": "REAL",
        "timestamp_utc": "TEXT", "origen": "TEXT",
        "modelo_version": "TEXT", "feature_version": "TEXT",
        "universo_version": "TEXT", "ventana_betas": "INTEGER",
    })
    _asegurar_columnas(conn, "senales_ticker", {
        "timestamp_utc": "TEXT",       # momento exacto de emisión (UTC)
        "exchange": "TEXT",            # bolsa del activo (XKRX, XTKS, ...)
        "sesion_objetivo": "TEXT",     # sesión local que la predicción anticipa
        "available_at": "TEXT",        # cuándo era conocible la info usada
        "estado": "TEXT",              # pendiente/verificada/no_verificable_timing/legacy
        "intervalo80_pp": "REAL",      # ± del intervalo central del 80%
        "n_muestra": "INTEGER",        # sesiones usadas en la regresión
        "modelo_version": "TEXT",
    })
    _asegurar_columnas(conn, "verificacion_apertura", {
        "gap_pct": "REAL",             # open(obj)/close(ant) - 1
        "acierto_gap": "INTEGER",
        "error_gap_pp": "REAL",
        "modelo_version": "TEXT",
        "legacy": "INTEGER",
    })
    # --- Migración Etapa 5.0 (WS2.2): salud de descarga sellada por snapshot.
    # Excepción quirúrgica #1 de la constitución: SOLO observabilidad — qué
    # fracción del lote de tickers descargó bien al momento de sellar. Cero
    # cambios en la lógica de señales.
    _asegurar_columnas(conn, "snapshots", {
        "descarga_ok": "INTEGER",      # tickers con datos recientes al sellar
        "descarga_total": "INTEGER",   # tickers esperados (universo + ^SOX)
        "descarga_caidos": "TEXT",     # lista separada por comas de los caídos
        "plataforma_version": "TEXT",  # versionado dual 5.0: plataforma vs modelo
        # WS3: el reporte solo dice lo SELLADO — para que diga qué SOX alimentó
        # las predicciones, ese dato se sella también (era parte del frame de
        # predicción del motor; aditivo, cero lógica nueva).
        "sox_usado_pct": "REAL",
        "sox_fecha": "TEXT",
    })
    # WS3: la beta de contagio de cada predicción también queda sellada
    # (el motor siempre la calculó; ahora el sello la conserva).
    _asegurar_columnas(conn, "senales_ticker", {"beta": "REAL"})
    _asegurar_columnas(conn, "divergencias", {
        "spread_simple_pct": "REAL", "z_simple": "REAL",
    })
    # Filas históricas sin timestamp confiable → legacy: se conservan para
    # auditoría, pero quedan fuera de todas las métricas.
    conn.execute(f"""
        UPDATE senales_ticker SET estado = '{ESTADO_LEGACY}'
        WHERE timestamp_utc IS NULL AND (estado IS NULL OR estado = '')
    """)
    conn.execute("""
        UPDATE verificacion_apertura SET legacy = 1
        WHERE modelo_version IS NULL AND (legacy IS NULL)
    """)
    conn.commit()
    conn.close()


# ------------------------------------------------------------
# Snapshot diario
# ------------------------------------------------------------
def ya_existe_snapshot_hoy() -> bool:
    init_db()
    conn = get_connection()
    existe = conn.execute("SELECT 1 FROM snapshots WHERE fecha = ?",
                          (date.today().isoformat(),)).fetchone()
    conn.close()
    return existe is not None


def info_snapshot_hoy() -> dict | None:
    """Metadatos del snapshot de hoy (para la tarjeta de estado del sistema)."""
    init_db()
    conn = get_connection()
    fila = conn.execute("""
        SELECT fecha, creado_en, timestamp_utc, origen, modelo_version
        FROM snapshots WHERE fecha = ?""", (date.today().isoformat(),)).fetchone()
    conn.close()
    if not fila:
        return None
    return {"fecha": fila[0], "creado_en": fila[1], "timestamp_utc": fila[2],
            "origen": fila[3] or "dashboard", "modelo_version": fila[4]}


def guardar_snapshot(fecha: str, timestamp_utc: str, origen: str,
                     metricas_df: pd.DataFrame, sentimientos: dict,
                     predicciones: list, regimen: str = None,
                     roca_chip: float = None, divergencias: list = None,
                     ventana_betas: int = None, available_at: str = None,
                     salud_descarga: dict = None, sox_usado_pct: float = None,
                     sox_fecha: str = None) -> bool:
    """Guarda el snapshot del día (idempotente: si ya existe, no duplica).

    `predicciones`: lista de dicts con Ticker, Apertura estimada %, R2,
    Intervalo80 pp, N muestra, exchange, sesion_objetivo — cada una queda
    sellada con timestamp_utc y available_at para el verificador.
    `salud_descarga` (Etapa 5.0 WS2.2, opcional): {"ok_n", "total", "caidos"}
    — observabilidad sellada de la descarga; no toca ninguna señal."""
    init_db()
    if ya_existe_snapshot_hoy() or metricas_df.empty:
        return False
    salud = salud_descarga or {}
    conn = get_connection()
    conn.execute("""
        INSERT INTO snapshots (fecha, creado_en, regimen, roca_chip, timestamp_utc,
                               origen, modelo_version, feature_version,
                               universo_version, ventana_betas,
                               descarga_ok, descarga_total, descarga_caidos,
                               plataforma_version, sox_usado_pct, sox_fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (fecha, timestamp_utc, regimen, roca_chip, timestamp_utc, origen,
         MODELO_VERSION, FEATURE_VERSION, UNIVERSO_VERSION, ventana_betas,
         salud.get("ok_n"), salud.get("total"),
         ",".join(salud["caidos"]) if salud.get("caidos") else None,
         PLATAFORMA_VERSION, sox_usado_pct, sox_fecha))

    for div in divergencias or []:
        conn.execute("""
            INSERT OR IGNORE INTO divergencias
            (fecha, par, spread_20d_pct, z_score, explicacion, spread_simple_pct, z_simple)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (fecha, div["par"], div["spread"], div["z"], div.get("explicacion", ""),
             div.get("spread_simple"), div.get("z_simple")))

    pred_por_ticker = {p["Ticker"]: p for p in (predicciones or [])}
    for _, fila in metricas_df.iterrows():
        ticker = fila["Ticker"]
        puntaje_v0 = float(fila["Puntaje v0"])
        sentimiento = sentimientos.get(ticker)
        puntaje_ia = None
        if sentimiento is not None:
            puntaje_ia = round(puntaje_v0 * 0.7 + ((sentimiento + 1) / 2) * 0.3, 4)
        pred = pred_por_ticker.get(ticker)
        conn.execute("""
            INSERT OR IGNORE INTO senales_ticker
            (fecha, ticker, puntaje_v0, sentimiento_ia, puntaje_ia,
             apertura_estimada_pct, confianza_r2, timestamp_utc, exchange,
             sesion_objetivo, available_at, estado, intervalo80_pp, n_muestra,
             modelo_version, beta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (fecha, ticker, puntaje_v0, sentimiento, puntaje_ia,
             pred["Apertura estimada %"] if pred else None,
             pred["R2"] if pred else None,
             timestamp_utc,
             pred.get("exchange") if pred else None,
             pred.get("sesion_objetivo") if pred else None,
             available_at or timestamp_utc,
             ESTADO_PENDIENTE if pred else None,
             pred.get("Intervalo80 pp") if pred else None,
             pred.get("N muestra") if pred else None,
             MODELO_VERSION,
             pred.get("Beta") if pred else None))
    conn.commit()
    conn.close()
    return True


# ------------------------------------------------------------
# Verificador — regla maestra de timing + doble objetivo
# ------------------------------------------------------------
def _ohlc_local(ticker: str, desde: str) -> pd.DataFrame:
    """Open/Close locales de un ticker desde una fecha (para gap y retorno)."""
    datos = yf.download(ticker, start=desde, auto_adjust=True, progress=False)
    if datos.empty:
        return pd.DataFrame()
    if isinstance(datos.columns, pd.MultiIndex):
        datos.columns = datos.columns.get_level_values(0)
    return datos[["Open", "Close"]].dropna(how="all")


def verificar_apertura_pendientes() -> dict:
    """Verifica las predicciones de apertura pendientes aplicando la REGLA
    MAESTRA: solo se evalúan las emitidas (timestamp_utc) ANTES de la apertura
    UTC de su sesión objetivo. Las emitidas tarde quedan como
    'no_verificable_timing' (auditables, fuera de métricas). Para las válidas
    cuya sesión ya cerró, calcula el DOBLE objetivo: gap de apertura y retorno
    de sesión (ambos vs el cierre de la sesión local anterior)."""
    init_db()
    conn = get_connection()
    pendientes = conn.execute(f"""
        SELECT id, fecha, ticker, apertura_estimada_pct, timestamp_utc,
               exchange, sesion_objetivo, modelo_version
        FROM senales_ticker
        WHERE estado = '{ESTADO_PENDIENTE}' AND apertura_estimada_pct IS NOT NULL
          AND timestamp_utc IS NOT NULL AND sesion_objetivo IS NOT NULL
        ORDER BY fecha
    """).fetchall()

    verificadas, descartadas, atascadas = 0, 0, 0
    for (id_, fecha_senal, ticker, est_pct, ts_utc, exchange,
         sesion_obj, modelo_ver) in pendientes:
        try:
            apertura = calendarios.apertura_utc(exchange, sesion_obj)
        except Exception:
            continue
        emitida = datetime.fromisoformat(ts_utc)
        if emitida.tzinfo is None:
            emitida = emitida.replace(tzinfo=timezone.utc)

        # REGLA MAESTRA: emitida tarde → no verificable, fuera de métricas
        if emitida >= apertura:
            conn.execute("UPDATE senales_ticker SET estado = ? WHERE id = ?",
                         (ESTADO_NO_VERIFICABLE, id_))
            descartadas += 1
            continue

        if not calendarios.sesion_ya_cerro(exchange, sesion_obj):
            continue  # la sesión objetivo aún no cierra: se reintenta después

        sesion_ant = calendarios.sesion_anterior(exchange, sesion_obj)
        datos = _ohlc_local(ticker, (pd.Timestamp(sesion_ant) - pd.Timedelta(days=7)).date().isoformat())
        fechas_str = datos.index.strftime("%Y-%m-%d") if not datos.empty else []
        if datos.empty or sesion_obj not in set(fechas_str):
            # Yahoo aún no publica la sesión objetivo. Normalmente se
            # reintenta en la próxima corrida — pero si ya cerraron
            # SESIONES_LIMITE_SIN_DATOS sesiones posteriores y los datos
            # siguen sin aparecer, la verificación está atascada: pasa al
            # estado TERMINAL sin_datos_mercado (Etapa 5.0 WS2.6 — auditable,
            # fuera de métricas; jamás se inventa un resultado).
            if (calendarios.sesiones_cerradas_desde(exchange, sesion_obj)
                    >= SESIONES_LIMITE_SIN_DATOS):
                conn.execute("UPDATE senales_ticker SET estado = ? WHERE id = ?",
                             (ESTADO_SIN_DATOS, id_))
                atascadas += 1
            continue
        idx_obj = list(fechas_str).index(sesion_obj)
        previos = datos.iloc[:idx_obj]
        if previos.empty:
            continue
        close_ant = float(previos["Close"].iloc[-1])
        open_obj = float(datos["Open"].iloc[idx_obj])
        close_obj = float(datos["Close"].iloc[idx_obj])
        if close_ant <= 0:
            continue

        gap = (open_obj / close_ant - 1) * 100
        retorno_sesion = (close_obj / close_ant - 1) * 100
        conn.execute("""
            INSERT OR IGNORE INTO verificacion_apertura
            (fecha_senal, ticker, apertura_estimada_pct, retorno_real_pct,
             acierto_direccion, error_pp, gap_pct, acierto_gap, error_gap_pp,
             verificado_en, modelo_version, legacy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (fecha_senal, ticker, est_pct,
             round(retorno_sesion, 4),
             1 if (est_pct >= 0) == (retorno_sesion >= 0) else 0,
             round(abs(est_pct - retorno_sesion), 4),
             round(gap, 4),
             1 if (est_pct >= 0) == (gap >= 0) else 0,
             round(abs(est_pct - gap), 4),
             datetime.now(timezone.utc).isoformat(), modelo_ver))
        conn.execute("UPDATE senales_ticker SET estado = ? WHERE id = ?",
                     (ESTADO_VERIFICADA, id_))
        verificadas += 1
    conn.commit()
    conn.close()
    return {"verificadas": verificadas, "no_verificables": descartadas,
            "sin_datos_mercado": atascadas}


def verificar_puntaje_pendientes() -> int:
    """Compara el Puntaje IA contra el retorno real de los DIAS_FORWARD_PUNTAJE
    días hábiles siguientes. Solo evalúa filas de la Etapa 4.6 en adelante
    (con timestamp); las legacy quedan fuera."""
    init_db()
    conn = get_connection()
    pendientes = conn.execute(f"""
        SELECT s.fecha, s.ticker, s.puntaje_ia
        FROM senales_ticker s
        LEFT JOIN verificacion_puntaje v
          ON v.fecha_senal = s.fecha AND v.ticker = s.ticker
        WHERE s.puntaje_ia IS NOT NULL AND v.id IS NULL
          AND s.timestamp_utc IS NOT NULL
          AND (s.estado IS NULL OR s.estado != '{ESTADO_LEGACY}')
          AND s.fecha <= date('now', '-7 days')  -- antes es imposible que existan 5 sesiones
        ORDER BY s.fecha
    """).fetchall()

    verificados = 0
    for fecha_senal, ticker, puntaje_ia in pendientes:
        datos = _ohlc_local(ticker, fecha_senal)
        if datos.empty:
            continue
        cierres = datos["Close"]
        cierres = cierres[cierres.index.strftime("%Y-%m-%d") >= fecha_senal]
        if len(cierres) < DIAS_FORWARD_PUNTAJE + 1:
            continue
        retorno_5d = (cierres.iloc[DIAS_FORWARD_PUNTAJE] / cierres.iloc[0] - 1) * 100
        conn.execute("""
            INSERT OR IGNORE INTO verificacion_puntaje
            (fecha_senal, ticker, puntaje_ia, retorno_5d_pct, verificado_en)
            VALUES (?, ?, ?, ?, ?)""",
            (fecha_senal, ticker, puntaje_ia, round(float(retorno_5d), 4),
             datetime.now(timezone.utc).isoformat()))
        verificados += 1
    conn.commit()
    conn.close()
    return verificados


def verificar_pendientes() -> tuple:
    """Corre ambos verificadores. Devuelve (dict_apertura, n_puntaje)."""
    return verificar_apertura_pendientes(), verificar_puntaje_pendientes()


# ------------------------------------------------------------
# Consultas para el dashboard (honestas + filtradas por versión)
# ------------------------------------------------------------
def metricas_apertura(dias: int = 30, modelo_version: str = MODELO_VERSION) -> dict:
    """Métricas del DOBLE objetivo, solo con predicciones verificadas de la
    misma modelo_version (nunca se mezclan lógicas distintas) y nunca legacy."""
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT acierto_gap, error_gap_pp, acierto_direccion, error_pp
        FROM verificacion_apertura
        WHERE legacy = 0 AND modelo_version = ? AND gap_pct IS NOT NULL
          AND fecha_senal >= date('now', ?)
    """, (modelo_version, f"-{dias} days")).fetchall()
    conn.close()
    n = len(filas)
    if n < MINIMO_OBSERVACIONES:
        return {"suficiente": False, "n": n}
    return {
        "suficiente": True, "n": n,
        "gap": {
            "pct_aciertos": round(100 * sum(f[0] for f in filas) / n, 1),
            "mae_pp": round(sum(f[1] for f in filas) / n, 2),
        },
        "retorno_sesion": {
            "pct_aciertos": round(100 * sum(f[2] for f in filas) / n, 1),
            "mae_pp": round(sum(f[3] for f in filas) / n, 2),
        },
    }


def calibracion_intervalos(modelo_version: str = MODELO_VERSION) -> dict:
    """Cobertura empírica del intervalo del 80%: qué fracción de los gaps
    reales cayó dentro de estimación ± intervalo80. Con pocos datos:
    'calibración: pendiente'."""
    init_db()
    conn = get_connection()
    filas = conn.execute("""
        SELECT v.gap_pct, s.apertura_estimada_pct, s.intervalo80_pp
        FROM verificacion_apertura v
        JOIN senales_ticker s
          ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
        WHERE v.legacy = 0 AND v.modelo_version = ? AND v.gap_pct IS NOT NULL
          AND s.intervalo80_pp IS NOT NULL
    """, (modelo_version,)).fetchall()
    conn.close()
    n = len(filas)
    if n < MINIMO_OBSERVACIONES:
        return {"suficiente": False, "n": n}
    dentro = sum(1 for gap, est, int80 in filas if abs(gap - est) <= int80)
    return {"suficiente": True, "n": n,
            "cobertura_pct": round(100 * dentro / n, 1)}


def evolucion_aciertos_apertura(modelo_version: str = MODELO_VERSION) -> pd.DataFrame:
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT fecha_senal AS Fecha,
               AVG(acierto_gap) * 100 AS "% Aciertos gap",
               AVG(acierto_direccion) * 100 AS "% Aciertos sesión",
               COUNT(*) AS N
        FROM verificacion_apertura
        WHERE legacy = 0 AND modelo_version = ? AND gap_pct IS NOT NULL
        GROUP BY fecha_senal ORDER BY fecha_senal
    """, conn, params=(modelo_version,))
    conn.close()
    return df


def ultimas_predicciones_apertura(limite: int = 50,
                                  modelo_version: str = MODELO_VERSION) -> pd.DataFrame:
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT v.fecha_senal AS Fecha, v.ticker AS Ticker,
               v.apertura_estimada_pct AS "Estimado %",
               v.gap_pct AS "Gap real %",
               v.retorno_real_pct AS "Sesión real %",
               v.acierto_gap AS "Acierto gap",
               v.acierto_direccion AS "Acierto sesión",
               s.sesion_objetivo AS "Sesión objetivo",
               s.timestamp_utc AS "Emitida (UTC)"
        FROM verificacion_apertura v
        LEFT JOIN senales_ticker s
          ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
        WHERE v.legacy = 0 AND v.modelo_version = ?
        ORDER BY v.fecha_senal DESC LIMIT ?
    """, conn, params=(modelo_version, limite))
    conn.close()
    return df


def conteo_por_estado() -> pd.DataFrame:
    """Auditoría: cuántas predicciones hay en cada estado (incluye legacy y
    no_verificable_timing, que están fuera de métricas pero no se borran)."""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT COALESCE(estado, 'sin_prediccion') AS Estado, COUNT(*) AS N
        FROM senales_ticker GROUP BY estado ORDER BY N DESC
    """, conn)
    conn.close()
    return df


def historial_snapshots(limite: int = 30) -> pd.DataFrame:
    """Origen y hora de emisión de los últimos snapshots (programado/manual)."""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT fecha AS Fecha, COALESCE(origen, 'dashboard (pre-4.6)') AS Origen,
               COALESCE(timestamp_utc, creado_en) AS "Emitido (UTC)",
               COALESCE(modelo_version, 'pre-4.6') AS "Versión",
               ventana_betas AS "Ventana betas"
        FROM snapshots ORDER BY fecha DESC LIMIT ?
    """, conn, params=(limite,))
    conn.close()
    return df


def analisis_puntaje_ia(dias: int = 90, modelo_version: str = MODELO_VERSION) -> dict:
    """¿El Puntaje IA anticipa el retorno a 5 días? Solo filas post-4.6."""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query(f"""
        SELECT v.puntaje_ia AS puntaje, v.retorno_5d_pct AS retorno
        FROM verificacion_puntaje v
        JOIN senales_ticker s
          ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
        WHERE v.fecha_senal >= date('now', ?)
          AND s.timestamp_utc IS NOT NULL AND s.modelo_version = ?
    """, conn, params=(f"-{dias} days", modelo_version))
    conn.close()
    n = len(df)
    if n < MINIMO_OBSERVACIONES:
        return {"suficiente": False, "n": n, "datos": df}
    df = df.sort_values("puntaje")
    corte = max(1, n // 3)
    correlacion = df["puntaje"].corr(df["retorno"]) if n >= 3 else None
    return {
        "suficiente": True, "n": n, "datos": df,
        "retorno_tercio_alto": round(df.iloc[-corte:]["retorno"].mean(), 2),
        "retorno_tercio_bajo": round(df.iloc[:corte]["retorno"].mean(), 2),
        "correlacion": round(correlacion, 2) if correlacion is not None else None,
    }


def snapshot_del_dia(fecha: str = None) -> dict | None:
    """La fila COMPLETA del snapshot sellado de `fecha` (default hoy) — la
    fuente única del reporte 2.0 (Etapa 5.0 WS3): el reporte dice lo sellado
    y nada más."""
    init_db()
    fecha = fecha or date.today().isoformat()
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    fila = conn.execute("""
        SELECT fecha, timestamp_utc, origen, regimen, roca_chip,
               modelo_version, plataforma_version, ventana_betas,
               descarga_ok, descarga_total, descarga_caidos,
               sox_usado_pct, sox_fecha
        FROM snapshots WHERE fecha = ?""", (fecha,)).fetchone()
    conn.close()
    return dict(fila) if fila else None


def predicciones_selladas_del_dia(fecha: str = None) -> list:
    """Las predicciones SELLADAS de `fecha` (default hoy), ordenadas por
    |estimado| descendente — para el reporte 2.0 y la vista /salud."""
    init_db()
    fecha = fecha or date.today().isoformat()
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    filas = conn.execute("""
        SELECT ticker, apertura_estimada_pct, confianza_r2 AS r2,
               intervalo80_pp, n_muestra, beta, exchange, sesion_objetivo,
               timestamp_utc, estado
        FROM senales_ticker
        WHERE fecha = ? AND apertura_estimada_pct IS NOT NULL
        ORDER BY ABS(apertura_estimada_pct) DESC""", (fecha,)).fetchall()
    conn.close()
    return [dict(f) for f in filas]


def regimen_snapshot_anterior() -> str | None:
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
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT par AS Par, spread_20d_pct AS "Spread resid. %", z_score AS "Z-score",
               spread_simple_pct AS "Spread simple %", z_simple AS "Z simple",
               explicacion AS "Explicación"
        FROM divergencias WHERE fecha = date('now') ORDER BY ABS(z_score) DESC
    """, conn)
    conn.close()
    return df


def historial_roca_chip(dias: int = 90) -> pd.DataFrame:
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT fecha AS Fecha, roca_chip AS "Roca→Chip" FROM snapshots
        WHERE roca_chip IS NOT NULL AND fecha >= date('now', ?)
        ORDER BY fecha
    """, conn, params=(f"-{dias} days",))
    conn.close()
    return df
