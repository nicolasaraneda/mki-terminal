"""Corrida 12, bloque 3 — E0: el sellador prospectivo del riel de dinero.

Lo que estos tests exigen, campo por campo, es lo que el `auditor-lookahead`
pidió antes del primer sello (dictamen_12/auditor_lookahead_sello_dinero.md,
E1–E8): que el valor de cada campo en t no cambie si se borra el futuro; que
el gate NO sea vacuo; que la fila no se pueda reescribir; que `available_at`
sea el cierre por calendario y no el reloj de pared; que el orden
available_at < timestamp_utc < apertura objetivo se exija; que el «día» del
sello salga del calendario de Nueva York y no del huso del host; que la
disponibilidad se selle por ticker y un insumo incompleto no cuente para N;
que un segundo sello con otro insumo deje rastro; que exportar desde una base
temporal no pueda pisar el CSV real; y que el tamaño nominal sea cero
siempre. Base temporal en cada test: `sello_dinero.db` real no se toca."""
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from dinero import precios
from dinero import sello_dinero as S

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UTC = timezone.utc


@pytest.fixture(scope="module")
def base():
    return precios.cargar_congelado()


def _extension_sintetica(tmp_path, base, sesiones=("2026-09-08",), factor=1.01, sin_dato=()):
    """Una extensión con las sesiones dadas, precios = último cierre × factor,
    con su meta (disponibilidad G8) y sha256, escrita como la real. `sin_dato`
    deja NaN esos tickers en la última sesión (publicación asincrónica)."""
    ult = base.iloc[-1]
    filas = {pd.Timestamp(s): ult * factor for s in sesiones}
    ext = pd.DataFrame(filas).T
    for t in sin_dato:
        ext.loc[pd.Timestamp(sesiones[-1]), t] = float("nan")
    ext.index.name = "Date"
    ruta = str(tmp_path / f"ext_{sesiones[-1]}.csv")
    ext.to_csv(ruta)
    meta = {"sha256": S._sha256(ruta), "hasta": sesiones[-1], "tickers": list(ext.columns),
            "desde": sesiones[0], "extiende_a": {"hasta": "2026-09-04"},
            "disponibilidad": {"exchange": "XNYS", "por_ticker": precios.disponibilidad_por_ticker(ext)}}
    with open(ruta.replace(".csv", ".meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f)
    return ruta, meta


# ------------------------------------------------------------
# 1. La decisión es función pura del pasado; el gate no es vacuo
# ------------------------------------------------------------
def test_la_decision_del_dia_no_cambia_si_se_borra_el_futuro(base):
    for dia in ("2026-08-20", "2026-06-15", "2025-11-03"):
        g = S.verificar_invariancia_decision(base, dia, futuros=5)
        assert g["resultado"] == "INVARIANTE" and g["cortes"] == 6


def test_contraprueba_una_decision_que_mira_manana_rompe_el_gate(base, monkeypatch):
    """Un gate que no puede fallar no es un gate: si `decidir` usara el cierre
    de d+1 como precio de referencia (la fuga G3), el gate tiene que verlo."""
    from backtest.datos import ErrorLookAhead
    original = S.decidir

    def con_fuga(cierres, dia, cfg=None, juego=None, presupuesto=None):
        idx = cierres.index
        pos = idx.get_indexer([pd.Timestamp(dia)])[0]
        if pos + 1 < len(idx):
            tramp = cierres.copy()
            tramp.iloc[pos] = cierres.iloc[pos + 1].values
            return original(tramp, dia, cfg, juego, presupuesto)
        return original(cierres, dia, cfg, juego, presupuesto)

    monkeypatch.setattr(S, "decidir", con_fuga)
    with pytest.raises(ErrorLookAhead):
        S.verificar_invariancia_decision(base, "2026-08-20", futuros=3)


def test_E1_el_gate_en_el_ultimo_dia_es_vacuo_y_lo_dice(base):
    """H1 del auditor: en el último día hay un solo corte y el gate comparaba
    la decisión consigo misma. Ahora revienta en vez de fingir."""
    from backtest.datos import ErrorLookAhead
    with pytest.raises(ErrorLookAhead, match="VACUO"):
        S.verificar_invariancia_decision(base, base.index.max())


def test_E1_el_gate_previo_al_sello_vigila_el_penultimo_y_seis_atras(base):
    gates = S.gate_previo_al_sello(base)
    assert [g["cortes"] for g in gates] == [2, 6]
    assert all(g["resultado"] == "INVARIANTE" for g in gates)


def test_decidir_exige_que_el_dia_tenga_dato(base):
    with pytest.raises(ValueError, match="no tiene la sesión"):
        S.decidir(base, "2026-09-07")   # feriado: no hay cierre


def test_la_decision_declara_su_fuente_su_presupuesto_y_la_disponibilidad_por_ticker(base):
    d = S.decidir(base, "2026-09-04")
    assert d["juego"] == "conservador" and d["presupuesto_usd"] == 500.0
    assert len(d["filas"]) == len(d["operables"]) == 33
    assert d["insumo_completo"] is True and d["sin_dato"] == []
    assert all(f["decision"] in ("compra", "venta", "nada") for f in d["filas"])
    assert all(f["motivo"] for f in d["filas"] if f["decision"] == "nada")
    assert all(f["ultimo_cierre_ticker"] == "2026-09-04" and f["available_at_ticker"] == "2026-09-04T20:00:00+00:00"
               for f in d["filas"])
    assert "sin información" in S.SENAL_FUENTE and "no track record" in S.SENAL_FUENTE


# ------------------------------------------------------------
# 2. Sellar: timing, huso, disponibilidad, divergencia, inmutabilidad
# ------------------------------------------------------------
def test_sellar_pone_available_at_por_calendario_y_exige_el_orden(tmp_path, base):
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-08",))
    db = str(tmp_path / "s.db")
    ahora = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)          # 23:00 NY del 8-sep (día con sesión)
    r = S.sellar(ruta, meta, ahora_utc=ahora, ruta_db=db)
    assert r["resultado"] == "sellada"
    assert r["available_at"] == "2026-09-08T20:00:00+00:00"            # cierre NYSE por calendario, no el reloj
    assert r["available_at"] != r["timestamp_utc"]
    assert r["sesion_objetivo"] == "2026-09-09" and r["apertura_objetivo_utc"].startswith("2026-09-09T13:30")
    assert datetime.fromisoformat(r["available_at"]) < ahora < datetime.fromisoformat(r["apertura_objetivo_utc"])
    assert r["estado"] == "pendiente" and r["cuenta_para_N"] == 1
    assert r["insumo_fresco"] is True and r["insumo_completo"] is True
    assert r["fecha_sello_ny"] == "2026-09-08" and r["estado_dia"] == "sesion" and r["estado_timing"] == "ok"
    assert r["filas_insertadas"] == r["filas_decididas"] == 33
    con = sqlite3.connect(db)
    assert con.execute("SELECT DISTINCT tamano_nominal FROM sellos_dinero").fetchall() == [(0,)]
    assert con.execute("SELECT DISTINCT insumo_ext_sha256 FROM sellos_dinero").fetchone()[0] == meta["sha256"]
    assert con.execute("SELECT DISTINCT plataforma_version FROM sellos_dinero").fetchone()[0] == S.PLATAFORMA_VERSION
    assert con.execute("SELECT DISTINCT reglas_sha256 FROM sellos_dinero").fetchone()[0] == S._sha256(
        os.path.join(RAIZ, "dinero", "reglas.json"))
    assert con.execute("SELECT DISTINCT sellador_sha256 FROM sellos_dinero").fetchone()[0] == S._sha256(S.__file__)
    assert con.execute("SELECT DISTINCT ultimo_cierre_ticker FROM sellos_dinero").fetchall() == [("2026-09-08",)]
    con.close()


def test_sellar_despues_de_la_apertura_queda_no_verificable(tmp_path, base):
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-08",))
    tarde = datetime(2026, 9, 9, 14, 0, tzinfo=UTC)          # media hora después de abrir
    r = S.sellar(ruta, meta, ahora_utc=tarde, ruta_db=str(tmp_path / "s.db"))
    assert r["timing_ok"] is False and r["estado"] == "no_verificable_timing" and r["cuenta_para_N"] == 0
    assert r["estado_timing"] == "roto"


def test_E2_el_dia_del_sello_sale_del_calendario_de_nueva_york_no_del_host(tmp_path, base):
    """H4 del auditor: sábado 00:30 Chile ES viernes 23:30 en Nueva York. La
    misma información sellada a las 20:30 o a las 00:30 de Chile tiene que
    contar igual, y no puede depender de TZ del proceso."""
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-11",))
    r1 = S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 11, 23, 30, tzinfo=UTC), ruta_db=str(tmp_path / "a.db"))
    r2 = S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 12, 3, 30, tzinfo=UTC), ruta_db=str(tmp_path / "b.db"))
    assert r1["fecha_sello_ny"] == r2["fecha_sello_ny"] == "2026-09-11"
    assert r1["estado_dia"] == r2["estado_dia"] == "sesion"
    assert r1["cuenta_para_N"] == r2["cuenta_para_N"] == 1
    assert r1["sesion_objetivo"] == "2026-09-14"


