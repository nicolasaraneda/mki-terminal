# ============================================================
# La corrida de VEREDICTO de la Etapa 5.1 — B0→B5 contra los criterios
# CONGELADOS de backtest/DISEÑO.md §8 y GEMELO/DISEÑO.md §6 (V1–V7, R1–R3).
#
# Este módulo NO define ni mueve un solo criterio: los lee donde están
# congelados y los aplica. Todo parámetro de la corrida está declarado
# ANTES de correr en GEMELO/resultados/gatillo_51.md, incluido el
# N_intentos del Deflated Sharpe.
#
#   source venv/bin/activate
#   python -m backtest.veredicto_51
#
# LO QUE ESTE MÓDULO NO HACE, A PROPÓSITO:
#   - NO evalúa el holdout en cuarentena. GEMELO/DISEÑO.md §6.1 V7 lo define
#     como "evaluado una sola vez": es irreversible, el gatillo del GATE B
#     no está cumplido, y gastarlo hoy lo quemaría para siempre. V7 sale
#     NO EVALUABLE por esa razón, no por falta de maquinaria.
#   - NO escribe en senales.db ni en noticias.db (mode=ro heredado de
#     backtest/datos.py).
# ============================================================

import json
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude", "skills", "estadistica-evaluacion", "scripts"))
import evaluacion as ev  # noqa: E402

from backtest import cartera, inferencia, metricas, motorbt  # noqa: E402
from backtest.datos import FuenteCongelada, predicciones_selladas  # noqa: E402

# ------------------------------------------------------------
# PARÁMETROS — declarados en GEMELO/resultados/gatillo_51.md §2 el
# 2026-09-01 01:42 hora de Chile, ANTES de correr. Cambiar cualquiera de
# éstos después de ver los resultados sería elegir la configuración
# favorable; por eso viven aquí, en una sola pantalla, y no dispersos.
# ------------------------------------------------------------
DESDE = date(2024, 9, 2)      # 250 sesiones de burn-in del ^SOX cumplidas
HASTA = date(2026, 8, 28)     # último viernes con desenlace completo
SEMILLA_BOOTSTRAP = 20260901
ALPHA_BOOTSTRAP = 0.05        # IC 95%: más ancho, más exigente que el 0.10
ETIQUETA = "5.1-arnes-corregido-gatillo-incumplido"

# Fechas del GATE DE CAUSALIDAD — declaradas ANTES de correr, repartidas
# por la ventana (una por trimestre aproximado, más los bordes). Doce, no
# una: la prueba maestra anterior cubría UNA fecha y tres baselines, así
# que las cinco features exclusivas de B4/B5 eran invisibles.
FECHAS_GATE = (date(2024, 10, 15), date(2024, 12, 10), date(2025, 2, 11),
               date(2025, 4, 15), date(2025, 6, 10), date(2025, 8, 12),
               date(2025, 10, 14), date(2025, 12, 9), date(2026, 2, 10),
               date(2026, 4, 14), date(2026, 6, 9), date(2026, 8, 11))

# N_intentos del DSR — §1.4 del expediente declaró 82 el 2026-09-01 01:42
# (25 en código + 1 declarado no corrido + 18 en prosa + 32 reconstruidos +
# 6 de la corrida de esa noche). Esta corrida vuelve a mirar las SEIS
# baselines sobre la misma ventana con el arnés CORREGIDO: por la regla
# congelada, seis configuraciones más. La §1.4 no se reescribe — la
# corrección se agrega al pie con su fecha, que es la regla de la casa.
#
# 82 + 6 = 88. Se sube y no se reusa: bajar N es lo único que el DSR no
# perdona, y contar de más es el lado seguro del error.
N_INTENTOS_51 = 88
BANDA_N = (26, 44, 82, 88, 110)

# Un Sharpe ANUALIZADO sobre pocas decenas de días es un artefacto de
# multiplicar por √252. Espejo de GEMELO/control_lineal.py:81 — abajo de
# esto, PSR y DSR se reportan NO INTERPRETABLE, jamás el número.
MINIMO_DIAS_SHARPE = 60

# GEMELO/DISEÑO.md §6.2 R2: la ventana que sostiene casi toda la ventaja
# del campeón. Se aplica por RANGO DE FECHAS, no por índice de bloque.
VENTANA_R2 = ("2026-07-15", "2026-07-23")

# GEMELO/DISEÑO.md §6.1 V3 y V4: las varas congeladas.
V3_COBERTURA = (76.0, 84.0)
V4_MAE_CAMPEON_SELLADO = 3.064   # pp, §2.5 — ventana SELLADA, no ésta
CAMPEON = "B2"                   # el modelo de producción 4.6.0 tal cual

Z80 = 1.2815515655446004

