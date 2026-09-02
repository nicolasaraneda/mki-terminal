# ============================================================
# tests/test_segundo_sello.py — el arnés del segundo sello.
#
# Lo que estos tests defienden, en orden de importancia:
#   1. LA CONTRAPRUEBA (docs/SEGUNDO_SELLO.md §2): el mecanismo puede
#      discrepar, con la magnitud correcta, y NO discrepa cuando no hay
#      nada que reportar. Sin las dos ramas la prueba no vale.
#   2. LA CEGUERA: la fase que produce el número no puede leer el sello.
#      Verificada sobre el AST, no sobre la intención.
#   3. LA ADITIVIDAD: solo INSERT; ninguna sentencia que reescriba.
#   4. LA DIRECCIÓN DEL IMPORT: nada de la ruta de sellado importa esto.
# ============================================================

import ast
import os
import sqlite3
import sys

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from GEMELO.SEGUNDO_SELLO import segundo_sello as ss   # noqa: E402

RUTA_MODULO = os.path.abspath(ss.__file__)

# Cierres reales de ^SOX medidos el 1-sep-2026 (yfinance, auto_adjust=True).
# La barra del 2026-08-28 NO está: ese es el incidente que motiva el frente.
CIERRES_MEDIDOS_HOY = {
    "2026-08-24": 11423.169922,
    "2026-08-25": 11588.040039,
    "2026-08-26": 11611.240234,
    "2026-08-27": 11882.169922,
    "2026-08-31": 11535.049805,
}
# El cierre del 28-ago que la producción SÍ vio, implícito en dos sellos
# independientes (-3.47 el 28 y +0.57 el 31): banda [11469.26, 11470.24].
CIERRE_28_IMPLICITO = 11469.86


def _serie(mapa: dict) -> pd.DataFrame:
    idx = pd.to_datetime(sorted(mapa))
    return pd.DataFrame({"^SOX": [mapa[str(i.date())] for i in idx]}, index=idx)


def _senales_falsa(ruta: str, filas: list) -> None:
    """Una `senales.db` de juguete. Los tests JAMÁS tocan la real."""
    conn = sqlite3.connect(ruta)
    conn.execute("CREATE TABLE snapshots (fecha TEXT, sox_usado_pct REAL, "
                 "sox_fecha TEXT, timestamp_utc TEXT, plataforma_version TEXT)")
    conn.executemany("INSERT INTO snapshots VALUES (?, ?, ?, ?, ?)", filas)
    conn.commit()
    conn.close()


# ------------------------------------------------------------
# 1. LA CONTRAPRUEBA
# ------------------------------------------------------------

def test_contraprueba_detecta_una_diferencia_inyectada(tmp_path):
    """Rama positiva Y control negativo, en la misma corrida."""
    mapa = dict(CIERRES_MEDIDOS_HOY)
    mapa["2026-08-28"] = CIERRE_28_IMPLICITO
    cierres = _serie(mapa)

    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-28", -3.47, "2026-08-28",
                               "2026-08-28T22:15:03+00:00", "5.0.3")])
    ruta_db = str(tmp_path / "segundo_sello.db")

    r = ss.contraprueba(cierres, "2026-08-28", ruta_db, ruta_sen,
                        perturbacion_pp=1.00)

    assert r["control"]["veredicto"] == ss.PARIDAD, r["control"]
    assert r["perturbada"]["veredicto"] == ss.DIVERGENCIA_DE_VALOR, r["perturbada"]
    assert r["detecta"] is True
    # La magnitud reportada es la inyectada, no "algo distinto de cero".
    assert abs(r["magnitud_reportada_pp"] - 1.00) < 0.01


