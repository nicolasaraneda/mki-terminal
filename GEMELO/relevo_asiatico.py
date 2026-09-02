# ============================================================
# GEMELO/relevo_asiatico.py — WS5: la hipótesis del relevo asiático
# (Etapa 6.0.0).
#
#   source venv/bin/activate
#   python -m GEMELO.relevo_asiatico
#
# ============================================================
# ⚠ POST-HOC. ESTO NO ES CONFIRMATORIO.
# ============================================================
# La hipótesis se formó DESPUÉS de ver el desglose por bolsa del WS4: el
# campeón gana +15 a +19 pp en las bolsas que abren dentro de 3 h de la
# emisión y solo +2.5 pp (p=0.111) en Fráncfort, que abre 8.75 h después.
# La explicación candidata es que para Europa el SOX de hace nueve horas NO
# es la información más fresca — entre medio Asia operó una sesión entera —
# y que la cadena real sería NY → Asia → Europa.
#
# Una hipótesis construida sobre un patrón ya visto NO se confirma con los
# datos que la sugirieron. El techo alcanzable aquí es «NO REFUTADA».
# Pre-registro completo, con el N y la regla de decisión declarados ANTES de
# correr: GEMELO/resultados/preregistro_ws5.md.
#
# ============================================================
# LO QUE HACE FALSABLE ESTO: LA PRUEBA DE SIMETRÍA
# ============================================================
# Las mismas tres configuraciones se corren sobre los objetivos ASIÁTICOS.
# Si el mecanismo es propagación con decaimiento, E2 debe mejorar a E1 en
# Fráncfort y NO mejorarlo en Asia, donde el SOX ya es el insumo fresco. Si
# E2 gana en las dos, no es relevo: es capacidad, y la hipótesis cae.
#
# ============================================================
# LA TRAMPA, Y ES GRAVE
# ============================================================
# Para un objetivo asiático su PROPIO índice local es casi circular:
# Samsung está dentro del KOSPI, TSMC dentro del TWSE. Sin excluirlo, E2
# luciría espectacular en Asia por la razón equivocada y la prueba de
# simetría concluiría lo contrario de lo que los datos dicen. Se excluye
# SIEMPRE el índice de la bolsa del objetivo, y hay un test que lo fija.
#
# ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1 y no calcula el escalonado de
# B0→B5. No se toca motor.py, senales.py, snapshot.py, el camino de sellado
# ni universo.py.
# ============================================================

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

import calendarios
from universo import EXCHANGE_POR_TICKER, MERCADOS_POR_ABRIR

from backtest import inferencia as inf

from GEMELO import control_lineal as cl
from GEMELO import datos, features
from GEMELO.experimento import _tabla, construir_panel

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "resultados")

