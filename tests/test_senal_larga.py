# ============================================================
# tests/test_senal_larga.py — GATE de causalidad de la señal larga v1.
#
# Escrito por `auditor-lookahead` ANTES de la primera medición, como manda
# GEMELO/preregistro/senal_larga_v1.md §8. El orden importa: un test de
# fuga escrito después de ver el resultado ya no es un test, es una excusa.
#
# QUÉ SE PRUEBA, en orden de importancia:
#
#   1. LA PRUEBA MAESTRA. `construir_paneles` es pura: truncar los cierres
#      en T no puede alterar NINGUNA fila con fecha <= T-h (h días de
#      negociación, no de calendario). Hoy FALLA — ver el xfail estricto y
#      la fuga confirmada que documenta.
#   2. LOCALIZACIÓN. Con la membresía congelada la invariancia se cumple
#      exacta (0.0). Eso prueba que la fuga está entera en
#      `miembros_por_eslabon` y que el resto del pipeline —acumulados,
#      shift, dispersión, residualización— está limpio.
#   3. CONTRAPRUEBA. Se inyecta una fuga (`shift(-1)`) y se comprueba que
#      el criterio de (1) la caza. Un test de fuga que no puede fallar no
#      prueba nada.
#   4. ARITMÉTICA DEL DESPLAZAMIENTO. La feature en t no toca t+1; la
#      etiqueta en t está anclada en el precio de t y cierra en t+h.
#   5. EMBARGO. Ninguna fila de ajuste tiene ventana de etiqueta que llegue
#      a la fecha en que se predice, con la separación declarada.
#
# Nada de este archivo calcula MAE, acierto ni CRPS: medir es el bloque de
# `senal_larga_reporte`, y el pre-registro exige que la auditoría vaya
# primero. Este archivo audita ENTRADAS, nunca resultados.
# ============================================================
import os
import sys

import numpy as np
import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dinero import senal_larga as SL
from dinero import universo_dinero as U

# E7 (auditor, corridas 10 y 11): cortes DENTRO del período de ajuste, no
# sólo en o después de su borde, para que esta vía pueda ponerse roja.
CORTES = ("2020-12-31", "2022-12-30", "2023-09-04", "2024-12-31", "2025-12-31")
TOL = 1e-12


# ------------------------------------------------------------
# utilidades
# ------------------------------------------------------------
def _cierres():
    return SL.cargar_cierres()


def _limite_exacto(cierres, T, h):
    """La última fecha cuya etiqueta CIERRA en T o antes.

    ACTUALIZADO tras la corrección de S7 (retardo de implementación): la
    etiqueta ya no va de t a t+h sino de t+1 a t+1+h, así que el límite
    retrocede un día más. Es la única constante de este archivo que la
    corrección movió, y se mueve acá y no en la tolerancia.

    Se cuenta en días de NEGOCIACIÓN sobre el índice real, no con `BDay`:
    `BDay` cuenta lunes-viernes e ignora los feriados de NY, así que da un
    límite demasiado laxo y el test dejaría pasar filas cuya etiqueta se
    trunca. La diferencia medida en esta muestra es de 7 a 21 filas."""
    idx = cierres.index[cierres.index <= pd.Timestamp(T)]
    return idx[-1 - h - SL.RETARDO_IMPLEMENTACION]


def _comparar(cierres, T, h, espec, construir=None):
    """Filas comunes del panel completo y del truncado en T, hasta el
    límite exacto. Devuelve (n_completo, n_truncado, n_comun, max_dif)."""
    construir = construir or SL.construir_paneles
    lim = _limite_exacto(cierres, T, h)
    completo = construir(cierres, h)[espec]
    truncado = construir(cierres.loc[:T], h)[espec]
    llave = ["fecha", "par"]
    a = completo[completo["fecha"] <= lim].set_index(llave).sort_index()
    b = truncado[truncado["fecha"] <= lim].set_index(llave).sort_index()
    comun = a.index.intersection(b.index)
    cols = [c for c in ("x", "y", "x_cesta", "y_cesta") if c in a.columns]
    if len(comun) == 0:
        return len(a), len(b), 0, float("nan")
    dif = (a.loc[comun, cols] - b.loc[comun, cols]).abs().to_numpy()
    return len(a), len(b), len(comun), float(np.nanmax(dif))