ESTADO_GATILLO = {
    "cumplido": False,
    "vias": [
        "**(a)** N ≥ 150 verificaciones limpias **Y** un cambio de régimen "
        "del SOX: 261 verificaciones limpias — CUMPLE la primera mitad —, "
        "pero el track record tiene **una sola etiqueta de régimen** "
        "(`Alcista · vol alta`, 38 snapshots, más 2 nulos). La conjunción "
        "**NO se cumple**.",
        "**(b)** 3 meses continuos desde el 25-jul-2026: faltan **54 días** "
        "(cae el 25-oct-2026). **NO se cumple**.",
    ],
    "holdout_intacto": True,
    "expediente": "GEMELO/resultados/gatillo_51.md",
    # Fugas DEMOSTRADAS. B-1 y B-2 quedaron CORREGIDAS el 2026-09-01 y
    # están reproducidas en la suite; la lista se vacía porque el arreglo
    # fue al ejecutable, no a la prosa. Lo que NO se arregló vive abajo, en
    # `defectos_abiertos`, y sigue bloqueando el veredicto — sólo que por
    # otra razón que R3.
    "fugas": [],
    "correcciones_2026_09_01": [
        "**B-1 CORREGIDA** — `SentimientoPIT` corta por "
        "`max(publicación, analizado_en) <= 22:15 UTC`: hacen falta LAS DOS "
        "marcas para que el juicio exista. (El acta lo había escrito como "
        "`min()`; con el mínimo el predicado colapsa al roto, porque "
        "`analizado_en` es posterior a la publicación por construcción — "
        "errata para DECISIONES.md.) `buzz` pasa por el mismo corte y "
        "estrena grado propio; el relleno neutro dejó de viajar como si "
        "fuera dato y se declara como **grado S**. Tests: "
        "`tests/test_backtest.py::test_b1_*` (5).",
        "**B-2 CORREGIDA** — el corte lo hace ahora `recortar_pit()`, que "
        "recibe la serie SIN recortar, y la guarda de verdad es el GATE DE "
        "CAUSALIDAD (`backtest/causalidad.py`): reconstruye el arnés entero "
        "—precios, OHLC **y noticias**— con la fuente truncada en D y exige "
        "predicción idéntica. Corre DENTRO de la corrida, sobre 12 fechas × "
        "6 baselines, y la mata si algo se mueve. Contraprueba permanente: "
        "10 tests parametrizados inyectan `shift(-1)` en cada feature "
        "—incluidas las cinco exclusivas de B4/B5— y exigen que el gate "
        "DISPARE. Una guarda sin contraprueba no es una guarda.",
    ],
    # NO son fugas temporales, y por eso no las juzga R3. Bloquean el
    # veredicto igual, y decirlo separado es la diferencia entre "el arnés
    # tiene fuga" y "el arnés tiene la unidad de observación mal".
    "defectos_abiertos": [
        "**B-3 · el mismo desenlace cuenta hasta 8 veces.** Varias "
        "emisiones consecutivas apuntan a la MISMA sesión objetivo en "
        "feriados largos y `motorbt` escribe una fila por emisión con el "
        "outcome repetido. **No es fuga de futuro: es contaminación de la "
        "unidad de observación.** Se mide en cada corrida "
        "(`impacto_b3_duplicados`) y sigue SIN corregir.",
        "**B4 y B5 no son evaluables sobre la ventana larga.** No es un "
        "defecto del código sino de los datos que existen: el primer juicio "
        "de IA del sistema es del 2026-07-04 y la ventana empieza el "
        "2024-09-02, así que con el corte honesto la enorme mayoría de sus "
        "filas se emiten con las tres features de noticias en el relleno "
        "neutro. Sus cifras NO contestan *«¿las noticias aportan?»*.",
        "**S-1 · el embargo purga días CORRIDOS, no jornadas.** Declarado y "
        "sin corregir; cambiarlo la víspera del veredicto sería mover el "
        "arnés después de haber visto el diseño.",
        "**S-3 · `estado_gatillo` se recibe, no se computa.**",
        "**No hay holdout MATERIAL.** La cuarentena de V7 es procedimental: "
        "no hay split, constante de fecha, archivo ni tabla que reserve "
        "datos. V7 no sólo no se evaluó — hoy no es evaluable.",
        "**La fuente no es point-in-time.** Yahoo reescribe la historia en "
        "silencio; se mide contra los sellos reales en cada corrida "
        "(`fidelidad_b2_vs_sellos`) y es una limitación de primer orden.",
    ],
}


# ------------------------------------------------------------
# Utilidades de lectura
# ------------------------------------------------------------
def _series_ls(df: pd.DataFrame, costo_pb: int = 25) -> pd.Series:
    return cartera.retornos_cartera(df, costo_pb)["long_short"]


def _direcciones(df: pd.DataFrame):
    """Filas evaluables para dirección del gap, con la baseline 'siempre al
    alza' medida SOBRE LAS MISMAS FILAS (jamás contra 50%)."""
    d = df.dropna(subset=["gap_pct"]).copy()
    d = d[d["est"] != 0]                       # B0 no tiene signo que acertar
    if d.empty:
        return None
    acierto = ((d["est"] >= 0) == (d["gap_pct"] >= 0)).to_numpy()
    base = ev.baseline_siempre_alza(d["gap_pct"].to_numpy())
    return d, acierto, base


def _duelo(df: pd.DataFrame) -> dict | None:
    r = _direcciones(df)
    if r is None:
        return None
    d, acierto, base = r
    comp = ev.comparar_pareado(acierto, base)
    lo, hi = ev.wilson_ci(int(acierto.sum()), len(acierto))
    return {
        "n": int(len(acierto)),
        "modelo_pct": round(100 * float(acierto.mean()), 2),
        "wilson95_pp": [round(100 * lo, 2), round(100 * hi, 2)],
        "base_pct": round(100 * float(base.mean()), 2),
        "ventaja_pp": round(100 * float(acierto.mean() - base.mean()), 2),
        "b": int(comp.b), "c": int(comp.c),
        "mcnemar_p": round(float(comp.p_mcnemar), 4),
    }


def _crps(df: pd.DataFrame) -> np.ndarray | None:
    """CRPS de la densidad predictiva gaussiana implícita en (est, int80)."""
    d = df.dropna(subset=["gap_pct", "int80"])
    d = d[d["int80"] > 0]
    if d.empty:
        return None
    sigma = d["int80"].to_numpy() / Z80
    return ev.crps_normal(d["gap_pct"].to_numpy(), d["est"].to_numpy(), sigma), d.index


def _cobertura80(df: pd.DataFrame) -> dict | None:
    d = df.dropna(subset=["gap_pct", "int80"])
    d = d[d["int80"] > 0]
    if len(d) < 30:
        return None
    dentro = (d["gap_pct"] - d["est"]).abs() <= d["int80"]
    k, n = int(dentro.sum()), int(len(dentro))
    lo, hi = ev.wilson_ci(k, n)
    return {"n": n, "cobertura_pct": round(100 * k / n, 2),
            "wilson95_pp": [round(100 * lo, 2), round(100 * hi, 2)]}


