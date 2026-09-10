"""Corrida 12, bloque 2.7 — el mismo `pd.concat` del `motor_concat.diff`,
fuera de `motor.py`: `api/main.py` (correlaciones de la vista) y
`backtest/baselines.py` (z de divergencia). Los dos recibieron `sort=True`
explícito. La fixture `tests/fixtures/concat_2_7_antes.pkl` se congeló ANTES
de editar, con el código viejo (pre-mortem 16: un test «antes y después»
escrito después compara el código nuevo consigo mismo). Se compara byte a
byte (CSV) y con igualdad exacta de pandas."""
import os
import pickle
import warnings

import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(RAIZ, "tests", "fixtures", "concat_2_7_antes.pkl")


def _cargar():
    with open(FIXTURE, "rb") as f:
        return pickle.load(f)


def test_la_fixture_se_congelo_antes_y_con_el_aviso_de_pandas():
    fx = _cargar()
    assert "ANTES de editar" in fx["congelado"]
    assert fx["n_avisos_antes"] > 0, "si el código viejo no avisaba, el test no prueba nada"


def test_api_alinear_reproduce_la_salida_anterior_byte_a_byte():
    from api.main import _alinear
    fx = _cargar()
    e, salida = fx["entradas"], fx["salida"]
    with warnings.catch_warnings():
        warnings.simplefilter("error")   # ningún aviso de pandas puede quedar
        nuevo = {
            "par_k": _alinear(e["rs"], e["rk"]).dropna().tail(252),
            "par_x0": _alinear(e["rs"], e["rx"]).dropna().tail(252),
            "par_x1": _alinear(e["rs"], e["rx"].shift(1)).dropna().tail(252),
            "par_lag": _alinear(e["ret_a"].shift(5), e["ret_b"]).dropna(),
        }
    for k, v in nuevo.items():
        assert_frame_equal(v, salida[k], check_exact=True)
        assert v.to_csv() == salida[k].to_csv(), f"{k}: la salida cambió byte a byte"


def test_baselines_concat_reproduce_la_salida_anterior_byte_a_byte():
    fx = _cargar()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        nuevo = pd.concat(fx["entradas"]["zs"], axis=1, sort=True).mean(axis=1)
    assert_series_equal(nuevo, fx["salida"]["z_media"], check_exact=True)
    assert nuevo.to_csv() == fx["salida"]["z_media"].to_csv()


def test_los_sitios_nombrados_llevan_sort_explicito():
    """Los sitios que el pre-commit del 8-sep marcó con la advertencia de
    pandas: `api/main.py` (los tres `par_*` del caso destacado y el `par` de
    las correlaciones con desfase, hoy vía `_alinear`) y `backtest/baselines.py`
    (la media de z de divergencia). Los otros dos `pd.concat` de baselines
    (beta_sox por dict, cadena por niveles) NO fueron marcados por pandas y
    se dejan como están a propósito: tocarlos sin advertencia sería un cambio
    sin evidencia de que reproduce la salida."""
    src_api = open(os.path.join(RAIZ, "api", "main.py"), encoding="utf-8").read()
    assert "return pd.concat(list(series), axis=1, sort=True)" in src_api
    assert src_api.count("_alinear(") >= 5   # definición + 4 usos
    assert "pd.concat([rs, rk]" not in src_api and "pd.concat([ret_nivel" not in src_api
    src_bl = open(os.path.join(RAIZ, "backtest", "baselines.py"), encoding="utf-8").read()
    assert "pd.concat(series, axis=1, sort=True).mean(axis=1)" in src_bl
