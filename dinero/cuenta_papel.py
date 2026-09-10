# ============================================================
# dinero/cuenta_papel.py — corre la cuenta en papel y escribe el reporte.
#
#   python -m dinero.cuenta_papel
#
# ORDEN: línea base primero (dos variantes), estrategia después. Los tres
# juegos de parámetros estaban DECLARADOS Y CONGELADOS en dinero/reglas.json
# antes de la primera corrida; acá se mide qué le cuesta a cada uno existir,
# y NO se elige uno mirando el resultado. El que rige por defecto lo fija
# una regla escrita: el conservador.
#
# La señal que alimenta la estrategia NO TIENE INFORMACIÓN, a propósito. Lo
# que este reporte mide es fricción, no habilidad.
#
# ------------------------------------------------------------
# HISTORIA: RETIRADA el 7-sep-2026, RECONSTRUIDA el 8-sep-2026
# ------------------------------------------------------------
# `GEMELO/resultados/dictamen_10/auditor_lookahead.md` demostró CUATRO
# mecanismos de fuga temporal en este módulo y en `contabilidad.py`,
# ejecutando código y no leyéndolo:
#
#   F1  el universo operable de una ventana de tres años se elegía con el
#       cierre del ÚLTIMO día de esa misma ventana; truncar al inicio lo
#       movía de 29 a 33 tickers y los excluidos eran los que más subieron.
#   F2  la señal "sin información" se sorteaba de la distribución de
#       retornos FUTUROS de la propia ventana simulada (755 de 756 señales
#       cambiaban al truncar).
#   F3  `apagado_por_perdida_pct` salía de una sigma calculada con futuro
#       (materialidad medida: nula, el interruptor nunca dispara).
#   F4  retardo de implementación CERO: se decidía y ejecutaba contra el
#       mismo cierre, mientras `senal_larga.py` usa 1 día.
#
# La página quedó RETIRADA y ninguna de sus cifras se pudo citar. El acta
# §82.4 firmó la reconstrucción (opción A) con el orden del auditor: el
# test de truncación primero (ya estaba, tests/test_dinero.py sección 6),
# después E1 membresía acotada por fecha, E3 sorteo desde datos anteriores
# a la ventana, E4 retardo en las dos patas, E5 sigma del interruptor sin
# futuro, E6 `ErrorLookAhead` cableado al riel, y recién después republicar.
#
# Lo que este módulo hace ahora distinto:
#   · `universo_operable(cierres, cfg, hasta=DESDE)` decide la membresía
#     con los cierres HASTA el inicio de la ventana (E1). La función recibe
#     la fecha como argumento explícito para que la dependencia se vea.
#   · la señal se sortea con `desde=DESDE` (E3, en contabilidad.py).
#   · `verificar_invariancia()` reconstruye la cuenta con la fuente
#     truncada y revienta con `backtest.datos.ErrorLookAhead` si un solo
#     movimiento cambia (E6). `main()` lo corre ANTES de escribir nada.
#   · el parámetro de costo es el del insumo del §40 (arancel publicado de
#     Interactive Brokers (IBKR), con acceso desde Chile, Pro Tiered, columna de acciones ENTERAS), leído de reglas.json,
#     y no un supuesto. Cuál columna se usó se declara en el reporte.
#
# Las cifras del reporte anterior (27 % / 57 % del capital en comisiones,
# etc.) NO se citan ni se comparan acá: están retiradas y compararlas
# sería darles uso.
# ============================================================
from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

from backtest import inferencia
from backtest.datos import ErrorLookAhead
from dinero import contabilidad as C
from dinero import precios
from dinero import universo_dinero as U

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "resultados")
SALIDA = os.path.join(DIR_RESULTADOS, "cuenta_papel.md")
SALIDA_JSON = os.path.join(DIR_RESULTADOS, "cuenta_papel.json")

# Congelados ANTES de correr, en este archivo y no como argumento suelto.
DESDE = "2023-09-05"
HASTA = "2026-09-04"
APORTE_SEMANAL_USD = 100.0
HORIZONTE_SENAL_HABILES = 20
ETFS_BASE = ("SMH", "XSD")
SEMILLA_COMPARACION = 20260906
# Cortes del gate de invariancia (E6). Regla, no lista a dedo (exigencia G2 del
# auditor, corrida 11): una sesión de cada PASO_CORTES dentro de la ventana,
# empezando PASO_CORTES sesiones después de DESDE. El auditor midió que una
# fuga de k días sólo deja huella en los k días previos a cada corte, así que
# el poder del gate contra fugas cortas crece con la densidad de cortes; con
# dos cortes a dedo una fuga de 1 día por `precios_ref` pasó (2 de 11 cortes
# la veían, 0 de los 2 declarados). Ver `verificar_invariancia.metodo`.
PASO_CORTES = 30


def cortes_invariancia(cierres: pd.DataFrame | None = None) -> tuple:
    completo = precios.cargar_congelado() if cierres is None else cierres
    idx = _ventana(completo).index
    return tuple(str(d.date()) for d in idx[PASO_CORTES::PASO_CORTES])


CORTES_INVARIANCIA = None   # se resuelve por regla en verificar_invariancia
JUEGOS = ("conservador", "medio", "agresivo")
# K semillas del sorteo de señal (exigencia C1 del adversario): la fricción y
# el conteo de ✓ son función del sorteo, así que sin K semillas son puntos
# disfrazados de hallazgos. K declarado acá, no elegido después.
K_SEMILLAS = 20


def _ventana(cierres):
    return cierres.loc[DESDE:HASTA]


def universo_operable(cierres: pd.DataFrame, cfg: dict | None = None,
                      hasta: str = DESDE) -> list:
    """Los instrumentos verificados y comprables con el techo, decididos
    con los cierres HASTA `hasta` — el inicio de la ventana, no su final.

    E1 de la reconstrucción. La versión de la corrida 10 pasaba el archivo
    entero a `construir_mapa`, que mira el último cierre: la membresía de
    tres años la decidía el último día, y los excluidos eran los que más
    habían subido. Recibir `hasta` como argumento hace visible de qué
    depende la lista, igual que `senal_larga.construir_paneles` recibe la
    membresía."""
    cfg = cfg or U.reglas()
    mapa = U.construir_mapa(cierres.loc[:hasta], cfg)
    return sorted(f.candidato.ticker for f in mapa
                  if f.verificado and f.alcanza_con_techo
                  and f.candidato.ticker in cierres.columns)


