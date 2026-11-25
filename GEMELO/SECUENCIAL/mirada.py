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

CINCO candados, para que el script no pueda usarse mal: tres
estructurales, más uno por cada parámetro sin firmar.

0. **No computa mientras falte una firma.** `MDE_FIRMADO` y
   `REGLA_DEDUP_ESTIMADOR` están en `None` y `ejecutar()` aborta con
   cualquiera de los dos así. El primero fija el n de la mirada; el segundo,
   cómo se agrupan los clústeres, o sea la varianza — el denominador del
   estadístico. Los dos tienen test.
1. **No puede mirar la ventana antecedente.** Descarta por construcción
   toda fila con `fecha` <= FECHA_CONGELAMIENTO: hoy son las 262 filas de la
   ventana antecedente anclada, y volver a analizarlas es "la trampa de esta
   etapa".
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
# EL PLAN QUE SE PROPONE CONGELAR. Estas constantes son el pre-registro: si
# alguna cambia DESPUÉS DE LA FIRMA, el diseño terminó y hay que decirlo con
# acta.
#
# OJO con la redacción anterior de este encabezado, que decía «EL PLAN,
# CONGELADO ... si alguna cambia después del 31-ago-2026». **El documento
# nunca se congeló**, y el acta de congelamiento llama a esa fecha SIN
# FIRMAR: el archivo que hace exigible el régimen no puede declarar
# congelado lo que el acta deja abierto. Lo cazó el `curador-epistemico` en
# la corrida 17.
# ---------------------------------------------------------------------------

# La frontera de la población, de §A2. **Es uno de los parámetros SIN
# FIRMAR** (tarjeta §93: el documento nunca se congeló, así que desde cuándo
# cuenta la población es una decisión). Está escrita acá porque el candado
# estructural de `cargar_ventana_nueva` la necesita para poder descartar la
# ventana antecedente; que esté escrita no la firma.
FECHA_CONGELAMIENTO = "2026-08-31"
CONVENCION = "excluir_cero"          # GEMELO/DISEÑO.md §2.8

# EL MDE — uno de los DOS parámetros con candado en este archivo (el otro es
# `REGLA_DEDUP_ESTIMADOR`, más abajo), y uno de los cuatro sin firmar del
# pre-registro. `DISEÑO.md` §A3.1 lo deriva en la escala del endpoint:
# **8.51 pp, IC95 [4.94, 13.09]**. Mientras valga None, este script se niega
# a computar: correr una mirada con un N_max que nadie firmó sería elegir el
# tamaño de muestra después de ver los datos, que es lo mismo que elegir el
# umbral después de ver los datos.
MDE_FIRMADO = None
# OJO — el valor que esta línea ofrecía antes está **RETIRADO** desde el
# 31-ago (acta §56): se derivó en la escala del retorno de sesión cuando el
# endpoint congelado es `acierto_gap`. El que lo reemplazó en la cabecera de
# la v5 está **a su vez objetado** —su intervalo era el de E|gap| invertido,
# un insumo de tres, como mostró el Frente D del 1-sep— y la corrida 17 lo
# recomputó. **NINGÚN valor está firmado**, y ofrecer uno acá sería poner el
# dedo en la balanza: por eso esta constante queda en None y el número vive
# en `mde_desde_v6.py`, que lo computa.
MDE_PROPUESTO = None

