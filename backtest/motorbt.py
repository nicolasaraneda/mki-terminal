# ============================================================
# El loop walk-forward (DISEÑO.md §9) — único punto de entrada.
#
#   source venv/bin/activate
#   python -m backtest.motorbt --desde 2026-04-01 --hasta 2026-07-20
#
# Toda corrida escribe backtest/resultados/<id>/ (resumen.md versionable;
# CSV/JSON gitignorados). Mientras el gatillo de la Etapa 5.1 no se cumpla
# Y el usuario no lo dispare, TODA salida se marca NO-CONCLUYENTE.
# ============================================================

import argparse
import json
import os
import subprocess
from datetime import date, datetime, timezone

import pandas as pd

from universo import BENCHMARK, EXCHANGE_POR_TICKER, MERCADOS_POR_ABRIR

from backtest import baselines as bl
from backtest import cartera, causalidad, emision, metricas
from backtest.datos import FuenteCongelada, predicciones_selladas

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
REGION = {"XKRX": "Corea", "XTKS": "Japón", "XTAI": "Taiwán",
          "XETR": "Europa", "XNYS": "EE.UU."}
COSTOS_PB = (10, 25, 50)

# Prefijo de las corridas CON veredicto. Una etiqueta que empieza por "5.1"
# deja de ser corrida de humo; si además viene un `estado_gatillo` que
# declara el gatillo INCUMPLIDO, el resumen lo dice en la primera pantalla.
# Son TRES estados, no dos: humo / veredicto con gatillo incumplido /
# veredicto pleno. Colapsarlos en dos es lo que permitiría que una corrida
# ejecutada antes de tiempo se leyera como el veredicto definitivo.
PREFIJO_VEREDICTO = "5.1"


def correr(desde: date, hasta: date, cuales: tuple = ("B0", "B1", "B2", "B3", "B4", "B5"),
           etiqueta: str = "dry-run", fuente: FuenteCongelada | None = None,
           escribir: bool = True, embargo_dias: int = bl.EMBARGO_DIAS,
           semilla_bootstrap: int = 500, alpha_bootstrap: float = 0.10,
           estado_gatillo: dict | None = None,
           fechas_gate: tuple | None = None) -> dict:
    no_concluyente = not etiqueta.startswith(PREFIJO_VEREDICTO)
    fuente = fuente or FuenteCongelada()
    with fuente:
        # GATE DE CAUSALIDAD (B-2): antes de emitir una sola fila. Reconstruye
        # el arnés con la fuente truncada en cada fecha declarada y exige
        # predicción idéntica. Si algo se mueve, la corrida MUERE aquí — R3
        # no admite excepciones. `fechas_gate=None` lo declara NO EJECUTADO
        # en el reporte: no ejecutarlo no puede quedar en silencio.
        if fechas_gate:
            gate = causalidad.gate(fuente, fechas_gate, cuales,
                                   embargo_dias=embargo_dias)
        else:
            gate = {"ejecutado": False,
                    "resultado": "NO EJECUTADO — la corrida no declaró fechas "
                                 "de gate; ninguna afirmación de ausencia de "
                                 "fuga se apoya en este reporte"}
        ctx = bl.ContextoRun(fuente, embargo_dias=embargo_dias)
        modelos = bl.construir_baselines(ctx, cuales)
        instantes = emision.emisiones(desde, hasta)

        filas: dict = {n: [] for n in cuales}
        descartes = 0
        for instante in instantes:
            D = instante.date()
            objetivos = {}
            for ex in {EXCHANGE_POR_TICKER[t] for t in MERCADOS_POR_ABRIR}:
                try:
                    objetivos[ex] = emision.sesion_objetivo(ex, instante)
                except Exception:
                    continue
            outcomes = {}
            for t in MERCADOS_POR_ABRIR:
                obj = objetivos.get(EXCHANGE_POR_TICKER[t])
                if obj is None:
                    continue
                resultado = fuente.resultado_sesion(t, obj[0])
                if resultado is None:
                    descartes += 1
                    continue
                outcomes[t] = {"sesion_objetivo": obj[0], **resultado}
            if not outcomes:
                continue
            regimen_dia = ctx.regimen[ctx.regimen.index.date <= D]
            regimen_dia = (str(regimen_dia.iloc[-1])
                           if len(regimen_dia) and pd.notna(regimen_dia.iloc[-1])
                           else "sin régimen")
            for nombre_b, modelo in modelos.items():
                pred = modelo.predecir(D)
                for _, p in pred.iterrows():
                    t = p["Ticker"]
                    if t not in outcomes:
                        continue
                    filas[nombre_b].append({
                        "fecha_emision": D.isoformat(), "ticker": t,
                        "exchange": EXCHANGE_POR_TICKER[t],
                        "region": REGION.get(EXCHANGE_POR_TICKER[t]),
                        "regimen": regimen_dia,
                        "est": float(p["est"]),
                        "int80": (float(p["int80"]) if p["int80"] is not None
                                  and p["int80"] == p["int80"] else None),
                        "grado": p["grado"],
                        **outcomes[t],
                    })

        smh = fuente.serie_benchmark(BENCHMARK)
        cobertura_sent = {**ctx.sentimiento.cobertura(),
                          "accesos_con_sentimiento": ctx.filas_con_sentimiento,
                          "accesos_sin_sentimiento": ctx.filas_sin_sentimiento}

    dfs = {n: pd.DataFrame(f) for n, f in filas.items() if f}
    reporte = _evaluar(dfs, smh, descartes, etiqueta, no_concluyente,
                       desde, hasta, embargo_dias=embargo_dias,
                       semilla_bootstrap=semilla_bootstrap,
                       alpha_bootstrap=alpha_bootstrap,
                       estado_gatillo=estado_gatillo)
    reporte["gate_causalidad"] = gate
    reporte["cobertura_sentimiento"] = cobertura_sent
    if escribir:
        reporte["ruta"] = _escribir(reporte, dfs)
    return reporte


