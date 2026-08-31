# ============================================================
# Tests del Frente D — registro de divergencias titular/réplica
# (docs/REPLICA.md, módulo replica.py).
#
# Lo que estos tests protegen: que el registro sea SOLO auditoría —
# escribe hallazgos cuando de verdad hay una DIVERGENCIA, nunca por una
# ausencia legítima (corte, huella de copia, pendiente de push), y nunca
# decide "quién gana" (resuelto_como queda en NULL siempre). Todo corre
# contra bases sqlite sintéticas en tmp_path — nunca contra senales.db ni
# noticias.db reales.
# ============================================================

import os
import sys
from datetime import date

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import comparar_sombra as cs
import replica


FECHA_OK = "2026-08-26"     # posterior a FECHA_CORTE, como en test_sombra.py
POSTERIOR = "2026-08-27"    # el titular ya publicó ESTE día


def _snap(fecha=FECHA_OK, **cambios):
    fila = {"fecha": fecha, "creado_en": f"{fecha}T22:00:00.118402+00:00",
            "regimen": "Alcista · vol alta", "roca_chip": 50.0,
            "timestamp_utc": f"{fecha}T22:00:00.118402+00:00",
            "origen": "programado",
            "modelo_version": "4.6.0", "feature_version": "4.6.0",
            "universo_version": "4.6.0", "ventana_betas": 120.0,
            "descarga_ok": 28.0, "descarga_total": 28.0, "descarga_caidos": None,
            "plataforma_version": "5.0.2", "sox_usado_pct": -2.7,
            "sox_fecha": fecha}
    fila.update(cambios)
    return fila


def _sombra_snap(fecha=FECHA_OK, **cambios):
    base = {"creado_en": f"{fecha}T22:00:04.771903+00:00",
            "timestamp_utc": f"{fecha}T22:00:04.771903+00:00",
            "plataforma_version": "5.0.3"}
    base.update(cambios)
    return _snap(fecha=fecha, **base)


def _ticker(ticker="2330.TW", fecha=FECHA_OK, **cambios):
    fila = {"fecha": fecha, "ticker": ticker, "puntaje_v0": 0.57,
            "sentimiento_ia": 0.4488513020729087, "puntaje_ia": 0.6163,
            "apertura_estimada_pct": -1.03, "confianza_r2": 0.2846,
            "timestamp_utc": f"{fecha}T22:00:00+00:00", "exchange": "XTAI",
            "sesion_objetivo": "2026-08-27",
            "available_at": f"{fecha}T20:00:00+00:00", "estado": "pendiente",
            "intervalo80_pp": 2.66, "n_muestra": 120.0,
            "modelo_version": "4.6.0", "beta": 0.38}
    fila.update(cambios)
    return fila


def _montar(monkeypatch, snap_sombra, tickers_sombra):
    def falso(tabla, fecha):
        if tabla == "snapshots":
            return pd.DataFrame([snap_sombra] if snap_sombra else [])
        return pd.DataFrame(tickers_sombra)
    monkeypatch.setattr(cs, "leer_tabla_local", falso)


def _ruta_db(tmp_path):
    return str(tmp_path / "divergencias_replica.db")


# ------------------------------------------------------------
# (a) las dos máquinas sellan la misma fecha y coinciden → PARIDAD,
#     se registra sin ninguna fila de divergencia.
# ------------------------------------------------------------
def test_paridad_no_registra_ninguna_divergencia(monkeypatch, tmp_path):
    _montar(monkeypatch, _sombra_snap(), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_PARIDAD

    ruta = _ruta_db(tmp_path)
    n = replica.registrar_comparacion(res, ruta_db=ruta)

    assert n == 0
    assert replica.leer_divergencias(ruta) == []


# ------------------------------------------------------------
# (b) las dos máquinas sellan la misma fecha y DIFIEREN → al menos una
#     fila de divergencia, con su clase correcta.
# ------------------------------------------------------------
def test_divergencia_de_computo_se_registra_con_su_clase(monkeypatch, tmp_path):
    """beta distinto con los mismos insumos declarados es, por diseño,
    'cómputo' (docs/REPLICA.md §1: mismos insumos, resultado distinto)."""
    _montar(monkeypatch, _sombra_snap(), [_ticker(beta=0.39)])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker(beta=0.38)]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA

    ruta = _ruta_db(tmp_path)
    n = replica.registrar_comparacion(res, ruta_db=ruta)
    assert n == len(res["hallazgos"]) and n >= 1

    filas = replica.leer_divergencias(ruta, fecha=FECHA_OK)
    beta_filas = [f for f in filas if f["campo"] == "beta"]
    assert len(beta_filas) == 1
    f = beta_filas[0]
    assert f["clase"] == replica.CLASE_COMPUTO
    assert f["valor_titular"] == "0.38" and f["valor_sombra"] == "0.39"
    assert f["tolerancia_excedida"] == 1
    assert f["resuelto_como"] is None   # nunca se decide quién gana