def correr(cierres_completo: pd.DataFrame | None = None,
           cfg: dict | None = None,
           senales_por_dia: dict | None = None,
           fuga_precios_ref_dias: int = 0):
    """La cuenta entera. `cierres_completo` es el archivo congelado (o una
    versión truncada de él: eso es lo que usa el gate). Todo lo que decide
    algo mira sólo datos anteriores o iguales al día en que decide."""
    cfg = cfg or U.reglas()
    costos = cfg["costos"]
    techo = cfg["presupuesto"]["techo_usd"]
    completo = precios.cargar_congelado() if cierres_completo is None else cierres_completo
    cierres = _ventana(completo)
    dias = [d.date() for d in cierres.index]
    aportes = C.calendario_aportes(dias, APORTE_SEMANAL_USD, techo)

    operables = universo_operable(completo, cfg, hasta=DESDE)
    if senales_por_dia is None:
        senales_por_dia = C.senales_sin_informacion(
            completo, operables, HORIZONTE_SENAL_HABILES,
            C.SEMILLA_SENAL_SIN_INFORMACION, desde=DESDE)

    resultados = {"aportes": aportes, "operables": operables,
                  "base": {}, "estrategia": {}}
    for pb in costos["barrido_deslizamiento_pb"]:
        for etf in ETFS_BASE:
            libro = C.linea_base(cierres, etf, aportes, costos, pb)
            valor = C.valorizar(cierres, libro.movimientos, aportes, costos)
            resultados["base"][(etf, pb)] = (libro, valor)
        for nombre in JUEGOS:
            libro = C.correr_estrategia(cierres, senales_por_dia, cfg, nombre,
                                        aportes, pb, techo,
                                        fuga_precios_ref_dias=fuga_precios_ref_dias)
            valor = C.valorizar(cierres, libro.movimientos, aportes, costos)
            resultados["estrategia"][(nombre, pb)] = (libro, valor)
    resultados["cierres"] = cierres
    return cfg, resultados


# ------------------------------------------------------------
# E6 — el gate de invariancia al truncado, cableado al riel
# ------------------------------------------------------------
def _huella_movimientos(res: dict, hasta: str) -> dict:
    """Todo movimiento ejecutado hasta `hasta`, de todos los libros, como
    tuplas comparables. Incluye la fecha de decisión y las acciones
    decididas: un cambio en cualquiera es fuga."""
    h = {}
    corte = pd.Timestamp(hasta).date()
    for clave, (libro, _) in list(res["base"].items()) + list(res["estrategia"].items()):
        h[str(clave)] = [
            (m.fecha.isoformat(), m.ticker, m.lado, m.acciones,
             round(m.precio_ejecucion, 8), round(m.comision_usd, 8),
             m.decidida_el.isoformat() if m.decidida_el else None,
             m.acciones_decididas)
            for m in libro.movimientos if m.fecha <= corte]
        # y las DECISIONES hasta el corte, ejecutadas o no: una decisión
        # tomada en D que cambia según exista D+1 es la fuga canónica, y
        # sólo se ve acá porque su ejecución cae fuera del corte
        h[str(clave) + " decisiones"] = [
            (dd.isoformat(), t, lado, n) for (dd, t, lado, n) in libro.decisiones
            if dd <= corte]
    h["operables"] = list(res["operables"])
    return h


def verificar_invariancia(cortes=CORTES_INVARIANCIA, cfg: dict | None = None,
                          cierres_completo: pd.DataFrame | None = None,
                          fabrica_senales=None,
                          fuga_precios_ref_dias: int = 0,
                          diagnostico: bool = False) -> dict:
    """Reconstruye la cuenta con la fuente ENTERA y con la fuente cortada
    en cada `corte`, y exige que todo movimiento ejecutado hasta ese corte
    sea idéntico. Si algo se mueve, revienta con `ErrorLookAhead`: R3 no
    admite excepciones, y menos una que el propio riel detectó.

    Es la única guarda con dientes (backtest/causalidad.py dice por qué):
    depende de los VALORES, no del índice. `fabrica_senales(cierres)` se
    puede inyectar para la contraprueba: se llama con la fuente completa y
    con cada fuente truncada, y una fábrica que mire un día adelante tiene
    que hacer disparar esto. `fuga_precios_ref_dias` inyecta la OTRA fuga
    (por el precio con que se dimensiona, G3) por el mismo canal.

    `diagnostico=False` (por defecto) revienta en el PRIMER corte roto, que
    es lo que el riel necesita antes de escribir. `diagnostico=True`
    (hallazgo 5 de la revisión de la corrida 11) recorre TODOS los cortes y
    devuelve el mapa completo de los rotos en `cortes_rotos`, sin levantar:
    sirve para medir qué cortes ven una fuga y cuáles no, que es la pregunta
    del auditor sobre la densidad del barrido. No cambia el `raise` por
    defecto ni el resultado cuando no hay fuga."""
    completo = precios.cargar_congelado() if cierres_completo is None else cierres_completo
    cfg = cfg or U.reglas()
    cortes = cortes_invariancia(completo) if cortes is None else tuple(cortes)
    # Vacuidad (hallazgo H1 del auditor sobre el sellador, generalizado acá por el
    # director de programa, corrida 12): un corte en o después del último día de la
    # fuente compara la cuenta consigo misma y no vigila nada. Se rechaza en vez
    # de contarse como INVARIANTE.
    ultimo = completo.index.max()
    vacuos = [c for c in cortes if pd.Timestamp(c) >= ultimo]
    if vacuos or not cortes:
        raise ErrorLookAhead(
            f"gate VACUO: corte(s) {vacuos or '(ninguno)'} en o después del último día de la fuente "
            f"({ultimo.date()}): comparar la cuenta consigo misma no vigila nada")
    _, res_full = correr(completo, cfg, fabrica_senales(completo) if fabrica_senales else None,
                         fuga_precios_ref_dias=fuga_precios_ref_dias)
    comparaciones, rotos = [], []
    for corte in cortes:
        recortado = completo.loc[:corte]
        _, res_cut = correr(recortado, cfg, fabrica_senales(recortado) if fabrica_senales else None,
                            fuga_precios_ref_dias=fuga_precios_ref_dias)
        a, b = _huella_movimientos(res_full, corte), _huella_movimientos(res_cut, corte)
        for clave in a:
            if a[clave] != b.get(clave):
                bc = b.get(clave, [])
                i = next((k for k, (x, y) in enumerate(zip(a[clave], bc)) if x != y), None)
                if i is None:
                    i = min(len(a[clave]), len(bc))
                con = a[clave][i] if i < len(a[clave]) else "(ninguna)"
                sin = bc[i] if i < len(bc) else "(ninguna)"
                detalle = (
                    f"invariancia al truncado ROTA en {corte} · {clave}: la cuenta "
                    f"cambia según existan o no los datos posteriores al corte. "
                    f"{len(a[clave])} con futuro contra {len(bc)} sin futuro; primera "
                    f"diferencia en la posición {i}. Con futuro: {con} · sin futuro: {sin}")
                if not diagnostico:
                    raise ErrorLookAhead(detalle)
                rotos.append({"corte": corte, "clave": clave, "detalle": detalle})
                break   # un corte roto se cuenta una vez; el detalle es el primero
        comparaciones.append({"corte": corte,
                              "libros": sum(1 for k in a if k != "operables" and not k.endswith(" decisiones")),
                              "movimientos_comparados": sum(len(v) for k, v in a.items()
                                                            if k != "operables" and not k.endswith(" decisiones")),
                              "decisiones_comparadas": sum(len(v) for k, v in a.items()
                                                           if k.endswith(" decisiones"))})
    return {"ejecutado": True,
            "resultado": "ROTA" if rotos else "INVARIANTE",
            "cortes": list(cortes),
            "cortes_rotos": rotos,
            "fuga_inyectada": {"precios_ref_dias": fuga_precios_ref_dias,
                               "fabrica_senales": fabrica_senales is not None},
            "comparaciones": comparaciones,
            "metodo": ("se reconstruye la cuenta entera (membresía, señales, línea base, "
                       "tres juegos, cuatro deslizamientos) con la fuente cortada en D y se "
                       "exige que todo movimiento ejecutado hasta D (fecha, ticker, lado, "
                       "acciones, precio, comisión, fecha de decisión y acciones decididas) y "
                       "toda DECISIÓN tomada hasta D, ejecutada o no, sea idéntica a la de la "
                       "fuente completa"),
            "alcance": (f"invariancia al truncado en {len(cortes)} cortes por regla (una sesión de cada "
                        f"{PASO_CORTES}). Una fuga de k días sólo deja huella en los k días previos a "
                        "cada corte: el poder contra fugas cortas es la probabilidad de que en esos "
                        "días haya una decisión distinta. Medido por el auditor (corrida 11): una fuga "
                        "de 1 día por precios_ref la veían 2 de 11 cortes. INVARIANTE no significa "
                        "ausencia de fuga: significa que ninguna entró por las vías que estos cortes "
                        "ven. La contraprueba de precios_ref (G3, corrida 12) existe como prueba de "
                        "borde: el corte se pone en el primer día en que la fuga cambia una "
                        "decisión, leído de Libro.decisiones, y ahí el gate dispara."),
            "cubre_solo_la_semilla_0": True,
            "contraprueba": ("tests/test_dinero.py inyecta una señal que mira un día "
                             "adelante (por fabrica_senales) y un precio de dimensionamiento "
                             "que mira un día adelante (por fuga_precios_ref_dias, G3), y "
                             "exige que este gate dispare en los dos casos")}


