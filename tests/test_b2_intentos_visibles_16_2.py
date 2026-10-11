"""Corrida 16-2 (11-oct-2026): B2 del dictamen de la corrida 15 — el intento no
verificable es visible fuera del log (acta §93.7; enmienda 16-2 de
`api/CONTRATO.md`, escrita ANTES que este código).

Lo que estos tests exigen: (1) `estado()` gana `ultimo_intento` con las
mismas claves que `ultimo`, `None` sin intentos; (2) con una base ANTERIOR a
E0.3 (sin la tabla) `estado()` y la API responden igual que hoy, con 0 y
`null`, y la lectura NO crea la tabla; (3) `/api/dinero/sellos` sirve
`intentos_no_verificables`, `ultimo_intento` y `nota_intentos` dentro de
`E0`, y un intento nunca entra a `sesiones_selladas`,
`sesiones_que_cuentan_para_N`, `filas`, `ultimo_sello` ni
`decisiones_proxima_apertura`; (4) ninguna clave existente de `E0` cambia;
(5) el contrato y los tipos del frontend declaran las tres claves; (6) la
norma del contrato (nada que insinúe resultado) rige sobre la frase nueva.
Base temporal en cada test; la API se prueba con `estado` redirigido a esa
base (la real no se abre)."""
import inspect
import os
import re
import sqlite3
from datetime import datetime, timezone

import pandas as pd
import pytest

from dinero import precios
from dinero import sello_dinero as S

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UTC = timezone.utc
N_OPERABLES = 32
BASE_HASTA = "2026-09-04"
LUNES = "2026-09-14"
SESIONES = ("2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11", LUNES)
T_INTRADIA = datetime(2026, 9, 14, 17, 43, 1, tzinfo=UTC)      # bolsa abierta: timing roto
T_NOCHE = datetime(2026, 9, 15, 3, 30, 4, tzinfo=UTC)          # 23:30 NY: timing ok
TABLA_INTENTOS = "intentos_no_verificables"
CLAVES_E0_VIEJAS = {"estado", "sesiones_selladas", "sesiones_que_cuentan_para_N", "N_objetivo", "N_objetivo_fuente",
                    "fuente_conteos", "filas", "divergencias_registradas", "nota", "estatus"}
CLAVES_E0_NUEVAS = {"intentos_no_verificables", "ultimo_intento", "nota_intentos"}
PROHIBIDAS = ("rentable", "retorno esperado", "ganancia esperada", "confianza", "sostiene casi toda")


@pytest.fixture(scope="module")
def base():
    return precios.cargar_congelado()


@pytest.fixture
def entorno_temporal(tmp_path, monkeypatch):
    db = str(tmp_path / "sello_dinero.db")
    monkeypatch.setattr(S, "DIR_EXT", str(tmp_path / "datos" / "sello"))
    monkeypatch.setattr(S, "RUTA_DB", db)
    monkeypatch.setattr(S, "DIR_BACKUP_EXT", str(tmp_path / "backups_ext"))
    monkeypatch.setattr(S, "RUTA_BACKUP_CSV", str(tmp_path / "sello_dinero.csv"))
    return db


def _ext(base, factor_ultima):
    ult = base.iloc[-1]
    ext = pd.DataFrame({pd.Timestamp(s): ult * 1.01 for s in SESIONES}).T
    ext.iloc[-1] = ult.values * factor_ultima
    ext.index.name = "Date"
    return ext


def _disparo(base, db, ahora, factor):
    ruta, meta = S.congelar_extension(_ext(base, factor), BASE_HASTA, ahora_utc=ahora)
    try:
        return S.sellar(ruta, meta, ahora_utc=ahora, ruta_db=db)
    finally:
        if not meta.get("persistido", True) and os.path.exists(ruta):
            os.remove(ruta)


def _tablas(db) -> set:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    finally:
        con.close()


def _base_e02(db) -> None:
    """El esquema anterior a E0.3, fabricado sin pasar por `init_db` (que ya
    crearía la tabla de intentos): la base real tal como está hoy."""
    con = sqlite3.connect(db)
    con.executescript(S._ddl_filas("sellos_dinero") + S._DDL_DIVERGENCIAS)
    con.commit(); con.close()


def _api_sellos(monkeypatch, db) -> dict:
    """`/api/dinero/sellos` leyendo la base temporal: `estado` se redirige
    porque su `ruta_db` por defecto quedó ligada al importar."""
    from fastapi.testclient import TestClient
    from api.main import app
    real = S.estado
    monkeypatch.setattr(S, "estado", lambda ruta_db=db: real(ruta_db))
    r = TestClient(app).get("/api/dinero/sellos")
    assert r.status_code == 200
    return r.json()["datos"]


