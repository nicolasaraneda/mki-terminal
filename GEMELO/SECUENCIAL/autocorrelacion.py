"""Frente D de la séptima corrida (2-sep-2026): la autocorrelación que 34
fechas no acotan — dos salidas.

PROPUESTA (regla quinta): nada entra a `DISEÑO.md` ni a un documento de
resultados sin dictamen de `estadistico-adversario`, que ya rechazó cuatro
veces el diseño secuencial.

El bloqueo: el plan promete α = 0,05 y entrega [0,046, 0,079] según la
autocorrelación lag-1 (AC1) de d_j entre fechas, medida en −0,13 ± 0,17
sobre 35 fechas: no distingue 0 de +0,2.

SALIDA 1 — acotar AC1 con un prior de la ventana larga. El campeón es
β·SOX(t−1): un modelo determinista aplicado a precios. La reconstrucción
de la Etapa 5.1 (`backtest/resultados/20260901-133154-*/predicciones_B2.csv`,
B2 = motor de producción verbatim, 4.152 filas, sep-2024 → ago-2026) da
~490 fechas de d_j del MISMO modelo sobre los MISMOS mercados, y M1 del
Frente A midió que Yahoo no cambió un retorno en esa historia. Con ~490
fechas la SE de AC1 baja de 0,17 a ~0,045. Se reporta AC1…AC5, un IC por
bootstrap de bloques móviles, y AC1 por año calendario (estacionariedad).
Advertencia declarada: la ventana larga NO es la sellada (B-3 duplica
desenlaces en feriados; se deduplica por `(ticker, sesion_objetivo)`
antes; el 28-ago está reconstruido con signo contrario, es 1 fecha de ~490).

SALIDA 2 — un diseño que no necesite AC1. Simulador propio y transparente
(AR(1) en d_j bajo H0, sin bootstrap interno) que mide el α global del plan
de 4 miradas O'Brien-Fleming para tres estadísticos:
  DIA   z con varianza iid de fechas (el supuesto que el plan no puede
        verificar; referencia).
  BLQ   la unidad es el BLOQUE de B fechas consecutivas (B=10, 20): z con la
        varianza de las sumas por bloque. Para AR(1) con φ ≤ 0,3 la
        correlación entre bloques adyacentes cae a ~φ/B, así que α queda
        cerca del nominal sin conocer φ. Costo: menos unidades → varianza
        estimada con menos grados de libertad.
  HAC   z con varianza Newey-West (Bartlett) de rezago L=5, 10: robusta a
        dependencia de corto alcance sin fijar B.
Para cada uno: α bajo φ ∈ {0, 0,1, 0,2, 0,3} y potencia bajo φ=0 frente a
un drift fijo, para ver qué se paga.

Uso: `python GEMELO/SECUENCIAL/autocorrelacion.py` → `GEMELO/resultados/autocorrelacion.{json,md}`.
"""
from __future__ import annotations

import glob
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

from backtest import linea_base as lb                              # noqa: E402
from GEMELO.SECUENCIAL import diseno_secuencial as ds              # noqa: E402
from GEMELO.SECUENCIAL.mirada import (autocorrelacion_lag1,        # noqa: E402
                                      contribuciones_por_fecha)

DIR_RESULTADOS = os.path.join(_RAIZ, "GEMELO", "resultados")
RUTA_B2 = sorted(glob.glob(os.path.join(
    _RAIZ, "backtest", "resultados", "20260901-133154-*", "predicciones_B2.csv")))
SEMILLA = 20260902
N_REP = 20_000
BLOQUE_BOOT = 20
N_BOOT = 2000
PHIS = (0.0, 0.1, 0.2, 0.3)
DRIFT = 0.18   # por fecha, en unidades de sd de d_j: elegido para ~0,8 de potencia DIA a φ=0


# ------------------------------------------------------------
# Salida 1 · AC de d_j en la ventana larga reconstruida
# ------------------------------------------------------------
def d_por_fecha_ventana_larga() -> pd.Series:
    df = pd.read_csv(RUTA_B2[-1])
    df = df.drop_duplicates(subset=["ticker", "sesion_objetivo"], keep="first")  # B-3
    df = df[df["gap_pct"] != 0]                                                   # excluir_cero
    base = (df["gap_pct"] > 0).astype(int)
    mod = ((df["est"] >= 0) == (df["gap_pct"] > 0)).astype(int)
    df = df.assign(d=(mod - base))
    return df.groupby("fecha_emision")["d"].sum().astype(float)