# ------------------------------------------------------------
# Resúmenes
# ------------------------------------------------------------
def _resumen(libro, valor, aportado):
    final = float(valor.iloc[-1]) if len(valor) else 0.0
    movs = libro.movimientos
    reducidas = sum(1 for m in movs if m.acciones_decididas is not None
                    and m.acciones < m.acciones_decididas)
    return {
        "final_usd": final,
        "aportado_usd": aportado,
        "resultado_usd": final - aportado,
        "resultado_pct": (100.0 * (final / aportado - 1.0)) if aportado else float("nan"),
        "ordenes": len(movs),
        "ordenes_reducidas_al_ejecutar": reducidas,
        "comisiones_usd": libro.comisiones_usd,
        "deslizamiento_usd": libro.deslizamiento_usd,
        "comisiones_pct_del_aportado": (100.0 * libro.comisiones_usd / aportado) if aportado else float("nan"),
    }


def sigma_diferencia_semanal(res: dict, cfg: dict, juego: str | None = None,
                             etf: str = "SMH", pb: float | None = None) -> dict:
    """La σ de la diferencia semanal juego − base, CON intervalo (bootstrap
    circular de bloques de semanas). Es el parámetro que la tabla de potencia
    del pre-registro necesitaba y que hasta hoy viajaba retirado y sin
    intervalo. Juego y deslizamiento por defecto: los de reglas.json."""
    juego = juego or cfg["juego_activo"]
    pb = cfg["costos"]["deslizamiento_pb_por_lado"] if pb is None else pb
    _, ve = res["estrategia"][(juego, pb)]
    _, vb = res["base"][(etf, pb)]
    re_, rb = C.retornos_semanales(ve), C.retornos_semanales(vb)
    comun = re_.index.intersection(rb.index)
    dif = (re_.loc[comun] - rb.loc[comun]).dropna().to_numpy()
    n = len(dif)
    sd = float(np.std(dif, ddof=1)) if n > 1 else float("nan")
    idx = inferencia._remuestrear_circular(np.arange(n), SEMILLA_COMPARACION + 7,
                                           C.REPLICAS_BOOTSTRAP, C.BLOQUE_BOOTSTRAP_SEMANAS)
    sds = np.array([np.std(dif[i], ddof=1) for i in idx])
    return {"juego": juego, "base": etf, "deslizamiento_pb": pb, "semanas": int(n),
            "sigma_pp_semana": round(sd, 4),
            "ic95": [round(float(np.quantile(sds, 0.025)), 4), round(float(np.quantile(sds, 0.975)), 4)],
            "metodo": (f"sd (ddof=1) de la diferencia semanal, IC por bootstrap circular de bloques de "
                       f"{C.BLOQUE_BOOTSTRAP_SEMANAS} semanas, {C.REPLICAS_BOOTSTRAP} réplicas, "
                       f"semilla {SEMILLA_COMPARACION + 7}")}


