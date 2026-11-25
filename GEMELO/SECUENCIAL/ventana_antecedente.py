"""ventana_antecedente.py — las DOS ventanas del pre-registro, ancladas.

Existe por la **condición 4** del cuarto dictamen: *«un pre-registro que no
reproduce el día que se firma no está congelado, está fechado»*. La causa
raíz que el dictamen nombró es que `mde_desde_v6.py` escribía su propio SQL
y por lo tanto **no tenía ancla temporal**: con corte del 26-ago el MDE daba
un número, con el del 28-ago otro, y «hoy» otro. Este módulo es el único
lugar donde se define qué filas son la ventana antecedente, y lo hace con
dos cortes explícitos en vez de con el reloj.

`DISEÑO.md` §A2 parte la base en dos y la partición es del pre-registro, no
de este módulo:

  * **POBLACIÓN** — filas con fecha de emisión **posterior** al
    `CORTE_EMISION`. Son las que el estadístico va a usar, y sobre ellas
    está prohibido computar cualquier función del resultado (§A3.8: una
    sola mirada furtiva lleva el α del plan de 0.05 a 0.094).
  * **VENTANA ANTECEDENTE** — el complemento exacto: fecha de emisión hasta
    el `CORTE_EMISION`. No aporta un solo grado de libertad a ninguna
    mirada; aporta los parámetros de estorbo de §A2 (`p_d`, DEFF, `ac1`) y
    los insumos del MDE (`f`, `E|gap|`).

**Por qué hacen falta DOS cortes y no uno.** `backtest.linea_base.cargar`
ancla por `verificado_en` (`hasta_sello`), que es el instante en que la
fila entró a las métricas; el pre-registro parte por `fecha` de emisión.
Los dos cortes no son el mismo conjunto: una fila emitida el último día de
agosto puede haberse verificado en septiembre. Un corte de emisión solo
**no es inmune al reloj** —una verificación tardía agrandaría la ventana
antecedente—, y un corte de sello solo **no es el complemento de la
población**. Así que se aplican los dos: `hasta_sello=CORTE_SELLO` congela
el conjunto, y el filtro por `fecha <= CORTE_EMISION` lo hace coincidir con
la partición de §A2.

**El candado que no depende de la memoria de nadie:** `CORTE_SELLO` sólo es
válido si ninguna fila emitida hasta el `CORTE_EMISION` se verificó después
de él. Eso es verificable con un conteo —`cierre_de_ventana()`— y el
cargador lo exige. Si algún día una verificación tardía lo rompe, la
función lo dice en vez de devolver una ventana distinta en silencio, que es
exactamente el modo de falla que la condición 4 vino a cerrar.

**LO QUE ESTE MÓDULO AMPUTA, A PROPÓSITO.** `cargar_poblacion()` devuelve
las filas de la población **sin ninguna columna de resultado**: lo que no
está no se puede computar por descuido. Contar filas y leer sus fechas,
tickers, sesiones objetivo y estado es legítimo y es lo que el calendario
necesita; cualquier cosa que dependa de `gap_pct`, de `retorno_real_pct` o
del acierto es una mirada y se paga en α.

**La convención `excluir_cero` NO se aplica a la población**, y es una
consecuencia de lo anterior: `gap_pct == 0` es una función de `gap_pct`.
El conteo de la población es por lo tanto un **techo** del n del plan —la
convención sólo puede retirar filas—, así que las fechas estimadas de las
miradas que salen de acá son **más tempranas** que las reales. Para una
firma con plazo, equivocarse en esa dirección es lo correcto. La magnitud
del sesgo se mide en la ventana antecedente, donde computar sí está
permitido (`tasa_empates_antecedente()`).

SOLO LECTURA. `senales.db` se abre en `mode=ro` a través de
`backtest.linea_base`. No importa `motor.py`, no toca una fila sellada y no
escribe en ninguna base.

Corre con:  python -m GEMELO.SECUENCIAL.ventana_antecedente
"""
from __future__ import annotations

import datetime as dt
import os
import sys

import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from backtest import linea_base as lb  # noqa: E402

# ---------------------------------------------------------------------------
# LOS DOS CORTES
# ---------------------------------------------------------------------------

