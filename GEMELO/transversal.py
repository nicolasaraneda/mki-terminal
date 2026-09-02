"""Frente D de la octava corrida: predicción transversal (ranking dentro del día).

Pre-registro: `GEMELO/preregistro/frente_D.md` (leerlo primero: estadístico,
nula, intervalo, partición y efecto relevante están fijados ahí).

Dos ventanas:
  1. Sellada (viva, regla firmada, excluir_cero): predicción = la sellada.
  2. Larga reconstruida SIN motor: predicción transversal = orden de β
     (OLS gap ~ SOX(t−1) por ticker, estimado SÓLO en los años de ajuste)
     multiplicado por el signo del SOX de la sesión anterior. Gaps de
     `GEMELO/cache/gaps_*.csv` y `^SOX` de la caché testigo (lectura).

Uso: `python GEMELO/transversal.py [--abrir-prueba]` →
`GEMELO/resultados/transversal.{json,md}`. Sin `--abrir-prueba` sólo corre
la ventana sellada y los años de ajuste (protocolo: la prueba se abre
después de cerrar y auditar el ajuste).
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

from backtest import linea_base as lb
from GEMELO import bifurcaciones as bf                       # noqa: E402

DIR_RESULTADOS = os.path.join(_AQUI, "resultados")
RUTA_GAPS_GZ = os.path.join(DIR_RESULTADOS, "testigos_fuente", "gaps_v2_propio_indice.csv.gz")
RUTA_SOX_GZ = os.path.join(DIR_RESULTADOS, "testigos_fuente", "cierres_353cacd57dc25f6a.csv.gz")
SEMILLA = 20260902
N_PERM = 4000
N_BOOT = 4000
MIN_TICKERS = 4
RHO_RELEVANTE = 0.20
AJUSTE = ("2018-09-01", "2023-12-31")
PRUEBA = ("2024-01-01", "2026-08-31")
EMBARGO_SESIONES = 5          # purga en la frontera ajuste/prueba (como backtest.EMBARGO_DIAS)
BURN_IN = 250                 # sesiones antes de la primera β causal
SELLADA = ("2026-07-05", "2026-08-31")   # excluida de la prueba: ya fue leída (auditoría F2)


def _rangos(x: np.ndarray) -> np.ndarray:
    return pd.Series(x).rank().to_numpy()


def spearman(a, b) -> float:
    ra, rb = _rangos(np.asarray(a, float)), _rangos(np.asarray(b, float))
    if ra.std() == 0 or rb.std() == 0:
        return 0.0
    with np.errstate(invalid="ignore", divide="ignore"):     # (dictamen D, exigido 15)
        return float(np.corrcoef(ra, rb)[0, 1])


def kendall(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = len(a)
    s = 0
    for i in range(n):
        for j in range(i + 1, n):
            s += np.sign(a[i] - a[j]) * np.sign(b[i] - b[j])
    return float(s / (n * (n - 1) / 2))


def concordancia_por_fecha(df: pd.DataFrame, col_pred: str, col_real: str) -> pd.DataFrame:
    filas = []
    for f, g in df.groupby("fecha"):
        if len(g) < MIN_TICKERS or g[col_real].nunique() < 2:
            continue
        filas.append({"fecha": f, "k": len(g),
                      "rho": spearman(g[col_pred], g[col_real]),
                      "tau": kendall(g[col_pred], g[col_real])})
    return pd.DataFrame(filas)


def _corr_filas(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Correlación de cada fila de A (n_perm × k) con el vector b (k)."""
    A = A - A.mean(axis=1, keepdims=True)
    b = b - b.mean()
    den = np.sqrt((A ** 2).sum(axis=1) * (b ** 2).sum())
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, (A @ b) / den, 0.0)


