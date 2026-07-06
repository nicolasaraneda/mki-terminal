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
from api.utilidades import cache_ttl, dias_a_proximos_earnings, ohlc_1y, serie_a_lista
from universo import (ACCIONES, BENCHMARK, EXCHANGE_POR_TICKER, MERCADOS_POR_ABRIR,
                      MONEDA_TICKER, NIVELES_CADENA, TICKERS_POR_NIVEL, UNIVERSO,
                      nombre)
from version import FEATURE_VERSION, MODELO_VERSION, UNIVERSO_VERSION

app = FastAPI(title="MKI Terminal API", version="1.0",
              description="API de solo lectura sobre el motor de señales MKI")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost(:\d+)?|http://127\.0\.0\.1(:\d+)?",
    allow_methods=["GET"],
    allow_headers=["*"],
)

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
                      "universo": UNIVERSO_VERSION},
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
            par = pd.concat([ret_nivel[a].shift(lag), ret_nivel[b]], axis=1).dropna()
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
        par_k = pd.concat([rs, rk], axis=1).dropna().tail(252)
        par_x0 = pd.concat([rs, rx], axis=1).dropna().tail(252)
        par_x1 = pd.concat([rs, rx.shift(1)], axis=1).dropna().tail(252)
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