def test_divergencia_de_insumos_se_registra_con_su_clase(monkeypatch, tmp_path):
    """sox_fecha distinto = cierres del SOX de días distintos: eso es el
    mundo siendo asíncrono (§1), no un desacuerdo de cómputo."""
    _montar(monkeypatch, _sombra_snap(sox_fecha="2026-08-25"), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap(sox_fecha="2026-08-26")]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA

    ruta = _ruta_db(tmp_path)
    replica.registrar_comparacion(res, ruta_db=ruta)
    filas = replica.leer_divergencias(ruta, fecha=FECHA_OK)
    sox_filas = [f for f in filas if f["campo"] == "sox_fecha"]
    assert len(sox_filas) == 1
    assert sox_filas[0]["clase"] == replica.CLASE_INSUMOS


def test_divergencia_de_existencia_por_conjunto_de_tickers(monkeypatch, tmp_path):
    _montar(monkeypatch, _sombra_snap(), [_ticker("2330.TW")])
    res = cs.comparar_fecha(
        FECHA_OK, pd.DataFrame([_snap()]),
        pd.DataFrame([_ticker("2330.TW"), _ticker("005930.KS")]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA

    ruta = _ruta_db(tmp_path)
    replica.registrar_comparacion(res, ruta_db=ruta)
    filas = replica.leer_divergencias(ruta, fecha=FECHA_OK)
    conjunto_filas = [f for f in filas if f["campo"] == "tickers_sellados"]
    assert len(conjunto_filas) == 1
    assert conjunto_filas[0]["clase"] == replica.CLASE_EXISTENCIA


def test_divergencia_sin_hallazgos_de_campo_se_registra_como_sello_ausente(
        monkeypatch, tmp_path):
    """El titular selló y la sombra no: comparar_fecha da DIVERGENCIA con
    hallazgos == [] (la ausencia misma es el hallazgo). Debe quedar UNA
    fila, no cero."""
    _montar(monkeypatch, None, [])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA
    assert res["hallazgos"] == []

    ruta = _ruta_db(tmp_path)
    n = replica.registrar_comparacion(res, ruta_db=ruta)
    assert n == 1
    filas = replica.leer_divergencias(ruta, fecha=FECHA_OK)
    assert len(filas) == 1
    assert filas[0]["campo"] == replica.CAMPO_SELLO_AUSENTE
    assert filas[0]["clase"] == replica.CLASE_EXISTENCIA
    assert filas[0]["resuelto_como"] is None


# ------------------------------------------------------------
# (c) una máquina (el titular) no selló esa fecha → DIA_NO_COMPUTABLE o
#     PENDIENTE_PUBLICACION según corresponda, y CERO filas de divergencia
#     por una ausencia legítima.
# ------------------------------------------------------------
def test_dia_no_computable_no_registra_ninguna_divergencia(monkeypatch, tmp_path):
    """El titular no publicó esta fecha, pero sí publicó una posterior:
    ausencia DEFINITIVA → DIA_NO_COMPUTABLE, día perdido, no divergencia."""
    _montar(monkeypatch, _sombra_snap(), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap(fecha=POSTERIOR)]),
                            pd.DataFrame([_ticker(fecha=POSTERIOR)]))
    assert res["veredicto"] == cs.VEREDICTO_NO_COMPUTABLE

    ruta = _ruta_db(tmp_path)
    n = replica.registrar_comparacion(res, ruta_db=ruta)
    assert n == 0
    assert replica.leer_divergencias(ruta) == []


def test_pendiente_publicacion_no_registra_ninguna_divergencia(monkeypatch, tmp_path):
    """Ausencia AMBIGUA (sin fila del titular y sin sellos posteriores):
    PENDIENTE_PUBLICACION, no es un día perdido ni una divergencia — se
    resuelve re-ejecutando después del push."""
    _montar(monkeypatch, _sombra_snap(), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame(columns=["fecha"]),
                            pd.DataFrame(columns=["fecha", "ticker"]))
    assert res["veredicto"] == cs.VEREDICTO_PENDIENTE

    ruta = _ruta_db(tmp_path)
    n = replica.registrar_comparacion(res, ruta_db=ruta)
    assert n == 0
    assert replica.leer_divergencias(ruta) == []