def inferencia(df: pd.DataFrame, col_pred: str, col_real: str, semilla: int = SEMILLA) -> dict:
    """ρ̄ y τ̄ con p por permutación DENTRO de cada fecha (vectorizada por
    grupo) e IC por bootstrap de fechas."""
    conc = concordancia_por_fecha(df, col_pred, col_real)
    if conc.empty:
        return {"fechas": 0}
    rng = np.random.default_rng(semilla)
    grupos = [g for _, g in df.groupby("fecha") if len(g) >= MIN_TICKERS and g[col_real].nunique() > 1]
    obs_rho, obs_tau = conc["rho"].mean(), conc["tau"].mean()
    # permutación dentro del día: para cada grupo, n_perm permutaciones de
    # los rangos realizados contra los rangos predichos (fijos)
    nulos = np.zeros(N_PERM)
    for g in grupos:
        rp = _rangos(g[col_pred].to_numpy(float))
        rr = _rangos(g[col_real].to_numpy(float))
        k = len(rr)
        perms = np.argsort(rng.random((N_PERM, k)), axis=1)
        nulos += _corr_filas(rr[perms], rp)
    nulos /= len(grupos)
    n_ge = int((np.abs(nulos) >= abs(obs_rho) - 1e-12).sum())
    p_rho = float((1 + n_ge) / (N_PERM + 1))
    # bootstrap de fechas (percentil iid) + t de clúster con gl = k−1 (el
    # estimador que el Frente A midió bien calibrado con pocos clústeres)
    r = conc["rho"].to_numpy()
    idx = rng.integers(0, len(r), size=(N_BOOT, len(r)))
    reps = r[idx].mean(axis=1)
    lo, hi = np.quantile(reps, [0.025, 0.975])
    k = len(r)
    se_muestral = float(r.std(ddof=1) / math.sqrt(k))
    tq = bf._t_ppf(0.975, k - 1) if k > 2 else float("nan")
    lo_tc, hi_tc = float(obs_rho - tq * se_muestral), float(obs_rho + tq * se_muestral)
    se_nula = float(nulos.std(ddof=1))
    # dos SE, dos p: la permutación condiciona a la dispersión NULA de ρ_d, que
    # en la sellada es menor que la real; el p con la SE muestral es el otro
    p_z_muestral = float(math.erfc(abs(obs_rho) / se_muestral / math.sqrt(2))) if se_muestral > 0 else float("nan")
    t = conc["tau"].to_numpy()
    reps_t = t[idx].mean(axis=1)
    lo_t, hi_t = np.quantile(reps_t, [0.025, 0.975])
    pos = int((r > 0).sum())
    w_lo, w_hi = lb._wilson(pos, k)
    return {"fechas": int(len(conc)), "filas": int(sum(len(g) for g in grupos)),
            "rho_medio": round(float(obs_rho), 4), "ic95_rho": [round(float(lo), 4), round(float(hi), 4)],
            "ic95_rho_t_cluster": [round(lo_tc, 4), round(hi_tc, 4)],
            "se_muestral": round(se_muestral, 4), "se_nula_permutacion": round(se_nula, 4),
            "p_permutacion_dentro_del_dia": round(p_rho, 4),
            "p_permutacion_texto": (f"< {1 / (N_PERM + 1):.5f} (piso de {N_PERM} permutaciones)" if n_ge == 0 else f"{p_rho:.4f}"),
            "p_z_se_muestral": round(p_z_muestral, 4),
            "tau_medio": round(float(obs_tau), 4), "ic95_tau": [round(float(lo_t), 4), round(float(hi_t), 4)],
            "fraccion_fechas_rho_positivo": round(float((r > 0).mean()), 3),
            "wilson95_fraccion_positiva": [round(w_lo / 100, 3), round(w_hi / 100, 3)],
            "relevante": bool(lo > RHO_RELEVANTE), "contiene_cero": bool(lo <= 0 <= hi),
            "contiene_cero_t_cluster": bool(lo_tc <= 0 <= hi_tc),
            "mde_80_con_se_muestral": round(2.8 * se_muestral, 4)}


