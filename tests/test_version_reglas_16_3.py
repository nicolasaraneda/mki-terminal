"""Corrida 16-3, Bloque C (acta §102.4): el parche `version_reglas_16_3.diff`,
que NO se aplica al árbol real en la 16-3 (regla de un solo cambio al sellador
por noche; la del 13-oct lleva el camino T). Cuatro cosas firmadas o
recomendadas, en un solo parche:

 (1) §99.5 (firma de Nicolás, 10-oct-2026): `version_reglas` pasa de
     0.2.0-PROPUESTA a 0.3.0-PROPUESTA, legible en el CSV versionado sin
     cotejar hashes. Cambia `reglas_sha256` otra vez: tercera población de
     filas de E0, distinguible por versión y por huella. Ninguna regla
     numérica se mueve.
 (2) R4 del dictamen 16b: un ticker declarado en `exclusiones_insumo_e0` que
     no está en el censo de operables revienta con `ValueError` nombrándolo,
     en vez de ignorarse en silencio (un nombre mal escrito dejaría de excluir
     y nadie lo sabría).
 (3) §81.3 (b), firmada en §102.6 (3): las filas de un intento no verificable
     llevan en `motivo` el instante con que se decidió el timing (el de
     congelar, cuando la evidencia nació `.no_verificable`; F2 del dictamen
     16-2: una fila de intento podía satisfacer la regla maestra en sus tres
     columnas y decir `roto` sin que la fila lo explicara). Sin cambio de
     esquema. Las filas de un sello no cambian.
 (4) R2 del dictamen 16b: `estado()` gana `por_reglas_sha256`, el desglose por
     población (hash, versión, sesiones, las que cuentan, filas, desde, hasta),
     aditivo; la API no lo sirve todavía (sin enmienda del contrato).

Escritos antes del código y rojos sobre HEAD por su propia aserción. Base
temporal en cada test; la real sólo en `mode=ro` y con salto declarado."""
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from dinero import precios
from dinero import sello_dinero as S
from dinero import universo_dinero as U

UTC = timezone.utc
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N_OPERABLES = 32
BASE_HASTA = "2026-09-04"
LUNES = "2026-09-14"
SESIONES = ("2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11", LUNES)
T_INTRADIA = datetime(2026, 9, 14, 17, 43, 1, tzinfo=UTC)      # 13:43 NY, bolsa abierta: timing roto
T_NOCHE = datetime(2026, 9, 15, 3, 30, 4, tzinfo=UTC)          # 23:30 NY: timing ok
HUELLAS_ANTERIORES = {"125a8602a684939576278093b306add6a6fa7a0157389f71a5c0029455ab9ba0",   # hasta el 2-oct (33 operables)
                      "b6080eee4351ed433aeb5a124ec4603dcb3db3b3278b1791c40ee8a4ad0abc6c"}   # desde el 5-oct (sin TOELY)
COLUMNAS_FILA = ("id", "fecha_sello", "fecha_insumo", "timestamp_utc", "available_at", "exchange", "sesion_objetivo",
                 "apertura_objetivo_utc", "ticker", "decision", "acciones_regla", "tamano_nominal", "precio_ref_usd",
                 "senal_magnitud_pp", "senal_banda_baja_pp", "senal_banda_alta_pp", "senal_fuente", "juego",
                 "presupuesto_usd", "reglas_version", "motivo", "ultimo_cierre_ticker", "available_at_ticker",
                 "insumo_ext_sha256", "insumo_ext_archivo", "insumo_base_sha256", "reglas_sha256", "sellador_sha256",
                 "plataforma_version", "version_sello", "estado", "estado_timing", "estado_dia", "insumo_completo",
                 "cuenta_para_N", "creado_en")


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


def _ext(base, factor_ultima, sesiones=SESIONES):
    ult = base.iloc[-1]
    ext = pd.DataFrame({pd.Timestamp(s): ult * 1.01 for s in sesiones}).T
    ext.iloc[-1] = ult.values * factor_ultima
    ext.index.name = "Date"
    return ext


def _disparo(base, db, congelar_en, sellar_en, factor=0.97, cfg=None):
    ruta, meta = S.congelar_extension(_ext(base, factor), BASE_HASTA, ahora_utc=congelar_en)
    try:
        return S.sellar(ruta, meta, ahora_utc=sellar_en, ruta_db=db, cfg=cfg)
    finally:
        if not meta.get("persistido", True) and os.path.exists(ruta):
            os.remove(ruta)


