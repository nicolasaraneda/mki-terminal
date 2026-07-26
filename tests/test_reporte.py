# ============================================================
# Tests del reporte de Telegram 2.0 (Etapa 5.0 WS3).
#
# El contrato: el reporte se construye COMPLETO desde lo sellado en
# senales.db + el cache de noticias.db. Jamás recompone una señal en vivo,
# jamás rellena un hueco del sello, y jamás usa la palabra prohibida.
# ============================================================

import os
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import alertas
import noticias
import senales


HOY = date.today().isoformat()
AYER = (date.today() - timedelta(days=1)).isoformat()
AHORA = datetime.now(timezone.utc).isoformat()


@pytest.fixture
def dbs(monkeypatch, tmp_path):
    """senales.db y noticias.db temporales, pobladas con un día sellado."""
    monkeypatch.setattr(senales, "DB_PATH", str(tmp_path / "senales.db"))
    monkeypatch.setattr(noticias, "DB_PATH", str(tmp_path / "noticias.db"))
    senales.init_db()
    noticias.init_db()

    conn = senales.get_connection()
    conn.execute("""INSERT INTO snapshots
        (fecha, creado_en, timestamp_utc, origen, regimen, roca_chip,
         modelo_version, plataforma_version, ventana_betas,
         descarga_ok, descarga_total, descarga_caidos, sox_usado_pct, sox_fecha)
        VALUES (?, ?, ?, 'programado', 'Alcista · vol alta', 42, '4.6.0',
                '5.0.0', 120, 25, 28, 'MU,2330.TW', -1.25, ?)""",
        (HOY, AHORA, AHORA, AYER))
    predicciones = [  # (ticker, est, r2, int80, n, beta)
        ("005930.KS", -1.9, 0.28, 2.4, 120, 0.37),
        ("000660.KS", 2.6, 0.31, 3.1, 120, 0.55),
        ("2330.TW", -0.8, 0.22, 1.9, 118, 0.30),
        ("6857.T", 0.5, 0.15, 2.2, 120, 0.25),
        ("8035.T", -2.1, 0.26, 2.8, 120, 0.44),
        ("IFX.DE", 0.3, 0.08, 1.5, 115, 0.12),
    ]
    for t, est, r2, i80, n, b in predicciones:
        conn.execute("""INSERT INTO senales_ticker
            (fecha, ticker, puntaje_v0, apertura_estimada_pct, confianza_r2,
             intervalo80_pp, n_muestra, beta, exchange, sesion_objetivo,
             timestamp_utc, estado, modelo_version)
            VALUES (?, ?, 0.5, ?, ?, ?, ?, ?, 'XKRX', '2099-01-04', ?,
                    'pendiente', '4.6.0')""", (HOY, t, est, r2, i80, n, b, AHORA))
        # verificaciones de ayer para el bloque de track record
        conn.execute("""INSERT INTO senales_ticker
            (fecha, ticker, puntaje_v0, apertura_estimada_pct, intervalo80_pp,
             timestamp_utc, estado, modelo_version)
            VALUES (?, ?, 0.5, ?, ?, ?, 'verificada', '4.6.0')""",
            (AYER, t, est, i80, AHORA))
        conn.execute("""INSERT INTO verificacion_apertura
            (fecha_senal, ticker, apertura_estimada_pct, retorno_real_pct,
             acierto_direccion, error_pp, gap_pct, acierto_gap, error_gap_pp,
             verificado_en, modelo_version, legacy)
            VALUES (?, ?, ?, 1.0, 1, 1.0, ?, 1, 0.5, ?, '4.6.0', 0)""",
            (AYER, t, est, est * 0.8, AHORA))
    conn.commit()
    conn.close()

    conn = noticias.get_connection()
    for i, (titular, sent, rel) in enumerate([
            ("TSMC lifts capex guidance after record quarter", 0.6, 0.95),
            ("Samsung <b>flags</b> weaker memory pricing", -0.4, 0.90),
            ("Chip sector edges higher", 0.1, 0.30),
            ("Analyst mentions semis in passing", 0.0, 0.10)]):
        conn.execute("INSERT INTO titulares (fecha, fuente, titular, url) "
                     "VALUES (?, 'test', ?, ?)", (AHORA, titular, f"http://t/{i}"))
        conn.execute("""INSERT INTO analisis
            (titular_id, sentimiento, tickers_afectados, impacto_estimado,
             explicacion, analizado_en, relevancia)
            VALUES (last_insert_rowid(), ?, '', 'medio', 'x', ?, ?)""",
            (sent, AHORA, rel))
    conn.commit()
    conn.close()


