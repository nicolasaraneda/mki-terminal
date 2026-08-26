# ============================================================
# GEMELO/features.py — construcción CAUSAL y ESTACIONARIA (6.0.0 WS2a).
#
# Catálogo especificado en GEMELO/DISEÑO.md §4.1. Este módulo NO modela:
# solo construye la matriz de features. El control lineal es WS2b.
#
# DOS REGLAS, y las dos se testean:
#
# 1. CAUSAL. El valor en t usa solo información conocible en t. Todas las
#    transformaciones son RETROSPECTIVAS (pct_change, shift, rolling hacia
#    atrás): nunca un center=True, nunca un shift negativo. La prueba no es
#    la inspección sino la propiedad: `construir(series)` truncado a <= t
#    debe dar en t exactamente lo mismo que sin truncar.
#
# 2. ESTACIONARIA POR CONSTRUCCIÓN. Retornos, razones y distancias; NUNCA
#    niveles crudos. Un nivel deriva monótonamente y el modelo termina
#    usándolo como proxy del calendario — aprende "más adelante en el
#    tiempo" en vez de "más riesgo", y eso no generaliza a mañana.
#
# La asincronía de las barras (GEMELO/datos.py) es responsabilidad de
# `datos.verificar_conocibles`, que se invoca desde aquí: ninguna feature
# puede nacer de dos barras cuyo available_at sea posterior a la emisión.
# ============================================================

import numpy as np
import pandas as pd

from GEMELO import datos

VENTANA_VOL = 20          # sesiones de la volatilidad realizada
VENTANA_MEDIANA_VOL = 252  # ~1 año, para normalizar el régimen de vol

# Qué series alimenta cada feature. Es un DATO y no un comentario, porque
# el test de asincronía lo recorre: si una feature usara una serie no
# conocible a la emisión, el test la nombra.
DEPENDENCIAS = {
    "sox_t":         ("^SOX",),
    "sox_t1":        ("^SOX",),
    "es_ret":        ("ES=F",),
    "nq_ret":        ("NQ=F",),
    "krw_ret":       ("KRW=X",),
    "twd_ret":       ("TWD=X",),
    "jpy_ret":       ("JPY=X",),
    "eurusd_ret":    ("EURUSD=X",),
    "ks11_ret":      ("^KS11",),
    "twii_ret":      ("^TWII",),
    "n225_ret":      ("^N225",),
    "gdaxi_ret":     ("^GDAXI",),
    "vix_term":      ("^VIX3M", "^VIX"),
    "vix_dln":       ("^VIX",),
    "credit_ratio":  ("HYG", "LQD"),
    "vol_regime":    ("^SOX",),
}

FEATURES = tuple(DEPENDENCIAS)


def _ret(serie: pd.Series) -> pd.Series:
    """Retorno simple en %, retrospectivo por construcción."""
    return serie.pct_change() * 100


def _col(series: pd.DataFrame, ticker: str) -> pd.Series | None:
    if ticker not in series.columns:
        return None
    s = pd.to_numeric(series[ticker], errors="coerce")
    return s if s.notna().any() else None