# ------------------------------------------------------------
# 1. LA PRUEBA MAESTRA
# ------------------------------------------------------------
# HISTORIA DE ESTE TEST, que no se borra porque es lo que le da valor:
# nació en XFAIL ESTRICTO documentando una fuga CONFIRMADA. `construir_paneles`
# llamaba a `miembros_por_eslabon` -> `U.construir_mapa(cierres)`, que decidía
# la composición de cada eslabón con `precios.ultimo_cierre`, o sea el precio
# del ÚLTIMO día del archivo. Con la muestra completa ese día era 2026-09-04 y
# el filtro `alcanza_con_techo` (¿entra 1 acción en 500 USD?) expulsaba a ASML,
# MU, SNDK, MSFT y META; truncando en 2025-12-31 los admitía, y cambiaban el
# 42,9 % de las filas del panel desde 2018-11-29, con diferencias de hasta
# 0,907 en la etiqueta. Se arregló ANTES de la primera medición: la membresía
# se decide ahora por cobertura sobre el período de AJUSTE, al principio de la
# muestra y sin mirar el nivel del precio. El xfail se quitó porque el test
# pasa, no porque estorbara.
@pytest.mark.parametrize("T", CORTES)
@pytest.mark.parametrize("h", SL.HORIZONTES)
@pytest.mark.parametrize("espec", SL.ESPECIFICACIONES)
def test_construir_paneles_es_invariante_a_borrar_el_futuro(T, h, espec):
    """EL test. El valor en t no puede depender de datos posteriores a t."""
    c = _cierres()
    n_a, n_b, n_com, dif = _comparar(c, T, h, espec)
    assert n_a == n_b == n_com, (
        f"{espec} h={h} T={T}: el truncado cambia el CENSO de filas "
        f"(completo {n_a}, truncado {n_b}, comunes {n_com})")
    assert dif <= TOL, (
        f"{espec} h={h} T={T}: truncar en {T} altera filas anteriores a "
        f"{_limite_exacto(c, T, h).date()} en hasta {dif:.6e} — HAY FUGA")


# ------------------------------------------------------------
# 2. LOCALIZACIÓN: dónde está la fuga y dónde no
# ------------------------------------------------------------
@pytest.mark.parametrize("T", CORTES)
@pytest.mark.parametrize("h", SL.HORIZONTES)
@pytest.mark.parametrize("espec", SL.ESPECIFICACIONES)
def test_con_la_membresia_congelada_la_invariancia_es_exacta(
        T, h, espec, monkeypatch):
    """Aísla la fuga. Si la composición de los eslabones se fija por fuera
    —cualquier composición, con tal de que no dependa del largo del
    archivo— entonces los acumulados hacia atrás y hacia adelante, el
    `shift(-h)`, la dispersión de L3 y las series de la cesta de L2 son
    exactamente invariantes a borrar el futuro. La diferencia no es
    'pequeña': es 0.0. Luego el defecto es UNO solo y tiene nombre."""
    c = _cierres()
    fijos = SL.miembros_por_eslabon(c)
    monkeypatch.setattr(SL, "miembros_por_eslabon", lambda cierres: fijos)
    n_a, n_b, n_com, dif = _comparar(c, T, h, espec)
    assert n_a == n_b == n_com, (n_a, n_b, n_com)
    assert dif == 0.0, f"{espec} h={h} T={T}: dif={dif:.6e}"


