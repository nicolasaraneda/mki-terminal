# ============================================================
# bifurcaciones.py — el jardín de senderos que se bifurcan
# (Gelman & Loken 2013) aplicado al track record sellado de MKI.
#
#   source venv/bin/activate
#   python -m GEMELO.bifurcaciones
#
# LA PREGUNTA. El proyecto tomó decenas de decisiones de análisis a lo
# largo de meses, cada una razonable por separado y documentada en su
# sitio. Nadie midió nunca cuánto de lo que se cree depende de esas
# elecciones y no de los datos. Este módulo construye la matriz COMPLETA
# de esas bifurcaciones y computa cada celda, para que el cociente
# «celdas significativas / celdas totales» se pueda LEER en vez de
# suponerse.
#
# NO es un análisis nuevo del modelo. Es una medición de la FRAGILIDAD de
# los análisis que ya existen. Ninguna celda es «la buena» y ninguna
# reemplaza a la publicada: el resultado es la DISPERSIÓN.
#
# SOLO LECTURA por construcción. La única entrada a `senales.db` sale de
# `backtest.linea_base.cargar` y de `backtest.datos._conexion_ro`, ambas
# en `uri mode=ro`. Este módulo no escribe en ninguna base, no toca
# `motor.py` ni `senales.py`, y no reescribe ninguna fila sellada.
#
# ------------------------------------------------------------
# LAS DOS RUTAS DE McNEMAR — leer antes de comparar un p
# ------------------------------------------------------------
# Hay dos implementaciones vivas en el repo y NO dan lo mismo:
#
#   `backtest.linea_base.mcnemar`  chi-cuadrado con corrección de
#       continuidad de Edwards. Es de donde salen TODAS las cifras
#       publicadas (README, GEMELO/DISEÑO.md §2, línea base §2.8).
#   `evaluacion.mcnemar_exact`     binomial exacta con p=0.5, la del
#       módulo de la skill `estadistica-evaluacion`.
#
# DECISIONES.md §55 ya midió la brecha en la cifra titular: 0.1849 por
# chi2 contra 0.1847 exacto, «las dos cifras son correctas». Este informe
# reporta LAS DOS en cada celda. **El conteo titular usa la EXACTA**,
# porque a estos n no depende de una aproximación asintótica y porque
# —DECISIONES.md §52— *una verificación que usa el mismo mecanismo que
# produjo la cifra NO es una verificación*: el estimador principal tiene
# que venir de otra familia que la que produjo lo publicado. El chi2 se
# reporta al lado para que ninguna cifra publicada quede sin su ruta.
#
# ------------------------------------------------------------
# EL ANCLA
# ------------------------------------------------------------
# El track record CRECE. Reproducir una afirmación congelada contra una
# base viva compara una cifra fija con un denominador móvil — hallazgo
# del WS5 del 30-ago, ya documentado en
# `backtest/linea_base.py:CORTE_SECCION_2`, y reincidente en el cuarto
# dictamen del diseño secuencial el 31-ago. Así que el corte de sello es
# aquí un EJE declarado, no un default escondido, y su nivel `publicado`
# reproduce EXACTAMENTE la cifra del README (n=248, +6.5 pp, p=0.1849).
# `_verificar_ancla()` lo comprueba en cada corrida y aborta si no.
# ============================================================

import argparse
import itertools
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude", "skills", "estadistica-evaluacion", "scripts"))

from evaluacion import (  # noqa: E402
    block_bootstrap, mcnemar_exact, wilson_ci,
)

from backtest.datos import RUTA_SENALES, _conexion_ro  # noqa: E402
from backtest.linea_base import cargar, mcnemar as mcnemar_chi2  # noqa: E402
from version import MODELO_VERSION  # noqa: E402

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "resultados")
DESTINO = os.path.join(DIR_RESULTADOS, "bifurcaciones.md")
DESTINO_CSV = os.path.join(DIR_RESULTADOS, "bifurcaciones.csv")

ALFA = 0.05
NOMINAL_INTERVALO = 0.80

# Bloque del bootstrap. El módulo de la skill exige bloques y no iid. Las
# filas van ORDENADAS POR FECHA. El bootstrap TITULAR es de clústeres de
# día (`_bootstrap_dia`); el de bloques de 20 filas del módulo de la
# skill se conserva SÓLO como segunda ruta del ΔMAE, para exhibir cuánto
# del veredicto lo pone el supuesto de independencia.
N_BOOT = 10_000     # el default del módulo de la skill; no se desvía sin decirlo
SEMILLA = 0         # obligatoria: un bootstrap sin semilla no reproduce
MINIMO_FILAS = 30   # piso declarado: bajo esto una celda no se puntúa

# ------------------------------------------------------------
# EL ANCLA PUBLICADA — README.md líneas 124-126, ventana sellada canónica
# ------------------------------------------------------------
# Esta celda de la matriz ES la cifra publicada. Si deja de reproducir, el
# informe no se escribe: o cambió la base, o cambió el código, y en
# cualquiera de los dos casos la matriz entera queda sin ancla.
CORTE_PUBLICADO = "2026-08-28"
ANCLA = {"n": 248, "modelo_pct": 66.1, "base_pct": 59.7,
         "ventaja_pp": 6.5, "b": 72, "c": 56, "p_chi2": 0.1849,
         "p_exacto": 0.1847}   # DECISIONES.md §55: las dos son correctas

# EL SEGUNDO ANCLA — la misma ventana BAJO LA REGLA FIRMADA (1-sep-2026).
# Hacen falta las dos: la de arriba prueba que el código sigue
# reproduciendo lo PUBLICADO (una afirmación anterior a la firma, y que
# nadie movió todavía); ésta es la celda ancla de la matriz de hoy. Si
# alguna de las dos deja de reproducir, el informe no se escribe.
#
# Y la diferencia entre ambas ES el hallazgo de este frente: la regla
# firmada mueve p de 0.1847 a 0.0451 — un desenlace que no estaba a la
# vista cuando se firmó, porque los dos que sí lo estaban eran 0.1847 y
# el 0.0323 de la rama prohibida.
ANCLA_REGLA = {"n": 238, "modelo_pct": 67.6, "base_pct": 58.0,
               "ventaja_pp": 9.7, "b": 72, "c": 49, "p_chi2": 0.0455,
               "p_exacto": 0.0451}

# ------------------------------------------------------------
# LOS EJES
# ------------------------------------------------------------
# Un eje entra sólo si cambia el CONJUNTO DE FILAS o el PUNTAJE, y sólo
# si es una elección DOCUMENTADA entre alternativas. Los candidatos que
# no cumplen están en `NO_EJES` con la razón medida — declarar un eje
# descartado importa tanto como incluirlo, porque un eje omitido en
# silencio es exactamente el grado de libertad que Gelman y Loken
# describen.

EJES = {
    # ---- 1. (RETIRADO) Regla de deduplicación --------------------
    # ESTE EJE YA NO EXISTE: la deduplicación dejó de ser una elección
    # abierta el 1-sep-2026, cuando Nicolás FIRMÓ la regla —«la fila
    # válida es la que tiene la sesión objetivo correcta según
    # `available_at`; el criterio es la corrección de la sesión, nunca la
    # frescura», con `keep="last"` explícitamente PROHIBIDA—. Un eje mide
    # una elección viva; una regla firmada no es una elección viva, y
    # dejarla como eje seguiría ofreciendo desde el código las tres ramas
    # que la firma retiró.
    #
    # La regla vive en `backtest.linea_base.deduplicar_por_sesion` y
    # `cargar()` la aplica por defecto, así que entra a esta matriz por la
    # carga y no por una celda. Consecuencia declarada: **la matriz pasa
    # de 768 celdas a 192**, y el veredicto del frente se recomputa sobre
    # las 192 en vez de suponerse.
    # CITA: la firma, DECISIONES.md (acta de la regla de deduplicación);
    # el forense en GEMELO/resultados/dedup_opciones.md.

    # ---- 2. Convención de empate ---------------------------------
    # El verificador puntúa al campeón con `>=` (senales.py): un gap de
    # exactamente 0.0 le cuenta como acierto si predijo >= 0. La baseline
    # de la §2.1 usaba `>`. Dos reglas distintas para los dos lados.
    # `gap == 0.00` exacto es la firma del ffill de feriados
    # (Supuesto #1 de CLAUDE.md): 4 de las 5 filas son 2330.TW.
    # CITA: backtest/linea_base.py, cabecera «LA CONVENCIÓN DEL EMPATE»;
    # DECISIONES.md §25.1 (línea 2149); congelada en `excluir_cero` por
    # GEMELO/DISEÑO.md §2.8 el 26-ago.
    "empate": ("estricta", "verificador", "excluir_cero"),

    # ---- 3. Bloque 15-23 jul 2026 --------------------------------
    # El criterio R2 del pre-registro descarta a un retador si su ventaja
    # desaparece al excluir esta ventana. Se operacionaliza por RANGO DE
    # FECHAS y no por índice de bloque porque el reparto interno de los
    # bloques NO REPRODUCE: se probaron cuatro órdenes de fila y ninguno
    # da los bloques publicados.
    # CITA: GEMELO/DISEÑO.md §6.2 (R2); DECISIONES.md §25.2 (líneas
    # 2188-2195); backtest/linea_base.py:VENTANA_R2.
    "ventana_r2": ("dentro", "fuera"),

    # ---- 4. Filas del 29-jul -------------------------------------
    # Pregunta abierta y NO decidida: «si las 8 filas del 29-jul (sesión
    # saltada) deben seguir en las métricas — que es la decisión de
    # abstención pendiente desde la 5.0.2». La regla de abstención por
    # sello tardío es una PROPUESTA formal, no implementada (4.6.0
    # congelado). Mientras no se decida, esas filas están dentro por
    # omisión, que es una elección tanto como sacarlas.
    # OJO: de las 8, sólo 7 saltaron sesión (las XKRX/XTAI/XTKS, 0/7 en
    # gap); IFX.DE conservó su objetivo natural y acertó. El eje quita
    # las 8, que es lo que la pregunta abierta dice literalmente.
    # CITA: DECISIONES.md §33.8 (líneas 2963-2973) y Etapa 5.0.2 §4
    # (líneas 1011-1025 y la tabla de 1240-1247).
    "filas_29jul": ("dentro", "fuera"),

    # ---- 5. Fechas con emisión parcial ---------------------------
    # HALLAZGO DE ESTE FRENTE, con precedente documentado. Cinco fechas
    # emitieron MENOS de las 8 predicciones de apertura habituales porque
    # la descarga no trajo todos los tickers: 13-jul (4/8), 21-jul (6/8),
    # 3-ago (4/8), 12-ago (5/8), 17-ago (4/8). La composición de tickers
    # de esos días no es aleatoria: es la que el proveedor entregó. Tres
    # de las cinco son además fechas de pares duplicados, así que este eje
    # y la regla de deduplicación se tocan sobre las mismas fechas — a
    # propósito y a la vista.
    # CITA: la errata de descarga del 8-24 jul (DECISIONES.md líneas
    # 664-686 y 1113-1119) enumera el mismo fenómeno y afirma que «el
    # costo fue de COBERTURA, no de veracidad»; esa afirmación es
    # exactamente lo que este eje pone a prueba. La salud de descarga se
    # sella desde 5.0 (`snapshots.descarga_ok/total`).
    "emision_parcial": ("dentro", "fuera"),

    # ---- 6. Corte de sello ---------------------------------------
    # El track record crece: contrastar una cifra congelada contra una
    # base viva compara numerador fijo con denominador móvil. El proyecto
    # se pisó con esto dos veces (WS5 el 30-ago; cuarto dictamen el
    # 31-ago: «con corte 26-ago el MDE da 7.38 pp, con 28/30-ago 7.22,
    # hoy 7.13»). Y ya lleva SIETE valores de n publicados (184, 223, 228,
    # 240, 245, 248, 253) — hoy 261, el octavo. Elegir CUÁNDO mirar es
    # una bifurcación.
    # CITA: backtest/linea_base.py:CORTE_SECCION_2; DECISIONES.md §34.10
    # (líneas 3184-3196) y §47 (líneas 4163-4171).
    "corte": ("publicado", "vivo"),

    # ---- 7. Cuál de los dos objetivos se puntúa ------------------
    # El verificador sella el DOBLE OBJETIVO por predicción: `gap_pct`
    # (¿existe la señal?) y `retorno_real_pct` (¿es capturable?), cada uno
    # con su acierto y su error. Las dos columnas viven en la MISMA fila
    # sellada y el proyecto publica las dos, pero el titular cita el gap.
    # CITA: CLAUDE.md, `senales.py` — THE verifier, «double objective»;
    # DECISIONES.md §32.6 (líneas 2828-2832: «el gap es precisamente lo
    # que NO se puede capturar») y §37.6 (línea 3606: gap 66.1% contra
    # retorno de sesión 60.9%).
    "objetivo": ("gap", "retorno_sesion"),

    # ---- 8. Zona muerta ------------------------------------------
    # Abstenerse por debajo de un umbral de |predicción|. La §2.4 la
    # publica con seis umbrales y cita el de 0.25 (n=184, +8.2 pp). Cada
    # nivel se compara contra SU PROPIA baseline sobre las filas que
    # sobreviven — comparar contra la global cambiaría el denominador.
    # Se toman dos niveles: sin zona muerta y el umbral publicado.
    # CITA: backtest/linea_base.py:UMBRALES_ZONA_MUERTA y su docstring;
    # GEMELO/DISEÑO.md §2.4; DECISIONES.md línea 2138 (entre las 21
    # afirmaciones reproducidas).
    "zona_muerta": (0.00, 0.25),
}

VENTANA_R2 = ("2026-07-15", "2026-07-23")
FECHA_29JUL = "2026-07-29"
FECHAS_PARCIALES = ("2026-07-13", "2026-07-21", "2026-08-03",
                    "2026-08-12", "2026-08-17")
EMISION_COMPLETA = 8      # predicciones de apertura por sesión

# Columnas selladas por objetivo: (acierto, valor real, error absoluto)
COLUMNAS_OBJETIVO = {
    "gap":            ("acierto_gap", "gap_pct", "error_gap_pp"),
    "retorno_sesion": ("acierto_direccion", "retorno_real_pct", "error_pp"),
}

