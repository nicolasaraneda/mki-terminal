"""Frente B1 de la octava corrida: el experimento natural de los feriados.

Pre-registro: `GEMELO/preregistro/frente_B.md` (H_dis vs H_abs; condiciones
C1/C2/C3; estadístico; efecto relevante; partición). Retornos crudos, sin
motor: el «insumo» es el último cierre de NY estrictamente anterior a la
apertura local (`merge_asof` hacia atrás, excluyente), y la predicción
direccional es su signo.

Condiciones por sesión local d de un exchange X (calendarios de
`exchange_calendars`, no huecos de la fuente):
  n_ny  = sesiones de NY que cerraron entre la sesión local anterior y la
          apertura de d. 1 = normal; 0 = NY estuvo cerrada (C1: el cierre
          disponible es viejo); ≥2 = X estuvo cerrada mientras NY operó
          (feriado local: el gap agrega dos movimientos de NY).
  asia_abierta = cuántas de {XTKS, XKRX, XTAI} operaron en d ANTES de la
          apertura de X (sólo tiene sentido para XETR): 3 = normal; 2 = un
          intermediario menos (C2 si el que falta es Tokio, C3 si es Seúl o
          Taipéi); ≤1 = casi sin intermediarios.

Uso: `python GEMELO/decaimiento_feriados.py [--abrir-prueba]` →
`GEMELO/resultados/decaimiento_feriados.{json,md}`.
"""
from __future__ import annotations

import gzip
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

import exchange_calendars as xc                              # noqa: E402
from universo import EXCHANGE_POR_TICKER                     # noqa: E402

DIR_RESULTADOS = os.path.join(_AQUI, "resultados")
RUTA_GAPS_GZ = os.path.join(DIR_RESULTADOS, "testigos_fuente", "gaps_v2_propio_indice.csv.gz")
RUTA_SOX_GZ = os.path.join(DIR_RESULTADOS, "testigos_fuente", "cierres_353cacd57dc25f6a.csv.gz")
SEMILLA = 20260902
N_BOOT = 4000
N_PERM = 4000
BLOQUE_FECHAS = 20            # el bootstrap de bloques de la casa, publicado junto al iid de fechas
AJUSTE = ("2018-09-01", "2023-12-31")
PRUEBA = ("2024-01-01", "2026-08-31")
RELEVANTE_PP = 5.0
ASIA = ("XTKS", "XKRX", "XTAI")
EMBARGO_SESIONES = 5
RUTA_BACKUP_SENALES = os.path.join(_RAIZ, "data", "backups", "senales_senales_ticker.csv")
RUTA_PREREGISTRO = os.path.join(_AQUI, "preregistro", "frente_B.md")
RUTA_LOCK = os.path.join(DIR_RESULTADOS, "decaimiento_feriados.lock")


def sellada_desde_backup() -> tuple:
    """Ventana sellada derivada de `sesion_objetivo` del backup versionado
    (dictamen B, B-1: el entregable decía «sin las 37 selladas, con embargo»
    y el código no hacía ni lo uno ni lo otro)."""
    b = pd.read_csv(RUTA_BACKUP_SENALES, usecols=["sesion_objetivo"])
    so = pd.to_datetime(b["sesion_objetivo"]).dropna()
    return (so.min().strftime("%Y-%m-%d"), so.max().strftime("%Y-%m-%d"))


SELLADA = sellada_desde_backup()


def _sesiones(exch: str, desde: str, hasta: str) -> pd.DatetimeIndex:
    return xc.get_calendar(exch).sessions_in_range(desde, hasta)


