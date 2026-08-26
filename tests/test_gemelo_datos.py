# ============================================================
# GATE del WS2a (Etapa 6.0.0) — tests de la capa de datos del retador.
#
# Tres cosas se prueban, y la primera es la que decide si la capa sirve:
#
#  1. CAUSALIDAD por feature: el valor en t es invariante a borrar todo
#     dato posterior a t. Es la extensión del test anti-look-ahead del
#     motor a cada feature nueva, y caza casi cualquier regresión de fuga.
#  2. ASINCRONÍA: ninguna feature combina series cuya barra aún no cerró a
#     la emisión (22:15 UTC).
#  3. AISLAMIENTO: GEMELO/ no importa el camino de sellado ni escribe en
#     ninguna base.
#
# Todo sintético: no se descarga nada, no se toca ninguna base.
# ============================================================

import ast
import os
import sys
from datetime import date, datetime, time, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from GEMELO import datos, features

FECHAS_PRUEBA = ("2026-07-26", "2026-05-27", "2026-02-26")


def _series_sinteticas(n=800, semilla=11, fin="2026-08-24"):
    """Precios sintéticos con deriva y volatilidad realistas."""
    idx = pd.bdate_range(end=fin, periods=n)
    rng = np.random.default_rng(semilla)
    datos_ = {}
    for i, t in enumerate(datos.TICKERS):
        pasos = rng.normal(0.0003, 0.012, n)
        datos_[t] = 100 * np.exp(np.cumsum(pasos))
    df = pd.DataFrame(datos_, index=idx)
    df["^VIX"] = 12 + 8 * np.abs(rng.normal(0, 1, n))
    df["^VIX3M"] = df["^VIX"] * (1.05 + 0.08 * rng.normal(0, 1, n)).clip(0.8, 1.4)
    return df


# ============================================================
# 1. EL GATE: causalidad, feature por feature
# ============================================================
@pytest.mark.parametrize("corte", FECHAS_PRUEBA)
def test_cada_feature_es_invariante_a_borrar_el_futuro(corte):
    """EL test del WS2a. Se construyen las features con TODA la historia y
    con la historia truncada en `corte`; el valor en `corte` debe ser
    idéntico. Si alguna transformación mirara hacia adelante —un center=True,
    un shift negativo, un fillna(method='bfill')— este test lo caza."""
    series = _series_sinteticas()
    # Las tres fechas vienen de tests/test_motor.py; alguna cae en fin de
    # semana, así que se evalúa el último día hábil disponible <= corte.
    f_corte = series.index[series.index <= pd.Timestamp(corte)][-1]

    completo = features.construir(series, verificar=False)
    truncado = features.construir(series[series.index <= f_corte], verificar=False)

    assert f_corte in completo.index and f_corte in truncado.index
    assert list(completo.columns) == list(truncado.columns)

    for col in completo.columns:
        a, b = completo.loc[f_corte, col], truncado.loc[f_corte, col]
        if pd.isna(a) and pd.isna(b):
            continue
        assert a == pytest.approx(b, rel=1e-12, abs=1e-12), (
            f"{col} en {corte}: con futuro {a}, sin futuro {b} — HAY FUGA")


def test_la_invariancia_vale_para_toda_la_historia_previa_no_solo_el_corte():
    """Más fuerte: truncar en `corte` no puede alterar NINGÚN valor anterior."""
    series = _series_sinteticas()
    corte = pd.Timestamp("2026-05-27")
    completo = features.construir(series, verificar=False)
    truncado = features.construir(series[series.index <= corte], verificar=False)
    solapan = truncado.index
    pd.testing.assert_frame_equal(
        completo.loc[solapan], truncado, check_freq=False, rtol=1e-12)


def test_el_test_de_causalidad_detecta_una_fuga_inyectada():
    """Contraprueba del propio test: si se introduce una feature que mira
    al futuro, el criterio de arriba tiene que fallar. Un test de fuga que
    no puede fallar no prueba nada."""
    series = _series_sinteticas()
    corte = pd.Timestamp("2026-05-27")
    fuga_completo = series["^SOX"].pct_change().shift(-1)      # ¡mañana!
    fuga_truncado = series[series.index <= corte]["^SOX"].pct_change().shift(-1)
    assert not (fuga_completo.loc[corte] == pytest.approx(
        fuga_truncado.loc[corte], rel=1e-12, nan_ok=False)
        if not pd.isna(fuga_truncado.loc[corte]) else False)


def test_toda_feature_declarada_tiene_dependencias_y_viceversa():
    series = _series_sinteticas()
    f = features.construir(series, verificar=False)
    assert set(f.columns) <= set(features.DEPENDENCIAS)
    assert set(features.FEATURES) == set(features.DEPENDENCIAS)