# ============================================================
# CONTEO DE INTENTOS DEL DSR — REGISTRO ESTRUCTURADO
# ============================================================
# Regla congelada (`GEMELO/DISEÑO.md`:363-364, §4.2 bis): un intento =
# (configuración × ventana de evaluación) con resultado reportable.
# Regla de arbitraje, de Nicolás (2026-09-01): **lo que define un intento
# es que se evaluó una configuración y se miró el resultado.** Un intento
# descartado por malo cuenta; uno cuya CONCLUSIÓN se retractó, también —
# la retractación de la corrida de `concentracion.md` fue sobre su
# conclusión, no sobre que esos análisis se corrieron. Simétricamente: un
# experimento **declarado y nunca corrido** NO cuenta, y una condición
# declarada **NO MEDIBLE** tampoco, porque nadie miró un resultado.
#
# Por qué esto es una tabla y no un entero: hasta el 2026-09-01 este
# archivo declaraba `N_INTENTOS_WS5 = 25` con un test que fijaba el
# literal, mientras cuatro documentos del repo declaraban 25 / 26 / 32 /
# 43 / 82. **El test hacía al número inmune a la corrección en vez de
# protegerlo de la corrupción** — es la cuarta regla de la casa. Con el
# desglose como DATO, el test verifica que la suma cuadre y que cada
# tramo cite su evidencia; agregar un intento es agregar una fila, y el
# número se recalcula solo. Un entero no se puede auditar; una tabla sí.
#
# Columnas: (n, tramo, qué se evaluó, dónde vive la evidencia).
# ------------------------------------------------------------
REGISTRO_INTENTOS = (
    # --- lo que el WS5 ya contenía cuando se selló (subtotal 25) -------
    (6, "WS0", "B0-B5, walk-forward de humo 2026-06-01 -> 07-18",
     "backtest/resultados/20260726-032635-humo-legacy/resumen.md"),
    (3, "WS2b", "C1, C2, C3 sobre la ventana sellada",
     "GEMELO/resultados/control_lineal.md:62-64"),
    (3, "WS3", "C1, C2, C3 sobre la ventana larga",
     "GEMELO/resultados/ventana_larga.md:124-126"),
    (1, "WS3", "campeón reconstruido (= B2) sobre la ventana larga, "
               "convención estricta", "GEMELO/DISEÑO.md:386"),
    (12, "WS5", "E1, E2, E3 x {XETR, ASIA} x {exploración, holdout}",
     "GEMELO/resultados/relevo_asiatico.md:149-160"),
    # --- corridas posteriores al sello del WS5 ------------------------
    (6, "CONDICIONAL", "5 condiciones candidatas MEDIDAS + el modelo "
                       "conjunto; la 6a (densidad de noticias) se declaró "
                       "NO MEDIBLE y por eso NO cuenta",
     "GEMELO/CONDICIONAL/DISEÑO.md:268-289; medidas en "
     "GEMELO/resultados/bitacora_02.md:74-94"),
    (3, "CONCENTRACION", "3 scan-statistics sobre la ventana sellada",
     "GEMELO/resultados/concentracion.md:85-89"),
    (8, "CONCENTRACION", "8 McNemar por bolsa (4 bolsas x dentro/fuera "
                         "del bloque 15-23-jul)",
     "GEMELO/resultados/concentracion.md:50-55"),
    (1, "CONCENTRACION", "scan-statistic de ancho fijo 6 sobre la ventana "
                         "LARGA (ventana distinta de los 3 anteriores)",
     "GEMELO/resultados/bitacora_02.md:64-67"),
    (4, "WS4", "campeón desglosado por bolsa sobre la ventana larga "
               "(+19.1 / +16.8 / +15.4 / +2.5 pp); el WS5 entero nació de "
               "mirarlos", "GEMELO/resultados/auditoria_ws3.md:26-31"),
    (2, "WS4", "campeón sobre la ventana larga bajo las convenciones "
               "`verificador` (+15.27) y `excluir_cero` (+15.66); el "
               "intento del WS3 sólo cubrió `estricta` (+15.90)",
     "GEMELO/resultados/auditoria_ws3.md:131-135"),
    (5, "DISEÑO §2", "abstención por magnitud a los umbrales 0.15 / 0.25 / "
                     "0.30 / 0.50 / 0.75 (el 0.00 es la mirada base y no "
                     "se cuenta dos veces)", "GEMELO/DISEÑO.md:115-121"),
    (1, "RELEVO", "la abstención a 0.25 RE-evaluada sobre la ventana "
                  "sellada actual (+6.5 -> +10.7 pp); ancla el umbral de "
                  "5 pp de REL-V4", "GEMELO/RELEVO.md:177-183"),
    (2, "DISEÑO §2", "hipótesis del punto de giro: particiones "
                     "SOX usado < 0 y >= 0 (formulada y refutada)",
     "GEMELO/DISEÑO.md:87-88"),
    (6, "DISEÑO §2", "los 6 bloques de 40 filas de «dónde está la ventaja "
                     "en el tiempo». Cuentan: de ahí salió la ventana "
                     "15-23-jul que R2 congeló como vara permanente, o "
                     "sea que SÍ se tomó una decisión mirándolos",
     "GEMELO/DISEÑO.md:66-78"),
    (4, "DOS VENTANAS", "desglose por bolsa de la ventana sellada COMPLETA "
                        "(distinta de los 8 McNemar dentro/fuera)",
     "GEMELO/resultados/dos_ventanas.md:217-222"),
    (4, "ERRATA §38", "recomputo de C1, C2, C3 y CAMPEÓN sobre la ventana "
                      "sellada nueva (pares n=240)", "DECISIONES.md §38.2"),
    (2, "COLA", "reglas de deduplicación keep=\"first\" (+6.64 pp, "
                "p=0.1847) y keep=\"last\" (+9.96 pp, p=0.0323); «sin "
                "deduplicar» es el statu quo ya contado",
     "GEMELO/resultados/cola_decisiones.md:88-91"),
    (7, "PASIVO", "las miradas al duelo campeón-vs-baseline, contadas por "
                  "(convención x población) DISTINTA: 9 combinaciones "
                  "únicas de las 12 lecturas, menos 2 ya contadas aquí "
                  "(excluir_cero n=240 va en ERRATA §38; excluir_cero "
                  "n=184 es el umbral 0.25 de DISEÑO §2)",
     "GEMELO/SECUENCIAL/DISEÑO.md:207-225"),
    (6, "5.1", "B0-B5 sobre la ventana de evaluación nueva "
               "2024-09-02 -> 2026-08-28 (ventana nueva => intentos "
               "nuevos)", "backtest/veredicto_51.py:54"),
    (5, "BANCO", "las 5 cláusulas candidatas corridas por el banco de "
                 "pruebas: C1 (era del Mac), C2 (era de las dos "
                 "máquinas), C3a y C3b (las DOS lecturas de «selló a "
                 "tiempo»: contra la apertura y contra la ventana "
                 "operativa) y C4 («iguales» leído sobre el desenlace). "
                 "Cada una define una población distinta de la ventana "
                 "sellada y de cada una se leyó un duelo, así que cada "
                 "una es una configuración. C3a y C3b cuentan por "
                 "separado a propósito: una operacionalización distinta "
                 "es una configuración distinta, y evaluar dos para "
                 "reportar una sería elegir la definición sin decirlo",
     "GEMELO/resultados/clausulas.md; ejecutable en "
     "GEMELO/banco_clausulas.py:CANDIDATAS"),
    # --- séptima corrida, 2-sep-2026: registrados por exigencia del
    # dictamen del estadistico-adversario ("ninguna configuración nueva
    # puede alimentar un DSR hasta que el registro las absorba") ---------
    (4, "TRAY", "cuatro estadísticos principales candidatos NUEVOS evaluados "
                "sobre la trayectoria real de la ventana sellada (Frente C): "
                "t sobre medias diarias, posterior con prior N(0, 0,05²), "
                "proceso de apuestas anytime-valid (c=0,5, α=0,05) y signo "
                "de los días. McNemar, IC de clúster de día y permutación de "
                "signo por día no cuentan: eran maquinaria ya registrada",
     "GEMELO/SECUENCIAL/trayectoria.py:CANDIDATOS; "
     "GEMELO/resultados/propuestas_cde.md §C"),
    (5, "ESTIM", "cinco estimandos alternativos evaluados sobre la ventana "
                 "sellada y la larga (Frente E): magnitud |g|−|p−g|, gap "
                 "capturado continuo, pendiente de calibración g~p, "
                 "pendiente del decaimiento por hora y contraste "
                 "Asia−Fráncfort. La dirección (E0) no cuenta: es el "
                 "endpoint congelado. Se cuentan como configuraciones, no "
                 "como configuraciones × ventana: ninguno se eligió por "
                 "ventana",
     "GEMELO/SECUENCIAL/estimandos.py:CLAVES; "
     "GEMELO/resultados/propuestas_cde.md §E"),
)

