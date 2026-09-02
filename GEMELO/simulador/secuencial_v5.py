"""Frente F de la octava corrida: plan secuencial v5 con características
operativas SIMULADAS sobre el generador calibrado del Frente A.

Pre-registro: `GEMELO/preregistro/secuencial_v5.md` (miradas fijas en
fechas selladas, estadístico por fecha con varianza re-estimada, gasto de
α Lan-DeMets con forma O'Brien-Fleming, fronteras por simulación bajo H0).

Uso: `python GEMELO/simulador/secuencial_v5.py` →
`GEMELO/resultados/secuencial_v5.{json,md}`.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone

import numpy as np

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from backtest import linea_base as lb                       # noqa: E402
from backtest.inferencia import Phi, Phi_inv                # noqa: E402
from GEMELO import bifurcaciones as bf                      # noqa: E402
from GEMELO.simulador import proceso as pr                  # noqa: E402

DIR_RESULTADOS = os.path.join(_RAIZ, "GEMELO", "resultados")
SEMILLA = 20260902
ALFA = 0.05
MIRADAS = (50, 100, 150, 200, 250)
N_REP_FRONTERAS = 20000
N_REP_POTENCIA = 4000
DELTAS = (0.09, 0.065, 0.05)
PHIS = (0.0, 0.1, 0.2, 0.3)


def gasto_obf(t: float, alfa: float = ALFA) -> float:
    """Lan-DeMets con forma de O'Brien-Fleming, bilateral."""
    return 2 - 2 * Phi(Phi_inv(1 - alfa / 2) / math.sqrt(t))


def _contribuciones(p, n_dias, rng, phi=0.0):
    """S_j por fecha (Σ_i acierto_modelo − acierto_base) de una ventana
    simulada. Con φ > 0 se induce autocorrelación entre fechas mezclando el
    shock S_d con un AR(1): S_d ← φ·S_{d−1} + √(1−φ²)·S_d (misma marginal)."""
    df = pr.simular(p, n_dias, rng)
    if phi > 0:
        # re-simular con S autocorrelado: se aplica sobre el factor del día
        # modificando las contribuciones no es válido; se re-genera el panel
        # con un S filtrado. Para mantener el generador calibrado se filtra
        # la serie S y se recomputa gap/pred con las mismas innovaciones.
        S = df.groupby("dia")["sox"].first().to_numpy()
        e = np.empty_like(S); e[0] = S[0]
        for j in range(1, len(S)):
            e[j] = phi * e[j - 1] + math.sqrt(1 - phi * phi) * S[j]
        esc = e[df["dia"].to_numpy()] / np.where(S[df["dia"].to_numpy()] == 0, 1e-12, S[df["dia"].to_numpy()])
        # gap = mu + beta*(b*S + c*U) + idio; la parte b*beta*S se reescala por esc
        beta = df["ticker"].map(p.beta).to_numpy()
        parte_S = beta * p.b * df["sox"].to_numpy()
        df["gap_pct"] = df["gap_pct"] - parte_S + parte_S * esc
        df["apertura_estimada_pct"] = df["apertura_estimada_pct"] * esc
        df["acierto_gap"] = ((df["apertura_estimada_pct"] >= 0) == (df["gap_pct"] >= 0)).astype(int)
    d = df[df["gap_pct"] != 0]
    dif = (d["acierto_gap"] - (d["gap_pct"] > 0).astype(int)).to_numpy(float)
    return np.bincount(d["dia"].to_numpy(), weights=dif, minlength=n_dias)


def _z(S: np.ndarray) -> float:
    k = len(S)
    s2 = S.var(ddof=1)
    return float(S.sum() / math.sqrt(k * s2)) if s2 > 0 else 0.0


def trayectorias_z(p, n_rep, phi=0.0, semilla=SEMILLA, con_ac1=False):
    """Trayectorias del z por mirada. Con `con_ac1` devuelve también el AC1
    REALIZADO de las contribuciones diarias y la fracción de fechas que
    contribuyen exactamente cero (dictamen F: el filtro φ sobre el factor de
    día NO se transmite a las contribuciones, porque cuando el SOX sube el
    modelo y la baseline coinciden y el día contribuye 0)."""
    rng = np.random.default_rng(semilla)
    Z = np.empty((n_rep, len(MIRADAS)))
    ac1, ceros = [], []
    for r in range(n_rep):
        S = _contribuciones(p, MIRADAS[-1], rng, phi)
        for i, k in enumerate(MIRADAS):
            Z[r, i] = _z(S[:k])
        if con_ac1:
            if S.std() > 0:
                ac1.append(float(np.corrcoef(S[:-1], S[1:])[0, 1]))
            ceros.append(float((S == 0).mean()))
    if con_ac1:
        return Z, {"ac1_realizado_medio": round(float(np.mean(ac1)), 4), "fraccion_fechas_contribucion_cero": round(float(np.mean(ceros)), 3)}
    return Z