def barrido_semillas(cfg: dict | None = None, K: int = K_SEMILLAS,
                     cierres_completo: pd.DataFrame | None = None) -> dict:
    """K sorteos de la señal sin información, y sobre ellos la fricción por
    juego y la fracción de comparaciones cuyo IC excluye el cero, CON
    intervalo (percentiles entre semillas para la fricción; para la fracción,
    la unidad de replicación es la SEMILLA, no la comparación: las 24
    comparaciones de una semilla comparten sorteo, calendario, instrumentos
    y semilla de bootstrap, así que el Wilson sobre K×24 que viajaba hasta el
    re-dictamen de la corrida 12 era un intervalo iid sobre unidades
    agrupadas y se RETIRÓ (exigencia D7). Queda el conteo desnudo y un
    intervalo t sobre las K fracciones por semilla). Semilla i =
    SEMILLA_SENAL_SIN_INFORMACION + i; la semilla 0 es la de la página."""
    cfg = cfg or U.reglas()
    completo = precios.cargar_congelado() if cierres_completo is None else cierres_completo
    operables = universo_operable(completo, cfg, hasta=DESDE)
    pbs = cfg["costos"]["barrido_deslizamiento_pb"]
    pb0 = cfg["costos"]["deslizamiento_pb_por_lado"]
    fr = {j: [] for j in JUEGOS}
    ordenes = {j: [] for j in JUEGOS}
    marcados = total = 0
    negativos_vs_smh = {j: 0 for j in JUEGOS}
    fraccion_por_semilla = []
    for i in range(K):
        marcados_semilla = total_semilla = 0
        sen = C.senales_sin_informacion(completo, operables, HORIZONTE_SENAL_HABILES,
                                        C.SEMILLA_SENAL_SIN_INFORMACION + i, desde=DESDE)
        _, res = correr(completo, cfg, sen)
        aportado = sum(res["aportes"].values())
        for j in JUEGOS:
            libro, valor = res["estrategia"][(j, pb0)]
            fr[j].append(100.0 * libro.comisiones_usd / aportado)
            ordenes[j].append(len(libro.movimientos))
            for pb in pbs:
                _, v = res["estrategia"][(j, pb)]
                for etf in ETFS_BASE:
                    _, vb = res["base"][(etf, pb)]
                    comp = C.comparar(v, vb, semilla=SEMILLA_COMPARACION)
                    total += 1
                    total_semilla += 1
                    if not comp["cruza_cero"]:
                        marcados += 1
                        marcados_semilla += 1
                        if etf == "SMH" and comp["dif_media_pp"] < 0:
                            negativos_vs_smh[j] += 1
        fraccion_por_semilla.append(marcados_semilla / total_semilla)
    fps = np.asarray(fraccion_por_semilla)
    # t sobre las K semillas (clúster = semilla). Con K = 20, t(19) al 97,5 % = 2,093.
    from math import sqrt
    t975 = 2.093 if K == 20 else 1.96
    media_f = float(fps.mean())
    ee = float(fps.std(ddof=1) / sqrt(K)) if K > 1 else float("nan")
    q = lambda v: [round(float(np.quantile(v, 0.025)), 2), round(float(np.quantile(v, 0.975)), 2)]
    return {
        "K": K, "semillas": [C.SEMILLA_SENAL_SIN_INFORMACION + i for i in range(K)],
        "deslizamiento_pb": pb0,
        "comisiones_pct_del_aportado": {
            j: {"mediana": round(float(np.median(fr[j])), 2), "banda_p2_5_p97_5": q(fr[j]),
                "min": round(min(fr[j]), 2), "max": round(max(fr[j]), 2),
                "ordenes_mediana": int(np.median(ordenes[j])), "ordenes_banda": q(ordenes[j])}
            for j in JUEGOS},
        "ic_excluye_cero": {"marcados": marcados, "comparaciones": total,
                            "fraccion": round(marcados / total, 4),
                            "unidad_de_replicacion": "semilla",
                            "fraccion_por_semilla": [round(float(x), 4) for x in fps],
                            "ic95_t_entre_semillas": [round(media_f - t975 * ee, 4), round(media_f + t975 * ee, 4)],
                            "wilson95_retirado": ("el Wilson sobre K×24 comparaciones se retiró en el re-dictamen "
                                                  "de la corrida 12 (D7): era iid sobre unidades agrupadas"),
                            "de_los_cuales_agresivo_negativo_vs_SMH": negativos_vs_smh["agresivo"]},
        "banda_es": ("percentiles 2,5 y 97,5 ENTRE SORTEOS de la señal (con K = 20 son casi el mínimo y el "
                     "máximo), no un intervalo de cobertura nominal"),
        "nota": ("La fracción de IC que excluyen el cero NO es una tasa de falsos positivos "
                 "(la nula no es cero: hay arrastre de comisión). Es cuánto produce este diseño "
                 "con una señal sin información, con la misma semilla de bootstrap en las K×24."),
    }


# ------------------------------------------------------------
# El reporte
# ------------------------------------------------------------
def _cobertura_simulador(T: int = 156):
    """La cobertura medida del IC del instrumento al horizonte T (exigencia
    C3), leída del artefacto del bloque 1 si existe."""
    ruta = os.path.join(RAIZ, "GEMELO", "resultados", "instrumento_dinero.json")
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        d = json.load(f)
    k = (d.get("calibracion") or {}).get(str(T))
    return k


def sesgo_de_la_sonda(res: dict, cfg: dict) -> dict:
    """La sonda no es neutral aunque no tenga información direccional
    (exigencia G5 del auditor): hereda la deriva del período anterior a
    DESDE. Se mide y se declara."""
    completo = precios.cargar_congelado()
    operables = res["operables"]
    sen = C.senales_sin_informacion(completo, operables, HORIZONTE_SENAL_HABILES,
                                    C.SEMILLA_SENAL_SIN_INFORMACION, desde=DESDE)
    m = np.array([s.magnitud_pp for lote in sen.values() for s in lote])
    return {"n_senales": int(len(m)), "fraccion_positivas": round(float((m > 0).mean()), 4),
            "magnitud_media_pp": round(float(m.mean()), 3),
            "lectura": "sonda larga por construcción: sin información sobre la dirección no es lo mismo que sin sesgo"}


def membresia_como_corte(res: dict, cfg: dict) -> dict:
    """La membresía E1 es un corte transversal fijo al DESDE, ni futuro ni
    point-in-time (exigencia G6): se declara con su dirección medida."""
    completo = precios.cargar_congelado()
    ventana = _ventana(completo)
    todos = [c.ticker for c in U.CANDIDATOS if c.ticker in completo.columns]
    incluidos = list(res["operables"])
    excluidos = [t for t in todos if t not in incluidos]
    def ret(ts):
        out = []
        for t in ts:
            s = ventana[t].dropna()
            if len(s) > 1:
                out.append(100.0 * (s.iloc[-1] / s.iloc[0] - 1.0))
        return round(float(np.median(out)), 1) if out else None
    razon = {}
    for t in excluidos:
        s = completo[t].dropna()
        if s.empty or s.index[0] > pd.Timestamp(DESDE):
            razon[t] = f"sin cierre anterior a {DESDE} (listada después)"
        else:
            razon[t] = f"precio al {DESDE} por encima del techo"
    return {"incluidos": len(incluidos), "excluidos": excluidos, "razon_exclusion": razon,
            "retorno_mediano_ventana_incluidos_pct": ret(incluidos),
            "retorno_mediano_ventana_excluidos_pct": ret(excluidos)}