# ------------------------------------------------------------
# CANDIDATOS QUE NO SON EJES — y por qué, medido
# ------------------------------------------------------------
NO_EJES = (
    ("regla de deduplicación",
     "La firma de Nicolás del 1-sep-2026 (acta en DECISIONES.md); el "
     "forense en GEMELO/resultados/dedup_opciones.md; la implementación "
     "en backtest/linea_base.py:deduplicar_por_sesion",
     "**YA NO ES UN EJE: es una regla FIRMADA.** «La fila válida es la "
     "que tiene la sesión objetivo correcta según `available_at`, no la "
     "más reciente; el criterio es la corrección de la sesión, nunca la "
     "frescura», con `keep=\"last\"` PROHIBIDA. Se aplica en la carga, "
     "así que la matriz pasó de 768 celdas a 192. Lo que la regla NO "
     "cubre —15 filas sin pareja que tampoco calzan— queda dentro y "
     "abierto en `cola_decisiones.md`."),
    ("residualización sí/no",
     "CLAUDE.md y motor.py: `divergencias_al` residualiza contra índice "
     "local + FX por defecto, «simple spread kept for comparison»; "
     "DECISIONES.md líneas 1384-1391 y §30.2 (línea 2568)",
     "NO ES UN EJE DE ESTA MATRIZ. Las divergencias residualizadas "
     "alimentan `z_divergencia` y de ahí las baselines B3-B5; NO entran a "
     "`prediccion_apertura_al`, que es β·SOX. Aunque entraran, variarlas "
     "exigiría re-emitir, y las filas selladas no se reescriben "
     "(Constitución 5.0, punto 3)."),
    ("ventana de betas (120 sesiones)",
     "CLAUDE.md y motor.py: `betas_al` «rolling window, default 120 "
     "trading days», sellada en `snapshots.ventana_betas`; DECISIONES.md "
     "§32.2 (línea 2760)",
     "NO COMPUTABLE sobre filas selladas: está horneada dentro de "
     "`apertura_estimada_pct`. Verificado abajo que toma UN SOLO valor en "
     "toda la ventana, así que ni siquiera hay variación histórica que "
     "explotar. Sí es un eje para la ventana larga reconstruida."),
    ("ffill de feriados (Supuesto #1)",
     "CLAUDE.md, «Data conventions»; DECISIONES.md §25.1 (línea 2149)",
     "YA ESTÁ EN LA MATRIZ, dentro del eje `empate`: el ffill es la CAUSA "
     "de `gap_pct == 0.00` y toda la bifurcación vive en cómo se puntúan "
     "esas filas. No se cuenta dos veces."),
    ("estado `sin_datos_mercado`",
     "CLAUDE.md, extras sellados 5.0; senales.py: «nunca entra a "
     "`verificacion_apertura`»; DECISIONES.md líneas 712-721",
     "NO ES UN EJE: esas filas no llegan al conjunto que la matriz mide. "
     "El umbral que las produce (5 sesiones del calendario real) es una "
     "elección documentada, pero gobierna la EMISIÓN, no la medición. "
     "Conteo verificado abajo."),
    ("estado `no_verificable_timing`",
     "CLAUDE.md, LA REGLA MAESTRA (Etapa 4.6): «kept for audit, excluded "
     "from ALL metrics»; DECISIONES.md líneas 1011-1013",
     "NO ES UN EJE, y hoy además está VACÍO: cero filas lo llevan. En "
     "particular el 29-jul no produjo ninguna, así que filtrar por ese "
     "estado no quita nada. Y la regla maestra no es una elección de "
     "análisis sino una restricción."),
    ("tickers con `duplicado_de` (TSM → 2330.TW)",
     "universo.py: «TSM counts once via 2330.TW»; DECISIONES.md líneas "
     "167-174",
     "NO ES UN EJE en este conjunto: TSM no emite predicción de apertura "
     "y no aparece en ninguna fila verificada. Verificado abajo."),
    ("MINIMO_OBSERVACIONES",
     "senales.py: `calibracion_intervalos()` devuelve «pendiente» por "
     "debajo del umbral",
     "NO ES UN EJE: es un umbral de PRESENTACIÓN (decide si se MUESTRA la "
     "cobertura, no qué filas la componen), y toda ventana de esta matriz "
     "lo supera con holgura. La cobertura se computa igual en cada celda "
     "y se reporta con su Wilson, que dice lo mismo sin ocultar."),
    ("filas canónicas en días de solapamiento titular/sombra",
     "docs/SOMBRA.md; DECISIONES.md §36.1 (líneas 3382-3385) y §36.7 "
     "(líneas 3491-3494)",
     "YA DECIDIDO Y APLICADO, no abierto: «fecha <= 2026-08-25 → canónico "
     "el MAC; fecha >= 2026-08-26 → canónico el PC». Movió n de 245 a 253 "
     "y la ventaja de +6.7 a +6.5 pp. La base local ya está en su forma "
     "canónica y tiene UNA sola fila por (fecha, ticker) —verificado "
     "abajo—, así que no queda bifurcación DENTRO de esta base."),
    ("desglose por bolsa / región",
     "DECISIONES.md §33.2 (líneas 2885-2895), §34.2 (líneas 3012-3015), "
     "§47 (líneas 4176-4181)",
     "DELIBERADAMENTE FUERA. Es un desglose de SUBGRUPOS, no una "
     "bifurcación de la cifra titular, y el propio proyecto ya registró "
     "que esas miradas produjeron falsos positivos retractados (Tokio "
     "p=0.021, Seúl p=0.031, «ninguno sobrevive Bonferroni ×8») y que "
     "«si alguna decisión se tomara mirándolo, N sube a 31 y hay que "
     "decirlo». Meterlos aquí fabricaría significancia, que es el pecado "
     "que esta matriz mide."),
    ("regla de abstención por sello tardío, alcance completo (17 filas)",
     "DECISIONES.md, Etapa 5.0.2 §4 (líneas 1225-1247): 29-jul 7 · "
     "03-ago 3 · 05-ago 7, «4/17 (23.5%)» contra «15/15» de las frescas",
     "PARCIALMENTE COMPUTADO. Las 15 filas rancias que TIENEN pareja "
     "fresca son exactamente las que retira la regla firmada, así que "
     "ya las cubre. Las de 05-ago no tienen pareja («no hubo, hueco del "
     "06») y no se pueden identificar desde columnas selladas. Se intentó "
     "reconstruirlas comparando `sesion_objetivo` contra "
     "`calendarios.proxima_sesion_despues_de` a la hora nominal de sello: "
     "NO REPRODUCE (difiere en las 261 filas), así que se descarta en vez "
     "de publicar una identificación que no se sostiene."),
)


# ------------------------------------------------------------
# Carga
# ------------------------------------------------------------
def cargar_filas(corte: str | None, dedup: bool = True) -> pd.DataFrame:
    """`backtest.linea_base.cargar` (mode=ro, legacy=0, sólo 4.6.0, sólo
    con gap) más las columnas del segundo objetivo, que `cargar` no trae.

    `dedup=True` es el default y **aplica la regla firmada** — por eso la
    deduplicación ya no es un eje de esta matriz. `dedup=False` existe
    para UNA cosa: verificar que la ventana publicada del README sigue
    reproduciendo, que es una afirmación anterior a la firma."""
    df = cargar(hasta_sello=corte, dedup=dedup)
    if df.empty:
        return df
    conn = _conexion_ro(RUTA_SENALES)
    try:
        ve = pd.read_sql_query(
            "SELECT fecha_senal AS fecha, ticker, acierto_direccion, error_pp"
            " FROM verificacion_apertura"
            " WHERE legacy = 0 AND modelo_version = ? AND gap_pct IS NOT NULL",
            conn, params=(MODELO_VERSION,))
    finally:
        conn.close()
    out = df.merge(ve, on=["fecha", "ticker"], how="left")
    if len(out) != len(df):
        raise RuntimeError("el join auxiliar duplicó filas")
    faltan = ["sesion_objetivo", "acierto_direccion", "error_pp"]
    if out[faltan].isna().any().any():
        raise RuntimeError(f"filas verificadas sin {faltan}")
    return out


# ------------------------------------------------------------
# Los ejes, aplicados. EL ORDEN IMPORTA Y SE DECLARA:
#   1) corte Y regla de deduplicación (ya aplicados en la carga)
#   2) objetivo: elige el par (acierto, real, error) sellado que se puntúa
#   3) filtros de filas: ventana_r2, 29-jul, emisión parcial, zona muerta
#   4) convención de empate (puntaje, y descarte si `excluir_cero`)
# La deduplicación se movió al PASO 1 con la firma del 1-sep: antes era el
# paso 4 y su enredo con `filas_29jul` era un hallazgo que había que
# mostrar (si el 29-jul salía, el par se resolvía solo y `first` y `last`
# coincidían). Con la regla firmada ese enredo desaparece por
# construcción: la fila que se conserva no depende de qué otras filas
# sigan en el conjunto, sólo de su propio `available_at`. Eso es una
# propiedad de la regla, no una comodidad — y es la razón por la que
# aplicarla en la carga es legítimo y aplicar `first`/`last` allí no lo
# habría sido.
# ------------------------------------------------------------
def aplicar(df: pd.DataFrame, celda: dict) -> pd.DataFrame:
    col_ac, col_real, col_err = COLUMNAS_OBJETIVO[celda["objetivo"]]
    out = df

    if celda["ventana_r2"] == "fuera":
        out = out[(out["fecha"] < VENTANA_R2[0]) | (out["fecha"] > VENTANA_R2[1])]
    if celda["filas_29jul"] == "fuera":
        out = out[out["fecha"] != FECHA_29JUL]
    if celda["emision_parcial"] == "fuera":
        out = out[~out["fecha"].isin(FECHAS_PARCIALES)]
    if celda["zona_muerta"] > 0:
        out = out[out["apertura_estimada_pct"].abs() >= celda["zona_muerta"]]

    out = out.copy()
    out["real"] = out[col_real].astype(float)
    out["acierto"] = out[col_ac].astype(int)
    out["error"] = out[col_err].astype(float)

    conv = celda["empate"]
    if conv == "excluir_cero":
        out = out[out["real"] != 0].copy()
        out["base_acierto"] = (out["real"] > 0).astype(int)
    elif conv == "estricta":
        out["base_acierto"] = (out["real"] > 0).astype(int)
    else:                                   # verificador
        out["base_acierto"] = (out["real"] >= 0).astype(int)
    return out


# ------------------------------------------------------------
# EL CLÚSTER ES EL DÍA — no la fila
# ------------------------------------------------------------
# Las ~8 filas de una sesión comparten el mismo movimiento del SOX: la
# predicción de cada ticker es βᵢ·SOX, así que en un día en que el SOX se
# movió al revés de lo esperado fallan casi todas juntas. Tratarlas como
# 248 observaciones independientes infla cualquier significancia.
#
# `icc_y_deff()` lo computa; no se hardcodea ninguna cifra aquí, que es
# como se desincronizan los comentarios de los números.
#
# Por eso el estimador titular de este frente es de CLÚSTER: se remuestrean
# y se permutan DÍAS ENTEROS, no filas. McNemar —que supone filas
# independientes— se reporta al lado, porque es la ruta que produjo las
# cifras publicadas, pero no es la que manda.
N_PERM = 4000

# Parámetros del IC de los dos MDE. El punto y las réplicas del bootstrap
# usan EXACTAMENTE los mismos, para que el intervalo sea coherente con su
# propio centro: computar el punto con más precisión que las réplicas
# dejaría un centro que no pertenece a la distribución que lo rodea.
# El MDE que el pre-registro secuencial derivó, citado como REFERENCIA
# EXTERNA y no recomputado aquí (su propio intervalo está en disputa, ver
# `GEMELO/resultados/mde_vs_observado.md`). CITA: cola_decisiones.md §2b y
# GEMELO/SECUENCIAL/mde_desde_v6.py — 8.96 pp en la escala del endpoint
# congelado `acierto_gap`.
#
# ERRATA, 1-sep-2026: el módulo se commiteó (`a49ad76`) USANDO este nombre
# sin definirlo nunca, así que `python -m GEMELO.bifurcaciones` reventaba
# con NameError antes de escribir el informe. El `bifurcaciones.md`
# versionado es anterior a esa línea. Se define aquí con su cita en vez de
# borrar el párrafo, que es lo que la referencia quiso decir.
MDE_RELEVANCIA_PUBLICADO = 8.96

BOOT_MDE50 = {"n_boot": 200}
BOOT_MDE80 = {"n_boot": 120, "n_sim": 250, "n_perm": 1000}


def _por_dia(df: pd.DataFrame, valores: np.ndarray) -> list:
    """Parte un vector de valores en la lista de sus clústeres de día."""
    codigos = pd.factorize(df["fecha"].to_numpy())[0]
    return [valores[codigos == j] for j in range(codigos.max() + 1)]


def icc_y_deff(grupos: list) -> dict:
    """ICC por ANOVA de una variable agrupada en clústeres, y el efecto de
    diseño que se sigue de ella. Es lo que traduce «las filas de un día no
    son independientes» a un número: con deff D, las N filas valen N/D
    observaciones efectivas.

    Estimador clásico de una vía (Fisher / Donner): con clústeres de
    tamaños distintos, m0 es el tamaño ajustado, no la media."""
    k = len(grupos)
    n_j = np.array([len(g) for g in grupos], dtype=float)
    N = n_j.sum()
    if k < 2 or N <= k:
        return {}
    medias = np.array([g.mean() for g in grupos], dtype=float)
    gran = float(np.concatenate(grupos).mean())
    msb = float((n_j * (medias - gran) ** 2).sum() / (k - 1))
    msw = float(sum(((g - g.mean()) ** 2).sum() for g in grupos) / (N - k))
    m0 = (N - (n_j ** 2).sum() / N) / (k - 1)
    denom = msb + (m0 - 1) * msw
    icc = (msb - msw) / denom if denom else float("nan")
    # Kish: el tamaño que entra al deff es Σn²/N, no la media. Con
    # clústeres desiguales los dos difieren y el docstring manda.
    m_kish = float((n_j ** 2).sum() / N)
    deff = 1 + (m_kish - 1) * icc
    return {"clusters": k, "n": int(N), "tam_medio": N / k,
            "tam_kish": m_kish, "icc": icc, "deff": deff,
            "n_efectivo": N / deff if deff and deff > 0 else float("nan")}


def estructura_disidencia(df: pd.DataFrame) -> dict:
    """DÓNDE vive la comparación, contado sin ningún estimador de por medio.

    Contra «siempre al alza», el modelo sólo puede diferir en las filas
    donde predijo BAJA: en las demás los dos dicen lo mismo y aportan
    exactamente cero a la ventaja. Así que el denominador honesto no son
    las n filas, son las filas de DISIDENCIA — y agrupadas por día, los
    días con saldo. Esta función lo dice en enteros, que es la forma más
    difícil de discutir y la más fácil de leer."""
    d = (df["acierto"] - df["base_acierto"]).to_numpy(float)
    dis = d != 0
    sub = df[dis]
    saldos = pd.Series(d[dis]).groupby(sub["fecha"].to_numpy()).sum()
    gana = int((saldos > 0).sum())
    pierde = int((saldos < 0).sum())
    empata = int((saldos == 0).sum())
    return {
        "filas": len(df),
        "disidencias": int(dis.sum()),
        "aciertos_en_disidencia": int(df.loc[dis, "acierto"].sum()),
        "dias_totales": int(df["fecha"].nunique()),
        "dias_con_disidencia": int(len(saldos)),
        "dias_gana": gana, "dias_pierde": pierde, "dias_empata": empata,
        "p_dias": mcnemar_exact(gana, pierde),
    }