def construir(series: pd.DataFrame, verificar: bool = True) -> pd.DataFrame:
    """Matriz de features a partir de los cierres crudos.

    Función PURA: mismas series de entrada → misma salida. No descarga, no
    cachea, no escribe. Es lo que permite al test de causalidad truncar la
    entrada y comparar, sin parchear nada.

    Una serie ausente produce su columna ausente, no un error: la
    investigación tiene que poder correr con lo que Yahoo entregó hoy. Las
    que faltan quedan declaradas en el atributo `.attrs["ausentes"]`.
    """
    if series is None or series.empty:
        return pd.DataFrame()

    if verificar:
        # Guarda dura de la asincronía sobre el último día disponible.
        ultimo = pd.Timestamp(series.index.max()).date()
        datos.verificar_conocibles(tuple(series.columns), ultimo)

    f = {}

    # --- Contagio: el SOX del día y el del día anterior, EXPLÍCITOS ---
    # El README documenta 0.24 con el SOX del día y 0.38 con el del día
    # anterior. La estructura de rezago va explícita, no escondida dentro
    # de una ventana rodante que la promedie.
    sox = _col(series, "^SOX")
    if sox is not None:
        r = _ret(sox)
        f["sox_t"] = r
        f["sox_t1"] = r.shift(1)
        # Régimen de volatilidad: RAZÓN entre la vol realizada reciente y su
        # propia mediana de un año. Es una distancia relativa, no un nivel:
        # un 1.8 significa lo mismo en 2019 que en 2026.
        vol = r.rolling(VENTANA_VOL).std()
        mediana = vol.rolling(VENTANA_MEDIANA_VOL).median()
        f["vol_regime"] = vol / mediana.replace(0.0, np.nan)

    # --- Overnight US: lo que se mueve entre el cierre del SOX y la
    #     apertura asiática, que es justo lo que hoy se tira ---
    for ticker, nombre in (("ES=F", "es_ret"), ("NQ=F", "nq_ret")):
        s = _col(series, ticker)
        if s is not None:
            f[nombre] = _ret(s)

    # --- Divisas: el retorno en moneda local depende del tipo de cambio ---
    for ticker, nombre in (("KRW=X", "krw_ret"), ("TWD=X", "twd_ret"),
                           ("JPY=X", "jpy_ret"), ("EURUSD=X", "eurusd_ret")):
        s = _col(series, ticker)
        if s is not None:
            f[nombre] = _ret(s)

    # --- Mercado local: separa "gapea el mercado" de "gapean los semis" ---
    for ticker, nombre in (("^KS11", "ks11_ret"), ("^TWII", "twii_ret"),
                           ("^N225", "n225_ret"), ("^GDAXI", "gdaxi_ret")):
        s = _col(series, ticker)
        if s is not None:
            f[nombre] = _ret(s)

    # --- Volatilidad: la estructura temporal es genuinamente prospectiva ---
    vix, vix3m = _col(series, "^VIX"), _col(series, "^VIX3M")
    if vix is not None and vix3m is not None:
        f["vix_term"] = vix3m / vix.replace(0.0, np.nan)
    if vix is not None:
        # Δln en vez del nivel: el nivel del VIX deriva por régimen.
        f["vix_dln"] = np.log(vix.replace(0.0, np.nan)).diff()

    # --- Crédito: apetito por riesgo ---
    hyg, lqd = _col(series, "HYG"), _col(series, "LQD")
    if hyg is not None and lqd is not None:
        # RAZÓN de dos precios, según §4.1. Advertencia honesta: una razón
        # de niveles puede derivar, así que es la MENOS estacionaria del
        # catálogo. Se implementa como está especificada y queda anotada
        # en DECISIONES.md §29 como candidata a pasar a forma de distancia
        # si el control lineal de WS2b la muestra derivando.
        f["credit_ratio"] = np.log(
            hyg.replace(0.0, np.nan) / lqd.replace(0.0, np.nan))

    out = pd.DataFrame(f, index=series.index)
    out = out.reindex(columns=[c for c in FEATURES if c in out.columns])
    out.attrs["ausentes"] = [c for c in FEATURES if c not in out.columns]
    return out


def construir_desde_yahoo(**kwargs) -> tuple:
    """Conveniencia para la investigación: descarga y construye. Devuelve
    (features, descartadas_por_cobertura)."""
    series, descartadas = datos.series_para_investigacion(**kwargs)
    return construir(series), descartadas


def resumen(features: pd.DataFrame) -> pd.DataFrame:
    """Cobertura y momentos de cada feature — para mirar antes de modelar."""
    if features.empty:
        return pd.DataFrame()
    return pd.DataFrame([{
        "feature": c,
        "n": int(features[c].notna().sum()),
        "cobertura": round(float(features[c].notna().mean()), 3),
        "media": round(float(features[c].mean()), 4),
        "desv": round(float(features[c].std()), 4),
        "min": round(float(features[c].min()), 4),
        "max": round(float(features[c].max()), 4),
    } for c in features.columns])
