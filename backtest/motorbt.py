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
from backtest import cartera, emision, metricas
from backtest.datos import FuenteCongelada, predicciones_selladas

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
REGION = {"XKRX": "Corea", "XTKS": "Japón", "XTAI": "Taiwán",
          "XETR": "Europa", "XNYS": "EE.UU."}
COSTOS_PB = (10, 25, 50)


def correr(desde: date, hasta: date, cuales: tuple = ("B0", "B1", "B2", "B3", "B4", "B5"),
           etiqueta: str = "dry-run", fuente: FuenteCongelada | None = None,
           escribir: bool = True, embargo_dias: int = bl.EMBARGO_DIAS,
           semilla_bootstrap: int = 500, alpha_bootstrap: float = 0.10) -> dict:
    no_concluyente = etiqueta != "5.1"
    fuente = fuente or FuenteCongelada()
    with fuente:
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

    dfs = {n: pd.DataFrame(f) for n, f in filas.items() if f}
    reporte = _evaluar(dfs, smh, descartes, etiqueta, no_concluyente,
                       desde, hasta, embargo_dias=embargo_dias,
                       semilla_bootstrap=semilla_bootstrap,
                       alpha_bootstrap=alpha_bootstrap)
    if escribir:
        reporte["ruta"] = _escribir(reporte, dfs)
    return reporte


def _evaluar(dfs: dict, smh: pd.Series, descartes: int, etiqueta: str,
             no_concluyente: bool, desde: date, hasta: date,
             embargo_dias: int = bl.EMBARGO_DIAS,
             semilla_bootstrap: int = 500,
             alpha_bootstrap: float = 0.10) -> dict:
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
    if r["no_concluyente"]:
        lineas.append("# ⚠ RESULTADO NO-CONCLUYENTE (corrida de humo)\n")
        lineas.append("El gatillo de la Etapa 5.1 no se ha cumplido o el "
                      "usuario no ha disparado la corrida con veredicto. "
                      "Estos números SOLO prueban que la maquinaria "
                      "funciona.\n")
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
    lineas.append("\n## Baselines\n")
    lineas.append(f"| B | n | %grado B | IC medio | t(NW) | MAE gap | "
                  f"Sharpe LS 25pb [IC{nivel}] | acum. LS 25pb |")
    lineas.append("|---|---|---|---|---|---|---|---|")
    for n, b in r["baselines"].items():
        ls = b["carteras"][25]["long_short"]
        lineas.append(
            f"| {n} | {b['n_pares']} | {b['grado_B_pct']}% | {b['ic_medio']} | "
            f"{b['ic_t_nw']} | {b['mae_gap_pp']} | {ls['sharpe']} "
            f"{_ic(ls['sharpe_ic'])} | {ls['acumulado_pct']}% |")
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