def _motivos(db, tabla):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return [r[0] for r in con.execute(f"SELECT motivo FROM {tabla} ORDER BY ticker")]
    finally:
        con.close()


def _columnas(db, tabla):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return tuple(c[1] for c in con.execute(f"PRAGMA table_info({tabla})"))
    finally:
        con.close()


# ------------------------------------------------------------
# (1) version_reglas
# ------------------------------------------------------------
def test_version_reglas_es_0_3_0_propuesta_con_su_nota_y_sin_mover_ninguna_regla():
    cfg = U.reglas()
    assert cfg["version_reglas"] == "0.3.0-PROPUESTA"
    nota = cfg.get("version_reglas_nota", "")
    assert "99.5" in nota and "0.3.0-PROPUESTA" in nota and "reglas_sha256" in nota
    assert cfg["exclusiones_insumo_e0"]["tickers"] == ["TOELY"]       # §95.4 intacta
    assert cfg["juego_activo"] == "conservador"
    assert cfg["juegos"]["conservador"]["umbral_senal_pp"] == 1.35      # las reglas numéricas las recomputa test_dinero


def test_la_huella_de_reglas_es_una_tercera_poblacion():
    """El sha del archivo cambia con la versión: las filas que selle llevan una
    huella distinta de las dos poblaciones ya selladas, y `reglas_version`
    las distingue sin cotejar hashes."""
    assert S._sha256(U.RUTA_REGLAS) not in HUELLAS_ANTERIORES


def test_una_fila_sellada_con_el_parche_declara_la_version_nueva(entorno_temporal, base):
    db = entorno_temporal
    r = _disparo(base, db, T_NOCHE, T_NOCHE)
    assert r["resultado"] == "sellada" and r["filas_insertadas"] == N_OPERABLES
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    versiones = {x[0] for x in con.execute("SELECT DISTINCT reglas_version FROM sellos_dinero")}
    huellas = {x[0] for x in con.execute("SELECT DISTINCT reglas_sha256 FROM sellos_dinero")}
    con.close()
    assert versiones == {"0.3.0-PROPUESTA"} and not (huellas & HUELLAS_ANTERIORES)


# ------------------------------------------------------------
# (2) R4: la exclusión revienta ante un ticker desconocido
# ------------------------------------------------------------
def test_R4_un_ticker_desconocido_en_la_exclusion_revienta_nombrandolo(base):
    cfg = json.loads(json.dumps(U.reglas()))
    cfg["exclusiones_insumo_e0"]["tickers"] = ["TOELLY"]
    with pytest.raises(ValueError, match="TOELLY"):
        S.decidir(base, base.index.max(), cfg)


def test_R4_toely_sigue_saliendo_y_sin_la_clave_todo_sigue_igual(base):
    dec = S.decidir(base, base.index.max())
    assert "TOELY" not in dec["operables"] and dec["excluidos_universo"] == ["TOELY"] and len(dec["operables"]) == N_OPERABLES
    cfg = json.loads(json.dumps(U.reglas()))
    del cfg["exclusiones_insumo_e0"]
    dec0 = S.decidir(base, base.index.max(), cfg)
    assert "TOELY" in dec0["operables"] and dec0["excluidos_universo"] == [] and len(dec0["operables"]) == N_OPERABLES + 1


def test_R4_un_ticker_del_universo_pero_fuera_del_censo_tambien_revienta(base):
    """El censo (`universo_operable`) deja fuera instrumentos que el congelado
    sí trae; declararlos en la exclusión es declarar algo que la regla no
    puede hacer, y se dice."""
    dec = S.decidir(base, base.index.max())
    fuera_del_censo = sorted(set(base.columns) - set(dec["operables"]) - {"TOELY"})
    if not fuera_del_censo:
        pytest.skip("el congelado no trae instrumentos fuera del censo")
    cfg = json.loads(json.dumps(U.reglas()))
    cfg["exclusiones_insumo_e0"]["tickers"] = ["TOELY", fuera_del_censo[0]]
    with pytest.raises(ValueError, match=fuera_del_censo[0]):
        S.decidir(base, base.index.max(), cfg)