def cargar() -> pd.DataFrame:
    with gzip.open(RUTA_GAPS_GZ, "rt") as f:
        gaps = pd.read_csv(f)
    gaps["fecha"] = pd.to_datetime(gaps["sesion"])
    gaps["exchange"] = gaps["ticker"].map(EXCHANGE_POR_TICKER)
    with gzip.open(RUTA_SOX_GZ, "rt") as f:
        sox = pd.read_csv(f, index_col=0, parse_dates=True)["^SOX"].dropna()
    ret = (sox.pct_change().dropna() * 100).rename("sox_prev")
    r = pd.DataFrame({"fecha_sox": ret.index, "sox_prev": ret.to_numpy()}).sort_values("fecha_sox")
    g = gaps.sort_values("fecha")
    m = pd.merge_asof(g, r, left_on="fecha", right_on="fecha_sox", direction="backward",
                      allow_exact_matches=False).dropna(subset=["sox_prev"])
    # el SOX de la sesión de NY anterior a la del insumo (para el agregado
    # de dos movimientos en feriados locales)
    r2 = r.copy(); r2["sox_prev2"] = r2["sox_prev"].shift(1)
    m = m.merge(r2[["fecha_sox", "sox_prev2"]], on="fecha_sox", how="left")
    # Regla (enmienda 2, auditoría): el insumo apareado tiene que ser la
    # ÚLTIMA sesión de NY del calendario anterior a la fecha local. Si la
    # serie del ^SOX no tiene esa barra (el 28-ago retirado, el fin de la
    # caché), la fila se EXCLUYE y se cuenta, en vez de entrar al cubo
    # «normal» con un insumo más viejo que su etiqueta.
    ny = _sesiones("XNYS", "2018-01-01", "2026-12-31")
    prev_ny = pd.Series(ny, index=ny).reindex(pd.DatetimeIndex(m["fecha"].unique()), method=None)
    ultima_ny_antes = {d: ny[ny < d][-1] for d in m["fecha"].unique()}
    m["ny_esperada"] = m["fecha"].map(ultima_ny_antes)
    m["insumo_rancio"] = m["fecha_sox"] != m["ny_esperada"]
    return m[["fecha", "ticker", "exchange", "gap_pct", "fecha_sox", "sox_prev", "sox_prev2", "insumo_rancio"]]


def condiciones(df: pd.DataFrame) -> pd.DataFrame:
    """n_ny por (exchange, fecha) y asia_abierta para XETR, desde los calendarios."""
    desde, hasta = df["fecha"].min().strftime("%Y-%m-%d"), df["fecha"].max().strftime("%Y-%m-%d")
    ny = _sesiones("XNYS", "2018-01-01", "2026-12-31")
    cal = {e: _sesiones(e, "2018-01-01", "2026-12-31") for e in set(df["exchange"]) | set(ASIA)}
    out = []
    for e in sorted(set(df["exchange"])):
        s = cal[e]
        prev = pd.Series(s[:-1], index=s[1:])            # sesión local anterior
        for d in s[(s >= desde) & (s <= hasta)]:
            if d not in prev.index:
                continue
            p = prev[d]
            # sesiones de NY con cierre entre la sesión local anterior y la
            # apertura de d: para Asia (abre 00:00Z) son las de fecha ≥ p y
            # < d; para XETR (abre 07:00Z) igual — el cierre de NY de d es
            # posterior a la apertura de XETR (21:00Z)
            n_ny = int(((ny >= p) & (ny < d)).sum())
            asia = int(sum(d in cal[a] for a in ASIA)) if e == "XETR" else None
            tk, ks, tw = (d in cal["XTKS"]), (d in cal["XKRX"]), (d in cal["XTAI"])
            out.append({"exchange": e, "fecha": d, "n_ny": n_ny, "asia_abierta": asia,
                        # C2: SÓLO Tokio cerrada (Seúl y Taipéi abiertos), como el pre-registro
                        "sin_tokio": (e == "XETR" and (not tk) and ks and tw),
                        # C3: exactamente uno de Seúl/Taipéi cerrado, Tokio abierta — disjunto de C2
                        "sin_seul_o_taipei": (e == "XETR" and tk and (ks != tw)),
                        "lunes": bool(d.weekday() == 0)})
    return pd.DataFrame(out)


def _por_fecha(d: pd.DataFrame, col_sox: str) -> np.ndarray:
    """Por fecha: (n, aciertos del signo, aciertos de «siempre al alza»), con
    `excluir_cero`. Todo lo demás se hace sobre esta matriz (vectorizado)."""
    d = d[d["gap_pct"] != 0]
    hit = ((d[col_sox] >= 0) == (d["gap_pct"] > 0)).astype(float)
    base = (d["gap_pct"] > 0).astype(float)
    t = pd.DataFrame({"fecha": d["fecha"].to_numpy(), "n": 1.0, "hit": hit.to_numpy(), "base": base.to_numpy()})
    return t.groupby("fecha")[["n", "hit", "base"]].sum().to_numpy()


def _ventaja(m: np.ndarray) -> float:
    n = m[:, 0].sum()
    return float((m[:, 1].sum() - m[:, 2].sum()) / n) if n > 0 else float("nan")


