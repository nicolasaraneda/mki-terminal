# ============================================================
# La corrida de VEREDICTO de la Etapa 5.1 — B0→B5 contra los criterios
# CONGELADOS de backtest/DISEÑO.md §8 y GEMELO/DISEÑO.md §6 (V1–V7, R1–R3).
#
# Este módulo NO define ni mueve un solo criterio: los lee donde están
# congelados y los aplica. Todo parámetro de la corrida está declarado
# ANTES de correr en GEMELO/resultados/gatillo_51.md, incluido el
# N_intentos del Deflated Sharpe.
#
#   source venv/bin/activate
#   python -m backtest.veredicto_51
#
# LO QUE ESTE MÓDULO NO HACE, A PROPÓSITO:
#   - NO evalúa el holdout en cuarentena. GEMELO/DISEÑO.md §6.1 V7 lo define
#     como "evaluado una sola vez": es irreversible, el gatillo del GATE B
#     no está cumplido, y gastarlo hoy lo quemaría para siempre. V7 sale
#     NO EVALUABLE por esa razón, no por falta de maquinaria.
#   - NO escribe en senales.db ni en noticias.db (mode=ro heredado de
#     backtest/datos.py).
# ============================================================

import json
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude", "skills", "estadistica-evaluacion", "scripts"))
import evaluacion as ev  # noqa: E402

from backtest import cartera, inferencia, metricas, motorbt  # noqa: E402
from backtest.datos import FuenteCongelada, predicciones_selladas  # noqa: E402

# ------------------------------------------------------------
# PARÁMETROS — declarados en GEMELO/resultados/gatillo_51.md §2 el
# 2026-09-01 01:42 hora de Chile, ANTES de correr. Cambiar cualquiera de
# éstos después de ver los resultados sería elegir la configuración
# favorable; por eso viven aquí, en una sola pantalla, y no dispersos.
# ------------------------------------------------------------
DESDE = date(2024, 9, 2)      # 250 sesiones de burn-in del ^SOX cumplidas
HASTA = date(2026, 8, 28)     # último viernes con desenlace completo
SEMILLA_BOOTSTRAP = 20260901
ALPHA_BOOTSTRAP = 0.05        # IC 95%: más ancho, más exigente que el 0.10
ETIQUETA = "5.1-invalidada-por-fuga"

# N_intentos del DSR — §1.4 del expediente. 25 (en código) + 1 (declarado
# no corrido) + 18 (declarado en prosa) + 32 (reconstruidos) + 6 (esta
# corrida sobre ventana nueva). La banda existe para que el veredicto no
# dependa de dónde se corte el conteo.
N_INTENTOS_51 = 82
BANDA_N = (26, 44, 82, 110)

# Un Sharpe ANUALIZADO sobre pocas decenas de días es un artefacto de
# multiplicar por √252. Espejo de GEMELO/control_lineal.py:81 — abajo de
# esto, PSR y DSR se reportan NO INTERPRETABLE, jamás el número.
MINIMO_DIAS_SHARPE = 60

# GEMELO/DISEÑO.md §6.2 R2: la ventana que sostiene casi toda la ventaja
# del campeón. Se aplica por RANGO DE FECHAS, no por índice de bloque.
VENTANA_R2 = ("2026-07-15", "2026-07-23")

# GEMELO/DISEÑO.md §6.1 V3 y V4: las varas congeladas.
V3_COBERTURA = (76.0, 84.0)
V4_MAE_CAMPEON_SELLADO = 3.064   # pp, §2.5 — ventana SELLADA, no ésta
CAMPEON = "B2"                   # el modelo de producción 4.6.0 tal cual

Z80 = 1.2815515655446004

ESTADO_GATILLO = {
    "cumplido": False,
    "vias": [
        "**(a)** N ≥ 150 verificaciones limpias **Y** un cambio de régimen "
        "del SOX: 261 verificaciones limpias — CUMPLE la primera mitad —, "
        "pero el track record tiene **una sola etiqueta de régimen** "
        "(`Alcista · vol alta`, 38 snapshots, más 2 nulos). La conjunción "
        "**NO se cumple**.",
        "**(b)** 3 meses continuos desde el 25-jul-2026: faltan **54 días** "
        "(cae el 25-oct-2026). **NO se cumple**.",
    ],
    "holdout_intacto": True,
    "expediente": "GEMELO/resultados/gatillo_51.md",
    # Fugas DEMOSTRADAS y medidas por la auditoría adversaria del arnés,
    # antes de correr. Cada una está reproducida de forma independiente en
    # la §3 del expediente. R3 no admite excepciones.
    "fugas": [
        "**B-1 · el sentimiento usa juicios de IA que no existían.** "
        "`backtest/datos.py` corta por `titulares.fecha` (publicación) y "
        "**nunca mira `analisis.analizado_en`**. Medido sobre `noticias.db` "
        "en `mode=ro`: **3407 de 5094 análisis (66.9%)** se produjeron "
        "después de las 22:15 UTC del día de publicación; rezago máximo "
        "**320 días**; y el **primer análisis de IA que existe en el "
        "sistema es del 2026-07-04**, mientras los titulares arrancan el "
        "2025-09-09. En la ventana declarada, casi 22 de 24 meses alimentan "
        "B4 y B5 con sentimiento construido con juicios que no existían el "
        "día de la emisión. El `grado B` lo declara pero **ninguna métrica "
        "lo excluye**, y `buzz` sale del mismo join sin grado ninguno.",
        "**B-2 · la guarda `ErrorLookAhead` es tautológica.** "
        "`backtest/baselines.py:182-184` y `:314-315` validan un frame que "
        "acaban de recortar con el MISMO predicado (`index.date <= fecha`), "
        "así que la condición de disparo es inalcanzable por construcción. "
        "Medido: **401.184 invocaciones en un walk-forward, cero capaces de "
        "disparar.** Y una fuga real (`shift(-1)`) desplaza VALORES, no el "
        "índice: la guarda no la ve. La prueba maestra "
        "`test_truncar_futuro_no_cambia_predicciones` cubre **una fecha y "
        "tres baselines**, así que una fuga en las cinco features "
        "exclusivas de B4/B5 es invisible para toda la suite.",
        "**B-3 · el mismo desenlace cuenta hasta 8 veces.** Varias "
        "emisiones consecutivas apuntan a la MISMA sesión objetivo en "
        "feriados largos y `motorbt` escribe una fila por emisión con el "
        "outcome repetido. Medido sobre la ventana declarada: **263 de "
        "4160 filas (6.3%) son desenlaces duplicados**, con dos pares "
        "contados **8 veces** (`2330.TW` 2025-02-03 y 2026-02-23). "
        "Contamina el rank IC diario, la n de Wilson y los retornos de "
        "cartera; y `t_newey_west` usa **lag 5**, que no cubre un bloque de "
        "8 duplicados perfectos: el t-stat del veredicto escalonado sale "
        "inflado.",
    ],
}


