# ============================================================
# GEMELO/universo_por_presupuesto.py — el universo operable por presupuesto,
# con acciones ENTERAS, para la reevaluación del monto de E2 que el §86.3
# prevé por acta antes de E2. Corrida 13 (19-sep-2026), encargo §8 (bloque 6).
#
#   python -m GEMELO.universo_por_presupuesto            # escribe GEMELO/resultados/universo_por_presupuesto.{md,json}
#
# QUÉ MIDE, por presupuesto de 100 a 500 USD de a 50:
#   · cuántos y cuáles instrumentos verificados alcanzan UNA acción entera al
#     último cierre congelado (`dinero/datos/cierres_congelados.csv`, hasta
#     2026-09-04), con el mismo `construir_mapa` del riel (piso de comisión
#     incluido);
#   · una COTA SUPERIOR NOMINAL de posiciones (una acción entera de cada una,
#     las más baratas primero, sin comisión; regla que la cuenta no usa);
#   · qué fracción de las K semillas del juego conservador se CONGELA (la
#     cuenta deja de operar por falta de caja para una acción entera antes de
#     las 156 semanas, misma definición que `GEMELO.m2_periodo.lecturas_m2`,
#     exigencia E4 del adversario del §43), con Wilson 95 % sobre K rotulado
#     como error de simulación sobre UN solo camino de mercado, y la fricción
#     a 156 semanas CONDICIONADA al estado (vivas / congeladas).
#
# LO QUE EL ADVERSARIO EXIGIÓ (dictamen_13/adversario_universo_presupuesto.md)
# y está acá: la «verificación» contra la corrida 12 es una REPRODUCCIÓN
# determinista (mismas semillas, misma rama) y su valor se lee de m2_periodo.json;
# `universo_operable` depende del techo, así que las filas NO son pareadas (la
# membresía en DESDE va como columna y la tabla no se lee en columna); tres
# poblaciones y tres fechas por fila, separadas en dos tablas.
#
# QUÉ NO HACE: no fija ni recomienda el monto. Estatus PROPUESTA (tabla
# DESCRIPTIVA, sin verdad conocida para este estimador). Sin red.
# ============================================================
from __future__ import annotations

import copy
import json
import os
import sys
from datetime import datetime, timezone

import pandas as pd

from dinero import contabilidad as C
from dinero import cuenta_papel as CP
from dinero import precios
from dinero import universo_dinero as U
from GEMELO.m2_periodo import lecturas_m2

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, ".claude", "skills", "estadistica-evaluacion", "scripts"))
from evaluacion import wilson_ci  # noqa: E402

SALIDA = os.path.join(RAIZ, "GEMELO", "resultados", "universo_por_presupuesto")
PRESUPUESTOS = [float(p) for p in range(100, 501, 50)]
JUEGO = "conservador"
HORIZONTE_CONGELACION = 156
# REPRODUCCIÓN DETERMINISTA (no verificación: misma función, mismas semillas, mismo
# congelado, y 500 USD es el techo por defecto de reglas.json, o sea la misma rama
# que m2_periodo.correr) del artefacto de la corrida 12: se LEE de m2_periodo.json,
# no se escribe acá. Es un chequeo de regresión; no puede ver un error compartido.
RUTA_M2 = os.path.join(RAIZ, "GEMELO", "resultados", "m2_periodo.json")


def _referencia_corrida_12() -> dict | None:
    if not os.path.exists(RUTA_M2):
        return None
    with open(RUTA_M2, encoding="utf-8") as f:
        m = json.load(f)
    celda = m["resumen"][JUEGO][f"pct_a_{HORIZONTE_CONGELACION}_semanas"]
    return {"presupuesto_usd": 500.0, "semillas_congeladas": celda["semillas_congeladas"], "K": celda["K"],
            "fuente": f"GEMELO/resultados/m2_periodo.json → resumen.{JUEGO}.pct_a_{HORIZONTE_CONGELACION}_semanas"}


def _cfg_con_techo(cfg: dict, presupuesto: float) -> dict:
    c = copy.deepcopy(cfg)
    c["presupuesto"]["techo_usd"] = float(presupuesto)
    return c


