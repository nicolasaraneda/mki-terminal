"""cifras.py — el módulo árbitro de toda cifra publicada de MKI Terminal.

Octava corrida (2-sep-2026), Frente G: reglas de la casa ejecutables.
Novena corrida (3-sep-2026), Frente 1a: la convención publicada pasa a la
REGLA DE DEDUPLICACIÓN FIRMADA el 1-sep (decisión D1 de Nicolás); la
convención sin deduplicar queda DEROGADA y sus cifras entran al registro
de cifras retiradas. Cada estimador lleva ahora su intervalo de CLÚSTER
DE DÍA además del Wilson de filas: las ocho filas de un día comparten el
mismo movimiento del SOX y no son independientes (acta §61).

Regla: una cifra publicada tiene UNA fuente, con n e intervalo, y los
documentos la citan desde acá — o un test falla cuando el documento y el
árbitro no coinciden. Este módulo NO inventa cifras: las de la ventana
sellada se COMPUTAN desde `senales.db` (mode=ro) en el instante pinchado
`CORTE_README`; las de la ventana larga están CONGELADAS aquí con su
procedencia (recomputarlas exige una descarga y mueve los doce bloques:
lleva firma).

Uso:
    from cifras import sellada, larga, doce_bloques
    c = sellada()             # dict con n, acierto, base, ventaja, IC de día, p, MAE, cobertura…
    for archivo, fragmento in doce_bloques(c): ...

El test `tests/test_cifras_arbitro.py` fija que cada uno de los doce bloques
aparece textualmente en su archivo, que cambiar n en el árbitro cambia los
doce, que cambiar la CONVENCIÓN (dedup) también los cambia y que la rama
derogada ya no aparece en ningún documento, y que ninguna cifra RETIRADA
(`GEMELO/cifras_retiradas.md`) vuelve a aparecer en un documento publicado.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

_RAIZ = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------
# Ventana sellada: computada, no escrita
# ------------------------------------------------------------
# El instante en que el README publicó su ventana sellada: distinto de
# `CORTE_SECCION_2` (24-ago, la línea base de la §2.8, n = 223) y de
# `CORTE_REGLA_FIRMADA` (31-ago). Tres instantes pinchados, tres nombres.
# El README publicaba la rama sin deduplicar en este mismo corte (era
# n = 248); desde el 3-sep-2026 publica la regla firmada (D1), mismo corte.
CORTE_README = "2026-08-28"
# La convención publicada. `True` = regla de deduplicación firmada el
# 1-sep-2026 (`backtest.linea_base.deduplicar_por_sesion`: entre dos filas
# que apuntan a la misma sesión objetivo sobrevive la que corresponde a su
# `available_at`; nunca la más fresca). `False` es la RAMA DEROGADA (D1,
# acta §78) y sólo sirve para probar que sus cifras ya no circulan.
DEDUP_PUBLICADO = True
N_BOOT_DIA = 4000
N_PERM_DIA = 4000


def _grupos_por_dia(df, valores):
    import numpy as np
    v = np.asarray(valores, dtype=float)
    fechas = df["fecha"].to_numpy()
    return [v[fechas == f] for f in sorted(set(fechas))]


def _ic_ratio_dia(df, n_boot: int = N_BOOT_DIA):
    """IC95 de clúster de día del ratio ancho medio / error medio: remuestrea
    días enteros y recomputa el cociente de medias en cada réplica."""
    import numpy as np
    from GEMELO import bifurcaciones as bf
    d = df.dropna(subset=["intervalo80_pp"])
    fechas = sorted(set(d["fecha"]))
    ancho = _grupos_por_dia(d, d["intervalo80_pp"])
    err = _grupos_por_dia(d, d["error_gap_pp"])
    sa = np.array([g.sum() for g in ancho]); se = np.array([g.sum() for g in err])
    cnt = np.array([len(g) for g in ancho], dtype=float)
    k = len(fechas)
    rng = np.random.default_rng(bf.SEMILLA)
    idx = rng.integers(0, k, size=(n_boot, k))
    reps = (sa[idx].sum(axis=1) / cnt[idx].sum(axis=1)) / (se[idx].sum(axis=1) / cnt[idx].sum(axis=1))
    lo, hi = np.quantile(reps, [0.025, 0.975])
    return [round(float(lo), 2), round(float(hi), 2)]


def sellada(hasta_sello: str | None = None, dedup: bool = DEDUP_PUBLICADO) -> dict:
    """Las cifras de la ventana sellada bajo la convención canónica
    (`excluir_cero`) y la regla de deduplicación firmada (`dedup=True`, lo
    publicado en el README desde el 3-sep-2026), al instante pinchado del
    README. Toda cifra lleva su n y su intervalo; los estimadores de la
    ventaja llevan además el intervalo de clúster de día y el p de
    permutación de signo por día, que son los que respetan que las filas de
    un día no son independientes. `dedup=False` es la rama derogada."""
    import sqlite3
    import pandas as pd
    from backtest import linea_base as lb
    from GEMELO import bifurcaciones as bf
    corte = hasta_sello or CORTE_README
    crudo = lb.cargar(hasta_sello=corte, dedup=dedup)
    df = lb.aplicar_convencion(crudo, lb.CONVENCION_OFICIAL)
    d = lb.duelo(df)
    m = lb.magnitud(df)
    cal = lb.calibracion(df)
    n = d["n"]
    f = lambda x: float(x) if x is not None else None   # sin np.float64 en el JSON
    # --- clúster de día sobre la diferencia acierto_modelo − acierto_base ---
    diff = (df["acierto_gap"].astype(int) - df["base_acierto"].astype(int)).to_numpy(dtype=float)
    grupos = _grupos_por_dia(df, diff)
    punto, lo, hi = bf._bootstrap_dia(grupos, N_BOOT_DIA)
    _, lo_t, hi_t = bf._ic_t_cluster(grupos)
    p_dia = bf._p_permutacion_dia(grupos, N_PERM_DIA)
    icc = bf.icc_y_deff(grupos)
    # --- ganancia de MAE contra predecir cero, CON su intervalo de día ---
    # Era el único estimador del árbitro que salía sin intervalo (dictamen del
    # `curador-epistemico`, 6-sep-2026, exigencia 1, y su O16: el test que dice
    # vigilar esto no lo cazaba porque `mae_mejora_pct` es un cociente y el
    # detector busca pares punto/intervalo). El cociente no tiene unidad de
    # replicación; la ganancia por fila sí, y es el día.
    gan = (df["gap_pct"].abs()
           - (df["apertura_estimada_pct"] - df["gap_pct"]).abs()).to_numpy(dtype=float)
    g_gan = _grupos_por_dia(df, gan)
    _, gan_lo, gan_hi = bf._ic_t_cluster(g_gan)
    gan_p = bf._p_permutacion_dia(g_gan, N_PERM_DIA)
    # --- McNemar exacta (binomial bilateral), al lado de la χ²cc que publica el README ---
    from math import comb
    b, c = int(d["mcnemar_b01"]), int(d["mcnemar_b10"])
    nb, kb = b + c, min(b, c)
    p_exacta = min(1.0, 2 * sum(comb(nb, i) for i in range(kb + 1)) / 2 ** nb)
    # --- acierto del retorno de sesión (misma dedup, sin excluir_cero: el gap==0 no afecta al retorno) ---
    conn = sqlite3.connect(f"file:{lb.RUTA_SENALES}?mode=ro", uri=True)
    try:
        v = pd.read_sql_query(
            "SELECT fecha_senal AS fecha, ticker, retorno_real_pct, acierto_direccion "
            "FROM verificacion_apertura WHERE legacy = 0 AND modelo_version = ? "
            "AND substr(verificado_en, 1, 10) <= ?", conn, params=[lb.MODELO_VERSION, corte])
    finally:
        conn.close()
    r = crudo.merge(v, on=["fecha", "ticker", "retorno_real_pct"], how="inner").dropna(subset=["acierto_direccion"])
    ra, rn = int(r["acierto_direccion"].astype(int).sum()), int(len(r))
    return {
        "hasta_sello": corte, "convencion": lb.CONVENCION_OFICIAL, "dedup": dedup,
        "n": n, "dias": int(df["fecha"].nunique()),
        "modelo_aciertos": int(d["modelo_aciertos"]), "modelo_pct": f(d["modelo_pct"]), "modelo_wilson": [f(x) for x in d["modelo_wilson"]],
        "base_aciertos": int(d["base_aciertos"]), "base_pct": f(d["base_pct"]), "base_wilson": [f(x) for x in d["base_wilson"]],
        "ventaja_pp": f(d["ventaja_pp"]), "ventaja_pp_exacta": round(100 * (d["modelo_aciertos"] - d["base_aciertos"]) / n, 2),
        "ventaja_ic_dia": [round(100 * lo, 1), round(100 * hi, 1)],
        "ventaja_ic_t_cluster": [round(100 * float(lo_t), 1), round(100 * float(hi_t), 1)],
        "p_permutacion_dia": round(float(p_dia), 3),
        "icc": round(float(icc["icc"]), 3), "deff": round(float(icc["deff"]), 2), "n_efectivo": round(float(icc["n_efectivo"]), 1),
        "mcnemar_p": f(d["mcnemar_p"]), "mcnemar_p_exacta": round(p_exacta, 4), "b": b, "c": c,
        "retorno_aciertos": ra, "retorno_n": rn, "retorno_pct": round(100 * ra / rn, 1) if rn else None,
        "retorno_wilson": [f(x) for x in lb._wilson(ra, rn)] if rn else None,
        "mae_modelo_pp": f(m["mae_modelo"]), "mae_cero_pp": f(m["mae_cero"]),
        "mae_mejora_pct": round(100 * (m["mae_modelo"] / m["mae_cero"] - 1), 1),
        "mae_ganancia_pp": round(float(gan.mean()), 4),
        "mae_ganancia_ic_t_dia": [round(float(gan_lo), 3), round(float(gan_hi), 3)],
        "mae_ganancia_p_dia": round(float(gan_p), 3),
        "cobertura_80_pct": f(cal.get("cobertura_pct")), "ratio_ancho": f(cal.get("ratio_ancho_error")),
        "ratio_ancho_ic_dia": _ic_ratio_dia(df),
        "procedencia": ("backtest.linea_base.{cargar(dedup=%s),aplicar_convencion,duelo,magnitud,calibracion} en mode=ro; "
                        "clúster de día: GEMELO.bifurcaciones.{_bootstrap_dia,_ic_t_cluster,_p_permutacion_dia,icc_y_deff}" % dedup),
    }


# ------------------------------------------------------------
# Ventana larga: congelada con procedencia (no recomputable sin descarga)
# ------------------------------------------------------------
@dataclass(frozen=True)
class Larga:
    n: int = 14618
    ventaja_pp: float = 15.66
    por_bolsa: tuple = (("Tokio", "XTKS", 7230, 19.1, 1.75), ("Taipéi", "XTAI", 1807, 16.8, 2.75),
                        ("Seúl", "XKRX", 3626, 15.4, 1.75), ("Fráncfort", "XETR", 1955, 2.5, 8.75))
    p_francfort: float = 0.111
    procedencia: str = ("GEMELO/ventana_larga.py sobre el caché de gaps v1 (26-ago-2026); README.md:46-49 y :146. "
                        "ADVERTENCIA (2-sep-2026, acta de la octava corrida): el caché v1 omitía toda sesión "
                        "posterior a un feriado local (~4,5% de las filas); recomputar mueve los doce bloques y lleva firma.")


def larga() -> Larga:
    return Larga()


# ------------------------------------------------------------
# Los doce bloques que se mueven con n
# ------------------------------------------------------------
def doce_bloques(c: dict) -> list:
    """(archivo, fragmento) que DEBE aparecer textualmente en el archivo para
    la cifra vigente. Si n cambia en el árbitro, los doce fragmentos cambian
    (test), y cada archivo tiene que actualizarse — o no se mueve ninguno.
    Desde el 3-sep-2026 el bloque 2 (TL;DR) y el 6 (tabla) llevan el IC de
    clúster de día, y el 9 lleva el ratio de ancho con su IC. El «1,84×»
    suelto quedó RETIRADO el 3-sep-2026 por D1 y está en el registro
    `GEMELO/cifras_retiradas.md`: el ratio entra con n e intervalo, o no
    entra."""
    n = c["n"]
    v = f"{c['ventaja_pp']:+.1f}"
    ic = f"[{c['ventaja_ic_dia'][0]:+.1f}, {c['ventaja_ic_dia'][1]:+.1f}]"
    ric = f"[{c['ratio_ancho_ic_dia'][0]:.2f}, {c['ratio_ancho_ic_dia'][1]:.2f}]"
    return [
        ("README.md", f"sealed window (n={n})"),                                          # 1 TL;DR
        ("README.md", f"**{v} pp, day-cluster 95% CI {ic}"),                             # 2 TL;DR cifra + IC de día
        ("README.md", f"n%3D{n}"),                                                        # 3 badge
        ("README.md", f"**{c['modelo_pct']:.1f}%** ({c['modelo_aciertos']}/{n})"),        # 4 tabla modelo
        ("README.md", f"**{c['base_pct']:.1f}%** ({c['base_aciertos']}/{n})"),            # 5 tabla base
        ("README.md", f"**{v} pp** | IC95 de día **{ic}** · McNemar p = {c['mcnemar_p']:.4f}"),  # 6 tabla ventaja
        ("README.md", f"| Otras métricas (n={n}) |"),                                     # 7 otras métricas
        ("README.md", f"**{c['mae_modelo_pp']:.2f} pp** vs **{c['mae_cero_pp']:.2f}** de predecir cero | ganancia {c['mae_ganancia_pp']:+.2f} pp por fila, IC95 t de clúster de día [{c['mae_ganancia_ic_t_dia'][0]:+.2f}, {c['mae_ganancia_ic_t_dia'][1]:+.2f}]"),   # 8 MAE con su ganancia e IC de día
        ("README.md", f"{c['cobertura_80_pct']:.1f}% (nominal 80%) | intervalos **{c['ratio_ancho']:.2f}× más anchos** de lo necesario (IC95 de día {ric})"),  # 9 cobertura + ratio con IC
        (".claude/skills/cifras-canonicas/SKILL.md", f"**{n}** | **{c['modelo_pct']:.1f}%** | **{c['base_pct']:.1f}%** | **{v} pp** | **{ic}** | **{c['mcnemar_p']:.4f}**"),  # 10 skill
        (".claude/skills/cifras-canonicas/SKILL.md", f"MAE del gap {c['mae_modelo_pp']:.2f} contra {c['mae_cero_pp']:.2f}"),   # 11 skill MAE
        ("GEMELO/resultados/estado_epistemico.md", f"+{c['ventaja_pp']:.1f} pp, n = {n}".replace(".", ",")),  # 12 estado epistémico (coma decimal)
    ]


# ------------------------------------------------------------
# Cifras retiradas: legibles por máquina desde GEMELO/cifras_retiradas.md
# ------------------------------------------------------------
RUTA_RETIRADAS = os.path.join(_RAIZ, "GEMELO", "cifras_retiradas.md")
DOCUMENTOS_PUBLICADOS = ("README.md", "GEMELO/resultados/estado_epistemico.md",
                         ".claude/skills/cifras-canonicas/SKILL.md")


def cifras_retiradas() -> list:
    """Filas de la tabla de `GEMELO/cifras_retiradas.md`: cada una con el
    patrón (regex) que NO debe reaparecer en un documento publicado, el
    contexto y el acta que la retiró."""
    out = []
    if not os.path.exists(RUTA_RETIRADAS):
        return out
    for linea in open(RUTA_RETIRADAS, encoding="utf-8"):
        if not linea.startswith("| `"):
            continue
        celdas = [x.strip() for x in linea.strip().strip("|").split(" | ")]
        if len(celdas) < 4 or celdas[0] in ("`patrón`",):
            continue
        out.append({"patron": celdas[0].strip("`"), "contexto": celdas[1], "retirada": celdas[2],
                    "acta": celdas[3], "reemplazo": celdas[4] if len(celdas) > 4 else ""})
    return out


MARCAS_DE_RETIRO = ("retirad", "errata", "decía", "decia", "era ", "refutad", "corregid",
                    "es falsa", "falso", "desmont", "derogad")


def _tiene_marca_de_retiro(lineas: list, i: int) -> bool:
    """¿Hay una marca de retiro a ±2 líneas de la línea i?"""
    ctx = " ".join(lineas[max(0, i - 2):i + 3]).lower()
    return any(m in ctx for m in MARCAS_DE_RETIRO)


def reintroducciones(texto: str, retiradas: list | None = None) -> list:
    """Cifras retiradas que aparecen en `texto` sin una marca de retiro a
    ±2 líneas («retirad», «errata», «era», «decía», «es falsa», «desmont»…).
    Lo que usa el test y el hook propuesto."""
    retiradas = retiradas if retiradas is not None else cifras_retiradas()
    lineas = texto.split("\n")
    hallazgos = []
    for i, linea in enumerate(lineas):
        if _tiene_marca_de_retiro(lineas, i):
            continue
        for r in retiradas:
            if re.search(r["patron"], linea):
                hallazgos.append((i + 1, r["patron"], linea.strip()[:100]))
    return hallazgos