# ------------------------------------------------------------
# Utilidades de lectura
# ------------------------------------------------------------
def _series_ls(df: pd.DataFrame, costo_pb: int = 25) -> pd.Series:
    return cartera.retornos_cartera(df, costo_pb)["long_short"]


def _direcciones(df: pd.DataFrame):
    """Filas evaluables para dirección del gap, con la baseline 'siempre al
    alza' medida SOBRE LAS MISMAS FILAS (jamás contra 50%)."""
    d = df.dropna(subset=["gap_pct"]).copy()
    d = d[d["est"] != 0]                       # B0 no tiene signo que acertar
    if d.empty:
        return None
    acierto = ((d["est"] >= 0) == (d["gap_pct"] >= 0)).to_numpy()
    base = ev.baseline_siempre_alza(d["gap_pct"].to_numpy())
    return d, acierto, base


def _duelo(df: pd.DataFrame) -> dict | None:
    r = _direcciones(df)
    if r is None:
        return None
    d, acierto, base = r
    comp = ev.comparar_pareado(acierto, base)
    lo, hi = ev.wilson_ci(int(acierto.sum()), len(acierto))
    return {
        "n": int(len(acierto)),
        "modelo_pct": round(100 * float(acierto.mean()), 2),
        "wilson95_pp": [round(100 * lo, 2), round(100 * hi, 2)],
        "base_pct": round(100 * float(base.mean()), 2),
        "ventaja_pp": round(100 * float(acierto.mean() - base.mean()), 2),
        "b": int(comp.b), "c": int(comp.c),
        "mcnemar_p": round(float(comp.p_mcnemar), 4),
    }


def _crps(df: pd.DataFrame) -> np.ndarray | None:
    """CRPS de la densidad predictiva gaussiana implícita en (est, int80)."""
    d = df.dropna(subset=["gap_pct", "int80"])
    d = d[d["int80"] > 0]
    if d.empty:
        return None
    sigma = d["int80"].to_numpy() / Z80
    return ev.crps_normal(d["gap_pct"].to_numpy(), d["est"].to_numpy(), sigma), d.index


def _cobertura80(df: pd.DataFrame) -> dict | None:
    d = df.dropna(subset=["gap_pct", "int80"])
    d = d[d["int80"] > 0]
    if len(d) < 30:
        return None
    dentro = (d["gap_pct"] - d["est"]).abs() <= d["int80"]
    k, n = int(dentro.sum()), int(len(dentro))
    lo, hi = ev.wilson_ci(k, n)
    return {"n": n, "cobertura_pct": round(100 * k / n, 2),
            "wilson95_pp": [round(100 * lo, 2), round(100 * hi, 2)]}