def test_huella_de_copia_no_registra_ninguna_divergencia(monkeypatch, tmp_path):
    """La huella de base copiada rechaza la comparación entera (DIA_NO_
    COMPUTABLE): una paridad trivial tampoco es evidencia de divergencia."""
    _montar(monkeypatch, _snap(), [_ticker()])       # misma fila = huella
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_NO_COMPUTABLE

    ruta = _ruta_db(tmp_path)
    n = replica.registrar_comparacion(res, ruta_db=ruta)
    assert n == 0


# ------------------------------------------------------------
# Aditividad / inmutabilidad del registro
# ------------------------------------------------------------
def test_registrar_es_aditivo_entre_corridas(monkeypatch, tmp_path):
    """Dos corridas de días distintos con divergencia se ACUMULAN — la
    segunda no borra ni pisa la primera."""
    ruta = _ruta_db(tmp_path)

    _montar(monkeypatch, _sombra_snap(), [_ticker(beta=0.39)])
    res1 = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                             pd.DataFrame([_ticker(beta=0.38)]))
    replica.registrar_comparacion(res1, ruta_db=ruta)

    otro_dia = "2026-08-28"
    _montar(monkeypatch, _sombra_snap(fecha=otro_dia), [_ticker(fecha=otro_dia, beta=0.50)])
    res2 = cs.comparar_fecha(otro_dia, pd.DataFrame([_snap(fecha=otro_dia)]),
                             pd.DataFrame([_ticker(fecha=otro_dia, beta=0.45)]))
    replica.registrar_comparacion(res2, ruta_db=ruta)

    todas = replica.leer_divergencias(ruta)
    fechas = {f["fecha"] for f in todas}
    assert fechas == {FECHA_OK, otro_dia}


def test_no_hay_update_ni_delete_en_el_modulo():
    """Blindaje de inmutabilidad: el módulo nunca reescribe ni borra una
    fila ya escrita."""
    fuente = open(replica.__file__, encoding="utf-8").read()
    assert "conn.execute(\"UPDATE" not in fuente
    assert "\"\"\"UPDATE" not in fuente
    assert "DELETE FROM" not in fuente.upper()


def test_fecha_corte_parametrizable_no_cambia_el_default():
    """Aditividad del cambio en comparar_sombra.py: sin pasar fecha_corte,
    el comportamiento es idéntico al de siempre (FECHA_CORTE del módulo).
    La rama del corte devuelve NO_COMPUTABLE antes de tocar ningún dato
    local, así que ni hace falta montar la lectura local."""
    for f in ("2026-08-24", "2026-08-20"):
        res = cs.comparar_fecha(f, pd.DataFrame([_snap(fecha=f)]),
                                pd.DataFrame([_ticker(fecha=f)]))
        assert res["veredicto"] == cs.VEREDICTO_NO_COMPUTABLE
        assert "corte" in res["motivo"].lower()


def test_fecha_corte_none_se_apoya_solo_en_la_defensa_estructural(monkeypatch):
    """Con fecha_corte=None, una fecha <= FECHA_CORTE deja de rechazarse
    por el corte, pero la huella de copia (si las filas son idénticas)
    sigue rechazando igual — cinturón y tirantes preservado."""
    f = "2026-08-20"
    _montar(monkeypatch, _snap(fecha=f), [_ticker(fecha=f)])  # misma fila = huella
    res = cs.comparar_fecha(f, pd.DataFrame([_snap(fecha=f)]),
                            pd.DataFrame([_ticker(fecha=f)]), fecha_corte=None)
    assert res["veredicto"] == cs.VEREDICTO_NO_COMPUTABLE
    assert "copiada" in res["motivo"].lower()


def test_fecha_corte_none_permite_evaluar_una_fecha_temprana_con_filas_distintas(
        monkeypatch):
    """Sin el corte fijo y sin huella de copia (filas realmente distintas
    de dos máquinas), una fecha temprana ya se puede evaluar de verdad —
    exactamente lo que un rol permanente necesita (docs/REPLICA.md §4)."""
    f = "2026-08-20"
    _montar(monkeypatch, _sombra_snap(fecha=f), [_ticker(fecha=f)])
    res = cs.comparar_fecha(f, pd.DataFrame([_snap(fecha=f)]),
                            pd.DataFrame([_ticker(fecha=f)]), fecha_corte=None)
    assert res["veredicto"] == cs.VEREDICTO_PARIDAD
