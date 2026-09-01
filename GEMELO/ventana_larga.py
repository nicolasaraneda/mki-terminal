# ============================================================
# GEMELO/ventana_larga.py — WS3: la misma comparación del WS2b, sobre
# TODA la historia disponible (Etapa 6.0.0).
#
#   source venv/bin/activate
#   python -m GEMELO.ventana_larga
#
# ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1, y la distinción es precisa:
# el veredicto de la 5.1 es el criterio ESCALONADO capa-contra-capa sobre
# B0→B5, con sus reglas congeladas en el GATE B, y su ejecución es
# decisión humana. Aquí NO se calcula el veredicto escalonado ni se emite
# juicio sobre B0→B5. El campeón reconstruido aparece SOLO como término de
# comparación del retador.
#
# POR QUÉ EXISTE ESTA ETAPA
# El WS2b concluyó que el conjunto de información expandido no aporta,
# pero esa conclusión estaba sub-potenciada: C2 vs C1 no se distinguía de
# cero sobre la ventana sellada del WS2b. Con esa muestra no se puede
# distinguir "no hay señal" de "la señal no se ve". El cuello de botella no
# era información: era muestra. Y la muestra existe.
#
# ERRATA (2026-09-01) — este encabezado y el reporte de abajo citaban
# "p=0.36 sobre 215 filas". Esa cifra está SUPERADA: la línea base corregida
# congela n=223, +4.0 pp, p=0.4633 bajo la convención `excluir_cero`
# (`GEMELO/DISEÑO.md` §2.8; las filas con gap==0.00 son artefactos de ffill
# y se excluyen de AMBOS lados). Un número retirado que sigue ofrecido en el
# código vuelve a circular: por eso se corrige aquí y no sólo en prosa.
#
# CÓMO SE RECONSTRUYE EL CAMPEÓN
# Con la MISMA función de producción (`motor.prediccion_apertura_al`, vía
# `backtest.baselines.B2Produccion` — auditoría, no imitación). Lo único
# que cambia es la profundidad de la serie que se le sirve: se inyecta un
# histórico más largo en `FuenteCongelada(series=..., ohlc=...)`, que es
# su punto de extensión declarado. Como `betas_al` usa una ventana rodante
# de 120 sesiones, **el cómputo del campeón en cada fecha es idéntico al
# que haría en vivo**; solo se amplía el rango de fechas computables.
# `motor.py` no se toca.
# ============================================================

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

import motor
from universo import (INDICE_LOCAL_POR_EXCHANGE, MERCADOS_POR_ABRIR,
                      PARES_FX, UNIVERSO)
from backtest import baselines as bl
from backtest import inferencia as inf
from backtest.datos import FuenteCongelada

from GEMELO import control_lineal as cl
from GEMELO import datos, features
from GEMELO.experimento import construir_panel

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "resultados")

# ------------------------------------------------------------
# CONTEO DE INTENTOS — declarado en GEMELO/DISEÑO.md §4.2 bis ANTES de
# correr nada. Regla: cuenta como UN intento cada par
# (configuración × ventana de evaluación) con resultado reportable.
#   6  B0-B5 sobre la ventana del backtest
#   3  C1,C2,C3 sobre la ventana sellada (WS2b)
#   3  C1,C2,C3 sobre la ventana larga (WS3)
#   1  campeón reconstruido (= B2) sobre la ventana larga
# = 13. La baseline "siempre al alza" NO cuenta: es la hipótesis nula, no
# un modelo ajustado. La búsqueda de alpha tampoco: no mira evaluación.
# ------------------------------------------------------------
N_INTENTOS_WS3 = 13

ANIOS = 8
SUBVENTANA_FILAS = 200      # tamaño de sub-ventana para la distribución R2

# La n canónica de la ventana sellada del WS2b, congelada en
# `GEMELO/DISEÑO.md` §2.8 bajo la convención `excluir_cero` (n=223, +4.0 pp,
# p=0.4633). Sustituye al 215 que este módulo seguía ofreciendo — ver la
# ERRATA del encabezado.
N_WS2B_CANONICO = 223


