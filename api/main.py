# ============================================================
# API MKI Terminal (Etapa 4.7 "Fachada") — FastAPI, SOLO LECTURA.
#
# REGLA CERO: esta capa no contiene lógica de señales. Envuelve las
# funciones puras de motor.py, lee senales.db/noticias.db mediante los
# helpers de consulta existentes, y usa calendarios.py para el timing.
# Lo único que computa por sí misma es presentación (base 100, estados
# de sesión, correlaciones para gráficos). Jamás escribe en las bases ni
# llama a la API de Anthropic. El contrato completo vive en CONTRATO.md.
#
# Correr:  source venv/bin/activate && uvicorn api.main:app --reload
# ============================================================

from datetime import date, datetime, timedelta, timezone

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import calendarios
import motor
import noticias
import senales
from api.utilidades import (Z_POR_NOMINAL, cache_ttl, dias_a_proximos_earnings,
                            intervalo_wilson, ohlc_1y, serie_a_lista)
from universo import (ACCIONES, BENCHMARK, EXCHANGE_POR_TICKER, MERCADOS_POR_ABRIR,
                      MONEDA_TICKER, NIVELES_CADENA, TICKERS_POR_NIVEL, UNIVERSO,
                      nombre)
from version import (FEATURE_VERSION, MODELO_VERSION, PLATAFORMA_VERSION,
                     UNIVERSO_VERSION)

app = FastAPI(title="MKI Terminal API", version="1.0",
              description="API de solo lectura sobre el motor de señales MKI")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost(:\d+)?|http://127\.0\.0\.1(:\d+)?",
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --- Manejo homogéneo de errores (Etapa 5.0 WS6, CONTRATO.md):
#     siempre {"detail": causa, "codigo": ...}; los 500 pasan por el
#     enmascarador de secretos — un traceback jamás filtra una clave.
from fastapi import Request  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

from seguridad import enmascarar_secretos  # noqa: E402

_CODIGOS_HTTP = {400: "parametros_invalidos", 404: "no_encontrado"}


@app.exception_handler(HTTPException)
async def _error_http(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={
        "detail": exc.detail,
        "codigo": _CODIGOS_HTTP.get(exc.status_code, f"http_{exc.status_code}"),
    })


@app.exception_handler(Exception)
async def _error_interno(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={
        "detail": enmascarar_secretos(f"{type(exc).__name__}: {exc}"),
        "codigo": "error_interno",
    })

EXCHANGES_CINTA = [
    ("XKRX", "KRX · Seúl", "asia"),
    ("XTKS", "TSE · Tokio", "asia"),
    ("XTAI", "TWSE · Taipéi", "asia"),
    ("XETR", "Xetra · Fráncfort", "europa"),
    ("XNYS", "NYSE/Nasdaq · Nueva York", "eeuu"),
]


# ------------------------------------------------------------
# Bloques compartidos (cacheados)
# ------------------------------------------------------------
@cache_ttl(300)
def _regimen_hoy() -> dict | None:
    return motor.regimen_al(date.today())


@cache_ttl(300)
def _prediccion_hoy() -> pd.DataFrame:
    return motor.prediccion_apertura_al(
        date.today(), dias_earnings=dias_a_proximos_earnings(ACCIONES))


@cache_ttl(300)
def _cadena_hoy() -> dict:
    return motor.datos_cadena_al(date.today())


# P0 (4.7.1): el índice Roca→Chip que muestra el terminal es EXCLUSIVAMENTE
# el valor sellado del último snapshot en senales.db — la API no lo recalcula
# al momento de la visita (una sola fuente de verdad; el modo "en vivo" queda
# diferido a la integración intradía futura, ver DECISIONES.md).
@cache_ttl(300)
def _roca_chip_sellado() -> dict | None:
    df = senales.historial_roca_chip(dias=365)
    if df.empty:
        return None
    return {
        "valor": round(float(df.iloc[-1]["Roca→Chip"])),
        "fecha": str(df.iloc[-1]["Fecha"]),
        # la historia del sparkline también es sellada: un punto por snapshot
        "historia": [round(float(v), 1) for v in df["Roca→Chip"].tail(30)],
    }


@cache_ttl(300)
def _roca_chip_contexto(fecha_iso: str) -> dict | None:
    """Serie de contexto (momentum 20d crudo) ANCLADA a la fecha sellada:
    usa solo datos ≤ fecha del sello, así es idéntica en cada visita."""
    return motor.roca_chip_al(date.fromisoformat(fecha_iso))


@cache_ttl(300)
def _divergencias_hoy() -> list:
    return motor.divergencias_al(date.today())


@cache_ttl(300)
def _salud_hoy() -> dict:
    return motor.salud_datos_al(date.today())


def _sox_ultimo() -> dict | None:
    """Último movimiento real del SOX (presentación del dato del motor)."""
    sox = motor._datos_crudos(("^SOX",))
    if sox.empty:
        return None
    ret = sox.iloc[:, 0].pct_change().dropna()
    if ret.empty:
        return None
    fecha_reciente = ret.index[-1].date().isoformat()
    feriado_hoy = abs(float(ret.iloc[-1])) < 1e-6
    no_cero = ret[ret.abs() >= 1e-6]
    if no_cero.empty:
        return None
    return {"mov_pct": round(float(no_cero.iloc[-1]) * 100, 2),
            "fecha": no_cero.index[-1].date().isoformat(),
            "feriado_hoy": feriado_hoy, "fecha_reciente": fecha_reciente}


def _meta() -> dict:
    regimen = _regimen_hoy()
    return {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "fecha_datos": date.today().isoformat(),
        "regimen": regimen["etiqueta"] if regimen else None,
        "modelo_version": MODELO_VERSION,
        "plataforma_version": PLATAFORMA_VERSION,   # 5.0: versionado dual
        "snapshot_hoy": senales.info_snapshot_hoy(),
    }


# P1 (4.7.1): etiqueta de señal derivada SOLO de umbrales de R² histórico —
# la incertidumbre se comunica con muestra, R² e intervalo, nunca con
# etiquetas subjetivas. La zona de earnings viaja aparte y no altera esto.
def _etiqueta_senal(r2: float) -> str:
    return "fuerte" if r2 > 0.25 else ("moderada" if r2 > 0.10 else "debil")


# P4 (4.7.1): filtro de portada — /hoy muestra solo lo mejor del día;
# /api/noticias sigue sirviendo TODO (ahí el usuario explora).
RELEVANCIA_MINIMA_PORTADA = 0.5
MAX_TITULARES_PORTADA = 5


@cache_ttl(300)
def _titulares_portada() -> list:
    """Lectura pura de noticias.db (capa de presentación). Pasan a portada:
    relevancia ≥ umbral; los análisis previos a la columna relevancia (NULL)
    solo si el matching estricto (helper existente de noticias.py) confirma
    una empresa del universo nombrada de forma inequívoca en el titular."""
    conn = noticias.get_connection()
    try:
        filas = conn.execute("""
            SELECT t.fecha, t.fuente, t.titular, a.sentimiento,
                   a.tickers_afectados, a.relevancia
            FROM analisis a JOIN titulares t ON t.id = a.titular_id
            ORDER BY t.fecha DESC LIMIT 60
        """).fetchall()
    finally:
        conn.close()
    resultado = []
    for fecha, fuente, titular, sentimiento, tickers, relevancia in filas:
        if relevancia is not None:
            if relevancia < RELEVANCIA_MINIMA_PORTADA:
                continue
        elif not noticias.tickers_estrictos(titular):
            continue
        resultado.append({"titular": titular, "fuente": fuente, "fecha": fecha,
                          "sentimiento": sentimiento, "relevancia": relevancia,
                          "tickers": tickers})
        if len(resultado) >= MAX_TITULARES_PORTADA:
            break
    return resultado


