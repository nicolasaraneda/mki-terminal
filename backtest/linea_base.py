# ============================================================
# linea_base.py — reproducción de la §2 de GEMELO/DISEÑO.md dentro del
# harness (Etapa 6.0.0, §9: es lo ÚNICO autorizado a empezar).
#
#   source venv/bin/activate
#   python -m backtest.linea_base                    # informe completo
#   python -m backtest.linea_base --convencion verificador
#
# Las cifras de la §2 salieron de un análisis externo sobre
# data/backups/*.csv. Aquí se recalculan desde senales.db en mode=ro, que
# es la autoridad. Si el harness contradice al documento, **manda el
# harness y el hallazgo se reporta** — el pre-registro NO se edita para
# que cuadre (DECISIONES.md §23).
#
# SOLO LECTURA por construcción, como todo backtest/: la única conexión
# sale de _conexion_ro (uri mode=ro; propia desde la 16-3, ver abajo). Este módulo no escribe en
# ninguna base ni toca motor.py.
#
# ------------------------------------------------------------
# LA CONVENCIÓN DEL EMPATE — leer antes de comparar cifras
# ------------------------------------------------------------
# El verificador de producción puntúa al campeón con `>=`:
#     acierto_gap = 1 si (est_pct >= 0) == (gap >= 0)      senales.py:373
# es decir, un gap de EXACTAMENTE 0.0 cuenta como "al alza" y el campeón
# acierta si predijo >= 0.
#
# Hay 5 filas con gap_pct == 0.0 en las 228. Cómo se traten cambia el
# resultado titular. GEMELO/DISEÑO.md §2.8 CONGELÓ `excluir_cero` el
# 26-ago; las tres se siguen calculando y el informe las muestra JUNTAS,
# porque la elección debe quedar auditable y no escondida en un default.
#
#   "estricta"    baseline acierta si gap  > 0   ← la del documento
#   "verificador" baseline acierta si gap >= 0   ← simétrica con el campeón
#   "excluir_cero" se descartan las 5 filas de ambos lados
#
# `gap == 0.0` exacto significa apertura idéntica al cierre previo, que es
# la firma del ffill de feriados (Supuesto #1 de CLAUDE.md): "un feriado
# se ve como +0.00%". Son artefactos de datos, no eventos de mercado.
#
# ------------------------------------------------------------
# LA REGLA DE DEDUPLICACIÓN — firmada el 1-sep-2026
# ------------------------------------------------------------
# Treinta filas selladas (quince pares) apuntan a la MISMA
# `sesion_objetivo` con el mismo `gap_pct`. Nicolás firmó la regla y su
# texto es el criterio, no una lista de fechas:
#
#   «Los dos grupos se tratan por separado, porque tienen orígenes
#    distintos y una sola regla sería arbitraria por construcción.
#    Grupo del defecto de snapshot.py: la fila válida es la que tiene la
#    sesión objetivo correcta según `available_at`, no la más reciente.
#    El criterio es la corrección de la sesión, nunca la frescura.
#    Grupo de feriados reales: las dos emisiones están igualmente a
#    tiempo, así que no es un problema de deduplicación.
#    QUEDA PROHIBIDO keep="last" o cualquier regla equivalente por
#    frescura: el forense demostró que retira selectivamente errores del
#    modelo.»
#
# La regla se implementa SOLA y no clasifica grupos a mano: dentro de cada
# par, se conserva la fila cuya `sesion_objetivo` coincide con
# `calendarios.proxima_sesion_despues_de(exchange, available_at)`. En los
# 10 pares del defecto eso deja UNA fila; en los 5 de feriado las dos
# calzan y no se descarta nada — la separación es una consecuencia del
# criterio, no una entrada de él. Una lista de fechas cableada sería la
# regla escondiendo su propio criterio.
#
# ALCANCE, declarado porque importa: la regla es de DEDUPLICACIÓN. Sólo
# actúa dentro de grupos `(ticker, sesion_objetivo)` con más de una fila.
# NO es un filtro global de coherencia — ver `auditar_dedup()`, que cuenta
# cuántas filas SIN pareja tampoco calzan (hoy 15) y las deja intactas a
# propósito: retirarlas sería otra decisión, no ésta, y no está firmada.
#
# La exclusión vive AQUÍ, en la capa de medición, por la misma razón que
# `excluir_cero`: `senales.py` no se toca y ninguna fila sellada se
# reescribe.
#
# ------------------------------------------------------------
# LA REGLA DE CONOCIBILIDAD — firmada el 29-sep-2026
# ------------------------------------------------------------
# Toda fila sellada declara dos instantes: `timestamp_utc` (cuándo se
# emitió) y `available_at` (cuándo era conocible el insumo que usó: el
# cierre UTC de la sesión del SOX). Una fila con
#
#     available_at > timestamp_utc
#
# declara que su insumo fue conocible DESPUÉS de que la fila ya existía.
# No usó un cierre sino una barra de sesión abierta, y un tercero no puede
# reproducirla desde el registro sellado. Queda FUERA de toda métrica
# (DECISIONES.md, acta §90.1 d).
#
# El criterio es POR REGLA y no por fecha: este módulo no nombra ningún
# día. Las filas que alcanza salen de comparar los dos instantes —como
# instantes con zona, no como texto—, se cuentan en
# `auditar_conocibilidad()` y el informe las declara. El orden es
# ESTRICTO: la igualdad (la rama del `except` de snapshot.py, que deja
# `available_at` en el reloj de pared) no queda alcanzada; ésa tiene su
# propia alerta en el vigía.
#
# ORDEN DE APLICACIÓN: la exclusión corre ANTES que la deduplicación. Una
# fila fuera de toda métrica tampoco arbitra un par: deduplicando primero,
# una fila inválida que «calza» podría retirar a su pareja válida y caer
# después ella, y se perderían las dos.
#
# Vive AQUÍ por la misma razón que las otras dos: las filas alcanzadas
# conservan su `estado` y su fila en `verificacion_apertura` como registro
# histórico, y ninguna fila sellada se reescribe.
#
# ALCANCE, declarado porque importa: la regla se define sobre
# `senales_ticker`, que es la tabla que sella `available_at`. La tabla
# `snapshots` no lo sella, así que el `regimen` de un snapshot emitido con
# la sesión abierta NO queda alcanzado (conteo de regímenes de
# `salud_r2_regimen_beta`). Retirarlo sería otra regla, y no está firmada.
# ============================================================

import argparse
import math
import os
import sqlite3
import sys
from datetime import datetime, timezone

import pandas as pd

import calendarios
from api.utilidades import intervalo_wilson
from version import MODELO_VERSION

# Corrida 16-3 (B5 del dictamen del auditor sobre la fuente única): hasta acá
# `RUTA_SENALES` y `_conexion_ro` se importaban de `backtest/datos.py`, que a
# nivel de módulo importa `motor` (y con él yfinance, numpy y
# exchange_calendars). Desde la 16-3 el reporte de Telegram importa este módulo,
# y la garantía de la 5.0 es que el reporte compone aunque el motor no exista:
# un `import motor` roto habría matado el reporte entero a las 18:25. Los dos
# símbolos son triviales y viven acá; `backtest/datos.py` conserva los suyos.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_SENALES = os.path.join(RAIZ, "senales.db")


def _conexion_ro(ruta: str) -> sqlite3.Connection:
    """Conexión ESTRICTAMENTE de solo lectura a una base de producción
    (la misma de `backtest.datos._conexion_ro`, sin arrastrar el motor)."""
    return sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "resultados", "linea_base")

CONVENCIONES = ("estricta", "verificador", "excluir_cero")

# CONGELADA en GEMELO/DISEÑO.md §2.8 el 26-ago: las 5 filas con
# `gap_pct == 0.00` se excluyen de AMBOS lados. No son eventos de mercado
# sino artefactos del ffill de feriados, y excluirlas es la única salida que
# no obliga a elegir a quién se le regala el empate.
#
# La exclusión vive AQUÍ, en la capa de medición. `senales.py` NO se toca:
# `acierto_gap` es un valor sellado, y cambiar el scoring reescribiría el
# significado de filas ya selladas.
CONVENCION_OFICIAL = "excluir_cero"

# FIRMADA el 1-sep-2026 (DECISIONES.md, acta de la regla de deduplicación).
# `cargar()` la aplica por defecto: dejar la rama sin deduplicar como
# default sería seguir ofreciendo desde el código un conjunto de filas que
# la firma retiró, y un número retirado que sigue ofrecido vuelve a
# circular. Quien reproduce una afirmación CONGELADA anterior a la firma
# —la §2 y la línea base de la §2.8— pasa `dedup=False` explícitamente y
# dice por qué.
DEDUP_OFICIAL = True

# FIRMADA el 29-sep-2026 (DECISIONES.md, acta §90.1 d). `cargar()` la
# aplica por defecto, por la misma razón que la deduplicación: una fila
# retirada que el código sigue ofreciendo vuelve a circular.
# `conocibilidad=False` existe sólo para poder CONTAR lo que la regla
# retira y para probar que no mueve ninguna ventana congelada.
CONOCIBILIDAD_OFICIAL = True

