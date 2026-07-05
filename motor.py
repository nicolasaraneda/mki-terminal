# ============================================================
# Motor de señales (Etapa 4.6) — funciones puras parametrizadas por fecha.
#
# GARANTÍA DE NO-CONTAMINACIÓN: toda función *_al(fecha) usa EXCLUSIVAMENTE
# datos con índice <= fecha (inclusive). La descarga cruda pasa por UN solo
# punto (_datos_crudos), y _hasta() recorta ahí mismo; tests/test_motor.py
# verifica que recortar los datos posteriores a la fecha no cambia ningún
# resultado. El dashboard, snapshot.py y el backtest de la Etapa 5 consumen
# estas mismas funciones: una sola fuente de verdad.
#
# Este módulo NO importa Streamlit.
# ============================================================

import time as _time
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

from universo import (ACCIONES, FX_POR_EXCHANGE, EXCHANGE_POR_TICKER,
                      INDICE_LOCAL_POR_EXCHANGE, MERCADOS_POR_ABRIR,
                      MONEDA_TICKER, NIVELES_CADENA, PARES_COMPETIDORES,
                      PARES_FX, TICKERS_POR_NIVEL, UNIVERSO, nombre)

VENTANA_BETAS_DEFAULT = 120   # días hábiles de historia para las betas de contagio
ANIOS_DATOS = 3               # profundidad de la descarga cruda
_TTL_CACHE_SEG = 900          # la caché en memoria caduca a los 15 minutos

_cache: dict = {}

Z80 = 1.2816  # cuantil 90% de la normal: intervalo central del 80% = ±z80·sigma


def _datos_crudos(tickers: tuple) -> pd.DataFrame:
    """ÚNICO punto de acceso a precios crudos (Close ajustado, ANIOS_DATOS años).

    Los tests de no-contaminación parchean esta función para recortar datos;
    cualquier otra vía de acceso a datos rompería la garantía del módulo."""
    ahora = _time.time()
    entrada = _cache.get(tickers)
    if entrada is not None and ahora - entrada[0] < _TTL_CACHE_SEG:
        return entrada[1].copy()
    data = yf.download(list(tickers), period=f"{ANIOS_DATOS}y", interval="1d",
                       auto_adjust=True, progress=False)
    if data.empty:
        cierres = pd.DataFrame()
    else:
        cierres = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data[["Close"]]
        if isinstance(cierres, pd.Series):
            cierres = cierres.to_frame(name=tickers[0])
    _cache[tickers] = (ahora, cierres)
    return cierres.copy()


def _hasta(df: pd.DataFrame, fecha: date) -> pd.DataFrame:
    """Recorta un DataFrame a filas con fecha <= `fecha`. LA garantía anti
    look-ahead del motor: se aplica inmediatamente después de la descarga."""
    if df.empty:
        return df
    return df[df.index.date <= fecha]


def _precios_hasta(tickers: tuple, fecha: date, en_usd: bool = True) -> pd.DataFrame:
    """Cierres hasta `fecha` (ffill por feriados — Supuesto #1), opcionalmente
    convertidos a USD con los tipos de cambio TAMBIÉN recortados a `fecha`."""
    precios = _hasta(_datos_crudos(tuple(tickers)), fecha).ffill().dropna(axis=1, how="all")
    if not en_usd or precios.empty:
        return precios
    fx = _hasta(_datos_crudos(PARES_FX), fecha).ffill()
    resultado = precios.copy()
    for t in resultado.columns:
        par = MONEDA_TICKER.get(t)
        if par is None or par not in fx.columns:
            continue
        tasa = fx[par].reindex(resultado.index).ffill().bfill()
        resultado[t] = resultado[t] / tasa
    return resultado