# La fecha de congelamiento propuesta por §A2. Es parte del pre-registro y
# vale lo mismo acá y en `mirada.FECHA_CONGELAMIENTO`; hay test.
CORTE_EMISION = "2026-08-31"

# El cierre de la ventana antecedente, MEDIDO y no elegido: la última
# verificación de una fila emitida hasta el `CORTE_EMISION`. Al 25-oct-2026
# es el 2026-09-02 (verificación de las 22:15 UTC). Subirlo no agranda la
# ventana mientras `cierre_de_ventana()["tardias"]` sea 0; bajarlo la
# amputaría. No se toca sin acta: es el ancla que hace reproducible todo lo
# que este módulo alimenta.
CORTE_SELLO = "2026-09-02"

CONVENCION = lb.CONVENCION_OFICIAL      # `excluir_cero`, GEMELO/DISEÑO.md §2.8

# Las columnas que `cargar_poblacion()` amputa. Son todas las que dependen
# del resultado de la predicción, directa o indirectamente.
COLUMNAS_DE_RESULTADO = ("gap_pct", "retorno_real_pct", "acierto_gap",
                         "error_gap_pp", "apertura_estimada_pct",
                         "base_acierto")


class VentanaAbierta(RuntimeError):
    """`CORTE_SELLO` ya no cierra la ventana antecedente."""


# ---------------------------------------------------------------------------
# El candado
# ---------------------------------------------------------------------------

def cierre_de_ventana() -> dict:
    """Cuántas filas emitidas hasta `CORTE_EMISION` se verificaron DESPUÉS
    de `CORTE_SELLO`. Tiene que ser 0: si no lo es, el corte de sello ya no
    es el cierre de la ventana y la ventana antecedente crecería con el
    reloj, que es el defecto de la condición 4.

    Es un conteo sobre fechas: no toca ninguna columna de resultado.
    """
    if not os.path.exists(lb.RUTA_SENALES):
        return {"base": False, "tardias": 0, "ultima_verificacion": None}
    conn = lb._conexion_ro(lb.RUTA_SENALES)
    try:
        fila = conn.execute(
            """SELECT COUNT(*), MAX(verificado_en)
                 FROM verificacion_apertura
                WHERE legacy = 0 AND modelo_version = ?
                  AND gap_pct IS NOT NULL
                  AND fecha_senal <= ?
                  AND substr(verificado_en, 1, 10) > ?""",
            (lb.MODELO_VERSION, CORTE_EMISION, CORTE_SELLO)).fetchone()
        ultima = conn.execute(
            """SELECT MAX(verificado_en)
                 FROM verificacion_apertura
                WHERE legacy = 0 AND modelo_version = ?
                  AND gap_pct IS NOT NULL AND fecha_senal <= ?""",
            (lb.MODELO_VERSION, CORTE_EMISION)).fetchone()[0]
    finally:
        conn.close()
    return {"base": True, "tardias": int(fila[0]),
            "tardia_mas_nueva": fila[1], "ultima_verificacion": ultima}


# ---------------------------------------------------------------------------
# La ventana antecedente — acá sí se puede computar
# ---------------------------------------------------------------------------

def cargar_antecedente(convencion: str | None = CONVENCION,
                       dedup: bool = True,
                       exigir_cierre: bool = True) -> pd.DataFrame:
    """Las filas de la ventana antecedente, con los dos cortes aplicados.

    `dedup` va en `True`: es la **regla firmada el 1-sep-2026**
    (`lb.deduplicar_por_sesion`), la misma que aplican las dos ventanas del
    proyecto. La rama sin deduplicar existe sólo para contar qué retira la
    regla, nunca para publicar un parámetro.

    `convencion=None` devuelve las filas sin aplicar `excluir_cero`, que es
    lo que hace falta para medir cuántos empates hay.
    """
    if exigir_cierre:
        estado = cierre_de_ventana()
        if estado["base"] and estado["tardias"]:
            raise VentanaAbierta(
                f"{estado['tardias']} fila(s) emitida(s) hasta {CORTE_EMISION} "
                f"se verificaron después de CORTE_SELLO={CORTE_SELLO} "
                f"(la más nueva, {estado['tardia_mas_nueva']}). La ventana "
                "antecedente dejó de estar cerrada: subir CORTE_SELLO con "
                "acta, y volver a correr todo lo que depende de ella. No se "
                "devuelve una ventana distinta en silencio.")
    df = lb.cargar(hasta_sello=CORTE_SELLO, dedup=dedup)
    if df.empty:
        return df
    df = df[df["fecha"] <= CORTE_EMISION].reset_index(drop=True)
    if convencion is None:
        return df
    return lb.aplicar_convencion(df, convencion).reset_index(drop=True)