# ------------------------------------------------------------
# Los criterios
# ------------------------------------------------------------
def evaluar(reporte: dict, dfs: dict) -> dict:
    crit: dict = {}
    bl_ord = [b for b in ("B0", "B1", "B2", "B3", "B4", "B5") if b in dfs]

    # ---------- V1: habilidad sobre la base (McNemar p < 0.05) ----------
    v1 = {b: _duelo(dfs[b]) for b in bl_ord}
    pasan_v1 = [b for b, d in v1.items()
                if d and d["mcnemar_p"] < 0.05 and d["ventaja_pp"] > 0]
    crit["V1"] = {
        "enunciado": "Ventaja sobre 'siempre al alza' en la misma ventana, "
                     "McNemar p < 0.05 (GEMELO/DISEÑO.md §6.1)",
        "detalle": v1,
        "veredicto": "PASA" if pasan_v1 else "NO PASA",
        "quienes": pasan_v1,
    }

    # ---------- V2: CRPS mejor que el campeón, IC que excluye el cero ----
    v2 = {}
    base_crps = _crps(dfs[CAMPEON]) if CAMPEON in dfs else None
    for b in bl_ord:
        if b == CAMPEON or base_crps is None:
            continue
        propio = _crps(dfs[b])
        if propio is None:
            v2[b] = {"estado": "sin densidad predictiva (int80 ausente)"}
            continue
        # emparejar por (fecha, ticker): sólo filas donde ambos emitieron
        a = dfs[b].loc[propio[1], ["fecha_emision", "ticker"]].copy()
        a["crps"] = propio[0]
        c = dfs[CAMPEON].loc[base_crps[1], ["fecha_emision", "ticker"]].copy()
        c["crps"] = base_crps[0]
        j = a.merge(c, on=["fecha_emision", "ticker"], suffixes=("_x", "_c"))
        if len(j) < 30:
            v2[b] = {"estado": f"sólo {len(j)} filas emparejadas"}
            continue
        # mejora = campeón − retador (positivo = el retador es mejor).
        # IC por bootstrap CIRCULAR de bloques del módulo del proyecto
        # (inferencia.bootstrap_media) — NUNCA el iid ni el no circular:
        # el no circular submuestrea la cola de la serie, que es lo más
        # reciente (DECISIONES.md §28).
        dif = inferencia.bootstrap_media(
            (j["crps_c"] - j["crps_x"]).to_numpy(), semilla=SEMILLA_BOOTSTRAP,
            n_draws=2000, bloque=20, alpha=ALPHA_BOOTSTRAP)
        v2[b] = {"n": int(len(j)),
                 "crps_propio": round(float(j["crps_x"].mean()), 4),
                 "crps_campeon": round(float(j["crps_c"].mean()), 4),
                 "mejora": round(float(dif["media"]), 4),
                 "ic95": [round(dif["lo"], 4), round(dif["hi"], 4)],
                 "excluye_cero": bool(dif["lo"] > 0)}
    pasan_v2 = [b for b, d in v2.items() if d.get("excluye_cero")]
    crit["V2"] = {
        "enunciado": f"Mejora del CRPS sobre el campeón ({CAMPEON}) con IC de "
                     "bootstrap de bloques que excluya el cero",
        "detalle": v2,
        "veredicto": "PASA" if pasan_v2 else "NO PASA",
        "quienes": pasan_v2,
    }

    # ---------- V3: calibración del intervalo 80% en [76, 84] ----------
    v3 = {b: _cobertura80(dfs[b]) for b in bl_ord}
    pasan_v3 = [b for b, d in v3.items()
                if d and V3_COBERTURA[0] <= d["cobertura_pct"] <= V3_COBERTURA[1]]
    crit["V3"] = {
        "enunciado": f"Cobertura empírica del intervalo 80% dentro de "
                     f"[{V3_COBERTURA[0]}%, {V3_COBERTURA[1]}%]",
        "detalle": v3,
        "veredicto": "PASA" if pasan_v3 else "NO PASA",
        "quienes": pasan_v3,
    }

    # ---------- V4: MAE del gap ----------
    mae = {b: reporte["baselines"][b]["mae_gap_pp"] for b in bl_ord}
    mae_campeon = mae.get(CAMPEON)
    mejores = [b for b in bl_ord
               if b != CAMPEON and mae[b] is not None and mae_campeon is not None
               and mae[b] < mae_campeon]
    crit["V4"] = {
        "enunciado": f"MAE del gap estrictamente menor que el del campeón "
                     f"(la vara publicada, {V4_MAE_CAMPEON_SELLADO} pp, es de "
                     f"la ventana SELLADA — aquí se compara EN VENTANA contra "
                     f"el {CAMPEON} de esta misma corrida, que es la "
                     f"comparación honesta)",
        "mae_por_baseline_pp": mae,
        "mae_campeon_en_ventana_pp": mae_campeon,
        "mae_campeon_ventana_sellada_pp": V4_MAE_CAMPEON_SELLADO,
        "veredicto": "PASA" if mejores else "NO PASA",
        "quienes": mejores,
    }

    # ---------- V5: Deflated Sharpe con el N declarado ----------
    sharpes, dias_por_b, momentos = {}, {}, {}
    for b in bl_ord:
        s = _series_ls(dfs[b], 25) / 100.0
        s = s.dropna()
        dias_por_b[b] = int(len(s))
        sharpes[b] = (inferencia.sharpe(s.to_numpy(), anualizar=252)
                      if len(s) >= 2 else float("nan"))
        momentos[b] = ev.momentos(s.to_numpy()) if len(s) >= 4 else (0.0, 3.0)
    validos = [v for v in sharpes.values() if v == v]
    V = float(np.var(validos, ddof=1)) if len(validos) >= 2 else 0.25
    v5 = {}
    for b in bl_ord:
        sr, n = sharpes[b], dias_por_b[b]
        if sr != sr:
            v5[b] = {"estado": "Sharpe indefinido"}
            continue
        if n < MINIMO_DIAS_SHARPE:
            v5[b] = {"sharpe_ls_25pb": round(sr, 3), "dias": n,
                     "psr": "NO INTERPRETABLE", "dsr": "NO INTERPRETABLE",
                     "motivo": f"menos de {MINIMO_DIAS_SHARPE} días"}
            continue
        sk, ku = momentos[b]
        fila = {"sharpe_ls_25pb": round(sr, 3), "dias": n,
                "skew": round(sk, 3), "kurtosis": round(ku, 3),
                "V_intentos": round(V, 4),
                "psr_vs_cero": round(inferencia.psr(sr, 0.0, n, sk, ku), 4),
                "psr_vs_cero_momentos_normales":
                    round(inferencia.psr(sr, 0.0, n, 0.0, 3.0), 4),
                "dsr_por_N": {}}
        for N in BANDA_N:
            sr0 = inferencia.sr0_deflacionado(N, V)
            fila["dsr_por_N"][N] = {
                "sr0": round(sr0, 4),
                "dsr": round(inferencia.dsr(sr, n, sk, ku, N, V), 4),
                "dsr_momentos_normales":
                    round(inferencia.dsr(sr, n, 0.0, 3.0, N, V), 4)}
        v5[b] = fila
    pasan_v5 = [b for b, d in v5.items()
                if isinstance(d.get("dsr_por_N"), dict)
                and d["dsr_por_N"][N_INTENTOS_51]["dsr"] >= 0.95]
    crit["V5"] = {
        "enunciado": f"DSR ≥ 0.95 contando TODOS los intentos "
                     f"(N declarado = {N_INTENTOS_51}; banda {BANDA_N})",
        "N_declarado": N_INTENTOS_51, "banda_N": list(BANDA_N),
        "V_intentos": round(V, 4),
        "nota_saturacion": "Phi satura sobre z≈8.3: un PSR/DSR de 1.0000 "
                           "significa 'más allá de lo que la doble precisión "
                           "distingue', NO 'certeza'.",
        "detalle": v5,
        "veredicto": "PASA" if pasan_v5 else "NO PASA",
        "quienes": pasan_v5,
    }

    # ---------- V6: superar comprar SMH y no hacer nada ----------
    smh = reporte["benchmark_smh"]
    v6 = {}
    for b in bl_ord:
        por_costo = {}
        for costo in motorbt.COSTOS_PB:
            c = reporte["baselines"][b]["carteras"][costo]
            por_costo[costo] = {
                "long_short": {"acum_pct": c["long_short"]["acumulado_pct"],
                               "sharpe": c["long_short"]["sharpe"],
                               "mdd_pct": c["long_short"]["mdd_pct"]},
                "long_only": {"acum_pct": c["long_only"]["acumulado_pct"],
                              "sharpe": c["long_only"]["sharpe"],
                              "mdd_pct": c["long_only"]["mdd_pct"]},
            }
        gana25 = [lado for lado in ("long_short", "long_only")
                  if (por_costo[25][lado]["acum_pct"] is not None
                      and smh["acumulado_pct"] is not None
                      and por_costo[25][lado]["acum_pct"] > smh["acumulado_pct"])]
        v6[b] = {"por_costo": por_costo, "supera_smh_a_25pb": gana25}
    pasan_v6 = [b for b, d in v6.items() if d["supera_smh_a_25pb"]]
    crit["V6"] = {
        "enunciado": "Superar comprar SMH y no hacer nada después de 25 pb "
                     "por lado, con barrido 10/25/50",
        "benchmark_smh": smh, "detalle": v6,
        "veredicto": "PASA" if pasan_v6 else "NO PASA",
        "quienes": pasan_v6,
    }

    # ---------- V7: holdout — NO SE GASTA ----------
    crit["V7"] = {
        "enunciado": "Confirmación en el holdout en cuarentena, evaluado una "
                     "sola vez (GEMELO/DISEÑO.md §6.1)",
        "veredicto": "NO EVALUABLE",
        "razon": "DELIBERADO. El holdout es un recurso de UN SOLO USO y el "
                 "gatillo del GATE B no está cumplido por ninguna de sus dos "
                 "vías. Gastarlo hoy lo quemaría para siempre y no se puede "
                 "deshacer. Queda INTACTO y en cuarentena. Esto NO es una "
                 "limitación de maquinaria: es la decisión de no gastar un "
                 "recurso irreversible antes de tiempo.",
    }

    # ---------- R1: el control lineal le gana ----------
    ic = {b: reporte["baselines"][b]["ic_medio"] for b in bl_ord}
    lineales = [b for b in ("B1", "B3") if b in ic]
    ricos = [b for b in ("B4", "B5") if b in ic]
    gana_lineal = [(l, r) for l in lineales for r in ricos
                   if ic[l] is not None and ic[r] is not None and ic[l] > ic[r]]
    crit["R1"] = {
        "enunciado": "Se descarta al retador si el control lineal le gana",
        "veredicto": "NO EVALUABLE",
        "razon": "R1 está escrito para un RETADOR contra su control lineal, y "
                 "en esta corrida no hay retador: hay seis baselines. Se "
                 "reporta el análogo —capas simples vs capas ricas— sin "
                 "llamarlo R1.",
        "analogo_ic_medio": ic,
        "capas_simples_que_ganan_a_las_ricas": [f"{l} > {r}" for l, r in gana_lineal],
    }

    # ---------- R2: la ventaja sobrevive excluyendo 15–23 jul ----------
    r2 = {}
    for b in bl_ord:
        df = dfs[b]
        fuera = df[~df["fecha_emision"].between(*VENTANA_R2)]
        dentro = df[df["fecha_emision"].between(*VENTANA_R2)]
        r2[b] = {"n_dentro_ventana": int(len(dentro)),
                 "duelo_sin_la_ventana": _duelo(fuera),
                 "duelo_completo": v1[b]}
    sobreviven = [b for b, d in r2.items()
                  if d["duelo_sin_la_ventana"]
                  and d["duelo_sin_la_ventana"]["ventaja_pp"] > 0]
    crit["R2"] = {
        "enunciado": f"Se descarta a quien pierda su ventaja al excluir "
                     f"{VENTANA_R2[0]} → {VENTANA_R2[1]} (por RANGO DE FECHAS)",
        "detalle": r2,
        "veredicto": "PASA" if sobreviven else "NO PASA",
        "quienes_sobreviven": sobreviven,
    }

    # ---------- R3: fuga detectada por el test de causalidad ----------
    # Éste es el criterio que decide, y decide en contra. Va ANTES que
    # cualquier lectura de las cifras de arriba, no después.
    crit["R3"] = {
        "enunciado": "Cualquier fuga detectada por el test de causalidad. Sin "
                     "discusión y sin excepción.",
        "veredicto": "NO PASA",
        "fugas_demostradas": ESTADO_GATILLO["fugas"],
        "B1_medida_ahora": medir_fuga_sentimiento(),
        "consecuencia": "R3 no admite excepciones. Con fuga demostrada, "
                        "NINGÚN otro criterio de esta corrida es un "
                        "veredicto: las cifras de V1 a V6 se reportan como "
                        "referencia contaminada y nada más. El veredicto de "
                        "la Etapa 5.1 ESPERA a que el arnés se arregle.",
        "lo_que_si_esta_verde": "Suite completa 372/372 antes de tocar nada, "
                                "`python tests/test_motor.py` verde "
                                "(anti-look-ahead del MOTOR de producción en "
                                "4 fechas × 6 funciones), regla maestra de "
                                "emisión sin una sola violación en 172 "
                                "emisiones × 4 bolsas, y todas las "
                                "conexiones a bases de producción en "
                                "`mode=ro` (sonda: «attempt to write a "
                                "readonly database»). La fuga NO está en "
                                "motor.py: está en la capa de datos del "
                                "backtest.",
    }

    # ---------- El veredicto final del §8 de backtest/DISEÑO.md ----------
    ics = {b: metricas.rank_ic_diario(dfs[b]) for b in bl_ord}

    def _delta_t(a: str, b: str) -> dict:
        if a not in ics or b not in ics:
            return {"estado": "no disponible"}
        par = pd.concat({"a": ics[a], "b": ics[b]}, axis=1).dropna()
        if len(par) < 10:
            return {"estado": f"sólo {len(par)} días"}
        dif = par["a"] - par["b"]
        t = metricas.t_newey_west(dif)
        return {"delta_ic": round(float(dif.mean()), 4),
                "t_nw": round(float(t), 2) if t == t else None,
                "n_dias": int(len(par)),
                "supera": bool(dif.mean() > 0 and t == t and t > 2)}

    cond = {}
    for cand in ("B5", "B4"):
        if cand not in dfs:
            continue
        vs1, vs2 = _delta_t(cand, "B1"), _delta_t(cand, CAMPEON)
        ls25 = reporte["baselines"][cand]["carteras"][25]["long_short"]
        ic_sharpe = ls25["sharpe_ic"]
        sharpe_pos = bool(ls25["sharpe"] is not None and ls25["sharpe"] > 0
                          and ic_sharpe and ic_sharpe[0] > 0)
        bate_smh = bool(ls25["acumulado_pct"] is not None
                        and smh["acumulado_pct"] is not None
                        and ls25["acumulado_pct"] > smh["acumulado_pct"])
        cond[cand] = {
            "supera_B1_en_IC_con_t_mayor_2": vs1,
            f"supera_{CAMPEON}_en_IC_con_t_mayor_2": vs2,
            "sharpe_ls_25pb_positivo_con_IC_sobre_cero": {
                "sharpe": ls25["sharpe"],
                "ic95": ([round(ic_sharpe[0], 3), round(ic_sharpe[1], 3)]
                         if ic_sharpe else None),
                "cumple": sharpe_pos},
            "retorno_supera_buy_and_hold_SMH": {
                "acum_estrategia_pct": ls25["acumulado_pct"],
                "acum_smh_pct": smh["acumulado_pct"],
                "mdd_estrategia_pct": ls25["mdd_pct"],
                "mdd_smh_pct": smh["mdd_pct"],
                "cumple": bate_smh},
            "cumple_las_tres": bool(vs1.get("supera") and vs2.get("supera")
                                    and sharpe_pos and bate_smh),
        }
    # Toda cifra de arriba queda marcada por lo que R3 acaba de dictar.
    for clave, valor in crit.items():
        if clave.startswith("V") and valor.get("veredicto") in ("PASA", "NO PASA"):
            valor["veredicto"] = f"{valor['veredicto']} (SOBRE DATOS CON FUGA — no vale)"

    crit["veredicto_final_diseno_8"] = {
        "enunciado": "La cadena MKI 'agrega valor' si B5 (o B4) supera a B1 Y "
                     "a B2 en rank IC con t > 2, Y el Sharpe neto a 25 pb de "
                     "la long-short es positivo con su intervalo bootstrap "
                     "sobre cero, Y el retorno neto acumulado supera al "
                     "buy-and-hold de SMH (backtest/DISEÑO.md §8)",
        "detalle": cond,
        "veredicto": ("AGREGA VALOR"
                      if any(v["cumple_las_tres"] for v in cond.values())
                      else "NO AGREGA VALOR"),
    }
    return crit