def _ultimo_mov_no_cero(retornos: pd.Series, umbral: float = 1e-6):
    """Último retorno realmente distinto de cero (el ffill de feriados produce
    ceros que no son movimientos de mercado). Devuelve (pct, fecha) o (None, None)."""
    retornos = retornos.dropna()
    no_cero = retornos[retornos.abs() >= umbral]
    if no_cero.empty:
        return None, None
    return float(no_cero.iloc[-1] * 100), no_cero.index[-1].date()


# ------------------------------------------------------------
# Señales
# ------------------------------------------------------------
def regimen_al(fecha: date) -> dict | None:
    """Régimen de mercado del SOX AL CIERRE de `fecha`: tendencia (MA50 vs
    MA200, banda lateral ±1%) × volatilidad (realizada 20d vs mediana 1 año).

    Garantía: usa exclusivamente datos hasta `fecha` inclusive."""
    sox = _hasta(_datos_crudos(("^SOX",)), fecha)
    if sox.empty or len(sox) < 220:
        return None
    serie = sox.iloc[:, 0].dropna()
    if len(serie) < 220:
        return None
    ma50 = serie.rolling(50).mean().iloc[-1]
    ma200 = serie.rolling(200).mean().iloc[-1]
    ratio = ma50 / ma200 - 1
    tendencia = "Alcista" if ratio > 0.01 else ("Bajista" if ratio < -0.01 else "Lateral")
    vol20 = serie.pct_change().rolling(20).std() * (252 ** 0.5) * 100
    vol_actual = float(vol20.iloc[-1])
    vol_mediana = float(vol20.tail(252).median())
    vol_label = "alta" if vol_actual > vol_mediana else "baja"
    return {
        "tendencia": tendencia, "vol": vol_label,
        "etiqueta": f"{tendencia} · vol {vol_label}",
        "ratio_ma_pct": round(ratio * 100, 2),
        "vol_actual": round(vol_actual, 1), "vol_mediana": round(vol_mediana, 1),
    }


def puntaje_v0_al(fecha: date, ventana_dias: int = 126) -> pd.DataFrame:
    """Métricas y Puntaje v0 de todas las acciones del universo AL CIERRE de
    `fecha`, sobre una ventana de ~6 meses (126 sesiones). Siempre en USD.

    Garantía: usa exclusivamente datos hasta `fecha` inclusive."""
    precios = _precios_hasta(ACCIONES, fecha)
    if precios.empty:
        return pd.DataFrame()
    precios = precios.tail(ventana_dias)
    retornos = precios.pct_change().dropna(how="all")
    filas = []
    for t in precios.columns:
        serie = precios[t].dropna()
        if len(serie) < 20:
            continue
        info = UNIVERSO.get(t, {})
        filas.append({
            "Ticker": t,
            "Empresa": info.get("nombre", t),
            "Segmento": info.get("segmento", ""),
            "Retorno período %": round((serie.iloc[-1] / serie.iloc[0] - 1) * 100, 1),
            "Volatilidad anual %": round(retornos[t].std() * (252 ** 0.5) * 100, 1),
            "Dist. del máximo %": round((serie.iloc[-1] / serie.max() - 1) * 100, 1),
            "Momentum 20d %": round((serie.iloc[-1] / serie.iloc[-min(21, len(serie))] - 1) * 100, 1),
        })
    df = pd.DataFrame(filas)
    if df.empty:
        return df
    df["Puntaje v0"] = (df["Momentum 20d %"].rank(pct=True) * 0.4
                        + df["Retorno período %"].rank(pct=True) * 0.4
                        + (1 - df["Volatilidad anual %"].rank(pct=True)) * 0.2).round(2)
    return df.sort_values("Puntaje v0", ascending=False).reset_index(drop=True)


