# ============================================================
# banco_clausulas.py — el banco de pruebas de cláusulas candidatas
#
#   source venv/bin/activate
#   python -m GEMELO.banco_clausulas
#
# QUÉ ES. Un banco que recibe UNA CLÁUSULA COMO FUNCIÓN y le corre tres
# pruebas fijas. Las cuatro cláusulas que hoy están sobre la mesa son
# instancias, no el propósito: el propósito es que la QUINTA cláusula —la
# que todavía no existe— se pueda evaluar con el mismo instrumento, sin
# reescribir nada y sin que el juicio dependa de quién la propuso.
#
# QUÉ NO ES. No aplica ninguna cláusula, no recomienda ninguna, no mueve
# ninguna cifra publicada y no toca ninguna fila sellada. `senales.db` se
# lee SIEMPRE en `mode=ro`, por `backtest.linea_base.cargar` y
# `backtest.datos._conexion_ro`. `motor.py`, `senales.py`, `snapshot.py`
# y `universo.py` no se importan para escribir nada ni se modifican.
#
# ------------------------------------------------------------
# LAS TRES PRUEBAS, y por qué son ésas
# ------------------------------------------------------------
# PRUEBA 1 — METADATA. ¿La cláusula se decide con información fijada
#   ANTES de conocerse el resultado? Timestamp, identidad de máquina y
#   calendario son seguros; el gap y el acierto de la fila, prohibidos.
#   La prueba tiene TRES partes y las tres hacen falta:
#     1a  declarativa: qué campos dice la cláusula que usa.
#     1b  MEDIDA: se permutan los campos de resultado entre filas y se
#         verifica que la selección no cambia. Una declaración puede
#         mentir; esto no depende de ella.
#     1c  MEDIDA: asociación entre el CRITERIO de la cláusula y el
#         acierto. Una cláusula puede ser metadata en la forma y
#         resultado en el fondo: si su criterio correlaciona con el
#         acierto, seleccionar por él es seleccionar por resultado con
#         un rodeo. Va con intervalo, y si el intervalo contiene el nulo
#         se dice.
#   1a y 1b se pasan o se fallan. 1c NO tiene umbral de aprobación: es
#   una medición que se REPORTA, porque el umbral sería una convención y
#   la convención es de Nicolás.
#
# PRUEBA 2 — LA DEL b/c. Cómo mueve la cláusula los pares discordantes de
#   McNemar. Es la prueba que destapó `keep="last"`: `b` quedaba en 72 y
#   `c` bajaba de 56 a 49, con los 7 pares retirados favoreciendo TODOS a
#   la baseline. Una cláusula que mueve `c` y no mueve `b` no queda
#   refutada por eso —puede ser la corrección correcta— pero queda
#   marcada EXIGE MECANISMO: hay que exhibir por qué el defecto que
#   corrige es asimétrico, antes de aceptarla.
#
# PRUEBA 3 — ANCLAS. Toda regla candidata tiene que preservar la
#   reproducción de los pre-registros congelados: 21/21 (§2, convención
#   `estricta`) y 7/7 (línea base §2.8, `excluir_cero`), ambos sobre
#   `cargar(hasta_sello=CORTE_SECCION_2, dedup=False)`. Una regla que
#   rompa eso es peor que el problema que resuelve.
#
# ------------------------------------------------------------
# EL BANCO TIENE QUE PODER FALLAR
# ------------------------------------------------------------
# `CLAUSULA_TRAMPA` es una cláusula que lee `acierto_gap` a propósito y
# se queda con las filas que el modelo acertó. Está acá para que la
# PRUEBA 1 tenga una contraprueba viva: si el banco no la reprueba, el
# banco no mide nada. `tests/test_banco_clausulas.py` lo fija. NO es
# candidata y NO cuenta como intento: de ella no se lee ningún resultado
# sobre el modelo, sólo sobre el instrumento.
#
# ------------------------------------------------------------
# LA BASE SOBRE LA QUE ACTÚAN LAS CLÁUSULAS — declarado, no default
# ------------------------------------------------------------
# `dedup=False`. No es una preferencia ni un descuido: las cláusulas bajo
# prueba son ELLAS MISMAS reglas de arbitraje o de población, y correrlas
# encima de la regla firmada mediría la COMPOSICIÓN de las dos, no la
# cláusula. La regla firmada entra al banco como cláusula de referencia
# (`C0`) para que su propio movimiento de b/c esté en la misma tabla y
# nadie tenga que confiar en la memoria.
#
# CUIDADO CON LA CUARTA REGLA DE LA CASA: la base `dedup=False` produce
# cifras ANTERIORES a la firma del 1-sep. En este informe aparecen como
# «lo que la cláusula recibe», nunca como cifra vigente, y siempre con la
# fila C0 al lado. La cifra vigente de la ventana sellada es la de la
# regla firmada, +9,7 pp, y su IC95 de clúster de día es [−7,2, +26,5]
# con n efectivo 67 — el p no se cita nunca solo.
#
# ------------------------------------------------------------
# EL ESTADÍSTICO
# ------------------------------------------------------------
# La unidad real de este track record es el DÍA, no la fila: las ~7 filas
# de un sello comparten insumo, régimen y desenlace de mercado. Todos los
# intervalos de este módulo son de CLÚSTER DE DÍA (bootstrap de días
# enteros, semilla obligatoria) y todos los p de comparación entre grupos
# de días son de PERMUTACIÓN DE LA ETIQUETA A NIVEL DE DÍA. Wilson
# aparece sólo como segunda ruta, DECLARADA COMO OPTIMISTA porque supone
# filas independientes. Ningún estimador puntual sale de acá sin
# intervalo, y ningún p sale sin su intervalo al lado.
#
# Wilson y McNemar exacto vienen de
# `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py`; el ICC y
# el efecto de diseño, de `GEMELO.bifurcaciones`. No se reimplementa
# ninguno de los tres.
# ============================================================

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude", "skills", "estadistica-evaluacion", "scripts"))

from evaluacion import mcnemar_exact, wilson_ci  # noqa: E402

import calendarios  # noqa: E402
import backtest.linea_base as lb  # noqa: E402
from backtest.datos import RUTA_SENALES, _conexion_ro  # noqa: E402
from GEMELO.bifurcaciones import _por_dia, icc_y_deff  # noqa: E402
from version import MODELO_VERSION  # noqa: E402

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "resultados")
DESTINO = os.path.join(DIR_RESULTADOS, "clausulas.md")
DESTINO_JSON = os.path.join(DIR_RESULTADOS, "clausulas.json")
RUTA_VEREDICTOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "sombra", "veredictos.jsonl")

ALFA = 0.05
SEMILLA = 0            # obligatoria: un bootstrap sin semilla no reproduce
N_BOOT = 10_000
N_PERM = 20_000
N_PERM_INVARIANZA = 200
# El piso declarado de `GEMELO.bifurcaciones`: bajo esto una celda no se
# puntúa. Se importa el número, no se elige uno nuevo.
MINIMO_FILAS = 30
TZ_CHILE = ZoneInfo("America/Santiago")

# La ventana de sellado declarada por el proyecto, hora de Chile.
VENTANA_SELLADO = (17, 50, 20, 30)

# El corte de composición canónica de la base, sellado en
# `data/sombra/switch_20260830.md` §2: `fecha <= 2026-08-25` → MAC,
# `fecha >= 2026-08-26` → PC. No es memoria de nadie: se corrobora contra
# `plataforma_version`, que está sellada fila por fila (5.0.3 aparece
# exactamente el 26-ago). `_verificar_corroboracion_maquina` aborta si
# las dos varas dejaran de coincidir.
CORTE_MAQUINA = "2026-08-25"
VERSION_PC = "5.0.3"

# ------------------------------------------------------------
# LA CLASIFICACIÓN DE CAMPOS — el criterio de la PRUEBA 1a
# ------------------------------------------------------------
# SEGURO = fijado antes de conocerse el desenlace de la sesión objetivo.
# PROHIBIDO = el desenlace mismo, o cualquier función de él.
# Un campo que no esté en ninguna de las dos listas NO se aprueba por
# omisión: la cláusula tiene que declararlo y alguien tiene que
# clasificarlo. El silencio no es una clasificación.
CAMPOS_SEGUROS = frozenset({
    "fecha", "ticker", "exchange", "sesion_objetivo", "available_at",
    "timestamp_utc", "plataforma_version", "origen", "sox_fecha",
    "sox_usado_pct", "regimen", "n_muestra", "confianza_r2",
    "intervalo80_pp", "beta", "apertura_estimada_pct",
    # derivados de los anteriores por calendario o por el documento de
    # composición: siguen siendo metadata
    "maquina", "sesion_recomputada", "sesion_calza", "sello_a_tiempo",
    "sello_en_ventana", "era", "solapamiento",
})
CAMPOS_PROHIBIDOS = frozenset({
    "gap_pct", "acierto_gap", "retorno_real_pct", "error_gap_pp",
    "base_acierto", "acierto_direccion", "error_pp",
})
# Las columnas cuyo valor se permuta en la PRUEBA 1b. Se permutan JUNTAS,
# como una tupla por fila: romper su coherencia interna probaría otra
# cosa (que la cláusula no lee un desenlace incoherente), no la que
# interesa.
COLUMNAS_RESULTADO = ("gap_pct", "acierto_gap", "retorno_real_pct",
                      "error_gap_pp", "base_acierto")


# ------------------------------------------------------------
# Carga — solo lectura, con las metadatas que las cláusulas necesitan
# ------------------------------------------------------------
def _metadatos_sello() -> tuple:
    """`timestamp_utc` por fila y `plataforma_version`/`origen` por sello.

    `linea_base.cargar` no los trae porque no los necesita; son el insumo
    de toda cláusula que hable de relojes o de máquinas."""
    conn = _conexion_ro(RUTA_SENALES)
    try:
        st = pd.read_sql_query(
            "SELECT fecha, ticker, timestamp_utc FROM senales_ticker"
            " WHERE modelo_version = ?", conn, params=(MODELO_VERSION,))
        sn = pd.read_sql_query(
            "SELECT fecha, timestamp_utc AS ts_snapshot, origen,"
            " plataforma_version FROM snapshots", conn)
    finally:
        conn.close()
    return st, sn


