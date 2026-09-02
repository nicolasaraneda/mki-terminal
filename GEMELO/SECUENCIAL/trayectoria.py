"""Frente C de la séptima corrida (2-sep-2026): la fragilidad de cruzar α.

PROPUESTA (regla quinta de la corrida): nada de lo que este script computa
entra a una cifra publicada, a un criterio congelado ni a un documento de
resultados sin dictamen de `estadistico-adversario`.

El hecho que motiva: el 1-sep el sello de las 18:15 agregó UN día y el p
del McNemar sin deduplicar pasó de 0,1849 a 0,0486 (acta §70). Un solo día
movió el estadístico de un lado de α al otro.

La pregunta: ¿qué estadístico principal NO tiene esa propiedad? La
respuesta honesta empieza por decir que TODO test con umbral la tiene
cuando el valor está cerca del umbral: la propiedad no es del estadístico
sino de la DECISIÓN binaria. Lo que sí varía entre candidatos es (a) cuánto
se mueve el estadístico por observación, (b) si la decisión al cruzar
sigue siendo válida cuando se mira todos los días (anytime-valid), y (c) si
el reporte es un número continuo (intervalo, posterior) o una decisión.

Candidatos, evaluados sobre la trayectoria REAL de la ventana sellada
(prefijos crecientes por fecha de emisión, desde 10 días):

  MCN  McNemar exacto sobre filas (el estadístico degradado en la acta §61).
  ICD  Intervalo de clúster de día (el principal desde la acta §61):
       decisión = el IC95 excluye 0.
  PSD  Permutación de signo por día (`bifurcaciones._p_permutacion_dia`).
  TDM  t sobre las medias diarias (día = unidad, aproximación normal).
  BAY  Posterior bayesiana de la ventaja media diaria con prior escéptica
       N(0, 0,05²) — reporta P(Δ>0) y P(Δ>9 pp); «decisión» = P(Δ>0) ≥ 0,95.
  AVS  Proceso de apuestas anytime-valid (Waudby-Smith & Ramdas 2020,
       «hedged capital», una cola: H0: Δ ≤ 0) sobre la media diaria
       reescalada a [0,1]; decisión = capital ≥ 1/α. Válido a CUALQUIER
       instante de parada: mirarlo cada día no infla α.
  SGN  Signo de los días (cuántos días ganó el modelo vs perdió),
       binomial exacta bilateral. Es el «10-6» de la acta §61.

Para cada uno: la trayectoria completa, el número de CRUCES del umbral a lo
largo de la trayectoria (cuántas veces la decisión cambió de un día al
siguiente), y el salto del último día. Un candidato que cruza muchas veces
no es un candidato para decidir; uno que no cruza nunca puede ser que no
tenga potencia.

Ancla: track record vivo (`hasta_sello=None`) — a propósito, porque el
objeto de estudio es la trayectoria, no una cifra; el último punto se
etiqueta con la fecha del último sello para que reproduzca.

Uso: `python GEMELO/SECUENCIAL/trayectoria.py` → `GEMELO/resultados/trayectoria.{json,md}`.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from backtest import linea_base as lb                     # noqa: E402
from backtest.inferencia import Phi, Phi_inv              # noqa: E402
from GEMELO import bifurcaciones as bf                    # noqa: E402

DIR_RESULTADOS = os.path.join(_RAIZ, "GEMELO", "resultados")
ALFA = 0.05
PRIOR_SD = 0.05          # prior escéptica: la ventaja media diaria ~ N(0, 5 pp²)
RELEVANCIA = 0.09        # 9 pp, la relevancia del propio proyecto
MIN_DIAS = 10
N_BOOT = 4000
N_PERM = 4000
SEMILLA = 20260902


def _binomial_bilateral(k: int, n: int) -> float:
    """p exacta bilateral del test de signo (suma de probabilidades ≤ la observada)."""
    if n == 0:
        return 1.0
    p_obs = math.comb(n, k) / 2 ** n
    return min(1.0, sum(math.comb(n, i) for i in range(n + 1)
                        if math.comb(n, i) / 2 ** n <= p_obs + 1e-15) / 2 ** n)


def proceso_apuestas(x: np.ndarray, alfa: float = ALFA, mu0: float = 0.5,
                     c: float = 0.5) -> np.ndarray:
    """Capital del proceso «hedged» de una cola (Waudby-Smith & Ramdas 2020,
    predictable plug-in). x ∈ [0,1]; H0: E[x] ≤ mu0. Devuelve K_t; rechaza
    cuando K_t ≥ 1/α. λ_t usa sólo el pasado (predecible)."""
    K = np.empty(len(x))
    cap = 1.0
    m_prev, s2_prev = 0.5, 0.25          # priors del plug-in
    suma, suma2 = 0.0, 0.0
    for t, xt in enumerate(x, start=1):
        lam = min(c, math.sqrt(2 * math.log(1 / alfa) / (s2_prev * t * math.log(1 + t))))
        cap *= max(1e-12, 1 + lam * (xt - mu0))
        K[t - 1] = cap
        suma += xt
        suma2 += xt * xt
        m_prev = (0.5 + suma) / (t + 1)
        s2_prev = (0.25 + suma2 - (t + 1) * m_prev ** 2 + 0.25) / (t + 1)
        s2_prev = max(s2_prev, 1e-4)
    return K


def estadisticos(df: pd.DataFrame) -> dict:
    d = (df["acierto_gap"] - df["base_acierto"]).to_numpy(dtype=float)
    grupos = bf._por_dia(df, d)
    k = len(grupos)
    medias = np.array([g.mean() for g in grupos])
    duelo = lb.duelo(df)
    p_mcn = float(lb.mcnemar(duelo["mcnemar_b01"], duelo["mcnemar_b10"], correccion=False))
    punto, lo, hi = bf._bootstrap_dia(grupos, n_boot=N_BOOT)
    p_psd = bf._p_permutacion_dia(grupos, N_PERM)
    # t sobre medias diarias (normal aprox.)
    sd = medias.std(ddof=1) if k > 1 else float("nan")
    t = medias.mean() / (sd / math.sqrt(k)) if sd > 0 else 0.0
    p_tdm = 2 * (1 - Phi(abs(t)))
    # posterior conjugada: prior N(0, PRIOR_SD²), verosimilitud de la media
    var_lik = (sd ** 2) / k if sd > 0 else 1e-6
    prec = 1 / PRIOR_SD ** 2 + 1 / var_lik
    mu_post = (medias.mean() / var_lik) / prec
    sd_post = math.sqrt(1 / prec)
    p_gt0 = 1 - Phi((0 - mu_post) / sd_post)
    p_gt_rel = 1 - Phi((RELEVANCIA - mu_post) / sd_post)
    # apuestas anytime-valid sobre x = (media diaria + 1)/2 ∈ [0,1]
    K = proceso_apuestas((medias + 1) / 2)
    # signo de los días
    pos, neg = int((medias > 0).sum()), int((medias < 0).sum())
    p_sgn = _binomial_bilateral(min(pos, neg), pos + neg)
    return {
        "dias": k, "filas": int(len(d)), "ventaja_pp": round(100 * float(d.mean()), 2),
        "MCN_p": round(p_mcn, 4), "MCN_decide": int(p_mcn < ALFA),
        "ICD_lo_pp": round(100 * lo, 2), "ICD_hi_pp": round(100 * hi, 2),
        "ICD_decide": int(lo > 0 or hi < 0),
        "PSD_p": round(p_psd, 4), "PSD_decide": int(p_psd < ALFA),
        "TDM_t": round(float(t), 3), "TDM_p": round(p_tdm, 4), "TDM_decide": int(p_tdm < ALFA),
        "BAY_mu_pp": round(100 * mu_post, 2), "BAY_sd_pp": round(100 * sd_post, 2),
        "BAY_p_gt0": round(p_gt0, 3), "BAY_p_gt9pp": round(p_gt_rel, 3),
        "BAY_decide": int(p_gt0 >= 1 - ALFA),
        "AVS_capital": round(float(K[-1]), 3), "AVS_decide": int(K[-1] >= 1 / ALFA),
        "SGN_pos": pos, "SGN_neg": neg, "SGN_p": round(p_sgn, 4), "SGN_decide": int(p_sgn < ALFA),
    }


CANDIDATOS = ("MCN", "ICD", "PSD", "TDM", "BAY", "AVS", "SGN")


def main() -> dict:
    df = lb.aplicar_convencion(lb.cargar(hasta_sello=None), lb.CONVENCION_OFICIAL)
    fechas = sorted(df["fecha"].unique())
    tray = []
    for i in range(MIN_DIAS, len(fechas) + 1):
        sub = df[df["fecha"] <= fechas[i - 1]]
        e = estadisticos(sub)
        e["hasta_fecha"] = fechas[i - 1]
        tray.append(e)
    # El motivo correcto de C-3 (dictamen del adversario): el McNemar de filas
    # no es «frágil», tiene la escala inflada por √DEFF. Un test que rechaza
    # a |z| > 1,96 con un SE √DEFF veces menor que el verdadero rechaza en
    # realidad a |z_true| > 1,96/√DEFF: ése es su α real.
    d_all = (df["acierto_gap"] - df["base_acierto"]).to_numpy(dtype=float)
    icc = bf.icc_y_deff(bf._por_dia(df, d_all))
    z_nom = Phi_inv(1 - ALFA / 2)
    alfa_real = 2 * (1 - Phi(z_nom / math.sqrt(icc["deff"])))
    escala = {"icc": round(icc["icc"], 4), "deff": round(icc["deff"], 4),
              "raiz_deff": round(math.sqrt(icc["deff"]), 3),
              "alfa_real_del_mcnemar_de_filas_a_5pct_nominal": round(alfa_real, 3),
              "z_MCN_sobre_z_ICD_hoy": None}
    cruces = {}
    for c in CANDIDATOS:
        dec = [t[f"{c}_decide"] for t in tray]
        cruces[c] = {"cruces": int(sum(1 for a, b in zip(dec, dec[1:]) if a != b)),
                     "dias_decidiendo": int(sum(dec)), "decide_hoy": dec[-1],
                     "decide_ultimos_5": dec[-5:]}
    ultimo, penultimo = tray[-1], tray[-2]
    salto = {"de": penultimo["hasta_fecha"], "a": ultimo["hasta_fecha"],
             "MCN_p": [penultimo["MCN_p"], ultimo["MCN_p"]],
             "ICD_pp": [[penultimo["ICD_lo_pp"], penultimo["ICD_hi_pp"]], [ultimo["ICD_lo_pp"], ultimo["ICD_hi_pp"]]],
             "PSD_p": [penultimo["PSD_p"], ultimo["PSD_p"]],
             "TDM_p": [penultimo["TDM_p"], ultimo["TDM_p"]],
             "BAY_p_gt0": [penultimo["BAY_p_gt0"], ultimo["BAY_p_gt0"]],
             "AVS_capital": [penultimo["AVS_capital"], ultimo["AVS_capital"]],
             "SGN": [f"{penultimo['SGN_pos']}-{penultimo['SGN_neg']}", f"{ultimo['SGN_pos']}-{ultimo['SGN_neg']}"]}
    # cociente de escalas hoy: z del McNemar (de su p) sobre z del ICD (de su IC)
    u = tray[-1]
    z_mcn = Phi_inv(1 - u["MCN_p"] / 2)
    se_icd = (u["ICD_hi_pp"] - u["ICD_lo_pp"]) / (2 * Phi_inv(0.975))
    z_icd = u["ventaja_pp"] / se_icd if se_icd else float("nan")
    escala["z_MCN_sobre_z_ICD_hoy"] = round(z_mcn / z_icd, 3) if z_icd else None
    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "escala_del_mcnemar_de_filas": escala,
           "ancla": {"hasta_sello": None, "ultimo_sello": fechas[-1], "dias": len(fechas),
                     "filas": int(len(df)), "convencion": lb.CONVENCION_OFICIAL,
                     "dedup": "regla firmada"},
           "parametros": {"alfa": ALFA, "prior_sd": PRIOR_SD, "relevancia": RELEVANCIA,
                          "min_dias": MIN_DIAS, "n_boot": N_BOOT, "n_perm": N_PERM},
           "cruces": cruces, "salto_ultimo_dia": salto, "trayectoria": tray,
           "etiqueta": "PROPUESTA — sin dictamen del estadistico-adversario no entra a ningún documento de resultados"}
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "trayectoria.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "trayectoria.md"), "w") as f:
        f.write(informe(res))
    return res


def informe(r: dict) -> str:
    a = r["ancla"]
    L = ["# La fragilidad de cruzar α — trayectorias de siete estadísticos (Frente C, PROPUESTA)\n",
         f"> **{r['etiqueta']}**\n",
         f"- Generado: {r['generado_en_utc']} · `python GEMELO/SECUENCIAL/trayectoria.py`",
         f"- Ancla: track record vivo hasta el sello del **{a['ultimo_sello']}** ({a['dias']} días, {a['filas']} filas, "
         f"regla firmada, `{a['convencion']}`). Prefijos por fecha de emisión desde {r['parametros']['min_dias']} días.\n",
         "## Cruces del umbral de decisión a lo largo de la trayectoria\n",
         "| candidato | cruces | días «decidiendo» | decide hoy | últimos 5 |", "|---|---|---|---|---|"]
    for c, v in r["cruces"].items():
        L.append(f"| {c} | **{v['cruces']}** | {v['dias_decidiendo']} | {v['decide_hoy']} | {v['decide_ultimos_5']} |")
    e = r["escala_del_mcnemar_de_filas"]
    L += [f"\n## La escala del McNemar de filas (por qué C-3)\n",
          f"- ICC {e['icc']}, DEFF {e['deff']}, √DEFF {e['raiz_deff']}; z_MCN / z_ICD hoy = {e['z_MCN_sobre_z_ICD_hoy']}.",
          f"- **α real de un McNemar de filas al 5% nominal bajo este agrupamiento: {e['alfa_real_del_mcnemar_de_filas_a_5pct_nominal']}.** "
          f"No es fragilidad: es un test cuyo tamaño no es el que declara."]
    s = r["salto_ultimo_dia"]
    L += [f"\n## El salto del último día ({s['de']} → {s['a']})\n", "| candidato | antes | después |", "|---|---|---|",
          f"| MCN p | {s['MCN_p'][0]} | {s['MCN_p'][1]} |",
          f"| ICD IC95 pp | {s['ICD_pp'][0]} | {s['ICD_pp'][1]} |",
          f"| PSD p | {s['PSD_p'][0]} | {s['PSD_p'][1]} |",
          f"| TDM p | {s['TDM_p'][0]} | {s['TDM_p'][1]} |",
          f"| BAY P(Δ>0) | {s['BAY_p_gt0'][0]} | {s['BAY_p_gt0'][1]} |",
          f"| AVS capital | {s['AVS_capital'][0]} | {s['AVS_capital'][1]} |",
          f"| SGN días +/− | {s['SGN'][0]} | {s['SGN'][1]} |",
          "\n## Trayectoria completa\n",
          "| hasta | días | filas | ventaja | MCN p | ICD IC95 | PSD p | TDM p | BAY P(Δ>0) | BAY P(Δ>9) | AVS K | SGN |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in r["trayectoria"]:
        L.append(f"| {t['hasta_fecha']} | {t['dias']} | {t['filas']} | {t['ventaja_pp']} | {t['MCN_p']} | "
                 f"[{t['ICD_lo_pp']}, {t['ICD_hi_pp']}] | {t['PSD_p']} | {t['TDM_p']} | {t['BAY_p_gt0']} | "
                 f"{t['BAY_p_gt9pp']} | {t['AVS_capital']} | {t['SGN_pos']}-{t['SGN_neg']} |")
    L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["cruces"], indent=1))
    print(json.dumps(r["salto_ultimo_dia"], indent=1))