def _evaluar(dfs: dict, smh: pd.Series, descartes: int, etiqueta: str,
             no_concluyente: bool, desde: date, hasta: date,
             embargo_dias: int = bl.EMBARGO_DIAS,
             semilla_bootstrap: int = 500,
             alpha_bootstrap: float = 0.10,
             estado_gatillo: dict | None = None) -> dict:
    ics = {n: metricas.rank_ic_diario(df) for n, df in dfs.items()}
    resumen_bl = {}
    for n, df in dfs.items():
        ic = ics[n]
        carteras = {}
        for costo in COSTOS_PB:
            series = cartera.retornos_cartera(df, costo)
            carteras[costo] = {
                lado: {
                    "sharpe": metricas.sharpe_anual(series[lado]),
                    # el nombre ya no fija el nivel: el alpha es parámetro
                    "sharpe_ic": metricas.bootstrap_sharpe(
                        series[lado], semilla=semilla_bootstrap,
                        alpha=alpha_bootstrap),
                    "mdd_pct": metricas.max_drawdown(series[lado]),
                    "acumulado_pct": round(float(
                        ((1 + series[lado] / 100).prod() - 1) * 100), 1)
                    if len(series[lado]) else None,
                } for lado in ("long_only", "long_short")}
        por_dimension = {}
        for dim in ("region", "regimen"):
            por_dimension[dim] = {
                str(v): {"n": len(g),
                         "ic_medio": (round(float(metricas.rank_ic_diario(g).mean()), 4)
                                      if len(metricas.rank_ic_diario(g)) else None),
                         "mae": metricas.mae_gap(g)}
                for v, g in df.groupby(dim)}
        resumen_bl[n] = {
            "n_pares": int(len(df)),
            "grado_B_pct": round(100 * float((df["grado"] == "B").mean()), 1),
            # grado S = la fila se emitió SIN un solo juicio de IA
            # disponible y el hueco se rellenó con el neutro 0.0. Antes esto
            # no se contaba: el relleno viajaba como si fuera dato.
            "grado_S_sin_noticias_pct": round(
                100 * float((df["grado"] == "S").mean()), 1),
            "n_filas_con_sentimiento_real": int((df["grado"].isin(("A", "B"))).sum())
            if n in ("B4", "B5") else None,
            "ic_medio": round(float(ic.mean()), 4) if len(ic) else None,
            "ic_t_nw": (round(metricas.t_newey_west(ic), 2)
                        if len(ic) >= 10 else None),
            "hits": metricas.hits_condicionados(df),
            "mae_gap_pp": metricas.mae_gap(df),
            "calibracion": metricas.calibracion(df),
            "carteras": carteras,
            "por_dimension": por_dimension,
        }

    fechas = (pd.to_datetime(sorted({f for df in dfs.values()
                                     for f in df["fecha_emision"]}))
              if dfs else pd.DatetimeIndex([]))
    ret_smh = cartera.benchmark_smh(smh, fechas)
    bench = {
        "ticker": BENCHMARK,
        "acumulado_pct": (round(float(((1 + ret_smh / 100).prod() - 1) * 100), 1)
                          if len(ret_smh) else None),
        "sharpe": metricas.sharpe_anual(ret_smh),
        "mdd_pct": metricas.max_drawdown(ret_smh),
    }

    # Auditoría de reproducción de B2 contra los sellos reales
    auditoria = None
    if "B2" in dfs:
        sellados = predicciones_selladas()
        if not sellados.empty:
            join = dfs["B2"].merge(
                sellados, left_on=["fecha_emision", "ticker"],
                right_on=["fecha", "ticker"], how="inner")
            if not join.empty:
                dif = (join["est"] - join["apertura_estimada_pct"]).abs()
                auditoria = {"n_comparadas": int(len(join)),
                             "dif_media_pp": round(float(dif.mean()), 3),
                             "dif_max_pp": round(float(dif.max()), 3),
                             "nota": ("las diferencias reflejan deriva de datos "
                                      "de la fuente entre el sello y hoy "
                                      "(hallazgo 4.7.1), no necesariamente un bug")}

    return {
        "etiqueta": etiqueta,
        "no_concluyente": no_concluyente,
        "estado_gatillo": estado_gatillo,
        "periodo": {"desde": desde.isoformat(), "hasta": hasta.isoformat()},
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "commit": _commit_actual(),
        # Los parámetros que definen la corrida van SELLADOS en el reporte:
        # una corrida cuyo embargo no queda escrito no es reproducible, y el
        # embargo cambia los resultados.
        "parametros": {"embargo_dias": embargo_dias,
                       "ventana_entrenamiento": bl.VENTANA_ENTRENAMIENTO,
                       "dias_reajuste": bl.DIAS_REAJUSTE,
                       "bootstrap": {"metodo": "circular de bloques "
                                                "(Politis & Romano 1994)",
                                     "semilla": semilla_bootstrap,
                                     "alpha": alpha_bootstrap,
                                     "bloque_dias": 10, "replicas": 2000}},
        "descartes_sin_datos": descartes,
        "baselines": resumen_bl,
        "benchmark_smh": bench,
        "auditoria_b2": auditoria,
        "veredicto_escalonado": metricas.veredicto_escalonado(ics),
    }