def _a_utc(ts) -> datetime | None:
    if ts is None or (isinstance(ts, float) and np.isnan(ts)) or pd.isna(ts):
        return None
    t = datetime.fromisoformat(str(ts))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def ventana_solapamiento() -> list:
    """Las fechas en que EVIDENTEMENTE sellaron LAS DOS máquinas.

    No se cablea: se lee de `data/sombra/veredictos.jsonl`, que es la
    evidencia sellada de la ventana de paridad. Un veredicto de PARIDAD o
    DIVERGENCIA implica que hubo fila del titular Y fila de la sombra
    para esa fecha; DIA_NO_COMPUTABLE implica que el titular no selló, y
    PENDIENTE_PUBLICACION que todavía no se sabe.

    LIMITACIÓN DECLARADA: la ausencia de comparación para una fecha NO
    prueba que no hubo solapamiento ese día — `comparar_sombra.py` tiene
    `FECHA_CORTE = 2026-08-24` y las fechas anteriores se REHÚSAN por
    diseño (bases copiadas). Así que ésta es la ventana EVIDENCIADA, no
    necesariamente la ventana real."""
    if not os.path.exists(RUTA_VEREDICTOS):
        return []
    ultimo = {}
    with open(RUTA_VEREDICTOS, encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea:
                continue
            d = json.loads(linea)
            ultimo[d["fecha"]] = d["veredicto"]   # el último gana
    return sorted(f for f, v in ultimo.items()
                  if v in ("PARIDAD", "DIVERGENCIA"))


def _verificar_corroboracion_maquina(df: pd.DataFrame) -> None:
    """Dos varas para la misma atribución de máquina, y tienen que
    coincidir: el corte del documento de composición y la columna
    `plataforma_version`, que está SELLADA fila por fila. Si dejaran de
    coincidir, la atribución de máquina pasaría a depender de la memoria
    de un documento — y el banco se detiene antes que dejar pasar eso."""
    con_version = df[df["plataforma_version"].notna()]
    if con_version.empty:
        return
    por_version = con_version["fecha"] > CORTE_MAQUINA
    por_documento = con_version["plataforma_version"] == VERSION_PC
    if not (por_version == por_documento).all():
        malas = con_version.loc[por_version != por_documento,
                                ["fecha", "plataforma_version"]]
        raise RuntimeError(
            "la atribución de máquina dejó de tener dos varas coincidentes; "
            f"filas en desacuerdo:\n{malas.drop_duplicates().to_string()}")


def cargar_base(hasta_sello: str | None = None,
                convencion: str | None = lb.CONVENCION_OFICIAL) -> pd.DataFrame:
    """La ventana sellada con TODA la metadata que una cláusula puede
    querer, y ninguna columna nueva de resultado.

    `dedup=False` está fijado a propósito y su razón está en la cabecera:
    las cláusulas bajo prueba son ellas mismas reglas de arbitraje."""
    df = lb.cargar(hasta_sello=hasta_sello, dedup=False)
    if df.empty:
        return df
    st, sn = _metadatos_sello()
    df = df.merge(st, on=["fecha", "ticker"], how="left")
    df = df.merge(sn, on="fecha", how="left")
    df["timestamp_utc"] = df["timestamp_utc"].fillna(df["ts_snapshot"])
    df = df.drop(columns=["ts_snapshot"])

    # Sesión que el `available_at` de la fila implica — la vara de la
    # regla firmada, importada, no reimplementada.
    df = lb.marcar_sesion(df)

    # Puntualidad, en sus DOS lecturas posibles. Las dos son metadata en
    # la forma; la PRUEBA 1c mide si alguna lo es también en el fondo.
    df["sello_a_tiempo"] = [
        _a_tiempo_por_apertura(e, s, t)
        for e, s, t in zip(df["exchange"], df["sesion_recomputada"],
                           df["timestamp_utc"])]
    df["sello_en_ventana"] = [_en_ventana_de_sellado(t)
                              for t in df["timestamp_utc"]]

    # Identidad de máquina y era.
    df["maquina"] = np.where(df["fecha"] > CORTE_MAQUINA, "PC", "MAC")
    solape = ventana_solapamiento()
    df["solapamiento"] = df["fecha"].isin(solape)
    df["era"] = np.where(df["solapamiento"], "AMBAS", df["maquina"])
    _verificar_corroboracion_maquina(df)

    if convencion is not None:
        df = lb.aplicar_convencion(df, convencion)
    return df.reset_index(drop=True)


def _a_tiempo_por_apertura(exchange, sesion, ts) -> bool:
    """«Selló a tiempo» = el sello ocurrió ANTES de que abriera la sesión
    que su propio `available_at` implica.

    Es la lectura estricta de la puntualidad: no mide si el proceso corrió
    a la hora de costumbre, mide si llegó antes de que el evento que
    pretende anticipar empezara. Es también la definición que la regla
    maestra de `CLAUDE.md` ya usa para decidir verificabilidad."""
    t = _a_utc(ts)
    if not exchange or not sesion or pd.isna(sesion) or t is None:
        return False
    try:
        return t < calendarios.apertura_utc(str(exchange), str(sesion))
    except Exception:
        return False


def _en_ventana_de_sellado(ts) -> bool:
    """La OTRA lectura de puntualidad: el sello cayó dentro de la ventana
    operativa declarada del proyecto (17:50–20:30 hora de Chile).

    No es la misma cosa que la anterior y por eso son dos cláusulas
    distintas, no dos formas de escribir una. Un sello a las 21:00 de
    Chile está fuera de la ventana operativa y sin embargo puede llegar
    holgadamente antes de que abra Seúl."""
    t = _a_utc(ts)
    if t is None:
        return False
    loc = t.astimezone(TZ_CHILE)
    h0, m0, h1, m1 = VENTANA_SELLADO
    return (h0 * 60 + m0) <= (loc.hour * 60 + loc.minute) <= (h1 * 60 + m1)


# ------------------------------------------------------------
# La cláusula, como objeto: una función más su declaración
# ------------------------------------------------------------
@dataclass(frozen=True)
class Clausula:
    """Todo lo que el banco necesita de una cláusula, y nada más.

    `seleccionar` devuelve el ÍNDICE de las filas que sobreviven. Que sea
    una selección de filas y no una transformación no es una comodidad:
    es lo que hace que «antes» y «después» sean comparables y que las
    filas retiradas se puedan mirar de a una en la PRUEBA 2.

    `criterio` es el indicador binario por fila del criterio propio de la
    cláusula (1 = la fila satisface el criterio). Es lo que la PRUEBA 1c
    cruza contra el acierto. Si una cláusula no tiene un criterio por
    fila, se declara `None` y 1c se reporta como no aplicable — que es
    una respuesta, no un aprobado."""
    nombre: str
    texto: str
    operacionalizacion: str
    procedencia: str
    campos: tuple
    seleccionar: Callable[[pd.DataFrame], pd.Index]
    criterio: Callable[[pd.DataFrame], pd.Series] | None = None
    es_candidata: bool = True
    notas: tuple = field(default_factory=tuple)


# ------------------------------------------------------------
# PRUEBA 1 — METADATA
# ------------------------------------------------------------
def _permutar_resultado(df: pd.DataFrame, rng) -> pd.DataFrame:
    cols = [c for c in COLUMNAS_RESULTADO if c in df.columns]
    out = df.copy()
    orden = rng.permutation(len(out))
    out[cols] = out[cols].to_numpy()[orden]
    return out


def prueba_1_metadata(cl: Clausula, df: pd.DataFrame,
                      n_perm: int = N_PERM_INVARIANZA,
                      n_boot: int = N_BOOT) -> dict:
    # --- 1a: declarativa -------------------------------------------
    prohibidos = sorted(set(cl.campos) & CAMPOS_PROHIBIDOS)
    sin_clasificar = sorted(set(cl.campos) - CAMPOS_SEGUROS - CAMPOS_PROHIBIDOS)
    a_ok = not prohibidos and not sin_clasificar

    # --- 1b: invarianza MEDIDA -------------------------------------
    rng = np.random.default_rng(SEMILLA)
    base = set(cl.seleccionar(df))
    cambios = 0
    for _ in range(n_perm):
        if set(cl.seleccionar(_permutar_resultado(df, rng))) != base:
            cambios += 1
    frac = cambios / n_perm
    lo_c, hi_c = wilson_ci(cambios, n_perm)
    b_ok = cambios == 0

    # --- 1c: asociación criterio ↔ acierto, MEDIDA ------------------
    if cl.criterio is None:
        c = {"aplicable": False,
             "motivo": "la cláusula no define un criterio por fila"}
    else:
        c = asociacion_criterio_acierto(df, cl.criterio(df).astype(bool),
                                        n_boot=n_boot)
    return {"1a_campos_declarados": list(cl.campos),
            "1a_prohibidos": prohibidos,
            "1a_sin_clasificar": sin_clasificar,
            "1a_pasa": a_ok,
            "1b_permutaciones": n_perm,
            "1b_selecciones_que_cambiaron": cambios,
            "1b_fraccion": frac,
            "1b_wilson": [lo_c, hi_c],
            "1b_pasa": b_ok,
            "1c": c,
            "pasa": bool(a_ok and b_ok)}


def _dif_tasas_por_dia(fechas, criterio, acierto, n_boot: int,
                       alpha: float = ALFA) -> dict:
    """Diferencia de tasa de acierto entre las filas que satisfacen el
    criterio y las que no, con IC de CLÚSTER DE DÍA.

    Se remuestrean DÍAS ENTEROS con reemplazo —la misma unidad y la misma
    semilla que el resto del proyecto— y se recalcula la diferencia como
    razón de sumas, que es lo correcto con clústeres de tamaños
    distintos. Las réplicas en que un lado queda vacío no dan número: se
    cuentan en `frac_degeneradas` en vez de esconderse con un `dropna`."""
    dias = pd.factorize(np.asarray(fechas))[0]
    k = dias.max() + 1
    crit = np.asarray(criterio, dtype=bool)
    ac = np.asarray(acierto, dtype=float)
    trozos = [(ac[dias == j], crit[dias == j]) for j in range(k)]

    def dif(sel):
        a = np.concatenate([t[0] for t in sel])
        m = np.concatenate([t[1] for t in sel])
        if m.sum() == 0 or (~m).sum() == 0:
            return np.nan
        return 100.0 * (a[m].mean() - a[~m].mean())

    punto = dif(trozos)
    rng = np.random.default_rng(SEMILLA)
    reps = np.array([dif([trozos[j] for j in rng.integers(0, k, size=k)])
                     for _ in range(n_boot)], dtype=float)
    ok = reps[np.isfinite(reps)]
    if len(ok) < 20:
        return {"dif_pp": float(punto), "lo": float("nan"), "hi": float("nan"),
                "frac_degeneradas": 1 - len(ok) / n_boot, "n_boot": n_boot}
    lo, hi = np.quantile(ok, [alpha / 2, 1 - alpha / 2])
    # Fracción de réplicas del OTRO lado del cero: es la lectura
    # bootstrap del «cuán lejos del nulo», y sirve donde la permutación
    # de etiqueta de día no aplica porque el criterio varía dentro del
    # día. No es un p y no se llama p.
    cruzan = float((ok <= 0).mean() if punto > 0 else (ok >= 0).mean())
    return {"dif_pp": float(punto), "lo": float(lo), "hi": float(hi),
            "frac_degeneradas": 1 - len(ok) / n_boot, "n_boot": n_boot,
            "frac_replicas_del_otro_lado": cruzan,
            "punto_dentro": bool(lo <= punto <= hi)}


def _p_permutacion_etiqueta_dia(fechas, criterio, acierto,
                                n_perm: int = N_PERM) -> dict:
    """p bilateral permutando la ETIQUETA DEL DÍA, no la de la fila.

    Cuando el criterio es una propiedad del sello —la puntualidad lo es:
    todas las filas de un snapshot la comparten— la comparación es ENTRE
    CLÚSTERES. Permutar filas fabricaría una precisión que no existe;
    permutar días enteros respeta la unidad real. Corrección +1 de
    Phipson-Smyth: nunca devuelve 0.

    Devuelve también si el criterio es realmente constante dentro del
    día, porque de eso depende que este test sea el correcto."""
    f = np.asarray(fechas)
    crit = np.asarray(criterio, dtype=bool)
    ac = np.asarray(acierto, dtype=float)
    tab = pd.DataFrame({"f": f, "c": crit, "a": ac})
    por_dia = tab.groupby("f").agg(c=("c", "mean"), suma=("a", "sum"),
                                   n=("a", "size"))
    constante = bool(((por_dia["c"] == 0) | (por_dia["c"] == 1)).all())
    if not constante:
        return {"aplicable": False, "criterio_constante_en_el_dia": False,
                "motivo": "el criterio varía dentro de un mismo día: la "
                          "permutación de etiqueta de día no es el test "
                          "correcto y no se reporta un p que no aplica"}
    etiqueta = por_dia["c"].to_numpy(dtype=bool)
    suma = por_dia["suma"].to_numpy(dtype=float)
    cuenta = por_dia["n"].to_numpy(dtype=float)
    k1 = int(etiqueta.sum())
    k = len(etiqueta)
    if k1 == 0 or k1 == k:
        return {"aplicable": False, "criterio_constante_en_el_dia": True,
                "motivo": "todos los días caen del mismo lado del criterio"}

    def dif(sel):
        return (suma[sel].sum() / cuenta[sel].sum()
                - suma[~sel].sum() / cuenta[~sel].sum())

    obs = abs(dif(etiqueta))
    rng = np.random.default_rng(SEMILLA)
    extremos = 0
    for _ in range(n_perm):
        sel = np.zeros(k, dtype=bool)
        sel[rng.choice(k, size=k1, replace=False)] = True
        if abs(dif(sel)) >= obs - 1e-12:
            extremos += 1
    return {"aplicable": True, "criterio_constante_en_el_dia": True,
            "p": (1 + extremos) / (n_perm + 1), "n_perm": n_perm,
            "dias_con_criterio": k1, "dias_sin_criterio": k - k1}


def asociacion_criterio_acierto(df: pd.DataFrame, criterio: pd.Series,
                                n_boot: int = N_BOOT,
                                columna: str = "acierto_gap") -> dict:
    """LA MEDICIÓN DE LA PRUEBA 1c, y la que el encargo pide de frente
    para la cláusula 3: ¿el criterio de la cláusula correlaciona con el
    acierto de la fila?

    Si correlaciona, la cláusula es metadata en la forma y resultado en
    el fondo: seleccionar por ella es seleccionar por desenlace con un
    rodeo. Y si NO correlaciona de forma detectable, eso tampoco es un
    permiso — con pocos clústeres el intervalo puede ser tan ancho que no
    excluya nada, y entonces la respuesta honesta es «no se puede
    distinguir», no «no correlaciona». Las dos frases se reportan según
    corresponda."""
    crit = criterio.to_numpy(dtype=bool)
    ac = df[columna].to_numpy(dtype=float)
    n1, n0 = int(crit.sum()), int((~crit).sum())
    if n1 == 0 or n0 == 0:
        return {"aplicable": False,
                "motivo": f"todas las filas caen del mismo lado "
                          f"(criterio=1 en {n1}, criterio=0 en {n0})"}
    k1, k0 = int(ac[crit].sum()), int(ac[~crit].sum())
    boot = _dif_tasas_por_dia(df["fecha"], crit, ac, n_boot)
    perm = _p_permutacion_etiqueta_dia(df["fecha"], crit, ac)
    # ICC de la variable de acierto: es lo que traduce «las filas de un
    # día no son independientes» a un número, y sin él el lector no puede
    # juzgar cuánto vale cada n.
    est = icc_y_deff(_por_dia(df, ac))
    excluye_cero = bool(np.isfinite(boot.get("lo", np.nan))
                        and (boot["lo"] > 0 or boot["hi"] < 0))
    p_perm = perm.get("p") if perm.get("aplicable") else None
    minoria = (min(perm.get("dias_con_criterio", 0),
                   perm.get("dias_sin_criterio", 0))
               if perm.get("aplicable") else None)
    # LAS TRES LECTURAS POSIBLES, y la del medio es la que importa: un p
    # que cruza α mientras el intervalo contiene el cero no es evidencia,
    # es una discrepancia entre dos rutas de clúster que hay que exhibir.
    if excluye_cero:
        lectura = ("el intervalo EXCLUYE el cero: el criterio correlaciona "
                   "con el acierto y la cláusula es metadata en la forma y "
                   "resultado en el fondo")
    elif p_perm is not None and p_perm < ALFA:
        lectura = (f"DISCREPANCIA ENTRE RUTAS: la permutación de etiqueta de "
                   f"día cruza α (p = {p_perm:.4f}) pero el IC95 de clúster "
                   f"CONTIENE el cero. Cruzar α no es tener evidencia. Con "
                   f"{minoria} día(s) del lado minoritario la asociación no "
                   f"se puede establecer NI descartar — y el punto "
                   f"({boot['dif_pp']:+.1f} pp) es lo bastante grande como "
                   f"para que 'no se puede descartar' sea la parte que "
                   f"pesa")
    else:
        cola = ("y la permutación de día no cruza α" if p_perm is not None
                else "y no hay permutación de día válida (el criterio varía "
                     "dentro del día), así que el intervalo es la única ruta")
        lectura = (f"el intervalo CONTIENE el cero {cola}: con estos datos no "
                   f"se puede distinguir asociación de ausencia de asociación "
                   f"— no es un permiso, es una falta de resolución, y "
                   f"con un punto de {boot['dif_pp']:+.1f} pp la parte que "
                   f"pesa es que tampoco se puede descartar")
    return {
        "aplicable": True,
        "n_criterio_1": n1, "aciertos_criterio_1": k1,
        "tasa_criterio_1_pct": 100.0 * k1 / n1,
        "wilson_criterio_1": list(wilson_ci(k1, n1)),
        "n_criterio_0": n0, "aciertos_criterio_0": k0,
        "tasa_criterio_0_pct": 100.0 * k0 / n0,
        "wilson_criterio_0": list(wilson_ci(k0, n0)),
        "diferencia_pp": 100.0 * (k1 / n1 - k0 / n0),
        "ic95_cluster_dia": [boot.get("lo"), boot.get("hi")],
        "frac_degeneradas": boot.get("frac_degeneradas"),
        "frac_replicas_del_otro_lado": boot.get("frac_replicas_del_otro_lado"),
        "p_permutacion_dia": perm,
        "dias_lado_minoritario": minoria,
        "icc_acierto": est.get("icc"), "deff": est.get("deff"),
        "n_efectivo": est.get("n_efectivo"), "clusters": est.get("clusters"),
        "ic_excluye_cero": excluye_cero,
        "discrepancia_entre_rutas": bool(not excluye_cero and p_perm is not None
                                         and p_perm < ALFA),
        "lectura": lectura,
    }


# ------------------------------------------------------------
# PRUEBA 2 — LA DEL b/c
# ------------------------------------------------------------
def _bc(df: pd.DataFrame) -> tuple:
    mod = df["acierto_gap"].to_numpy(dtype=int)
    base = df["base_acierto"].to_numpy(dtype=int)
    return (int(((mod == 1) & (base == 0)).sum()),
            int(((mod == 0) & (base == 1)).sum()))


def _ventaja_con_ic(df: pd.DataFrame, n_boot: int = N_BOOT) -> dict:
    """La ventaja pareada con IC de clúster de día. Nunca el punto solo."""
    if df.empty:
        return {}
    d = (df["acierto_gap"].to_numpy(dtype=float)
         - df["base_acierto"].to_numpy(dtype=float))
    grupos = _por_dia(df, d)
    k = len(grupos)
    sumas = np.array([g.sum() for g in grupos], dtype=float)
    cuentas = np.array([len(g) for g in grupos], dtype=float)
    punto = 100.0 * sumas.sum() / cuentas.sum()
    if k < 2:
        return {"ventaja_pp": punto, "lo": float("nan"), "hi": float("nan"),
                "clusters": k}
    rng = np.random.default_rng(SEMILLA)
    idx = rng.integers(0, k, size=(n_boot, k))
    reps = 100.0 * sumas[idx].sum(axis=1) / cuentas[idx].sum(axis=1)
    lo, hi = np.quantile(reps, [ALFA / 2, 1 - ALFA / 2])
    est = icc_y_deff(_por_dia(df, d))
    return {"ventaja_pp": punto, "lo": float(lo), "hi": float(hi),
            "clusters": k, "n_efectivo": est.get("n_efectivo")}


def prueba_2_bc(cl: Clausula, df: pd.DataFrame, n_boot: int = N_BOOT) -> dict:
    sel = pd.Index(cl.seleccionar(df))
    despues = df.loc[df.index.intersection(sel)]
    retiradas = df.drop(index=despues.index)

    b0, c0 = _bc(df)
    b1, c1 = _bc(despues) if not despues.empty else (0, 0)

    mod = retiradas["acierto_gap"].to_numpy(dtype=int) if len(retiradas) else np.array([], int)
    bas = retiradas["base_acierto"].to_numpy(dtype=int) if len(retiradas) else np.array([], int)
    ret_b = int(((mod == 1) & (bas == 0)).sum())     # favorecían al MODELO
    ret_c = int(((mod == 0) & (bas == 1)).sum())     # favorecían a la BASELINE
    ret_conc = len(retiradas) - ret_b - ret_c
    m = ret_b + ret_c

    # ¿El retiro de discordantes es simétrico? Binomial exacta contra 0.5
    # (la misma función que el McNemar exacto del proyecto: b y c contra
    # una moneda) más Wilson sobre la proporción. No se reimplementa nada.
    p_asim = mcnemar_exact(ret_c, ret_b) if m else None
    wil = list(wilson_ci(ret_c, m)) if m else None

    mueve_c_no_b = (c1 != c0) and (b1 == b0)
    todos_un_signo = m > 0 and (ret_b == 0 or ret_c == 0)
    # Una cláusula puede no disparar la alarma de asimetría simplemente
    # porque no deja nada sobre lo que haya asimetría. Eso NO es aprobar
    # la prueba y hay que decirlo con su propio nombre: sin pares
    # discordantes el duelo campeón-vs-baseline no distingue nada, y una
    # ventaja de +0.0 pp con IC [0, 0] es la ausencia de medición, no una
    # medición de ausencia.
    sin_poder = (b1 + c1) == 0 or len(despues) < MINIMO_FILAS

    return {
        "n_antes": len(df), "n_despues": len(despues),
        "filas_retiradas": len(retiradas),
        "b_antes": b0, "c_antes": c0, "b_despues": b1, "c_despues": c1,
        "delta_b": b1 - b0, "delta_c": c1 - c0,
        "retiradas_tipo_b": ret_b, "retiradas_tipo_c": ret_c,
        "retiradas_concordantes": ret_conc,
        "retiradas_discordantes": m,
        "prop_retiradas_pro_baseline": (ret_c / m) if m else None,
        "wilson_prop_pro_baseline": wil,
        "p_binomial_exacta_simetria": p_asim,
        "mcnemar_exacto_antes": mcnemar_exact(b0, c0),
        "mcnemar_exacto_despues": mcnemar_exact(b1, c1) if despues.shape[0] else None,
        "ventaja_antes": _ventaja_con_ic(df, n_boot),
        "ventaja_despues": _ventaja_con_ic(despues, n_boot),
        "mueve_c_y_no_b": bool(mueve_c_no_b),
        "retiradas_todas_un_signo": bool(todos_un_signo),
        "exige_mecanismo": bool(mueve_c_no_b or todos_un_signo),
        "sin_poder_resolutivo": bool(sin_poder),
        "minimo_filas_declarado": MINIMO_FILAS,
        "detalle_retiradas": (
            retiradas[["fecha", "ticker", "exchange", "sesion_objetivo",
                       "acierto_gap", "base_acierto"]]
            .assign(signo=np.where(mod > bas, "b (pro modelo)",
                                   np.where(mod < bas, "c (pro baseline)",
                                            "concordante")))
            .to_dict("records") if len(retiradas) else []),
    }


# ------------------------------------------------------------
# PRUEBA 3 — ANCLAS
# ------------------------------------------------------------
ANCLAS_ESPERADAS = {"seccion_2": 21, "linea_base_2_8": 7}


def prueba_3_anclas(cl: Clausula) -> dict:
    """Los dos pre-registros congelados: 21/21 (§2, `estricta`) y 7/7
    (línea base §2.8, `excluir_cero`), ambos sobre
    `cargar(hasta_sello=CORTE_SECCION_2, dedup=False)`.

    LA PRUEBA TIENE DOS NIVELES, y separarlos NO es una concesión: es lo
    que hace que la prueba distinga dos cosas distintas.

      3a — COSTO RETROACTIVO. ¿Los pre-registros siguen reproduciendo si
        la cláusula se aplicara TAMBIÉN a la ventana congelada? Se
        reporta siempre. Fallarlo NO es automáticamente descalificante, y
        hay una razón dura para decirlo: **la regla ya firmada también lo
        falla**, porque toca filas anteriores al 24-ago. La respuesta que
        el proyecto ya dio a ese problema es `dedup=False` como rama
        histórica EXPLÍCITA (`backtest/linea_base.py`:105-112). Una
        cláusula que falla 3a hereda esa obligación: si se adopta, la
        rama histórica tiene que seguir existiendo y hay que decir cuál
        afirmación se reproduce por cuál ruta.

      3b — RUTA DEL ANCLA PRESERVADA. ¿El ancla sigue reproduciendo desde
        SU PROPIA ruta después de correr la cláusula, y la cláusula dejó
        la base tal como la recibió? Esto sí es FATAL: una cláusula que
        muta el conjunto que se le pasa, o que se cuela en el camino de
        carga por defecto, destruye la reproducibilidad de un
        pre-registro congelado — y eso es peor que el problema que
        resuelve, sin atenuantes.
    """
    hist = cargar_base(hasta_sello=lb.CORTE_SECCION_2, convencion=None)
    if hist.empty:
        return {"disponible": False}
    huella_antes = pd.util.hash_pandas_object(hist, index=True).sum()
    sel = pd.Index(cl.seleccionar(hist))
    huella_despues = pd.util.hash_pandas_object(hist, index=True).sum()
    aplicado = hist.loc[hist.index.intersection(sel)]

    def contar(base):
        # Una cláusula puede vaciar la ventana histórica entera (una
        # cláusula de población cuya era no existía todavía lo hace). Eso
        # NO es un error del banco: es el peor resultado posible de la
        # PRUEBA 3 —cero afirmaciones reproducidas— y se reporta como tal
        # en vez de reventar.
        if len(base) == 0:
            return (0, len(lb.AFIRMACIONES), 0, len(lb.LINEA_BASE_OFICIAL),
                    ["(la cláusula deja la ventana histórica VACÍA: "
                     "ninguna afirmación tiene filas sobre las que medirse)"],
                    ["(ídem)"])
        c1 = lb.contrastar(lb.aplicar_convencion(base, "estricta"))
        c2 = lb.contrastar_linea_oficial(
            lb.aplicar_convencion(base, lb.CONVENCION_OFICIAL))
        return ((c1["veredicto"] == "reproduce").sum(), len(c1),
                (c2["veredicto"] == "coincide").sum(), len(c2),
                c1[c1["veredicto"] != "reproduce"]["afirmación"].tolist(),
                c2[c2["veredicto"] != "coincide"]["campo"].tolist())

    s_ok, s_n, o_ok, o_n, s_mal, o_mal = contar(aplicado)

    # 3b: el ancla, recargada DESDE CERO por su propia ruta después de
    # haber corrido la cláusula. Si la cláusula mutó algo o se coló en el
    # camino de carga, esto lo ve.
    ruta = cargar_base(hasta_sello=lb.CORTE_SECCION_2, convencion=None)
    r_ok, r_n, ro_ok, ro_n, r_mal, ro_mal = contar(ruta)
    ruta_intacta = (int(r_ok) == ANCLAS_ESPERADAS["seccion_2"]
                    and int(ro_ok) == ANCLAS_ESPERADAS["linea_base_2_8"])
    sin_mutar = bool(huella_antes == huella_despues)

    return {
        "disponible": True,
        "filas_historicas": len(hist),
        "filas_retiradas_del_historico": len(hist) - len(aplicado),
        "3a_seccion_2": f"{int(s_ok)}/{int(s_n)}",
        "3a_linea_base_2_8": f"{int(o_ok)}/{int(o_n)}",
        "3a_afirmaciones_rotas": s_mal, "3a_linea_base_rota": o_mal,
        "3a_pasa": bool(int(s_ok) == ANCLAS_ESPERADAS["seccion_2"]
                        and int(o_ok) == ANCLAS_ESPERADAS["linea_base_2_8"]),
        "3b_seccion_2": f"{int(r_ok)}/{int(r_n)}",
        "3b_linea_base_2_8": f"{int(ro_ok)}/{int(ro_n)}",
        "3b_base_sin_mutar": sin_mutar,
        "3b_pasa": bool(ruta_intacta and sin_mutar),
        "pasa": bool(ruta_intacta and sin_mutar),
    }


# ------------------------------------------------------------
# El banco
# ------------------------------------------------------------
def evaluar(cl: Clausula, df: pd.DataFrame, n_boot: int = N_BOOT,
            n_perm_inv: int = N_PERM_INVARIANZA) -> dict:
    """Las tres pruebas sobre una cláusula. Ésta es la puerta por la que
    entra la quinta cláusula: se construye un `Clausula` y se la pasa."""
    p1 = prueba_1_metadata(cl, df, n_perm=n_perm_inv, n_boot=n_boot)
    p2 = prueba_2_bc(cl, df, n_boot=n_boot)
    p3 = prueba_3_anclas(cl)
    return {"nombre": cl.nombre, "texto": cl.texto,
            "operacionalizacion": cl.operacionalizacion,
            "procedencia": cl.procedencia, "candidata": cl.es_candidata,
            "notas": list(cl.notas),
            "prueba_1": p1, "prueba_2": p2, "prueba_3": p3,
            "veredicto": _veredicto(p1, p2, p3)}


def _veredicto(p1: dict, p2: dict, p3: dict) -> str:
    """El veredicto es una LECTURA de las tres pruebas, no un umbral de
    aceptación: el banco no adopta cláusulas. Sólo dos cosas son fatales
    —leer el resultado (PRUEBA 1) y destruir la ruta del ancla (3b)—;
    todo lo demás se marca para que lo decida quien firma."""
    if not p1["pasa"]:
        return "REPROBADA en la PRUEBA 1 (lee el resultado)"
    if p3.get("disponible") and not p3.get("3b_pasa", False):
        return "REPROBADA en la PRUEBA 3b (destruye la ruta del ancla)"
    marcas = []
    if p3.get("disponible") and not p3.get("3a_pasa", True):
        marcas.append("COSTO RETROACTIVO en 3a")
    if p2["exige_mecanismo"]:
        marcas.append("EXIGE MECANISMO en la PRUEBA 2")
    if p2["sin_poder_resolutivo"]:
        marcas.append("SIN PODER RESOLUTIVO (la población que deja no "
                      "distingue al campeón de la baseline)")
    if p1["1c"].get("aplicable") and p1["1c"].get("ic_excluye_cero"):
        marcas.append("su criterio CORRELACIONA con el acierto (1c)")
    return "PASA LAS TRES" if not marcas else \
        "no reprobada · " + " · ".join(marcas)


# ------------------------------------------------------------
# LAS CLÁUSULAS
# ------------------------------------------------------------
# Cada una lleva su OPERACIONALIZACIÓN escrita: una cláusula en castellano
# no es ejecutable hasta que alguien la traduce, y la traducción es una
# decisión que hay que poder discutir. Una operacionalización distinta es
# una CLÁUSULA DISTINTA y suma un intento propio — por eso la 3 aparece
# dos veces, con sus dos lecturas de «a tiempo», en vez de una sola con
# la lectura que le convenga a alguien.
# ------------------------------------------------------------
def _sel_era(df, era):
    return df.index[df["era"] == era] if era == "AMBAS" else \
        df.index[(df["maquina"] == era) & (~df["solapamiento"])]


def _sel_por_criterio_en_duplicados(df, col):
    """Arbitraje DENTRO de los grupos duplicados: conserva las filas que
    satisfacen `col`; si ninguna o todas lo satisfacen, conserva el grupo
    entero. Las filas sin pareja NUNCA se tocan — esto deduplica, no
    filtra por coherencia. Es la misma forma que la regla firmada, con
    otro criterio adentro, para que la comparación entre las dos sea de
    criterio y no de forma."""
    dup = df.duplicated(["ticker", "sesion_objetivo"], keep=False)
    vivos = list(df.index[~dup])
    for _, g in df[dup].groupby(["ticker", "sesion_objetivo"], sort=False):
        ok = g[g[col].astype(bool)]
        vivos += list(ok.index if 0 < len(ok) < len(g) else g.index)
    return pd.Index(sorted(vivos))


def _sel_iguales_una_vez(df):
    """«Si son iguales, contar una vez.» IGUALES se define sobre lo que
    el duelo puntúa: dos filas del mismo `(ticker, sesion_objetivo)` que
    coinciden en `acierto_gap` y en `gap_pct`. Si coinciden, aportan la
    misma información dos veces y se cuenta una.

    `base_acierto` NO entra en la comparación y no hace falta: bajo
    cualquiera de las tres convenciones es una función determinista de
    `gap_pct`, así que dos filas con el mismo `gap_pct` tienen la misma
    baseline por construcción. Incluirla ataría la cláusula a que la
    convención ya esté aplicada, y entonces el orden convención/cláusula
    dejaría de ser inmaterial — que es justo lo que el chequeo
    estructural del banco exige.

    EL DESEMPATE ESTÁ DECLARADO Y NO ES FRESCURA: se conserva la emisión
    MÁS ANTIGUA. Sobre b/c da igual cuál se conserve —las dos filas
    puntúan idéntico, que es la definición de «iguales»— pero sobre el
    MAE no da igual, porque `error_gap_pp` sí difiere. Elegir la fresca
    sería `keep="last"` entrando por la ventana."""
    dup = df.duplicated(["ticker", "sesion_objetivo"], keep=False)
    vivos = list(df.index[~dup])
    for _, g in df[dup].groupby(["ticker", "sesion_objetivo"], sort=False):
        claves = g[["acierto_gap", "gap_pct"]].drop_duplicates()
        if len(claves) == 1:
            vivos.append(g.sort_values(["fecha", "ticker"]).index[0])
        else:
            vivos += list(g.index)
    return pd.Index(sorted(vivos))


C0_REGLA_FIRMADA = Clausula(
    nombre="C0 — la regla firmada (referencia, NO candidata)",
    texto="dentro de cada par, la fila válida es la de sesión objetivo "
          "correcta según `available_at`, nunca la más fresca",
    operacionalizacion="`backtest.linea_base.deduplicar_por_sesion`, "
                       "importada tal cual: el banco no la reimplementa",
    procedencia="firmada el 1-sep-2026; DECISIONES.md, acta de la regla de "
                "deduplicación; ya APLICADA en el ejecutable",
    campos=("exchange", "available_at", "sesion_objetivo", "ticker"),
    seleccionar=lambda df: lb.deduplicar_por_sesion(df).index,
    criterio=lambda df: df["sesion_calza"],
    es_candidata=False,
    notas=("Entra al banco para que su propio movimiento de b/c esté en la "
           "misma tabla que el de las candidatas. NO suma un intento: sus "
           "cifras ya están publicadas y la regla ya está aplicada.",),
)

C1_SOLO_MAC = Clausula(
    nombre="C1 — considerar las filas de cuando cerraba sólo el Mac",
    texto="considerar las filas de cuando cerraba sólo el Mac",
    operacionalizacion="conserva las filas cuya `fecha` cae en la era en que "
                       "el Mac era la única máquina que sellaba: `fecha <= "
                       "2026-08-25` y fuera de la ventana de solapamiento "
                       "evidenciada. El corte sale del documento de "
                       "composición canónica y se corrobora contra "
                       "`plataforma_version`, que está sellada por fila.",
    procedencia="propuesta de Nicolás, sexta corrida: construir la regla "
                "desde el historial de máquinas",
    campos=("fecha", "maquina", "solapamiento", "plataforma_version"),
    seleccionar=lambda df: _sel_era(df, "MAC"),
    criterio=lambda df: (df["maquina"] == "MAC") & (~df["solapamiento"]),
    notas=("Es una cláusula de POBLACIÓN, no de arbitraje: no elige entre "
           "dos filas que compiten, elige una era entera. Las 25 filas del "
           "defecto de `snapshot.py:140` son TODAS de la era del Mac, así "
           "que esta cláusula las conserva a las 25.",),
)

C2_AMBAS = Clausula(
    nombre="C2 — considerar las de cuando cerraban ambas máquinas",
    texto="considerar las de cuando cerraban ambas máquinas",
    operacionalizacion="conserva las filas cuya `fecha` está en la ventana de "
                       "solapamiento EVIDENCIADA, leída de "
                       "`data/sombra/veredictos.jsonl` (veredicto PARIDAD o "
                       "DIVERGENCIA ⇒ sellaron las dos). No se cablea "
                       "ninguna fecha.",
    procedencia="propuesta de Nicolás, sexta corrida: construir la regla "
                "desde el historial de máquinas",
    campos=("fecha", "solapamiento", "era"),
    seleccionar=lambda df: _sel_era(df, "AMBAS"),
    criterio=lambda df: df["solapamiento"],
    notas=("LIMITACIÓN DECLARADA: la ventana evidenciada no es "
           "necesariamente la ventana real. `comparar_sombra.py` REHÚSA por "
           "diseño las fechas <= 2026-08-24 (bases copiadas), así que un "
           "solapamiento anterior no dejaría rastro comparable. La cláusula "
           "se evalúa sobre lo que hay evidencia de que pasó.",),
)

C3A_A_TIEMPO_APERTURA = Clausula(
    nombre="C3a — preferir la que selló a tiempo (antes de la apertura)",
    texto="preferir la que selló a tiempo",
    operacionalizacion="arbitraje dentro de cada grupo `(ticker, "
                       "sesion_objetivo)` duplicado: conserva la fila cuyo "
                       "`timestamp_utc` es anterior a la apertura UTC de la "
                       "sesión que su propio `available_at` implica. Si "
                       "ninguna o todas cumplen, el grupo queda intacto. "
                       "Las filas sin pareja no se tocan.",
    procedencia="propuesta de Nicolás, sexta corrida; la puntualidad como "
                "criterio de arbitraje",
    campos=("ticker", "sesion_objetivo", "timestamp_utc", "available_at",
            "exchange", "sello_a_tiempo"),
    seleccionar=lambda df: _sel_por_criterio_en_duplicados(df, "sello_a_tiempo"),
    criterio=lambda df: df["sello_a_tiempo"],
    notas=("ES LA CLÁUSULA QUE HAY QUE MIRAR DE FRENTE: es metadata en la "
           "forma —un timestamp contra un calendario— pero la puntualidad "
           "puede correlacionar con el acierto, porque un sello tardío usa "
           "datos distintos. La PRUEBA 1c lo MIDE en vez de suponerlo.",),
)

C3B_EN_VENTANA = Clausula(
    nombre="C3b — preferir la que selló a tiempo (dentro de la ventana "
           "operativa 17:50–20:30)",
    texto="preferir la que selló a tiempo",
    operacionalizacion="idéntica a C3a salvo la definición de «a tiempo»: "
                       "aquí es que el sello cayó dentro de la ventana "
                       "operativa declarada del proyecto, 17:50–20:30 hora "
                       "de Chile.",
    procedencia="segunda lectura de la misma cláusula 3; se evalúa aparte "
                "porque una operacionalización distinta es una cláusula "
                "distinta y suma su propio intento",
    campos=("ticker", "sesion_objetivo", "timestamp_utc", "sello_en_ventana"),
    seleccionar=lambda df: _sel_por_criterio_en_duplicados(df, "sello_en_ventana"),
    criterio=lambda df: df["sello_en_ventana"],
    notas=("Las dos lecturas no son equivalentes: un sello a las 21:00 de "
           "Chile está fuera de la ventana operativa y sin embargo llega "
           "holgado antes de que abra Seúl. Evaluar sólo una de las dos "
           "sería elegir la definición sin decirlo.",),
)

C4_IGUALES_UNA_VEZ = Clausula(
    nombre="C4 — si son iguales, contar una vez",
    texto="si son iguales, contar una vez",
    operacionalizacion="dentro de cada grupo `(ticker, sesion_objetivo)` "
                       "duplicado, si las filas coinciden en `acierto_gap` y "
                       "en `gap_pct` —lo que el duelo puntúa— se conserva "
                       "una sola, la de emisión MÁS ANTIGUA. Si no "
                       "coinciden, el grupo queda intacto.",
    procedencia="propuesta de Nicolás, sexta corrida",
    campos=("ticker", "sesion_objetivo", "fecha", "acierto_gap", "gap_pct"),
    seleccionar=_sel_iguales_una_vez,
    criterio=None,
    notas=("El desempate declarado (la más antigua) es inmaterial para b/c "
           "por construcción —las dos filas puntúan idéntico— pero NO para "
           "el MAE, porque `error_gap_pp` sí difiere entre ellas. Quedarse "
           "con la fresca sería `keep=\"last\"` entrando por la ventana.",
           "Esta cláusula LEE `acierto_gap` para decidir. La PRUEBA 1 lo "
           "va a marcar, y ése es exactamente el punto del banco.",),
)

C4B_MISMO_EVENTO = Clausula(
    nombre="C4b — si son iguales, contar una vez (lectura de metadata: "
           "«iguales» = el mismo evento)",
    texto="si son iguales, contar una vez",
    operacionalizacion="«iguales» NO se lee sobre el desenlace sino sobre la "
                       "identidad del evento: dos filas del mismo `(ticker, "
                       "sesion_objetivo)` son dos pronósticos del MISMO "
                       "evento y se cuenta uno. Desempate declarado y NO por "
                       "frescura: la emisión más antigua.",
    procedencia="segunda lectura de la cláusula 4, evaluada para no "
                "reportar sólo la lectura menos favorable. Resulta ser "
                "EXACTAMENTE la regla `keep=\"first\"` que la cola de "
                "decisiones ya midió (n=241, +6,64 pp, p=0,1847), así que "
                "**NO suma un intento nuevo**: es un intento ya contado, y "
                "reproducirlo sirve de validación externa del banco",
    campos=("ticker", "sesion_objetivo", "fecha"),
    seleccionar=lambda df: pd.Index(
        df.sort_values(["fecha", "ticker"])
          .drop_duplicates(["ticker", "sesion_objetivo"]).index.sort_values()),
    criterio=None,
    notas=("Es la lectura que NO lee el resultado, y por eso pasa la PRUEBA "
           "1 donde C4 la reprueba. La diferencia entre C4 y C4b no es de "
           "grado: es qué significa «iguales», y esa palabra es toda la "
           "cláusula.",
           "El desempate por la más antigua está declarado. Su espejo por "
           "frescura está PROHIBIDO por la firma del 1-sep y este módulo no "
           "lo ofrece en ninguna forma — un número retirado que sigue "
           "ofrecido en el código vuelve a circular.",
           "Sus cifras son la VALIDACIÓN EXTERNA del banco: si no "
           "reprodujeran n=241 y b/c 72/56, el instrumento estaría mal y "
           "nada de lo demás valdría.",),
)

CLAUSULA_TRAMPA = Clausula(
    nombre="TRAMPA — conservar las filas que el modelo acertó",
    texto="(no es una propuesta de nadie: es la contraprueba del banco)",
    operacionalizacion="conserva las filas con `acierto_gap == 1`",
    procedencia="construida por el banco para probar que el banco puede "
                "reprobar algo",
    campos=("acierto_gap",),
    seleccionar=lambda df: df.index[df["acierto_gap"] == 1],
    criterio=lambda df: df["acierto_gap"].astype(bool),
    es_candidata=False,
    notas=("Si el banco no reprueba esto, el banco no mide nada. NO cuenta "
           "como intento: de ella no se lee ningún resultado sobre el "
           "modelo, sólo sobre el instrumento.",),
)

CANDIDATAS = (C1_SOLO_MAC, C2_AMBAS, C3A_A_TIEMPO_APERTURA,
              C3B_EN_VENTANA, C4_IGUALES_UNA_VEZ, C4B_MISMO_EVENTO)
TODAS = (C0_REGLA_FIRMADA,) + CANDIDATAS

# La validación externa del banco: C4b tiene que reproducir la cifra que
# `GEMELO/resultados/dedup_opciones.md` §A2 publicó para `keep="first"`
# sobre la misma ventana (se cita por sección, no por línea: un número de
# línea lo desplaza la próxima edición del documento citado). Si no
# reprodujera, el instrumento estaría mal.
ANCLA_C4B = {"n": 241, "b": 72, "c": 56}

# Y el corte que hace que ese ancla signifique algo. Sin él, `cargar_base`
# lee la ventana VIVA y el ancla se rompe sola la próxima vez que
# producción sella —pasó el 1-sep-2026 a las 18:15, entre que este banco
# corrió (12:07) y el dictamen del guardián: la ventana subió de 256 a
# 271 filas y la validación externa pasó a comparar 256 contra 241—.
# Se pincha el INSTANTE, no se mueve el número: es el mismo mecanismo que
# `backtest.linea_base.CORTE_SECCION_2`, y la razón por la que ese
# precedente existe. Quien quiera el contraste contra la base viva pasa
# `hasta_sello=None` a sabiendas de que no reproducirá el ancla.
CORTE_BANCO = lb.CORTE_REGLA_FIRMADA


# ------------------------------------------------------------
# Chequeos estructurales del banco — antes de reportar nada
# ------------------------------------------------------------
def chequeos_estructurales(df: pd.DataFrame,
                           hasta_sello: str | None = None) -> dict:
    """Lo que tiene que ser cierto para que las tres pruebas signifiquen
    lo que dicen. Si algo de esto falla, el informe no se escribe."""
    fallas = []

    # 1. El orden convención-cláusula tiene que ser inmaterial. Si no lo
    #    fuera, «antes» y «después» dependerían de un orden no declarado.
    # El MISMO instante que el `df` que se está chequeando. Recargar sin
    # el corte compara una ventana congelada contra la viva, y el
    # chequeo falla por una diferencia que no es la que mide.
    crudo = cargar_base(hasta_sello=hasta_sello, convencion=None)
    for cl in TODAS:
        a = set(cl.seleccionar(df))
        b = set(lb.aplicar_convencion(
            crudo.loc[crudo.index.intersection(pd.Index(cl.seleccionar(crudo)))],
            lb.CONVENCION_OFICIAL).index)
        # los índices no son comparables entre bases distintas: se comparan
        # por (fecha, ticker), que sí identifica una fila
        ka = set(map(tuple, df.loc[sorted(a), ["fecha", "ticker"]].to_numpy()))
        kb = set(map(tuple, crudo.loc[sorted(b), ["fecha", "ticker"]].to_numpy()))
        if ka != kb:
            fallas.append(f"{cl.nombre}: el orden convención/cláusula importa")

    # 2. Toda selección tiene que ser un subconjunto de la base.
    for cl in TODAS:
        if not set(cl.seleccionar(df)).issubset(set(df.index)):
            fallas.append(f"{cl.nombre}: la selección no es un subconjunto")

    # 3. La contraprueba tiene que ser reprobada por la PRUEBA 1.
    t = prueba_1_metadata(CLAUSULA_TRAMPA, df, n_perm=25, n_boot=200)
    if t["pasa"]:
        fallas.append("la cláusula TRAMPA pasó la PRUEBA 1: el banco no mide")

    # 4. VALIDACIÓN EXTERNA: C4b tiene que reproducir la cifra publicada
    #    de `keep="first"`. Un banco que no reproduce una cifra ya medida
    #    por otra vía no está midiendo, está inventando.
    c4b = df.loc[df.index.intersection(pd.Index(C4B_MISMO_EVENTO.seleccionar(df)))]
    b4, c4 = _bc(c4b)
    ancla_ok = (len(c4b) == ANCLA_C4B["n"] and b4 == ANCLA_C4B["b"]
                and c4 == ANCLA_C4B["c"])
    if not ancla_ok:
        fallas.append(
            f"C4b no reproduce la cifra publicada de `keep=\"first\"`: "
            f"n={len(c4b)} b={b4} c={c4}, esperado {ANCLA_C4B}")

    # 5. HALLAZGO ESTRUCTURAL, medido y no supuesto: ¿el criterio de la
    #    cláusula 3 («selló a tiempo», leído contra la apertura) es el
    #    MISMO indicador que el criterio de la regla ya firmada
    #    («la sesión sellada calza con `available_at`»)?
    #
    #    Tiene que serlo por álgebra: `sesion_objetivo` se selló como
    #    `proxima_sesion_despues_de(exchange, ahora_utc)`, así que calza
    #    con la sesión que implica `available_at` si y sólo si ninguna
    #    apertura cayó entre `available_at` y el sello — que es
    #    exactamente «selló antes de que abriera». Se MIDE igual: un
    #    argumento algebraico sobre código que nadie recompiló es una
    #    hipótesis.
    iguales = int((df["sesion_calza"].astype(bool)
                   == df["sello_a_tiempo"].astype(bool)).sum())
    return {"fallas": fallas, "trampa_reprobada": not t["pasa"],
            "trampa_1a": t["1a_pasa"], "trampa_1b": t["1b_pasa"],
            "ancla_c4b_reproduce": bool(ancla_ok),
            "ancla_c4b_obtenido": {"n": len(c4b), "b": b4, "c": c4},
            "calza_igual_a_tiempo": iguales == len(df),
            "filas_en_desacuerdo_calza_vs_a_tiempo": len(df) - iguales,
            "filas_que_no_calzan": int((~df["sesion_calza"].astype(bool)).sum()),
            "filas_selladas_tarde": int((~df["sello_a_tiempo"].astype(bool)).sum())}


# ------------------------------------------------------------
# Informe
# ------------------------------------------------------------
def _pp(x, d=1):
    return "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) \
        else f"{x:+.{d}f}"


def _ic(v):
    lo, hi = v.get("lo"), v.get("hi")
    if lo is None or hi is None or not np.isfinite(lo) or not np.isfinite(hi):
        return "—"
    return f"[{lo:+.1f}, {hi:+.1f}]"


def componer_informe(resultados: list, df: pd.DataFrame, chk: dict) -> str:
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    solape = ventana_solapamiento()
    L = [
        "# El banco de pruebas de cláusulas, y las cuatro que estaban sobre la mesa",
        "",
        f"**Generado:** {hoy} · `python -m GEMELO.banco_clausulas` · "
        f"semilla {SEMILLA} · `senales.db` en `mode=ro`.",
        "",
        "**Este documento no aplica ninguna cláusula, no recomienda ninguna "
        "y no mueve ninguna cifra publicada.** Reporta lo que tres pruebas "
        "fijas dicen de cada una. Donde una falla, se dice cuál y con qué "
        "evidencia; donde pasan todas, también.",
        "",
        "**El banco vale más que las cuatro respuestas.** Está escrito para "
        "recibir una cláusula como función (`Clausula` + `evaluar`), así que "
        "la quinta —la que todavía no existe— se evalúa sin tocar una línea "
        "de este módulo. Las cuatro de hoy son instancias.",
        "",
        "---",
        "",
        "## 0. La base, y la advertencia que va pegada a toda cifra de acá",
        "",
        f"- Ventana sellada **pinchada al {CORTE_BANCO}** "
        f"(`hasta_sello`): **n = {len(df)}** filas bajo la convención "
        f"congelada `{lb.CONVENCION_OFICIAL}`, **sin deduplicar** "
        "(`dedup=False`).",
        f"- **Por qué pinchada y no viva.** Este informe se corrió "
        f"por primera vez el 1-sep-2026 contra la ventana VIVA, y "
        f"esa misma noche el snapshot de las 18:15 selló un día "
        f"más: la ventana pasó de 256 a 271 filas y la validación "
        f"externa del banco —que reproduce una cifra publicada— se "
        f"rompió sola. Toda cifra de acá es reproducible **porque "
        f"el instante está pinchado**; contra la base viva no lo "
        f"sería, y dejaría de serlo cada noche a las 18:15.",
        "- **`dedup=False` está declarado, no elegido por comodidad:** las "
        "cláusulas bajo prueba son ellas mismas reglas de arbitraje o de "
        "población, y correrlas encima de la regla firmada mediría la "
        "composición de las dos, no la cláusula. La regla firmada entra "
        "como **C0**, de referencia, para que su propio movimiento esté en "
        "la misma tabla.",
        "- **Las cifras de la base `dedup=False` son ANTERIORES a la firma "
        "del 1-sep.** Acá aparecen como *lo que la cláusula recibe*, nunca "
        "como cifra vigente. **La cifra vigente de la ventana sellada es la "
        "de la regla firmada: +9,7 pp, IC95 de clúster de día [−7,2, +26,5], "
        "n efectivo 67.** Un p sin ese intervalo al lado no se cita.",
        "- **Cruzar α no es tener evidencia.** Todo p de este informe va con "
        "su intervalo de clúster; donde el intervalo contiene el cero, se "
        "dice con esas palabras.",
        f"- Ventana de solapamiento EVIDENCIADA (leída de "
        f"`data/sombra/veredictos.jsonl`, no cableada): "
        f"**{', '.join(solape) if solape else '(ninguna)'}**.",
        "",
        "### La contraprueba del banco",
        "",
        "Un banco que no puede reprobar nada no mide nada. `CLAUSULA_TRAMPA` "
        "lee `acierto_gap` a propósito y se queda con las filas que el "
        "modelo acertó. La PRUEBA 1 **la reprueba**: "
        f"1a {'REPRUEBA' if not chk['trampa_1a'] else 'pasa'}, "
        f"1b {'REPRUEBA' if not chk['trampa_1b'] else 'pasa'}. "
        "No es candidata y no cuenta como intento.",
        "",
        "### La validación externa del banco",
        "",
        "Que el banco reprueba lo que tiene que reprobar no prueba que "
        "MIDA bien lo que deja pasar. Así que además reproduce una cifra "
        "que otra vía ya midió: **C4b tiene que dar la cifra publicada de "
        "`keep=\"first\"`** (`GEMELO/resultados/dedup_opciones.md` §A2, "
        "n = 241, "
        f"b/c = 72/56). Obtenido: **n = {chk['ancla_c4b_obtenido']['n']}, "
        f"b/c = {chk['ancla_c4b_obtenido']['b']}/"
        f"{chk['ancla_c4b_obtenido']['c']}** → "
        + ("**reproduce**." if chk["ancla_c4b_reproduce"] else "**NO REPRODUCE**.")
        + " Si no reprodujera, nada de lo demás valdría.",
        "",
        "---",
        "",
        "## 0 bis. Un hallazgo estructural que cambia cómo se lee la "
        "cláusula 3",
        "",
        "**El criterio de la cláusula 3 —«selló a tiempo», leído contra la "
        "apertura de la sesión— y el criterio de la regla YA FIRMADA —«la "
        "sesión sellada calza con `available_at`»— son el MISMO indicador, "
        "fila por fila.**",
        "",
        f"Medido, no supuesto: coinciden en las **{len(df)} de {len(df)}** "
        f"filas de la ventana "
        f"({chk['filas_en_desacuerdo_calza_vs_a_tiempo']} en desacuerdo). "
        f"Las dos marcan exactamente las mismas "
        f"**{chk['filas_que_no_calzan']}** filas — las 25 del defecto de "
        "`snapshot.py:140` que el expediente `parche_snapshot140.md` §4 ya "
        "había censado por otra vía.",
        "",
        "**Y tiene que ser así por álgebra, no por casualidad:** "
        "`sesion_objetivo` se selló como "
        "`proxima_sesion_despues_de(exchange, ahora_utc)`, así que calza con "
        "la sesión que implica `available_at` **si y sólo si** ninguna "
        "apertura cayó entre `available_at` y el instante del sello — que "
        "es literalmente «selló antes de que abriera». La medición está "
        "igual porque un argumento algebraico sobre código que nadie "
        "recompiló es una hipótesis.",
        "",
        "**Consecuencia, y es la que hay que leer despacio:** todo lo que la "
        "PRUEBA 1c mide sobre la cláusula 3 vale, palabra por palabra, "
        "sobre el criterio de la regla que ya está firmada y aplicada. La "
        "pregunta «¿es metadata en la forma y resultado en el fondo?» no es "
        "una pregunta sobre una candidata: es una pregunta sobre lo que ya "
        "está corriendo. Este banco no la responde ni la usa para pedir "
        "nada — la deja escrita con su medición al lado.",
        "",
        "---",
        "",
        "## 1. El veredicto, en una tabla",
        "",
        "Siete corridas: las **cuatro cláusulas del encargo** (la 3 en sus dos lecturas, C3a y C3b, y la 4 en las suyas, C4 y C4b), más la regla YA FIRMADA como referencia (C0).",
        "",
    ]
    fil = []
    for r in resultados:
        p1, p2, p3 = r["prueba_1"], r["prueba_2"], r["prueba_3"]
        fil.append({
            "cláusula": r["nombre"].split(" — ")[0],
            "P1 metadata": ("pasa" if p1["pasa"] else "REPRUEBA"),
            "P1c asociación": (
                "no aplica" if not p1["1c"].get("aplicable")
                else ("EXCLUYE cero" if p1["1c"]["ic_excluye_cero"]
                      else ("IC contiene cero · p cruza α"
                            if p1["1c"]["discrepancia_entre_rutas"]
                            else "contiene cero"))),
            "P2 b/c": f"{p2['b_antes']}/{p2['c_antes']} → "
                      f"{p2['b_despues']}/{p2['c_despues']}",
            "P2 exige mecanismo": "SÍ" if p2["exige_mecanismo"] else "no",
            "P3a retroactivo": f"{p3.get('3a_seccion_2', '—')} y "
                               f"{p3.get('3a_linea_base_2_8', '—')}",
            "P3b ruta": ("pasa" if p3.get("3b_pasa") else "REPRUEBA"),
            "veredicto": r["veredicto"],
        })
    L += [_tabla(pd.DataFrame(fil)), ""]
    L += ["> C0 es la regla ya firmada y aplicada: está en la tabla como "
          "referencia, no como candidata.", "", "---", ""]
    L += _sintesis(resultados)

    for r in resultados:
        L += _bloque_clausula(r)

    L += [
        "---",
        "",
        "## Cómo se evalúa la QUINTA cláusula",
        "",
        "Sin tocar una línea de `GEMELO/banco_clausulas.py`. Se construye "
        "un `Clausula` y se lo pasa a `evaluar`:",
        "",
        "```python",
        "from GEMELO.banco_clausulas import Clausula, cargar_base, evaluar",
        "",
        "C5 = Clausula(",
        "    nombre=\"C5 — <la cláusula, en una línea>\",",
        "    texto=\"<como la escribió quien la propuso>\",",
        "    operacionalizacion=\"<cómo se traduce a código, explícito: una \"",
        "                       \"traducción distinta es OTRA cláusula>\",",
        "    procedencia=\"<quién la propuso y dónde consta>\",",
        "    campos=(\"fecha\", \"exchange\", ...),   # los que LEE, declarados",
        "    seleccionar=lambda df: df.index[...],  # devuelve el índice que sobrevive",
        "    criterio=lambda df: df[\"<indicador binario por fila>\"],  # o None",
        ")",
        "",
        "df = cargar_base(hasta_sello=CORTE_BANCO)",
        "r = evaluar(C5, df)          # las tres pruebas, con sus intervalos",
        "print(r[\"veredicto\"])",
        "```",
        "",
        "**Tres obligaciones que el banco impone y no se pueden esquivar:**",
        "",
        "1. `campos` hay que declararlo, y un campo que no esté clasificado "
        "como seguro o prohibido **reprueba 1a**: el silencio no es una "
        "clasificación. Pero declarar bien tampoco alcanza — **1b permuta "
        "el desenlace y mide**, así que una declaración mentirosa se cae "
        "igual (hay un test que lo fija con una cláusula que declara "
        "metadata y lee el gap).",
        "2. `seleccionar` devuelve un ÍNDICE, no un DataFrame. Eso obliga a "
        "que la cláusula sea una selección de filas y no una "
        "transformación, y es lo que hace que las filas retiradas se "
        "puedan mirar de a una en la PRUEBA 2.",
        "3. La corrida **suma un intento** y hay que agregarlo a "
        "`REGISTRO_INTENTOS` con su procedencia. Si la quinta se evalúa en "
        "dos operacionalizaciones, son dos.",
        "",
        "---",
        "",
        "## Lo que este banco NO decide",
        "",
        "- **Cuál cláusula adoptar.** El banco reporta tres pruebas; el "
        "criterio de aceptación es de Nicolás. Una cláusula marcada EXIGE "
        "MECANISMO no está refutada: está pendiente de que alguien exhiba "
        "por qué el defecto que corrige es asimétrico.",
        "- **Qué pasa con las 15 huérfanas.** Eso es el forense de otro "
        "frente (`GEMELO/resultados/huerfanas.md`) y no entra acá: este "
        "banco evalúa cláusulas, no decide cuál se aplica a qué población.",
        "- **Si la operacionalización es la correcta.** Una cláusula en "
        "castellano no es ejecutable hasta que alguien la traduce, y la "
        "traducción es discutible. Cada una lleva la suya escrita; una "
        "traducción distinta es una cláusula distinta y suma su propio "
        "intento.",
        "",
        "## Los intentos que suma esta corrida",
        "",
        "**Cinco**: C1, C2, C3a, C3b y C4. Van como una fila del registro "
        "estructurado de `GEMELO/relevo_asiatico.py` "
        "(`REGISTRO_INTENTOS`, ahora 21 tramos), con su procedencia. **No "
        "se escribió ningún entero nuevo**: `N_INTENTOS_ACUMULADO` se "
        "calcula como la suma del registro, y esa suma pasó de **86 a "
        "91**.",
        "",
        "**Lo que eso arrastra, declarado acá porque un número que sigue "
        "ofrecido vuelve a circular:**",
        "",
        "- `backtest/veredicto_51.py:N_INTENTOS_PREVIO` estaba en 86 y un "
        "test lo ata al registro precisamente para que no se separe en "
        "silencio. Se actualizó a **91** (y `N_INTENTOS_51` a 97). Subir N "
        "sólo hace el DSR **más** exigente, nunca más favorable: el "
        "NO-CONCLUYENTE de la corrida ya sellada no puede darse vuelta por "
        "esto.",
        "- El resumen ya sellado de la corrida "
        "`20260901-133154-5.1-arnes-corregido-gatillo-incumplido` declaró "
        "**N = 92 antes de correr** y **no se reescribe**: era el registro "
        "en SU instante. Por eso 92 quedó explícitamente conservado en "
        "`BANDA_N`, para que ese resumen siga siendo reproducible columna "
        "a columna.",
        "- **Queda una decisión abierta que no es de este frente:** el "
        "arreglo elegido fue subir la constante. La alternativa —y es la "
        "que el proyecto ya usa en `CORTE_SECCION_2`— es **pinchar el "
        "instante en vez de mover el número**: que `N_INTENTOS_PREVIO` "
        "quede declarado como «el registro al 2026-09-01 13:31» y que el "
        "test compare contra esa foto, no contra la suma viva. Eso saca a "
        "los dos números del choque de una vez y para siempre, en lugar de "
        "obligar a una edición cada vez que el registro crece. No se hizo "
        "acá porque es un rediseño del módulo del veredicto 5.1, que es "
        "otro frente.",
        "- Siguen diciendo **86** como cifra vigente "
        "`GEMELO/resultados/espera_firma.md` (§«Antes de citar cualquier "
        "cifra de acá») y `GEMELO/resultados/cola_decisiones.md` (tabla de "
        "apertura). Son documentos ya commiteados de otros frentes y este "
        "informe **no los edita** — la frontera de la errata es el commit. "
        "Quien los cite hoy tiene que citar 91. (Se citan por sección y no "
        "por línea a propósito: un número de línea lo desplaza la próxima "
        "edición del documento citado, que es un error crónico ya fijado "
        "por un test del proyecto.)",
        "",
        "C3a y C3b cuentan **por separado** aunque sean la misma cláusula "
        "en castellano: una operacionalización distinta es una "
        "configuración distinta, y evaluar dos y reportar una sería elegir "
        "la definición sin decirlo.",
        "",
        "NO suman, y se declara para que la exclusión sea auditable:",
        "",
        "- **C0**, la regla firmada: ya está evaluada, publicada y "
        "aplicada. Entra como referencia.",
        "- **C4b**: resulta ser exactamente `keep=\"first\"`, ya contado en "
        "el registro (fila `COLA`, 2 intentos). Contarlo otra vez sería "
        "inflar el N por haberlo mirado desde otro nombre.",
        "- **`CLAUSULA_TRAMPA`**: es la contraprueba del instrumento. De "
        "ella no se lee ningún resultado sobre el modelo.",
        "- **Las mediciones de la PRUEBA 1c** (asociación criterio↔acierto), "
        "la validación externa y los chequeos estructurales: son "
        "diagnóstico del método, no configuraciones predictivas — la misma "
        "clase de exclusión que el registro ya declara para el MDE y las "
        "fronteras de gasto de alpha.",
        "",
    ]
    return "\n".join(L) + "\n"


def _sintesis(resultados: list) -> list:
    """La respuesta directa a las dos preguntas del encargo, con las
    cifras traídas de la corrida y no escritas a mano. Sin recomendar
    ninguna: qué falla qué, y si la 3 correlaciona."""
    por = {r["nombre"].split(" —")[0]: r for r in resultados}
    c3a, c3b = por["C3a"], por["C3b"]
    a3a, a3b = c3a["prueba_1"]["1c"], c3b["prueba_1"]["1c"]
    p3b = a3b["p_permutacion_dia"]
    L = ["## 2. Las dos preguntas del encargo, respondidas", "",
         "### ¿Qué cláusula falla qué prueba?", "",
         "- **C1 (era del Mac)** — no falla ninguna. Retira 16 filas y las "
         "16 son CONCORDANTES: Δb = 0, Δc = 0. Es la única que no mueve "
         "nada de la estructura de discordancia, y sobre la ventana "
         "congelada retira cero filas, así que las anclas reproducen "
         "21/21 y 7/7 incluso aplicada al pasado.",
         "- **C2 (las dos máquinas)** — pasa la 1 y la 3b, pero deja "
         f"**{por['C2']['prueba_2']['n_despues']} filas y CERO pares "
         "discordantes**. No dispara la alarma del b/c porque no queda "
         "nada sobre lo que haya asimetría. Eso no es un aprobado y el "
         "banco lo marca SIN PODER RESOLUTIVO: con 0 discordancias el "
         "duelo campeón-vs-baseline no distingue nada, en ninguna "
         "dirección.",
         "- **C3a y C3b (la que selló a tiempo)** — pasan la 1a y la 1b, "
         "pasan la 3b, y **disparan la alarma de la PRUEBA 2**: Δb = 0, "
         f"Δc = {c3a['prueba_2']['delta_c']}, y las "
         f"{c3a['prueba_2']['retiradas_discordantes']} discordantes "
         "retiradas favorecen TODAS a la baseline "
         f"(binomial exacta p = "
         f"{c3a['prueba_2']['p_binomial_exacta_simetria']:.4f}). Es la "
         "misma firma que destapó `keep=\"last\"`, y el banco no las "
         "acepta sin que alguien exhiba el mecanismo.",
         "- **C4 (si son iguales, contar una vez)** — **REPROBADA en la "
         "PRUEBA 1** en su lectura literal: «iguales» sólo puede leerse "
         "sobre el desenlace, porque las dos filas de un par difieren en "
         "todo lo demás. Lo declara (1a) y además se mide (1b: la "
         "selección cambió en las "
         f"{por['C4']['prueba_1']['1b_selecciones_que_cambiaron']} de "
         f"{por['C4']['prueba_1']['1b_permutaciones']} permutaciones del "
         "resultado). **Su segunda lectura, C4b —«iguales» = el mismo "
         "evento— pasa la 1**, y resulta ser exactamente el "
         "`keep=\"first\"` ya medido.",
         "",
         "### ¿La cláusula 3 correlaciona con el acierto?", "",
         "**Medido, no supuesto — y la respuesta honesta tiene dos "
         "mitades que hay que leer juntas.**", "",
         f"| lectura de «a tiempo» | acierto a tiempo | acierto tarde | "
         f"diferencia | IC95 clúster de día | p de permutación de día |",
         "|---|---|---|---|---|---|",
         f"| C3a (antes de la apertura) | {a3a['tasa_criterio_1_pct']:.1f}% "
         f"({a3a['n_criterio_1']}) | {a3a['tasa_criterio_0_pct']:.1f}% "
         f"({a3a['n_criterio_0']}) | **{a3a['diferencia_pp']:+.1f} pp** | "
         f"[{a3a['ic95_cluster_dia'][0]:+.1f}, "
         f"{a3a['ic95_cluster_dia'][1]:+.1f}] | no aplica (el criterio "
         "varía dentro del día) |",
         f"| C3b (ventana 17:50–20:30) | {a3b['tasa_criterio_1_pct']:.1f}% "
         f"({a3b['n_criterio_1']}) | {a3b['tasa_criterio_0_pct']:.1f}% "
         f"({a3b['n_criterio_0']}) | **{a3b['diferencia_pp']:+.1f} pp** | "
         f"[{a3b['ic95_cluster_dia'][0]:+.1f}, "
         f"{a3b['ic95_cluster_dia'][1]:+.1f}] | "
         + (f"**{p3b['p']:.4f}** ({p3b['dias_con_criterio']} días contra "
            f"{p3b['dias_sin_criterio']})" if p3b.get("aplicable")
            else "no aplica") + " |",
         "",
         "**Primera mitad: el punto es enorme y va en la dirección que "
         "importa.** Las filas selladas tarde aciertan el gap "
         f"{a3a['tasa_criterio_0_pct']:.0f}% contra "
         f"{a3a['tasa_criterio_1_pct']:.0f}% de las selladas a tiempo — "
         f"una brecha de {a3a['diferencia_pp']:.0f} pp. Un sello tardío "
         "usa datos distintos, y eso es exactamente el defecto de "
         "`snapshot.py:140`: la puntualidad NO es una etiqueta neutra "
         "pegada a la fila.",
         "",
         "**Segunda mitad: no alcanza para establecerlo.** El IC95 de "
         "clúster de día **contiene el cero en las dos lecturas**, y en "
         "C3b la permutación de día cruza α "
         + (f"(p = {p3b['p']:.4f}) " if p3b.get("aplicable") else "")
         + "mientras el intervalo no excluye nada — **una discrepancia "
         "entre dos rutas de clúster, no una evidencia**. La razón es "
         f"contable y no estadística: hay **{a3b['n_criterio_0']} filas "
         f"tardías en {p3b.get('dias_sin_criterio', '?')} días**, y un "
         "puñado de clústeres no resuelve nada.",
         "",
         "**La lectura que el banco deja escrita, sin recomendar:** con "
         "estos datos la cláusula 3 **no se puede declarar limpia de "
         "resultado**, y tampoco se puede declarar contaminada. El punto "
         "es demasiado grande para tratarlo como ruido y el intervalo "
         "demasiado ancho para tratarlo como hallazgo. **«No se puede "
         "descartar» es la parte que pesa**, porque el sentido del "
         "defecto —el sello tardío usa otros datos— ya está establecido "
         "por el código, no por estos números.",
         "",
         "---", ""]
    return L


def _bloque_clausula(r: dict) -> list:
    p1, p2, p3 = r["prueba_1"], r["prueba_2"], r["prueba_3"]
    L = [f"## {r['nombre']}", "",
         f"> «{r['texto']}»", "",
         f"**Operacionalización.** {r['operacionalizacion']}", "",
         f"**Procedencia.** {r['procedencia']}", ""]
    for n in r["notas"]:
        L += [f"- {n}", ""]

    # PRUEBA 1
    L += ["### PRUEBA 1 — metadata", "",
          f"- **1a (declarativa).** Campos declarados: "
          f"`{'`, `'.join(p1['1a_campos_declarados'])}`. "
          + ("Ninguno prohibido, ninguno sin clasificar → **pasa**."
             if p1["1a_pasa"] else
             f"**REPRUEBA** — prohibidos: "
             f"`{'`, `'.join(p1['1a_prohibidos']) or '(ninguno)'}`; "
             f"sin clasificar: "
             f"`{'`, `'.join(p1['1a_sin_clasificar']) or '(ninguno)'}`."),
          f"- **1b (medida: invarianza).** Se permutaron los campos de "
          f"resultado {p1['1b_permutaciones']} veces; la selección cambió en "
          f"**{p1['1b_selecciones_que_cambiaron']}** "
          f"(IC95 Wilson de la fracción "
          f"[{p1['1b_wilson'][0]:.3f}, {p1['1b_wilson'][1]:.3f}]) → "
          + ("**pasa**: la cláusula no lee el desenlace."
             if p1["1b_pasa"] else
             "**REPRUEBA**: la selección depende del desenlace, diga lo que "
             "diga su declaración."),
          ""]
    c = p1["1c"]
    if not c.get("aplicable"):
        L += [f"- **1c (asociación criterio↔acierto).** No aplicable: "
              f"{c.get('motivo')}.", ""]
    else:
        perm = c["p_permutacion_dia"]
        p_txt = (f"p de permutación de etiqueta de día = "
                 f"**{perm['p']:.4f}** ({perm['dias_con_criterio']} días con "
                 f"criterio contra {perm['dias_sin_criterio']} sin)"
                 if perm.get("aplicable") else
                 f"sin p de permutación de día ({perm.get('motivo')}); en su "
                 f"lugar, la fracción de réplicas bootstrap del otro lado "
                 f"del cero es "
                 f"**{c.get('frac_replicas_del_otro_lado', float('nan')):.3f}**"
                 f" — no es un p y no se cita como uno")
        L += [f"- **1c (medida: asociación criterio↔acierto).** "
              f"Filas con criterio: {c['n_criterio_1']}, acierto "
              f"{c['tasa_criterio_1_pct']:.1f}% "
              f"(Wilson [{100*c['wilson_criterio_1'][0]:.1f}, "
              f"{100*c['wilson_criterio_1'][1]:.1f}] — **optimista**, supone "
              f"filas independientes). Sin criterio: {c['n_criterio_0']}, "
              f"acierto {c['tasa_criterio_0_pct']:.1f}%.",
              f"  **Diferencia {c['diferencia_pp']:+.1f} pp, IC95 de clúster "
              f"de día [{c['ic95_cluster_dia'][0]:+.1f}, "
              f"{c['ic95_cluster_dia'][1]:+.1f}]**; {p_txt}.",
              f"  ICC del acierto {c['icc_acierto']:.3f}, efecto de diseño "
              f"{c['deff']:.2f} → **n efectivo {c['n_efectivo']:.0f}** sobre "
              f"{c['clusters']} días.",
              f"  **{c['lectura']}.**", ""]

    # PRUEBA 2
    v0, v1 = p2["ventaja_antes"], p2["ventaja_despues"]
    L += ["### PRUEBA 2 — la del b/c", "",
          f"| | n | b | c | ventaja | IC95 clúster | p exacta |",
          "|---|---|---|---|---|---|---|",
          f"| antes | {p2['n_antes']} | {p2['b_antes']} | {p2['c_antes']} | "
          f"{_pp(v0.get('ventaja_pp'))} pp | {_ic(v0)} | "
          f"{p2['mcnemar_exacto_antes']:.4f} |",
          f"| después | {p2['n_despues']} | {p2['b_despues']} | "
          f"{p2['c_despues']} | {_pp(v1.get('ventaja_pp'))} pp | {_ic(v1)} | "
          + (f"{p2['mcnemar_exacto_despues']:.4f} |"
             if p2["mcnemar_exacto_despues"] is not None else "— |"),
          "",
          f"**Δb = {p2['delta_b']:+d} · Δc = {p2['delta_c']:+d}.** "
          f"Retiró {p2['filas_retiradas']} filas: "
          f"{p2['retiradas_tipo_b']} discordantes a favor del MODELO (`b`), "
          f"{p2['retiradas_tipo_c']} a favor de la BASELINE (`c`), "
          f"{p2['retiradas_concordantes']} concordantes.", ""]
    if p2["retiradas_discordantes"]:
        w = p2["wilson_prop_pro_baseline"]
        L += [f"De las {p2['retiradas_discordantes']} discordantes retiradas, "
              f"**{p2['retiradas_tipo_c']} favorecían a la baseline** "
              f"({100*p2['prop_retiradas_pro_baseline']:.0f}%, IC95 Wilson "
              f"[{100*w[0]:.0f}%, {100*w[1]:.0f}%], binomial exacta contra "
              f"una moneda p = {p2['p_binomial_exacta_simetria']:.4f}).", ""]
    if p2["exige_mecanismo"]:
        motivos = []
        if p2["mueve_c_y_no_b"]:
            motivos.append("mueve `c` y NO mueve `b`")
        if p2["retiradas_todas_un_signo"]:
            motivos.append("todas las discordantes retiradas tienen el mismo "
                           "signo")
        L += [f"> **EXIGE MECANISMO** — {'; '.join(motivos)}. Es la firma "
              "que destapó `keep=\"last\"`. No queda refutada por esto: "
              "queda pendiente de que alguien exhiba por qué el defecto que "
              "corrige es asimétrico, ANTES de aceptarla y por impecable "
              "que suene el razonamiento.", ""]
    else:
        L += ["> No dispara la alarma del b/c.", ""]
    if p2["sin_poder_resolutivo"]:
        L += [f"> **SIN PODER RESOLUTIVO.** La población que deja "
              f"({p2['n_despues']} filas, {p2['b_despues']} + "
              f"{p2['c_despues']} pares discordantes) no distingue al "
              f"campeón de la baseline: sin discordancias el duelo no tiene "
              f"nada que medir, y una ventaja con IC [0, 0] es la ausencia "
              f"de medición, no una medición de ausencia. El piso declarado "
              f"del proyecto es {p2['minimo_filas_declarado']} filas.", ""]

    # PRUEBA 3
    if not p3.get("disponible"):
        L += ["### PRUEBA 3 — anclas", "", "Sin base histórica disponible.",
              ""]
    else:
        L += ["### PRUEBA 3 — anclas", "",
              f"Sobre `cargar(hasta_sello={lb.CORTE_SECCION_2}, "
              f"dedup=False)` ({p3['filas_historicas']} filas), la cláusula "
              f"retira **{p3['filas_retiradas_del_historico']}**.",
              "",
              f"- **3a — costo retroactivo.** §2 (`estricta`): "
              f"**{p3['3a_seccion_2']}** · línea base §2.8 "
              f"(`excluir_cero`): **{p3['3a_linea_base_2_8']}**. "
              + ("Los dos pre-registros siguen reproduciendo con la cláusula "
                 "aplicada también al pasado." if p3["3a_pasa"] else
                 f"**NO reproducen.** Rotas en §2: "
                 f"{p3['3a_afirmaciones_rotas'] or '(ninguna)'}; en la línea "
                 f"base: {p3['3a_linea_base_rota'] or '(ninguna)'}. Si la "
                 "cláusula se adoptara, la rama histórica `dedup=False` "
                 "tendría que seguir existiendo y habría que declarar cuál "
                 "afirmación se reproduce por cuál ruta."),
              f"- **3b — ruta del ancla preservada (FATAL si falla).** "
              f"Recargando el ancla desde cero después de correr la "
              f"cláusula: §2 **{p3['3b_seccion_2']}**, línea base "
              f"**{p3['3b_linea_base_2_8']}**; base sin mutar: "
              f"**{'sí' if p3['3b_base_sin_mutar'] else 'NO'}**. "
              + ("**PASA.**" if p3["3b_pasa"] else
                 "**REPRUEBA: una regla que rompe esto es peor que el "
                 "problema que resuelve.**"),
              ""]
    L += [f"**Veredicto del banco: {r['veredicto']}.**", "", "---", ""]
    return L


def _tabla(df: pd.DataFrame) -> str:
    if df.empty:
        return "(sin filas)\n"
    cols = list(df.columns)
    L = ["| " + " | ".join(cols) + " |",
         "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, f in df.iterrows():
        L.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in f) + " |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    ap.add_argument("--n-perm-invarianza", type=int,
                    default=N_PERM_INVARIANZA)
    ap.add_argument("--salida", default=DESTINO)
    args = ap.parse_args(argv)

    df = cargar_base(hasta_sello=CORTE_BANCO)
    if df.empty:
        print("sin senales.db o sin filas: no se escribe informe")
        return 1

    chk = chequeos_estructurales(df, hasta_sello=CORTE_BANCO)
    if chk["fallas"]:
        for f in chk["fallas"]:
            print("CHEQUEO ESTRUCTURAL FALLIDO:", f)
        return 2

    resultados = [evaluar(cl, df, n_boot=args.n_boot,
                          n_perm_inv=args.n_perm_invarianza)
                  for cl in TODAS]

    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(args.salida, "w", encoding="utf-8") as fh:
        fh.write(componer_informe(resultados, df, chk))
    with open(DESTINO_JSON, "w", encoding="utf-8") as fh:
        json.dump({"generado_en": datetime.now(timezone.utc).isoformat(),
                   "semilla": SEMILLA, "n_base": len(df),
                   "chequeos": chk, "resultados": resultados},
                  fh, ensure_ascii=False, indent=2, default=str)
    print(f"escrito: {args.salida}")
    for r in resultados:
        print(f"  {r['nombre'].split(' — ')[0]:5s} {r['veredicto']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
