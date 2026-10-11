# ============================================================
# tests/test_puntaje_retorno.py — la cuenta de excluidas viaja en el valor
# de retorno de `senales.verificar_puntaje_pendientes` (acta §95.2, R2 del
# auditor de la corrida 16a; corrida 16-1, 10-oct-2026).
#
# Lo que cambia: el verificador devolvía un entero (`verificadas`) y la
# exclusión por conocibilidad (acta §93.4-bis i) sólo vivía en una línea de
# `snapshot.log`, que rota. Ahora devuelve un dict con `verificadas`,
# `excluidas` y `fechas_excluidas`. Lo que NO cambia: qué se escribe en
# `verificacion_puntaje` (ni una fila más ni una menos) y que el `estado`
# de `senales_ticker` no se toca.
#
# El test de conducta de escritura compara, sobre la MISMA siembra, lo que
# escribe esta versión con lo que escribía la versión ANTERIOR al cambio
# (`git show 864606c:senales.py`, importada bajo otro nombre; R2 del
# dictamen 16-1: con `HEAD` el test se volvía tautológico tras el commit).
# El mismo archivo fija, además, las filas esperadas de forma explícita.
#
# Fixture `base_puntaje` reutilizada de tests/test_guarda_puntaje.py (base
# temporal, red reemplazada, guardia contra la base real). Cero intentos del
# DSR.
# ============================================================

import importlib.util
import os
import shutil
import subprocess
import sys
from datetime import date, timedelta

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import senales  # noqa: E402
from test_guarda_puntaje import (  # noqa: E402,F401  (la fixture se registra al importarla)
    EMISION, FECHA_SENAL, INSUMO_ANTERIOR, INSUMO_POSTERIOR, RETORNO_5D_ESPERADO,
    _ohlc_falso, _ro, base_puntaje)

OTRA_FECHA = (date.fromisoformat(FECHA_SENAL) - timedelta(days=7)).isoformat()
OTRA_EMISION = f"{OTRA_FECHA}T21:15:00+00:00"
OTRO_INSUMO_POSTERIOR = f"{OTRA_FECHA}T23:00:00+00:00"


# ------------------------------------------------------------
# Reproducción: el retorno
# ------------------------------------------------------------
def test_reproduccion_el_retorno_lleva_la_cuenta_de_excluidas(base_puntaje):
    """REPRODUCCIÓN (falla sobre HEAD, que devuelve un entero). Dos filas
    invertidas de dos fechas y una fila normal: una verificada, dos
    excluidas, dos fechas, en el retorno y no sólo en stdout."""
    base_puntaje["sembrar"]("005930.KS", EMISION, INSUMO_POSTERIOR)
    base_puntaje["sembrar"]("000660.KS", OTRA_EMISION, OTRO_INSUMO_POSTERIOR, fecha=OTRA_FECHA)
    base_puntaje["sembrar"]("NVDA", EMISION, INSUMO_ANTERIOR)
    r = senales.verificar_puntaje_pendientes()
    assert isinstance(r, dict), r
    assert r == {"verificadas": 1, "excluidas": 2,
                 "fechas_excluidas": sorted([OTRA_FECHA, FECHA_SENAL])}
    _, verificadas = base_puntaje["leer"]()
    assert verificadas == {"NVDA": RETORNO_5D_ESPERADO}


def test_sin_excluidas_el_retorno_dice_cero_y_sin_fechas(base_puntaje):
    base_puntaje["sembrar"]("NVDA", EMISION, INSUMO_ANTERIOR)
    base_puntaje["sembrar"]("005930.KS", EMISION, None)
    assert senales.verificar_puntaje_pendientes() == {
        "verificadas": 2, "excluidas": 0, "fechas_excluidas": []}


def test_sin_candidatas_el_retorno_es_el_mismo_dict(base_puntaje):
    assert senales.verificar_puntaje_pendientes() == {
        "verificadas": 0, "excluidas": 0, "fechas_excluidas": []}


def test_la_cuenta_se_repite_en_cada_corrida_porque_la_fila_sigue_candidata(base_puntaje):
    """La fila excluida no se escribe, así que vuelve a ser candidata en la
    corrida siguiente y se vuelve a contar (trato ratificado en §95.2 b)."""
    base_puntaje["sembrar"]("005930.KS", EMISION, INSUMO_POSTERIOR)
    primera = senales.verificar_puntaje_pendientes()
    segunda = senales.verificar_puntaje_pendientes()
    assert primera == segunda == {"verificadas": 0, "excluidas": 1,
                                  "fechas_excluidas": [FECHA_SENAL]}


def test_verificar_pendientes_devuelve_los_dos_dicts(base_puntaje, monkeypatch):
    monkeypatch.setattr(senales, "verificar_apertura_pendientes",
                        lambda: {"verificadas": 0, "no_verificables": 0,
                                 "sin_datos_mercado": 0, "sin_calendario": 0})
    base_puntaje["sembrar"]("005930.KS", EMISION, INSUMO_POSTERIOR)
    apertura, puntaje = senales.verificar_pendientes()
    assert isinstance(apertura, dict) and isinstance(puntaje, dict)
    assert puntaje["excluidas"] == 1 and puntaje["verificadas"] == 0


