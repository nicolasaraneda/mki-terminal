"""Corrida 16-2 (11-oct-2026, actas §93.7 y §99.2): el camino T de §62 rebasado
sobre el sellador de la 16b (TOELY fuera, 32 operables).

Dos veces un disparo del sellador fuera de hora dejó una fecha «sellada» como
`no_verificable_timing` y le quitó la sesión a N = 40:
  · 28-sep-2026, 14:42:52 Chile (13:43 NY, bolsa abierta): el PC despertó de
    la suspensión; 33 filas rotas en `sellos_dinero`, `ext_2026-09-28.csv` con
    la matriz de media sesión; el disparo bueno de las 23:30 NY entró por
    divergencia con cero filas.
  · 7-oct-2026, 10:30:55 Chile (09:30 NY, un minuto después de abrir): el PC
    estuvo apagado a las 00:30 (corte de luz) y el timer (`Persistent=true`)
    disparó de recuperación al volver; 32 filas rotas con SHECY sin dato (el
    ADR de mostrador todavía no tenía barra); el disparo normal del 8-oct a
    las 00:30 encontró la fecha ocupada y escribió cero filas. La sesión del
    6-oct no tiene filas: el camino T no la habría salvado y acá se declara.

Lo que estos tests exigen, escritos ANTES de rebasar el parche y rojos sobre
HEAD por su propia aserción (no por un TypeError: `_congelar` adapta la
firma): (i) el 28-sep con los relojes reales; (ii) el 7-oct, con un ticker sin
dato; (iii) lo de la 16b sigue en pie con T: 32 operables, TOELY excluido en
las dos tablas, y un faltante distinto de TOELY sigue siendo incompleto también
en un intento; (iv) un disparo de recuperación en día SIN sesión con timing
ok sella en la tabla principal como `dia_sin_sesion` (igual que E0.2: T no
interviene). Base temporal en cada test: la real no se toca; los tests sobre
la base real van en `mode=ro` y se saltan sin ella."""
import inspect
import json
import os
import sqlite3
from datetime import datetime, timezone

import pandas as pd
import pytest

from dinero import precios
from dinero import sello_dinero as S

UTC = timezone.utc
N_OPERABLES = 32          # 33 hasta la corrida 16b; TOELY fuera del insumo de E0 desde el 5-oct-2026 (acta §95.4)
EXCLUIDO = "TOELY"
SIN_BARRA = "SHECY"       # el ticker sin dato del disparo de recuperación del 7-oct
BASE_HASTA = "2026-09-04"
# Sesiones sintéticas: lunes 14-sep (análogo del 28-sep y del 6-oct) y martes 15-sep (análogo del 7-oct)
LUNES, MARTES, MIERCOLES = "2026-09-14", "2026-09-15", "2026-09-16"
SESIONES_HASTA_LUNES = ("2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11", LUNES)
SESIONES_HASTA_MARTES = SESIONES_HASTA_LUNES + (MARTES,)
T_28SEP = datetime(2026, 9, 14, 17, 43, 1, tzinfo=UTC)       # 14:43:01 Chile = 13:43 NY, bolsa abierta
T_NOCHE_LUNES = datetime(2026, 9, 15, 3, 30, 4, tzinfo=UTC)  # 23:30 NY del lunes: el timer
T_7OCT = datetime(2026, 9, 15, 13, 31, 4, tzinfo=UTC)        # 10:31:04 Chile = 09:31 NY del martes: recuperación
T_NOCHE_MARTES = datetime(2026, 9, 16, 3, 30, 4, tzinfo=UTC) # 23:30 NY del martes: el timer
T_SABADO = datetime(2026, 9, 12, 14, 0, tzinfo=UTC)          # sábado 10:00 NY: recuperación en día sin sesión
TABLA_INTENTOS = "intentos_no_verificables"


@pytest.fixture(scope="module")
def base():
    return precios.cargar_congelado()


@pytest.fixture
def entorno_temporal(tmp_path, monkeypatch):
    """Carpeta de evidencia, base, respaldo y CSV versionado: todos en tmp."""
    db = str(tmp_path / "sello_dinero.db")
    monkeypatch.setattr(S, "DIR_EXT", str(tmp_path / "datos" / "sello"))
    monkeypatch.setattr(S, "RUTA_DB", db)
    monkeypatch.setattr(S, "DIR_BACKUP_EXT", str(tmp_path / "backups_ext"))
    monkeypatch.setattr(S, "RUTA_BACKUP_CSV", str(tmp_path / "sello_dinero.csv"))
    return db