def test_un_dia_sin_sesion_se_sella_con_su_marca_y_no_cuenta_para_N(tmp_path, base):
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-11",))
    sabado_ny = datetime(2026, 9, 12, 16, 0, tzinfo=UTC)     # sábado 12:00 en Nueva York
    r = S.sellar(ruta, meta, ahora_utc=sabado_ny, ruta_db=str(tmp_path / "s.db"))
    assert r["estado_dia"] == "sin_sesion" and r["estado"] == "dia_sin_sesion" and r["cuenta_para_N"] == 0
    assert r["timing_ok"] is True and r["sesion_objetivo"] == "2026-09-14"
    assert r["filas_insertadas"] == 33                                  # se sella igual


def test_un_insumo_desactualizado_no_cuenta_para_N(tmp_path, base):
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-04",), factor=1.0)
    r = S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 9, 3, 0, tzinfo=UTC), ruta_db=str(tmp_path / "s.db"))
    assert r["sesion_objetivo"] == "2026-09-08"     # lo siguiente a available_at (4-sep 20:00Z)
    assert r["timing_ok"] is False and r["cuenta_para_N"] == 0


def test_E3_un_insumo_incompleto_lo_dice_por_ticker_y_no_cuenta_para_N(tmp_path, base):
    """H3 del auditor: publicación asincrónica. 32 tickers sin la última
    sesión no pueden contar como un día completo, y el motivo de la fila no
    puede atribuir a la señal lo que fue falta de dato."""
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-08",), sin_dato=("AMD", "KLAC"))
    r = S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 9, 3, 0, tzinfo=UTC), ruta_db=str(tmp_path / "s.db"))
    assert r["insumo_completo"] is False and set(r["sin_dato"]) == {"AMD", "KLAC"}
    assert r["estado"] == "insumo_incompleto" and r["cuenta_para_N"] == 0
    con = sqlite3.connect(str(tmp_path / "s.db"))
    filas = dict(con.execute("SELECT ticker, motivo FROM sellos_dinero WHERE ticker IN ('AMD','KLAC')").fetchall())
    assert all("sin dato en el insumo" in m for m in filas.values())
    assert con.execute("SELECT ultimo_cierre_ticker FROM sellos_dinero WHERE ticker='AMD'").fetchone()[0] == "2026-09-04"
    assert con.execute("SELECT ultimo_cierre_ticker FROM sellos_dinero WHERE ticker='NVDA'").fetchone()[0] == "2026-09-08"
    con.close()