def caida_r2_con_ic(df: pd.DataFrame, n_boot: int) -> dict:
    """Cuánto cae la ventaja al excluir la ventana R2, CON su intervalo de
    clúster de día. El punto solo no alcanza: afirmar «R2 dispara por
    efecto» es una inferencia y necesita el mismo estimador que el resto
    del informe, no aritmética simple sobre la mediana de las celdas."""
    d = (df["acierto"] - df["base_acierto"]).to_numpy(float)
    dentro = np.ones(len(df), dtype=bool)
    fuera = ((df["fecha"] < VENTANA_R2[0]) |
             (df["fecha"] > VENTANA_R2[1])).to_numpy()
    fechas = df["fecha"].to_numpy()
    dias = pd.factorize(fechas)[0]
    k = dias.max() + 1
    trozos = [(d[dias == j], dentro[dias == j], fuera[dias == j])
              for j in range(k)]

    def caida(sel):
        dd = np.concatenate([t[0] for t in sel])
        ff = np.concatenate([t[2] for t in sel])
        if ff.sum() == 0 or len(dd) == 0:
            return np.nan
        return 100.0 * (dd.mean() - dd[ff].mean())

    punto = caida(trozos)
    rng = np.random.default_rng(SEMILLA)
    reps = np.array([caida([trozos[j] for j in rng.integers(0, k, size=k)])
                     for _ in range(n_boot)], dtype=float)
    reps = reps[np.isfinite(reps)]
    lo, hi = np.quantile(reps, [ALFA / 2, 1 - ALFA / 2])
    return {"caida_pp": float(punto), "lo": float(lo), "hi": float(hi),
            "frac_no_positiva": float((reps <= 0).mean())}


def potencia_permutacion_dia(grupos: list, delta: float, n_sim: int,
                             n_perm: int, alpha: float = ALFA) -> float:
    """Potencia del test de permutación por día frente a un desplazamiento
    `delta` (en fracción, no pp), simulada remuestreando DÍAS ENTEROS de
    los residuos observados y sumándoles el efecto. Devuelve la fracción
    de simulaciones que rechazan."""
    todo = np.concatenate(grupos)
    cent = [g - todo.mean() for g in grupos]
    k = len(cent)
    rng = np.random.default_rng(SEMILLA)
    rechazos = 0
    for _ in range(n_sim):
        idx = rng.integers(0, k, size=k)
        muestra = [cent[j] + delta for j in idx]
        if _p_permutacion_dia(muestra, n_perm) < alpha:
            rechazos += 1
    return rechazos / n_sim


def mde_por_potencia(grupos: list, potencia: float = 0.80,
                     n_sim: int = 300, n_perm: int = 1200,
                     alpha: float = ALFA) -> float:
    """El efecto mínimo detectable AL NIVEL DE POTENCIA pedido, en pp.

    Importa la distinción: la bisección ingenua sobre «el p observado
    cruza α» devuelve el umbral al **50%** de potencia, que es la mitad
    del que hace falta para diseñar un experimento. El convencional es
    80%, y se reporta junto al otro para que nadie lea uno por el otro."""
    lo, hi = 0.0, 0.05
    for _ in range(12):
        if potencia_permutacion_dia(grupos, hi, n_sim, n_perm, alpha) >= potencia:
            break
        hi *= 1.6
        if hi > 5.0:
            return float("nan")
    for _ in range(9):
        mid = (lo + hi) / 2
        if potencia_permutacion_dia(grupos, mid, n_sim, n_perm,
                                    alpha) >= potencia:
            hi = mid
        else:
            lo = mid
    return 100.0 * hi


def ic_mde(grupos: list, cual: str, n_boot: int = 200,
           alpha: float = ALFA, **kw) -> dict:
    """IC del efecto mínimo detectable por bootstrap de DÍAS ENTEROS.

    El MDE se deriva de la dispersión OBSERVADA entre días, y esa
    dispersión sale de 34 días, no de infinitos: tiene incertidumbre
    muestral como cualquier otro estimador. Publicarlo pelado sería
    exigirle al resto del informe una regla que la cifra de diseño no
    cumple — y este informe rechaza el supuesto de independencia
    justamente por todo lo demás.

    Se remuestrean días con reemplazo (la MISMA unidad de clúster que el
    resto del módulo, la misma semilla) y se recalcula el MDE en cada
    réplica. `frac_degeneradas` declara cuántas réplicas no dieron un
    número: un remuestreo puede quedarse sin días informativos, y eso hay
    que contarlo en vez de esconderlo con un `dropna`.

    LIMITACIÓN DECLARADA: el MDE al 80% se busca por bisección sobre una
    curva de potencia SIMULADA, así que su IC arrastra ruido de Monte
    Carlo además del muestral. El de 50% no: su bisección es sobre un p
    de permutación, mucho más barato y estable.
    """
    fn = {"50": mde_permutacion_dia, "80": mde_por_potencia}[cual]
    k = len(grupos)
    rng = np.random.default_rng(SEMILLA)
    reps = []
    for _ in range(n_boot):
        idx = rng.integers(0, k, size=k)
        reps.append(fn([grupos[j] for j in idx], **kw))
    arr = np.array(reps, dtype=float)
    ok = arr[np.isfinite(arr)]
    if len(ok) < 20:
        return {"punto": fn(grupos), "lo": float("nan"), "hi": float("nan"),
                "n_boot": n_boot, "frac_degeneradas": 1 - len(ok) / n_boot}
    lo, hi = np.quantile(ok, [alpha / 2, 1 - alpha / 2])
    punto = fn(grupos, **kw)
    # DECISIONES.md §34.9: un punto que cae FUERA de su propio intervalo
    # de percentiles no es un error de cálculo, es una señal de sesgo de
    # la distribución bootstrap — y hay que reportarla, no taparla. Pasa
    # cuando los remuestreos son sistemáticamente más heterogéneos que la
    # muestra original, que es justo lo que infla un MDE.
    return {"punto": punto, "lo": float(lo), "hi": float(hi),
            "n_boot": n_boot, "frac_degeneradas": 1 - len(ok) / n_boot,
            "punto_dentro": bool(lo <= punto <= hi)}


def mde_permutacion_dia(grupos: list, n_perm: int = N_PERM,
                        alpha: float = ALFA) -> float:
    """El EFECTO MÍNIMO DETECTABLE del test de permutación por día, en pp.

    Un test que no puede rechazar nada tampoco es una medición: si el
    «0 de N» viniera de un test sin potencia, no diría nada del modelo.
    Así que se mide con qué ventaja constante SÍ rechazaría, sobre esta
    misma estructura de días y tamaños.

    Se centra la diferencia observada, se le suma un desplazamiento δ
    idéntico a cada fila y se busca por bisección el δ más chico que hace
    p < alpha. Devuelve δ en puntos porcentuales."""
    if len(grupos) < 2:
        return float("nan")
    todo = np.concatenate(grupos)
    centrados = [g - todo.mean() for g in grupos]

    def rechaza(delta: float) -> bool:
        return _p_permutacion_dia([g + delta for g in centrados],
                                  n_perm) < alpha

    lo, hi = 0.0, 1.0
    for _ in range(40):                       # encontrar una cota superior
        if rechaza(hi):
            break
        hi *= 2
        if hi > 1e3:
            return float("nan")
    for _ in range(40):                       # bisección
        mid = (lo + hi) / 2
        if rechaza(mid):
            hi = mid
        else:
            lo = mid
    return 100.0 * hi


def _bootstrap_dia(grupos: list, n_boot: int, alpha: float = ALFA) -> tuple:
    """Bootstrap de CLÚSTERES DE DÍA: remuestrea días enteros con
    reemplazo y devuelve el IC de la media global como razón de sumas
    —que es lo correcto cuando los clústeres tienen tamaños distintos—.

    Reemplaza al bootstrap de bloques de filas: con 34 días hay clústeres
    de sobra, y el bloque de 20 filas mezclaba días parciales además de
    ser NO circular (el defecto que `backtest/metricas.py` ya corrigió el
    26-ago para el Sharpe y que no había que reintroducir aquí)."""
    k = len(grupos)
    sumas = np.array([g.sum() for g in grupos], dtype=float)
    cuentas = np.array([len(g) for g in grupos], dtype=float)
    punto = float(sumas.sum() / cuentas.sum())
    if k < 2:
        return punto, float("nan"), float("nan")
    rng = np.random.default_rng(SEMILLA)
    idx = rng.integers(0, k, size=(n_boot, k))
    reps = sumas[idx].sum(axis=1) / cuentas[idx].sum(axis=1)
    lo, hi = np.quantile(reps, [alpha / 2, 1 - alpha / 2])
    return punto, float(lo), float(hi)


def _p_permutacion_dia(grupos: list, n_perm: int = N_PERM,
                       semilla: int = SEMILLA) -> float:
    """p bilateral por permutación de SIGNO a nivel de día (cluster
    randomization test). H0: la diferencia media de un día es simétrica
    alrededor de cero — o sea, el modelo no le gana a la baseline en
    ningún sentido sistemático.

    Se permuta el signo de la SUMA de cada día, no de cada fila: eso es
    lo que respeta que las filas de un día no son independientes. Lleva
    la corrección +1 de Phipson-Smyth, así que nunca devuelve 0."""
    S = np.array([g.sum() for g in grupos], dtype=float)
    if len(S) < 2:
        return 1.0
    obs = abs(float(S.sum()))
    # La semilla es la MISMA en todas las celdas, a propósito: el ruido de
    # Monte Carlo queda común a la matriz entera, así que la comparación
    # entre celdas no lo hereda como si fuera señal. Y reproduce.
    # `semilla` es inyectable (2-sep, dictamen del adversario): dentro de un
    # ESTUDIO de α o potencia, re-sembrar igual en cada réplica hace que
    # todas compartan una sola matriz de signos y el estimador no converge
    # con n_sim. Para las celdas de la matriz el default sigue siendo fijo.
    rng = np.random.default_rng(semilla)
    signos = rng.choice(np.array([-1.0, 1.0]), size=(n_perm, len(S)))
    nulos = np.abs(signos @ S)
    return float((1 + int((nulos >= obs - 1e-12).sum())) / (n_perm + 1))


# ------------------------------------------------------------
# Métricas de una celda — ningún estimador puntual sin intervalo
# ------------------------------------------------------------
def metricas(df: pd.DataFrame, n_boot: int = N_BOOT,
             objetivo_gap: bool = True) -> dict:
    n = len(df)
    if n < MINIMO_FILAS:
        return {"n": n}
    mod = df["acierto"].to_numpy(dtype=int)
    base = df["base_acierto"].to_numpy(dtype=int)
    km, kb = int(mod.sum()), int(base.sum())

    b = int(((mod == 1) & (base == 0)).sum())
    c = int(((mod == 0) & (base == 1)).sum())

    # Wilson sobre las tasas: es la convención publicada y se conserva
    # para poder comparar. DECLARADO: Wilson supone filas independientes,
    # que aquí no lo son, así que estos dos intervalos son OPTIMISTAS. La
    # comparación —que es lo que decide— va por clúster de día.
    mo_lo, mo_hi = wilson_ci(km, n)
    ba_lo, ba_hi = wilson_ci(kb, n)

    # Ventaja: diferencia PAREADA sobre las mismas filas, con IC y p de
    # CLÚSTER DE DÍA.
    d = (mod - base).astype(float)
    grupos_d = _por_dia(df, d)
    _, v_lo, v_hi = _bootstrap_dia(grupos_d, n_boot)
    p_dia = _p_permutacion_dia(grupos_d)

    # Magnitud: la diferencia PAREADA contra predecir 0.0, que es lo que
    # la casa pide. Comparar el IC del MAE del modelo contra el MAE de
    # cero como si fuera un punto sin intervalo es doblemente inválido
    # (punto desnudo + comparación no pareada sobre series correlacionadas).
    err = df["error"].to_numpy(dtype=float)
    triv = np.abs(df["real"].to_numpy(dtype=float))
    mae, mae_lo, mae_hi = _bootstrap_dia(_por_dia(df, err), n_boot)
    mae_cero, mc_lo, mc_hi = _bootstrap_dia(_por_dia(df, triv), n_boot)
    dpar = err - triv
    dmae, dmae_lo, dmae_hi = _bootstrap_dia(_por_dia(df, dpar), n_boot)
    # La MISMA diferencia pareada por la otra ruta: bootstrap de bloques
    # de FILAS, que es el default del módulo de la skill. Se reporta al
    # lado por la misma razón que las dos rutas de McNemar — para que se
    # vea qué parte del veredicto la pone el clúster y qué parte los datos.
    _, dmb_lo, dmb_hi = block_bootstrap(dpar, np.mean, 20, n_boot,
                                        ALFA, SEMILLA)

    # El intervalo del 80% se construyó para el GAP. Medir su cobertura
    # contra el retorno de sesión produce un número que se PARECE a una
    # cobertura y no lo es — y cae dentro de la banda de V3 por accidente,
    # así que publicarlo invita a leer «V3 pasa». No se computa.
    cal = (df.dropna(subset=["intervalo80_pp"])
           if objetivo_gap else df.iloc[0:0])
    if len(cal):
        dentro = ((cal["real"] - cal["apertura_estimada_pct"]).abs()
                  <= cal["intervalo80_pp"]).to_numpy().astype(float)
        k_cob, n_cob = int(dentro.sum()), len(cal)
        cob_lo, cob_hi = wilson_ci(k_cob, n_cob)
        cobertura_pct = 100 * k_cob / n_cob
        _, cd_lo, cd_hi = _bootstrap_dia(_por_dia(cal, dentro), n_boot)
    else:
        n_cob = 0
        cobertura_pct = cob_lo = cob_hi = cd_lo = cd_hi = float("nan")

    return {
        "n": n, "dias": int(df["fecha"].nunique()),
        "modelo_pct": 100 * km / n,
        "modelo_lo": 100 * mo_lo, "modelo_hi": 100 * mo_hi,
        "base_pct": 100 * kb / n,
        "base_lo": 100 * ba_lo, "base_hi": 100 * ba_hi,
        "ventaja_pp": 100 * (km - kb) / n,
        "ventaja_lo": 100 * v_lo, "ventaja_hi": 100 * v_hi,
        "p_dia": p_dia,
        "b": b, "c": c,
        "p_exacto": mcnemar_exact(b, c),
        "p_chi2": mcnemar_chi2(b, c),
        "mae": mae, "mae_lo": mae_lo, "mae_hi": mae_hi,
        "mae_cero": mae_cero, "mae_cero_lo": mc_lo, "mae_cero_hi": mc_hi,
        "dmae": dmae, "dmae_lo": dmae_lo, "dmae_hi": dmae_hi,
        "dmae_bloque_lo": dmb_lo, "dmae_bloque_hi": dmb_hi,
        "n_cobertura": n_cob,
        "cobertura_pct": cobertura_pct,
        "cobertura_lo": 100 * cob_lo, "cobertura_hi": 100 * cob_hi,
        "cobertura_dia_lo": 100 * cd_lo, "cobertura_dia_hi": 100 * cd_hi,
    }