def ventaja(d: pd.DataFrame, col_sox: str = "sox_prev") -> float:
    m = _por_fecha(d, col_sox)
    return _ventaja(m) if len(m) else float("nan")


def contraste(df: pd.DataFrame, mascara_cond, mascara_norm, col_sox="sox_prev",
              semilla=SEMILLA) -> dict:
    """Δ(condición) − Δ(normal) con IC por bootstrap de FECHAS (vectorizado
    sobre las sumas por fecha) y p por permutación de la etiqueta de
    condición entre fechas."""
    a, b = df[mascara_cond], df[mascara_norm]
    ma, mb = _por_fecha(a, col_sox), _por_fecha(b, col_sox)
    if len(ma) < 5 or len(mb) < 5:
        return {"fechas_cond": int(len(ma)), "fechas_norm": int(len(mb)),
                "nota": "menos de 5 fechas en una condición: no se estima"}
    rng = np.random.default_rng(semilla)
    dif = _ventaja(ma) - _ventaja(mb)

    def _v(M, idx):
        S = M[idx].sum(axis=1)                      # (n_rep, 3)
        return (S[:, 1] - S[:, 2]) / S[:, 0]

    ia = rng.integers(0, len(ma), size=(N_BOOT, len(ma)))
    ib = rng.integers(0, len(mb), size=(N_BOOT, len(mb)))
    reps = _v(ma, ia) - _v(mb, ib)
    lo, hi = np.quantile(reps, [0.025, 0.975])
    # bloques circulares de fechas (la regla de la casa), publicado junto al iid
    ia2 = _indices_bloques(rng, len(ma), N_BOOT, BLOQUE_FECHAS)
    ib2 = _indices_bloques(rng, len(mb), N_BOOT, BLOQUE_FECHAS)
    reps2 = _v(ma, ia2) - _v(mb, ib2)
    lo2, hi2 = np.quantile(reps2, [0.025, 0.975])
    todo = np.vstack([ma, mb]); k = len(ma)
    nulos = np.empty(N_PERM)
    for i in range(N_PERM):
        perm = rng.permutation(len(todo))
        nulos[i] = _ventaja(todo[perm[:k]]) - _ventaja(todo[perm[k:]])
    p = float((1 + (np.abs(nulos) >= abs(dif) - 1e-12).sum()) / (N_PERM + 1))
    return {"fechas_cond": int(len(ma)), "filas_cond": int(ma[:, 0].sum()), "fechas_norm": int(len(mb)),
            "ventaja_cond_pp": round(100 * _ventaja(ma), 2), "ventaja_norm_pp": round(100 * _ventaja(mb), 2),
            "diferencia_pp": round(100 * dif, 2), "ic95_pp": [round(float(100 * lo), 2), round(float(100 * hi), 2)],
            "ic95_bloques20_pp": [round(float(100 * lo2), 2), round(float(100 * hi2), 2)],
            "contiene_cero_bloques20": bool(lo2 <= 0 <= hi2),
            "p_permutacion": round(p, 4), "contiene_cero": bool(lo <= 0 <= hi),
            "excluye_5pp": bool(hi < RELEVANTE_PP / 100), "supera_5pp": bool(lo > RELEVANTE_PP / 100),
            "contiene_5pp": bool(lo <= RELEVANTE_PP / 100 <= hi) or bool(lo <= -RELEVANTE_PP / 100 <= hi)}


