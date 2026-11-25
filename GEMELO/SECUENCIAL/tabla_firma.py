"""tabla_firma.py — la tabla que Nicolás necesita para firmar el MDE.

Un abanico de MDE candidatos y, para cada uno: el `N_max` del plan, el n de
cada una de las cuatro miradas, la fecha estimada en que la población lo
alcanza al ritmo MEDIDO, y la potencia realizada. Nada más: este script no
elige el MDE y no puede, porque la elección mueve el calendario en años y
es de Nicolás (`DISEÑO.md` §A3.1.d).

**Por qué este script existe y no bastaba la tabla de la v5.** La v5
publicaba el calendario con el ritmo de la ventana ANTECEDENTE (6.56 filas
por día hábil, medido sobre las filas de julio y agosto) porque la
población no existía todavía. Hoy la población tiene semanas de historia, y
el ritmo se mide donde ocurre. El ritmo real es MAYOR, así que las fechas
se adelantan — y la fecha de la primera mirada es el plazo real de la firma.

**NINGUNA CIFRA DE RESULTADO ENTRA ACÁ.** El ritmo sale de CONTAR filas de
la población (`ventana_antecedente.ritmo_poblacion`, que las devuelve sin
columnas de resultado); los parámetros de estorbo —`p_d`— salen de la
ventana antecedente, donde computarlos está autorizado por §A2. No se
computa ninguna ventaja, ningún p y ningún acierto, en ninguna de las dos
ventanas. Este script se puede correr tantas veces como haga falta sin
gastar un punto de α, y eso es una propiedad del diseño del script, no una
promesa.

SOLO LECTURA. Corre con:
    python -m GEMELO.SECUENCIAL.tabla_firma
    python -m GEMELO.SECUENCIAL.tabla_firma --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)
sys.path.insert(0, _AQUI)

from GEMELO.SECUENCIAL import ventana_antecedente as va   # noqa: E402
import diseno_secuencial as D                             # noqa: E402

# El abanico que la tarjeta pone sobre la mesa. Los tres primeros salen del
# intervalo del MDE que `mde_desde_v6.py` computa hoy sobre la ventana
# antecedente anclada; el cuarto es el valor que la v4 del documento usaba
# por calendario y que §A3.1.d manda declarar como elección de calendario
# si se firma.
#
# NO están cableados: `abanico()` los lee del script, y si el script da
# otro número la tabla cambia con él. Un abanico cableado sería un MDE
# cableado con pasos intermedios.
MDE_CALENDARIO_HISTORICO = 0.10

# El factor con que §A3.3 paga en N la diferencia entre el umbral final del
# plan (2.024) y el 1.96 de muestra fija. No depende del MDE.
#
# SE COMPUTA, NO SE CABLEA — defecto N3 del re-dictamen, y es de la clase
# exacta que el cuarto dictamen hizo bloqueante. El valor cableado era
# 1.0241 y **el script versionado de este repo no lo reproduce**: da
# 1.026380, y con el cableado la potencia idealizada no es 0.80 sino
# **0.7991**. La magnitud es trivial (0.09 pp); la clase no: una constante
# de pre-registro que el script del mismo repo contradice es, textualmente,
# lo que el cuarto dictamen llamó «un pre-registro que no reproduce el día
# que se firma». Se conserva el valor viejo al lado para que la corrección
# quede auditable.
FACTOR_SECUENCIAL_CABLEADO_HASTA_LA_CORRIDA_17 = (
    D.FACTOR_SECUENCIAL_CABLEADO_HASTA_LA_CORRIDA_17)


# El factor vive en `diseno_secuencial` y acá sólo se re-exporta, para que
# `mirada.py` y este módulo no puedan desincronizarse (dictamen de cierre,
# O-1): tenerlo en dos sitios dejó dos generaciones de `N_max` vivas.
factor_secuencial = D.factor_secuencial
FACTOR_SECUENCIAL = D.factor_secuencial()


def abanico(mde_json: dict | None = None) -> list[tuple[str, float]]:
    """(etiqueta, MDE en proporción) — el borde inferior del intervalo, el
    punto, el borde superior y el valor histórico de calendario."""
    if mde_json is None:
        from GEMELO.SECUENCIAL import mde_desde_v6 as M
        mde_json = M.medir()
    lo, hi = mde_json["mde_ic_pp"]
    crit = mde_critico(mde_json["p_d"], va.ritmo_poblacion()["filas"])
    filas = [
        ("borde inferior del IC95", lo / 100),
        ("punto", mde_json["mde_pp"] / 100),
        ("el MDE crítico: la mirada 1 ya vence acá", crit),
        ("borde superior del IC95", hi / 100),
        ("elección de calendario (§A3.1.d)", MDE_CALENDARIO_HISTORICO),
    ]
    # Ordenado por MDE para que la tabla se lea como un abanico y no como
    # una lista de etiquetas: el lector tiene que ver dónde cae el crítico
    # respecto del punto y de los bordes, que es la decisión.
    return sorted(filas, key=lambda f: f[1])


def n_max(mde: float, p_d: float, deff: float = None) -> dict:
    """`N_max` del plan secuencial para un MDE, con sus tres escalones.

    El total delega en `diseno_secuencial.n_max_del_plan`, que es el ÚNICO
    lugar donde vive el factor secuencial: tenerlo en dos sitios dejó dos
    generaciones de `N_max` vivas a la vez (dictamen de cierre, O-1).
    """
    deff = D.DEFF_PLANIFICACION if deff is None else deff
    n_iid = D.n_mcnemar(mde, p_d=p_d)
    return {"n_iid": n_iid, "n_con_deff": n_iid * deff,
            "n_max": D.n_max_del_plan(mde, p_d=p_d, deff=deff)}


def potencia_del_plan() -> dict:
    """La potencia que el plan entrega con su `N_max`, y el agujero de §A3.3.

    Dos números y la distancia entre ellos:
      * `idealizada` — con la varianza CONOCIDA, que es el supuesto bajo el
        que `N_max` se eligió. Da 0.80 por construcción.
      * `con_regla_del_maximo` — descontando que `V̂` es el máximo de tres
        estimadores ruidosos y por lo tanto está sesgado hacia arriba. Es la
        cifra que §A3.3 declara sin resolver.

    **NO TOMA ARGUMENTOS, y antes tomaba dos que no leía** (`mde` y `p_d`):
    lo cazó el quinto dictamen (E4). No los lee porque no los necesita — la
    potencia del plan depende de la fracción de información y de los
    umbrales, no del MDE: el MDE se paga en `N_max`, y por eso `N_max` está
    calibrado para dar 0.80 a CUALQUIER MDE. Una firma que acepta argumentos
    que ignora invita a creer que la cifra es condicional a ellos.

    El sesgo del máximo NO se vuelve a simular acá: la v4 lo midió en ~12 %
    sobre `V̂`, y lo que este script hace es propagarlo al drift requerido,
    que es aritmética sobre una cifra medida. **Ese 12 % no tiene intervalo**,
    así que la potencia que sale de él **no se cita con cuatro decimales**:
    se cita como **≈0.75** (exigencia E4). Y hay dos mediciones de la misma
    cantidad que se contradicen —1.7 pp simulada contra 4.6 pp analítica— y
    reconciliarlas es parte de E4, no está hecho, y está en la tarjeta §92.
    """
    from evaluacion import norm_ppf
    malla = D.Malla(D.FRACCIONES, m=2001, ancho=7.0)
    umbrales = list(D.UMBRALES_OBF)
    drift = D.drift_para_potencia(malla, umbrales, objetivo=0.80)

    # LA POTENCIA SE EVALÚA EN EL DRIFT QUE `FACTOR_SECUENCIAL` COMPRA, no en
    # el drift que la bisección acaba de despejar — defecto N4 del
    # re-dictamen. Evaluarla en el drift despejado da 0.80 **por
    # construcción**, independiente del factor, de `N_max`, de `p_d` y del
    # MDE: era un test tautológico dentro de la función que venía a
    # auditarlo, o sea el defecto N8 del tercer dictamen reintroducido. Así
    # como está, la cifra puede FALLAR si el factor se desincroniza, que es
    # lo único que la hace informativa.
    drift_comprado = (norm_ppf(0.975) + norm_ppf(0.80)) * FACTOR_SECUENCIAL ** 0.5
    ideal, _ = D.potencia_secuencial(malla, umbrales, drift_comprado)
    # V̂ inflada 12% => Z se divide por sqrt(1.12) => el drift efectivo baja
    # en el mismo factor.
    con_max, _ = D.potencia_secuencial(malla, umbrales,
                                       drift_comprado / (1.12 ** 0.5))
    return {"drift_requerido": drift, "drift_comprado": drift_comprado,
            "factor_secuencial": FACTOR_SECUENCIAL,
            "potencia_idealizada": ideal,
            "potencia_con_regla_del_maximo": con_max,
            "inflacion_v_hat_supuesta": 0.12}


def mde_critico(p_d: float, filas_hoy: int, fraccion: float = 0.25) -> float:
    """El MDE a partir del cual la PRIMERA mirada ya está vencida.

    `N_max` decrece con el MDE, así que por encima de cierto MDE el n de la
    mirada 1 (= 0.25 · N_max) cae por debajo de las filas que la población
    ya tiene. Firmar ahí significa que el plan arranca con una mirada
    debida: §A3.8 dice que una mirada saltada no se recupera y que una
    "omitida" que en realidad se hizo es fraude, así que esto no es un
    detalle de calendario — es una condición que la firma tiene que conocer
    ANTES, y es la razón por la que esta corrida existe.

    Se resuelve por bisección sobre el MDE. Devuelve el MDE en proporción.
    """
    lo, hi = 0.01, 0.50
    for _ in range(80):
        medio = 0.5 * (lo + hi)
        n_1 = fraccion * n_max(medio, p_d)["n_max"]
        if n_1 > filas_hoy:
            lo = medio          # todavía no vencida: hace falta un MDE mayor
        else:
            hi = medio
        if hi - lo < 1e-6:
            break
    return 0.5 * (lo + hi)


def propagacion_conjunta(mde_json: dict | None = None) -> dict:
    """`N_max` y el n de cada mirada con **`p_d` = `f` dentro de cada
    réplica**. Es la exigencia E2 del quinto dictamen, y arregla un defecto
    de método, no una cifra.

    **El defecto.** El abanico de `tabla()` toma los BORDES del IC95 del MDE
    —que vienen de réplicas con `f` chico o grande— y los mete en Connor con
    `p_d` fija en su PUNTO. Pero `p_d` **es** `f` (identidad estructural, ver
    `mde_desde_v6.replicas`), así que eso combina réplicas distintas del
    mismo remuestreo. Medido: los dos extremos del abanico caen **fuera** del
    intervalo honesto. El plug-in no es conservador ni optimista: está mal
    emparejado, y por eso lo que sale de él no es un intervalo de nada.

    Acá, por cada réplica del bootstrap de clústeres de día se computa su
    propio MDE y su propio `N_max` con el MISMO `f`, y se reportan los
    percentiles de la distribución resultante. El abanico de `tabla()` se
    conserva porque es el que responde «si firmo ESTE número, ¿cuándo mira
    el plan?» —una pregunta condicional, legítima y necesaria para firmar—,
    pero deja de presentarse como un intervalo.
    """
    import numpy as np
    sys.path.insert(0, os.path.join(_RAIZ, '.claude/skills/estadistica-evaluacion/scripts'))
    from GEMELO.SECUENCIAL import mde_desde_v6 as M
    if mde_json is None:
        mde_json = M.medir()
    r = M.replicas(c_pb=mde_json["costo_pb"])
    f_rep, mde_rep = r["f"], r["mde_pp"]
    ok = (f_rep > 0) & (f_rep < 1) & np.isfinite(mde_rep) & (mde_rep > 0)
    nmax = np.array([n_max(m / 100.0, pd_)["n_max"]
                     for m, pd_ in zip(mde_rep[ok], f_rep[ok])])
    ritmo = va.ritmo_poblacion()
    out = {"replicas_utiles": int(ok.sum()), "n_boot": r["n_boot"],
           "semilla": r["semilla"], "clusteres": r["clusteres"],
           "n_max_mediana": float(np.median(nmax)),
           "n_max_ic": (float(np.percentile(nmax, 2.5)),
                        float(np.percentile(nmax, 97.5))),
           "miradas": []}
    for t in D.FRACCIONES:
        nk = t * nmax
        lo, med, hi = (float(np.percentile(nk, 2.5)), float(np.median(nk)),
                       float(np.percentile(nk, 97.5)))
        fe = va.fecha_para_filas(round(med), ritmo["filas_por_dia_habil"],
                                ritmo["filas"], ritmo["ultima"])
        out["miradas"].append({
            "fraccion": t, "n_mediana": med, "n_ic": (lo, hi),
            "fecha_de_la_mediana": fe.isoformat() if fe else "ALCANZADO"})
    # P(la mirada 1 ya está vencida), que es la cantidad bien definida que
    # reemplaza al «el crítico cae dentro del IC»: la fracción de réplicas en
    # que 0.25·N_max no supera las filas ya contadas.
    # F9 del re-dictamen: con su Wilson, y con el nombre condicionado. Si la
    # mirada 1 está vencida o no es, en rigor, una función DETERMINISTA del
    # MDE **firmado**, y no hay MDE firmado; lo que esta proporción mide es
    # la fracción de remuestreos de los días de la ventana antecedente en
    # que el MDE derivado dejaría la mirada 1 debida. Publicarla desnuda
    # habría sido un punto sin intervalo en la ronda que corrigió
    # exactamente eso.
    from evaluacion import wilson_ci
    vencidas = int((0.25 * nmax <= ritmo["filas"]).sum())
    out["p_mirada1_vencida"] = vencidas / len(nmax)
    out["p_vencida_wilson"] = tuple(wilson_ci(vencidas, len(nmax)))
    out["p_vencida_glosa"] = (
        "fracción de réplicas en que el MDE derivado dejaría la mirada 1 "
        "debida; condicional a firmar la regla del punto derivado, no una "
        "probabilidad sobre un MDE firmado")
    return out


def tabla(mde_json: dict | None = None) -> dict:
    ritmo = va.ritmo_poblacion()
    if mde_json is None:
        from GEMELO.SECUENCIAL import mde_desde_v6 as M
        mde_json = M.medir()
    p_d = mde_json["p_d"]
    hoy = dt.date.today()
    filas = []
    for etiqueta, mde in abanico(mde_json):
        nm = n_max(mde, p_d)
        N = round(nm["n_max"])
        miradas = []
        for t, umbral in zip(D.FRACCIONES, D.UMBRALES_OBF):
            n_k = round(t * N)
            f = va.fecha_para_filas(n_k, ritmo["filas_por_dia_habil"],
                                    ritmo["filas"], ritmo["ultima"])
            miradas.append({
                "fraccion": t, "n": n_k, "umbral": umbral,
                "fecha": f.isoformat() if f else "ALCANZADO",
                "dias_desde_hoy": (f - hoy).days if f else 0,
                "dentro_de_una_semana": bool(f and (f - hoy).days <= 7),
            })
        filas.append({"etiqueta": etiqueta, "mde_pp": mde * 100,
                      "n_iid": round(nm["n_iid"]),
                      "n_con_deff": round(nm["n_con_deff"]),
                      "n_max": N, "miradas": miradas})
    critico = mde_critico(p_d, ritmo["filas"])
    conjunta = propagacion_conjunta(mde_json)
    # EL INTERVALO DEL MDE CRÍTICO, y por qué existe. `N_max` depende de
    # `p_d`, y `p_d` **es** `f` — identidad estructural, no coincidencia: la
    # baseline siempre dice «al alza», así que modelo y baseline sólo pueden
    # discordar donde el modelo dice BAJA, y bajo `excluir_cero` el conjunto
    # discordante ES el conjunto BAJA. Así que el MDE crítico hereda el
    # intervalo de `f`, el mismo que el MDE propaga. Publicarlo como punto
    # sería la regla 1 de la casa rota en el umbral que decide si una mirada
    # está vencida — lo cazó el `curador-epistemico` en la corrida 17.
    f_lo, f_hi = mde_json["f_ic"]
    critico_lo = mde_critico(f_lo, ritmo["filas"])
    critico_hi = mde_critico(f_hi, ritmo["filas"])
    return {"hoy": hoy.isoformat(), "ritmo": ritmo, "p_d": p_d,
            "mde_critico_ic_pp": (critico_lo * 100, critico_hi * 100),
            "deff_planificacion": D.DEFF_PLANIFICACION,
            "factor_secuencial": FACTOR_SECUENCIAL,
            "mde": {"punto_pp": mde_json["mde_pp"],
                    "ic_pp": mde_json["mde_ic_pp"],
                    "costo_pb": mde_json["costo_pb"]},
            "conjunta": conjunta,
            "mde_critico_pp": critico * 100,
            "mde_critico_dentro_del_ic": bool(
                mde_json["mde_ic_pp"][0] <= critico * 100
                <= mde_json["mde_ic_pp"][1]),
            "filas": filas,
            "potencia": potencia_del_plan()}


def markdown(t: dict) -> str:
    r, L = t["ritmo"], []
    L.append(f"Ritmo MEDIDO de la población, por conteo: **{r['filas']} filas "
             f"en {r['dias_habiles']} días hábiles** desde el corte "
             f"({r['primera']} a {r['ultima']}), "
             f"**{r['filas_por_dia_habil']:.3f} filas/día hábil** "
             f"en {r['fechas']} fechas de emisión.")
    L.append("")
    L.append(f"`p_d` de la ventana antecedente anclada: **{t['p_d']:.4f}**. "
             f"DEFF de planificación {t['deff_planificacion']}, factor "
             f"secuencial {t['factor_secuencial']}.")
    L.append("")
    c = t["conjunta"]
    L.append("**EL INTERVALO HONESTO de `N_max`**, con `p_d` = `f` dentro de "
             f"cada réplica ({c['n_boot']} réplicas de clústeres de día, "
             f"semilla {c['semilla']}, {c['clusteres']} clústeres). `p_d` ES "
             "`f`, así que el MDE y el `N_max` que lo paga están acoplados "
             "por la MISMA estimación:")
    L.append("")
    L.append("| | mediana | IC95 |")
    L.append("|---|---|---|")
    L.append(f"| **`N_max`** | **{c['n_max_mediana']:.0f}** | "
             f"[{c['n_max_ic'][0]:.0f}, {c['n_max_ic'][1]:.0f}] |")
    for m in c["miradas"]:
        L.append(f"| mirada {int(m['fraccion']*4)} ({m['fraccion']:.0%}) | "
                 f"{m['n_mediana']:.0f} → {m['fecha_de_la_mediana']} | "
                 f"[{m['n_ic'][0]:.0f}, {m['n_ic'][1]:.0f}] |")
    L.append("")
    L.append(f"**P(la mirada 1 ya está vencida, si se firma la regla del "
             f"punto derivado) = {c['p_mirada1_vencida']:.4f}**, Wilson 95 % "
             f"[{c['p_vencida_wilson'][0]:.4f}, "
             f"{c['p_vencida_wilson'][1]:.4f}].")
    L.append("")
    L.append("**EL ABANICO CONDICIONAL — NO es un intervalo.** Responde «si "
             "firmo ESTE número, ¿cuándo mira el plan?». Cada fila combina el "
             "MDE de una réplica con `p_d` del punto, así que **las filas de "
             "los bordes caen FUERA del intervalo honesto de arriba** y no "
             "son bordes de nada:")
    L.append("")
    L.append("| MDE | qué es (CONDICIONAL) | `N_max` | mirada 1 | mirada 2 | "
             "mirada 3 | mirada 4 (final) |")
    L.append("|---|---|---|---|---|---|---|")
    for f in t["filas"]:
        celdas = []
        for m in f["miradas"]:
            if m["fecha"] == "ALCANZADO":
                celdas.append(f"{m['n']} → **YA VENCIDA** ⛔")
            else:
                marca = " ⚠" if m["dentro_de_una_semana"] else ""
                celdas.append(f"{m['n']} → {m['fecha']}{marca}")
        L.append(f"| **{f['mde_pp']:.2f} pp** | {f['etiqueta']} | "
                 f"{f['n_max']} | " + " | ".join(celdas) + " |")
    L.append("")
    L.append("⚠ = la mirada caería **dentro de una semana de hoy** "
             f"({t['hoy']}). ⛔ = la población YA tiene ese n: firmar ese "
             "MDE arranca el plan con una mirada debida.")
    L.append("")
    clo, chi = t["mde_critico_ic_pp"]
    L.append(f"**El MDE crítico es {t['mde_critico_pp']:.2f} pp como PUNTO, "
             f"IC95 [{clo:.2f}, {chi:.2f}]** (propagando el mismo intervalo "
             f"de `f` que propaga el MDE; `p_d` ≡ `f`, ver el código). Por "
             f"encima de él la primera mirada ya está vencida con las "
             f"{r['filas']} filas contadas. Está "
             + ("DENTRO" if t["mde_critico_dentro_del_ic"] else "fuera")
             + " del IC95 del MDE.")
    L.append("")
    L.append("**Lo que ese intervalo obliga a decir, y es lo contrario de un "
             "umbral:** cuál de las opciones arranca vencida está "
             f"**indeterminado entre {clo:.2f} y {chi:.2f} pp**. Lo que SÍ "
             "está medido: por encima del borde superior del IC del crítico "
             f"({chi:.2f} pp) la mirada 1 está vencida para TODO el intervalo "
             "de `f`, y el borde superior del IC del MDE "
             f"({t['mde']['ic_pp'][1]:.2f} pp) está por encima de él. "
             "Además el conteo que define el crítico es un techo que no "
             "aplica `excluir_cero` y cierra en la última fecha de emisión, "
             "no hoy: los dos efectos lo mueven unas décimas en direcciones "
             "opuestas.")
    L.append("")
    p = t["potencia"]
    L.append(f"Potencia del plan: **{p['potencia_idealizada']:.2f}** con la "
             f"varianza conocida (el supuesto con que se eligió `N_max`, "
             f"evaluada en el drift que `FACTOR_SECUENCIAL` = "
             f"{p['factor_secuencial']:.5f} compra) y **≈"
             f"{p['potencia_con_regla_del_maximo']:.2f}** descontando que la "
             f"regla del máximo infla `V̂` un "
             f"{p['inflacion_v_hat_supuesta']:.0%}. **Sin más decimales: el "
             "12 % no tiene intervalo**, así que la segunda cifra no admite "
             "cuatro. La diferencia es el agujero que §A3.3 declara sin "
             "resolver.")
    return "\n".join(L)


def conteo_por_regla_estimador() -> dict:
    """Qué le hace cada opción de la regla del estimador a las DOS ventanas,
    en conteos: n, clústeres y ritmo. Sin una sola cifra de resultado.

    Es lo que la tarjeta necesita para que la regla se elija **por
    principio y no por resultado**: ninguna ventaja y ningún p aparecen acá,
    ni se pueden, porque `cargar_poblacion()` devuelve las filas sin
    columnas de resultado.
    """
    from GEMELO.SECUENCIAL import mirada as M
    pob = va.cargar_poblacion()
    ant = va.cargar_antecedente(convencion=None)
    ritmo = va.ritmo_poblacion()
    out = {}
    for regla, glosa in M.REGLAS_DEDUP_ESTIMADOR.items():
        fila = {"glosa": glosa,
                "prohibida": regla in M.REGLAS_PROHIBIDAS}
        if fila["prohibida"]:
            out[regla] = fila
            continue
        p, clave = M.aplicar_regla_estimador(pob, regla)
        a, _ = M.aplicar_regla_estimador(ant, regla)
        habiles = ritmo["dias_habiles"]
        fila.update({
            "clave_cluster": clave,
            "poblacion_n": len(p),
            "poblacion_clusteres": int(p[clave].nunique()),
            "poblacion_filas_por_dia_habil": len(p) / habiles if habiles else None,
            "antecedente_n": len(a),
            "antecedente_clusteres": int(a[clave].nunique()),
        })
        out[regla] = fila
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--reglas", action="store_true",
                    help="el conteo por opción de la regla del estimador")
    ap.add_argument("--sellar", metavar="RUTA",
                    help="escribe la tabla con su INSTANTE en un JSON. Las "
                         "cifras de calendario son una medición puntual —la "
                         "población crece todos los días hábiles— así que sin "
                         "su instante no significan nada, igual que un precio "
                         "sin su `available_at`. No las congela: las fecha.")
    args = ap.parse_args()
    if args.reglas:
        r = conteo_por_regla_estimador()
        if args.json:
            print(json.dumps(r, indent=2, default=str, ensure_ascii=False))
            return
        print("CONTEO POR OPCIÓN DE LA REGLA DEL ESTIMADOR")
        print("(sólo conteos: ninguna ventaja, ningún p, en ninguna ventana)")
        print()
        print("| opción | clúster | n población | clústeres | filas/día hábil "
              "| n antecedente | clústeres |")
        print("|---|---|---|---|---|---|---|")
        for k, v in r.items():
            if v["prohibida"]:
                print(f"| `{k}` | — | PROHIBIDA (acta §60) | — | — | — | — |")
                continue
            print(f"| `{k}` | `{v['clave_cluster']}` | {v['poblacion_n']} | "
                  f"{v['poblacion_clusteres']} | "
                  f"{v['poblacion_filas_por_dia_habil']:.3f} | "
                  f"{v['antecedente_n']} | {v['antecedente_clusteres']} |")
        return
    t = tabla()
    t["medido_en"] = dt.datetime.now(dt.timezone.utc).isoformat(
        timespec="seconds")
    if args.sellar:
        with open(args.sellar, "w", encoding="utf-8") as fh:
            json.dump(t, fh, indent=2, default=str, ensure_ascii=False)
        print(f"[tabla sellada en {args.sellar} con instante "
              f"{t['medido_en']}]")
        return
    if args.json:
        print(json.dumps(t, indent=2, default=str, ensure_ascii=False))
        return
    print("=" * 72)
    print("LA TABLA DE LA FIRMA DEL MDE")
    print("=" * 72)
    print()
    print(markdown(t))
    print()
    print("Lo que esta tabla NO hace: elegir. §A3.1.d dice que si se firma un")
    print("valor que no sale de la derivación —por ejemplo el de calendario—")
    print("se declara como elección de calendario y no como derivación de V6.")


if __name__ == "__main__":
    main()
