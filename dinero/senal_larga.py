# ============================================================
# dinero/senal_larga.py — la primera señal larga del riel de dinero.
#
# PRE-REGISTRADA en GEMELO/preregistro/senal_larga_v1.md, commiteado ANTES
# que este archivo (commit e368dad). Tres especificaciones —L1, L2, L3—
# declaradas por nombre, dos horizontes, y ninguna cuarta: esa tentación es
# el sesgo que el registro de intentos mide.
#
# HIPÓTESIS: el retorno de un eslabón anticipa el del eslabón aguas abajo,
# con retardo de semanas. Nula económica a vencer: el sector se mueve como
# un bloque y toda «anticipación» es la misma noticia llegando a dos
# precios a la vez. L2 existe para atacar exactamente esa alternativa.
#
# ============================================================
# LO QUE LA AUDITORÍA DE FUGA CAMBIÓ, ANTES DE LA PRIMERA MEDICIÓN
# ============================================================
# `auditor-lookahead` corrió sobre la v1 de este archivo —como manda el
# pre-registro §8: antes, no después— y encontró una fuga DEMOSTRADA más
# tres sesgos que empujaban a favor. Se arreglaron los cinco puntos antes de
# calcular un solo número. Queda escrito acá porque el archivo sin esta
# historia parece haber nacido bien:
#
#  · **F1, fuga de selección (R3).** La composición de cada eslabón salía de
#    `construir_mapa`, que decide con `ultimo_cierre` del archivo ENTERO si
#    una acción «alcanza con 500 USD». O sea: la membresía de ocho años la
#    fijaba el último renglón, y el filtro expulsa a los que SUBIERON
#    (excluidos: retorno mediano 847 % contra 547 % de los incluidos).
#    Microsoft quedaba fuera de «demanda final» durante ocho años por 70
#    centavos del último día. Medido: truncar en 2025-12-31 cambiaba el
#    42,9 % de las filas, desde la primera del panel.
#    → Ahora la membresía se decide al PRINCIPIO de la muestra y con
#      criterio de cobertura, no de precio. `construir_paneles` la recibe
#      como argumento para que la dependencia sea explícita.
#  · **S1, el protocolo ejecutado no era el pre-registrado.** El walk-forward
#    expansivo metía hasta el 36 % del último ajuste DENTRO del período de
#    prueba, mientras el reporte imprimía «ajuste y prueba congelados».
#    → Gana el pre-registro: un solo ajuste sobre el período congelado, una
#      sola evaluación sobre el de prueba. Errata fechada en el §8 del
#      pre-registro, escrita SIN haber visto ningún resultado.
#  · **S2, L2 no quitaba la beta común.** La beta salía pooleada sobre los
#    siete pares; los residuos seguían cargando la cesta (beta residual de
#    −0,20 a +0,14 según eslabón), y con eso la regla «si L1 gana y L2 no,
#    era beta común» quedaba ininterpretable en las dos direcciones.
#    → Beta POR ESLABÓN, estimada sólo en ajuste.
#  · **S3, L3 medía su propio objetivo.** La dispersión transversal incluía
#    al eslabón de abajo (corr hasta +0,57 con su propio retorno).
#    → La dispersión excluye al eslabón objetivo de cada par.
#  · **S7, retardo de implementación cero.** La etiqueta arrancaba en el
#    mismo cierre con que se decide. Nadie ejecuta al cierre que acaba de
#    observar, y el auditor midió que un día de retardo mueve la etiqueta
#    3,6–4,0 pp de media: **del mismo orden que el umbral de señal del juego
#    conservador (3,49 pp)**.
#    → La etiqueta arranca en t+1. Esto hace la vara MÁS difícil, no menos.
#  · **S8, `sign(0) == sign(0)` contaba como acierto.** El proyecto ya
#    congeló `excluir_cero` por este mismo artefacto (GEMELO/DISEÑO §2.8).
#    → Las filas con retorno real exactamente cero salen de la métrica de
#      dirección, de los dos lados.
#
# Lo que NO se arregló, porque no se puede con estos datos, va declarado en
# el reporte: supervivencia (los 36 tickers son los que existen hoy), que la
# fuente no es point-in-time, la identidad de VRT (fue un SPAC hasta feb-2020)
# y la fuga por el analista, que sólo el sellado en vivo desmiente.
#
# ------------------------------------------------------------
# CÓMO SE EVITA LA FUGA TEMPORAL
# ------------------------------------------------------------
# 1. Features: retornos acumulados HACIA ATRÁS, r(t-h → t). Nunca tocan
#    datos posteriores a t.
# 2. Etiqueta: r(t+1 → t+1+h). Es futuro por definición —eso es lo que se
#    predice— y su ventana cierra en t+h+1, que es lo que gobierna el embargo.
# 3. El ajuste usa SOLO pares cuya ventana de etiqueta cierra antes del
#    inicio del período de prueba, menos el embargo.
# 4. Las betas de L2 se estiman SOLO con datos de ajuste.
# 5. `construir_paneles` es PURA y recibe la membresía: el test de causalidad
#    le trunca la entrada y comprueba que nada cambia (tests/test_senal_larga.py).
# ============================================================
from __future__ import annotations