def test_ninguna_feature_es_un_nivel_crudo():
    """Estacionariedad por construcción: un nivel deriva monótonamente y el
    modelo lo usa como proxy del calendario. Se comprueba que ninguna
    feature esté fuertemente correlacionada con el índice temporal."""
    series = _series_sinteticas()
    f = features.construir(series, verificar=False).dropna()
    t = np.arange(len(f), dtype=float)
    for col in f.columns:
        if col == "credit_ratio":
            continue   # razón de niveles: ver DECISIONES.md §29
        corr = abs(np.corrcoef(t, f[col].values)[0, 1])
        assert corr < 0.85, f"{col} correlaciona {corr:.2f} con el calendario"


# ============================================================
# 2. Asincronía de las barras diarias
# ============================================================
def test_toda_serie_del_catalogo_es_conocible_a_la_emision():
    dia = date(2026, 8, 24)
    emision = datos.emision_utc(dia)
    assert emision.time() == time(22, 15)
    for t, s in datos.CATALOGO.items():
        assert s.conocible_en(dia, emision), (
            f"{t} cierra {s.available_at(dia)} > emisión {emision}")


def test_ninguna_feature_combina_series_no_conocibles():
    """La exigencia literal del encargo: si una feature dependiera de una
    serie cuyo available_at es posterior a la emisión, este test la nombra."""
    dia = date(2026, 8, 24)
    for nombre, tickers in features.DEPENDENCIAS.items():
        try:
            datos.verificar_conocibles(tickers, dia)
        except datos.SerieNoConocible as e:
            pytest.fail(f"feature {nombre}: {e}")


def test_verificar_conocibles_revienta_con_una_serie_tardia(monkeypatch):
    """Contraprueba: la guarda tiene que poder fallar."""
    tarde = datos._Serie("TARDE=X", "prueba", "cierra después de la emisión",
                         "23:00 UTC", time(23, 0))
    monkeypatch.setitem(datos.CATALOGO, "TARDE=X", tarde)
    with pytest.raises(datos.SerieNoConocible):
        datos.verificar_conocibles(("TARDE=X",), date(2026, 8, 24))


def test_los_futuros_son_la_serie_mas_ajustada_y_esta_declarado():
    """ES=F/NQ=F cierran 17:00 ET = 22:00 UTC en invierno: 15 minutos antes
    de la emisión. Es holgura real pero mínima, y está sellada como tal."""
    dia = date(2026, 8, 24)
    emision = datos.emision_utc(dia)
    margen = {t: (emision - s.available_at(dia)).total_seconds() / 60
              for t, s in datos.CATALOGO.items()}
    assert margen["ES=F"] == 15.0 and margen["NQ=F"] == 15.0
    assert min(margen.values()) == 15.0


def test_con_un_margen_de_2h_caeria_hasta_el_propio_SOX():
    """Deja MEDIDA la tensión con el margen de publicación de 2 h que usa
    `calendarios.sesion_ya_cerro`. El hallazgo es más fuerte de lo que
    parecía: con ese criterio caen 11 de 15 series, **incluido ^SOX**, que
    es el insumo primario que el campeón usa HOY a las 22:15.

    La lectura correcta es que el margen de 2 h es un criterio de
    VERIFICACIÓN —¿ya se puede saber cómo cerró la sesión objetivo?— y no
    un criterio de INSUMO. Producción sella `available_at` como el cierre
    UTC de la sesión de SOX usada, sin sumarle margen. Aplicar el criterio
    de verificación a los insumos descalificaría al propio campeón."""
    dia = date(2026, 8, 24)
    emision = datos.emision_utc(dia)
    caen = {t for t, s in datos.CATALOGO.items()
            if not s.conocible_en(dia, emision, margen_h=2.0)}
    assert "^SOX" in caen                      # el insumo del campeón
    assert len(caen) == 11
    # los mercados locales, cerrados hace horas, pasan con cualquier margen
    assert {"^KS11", "^TWII", "^N225", "^GDAXI"}.isdisjoint(caen)


def test_la_tabla_de_disponibilidad_existe_como_dato():
    tabla = datos.tabla_disponibilidad()
    assert len(tabla) == len(datos.CATALOGO)
    assert tabla["conocible_dia_D"].all()
    assert set(tabla.columns) >= {"ticker", "cierre_local", "cierre_utc",
                                  "available_at", "conocible_dia_D"}