def fronteras_por_simulacion(Z0: np.ndarray) -> list:
    """Frontera c_k tal que la probabilidad de cruzar POR PRIMERA VEZ en la
    mirada k bajo H0 sea α(t_k) − α(t_{k−1}), sobre las trayectorias nulas
    simuladas (bisección sobre el cuantil condicional)."""
    n = len(Z0)
    vivas = np.ones(n, dtype=bool)
    c = []
    gastado = 0.0
    for i, k in enumerate(MIRADAS):
        objetivo = gasto_obf(k / MIRADAS[-1]) - gastado
        # entre las trayectorias vivas, el umbral que deja cruzar exactamente objetivo·n
        z_vivas = np.abs(Z0[vivas, i])
        m = int(round(objetivo * n))
        if m <= 0:
            ck = float("inf")
        else:
            ck = float(np.sort(z_vivas)[::-1][m - 1]) if m <= len(z_vivas) else 0.0
        cruzan = vivas & (np.abs(Z0[:, i]) >= ck)
        gastado += cruzan.sum() / n
        vivas &= ~cruzan
        c.append(ck)
    return c


def caracteristicas(Z: np.ndarray, c: list) -> dict:
    n = len(Z)
    vivas = np.ones(n, dtype=bool)
    por_mirada, n_decision = [], np.full(n, MIRADAS[-1], dtype=float)
    for i, k in enumerate(MIRADAS):
        cruzan = vivas & (np.abs(Z[:, i]) >= c[i])
        n_decision[cruzan] = k
        por_mirada.append(int(cruzan.sum()))
        vivas &= ~cruzan
    tot = sum(por_mirada)
    lo, hi = lb._wilson(tot, n)
    return {"rechazo_total": round(tot / n, 4), "ic95": [round(lo / 100, 4), round(hi / 100, 4)],
            "rechazo_por_mirada": [round(x / n, 4) for x in por_mirada],
            "acumulado_por_mirada": [round(sum(por_mirada[:i + 1]) / n, 4) for i in range(len(MIRADAS))],
            "n_esperado_fechas": round(float(n_decision.mean()), 1)}