def _sin_nan(obj):
    """JSON no admite NaN/inf; los .to_dict() de pandas los traen (celdas
    vacías del track record en maduración, etc.) → null explícito."""
    import math
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    if isinstance(obj, dict):
        return {k: _sin_nan(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sin_nan(v) for v in obj]
    return obj


def _envuelve(datos: dict) -> dict:
    return {"meta": _meta(), "datos": _sin_nan(datos)}


def _predicciones_enriquecidas() -> list:
    """Predicción viva del motor + sellado del snapshot de hoy (timestamps de
    emisión reales — la garantía anti look-ahead). Lectura pura de senales.db."""
    vivas = _prediccion_hoy()
    selladas = {}
    conn = senales.get_connection()
    try:
        for fila in conn.execute("""
            SELECT ticker, apertura_estimada_pct, intervalo80_pp, n_muestra,
                   exchange, sesion_objetivo, timestamp_utc, estado
            FROM senales_ticker
            WHERE fecha = ? AND apertura_estimada_pct IS NOT NULL
        """, (date.today().isoformat(),)).fetchall():
            selladas[fila[0]] = fila
    finally:
        conn.close()

    resultado = []
    if vivas is None or vivas.empty:
        return resultado
    ahora = datetime.now(timezone.utc)
    for _, p in vivas.iterrows():
        t = p["Ticker"]
        sello = selladas.get(t)
        exchange = (sello[4] if sello and sello[4]
                    else EXCHANGE_POR_TICKER.get(t, "XNYS"))
        if sello and sello[5]:
            sesion_obj = sello[5]
        else:
            try:
                sesion_obj, _, _ = calendarios.proxima_sesion_despues_de(exchange, ahora)
            except Exception:
                sesion_obj = None
        apertura_obj = None
        if sesion_obj:
            try:
                apertura_obj = calendarios.apertura_utc(exchange, sesion_obj).isoformat()
            except Exception:
                pass
        resultado.append({
            "ticker": t,
            "nombre": nombre(t),
            "mercado": UNIVERSO.get(t, {}).get("segmento", "").split(" - ")[0],
            "exchange": exchange,
            "sesion_objetivo": sesion_obj,
            "apertura_objetivo_utc": apertura_obj,
            # Si hay sello, el número vigente es el SELLADO (el emitido);
            # el vivo puede diferir si el mercado se movió después.
            "estimado_pct": float(sello[1]) if sello else float(p["Apertura estimada %"]),
            "intervalo80_pp": (float(sello[2]) if sello and sello[2] is not None
                               else float(p["Intervalo80 pp"])),
            "n_muestra": int(sello[3]) if sello and sello[3] else int(p["N muestra"]),
            "beta": float(p["Beta de contagio"]),
            "r2_historico": float(p["R2"]),
            "senal": _etiqueta_senal(float(p["R2"])),
            "zona_earnings": bool(p["Zona earnings"]),
            "dias_earnings": (int(p["Dias earnings"])
                              if p["Zona earnings"] and pd.notna(p["Dias earnings"])
                              else None),
            "sellada": sello is not None,
            "emitida_utc": sello[6] if sello else None,
            "estado": sello[7] if sello else "no_sellada",
        })
    return resultado


def _husos() -> list:
    """La cinta: sesiones por exchange con estado y beta de contagio promedio."""
    ahora = datetime.now(timezone.utc)
    betas = motor.betas_al(date.today())
    beta_por_exchange: dict = {}
    if not betas.empty:
        for _, b in betas.iterrows():
            ex = EXCHANGE_POR_TICKER.get(b["Ticker"], "XNYS")
            beta_por_exchange.setdefault(ex, []).append(float(b["beta"]))

    filas = []
    proxima_apertura_ts = None
    for exchange, etiqueta, region in EXCHANGES_CINTA:
        try:
            sesion, open_u, close_u = calendarios.proxima_sesion_despues_de(exchange, ahora)
        except Exception:
            continue
        # ¿Sesión en curso? La "próxima" sesión abre en el futuro; si además
        # hay una sesión de HOY cuyo cierre aún no llega, el mercado está abierto.
        estado = "cerrada"
        hoy_ex = ahora.date().isoformat()
        try:
            if calendarios.es_sesion(exchange, hoy_ex):
                o_hoy = calendarios.apertura_utc(exchange, hoy_ex)
                c_hoy = calendarios.cierre_utc(exchange, hoy_ex)
                if o_hoy <= ahora <= c_hoy:
                    estado = "abierta"
                    sesion, open_u, close_u = hoy_ex, o_hoy, c_hoy
        except Exception:
            pass
        betas_ex = beta_por_exchange.get(exchange)
        filas.append({
            "exchange": exchange, "nombre": etiqueta, "region": region,
            "sesion": sesion,
            "apertura_utc": (open_u.isoformat() if isinstance(open_u, datetime)
                             else str(open_u)),
            "cierre_utc": (close_u.isoformat() if isinstance(close_u, datetime)
                           else str(close_u)),
            "estado": estado,
            "beta_contagio_promedio": (round(sum(betas_ex) / len(betas_ex), 2)
                                       if betas_ex else None),
            "cerro_antes": "XNYS" if exchange != "XNYS" else None,
            "tickers": [{"ticker": t, "nombre": nombre(t)}
                        for t, ex in EXCHANGE_POR_TICKER.items()
                        if ex == exchange and t in UNIVERSO
                        and UNIVERSO[t]["tipo"] == "accion"],
        })
        if estado != "abierta":
            ts = filas[-1]["apertura_utc"]
            if proxima_apertura_ts is None or ts < proxima_apertura_ts:
                proxima_apertura_ts = ts
    # marcar la próxima en abrir
    for f in filas:
        if f["estado"] == "cerrada" and f["apertura_utc"] == proxima_apertura_ts:
            f["estado"] = "proxima"
    return filas


# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------
def _operacion() -> dict:
    """Bloque operacional 5.0 (la sala de máquinas): estado de los 5 jobs
    según sus ARTEFACTOS (sello, ledger de costos, logs, git) — los mismos
    chequeos del vigía, reutilizados. Solo lectura."""
    import os

    import costos
    import mki_vigia

    directorio = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    definicion = [
        ("noticias", "17:50", mki_vigia.chequear_noticias, "data/noticias.log"),
        ("snapshot", "18:15", mki_vigia.chequear_snapshot, "data/snapshot.log"),
        ("reporte", "18:25", mki_vigia.chequear_reporte, "data/reporte.log"),
        ("backup", "18:40", mki_vigia.chequear_backup, "data/backup.log"),
        ("vigia", "19:00", None, "data/vigia.log"),
    ]
    jobs = []
    for nombre_job, hora, chequeo, log_rel in definicion:
        ruta_log = os.path.join(directorio, log_rel)
        mtime = None
        if os.path.exists(ruta_log):
            mtime = datetime.fromtimestamp(os.path.getmtime(ruta_log),
                                           tz=timezone.utc).isoformat()
        if chequeo is not None:
            try:
                ok, detalle = chequeo()
            except Exception as e:
                ok, detalle = False, f"chequeo falló: {e}"
        else:
            # el vigía se evalúa por su propio log (si corrió hoy, escribió)
            hoy = date.today().isoformat()
            ok = bool(mtime) and mtime[:10] == hoy
            detalle = ("vigia: corrió hoy" if ok
                       else "vigia: sin corrida registrada hoy")
        jobs.append({"job": nombre_job, "hora_programada": hora, "ok": ok,
                     "detalle": detalle, "log": log_rel,
                     "log_modificado_utc": mtime})

    conn = senales.get_connection()
    try:
        semana = [dict(zip(("fecha", "origen", "descarga_ok", "descarga_total",
                            "descarga_caidos"), f))
                  for f in conn.execute("""
                      SELECT fecha, origen, descarga_ok, descarga_total,
                             descarga_caidos
                      FROM snapshots ORDER BY fecha DESC LIMIT 10""")]
    finally:
        conn.close()

    dbs = []
    for nombre_db in ("senales.db", "noticias.db", "alertas.db"):
        ruta = os.path.join(directorio, nombre_db)
        if os.path.exists(ruta):
            dbs.append({"nombre": nombre_db, "bytes": os.path.getsize(ruta)})

    return {
        "es_dia_habil": date.today().weekday() < 5,
        "jobs": jobs,
        "descarga_semana": semana,
        "verificaciones": {
            "estados": senales.conteo_por_estado().to_dict(orient="records"),
            "pendientes": senales.predicciones_por_estado(senales.ESTADO_PENDIENTE),
            "atascadas": senales.predicciones_por_estado(senales.ESTADO_SIN_DATOS),
        },
        "presupuesto": {**costos.estado_presupuesto(),
                        "gasto_mes_usd": costos.gasto_del_mes(),
                        "corridas_hoy": costos.corridas_del_dia()},
        "dbs": dbs,
    }


@app.get("/api/salud")
def salud():
    snap = senales.info_snapshot_hoy()
    edad_horas, viejo = None, False
    historial = senales.historial_snapshots(1)
    if not historial.empty:
        ultimo = historial.iloc[0]
        try:
            emitido = datetime.fromisoformat(str(ultimo["Emitido (UTC)"]))
            if emitido.tzinfo is None:
                emitido = emitido.replace(tzinfo=timezone.utc)
            edad_horas = round((datetime.now(timezone.utc) - emitido).total_seconds() / 3600, 1)
            # >1 día hábil: más de 24h en semana, más de 72h si cruza fin de semana
            limite = 72 if datetime.now(timezone.utc).weekday() == 0 else 24
            viejo = edad_horas > limite
        except (ValueError, TypeError):
            pass
    else:
        viejo = True
    horarios = calendarios.tabla_horarios()
    return _envuelve({
        "snapshot": snap,
        "snapshot_viejo": viejo,
        "edad_snapshot_horas": edad_horas,
        "salud_datos": _salud_hoy(),
        "horarios_utc": horarios.to_dict(orient="records"),
        "versiones": {"modelo": MODELO_VERSION, "feature": FEATURE_VERSION,
                      "universo": UNIVERSO_VERSION,
                      "plataforma": PLATAFORMA_VERSION},
        "operacion": _operacion(),
    })


@app.get("/api/universo")
def universo_endpoint():
    """Exposición plana del universo (sin lógica): para selectores del front."""
    return _envuelve({
        "instrumentos": [{
            "ticker": t, "nombre": info["nombre"], "segmento": info["segmento"],
            "nivel": info["nivel"], "tipo": info["tipo"],
            "exchange": EXCHANGE_POR_TICKER.get(t),
        } for t, info in UNIVERSO.items()],
    })


@app.get("/api/hoy")
def hoy():
    regimen = _regimen_hoy()
    roca = _roca_chip_sellado()
    predicciones = _predicciones_enriquecidas()
    divergencias = [d for d in _divergencias_hoy() if d["activa"]]
    sentimientos = noticias.sentimiento_promedio_por_ticker()
    buzz = noticias.buzz_por_ticker()

    # Señales del día — misma lógica de puntuación que la portada Streamlit:
    # fuerza = distancia relativa al umbral de activación de cada familia.
    candidatas = []
    for p in divergencias:
        candidatas.append((abs(p["z"]) / 2, {
            "tipo": "divergencia", "titulo": f"Divergencia: {p['par']}",
            "direccion": "neutra",
            "magnitud": f"{p['spread']:+.1f} pp spread 20d (z={p['z']:+.1f})",
            "porque": p["explicacion"],
            "n_muestra": None, "r2_historico": None, "intervalo80_pp": None,
            "emitida_utc": None}))
    for p in predicciones:
        # mismo criterio que usaba el motor para su nivel máximo:
        # R² sobre el umbral fuerte y fuera de la zona de earnings.
        if p["r2_historico"] > 0.25 and not p["zona_earnings"]:
            candidatas.append((abs(p["estimado_pct"]) / 2, {
                "tipo": "apertura",
                "titulo": f"Apertura estimada: {p['nombre']} {p['estimado_pct']:+.2f}%",
                "direccion": "pos" if p["estimado_pct"] >= 0 else "neg",
                "magnitud": (f"intervalo 80%: "
                             f"{p['estimado_pct'] - p['intervalo80_pp']:+.1f} a "
                             f"{p['estimado_pct'] + p['intervalo80_pp']:+.1f} pp"),
                "porque": (f"Beta de contagio {p['beta']:.2f} sobre el último "
                           f"movimiento real del SOX."),
                "n_muestra": p["n_muestra"], "r2_historico": p["r2_historico"],
                "intervalo80_pp": p["intervalo80_pp"],
                "emitida_utc": p["emitida_utc"]}))
    for t, s in sentimientos.items():
        if t in UNIVERSO and abs(s) > 0.6:
            candidatas.append((abs(s) / 0.6, {
                "tipo": "sentimiento",
                "titulo": f"Sentimiento extremo: {nombre(t)} {s:+.2f}",
                "direccion": "pos" if s >= 0 else "neg",
                "magnitud": f"{s:+.2f} (umbral ±0.60)",
                "porque": ("Noticias recientes con sentimiento inusualmente "
                           f"{'positivo' if s > 0 else 'negativo'}, ponderadas "
                           "por frescura y relevancia."),
                "n_muestra": None, "r2_historico": None, "intervalo80_pp": None,
                "emitida_utc": None}))
    for t, b in buzz.items():
        if b.get("buzz") and t in UNIVERSO:
            ratio = (b["hoy"] / b["promedio_diario"] if b["promedio_diario"] > 0 else 3.0)
            candidatas.append((ratio / 3, {
                "tipo": "buzz", "titulo": f"Alto buzz: {nombre(t)}",
                "direccion": "neutra",
                "magnitud": f"{b['hoy']} titulares hoy vs {b['promedio_diario']:.1f}/día",
                "porque": "El flujo de noticias triplica su ritmo habitual.",
                "n_muestra": None, "r2_historico": None, "intervalo80_pp": None,
                "emitida_utc": None}))
    senales_dia = [s for _, s in sorted(candidatas, key=lambda x: -x[0])[:3]]

    # Próxima apertura (protagonista de la portada)
    husos = _husos()
    proxima = next((h for h in husos if h["estado"] == "proxima"), None)
    proxima_apertura = None
    if proxima:
        proxima_apertura = {
            **{k: proxima[k] for k in ["exchange", "nombre", "sesion", "apertura_utc"]},
            "predicciones": [p for p in predicciones
                             if p["exchange"] == proxima["exchange"]],
        }

    metricas_tr = senales.metricas_apertura(dias=30)
    return _envuelve({
        "regimen": regimen,
        "roca_chip": roca,
        "sox": _sox_ultimo(),
        "sentimiento_sector": (round(noticias.sentimiento_promedio_sector(), 2)
                               if noticias.sentimiento_promedio_sector() is not None
                               else None),
        "track_record": {"minimo": senales.MINIMO_OBSERVACIONES, **metricas_tr},
        "senales_dia": senales_dia,
        "proxima_apertura": proxima_apertura,
        "husos": husos,
        "resumen_ia": noticias.obtener_resumen_guardado(),
        "noticias_top": _titulares_portada(),
    })


@app.get("/api/aperturas")
def aperturas():
    sox = _sox_ultimo()
    return _envuelve({
        "sox_usado": ({"mov_pct": sox["mov_pct"], "fecha": sox["fecha"]}
                      if sox else None),
        "ventana_betas": motor.VENTANA_BETAS_DEFAULT,
        "calibracion": {"minimo": senales.MINIMO_OBSERVACIONES,
                        **senales.calibracion_intervalos()},
        "predicciones": _predicciones_enriquecidas(),
    })


@app.get("/api/comparador")
def comparador(tickers: str = Query(...), base: str = Query("usd"),
               desde: str = Query(None)):
    lista = [t.strip() for t in tickers.split(",") if t.strip()]
    desconocidos = [t for t in lista if t not in UNIVERSO]
    if desconocidos:
        raise HTTPException(400, f"Tickers fuera del universo: {desconocidos}")
    if len(lista) < 2:
        raise HTTPException(400, "Se necesitan al menos 2 tickers")
    if base not in ("usd", "local"):
        raise HTTPException(400, "base debe ser 'usd' o 'local'")
    hoy_f = date.today()
    fecha_desde = (date.fromisoformat(desde) if desde
                   else hoy_f - timedelta(days=365))

    precios = motor._precios_hasta(tuple(lista), hoy_f, en_usd=(base == "usd"))
    precios = precios[precios.index.date >= fecha_desde]
    if precios.empty:
        raise HTTPException(400, "Sin datos para ese rango")
    base100 = precios / precios.iloc[0] * 100

    bench = motor._precios_hasta((BENCHMARK,), hoy_f, en_usd=True)
    bench = bench[bench.index.date >= fecha_desde]
    bench100 = (bench / bench.iloc[0] * 100) if not bench.empty else pd.DataFrame()

    puntajes = motor.puntaje_v0_al(hoy_f).set_index("Ticker")
    retornos = precios.pct_change()
    tabla = []
    for t in lista:
        if t not in precios.columns:
            continue
        serie = precios[t].dropna()
        if len(serie) < 5:
            continue
        info = UNIVERSO[t]
        tabla.append({
            "ticker": t, "nombre": info["nombre"], "segmento": info["segmento"],
            "ret_periodo_pct": round((serie.iloc[-1] / serie.iloc[0] - 1) * 100, 1),
            "vol_anual_pct": round(float(retornos[t].std()) * (252 ** 0.5) * 100, 1),
            "momentum_20d_pct": round(
                (serie.iloc[-1] / serie.iloc[-min(21, len(serie))] - 1) * 100, 1),
            "puntaje_v0": (float(puntajes.loc[t, "Puntaje v0"])
                           if t in puntajes.index else None),
        })
    return _envuelve({
        "base": base, "desde": fecha_desde.isoformat(),
        "series": {t: serie_a_lista(base100[t], 2) for t in base100.columns},
        "benchmark": ({"ticker": BENCHMARK, **serie_a_lista(bench100.iloc[:, 0], 2)}
                      if not bench100.empty else None),
        "tabla": tabla,
    })


@app.get("/api/mercados")
def mercados():
    hoy_f = date.today()
    betas = motor.betas_al(hoy_f)
    filas_betas = []
    if not betas.empty:
        for _, b in betas.sort_values("beta", key=abs, ascending=False).iterrows():
            t = b["Ticker"]
            filas_betas.append({
                "ticker": t, "nombre": nombre(t),
                "mercado": UNIVERSO.get(t, {}).get("segmento", "").split(" - ")[0],
                "exchange": EXCHANGE_POR_TICKER.get(t),
                "beta": round(float(b["beta"]), 2),
                "r2_historico": round(float(b["r2"]), 2),
                "n_muestra": int(b["n_muestra"]),
            })

    # Correlaciones con desfase entre eslabones (presentación, igual que la
    # vista Cadena de Streamlit)
    cadena = _cadena_hoy()
    ret_nivel = cadena["ret_nivel"]
    LAGS = [5, 10, 20]
    PARES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 3)]
    filas_desfase = []
    for a, b in PARES:
        if a not in ret_nivel or b not in ret_nivel:
            continue
        valores = []
        for lag in LAGS:
            par = _alinear(ret_nivel[a].shift(lag), ret_nivel[b]).dropna()
            valores.append(round(float(par.iloc[:, 0].corr(par.iloc[:, 1])), 2)
                           if len(par) > 60 else None)
        filas_desfase.append({
            "nombre": f"{NIVELES_CADENA[a]} → {NIVELES_CADENA[b]}",
            "valores": valores})

    # Caso destacado: Samsung correlaciona con el KOSPI el mismo día, pero con
    # el SOX del día ANTERIOR — el contagio viaja con el sol.
    caso = None
    samsung = "005930.KS"
    precios_s = motor._precios_hasta((samsung,), hoy_f)
    kospi = motor._datos_crudos(("^KS11",))
    sox = motor._datos_crudos(("^SOX",))
    if not precios_s.empty and not kospi.empty and not sox.empty:
        rs = precios_s[samsung].pct_change()
        rk = kospi.iloc[:, 0].pct_change()
        rx = sox.iloc[:, 0].pct_change()
        par_k = _alinear(rs, rk).dropna().tail(252)
        par_x0 = _alinear(rs, rx).dropna().tail(252)
        par_x1 = _alinear(rs, rx.shift(1)).dropna().tail(252)
        if len(par_k) > 60:
            caso = {
                "ticker": samsung, "nombre": nombre(samsung),
                "corr_kospi_mismo_dia": round(float(par_k.iloc[:, 0].corr(par_k.iloc[:, 1])), 2),
                "corr_sox_mismo_dia": round(float(par_x0.iloc[:, 0].corr(par_x0.iloc[:, 1])), 2),
                "corr_sox_dia_anterior": round(float(par_x1.iloc[:, 0].corr(par_x1.iloc[:, 1])), 2),
                "n_sesiones": int(len(par_k)),
            }

    return _envuelve({
        "betas": filas_betas,
        "correlaciones_desfase": {"lags": LAGS, "filas": filas_desfase},
        "caso_destacado": caso,
    })