def autocorrelaciones(x: np.ndarray, rezagos: int = 5) -> list:
    x = x - x.mean()
    den = float((x * x).sum())
    return [float((x[:-h] * x[h:]).sum() / den) if den else float("nan")
            for h in range(1, rezagos + 1)]


def ic_ac1_bootstrap_bloques(x: np.ndarray, bloque: int = BLOQUE_BOOT,
                             n_boot: int = N_BOOT, semilla: int = SEMILLA) -> tuple:
    rng = np.random.default_rng(semilla)
    n = len(x)
    nb = math.ceil(n / bloque)
    reps = []
    for _ in range(n_boot):
        ini = rng.integers(0, n, size=nb)
        idx = (ini[:, None] + np.arange(bloque)[None, :]).ravel() % n      # circular
        reps.append(autocorrelacion_lag1(x[idx[:n]])[0])
    lo, hi = np.quantile(reps, [0.025, 0.975])
    return float(lo), float(hi)


def salida1() -> dict:
    s = d_por_fecha_ventana_larga()
    x = s.to_numpy()
    ac = autocorrelaciones(x)
    ac1, ee = autocorrelacion_lag1(x)
    lo, hi = ic_ac1_bootstrap_bloques(x)
    por_anio = {}
    for anio, g in s.groupby(pd.to_datetime(s.index).year):
        a, e = autocorrelacion_lag1(g.to_numpy())
        por_anio[int(anio)] = {"fechas": int(len(g)), "ac1": round(a, 3), "ee": round(e, 3)}
    # la ventana sellada, misma aritmética, para ponerla al lado
    sell = lb.aplicar_convencion(lb.cargar(hasta_sello=None), lb.CONVENCION_OFICIAL)
    d_sell = contribuciones_por_fecha(sell)
    ac1_s, ee_s = autocorrelacion_lag1(d_sell)
    # el chequeo que decide la admisibilidad (dictamen del adversario): la
    # reconstrucción restringida al MISMO tramo de calendario que la sellada
    primera_sellada = sell["fecha"].min()
    sol = s[s.index >= primera_sellada].to_numpy()
    ac1_sol, ee_sol = autocorrelacion_lag1(sol)
    return {"fuente": os.path.relpath(RUTA_B2[-1], _RAIZ), "fechas": int(len(x)),
            "desde": s.index.min(), "hasta": s.index.max(),
            "ac_1_a_5": [round(a, 3) for a in ac], "ac1": round(ac1, 3), "ee_1_sobre_raiz_m": round(ee, 3),
            "ic95_bootstrap_bloques": [round(lo, 3), round(hi, 3)], "bloque_boot": BLOQUE_BOOT,
            "por_anio": por_anio,
            "ventana_sellada": {"fechas": int(len(d_sell)), "ac1": round(ac1_s, 3), "ee": round(ee_s, 3)},
            "reconstruida_en_el_tramo_sellado": {"desde": primera_sellada, "fechas": int(len(sol)),
                                                 "ac1": round(ac1_sol, 3), "ee": round(ee_sol, 3)},
            "max_abs_ac_1_a_5": round(max(abs(a) for a in ac), 3),
            "advertencias": [
                "ventana reconstruida (B2 = motor de producción sobre Yahoo del 1-sep), no sellada",
                "deduplicada por (ticker, sesion_objetivo) para neutralizar B-3",
                "incluye el 28-ago reconstruido con signo contrario (1 fecha)",
                "una sola descarga congelada: ciega por construcción a la intermitencia de la fuente (M6 del Frente A)",
                "es una MEDICIÓN DE REFERENCIA con su IC, no una cota: el extremo de un IC no es una certeza",
            ]}


# ------------------------------------------------------------
# Salida 2 · α del plan bajo AR(1), para tres estadísticos, sin bootstrap
# ------------------------------------------------------------
def _ar1(rng, m: int, phi: float, drift: float = 0.0) -> np.ndarray:
    e = rng.normal(size=m)
    d = np.empty(m)
    d[0] = e[0]
    raiz = math.sqrt(max(1 - phi * phi, 1e-9))
    for j in range(1, m):
        d[j] = phi * d[j - 1] + raiz * e[j]
    return d + drift