def test_las_filas_selladas_no_se_reescriben_ni_se_borran(tmp_path, base):
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-08",))
    db = str(tmp_path / "s.db")
    S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 9, 3, 0, tzinfo=UTC), ruta_db=db)
    con = sqlite3.connect(db)
    with pytest.raises(sqlite3.IntegrityError, match="no se reescriben"):
        con.execute("UPDATE sellos_dinero SET decision = 'compra'")
    with pytest.raises(sqlite3.IntegrityError, match="no se borran"):
        con.execute("DELETE FROM sellos_dinero")
    con.close()


def test_sellar_es_idempotente_con_el_mismo_insumo(tmp_path, base):
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-08",))
    db = str(tmp_path / "s.db")
    t = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)
    r1 = S.sellar(ruta, meta, ahora_utc=t, ruta_db=db)
    r2 = S.sellar(ruta, meta, ahora_utc=t + timedelta(minutes=5), ruta_db=db)
    assert r1["filas_insertadas"] == 33
    assert r2["resultado"] == "ya_sellada" and r2["filas_insertadas"] == 0
    assert "estado" not in r2 and "cuenta_para_N" not in r2     # no describe un sello que no ocurrió
    e = S.estado(db)
    assert e["filas"] == 33 and e["sesiones_selladas"] == 1 and e["sesiones_que_cuentan_para_N"] == 1
    assert e["N_objetivo"] == 40 and "acta §84.4.7" in e["N_objetivo_fuente"]
    assert e["ultimo"]["timestamp_utc"] == r1["timestamp_utc"] and e["divergencias_registradas"] == 0