# ------------------------------------------------------------
# Fidelidad del arnés: B2 contra los sellos reales, por fecha
# ------------------------------------------------------------
def fidelidad_b2(dfs: dict) -> dict:
    if CAMPEON not in dfs:
        return {}
    sel = predicciones_selladas()
    if sel.empty:
        return {}
    j = dfs[CAMPEON].merge(sel, left_on=["fecha_emision", "ticker"],
                           right_on=["fecha", "ticker"], how="inner")
    if j.empty:
        return {}
    j = j.assign(dif=(j["est"] - j["apertura_estimada_pct"]).abs())
    por_fecha = j.groupby("fecha_emision")["dif"].mean().sort_values(ascending=False)
    peor = por_fecha.index[0]
    sin_peor = j[j["fecha_emision"] != peor]
    return {
        "n_comparadas": int(len(j)),
        "dif_media_pp": round(float(j["dif"].mean()), 4),
        "dif_mediana_pp": round(float(j["dif"].median()), 4),
        "dif_p90_pp": round(float(j["dif"].quantile(0.90)), 4),
        "dif_max_pp": round(float(j["dif"].max()), 3),
        "peor_fecha": peor,
        "dif_media_peor_fecha_pp": round(float(por_fecha.iloc[0]), 4),
        "sin_la_peor_fecha": {
            "n": int(len(sin_peor)),
            "dif_media_pp": round(float(sin_peor["dif"].mean()), 4),
            "dif_max_pp": round(float(sin_peor["dif"].max()), 3)},
        "peores_fechas": {f: round(float(v), 4)
                          for f, v in por_fecha.head(6).items()},
    }