def _alinear(*series: pd.Series) -> pd.DataFrame:
    """`pd.concat` por columnas con `sort=True` EXPLÍCITO (corrida 12, bloque
    2.7): pandas 3 ordena por defecto cuando todos los índices son
    DatetimeIndex y avisa que en pandas 4 el default pasa a `sort=False`.
    `sort=True` es el valor que REPRODUCE la salida actual, demostrado por
    `tests/test_concat_fuera_de_motor.py` contra una fixture congelada ANTES
    de este cambio. Es presentación (correlaciones de la vista), no señal."""
    return pd.concat(list(series), axis=1, sort=True)


@app.get("/api/cadena")
def cadena():
    datos = _cadena_hoy()
    roca = _roca_chip_sellado()
    contexto = _roca_chip_contexto(roca["fecha"]) if roca else None
    niveles = []
    for nivel, nombre_nivel in NIVELES_CADENA.items():
        if nivel not in datos["series_nivel"]:
            continue
        mom = datos["series_nivel"][nivel].dropna()
        if mom.empty:
            continue
        cols = [t for t in TICKERS_POR_NIVEL[nivel] if t in datos["precios"].columns]
        base = datos["precios"][cols].dropna(how="all")
        prom_norm = (base / base.iloc[0]).mean(axis=1).tail(30)
        niveles.append({
            "nivel": nivel, "nombre": nombre_nivel,
            "momentum_20d_pct": round(float(mom.iloc[-1]) * 100, 1),
            "sparkline": [round(float(v), 4) for v in prom_norm.values],
            "tickers": [{"ticker": t, "nombre": nombre(t)} for t in cols],
        })
    return _envuelve({
        "niveles": niveles,
        "roca_chip": ({"valor": roca["valor"], "fecha": roca["fecha"],
                       "serie": (serie_a_lista(contexto["serie"], 2)
                                 if contexto else None)} if roca else None),
        "divergencias": _divergencias_hoy(),
    })


