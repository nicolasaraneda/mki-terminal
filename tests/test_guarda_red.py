# ============================================================
# tests/test_guarda_red.py — la guarda de la ventana de sellado.
#
# Deuda de la corrida 09 (encargo 10 §2). Dos piezas independientes:
#
#   A. scripts/guarda_red.sh — decide si el instante está dentro de la
#      ventana 17:50–20:30 de Chile en día hábil. Se prueba con RELOJ FALSO
#      (MKI_AHORA_PRUEBA), que es la única forma de probar una regla
#      horaria sin esperar a que sean las 17:50 de un jueves.
#
#   B. tests/conftest.py — el marcador `red`: un test que abre conexiones
#      salientes y no lo declara, falla. Se prueba corriendo un pytest
#      ANIDADO en un directorio temporal, con una copia del conftest: es la
#      única manera de observar el fallo de un test sin que ese fallo sea
#      el de esta misma corrida.
# ============================================================
import os
import shutil
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUARDA = os.path.join(RAIZ, "scripts", "guarda_red.sh")
CONFTEST = os.path.join(RAIZ, "tests", "conftest.py")


def _guarda(instante: str) -> bool:
    """True si la guarda dice DENTRO de la ventana."""
    entorno = dict(os.environ, MKI_AHORA_PRUEBA=instante)
    r = subprocess.run(["bash", GUARDA], env=entorno)
    return r.returncode == 0


# ------------------------------------------------------------
# A. la ventana
# ------------------------------------------------------------
# 2026-09-03 fue JUEVES: es el día en que el hook corrió la suite a las
# 17:57 y cruzó la regla. 09-05 fue sábado y 09-06 domingo.
DENTRO = [
    ("2026-09-03T17:57", "el caso real que originó la regla"),
    ("2026-09-03T17:50", "el borde inicial es parte de la ventana"),
    ("2026-09-03T20:30", "el borde final también"),
    ("2026-09-03T18:15", "la hora del snapshot"),
    ("2026-09-07T19:00", "lunes, la hora del vigía"),
]
FUERA = [
    ("2026-09-03T17:49", "un minuto antes"),
    ("2026-09-03T20:31", "un minuto después"),
    ("2026-09-03T09:00", "la mañana"),
    ("2026-09-05T18:15", "sábado: no hay sello que proteger"),
    ("2026-09-06T18:15", "domingo"),
]


@pytest.mark.parametrize("instante,motivo", DENTRO)
def test_la_guarda_dispara_dentro_de_la_ventana(instante, motivo):
    assert _guarda(instante), f"debería disparar ({motivo}): {instante}"


@pytest.mark.parametrize("instante,motivo", FUERA)
def test_la_guarda_no_dispara_fuera_de_la_ventana(instante, motivo):
    assert not _guarda(instante), f"NO debería disparar ({motivo}): {instante}"


def test_sin_reloj_falso_la_guarda_igual_responde():
    """Sin MKI_AHORA_PRUEBA lee el reloj real. No se afirma qué contesta
    —depende de cuándo corra la suite—, sí que contesta 0 o 1 y no revienta."""
    entorno = {k: v for k, v in os.environ.items() if k != "MKI_AHORA_PRUEBA"}
    r = subprocess.run(["bash", GUARDA], env=entorno,
                       capture_output=True, text=True)
    assert r.returncode in (0, 1), r.stderr
    assert r.stdout == "" and r.stderr == "", "la guarda no imprime: decide"


def test_el_hook_consulta_la_guarda_y_nombra_la_regla():
    """La corrección va al ejecutable: el hook tiene que USAR la guarda."""
    hook = open(os.path.join(RAIZ, "scripts", "pre-commit"),
                encoding="utf-8").read()
    assert "guarda_red.sh" in hook
    assert 'pytest tests/ -q -m "not red"' in hook, (
        "dentro de la ventana los tests de red no se corren")
    assert "VENTANA DE SELLADO" in hook, "el mensaje debe nombrar la regla"
    assert "PARCIAL" in hook, (
        "una suite recortada no puede anunciarse como verde")


def test_mki_tests_aplica_la_misma_regla_que_el_hook():
    """`./mki tests` es la puerta humana a la misma suite. Si la regla
    valiera sólo en el hook, bastaría correr los tests a mano para
    cruzarla."""
    mki = open(os.path.join(RAIZ, "mki"), encoding="utf-8").read()
    assert "guarda_red.sh" in mki
    assert 'MKI_EN_VENTANA' in mki
    assert 'pytest tests/ -q -m "not red"' in mki


# ------------------------------------------------------------
# B. el marcador `red`
# ------------------------------------------------------------
_ANIDADO = '''
import conftest
import pytest


def test_sin_marcador_tocando_la_red():
    conftest._anotar(("query1.finance.yahoo.com", 443))


@pytest.mark.red
def test_con_marcador_tocando_la_red():
    conftest._anotar(("query1.finance.yahoo.com", 443))


def test_sin_marcador_y_solo_local():
    conftest._anotar(("127.0.0.1", 8000))
'''


def _pytest_anidado(tmp_path, extra=()):
    shutil.copy(CONFTEST, tmp_path / "conftest.py")
    (tmp_path / "test_anidado.py").write_text(_ANIDADO, encoding="utf-8")
    entorno = {k: v for k, v in os.environ.items()
               if k not in ("MKI_RED_LIBRE", "MKI_RED_INFORME")}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         str(tmp_path), *extra],
        capture_output=True, text=True, env=entorno, cwd=str(tmp_path))


def test_un_test_que_toca_la_red_sin_marcador_falla(tmp_path):
    """El veredicto llega en el teardown —que es donde ya se sabe si el
    test tocó la red—, así que pytest lo rotula ERROR y no FAILED. Da igual
    para lo que importa: la corrida no queda verde y el mensaje nombra la
    regla. Se comprueba con el rótulo real, no con el que uno esperaría."""
    r = _pytest_anidado(tmp_path)
    assert "test_sin_marcador_tocando_la_red" in r.stdout
    assert r.returncode != 0, "la corrida anidada tiene que quedar roja"
    assert "1 error" in r.stdout, r.stdout[-2000:]
    assert "3 passed" in r.stdout, (
        "los otros dos pasan; el sin-marcador pasa y revienta en el teardown")
    assert "pytest.mark.red" in r.stdout
    assert "ventana de sellado" in r.stdout


def test_dentro_de_la_ventana_el_test_de_red_ni_se_colecta(tmp_path):
    """Lo que el hook corre en la ventana: -m 'not red'. El test marcado
    queda deseleccionado, que es el punto entero de marcarlo."""
    r = _pytest_anidado(tmp_path, extra=["-m", "not red"])
    assert "1 deselected" in r.stdout, r.stdout[-2000:]
    assert "test_con_marcador_tocando_la_red" not in r.stdout


def test_el_marcador_esta_registrado():
    """Sin registrar, `-m red` es un typo silencioso en vez de un filtro."""
    conftest = open(CONFTEST, encoding="utf-8").read()
    assert 'addinivalue_line(' in conftest and '"markers"' in conftest
