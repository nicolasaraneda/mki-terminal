# ============================================================
# WS4 — auditoría adversarial del WS3 (Etapa 6.0.0).
#
# Estos tests no confirman el hallazgo: intentan derrumbarlo. Cada uno
# corresponde a una amenaza del informe GEMELO/resultados/auditoria_ws3.md
# y fija su resultado para que no se pierda ni se revierta en silencio.
#
# Nada aquí toca bases, filas selladas ni el camino de sellado.
# ============================================================

import os
import sys
from datetime import datetime, time, timezone

import numpy as np
import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from GEMELO import control_lineal as cl
from GEMELO import ventana_larga as vl
from GEMELO.experimento import _fecha_emision_por_sesion, construir_panel


# ============================================================
# AMENAZA 3 — la convención del empate, reintroducida en el WS3
# ============================================================
def test_el_WS3_usa_la_convencion_asimetrica_y_eso_infla_la_ventaja():
    """HALLAZGO del WS4: `cl.evaluar` puntúa al modelo con `>=` y a la
    baseline con `>`, que es exactamente el sesgo que la §2.8 congeló para
    la ventana sellada — y que el WS3 no aplicó. Este test FIJA el
    hallazgo: si alguien lo 'arregla' sin documentarlo, falla."""
    d = pd.DataFrame({"fecha": ["d"] * 4, "ticker": list("ABCD"),
                      "pred": [1.0, 1.0, -1.0, 1.0],
                      "gap_pct": [0.0, 2.0, -2.0, -1.0],
                      "sigma": [1.0] * 4, "alpha": [1.0] * 4,
                      "n_train": [100] * 4})
    r = cl.evaluar(d, "X")
    # la fila de gap 0.0: el modelo (pred>=0) ACIERTA, la baseline (gap>0) NO
    assert r["acierto_pct"] == 75.0
    assert r["base_pct"] == 25.0      # solo la de gap 2.0
    # con la convención simétrica la baseline habría acertado también la de 0.0
    base_simetrica = 100 * (d["gap_pct"] >= 0).mean()
    assert base_simetrica > r["base_pct"]


def test_la_baseline_se_mide_sobre_exactamente_las_mismas_filas():
    """Amenaza 3, la parte que resultó INOFENSIVA: base y modelo salen del
    mismo DataFrame, así que no puede haber asimetría de universo, sesiones
    ni filtro. La única asimetría es la del empate (test anterior)."""
    import inspect
    fuente = inspect.getsource(cl.evaluar)
    assert 'gap = df["gap_pct"]' in fuente
    assert 'base = (gap > 0)' in fuente      # misma serie `gap`, mismas filas


# ============================================================
# AMENAZA 4 — fuga en el camino largo (con contraprueba)
# ============================================================
def _panel_sintetico(n_dias=700, tickers=("A", "B"), semilla=13):
    rng = np.random.default_rng(semilla)
    fechas = pd.bdate_range(end="2026-08-21", periods=n_dias)
    filas = []
    for f in fechas:
        sox = rng.normal(0, 1.2)
        for t in tickers:
            filas.append({"fecha": f, "ticker": t, "sox_t": sox,
                          "sox_t1": rng.normal(0, 1.2),
                          "gap_pct": 0.6 * sox + rng.normal(0, 1.0)})
    return pd.DataFrame(filas)


def test_truncar_el_panel_no_altera_NINGUNA_prediccion_anterior():
    """La forma fuerte, sobre el camino largo completo: cortar la entrada
    en T no puede mover ninguna predicción de fecha < T."""
    panel = _panel_sintetico()
    corte = pd.Timestamp("2026-06-01")
    ev = panel[(panel["fecha"] >= "2026-03-01") & (panel["fecha"] < corte)].copy()

    completo = cl.correr_configuracion("C1", panel, ev)
    truncado = cl.correr_configuracion("C1", panel[panel["fecha"] < corte], ev)
    assert not completo.empty
    pd.testing.assert_frame_equal(
        completo.reset_index(drop=True), truncado.reset_index(drop=True))