import numpy as np
import pandas as pd

from dinero import precios
from dinero import universo_dinero as U

EMBARGO_DIAS = 5
RETARDO_IMPLEMENTACION = 1   # se decide con el cierre de t, se entra en t+1
HORIZONTES = (20, 60)
CESTA = "SMH"
MINIMO_AJUSTE = 250

# Congelados ANTES de mirar (pre-registro §8).
AJUSTE_DESDE = "2018-09-05"
AJUSTE_HASTA = "2023-09-04"
PRUEBA_DESDE = "2023-09-05"
PRUEBA_HASTA = "2026-09-04"

# Cobertura mínima exigida a un instrumento para componer un eslabón,
# medida SOBRE EL PERÍODO DE AJUSTE y por lo tanto decidida al principio de
# la muestra. Sin esto, ARM entra nueve días después de PRUEBA_DESDE y el
# índice de `diseno_eda` cambia de composición justo en la frontera.
COBERTURA_MINIMA_AJUSTE = 0.98

CADENA = ("materias_primas", "materiales_obleas", "litografia_equipos",
          "fabricacion_vanguardia", "memoria", "ensamblaje_prueba",
          "diseno_eda", "demanda_final")
PARES = tuple(zip(CADENA[:-1], CADENA[1:]))
ESPECIFICACIONES = ("L1", "L2", "L3")


# ------------------------------------------------------------
# Los eslabones como series
# ------------------------------------------------------------
def miembros_por_eslabon(cierres: pd.DataFrame,
                         hasta: str = AJUSTE_HASTA) -> dict:
    """Composición de cada eslabón, decidida con datos del PRINCIPIO.

    Criterio, y es de cobertura y no de precio: entra el instrumento que
    (a) es del eslabón, (b) no es una cesta —un ETF no es un eslabón— y
    (c) tiene cierre en al menos el 98 % de las sesiones del período de
    AJUSTE. Nada de esto mira el nivel del precio ni el final de la muestra.

    La versión anterior filtraba por «¿entra una acción en 500 dólares?»
    usando el último cierre del archivo: eso expulsaba a los que subieron y
    era fuga de selección demostrada. La restricción de presupuesto es real,
    pero es una restricción de DECISIÓN —vive en `dinero/decision.py`, que la
    aplica con el precio del día— y no de construcción del índice."""
    ajuste = cierres.loc[:hasta]
    n = len(ajuste)
    salida = {}
    for clave in CADENA:
        elegidos = []
        for c in U.CANDIDATOS:
            if c.eslabon != clave or c.forma == "ETF":
                continue
            if c.ticker not in cierres.columns:
                continue
            if n and ajuste[c.ticker].notna().sum() / n >= COBERTURA_MINIMA_AJUSTE:
                elegidos.append(c.ticker)
        salida[clave] = elegidos
    return salida


def retornos_eslabon(cierres: pd.DataFrame, miembros: dict) -> pd.DataFrame:
    """Retorno diario de cada eslabón: promedio equiponderado del retorno de
    sus miembros. Se promedian RETORNOS y no precios: promediar precios de
    instrumentos de escala distinta deja al más caro mandando el índice."""
    r = cierres.pct_change()
    cols = {}
    for clave, ts in miembros.items():
        if ts:
            cols[clave] = r[ts].mean(axis=1, skipna=True)
    return pd.DataFrame(cols)