# ------------------------------------------------------------
# Los criterios
# ------------------------------------------------------------
def evaluar(reporte: dict, dfs: dict) -> dict:
    crit: dict = {}
    bl_ord = [b for b in ("B0", "B1", "B2", "B3", "B4", "B5") if b in dfs]

    # ---------- V1: habilidad sobre la base (McNemar p < 0.05) ----------
    v1 = {b: _duelo(dfs[b]) for b in bl_ord}
    pasan_v1 = [b for b, d in v1.items()
                if d and d["mcnemar_p"] < 0.05 and d["ventaja_pp"] > 0]
    crit["V1"] = {
        "enunciado": "Ventaja sobre 'siempre al alza' en la misma ventana, "
                     "McNemar p < 0.05 (GEMELO/DISEÑO.md §6.1)",
        "detalle": v1,
        "veredicto": "PASA" if pasan_v1 else "NO PASA",
        "quienes": pasan_v1,
    }

    # ---------- V2: CRPS mejor que el campeón, IC que excluye el cero ----
    v2 = {}
    base_crps = _crps(dfs[CAMPEON]) if CAMPEON in dfs else None
    for b in bl_ord:
        if b == CAMPEON or base_crps is None:
            continue
        propio = _crps(dfs[b])
        if propio is None:
            v2[b] = {"estado": "sin densidad predictiva (int80 ausente)"}
            continue
        # emparejar por (fecha, ticker): sólo filas donde ambos emitieron
        a = dfs[b].loc[propio[1], ["fecha_emision", "ticker"]].copy()
        a["crps"] = propio[0]
        c = dfs[CAMPEON].loc[base_crps[1], ["fecha_emision", "ticker"]].copy()
        c["crps"] = base_crps[0]
        j = a.merge(c, on=["fecha_emision", "ticker"], suffixes=("_x", "_c"))
        if len(j) < 30:
            v2[b] = {"estado": f"sólo {len(j)} filas emparejadas"}
            continue
        # mejora = campeón − retador (positivo = el retador es mejor).
        # IC por bootstrap CIRCULAR de bloques del módulo del proyecto
        # (inferencia.bootstrap_media) — NUNCA el iid ni el no circular:
        # el no circular submuestrea la cola de la serie, que es lo más
        # reciente (DECISIONES.md §28).
        dif = inferencia.bootstrap_media(
            (j["crps_c"] - j["crps_x"]).to_numpy(), semilla=SEMILLA_BOOTSTRAP,
            n_draws=2000, bloque=20, alpha=ALPHA_BOOTSTRAP)
        v2[b] = {"n": int(len(j)),
                 "crps_propio": round(float(j["crps_x"].mean()), 4),
                 "crps_campeon": round(float(j["crps_c"].mean()), 4),
                 "mejora": round(float(dif["media"]), 4),
                 "ic95": [round(dif["lo"], 4), round(dif["hi"], 4)],
                 "excluye_cero": bool(dif["lo"] > 0)}
    pasan_v2 = [b for b, d in v2.items() if d.get("excluye_cero")]
    crit["V2"] = {
        "enunciado": f"Mejora del CRPS sobre el campeón ({CAMPEON}) con IC de "
                     "bootstrap de bloques que excluya el cero",
        "detalle": v2,
        "veredicto": "PASA" if pasan_v2 else "NO PASA",
        "quienes": pasan_v2,
    }

    # ---------- V3: calibración del intervalo 80% en [76, 84] ----------
    v3 = {b: _cobertura80(dfs[b]) for b in bl_ord}
    pasan_v3 = [b for b, d in v3.items()
                if d and V3_COBERTURA[0] <= d["cobertura_pct"] <= V3_COBERTURA[1]]
    crit["V3"] = {
        "enunciado": f"Cobertura empírica del intervalo 80% dentro de "
                     f"[{V3_COBERTURA[0]}%, {V3_COBERTURA[1]}%]",
        "detalle": v3,
        "veredicto": "PASA" if pasan_v3 else "NO PASA",
        "quienes": pasan_v3,
    }

    # ---------- V4: MAE del gap ----------
    mae = {b: reporte["baselines"][b]["mae_gap_pp"] for b in bl_ord}
    mae_campeon = mae.get(CAMPEON)
    mejores = [b for b in bl_ord
               if b != CAMPEON and mae[b] is not None and mae_campeon is not None
               and mae[b] < mae_campeon]
    crit["V4"] = {
        "enunciado": f"MAE del gap estrictamente menor que el del campeón "
                     f"(la vara publicada, {V4_MAE_CAMPEON_SELLADO} pp, es de "
                     f"la ventana SELLADA — aquí se compara EN VENTANA contra "
                     f"el {CAMPEON} de esta misma corrida, que es la "
                     f"comparación honesta)",
        "mae_por_baseline_pp": mae,
        "mae_campeon_en_ventana_pp": mae_campeon,
        "mae_campeon_ventana_sellada_pp": V4_MAE_CAMPEON_SELLADO,
        "veredicto": "PASA" if mejores else "NO PASA",
        "quienes": mejores,
    }

    # ---------- V5: Deflated Sharpe con el N declarado ----------
    sharpes, dias_por_b, momentos = {}, {}, {}
    for b in bl_ord:
        s = _series_ls(dfs[b], 25) / 100.0
        s = s.dropna()
        dias_por_b[b] = int(len(s))
        sharpes[b] = (inferencia.sharpe(s.to_numpy(), anualizar=252)
                      if len(s) >= 2 else float("nan"))
        momentos[b] = ev.momentos(s.to_numpy()) if len(s) >= 4 else (0.0, 3.0)
    validos = [v for v in sharpes.values() if v == v]
    V = float(np.var(validos, ddof=1)) if len(validos) >= 2 else 0.25
    v5 = {}
    for b in bl_ord:
        sr, n = sharpes[b], dias_por_b[b]
        if sr != sr:
            v5[b] = {"estado": "Sharpe indefinido"}
            continue
        if n < MINIMO_DIAS_SHARPE:
            v5[b] = {"sharpe_ls_25pb": round(sr, 3), "dias": n,
                     "psr": "NO INTERPRETABLE", "dsr": "NO INTERPRETABLE",
                     "motivo": f"menos de {MINIMO_DIAS_SHARPE} días"}
            continue
        sk, ku = momentos[b]
        fila = {"sharpe_ls_25pb": round(sr, 3), "dias": n,
                "skew": round(sk, 3), "kurtosis": round(ku, 3),
                "V_intentos": round(V, 4),
                "psr_vs_cero": round(inferencia.psr(sr, 0.0, n, sk, ku), 4),
                "psr_vs_cero_momentos_normales":
                    round(inferencia.psr(sr, 0.0, n, 0.0, 3.0), 4),
                "dsr_por_N": {}}
        for N in BANDA_N:
            sr0 = inferencia.sr0_deflacionado(N, V)
            fila["dsr_por_N"][N] = {
                "sr0": round(sr0, 4),
                "dsr": round(inferencia.dsr(sr, n, sk, ku, N, V), 4),
                "dsr_momentos_normales":
                    round(inferencia.dsr(sr, n, 0.0, 3.0, N, V), 4)}
        v5[b] = fila
    pasan_v5 = [b for b, d in v5.items()
                if isinstance(d.get("dsr_por_N"), dict)
                and d["dsr_por_N"][N_INTENTOS_51]["dsr"] >= 0.95]
    crit["V5"] = {
        "enunciado": f"DSR ≥ 0.95 contando TODOS los intentos "
                     f"(N declarado = {N_INTENTOS_51}; banda {BANDA_N})",
        "N_declarado": N_INTENTOS_51, "banda_N": list(BANDA_N),
        "V_intentos": round(V, 4),
        "nota_saturacion": "Phi satura sobre z≈8.3: un PSR/DSR de 1.0000 "
                           "significa 'más allá de lo que la doble precisión "
                           "distingue', NO 'certeza'.",
        "detalle": v5,
        "veredicto": "PASA" if pasan_v5 else "NO PASA",
        "quienes": pasan_v5,
    }

    # ---------- V6: superar comprar SMH y no hacer nada ----------
    smh = reporte["benchmark_smh"]
    v6 = {}
    for b in bl_ord:
        por_costo = {}
        for costo in motorbt.COSTOS_PB:
            c = reporte["baselines"][b]["carteras"][costo]
            por_costo[costo] = {
                "long_short": {"acum_pct": c["long_short"]["acumulado_pct"],
                               "sharpe": c["long_short"]["sharpe"],
                               "mdd_pct": c["long_short"]["mdd_pct"]},
                "long_only": {"acum_pct": c["long_only"]["acumulado_pct"],
                              "sharpe": c["long_only"]["sharpe"],
                              "mdd_pct": c["long_only"]["mdd_pct"]},
            }
        gana25 = [lado for lado in ("long_short", "long_only")
                  if (por_costo[25][lado]["acum_pct"] is not None
                      and smh["acumulado_pct"] is not None
                      and por_costo[25][lado]["acum_pct"] > smh["acumulado_pct"])]
        v6[b] = {"por_costo": por_costo, "supera_smh_a_25pb": gana25}
    pasan_v6 = [b for b, d in v6.items() if d["supera_smh_a_25pb"]]
    crit["V6"] = {
        "enunciado": "Superar comprar SMH y no hacer nada después de 25 pb "
                     "por lado, con barrido 10/25/50",
        "benchmark_smh": smh, "detalle": v6,
        "veredicto": "PASA" if pasan_v6 else "NO PASA",
        "quienes": pasan_v6,
    }

    # ---------- V7: holdout — NO SE GASTA ----------
    crit["V7"] = {
        "enunciado": "Confirmación en el holdout en cuarentena, evaluado una "
                     "sola vez (GEMELO/DISEÑO.md §6.1)",
        "veredicto": "NO EVALUABLE",
        "razon": "DELIBERADO. El holdout es un recurso de UN SOLO USO y el "
                 "gatillo del GATE B no está cumplido por ninguna de sus dos "
                 "vías. Gastarlo hoy lo quemaría para siempre y no se puede "
                 "deshacer. Queda INTACTO y en cuarentena. Esto NO es una "
                 "limitación de maquinaria: es la decisión de no gastar un "
                 "recurso irreversible antes de tiempo.",
    }

    # ---------- R1: el control lineal le gana ----------
    ic = {b: reporte["baselines"][b]["ic_medio"] for b in bl_ord}
    lineales = [b for b in ("B1", "B3") if b in ic]
    ricos = [b for b in ("B4", "B5") if b in ic]
    gana_lineal = [(l, r) for l in lineales for r in ricos
                   if ic[l] is not None and ic[r] is not None and ic[l] > ic[r]]
    crit["R1"] = {
        "enunciado": "Se descarta al retador si el control lineal le gana",
        "veredicto": "NO EVALUABLE",
        "razon": "R1 está escrito para un RETADOR contra su control lineal, y "
                 "en esta corrida no hay retador: hay seis baselines. Se "
                 "reporta el análogo —capas simples vs capas ricas— sin "
                 "llamarlo R1.",
        "analogo_ic_medio": ic,
        "capas_simples_que_ganan_a_las_ricas": [f"{l} > {r}" for l, r in gana_lineal],
    }

    # ---------- R2: la ventaja sobrevive excluyendo 15–23 jul ----------
    r2 = {}
    for b in bl_ord:
        df = dfs[b]
        fuera = df[~df["fecha_emision"].between(*VENTANA_R2)]
        dentro = df[df["fecha_emision"].between(*VENTANA_R2)]
        r2[b] = {"n_dentro_ventana": int(len(dentro)),
                 "duelo_sin_la_ventana": _duelo(fuera),
                 "duelo_completo": v1[b]}
    sobreviven = [b for b, d in r2.items()
                  if d["duelo_sin_la_ventana"]
                  and d["duelo_sin_la_ventana"]["ventaja_pp"] > 0]
    crit["R2"] = {
        "enunciado": f"Se descarta a quien pierda su ventaja al excluir "
                     f"{VENTANA_R2[0]} → {VENTANA_R2[1]} (por RANGO DE FECHAS)",
        "detalle": r2,
        "veredicto": "PASA" if sobreviven else "NO PASA",
        "quienes_sobreviven": sobreviven,
    }

    # ---------- R3: fuga detectada por el test de causalidad ----------
    # Éste es el criterio que decide, y se computa: se lee el resultado del
    # GATE que la propia corrida ejecutó antes de emitir una sola fila, no
    # una declaración de intenciones. Si el gate no corrió, R3 NO puede
    # declararse limpio — la ausencia de prueba no es prueba de ausencia.
    gate = reporte.get("gate_causalidad") or {}
    hay_fugas = bool(ESTADO_GATILLO.get("fugas"))
    gate_limpio = gate.get("resultado") == "INVARIANTE"
    crit["R3"] = {
        "enunciado": "Cualquier fuga detectada por el test de causalidad. Sin "
                     "discusión y sin excepción.",
        "veredicto": ("PASA" if (gate_limpio and not hay_fugas)
                      else "NO PASA"),
        "gate_de_causalidad": gate,
        "fugas_declaradas": ESTADO_GATILLO.get("fugas") or [],
        "correcciones": ESTADO_GATILLO.get("correcciones_2026_09_01") or [],
        "B1_medida_ahora": medir_fuga_sentimiento(),
        "sentimiento_pit": reporte.get("cobertura_sentimiento"),
        "consecuencia": (
            "R3 no dispara: el test de causalidad —invariancia al truncado "
            "de precios, OHLC y noticias, con contraprueba shift(-1) que lo "
            "hace fallar a propósito— no detecta fuga sobre "
            f"{gate.get('n_comparaciones')} comparaciones. Esto NO convierte "
            "la corrida en el veredicto de la 5.1: el gatillo del GATE B "
            "sigue incumplido y quedan defectos abiertos del arnés que no "
            "son fugas temporales (`defectos_abiertos`)."
            if (gate_limpio and not hay_fugas) else
            "R3 no admite excepciones. Con fuga demostrada —o sin gate que "
            "pueda demostrar lo contrario—, NINGÚN otro criterio de esta "
            "corrida es un veredicto.") ,
        "defectos_abiertos_que_no_son_fuga": ESTADO_GATILLO.get(
            "defectos_abiertos") or [],
    }

    # ---------- El veredicto final del §8 de backtest/DISEÑO.md ----------
    ics = {b: metricas.rank_ic_diario(dfs[b]) for b in bl_ord}

    def _delta_t(a: str, b: str) -> dict:
        if a not in ics or b not in ics:
            return {"estado": "no disponible"}
        par = pd.concat({"a": ics[a], "b": ics[b]}, axis=1).dropna()
        if len(par) < 10:
            return {"estado": f"sólo {len(par)} días"}
        dif = par["a"] - par["b"]
        t = metricas.t_newey_west(dif)
        return {"delta_ic": round(float(dif.mean()), 4),
                "t_nw": round(float(t), 2) if t == t else None,
                "n_dias": int(len(par)),
                "supera": bool(dif.mean() > 0 and t == t and t > 2)}

    cond = {}
    for cand in ("B5", "B4"):
        if cand not in dfs:
            continue
        vs1, vs2 = _delta_t(cand, "B1"), _delta_t(cand, CAMPEON)
        ls25 = reporte["baselines"][cand]["carteras"][25]["long_short"]
        ic_sharpe = ls25["sharpe_ic"]
        sharpe_pos = bool(ls25["sharpe"] is not None and ls25["sharpe"] > 0
                          and ic_sharpe and ic_sharpe[0] > 0)
        bate_smh = bool(ls25["acumulado_pct"] is not None
                        and smh["acumulado_pct"] is not None
                        and ls25["acumulado_pct"] > smh["acumulado_pct"])
        cond[cand] = {
            "supera_B1_en_IC_con_t_mayor_2": vs1,
            f"supera_{CAMPEON}_en_IC_con_t_mayor_2": vs2,
            "sharpe_ls_25pb_positivo_con_IC_sobre_cero": {
                "sharpe": ls25["sharpe"],
                "ic95": ([round(ic_sharpe[0], 3), round(ic_sharpe[1], 3)]
                         if ic_sharpe else None),
                "cumple": sharpe_pos},
            "retorno_supera_buy_and_hold_SMH": {
                "acum_estrategia_pct": ls25["acumulado_pct"],
                "acum_smh_pct": smh["acumulado_pct"],
                "mdd_estrategia_pct": ls25["mdd_pct"],
                "mdd_smh_pct": smh["mdd_pct"],
                "cumple": bate_smh},
            "cumple_las_tres": bool(vs1.get("supera") and vs2.get("supera")
                                    and sharpe_pos and bate_smh),
        }
    # Toda cifra de arriba queda marcada por lo que R3 acaba de dictar.
    for clave, valor in crit.items():
        if clave.startswith("V") and valor.get("veredicto") in ("PASA", "NO PASA"):
            valor["veredicto"] = f"{valor['veredicto']} (SOBRE DATOS CON FUGA — no vale)"

    crit["veredicto_final_diseno_8"] = {
        "enunciado": "La cadena MKI 'agrega valor' si B5 (o B4) supera a B1 Y "
                     "a B2 en rank IC con t > 2, Y el Sharpe neto a 25 pb de "
                     "la long-short es positivo con su intervalo bootstrap "
                     "sobre cero, Y el retorno neto acumulado supera al "
                     "buy-and-hold de SMH (backtest/DISEÑO.md §8)",
        "detalle": cond,
        "veredicto": ("AGREGA VALOR"
                      if any(v["cumple_las_tres"] for v in cond.values())
                      else "NO AGREGA VALOR"),
    }
    return crit