def _descargar_para_el_campeon(anios: int, usar_cache: bool) -> tuple:
    """Series y OHLC que `FuenteCongelada` necesita, con MÁS profundidad
    que `motor.ANIOS_DATOS`. Se inyectan; no se modifica motor.py."""
    import yfinance as yf
    extras = ("^SOX",) + tuple(PARES_FX) + tuple(INDICE_LOCAL_POR_EXCHANGE.values())
    todos = tuple(sorted(set(list(UNIVERSO.keys()) + list(extras))))
    series = datos.descargar_cierres(todos, anios=anios, usar_cache=usar_cache)
    ohlc = {}
    data = yf.download(list(MERCADOS_POR_ABRIR), period=f"{anios}y",
                       interval="1d", auto_adjust=True, progress=False)
    for t in MERCADOS_POR_ABRIR:
        try:
            d = pd.DataFrame({"Open": data["Open"][t], "Close": data["Close"][t]})
        except KeyError:
            continue
        ohlc[t] = d.dropna(how="all")
    return series, ohlc


def correr(anios: int = ANIOS, usar_cache: bool = True,
           embargo_dias: int = cl.EMBARGO_DIAS) -> dict:
    # --- features y etiquetas de GEMELO (8 años) ---
    series_g, descartadas = datos.series_para_investigacion(
        anios=anios, usar_cache=usar_cache)
    feats = features.construir(series_g, verificar=False)
    gaps = datos.descargar_gaps(tuple(MERCADOS_POR_ABRIR), anios=anios,
                                usar_cache=usar_cache)
    panel = construir_panel(feats, gaps)
    panel = panel.sort_values(["fecha", "ticker"]).reset_index(drop=True)

    # --- el campeón, con la función de producción y serie más profunda ---
    series_c, ohlc_c = _descargar_para_el_campeon(anios, usar_cache)
    fechas_eval = sorted(panel["fecha"].unique())
    filas_camp = []
    with FuenteCongelada(series=series_c, ohlc=ohlc_c) as fuente:
        ctx = bl.ContextoRun(fuente, embargo_dias=embargo_dias)
        b2 = bl.B2Produccion(ctx)
        for f in fechas_eval:
            d = pd.Timestamp(f).date()
            try:
                pred = b2.predecir(d)
            except Exception:
                continue
            if pred.empty:
                continue
            for _, fila in pred.iterrows():
                filas_camp.append({"fecha": pd.Timestamp(f),
                                   "ticker": fila["Ticker"],
                                   "pred": float(fila["est"]),
                                   "int80": fila.get("int80")})
    camp = pd.DataFrame(filas_camp)

    # --- evaluación común: filas donde el campeón pudo predecir ---
    evaluacion = panel.merge(camp[["fecha", "ticker"]], on=["fecha", "ticker"],
                             how="inner") if not camp.empty else panel
    if not camp.empty:
        camp = camp.merge(panel[["fecha", "ticker", "gap_pct"]],
                          on=["fecha", "ticker"], how="inner")
        z80 = 1.2816
        camp["sigma"] = (pd.to_numeric(camp["int80"], errors="coerce") / z80)
        camp["sigma"] = camp["sigma"].replace(0.0, np.nan)
        camp["sigma"] = camp["sigma"].fillna(camp["sigma"].median())
        camp["alpha"] = np.nan
        camp["n_train"] = np.nan
        camp = camp[["fecha", "ticker", "pred", "sigma", "alpha", "n_train",
                     "gap_pct"]]

    predicciones, resultados = {}, {}
    for nombre in cl.CONFIGURACIONES:
        df = cl.correr_configuracion(nombre, panel, evaluacion, embargo_dias)
        predicciones[nombre] = df
        resultados[nombre] = cl.evaluar(df, nombre)
    if not camp.empty:
        predicciones["CAMPEON"] = camp
        resultados["CAMPEON"] = cl.evaluar(camp, "CAMPEON")

    pares = []
    for a, b in (("C2", "C1"), ("C3", "C1"), ("C3", "C2"),
                 ("C1", "CAMPEON"), ("C2", "CAMPEON"), ("C3", "CAMPEON")):
        if a in predicciones and b in predicciones:
            pares.append(cl.comparar(predicciones[a], predicciones[b], a, b))

    return {
        "es_veredicto_5_1": False,
        "calcula_veredicto_escalonado": False,
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "parametros": {
            "N_intentos_declarado": N_INTENTOS_WS3,
            "desglose_N": "6 (B0-B5) + 3 (C1-C3 ventana sellada) + "
                          "3 (C1-C3 ventana larga) + 1 (campeón ventana larga)",
            "regla_conteo": "un intento = (configuración × ventana de "
                            "evaluación) con resultado reportable",
            "embargo_dias": embargo_dias,
            "ventana_entrenamiento": "EXPANSIVA (todo el pasado disponible)",
            "alphas_cv": list(cl.ALPHAS_CV), "pliegues_cv": cl.PLIEGUES_CV,
            "minimo_entrenamiento": cl.MINIMO_ENTRENAMIENTO,
            "semilla_bootstrap": cl.SEMILLA_BOOTSTRAP,
            "bloque_bootstrap": cl.BLOQUE_BOOTSTRAP,
            "alpha_bootstrap": cl.ALPHA_BOOTSTRAP,
            "anios_datos": anios,
            "subventana_filas": SUBVENTANA_FILAS,
            "campeon": "motor.prediccion_apertura_al vía B2Produccion, con "
                       "serie inyectada más profunda; ventana de betas 120 "
                       "sesiones (idéntica a producción)",
        },
        "cobertura_features": cobertura_features(feats),
        "validacion_reconstruccion": validar_reconstruccion(panel),
        "descartadas_por_cobertura": descartadas,
        "ventana": {
            "desde": str(panel["fecha"].min().date()) if not panel.empty else None,
            "hasta": str(panel["fecha"].max().date()) if not panel.empty else None,
            "filas_panel": int(len(panel)),
            "filas_evaluacion": int(len(evaluacion)),
            "fechas": int(panel["fecha"].nunique()) if not panel.empty else 0,
        },
        "resultados": resultados,
        "pares": pares,
        "inferencia_sharpe": cl.inferencia_sharpe(resultados, N_INTENTOS_WS3),
        "distribucion_ventaja": {n: distribucion_ventaja(df)
                                 for n, df in predicciones.items()
                                 if not df.empty},
    }