def test_E4_un_segundo_sello_con_otro_insumo_deja_rastro_y_no_inserta(tmp_path, base):
    """H5 del auditor: el mismo día con OTRA extensión no se ignora en silencio."""
    ruta_a, meta_a = _extension_sintetica(tmp_path, base, ("2026-09-08",), factor=1.01)
    dir_b = tmp_path / "b"; dir_b.mkdir()
    ruta_b, meta_b = _extension_sintetica(dir_b, base, ("2026-09-08",), factor=1.03)
    assert meta_a["sha256"] != meta_b["sha256"]
    db = str(tmp_path / "s.db")
    t = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)
    S.sellar(ruta_a, meta_a, ahora_utc=t, ruta_db=db)
    r = S.sellar(ruta_b, meta_b, ahora_utc=t + timedelta(minutes=1), ruta_db=db)
    assert r["resultado"] == "divergencia_registrada" and r["filas_insertadas"] == 0
    assert r["sha_sellado"] == meta_a["sha256"] and r["sha_nuevo"] == meta_b["sha256"]
    con = sqlite3.connect(db)
    assert con.execute("SELECT COUNT(*) FROM sellos_dinero").fetchone()[0] == 33
    assert con.execute("SELECT COUNT(*) FROM divergencias_sello").fetchone()[0] == 1
    assert con.execute("SELECT DISTINCT insumo_ext_sha256 FROM sellos_dinero").fetchone()[0] == meta_a["sha256"]
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("DELETE FROM divergencias_sello")
    con.close()
    assert S.estado(db)["divergencias_registradas"] == 1


def test_E5_exportar_desde_una_base_temporal_exige_ruta_y_reproduce_la_tabla(tmp_path, base):
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-08",))
    db = str(tmp_path / "s.db")
    S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 9, 3, 0, tzinfo=UTC), ruta_db=db)
    with pytest.raises(ValueError, match="ruta_csv"):
        S.exportar_csv(db)                                   # H8: jamás pisa el CSV versionado
    csvp = S.exportar_csv(db, str(tmp_path / "b.csv"))
    df = pd.read_csv(csvp)
    assert len(df) == 33 and set(df["tamano_nominal"]) == {0} and "insumo_ext_sha256" in df.columns
    assert os.path.exists(str(tmp_path / "b_divergencias.csv"))
    copias = S.respaldar_extension(ruta, str(tmp_path / "bk"))
    assert len(copias) == 2 and S._sha256(copias[0]) == meta["sha256"]


def test_E7_el_solape_contra_el_congelado_detecta_un_reajuste(base):
    """Un split 2:1 en la descarga nueva sobre sesiones que el congelado ya
    tiene se declara en el meta; sin reajuste, dif_rel_max ≈ 0."""
    ult = base.tail(3).copy()
    limpio = S._solape_contra_congelado(ult, "2026-09-04")
    assert limpio["sesiones"] == 3 and limpio["reajuste_detectado"] is False
    sucio = ult.copy(); sucio["NVDA"] = sucio["NVDA"] / 2.0
    r = S._solape_contra_congelado(sucio, "2026-09-04")
    assert r["reajuste_detectado"] is True and r["tickers_con_reajuste"] == ["NVDA"]
    assert S._solape_contra_congelado(ult.iloc[0:0], "2026-09-04")["reajuste_detectado"] is None


def test_la_extension_real_si_existe_es_consistente_con_su_meta():
    """Cuando ya hubo un sello real, su extensión congelada tiene que
    coincidir con su sha256 y su disponibilidad por ticker (G8), y su copia
    en data/backups/ (E5) tiene que ser idéntica."""
    u = S.ultima_extension()
    if u is None:
        pytest.skip("todavía no hay extensión congelada")
    ruta, meta = u
    assert S._sha256(ruta) == meta["sha256"]
    ext = pd.read_csv(ruta, index_col=0, parse_dates=True)
    assert precios.disponibilidad_por_ticker(ext) == meta["disponibilidad"]["por_ticker"]
    assert pd.Timestamp(meta["desde"]) > pd.Timestamp(meta["extiende_a"]["hasta"])
    copia = os.path.join(S.DIR_BACKUP_EXT, os.path.basename(ruta))
    assert os.path.exists(copia) and S._sha256(copia) == meta["sha256"]


# ------------------------------------------------------------
# 3. E4-bis (corrida 13): el ARCHIVO de la extensión sellada tampoco se toca
# ------------------------------------------------------------
# El 10-sep-2026 03:30 UTC el timer disparó sobre el 09-sep ya sellado con
# otro insumo. `sellar()` registró la divergencia y no insertó nada (E4),
# pero `main()` ya había llamado a `congelar_extension()`, que pisó
# `ext_2026-09-09.csv` + meta con el insumo nuevo: nueve días el disco tuvo
# el sha 7300787b… mientras las filas citaban 126e4f2c…. Estos tests recorren
# el camino de `main()` (congelar + sellar), no sólo `sellar`. Los tres
# primeros (`test_E4_archivo_*`) los escribió el `auditor-lookahead` ANTES de
# la corrección y fallaban (dictamen_13/auditor_e4_archivo.md); los demás
# fijan la forma de la corrección que el auditor dictaminó (opción A: con la
# fecha ya sellada no se escribe NINGÚN archivo de esa fecha en DIR_EXT).
BASE_HASTA = "2026-09-04"        # última sesión del congelado grande
FECHA = "2026-09-08"             # primera sesión posterior (el 7-sep es feriado)