# EL número vigente. Se calcula, no se escribe.
N_INTENTOS_ACUMULADO = sum(f[0] for f in REGISTRO_INTENTOS)

# El sello histórico del WS5: lo que este archivo declaró el 2026-08-30 y
# lo que el reporte `GEMELO/resultados/relevo_asiatico.md` lleva impreso.
# Se conserva SOLO para que ese reporte siga siendo reproducible y para
# que el test pueda verificar su desglose. **No es el N vigente y no se
# usa para calcular nada**: quien necesite un N para un DSR usa
# `N_INTENTOS_ACUMULADO`.
N_ACUMULADO_WS3 = 13                       # sello histórico (WS3, 26-ago)
N_INTENTOS_WS5 = 25                        # sello histórico (WS5, 30-ago)

# Lo que NO se cuenta, declarado para que la exclusión sea auditable y no
# desaparezca (cada línea es «se evaluó pero nadie miró un resultado», o
# «no es selección de modelo»):
#   - el complemento ventana larga vs. sellada, DECLARADO Y NUNCA CORRIDO
#     (`dos_ventanas.md`:178-184). El 82 del expediente 5.1 lo incluyó por
#     conservadurismo; la regla de arbitraje lo excluye.
#   - la densidad de noticias como condición candidata: NO MEDIBLE
#     (`bitacora_02.md`:74-76). Incluida en el 43 y en el 82; se excluye.
#   - las 576 celdas de `GEMELO/bifurcaciones.py`: censo exhaustivo de
#     convenciones de MEDICIÓN, sin selección de modelo. Pero citar
#     cualquier celda suelta como resultado del proyecto SÍ mueve este
#     registro, y hay que decirlo en el mismo párrafo.
#   - la baseline «siempre al alza» (es la hipótesis nula) y la búsqueda
#     interna de `alpha` por CV temporal (`GEMELO/DISEÑO.md`:374-377).
#   - MDE, fronteras de gasto de alpha, BLOQUES_FECHAS, el RTL del frente
#     MICRO y las tres rutas del McNemar: parámetros de diseño o elección
#     de método, no configuraciones predictivas.
#   - del banco de cláusulas (`GEMELO/banco_clausulas.py`): la regla
#     FIRMADA corrida como referencia (ya evaluada, publicada y
#     aplicada); `C4b`, que resulta ser exactamente el `keep="first"` ya
#     contado en la fila `COLA` —contarlo otra vez sería inflar el N por
#     haberlo mirado desde otro nombre—; la `CLAUSULA_TRAMPA`, que es la
#     contraprueba del instrumento y de la que no se lee ningún resultado
#     sobre el modelo; y las mediciones de asociación criterio-acierto,
#     que son diagnóstico del método.
#
# El desglose por bolsa dentro de ASIA en el WS5 tampoco suma: el ajuste
# tiene que ser por bolsa (la trampa), pero el resultado reportable es el
# del estrato. Si alguna decisión se tomara mirándolo, son 6 intentos más
# y hay que declararlo.
# ------------------------------------------------------------

ANIOS = 8
FRACCION_HOLDOUT = 0.20        # último 20% de fechas de emisión, en cuarentena

# El índice local de cada bolsa, en el nombre que tiene como feature. Es la
# lista de exclusión de la trampa: nunca alimenta a un objetivo de su
# propia bolsa.
INDICE_POR_EXCHANGE = {
    "XKRX": "ks11_ret",
    "XTAI": "twii_ret",
    "XTKS": "n225_ret",
    "XETR": "gdaxi_ret",
}
FEATURES_ASIA = ("ks11_ret", "twii_ret", "n225_ret")
FEATURES_ASIA_TICKERS = ("^KS11", "^TWII", "^N225")
FEATURES_SOX = cl.FEATURES_SOLO_SOX          # ("sox_t", "sox_t1")

ESTRATOS = {"XETR": ("XETR",), "ASIA": ("XKRX", "XTAI", "XTKS")}
PORCIONES = ("exploracion", "holdout")


def features_e2(exchange: str) -> tuple:
    """Los cierres asiáticos MENOS el índice de la bolsa del objetivo.

    Es la regla anti-trampa, y vive aquí —en una función— para que un test
    pueda comprobarla en vez de que sea un comentario.
    """
    propio = INDICE_POR_EXCHANGE.get(exchange)
    return tuple(f for f in FEATURES_ASIA if f != propio)