def validar_reconstruccion(panel: pd.DataFrame) -> dict:
    """MIDE la contaminación por revisión de historia en vez de declararla.

    Compara los gaps reconstruidos hoy contra los que el verificador SELLÓ
    en su momento, sobre las filas comunes. Cada fila que difiere es una
    revisión silenciosa de Yahoo: prueba directa, y cuantificada, de que
    esta ventana NO es point-in-time.
    """
    try:
        from backtest import linea_base as lb
        sell = lb.aplicar_convencion(lb.cargar(), lb.CONVENCION_OFICIAL)
    except Exception:
        return {}
    if sell.empty or panel.empty:
        return {}
    sell = sell.copy()
    sell["fecha"] = pd.to_datetime(sell["fecha"])
    j = sell.merge(panel[["fecha", "ticker", "gap_pct"]],
                   on=["fecha", "ticker"], suffixes=("_sellado", "_recon"))
    if j.empty:
        return {}
    dif = (j["gap_pct_sellado"] - j["gap_pct_recon"]).abs()
    difieren = j[dif >= 0.01].assign(dif=dif[dif >= 0.01])
    peores = (difieren.sort_values("dif", ascending=False)
              .head(5)[["fecha", "ticker", "gap_pct_sellado", "gap_pct_recon", "dif"]])
    return {
        "n_comparadas": int(len(j)),
        "coinciden_pct": round(100 * float((dif < 0.01).mean()), 1),
        "difieren": int(len(difieren)),
        "dif_media_pp": round(float(dif.mean()), 4),
        "dif_max_pp": round(float(dif.max()), 4),
        "fechas_con_revision": sorted(
            {str(pd.Timestamp(f).date()) for f in difieren["fecha"]}),
        "peores": [{k: (str(pd.Timestamp(v).date()) if k == "fecha"
                        else (round(float(v), 4) if k != "ticker" else v))
                    for k, v in fila.items()}
                   for fila in peores.to_dict("records")],
    }


def cobertura_features(feats: pd.DataFrame) -> list:
    """Desde cuándo existe cada feature. Sobre una ventana de años el
    catálogo NO es constante: reportarlo es parte del resultado."""
    if feats.empty:
        return []
    filas = []
    for c in feats.columns:
        s = feats[c].dropna()
        filas.append({"feature": c,
                      "desde": str(s.index.min().date()) if len(s) else None,
                      "hasta": str(s.index.max().date()) if len(s) else None,
                      "n": int(len(s)),
                      "cobertura": round(float(feats[c].notna().mean()), 3)})
    return filas