@pytest.mark.parametrize("pp", [0.10, 0.50, 2.00, -1.50])
def test_la_magnitud_reportada_es_la_inyectada(tmp_path, pp):
    mapa = dict(CIERRES_MEDIDOS_HOY)
    mapa["2026-08-28"] = CIERRE_28_IMPLICITO
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-28", -3.47, "2026-08-28",
                               "2026-08-28T22:15:03+00:00", "5.0.3")])
    r = ss.contraprueba(_serie(mapa), "2026-08-28",
                        str(tmp_path / "db.db"), ruta_sen, perturbacion_pp=pp)
    assert r["perturbada"]["veredicto"] == ss.DIVERGENCIA_DE_VALOR
    assert abs(r["magnitud_reportada_pp"] - abs(pp)) < 0.01


def test_una_perturbacion_bajo_tolerancia_no_es_divergencia(tmp_path):
    """La tolerancia existe porque el sello está redondeado a 2 decimales.
    Una diferencia de 0.001 pp es redondeo, no un hallazgo."""
    mapa = dict(CIERRES_MEDIDOS_HOY)
    mapa["2026-08-28"] = CIERRE_28_IMPLICITO
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-28", -3.47, "2026-08-28",
                               "2026-08-28T22:15:03+00:00", "5.0.3")])
    r = ss.contraprueba(_serie(mapa), "2026-08-28",
                        str(tmp_path / "db.db"), ruta_sen, perturbacion_pp=0.001)
    assert r["perturbada"]["veredicto"] == ss.PARIDAD


# ------------------------------------------------------------
# 2. EL CASO REAL: la barra retirada del 2026-08-28
# ------------------------------------------------------------

def test_el_incidente_del_28_de_agosto_sale_como_barra_retirada(tmp_path):
    """Sin inyectar nada: con los cierres que la fuente sirve HOY, el sello
    del 28-ago no es reproducible porque su barra ya no existe."""
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-28", -3.47, "2026-08-28",
                               "2026-08-28T22:15:03+00:00", "5.0.3")])
    ruta_db = str(tmp_path / "db.db")
    fechas = sorted(set(CIERRES_MEDIDOS_HOY) | {"2026-08-28"})
    obs = ss.observar(fechas, lambda t: _serie(CIERRES_MEDIDOS_HOY),
                      observado_en="2026-09-01T16:12:00+00:00", horizonte=1)
    ss.registrar(obs, ruta_db)
    r = ss.contrastar("2026-08-28", obs[0]["corrida"], ruta_db, ruta_sen)
    assert r["veredicto"] == ss.BARRA_RETIRADA, r
    assert r["final"] is True
    assert r["canonica"] is None      # el arnés no decide


def test_el_31_de_agosto_sale_como_barra_aparecida_no_como_paridad(tmp_path):
    """El 31 tiene barra, pero su retorno de hoy abarca dos sesiones porque
    la del 28 falta. Que el número difiera NO es 'la fuente revisó el
    precio del 31': es la misma amputación vista desde el día siguiente."""
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-31", 0.57, "2026-08-31",
                               "2026-08-31T22:15:03+00:00", "5.0.3")])
    ruta_db = str(tmp_path / "db.db")
    fechas = sorted(set(CIERRES_MEDIDOS_HOY) | {"2026-08-28"})
    obs = ss.observar(fechas, lambda t: _serie(CIERRES_MEDIDOS_HOY),
                      observado_en="2026-09-01T16:12:00+00:00", horizonte=1)
    ss.registrar(obs, ruta_db)
    r = ss.contrastar("2026-08-31", obs[0]["corrida"], ruta_db, ruta_sen)
    assert r["veredicto"] != ss.PARIDAD
    assert r["final"] is True
    assert round(abs(r["dif_pp"]), 2) == 3.49    # cifra medida el 1-sep-2026


# ------------------------------------------------------------
# 2 bis. LA GUARDIA DE COBERTURA — el defecto que el propio arnés se
#        encontró en su primera corrida real (1-sep-2026).
# ------------------------------------------------------------

SESIONES_AGO = ["2026-08-24", "2026-08-25", "2026-08-26", "2026-08-27",
                "2026-08-28", "2026-08-31"]