def datos_cadena_al(fecha: date) -> dict:
    """Agregados de la cadena AL CIERRE de `fecha` (siempre USD): momentum 20d
    y retornos diarios por eslabón, y los precios subyacentes para gráficos.
    El ADR TSM está excluido de los eslabones (duplicado de 2330.TW).

    Garantía: usa exclusivamente datos hasta `fecha` inclusive."""
    precios = _precios_hasta(tuple(UNIVERSO.keys()), fecha)
    if precios.empty:
        return {"series_nivel": {}, "ret_nivel": {}, "precios": precios,
                "mom20": pd.DataFrame()}
    precios = precios.tail(300)  # ~14 meses: suficiente para percentil de 1 año
    ret = precios.pct_change()
    mom20 = precios / precios.shift(20) - 1
    series_nivel, ret_nivel = {}, {}
    for nivel in NIVELES_CADENA:
        cols = [t for t in TICKERS_POR_NIVEL[nivel] if t in precios.columns]
        if cols:
            series_nivel[nivel] = mom20[cols].mean(axis=1)
            ret_nivel[nivel] = ret[cols].mean(axis=1)
    return {"series_nivel": series_nivel, "ret_nivel": ret_nivel,
            "precios": precios, "mom20": mom20}


def roca_chip_al(fecha: date) -> dict | None:
    """Índice Roca→Chip AL CIERRE de `fecha`: momentum 20d promedio de los
    eslabones (peso igual), como percentil dentro de su último año (0-100).

    Garantía: usa exclusivamente datos hasta `fecha` inclusive."""
    cadena = datos_cadena_al(fecha)
    if len(cadena["series_nivel"]) < 3:
        return None
    serie = pd.concat(cadena["series_nivel"].values(), axis=1).mean(axis=1).dropna() * 100
    if len(serie) <= 60:
        return None
    percentil = float((serie.tail(252) <= serie.iloc[-1]).mean() * 100)
    return {
        "valor": round(percentil),
        "crudo_pct": round(float(serie.iloc[-1]), 2),
        "historia": list(serie.tail(30)),
        "serie": serie,
    }


def _residualizar(ret_accion: pd.Series, fecha: date) -> pd.Series:
    """Residuos de regresar los retornos diarios (USD) de una acción contra su
    índice local y su tipo de cambio: lo que queda es el movimiento propio de
    la empresa, sin el arrastre de su bolsa ni de su moneda."""
    exchange = EXCHANGE_POR_TICKER.get(ret_accion.name, "XNYS")
    regresores = []
    idx_local = INDICE_LOCAL_POR_EXCHANGE.get(exchange)
    if idx_local:
        serie_idx = _hasta(_datos_crudos((idx_local,)), fecha)
        if not serie_idx.empty:
            regresores.append(serie_idx.iloc[:, 0].pct_change().rename("idx"))
    par_fx = FX_POR_EXCHANGE.get(exchange)
    if par_fx:
        fx = _hasta(_datos_crudos(PARES_FX), fecha)
        if par_fx in fx.columns:
            regresores.append(fx[par_fx].pct_change().rename("fx"))
    if not regresores:
        return ret_accion - ret_accion.mean()
    df = pd.concat([ret_accion.rename("y")] + regresores, axis=1).dropna()
    if len(df) < 60:
        return ret_accion - ret_accion.mean()
    X = df.drop(columns=["y"])
    X = X.assign(const=1.0)
    # Mínimos cuadrados ordinarios sin dependencia extra
    import numpy as np
    beta, *_ = np.linalg.lstsq(X.values, df["y"].values, rcond=None)
    residuos = df["y"].values - X.values @ beta
    return pd.Series(residuos, index=df.index, name=ret_accion.name)