def test_reporte_completo(dbs):
    texto = alertas.componer_reporte_sellado()
    # Cabecera: versionado dual y hora del sello
    assert "plataforma 5.0.0 / modelo 4.6.0" in texto
    # Bloque sellado
    assert "Régimen: Alcista · vol alta" in texto
    assert "SOX: -1.25% (sesión del" in texto
    assert "Roca→Chip: 42/100" in texto
    assert "Descarga: 25/28 ⚠ caídos: MU,2330.TW" in texto
    # Predicciones: orden por |estimado| (000660 con 2.6 primero), formato
    # compacto con incertidumbre completa, y el total
    idx_660 = texto.index("+2.6% [80%: -0.5,+5.7] β0.55 R²0.31 n120")
    idx_8035 = texto.index("-2.1% [80%: -4.9,+0.7] β0.44 R²0.26 n120")
    assert idx_660 < idx_8035
    assert "6 selladas en total" in texto
    # IFX (|0.3|, el 6º) queda fuera del top 5
    assert "β0.12" not in texto
    # Track record: MISMOS números que la consulta del dashboard
    m = senales.metricas_apertura(dias=30)
    assert f"N={m['n']}" in texto
    assert f"gap {m['gap']['pct_aciertos']:.1f}%" in texto
    cal = senales.calibracion_intervalos()
    assert f"Cobertura del intervalo 80%: {cal['cobertura_pct']:.1f}%" in texto
    # Noticias: por relevancia (TSMC 0.95 antes que Samsung 0.90), HTML escapado
    assert texto.index("TSMC lifts capex") < texto.index("Samsung &lt;b&gt;flags")
    assert "(+0.6)" in texto and "(-0.4)" in texto
    assert "no constituye asesoría financiera" in texto


def test_palabra_prohibida(dbs):
    # Constitución 5.0 #4: "confianza" está prohibida en todo el sistema.
    assert "confianza" not in alertas.componer_reporte_sellado().lower()


def test_sin_snapshot_lo_dice(dbs, monkeypatch, tmp_path):
    monkeypatch.setattr(senales, "DB_PATH", str(tmp_path / "vacia.db"))
    texto = alertas.componer_reporte_sellado()
    assert "sin snapshot sellado hoy" in texto
    assert "sin predicciones selladas hoy" in texto
    assert "datos insuficientes" in texto
    assert "pendiente" in texto  # cobertura del intervalo


def test_hueco_sellado_se_declara(dbs):
    conn = senales.get_connection()
    conn.execute("UPDATE snapshots SET regimen = NULL, roca_chip = NULL "
                 "WHERE fecha = ?", (HOY,))
    conn.commit()
    conn.close()
    texto = alertas.componer_reporte_sellado()
    # El bug del 22-jul no puede repetirse: el hueco se DICE, no se rellena
    assert "Régimen: sin dato sellado hoy ⚠" in texto
    assert "Roca→Chip: sin dato sellado hoy ⚠" in texto


def test_jamas_llama_al_motor(dbs, monkeypatch):
    """El reporte no recompone NADA en vivo: aunque el motor explote, el
    reporte sale igual (solo lee las bases)."""
    import motor

    def bomba(*a, **k):
        raise RuntimeError("el reporte llamó al motor en vivo")

    for fn in ("regimen_al", "roca_chip_al", "prediccion_apertura_al",
               "divergencias_al", "betas_al", "puntaje_v0_al", "_datos_crudos"):
        monkeypatch.setattr(motor, fn, bomba)
    texto = alertas.componer_reporte_sellado()
    assert "plataforma 5.0.0" in texto