# ---------------------------------------------------------------------------
# LA REGLA DE DEDUPLICACIÓN DEL ESTIMADOR — el segundo parámetro SIN FIRMAR.
# ---------------------------------------------------------------------------
# Hay DOS reglas de deduplicación y la v5 las confundía en una.
#
#   1. La regla de FILAS, FIRMADA el 1-sep-2026 (actas §60 y §61):
#      `backtest.linea_base.deduplicar_por_sesion`, que `cargar()` aplica
#      por defecto. Dentro de cada grupo `(ticker, sesion_objetivo)`
#      conserva la fila cuya `sesion_objetivo` corresponde a su
#      `available_at`. En los pares del defecto de `snapshot.py` eso deja
#      UNA fila; en los pares de FERIADO las dos corresponden y se
#      conservan las DOS. `keep="last"` quedó PROHIBIDA por esa acta.
#      Esta regla ya está vigente y este módulo la hereda de `cargar()`.
#
#   2. La regla del ESTIMADOR, que es la que falta: qué hace el estadístico
#      con los pares que la regla de filas CONSERVA. Es una pregunta
#      distinta, y es la que el cuarto dictamen señaló como el defecto
#      descalificante: `contribuciones_por_fecha` agrupa por FECHA DE
#      EMISIÓN, y las dos filas de un par de feriado tienen fechas de
#      emisión distintas, así que caen en clústeres distintos aunque
#      apunten a la misma sesión. Si su resultado está correlacionado —y lo
#      está, porque es el gap de la MISMA sesión— el bootstrap de fechas
#      las trata como independientes y `V̂` sale corta.
#
# UNA CORRECCIÓN AL CUARTO DICTAMEN, que importa para elegir. El dictamen
# dice que los pares tienen «resultado idéntico». Es cierto del GAP y no
# tiene por qué ser cierto del ACIERTO: las dos filas comparten
# `gap_pct` porque comparten sesión objetivo, pero se emitieron en fechas
# distintas y por lo tanto con predicciones distintas, así que
# `acierto_gap` puede diferir. Lo que McNemar puntúa es el acierto, no el
# gap. Esta corrida NO mide si difieren: medirlo es computar una función del
# acierto, y el encargo no recomputa ninguna sobre ninguna de las dos
# ventanas. Queda dicho como lo que es —una posibilidad lógica que la
# elección tiene que contemplar— y no como un hallazgo.
#
# Mientras valga None este módulo se niega a computar, por la misma razón
# que con el MDE: elegir cómo se agrupan los clústeres después de ver los
# datos es elegir la varianza después de verlos, y la varianza es el
# denominador del estadístico.
REGLA_DEDUP_ESTIMADOR = None

# Las opciones, declaradas ANTES de que ninguna se corra sobre datos reales.
# `keep_last` está en la lista porque la v5 publicó su p en su cabecera y
# por lo tanto está a la vista de quien firma; está marcada PROHIBIDA
# porque el acta §60 la prohibió, y ofrecerla sin la marca sería ofrecer una
# rama vetada.
# OJO CON LA PALABRA «PAR», y es la exigencia E8 del quinto dictamen: en la
# POBLACIÓN los grupos `(ticker, sesion_objetivo)` son **11 de DOS filas y 4
# de CUATRO** (38 filas en 15 grupos). En la ventana antecedente, **bajo la
# regla de filas FIRMADA, son 5 grupos de dos** (10 filas); los 15 de dos (30
# filas) son la rama SIN esa regla, o sea la que D1 derogó, y citarla acá sin
# decirlo —como hacía este comentario— ponía la cifra de la rama derogada dos
# líneas arriba de las opciones que hay que elegir, cuando la decisión versa
# sobre los grupos que la regla de filas CONSERVA. Lo cazó el dictamen de
# cierre (O-7). Las glosas de abajo hablan de GRUPOS y no de pares porque
# «el par» es
# falso en 4 de los 15 grupos, y porque sobre un grupo de cuatro
# `colapsar_el_par` descarta TRES filas y no una. El acta §60 firmó la rama
# de feriados razonando sobre DOS emisiones igualmente a tiempo: **cuatro
# emisiones apuntando a una sesión es un caso que esa acta no decidió.**
REGLAS_DEDUP_ESTIMADOR = {
    "conservar_ambas": "todas las filas del grupo entran, clúster por fecha "
                       "de emisión (lo que el código hace hoy). Sobre un "
                       "grupo de cuatro, cuatro clústeres distintos con el "
                       "mismo desenlace",
    "clusterizar_por_sesion_objetivo": "todas las filas entran, pero el "
                                       "clúster es la SESIÓN OBJETIVO, así "
                                       "que el grupo entero cae en UN solo "
                                       "clúster, sea de dos o de cuatro",
    "colapsar_el_par": "el grupo se colapsa en UNA observación: descarta "
                       "una de dos, y TRES de cuatro. COINCIDE con "
                       "`keep_first` y no es una quinta opción: colapsar "
                       "exige decir qué fila sobrevive, y la única que no "
                       "elige por frescura es la más temprana. La otra "
                       "lectura de «colapsar» —AGREGAR las filas en una— "
                       "necesitaría una regla de empate para un acierto "
                       "binario, o sea una convención nueva, y la convención "
                       "está congelada (§A3.7 cláusula 4)",
    "keep_first": "se conserva la emisión más temprana de cada grupo "
                  "(NO es la regla firmada: la firmada arbitra por "
                  "correspondencia de sesión, no por orden)",
    "keep_last": "PROHIBIDA por el acta §60 del 1-sep-2026: retira "
                 "selectivamente errores del modelo",
}
REGLAS_PROHIBIDAS = ("keep_last",)

