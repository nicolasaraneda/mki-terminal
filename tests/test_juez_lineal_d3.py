"""El juez lineal bajo D3 (corrida 09) no puede descargar: la guarda tiene test."""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)


def test_prohibir_descarga_inutiliza_yfinance_y_acepta_cache_sin_ttl(tmp_path):
    from GEMELO import datos
    from GEMELO import juez_lineal_d3 as j
    original = datos.yf.download
    try:
        j._prohibir_descarga()
        with pytest.raises(RuntimeError, match="descarga prohibida"):
            datos.yf.download(["^SOX"], period="1y")
        ruta = tmp_path / "x.csv"
        ruta.write_text("a\n")
        assert datos._cache_vigente(str(ruta), ttl_horas=0) is True
        assert datos._cache_vigente(str(tmp_path / "no.csv"), ttl_horas=1e9) is False
    finally:
        datos.yf.download = original


def test_el_preregistro_declara_la_enmienda_antes_de_correr():
    texto = open(os.path.join(RAIZ, "GEMELO", "preregistro", "juez_lineal_d3.md"), encoding="utf-8").read()
    assert "Enmienda 1" in texto and "ANTES de la primera corrida" in texto
    assert "36" in texto  # intentos declarados