# ------------------------------------------------------------
# EL INSTANTE «A LA FECHA» DE LA §2 — hallazgo del 30-ago (WS5)
# ------------------------------------------------------------
# Las cifras de la §2 son una medición PUNTUAL: se tomaron el 25-ago sobre
# las verificaciones que existían entonces (n=228). El track record sigue
# creciendo —el 30-ago ya son 245— así que reproducir «la §2» contra la
# base completa compara una cifra congelada con un denominador que se
# mueve. Los cinco tests de reproducción llevaban esa dependencia con el
# reloj sin declararla y empezaron a fallar solos.
#
# La corrección NO toca ninguna cifra del documento: le devuelve su
# instante. Es la misma disciplina que el proyecto ya aplica en todas
# partes —un dato sin su `available_at` no significa nada— aplicada a una
# afirmación en vez de a un precio.
#
# El instante es UNO SOLO —el último sello anterior al congelamiento— y
# reproduce las tres familias de cifras a la vez:
#   verificaciones con `verificado_en` <= 24-ago  → 228 filas exactas
#     (la última tanda fue la del 24-ago 22:15:39 UTC, acumulado 228; la
#      siguiente, del 26-ago, ya suma 9 más)
#   snapshots con `fecha` <= 24-ago               → 35, como dice el doc
#   betas con `fecha` <= 24-ago                   → |Δβ| 0.0427 (doc 0.043)
#
# Filtrar por `verificado_en` y no por `fecha_senal` no es un detalle: el
# 21-ago tiene filas verificadas a ambos lados del congelamiento, así que
# NINGÚN corte por fecha de señal reproduce las 228.
#
# El corte es OPT-IN a propósito: `cargar()` sin argumentos sigue leyendo
# el track record VIVO, que es lo correcto para la plataforma. Pinchar el
# instante es cosa de quien reproduce una afirmación congelada.
CORTE_SECCION_2 = "2026-08-24"

# El segundo instante pinchado, por la misma razón y con una lección
# propia. La regla de deduplicación se firmó (acta §60) conociendo dos
# desenlaces —p = 0,1847 sin deduplicar y p = 0,0323 con `keep="last"`,
# prohibida— y produjo un tercero: bajo la convención oficial la ventaja
# cruza α. Ese hallazgo se fijó como test contra la ventana VIVA, y el
# 1-sep-2026 a las 18:15 producción selló un día más: el p SIN deduplicar
# pasó de 0,1849 a 0,0486 y el test que fijaba «> 0,05» se cayó solo.
#
# No es un test roto: es la demostración más nítida de lo que esta misma
# corrida estableció —CRUZAR α NO ES TENER EVIDENCIA—. Un solo día de
# sellado movió el p de un lado al otro del umbral. Lo que estaba mal era
# verificar una afirmación congelada contra una base que crece.
CORTE_REGLA_FIRMADA = "2026-08-31"

# La línea base oficial que la §2.8 congela.
LINEA_BASE_OFICIAL = (
    ("n",                   223,    0),
    ("modelo: acierto %",    65.9,  0.05),
    ("baseline: acierto %",  61.9,  0.05),
    ("ventaja pp",            4.0,  0.05),
    ("McNemar b01",          64,    0),
    ("McNemar b10",          55,    0),
    ("McNemar p",             0.4633, 0.0005),
)
TAM_BLOQUE = 40
UMBRALES_ZONA_MUERTA = (0.00, 0.15, 0.25, 0.30, 0.50, 0.75)
NOMINAL_INTERVALO = 0.80


# ------------------------------------------------------------
# Estadística — stdlib, sin dependencias nuevas
# ------------------------------------------------------------
# El proyecto fija requirements.txt y las dos máquinas deben tener
# dependencias idénticas (DECISIONES.md, asimetría de intérprete): añadir
# scipy solo para esto rompería esa invariante. chi2 con 1 gl tiene forma
# cerrada: sf(x) = erfc(sqrt(x/2)).
def chi2_sf_1gl(x: float) -> float:
    return math.erfc(math.sqrt(x / 2.0)) if x > 0 else 1.0


def mcnemar(b01: int, b10: int, correccion: bool = True) -> float:
    """p de McNemar sobre los DESACUERDOS. `b01` = el modelo acierta donde
    la baseline falla; `b10` al revés. Con corrección de continuidad de
    Edwards por defecto: es la variante que reproduce el 0.3193 que el
    documento reporta para 67 vs 55 (sin corrección daría 0.2773)."""
    n = b01 + b10
    if n == 0:
        return 1.0
    d = abs(b01 - b10) - (1 if correccion else 0)
    d = max(d, 0)
    return chi2_sf_1gl(d * d / n)


def _wilson(aciertos: int, n: int) -> tuple:
    return intervalo_wilson(int(aciertos), int(n))


# ------------------------------------------------------------
# La regla de deduplicación, firmada — ver la cabecera
# ------------------------------------------------------------
_MEMO_SESION: dict = {}


def sesion_correcta(exchange: str, available_at: str) -> str | None:
    """La sesión que la predicción DEBÍA apuntar según el instante en que
    su información se volvió conocible.

    `available_at` es el cierre UTC real del SOX que alimenta la
    predicción (`snapshot.py`:133), calculado por una vía independiente de
    la línea defectuosa (`:140`, que usa el reloj de pared del proceso).
    Ese es exactamente el motivo por el que sirve de árbitro: no comparte
    mecanismo con la cifra que juzga."""
    if not exchange or not available_at or pd.isna(available_at):
        return None
    clave = (exchange, str(available_at))
    if clave not in _MEMO_SESION:
        t = datetime.fromisoformat(str(available_at))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        try:
            _MEMO_SESION[clave] = str(
                calendarios.proxima_sesion_despues_de(exchange, t)[0])
        except Exception:
            _MEMO_SESION[clave] = None
    return _MEMO_SESION[clave]


def marcar_sesion(df: pd.DataFrame) -> pd.DataFrame:
    """Añade `sesion_recomputada` y `sesion_calza`. Sin efectos: es el
    insumo tanto de la regla como de su auditoría."""
    out = df.copy()
    if out.empty:
        out["sesion_recomputada"] = pd.Series(dtype=object)
        out["sesion_calza"] = pd.Series(dtype=bool)
        return out
    out["sesion_recomputada"] = [
        sesion_correcta(e, a)
        for e, a in zip(out["exchange"], out["available_at"])]
    out["sesion_calza"] = (out["sesion_recomputada"].notna() &
                           (out["sesion_recomputada"].astype(object)
                            == out["sesion_objetivo"].astype(object)))
    return out


def deduplicar_por_sesion(df: pd.DataFrame) -> pd.DataFrame:
    """LA REGLA FIRMADA. Dentro de cada grupo `(ticker, sesion_objetivo)`
    con más de una fila, conserva la(s) que calza(n) con
    `sesion_correcta(exchange, available_at)`.

    Tres casos, y los tres son deliberados:
      · exactamente una calza  → se conserva ésa (grupo del defecto).
      · calzan las dos         → se conservan las dos: no hay problema de
        deduplicación que resolver, y el par va a la cola como ítem de
        calendario y universo (grupo de feriados reales).
      · no calza ninguna       → se conservan todas. La regla no inventa
        un criterio donde no lo tiene; callarse es más barato que elegir
        por frescura, que está PROHIBIDO.

    Las filas SIN pareja no se tocan nunca, calcen o no: esto deduplica,
    no filtra por coherencia."""
    if df.empty:
        return df
    m = marcar_sesion(df)
    dup = m.duplicated(["ticker", "sesion_objetivo"], keep=False)
    if not dup.any():
        return df
    piezas = [m[~dup]]
    for _, g in m[dup].groupby(["ticker", "sesion_objetivo"], sort=False):
        ok = g[g["sesion_calza"]]
        piezas.append(ok if 0 < len(ok) < len(g) else g)
    fuera = pd.concat(piezas).sort_values(["fecha", "ticker"])
    return fuera.drop(columns=["sesion_recomputada", "sesion_calza"])


def filtrar_sesion_coherente(df: pd.DataFrame) -> pd.DataFrame:
    """NO ES LA REGLA FIRMADA y no se aplica en ningún camino por defecto.

    Es el criterio de COHERENCIA: retira TODA fila cuya `sesion_objetivo`
    no calce con su `available_at`, tenga pareja o no. Existe sólo para
    poder poner su cifra al lado de la de la regla, que es lo que la cola
    de decisiones necesita para que la pregunta de las 15 filas sin pareja
    se decida con los dos números a la vista.

    La diferencia con la regla firmada es de naturaleza, no de grado: la
    regla ARBITRA entre dos filas que compiten y siempre deja una; esto
    DESCARTA sin reemplazo. Nicolás firmó lo primero."""
    if df.empty:
        return df
    m = marcar_sesion(df)
    return (m[m["sesion_calza"]]
            .drop(columns=["sesion_recomputada", "sesion_calza"]))