def _cierres_ext_sinteticos(base, sesiones=(FECHA,), factor=1.01) -> pd.DataFrame:
    """Lo que `descargar_extension()` devolvería: cierres crudos SIN recortar
    (es `congelar_extension` quien recorta a lo posterior a `base_hasta`).
    Último cierre del congelado × factor; dos factores distintos = dos insumos
    distintos, igual que dos descargas de Yahoo en la misma noche."""
    ult = base.iloc[-1]
    ext = pd.DataFrame({pd.Timestamp(s): ult * factor for s in sesiones}).T
    ext.index.name = "Date"
    return ext


def _camino_main(cierres_ext, db, ahora, base_hasta=BASE_HASTA):
    """El camino que recorre `main()`: congela la extensión EN DISCO, sella y
    borra el temporal de un insumo divergente no conservado."""
    ruta, meta = S.congelar_extension(cierres_ext, base_hasta)
    try:
        return ruta, meta, S.sellar(ruta, meta, ahora_utc=ahora, ruta_db=db)
    finally:
        if not meta.get("persistido", True) and os.path.exists(ruta):
            os.remove(ruta)


def _huella_ext(fecha=FECHA) -> dict:
    """(sha256, mtime_ns) de los archivos CANÓNICOS de esa fecha en S.DIR_EXT.
    El mtime va incluido a propósito: la exigencia es que el archivo sellado
    NO SE TOQUE, no que se reescriba con bytes parecidos."""
    huella = {}
    for nombre in (f"ext_{fecha}.csv", f"ext_{fecha}.meta.json"):
        r = os.path.join(S.DIR_EXT, nombre)
        huella[nombre] = (S._sha256(r), os.stat(r).st_mtime_ns) if os.path.exists(r) else None
    return huella


def _volcado_sellos(db) -> list:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return con.execute("SELECT * FROM sellos_dinero ORDER BY id").fetchall()
    finally:
        con.close()


def _cuenta(db, tabla) -> int:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    finally:
        con.close()


@pytest.fixture
def entorno_temporal(tmp_path, monkeypatch):
    """Directorio de extensiones y base, los dos temporales. `S.RUTA_DB` se
    parchea además de pasar `ruta_db=` porque cualquier ruta que lea el global
    (`congelar_extension`, `exportar_csv`) tiene que caer también en tmp_path."""
    dir_ext = tmp_path / "datos" / "sello"
    db = str(tmp_path / "sello_dinero.db")
    monkeypatch.setattr(S, "DIR_EXT", str(dir_ext))
    monkeypatch.setattr(S, "RUTA_DB", db)
    monkeypatch.setattr(S, "DIR_BACKUP_EXT", str(tmp_path / "backups_ext"))
    return db


def test_E4_archivo_un_segundo_sello_con_otro_insumo_no_toca_la_extension_sellada(
        entorno_temporal, base):
    """REPRODUCE el 10-sep: mismo día, mismo `fecha_insumo`, insumo distinto.
    E4 hace lo correcto con la base; el archivo que el sha sellado cita tiene
    que quedar igual, byte a byte, y `ultima_extension()` tiene que seguir
    devolviendo el insumo SELLADO (si no, `--sin-red` sella mañana con el
    insumo divergente)."""
    db = entorno_temporal
    t0 = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)

    _, meta_a, r1 = _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.01), db, t0)
    assert r1["resultado"] == "sellada" and r1["filas_insertadas"] == 33
    assert r1["insumo_ext_sha256"] == meta_a["sha256"]
    sellado = _huella_ext()
    volcado = _volcado_sellos(db)
    assert sellado[f"ext_{FECHA}.csv"][0] == meta_a["sha256"]

    # segunda pasada del mismo día con OTRO insumo (Yahoo ya trajo el cierre)
    _, meta_b, r2 = _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.03), db, t0 + timedelta(minutes=30))
    assert meta_b["sha256"] != meta_a["sha256"], "el insumo tiene que ser distinto o el test no prueba nada"
    assert r2["resultado"] == "divergencia_registrada" and r2["filas_insertadas"] == 0

    # la base: ninguna fila sellada cambia; la divergencia SÍ se registra (E4)
    assert _volcado_sellos(db) == volcado
    assert _cuenta(db, "divergencias_sello") == 1

    # el disco: el archivo que el sha sellado cita no se toca
    assert _huella_ext() == sellado, (
        "FUGA E4-archivo: congelar_extension() reescribió la extensión de una "
        "fecha ya sellada con otro insumo; el sha de la base deja de apuntar a "
        "lo que hay en disco")

    # y el insumo divergente, exista o no como archivo aparte, nunca es el que
    # `--sin-red` levanta mañana
    ruta_u, meta_u = S.ultima_extension()
    assert os.path.basename(ruta_u) == f"ext_{FECHA}.csv"
    assert meta_u["sha256"] == meta_a["sha256"] == S._sha256(ruta_u)


