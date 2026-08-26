# ============================================================
# GEMELO/experimento.py — el runner del control lineal (6.0.0 WS2b).
#
#   source venv/bin/activate
#   python -m GEMELO.experimento
#
# ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1. Es una corrida de investigación
# del control lineal del retador. El gatillo de la 5.1 sigue siendo
# decisión humana y sigue sin cumplirse. El reporte lo sella en su primera
# línea para que nadie pueda leerlo como aquello.
#
# AISLAMIENTO: a diferencia de datos.py/features.py/control_lineal.py, este
# runner SÍ importa `backtest.linea_base` — que es la capa de solo lectura
# ya auditada (sqlite `mode=ro`) y la autoridad sobre las filas selladas.
# La dirección que importa para el sello es la contraria: **nada del camino
# de sellado importa GEMELO**, y hay un test que lo verifica. Un fallo aquí
# no puede tocar snapshot.py.
# ============================================================

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from universo import MERCADOS_POR_ABRIR          # constantes puras, sin efectos

from GEMELO import control_lineal as cl
from GEMELO import datos, features

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "resultados")
Z80 = 1.2816   # el mismo cuantil con que el campeón sella su intervalo


def _fecha_emision_por_sesion(sesiones: pd.Series, idx_features: pd.Index) -> pd.Series:
    """La emisión que anticipa una sesión es la última fecha de features
    ESTRICTAMENTE anterior a ella: a las 22:15 UTC del día D ya cerraron
    todas las series (GEMELO/datos.py) y la sesión objetivo aún no abrió."""
    orden = pd.Index(sorted(idx_features))
    pos = orden.searchsorted(pd.to_datetime(sesiones), side="left") - 1
    return pd.Series([orden[p] if p >= 0 else pd.NaT for p in pos],
                     index=sesiones.index)


def construir_panel(feats: pd.DataFrame, gaps: pd.DataFrame) -> pd.DataFrame:
    """Panel de entrenamiento: cada etiqueta (sesión, ticker, gap) pegada a
    las features de la emisión que la anticipa."""
    if feats.empty or gaps.empty:
        return pd.DataFrame()
    g = gaps.copy()
    g["fecha"] = _fecha_emision_por_sesion(g["sesion"], feats.index)
    g = g.dropna(subset=["fecha"])
    panel = g.merge(feats, left_on="fecha", right_index=True, how="left")
    return panel.dropna(subset=["gap_pct"])