def auditar_dedup(df: pd.DataFrame) -> dict:
    """Lo que la regla hace Y lo que deliberadamente NO hace, en enteros.

    El segundo conteo es el que importa declarar: hay filas cuya
    `sesion_objetivo` tampoco calza con su `available_at` y que la regla
    NO retira porque no tienen pareja. Retirarlas sería otra decisión —
    un criterio de coherencia, no de deduplicación— y no está firmada."""
    if df.empty:
        return {}
    m = marcar_sesion(df)
    dup = m.duplicated(["ticker", "sesion_objetivo"], keep=False)
    grupos = m[dup].groupby(["ticker", "sesion_objetivo"], sort=False)
    resueltos, sin_criterio, ambiguos = [], [], []
    for clave, g in grupos:
        k = int(g["sesion_calza"].sum())
        (resueltos if k == 1 else ambiguos if k > 1
         else sin_criterio).append(clave)
    return {
        "filas": len(m),
        "pares": grupos.ngroups,
        "pares_resueltos": len(resueltos),
        "pares_las_dos_calzan": len(ambiguos),
        "pares_sin_criterio": len(sin_criterio),
        "filas_retiradas": len(df) - len(deduplicar_por_sesion(df)),
        "sesiones_resueltas": sorted({s for _, s in resueltos}),
        "sesiones_intactas": sorted({s for _, s in ambiguos}),
        # Lo que la regla NO toca, y hay que decirlo:
        "filas_sin_pareja_que_no_calzan": int((~dup & ~m["sesion_calza"]).sum()),
        "fechas_sin_pareja_que_no_calzan": sorted(
            m.loc[~dup & ~m["sesion_calza"], "fecha"].unique().tolist()),
        "filas_que_no_calzan_total": int((~m["sesion_calza"]).sum()),
    }


# ------------------------------------------------------------
# La regla de conocibilidad, firmada — ver la cabecera
# ------------------------------------------------------------
def _instante_utc(texto) -> datetime | None:
    """Un instante sellado (ISO 8601) como datetime con zona. Sin zona se
    lee como UTC, igual que hace el verificador con `timestamp_utc`."""
    if texto is None or pd.isna(texto) or not str(texto):
        return None
    t = datetime.fromisoformat(str(texto))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def sin_conocibilidad(timestamp_utc, available_at) -> bool:
    """LA REGLA FIRMADA (acta §90.1 d): True si la fila declara su insumo
    conocible DESPUÉS de haber sido emitida. Orden estricto; un instante
    ausente no dispara (no hay nada que comparar, y callarse es más barato
    que inventar un criterio)."""
    emitida, conocible = _instante_utc(timestamp_utc), _instante_utc(available_at)
    if emitida is None or conocible is None:
        return False
    return conocible > emitida


def excluir_sin_conocibilidad(df: pd.DataFrame) -> pd.DataFrame:
    """Retira las filas que la regla alcanza. Necesita las columnas
    `timestamp_utc` y `available_at`. Sin efectos sobre la base."""
    if df.empty:
        return df
    fuera = [sin_conocibilidad(t, a)
             for t, a in zip(df["timestamp_utc"], df["available_at"])]
    if not any(fuera):
        return df
    return df[[not f for f in fuera]].reset_index(drop=True)


def filas_sin_conocibilidad() -> pd.DataFrame:
    """Las filas de `senales_ticker` que la regla alcanza, TODAS: con
    predicción o sin ella, verificadas o no. `con_verificacion` dice cuáles
    tienen fila en `verificacion_apertura`, que son las que `cargar()`
    dejaría entrar a las métricas si la regla no existiera."""
    columnas = ["fecha", "ticker", "timestamp_utc", "available_at", "estado",
                "con_verificacion"]
    if not os.path.exists(RUTA_SENALES):
        return pd.DataFrame(columns=columnas).astype({"con_verificacion": bool})
    conn = _conexion_ro(RUTA_SENALES)
    try:
        df = pd.read_sql_query("""
            SELECT s.fecha, s.ticker, s.timestamp_utc, s.available_at,
                   s.estado, v.id IS NOT NULL AS con_verificacion
            FROM senales_ticker s
            LEFT JOIN verificacion_apertura v
                   ON v.fecha_senal = s.fecha AND v.ticker = s.ticker
            WHERE s.timestamp_utc IS NOT NULL AND s.available_at IS NOT NULL
            ORDER BY s.fecha, s.ticker
        """, conn)
    finally:
        conn.close()
    df["con_verificacion"] = df["con_verificacion"].astype(bool)
    alcanzadas = [sin_conocibilidad(t, a)
                  for t, a in zip(df["timestamp_utc"], df["available_at"])]
    return df[alcanzadas].reset_index(drop=True)[columnas]


def auditar_conocibilidad() -> dict:
    """Lo que la regla retira, en enteros, para que el informe lo declare.
    Las fechas salen de los datos: el código no nombra ninguna."""
    alcanzadas = filas_sin_conocibilidad()
    return {
        "filas_alcanzadas": len(alcanzadas),
        "con_verificacion_apertura": int(alcanzadas["con_verificacion"].sum()),
        "fechas": sorted(alcanzadas["fecha"].unique().tolist()),
    }


# ------------------------------------------------------------
# Carga — solo lectura
# ------------------------------------------------------------
def cargar(modelo_version: str = MODELO_VERSION,
           hasta_sello: str | None = None,
           dedup: bool = DEDUP_OFICIAL,
           conocibilidad: bool = CONOCIBILIDAD_OFICIAL) -> pd.DataFrame:
    """Une verificacion_apertura con senales_ticker por (fecha, ticker) y
    con snapshots por fecha. Solo 4.6.0, nunca legacy, solo con gap.

    `hasta_sello`: fecha UTC (YYYY-MM-DD) de corte sobre `verificado_en`.
    Sin ella se lee el track record VIVO, que es lo correcto para la
    plataforma. Con `CORTE_SECCION_2` se recupera el conjunto exacto de
    filas sobre el que se midió la §2 — ver el comentario de esa constante.

    `dedup`: aplica la regla firmada (ver cabecera). Va en `True` por
    defecto. `dedup=False` es la RAMA HISTÓRICA y sólo se justifica para
    reproducir una afirmación congelada ANTES de la firma; quien la pase
    tiene que decir cuál.

    `conocibilidad`: aplica la regla de conocibilidad (acta §90.1 d, ver
    cabecera) ANTES de deduplicar. Va en `True` por defecto. No alcanza a
    ninguna fila de las ventanas congeladas, así que reproducirlas no
    exige apagarla.
    """
    if not os.path.exists(RUTA_SENALES):
        return pd.DataFrame()
    conn = _conexion_ro(RUTA_SENALES)
    filtro = "AND substr(v.verificado_en, 1, 10) <= ?" if hasta_sello else ""
    params = ([modelo_version, hasta_sello] if hasta_sello
              else [modelo_version])
    try:
        df = pd.read_sql_query(f"""
            SELECT v.fecha_senal AS fecha, v.ticker,
                   v.apertura_estimada_pct, v.gap_pct, v.acierto_gap,
                   v.error_gap_pp, v.retorno_real_pct,
                   s.confianza_r2, s.intervalo80_pp, s.n_muestra, s.beta,
                   s.exchange, s.sesion_objetivo, s.available_at,
                   snap.regimen, snap.sox_usado_pct, snap.sox_fecha,
                   s.timestamp_utc
            FROM verificacion_apertura v
            LEFT JOIN senales_ticker s
                   ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
            LEFT JOIN snapshots snap ON snap.fecha = v.fecha_senal
            WHERE v.legacy = 0 AND v.modelo_version = ?
              AND v.gap_pct IS NOT NULL {filtro}
            ORDER BY v.fecha_senal, v.ticker
        """, conn, params=params)
    finally:
        conn.close()
    if conocibilidad:
        df = excluir_sin_conocibilidad(df)
    # `timestamp_utc` se lee sólo para aplicar la regla: el frame que sale
    # tiene las mismas columnas que antes de ella.
    df = df.drop(columns=["timestamp_utc"])
    return deduplicar_por_sesion(df) if dedup else df


def aplicar_convencion(df: pd.DataFrame, convencion: str) -> pd.DataFrame:
    """Añade `base_acierto` (la baseline 'siempre al alza') según la
    convención de empate elegida, y descarta filas si corresponde."""
    if convencion not in CONVENCIONES:
        raise ValueError(f"convención desconocida: {convencion}")
    out = df.copy()
    if convencion == "excluir_cero":
        out = out[out["gap_pct"] != 0].copy()
        out["base_acierto"] = (out["gap_pct"] > 0).astype(int)
    elif convencion == "estricta":
        out["base_acierto"] = (out["gap_pct"] > 0).astype(int)
    else:
        out["base_acierto"] = (out["gap_pct"] >= 0).astype(int)
    out["acierto_gap"] = out["acierto_gap"].astype(int)
    return out