# N_max por MDE, de `diseno_secuencial` (Connor × DEFF × el factor
# secuencial computado, `diseno_secuencial.factor_secuencial()`). Los
# umbrales y la futilidad NO dependen del MDE: dependen de la fracción de
# información y del α, así que valen igual para cualquiera de los dos.
#
# CORRIDA 17: este diccionario ya no se usa como tabla cerrada. `N_max` se
# computa desde `diseno_secuencial` con el `p_d` de la ventana antecedente
# ANCLADA, porque los dos valores que estaban cableados acá se derivaron con
# un `p_d` que salía de la rama de filas que la decisión D1 derogó el
# 3-sep-2026. Se conserva vacío a propósito: un diccionario con dos entradas
# viejas es una invitación a firmar una de las dos.
N_MAX_POR_MDE: dict[float, int] = {}
UMBRALES_OBF = (4.048, 2.862, 2.337, 2.024)
Z_FUTILIDAD = (-1.662, 0.016, 1.033, None)
FRACCIONES = (0.25, 0.50, 0.75, 1.00)

# Las fechas estimadas ya NO viven en una tabla cableada. La v5 las fijaba
# al ritmo de la ventana ANTECEDENTE porque la población no existía; hoy el
# ritmo se mide donde ocurre, por conteo, y la tabla completa la produce
# `GEMELO/SECUENCIAL/tabla_firma.py`. Dos tuplas de fechas cableadas en este
# módulo serían dos fechas que envejecen en silencio.
FECHAS_POR_MDE: dict[float, tuple] = {}


def _n_max(mde: float, p_d: float | None = None) -> int:
    """`N_max` del plan, delegado a `diseno_secuencial.n_max_del_plan`.

    Se computa en vez de leerse de una tabla, porque los dos valores que la
    tabla traía se derivaron con un `p_d` que salía de la rama de filas que
    la decisión D1 de Nicolás derogó el 3-sep-2026 (acta §78).

    **Y se DELEGA en vez de repetir la cuenta.** Hasta el dictamen de cierre
    de la corrida 17 esta función multiplicaba por un `1.0241` cableado
    mientras `tabla_firma.py` ya usaba el factor computado: eso dejó dos
    respuestas distintas a «¿con qué n se dispara la mirada 1?» —354 acá y
    355 allá— entre el script que CORRE la mirada y la tabla que se FIRMA.
    Un pre-registro con dos `N_max` no reproduce el día que se firma, que es
    la vara del cuarto dictamen. Ahora el factor vive en un solo lugar.
    """
    import diseno_secuencial as D
    return round(D.n_max_del_plan(mde, p_d=p_d))


def plan(mde: float | None = None, p_d: float | None = None,
         fechas: tuple | None = None) -> dict:
    """(n de filas, umbral |Z|, Z de futilidad, fecha estimada) por mirada.

    `fechas` es opcional: las fechas son una ESTIMACIÓN al ritmo del momento
    y la mirada la dispara el n, no la fecha. Quien las quiera las pasa
    (`tabla_firma.py` las computa desde el ritmo medido); sin ellas el plan
    es igual de válido y la cuarta posición viene en None.
    """
    mde = mde if mde is not None else MDE_FIRMADO
    if mde is None:
        raise SystemExit(
            "MDE SIN FIRMAR, y hoy NO hay número propuesto.\n"
            "El valor que este módulo ofrecía en la escala del retorno de "
            "sesión quedó RETIRADO el 31-ago, y el que lo reemplazó traía "
            "como intervalo el de E|gap| invertido —un insumo de tres—, "
            "que el Frente D del 1-sep ya había objetado.\n"
            "La corrida 17 (25-oct-2026) dejó el número y su intervalo "
            "recomputados sobre la ventana antecedente ANCLADA, con dos "
            "insumos propagados, en `GEMELO/SECUENCIAL/mde_desde_v6.py`, y "
            "la tabla de la firma —N_max, el n de cada mirada y su fecha al "
            "ritmo medido— en `GEMELO/SECUENCIAL/tabla_firma.py`. La "
            "elección sigue siendo de Nicolás.\n"
            "Correr una mirada con un N_max que nadie fijó es elegir el "
            "tamaño de muestra después de ver los datos.\n"
            "Poner `MDE_FIRMADO` cuando la decisión esté escrita y fechada "
            "en DECISIONES.md.")
    n_max = _n_max(mde, p_d)
    fechas = fechas if fechas is not None else (None,) * len(FRACCIONES)
    return {k + 1: (round(t * n_max), UMBRALES_OBF[k], Z_FUTILIDAD[k], fechas[k])
            for k, t in enumerate(FRACCIONES)}