def _ext(base, sesiones, factor_ultima, sin_dato=()):
    """Lo que `descargar_extension()` devolvería: historia × 1.01 y la última
    sesión × `factor_ultima` (la barra intradía y el cierre difieren sólo en
    la última fila, como el 28-sep y el 7-oct); `sin_dato` deja NaN esos
    tickers en la última sesión (el ADR sin barra a las 09:31 NY)."""
    ult = base.iloc[-1]
    ext = pd.DataFrame({pd.Timestamp(s): ult * 1.01 for s in sesiones}).T
    ext.iloc[-1] = ult.values * factor_ultima
    for t in sin_dato:
        ext.loc[pd.Timestamp(sesiones[-1]), t] = float("nan")
    ext.index.name = "Date"
    return ext


def _congelar(cierres_ext, ahora):
    """Sobre HEAD `congelar_extension` no recibe el instante (no mira el reloj:
    por eso ocupó el cupo canónico el 28-sep y el 7-oct); se la llama sin él
    para que la reproducción falle en HEAD por su aserción y no por TypeError."""
    if "ahora_utc" in inspect.signature(S.congelar_extension).parameters:
        return S.congelar_extension(cierres_ext, BASE_HASTA, ahora_utc=ahora)
    return S.congelar_extension(cierres_ext, BASE_HASTA)


def _disparo(cierres_ext, db, ahora):
    """El camino de `main()`: congelar en disco, sellar, borrar el temporal."""
    assert os.path.abspath(S.RUTA_DB) == os.path.abspath(db)
    ruta, meta = _congelar(cierres_ext, ahora)
    try:
        return ruta, meta, S.sellar(ruta, meta, ahora_utc=ahora, ruta_db=db)
    finally:
        if not meta.get("persistido", True) and os.path.exists(ruta):
            os.remove(ruta)


def _cuenta(db, tabla) -> int:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    except sqlite3.OperationalError:
        return 0
    finally:
        con.close()


def _tickers(db, tabla, fecha) -> list:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return [r[0] for r in con.execute(f"SELECT DISTINCT ticker FROM {tabla} WHERE fecha_insumo = ? ORDER BY ticker",
                                          (fecha,)).fetchall()]
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()


# ------------------------------------------------------------
# (i) El 28-sep con los relojes reales, sobre el sellador de la 16b
# ------------------------------------------------------------
def test_reproduccion_28sep_con_los_relojes_reales_el_disparo_bueno_sella_32_sin_toely(entorno_temporal, base):
    db = entorno_temporal
    ruta1, meta1, r1 = _disparo(_ext(base, SESIONES_HASTA_LUNES, 0.98), db, T_28SEP)
    assert r1["timing_ok"] is False and r1["estado"] == "no_verificable_timing" and r1["cuenta_para_N"] == 0
    assert r1["filas_insertadas"] == N_OPERABLES and r1["excluidos_universo"] == [EXCLUIDO]

    ruta2, meta2, r2 = _disparo(_ext(base, SESIONES_HASTA_LUNES, 1.02), db, T_NOCHE_LUNES)
    assert meta2["sha256"] != meta1["sha256"]
    assert r2["resultado"] == "sellada", (
        "EL 28-SEP: el disparo bueno de las 23:30 NY no selló porque la fecha quedó ocupada por el intento "
        f"de la bolsa abierta (resultado={r2['resultado']!r}, filas_insertadas={r2.get('filas_insertadas')})")
    assert r2["estado"] == "pendiente" and r2["cuenta_para_N"] == 1 and r2["filas_insertadas"] == N_OPERABLES
    assert r2["insumo_completo"] is True and r2["excluidos_universo"] == [EXCLUIDO] and r2["sesion_objetivo"] == MARTES

    assert r1["resultado"] == "intento_no_verificable" and r1["tabla"] == TABLA_INTENTOS
    assert _cuenta(db, "sellos_dinero") == _cuenta(db, TABLA_INTENTOS) == N_OPERABLES
    assert _cuenta(db, "divergencias_sello") == 0
    assert EXCLUIDO not in _tickers(db, "sellos_dinero", LUNES) and EXCLUIDO not in _tickers(db, TABLA_INTENTOS, LUNES)
    assert os.path.basename(ruta1) == f"ext_{LUNES}.no_verificable.csv" and os.path.basename(ruta2) == f"ext_{LUNES}.csv"
    assert S.sello_previo(LUNES, db) == {"sha256": meta2["sha256"], "archivo": f"ext_{LUNES}.csv"}
    assert S.intento_previo(LUNES, db) == {"sha256": meta1["sha256"], "archivo": f"ext_{LUNES}.no_verificable.csv"}