def test_la_composicion_del_eslabon_ya_no_mira_el_final_de_la_muestra():
    """Guarda de regresión del defecto F1, invertida.

    Este test decía lo contrario: comprobaba que `miembros_por_eslabon`
    cambiaba al truncar, porque `U.construir_mapa` preguntaba por
    `precios.ultimo_cierre` —el último cierre no nulo del DataFrame
    entero— y decidía con el final de la muestra la composición de ocho
    años. Los hechos que midió la auditoría sobre el congelado sha256
    69ca7283… quedan escritos acá para que no se pierdan: `memoria` se
    quedaba con WDC solo y perdía a Micron, su dominante declarado; y
    `demanda_final` perdía a MSFT y META —Microsoft cerró a 499,70 y con
    la comisión mínima de 1 USD no entraba en 500, así que quedaba fuera
    del eslabón durante ocho años por setenta centavos del último día.

    Ahora se exige lo inverso: que truncar el archivo NO cambie la
    composición, y que los dominantes hayan vuelto."""
    c = _cierres()
    hoy = SL.miembros_por_eslabon(c)
    for corte in ("2025-12-31", "2024-12-31"):
        assert SL.miembros_por_eslabon(c.loc[:corte]) == hoy, (
            f"truncar en {corte} cambia la composición: la membresía "
            f"volvió a depender del final de la muestra")
    assert "MU" in hoy["memoria"], "Micron es el dominante declarado de memoria"
    assert {"MSFT", "META"} <= set(hoy["demanda_final"])
    assert "ASML" in hoy["litografia_equipos"]
    for clave, ts in hoy.items():
        assert ts, f"el eslabón {clave} quedó sin miembros"


def test_la_membresia_no_usa_el_filtro_de_presupuesto():
    """La restricción de presupuesto es real pero es de DECISIÓN, no de
    construcción del índice: vive en `dinero/decision.py`, que la aplica
    con el precio del día. Usarla para componer el índice es filtrar por un
    nivel de precio del final de la muestra, que es el defecto F1."""
    import inspect
    fuente = inspect.getsource(SL.miembros_por_eslabon)
    assert "alcanza_con_techo" not in fuente
    assert "construir_mapa" not in fuente


def test_el_filtro_de_precio_excluye_por_haber_subido():
    """Dirección del sesgo, no sólo su existencia. `alcanza_con_techo` es
    un filtro sobre el NIVEL de precio al final de la muestra; el nivel
    final es, mecánicamente, el nivel inicial por el retorno de la muestra.
    Luego el filtro descarta a los que más subieron. No es ruido: es sesgo
    con signo, y el signo apunta a excluir ganadores."""
    c = _cierres()
    mapa = {f.candidato.ticker: f for f in U.construir_mapa(c)}
    dentro, fuera = [], []
    for t in c.columns:
        f = mapa.get(t)
        if f is None or not f.verificado or f.candidato.forma == "ETF":
            continue
        s = c[t].dropna()
        (dentro if f.alcanza_con_techo else fuera).append(
            float(s.iloc[-1] / s.iloc[0] - 1.0))
    assert fuera, "sin excluidos no hay nada que auditar"
    assert np.median(fuera) > np.median(dentro), (
        f"mediana del retorno total: excluidos {np.median(fuera):.2f} vs "
        f"incluidos {np.median(dentro):.2f}")