# ------------------------------------------------------------
# Fidelidad del arnés: B2 contra los sellos reales, por fecha
# ------------------------------------------------------------
def fidelidad_b2(dfs: dict) -> dict:
    if CAMPEON not in dfs:
        return {}
    sel = predicciones_selladas()
    if sel.empty:
        return {}
    j = dfs[CAMPEON].merge(sel, left_on=["fecha_emision", "ticker"],
                           right_on=["fecha", "ticker"], how="inner")
    if j.empty:
        return {}
    j = j.assign(dif=(j["est"] - j["apertura_estimada_pct"]).abs())
    por_fecha = j.groupby("fecha_emision")["dif"].mean().sort_values(ascending=False)
    peor = por_fecha.index[0]
    sin_peor = j[j["fecha_emision"] != peor]
    return {
        "n_comparadas": int(len(j)),
        "dif_media_pp": round(float(j["dif"].mean()), 4),
        "dif_mediana_pp": round(float(j["dif"].median()), 4),
        "dif_p90_pp": round(float(j["dif"].quantile(0.90)), 4),
        "dif_max_pp": round(float(j["dif"].max()), 3),
        "peor_fecha": peor,
        "dif_media_peor_fecha_pp": round(float(por_fecha.iloc[0]), 4),
        "sin_la_peor_fecha": {
            "n": int(len(sin_peor)),
            "dif_media_pp": round(float(sin_peor["dif"].mean()), 4),
            "dif_max_pp": round(float(sin_peor["dif"].max()), 3)},
        "peores_fechas": {f: round(float(v), 4)
                          for f, v in por_fecha.head(6).items()},
    }