@app.get("/api/noticias")
def noticias_endpoint(entidad: str = Query(None)):
    if entidad and entidad != "sector" and entidad not in UNIVERSO:
        raise HTTPException(400, f"Entidad desconocida: {entidad}")
    if entidad and entidad != "sector":
        titulares = noticias.obtener_titulares_por_ticker(entidad, limite=50)
    else:
        titulares = noticias.obtener_titulares_analizados(limite=100)
        if entidad == "sector":
            titulares = [t for t in titulares if not (t["Tickers afectados"] or "").strip()]
    return _envuelve({
        "sentimiento_por_ticker": {
            t: round(v, 3) for t, v in noticias.sentimiento_promedio_por_ticker().items()
            if t in UNIVERSO},
        "buzz": noticias.buzz_por_ticker(),
        "resumen_dia": noticias.obtener_resumen_guardado(),
        "titulares": [{
            "titular": n["Titular"], "fuente": n["Fuente"], "fecha": n["Fecha"],
            "url": n.get("URL"), "sentimiento": n["Sentimiento"],
            "impacto": n.get("Impacto"), "relevancia": n.get("Relevancia"),
            "tickers": n["Tickers afectados"],
            "peso_temporal": round(noticias._peso_por_antiguedad(n["Fecha"]), 3),
        } for n in titulares],
    })


REGION_POR_EXCHANGE = {"XKRX": "Corea", "XTKS": "Japón", "XTAI": "Taiwán",
                       "XETR": "Europa", "XNYS": "EE.UU."}


def _estadistica_track_record() -> dict:
    """Presentación 5.0 sobre las verificaciones limpias: intervalos de
    Wilson, curva de calibración (re-escala del sigma sellado) y desgloses
    por región/régimen. Los datos vienen del helper de senales.py; aquí
    solo se agrupa y se calcula incertidumbre de PRESENTACIÓN."""
    df = senales.verificaciones_detalle()
    if df.empty:
        return {"wilson": None, "calibracion_curva": None,
                "por_region": [], "por_regimen": []}
    n = len(df)

    def _wilson_dict(col: str) -> dict:
        k = int(df[col].sum())
        lo, hi = intervalo_wilson(k, n)
        return {"pct": round(100 * k / n, 1), "lo_pct": lo, "hi_pct": hi, "n": n}

    wilson = {"gap": _wilson_dict("acierto_gap"),
              "retorno_sesion": _wilson_dict("acierto_direccion")}

    curva = None
    con_intervalo = df.dropna(subset=["intervalo80_pp", "apertura_estimada_pct"])
    if len(con_intervalo) >= senales.MINIMO_OBSERVACIONES:
        errores = (con_intervalo["gap_pct"]
                   - con_intervalo["apertura_estimada_pct"]).abs()
        sigma = con_intervalo["intervalo80_pp"] / Z_POR_NOMINAL[80]
        niveles = sorted(Z_POR_NOMINAL)
        curva = {"nominal_pct": niveles,
                 "real_pct": [round(float((errores <= sigma * Z_POR_NOMINAL[q])
                                          .mean() * 100), 1) for q in niveles],
                 "n": int(len(con_intervalo))}

    def _desglose(serie: pd.Series, etiqueta: str) -> list:
        filas = []
        for valor, grupo in df.groupby(serie):
            k, m = int(grupo["acierto_gap"].sum()), len(grupo)
            lo, hi = intervalo_wilson(k, m)
            filas.append({etiqueta: valor, "n": m,
                          "gap_pct": round(100 * k / m, 1),
                          "wilson_lo_pct": lo, "wilson_hi_pct": hi,
                          "mae_gap_pp": round(float(grupo["error_gap_pp"].mean()), 2)})
        return sorted(filas, key=lambda f: -f["n"])

    region = df["exchange"].map(lambda e: REGION_POR_EXCHANGE.get(e, e or "—"))
    regimen = df["regimen"].fillna("sin régimen sellado")
    return {"wilson": wilson, "calibracion_curva": curva,
            "por_region": _desglose(region, "region"),
            "por_regimen": _desglose(regimen, "regimen")}