# ------------------------------------------------------------
# 3. CONTRAPRUEBA: el criterio de (1) sabe fallar
# ------------------------------------------------------------
@pytest.mark.parametrize("h", SL.HORIZONTES)
def test_el_gate_detecta_una_fuga_inyectada_en_la_feature(h, monkeypatch):
    """Se envenena `_acumulado_hacia_atras` con un `shift(-1)`: la feature de
    t pasa a leer el cierre de t+1. Con la membresía congelada —o sea con la
    fuga real neutralizada— el gate tiene que ponerse rojo igual.

    LECCIÓN DEL PROPIO GATE, y por eso queda escrita acá: la fuga de un día
    NO se manifiesta como diferencia de valor. `_acumulado_hacia_adelante`
    llama a `_acumulado_hacia_atras` por nombre global, así que el veneno
    corre parejo en la feature y en la etiqueta, y las filas que quedan en
    los DOS paneles siguen coincidiendo dígito a dígito (medido: dif = 0.0).
    Lo único que la delata es el CENSO: el panel truncado ya no puede
    producir la última fila —le falta un día— y sale 10857 contra 10864,
    exactamente una fila por cada uno de los 7 pares. Un gate que sólo
    compare valores sobre la intersección de filas es CIEGO a esta familia
    entera de fugas. La comparación de censo no es un extra: es la mitad
    del criterio."""
    c = _cierres()
    fijos = SL.miembros_por_eslabon(c)
    monkeypatch.setattr(SL, "miembros_por_eslabon", lambda cierres: fijos)
    limpio = SL._acumulado_hacia_atras
    monkeypatch.setattr(SL, "_acumulado_hacia_atras",
                        lambda r, hh: limpio(r, hh).shift(-1))
    n_a, n_b, n_com, dif = _comparar(c, "2024-12-31", h, "L1")
    assert n_com > 0
    assert n_a != n_b or dif > TOL, (
        "el gate NO detectó una fuga inyectada de un solo día: el criterio "
        "es ciego y todo verde suyo es falso")
    assert n_a > n_b, (
        "se esperaba que la delatara el censo; si la delata el valor, "
        "revisar el razonamiento del docstring antes de creerle al verde")


@pytest.mark.parametrize("espec", SL.ESPECIFICACIONES)
def test_el_gate_detecta_una_normalizacion_con_toda_la_muestra(
        espec, monkeypatch):
    """Tercera contraprueba, de la familia que SÍ mueve valores: se z-scorea
    la feature con la media y la desviación de la muestra ENTERA. Es la fuga
    más común del oficio —normalizar antes de partir— y no toca el censo,
    así que ejercita el otro brazo del criterio."""
    c = _cierres()
    fijos = SL.miembros_por_eslabon(c)
    monkeypatch.setattr(SL, "miembros_por_eslabon", lambda cierres: fijos)
    limpio = SL._acumulado_hacia_atras

    def envenenado(r, hh):
        s_ = limpio(r, hh)
        return (s_ - s_.mean()) / s_.std()

    monkeypatch.setattr(SL, "_acumulado_hacia_atras", envenenado)
    n_a, n_b, n_com, dif = _comparar(c, "2024-12-31", 20, espec)
    assert n_com > 0
    assert dif > TOL, (
        f"{espec}: el gate no vio una normalización con toda la muestra")


def test_el_gate_detecta_una_fuga_inyectada_en_la_composicion(monkeypatch):
    """Segunda contraprueba, de otra familia: una composición elegida con el
    futuro —los que más subieron en TODA la muestra— también tiene que hacer
    fallar el gate. Es exactamente la FORMA de la fuga real del módulo, y
    por eso sirve de patrón de regresión cuando se arregle."""
    c = _cierres()
    base = SL.miembros_por_eslabon(c)

    def mirando_adelante(cierres):
        retorno_total = cierres.iloc[-1] / cierres.iloc[0]
        top = set(retorno_total.sort_values().index[-12:])
        elegidos = {k: [t for t in v if t in top] for k, v in base.items()}
        # que no quede un eslabón vacío: el gate debe fallar por la fuga,
        # no por un panel que se desarmó.
        return {k: (v if v else base[k]) for k, v in elegidos.items()}

    monkeypatch.setattr(SL, "miembros_por_eslabon", mirando_adelante)
    _, _, n_com, dif = _comparar(c, "2024-12-31", 20, "L1")
    assert n_com > 0
    assert dif > TOL, "el gate no vio una selección hecha con el futuro"


# ------------------------------------------------------------
# 4. ARITMÉTICA DEL DESPLAZAMIENTO
# ------------------------------------------------------------
def _precios_sinteticos(n=400, semilla=20260907):
    rng = np.random.default_rng(semilla)
    idx = pd.bdate_range("2020-01-01", periods=n)
    return pd.Series(100.0 * np.exp(np.cumsum(rng.normal(0, 0.01, n))),
                     index=idx)