# ------------------------------------------------------------
# La conducta de escritura es la de HEAD
# ------------------------------------------------------------
def _sembrar_escenarios(sembrar) -> None:
    """Los seis casos que distingue la guarda, en una sola base."""
    sembrar("NVDA", EMISION, INSUMO_ANTERIOR)                       # normal → se verifica
    sembrar("005930.KS", EMISION, INSUMO_POSTERIOR)                 # invertida → excluida
    sembrar("000660.KS", OTRA_EMISION, OTRO_INSUMO_POSTERIOR,
            fecha=OTRA_FECHA, estado=senales.ESTADO_VERIFICADA)     # invertida de otra fecha
    sembrar("2330.TW", EMISION, None)                               # NULL → se verifica
    sembrar("8035.T", EMISION, EMISION)                             # igualdad → se verifica
    sembrar("MU", EMISION, INSUMO_POSTERIOR, estado=senales.ESTADO_LEGACY)  # legacy → fuera


def _volcado(ruta: str) -> tuple:
    conn = _ro(ruta)
    try:
        escritas = conn.execute(
            "SELECT fecha_senal, ticker, puntaje_ia, retorno_5d_pct "
            "FROM verificacion_puntaje ORDER BY fecha_senal, ticker").fetchall()
        tickers = conn.execute(
            "SELECT fecha, ticker, puntaje_ia, timestamp_utc, available_at, estado "
            "FROM senales_ticker ORDER BY fecha, ticker").fetchall()
    finally:
        conn.close()
    return escritas, tickers


def test_las_filas_escritas_son_exactamente_las_esperadas(base_puntaje):
    """Fijación explícita: con los seis casos sembrados, se escriben tres
    filas (normal, NULL, igualdad) y ninguna otra; los estados no cambian.
    Este test pasa en HEAD y después del cambio: es la conducta que no
    puede moverse."""
    _sembrar_escenarios(base_puntaje["sembrar"])
    antes = _volcado(senales.DB_PATH)
    senales.verificar_puntaje_pendientes()
    escritas, tickers = _volcado(senales.DB_PATH)
    assert escritas == [(FECHA_SENAL, "2330.TW", 0.35, RETORNO_5D_ESPERADO),
                        (FECHA_SENAL, "8035.T", 0.35, RETORNO_5D_ESPERADO),
                        (FECHA_SENAL, "NVDA", 0.35, RETORNO_5D_ESPERADO)]
    assert tickers == antes[1], "senales_ticker cambió"


def test_el_retorno_sobre_los_seis_casos(base_puntaje):
    """La cuenta que acompaña a las filas de arriba (falla sobre HEAD)."""
    _sembrar_escenarios(base_puntaje["sembrar"])
    r = senales.verificar_puntaje_pendientes()
    assert r["verificadas"] == 3 and r["excluidas"] == 2
    assert r["fechas_excluidas"] == sorted([OTRA_FECHA, FECHA_SENAL])


# R2 del dictamen 16-1: la referencia es el commit ANTERIOR al cambio, no
# `HEAD`, para que el test siga siendo discriminante después del commit
# (con `HEAD` compararía la función consigo misma). Es el último commit en
# que `verificar_puntaje_pendientes` devolvía un entero.
COMMIT_DE_REFERENCIA = "864606c"


def _senales_de_head(destino: str):
    """`senales.py` tal como está en `COMMIT_DE_REFERENCIA`, importado bajo
    otro nombre. None si no hay git o el commit no está (p. ej. una copia
    sin repo)."""
    try:
        p = subprocess.run(["git", "-C", RAIZ, "show", f"{COMMIT_DE_REFERENCIA}:senales.py"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0 or not p.stdout:
        return None
    ruta = os.path.join(destino, "senales_head.py")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(p.stdout)
    spec = importlib.util.spec_from_file_location("senales_head", ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules["senales_head"] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def test_la_conducta_de_escritura_es_identica_a_la_de_HEAD(base_puntaje, monkeypatch, tmp_path):
    """La misma siembra, dos bases: la versión actual escribe en una y la
    de HEAD en la otra. `verificacion_puntaje` (sin `verificado_en`, que es
    reloj) y `senales_ticker` quedan byte a byte iguales. Discriminante
    hasta el commit; guardia después."""
    head = _senales_de_head(str(tmp_path))
    if head is None:
        pytest.skip(f"sin git o sin el commit {COMMIT_DE_REFERENCIA}: no hay versión de referencia")
    _sembrar_escenarios(base_puntaje["sembrar"])
    base_actual = senales.DB_PATH
    base_head = str(tmp_path / "senales_head.db")
    shutil.copy(base_actual, base_head)
    assert _volcado(base_actual) == _volcado(base_head)

    monkeypatch.setattr(head, "DB_PATH", base_head)
    monkeypatch.setattr(head, "_ohlc_local", _ohlc_falso())
    assert head.DB_PATH.startswith(str(tmp_path))
    r_actual = senales.verificar_puntaje_pendientes()
    r_head = head.verificar_puntaje_pendientes()

    assert _volcado(base_actual) == _volcado(base_head)
    n_head = r_head if isinstance(r_head, int) else r_head["verificadas"]
    n_actual = r_actual if isinstance(r_actual, int) else r_actual["verificadas"]
    assert n_actual == n_head == 3


def test_el_retorno_no_depende_de_la_red(base_puntaje, monkeypatch):
    """Con la fuente vacía nada se verifica, pero la cuenta de excluidas es
    la misma: la exclusión se decide ANTES de la descarga."""
    monkeypatch.setattr(senales, "_ohlc_local", lambda *a, **k: pd.DataFrame())
    _sembrar_escenarios(base_puntaje["sembrar"])
    r = senales.verificar_puntaje_pendientes()
    assert r == {"verificadas": 0, "excluidas": 2,
                 "fechas_excluidas": sorted([OTRA_FECHA, FECHA_SENAL])}
    assert _volcado(senales.DB_PATH)[0] == []