def nula_etiquetas_beta(df: pd.DataFrame, betas: dict, n_rep: int = 2000, semilla: int = SEMILLA) -> dict:
    """La nula HONESTA para «el orden de las β tiene información»: un orden
    cualquiera de los mismos tickers. Se permuta el vector β entre los
    tickers y se recomputa ρ̄ con la misma maquinaria. La unidad de
    replicación de la afirmación es el ORDENAMIENTO (n = 1), no la fecha
    (dictamen D, bloqueo 3). La within-day queda como sensibilidad."""
    rng = np.random.default_rng(semilla + 7)
    tick = sorted(betas)
    vals = np.array([betas[t] for t in tick])
    obs = concordancia_por_fecha(prediccion_transversal(df, betas), "pred", "gap_pct")["rho"].mean()
    nul = []
    for _ in range(n_rep):
        b = dict(zip(tick, vals[rng.permutation(len(vals))]))
        nul.append(concordancia_por_fecha(prediccion_transversal(df, b), "pred", "gap_pct")["rho"].mean())
    nul = np.array(nul)
    return {"rho_observado": round(float(obs), 4), "n_rep": n_rep, "nula_media": round(float(nul.mean()), 4),
            "nula_sd": round(float(nul.std(ddof=1)), 4),
            "nula_q025_q975": [round(float(np.quantile(nul, 0.025)), 4), round(float(np.quantile(nul, 0.975)), 4)],
            "p_bilateral": round(float((1 + (np.abs(nul) >= abs(obs) - 1e-12).sum()) / (n_rep + 1)), 4),
            "fraccion_ordenes_sobre_relevante": round(float((nul > RHO_RELEVANTE).mean()), 3)}


def dejar_uno_fuera(df: pd.DataFrame, col_pred: str, col_real: str) -> dict:
    out = {}
    for t in sorted(df["ticker"].unique()):
        c = concordancia_por_fecha(df[df["ticker"] != t], col_pred, col_real)
        out[f"sin_{t}"] = round(float(c["rho"].mean()), 4) if len(c) else None
    return out


def por_signo_sox(df: pd.DataFrame, col_pred: str, col_real: str, col_sox: str) -> dict:
    """Si el efecto fuera un artefacto de diferencias incondicionales de nivel
    entre tickers, sería positivo en días de alza y negativo en días de baja."""
    out = {}
    for nombre, mask in (("sox_positivo", df[col_sox] > 0), ("sox_negativo", df[col_sox] < 0)):
        c = concordancia_por_fecha(df[mask], col_pred, col_real)
        if len(c) > 2:
            r = c["rho"].to_numpy(); se = r.std(ddof=1) / math.sqrt(len(r))
            out[nombre] = {"fechas": int(len(r)), "rho_medio": round(float(r.mean()), 4),
                           "ic95_aprox": [round(float(r.mean() - 1.96 * se), 4), round(float(r.mean() + 1.96 * se), 4)]}
    return out


def identidad_signo(df: pd.DataFrame, betas: dict) -> float:
    """ρ_d ≡ sign(S_d)·spearman(orden β, gap): dentro de un día la predicción
    β·S sólo aporta el SIGNO del SOX. Devuelve la discrepancia máxima."""
    d = prediccion_transversal(df, betas)
    d["orden"] = d["ticker"].map(betas)
    a = concordancia_por_fecha(d, "pred", "gap_pct").set_index("fecha")["rho"]
    b = concordancia_por_fecha(d.assign(pred=d["orden"]), "pred", "gap_pct").set_index("fecha")["rho"]
    sg = d.groupby("fecha")["sox_prev"].first().reindex(a.index)
    return float((a - np.sign(sg) * b.reindex(a.index)).abs().max())


# ------------------------------------------------------------
# ventana larga sin motor
# ------------------------------------------------------------
def cargar_larga() -> pd.DataFrame:
    with gzip.open(RUTA_GAPS_GZ, "rt") as f:
        gaps = pd.read_csv(f)
    gaps["fecha"] = pd.to_datetime(gaps["sesion"])
    with gzip.open(RUTA_SOX_GZ, "rt") as f:
        sox = pd.read_csv(f, index_col=0, parse_dates=True)["^SOX"].dropna()
    ret = sox.pct_change().dropna() * 100
    # el SOX «de la sesión anterior» a una sesión local d es el último cierre
    # de NY estrictamente anterior a d (la apertura asiática de d ocurre
    # después del cierre de NY de d−1): merge_asof hacia atrás, excluyente
    r = pd.DataFrame({"fecha_sox": ret.index, "sox_prev": ret.to_numpy()}).sort_values("fecha_sox")
    g = gaps.sort_values("fecha")
    m = pd.merge_asof(g, r, left_on="fecha", right_on="fecha_sox", direction="backward",
                      allow_exact_matches=False)
    m = m.dropna(subset=["sox_prev"])
    return m[["fecha", "ticker", "gap_pct", "sox_prev"]]