# ------------------------------------------------------------
# (3) §81.3 b: el motivo de un intento lleva el instante del timing
# ------------------------------------------------------------
def test_las_filas_de_un_intento_llevan_el_instante_con_que_se_decidio_el_timing(entorno_temporal, base):
    """F2: la evidencia se congela a T1 (bolsa abierta) y se sella 2 s después
    a T2; el instante que decidió el timing es T1, el de congelar, y es el que
    la fila declara aunque sus tres columnas de tiempo digan otra cosa."""
    db = entorno_temporal
    t1, t2 = T_INTRADIA, T_INTRADIA + timedelta(seconds=2)
    r = _disparo(base, db, t1, t2)
    assert r["resultado"] == "intento_no_verificable" and r["filas_insertadas"] == N_OPERABLES
    motivos = _motivos(db, S.TABLA_INTENTOS)
    assert len(motivos) == N_OPERABLES
    for m in motivos:
        assert m and f"timing roto decidido al congelar la evidencia, a las {t1.isoformat()}" in m, m
        assert t2.isoformat() not in m
        assert "available_at" in m and "apertura objetivo" in m and "no se cumplía a ese instante" in m
    assert _motivos(db, S.TABLA_SELLOS) == []


def test_sin_bloque_timing_la_fila_cita_la_clase_de_la_evidencia_y_no_el_reloj_del_sello(entorno_temporal, base):
    """B1 del auditor 16-3. Una evidencia `.no_verificable` cuyo meta no trae el
    bloque `timing` (camino hoy no alcanzable por `main()`: `congelar_extension`
    siempre lo escribe) se sella a un instante en que la regla SÍ se cumple: el
    veredicto lo fijó la CLASE de la evidencia, y la fila no puede decir que la
    regla no se cumplía con el reloj del sello (una frase falsa en un campo
    inmutable). Cita el instante de congelar (`congelado_en_utc`) y la clase."""
    db = entorno_temporal
    ruta, meta = S.congelar_extension(_ext(base, 0.97), BASE_HASTA, ahora_utc=T_INTRADIA)
    meta_sin_timing = {k: v for k, v in meta.items() if k != "timing"}
    assert S.evaluar_timing((meta["disponibilidad"] or {}).get("por_ticker"), LUNES, T_NOCHE)["timing_ok"] is True
    r = S.sellar(ruta, meta_sin_timing, ahora_utc=T_NOCHE, ruta_db=db)
    assert r["resultado"] == "intento_no_verificable" and r["filas_insertadas"] == N_OPERABLES
    for m in _motivos(db, S.TABLA_INTENTOS):
        assert "timing roto decidido por la clase de la evidencia (" + os.path.basename(ruta) in m, m
        assert f"congelada a las {meta['congelado_en_utc']}" in m
        assert "no fijó el veredicto" in m and "no se cumple" not in m and "no se cumplía" not in m
        assert T_NOCHE.isoformat() in m          # el reloj del sello se declara como lo que es


def test_las_filas_de_un_sello_no_llevan_la_nota_del_timing(entorno_temporal, base):
    db = entorno_temporal
    r = _disparo(base, db, T_NOCHE, T_NOCHE)
    assert r["resultado"] == "sellada"
    motivos = _motivos(db, S.TABLA_SELLOS)
    assert len(motivos) == N_OPERABLES
    for m in motivos:
        assert not (m and "timing roto decidido" in m)


def test_en_un_intento_el_motivo_de_sin_dato_se_conserva_delante_de_la_nota(entorno_temporal, base):
    """E3 sigue mandando: el ticker sin cierre lo dice primero, y la nota del
    timing va detrás, separada por «; »."""
    db = entorno_temporal
    ext = _ext(base, 0.97)
    ext.loc[pd.Timestamp(LUNES), "SHECY"] = float("nan")
    ruta, meta = S.congelar_extension(ext, BASE_HASTA, ahora_utc=T_INTRADIA)
    r = S.sellar(ruta, meta, ahora_utc=T_INTRADIA, ruta_db=db)
    assert r["resultado"] == "intento_no_verificable" and r["sin_dato"] == ["SHECY"]
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    m_shecy = con.execute(f"SELECT motivo FROM {S.TABLA_INTENTOS} WHERE ticker = 'SHECY'").fetchone()[0]
    con.close()
    assert m_shecy.startswith("sin dato en el insumo para la sesión") and "; timing roto decidido al congelar la evidencia" in m_shecy


def test_sin_cambio_de_esquema_las_dos_tablas_tienen_las_columnas_de_head(entorno_temporal):
    con = S.conectar(entorno_temporal)
    con.close()
    assert _columnas(entorno_temporal, S.TABLA_SELLOS) == COLUMNAS_FILA
    assert _columnas(entorno_temporal, S.TABLA_INTENTOS) == COLUMNAS_FILA