# ------------------------------------------------------------
# (ii) El 7-oct: disparo de recuperación a las 09:31 NY del día siguiente,
#      con un ticker sin barra; la sesión anterior (6-oct) queda sin filas
# ------------------------------------------------------------
def test_reproduccion_7oct_la_recuperacion_de_la_manana_no_quema_la_sesion_del_dia(entorno_temporal, base):
    db = entorno_temporal
    # la noche del lunes el PC estaba apagado: ningún disparo con fecha_insumo = LUNES
    ruta1, meta1, r1 = _disparo(_ext(base, SESIONES_HASTA_MARTES, 0.99, sin_dato=(SIN_BARRA,)), db, T_7OCT)
    assert r1["fecha_insumo"] == MARTES and r1["fecha_sello_ny"] == MARTES
    assert r1["available_at"] == f"{MARTES}T20:00:00+00:00"            # el cierre por calendario, futuro respecto del disparo
    assert r1["apertura_objetivo_utc"].startswith(f"{MIERCOLES}T13:30") and r1["sesion_objetivo"] == MIERCOLES
    assert r1["timing_ok"] is False and r1["estado"] == "no_verificable_timing" and r1["estado_timing"] == "roto"
    assert r1["insumo_completo"] is False and r1["sin_dato"] == [SIN_BARRA] and r1["cuenta_para_N"] == 0
    assert r1["filas_insertadas"] == N_OPERABLES and r1["excluidos_universo"] == [EXCLUIDO]

    # el disparo normal de las 23:30 NY del martes, con el cierre completo
    ruta2, meta2, r2 = _disparo(_ext(base, SESIONES_HASTA_MARTES, 1.02), db, T_NOCHE_MARTES)
    assert meta2["sha256"] != meta1["sha256"]
    assert r2["resultado"] == "sellada", (
        "EL 7-OCT: el disparo normal de las 23:30 NY no selló porque la fecha quedó ocupada por el disparo de "
        f"recuperación de la mañana (resultado={r2['resultado']!r}, filas_insertadas={r2.get('filas_insertadas')})")
    assert r2["estado"] == "pendiente" and r2["cuenta_para_N"] == 1 and r2["filas_insertadas"] == N_OPERABLES
    assert r2["insumo_completo"] is True and r2["sin_dato"] == [] and r2["sesion_objetivo"] == MIERCOLES

    # con T: el intento en su tabla con SHECY sin dato, el sello en la principal, ninguna divergencia
    assert r1["resultado"] == "intento_no_verificable" and r1["tabla"] == TABLA_INTENTOS
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    intento = con.execute(f"SELECT DISTINCT estado, insumo_completo, cuenta_para_N, insumo_ext_archivo FROM {TABLA_INTENTOS}").fetchall()
    sin_barra = con.execute(f"SELECT ultimo_cierre_ticker, motivo FROM {TABLA_INTENTOS} WHERE ticker = ?", (SIN_BARRA,)).fetchone()
    sello = con.execute("SELECT DISTINCT fecha_insumo, estado, insumo_completo, cuenta_para_N FROM sellos_dinero").fetchall()
    con.close()
    assert intento == [("no_verificable_timing", 0, 0, f"ext_{MARTES}.no_verificable.csv")]
    assert sin_barra[0] == LUNES and "sin dato en el insumo" in sin_barra[1]
    assert sello == [(MARTES, "pendiente", 1, 1)]
    assert _cuenta(db, "divergencias_sello") == 0

    # lo que T NO salva, declarado: la sesión del lunes (6-oct) no tiene filas en ninguna tabla
    assert S.sello_previo(LUNES, db) is None and S.intento_previo(LUNES, db) is None
    assert _tickers(db, "sellos_dinero", LUNES) == [] and _tickers(db, TABLA_INTENTOS, LUNES) == []
    e = S.estado(db)
    assert e["sesiones_selladas"] == 1 and e["sesiones_que_cuentan_para_N"] == 1 and e["intentos_no_verificables"] == 1
    # el disco: el canónico es el cierre, el par .no_verificable es la barra de la mañana
    assert sorted(os.listdir(S.DIR_EXT)) == [f"ext_{MARTES}.csv", f"ext_{MARTES}.meta.json",
                                             f"ext_{MARTES}.no_verificable.csv", f"ext_{MARTES}.no_verificable.meta.json"]
    with open(os.path.join(S.DIR_EXT, f"ext_{MARTES}.no_verificable.meta.json"), encoding="utf-8") as f:
        meta_nv = json.load(f)
    assert meta_nv["cupo_canonico"] is False and meta_nv["timing"]["emision_utc"] == T_7OCT.isoformat()
    assert meta_nv["timing"]["available_at"] == f"{MARTES}T20:00:00+00:00"


