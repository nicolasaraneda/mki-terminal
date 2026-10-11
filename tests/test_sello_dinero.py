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
siempre. Base temporal en cada test: `sello_dinero.db` real no se toca.

Corrida 15 (sección 5, acta §90.6): un disparo con timing roto ya no escribe
en `sellos_dinero` ni ocupa `ext_<fecha>.csv`; va a `intentos_no_verificables`
y a `ext_<fecha>.no_verificable.csv`. Los tests de E4 que fijaban lo viejo
se adaptaron y lo dicen en su docstring."""
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from dinero import precios
from dinero import sello_dinero as S
from dinero import universo_dinero as U

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UTC = timezone.utc
N_OPERABLES = 32   # operables con el techo de 500 USD: 33 hasta la corrida 16b; TOELY fuera del insumo de E0 desde el 5-oct-2026 (acta §95.4)


@pytest.fixture(scope="module")
def base():
    return precios.cargar_congelado()


def _extension_sintetica(tmp_path, base, sesiones=("2026-09-08",), factor=1.01, sin_dato=(), no_verificable=False):
    """Una extensión con las sesiones dadas, precios = último cierre × factor,
    con su meta (disponibilidad G8) y sha256, escrita como la real. `sin_dato`
    deja NaN esos tickers en la última sesión (publicación asincrónica).
    `no_verificable` la escribe como la escribe `congelar_extension` desde
    E0.3 cuando el timing está roto: `ext_<fecha>.no_verificable.csv` y
    `cupo_canonico: false` en el meta."""
    ult = base.iloc[-1]
    filas = {pd.Timestamp(s): ult * factor for s in sesiones}
    ext = pd.DataFrame(filas).T
    for t in sin_dato:
        ext.loc[pd.Timestamp(sesiones[-1]), t] = float("nan")
    ext.index.name = "Date"
    ruta = str(tmp_path / f"ext_{sesiones[-1]}{'.no_verificable' if no_verificable else ''}.csv")
    ext.to_csv(ruta)
    meta = {"sha256": S._sha256(ruta), "hasta": sesiones[-1], "tickers": list(ext.columns),
            "desde": sesiones[0], "extiende_a": {"hasta": "2026-09-04"},
            "disponibilidad": {"exchange": "XNYS", "por_ticker": precios.disponibilidad_por_ticker(ext)}}
    if no_verificable:
        meta["cupo_canonico"] = False
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
    assert len(d["filas"]) == len(d["operables"]) == N_OPERABLES
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
    assert r["filas_insertadas"] == r["filas_decididas"] == N_OPERABLES
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
    """ADAPTADO en la corrida 15 (acta §90.6, política de retención): hasta
    E0.2 la fila no verificable se insertaba en `sellos_dinero` (resultado
    `sellada`) y ocupaba la fecha; desde E0.3 va a `intentos_no_verificables`
    (resultado `intento_no_verificable`) citando la evidencia
    `.no_verificable.csv`, y `sellos_dinero` queda vacía. Lo que E4 exigía
    —timing roto, estado y cuenta_para_N = 0— se exige igual."""
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-08",), no_verificable=True)
    tarde = datetime(2026, 9, 9, 14, 0, tzinfo=UTC)          # media hora después de abrir
    db = str(tmp_path / "s.db")
    r = S.sellar(ruta, meta, ahora_utc=tarde, ruta_db=db)
    assert r["timing_ok"] is False and r["estado"] == "no_verificable_timing" and r["cuenta_para_N"] == 0
    assert r["estado_timing"] == "roto"
    assert r["resultado"] == "intento_no_verificable" and r["tabla"] == "intentos_no_verificables"
    assert r["filas_insertadas"] == N_OPERABLES
    con = sqlite3.connect(db)
    assert con.execute("SELECT COUNT(*) FROM sellos_dinero").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*), MIN(estado), MAX(estado), MIN(insumo_ext_archivo) FROM intentos_no_verificables"
                       ).fetchone() == (N_OPERABLES, "no_verificable_timing", "no_verificable_timing", "ext_2026-09-08.no_verificable.csv")
    con.close()


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
    assert r["filas_insertadas"] == N_OPERABLES                                  # se sella igual


def test_un_insumo_desactualizado_no_cuenta_para_N(tmp_path, base):
    """ADAPTADO en la corrida 15: un insumo desactualizado tiene la apertura
    objetivo en el pasado, o sea timing roto, y desde E0.3 eso es un intento
    no verificable (tabla aparte, evidencia `.no_verificable.csv`), no una
    fila en `sellos_dinero`. Sigue sin contar para N."""
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-04",), factor=1.0, no_verificable=True)
    db = str(tmp_path / "s.db")
    r = S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 9, 3, 0, tzinfo=UTC), ruta_db=db)
    assert r["sesion_objetivo"] == "2026-09-08"     # lo siguiente a available_at (4-sep 20:00Z)
    assert r["timing_ok"] is False and r["cuenta_para_N"] == 0
    assert r["resultado"] == "intento_no_verificable" and r["estado"] == "no_verificable_timing"
    assert S.estado(db)["filas"] == 0 and S.estado(db)["intentos_no_verificables"] == 1


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
    assert r1["filas_insertadas"] == N_OPERABLES
    assert r2["resultado"] == "ya_sellada" and r2["filas_insertadas"] == 0
    assert "estado" not in r2 and "cuenta_para_N" not in r2     # no describe un sello que no ocurrió
    e = S.estado(db)
    assert e["filas"] == N_OPERABLES and e["sesiones_selladas"] == 1 and e["sesiones_que_cuentan_para_N"] == 1
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
    assert con.execute("SELECT COUNT(*) FROM sellos_dinero").fetchone()[0] == N_OPERABLES
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
    assert len(df) == N_OPERABLES and set(df["tamano_nominal"]) == {0} and "insumo_ext_sha256" in df.columns
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
    borra el temporal de un insumo divergente no conservado.

    Guarda de la corrida 14 (deuda que el guardián de la corrida 13 dejó
    anotada): `congelar_extension` se llama a propósito SIN `ruta_db`, igual que
    lo hace `main()`, así que el `sello_previo()` de adentro lee el GLOBAL
    `S.RUTA_DB`. Eso es seguro sólo mientras el fixture lo tenga parcheado a la
    base temporal. Si algún día deja de parchearlo, este helper consultaría la
    base REAL de producción sin decir nada y el test pasaría igual. Que reviente
    acá, con el motivo escrito, en vez de mirar producción en silencio.
    """
    raiz_tmp = os.path.dirname(os.path.abspath(db))
    assert os.path.abspath(S.RUTA_DB) == os.path.abspath(db), (
        "el fixture dejó de parchear S.RUTA_DB: congelar_extension() leería "
        f"{S.RUTA_DB} y no la base temporal {db}")
    for nombre in ("DIR_EXT", "DIR_BACKUP_EXT"):
        destino = os.path.abspath(getattr(S, nombre))
        assert destino.startswith(raiz_tmp + os.sep), (
            f"el fixture dejó de parchear S.{nombre}: apunta a {destino}, "
            f"fuera del tmp_path {raiz_tmp}")
    ruta, meta = _congelar(cierres_ext, base_hasta, ahora)
    try:
        return ruta, meta, S.sellar(ruta, meta, ahora_utc=ahora, ruta_db=db)
    finally:
        if not meta.get("persistido", True) and os.path.exists(ruta):
            os.remove(ruta)