# ------------------------------------------------------------
# (4) R2: estado() con el desglose por población
# ------------------------------------------------------------
def test_estado_sin_base_trae_el_desglose_vacio_y_las_claves_de_siempre(tmp_path):
    e = S.estado(str(tmp_path / "no_existe.db"))
    assert e["por_reglas_sha256"] == []
    assert {"filas", "sesiones_selladas", "sesiones_que_cuentan_para_N", "intentos_no_verificables", "ultimo_intento"} <= set(e)


def test_estado_desglosa_por_poblacion_y_la_suma_es_el_total(entorno_temporal, base, tmp_path, monkeypatch):
    """Dos poblaciones: se sella una sesión con el reglas.json del parche y
    otra con una copia de otra versión (otro sha). El desglose las separa, en
    orden de primera fecha, y suma el total de `estado()`."""
    db = entorno_temporal
    r1 = _disparo(base, db, T_NOCHE, T_NOCHE)
    assert r1["resultado"] == "sellada"
    otra = tmp_path / "reglas_otra.json"
    cfg2 = json.loads(json.dumps(U.reglas()))
    cfg2["version_reglas"] = "0.9.9-PRUEBA"
    otra.write_text(json.dumps(cfg2, indent=1, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(U, "RUTA_REGLAS", str(otra))
    martes = ("2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11", LUNES, "2026-09-15")
    ruta, meta = S.congelar_extension(_ext(base, 0.98, martes), BASE_HASTA, ahora_utc=T_NOCHE + timedelta(days=1))
    r2 = S.sellar(ruta, meta, ahora_utc=T_NOCHE + timedelta(days=1), ruta_db=db, cfg=cfg2)
    assert r2["resultado"] == "sellada"
    e = S.estado(db)
    pobl = e["por_reglas_sha256"]
    assert [p["reglas_version"] for p in pobl] == ["0.3.0-PROPUESTA", "0.9.9-PRUEBA"]
    assert [p["desde"] for p in pobl] == [LUNES, "2026-09-15"] and [p["hasta"] for p in pobl] == [LUNES, "2026-09-15"]
    assert sum(p["sesiones_selladas"] for p in pobl) == e["sesiones_selladas"] == 2
    assert sum(p["filas"] for p in pobl) == e["filas"] == 2 * N_OPERABLES
    assert sum(p["sesiones_que_cuentan_para_N"] for p in pobl) == e["sesiones_que_cuentan_para_N"]
    assert {p["reglas_sha256"] for p in pobl} == {r1["reglas_sha256"], r2["reglas_sha256"]}
    assert all(set(p) == {"reglas_sha256", "reglas_version", "sesiones_selladas", "sesiones_que_cuentan_para_N",
                          "filas", "desde", "hasta"} for p in pobl)


def test_estado_sobre_la_base_real_separa_las_poblaciones_ya_selladas():
    """`mode=ro`. Hoy la base real tiene dos poblaciones (33 operables hasta el
    2-oct; 32 sin TOELY desde el 5-oct) con la misma `reglas_version`: el
    desglose las separa por hash y suma el total. Se salta sin la base."""
    if not os.path.exists(S.RUTA_DB):
        pytest.skip(f"sin base real en {S.RUTA_DB}")
    e = S.estado(S.RUTA_DB)
    pobl = e["por_reglas_sha256"]
    assert len(pobl) >= 2
    assert sum(p["sesiones_selladas"] for p in pobl) == e["sesiones_selladas"]
    assert sum(p["filas"] for p in pobl) == e["filas"]
    assert sum(p["sesiones_que_cuentan_para_N"] for p in pobl) == e["sesiones_que_cuentan_para_N"]
    assert HUELLAS_ANTERIORES <= {p["reglas_sha256"] for p in pobl}      # por hash, no por posición (R2 del auditor)
    assert all(p["desde"] <= p["hasta"] for p in pobl)
    # las poblaciones ya selladas no se solapan en fechas (si una fecha anterior se sellara con
    # reglas nuevas, la nueva quedaría en medio y esto lo diría)
    rangos = sorted((p["desde"], p["hasta"]) for p in pobl)
    assert all(a[1] < b[0] for a, b in zip(rangos, rangos[1:])), rangos


def test_la_api_no_sirve_el_desglose_todavia_y_el_contrato_no_cambia():
    """R2 es aditivo en `estado()`; `/api/dinero/sellos` arma `E0` clave por
    clave y no lo expone: servirlo exige enmendar `api/CONTRATO.md` antes."""
    fuente = open(os.path.join(RAIZ, "api", "main.py"), encoding="utf-8").read()
    assert "por_reglas_sha256" not in fuente
    assert "por_reglas_sha256" not in open(os.path.join(RAIZ, "api", "CONTRATO.md"), encoding="utf-8").read()