def componer(cfg, res, gate: dict | None = None, semillas: dict | None = None) -> str:
    cierres = res["cierres"]
    aportado = sum(res["aportes"].values())
    pbs = cfg["costos"]["barrido_deslizamiento_pb"]
    c = cfg["costos"]
    L = []
    L.append("# Cuenta en papel del riel de dinero — **SIMULADO** (v2, reconstruida sin fuga)\n")
    L.append("> **SIMULADO. PROPUESTA hasta el dictamen del `estadistico-adversario` y del")
    L.append("> `auditor-lookahead`.** Ninguna cifra de este documento es un resultado del")
    L.append("> proyecto, ninguna entra al README. No hay cuenta de corredora y no se envió")
    L.append("> ninguna orden a ningún lado. Cero filas selladas de este riel.")
    L.append(">")
    L.append("> **Lo que esta cuenta mide es FRICCIÓN, no habilidad.** La estrategia se")
    L.append("> alimenta de una señal SIN INFORMACIÓN, sorteada de la distribución de")
    L.append(f"> retornos a {HORIZONTE_SENAL_HABILES} días hábiles de cada instrumento medida")
    L.append(f"> con datos **anteriores a {DESDE}** (semilla {C.SEMILLA_SENAL_SIN_INFORMACION}),")
    L.append("> justamente para que lo que se lea acá sea lo que le cuesta a cada juego de")
    L.append("> parámetros existir. Una estrategia con señal de verdad tendría que superar")
    L.append("> esto ANTES de poder llamarse habilidad.")
    L.append(">")
    L.append("> **Versión 2, reconstruida el 8-sep-2026 (corrida 11, acta §82.4).** La v1")
    L.append("> del 7-sep está RETIRADA por cuatro fugas temporales demostradas (F1 a F4,")
    L.append("> `GEMELO/resultados/dictamen_10/auditor_lookahead.md`). Ninguna cifra de la v1")
    L.append("> se cita ni se compara acá. Las correcciones, en el orden que fijó el auditor:")
    L.append(f"> E1 membresía decidida con los cierres hasta {DESDE}; E3 señal sorteada de")
    L.append(f"> datos anteriores a {DESDE}; E4 retardo de implementación de")
    L.append(f"> {C.RETARDO_IMPLEMENTACION} sesión en las DOS patas; E5 sigma del interruptor")
    L.append(f"> medida hasta {DESDE}; E6 gate de invariancia al truncado cableado y corrido")
    L.append("> antes de escribir esta página.")
    if gate:
        L.append(f"> **Gate de invariancia:** {gate['resultado']} en {len(gate['cortes'])} cortes por regla "
                 f"(una sesión de cada {PASO_CORTES}; {sum(x['movimientos_comparados'] for x in gate['comparaciones'])} "
                 f"movimientos y {sum(x.get('decisiones_comparadas', 0) for x in gate['comparaciones'])} decisiones "
                 f"comparadas). **Alcance:** {gate.get('alcance', '')}\n")
    else:
        L.append("> **Gate de invariancia: NO corrido en esta composición.**\n")
    L.append("Generado por `python -m dinero.cuenta_papel` el "
             f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')} UTC.\n")

    L.append("## Parámetros congelados antes de correr\n")
    L.append(f"- Ventana: **{DESDE} a {HASTA}** ({len(cierres)} días de mercado), "
             f"sobre `dinero/datos/cierres_congelados.csv`. **Sin descargas.**")
    L.append(f"- Aporte: **{APORTE_SEMANAL_USD:.0f} USD el primer día hábil de cada "
             f"semana, hasta agotar el techo de {cfg['presupuesto']['techo_usd']:.0f} "
             f"USD**. Total aportado: **{aportado:.0f} USD** en "
             f"{len(res['aportes'])} aportes. Es el flujo IMPLEMENTADO (errata §6 C del")
    L.append("  pre-registro: rige lo implementado). La línea base y la estrategia reciben")
    L.append("  **el mismo flujo de caja**, que es lo que las hace comparables.")
    L.append(f"- Universo operable: **{len(res['operables'])} instrumentos**, los verificados y")
    L.append(f"  comprables con {cfg['presupuesto']['techo_usd']:.0f} USD **al {DESDE}** (E1): "
             + ", ".join(f"`{t}`" for t in res["operables"]) + ".")
    L.append(f"- **Parámetro de costo: el arancel publicado del insumo del §40** "
             f"(`GEMELO/propuestas/insumo_40_aranceles_*.md`, arancel Pro Tiered del corredor del §40, consultado el")
    L.append(f"  7-sep-2026), **columna de acciones ENTERAS**: {c['comision_por_accion_usd']} USD por")
    L.append(f"  acción, mínimo {c['comision_minima_usd']:.2f} USD por orden, tope "
             f"{c['comision_tope_pct_del_monto']} % del monto. La columna de fraccionarias")
    L.append("  (1 % del monto, mínimo 0,01) NO aplica: esta cuenta compra acciones enteras.")
    L.append("  Las tarifas de terceros (SEC, FINRA, compensación) no están en el modelo:")
    L.append("  a estos tamaños suman centavos y el insumo lo declara.")
    L.append(f"- Barrido de deslizamiento: {pbs} pb por lado, **además** de la comisión.")
    L.append(f"- Retardo de implementación: **{C.RETARDO_IMPLEMENTACION} sesión** en las dos patas. "
             "Se decide con el cierre de d y se ejecuta contra el cierre de d+1; si a ese")
    L.append("  precio la caja no alcanza, la orden se reduce y queda contada en la columna")
    L.append("  «reducidas». Con retardo 1 no hay caja comprometida al decidir (lo pendiente se")
    L.append("  ejecuta antes de decidir el mismo día): el descuento existe en el código sólo para")
    L.append("  retardo > 1, y las dos patas usan la misma convención (n × precio de decisión).")
    sb = sesgo_de_la_sonda(res, cfg)
    L.append(f"- **La sonda es larga por construcción** (exigencia G5 del auditor): {sb['fraccion_positivas']*100:.1f} % de "
             f"las {sb['n_senales']} señales son positivas y la magnitud media es {sb['magnitud_media_pp']:+.2f} pp, porque")
    L.append(f"  hereda la deriva anterior a {DESDE}. Sin información sobre la dirección no es lo mismo que sin")
    L.append("  sesgo: lo medido es la fricción de un comprador aleatorio sesgado a largo en un mercado que subió.")
    mc = membresia_como_corte(res, cfg)
    L.append(f"- **La membresía es un corte transversal fijo al {DESDE}**, ni futuro ni point-in-time (exigencia G6): "
             f"excluye {', '.join('`%s` (%s)' % (t, mc['razon_exclusion'][t]) for t in mc['excluidos'])}. Los excluidos")
    L.append(f"  rindieron en la ventana una mediana de {mc['retorno_mediano_ventana_excluidos_pct']:+.1f} % contra "
             f"{mc['retorno_mediano_ventana_incluidos_pct']:+.1f} % de los incluidos: el sesgo va EN CONTRA de la cuenta.")
    L.append("  Un inversor real podía comprar las listadas después desde su listado; acá quedan vetadas tres años.")
    L.append("- Existe un segundo congelado (`dinero/datos/cierres_congelados_dia2.csv`, 8-sep 04:21 UTC, mismo rango):")
    L.append("  la cuenta recorrida contra él es bit a bit idéntica (diferencia relativa máxima 8,4e-7 en los")
    L.append("  precios). Es evidencia contra revisión silenciosa de la fuente en 26 horas, no en años.\n")

    L.append("## 4a. La línea base aburrida\n")
    L.append("Comprar un ETF del sector con el aporte semanal, sin decidir nada. Si el")
    L.append("aporte no alcanza para una acción entera, **acumula**.\n")
    L.append("| ETF | Deslizamiento | Órdenes | Comisiones USD | Final USD | Resultado USD | Resultado % |")
    L.append("|---|---:|---:|---:|---:|---:|---:|")
    for etf in ETFS_BASE:
        for pb in pbs:
            libro, valor = res["base"][(etf, pb)]
            r = _resumen(libro, valor, aportado)
            L.append(f"| `{etf}` | {pb:.0f} pb | {r['ordenes']} | "
                     f"{r['comisiones_usd']:.2f} | {r['final_usd']:.2f} | "
                     f"{r['resultado_usd']:+.2f} | {r['resultado_pct']:+.2f} % |")
    L.append("")
    L.append("`SMH` es el BENCHMARK declarado del riel de medición y por eso está; `XSD` es")
    L.append("el ETF sectorial cuya acción cabe en el presupuesto. La diferencia entre las")
    L.append("dos filas **no es una diferencia de mercado: es el costo de no poder comprar")
    L.append("fracciones**.\n")

    L.append("## 4b/4c. Los tres juegos, contra la línea base\n")
    L.append("Los tres estaban declarados y congelados en `dinero/reglas.json` antes de la")
    L.append("primera corrida, con su regla de derivación. Se muestran **los tres, sin ranking")
    L.append("y sin recomendación**. El que rige por defecto lo fija una regla escrita —el")
    L.append("conservador—, no su resultado.\n")
    for pb in pbs:
        L.append(f"### Deslizamiento {pb:.0f} pb por lado\n")
        L.append("| Juego | Órdenes | Reducidas | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |")
        L.append("|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|")
        for nombre in JUEGOS:
            libro, valor = res["estrategia"][(nombre, pb)]
            r = _resumen(libro, valor, aportado)
            celdas = []
            for etf in ETFS_BASE:
                _, vb = res["base"][(etf, pb)]
                comp = C.comparar(valor, vb, semilla=SEMILLA_COMPARACION)
                marca = "" if comp["cruza_cero"] else " ✓"
                celdas.append(f"{comp['dif_media_pp']:+.3f}")
                celdas.append(f"[{comp['ic_lo']:+.3f}, {comp['ic_hi']:+.3f}]{marca}")
            L.append(f"| {nombre} | {r['ordenes']} | {r['ordenes_reducidas_al_ejecutar']} | "
                     f"{r['comisiones_usd']:.2f} | {r['deslizamiento_usd']:.2f} | {r['final_usd']:.2f} | "
                     f"{r['resultado_pct']:+.2f} % | " + " | ".join(celdas) + " |")
        L.append("")
    L.append("Los intervalos son **bootstrap circular de bloques sobre SEMANAS** "
             f"(bloque de {C.BLOQUE_BOOTSTRAP_SEMANAS} semanas, "
             f"{C.REPLICAS_BOOTSTRAP} réplicas, semilla {SEMILLA_COMPARACION}, "
             "α = 0.05), con `backtest.inferencia.bootstrap_media`. Este instrumento fue")
    L.append("**puesto a prueba contra una verdad conocida** en el bloque 1 de la corrida 11")
    L.append("(`GEMELO/resultados/instrumento_dinero.md`): **discrimina** por el criterio pre-declarado y")
    L.append("**NO está calibrado a α = 0,05 en ninguno de los tres horizontes** (sub-cubre bajo la nula).")
    cs = _cobertura_simulador(156)
    if cs:
        L.append(f"Al horizonte de ESTAS comparaciones (156 semanas) la cobertura medida es "
                 f"{cs['cobertura']['tasa']:.3f} {cs['cobertura']['wilson95']} y el tamaño bilateral "
                 f"{cs['tamano_bilateral']['tasa']:.3f} {cs['tamano_bilateral']['wilson95']}: el α real de un "
                 f"`✓` es ≈ {cs['alpha_real']:.3f}, no 0,05.")
    else:
        L.append("La cobertura al horizonte de estas comparaciones (156 semanas) no está en el artefacto del bloque 1.")
    L.append("Un `✓` marca un intervalo que **no** contiene el cero; sin `✓`, la diferencia **no se")
    L.append("distingue de cero**.\n")

    # --- hallazgos ---
    L.append("## Qué de esto es un hallazgo y qué no\n")
    L.append("### 1. Cuánto cuesta rotar, con el arancel publicado\n")
    L.append(f"| Juego | Órdenes (rango del barrido) | Comisiones USD | Como fracción de los {aportado:.0f} USD aportados |")
    L.append("|---|---:|---:|---:|")
    for nombre in JUEGOS:
        ords = [len(res["estrategia"][(nombre, pb)][0].movimientos) for pb in pbs]
        coms = [res["estrategia"][(nombre, pb)][0].comisiones_usd for pb in pbs]
        L.append(f"| {nombre} | {min(ords)}–{max(ords)} | {min(coms):.2f}–{max(coms):.2f} | "
                 f"**{100*min(coms)/aportado:.1f} % – {100*max(coms)/aportado:.1f} %** |")
    for etf in ETFS_BASE:
        coms = [res["base"][(etf, pb)][0].comisiones_usd for pb in pbs]
        ords = [len(res["base"][(etf, pb)][0].movimientos) for pb in pbs]
        L.append(f"| línea base `{etf}` | {min(ords)}–{max(ords)} | {min(coms):.2f}–{max(coms):.2f} | "
                 f"{100*min(coms)/aportado:.1f} % – {100*max(coms)/aportado:.1f} % |")
    L.append("")
    L.append("**Esos rangos son el mínimo y el máximo sobre los cuatro niveles de deslizamiento")
    L.append("de UN solo sorteo de señal: no son intervalos y no se pueden leer como tales.**")
    L.append("Lo que sí se sostiene es la aritmética: con el arancel del §40 cada orden de acciones")
    L.append(f"enteras cuesta como máximo {c['comision_minima_usd']:.2f} USD, así que la fracción del capital que")
    L.append("se va en comisiones es, como COTA SUPERIOR, el número de órdenes por 0,35 sobre lo aportado;")
    L.append("el tope del 1 % del monto muerde en las órdenes de menos de 35 USD y deja la cifra real")
    L.append("por debajo de esa cota (exigencia C2: 205 × 0,35 / 500 = 14,4 % contra 12,4 % medido).")
    L.append("**La fricción la fija el número de órdenes del diseño, no el arancel**; la nota del §82.4")
    L.append("se lee después de esta tabla, no antes.\n")
    if semillas:
        sm = semillas
        L.append(f"### 1b. Con {sm['K']} semillas del sorteo, y con intervalo (exigencia C1)\n")
        L.append(f"Deslizamiento {sm['deslizamiento_pb']:.0f} pb. Banda = percentiles 2,5 y 97,5 entre semillas.\n")
        L.append("| Juego | Comisiones % del aportado, mediana | banda entre semillas | mín–máx | Órdenes, mediana | banda |")
        L.append("|---|---:|---|---|---:|---|")
        for j in JUEGOS:
            x = sm["comisiones_pct_del_aportado"][j]
            L.append(f"| {j} | **{x['mediana']:.1f} %** | {x['banda_p2_5_p97_5']} | {x['min']:.1f}–{x['max']:.1f} | "
                     f"{x['ordenes_mediana']} | {x['ordenes_banda']} |")
        ie = sm["ic_excluye_cero"]
        L.append("")
        L.append(f"Comparaciones cuyo IC excluye el cero: **{ie['marcados']} de {ie['comparaciones']}** "
                 f"({ie['fraccion']:.3f}; IC95 t con la SEMILLA como unidad de replicación "
                 f"{ie['ic95_t_entre_semillas']}, el Wilson iid sobre K×24 se retiró en el re-dictamen D7) "
                 f"sobre {sm['K']} semillas × 24; de ellas, "
                 f"{ie['de_los_cuales_agresivo_negativo_vs_SMH']} son `agresivo` perdiendo contra `SMH`. {sm['nota']}\n")

    L.append("### 2. El barrido de deslizamiento NO es una curva de sensibilidad al costo.\n")
    for nombre in JUEGOS:
        rs = [(pb, _resumen(*res["estrategia"][(nombre, pb)], aportado)) for pb in pbs]
        peor, mejor = min(rs, key=lambda x: x[1]["resultado_pct"]), max(rs, key=lambda x: x[1]["resultado_pct"])
        L.append(f"- `{nombre}`: de **{peor[1]['resultado_pct']:+.0f} %** a "
                 f"{peor[0]:.0f} pb hasta **{mejor[1]['resultado_pct']:+.0f} %** a "
                 f"{mejor[0]:.0f} pb — {mejor[1]['resultado_pct']-peor[1]['resultado_pct']:.0f} "
                 f"puntos porcentuales de diferencia, y órdenes "
                 f"{peor[1]['ordenes']} contra {mejor[1]['ordenes']}.")
    L.append("")
    L.append("Diez puntos básicos por lado no pueden mover un resultado decenas o cientos de")
    L.append("puntos porcentuales. **El deslizamiento cambia cuántas acciones enteras entran en")
    L.append("el margen, y eso cambia QUÉ instrumento se compra**: las filas del barrido no son")
    L.append("la misma estrategia a distinto costo, son caminos distintos.\n")

    total = 0
    marcados = 0
    for pb in pbs:
        for nombre in JUEGOS:
            _, valor = res["estrategia"][(nombre, pb)]
            for etf in ETFS_BASE:
                _, vb = res["base"][(etf, pb)]
                total += 1
                if not C.comparar(valor, vb, semilla=SEMILLA_COMPARACION)["cruza_cero"]:
                    marcados += 1
    L.append("### 3. Los `✓` de la tabla, y por qué no son una tasa de falsos positivos\n")
    L.append(f"De **{total}** comparaciones, **{marcados}** tienen un intervalo del 95 % que")
    L.append("excluye el cero. Eso NO es una tasa de falsos positivos, por las tres razones que")
    L.append("el adversario dejó escritas en el cierre de la corrida 10: la nula no es cero (el")
    L.append("arrastre de comisión garantiza una diferencia verdadera negativa); un intervalo")
    L.append("negativo que excluye el cero es el resultado VERDADERO de la fricción; y las")
    L.append(f"{total} comparaciones comparten sorteo, calendario e instrumentos. Cuánto de fácil")
    L.append("es que este diseño produzca un `✓` sin que haya nada se mide con K semillas: **está")
    L.append("medido en §1b** (20 semillas × 24 comparaciones, con Wilson), y ni siquiera eso es una")
    L.append("tasa de falsos positivos porque la nula no es cero.\n")

    sig = sigma_diferencia_semanal(res, cfg)
    L.append("### 4. La σ de la diferencia semanal, con intervalo\n")
    L.append(f"Juego por defecto (`{sig['juego']}`) contra `{sig['base']}` a {sig['deslizamiento_pb']:.0f} pb, "
             f"{sig['semanas']} semanas: **σ = {sig['sigma_pp_semana']:.3f} pp/semana**, intervalo bootstrap de "
             f"nominal 95 % {sig['ic95']} ({sig['metodo']}). Es el parámetro que la tabla de potencia del")
    cs = _cobertura_simulador(156) or {}
    cob_sd = (cs.get("cobertura_ic_sd") or {}).get("tasa")
    if cob_sd is not None:
        L.append("pre-registro (§2.1) necesitaba. **Ese intervalo NO es un 95 %:** el bloque 1 midió que el")
        L.append(f"bootstrap de bloques de una desviación cubre {cob_sd:.3f} a 156 semanas. El punto sirve de")
        L.append("insumo; el intervalo no, hasta que se calibre (decisión en `espera_firma.md` §50). La tabla")
    else:
        L.append("pre-registro (§2.1) necesitaba y que viajaba retirado y sin intervalo. La tabla")
    L.append("de potencia NO se recomputa acá: se recomputa con el simulador puesto a prueba (discrimina y NO está calibrado a α = 0,05)")
    L.append("(`GEMELO/simulador/instrumento_dinero.py`) y es un paso aparte.\n")

    L.append("### 5. Lo que esta cuenta NO midió\n")
    L.append("- **Habilidad.** No hay señal. La primera señal larga es el bloque 6 de la")
    L.append("  corrida 10 y su resultado está en `dinero/resultados/senal_larga_v1.md`.")
    L.append("- **Impacto de mercado.** El deslizamiento es un supuesto lineal por lado.")
    L.append("- **Impuestos, retención de dividendos de ADR, cambio de moneda, tarifas de")
    L.append("  terceros ni tarifas de bolsa por venue.** Ninguno está en el modelo de costo.")
    L.append("- **Que los precios sean point-in-time.** Los cierres vienen ajustados")
    L.append("  retroactivamente; está declarado en el metadato del congelado.")
    L.append("- **Supervivencia.** Los instrumentos son los que existen hoy.\n")
    return "\n".join(L) + "\n"


def a_json(cfg, res, gate: dict | None = None, semillas: dict | None = None) -> dict:
    """La misma medición, en estructura, para que la capa visual no tenga
    que parsear markdown. Se emite del mismo objeto que compone el .md."""
    aportado = sum(res["aportes"].values())
    pbs = cfg["costos"]["barrido_deslizamiento_pb"]
    c = cfg["costos"]
    salida = {
        "etiqueta": "SIMULADO",
        "estatus": "PROPUESTA",
        "version": 2,
        "reconstruccion": {
            "fecha": "2026-09-08",
            "acta": "DECISIONES.md §82.4 (opción A) y §83",
            "reemplaza": "v1 del 2026-09-07, RETIRADA por fuga temporal demostrada (dictamen 10, F1 a F4)",
            "correcciones": {
                "E1": f"membresía del universo operable decidida con los cierres hasta {DESDE}",
                "E3": f"señal sin información sorteada de retornos anteriores a {DESDE}",
                "E4": f"retardo de implementación de {C.RETARDO_IMPLEMENTACION} sesión en las dos patas",
                "E5": f"sigma del interruptor medida hasta {DESDE} (dinero/derivacion.py)",
                "E6": "gate de invariancia al truncado cableado (verificar_invariancia) y corrido antes de escribir",
            },
            "gate_invariancia": gate,
            "costo": {"fuente": "GEMELO/propuestas/insumo_40_aranceles_ibkr.md (Interactive Brokers, Pro Tiered, tabla United States, consultado el 7-sep-2026)",
                      "columna": "acciones enteras",
                      "comision_por_accion_usd": c["comision_por_accion_usd"],
                      "comision_minima_usd": c["comision_minima_usd"],
                      "comision_tope_pct_del_monto": c["comision_tope_pct_del_monto"]},
        },
        "advertencia": (
            "La señal que alimenta la estrategia NO tiene información: lo medido es "
            "fricción, no habilidad. Ninguna cifra es un resultado del proyecto y "
            "ninguna entra al README. PROPUESTA hasta el dictamen del adversario."),
        "ventana": {"desde": DESDE, "hasta": HASTA,
                    "dias_de_mercado": int(len(res["cierres"]))},
        "aportado_usd": aportado,
        "aportes": len(res["aportes"]),
        "instrumentos_operables": len(res["operables"]),
        "operables": list(res["operables"]),
        "retardo_implementacion": C.RETARDO_IMPLEMENTACION,
        "barrido_deslizamiento_pb": pbs,
        "linea_base": [], "juegos": [],
    }
    cal156 = _cobertura_simulador(156) or {}
    for etf in ETFS_BASE:
        for pb in pbs:
            libro, valor = res["base"][(etf, pb)]
            r = _resumen(libro, valor, aportado)
            salida["linea_base"].append(dict(etf=etf, deslizamiento_pb=pb, **r))
    for nombre in JUEGOS:
        for pb in pbs:
            libro, valor = res["estrategia"][(nombre, pb)]
            r = _resumen(libro, valor, aportado)
            contra = {}
            for etf in ETFS_BASE:
                _, vb = res["base"][(etf, pb)]
                cc = C.comparar(valor, vb, semilla=SEMILLA_COMPARACION)
                # D8 (re-dictamen, corrida 12): el intervalo viaja con su
                # cobertura MEDIDA en el mismo objeto. `alpha` es nominal.
                cc["alpha_es"] = "nominal"
                cc["alpha_real_medido"] = (cal156.get("alpha_real") if cal156 else None)
                cc["cobertura_medida_ic_media"] = ((cal156.get("cobertura") or {}).get("tasa") if cal156 else None)
                cc["cobertura_medida_horizonte_semanas"] = 156 if cal156 else None
                cc["fuente_cobertura"] = "GEMELO/resultados/instrumento_dinero.json calibracion.156" if cal156 else None
                contra[etf] = cc
            salida["juegos"].append(dict(juego=nombre, deslizamiento_pb=pb,
                                         contra=contra, **r))
    total = sum(1 for j in salida["juegos"] for _ in j["contra"])
    marcados = sum(1 for j in salida["juegos"]
                   for cc in j["contra"].values() if not cc["cruza_cero"])
    salida["falsos_positivos"] = {
        "comparaciones": total, "con_ic_que_excluye_cero": marcados,
        "nota": ("NO es una tasa de falsos positivos: la nula no es cero (arrastre "
                 "de comisión), un intervalo negativo es el resultado verdadero de la "
                 "fricción, y las comparaciones comparten sorteo. Con 20 semillas del "
                 "sorteo la fracción está en `barrido_semillas` con la semilla como unidad "
                 "de replicación (§1b del .md); esta celda es la de la semilla de la página.")}
    salida["sigma_dif_semanal"] = sigma_diferencia_semanal(res, cfg)
    cs = _cobertura_simulador(156) or {}
    cob_sd = (cs.get("cobertura_ic_sd") or {}).get("tasa")
    salida["sigma_dif_semanal"]["advertencia"] = (
        "El IC es un percentil de bootstrap de bloques de una DESVIACIÓN y NO es un 95 %: el "
        f"bloque 1 midió su cobertura a 156 semanas en {cob_sd if cob_sd is not None else '?'} "
        "(instrumento_dinero.md, columna «cobertura IC sd»). El punto es utilizable como insumo; "
        "el intervalo, no, hasta que se calibre. Y refleja UN sorteo de señal: ver el barrido de "
        "semillas.")
    salida["sigma_dif_semanal"]["cobertura_medida_del_ic_a_156_semanas"] = cob_sd
    salida["barrido_semillas"] = semillas
    salida["sesgo_de_la_sonda"] = sesgo_de_la_sonda(res, cfg)
    salida["membresia"] = membresia_como_corte(res, cfg)
    salida["cobertura_del_instrumento_a_156_semanas"] = _cobertura_simulador(156)
    return salida


def main():
    gate = verificar_invariancia()      # E6: si hay fuga, revienta antes de escribir
    cfg, res = correr()
    semillas = barrido_semillas(cfg)
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(componer(cfg, res, gate, semillas))
    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(a_json(cfg, res, gate, semillas), f, indent=1, ensure_ascii=False,
                  default=float)
        f.write("\n")
    print("gate:", gate["resultado"], gate["cortes"])
    print("escrito", SALIDA, "y", SALIDA_JSON)


if __name__ == "__main__":
    main()