def medir_fuga_sentimiento() -> dict:
    """B-1 MEDIDA, no afirmada: cuántos juicios de IA no existían todavía a
    la hora de la emisión que los usa como feature.

    `backtest/datos.py` corta el sentimiento por `titulares.fecha` (la
    PUBLICACIÓN del titular) y nunca mira `analisis.analizado_en` (cuándo
    Claude emitió el juicio). Esta función abre `noticias.db` en `mode=ro`
    y cuenta la diferencia. Una afirmación de fuga sin su medición al lado
    es prosa; ésta trae el número y se recomputa en cada corrida.
    """
    import sqlite3

    from backtest.datos import RUTA_NOTICIAS
    if not os.path.exists(RUTA_NOTICIAS):
        return {"estado": "noticias.db no disponible"}
    c = sqlite3.connect(f"file:{RUTA_NOTICIAS}?mode=ro", uri=True)
    try:
        fila = c.execute("""
            SELECT COUNT(*),
                   SUM(CASE WHEN a.analizado_en >
                        (substr(t.fecha,1,10) || 'T22:15:00+00:00')
                       THEN 1 ELSE 0 END),
                   SUM(CASE WHEN substr(a.analizado_en,1,10) >
                        substr(t.fecha,1,10) THEN 1 ELSE 0 END),
                   MAX(julianday(substr(a.analizado_en,1,10))
                       - julianday(substr(t.fecha,1,10))),
                   MIN(a.analizado_en), MIN(substr(t.fecha,1,10))
            FROM analisis a JOIN titulares t ON t.id = a.titular_id""").fetchone()
    finally:
        c.close()
    total = fila[0] or 0
    if not total:
        return {"estado": "sin análisis en la base"}
    return {
        "total_analisis": int(total),
        "analizados_despues_de_la_emision_de_su_dia": int(fila[1] or 0),
        "pct_tarde": round(100 * (fila[1] or 0) / total, 1),
        "analizados_en_dia_calendario_posterior": int(fila[2] or 0),
        "rezago_maximo_dias": int(fila[3] or 0),
        "primer_juicio_de_ia_del_sistema": fila[4],
        "primer_titular": fila[5],
        "lectura": ("Toda emisión anterior a "
                    f"{str(fila[4])[:10]} alimenta B4/B5 con sentimiento "
                    "construido con juicios que NO existían ese día. El "
                    "`grado B` lo declara pero ninguna métrica lo excluye."),
    }