def configuraciones(exchange: str) -> dict:
    """Las TRES configuraciones declaradas, resueltas para una bolsa."""
    e2 = features_e2(exchange)
    return {
        "E1": {"features": FEATURES_SOX, "agrupado": True,
               "descripcion": "solo el SOX (t y t-1) — CONTROL: la "
                              "información actual del sistema"},
        "E2": {"features": e2, "agrupado": True,
               "descripcion": f"solo cierres asiáticos {list(e2)} — el "
                              f"relevo (excluido el índice de {exchange})"},
        "E3": {"features": tuple(FEATURES_SOX) + e2, "agrupado": True,
               "descripcion": "ambos"},
    }


# ------------------------------------------------------------
# DISPONIBILIDAD — se demuestra, no se asume
# ------------------------------------------------------------
def disponibilidad_relevo(sesion_xetr: str = "2026-08-26") -> dict:
    """Las dos mitades de la disponibilidad, MEDIDAS.

    (a) La que la hipótesis necesita: la apertura de XETR del día D+1
        ocurre DESPUÉS del cierre asiático del día D ⇒ la relación es
        causal. Se calcula con `calendarios.apertura_utc`, que usa los
        calendarios históricos reales, y con los cierres sellados en
        `datos.CATALOGO`.

    (b) La que la hipótesis NO menciona, y cambia qué significa un nulo:
        a la emisión (22:15 UTC del día D) el ^SOX de D tiene ~1.25 h y el
        ^KS11 de D tiene ~15.75 h. Bajo la restricción de emisión del
        sistema el insumo asiático disponible es el MÁS VIEJO. La sesión
        asiática que el relato describe —la que ocurre entre el cierre del
        SOX y la apertura de Fráncfort— cierra el día D+1 y NO es conocible
        a la emisión.
    """
    apertura = calendarios.apertura_utc("XETR", sesion_xetr)
    # El día de emisión que anticipa esa sesión: el hábil anterior.
    dia_d = (pd.Timestamp(sesion_xetr) - pd.tseries.offsets.BDay(1)).date()
    emision = datos.emision_utc(dia_d)
    filas = []
    for tk in ("^SOX",) + FEATURES_ASIA_TICKERS:
        s = datos.CATALOGO[tk]
        for etiqueta, dia in (("D", dia_d),
                              ("D+1", apertura.date())):
            av = s.available_at(dia)
            filas.append({
                "serie": tk, "barra": etiqueta,
                "cierre_utc": av.isoformat(),
                "h_antes_de_la_emision": round(
                    (emision - av).total_seconds() / 3600, 2),
                "h_antes_de_apertura_XETR": round(
                    (apertura - av).total_seconds() / 3600, 2),
                "conocible_a_la_emision": bool(av <= emision),
            })
    return {
        "sesion_xetr": sesion_xetr,
        "dia_emision": str(dia_d),
        "emision_utc": emision.isoformat(),
        "apertura_xetr_utc": apertura.isoformat(),
        "h_emision_a_apertura": round(
            (apertura - emision).total_seconds() / 3600, 2),
        "series": filas,
    }


def causalidad_xetr_ok(sesion_xetr: str) -> bool:
    """La condición dura: la apertura de XETR de la sesión objetivo ocurre
    después del cierre asiático del día de emisión, y ese cierre es
    conocible a la emisión."""
    d = disponibilidad_relevo(sesion_xetr)
    de_d = [f for f in d["series"] if f["barra"] == "D"
            and f["serie"] in FEATURES_ASIA_TICKERS]
    return bool(de_d) and all(f["conocible_a_la_emision"]
                              and f["h_antes_de_apertura_XETR"] > 0
                              for f in de_d)



# ------------------------------------------------------------
# La convención del empate, aplicada desde la primera línea
# ------------------------------------------------------------
def excluir_cero(df: pd.DataFrame) -> pd.DataFrame:
    """`excluir_cero` congelada en §2.8: las filas con `gap == 0.00` se
    descartan de AMBOS lados.

    `gap == 0.00` exacto es la firma del ffill de feriados (Supuesto #1),
    no un evento de mercado. El WS3 no la aplicó y se infló 0.24 pp
    (WS4, Amenaza 3). `cl.evaluar` NO se modifica —un test del WS4 fija su
    comportamiento actual—: se filtra antes y se delega.
    """
    if df.empty:
        return df
    return df[df["gap_pct"] != 0.0].copy()


def evaluar(df: pd.DataFrame, etiqueta: str) -> dict:
    return cl.evaluar(excluir_cero(df), etiqueta)