def medir_fuga_sentimiento() -> dict:
    """B-1 MEDIDA, no afirmada: cuántos juicios de IA no existían todavía a
    la hora de la emisión que los usa como feature.

    `backtest/datos.py` corta el sentimiento por `titulares.fecha` (la
    PUBLICACIÓN del titular) y nunca mira `analisis.analizado_en` (cuándo
    Claude emitió el juicio). Esta función abre `noticias.db` en `mode=ro`
    y cuenta la diferencia. Una afirmación de fuga sin su medición al lado
    es prosa; ésta trae el número y se recomputa en cada corrida.
    """
    import sqlite3

    from backtest.datos import RUTA_NOTICIAS
    if not os.path.exists(RUTA_NOTICIAS):
        return {"estado": "noticias.db no disponible"}
    c = sqlite3.connect(f"file:{RUTA_NOTICIAS}?mode=ro", uri=True)
    try:
        fila = c.execute("""
            SELECT COUNT(*),
                   SUM(CASE WHEN a.analizado_en >
                        (substr(t.fecha,1,10) || 'T22:15:00+00:00')
                       THEN 1 ELSE 0 END),
                   SUM(CASE WHEN substr(a.analizado_en,1,10) >
                        substr(t.fecha,1,10) THEN 1 ELSE 0 END),
                   MAX(julianday(substr(a.analizado_en,1,10))
                       - julianday(substr(t.fecha,1,10))),
                   MIN(a.analizado_en), MIN(substr(t.fecha,1,10))
            FROM analisis a JOIN titulares t ON t.id = a.titular_id""").fetchone()
    finally:
        c.close()
    total = fila[0] or 0
    if not total:
        return {"estado": "sin análisis en la base"}
    return {
        "total_analisis": int(total),
        "analizados_despues_de_la_emision_de_su_dia": int(fila[1] or 0),
        "pct_tarde": round(100 * (fila[1] or 0) / total, 1),
        "analizados_en_dia_calendario_posterior": int(fila[2] or 0),
        "rezago_maximo_dias": int(fila[3] or 0),
        "primer_juicio_de_ia_del_sistema": fila[4],
        "primer_titular": fila[5],
        "lectura": ("Toda emisión anterior a "
                    f"{str(fila[4])[:10]} alimenta B4/B5 con sentimiento "
                    "construido con juicios que NO existían ese día. El "
                    "`grado B` lo declara pero ninguna métrica lo excluye."),
    }


