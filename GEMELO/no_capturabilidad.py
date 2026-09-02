"""Frente C de la octava corrida: la no capturabilidad como hipótesis.

Pre-registro: `GEMELO/preregistro/frente_C.md` (H1 estructural, H2
asimetría de magnitud, H3 sobrerreacción/deriva; estadísticos, efectos
relevantes y partición fijados ahí). Sin motor: la predicción es el signo
del último cierre de NY anterior a la apertura local.

Datos (testigos preservados, no cachés mutables): gaps v2
(`gaps_v2_propio_indice.csv.gz`), cierres de los 8 tickers
(`cierres_03fdca36d64efb0d.csv.gz`, 26-ago) y `^SOX` del 1-sep.
Sesión r = close_d / open_d − 1 con open_d = close_{d−1}·(1 + g/100).

Uso: `python GEMELO/no_capturabilidad.py [--abrir-prueba]` →
`GEMELO/resultados/no_capturabilidad.{json,md}`.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(_AQUI)
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from universo import EXCHANGE_POR_TICKER                     # noqa: E402

DIR_RESULTADOS = os.path.join(_AQUI, "resultados")
T = os.path.join(DIR_RESULTADOS, "testigos_fuente")
RUTA_GAPS_GZ = os.path.join(T, "gaps_v2_propio_indice.csv.gz")
RUTA_CIERRES_GZ = os.path.join(T, "cierres_03fdca36d64efb0d.csv.gz")
RUTA_SOX_GZ = os.path.join(T, "cierres_353cacd57dc25f6a.csv.gz")
SEMILLA = 20260902
N_BOOT = 4000
BLOQUE_FECHAS = 10          # bootstrap de bloques CIRCULARES de fechas (DISEÑO.md §8.5); |q| tiene AC 0,18-0,21
AJUSTE = ("2018-09-01", "2023-12-31")
# El testigo de cierres se capturó el 2026-08-26 04:23 UTC con Seúl, Tokio y
# Taipéi EN SESIÓN: su última barra es una cotización en vivo, no un cierre
# (auditoría de fuga, 2-sep). Se trunca en la última barra COMPLETA.
CAPTURA_CIERRES_UTC = "2026-08-26T04:23:39Z"
ULTIMA_BARRA_COMPLETA = "2026-08-25"
PRUEBA = ("2024-01-01", ULTIMA_BARRA_COMPLETA)
EMBARGO_SESIONES = 5
RUTA_BACKUP_SENALES = os.path.join(_RAIZ, "data", "backups", "senales_senales_ticker.csv")
RUTA_PREREGISTRO = os.path.join(_AQUI, "preregistro", "frente_C.md")
RUTA_LOCK = os.path.join(DIR_RESULTADOS, "no_capturabilidad.lock")


def sellada_desde_backup() -> tuple:
    """La ventana sellada NO se escribe a mano: se deriva de `sesion_objetivo`
    del backup versionado (la constante manual decía 05-jul → 31-ago y las
    sesiones selladas llegan al 02-sep). Devuelve (primera, última)."""
    b = pd.read_csv(RUTA_BACKUP_SENALES, usecols=["sesion_objetivo"])
    so = pd.to_datetime(b["sesion_objetivo"]).dropna()
    return (so.min().strftime("%Y-%m-%d"), so.max().strftime("%Y-%m-%d"))


SELLADA = sellada_desde_backup()


def cargar(hasta: str = ULTIMA_BARRA_COMPLETA) -> pd.DataFrame:
    """Filas (fecha, ticker, gap, sesión, sox_prev) hasta la última barra
    completa. `hasta` existe para el test de invariancia a truncar: el valor
    de cada fila en t no depende de nada posterior a t."""
    with gzip.open(RUTA_GAPS_GZ, "rt") as f:
        gaps = pd.read_csv(f)
    gaps["fecha"] = pd.to_datetime(gaps["sesion"])
    gaps = gaps[gaps["fecha"] <= hasta]
    with gzip.open(RUTA_CIERRES_GZ, "rt") as f:
        cierres = pd.read_csv(f, index_col=0, parse_dates=True)
    cierres = cierres[cierres.index <= hasta]
    with gzip.open(RUTA_SOX_GZ, "rt") as f:
        sox = pd.read_csv(f, index_col=0, parse_dates=True)["^SOX"].dropna()
    sox = sox[sox.index <= hasta]
    ret = (sox.pct_change().dropna() * 100).rename("sox_prev")
    r = pd.DataFrame({"fecha_sox": ret.index, "sox_prev": ret.to_numpy()}).sort_values("fecha_sox")
    filas = []
    for t in gaps["ticker"].unique():
        c = cierres[t].dropna()
        g = gaps[gaps["ticker"] == t].set_index("fecha")["gap_pct"]
        comun = g.index.intersection(c.index)
        c_prev = c.shift(1).reindex(comun)
        c_hoy = c.reindex(comun)
        gg = g.reindex(comun)
        open_ = c_prev * (1 + gg / 100.0)
        ses = (c_hoy / open_ - 1.0) * 100.0
        filas.append(pd.DataFrame({"fecha": comun, "ticker": t, "gap_pct": gg.to_numpy(),
                                   "sesion_pct": ses.to_numpy(),
                                   "total_pct": ((c_hoy / c_prev - 1.0) * 100.0).to_numpy()}))
    df = pd.concat(filas).dropna().sort_values("fecha")
    # `excluir_cero` en los DOS lados (dictamen C, bloqueo 10): un retorno TOTAL
    # exactamente cero es el mismo artefacto de ffill que un gap cero, y en esa
    # fila la sesión es, por identidad, −gap: una pérdida garantizada.
    df = df[np.isclose(df["total_pct"], 0.0) == False]
    df["exchange"] = df["ticker"].map(EXCHANGE_POR_TICKER)
    m = pd.merge_asof(df, r, left_on="fecha", right_on="fecha_sox", direction="backward",
                      allow_exact_matches=False).dropna(subset=["sox_prev"])
    return m[m["gap_pct"] != 0].reset_index(drop=True)


def _sumas_por_fecha(df: pd.DataFrame, cols) -> np.ndarray:
    """Matriz (fechas × [n, Σcol1, Σcol2, …]) para bootstrap vectorizado."""
    t = df[["fecha"] + list(cols)].copy()
    t["n"] = 1.0
    return t.groupby("fecha")[["n"] + list(cols)].sum().to_numpy(float)


def _indices_bloques(rng, n: int, n_boot: int, bloque: int) -> np.ndarray:
    """Bootstrap de bloques CIRCULARES de `bloque` fechas consecutivas (el
    mismo esquema que `backtest/metricas.bootstrap_sharpe` desde el 26-ago):
    los arranques se sortean en [0, n) y el bloque da la vuelta al final."""
    if bloque <= 1 or n <= bloque:
        return rng.integers(0, n, size=(n_boot, n))
    nb = -(-n // bloque)
    arranques = rng.integers(0, n, size=(n_boot, nb))
    idx = (arranques[:, :, None] + np.arange(bloque)[None, None, :]) % n
    return idx.reshape(n_boot, nb * bloque)[:, :n]


def _boot(M: np.ndarray, f, n_boot: int = N_BOOT, semilla: int = SEMILLA, bloque: int = BLOQUE_FECHAS,
          nulo: float = 0.0, umbral: float | None = None) -> dict:
    """Bootstrap de bloques de FECHAS sobre sumas por fecha: f(S) con S =
    sumas totales. Cada IC declara CUÁL es su nulo (0 para medias y
    pendientes, 1 para razones) y, si lo hay, el umbral de relevancia
    pre-registrado — «contiene el cero» en una razón ocultaba su nulo
    (dictamen C, bloqueo 4). Reporta las réplicas no finitas descartadas."""
    rng = np.random.default_rng(semilla)
    punto = float(f(M.sum(axis=0)))
    idx = _indices_bloques(rng, len(M), n_boot, bloque)
    reps = np.array([f(M[i].sum(axis=0)) for i in idx], float)
    finitas = reps[np.isfinite(reps)]
    lo, hi = np.quantile(finitas, [0.025, 0.975])
    out = {"punto": round(punto, 4), "ic95": [round(float(lo), 4), round(float(hi), 4)],
           "nulo": nulo, "contiene_nulo": bool(lo <= nulo <= hi),
           "contiene_cero": bool(lo <= 0 <= hi), "fechas": int(len(M)),
           "bloque": bloque, "replicas_no_finitas": int(n_boot - len(finitas))}
    if umbral is not None:
        out["umbral_relevancia"] = umbral
        out["ic_contiene_umbral"] = bool(lo <= umbral <= hi or lo <= -umbral <= hi)
        out["todo_el_ic_bajo_el_umbral"] = bool(max(abs(lo), abs(hi)) < abs(umbral))
    return out


def _boot_media(df: pd.DataFrame, col: str, escala: float = 1.0, **kw) -> dict:
    M = _sumas_por_fecha(df, [col])
    out = _boot(M, lambda S: escala * S[1] / S[0], **kw)
    out["filas"] = int(len(df))
    return out


def _boot_dif_medias(df: pd.DataFrame, a: str, b: str, escala: float = 1.0, **kw) -> dict:
    M = _sumas_por_fecha(df, [a, b])
    out = _boot(M, lambda S: escala * (S[1] - S[2]) / S[0], **kw)
    out["filas"] = int(len(df))
    return out


def _boot_pendiente(df: pd.DataFrame, x: str, y: str, **kw) -> dict:
    d = df.assign(xx=df[x] ** 2, xy=df[x] * df[y])
    M = _sumas_por_fecha(d, [x, y, "xx", "xy"])

    def pend(S):
        n, sx, sy, sxx, sxy = S
        vx = sxx / n - (sx / n) ** 2
        return (sxy / n - (sx / n) * (sy / n)) / vx if vx > 0 else float("nan")
    out = _boot(M, pend, **kw)
    out["filas"] = int(len(df))
    return out


def _boot_razon_h2(df: pd.DataFrame, **kw) -> dict:
    """|E[q|error]| / E[q|acierto], con las cuatro sumas por fecha."""
    d = df.assign(q_ac=df["q"] * df["acierto_gap"], n_ac=df["acierto_gap"],
                  q_er=df["q"] * (1 - df["acierto_gap"]), n_er=1 - df["acierto_gap"])
    M = _sumas_por_fecha(d, ["q_ac", "n_ac", "q_er", "n_er"])

    def razon(S):
        _, qa, na, qe, ne = S
        ma = qa / na if na > 0 else float("nan")
        me = qe / ne if ne > 0 else float("nan")
        return abs(me) / abs(ma) if ma not in (0.0,) and np.isfinite(ma) and np.isfinite(me) else float("nan")
    out = _boot(M, razon, nulo=1.0, umbral=1.5, **kw)
    out["filas"] = int(len(df))
    return out


def _boot_dif_condicional(df: pd.DataFrame, **kw) -> dict:
    """E[q|acierto] − E[q|error]: la diferencia que H2 pregunta, con su IC."""
    d = df.assign(q_ac=df["q"] * df["acierto_gap"], n_ac=df["acierto_gap"],
                  q_er=df["q"] * (1 - df["acierto_gap"]), n_er=1 - df["acierto_gap"])
    M = _sumas_por_fecha(d, ["q_ac", "n_ac", "q_er", "n_er"])
    out = _boot(M, lambda S: S[1] / S[2] - S[3] / S[4] if S[2] > 0 and S[4] > 0 else float("nan"), **kw)
    out["filas"] = int(len(df)); return out


def _boot_contribucion(df: pd.DataFrame, mask, **kw) -> dict:
    """Σ_{grupo} q / n_total: la contribución de un grupo al retorno medio."""
    d = df.assign(qg=df["q"] * mask.astype(float))
    M = _sumas_por_fecha(d, ["qg"])
    return _boot(M, lambda S: S[1] / S[0], **kw)


def _boot_dif_terciles(df: pd.DataFrame, cortes, **kw) -> dict:
    alto, bajo = (df["s"] > cortes[1]).astype(float), (df["s"] <= cortes[0]).astype(float)
    d = df.assign(ra=df["sesion_pct"] * alto, na=alto, rb=df["sesion_pct"] * bajo, nb=bajo)
    M = _sumas_por_fecha(d, ["ra", "na", "rb", "nb"])
    return _boot(M, lambda S: S[1] / S[2] - S[3] / S[4] if S[2] > 0 and S[4] > 0 else float("nan"), **kw)


def _mcnemar(df: pd.DataFrame, a: str, b: str) -> dict:
    """Comparación PAREADA modelo vs «siempre al alza» sobre las mismas filas:
    b, c y p (χ² con corrección de continuidad). Advertencia obligatoria: p y
    Wilson de filas son OPTIMISTAS por clustering de día."""
    from backtest import linea_base as lb
    x, y = df[a].to_numpy() > 0.5, df[b].to_numpy() > 0.5
    b01, b10 = int((x & ~y).sum()), int((~x & y).sum())
    n = len(df)
    lo, hi = lb._wilson(int(x.sum()), n)
    return {"n": n, "modelo_pct": round(100 * x.mean(), 2), "base_pct": round(100 * y.mean(), 2),
            "wilson_modelo_filas": [round(lo, 2), round(hi, 2)], "b": b01, "c": b10,
            "mcnemar_p": lb.mcnemar(b01, b10),
            "advertencia": "p y Wilson de FILAS: optimistas por clustering de día (unidad = fecha)"}


def _pendiente(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    vx = x.var()
    return float(((x - x.mean()) * (y - y.mean())).mean() / vx) if vx > 0 else float("nan")


def betas_ajuste(df: pd.DataFrame, hasta: str = AJUSTE[1]) -> dict:
    """β por ticker sobre el ajuste (OLS de gap sobre sox_prev). Invariante a
    truncar en cualquier fecha ≥ AJUSTE[1] (auditoría): para la PRUEBA es una
    β congelada; para el AJUSTE es in-sample y su H3 se rotula descriptiva."""
    sub = df[(df["fecha"] >= AJUSTE[0]) & (df["fecha"] <= hasta)]
    return {t: _pendiente(g["sox_prev"], g["gap_pct"]) for t, g in sub.groupby("ticker")}


def mitad_del_ajuste(df: pd.DataFrame) -> str:
    sub = df[(df["fecha"] >= AJUSTE[0]) & (df["fecha"] <= AJUSTE[1])]
    return sub["fecha"].quantile(0.5).strftime("%Y-%m-%d")


def analizar(df: pd.DataFrame, betas: dict, etiqueta: str, cortes=None, betas_alt: dict | None = None) -> dict:
    """`cortes`: los dos cortes de tercil de la sorpresa s. Si es None se
    calculan sobre `df` (sólo legítimo en el AJUSTE) y se devuelven en
    `cortes_tercil_s`; en la prueba se pasan CONGELADOS del ajuste."""
    d = df.copy()
    d["pred"] = np.sign(d["sox_prev"]).replace(0, 1.0)
    d["acierto_gap"] = (d["pred"] == np.sign(d["gap_pct"])).astype(float)
    d["acierto_sesion"] = (d["pred"] == np.sign(d["sesion_pct"])).astype(float)
    d["base_gap"] = (d["gap_pct"] > 0).astype(float)
    d["base_sesion"] = (d["sesion_pct"] > 0).astype(float)
    d["q"] = d["pred"] * d["sesion_pct"]                    # cartera direccional sobre la sesión
    d["q_gap"] = d["pred"] * d["gap_pct"]                   # lo que capturaría si el gap fuera operable
    d["s"] = d["gap_pct"] - d["ticker"].map(betas) * d["sox_prev"]   # sorpresa vs β·SOX
    d["s0"] = d["gap_pct"]                                  # sorpresa «sin modelo»
    out = {"etiqueta": etiqueta, "filas": int(len(d)), "fechas": int(d["fecha"].nunique())}
    # H1
    out["H1"] = {
        "ventaja_direccional_gap_pp": _boot_dif_medias(d, "acierto_gap", "base_gap", 100.0),
        "mcnemar_gap": _mcnemar(d, "acierto_gap", "base_gap"),
        "ventaja_direccional_sesion_pp": _boot_dif_medias(d, "acierto_sesion", "base_sesion", 100.0),
        "mcnemar_sesion": _mcnemar(d, "acierto_sesion", "base_sesion"),
        "retorno_medio_cartera_sesion_pp": _boot_media(d, "q"),
        "retorno_medio_si_el_gap_fuera_operable_pp": {**_boot_media(d, "q_gap"),
            "rotulo": "NO EJECUTABLE: exige comprar al cierre local ANTES de que exista el cierre de NY; "
                      "su Sharpe/DSR saturan y no son un aprobado"},
        "retorno_medio_siempre_largo_sesion_pp": _boot_media(d, "sesion_pct"),
        "fraccion_aciertos_gap": _boot_media(d, "acierto_gap")}
    # H2
    ac, er = d[d["acierto_gap"] == 1], d[d["acierto_gap"] == 0]
    qa, qe = _boot_media(ac, "q"), _boot_media(er, "q")
    out["H2"] = {
        "q_medio_dado_acierto_pp": qa,
        "q_medio_dado_error_pp": qe,
        "diferencia_acierto_menos_error_pp": _boot_dif_condicional(d),
        "contribucion_aciertos_pp_ic": _boot_contribucion(d, d["acierto_gap"] == 1),
        "contribucion_errores_pp_ic": _boot_contribucion(d, d["acierto_gap"] == 0),
        "veredicto": ("REFUTADA EN SU PREMISA: los aciertos pierden más que los errores (signo contrario al "
                      "postulado); la diferencia no se distingue de cero. El criterio original aplicado "
                      "literalmente habría dado un FALSO POSITIVO por aritmética de signos."
                      if qa["punto"] <= 0 and qa["punto"] <= qe["punto"] else "ver razón y diferencia"),
        "signo_q_acierto": "+" if qa["punto"] > 0 else "−",
        "signo_q_error": "+" if qe["punto"] > 0 else "−",
        # El criterio «|E[q|error]| ≥ 1,5 × E[q|acierto]» suponía E[q|acierto] > 0.
        # Si los aciertos también pierden, la razón no dice lo que el criterio lee.
        "razon_aplicable": bool(qa["punto"] > 0),
        "fraccion_aciertos": round(float(d["acierto_gap"].mean()), 4),
        "contribucion_aciertos_pp": round(float(ac["q"].sum() / len(d)), 4),
        "contribucion_errores_pp": round(float(er["q"].sum() / len(d)), 4),
        "razon_magnitud_error_sobre_acierto": _boot_razon_h2(d)}
    # H3
    out["H3"] = {
        "pendiente_sesion_sobre_sorpresa_beta": _boot_pendiente(d, "s", "sesion_pct", umbral=0.1),
        "beta_de_la_sorpresa": "in-sample (descriptiva)" if etiqueta == "ajuste" else "congelada del ajuste",
        "pendiente_sesion_sobre_gap": _boot_pendiente(d, "s0", "sesion_pct", umbral=0.1),
        "advertencia_pendiente_gap": ("sesión ≡ total − gap por identidad exacta (sin Open independiente): la pendiente "
                                      "sesión~gap es indistinguible de la atenuación −Var(ε)/Var(g) por error de medición "
                                      "del gap (testigos de dos añadas: gaps del 2-sep, cierres del 26-ago)"),
        "sesion_media_por_tercil_de_sorpresa_pp": {}}
    if betas_alt is not None:
        d["s_alt"] = d["gap_pct"] - d["ticker"].map(betas_alt) * d["sox_prev"]
        out["H3"]["pendiente_sesion_sobre_sorpresa_beta_primera_mitad"] = _boot_pendiente(d, "s_alt", "sesion_pct", umbral=0.1)
    if cortes is None:
        cortes = [float(x) for x in d["s"].quantile([1 / 3, 2 / 3]).to_numpy()]
    q = cortes
    out["cortes_tercil_s"] = [round(x, 4) for x in q]
    for nombre, mask in (("bajo", d["s"] <= q[0]), ("medio", (d["s"] > q[0]) & (d["s"] <= q[1])), ("alto", d["s"] > q[1])):
        out["H3"]["sesion_media_por_tercil_de_sorpresa_pp"][nombre] = _boot_media(d[mask], "sesion_pct")
    out["H3"]["diferencia_tercil_alto_menos_bajo_pp"] = _boot_dif_terciles(d, q)
    out["H3"]["veredicto"] = ("No se detecta relación de la sesión con la sorpresa respecto de β (IC contiene el cero). "
                              "Sobre el gap crudo la pendiente es negativa pero confundida con error de medición y su "
                              "irrelevancia (|pendiente| < 0,1) sólo se establece donde TODO el IC queda bajo 0,1.")
    # sensibilidad al bloque (la casa tiene 10 en DISEÑO.md §8.5 y 20 en .claude/rules/backtest.md)
    out["sensibilidad_bloque"] = {}
    for bl in (1, 5, 10, 20, 40, 60):
        out["sensibilidad_bloque"][str(bl)] = {
            "ventaja_sesion_pp": _boot_dif_medias(d, "acierto_sesion", "base_sesion", 100.0, bloque=bl)["ic95"],
            "q_medio_pp": _boot_media(d, "q", bloque=bl)["ic95"],
            "pendiente_sesion_gap": _boot_pendiente(d, "s0", "sesion_pct", bloque=bl)["ic95"],
            "pendiente_sesion_sorpresa": _boot_pendiente(d, "s", "sesion_pct", bloque=bl)["ic95"]}
    # costos: cartera direccional y su CONTRARIA (lo que H1 implica), en pb por lado
    out["costos"] = {}
    for pb in (0, 5, 10, 25):
        d["q_c"] = d["q"] - 2 * pb / 100.0
        d["q_contra"] = -d["q"] - 2 * pb / 100.0
        out["costos"][f"{pb}pb_por_lado"] = {"direccional_pp_dia": _boot_media(d, "q_c", bloque=20),
                                             "contraria_pp_dia": _boot_media(d, "q_contra", bloque=20)}
    eq = float(d["q"].mean())
    out["costos"]["punto_muerto_contraria_pb_por_lado"] = round(-eq * 100 / 2, 2)
    # DSR de la contraria: retornos diarios = media de q por fecha, Sharpe por período, V teórica 1/T
    from backtest import inferencia as inf
    from GEMELO.relevo_asiatico import N_INTENTOS_ACUMULADO
    diario = (-d.groupby("fecha")["q"].mean()).to_numpy() / 100.0
    sr_p = inf.sharpe(diario, anualizar=1)
    T = len(diario)
    out["costos"]["contraria_sharpe_por_periodo"] = round(sr_p, 4)
    out["costos"]["contraria_dsr"] = {str(N): round(inf.dsr(sr_p, T, 0.0, 3.0, N, 1.0 / T), 3)
                                      for N in (14, 29, N_INTENTOS_ACUMULADO, N_INTENTOS_ACUMULADO + 60)}
    out["costos"]["nota"] = "V = 1/T (teórica); N incluye el registro de la máquina; 25 pb por lado = la vara de la casa"
    # robustez (bloque 20): dejar-un-año-fuera, dejar-un-ticker-fuera, winsorizado 0,5%, por ticker
    out["robustez"] = {"sin_anio": {}, "sin_ticker": {}, "por_ticker": {}}
    for anio, g in d.groupby(d["fecha"].dt.year):
        resto = d[d["fecha"].dt.year != anio]
        if len(resto) and d["fecha"].dt.year.nunique() > 1:
            out["robustez"]["sin_anio"][str(anio)] = {"q_medio_pp": _boot_media(resto, "q", bloque=20)["ic95"],
                                                    "ventaja_gap_pp": _boot_dif_medias(resto, "acierto_gap", "base_gap", 100.0, bloque=20)["ic95"]}
    for t in sorted(d["ticker"].unique()):
        out["robustez"]["sin_ticker"][t] = _boot_media(d[d["ticker"] != t], "q", bloque=20)["ic95"]
        out["robustez"]["por_ticker"][t] = _boot_media(d[d["ticker"] == t], "q", bloque=20)
    lo_w, hi_w = d["q"].quantile([0.005, 0.995])
    out["robustez"]["winsorizado_0_5pct_q_medio_pp"] = _boot_media(d.assign(q=d["q"].clip(lo_w, hi_w)), "q", bloque=20)
    # Fráncfort no es contemporáneo de Asia: su ventana de gap sólo contiene la
    # cola de la sesión de NY. H1 y H3 también por exchange.
    out["por_exchange"] = {}
    for ex, g in d.groupby("exchange"):
        out["por_exchange"][ex] = {
            "filas": int(len(g)), "tickers": sorted(g["ticker"].unique().tolist()),
            "ventaja_direccional_gap_pp": _boot_dif_medias(g, "acierto_gap", "base_gap", 100.0),
            "ventaja_direccional_sesion_pp": _boot_dif_medias(g, "acierto_sesion", "base_sesion", 100.0),
            "retorno_medio_cartera_sesion_pp": _boot_media(g, "q"),
            "pendiente_sesion_sobre_sorpresa_beta": _boot_pendiente(g, "s", "sesion_pct")}
    return out


def _sha(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _hash_apertura() -> str:
    h = hashlib.sha256()
    for ruta in (os.path.abspath(__file__), RUTA_PREREGISTRO):
        with open(ruta, "rb") as f:
            h.update(f.read())
    return h.hexdigest()


def _hash_datos() -> dict:
    """El candado protege también los DATOS (dictamen C, exigido 12): un
    testigo re-descargado con el mismo nombre reabriría la prueba en silencio."""
    return {os.path.relpath(r, _RAIZ): _sha(r) for r in (RUTA_GAPS_GZ, RUTA_CIERRES_GZ, RUTA_SOX_GZ)}


def candado_de_apertura(enmienda: str | None = None) -> dict:
    """La prueba se abre UNA vez. El candado guarda el sha256 del módulo, del
    pre-registro y de los tres testigos. Si cambió cualquiera, no se reabre
    en silencio: sólo con `enmienda="razón"`, que deja RASTRO en el candado
    (hash anterior, hash nuevo, instante, razón). Una enmienda no es una
    reapertura limpia: cada estadístico nuevo que agregue cuenta como intento."""
    actual, datos = _hash_apertura(), _hash_datos()
    ahora = datetime.now(timezone.utc).isoformat()
    if os.path.exists(RUTA_LOCK):
        with open(RUTA_LOCK) as f:
            previo = json.load(f)
        cambio = previo.get("sha256") != actual or previo.get("datos") not in (None, datos)
        if not cambio:
            return previo
        if not enmienda:
            raise RuntimeError(
                f"la prueba del Frente C ya fue abierta el {previo.get('abierta_en_utc')} con otro "
                f"módulo/pre-registro/datos (sha256 {previo.get('sha256', '')[:12]}… ≠ {actual[:12]}…): no se reabre "
                "en silencio. Con --enmienda \"razón\" queda rastro y cada estadístico nuevo es un intento.")
        previo.setdefault("enmiendas", []).append({"en_utc": ahora, "sha256_anterior": previo["sha256"],
                                                   "sha256_nuevo": actual, "razon": enmienda})
        previo["sha256"], previo["datos"] = actual, datos
        with open(RUTA_LOCK, "w") as f:
            json.dump(previo, f, indent=1, ensure_ascii=False)
        return previo
    lock = {"sha256": actual, "datos": datos, "abierta_en_utc": ahora,
            "archivos": [os.path.relpath(os.path.abspath(__file__), _RAIZ), os.path.relpath(RUTA_PREREGISTRO, _RAIZ)]}
    with open(RUTA_LOCK, "w") as f:
        json.dump(lock, f, indent=1)
    return lock


def contar_intervalos(o) -> int:
    """Intentos del DSR = intervalos publicados en el artefacto (la casa yerra
    hacia arriba). El 14 declarado a mano era la mitad del conteo real."""
    if isinstance(o, dict):
        return 1 if ("ic95" in o and "punto" in o) else sum(contar_intervalos(v) for v in o.values())
    if isinstance(o, list):
        return sum(contar_intervalos(v) for v in o)
    return 0


def ventana_prueba(df: pd.DataFrame) -> pd.DataFrame:
    """Prueba = desde PRUEBA[0] + embargo hasta min(PRUEBA[1], primera sesión
    sellada − embargo), y fuera de [sellada − embargo, sellada + embargo]:
    la misma barra del `^SOX` no puede alimentar una fila de prueba y una
    sellada (auditoría, 2-sep)."""
    bd = pd.tseries.offsets.BDay(EMBARGO_SESIONES)
    desde = pd.Timestamp(PRUEBA[0]) + bd
    s_ini, s_fin = pd.Timestamp(SELLADA[0]) - bd, pd.Timestamp(SELLADA[1]) + bd
    hasta = min(pd.Timestamp(PRUEBA[1]), s_ini - pd.Timedelta(days=1))
    out = df[(df["fecha"] >= desde) & (df["fecha"] <= hasta) & ~((df["fecha"] >= s_ini) & (df["fecha"] <= s_fin))]
    assert ((out["fecha"] >= SELLADA[0]) & (out["fecha"] <= SELLADA[1])).sum() == 0, "la prueba toca la ventana sellada"
    return out


def main(abrir_prueba: bool = False, enmienda: str | None = None) -> dict:
    df = cargar()
    betas = betas_ajuste(df)
    mitad = mitad_del_ajuste(df)
    betas_mitad = betas_ajuste(df, hasta=mitad)
    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "etiqueta": "PROPUESTA — Frente C, octava corrida; pendiente de dictamen",
           "parametros": {"n_boot": N_BOOT, "bloque_fechas": BLOQUE_FECHAS, "semilla": SEMILLA, "ajuste": AJUSTE,
                          "prueba": PRUEBA, "ultima_barra_completa": ULTIMA_BARRA_COMPLETA,
                          "captura_cierres_utc": CAPTURA_CIERRES_UTC,
                          "embargo": EMBARGO_SESIONES, "sellada_excluida": SELLADA,
                          "sellada_derivada_de": os.path.relpath(RUTA_BACKUP_SENALES, _RAIZ),
                          "prueba_abierta": abrir_prueba,
                          "betas_ajuste": {k: round(v, 4) for k, v in betas.items()},
                          "mitad_del_ajuste": mitad,
                          "betas_primera_mitad": {k: round(v, 4) for k, v in betas_mitad.items()},
                          "fuentes": [os.path.relpath(x, _RAIZ) for x in (RUTA_GAPS_GZ, RUTA_CIERRES_GZ, RUTA_SOX_GZ)]}}
    aj = df[(df["fecha"] >= AJUSTE[0]) & (df["fecha"] <= AJUSTE[1])]
    res["ajuste"] = analizar(aj, betas, "ajuste", betas_alt=betas_mitad)
    res["parametros"]["cortes_tercil_s_congelados_en_ajuste"] = res["ajuste"]["cortes_tercil_s"]
    if abrir_prueba:
        res["parametros"]["candado"] = candado_de_apertura(enmienda)
        pr_ = ventana_prueba(df)
        res["parametros"]["prueba_efectiva"] = [pr_["fecha"].min().strftime("%Y-%m-%d"), pr_["fecha"].max().strftime("%Y-%m-%d")]
        res["prueba"] = analizar(pr_, betas, "prueba", cortes=res["ajuste"]["cortes_tercil_s"])
    # colisión de procedencia con la cifra canónica de disipación (README: XETR +2,5 pp, p 0,111
    # con el MODELO 4.6.0 reconstruido sobre n = 14.618): acá el predictor es el signo crudo
    # del SOX y la población es otra. Se declara donde se lee.
    todo = df.assign(pred=np.sign(df["sox_prev"]).replace(0, 1.0))
    todo["acierto_gap"] = (todo["pred"] == np.sign(todo["gap_pct"])).astype(float)
    todo["base_gap"] = (todo["gap_pct"] > 0).astype(float)
    res["colision_procedencia"] = {
        "nota": "signo crudo del SOX sobre toda la ventana reconstruida (incluye fechas selladas, reconstruidas desde testigos, no desde senales.db) — NO es la cifra canónica del README (modelo 4.6.0, n = 14.618)",
        "ventana": [todo["fecha"].min().strftime("%Y-%m-%d"), todo["fecha"].max().strftime("%Y-%m-%d")], "filas": int(len(todo)),
        "por_exchange": {ex: {**_boot_dif_medias(g, "acierto_gap", "base_gap", 100.0, bloque=20), **_mcnemar(g, "acierto_gap", "base_gap")}
                         for ex, g in todo.groupby("exchange")}}
    res["intentos_dsr"] = {"intervalos_publicados_ajuste": contar_intervalos(res.get("ajuste", {})),
                           "intervalos_publicados_prueba": contar_intervalos(res.get("prueba", {})),
                           "intervalos_publicados_total": contar_intervalos(res),
                           "regla": "un intento por intervalo publicado (la casa yerra hacia arriba); el 14 declarado a mano queda retirado"}
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "no_capturabilidad.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "no_capturabilidad.md"), "w") as f:
        f.write(informe(res))
    return res


def _v(x):
    """Imprime el IC con SU nulo (0, 1…) y, si lo hay, el umbral pre-registrado."""
    nulo = x.get("nulo", 0.0)
    s = f"{x['punto']} {x['ic95']}"
    if x.get("contiene_nulo", x.get("contiene_cero")):
        s += f" (contiene el {'cero' if nulo == 0 else 'nulo ' + str(nulo)})"
    if "umbral_relevancia" in x:
        u = x["umbral_relevancia"]
        s += f"; IC {'contiene' if x['ic_contiene_umbral'] else 'no contiene'} ±{u}" + \
             (", todo el IC bajo el umbral" if x["todo_el_ic_bajo_el_umbral"] else "")
    return s


def _mc(m):
    return f"modelo {m['modelo_pct']}% (Wilson filas {m['wilson_modelo_filas']}) vs base {m['base_pct']}%, b = {m['b']}, c = {m['c']}, McNemar p = {m['mcnemar_p']} — {m['advertencia']}"


def informe(r: dict) -> str:
    L = ["# La no capturabilidad como hipótesis — Frente C (PROPUESTA)\n",
         f"> **{r['etiqueta']}** · generado {r['generado_en_utc']} · `python GEMELO/no_capturabilidad.py`"
         f"{' --abrir-prueba' if r['parametros']['prueba_abierta'] else ''}\n",
         "Pre-registro: `GEMELO/preregistro/frente_C.md`. Sin motor: predicción = signo del último cierre de NY anterior a la apertura local. "
         f"Sesión = close/open − 1. Cartera direccional q = signo(pred)·sesión, sin costos. IC por bootstrap de bloques circulares de {r['parametros']['bloque_fechas']} fechas. "
         f"Datos hasta la última barra completa ({r['parametros']['ultima_barra_completa']}); ventana sellada {r['parametros']['sellada_excluida']} derivada del backup y embargada en sus dos bordes.\n"]
    for ven in ("ajuste", "prueba"):
        if ven not in r:
            L.append(f"## Años de {ven.upper()}: no abiertos todavía\n"); continue
        a = r[ven]
        L += [f"## Años de {ven.upper()}: {a['filas']} filas, {a['fechas']} fechas\n",
              "### H1 · estructural: el gap se acierta, la sesión no se captura\n",
              "| cantidad | punto | IC95 (fechas) |", "|---|---|---|"]
        for k, v in a["H1"].items():
            if "punto" in v:
                L.append(f"| {k} | {v['punto']} | {v['ic95']}{' (contiene el cero)' if v['contiene_cero'] else ''}{' — **' + v['rotulo'] + '**' if 'rotulo' in v else ''} |")
        L += ["", f"- McNemar gap: {_mc(a['H1']['mcnemar_gap'])}", f"- McNemar sesión: {_mc(a['H1']['mcnemar_sesion'])}"]
        h2 = a["H2"]
        L += ["\n### H2 · asimetría de magnitud\n",
              f"- Fracción de aciertos del gap: {_v(a['H1']['fraccion_aciertos_gap'])}; contribución al retorno medio de la cartera: aciertos {_v(h2['contribucion_aciertos_pp_ic'])} pp, errores {_v(h2['contribucion_errores_pp_ic'])} pp.",
              f"- Diferencia E[q|acierto] − E[q|error]: {_v(h2['diferencia_acierto_menos_error_pp'])} pp.",
              f"- **Veredicto H2:** {h2['veredicto']}",
              f"- q medio dado acierto: {_v(h2['q_medio_dado_acierto_pp'])}; dado error: {_v(h2['q_medio_dado_error_pp'])}.",
              f"- Signos: q|acierto {h2['signo_q_acierto']}, q|error {h2['signo_q_error']}. Razón |E[q|error]| / |E[q|acierto]| (nulo 1, umbral 1,5): "
              f"{_v(h2['razon_magnitud_error_sobre_acierto'])} — el criterio «≥ 1,5» "
              f"{'aplica' if h2['razon_aplicable'] else 'aplicado literalmente daría un FALSO POSITIVO (E[q|acierto] ≤ 0 vuelve trivial la desigualdad)'}.",
              "\n### H3 · sobrerreacción (pendiente < 0) o deriva (> 0) de la sesión sobre la sorpresa\n",
              f"- Pendiente sesión ~ sorpresa (gap − β·SOX; β {a['H3']['beta_de_la_sorpresa']}): {_v(a['H3']['pendiente_sesion_sobre_sorpresa_beta'])}"
              + (f"; con β de la primera mitad del ajuste: {_v(a['H3']['pendiente_sesion_sobre_sorpresa_beta_primera_mitad'])}" if 'pendiente_sesion_sobre_sorpresa_beta_primera_mitad' in a['H3'] else ""),
              f"- Cortes de tercil de s: {a['cortes_tercil_s']} ({'calculados aquí' if ven == 'ajuste' else 'CONGELADOS del ajuste'})",
              f"- Pendiente sesión ~ gap: {_v(a['H3']['pendiente_sesion_sobre_gap'])}",
              "- Sesión media por tercil de sorpresa: " + "; ".join(f"{k} {_v(v)}" for k, v in a["H3"]["sesion_media_por_tercil_de_sorpresa_pp"].items())
              + f"; diferencia alto − bajo: {_v(a['H3']['diferencia_tercil_alto_menos_bajo_pp'])}",
              f"- {a['H3']['advertencia_pendiente_gap']}.",
              f"- **Veredicto H3:** {a['H3']['veredicto']}", "",
              "### Sensibilidad al bloque del bootstrap (IC95 por bloque de 1/5/10/20/40/60 fechas)\n",
              "| bloque | ventaja sesión (pp) | q medio (pp) | pendiente sesión~gap | pendiente sesión~sorpresa |", "|---|---|---|---|---|"]
        for bl, v in a["sensibilidad_bloque"].items():
            L.append(f"| {bl} | {v['ventaja_sesion_pp']} | {v['q_medio_pp']} | {v['pendiente_sesion_gap']} | {v['pendiente_sesion_sorpresa']} |")
        co = a["costos"]
        L += ["", "### Costos: la cartera direccional y su CONTRARIA (lo que H1 implica), bloque 20\n",
              "| pb por lado | direccional (pp/día) | contraria (pp/día) |", "|---|---|---|"]
        for pb in ("0pb_por_lado", "5pb_por_lado", "10pb_por_lado", "25pb_por_lado"):
            L.append(f"| {pb.split('pb')[0]} | {_v(co[pb]['direccional_pp_dia'])} | {_v(co[pb]['contraria_pp_dia'])} |")
        L += [f"\nPunto muerto de la contraria: **{co['punto_muerto_contraria_pb_por_lado']} pb por lado**; Sharpe por período de la contraria "
              f"{co['contraria_sharpe_por_periodo']}; DSR por N: {co['contraria_dsr']} ({co['nota']}). "
              "La contraria muere por costos y por multiplicidad: es la mitad que cierra el argumento de no capturabilidad.", "",
              "### Robustez (bloque 20)\n",
              "- q medio dejando un año fuera: " + "; ".join(f"sin {k}: {v['q_medio_pp']}" for k, v in a["robustez"]["sin_anio"].items()),
              "- q medio dejando un ticker fuera: " + "; ".join(f"sin {k}: {v}" for k, v in a["robustez"]["sin_ticker"].items()),
              "- q medio por ticker (heterogéneo: sólo los que excluyen el cero pierden por sí solos): " + "; ".join(f"{k} {_v(v)}" for k, v in a["robustez"]["por_ticker"].items()),
              f"- q medio winsorizado al 0,5%: {_v(a['robustez']['winsorizado_0_5pct_q_medio_pp'])}", "",
              "### Por exchange (Fráncfort no es contemporáneo de Asia)\n",
              "| exchange | filas | ventaja gap (pp) | ventaja sesión (pp) | q medio (pp) | pendiente sesión~sorpresa |", "|---|---|---|---|---|---|"]
        for ex, v in a["por_exchange"].items():
            L.append(f"| {ex} | {v['filas']} | {_v(v['ventaja_direccional_gap_pp'])} | {_v(v['ventaja_direccional_sesion_pp'])} | "
                     f"{_v(v['retorno_medio_cartera_sesion_pp'])} | {_v(v['pendiente_sesion_sobre_sorpresa_beta'])} |")
        L.append("")
    cp = r.get("colision_procedencia")
    if cp:
        L += ["## Colisión de procedencia con la cifra canónica de disipación\n", cp["nota"] + f" — ventana {cp['ventana']}, {cp['filas']} filas.", "",
              "| exchange | ventaja gap signo-SOX (pp) | McNemar |", "|---|---|---|"]
        for ex, v in cp["por_exchange"].items():
            L.append(f"| {ex} | {_v(v)} | b = {v['b']}, c = {v['c']}, p = {v['mcnemar_p']} |")
        L += ["", "El README publica Fráncfort **+2,5 pp, p = 0,111** con el MODELO 4.6.0 reconstruido (n = 14.618): otra población y otro predictor. No es contradicción; es procedencia distinta, y se dice acá para que la portada no quede inconsistente.", ""]
    it = r.get("intentos_dsr")
    if it:
        L += [f"## Intentos del DSR\n", f"Intervalos publicados: ajuste {it['intervalos_publicados_ajuste']}, prueba {it['intervalos_publicados_prueba']}, total **{it['intervalos_publicados_total']}**. {it['regla']}.", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    enm = None
    if "--enmienda" in sys.argv:
        enm = sys.argv[sys.argv.index("--enmienda") + 1]
    r = main(abrir_prueba="--abrir-prueba" in sys.argv, enmienda=enm)
    print(json.dumps({"H1": r["ajuste"]["H1"], "H2": {k: v for k, v in r["ajuste"]["H2"].items()}, "H3": {k: v for k, v in r["ajuste"]["H3"].items() if k != "sesion_media_por_tercil_de_sorpresa_pp"}}, indent=1, default=str))