def orden_beta(df: pd.DataFrame, desde: str, hasta: str) -> dict:
    """β_i por OLS gap ~ SOX(t−1), sólo en [desde, hasta]. Devuelve {ticker: β}."""
    sub = df[(df["fecha"] >= desde) & (df["fecha"] <= hasta)]
    out = {}
    for t, g in sub.groupby("ticker"):
        x, y = g["sox_prev"].to_numpy(float), g["gap_pct"].to_numpy(float)
        vx = x.var()
        out[t] = float(((x - x.mean()) * (y - y.mean())).mean() / vx) if vx > 0 else 0.0
    return out


def prediccion_transversal(df: pd.DataFrame, betas: dict, excluir_cero: bool = True) -> pd.DataFrame:
    """Predicción con β FIJAS (las del ajuste): para la prueba. `excluir_cero`
    filtra sobre la variable dependiente (108/15.011 filas en la larga):
    se publica la sensibilidad con y sin."""
    out = df.copy()
    out["pred"] = out["ticker"].map(betas) * out["sox_prev"]
    return out[out["gap_pct"] != 0] if excluir_cero else out


def betas_causales(df: pd.DataFrame, burn_in: int = BURN_IN) -> pd.DataFrame:
    """β_i estimada, para cada fecha d, SÓLO con filas de fechas < d
    (expansiva). Es la única forma de evaluar dentro del ajuste sin que la
    fila evaluada participe de su propio predictor (auditoría F1: la
    primera versión estimaba β con todo el ajuste y evaluaba sobre lo mismo).
    Devuelve el frame con `pred` causal; las primeras `burn_in` sesiones por
    ticker no tienen predicción."""
    out = []
    for t, g in df.sort_values("fecha").groupby("ticker"):
        x = g["sox_prev"].to_numpy(float); y = g["gap_pct"].to_numpy(float)
        n = np.arange(1, len(x) + 1)
        sx, sy, sxx, sxy = np.cumsum(x), np.cumsum(y), np.cumsum(x * x), np.cumsum(x * y)
        # momentos con las filas 1..i (inclusive) -> se usan para la fila i+1
        cov = sxy / n - (sx / n) * (sy / n)
        var = sxx / n - (sx / n) ** 2
        beta_hasta_i = np.where(var > 0, cov / var, np.nan)
        beta_prev = np.concatenate([[np.nan], beta_hasta_i[:-1]])   # sólo pasado estricto
        beta_prev[:burn_in] = np.nan
        gg = g.copy(); gg["beta_causal"] = beta_prev; gg["pred"] = gg["beta_causal"] * gg["sox_prev"]
        out.append(gg)
    res = pd.concat(out).dropna(subset=["pred"])
    return res[res["gap_pct"] != 0]