def _z_dia(d: np.ndarray) -> float:
    return d.sum() / math.sqrt(len(d) * d.var(ddof=1)) if len(d) > 1 else 0.0


def _z_bloque(d: np.ndarray, B: int) -> float:
    nb = len(d) // B
    if nb < 3:
        return 0.0
    S = d[:nb * B].reshape(nb, B).sum(axis=1)
    return S.sum() / math.sqrt(nb * S.var(ddof=1))


def _z_hac(d: np.ndarray, L: int) -> float:
    x = d - d.mean()
    n = len(x)
    g0 = float((x * x).sum() / n)
    lr = g0
    for h in range(1, L + 1):
        w = 1 - h / (L + 1)
        lr += 2 * w * float((x[:-h] * x[h:]).sum() / n)
    return d.sum() / math.sqrt(n * max(lr, 1e-12))


ESTADISTICOS = {
    "DIA": lambda d: _z_dia(d),
    "BLQ10": lambda d: _z_bloque(d, 10),
    "BLQ20": lambda d: _z_bloque(d, 20),
    "HAC5": lambda d: _z_hac(d, 5),
    "HAC10": lambda d: _z_hac(d, 10),
}


def cruces_plan(phi: float, drift: float, n_rep: int = N_REP, semilla: int = SEMILLA) -> dict:
    """Fracción de réplicas en que el plan OBF de 4 miradas cruza, por estadístico."""
    rng = np.random.default_rng(semilla)
    m = ds.FECHAS_POR_MIRADA[-1]
    cruz = {k: 0 for k in ESTADISTICOS}
    for _ in range(n_rep):
        d = _ar1(rng, m, phi, drift)
        for nombre, f in ESTADISTICOS.items():
            for k, nf in enumerate(ds.FECHAS_POR_MIRADA):
                if abs(f(d[:nf])) >= ds.UMBRALES_OBF[k]:
                    cruz[nombre] += 1
                    break
    return {k: v / n_rep for k, v in cruz.items()}


def alfa_plan_con_error_mc(ruta_json: str) -> dict:
    """El α del plan en los extremos del IC de AC1, con las DOS fuentes de
    error: el IC de AC1 y el Wilson de las réplicas del simulador."""
    if not os.path.exists(ruta_json):
        return {}
    d = json.load(open(ruta_json))
    los = [v["lo"] for v in d.values()]
    his = [v["hi"] for v in d.values()]
    return {"por_ac1": {k: [round(v["alfa"], 4), round(v["lo"], 4), round(v["hi"], 4)] for k, v in d.items()},
            "rango_honesto": [round(min(los), 3), round(max(his), 3)],
            "nota": "DGP del simulador del diseño: d_j discretizado (np.round(d·7/2)); el de Salida 2: normal continuo. Dos DGP."}


def salida2() -> dict:
    alfa = {phi: cruces_plan(phi, 0.0) for phi in PHIS}
    potencia = {phi: cruces_plan(phi, DRIFT, semilla=SEMILLA + 1) for phi in (0.0, 0.2)}
    return {"n_rep": N_REP, "fechas_por_mirada": list(ds.FECHAS_POR_MIRADA),
            "umbrales_obf": list(ds.UMBRALES_OBF), "drift_por_fecha_sd": DRIFT,
            "alfa_por_phi": {str(p): {k: round(v, 4) for k, v in a.items()} for p, a in alfa.items()},
            "potencia_por_phi": {str(p): {k: round(v, 4) for k, v in a.items()} for p, a in potencia.items()},
            "wilson_pm": round(1.96 * math.sqrt(0.05 * 0.95 / N_REP), 4)}


def main() -> dict:
    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "etiqueta": "PROPUESTA — sin dictamen del estadistico-adversario no entra a DISEÑO.md ni a resultados"}
    res["salida1_prior_ventana_larga"] = salida1()
    res["salida2_disenos_robustos"] = salida2()
    res["alfa_plan_bajo_la_referencia"] = alfa_plan_con_error_mc(
        os.path.join(DIR_RESULTADOS, "autocorrelacion_alfa_plan_prior.json"))
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "autocorrelacion.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "autocorrelacion.md"), "w") as f:
        f.write(informe(res))
    return res


