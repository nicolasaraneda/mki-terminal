"""Corrida 09, Frente 2f — el parche PROPUESTO `GEMELO/propuestas/parches/
motor_concat.diff` hace explícito `sort=True` en los tres `pd.concat` de
`motor.py` (líneas 185, 215 y 298), que es el valor que REPRODUCE el
comportamiento actual de pandas 3.0.3 (ordena por defecto cuando todos los
índices son DatetimeIndex y avisa con `Pandas4Warning` que en pandas 4 el
default pasará a `sort=False`). DECISIONES.md §3 exige que esa preservación
se demuestre idéntica antes de tocar nada.

`motor.py` es INTOCABLE: el test copia el archivo a un directorio temporal,
aplica el diff sobre la COPIA con `patch`, la importa bajo otro nombre y
compara sus resultados con los del motor real, función por función, con
igualdad EXACTA. Además comprueba que el aviso existe en el motor real y
desaparece en la copia parcheada, y que el hash de `motor.py` no cambió.

Datos: SINTÉTICOS (sin red — el preámbulo de la corrida 09 prohíbe
descargar; `tests/test_motor.py` sí baja de Yahoo). Se parchea
`_datos_crudos` —el ÚNICO punto de acceso a precios, el mismo mecanismo de
`tests/test_motor.py`— en los dos módulos con el MISMO DataFrame. Cada
ticker pierde un 3 % de fechas propias y las acciones comparten además un
2 % de feriados en los que el SOX, los índices locales y el FX sí operan. Medido en pandas 3.0.3: el aviso
salta cuando el PRIMER índice del `concat` no contiene a los demás (si es
superconjunto, no hay nada que ordenar y no avisa), así que los feriados
compartidos son lo que garantiza que el motor real avise con estos datos
—y el test lo comprueba antes de comprobar que la copia no avisa.
"""
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import warnings
from datetime import date

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import motor  # noqa: E402
from universo import (INDICE_LOCAL_POR_EXCHANGE, PARES_FX,  # noqa: E402
                      UNIVERSO)

RUTA_MOTOR = os.path.join(RAIZ, "motor.py")
RUTA_DIFF = os.path.join(RAIZ, "GEMELO", "propuestas", "parches",
                         "motor_concat.diff")
FECHA = date(2026, 8, 3)
MENSAJE = "Sorting by default when concatenating all DatetimeIndex"
FUNCIONES = ("betas_al", "prediccion_apertura_al", "divergencias_al",
             "datos_cadena_al", "roca_chip_al")