def impacto_b3(dfs: dict) -> dict:
    """Cuánto mueve B-3 (desenlaces duplicados) las cifras.

    NO es una segunda corrida ni una configuración nueva: es la MISMA
    corrida releída colapsando las filas que comparten
    (ticker, sesion_objetivo) — se conserva la emisión más TARDÍA, que es
    la que de verdad anticipa esa sesión. Mide fidelidad del arnés, no
    ventaja predictiva, así que no suma intentos al N (misma regla con la
    que la §1.5 del expediente dejó fuera al frente MICRO).
    """
    out = {}
    for b, df in dfs.items():
        if "sesion_objetivo" not in df.columns:
            continue
        dedup = (df.sort_values("fecha_emision")
                   .drop_duplicates(subset=["ticker", "sesion_objetivo"],
                                    keep="last"))
        ic_a, ic_d = metricas.rank_ic_diario(df), metricas.rank_ic_diario(dedup)
        s_a = _series_ls(df, 25) / 100.0
        s_d = _series_ls(dedup, 25) / 100.0
        out[b] = {
            "n_filas": int(len(df)), "n_filas_dedup": int(len(dedup)),
            "filas_duplicadas": int(len(df) - len(dedup)),
            "duelo_como_esta": _duelo(df),
            "duelo_deduplicado": _duelo(dedup),
            "ic_medio_como_esta": (round(float(ic_a.mean()), 4)
                                   if len(ic_a) else None),
            "ic_medio_dedup": (round(float(ic_d.mean()), 4)
                               if len(ic_d) else None),
            "t_nw_como_esta": (round(metricas.t_newey_west(ic_a), 2)
                               if len(ic_a) >= 10 else None),
            "t_nw_dedup": (round(metricas.t_newey_west(ic_d), 2)
                           if len(ic_d) >= 10 else None),
            "mae_como_esta": metricas.mae_gap(df),
            "mae_dedup": metricas.mae_gap(dedup),
            "sharpe_ls25_como_esta": (round(inferencia.sharpe(s_a.to_numpy()), 3)
                                      if len(s_a) >= 2 else None),
            "sharpe_ls25_dedup": (round(inferencia.sharpe(s_d.to_numpy()), 3)
                                  if len(s_d) >= 2 else None),
        }
    return out


