"""Frente B de la séptima corrida (2-sep-2026): ¿es medible en principio?

La pregunta, en forma decidible: dado el proceso generador REAL de la
ventana sellada —8 tickers por día, clúster de día con ICC ≈ 0,4, cadencia
de ~0,9 sellos por día hábil— ¿existe un horizonte de acumulación en el que
un efecto del tamaño que importa (8–9 pp de relevancia; 6,5 pp; 5 pp del
umbral de `RELEVO.md`) sea detectable con potencia 0,80 al α = 0,05 del
estadístico PRINCIPAL del proyecto (el que respeta el clúster de día)?

Dos rutas, para que la respuesta no dependa de una:

  (1) Analítica: el error estándar del estadístico de día escala como
      1/√D en el número de días D. Se estima SE en los D observados por
      bootstrap de días enteros (`bifurcaciones._bootstrap_dia`) y se
      extrapola. Supone que los días son intercambiables (AC1 ≈ 0; la
      medida es −0,13 ± 0,17, ver `diseno_secuencial.ac1_ventana_antecedente`).
  (2) Simulación: remuestrea DÍAS ENTEROS de los residuos observados hasta
      D días, suma el efecto δ y aplica el test de permutación de signo por
      día (`bifurcaciones._p_permutacion_dia`). No supone normalidad ni
      tamaños de clúster iguales: usa los de verdad.

Las dos usan las MISMAS filas que la cifra publicada bajo la regla firmada
(`backtest.linea_base.cargar(hasta_sello=CORTE_REGLA_FIRMADA)`,
`excluir_cero`), con el instante pinchado para que reproduzca mañana.

Lo que este script NO puede responder, y lo dice: si el efecto es
ESTACIONARIO en el horizonte que calcula. Con un solo régimen sellado
(`regimen` toma un único valor en la ventana), un modelo congelado y una
fuente que muta, «D días más» sólo mide un efecto que no cambió en el
camino. Eso no es una limitación del cálculo: es la limitación del
instrumento, y es la respuesta a la pregunta dura.

Uso: `python GEMELO/SECUENCIAL/horizonte.py` → `GEMELO/resultados/horizonte.{json,md}`.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, datetime, timezone

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
CORTE = lb.CORTE_REGLA_FIRMADA          # 2026-08-31, pinchado
CONVENCION = lb.CONVENCION_OFICIAL      # excluir_cero (§2.8, congelada)
ALFA = 0.05
POTENCIA = 0.80
SEMILLA = 20260902
DELTAS_PP = (5.0, 6.5, 9.0, 12.0)
HORIZONTES_DIAS = (35, 73, 125, 250, 500, 750, 1000)
N_SIM = 3000        # 300 en la primera corrida: el α empírico salió 0,083 y era ruido de MC; el dictamen exige ≥ 3.000
N_PERM = 800
FACTOR_OBF = 1.0241 # gasto de α del plan secuencial, DISEÑO.md §A3.3 (no 3–5%: 2,4%)
# Cadencia observada: fechas selladas por día hábil (ver
# diseno_secuencial.FECHAS_POR_DIA_HABIL = 35/39). Se recalcula acá desde
# los datos, no se copia.
DIAS_HABILES_ANIO = 252


def cargar_grupos() -> tuple:
    df = lb.aplicar_convencion(lb.cargar(hasta_sello=CORTE), CONVENCION)
    d = (df["acierto_gap"] - df["base_acierto"]).to_numpy(dtype=float)
    grupos = bf._por_dia(df, d)
    return df, grupos


def _z(p: float) -> float:
    return Phi_inv(p)


def potencia_analitica(delta: float, se: float, alfa: float = ALFA) -> float:
    """Potencia bilateral de un test z con efecto `delta` y error estándar `se`."""
    z = _z(1 - alfa / 2)
    return Phi(delta / se - z) + Phi(-delta / se - z)


def dias_para_potencia(delta: float, se_obs: float, k_obs: int,
                       potencia: float = POTENCIA, alfa: float = ALFA) -> float:
    """Días D tales que SE(D) = SE_obs·√(k/D) da la potencia pedida."""
    zt = _z(1 - alfa / 2) + _z(potencia)
    return k_obs * (zt * se_obs / delta) ** 2


def mde_a(dias: float, se_obs: float, k_obs: int,
          potencia: float = POTENCIA, alfa: float = ALFA) -> float:
    zt = _z(1 - alfa / 2) + _z(potencia)
    return zt * se_obs * math.sqrt(k_obs / dias)


def ic_se_dia(grupos: list, n_ext: int = 300, n_int: int = 1000,
              semilla: int = SEMILLA) -> tuple:
    """IC95 del propio SE de día, por bootstrap anidado (regla 3 de la casa:
    el MDE y los «días para potencia» se derivan del SE, así que heredan su
    incertidumbre y hay que computarla, no suponerla). Devuelve
    (se_lo, se_hi) en fracción."""
    k = len(grupos)
    sumas = np.array([g.sum() for g in grupos], dtype=float)
    cuentas = np.array([len(g) for g in grupos], dtype=float)
    rng = np.random.default_rng(semilla + 11)
    ses = []
    for _ in range(n_ext):
        idx = rng.integers(0, k, size=k)
        s_, c_ = sumas[idx], cuentas[idx]
        idx2 = rng.integers(0, k, size=(n_int, k))
        reps = s_[idx2].sum(axis=1) / c_[idx2].sum(axis=1)
        ses.append(reps.std(ddof=1))
    lo, hi = np.quantile(ses, [0.025, 0.975])
    return float(lo), float(hi)


def potencia_simulada(grupos: list, delta: float, D: int, n_sim: int = N_SIM,
                      n_perm: int = N_PERM, semilla: int = SEMILLA) -> float:
    """Remuestrea D días enteros de los residuos centrados, suma `delta`
    (fracción) y aplica el test de permutación de signo por día."""
    todo = np.concatenate(grupos)
    cent = [g - todo.mean() for g in grupos]
    k = len(cent)
    rng = np.random.default_rng(semilla)
    rech = 0
    for i in range(n_sim):
        idx = rng.integers(0, k, size=D)
        muestra = [cent[j] + delta for j in idx]
        # semilla distinta por réplica: con la fija, 300 réplicas compartían
        # una sola matriz de signos (dictamen del adversario, 2-sep)
        if bf._p_permutacion_dia(muestra, n_perm, semilla=semilla + 1000 * i + D) < ALFA:
            rech += 1
    return rech / n_sim


def _wilson(k: int, n: int) -> list:
    from backtest.linea_base import _wilson as w
    lo, hi = w(k, n)
    return [round(lo / 100, 3), round(hi / 100, 3)]


def fecha_a_dias(D: float, k_obs: int, primera: str, ultima: str) -> str:
    """Fecha de calendario en que se acumulan D fechas selladas, a la cadencia
    observada (fechas selladas por día hábil entre `primera` y `ultima`)."""
    habiles = len(pd.bdate_range(primera, ultima))
    cadencia = k_obs / habiles
    faltan_habiles = max(0.0, (D - k_obs) / cadencia)
    return (pd.Timestamp(ultima) + pd.offsets.BDay(int(round(faltan_habiles)))).date().isoformat()


def mitades(df: pd.DataFrame, grupos: list) -> dict:
    """La misma ventaja en la primera y la segunda mitad de los días, con IC de
    día: el chequeo mínimo de estacionariedad que 35 días permiten."""
    k = len(grupos)
    h = k // 2
    out = {}
    for nombre, sub in (("primera_mitad", grupos[:h]), ("segunda_mitad", grupos[h:])):
        p, lo, hi = bf._bootstrap_dia(sub, n_boot=4000)
        out[nombre] = {"dias": len(sub), "filas": int(sum(len(g) for g in sub)),
                       "ventaja_pp": round(100 * p, 2),
                       "ic95_pp": [round(100 * lo, 2), round(100 * hi, 2)]}
    return out


def main() -> dict:
    df, grupos = cargar_grupos()
    k = len(grupos)
    n = int(sum(len(g) for g in grupos))
    duelo = lb.duelo(df)
    punto, lo, hi = bf._bootstrap_dia(grupos, n_boot=10_000)
    se_obs = (hi - lo) / (2 * _z(0.975))          # SE implícito del IC de día
    icc = bf.icc_y_deff(grupos)
    primera, ultima = df["fecha"].min(), df["fecha"].max()
    habiles = len(pd.bdate_range(primera, ultima))
    cadencia = k / habiles
    regimenes = sorted(df["regimen"].dropna().unique().tolist())

    res = {
        "generado_en_utc": datetime.now(timezone.utc).isoformat(),
        "ancla": {"hasta_sello": CORTE, "convencion": CONVENCION, "n": n, "dias": k,
                  "primera": primera, "ultima": ultima, "dias_habiles_en_ventana": habiles,
                  "cadencia_sellos_por_dia_habil": round(cadencia, 3),
                  "ventaja_pp": round(100 * punto, 2),
                  "ic95_dia_pp": [round(100 * lo, 2), round(100 * hi, 2)],
                  "se_dia_pp": round(100 * se_obs, 2),
                  "duelo": duelo, "icc_deff": {kk: (round(v, 4) if isinstance(v, float) else v)
                                              for kk, v in icc.items()},
                  "info_efectiva_por_dia": round(icc["n_efectivo"] / k, 2),
                  "regimenes_en_ventana": regimenes},
        "parametros": {"alfa": ALFA, "potencia": POTENCIA, "semilla": SEMILLA,
                       "n_sim": N_SIM, "n_perm": N_PERM, "deltas_pp": list(DELTAS_PP),
                       "horizontes_dias": list(HORIZONTES_DIAS)},
    }

    # el SE de día tiene su propio intervalo (bootstrap anidado); todo lo que
    # se deriva de él —días para potencia, MDE— lo hereda
    se_lo, se_hi = ic_se_dia(grupos)
    res["ancla"]["ic95_se_dia_pp"] = [round(100 * se_lo, 2), round(100 * se_hi, 2)]

    # (1) analítica: días y fecha para cada δ, con el intervalo heredado del SE
    ana = []
    for dpp in DELTAS_PP:
        D = dias_para_potencia(dpp / 100, se_obs, k)
        D_lo = dias_para_potencia(dpp / 100, se_lo, k)
        D_hi = dias_para_potencia(dpp / 100, se_hi, k)
        ana.append({"delta_pp": dpp, "dias_sellados": round(D),
                    "ic95_dias_sellados": [round(D_lo), round(D_hi)],
                    "anios_de_sellado": round(D / (cadencia * DIAS_HABILES_ANIO), 2),
                    "fecha_estimada": fecha_a_dias(D, k, primera, ultima),
                    "ic95_fecha": [fecha_a_dias(D_lo, k, primera, ultima),
                                   fecha_a_dias(D_hi, k, primera, ultima)],
                    "potencia_hoy": round(potencia_analitica(dpp / 100, se_obs), 3)})
    res["analitica"] = ana

    # MDE al 80% en horizontes de referencia, con intervalo
    mdes = []
    for D in HORIZONTES_DIAS:
        mdes.append({"dias": D, "fecha_estimada": fecha_a_dias(D, k, primera, ultima),
                     "mde80_pp": round(100 * mde_a(D, se_obs, k), 1),
                     "ic95_mde80_pp": [round(100 * mde_a(D, se_lo, k), 1),
                                       round(100 * mde_a(D, se_hi, k), 1)],
                     "mde50_pp": round(100 * mde_a(D, se_obs, k, potencia=0.50), 1)})
    res["mde_por_horizonte"] = mdes

    # (2) simulación: potencia por (δ, D), con δ = 0 como control de α; cada
    # fracción lleva su Wilson (n_sim réplicas)
    sim = []
    for D in HORIZONTES_DIAS:
        a = potencia_simulada(grupos, 0.0, D)
        fila = {"dias": D, "alfa_empirico": a, "alfa_ic95": _wilson(round(a * N_SIM), N_SIM)}
        for dpp in DELTAS_PP:
            p = potencia_simulada(grupos, dpp / 100, D)
            fila[f"potencia_{dpp}pp"] = p
            fila[f"potencia_{dpp}pp_ic95"] = _wilson(round(p * N_SIM), N_SIM)
        sim.append(fila)
    res["simulacion"] = sim

    # cadencia con intervalo (Wilson sobre sellos / días hábiles) y su efecto
    # sobre la fecha de los 9 pp; el calendario usa días hábiles genéricos
    # (`BDay`), no feriados de bolsa: ±2 meses de holgura adicional
    cad_lo, cad_hi = [x / 100 for x in lb._wilson(k, habiles)]
    D9 = dias_para_potencia(0.09, se_obs, k)
    res["cadencia"] = {"sellos_por_dia_habil": round(cadencia, 3), "wilson95": [round(cad_lo, 3), round(cad_hi, 3)],
                       "fecha_9pp_con_cadencia_alta": (pd.Timestamp(ultima) + pd.offsets.BDay(int((D9 - k) / cad_hi))).date().isoformat(),
                       "fecha_9pp_con_cadencia_baja": (pd.Timestamp(ultima) + pd.offsets.BDay(int((D9 - k) / cad_lo))).date().isoformat(),
                       "gasto_alfa_secuencial_factor": FACTOR_OBF,
                       "dias_9pp_con_gasto_secuencial": round(D9 * FACTOR_OBF)}

    # R2 sobre este mismo ancla: excluir el bloque 15–23 jul (criterio
    # congelado de rechazo, GEMELO/DISEÑO.md §6.2). El adversario lo cazó:
    # «las mitades» eran R2 con otro nombre.
    d_r2 = lb.duelo_excluyendo(df, "2026-07-15", "2026-07-23")
    fuera = df[(df["fecha"] < "2026-07-15") | (df["fecha"] > "2026-07-23")]
    dd = (fuera["acierto_gap"] - fuera["base_acierto"]).to_numpy(dtype=float)
    g2 = bf._por_dia(fuera, dd)
    p2, lo2, hi2 = bf._bootstrap_dia(g2, n_boot=10_000)
    res["R2_excluyendo_15_23_jul"] = {
        "n": d_r2["n"], "ventaja_pp": d_r2["ventaja_pp"], "mcnemar_filas_p": d_r2["mcnemar_p"],
        "b": d_r2["mcnemar_b01"], "c": d_r2["mcnemar_b10"],
        "ic95_dia_pp": [round(100 * lo2, 2), round(100 * hi2, 2)],
        "permutacion_dia_p": round(bf._p_permutacion_dia(g2, 4000), 4),
        "lectura": "R2 DISPARA sobre este ancla: sin el bloque 1 la ventaja no se distingue de cero por ninguna ruta"}

    # estacionariedad mínima
    res["mitades"] = mitades(df, grupos)

    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "horizonte.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "horizonte.md"), "w") as f:
        f.write(informe(res))
    return res


def informe(r: dict) -> str:
    a = r["ancla"]
    L = ["# ¿Es medible en principio? — Frente B (séptima corrida)\n",
         f"- Generado: {r['generado_en_utc']} · `python GEMELO/SECUENCIAL/horizonte.py`",
         f"- Ancla: `hasta_sello = {a['hasta_sello']}`, `{a['convencion']}` → **n = {a['n']} en {a['dias']} días** "
         f"({a['primera']} → {a['ultima']}, {a['dias_habiles_en_ventana']} días hábiles, "
         f"cadencia {a['cadencia_sellos_por_dia_habil']} sellos/día hábil)",
         f"- Ventaja {a['ventaja_pp']} pp, IC95 de día {a['ic95_dia_pp']} (contiene el cero), SE de día **{a['se_dia_pp']} pp** "
         f"(IC95 del SE, bootstrap anidado: {a['ic95_se_dia_pp']}); "
         f"ICC {a['icc_deff']['icc']}, DEFF {a['icc_deff']['deff']}, n efectivo {a['icc_deff']['n_efectivo']} "
         f"→ **{a['info_efectiva_por_dia']} observaciones efectivas por día sellado**",
         f"- Regímenes presentes en la ventana: {a['regimenes_en_ventana']}\n",
         "## Ruta 1 · analítica (SE ∝ 1/√días)\n",
         "| efecto | días sellados (IC95) | años de sellado | fecha estimada (IC95) | potencia hoy |", "|---|---|---|---|---|"]
    for x in r["analitica"]:
        L.append(f"| **{x['delta_pp']} pp** | {x['dias_sellados']} {x['ic95_dias_sellados']} | {x['anios_de_sellado']} | "
                 f"{x['fecha_estimada']} [{x['ic95_fecha'][0]}, {x['ic95_fecha'][1]}] | {x['potencia_hoy']} |")
    L += ["\n## MDE por horizonte\n", "| días | fecha | MDE 80% (IC95) | MDE 50% |", "|---|---|---|---|"]
    for x in r["mde_por_horizonte"]:
        L.append(f"| {x['dias']} | {x['fecha_estimada']} | **{x['mde80_pp']} pp** {x['ic95_mde80_pp']} | {x['mde50_pp']} pp |")
    L += ["\n## Ruta 2 · simulación (días reales remuestreados, permutación de signo por día)\n",
          "| días | α empírico (δ=0) | " + " | ".join(f"δ={d} pp" for d in r["parametros"]["deltas_pp"]) + " |",
          "|---|---|" + "---|" * len(r["parametros"]["deltas_pp"])]
    for x in r["simulacion"]:
        L.append(f"| {x['dias']} | {x['alfa_empirico']:.3f} {x['alfa_ic95']} | " +
                 " | ".join(f"{x[f'potencia_{d}pp']:.2f} {x[f'potencia_{d}pp_ic95']}" for d in r["parametros"]["deltas_pp"]) + " |")
    r2 = r["R2_excluyendo_15_23_jul"]
    L += [f"\n## R2 sobre este ancla (excluir 15–23 jul, criterio congelado)\n",
          f"- n = {r2['n']}, ventaja **{r2['ventaja_pp']} pp**, IC95 de día {r2['ic95_dia_pp']} (contiene el cero), "
          f"McNemar de filas p = {r2['mcnemar_filas_p']} (b = {r2['b']}, c = {r2['c']}), permutación de día p = {r2['permutacion_dia_p']}. **{r2['lectura']}.**",
          f"- Cadencia {r['cadencia']['sellos_por_dia_habil']} sellos/día hábil, Wilson {r['cadencia']['wilson95']}: la fecha de los 9 pp va de "
          f"{r['cadencia']['fecha_9pp_con_cadencia_alta']} a {r['cadencia']['fecha_9pp_con_cadencia_baja']} por cadencia sola; con el gasto de α del plan "
          f"secuencial (×{r['cadencia']['gasto_alfa_secuencial_factor']}, DISEÑO.md §A3.3) son {r['cadencia']['dias_9pp_con_gasto_secuencial']} días."]
    m = r["mitades"]
    L += ["\n## Estacionariedad mínima: las dos mitades de la ventana (ojo: el bloque 1 de R2 está entero en la primera)\n",
          "| mitad | días | filas | ventaja | IC95 de día |", "|---|---|---|---|---|"]
    for kk, v in m.items():
        L.append(f"| {kk} | {v['dias']} | {v['filas']} | {v['ventaja_pp']} pp | {v['ic95_pp']} |")
    L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["ancla"], indent=1, ensure_ascii=False, default=str))
    for x in r["analitica"]:
        print(x)
    for x in r["simulacion"]:
        print(x)
    print(r["mitades"])
