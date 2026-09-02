"""Frente C (octava corrida): la prueba maestra que faltaba para `cargar()`.

El auditor de fuga la corrió como sonda y exigió que viva en `tests/` antes
de abrir la prueba: el valor de cada fila en t es invariante a truncar los
testigos en t (gap, sesión y sox_prev son razones: estacionarias por
construcción). Con contraprueba: un `shift(-1)` en `sox_prev` dispara.
"""
import json
import os

import numpy as np
import pandas as pd
import pytest

from GEMELO import no_capturabilidad as nc

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def completo():
    return nc.cargar()


@pytest.mark.parametrize("corte", ["2021-03-15", "2023-12-29", "2024-06-14"])
def test_cargar_es_invariante_a_truncar_en_t(completo, corte):
    trunc = nc.cargar(hasta=corte)
    assert trunc["fecha"].max() <= pd.Timestamp(corte)
    ref = completo[completo["fecha"] <= corte]
    m = ref.merge(trunc, on=["fecha", "ticker"], suffixes=("_ref", "_tr"))
    assert len(m) == len(trunc) == len(ref)
    for col in ("gap_pct", "sesion_pct", "sox_prev"):
        assert np.abs(m[f"{col}_ref"] - m[f"{col}_tr"]).max() == 0.0


def test_contraprueba_un_shift_hacia_el_futuro_dispara(completo, monkeypatch):
    original = pd.merge_asof

    def con_fuga(*a, **kw):
        out = original(*a, **kw)
        out["sox_prev"] = out["sox_prev"].shift(-1)
        return out
    monkeypatch.setattr(pd, "merge_asof", con_fuga)
    trunc = nc.cargar(hasta="2023-12-29")
    ref = completo[completo["fecha"] <= "2023-12-29"]
    m = ref.merge(trunc, on=["fecha", "ticker"], suffixes=("_ref", "_tr")).dropna()
    assert np.abs(m["sox_prev_ref"] - m["sox_prev_tr"]).max() > 1.0


def test_no_hay_barra_intradia_ni_fila_sellada_en_la_prueba(completo):
    assert completo["fecha"].max() <= pd.Timestamp(nc.ULTIMA_BARRA_COMPLETA)
    pr_ = nc.ventana_prueba(completo)
    assert ((pr_["fecha"] >= nc.SELLADA[0]) & (pr_["fecha"] <= nc.SELLADA[1])).sum() == 0
    bd = pd.tseries.offsets.BDay(nc.EMBARGO_SESIONES)
    assert pr_["fecha"].max() < pd.Timestamp(nc.SELLADA[0]) - bd


def test_sellada_se_deriva_del_backup_y_cubre_las_sesiones_objetivo():
    b = pd.read_csv(nc.RUTA_BACKUP_SENALES, usecols=["sesion_objetivo"])
    so = pd.to_datetime(b["sesion_objetivo"]).dropna()
    assert nc.SELLADA == (so.min().strftime("%Y-%m-%d"), so.max().strftime("%Y-%m-%d"))


def test_el_candado_no_deja_reabrir_con_otro_hash(tmp_path, monkeypatch):
    monkeypatch.setattr(nc, "RUTA_LOCK", str(tmp_path / "lock.json"))
    primero = nc.candado_de_apertura()
    assert nc.candado_de_apertura()["sha256"] == primero["sha256"]      # mismo código: reproduce
    with open(nc.RUTA_LOCK, "w") as f:
        json.dump({**primero, "sha256": "0" * 64}, f)
    with pytest.raises(RuntimeError):
        nc.candado_de_apertura()


def test_bootstrap_de_bloques_circulares_cubre_toda_la_serie():
    rng = np.random.default_rng(0)
    idx = nc._indices_bloques(rng, 23, 500, 10)
    assert idx.shape == (500, 23) and idx.min() == 0 and idx.max() == 22
    # dentro de un bloque las fechas son consecutivas (módulo n)
    assert ((idx[:, 1] - idx[:, 0]) % 23 == 1).all()


def test_el_candado_con_enmienda_deja_rastro_y_cubre_los_datos(tmp_path, monkeypatch):
    monkeypatch.setattr(nc, "RUTA_LOCK", str(tmp_path / "lock.json"))
    primero = nc.candado_de_apertura()
    assert set(primero["datos"]) == {"GEMELO/resultados/testigos_fuente/" + os.path.basename(r)
                                     for r in (nc.RUTA_GAPS_GZ, nc.RUTA_CIERRES_GZ, nc.RUTA_SOX_GZ)}
    with open(nc.RUTA_LOCK, "w") as f:
        json.dump({**primero, "sha256": "0" * 64}, f)
    with pytest.raises(RuntimeError):
        nc.candado_de_apertura()                       # sin razón: no se reabre
    lock = nc.candado_de_apertura(enmienda="prueba de rastro")
    assert lock["sha256"] == primero["sha256"] and lock["enmiendas"][0]["razon"] == "prueba de rastro"
    assert lock["enmiendas"][0]["sha256_anterior"] == "0" * 64


def test_contar_intervalos_cuenta_cada_ic_publicado():
    o = {"a": {"punto": 1, "ic95": [0, 2]}, "b": [{"punto": 0, "ic95": [0, 0]}, {"x": {"punto": 1, "ic95": [1, 1]}}], "c": 3}
    assert nc.contar_intervalos(o) == 3