# ------------------------------------------------------------
# El ancla — verificar una cifra publicada ANTES de escribir nada
# ------------------------------------------------------------
CELDA_ANCLA = {"empate": "excluir_cero",
               "ventana_r2": "dentro", "filas_29jul": "dentro",
               "emision_parcial": "dentro", "corte": "publicado",
               "objetivo": "gap", "zona_muerta": 0.00}


def ancla_por_ruta_independiente() -> dict:
    """El ancla recalculada por una ruta que NO comparte código con la
    matriz: su propio SQL y su propia aritmética a mano, sin `cargar()`,
    sin `aplicar()` y sin `metricas()`. DECISIONES.md §52: *una
    verificación que usa el mismo mecanismo que produjo la cifra no es
    una verificación*.

    Lo ÚNICO que comparte con la matriz es `_conexion_ro`, y eso no es
    negociable: el invariante de aislamiento del proyecto exige que nada
    en `GEMELO/` abra `senales.db` por su cuenta, porque una conexión
    cruda puede quedar en modo escritura por omisión sobre la base que
    sella en producción. Abrir el archivo no es parte del mecanismo que
    produjo la cifra; la consulta, la selección de filas y la aritmética
    sí, y ésas son propias."""
    import math
    conn = _conexion_ro(RUTA_SENALES)
    try:
        d = pd.read_sql_query(
            "SELECT v.fecha_senal f, v.ticker t, v.gap_pct g, v.acierto_gap a,"
            "       s.exchange x, s.sesion_objetivo so, s.available_at av"
            " FROM verificacion_apertura v"
            " LEFT JOIN senales_ticker s"
            "        ON s.fecha = v.fecha_senal AND s.ticker = v.ticker"
            " WHERE v.legacy = 0 AND v.modelo_version = ?"
            "   AND v.gap_pct IS NOT NULL"
            "   AND substr(v.verificado_en, 1, 10) <= ?",
            conn, params=(MODELO_VERSION, CORTE_PUBLICADO))
    finally:
        conn.close()

    def duelo(sub):
        mod = sub["a"].astype(int)
        base = (sub["g"] > 0).astype(int)
        b = int(((mod == 1) & (base == 0)).sum())
        c = int(((mod == 0) & (base == 1)).sum())
        n, k = b + c, min(b, c)
        p = (min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
             if n else 1.0)
        return {"n": len(sub), "modelo_pct": round(100 * mod.mean(), 1),
                "base_pct": round(100 * base.mean(), 1),
                "ventaja_pp": round(100 * (mod.mean() - base.mean()), 1),
                "b": b, "c": c, "p_exacto": round(p, 4)}

    d = d[d["g"] != 0]                                   # excluir_cero

    # La REGLA FIRMADA, reimplementada aquí a mano: bucle explícito sobre
    # los grupos duplicados, sin `deduplicar_por_sesion` y sin ninguna
    # ayuda de pandas para colapsar. Lo único compartido con la matriz es
    # `calendarios.proxima_sesion_despues_de`, que ES el criterio y no el
    # mecanismo — igual que `_conexion_ro` abre el archivo sin ser parte
    # de la aritmética.
    import calendarios
    from datetime import datetime, timezone

    def sesion(x, av):
        t = datetime.fromisoformat(str(av))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return str(calendarios.proxima_sesion_despues_de(x, t)[0])

    cuenta = d.groupby(["t", "so"])["f"].transform("size")
    filas = []
    for _, fila in d.iterrows():
        if cuenta[fila.name] == 1:
            filas.append(fila)
            continue
        hermanas = d[(d["t"] == fila["t"]) & (d["so"] == fila["so"])]
        calzan = [sesion(h["x"], h["av"]) == h["so"]
                  for _, h in hermanas.iterrows()]
        if sum(calzan) == 1 and sesion(fila["x"], fila["av"]) != fila["so"]:
            continue                       # la retira la regla
        filas.append(fila)
    reglada = pd.DataFrame(filas)

    fuera = d[(d["f"] < VENTANA_R2[0]) | (d["f"] > VENTANA_R2[1])]
    return {"ancla": duelo(d), "ancla_regla": duelo(reglada),
            "sin_ventana_r2": duelo(fuera)}


def _contrastar_ancla(m: dict, esperado: dict, etiqueta: str) -> list:
    fallos = []
    for k, tol in (("n", 0), ("modelo_pct", 0.05), ("base_pct", 0.05),
                   ("ventaja_pp", 0.05)):
        if abs(float(m[k]) - float(esperado[k])) > tol:
            fallos.append(f"[{etiqueta}] {k}: {esperado[k]} · matriz {m[k]}")
    for k in ("b", "c"):
        if m[k] != esperado[k]:
            fallos.append(f"[{etiqueta}] McNemar {k}: {esperado[k]} · "
                          f"matriz {m[k]}")
    for k, ruta in (("p_chi2", "chi2"), ("p_exacto", "exacta")):
        if abs(m[k] - esperado[k]) > 0.0005:
            fallos.append(f"[{etiqueta}] p (ruta {ruta}): {esperado[k]} · "
                          f"matriz {round(m[k], 4)}")
    return fallos


def _verificar_ancla(bases: dict) -> list:
    """DOS anclas, y las dos tienen que reproducir o el informe no se
    escribe:

      · `publicada` — la ventana sellada canónica del README, medida SIN
        la regla de deduplicación porque es una afirmación anterior a la
        firma. Comprueba que el código sigue reproduciendo lo publicado.
      · `regla` — la misma celda BAJO la regla firmada. Es la referencia
        de la matriz de hoy.

    La distancia entre las dos no es ruido: es el efecto de la firma, y
    está declarada arriba en `ANCLA` / `ANCLA_REGLA`."""
    fallos = _contrastar_ancla(
        metricas(aplicar(bases["publicado_sin_dedup"], CELDA_ANCLA),
                 n_boot=200), ANCLA, "publicada")
    fallos += _contrastar_ancla(
        metricas(aplicar(bases["publicado"], CELDA_ANCLA), n_boot=200),
        ANCLA_REGLA, "regla firmada")
    return fallos


# ------------------------------------------------------------
# La matriz
# ------------------------------------------------------------
def construir_matriz(n_boot: int = N_BOOT) -> tuple:
    bases = {"publicado": cargar_filas(CORTE_PUBLICADO),
             "vivo": cargar_filas(None),
             "publicado_sin_dedup": cargar_filas(CORTE_PUBLICADO,
                                                 dedup=False)}
    fallos = _verificar_ancla(bases)
    if fallos:
        raise RuntimeError(
            "EL ANCLA NO REPRODUCE — la matriz queda sin referencia y no se "
            "escribe informe. Diferencias:\n  " + "\n  ".join(fallos))

    nombres = list(EJES)
    filas = []
    for combo in itertools.product(*(EJES[k] for k in nombres)):
        celda = dict(zip(nombres, combo))
        m = metricas(aplicar(bases[celda["corte"]], celda), n_boot,
                     objetivo_gap=(celda["objetivo"] == "gap"))
        filas.append({**celda, **m})

    # El nivel `vivo` se mueve con el reloj. Se SELLA en el informe qué
    # era «vivo» el día de la corrida: sin eso, esta cifra hereda la
    # misma dependencia del reloj que el WS5 diagnosticó y §45 castiga.
    ctx = {
        "filas_publicado": len(bases["publicado"]),
        "filas_vivo": len(bases["vivo"]),
        "ultima_fecha_vivo": bases["vivo"]["fecha"].max(),
    }
    return pd.DataFrame(filas), ctx


# ------------------------------------------------------------
# ¿Qué eje mueve el veredicto? — medido, no opinado
# ------------------------------------------------------------
def influencia(mat: pd.DataFrame) -> pd.DataFrame:
    """Para cada eje: manteniendo TODOS los demás fijos, cuánto se mueve
    la métrica al recorrer sólo los niveles de ese eje.

    `rango_ventaja_pp` es la media, sobre todos los grupos de los otros
    ejes, del (max - min) dentro del grupo. `cruza_pct` es la fracción de
    grupos en los que ese eje **por sí solo** hace cruzar α = 0.05: es la
    medida directa de «mueve el veredicto»."""
    nombres = list(EJES)
    out = []
    for eje in nombres:
        otros = [e for e in nombres if e != eje]
        rangos_v, rangos_p, cruces, cruces_mc, grupos = [], [], 0, 0, 0
        for _, sub in mat.groupby(otros, sort=False):
            if sub["n"].min() < MINIMO_FILAS:
                continue
            grupos += 1
            rangos_v.append(sub["ventaja_pp"].max() - sub["ventaja_pp"].min())
            rangos_p.append(sub["p_dia"].max() - sub["p_dia"].min())
            sig = sub["p_dia"] < ALFA
            if sig.any() and (~sig).any():
                cruces += 1
            sig_mc = sub["p_exacto"] < ALFA
            if sig_mc.any() and (~sig_mc).any():
                cruces_mc += 1
        out.append({
            "eje": eje,
            "niveles": len(EJES[eje]),
            "rango_ventaja_pp": float(np.mean(rangos_v)),
            "rango_ventaja_max_pp": float(np.max(rangos_v)),
            "rango_p": float(np.mean(rangos_p)),
            "rango_p_max": float(np.max(rangos_p)),
            "grupos": grupos,
            "cruza_p_dia": cruces,
            "cruza_mcnemar": cruces_mc,
        })
    # Se ordena por cuánto MUEVE LA VENTAJA, no por cruces: bajo
    # inferencia de clúster no hay ninguna celda significativa, así que
    # `cruza_p_dia` es 0 en todos los ejes y no ordena nada. Ese cero no
    # es un empate entre ejes: es el veredicto del frente.
    return (pd.DataFrame(out)
            .sort_values("rango_ventaja_pp", ascending=False)
            .reset_index(drop=True))


# ------------------------------------------------------------
# ¿Qué sobrevive en TODAS las celdas?
# ------------------------------------------------------------
def desglose_significancia(mat: pd.DataFrame) -> pd.DataFrame:
    """Nivel por nivel: de las celdas que contienen ese nivel, cuántas dan
    p < α. Si un nivel concentra TODAS las celdas significativas, eso es
    el hallazgo: la significancia no es del modelo, es de esa elección."""
    v = mat[mat["n"] >= MINIMO_FILAS]
    filas = []
    for eje, niveles in EJES.items():
        for niv in niveles:
            sub = v[v[eje] == niv]
            filas.append({
                "eje": eje, "nivel": str(niv),
                "celdas": len(sub),
                "p_dia<0.05": int((sub["p_dia"] < ALFA).sum()),
                "McNemar<0.05": int((sub["p_exacto"] < ALFA).sum()),
                "ventaja mediana pp": float(sub["ventaja_pp"].median()),
                "ventaja min pp": float(sub["ventaja_pp"].min()),
                "ventaja max pp": float(sub["ventaja_pp"].max()),
            })
    return pd.DataFrame(filas)


def supervivientes(mat: pd.DataFrame) -> pd.DataFrame:
    """Afirmaciones que el proyecto podría querer hacer. Sobrevive sólo la
    que se cumple en el 100% de las celdas — cualquier otra hay que
    condicionarla a la elección de análisis que la sostiene."""
    v = mat[mat["n"] >= MINIMO_FILAS]
    # La cobertura del intervalo del 80% se construyó para el GAP. Sus
    # filas se evalúan SÓLO sobre las celdas del objetivo publicado —
    # promediarlas con `retorno_sesion` produciría un porcentaje que no
    # describe a ninguno de los dos.
    g = v[v["objetivo"] == "gap"]
    pruebas = (
        ("La ventaja sobre «siempre al alza» es positiva",
         v, v["ventaja_pp"] > 0),
        ("La ventaja es significativa con inferencia de clúster de día "
         "(p_dia < 0.05)", v, v["p_dia"] < ALFA),
        ("La ventaja es significativa por McNemar, que supone filas "
         "independientes", v, v["p_exacto"] < ALFA),
        ("El IC95 de la ventaja (clúster de día) excluye el cero",
         v, v["ventaja_lo"] > 0),
        ("Los IC95 Wilson del modelo y de la baseline se solapan",
         v, (v["modelo_lo"] <= v["base_hi"]) & (v["base_lo"] <= v["modelo_hi"])),
        ("El modelo acierta más del 50%", v, v["modelo_pct"] > 50),
        ("El IC95 Wilson del modelo excluye el 50%", v, v["modelo_lo"] > 50),
        # Las dos de control: si la baseline CONSTANTE también las cumple,
        # las dos de arriba no dicen nada del modelo, dicen que la ventana
        # fue alcista. Van aquí para que el superviviente no se lea solo.
        ("(control) La baseline «siempre al alza» acierta más del 50%",
         v, v["base_pct"] > 50),
        ("(control) El IC95 Wilson de la baseline excluye el 50%",
         v, v["base_lo"] > 50),
        ("El MAE del modelo es menor que el de predecir 0.0",
         v, v["dmae"] < 0),
        ("El IC95 PAREADO de ΔMAE excluye el cero (clúster de día)",
         v, v["dmae_hi"] < 0),
        ("El IC95 PAREADO de ΔMAE excluye el cero (bloques de filas, la "
         "ruta que supone independencia)", v, v["dmae_bloque_hi"] < 0),
        ("(sólo objetivo `gap`) La cobertura del intervalo 80% supera su "
         "nominal", g, g["cobertura_pct"] > 100 * NOMINAL_INTERVALO),
        ("(sólo objetivo `gap`) La cobertura cae en la banda [76%, 84%] "
         "que exige V3", g,
         (g["cobertura_pct"] >= 76) & (g["cobertura_pct"] <= 84)),
        ("(sólo objetivo `gap`) El IC95 de la cobertura excluye el 80% "
         "nominal (intervalos demasiado anchos)", g,
         g["cobertura_lo"] > 100 * NOMINAL_INTERVALO),
    )
    filas = []
    for etiqueta, universo, mascara in pruebas:
        k, n = int(mascara.sum()), len(universo)
        filas.append({
            "afirmación": etiqueta,
            "celdas": f"{k}/{n}",
            "%": 100.0 * k / n,
            "sobrevive": "SÍ" if k == n else "no",
        })
    return pd.DataFrame(filas)


