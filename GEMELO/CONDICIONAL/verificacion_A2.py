"""
verificacion_A2.py — recomputa, de forma reproducible y versionada, los
números corregidos de GEMELO/resultados/concentracion.md §A2 tras la
revisión adversaria del 31-ago-2026 (estadistico-adversario RECHAZÓ/pidió
correcciones sobre la versión que solo vivía como comandos sueltos en /tmp,
que dejaron de existir al cerrar la sesión — este archivo es la corrección
de ESE defecto también: el análisis queda en el repo, no en /tmp).

Solo lectura contra senales.db (mode=ro). No escribe nada.

Corre con: python GEMELO/CONDICIONAL/verificacion_A2.py
"""
import os
import sqlite3
import sys

import numpy as np
import pandas as pd

_RAIZ_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _RAIZ_REPO)
sys.path.insert(0, os.path.join(_RAIZ_REPO, ".claude/skills/estadistica-evaluacion/scripts"))
from evaluacion import comparar_pareado, wilson_ci  # noqa: E402
from backtest import inferencia as inf  # noqa: E402

BLOQUE_INICIO = "2026-07-15"
BLOQUE_FIN = "2026-07-23"
SEMILLA = 20260831


def cargar() -> pd.DataFrame:
    con = sqlite3.connect("file:senales.db?mode=ro", uri=True)
    df = pd.read_sql_query(
        """
        SELECT va.fecha_senal AS fecha, va.ticker, va.gap_pct, va.acierto_gap,
               st.exchange
        FROM verificacion_apertura va
        LEFT JOIN senales_ticker st
          ON st.fecha = va.fecha_senal AND st.ticker = va.ticker
        WHERE va.legacy = 0 AND va.modelo_version = '4.6.0'
          AND va.gap_pct IS NOT NULL AND va.gap_pct != 0.0
        """,
        con,
    )
    con.close()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["base_ok"] = (df["gap_pct"] > 0).astype(int)
    df["modelo_ok"] = df["acierto_gap"].astype(int)
    return df


def _bc(g: pd.DataFrame) -> pd.Series:
    b = int(((g["modelo_ok"] == 1) & (g["base_ok"] == 0)).sum())
    c = int(((g["modelo_ok"] == 0) & (g["base_ok"] == 1)).sum())
    return pd.Series({"n": len(g), "b": b, "c": c})


def por_bolsa_dentro_y_fuera(df: pd.DataFrame) -> None:
    bloque = df[(df["fecha"] >= BLOQUE_INICIO) & (df["fecha"] <= BLOQUE_FIN)]
    resto = df[~((df["fecha"] >= BLOQUE_INICIO) & (df["fecha"] <= BLOQUE_FIN))]
    print("=== por bolsa DENTRO del bloque 15-23-jul ===")
    for ex, g in bloque.groupby("exchange"):
        print(" ", ex, comparar_pareado(g["modelo_ok"].astype(bool), g["base_ok"].astype(bool)))
    print("\n=== por bolsa FUERA del bloque ===")
    for ex, g in resto.groupby("exchange"):
        print(" ", ex, comparar_pareado(g["modelo_ok"].astype(bool), g["base_ok"].astype(bool)))


def bootstrap_diferencia_bloque_resto(por_fecha: pd.DataFrame, n_draws: int = 20000):
    """IC de la diferencia bloque-resto por bootstrap CIRCULAR de bloques
    por fecha, usando `backtest.inferencia._remuestrear_circular` — nunca
    un remuestreo iid de fechas sueltas (ese fue el defecto que
    `guardian-constitucion` encontró en la versión anterior de este mismo
    script: el bootstrap reintrodujo, versionado, el mismo defecto que la
    corrección de A4-A5 estaba retractando).

    `_remuestrear_circular(r, semilla, n_draws, bloque)` genera los índices
    de remuestreo a partir SOLO de `len(r)`, la semilla y `n_draws`/`bloque`
    — nunca de los valores de `r` — así que llamarla con la MISMA semilla
    sobre `n`, `b` y `c` da, para los tres, la MISMA secuencia de índices, y
    los tríos (n_i, b_i, c_i) de cada réplica quedan alineados por fecha.

    **El tamaño de bloque se fija en 1 para el grupo del bloque (6 fechas),
    y se comprobó por qué**: con solo 6 fechas, un bloque de tamaño ≥4 deja
    pocas posiciones circulares de inicio distintas, y con bloque=6 (=el
    tamaño del grupo) el bootstrap degenera por completo (varianza cero: la
    única "ventana circular" posible es la serie entera). Se midió la
    sensibilidad barriendo bloque=1..6: el IC se angosta artificialmente
    a medida que el bloque crece, no porque haya menos incertidumbre real,
    sino porque el bootstrap se queda sin combinaciones distintas para
    muestrear. Bloque=1 (equivalente a remuestreo iid del elemento, vía la
    misma función) es la única opción no degenerada para un grupo de 6, y
    es la que se reporta — con esta nota, en vez de elegir en silencio el
    bloque que da el intervalo más angosto.
    """
    fb = por_fecha[por_fecha["en_bloque"]].reset_index(drop=True)
    fr = por_fecha[~por_fecha["en_bloque"]].reset_index(drop=True)

    def _medias_por_draw(grupo: pd.DataFrame, semilla: int, bloque_local: int) -> np.ndarray:
        n_arr = grupo["n"].to_numpy(float)
        b_arr = grupo["b"].to_numpy(float)
        c_arr = grupo["c"].to_numpy(float)
        bloque_local = min(bloque_local, len(n_arr))
        n_re = inf._remuestrear_circular(n_arr, semilla, n_draws, bloque_local)
        b_re = inf._remuestrear_circular(b_arr, semilla, n_draws, bloque_local)
        c_re = inf._remuestrear_circular(c_arr, semilla, n_draws, bloque_local)
        return 100 * (b_re.sum(axis=1) - c_re.sum(axis=1)) / n_re.sum(axis=1)

    # semillas distintas para bloque y resto: son dos grupos disjuntos, no
    # dos series alineadas — no hay razón para acoplar su sorteo.
    medias_bloque = _medias_por_draw(fb, SEMILLA, 1)
    medias_resto = _medias_por_draw(fr, SEMILLA + 1, 1)
    diffs = medias_bloque - medias_resto

    obs = (
        100 * (fb["b"].sum() - fb["c"].sum()) / fb["n"].sum()
        - 100 * (fr["b"].sum() - fr["c"].sum()) / fr["n"].sum()
    )
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    frac_cero = float(np.mean(diffs <= 0))
    return obs, lo, hi, frac_cero


