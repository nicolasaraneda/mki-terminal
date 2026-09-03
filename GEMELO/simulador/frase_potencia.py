"""Frase de potencia del veredicto 5.1 en dos versiones (dirección y magnitud),
cada una con n, intervalo y fecha estimada de veredicto — encargo 09, 1b y 3c.

PROPUESTA. Lee de la máquina, no de la bitácora:
  - `GEMELO/resultados/horizonte.json` (ruta 3 = simulador calibrado, la que manda)
  - `GEMELO/resultados/potencia_por_metrica.json` (Frente E v2: DIR / MAE / CRPS
    sobre la ventana sellada bajo la regla firmada, y potencia por horizonte en
    el simulador)
y convierte «días sellados» en fecha de calendario con la cadencia observada
(`horizonte.fecha_a_dias`). El 25-oct-2026 es el gatillo; se dice si la fecha
de potencia 0,80 cae antes o después. Uso:
    python GEMELO/simulador/frase_potencia.py → GEMELO/resultados/corrida09/frase_potencia.md
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)
from GEMELO.SECUENCIAL.horizonte import fecha_a_dias          # noqa: E402

DIR_RES = os.path.join(_RAIZ, "GEMELO", "resultados")
GATILLO = "2026-10-25"
DIAS_GATILLO = 73          # horizonte de referencia del 25-oct en los dos instrumentos


def _interp_dias(horizontes, potencias, objetivo=0.80):
    """Primer cruce de `objetivo` interpolando en log(D)."""
    h = np.array(horizontes, float); p = np.array(potencias, float)
    for i in range(1, len(h)):
        if p[i - 1] < objetivo <= p[i]:
            x0, x1 = np.log(h[i - 1]), np.log(h[i])
            return float(np.exp(x0 + (objetivo - p[i - 1]) * (x1 - x0) / (p[i] - p[i - 1])))
    return float("inf") if p[-1] < objetivo else float(h[0])


def main() -> dict:
    with open(os.path.join(DIR_RES, "horizonte.json")) as f:
        H = json.load(f)
    with open(os.path.join(DIR_RES, "potencia_por_metrica.json")) as f:
        E = json.load(f)
    a = H["ancla"]; k, primera, ultima = a["dias"], a["primera"], a["ultima"]
    fecha = lambda D: fecha_a_dias(D, k, primera, ultima) if D != float("inf") and D is not None else "∞"

    out = {"fuentes": {"horizonte": H["generado_en_utc"], "potencia_por_metrica": E["generado_utc"] if "generado_utc" in E else E.get("generado_en_utc")},
           "ancla": {"hasta_sello": a["hasta_sello"], "n": a["n"], "dias": k, "ventaja_pp": a["ventaja_pp"], "ic95_dia_pp": a["ic95_dia_pp"],
                     "cadencia": a["cadencia_sellos_por_dia_habil"]}}

    # --- DIRECCIÓN: ruta 3 del horizonte (simulador calibrado), δ = 9 y 6,5 pp ---
    sc = H["simulador_calibrado"]
    pot73 = next(x for x in sc["potencia"] if x["dias"] == DIAS_GATILLO)
    d80 = sc["dias_para_0_80"]
    out["direccion"] = {
        "potencia_25oct": {d: [pot73[f"potencia_{d}pp"], pot73[f"potencia_{d}pp_ic95"]] for d in ("9.0", "6.5", "5.0")},
        "dias_para_0_80": {d: {"dias": d80[d]["dias"], "rango_mc": d80[d]["ic_mc"], "rango_semillas": d80[d]["rango_semillas"], "fecha": d80[d].get("fecha_estimada"), "fecha_rango_mc": d80[d].get("fecha_rango_mc")} for d in d80},
        "observado_ruta_E": E["sellada"]["DIR"],
    }
    # --- MAGNITUD: Frente E (MAE contra cero, CRPS contra climatología) ---
    sim = E["simulador"]["sigma_pred_sellada"]
    hs = [x["n_dias"] for x in sim]
    mag = {}
    for col in ("MAE", "CRPS"):
        ps = [x[col]["potencia"] for x in sim]
        los = [x[col]["ic95"][0] for x in sim]; his = [x[col]["ic95"][1] for x in sim]
        D = _interp_dias(hs, ps); D_lo = _interp_dias(hs, his); D_hi = _interp_dias(hs, los)
        p73 = next(x for x in sim if x["n_dias"] == DIAS_GATILLO)[col]
        obs = E["sellada"][col]
        mag[col] = {"potencia_25oct_simulador_9pp": [p73["potencia"], p73["ic95"]],
                    "dias_para_0_80_simulador": {"dias": round(D), "ic95": [round(D_lo), round(D_hi) if D_hi != float("inf") else "∞"],
                                                 "fecha": fecha(D), "ic95_fecha": [fecha(D_lo), fecha(D_hi)]},
                    "dias_para_0_80_al_efecto_observado": {"dias": obs["dias_para_0_80_al_efecto_observado"], "ic95": obs["dias_para_0_80_ic95"],
                                                           "fecha": fecha(obs["dias_para_0_80_al_efecto_observado"]),
                                                           "ic95_fecha": [fecha(obs["dias_para_0_80_ic95"][0]), fecha(obs["dias_para_0_80_ic95"][1])]},
                    "efecto_observado": {"punto": obs["punto"], "ic95_t_cluster": obs["ic95"], "z": obs["z"], "dias": obs["dias"]},
                    "banda_73_dias": {kk: v[col] for kk, v in E["simulador"]["banda_potencia_73_dias"].items()},
                    "R2": E["sellada"]["R2_sin_15_23_jul"][col]["dias_para_0_80_al_efecto_observado"]}
    out["magnitud"] = mag
    out["gatillo"] = GATILLO
    os.makedirs(os.path.join(DIR_RES, "corrida09"), exist_ok=True)
    with open(os.path.join(DIR_RES, "corrida09", "frase_potencia.json"), "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RES, "corrida09", "frase_potencia.md"), "w") as f:
        f.write(informe(out))
    return out


def _antes(fecha_str):
    return "ANTES" if fecha_str not in ("∞", None) and fecha_str <= GATILLO else "DESPUÉS"


def informe(o: dict) -> str:
    a = o["ancla"]; d = o["direccion"]; m = o["magnitud"]
    p9, p65 = d["potencia_25oct"]["9.0"], d["potencia_25oct"]["6.5"]
    d9, d65 = d["dias_para_0_80"]["9.0"], d["dias_para_0_80"]["6.5"]
    mae, crps = m["MAE"], m["CRPS"]
    L = ["# La frase de potencia del 5.1, en dos versiones — con n, intervalo y fecha (encargo 09, 1b/3c)\n",
         "> PROPUESTA v2 (dictamen 1b/3c aplicado: sin fecha encabezando; ancla y N declarados). Leída de `horizonte.json` (ruta 3, simulador calibrado) y de "
         "`potencia_por_metrica.json` (Frente E v2). Ancla: cadena local a "
         f"`{a['hasta_sello']}` con la regla de deduplicación firmada, **n = {a['n']} en {a['dias']} días**, ventaja {a['ventaja_pp']} pp, "
         f"IC95 de día {a['ic95_dia_pp']}, cadencia {a['cadencia']} sellos/día hábil. Gatillo: {o['gatillo']} (~{DIAS_GATILLO} días sellados).\n",
         "## Versión «dirección» (V1 congelado; secundaria bajo D3)\n",
         f"> Con ~{DIAS_GATILLO} días sellados el 25-oct, la potencia para detectar una ventaja direccional verdadera de 9 pp es "
         f"**{p9[0]:.2f} {p9[1]}**; de 6,5 pp, **{p65[0]:.2f} {p65[1]}** (simulador calibrado, {a['dias']} días de ancla, n = {a['n']}). "
         f"Para llegar a 0,80 hacen falta **≈{d9['dias']} días sellados** a 9 pp (rango Monte Carlo {d9['rango_mc']}; banda paramétrica de la ruta 1: 248 [109, 370]) → **{d9['fecha']}** {d9['fecha_rango_mc']}, "
         f"y ≈{d65['dias']} (MC {d65['rango_mc']}; ruta 1: 475 [209, 709]) a 6,5 pp → **{d65['fecha']}** {d65['fecha_rango_mc']}. "
         f"Al efecto observado (z de día {d['observado_ruta_E']['z']}) son {d['observado_ruta_E']['dias_para_0_80_al_efecto_observado']} días "
         f"{[x if x != float("inf") else "∞" for x in d["observado_ruta_E"]["dias_para_0_80_ic95"]]}. El veredicto del 25-oct sobre la dirección será, con alta probabilidad, "
         "«no distinguible de cero» aunque la ventaja exista.\n",
         "## Versión «magnitud» (V1-bis propuesta; primaria bajo D3) — v2 tras el dictamen\n",
         f"> Con ~{DIAS_GATILLO} días sellados el 25-oct, la potencia para detectar que el modelo reduce el MAE del gap frente a predecir cero está en la banda "
         f"**{mae['banda_73_dias']['generador_9pp']['potencia']:.2f} / {mae['banda_73_dias']['efecto_observado']['potencia']:.2f} / {mae['banda_73_dias']['efecto_bajo_R2']['potencia']:.2f}** "
         f"(generador de 9 pp {mae['banda_73_dias']['generador_9pp']['ic95']} / efecto observado {mae['banda_73_dias']['efecto_observado']['ic95']} / bajo R2 {mae['banda_73_dias']['efecto_bajo_R2']['ic95']}); "
         f"para el CRPS frente a la climatología **{crps['potencia_25oct_simulador_9pp'][0]:.2f} {crps['potencia_25oct_simulador_9pp'][1]}**. "
         f"Días para potencia 0,80 en MAE **al efecto observado** ({mae['efecto_observado']['punto']:+.3f} pp, IC t de clúster {mae['efecto_observado']['ic95_t_cluster']}: contiene el cero): "
         f"**{mae['dias_para_0_80_al_efecto_observado']['dias']} {mae['dias_para_0_80_al_efecto_observado']['ic95']} → {mae['dias_para_0_80_al_efecto_observado']['fecha']}** "
         f"{mae['dias_para_0_80_al_efecto_observado']['ic95_fecha']}; bajo R2, {mae['R2']} días. Si el efecto fuera el del generador de 9 pp, ≈{mae['dias_para_0_80_simulador']['dias']} días "
         f"(interpolación en log(D), verificada directa 0,80–0,82; sólo Monte Carlo, sin incertidumbre paramétrica). "
         "**Ninguna fecha encabeza:** el 25-oct fija ~73 días, y lo que la muestra dice es la banda de potencia a ese horizonte; una fecha de 0,80 sólo vale condicional al tamaño del efecto, "
         "que hoy tiene un intervalo que contiene el cero.\n",
         "## Lo que hay que saber al firmar\n",
         f"- **Ancla:** los dos instrumentos usan la cadena local a 31-ago (n = {a['n']}, +{a['ventaja_pp']} pp) y NO la ventana canónica del README (28-ago, n = 238, +9,66 pp, `cifras.sellada()`): divergencia declarada, misma regla de deduplicación, tres sellos más.",
         "- **Registro de intentos al escribir esta frase: 310** (`GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO`; `horizonte.md` imprime el N del momento de su corrida).",
         "- La interpolación en log(D) no estaba prefijada: lineal daría ≈61 [57, 65] (dictamen 1b); por eso el «≈58» va sin intervalo y condicional al generador.",
         "- Los «días para 0,80» del simulador miden sólo error de Monte Carlo; la banda paramétrica (SE de día, ICC, b, c) es la de la ruta 1 de `horizonte.md`.",
         "- Las dos versiones se publican juntas y en ese orden, sin la palabra prohibida; ninguna va al README hasta la firma.",
         "- La magnitud contrasta CAMPEÓN contra cero/climatología: no es V2 ni V4 (retador contra campeón). Es lo que la muestra sí hace medible.",
         "- MAE y CRPS son UNA familia (Frente E): con σ_pred ≈ sd_clim casi toda la ganancia de CRPS es la media; no son dos corroboraciones.",
         "- La climatología y σ_pred del Frente E están estimadas EN MUESTRA (sesgo declarado allí); el juez lineal de 3b usa climatología causal.",
         "- Extremo superior ∞ en un intervalo = el IC del efecto contiene el cero.",
         ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    o = main()
    print(informe(o))