def _acumulado_hacia_atras(r: pd.Series, h: int) -> pd.Series:
    """Retorno compuesto de los h días hábiles que TERMINAN en t (inclusive)."""
    return (1.0 + r).rolling(h).apply(np.prod, raw=True) - 1.0


def _acumulado_hacia_adelante(r: pd.Series, h: int,
                              retardo: int = RETARDO_IMPLEMENTACION) -> pd.Series:
    """Retorno compuesto de los h días hábiles que empiezan `retardo` días
    después de t. Con retardo 1: se decide con el cierre de t y se entra al
    cierre de t+1. La ventana cierra en t+h+retardo."""
    return _acumulado_hacia_atras(r, h).shift(-(h + retardo))


def construir_paneles(cierres: pd.DataFrame, h: int,
                      miembros: dict | None = None) -> dict:
    """Función PURA: de cierres (y una membresía dada) a los paneles.

    `miembros` entra como argumento a propósito: mientras la composición se
    calculaba adentro y miraba el final del archivo, el valor de una feature
    en t cambiaba al borrar el futuro. Pasarla explícitamente hace visible de
    qué depende el panel."""
    miembros = miembros_por_eslabon(cierres) if miembros is None else miembros
    r_esl = retornos_eslabon(cierres, miembros)
    r_cesta = cierres[CESTA].pct_change() if CESTA in cierres.columns else None

    atras = {c: _acumulado_hacia_atras(r_esl[c], h) for c in r_esl.columns}
    adelante = {c: _acumulado_hacia_adelante(r_esl[c], h) for c in r_esl.columns}
    atras_cesta = (_acumulado_hacia_atras(r_cesta, h)
                   if r_cesta is not None else None)
    adelante_cesta = (_acumulado_hacia_adelante(r_cesta, h)
                      if r_cesta is not None else None)

    marco_atras = pd.DataFrame(atras)

    paneles = {}
    for espec in ESPECIFICACIONES:
        filas = []
        for arriba, abajo in PARES:
            if arriba not in atras or abajo not in adelante:
                continue
            if espec == "L2":
                if atras_cesta is None:
                    continue
                filas.append(pd.DataFrame({
                    "fecha": atras[arriba].index, "par": f"{arriba}>{abajo}",
                    "x": atras[arriba].to_numpy(),
                    "x_cesta": atras_cesta.to_numpy(),
                    "y": adelante[abajo].to_numpy(),
                    "y_cesta": adelante_cesta.to_numpy()}))
                continue
            if espec == "L3":
                # La dispersión EXCLUYE al eslabón objetivo: incluirlo hacía
                # que L3 midiera el propio retorno de la serie que predice.
                otros = [c for c in marco_atras.columns if c != abajo]
                x = marco_atras[otros].std(axis=1, ddof=1)
            else:
                x = atras[arriba]
            filas.append(pd.DataFrame({
                "fecha": x.index, "par": f"{arriba}>{abajo}",
                "x": x.to_numpy(), "y": adelante[abajo].to_numpy()}))
        panel = pd.concat(filas, ignore_index=True) if filas else pd.DataFrame()
        paneles[espec] = panel.dropna().reset_index(drop=True)
    return paneles


# ------------------------------------------------------------
# Ajuste ÚNICO sobre el período congelado, evaluación ÚNICA sobre el de prueba
# ------------------------------------------------------------
def _ols(x: np.ndarray, y: np.ndarray):
    """(a, b, sigma) de y = a + b·x. Sin dependencias nuevas."""
    n = len(x)
    if n < 3:
        return 0.0, 0.0, float("nan")
    mx, my = x.mean(), y.mean()
    vx = ((x - mx) ** 2).sum()
    b = float(((x - mx) * (y - my)).sum() / vx) if vx > 0 else 0.0
    a = float(my - b * mx)
    res = y - (a + b * x)
    return a, b, float(np.std(res, ddof=2))