def comparar(a: pd.DataFrame, b: pd.DataFrame, na: str, nb: str) -> dict:
    """Comparación pareada con la convención aplicada y **el IC del ΔMAE en
    su propia escala**.

    HALLAZGO DEL WS5, y toca a los reportes anteriores: `cl.comparar`
    acompaña un `delta_mae` en **pp** con un intervalo salido de
    `inf.bootstrap_bloques`, que es el IC del **Sharpe** (media/desv). Son
    escalas distintas, y se ve a simple vista: en 8 de los 12 pares de esta
    corrida el punto estimado caía FUERA de su propio intervalo.

    **Ninguna conclusión previa cambia:** las decisiones se tomaron con
    `ic_excluye_cero`, que es exactamente equivalente en ambas escalas
    (`sd > 0` conserva el signo réplica a réplica, y el evento depende solo
    de la proporción de réplicas sobre cero). Lo que estaba mal era el
    número impreso, no el veredicto.

    Aquí se publican los dos, con el nombre que dice qué es cada uno:
    `ic_sharpe_dmae` (la maquinaria del WS2b/WS3, para comparabilidad) e
    `ic_delta_mae_pp` (el intervalo de lo que la columna dice ser).
    """
    a, b = excluir_cero(a), excluir_cero(b)
    r = cl.comparar(a, b, na, nb)
    if not r.get("n"):
        return r
    j = a.merge(b, on=["fecha", "ticker"], suffixes=("_a", "_b"))
    gap = j["gap_pct_a"].to_numpy(float)
    dif = (np.abs(j["pred_b"].to_numpy(float) - gap)
           - np.abs(j["pred_a"].to_numpy(float) - gap))
    ic = inf.bootstrap_media(dif, semilla=cl.SEMILLA_BOOTSTRAP,
                             bloque=cl.BLOQUE_BOOTSTRAP,
                             alpha=cl.ALPHA_BOOTSTRAP)
    r["ic_sharpe_dmae"] = r.pop("delta_mae_ic")
    r["ic_delta_mae_pp"] = [round(ic["lo"], 4), round(ic["hi"], 4)]
    r["ic_pp_excluye_cero"] = bool(ic["lo"] > 0 or ic["hi"] < 0)
    return r


# ------------------------------------------------------------
# El experimento
# ------------------------------------------------------------
def correr(anios: int = ANIOS, usar_cache: bool = True,
           embargo_dias: int = cl.EMBARGO_DIAS,
           fraccion_holdout: float = FRACCION_HOLDOUT) -> dict:
    series, descartadas = datos.series_para_investigacion(
        anios=anios, usar_cache=usar_cache)
    feats = features.construir(series, verificar=False)
    gaps = datos.descargar_gaps(tuple(MERCADOS_POR_ABRIR), anios=anios,
                                usar_cache=usar_cache)
    panel = construir_panel(feats, gaps)
    panel = panel.sort_values(["fecha", "ticker"]).reset_index(drop=True)
    panel["exchange"] = panel["ticker"].map(EXCHANGE_POR_TICKER)

    fechas = np.array(sorted(panel["fecha"].unique()))
    corte = pd.Timestamp(fechas[int(len(fechas) * (1 - fraccion_holdout))])

    # --- walk-forward por BOLSA (el índice excluido depende de la bolsa) ---
    predicciones = {}          # (config, exchange) -> frame
    for exchange in sorted(panel["exchange"].dropna().unique()):
        sub = panel[panel["exchange"] == exchange]
        cfgs = configuraciones(exchange)
        for nombre, cfg in cfgs.items():
            df = cl.correr_configuracion(nombre, sub, sub, embargo_dias,
                                         cfg=cfg)
            if not df.empty:
                df = df.copy()
                df["exchange"] = exchange
            predicciones[(nombre, exchange)] = df

    def _slice(nombre, bolsas, porcion):
        trozos = [predicciones.get((nombre, b), pd.DataFrame())
                  for b in bolsas]
        trozos = [t for t in trozos if not t.empty]
        if not trozos:
            return pd.DataFrame()
        d = pd.concat(trozos, ignore_index=True)
        if porcion == "exploracion":
            return d[d["fecha"] < corte].copy()
        if porcion == "holdout":
            return d[d["fecha"] >= corte].copy()
        return d

    resultados, pares, por_bolsa = [], [], []
    marcos = {}
    for estrato, bolsas in ESTRATOS.items():
        for porcion in PORCIONES:
            for nombre in ("E1", "E2", "E3"):
                d = _slice(nombre, bolsas, porcion)
                marcos[(nombre, estrato, porcion)] = d
                if d.empty:
                    continue
                r = evaluar(d, nombre)
                r |= {"estrato": estrato, "porcion": porcion}
                resultados.append(r)
            for a, b in (("E2", "E1"), ("E3", "E1"), ("E3", "E2")):
                da = marcos[(a, estrato, porcion)]
                db = marcos[(b, estrato, porcion)]
                if da.empty or db.empty:
                    continue
                p = comparar(da, db, a, b)
                p |= {"estrato": estrato, "porcion": porcion}
                pares.append(p)

    # Desglose DESCRIPTIVO por bolsa (declarado: no suma a N; ninguna
    # decisión se toma mirándolo).
    for exchange in sorted(panel["exchange"].dropna().unique()):
        for porcion in PORCIONES:
            da = _slice("E2", (exchange,), porcion)
            db = _slice("E1", (exchange,), porcion)
            if da.empty or db.empty:
                continue
            p = comparar(da, db, "E2", "E1")
            p |= {"bolsa": exchange, "porcion": porcion}
            por_bolsa.append(p)

    ventana_sesion = _sesion_xetr_de_referencia(panel)
    return {
        "es_veredicto_5_1": False,
        "calcula_veredicto_escalonado": False,
        "post_hoc": True,
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "parametros": {
            "N_intentos_declarado": N_INTENTOS_ACUMULADO,
            "N_intentos_sello_ws5": N_INTENTOS_WS5,
            "desglose_N": " + ".join(f"{n} {tramo}"
                                     for n, tramo, _, _ in REGISTRO_INTENTOS),
            "registro_intentos": [{"n": n, "tramo": t, "que": q, "fuente": f}
                                  for n, t, q, f in REGISTRO_INTENTOS],
            "regla_conteo": "un intento = (configuración × ventana de "
                            "evaluación) con resultado reportable",
            "convencion_empate": "excluir_cero (§2.8) — aplicada, a "
                                 "diferencia del WS3",
            "embargo_dias": embargo_dias,
            "ventana_entrenamiento": "EXPANSIVA (todo el pasado disponible)",
            "ajuste": "ridge agrupada DENTRO de la bolsa del objetivo",
            "alphas_cv": list(cl.ALPHAS_CV), "pliegues_cv": cl.PLIEGUES_CV,
            "minimo_entrenamiento": cl.MINIMO_ENTRENAMIENTO,
            "semilla_bootstrap": cl.SEMILLA_BOOTSTRAP,
            "bloque_bootstrap": cl.BLOQUE_BOOTSTRAP,
            "alpha_bootstrap": cl.ALPHA_BOOTSTRAP,
            "fraccion_holdout": fraccion_holdout,
            "corte_holdout": str(corte.date()),
            "anios_datos": anios,
        },
        "exclusion_por_bolsa": [
            {"bolsa": e, "indice_excluido": INDICE_POR_EXCHANGE.get(e),
             "E2": list(features_e2(e))}
            for e in sorted(panel["exchange"].dropna().unique())],
        "disponibilidad": disponibilidad_relevo(ventana_sesion),
        "descartadas_por_cobertura": descartadas,
        "ventana": {
            "desde": str(panel["fecha"].min().date()),
            "hasta": str(panel["fecha"].max().date()),
            "fechas": int(panel["fecha"].nunique()),
            "filas_panel": int(len(panel)),
            "corte_holdout": str(corte.date()),
            "fechas_exploracion": int(
                panel[panel["fecha"] < corte]["fecha"].nunique()),
            "fechas_holdout": int(
                panel[panel["fecha"] >= corte]["fecha"].nunique()),
        },
        "resultados": resultados,
        "pares": pares,
        "por_bolsa_descriptivo": por_bolsa,
        "veredicto": veredicto(pares),
    }