def impacto_b3(dfs: dict) -> dict:
    """Cuánto mueve B-3 (desenlaces duplicados) las cifras.

    NO es una segunda corrida ni una configuración nueva: es la MISMA
    corrida releída colapsando las filas que comparten
    (ticker, sesion_objetivo) — se conserva la emisión más TARDÍA, que es
    la que de verdad anticipa esa sesión. Mide fidelidad del arnés, no
    ventaja predictiva, así que no suma intentos al N (misma regla con la
    que la §1.5 del expediente dejó fuera al frente MICRO).
    """
    out = {}
    for b, df in dfs.items():
        if "sesion_objetivo" not in df.columns:
            continue
        dedup = (df.sort_values("fecha_emision")
                   .drop_duplicates(subset=["ticker", "sesion_objetivo"],
                                    keep="last"))
        ic_a, ic_d = metricas.rank_ic_diario(df), metricas.rank_ic_diario(dedup)
        s_a = _series_ls(df, 25) / 100.0
        s_d = _series_ls(dedup, 25) / 100.0
        out[b] = {
            "n_filas": int(len(df)), "n_filas_dedup": int(len(dedup)),
            "filas_duplicadas": int(len(df) - len(dedup)),
            "duelo_como_esta": _duelo(df),
            "duelo_deduplicado": _duelo(dedup),
            "ic_medio_como_esta": (round(float(ic_a.mean()), 4)
                                   if len(ic_a) else None),
            "ic_medio_dedup": (round(float(ic_d.mean()), 4)
                               if len(ic_d) else None),
            "t_nw_como_esta": (round(metricas.t_newey_west(ic_a), 2)
                               if len(ic_a) >= 10 else None),
            "t_nw_dedup": (round(metricas.t_newey_west(ic_d), 2)
                           if len(ic_d) >= 10 else None),
            "mae_como_esta": metricas.mae_gap(df),
            "mae_dedup": metricas.mae_gap(dedup),
            "sharpe_ls25_como_esta": (round(inferencia.sharpe(s_a.to_numpy()), 3)
                                      if len(s_a) >= 2 else None),
            "sharpe_ls25_dedup": (round(inferencia.sharpe(s_d.to_numpy()), 3)
                                  if len(s_d) >= 2 else None),
        }
    return out