def _indices_bloques(rng, n: int, n_boot: int, bloque: int) -> np.ndarray:
    if bloque <= 1 or n <= bloque:
        return rng.integers(0, n, size=(n_boot, n))
    nb = -(-n // bloque)
    arr = rng.integers(0, n, size=(n_boot, nb))
    idx = (arr[:, :, None] + np.arange(bloque)[None, None, :]) % n
    return idx.reshape(n_boot, nb * bloque)[:, :n]


def contraste_estandarizado(df: pd.DataFrame, mascara_cond, mascara_norm, col_sox="sox_prev",
                            n_estratos: int = 4, semilla=SEMILLA) -> dict:
    """Control de |SOX| BIEN especificado (dictamen B, B-3): estandarización
    directa por estratos de |SOX| —cortes = cuartiles del grupo normal—:
    Δ_cond,std = Σ_s w_s·Δ_cond,s con w_s = proporción de fechas normales en
    el estrato s; diferencia = Δ_cond,std − Δ_norm. IC por bootstrap de
    fechas dentro de cada (grupo, estrato). También el truncado SIMÉTRICO
    (los dos grupos a |SOX| ≤ p75 de la condición). La versión anterior
    truncaba sólo el grupo normal: invertía el desbalance."""
    a, b = df[mascara_cond].copy(), df[mascara_norm].copy()
    if a["fecha"].nunique() < 8 or b["fecha"].nunique() < 8:
        return {"nota": "menos de 8 fechas: no se estandariza"}
    cortes = b.groupby("fecha")[col_sox].first().abs().quantile([0.25, 0.5, 0.75]).to_numpy()
    def estrato(d):
        s = d.groupby("fecha")[col_sox].first().abs()
        return pd.Series(np.searchsorted(cortes, s.to_numpy()), index=s.index)
    ea, eb = estrato(a), estrato(b)
    Ma = {k: _por_fecha(a[a["fecha"].isin(ea.index[ea == k])], col_sox) for k in range(n_estratos)}
    Mb = {k: _por_fecha(b[b["fecha"].isin(eb.index[eb == k])], col_sox) for k in range(n_estratos)}
    w = np.array([len(Mb[k]) for k in range(n_estratos)], float); w /= w.sum()
    def dif(Ma_, Mb_):
        va = sum(w[k] * _ventaja(Ma_[k]) for k in range(n_estratos) if len(Ma_[k]))
        vb = _ventaja(np.vstack([Mb_[k] for k in range(n_estratos) if len(Mb_[k])]))
        return va - vb
    punto = dif(Ma, Mb)
    rng = np.random.default_rng(semilla + 1)
    reps = []
    for _ in range(1000):
        Ra = {k: (Ma[k][rng.integers(0, len(Ma[k]), len(Ma[k]))] if len(Ma[k]) else Ma[k]) for k in Ma}
        Rb = {k: (Mb[k][rng.integers(0, len(Mb[k]), len(Mb[k]))] if len(Mb[k]) else Mb[k]) for k in Mb}
        reps.append(dif(Ra, Rb))
    lo, hi = np.quantile(reps, [0.025, 0.975])
    # truncado simétrico
    tope = a.groupby("fecha")[col_sox].first().abs().quantile(0.75)
    sim = contraste(df, mascara_cond & (df[col_sox].abs() <= tope), mascara_norm & (df[col_sox].abs() <= tope), col_sox, semilla + 2)
    return {"estandarizado_por_estratos": {"diferencia_pp": round(100 * punto, 2), "ic95_pp": [round(100 * float(lo), 2), round(100 * float(hi), 2)],
                                           "contiene_cero": bool(lo <= 0 <= hi), "cortes_abs_sox": [round(float(x), 3) for x in cortes],
                                           "fechas_cond_por_estrato": [int(len(Ma[k])) for k in range(n_estratos)]},
            "truncado_simetrico_p75": sim, "tope_abs_sox_pp": round(float(tope), 3)}


def mcnemar_pareado(df: pd.DataFrame, col_a: str = "sox_prev", col_b: str = "sox_prev2") -> dict:
    """Último cierre vs cierre anterior sobre las MISMAS filas (dictamen B,
    E-3): b, c, p (χ² con continuidad) y Wilson de filas. Optimista por
    clustering de día, y se dice."""
    from backtest import linea_base as lb
    d = df[(df["gap_pct"] != 0) & df[col_b].notna()]
    ha = ((d[col_a] >= 0) == (d["gap_pct"] > 0)).to_numpy()
    hb = ((d[col_b] >= 0) == (d["gap_pct"] > 0)).to_numpy()
    base = (d["gap_pct"] > 0).to_numpy()
    b01, b10 = int((ha & ~hb).sum()), int((~ha & hb).sum())
    n = len(d)
    if n == 0:
        return {"n": 0}
    return {"n": n, "ultimo_cierre_pct": round(100 * ha.mean(), 1), "cierre_anterior_pct": round(100 * hb.mean(), 1),
            "base_pct": round(100 * base.mean(), 1), "b": b01, "c": b10, "mcnemar_p": lb.mcnemar(b01, b10),
            "advertencia": "filas como unidad: optimista por clustering de día"}


def correr(df: pd.DataFrame, desde: str, hasta: str, etiqueta: str) -> dict:
    sub = df[(df["fecha"] >= desde) & (df["fecha"] <= hasta)].copy()
    rancias = int(sub["insumo_rancio"].sum())
    sub = sub[~sub["insumo_rancio"]]
    # ventana sellada EXCLUIDA y embargada en sus dos bordes (5 sesiones): antes
    # el entregable lo declaraba y el código no lo hacía (dictamen B, B-1)
    bd = pd.tseries.offsets.BDay(EMBARGO_SESIONES)
    s_ini, s_fin = pd.Timestamp(SELLADA[0]) - bd, pd.Timestamp(SELLADA[1]) + bd
    selladas = int(((sub["fecha"] >= s_ini) & (sub["fecha"] <= s_fin)).sum())
    sub = sub[~((sub["fecha"] >= s_ini) & (sub["fecha"] <= s_fin))]
    if etiqueta == "prueba":
        sub = sub[sub["fecha"] >= pd.Timestamp(desde) + bd]
    cond = condiciones(sub)
    sub = sub.merge(cond, on=["exchange", "fecha"], how="inner")
    out = {"ventana": etiqueta, "filas": int(len(sub)), "fechas": int(sub["fecha"].nunique()),
           "filas_excluidas_por_insumo_rancio": rancias,
           "filas_excluidas_ventana_sellada_con_embargo": selladas, "sellada": SELLADA, "embargo_sesiones": EMBARGO_SESIONES,
           "conteo_n_ny": {f"{e}|n_ny={k}": int(v) for (e, k), v in
                           sub.drop_duplicates(["exchange", "fecha"]).groupby(["exchange", "n_ny"]).size().items()}}
    # C1: NY cerrada (n_ny = 0) contra normal (n_ny = 1), por bolsa; y dos
    # controles de la auditoría: contra los normales NO lunes (el lunes
    # «normal» tiene h ≈ 52 h), y contra normales con |SOX| emparejado (los
    # feriados de NY caen en tramos quietos: |gap| menor, más ruido de signo)
    out["C1_ny_cerrada"] = {}
    out["C1_control_sin_lunes"] = {}
    out["C1_control_sox_emparejado"] = {}
    for e in sorted(sub["exchange"].unique()):
        s_ = sub[sub.exchange == e]
        out["C1_ny_cerrada"][e] = contraste(s_, s_.n_ny == 0, s_.n_ny == 1)
        out["C1_control_sin_lunes"][e] = contraste(s_, s_.n_ny == 0, (s_.n_ny == 1) & (~s_.lunes))
        # RETIRADO el truncado asimétrico (sólo el grupo normal): invertía el desbalance
        out["C1_control_sox_emparejado"][e] = contraste_estandarizado(s_, s_.n_ny == 0, s_.n_ny == 1)
        # la confusión estructural de C1: en n_ny = 0 la sesión local anterior ya abrió con el MISMO insumo
        prev = s_.drop_duplicates(["fecha"]).sort_values("fecha")
        mismo = (prev["sox_prev"].to_numpy()[1:] == prev["sox_prev"].to_numpy()[:-1])
        nn = prev["n_ny"].to_numpy()[1:]
        out["C1_ny_cerrada"][e]["fraccion_insumo_ya_negociado_por_la_sesion_anterior"] = {
            "n_ny_0": round(float(mismo[nn == 0].mean()), 3) if (nn == 0).any() else None,
            "n_ny_1": round(float(mismo[nn == 1].mean()), 3) if (nn == 1).any() else None}
    # feriado local (n_ny ≥ 2): el insumo es el ÚLTIMO cierre; control con el anterior
    out["feriado_local_n_ny_2"] = {}
    for e in sorted(sub["exchange"].unique()):
        s = sub[sub.exchange == e]
        out["feriado_local_n_ny_2"][e] = {
            "insumo_ultimo_cierre": contraste(s, s.n_ny >= 2, s.n_ny == 1),
            "insumo_cierre_anterior_(el_viejo)": contraste(s, s.n_ny >= 2, s.n_ny == 1, col_sox="sox_prev2"),
            "mcnemar_ultimo_vs_anterior_mismas_filas": mcnemar_pareado(s[s.n_ny >= 2])}
    # C2 / C3: Fráncfort con un intermediario menos (n_ny = 1 en las dos condiciones)
    x = sub[(sub.exchange == "XETR") & (sub.n_ny == 1)]
    out["C2_xetr_sin_tokio"] = contraste(x, x.sin_tokio, x.asia_abierta == 3)
    out["C3_xetr_sin_seul_o_taipei"] = contraste(x, x.sin_seul_o_taipei, x.asia_abierta == 3)
    out["C23_xetr_con_2_intermediarios"] = contraste(x, x.asia_abierta == 2, x.asia_abierta == 3)
    # potencia de C2/C3 calculada, no dicha: semiancho del IC al multiplicar las fechas de condición
    mc, mn = _por_fecha(x[x.asia_abierta == 2], "sox_prev"), _por_fecha(x[x.asia_abierta == 3], "sox_prev")
    rng = np.random.default_rng(SEMILLA + 9)
    out["potencia_C23_semiancho_pp_por_multiplicador"] = {}
    for mult in (1, 6, 10, 23):
        ka = len(mc) * mult
        ia = rng.integers(0, len(mc), size=(2000, ka)); ib = rng.integers(0, len(mn), size=(2000, len(mn)))
        Sa, Sb = mc[ia].sum(axis=1), mn[ib].sum(axis=1)
        reps = (Sa[:, 1] - Sa[:, 2]) / Sa[:, 0] - (Sb[:, 1] - Sb[:, 2]) / Sb[:, 0]
        lo, hi = np.quantile(reps, [0.025, 0.975])
        out["potencia_C23_semiancho_pp_por_multiplicador"][f"x{mult}"] = {"fechas_cond": int(ka), "semiancho_pp": round(100 * float(hi - lo) / 2, 2)}
    out["fechas_C1_union_interseccion"] = _union_interseccion(sub)
    return out, {k: v for k, v in out["conteo_n_ny"].items()}


def _union_interseccion(sub: pd.DataFrame) -> dict:
    conj = {e: set(sub[(sub.exchange == e) & (sub.n_ny == 0)]["fecha"]) for e in sorted(sub["exchange"].unique())}
    vals = list(conj.values())
    return {"union": len(set.union(*vals)) if vals else 0, "interseccion": len(set.intersection(*vals)) if vals else 0,
            "por_exchange": {e: len(v) for e, v in conj.items()}}


def _sha(ruta):
    import hashlib
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def candado_de_apertura(enmienda: str | None = None) -> dict:
    """Una sola apertura de la prueba, con rastro (dictamen B, E-7; misma
    mecánica que `no_capturabilidad.candado_de_apertura`)."""
    import hashlib
    h = hashlib.sha256()
    for r in (os.path.abspath(__file__), RUTA_PREREGISTRO):
        with open(r, "rb") as f:
            h.update(f.read())
    actual, datos = h.hexdigest(), {os.path.relpath(r, _RAIZ): _sha(r) for r in (RUTA_GAPS_GZ, RUTA_SOX_GZ)}
    ahora = datetime.now(timezone.utc).isoformat()
    if os.path.exists(RUTA_LOCK):
        with open(RUTA_LOCK) as f:
            previo = json.load(f)
        if previo.get("sha256") == actual and previo.get("datos") in (None, datos):
            return previo
        if not enmienda:
            raise RuntimeError("la prueba del Frente B1 ya fue abierta con otro módulo/pre-registro/datos: no se reabre en silencio; usar --enmienda \"razón\"")
        previo.setdefault("enmiendas", []).append({"en_utc": ahora, "sha256_anterior": previo["sha256"], "sha256_nuevo": actual, "razon": enmienda})
        previo["sha256"], previo["datos"] = actual, datos
        with open(RUTA_LOCK, "w") as f:
            json.dump(previo, f, indent=1, ensure_ascii=False)
        return previo
    lock = {"sha256": actual, "datos": datos, "abierta_en_utc": ahora,
            "nota": "la primera apertura (12:24) fue anterior al candado; se registra aquí la primera con rastro",
            "enmiendas": [{"en_utc": ahora, "razon": enmienda}] if enmienda else []}
    with open(RUTA_LOCK, "w") as f:
        json.dump(lock, f, indent=1, ensure_ascii=False)
    return lock


def contar_intervalos(o) -> int:
    if isinstance(o, dict):
        return 1 if ("ic95_pp" in o and "diferencia_pp" in o) else sum(contar_intervalos(v) for v in o.values())
    if isinstance(o, list):
        return sum(contar_intervalos(v) for v in o)
    return 0


def main(abrir_prueba: bool = False, enmienda: str | None = None) -> dict:
    df = cargar()
    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "etiqueta": "PROPUESTA — Frente B1, octava corrida; pendiente de dictamen",
           "parametros": {"n_boot": N_BOOT, "n_perm": N_PERM, "relevante_pp": RELEVANTE_PP,
                          "ajuste": AJUSTE, "prueba": PRUEBA, "prueba_abierta": abrir_prueba, "semilla": SEMILLA,
                          "fuentes": [os.path.relpath(RUTA_GAPS_GZ, _RAIZ), os.path.relpath(RUTA_SOX_GZ, _RAIZ),
                                      f"exchange_calendars {xc.__version__}"]}}
    res["ajuste"], _ = correr(df, *AJUSTE, etiqueta="ajuste")
    if abrir_prueba:
        res["parametros"]["candado"] = candado_de_apertura(enmienda)
        res["parametros"]["aperturas"] = ["12:24 (sin candado; la prueba INCLUÍA las fechas selladas y no tenía embargo)",
                                          "re-corrida con --enmienda tras el dictamen B: selladas excluidas y embargadas; una sola re-apertura, declarada"]
        res["prueba"], _ = correr(df, *PRUEBA, etiqueta="prueba")
    res["intentos_dsr"] = {"intervalos_publicados": contar_intervalos(res), "regla": "un intento por intervalo publicado (misma convención que C y D); el 17 a mano queda retirado"}
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "decaimiento_feriados.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "decaimiento_feriados.md"), "w") as f:
        f.write(informe(res))
    return res


