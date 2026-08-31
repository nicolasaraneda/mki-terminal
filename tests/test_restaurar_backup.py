"""
Tests del importador de CSV (Frente 5). Corren en la suite normal
(`python -m pytest tests/ -q`).

Regla dura verificada en todos lados: este módulo NUNCA abre senales.db ni
noticias.db en modo escritura. Cuando compara contra las bases reales, las
abre siempre `mode=ro`.
"""
import csv
import os
import sqlite3
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import restaurar_backup as rb  # noqa: E402

ORIGEN = os.path.join(RAIZ, "data", "backups")
SENALES_REAL = os.path.join(RAIZ, "senales.db")
NOTICIAS_REAL = os.path.join(RAIZ, "noticias.db")


def _contar_filas_csv(nombre: str) -> int:
    ruta = os.path.join(ORIGEN, nombre)
    with open(ruta, encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


# --------------------------------------------------------------- restauración

def test_restaura_sin_tocar_las_bases_reales(tmp_path, monkeypatch):
    """La restauración nunca abre senales.db/noticias.db reales — ni para
    leer. No alcanza con "corre aunque no existan": esto espía CADA llamada
    a sqlite3.connect durante restaurar() y falla si alguna apunta a la
    ruta real, sea como path plano o como URI `file:...`."""
    rutas_reales_abs = {os.path.abspath(SENALES_REAL), os.path.abspath(NOTICIAS_REAL)}
    conexiones_abiertas = []

    conectar_original = sqlite3.connect

    def _espia_connect(database, *args, **kwargs):
        objetivo = database
        if isinstance(database, str) and database.startswith("file:"):
            # pelar "file:" y cualquier "?modo=..." para comparar el path crudo
            objetivo = database[len("file:"):].split("?", 1)[0]
        if isinstance(objetivo, str) and os.path.isabs(objetivo):
            conexiones_abiertas.append(os.path.abspath(objetivo))
        return conectar_original(database, *args, **kwargs)

    monkeypatch.setattr(rb.sqlite3, "connect", _espia_connect)

    destino = tmp_path / "restaurado"
    ruta_senales, ruta_noticias, reportes = rb.restaurar(ORIGEN, str(destino))

    tocadas = [c for c in conexiones_abiertas if c in rutas_reales_abs]
    assert tocadas == [], f"restaurar() abrió una conexión a la base REAL: {tocadas}"

    assert os.path.isfile(ruta_senales)
    assert os.path.isfile(ruta_noticias)
    assert len(reportes) == len(rb.ESQUEMA_SENALES) + len(rb.ESQUEMA_NOTICIAS)


def test_no_pisa_una_restauracion_existente(tmp_path):
    destino = tmp_path / "restaurado"
    rb.restaurar(ORIGEN, str(destino))
    with pytest.raises(FileExistsError):
        rb.restaurar(ORIGEN, str(destino))


@pytest.mark.parametrize("tabla,spec", list(rb.ESQUEMA_SENALES.items()) + list(rb.ESQUEMA_NOTICIAS.items()))
def test_todas_las_filas_del_csv_se_importan(tmp_path, tabla, spec):
    """La prueba mínima de fidelidad: ninguna fila se pierde ni se duplica
    en el viaje CSV -> base nueva."""
    destino = tmp_path / "restaurado"
    rb.restaurar(ORIGEN, str(destino))
    csv_nombre = spec[0]
    esperadas = _contar_filas_csv(csv_nombre)

    es_senales = tabla in rb.ESQUEMA_SENALES
    ruta_db = str(destino / ("senales_restaurado.db" if es_senales else "noticias_restaurado.db"))
    conn = sqlite3.connect(f"file:{ruta_db}?mode=ro", uri=True)
    try:
        n = conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    finally:
        conn.close()
    assert n == esperadas, f"{tabla}: {esperadas} filas en el CSV, {n} importadas"


def test_hash_es_reproducible_entre_dos_restauraciones_independientes(tmp_path):
    """Restaurar dos veces desde los mismos CSV, a directorios distintos,
    tiene que dar el HASH DE CONTENIDO idéntico por tabla — es la prueba de
    que el importador es determinístico, no solo "parece que anduvo"."""
    d1 = tmp_path / "r1"
    d2 = tmp_path / "r2"
    rb.restaurar(ORIGEN, str(d1))
    rb.restaurar(ORIGEN, str(d2))

    for tabla, (_csv, _ddl, columnas, pk) in rb.ESQUEMA_SENALES.items():
        nombres = [c for c, _t in columnas]
        c1 = sqlite3.connect(f"file:{d1 / 'senales_restaurado.db'}?mode=ro", uri=True)
        c2 = sqlite3.connect(f"file:{d2 / 'senales_restaurado.db'}?mode=ro", uri=True)
        try:
            h1 = rb.hash_tabla(c1, tabla, nombres, pk)
            h2 = rb.hash_tabla(c2, tabla, nombres, pk)
        finally:
            c1.close()
            c2.close()
        assert h1 == h2, f"{tabla}: el hash difiere entre dos restauraciones del mismo CSV"


# ------------------------------------------------------- coacción de tipos

def test_coaccion_recupera_el_artefacto_conocido_de_pandas():
    """'120.0' en una columna INTEGER (el artefacto de pandas al exportar
    una columna entera con NULLs) se recupera como el entero 120, sin
    hallazgo — es pérdida cosmética, no de valor."""
    hallazgos = []
    v = rb._coaccionar("120.0", "INTEGER", hallazgos, "test")
    assert v == 120
    assert isinstance(v, int)
    assert hallazgos == []


def test_coaccion_marca_fraccion_real_como_hallazgo():
    """Si alguna vez aparece una fracción REAL (no el artefacto de pandas)
    en una columna declarada INTEGER, no se trunca en silencio: se guarda
    tal cual y se declara como hallazgo."""
    hallazgos = []
    v = rb._coaccionar("120.5", "INTEGER", hallazgos, "test")
    assert v == 120.5
    assert len(hallazgos) == 1


def test_coaccion_vacio_es_null_por_defecto():
    hallazgos = []
    assert rb._coaccionar("", "TEXT", hallazgos, "test") is None
    assert rb._coaccionar("", "REAL", hallazgos, "test") is None
    assert rb._coaccionar("", "INTEGER", hallazgos, "test") is None


def test_coaccion_vacio_es_cadena_vacia_en_columnas_default_vacio():
    """El hallazgo real de esta corrida: `titulares.tickers`,
    `divergencias.explicacion` y `analisis.tickers_afectados` son
    TEXT NOT NULL DEFAULT '' — un campo vacío del CSV ahí es la cadena
    vacía real, NUNCA NULL (insertar NULL viola la constraint, como pasó
    en la primera corrida de este importador)."""
    hallazgos = []
    assert rb._coaccionar("", "TEXT", hallazgos, "test", defecto_vacio=True) == ""


# ------------------------------------------ comparación contra las bases reales

pytestmark_reales = pytest.mark.skipif(
    not (os.path.isfile(SENALES_REAL) and os.path.isfile(NOTICIAS_REAL)),
    reason="senales.db/noticias.db no existen en este checkout — exactamente "
           "el escenario de 'se perdió el disco', nada que comparar",
)


@pytestmark_reales
def test_verificacion_puntaje_es_identica_a_la_base_real(tmp_path):
    """De las ocho tablas, `verificacion_puntaje` es la que hoy (31-ago-2026)
    coincide exactamente con la base real — sirve de canario: si esto deja
    de ser cierto, algo cambió en cómo se exporta o se importa esa tabla."""
    destino = tmp_path / "restaurado"
    ruta_senales, _n, _r = rb.restaurar(ORIGEN, str(destino))
    diffs = rb.comparar_con_original(SENALES_REAL, ruta_senales, rb.ESQUEMA_SENALES)
    por_tabla = {d.tabla: d for d in diffs}
    vp = por_tabla["verificacion_puntaje"]
    assert vp.identica, (
        f"verificacion_puntaje ya no es idéntica al backup: "
        f"n_original={vp.conteo_original} n_restaurado={vp.conteo_restaurado}"
    )


@pytestmark_reales
def test_comparacion_no_pierde_filas_de_noticias_que_no_esten_en_el_csv(tmp_path):
    """Las tablas de noticias solo pueden CRECER entre un backup y ahora
    (nunca se borra un titular) — si la base restaurada (congelada al
    momento del backup) tuviera MÁS filas que la base real actual, eso sí
    sería una señal de corrupción real, no de staleness normal."""
    destino = tmp_path / "restaurado"
    _s, ruta_noticias, _r = rb.restaurar(ORIGEN, str(destino))
    diffs = rb.comparar_con_original(NOTICIAS_REAL, ruta_noticias, rb.ESQUEMA_NOTICIAS)
    for d in diffs:
        assert d.conteo_restaurado <= d.conteo_original, (
            f"{d.tabla}: el backup tiene MÁS filas ({d.conteo_restaurado}) que la "
            f"base real actual ({d.conteo_original}) — eso no es staleness, "
            "es una pérdida real en la base real y hay que investigarlo"
        )