def tasa_empates_antecedente() -> dict:
    """Qué fracción de la ventana antecedente retira `excluir_cero`.

    Es el único lugar donde se mide la magnitud del sesgo que el conteo de
    la población arrastra por NO poder aplicar la convención (ver cabecera).
    Se mide acá porque acá computar está permitido.
    """
    crudo = cargar_antecedente(convencion=None)
    if crudo.empty:
        return {"n_sin_convencion": 0, "n_con_convencion": 0,
                "empates": 0, "tasa": float("nan")}
    con = lb.aplicar_convencion(crudo, CONVENCION)
    empates = len(crudo) - len(con)
    return {"n_sin_convencion": len(crudo), "n_con_convencion": len(con),
            "empates": empates, "tasa": empates / len(crudo)}


# ---------------------------------------------------------------------------
# La población — acá NO se puede computar, y el cargador lo hace imposible
# ---------------------------------------------------------------------------

def cargar_poblacion(dedup: bool = True) -> pd.DataFrame:
    """Las filas de la POBLACIÓN, **sin columnas de resultado**.

    Lo que queda: `fecha`, `ticker`, `exchange`, `sesion_objetivo`,
    `available_at` y lo que no dependa del resultado. Lo que se va:
    `COLUMNAS_DE_RESULTADO`. No es una convención de estilo — es el candado
    de §A3.8 hecho estructura, porque el número está a un comando de
    distancia y la regla escrita no alcanza para que nadie lo escriba.

    `excluir_cero` **no** se aplica (es una función de `gap_pct`), así que
    `len()` de esto es un techo del n del plan. Ver cabecera.
    """
    df = lb.cargar(hasta_sello=None, dedup=dedup)
    if df.empty:
        return df
    df = df[df["fecha"] > CORTE_EMISION].reset_index(drop=True)
    return df.drop(columns=[c for c in COLUMNAS_DE_RESULTADO
                            if c in df.columns])


def _dias_habiles(desde: dt.date, hasta: dt.date) -> int:
    """Días hábiles (lun-vie) en `(desde, hasta]`. No sabe de feriados: el
    ritmo se mide contra el mismo denominador que usa `diseno_secuencial`,
    y los feriados ya están dentro de las filas que se cuentan."""
    dias = 0
    d = desde + dt.timedelta(days=1)
    while d <= hasta:
        if d.weekday() < 5:
            dias += 1
        d += dt.timedelta(days=1)
    return dias


def ritmo_poblacion(dedup: bool = True) -> dict:
    """El ritmo de acumulación de la población, por CONTEO.

    Devuelve filas, fechas de emisión, días hábiles transcurridos y filas
    por día hábil. Todo son conteos y fechas: no hay ninguna función del
    resultado acá, y por eso se puede correr tantas veces como haga falta
    sin gastar α.
    """
    df = cargar_poblacion(dedup=dedup)
    if df.empty:
        return {"filas": 0, "fechas": 0, "primera": None, "ultima": None,
                "dias_habiles": 0, "filas_por_dia_habil": float("nan"),
                "dedup": dedup}
    primera, ultima = str(df["fecha"].min()), str(df["fecha"].max())
    habiles = _dias_habiles(dt.date.fromisoformat(CORTE_EMISION),
                            dt.date.fromisoformat(ultima))
    return {"filas": len(df), "fechas": int(df["fecha"].nunique()),
            "primera": primera, "ultima": ultima, "dias_habiles": habiles,
            "filas_por_dia_habil": len(df) / habiles if habiles else float("nan"),
            "dedup": dedup}