def test_E4_archivo_un_segundo_sello_con_el_MISMO_insumo_tampoco_reescribe_nada(
        entorno_temporal, base):
    """Mismo día, MISMO insumo: `sellar()` devuelve «ya_sellada» y no inserta,
    pero `congelar_extension()` reescribía los dos archivos antes de que nadie
    mirara la base. El CSV volvía con bytes idénticos (el sha no lo delata) y
    el `.meta.json` lleva `congelado_en_utc`, así que EN PRODUCCIÓN —dos
    disparos separados por minutos— cambiaba también de sha; dentro de un
    test que corre en menos de un segundo los bytes coinciden, y por eso la
    evidencia determinista de la reescritura es el mtime, no el sha.
    La exigencia es que un archivo sellado no se TOQUE."""
    db = entorno_temporal
    t0 = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)

    _, meta_a, r1 = _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.01), db, t0)
    assert r1["resultado"] == "sellada"
    sellado = _huella_ext()
    volcado = _volcado_sellos(db)

    _, meta_b, r2 = _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.01), db, t0 + timedelta(minutes=30))
    assert meta_b["sha256"] == meta_a["sha256"]
    assert r2["resultado"] == "ya_sellada" and r2["filas_insertadas"] == 0

    assert _volcado_sellos(db) == volcado
    assert _cuenta(db, "divergencias_sello") == 0
    assert _huella_ext() == sellado, (
        "FUGA E4-archivo (variante idempotente): la extensión de una fecha ya "
        "sellada se reescribe aunque el insumo sea el mismo")


def test_E4_archivo_el_respaldo_en_backups_tampoco_cambia(entorno_temporal, base):
    """E5: el sha sellado tiene que apuntar a algo que exista mañana. La copia
    en data/backups/ es la única versionada; una segunda pasada con otro
    insumo no puede pisarla (antes no la pisaba porque `main()` sólo respalda
    con resultado «sellada», un accidente feliz que acá se fija con test)."""
    db = entorno_temporal
    t0 = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)

    ruta_a, meta_a, r1 = _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.01), db, t0)
    assert r1["resultado"] == "sellada"
    copias = S.respaldar_extension(ruta_a, S.DIR_BACKUP_EXT)          # lo que hace main()
    antes = {os.path.basename(c): (S._sha256(c), os.stat(c).st_mtime_ns) for c in copias}
    assert antes[f"ext_{FECHA}.csv"][0] == meta_a["sha256"]

    ruta_b, meta_b, r2 = _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.03), db, t0 + timedelta(minutes=30))
    assert r2["resultado"] == "divergencia_registrada"
    despues = {n: (S._sha256(os.path.join(S.DIR_BACKUP_EXT, n)), os.stat(os.path.join(S.DIR_BACKUP_EXT, n)).st_mtime_ns)
               for n in antes}
    assert despues == antes, "el respaldo versionado del insumo sellado cambió"