def _huella_archivos(nombres) -> dict:
    """(sha256, mtime_ns) de esos archivos en S.DIR_EXT. El mtime va incluido
    a propósito: la exigencia es que el archivo sellado NO SE TOQUE, no que se
    reescriba con bytes parecidos."""
    huella = {}
    for nombre in nombres:
        r = os.path.join(S.DIR_EXT, nombre)
        huella[nombre] = (S._sha256(r), os.stat(r).st_mtime_ns) if os.path.exists(r) else None
    return huella


def _huella_ext(fecha=FECHA) -> dict:
    """Los archivos CANÓNICOS de esa fecha."""
    return _huella_archivos((f"ext_{fecha}.csv", f"ext_{fecha}.meta.json"))


def _volcado(db, tabla) -> list:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return con.execute(f"SELECT * FROM {tabla} ORDER BY id").fetchall()
    finally:
        con.close()


def _volcado_sellos(db) -> list:
    return _volcado(db, "sellos_dinero")


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
    # R3 del auditor (corrida 15): con RUTA_DB parcheada, la guarda H8 de
    # `exportar_csv` dejaría escribir en el CSV versionado real; que caiga en tmp
    monkeypatch.setattr(S, "RUTA_BACKUP_CSV", str(tmp_path / "sello_dinero.csv"))
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
    assert r1["resultado"] == "sellada" and r1["filas_insertadas"] == N_OPERABLES
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
    de E0.2: `ext_<fecha>.csv` con su sha en el meta, igual al del archivo.
    ADAPTADO en la corrida 15: desde E0.3 `congelar_extension` decide el
    timing con `ahora_utc`, así que se le pasa un instante dentro de la
    ventana (antes se llamaba sin reloj)."""
    db = entorno_temporal
    t_08 = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)
    assert S.sello_previo(FECHA, db) is None                              # la base no existe todavía
    ruta, meta = S.congelar_extension(_cierres_ext_sinteticos(base), BASE_HASTA, ahora_utc=t_08)
    assert os.path.basename(ruta) == f"ext_{FECHA}.csv" and "divergente_de" not in meta and "persistido" not in meta
    assert "cupo_canonico" not in meta and "timing" not in meta           # el canónico se escribe como en E0.2
    assert S._sha256(ruta) == meta["sha256"]
    S.sellar(ruta, meta, ahora_utc=t_08, ruta_db=db)
    assert S.sello_previo(FECHA, db) == {"sha256": meta["sha256"], "archivo": f"ext_{FECHA}.csv"}
    # con base pero otra fecha: tampoco es divergencia, y el archivo del 08 sigue intacto
    huella_08 = _huella_ext()
    ruta2, meta2 = S.congelar_extension(_cierres_ext_sinteticos(base, (FECHA, "2026-09-09")), BASE_HASTA,
                                        ahora_utc=datetime(2026, 9, 10, 3, 0, tzinfo=UTC))
    assert os.path.basename(ruta2) == "ext_2026-09-09.csv" and "divergente_de" not in meta2
    assert _huella_ext() == huella_08


def test_E4bis_sello_previo_no_filtra_por_juego(entorno_temporal, base):
    """R4 del auditor: E4 dentro de `sellar` filtra por juego, así que un
    cambio de `juego_activo` habría vuelto a escribir la extensión de una
    fecha sellada. `sello_previo` mira la fecha y nada más. (Corrida 15: se
    pasa `ahora_utc` dentro de la ventana; nada más cambió.)"""
    db = entorno_temporal
    t_08 = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)
    ruta, meta = S.congelar_extension(_cierres_ext_sinteticos(base), BASE_HASTA, ahora_utc=t_08)
    S.sellar(ruta, meta, ahora_utc=t_08, ruta_db=db)
    con = sqlite3.connect(db)
    juego = con.execute("SELECT DISTINCT juego FROM sellos_dinero").fetchone()[0]
    con.close()
    assert juego == "conservador"
    sellado = _huella_ext()
    # `sello_previo` no recibe juego y encuentra la fecha igual; el guardia de
    # `congelar_extension` no tiene por dónde dejar pasar un juego distinto
    assert S.sello_previo(FECHA, db) is not None
    ruta2, meta2 = S.congelar_extension(_cierres_ext_sinteticos(base, factor=1.05), BASE_HASTA, ahora_utc=t_08)
    assert meta2.get("persistido") is False and _huella_ext() == sellado
    if os.path.exists(ruta2):
        os.remove(ruta2)


def test_solo_ext_fecha_csv_es_insumo_sellable():
    assert S.es_extension_sellable("ext_2026-09-09.csv")
    assert S.es_extension_sellable("/x/y/ext_2026-09-09.csv")
    assert not S.es_extension_sellable("ext_2026-09-09_divergente_20260910T033004Z.csv")
    assert not S.es_extension_sellable("ext_2026-09-09.no_verificable.csv")          # E0.3
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
#
# Corrida 15 (política §5): se verifica CADA tabla contra sus propios
# archivos —`sellos_dinero` cita canónicos, `intentos_no_verificables` cita
# `.no_verificable.csv`— y «un solo insumo por fecha» vale por tabla (una
# fecha puede tener un intento y un sello: dos insumos, cada uno en la suya).
# Invariante nuevo: ninguna tabla cita la evidencia de la otra. Y las filas
# `no_verificable_timing` que E0.2 dejó en la tabla principal se toleran POR
# REGLA (version_sello anterior al corte de método), sin nombrar la fecha.
# Una base sin la tabla de intentos (la real, hasta que el sellador parcheado
# la cree) se lee como cero intentos: no es un error.
TABLAS_CON_EVIDENCIA = ("sellos_dinero", "intentos_no_verificables")
VERSION_CORTE_DE_METODO = "E0.3"     # desde esta VERSION_SELLO un timing roto no escribe en la tabla principal


def _version(v: str) -> tuple:
    return tuple(int(x) for x in v.lstrip("E").split("."))


def _citas_selladas(ruta_db, tabla="sellos_dinero"):
    if not os.path.exists(ruta_db):
        pytest.skip(f"sin base real en {ruta_db}: nada que verificar en este checkout")
    con = S.conectar(ruta_db, solo_lectura=True)
    try:
        filas = con.execute(f"SELECT DISTINCT fecha_insumo, insumo_ext_archivo, insumo_ext_sha256 "
                            f"FROM {tabla} ORDER BY fecha_insumo").fetchall()
    except sqlite3.OperationalError:
        if tabla == "sellos_dinero":
            raise
        # R2 del auditor (corrida 15): saltar con razón, no pasar en falso con []
        pytest.skip(f"la base real todavía no tiene {tabla}: cero intentos, nada que verificar")
    finally:
        con.close()
    if not filas and tabla == "sellos_dinero":
        pytest.skip("la base real no tiene filas selladas todavía")
    return filas


def _tabla_existe(ruta_db, tabla) -> bool:
    con = S.conectar(ruta_db, solo_lectura=True)
    try:
        return con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = ?", (tabla,)).fetchone()[0] == 1
    finally:
        con.close()


def _filas_rotas_en_principal(ruta_db) -> list:
    """(fecha, estado, estado_timing, version_sello) distintos de las filas de
    `sellos_dinero` con timing roto."""
    if not os.path.exists(ruta_db):
        pytest.skip(f"sin base real en {ruta_db}: nada que verificar en este checkout")
    con = S.conectar(ruta_db, solo_lectura=True)
    try:
        return con.execute("SELECT DISTINCT fecha_insumo, estado, estado_timing, version_sello FROM sellos_dinero "
                           "WHERE estado = 'no_verificable_timing' OR estado_timing = 'roto' ORDER BY fecha_insumo").fetchall()
    finally:
        con.close()


def _verificar_clase_de_evidencia(filas_sellos, filas_intentos):
    """Política §5.2: `sellos_dinero` nunca cita un `.no_verificable.csv`;
    `intentos_no_verificables` nunca cita un canónico."""
    fallas = [f"{f}: sellos_dinero cita {a}" for f, a, _ in filas_sellos
              if S.es_extension_no_verificable(a or f"ext_{f}.csv")]
    fallas += [f"{f}: intentos_no_verificables cita {a}" for f, a, _ in filas_intentos
               if not S.es_extension_no_verificable(a or f"ext_{f}.csv")]
    assert not fallas, "PARAR Y REPORTAR (cada tabla cita su clase de evidencia, política §5.2):\n" + "\n".join(fallas)


def _verificar_regla_del_corte(filas_rotas):
    """Una fila con timing roto en la tabla principal sólo puede venir de un
    sellador anterior al corte (E0.2: el 28-sep-2026). Desde E0.3 va a la
    tabla de intentos; si aparece una con esa versión, el parche no hizo lo
    que dice. La versión se compara como números, no como texto."""
    fallas = [f"{f}: {e} / {t} con version_sello {v}" for f, e, t, v in filas_rotas
              if _version(v) >= _version(VERSION_CORTE_DE_METODO)]
    assert not fallas, ("PARAR Y REPORTAR: desde E0.3 un timing roto no escribe en sellos_dinero; "
                        "estas filas dicen lo contrario:\n" + "\n".join(fallas))


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


@pytest.mark.parametrize("tabla", TABLAS_CON_EVIDENCIA)
def test_integridad_cada_extension_sellada_en_disco_es_la_que_la_base_cita(tabla):
    """Para cada `fecha_insumo` de la tabla, sha256(dinero/datos/sello/<insumo_ext_archivo>)
    == `insumo_ext_sha256` de sus filas. Es el test que habría estado rojo del
    10-sep al 19-sep-2026. Corrida 15: una vez por tabla."""
    _verificar_citas_en(S.DIR_EXT, _citas_selladas(S.RUTA_DB, tabla))


@pytest.mark.parametrize("tabla", TABLAS_CON_EVIDENCIA)
def test_integridad_la_copia_versionada_en_backups_es_la_que_la_base_cita(tabla):
    """`respaldar_extension` copia byte a byte a data/backups/sello_dinero_ext/
    (E5); el sha citado tiene que existir también ahí. Una vez por tabla."""
    _verificar_citas_en(S.DIR_BACKUP_EXT, _citas_selladas(S.RUTA_DB, tabla))


def test_integridad_ninguna_tabla_cita_la_evidencia_de_la_otra():
    """Política §5.2, sobre la base real. La mitad de `sellos_dinero` se
    verifica siempre; la de intentos sólo si la tabla ya existe (R2)."""
    sellos = _citas_selladas(S.RUTA_DB, "sellos_dinero")
    intentos = _citas_selladas(S.RUTA_DB, "intentos_no_verificables") if _tabla_existe(S.RUTA_DB, "intentos_no_verificables") else []
    _verificar_clase_de_evidencia(sellos, intentos)


def test_integridad_las_filas_rotas_de_la_tabla_principal_son_anteriores_al_corte():
    """Política §6.1: las filas `no_verificable_timing` que hay en la tabla
    principal son de un sellador anterior al corte (E0.2) y se quedan; con la
    versión del corte o posterior no puede haber ninguna. La regla no nombra
    la fecha."""
    _verificar_regla_del_corte(_filas_rotas_en_principal(S.RUTA_DB))


def _columnas(ruta_db, tabla) -> list:
    """(nombre, tipo) de cada columna, por PRAGMA, en una base abierta en mode=ro."""
    con = S.conectar(ruta_db, solo_lectura=True)
    try:
        return [(c[1], c[2]) for c in con.execute(f"PRAGMA table_info({tabla})").fetchall()]
    finally:
        con.close()


def _verificar_paridad_columnas(principal, intentos):
    """R2 del auditor (corrida 16-2, F4): las dos tablas de filas tienen que
    tener las MISMAS columnas, porque el INSERT de `sellar` es uno solo y
    `CREATE TABLE IF NOT EXISTS` no propaga una columna nueva a la tabla que
    ya existe. Compara nombre y tipo, en orden."""
    assert principal == intentos, ("PARAR Y REPORTAR: las dos tablas de filas divergieron en columnas "
                                   f"(sólo en sellos_dinero: {sorted(set(principal) - set(intentos))}; sólo en "
                                   f"intentos_no_verificables: {sorted(set(intentos) - set(principal))}); una columna "
                                   "nueva en _ddl_filas exige una migración aparte, con acta")


def test_integridad_las_dos_tablas_de_filas_tienen_las_mismas_columnas_en_la_base_real():
    """R2 del auditor (corrida 16-2): la paridad se verifica sobre la base REAL,
    no sobre una fresca de tmp (que por construcción no puede divergir). Salta
    con razón mientras la base real no tenga la tabla de intentos; empieza a
    correr la primera noche con E0.3."""
    if not os.path.exists(S.RUTA_DB):
        pytest.skip(f"sin base real en {S.RUTA_DB}: nada que verificar en este checkout")
    if not _tabla_existe(S.RUTA_DB, "intentos_no_verificables"):
        pytest.skip("la base real todavía no tiene intentos_no_verificables: la paridad se compara cuando el sellador la cree")
    _verificar_paridad_columnas(_columnas(S.RUTA_DB, "sellos_dinero"), _columnas(S.RUTA_DB, "intentos_no_verificables"))


def test_contraprueba_la_paridad_de_columnas_ve_una_base_vieja_a_la_que_init_db_no_le_agrega_la_columna(tmp_path):
    """F4 medida por el auditor: una `sellos_dinero` a la que le falta una
    columna sigue sin ella después de `init_db` (IF NOT EXISTS es un no-op),
    mientras la tabla de intentos nace completa. El verificador tiene que
    verlo; sobre una base nacida en E0.3 tiene que pasar."""
    db = str(tmp_path / "vieja.db")
    con = sqlite3.connect(db)
    con.executescript(S._ddl_filas("sellos_dinero").replace("            insumo_completo INTEGER,            -- E3: 1 si todos los operables tienen cierre en fecha_insumo\n", ""))
    con.commit(); con.close()
    assert ("insumo_completo", "INTEGER") not in _columnas(db, "sellos_dinero"), "la contraprueba no fabricó la carencia"
    con = S.conectar(db)                      # init_db: crea intentos_no_verificables, NO repara sellos_dinero
    con.close()
    with pytest.raises(AssertionError, match="PARAR Y REPORTAR"):
        _verificar_paridad_columnas(_columnas(db, "sellos_dinero"), _columnas(db, "intentos_no_verificables"))
    db2 = str(tmp_path / "nueva.db")
    S.conectar(db2).close()
    _verificar_paridad_columnas(_columnas(db2, "sellos_dinero"), _columnas(db2, "intentos_no_verificables"))
    assert len(_columnas(db2, "sellos_dinero")) == 36


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


# ------------------------------------------------------------
# 5. Corrida 15 (acta §90.6; política GEMELO/propuestas/parches/
#    politica_evidencia_no_verificable.md, camino T): un disparo con timing
#    roto no ocupa ni la fecha en `sellos_dinero` ni el cupo `ext_<fecha>.csv`
# ------------------------------------------------------------
# El 28-sep-2026 el PC despertó de la suspensión y el timer disparó a las
# 13:42 de Nueva York con la bolsa abierta. E4 marcó las 33 filas
# `no_verificable_timing` —correcto— pero las escribió en `sellos_dinero`, y
# `congelar_extension()` ya había escrito `ext_2026-09-28.csv` con la matriz
# de media sesión. A las 23:30 NY el disparo bueno encontró la fecha sellada,
# entró por divergencia y escribió cero filas: la sesión se perdió y el cupo
# de evidencia quedó ocupado para siempre por un insumo que E4 había
# rechazado (tarjeta §62; dictamen_14/auditor_sello_28sep.md). Como
# `UNIQUE (fecha_insumo, ticker, juego)` impide que las filas rechazadas y
# las buenas convivan en la tabla, las rechazadas van a una tabla aparte,
# `intentos_no_verificables`, con las mismas columnas y la misma
# inmutabilidad; y el timing se decide ANTES de congelar la extensión, así
# que un insumo rechazado se escribe como `ext_<fecha>.no_verificable.csv`
# y el nombre canónico queda libre. El primer test REPRODUCE el 28-sep y
# falla sobre E0.2 por su propia aserción (salida guardada en
# GEMELO/propuestas/parches/sello_no_verificable.md).
LUNES = "2026-09-14"
SESIONES_HASTA_LUNES = ("2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11", LUNES)
T_INTRADIA = datetime(2026, 9, 14, 17, 42, tzinfo=UTC)     # 13:42 NY del lunes: bolsa abierta (el 28-sep)
T_NOCHE = datetime(2026, 9, 15, 3, 30, tzinfo=UTC)         # 23:30 NY del mismo lunes: el timer
T_TARDE = datetime(2026, 9, 15, 14, 0, tzinfo=UTC)         # 10:00 NY del martes: después de la apertura objetivo
CANON_CSV, CANON_META = f"ext_{LUNES}.csv", f"ext_{LUNES}.meta.json"
NV_CSV, NV_META = f"ext_{LUNES}.no_verificable.csv", f"ext_{LUNES}.no_verificable.meta.json"
TABLA_INTENTOS = "intentos_no_verificables"


def _congelar(cierres_ext, base_hasta, ahora):
    """`congelar_extension` con el reloj inyectado. Sobre E0.2 la función no
    recibía el instante (no miraba el reloj: por eso el 28-sep ocupó el cupo
    canónico) y se la llama sin él, para que la reproducción falle sobre HEAD
    por su propia aserción y no por un TypeError. Con el parche aplicado la
    rama sin `ahora_utc` es código muerto y se queda como constancia."""
    import inspect
    if "ahora_utc" in inspect.signature(S.congelar_extension).parameters:
        return S.congelar_extension(cierres_ext, base_hasta, ahora_utc=ahora)
    return S.congelar_extension(cierres_ext, base_hasta)


def _ext_con_ultima_fila(base, factor_ultima, sesiones=SESIONES_HASTA_LUNES) -> pd.DataFrame:
    """Historia idéntica (× 1.01) y SÓLO la última sesión distinta: la barra
    intradía de las 13:42 y el cierre de las 23:30 difieren en la última fila
    y en nada más, como el 28-sep."""
    ext = _cierres_ext_sinteticos(base, sesiones, 1.01)
    ext.iloc[-1] = base.iloc[-1].values * factor_ultima
    return ext


def test_reproduccion_28sep_un_disparo_intradia_no_quema_la_sesion_ni_el_cupo_canonico(entorno_temporal, base):
    """Disparo 1 a las 13:42 NY de un lunes con la barra intradía de ese lunes
    como última fila; disparo 2 a las 23:30 NY del mismo lunes con el cierre
    (otra última fila, misma fecha). Exige que el 2 SELLE, que las filas del
    1 sigan intactas en su tabla, que `ext_<fecha>.csv` tenga el insumo BUENO
    y que el par `.no_verificable` tenga el del disparo 1.
    Sobre E0.2 falla en la aserción del resultado del disparo 2: da
    `divergencia_registrada` y el canónico queda con la matriz intradía."""
    db = entorno_temporal
    ruta1, meta1, r1 = _camino_main(_ext_con_ultima_fila(base, 0.98), db, T_INTRADIA)
    assert r1["timing_ok"] is False and r1["estado"] == "no_verificable_timing" and r1["cuenta_para_N"] == 0
    assert r1["estado_timing"] == "roto" and r1["filas_insertadas"] == N_OPERABLES

    ruta2, meta2, r2 = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_NOCHE)
    assert meta2["sha256"] != meta1["sha256"], "los dos insumos tienen que ser distintos o el test no prueba nada"
    assert r2["resultado"] == "sellada", (
        "EL 28-SEP: el disparo bueno de las 23:30 NY no selló porque la fecha quedó ocupada por el "
        f"intento intradía (resultado={r2['resultado']!r}, filas_insertadas={r2.get('filas_insertadas')})")
    assert r2["estado"] == "pendiente" and r2["cuenta_para_N"] == 1 and r2["filas_insertadas"] == N_OPERABLES
    assert r2["insumo_fresco"] is True and r2["insumo_completo"] is True
    assert r2["insumo_ext_sha256"] == meta2["sha256"] and r2["sesion_objetivo"] == "2026-09-15"

    # la base: el intento en su tabla, intacto; el sello en la principal; ninguna divergencia
    assert r1["resultado"] == "intento_no_verificable"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    intentos = con.execute(f"SELECT DISTINCT estado, estado_timing, cuenta_para_N, insumo_ext_sha256, insumo_ext_archivo, "
                           f"version_sello FROM {TABLA_INTENTOS}").fetchall()
    sellos = con.execute("SELECT DISTINCT estado, estado_timing, cuenta_para_N, insumo_ext_sha256, insumo_ext_archivo, "
                         "version_sello FROM sellos_dinero").fetchall()
    con.close()
    assert intentos == [("no_verificable_timing", "roto", 0, meta1["sha256"], NV_CSV, S.VERSION_SELLO)]
    assert sellos == [("pendiente", "ok", 1, meta2["sha256"], CANON_CSV, S.VERSION_SELLO)]
    assert _cuenta(db, TABLA_INTENTOS) == N_OPERABLES and _cuenta(db, "sellos_dinero") == N_OPERABLES and _cuenta(db, "divergencias_sello") == 0
    assert S.sello_previo(LUNES, db) == {"sha256": meta2["sha256"], "archivo": CANON_CSV}
    assert S.intento_previo(LUNES, db) == {"sha256": meta1["sha256"], "archivo": NV_CSV}

    # el disco: el canónico es el insumo BUENO; el par no verificable es el del disparo 1, byte a byte
    assert os.path.basename(ruta1) == NV_CSV and os.path.basename(ruta2) == CANON_CSV
    assert sorted(os.listdir(S.DIR_EXT)) == [CANON_CSV, CANON_META, NV_CSV, NV_META]
    assert S._sha256(os.path.join(S.DIR_EXT, CANON_CSV)) == meta2["sha256"]
    assert S._sha256(os.path.join(S.DIR_EXT, NV_CSV)) == meta1["sha256"]
    with open(os.path.join(S.DIR_EXT, NV_META), encoding="utf-8") as f:
        meta_nv = json.load(f)
    assert meta_nv["sha256"] == meta1["sha256"] and meta_nv["cupo_canonico"] is False
    assert meta_nv["timing"]["available_at"] == "2026-09-14T20:00:00+00:00"
    assert meta_nv["timing"]["emision_utc"] == T_INTRADIA.isoformat()
    assert meta_nv["timing"]["apertura_objetivo_utc"].startswith("2026-09-15T13:30") and meta_nv["timing"]["timing_ok"] is False
    assert "cupo_canonico" not in meta2 and "timing" not in meta2          # el canónico se escribe como siempre

    # el estado que lee la API y el insumo que --sin-red levantaría mañana
    e = S.estado(db)
    assert e["filas"] == N_OPERABLES and e["sesiones_selladas"] == 1 and e["sesiones_que_cuentan_para_N"] == 1
    assert e["intentos_no_verificables"] == 1 and e["ultimo"]["timestamp_utc"] == r2["timestamp_utc"]
    ruta_u, meta_u = S.ultima_extension()
    assert os.path.basename(ruta_u) == CANON_CSV and meta_u["sha256"] == meta2["sha256"]


def test_las_filas_del_intento_no_cambian_cuando_llega_el_sello_bueno(entorno_temporal, base):
    """Volcado byte a byte de la tabla de intentos y huella (sha + mtime) del
    par `.no_verificable` antes y después del sello de las 23:30."""
    db = entorno_temporal
    _camino_main(_ext_con_ultima_fila(base, 0.98), db, T_INTRADIA)
    volcado = _volcado(db, TABLA_INTENTOS)
    huella = _huella_archivos((NV_CSV, NV_META))
    assert len(volcado) == N_OPERABLES and None not in huella.values()
    _, _, r2 = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_NOCHE)
    assert r2["resultado"] == "sellada"
    assert _volcado(db, TABLA_INTENTOS) == volcado
    assert _huella_archivos((NV_CSV, NV_META)) == huella


def test_un_segundo_intento_no_verificable_deja_divergencia_y_ningun_archivo_nuevo(entorno_temporal, base):
    """Política §2.4: un solo intento persistido por fecha. El segundo deja una
    fila en `divergencias_sello` con los dos sha (el «sellado» es el del
    intento previo y el detalle lo dice), cero filas nuevas y ningún archivo
    nuevo en la carpeta; el temporal vive fuera y `main()` lo borra."""
    db = entorno_temporal
    ruta1, meta1, r1 = _camino_main(_ext_con_ultima_fila(base, 0.98), db, T_INTRADIA)
    assert r1["resultado"] == "intento_no_verificable"
    antes = sorted(os.listdir(S.DIR_EXT))
    huella = _huella_archivos((NV_CSV, NV_META))
    volcado = _volcado(db, TABLA_INTENTOS)

    ruta2, meta2, r2 = _camino_main(_ext_con_ultima_fila(base, 0.97), db, T_INTRADIA + timedelta(minutes=20))
    assert meta2["sha256"] != meta1["sha256"]
    assert r2["resultado"] == "divergencia_registrada" and r2["filas_insertadas"] == 0
    assert r2["sha_sellado"] == meta1["sha256"] and r2["sha_nuevo"] == meta2["sha256"]
    assert r2["insumo_divergente_conservado"] is False and r2["divergente_de"] == "intento_no_verificable"
    assert meta2["persistido"] is False and meta2["cupo_canonico"] is False and not os.path.exists(ruta2)
    assert os.path.dirname(os.path.abspath(ruta2)) != os.path.abspath(S.DIR_EXT)
    assert meta2["divergente_de"] == {"archivo": NV_CSV, "sha256_intento": meta1["sha256"], "nota": meta2["divergente_de"]["nota"]}

    assert sorted(os.listdir(S.DIR_EXT)) == antes == [NV_CSV, NV_META]
    assert _huella_archivos((NV_CSV, NV_META)) == huella
    assert _volcado(db, TABLA_INTENTOS) == volcado and _cuenta(db, "sellos_dinero") == 0
    assert _cuenta(db, "divergencias_sello") == 1
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    detalle, sha_s, sha_n = con.execute("SELECT detalle, sha_sellado, sha_nuevo FROM divergencias_sello").fetchone()
    con.close()
    assert "intento no verificable" in detalle and "NO conservado" in detalle and (sha_s, sha_n) == (meta1["sha256"], meta2["sha256"])

    # y después de los dos intentos el sello bueno entra igual (§2.5)
    _, meta3, r3 = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_NOCHE)
    assert r3["resultado"] == "sellada" and r3["filas_insertadas"] == N_OPERABLES
    assert sorted(os.listdir(S.DIR_EXT)) == [CANON_CSV, CANON_META, NV_CSV, NV_META]


def test_un_disparo_fuera_de_hora_sobre_una_fecha_ya_sellada_no_toca_nada(entorno_temporal, base):
    """Política §2.5: un sello nunca se deshace por un intento posterior. Con
    otro insumo → divergencia, con el mismo → `ya_sellada`, como hoy; cero
    filas, el canónico intacto (sha y mtime) y ningún archivo nuevo."""
    db = entorno_temporal
    _, meta1, r1 = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_NOCHE)
    assert r1["resultado"] == "sellada"
    sellado = _huella_ext(LUNES)
    volcado = _volcado_sellos(db)
    archivos = sorted(os.listdir(S.DIR_EXT))

    ruta2, meta2, r2 = _camino_main(_ext_con_ultima_fila(base, 1.03), db, T_TARDE)
    assert r2["resultado"] == "divergencia_registrada" and r2["filas_insertadas"] == 0
    assert meta2.get("persistido") is False and not os.path.exists(ruta2)
    ruta3, meta3, r3 = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_TARDE + timedelta(minutes=1))
    assert meta3["sha256"] == meta1["sha256"]
    assert r3["resultado"] == "ya_sellada" and r3["filas_insertadas"] == 0

    assert _huella_ext(LUNES) == sellado and _volcado_sellos(db) == volcado
    assert sorted(os.listdir(S.DIR_EXT)) == archivos == [CANON_CSV, CANON_META]
    assert _cuenta(db, TABLA_INTENTOS) == 0 and _cuenta(db, "divergencias_sello") == 1


def test_un_sello_tardio_va_a_intentos_y_un_disparo_posterior_tampoco_sella(entorno_temporal, base):
    """Emisión después de la apertura objetivo (martes 10:00 NY con el insumo
    del lunes): va a la tabla de intentos. Un disparo posterior, también
    tardío, no sella. ADAPTADO por la R4 del auditor (corrida 15): con el
    MISMO insumo el segundo es `ya_intentada`, cero filas y SIN fila en
    `divergencias_sello` (simétrico con `ya_sellada`: un re-disparo en el
    mismo minuto roto no infla el contador); antes se fijaba una divergencia
    con sha_sellado == sha_nuevo. Con OTRO insumo sigue siendo divergencia."""
    db = entorno_temporal
    ruta1, meta1, r1 = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_TARDE)
    assert r1["resultado"] == "intento_no_verificable" and r1["timing_ok"] is False
    assert r1["estado"] == "no_verificable_timing" and r1["cuenta_para_N"] == 0 and r1["filas_insertadas"] == N_OPERABLES
    assert os.path.basename(ruta1) == NV_CSV and S.sello_previo(LUNES, db) is None
    assert S.intento_previo(LUNES, db) == {"sha256": meta1["sha256"], "archivo": NV_CSV}
    huella = _huella_archivos((NV_CSV, NV_META))

    _, meta2, r2 = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_TARDE + timedelta(hours=1))
    assert meta2["sha256"] == meta1["sha256"]
    assert r2["resultado"] == "ya_intentada" and r2["filas_insertadas"] == 0
    assert "estado" not in r2 and "cuenta_para_N" not in r2               # no describe un intento que no ocurrió
    assert _cuenta(db, "sellos_dinero") == 0 and _cuenta(db, TABLA_INTENTOS) == N_OPERABLES and _cuenta(db, "divergencias_sello") == 0
    assert sorted(os.listdir(S.DIR_EXT)) == [NV_CSV, NV_META] and _huella_archivos((NV_CSV, NV_META)) == huella
    _, meta3, r3 = _camino_main(_ext_con_ultima_fila(base, 1.03), db, T_TARDE + timedelta(hours=2))
    assert meta3["sha256"] != meta1["sha256"] and r3["resultado"] == "divergencia_registrada"
    assert _cuenta(db, "divergencias_sello") == 1 and _cuenta(db, TABLA_INTENTOS) == N_OPERABLES
    e = S.estado(db)
    assert e["filas"] == 0 and e["sesiones_selladas"] == 0 and e["ultimo"] is None and e["intentos_no_verificables"] == 1


def test_los_intentos_no_verificables_no_se_reescriben_ni_se_borran(entorno_temporal, base):
    """Misma inmutabilidad que `sellos_dinero`: los disparadores abortan."""
    db = entorno_temporal
    _camino_main(_ext_con_ultima_fila(base, 0.98), db, T_INTRADIA)
    con = sqlite3.connect(db)
    with pytest.raises(sqlite3.IntegrityError, match="no se reescriben"):
        con.execute(f"UPDATE {TABLA_INTENTOS} SET decision = 'compra'")
    with pytest.raises(sqlite3.IntegrityError, match="no se borran"):
        con.execute(f"DELETE FROM {TABLA_INTENTOS}")
    con.close()
    assert _cuenta(db, TABLA_INTENTOS) == N_OPERABLES


def test_la_tabla_de_intentos_tiene_las_mismas_columnas_que_la_principal(entorno_temporal):
    con = S.conectar(entorno_temporal)
    principal = con.execute("PRAGMA table_info(sellos_dinero)").fetchall()
    intentos = con.execute(f"PRAGMA table_info({TABLA_INTENTOS})").fetchall()
    con.close()
    assert principal == intentos and len(principal) == 36          # id + las 35 columnas que INSERT escribe


def test_sin_red_jamas_levanta_un_archivo_no_verificable(entorno_temporal, base):
    """Política §5.4: `es_extension_sellable` sólo acepta `ext_YYYY-MM-DD.csv`.
    Con sólo el par no verificable en la carpeta no hay insumo; con un
    canónico más viejo al lado, `--sin-red` levanta ese y no el no
    verificable más nuevo (que ordena después)."""
    db = entorno_temporal
    assert not S.es_extension_sellable(NV_CSV) and not S.es_extension_sellable(NV_META)
    assert S.es_extension_no_verificable(NV_CSV) and S.es_extension_no_verificable("/x/" + NV_CSV)
    assert not S.es_extension_no_verificable(CANON_CSV) and not S.es_extension_no_verificable(NV_META)
    _camino_main(_ext_con_ultima_fila(base, 0.98), db, T_INTRADIA)
    assert sorted(os.listdir(S.DIR_EXT)) == [NV_CSV, NV_META] and S.ultima_extension() is None
    _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.01), db, datetime(2026, 9, 9, 3, 0, tzinfo=UTC))
    ruta_u, meta_u = S.ultima_extension()
    assert os.path.basename(ruta_u) == f"ext_{FECHA}.csv" and "cupo_canonico" not in meta_u
    assert sorted(os.listdir(S.DIR_EXT))[-1] == NV_META          # el no verificable ordena después y no se levanta


def test_evaluar_timing_es_una_sola_formula_para_congelar_y_sellar(base):
    """El timing se calcula en una función pura que usan `congelar_extension`
    y `sellar`, para que no haya dos fórmulas: available_at < emisión <
    apertura objetivo, con available_at por calendario y nunca el reloj."""
    import inspect
    disp = precios.disponibilidad_por_ticker(_ext_con_ultima_fila(base, 1.0))
    t = S.evaluar_timing(disp, LUNES, T_INTRADIA)
    assert t["avail"] == "2026-09-14T20:00:00+00:00" and t["sesion_obj"] == "2026-09-15"
    assert t["apertura_obj"].isoformat().startswith("2026-09-15T13:30") and t["timing_ok"] is False
    assert S.evaluar_timing(disp, LUNES, T_NOCHE)["timing_ok"] is True
    assert S.evaluar_timing(disp, LUNES, T_TARDE)["timing_ok"] is False
    assert S.evaluar_timing(disp, LUNES, datetime(2026, 9, 15, 13, 30, tzinfo=UTC))["timing_ok"] is False   # la apertura misma no es antes
    assert S.evaluar_timing(disp, LUNES, datetime(2026, 9, 14, 20, 0, tzinfo=UTC))["timing_ok"] is False    # el cierre mismo tampoco
    assert S.evaluar_timing({}, LUNES, T_NOCHE)["avail"] == "2026-09-14T20:00:00+00:00"                  # sin meta: cierre por calendario
    with pytest.raises(ValueError, match="zona horaria"):
        S.evaluar_timing(disp, LUNES, datetime(2026, 9, 15, 3, 30))
    for fn in (S.sellar, S.congelar_extension):
        assert "evaluar_timing(" in inspect.getsource(fn) and "proxima_sesion_despues_de(" not in inspect.getsource(fn)


def test_una_evidencia_congelada_como_no_verificable_no_sella_aunque_el_reloj_del_sello_diga_ok(entorno_temporal, base):
    """Entre congelar y sellar pasan segundos. Si el cierre cae en el medio,
    `congelar_extension` vio timing roto (la barra se congeló ANTES de ser
    conocible) y `sellar` lo vería ok. Manda la clase de la evidencia: el
    reloj del sello sólo puede endurecer el veredicto, nunca ablandarlo."""
    db = entorno_temporal
    ruta, meta = S.congelar_extension(_ext_con_ultima_fila(base, 0.98), BASE_HASTA,
                                      ahora_utc=datetime(2026, 9, 14, 19, 59, 58, tzinfo=UTC))
    assert os.path.basename(ruta) == NV_CSV and meta["cupo_canonico"] is False
    r = S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 14, 20, 0, 2, tzinfo=UTC), ruta_db=db)
    assert r["resultado"] == "intento_no_verificable" and r["timing_ok"] is False and r["estado_timing"] == "roto"
    assert _cuenta(db, "sellos_dinero") == 0 and _cuenta(db, TABLA_INTENTOS) == N_OPERABLES


def test_un_rechazo_por_evidencia_canonica_deja_fila_en_divergencias_y_cero_en_las_dos_tablas(entorno_temporal, base):
    """El caso inverso: la evidencia se congeló con timing ok (nombre canónico)
    y la apertura se cruzó antes de sellar; o `--sin-red` levanta un canónico
    que nunca se selló. Una fila de intentos citando un canónico rompería el
    invariante de la política (§5.2), y una fila en la principal con timing
    roto es lo que este parche cierra. Se rechaza: cero filas en las dos
    tablas de filas, el archivo no se toca, y (B1 del auditor, corrida 15) el
    rastro queda en `divergencias_sello` con sha_sellado = sha_nuevo = el
    propio insumo rechazado y un detalle que dice qué es cada cosa."""
    db = entorno_temporal
    ruta, meta = S.congelar_extension(_ext_con_ultima_fila(base, 1.02), BASE_HASTA,
                                      ahora_utc=datetime(2026, 9, 15, 13, 29, 58, tzinfo=UTC))
    assert os.path.basename(ruta) == CANON_CSV and "cupo_canonico" not in meta
    huella = _huella_ext(LUNES)
    t_sello = datetime(2026, 9, 15, 13, 30, 2, tzinfo=UTC)
    r = S.sellar(ruta, meta, ahora_utc=t_sello, ruta_db=db)
    assert r["resultado"] == "rechazado_evidencia_canonica" and r["filas_insertadas"] == 0 and r["timing_ok"] is False
    assert "estado" not in r and "cuenta_para_N" not in r                  # no describe un sello que no ocurrió
    assert _cuenta(db, "sellos_dinero") == 0 and _cuenta(db, TABLA_INTENTOS) == 0
    assert _cuenta(db, "divergencias_sello") == 1
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    fecha, ts, sha_s, sha_n, distintas, detalle = con.execute(
        "SELECT fecha_insumo, timestamp_utc, sha_sellado, sha_nuevo, decisiones_distintas, detalle FROM divergencias_sello").fetchone()
    con.close()
    assert (fecha, ts, sha_s, sha_n, distintas) == (LUNES, t_sello.isoformat(), meta["sha256"], meta["sha256"], 0)
    assert "nombre canónico" in detalle and "propio insumo rechazado" in detalle and "no el de un sello" in detalle
    assert "available_at=2026-09-14T20:00:00+00:00" in detalle and f"emision={t_sello.isoformat()}" in detalle
    assert "apertura_objetivo=2026-09-15T13:30:00+00:00" in detalle
    assert _huella_ext(LUNES) == huella and sorted(os.listdir(S.DIR_EXT)) == [CANON_CSV, CANON_META]
    assert S.estado(db)["divergencias_registradas"] == 1 and S.estado(db)["intentos_no_verificables"] == 0


def test_exportar_y_respaldar_cubren_el_par_no_verificable(entorno_temporal, base):
    """Política §4: `exportar_csv` exporta la tabla nueva a
    `<ruta>_no_verificables.csv` y `respaldar_extension` copia el par
    `.no_verificable` con el mismo nombre (deriva el meta con splitext, y
    `ext_F.no_verificable` + `.meta.json` es el nombre que congelar escribió)."""
    db = entorno_temporal
    raiz = os.path.dirname(db)
    ruta1, meta1, _ = _camino_main(_ext_con_ultima_fila(base, 0.98), db, T_INTRADIA)
    ruta2, meta2, _ = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_NOCHE)
    csvp = S.exportar_csv(db, os.path.join(raiz, "sello_dinero.csv"))
    principal = pd.read_csv(csvp)
    nv = pd.read_csv(os.path.join(raiz, "sello_dinero_no_verificables.csv"))
    assert list(nv.columns) == list(principal.columns) and len(nv) == len(principal) == N_OPERABLES
    assert set(nv["estado"]) == {"no_verificable_timing"} and set(principal["estado"]) == {"pendiente"}
    assert set(nv["insumo_ext_archivo"]) == {NV_CSV} and set(principal["insumo_ext_archivo"]) == {CANON_CSV}
    assert os.path.exists(os.path.join(raiz, "sello_dinero_divergencias.csv"))
    copias = S.respaldar_extension(ruta1, S.DIR_BACKUP_EXT) + S.respaldar_extension(ruta2, S.DIR_BACKUP_EXT)
    assert sorted(os.path.basename(c) for c in copias) == [CANON_CSV, CANON_META, NV_CSV, NV_META]
    assert S._sha256(os.path.join(S.DIR_BACKUP_EXT, NV_CSV)) == meta1["sha256"]
    assert S._sha256(os.path.join(S.DIR_BACKUP_EXT, CANON_CSV)) == meta2["sha256"]


def test_estado_agrega_los_intentos_sin_cambiar_las_claves_que_lee_la_api(entorno_temporal, base):
    claves_api = {"filas", "sesiones_selladas", "sesiones_que_cuentan_para_N", "N_objetivo", "N_objetivo_fuente",
                  "fuente_conteos", "ultimo", "filas_ultimo_sello", "divergencias_registradas", "senal_fuente", "estatus"}
    db = entorno_temporal
    vacio = S.estado(db)                                       # la base no existe todavía
    assert claves_api <= set(vacio) and vacio["intentos_no_verificables"] == 0
    _camino_main(_ext_con_ultima_fila(base, 0.98), db, T_INTRADIA)
    e = S.estado(db)
    assert claves_api <= set(e) and e["intentos_no_verificables"] == 1
    assert e["filas"] == 0 and e["sesiones_selladas"] == 0 and e["ultimo"] is None and e["filas_ultimo_sello"] == []


def test_una_base_sin_la_tabla_de_intentos_se_lee_como_cero_intentos(tmp_path, base):
    """La base real no tiene la tabla hasta que el sellador parcheado la cree
    (`CREATE TABLE IF NOT EXISTS`, aditivo). Leerla antes no es un error: cero
    intentos. Y crearla no toca nada de lo que ya hay."""
    db = str(tmp_path / "vieja.db")
    con = sqlite3.connect(db)
    con.executescript(S._ddl_filas("sellos_dinero") + S._DDL_DIVERGENCIAS)       # el esquema de E0.2
    con.commit(); con.close()
    assert S.intento_previo(LUNES, db) is None and S.sello_previo(LUNES, db) is None
    assert S.estado(db)["intentos_no_verificables"] == 0 and S.estado(db)["filas"] == 0
    S.exportar_csv(db, str(tmp_path / "v.csv"))
    assert os.path.exists(str(tmp_path / "v.csv")) and not os.path.exists(str(tmp_path / "v_no_verificables.csv"))
    ruta, meta = _extension_sintetica(tmp_path, base, ("2026-09-08",))
    r = S.sellar(ruta, meta, ahora_utc=datetime(2026, 9, 9, 3, 0, tzinfo=UTC), ruta_db=db)
    assert r["resultado"] == "sellada"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    tablas = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    con.close()
    assert {"sellos_dinero", TABLA_INTENTOS, "divergencias_sello"} <= tablas
    assert _cuenta(db, "sellos_dinero") == N_OPERABLES and _cuenta(db, TABLA_INTENTOS) == 0


def _insertar_fila_vieja(db, fecha, ticker, sha, archivo, estado, estado_timing, version_sello):
    """Una fila como las que E0.2 dejó en `sellos_dinero` el 28-sep: se
    fabrica con INSERT (los disparadores prohíben UPDATE y DELETE, no INSERT)
    con las columnas NOT NULL y las que el test mira. No nombra esa fecha."""
    con = S.conectar(db)
    con.execute("INSERT INTO sellos_dinero (fecha_sello, fecha_insumo, timestamp_utc, exchange, ticker, decision, "
                "tamano_nominal, senal_fuente, juego, presupuesto_usd, reglas_version, insumo_ext_sha256, "
                "insumo_ext_archivo, insumo_base_sha256, plataforma_version, version_sello, estado, estado_timing, "
                "cuenta_para_N, creado_en) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (fecha, fecha, f"{fecha}T17:43:01+00:00", "XNYS", ticker, "nada", 0, S.SENAL_FUENTE, "conservador",
                 500.0, "?", sha, archivo, "0" * 64, S.PLATAFORMA_VERSION, version_sello, estado, estado_timing, 0,
                 f"{fecha}T17:43:01+00:00"))
    con.commit(); con.close()


def test_las_filas_no_verificables_viejas_de_la_tabla_principal_siguen_ocupando_su_fecha(entorno_temporal, base):
    """Punto 5 del diseño: las filas `no_verificable_timing` que E0.2 dejó en
    `sellos_dinero` se quedan donde están. `sello_previo()` sigue devolviendo
    esa fecha (UNIQUE impediría igual insertar las buenas, y la sesión ya
    pasó) y un disparo posterior entra por divergencia, como hoy. El código
    no nombra ninguna fecha; acá se fabrica una."""
    db = entorno_temporal
    _insertar_fila_vieja(db, FECHA, "NVDA", "a" * 64, f"ext_{FECHA}.csv", "no_verificable_timing", "roto", "E0.2")
    assert S.sello_previo(FECHA, db) == {"sha256": "a" * 64, "archivo": f"ext_{FECHA}.csv"}
    assert S.intento_previo(FECHA, db) is None
    ruta, meta, r = _camino_main(_cierres_ext_sinteticos(base, (FECHA,), 1.01), db, datetime(2026, 9, 9, 3, 0, tzinfo=UTC))
    assert r["resultado"] == "divergencia_registrada" and r["filas_insertadas"] == 0
    assert meta.get("persistido") is False and os.listdir(S.DIR_EXT) == []
    assert _cuenta(db, "sellos_dinero") == 1 and _cuenta(db, TABLA_INTENTOS) == 0


def test_integridad_de_punta_a_punta_con_intento_y_sello_de_la_misma_fecha(entorno_temporal, base):
    """Política §5: cada tabla contra sus archivos, en las dos carpetas; «un
    solo insumo por fecha» vale por tabla (una fecha puede tener un intento y
    un sello: dos insumos, cada uno en su tabla); ninguna tabla cita la
    evidencia de la otra; y ninguna fila con timing roto en la principal
    lleva la versión del corte."""
    db = entorno_temporal
    ruta1, _, _ = _camino_main(_ext_con_ultima_fila(base, 0.98), db, T_INTRADIA)
    ruta2, _, _ = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_NOCHE)
    S.respaldar_extension(ruta1, S.DIR_BACKUP_EXT); S.respaldar_extension(ruta2, S.DIR_BACKUP_EXT)
    citas = {t: _citas_selladas(db, t) for t in TABLAS_CON_EVIDENCIA}
    assert len(citas["sellos_dinero"]) == len(citas[TABLA_INTENTOS]) == 1
    for t in TABLAS_CON_EVIDENCIA:
        _verificar_citas_en(S.DIR_EXT, citas[t])
        _verificar_citas_en(S.DIR_BACKUP_EXT, citas[t])
    _verificar_clase_de_evidencia(citas["sellos_dinero"], citas[TABLA_INTENTOS])
    _verificar_regla_del_corte(_filas_rotas_en_principal(db))
    # y con las dos citas juntas el chequeo viejo (una sola tabla) diría «dos insumos»: por eso es por tabla
    with pytest.raises(AssertionError, match="shas distintos"):
        _verificar_citas_en(S.DIR_EXT, citas["sellos_dinero"] + citas[TABLA_INTENTOS])


def test_contraprueba_la_integridad_ve_la_clase_equivocada_y_la_fila_rota_posterior_al_corte():
    """Un verificador que no puede fallar no verifica."""
    sha = "0" * 64
    _verificar_clase_de_evidencia([(LUNES, CANON_CSV, sha)], [(LUNES, NV_CSV, sha)])                  # cada una la suya: pasa
    with pytest.raises(AssertionError, match="PARAR Y REPORTAR"):
        _verificar_clase_de_evidencia([(LUNES, NV_CSV, sha)], [])                                    # la principal cita un .no_verificable
    with pytest.raises(AssertionError, match="PARAR Y REPORTAR"):
        _verificar_clase_de_evidencia([], [(LUNES, CANON_CSV, sha)])                                 # los intentos citan un canónico
    _verificar_regla_del_corte([(FECHA, "no_verificable_timing", "roto", "E0.2")])                  # anterior al corte: tolerada
    _verificar_regla_del_corte([])
    with pytest.raises(AssertionError, match="PARAR Y REPORTAR"):
        _verificar_regla_del_corte([(FECHA, "no_verificable_timing", "roto", VERSION_CORTE_DE_METODO)])
    with pytest.raises(AssertionError, match="PARAR Y REPORTAR"):
        _verificar_regla_del_corte([(FECHA, "pendiente", "roto", "E0.10")])                          # E0.10 > E0.3: no es orden de texto
    assert S.VERSION_SELLO == VERSION_CORTE_DE_METODO


def test_un_cambio_de_juego_entre_dos_disparos_no_inserta_filas_que_citen_un_archivo_que_main_borra(entorno_temporal, base):
    """F3 del auditor (corrida 16-2), reproducida: con la fecha ya sellada por
    el juego A y OTRO insumo, `congelar_extension` manda el insumo al temporal
    (E4-bis, correcto), pero `previas` filtra por juego, así que un disparo
    con `juego_activo` = B llegaba al INSERT y dejaba filas citando
    `ext_<fecha>_divergente_….csv`, que `main()` borra: integridad rota para
    siempre, idéntica en E0.2 y en E0.3 sin la guarda R1. Ahora: cero filas en
    las dos tablas, una fila en `divergencias_sello` que lo declara, y la
    integridad en pie. Rojo sobre el camino T sin R1 por su propia aserción."""
    db = entorno_temporal
    cfg_a = U.reglas()
    assert cfg_a["juego_activo"] == "conservador" and "agresivo" in cfg_a["juegos"]
    ruta1, meta1, r1 = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_NOCHE)
    assert r1["resultado"] == "sellada" and r1["juego"] == "conservador"
    cfg_b = dict(cfg_a, juego_activo="agresivo")
    t2 = T_NOCHE + timedelta(minutes=1)
    ruta2, meta2 = _congelar(_ext_con_ultima_fila(base, 1.03), BASE_HASTA, t2)
    assert meta2["persistido"] is False and meta2["sha256"] != meta1["sha256"]
    try:
        r2 = S.sellar(ruta2, meta2, ahora_utc=t2, ruta_db=db, cfg=cfg_b)
    finally:
        if os.path.exists(ruta2):
            os.remove(ruta2)                                    # lo que hace main()
    assert r2["filas_insertadas"] == 0, (
        "F3: sellar insertó filas con juego 'agresivo' que citan un archivo que main() borra "
        f"(resultado={r2['resultado']!r}, filas_insertadas={r2['filas_insertadas']})")
    assert r2["resultado"] == "rechazado_insumo_no_persistido" and r2["juego"] == "agresivo"
    assert r2["sha_sellado"] == meta1["sha256"] and r2["insumo_ext_sha256"] == meta2["sha256"]
    assert _cuenta(db, "sellos_dinero") == N_OPERABLES and _cuenta(db, TABLA_INTENTOS) == 0
    assert _cuenta(db, "divergencias_sello") == 1
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    sha_s, sha_n, distintas, detalle = con.execute(
        "SELECT sha_sellado, sha_nuevo, decisiones_distintas, detalle FROM divergencias_sello").fetchone()
    con.close()
    assert (sha_s, sha_n, distintas) == (meta1["sha256"], meta2["sha256"], None)
    assert "NO persistido" in detalle and "'agresivo'" in detalle and "R1 del auditor" in detalle
    # la integridad permanente queda en pie: toda cita apunta a un archivo que existe
    _verificar_citas_en(S.DIR_EXT, _citas_selladas(db, "sellos_dinero"))
    assert sorted(os.listdir(S.DIR_EXT)) == [CANON_CSV, CANON_META]