def test_una_sesion_no_observada_no_puede_salir_como_divergencia(tmp_path):
    """Observar SOLO las fechas selladas hizo que el 2026-08-07 saliera
    como divergencia de 0.34 pp. Era un artefacto: faltaba la barra del
    08-06 en la MUESTRA, no en la FUENTE. La guardia lo convierte en una
    ausencia declarada, que es lo que es."""
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-27", 2.33, "2026-08-27", "x", "5.0.3")])
    ruta_db = str(tmp_path / "db.db")
    # Se omite el 2026-08-26 de la observación, no de la fuente.
    fechas = ["2026-08-24", "2026-08-25", "2026-08-27"]
    obs = ss.observar(fechas, lambda t: _serie(CIERRES_MEDIDOS_HOY),
                      observado_en="t", horizonte=1)
    ss.registrar(obs, ruta_db)
    sin_guardia = ss.contrastar("2026-08-27", obs[0]["corrida"], ruta_db, ruta_sen)
    con_guardia = ss.contrastar("2026-08-27", obs[0]["corrida"], ruta_db,
                                ruta_sen, sesiones=SESIONES_AGO)
    assert sin_guardia["cobertura_verificada"] is False
    assert con_guardia["veredicto"] == ss.SIN_SEGUNDA_OBSERVACION
    assert con_guardia["final"] is False
    assert "2026-08-26" in con_guardia["sesiones_no_observadas"]


def test_con_el_calendario_el_31_se_lee_como_barra_retirada(tmp_path):
    """Con la guardia puesta, el 31-ago deja de leerse como 'la fuente
    revisó el precio del 31' y se lee por su causa real: falta la del 28."""
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-31", 0.57, "2026-08-31", "x", "5.0.3")])
    ruta_db = str(tmp_path / "db.db")
    obs = ss.observar(SESIONES_AGO, lambda t: _serie(CIERRES_MEDIDOS_HOY),
                      observado_en="t", horizonte=1)
    ss.registrar(obs, ruta_db)
    r = ss.contrastar("2026-08-31", obs[0]["corrida"], ruta_db, ruta_sen,
                      sesiones=SESIONES_AGO)
    assert r["veredicto"] == ss.BARRA_RETIRADA, r
    assert r["sesiones_retiradas"] == ["2026-08-28"]
    assert r["par_usado_hoy"] == ["2026-08-27", "2026-08-31"]


def test_una_divergencia_de_valor_real_sobrevive_a_la_guardia(tmp_path):
    """La guardia no puede convertirlo TODO en ausencia: con cobertura
    completa y una perturbación inyectada, el veredicto sigue siendo
    divergencia de valor."""
    mapa = dict(CIERRES_MEDIDOS_HOY)
    mapa["2026-08-28"] = CIERRE_28_IMPLICITO
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-28", -3.47, "2026-08-28", "x", "5.0.3")])
    r = ss.contraprueba(_serie(mapa), "2026-08-28", str(tmp_path / "db.db"),
                        ruta_sen, perturbacion_pp=1.00, sesiones=SESIONES_AGO)
    assert r["control"]["veredicto"] == ss.PARIDAD
    assert r["perturbada"]["veredicto"] == ss.DIVERGENCIA_DE_VALOR
    assert r["control"]["cobertura_verificada"] is True


# ------------------------------------------------------------
# 3. "NADA = NADA" NUNCA ES PARIDAD  (lección de comparar_sombra.py)
# ------------------------------------------------------------

def test_sin_observacion_no_es_paridad(tmp_path):
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-27", 2.33, "2026-08-27", "x", "5.0.3")])
    r = ss.contrastar("2026-08-27", "corrida-inexistente",
                      str(tmp_path / "db.db"), ruta_sen)
    assert r["veredicto"] == ss.SIN_SEGUNDA_OBSERVACION
    assert r["final"] is False