@pytest.mark.parametrize("h", (5, 20, 60))
def test_los_acumulados_caen_exactamente_donde_dice_la_documentacion(h):
    """`atras[t]` = p[t]/p[t-h] - 1 y, con retardo de implementación d=1,
    `adelante[t]` = p[t+h+d]/p[t+d] - 1. Se comprueba contra la razón de
    precios, que es la definición, y no contra otra implementación del
    mismo error."""
    p = _precios_sinteticos()
    r = p.pct_change()
    atras = SL._acumulado_hacia_atras(r, h)
    adelante = SL._acumulado_hacia_adelante(r, h)
    d = SL.RETARDO_IMPLEMENTACION
    for t in (h, h + 1, 150, len(p) - h - d - 1):
        assert atras.iloc[t] == pytest.approx(
            p.iloc[t] / p.iloc[t - h] - 1.0, rel=1e-12)
        assert adelante.iloc[t] == pytest.approx(
            p.iloc[t + h + d] / p.iloc[t + d] - 1.0, rel=1e-12)
    # y el borde: la etiqueta no existe para los últimos h+d días
    assert adelante.iloc[-(h + d):].isna().all()


@pytest.mark.parametrize("h", (5, 20))
def test_la_feature_de_t_no_toca_ningun_precio_posterior_a_t(h):
    """Prueba de mancha: se perturba UN precio futuro y se exige que la
    feature de t no se mueva. Cubre el off-by-one de un día, que es el que
    ninguna revisión de lectura ve."""
    p = _precios_sinteticos()
    t = 200
    atras = SL._acumulado_hacia_atras(p.pct_change(), h)
    for adelanto in (1, 2, h):
        q = p.copy()
        q.iloc[t + adelanto] *= 1.37
        sucio = SL._acumulado_hacia_atras(q.pct_change(), h)
        assert sucio.iloc[t] == pytest.approx(atras.iloc[t], rel=1e-12), (
            f"la feature en t cambió al perturbar t+{adelanto}")


@pytest.mark.parametrize("h", (5, 20))
def test_la_etiqueta_de_t_esta_anclada_en_t_y_cierra_en_t_mas_h(h):
    """Con retardo de implementación d, la etiqueta de t debe moverse si se
    perturba cualquier precio de (t+d, t+h+d], y NO moverse si se perturba
    t+h+d+1 ni el propio t. Fija los DOS bordes: el derecho gobierna el
    tamaño del embargo, y el izquierdo es lo que hace que el retardo sea de
    verdad un retardo — si la etiqueta siguiera anclada en el cierre de t,
    se estaría entrando al mismo precio que se acaba de observar."""
    p = _precios_sinteticos()
    t = 200
    d = SL.RETARDO_IMPLEMENTACION
    ade = SL._acumulado_hacia_adelante(p.pct_change(), h)
    q = p.copy()
    q.iloc[t + h + d] *= 1.37
    assert SL._acumulado_hacia_adelante(q.pct_change(), h).iloc[t] != \
        pytest.approx(ade.iloc[t], rel=1e-12)
    q = p.copy()
    q.iloc[t + h + d + 1] *= 1.37
    assert SL._acumulado_hacia_adelante(q.pct_change(), h).iloc[t] == \
        pytest.approx(ade.iloc[t], rel=1e-12), (
            "la etiqueta de t se extiende más allá de t+h+d: el embargo "
            "estaría mal dimensionado")
    # El borde IZQUIERDO, que es lo que hace que el retardo sea un retardo:
    # con d=1 el precio de entrada es p[t+1], no p[t]. Perturbar el cierre
    # con el que se DECIDE no puede mover el retorno que se captura.
    q = p.copy()
    q.iloc[t] *= 1.37
    assert SL._acumulado_hacia_adelante(q.pct_change(), h).iloc[t] == \
        pytest.approx(ade.iloc[t], rel=1e-12), (
            "la etiqueta usa el cierre de t como precio de entrada: el "
            "retardo de implementación no está aplicado")
    q = p.copy()
    q.iloc[t + d] *= 1.37
    assert SL._acumulado_hacia_adelante(q.pct_change(), h).iloc[t] != \
        pytest.approx(ade.iloc[t], rel=1e-12), (
            "perturbar el precio de ENTRADA (t+d) tiene que mover la etiqueta")