# ------------------------------------------------------------
# LAS CIFRAS VIVAS PUBLICADAS: la fuente única del reporte de Telegram, la
# API y el dashboard (actas §93.4, §93.4-bis ii y §99.6; corrida 16-3,
# 11-oct-2026)
# ------------------------------------------------------------
# Hasta la corrida 16-3, las cifras de acierto que ve el público salían de
# seis consultas directas de `senales.py` (`metricas_apertura`,
# `calibracion_intervalos`, `evolucion_aciertos_apertura`,
# `ultimas_predicciones_apertura`, `verificaciones_detalle` y
# `analisis_puntaje_ia`) que NO pasaban por la regla de conocibilidad de
# arriba: al 29-sep-2026, 8 de las 160 filas de la ventana de 30 días eran
# las invertidas del evento de la corrida 14 (acta §89), y el reporte, la
# API y el dashboard las contaban
# (dictamen_15/auditor_bloque1.md, B1; tarjeta §73). Nicolás firmó UNA sola
# fuente (§93.4, opción b): estas funciones. Llevan los MISMOS nombres que
# las de `senales.py` para que la migración de cada consumidor sea un token
# y la comparación con la función vieja, un test.
#
# LO QUE CAMBIA Y LO QUE NO, dicho antes de que alguien lo lea mal:
#   · La ÚNICA diferencia con las consultas de `senales.py` son las filas que
#     `excluir_sin_conocibilidad` retira (encargo 16-3, §1): misma ventana
#     (el `date('now', '-N days')` de SQLite, día UTC), mismo denominador,
#     mismo redondeo, mismas columnas con los mismos nombres y el mismo orden
#     de filas: el del índice único (fecha_senal, ticker) con el que SQLite
#     sirve las consultas viejas, que es lo que hace que las sumas en coma
#     flotante y los tercios del puntaje (513 empates al 11-oct) den lo
#     mismo. tests/test_fuente_unica_16_3.py lo fija contra las funciones
#     viejas, cifra por cifra.
#   · La DEDUPLICACIÓN firmada (`deduplicar_por_sesion`) NO se aplica acá.
#     La firma de §93.4 nombra sólo la conocibilidad, y deduplicar movería el
#     n de las cifras de toda la historia (calibración, evolución, últimas,
#     detalle) por otra razón que la conocibilidad, lo que el encargo 16-3
#     prohíbe. Queda MEDIDO y puesto a firma (espera_firma.md, tarjeta §82).
#     Hasta esa firma las cifras vivas y la ventana sellada del README siguen
#     difiriendo en eso, como difieren desde el 1-sep-2026.
#   · `cargar()` de arriba sigue siendo la carga del ÁRBITRO (dedup por
#     defecto); `cargar_vivas()` es la carga de lo PUBLICADO EN VIVO. Las dos
#     pasan por la misma `excluir_sin_conocibilidad`.
#   · Solo lectura, como todo el módulo (`mode=ro`). Las seis consultas de
#     `senales.py` abrían la base en escritura y corrían `init_db()` (DDL) en
#     cada llamada; éstas no, y sin base devuelven «datos insuficientes» con
#     n = 0 sin crear nada.
#   · `analisis_puntaje_ia` (§99.6): la exclusión es hoy no-operativa sobre la
#     base real, porque la guarda de la 16a en `verificar_puntaje_pendientes`
#     ya no deja entrar filas invertidas a `verificacion_puntaje` (0 adentro
#     al 11-oct). Acá vive igual, para que la cifra publicada no dependa de
#     lo que un escritor dejó pasar.
#   · Las seis funciones de `senales.py` quedan sin consumidor publicado y NO
#     se borran en la 16-3 (tarjeta §82); un test fija que ningún consumidor
#     publicado las llame. `senales` no se importa acá: la capa de medición no
#     cuelga del módulo que escribe la base, y el mínimo se ata con un test.
MINIMO_OBSERVACIONES = 5   # == senales.MINIMO_OBSERVACIONES: debajo, «datos insuficientes»

_COLUMNAS_VIVAS = ["id", "fecha_senal", "ticker", "apertura_estimada_pct", "gap_pct", "retorno_real_pct",
                   "acierto_gap", "acierto_direccion", "error_gap_pp", "error_pp", "verificado_en",
                   "exchange", "sesion_objetivo", "intervalo80_pp", "estimado_sellado",
                   "timestamp_utc", "available_at", "regimen"]
_COLUMNAS_EVOLUCION = ["Fecha", "% Aciertos gap", "% Aciertos sesión", "N"]
_COLUMNAS_ULTIMAS = {"fecha_senal": "Fecha", "ticker": "Ticker", "apertura_estimada_pct": "Estimado %",
                     "gap_pct": "Gap real %", "retorno_real_pct": "Sesión real %", "acierto_gap": "Acierto gap",
                     "acierto_direccion": "Acierto sesión", "sesion_objetivo": "Sesión objetivo",
                     "timestamp_utc": "Emitida (UTC)"}
_COLUMNAS_DETALLE = ["fecha_senal", "ticker", "acierto_gap", "acierto_direccion", "error_gap_pp", "gap_pct",
                     "apertura_estimada_pct", "exchange", "intervalo80_pp", "regimen"]
_COLUMNAS_PUNTAJE = ["puntaje", "retorno", "fecha_senal", "ticker", "timestamp_utc", "available_at"]


def cargar_vivas(modelo_version: str = MODELO_VERSION, dias: int | None = None,
                 solo_con_gap: bool = True) -> pd.DataFrame:
    """Las verificaciones de apertura TAL COMO las consultan las cifras vivas
    (verificacion_apertura con senales_ticker y snapshots, nunca legacy, una
    sola modelo_version), menos las filas que la regla de conocibilidad
    retira.

    `dias`: ventana `fecha_senal >= date('now', '-dias days')`, la misma
    expresión de SQLite (día UTC) que usa `senales.metricas_apertura`; None
    es toda la historia. `solo_con_gap`: `gap_pct IS NOT NULL`, que exigen
    todas las consultas viejas menos `ultimas_predicciones_apertura`.

    Devuelve las columnas que las seis cifras necesitan (`estimado_sellado`
    es `senales_ticker.apertura_estimada_pct`, el que usa la calibración),
    ordenadas por (fecha_senal, ticker): el orden del índice único en que
    SQLite sirve las consultas viejas."""
    if not os.path.exists(RUTA_SENALES):
        return pd.DataFrame(columns=_COLUMNAS_VIVAS)
    filtros, params = [], [modelo_version]
    if solo_con_gap:
        filtros.append("AND v.gap_pct IS NOT NULL")
    if dias is not None:
        filtros.append("AND v.fecha_senal >= date('now', ?)")
        params.append(f"-{int(dias)} days")
    conn = _conexion_ro(RUTA_SENALES)
    try:
        df = pd.read_sql_query(f"""
            SELECT v.id, v.fecha_senal, v.ticker, v.apertura_estimada_pct, v.gap_pct,
                   v.retorno_real_pct, v.acierto_gap, v.acierto_direccion,
                   v.error_gap_pp, v.error_pp, v.verificado_en,
                   s.exchange, s.sesion_objetivo, s.intervalo80_pp,
                   s.apertura_estimada_pct AS estimado_sellado,
                   s.timestamp_utc, s.available_at, snap.regimen
            FROM verificacion_apertura v
            LEFT JOIN senales_ticker s
                   ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
            LEFT JOIN snapshots snap ON snap.fecha = v.fecha_senal
            WHERE v.legacy = 0 AND v.modelo_version = ? {' '.join(filtros)}
            ORDER BY v.fecha_senal, v.ticker
        """, conn, params=params)
    finally:
        conn.close()
    return excluir_sin_conocibilidad(df)


def metricas_apertura(dias: int = 30, modelo_version: str = MODELO_VERSION) -> dict:
    """Métricas del DOBLE objetivo (gap y retorno de sesión) sobre la
    ventana de `dias`: lo que publican el reporte de Telegram, la portada de
    la API y el dashboard. Mismo cálculo que `senales.metricas_apertura`
    (sumas en el orden de la consulta, redondeo a 1 y 2 decimales), menos
    las filas que la regla de conocibilidad retira."""
    df = cargar_vivas(modelo_version, dias=dias)
    n = len(df)
    if n < MINIMO_OBSERVACIONES:
        return {"suficiente": False, "n": n}
    return {
        "suficiente": True, "n": n,
        "gap": {
            "pct_aciertos": round(100 * sum(df["acierto_gap"].tolist()) / n, 1),
            "mae_pp": round(sum(df["error_gap_pp"].tolist()) / n, 2),
        },
        "retorno_sesion": {
            "pct_aciertos": round(100 * sum(df["acierto_direccion"].tolist()) / n, 1),
            "mae_pp": round(sum(df["error_pp"].tolist()) / n, 2),
        },
    }


def calibracion_intervalos(modelo_version: str = MODELO_VERSION) -> dict:
    """Cobertura empírica del intervalo del 80% sobre toda la historia: qué
    fracción de los gaps reales cayó dentro de estimación ± intervalo80. Sólo
    filas con intervalo sellado (el JOIN interno de la consulta vieja);
    debajo del mínimo, «pendiente»."""
    df = cargar_vivas(modelo_version)
    d = df[df["intervalo80_pp"].notna()]
    n = len(d)
    if n < MINIMO_OBSERVACIONES:
        return {"suficiente": False, "n": n}
    dentro = sum(1 for gap, est, int80 in zip(d["gap_pct"].tolist(), d["estimado_sellado"].tolist(),
                                              d["intervalo80_pp"].tolist())
                 if abs(gap - est) <= int80)
    return {"suficiente": True, "n": n, "cobertura_pct": round(100 * dentro / n, 1)}