def alcance_enteras(cierres: pd.DataFrame, cfg: dict, presupuesto: float) -> dict:
    """Con `construir_mapa` sobre los cierres hasta el último congelado."""
    mapa = U.construir_mapa(cierres, _cfg_con_techo(cfg, presupuesto))
    ver = [f for f in mapa if f.verificado]
    alcanzan = sorted((f.candidato.ticker, round(float(f.precio), 2), int(f.acciones_con_techo))
                      for f in ver if f.alcanza_con_techo)
    no_alcanzan = sorted((f.candidato.ticker, round(float(f.precio), 2)) for f in ver if not f.alcanza_con_techo)
    # cota superior NOMINAL de diversificación: una acción entera de cada una, las más
    # baratas primero, sobre el precio crudo (sin comisión). La cuenta NO compra así
    # (compra por señal, con aporte semanal): es una cota, no una cartera (adversario, 6).
    precios_ord = sorted(p for _, p, _ in alcanzan)
    acumulado, caben = 0.0, 0
    for p in precios_ord:
        if acumulado + p <= presupuesto:
            acumulado += p
            caben += 1
        else:
            break
    return {"presupuesto_usd": presupuesto, "verificados": len(ver), "alcanzan_una_accion_entera": len(alcanzan),
            "tickers_alcanzan": [t for t, _, _ in alcanzan], "precios_alcanzan": {t: p for t, p, _ in alcanzan},
            "acciones_con_techo": {t: n for t, _, n in alcanzan},
            "no_alcanzan": [t for t, _ in no_alcanzan], "precios_no_alcanzan": {t: p for t, p in no_alcanzan},
            "cota_superior_posiciones_nominal": caben,
            "cota_superior_posiciones_nota": "más baratas primero, precio crudo sin comisión, regla que la cuenta no usa; punto de un solo día"}


def semillas_congeladas(completo: pd.DataFrame, cfg: dict, presupuesto: float, K: int) -> dict:
    """Corre la cuenta en papel v2 con el techo dado y cuenta, con la definición
    de `lecturas_m2`, las semillas del juego conservador congeladas antes de
    156 semanas. Wilson 95 % sobre K (unidad = semilla)."""
    c = _cfg_con_techo(cfg, presupuesto)
    pb = c["costos"]["deslizamiento_pb_por_lado"]
    operables = CP.universo_operable(completo, c, hasta=CP.DESDE)
    por_semilla = []
    for i in range(K):
        sen = C.senales_sin_informacion(completo, operables, CP.HORIZONTE_SENAL_HABILES,
                                        C.SEMILLA_SENAL_SIN_INFORMACION + i, desde=CP.DESDE)
        _, res = CP.correr(completo, c, sen)
        lec = lecturas_m2(res, c, pb)[JUEGO]
        por_semilla.append({"semilla": C.SEMILLA_SENAL_SIN_INFORMACION + i,
                            "congelada": bool(lec.get(f"congelada_antes_de_{HORIZONTE_CONGELACION}")),
                            "friccion_pct_a_156": lec.get(f"pct_a_{HORIZONTE_CONGELACION}_semanas")})
    congeladas = sum(1 for x in por_semilla if x["congelada"])
    lo, hi = wilson_ci(congeladas, K)

    def _resumen(vals):
        v = [x for x in vals if x is not None]
        return {"n": len(v), "mediana": (round(float(pd.Series(v).median()), 2) if v else None),
                "min_max": ([round(min(v), 2), round(max(v), 2)] if v else None)}
    # la fricción se reporta CONDICIONADA al estado (vivas / congeladas): la mezcla es
    # bimodal y su mediana salta de modo según quién sea mayoría (adversario, 3)
    return {"K": K, "semillas_congeladas": congeladas, "fraccion": round(congeladas / K, 3),
            "wilson_95_error_de_simulacion": [round(lo, 3), round(hi, 3)],
            "wilson_nota": "Wilson sobre K semillas = error de Monte Carlo condicional a UN solo camino de mercado; no es incertidumbre de mundo",
            "friccion_pct_a_156_vivas": _resumen([x["friccion_pct_a_156"] for x in por_semilla if not x["congelada"]]),
            "friccion_pct_a_156_congeladas": _resumen([x["friccion_pct_a_156"] for x in por_semilla if x["congelada"]]),
            "friccion_definicion": "100 × comisiones acumuladas / capital aportado acumulado, a 156 semanas, SIN anualizar (m2_periodo.lecturas_m2)",
            "operables_en_DESDE": len(operables), "tickers_operables_en_DESDE": list(operables),
            "por_semilla": por_semilla}


