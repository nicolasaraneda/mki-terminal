"""Contrapruebas del simulador del instrumento del riel de dinero
(`GEMELO/simulador/instrumento_dinero.py`, bloque 1 de la corrida 11).

Sin red: los precios entran del congelado sólo para la σ, y acá la σ se
pasa a mano. Réplicas chicas a propósito: esto prueba que el instrumento
puede FALLAR la prueba y que la prueba lo mide, no el resultado publicado.
"""
import ast
import os

import numpy as np
import pytest

from GEMELO.simulador import instrumento_dinero as I

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = np.array([0.5, -1.0, 2.0, 0.0, -0.5, 1.5, -2.0, 0.8] * 10)


def test_no_importa_el_camino_de_sellado():
    ruta = os.path.join(RAIZ, "GEMELO", "simulador", "instrumento_dinero.py")
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres |= {a.name.split(".")[0] for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module.split(".")[0])
    assert not nombres & {"snapshot", "senales", "alertas", "motor", "noticias", "app"}


def test_las_magnitudes_declaradas_son_las_del_preregistro():
    assert I.DELTAS_PP_SEMANA == (0.0, 0.25, 0.50, 1.00)
    assert 52 in I.HORIZONTES_SEMANAS


def test_la_deteccion_crece_con_la_ventaja_y_es_rara_bajo_la_nula():
    tasas = [I.simular_celda(d, 2.5, 0.0, 52, BASE, n_rep=60, semilla=3)["deteccion"]["tasa"]
             for d in (0.0, 1.0, 3.0)]
    assert tasas[0] <= 0.2          # bajo la nula, casi nunca
    assert tasas[2] >= 0.9          # con 3 pp/semana sobre σ 2,5, casi siempre
    assert tasas[0] < tasas[1] < tasas[2]


def test_el_wilson_va_en_proporcion_y_contiene_la_tasa():
    c = I.simular_celda(0.5, 2.5, 0.0, 52, BASE, n_rep=40, semilla=4)
    lo, hi = c["deteccion"]["wilson95"]
    assert 0.0 <= lo <= c["deteccion"]["tasa"] <= hi <= 1.0
    assert c["cobertura_ic95"]["wilson95"][1] <= 1.0


def test_el_veredicto_puede_ser_no_discrimina():
    """Contraprueba: con σ enorme frente a las magnitudes, ninguna celda
    separa su piso del techo de la nula, y el veredicto tiene que decirlo."""
    celdas = []
    for T in (52,):
        for d in I.DELTAS_PP_SEMANA:
            c = I.simular_celda(d, 200.0, 0.0, T, BASE, n_rep=40, semilla=5)
            c["grupo"] = "base"
            celdas.append(c)
    v = I.veredicto(celdas)
    assert v["instrumento_discrimina"] is False
    assert "SUSPENDIDO" in v["consecuencia"]


def test_la_serie_de_la_base_no_cambia_el_estadistico():
    """`comparar` resta retornos semanales: la base entra y sale."""
    a = I.simular_celda(0.5, 2.5, 0.0, 52, BASE, n_rep=25, semilla=6)
    b = I.simular_celda(0.5, 2.5, 0.0, 52, BASE * 3.0, n_rep=25, semilla=6)
    assert a["punto_medio_pp"] == pytest.approx(b["punto_medio_pp"], abs=1e-6)
    assert a["deteccion"]["k"] == b["deteccion"]["k"]


def test_reproducible_con_semilla():
    a = I.simular_celda(0.25, 2.5, 0.2, 52, BASE, n_rep=20, semilla=8)
    b = I.simular_celda(0.25, 2.5, 0.2, 52, BASE, n_rep=20, semilla=8)
    assert a == b
