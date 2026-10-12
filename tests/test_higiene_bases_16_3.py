"""Corrida 16-3, Bloque D (R5 del dictamen 16-1 y hecho de entorno (ii) de la
tarjeta §80; acta §102.2): la higiene de la suite frente a las bases.

(1) `hay_filas` (tests/bases_de_prueba.py) distingue base ausente, archivo
    vacío, base sin la tabla y tabla con filas, y no crea nada.
(2) Los cinco marcadores `solo_con_base` preguntan por la tabla con filas, no
    por el archivo (R5).
(3) La guarda de `tests/conftest.py` ve una base que un test creó en la raíz
    y calla si ya existía (contraprueba del detector); y `tests/test_api.py`,
    el único creador medido, declara su fixture de bases temporales."""
import importlib
import os
import re
import sqlite3
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from bases_de_prueba import hay_filas, razon_sin_base  # noqa: E402

ARCHIVOS_CON_MARCADOR = {
    "test_linea_base.py": "verificacion_apertura",
    "test_conocibilidad.py": "verificacion_apertura",
    "test_frescura.py": "snapshots",
    "test_guarda_puntaje.py": "senales_ticker",
    "test_bifurcaciones.py": "verificacion_apertura",
    "test_banco_clausulas.py": "verificacion_apertura",
}


# ------------------------------------------------------------
# (1) hay_filas
# ------------------------------------------------------------
def test_hay_filas_distingue_ausente_vacia_sin_tabla_y_con_filas(tmp_path):
    ruta = str(tmp_path / "b.db")
    assert hay_filas(ruta, "t") is False                      # ausente
    open(ruta, "wb").close()
    assert hay_filas(ruta, "t") is False                      # archivo vacío (lo que dejaba init_db a medias)
    con = sqlite3.connect(ruta)
    con.execute("CREATE TABLE otra (x INTEGER)")
    con.commit(); con.close()
    assert hay_filas(ruta, "t") is False                      # base sin la tabla
    con = sqlite3.connect(ruta)
    con.execute("CREATE TABLE t (x INTEGER)")
    con.commit(); con.close()
    assert hay_filas(ruta, "t") is False                      # la tabla, vacía: es el caso de la 16-1
    con = sqlite3.connect(ruta)
    con.execute("INSERT INTO t VALUES (1)")
    con.commit(); con.close()
    assert hay_filas(ruta, "t") is True
    assert "no hay historia sellada" in razon_sin_base(ruta, "t")


def test_hay_filas_no_crea_la_base_ni_la_modifica(tmp_path):
    ausente = str(tmp_path / "no_existe.db")
    hay_filas(ausente, "t")
    assert not os.path.exists(ausente)
    ruta = str(tmp_path / "b.db")
    con = sqlite3.connect(ruta)
    con.execute("CREATE TABLE t (x INTEGER)"); con.execute("INSERT INTO t VALUES (1)")
    con.commit(); con.close()
    antes = os.stat(ruta)
    assert hay_filas(ruta, "t") is True
    despues = os.stat(ruta)
    assert (antes.st_size, antes.st_mtime_ns) == (despues.st_size, despues.st_mtime_ns)


# ------------------------------------------------------------
# (2) los marcadores
# ------------------------------------------------------------
@pytest.mark.parametrize("archivo,tabla", sorted(ARCHIVOS_CON_MARCADOR.items()))
def test_el_marcador_solo_con_base_exige_la_tabla_con_filas_y_no_el_archivo(archivo, tabla):
    fuente = open(os.path.join(RAIZ, "tests", archivo), encoding="utf-8").read()
    assert "solo_con_base" in fuente, archivo
    assert f'hay_filas(' in fuente and f'"{tabla}"' in fuente, f"{archivo}: el marcador no pregunta por {tabla} con filas"
    # la condición vieja, por archivo presente, ya no define al marcador
    bloque = fuente[fuente.index("solo_con_base") - 400: fuente.index("solo_con_base") + 200]
    assert not re.search(r"(HAY_BASE|solo_con_base)\s*=\s*(pytest\.mark\.skipif\()?\s*(not\s+)?os\.path\.exists", bloque), (
        f"{archivo}: el marcador sigue preguntando si el archivo existe")


_SKIP_POR_ARCHIVO = re.compile(
    r"skipif\(\s*not\s*\(?\s*os\.path\.(exists|isfile)\(\s*[A-Za-z_.]*(SENALES|BASE_REAL|RUTA_SENALES|NOTICIAS)", re.S)
# B4 del dictamen 16-3: la misma compuerta dentro del cuerpo de un test (`if not os.path.exists(<base real>): skip`)
_COMPUERTA_POR_ARCHIVO = re.compile(
    r"if\s+not\s+os\.path\.(exists|isfile)\(\s*[A-Za-z_.]*(SENALES_REAL|BASE_REAL|RUTA_SENALES|NOTICIAS_REAL)\s*\)")