def _sesion_xetr_de_referencia(panel: pd.DataFrame) -> str:
    """Una sesión real de XETR dentro de la ventana, para medir la
    disponibilidad sobre un caso que existe y no sobre uno inventado."""
    d = panel[panel["ticker"] == "IFX.DE"]
    if d.empty:
        return "2026-08-26"
    f = pd.Timestamp(d["fecha"].max())
    return str((f + pd.tseries.offsets.BDay(1)).date())


def veredicto(pares: list) -> dict:
    """La regla de decisión del preregistro §6, aplicada MECÁNICAMENTE.

    Primario: E2 vs E1, pareado, en DIRECCIÓN, sobre el HOLDOUT.
    «E2 mejora a E1» ⟺ ventaja > 0 y McNemar p < 0.05.
    """
    def mejora(estrato):
        for p in pares:
            if (p.get("estrato") == estrato and p.get("porcion") == "holdout"
                    and p.get("par") == "E2 vs E1"):
                return (p.get("ventaja_pp", 0) > 0
                        and p.get("mcnemar_p", 1.0) < 0.05), p
        return None, None

    xetr, p_x = mejora("XETR")
    asia, p_a = mejora("ASIA")
    if xetr is None or asia is None:
        return {"veredicto": "NO COMPUTABLE",
                "motivo": "falta el par E2 vs E1 en algún estrato del holdout"}
    if xetr and not asia:
        v = "NO REFUTADA"
        lectura = ("E2 mejora a E1 en Fráncfort y no en Asia: es el patrón "
                   "que el relevo predice. Techo alcanzable para una "
                   "hipótesis post-hoc.")
    elif xetr and asia:
        v = "REFUTADA (capacidad)"
        lectura = ("E2 mejora a E1 en las dos: añadir regresores mejora en "
                   "todas partes. No es relevo.")
    elif not xetr and asia:
        v = "REFUTADA (al revés de lo predicho)"
        lectura = ("E2 no mejora donde debería y sí donde no debería.")
    else:
        v = "REFUTADA (ausencia)"
        lectura = ("E2 no mejora a E1 en Fráncfort: el relevo no aporta "
                   "donde el mecanismo lo exige.")
    return {"veredicto": v, "lectura": lectura,
            "E2_mejora_E1_en_XETR": bool(xetr),
            "E2_mejora_E1_en_ASIA": bool(asia),
            "par_XETR": p_x, "par_ASIA": p_a}