def test_sin_sello_no_es_paridad(tmp_path):
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [])
    ruta_db = str(tmp_path / "db.db")
    obs = ss.observar(sorted(CIERRES_MEDIDOS_HOY),
                      lambda t: _serie(CIERRES_MEDIDOS_HOY),
                      observado_en="t", horizonte=1)
    ss.registrar(obs, ruta_db)
    r = ss.contrastar("2026-08-27", obs[0]["corrida"], ruta_db, ruta_sen)
    assert r["veredicto"] == ss.SIN_SELLO
    assert r["final"] is False


# ------------------------------------------------------------
# 4. LA CEGUERA (B2), verificada sobre el AST
# ------------------------------------------------------------

PROHIBIDO_EN_LA_FASE_CIEGA = {
    "senales", "snapshot", "motor", "sellado", "_sellado",
    "RUTA_SENALES", "contrastar", "leer_observaciones", "sqlite3",
}


def _nombres_usados(fn: ast.FunctionDef) -> set:
    usados = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Name):
            usados.add(n.id)
        elif isinstance(n, ast.Attribute):
            usados.add(n.attr)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            mod = getattr(n, "module", None) or ""
            usados.add(mod.split(".")[0])
            for a in n.names:
                usados.add(a.name.split(".")[0])
    return usados


@pytest.mark.parametrize("nombre", ["observar", "proveedor_yahoo", "id_corrida"])
def test_la_fase_que_produce_el_numero_es_ciega_al_sello(nombre):
    arbol = ast.parse(open(RUTA_MODULO, encoding="utf-8").read())
    fn = next(n for n in arbol.body
              if isinstance(n, ast.FunctionDef) and n.name == nombre)
    fuga = _nombres_usados(fn) & PROHIBIDO_EN_LA_FASE_CIEGA
    assert not fuga, (
        f"`{nombre}` produce su número mirando {sorted(fuga)}: eso es una "
        "confirmación, no una verificación (regla 1 de la casa).")


def test_observar_no_recibe_ni_deduce_la_lista_de_fechas_selladas():
    """Refuerzo de la ceguera: `observar` recibe fechas, no una base."""
    import inspect
    firma = inspect.signature(ss.observar)
    assert "fechas" in firma.parameters
    assert not any("senales" in p or "ruta" in p for p in firma.parameters)


# ------------------------------------------------------------
# 5. ADITIVIDAD (B1) e INMUTABILIDAD DE LA BASE SELLADA
# ------------------------------------------------------------

def test_el_modulo_no_tiene_una_sola_sentencia_que_reescriba():
    """Se mira el SQL de verdad —los literales de cadena del AST—, no la
    prosa: un comentario que menciona UPDATE no reescribe nada, y un test
    que confunde las dos cosas se desactiva solo a la primera molestia."""
    arbol = ast.parse(open(RUTA_MODULO, encoding="utf-8").read())
    literales = [n.value.upper() for n in ast.walk(arbol)
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    # Los docstrings son prosa, no SQL: se excluyen explícitamente.
    docstrings = {ast.get_docstring(n) for n in ast.walk(arbol)
                  if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))}
    docstrings = {d.upper() for d in docstrings if d}
    for lit in literales:
        if lit in docstrings:
            continue
        for prohibida in ("UPDATE ", "DELETE FROM", "DROP TABLE", "ALTER TABLE",
                          "INSERT OR REPLACE", "IF_EXISTS"):
            assert prohibida not in lit, f"{prohibida!r} en el SQL: {lit[:120]!r}"


def test_una_segunda_observacion_se_suma_no_pisa_a_la_primera(tmp_path):
    ruta_db = str(tmp_path / "db.db")
    o1 = ss.observar(["2026-08-27"], lambda t: _serie(CIERRES_MEDIDOS_HOY),
                     observado_en="T1", horizonte=1)
    o2 = ss.observar(["2026-08-27"], lambda t: _serie(CIERRES_MEDIDOS_HOY),
                     observado_en="T2", horizonte=3)
    assert ss.registrar(o1, ruta_db) == 1
    assert ss.registrar(o2, ruta_db) == 1
    conn = sqlite3.connect(f"file:{ruta_db}?mode=ro", uri=True)
    n, corridas = conn.execute(
        "SELECT COUNT(*), COUNT(DISTINCT corrida) FROM observaciones").fetchone()
    conn.close()
    assert (n, corridas) == (2, 2)
    # Y repetir la misma corrida no inserta ni modifica nada.
    assert ss.registrar(o1, ruta_db) == 0