def test_ningun_test_salta_por_la_existencia_del_archivo_de_una_base_real():
    """Si alguien copia el patrón viejo (saltar si el ARCHIVO no existe) a un
    archivo nuevo, este test lo dice. Medido el 11-oct-2026: además de los
    seis marcadores `solo_con_base`, `test_importador_roundtrip.py` y
    `test_restaurar_backup.py` saltaban por `isfile` y, con una base vacía
    dejada por otro test, compararon 0 filas contra la restauración."""
    culpables = []
    for nombre in sorted(os.listdir(os.path.join(RAIZ, "tests"))):
        if not nombre.startswith("test_") or not nombre.endswith(".py"):
            continue
        if nombre == os.path.basename(__file__):
            continue                      # la contraprueba de abajo lleva el patrón a propósito
        fuente = open(os.path.join(RAIZ, "tests", nombre), encoding="utf-8").read()
        if _SKIP_POR_ARCHIVO.search(fuente) or _COMPUERTA_POR_ARCHIVO.search(fuente):
            culpables.append(nombre)
        if "solo_con_base" in fuente and re.search(
                r"solo_con_base\s*=\s*pytest\.mark\.skipif\(\s*not\s+(HAY_BASE|os\.path\.exists)", fuente) \
                and "hay_filas(" not in fuente:
            culpables.append(nombre)
    assert not culpables, culpables


def test_contraprueba_el_barrido_ve_un_skipif_por_archivo():
    assert _SKIP_POR_ARCHIVO.search('x = pytest.mark.skipif(\n    not os.path.isfile(SENALES_REAL), reason="")')
    assert _SKIP_POR_ARCHIVO.search('pytest.mark.skipif(not (os.path.isfile(SENALES_REAL) and os.path.isfile(NOTICIAS_REAL)))')
    assert not _SKIP_POR_ARCHIVO.search('pytest.mark.skipif(not hay_filas(SENALES_REAL, "t"))')
    assert _COMPUERTA_POR_ARCHIVO.search("    if not os.path.exists(lb.RUTA_SENALES):\n        pytest.skip('x')")
    assert not _COMPUERTA_POR_ARCHIVO.search("    if not hay_filas(lb.RUTA_SENALES, 'verificacion_apertura'):")


# ------------------------------------------------------------
# (3) la guarda del conftest y el creador medido
# ------------------------------------------------------------
def test_contraprueba_el_detector_de_la_guarda_ve_una_base_creada_y_calla_si_ya_existia(tmp_path):
    conftest = importlib.import_module("conftest")
    raiz = str(tmp_path)
    os.makedirs(os.path.join(raiz, "dinero"))
    antes = conftest.existencia_bases(raiz)
    assert antes == {b: False for b in conftest.BASES_DEL_REPO}
    assert conftest.bases_creadas(antes, raiz) == []
    open(os.path.join(raiz, "senales.db"), "wb").close()
    assert conftest.bases_creadas(antes, raiz) == ["senales.db"]
    # si ya existía al empezar, no es «nueva»
    antes2 = conftest.existencia_bases(raiz)
    open(os.path.join(raiz, "noticias.db"), "wb").close()
    assert conftest.bases_creadas(antes2, raiz) == ["noticias.db"]


def test_contraprueba_el_detector_de_respaldos_ve_un_archivo_nuevo_bajo_data_backups(tmp_path):
    conftest = importlib.import_module("conftest")
    raiz = str(tmp_path)
    carpeta = os.path.join(raiz, "data", "backups", "sello_dinero_ext")
    os.makedirs(carpeta)
    habia = conftest.archivos_de_respaldo(raiz)
    assert habia == set() and conftest.respaldos_creados(habia, raiz) == []
    open(os.path.join(carpeta, "ext_2026-09-14.no_verificable.csv"), "wb").close()
    assert conftest.respaldos_creados(habia, raiz) == [os.path.join("data", "backups", "sello_dinero_ext",
                                                                     "ext_2026-09-14.no_verificable.csv")]
    habia2 = conftest.archivos_de_respaldo(raiz)
    assert conftest.respaldos_creados(habia2, raiz) == []            # lo que ya estaba no es nuevo


def test_la_guarda_esta_instalada_como_fixture_automatico():
    conftest = importlib.import_module("conftest")
    fx = getattr(conftest, "_ninguna_base_nueva_en_el_repo", None)
    assert fx is not None
    marca = getattr(fx, "_pytestfixturefunction", None) or getattr(fx, "_fixture_function_marker", None)
    fuente = open(os.path.join(RAIZ, "tests", "conftest.py"), encoding="utf-8").read()
    assert re.search(r"@pytest\.fixture\(autouse=True\)\s*\ndef _ninguna_base_nueva_en_el_repo", fuente)
    assert "senales.db" in fuente and "noticias.db" in fuente and "sello_dinero.db" in fuente


def test_test_api_declara_su_fixture_de_bases_temporales():
    """El único creador medido (11-oct-2026, 22 nodos de test_api.py) lee
    copias en tmp; la API no vuelve a correr DDL sobre la ruta real."""
    fuente = open(os.path.join(RAIZ, "tests", "test_api.py"), encoding="utf-8").read()
    assert re.search(r'@pytest\.fixture\(scope="module", autouse=True\)\s*\ndef _bases_de_la_api', fuente)
    for patron in ('mp.setattr(modulo, "DB_PATH", copia)', 'mp.setattr(lb, "RUTA_SENALES"', "origen.backup(destino)"):
        assert patron in fuente, patron