def _md(salida: dict, reporte: dict) -> str:
    """El veredicto en prosa, generado ENTERO desde el JSON de esta corrida.

    Antes esta función llevaba cifras escritas a mano de la corrida del
    2026-09-01 06:17 —«−40.7 %», «−92.6 %», «520 días», «DSR N=82»—. Esa
    corrida quedó INVALIDADA por fuga: un número retirado que sigue ofrecido
    en el código vuelve a circular, y habría vuelto a circular dentro del
    reporte siguiente. Aquí no queda ninguno: todo lo que se afirma se lee
    del JSON o no se escribe."""
    c = salida["criterios"]
    par = salida["parametros_declarados"]
    gate = salida.get("gate_causalidad") or {}
    cob = salida.get("cobertura_sentimiento") or {}
    abiertos = salida.get("estado_gatillo", {}).get("defectos_abiertos") or []
    N = par["N_intentos"]
    banda = par["banda_N"]
    limpio = gate.get("resultado") == "INVARIANTE"

    L = ["# Veredicto de la Etapa 5.1 — B0→B5", ""]
    if limpio:
        L += ["## R3: LIMPIO. Y aun así esto NO es el veredicto de la 5.1.", "",
              "`GEMELO/DISEÑO.md` §6.2 **R3**: *«cualquier fuga detectada por "
              "el test de causalidad. Sin discusión y sin excepción.»* El "
              "test de causalidad existe ahora de verdad —invariancia al "
              "truncado de precios, OHLC **y noticias**, con contraprueba "
              "`shift(-1)` que lo hace fallar a propósito— y sobre "
              f"**{gate.get('n_comparaciones')} comparaciones "
              f"({gate.get('n_fechas')} fechas × "
              f"{len(gate.get('baselines', []))} baselines)** no detecta "
              "ninguna fuga. **R3 no dispara.**", "",
              "Lo que impide el veredicto ahora es otra cosa, y hay que "
              "decirlo con la misma firmeza: el **gatillo congelado del GATE "
              "B no está cumplido** (`backtest/DISEÑO.md` §11) y quedan "
              "**defectos abiertos del arnés que no son fugas temporales** "
              "pero sí contaminan la unidad de observación. El **holdout NO "
              "se gastó**."]
    else:
        L += ["## ⛔ NO HAY VEREDICTO. R3 lo impide, y R3 no admite "
              "excepciones.", "",
              "`GEMELO/DISEÑO.md` §6.2 **R3**: *«cualquier fuga detectada por "
              "el test de causalidad. Sin discusión y sin excepción.»* "
              "**El veredicto de la Etapa 5.1 espera** a que el arnés se "
              "arregle."]
    L += ["", "Expediente completo, con el conteo de intentos declarado antes "
          f"de correr: `{par['expediente']}`.", "",
          "## Tabla de criterios", "",
          "| Criterio | Veredicto | Razón |", "|---|---|---|"]
    razones = {
        "V1": "Habilidad sobre 'siempre al alza' en las MISMAS filas",
        "V2": "CRPS vs el campeón, IC de bootstrap circular",
        "V3": "Cobertura empírica del intervalo 80%",
        "V4": "MAE del gap vs el campeón en ventana",
        "V5": f"DSR ≥ 0.95 con N declarado = {N}",
        "V6": "Superar comprar SMH y no hacer nada, a 25 pb por lado",
        "V7": "Holdout en cuarentena — **deliberadamente NO gastado**",
        "R1": "Control lineal vs retador — no hay retador en esta corrida",
        "R2": "La ventaja sobrevive excluyendo 15–23 jul",
        "R3": ("**Gate de causalidad INVARIANTE — no dispara.**" if limpio
               else "**Fuga detectada. Sin discusión y sin excepción.**"),
        "veredicto_final_diseno_8": "El criterio de lectura del §8",
    }
    for k, v in c.items():
        L.append(f"| **{k}** | {v.get('veredicto')} | {razones.get(k, '')} |")

    # ---------- B-1: qué sobrevive al corte honesto ----------
    if cob:
        con = cob.get("accesos_con_sentimiento", 0)
        sin = cob.get("accesos_sin_sentimiento", 0)
        tot = con + sin
        pct = round(100 * con / tot, 2) if tot else 0.0
        L += ["", "## B-1 corregido — y lo que sobrevive al corte honesto", "",
              "El sentimiento ya no se corta por la fecha de PUBLICACIÓN del "
              "titular sino por `max(publicación, analizado_en)`: hacen falta "
              "**las dos** marcas para que el juicio exista. (El acta lo "
              "había escrito como `min()`; con el mínimo el predicado colapsa "
              "al roto, porque `analizado_en` es posterior a la publicación "
              "por construcción. La corrección va al ejecutable.)", "",
              f"- Pares (titular × ticker) en `noticias.db`: "
              f"**{cob.get('filas_ticker_analisis')}**, de los cuales "
              f"**{cob.get('pct_tarde')}%** quedaron disponibles DESPUÉS de "
              f"su publicación (rezago máximo "
              f"{cob.get('rezago_max_dias')} días).",
              f"- Primer dato de IA disponible en el sistema: "
              f"**{cob.get('primer_dia_con_dato_disponible')}**. Primer "
              f"titular publicado: {cob.get('primer_titular_publicado')}.",
              f"- Accesos a la feature de sentimiento con dato REAL: "
              f"**{con}** de {tot} (**{pct}%**). El resto se emitió con el "
              f"relleno neutro 0.0, declarado como **grado S**.", ""]
        b45 = {b: reporte["baselines"][b].get("grado_S_sin_noticias_pct")
               for b in ("B4", "B5") if b in reporte.get("baselines", {})}
        if b45 and all((v or 0) >= 50 for v in b45.values()):
            L += [f"### {' y '.join(b45)} NO son evaluables sobre esta ventana",
                  "", "Con el corte honesto, "
                  + " · ".join(f"**{b}: {v}% de sus filas sin ninguna "
                               f"noticia disponible**" for b, v in b45.items())
                  + ". Sus tres features de noticias valen la constante 0.0 en "
                  "esas filas, así que la capa colapsa a la anterior. Sus "
                  "cifras se leen como *«la capa de precios con columnas "
                  "constantes»*, **jamás** como *«las noticias no aportan»*: "
                  "esa pregunta no se puede contestar con dos años de datos "
                  "porque el sistema sólo tiene noticias analizadas desde "
                  f"{cob.get('primer_dia_con_dato_disponible')}.", "",
                  "**B0, B1, B2 y B3 no tocan el sentimiento y siguen "
                  "evaluables sobre la ventana completa.** Que dos baselines "
                  "de seis no sean evaluables no es que el backtest no lo "
                  "sea.", ""]

    # ---------- V6 ----------
    smh = c["V6"]["benchmark_smh"]
    L += ["", "## V6 — el benchmark obligatorio", "",
          f"**Comprar {smh['ticker']} y no hacer nada: "
          f"{smh['acumulado_pct']}% acumulado, Sharpe {smh['sharpe']}, "
          f"MDD {smh['mdd_pct']}%.**", "",
          "| B | LS 10 pb | LS 25 pb | LS 50 pb | LO 25 pb | Sharpe LS 25 pb |",
          "|---|---|---|---|---|---|"]
    for b, v in c["V6"]["detalle"].items():
        p = v["por_costo"]
        L.append(f"| {b} | {p[10]['long_short']['acum_pct']}% | "
                 f"**{p[25]['long_short']['acum_pct']}%** | "
                 f"{p[50]['long_short']['acum_pct']}% | "
                 f"{p[25]['long_only']['acum_pct']}% | "
                 f"{p[25]['long_short']['sharpe']} |")
    ganan = c["V6"]["quienes"]
    L += ["", (f"Superan al benchmark a 25 pb: **{', '.join(ganan)}**."
               if ganan else
               "**Ninguna cartera, en ningún nivel de costos, supera al "
               "benchmark.** El diseño ya lo había anticipado con *«una "
               "estrategia que sólo vive con 10 pb no aprueba»*."), ""]

    # ---------- V5 ----------
    cab = " | ".join(f"DSR N={n}" for n in banda)
    L += ["## V5 — Deflated Sharpe con el N declarado", "",
          f"| B | Sharpe LS 25 pb | días | skew | curtosis | PSR vs 0 | {cab} |",
          "|---|" + "---|" * (5 + len(banda))]
    dias_vistos, sharpes_vistos = [], []
    for b, v in c["V5"]["detalle"].items():
        if "dsr_por_N" not in v:
            L.append(f"| {b} | {v.get('sharpe_ls_25pb', '—')} | "
                     f"{v.get('dias', '—')} | — | — | "
                     f"{v.get('psr', v.get('estado', '—'))} |"
                     + " — |" * len(banda))
            continue
        d = v["dsr_por_N"]
        dias_vistos.append(v["dias"])
        sharpes_vistos.append(v["sharpe_ls_25pb"])
        L.append(f"| {b} | {v['sharpe_ls_25pb']} | {v['dias']} | {v['skew']} | "
                 f"{v['kurtosis']} | {v['psr_vs_cero']} | "
                 + " | ".join(str(d[n]["dsr"]) for n in banda) + " |")
    detalle_b2 = c["V5"]["detalle"].get(CAMPEON, {})
    if "dsr_por_N" in detalle_b2:
        L += ["", f"`V_intentos` = {c['V5']['V_intentos']} · umbral "
              f"deflactado `SR0` = {detalle_b2['dsr_por_N'][N]['sr0']} a "
              f"N={N}."]
    if dias_vistos:
        d_min = min(dias_vistos)
        L += ["", (f"Los {d_min} días de retornos superan el mínimo de "
                   f"{MINIMO_DIAS_SHARPE}: el DSR **es interpretable**."
                   if d_min >= MINIMO_DIAS_SHARPE else
                   f"Con {d_min} días de retornos —por debajo del mínimo de "
                   f"{MINIMO_DIAS_SHARPE}— el Sharpe anualizado es un "
                   f"artefacto y PSR/DSR se reportan **NO INTERPRETABLE**."),
              "", f"Sharpe long-short a 25 pb observado: de "
              f"{min(sharpes_vistos)} a {max(sharpes_vistos)}.",
              "", f"El conteo de intentos se declaró en **N = {N}** ANTES de "
              f"correr, con banda {banda}, y no se movió después de ver un "
              f"solo resultado.", ""]

    # ---------- V1 ----------
    L += ["## V1 — dirección del gap contra 'siempre al alza', mismas filas",
          "", "| B | n | acierto % | Wilson 95% | base % | ventaja pp | "
          "McNemar p |", "|---|---|---|---|---|---|---|"]
    for b, d in c["V1"]["detalle"].items():
        if not d:
            L.append(f"| {b} | — | — | — | — | — | — |")
            continue
        L.append(f"| {b} | {d['n']} | {d['modelo_pct']}% | "
                 f"{d['wilson95_pp']} | {d['base_pct']}% | "
                 f"{d['ventaja_pp']} | {d['mcnemar_p']} |")
    L.append("")

    # ---------- defectos abiertos ----------
    if abiertos:
        L += ["## Defectos ABIERTOS del arnés — no son fugas, y bloquean igual",
              ""]
        for d in abiertos:
            L.append(f"- {d}")
        L.append("")

    b3 = salida.get("impacto_b3_duplicados") or {}
    if b3:
        L += ["### B-3 medido sobre ESTA corrida", "",
              "Las MISMAS filas releídas colapsando los desenlaces "
              "duplicados por `(ticker, sesión objetivo)`:", "",
              "| B | filas | ventaja pp | IC medio | t(NW) | MAE |",
              "|---|---|---|---|---|---|"]
        for b, v in b3.items():
            dm, dd = v.get("duelo_como_esta"), v.get("duelo_deduplicado")
            L.append(f"| {b} | {v['n_filas']} → {v['n_filas_dedup']} | "
                     f"{dm['ventaja_pp'] if dm else '—'} → "
                     f"{dd['ventaja_pp'] if dd else '—'} | "
                     f"{v['ic_medio_como_esta']} → {v['ic_medio_dedup']} | "
                     f"{v['t_nw_como_esta']} → {v['t_nw_dedup']} | "
                     f"{v['mae_como_esta']} → {v['mae_dedup']} |")
        L += ["", "La unidad de observación sigue mal y hay que arreglarla; "
              "la lectura de la dirección del efecto se hace sobre estas "
              "cifras, no sobre las de ninguna corrida anterior.", ""]

    fid = salida.get("fidelidad_b2_vs_sellos") or {}
    if fid:
        L += ["## La fuente no es point-in-time, y está medido", "",
              f"`{CAMPEON}` contra las predicciones realmente selladas por "
              f"producción, {fid['n_comparadas']} filas: diferencia mediana "
              f"**{fid['dif_mediana_pp']} pp**, media "
              f"**{fid['dif_media_pp']} pp**, máxima "
              f"**{fid['dif_max_pp']} pp**. La peor fecha es "
              f"**{fid['peor_fecha']}** (media "
              f"{fid['dif_media_peor_fecha_pp']} pp); sin ella la media cae "
              f"a **{fid['sin_la_peor_fecha']['dif_media_pp']} pp** y el "
              f"máximo a {fid['sin_la_peor_fecha']['dif_max_pp']} pp.", "",
              "**Yahoo reescribe la historia en silencio**: la serie que se "
              "descarga hoy no es la que existía el día del sello. Es una "
              "limitación de primer orden del backtest entero, no una nota "
              "al pie.", ""]

    L += ["---", "", "## Qué queda por arreglar antes de que exista un "
          "veredicto", "",
          "En este orden, y el primer entregable de cada punto es el "
          "**test**, no el arreglo:", "",
          "1. ~~**B-1** — cortar el sentimiento por `analizado_en`.~~ "
          "**HECHO** (`max(publicación, analizado_en)`); `buzz` pasa por el "
          "mismo corte y tiene grado propio.",
          "2. ~~**B-2** — prueba maestra sobre B0–B5 × ≥10 fechas y "
          "contraprueba `shift(-1)` permanente.~~ **HECHO** "
          "(`backtest/causalidad.py` + 10 contrapruebas parametrizadas).",
          "3. **B-3** — deduplicar por `(ticker, sesión objetivo)` o declarar "
          "la sesión objetivo como unidad de observación. **ABIERTO.**",
          "4. **S-1** — contar sesiones del calendario, no días corridos, y "
          "sellar las efectivamente purgadas. **ABIERTO.**",
          "5. **S-3** — computar `estado_gatillo` en vez de recibirlo. "
          "**ABIERTO.**",
          "6. Construir un **holdout material**: hoy la cuarentena es sólo "
          "procedimental. **ABIERTO.**", "",
          "---", "Herramienta de análisis — no constituye asesoría "
          "financiera. Criterios congelados en `backtest/DISEÑO.md` §8 y "
          "`GEMELO/DISEÑO.md` §6; ninguno fue modificado para esta corrida.",
          ""]
    return "\n".join(L)



