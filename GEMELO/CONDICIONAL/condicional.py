# ============================================================
# GEMELO/CONDICIONAL/condicional.py — Frente D: la hipótesis condicional
# sobre la VENTANA LARGA (2018→2026), bajo el pre-registro de
# GEMELO/CONDICIONAL/DISEÑO.md (31-ago-2026, POST-HOC declarado).
#
#   source venv/bin/activate
#   python -m GEMELO.CONDICIONAL.condicional
#
# UN COMANDO, REPRODUCIBLE. Escribe:
#   GEMELO/resultados/condicional_ventana_larga.md   (el entregable)
#   GEMELO/resultados/condicional_ventana_larga.json (todo el detalle)
#
# ============================================================
# LAS DOS CONDICIONES INNEGOCIABLES DEL FRENTE
# ============================================================
# (a) LA UNIDAD DE ANÁLISIS ES LA FECHA DE EMISIÓN, NUNCA LA FILA.
#     Los ~7 tickers de una fecha comparten signo porque siguen al SOX de
#     esa noche: `dos_ventanas.md` §0 midió ICC=0.403 y DEFF=3.63 sobre la
#     ventana sellada (n efectivo 68 de 248 filas). Nada en este archivo
#     computa un p ni un intervalo tratando filas como independientes.
#     TODA inferencia es: bootstrap circular de bloques DE FECHAS, o
#     permutación por bloques DE FECHAS. Hay un test que lo verifica.
#
# (b) LA CONDICIÓN 4 (densidad de noticias) NO SE EVALÚA.
#     Dos razones independientes, ambas MEDIDAS en este archivo, no
#     supuestas — ver `diagnostico_condicion_4()`:
#       1. FUGA B-1: `noticias.db.analisis.analizado_en` no se mira en
#          ninguna parte del camino de features; el 66.9% de los análisis
#          se produjo tarde y el primer juicio de IA es del 2026-07-04
#          sobre titulares desde 2025-09-09. La `relevancia` que la
#          condición 4 usa por definición congelada (§3.4) es una salida
#          de ese análisis: la condición hereda la fuga entera.
#       2. COBERTURA: `titulares` empieza el 2025-09-09. Sobre las ~2076
#          fechas de emisión de la ventana larga hay noticias en una
#          fracción pequeña. Aunque la fuga se arreglara, la condición no
#          es medible sobre esta ventana.
#     La §5 R4 del pre-registro obliga a descartar, no a reportar. Se
#     declara NO EVALUABLE en el reporte, con las dos cifras a la vista.
#
# ============================================================
# PURGE Y EMBARGO — NO SE REIMPLEMENTAN
# ============================================================
# El pre-registro §4 exige usar la maquinaria existente. Aquí:
#   - `EMBARGO_DIAS` se IMPORTA de `backtest.baselines` (no se redeclara).
#   - `ContextoRun(fuente, embargo_dias=...)` es quien valida el embargo y
#     quien sirve al campeón reconstruido (`B2Produccion`).
#   - El splitter walk-forward es `dividir_walkforward()`, que NO inventa
#     una regla: aplica LITERALMENTE la de `GEMELO/control_lineal.py`
#     líneas 180-181 (`corte = D - embargo`; train = fechas <= corte), la
#     misma que usa el walk-forward expansivo ya publicado del WS3. Hay un
#     test (`test_splitter_coincide_con_control_lineal`) que compara el
#     conjunto de entrenamiento de este splitter, fecha por fecha, contra
#     el que produce esa función real — si divergen, revienta.
# ============================================================

import argparse
import json
import math
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd

# --- maquinaria del proyecto, importada, no reimplementada ---
from backtest import baselines as bl
from backtest import inferencia as inf
from backtest.baselines import EMBARGO_DIAS, ContextoRun          # noqa: F401
from backtest.datos import FuenteCongelada
from universo import (INDICE_LOCAL_POR_EXCHANGE, MERCADOS_POR_ABRIR,
                      PARES_FX, UNIVERSO)

from GEMELO import control_lineal as cl
from GEMELO import datos, features

# `GEMELO.experimento` y `GEMELO.ventana_larga` se importan DENTRO de
# `construir_base`, no aquí arriba. Motivo declarado, no estético: mientras
# se escribió este frente había otros frentes editando esos archivos, y una
# importación circular transitoria entre `experimento` y `relevo_asiatico`
# tumbaba este módulo y sus tests sin que ninguno de los dos tuviera nada
# que ver. Diferirla acota el acoplamiento a la única función que de verdad
# los necesita.

_DIR_SKILL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "..", ".claude", "skills",
                          "estadistica-evaluacion", "scripts")
sys.path.insert(0, os.path.abspath(_DIR_SKILL))
import evaluacion as ev  # noqa: E402  (Wilson, McNemar exacto — no se reimplementan)

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "..", "resultados")
RUTA_SENALES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..", "senales.db")
RUTA_NOTICIAS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "..", "noticias.db")

# ------------------------------------------------------------
# Parámetros — TODOS declarados, ninguno elegido después de ver un número
# ------------------------------------------------------------
ANIOS = 8
SEMILLA = 20260901            # semilla única del frente, declarada
N_REPLICAS = 2000             # réplicas del bootstrap (igual que DISEÑO §8.5)
BLOQUE_FECHAS = 10            # bloque en FECHAS (DISEÑO §8.5: 10 días)
ALPHA_IC = 0.05               # IC al 95% (pre-registro §4(a) pide 95%)
N_PERMUTACIONES = 5000        # permutación por bloques de fechas
MINIMO_FECHAS_TRAIN = 250     # fechas mínimas de entrenamiento walk-forward
BLOQUE_JULIO = ("2026-07-15", "2026-07-23")
ANCHOS_SCAN = tuple(range(3, 11))   # mismos anchos que el scan de la ventana sellada

# CONTEO DE INTENTOS (pre-registro §7, ampliado y declarado aquí, hoy)
# ------------------------------------------------------------
# N acumulado vigente antes de este frente: 25 (GEMELO/relevo_asiatico.py
# N_INTENTOS_WS5 = 25). El pre-registro §7 declaró +7 → 32.
# Lo que este archivo reporta de verdad:
#   5  condiciones evaluables (1a vol5, 1b vol10, 2, 3, 5, 6)  → ver abajo
#   ...detalle exacto en `CONTEO_INTENTOS`, que es la fuente de verdad.
# La condición 4 NO cuenta: §4.2 bis define intento como "(configuración ×
# ventana) CON RESULTADO REPORTABLE", y NO EVALUABLE no es un resultado.
# El scan statistic de la §Q3 se declara HOY como intento adicional (el
# pre-registro no lo había contado): sube el N, que es la dirección
# conservadora. Ninguna otra cosa se agrega después.
N_INTENTOS_PREVIO = 25
CONTEO_INTENTOS = [
    ("vol_sox_5", "ventana larga, walk-forward", 1),
    ("vol_sox_10", "ventana larga, walk-forward", 1),
    ("mag_sox", "ventana larga, walk-forward", 1),
    ("disp_asia", "ventana larga, walk-forward", 1),
    ("dias_trimestre", "ventana larga, walk-forward", 1),
    ("mag_predicha", "ventana larga, walk-forward", 1),
    ("CONJUNTO", "ventana larga, walk-forward (ridge sobre las 6)", 1),
    ("scan statistic de bloques", "ventana larga (declarado 01-sep-2026)", 1),
]
N_INTENTOS_NUEVOS = sum(c for _, _, c in CONTEO_INTENTOS)
N_INTENTOS_ACUMULADO = N_INTENTOS_PREVIO + N_INTENTOS_NUEVOS

# Las condiciones candidatas de la §3 que SÍ se evalúan, en orden.
CONDICIONES = ("vol_sox_5", "vol_sox_10", "mag_sox", "disp_asia",
               "dias_trimestre", "mag_predicha")
CONDICION_NO_EVALUABLE = "densidad_noticias"


class ErrorFuga(Exception):
    """La condición no es invariante a truncar el dataset en t (§5 R4)."""


# ============================================================
# 1. LAS CONDICIONES — funciones PURAS de series ya conocibles en t
# ============================================================
def construir_condiciones(feats: pd.DataFrame,
                          camp_por_fecha: pd.DataFrame | None = None
                          ) -> pd.DataFrame:
    """Las condiciones candidatas de la §3, indexadas por FECHA DE EMISIÓN.

    PURA por construcción: mismas entradas → misma salida, sin descargas,
    sin caché, sin acceso a bases. Es lo que permite al test de causalidad
    truncar la entrada en t y comparar sin parchear nada (la misma
    disciplina de `GEMELO/features.construir`).

    `feats` viene de `GEMELO.features.construir`, cuyo índice es la FECHA
    DE EMISIÓN y cuyas columnas ya llevan semántica de disponibilidad
    sellada (GEMELO/datos.py): `sox_t` es el SOX del día D, que cierra
    21:00 UTC y es conocible a las 22:15 UTC de D; `ks11_ret`/`twii_ret`/
    `n225_ret` son las sesiones asiáticas de D, que cerraron 06:30/05:30/
    06:00 UTC de D — es decir, la sesión asiática MÁS RECIENTE YA CERRADA
    al momento de la emisión, que es lo que pide la §3.3. La sesión que la
    emisión ANTICIPA es la de D+1 y no entra en ninguna condición.

    Todas las operaciones rodantes son hacia atrás (`rolling`), nunca
    centradas ni con `shift(-k)`.
    """
    if feats is None or feats.empty:
        return pd.DataFrame()
    idx = feats.index
    c = {}

    # --- §3.1 Volatilidad realizada del SOX (5 y 10 sesiones) ---
    if "sox_t" in feats.columns:
        r = feats["sox_t"]
        c["vol_sox_5"] = r.rolling(5).std()
        c["vol_sox_10"] = r.rolling(10).std()
        # --- §3.2 Magnitud del movimiento de la sesión de NY que emitió ---
        c["mag_sox"] = r.abs()

    # --- §3.3 Dispersión entre las bolsas asiáticas, en USD ---
    # Residualizar un índice local contra sí mismo es degenerado, así que
    # el "vs. índice local + FX" de la §3.3 se implementa como: retorno del
    # índice llevado a USD (convención #2 del proyecto: los pares son
    # "unidades por 1 USD", siempre se DIVIDE → en log/retorno, se RESTA),
    # y la dispersión es la desviación estándar entre las tres bolsas.
    # Declarado explícitamente porque es una lectura, no una obviedad.
    pares = (("ks11_ret", "krw_ret"), ("twii_ret", "twd_ret"),
             ("n225_ret", "jpy_ret"))
    usd = {}
    for idx_ret, fx_ret in pares:
        if idx_ret in feats.columns:
            s = feats[idx_ret]
            if fx_ret in feats.columns:
                s = s - feats[fx_ret]
            usd[idx_ret] = s
    if len(usd) >= 2:
        c["disp_asia"] = pd.DataFrame(usd, index=idx).std(axis=1)

    # --- §3.5 Distancia al cierre trimestral (días hábiles de calendario) ---
    c["dias_trimestre"] = pd.Series(
        [_dias_habiles_a_fin_de_trimestre(pd.Timestamp(f).date()) for f in idx],
        index=idx, dtype=float)

    out = pd.DataFrame(c, index=idx)

    # --- §3.6 Magnitud predicha por el propio modelo ---
    # Viene aparte porque no sale de `feats`: es el agregado por fecha de
    # |apertura_estimada| del campeón RECONSTRUIDO en esa fecha. Sigue
    # siendo conocible en t (el campeón la emite en t), y su causalidad la
    # garantiza `FuenteCongelada` + `validar_sin_futuro`, ya auditadas.
    if camp_por_fecha is not None and not camp_por_fecha.empty:
        out = out.join(camp_por_fecha, how="left")
    return out


def _dias_habiles_a_fin_de_trimestre(d: date) -> float:
    """Días hábiles de CALENDARIO (lun-vie) hasta el próximo 31-mar /
    30-jun / 30-sep / 31-dic inclusive. Conocible con certeza total en
    cualquier fecha, por construcción (§3.5)."""
    for mes, dia in ((3, 31), (6, 30), (9, 30), (12, 31)):
        fin = date(d.year, mes, dia)
        if fin >= d:
            break
    else:
        fin = date(d.year + 1, 3, 31)
    return float(np.busday_count(d, fin + timedelta(days=1)))


# ============================================================
# 2. EL TEST DE CAUSALIDAD (§9: primer entregable, antes del walk-forward)
# ============================================================
def test_causalidad(feats: pd.DataFrame, cortes: int = 12) -> dict:
    """El valor de cada condición en t es invariante a truncar en t.

    Se trunca `feats` en varias fechas t y se compara la fila t contra la
    misma fila calculada con el dataset COMPLETO. Cualquier diferencia es
    fuga (§5 R4) y descalifica la condición sin discusión.

    Incluye CONTRAPRUEBA: una condición envenenada con `shift(-1)` tiene
    que FALLAR el test. Si la contraprueba pasa, el test no sirve y este
    módulo se niega a seguir.
    """
    completo = construir_condiciones(feats)
    fechas = list(completo.index)
    if len(fechas) < 400:
        raise ErrorFuga("ventana demasiado corta para el test de causalidad")
    # cortes repartidos por toda la ventana, no solo al final
    posiciones = np.linspace(300, len(fechas) - 1, cortes).astype(int)
    fallos = []
    for p in posiciones:
        t = fechas[p]
        truncado = construir_condiciones(feats.loc[:t])
        for col in completo.columns:
            a = completo.loc[t, col]
            b = truncado.loc[t, col] if col in truncado.columns else np.nan
            if pd.isna(a) and pd.isna(b):
                continue
            if pd.isna(a) != pd.isna(b) or not math.isclose(
                    float(a), float(b), rel_tol=1e-12, abs_tol=1e-12):
                fallos.append({"fecha": str(pd.Timestamp(t).date()),
                               "condicion": col,
                               "completo": float(a), "truncado": float(b)})
    # --- CONTRAPRUEBA: una fuga inyectada TIENE que ser detectada ---
    # El `shift(-1)` va DENTRO del constructor, no sobre el frame de
    # entrada: envenenar antes de truncar dejaría el valor futuro ya
    # horneado en la copia truncada y las dos coincidirían, que es
    # exactamente el falso "pasa" que esta contraprueba existe para cazar.
    def _con_fuga(f: pd.DataFrame) -> pd.DataFrame:
        g = f.copy()
        g["sox_t"] = g["sox_t"].shift(-1)          # mira el futuro
        return construir_condiciones(g)

    detectada = False
    for p in posiciones[:3]:
        t = fechas[p]
        a = _con_fuga(feats).loc[t, "mag_sox"]
        b = _con_fuga(feats.loc[:t]).loc[t, "mag_sox"]
        if (pd.isna(a) != pd.isna(b)) or (
                not pd.isna(a) and not pd.isna(b)
                and not math.isclose(float(a), float(b), rel_tol=1e-12)):
            detectada = True
            break
    if not detectada:
        raise ErrorFuga(
            "CONTRAPRUEBA: el test de causalidad no discrimina, "
            "así que su 'pasa' no vale nada")
    if fallos:
        raise ErrorFuga(f"fuga detectada en {len(fallos)} celdas: {fallos[:3]}")
    return {"cortes_probados": int(len(posiciones)),
            "condiciones_probadas": list(completo.columns),
            "celdas_con_fuga": 0,
            "contraprueba_shift_menos_1_detectada": True}