# ------------------------------------------------------------
# 1 y 2. estado(): ultimo_intento, con y sin la tabla
# ------------------------------------------------------------
def test_estado_sin_base_y_con_base_anterior_a_e03_da_cero_intentos_y_ningun_ultimo_intento(tmp_path):
    db = str(tmp_path / "vieja.db")
    vacio = S.estado(db)                                            # la base no existe
    assert vacio["intentos_no_verificables"] == 0 and vacio["ultimo_intento"] is None
    _base_e02(db)
    antes = _tablas(db)
    assert TABLA_INTENTOS not in antes
    e = S.estado(db)
    assert e["intentos_no_verificables"] == 0 and e["ultimo_intento"] is None and e["filas"] == 0
    assert _tablas(db) == antes, "leer el estado NO crea la tabla de intentos"


def test_estado_con_un_intento_trae_ultimo_intento_con_las_claves_de_ultimo_y_ultimo_sigue_vacio(entorno_temporal, base):
    db = entorno_temporal
    r1 = _disparo(base, db, T_INTRADIA, 0.98)
    assert r1["resultado"] == "intento_no_verificable"
    e = S.estado(db)
    u = e["ultimo_intento"]
    assert u is not None and set(u) == set(S._CLAVES_ULTIMO)
    assert u["fecha_insumo"] == LUNES and u["timestamp_utc"] == r1["timestamp_utc"]
    assert u["estado"] == "no_verificable_timing" and u["estado_timing"] == "roto" and u["cuenta_para_N"] == 0
    assert u["insumo_ext_archivo"] == f"ext_{LUNES}.no_verificable.csv" and u["version_sello"] == S.VERSION_SELLO
    assert e["ultimo"] is None and e["filas"] == 0 and e["sesiones_selladas"] == 0 and e["intentos_no_verificables"] == 1
    # llega el sello bueno: `ultimo` es el sello, `ultimo_intento` no cambia
    r2 = _disparo(base, db, T_NOCHE, 1.02)
    assert r2["resultado"] == "sellada"
    e2 = S.estado(db)
    assert e2["ultimo"]["timestamp_utc"] == r2["timestamp_utc"] and e2["ultimo_intento"] == u
    assert e2["sesiones_selladas"] == 1 and e2["intentos_no_verificables"] == 1


def test_el_ultimo_intento_es_el_ultimo_por_id_cuando_hay_dos_fechas(entorno_temporal, base):
    db = entorno_temporal
    _disparo(base, db, T_INTRADIA, 0.98)                                              # intento del lunes
    ext = _ext(base, 0.99); ext.loc[pd.Timestamp("2026-09-15")] = base.iloc[-1].values * 0.97   # martes intradía
    ruta, meta = S.congelar_extension(ext, BASE_HASTA, ahora_utc=datetime(2026, 9, 15, 13, 31, 4, tzinfo=UTC))
    r = S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 15, 13, 31, 4, tzinfo=UTC), ruta_db=db)
    assert r["resultado"] == "intento_no_verificable" and r["fecha_insumo"] == "2026-09-15"
    e = S.estado(db)
    assert e["intentos_no_verificables"] == 2 and e["ultimo_intento"]["fecha_insumo"] == "2026-09-15"


# ------------------------------------------------------------
# 3 y 4. La API: las tres claves dentro de E0, las viejas intactas
# ------------------------------------------------------------
def test_la_api_sirve_el_intento_dentro_de_E0_y_nunca_como_sello(entorno_temporal, base, monkeypatch):
    db = entorno_temporal
    r1 = _disparo(base, db, T_INTRADIA, 0.98)
    d = _api_sellos(monkeypatch, db)
    e0 = d["E0"]
    assert set(e0) == CLAVES_E0_VIEJAS | CLAVES_E0_NUEVAS
    assert e0["intentos_no_verificables"] == 1
    assert e0["ultimo_intento"]["timestamp_utc"] == r1["timestamp_utc"]
    assert e0["ultimo_intento"]["estado"] == "no_verificable_timing" and e0["ultimo_intento"]["cuenta_para_N"] == 0
    assert isinstance(e0["nota_intentos"], str) and "no cuentan para N" in e0["nota_intentos"]
    # el intento no es un sello en ningún contador ni en la última fila
    assert e0["estado"] == "SIN FILAS" and e0["sesiones_selladas"] == 0 and e0["sesiones_que_cuentan_para_N"] == 0
    assert e0["filas"] == 0 and d["ultimo_sello"] is None and d["decisiones_proxima_apertura"] == []
    # y después del sello bueno, el intento sigue visible y el sello manda en lo suyo
    r2 = _disparo(base, db, T_NOCHE, 1.02)
    d2 = _api_sellos(monkeypatch, db)
    assert d2["E0"]["sesiones_selladas"] == 1 and d2["E0"]["filas"] == N_OPERABLES
    assert d2["ultimo_sello"]["timestamp_utc"] == r2["timestamp_utc"] and len(d2["decisiones_proxima_apertura"]) == N_OPERABLES
    assert d2["E0"]["intentos_no_verificables"] == 1 and d2["E0"]["ultimo_intento"] == e0["ultimo_intento"]