def fecha_para_filas(objetivo: int, filas_por_dia_habil: float,
                     filas_hoy: int, ultima: str) -> dt.date | None:
    """La fecha estimada en que la población alcanza `objetivo` filas.

    Cuenta hacia adelante **día hábil por día hábil** desde la última fecha
    de emisión observada, en vez de multiplicar por 7/5 como hacía
    `diseno_secuencial.fecha_para_filas`: ese factor mete fines de semana a
    prorrata y corre la fecha unos días. Devuelve None si ya se alcanzó.
    """
    if filas_hoy >= objetivo:
        return None
    if not (filas_por_dia_habil > 0):
        return None
    faltan = objetivo - filas_hoy
    habiles = faltan / filas_por_dia_habil
    d = dt.date.fromisoformat(ultima)
    restantes = habiles
    while restantes > 0:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            restantes -= 1
    return d


# ---------------------------------------------------------------------------
# Pares que apuntan a la misma sesión objetivo — conteo, en las dos ventanas
# ---------------------------------------------------------------------------

def pares_misma_sesion(df: pd.DataFrame) -> dict:
    """Grupos `(ticker, sesion_objetivo)` con más de una fila.

    Es un conteo sobre identificadores y fechas: vale igual en la ventana
    antecedente y en la población, y es lo que la tarjeta de la regla de
    deduplicación del estimador necesita para decidirse por principio en
    vez de por resultado.
    """
    if df.empty or "sesion_objetivo" not in df.columns:
        return {"filas": len(df), "filas_en_pares": 0, "grupos": 0,
                "reparto_por_tamano": {}, "grupo_mas_grande": 0,
                "sesiones": [], "fechas_de_emision": []}
    dup = df[df.duplicated(["ticker", "sesion_objetivo"], keep=False)]
    if dup.empty:
        return {"filas": len(df), "filas_en_pares": 0, "grupos": 0,
                "reparto_por_tamano": {}, "grupo_mas_grande": 0,
                "sesiones": [], "fechas_de_emision": []}
    tamanos = dup.groupby(["ticker", "sesion_objetivo"]).size()
    # LA DISTRIBUCIÓN DE TAMAÑOS, por exigencia E8 del quinto dictamen. Sin
    # ella esta función imprimía «38 filas en 15 grupos» al lado de una prosa
    # que decía «pares» — y 15 pares son 30 filas, no 38. El entero que
    # contradecía al texto se imprimía junto al texto sin que nadie los
    # cruzara, que es el defecto que el pre-registro se reprocha a sí mismo.
    # En la población hay grupos de CUATRO, y «el par» no los describe.
    reparto = {int(k): int(v) for k, v in
               sorted(tamanos.value_counts().items())}
    return {
        "filas": len(df),
        "filas_en_pares": len(dup),
        "grupos": int(tamanos.size),
        "reparto_por_tamano": reparto,
        "grupo_mas_grande": int(tamanos.max()),
        "sesiones": sorted(str(s) for s in dup["sesion_objetivo"].unique()),
        "fechas_de_emision": sorted(str(f) for f in dup["fecha"].unique()),
        "tickers": sorted(str(t) for t in dup["ticker"].unique()),
    }


def boot_dias(df: pd.DataFrame, fn, n_boot: int = 10_000,
              semilla: int = 20260901):
    """Bootstrap de CLÚSTERES DE DÍA. La unidad real de este experimento.

    Las ~7 filas de una fecha de emisión son βᵢ·SOX sobre el MISMO
    movimiento del SOX: aciertan y fallan casi todas juntas. Un bootstrap de
    filas produce intervalos falsamente angostos, y uno de bloques de 20
    filas también, porque el bloque no respeta el borde del día.

    `fn` recibe un array de índices posicionales y devuelve un escalar. Es
    el MISMO método, los mismos `n_boot` y la misma semilla que
    `mde_vs_observado._boot_dias`, que es el otro lugar del repo donde vive;
    un test comprueba que los dos devuelven la MISMA muestra para el mismo
    insumo, para que la duplicación sea exigible en vez de silenciosa.
    """
    import numpy as np
    fecha = df["fecha"].to_numpy()
    dias = pd.unique(fecha)
    idx = {d: np.where(fecha == d)[0] for d in dias}
    rng = np.random.default_rng(semilla)
    out = []
    for _ in range(n_boot):
        sel = rng.choice(dias, size=len(dias), replace=True)
        out.append(fn(np.concatenate([idx[d] for d in sel])))
    return np.array(out)