@app.get("/api/historial")
def historial():
    evolucion = senales.evolucion_aciertos_apertura()
    ultimas = senales.ultimas_predicciones_apertura(limite=100)
    estados = senales.conteo_por_estado()
    snapshots = senales.historial_snapshots(60)

    # ¿Cuándo puede existir la primera verificación? La sesión objetivo más
    # próxima entre las predicciones pendientes selladas.
    conn = senales.get_connection()
    try:
        fila = conn.execute("""
            SELECT MIN(sesion_objetivo), COUNT(*) FROM senales_ticker
            WHERE estado = 'pendiente' AND sesion_objetivo IS NOT NULL
        """).fetchone()
    finally:
        conn.close()
    return _envuelve({
        "metricas": {"minimo": senales.MINIMO_OBSERVACIONES,
                     **senales.metricas_apertura(dias=30)},
        "calibracion": {"minimo": senales.MINIMO_OBSERVACIONES,
                        **senales.calibracion_intervalos()},
        "evolucion": evolucion.to_dict(orient="records"),
        "ultimas": ultimas.to_dict(orient="records"),
        "estados": estados.to_dict(orient="records"),
        "snapshots": snapshots.to_dict(orient="records"),
        "puntaje_ia": {
            k: v for k, v in senales.analisis_puntaje_ia(dias=90).items()
            if k != "datos"},
        "primera_verificacion_posible": fila[0] if fila else None,
        "pendientes_en_maduracion": fila[1] if fila else 0,
        **_estadistica_track_record(),
    })


@app.get("/api/detalle/{ticker}")
def detalle(ticker: str):
    if ticker not in UNIVERSO:
        raise HTTPException(404, f"Ticker desconocido: {ticker}")
    info = UNIVERSO[ticker]
    hoy_f = date.today()

    metricas = motor.puntaje_v0_al(hoy_f)
    fila_m = None
    if not metricas.empty:
        sel = metricas[metricas["Ticker"] == ticker]
        if not sel.empty:
            fila_m = {k: (v if not isinstance(v, float) else round(v, 2))
                      for k, v in sel.iloc[0].to_dict().items()}

    # Correlaciones principales (presentación): retornos USD del universo
    precios_u = motor._precios_hasta(ACCIONES, hoy_f)
    corr_top = []
    if ticker in precios_u.columns and precios_u.shape[1] > 1:
        rets = precios_u.pct_change()
        corr = rets.corr()[ticker].drop(ticker).dropna()
        top = corr.reindex(corr.abs().sort_values(ascending=False).index).head(6)
        corr_top = [{"ticker": t, "nombre": nombre(t), "corr": round(float(v), 2)}
                    for t, v in top.items()]

    senal = next((p for p in _predicciones_enriquecidas() if p["ticker"] == ticker),
                 None)
    return _envuelve({
        "perfil": {
            "ticker": ticker, "nombre": info["nombre"], "segmento": info["segmento"],
            "nivel": info["nivel"], "tipo": info["tipo"],
            "exchange": EXCHANGE_POR_TICKER.get(ticker),
            "moneda": MONEDA_TICKER.get(ticker, "USD").replace("=X", ""),
            "duplicado_de": info.get("duplicado_de"),
        },
        "ohlc": ohlc_1y(ticker),
        "metricas": fila_m,
        "sentimiento": (round(noticias.sentimiento_promedio_por_ticker().get(ticker), 3)
                        if noticias.sentimiento_promedio_por_ticker().get(ticker) is not None
                        else None),
        "buzz": noticias.buzz_por_ticker().get(ticker),
        "noticias": [{
            "titular": n["Titular"], "fuente": n["Fuente"], "fecha": n["Fecha"],
            "url": n.get("URL"), "sentimiento": n["Sentimiento"],
            "impacto": n.get("Impacto"), "relevancia": n.get("Relevancia")}
            for n in noticias.obtener_titulares_por_ticker(ticker, limite=25)],
        "senal_apertura": senal,
        "correlaciones_top": corr_top,
    })


# ============================================================
# RIEL DE DINERO (Etapa 7.0.0, corrida 10) — CONTRATO.md, enmienda 7.0.0
#
# Tres endpoints de solo lectura sobre artefactos YA GENERADOS. No computan
# nada: leen los JSON que producen `python -m dinero.mapa`,
# `python -m dinero.cuenta_papel` y `python -m dinero.senal_larga_reporte`,
# más el árbitro `cifras.py` para el estado del riel de medición.
#
# La regla propia de estos tres, porque sirven cifras de un riel que no
# tiene NINGUNA fila sellada: cada objeto lleva su `estatus`, y todo
# estimador puntual viaja con su intervalo en el mismo objeto. Un número
# suelto no sale por acá. Re-dictamen de la corrida 12 (D1 a D15): el
# intervalo viaja además con su COBERTURA MEDIDA cuando existe, ninguna
# etiqueta de nivel se escribe a mano, y ningún resumen se sirve sin el
# presupuesto y el modo con que se computó.
# ============================================================
import json as _json  # noqa: E402
import logging as _logging  # noqa: E402
import os as _os  # noqa: E402

_RAIZ = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DIR_DINERO = _os.path.join(_RAIZ, "dinero", "resultados")
_DIR_GEMELO = _os.path.join(_RAIZ, "GEMELO", "resultados")
_log = _logging.getLogger("mki.api.dinero")


def _artefacto_gemelo(nombre: str) -> dict | None:
    """Artefactos de GEMELO/resultados/ que la vista cita (instrumento del
    riel de dinero, intervalo de coherencia). Sólo lectura, igual que los
    de dinero/resultados/."""
    ruta = _os.path.join(_DIR_GEMELO, nombre)
    if not _os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        return _json.load(f)


def _meta_simple(artefacto: str | None = None) -> dict:
    """Meta reducido: estos endpoints no dependen del motor ni del régimen,
    y llamarlo sólo para rellenar un campo sería trabajo (y red) por nada.

    `generado_en` es la hora de ESTA respuesta, no la del dato. Estampar
    hora fresca sobre un JSON que puede tener semanas es la misma zona
    ciega de sellado que el proyecto ya tiene identificada en producción
    (exigencia E10 del `auditor-lookahead`, corrida 10), así que cuando la
    respuesta sale de un artefacto se declara también CUÁNDO se generó ese
    artefacto y con qué huella.
    """
    m = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "modelo_version": MODELO_VERSION,
        "plataforma_version": PLATAFORMA_VERSION,
    }
    if artefacto:
        m["artefacto"] = _sello_artefacto(artefacto)
    return m


def _sello_artefacto(nombre: str) -> dict | None:
    """Fecha de modificación y sha256 del artefacto que sirve la respuesta."""
    ruta = _os.path.join(_DIR_DINERO, nombre)
    if not _os.path.exists(ruta):
        return None
    import hashlib
    with open(ruta, "rb") as f:
        crudo = f.read()
    return {
        "nombre": nombre,
        "generado_en": datetime.fromtimestamp(
            _os.path.getmtime(ruta), timezone.utc).isoformat(),
        "sha256": hashlib.sha256(crudo).hexdigest(),
        "bytes": len(crudo),
    }


def _artefacto(nombre: str) -> dict | None:
    ruta = _os.path.join(_DIR_DINERO, nombre)
    if not _os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        return _json.load(f)


@app.get("/api/dinero/universo")
def dinero_universo():
    datos = _artefacto("universo_operable.json")
    if datos is None:
        raise HTTPException(
            status_code=404,
            detail=("todavía no se generó el mapa operable; se genera con "
                    "`python -m dinero.mapa`"))
    return {"meta": _meta_simple("universo_operable.json"),
            "datos": datos}


@app.get("/api/dinero/cuenta")
def dinero_cuenta():
    datos = _artefacto("cuenta_papel.json")
    if datos is None:
        raise HTTPException(
            status_code=404,
            detail=("todavía no se corrió la cuenta en papel; se corre con "
                    "`python -m dinero.cuenta_papel`"))
    return {"meta": _meta_simple("cuenta_papel.json"), "datos": datos}