def _guard_regla_estimador(regla: str | None = None) -> str:
    """El candado de la regla de deduplicación del ESTIMADOR.

    Mismo argumento que el candado del MDE: elegir cómo se agrupan los
    clústeres después de ver los datos es elegir la varianza después de
    verlos, y la varianza es el denominador del estadístico. El cuarto
    dictamen midió que la elección de la regla de FILAS valía la diferencia
    entre un veredicto y el contrario; la de clústeres mueve `V̂`, que es
    exactamente lo mismo un escalón más abajo.
    """
    regla = REGLA_DEDUP_ESTIMADOR if regla is None else regla
    if regla is None:
        raise SystemExit(
            "REGLA DE DEDUPLICACIÓN DEL ESTIMADOR SIN FIRMAR.\n"
            "La regla de FILAS está firmada (actas §60 y §61, 1-sep-2026) y "
            "`cargar()` la aplica. Lo que falta es qué hace el ESTADÍSTICO "
            "con los pares que esa regla CONSERVA: hoy `contribuciones()` "
            "agruparía por fecha de emisión, y las dos filas de un par de "
            "feriado tienen fechas de emisión distintas y la MISMA sesión "
            "objetivo, así que caerían en clústeres distintos y `V̂` saldría "
            "corta.\n"
            "Las opciones están declaradas en `REGLAS_DEDUP_ESTIMADOR` y la "
            "tarjeta correspondiente de `GEMELO/resultados/espera_firma.md` "
            "las pone con su conteo al lado. NO se computa nada hasta que "
            "haya una firma fechada en DECISIONES.md.")
    if regla in REGLAS_PROHIBIDAS:
        raise SystemExit(
            f"La regla `{regla}` está PROHIBIDA por el acta §60 del "
            "1-sep-2026: retira selectivamente errores del modelo. Está en "
            "la lista para que quede constancia de que se consideró, no para "
            "poder elegirla.")
    if regla not in REGLAS_DEDUP_ESTIMADOR:
        raise SystemExit(f"Regla desconocida: {regla}. Las declaradas son "
                         f"{sorted(REGLAS_DEDUP_ESTIMADOR)}.")
    return regla


def aplicar_regla_estimador(df, regla: str | None = None):
    """(df, clave de clúster) según la regla del estimador.

    Es PURA: no consulta la base y no depende de la fecha, así que los
    tests la ejercitan entera sobre datos sintéticos con pares plantados.
    """
    regla = _guard_regla_estimador(regla)
    if regla == "clusterizar_por_sesion_objetivo":
        return df, "sesion_objetivo"
    if regla in ("colapsar_el_par", "keep_first"):
        # Una observación por (ticker, sesión objetivo): la de emisión más
        # temprana. Las dos reglas comparten rama porque son la MISMA
        # operación —ver `REGLAS_DEDUP_ESTIMADOR`—, y escribirlas dos veces
        # habría hecho pasar por distintas dos cosas que no lo son.
        # El orden es por fecha y no por el orden en que la base devolvió
        # las filas: un `drop_duplicates` sobre un frame sin ordenar depende
        # del `ORDER BY` del SQL, que no es parte del pre-registro.
        orden = df.sort_values(["ticker", "sesion_objetivo", "fecha"],
                               kind="stable")
        return (orden.drop_duplicates(["ticker", "sesion_objetivo"],
                                      keep="first")
                     .sort_values(["fecha", "ticker"], kind="stable")
                     .reset_index(drop=True), "fecha")
    return df, "fecha"          # conservar_ambas


# `PLAN` ya no se materializa al importar: con el MDE retirado no hay
# ningún valor por defecto honesto, y fabricar uno "para poder
# inspeccionarlo" es exactamente cómo un número retirado vuelve a
# circular. Quien quiera ver un plan hipotético llama a `plan(0.07)` o
# `plan(0.10)` explícitamente y se hace cargo de lo que está mirando.

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