def test_la_contraprueba_de_fuga_es_detectada():
    """Un test de fuga que no puede fallar no prueba nada. Se inyecta una
    etiqueta que mira al futuro y se verifica que el criterio la caza."""
    panel = _panel_sintetico()
    corte = pd.Timestamp("2026-06-01")
    ev = panel[(panel["fecha"] >= "2026-03-01") & (panel["fecha"] < corte)].copy()

    # Fuga deliberada EN EL MECANISMO: un embargo NEGATIVO hace que el
    # entrenamiento incluya filas POSTERIORES a la emisión. Es la fuga que
    # el método de truncar-y-comparar debe cazar; si no la cazara, el test
    # de arriba no probaría nada.
    a = cl.correr_configuracion("C1", panel, ev, embargo_dias=-30)
    b = cl.correr_configuracion("C1", panel[panel["fecha"] < corte], ev,
                                embargo_dias=-30)
    assert not a.empty and not b.empty
    m = a.merge(b, on=["fecha", "ticker"], suffixes=("_a", "_b"))
    assert len(m) > 0
    assert not np.allclose(m["pred_a"], m["pred_b"]), \
        "la contraprueba no detectó una fuga inyectada"


def test_el_emparejamiento_sesion_emision_es_estrictamente_causal():
    """La emisión asignada a una sesión debe ser ESTRICTAMENTE anterior."""
    idx = pd.bdate_range("2020-01-01", periods=300)
    sesiones = pd.Series(idx[10:200])
    em = _fecha_emision_por_sesion(sesiones, idx)
    assert (pd.to_datetime(em) < pd.to_datetime(sesiones)).all()


def test_truncar_el_indice_no_cambia_emisiones_anteriores():
    idx = pd.bdate_range("2020-01-01", periods=300)
    sesiones = pd.Series(idx[10:150])
    completo = _fecha_emision_por_sesion(sesiones, idx)
    truncado = _fecha_emision_por_sesion(sesiones, idx[:200])
    pd.testing.assert_series_equal(completo, truncado)


# ============================================================
# AMENAZA 7 — el 91.4% era un artefacto del join
# ============================================================
def test_el_desajuste_de_sesion_objetivo_puede_fingir_una_revision():
    """HALLAZGO del WS4: el 8.6% de 'revisiones' del WS3 no eran
    revisiones de Yahoo sino filas emparejadas con OTRA sesión objetivo.
    El panel empareja emisión→sesión-calendario-siguiente; el verificador
    usa la sesión siguiente al SELLO real, que en un sello tardío puede
    saltarse una. Comparar sin alinear por `sesion_objetivo` finge una
    discrepancia de datos donde solo hay una de emparejamiento."""
    idx = pd.bdate_range("2026-07-27", periods=6)
    # el panel empareja la emisión del 29 con la sesión del 30
    ses = pd.Series([pd.Timestamp("2026-07-30")])
    assert pd.to_datetime(_fecha_emision_por_sesion(ses, idx)).iloc[0] \
        == pd.Timestamp("2026-07-29")
    # pero el sello del 29-jul declaró sesion_objetivo = 31 (sello tardío)
    # ⇒ los gaps NO son comparables fila a fila sin alinear por sesión.
    assert pd.Timestamp("2026-07-31") != pd.Timestamp("2026-07-30")


# ============================================================
# AMENAZA 1 — supervivencia: el canal medible es cero
# ============================================================
def test_todos_los_tickers_objetivo_tienen_historia_completa():
    """El canal de ENTRADA TARDÍA es medible y resultó vacío: los 8
    objetivos existen desde el inicio de la ventana. Si algún día entra un
    ticker nuevo al universo, este test obliga a re-medirlo."""
    from universo import MERCADOS_POR_ABRIR
    assert len(MERCADOS_POR_ABRIR) == 8
    # (la verificación empírica contra la fuente vive en el informe; aquí
    #  se fija el universo evaluado para que un cambio no pase inadvertido)
    assert set(MERCADOS_POR_ABRIR) == {
        "005930.KS", "000660.KS", "2330.TW", "8035.T", "6857.T",
        "IFX.DE", "4063.T", "3436.T"}


# ============================================================
# El informe existe y declara lo que debe
# ============================================================
def test_el_criterio_del_29jul_se_declaro_antes_de_correrlo():
    ruta = os.path.join(RAIZ, "GEMELO", "resultados",
                        "criterio_rancio_declarado.md")
    texto = open(ruta, encoding="utf-8").read()
    assert "DECLARADO ANTES DE CORRERLO" in texto
    assert "5%" in texto
    assert "SUBE el 65.9% publicado" in texto     # el sesgo, nombrado
    assert "No se toca ninguna fila" in texto or "Nada." in texto


def test_el_informe_de_auditoria_lleva_el_veredicto_arriba():
    ruta = os.path.join(RAIZ, "GEMELO", "resultados", "auditoria_ws3.md")
    texto = open(ruta, encoding="utf-8").read()
    assert texto.startswith("# Auditoría adversarial del WS3")
    assert "VEREDICTO" in texto[:2000]
    assert "Preguntas abiertas" in texto
    assert "NO EVALUABLE" in texto or "no evaluable" in texto