def test_la_api_responde_igual_con_una_base_anterior_a_e03_y_no_le_crea_la_tabla(tmp_path, monkeypatch):
    db = str(tmp_path / "vieja.db")
    _base_e02(db)
    antes = _tablas(db)
    d = _api_sellos(monkeypatch, db)
    assert d["E0"]["intentos_no_verificables"] == 0 and d["E0"]["ultimo_intento"] is None
    assert set(d["E0"]) == CLAVES_E0_VIEJAS | CLAVES_E0_NUEVAS and d["E0"]["estado"] == "SIN FILAS"
    assert _tablas(db) == antes and TABLA_INTENTOS not in antes


def test_las_frases_nuevas_de_la_api_no_insinuan_resultado(entorno_temporal, base, monkeypatch):
    """La norma del contrato de la corrida 12, aplicada a `nota_intentos` y al
    payload entero con un intento adentro."""
    import json
    db = entorno_temporal
    _disparo(base, db, T_INTRADIA, 0.98)
    txt = json.dumps(_api_sellos(monkeypatch, db), ensure_ascii=False, default=str).lower()
    for p in PROHIBIDAS:
        assert p not in txt, p


# ------------------------------------------------------------
# 5. El contrato y los tipos declaran lo que la API sirve
# ------------------------------------------------------------
def test_el_contrato_y_los_tipos_del_frontend_declaran_las_tres_claves():
    contrato = open(os.path.join(RAIZ, "api", "CONTRATO.md"), encoding="utf-8").read()
    i = contrato.find("Enmienda 16-2")
    assert i > 0, "api/CONTRATO.md no tiene la enmienda 16-2 (se enmienda ANTES de tocar la API)"
    seccion = contrato[i:]
    for clave in CLAVES_E0_NUEVAS:
        assert f"`{clave}`" in seccion, clave
    tipos = open(os.path.join(RAIZ, "frontend", "src", "lib", "tipos.ts"), encoding="utf-8").read()
    e0 = re.search(r"export interface DatosSellosDinero \{.*?\n  E0: \{(.*?)\n  \}", tipos, re.S).group(1)
    for clave in CLAVES_E0_NUEVAS:
        assert re.search(rf"^\s+{clave}:", e0, re.M), f"tipos.ts no declara E0.{clave}"
    assert "ultimo_intento: UltimoSelloDinero | null" in e0 and "ultimo_sello: UltimoSelloDinero | null" in tipos
    # R6 del auditor (corrida 16-2): la interfaz cubre las 21 claves de `_CLAVES_ULTIMO`, ni una menos
    cuerpo = re.search(r"export interface UltimoSelloDinero \{(.*?)\n\}", tipos, re.S).group(1)
    campos = set(re.findall(r"^\s+(\w+):", cuerpo, re.M))
    assert campos == set(S._CLAVES_ULTIMO), (sorted(set(S._CLAVES_ULTIMO) - campos), sorted(campos - set(S._CLAVES_ULTIMO)))


def test_la_api_no_computa_el_intento_lo_lee_de_estado():
    """La API es de sólo lectura: las claves nuevas salen de `estado()` y no
    de una consulta propia a la base del sellador."""
    from api import main as api
    src = inspect.getsource(api.dinero_sellos)
    assert 'e.get("intentos_no_verificables", 0)' in src and 'e.get("ultimo_intento")' in src
    assert "sqlite3" not in src and "intentos_no_verificables" not in src.replace('e.get("intentos_no_verificables", 0)', "").replace('"intentos_no_verificables":', "")