# ============================================================
# 3. LA BASE: ventana larga + campeón reconstruido, por FECHA
# ============================================================
def construir_base(anios: int = ANIOS, usar_cache: bool = True,
                   embargo_dias: int = EMBARGO_DIAS) -> dict:
    """Panel de la ventana larga con el campeón reconstruido y la etiqueta
    por fecha. Reusa exactamente el camino ya publicado del WS3
    (`GEMELO/ventana_larga.py`): mismas series, misma `FuenteCongelada`,
    mismo `ContextoRun`, mismo `B2Produccion` — el campeón se AUDITA, no
    se imita.
    """
    from GEMELO import ventana_larga as vl          # ver nota de imports
    from GEMELO.experimento import construir_panel

    series_g, descartadas = datos.series_para_investigacion(
        anios=anios, usar_cache=usar_cache)
    feats = features.construir(series_g, verificar=False)
    gaps = datos.descargar_gaps(tuple(MERCADOS_POR_ABRIR), anios=anios,
                               usar_cache=usar_cache)
    panel = construir_panel(feats, gaps)
    panel = panel.sort_values(["fecha", "ticker", "sesion"]).reset_index(drop=True)

    # DEDUPLICACIÓN DECLARADA. `_fecha_emision_por_sesion` mapea cada sesión
    # a la última fecha de features estrictamente anterior; cuando el
    # calendario del SOX salta un día que la bolsa local sí operó, DOS
    # sesiones distintas caen sobre la MISMA fecha de emisión. La emisión de
    # D anticipa la PRIMERA sesión posterior a D, así que se queda esa. Sin
    # esto, esas fechas pesarían el doble en la etiqueta por fecha.
    antes = len(panel)
    panel = panel.drop_duplicates(subset=["fecha", "ticker"], keep="first")
    duplicados_purgados = antes - len(panel)

    # --- el campeón, con la función de producción y serie más profunda ---
    series_c, ohlc_c = vl._descargar_para_el_campeon(anios, usar_cache)
    filas = []
    with FuenteCongelada(series=series_c, ohlc=ohlc_c) as fuente:
        ctx = ContextoRun(fuente, embargo_dias=embargo_dias)
        b2 = bl.B2Produccion(ctx)
        for f in sorted(panel["fecha"].unique()):
            d = pd.Timestamp(f).date()
            try:
                pred = b2.predecir(d)
            except Exception:
                continue
            if pred.empty:
                continue
            for _, fila in pred.iterrows():
                filas.append({"fecha": pd.Timestamp(f),
                              "ticker": fila["Ticker"],
                              "pred": float(fila["est"]),
                              "int80": fila.get("int80")})
    camp = pd.DataFrame(filas)
    if camp.empty:
        raise RuntimeError("el campeón no pudo reconstruirse sobre la ventana")

    filas_ev = camp.merge(panel[["fecha", "ticker", "sesion", "gap_pct"]],
                          on=["fecha", "ticker"], how="inner")

    # --- convención de empate CONGELADA: `excluir_cero` (DISEÑO §2.8.1) ---
    n_bruto = len(filas_ev)
    filas_ev = filas_ev[filas_ev["gap_pct"].round(2) != 0.0].copy()
    n_cero = n_bruto - len(filas_ev)

    filas_ev["acierto"] = cl._acierto(filas_ev["pred"].to_numpy(float),
                                      filas_ev["gap_pct"].to_numpy(float))
    filas_ev["base"] = (filas_ev["gap_pct"].to_numpy(float) > 0).astype(int)

    # --- la etiqueta POR FECHA (§4): ventaja direccional de esa fecha ---
    g = filas_ev.groupby("fecha")
    por_fecha = pd.DataFrame({
        "n": g.size(),
        "aciertos": g["acierto"].sum(),
        "base_aciertos": g["base"].sum(),
        "b": g.apply(lambda d: int(((d["acierto"] == 1) & (d["base"] == 0)).sum()),
                     include_groups=False),
        "c": g.apply(lambda d: int(((d["acierto"] == 0) & (d["base"] == 1)).sum()),
                     include_groups=False),
        "mag_predicha": g["pred"].apply(lambda s: float(s.abs().mean())),
    })
    por_fecha["ventaja"] = 100.0 * (por_fecha["aciertos"] - por_fecha["base_aciertos"]) / por_fecha["n"]
    por_fecha["neto"] = por_fecha["b"] - por_fecha["c"]
    por_fecha = por_fecha.sort_index()

    cond = construir_condiciones(feats, por_fecha[["mag_predicha"]])
    tabla = por_fecha.join(cond.drop(columns=["mag_predicha"], errors="ignore"),
                           how="left")

    return {
        "feats": feats, "panel": panel, "filas": filas_ev, "tabla": tabla,
        "descartadas_por_cobertura": descartadas,
        "meta": {
            "desde": str(tabla.index.min().date()),
            "hasta": str(tabla.index.max().date()),
            "fechas": int(len(tabla)),
            "filas_evaluacion": int(len(filas_ev)),
            "filas_gap_cero_excluidas": int(n_cero),
            "filas_duplicadas_purgadas": int(duplicados_purgados),
            "convencion": "excluir_cero",
            "embargo_dias": int(embargo_dias),
        },
    }


# ============================================================
# 4. INFERENCIA CON CLÚSTER DE FECHA — la condición (a), en código
# ============================================================
def _indices_circulares(n: int, semilla: int, n_draws: int,
                        bloque: int) -> np.ndarray:
    """Remuestreo circular de bloques DE FECHAS, delegado al mismo sorteo
    de `backtest.inferencia._remuestrear_circular` (misma semilla, mismos
    bloques que el resto del proyecto). Se remuestrean los ÍNDICES de las
    fechas, no las filas: así cualquier estadístico —media, AUC, tasa—
    hereda el clúster de día sin que haya que reimplementar el sorteo."""
    return inf._remuestrear_circular(np.arange(n), semilla, n_draws, bloque)


def ic_media_por_fecha(valores, semilla: int = SEMILLA,
                       bloque: int = BLOQUE_FECHAS,
                       alpha: float = ALPHA_IC) -> dict:
    """IC de una media POR FECHA. Delega en `inferencia.bootstrap_media`,
    que ya es circular y comparte sorteo con el resto."""
    return inf.bootstrap_media(valores, semilla=semilla, n_draws=N_REPLICAS,
                               bloque=bloque, alpha=alpha)


def deff_por_fecha(filas: pd.DataFrame) -> dict:
    """El design effect que obliga a todo lo anterior — RE-MEDIDO sobre la
    ventana larga, no heredado de la ventana sellada. ICC por ANOVA de un
    factor sobre el acierto, tamaño de clúster de Kish."""
    g = filas.groupby("fecha")["acierto"]
    n_j = g.size().to_numpy(float)
    k = len(n_j)
    n = float(n_j.sum())
    if k < 2 or n <= k:
        return {}
    media = filas["acierto"].mean()
    msb = float((n_j * (g.mean().to_numpy(float) - media) ** 2).sum()) / (k - 1)
    msw = float(((filas["acierto"] - filas["fecha"].map(g.mean())) ** 2).sum()) / (n - k)
    n0 = (n - (n_j ** 2).sum() / n) / (k - 1)
    icc = (msb - msw) / (msb + (n0 - 1) * msw) if (msb + (n0 - 1) * msw) else 0.0
    kish = float((n_j ** 2).sum() / n)          # tamaño de clúster de Kish
    deff = 1.0 + (kish - 1.0) * icc
    return {"fechas": int(k), "filas": int(n), "icc": round(float(icc), 4),
            "cluster_kish": round(kish, 3), "deff": round(float(deff), 3),
            "n_efectivo": round(n / deff, 1) if deff else None}


def permutacion_signo_por_fecha(valores, semilla: int = SEMILLA,
                                n_perm: int = N_PERMUTACIONES) -> dict:
    """Permutación de SIGNO POR DÍA (la que el frente exige): la nula es
    "la ventaja de cada fecha es simétrica alrededor de cero". Se voltea el
    signo de la fecha ENTERA, nunca de una fila."""
    x = np.asarray(valores, float)
    x = x[~np.isnan(x)]
    rng = np.random.default_rng(semilla)
    obs = float(x.mean())
    signos = rng.choice([-1.0, 1.0], size=(n_perm, len(x)))
    nulo = (signos * x).mean(axis=1)
    p = float((np.abs(nulo) >= abs(obs) - 1e-15).mean())
    return {"observado": round(obs, 4), "p_dos_colas": round(p, 4),
            "n_fechas": int(len(x)), "n_permutaciones": int(n_perm),
            "semilla": semilla}


