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
# sale de datos._conexion_ro (uri mode=ro). Este módulo no escribe en
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
# ============================================================

import argparse
import math
import os
import sys
from datetime import datetime, timezone

import pandas as pd

from api.utilidades import intervalo_wilson
from backtest.datos import RUTA_SENALES, _conexion_ro
from version import MODELO_VERSION

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
# Carga — solo lectura
# ------------------------------------------------------------
def cargar(modelo_version: str = MODELO_VERSION) -> pd.DataFrame:
    """Une verificacion_apertura con senales_ticker por (fecha, ticker) y
    con snapshots por fecha. Solo 4.6.0, nunca legacy, solo con gap."""
    if not os.path.exists(RUTA_SENALES):
        return pd.DataFrame()
    conn = _conexion_ro(RUTA_SENALES)
    try:
        df = pd.read_sql_query("""
            SELECT v.fecha_senal AS fecha, v.ticker,
                   v.apertura_estimada_pct, v.gap_pct, v.acierto_gap,
                   v.error_gap_pp, v.retorno_real_pct,
                   s.confianza_r2, s.intervalo80_pp, s.n_muestra, s.beta,
                   s.exchange,
                   snap.regimen, snap.sox_usado_pct, snap.sox_fecha
            FROM verificacion_apertura v
            LEFT JOIN senales_ticker s
                   ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
            LEFT JOIN snapshots snap ON snap.fecha = v.fecha_senal
            WHERE v.legacy = 0 AND v.modelo_version = ?
              AND v.gap_pct IS NOT NULL
            ORDER BY v.fecha_senal, v.ticker
        """, conn, params=(modelo_version,))
    finally:
        conn.close()
    return df


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
                          modelo_version: str = MODELO_VERSION) -> dict:
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
            "SELECT fecha, ticker, beta FROM senales_ticker"
            " WHERE beta IS NOT NULL AND modelo_version = ?"
            " ORDER BY ticker, fecha", conn, params=(modelo_version,))
    finally:
        conn.close()

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


def contrastar(df: pd.DataFrame) -> pd.DataFrame:
    """Compara cada afirmación ORIGINAL de la §2 contra lo que da el
    harness. Esas cifras se escribieron con la convención `estricta`, así
    que reproducen bajo ella — es la verificación histórica del
    pre-registro, distinta de la línea base oficial de la §2.8."""
    zm = zona_muerta(df)
    fila25 = zm[zm["umbral"] == 0.25]
    R = {"duelo": duelo(df), "magnitud": magnitud(df),
         "calibracion": calibracion(df), "salud": salud_r2_regimen_beta(df),
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

    L = [f"# Línea base del campeón {MODELO_VERSION} — reproducción de la §2",
         "",
         f"- Generado: {datetime.now(timezone.utc).isoformat()}",
         f"- Fuente: `senales.db` en `mode=ro` (autoridad), NO los CSV de respaldo",
         f"- Convención de empate: **{convencion}**",
         f"- Filas: **n = {d['n']}** · {df['fecha'].min()} → {df['fecha'].max()}",
         "",
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
    contraste = contrastar(aplicar_convencion(base_df, "estricta"))
    fallan = contraste[contraste["veredicto"] != "reproduce"]
    oficial = contrastar_linea_oficial(
        aplicar_convencion(base_df, CONVENCION_OFICIAL))
    of_mal = oficial[oficial["veredicto"] != "coincide"]
    cb = contrastar_bloques(df)
    cb_mal = cb[cb["veredicto"] != "reproduce"]
    r2 = duelo_excluyendo(df, *VENTANA_R2)
    L += ["## Línea base OFICIAL (§2.8, congelada)", "",
          f"Convención congelada: **`{CONVENCION_OFICIAL}`** — las filas con "
          "`gap_pct == 0.00` se excluyen de ambos lados (artefactos del ffill "
          "de feriados). La exclusión vive en esta capa de medición; "
          "`senales.py` no se toca.", "",
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