def correr(K: int = CP.K_SEMILLAS, presupuestos=PRESUPUESTOS) -> dict:
    cfg = U.reglas()
    completo = precios.cargar_congelado()
    meta = precios.meta_congelado()
    hasta = str(completo.index.max().date())
    filas = []
    for P in presupuestos:
        a = alcance_enteras(completo.loc[:hasta], cfg, P)
        s = semillas_congeladas(completo, cfg, P, K)
        filas.append({**a, **{f"conservador_{k}": v for k, v in s.items()}})
    ref = _referencia_corrida_12()
    en_500 = next((f for f in filas if f["presupuesto_usd"] == 500.0), None)
    reproduccion = None
    if ref is not None and en_500 is not None:
        reproduccion = {**ref, "recomputado": en_500["conservador_semillas_congeladas"], "K_recomputado": en_500["conservador_K"],
                        "coincide": (en_500["conservador_semillas_congeladas"] == ref["semillas_congeladas"] and en_500["conservador_K"] == ref["K"]),
                        "que_es": "reproducción determinista (misma función, mismas semillas, mismo congelado): chequeo de regresión, NO verificación independiente"}
    return {
        "generado_en_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estatus": "PROPUESTA — insumo para la reevaluación del monto de E2 (acta §86.3); no fija ni recomienda ningún monto; hasta el dictamen del estadistico-adversario",
        "que_es": ("universo operable con acciones ENTERAS por presupuesto, al último cierre del congelado grande, con el "
                   "`construir_mapa` del riel; posiciones simultáneas = una acción entera de cada instrumento, las más baratas "
                   "primero; semillas congeladas = cuenta en papel v2 (señal sin información, K semillas) cuyo último movimiento "
                   "es anterior a 156 − 26 semanas (definición de `GEMELO.m2_periodo.lecturas_m2`, E4 del §43)"),
        "congelado": {"archivo": os.path.basename(precios.RUTA_CIERRES), "hasta": hasta, "sha256": meta.get("sha256"),
                      "tickers": len(meta.get("tickers", []))},
        "juego": JUEGO, "K": K, "reglas_version": cfg.get("version_reglas"), "presupuestos_usd": list(presupuestos),
        "reproduccion_corrida_12": reproduccion,
        "filas": filas,
        "lectura": ("las filas NO son pareadas ni anidadas: `universo_operable` depende del techo, así que a cada presupuesto la "
                    "cuenta juega con otra membresía (columna «operables en DESDE») y, con la misma semilla, otro flujo de sorteos. "
                    "La tabla no se lee en columna: comparar la fracción de congeladas entre presupuestos mezcla presupuesto, "
                    "membresía y realización. Tres poblaciones y tres fechas por fila, separadas en la tabla."),
        "advertencias": [
            "una semilla congelada acumula poca comisión por QUIEBRA operativa, no por baratura (E4 del §43)",
            "los cierres del congelado son ajustados retroactivamente por yfinance: no point-in-time (declarado)",
            "la membresía del universo se fija en DESDE (2023-09-05) para la cuenta y al último cierre para el alcance: son dos preguntas distintas y se declaran las dos",
        ],
    }