# ------------------------------------------------------------
# Los NO-ejes, auditados con números en vez de con una afirmación
# ------------------------------------------------------------
def auditar_no_ejes() -> dict:
    conn = _conexion_ro(RUTA_SENALES)
    try:
        st = pd.read_sql_query(
            "SELECT fecha, ticker, estado, exchange FROM senales_ticker", conn)
        snaps = pd.read_sql_query("SELECT ventana_betas FROM snapshots", conn)
        ver = pd.read_sql_query(
            "SELECT ticker, legacy, modelo_version, gap_pct"
            " FROM verificacion_apertura", conn)
    finally:
        conn.close()
    vivos = ver[(ver["legacy"] == 0) & (ver["modelo_version"] == MODELO_VERSION)
                & ver["gap_pct"].notna()]
    est = st["estado"].fillna("(NULL)").value_counts().to_dict()
    return {
        "estados": est,
        "sin_datos_mercado": int(est.get("sin_datos_mercado", 0)),
        "no_verificable_timing": int(est.get("no_verificable_timing", 0)),
        "legacy_pre_46": int(est.get("legacy_pre_4.6", 0)),
        "tsm_en_verificadas": int((vivos["ticker"] == "TSM").sum()),
        "tsm_emite_apertura": int(((st["ticker"] == "TSM")
                                   & st["exchange"].notna()).sum()),
        "ventana_betas": sorted(
            snaps["ventana_betas"].dropna().unique().tolist()),
        "duplicados_fecha_ticker": int(st.duplicated(["fecha", "ticker"]).sum()),
    }


def resumen_parciales() -> pd.DataFrame:
    """La evidencia del eje 5, computada y no afirmada."""
    conn = _conexion_ro(RUTA_SENALES)
    try:
        st = pd.read_sql_query(
            "SELECT fecha, ticker FROM senales_ticker"
            " WHERE modelo_version = ? AND exchange IS NOT NULL",
            conn, params=(MODELO_VERSION,))
    finally:
        conn.close()
    g = (st.groupby("fecha")
           .agg(emitidas=("ticker", "size"),
                tickers=("ticker", lambda s: ", ".join(sorted(s))))
           .reset_index())
    return g[g["emitidas"] < EMISION_COMPLETA].reset_index(drop=True)


def resumen_duplicados(corte: str | None = CORTE_PUBLICADO,
                       dedup: bool = False) -> pd.DataFrame:
    """La evidencia del eje retirado, computada y no afirmada.

    `dedup=False` a propósito: la evidencia son los 15 pares TAL COMO
    ESTÁN en la base. Leerla sobre las filas que la regla ya dejó
    mostraría sólo su resultado y escondería sobre qué actuó."""
    df = cargar_filas(corte, dedup=dedup)
    dup = df[df.duplicated(["ticker", "sesion_objetivo"], keep=False)]
    return (dup.groupby("sesion_objetivo")
               .agg(pares=("ticker", "nunique"),
                    filas=("ticker", "size"),
                    emitidas_en=("fecha", lambda s: " y ".join(sorted(set(s)))),
                    aciertos_gap=("acierto_gap", "sum"))
               .reset_index())


# ------------------------------------------------------------
# Informe
# ------------------------------------------------------------
def _tabla(df: pd.DataFrame, flotantes: int = 2) -> str:
    if df.empty:
        return "(sin filas)\n"
    d = df.copy()
    for col in d.columns:
        if pd.api.types.is_float_dtype(d[col]):
            d[col] = d[col].map(lambda v: "" if pd.isna(v)
                                else f"{v:.{flotantes}f}")
    L = ["| " + " | ".join(str(c) for c in d.columns) + " |",
         "|" + "|".join(["---"] * len(d.columns)) + "|"]
    for _, f in d.iterrows():
        L.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in f) + " |")
    return "\n".join(L) + "\n"


