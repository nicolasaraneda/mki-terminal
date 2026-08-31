"""
mirada.py — ejecuta UNA mirada del diseño secuencial pre-registrado.

**Se escribe hoy, 31-ago-2026, junto con el pre-registro, y no en
noviembre.** Es la regla 1 de `DISEÑO.md` §A3.8: un script que se escribe
el día de la mirada es un script que se escribe viendo los datos. Escribir
el criterio y el código antes es lo único que hace falsable a un
pre-registro.

Corre así, en la fecha del calendario y no antes:

    source venv/bin/activate
    python -m GEMELO.SECUENCIAL.mirada --mirada 1
    python -m GEMELO.SECUENCIAL.mirada --mirada 1 --escribir   # deja el acta

Tres candados estructurales, para que el script no pueda usarse mal:

1. **No puede mirar la ventana antecedente.** Descarta por construcción
   toda fila con `fecha` <= FECHA_CONGELAMIENTO. Las 248 filas de hoy son
   antecedente y volver a analizarlas es "la trampa de esta etapa".
2. **No puede adelantar una mirada.** Si el n acumulado todavía no llegó
   al n de la mirada pedida, NO computa el estadístico: dice cuánto falta
   y termina. Adelantar una mirada es gastar alfa que la frontera no
   presupuestó.
3. **No escribe en ninguna base.** `senales.db` se abre en `mode=ro` a
   través de `backtest.linea_base`, que es la única vía autorizada.

SOLO LECTURA. No importa `motor.py` ni escribe una fila sellada.
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import sys

import numpy as np

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)
sys.path.insert(0, os.path.join(_RAIZ, ".claude/skills/estadistica-evaluacion/scripts"))
sys.path.insert(0, _AQUI)

from backtest import inferencia as inf              # noqa: E402
from backtest.linea_base import aplicar_convencion, cargar  # noqa: E402
from evaluacion import comparar_pareado, norm_cdf   # noqa: E402

# ---------------------------------------------------------------------------
# EL PLAN, CONGELADO. Estas constantes son el pre-registro: si alguna cambia
# después del 31-ago-2026, el diseño terminó y hay que decirlo con acta.
# ---------------------------------------------------------------------------

FECHA_CONGELAMIENTO = "2026-08-31"
CONVENCION = "excluir_cero"          # GEMELO/DISEÑO.md §2.8

# (n de filas, umbral |Z| O'Brien-Fleming, Z de futilidad, fecha estimada)
PLAN = {
    1: (371,  4.048, -1.662, "2026-11-19"),
    2: (742,  2.862,  0.016, "2027-02-07"),
    3: (1114, 2.337,  1.033, "2027-04-28"),
    4: (1485, 2.024,  None,  "2027-07-17"),
}

# El bootstrap de la varianza cluster-robusta. Todo lo que determina V̂ se
# congela acá Y en DISEÑO.md §A3.2 — la semilla incluida. Elegir semilla,
# bloque o nº de réplicas viendo el resultado es otra forma de mirar dos
# veces.
SEMILLA_BOOTSTRAP = 20260831

# 200.000 y no 5.000: con 5.000 la desviación de V̂ entre semillas es 2.3%,
# que son ±0.023 sobre un umbral de 2.024. La semilla está congelada, así
# que el resultado es determinista — pero "determinista" no es "preciso":
# significaría que la semilla congelada vale ±0.02 de Z en una decisión que
# es un filo por construcción. Con 200.000 baja a ±0.003 y cuesta
# milisegundos sobre doscientos números.
N_DRAWS = 200_000

# LOS BLOQUES, y por qué son tres. Un bootstrap que sortea FECHAS
# independientes corrige la dependencia DENTRO de la fecha y es
# estructuralmente ciego a la dependencia ENTRE fechas. Si esa dependencia
# existe, V̂ sale corta y Z sale inflado. Y el proyecto tiene DOS
# afirmaciones propias de que existe: el bloque de 6 fechas consecutivas
# del 15-23-jul, y el criterio R2, que ES una afirmación sobre fechas
# contiguas.
#
# Con ~51 fechas en la mirada 1 ninguna longitud de bloque es confiable
# sola, así que se computan las tres y **el estadístico usa la mayor**.
# Tomar el máximo solo puede INFLAR la varianza, o sea solo puede bajar el
# α RESPECTO DEL PLAN DE BLOQUE 1. Ojo con leer eso como "el α queda en
# 0.05": no queda, y la tabla de §A3.2 dice cuánto.
BLOQUES_FECHAS = (1, 5, 10)
REGLA_VARIANZA = "max"

# La tabla de exposición residual (qué consigue la regla del máximo y qué
# NO) vive en UN solo lugar: `DISEÑO.md` §A3.2, computada por
# `diseno_secuencial.alfa_plan_bajo_correlacion`. Acá NO se copia: una
# tabla copiada en tres archivos es una tabla que se desactualiza en dos.
# Lo único que hay que saber para leer este módulo es que la exposición se
# reduce pero **no se elimina**, y que con ~51 fechas en la primera mirada
# eso es el límite del n, no un defecto del estimador.

# La cláusula 1 de §A3.7: un cambio de modelo TERMINA el diseño, sin
# excepción. Estaba escrita en prosa y el código no la conocía.
MODELO_ESPERADO = "4.6.0"
UNIVERSO_ESPERADO = "4.6.0"   # `version.py` HOY. Una constante de pre-registro
                              # que "se completa después" no está congelada, y su
                              # guard es código muerto hasta entonces.

DIR_ACTAS = os.path.join(_AQUI, "miradas")
RUTA_REGISTRO = os.path.join(DIR_ACTAS, "registro.log")


def cargar_ventana_nueva():
    """Las filas NUEVAS: emisión posterior al congelamiento, convención
    congelada. Devuelve (df, n_descartadas_por_antecedente)."""
    df = cargar()
    if df.empty:
        return df, 0
    antes = len(df)
    df = df[df["fecha"] > FECHA_CONGELAMIENTO].copy()
    descartadas = antes - len(df)
    if df.empty:
        return df, descartadas
    return aplicar_convencion(df, CONVENCION), descartadas


def contribuciones_por_fecha(df) -> np.ndarray:
    """d_j = Σ_i (acierto_modelo − acierto_base) sobre las filas de la fecha j.

    `b − c` se descompone EXACTAMENTE como la suma de estas contribuciones,
    y por eso la varianza de `b − c` se puede estimar remuestreando fechas.
    """
    return (df.groupby("fecha")
              .apply(lambda g: int((g["acierto_gap"].astype(int)
                                    - g["base_acierto"].astype(int)).sum()),
                     include_groups=False)
              .to_numpy(dtype=float))


def autocorrelacion_lag1(d: np.ndarray) -> tuple[float, float]:
    """(ac1, error estándar aproximado 1/√m). El parámetro que decide si el
    bloque 1 alcanza — se reporta SIEMPRE, no se usa para elegir nada."""
    m = len(d)
    if m < 3:
        return float("nan"), float("nan")
    x = d - d.mean()
    den = float((x * x).sum())
    if den == 0:
        return float("nan"), 1.0 / math.sqrt(m)
    return float((x[:-1] * x[1:]).sum() / den), 1.0 / math.sqrt(m)


def varianza_cluster(df) -> dict:
    """Factor de varianza cluster-robusta V̂, re-estimado con ESTOS datos.

    Bajo independencia Var(b−c) = b+c. Se remuestrean FECHAS con el
    remuestreador circular del proyecto (`backtest.inferencia.
    _remuestrear_circular`) en las TRES longitudes de bloque congeladas, y
    **V̂ es la mayor de las tres** (`REGLA_VARIANZA`). Bloque 1 captura el
    agrupamiento dentro de la fecha; los bloques 5 y 10 además el de fechas
    contiguas, que es al que un bootstrap de clúster puro es ciego.

    V̂ ≈ 1 significaría que no hay agrupamiento de ninguna clase. La
    planificación supuso V̂ ≈ 3.6; el estadístico usa el que salga.

    Devuelve SIEMPRE el mismo juego de claves, degenerado o no: la versión
    anterior devolvía un dict corto en la rama degenerada y quien lo leía
    reventaba con KeyError. La rama que existe para manejar el caso raro
    era la única que fallaba.
    """
    d = contribuciones_por_fecha(df)
    b = int(((df["acierto_gap"] == 1) & (df["base_acierto"] == 0)).sum())
    c = int(((df["acierto_gap"] == 0) & (df["base_acierto"] == 1)).sum())
    var_iid = float(b + c)
    ac1, ac1_ee = autocorrelacion_lag1(d)

    base = {
        "b": b, "c": c, "fechas": len(d), "var_iid": var_iid,
        "ac1": ac1, "ac1_ee": ac1_ee,
        "semilla": SEMILLA_BOOTSTRAP, "n_draws": N_DRAWS,
        "bloques": BLOQUES_FECHAS, "regla": REGLA_VARIANZA,
        "v_por_bloque": {}, "v_hat": float("nan"), "var_boot": float("nan"),
        "degenerado": None,
    }
    if var_iid == 0 or len(d) < 2:
        base["degenerado"] = ("sin discordantes" if var_iid == 0
                              else "menos de dos fechas")
        return base

    for bloque in BLOQUES_FECHAS:
        sumas = inf._remuestrear_circular(
            d, SEMILLA_BOOTSTRAP, N_DRAWS, bloque).sum(axis=1)
        base["v_por_bloque"][bloque] = float(np.var(sumas, ddof=1)) / var_iid

    v_hat = max(base["v_por_bloque"].values())
    if not (v_hat > 0) or not math.isfinite(v_hat):
        # Todas las fechas del mismo signo: la varianza remuestreada colapsa
        # a cero y dividir por su raíz reventaba el script el día de la
        # mirada. No se inventa un número: se declara degenerado.
        base["degenerado"] = "varianza remuestreada nula o no finita"
        return base

    base["v_hat"] = v_hat
    base["var_boot"] = v_hat * var_iid
    return base


def _guard_versiones() -> str | None:
    """La cláusula 1 de §A3.7 hecha código: un cambio de `MODELO_VERSION`
    TERMINA el diseño, sin excepción, porque las filas del modelo nuevo no
    son la misma población.

    Sin este guard el script seguía corriendo después de un relevo,
    contando filas del modelo nuevo hacia el n del plan y emitiendo un
    veredicto como si el diseño estuviera vivo. La cláusula estaba escrita
    en prosa y el código no la conocía.
    """
    from version import MODELO_VERSION, UNIVERSO_VERSION
    if MODELO_VERSION != MODELO_ESPERADO:
        return (f"DISEÑO TERMINADO — `MODELO_VERSION` es {MODELO_VERSION} y el "
                f"pre-registro se congeló sobre {MODELO_ESPERADO}. Cláusula 1 de "
                "§A3.7: las filas del modelo nuevo no son la misma población. "
                "Reportar el resultado parcial con su n, declarar terminado por "
                "cambio de modelo, y que el modelo nuevo arranque su propio "
                "diseño desde cero. NO se computa nada.")
    if UNIVERSO_ESPERADO is not None and UNIVERSO_VERSION != UNIVERSO_ESPERADO:
        return (f"REVISAR ANTES DE SEGUIR — `UNIVERSO_VERSION` es "
                f"{UNIVERSO_VERSION}, se esperaba {UNIVERSO_ESPERADO}. "
                "Cláusula 2 de §A3.7: el diseño continúa solo si el cambio "
                "afecta a menos del 10% de las filas acumuladas.")
    return None


def _registrar(salida: dict) -> None:
    """Append-only. TODA ejecución que compute el estadístico deja línea,
    con `--escribir` o sin él.

    Sin esto la regla de las miradas furtivas no es exigible: el documento
    le pone precio a una mirada no declarada (α de 0.050 a 0.094) y la
    herramienta hacía que no declararla fuera el comportamiento por
    defecto.
    """
    os.makedirs(DIR_ACTAS, exist_ok=True)
    with open(RUTA_REGISTRO, "a", encoding="utf-8") as fh:
        fh.write(f"{salida['corrida_en']}\tmirada={salida['mirada']}\t"
                 f"n={salida['n']}\tZ={salida.get('z', 'NA')}\t"
                 f"veredicto={salida['veredicto']}\n")


def ejecutar(k: int) -> dict:
    n_obj, umbral, z_fut, fecha_plan = PLAN[k]
    salida = {
        "mirada": k, "n_objetivo": n_obj, "umbral": umbral,
        "z_futilidad": z_fut, "fecha_plan": fecha_plan,
        "corrida_en": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }

    problema = _guard_versiones()
    if problema:
        salida.update({"n": 0, "descartadas_antecedente": 0,
                       "veredicto": problema})
        return salida

    df, descartadas = cargar_ventana_nueva()
    n = len(df)
    salida.update({"n": n, "descartadas_antecedente": descartadas})

    if n < n_obj:
        salida["veredicto"] = "TODAVÍA NO"
        salida["faltan"] = n_obj - n
        return salida

    # El plan fija fracciones de información 0.25/0.50/0.75/1.00 sobre
    # N_max. Si el n real las excede, el umbral que se aplica corresponde a
    # menos información de la que hay: es conservador, pero hay que decirlo.
    salida["t_real"] = n / PLAN[max(PLAN)][0]
    salida["exceso_sobre_plan"] = n - n_obj

    cmp = comparar_pareado(df["acierto_gap"].astype(bool),
                           df["base_acierto"].astype(bool))
    var = varianza_cluster(df)

    if var["degenerado"] is not None:
        salida.update({"b": var["b"], "c": var["c"], "fechas": var["fechas"],
                       "degenerado": var["degenerado"],
                       "veredicto": f"NO COMPUTABLE — {var['degenerado']}"})
        _registrar(salida)
        return salida

    z0 = (var["b"] - var["c"]) / math.sqrt(var["var_iid"])
    z_k = z0 / math.sqrt(var["v_hat"])

    salida.update({
        "acierto_modelo": cmp.acierto_a, "acierto_base": cmp.acierto_b,
        "ic_modelo": cmp.ic_a, "ic_base": cmp.ic_b,
        "ventaja_pp": cmp.ventaja_pp,
        "b": var["b"], "c": var["c"], "fechas": var["fechas"],
        "v_hat": var["v_hat"], "v_por_bloque": var["v_por_bloque"],
        "ac1": var["ac1"], "ac1_ee": var["ac1_ee"],
        "z0": z0, "z": z_k,
        "p_nominal_bilateral": 2 * (1 - norm_cdf(abs(z_k))),
        "p_mcnemar_exacto_referencia": cmp.p_mcnemar,
        "bootstrap": {kk: var[kk] for kk in
                      ("semilla", "n_draws", "bloques", "regla")},
    })

    if abs(z_k) >= umbral:
        salida["veredicto"] = "CRUZA LA FRONTERA — se para y se declara"
    elif z_fut is not None and z_k < z_fut:
        salida["veredicto"] = ("FUTILIDAD (no vinculante) — se puede parar y "
                               "declarar 'si hay ventaja, es menor que el MDE'")
    elif k == len(PLAN):
        salida["veredicto"] = "NO CRUZA en el análisis final — H₀ no se rechaza"
    else:
        salida["veredicto"] = "SIGUE — ni cruce ni futilidad"
    _registrar(salida)
    return salida


def _formatear(s: dict) -> str:
    L = [f"# Mirada {s['mirada']} del diseño secuencial",
         "",
         f"- Corrida: {s['corrida_en']}  (fecha de plan: {s['fecha_plan']})",
         f"- Filas nuevas acumuladas (posteriores a {FECHA_CONGELAMIENTO}, "
         f"convención `{CONVENCION}`): **{s['n']}**",
         f"- Filas antecedentes descartadas por construcción: {s['descartadas_antecedente']}",
         f"- n requerido por el plan: {s['n_objetivo']}", ""]
    if s["veredicto"] == "TODAVÍA NO":
        L += [f"## Veredicto: TODAVÍA NO",
              "",
              f"Faltan **{s['faltan']} filas**. El estadístico NO se computó: "
              "adelantar una mirada gasta alfa que la frontera no presupuestó "
              "(`DISEÑO.md` §A3.8).", ""]
        return "\n".join(L)
    if "z" not in s:
        L += [f"## Veredicto: {s['veredicto']}", "",
              f"discordantes b/c = {s.get('b')}/{s.get('c')} sobre "
              f"{s.get('fechas')} fechas.", ""]
        return "\n".join(L)
    if s.get("exceso_sobre_plan", 0) > 0:
        L += [f"> **Aviso:** hay {s['exceso_sobre_plan']} filas MÁS que las "
              f"{s['n_objetivo']} del plan. La fracción de información real es "
              f"t = {s['t_real']:.3f}, no la nominal de esta mirada. Se aplica "
              "el umbral del plan igual, que es la dirección conservadora "
              "(más información contra el mismo umbral), pero queda dicho.", ""]
    L += [
        "## El estadístico", "",
        f"| | |", "|---|---|",
        f"| modelo | {100*s['acierto_modelo']:.1f}% "
        f"[{100*s['ic_modelo'][0]:.1f}, {100*s['ic_modelo'][1]:.1f}] |",
        f"| baseline 'siempre al alza' | {100*s['acierto_base']:.1f}% "
        f"[{100*s['ic_base'][0]:.1f}, {100*s['ic_base'][1]:.1f}] |",
        f"| ventaja | {s['ventaja_pp']:+.1f} pp |",
        f"| discordantes b / c | {s['b']} / {s['c']} |",
        f"| fechas de emisión (clústeres) | {s['fechas']} |",
        f"| Z₀ = (b−c)/√(b+c) | {s['z0']:.4f} |",
        f"| V̂ por bloque | "
        + " · ".join(f"bloque {b}: {v:.3f}" for b, v in sorted(s['v_por_bloque'].items()))
        + " |",
        f"| **V̂ usada** ({REGLA_VARIANZA} de las anteriores) | **{s['v_hat']:.3f}** |",
        f"| autocorrelación lag-1 de d_j | {s['ac1']:+.3f} ± {s['ac1_ee']:.3f} |",
        f"| **Z = Z₀/√V̂** | **{s['z']:.4f}** |",
        f"| umbral OBF de esta mirada | {s['umbral']:.3f} |",
        f"| p nominal bilateral (referencia, NO decide) | {s['p_nominal_bilateral']:.4f} |",
        f"| McNemar exacto (referencia, NO decide) | {s['p_mcnemar_exacto_referencia']:.4f} |",
        "",
        f"Bootstrap: {s['bootstrap']}",
        "",
        f"## Veredicto: {s['veredicto']}",
        "",
    ]
    if not math.isnan(s["v_hat"]) and s["v_hat"] > 3.6:
        L += [f"> Nota: la V̂ medida ({s['v_hat']:.2f}) es mayor que la supuesta "
              "en la planificación (3.6). Esta mirada llega con menos "
              "información efectiva de la planeada, y por lo tanto con menos "
              "potencia. Si V̂ **deriva entre miradas** —y no solo es alta— las "
              "fracciones de información dejan de ser 0.25/0.50/0.75/1.00 y el "
              "α real se mueve. `DISEÑO.md` §A3.2 declara ese residuo, y "
              "declara también que NO tiene una cifra medida en este repo.", ""]
    if abs(s["ac1"]) > 2 * s["ac1_ee"]:
        L += [f"> **Atención:** la autocorrelación de fecha a fecha "
              f"({s['ac1']:+.3f} ± {s['ac1_ee']:.3f}) es distinguible de cero. "
              "Ese es el eje al que un bootstrap de clúster puro es ciego; por "
              "eso V̂ se toma como el máximo entre los bloques "
              f"{BLOQUES_FECHAS}. Verificar que los bloques largos la estén "
              "capturando antes de leer el veredicto.", ""]
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mirada", type=int, required=True, choices=sorted(PLAN))
    ap.add_argument("--escribir", action="store_true",
                    help="deja el acta en GEMELO/SECUENCIAL/miradas/")
    args = ap.parse_args()

    salida = ejecutar(args.mirada)
    texto = _formatear(salida)
    print(texto)

    if args.escribir:
        os.makedirs(DIR_ACTAS, exist_ok=True)
        ruta = os.path.join(DIR_ACTAS, f"mirada_{args.mirada}.md")
        if os.path.exists(ruta):
            # Append-only por diseño: sobrescribir un acta sería borrar la
            # evidencia de una mirada anterior con un flag.
            raise SystemExit(
                f"El acta {ruta} YA EXISTE y no se sobrescribe.\n"
                "Una mirada ya ejecutada no se vuelve a ejecutar: si hace falta "
                "revisarla, se lee el acta; si de verdad hubo que rehacerla, se "
                "declara como mirada nueva y se paga su alfa (§A3.8).\n"
                f"El registro de todas las ejecuciones está en {RUTA_REGISTRO}.")
        with open(ruta, "w", encoding="utf-8") as fh:
            fh.write(texto)
        print(f"\n[acta escrita en {ruta}]")
        print("Commitear esta acta es parte de la mirada: el plan exige que la")
        print("salida quede en el repo en la fecha del calendario, cruce o no.")
    if "z" in salida:
        print(f"\n[esta ejecución quedó registrada en {RUTA_REGISTRO} — toda "
              "corrida que computa el estadístico deja línea, con --escribir o "
              "sin él]")


if __name__ == "__main__":
    main()