def evolucion_aciertos_apertura(modelo_version: str = MODELO_VERSION) -> pd.DataFrame:
    """% de aciertos (gap y sesión) y N por fecha de señal, en orden de fecha.
    Mismas columnas que la consulta vieja (`Fecha`, `% Aciertos gap`,
    `% Aciertos sesión`, `N`): el gráfico del dashboard y de /historial las
    nombra así."""
    df = cargar_vivas(modelo_version)
    if df.empty:
        return pd.DataFrame(columns=_COLUMNAS_EVOLUCION)
    g = df.groupby("fecha_senal", sort=True)
    agg = g.agg(gap=("acierto_gap", "mean"), sesion=("acierto_direccion", "mean"), n=("acierto_gap", "size"))
    return pd.DataFrame({
        "Fecha": agg.index.tolist(),
        "% Aciertos gap": (agg["gap"] * 100).tolist(),
        "% Aciertos sesión": (agg["sesion"] * 100).tolist(),
        "N": agg["n"].tolist(),
    })


def ultimas_predicciones_apertura(limite: int = 50,
                                  modelo_version: str = MODELO_VERSION) -> pd.DataFrame:
    """Las últimas `limite` verificaciones (con o sin gap, como la consulta
    vieja), de la más reciente a la más antigua, con su sesión objetivo y su
    instante de emisión. El orden dentro de una misma fecha es el del índice
    único recorrido al revés (ticker descendente), el que la consulta vieja
    daba sin declararlo."""
    df = cargar_vivas(modelo_version, solo_con_gap=False)
    df = df.sort_values(["fecha_senal", "ticker"], ascending=[False, False], kind="stable").head(limite)
    return df[list(_COLUMNAS_ULTIMAS)].rename(columns=_COLUMNAS_ULTIMAS).reset_index(drop=True)


def verificaciones_detalle(modelo_version: str = MODELO_VERSION) -> pd.DataFrame:
    """Cada verificación limpia con su contexto de emisión (exchange,
    intervalo sellado, régimen sellado del snapshot del día), para los
    desgloses por región y por régimen de /historial. La agrupación y los
    Wilson son presentación (capa API)."""
    return cargar_vivas(modelo_version)[_COLUMNAS_DETALLE].reset_index(drop=True)


def cargar_puntaje_vivo(modelo_version: str = MODELO_VERSION, dias: int | None = 90) -> pd.DataFrame:
    """`verificacion_puntaje` con `senales_ticker`, como lo consulta
    `senales.analisis_puntaje_ia` (sólo filas con timestamp_utc, una sola
    modelo_version, ventana de `dias` sobre fecha_senal), menos las filas que
    la regla de conocibilidad retira (acta §99.6). Orden (fecha_senal,
    ticker): el de la consulta vieja, del que dependen los tercios cuando
    hay empates de puntaje."""
    if not os.path.exists(RUTA_SENALES):
        return pd.DataFrame(columns=_COLUMNAS_PUNTAJE)
    filtro = "AND v.fecha_senal >= date('now', ?)" if dias is not None else ""
    params = [f"-{int(dias)} days", modelo_version] if dias is not None else [modelo_version]
    conn = _conexion_ro(RUTA_SENALES)
    try:
        df = pd.read_sql_query(f"""
            SELECT v.puntaje_ia AS puntaje, v.retorno_5d_pct AS retorno,
                   v.fecha_senal, v.ticker, s.timestamp_utc, s.available_at
            FROM verificacion_puntaje v
            JOIN senales_ticker s
              ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
            WHERE 1 = 1 {filtro}
              AND s.timestamp_utc IS NOT NULL AND s.modelo_version = ?
            ORDER BY v.fecha_senal, v.ticker
        """, conn, params=params)
    finally:
        conn.close()
    return excluir_sin_conocibilidad(df)