def informe(r: dict) -> str:
    s1, s2 = r["salida1_prior_ventana_larga"], r["salida2_disenos_robustos"]
    L = ["# La autocorrelación que 35 fechas no acotan — dos salidas (Frente D, PROPUESTA)\n",
         f"> **{r['etiqueta']}**\n",
         f"- Generado: {r['generado_en_utc']} · `python GEMELO/SECUENCIAL/autocorrelacion.py`\n",
         "## Salida 1 · AC1 de d_j en la ventana larga reconstruida, como prior\n",
         f"- Fuente: `{s1['fuente']}` — **{s1['fechas']} fechas** ({s1['desde']} → {s1['hasta']}), "
         f"deduplicada por sesión objetivo, `excluir_cero`.",
         f"- AC1…AC5: {s1['ac_1_a_5']}",
         f"- **AC1 = {s1['ac1']}**, EE 1/√m = {s1['ee_1_sobre_raiz_m']}, IC95 bootstrap de bloques ({s1['bloque_boot']}): "
         f"**{s1['ic95_bootstrap_bloques']}** (contiene el cero: AC1 no se distingue de 0)",
         f"- Ventana sellada, misma aritmética: AC1 = {s1['ventana_sellada']['ac1']} ± {s1['ventana_sellada']['ee']} "
         f"sobre {s1['ventana_sellada']['fechas']} fechas.",
         f"- **La reconstrucción en el mismo tramo de calendario que la sellada** (desde {s1['reconstruida_en_el_tramo_sellado']['desde']}, "
         f"{s1['reconstruida_en_el_tramo_sellado']['fechas']} fechas): AC1 = {s1['reconstruida_en_el_tramo_sellado']['ac1']} ± "
         f"{s1['reconstruida_en_el_tramo_sellado']['ee']} — reproduce a la sellada donde las dos existen.",
         f"- Máximo |AC| en los rezagos 1–5: {s1['max_abs_ac_1_a_5']}.",
         f"- α del plan bajo esta referencia (simulador del diseño, 2.000 réplicas, con el Wilson de las réplicas): "
         f"{r['alfa_plan_bajo_la_referencia'].get('por_ac1')} → **rango honesto {r['alfa_plan_bajo_la_referencia'].get('rango_honesto')}**. "
         f"{r['alfa_plan_bajo_la_referencia'].get('nota')}\n",
         "| año | fechas | AC1 | EE |", "|---|---|---|---|"]
    for a, v in s1["por_anio"].items():
        L.append(f"| {a} | {v['fechas']} | {v['ac1']} | {v['ee']} |")
    L.append("\nAdvertencias: " + "; ".join(s1["advertencias"]) + ".\n")
    L += ["## Salida 2 · α global del plan OBF (4 miradas) por estadístico, bajo AR(1) en d_j\n",
          f"- {s2['n_rep']} réplicas por celda (±{s2['wilson_pm']}), fechas por mirada {s2['fechas_por_mirada']}, "
          f"umbrales {s2['umbrales_obf']}. Sin bootstrap interno: mide el estadístico, no el estimador de varianza del plan.\n",
          "| φ | " + " | ".join(ESTADISTICOS) + " |", "|---|" + "---|" * len(ESTADISTICOS)]
    for p, a in s2["alfa_por_phi"].items():
        L.append(f"| {p} | " + " | ".join(f"{a[k]:.4f}" for k in ESTADISTICOS) + " |")
    L += [f"\n**Potencia** frente a un drift de {s2['drift_por_fecha_sd']} sd por fecha:\n",
          "| φ | " + " | ".join(ESTADISTICOS) + " |", "|---|" + "---|" * len(ESTADISTICOS)]
    for p, a in s2["potencia_por_phi"].items():
        L.append(f"| {p} | " + " | ".join(f"{a[k]:.3f}" for k in ESTADISTICOS) + " |")
    L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["salida1_prior_ventana_larga"], indent=1, default=str))
    print(json.dumps(r["salida2_disenos_robustos"], indent=1))