def _comisiones_juego_activo(cuenta: dict):
    """Fricción del juego por defecto, leída del artefacto (nunca recomputada)
    como OBJETO y no como escalar (exigencia D1 del re-dictamen, corrida 12):
    mediana entre las K semillas del sorteo, banda entre semillas, K,
    deslizamiento, semanas y denominador. La versión anterior devolvía el
    número de UNA semilla (la de la página) redondeado a un decimal, sin
    intervalo, sin período ni denominador, y eso se retiró.

    Manejo explícito (hallazgo 2 de la revisión del 8-sep): antes terminaba
    en `except Exception: return None`, que tragaba cualquier error sin
    dejar rastro. Las excepciones que de verdad pueden ocurrir son las de
    leer `reglas.json` y las de un artefacto con otra forma; se registran."""
    try:
        from dinero import universo_dinero as U
        cfg = U.reglas()
        juego = cfg["juego_activo"]
        pb = cfg["costos"]["deslizamiento_pb_por_lado"]
    except (OSError, KeyError, ValueError) as e:   # ValueError cubre JSONDecodeError
        _log.warning("reglas del riel de dinero ilegibles: %s", e)
        return None
    bs = (cuenta or {}).get("barrido_semillas") or {}
    try:
        x = bs["comisiones_pct_del_aportado"][juego]
        if bs.get("deslizamiento_pb") != pb:
            _log.warning("barrido_semillas a %s pb, reglas a %s pb: no se sirve", bs.get("deslizamiento_pb"), pb)
            return None
        return {
            "mediana_pct": x["mediana"],
            "banda_p2_5_p97_5": x["banda_p2_5_p97_5"],
            "banda_es": bs.get("banda_es", "percentiles 2,5 y 97,5 entre sorteos de la señal, no un intervalo de cobertura nominal"),
            "K": bs.get("K"),
            "deslizamiento_pb": pb,
            "semanas": ((cuenta.get("sigma_dif_semanal") or {}).get("semanas")),
            "denominador_usd": cuenta.get("aportado_usd"),
            "juego": juego,
            "es_una_semilla": False,
            "estatus": "SIMULADO",   # salida de simulación; pasó por el adversario (re-dictamen D1)
        }
    except (KeyError, TypeError) as e:
        _log.warning("cuenta_papel.json sin la forma esperada en barrido_semillas: %s", e)
        return None


def _potencia_desde_artefacto(cuenta: dict) -> dict:
    """σ de la diferencia semanal CON intervalo, del artefacto de la cuenta
    reconstruida. Si el artefacto está retirado o no trae la σ, se declara
    RETIRADO y no viaja ningún número: la regla de la casa es que un
    estimador no viaja sin intervalo.

    Re-dictamen (corrida 12), D2 y D3: la etiqueta del intervalo NO se
    escribe a mano —viaja la advertencia del artefacto y la cobertura MEDIDA
    del IC de la desviación, leída del instrumento—, y el MDE80 del bloque 1
    se cita con SU σ (el ancla del simulador), nunca atribuido a la σ que
    esta tarjeta sirve."""
    sig = (cuenta or {}).get("sigma_dif_semanal") or {}
    retirado = (cuenta or {}).get("estatus") in (None, "RETIRADO")
    if retirado or sig.get("sigma_pp_semana") is None or not sig.get("ic95"):
        return {
            "sigma_dif_semanal_pp": None, "estatus": "RETIRADO",
            "nota": ("La σ semanal de la cuenta en papel v1 está RETIRADA por "
                     "fuga temporal demostrada (dictamen 10, F1 a F4) y viajaba "
                     "sin intervalo. La cifra vuelve cuando exista sobre una "
                     "cuenta sin fuga y con su intervalo.")}
    inst = _artefacto_gemelo("instrumento_dinero.json") or {}
    cal = (inst.get("calibracion") or {})
    clave_h = str(sig.get("semanas") or 156) if str(sig.get("semanas") or 156) in cal else "156"
    k156 = cal.get(clave_h) or {}
    cob_sd = k156.get("cobertura_ic_sd") or {}
    if cob_sd.get("tasa") is not None:
        tipo = (f"bootstrap circular de bloques de semanas, nominal 95 %, cobertura medida "
                f"{cob_sd['tasa']:.3f} {cob_sd.get('wilson95')} a {clave_h} semanas")
    else:
        tipo = "bootstrap circular de bloques de semanas, nominal 95 %, cobertura medida: no disponible"
    k52 = cal.get("52") or {}
    mde = k52.get("mde80_alpha_nominal") or {}
    mde_real = k52.get("mde80_alpha_real") or {}
    sigma_ancla = (inst.get("sigma_medida") or {}).get("sigma_pp_semana")
    # Dos frases separadas a propósito: la σ servida y el MDE80 nunca van en la
    # misma oración (D3; test en tests/test_api.py).
    cob_txt = (f"con cobertura medida {cob_sd['tasa']:.3f}, por debajo del 95 % nominal: el punto es "
               f"utilizable, el intervalo no" if cob_sd.get("tasa") is not None else
               "con intervalo de cobertura no medida: el punto es utilizable, el intervalo no")
    frase_sigma = (f"σ de la diferencia semanal juego por defecto − SMH sobre la cuenta "
                   f"reconstruida (8-sep-2026), {cob_txt}. Refleja UN sorteo de señal.")
    if mde.get("pp_semana") is not None and sigma_ancla is not None:
        frase_mde = (f"El MDE80 del bloque 1 es {mde['pp_semana']:.2f} pp/semana a 52 semanas "
                     f"(banda {mde.get('banda_pp_semana')} por la banda entre sorteos; "
                     f"{mde_real.get('pp_semana', float('nan')):.2f} al α real medido) y está computado con la σ ancla "
                     f"del simulador, {sigma_ancla:.3f} pp/semana, no con la σ de esta tarjeta. "
                     f"El instrumento fue puesto a prueba con verdad conocida: discrimina y NO está calibrado a α = 0,05.")
    else:
        frase_mde = ("El MDE80 del bloque 1 no está disponible en el artefacto del instrumento; no se cita "
                     "ningún número de potencia.")
    return {
        "sigma_dif_semanal_pp": sig["sigma_pp_semana"],
        "intervalo": sig["ic95"], "tipo_intervalo": tipo,
        "cobertura_medida_ic_sd": cob_sd or None,
        "advertencia_del_artefacto": sig.get("advertencia"),
        "semanas": sig.get("semanas"), "juego": sig.get("juego"), "base": sig.get("base"),
        "mde80_bloque_1": ({"pp_semana": mde.get("pp_semana"), "banda_pp_semana": mde.get("banda_pp_semana"),
                            "al_alpha_real_pp_semana": mde_real.get("pp_semana"),
                            "sigma_ancla_pp_semana": sigma_ancla, "horizonte_semanas": 52,
                            "convencion_anualizacion": mde.get("convencion_anualizacion"),
                            "pp_anio_suma_aritmetica": mde.get("pp_anio_suma_aritmetica"),
                            "pp_anio_capitalizado": mde.get("pp_anio_capitalizado")}
                           if mde.get("pp_semana") is not None else None),
        "estatus": "SIMULADO",   # salida de simulación; pasó por el adversario (re-dictamen D2/D3)
        "nota": frase_sigma + " " + frase_mde,
    }


def _que_mata_medicion() -> str:
    """R2 leído del artefacto de coherencia (`GEMELO/intervalo_coherencia.py`,
    rama «regla firmada»), no escrito a mano. La versión anterior decía que
    bajo la regla firmada R2 «NO está recomputada», y eso es falso desde el
    8-sep-2026 (re-dictamen, D11)."""
    base = ("V1–V7 y R1–R3 de GEMELO/DISEÑO.md §6, fijados antes de cualquier "
            "resultado. R2 —excluir la ventana 15–23 jul— ya golpeó al titular: la ventaja "
            "de la ventana completa no se distingue de cero (su IC de día contiene el cero), y ")
    coh = _artefacto_gemelo("intervalo_coherencia.json") or {}
    rama = next((r for r in coh.get("ramas", []) if "firmada" in str(r.get("rama", ""))), None)
    r2 = (rama or {}).get("R2_sin_15_23_jul") if rama else None
    if r2:
        return (base + f"bajo la regla de deduplicación firmada el 1-sep, sin esa ventana la ventaja "
                f"cae a {r2['ventaja_pp']:+.1f} pp (n={r2['n']}, {r2['dias']} días, IC95 t de clúster de día "
                f"{r2['ic95_t_cluster']}, permutación de día p = {r2['p_permutacion_dia']}, McNemar exacta "
                f"{r2['mcnemar_exacta']}): no se distingue de cero. Recomputado el 8-sep-2026 "
                f"(GEMELO/resultados/intervalo_coherencia.md §3b). La valla no se bajó.")
    return (base + "el R2 bajo la regla firmada no está disponible en el artefacto de coherencia "
            "(GEMELO/resultados/intervalo_coherencia.json); no se cita ningún número. La valla no se bajó.")