def corte_de_ajuste(fechas: np.ndarray, h: int,
                    embargo: int = EMBARGO_DIAS) -> np.datetime64:
    """Última fecha de emisión admisible en el ajuste.

    La etiqueta de una emisión en s cierra en s + h + retardo. Para que
    ninguna etiqueta de ajuste alcance el período de prueba hay que
    retroceder ese largo MÁS el embargo desde PRUEBA_DESDE. Sin esto, un par
    de hace h−1 días sigue mirando el futuro de la fecha en que se predice y
    ninguna guarda de «datos ≤ t» se queja."""
    purga = h + RETARDO_IMPLEMENTACION + embargo
    posteriores = np.where(fechas >= pd.Timestamp(PRUEBA_DESDE))[0]
    i0 = int(posteriores[0]) if len(posteriores) else len(fechas)
    return fechas[max(0, i0 - purga)]


def evaluar(panel: pd.DataFrame, espec: str, h: int,
            embargo: int = EMBARGO_DIAS) -> pd.DataFrame:
    """Un ajuste, una evaluación. Es lo que dice el pre-registro §8 —«años de
    ajuste y prueba congelados antes de mirar»— y lo que la v1 no hacía: su
    walk-forward expansivo metía hasta el 36 % del último ajuste dentro del
    período de prueba mientras el reporte afirmaba lo contrario."""
    if panel.empty:
        return pd.DataFrame()
    fechas = np.array(sorted(pd.to_datetime(panel["fecha"].unique())))
    corte = corte_de_ajuste(fechas, h, embargo)
    ajuste = panel[panel["fecha"] < corte]
    prueba = panel[(panel["fecha"] >= pd.Timestamp(PRUEBA_DESDE)) &
                   (panel["fecha"] <= pd.Timestamp(PRUEBA_HASTA))]
    if len(ajuste) < MINIMO_AJUSTE or prueba.empty:
        return pd.DataFrame()

    if espec == "L2":
        # Beta POR ESLABÓN, no pooleada: una sola beta para los siete pares
        # dejaba residuos que seguían cargando la cesta, y con eso la regla
        # «si L1 gana y L2 no, era beta común» no se podía leer.
        betas_x, betas_y = {}, {}
        for par in ajuste["par"].unique():
            sub = ajuste[ajuste["par"] == par]
            _, bx, _ = _ols(sub["x_cesta"].to_numpy(), sub["x"].to_numpy())
            _, by, _ = _ols(sub["y_cesta"].to_numpy(), sub["y"].to_numpy())
            betas_x[par], betas_y[par] = bx, by

        def residuos(df):
            bx = df["par"].map(betas_x).to_numpy()
            by = df["par"].map(betas_y).to_numpy()
            return (df["x"].to_numpy() - bx * df["x_cesta"].to_numpy(),
                    df["y"].to_numpy() - by * df["y_cesta"].to_numpy())

        xa, ya = residuos(ajuste)
        xp, yp = residuos(prueba)
    else:
        xa, ya = ajuste["x"].to_numpy(), ajuste["y"].to_numpy()
        xp, yp = prueba["x"].to_numpy(), prueba["y"].to_numpy()

    a, b, sigma = _ols(xa, ya)
    sigma_cero = float(np.std(ya, ddof=1))
    clima = float((ya > 0).mean())
    # CLIMATOLOGÍA CAUSAL: la media de la etiqueta EN EL AJUSTE, en el mismo
    # espacio de cada especificación (residual para L2, crudo para el resto).
    # Es la vara que el adversario del proyecto ya exigía antes de esta
    # corrida: «predecir cero» no es una vara neutra en un mercado que sube,
    # porque cero está sesgado hacia abajo respecto de la media incondicional.
    clima_media = float(np.mean(ya))
    sigma_clima = sigma_cero
    return pd.DataFrame({
        "fecha": prueba["fecha"].to_numpy(), "par": prueba["par"].to_numpy(),
        "pred": a + b * xp, "real": yp, "sigma": sigma,
        "sigma_cero": sigma_cero, "clima": clima,
        "clima_media": clima_media, "sigma_clima": sigma_clima,
        "a": a, "b": b, "n_ajuste": len(ajuste),
        "corte_ajuste": str(pd.Timestamp(corte).date()),
    })


def cargar_cierres():
    """Sólo el congelado. Si falta, revienta: no se descarga al vuelo."""
    return precios.cargar_congelado()
