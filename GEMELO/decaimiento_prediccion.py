"""Frente B2 de la octava corrida: la curva de decaimiento como predicción
fuera de muestra, para exchanges que el proyecto nunca miró.

Pre-registro: `GEMELO/preregistro/frente_B.md` §B2. Dos fases, separadas a
propósito:

  --ajustar   Ajusta Δ(h) = a·exp(−h/τ) (mínimos cuadrados ponderados por
              fechas) y el control isotónico sobre los CUATRO exchanges
              actuales en los años de AJUSTE (gaps v2 + SOX testigo, sin
              motor), con IC de (a, τ) por bootstrap de fechas, y escribe
              las PREDICCIONES con intervalo para los exchanges nuevos en
              `GEMELO/resultados/decaimiento_prediccion.json` (sección
              «predicciones_escritas_antes»). No descarga nada.
  --medir     Recién después: descarga los tickers nuevos (yfinance,
              directo, sin caché de GEMELO), calcula sus gaps con
              `GEMELO.datos.gaps_desde_ohlc`, anota qué sesiones faltan, y
              mide Δ por exchange con clúster de fecha en los mismos años.
              Compara contra la predicción escrita.

Uso: `python GEMELO/decaimiento_prediccion.py --ajustar` y luego `--medir`.
"""
from __future__ import annotations

import gzip
import json
import math
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(_AQUI)
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from GEMELO import decaimiento_feriados as dfz              # noqa: E402

DIR_RESULTADOS = os.path.join(_AQUI, "resultados")
RUTA_JSON = os.path.join(DIR_RESULTADOS, "decaimiento_prediccion.json")
RUTA_TESTIGO_B2 = os.path.join(DIR_RESULTADOS, "testigos_fuente", "b2_nuevos_ohlc.csv.gz")   # dictamen B, B-6
SEMILLA = 20260902
N_BOOT = 4000
H_ACTUALES = {"XTKS": 1.75, "XKRX": 1.75, "XTAI": 2.75, "XETR": 8.75}
# exchanges nuevos: apertura UTC − 22:15Z; tickers candidatos de semiconductores
NUEVOS = {
    "XHKG": {"h": 3.25, "tickers": ["0981.HK", "1347.HK"]},
    "XAMS": {"h": 8.75, "tickers": ["ASML.AS", "BESI.AS"]},
    "XNSE": {"h": 5.5, "tickers": ["MOSCHIP.NS", "TATAELXSI.NS"]},
    "XASX": {"h": 1.75, "tickers": []},
}
AJUSTE = dfz.AJUSTE
PRUEBA = dfz.PRUEBA


def _delta_por_exchange(df: pd.DataFrame, desde: str, hasta: str) -> dict:
    sub = df[(df["fecha"] >= desde) & (df["fecha"] <= hasta)]
    out = {}
    for e, g in sub.groupby("exchange"):
        m = dfz._por_fecha(g, "sox_prev")
        out[e] = {"M": m, "delta": dfz._ventaja(m), "fechas": len(m)}
    return out


def _ajuste_exp(h: np.ndarray, d: np.ndarray, w: np.ndarray) -> tuple:
    """Δ(h) = a·exp(−h/τ) por mínimos cuadrados ponderados en escala lineal
    (grilla en τ, a cerrado). Devuelve (a, τ)."""
    mejor = None
    for tau in np.linspace(0.5, 40, 800):
        x = np.exp(-h / tau)
        a = float((w * x * d).sum() / (w * x * x).sum())
        err = float((w * (d - a * x) ** 2).sum())
        if mejor is None or err < mejor[0]:
            mejor = (err, a, tau)
    return mejor[1], mejor[2]


def _isotonica(h: np.ndarray, d: np.ndarray, w: np.ndarray, h_nuevo: float) -> float:
    """Control no paramétrico: regresión isotónica DECRECIENTE en h (pool
    adjacent violators con pesos), evaluada en h_nuevo por interpolación
    lineal; fuera del rango, el extremo más cercano."""
    orden = np.argsort(h)
    hs, ds, ws = h[orden], d[orden], w[orden]
    # PAV decreciente: bloques
    bloques = [[float(ds[i]), float(ws[i]), float(hs[i]), float(hs[i])] for i in range(len(ds))]
    i = 0
    while i < len(bloques) - 1:
        if bloques[i][0] < bloques[i + 1][0]:      # violación (debe ser decreciente)
            v, wv = bloques[i], bloques[i + 1]
            m = (v[0] * v[1] + wv[0] * wv[1]) / (v[1] + wv[1])
            bloques[i:i + 2] = [[m, v[1] + wv[1], v[2], wv[3]]]
            i = max(i - 1, 0)
        else:
            i += 1
    xs = [(b[2] + b[3]) / 2 for b in bloques]; ys = [b[0] for b in bloques]
    if h_nuevo <= xs[0]:
        return ys[0]
    if h_nuevo >= xs[-1]:
        return ys[-1]
    return float(np.interp(h_nuevo, xs, ys))


