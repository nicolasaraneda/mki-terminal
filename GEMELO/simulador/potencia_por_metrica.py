"""Frente E de la octava corrida: la métrica que maximiza información por día sellado.

PROPUESTA. Con el simulador calibrado (Frente A) y con la ventana sellada,
cuántos días sellados exige detectar, al 80% de potencia y con clúster de
día, el efecto del campeón medido con tres métricas:

  DIR  dirección: d = acierto_modelo − acierto_«siempre al alza» (el
       endpoint congelado; 1 bit por fila).
  MAE  magnitud: m = |g| − |p − g| (cuánto reduce el error absoluto conocer
       p frente a predecir gap cero; lo que publica el README: 2,98 contra
       3,33 pp).
  CRPS densidad: c = CRPS(climatología) − CRPS(modelo), con el modelo como
       N(p, σ_pred) y la climatología como N(media, sd) del gap; σ_pred se
       calibra al ancho medio del `intervalo80_pp` sellado (1,84× más ancho
       de lo necesario, README) y se reporta también con la σ que
       calibraría el modelo.

Para cada métrica, el test es el mismo (permutación de signo de la SUMA
diaria, `bifurcaciones._p_permutacion_dia`), así que la única diferencia
es cuánta señal por día lleva cada una. El simulador da la potencia por
horizonte; la ventana sellada da el z observado de cada métrica y su «días
para 0,80 al efecto observado» (cota inferior optimista, como en E de la
séptima corrida). Uso: `python GEMELO/simulador/potencia_por_metrica.py`.
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

from backtest import linea_base as lb                       # noqa: E402
from backtest.inferencia import Phi_inv                     # noqa: E402
from GEMELO import bifurcaciones as bf                      # noqa: E402
from GEMELO.simulador import proceso as pr                  # noqa: E402

sys.path.insert(0, os.path.join(_RAIZ, ".claude", "skills", "estadistica-evaluacion", "scripts"))
from evaluacion import crps_normal                          # noqa: E402

DIR_RESULTADOS = os.path.join(_RAIZ, "GEMELO", "resultados")
SEMILLA = 20260902
HORIZONTES = (35, 73, 125, 250, 475)
N_REP = 500
N_PERM = 400
Z80 = Phi_inv(0.975) + Phi_inv(0.80)


def metricas_por_fila(df: pd.DataFrame, sigma_pred: float, mu_clim: float, sd_clim: float) -> pd.DataFrame:
    d = df[df["gap_pct"] != 0].copy()
    g, p = d["gap_pct"].to_numpy(float), d["apertura_estimada_pct"].to_numpy(float)
    d["DIR"] = ((p >= 0) == (g > 0)).astype(float) - (g > 0).astype(float)
    d["MAE"] = np.abs(g) - np.abs(p - g)
    d["CRPS"] = crps_normal(g, mu_clim, sd_clim) - crps_normal(g, p, sigma_pred)
    return d


def _p_dia(d: pd.DataFrame, col: str, semilla: int) -> float:
    d = d.copy()
    d["fecha"] = d["dia"] if "dia" in d else d["fecha"]
    g = bf._por_dia(d, d[col].to_numpy(float))
    return bf._p_permutacion_dia(g, N_PERM, semilla=semilla)


def potencia(p, sigma_pred, mu_clim, sd_clim, n_dias, n_rep=N_REP, semilla=SEMILLA) -> dict:
    rng = np.random.default_rng(semilla + n_dias)
    k = {"DIR": 0, "MAE": 0, "CRPS": 0}
    for r in range(n_rep):
        df = pr.simular(p, n_dias, rng)
        d = metricas_por_fila(df, sigma_pred, mu_clim, sd_clim)
        for col in k:
            if _p_dia(d, col, semilla + 97 * r + n_dias) < 0.05:
                k[col] += 1
    out = {"n_dias": n_dias, "n_rep": n_rep}
    for col, v in k.items():
        lo, hi = lb._wilson(v, n_rep)
        out[col] = {"potencia": round(v / n_rep, 3), "ic95": [round(lo / 100, 3), round(hi / 100, 3)]}
    return out


def _dias(k: int, z: float):
    """Días para potencia 0,80 con un z observado sobre k días: k·(Z80/z)²;
    ∞ si z ≤ 0 (el IC del efecto contiene el cero)."""
    return int(round(k * (Z80 / z) ** 2)) if z > 0 else float("inf")


def dias_para_80(d: pd.DataFrame, col: str, n_boot: int = 4000, semilla: int = SEMILLA,
                 efecto_alternativo: float | None = None) -> dict:
    """z de la media de `col` con IC de día por t de CLÚSTER (gl = k−1: el
    estimador que el Frente A midió calibrado; el percentil sub-cubre y
    daba un z ~9% inflado), y días para potencia 0,80 CON INTERVALO: el
    extremo superior es ∞ cuando el IC del efecto contiene el cero. Cota
    inferior optimista, sesgo de ganador declarado. `efecto_alternativo`
    (p. ej. el +6,45 pp publicado en el README para DIR) da los días a ese
    efecto con la misma SE."""
    dd = d.copy()
    dd["fecha"] = dd["fecha"] if "fecha" in dd else dd["dia"]
    g = bf._por_dia(dd, dd[col].to_numpy(float))
    punto, lo, hi = bf._ic_t_cluster(g)
    _, lo_p, hi_p = bf._bootstrap_dia(g, n_boot=n_boot)
    k = len(g)
    tq = bf._t_ppf(0.975, k - 1)
    se = (hi - lo) / (2 * tq)
    z = punto / se if se > 0 else float("nan")
    z_lo, z_hi = lo / se, hi / se
    out = {"punto": round(float(punto), 4), "ic95": [round(float(lo), 4), round(float(hi), 4)],
           "ic95_percentil_dia": [round(float(lo_p), 4), round(float(hi_p), 4)],
           "z": round(float(z), 2), "dias": k,
           "dias_para_0_80_al_efecto_observado": _dias(k, z),
           "dias_para_0_80_ic95": [_dias(k, z_hi), _dias(k, z_lo)],
           "nota": "IC de los días propagado del IC del efecto; ∞ = el IC del efecto contiene el cero"}
    if efecto_alternativo is not None and se > 0:
        out["dias_para_0_80_al_efecto_alternativo"] = {"efecto": efecto_alternativo, "dias": _dias(k, efecto_alternativo / se)}
    return out


def ganancia_mae(q, sigma_pred, mu_clim, sd_clim, n_dias=40000, semilla=SEMILLA + 11) -> float:
    d = metricas_por_fila(pr.simular(q, n_dias, np.random.default_rng(semilla)), sigma_pred, mu_clim, sd_clim)
    return float(d["MAE"].mean())


def calibrar_b_a_mae(base, c_fijo, objetivo_mae, sigma_pred, mu_clim, sd_clim):
    """b tal que la ganancia de MAE del simulador reproduce `objetivo_mae`
    (bisección con c FIJO en el del generador de 9 pp: sólo se mueve la
    información; el generador de 9 pp da ~8% más ganancia que la observada,
    y la potencia se publica a las TRES: generador, observada, R2)."""
    lo, hi = 0.05, 2.0
    for _ in range(18):
        mid = (lo + hi) / 2
        q = pr.Parametros(**{**base.__dict__, "b": mid, "c": c_fijo})
        g = ganancia_mae(q, sigma_pred, mu_clim, sd_clim)
        if g < objetivo_mae:
            lo = mid
        else:
            hi = mid
    return q, g


def main() -> dict:
    sell = lb.aplicar_convencion(lb.cargar(hasta_sello=lb.CORTE_REGLA_FIRMADA), lb.CONVENCION_OFICIAL)
    sigma_pred_sellada = float(sell["intervalo80_pp"].mean() / Phi_inv(0.90))   # σ implícita del intervalo 80%
    mu_clim, sd_clim = float(sell["gap_pct"].mean()), float(sell["gap_pct"].std())
    base = pr.calibrar_desde_sellado()
    df_real = sell
    vals = (df_real["acierto_gap"] - df_real["base_acierto"]).to_numpy(float)
    icc_real = bf.icc_y_deff(bf._por_dia(df_real, vals))["icc"]
    q = pr.calibrar(base, 0.09, icc_real)          # el generador de 9 pp del Frente A
    grande = pr.simular(q, 100_000, np.random.default_rng(SEMILLA + 5))
    dg = metricas_por_fila(grande, sigma_pred_sellada, mu_clim, sd_clim)
    # σ que calibraría al modelo en el simulador: la sd del error p − g
    sigma_calibrada = float((grande["apertura_estimada_pct"] - grande["gap_pct"]).std())

    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "etiqueta": "PROPUESTA — Frente E v2, octava corrida; reescrito tras el dictamen E (NO CONCLUYENTE sobre las cifras operativas)",
           "parametros": {"n_rep": N_REP, "n_perm": N_PERM, "horizontes": list(HORIZONTES), "semilla": SEMILLA,
                          "sigma_pred_sellada_pp": round(sigma_pred_sellada, 3),
                          "sigma_calibrada_en_simulador_pp": round(sigma_calibrada, 3),
                          "climatologia": {"mu": round(mu_clim, 3), "sd": round(sd_clim, 3)},
                          "generador": {"b": round(q.b, 4), "c": round(q.c, 4), "delta_verdad_pp": round(100 * pr.ventaja(grande), 2)}},
           "efecto_verdadero_por_metrica_en_el_simulador": {
               "DIR_pp": round(100 * float(dg["DIR"].mean()), 3),
               "MAE_pp": round(float(dg["MAE"].mean()), 4),
               "MAE_modelo_pp": round(float(np.abs(grande["apertura_estimada_pct"] - grande["gap_pct"]).mean()), 3),
               "MAE_cero_pp": round(float(np.abs(grande["gap_pct"]).mean()), 3),
               "CRPS_pp": round(float(dg["CRPS"].mean()), 4)},
           "sellada": {}}
    # ventana sellada: z observado por métrica y días para 0,80, con intervalo
    ds = metricas_por_fila(sell, sigma_pred_sellada, mu_clim, sd_clim)
    res["sellada"]["ancla"] = "cadena LOCAL a CORTE_REGLA_FIRMADA (31-ago) CON la regla de dedup firmada: +9,3 pp — NO el +6,45 pp publicado (rama sin dedup); hay una tercera rama (+14,3 pp) en cola_decisiones.md §2a-ter"
    res["sellada"]["climatologia_y_sigma_pred"] = "ESTIMADAS EN MUESTRA sobre las mismas filas que puntúan (sesgo: la climatología ajustada en muestra favorece a la baseline; σ_pred sellada favorece al modelo sólo si está calibrada)"
    for col in ("DIR", "MAE", "CRPS"):
        res["sellada"][col] = dias_para_80(ds, col, efecto_alternativo=(0.0645 if col == "DIR" else None))
    res["sellada"]["mae_modelo_pp"] = round(float(sell["error_gap_pp"].mean()), 3)
    res["sellada"]["mae_cero_pp"] = round(float(sell["gap_pct"].abs().mean()), 3)
    res["sellada"]["mae_constante_mu_pp"] = round(float((sell["gap_pct"] - mu_clim).abs().mean()), 3)
    res["sellada"]["fraccion_de_la_ganancia_mae_que_da_la_constante_mu"] = round(
        float((sell["gap_pct"].abs().mean() - (sell["gap_pct"] - mu_clim).abs().mean()) / max(res["sellada"]["MAE"]["punto"], 1e-9)), 3)
    res["sellada"]["nota_familia"] = "CRPS y MAE no son métricas independientes: con σ_pred ≈ sd_clim casi toda la ganancia de CRPS es la media; se reportan como UNA familia (magnitud), no como dos corroboraciones"
    # R2 (criterio congelado): sin el bloque 15–23 jul
    r2 = sell[~((sell["fecha"] >= "2026-07-15") & (sell["fecha"] <= "2026-07-23"))]
    ds_r2 = metricas_por_fila(r2, sigma_pred_sellada, mu_clim, sd_clim)
    res["sellada"]["R2_sin_15_23_jul"] = {col: dias_para_80(ds_r2, col, semilla=SEMILLA + 2) for col in ("DIR", "MAE", "CRPS")}
    # potencia por horizonte en el simulador (σ_pred sellada y calibrada)
    res["simulador"] = {"sigma_pred_sellada": [potencia(q, sigma_pred_sellada, mu_clim, sd_clim, D) for D in HORIZONTES]}
    res["simulador"]["sigma_calibrada"] = [potencia(q, sigma_calibrada, mu_clim, sd_clim, D) for D in (73, 250)]
    # banda de sensibilidad de la potencia de MAE a 73 días: generador (9 pp) / efecto OBSERVADO / efecto bajo R2
    banda = {"generador_9pp": {"ganancia_mae_pp": res["efecto_verdadero_por_metrica_en_el_simulador"]["MAE_pp"],
                               **{k: v for k, v in res["simulador"]["sigma_pred_sellada"][1].items() if k in ("DIR", "MAE", "CRPS")}}}
    for nombre, objetivo in (("efecto_observado", res["sellada"]["MAE"]["punto"]), ("efecto_bajo_R2", res["sellada"]["R2_sin_15_23_jul"]["MAE"]["punto"])):
        qb, g = calibrar_b_a_mae(base, q.c, objetivo, sigma_pred_sellada, mu_clim, sd_clim)
        pot = potencia(qb, sigma_pred_sellada, mu_clim, sd_clim, 73, semilla=SEMILLA + 13)
        banda[nombre] = {"b": round(qb.b, 4), "ganancia_mae_pp": round(g, 4), **{k: pot[k] for k in ("DIR", "MAE", "CRPS")}}
    res["simulador"]["banda_potencia_73_dias"] = banda
    res["intentos_dsr"] = {"incremento": 2, "regla": "DIR es el endpoint congelado (no cuenta); la magnitud |g|−|p−g| ya está en el tramo ESTIM (no se cuenta dos veces); cuentan CRPS y su variante sigma_calibrada"}
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "potencia_por_metrica.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "potencia_por_metrica.md"), "w") as f:
        f.write(informe(res))
    return res


def _dias_txt(v):
    lo, hi = v["dias_para_0_80_ic95"]
    return f"{v['dias_para_0_80_al_efecto_observado']} [{lo}, {'∞' if hi == float('inf') else hi}]"


def informe(r: dict) -> str:
    p = r["parametros"]
    e = r["efecto_verdadero_por_metrica_en_el_simulador"]
    L = ["# La métrica que maximiza información por día sellado — Frente E (PROPUESTA)\n",
         f"> **{r['etiqueta']}** · generado {r['generado_en_utc']} · `python GEMELO/simulador/potencia_por_metrica.py`\n",
         f"Generador de 9 pp del Frente A (b = {p['generador']['b']}, c = {p['generador']['c']}, δ verdad {p['generador']['delta_verdad_pp']} pp). "
         f"En el simulador el mismo campeón tiene MAE {e['MAE_modelo_pp']} contra {e['MAE_cero_pp']} de predecir cero "
         f"(real sellado: {r['sellada']['mae_modelo_pp']} contra {r['sellada']['mae_cero_pp']}); σ_pred implícita del intervalo 80% sellado "
         f"{p['sigma_pred_sellada_pp']} pp, σ que calibraría {p['sigma_calibrada_en_simulador_pp']} pp; climatología N({p['climatologia']['mu']}, {p['climatologia']['sd']}).\n",
         "## Ventana sellada: z observado por métrica (IC de clúster de día)\n",
         "| métrica | punto | IC95 (t de clúster) | z | días | días para 0,80 al efecto observado [IC; ∞ = el IC del efecto contiene el cero] |",
         "|---|---|---|---|---|---|"]
    for col in ("DIR", "MAE", "CRPS"):
        v = r["sellada"][col]
        L.append(f"| {col} | {v['punto']} | {v['ic95']} | {v['z']} | {v['dias']} | **{_dias_txt(v)}** |")
    L += ["\n## Simulador: potencia por horizonte (permutación de signo por día, α = 0,05), σ_pred del intervalo sellado\n",
          "| días | DIR | MAE | CRPS |", "|---|---|---|---|"]
    for x in r["simulador"]["sigma_pred_sellada"]:
        L.append(f"| {x['n_dias']} | {x['DIR']['potencia']} {x['DIR']['ic95']} | {x['MAE']['potencia']} {x['MAE']['ic95']} | {x['CRPS']['potencia']} {x['CRPS']['ic95']} |")
    L += ["\nCon la σ calibrada (lo que el modelo tendría si su intervalo no fuera 1,84× ancho):\n", "| días | DIR | MAE | CRPS |", "|---|---|---|---|"]
    for x in r["simulador"]["sigma_calibrada"]:
        L.append(f"| {x['n_dias']} | {x['DIR']['potencia']} {x['DIR']['ic95']} | {x['MAE']['potencia']} {x['MAE']['ic95']} | {x['CRPS']['potencia']} {x['CRPS']['ic95']} |")
    L.append("")
    se_ = r["sellada"]
    L += ["", "## Correcciones tras el dictamen E (2-sep)", "",
          f"- Ancla: {se_['ancla']}.", f"- {se_['climatologia_y_sigma_pred']}.", f"- {se_['nota_familia']}.",
          f"- La constante μ (cero información) recupera el {100*se_['fraccion_de_la_ganancia_mae_que_da_la_constante_mu']:.1f}% de la ganancia de MAE: «predecir cero» no es la baseline pareada de «siempre al alza».",
          "- z e IC por **t de clúster** (gl = k−1), no percentil: el percentil sub-cubre y daba un z ~9% inflado.", "",
          "| métrica | punto | IC95 t de clúster | z | días para 0,80 [IC] | días al +6,45 pp publicado | R2 (sin 15–23 jul): punto · z · días [IC] |", "|---|---|---|---|---|---|---|"]
    for col in ("DIR", "MAE", "CRPS"):
        v, w = se_[col], se_["R2_sin_15_23_jul"][col]
        alt = v.get("dias_para_0_80_al_efecto_alternativo", {}).get("dias", "—")
        L.append(f"| {col} | {v['punto']} | {v['ic95']} | {v['z']} | **{_dias_txt(v)}** | {alt} | {w['punto']} · {w['z']} · {_dias_txt(w)} |")
    b = r["simulador"]["banda_potencia_73_dias"]
    L += ["", "**Banda de sensibilidad de la potencia a 73 días (MAE / CRPS / DIR):** " + "; ".join(
        f"{k}: ganancia MAE {v['ganancia_mae_pp']} pp → MAE {v['MAE']['potencia']} {v['MAE']['ic95']}, CRPS {v['CRPS']['potencia']}, DIR {v['DIR']['potencia']}" for k, v in b.items()),
          "La potencia de MAE a 73 días NO es un número: es la banda generador / observado / bajo R2. R2 es criterio congelado de rechazo, no una sensibilidad opcional.",
          f"", f"Intentos del DSR: incremento **{r['intentos_dsr']['incremento']}** ({r['intentos_dsr']['regla']}).", ""]
    return "\n".join(L) + "\n"


def solo_informe() -> dict:
    with open(os.path.join(DIR_RESULTADOS, "potencia_por_metrica.json")) as f:
        r = json.load(f)
    r["etiqueta"] = "PROPUESTA — Frente E v2, octava corrida; reescrito tras el dictamen E (NO CONCLUYENTE sobre las cifras operativas)"
    with open(os.path.join(DIR_RESULTADOS, "potencia_por_metrica.json"), "w") as f:
        json.dump(r, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "potencia_por_metrica.md"), "w") as f:
        f.write(informe(r))
    return r


if __name__ == "__main__":
    if "--solo-informe" in sys.argv:
        solo_informe(); sys.exit(0)
    r = main()
    print(json.dumps({"sellada": r["sellada"], "efecto": r["efecto_verdadero_por_metrica_en_el_simulador"],
                      "sim": r["simulador"]["sigma_pred_sellada"]}, indent=1, default=str))
