"""El intervalo de clúster de día de la rama de coherencia (bloque 4, corrida 11).

Lo pide el acta §82.3: la rama que retira las 15 filas sin pareja cuya
`sesion_objetivo` no calza con su `available_at`
(`backtest.linea_base.filtrar_sesion_coherente`) tiene p exacta pero NO
tiene intervalo de clúster de día, y hasta que lo tenga es una consecuencia
declarada y no un argumento. Esto lo computa. **No lo cablea**: el filtro
sigue sin aplicarse por defecto en ningún camino, y ninguna cifra publicada
se mueve.

Predicción escrita ANTES de computarlo (§82.3 y encargo, bloque 4): es
esperable que el intervalo contenga el cero, como lo contiene el de la
regla firmada.

Segunda ruta SIEMPRE (pre-mortem, objeción 4): se publican los tres
estimadores de día que ya existen —percentil de bootstrap de días, t de
clúster con gl = k−1, permutación de signo por día— sobre las DOS ramas,
salga lo que salga. La verificación no se activa sólo cuando el resultado
contradice la predicción.

Identidad de conjuntos ANTES de computar (pre-mortem, objeción 5): el
«n = 223» del acta sale de `filtrar_sesion_coherente(cargar(dedup=False))`
más `excluir_cero`, y el «238 − 15» sale de la regla firmada. Se prueba que
son el mismo conjunto de (fecha, ticker); si no lo son, se para y se anota.

Lectura en `mode=ro` vía `backtest.linea_base`. Sin red. Intentos del DSR:
0 (no es una hipótesis nueva: es el intervalo de una cifra ya declarada).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from math import comb

import numpy as np
import pandas as pd

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

import cifras  # noqa: E402
from backtest import linea_base as lb  # noqa: E402
from GEMELO import bifurcaciones as bf  # noqa: E402

DIR_RESULTADOS = os.path.join(_RAIZ, "GEMELO", "resultados")
SALIDA_MD = os.path.join(DIR_RESULTADOS, "intervalo_coherencia.md")
SALIDA_JSON = os.path.join(DIR_RESULTADOS, "intervalo_coherencia.json")
PREDICCION_PREVIA = ("el intervalo de clúster de día de la rama de coherencia contiene el cero, "
                     "como lo contiene el de la regla firmada (§82.3, escrito antes de computar)")


def _p_exacta(b: int, c: int) -> float:
    nb, kb = b + c, min(b, c)
    if nb == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(nb, i) for i in range(kb + 1)) / 2 ** nb)


def _claves(df: pd.DataFrame) -> set:
    return set(zip(df["fecha"].astype(str), df["ticker"].astype(str)))


R2_DESDE, R2_HASTA = "2026-07-15", "2026-07-23"   # el bloque de R2 (GEMELO/DISEÑO.md §6.2)


def medir_rama(df: pd.DataFrame, nombre: str) -> dict:
    d = lb.duelo(df)
    diff = (df["acierto_gap"].astype(int) - df["base_acierto"].astype(int)).to_numpy(dtype=float)
    grupos = cifras._grupos_por_dia(df, diff)
    punto, lo, hi = bf._bootstrap_dia(grupos, cifras.N_BOOT_DIA)
    _, lo_t, hi_t = bf._ic_t_cluster(grupos)
    p_dia = bf._p_permutacion_dia(grupos, cifras.N_PERM_DIA)
    icc = bf.icc_y_deff(grupos)
    b, c = int(d["mcnemar_b01"]), int(d["mcnemar_b10"])
    sumas = np.array([g.sum() for g in grupos])
    # R2 (exigencia B1 del adversario): la vara de rechazo congelada se corre
    # sobre CADA rama, PROPUESTA o no. Sin el bloque 15–23 jul.
    sin = df[~((df["fecha"] >= R2_DESDE) & (df["fecha"] <= R2_HASTA))]
    d2 = lb.duelo(sin)
    diff2 = (sin["acierto_gap"].astype(int) - sin["base_acierto"].astype(int)).to_numpy(dtype=float)
    g2 = cifras._grupos_por_dia(sin, diff2)
    _, lo2, hi2 = bf._bootstrap_dia(g2, cifras.N_BOOT_DIA)
    _, lo2t, hi2t = bf._ic_t_cluster(g2)
    b2, c2 = int(d2["mcnemar_b01"]), int(d2["mcnemar_b10"])
    return {
        "rama": nombre, "n": int(d["n"]), "dias": len(grupos),
        "dias_informativos": int((sumas != 0).sum()),
        "clusteres_de_tamano_1": int((np.array([len(g) for g in grupos]) == 1).sum()),
        "suma_por_dia_ordenada": [int(x) for x in sorted(sumas)],
        "R2_sin_15_23_jul": {
            "n": int(d2["n"]), "dias": len(g2), "ventaja_pp": d2["ventaja_pp"],
            "ic95_percentil_dia": [round(100 * lo2, 1), round(100 * hi2, 1)],
            "ic95_t_cluster": [round(100 * float(lo2t), 1), round(100 * float(hi2t), 1)],
            "p_permutacion_dia": round(float(bf._p_permutacion_dia(g2, cifras.N_PERM_DIA)), 3),
            "b": b2, "c": c2, "mcnemar_exacta": round(_p_exacta(b2, c2), 4),
        },
        "modelo_pct": d["modelo_pct"], "base_pct": d["base_pct"],
        "ventaja_pp": d["ventaja_pp"],
        "ventaja_pp_exacta": round(100 * (d["modelo_aciertos"] - d["base_aciertos"]) / d["n"], 2),
        "ic95_percentil_dia": [round(100 * lo, 1), round(100 * hi, 1)],
        "ic95_t_cluster": [round(100 * float(lo_t), 1), round(100 * float(hi_t), 1)],
        "p_permutacion_dia": round(float(p_dia), 3),
        "icc": round(float(icc["icc"]), 3), "deff": round(float(icc["deff"]), 2),
        "n_efectivo": round(float(icc["n_efectivo"]), 1),
        "b": b, "c": c,
        "mcnemar_chi2cc": round(float(d["mcnemar_p"]), 4), "mcnemar_exacta": round(_p_exacta(b, c), 4),
        "contiene_cero": {"percentil_dia": bool(lo <= 0 <= hi), "t_cluster": bool(lo_t <= 0 <= hi_t)},
    }


def correr(corte: str = cifras.CORTE_README) -> dict:
    conv = lb.CONVENCION_OFICIAL
    crudo = lb.cargar(hasta_sello=corte, dedup=False)
    firmada = lb.aplicar_convencion(lb.cargar(hasta_sello=corte, dedup=True), conv)
    # así lo computa el informe de linea_base (:762-763): filtro sobre el crudo, DESPUÉS la convención
    coherencia_informe = lb.aplicar_convencion(lb.filtrar_sesion_coherente(crudo), conv)
    # la otra lectura: la regla firmada, y después el filtro de coherencia
    coherencia_sobre_firmada = lb.filtrar_sesion_coherente(firmada)

    k_f, k_ci, k_cf = _claves(firmada), _claves(coherencia_informe), _claves(coherencia_sobre_firmada)
    retiradas = sorted(k_f - k_ci)
    identidad = {
        "n_regla_firmada": len(k_f), "n_coherencia_informe": len(k_ci),
        "n_coherencia_sobre_firmada": len(k_cf),
        "coherencia_es_subconjunto_de_firmada": k_ci <= k_f,
        "los_dos_ordenes_dan_el_mismo_conjunto": k_ci == k_cf,
        "retiradas_n": len(retiradas),
        "retiradas_por_fecha": {f: sorted(t for ff, t in retiradas if ff == f)
                                for f in sorted({ff for ff, _ in retiradas})},
    }
    identidad["ok"] = (identidad["coherencia_es_subconjunto_de_firmada"]
                       and identidad["los_dos_ordenes_dan_el_mismo_conjunto"])

    # ¿Las fechas retiradas eran días enteros o quedan mutilados? ¿Eran informativos?
    diff_f = (firmada["acierto_gap"].astype(int) - firmada["base_acierto"].astype(int))
    por_fecha_f = firmada.assign(d=diff_f).groupby("fecha")["d"].agg(["size", "sum"])
    dias_retirados = {}
    for f in identidad["retiradas_por_fecha"]:
        filas_dia = int(por_fecha_f.loc[f, "size"]) if f in por_fecha_f.index else 0
        quedan = int(coherencia_informe[coherencia_informe["fecha"] == f].shape[0])
        dias_retirados[f] = {
            "filas_en_regla_firmada": filas_dia,
            "retiradas": len(identidad["retiradas_por_fecha"][f]),
            "quedan": quedan,
            "dia_entero": quedan == 0,
            "suma_diff_del_dia_en_firmada": int(por_fecha_f.loc[f, "sum"]) if f in por_fecha_f.index else None,
            "era_informativo": bool(por_fecha_f.loc[f, "sum"] != 0) if f in por_fecha_f.index else None,
        }

    ramas = [medir_rama(firmada, "regla firmada (publicada)"),
             medir_rama(coherencia_informe, "+ coherencia (NO aplicada)")]
    coh = ramas[1]
    return {
        "generado_en_utc": datetime.now(timezone.utc).isoformat(),
        "etiqueta": "PROPUESTA — bloque 4 de la corrida 11; computado, NO cableado; ninguna cifra publicada se mueve",
        "corte": corte, "convencion": conv,
        "prediccion_previa": PREDICCION_PREVIA,
        "identidad_de_conjuntos": identidad,
        "dias_retirados": dias_retirados,
        "ramas": ramas,
        "prediccion_se_cumple": {
            "percentil_dia": coh["contiene_cero"]["percentil_dia"],
            "t_cluster": coh["contiene_cero"]["t_cluster"],
            "permutacion_dia_p_mayor_005": coh["p_permutacion_dia"] > 0.05,
        },
        "cableado": "filtrar_sesion_coherente sigue SIN aplicarse por defecto; cablearlo es decisión aparte, no firmada",
        "procedencia": ("backtest.linea_base.{cargar(dedup=...),filtrar_sesion_coherente,aplicar_convencion,duelo} "
                        "mode=ro; GEMELO.bifurcaciones.{_bootstrap_dia,_ic_t_cluster,_p_permutacion_dia,icc_y_deff}; "
                        f"N_BOOT_DIA={cifras.N_BOOT_DIA}, N_PERM_DIA={cifras.N_PERM_DIA}"),
        "intentos_dsr": 0,
    }


def informe(r: dict) -> str:
    idt, L = r["identidad_de_conjuntos"], []
    L.append("# El intervalo de clúster de día de la rama de coherencia — bloque 4, corrida 11 (PROPUESTA)\n")
    L.append(f"> **{r['etiqueta']}.** Generado {r['generado_en_utc']} por `python -m GEMELO.intervalo_coherencia`. "
             f"Corte `{r['corte']}`, convención `{r['convencion']}`, `senales.db` en `mode=ro`.")
    L.append(">")
    L.append(f"> **Predicción escrita antes de computar:** {r['prediccion_previa']}.\n")
    L.append("## 1. Identidad de conjuntos, antes de computar nada\n")
    L.append(f"- Regla firmada: n = {idt['n_regla_firmada']}. Coherencia como la computa el informe de "
             f"`linea_base` (filtro sobre el crudo, después la convención): n = {idt['n_coherencia_informe']}. "
             f"Coherencia aplicada SOBRE la regla firmada: n = {idt['n_coherencia_sobre_firmada']}.")
    L.append(f"- ¿Coherencia ⊂ firmada? **{idt['coherencia_es_subconjunto_de_firmada']}**. ¿Los dos órdenes dan el "
             f"mismo conjunto? **{idt['los_dos_ordenes_dan_el_mismo_conjunto']}**. Filas retiradas: "
             f"**{idt['retiradas_n']}**.")
    for f, ts in idt["retiradas_por_fecha"].items():
        L.append(f"  - {f}: {len(ts)} filas ({', '.join(ts)})")
    if not idt["ok"]:
        L.append("\n**Los conjuntos NO coinciden: se para acá y se anota.** Las cifras de abajo se computan igual "
                 "sobre la rama del informe, pero no se puede decir que sean «238 − 15».\n")
    L.append("\n## 2. ¿Días enteros o días mutilados? ¿Eran informativos?\n")
    L.append("| fecha | filas en la regla firmada | retiradas | quedan | ¿día entero? | Σ(modelo−base) del día | ¿informativo? |")
    L.append("|---|---|---|---|---|---|---|")
    for f, d in r["dias_retirados"].items():
        L.append(f"| {f} | {d['filas_en_regla_firmada']} | {d['retiradas']} | {d['quedan']} | "
                 f"{'sí' if d['dia_entero'] else '**no**'} | {d['suma_diff_del_dia_en_firmada']:+d} | "
                 f"{'sí' if d['era_informativo'] else 'no'} |")
    L.append("\nUn día informativo es uno cuya suma de (acierto del modelo − acierto de la base) no es cero: "
             "es el que mueve el estadístico de día. Si el retiro se lleva días enteros, cambia k; si los "
             "mutila, cambia el peso de un día que sigue existiendo.\n")
    L.append("## 3. Las dos ramas, con los tres estimadores de día (segunda ruta siempre)\n")
    L.append("| rama | n | días | días informativos | modelo | base | ventaja | IC95 percentil de día | IC95 t de clúster | p permutación de día | ICC | DEFF | n efectivo | b/c | McNemar χ²cc | McNemar exacta |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for m in r["ramas"]:
        L.append(f"| {m['rama']} | {m['n']} | {m['dias']} | {m['dias_informativos']} | {m['modelo_pct']} % | "
                 f"{m['base_pct']} % | **{m['ventaja_pp']:+} pp** | {m['ic95_percentil_dia']} | {m['ic95_t_cluster']} | "
                 f"{m['p_permutacion_dia']} | {m['icc']} | {m['deff']} | {m['n_efectivo']} | {m['b']}/{m['c']} | "
                 f"{m['mcnemar_chi2cc']} | {m['mcnemar_exacta']} |")
    L.append("")
    L.append("**Cuál de los dos IC es el calibrado** (exigencia B2): la t de clúster con gl = k−1, que el")
    L.append("Frente A midió con cobertura 0,949–0,951 a k = 35; el percentil de día cubre ~0,93 ahí. Acá la")
    L.append(f"rama de coherencia tiene k = {r['ramas'][1]['dias']} con "
             f"{r['ramas'][1]['clusteres_de_tamano_1']} clúster(es) de tamaño 1 (el 2026-08-05 mutilado), fuera del")
    L.append("estudio de cobertura. Que el percentil «roce» −1,4 no significa nada: es el estimador que sub-cubre.\n")
    L.append("## 3b. R2 sobre las dos ramas (exigencia B1: una vara de rechazo congelada no se omite porque la rama sea PROPUESTA)\n")
    L.append("| rama | n sin 15–23 jul | días | ventaja | IC95 percentil | IC95 t de clúster | p permutación | b/c | McNemar exacta |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for m in r["ramas"]:
        x = m["R2_sin_15_23_jul"]
        L.append(f"| {m['rama']} | {x['n']} | {x['dias']} | {x['ventaja_pp']:+} pp | {x['ic95_percentil_dia']} | "
                 f"{x['ic95_t_cluster']} | {x['p_permutacion_dia']} | {x['b']}/{x['c']} | {x['mcnemar_exacta']} |")
    L.append("")
    L.append("Las dos fechas retiradas (5-jul y 5-ago) están FUERA del bloque de R2: la rama de coherencia hereda")
    L.append("intacta la ventana afortunada, y sin ella se apaga igual que la regla firmada.\n")
    L.append("## 3c. La asimetría del retiro, en números (exigencia B3)\n")
    f = r["ramas"][0]
    L.append(f"Σ(modelo − base) por día en la regla firmada, ordenada: `{f['suma_por_dia_ordenada']}`. Días negativos: "
             f"{sum(1 for x in f['suma_por_dia_ordenada'] if x < 0)}; positivos: "
             f"{sum(1 for x in f['suma_por_dia_ordenada'] if x > 0)}. El retiro se llevó los dos días con Σ = −4, o sea")
    L.append("**2 de los negativos y 0 de los positivos**. No es indicio de acomodo: es exactamente el mecanismo que el")
    L.append("§82.3 escribió ANTES de computar (una fila puntuada contra el día equivocado pierde contra una baseline")
    L.append("con deriva al alza). Consecuencia que sí hay que decir (exigencia B4): **+14,3 pp es otro estimando**, la")
    L.append("ventaja restringida a filas con sesión coherente, no «+9,7 medido mejor»; el movimiento entero sale de 2")
    L.append("días de 34.\n")
    pc = r["prediccion_se_cumple"]
    L.append("## 4. La predicción, contra el resultado\n")
    L.append(f"- Percentil de día contiene el cero: **{pc['percentil_dia']}**. t de clúster contiene el cero: "
             f"**{pc['t_cluster']}**. Permutación de día p > 0,05: **{pc['permutacion_dia_p_mayor_005']}**.")
    todas = all(pc.values())
    ninguna = not any(pc.values())
    if todas:
        L.append("- **La predicción se cumple en las tres rutas.** El retiro de las 15 filas mueve el punto y el "
                 "McNemar de filas, no la conclusión de día: la ventaja sigue sin distinguirse de cero cuando se "
                 "respeta que las filas de un día no son independientes.")
    elif ninguna:
        L.append("- **La predicción NO se cumple en ninguna ruta.** Es un hallazgo y lo juzga el adversario; "
                 "acá no se interpreta más allá de anotarlo.")
    else:
        L.append("- **Las rutas discrepan.** Se publica la discrepancia tal cual; no se elige la ruta que conviene.")
    L.append(f"\n**Cableado:** {r['cableado']}. Intentos del DSR: {r['intentos_dsr']}: el «0» se sostiene sólo porque la")
    L.append("rama no está cableada ni publicada; si algún día `filtrar_sesion_coherente` pasa a aplicarse por defecto,")
    L.append("**es un intento** y entra a `GEMELO.relevo_asiatico` (exigencia B5).\n")
    L.append(f"Procedencia: {r['procedencia']}.")
    return "\n".join(L) + "\n"


def main() -> dict:
    r = correr()
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1, ensure_ascii=False, default=float)
        f.write("\n")
    with open(SALIDA_MD, "w", encoding="utf-8") as f:
        f.write(informe(r))
    print("escrito", SALIDA_MD)
    print("identidad ok:", r["identidad_de_conjuntos"]["ok"], "| predicción:", r["prediccion_se_cumple"])
    return r


if __name__ == "__main__":
    main()