def divergencias_al(fecha: date, residualizar: bool = True) -> list:
    """Divergencias entre competidores directos AL CIERRE de `fecha`.

    El spread se calcula sobre momentum 20d de retornos RESIDUALIZADOS
    (limpiados del índice local y el tipo de cambio de cada acción) — así una
    brecha entre SK Hynix y Micron no puede ser solo 'el KOSPI subió'. Se
    guarda también el spread simple (sin residualizar) para comparación.
    |z| > 2 del spread residualizado = divergencia activa.

    Garantía: usa exclusivamente datos hasta `fecha` inclusive."""
    precios = _precios_hasta(tuple(UNIVERSO.keys()), fecha)
    if precios.empty:
        return []
    ret = precios.pct_change()
    mom20_simple = precios / precios.shift(20) - 1

    resultado = []
    for grupo, tickers_grupo in PARES_COMPETIDORES:
        presentes = [t for t in tickers_grupo if t in precios.columns]
        for i in range(len(presentes)):
            for j in range(i + 1, len(presentes)):
                a, b = presentes[i], presentes[j]
                spread_simple = (mom20_simple[a] - mom20_simple[b]).dropna() * 100
                if len(spread_simple) < 120 or spread_simple.std() == 0:
                    continue
                z_simple = float((spread_simple.iloc[-1] - spread_simple.mean())
                                 / spread_simple.std())
                if residualizar:
                    res_a = _residualizar(ret[a], fecha)
                    res_b = _residualizar(ret[b], fecha)
                    mom_res = (res_a.rolling(20).sum() - res_b.rolling(20).sum()).dropna() * 100
                    if len(mom_res) < 120 or mom_res.std() == 0:
                        continue
                    spread_val = float(mom_res.iloc[-1])
                    z = float((mom_res.iloc[-1] - mom_res.mean()) / mom_res.std())
                else:
                    spread_val, z = float(spread_simple.iloc[-1]), z_simple
                delante, detras = (a, b) if spread_val > 0 else (b, a)
                resultado.append({
                    "par": f"{nombre(a)} vs {nombre(b)}",
                    "grupo": grupo,
                    "spread": round(spread_val, 2),
                    "z": round(z, 2),
                    "spread_simple": round(float(spread_simple.iloc[-1]), 2),
                    "z_simple": round(z_simple, 2),
                    "activa": abs(z) > 2,
                    "explicacion": (
                        f"{nombre(delante)} le saca {abs(spread_val):.1f} pp de "
                        f"rendimiento propio 20d a {nombre(detras)} (limpiado de "
                        f"índice local y moneda) — inusual vs su historia "
                        f"(z={z:+.1f})."),
                })
    return resultado


def betas_al(fecha: date, ventana: int = VENTANA_BETAS_DEFAULT) -> pd.DataFrame:
    """Betas de contagio SOX(t-1) → acción(t) AL CIERRE de `fecha`, con ventana
    rodante de `ventana` días hábiles. Devuelve por ticker: beta, r2, n_muestra
    y la desviación estándar de los residuos (para intervalos de predicción).

    Garantía: usa exclusivamente datos hasta `fecha` inclusive."""
    precios = _precios_hasta(tuple(MERCADOS_POR_ABRIR), fecha)
    sox = _hasta(_datos_crudos(("^SOX",)), fecha)
    if precios.empty or sox.empty:
        return pd.DataFrame()
    ret_acc = precios.pct_change()
    ret_sox = sox.iloc[:, 0].pct_change()
    filas = []
    for t in MERCADOS_POR_ABRIR:
        if t not in ret_acc.columns:
            continue
        par = pd.concat([ret_acc[t], ret_sox.shift(1)], axis=1).dropna().tail(ventana)
        if len(par) < 40:
            continue
        y, x = par.iloc[:, 0], par.iloc[:, 1]
        var_x = x.var()
        if var_x <= 0:
            continue
        beta = float(x.cov(y) / var_x)
        alfa = float(y.mean() - beta * x.mean())
        residuos = y - (alfa + beta * x)
        r2 = float(x.corr(y) ** 2)
        filas.append({
            "Ticker": t, "beta": beta, "r2": r2, "n_muestra": int(len(par)),
            "resid_std_pct": float(residuos.std() * 100),
        })
    return pd.DataFrame(filas)