def _mapa_con_etiqueta(mapa: dict) -> dict | None:
    """D9 y D10: el resumen del mapa es la celda «techo (500 USD) / enteras»
    y sin decirlo el conteo de huecos es falso a 100 USD. Se sirve con
    presupuesto, modo, al_borde, días de censo y fecha, o no se sirve."""
    if not mapa or not mapa.get("resumen"):
        return None
    pres = (mapa.get("presupuesto") or {})
    techo = pres.get("techo_usd") if isinstance(pres, dict) else None
    celdas = ((mapa.get("censo_por_presupuesto_y_modo") or {}).get("celdas") or [])
    celda = next((x for x in celdas if x.get("modo") == "enteras" and x.get("presupuesto_usd") == techo), None)
    # días de censo DERIVADOS de las metas congeladas (curador #32): un día = una
    # sesión `hasta` distinta entre los congelados; el segundo congelado cayó en
    # la misma sesión y por eso hoy cuenta uno
    import glob as _glob
    hastas = set()
    for ruta_meta in _glob.glob(_os.path.join(_RAIZ, "dinero", "datos", "cierres_congelados*.meta.json")):
        try:
            with open(ruta_meta, encoding="utf-8") as f:
                hastas.add(_json.load(f).get("hasta"))
        except (OSError, ValueError) as e:
            _log.warning("meta del congelado ilegible: %s", e)
    hastas.discard(None)
    fecha_censo = max(hastas) if hastas else None
    dias_censo = len(hastas)
    if techo is None or celda is None:
        _log.warning("mapa sin presupuesto o sin la celda techo/enteras: no se sirve el resumen")
        return None
    return {
        **mapa["resumen"],
        "presupuesto_usd": techo, "modo": "enteras",
        "al_borde": celda.get("al_borde", []),
        "alcanzables": celda.get("alcanzables"),
        "dias_de_censo": dias_censo, "fecha_censo": fecha_censo,
        "nota": (f"Celda de {techo:.0f} USD en acciones enteras, censo de {dias_censo} día(s) (último: {fecha_censo}). "
                 f"No lleva intervalo porque la unidad de replicación es el día y n = {dias_censo}; el segundo "
                 "congelado cayó en la misma sesión (feriado NYSE del 7-sep) y no cuenta. A otros "
                 "presupuestos el resumen es otro: ver `censo_por_presupuesto_y_modo` en /api/dinero/universo."),
        "estatus": "PROPUESTA",
    }


@cache_ttl(600)
def _estado_rieles() -> dict:
    """Los dos rieles, uno al lado del otro. El de medición se lee del
    ÁRBITRO (`cifras.sellada()`), nunca de un número escrito a mano."""
    import cifras
    c = cifras.sellada()
    mapa = _artefacto("universo_operable.json") or {}
    cuenta = _artefacto("cuenta_papel.json") or {}
    larga = _artefacto("senal_larga_v1.json") or {}
    medicion = {
        "nombre": "Riel de medición",
        "estatus": "MEDIDO",
        "que_mide": ("si la apertura de Tokio, Taipéi y Seúl se puede "
                     "anticipar desde el cierre del SOX, con la predicción "
                     "sellada ANTES de la apertura que intenta predecir"),
        "horizonte": "una noche",
        "vara": "«siempre al alza», sobre las mismas filas",
        "mueve_plata": False,
        "muestra": {"n": c["n"], "dias": c["dias"],
                    "hasta_sello": c["hasta_sello"]},
        # `es_diferencia` NO es decoración: la frase «el intervalo no
        # contiene el cero» sólo significa algo sobre una DIFERENCIA. El
        # intervalo de Wilson de una tasa de acierto no puede contener el
        # cero nunca, así que decirlo debajo de un 67,6 % se lee como «el
        # efecto existe» al lado de la ventaja de verdad, que sí lo
        # contiene. Exigencia 9 del `curador-epistemico`, corrida 10.
        "cifras": [
            {"nombre": "acierto del modelo", "valor_pct": c["modelo_pct"],
             "intervalo": c["modelo_wilson"], "tipo_intervalo": "Wilson 95 %",
             "es_diferencia": False, "comparar_contra": "acierto de la base"},
            {"nombre": "acierto de la base", "valor_pct": c["base_pct"],
             "intervalo": c["base_wilson"], "tipo_intervalo": "Wilson 95 %",
             "es_diferencia": False, "comparar_contra": None},
            {"nombre": "ventaja sobre la base", "valor_pct": c["ventaja_pp"],
             "intervalo": c["ventaja_ic_dia"],
             "tipo_intervalo": "IC95 de clúster de día",
             "es_diferencia": True,
             "cruza_cero": c["ventaja_ic_dia"][0] <= 0 <= c["ventaja_ic_dia"][1]},
            {"nombre": "ganancia de MAE sobre predecir cero",
             "valor_pct": c["mae_ganancia_pp"],
             "intervalo": c["mae_ganancia_ic_t_dia"],
             "tipo_intervalo": "IC95 t de clúster de día",
             "es_diferencia": True,
             "cruza_cero": (c["mae_ganancia_ic_t_dia"][0] <= 0 <=
                            c["mae_ganancia_ic_t_dia"][1])},
            {"nombre": "cobertura del intervalo 80 %", "valor_pct": c["cobertura_80_pct"],
             "intervalo": c.get("cobertura_80_wilson"), "tipo_intervalo": "Wilson 95 %",
             "es_diferencia": False, "comparar_contra": "80 % nominal (V3 se juzga contra [76, 84])"},
        ],
        # El contrato prometía McNemar y el endpoint no lo servía. Manda la
        # máquina: se sirve, con el caveat que lo vuelve legible.
        "mcnemar_p_filas": c["mcnemar_p"],
        "mcnemar_caveat": ("Es un p de FILAS. Las ocho filas de un día no "
                           "son observaciones independientes (ICC 0,39, "
                           "DEFF 3,55): manda el intervalo de clúster de "
                           "día, que contiene el cero."),
        "cobertura_80_pct": c["cobertura_80_pct"],
        # D12: una proporción de esta casa viaja con su Wilson
        "cobertura_80": {"valor_pct": c["cobertura_80_pct"], "intervalo": c.get("cobertura_80_wilson"),
                         "tipo_intervalo": "Wilson 95 %", "k": c.get("cobertura_80_k"), "n": c.get("cobertura_80_n"),
                         "nominal_pct": 80.0},
        "n_efectivo": c["n_efectivo"], "icc": c["icc"], "deff": c["deff"],
        # D13: n en un solo régimen es más chico que n
        "regimenes_en_ventana": c.get("regimenes_en_ventana"),
        "un_solo_regimen": c.get("un_solo_regimen"),
        "etiqueta_regimen": (("UN SOLO RÉGIMEN en la ventana sellada (%s): la muestra no dice nada sobre "
                              "otros regímenes." % ", ".join(f"{k}: {v} snapshots" for k, v in (c.get("regimenes_en_ventana") or {}).items()))
                             if c.get("un_solo_regimen") else
                             ("Regímenes en la ventana: %s." % ", ".join(f"{k}: {v} snapshots" for k, v in (c.get("regimenes_en_ventana") or {}).items()))),
        "falta_para_veredicto": (
            "El veredicto 5.1 está pre-registrado en backtest/DISEÑO.md y su "
            "ejecución es decisión humana. Gatillo: N ≥ 150 filas selladas "
            "más un cambio de régimen, o 3 meses, lo que llegue primero."),
        "que_lo_mata": _que_mata_medicion(),
        "procedencia": c["procedencia"],
    }
    dinero = {
        "nombre": "Riel de dinero",
        "estatus": "SIMULADO",
        "que_mide": ("si un movimiento en un eslabón anticipa el de otro "
                     "aguas abajo, y si actuar sobre eso supera a comprar un "
                     "ETF del sector todas las semanas sin decidir nada"),
        "horizonte": "semanas (20 y 60 días hábiles)",
        "vara": "aporte fijo semanal a SMH, con los mismos costos",
        "mueve_plata": False,
        "muestra": {"filas_selladas": 0,
                    "nota": ("CERO filas selladas. El track record "
                             "prospectivo es del riel de medición, no de "
                             "éste. Nada de este riel es evidencia del mismo "
                             "tipo.")},
        "mapa": _mapa_con_etiqueta(mapa),
        # La v1 de la cuenta en papel tuvo fuga temporal DEMOSTRADA
        # (dictamen 10, F1 a F4) y estuvo RETIRADA del 7 al 8-sep-2026; la v2
        # (corrida 11, acta §82.4) se reconstruyó sin fuga y con gate de
        # invariancia. `cifras_disponibles` se lee del artefacto: mientras
        # el estatus sea RETIRADO este endpoint sirve el motivo del retiro y
        # nada más, porque servir el número con una advertencia al lado
        # sería seguir haciéndolo circular.
        "cuenta_en_papel": ({
            "estatus": cuenta.get("estatus"),
            "version": cuenta.get("version"),
            "retirado": cuenta.get("retirado"),
            "reconstruccion": ({
                "fecha": cuenta["reconstruccion"].get("fecha"),
                "gate_invariancia": (cuenta["reconstruccion"].get("gate_invariancia") or {}).get("resultado"),
            } if cuenta.get("reconstruccion") else None),
            "advertencia": cuenta.get("advertencia"),
            "cifras_disponibles": cuenta.get("estatus") not in (None, "RETIRADO"),
            "comisiones_pct_del_aportado_juego_activo": _comisiones_juego_activo(cuenta),
        } if cuenta else None),
        "senal_larga": ({
            "estatus": larga.get("estatus"),
            "multiplicidad": larga.get("multiplicidad", {}).get(
                "familia_contrastes"),
            "pasan_holm": larga.get("multiplicidad", {}).get("pasan"),
            **(larga.get("resumen") or {}),
            # D15: dos denominadores en el mismo objeto se leen como «1 de 30».
            "denominadores": {
                "ganan_sin_corregir_es_sobre": "celdas",
                "celdas": (larga.get("resumen") or {}).get("celdas"),
                "contrastes_familia_holm": (larga.get("resumen") or {}).get("contrastes"),
                "k_bajo_la_nula": None,
                "nota": ("El k de «ganan a la climatología sin corregir» es sobre las CELDAS (no sobre los "
                         "30 contrastes de la familia de Holm). La distribución de k bajo la nula con el "
                         "ICC medido no está computada: ningún «k de m» de este bloque se lee como tasa."),
            },
        } if larga else None),
        "falta_para_veredicto": (
            "52 semanas de cuenta en papel hacia adelante, con la señal "
            "congelada, UNA comparación declarada y una sola mirada al final "
            "(dinero/preregistro_dinero.md §2). Hoy: 0 semanas."),
        "que_lo_mata": (
            "M1: 104 semanas sin distinguirse del cero y con punto negativo. "
            "M2: comisión acumulada sobre el 25 % del capital — la cifra "
            "vieja (14 % a 43 %) está RETIRADA por fuga; la cuenta "
            "reconstruida el 8-sep mide la comisión sobre 156 semanas, pero "
            "M2 sigue sin poder leerse hasta que se fije su período (§43, "
            "decisión de Nicolás). M3: cualquier fuga — disparó en la v1 de "
            "la cuenta en papel; la v2 pasa el gate de invariancia y el auditor "
            "no encontró fuga (dictamen 11, PROPUESTA). M4: que la señal larga no supere ninguna vara; hoy no "
            "se puede dar por leído, porque la segunda vara pre-registrada "
            "no se evaluó."),
        # σ salía de la cuenta en papel, que está retirada por fuga; y
        # viajaba como número suelto, sin intervalo, contra la regla que
        # este mismo bloque declara arriba. No viaja más hasta que se
        # recompute con su intervalo sobre una cuenta sin fuga.
        "potencia": _potencia_desde_artefacto(cuenta),
    }
    return {"rieles": [medicion, dinero],
            "por_que_son_dos": (
                "El proyecto mide una noche y quiere operar en semanas. Las "
                "dos cosas son legítimas y no son la misma. Ver VISION.md.")}