def _sha(ruta: str) -> str:
    with open(ruta, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _datos_sinteticos() -> pd.DataFrame:
    tickers = sorted(set(list(UNIVERSO) + ["^SOX"] + list(PARES_FX)
                         + list(INDICE_LOCAL_POR_EXCHANGE.values())))
    idx = pd.bdate_range("2023-09-01", "2026-08-31")
    rng = np.random.default_rng(20260903)
    ret_sox = rng.normal(0, 0.02, len(idx))
    df = pd.DataFrame(index=idx)
    feriado_comun = rng.random(len(idx)) < 0.02   # cierran todas; el SOX no
    for t in tickers:
        if t == "^SOX":
            df[t] = 100 * np.exp(np.cumsum(ret_sox))
            continue
        beta = rng.uniform(0.3, 1.2)
        # contagio con rezago: la beta SOX(t-1)→acción(t) no es trivial
        r = beta * np.roll(ret_sox, 1) + rng.normal(0, 0.015, len(idx))
        s = pd.Series(100 * np.exp(np.cumsum(r)), index=idx)
        s[rng.random(len(idx)) < 0.03] = np.nan   # feriados propios
        if t in UNIVERSO:          # índices locales y FX sí cotizan ese día
            s[feriado_comun] = np.nan
        df[t] = s
    return df


MAESTRO = _datos_sinteticos()


def _datos_crudos_falso(tickers: tuple) -> pd.DataFrame:
    cols = [t for t in tickers if t in MAESTRO.columns]
    if not cols:
        return pd.DataFrame()
    return MAESTRO[cols].dropna(how="all").copy()


@pytest.fixture(scope="module")
def motor_parcheado(tmp_path_factory):
    sha_antes = _sha(RUTA_MOTOR)
    destino = tmp_path_factory.mktemp("parche") / "motor_parcheado.py"
    shutil.copy(RUTA_MOTOR, destino)
    r = subprocess.run(["patch", "-p1", "--forward", "--silent",
                        str(destino), RUTA_DIFF],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"el diff no aplica limpio:\n{r.stdout}\n{r.stderr}"
    assert _sha(RUTA_MOTOR) == sha_antes, "motor.py real cambió: PROHIBIDO"
    spec = importlib.util.spec_from_file_location("motor_parcheado", destino)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["motor_parcheado"] = mod
    spec.loader.exec_module(mod)
    return mod


def _con_datos_falsos(modulos, funcion):
    originales = [(m, m._datos_crudos) for m in modulos]
    for m in modulos:
        m._datos_crudos = _datos_crudos_falso
    try:
        return funcion()
    finally:
        for m, orig in originales:
            m._datos_crudos = orig


def _identico(a, b, ruta="") -> None:
    if isinstance(a, pd.DataFrame):
        assert_frame_equal(a, b, check_exact=True, obj=ruta or "DataFrame")
    elif isinstance(a, pd.Series):
        assert_series_equal(a, b, check_exact=True, obj=ruta or "Series")
    elif isinstance(a, dict):
        assert list(a.keys()) == list(b.keys()), ruta
        for k in a:
            _identico(a[k], b[k], f"{ruta}.{k}")
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b), ruta
        for i, (x, y) in enumerate(zip(a, b)):
            _identico(x, y, f"{ruta}[{i}]")
    elif isinstance(a, float):
        assert (a == b) or (np.isnan(a) and np.isnan(b)), f"{ruta}: {a} != {b}"
    else:
        assert type(a) is type(b) and a == b, f"{ruta}: {a!r} != {b!r}"


def test_el_diff_solo_agrega_sort_true_en_tres_concat(motor_parcheado):
    with open(RUTA_MOTOR, encoding="utf-8") as f:
        original = f.read().splitlines()
    with open(motor_parcheado.__file__, encoding="utf-8") as f:
        parcheado = f.read().splitlines()
    assert len(original) == len(parcheado)
    distintas = [(o, p) for o, p in zip(original, parcheado) if o != p]
    assert len(distintas) == 3
    for o, p in distintas:
        assert "pd.concat(" in o
        assert p == o.replace("axis=1)", "axis=1, sort=True)", 1)
    assert original.count("") == parcheado.count("")   # nada más se movió


def test_sort_true_es_el_comportamiento_actual_de_pandas():
    """Verificación empírica de la elección: hoy pandas ORDENA por defecto
    dos DatetimeIndex desordenados y distintos; `sort=True` lo reproduce,
    `sort=False` no."""
    a = pd.Series([1, 2, 3], index=pd.to_datetime(
        ["2024-01-03", "2024-01-01", "2024-01-02"]), name="a")
    b = pd.Series([4, 5], index=pd.to_datetime(
        ["2024-01-02", "2024-01-04"]), name="b")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hoy = pd.concat([a, b], axis=1)
    assert hoy.equals(pd.concat([a, b], axis=1, sort=True))
    assert not hoy.equals(pd.concat([a, b], axis=1, sort=False))


@pytest.mark.parametrize("nombre", FUNCIONES)
def test_resultados_identicos_entre_motor_real_y_copia_parcheada(
        motor_parcheado, nombre):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        real = _con_datos_falsos([motor], lambda: getattr(motor, nombre)(FECHA))
        copia = _con_datos_falsos([motor_parcheado],
                                  lambda: getattr(motor_parcheado, nombre)(FECHA))
    # la comparación tiene que ser sobre resultados NO triviales
    if isinstance(real, pd.DataFrame):
        assert not real.empty and len(real) >= 5
    elif isinstance(real, list):
        assert len(real) >= 3
    elif isinstance(real, dict) and "series_nivel" in real:
        assert len(real["series_nivel"]) >= 3
    else:
        assert real is not None and 0 <= real["valor"] <= 100
    _identico(real, copia, nombre)


def _avisos_de(modulo, nombre):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _con_datos_falsos([modulo], lambda: getattr(modulo, nombre)(FECHA))
    return [x for x in w if MENSAJE in str(x.message)
            and os.path.basename(x.filename) == os.path.basename(modulo.__file__)]


@pytest.mark.parametrize("nombre", ("betas_al", "divergencias_al"))
def test_el_aviso_existe_en_el_motor_real_y_desaparece_en_la_copia(
        motor_parcheado, nombre):
    """Contraprueba primero: el motor real SÍ emite el Pandas4Warning con los
    datos sintéticos (si no, el test no probaría nada). Luego: la copia
    parcheada no lo emite."""
    assert len(_avisos_de(motor, nombre)) >= 1
    assert _avisos_de(motor_parcheado, nombre) == []


def test_motor_real_sigue_intacto(motor_parcheado):
    r = subprocess.run(["git", "diff", "--quiet", "--", "motor.py"],
                       cwd=RAIZ, capture_output=True)
    assert r.returncode == 0, "motor.py tiene cambios en el árbol"