def main() -> dict:
    base = pr.calibrar_desde_sellado()
    df_real = lb.aplicar_convencion(lb.cargar(hasta_sello=lb.CORTE_REGLA_FIRMADA), lb.CONVENCION_OFICIAL)
    vals = (df_real["acierto_gap"] - df_real["base_acierto"]).to_numpy(float)
    icc = bf.icc_y_deff(bf._por_dia(df_real, vals))["icc"]
    p0 = pr.calibrar(base, 0.0, icc)
    Z0 = trayectorias_z(p0, N_REP_FRONTERAS)
    c = fronteras_por_simulacion(Z0)
    # referencia EXTERNA (la que el v5 había abandonado y el rechazo #1 exige):
    # O'Brien-Fleming K = 5 por la recursión de Armitage (GEMELO/SECUENCIAL/fronteras.py)
    try:
        from GEMELO.SECUENCIAL import fronteras as fr
        fracs = [k / MIRADAS[-1] for k in MIRADAS]
        externa = [round(float(x), 3) for x in fr.frontera_obf(fracs, alpha=ALFA)[1]]
    except Exception as exc:  # pragma: no cover
        externa = f"no disponible: {exc}"
    # contribuciones selladas: AC1 y fracción de fechas con contribución cero
    S_real = np.array([g.sum() for g in bf._por_dia(df_real, vals)])
    ac1_real = float(np.corrcoef(S_real[:-1], S_real[1:])[0, 1])
    ceros_real = float((S_real == 0).mean())
    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "etiqueta": "PROPUESTA — Frente F, octava corrida; pendiente de dictamen (lee los cuatro rechazos)",
           "parametros": {"alfa": ALFA, "miradas_fechas": list(MIRADAS), "gasto": "Lan-DeMets O'Brien-Fleming, bilateral",
                          "gasto_acumulado_nominal": [round(gasto_obf(k / MIRADAS[-1]), 4) for k in MIRADAS],
                          "n_rep_fronteras": N_REP_FRONTERAS, "n_rep_potencia": N_REP_POTENCIA, "semilla": SEMILLA,
                          "icc_calibrado": round(icc, 4), "generador_nulo": {"b": round(p0.b, 4), "c": round(p0.c, 4)}},
           "fronteras_z": [round(x, 3) for x in c],
           "fronteras_obf_externa_armitage": externa,
           "nota_fronteras": ("la mirada 1 tiene c = ∞ por RESOLUCIÓN, no por diseño: α₁ = 1,2e−5 sobre 20.000 réplicas son 0,2 cruces "
                              "esperados → el plan tiene CUATRO miradas efectivas, no cinco; la frontera de la mirada 2 se apoya en ~38 cruces, "
                              "así que los IC de tipo I y potencia son CONDICIONALES a una frontera con error de Monte Carlo no propagado; "
                              "tres de las cuatro fronteras finitas quedan por DEBAJO de la referencia externa gaussiana con colas t(4)"),
           "estadistico": ("z gaussiano sobre la suma de contribuciones diarias con varianza muestral: es un estadístico NUEVO, distinto de la "
                           "permutación de signo por día que gobierna la ventana sellada y que el Frente A calibró; cuenta como intento"),
           "contribuciones_selladas": {"fechas": int(len(S_real)), "ac1": round(ac1_real, 4), "fraccion_contribucion_cero": round(ceros_real, 3)},
           "tipo_I": {"phi_0.0_AJUSTE_no_medicion_(mismas_trayectorias_que_las_fronteras)": caracteristicas(Z0, c)},
           "potencia": {}}
    # tipo I FUERA de muestra: semillas independientes, agrupado
    fuera, tot, n_tot = [], 0, 0
    for i, sem in enumerate((SEMILLA + 101, SEMILLA + 202)):
        Zf = trayectorias_z(p0, 10000, semilla=sem)
        car = caracteristicas(Zf, c); fuera.append({"semilla": sem, **car})
        tot += round(car["rechazo_total"] * 10000); n_tot += 10000
    lo, hi = lb._wilson(tot, n_tot)
    res["tipo_I"]["phi_0.0_FUERA_DE_MUESTRA"] = {"por_semilla": fuera, "agrupado": round(tot / n_tot, 4), "ic95": [round(lo / 100, 4), round(hi / 100, 4)], "n": n_tot}
    # sensibilidad a φ CON control φ = 0 al mismo protocolo y AC1 realizado
    res["sensibilidad_phi"] = {}
    for phi in PHIS:
        Zp, diag = trayectorias_z(p0, 6000, phi=phi, semilla=SEMILLA + 3, con_ac1=True)
        res["sensibilidad_phi"][f"phi_{phi}"] = {**caracteristicas(Zp, c), **diag}
    res["lectura_phi"] = ("el AC1 realizado de las contribuciones NO sigue a φ (queda ≈ 0): el eje es inerte porque ~la mitad de las fechas "
                          "contribuyen exactamente cero (modelo = baseline cuando el SOX sube). El control φ = 0 al mismo protocolo contiene a las "
                          "filas φ > 0: la tabla es cuatro corridas de la misma nula, NO una medición de dependencia. El plan sigue SIN evidencia "
                          "de que controla α bajo dependencia; la banda firmada [0,046, 0,079] queda intacta")
    for dlt in DELTAS:
        q = pr.calibrar(base, dlt, icc)
        Z1 = trayectorias_z(q, N_REP_POTENCIA, semilla=SEMILLA + 7)
        res["potencia"][f"{dlt}"] = {"b": round(q.b, 4), "c": round(q.c, 4), **caracteristicas(Z1, c)}
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "secuencial_v5.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "secuencial_v5.md"), "w") as f:
        f.write(informe(res))
    return res