@app.get("/api/rieles")
def rieles():
    return {"meta": _meta_simple(), "datos": _estado_rieles()}


# ============================================================
# E0 / E1 — lo que la máquina decidió para la próxima apertura (corrida 12,
# bloque 5). Regla del bloque: cada número lleva estatus, n donde exista y
# fuente. Solo lectura: `dinero/sello_dinero.db` en mode=ro y artefactos.
# ============================================================
def _e1_estado() -> dict:
    """E1 (cuenta de práctica): NO EJECUTADO en la corrida 12. La pantalla
    muestra un estado vacío que dice qué falta; NUNCA datos de ejemplo
    (pre-mortem 20). Cuando E1 corra, este objeto trae posiciones, efectivo y
    ejecuciones leídas por API con su marca de retraso."""
    return {
        "estado": "NO EJECUTADO",
        "etiqueta": "PRÁCTICA",
        "por_que": ("sin credenciales de cuenta de práctica ni gateway del corredor en la máquina "
                    "(chequeo 0.7 de la corrida 12, 8-sep-2026 23:25, sondeo TCP de lectura sin "
                    "órdenes); y de noche NYSE está cerrada, así que «enviar una orden y leer su "
                    "ejecución en el mismo ciclo» no era ejecutable aunque hubiera cuenta"),
        "adaptador": "corredor/ibkr.py (guardia de papel en código, probado contra réplica escrita desde documentación: NO es evidencia de C1/C2)",
        "cuenta_practica": None, "posiciones": None, "efectivo": None, "ejecuciones": None,
        "marca_retraso": None,
        "estatus": "PROPUESTA",
    }


@app.get("/api/dinero/sellos")
def dinero_sellos():
    from dinero import sello_dinero as S
    e = S.estado()
    cuenta = _artefacto("cuenta_papel.json") or {}
    gate = ((cuenta.get("reconstruccion") or {}).get("gate_invariancia") or {})
    ult = e.get("ultimo")
    return {"meta": _meta_simple(), "datos": {
        "estatus": "PROPUESTA",
        "que_es": ("E0 del riel de dinero: la decisión del juego por defecto para la PRÓXIMA apertura "
                   "de NYSE, sellada por la máquina antes de esa apertura, con tamaño nominal CERO. "
                   "Nada de esta pantalla mueve plata ni afirma una ventaja."),
        "senal_fuente": e["senal_fuente"],
        "E0": {"estado": "EN CURSO" if e["sesiones_selladas"] else "SIN FILAS",
               "sesiones_selladas": e["sesiones_selladas"],
               "sesiones_que_cuentan_para_N": e["sesiones_que_cuentan_para_N"],
               "N_objetivo": e["N_objetivo"], "N_objetivo_fuente": e["N_objetivo_fuente"],
               "fuente_conteos": e["fuente_conteos"], "filas": e["filas"],
               "divergencias_registradas": e.get("divergencias_registradas", 0),
               "nota": ("Cuentan sólo las sesiones con fila pendiente de un día con sesión e insumo fresco. "
                        "Estas filas prueban la maquinaria del sellado prospectivo (señal sin información): "
                        "no son un track record de habilidad."),
               "estatus": "PROPUESTA"},
        "E1": _e1_estado(),
        "ultimo_sello": ult,
        "decisiones_proxima_apertura": e["filas_ultimo_sello"],
        "gate_invariancia_ultima_corrida": {
            "resultado": gate.get("resultado"), "cortes": len(gate.get("cortes") or []),
            "fecha": (cuenta.get("reconstruccion") or {}).get("fecha"),
            "fuga_inyectada": gate.get("fuga_inyectada"),
            "alcance": gate.get("alcance"),
            "fuente": "dinero/resultados/cuenta_papel.json (gate de la cuenta en papel v2)",
            "nota_e0": ("Este gate es el de la CUENTA EN PAPEL v2 (corrida 11, 25 cortes), no de la maquinaria de "
                        "sellado de E0. E0 tiene su propio gate de decisión (dinero/sello_dinero.py, penúltimo día y 6 "
                        "sesiones atrás), que corre antes de cada sello y cuyo resultado queda en el log del sellador, "
                        "no en esta pantalla todavía."),
            "estatus": "PROPUESTA"},
        "smh": ("SMH es el benchmark declarado del proyecto y NO cabe con el piso de acciones enteras a "
                "ningún presupuesto del rango: el riel se compara contra él como línea base sin poder "
                "tomar posición (acta §84.4.6)."),
    }}