def prediccion_apertura_al(fecha: date, ventana: int = VENTANA_BETAS_DEFAULT,
                           dias_earnings: dict | None = None) -> pd.DataFrame:
    """Predicción del anticipador AL CIERRE de `fecha`: aplica las betas de
    contagio al último movimiento real del SOX conocido hasta `fecha`.
    Incluye el intervalo central del 80% (±1.2816 × sigma de los residuos de
    la regresión). `dias_earnings` (opcional, {ticker: días}) degrada la
    confianza un nivel dentro de la zona de earnings (<5 días).

    Garantía: usa exclusivamente datos de precios hasta `fecha` inclusive
    (dias_earnings viene de un calendario corporativo, no de precios)."""
    betas = betas_al(fecha, ventana)
    if betas.empty:
        return pd.DataFrame()
    sox = _hasta(_datos_crudos(("^SOX",)), fecha)
    if sox.empty:
        return pd.DataFrame()
    ult_mov, ult_fecha = _ultimo_mov_no_cero(sox.iloc[:, 0].pct_change())
    if ult_mov is None:
        return pd.DataFrame()
    dias_earnings = dias_earnings or {}
    filas = []
    for _, b in betas.iterrows():
        t = b["Ticker"]
        est = b["beta"] * ult_mov
        int80 = Z80 * b["resid_std_pct"]
        confianza = "Alta" if b["r2"] > 0.25 else ("Media" if b["r2"] > 0.10 else "Baja")
        dias_e = dias_earnings.get(t)
        zona_earnings = dias_e is not None and dias_e < 5
        if zona_earnings:
            confianza = {"Alta": "Media", "Media": "Baja", "Baja": "Baja"}[confianza]
        filas.append({
            "Ticker": t,
            "Apertura estimada %": round(float(est), 2),
            "Intervalo80 pp": round(float(int80), 2),
            "Beta de contagio": round(float(b["beta"]), 2),
            "R2": round(float(b["r2"]), 4),
            "N muestra": int(b["n_muestra"]),
            "Confianza": confianza,
            "Zona earnings": bool(zona_earnings),
            "Dias earnings": dias_e if zona_earnings else None,
            "SOX usado %": round(ult_mov, 2),
            "SOX fecha": ult_fecha.isoformat() if ult_fecha else None,
        })
    df = pd.DataFrame(filas)
    return df.sort_values("Apertura estimada %", ascending=False).reset_index(drop=True)


def salud_datos_al(fecha: date, umbral_salto: float = 0.40) -> dict:
    """Chequeos de integridad de datos AL CIERRE de `fecha`:
    (a) saltos diarios anómalos (>umbral, posible split mal ajustado o dato
    corrupto — con auto_adjust=True un salto así es sospechoso), (b) cobertura
    del mapeo de monedas para sufijos no-USD, (c) confirmación de auto_adjust.

    Garantía: usa exclusivamente datos hasta `fecha` inclusive."""
    problemas = []
    precios = _precios_hasta(tuple(UNIVERSO.keys()), fecha, en_usd=False)
    if not precios.empty:
        ret = precios.pct_change().tail(252)
        for t in ret.columns:
            saltos = ret[t].dropna()
            extremos = saltos[saltos.abs() > umbral_salto]
            for fecha_salto, valor in extremos.items():
                problemas.append(
                    f"{nombre(t)} ({t}): salto de {valor * 100:+.0f}% el "
                    f"{fecha_salto.date()} — revisar split/dato corrupto")
    sufijos_no_usd = {".KS": "KRW=X", ".TW": "TWD=X", ".T": "JPY=X", ".DE": "EUR=X"}
    for t in UNIVERSO:
        for suf, par in sufijos_no_usd.items():
            if t.endswith(suf) and MONEDA_TICKER.get(t) != par:
                problemas.append(f"{t}: sufijo {suf} sin par de moneda {par} en MONEDA_TICKER")
    return {
        "fecha": fecha.isoformat(),
        "tickers_revisados": len(precios.columns) if not precios.empty else 0,
        "auto_adjust": True,  # constante en todas las descargas del sistema
        "problemas": problemas,
        "ok": len(problemas) == 0,
    }