def informe(r: dict) -> str:
    p = r["parametros"]
    L = ["# Plan secuencial v5 — características operativas simuladas (Frente F, PROPUESTA)\n",
         f"> **{r['etiqueta']}** · generado {r['generado_en_utc']} · `python GEMELO/simulador/secuencial_v5.py`\n",
         f"Pre-registro: `GEMELO/preregistro/secuencial_v5.md`. Miradas a {p['miradas_fechas']} fechas selladas; gasto {p['gasto']}, "
         f"acumulado nominal {p['gasto_acumulado_nominal']}; fronteras derivadas por simulación bajo H0 con el generador calibrado "
         f"(ICC {p['icc_calibrado']}, b = {p['generador_nulo']['b']}, c = {p['generador_nulo']['c']}), {p['n_rep_fronteras']} réplicas: "
         f"**c_k = {r['fronteras_z']}**.\n",
         "## Tipo I (rechazo bajo H0), total y por mirada\n",
         "| autocorrelación entre fechas φ | rechazo total | IC95 | por mirada | acumulado |", "|---|---|---|---|---|"]
    for k, v in r["tipo_I"].items():
        if "rechazo_total" not in v:          # la fila fuera de muestra (agrupado por semillas)
            L.append(f"| {k} | **{v['agrupado']}** | {v['ic95']} | por semilla: {[x['rechazo_total'] for x in v['por_semilla']]} | n = {v['n']} |")
            continue
        L.append(f"| {k} | **{v['rechazo_total']}** | {v['ic95']} | {v['rechazo_por_mirada']} | {v['acumulado_por_mirada']} |")
    L += ["", f"**Referencia externa (O'Brien-Fleming K = 5, recursión de Armitage, `GEMELO/SECUENCIAL/fronteras.py`): c_k = {r['fronteras_obf_externa_armitage']}** contra las simuladas {r['fronteras_z']}.",
          f"- {r['nota_fronteras']}.", f"- Estadístico: {r['estadistico']}.",
          f"- Tipo I FUERA de muestra (semillas independientes, agrupado n = {r['tipo_I']['phi_0.0_FUERA_DE_MUESTRA']['n']}): **{r['tipo_I']['phi_0.0_FUERA_DE_MUESTRA']['agrupado']}** {r['tipo_I']['phi_0.0_FUERA_DE_MUESTRA']['ic95']}. La fila «AJUSTE» de arriba NO es una medición: es la definición del ajuste.",
          "", "## Sensibilidad a φ, con control φ = 0 al mismo protocolo y AC1 REALIZADO", "",
          "| φ | rechazo total | IC95 | AC1 realizado de las contribuciones | fracción de fechas con contribución 0 |", "|---|---|---|---|---|"]
    for k, v in r["sensibilidad_phi"].items():
        L.append(f"| {k} | {v['rechazo_total']} | {v['ic95']} | **{v['ac1_realizado_medio']}** | {v['fraccion_fechas_contribucion_cero']} |")
    cs = r["contribuciones_selladas"]
    L += ["", f"**Lectura:** {r['lectura_phi']}. En la ventana sellada: AC1 = {cs['ac1']} y **{100*cs['fraccion_contribucion_cero']:.0f}% de las {cs['fechas']} fechas contribuyen exactamente cero** — más de la mitad de las fechas selladas no aportan información al estadístico direccional, porque el campeón y la baseline coinciden por construcción cuando el SOX sube. Eso explica por qué la dirección necesita ~250 días y la magnitud ~100.",
          "", "**Conclusión (dictamen F, quinto rechazo):** el plan reproduce pero se verifica contra sí mismo (rechazo #1, reintroducido); vuelve a `cola_decisiones.md`, no entra a `espera_firma.md`. Intentos: **2** (el diseño y el estadístico nuevo).",
          "\n## Potencia por mirada y n esperado hasta decisión\n",
          "| δ verdad | rechazo total (potencia) | IC95 | por mirada | acumulado | fechas esperadas |", "|---|---|---|---|---|---|"]
    for k, v in r["potencia"].items():
        L.append(f"| {float(k) * 100:.1f} pp | **{v['rechazo_total']}** | {v['ic95']} | {v['rechazo_por_mirada']} | {v['acumulado_por_mirada']} | {v['n_esperado_fechas']} |")
    L.append("")
    return "\n".join(L) + "\n"


def solo_informe() -> dict:
    with open(os.path.join(DIR_RESULTADOS, "secuencial_v5.json")) as f:
        r = json.load(f)
    if isinstance(r.get("fronteras_obf_externa_armitage"), str):      # recomputar la referencia externa (aritmética, no simulación)
        from GEMELO.SECUENCIAL import fronteras as fr
        fracs = [k / MIRADAS[-1] for k in MIRADAS]
        r["fronteras_obf_externa_armitage"] = [round(float(x), 3) for x in fr.frontera_obf(fracs, alpha=ALFA)[1]]
        with open(os.path.join(DIR_RESULTADOS, "secuencial_v5.json"), "w") as f:
            json.dump(r, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "secuencial_v5.md"), "w") as f:
        f.write(informe(r))
    return r


if __name__ == "__main__":
    if "--solo-informe" in sys.argv:
        solo_informe(); sys.exit(0)
    r = main()
    print(json.dumps({"fronteras": r["fronteras_z"], "tipo_I": r["tipo_I"], "potencia": r["potencia"]}, indent=1, default=str))