def informe(r: dict) -> str:
    L = ["# Universo operable por presupuesto, con acciones enteras", "",
         f"- Generado: {r['generado_en_utc']} · congelado `{r['congelado']['archivo']}` hasta {r['congelado']['hasta']} "
         f"(sha256 `{(r['congelado']['sha256'] or '')[:12]}…`, {r['congelado']['tickers']} tickers) · juego `{r['juego']}` · K = {r['K']} semillas · reglas {r['reglas_version']}",
         f"- **Estatus: {r['estatus']}**",
         f"- **Cómo se lee:** {r['lectura']}", ""]
    v = r.get("reproduccion_corrida_12")
    if v:
        L.append(f"- Reproducción determinista del artefacto de la corrida 12 (NO verificación independiente: misma función, mismas semillas, mismo congelado): "
                 f"a {v['presupuesto_usd']:.0f} USD `m2_periodo.json` dice {v['semillas_congeladas']} de {v['K']} semillas congeladas; recomputado "
                 f"{v['recomputado']} de {v['K_recomputado']} → {'COINCIDE' if v['coincide'] else 'NO COINCIDE (parar y reportar)'}.")
    L += ["", "## A. Alcance con acciones enteras al último cierre congelado (36 verificados al 2026-09-04)", "",
          "| Presupuesto | Alcanzan 1 acción entera | Cota superior nominal de posiciones (más baratas primero, sin comisión; regla que la cuenta no usa) | No alcanzan |",
          "|---|---|---|---|"]
    for f in r["filas"]:
        L.append(f"| {f['presupuesto_usd']:.0f} USD | **{f['alcanzan_una_accion_entera']} de {f['verificados']}** | {f['cota_superior_posiciones_nominal']} | "
                 f"{', '.join(f['no_alcanzan']) or '—'} |")
    L += ["", f"## B. Cuenta en papel v2, juego `{r['juego']}`, K = {r['K']} sorteos sin información sobre UN camino de mercado (membresía fijada en DESDE = 2023-09-05, que depende del techo)", "",
          "| Presupuesto | Operables en DESDE | Semillas congeladas antes de 156 sem. | Wilson 95 % (error de simulación, un solo camino) | Fricción a 156 sem., VIVAS: n · mediana [mín, máx] | Fricción a 156 sem., CONGELADAS: n · mediana [mín, máx] |",
          "|---|---|---|---|---|---|"]
    for f in r["filas"]:
        vv, cc = f["conservador_friccion_pct_a_156_vivas"], f["conservador_friccion_pct_a_156_congeladas"]
        L.append(f"| {f['presupuesto_usd']:.0f} USD | {f['conservador_operables_en_DESDE']} | {f['conservador_semillas_congeladas']} de {f['conservador_K']} "
                 f"({100*f['conservador_fraccion']:.0f} %) | [{100*f['conservador_wilson_95_error_de_simulacion'][0]:.0f} %, {100*f['conservador_wilson_95_error_de_simulacion'][1]:.0f} %] | "
                 f"{vv['n']} · {vv['mediana'] if vv['mediana'] is not None else '—'} % {vv['min_max'] or ''} | "
                 f"{cc['n']} · {cc['mediana'] if cc['mediana'] is not None else '—'} % {cc['min_max'] or ''} |")
    L += ["", f"Fricción = {r['filas'][0]['conservador_friccion_definicion']}. Se reporta condicionada al estado porque la mezcla es bimodal y su "
          "mediana salta de modo según quién sea mayoría; una cuenta congelada acumula poca comisión por QUIEBRA operativa, no por baratura (E4 del §43).",
          "", "## Quiénes alcanzan, por presupuesto", ""]
    for f in r["filas"]:
        L.append(f"- **{f['presupuesto_usd']:.0f} USD:** " + ", ".join(f"{t} ({f['precios_alcanzan'][t]:.2f})" for t in f["tickers_alcanzan"]))
    L += ["", "## Advertencias", ""] + [f"- {a}" for a in r["advertencias"]]
    L += ["", "Ninguna fila de esta tabla fija el monto de E2: es el insumo de la reevaluación que el §86.3 prevé por acta. "
          "Tabla DESCRIPTIVA: no hay corrida con verdad conocida para la fracción de semillas congeladas ni para su Wilson "
          "(`instrumento_dinero.py` valida otro estimador); si alguna fila fuera a informar un umbral, el simulador se extiende primero. "
          "El barrido (9 presupuestos × 20 semillas) está declarado en `dinero/registro_intentos.py` como una hipótesis descriptiva; "
          "elegir después un presupuesto de esta tabla no es pre-especificarlo."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--K", type=int, default=CP.K_SEMILLAS)
    ap.add_argument("--salida", default=SALIDA)
    a = ap.parse_args(argv)
    r = correr(K=a.K)
    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    with open(a.salida + ".md", "w", encoding="utf-8") as f:
        f.write(informe(r))
    with open(a.salida + ".json", "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(a.salida + ".md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