def resumen() -> dict:
    """Todo lo que este módulo mide, en un dict, para que los demás scripts
    no vuelvan a consultar la base por su cuenta."""
    cierre = cierre_de_ventana()
    ant = cargar_antecedente()
    ant_sin_dedup = cargar_antecedente(dedup=False)
    return {
        "cortes": {"emision": CORTE_EMISION, "sello": CORTE_SELLO,
                   "convencion": CONVENCION},
        "cierre": cierre,
        "antecedente": {
            "n": len(ant), "fechas": int(ant["fecha"].nunique()) if len(ant) else 0,
            "n_sin_dedup": len(ant_sin_dedup),
            "retiradas_por_dedup": len(ant_sin_dedup) - len(ant),
            "empates": tasa_empates_antecedente(),
            "pares": pares_misma_sesion(cargar_antecedente(convencion=None)),
        },
        "poblacion": {
            "ritmo": ritmo_poblacion(),
            "ritmo_sin_dedup": ritmo_poblacion(dedup=False),
            "pares": pares_misma_sesion(cargar_poblacion()),
        },
    }


def main() -> None:
    r = resumen()
    print("=" * 72)
    print("LAS DOS VENTANAS DEL PRE-REGISTRO, ANCLADAS")
    print("=" * 72)
    c = r["cortes"]
    print(f"\ncorte de emisión .... {c['emision']}   (§A2: la población es lo "
          "posterior)")
    print(f"corte de sello ...... {c['sello']}   (cierre medido de la "
          "antecedente)")
    print(f"convención .......... {c['convencion']}")

    z = r["cierre"]
    print(f"\nCANDADO — filas emitidas hasta {c['emision']} verificadas "
          f"después de {c['sello']}: {z['tardias']}")
    print(f"          última verificación de la ventana: "
          f"{z['ultima_verificacion']}")
    if z["tardias"]:
        print("          *** LA VENTANA SE ABRIÓ: ver cierre_de_ventana() ***")

    a = r["antecedente"]
    print(f"\nVENTANA ANTECEDENTE (computar acá está permitido)")
    print(f"  filas, regla firmada + {c['convencion']} ... {a['n']}")
    print(f"  fechas de emisión ......................... {a['fechas']}")
    print(f"  filas sin la regla de deduplicación ....... {a['n_sin_dedup']}"
          f"  (la regla retira {a['retiradas_por_dedup']})")
    e = a["empates"]
    print(f"  empates (gap == 0) que {c['convencion']} retira ... "
          f"{e['empates']} de {e['n_sin_convencion']} ({e['tasa']:.2%})")
    p = a["pares"]
    print(f"  filas en pares (ticker, sesión objetivo) .. {p['filas_en_pares']}"
          f" en {p['grupos']} grupos, {len(p['sesiones'])} sesiones")

    q = r["poblacion"]
    rt, rs = q["ritmo"], q["ritmo_sin_dedup"]
    print(f"\nPOBLACIÓN (sólo conteos y fechas; sin columnas de resultado)")
    print(f"  filas, regla firmada ...................... {rt['filas']}")
    print(f"  filas sin la regla de deduplicación ....... {rs['filas']}")
    print(f"  fechas de emisión ......................... {rt['fechas']}")
    print(f"  primera / última .......................... {rt['primera']} / "
          f"{rt['ultima']}")
    print(f"  días hábiles desde el corte ............... {rt['dias_habiles']}")
    print(f"  filas por día hábil ....................... "
          f"{rt['filas_por_dia_habil']:.3f}   (sin dedup: "
          f"{rs['filas_por_dia_habil']:.3f})")
    pp = q["pares"]
    print(f"  filas en pares (ticker, sesión objetivo) .. {pp['filas_en_pares']}"
          f" en {pp['grupos']} grupos, {len(pp['sesiones'])} sesiones")
    print("\n  OJO: este conteo NO aplica la convención del empate, porque "
          "`gap_pct == 0`")
    print("  es una función de `gap_pct` y la población no se mira. Es un "
          "TECHO del n")
    print("  del plan, así que las fechas que salen de él son más TEMPRANAS "
          "que las")
    print(f"  reales; en la ventana antecedente la convención retira el "
          f"{e['tasa']:.2%}.")


if __name__ == "__main__":
    main()