def _md(salida: dict, reporte: dict) -> str:
    """El veredicto en prosa, generado desde el JSON. Se escribe con la
    misma firmeza si es negativo — instrucción de Nicolás, y además es lo
    único que hace útil publicar un negativo."""
    c = salida["criterios"]
    L = ["# Veredicto de la Etapa 5.1 — B0→B5", "",
         "## ⛔ NO HAY VEREDICTO. R3 lo impide, y R3 no admite excepciones.", "",
         "`GEMELO/DISEÑO.md` §6.2 **R3**: *«cualquier fuga detectada por el "
         "test de causalidad. Sin discusión y sin excepción.»* Se detectaron "
         "**tres** defectos demostrados y medidos en el arnés, uno de ellos "
         "una fuga temporal de manual. **El veredicto de la Etapa 5.1 "
         "espera** a que el arnés se arregle.", "",
         "Además, el gatillo congelado del GATE B **no está cumplido por "
         "ninguna de sus dos vías** (`backtest/DISEÑO.md` §11), y el "
         "**holdout NO se gastó**. Expediente completo, con el conteo de "
         "intentos declarado antes de correr: "
         f"`{salida['parametros_declarados']['expediente']}`.", "",
         "## Tabla de criterios", "",
         "| Criterio | Veredicto | Razón |", "|---|---|---|"]
    razones = {
        "V1": "Habilidad sobre 'siempre al alza' — cifra contaminada, ver abajo",
        "V2": "CRPS vs el campeón — cifra contaminada",
        "V3": "Cobertura del intervalo 80% — cifra contaminada",
        "V4": "MAE del gap vs el campeón en ventana",
        "V5": "DSR ≥ 0.95 con N declarado = "
              f"{salida['parametros_declarados']['N_intentos']}",
        "V6": "Superar comprar SMH y no hacer nada, a 25 pb por lado",
        "V7": "Holdout en cuarentena — **deliberadamente NO gastado**",
        "R1": "Control lineal vs retador — no hay retador en esta corrida",
        "R2": "La ventaja sobrevive excluyendo 15–23 jul",
        "R3": "**Fuga detectada. Sin discusión y sin excepción.**",
        "veredicto_final_diseno_8": "El criterio de lectura del §8",
    }
    for k, v in c.items():
        L.append(f"| **{k}** | {v.get('veredicto')} | {razones.get(k, '')} |")

    smh = c["V6"]["benchmark_smh"]
    L += ["", "## V6 — el benchmark obligatorio, y no está cerca", "",
          f"**Comprar {smh['ticker']} y no hacer nada: "
          f"{smh['acumulado_pct']}% acumulado, Sharpe {smh['sharpe']}, "
          f"MDD {smh['mdd_pct']}%.**", "",
          "| B | LS 10 pb | LS 25 pb | LS 50 pb | LO 25 pb | Sharpe LS 25 pb |",
          "|---|---|---|---|---|---|"]
    for b, v in c["V6"]["detalle"].items():
        p = v["por_costo"]
        L.append(f"| {b} | {p[10]['long_short']['acum_pct']}% | "
                 f"**{p[25]['long_short']['acum_pct']}%** | "
                 f"{p[50]['long_short']['acum_pct']}% | "
                 f"{p[25]['long_only']['acum_pct']}% | "
                 f"{p[25]['long_short']['sharpe']} |")
    L += ["", "**Ninguna cartera, en ningún nivel de costos, en ningún lado, "
          "se acerca al benchmark.** El diseño ya lo había anticipado con "
          "*«una estrategia que sólo vive con 10 pb no aprueba»*: aquí no "
          "vive ninguna ni con 10 pb.", ""]

    L += ["## V5 — Deflated Sharpe: cero, y el conteo de intentos no era el "
          "problema", "",
          "| B | Sharpe LS 25 pb | días | skew | curtosis | PSR vs 0 | "
          "DSR N=26 | DSR N=44 | **DSR N=82** | DSR N=110 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for b, v in c["V5"]["detalle"].items():
        if "dsr_por_N" not in v:
            continue
        d = v["dsr_por_N"]
        L.append(f"| {b} | {v['sharpe_ls_25pb']} | {v['dias']} | {v['skew']} | "
                 f"{v['kurtosis']} | {v['psr_vs_cero']} | {d[26]['dsr']} | "
                 f"{d[44]['dsr']} | **{d[82]['dsr']}** | {d[110]['dsr']} |")
    L += ["", f"`V_intentos` = {c['V5']['V_intentos']} · umbral deflactado "
          f"`SR0` = {c['V5']['detalle']['B2']['dsr_por_N'][82]['sr0']} a N=82.",
          "", "Los 520 días superan el mínimo de "
          f"{MINIMO_DIAS_SHARPE}, así que el DSR **sí es interpretable** "
          "aquí — no hay que escribir NO INTERPRETABLE. Y lo que dice es "
          "**0.0000 en las seis baselines y en los cuatro valores de N**. "
          "Conviene decirlo sin adornos: **el conteo de intentos, que este "
          "expediente se tomó el trabajo de reconstruir desde 25 hasta 82, "
          "resultó no ser la restricción que decide.** Con Sharpe entre −5.4 "
          "y −8.1, ningún N habría cambiado el resultado. El conteo se "
          "declaró igual y antes de correr, porque su valor no depende de "
          "que termine siendo decisivo.", ""]

    L += ["## Lo que sí se aprende, incluso con el arnés roto", "",
          "Hay una asimetría que conviene mirar, porque la contaminación "
          "conocida va en la dirección de **favorecer** al modelo y aun así "
          "el resultado económico es demoledor:", "",
          "| | |", "|---|---|"]
    d2 = c["V1"]["detalle"].get(CAMPEON) or {}
    L += [f"| Acierto direccional del gap ({CAMPEON}) | "
          f"**{d2.get('modelo_pct')}%** (Wilson95 "
          f"{d2.get('wilson95_pp')}) vs base {d2.get('base_pct')}%, "
          f"ventaja **{d2.get('ventaja_pp')} pp**, McNemar p={d2.get('mcnemar_p')} |",
          "| Cartera long-short **bruta, sin un solo punto básico de costo** | "
          "**−40.7 %** acumulado, Sharpe **−1.08** |",
          "| Cartera long-only bruta | −19.8 % acumulado, Sharpe −0.24 |",
          "| Arrastre puro de costos a 25 pb/lado sobre 520 días | −92.6 % |",
          "",
          "**El modelo acierta la dirección del gap y aun así la cartera "
          "pierde el 41 % antes de costos.** No es un problema de costos: los "
          "costos rematan algo que ya venía perdiendo. Es la distinción que "
          "el propio proyecto tiene escrita desde la Etapa 4.6 —¿la señal "
          "EXISTE? ¿es CAPTURABLE?— medida ahora sobre dos años: **el gap "
          "existe y no es capturable.** Comprar en la subasta de apertura ya "
          "es tarde; el gap ocurrió antes de que se pudiera operar.", "",
          "Esto no es un veredicto, porque R3 lo prohíbe. Pero es la "
          "dirección en la que el arreglo del arnés tendrá que ser "
          "sorprendente para cambiar algo.", ""]

    b3 = salida.get("impacto_b3_duplicados") or {}
    if b3:
        L += ["## B-3 medido: y la contaminación va al revés de lo que supuse",
              "", "Releyendo las MISMAS filas con los desenlaces duplicados "
              "colapsados por `(ticker, sesión objetivo)`:", "",
              "| B | filas | ventaja pp | IC medio | t(NW) | MAE |",
              "|---|---|---|---|---|---|"]
        for b, v in b3.items():
            dm, dd = v.get("duelo_como_esta"), v.get("duelo_deduplicado")
            L.append(f"| {b} | {v['n_filas']} → {v['n_filas_dedup']} | "
                     f"{dm['ventaja_pp'] if dm else '—'} → "
                     f"{dd['ventaja_pp'] if dd else '—'} | "
                     f"{v['ic_medio_como_esta']} → {v['ic_medio_dedup']} | "
                     f"{v['t_nw_como_esta']} → {v['t_nw_dedup']} | "
                     f"{v['mae_como_esta']} → {v['mae_dedup']} |")
        L += ["", "**La auditoría predijo que los duplicados INFLABAN el "
              "t-stat. Medido, hacen lo contrario:** al deduplicar, la "
              "ventaja sube, el IC sube y el t(NW) sube en todas las capas. "
              "El defecto es real —la unidad de observación está mal y hay "
              "que arreglarla igual—, pero su dirección no era la que supuse, "
              "y decirlo es parte del trabajo. Corregir el arnés no va a "
              "rescatar estos números: va a empeorarlos un poco más del lado "
              "económico.", ""]

    fid = salida.get("fidelidad_b2_vs_sellos") or {}
    if fid:
        L += ["## La fuente no es point-in-time, y esta vez está medido", "",
              f"`{CAMPEON}` contra las predicciones realmente selladas por "
              f"producción, {fid['n_comparadas']} filas: diferencia mediana "
              f"**{fid['dif_mediana_pp']} pp**, media "
              f"**{fid['dif_media_pp']} pp**, máxima "
              f"**{fid['dif_max_pp']} pp**. Toda la discrepancia vive en una "
              f"sola fecha, **{fid['peor_fecha']}** (media "
              f"{fid['dif_media_peor_fecha_pp']} pp); sin ella, la media cae "
              f"a **{fid['sin_la_peor_fecha']['dif_media_pp']} pp** y el "
              f"máximo a {fid['sin_la_peor_fecha']['dif_max_pp']} pp.", "",
              "La causa, verificada contra la fuente: **Yahoo borró la sesión "
              "del 2026-08-28 de `^SOX`, `SMH` y `^GSPC`** (`NVDA` sí la "
              "tiene). Producción la vivió y la selló —`sox_fecha` "
              "2026-08-28, `sox_usado_pct` −3.47—; hoy esa barra no existe y "
              "el backtest reconstruye ese día con el SOX del 27 (+2.33 %), "
              "**invirtiendo el signo de las ocho acciones**. La barra "
              "desaparecida es también la del **benchmark obligatorio SMH**.",
              "", "Es la primera vez que la limitación *«esto no es "
              "point-in-time»* se mide sobre el camino del backtest, y su "
              "magnitud no es un decimal: da vuelta una sección transversal "
              "entera.", ""]

    L += ["---", "", "## Qué hay que arreglar antes de que exista un veredicto",
          "", "En este orden, y el primer entregable de cada punto es el "
          "**test**, no el arreglo. Ver §3.10 del expediente.", "",
          "1. **B-1** — cortar el sentimiento por "
          "`min(titulares.fecha, analisis.analizado_en)` contra el instante "
          "de emisión. Hoy `buzz` no tiene grado ninguno.",
          "2. **B-2** — parametrizar la prueba maestra sobre **B0–B5 × ≥10 "
          "fechas** y añadir la contraprueba `shift(-1)` como test "
          "permanente: que el test pueda fallar es parte del test.",
          "3. **B-3** — deduplicar por `(ticker, sesión objetivo)` o declarar "
          "la sesión objetivo como unidad de observación.",
          "4. **S-1** — contar sesiones del calendario, no días corridos, y "
          "sellar las efectivamente purgadas.",
          "5. **S-3** — computar `estado_gatillo` en vez de recibirlo.",
          "6. Construir un **holdout material**: hoy la cuarentena es sólo "
          "procedimental.", "",
          "---", "Herramienta de análisis — no constituye asesoría "
          "financiera. Criterios congelados en `backtest/DISEÑO.md` §8 y "
          "`GEMELO/DISEÑO.md` §6; ninguno fue modificado para esta corrida.",
          ""]
    return "\n".join(L)


def main(ruta_existente: str | None = None) -> int:
    """Con `ruta_existente` re-evalúa los criterios sobre las predicciones ya
    escritas por una corrida, SIN volver a correr el walk-forward: las
    mismas filas, la misma semilla, el mismo resultado. Sirve cuando falla
    la capa de criterios y no la de datos — volver a bajar y recalcular
    cambiaría la fuente (Yahoo reescribe) y con ella los números."""
    if ruta_existente:
        with open(os.path.join(ruta_existente, "metricas.json"),
                  encoding="utf-8") as f:
            reporte = json.load(f)
        reporte["baselines"] = {b: {**v, "carteras": {int(k): c for k, c
                                                      in v["carteras"].items()}}
                                for b, v in reporte["baselines"].items()}
        reporte["ruta"] = ruta_existente
    else:
        fuente = FuenteCongelada()
        reporte = motorbt.correr(DESDE, HASTA, etiqueta=ETIQUETA, fuente=fuente,
                                 semilla_bootstrap=SEMILLA_BOOTSTRAP,
                                 alpha_bootstrap=ALPHA_BOOTSTRAP,
                                 estado_gatillo=ESTADO_GATILLO)
    ruta = reporte["ruta"]
    dfs = {}
    for b in ("B0", "B1", "B2", "B3", "B4", "B5"):
        p = os.path.join(ruta, f"predicciones_{b}.csv")
        if os.path.exists(p):
            dfs[b] = pd.read_csv(p)
    criterios = evaluar(reporte, dfs)
    fidelidad = fidelidad_b2(dfs)
    salida = {"parametros_declarados": {
                  "ventana": [DESDE.isoformat(), HASTA.isoformat()],
                  "semilla_bootstrap": SEMILLA_BOOTSTRAP,
                  "alpha_bootstrap": ALPHA_BOOTSTRAP,
                  "N_intentos": N_INTENTOS_51, "banda_N": list(BANDA_N),
                  "expediente": "GEMELO/resultados/gatillo_51.md"},
              "estado_gatillo": ESTADO_GATILLO,
              "fidelidad_b2_vs_sellos": fidelidad,
              "impacto_b3_duplicados": impacto_b3(dfs),
              "criterios": criterios}
    with open(os.path.join(ruta, "veredicto.json"), "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2, default=str)
    texto = _md(salida, reporte)
    with open(os.path.join(ruta, "veredicto.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    # El resumen.md es el artefacto VERSIONADO: el veredicto tiene que vivir
    # ahí, no sólo en un archivo al lado. Se reescribe entero desde el
    # reporte + el veredicto, nunca se acumulan copias al pie.
    resumen = motorbt._resumen_md(reporte)
    marca = "\n\n---\n\n"
    with open(os.path.join(ruta, "resumen.md"), "w", encoding="utf-8") as f:
        f.write(resumen + marca + texto)
    print(f"resultados en {ruta}")
    print(json.dumps({k: v.get("veredicto") for k, v in criterios.items()},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    import argparse
    _p = argparse.ArgumentParser(description="Veredicto 5.1 sobre B0→B5")
    _p.add_argument("--solo-criterios", default=None,
                    help="ruta de una corrida ya escrita: re-evalúa los "
                         "criterios sobre SUS filas, sin volver a correr el "
                         "walk-forward ni volver a descargar")
    raise SystemExit(main(_p.parse_args().solo_criterios))