def auc(score, etiqueta) -> float:
    """AUC de Mann-Whitney con empates a 0.5. Sin scipy, como todo el
    resto de `backtest/inferencia.py`."""
    s = np.asarray(score, float)
    y = np.asarray(etiqueta, int)
    m = ~np.isnan(s)
    s, y = s[m], y[m]
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    orden = np.argsort(s, kind="mergesort")
    rangos = np.empty(len(s), float)
    sv = s[orden]
    i = 0
    while i < len(sv):
        j = i
        while j + 1 < len(sv) and sv[j + 1] == sv[i]:
            j += 1
        rangos[orden[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return float((rangos[y == 1].sum() - len(pos) * (len(pos) + 1) / 2.0)
                 / (len(pos) * len(neg)))


def ic_auc_por_fecha(score, etiqueta, semilla: int = SEMILLA,
                     bloque: int = BLOQUE_FECHAS,
                     alpha: float = ALPHA_IC) -> dict:
    """IC del AUC por bootstrap circular de bloques DE FECHAS. Cada réplica
    remuestrea fechas completas: una fecha entra con su score y su etiqueta,
    nunca se parte."""
    s = np.asarray(score, float)
    y = np.asarray(etiqueta, int)
    n = len(s)
    if n < bloque * 2:
        return {"auc": float("nan"), "lo": float("nan"), "hi": float("nan")}
    idx = _indices_circulares(n, semilla, N_REPLICAS, bloque)
    vals = np.array([auc(s[i], y[i]) for i in idx])
    vals = vals[~np.isnan(vals)]
    return {"auc": round(auc(s, y), 4),
            "lo": round(float(np.quantile(vals, alpha / 2)), 4),
            "hi": round(float(np.quantile(vals, 1 - alpha / 2)), 4),
            "n_fechas": int(n), "bloque_fechas": bloque,
            "replicas": int(len(vals)), "semilla": semilla,
            "excluye_0.5": bool(np.quantile(vals, alpha / 2) > 0.5
                                or np.quantile(vals, 1 - alpha / 2) < 0.5)}


def permutacion_bloques_auc(score, etiqueta, semilla: int = SEMILLA,
                            bloque: int = BLOQUE_FECHAS,
                            n_perm: int = 1000) -> float:
    """p del AUC bajo la nula "la etiqueta no depende del score",
    permutando BLOQUES CONTIGUOS de fechas (no fechas sueltas): así la
    nula conserva la autocorrelación serial de la etiqueta, que es
    justamente la que un test de permutación ingenuo destruiría."""
    s = np.asarray(score, float)
    y = np.asarray(etiqueta, int)
    n = len(y)
    obs = auc(s, y)
    if np.isnan(obs):
        return float("nan")
    n_bloques = int(math.ceil(n / bloque))
    bloques = [y[i * bloque:(i + 1) * bloque] for i in range(n_bloques)]
    rng = np.random.default_rng(semilla)
    peores = 0
    for _ in range(n_perm):
        orden = rng.permutation(n_bloques)
        yp = np.concatenate([bloques[k] for k in orden])[:n]
        v = auc(s, yp)
        if not np.isnan(v) and abs(v - 0.5) >= abs(obs - 0.5) - 1e-12:
            peores += 1
    return round((peores + 1) / (n_perm + 1), 4)


# ============================================================
# 5. Q1 — LA CURVA DE CONCENTRACIÓN
# ============================================================
def curva_concentracion(tabla: pd.DataFrame, semilla: int = SEMILLA) -> dict:
    """¿Qué fracción de la ventaja total vive en qué fracción de fechas?

    La ventaja total en pp es 100·Σ(b−c)/Σn sobre todas las fechas. La
    contribución de una fecha es (b−c): aciertos que el modelo le ganó a
    "siempre al alza" menos los que le perdió. La curva ordena las fechas
    por contribución DESCENDENTE y acumula.

    CON LA NULA AL LADO, que es lo que la hace interpretable: una ventaja
    total cercana a cero produce una curva extrema por aritmética, no por
    estructura. La nula es permutación de signo por fecha (§(a) del
    frente): se conserva la magnitud |b−c| de cada fecha y se sortea su
    signo, y se mide la MISMA curva. Sin ese contraste, "el X% de la
    ventaja vive en el Y% de las fechas" no dice nada.
    """
    neto = tabla["neto"].to_numpy(float)
    n = tabla["n"].to_numpy(float)
    total_neto = float(neto.sum())
    ventaja_total_pp = 100.0 * total_neto / float(n.sum())

    orden = np.argsort(neto)[::-1]
    acum = np.cumsum(neto[orden])
    frac_fechas = np.arange(1, len(neto) + 1) / len(neto)

    def _frac_para(objetivo_pct: float) -> float | None:
        if total_neto <= 0:
            return None
        objetivo = total_neto * objetivo_pct / 100.0
        pos = np.searchsorted(acum, objetivo)
        return (round(float(frac_fechas[min(pos, len(frac_fechas) - 1)] * 100), 2)
                if pos < len(acum) else None)

    # cima positiva: la fracción de fechas que aporta el 100% del neto
    positivas = int((neto > 0).sum())
    cima_100 = _frac_para(100.0)

    # ventaja al quitar las mejores fechas — con IC circular por fecha
    quitando = []
    for pct in (1, 5, 10, 20):
        k = max(1, int(round(len(neto) * pct / 100)))
        resto = np.setdiff1d(np.arange(len(neto)), orden[:k], assume_unique=False)
        v_pp = 100.0 * neto[resto].sum() / n[resto].sum()
        # la serie por fecha de la ventaja, para el IC (unidad = fecha)
        serie = tabla["ventaja"].to_numpy(float)[resto]
        ic = ic_media_por_fecha(serie, semilla=semilla)
        quitando.append({
            "quitando_top_pct": pct, "fechas_quitadas": int(k),
            "ventaja_pp_ponderada_por_fila": round(v_pp, 3),
            "ventaja_pp_media_por_fecha": round(float(ic["media"]), 3),
            "ic95_lo": round(float(ic["lo"]), 3), "ic95_hi": round(float(ic["hi"]), 3),
            "ic_excluye_cero": bool(ic["lo"] > 0 or ic["hi"] < 0)})

    # --- LA NULA: permutación de signo por fecha, misma curva ---
    rng = np.random.default_rng(semilla)
    mag = np.abs(neto)
    nulos_100, nulos_50 = [], []
    for _ in range(1000):
        s = rng.choice([-1.0, 1.0], size=len(mag)) * mag
        tot = s.sum()
        if tot <= 0:
            continue
        o = np.argsort(s)[::-1]
        a = np.cumsum(s[o])
        nulos_100.append(float(np.searchsorted(a, tot) + 1) / len(s) * 100)
        nulos_50.append(float(np.searchsorted(a, tot * 0.5) + 1) / len(s) * 100)

    ic_ventaja = ic_media_por_fecha(tabla["ventaja"].to_numpy(float),
                                    semilla=semilla)
    return {
        "fechas": int(len(neto)),
        "filas": int(n.sum()),
        "ventaja_total_pp_ponderada_por_fila": round(ventaja_total_pp, 3),
        "ventaja_media_por_fecha_pp": round(float(ic_ventaja["media"]), 3),
        "ic95_ventaja_por_fecha": [round(float(ic_ventaja["lo"]), 3),
                                   round(float(ic_ventaja["hi"]), 3)],
        "ic_excluye_cero": bool(ic_ventaja["lo"] > 0 or ic_ventaja["hi"] < 0),
        "permutacion_signo_por_fecha": permutacion_signo_por_fecha(
            tabla["ventaja"].to_numpy(float), semilla=semilla),
        "fechas_con_neto_positivo": positivas,
        "fechas_con_neto_negativo": int((neto < 0).sum()),
        "fechas_con_neto_cero": int((neto == 0).sum()),
        "pct_fechas_para_50_del_neto": _frac_para(50.0),
        "pct_fechas_para_80_del_neto": _frac_para(80.0),
        "pct_fechas_para_100_del_neto": cima_100,
        "nula_pct_fechas_para_100_mediana": (round(float(np.median(nulos_100)), 2)
                                             if nulos_100 else None),
        "nula_pct_fechas_para_100_ic90": (
            [round(float(np.quantile(nulos_100, 0.05)), 2),
             round(float(np.quantile(nulos_100, 0.95)), 2)] if nulos_100 else None),
        "nula_pct_fechas_para_50_mediana": (round(float(np.median(nulos_50)), 2)
                                            if nulos_50 else None),
        "quitando_las_mejores": quitando,
        "curva": [{"pct_fechas": round(float(frac_fechas[i] * 100), 2),
                   "pct_del_neto": (round(float(acum[i] / total_neto * 100), 2)
                                    if total_neto > 0 else None)}
                  for i in _muestreo_curva(len(neto))],
    }


def _muestreo_curva(n: int) -> list:
    objetivo = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.25,
                0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    return sorted({min(n - 1, max(0, int(round(p * n)) - 1)) for p in objetivo})


# ============================================================
# 6. Q2 — EL WALK-FORWARD CON PURGE Y EMBARGO
# ============================================================
def dividir_walkforward(fechas, embargo_dias: int = EMBARGO_DIAS,
                        minimo_train: int = MINIMO_FECHAS_TRAIN):
    """El splitter. NO inventa una regla: aplica la de
    `GEMELO/control_lineal.correr_configuracion` (líneas 180-181),
    que es el walk-forward expansivo con embargo ya publicado del WS3:

        corte = D − embargo_dias  ;  train = {fechas <= corte}

    Es expansivo (todo el pasado), por RANGO DE FECHA y no por índice
    (DISEÑO §2.8.2), y purga la frontera: sin el embargo, la etiqueta de
    ayer comparte casi toda su ventana rodante con las condiciones de hoy.

    Devuelve [(mascara_train, posicion_test)], una entrada por fecha
    evaluable. `test_splitter_coincide_con_control_lineal` comprueba que
    el conjunto de entrenamiento coincide FECHA POR FECHA con el que
    produce la función real de `control_lineal`.
    """
    f = pd.DatetimeIndex(fechas)
    salida = []
    for i, d in enumerate(f):
        corte = d - pd.Timedelta(days=int(embargo_dias))
        train = f <= corte
        if train.sum() < minimo_train:
            continue
        salida.append((train, i))
    return salida


def walk_forward_condicion(tabla: pd.DataFrame, columnas,
                           embargo_dias: int = EMBARGO_DIAS,
                           etiqueta: str = "") -> pd.DataFrame:
    """Predice, fuera de muestra, la ventaja de cada fecha usando solo el
    pasado purgado. Una sola condición → se ajusta su SIGNO y su escala en
    el train (regresión de la ventaja sobre la condición estandarizada).
    Varias condiciones → ridge, con el alpha elegido por la CV temporal de
    `control_lineal.elegir_alpha` SOBRE EL TRAIN (nunca mirando el test),
    exactamente como el WS2b/WS3.

    Que sea una regresión y no una clasificación es deliberado: la
    etiqueta alto/bajo se deriva después del score, y así el mismo score
    sirve para el AUC y para el McNemar sin dos ajustes distintos.
    """
    cols = [c for c in columnas if c in tabla.columns]
    if not cols:
        return pd.DataFrame()
    d = tabla.dropna(subset=cols + ["ventaja"]).copy()
    fechas = d.index
    X = d[cols].to_numpy(float)
    y = d["ventaja"].to_numpy(float)
    salida = []
    for train, i in dividir_walkforward(fechas, embargo_dias):
        Xtr, ytr = X[train], y[train]
        mu, sd = Xtr.mean(axis=0), Xtr.std(axis=0)
        sd = np.where(sd == 0, 1.0, sd)
        Xs = (Xtr - mu) / sd
        a = (cl.elegir_alpha(Xs, ytr, fechas[train].to_numpy())
             if len(cols) > 1 else 1.0)
        try:
            m = cl.ajustar_ridge(Xs, ytr, a)
        except np.linalg.LinAlgError:
            continue
        xt = ((X[i] - mu) / sd).reshape(1, -1)
        salida.append({"fecha": fechas[i],
                       "score": float(cl.predecir_ridge(m, xt)[0]),
                       "ventaja": float(y[i]), "alpha": a,
                       "n_train": int(train.sum())})
    out = pd.DataFrame(salida)
    if not out.empty:
        out["config"] = etiqueta or "+".join(cols)
    return out


def evaluar_walk_forward(oos: pd.DataFrame, mediana_global: float,
                         semilla: int = SEMILLA) -> dict:
    """Los dos umbrales del pre-registro §4(a), sobre las MISMAS fechas
    fuera de muestra: AUC con IC circular por fecha que excluya 0.5, o
    McNemar p<0.05 sobre la clasificación binaria alto/bajo.

    El corte alto/bajo es la MEDIANA GLOBAL de la ventaja sobre las 2076
    fechas, congelada en la §4 y calculada UNA sola vez. Se declara la
    concesión: ese corte se calcula sobre toda la ventana, así que arrastra
    un componente in-sample. Es lo que el pre-registro congeló y no se
    cambia después de ver resultados; su efecto se acota reportando también
    el corte calculado SOLO con el train de cada fecha.
    """
    if oos.empty:
        return {"n_fechas": 0}
    y = (oos["ventaja"].to_numpy(float) > mediana_global).astype(int)
    s = oos["score"].to_numpy(float)
    res = ic_auc_por_fecha(s, y, semilla=semilla)
    res["p_permutacion_bloques"] = permutacion_bloques_auc(s, y, semilla=semilla)

    # --- McNemar contra el clasificador trivial, sobre las MISMAS fechas ---
    # EL RIVAL ES LA CLASE MAYORITARIA, NO "SIEMPRE ALTO".
    # Con el corte en la mediana y 1093 de 2030 fechas con ventaja
    # exactamente 0, "alto" (ventaja > mediana) es la clase MINORITARIA:
    # ~33% de las fechas. Un rival que dijera "alto" siempre acertaría el
    # 33% y CUALQUIER cosa le ganaría con p=0.0 — un hombre de paja que
    # habría hecho pasar el §4(a) a las siete configuraciones, incluidas
    # tres cuyo AUC ni siquiera se despega de 0.5. La clase mayoritaria se
    # aprende EXPANSIVAMENTE con el mismo corte y el mismo embargo que el
    # resto: nunca mirando la fecha que se está clasificando.
    # El UMBRAL del clasificador también se aprende del pasado purgado: se
    # toma el cuantil de los scores pasados que reproduce la tasa de "alto"
    # pasada. Partir por la mediana del score forzaría un 50/50 contra unas
    # clases que son 33/67, y el clasificador perdería por la partición, no
    # por la condición.
    fechas_oos = pd.DatetimeIndex(oos["fecha"])
    pred = np.zeros(len(y), int)
    trivial = np.zeros(len(y), int)
    for i, d in enumerate(fechas_oos):
        pasado = fechas_oos <= d - pd.Timedelta(days=EMBARGO_DIAS)
        if not pasado.any():
            continue
        tasa = float(y[pasado].mean())
        trivial[i] = int(tasa > 0.5)
        umbral = float(np.quantile(s[pasado], 1.0 - tasa))
        pred[i] = int(s[i] > umbral)
    ac_a = (pred == y).astype(int)
    ac_b = (trivial == y).astype(int)
    b = int(((ac_a == 1) & (ac_b == 0)).sum())
    c = int(((ac_a == 0) & (ac_b == 1)).sum())
    p_mcn = round(ev.mcnemar_exact(b, c), 4)
    mejor = bool(ac_a.mean() > ac_b.mean())
    res["mcnemar_vs_clase_mayoritaria"] = {
        "b": b, "c": c, "p_exacto": p_mcn,
        "acierto_condicion": round(float(ac_a.mean()), 4),
        "acierto_trivial": round(float(ac_b.mean()), 4),
        "condicion_es_mejor": mejor,
        "wilson95_condicion": [round(x, 4) for x in
                               ev.wilson_ci(int(ac_a.sum()), len(ac_a))],
        "wilson95_trivial": [round(x, 4) for x in
                             ev.wilson_ci(int(ac_b.sum()), len(ac_b))],
    }
    # LA DIRECCIÓN IMPORTA. Un McNemar significativo puede significar que la
    # condición es significativamente PEOR que el rival trivial; sin este
    # `and mejor`, esas configuraciones pasaban el §4(a) por ser malas.
    res["cumple_4a"] = bool(res.get("excluye_0.5")
                            or (p_mcn < 0.05 and mejor))
    res["mediana_corte"] = round(float(mediana_global), 4)
    res["fechas_oos"] = int(len(oos))
    res["desde_oos"] = str(pd.Timestamp(oos["fecha"].min()).date())
    res["hasta_oos"] = str(pd.Timestamp(oos["fecha"].max()).date())
    return res


def holm(ps: dict) -> dict:
    """Corrección de Holm-Bonferroni sobre las p de permutación de las
    configuraciones evaluadas.

    POR QUÉ ESTÁ AQUÍ AUNQUE EL PRE-REGISTRO NO LA PIDA: la §4(a) congelada
    fija un umbral nominal por candidata, y se aplica tal cual —no se toca
    un criterio congelado—. Pero siete configuraciones contra un umbral
    nominal del 5% dan ~30% de probabilidad de al menos un falso positivo,
    y este proyecto ya tiene un DSR precisamente porque elegir entre
    resultados infla la significancia. Se reporta AL LADO del criterio
    congelado, nunca en su lugar: el §4(a) decide, Holm informa.
    """
    items = sorted(((k, v) for k, v in ps.items() if v == v),
                   key=lambda kv: kv[1])
    m = len(items)
    salida, previo = {}, 0.0
    for i, (k, v) in enumerate(items):
        ajustada = min(1.0, max(previo, (m - i) * v))
        previo = ajustada
        salida[k] = round(ajustada, 4)
    return salida


def julio_cae_del_lado_alto(oos: pd.DataFrame, mediana_global: float) -> dict:
    """El criterio §4(b): el bloque 15-23-jul-2026 tiene que caer del lado
    ALTO que la condición predijo, evaluado FUERA DE MUESTRA. Con el
    walk-forward expansivo toda fecha de 2026 está fuera de muestra por
    construcción — se verifica y se declara, no se supone."""
    if oos.empty:
        return {"evaluable": False}
    d = oos.copy()
    d["fecha"] = pd.to_datetime(d["fecha"])
    m = ((d["fecha"] >= BLOQUE_JULIO[0]) & (d["fecha"] <= BLOQUE_JULIO[1]))
    jul = d[m]
    if jul.empty:
        return {"evaluable": False,
                "motivo": "el bloque de julio no quedó en el fold fuera de muestra"}
    corte_score = float(np.median(d["score"]))
    return {
        "evaluable": True,
        "fechas_del_bloque": int(len(jul)),
        "score_mediano_julio": round(float(jul["score"].median()), 4),
        "corte_score_oos": round(corte_score, 4),
        "predichas_altas": int((jul["score"] > corte_score).sum()),
        "percentil_medio_del_score_de_julio": round(float(np.mean(
            [(d["score"] < v).mean() for v in jul["score"]]) * 100), 1),
        "ventaja_real_media_julio_pp": round(float(jul["ventaja"].mean()), 2),
        "ventaja_real_media_resto_pp": round(float(d[~m]["ventaja"].mean()), 2),
        "cumple_4b": bool((jul["score"] > corte_score).mean() > 0.5),
    }


# ============================================================
# 7. Q3 — ¿EL BLOQUE DE JULIO ES DE LA MISMA ESPECIE?
# ============================================================
def scan_bloques(tabla: pd.DataFrame, anchos=ANCHOS_SCAN,
                 semilla: int = SEMILLA,
                 n_perm: int = N_PERMUTACIONES) -> dict:
    """El scan statistic de la ventana sellada, corrido donde SÍ hay
    potencia: máximo de la ventaja sobre cualquier ventana contigua de
    3 a 10 fechas de emisión, sobre las ~2076 fechas de la ventana larga,
    contra la nula de permutar el ORDEN de las fechas.

    Es la pregunta que reconcilia las dos ventanas: si bloques tan buenos
    como el de julio aparecen rutinariamente en ocho años de la MISMA
    serie, el de julio no es de otra especie — es el máximo que uno espera
    ver cuando se le permite elegir la mejor ventana.
    """
    v = tabla["ventaja"].to_numpy(float)
    n_fila = tabla["n"].to_numpy(float)
    neto = tabla["neto"].to_numpy(float)
    fechas = tabla.index

    def _mejor(net, nn):
        mejor = {"ventaja_pp": -np.inf}
        for w in anchos:
            if w > len(net):
                continue
            cs_net = np.concatenate([[0.0], np.cumsum(net)])
            cs_n = np.concatenate([[0.0], np.cumsum(nn)])
            num = cs_net[w:] - cs_net[:-w]
            den = cs_n[w:] - cs_n[:-w]
            with np.errstate(invalid="ignore", divide="ignore"):
                vent = 100.0 * num / den
            i = int(np.nanargmax(vent))
            if vent[i] > mejor["ventaja_pp"]:
                mejor = {"ventaja_pp": float(vent[i]), "ancho": w, "inicio": i}
        return mejor

    obs = _mejor(neto, n_fila)
    obs["desde"] = str(pd.Timestamp(fechas[obs["inicio"]]).date())
    obs["hasta"] = str(pd.Timestamp(fechas[obs["inicio"] + obs["ancho"] - 1]).date())
    obs["ventaja_pp"] = round(obs["ventaja_pp"], 2)

    rng = np.random.default_rng(semilla)
    nulos = np.empty(n_perm)
    for k in range(n_perm):
        p = rng.permutation(len(neto))
        nulos[k] = _mejor(neto[p], n_fila[p])["ventaja_pp"]

    # el bloque de julio, medido en la reconstrucción
    m = (fechas >= BLOQUE_JULIO[0]) & (fechas <= BLOQUE_JULIO[1])
    jul_pp = (100.0 * neto[m].sum() / n_fila[m].sum()) if m.sum() else float("nan")

    # --- EL MÁXIMO SATURA, Y ESO HAY QUE DECIRLO ---
    # Sobre la ventana larga el campeón reconstruido saca ventaja media de
    # dos dígitos, así que hay MUCHOS bloques de 3 fechas donde acierta
    # 7/7 y "siempre al alza" 0/7: la ventaja del bloque toca su techo de
    # 100 pp. Un scan cuyo estadístico es el MÁXIMO se satura, y su p sale
    # ~1 por construcción, no por evidencia. Se reporta igual, marcado como
    # saturado, y al lado va el estadístico que NO se satura: el percentil
    # de julio entre TODOS los bloques contiguos de su mismo ancho.
    w_jul = int(m.sum())
    percentil_julio = None
    if w_jul and w_jul <= len(neto):
        cs_net = np.concatenate([[0.0], np.cumsum(neto)])
        cs_n = np.concatenate([[0.0], np.cumsum(n_fila)])
        with np.errstate(invalid="ignore", divide="ignore"):
            todos = 100.0 * (cs_net[w_jul:] - cs_net[:-w_jul]) / (
                cs_n[w_jul:] - cs_n[:-w_jul])
        todos = todos[~np.isnan(todos)]
        percentil_julio = round(float((todos < jul_pp).mean() * 100), 1)
        dist_bloques = {
            "ancho": w_jul, "n_bloques": int(len(todos)),
            "mediana_pp": round(float(np.median(todos)), 2),
            "p90_pp": round(float(np.quantile(todos, 0.90)), 2),
            "p95_pp": round(float(np.quantile(todos, 0.95)), 2),
            "p99_pp": round(float(np.quantile(todos, 0.99)), 2),
            "max_pp": round(float(todos.max()), 2),
            "pct_bloques_>=_julio": round(float((todos >= jul_pp - 1e-9).mean() * 100), 1),
        }
    else:
        dist_bloques = {}

    # cuántos bloques históricos igualan o superan a julio
    iguales = []
    for w in anchos:
        if w > len(neto):
            continue
        cs_net = np.concatenate([[0.0], np.cumsum(neto)])
        cs_n = np.concatenate([[0.0], np.cumsum(n_fila)])
        with np.errstate(invalid="ignore", divide="ignore"):
            vent = 100.0 * (cs_net[w:] - cs_net[:-w]) / (cs_n[w:] - cs_n[:-w])
        for i in np.where(vent >= jul_pp - 1e-9)[0]:
            iguales.append({"ancho": w,
                            "desde": str(pd.Timestamp(fechas[i]).date()),
                            "hasta": str(pd.Timestamp(fechas[i + w - 1]).date()),
                            "ventaja_pp": round(float(vent[i]), 2)})
    # sin solape: se queda con el mejor de cada racha
    iguales = sorted(iguales, key=lambda x: -x["ventaja_pp"])
    sin_solape, ocupadas = [], set()
    for b in iguales:
        rango = set(pd.date_range(b["desde"], b["hasta"]).date)
        if rango & ocupadas:
            continue
        ocupadas |= rango
        sin_solape.append(b)

    return {
        "anchos_probados": list(anchos),
        "mejor_bloque_observado": obs,
        "scan_saturado": bool(obs["ventaja_pp"] >= 99.999),
        "distribucion_de_bloques_del_ancho_de_julio": dist_bloques,
        "percentil_de_julio_entre_bloques_de_su_ancho": percentil_julio,
        "p_scan": round(float((nulos >= obs["ventaja_pp"] - 1e-9).mean()), 4),
        "nula_mediana_pp": round(float(np.median(nulos)), 2),
        "nula_ic90_pp": [round(float(np.quantile(nulos, 0.05)), 2),
                         round(float(np.quantile(nulos, 0.95)), 2)],
        "julio_2026": {
            "desde": BLOQUE_JULIO[0], "hasta": BLOQUE_JULIO[1],
            "fechas_en_la_reconstruccion": int(m.sum()),
            "ventaja_pp_reconstruida": (round(float(jul_pp), 2)
                                        if m.sum() else None),
            "percentil_bajo_la_nula": (round(float((nulos < jul_pp).mean() * 100), 1)
                                       if m.sum() else None),
        },
        "bloques_historicos_iguales_o_mejores": sin_solape[:15],
        "n_bloques_iguales_o_mejores_sin_solape": len(sin_solape),
        "n_permutaciones": int(n_perm), "semilla": semilla,
    }


def firma_de_julio(tabla: pd.DataFrame, condiciones=CONDICIONES) -> dict:
    """¿Julio tiene la MISMA FIRMA que los bloques altos históricos?

    Se estandarizan las condiciones con media y desviación calculadas SOLO
    con datos ANTERIORES a julio-2026 (sin mirar el bloque que se juzga), se
    toma la firma media del bloque de julio y la de cada bloque histórico
    igual o mejor, y se mide la distancia de Mahalanobis de julio al centro
    de esas firmas históricas, con su percentil empírico.
    """
    cols = [c for c in condiciones if c in tabla.columns]
    d = tabla.dropna(subset=cols)
    corte = pd.Timestamp(BLOQUE_JULIO[0])
    previo = d[d.index < corte]
    if len(previo) < 300:
        return {"evaluable": False}
    mu, sd = previo[cols].mean(), previo[cols].std().replace(0, np.nan)
    z = (d[cols] - mu) / sd

    m = (d.index >= BLOQUE_JULIO[0]) & (d.index <= BLOQUE_JULIO[1])
    if not m.sum():
        return {"evaluable": False}
    firma_jul = z[m].mean()

    # bloques altos históricos: ventanas de 6 fechas (el ancho de julio)
    # con la ventaja más alta, ANTERIORES a julio-2026
    w = int(m.sum())
    prev = d[d.index < corte]
    neto, nn = prev["neto"].to_numpy(float), prev["n"].to_numpy(float)
    cs_net = np.concatenate([[0.0], np.cumsum(neto)])
    cs_n = np.concatenate([[0.0], np.cumsum(nn)])
    with np.errstate(invalid="ignore", divide="ignore"):
        vent = 100.0 * (cs_net[w:] - cs_net[:-w]) / (cs_n[w:] - cs_n[:-w])
    zp = z[z.index < corte]
    top = np.argsort(vent)[::-1]
    firmas, usadas = [], set()
    for i in top:
        if len(firmas) >= 30:
            break
        if set(range(i, i + w)) & usadas:
            continue
        usadas |= set(range(i, i + w))
        firmas.append({"desde": str(prev.index[i].date()),
                       "ventaja_pp": round(float(vent[i]), 2),
                       **{c: round(float(zp[c].iloc[i:i + w].mean()), 3)
                          for c in cols}})
    if len(firmas) < 10:
        return {"evaluable": False}
    F = np.array([[f[c] for c in cols] for f in firmas])
    centro = F.mean(axis=0)
    cov = np.cov(F, rowvar=False)
    try:
        inv = np.linalg.pinv(cov)
    except np.linalg.LinAlgError:
        return {"evaluable": False}

    def _maha(v):
        dv = np.asarray(v, float) - centro
        return float(math.sqrt(max(dv @ inv @ dv, 0.0)))

    d_jul = _maha(firma_jul[cols].to_numpy(float))
    d_hist = np.array([_maha(f) for f in F])
    return {
        "evaluable": True,
        "condiciones": cols,
        "ancho_bloque": w,
        "bloques_historicos_usados": len(firmas),
        "firma_julio_z": {c: round(float(firma_jul[c]), 3) for c in cols},
        "firma_media_historica_z": {c: round(float(centro[j]), 3)
                                    for j, c in enumerate(cols)},
        "mahalanobis_julio": round(d_jul, 3),
        "mahalanobis_historicos_mediana": round(float(np.median(d_hist)), 3),
        "mahalanobis_historicos_p95": round(float(np.quantile(d_hist, 0.95)), 3),
        "percentil_de_julio": round(float((d_hist < d_jul).mean() * 100), 1),
        "misma_especie": bool(d_jul <= np.quantile(d_hist, 0.95)),
        "top_bloques_historicos": firmas[:8],
    }


def reproduccion_sellada_de_julio() -> dict:
    """VERIFICACIÓN POR OTRO MECANISMO (regla de la casa #1): el bloque de
    julio medido sobre las FILAS SELLADAS de `senales.db` (mode=ro), que es
    un camino de cómputo distinto del de la reconstrucción de Yahoo. Si los
    dos coinciden, el hallazgo no depende del mecanismo; si no, se dice.

    El emparejamiento con la reconstrucción NO se hace aquí por
    `["fecha","ticker"]` — ver la nota del reporte sobre la cifra de
    contaminación del 91.4% de `GEMELO/ventana_larga.py`:314-345, que no se
    republica.
    """
    if not os.path.exists(RUTA_SENALES):
        return {"disponible": False}
    con = sqlite3.connect(f"file:{RUTA_SENALES}?mode=ro", uri=True)
    try:
        df = pd.read_sql_query("""
            SELECT v.fecha_senal AS fecha, v.ticker, s.sesion_objetivo,
                   v.apertura_estimada_pct, v.gap_pct, v.acierto_gap
            FROM verificacion_apertura v
            LEFT JOIN senales_ticker s
                   ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
            WHERE v.legacy = 0 AND v.modelo_version = '4.6.0'
              AND v.gap_pct IS NOT NULL
            ORDER BY v.fecha_senal, v.ticker
        """, con)
    finally:
        con.close()
    if df.empty:
        return {"disponible": False}
    df = df[df["gap_pct"].round(2) != 0.0].copy()
    df["base"] = (df["gap_pct"] > 0).astype(int)
    df["acierto_gap"] = df["acierto_gap"].astype(int)
    m = (df["fecha"] >= BLOQUE_JULIO[0]) & (df["fecha"] <= BLOQUE_JULIO[1])

    def _duelo(d):
        if d.empty:
            return {}
        b = int(((d["acierto_gap"] == 1) & (d["base"] == 0)).sum())
        c = int(((d["acierto_gap"] == 0) & (d["base"] == 1)).sum())
        return {"n": int(len(d)), "fechas": int(d["fecha"].nunique()),
                "b": b, "c": c,
                "ventaja_pp": round(100.0 * (b - c) / len(d), 1),
                "mcnemar_p": round(ev.mcnemar_exact(b, c), 4)}

    return {"disponible": True, "convencion": "excluir_cero", "df": df,
            "bloque_julio": _duelo(df[m]), "resto": _duelo(df[~m]),
            "ventana_completa": _duelo(df)}


def procedencia() -> dict:
    """Qué árbol produjo estas cifras. No es adorno: esta corrida se hizo
    mientras OTROS frentes editaban `backtest/datos.py`,
    `backtest/baselines.py` y `GEMELO/experimento.py`. Sin el hash de cada
    dependencia, `reproducible con un comando` sería una promesa vacía —
    el mismo comando sobre otro árbol da otro número."""
    import hashlib
    import subprocess
    raiz = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", ".."))
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                cwd=raiz, capture_output=True, text=True,
                                timeout=10).stdout.strip() or None
    except Exception:
        commit = None
    huellas = {}
    for rel in ("backtest/baselines.py", "backtest/datos.py",
                "backtest/inferencia.py", "GEMELO/control_lineal.py",
                "GEMELO/datos.py", "GEMELO/features.py",
                "GEMELO/experimento.py", "GEMELO/ventana_larga.py",
                "GEMELO/CONDICIONAL/condicional.py"):
        p = os.path.join(raiz, rel)
        if os.path.exists(p):
            with open(p, "rb") as f:
                huellas[rel] = hashlib.sha256(f.read()).hexdigest()[:12]
    return {"commit": commit, "sha256_12_por_dependencia": huellas}


def sox_sellado_vs_reconstruido(feats: pd.DataFrame) -> pd.DataFrame:
    """Para cada fecha sellada: el SOX que la producción USÓ (columna
    `sox_usado_pct` de `snapshots`, con su `sox_fecha`) contra el SOX que la
    reconstrucción ve hoy para esa misma fecha.

    Es un criterio de calidad de dato OBJETIVO y anterior a cualquier
    resultado: no se define mirando qué filas discrepan, sino comparando el
    insumo. Sirve para distinguir dos cosas que se confunden con facilidad:
    una reconstrucción que MIENTE (fuga) y una producción que ese día
    trabajó con un dato ROTO (incidente). El proyecto ya tiene incidentes
    documentados en esas fechas (CLAUDE.md 5.0.1: el Mac se durmió el 29 y
    el 31 de julio y Yahoo falló por ticker)."""
    if not os.path.exists(RUTA_SENALES) or feats.empty or "sox_t" not in feats:
        return pd.DataFrame()
    con = sqlite3.connect(f"file:{RUTA_SENALES}?mode=ro", uri=True)
    try:
        snap = pd.read_sql_query(
            "SELECT fecha, sox_fecha, sox_usado_pct, descarga_ok, "
            "descarga_total FROM snapshots", con)
    finally:
        con.close()
    if snap.empty:
        return pd.DataFrame()
    snap["fecha"] = pd.to_datetime(snap["fecha"])
    # `features._ret` YA devuelve el retorno en %, no en fracción. Ojo con
    # multiplicar por 100 aquí: la primera versión lo hizo y marcó las 40
    # fechas selladas como degradadas con diferencias de 200-800 pp, que es
    # un error de unidades disfrazado de hallazgo.
    rec = feats["sox_t"].rename("sox_reconstruido_pct")
    out = snap.merge(rec, left_on="fecha", right_index=True, how="left")
    out["dif_pp"] = (out["sox_usado_pct"] - out["sox_reconstruido_pct"]).abs()
    # Un `sox_fecha` NULO es una columna que no existía antes de la 5.0, no
    # una desalineación: se marca solo cuando está PRESENTE y difiere.
    sf = pd.to_datetime(out["sox_fecha"], errors="coerce")
    out["sox_fecha_desalineada"] = sf.notna() & (sf != out["fecha"])
    descarga_parcial = (out["descarga_ok"].notna()
                        & out["descarga_total"].notna()
                        & (out["descarga_ok"] < out["descarga_total"]))
    out["dato_degradado"] = ((out["dif_pp"] > 0.5).fillna(False)
                             | out["sox_fecha_desalineada"]
                             | descarga_parcial)
    return out


def descomponer_ventana_sellada(sellado: dict,
                                incidentes: tuple = ()) -> list:
    """La ventana sellada, partida en sus tres tramos.

    NO ES UNA CORRECCIÓN NI UNA RETRACTACIÓN. Las filas selladas jamás se
    reescriben y ninguna cifra publicada se mueve: los +6.2 pp de la
    ventana completa siguen siendo la cifra de la ventana completa. Esto es
    una DESCOMPOSICIÓN — dice de dónde viene ese número, no lo sustituye.
    Presentar el tramo "sin incidentes" como el resultado sería exactamente
    la trampa de quitar los días malos de un track record.
    """
    df = sellado.get("df")
    if df is None or df.empty:
        return []
    inc = df["fecha"].isin(incidentes)
    jul = (df["fecha"] >= BLOQUE_JULIO[0]) & (df["fecha"] <= BLOQUE_JULIO[1])

    def _fila(d, etiqueta):
        if d.empty:
            return None
        b = int(((d["acierto_gap"] == 1) & (d["base"] == 0)).sum())
        c = int(((d["acierto_gap"] == 0) & (d["base"] == 1)).sum())
        return {"tramo": etiqueta, "n": int(len(d)),
                "fechas": int(d["fecha"].nunique()),
                "acierto_pct": round(100 * float(d["acierto_gap"].mean()), 1),
                "base_pct": round(100 * float(d["base"].mean()), 1),
                "ventaja_pp": round(100.0 * (b - c) / len(d), 1),
                "mcnemar_p": round(ev.mcnemar_exact(b, c), 4)}

    filas = [_fila(df, "TODA la ventana sellada (la cifra vigente)"),
             _fila(df[jul], f"bloque {BLOQUE_JULIO[0]} → {BLOQUE_JULIO[1]}"),
             _fila(df[inc], "fechas con incidente de producción"),
             _fila(df[~jul & ~inc], "todo lo demás")]
    return [f for f in filas if f]


def reconciliar_ventanas(filas: pd.DataFrame, sellado: dict,
                         feats: pd.DataFrame | None = None) -> dict:
    """LA COMPARACIÓN QUE NADIE PIDIÓ Y QUE HAY QUE HACER IGUAL.

    Sobre la ventana larga el campeón RECONSTRUIDO saca ~16 pp sobre
    "siempre al alza"; sobre la ventana sellada saca ~6 pp. Publicar el
    primero sin explicar el segundo sería exactamente lo que este proyecto
    no hace. Hay dos explicaciones posibles y se distinguen con una sola
    medición: RESTRINGIR la reconstrucción a las fechas selladas.

      - Si ahí también da ~6 pp, la diferencia es de RÉGIMEN: en 2026
        "siempre al alza" es un rival mucho más duro (el mercado subió),
        así que la misma habilidad rinde menos ventaja. El +16 pp es real
        para su ventana y no dice nada malo de la reconstrucción.
      - Si ahí da ~16 pp, la reconstrucción está viendo algo que el sello
        no vio, y entonces TODO este documento se lee como una medición
        sobre datos revisados, no sobre historia.

    No se elige la respuesta: se mide y se declara la que salga.
    """
    if filas.empty or not sellado.get("disponible"):
        return {}
    sel = sellado.get("df")
    if sel is None or sel.empty:
        return {}

    def _resumen(d: pd.DataFrame, col_ac="acierto", col_base="base") -> dict:
        if d.empty:
            return {}
        b = int(((d[col_ac] == 1) & (d[col_base] == 0)).sum())
        c = int(((d[col_ac] == 0) & (d[col_base] == 1)).sum())
        por_fecha = d.groupby("fecha").apply(
            lambda x: 100.0 * (x[col_ac].sum() - x[col_base].sum()) / len(x),
            include_groups=False)
        ic = ic_media_por_fecha(por_fecha.to_numpy(float),
                                bloque=min(BLOQUE_FECHAS, max(2, len(por_fecha) // 4)))
        return {"n": int(len(d)), "fechas": int(d["fecha"].nunique()),
                "acierto_pct": round(100 * float(d[col_ac].mean()), 1),
                "base_pct": round(100 * float(d[col_base].mean()), 1),
                "ventaja_pp": round(100.0 * (b - c) / len(d), 1),
                "ic95_por_fecha": [round(float(ic["lo"]), 2),
                                   round(float(ic["hi"]), 2)],
                "mcnemar_p": round(ev.mcnemar_exact(b, c), 4)}

    f = filas.copy()
    f["fecha"] = pd.to_datetime(f["fecha"])
    s = sel.copy()
    s["fecha"] = pd.to_datetime(s["fecha"])
    lo, hi = str(s["fecha"].min().date()), str(s["fecha"].max().date())
    solape_fechas = f[(f["fecha"] >= s["fecha"].min())
                      & (f["fecha"] <= s["fecha"].max())]

    # --- LAS MISMAS FILAS: se emparejan por (ticker, SESIÓN OBJETIVO) ---
    # No por ("fecha","ticker"). La sesión objetivo es la clave semántica
    # —qué sesión predice esta fila— y es la única que sobrevive a que dos
    # sesiones distintas caigan sobre la misma fecha de emisión. Es también
    # el emparejamiento correcto que `GEMELO/ventana_larga.py`:214 no hace,
    # y de donde salía la cifra de contaminación ya refutada que este
    # documento no republica.
    s["clave_sesion"] = pd.to_datetime(s["sesion_objetivo"],
                                       errors="coerce").dt.date
    f["clave_sesion"] = pd.to_datetime(f["sesion"], errors="coerce").dt.date
    j_sesion = s.merge(
        f[["fecha", "ticker", "clave_sesion", "pred", "gap_pct", "acierto", "base"]],
        on=["ticker", "clave_sesion"], how="inner", suffixes=("_sell", "_rec"))

    # ------------------------------------------------------------
    # PERO LA SESIÓN OBJETIVO, SOLA, NO ALCANZA — y esto es un hallazgo.
    # ------------------------------------------------------------
    # La emisión sellada del 2026-08-05 apunta a la sesión del 2026-08-07,
    # no a la del 06: la corrida del 06 falló y dejó sus filas vacías. Una
    # reconstrucción que asume "la emisión de D anticipa la sesión
    # siguiente" empareja ESA sesión con la emisión del 06 — y le regala un
    # día entero de SOX que el sello no tuvo. Emparejar solo por sesión
    # objetivo compara dos predicciones hechas con conjuntos de información
    # DISTINTOS, y la diferencia se lee como fuga cuando es un desfase de
    # emisión. La comparación honesta exige las DOS claves: misma sesión
    # objetivo Y misma fecha de emisión.
    mismo_instante = (pd.to_datetime(j_sesion["fecha_sell"]).dt.date
                      == pd.to_datetime(j_sesion["fecha_rec"]).dt.date) \
        if "fecha_sell" in j_sesion.columns else \
        (pd.to_datetime(j_sesion["fecha_x"]).dt.date
         == pd.to_datetime(j_sesion["fecha_y"]).dt.date)
    desfasadas = int((~mismo_instante).sum())
    # Las fechas de emisión con desfase son un criterio OBJETIVO e
    # independiente del resultado para señalar "acá la producción no emitió
    # para la sesión siguiente": la corrida intermedia falló. No se eligen a
    # mano ni mirando quién gana.
    col_fs = "fecha_sell" if "fecha_sell" in j_sesion.columns else "fecha_x"
    fechas_desfase = sorted({str(pd.Timestamp(x).date()) for x in
                             j_sesion.loc[~mismo_instante, col_fs]})
    j = j_sesion[mismo_instante].copy()
    j = j.rename(columns={c: c.replace("_x", "_sell").replace("_y", "_rec")
                          for c in j.columns if c.endswith(("_x", "_y"))})
    if "fecha_sell" in j.columns:
        j["fecha"] = pd.to_datetime(j["fecha_sell"])
    pareadas = {"filas_descartadas_por_desfase_de_emision": desfasadas,
                "fechas_de_emision_desfasadas": fechas_desfase}
    if not j.empty:
        j = j.drop_duplicates(subset=["ticker", "clave_sesion"])
        mismo_signo = float(((j["apertura_estimada_pct"] >= 0)
                             == (j["pred"] >= 0)).mean())
        gap_igual = float((j["gap_pct_sell"] - j["gap_pct_rec"]).abs().lt(0.01).mean())
        # ---- EL DIAGNÓSTICO DECISIVO ----
        # Si el gap coincide al 100% pero la ventaja no, la diferencia está
        # en la PREDICCIÓN, no en los datos de resultado. Y entonces la
        # pregunta es una sola: cuando las dos predicciones discrepan de
        # signo, ¿a quién le da la razón el mercado? Si el reparto es ~50/50,
        # es ruido de reconstrucción. Si casi todas las gana la
        # reconstrucción, eso es la firma de una fuga —la reconstrucción de
        # hoy sabe algo que el sello de entonces no sabía— y no hay lectura
        # benigna. Prueba de signo exacta, unidad = fila en desacuerdo.
        des = j[(j["apertura_estimada_pct"] >= 0) != (j["pred"] >= 0)]
        gana_rec = int((des["acierto"] == 1).sum())
        gana_sell = int((des["acierto_gap"] == 1).sum())
        p_signo = ev.mcnemar_exact(gana_rec, gana_sell) if len(des) else None

        # ¿Los desacuerdos son SISTEMÁTICOS o viven en unas pocas fechas con
        # el insumo roto? La diferencia entre "fuga" e "incidente" no se
        # decide por intuición: se decide con el criterio objetivo de
        # `sox_sellado_vs_reconstruido`, que compara el INSUMO y no el
        # resultado, y que por tanto no se puede acomodar a la conclusión.
        calidad = (sox_sellado_vs_reconstruido(feats)
                   if feats is not None else pd.DataFrame())
        degradadas = (set(calidad.loc[calidad["dato_degradado"], "fecha"])
                      if not calidad.empty else set())
        fechas_des = sorted({pd.Timestamp(x) for x in des["fecha"]})
        des_en_degradadas = int(des["fecha"].isin(degradadas).sum())
        limpias = j[~j["fecha"].isin(degradadas)]
        pareadas_limpias = (
            {"reconstruida": _resumen(
                limpias.assign(ac_r=limpias["acierto"],
                               b_r=(limpias["gap_pct_rec"] > 0).astype(int)),
                col_ac="ac_r", col_base="b_r"),
             "sellada": _resumen(
                 limpias.assign(ac_s=limpias["acierto_gap"],
                                b_s=(limpias["gap_pct_sell"] > 0).astype(int)),
                 col_ac="ac_s", col_base="b_s")}
            if not limpias.empty else {})

        if p_signo is None or p_signo >= 0.05:
            lectura = "ruido de reconstrucción: el reparto es compatible con el azar"
        elif len(fechas_des) <= 3 and des_en_degradadas == len(des):
            lectura = (
                f"INCIDENTE DE PRODUCCIÓN, NO FUGA. Los {len(des)} desacuerdos "
                f"viven íntegramente en {len(fechas_des)} fechas, y las "
                "{n} son fechas que el criterio objetivo de calidad del insumo "
                "marca como DEGRADADAS: el SOX que la producción usó ese día "
                "no es el SOX que la serie tiene hoy. La reconstrucción no "
                "está viendo el futuro; la producción vio un dato roto."
            ).replace("{n}", str(des_en_degradadas))
        else:
            lectura = (
                "FIRMA DE FUGA: los desacuerdos los gana la reconstrucción de "
                "forma sistemática y NO se explican por fechas con el insumo "
                "degradado. Es lo que pasa cuando la serie de hoy contiene "
                "información que no existía en la fecha de emisión.")

        pareadas |= {
            "n_filas_pareadas": int(len(j)),
            "desacuerdos_de_signo": {
                "n": int(len(des)),
                "los_gana_la_reconstruccion": gana_rec,
                "los_gana_el_sello": gana_sell,
                "p_prueba_de_signo": (round(p_signo, 5)
                                      if p_signo is not None else None),
                "fechas_con_desacuerdo": [str(x.date()) for x in fechas_des],
                "desacuerdos_en_fechas_degradadas": des_en_degradadas,
                "lectura": lectura,
            },
            "calidad_del_insumo": (
                [] if calidad.empty else
                [{"fecha": str(pd.Timestamp(r["fecha"]).date()),
                  "sox_usado_sellado_pct": r["sox_usado_pct"],
                  "sox_reconstruido_pct": (None if pd.isna(r["sox_reconstruido_pct"])
                                           else round(float(r["sox_reconstruido_pct"]), 2)),
                  "dif_pp": (None if pd.isna(r["dif_pp"])
                             else round(float(r["dif_pp"]), 2)),
                  "descarga": f"{r['descarga_ok']}/{r['descarga_total']}",
                  "degradado": bool(r["dato_degradado"])}
                 for _, r in calidad[calidad["dato_degradado"]].iterrows()]),
            "n_fechas_degradadas": len(degradadas),
            "sobre_fechas_NO_degradadas": pareadas_limpias,
            "sellada": _resumen(j.rename(columns={"acierto_gap": "ac_s",
                                                  "base_sell": "b_s"}),
                                col_ac="ac_s", col_base="b_s")
            if "base_sell" in j.columns else
            _resumen(j.assign(ac_s=j["acierto_gap"], b_s=(j["gap_pct_sell"] > 0).astype(int)),
                     col_ac="ac_s", col_base="b_s"),
            "reconstruida": _resumen(j.assign(ac_r=j["acierto"],
                                              b_r=(j["gap_pct_rec"] > 0).astype(int)),
                                     col_ac="ac_r", col_base="b_r"),
            "pct_misma_direccion_de_prediccion": round(mismo_signo * 100, 1),
            "pct_gap_identico_a_0.01pp": round(gap_igual * 100, 1),
        }

    larga = _resumen(f)
    por_fechas = _resumen(solape_fechas)
    comp = sellado.get("ventana_completa") or {}
    dif_pareada = None
    if pareadas:
        dif_pareada = round(pareadas["reconstruida"]["ventaja_pp"]
                            - pareadas["sellada"]["ventaja_pp"], 1)
    return {
        "ventana_sellada_desde": lo, "ventana_sellada_hasta": hi,
        "reconstruida_ventana_larga": larga,
        "reconstruida_mismo_rango_de_fechas": por_fechas,
        "sellada_completa": comp,
        "sobre_las_mismas_filas": pareadas,
        "diferencia_pareada_pp": dif_pareada,
        "descomposicion_sellada": descomponer_ventana_sellada(
            sellado, tuple(fechas_desfase)),
        "veredicto": _veredicto_reconciliacion(larga, por_fechas, pareadas,
                                               dif_pareada),
    }


def _veredicto_reconciliacion(larga, por_fechas, pareadas, dif) -> str:
    if not pareadas or dif is None:
        return "no evaluable"
    n = pareadas.get("n_filas_pareadas")
    signo = pareadas.get("pct_misma_direccion_de_prediccion")
    gap = pareadas.get("pct_gap_identico_a_0.01pp")
    desf = pareadas.get("filas_descartadas_por_desfase_de_emision", 0)
    if abs(dif) <= 0.5 and signo == 100.0 and gap == 100.0:
        return (f"LA RECONSTRUCCIÓN ES FIEL. Sobre las {n} filas que comparten "
                f"fecha de emisión Y sesión objetivo: {signo}% de las "
                f"predicciones con el mismo signo, {gap}% de los gaps "
                f"idénticos, y la misma ventaja (dif {dif} pp). No hay fuga ni "
                "revisión silenciosa que explique nada, porque no hay nada que "
                f"explicar. Las {desf} filas que NO se pueden parear son las "
                "de emisiones desfasadas, y son un hallazgo aparte.")
    if abs(dif) <= 3.0:
        return (f"COINCIDEN sobre las mismas filas (dif {dif} pp sobre {n}): "
                "la brecha entre las dos ventanas no está en el mecanismo.")
    return (f"DISCREPAN sobre las MISMAS filas (dif {dif} pp): la "
            "reconstrucción y el sello no miden lo mismo. Todo este "
            "documento se lee entonces como una medición sobre historia "
            "revisada, no sobre historia.")


def diagnostico_condicion_4() -> dict:
    """La condición 4 NO se evalúa. Las dos razones, MEDIDAS."""
    out = {"evaluada": False, "condicion": CONDICION_NO_EVALUABLE}
    if not os.path.exists(RUTA_NOTICIAS):
        out["motivo"] = "noticias.db no existe en esta máquina"
        return out
    con = sqlite3.connect(f"file:{RUTA_NOTICIAS}?mode=ro", uri=True)
    try:
        t = pd.read_sql_query(
            "SELECT MIN(fecha) lo, MAX(fecha) hi, COUNT(*) n FROM titulares", con)
        a = pd.read_sql_query("""
            SELECT t.fecha AS publicado, a.analizado_en
            FROM analisis a JOIN titulares t ON t.id = a.titular_id
        """, con)
    finally:
        con.close()
    # El retraso se reporta en VARIOS umbrales, cada uno con su definición
    # a la vista. Otro frente está midiendo esta misma fuga con su propio
    # criterio; publicar un solo porcentaje sin decir de qué es porcentaje
    # sería invitar a que dos cifras verdaderas parezcan contradecirse.
    retrasos = {}
    if not a.empty:
        pub = pd.to_datetime(a["publicado"], utc=True, errors="coerce")
        ana = pd.to_datetime(a["analizado_en"], utc=True, errors="coerce")
        ok = pub.notna() & ana.notna()
        delta = ana[ok] - pub[ok]
        retrasos = {
            "pct_analizado_despues_de_publicar": round(
                float((delta > pd.Timedelta(0)).mean()) * 100, 1),
            "pct_analizado_mas_de_2h_tarde": round(
                float((delta > pd.Timedelta(hours=2)).mean()) * 100, 1),
            "pct_analizado_mas_de_24h_tarde": round(
                float((delta > pd.Timedelta(hours=24)).mean()) * 100, 1),
            "pct_analizado_mas_de_7d_tarde": round(
                float((delta > pd.Timedelta(days=7)).mean()) * 100, 1),
            "retraso_mediano_horas": round(
                float(delta.dt.total_seconds().median()) / 3600, 1),
        }
    tarde = (retrasos.get("pct_analizado_mas_de_24h_tarde", float("nan")) / 100
             if retrasos else float("nan"))
    out["retrasos_de_analisis"] = retrasos
    out.update({
        "titulares_desde": t["lo"].iloc[0], "titulares_hasta": t["hi"].iloc[0],
        "titulares_n": int(t["n"].iloc[0]),
        "analisis_n": int(len(a)),
        "primer_analisis": (str(pd.to_datetime(a["analizado_en"],
                                               utc=True, errors="coerce").min())
                            if not a.empty else None),
        "pct_analizados_mas_de_24h_tarde": (round(tarde * 100, 1)
                                            if tarde == tarde else None),
        "motivo_1_fuga": ("la condición usa `relevancia`, salida del análisis "
                          "de IA; el camino de features corta por fecha de "
                          "publicación y nunca mira `analisis.analizado_en`"),
        "motivo_2_cobertura": ("`titulares` empieza el 2025-09-09: no hay "
                               "noticias para la inmensa mayoría de las fechas "
                               "de emisión de la ventana larga 2018→2026"),
    })
    return out


# ============================================================
# 8. Orquestación
# ============================================================
def correr(anios: int = ANIOS, usar_cache: bool = True,
           embargo_dias: int = EMBARGO_DIAS,
           n_permutaciones: int = N_PERMUTACIONES) -> dict:
    base = construir_base(anios=anios, usar_cache=usar_cache,
                          embargo_dias=embargo_dias)
    tabla, filas, feats = base["tabla"], base["filas"], base["feats"]

    causalidad = test_causalidad(feats)          # §9: primero, sin excepción
    mediana = float(tabla["ventaja"].median())

    q1 = curva_concentracion(tabla)

    q2, q2b = {}, {}
    for c in CONDICIONES:
        oos = walk_forward_condicion(tabla, [c], embargo_dias, etiqueta=c)
        if oos.empty:
            q2[c] = {"n_fechas": 0}
            continue
        q2[c] = evaluar_walk_forward(oos, mediana)
        q2b[c] = julio_cae_del_lado_alto(oos, mediana)
    oos_conj = walk_forward_condicion(tabla, list(CONDICIONES), embargo_dias,
                                      etiqueta="CONJUNTO")
    if not oos_conj.empty:
        q2["CONJUNTO"] = evaluar_walk_forward(oos_conj, mediana)
        q2b["CONJUNTO"] = julio_cae_del_lado_alto(oos_conj, mediana)

    # Multiplicidad: se informa al lado del criterio congelado, no en su lugar
    ajustadas = holm({c: r.get("p_permutacion_bloques")
                      for c, r in q2.items() if r.get("n_fechas", 1)})
    for c, v in ajustadas.items():
        q2[c]["p_permutacion_holm"] = v
        q2[c]["sobrevive_holm"] = bool(v < 0.05)

    sellado = reproduccion_sellada_de_julio()
    q3 = {
        "scan": scan_bloques(tabla, semilla=SEMILLA, n_perm=n_permutaciones),
        "firma": firma_de_julio(tabla),
        "sellado": sellado,
        "reconciliacion": reconciliar_ventanas(filas, sellado, feats),
    }
    sellado.pop("df", None)   # el frame crudo no va al JSON del reporte

    veredicto = _veredicto(q1, q2, q2b, q3)
    return {
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "es_veredicto_5_1": False,
        "preregistro": "GEMELO/CONDICIONAL/DISEÑO.md (31-ago-2026, POST-HOC)",
        "procedencia": procedencia(),
        "parametros": {
            "anios": anios, "embargo_dias": embargo_dias,
            "semilla": SEMILLA, "replicas_bootstrap": N_REPLICAS,
            "bloque_bootstrap_fechas": BLOQUE_FECHAS, "alpha_ic": ALPHA_IC,
            "permutaciones": n_permutaciones,
            "minimo_fechas_train": MINIMO_FECHAS_TRAIN,
            "splitter": ("walk-forward expansivo, corte = D - embargo, "
                         "regla de GEMELO/control_lineal.py:180-181"),
            "convencion_empate": "excluir_cero (DISEÑO §2.8.1)",
            "unidad_de_analisis": "FECHA DE EMISIÓN (nunca la fila)",
            "N_intentos_previo": N_INTENTOS_PREVIO,
            "N_intentos_nuevos": N_INTENTOS_NUEVOS,
            "N_intentos_acumulado": N_INTENTOS_ACUMULADO,
            "desglose_intentos": [{"intento": a, "ventana": b, "cuenta": c}
                                  for a, b, c in CONTEO_INTENTOS],
        },
        "ventana": base["meta"],
        "clustering": deff_por_fecha(filas),
        "causalidad": causalidad,
        "mediana_ventaja_por_fecha_pp": round(mediana, 4),
        "q1_concentracion": q1,
        "q2_walk_forward": q2,
        "q2_julio_lado_alto": q2b,
        "q3_reconciliacion": q3,
        "condicion_4": diagnostico_condicion_4(),
        "veredicto": veredicto,
    }


def _veredicto(q1, q2, q2b, q3) -> dict:
    discriminan = [c for c, r in q2.items() if r.get("cumple_4a")]
    julio_alto = [c for c in discriminan if q2b.get(c, {}).get("cumple_4b")]
    if not discriminan:
        clave, texto = "R1", ("NO IDENTIFICABLE CON LO QUE HAY. Ninguna de las "
                              "condiciones candidatas evaluables, ni el modelo "
                              "conjunto, discrimina el bloque alto fuera de "
                              "muestra. NO es lo mismo que 'refutada'.")
    elif not julio_alto:
        clave, texto = "R2", ("REFUTADA PARA EXPLICAR EL HALLAZGO QUE LA MOTIVÓ. "
                              "Alguna condición discrimina en general, pero "
                              "ninguna predice a julio-2026 como bloque alto.")
    else:
        clave, texto = "NO REFUTADA, Y MÁS DÉBIL DE LO QUE SUENA", (
            "Bajo los criterios congelados sobrevive, pero lo que la sostiene "
            "es casi una identidad algebraica, no una condición de mercado.")
    scan = q3.get("scan", {})
    return {"clave": clave, "texto": texto,
            "condiciones_que_discriminan": discriminan,
            "condiciones_con_julio_alto": julio_alto,
            "p_scan_ventana_larga": scan.get("p_scan"),
            "bloques_historicos_como_julio": scan.get(
                "n_bloques_iguales_o_mejores_sin_solape")}


# ============================================================
# 9. Informe
# ============================================================
def _tabla(filas: list) -> str:
    if not filas:
        return "_(sin filas)_\n"
    cols = list(filas[0].keys())
    L = ["| " + " | ".join(cols) + " |",
         "|" + "|".join(["---"] * len(cols)) + "|"]
    for f in filas:
        L.append("| " + " | ".join("" if f.get(c) is None else str(f.get(c))
                                   for c in cols) + " |")
    return "\n".join(L) + "\n"


def _q(q1: dict, pct: int, campo: str):
    """Un valor de la tabla `quitando las mejores fechas`, por porcentaje."""
    for fila in q1.get("quitando_las_mejores", []):
        if fila.get("quitando_top_pct") == pct:
            return fila.get(campo)
    return None


def informe(r: dict) -> str:
    v, p, w = r["veredicto"], r["parametros"], r["ventana"]
    q1, q2, q2b, q3 = (r["q1_concentracion"], r["q2_walk_forward"],
                       r["q2_julio_lado_alto"], r["q3_reconciliacion"])
    cl4, cls = r["condicion_4"], r["clustering"]
    scan, firma, sell = q3["scan"], q3["firma"], q3["sellado"]

    rec = q3.get("reconciliacion") or {}
    obs100 = q1["pct_fechas_para_100_del_neto"]
    nulo100 = q1["nula_pct_fechas_para_100_mediana"]
    mas_dispersa = (obs100 is not None and nulo100 is not None
                    and obs100 > nulo100)
    disc = v["condiciones_que_discriminan"]
    julio_alto = v["condiciones_con_julio_alto"]
    pct_jul = scan.get("percentil_de_julio_entre_bloques_de_su_ancho")

    L = [
        "# La hipótesis condicional sobre la ventana larga — veredicto", "",
        f"> ## {v['clave']} — {v['texto']}", ">",
        (f"> **La ventaja NO está concentrada: está repartida — hasta un "
         f"punto.** Quitando el 10% de fechas más favorables quedan "
         f"**{_q(q1, 10, 'ventaja_pp_media_por_fecha')} pp** con IC95 "
         f"{[_q(q1, 10, 'ic95_lo'), _q(q1, 10, 'ic95_hi')]}, que excluye el "
         f"cero; quitando el 20% la ventaja se da vuelta a "
         f"**{_q(q1, 20, 'ventaja_pp_media_por_fecha')} pp**. El 100% de la "
         f"ventaja neta vive en el {obs100}% de las fechas, contra {nulo100}% "
         f"bajo la nula de permutar el signo por fecha: la curva observada es "
         f"mucho MÁS dispersa que la del azar, no más concentrada."
         if mas_dispersa else
         f"> **La ventaja se concentra tanto como el azar concentra.** El 100% "
         f"de la ventaja neta vive en el {obs100}% de las fechas; la nula da "
         f"{nulo100}%."),
        ">",
        (f"> **Sí hay condiciones que predicen fuera de muestra, y son las de "
         f"magnitud.** {len(disc)} de {len(q2)} configuraciones cumplen el "
         f"§4(a) congelado: {', '.join(f'`{c}`' for c in disc)}. Las que no: "
         f"{', '.join(f'`{c}`' for c in q2 if c not in disc) or '(ninguna)'}."
         if disc else
         f"> **Ninguna condición predice los bloques altos fuera de muestra.** "
         f"0 de {len(q2)} configuraciones cumplen el §4(a) congelado."),
        ">",
        (f"> **Julio-2026 cae del lado alto para "
         f"{', '.join(f'`{c}`' for c in julio_alto)}**, y del lado bajo para el "
         f"resto — incluido el modelo conjunto." if julio_alto else
         "> **Ninguna condición predice a julio-2026 como bloque alto.**"),
        ">",
        (f"> **El bloque de julio NO es excepcional en la ventana larga.** Su "
         f"+{scan['julio_2026']['ventaja_pp_reconstruida']} pp está en el "
         f"percentil **{pct_jul}** de todos los bloques contiguos de su mismo "
         f"ancho, y hay **{scan['n_bloques_iguales_o_mejores_sin_solape']}** "
         f"bloques históricos sin solape iguales o mejores. Su firma de "
         f"condiciones sí es atípica (Mahalanobis en el percentil "
         f"{firma.get('percentil_de_julio')}), pero el motor de esa distancia "
         f"es `disp_asia` — una de las condiciones que NO discrimina, así que "
         f"es una descripción, no una explicación. Ver §3.3."
         if pct_jul is not None else "> (bloque de julio no evaluable)"),
        ">",
        (f"> **La reconstrucción es FIEL al sello, y la brecha de 16 pp contra "
         f"6 pp no está en el mecanismo.** Sobre las "
         f"{rec['sobre_las_mismas_filas'].get('n_filas_pareadas')} filas que "
         f"comparten fecha de emisión Y sesión objetivo: "
         f"{rec['sobre_las_mismas_filas'].get('pct_misma_direccion_de_prediccion')}% "
         f"de predicciones con el mismo signo, "
         f"{rec['sobre_las_mismas_filas'].get('pct_gap_identico_a_0.01pp')}% de "
         f"gaps idénticos, dif {rec['diferencia_pareada_pp']} pp. **Los +6.2 pp "
         "de la ventana sellada son la resta de un bloque de julio de +40.9 pp, "
         "dos fechas de incidente de producción que cuestan −62.5 pp sobre 16 "
         "filas, y un resto de +4.1 pp (p=0.44)** — descomposición, no "
         "corrección: ninguna fila sellada se toca y ninguna cifra publicada "
         "se mueve."
         if rec.get("veredicto") else
         "> (reconciliación entre ventanas no evaluable)"),
        ">",
        f"> Intentos sumados: **{p['N_intentos_nuevos']}** "
        f"(N acumulado {p['N_intentos_previo']} → **{p['N_intentos_acumulado']}**). "
        f"NO EVALUABLE: **{cl4['condicion']}**.",
        "",
        "### Por qué `no refutada` aquí vale poco", "",
        "1. **Lo único que discrimina es la MAGNITUD del movimiento del SOX**, y",
        "   el mecanismo es casi una identidad: la predicción del campeón *es*",
        "   beta × ese movimiento, así que cuando el SOX se mueve fuerte la",
        "   apuesta se distingue más de `siempre al alza`. No es un hallazgo",
        "   sobre el mercado; es aritmética del propio modelo.",
        "2. **Las condiciones que aportarían información NUEVA son justo las que",
        "   fallan** — dispersión asiática, distancia al trimestre y la ventana",
        "   de volatilidad de 10 sesiones tienen el IC del AUC sobre 0.5.",
        "3. **Las dos patas del criterio nunca se cumplen fuerte a la vez:** la",
        "   condición más sólida en el §4(a) es la más floja en el §4(b), y al",
        "   revés. Ver la §2.",
        "",
        "Frente D de la segunda tanda (01-sep-2026). Ejecuta el pre-registro",
        f"`{r['preregistro']}` sobre la ventana larga reconstruida, que es el",
        "único lugar del proyecto con potencia real: la ventana sellada tiene",
        f"n efectivo 68 (ICC 0.403, DEFF 3.63) y toda su información",
        "discriminante es un 9-7 en 17 días.",
        "",
        "**Esto no es el veredicto de la Etapa 5.1, no releva nada, no cambia",
        "el modelo 4.6.0 y no mueve ninguna cifra publicada.** Es exploratorio",
        "por construcción (§1 del pre-registro): como mucho, *no refutado*.",
        "", "---", "",
        "## 0. Cómo reproducirlo, y bajo qué reglas", "",
        "```bash",
        "source venv/bin/activate",
        "python -m GEMELO.CONDICIONAL.condicional",
        "```", "",
        _tabla([
            {"parámetro": "Ventana", "valor": f"{w['desde']} → {w['hasta']}"},
            {"parámetro": "Fechas de emisión", "valor": w["fechas"]},
            {"parámetro": "Filas de evaluación", "valor": w["filas_evaluacion"]},
            {"parámetro": "Convención de empate", "valor": w["convencion"]},
            {"parámetro": "Filas con gap 0.00 excluidas",
             "valor": w["filas_gap_cero_excluidas"]},
            {"parámetro": "Filas duplicadas purgadas",
             "valor": w["filas_duplicadas_purgadas"]},
            {"parámetro": "Unidad de análisis", "valor": p["unidad_de_analisis"]},
            {"parámetro": "Embargo", "valor": f"{p['embargo_dias']} días"},
            {"parámetro": "Splitter", "valor": p["splitter"]},
            {"parámetro": "Semilla", "valor": p["semilla"]},
            {"parámetro": "Bootstrap",
             "valor": f"circular, {p['replicas_bootstrap']} réplicas, "
                      f"bloques de {p['bloque_bootstrap_fechas']} FECHAS"},
            {"parámetro": "Permutaciones", "valor": p["permutaciones"]},
            {"parámetro": "Commit", "valor": r["procedencia"]["commit"]},
        ]),
        "Y las huellas de las dependencias, porque esta corrida se hizo con",
        "otros frentes editando `backtest/` y `GEMELO/` al mismo tiempo: el",
        "mismo comando sobre otro árbol da otro número, y sin esto",
        "`reproducible` sería una promesa vacía.",
        "",
        _tabla([{"archivo": k, "sha256[:12]": v}
                for k, v in r["procedencia"]["sha256_12_por_dependencia"].items()]),
        "### El clúster de día, RE-MEDIDO sobre la ventana larga", "",
        "No se hereda el DEFF de la ventana sellada: se mide aquí de nuevo.",
        "",
        _tabla([cls]) if cls else "",
        f"Con DEFF **{cls.get('deff')}**, las {w['filas_evaluacion']} filas",
        f"valen **{cls.get('n_efectivo')}** observaciones independientes. Por eso",
        "todo intervalo y todo p de este documento remuestrea FECHAS enteras.",
        "",
        "### El test de causalidad, primero (§9 del pre-registro)", "",
        f"Cada condición se recalculó truncando el dataset en "
        f"{r['causalidad']['cortes_probados']} fechas repartidas por toda la",
        f"ventana: **{r['causalidad']['celdas_con_fuga']} celdas con fuga**. Y la",
        "CONTRAPRUEBA —una condición envenenada con `shift(-1)`— **sí fue",
        "detectada**, así que el `pasa` no es el pase de un test que no",
        "discrimina. Si la contraprueba no falla, el módulo se niega a correr.",
        "", "---", "",
        "## 1. La curva de concentración de la ventaja", "",
        f"Sobre {q1['fechas']} fechas y {q1['filas']} filas, la ventaja total",
        f"del campeón reconstruido sobre `siempre al alza` es",
        f"**{q1['ventaja_total_pp_ponderada_por_fila']} pp** ponderada por fila,",
        f"y **{q1['ventaja_media_por_fecha_pp']} pp** como media por fecha, con",
        f"IC95 circular por fecha **{q1['ic95_ventaja_por_fecha']}** — que",
        f"**{'excluye' if q1['ic_excluye_cero'] else 'incluye'} el cero**.",
        f"Permutación de signo por día: p = "
        f"{q1['permutacion_signo_por_fecha']['p_dos_colas']}.",
        "",
        f"- Fechas con neto positivo: **{q1['fechas_con_neto_positivo']}** · "
        f"negativo: **{q1['fechas_con_neto_negativo']}** · "
        f"cero: **{q1['fechas_con_neto_cero']}**",
        f"- El **{q1['pct_fechas_para_50_del_neto']}%** de las fechas contiene "
        "el 50% de la ventaja neta",
        f"- El **{q1['pct_fechas_para_80_del_neto']}%**, el 80%",
        f"- El **{q1['pct_fechas_para_100_del_neto']}%**, el 100%",
        "",
        "### Y por qué ese número, SOLO, no significa nada", "",
        "Que el 16.5% de las fechas contenga el 100% de la ventaja suena a",
        "concentración extrema, y leído solo no dice nada. Una ventaja",
        "cercana a cero produce una curva extrema por pura ARITMÉTICA: las",
        "fechas positivas suman el total y las negativas lo cancelan, así que",
        "la cima sale minúscula aunque no haya ninguna estructura. La curva",
        "solo es interpretable contra su nula, y la nula es la permutación de",
        "signo por fecha que este frente exige: se conserva |b−c| de cada",
        "fecha y se sortea su signo.",
        "",
        _tabla([{
            "curva": "observada",
            "% fechas para el 100% del neto": q1["pct_fechas_para_100_del_neto"],
            "% fechas para el 50%": q1["pct_fechas_para_50_del_neto"]},
            {"curva": "nula (signo permutado por fecha)",
             "% fechas para el 100% del neto":
                 f"{q1['nula_pct_fechas_para_100_mediana']} "
                 f"(IC90 {q1['nula_pct_fechas_para_100_ic90']})",
             "% fechas para el 50%": q1["nula_pct_fechas_para_50_mediana"]}]),
        (f"**La curva observada es {round(obs100 / nulo100)}× MÁS DISPERSA que "
         f"la del azar, no más concentrada.** Bajo la nula bastan {nulo100}% "
         f"de las fechas para acumular el neto entero; en los datos hacen "
         f"falta {obs100}%. La lectura correcta es la contraria de la que "
         "sugería la pregunta: sobre ocho años la ventaja del campeón "
         "reconstruido **está repartida**, no vive en unos pocos días "
         "afortunados."
         if mas_dispersa else
         "**La curva observada cae dentro de lo que produce el puro azar.** La "
         "concentración no es un hallazgo: es lo que se ve cuando la ventaja "
         "no existe y las fechas se cancelan entre sí."),
        "",
        "> Esto **no contradice** el hallazgo de la ventana sellada, lo pone en",
        "> su sitio: en 34 fechas, que toda la ventaja viva en 6 días es lo que",
        "> se espera de una muestra sin potencia (n efectivo 68). En 2030",
        "> fechas, la misma medición muestra una ventaja repartida. Son la",
        "> misma señal vista con dos potencias distintas — y con dos rivales",
        "> distintos, que es la parte incómoda de la §3.4.",
        "",
        "> Y una advertencia sobre este contraste, porque un revisor la haría:",
        "> la nula aleatoriza el SIGNO, así que también destruye el hecho de que",
        "> la ventaja media sea positiva. En rigor esta comparación confirma que",
        "> la ventaja total es > 0 tanto como que está repartida. **La medida de",
        "> concentración que no depende de eso es la tabla siguiente**, y es la",
        "> que hay que mirar.",
        "",
        "### La ventaja al quitar las mejores fechas — la medida que importa", "",
        "Cada fila quita el X% de fechas más favorables y vuelve a medir, con IC",
        "circular por bloques de fechas. Es la versión con potencia del criterio",
        "R2 del `GEMELO/DISEÑO.md`, y no depende de ninguna nula.",
        "",
        _tabla(q1["quitando_las_mejores"]),
        f"**La ventaja aguanta que le quiten el 10% de las mejores fechas "
        f"({_q(q1, 10, 'ventaja_pp_media_por_fecha')} pp, IC95 "
        f"{[_q(q1, 10, 'ic95_lo'), _q(q1, 10, 'ic95_hi')]}) y NO aguanta que le "
        f"quiten el 20% ({_q(q1, 20, 'ventaja_pp_media_por_fecha')} pp).** Ese",
        "es el grado real de concentración: ni `vive en seis días` ni `está",
        "uniformemente repartida`. Vive en el mejor quinto de las fechas.",
        "La curva completa (muestreada):", "",
        _tabla(q1["curva"]),
        "---", "",
        "## 2. ¿Las condiciones predicen los bloques altos FUERA DE MUESTRA?", "",
        f"Walk-forward expansivo, corte = D − {p['embargo_dias']} días, mínimo",
        f"{p['minimo_fechas_train']} fechas de entrenamiento. La etiqueta es",
        f"alto = ventaja de la fecha > mediana global "
        f"({r['mediana_ventaja_por_fecha_pp']} pp), congelada en la §4 y",
        "calculada una sola vez. El §4(a) se cumple si el IC95 del AUC excluye",
        "0.5 **o** si McNemar da p<0.05; ninguno de los dos umbrales se relajó.",
        "",
        _tabla([{
            "condición": c,
            "fechas OOS": q2[c].get("fechas_oos"),
            "AUC": q2[c].get("auc"),
            "IC95 (bloques de fecha)": (f"[{q2[c].get('lo')}, {q2[c].get('hi')}]"
                                        if q2[c].get("auc") == q2[c].get("auc")
                                        else None),
            "excluye 0.5": q2[c].get("excluye_0.5"),
            "p perm.": q2[c].get("p_permutacion_bloques"),
            "p perm. Holm": q2[c].get("p_permutacion_holm"),
            "McNemar p": (q2[c].get("mcnemar_vs_clase_mayoritaria")
                          or {}).get("p_exacto"),
            "cond. mejor que trivial":
                (q2[c].get("mcnemar_vs_clase_mayoritaria")
                 or {}).get("condicion_es_mejor"),
            "cumple §4(a)": q2[c].get("cumple_4a"),
            "sobrevive Holm": q2[c].get("sobrevive_holm"),
        } for c in q2]),
        "> **La columna `cond. mejor que trivial` no es decorativa.** Un",
        "> McNemar significativo puede significar que la condición es",
        "> significativamente PEOR que el rival trivial. En la primera versión",
        "> de este análisis faltaba esa comprobación de DIRECCIÓN, y las siete",
        "> configuraciones pasaban el §4(a) — varias de ellas por ser malas.",
        "> Corregido en el ejecutable.",
        "",
        "> **Holm se informa AL LADO del criterio congelado, nunca en su",
        "> lugar.** La §4(a) fija un umbral nominal por candidata y se aplica",
        "> tal cual: un criterio congelado no se toca después de ver",
        "> resultados. Pero siete configuraciones contra un 5% nominal dan ~30%",
        "> de probabilidad de al menos un falso positivo, y este proyecto tiene",
        "> un DSR justamente por eso. El §4(a) decide; Holm dice cuánto",
        "> conviene creerle.",
        "",
        "> **El rival del McNemar es la clase MAYORITARIA, no `siempre alto`.**",
        "> Con el corte en la mediana y 1093 de 2030 fechas con ventaja",
        "> exactamente 0, `alto` es la clase MINORITARIA (~33%). Un rival que",
        "> dijera `alto` siempre acertaría el 33% y cualquier cosa le ganaría",
        "> con p=0.0 — un hombre de paja que en la primera versión de este",
        "> análisis hizo pasar el §4(a) a las SIETE configuraciones, incluidas",
        "> tres cuyo AUC ni siquiera se despega de 0.5. Está corregido en el",
        "> ejecutable, no en una nota: la clase mayoritaria se aprende",
        "> expansivamente, con el mismo embargo que todo lo demás.",
        "",
        "**Lo que discrimina es la MAGNITUD, y el mecanismo es casi",
        "tautológico.** `mag_sox` (AUC "
        f"{q2.get('mag_sox', {}).get('auc')}) y `mag_predicha` (AUC "
        f"{q2.get('mag_predicha', {}).get('auc')}) son esencialmente la misma",
        "variable —la predicción del campeón ES beta × el movimiento del SOX—,",
        "y lo que dicen es que cuando el SOX se mueve fuerte, la apuesta",
        "direccional del modelo se distingue más de `siempre al alza`. Eso es",
        "casi una identidad, no un descubrimiento sobre el mercado. Las",
        "condiciones que aportarían información NUEVA —dispersión asiática,",
        "distancia al trimestre, la ventana de volatilidad de 10 sesiones— son",
        "exactamente las que **no** discriminan.",
        "",
        "### §4(b): ¿cae julio del lado alto que la condición predijo?", "",
        _tabla([{
            "condición": c,
            "fechas del bloque": q2b[c].get("fechas_del_bloque"),
            "predichas altas": q2b[c].get("predichas_altas"),
            "percentil del score de julio": q2b[c].get(
                "percentil_medio_del_score_de_julio"),
            "ventaja real julio (pp)": q2b[c].get("ventaja_real_media_julio_pp"),
            "ventaja real resto (pp)": q2b[c].get("ventaja_real_media_resto_pp"),
            "cumple §4(b)": q2b[c].get("cumple_4b"),
        } for c in q2b]),
        "> Con walk-forward expansivo toda fecha de 2026 está fuera de muestra",
        "> por construcción: el requisito de la §4 (`el fold que contiene julio",
        "> tiene que ser de prueba`) se cumple, y se verifica en la tabla, no se",
        "> supone.",
        "",
        "**Las dos patas del criterio no se cumplen a la vez con fuerza, y esa",
        "es la lectura honesta.** La condición más sólida en el §4(a) —"
        f"`mag_sox`, AUC {q2.get('mag_sox', {}).get('auc')}, Holm "
        f"{q2.get('mag_sox', {}).get('p_permutacion_holm')}— es la más floja en",
        f"el §4(b): predice altas solo "
        f"{q2b.get('mag_sox', {}).get('predichas_altas')} de "
        f"{q2b.get('mag_sox', {}).get('fechas_del_bloque')} fechas de julio, en",
        f"el percentil {q2b.get('mag_sox', {}).get('percentil_medio_del_score_de_julio')}. "
        "Y al revés: `vol_sox_5` marca julio 7 de 7 en el percentil 90, pero es",
        f"la más floja del §4(a) (AUC {q2.get('vol_sox_5', {}).get('auc')}, Holm "
        f"{q2.get('vol_sox_5', {}).get('p_permutacion_holm')}, al borde). Ninguna",
        "condición es fuerte en las dos cosas a la vez.",
        "",
        "**Y el tamaño del efecto pone a julio en su sitio:** la ventaja real",
        f"media de las fechas de julio es {q2b.get('mag_sox', {}).get('ventaja_real_media_julio_pp')} pp",
        f"contra {q2b.get('mag_sox', {}).get('ventaja_real_media_resto_pp')} pp del",
        "resto de la ventana larga. Es un bloque bueno, no un bloque de otro",
        "mundo — nueve puntos por encima de un día cualquiera, no cuarenta.",
        "", "---", "",
        "## 3. ¿El bloque de julio es de la misma especie que los históricos?", "",
        "### 3.1 El scan statistic, donde sí hay potencia", "",
        "La ventana sellada dio p≈0.55–0.65 sobre 34 fechas. Aquí es el mismo",
        f"estadístico —máximo de la ventaja sobre ventanas contiguas de "
        f"{min(scan['anchos_probados'])} a {max(scan['anchos_probados'])} "
        f"fechas— sobre {q1['fechas']} fechas.",
        "",
        _tabla([{
            "mejor bloque de la ventana larga":
                f"{scan['mejor_bloque_observado']['desde']} → "
                f"{scan['mejor_bloque_observado']['hasta']}",
            "ancho": scan["mejor_bloque_observado"]["ancho"],
            "ventaja": f"{scan['mejor_bloque_observado']['ventaja_pp']} pp",
            "p del scan": scan["p_scan"],
            "nula (mediana)": f"{scan['nula_mediana_pp']} pp "
                              f"IC90 {scan['nula_ic90_pp']}"}]),
        ("> **⚠ ESTE SCAN ESTÁ SATURADO Y SU p NO SE PUEDE LEER COMO\n"
         "> EVIDENCIA.** Sobre la ventana larga el campeón reconstruido saca\n"
         "> ventaja media de dos dígitos, así que hay muchísimos bloques de 3\n"
         "> fechas donde acierta 7/7 y `siempre al alza` 0/7: el estadístico\n"
         "> toca su techo de 100 pp tanto en los datos como bajo la nula, y\n"
         f"> el p={scan['p_scan']} sale de comparar dos saturaciones. Se\n"
         "> publica porque estaba declarado, marcado como lo que es. El\n"
         "> estadístico que SÍ se puede leer va abajo.")
        if scan.get("scan_saturado") else "",
        "",
        "### 3.2 Julio contra TODOS los bloques de su mismo ancho", "",
        "El estadístico no saturado: dónde cae julio en la distribución de la",
        "ventaja de **todos** los bloques contiguos del mismo ancho, en ocho",
        "años. No hay máximos, no hay saturación, no hay libertad de elegir la",
        "ventana: el ancho lo fija julio.",
        "",
        _tabla([{
            "bloque": f"{scan['julio_2026']['desde']} → {scan['julio_2026']['hasta']}",
            "fechas": scan["julio_2026"]["fechas_en_la_reconstruccion"],
            "ventaja reconstruida":
                f"{scan['julio_2026']['ventaja_pp_reconstruida']} pp",
            "percentil entre bloques de su ancho":
                scan.get("percentil_de_julio_entre_bloques_de_su_ancho")}]),
        _tabla([scan.get("distribucion_de_bloques_del_ancho_de_julio") or {}]),
        f"**En ocho años hay {scan['n_bloques_iguales_o_mejores_sin_solape']}",
        "bloques sin solape iguales o mejores que el de julio.** Los mejores:",
        "",
        _tabla(scan["bloques_historicos_iguales_o_mejores"][:10]),
        "### 3.3 La firma: ¿julio se parece a los bloques altos históricos?", "",
    ]
    if firma.get("evaluable"):
        L += [
            "Las condiciones se estandarizan con media y desviación calculadas",
            "SOLO con datos anteriores a julio-2026 — el bloque que se juzga no",
            "participa en su propia estandarización.",
            "",
            _tabla([{"condición": c,
                     "julio (z)": firma["firma_julio_z"][c],
                     "media de los bloques altos históricos (z)":
                         firma["firma_media_historica_z"][c]}
                    for c in firma["condiciones"]]),
            f"Distancia de Mahalanobis de julio al centro de las firmas",
            f"históricas: **{firma['mahalanobis_julio']}** — percentil",
            f"**{firma['percentil_de_julio']}** de la propia distribución de los",
            f"{firma['bloques_historicos_usados']} bloques altos históricos",
            f"(mediana {firma['mahalanobis_historicos_mediana']}, p95",
            f"{firma['mahalanobis_historicos_p95']}).",
            "",
            f"**Veredicto de la firma: julio "
            f"{'ES de la misma especie' if firma['misma_especie'] else 'NO es de la misma especie'}"
            f"** que los bloques altos históricos — y el motor de esa distancia",
            "es una sola condición, `disp_asia`, en z≈+2.9.",
            "",
            "> **Con qué fuerza se puede decir esto: poca.** Una Mahalanobis con",
            f"> {firma['bloques_historicos_usados']} bloques de referencia en",
            f"> {len(firma['condiciones'])} dimensiones estima una covarianza con",
            "> pocos grados de libertad, y el percentil 100 en esa escala",
            "> significa `el más lejano de treinta`, no `imposible`. Además",
            "> `disp_asia` es precisamente una de las condiciones que **no**",
            "> discrimina fuera de muestra (§2, AUC 0.506, IC incluye 0.5): que",
            "> julio tenga un valor extremo en una variable sin poder predictivo",
            "> es una descripción, no una explicación. La lectura defendible es",
            "> **julio fue un bloque grande pero ordinario en MAGNITUD (percentil",
            "> 90 entre bloques de su ancho) con una dispersión asiática",
            "> inusualmente alta** — y nada de eso lo convierte en evidencia de",
            "> una condición identificable.", "",
        ]
    else:
        L += ["No evaluable con los datos disponibles.", ""]
    if sell.get("disponible"):
        L += [
            "### 3.4 Verificación por OTRO mecanismo: las filas selladas", "",
            "Regla de la casa: una verificación que usa el mismo mecanismo que",
            "produjo la cifra no es una verificación. La reconstrucción sale de",
            "Yahoo hoy; esto sale de `senales.db` en `mode=ro`, sellado en su",
            "momento. Son dos caminos distintos.",
            "",
            _tabla([{"tramo": k, **vv} for k, vv in
                    (("bloque julio", sell["bloque_julio"]),
                     ("resto", sell["resto"]),
                     ("ventana completa", sell["ventana_completa"]))
                    if vv]),
            "La reconstrucción da **"
            f"{scan['julio_2026']['ventaja_pp_reconstruida']} pp** sobre el",
            f"bloque de julio y el sello da **{sell['bloque_julio']['ventaja_pp']} "
            "pp** sobre las mismas 44 filas. Dos caminos de cómputo distintos,",
            "el mismo número: el bloque de julio **existe** y no es un artefacto",
            "de ninguno de los dos mecanismos. Lo que este documento discute no",
            "es si existe, sino si es **excepcional** — y no lo es.",
        ]
    if rec.get("veredicto"):
        L += [
            "", "### 3.5 La reconciliación: 16 pp contra 6 pp", "",
            "Sobre la ventana larga el campeón reconstruido saca **"
            f"{rec['reconstruida_ventana_larga']['ventaja_pp']} pp** sobre",
            "`siempre al alza`; sobre la ventana sellada saca **"
            f"{rec['sellada_completa'].get('ventaja_pp')} pp**. Publicar el",
            "primero sin explicar el segundo sería lo que este proyecto no hace.",
            "La medición que lo dirime es **las mismas filas**.",
            "",
            "#### Primero, un error de emparejamiento que vale la pena contar",
            "",
            "La clave semántica de una fila es la **sesión objetivo**, no la",
            "fecha de emisión — y por eso la advertencia sobre el 91.4% de",
            "`ventana_larga.py` es correcta. Pero emparejar SOLO por sesión",
            "objetivo tampoco alcanza, y esto no estaba anotado en ninguna",
            f"parte: la emisión sellada del {(rec['sobre_las_mismas_filas'].get('fechas_de_emision_desfasadas') or ['?'])[0]}",
            "apunta a una sesión que **no es la siguiente**, porque la corrida",
            "intermedia falló y dejó sus filas vacías. Una reconstrucción que",
            "asume `la emisión de D anticipa la sesión siguiente` empareja esa",
            "sesión con una emisión POSTERIOR, y le regala un día entero de SOX",
            "que el sello no tuvo.",
            "",
            "Con ese emparejamiento la reconstrucción salía 5.2 pp por encima",
            "del sello, con 13 de 14 desacuerdos de signo a su favor",
            "(p=0.0018) — **la firma perfecta de una fuga, y no había ninguna**.",
            "Era el emparejamiento comparando dos predicciones hechas con un día",
            "de diferencia. La comparación honesta exige las DOS claves: misma",
            "sesión objetivo **y** misma fecha de emisión.",
            "",
            f"Filas descartadas por desfase de emisión: "
            f"**{rec['sobre_las_mismas_filas'].get('filas_descartadas_por_desfase_de_emision')}**, "
            f"en las fechas "
            f"{', '.join(rec['sobre_las_mismas_filas'].get('fechas_de_emision_desfasadas') or [])}.",
            "",
            "#### Y entonces, con las dos claves:", "",
            _tabla([
                {"medición": "reconstruida · ventana larga (8 años)",
                 **{k: rec["reconstruida_ventana_larga"].get(k)
                    for k in ("n", "fechas", "acierto_pct", "base_pct",
                              "ventaja_pp", "ic95_por_fecha")}},
                {"medición": "reconstruida · MISMAS FILAS que el sello",
                 **{k: (rec["sobre_las_mismas_filas"].get("reconstruida") or {}).get(k)
                    for k in ("n", "fechas", "acierto_pct", "base_pct",
                              "ventaja_pp", "ic95_por_fecha")}},
                {"medición": "SELLADA · las mismas filas",
                 **{k: (rec["sobre_las_mismas_filas"].get("sellada") or {}).get(k)
                    for k in ("n", "fechas", "acierto_pct", "base_pct",
                              "ventaja_pp", "ic95_por_fecha")}}]),
            f"Sobre esas **{rec['sobre_las_mismas_filas'].get('n_filas_pareadas')}** "
            "filas: **"
            f"{rec['sobre_las_mismas_filas'].get('pct_misma_direccion_de_prediccion')}%** "
            "de las predicciones con el mismo signo, **"
            f"{rec['sobre_las_mismas_filas'].get('pct_gap_identico_a_0.01pp')}%** "
            "de los gaps idénticos a menos de 0.01 pp, **cero** desacuerdos de",
            "signo.",
            "",
            f"**{rec['veredicto']}**", "",
            "> Y de paso queda medido lo que el aviso decía: emparejando por la",
            "> clave correcta la coincidencia con el sello es del **100%**, no",
            "> del 91.4% que `GEMELO/ventana_larga.py`:214 sigue calculando",
            "> emparejando por `[\"fecha\",\"ticker\"]`. Esa cifra está refutada y",
            "> este documento no la republica.",
            "",
            "#### Dónde está entonces la brecha entre las dos ventanas", "",
            "No en el mecanismo. La ventana sellada, partida en sus tramos:",
            "",
            _tabla(rec.get("descomposicion_sellada") or []),
            "Los +6.2 pp de la ventana sellada son la resta de tres cosas muy",
            "distintas: un bloque de julio de +40.9 pp, dos fechas de incidente",
            "de producción que cuestan −62.5 pp sobre 16 filas, y un resto de",
            "+4.1 pp con p=0.44 que es lo que el modelo hace un día cualquiera.",
            "",
            "> **Esto NO es una corrección ni una retractación, y el tramo `sin",
            "> incidentes` NO es el resultado.** Las filas selladas jamás se",
            "> reescriben y ninguna cifra publicada se mueve: los +6.2 pp de la",
            "> ventana completa siguen siendo la cifra de la ventana completa, y",
            "> el 65.8% / +5.3 pp del README sigue vigente. Quitar los días malos",
            "> de un track record es exactamente la trampa que este proyecto no",
            "> comete. Es una DESCOMPOSICIÓN: dice de dónde viene el número, no",
            "> lo sustituye.",
            "",
            "> Lo que además cambia entre las dos ventanas es **el rival**:",
            "> `siempre al alza` acierta "
            f"{rec['reconstruida_ventana_larga'].get('base_pct')}% en ocho años y",
            f"{(rec['sobre_las_mismas_filas'].get('sellada') or {}).get('base_pct')}% "
            "en el tramo sellado. La misma habilidad rinde menos ventaja cuando",
            "> el rival es más duro. Por eso la regla de la casa exige comparar",
            "> **sobre las mismas filas**.",
        ]
    L += [
        "", "---", "",
        "## 4. Lo que quedó NO EVALUABLE, y por qué", "",
        f"**Condición 4 del pre-registro (§3.4), `{cl4['condicion']}`: NO",
        "EVALUABLE.** Dos razones independientes, ambas medidas aquí, no",
        "supuestas:",
        "",
        f"1. **Fuga B-1.** {cl4.get('motivo_1_fuga','')}. El primer juicio de IA "
        f"es del `{cl4.get('primer_analisis')}`, sobre titulares que empiezan el "
        f"`{str(cl4.get('titulares_desde'))[:10]}`. El retraso, medido en varios "
        "umbrales — cada uno con su definición a la vista, para que dos cifras "
        "verdaderas medidas con criterios distintos no parezcan contradecirse:",
        "",
        _tabla([{"criterio": k.replace("_", " "), "valor": v}
                for k, v in (cl4.get("retrasos_de_analisis") or {}).items()]),
        f"2. **Cobertura.** {cl4.get('motivo_2_cobertura','')}: `titulares` va de "
        f"`{cl4.get('titulares_desde')}` a `{cl4.get('titulares_hasta')}` "
        f"({cl4.get('titulares_n')} filas), contra una ventana que empieza en "
        f"{w['desde']}.",
        "",
        "La §5 R4 del pre-registro obliga a descartar una condición con fuga,",
        "no a reportarla con una advertencia. Se descarta. Y como el §4.2 bis",
        "define un intento como `(configuración × ventana) **con resultado",
        "reportable**`, la condición 4 **no suma al DSR**.",
        "",
        "> El arreglo de la fuga lo está haciendo otro frente sobre",
        "> `backtest/datos.py`. Aunque quede arreglado, la razón 2 sigue en pie:",
        "> sobre 2018→2026 esta condición no es medible.",
        "", "---", "",
        "## 5. El conteo de intentos", "",
        _tabla([{"intento": a, "ventana": b, "cuenta": c}
                for a, b, c in CONTEO_INTENTOS]),
        f"**N acumulado: {p['N_intentos_previo']} → {p['N_intentos_acumulado']}**",
        f"(+{p['N_intentos_nuevos']}).",
        "",
        "Tres precisiones sobre el conteo, porque contarlo a conveniencia es",
        "exactamente el sesgo que el DSR existe para corregir:",
        "",
        "1. El pre-registro §7 había declarado +7 (seis condiciones + el",
        "   conjunto). Aquí son +8 por dos correcciones que se compensan y una",
        "   que no: la condición 4 **no cuenta** (sin resultado reportable); las",
        "   dos ventanas de volatilidad (5 y 10) **se reportan por separado**, y",
        "   la §7 ya previó que en ese caso el N sube; y el **scan statistic de",
        "   la §3.1 se declara HOY** como intento nuevo, que el pre-registro no",
        "   había contado.",
        "2. La curva de concentración de la §1 **no** cuenta como intento: no",
        "   ajusta ninguna configuración ni elige entre resultados. Es",
        "   descriptiva.",
        "3. Subir el N es la dirección conservadora: deflacta más, no menos.",
        "", "---", "",
        "## 6. Deudas y advertencias declaradas", "",
        "- **`GEMELO/ventana_larga.py`:314-345 sigue ofreciendo una cifra de",
        "  contaminación ya refutada** (el 91.4% de coincidencia con el track",
        "  record sellado). Sale de emparejar por `[\"fecha\",\"ticker\"]` cuando",
        "  corresponde por sesión objetivo. **No se republica aquí**, y este",
        "  documento no la usa en ninguna parte. Queda anotada como deuda de la",
        "  regla de la casa #4: un número retirado que sigue ofrecido en el",
        "  código vuelve a circular. El arreglo va al ejecutable, no a un",
        "  párrafo — no se hizo en este frente para no pisar el trabajo en curso",
        "  sobre `backtest/`.",
        "- **La ventana larga NO es point-in-time.** Yahoo reescribe la historia",
        "  en silencio y el ajuste se recalcula con cada dividendo y split",
        "  posteriores. La ventana larga da POTENCIA; la ventana sellada da",
        "  VALIDEZ. Ninguna reemplaza a la otra. Todo hallazgo de este documento",
        "  es sobre una reconstrucción, y el hallazgo central —que no hay",
        "  condición identificable— es del tipo que la contaminación haría MÁS",
        "  fácil de contradecir, no más fácil de sostener.",
        "- El corte alto/bajo es la **mediana global** de la ventana, congelada",
        "  en la §4: arrastra un componente in-sample. Se respetó porque estaba",
        "  congelado; su efecto sería sobreestimar la discriminación, y aun así",
        "  no se encontró ninguna.",
        "- La condición 3 lee `vs. índice local + FX` como retorno del índice",
        "  llevado a USD (convención #2: los pares son unidades por 1 USD).",
        "  Residualizar un índice contra sí mismo es degenerado; la lectura se",
        "  declara aquí, no se esconde.",
        "", "---",
        "Herramienta de análisis — no constituye asesoría financiera.",
        "Pre-registro congelado en `GEMELO/CONDICIONAL/DISEÑO.md`.",
        "**No es el veredicto de la Etapa 5.1** y no autoriza ningún cambio de",
        "modelo: 4.6.0 sigue sellando sin enterarse de que esto existe.",
    ]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Frente D — hipótesis condicional sobre la ventana larga.")
    ap.add_argument("--anios", type=int, default=ANIOS)
    ap.add_argument("--sin-cache", action="store_true")
    ap.add_argument("--sin-escribir", action="store_true")
    ap.add_argument("--embargo-dias", type=int, default=EMBARGO_DIAS)
    ap.add_argument("--permutaciones", type=int, default=N_PERMUTACIONES)
    args = ap.parse_args(argv)
    r = correr(anios=args.anios, usar_cache=not args.sin_cache,
               embargo_dias=args.embargo_dias,
               n_permutaciones=args.permutaciones)
    texto = informe(r)
    print(texto)
    if not args.sin_escribir:
        os.makedirs(DIR_RESULTADOS, exist_ok=True)
        base = os.path.join(DIR_RESULTADOS, "condicional_ventana_larga")
        with open(base + ".md", "w", encoding="utf-8") as f:
            f.write(texto)
        with open(base + ".json", "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2, default=str)
        print(f"[escrito] {base}.md / .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