# ------------------------------------------------------------
# Informe
# ------------------------------------------------------------
def informe(r: dict) -> str:
    p, v, w = r["parametros"], r["ventana"], r["veredicto"]
    disp = r["disponibilidad"]
    L = ["# ⚠ ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1", "",
         "Es una corrida de investigación (Etapa 6.0.0 WS5). El veredicto de",
         "la 5.1 es el criterio **escalonado capa-contra-capa sobre B0→B5**,",
         "con sus reglas congeladas en el GATE B, y su ejecución es **decisión",
         "humana**. Aquí NO se calcula ni se emite juicio sobre B0→B5.",
         "", "---", "",
         "# ⚠ Y ESTO ES POST-HOC. Sin eufemismos.", "",
         "**La hipótesis del relevo asiático se formó DESPUÉS de ver el",
         "desglose por bolsa del WS4.** No es confirmatoria: es exploratoria.",
         "Una hipótesis construida sobre un patrón ya visto **no se confirma",
         "con los datos que la sugirieron**. El techo alcanzable es",
         "«NO REFUTADA».",
         "",
         "El pre-registro —N, configuraciones y regla de decisión— se escribió",
         "y se dejó en el árbol **antes** de correr nada:",
         "[`preregistro_ws5.md`](preregistro_ws5.md).",
         "", "---", "",
         "# La hipótesis del relevo asiático", "",
         f"- Generado: {r['generado_utc']}",
         f"- Ventana: **{v['desde']} → {v['hasta']}** · {v['fechas']} fechas "
         f"de emisión · {v['filas_panel']} filas de panel",
         f"- Corte del holdout: **{v['corte_holdout']}** "
         f"({v['fechas_exploracion']} fechas de exploración · "
         f"**{v['fechas_holdout']} de holdout**)",
         "", "---", "",
         "## VEREDICTO", "",
         f"# {w.get('veredicto')}", "",
         w.get("lectura", ""), ""]
    if w.get("par_XETR"):
        L += ["El criterio primario, sobre el holdout:", "",
              _tabla([w["par_XETR"], w["par_ASIA"]])]
    L += ["---", "",
          "## Lo que este experimento NO puede probar — y hay que decirlo antes",
          "",
          "La hipótesis dice: «entre el cierre del SOX y la apertura de",
          "Fráncfort, Asia operó una sesión entera». **Esa sesión es la del día",
          "D+1, y NO es conocible a la emisión.**",
          "",
          f"Emisión del sistema: **{disp['emision_utc']}** (22:15 UTC del día "
          f"D). Apertura de XETR de la sesión objetivo: "
          f"**{disp['apertura_xetr_utc']}**, es decir "
          f"**{disp['h_emision_a_apertura']} h después**.",
          "", _tabla(disp["series"]),
          "Léase la columna `h_antes_de_la_emision`: **un número negativo",
          "significa que esa barra aún no existía cuando el sistema emitió.**",
          "",
          "De ahí salen dos hechos que cambian cómo debe leerse todo lo que",
          "sigue:",
          "",
          "1. **La sesión asiática fresca —la del día D+1, que cierra ~30 min",
          "   antes de que Fráncfort abra— NO es conocible a la emisión.** El",
          "   relato del relevo describe exactamente esa sesión. Este",
          "   experimento **no puede** probarla sin romper la restricción de",
          "   emisión del sistema.",
          "2. **El insumo asiático que SÍ es conocible es el MÁS VIEJO de los",
          "   dos.** A las 22:15 UTC del día D el `^SOX` de D tiene ~1.25 h y",
          "   el `^KS11` de D tiene ~15.75 h. Peor: el `^KS11` de D cerró",
          "   **antes** que el `^SOX` de D, así que reacciona al SOX de D−1 —",
          "   que E1 ya lleva dentro como `sox_t1`.",
          "",
          "> **Consecuencia para la lectura:** lo que se prueba aquí es la",
          "> versión **débil y compatible con el sistema** de la hipótesis:",
          "> ¿aporta la componente idiosincrática asiática del día D algo por",
          "> encima del SOX? Un resultado NULO refuta **esa** versión, y **no**",
          "> refuta el mecanismo del relevo con información fresca — que",
          "> seguiría siendo indemostrable sin mover la hora de emisión, y",
          "> mover la hora de emisión es territorio del modelo congelado.",
          "", "---", "",
          "## La trampa, y cómo se evitó", "",
          "Para un objetivo asiático su **propio** índice local es casi",
          "circular: Samsung está dentro del KOSPI, TSMC dentro del TWSE. Sin",
          "excluirlo, E2 luciría espectacular en Asia **por la razón",
          "equivocada** y la prueba de simetría concluiría lo contrario de lo",
          "que los datos dicen. Va como test, no como comentario.", "",
          _tabla(r["exclusion_por_bolsa"]),
          "## Parámetros sellados", "",
          "| Parámetro | Valor |", "|---|---|",
          f"| **N intentos acumulado (DSR)** | **{p['N_intentos_declarado']}** |",
          f"| Sello histórico del WS5 (superado el 01-sep) | {p['N_intentos_sello_ws5']} |",
          f"| Desglose | {p['desglose_N']} |",
          f"| Regla de conteo | {p['regla_conteo']} |",
          f"| **Convención del empate** | **{p['convencion_empate']}** |",
          f"| Embargo | {p['embargo_dias']} días |",
          f"| Ventana de entrenamiento | {p['ventana_entrenamiento']} |",
          f"| Ajuste | {p['ajuste']} |",
          f"| Alphas de la CV | {p['alphas_cv']} |",
          f"| Pliegues de la CV temporal | {p['pliegues_cv']} |",
          f"| Mínimo de entrenamiento | {p['minimo_entrenamiento']} filas |",
          f"| Semilla / bloque / alpha del bootstrap | "
          f"{p['semilla_bootstrap']} / {p['bloque_bootstrap']} / "
          f"{p['alpha_bootstrap']} |",
          f"| Fracción del holdout | {p['fraccion_holdout']} "
          f"(corte {p['corte_holdout']}) |",
          f"| Años de datos | {p['anios_datos']} |",
          "",
          f"**El N acumulado vigente es {N_INTENTOS_ACUMULADO}**, reconstruido",
          "desde las actas y con desglose auditable en la constante",
          "`REGISTRO_INTENTOS` de este mismo archivo. Al sellarse el WS5 el",
          f"conteo leía **{N_INTENTOS_WS5}** ({N_ACUMULADO_WS3} hasta WS3 + 12); esa cifra",
          "quedó **superada** el 2026-09-01 y se conserva sólo como sello",
          "histórico. Doce",
          "intentos nuevos salen de aplicar la regla congelada",
          "**mecánicamente**: tres configuraciones × dos estratos × dos",
          "porciones, y las doce son reportables. Contarlas de otro modo sería",
          "elegir el N que favorece al DSR, que es justo lo que el DSR existe",
          "para castigar. **No se probó una cuarta configuración.**",
          "",
          "## El holdout, y su cuarentena PARCIAL", "",
          "La cuarentena aquí es **procedimental**: configuraciones, regla de",
          "decisión y N quedaron fijados antes de correr, así que no hay nada",
          "que ajustar mirando el holdout.",
          "",
          "**Pero está contaminado y se declara:** la observación que generó la",
          "hipótesis —el +2.5 pp de Fráncfort del WS4— se midió sobre la",
          "ventana **completa**, holdout incluido. El holdout está en",
          "cuarentena frente a las decisiones de **este** experimento, no",
          "frente al hecho que lo motivó. Llamarla completa sería mentir.",
          "",
          "## Resultados por configuración", "",
          _tabla(r["resultados"]),
          "## Comparaciones pareadas", "",
          "Sobre las filas que **ambas** configuraciones predijeron.",
          "`delta_mae > 0` significa que A tiene MENOS error que B.", "",
          _tabla(r["pares"]),
          "### ⚠ Hallazgo colateral: el IC del ΔMAE venía en otra escala", "",
          "`cl.comparar` —la función que el WS2b escribió y el WS3 heredó—",
          "acompaña un `delta_mae` en **pp** con un intervalo salido de",
          "`inf.bootstrap_bloques`, que es el IC del **Sharpe** (media/desv).",
          "Son dos escalas distintas, y se ve a simple vista: **en 8 de los 12",
          "pares de esta corrida el punto estimado caía FUERA de su propio",
          "intervalo.**",
          "",
          "**Ninguna conclusión previa cambia.** Las decisiones se tomaron con",
          "`ic_excluye_cero`, que es **exactamente** equivalente en ambas",
          "escalas: `sd > 0` conserva el signo réplica a réplica, así que el",
          "evento «el cuantil α/2 está sobre cero» depende solo de la",
          "proporción de réplicas sobre cero, y ésa es idéntica para la media",
          "y para media/desv. Lo que estaba mal era el **número impreso**, no",
          "el veredicto.",
          "",
          "Aquí se publican los dos, con el nombre que dice qué es cada uno:",
          "`ic_sharpe_dmae` (la maquinaria del WS2b/WS3, para que las cifras",
          "sigan siendo comparables) e **`ic_delta_mae_pp`** (el intervalo de",
          "lo que la columna dice ser, vía `inf.bootstrap_media`, que comparte",
          "sorteo y semilla con el otro).",
          "",
          "**No se corrigió ningún reporte anterior** — eso es criterio de",
          "Nicolás y queda como pregunta abierta.", ""
          "## Desglose por bolsa — DESCRIPTIVO, no decisorio", "",
          "El ajuste **tiene** que ser por bolsa (la exclusión del índice",
          "propio depende de ella), pero el resultado reportable es el del",
          "estrato. Esta tabla se publica para que el lector vea la",
          "heterogeneidad; **ninguna decisión se toma mirándola.** Si alguna se",
          f"tomara, N sube de {N_INTENTOS_ACUMULADO} a "
          f"{N_INTENTOS_ACUMULADO + 6} y hay que decirlo.", "",
          _tabla(r["por_bolsa_descriptivo"])]
    if r["descartadas_por_cobertura"]:
        L += ["## Series descartadas por cobertura", "",
              _tabla(r["descartadas_por_cobertura"])]
    L += ["---",
          "Herramienta de análisis — no constituye asesoría financiera.",
          "Diseño congelado en GEMELO/DISEÑO.md. **No es el veredicto de la",
          "5.1** y **no calcula el veredicto escalonado de B0→B5.**",
          "**POST-HOC: exploratorio, no confirmatorio.**"]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="WS5 — relevo asiático (POST-HOC; NO es el veredicto de "
                    "la 5.1).")
    ap.add_argument("--anios", type=int, default=ANIOS)
    ap.add_argument("--sin-cache", action="store_true")
    ap.add_argument("--sin-escribir", action="store_true")
    args = ap.parse_args(argv)
    r = correr(anios=args.anios, usar_cache=not args.sin_cache)
    texto = informe(r)
    print(texto)
    if not args.sin_escribir:
        os.makedirs(DIR_RESULTADOS, exist_ok=True)
        with open(os.path.join(DIR_RESULTADOS, "relevo_asiatico.md"), "w",
                  encoding="utf-8") as f:
            f.write(texto)
        with open(os.path.join(DIR_RESULTADOS, "relevo_asiatico.json"), "w",
                  encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2, default=str)
        print(f"[escrito] {DIR_RESULTADOS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