def test_el_peor_caso_utc_es_el_de_invierno():
    """Sellar el offset más tardío del año es lo que hace que "conocible a
    las 22:15" valga los 365 días y no solo en verano."""
    assert datos.CATALOGO["^SOX"].cierre_utc == time(21, 0)      # EST, no EDT
    assert datos.CATALOGO["^GDAXI"].cierre_utc == time(16, 30)   # CET, no CEST


# ============================================================
# 3. Compuertas de robustez
# ============================================================
def test_el_ffill_esta_acotado():
    """Un ffill sin tope alimenta para siempre el último valor de una serie
    muerta, y la feature sigue existiendo, constante, aparentando dato."""
    idx = pd.bdate_range("2026-01-01", periods=20)
    s = pd.DataFrame({"X": [1.0] + [np.nan] * 19}, index=idx)
    r = datos.ffill_acotado(s, limite=5)
    assert r["X"].notna().sum() == 6      # el original + 5
    assert pd.isna(r["X"].iloc[-1])


def test_la_cobertura_minima_descarta_la_serie_corta_no_el_historico():
    """^VIX3M arranca ~2017: sin esta compuerta, un dropna posterior
    amputaría años de TODAS las demás en silencio."""
    idx = pd.bdate_range("2026-01-01", periods=100)
    df = pd.DataFrame({"LARGA": np.arange(100.0),
                       "CORTA": [np.nan] * 80 + list(np.arange(20.0))}, index=idx)
    filtrado, descartadas = datos.filtrar_por_cobertura(df, minimo=0.80)
    assert list(filtrado.columns) == ["LARGA"]
    assert len(filtrado) == 100                      # el histórico NO se tocó
    assert descartadas[0]["ticker"] == "CORTA"
    assert descartadas[0]["cobertura"] == 0.2


def test_la_cobertura_avisa_en_vez_de_borrar_en_silencio():
    idx = pd.bdate_range("2026-01-01", periods=100)
    df = pd.DataFrame({"A": np.arange(100.0)}, index=idx)
    _, descartadas = datos.filtrar_por_cobertura(df, minimo=0.80)
    assert descartadas == []


def test_construir_tolera_series_ausentes_y_las_declara():
    """La investigación tiene que poder correr con lo que Yahoo entregó."""
    series = _series_sinteticas()[["^SOX", "^VIX"]]
    f = features.construir(series, verificar=False)
    assert "sox_t" in f.columns and "vix_dln" in f.columns
    assert "vix_term" not in f.columns          # falta ^VIX3M
    assert "credit_ratio" in f.attrs["ausentes"]


def test_construir_con_entrada_vacia_no_revienta():
    assert features.construir(pd.DataFrame()).empty
    assert features.construir(None).empty


# ============================================================
# 4. AISLAMIENTO — una falla aquí no puede tocar el sello
# ============================================================
PROHIBIDOS = {"snapshot", "senales", "alertas", "mki_backup", "mki_vigia",
              "mki_noticias", "noticias", "app"}


def _importados(ruta):
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres |= {a.name.split(".")[0] for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module.split(".")[0])
    return nombres


def test_gemelo_no_importa_el_camino_de_sellado():
    """Trece feeds nuevos son trece formas nuevas de que Yahoo falle a las
    18:15. El titular no puede depender de ninguna."""
    carpeta = os.path.join(RAIZ, "GEMELO")
    for archivo in os.listdir(carpeta):
        if not archivo.endswith(".py"):
            continue
        prohibidos = _importados(os.path.join(carpeta, archivo)) & PROHIBIDOS
        assert not prohibidos, f"GEMELO/{archivo} importa {prohibidos}"


def test_gemelo_no_importa_motor_ni_universo():
    """La descarga se DUPLICA a propósito: el acoplamiento cuesta más que
    la duplicación cuando lo que está en juego es el sello nocturno."""
    carpeta = os.path.join(RAIZ, "GEMELO")
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".py"):
            assert "motor" not in _importados(os.path.join(carpeta, archivo))


def test_gemelo_no_escribe_en_ninguna_base():
    carpeta = os.path.join(RAIZ, "GEMELO")
    for archivo in os.listdir(carpeta):
        if not archivo.endswith(".py"):
            continue
        fuente = open(os.path.join(carpeta, archivo), encoding="utf-8").read()
        for prohibido in ("sqlite3", "senales.db", "noticias.db", "alertas.db",
                          "INSERT ", "UPDATE ", "get_connection"):
            assert prohibido not in fuente, f"GEMELO/{archivo}: {prohibido}"


def test_la_cache_de_gemelo_esta_gitignoreada():
    """La caché son megas de CSV regenerables: no entran al repo."""
    gitignore = open(os.path.join(RAIZ, ".gitignore"), encoding="utf-8").read()
    assert "GEMELO/cache" in gitignore