def componer_informe(mat: pd.DataFrame, n_boot: int, ctx: dict) -> str:
    v = mat[mat["n"] >= MINIMO_FILAS]
    n_tot = len(v)
    sig_d = int((v["p_dia"] < ALFA).sum())          # el estimador titular
    sig_e = int((v["p_exacto"] < ALFA).sum())       # la ruta publicada
    sig_c = int((v["p_chi2"] < ALFA).sum())
    # `dentro` es EL CONJUNTO COMPLETO de datos; `fuera` es la ablación
    # que R2 pre-registra. No son coequales y el cociente va estratificado.
    full = v[v["ventana_r2"] == "dentro"]
    abla = v[v["ventana_r2"] == "fuera"]
    inf = influencia(mat)
    sup = supervivientes(mat)
    des = desglose_significancia(mat)
    aud = auditar_no_ejes()
    indep = ancla_por_ruta_independiente()
    top = inf.iloc[0]
    # La fila del ancla, seleccionada por sus niveles y no por posición.
    _m = np.ones(len(v), dtype=bool)
    for eje, niv in CELDA_ANCLA.items():
        _m &= (v[eje] == niv).to_numpy()
    fila_ancla = v[_m].iloc[0]
    # El ICC y el efecto de diseño del ancla, COMPUTADOS aquí — no
    # citados. Son la justificación entera del estimador de clúster.
    _anc = aplicar(cargar_filas(CORTE_PUBLICADO), CELDA_ANCLA)
    _gd = _por_dia(_anc,
                   (_anc["acierto"] - _anc["base_acierto"]).to_numpy(float))
    clus = icc_y_deff(_gd)
    ic50 = ic_mde(_gd, "50", **BOOT_MDE50)
    ic80 = ic_mde(_gd, "80", **BOOT_MDE80)
    mde, mde80 = ic50["punto"], ic80["punto"]
    pot_pub = potencia_permutacion_dia(_gd, ANCLA["ventaja_pp"] / 100,
                                       400, 1500)
    pot_regla = potencia_permutacion_dia(_gd, ANCLA_REGLA["ventaja_pp"] / 100,
                                         400, 1500)
    estr = estructura_disidencia(_anc)
    r2ic = caida_r2_con_ic(_anc, min(n_boot, 4000))
    n_caminos = int(np.prod([len(x) for x in EJES.values()]))

    # ¿Hay algún nivel que concentre TODAS las celdas significativas? Si
    # lo hay, la significancia no es del modelo: es de esa elección.
    sig = v[v["p_exacto"] < ALFA]   # la ruta publicada: la única con celdas
    monopolios = [(eje, str(sig[eje].iloc[0]))
                  for eje in EJES
                  if sig[eje].nunique() == 1] if sig.shape[0] else []

    L = [
        "# El jardín de senderos que se bifurcan",
        "",
        "*Cuánto de lo que este proyecto cree depende de sus elecciones de "
        "análisis y no de sus datos.*",
        "",
        "> **EN DIEZ SEGUNDOS**",
        "> ",
        f"> **1. Toda la información discriminante del track record es un "
        f"{estr['dias_gana']}-{estr['dias_pierde']} en "
        f"{estr['dias_con_disidencia']} días.** Contra «siempre al alza» "
        f"el modelo sólo puede diferir cuando predice BAJA: "
        f"{estr['disidencias']} de {estr['filas']} filas, agrupadas en "
        f"{estr['dias_con_disidencia']} días de emisión, de los que ganó "
        f"{estr['dias_gana']}, perdió {estr['dias_pierde']} y empató "
        f"{estr['dias_empata']} — binomial exacta **p = "
        f"{estr['p_dias']:.2f}**. Eso se entiende sin estadística, y todo "
        "lo que sigue es la ruta formal hacia el mismo hecho.",
        "> ",
        f"> **2.** Bajo la **regla de deduplicación firmada** la ventaja de "
        f"la ventana es {ANCLA_REGLA['ventaja_pp']:+} pp (la publicada, "
        f"anterior a la firma, es {ANCLA['ventaja_pp']:+} pp); su "
        f"intervalo honesto —clúster de día, que es la unidad real— es "
        f"**[{fila_ancla['ventaja_lo']:+.1f}, "
        f"{fila_ancla['ventaja_hi']:+.1f}] pp**. No es que el modelo "
        f"falle: **el diseño no tiene potencia**. Frente al efecto de la "
        f"regla la potencia es **{100*pot_regla:.0f}%** (frente al "
        f"publicado, {100*pot_pub:.0f}%), y detectarlo al "
        f"80% exigiría **{mde80:.0f} pp, IC95 [{ic80['lo']:.0f}, "
        f"{ic80['hi']:.0f}]**.",
        "> ",
        f"> **3.** Sobre eso, {n_tot} formas legítimas de medir la misma "
        f"ventana dan una ventaja entre "
        f"{v['ventaja_pp'].min():+.1f} y {v['ventaja_pp'].max():+.1f} pp, "
        f"y **{sig_d} de {n_tot}** con p < 0.05 por clúster ({sig_e} por "
        f"la ruta publicada, que supone filas independientes). No "
        "sobrevive a todas las celdas ninguna afirmación sobre la ventaja "
        "del modelo. **El track record todavía no alcanza para juzgar al "
        "campeón, en ninguna dirección.**",
        "",
        f"- Generado: {datetime.now(timezone.utc).isoformat()}",
        f"- Fuente: `senales.db` en `mode=ro` · modelo {MODELO_VERSION} · "
        "`legacy = 0`",
        "- Reproducible con un comando: `python -m GEMELO.bifurcaciones` "
        f"(bootstrap de clústeres de día, semilla {SEMILLA}, {n_boot} "
        f"réplicas; permutación de signo por día, {N_PERM} permutaciones)",
        f"- **Dos anclas verificadas, y las dos abortan el informe si "
        f"fallan.** (1) *Publicada*: sin la regla de deduplicación, la "
        f"celda `excluir_cero · dentro · dentro · dentro · publicado · gap "
        f"· 0.00` reproduce la ventana sellada del README "
        f"(n={ANCLA['n']}, {ANCLA['modelo_pct']}% contra "
        f"{ANCLA['base_pct']}%, {ANCLA['ventaja_pp']:+} pp, b={ANCLA['b']}, "
        f"c={ANCLA['c']}, p = {ANCLA['p_chi2']}). (2) *Regla firmada*: la "
        f"MISMA celda con la regla aplicada da n={ANCLA_REGLA['n']}, "
        f"{ANCLA_REGLA['ventaja_pp']:+} pp, b={ANCLA_REGLA['b']}, "
        f"c={ANCLA_REGLA['c']}, **p = {ANCLA_REGLA['p_exacto']}** "
        f"(exacta; {ANCLA_REGLA['p_chi2']} por chi2). Esa es la celda "
        "ancla de esta matriz.",
        "- **La firma produjo un TERCER desenlace.** Nicolás firmó "
        "conociendo dos: p = 0.1847 sin deduplicar y p = 0.0323 con "
        "`keep=\"last\"`, que quedó prohibida. Su regla da **0.0451** — "
        "cruza α = 0.05, y no estaba a la vista al firmar. El criterio "
        "sigue siendo el correcto; el desenlace se declara porque una "
        "decisión informada por dos números que produce un tercero "
        "necesita esa nota.",
        f"- **Los dos cortes, sellados:** `publicado` = "
        f"{ctx['filas_publicado']} filas (hasta `verificado_en` "
        f"{CORTE_PUBLICADO}, pinchado y estable); `vivo` = "
        f"{ctx['filas_vivo']} filas, última señal "
        f"{ctx['ultima_fecha_vivo']}. El nivel `vivo` se mueve con el "
        "reloj, así que queda escrito qué era el día de la corrida: sin "
        "eso esta cifra heredaría la misma dependencia del reloj que el "
        "WS5 diagnosticó.",
        "- **Ninguna cifra publicada se mueve.** La matriz mide alrededor de "
        "lo publicado, no en lugar de ello.",
        "",
        "---",
        "",
        "## EL VEREDICTO",
        "",
        f"**La cifra de la ventana bajo la regla firmada, con su intervalo "
        f"honesto: {ANCLA_REGLA['ventaja_pp']:+} pp, IC95 de clúster de día "
        f"[{fila_ancla['ventaja_lo']:+.1f}, "
        f"{fila_ancla['ventaja_hi']:+.1f}] pp.** Ése es el número que "
        "faltaba, y explica todo lo que sigue: con un intervalo de "
        f"{fila_ancla['ventaja_hi'] - fila_ancla['ventaja_lo']:.0f} pp de "
        "ancho, esta ventana no separa al campeón de una constante — **y "
        "eso vale aunque McNemar cruce α**, que es exactamente la brecha "
        "que este informe existe para medir.",
        "",
        f"**{sig_d} de {n_tot} celdas dan p < 0.05.** Ése es el cociente "
        "que se pidió medir. Pero el cociente no es un veredicto sobre el "
        "modelo: es un veredicto sobre el tamaño de la muestra, y la "
        "sección de potencia lo dice con números.",
        "",
        "### Dónde vive la comparación, en enteros",
        "",
        "Antes de cualquier estimador, la observación que hace legible "
        "todo lo demás y que no necesita que nadie confíe en un bootstrap: "
        "contra «siempre al alza» el modelo **sólo puede diferir en las "
        "filas donde predijo BAJA**. En las demás los dos dicen lo mismo y "
        "aportan exactamente cero a la ventaja.",
        "",
        f"| | |", "|---|---|",
        f"| Filas del ancla | {estr['filas']} |",
        f"| De ellas, filas de **disidencia** (el modelo predijo baja) | "
        f"**{estr['disidencias']}** |",
        f"| Aciertos del modelo en esas filas | "
        f"{estr['aciertos_en_disidencia']} "
        f"({100*estr['aciertos_en_disidencia']/estr['disidencias']:.1f}%) |",
        f"| Días con alguna disidencia | "
        f"**{estr['dias_con_disidencia']}** de {estr['dias_totales']} |",
        f"| Días con saldo a favor / en contra / empatados | "
        f"{estr['dias_gana']} / {estr['dias_pierde']} / "
        f"{estr['dias_empata']} |",
        f"| Binomial exacta sobre los días con saldo | "
        f"**p = {estr['p_dias']:.2f}** |",
        "",
        f"Es decir: los **b = {ANCLA_REGLA['b']}** y **c = "
        f"{ANCLA_REGLA['c']}** que sostienen el p de la regla no son "
        f"{ANCLA_REGLA['b'] + ANCLA_REGLA['c']} observaciones "
        "independientes. "
        f"Son {estr['dias_gana']} días ganados contra "
        f"{estr['dias_pierde']} perdidos. **Un {estr['dias_gana']}-"
        f"{estr['dias_pierde']} no distingue nada**, y para verlo no hace "
        "falta ningún aparato: alcanza con contar. Todo el ICC, el "
        "bootstrap de clúster y la permutación de abajo son la ruta formal "
        "hacia este mismo hecho.",
        "",
        "El estimador es el que respeta el **clúster de día**: las ~8 filas "
        "de una sesión son βᵢ·SOX sobre el MISMO movimiento del SOX, así "
        "que fallan y aciertan casi todas juntas. Computado sobre el ancla "
        f"({clus['n']} filas en {clus['clusters']} días, "
        f"{clus['tam_medio']:.1f} por día), el ICC por día de la "
        f"diferencia pareada es **{clus['icc']:.3f}** y el efecto de "
        f"diseño **{clus['deff']:.2f}**: **el n efectivo es "
        f"{clus['n_efectivo']:.0f}, no {clus['n']}.** "
        "El ICC es el estimador **ANOVA de una vía** (Fisher/Donner, con "
        "el tamaño ajustado m0 y no la media) y el deff usa el **tamaño de "
        "Kish**, Σn²/N — una sola procedencia para la cifra, declarada "
        f"aquí: con clústeres desiguales Kish da {clus['tam_kish']:.2f} "
        f"contra {clus['tam_medio']:.2f} de la media simple, y el deff "
        f"pasa de 3.54 a {clus['deff']:.2f}. **Ese cambio vino de una "
        "corrección del `estadistico-adversario`**, que señaló que el "
        "docstring prometía Kish y el código usaba la media; la "
        "conclusión no se movió y la diferencia se deja escrita para que "
        "la cifra no tenga dos orígenes. La significancia se "
        f"computa por permutación de signo a nivel de día ({N_PERM} "
        "permutaciones) y el IC por bootstrap de días enteros.",
        "",
        f"**Por la ruta publicada —McNemar, que supone las filas "
        f"independientes— serían {sig_e} de {n_tot} celdas "
        f"({100*sig_e/n_tot:.1f}%)**, y {sig_c} por la variante "
        f"chi-cuadrado con corrección de continuidad de la que salen las "
        f"cifras del README. La distancia entre {sig_e} y {sig_d} no la "
        "produce ninguna bifurcación de esta matriz: la produce un "
        "supuesto de independencia que los datos no cumplen. **El p "
        "publicado es el más generoso de los estimadores disponibles.**",
        "",
        f"**La ventaja sobre «siempre al alza» recorre "
        f"[{v['ventaja_pp'].min():+.1f}, {v['ventaja_pp'].max():+.1f}] pp a "
        f"lo largo de la matriz, con mediana "
        f"{v['ventaja_pp'].median():+.1f} pp.** La misma ventana sellada, "
        f"medida con siete decisiones que el proyecto ya tomó o dejó "
        f"abiertas, admite un rango de "
        f"{v['ventaja_pp'].max() - v['ventaja_pp'].min():.1f} puntos "
        f"porcentuales — "
        f"{abs(v['ventaja_pp'].max() - v['ventaja_pp'].min()) / abs(ANCLA_REGLA['ventaja_pp']):.1f}× "
        f"la cifra de la regla ({ANCLA_REGLA['ventaja_pp']:+} pp). En "
        f"{100*float((v['ventaja_pp'] > 0).mean()):.1f}% de las celdas es "
        f"positiva; en el resto, no.",
        "",
        f"**El eje que más mueve la cifra es `{top['eje']}`.** Fijando los "
        f"otros seis, recorrer sólo sus niveles mueve la ventaja una "
        f"media de {top['rango_ventaja_pp']:.1f} pp (máximo "
        f"{top['rango_ventaja_max_pp']:.1f} pp) y el p una media de "
        f"{top['rango_p']:.2f}; por la ruta publicada es además el único "
        f"que hace cruzar α = 0.05, en {top['cruza_mcnemar']} de "
        f"{top['grupos']} grupos. Le siguen "
        + ", ".join(f"`{r['eje']}` ({r['rango_ventaja_pp']:.1f} pp)"
                    for _, r in inf.iloc[1:4].iterrows())
        + f". El que menos mueve es `{inf.iloc[-1]['eje']}` "
        f"({inf.iloc[-1]['rango_ventaja_pp']:.2f} pp).",
        "",
        f"**Por definición y no por elección, `{top['eje']}` es el que "
        "urge cerrar** — con la salvedad grande de la sección siguiente. "
        f"El siguiente en urgencia es `{inf.iloc[1]['eje']}`, y ése sí es "
        "una elección abierta que nadie tomó.",
        "",
        "### ¿Y si el test simplemente no tiene potencia?",
        "",
        "Un test que no puede rechazar nada tampoco es una medición, así "
        "que la pregunta hay que hacérsela y contestarla con números. "
        "Simulando sobre la estructura real de días —remuestreo de días "
        "enteros de los residuos observados, más un desplazamiento "
        "constante—:",
        "",
        "| | |", "|---|---|",
        f"| Potencia frente al efecto publicado "
        f"({ANCLA['ventaja_pp']:+} pp) | **{100*pot_pub:.0f}%** |",
        f"| Efecto detectable al **50%** de potencia | {mde:.1f} pp, "
        f"IC95 [{ic50['lo']:.1f}, {ic50['hi']:.1f}] |",
        f"| Efecto detectable al **80%** de potencia (el convencional) | "
        f"**{mde80:.1f} pp, IC95 [{ic80['lo']:.1f}, {ic80['hi']:.1f}]** |",
        f"| Días con saldo informativo | "
        f"{estr['dias_con_disidencia']} de {estr['dias_totales']} |",
        "",
        f"**La potencia frente al efecto que el proyecto publica es "
        f"{100*pot_pub:.0f}%, apenas por encima de α.** Con eso, el cero "
        "de celdas significativas estaba escrito de antemano por la "
        "estructura de los datos, no por el modelo. Y el número que hay "
        f"que citar como umbral de diseño es el de 80% —{mde80:.0f} pp—, "
        f"no el de 50% ({mde:.0f} pp): confundirlos subestima a la mitad "
        "lo que hace falta.",
        "",
        "**Los dos MDE llevan intervalo, y por la misma razón que todo lo "
        "demás.** Un MDE se deriva de la dispersión OBSERVADA entre días, "
        f"y esa dispersión sale de {clus['clusters']} días, no de "
        "infinitos: tiene incertidumbre muestral. Los IC de arriba salen "
        "de remuestrear días enteros —la misma unidad de clúster y la "
        "misma semilla que el resto del informe— con "
        f"{ic50['n_boot']} réplicas para el de 50% y {ic80['n_boot']} para "
        f"el de 80%; réplicas degeneradas: "
        f"{100*ic50['frac_degeneradas']:.0f}% y "
        f"{100*ic80['frac_degeneradas']:.0f}%. **Limitación declarada:** "
        "el de 80% se busca por bisección sobre una curva de potencia "
        "SIMULADA, así que su intervalo arrastra ruido de Monte Carlo "
        "además del muestral; el de 50% bisecta sobre un p de permutación "
        "y no. En los dos casos el punto y las réplicas usan parámetros "
        "idénticos, para que el centro pertenezca a la distribución que lo "
        "rodea.",
        ""] + ([] if (ic50["punto_dentro"] and ic80["punto_dentro"]) else [
        "> **Aviso, en la disciplina de `DECISIONES.md` §34.9:** "
        + " y ".join(f"el MDE al {c}%"
                     for c, o in (("50", ic50), ("80", ic80))
                     if not o["punto_dentro"])
        + " cae FUERA de su propio intervalo de percentiles. No es un "
        "error de cálculo: es sesgo de la distribución bootstrap, que "
        "aparece cuando los remuestreos son sistemáticamente más "
        "heterogéneos que la muestra original — justo lo que infla un "
        "MDE. Se reporta en vez de taparse, y significa que la banda hay "
        "que leerla como cota superior de la precisión, no como un "
        "intervalo centrado.", ""]) + [
        "",
        "> Y lo que el intervalo agrega a la lectura: incluso en el extremo "
        f"OPTIMISTA de la banda del 80% ({ic80['lo']:.0f} pp), el diseño "
        f"seguiría necesitando una ventaja "
        f"{ic80['lo']/ANCLA['ventaja_pp']:.1f}× la publicada. **La "
        "conclusión no depende de dónde caiga el MDE dentro de su propia "
        "incertidumbre**, que es exactamente lo que un intervalo sirve "
        "para poder decir.",
        "",
        "**Ésa es la lectura honesta del cociente, y es distinta de «el "
        f"modelo no sirve».** Con {estr['dias_con_disidencia']} días "
        "informativos, este experimento no puede resolver todavía un "
        "efecto del tamaño que el modelo podría tener. El track record no "
        "está refutando al campeón; **está diciendo que aún no alcanza "
        "para juzgarlo**, y el supuesto de independencia era lo que hacía "
        "parecer que sí. Conviene contrastarlo con el MDE que el "
        f"pre-registro secuencial derivó ({MDE_RELEVANCIA_PUBLICADO} pp): "
        "ese cálculo no lleva corrección de clúster, y el clúster lo "
        f"multiplica por {mde80/MDE_RELEVANCIA_PUBLICADO:.1f}. Ese MDE se "
        "cita como referencia externa y NO se recomputa acá; su propio "
        "intervalo está en disputa (ver `mde_vs_observado.md`, que muestra "
        "que el [6.67, 11.32] publicado es el IC de E|gap| invertido y no "
        "el del MDE).",
        "",
        "### El cociente, estratificado (y por qué hay que estratificarlo)",
        "",
        "`ventana_r2 = dentro` **es el conjunto completo de datos**: no es "
        "una elección de análisis, es el default. `fuera` es la ablación "
        "que el criterio R2 pre-registra como prueba de estrés. Contarlas "
        "coequales mezclaría medio jardín con media ablación, así que el "
        "cociente va partido:",
        "",
        "| conjunto | celdas | p_dia < 0.05 | McNemar < 0.05 | ventaja "
        "mediana pp | rango pp |",
        "|---|---|---|---|---|---|",
        f"| **datos completos** (`ventana_r2 = dentro`) | {len(full)} | "
        f"**{int((full['p_dia'] < ALFA).sum())}** | "
        f"{int((full['p_exacto'] < ALFA).sum())} | "
        f"{full['ventaja_pp'].median():+.1f} | "
        f"[{full['ventaja_pp'].min():+.1f}, {full['ventaja_pp'].max():+.1f}] |",
        f"| ablación R2 (`ventana_r2 = fuera`) | {len(abla)} | "
        f"**{int((abla['p_dia'] < ALFA).sum())}** | "
        f"{int((abla['p_exacto'] < ALFA).sum())} | "
        f"{abla['ventaja_pp'].median():+.1f} | "
        f"[{abla['ventaja_pp'].min():+.1f}, {abla['ventaja_pp'].max():+.1f}] |",
        "",
    ]

    # R2 dispara por EFECTO o por POTENCIA? Se mide pareando cada camino
    # consigo mismo con los otros seis ejes fijos. Si la ventaja cae
    # mucho perdiendo pocas filas, es efecto.
    otros = [e for e in EJES if e != "ventana_r2"]
    pares = (v.pivot_table(index=otros, columns="ventana_r2",
                           values=["ventaja_pp", "n"], aggfunc="first")
              .dropna())
    if len(pares):
        delta = pares["ventaja_pp"]["dentro"] - pares["ventaja_pp"]["fuera"]
        perdidas = pares["n"]["dentro"] - pares["n"]["fuera"]
        vuelcos = int((pares["ventaja_pp"]["fuera"] < 0).sum())
        L += [
            f"**Sacar la ventana R2 cuesta caro en el punto estimado, y "
            f"barato en filas.** Pareando cada camino consigo mismo con "
            f"los otros seis ejes fijos, la ventaja cae una mediana de "
            f"{delta.median():.2f} pp "
            f"(dispersión ENTRE CAMINOS "
            f"[{delta.min():.2f}, {delta.max():.2f}] — eso es variación de "
            f"análisis, no error de muestreo) a cambio de perder "
            f"{perdidas.median():.0f} filas de "
            f"{pares['n']['dentro'].median():.0f} "
            f"({100*perdidas.median()/pares['n']['dentro'].median():.0f}%). "
            f"En **{vuelcos} de {len(pares)}** caminos pareados la ventaja "
            "se vuelve NEGATIVA al quitarla.",
            "",
            "**Pero eso es el punto, no la inferencia, y el frente no "
            "puede aplicarse a sí mismo una vara distinta de la que "
            "exige.** Con el MISMO estimador de clúster que gobierna todo "
            f"el informe, la caída del camino ancla es "
            f"**{r2ic['caida_pp']:+.2f} pp con IC95 "
            f"[{r2ic['lo']:+.2f}, {r2ic['hi']:+.2f}]**, y el "
            f"{100*r2ic['frac_no_positiva']:.0f}% de las réplicas da una "
            "caída nula o negativa. **El intervalo roza el cero.** Así "
            "que la lectura correcta no es «R2 dispara por efecto "
            "demostrado», sino: el punto estimado dice que seis fechas "
            "sostienen el signo del track record, y el diseño no tiene "
            "resolución ni para confirmar eso.",
            "",
        ]

    if monopolios and sig_e:
        L += [f"Y aun por la ruta publicada, las {sig_e} celdas "
              "significativas **no están repartidas por la matriz**: todas "
              "y cada una comparten un mismo nivel en "
              + ("estos ejes" if len(monopolios) > 1 else "este eje") + ":",
              ""]
        L += [f"- `{e}` = **{n}** — cero celdas significativas con otro "
              "valor" for e, n in monopolios]
        L += ["", "> **Esto y la tabla de influencia de más abajo son el "
              "MISMO hecho, no dos.** Para un eje de dos niveles, si las K "
              "celdas significativas comparten un nivel, entonces cada una "
              "forma grupo con su gemela no significativa y el conteo de "
              "«cruces» es K por identidad algebraica. Se dice acá para "
              "que la tabla no se lea como una confirmación independiente.",
              ""]

    todos = sup[sup["sobrevive"] == "SÍ"]["afirmación"].tolist()
    sobreviven = [s for s in todos if not s.startswith("(control)")]
    controles = [s for s in todos if s.startswith("(control)")]
    if sobreviven:
        L += [f"**Lo que sobrevive en las {n_tot} celdas** — las únicas "
              "afirmaciones que el proyecto puede hacer hoy sin "
              "condicionarlas a una elección de análisis:", ""]
        L += [f"{i}. {s}" for i, s in enumerate(sobreviven, 1)]
        base50 = 100.0 * float((v["base_pct"] > 50).mean())
        L += ["", "**Y hay que leer las de acierto con su control al lado, "
              "porque solas engañan.** Hablan de superar una moneda, no de "
              "superar a la baseline. La baseline constante «siempre al "
              f"alza» acierta también más del 50% en el {base50:.1f}% de "
              "las celdas: «acertar más de la mitad» describe sobre todo la "
              "ventana —un mercado que subió—, y el modelo lo hace con más "
              "holgura, que es una afirmación real pero mucho más chica que "
              "la publicada.", ""]

        n_dm_dia = int((v["dmae_hi"] < 0).sum())
        n_dm_blq = int((v["dmae_bloque_hi"] < 0).sum())
        n_dm_pto = int((v["dmae"] < 0).sum())
        L += ["**La MAGNITUD merece su propio párrafo, porque es donde el "
              "modelo estuvo más cerca.** El campeón le gana a predecir "
              f"0.0 en punto estimado en **{n_dm_pto} de {n_tot}** celdas "
              f"(ΔMAE del ancla {fila_ancla['dmae']:.3f} pp, IC de clúster "
              f"[{fila_ancla['dmae_lo']:.3f}, {fila_ancla['dmae_hi']:.3f}]). "
              "Pero con intervalo pareado y "
              f"cluster-honesto excluye el cero en sólo **{n_dm_dia} de "
              f"{n_tot}**; por la ruta de bloques de filas —la que supone "
              f"independencia— serían **{n_dm_blq}**. La misma brecha que "
              "en dirección, por la misma razón. **Robusto no es.**", "",
              "**No sobrevive NINGUNA afirmación sobre la ventaja del "
              f"modelo respecto de su baseline a las {n_tot} celdas: ni "
              "direccional ni de magnitud, ni significativa ni con "
              "intervalo que excluya el cero, ni siquiera —en dirección— "
              "positiva en todas.** Lo único que sobrevive el modelo lo "
              "comparte con una constante o lo hereda de sus intervalos "
              "deliberadamente anchos. **Ese es el titular.**"]
        pos = 100.0 * float((v["ventaja_pp"] > 0).mean())
        L += ["", "Y, por contraste, **lo que NO sobrevive**: todo lo demás "
              "de la tabla de abajo, empezando por el veredicto de "
              f"significancia — y por el signo mismo, que sólo es positivo "
              f"en el {pos:.1f}% de las celdas."]
    else:
        L += ["**NO SOBREVIVE NINGUNA AFIRMACIÓN.** Toda conclusión del "
              "track record depende de al menos una elección de análisis. "
              "Ese es el titular."]
    L += ["", "---", ""]

    L += [
        "## Qué es esto y qué no",
        "",
        "Gelman y Loken (2013) describen el *garden of forking paths*: un "
        "analista honesto, que no está buscando un p pequeño, toma igual "
        "decenas de decisiones razonables —qué filas cuentan, cómo se "
        "puntúa un empate, qué ventana se excluye, cuándo se mira— y cada "
        "una podría haber sido otra. El p que publica es condicional a ese "
        "camino, pero se lee como si fuera incondicional. No hace falta "
        "mala fe: basta con no medir la dispersión.",
        "",
        "Este proyecto tiene el material para medirla, porque documentó "
        "cada elección en su sitio. Lo que faltaba era el conteo. Esto "
        "**no es un análisis nuevo del modelo** ni un reproche a las "
        "decisiones: ninguna celda es «la buena», ninguna reemplaza a la "
        "publicada, y el resultado es la DISPERSIÓN, no un valor central.",
        "",
        f"La matriz tiene {n_caminos} caminos y {n_tot} son computables. "
        "**Los ejes no son ortogonales y no se pretende que lo sean** — "
        "la regla de deduplicación y `filas_29jul` se tocan sobre las "
        "mismas fechas, "
        "`emision_parcial` toca tres de las cinco fechas de pares. Un "
        "producto cartesiano leído como si fueran caminos independientes "
        "sobrestimaría el tamaño del jardín; por eso el resultado se "
        "reporta como cociente y rango, y la tabla de influencia mide cada "
        "eje **con los demás fijos**, que es la lectura que el "
        "solapamiento no rompe.",
        "",
        "**Reglas de la casa aplicadas.** Ningún estimador puntual sin "
        "intervalo: las tasas llevan Wilson; la ventaja, el MAE y su "
        "diferencia pareada, bootstrap de CLÚSTERES DE DÍA con semilla "
        "fija; la cobertura, Wilson. Y "
        "—DECISIONES.md §52— *una verificación que usa el mismo mecanismo "
        "que produjo la cifra no es una verificación*: el estimador "
        "principal sale del módulo de la skill `estadistica-evaluacion` "
        "(binomial exacta), no de `backtest/linea_base.py` (chi2 con "
        "corrección de continuidad), que es la ruta de lo publicado. Las "
        "dos se reportan.",
        "",
        "### Las dos rutas de McNemar, comparadas",
        "",
        f"| Ruta | Implementación | Celdas con p < {ALFA} |",
        "|---|---|---|",
        f"| Binomial exacta (**la que se usa**) | `evaluacion.mcnemar_exact` "
        f"| **{sig_e} / {n_tot}** |",
        f"| chi2 con corrección de continuidad (la publicada) | "
        f"`backtest.linea_base.mcnemar` | {sig_c} / {n_tot} |",
        "",
        f"Diferencia media |p_exacto − p_chi2| = "
        f"{(v['p_exacto'] - v['p_chi2']).abs().mean():.4f}; máxima "
        f"{(v['p_exacto'] - v['p_chi2']).abs().max():.4f}. Discrepan en el "
        f"veredicto en "
        f"{int(((v['p_exacto'] < ALFA) != (v['p_chi2'] < ALFA)).sum())} "
        f"celdas de {n_tot}. La elección de ruta importa poco; se reporta "
        "igual, porque no declararla sería un eje más escondido.",
        "",
        "### La vara independiente", "",
        "DECISIONES.md §52: *una verificación que usa el mismo mecanismo "
        "que produjo la cifra no es una verificación*. Las dos cifras que "
        "sostienen este informe —el ancla y el colapso al sacar la ventana "
        "R2— se recalculan por una ruta con **su propia consulta, su "
        "propia selección de filas y su propia aritmética**, sin "
        "`cargar()`, sin `aplicar()` y sin `metricas()`. Lo único que "
        "comparte es `_conexion_ro`, que abre el archivo en solo lectura: "
        "el invariante de aislamiento del proyecto prohíbe que nada en "
        "`GEMELO/` abra `senales.db` por su cuenta, y abrir el archivo no "
        "es parte del mecanismo que produjo la cifra.", "",
        _tabla(pd.DataFrame([{**{"cifra": k}, **val,
                              "p_exacto": f"{val['p_exacto']:.4f}"}
                             for k, val in indep.items()]), 1),
        f"Coincide con la matriz y con el README en el ancla, y el "
        f"colapso sin la ventana R2 ({indep['sin_ventana_r2']['ventaja_pp']:+} "
        f"pp, p = {indep['sin_ventana_r2']['p_exacto']}) reproduce lo que "
        "el criterio R2 del pre-registro ya afirmaba del propio campeón.",
        "",
        "---",
        "",
        "## Los ejes",
        "",
        "Un eje entra si cambia el CONJUNTO DE FILAS o el PUNTAJE, y sólo "
        "si es una elección documentada entre alternativas.",
        "",
        "### 1. `dedup` — RETIRADO: dejó de ser un eje y pasó a ser una regla",
        "",
        "El 1-sep-2026 Nicolás **firmó** la regla de deduplicación: *«la "
        "fila válida es la que tiene la sesión objetivo correcta según "
        "`available_at`, no la más reciente. El criterio es la corrección "
        "de la sesión, nunca la frescura»*, con `keep=\"last\"` "
        "explícitamente **prohibida** porque el forense demostró que "
        "retira selectivamente errores del modelo. Un eje mide una "
        "elección viva; una regla firmada no lo es. La regla vive en "
        "`backtest.linea_base.deduplicar_por_sesion` y entra a esta matriz "
        "por la carga.",
        "",
        f"**Consecuencia declarada: la matriz pasó de 768 celdas a "
        f"{n_caminos}.** El veredicto se recomputó sobre las nuevas en vez "
        "de suponerse que no cambiaba.",
        "",
        "La regla se implementa sola y **no lleva ninguna lista de fechas "
        "cableada** —una lista sería la regla escondiendo su propio "
        "criterio—: conservar la fila cuya `sesion_objetivo` coincide con "
        "`calendarios.proxima_sesion_despues_de(exchange, available_at)` "
        "separa por construcción los dos grupos del forense. En los 10 "
        "pares del defecto de reloj (31-jul, 5-ago) sólo una fila calza y "
        "la otra se retira; en los 5 de feriado real (12-ago, 18-ago) "
        "calzan las dos y no se descarta nada.",
        "",
        "**La diferencia sustantiva con `keep=\"last\"`, y hay que poder "
        "ver las dos cosas juntas.** El retiro NO es por frescura sino por "
        "no-correspondencia demostrable: esas 10 filas usan el cierre del "
        "SOX de `available_at` para puntuarse contra una sesión que está "
        "una sesión más allá, así que su `gap_pct` no es el gap que su "
        "insumo podía predecir. Es una justificación real y distinta. "
        "**Pero el efecto sobre el conteo tiene el mismo signo:** b queda "
        f"en {ANCLA_REGLA['b']} sin cambio y c baja de {ANCLA['c']} a "
        f"{ANCLA_REGLA['c']} — de las 10 filas retiradas, 7 eran "
        "discordantes y **las 7 favorecían a la baseline; ninguna al "
        "modelo**. Es la misma asimetría que motivó prohibir la otra rama, "
        "y el lector tiene que poder juzgar las dos cosas a la vez.",
        "",
        "**La opción que NO se puede tomar, y por qué.** Lo más completo "
        "sería **re-verificar** esas 10 filas contra su sesión objetivo "
        "correcta en vez de descartarlas. Eso exige recomputar valores "
        "sellados, y las filas selladas no se reescriben nunca "
        "(Constitución 5.0, punto 3). **Descartarlas se eligió por "
        "restricción, no por preferencia**, y conviene decirlo así.",
        "",
        "**Lo que la regla NO cubre, y es una pregunta abierta.** Es una "
        "regla de DEDUPLICACIÓN: sólo arbitra entre filas que compiten. "
        "Recomputando la sesión sobre TODAS las filas —no sólo las "
        "duplicadas— hay **25 que no calzan**, y **15 de ellas no tienen "
        "pareja** (7 del 5-ago que apuntan a 08-07 debiendo apuntar a "
        "08-06; 8 del 5-jul que apuntan a 07-06 debiendo apuntar a "
        "07-03). La firma no las previó porque nadie sabía que existían, y "
        "descartarlas sin reemplazo es una operación distinta de la que se "
        "firmó. Quedan **dentro**, y la pregunta está abierta en "
        "`GEMELO/resultados/cola_decisiones.md`.",
        "",
    ]

    ejes_doc = (
        ("2. `empate` — convención de empate",
         "`estricta` · `verificador` · `excluir_cero`",
         "backtest/linea_base.py, cabecera; DECISIONES.md §25.1 (línea "
         "2149); congelada en `excluir_cero` por GEMELO/DISEÑO.md §2.8",
         "El verificador puntúa al campeón con `>=` y la baseline de la "
         "§2.1 usaba `>`: dos reglas para los dos lados. `gap == 0.00` "
         "exacto es la firma del ffill de feriados (Supuesto #1); 4 de las "
         "5 filas son 2330.TW. **Alcance declarado:** esa justificación "
         "documenta el objetivo `gap`. Bajo `objetivo = retorno_sesion` el "
         "nivel `excluir_cero` descarta las filas con "
         "`retorno_real_pct == 0` —otras 4 filas, otro fenómeno— sin acta "
         "que lo respalde; el eje se aplica igual por simetría, y se dice."),
        ("3. `ventana_r2` — bloque 15-23 jul 2026",
         "`dentro` · `fuera`",
         "GEMELO/DISEÑO.md §6.2 (criterio R2); DECISIONES.md §25.2 (líneas "
         "2188-2195); backtest/linea_base.py:VENTANA_R2",
         "R2 descarta a un retador si su ventaja desaparece al excluir esa "
         "ventana. Se operacionaliza por RANGO DE FECHAS y no por índice de "
         "bloque porque el reparto interno de los bloques publicados NO "
         "REPRODUCE: se probaron cuatro órdenes de fila y ninguno lo da."),
        ("4. `filas_29jul` — las 8 filas del 29-jul",
         "`dentro` · `fuera`",
         "DECISIONES.md §33.8 (líneas 2963-2973); Etapa 5.0.2 §4 (líneas "
         "1011-1025 y tabla 1240-1247)",
         "Pregunta abierta y explícitamente **no decidida**: «si las 8 "
         "filas del 29-jul (sesión saltada) deben seguir en las métricas — "
         "que es la decisión de abstención pendiente desde la 5.0.2». "
         "Mientras no se decida, están dentro por omisión, que es una "
         "elección tanto como sacarlas. De las 8, sólo 7 saltaron sesión "
         "(0/7 en gap); IFX.DE conservó su objetivo natural y acertó. El "
         "eje quita las 8, que es lo que la pregunta dice literalmente."),
        ("5. `emision_parcial` — fechas con emisión parcial",
         "`dentro` · `fuera`",
         "**Hallazgo de este frente**, medido sobre `senales_ticker`; "
         "precedente en la errata de descarga (DECISIONES.md líneas "
         "664-686 y 1113-1119)",
         "Cinco fechas emitieron menos de las 8 predicciones de apertura "
         "habituales porque la descarga no trajo todos los tickers. La "
         "composición de esos días no es aleatoria: es la que el proveedor "
         "entregó. La errata de julio afirma que «el costo fue de "
         "COBERTURA, no de veracidad»; este eje es precisamente la prueba "
         "de esa afirmación. Tres de las cinco fechas son además fechas de "
         "pares duplicados, así que este eje y la regla de deduplicación "
         "se tocan — a propósito y a la vista."),
        ("6. `corte` — corte de sello",
         "`publicado` (2026-08-28, la ventana del README) · `vivo` (toda la "
         "base)",
         "backtest/linea_base.py:CORTE_SECCION_2; DECISIONES.md §34.10 "
         "(líneas 3184-3196) y §47 (líneas 4163-4171)",
         "El track record crece: contrastar una cifra congelada contra una "
         "base viva compara numerador fijo con denominador móvil. El "
         "proyecto se pisó con esto dos veces (WS5 el 30-ago; cuarto "
         "dictamen el 31-ago). Y ya lleva SIETE valores de n publicados "
         "(184, 223, 228, 240, 245, 248, 253) — hoy 261, el octavo. Elegir "
         "CUÁNDO mirar es una bifurcación, y el §47 ya la contabilizó como "
         "α ∈ [0.09, 0.18]."),
        ("7. `objetivo` — cuál de los dos objetivos se puntúa",
         "`gap` · `retorno_sesion`",
         "CLAUDE.md y senales.py («double objective»); DECISIONES.md §32.6 "
         "(líneas 2828-2832) y §37.6 (línea 3606)",
         "El verificador sella los dos por predicción: `gap_pct` (¿existe "
         "la señal?) y `retorno_real_pct` (¿es capturable?), cada uno con "
         "su acierto y su error, en la MISMA fila. El proyecto publica los "
         "dos, pero el titular cita el gap — y §32.6 dice con todas sus "
         "letras que «el gap es precisamente lo que no se puede capturar». "
         "Elegir cuál se titula es una bifurcación."),
        ("8. `zona_muerta` — abstenerse bajo un umbral de |predicción|",
         "`0.00` (sin zona muerta) · `0.25` (el umbral publicado)",
         "backtest/linea_base.py:UMBRALES_ZONA_MUERTA; GEMELO/DISEÑO.md "
         "§2.4; DECISIONES.md línea 2138",
         "La §2.4 publica seis umbrales y cita el de 0.25 con n=184 y "
         "+8.2 pp. **Esa cifra NO reproduce bajo el corte de esta matriz** "
         "—con el resto del ancla, `zona_muerta=0.25` deja n≈197— porque "
         "salió de otro corte de sello y otra convención de empate; se "
         "cita como contexto del eje, no como reproducción. Cada nivel se "
         "compara contra SU PROPIA baseline sobre "
         "las filas que sobreviven — comparar contra la global cambiaría el "
         "denominador y regalaría ventaja. Se toman dos niveles: ninguno y "
         "el publicado."),
    )
    for titulo, niveles, cita, texto in ejes_doc:
        L += [f"### {titulo}", "", f"- **Niveles:** {niveles}",
              f"- **Cita:** {cita}", "", texto, ""]

    L += ["### La evidencia del eje retirado, computada", "",
          "Los 15 pares que apuntan a la misma sesión objetivo, **antes** "
          f"de aplicar la regla (corte `{CORTE_PUBLICADO}`). "
          "`aciertos_gap` cuenta sobre el total de `filas`: donde vale la "
          "mitad, las dos emisiones del par predijeron signos opuestos "
          "sobre un gap idéntico. La regla firmada retira una fila de "
          "cada uno de los 10 pares de 31-jul y 5-ago, y no toca los 5 de "
          "12-ago y 18-ago.", "",
          _tabla(resumen_duplicados()),
          "### La evidencia del eje 5, computada", "",
          _tabla(resumen_parciales()), ""]

    L += ["### Orden de aplicación (declarado, porque importa)", "",
          "1. `corte` (en la carga)",
          "2. `objetivo`: elige el par (acierto, valor real, error) sellado",
          "3. filtros de filas: `ventana_r2`, `filas_29jul`, "
          "`emision_parcial`, `zona_muerta`",
          "4. `empate` (puntaje, y descarte si `excluir_cero`)",
          "",
          "Deduplicar DESPUÉS de filtrar es deliberado: si el 29-jul sale, "
          "la sesión del 31-jul se queda con la fila del 30-jul y `first` y "
          "`last` coinciden. Ese enredo entre ejes es real; la matriz debe "
          "mostrarlo, no esconderlo invirtiendo el orden.", ""]

    L += ["---", "", "## Candidatos que NO son ejes, y por qué", "",
          "Declarar un eje descartado importa tanto como incluirlo: un eje "
          "omitido en silencio es exactamente el grado de libertad que "
          "Gelman y Loken describen. Cada descarte va con su cita y con su "
          "medición, no con una afirmación.", "",
          _tabla(pd.DataFrame(
              [{"candidato": a, "cita": b, "por qué no": c}
               for a, b, c in NO_EJES])),
          "**Comprobaciones que sostienen la tabla:**", "",
          f"- Estados en `senales_ticker`: {aud['estados']}",
          f"- Filas `sin_datos_mercado`: **{aud['sin_datos_mercado']}** — "
          "ninguna llega a `verificacion_apertura` con gap.",
          f"- Filas `no_verificable_timing`: **{aud['no_verificable_timing']}** "
          "— el estado existe y hoy está vacío.",
          f"- Filas `legacy_pre_4.6`: **{aud['legacy_pre_46']}** — excluidas "
          "por `cargar()` vía `legacy = 0` y `modelo_version`.",
          f"- TSM (`duplicado_de` 2330.TW) en filas verificadas: "
          f"**{aud['tsm_en_verificadas']}**; predicciones de apertura que "
          f"emite TSM: **{aud['tsm_emite_apertura']}**.",
          f"- `snapshots.ventana_betas` toma los valores "
          f"{aud['ventana_betas']} en toda la ventana: no hay variación "
          "histórica que explotar aunque se quisiera.",
          f"- Duplicados exactos de (fecha, ticker) en `senales_ticker`: "
          f"**{aud['duplicados_fecha_ticker']}** — la base local ya está en "
          "su forma canónica, así que el solapamiento titular/sombra no es "
          "una bifurcación DENTRO de esta base.", ""]

    L += ["---", "", "## Qué eje mueve el veredicto", "",
          "Para cada eje, manteniendo **todos los demás fijos**, cuánto se "
          "mueve la métrica al recorrer sólo los niveles de ese eje. "
          "`rango_ventaja_pp` es la media (sobre los grupos de los otros "
          "ejes) del máximo menos el mínimo dentro del grupo, y es lo que "
          "ordena la tabla. `cruza_p_dia` cuenta los grupos en que ese eje "
          "por sí solo hace cruzar α = 0.05 con inferencia de clúster: es "
          "**cero en todos los ejes**, y ese cero no es un empate — es el "
          "veredicto del frente otra vez. `cruza_mcnemar` es el mismo "
          "conteo por la ruta publicada, y ahí sí se separa.", "",
          _tabla(inf), "",
          "### Dónde viven las celdas significativas", "",
          "Nivel por nivel: de las celdas que contienen ese nivel, cuántas "
          "dan p < 0.05. Un nivel que concentra el 0% y su alternativa que "
          "concentra todo no es un matiz — es el veredicto entero colgando "
          "de esa elección.", "", _tabla(des, 1), ""]

    L += ["---", "", "## Qué sobrevive en TODAS las celdas", "",
          "Cada fila es una afirmación que el proyecto podría querer hacer. "
          "Sobrevive sólo la que se cumple en el 100% de las celdas; "
          "cualquier otra hay que condicionarla, en voz alta, a la elección "
          "de análisis que la sostiene.", "", _tabla(sup, 1), ""]

    L += ["---", "", "## La matriz completa", "",
          f"{n_tot} celdas, ordenadas por `p_dia`. `p_dia` es la "
          f"permutación de signo por día ({N_PERM} permutaciones) y es el "
          f"estimador titular; `p_exacto` y `p_chi2` son las rutas de "
          f"McNemar, que suponen filas independientes. `ventaja_*`, "
          f"`mae*` y `dmae*` llevan IC por bootstrap de CLÚSTERES DE DÍA "
          f"({n_boot} réplicas, semilla {SEMILLA}); las tasas llevan "
          f"Wilson. `dmae` es la diferencia PAREADA entre el MAE del "
          "modelo y el de predecir 0.0 — que es la comparación válida: "
          "las dos series se miden sobre las mismas filas y están muy "
          "correlacionadas, así que enfrentar dos IC no pareados no "
          "prueba nada.", "",
          f"> **Los días por celda van de {int(v['dias'].min())} a "
          f"{int(v['dias'].max())}** (mediana {int(v['dias'].median())}), y "
          "el día es la unidad muestral del estimador titular: el piso de "
          f"{MINIMO_FILAS} filas está en la unidad equivocada y se declara "
          "como tal. Ninguna celda quedó por debajo de 20 días, pero eso "
          "salió así, no se impuso.", "",
          "> **`ventaja_lo > 0` y `p_dia < 0.05` no son duales** y pueden "
          "discrepar: el primero es un percentil de bootstrap y el segundo "
          "una permutación de signo. En esta matriz discrepan en "
          f"{int(((v['ventaja_lo'] > 0) != (v['p_dia'] < ALFA)).sum())} "
          "celda(s). Se listan las dos filas en la tabla de "
          "supervivientes porque miden cosas parecidas, no la misma.", "",
          "> **Wilson supone filas independientes y aquí no lo son**, así "
          "que `modelo_lo/hi` y `base_lo/hi` son OPTIMISTAS. Se conservan "
          "porque son la convención publicada y hacen falta para "
          "comparar; lo que decide el veredicto va por clúster de día.",
          "",
          "> **Sobre la cobertura bajo `objetivo = retorno_sesion`.** El "
          "intervalo del 80% se construyó para el GAP. Medir su cobertura "
          "contra el retorno de sesión responde «¿está calibrado para el "
          "objetivo capturable?», que es una pregunta legítima y distinta; "
          "no es la cobertura publicada y no debe citarse como tal.", ""]

    cols = (list(EJES) +
            ["n", "dias", "modelo_pct", "modelo_lo", "modelo_hi", "base_pct",
             "base_lo", "base_hi", "ventaja_pp", "ventaja_lo", "ventaja_hi",
             "p_dia", "b", "c", "p_exacto", "p_chi2",
             "mae", "mae_lo", "mae_hi", "mae_cero", "mae_cero_lo",
             "mae_cero_hi", "dmae", "dmae_lo", "dmae_hi",
             "dmae_bloque_lo", "dmae_bloque_hi",
             "n_cobertura", "cobertura_pct", "cobertura_lo", "cobertura_hi",
             "cobertura_dia_lo", "cobertura_dia_hi"])
    tab = mat[cols].copy()
    tab = tab.sort_values(["p_dia", "p_exacto", "ventaja_pp"])
    for col in ("p_dia", "p_exacto", "p_chi2"):
        tab[col] = tab[col].map(lambda x: f"{x:.4f}")
    L += [_tabla(tab), ""]

    L += ["---", "", "## Lo que este frente NO computó", "",
          "- **Residualización y ventana de betas.** Son parámetros del "
          "MOTOR, no de la capa de medición: variarlos exige re-emitir las "
          "predicciones, y las filas selladas no se reescriben "
          "(Constitución 5.0, punto 3). Fuera por construcción, no por "
          "olvido.",
          "- **Qué hacer con las 15 filas SIN pareja cuya "
          "`sesion_objetivo` tampoco calza con su `available_at`.** Se "
          "cuentan y se declaran (arriba, en el eje retirado), pero NO se "
          "retiran: la regla firmada arbitra entre filas que compiten y "
          "estas 15 están solas. Descartarlas sin reemplazo es otra "
          "decisión y es de Nicolás — está abierta en "
          "`cola_decisiones.md`. Nota: en el caso del 5-jul la sesión "
          "correcta (07-03) YA HABÍA CERRADO al sellar, así que con el "
          "ancla temporal buena esas 8 filas caerían en "
          "`no_verificable_timing`. **No las descartaría un criterio "
          "nuevo: las descartaría la regla maestra que el proyecto ya "
          "tiene.**",
          "- **Una corrección de multiplicidad sobre las celdas.** A "
          "propósito: comparten casi todas las filas y un Bonferroni "
          "ingenuo sobre ellas no significaría nada. El resultado de este "
          "frente es el COCIENTE y el RANGO, no un p corregido.",
          "- **Un intervalo alrededor de los cocientes de celdas** "
          f"(«{sig_e}/{n_tot}», «{sig_d}/{n_tot}»). No se pone, y no por "
          f"olvido: las {n_tot} "
          "celdas son un CENSO exhaustivo y determinista sobre un solo "
          "conjunto de datos, no una muestra de un universo de caminos. "
          "No hay proceso de muestreo binomial que genere esa fracción, "
          f"así que un Wilson encima supondría {n_tot} Bernoulli "
          "independientes — exactamente el supuesto de independencia que "
          "este informe rechaza dos secciones más arriba, y el mismo "
          "argumento que descarta Bonferroni. La incertidumbre real vive "
          "en los datos, y la llevan los intervalos de cada celda.",
          "- **El desglose por bolsa**, por la razón de la tabla de "
          "no-ejes: meterlo fabricaría significancia, que es el pecado que "
          "esta matriz mide.", "",
          "---", "",
          "## El registro de intentos", "",
          "Regla de la casa: **cada configuración evaluada cuenta como "
          "intento**, incluidas las descartadas. Este frente evaluó "
          f"{n_tot} configuraciones de MEDICIÓN, no de modelo: no eligió "
          "features, no ajustó parámetros y no seleccionó una variante "
          f"ganadora. Por eso NO se suma como {n_tot} intentos al "
          "`N_intentos` "
          "del DSR, que cuenta selección de modelo.", "",
          "**Pero la exposición existe y se declara:** este informe publica "
          "celdas individuales que alguien podría citar sueltas —la de "
          f"ventaja máxima ({v['ventaja_pp'].max():+.1f} pp), o la propia "
          f"celda ancla bajo la regla firmada "
          f"({ANCLA_REGLA['ventaja_pp']:+} pp, p = "
          f"{ANCLA_REGLA['p_exacto']})—. **Citar cualquier celda "
          "individual como "
          "resultado del proyecto mueve `N_intentos` y hay que decirlo en "
          "el mismo párrafo en que se la cita.** El resultado de este "
          "frente es el COCIENTE, el RANGO y la lista de supervivientes; "
          "ninguna celda suelta lo es.", ""]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Matriz completa de bifurcaciones de análisis sobre el "
                    "track record sellado (mode=ro).")
    ap.add_argument("--n-boot", type=int, default=N_BOOT,
                    help="réplicas del bootstrap de clústeres de día")
    ap.add_argument("--sin-escribir", action="store_true")
    args = ap.parse_args(argv)

    mat, ctx = construir_matriz(args.n_boot)
    informe = componer_informe(mat, args.n_boot, ctx)
    if args.sin_escribir:
        print(informe)
        return 0
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(informe)
    mat.to_csv(DESTINO_CSV, index=False)
    v = mat[mat["n"] >= MINIMO_FILAS]
    print(f"[ancla]   reproduce la ventana sellada del README "
          f"(n={ANCLA['n']}, {ANCLA['ventaja_pp']:+} pp, p={ANCLA['p_chi2']})")
    print(f"[matriz]  {len(v)} celdas · "
          f"{int((v['p_dia'] < ALFA).sum())} con p < {ALFA} por clúster de "
          f"día (el titular) · {int((v['p_exacto'] < ALFA).sum())} por "
          f"McNemar exacto · {int((v['p_chi2'] < ALFA).sum())} por chi2")
    print(f"[dmae]    IC pareado excluye el cero en "
          f"{int((v['dmae_hi'] < 0).sum())} celdas")
    print(f"[ventaja] [{v['ventaja_pp'].min():+.1f}, "
          f"{v['ventaja_pp'].max():+.1f}] pp · "
          f"mediana {v['ventaja_pp'].median():+.1f}")
    print(f"[escrito] {os.path.relpath(DESTINO, os.getcwd())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
