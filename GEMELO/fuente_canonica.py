"""Frente A de la séptima corrida (2-sep-2026): ¿cuánta historia mutó?

Mide, contra lo que el proyecto GUARDÓ, cuánto cambió lo que la fuente
(Yahoo) SIRVE HOY. Cuatro testigos, cada uno con su fecha de captura:

  M1  Las cachés de `GEMELO/cache/` con `mtime` 26-ago-2026 (8 años de
      cierres, 8 y 27 tickers): una foto involuntaria de la fuente.
  M2  `snapshots.sox_usado_pct` sellado por producción (desde 27-jul).
  M3  `verificacion_apertura.gap_pct` / `retorno_real_pct` sellados por el
      verificador desde el Open/Close de la sesión objetivo.
  M4  `senales_ticker.apertura_estimada_pct` / `beta` sellados al emitir,
      contra `motor.prediccion_apertura_al(fecha)` re-corrido hoy.

Y un censo (M5) de sesiones de calendario sin barra hoy, por símbolo, que
NO distingue «retirada» de «nunca existió» y se declara así.

Reglas: `senales.db` sólo en `mode=ro`; las cachés NO se reescriben
(`usar_cache=False` en toda descarga); no se toca ninguna fila sellada; no
importa nada de la ruta de sellado salvo funciones PURAS de `motor` y
`calendarios` (la dirección protegida es la contraria: nada del sellado
importa esto). El objeto bajo prueba es el DATO, no el mecanismo: por eso
la derivación se mantiene idéntica a la de producción (§2.4 de
`docs/SEGUNDO_SELLO.md`).

Distinción que gobierna M1 (y que el expediente PIT ya formuló como
teorema): con `auto_adjust=True` un dividendo nuevo reescala TODO el
pasado de un ticker. Eso cambia NIVELES sin cambiar RETORNOS, y las
señales usan retornos. Por eso cada diferencia de valor se clasifica en
`proporcional` (el retorno diario no cambia) o `no_proporcional`.

Uso: `python GEMELO/fuente_canonica.py` → escribe
`GEMELO/resultados/fuente_canonica.json` y `fuente_canonica_medicion.md`
(el expediente con candidatas y diseño es `fuente_canonica.md`, escrito a mano
desde esas cifras).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(_AQUI)
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

import calendarios                                   # noqa: E402  (puro)
from backtest.datos import _conexion_ro               # noqa: E402  (la capa auditada de solo lectura)
from GEMELO import datos as gd                       # noqa: E402
from universo import (EXCHANGE_POR_TICKER, MERCADOS_POR_ABRIR,  # noqa: E402
                      UNIVERSO)

RUTA_SENALES = os.path.join(_RAIZ, "senales.db")
DIR_RESULTADOS = os.path.join(_AQUI, "resultados")
DIR_CACHE = gd.DIR_CACHE

# Tolerancias: el sello redondea a 2 decimales (`sox_usado_pct`, apertura,
# beta) y el verificador a 4 (`gap_pct`, `retorno_real_pct`). Media unidad
# del último decimal, como en `segundo_sello.TOLERANCIA_PP`.
TOL_2DEC = 0.005
TOL_4DEC = 0.00005
# Igualdad de un cierre crudo de Yahoo (float32 promovido a float64).
TOL_REL_NIVEL = 1e-6
# Un reescalado por dividendo deja los retornos iguales salvo ruido de
# float32 (medido: hasta 1,3e-6 en retorno); 5e-6 ABSOLUTO = 0,0005 pp, tres
# órdenes por debajo de lo que mueve un signo o un decimal sellado.
TOL_ABS_RETORNO = 5e-6

# Las dos cachés del 26-ago (8 años). Se identifican por la clave que
# `GEMELO.datos._ruta_cache` deriva de (tickers, anios): no por el nombre.
CACHES_TESTIGO = (
    (tuple(MERCADOS_POR_ABRIR), gd.ANIOS_DATOS),
    (tuple(UNIVERSO), gd.ANIOS_DATOS),
)


def _conn_ro():
    """Toda lectura de `senales.db` pasa por la capa de solo lectura del
    backtest (`mode=ro`), como el resto de GEMELO: este módulo no abre
    conexiones por su cuenta."""
    return _conexion_ro(RUTA_SENALES)


# ------------------------------------------------------------
# M1 · cachés del 26-ago contra la fuente de hoy
# ------------------------------------------------------------
def clasificar_celdas(viejo: pd.DataFrame, nuevo: pd.DataFrame,
                      hasta: str) -> dict:
    """Compara dos paneles de cierres (fecha × ticker) hasta `hasta`.

    Por ticker cuenta: `paridad` (mismo valor), `retirada` (había valor,
    hoy NaN o la fecha no existe), `aparecida` (NaN antes, valor hoy),
    `distinta` (dos valores distintos) y, dentro de `distinta`, cuántas
    son `proporcional` (el retorno diario del día no cambió: reescalado
    de la serie entera, típico de un dividendo bajo auto_adjust) y
    cuántas `no_proporcional` (el retorno cambió: eso sí mueve una señal).
    Devuelve también las fechas con alguna barra retirada por ticker.
    """
    # Ventana COMÚN: `period="8y"` desliza el inicio con la fecha de la
    # descarga, así que las primeras fechas de la caché faltan hoy por
    # construcción, no por retiro. Se comparan sólo desde el inicio común.
    desde = max(viejo.index.min(), nuevo.index.min())
    viejo = viejo.loc[(viejo.index >= desde) & (viejo.index <= pd.Timestamp(hasta))]
    fechas = viejo.index.union(nuevo.index[(nuevo.index >= desde) & (nuevo.index <= pd.Timestamp(hasta))])
    v = viejo.reindex(fechas)
    n = nuevo.reindex(fechas)
    rv = v.pct_change()
    rn = n.pct_change()
    salida = {}
    for t in viejo.columns:
        if t not in nuevo.columns:
            salida[t] = {"sin_serie_hoy": True}
            continue
        a, b = v[t], n[t]
        hay_a, hay_b = a.notna(), b.notna()
        paridad = hay_a & hay_b & (np.abs(a - b) <= TOL_REL_NIVEL * np.abs(a))
        distinta = hay_a & hay_b & ~paridad
        retirada = hay_a & ~hay_b
        aparecida = ~hay_a & hay_b
        # La última fecha de la caché puede ser una sesión que aún no había
        # cerrado al capturar (Asia a medio día, EEUU antes de abrir): una
        # celda NaN o parcial ahí no es mutación de la historia. Se separa de
        # TODO lo histórico: de `distinta`, de `proporcional` y del factor
        # (dictamen del adversario, 2-sep: la primera versión la dejaba
        # dentro de `distinta` y el "factor" que reportaba era la barra viva).
        ultima = fechas == viejo.index.max()
        aparecida_ultima = aparecida & ultima
        aparecida = aparecida & ~ultima
        distinta_ultima = distinta & ultima
        distinta = distinta & ~ultima
        # proporcional: el retorno del día NO cambió aunque el nivel sí
        ra, rb = rv[t], rn[t]
        ret_igual = ra.notna() & rb.notna() & (np.abs(ra - rb) <= TOL_ABS_RETORNO)
        prop = distinta & ret_igual
        no_prop = distinta & ~ret_igual & ra.notna() & rb.notna()
        no_prop_ultima = no_prop & ultima
        no_prop = no_prop & ~ultima
        max_dret = float(np.nanmax(np.abs(ra - rb)[~ultima])) if (~ultima).any() else 0.0
        # Lo que una señal ve: cuántos RETORNOS diarios cambiaron (un precio
        # revisado mueve dos: el de su día y el del siguiente).
        ret_cambiado = ra.notna() & rb.notna() & (np.abs(ra - rb) > TOL_ABS_RETORNO) & ~ultima
        # factor de reescalado, si toda la parte distinta HISTÓRICA comparte uno
        factor = None
        if distinta.any():
            f = (b[distinta] / a[distinta])
            if f.notna().any() and (f.max() - f.min()) <= 1e-6 * f.abs().max():
                factor = float(f.iloc[0])
        salida[t] = {
            "celdas": int((hay_a | hay_b).sum()),
            "paridad": int(paridad.sum()),
            "distinta": int(distinta.sum()),
            "proporcional": int(prop.sum()),
            "no_proporcional": int(no_prop.sum()),
            "retornos_cambiados": int(ret_cambiado.sum()),
            "retirada": int(retirada.sum()),
            "aparecida": int(aparecida.sum()),
            "ultima_fecha_parcial_o_nueva": int((aparecida_ultima | no_prop_ultima | distinta_ultima).sum()),
            "max_abs_dif_retorno": max_dret,
            "factor_reescalado": factor,
            "fechas_retiradas": [d.date().isoformat() for d in a.index[retirada]],
            "fechas_no_proporcionales": [d.date().isoformat() for d in a.index[no_prop]][:20],
            "fechas_retornos_cambiados": [d.date().isoformat() for d in a.index[ret_cambiado]][:20],
        }
    return salida


def m1_caches_vs_hoy() -> dict:
    resultado = {"testigos": [], "nota": (
        "Cada caché es la fuente tal como la sirvió Yahoo en el `mtime` del "
        "archivo. Se compara sólo hasta la última fecha de la caché; las "
        "descargas de hoy se hacen con usar_cache=False para NO reescribirla.")}
    for tickers, anios in CACHES_TESTIGO:
        ruta = gd._ruta_cache(tickers, anios)
        if not os.path.exists(ruta):
            resultado["testigos"].append({"ruta": ruta, "existe": False})
            continue
        mtime = datetime.fromtimestamp(os.path.getmtime(ruta), tz=timezone.utc)
        viejo = pd.read_csv(ruta, index_col=0, parse_dates=True)
        nuevo = gd.descargar_cierres(tickers, anios, usar_cache=False)
        hasta = viejo.index.max().date().isoformat()
        por_ticker = clasificar_celdas(viejo, nuevo, hasta)
        tot = {k: sum(v.get(k, 0) for v in por_ticker.values() if isinstance(v.get(k, 0), int))
               for k in ("celdas", "paridad", "distinta", "proporcional",
                         "no_proporcional", "retornos_cambiados", "retirada", "aparecida")}
        fechas_ret = sorted({d for v in por_ticker.values()
                             for d in v.get("fechas_retiradas", [])})
        tot["ultima_fecha_parcial_o_nueva"] = sum(
            v.get("ultima_fecha_parcial_o_nueva", 0) for v in por_ticker.values())
        tot["max_abs_dif_retorno"] = max(
            (v.get("max_abs_dif_retorno", 0.0) for v in por_ticker.values()), default=0.0)
        resultado["testigos"].append({
            "ruta": os.path.relpath(ruta, _RAIZ),
            "capturada_en_utc": mtime.isoformat(),
            "tickers": len(viejo.columns),
            "fechas": int(len(viejo.index)),
            "desde": viejo.index.min().date().isoformat(),
            "hasta": hasta,
            "totales": tot,
            "fechas_con_alguna_retirada": fechas_ret,
            "por_ticker": por_ticker,
        })
    return resultado


# ------------------------------------------------------------
# M2 · el SOX sellado contra el SOX de hoy (lógica de producción)
# ------------------------------------------------------------
def _sox_fresco() -> pd.Series:
    import motor  # funciones puras; la descarga se hace ACÁ, no por su caché
    import yfinance as yf
    d = yf.download("^SOX", period=f"{motor.ANIOS_DATOS}y", interval="1d",
                    auto_adjust=True, progress=False)
    c = d["Close"]
    if isinstance(c, pd.DataFrame):
        c = c.iloc[:, 0]
    return c.dropna()


def m2_sox_sellado_vs_hoy(sox: pd.Series) -> dict:
    import motor
    with _conn_ro() as c:
        filas = c.execute(
            "SELECT fecha, sox_usado_pct, sox_fecha, timestamp_utc FROM snapshots "
            "WHERE sox_usado_pct IS NOT NULL ORDER BY fecha").fetchall()
    out = []
    for fecha, sellado, sox_fecha, ts in filas:
        serie = sox[sox.index.date <= date.fromisoformat(fecha)]
        mov, f = motor._ultimo_mov_no_cero(serie.pct_change())
        f = f.isoformat() if f else None
        previa_hoy = None
        if f is not None:
            idx = serie.index[serie.index.date <= date.fromisoformat(f)]
            previa_hoy = idx[-2].date().isoformat() if len(idx) >= 2 else None
        previa_cal = calendarios.sesion_anterior("XNYS", f) if f else None
        if mov is None:
            veredicto = "SIN_DATO_HOY"
        elif f != sox_fecha:
            veredicto = "BARRA_RETIRADA"          # la barra del sello no está hoy
        elif abs(mov - sellado) <= TOL_2DEC:
            veredicto = "PARIDAD"
        elif previa_hoy != previa_cal:
            veredicto = "BARRA_PREVIA_RETIRADA"   # el retorno de hoy salta una sesión
        else:
            veredicto = "DIVERGENCIA_DE_VALOR"
        out.append({"fecha": fecha, "sellado_pct": sellado, "sellado_fecha": sox_fecha,
                    "hoy_pct": None if mov is None else round(mov, 4),
                    "hoy_fecha": f, "dif_pp": None if mov is None else round(mov - sellado, 4),
                    "previa_calendario": previa_cal, "previa_usada_hoy": previa_hoy,
                    "veredicto": veredicto, "timestamp_utc": ts})
    conteo = {}
    for r in out:
        conteo[r["veredicto"]] = conteo.get(r["veredicto"], 0) + 1
    return {"n_fechas": len(out), "conteo": conteo, "filas": out}


# ------------------------------------------------------------
# M3 · verificaciones selladas contra Open/Close de hoy (lógica del verificador)
# ------------------------------------------------------------
def _ohlc(ticker: str, desde: str) -> pd.DataFrame:
    import yfinance as yf
    d = yf.download(ticker, start=desde, auto_adjust=True, progress=False)
    if d.empty:
        return pd.DataFrame()
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    return d[["Open", "Close"]].dropna(how="all")


def m3_verificaciones_vs_hoy() -> dict:
    with _conn_ro() as c:
        filas = c.execute("""
            SELECT v.fecha_senal, v.ticker, v.apertura_estimada_pct, v.gap_pct,
                   v.retorno_real_pct, v.acierto_gap, v.acierto_direccion,
                   s.sesion_objetivo, s.exchange, v.verificado_en
            FROM verificacion_apertura v
            JOIN senales_ticker s ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
            WHERE v.legacy = 0 AND v.modelo_version = '4.6.0'
            ORDER BY v.fecha_senal, v.ticker""").fetchall()
    desde = (pd.Timestamp(min(r[0] for r in filas)) - pd.Timedelta(days=21)).date().isoformat()
    ohlc = {t: _ohlc(t, desde) for t in sorted({r[1] for r in filas})}
    out = []
    for (fs, t, est, gap_s, ret_s, ag_s, ad_s, sobj, exch, ver_en) in filas:
        d = ohlc[t]
        fechas = list(d.index.strftime("%Y-%m-%d")) if not d.empty else []
        fila = {"fecha_senal": fs, "ticker": t, "sesion_objetivo": sobj,
                "gap_sellado": gap_s, "retorno_sellado": ret_s,
                "acierto_gap_sellado": ag_s, "verificado_en": ver_en}
        if sobj not in fechas:
            fila.update(veredicto="BARRA_OBJETIVO_RETIRADA")
            out.append(fila)
            continue
        i = fechas.index(sobj)
        sesion_ant = calendarios.sesion_anterior(exch, sobj)
        previos = d.iloc[:i]
        previos = previos[previos.index >= pd.Timestamp(sesion_ant) - pd.Timedelta(days=7)]
        if previos.empty:
            fila.update(veredicto="SIN_BARRA_PREVIA_HOY")
            out.append(fila)
            continue
        close_ant = float(previos["Close"].iloc[-1])
        fecha_ant = previos.index[-1].date().isoformat()
        open_obj = float(d["Open"].iloc[i])
        close_obj = float(d["Close"].iloc[i])
        gap = round((open_obj / close_ant - 1) * 100, 4)
        ret = round((close_obj / close_ant - 1) * 100, 4)
        ag = 1 if (est >= 0) == (gap >= 0) else 0
        dg, dr = gap - gap_s, ret - ret_s
        if abs(dg) <= TOL_4DEC and abs(dr) <= TOL_4DEC:
            v = "PARIDAD"
        elif abs(dg) <= 3 * TOL_4DEC and abs(dr) <= 3 * TOL_4DEC:
            v = "PARIDAD_REDONDEO"    # ±1 en el 4º decimal: ruido de float, no dato
        elif fecha_ant != sesion_ant:
            v = "BARRA_PREVIA_DISTINTA"   # la previa usada hoy no es la del calendario
        else:
            v = "DIVERGENCIA_DE_VALOR"
        fila.update(veredicto=v, gap_hoy=gap, retorno_hoy=ret, dif_gap_pp=round(dg, 4),
                    dif_retorno_pp=round(dr, 4), acierto_gap_hoy=ag,
                    acierto_gap_cambia=int(ag != ag_s), previa_calendario=sesion_ant,
                    previa_usada_hoy=fecha_ant)
        out.append(fila)
    conteo = {}
    for r in out:
        conteo[r["veredicto"]] = conteo.get(r["veredicto"], 0) + 1
    cambia = sum(r.get("acierto_gap_cambia", 0) for r in out)
    return {"n_filas": len(out), "conteo": conteo,
            "filas_cuyo_acierto_gap_cambia": int(cambia), "filas": out}


# ------------------------------------------------------------
# M4 · aperturas y betas selladas contra el motor re-corrido hoy
# ------------------------------------------------------------
def m4_emisiones_vs_motor_hoy() -> dict:
    import motor
    with _conn_ro() as c:
        filas = c.execute("""
            SELECT fecha, ticker, apertura_estimada_pct, beta, estado
            FROM senales_ticker
            WHERE apertura_estimada_pct IS NOT NULL AND modelo_version = '4.6.0'
            ORDER BY fecha, ticker""").fetchall()
    por_fecha = {}
    for f, t, ap, b, e in filas:
        por_fecha.setdefault(f, []).append((t, ap, b, e))
    out, por_fecha_res = [], []
    for f in sorted(por_fecha):
        try:
            pred = motor.prediccion_apertura_al(date.fromisoformat(f))
        except Exception as exc:  # una fecha que no reproduce se declara
            por_fecha_res.append({"fecha": f, "error": str(exc)[:200]})
            continue
        pred = pred.set_index("Ticker") if "Ticker" in pred.columns else pred
        n_par = n_ap = n_beta = n_signo = 0
        for t, ap, b, e in por_fecha[f]:
            fila = {"fecha": f, "ticker": t, "estado": e, "apertura_sellada": ap,
                    "beta_sellada": b}
            if t not in pred.index:
                fila["veredicto"] = "SIN_PREDICCION_HOY"
                out.append(fila)
                continue
            ap_h = float(pred.loc[t, "Apertura estimada %"])
            b_h = float(pred.loc[t, "Beta de contagio"])
            fila.update(apertura_hoy=ap_h, beta_hoy=b_h,
                        dif_apertura_pp=round(ap_h - ap, 4),
                        dif_beta=None if b is None else round(b_h - b, 4),
                        signo_cambia=int((ap_h >= 0) != (ap >= 0)))
            ok_ap = abs(ap_h - ap) <= TOL_2DEC
            ok_b = b is None or abs(b_h - b) <= TOL_2DEC
            fila["veredicto"] = "PARIDAD" if (ok_ap and ok_b) else "DIVERGENCIA"
            n_par += ok_ap and ok_b
            n_ap += not ok_ap
            n_beta += not ok_b
            n_signo += fila["signo_cambia"]
            out.append(fila)
        por_fecha_res.append({"fecha": f, "filas": len(por_fecha[f]), "paridad": int(n_par),
                              "apertura_distinta": int(n_ap), "beta_distinta": int(n_beta),
                              "signo_cambia": int(n_signo)})
    conteo = {}
    for r in out:
        conteo[r["veredicto"]] = conteo.get(r["veredicto"], 0) + 1
    return {"n_filas": len(out), "n_fechas": len(por_fecha), "conteo": conteo,
            "filas_con_signo_cambiado": int(sum(r.get("signo_cambia", 0) for r in out)),
            "por_fecha": por_fecha_res, "filas": out}


# ------------------------------------------------------------
# M5 · censo de sesiones de calendario sin barra hoy (NO distingue causa)
# ------------------------------------------------------------
def m5_censo_huecos(panel: pd.DataFrame, anios: int = 3) -> dict:
    import exchange_calendars as xc
    # Tope: la última sesión XNYS ya cerrada (Asia ya tiene barra de HOY a
    # esta hora; contar la sesión en curso como "sin barra" sería fabricar).
    hasta = pd.Timestamp(calendarios.sesion_anterior(
        "XNYS", datetime.now(timezone.utc).date().isoformat()))
    hasta = min(hasta, panel.index.max())
    desde = hasta - pd.DateOffset(years=anios)
    out = {}
    cal_cache = {}
    for t in panel.columns:
        exch = EXCHANGE_POR_TICKER.get(t, "XNYS")
        if exch not in cal_cache:
            cal_cache[exch] = xc.get_calendar(exch)
        cal = cal_cache[exch]
        sesiones = cal.sessions_in_range(desde.date().isoformat(), hasta.date().isoformat())
        serie = panel[t].loc[desde:hasta]
        con_barra = set(serie.dropna().index.normalize())
        faltan = [s for s in sesiones if s.normalize() not in con_barra]
        out[t] = {"exchange": exch, "sesiones_calendario": len(sesiones),
                  "sin_barra_hoy": len(faltan),
                  "ultimas_5": [s.date().isoformat() for s in faltan[-5:]]}
    return {"anios": anios, "hasta": hasta.date().isoformat(), "por_ticker": out,
            "nota": ("Cuenta sesiones del calendario del exchange sin barra en la "
                     "descarga de hoy. NO distingue una barra retirada de una que "
                     "nunca existió (feriado no modelado, símbolo sin cotizar): "
                     "sólo los testigos M1–M4 pueden decir «estaba y ya no está».")}


# ------------------------------------------------------------
# M6 · hipótesis ejecutable: ¿una sola barra ausente explica una fecha?
# ------------------------------------------------------------
def m6_hipotesis_barra_transitoria(m4: dict, umbral_beta: float = 0.05,
                                   minimo_filas: int = 4, barras: int = 130) -> dict:
    """Para cada fecha de emisión cuyas betas selladas NO reproducen hoy
    (≥ `minimo_filas` filas con |Δbeta| > `umbral_beta`), prueba la
    hipótesis más simple: que al sellar la fuente sirvió el `^SOX` SIN una
    barra que hoy sí sirve. Quita una barra por vez (las últimas `barras`
    hasta la fecha), recomputa `motor.betas_al` con `_datos_crudos`
    parcheado y reporta la barra cuyo retiro deja las betas más cerca de
    las selladas. Es una hipótesis, no un testigo: la única forma de
    convertirla en hecho sería una copia del `^SOX` tomada esa noche, que
    no existe (§ diseño del congelado).
    """
    from unittest import mock
    import motor
    orig = motor._datos_crudos
    with _conn_ro() as c:
        sel = pd.read_sql(
            "SELECT fecha, ticker, beta FROM senales_ticker "
            "WHERE beta IS NOT NULL AND modelo_version = '4.6.0'", c)
    candidatas = [r["fecha"] for r in m4["por_fecha"]
                  if "error" not in r and r["beta_distinta"] >= minimo_filas]
    salida = []
    sox_hoy = orig(("^SOX",))
    for f in candidatas:
        fecha = date.fromisoformat(f)
        s = sel[sel.fecha == f].set_index("ticker")["beta"]
        if len(s) < minimo_filas:
            continue
        hoy = motor.betas_al(fecha).set_index("Ticker")["beta"].reindex(s.index)
        dist_hoy = float(np.abs(hoy - s).max())
        if dist_hoy <= umbral_beta:
            continue
        idx = sox_hoy.index[sox_hoy.index.date <= fecha][-barras:]
        mejor = None
        for d in idx:
            def parche(tickers, d=d):
                df = orig(tickers)
                return df[df.index != d] if "^SOX" in tickers else df
            with mock.patch.object(motor, "_datos_crudos", parche):
                b = motor.betas_al(fecha).set_index("Ticker")["beta"].reindex(s.index)
            dist = float(np.abs(b - s).max())
            if mejor is None or dist < mejor[0]:
                mejor = (dist, d.date().isoformat(), b.round(2).to_dict())
        salida.append({"fecha": f, "maxdif_con_fuente_de_hoy": round(dist_hoy, 3),
                       "barra_sox_cuyo_retiro_mejor_explica": mejor[1],
                       "maxdif_sin_esa_barra": round(mejor[0], 3),
                       "betas_sin_esa_barra": mejor[2],
                       "betas_selladas": s.round(2).to_dict()})
    return {"umbral_beta": umbral_beta, "fechas_probadas": candidatas, "resultados": salida,
            "nota": ("Hipótesis, no testigo. Si varias fechas señalan la MISMA barra "
                     "y la diferencia residual es de centésimas, la explicación más "
                     "simple es que la fuente sirvió la serie sin esa barra esas "
                     "noches y con ella las noches vecinas: una ausencia "
                     "TRANSITORIA, distinta del retiro del 28-ago.")}


# ------------------------------------------------------------
# Informe
# ------------------------------------------------------------
def _md(res: dict) -> str:
    L = []
    L.append("# Cuánta historia mutó — medición del Frente A (séptima corrida)\n")
    L.append(f"- Generado: {res['generado_en_utc']} · `python GEMELO/fuente_canonica.py`")
    L.append("- `senales.db` en `mode=ro`; cachés NO reescritas; ninguna fila tocada.")
    L.append("- Toda cifra de este archivo sale del `.json` homónimo; nada está cableado en la prosa.\n")
    L.append("## M1 · Las cachés del 26-ago contra la fuente de hoy\n")
    for tst in res["m1"]["testigos"]:
        if not tst.get("existe", True):
            L.append(f"- `{tst['ruta']}`: no existe.")
            continue
        t = tst["totales"]
        L.append(f"### `{tst['ruta']}` — capturada {tst['capturada_en_utc']}, "
                 f"{tst['tickers']} tickers × {tst['fechas']} fechas ({tst['desde']} → {tst['hasta']})\n")
        L.append("| celdas | paridad | distinta | de ellas proporcional | no proporcional | **retornos cambiados** | retirada | aparecida | última fecha parcial/nueva | max abs Δretorno |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        L.append(f"| {t['celdas']} | {t['paridad']} | {t['distinta']} | {t['proporcional']} | "
                 f"{t['no_proporcional']} | **{t['retornos_cambiados']}** | {t['retirada']} | {t['aparecida']} | "
                 f"{t['ultima_fecha_parcial_o_nueva']} | {t['max_abs_dif_retorno']:.2e} |")
        L.append(f"\nFechas con alguna barra retirada: {tst['fechas_con_alguna_retirada'] or 'ninguna'}\n")
        L.append("| ticker | paridad | distinta | proporcional | no prop. | retirada | aparecida | factor |")
        L.append("|---|---|---|---|---|---|---|---|")
        for tk, v in tst["por_ticker"].items():
            if v.get("sin_serie_hoy"):
                L.append(f"| {tk} | — | — | — | — | — | — | sin serie hoy |")
                continue
            fac = "" if v["factor_reescalado"] is None else f"{v['factor_reescalado']:.6f}"
            L.append(f"| {tk} | {v['paridad']} | {v['distinta']} | {v['proporcional']} | "
                     f"{v['no_proporcional']} | {v['retirada']} | {v['aparecida']} | {fac} |")
        L.append("")
    m2 = res["m2"]
    L.append(f"## M2 · `sox_usado_pct` sellado ({m2['n_fechas']} fechas) contra el `^SOX` de hoy\n")
    L.append(f"Conteo: {m2['conteo']}\n")
    L.append("| fecha | sellado | hoy | dif pp | veredicto |")
    L.append("|---|---|---|---|---|")
    for r in m2["filas"]:
        if r["veredicto"] != "PARIDAD":
            L.append(f"| {r['fecha']} | {r['sellado_pct']} ({r['sellado_fecha']}) | "
                     f"{r['hoy_pct']} ({r['hoy_fecha']}) | {r['dif_pp']} | **{r['veredicto']}** |")
    L.append("\n(Sólo se listan las fechas que no son PARIDAD.)\n")
    m3 = res["m3"]
    L.append(f"## M3 · Verificaciones selladas ({m3['n_filas']} filas) contra Open/Close de hoy\n")
    L.append(f"Conteo: {m3['conteo']} · **filas cuyo `acierto_gap` cambiaría: "
             f"{m3['filas_cuyo_acierto_gap_cambia']}**\n")
    L.append("| fecha señal | ticker | sesión obj. | gap sellado | gap hoy | dif | ret sellado | ret hoy | veredicto |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in m3["filas"]:
        if r["veredicto"] != "PARIDAD":
            L.append(f"| {r['fecha_senal']} | {r['ticker']} | {r['sesion_objetivo']} | "
                     f"{r['gap_sellado']} | {r.get('gap_hoy', '—')} | {r.get('dif_gap_pp', '—')} | "
                     f"{r['retorno_sellado']} | {r.get('retorno_hoy', '—')} | **{r['veredicto']}** |")
    L.append("\n(Sólo se listan las filas que no son PARIDAD.)\n")
    m4 = res["m4"]
    L.append(f"## M4 · Emisiones selladas ({m4['n_filas']} filas, {m4['n_fechas']} fechas) contra el motor de hoy\n")
    L.append(f"Conteo: {m4['conteo']} · **filas con el signo dado vuelta: {m4['filas_con_signo_cambiado']}**\n")
    L.append("| fecha | filas | paridad | apertura ≠ | beta ≠ | signo cambia |")
    L.append("|---|---|---|---|---|---|")
    for r in m4["por_fecha"]:
        if "error" in r:
            L.append(f"| {r['fecha']} | — | — | — | — | error: {r['error']} |")
        elif r["paridad"] != r["filas"]:
            L.append(f"| {r['fecha']} | {r['filas']} | {r['paridad']} | {r['apertura_distinta']} | "
                     f"{r['beta_distinta']} | {r['signo_cambia']} |")
    L.append("\n(Sólo se listan las fechas que no reproducen 8/8.)\n")
    m6 = res["m6"]
    L.append(f"## M6 · Hipótesis ejecutable sobre las fechas cuyas betas no reproducen\n")
    L.append(f"> {m6['nota']}\n")
    L.append("| fecha | max |Δbeta| con la fuente de hoy | barra `^SOX` cuyo retiro mejor explica | max |Δbeta| sin esa barra |")
    L.append("|---|---|---|---|")
    for r in m6["resultados"]:
        L.append(f"| {r['fecha']} | {r['maxdif_con_fuente_de_hoy']} | {r['barra_sox_cuyo_retiro_mejor_explica']} | {r['maxdif_sin_esa_barra']} |")
    L.append("")
    m5 = res["m5"]
    L.append(f"## M5 · Censo de sesiones de calendario sin barra hoy (últimos {m5['anios']} años, hasta {m5['hasta']})\n")
    L.append(f"> {m5['nota']}\n")
    L.append("| ticker | exchange | sesiones | sin barra hoy | últimas |")
    L.append("|---|---|---|---|---|")
    for t, v in sorted(m5["por_ticker"].items(), key=lambda kv: -kv[1]["sin_barra_hoy"]):
        L.append(f"| {t} | {v['exchange']} | {v['sesiones_calendario']} | {v['sin_barra_hoy']} | "
                 f"{', '.join(v['ultimas_5'])} |")
    return "\n".join(L) + "\n"


def main() -> dict:
    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat()}
    res["m1"] = m1_caches_vs_hoy()
    sox = _sox_fresco()
    res["m2"] = m2_sox_sellado_vs_hoy(sox)
    res["m3"] = m3_verificaciones_vs_hoy()
    res["m4"] = m4_emisiones_vs_motor_hoy()
    res["m6"] = m6_hipotesis_barra_transitoria(res["m4"])
    panel = gd.descargar_cierres(tuple(UNIVERSO) + ("^SOX",), 3, usar_cache=False)
    res["m5"] = m5_censo_huecos(panel, 3)
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "fuente_canonica.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "fuente_canonica_medicion.md"), "w") as f:
        f.write(_md(res))
    return res


if __name__ == "__main__":
    r = main()
    for k in ("m2", "m3", "m4"):
        print(k, r[k]["conteo"])
    for x in r["m6"]["resultados"]:
        print("m6", x["fecha"], x["maxdif_con_fuente_de_hoy"], "->", x["barra_sox_cuyo_retiro_mejor_explica"], x["maxdif_sin_esa_barra"])
    for t in r["m1"]["testigos"]:
        print("m1", t.get("ruta"), t.get("totales"))