# ------------------------------------------------------------
# 5. EMBARGO
# ------------------------------------------------------------
@pytest.mark.parametrize("h", SL.HORIZONTES)
def test_ninguna_etiqueta_de_ajuste_alcanza_el_periodo_de_prueba(h):
    """Se reproduce la aritmética de `corte_de_ajuste` FUERA de ella y se
    mide, en días de NEGOCIACIÓN, la separación entre el cierre de la
    ventana de etiqueta de la última fila de ajuste y el primer día del
    período de prueba. Tiene que ser >= EMBARGO_DIAS.

    Actualizado: `evaluar` ya no hace walk-forward expansivo. La auditoría
    mostró que aquella variante metía hasta el 36 % del último ajuste
    DENTRO del período de prueba mientras el reporte afirmaba que ajuste y
    prueba estaban congelados; gana el pre-registro, y ahora hay un solo
    ajuste y una sola evaluación."""
    c = _cierres()
    pos = {d: i for i, d in enumerate(c.index)}
    panel = SL.construir_paneles(c, h)["L1"]
    fechas = pd.DatetimeIndex(sorted(panel["fecha"].unique()))
    rango = c.index[(c.index >= fechas[0]) & (c.index <= fechas[-1])]
    assert len(rango.difference(fechas)) == 0, (
        "el panel se saltea días de negociación: el embargo contado en "
        "posiciones del panel no equivale al contado en días de mercado")

    corte = pd.Timestamp(SL.corte_de_ajuste(np.array(fechas), h))
    ajuste = panel[panel["fecha"] < corte]
    assert len(ajuste) >= SL.MINIMO_AJUSTE
    s_ = ajuste["fecha"].max()
    primera_prueba = fechas[fechas >= pd.Timestamp(SL.PRUEBA_DESDE)][0]
    fin_etiqueta = pos[s_] + h + SL.RETARDO_IMPLEMENTACION
    brecha = pos[primera_prueba] - fin_etiqueta
    assert brecha >= SL.EMBARGO_DIAS, (
        f"h={h}: la etiqueta de ajuste más reciente cierra sólo {brecha} "
        f"días de negociación antes del período de prueba; el embargo "
        f"declarado es {SL.EMBARGO_DIAS}")


def test_el_ajuste_no_se_mete_en_el_periodo_de_prueba(h=20):
    """La afirmación que el reporte imprime tiene que ser cierta."""
    c = _cierres()
    panel = SL.construir_paneles(c, h)["L1"]
    fechas = np.array(sorted(pd.to_datetime(panel["fecha"].unique())))
    corte = pd.Timestamp(SL.corte_de_ajuste(fechas, h))
    assert corte < pd.Timestamp(SL.PRUEBA_DESDE)
    res = SL.evaluar(panel, "L1", h)
    assert not res.empty
    assert res["fecha"].min() >= pd.Timestamp(SL.PRUEBA_DESDE)
    assert res["fecha"].max() <= pd.Timestamp(SL.PRUEBA_HASTA)
    assert res["corte_ajuste"].nunique() == 1, (
        "un solo ajuste: si hay más de un corte, volvió el walk-forward")


def test_el_embargo_declarado_es_el_de_backtest_y_se_amplia_al_horizonte():
    """El tamaño del embargo se declara, no se deduce. Si alguien lo mueve,
    este test lo obliga a mover también el pre-registro."""
    from backtest import datos as bdatos
    assert SL.EMBARGO_DIAS == getattr(bdatos, "EMBARGO_DIAS", 5) or \
        SL.EMBARGO_DIAS == 5
    assert SL.HORIZONTES == (20, 60)
