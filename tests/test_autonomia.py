# ============================================================
# Tests de la Etapa 5.0 WS2 — autonomía de datos.
#
# Cubren las DOS excepciones quirúrgicas de la constitución:
#   #1 salud de descarga SELLADA por snapshot (con test de no-contaminación:
#      observar la descarga no cambia ninguna señal, y sellar la salud no
#      cambia ninguna fila de predicción), y
#   #2 reintento parcial pre-sello cuando el lote baja incompleto.
# Más el estado terminal 'sin_datos_mercado' del verificador (WS2.6).
#
# Todo sintético: sin red, sin tocar senales.db real (DBs temporales).
# ============================================================

import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import pytest

import motor
import noticias
import senales
import snapshot


# ------------------------------------------------------------
# Datos sintéticos deterministas (400 días hábiles hasta hoy)
# ------------------------------------------------------------
def _frame_sintetico(tickers: tuple, sin_datos: set = frozenset()) -> pd.DataFrame:
    idx = pd.bdate_range(end=pd.Timestamp(date.today()), periods=400)
    datos = {}
    for t in tickers:
        semilla = abs(hash(t)) % (2**32)
        rng = np.random.default_rng(semilla)
        serie = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.02, len(idx))))
        datos[t] = np.full(len(idx), np.nan) if t in sin_datos else serie
    return pd.DataFrame(datos, index=idx)


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    """DB temporal de señales, sentimientos vacíos y caché del motor limpia.
    Devuelve un helper para parchear _datos_crudos con caídos configurables."""
    monkeypatch.setattr(senales, "DB_PATH", str(tmp_path / "senales_test.db"))
    monkeypatch.setattr(noticias, "sentimiento_promedio_por_ticker", lambda: {})
    motor._cache.clear()

    def instalar_fake(caidos_por_llamada):
        """`caidos_por_llamada`: lista de sets — el lote del UNIVERSO de la
        llamada k usa el set k (la última se repite). ^SOX y demás lotes
        siempre completos."""
        contador = {"n": 0}

        def fake(tickers):
            sin_datos = frozenset()
            if set(tickers) == set(snapshot.UNIVERSO.keys()):
                k = min(contador["n"], len(caidos_por_llamada) - 1)
                sin_datos = frozenset(caidos_por_llamada[k])
                contador["n"] += 1
            return _frame_sintetico(tuple(tickers), sin_datos)

        monkeypatch.setattr(motor, "_datos_crudos", fake)
        return contador

    yield instalar_fake
    motor._cache.clear()


# ------------------------------------------------------------
# WS2.2 — salud de descarga
# ------------------------------------------------------------
def test_salud_detecta_caidos(entorno):
    entorno([{"MU", "2330.TW"}])
    salud = snapshot.salud_descarga(date.today())
    assert set(salud["caidos"]) == {"MU", "2330.TW"}
    assert salud["ok_n"] + len(salud["caidos"]) == salud["total"]
    assert not salud["completa"]


def test_salud_completa(entorno):
    entorno([set()])
    salud = snapshot.salud_descarga(date.today())
    assert salud["completa"] and salud["caidos"] == []
    assert salud["total"] == len(snapshot.UNIVERSO) + 1  # universo + ^SOX


def test_no_contaminacion_observar_salud(entorno):
    """Excepción #1: observar la descarga NO cambia ninguna señal del motor."""
    entorno([set()])
    hoy = date.today()
    antes = motor.puntaje_v0_al(hoy)
    regimen_antes = motor.regimen_al(hoy)
    snapshot.salud_descarga(hoy)  # observa
    despues = motor.puntaje_v0_al(hoy)
    regimen_despues = motor.regimen_al(hoy)
    assert antes.equals(despues)
    assert regimen_antes == regimen_despues


def test_no_contaminacion_sellado(entorno, tmp_path):
    """Excepción #1: sellar la salud no cambia NINGUNA fila de predicción —
    las filas de senales_ticker son idénticas con y sin salud_descarga."""
    entorno([set()])
    hoy = date.today()
    metricas = motor.puntaje_v0_al(hoy)
    args = dict(fecha=hoy.isoformat(), timestamp_utc="2026-01-01T00:00:00+00:00",
                origen="test", metricas_df=metricas, sentimientos={},
                predicciones=[{"Ticker": "005930.KS", "Apertura estimada %": -1.0,
                               "R2": 0.3, "Intervalo80 pp": 2.0, "N muestra": 120,
                               "exchange": "XKRX", "sesion_objetivo": "2099-01-04"}],
                regimen="Alcista · vol alta", roca_chip=50.0, divergencias=[],
                ventana_betas=120, available_at="2026-01-01T00:00:00+00:00")
    filas = {}
    for nombre_db, salud in (("con", {"ok_n": 25, "total": 28, "caidos": ["MU"]}),
                             ("sin", None)):
        senales.DB_PATH = str(tmp_path / f"senales_{nombre_db}.db")
        assert senales.guardar_snapshot(**args, salud_descarga=salud)
        conn = senales.get_connection()
        filas[nombre_db] = conn.execute(
            """SELECT fecha, ticker, puntaje_v0, apertura_estimada_pct,
                      confianza_r2, timestamp_utc, exchange, sesion_objetivo,
                      available_at, estado, intervalo80_pp, n_muestra,
                      modelo_version
               FROM senales_ticker ORDER BY ticker""").fetchall()
        salud_sellada = conn.execute(
            "SELECT descarga_ok, descarga_total, descarga_caidos FROM snapshots"
        ).fetchone()
        conn.close()
        if nombre_db == "con":
            assert salud_sellada == (25, 28, "MU")
        else:
            assert salud_sellada == (None, None, None)
    assert filas["con"] == filas["sin"]