def distribucion_ventaja(df: pd.DataFrame, tam: int = SUBVENTANA_FILAS) -> dict:
    """R2 con potencia: en vez de excluir UNA semana, se mide la
    DISTRIBUCIÓN de la ventaja sobre la baseline por sub-ventana.

    La pregunta que R2 quería hacer —¿la ventaja está repartida o vive en
    unas pocas ventanas afortunadas?— solo tiene respuesta con años de
    datos. Con siete semanas, excluir una es casi una anécdota.
    """
    if df.empty:
        return {}
    d = df.sort_values(["fecha", "ticker"]).reset_index(drop=True)
    gap = d["gap_pct"].to_numpy(float)
    ac = cl._acierto(d["pred"].to_numpy(float), gap)
    base = (gap > 0).astype(int)
    ventajas = []
    for i in range(0, len(d) - tam + 1, tam):
        v = 100 * (ac[i:i + tam].mean() - base[i:i + tam].mean())
        ventajas.append({"desde": str(d["fecha"].iloc[i].date()),
                         "hasta": str(d["fecha"].iloc[i + tam - 1].date()),
                         "ventaja_pp": round(float(v), 1)})
    if not ventajas:
        return {}
    v = np.array([x["ventaja_pp"] for x in ventajas])
    orden = np.sort(v)[::-1]
    # ventaja global tras quitar la MEJOR sub-ventana y el mejor decil
    k = max(1, len(v) // 10)
    return {
        "n_subventanas": len(v), "tam_subventana": tam,
        "ventaja_media_pp": round(float(v.mean()), 2),
        "ventaja_mediana_pp": round(float(np.median(v)), 2),
        "desv_pp": round(float(v.std(ddof=1)), 2) if len(v) > 1 else None,
        "pct_subventanas_positivas": round(100 * float((v > 0).mean()), 1),
        "mejor_pp": round(float(v.max()), 1), "peor_pp": round(float(v.min()), 1),
        "media_sin_la_mejor_pp": round(float(orden[1:].mean()), 2) if len(v) > 1 else None,
        "media_sin_el_mejor_decil_pp": round(float(orden[k:].mean()), 2) if len(v) > k else None,
        "subventanas": ventajas,
    }


# ------------------------------------------------------------
# Informe
# ------------------------------------------------------------
def informe(r: dict) -> str:
    from GEMELO.experimento import _tabla
    p, v = r["parametros"], r["ventana"]
    L = ["# ⚠ ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1", "",
         "Es la **evaluación del retador** sobre la ventana larga (Etapa 6.0.0",
         "WS3). El veredicto de la 5.1 es otra cosa y su distinción es precisa:",
         "es el criterio **escalonado capa-contra-capa sobre B0→B5**, con sus",
         "reglas congeladas en el GATE B, y su ejecución es **decisión humana**.",
         "",
         "**Aquí NO se calcula el veredicto escalonado ni se emite juicio sobre",
         "B0→B5.** El campeón reconstruido aparece SOLO como término de",
         "comparación del retador.",
         "", "---", "",
         "# La ventana real — el mismo experimento con potencia estadística", "",
         f"- Generado: {r['generado_utc']}",
         f"- Ventana: **{v['desde']} → {v['hasta']}** · {v['fechas']} fechas de "
         f"emisión · **{v['filas_evaluacion']} filas de evaluación**",
         f"  (la ventana sellada del WS2b tiene {N_WS2B_CANONICO} filas bajo la "
         f"convención `excluir_cero` de `GEMELO/DISEÑO.md` §2.8; esto es "
         f"**{v['filas_evaluacion'] // N_WS2B_CANONICO}× más**)",
         "",
         "## ⚠ LIMITACIÓN DE PRIMER ORDEN: esto NO es point-in-time", "",
         "**Yahoo reescribe la historia en silencio.** Sus precios vienen",
         "ajustados, y el ajuste se recalcula con cada dividendo y cada split",
         "**posteriores**: la serie de 2019 que se descarga hoy no es la que",
         "existía en 2019. Una reconstrucción a años vista está contaminada por",
         "esa revisión, y la contaminación va en la dirección optimista.",
         "",
         "**Y está MEDIDA, no solo declarada.** Ver la sección siguiente: se",
         "comparan los gaps reconstruidos hoy contra los que el verificador",
         "selló en su momento, fila por fila.",
         "",
         "Esto NO es una nota al pie: es la limitación que gobierna la lectura",
         "de todo lo que sigue. La única defensa real contra ella es el sellado",
         "en vivo sobre datos que no existían cuando se escribió el código — que",
         "el proyecto sí tiene, y que es exactamente la ventana de 223 filas del",
         "WS2b. **La ventana larga da potencia; la ventana sellada da validez.**",
         "Ninguna de las dos reemplaza a la otra.",
         "",
         "## La contaminación por revisión, medida", ""]
    vr = r.get("validacion_reconstruccion") or {}
    if vr:
        L += [f"Sobre las **{vr['n_comparadas']}** filas comunes con el track",
              f"record sellado, la reconstrucción de hoy **coincide en el "
              f"{vr['coinciden_pct']}%** (a menos de 0.01 pp) y **difiere en "
              f"{vr['difieren']}**, con un máximo de **{vr['dif_max_pp']} pp**.",
              "",
              "Cada fila que difiere es una revisión silenciosa entre el día del",
              "sello y hoy. Fechas afectadas: "
              + ", ".join(vr["fechas_con_revision"]) + ".", "",
              "Las mayores diferencias:", "",
              _tabla(vr["peores"]),
              "> **Esto NO se corrige.** Las filas selladas jamás se reescriben;",
              "> si alguna resultara errónea, se documenta como errata. Lo que la",
              "> tabla mide es cuánta confianza merece una reconstrucción a años",
              "> vista — y la respuesta es: bastante, pero no toda.", ""]
    else:
        L += ["(No se pudo comparar contra el track record sellado.)", ""]
    L += ["## Parámetros sellados", "",
         "| Parámetro | Valor |", "|---|---|",
         f"| **N intentos declarado (DSR)** | **{p['N_intentos_declarado']}** |",
         f"| Regla de conteo | {p['regla_conteo']} |",
         f"| Desglose | {p['desglose_N']} |",
         f"| Embargo | {p['embargo_dias']} días |",
         f"| Ventana de entrenamiento | {p['ventana_entrenamiento']} |",
         f"| Alphas de la CV | {p['alphas_cv']} |",
         f"| Pliegues de la CV temporal | {p['pliegues_cv']} |",
         f"| Mínimo de entrenamiento | {p['minimo_entrenamiento']} filas |",
         f"| Semilla / bloque / alpha del bootstrap | {p['semilla_bootstrap']} / "
         f"{p['bloque_bootstrap']} / {p['alpha_bootstrap']} |",
         f"| Años de datos | {p['anios_datos']} |",
         f"| Sub-ventana para la distribución | {p['subventana_filas']} filas |",
         f"| Campeón | {p['campeon']} |",
         "",
         "**El N subió de 9 a 13** porque re-evaluar las mismas tres",
         "configuraciones sobre una ventana distinta produce un segundo conjunto",
         "de resultados publicables entre los cuales se puede elegir — y elegir",
         "entre resultados es lo que el DSR deflacta. La regla se declaró en",
         "`GEMELO/DISEÑO.md` §4.2 bis **antes** de correr nada.",
         "",
         "## ASIMETRÍA DECLARADA — no supuesta", "",
         "El retador entrena con ventana **expansiva** sobre toda la historia",
         "previa; el campeón usa **120 sesiones rodantes**. Es una diferencia",
         "real de maquinaria y parte de lo que se mide. Por eso C1 existe: mismo",
         "insumo que el campeón, maquinaria nueva. **La comparación que responde",
         "la pregunta de la información es C2 vs C1.**",
         "",
         "## El catálogo de features NO es constante en la ventana", ""]
    L.append(_tabla(r["cobertura_features"]))
    if r["descartadas_por_cobertura"]:
        L += ["Descartadas por la compuerta del 80%:", "",
              _tabla(r["descartadas_por_cobertura"])]
    else:
        L += ["Ninguna serie fue descartada por la compuerta del 80% sobre esta",
              "ventana.", ""]
    L += ["", "## Resultados por configuración", "",
          _tabla(list(r["resultados"].values())),
          "## Comparaciones pareadas", "",
          _tabla(r["pares"]),
          "## R2 con potencia: distribución de la ventaja por sub-ventana", "",
          "Con siete semanas, excluir una era casi una anécdota. Con años de",
          "datos la pregunta de R2 —¿la ventaja está repartida o vive en unas",
          f"pocas ventanas afortunadas?— se responde midiendo la ventaja en",
          f"sub-ventanas de {p['subventana_filas']} filas y mirando su",
          "distribución. `media_sin_la_mejor` y `media_sin_el_mejor_decil` son",
          "la versión con potencia del criterio.", ""]
    resumen = []
    for n, d in r["distribucion_ventaja"].items():
        if d:
            resumen.append({k: v for k, v in d.items() if k != "subventanas"}
                           | {"config": n})
    if resumen:
        cols = ["config"] + [c for c in resumen[0] if c != "config"]
        L.append(_tabla([{c: f[c] for c in cols} for f in resumen]))
    L += ["## ⚠ El Sharpe de estas tablas NO es capturable", "",
          "`sharpe_ls_sin_costos` se construye sobre el **gap**, y el gap es",
          "precisamente lo que NO se puede capturar: es el salto entre el cierre",
          "previo y la apertura, y nadie transa a ese precio. El proyecto ya lo",
          "sabe — por eso su verificador mide el **doble objetivo**: `gap_pct`",
          "responde *¿existe la señal?* y `retorno_real_pct` responde *¿es",
          "capturable?*.",
          "",
          "Un Sharpe de dos cifras sobre gaps es **ficción económica**, no un",
          "hallazgo. Se reporta porque el PSR y el DSR necesitan una serie de",
          "retornos, y se marca así para que nadie lo lea como rendimiento. La",
          "prueba económica de verdad es V6 (SMH, 25 pb por lado) y no está",
          "hecha aquí.", "",
          "## PSR y DSR", "",
          f"Con menos de {cl.MINIMO_DIAS_SHARPE} días de retornos el PSR y el",
          "DSR se reportan como **NO INTERPRETABLE**: un Sharpe anualizado sobre",
          "una muestra diminuta es un artefacto de multiplicar por √252, y el",
          "PSR y el DSR **saturan en 1.0000** — que se leería como que V5 está",
          "superado cuando significa que el instrumento no aplica.", "",
          _tabla(r["inferencia_sharpe"]),
          "**`V_intentos` se estima con la varianza de los Sharpe disponibles",
          "aquí**, no con los de B0→B5 (corrida legacy no comparable,",
          "DECISIONES.md §28.5). Un V subestimado da un SR0 menor y un DSR más",
          "alto del que corresponde: la cifra es una cota superior.", "",
          "**El CRPS usa una predictiva NORMAL**, primera pasada declarada.",
          "`sharpe_ls_sin_costos` es long-short equiponderado **sin costos**: NO",
          "es la prueba del benchmark obligatorio (V6, que exige SMH y 25 pb por",
          "lado).", "",
          "---",
          "Herramienta de análisis — no constituye asesoría financiera.",
          "Diseño congelado en GEMELO/DISEÑO.md. **No es el veredicto de la 5.1**",
          "y **no calcula el veredicto escalonado de B0→B5.**"]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Retador sobre la ventana larga (NO es el veredicto de la 5.1).")
    ap.add_argument("--anios", type=int, default=ANIOS)
    ap.add_argument("--sin-cache", action="store_true")
    ap.add_argument("--sin-escribir", action="store_true")
    args = ap.parse_args(argv)
    r = correr(anios=args.anios, usar_cache=not args.sin_cache)
    texto = informe(r)
    print(texto)
    if not args.sin_escribir:
        os.makedirs(DIR_RESULTADOS, exist_ok=True)
        with open(os.path.join(DIR_RESULTADOS, "ventana_larga.md"), "w",
                  encoding="utf-8") as f:
            f.write(texto)
        with open(os.path.join(DIR_RESULTADOS, "ventana_larga.json"), "w",
                  encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2, default=str)
        print(f"[escrito] {DIR_RESULTADOS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