def filas_selladas_del_campeon() -> pd.DataFrame:
    """Las 223 filas de la convención congelada en la §2.8 (excluir_cero).
    Se leen por `backtest.linea_base`, que abre senales.db en `mode=ro`."""
    from backtest import linea_base as lb
    df = lb.aplicar_convencion(lb.cargar(), lb.CONVENCION_OFICIAL)
    df = df.rename(columns={"apertura_estimada_pct": "pred_campeon"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df[["fecha", "ticker", "gap_pct", "pred_campeon",
               "intervalo80_pp", "exchange"]]


def evaluar_campeon(sellado: pd.DataFrame) -> pd.DataFrame:
    """El campeón como una configuración más, sobre sus propias filas. Su
    sigma se deriva del intervalo sellado: intervalo80 = z80 · sigma."""
    d = sellado.dropna(subset=["pred_campeon"]).copy()
    d["pred"] = d["pred_campeon"]
    d["sigma"] = (d["intervalo80_pp"] / Z80).replace(0.0, np.nan)
    d["sigma"] = d["sigma"].fillna(d["sigma"].median())
    d["alpha"] = np.nan
    d["n_train"] = np.nan
    return d[["fecha", "ticker", "pred", "sigma", "alpha", "n_train", "gap_pct"]]


def correr(anios: int = 8, usar_cache: bool = True,
           embargo_dias: int = cl.EMBARGO_DIAS) -> dict:
    sellado = filas_selladas_del_campeon()
    series, descartadas = datos.series_para_investigacion(
        anios=anios, usar_cache=usar_cache)
    feats = features.construir(series, verificar=False)
    gaps = datos.descargar_gaps(tuple(MERCADOS_POR_ABRIR), anios=anios,
                                usar_cache=usar_cache)
    panel = construir_panel(feats, gaps)

    evaluacion = sellado.merge(feats, left_on="fecha", right_index=True,
                               how="left")

    predicciones, resultados = {}, {}
    for nombre in cl.CONFIGURACIONES:
        df = cl.correr_configuracion(nombre, panel, evaluacion, embargo_dias)
        predicciones[nombre] = df
        resultados[nombre] = cl.evaluar(df, nombre)

    camp = evaluar_campeon(sellado)
    predicciones["CAMPEON"] = camp
    resultados["CAMPEON"] = cl.evaluar(camp, "CAMPEON")

    pares = []
    for a, b in (("C2", "C1"), ("C3", "C1"), ("C3", "C2"),
                 ("C1", "CAMPEON"), ("C2", "CAMPEON"), ("C3", "CAMPEON")):
        pares.append(cl.comparar(predicciones[a], predicciones[b], a, b))

    return {
        "es_veredicto_5_1": False,
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "parametros": {
            "N_intentos_declarado": cl.N_INTENTOS_DECLARADO,
            "desglose_N": "3 configuraciones (C1,C2,C3) + 6 baselines B0-B5",
            "embargo_dias": embargo_dias,
            "ventana_entrenamiento": "EXPANSIVA (todo el pasado disponible)",
            "alphas_cv": list(cl.ALPHAS_CV),
            "pliegues_cv": cl.PLIEGUES_CV,
            "minimo_entrenamiento": cl.MINIMO_ENTRENAMIENTO,
            "semilla_bootstrap": cl.SEMILLA_BOOTSTRAP,
            "bloque_bootstrap": cl.BLOQUE_BOOTSTRAP,
            "alpha_bootstrap": cl.ALPHA_BOOTSTRAP,
            "anios_datos": anios,
            "convencion_empate": "excluir_cero (§2.8)",
        },
        "descartadas_por_cobertura": descartadas,
        "n_sellado": int(len(sellado)),
        "n_panel": int(len(panel)),
        "resultados": resultados,
        "pares": pares,
        "inferencia_sharpe": cl.inferencia_sharpe(resultados),
        "r2_por_configuracion": [cl.evaluar_r2(df, n)
                                 for n, df in predicciones.items()
                                 if not df.empty],
        "alpha_por_fold": {
            n: sorted(set(round(float(a), 3) for a in df["alpha"].dropna()))
            for n, df in predicciones.items() if not df.empty and "alpha" in df
        },
    }


def _celda(v) -> str:
    """Una celda puede llevar una lista (un IC), así que pd.isna no sirve."""
    if isinstance(v, (list, tuple)):
        return str(list(v))
    try:
        return "" if pd.isna(v) else str(v)
    except (TypeError, ValueError):
        return str(v)


def _tabla(filas) -> str:
    df = pd.DataFrame(filas)
    if df.empty:
        return "(sin filas)\n"
    L = ["| " + " | ".join(df.columns) + " |",
         "|" + "|".join(["---"] * len(df.columns)) + "|"]
    for _, f in df.iterrows():
        L.append("| " + " | ".join(_celda(v) for v in f) + " |")
    return "\n".join(L) + "\n"


def _lectura(r: dict) -> str:
    """Las conclusiones, con las cifras insertadas desde el resultado para
    que no puedan quedar desfasadas de la tabla."""
    par = {p["par"]: p for p in r["pares"]}
    res = r["resultados"]
    r2 = {x["config"]: x for x in r["r2_por_configuracion"]}
    c1c = par.get("C1 vs CAMPEON", {})
    c2c1 = par.get("C2 vs C1", {})
    c3c1 = par.get("C3 vs C1", {})
    L = []

    L.append(
        f"**1. El campeón y C1 aciertan la dirección en las MISMAS filas** "
        f"(McNemar {c1c.get('mcnemar', '?')} sobre n={c1c.get('n', '?')}). No es "
        "casualidad ni error: la predicción del campeón es βᵢ·SOX con βᵢ>0, así "
        "que su signo ES el signo del retorno del SOX — y C1, ridge agrupada "
        "sobre el mismo insumo, lo reproduce exactamente. Consecuencia: "
        "**cualquier diferencia direccional entre C2/C3 y el campeón es "
        "INFORMACIÓN, no maquinaria.** Es justo lo que C1 existía para separar.")

    L.append(
        f"\n**2. La pregunta real —C2 contra C1— no da nada.** Ventaja "
        f"{c2c1.get('ventaja_pp')} pp con McNemar p={c2c1.get('mcnemar_p')}, y el "
        f"IC del ΔMAE {c2c1.get('delta_mae_ic')} **incluye el cero**. Con el "
        "mismo motor y la misma ventana, añadir las catorce features nuevas a "
        "las dos del SOX **no produce una mejora detectable**, ni en dirección "
        "ni en magnitud.")

    L.append(
        f"\n**3. Lo que sí mueve la aguja es la estructura por ticker, y solo "
        f"en magnitud.** C3 contra C1: ΔMAE {c3c1.get('delta_mae')} con IC "
        f"{c3c1.get('delta_mae_ic')}, que **excluye el cero**. En dirección, en "
        f"cambio, p={c3c1.get('mcnemar_p')}: no significativo. Coincide con la "
        "§2.5 — la contribución medible está en la magnitud, no en el signo.")

    c3 = res.get("C3", {})
    c3r2 = r2.get("C3", {})
    L.append(
        f"\n**4. El único p<0.05 del experimento no sobrevive a R2.** C3 contra "
        f"la baseline sobre la ventana completa marca {c3.get('ventaja_pp')} pp "
        f"con p={c3.get('mcnemar_p')}. Excluyendo 15–23 jul cae a "
        f"{c3r2.get('ventaja_pp')} pp con p={c3r2.get('mcnemar_p')}. **La "
        "significancia venía de la misma ventana afortunada que sostiene la "
        "del campeón**, que es exactamente lo que R2 fue escrito para detectar.")

    caen = [c for c, x in r2.items() if not x.get("sobrevive_R2")]
    L.append(
        f"\n**5. Bajo R2 no pasa nadie.** Pierden su ventaja al excluir esa "
        f"ventana: {', '.join(sorted(caen))}. El campeón incluido. Ninguna "
        "configuración supera V1 (McNemar p<0.05) con R2 aplicado.")

    L.append(
        "\n**6. El resultado es NEGATIVO, y se publica tal cual.** El §6.3 del "
        "pre-registro lo dice: un retador que no supera al campeón, y un "
        "campeón que no supera a una constante, es un resultado. No se probó "
        "una cuarta variante buscando el positivo — esa tentación es "
        "literalmente el sesgo que el DSR mide, y habría subido N a 10.")
    return "\n".join(L)


def informe(r: dict) -> str:
    p = r["parametros"]
    L = ["# ⚠ ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1", "",
         "Es una **corrida de investigación del control lineal del retador**",
         "(Etapa 6.0.0 WS2b, §4.3 del pre-registro). El backtest con veredicto",
         "del campeón es otra cosa: su gatillo sigue siendo decisión humana y",
         "**sigue sin cumplirse** (N=228 sí, cambio de régimen no).",
         "", "---", "",
         "# Control lineal — el conjunto de información expandido, ¿trae señal?",
         "",
         f"- Generado: {r['generado_utc']}",
         f"- Filas selladas evaluadas: **{r['n_sellado']}** "
         f"(convención `{p['convencion_empate']}`)",
         f"- Panel de entrenamiento: {r['n_panel']} filas",
         "",
         "## Parámetros sellados", "",
         f"| Parámetro | Valor |", "|---|---|",
         f"| **N intentos declarado (DSR)** | **{p['N_intentos_declarado']}** "
         f"— {p['desglose_N']} |",
         f"| Embargo | {p['embargo_dias']} días |",
         f"| Ventana de entrenamiento | {p['ventana_entrenamiento']} |",
         f"| Alphas de la CV | {p['alphas_cv']} |",
         f"| Pliegues de la CV temporal | {p['pliegues_cv']} |",
         f"| Mínimo de entrenamiento | {p['minimo_entrenamiento']} filas |",
         f"| Semilla del bootstrap | {p['semilla_bootstrap']} |",
         f"| Bloque del bootstrap | {p['bloque_bootstrap']} |",
         f"| Alpha del bootstrap | {p['alpha_bootstrap']} |",
         f"| Años de datos | {p['anios_datos']} |",
         "",
         "**La búsqueda de alpha NO suma a N.** Se resuelve por CV temporal",
         "dentro de cada ventana de entrenamiento, sin tocar jamás una fila de",
         "evaluación. Lo que el DSR debe contar son las decisiones tomadas",
         "MIRANDO el resultado de evaluación, y ésta no lo es.",
         "",
         "### Alphas efectivamente elegidos por fold", "",
         "```", json.dumps(r["alpha_por_fold"], ensure_ascii=False), "```", "",
         "## ASIMETRÍA DECLARADA — no supuesta", "",
         "El retador entrena sobre **años** de historia con ventana expansiva;",
         "el campeón usa **120 sesiones rodantes**. Es una diferencia real de",
         "maquinaria y es **parte de lo que se está midiendo**, no un detalle",
         "de implementación. Por eso existe C1: usa el MISMO conjunto de",
         "información que el campeón (el SOX, t y t-1) con la maquinaria nueva.",
         "**La comparación que responde la pregunta real es C2 contra C1**, no",
         "C2 contra el campeón — ésta última mezcla información y maquinaria.",
         "",
         "## Las configuraciones", ""]
    for n, c in cl.CONFIGURACIONES.items():
        L.append(f"- **{n}** — {c['descripcion']}")
    L += ["", "## Resultados por configuración", "",
          _tabla(list(r["resultados"].values())),
          "La baseline «siempre al alza» sobre estas mismas filas está en la",
          "columna `base_pct`. `sharpe_ls_sin_costos` es un proxy económico de",
          "primera pasada (long-short equiponderado, **sin costos**): es",
          "optimista por construcción y NO es la prueba del benchmark",
          "obligatorio (§6.1 V6, que exige SMH y 25 pb por lado).",
          "",
          "## Comparaciones pareadas", "",
          "Sobre las filas que **ambas** configuraciones predijeron. `delta_mae`",
          "> 0 significa que A tiene MENOS error que B; su IC sale del bootstrap",
          "circular de bloques.", "",
          _tabla(r["pares"]),
          "## Lectura", "",
          _lectura(r), "",
          "## R2 del §6.2 aplicado a cada configuración", "",
          f"R2 descarta a quien pierda su ventaja al excluir la ventana "
          f"{cl.VENTANA_R2[0]}–{cl.VENTANA_R2[1]}, que sostiene casi toda la "
          "ventaja del campeón (§2.2). Se aplica por FECHAS, no por índice de "
          "bloque (§2.8.2). Al propio campeón esta prueba lo deja en ventaja "
          "NEGATIVA sobre las 223 filas — es una valla que hoy nadie tenía "
          "superada.", "",
          _tabla(r["r2_por_configuracion"]),
          "## PSR y DSR", "",
          f"**Aviso que manda sobre la tabla:** con menos de "
          f"{cl.MINIMO_DIAS_SHARPE} días, un Sharpe ANUALIZADO no es una "
          "estimación sino un artefacto de multiplicar por √252, y el PSR y "
          "el DSR **saturan en 1.0000**. Un DSR de 1.000 NO significa que V5 "
          "(DSR ≥ 0.95) esté superado: significa que el instrumento no aplica "
          "a esta muestra. Por eso se reportan como NO INTERPRETABLE en vez de "
          "emitir el número.", "",
          _tabla(r["inferencia_sharpe"]),
          "**`V_intentos` está SUBESTIMADA y por tanto el DSR es una cota",
          "superior optimista.** Se estima con la varianza de los Sharpe",
          "disponibles aquí; los de las seis baselines B0→B5 vienen de una",
          "corrida legacy con bootstrap no circular y sin embargo",
          "(DECISIONES.md §28.5), así que no se mezclan. Un V menor da un SR0",
          "menor y un DSR más alto del que corresponde.",
          "",
          "**El CRPS usa una predictiva NORMAL**, declarado como primera",
          "pasada: ridge entrega punto más varianza residual. La §2.7 ya mostró",
          "colas más gruesas que la normal en este objetivo, así que este CRPS",
          "es una cota optimista. La densidad con colas (Student-t) es el Nivel",
          "4 del retador, no de este control.", ""]
    if r["descartadas_por_cobertura"]:
        L += ["## Series descartadas por cobertura", "",
              _tabla(r["descartadas_por_cobertura"])]
    L += ["---",
          "Herramienta de análisis — no constituye asesoría financiera.",
          "Diseño congelado en GEMELO/DISEÑO.md. **No es el veredicto de la 5.1.**"]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Control lineal del retador (NO es el veredicto de la 5.1).")
    ap.add_argument("--anios", type=int, default=8)
    ap.add_argument("--sin-cache", action="store_true")
    ap.add_argument("--sin-escribir", action="store_true")
    args = ap.parse_args(argv)

    r = correr(anios=args.anios, usar_cache=not args.sin_cache)
    texto = informe(r)
    print(texto)
    if not args.sin_escribir:
        os.makedirs(DIR_RESULTADOS, exist_ok=True)
        with open(os.path.join(DIR_RESULTADOS, "control_lineal.md"), "w",
                  encoding="utf-8") as f:
            f.write(texto)
        with open(os.path.join(DIR_RESULTADOS, "control_lineal.json"), "w",
                  encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2, default=str)
        print(f"[escrito] {DIR_RESULTADOS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
