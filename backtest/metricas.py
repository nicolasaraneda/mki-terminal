# ============================================================
# Métricas del backtest (DISEÑO.md §8) — fijadas antes de correr.
#
# Rank IC diario, hit rate condicionado con Wilson, MAE, calibración,
# Sharpe neto con bootstrap por bloques (semilla fija), max drawdown,
# turnover, y el VEREDICTO ESCALONADO (ajuste del GATE B): cada capa
# contra la anterior con test t Newey-West de las diferencias de IC.
# ============================================================

import numpy as np
import pandas as pd

from api.utilidades import Z_POR_NOMINAL, intervalo_wilson

SEMILLA_BOOTSTRAP = 5_0_0  # fija: misma corrida → mismos intervalos


def rank_ic_diario(df: pd.DataFrame) -> pd.Series:
    """IC de Spearman (est vs gap real) por fecha de emisión. Requiere ≥4
    pares por día. Una predicción CONSTANTE (B0) puntúa IC = 0: cero
    información de ordenamiento — así 'B1 vs B0' es literalmente
    'momentum vs nada', con las series emparejadas por fecha."""
    ics = {}
    for fecha, g in df.dropna(subset=["gap_pct"]).groupby("fecha_emision"):
        if len(g) < 4:
            continue
        if g["est"].nunique() < 2:
            ics[fecha] = 0.0
        else:
            ics[fecha] = float(g["est"].rank().corr(g["gap_pct"].rank()))
    return pd.Series(ics).dropna()


def t_newey_west(serie: pd.Series, lag: int = 5) -> float:
    """t-stat de la media con errores Newey-West (autocorrelación hasta
    `lag`)."""
    x = serie.dropna().values
    n = len(x)
    if n < 10:
        return float("nan")
    media = x.mean()
    e = x - media
    var = float(e @ e) / n
    for k in range(1, min(lag, n - 1) + 1):
        peso = 1 - k / (lag + 1)
        var += 2 * peso * float(e[k:] @ e[:-k]) / n
    ee = (var / n) ** 0.5
    return media / ee if ee > 0 else float("nan")


def hits_condicionados(df: pd.DataFrame) -> list:
    """Hit rate del signo del gap, global y condicionado a |est|, cada
    celda con su Wilson 95%."""
    d = df.dropna(subset=["gap_pct"])
    d = d[d["est"] != 0]  # B0 no tiene signo que acertar
    resultado = []
    for etiqueta, sub in (("global", d),
                          ("|est| > 0.5%", d[d["est"].abs() > 0.5]),
                          ("|est| > 1.0%", d[d["est"].abs() > 1.0])):
        n = len(sub)
        if n == 0:
            resultado.append({"condicion": etiqueta, "n": 0})
            continue
        k = int(((sub["est"] >= 0) == (sub["gap_pct"] >= 0)).sum())
        lo, hi = intervalo_wilson(k, n)
        resultado.append({"condicion": etiqueta, "n": n,
                          "hit_pct": round(100 * k / n, 1),
                          "wilson_lo_pct": lo, "wilson_hi_pct": hi})
    return resultado


def mae_gap(df: pd.DataFrame) -> float | None:
    d = df.dropna(subset=["gap_pct"])
    if d.empty:
        return None
    return round(float((d["est"] - d["gap_pct"]).abs().mean()), 3)


def calibracion(df: pd.DataFrame) -> dict | None:
    d = df.dropna(subset=["gap_pct", "int80"])
    if len(d) < 30:
        return None
    err = (d["gap_pct"] - d["est"]).abs()
    sigma = d["int80"] / Z_POR_NOMINAL[80]
    niveles = sorted(Z_POR_NOMINAL)
    return {"nominal_pct": niveles,
            "real_pct": [round(float((err <= sigma * Z_POR_NOMINAL[q]).mean() * 100), 1)
                         for q in niveles],
            "n": int(len(d))}


def sharpe_anual(retornos_pct: pd.Series) -> float | None:
    r = retornos_pct.dropna() / 100
    if len(r) < 20 or r.std() == 0:
        return None
    return round(float(r.mean() / r.std() * np.sqrt(252)), 2)


def bootstrap_sharpe(retornos_pct: pd.Series, bloques: int = 10,
                     replicas: int = 2000) -> tuple | None:
    """IC 90% del Sharpe por bootstrap de bloques (semilla fija)."""
    r = (retornos_pct.dropna() / 100).values
    n = len(r)
    if n < 40:
        return None
    rng = np.random.default_rng(SEMILLA_BOOTSTRAP)
    sharpes = []
    n_bloques = int(np.ceil(n / bloques))
    for _ in range(replicas):
        inicios = rng.integers(0, n - bloques, n_bloques)
        muestra = np.concatenate([r[i:i + bloques] for i in inicios])[:n]
        if muestra.std() > 0:
            sharpes.append(muestra.mean() / muestra.std() * np.sqrt(252))
    if not sharpes:
        return None
    return (round(float(np.percentile(sharpes, 5)), 2),
            round(float(np.percentile(sharpes, 95)), 2))


def max_drawdown(retornos_pct: pd.Series) -> float | None:
    r = retornos_pct.dropna() / 100
    if r.empty:
        return None
    equity = (1 + r).cumprod()
    dd = equity / equity.cummax() - 1
    return round(float(dd.min()) * 100, 1)


def veredicto_escalonado(ics_por_baseline: dict) -> list:
    """Ajuste del GATE B: cada capa contra la ANTERIOR — delta de rank IC
    medio con t Newey-West de las diferencias diarias emparejadas.
    'aporta' = delta > 0 con t > 2."""
    orden = [b for b in ("B0", "B1", "B2", "B3", "B4", "B5")
             if b in ics_por_baseline]
    filas = []
    for previo, actual in zip(orden, orden[1:]):
        par = pd.concat({"a": ics_por_baseline[actual],
                         "p": ics_por_baseline[previo]}, axis=1).dropna()
        if len(par) < 10:
            filas.append({"capa": f"{actual} vs {previo}", "n_dias": len(par),
                          "veredicto": "insuficiente"})
            continue
        delta = par["a"] - par["p"]
        t = t_newey_west(delta)
        filas.append({
            "capa": f"{actual} vs {previo}",
            "delta_ic": round(float(delta.mean()), 4),
            "t_nw": round(t, 2) if t == t else None,
            "n_dias": int(len(par)),
            "veredicto": ("aporta" if delta.mean() > 0 and t > 2
                          else "no demostrado"),
        })
    return filas