# ------------------------------------------------------------
# WS2.3 — reintento parcial pre-sello
# ------------------------------------------------------------
def test_reintento_parcial_recupera(entorno, monkeypatch):
    """1ª descarga incompleta, 2ª completa: un solo sleep y sello sano."""
    entorno([{"MU"}, set()])
    esperas = []
    monkeypatch.setattr(snapshot.time, "sleep", lambda s: esperas.append(s))
    resultado = snapshot.ejecutar_snapshot("programado", reintentos_parciales=2)
    assert resultado["snapshot"] is True
    assert esperas == [60]
    assert resultado["caidos"] == []
    conn = senales.get_connection()
    fila = conn.execute("SELECT descarga_ok, descarga_total, descarga_caidos, "
                        "plataforma_version FROM snapshots").fetchone()
    conn.close()
    assert fila[0] == fila[1] and fila[2] is None
    from version import PLATAFORMA_VERSION
    assert fila[3] == PLATAFORMA_VERSION


def test_reintento_agotado_sella_degradado(entorno, monkeypatch):
    """Caído permanente: 2 esperas y se sella IGUAL con salud degradada
    visible — el sistema prefiere un sello honesto a no sellar."""
    entorno([{"MU"}])
    esperas = []
    monkeypatch.setattr(snapshot.time, "sleep", lambda s: esperas.append(s))
    resultado = snapshot.ejecutar_snapshot("programado", reintentos_parciales=2)
    assert resultado["snapshot"] is True
    assert esperas == [60, 120]
    assert resultado["caidos"] == ["MU"]
    conn = senales.get_connection()
    fila = conn.execute("SELECT descarga_ok, descarga_total, descarga_caidos "
                        "FROM snapshots").fetchone()
    conn.close()
    assert fila == (fila[1] - 1, fila[1], "MU")


def test_dashboard_jamas_espera(entorno, monkeypatch):
    """El fallback del dashboard (default reintentos_parciales=0) no duerme
    ni un segundo aunque la descarga venga incompleta."""
    entorno([{"MU"}])
    monkeypatch.setattr(snapshot.time, "sleep",
                        lambda s: pytest.fail("el dashboard no debe esperar"))
    resultado = snapshot.ejecutar_snapshot("dashboard")
    assert resultado["snapshot"] is True
    assert resultado["caidos"] == ["MU"]


# ------------------------------------------------------------
# WS2.6 — verificaciones atascadas → estado terminal
# ------------------------------------------------------------
def test_verificador_marca_atascadas(entorno, monkeypatch):
    # Fechas calculadas contra el calendario XKRX REAL, relativas a hoy: la
    # versión original (fechas fijas 16/23-jul) se pudrió cuando el
    # calendario avanzó y ambas filas pasaron a terminales (03-ago-2026).
    import calendarios
    entorno([set()])
    monkeypatch.setattr(senales, "_ohlc_local", lambda *a, **k: pd.DataFrame())

    d = date.today()
    while not (calendarios.es_sesion("XKRX", d.isoformat())
               and calendarios.sesion_ya_cerro("XKRX", d.isoformat())):
        d -= timedelta(days=1)
    fresca = d.isoformat()          # última sesión cerrada: < 5 posteriores
    vieja = fresca                  # 8 sesiones antes: ≥ 5 posteriores cerradas
    for _ in range(8):
        vieja = calendarios.sesion_anterior("XKRX", vieja)

    senales.init_db()
    conn = senales.get_connection()
    for ticker, sesion in (("005930.KS", vieja), ("000660.KS", fresca)):
        # Emitida la víspera a las 22:15 UTC — siempre ANTES de la apertura
        # XKRX (00:00 UTC), como manda la regla maestra.
        emision = (date.fromisoformat(sesion) - timedelta(days=1)).isoformat()
        conn.execute("""INSERT INTO senales_ticker
            (fecha, ticker, puntaje_v0, apertura_estimada_pct, timestamp_utc,
             exchange, sesion_objetivo, estado, modelo_version)
            VALUES (?, ?, 0.5, -1.0, ?, 'XKRX', ?, 'pendiente', '4.6.0')""",
            (emision, ticker, f"{emision}T22:15:05+00:00", sesion))
    conn.commit()
    conn.close()

    resultado = senales.verificar_apertura_pendientes()
    assert resultado["sin_datos_mercado"] == 1
    conn = senales.get_connection()
    estados = dict(conn.execute(
        "SELECT ticker, estado FROM senales_ticker").fetchall())
    conn.close()
    # Sesión vieja sin datos publicados tras ≥5 sesiones cerradas → TERMINAL.
    # Sesión recién cerrada → sigue pendiente (5 sesiones de paciencia).
    assert estados["005930.KS"] == senales.ESTADO_SIN_DATOS
    assert estados["000660.KS"] == senales.ESTADO_PENDIENTE


# ------------------------------------------------------------
# 5.0.2 — el job de noticias jamás se cuelga para siempre
# ------------------------------------------------------------
def test_timeout_global_de_red_en_noticias():
    """El 3-ago un socket hacia Yahoo que nunca murió dejó mki_noticias.py
    vivo 4 días, y launchd no re-dispara un label mientras su proceso siga
    vivo: noticias "no corrió" del 4 al 7. feedparser usa urllib SIN
    timeout — el default global del módulo socket (fijado al importar el
    entrypoint) es la única palanca que lo cubre sin tocar noticias.py."""
    import socket

    import mki_noticias

    assert mki_noticias.TIMEOUT_RED_SEG > 0
    assert socket.getdefaulttimeout() == mki_noticias.TIMEOUT_RED_SEG