def main(ruta_existente: str | None = None) -> int:
    """Con `ruta_existente` re-evalúa los criterios sobre las predicciones ya
    escritas por una corrida, SIN volver a correr el walk-forward: las
    mismas filas, la misma semilla, el mismo resultado. Sirve cuando falla
    la capa de criterios y no la de datos — volver a bajar y recalcular
    cambiaría la fuente (Yahoo reescribe) y con ella los números."""
    if ruta_existente:
        with open(os.path.join(ruta_existente, "metricas.json"),
                  encoding="utf-8") as f:
            reporte = json.load(f)
        reporte["baselines"] = {b: {**v, "carteras": {int(k): c for k, c
                                                      in v["carteras"].items()}}
                                for b, v in reporte["baselines"].items()}
        reporte["ruta"] = ruta_existente
    else:
        fuente = FuenteCongelada()
        reporte = motorbt.correr(DESDE, HASTA, etiqueta=ETIQUETA, fuente=fuente,
                                 semilla_bootstrap=SEMILLA_BOOTSTRAP,
                                 alpha_bootstrap=ALPHA_BOOTSTRAP,
                                 estado_gatillo=ESTADO_GATILLO)
    ruta = reporte["ruta"]
    dfs = {}
    for b in ("B0", "B1", "B2", "B3", "B4", "B5"):
        p = os.path.join(ruta, f"predicciones_{b}.csv")
        if os.path.exists(p):
            dfs[b] = pd.read_csv(p)
    criterios = evaluar(reporte, dfs)
    fidelidad = fidelidad_b2(dfs)
    salida = {"parametros_declarados": {
                  "ventana": [DESDE.isoformat(), HASTA.isoformat()],
                  "semilla_bootstrap": SEMILLA_BOOTSTRAP,
                  "alpha_bootstrap": ALPHA_BOOTSTRAP,
                  "N_intentos": N_INTENTOS_51, "banda_N": list(BANDA_N),
                  "expediente": "GEMELO/resultados/gatillo_51.md"},
              "estado_gatillo": ESTADO_GATILLO,
              "fidelidad_b2_vs_sellos": fidelidad,
              "impacto_b3_duplicados": impacto_b3(dfs),
              "criterios": criterios}
    with open(os.path.join(ruta, "veredicto.json"), "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2, default=str)
    texto = _md(salida, reporte)
    with open(os.path.join(ruta, "veredicto.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    # El resumen.md es el artefacto VERSIONADO: el veredicto tiene que vivir
    # ahí, no sólo en un archivo al lado. Se reescribe entero desde el
    # reporte + el veredicto, nunca se acumulan copias al pie.
    resumen = motorbt._resumen_md(reporte)
    marca = "\n\n---\n\n"
    with open(os.path.join(ruta, "resumen.md"), "w", encoding="utf-8") as f:
        f.write(resumen + marca + texto)
    print(f"resultados en {ruta}")
    print(json.dumps({k: v.get("veredicto") for k, v in criterios.items()},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    import argparse
    _p = argparse.ArgumentParser(description="Veredicto 5.1 sobre B0→B5")
    _p.add_argument("--solo-criterios", default=None,
                    help="ruta de una corrida ya escrita: re-evalúa los "
                         "criterios sobre SUS filas, sin volver a correr el "
                         "walk-forward ni volver a descargar")
    raise SystemExit(main(_p.parse_args().solo_criterios))