# ------------------------------------------------------------
# (iii) Lo de la 16b sigue en pie con T
# ------------------------------------------------------------
def test_toely_tampoco_entra_a_la_tabla_de_intentos_y_su_ausencia_no_vuelve_incompleto_un_intento(entorno_temporal, base):
    """La exclusión se aplica en `decidir`, antes de elegir la tabla: TOELY no
    aparece en `intentos_no_verificables`, y que TOELY no tenga barra (como
    el 28-sep) no es un faltante. Un intento con sólo TOELY sin dato lleva
    `insumo_completo = 1` igual que lo haría un sello."""
    db = entorno_temporal
    ruta, meta, r = _disparo(_ext(base, SESIONES_HASTA_LUNES, 0.98, sin_dato=(EXCLUIDO,)), db, T_28SEP)
    assert r["resultado"] == "intento_no_verificable"
    assert r["insumo_completo"] is True and r["sin_dato"] == [] and r["excluidos_universo"] == [EXCLUIDO]
    assert r["filas_insertadas"] == N_OPERABLES and EXCLUIDO not in _tickers(db, TABLA_INTENTOS, LUNES)
    assert len(_tickers(db, TABLA_INTENTOS, LUNES)) == N_OPERABLES
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    assert con.execute(f"SELECT DISTINCT insumo_completo FROM {TABLA_INTENTOS}").fetchall() == [(1,)]
    con.close()


def test_un_faltante_distinto_de_toely_sigue_siendo_incompleto_tambien_en_un_intento(entorno_temporal, base):
    db = entorno_temporal
    _, _, r = _disparo(_ext(base, SESIONES_HASTA_LUNES, 0.98, sin_dato=("AMD", EXCLUIDO)), db, T_28SEP)
    assert r["resultado"] == "intento_no_verificable" and r["estado"] == "no_verificable_timing"
    assert r["insumo_completo"] is False and r["sin_dato"] == ["AMD"]           # TOELY nunca aparece
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    assert con.execute(f"SELECT DISTINCT insumo_completo FROM {TABLA_INTENTOS}").fetchall() == [(0,)]
    con.close()


# ------------------------------------------------------------
# (iv) Recuperación en un día SIN sesión: T no interviene
# ------------------------------------------------------------
def test_una_recuperacion_en_sabado_con_el_cierre_del_viernes_sella_dia_sin_sesion_en_la_principal(entorno_temporal, base):
    """Si el PC estuvo apagado el viernes a las 23:30 NY y el timer dispara de
    recuperación el sábado con el cierre completo del viernes, el timing está
    OK (viernes 20:00Z < sábado < lunes 13:30Z): la fila va a `sellos_dinero`
    como `dia_sin_sesion`, `cuenta_para_N = 0` (regla E2/E8, §57 firmada tal
    como está en el código), y la fecha queda ocupada: igual que en E0.2, el
    camino T sólo actúa con timing roto. Pasa también sobre HEAD (control)."""
    db = entorno_temporal
    viernes = "2026-09-11"
    _, _, r = _disparo(_ext(base, SESIONES_HASTA_LUNES[:4], 1.02), db, T_SABADO)
    assert r["resultado"] == "sellada" and r["fecha_insumo"] == viernes
    assert r["timing_ok"] is True and r["estado_dia"] == "sin_sesion" and r["estado"] == "dia_sin_sesion"
    assert r["cuenta_para_N"] == 0 and r["sesion_objetivo"] == LUNES and r["filas_insertadas"] == N_OPERABLES
    assert _cuenta(db, "sellos_dinero") == N_OPERABLES and _cuenta(db, TABLA_INTENTOS) == 0
    assert S.sello_previo(viernes, db) is not None


# ------------------------------------------------------------
# La base real, en mode=ro: las dos fechas quemadas se quedan donde están
# ------------------------------------------------------------
def test_sobre_la_base_real_las_fechas_quemadas_siguen_en_la_principal_con_version_anterior_al_corte():
    """Las filas `no_verificable_timing` de la tabla principal son todas de un
    sellador anterior a E0.3 y siguen ocupando su fecha (`sello_previo` las
    devuelve): el camino T no las toca ni recupera esas sesiones (§57, §86.1).
    No nombra ninguna fecha: cuenta lo que hay."""
    if not os.path.exists(S.RUTA_DB):
        pytest.skip("sin base real en este checkout: nada que verificar")
    con = S.conectar(S.RUTA_DB, solo_lectura=True)
    try:
        rotas = con.execute("SELECT DISTINCT fecha_insumo, version_sello FROM sellos_dinero "
                            "WHERE estado = 'no_verificable_timing' ORDER BY fecha_insumo").fetchall()
    finally:
        con.close()
    if not rotas:
        pytest.skip("la base real no tiene filas rotas en la principal")
    assert all(tuple(int(x) for x in v.lstrip("E").split(".")) < (0, 3) for _, v in rotas), rotas
    for fecha, _ in rotas:
        assert S.sello_previo(fecha) is not None