def _fila(nombre, c):
    if "nota" in c:
        return f"| {nombre} | {c['fechas_cond']} / {c['fechas_norm']} | — | — | — | — | {c['nota']} |"
    vs0 = "contiene el cero" if c["contiene_cero"] else "excluye el cero"
    vs5 = "supera 5 pp" if c["supera_5pp"] else ("excluye ±5 pp" if c["excluye_5pp"] and not c["contiene_5pp"] else "contiene ±5 pp")
    b20 = f"{c['ic95_bloques20_pp']}{' (contiene el cero)' if c['contiene_cero_bloques20'] else ''}"
    return (f"| {nombre} | {c['fechas_cond']} / {c['fechas_norm']} | {c['ventaja_cond_pp']} | {c['ventaja_norm_pp']} | "
            f"**{c['diferencia_pp']}** {c['ic95_pp']} | {b20} | {c['p_permutacion']} | {vs0}; {vs5} |")


def informe(r: dict) -> str:
    L = ["# El experimento natural de los feriados — Frente B1 (PROPUESTA)\n",
         f"> **{r['etiqueta']}** · generado {r['generado_en_utc']} · `python GEMELO/decaimiento_feriados.py`"
         f"{' --abrir-prueba' if r['parametros']['prueba_abierta'] else ''}\n",
         "Pre-registro: `GEMELO/preregistro/frente_B.md`. Sin motor: predicción = signo del último cierre de NY anterior a la apertura local. "
         "Δ = acierto del signo − «siempre al alza» (`excluir_cero`). IC por bootstrap de fechas; p por permutación de la etiqueta de condición entre fechas. "
         f"Efecto relevante pre-declarado: {r['parametros']['relevante_pp']} pp.\n"]
    for ven in ("ajuste", "prueba"):
        if ven not in r:
            L.append(f"## Años de {ven.upper()}: no abiertos todavía\n")
            continue
        a = r[ven]
        L += [f"## Años de {ven.upper()} ({r['parametros'][ven][0]} → {r['parametros'][ven][1]}): {a['filas']} filas, {a['fechas']} fechas "
              f"({a['filas_excluidas_por_insumo_rancio']} filas excluidas por insumo rancio: la serie del SOX no tenía la última sesión de NY del calendario)\n",
              "| contraste | fechas cond / normal | Δ cond (pp) | Δ normal (pp) | diferencia (IC95 fechas iid) | IC95 bloques 20 | p perm | contra 0 / contra 5 pp |",
              "|---|---|---|---|---|---|---|---|"]
        for e, c in a["C1_ny_cerrada"].items():
            L.append(_fila(f"C1 · {e}: NY cerrada (n_ny=0) vs normal", c))
            L.append(_fila(f"C1 · {e}: vs normal SIN lunes (control h)", a["C1_control_sin_lunes"][e]))
            ce = a["C1_control_sox_emparejado"][e]
            if "nota" in ce:
                L.append(f"| C1 · {e}: control |SOX| | — | — | — | — | — | — | {ce['nota']} |")
            else:
                es = ce["estandarizado_por_estratos"]
                L.append(f"| C1 · {e}: control |SOX| ESTANDARIZADO por 4 estratos (cortes del grupo normal) | {es['fechas_cond_por_estrato']} | — | — | **{es['diferencia_pp']}** {es['ic95_pp']} | — | — | {'contiene el cero' if es['contiene_cero'] else 'excluye el cero'} |")
                L.append(_fila(f"C1 · {e}: control |SOX| truncado SIMÉTRICO a ≤ p75 de la condición ({ce['tope_abs_sox_pp']})", ce["truncado_simetrico_p75"]))
            fr = a["C1_ny_cerrada"][e].get("fraccion_insumo_ya_negociado_por_la_sesion_anterior", {})
            L.append(f"| C1 · {e}: fracción de fechas cuyo insumo YA fue negociado por la sesión local anterior | n_ny=0: {fr.get('n_ny_0')} · n_ny=1: {fr.get('n_ny_1')} | | | **confusión estructural: C1 contrasta insumo no incorporado vs YA incorporado, no fresco vs viejo** | | | |")
        for e, c in a["feriado_local_n_ny_2"].items():
            L.append(_fila(f"feriado local · {e}: n_ny≥2, insumo = último cierre", c["insumo_ultimo_cierre"]))
            L.append(_fila(f"feriado local · {e}: n_ny≥2, insumo = cierre ANTERIOR (viejo)", c["insumo_cierre_anterior_(el_viejo)"]))
            m = c["mcnemar_ultimo_vs_anterior_mismas_filas"]
            if m.get("n"):
                L.append(f"| feriado local · {e}: McNemar último vs anterior, MISMAS filas | n = {m['n']} | {m['ultimo_cierre_pct']} | {m['cierre_anterior_pct']} (base {m['base_pct']}) | b = {m['b']}, c = {m['c']} | — | **p = {m['mcnemar_p']}** | {m['advertencia']} |")
        L.append(_fila("C2 · XETR sin Tokio vs Asia completa", a["C2_xetr_sin_tokio"]))
        L.append(_fila("C3 · XETR sin Seúl o sin Taipéi vs Asia completa", a["C3_xetr_sin_seul_o_taipei"]))
        L.append(_fila("C2+C3 · XETR con 2 intermediarios vs 3", a["C23_xetr_con_2_intermediarios"]))
        L.append(f"\nConteo de (exchange, n_ny): {a['conteo_n_ny']}. Fechas C1 por exchange / unión / intersección: {a['fechas_C1_union_interseccion']} (un experimento, no cuatro). "
                 f"Excluidas: {a['filas_excluidas_ventana_sellada_con_embargo']} filas de la ventana sellada {a['sellada']} con embargo de {a['embargo_sesiones']} sesiones.\n")
        L.append("Potencia de C2+C3 calculada (semiancho del IC95 al multiplicar las fechas de condición): " +
                 "; ".join(f"{k}: {v['fechas_cond']} fechas → ±{v['semiancho_pp']} pp" for k, v in a["potencia_C23_semiancho_pp_por_multiplicador"].items()) +
                 ". Refutar H_dis exige semiancho < 5 pp; DECIDIR entre H_dis y H_abs exige semiancho < 2,5 pp. Multiplicando sólo las fechas de condición "
                 "el semiancho NO baja de ~±5 pp ni a ×23 (el grupo normal también acota): con feriados asiáticos la pregunta no se decide en ningún horizonte razonable "
                 "(×23 son más de un siglo de feriados).\n")
    L.append("**Lectura pre-registrada:** H_dis y H_abs coinciden en C1 (ambas: la ventaja cae); difieren en C2/C3 "
             "(H_dis: nada; H_abs: sube ≥ 5 pp). Si el IC de C2/C3 contiene 0 y 5 pp, no se distinguen con estos datos.\n")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    if "--solo-informe" in sys.argv:
        with open(os.path.join(DIR_RESULTADOS, "decaimiento_feriados.json")) as f:
            r = json.load(f)
        with open(os.path.join(DIR_RESULTADOS, "decaimiento_feriados.md"), "w") as f:
            f.write(informe(r))
        sys.exit(0)
    enm = sys.argv[sys.argv.index("--enmienda") + 1] if "--enmienda" in sys.argv else None
    r = main(abrir_prueba="--abrir-prueba" in sys.argv, enmienda=enm)
    print(json.dumps({k: v for k, v in r["ajuste"].items() if k != "conteo_n_ny"}, indent=1, default=str)[:6000])