def test_E4bis_el_insumo_divergente_no_se_conserva_y_la_divergencia_lo_declara(entorno_temporal, base):
    """Opción A del dictamen: con la fecha ya sellada no aparece NINGÚN archivo
    nuevo en DIR_EXT; el divergente vive en un temporal fuera de la carpeta,
    `main()` lo borra, y `divergencias_sello.detalle` dice que el sha apunta a
    un contenido que ya no existe."""
    db = entorno_temporal
    t0 = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)
    ruta_a, meta_a, r1 = _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.01), db, t0)
    antes = sorted(os.listdir(S.DIR_EXT))
    ruta_b, meta_b, r2 = _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.03), db, t0 + timedelta(minutes=30))
    assert sorted(os.listdir(S.DIR_EXT)) == antes == [f"ext_{FECHA}.csv", f"ext_{FECHA}.meta.json"]
    assert meta_b["persistido"] is False and not os.path.exists(ruta_b)
    assert os.path.dirname(os.path.abspath(ruta_b)) != os.path.abspath(S.DIR_EXT)
    assert meta_b["divergente_de"]["archivo"] == f"ext_{FECHA}.csv"
    assert meta_b["divergente_de"]["sha256_sellado"] == meta_a["sha256"]
    assert r2["insumo_divergente_conservado"] is False and r2["sha_nuevo"] == meta_b["sha256"]
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    detalle, sha_nuevo = con.execute("SELECT detalle, sha_nuevo FROM divergencias_sello").fetchone()
    con.close()
    assert "NO conservado" in detalle and "ya no existe" in detalle and sha_nuevo == meta_b["sha256"]
    # el sha del contenido en memoria ES el sha que se habría escrito
    assert "persistido" not in meta_a and S._sha256(ruta_a) == meta_a["sha256"]


def test_E4bis_sin_sello_previo_la_extension_se_escribe_como_siempre(entorno_temporal, base):
    """Sin base (primera noche) o con base sin esa fecha, nada cambia respecto
    de E0.2: `ext_<fecha>.csv` con su sha en el meta, igual al del archivo."""
    db = entorno_temporal
    assert S.sello_previo(FECHA, db) is None                              # la base no existe todavía
    ruta, meta = S.congelar_extension(_cierres_ext_sinteticos(base), BASE_HASTA)
    assert os.path.basename(ruta) == f"ext_{FECHA}.csv" and "divergente_de" not in meta and "persistido" not in meta
    assert S._sha256(ruta) == meta["sha256"]
    S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 9, 3, 0, tzinfo=UTC), ruta_db=db)
    assert S.sello_previo(FECHA, db) == {"sha256": meta["sha256"], "archivo": f"ext_{FECHA}.csv"}
    # con base pero otra fecha: tampoco es divergencia, y el archivo del 08 sigue intacto
    huella_08 = _huella_ext()
    ruta2, meta2 = S.congelar_extension(_cierres_ext_sinteticos(base, (FECHA, "2026-09-09")), BASE_HASTA)
    assert os.path.basename(ruta2) == "ext_2026-09-09.csv" and "divergente_de" not in meta2
    assert _huella_ext() == huella_08


def test_E4bis_sello_previo_no_filtra_por_juego(entorno_temporal, base):
    """R4 del auditor: E4 dentro de `sellar` filtra por juego, así que un
    cambio de `juego_activo` habría vuelto a escribir la extensión de una
    fecha sellada. `sello_previo` mira la fecha y nada más."""
    db = entorno_temporal
    ruta, meta = S.congelar_extension(_cierres_ext_sinteticos(base), BASE_HASTA)
    S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 9, 3, 0, tzinfo=UTC), ruta_db=db)
    con = sqlite3.connect(db)
    juego = con.execute("SELECT DISTINCT juego FROM sellos_dinero").fetchone()[0]
    con.close()
    assert juego == "conservador"
    sellado = _huella_ext()
    # `sello_previo` no recibe juego y encuentra la fecha igual; el guardia de
    # `congelar_extension` no tiene por dónde dejar pasar un juego distinto
    assert S.sello_previo(FECHA, db) is not None
    ruta2, meta2 = S.congelar_extension(_cierres_ext_sinteticos(base, factor=1.05), BASE_HASTA)
    assert meta2.get("persistido") is False and _huella_ext() == sellado
    if os.path.exists(ruta2):
        os.remove(ruta2)


def test_solo_ext_fecha_csv_es_insumo_sellable():
    assert S.es_extension_sellable("ext_2026-09-09.csv")
    assert S.es_extension_sellable("/x/y/ext_2026-09-09.csv")
    assert not S.es_extension_sellable("ext_2026-09-09_divergente_20260910T033004Z.csv")
    assert not S.es_extension_sellable("ext_2026-09-09.meta.json")
    assert not S.es_extension_sellable("cierres_congelados.csv")