def contribuciones(df, clave: str = "fecha") -> np.ndarray:
    """d_j = Σ_i (acierto_modelo − acierto_base) sobre las filas del clúster j.

    `b − c` se descompone EXACTAMENTE como la suma de estas contribuciones,
    y por eso la varianza de `b − c` se puede estimar remuestreando
    clústeres.

    `clave` es lo que define el clúster y lo fija la regla del estimador
    (`REGLA_DEDUP_ESTIMADOR`): `"fecha"` es la fecha de emisión —lo que el
    código hacía siempre— y `"sesion_objetivo"` la sesión que la predicción
    anticipa. La diferencia sólo existe para los pares que apuntan a la
    misma sesión desde fechas de emisión distintas, y es justamente ahí
    donde el cuarto dictamen dijo que el estimador se rompía.
    """
    return (df.groupby(clave)
              .apply(lambda g: int((g["acierto_gap"].astype(int)
                                    - g["base_acierto"].astype(int)).sum()),
                     include_groups=False)
              .to_numpy(dtype=float))


def contribuciones_por_fecha(df) -> np.ndarray:
    """Alias histórico de `contribuciones(df, "fecha")`.

    Se conserva porque `diseno_secuencial.ac1_ventana_antecedente` y los
    tests lo nombran, y porque el clúster por fecha de emisión sigue siendo
    una de las opciones declaradas. No es el default del estadístico: el
    default no existe hasta que la regla se firme.
    """
    return contribuciones(df, "fecha")


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


def varianza_cluster(df, clave: str = "fecha") -> dict:
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
    d = contribuciones(df, clave)
    b = int(((df["acierto_gap"] == 1) & (df["base_acierto"] == 0)).sum())
    c = int(((df["acierto_gap"] == 0) & (df["base_acierto"] == 1)).sum())
    var_iid = float(b + c)
    ac1, ac1_ee = autocorrelacion_lag1(d)

    base = {
        "b": b, "c": c, "fechas": len(d), "clave_cluster": clave,
        "var_iid": var_iid,
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
    ahora = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    # El guard de versiones va PRIMERO: un diseño terminado por relevo está
    # terminado aunque el MDE nunca se hubiera firmado, y decir "falta el
    # MDE" cuando en realidad cambió el modelo sería el mensaje equivocado.
    problema = _guard_versiones()
    if problema:
        return {"mirada": k, "corrida_en": ahora, "n": 0,
                "descartadas_antecedente": 0, "veredicto": problema}

    # Los dos candados de parámetros sin firmar, en este orden: el MDE fija
    # el n de la mirada, así que su ausencia se ve primero. Los dos levantan
    # SystemExit y ninguno computa nada.
    n_obj, umbral, z_fut, fecha_plan = plan()[k]
    regla = _guard_regla_estimador()
    salida = {
        "mirada": k, "n_objetivo": n_obj, "umbral": umbral,
        "z_futilidad": z_fut, "fecha_plan": fecha_plan,
        "corrida_en": ahora,
    }

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
    _plan = plan()
    salida["t_real"] = n / _plan[max(_plan)][0]
    salida["exceso_sobre_plan"] = n - n_obj

    df, clave = aplicar_regla_estimador(df, regla)
    salida["regla_estimador"] = regla
    salida["clave_cluster"] = clave
    salida["n_tras_regla_estimador"] = len(df)

    cmp = comparar_pareado(df["acierto_gap"].astype(bool),
                           df["base_acierto"].astype(bool))
    var = varianza_cluster(df, clave)

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
    elif k == len(_plan):
        salida["veredicto"] = "NO CRUZA en el análisis final — H₀ no se rechaza"
    else:
        salida["veredicto"] = "SIGUE — ni cruce ni futilidad"
    _registrar(salida)
    return salida


def _formatear(s: dict) -> str:
    plan_txt = (f"fecha de plan: {s['fecha_plan']}" if s.get("fecha_plan")
                else "sin fecha de plan: la mirada la dispara el n, y la "
                     "fecha estimada la computa `tabla_firma.py` al ritmo "
                     "medido del momento")
    L = [f"# Mirada {s['mirada']} del diseño secuencial",
         "",
         f"- Corrida: {s['corrida_en']}  ({plan_txt})",
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
        f"| regla del estimador | `{s.get('regla_estimador')}` "
        f"(clúster = `{s.get('clave_cluster')}`) |",
        f"| filas tras la regla del estimador | "
        f"{s.get('n_tras_regla_estimador')} |",
        f"| clústeres | {s['fechas']} |",
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
    # Las cuatro miradas existen por construcción (las fracciones de
    # información son 0.25/0.50/0.75/1.00); lo que el MDE mueve es su n,
    # no cuántas son. Por eso el CLI no necesita el plan materializado.
    ap.add_argument("--mirada", type=int, required=True,
                    choices=range(1, len(FRACCIONES) + 1))
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