def analisis_puntaje_ia(dias: int = 90, modelo_version: str = MODELO_VERSION) -> dict:
    """¿El Puntaje IA anticipa el retorno a 5 días? Tercio alto contra tercio
    bajo y correlación, sobre la ventana de `dias`. Mismo cálculo que
    `senales.analisis_puntaje_ia`; `datos` trae las dos columnas (puntaje,
    retorno) para el gráfico del dashboard."""
    df = cargar_puntaje_vivo(modelo_version, dias)[["puntaje", "retorno"]]
    n = len(df)
    if n < MINIMO_OBSERVACIONES:
        return {"suficiente": False, "n": n, "datos": df}
    df = df.sort_values("puntaje")
    corte = max(1, n // 3)
    correlacion = df["puntaje"].corr(df["retorno"]) if n >= 3 else None
    return {
        "suficiente": True, "n": n, "datos": df,
        "retorno_tercio_alto": round(df.iloc[-corte:]["retorno"].mean(), 2),
        "retorno_tercio_bajo": round(df.iloc[:corte]["retorno"].mean(), 2),
        "correlacion": round(correlacion, 2) if correlacion is not None else None,
    }


# ------------------------------------------------------------
# Bloques de la §2
# ------------------------------------------------------------
def duelo_excluyendo(df: pd.DataFrame, desde: str, hasta: str) -> dict:
    """El duelo SIN una ventana de fechas. Operacionaliza R2 de la §6.2
    ("su ventaja desaparece al excluir el bloque 1, 15-23 jul") por RANGO
    DE FECHAS y no por índice de bloque: los bloques dependen del orden de
    las filas dentro de cada fecha, el rango de fechas no."""
    fuera = df[(df["fecha"] < desde) | (df["fecha"] > hasta)]
    return duelo(fuera)


def duelo(df: pd.DataFrame) -> dict:
    """Campeón vs baseline sobre las MISMAS filas (§2.1)."""
    n = len(df)
    if n == 0:
        return {"n": 0}
    mod, base = df["acierto_gap"], df["base_acierto"]
    b01 = int(((mod == 1) & (base == 0)).sum())
    b10 = int(((mod == 0) & (base == 1)).sum())
    return {
        "n": n,
        "modelo_aciertos": int(mod.sum()),
        "modelo_pct": round(100 * mod.mean(), 1),
        "modelo_wilson": _wilson(mod.sum(), n),
        "base_aciertos": int(base.sum()),
        "base_pct": round(100 * base.mean(), 1),
        "base_wilson": _wilson(base.sum(), n),
        "ventaja_pp": round(100 * (mod.mean() - base.mean()), 1),
        "mcnemar_b01": b01, "mcnemar_b10": b10,
        "mcnemar_p": round(mcnemar(b01, b10), 4),
    }


def magnitud(df: pd.DataFrame) -> dict:
    """MAE del campeón contra los dos predictores triviales (§2.5). La
    baseline direccional ni siquiera produce una magnitud comparable."""
    if df.empty:
        return {}
    media = df["gap_pct"].mean()
    return {
        "mae_modelo": round(df["error_gap_pp"].mean(), 4),
        "mae_cero": round(df["gap_pct"].abs().mean(), 4),
        "mae_media": round((df["gap_pct"] - media).abs().mean(), 4),
        "media_gap": round(media, 4),
    }


def calibracion(df: pd.DataFrame) -> dict:
    """Cobertura empírica del intervalo 80% y cuánto sobra de ancho (§2.7)."""
    d = df.dropna(subset=["intervalo80_pp"])
    if d.empty:
        return {}
    dentro = (d["gap_pct"] - d["apertura_estimada_pct"]).abs() <= d["intervalo80_pp"]
    ancho = d["intervalo80_pp"].mean()
    err = d["error_gap_pp"].mean()
    return {
        "n": len(d),
        "cobertura_pct": round(100 * dentro.mean(), 1),
        "nominal_pct": round(100 * NOMINAL_INTERVALO, 1),
        "ancho_medio_pp": round(ancho, 2),
        "error_medio_pp": round(err, 2),
        "ratio_ancho_error": round(ancho / err, 2) if err else None,
    }


def zona_muerta(df: pd.DataFrame, umbrales=UMBRALES_ZONA_MUERTA) -> pd.DataFrame:
    """Abstenerse bajo un umbral de |predicción|, cada nivel contra SU
    PROPIA baseline sobre las filas que sobreviven (§2.4). Comparar contra
    la baseline global sería hacer trampa: cambia el denominador."""
    total = len(df)
    filas = []
    for u in umbrales:
        sub = df[df["apertura_estimada_pct"].abs() >= u]
        d = duelo(sub)
        if not d.get("n"):
            continue
        filas.append({
            "umbral": u, "n": d["n"], "modelo_pct": d["modelo_pct"],
            "base_pct": d["base_pct"], "ventaja_pp": d["ventaja_pp"],
            "mcnemar_p": d["mcnemar_p"],
            "descartado_pct": round(100 * (1 - d["n"] / total), 0) if total else 0,
        })
    return pd.DataFrame(filas)


def por_exchange(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for ex, sub in df.groupby("exchange", dropna=False):
        d = duelo(sub)
        filas.append({
            "exchange": ex, "n": d["n"], "modelo_pct": d["modelo_pct"],
            "base_pct": d["base_pct"], "ventaja_pp": d["ventaja_pp"],
            "r2_medio": round(sub["confianza_r2"].mean(), 3)
            if sub["confianza_r2"].notna().any() else None,
            "mae": round(sub["error_gap_pp"].mean(), 2),
        })
    return pd.DataFrame(filas).sort_values("n", ascending=False).reset_index(drop=True)


def por_bloques(df: pd.DataFrame, tam: int = TAM_BLOQUE) -> pd.DataFrame:
    """Bloques temporales de `tam` filas en orden de emisión (§2.2).

    ORDEN: `cargar()` ordena por (fecha, ticker) — determinista y sin
    depender del rowid. Importa decirlo: en las fechas que caen sobre una
    frontera de bloque, el orden interno decide qué filas van a cada lado,
    así que los porcentajes POR BLOQUE dependen del orden elegido. Los
    límites (fechas y n) no dependen de él; los porcentajes sí.
    """
    filas = []
    for i in range(0, len(df), tam):
        sub = df.iloc[i:i + tam]
        d = duelo(sub)
        filas.append({
            "bloque": i // tam, "desde": sub["fecha"].iloc[0],
            "hasta": sub["fecha"].iloc[-1], "n": d["n"],
            "modelo_pct": d["modelo_pct"], "base_pct": d["base_pct"],
            "ventaja_pp": d["ventaja_pp"],
        })
    return pd.DataFrame(filas)


def salud_r2_regimen_beta(df: pd.DataFrame,
                          modelo_version: str = MODELO_VERSION,
                          hasta_sello: str | None = None) -> dict:
    """Las tres afirmaciones sueltas de la §2.6/§2.7: R² medio, cuántas
    etiquetas de régimen distintas hay, y cuánto salta β entre días."""
    out = {"r2_medio": round(df["confianza_r2"].mean(), 4)
           if df["confianza_r2"].notna().any() else None}

    conn = _conexion_ro(RUTA_SENALES)
    try:
        snaps_todos = pd.read_sql_query(
            "SELECT fecha, regimen, modelo_version FROM snapshots ORDER BY fecha", conn)
        snaps = snaps_todos[snaps_todos["modelo_version"] == modelo_version]
        betas = pd.read_sql_query(
            "SELECT fecha, ticker, beta, timestamp_utc, available_at"
            " FROM senales_ticker"
            " WHERE beta IS NOT NULL AND modelo_version = ?"
            " ORDER BY ticker, fecha", conn, params=(modelo_version,))
    finally:
        conn.close()

    # La regla de conocibilidad (acta §90.1 d) rige también acá: la beta de
    # una fila emitida con la sesión abierta salió de la misma barra.
    if CONOCIBILIDAD_OFICIAL:
        betas = excluir_sin_conocibilidad(betas)

    # El mismo instante «a la fecha» que `cargar`: sin él, el conteo de
    # snapshots y el salto de β se miden sobre una base que sigue creciendo
    # mientras la cifra del documento está congelada.
    if hasta_sello:
        snaps_todos = snaps_todos[snaps_todos["fecha"] <= hasta_sello]
        snaps = snaps[snaps["fecha"] <= hasta_sello]
        betas = betas[betas["fecha"] <= hasta_sello]

    # El documento dice "35 snapshots"; con el filtro de modelo son 34. La
    # fila de 2026-07-04 es pre-versionado (modelo_version NULL). Se reportan
    # los dos conteos porque la afirmación de fondo —UNA etiqueta— vale igual.
    out["snapshots_4_6_0"] = len(snaps)
    out["snapshots_totales"] = len(snaps_todos)
    out["regimenes_distintos"] = int(snaps_todos["regimen"].nunique())
    out["regimenes"] = sorted(snaps_todos["regimen"].dropna().unique().tolist())

    saltos = betas.groupby("ticker")["beta"].diff().abs().dropna()
    if len(saltos):
        out.update({
            "beta_nivel_medio": round(betas["beta"].abs().mean(), 4),
            "beta_salto_medio": round(saltos.mean(), 4),
            "beta_salto_mediana": round(saltos.median(), 4),
            "beta_salto_max": round(saltos.max(), 4),
            "beta_saltos_sobre_010_pct": round(100 * (saltos > 0.10).mean(), 1),
            "beta_pares": len(saltos),
        })
        if out["beta_nivel_medio"]:
            out["beta_salto_pct_del_nivel"] = round(
                100 * out["beta_salto_medio"] / out["beta_nivel_medio"], 1)
    return out


# ------------------------------------------------------------
# Contraste con el pre-registro — confirmar o DESMENTIR
# ------------------------------------------------------------
# El pre-registro se congela; el harness manda. Si una cifra no reproduce,
# ESO es el hallazgo y se reporta aquí — jamás se edita GEMELO/DISEÑO.md
# para que cuadre (§9 del documento, DECISIONES.md §23).
#
# Cada entrada: (etiqueta, valor afirmado, tolerancia, extractor).
AFIRMACIONES = (
    ("n (verificaciones 4.6.0)",        228,    0,      lambda R: R["duelo"]["n"]),
    ("modelo: aciertos",                150,    0,      lambda R: R["duelo"]["modelo_aciertos"]),
    ("modelo: acierto de gap %",         65.8,  0.05,   lambda R: R["duelo"]["modelo_pct"]),
    ("baseline: aciertos",              138,    0,      lambda R: R["duelo"]["base_aciertos"]),
    ("baseline: acierto de gap %",        60.5,  0.05,  lambda R: R["duelo"]["base_pct"]),
    ("ventaja pp",                        5.3,  0.05,   lambda R: R["duelo"]["ventaja_pp"]),
    ("McNemar b01",                      67,    0,      lambda R: R["duelo"]["mcnemar_b01"]),
    ("McNemar b10",                      55,    0,      lambda R: R["duelo"]["mcnemar_b10"]),
    ("McNemar p",                         0.3193, 0.0005, lambda R: R["duelo"]["mcnemar_p"]),
    ("MAE modelo",                        3.064, 0.001, lambda R: R["magnitud"]["mae_modelo"]),
    ("MAE predecir 0.0",                  3.423, 0.001, lambda R: R["magnitud"]["mae_cero"]),
    ("MAE predecir la media",             3.395, 0.001, lambda R: R["magnitud"]["mae_media"]),
    ("cobertura del intervalo 80%",      89.5,  0.05,   lambda R: R["calibracion"]["cobertura_pct"]),
    ("ratio ancho/error",                 1.77, 0.005,  lambda R: R["calibracion"]["ratio_ancho_error"]),
    ("R² sellado medio",                  0.1635, 0.0001, lambda R: R["salud"]["r2_medio"]),
    ("zona muerta 0.25: n",             184,    0,      lambda R: R["zm25"]["n"]),
    ("zona muerta 0.25: ventaja pp",      8.2,  0.05,   lambda R: R["zm25"]["ventaja_pp"]),
    ("etiquetas de régimen distintas",    1,    0,      lambda R: R["salud"]["regimenes_distintos"]),
    ("snapshots sellados",               35,    0,      lambda R: R["salud"]["snapshots_totales"]),
    ("|Δβ| medio",                        0.043, 0.001, lambda R: R["salud"]["beta_salto_medio"]),
    ("|Δβ| como % del nivel",             8.0,  0.3,    lambda R: R["salud"]["beta_salto_pct_del_nivel"]),
)

# La tabla de la §2.2, bloque por bloque. Los LÍMITES (fechas y n) no
# dependen del orden de las filas; los PORCENTAJES sí, porque las fechas
# que caen sobre una frontera se reparten según ese orden.
AFIRMACIONES_BLOQUES = (
    # (bloque, desde, hasta, n, modelo %, base %)
    (0, "2026-07-05", "2026-07-15", 40, 75.0, 67.5),
    (1, "2026-07-15", "2026-07-23", 40, 82.5, 42.5),
    (2, "2026-07-24", "2026-07-30", 40, 57.5, 62.5),
    (3, "2026-07-31", "2026-08-10", 40, 67.5, 72.5),
    (4, "2026-08-10", "2026-08-18", 40, 62.5, 77.5),
    (5, "2026-08-18", "2026-08-21", 28, 42.9, 32.1),
)

# R2 de la §6.2 nombra "el bloque 1 (15-23 jul)". Como el índice de bloque
# depende del orden y el rango de fechas no, la regla se operacionaliza por
# FECHAS. Este es el rango.
VENTANA_R2 = ("2026-07-15", "2026-07-23")


def contrastar_bloques(df: pd.DataFrame) -> pd.DataFrame:
    obtenido = por_bloques(df)
    filas = []
    for b, desde, hasta, n, mod, base in AFIRMACIONES_BLOQUES:
        fila = obtenido[obtenido["bloque"] == b]
        if fila.empty:
            filas.append({"bloque": b, "campo": "(ausente)", "documento": "",
                          "harness": "", "veredicto": "SIN DATO"})
            continue
        f = fila.iloc[0]
        for campo, afirmado, real in (("límites", f"{desde}→{hasta} n={n}",
                                       f"{f['desde']}→{f['hasta']} n={f['n']}"),
                                      ("modelo %", mod, f["modelo_pct"]),
                                      ("base %", base, f["base_pct"])):
            if campo == "límites":
                ok = afirmado == real
            else:
                ok = abs(float(real) - float(afirmado)) <= 0.05
            filas.append({"bloque": b, "campo": campo, "documento": afirmado,
                          "harness": real,
                          "veredicto": "reproduce" if ok else "NO REPRODUCE"})
    return pd.DataFrame(filas)


def contrastar_linea_oficial(df: pd.DataFrame) -> pd.DataFrame:
    """Verifica la línea base CONGELADA en la §2.8 (convención oficial)."""
    d = duelo(df)
    obtenidos = {"n": d["n"], "modelo: acierto %": d["modelo_pct"],
                 "baseline: acierto %": d["base_pct"],
                 "ventaja pp": d["ventaja_pp"], "McNemar b01": d["mcnemar_b01"],
                 "McNemar b10": d["mcnemar_b10"], "McNemar p": d["mcnemar_p"]}
    filas = []
    for etiqueta, congelado, tol in LINEA_BASE_OFICIAL:
        real = obtenidos[etiqueta]
        filas.append({"campo": etiqueta, "congelado (§2.8)": congelado,
                      "harness": real,
                      "veredicto": "coincide"
                      if abs(float(real) - float(congelado)) <= tol
                      else "NO COINCIDE"})
    return pd.DataFrame(filas)


def contrastar(df: pd.DataFrame,
               hasta_sello: str | None = CORTE_SECCION_2) -> pd.DataFrame:
    """Compara cada afirmación ORIGINAL de la §2 contra lo que da el
    harness. Esas cifras se escribieron con la convención `estricta`, así
    que reproducen bajo ella — es la verificación histórica del
    pre-registro, distinta de la línea base oficial de la §2.8.

    `hasta_sello` viene pinchado en `CORTE_SECCION_2` por defecto: éstas
    son afirmaciones CONGELADAS y contrastarlas contra un track record que
    sigue creciendo compara una cifra fija con un denominador móvil. Quien
    quiera el contraste contra la base viva pasa `hasta_sello=None` y verá
    la deriva, que es información distinta y legítima."""
    zm = zona_muerta(df)
    fila25 = zm[zm["umbral"] == 0.25]
    R = {"duelo": duelo(df), "magnitud": magnitud(df),
         "calibracion": calibracion(df),
         "salud": salud_r2_regimen_beta(df, hasta_sello=hasta_sello),
         "zm25": fila25.iloc[0].to_dict() if not fila25.empty else {}}
    filas = []
    for etiqueta, afirmado, tol, extraer in AFIRMACIONES:
        try:
            obtenido = extraer(R)
        except (KeyError, IndexError):
            obtenido = None
        if obtenido is None:
            veredicto = "SIN DATO"
        else:
            veredicto = "reproduce" if abs(float(obtenido) - float(afirmado)) <= tol \
                else "NO REPRODUCE"
        filas.append({"afirmación": etiqueta, "documento": afirmado,
                      "harness": obtenido, "veredicto": veredicto})
    return pd.DataFrame(filas)


# ------------------------------------------------------------
# Informe
# ------------------------------------------------------------
def _tabla(df: pd.DataFrame) -> str:
    if df.empty:
        return "(sin filas)\n"
    cols = list(df.columns)
    L = ["| " + " | ".join(cols) + " |",
         "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, f in df.iterrows():
        L.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in f) + " |")
    return "\n".join(L) + "\n"


def componer_informe(base_df: pd.DataFrame, convencion: str) -> str:
    df = aplicar_convencion(base_df, convencion)
    d, mag = duelo(df), magnitud(df)
    cal, salud = calibracion(df), salud_r2_regimen_beta(df)
    # Las afirmaciones CONGELADAS (§2 y §2.8) son anteriores a la firma de
    # la regla de deduplicación, así que se contrastan contra su propio
    # conjunto de filas: el instante `CORTE_SECCION_2` y la rama histórica
    # `dedup=False`. Contrastarlas contra la base deduplicada compararía
    # una cifra fija con un conjunto de filas que la firma cambió — el
    # mismo error de denominador móvil que el WS5 diagnosticó, con otra
    # cara.
    historico = cargar(hasta_sello=CORTE_SECCION_2, dedup=False)
    aud = auditar_dedup(cargar(dedup=False))
    aud_con = auditar_conocibilidad()

    L = [f"# Línea base del campeón {MODELO_VERSION} — reproducción de la §2",
         "",
         f"- Generado: {datetime.now(timezone.utc).isoformat()}",
         f"- Fuente: `senales.db` en `mode=ro` (autoridad), NO los CSV de respaldo",
         f"- Convención de empate: **{convencion}**",
         f"- Regla de deduplicación: **aplicada** (firmada el 1-sep-2026)",
         f"- Regla de conocibilidad: **aplicada** (firmada el 29-sep-2026, "
         f"acta §90.1 d) — {aud_con['filas_alcanzadas']} filas alcanzadas",
         f"- Filas: **n = {d['n']}** · {df['fecha'].min()} → {df['fecha'].max()}",
         "",]
    L += ["## La regla de conocibilidad, aplicada", "",
          "Queda fuera de toda métrica la fila que declara su insumo "
          "conocible DESPUÉS de haber sido emitida: "
          "`available_at > timestamp_utc`, comparados como instantes. **El "
          "criterio es por regla, no por fecha**: no hay ninguna lista de "
          "días cableada, y las fechas de abajo salen de los datos. Se "
          "aplica ANTES de deduplicar: una fila fuera de toda métrica "
          "tampoco arbitra un par.", "",
          "| | |", "|---|---|",
          f"| Filas de `senales_ticker` alcanzadas | "
          f"**{aud_con['filas_alcanzadas']}** |",
          f"| De ellas, con fila en `verificacion_apertura` | "
          f"**{aud_con['con_verificacion_apertura']}** |",
          f"| Fechas de sello alcanzadas | "
          f"{', '.join(aud_con['fechas']) or '(ninguna)'} |", "",
          "> Las filas alcanzadas conservan su `estado` y su verificación en "
          "la base, como registro histórico: ninguna fila sellada se "
          "reescribe. **Lo que la regla NO alcanza, declarado:** la tabla "
          "`snapshots` no sella `available_at`, así que el `regimen` de un "
          "snapshot emitido con la sesión abierta sigue contando en la "
          "§2.7.", ""]
    if aud:
        L += ["## La regla de deduplicación, aplicada", "",
              "Se conserva la fila cuya `sesion_objetivo` coincide con "
              "`calendarios.proxima_sesion_despues_de(exchange, "
              "available_at)`. **El criterio es la corrección de la sesión, "
              "nunca la frescura** — `keep=\"last\"` está prohibido porque "
              "el forense mostró que retira selectivamente errores del "
              "modelo. La regla separa sola los dos grupos: no hay ninguna "
              "lista de fechas cableada.", "",
              f"| | |", "|---|---|",
              f"| Pares `(ticker, sesion_objetivo)` | {aud['pares']} |",
              f"| Pares donde UNA fila calza → se retira la otra | "
              f"**{aud['pares_resueltos']}** "
              f"({', '.join(aud['sesiones_resueltas'])}) |",
              f"| Pares donde calzan LAS DOS → no se toca nada | "
              f"**{aud['pares_las_dos_calzan']}** "
              f"({', '.join(aud['sesiones_intactas'])}) |",
              f"| Pares sin criterio (no calza ninguna) | "
              f"{aud['pares_sin_criterio']} |",
              f"| Filas retiradas | **{aud['filas_retiradas']}** |", "",
              "> **Lo que la regla NO hace, declarado.** Es una regla de "
              "DEDUPLICACIÓN: sólo actúa dentro de pares. Hay "
              f"**{aud['filas_sin_pareja_que_no_calzan']} filas SIN pareja** "
              f"({', '.join(aud['fechas_sin_pareja_que_no_calzan'])}) cuya "
              "`sesion_objetivo` tampoco calza con su `available_at`, y "
              f"quedan intactas — {aud['filas_que_no_calzan_total']} filas "
              "no calzan en total. Retirarlas sería un criterio de "
              "COHERENCIA, no de deduplicación, y no está firmado.", ""]
        crudo = cargar(dedup=False)
        alt = duelo(aplicar_convencion(
            filtrar_sesion_coherente(crudo), convencion))
        L += ["**La cifra de la rama que NO se aplicó**, para que la "
              "pregunta de esas 15 filas se decida con los dos números a "
              "la vista y no con uno: retirando además las filas sin "
              f"pareja que no calzan, bajo `{convencion}` quedaría "
              f"**n = {alt['n']}**, ventaja **{alt['ventaja_pp']:+} pp**, "
              f"McNemar {alt['mcnemar_b01']} vs {alt['mcnemar_b10']}, "
              f"**p = {alt['mcnemar_p']}**. Está computado y **no "
              "aplicado**: la decisión es de Nicolás y vive en "
              "`GEMELO/resultados/cola_decisiones.md`.", ""]
    L += [
         "## Las tres convenciones de empate, juntas",
         "",
         "Hay 5 filas con `gap_pct == 0.0` exacto (apertura idéntica al cierre",
         "previo: la firma del ffill de feriados; 4 de las 5 son 2330.TW). El",
         "verificador puntúa al campeón con `>=` y le da el acierto; la",
         "baseline original de la §2.1 usaba `>` y no se lo daba — dos reglas",
         "distintas para los dos lados. La §2.8 congeló `excluir_cero`; las",
         "tres se muestran igual, porque la elección debe quedar a la vista:",
         ""]
    comp = []
    for c in CONVENCIONES:
        dd = duelo(aplicar_convencion(base_df, c))
        comp.append({"convencion": c, "n": dd["n"],
                     "modelo_pct": dd["modelo_pct"], "base_pct": dd["base_pct"],
                     "ventaja_pp": dd["ventaja_pp"],
                     "mcnemar": f"{dd['mcnemar_b01']} vs {dd['mcnemar_b10']}",
                     "p": dd["mcnemar_p"]})
    L += [_tabla(pd.DataFrame(comp)), ""]

    # La reproducción del pre-registro se verifica SIEMPRE bajo `estricta`,
    # que es la convención con que se escribieron esas cifras — evaluarlas
    # bajo otra las haría "fallar" por comparar peras con manzanas.
    contraste = contrastar(aplicar_convencion(historico, "estricta"))
    fallan = contraste[contraste["veredicto"] != "reproduce"]
    oficial = contrastar_linea_oficial(
        aplicar_convencion(historico, CONVENCION_OFICIAL))
    of_mal = oficial[oficial["veredicto"] != "coincide"]
    cb = contrastar_bloques(df)
    cb_mal = cb[cb["veredicto"] != "reproduce"]
    r2 = duelo_excluyendo(df, *VENTANA_R2)
    L += ["## Línea base OFICIAL (§2.8, congelada)", "",
          f"Convención congelada: **`{CONVENCION_OFICIAL}`** — las filas con "
          "`gap_pct == 0.00` se excluyen de ambos lados (artefactos del ffill "
          "de feriados). La exclusión vive en esta capa de medición; "
          "`senales.py` no se toca.", "",
          f"Se contrasta contra el conjunto de filas de su propio instante "
          f"(`hasta_sello = {CORTE_SECCION_2}`) y **sin la regla de "
          "deduplicación**, que es posterior a la firma de la §2.8: una "
          "cifra congelada se reproduce sobre las filas que tenía, no "
          "sobre las que quedan hoy.", "",
          _tabla(oficial),
          ("" if of_mal.empty else
           "> **La línea oficial ya NO coincide con lo congelado.** Eso es un "
           "hallazgo, no algo que ajustar en el documento.\n"),
          "## Contraste con el pre-registro original (§2, convención `estricta`)",
          "",
          f"**{len(contraste) - len(fallan)} de {len(contraste)} afirmaciones "
          "reproducen.** Se evalúan bajo `estricta` porque es la convención "
          "con que se escribieron; la §2.8 las corrige, no las desmiente.", "",
          _tabla(contraste)]
    if not fallan.empty:
        L += ["> Las que no reproducen son **hallazgos**. El pre-registro NO se",
              "> edita para que cuadren: manda el harness y la corrección se",
              "> documenta aparte, con fecha posterior (DECISIONES.md §23).", ""]

    L += ["## §2.1 — El edge real", "",
          f"| | Acierto de gap | IC95 Wilson |", "|---|---|---|",
          f"| Modelo {MODELO_VERSION} | **{d['modelo_pct']}%** "
          f"({d['modelo_aciertos']}/{d['n']}) | "
          f"[{d['modelo_wilson'][0]} – {d['modelo_wilson'][1]}] |",
          f"| \"Siempre al alza\", mismas filas | **{d['base_pct']}%** "
          f"({d['base_aciertos']}/{d['n']}) | "
          f"[{d['base_wilson'][0]} – {d['base_wilson'][1]}] |",
          f"| **Ventaja** | **{d['ventaja_pp']:+} pp** | — |", "",
          f"McNemar sobre los desacuerdos: el modelo acierta donde la baseline",
          f"falla **{d['mcnemar_b01']}** veces; la baseline donde el modelo falla",
          f"**{d['mcnemar_b10']}**. **p = {d['mcnemar_p']}** "
          "(chi-cuadrado con corrección de continuidad).", "",
          "## §2.2 — Dónde está la ventaja, en el tiempo", "",
          _tabla(por_bloques(df)),
          "### Contraste bloque a bloque", "",
          f"{len(cb) - len(cb_mal)} de {len(cb)} celdas reproducen.", "",
          _tabla(cb),
          "### R2 de la §6.2, operacionalizado por fechas", "",
          "R2 descarta al retador si su ventaja desaparece al excluir el "
          f"bloque 1 ({VENTANA_R2[0]}–{VENTANA_R2[1]}). El ÍNDICE de bloque "
          "depende del orden de las filas; el RANGO DE FECHAS no, así que la "
          "regla solo es aplicable por fechas. Al propio campeón, esa misma "
          "prueba le da:", "",
          f"- Sin la ventana: n = {r2['n']}, modelo {r2['modelo_pct']}%, "
          f"base {r2['base_pct']}%, **ventaja {r2['ventaja_pp']:+} pp** "
          f"(McNemar p = {r2['mcnemar_p']}).", ""]
    L += [
          "## §2.4 — Zona muerta: abstenerse bajo un umbral", "",
          "Cada nivel contra **su propia** baseline sobre las filas que",
          "sobreviven — compararlo contra la baseline global cambiaría el",
          "denominador y regalaría ventaja.", "",
          _tabla(zona_muerta(df)),
          "## §2.5 — Magnitud: lo que la baseline no puede dar", "",
          f"| Predictor | MAE del gap |", "|---|---|",
          f"| Modelo {MODELO_VERSION} | **{mag['mae_modelo']} pp** |",
          f"| Predecir 0.0 | {mag['mae_cero']} pp |",
          f"| Predecir la media histórica ({mag['media_gap']}) | {mag['mae_media']} pp |",
          "",
          f"Mejora sobre predecir cero: "
          f"**{100 * (1 - mag['mae_modelo'] / mag['mae_cero']):.1f}%**.", "",
          "## §2.6 — Cortes por bolsa", "",
          _tabla(por_exchange(df)),
          "## §2.7 — Intervalos, régimen y estabilidad de β", ""]
    if cal:
        L += [f"- **Calibración:** cobertura empírica **{cal['cobertura_pct']}%** "
              f"contra un nominal de {cal['nominal_pct']}% (n={cal['n']}), ancho "
              f"medio {cal['ancho_medio_pp']} pp frente a error absoluto medio "
              f"{cal['error_medio_pp']} pp — **{cal['ratio_ancho_error']}× más "
              "anchos de lo necesario**."]
    L += [f"- **Régimen:** **{salud['regimenes_distintos']}** etiqueta(s) distinta(s) "
          f"en los {salud['snapshots_totales']} snapshots sellados "
          f"({salud['snapshots_4_6_0']} con modelo {MODELO_VERSION}; el de "
          f"2026-07-04 es pre-versionado, `modelo_version` NULL) → "
          f"{salud['regimenes']}",
          f"- **R² sellado medio:** {salud['r2_medio']}"]
    if "beta_salto_medio" in salud:
        L += [f"- **Estabilidad de β:** salto medio entre días consecutivos "
              f"{salud['beta_salto_medio']} sobre un nivel medio de "
              f"{salud['beta_nivel_medio']} — **{salud['beta_salto_pct_del_nivel']}% "
              f"del nivel, por día**. Mediana {salud['beta_salto_mediana']}; el "
              f"{salud['beta_saltos_sobre_010_pct']}% de los "
              f"{salud['beta_pares']} pares salta más de 0.10; máximo "
              f"{salud['beta_salto_max']}."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Reproduce la §2 de GEMELO/DISEÑO.md desde senales.db (mode=ro).")
    ap.add_argument("--convencion", default=CONVENCION_OFICIAL, choices=CONVENCIONES,
                    help="cómo puntúa la baseline un gap de exactamente 0")
    ap.add_argument("--sin-escribir", action="store_true")
    args = ap.parse_args(argv)

    base_df = cargar()
    if base_df.empty:
        print("No hay verificaciones que medir.", file=sys.stderr)
        return 1
    informe = componer_informe(base_df, args.convencion)
    print(informe)
    if not args.sin_escribir:
        os.makedirs(DIR_RESULTADOS, exist_ok=True)
        destino = os.path.join(DIR_RESULTADOS, f"linea_base_{args.convencion}.md")
        with open(destino, "w", encoding="utf-8") as f:
            f.write(informe)
        print(f"[escrito] {os.path.relpath(destino, os.path.dirname(DIR_RESULTADOS))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