def main(abrir_prueba: bool = False) -> dict:
    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "etiqueta": "PROPUESTA — Frente D, octava corrida; pendiente de dictamen",
           "parametros": {"n_perm": N_PERM, "n_boot": N_BOOT, "min_tickers": MIN_TICKERS,
                          "rho_relevante": RHO_RELEVANTE, "ajuste": AJUSTE, "prueba": PRUEBA,
                          "semilla": SEMILLA, "prueba_abierta": abrir_prueba}}
    # 1. sellada
    sell = lb.aplicar_convencion(lb.cargar(hasta_sello=None), lb.CONVENCION_OFICIAL)
    res["sellada"] = {"ultimo_sello": sell["fecha"].max(),
                      **inferencia(sell, "apertura_estimada_pct", "gap_pct"),
                      "dejar_uno_fuera": dejar_uno_fuera(sell, "apertura_estimada_pct", "gap_pct"),
                      "nota_ic": "el IC que vale es el de t de clúster (k = 35); el percentil sub-cubre (Frente A) y bloques de 20 degenera (2 bloques)",
                      "nota_empates": "apertura_estimada_pct está sellada a 2 decimales: empates en varias fechas atenúan ρ (sesgo CONTRA el hallazgo)"}
    # R2 (barra congelada): sin el bloque 15–23 jul
    r2 = sell[~((sell["fecha"] >= "2026-07-15") & (sell["fecha"] <= "2026-07-23"))]
    res["sellada"]["R2_sin_15_23_jul"] = inferencia(r2, "apertura_estimada_pct", "gap_pct", semilla=SEMILLA + 3)
    betas_campeon = sell.groupby("ticker")["beta"].mean().to_dict()
    res["sellada"]["betas_campeon_media_sellada"] = {k: round(v, 4) for k, v in betas_campeon.items()}
    # 2. larga: ajuste, con β CAUSAL (expansiva) — cada fila se evalúa con la
    # β estimada sólo con fechas anteriores; la β final del ajuste es la que
    # entra fija a la prueba
    larga = cargar_larga()
    betas = orden_beta(larga, *AJUSTE)
    res["larga"] = {"betas_ajuste": {k: round(v, 4) for k, v in betas.items()},
                    "orden_beta_ajuste": sorted(betas, key=betas.get, reverse=True),
                    "fuente_gaps": os.path.relpath(RUTA_GAPS_GZ, _RAIZ),
                    "fuente_sox": os.path.relpath(RUTA_SOX_GZ, _RAIZ),
                    "embargo_sesiones": EMBARGO_SESIONES, "burn_in": BURN_IN,
                    "sellada_excluida_de_la_prueba": SELLADA,
                    "excluir_cero": "aplicado también a la ventana larga (declarado en la enmienda del pre-registro)"}
    aj = betas_causales(larga[(larga["fecha"] >= AJUSTE[0]) & (larga["fecha"] <= AJUSTE[1])])
    aj["fecha"] = aj["fecha"].dt.date.astype(str)
    res["larga"]["ajuste_causal"] = inferencia(aj, "pred", "gap_pct")
    if abrir_prueba:
        desde = pd.Timestamp(PRUEBA[0]) + pd.tseries.offsets.BDay(EMBARGO_SESIONES)
        pr_ = larga[(larga["fecha"] >= desde) & (larga["fecha"] <= PRUEBA[1])
                    & ~((larga["fecha"] >= SELLADA[0]) & (larga["fecha"] <= SELLADA[1]))]
        crudo = pr_.copy()
        pr_ = prediccion_transversal(pr_, betas)
        pr_["fecha"] = pr_["fecha"].dt.date.astype(str)
        res["larga"]["prueba"] = {"desde_con_embargo": desde.date().isoformat(),
                                  "aperturas_de_la_prueba": ["12:11 (gaps v1, 626 fechas, ρ̄ 0,2373) — defecto de datos en descargar_gaps", "12:14 (gaps v2, 637 fechas) — la vigente; dos evaluaciones del holdout propio del frente, declaradas"],
                                  **inferencia(pr_, "pred", "gap_pct", semilla=SEMILLA + 1),
                                  "nula_etiquetas_beta": nula_etiquetas_beta(crudo, betas),
                                  "dejar_uno_fuera": dejar_uno_fuera(pr_, "pred", "gap_pct"),
                                  "por_signo_sox": por_signo_sox(pr_, "pred", "gap_pct", "sox_prev"),
                                  "identidad_rho_signo_max_discrepancia": identidad_signo(crudo, betas),
                                  "sin_excluir_cero": {k: v for k, v in inferencia(prediccion_transversal(crudo, betas, excluir_cero=False).assign(fecha=lambda d: d["fecha"].dt.date.astype(str)), "pred", "gap_pct", semilla=SEMILLA + 2).items() if k in ("fechas", "filas", "rho_medio", "ic95_rho")}}
        # el CAMPEÓN, no el proxy: el orden de las β selladas (media por ticker),
        # contrafactual CONTAMINADO (β estimadas en 2026) = cota optimista
        camp = prediccion_transversal(crudo, betas_campeon)
        camp["fecha"] = camp["fecha"].dt.date.astype(str)
        res["larga"]["prueba_con_orden_del_campeon"] = {
            "rotulo": "CONTRAFACTUAL CONTAMINADO (β selladas, estimadas en 2026): cota optimista de lo que el campeón habría hecho",
            **{k: v for k, v in inferencia(camp, "pred", "gap_pct", semilla=SEMILLA + 4).items()
               if k in ("fechas", "rho_medio", "ic95_rho", "ic95_rho_t_cluster", "relevante", "fraccion_fechas_rho_positivo")}}
        ca, cb = concordancia_por_fecha(pr_, "pred", "gap_pct").set_index("fecha")["rho"], concordancia_por_fecha(camp, "pred", "gap_pct").set_index("fecha")["rho"]
        dif = (ca - cb.reindex(ca.index)).dropna().to_numpy()
        se_d = dif.std(ddof=1) / math.sqrt(len(dif))
        res["larga"]["proxy_menos_campeon"] = {"fechas": int(len(dif)), "diferencia": round(float(dif.mean()), 4),
                                               "ic95_aprox": [round(float(dif.mean() - 1.96 * se_d), 4), round(float(dif.mean() + 1.96 * se_d), 4)]}
        rk = [betas[t] for t in sorted(betas)]; rc = [betas_campeon[t] for t in sorted(betas)]
        res["larga"]["spearman_beta_proxy_vs_campeon"] = round(spearman(np.array(rk), np.array(rc)), 4)
        res["larga"]["universo"] = "los 8 tickers son la composición de 2026 (universo.MERCADOS_POR_ABRIR) aplicada hacia atrás a 2018: selección ex post del corte transversal, declarada"
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "transversal.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "transversal.md"), "w") as f:
        f.write(informe(res))
    return res