# ------------------------------------------------------------
# 4. Integridad permanente: la evidencia en disco es la que la base cita
# ------------------------------------------------------------
# Corre sobre la base REAL en `mode=ro` y sobre los archivos reales. Si falla,
# el diagnóstico es «el disco no tiene lo que la base cita»: se PARA y se
# reporta; el archivo no se «arregla» (la fila sellada tampoco). En un
# checkout sin base (`*.db` está en .gitignore) se salta con razón declarada:
# saltar no es pasar. Itera por `fecha_insumo` SIN filtrar por juego (R4).
def _citas_selladas(ruta_db):
    if not os.path.exists(ruta_db):
        pytest.skip(f"sin base real en {ruta_db}: nada que verificar en este checkout")
    con = S.conectar(ruta_db, solo_lectura=True)
    try:
        filas = con.execute("SELECT DISTINCT fecha_insumo, insumo_ext_archivo, insumo_ext_sha256 "
                            "FROM sellos_dinero ORDER BY fecha_insumo").fetchall()
    finally:
        con.close()
    if not filas:
        pytest.skip("la base real no tiene filas selladas todavía")
    return filas


def _verificar_citas_en(directorio, filas):
    fallas = []
    por_fecha = {}
    for fecha, archivo, sha in filas:
        por_fecha.setdefault(fecha, set()).add(sha)
        ruta = os.path.join(directorio, archivo or f"ext_{fecha}.csv")
        if not os.path.exists(ruta):
            fallas.append(f"{fecha}: falta {ruta}")
        elif S._sha256(ruta) != sha:
            fallas.append(f"{fecha}: {os.path.basename(ruta)} tiene sha {S._sha256(ruta)[:12]}… y la base cita {sha[:12]}…")
    # una fecha sellada cita UN solo insumo (E4: el segundo no inserta)
    fallas += [f"{f}: {len(s)} shas distintos sellados" for f, s in por_fecha.items() if len(s) != 1]
    assert not fallas, "PARAR Y REPORTAR (no arreglar el archivo):\n" + "\n".join(fallas)


def test_integridad_cada_extension_sellada_en_disco_es_la_que_la_base_cita():
    """Para cada `fecha_insumo` sellada, sha256(dinero/datos/sello/<insumo_ext_archivo>)
    == `insumo_ext_sha256` de sus filas. Es el test que habría estado rojo del
    10-sep al 19-sep-2026."""
    _verificar_citas_en(S.DIR_EXT, _citas_selladas(S.RUTA_DB))


def test_integridad_la_copia_versionada_en_backups_es_la_que_la_base_cita():
    """`respaldar_extension` copia byte a byte a data/backups/sello_dinero_ext/
    (E5); el sha citado tiene que existir también ahí."""
    _verificar_citas_en(S.DIR_BACKUP_EXT, _citas_selladas(S.RUTA_DB))


def test_integridad_el_congelado_grande_es_el_que_la_base_cita():
    """R5 del auditor: `insumo_base_sha256` de toda fila cita el congelado
    grande; si `precios.congelar` lo reescribiera, todas las filas quedarían
    citando un archivo que no existe."""
    if not os.path.exists(S.RUTA_DB):
        pytest.skip("sin base real: nada que verificar en este checkout")
    con = S.conectar(S.RUTA_DB, solo_lectura=True)
    try:
        shas = [r[0] for r in con.execute("SELECT DISTINCT insumo_base_sha256 FROM sellos_dinero").fetchall()]
    finally:
        con.close()
    if not shas:
        pytest.skip("la base real no tiene filas selladas todavía")
    assert shas == [S._sha256(precios.RUTA_CIERRES)], "PARAR Y REPORTAR: el congelado grande no es el que la base cita"


def test_contraprueba_la_integridad_ve_un_archivo_pisado(tmp_path):
    """Un verificador que no puede fallar no verifica: con una cita que el
    disco no cumple, tiene que decir «parar y reportar»."""
    d = tmp_path / "d"; d.mkdir()
    (d / "ext_2026-09-09.csv").write_text("Date,NVDA\n2026-09-09,1.0\n")
    sha_real = S._sha256(str(d / "ext_2026-09-09.csv"))
    _verificar_citas_en(str(d), [("2026-09-09", "ext_2026-09-09.csv", sha_real)])          # coincide: pasa
    with pytest.raises(AssertionError, match="PARAR Y REPORTAR"):
        _verificar_citas_en(str(d), [("2026-09-09", "ext_2026-09-09.csv", "0" * 64)])       # pisado: falla
    with pytest.raises(AssertionError, match="falta"):
        _verificar_citas_en(str(d), [("2026-09-10", "ext_2026-09-10.csv", sha_real)])       # ausente: falla
    with pytest.raises(AssertionError, match="shas distintos"):                              # R4: dos insumos una fecha
        _verificar_citas_en(str(d), [("2026-09-09", "ext_2026-09-09.csv", sha_real),
                                     ("2026-09-09", "ext_2026-09-09.csv", sha_real.replace(sha_real[0], "f", 1))])