def p_posicion_fija_vs_busqueda(por_fecha: pd.DataFrame, n_perm: int = 20000):
    """Compara el p de la ventana EXACTA (sin buscar la mejor posición)
    contra el p de buscar la mejor de todas las posiciones de ancho fijo 6
    (scan-statistic), y contra elegir 6 fechas al azar SIN exigir que sean
    contiguas. Si los tres coinciden, la contigüidad no aporta nada — el
    bloque es "6 fechas que contienen varias de las mejores", no una racha."""
    rng = np.random.default_rng(SEMILLA)
    n_arr = por_fecha["n"].to_numpy(float)
    b_arr = por_fecha["b"].to_numpy(float)
    c_arr = por_fecha["c"].to_numpy(float)
    K = len(n_arr)
    pos = list(por_fecha[por_fecha["en_bloque"]].index)
    obs = 100 * (b_arr[pos].sum() - c_arr[pos].sum()) / n_arr[pos].sum()

    cnt = 0
    for _ in range(n_perm):
        perm = rng.permutation(K)
        ventana = perm[pos[0]:pos[0] + 6]
        v = 100 * (b_arr[ventana].sum() - c_arr[ventana].sum()) / n_arr[ventana].sum()
        if v >= obs - 1e-9:
            cnt += 1
    p_fijo = (cnt + 1) / (n_perm + 1)

    cnt = 0
    for _ in range(n_perm):
        sel = rng.choice(K, 6, replace=False)
        v = 100 * (b_arr[sel].sum() - c_arr[sel].sum()) / n_arr[sel].sum()
        if v >= obs - 1e-9:
            cnt += 1
    p_azar_no_contiguo = (cnt + 1) / (n_perm + 1)

    def max_scan_ancho_fijo(b, c, n, w):
        cb = np.concatenate([[0], np.cumsum(b)])
        cc = np.concatenate([[0], np.cumsum(c)])
        cn = np.concatenate([[0], np.cumsum(n)])
        bs = cb[w:] - cb[:-w]
        cs = cc[w:] - cc[:-w]
        ns = cn[w:] - cn[:-w]
        v = np.where(ns > 0, 100 * (bs - cs) / np.maximum(ns, 1), -1e18)
        i = int(np.argmax(v))
        return v[i]

    obs_scan = max_scan_ancho_fijo(b_arr, c_arr, n_arr, 6)
    cnt = 0
    for _ in range(n_perm):
        perm = rng.permutation(K)
        if max_scan_ancho_fijo(b_arr[perm], c_arr[perm], n_arr[perm], 6) >= obs_scan - 1e-9:
            cnt += 1
    p_scan_ancho6 = (cnt + 1) / (n_perm + 1)

    return obs, p_fijo, p_azar_no_contiguo, obs_scan, p_scan_ancho6


def main():
    df = cargar()
    por_bolsa_dentro_y_fuera(df)

    por_fecha = df.groupby("fecha").apply(_bc, include_groups=False).reset_index()
    por_fecha = por_fecha.sort_values("fecha").reset_index(drop=True)
    por_fecha["en_bloque"] = (por_fecha["fecha"] >= BLOQUE_INICIO) & (por_fecha["fecha"] <= BLOQUE_FIN)

    obs, lo, hi, frac0 = bootstrap_diferencia_bloque_resto(por_fecha)
    print(f"\ndiferencia bloque-resto: {obs:+.2f}pp  IC95 (bootstrap por fecha, "
          f"20000 réplicas, semilla {SEMILLA}): [{lo:.2f}, {hi:.2f}]  "
          f"fracción de réplicas <=0: {frac0*100:.2f}%")

    obs2, p_fijo, p_azar, obs_scan, p_scan = p_posicion_fija_vs_busqueda(por_fecha)
    print(f"\nventaja del bloque (posición exacta): {obs2:+.2f}pp")
    print(f"  p, SIN buscar la mejor posición (posición fija tal como cayó): {p_fijo:.4f}")
    print(f"  p, eligiendo 6 fechas al azar NO contiguas:                    {p_azar:.4f}")
    print(f"  -> {'la contigüidad NO aporta nada' if abs(p_fijo - p_azar) < 0.01 else 'la contigüidad SÍ aporta'} "
          f"(diferencia {abs(p_fijo-p_azar):.4f})")
    print(f"\n  máxima ventaja buscando entre TODAS las ventanas de ancho 6 (scan-statistic): {obs_scan:+.2f}pp")
    print(f"  p con corrección por búsqueda (scan-statistic): {p_scan:.4f}")
    print(f"  -> la distancia entre {p_fijo:.4f} y {p_scan:.4f} es enteramente el costo de "
          f"haber buscado la mejor de 29 posiciones posibles")


if __name__ == "__main__":
    main()