def ajustar() -> dict:
    df = dfz.cargar()
    por = _delta_por_exchange(df, *AJUSTE)
    ex = sorted(por)
    h = np.array([H_ACTUALES[e] for e in ex]); d = np.array([por[e]["delta"] for e in ex])
    w = np.array([por[e]["fechas"] for e in ex], float)
    a, tau = _ajuste_exp(h, d, w)
    rng = np.random.default_rng(SEMILLA)
    preds = {e: [] for e in NUEVOS}; params = []
    for _ in range(N_BOOT):
        db = []
        for e in ex:
            M = por[e]["M"]; idx = rng.integers(0, len(M), size=len(M))
            db.append(dfz._ventaja(M[idx]))
        db = np.array(db)
        ab, tb = _ajuste_exp(h, db, w)
        params.append((ab, tb))
        for e, spec in NUEVOS.items():
            preds[e].append((ab * math.exp(-spec["h"] / tb), _isotonica(h, db, w, spec["h"])))
    params = np.array(params)
    # anclas con intervalo, tasa base, exposición al SOX y dispersión entre tickers (dictamen B: B-2, E-5, E-6)
    sub = df[(df["fecha"] >= AJUSTE[0]) & (df["fecha"] <= AJUSTE[1])]
    sub = sub[sub["gap_pct"] != 0]
    anclas = {}
    for e in ex:
        M = por[e]["M"]; rb = np.random.default_rng(SEMILLA + 3)
        idx = rb.integers(0, len(M), size=(N_BOOT, len(M))); S = M[idx].sum(axis=1)
        reps = (S[:, 1] - S[:, 2]) / S[:, 0]; lo, hi = np.quantile(reps, [0.025, 0.975])
        g = sub[sub["exchange"] == e]
        por_ticker = {t: round(100 * dfz.ventaja(gt), 2) for t, gt in g.groupby("ticker")}
        anclas[e] = {"h": H_ACTUALES[e], "delta_pp": round(100 * por[e]["delta"], 2), "ic95_pp": [round(100 * float(lo), 2), round(100 * float(hi), 2)],
                     "contiene_cero": bool(lo <= 0 <= hi), "fechas": por[e]["fechas"],
                     "tasa_base_gap_positivo": round(float((g["gap_pct"] > 0).mean()), 3),
                     "corr_gap_sox": round(float(np.corrcoef(g["gap_pct"], g["sox_prev"])[0, 1]), 3),
                     "tickers": sorted(g["ticker"].unique().tolist()), "delta_por_ticker_pp": por_ticker}
    todos = [v for a_ in anclas.values() for v in a_["delta_por_ticker_pp"].values()]
    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "etiqueta": "PROPUESTA — Frente B2; predicciones escritas ANTES de descargar",
           "ajuste": {"anios": AJUSTE, "puntos": anclas,
                      "dispersion_entre_tickers_pp": {"de": round(float(np.std(todos, ddof=1)), 2), "min": min(todos), "max": max(todos), "n": len(todos)},
                      "advertencia_intervalo": ("el IC de la predicción propaga SÓLO el error de muestreo de las anclas: es un intervalo de CONFIANZA "
                                                "de la curva, no de PREDICCIÓN de un exchange nuevo; la dispersión entre conjuntos de tickers al mismo h "
                                                "(Seúl vs Tokio a 1,75 h) y entre tickers (DE arriba) no está incluida y es mayor que el semiancho publicado"),
           "confusion_h_tickers": "h y el conjunto de tickers están perfectamente confundidos en el ajuste (XETR = 1 ticker, XTAI = 1, XKRX = 2, XTKS = 4)",
                      "a_pp": round(100 * a, 2), "tau_h": round(tau, 2),
                      "ic95_a_pp": [round(100 * x, 2) for x in np.quantile(params[:, 0], [0.025, 0.975])],
                      "ic95_tau_h": [round(x, 2) for x in np.quantile(params[:, 1], [0.025, 0.975])],
                      "forma": "Δ(h) = a·exp(−h/τ), MCP ponderados por fechas; control isotónico decreciente",
                      "advertencia": "cuatro exchanges, tres valores de h: la curva tiene un grado de libertad efectivo; "
                                     "la predicción a h=8,75 (Ámsterdam) es la que separa exchange de margen"},
           "predicciones_escritas_antes": {}}
    for e, spec in NUEVOS.items():
        P = np.array(preds[e])
        res["predicciones_escritas_antes"][e] = {
            "h": spec["h"], "tickers_candidatos": spec["tickers"],
            "exp_pp": round(100 * a * math.exp(-spec["h"] / tau), 2),
            "exp_ic95_pp": [round(100 * x, 2) for x in np.quantile(P[:, 0], [0.025, 0.975])],
            "isotonica_pp": round(100 * _isotonica(h, d, w, spec["h"]), 2),
            "isotonica_ic95_pp": [round(100 * x, 2) for x in np.quantile(P[:, 1], [0.025, 0.975])]}
    with open(RUTA_JSON, "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    return res


def _descargar_testigo() -> pd.DataFrame:
    """Descarga UNA vez los OHLC de los tickers nuevos y los preserva como
    testigo (sha256 en el JSON). Después, `--medir` lee del testigo: las
    cifras de B2 son reproducibles (dictamen B, B-6: una re-descarga a 2 h
    de distancia movía los Δ hasta 0,6 pp)."""
    import yfinance as yf
    tick = [t for spec in NUEVOS.values() for t in spec["tickers"]]
    data = yf.download(tick, period="8y", interval="1d", auto_adjust=True, progress=False, group_by="column")
    filas = []
    for t in tick:
        try:
            ap = data["Open"][t]; ci = data["Close"][t]
        except KeyError:
            continue
        filas.append(pd.DataFrame({"fecha": ap.index, "ticker": t, "open": ap.to_numpy(), "close": ci.to_numpy()}))
    out = pd.concat(filas)
    os.makedirs(os.path.dirname(RUTA_TESTIGO_B2), exist_ok=True)
    with gzip.open(RUTA_TESTIGO_B2, "wt") as f:
        out.to_csv(f, index=False)
    return out


def _ohlc_testigo(t: str, testigo: pd.DataFrame):
    g = testigo[testigo["ticker"] == t].dropna(subset=["open", "close"])
    if g.empty:
        return None, None
    idx = pd.to_datetime(g["fecha"])
    return pd.Series(g["open"].to_numpy(), index=idx), pd.Series(g["close"].to_numpy(), index=idx)


def medir(redescargar: bool = False) -> dict:
    import hashlib
    from GEMELO.datos import gaps_desde_ohlc
    with open(RUTA_JSON) as f:
        res = json.load(f)
    assert "predicciones_escritas_antes" in res, "primero --ajustar"
    if redescargar or not os.path.exists(RUTA_TESTIGO_B2):
        _descargar_testigo()
    with gzip.open(RUTA_TESTIGO_B2, "rt") as f:
        testigo = pd.read_csv(f)
    with open(RUTA_TESTIGO_B2, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    with gzip.open(dfz.RUTA_SOX_GZ, "rt") as f:
        sox = pd.read_csv(f, index_col=0, parse_dates=True)["^SOX"].dropna()
    ret = (sox.pct_change().dropna() * 100)
    r = pd.DataFrame({"fecha_sox": ret.index, "sox_prev": ret.to_numpy()}).sort_values("fecha_sox")
    res["medicion"] = {"medido_en_utc": datetime.now(timezone.utc).isoformat(), "testigo": os.path.relpath(RUTA_TESTIGO_B2, _RAIZ),
                       "testigo_sha256": sha, "por_exchange": {}}
    for e, spec in NUEVOS.items():
        if not spec["tickers"]:
            res["medicion"]["por_exchange"][e] = {"nota": "sin ticker de semiconductores disponible: no se mide"}
            continue
        filas, faltantes = [], {}
        for t in spec["tickers"]:
            ap, ci = _ohlc_testigo(t, testigo)
            if ap is None:
                faltantes[t] = "sin datos"; continue
            g = gaps_desde_ohlc(ap, ci)
            if len(g) < 250:
                faltantes[t] = f"historia insuficiente ({len(g)} sesiones)"; continue
            filas.append(pd.DataFrame({"fecha": g.index, "ticker": t, "gap_pct": g.to_numpy()}))
        if not filas:
            res["medicion"]["por_exchange"][e] = {"nota": "ningún ticker con historia", "faltantes": faltantes}
            continue
        df = pd.concat(filas).sort_values("fecha")
        df["fecha"] = pd.to_datetime(df["fecha"]).astype("datetime64[ns]")
        r["fecha_sox"] = pd.to_datetime(r["fecha_sox"]).astype("datetime64[ns]")
        m = pd.merge_asof(df, r, left_on="fecha", right_on="fecha_sox", direction="backward",
                          allow_exact_matches=False).dropna(subset=["sox_prev"])
        out = {"faltantes": faltantes, "tickers_usados": sorted(df["ticker"].unique()),
               "primera_sesion": str(df["fecha"].min().date()), "ultima_sesion": str(df["fecha"].max().date())}
        for nombre, (d0, d1) in (("ajuste", AJUSTE), ("prueba", PRUEBA)):
            sub = m[(m["fecha"] >= d0) & (m["fecha"] <= d1)]
            M = dfz._por_fecha(sub, "sox_prev")
            if len(M) < 30:
                out[nombre] = {"fechas": int(len(M)), "nota": "menos de 30 fechas"}; continue
            rng = np.random.default_rng(SEMILLA + 5)
            idx = rng.integers(0, len(M), size=(N_BOOT, len(M)))
            S = M[idx].sum(axis=1); reps = (S[:, 1] - S[:, 2]) / S[:, 0]
            lo, hi = np.quantile(reps, [0.025, 0.975])
            pred = res["predicciones_escritas_antes"][e]
            delta = dfz._ventaja(M)
            # compatibilidad propagando LAS DOS incertidumbres (medida y predicha)
            se_m = float(hi - lo) / 3.92; se_p = (pred["exp_ic95_pp"][1] - pred["exp_ic95_pp"][0]) / 100 / 3.92
            dif = delta - pred["exp_pp"] / 100; se_d = math.sqrt(se_m ** 2 + se_p ** 2)
            ss = sub[sub["gap_pct"] != 0]
            out[nombre] = {"fechas": int(len(M)), "filas": int(M[:, 0].sum()),
                           "delta_pp": round(100 * delta, 2), "ic95_pp": [round(100 * float(lo), 2), round(100 * float(hi), 2)],
                           "contiene_cero": bool(lo <= 0 <= hi),
                           "diferencia_medido_menos_predicho_pp": round(100 * dif, 2),
                           "ic95_diferencia_pp": [round(100 * (dif - 1.96 * se_d), 2), round(100 * (dif + 1.96 * se_d), 2)],
                           "compatible_propagando_ambas": bool(abs(dif) <= 1.96 * se_d),
                           "tasa_base_gap_positivo": round(float((ss["gap_pct"] > 0).mean()), 3),
                           "corr_gap_sox": round(float(np.corrcoef(ss["gap_pct"], ss["sox_prev"])[0, 1]), 3),
                           "tickers_con_historia_en_la_ventana": sorted(ss["ticker"].unique().tolist()),
                           "prediccion_exp_pp": pred["exp_pp"], "prediccion_exp_ic95_pp": pred["exp_ic95_pp"],
                           "dentro_del_ic_de_la_prediccion_exp": bool(pred["exp_ic95_pp"][0] / 100 <= delta <= pred["exp_ic95_pp"][1] / 100),
                           "prediccion_isotonica_pp": pred["isotonica_pp"],
                           "dentro_del_ic_isotonica": bool(pred["isotonica_ic95_pp"][0] / 100 <= delta <= pred["isotonica_ic95_pp"][1] / 100)}
        res["medicion"]["por_exchange"][e] = out
    with open(RUTA_JSON, "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    return res


if __name__ == "__main__":
    if "--ajustar" in sys.argv:
        r = ajustar()
        print(json.dumps({"ajuste": r["ajuste"], "predicciones": r["predicciones_escritas_antes"]}, indent=1, default=str))
    elif "--medir" in sys.argv:
        r = medir(redescargar="--redescargar" in sys.argv)
        print(json.dumps(r["medicion"], indent=1, default=str))
    else:
        print("usar --ajustar y después --medir")