def test_contrastar_abre_senales_solo_en_modo_lectura():
    fuente = open(RUTA_MODULO, encoding="utf-8").read()
    aperturas = [l for l in fuente.splitlines() if "ruta_senales" in l and "connect" in l]
    assert aperturas, "no se encontró la apertura de senales.db"
    assert all("mode=ro" in l for l in aperturas), aperturas


def test_la_base_sellada_real_no_se_toca(tmp_path):
    """Si `senales.db` existe en esta máquina, contrastar no la modifica."""
    if not os.path.exists(ss.RUTA_SENALES):
        pytest.skip("no hay senales.db en esta máquina")
    antes = os.stat(ss.RUTA_SENALES).st_mtime_ns
    ss.contrastar("2026-08-27", "corrida-inexistente",
                  str(tmp_path / "db.db"), ss.RUTA_SENALES)
    assert os.stat(ss.RUTA_SENALES).st_mtime_ns == antes


# ------------------------------------------------------------
# 6. LA DIRECCIÓN DEL IMPORT: la ruta de sellado no sabe que esto existe
# ------------------------------------------------------------

@pytest.mark.parametrize("archivo", ["motor.py", "snapshot.py", "senales.py",
                                     "universo.py", "alertas.py", "app.py",
                                     "mki_vigia.py", "calendarios.py"])
def test_la_ruta_de_sellado_no_importa_el_segundo_sello(archivo):
    ruta = os.path.join(RAIZ, archivo)
    if not os.path.exists(ruta):
        pytest.skip(f"{archivo} no existe")
    fuente = open(ruta, encoding="utf-8").read()
    assert "SEGUNDO_SELLO" not in fuente and "segundo_sello" not in fuente


def test_nadie_lo_invoca_todavia():
    """Es código que existe y se prueba, no que se ejecuta. Si algún día
    un timer lo llama, este test lo obliga a pasar por una decisión."""
    for carpeta in ("systemd", "launchd"):
        d = os.path.join(RAIZ, carpeta)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p):
                assert "segundo_sello" not in open(p, encoding="utf-8",
                                                   errors="ignore").read()


# ------------------------------------------------------------
# 7. PARÁMETROS CONGELADOS ANTES DE LA PRIMERA FILA (B3 / B7)
# ------------------------------------------------------------

def test_los_parametros_congelados_estan_donde_dice_el_diseno():
    assert ss.TOLERANCIA_PP == 0.005
    assert ss.HORIZONTES_SESIONES == (1, 3, 7, 30)
    assert ss.PARIDAD in ss.VEREDICTOS_FINALES
    assert ss.SIN_SELLO not in ss.VEREDICTOS_FINALES
    assert ss.SIN_SEGUNDA_OBSERVACION not in ss.VEREDICTOS_FINALES


def test_el_arnes_nunca_declara_una_canonica(tmp_path):
    """La regla del §3 espera firma. Ninguna rama puede fijarla."""
    ruta_sen = str(tmp_path / "senales.db")
    _senales_falsa(ruta_sen, [("2026-08-27", 2.33, "2026-08-27", "x", "5.0.3")])
    ruta_db = str(tmp_path / "db.db")
    obs = ss.observar(sorted(CIERRES_MEDIDOS_HOY),
                      lambda t: _serie(CIERRES_MEDIDOS_HOY),
                      observado_en="t", horizonte=1)
    ss.registrar(obs, ruta_db)
    for fecha in ("2026-08-27", "2026-08-31", "2026-09-09"):
        assert ss.contrastar(fecha, obs[0]["corrida"], ruta_db,
                             ruta_sen)["canonica"] is None