def _fila(nombre, v):
    if v.get("fechas", 0) == 0:
        return f"| {nombre} | 0 | — | — | — | — | — |"
    return (f"| {nombre} | {v['fechas']} ({v['filas']} filas) | **{v['rho_medio']}** | {v['ic95_rho']}"
            f"{' (contiene el cero)' if v['contiene_cero'] else ''} | {v['ic95_rho_t_cluster']}"
            f"{' (contiene el cero)' if v['contiene_cero_t_cluster'] else ''} | {v['p_permutacion_texto']} / {v['p_z_se_muestral']} | "
            f"{v['tau_medio']} {v['ic95_tau']} | {v['fraccion_fechas_rho_positivo']} {v['wilson95_fraccion_positiva']} |")


def informe(r: dict) -> str:
    L = ["# Predicción transversal: ¿el orden de las β tiene información? — Frente D (PROPUESTA)\n",
         f"> **{r['etiqueta']}** · generado {r['generado_en_utc']} · `python GEMELO/transversal.py`"
         f"{' --abrir-prueba' if r['parametros']['prueba_abierta'] else ''}\n",
         f"Pre-registro: `GEMELO/preregistro/frente_D.md`. Unidad = la FECHA (n efectivo = fechas con ≥ {r['parametros']['min_tickers']} tickers). "
         f"p por permutación dentro del día ({r['parametros']['n_perm']}), IC por bootstrap de fechas ({r['parametros']['n_boot']}). "
         f"Efecto relevante pre-declarado: ρ̄ ≥ {r['parametros']['rho_relevante']}.\n",
         "**Título honesto (dictamen D):** un orden de β estimado SIN el motor ordena dentro del día; el orden del CAMPEÓN no alcanza la vara pre-registrada y en la ventana sellada no sobrevive a R2. Toda fila de la ventana larga es sobre el PROXY (OLS gap ~ SOX(t−1), expansiva/fija), no sobre el modelo 4.6.0 (rodante 120, cierre-a-cierre).\n",
         "| ventana | fechas (n efectivo) | ρ̄ Spearman | IC95 percentil | IC95 t de clúster | p permutación within-day / p con SE muestral | τ̄ Kendall IC95 | fechas con ρ > 0 [Wilson] |",
         "|---|---|---|---|---|---|---|---|",
         _fila(f"sellada (viva hasta {r['sellada']['ultimo_sello']}, predicción sellada)", r["sellada"]),
         _fila(f"larga · años de AJUSTE {r['parametros']['ajuste']} (β CAUSAL expansiva, burn-in {r['larga']['burn_in']})", r["larga"]["ajuste_causal"])]
    if "prueba" in r["larga"]:
        L.append(_fila(f"larga · años de PRUEBA desde {r['larga']['prueba']['desde_con_embargo']} (embargo {r['larga']['embargo_sesiones']} sesiones; β del ajuste fija; sin las fechas selladas {r['larga']['sellada_excluida_de_la_prueba']})", r["larga"]["prueba"]))
    else:
        L.append("| larga · años de PRUEBA | **no abiertos todavía** (protocolo: después de cerrar y auditar el ajuste) | | | | | | |")
    se_ = r["sellada"]
    L += ["", f"**Sellada, R2 (sin 15–23 jul):** ρ̄ {se_['R2_sin_15_23_jul']['rho_medio']} percentil {se_['R2_sin_15_23_jul']['ic95_rho']} / t de clúster {se_['R2_sin_15_23_jul']['ic95_rho_t_cluster']}"
          f"{' — cruza el cero: R2 SE ACTIVA' if se_['R2_sin_15_23_jul']['contiene_cero_t_cluster'] else ''}. MDE al 80% con la SE muestral: {se_['mde_80_con_se_muestral']} (efecto observado {se_['rho_medio']}). "
          f"Dejar-uno-fuera: {se_['dejar_uno_fuera']}. {se_['nota_ic']}. {se_['nota_empates']}."]
    if "prueba" in r["larga"]:
        pr_ = r["larga"]["prueba"]; ne = pr_["nula_etiquetas_beta"]; cc = r["larga"]["prueba_con_orden_del_campeon"]; pm = r["larga"]["proxy_menos_campeon"]
        L += ["", f"**Nula honesta (principal): etiquetas de β permutadas entre tickers** ({ne['n_rep']} réplicas): ρ̄ observado {ne['rho_observado']}, nula media {ne['nula_media']}, sd {ne['nula_sd']}, "
              f"q2,5/97,5 {ne['nula_q025_q975']}, **p bilateral {ne['p_bilateral']}**; fracción de órdenes aleatorios sobre {r['parametros']['rho_relevante']}: {ne['fraccion_ordenes_sobre_relevante']}. "
              "La unidad de replicación de la afirmación es el ORDENAMIENTO (n = 1); la permutación within-day es una sensibilidad de una hipótesis más débil.",
              f"**Identidad verificada:** ρ_d = sign(S_d)·spearman(orden β, gap), discrepancia máxima {pr_['identidad_rho_signo_max_discrepancia']:.2e}: el «modelo transversal» es un vector de 8 β más un bit por día.",
              f"Por signo del SOX: {pr_['por_signo_sox']} (simétrico = no es artefacto de nivel). Dejar-uno-fuera: {pr_['dejar_uno_fuera']}. Sin `excluir_cero`: {pr_['sin_excluir_cero']}.",
              f"Aperturas de la prueba: {pr_['aperturas_de_la_prueba']}.",
              f"**El CAMPEÓN, no el proxy:** orden de las β selladas → ρ̄ {cc['rho_medio']} {cc['ic95_rho']} (t de clúster {cc['ic95_rho_t_cluster']}), relevante: {cc['relevante']} — {cc['rotulo']}. "
              f"Proxy − campeón: {pm['diferencia']} {pm['ic95_aprox']} sobre {pm['fechas']} fechas. Spearman entre los dos vectores de β: {r['larga']['spearman_beta_proxy_vs_campeon']}.",
              f"Universo: {r['larga']['universo']}."]
    L += ["", f"Orden de β en el ajuste: {r['larga']['orden_beta_ajuste']} ({r['larga']['betas_ajuste']}).",
          f"Fuentes sin motor: `{r['larga']['fuente_gaps']}` (gaps reconstruidos) y `{r['larga']['fuente_sox']}` (SOX, caché testigo).", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    r = main(abrir_prueba="--abrir-prueba" in sys.argv)
    print(json.dumps({"sellada": r["sellada"], "larga_ajuste_causal": r["larga"]["ajuste_causal"],
                      "prueba": r["larga"].get("prueba")}, indent=1, default=str))