def _commit_actual() -> str | None:
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                       capture_output=True, text=True,
                       cwd=os.path.dirname(DIR_RESULTADOS))
    return r.stdout.strip() or None


def _escribir(reporte: dict, dfs: dict) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    ruta = os.path.join(DIR_RESULTADOS, f"{stamp}-{reporte['etiqueta']}")
    os.makedirs(ruta, exist_ok=True)
    with open(os.path.join(ruta, "metricas.json"), "w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2, default=str)
    for n, df in dfs.items():
        df.to_csv(os.path.join(ruta, f"predicciones_{n}.csv"), index=False)
    with open(os.path.join(ruta, "resumen.md"), "w", encoding="utf-8") as f:
        f.write(_resumen_md(reporte))
    return ruta


def _ic(par) -> str:
    """Redondeo de PRESENTACIÓN del intervalo. La métrica se guarda con toda
    su precisión en metricas.json; aquí se recorta para que la tabla se lea."""
    if not par:
        return "—"
    return f"[{par[0]:.2f}, {par[1]:.2f}]"


def _resumen_md(r: dict) -> str:
    lineas = []
    gat = r.get("estado_gatillo") or {}
    if r["no_concluyente"]:
        lineas.append("# ⚠ RESULTADO NO-CONCLUYENTE (corrida de humo)\n")
        lineas.append("El gatillo de la Etapa 5.1 no se ha cumplido o el "
                      "usuario no ha disparado la corrida con veredicto. "
                      "Estos números SOLO prueban que la maquinaria "
                      "funciona.\n")
    elif gat and not gat.get("cumplido", False):
        # Primera pantalla, no nota al pie: una corrida de veredicto
        # ejecutada con el gatillo sin cumplir tiene que decirlo arriba de
        # todo o se leerá como el veredicto definitivo. Y si además hay
        # fugas DEMOSTRADAS, la corrida no es "no concluyente": es
        # INVÁLIDA, que es una cosa peor y distinta.
        fugas = gat.get("fugas") or []
        if fugas:
            lineas.append("# ⛔ CORRIDA **INVALIDADA POR FUGA** — NO es el "
                          "veredicto de la Etapa 5.1\n")
            lineas.append("**R3 de `GEMELO/DISEÑO.md` §6.2 dice: *«cualquier "
                          "fuga detectada por el test de causalidad. Sin "
                          "discusión y sin excepción»*. Se detectaron fugas "
                          "DEMOSTRADAS y medidas en el arnés antes de correr. "
                          "Ninguna cifra de este documento puede citarse como "
                          "resultado del backtest:**\n")
            for f in fugas:
                lineas.append(f"- {f}")
            lineas.append("")
            lineas.append("Los números que siguen se publican **sólo** como "
                          "evidencia de que la maquinaria corre punta a punta "
                          "y como referencia para dimensionar la "
                          "contaminación. **No son un veredicto y no aprueban "
                          "ni reprueban ningún criterio.**\n")
        else:
            lineas.append("# ⚠ CORRIDA DE VEREDICTO CON EL GATILLO "
                          "**NO CUMPLIDO**\n")
            lineas.append("**Esto NO es el veredicto definitivo de la Etapa "
                          "5.1.** El gatillo congelado en "
                          "`backtest/DISEÑO.md` §11 no está cumplido por "
                          "ninguna de sus dos vías:\n")
        lineas.append("Estado del gatillo congelado (`backtest/DISEÑO.md` §11):\n")
        for via in gat.get("vias", []):
            lineas.append(f"- {via}")
        lineas.append("")
        correcciones = gat.get("correcciones_2026_09_01") or []
        if correcciones:
            lineas.append("**Correcciones del arnés aplicadas antes de esta "
                          "corrida** (la corrección va al ejecutable, no al "
                          "texto):\n")
            for c in correcciones:
                lineas.append(f"- {c}")
            lineas.append("")
        abiertos = gat.get("defectos_abiertos") or []
        if abiertos:
            lineas.append("**Defectos del arnés ABIERTOS.** No son fugas "
                          "temporales —R3 no los juzga— pero bloquean el "
                          "veredicto igual, y decirlo separado es la "
                          "diferencia entre *«el arnés tiene fuga»* y *«el "
                          "arnés tiene la unidad de observación mal»*:\n")
            for d in abiertos:
                lineas.append(f"- {d}")
            lineas.append("")
        if gat.get("holdout_intacto", True):
            lineas.append("**El holdout en cuarentena NO se evaluó y queda "
                          "INTACTO.** `GEMELO/DISEÑO.md` §6.1 V7 lo define "
                          "como *evaluado una sola vez*: es un recurso "
                          "irreversible y gastarlo con el gatillo sin "
                          "cumplir lo quemaría para siempre. V7 queda "
                          "NO EVALUABLE por esta razón, no por falta de "
                          "maquinaria.\n")
        if gat.get("expediente"):
            lineas.append(f"Expediente de la decisión pendiente: "
                          f"`{gat['expediente']}`.\n")
    else:
        lineas.append("# ✅ CORRIDA DE VEREDICTO — Etapa 5.1\n")
        lineas.append("Gatillo cumplido y corrida disparada por el usuario. "
                      "Estos números SÍ constituyen el veredicto.\n")
    lineas.append(f"# Backtest MKI — {r['etiqueta']} · "
                  f"{r['periodo']['desde']} → {r['periodo']['hasta']}\n")
    par = r.get("parametros", {})
    lineas.append(f"Generado {r['generado_utc']} · commit {r['commit']} · "
                  f"descartes sin datos: {r['descartes_sin_datos']}\n")
    bs = par.get("bootstrap", {})
    nivel = (f"{100 * (1 - bs['alpha']):.0f}" if "alpha" in bs else "?")
    lineas.append(f"Parámetros: embargo {par.get('embargo_dias', '?')} días · "
                  f"ventana entrenamiento {par.get('ventana_entrenamiento', '?')} · "
                  f"reajuste cada {par.get('dias_reajuste', '?')} días\n")
    lineas.append(f"Bootstrap: {bs.get('metodo', '?')} · bloque "
                  f"{bs.get('bloque_dias', '?')} días · "
                  f"{bs.get('replicas', '?')} réplicas · semilla "
                  f"{bs.get('semilla', '?')} · IC {nivel}%\n")
    gate = r.get("gate_causalidad") or {}
    if gate.get("ejecutado"):
        lineas.append(f"Gate de causalidad: **{gate['resultado']}** · "
                      f"{gate['n_comparaciones']} comparaciones "
                      f"({gate['n_fechas']} fechas × "
                      f"{len(gate['baselines'])} baselines) · invariancia al "
                      f"truncado de precios, OHLC **y noticias** · "
                      f"contraprueba `shift(-1)` en la suite\n")
    else:
        lineas.append(f"Gate de causalidad: **{gate.get('resultado', 'NO EJECUTADO')}**\n")
    cob = r.get("cobertura_sentimiento") or {}
    if cob.get("filas_ticker_analisis"):
        lineas.append(
            f"Sentimiento point-in-time (B-1): el corte es "
            f"`max(publicación, analizado_en) <= 22:15 UTC` — el juicio de la "
            f"IA sólo existe cuando existe. {cob['pct_tarde']}% de los "
            f"{cob['filas_ticker_analisis']} pares (titular × ticker) "
            f"quedaron disponibles DESPUÉS de su publicación (rezago máximo "
            f"{cob['rezago_max_dias']} días); el primer dato disponible es "
            f"del **{cob['primer_dia_con_dato_disponible']}** aunque el "
            f"primer titular sea del {cob['primer_titular_publicado']}. "
            f"Accesos a la feature con sentimiento real: "
            f"**{cob['accesos_con_sentimiento']}**; sin ninguno (relleno "
            f"neutro declarado, grado S): **{cob['accesos_sin_sentimiento']}**.\n")
    lineas.append("\n## Baselines\n")
    lineas.append(f"| B | n | %grado B | %grado S (sin noticias) | IC medio | "
                  f"t(NW) | MAE gap | Sharpe LS 25pb [IC{nivel}] | acum. LS 25pb |")
    lineas.append("|---|---|---|---|---|---|---|---|---|")
    for n, b in r["baselines"].items():
        ls = b["carteras"][25]["long_short"]
        lineas.append(
            f"| {n} | {b['n_pares']} | {b['grado_B_pct']}% | "
            f"{b.get('grado_S_sin_noticias_pct', 0.0)}% | {b['ic_medio']} | "
            f"{b['ic_t_nw']} | {b['mae_gap_pp']} | {ls['sharpe']} "
            f"{_ic(ls['sharpe_ic'])} | {ls['acumulado_pct']}% |")
    sin_noticias = [n for n, b in r["baselines"].items()
                    if n in ("B4", "B5")
                    and (b.get("grado_S_sin_noticias_pct") or 0) >= 50.0]
    if sin_noticias:
        detalle_s = " · ".join(
            f"{n}: {r['baselines'][n]['grado_S_sin_noticias_pct']}%"
            for n in sin_noticias)
        lineas.append(
            f"\n**{' y '.join(sin_noticias)} NO son evaluables sobre esta "
            f"ventana.** Filas emitidas SIN un solo juicio de IA disponible "
            f"({detalle_s}): sus tres features de noticias "
            f"valen el relleno neutro 0.0 y la capa colapsa a la anterior. "
            f"Sus cifras se leen como lo que son —la capa de precios con "
            f"columnas constantes—, no como *«las noticias no aportan»*. "
            f"**B0, B1, B2 y B3 no tocan el sentimiento y siguen evaluables "
            f"sobre la ventana completa.**\n")
    smh = r["benchmark_smh"]
    lineas.append(f"\n**Benchmark obligatorio — comprar {smh['ticker']} y no "
                  f"hacer nada**: acumulado {smh['acumulado_pct']}% · Sharpe "
                  f"{smh['sharpe']} · MDD {smh['mdd_pct']}% — toda cartera se "
                  f"lee CONTRA esta línea (ajuste GATE B).\n")
    lineas.append("\n## Veredicto escalonado (capa vs capa)\n")
    lineas.append("| Capa | ΔIC | t(NW) | días | veredicto |")
    lineas.append("|---|---|---|---|---|")
    for v in r["veredicto_escalonado"]:
        lineas.append(f"| {v['capa']} | {v.get('delta_ic', '—')} | "
                      f"{v.get('t_nw', '—')} | {v['n_dias']} | {v['veredicto']} |")
    aud = r.get("auditoria_b2")
    if aud:
        lineas.append(f"\n## Auditoría B2 vs sellos reales\n"
                      f"{aud['n_comparadas']} predicciones comparadas · "
                      f"diferencia media {aud['dif_media_pp']} pp · máx "
                      f"{aud['dif_max_pp']} pp. {aud['nota']}.\n")
    lineas.append("\n---\nHerramienta de análisis — no constituye asesoría "
                  "financiera. Diseño congelado en backtest/DISEÑO.md.\n")
    return "\n".join(lineas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtest walk-forward MKI B0→B5")
    parser.add_argument("--desde", required=True)
    parser.add_argument("--hasta", required=True)
    parser.add_argument("--baselines", default="B0,B1,B2,B3,B4,B5")
    parser.add_argument("--etiqueta", default="dry-run",
                        help="'5.1' SOLO cuando el usuario dispare la corrida "
                             "con veredicto (gatillo del GATE B cumplido)")
    parser.add_argument("--embargo-dias", type=int, default=bl.EMBARGO_DIAS,
                        help="jornadas purgadas entre entrenamiento y prueba "
                             "(López de Prado 2018 cap. 7); 0 lo desactiva")
    parser.add_argument("--semilla-bootstrap", type=int, default=500,
                        help="semilla del bootstrap; queda sellada en el reporte")
    parser.add_argument("--alpha-bootstrap", type=float, default=0.10,
                        help="1-alpha es el nivel del IC del Sharpe (0.10 → IC90)")
    args = parser.parse_args()
    reporte = correr(date.fromisoformat(args.desde), date.fromisoformat(args.hasta),
                     tuple(args.baselines.split(",")), args.etiqueta,
                     embargo_dias=args.embargo_dias,
                     semilla_bootstrap=args.semilla_bootstrap,
                     alpha_bootstrap=args.alpha_bootstrap)
    print(f"resultados en {reporte['ruta']}")
    if reporte["no_concluyente"]:
        print("⚠ NO-CONCLUYENTE (ver resumen.md)")
