# ============================================================
# Tests de la Etapa 5.0.1 — vigía con retractación.
#
# La regla nueva: una alerta jamás queda sin epílogo. Si el snapshot no
# está sellado al pasar lista (19:00), queda un marcador; el pase de las
# 20:30 (--rechequeo) o el propio sello tardío de snapshot.py envían el
# cierre — retractación si el día terminó bien, "sigue sin sellar" si no.
# Todo sintético: sin red, sin Telegram, sin tocar senales.db real.
# ============================================================

import os
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import alertas
import mki_vigia
import senales
import snapshot

HOY = date.today()


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    """DB, marcador y log de snapshot temporales; Telegram capturado.
    Devuelve la lista de mensajes 'enviados'."""
    monkeypatch.setattr(senales, "DB_PATH", str(tmp_path / "senales.db"))
    monkeypatch.setattr(mki_vigia, "RUTA_PENDIENTE",
                        str(tmp_path / "vigia_pendiente.json"))
    monkeypatch.setattr(mki_vigia, "RUTA_SNAPSHOT_LOG",
                        str(tmp_path / "snapshot.log"))
    enviados = []

    def fake_enviar(texto):
        enviados.append(texto)
        return True, "enviado"

    monkeypatch.setattr(alertas, "enviar_mensaje", fake_enviar)
    return enviados


def _sellar_hoy(ts_utc: str, ok: int = 28, total: int = 28,
                caidos: str = None) -> None:
    senales.init_db()
    conn = senales.get_connection()
    conn.execute("""INSERT INTO snapshots (fecha, creado_en, timestamp_utc,
                    origen, descarga_ok, descarga_total, descarga_caidos)
                    VALUES (?, ?, ?, 'programado', ?, ?, ?)""",
                 (HOY.isoformat(), ts_utc, ts_utc, ok, total, caidos))
    conn.commit()
    conn.close()


TS_TARDIO = datetime(HOY.year, HOY.month, HOY.day, 1, 23,
                     tzinfo=timezone.utc).isoformat()
HORA_EMISION = alertas._hora_chile(TS_TARDIO)


def _predicciones_selladas(n: int) -> None:
    """Inserta n filas de predicción sellada para HOY (para el conteo de
    la retractación 5.0.2)."""
    conn = senales.get_connection()
    for i in range(n):
        conn.execute("""INSERT INTO senales_ticker
                        (fecha, ticker, apertura_estimada_pct, timestamp_utc)
                        VALUES (?, ?, ?, ?)""",
                     (HOY.isoformat(), f"TK{i}", 1.0 + i, TS_TARDIO))
    conn.commit()
    conn.close()


# ------------------------------------------------------------
# Marcador pendiente
# ------------------------------------------------------------
def test_marcador_ciclo(entorno):
    assert mki_vigia._leer_pendiente(HOY) is None
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], True)
    p = mki_vigia._leer_pendiente(HOY)
    assert p["fecha"] == HOY.isoformat() and p["reintentos_activos"] is True
    mki_vigia._consumir_pendiente()
    assert not os.path.exists(mki_vigia.RUTA_PENDIENTE)


def test_marcador_de_otro_dia_se_ignora(entorno):
    # Una alerta jamás cruza de día: el epílogo que no llegó anoche ya no
    # tiene sentido a la mañana siguiente.
    mki_vigia._escribir_pendiente(HOY - timedelta(days=1), ["x"], False)
    assert mki_vigia._leer_pendiente(HOY) is None


# ------------------------------------------------------------
# Detección de reintentos en curso
# ------------------------------------------------------------
def test_en_curso_lee_el_detalle_del_log(entorno, monkeypatch):
    with open(mki_vigia.RUTA_SNAPSHOT_LOG, "w", encoding="utf-8") as f:
        f.write(f"[{HOY.isoformat()}T22:21:07+00:00] snapshot.py "
                "(origen=programado, modelo=4.6.0, plataforma=5.0.1)\n"
                "  descarga parcial (27/28, caídos: ^SOX) — reintento en 60s\n")
    monkeypatch.setattr(mki_vigia, "_hay_proceso_snapshot", lambda: True)
    activo, detalle = mki_vigia.snapshot_en_curso(HOY)
    assert activo and "27/28" in detalle and "^SOX" in detalle


def test_en_curso_exige_proceso_vivo(entorno, monkeypatch):
    # El log con reintentos NO basta (la corrida pudo morir): la prueba de
    # "en curso" es el proceso; el log solo aporta el detalle.
    with open(mki_vigia.RUTA_SNAPSHOT_LOG, "w", encoding="utf-8") as f:
        f.write(f"[{HOY.isoformat()}T22:21:07+00:00] snapshot.py (origen=programado)\n"
                "  descarga parcial (27/28, caídos: ^SOX) — reintento en 60s\n")
    monkeypatch.setattr(mki_vigia, "_hay_proceso_snapshot", lambda: False)
    activo, _ = mki_vigia.snapshot_en_curso(HOY)
    assert not activo


# ------------------------------------------------------------
# La alerta de las 19:00 anuncia el re-chequeo
# ------------------------------------------------------------
def test_alerta_con_reintentos_activos(entorno):
    resultados = [(False, "snapshot: NO se selló hoy"),
                  (True, "descarga: 28/28 completa")]
    texto = mki_vigia.componer_alerta(HOY, resultados,
                                      (True, "27/28, caídos: ^SOX"))
    assert "aún peleando con la descarga" in texto
    assert "reintentos activos" in texto
    assert "re-chequeo a las 20:30" in texto
    assert "^SOX" in texto


def test_alerta_sin_reintentos_tambien_anuncia_rechequeo(entorno):
    # El epílogo está garantizado en ambos casos (el sello puede llegar
    # tarde por su cuenta aunque no haya proceso vivo a las 19:00).
    resultados = [(False, "snapshot: NO se selló hoy")]
    texto = mki_vigia.componer_alerta(HOY, resultados, (False, ""))
    assert "re-chequeo a las 20:30" in texto
    assert "peleando" not in texto


# ------------------------------------------------------------
# Retractación
# ------------------------------------------------------------
def test_retractacion_tras_sello(entorno):
    _sellar_hoy(TS_TARDIO)
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], True)
    assert mki_vigia.enviar_retractacion_si_corresponde(HOY) is True
    assert len(entorno) == 1
    assert f"emisión {HORA_EMISION}" in entorno[0]
    assert "descarga 28/28" in entorno[0]
    assert mki_vigia._leer_pendiente(HOY) is None  # consumido
    # Segundo llamado: sin pendiente → silencio (jamás duplica).
    assert mki_vigia.enviar_retractacion_si_corresponde(HOY) is False
    assert len(entorno) == 1


def test_retractacion_distingue_emision_de_confirmacion(entorno):
    # 5.0.2 — el caso del 6-ago: timestamp estampado 18:24, fila visible
    # 19:08. El mensaje viejo ("recuperado: sellado 18:24") presentaba la
    # emisión como si fuera el momento en que el sello EXISTE, y chocaba
    # con el reporte de las 18:40 que dijo —verazmente— "sin snapshot".
    # Ahora ambos instantes viajan con su nombre.
    _sellar_hoy(TS_TARDIO)
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], True)
    assert mki_vigia.enviar_retractacion_si_corresponde(HOY) is True
    texto = entorno[0]
    assert f"emisión {HORA_EMISION}" in texto
    assert "confirmada a las " in texto
    assert "recuperado: sellado " not in texto  # la forma que mintió


def test_retractacion_cuenta_predicciones(entorno):
    _sellar_hoy(TS_TARDIO)
    _predicciones_selladas(8)
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], True)
    assert mki_vigia.enviar_retractacion_si_corresponde(HOY) is True
    assert "predicciones 8" in entorno[0]
    assert "sin cobertura" not in entorno[0]


def test_retractacion_advierte_sello_sin_predicciones(entorno):
    # El caso real del 6-ago: "recuperado" con 0 predicciones no es un día
    # normal — la sesión objetivo quedó sin cobertura y el mensaje lo dice.
    _sellar_hoy(TS_TARDIO)
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], True)
    assert mki_vigia.enviar_retractacion_si_corresponde(HOY) is True
    assert "predicciones 0" in entorno[0]
    assert "sin cobertura" in entorno[0]


def test_retractacion_declara_descarga_degradada(entorno):
    _sellar_hoy(TS_TARDIO, ok=25, total=28, caidos="TSM,SMH,IFX.DE")
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], True)
    assert mki_vigia.enviar_retractacion_si_corresponde(HOY) is True
    assert "descarga 25/28" in entorno[0] and "TSM,SMH,IFX.DE" in entorno[0]


def test_sin_sello_no_hay_retractacion(entorno):
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], True)
    assert mki_vigia.enviar_retractacion_si_corresponde(HOY) is False
    assert entorno == []
    assert mki_vigia._leer_pendiente(HOY) is not None  # sigue esperando


def test_sin_pendiente_no_hay_retractacion(entorno):
    _sellar_hoy(TS_TARDIO)
    assert mki_vigia.enviar_retractacion_si_corresponde(HOY) is False
    assert entorno == []


# ------------------------------------------------------------
# El pase de las 20:30
# ------------------------------------------------------------
def test_rechequeo_sin_pendiente_es_silencioso(entorno):
    assert mki_vigia.rechequeo(HOY) == 0
    assert entorno == []


def test_rechequeo_con_sello_retracta(entorno):
    _sellar_hoy(TS_TARDIO)
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], False)
    assert mki_vigia.rechequeo(HOY) == 0
    assert len(entorno) == 1 and "recuperado: snapshot sellado" in entorno[0]
    assert mki_vigia._leer_pendiente(HOY) is None


def test_rechequeo_sigue_sin_sellar(entorno, monkeypatch):
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], True)
    monkeypatch.setattr(mki_vigia, "_hay_proceso_snapshot", lambda: False)
    assert mki_vigia.rechequeo(HOY) == 0
    assert len(entorno) == 1 and "sigue sin sellar" in entorno[0]
    # El marcador QUEDA: si el sello llega más tarde por su cuenta,
    # snapshot.py enviará la retractación (caso real del 29-jul, 21:23).
    assert mki_vigia._leer_pendiente(HOY) is not None


# ------------------------------------------------------------
# El epílogo desde snapshot.py (sello tardío)
# ------------------------------------------------------------
def test_epilogo_retracta_tras_sello_tardio(entorno, capsys):
    _sellar_hoy(TS_TARDIO)
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], True)
    snapshot._epilogo_vigia()
    assert len(entorno) == 1 and "recuperado" in entorno[0]
    assert "retractación del vigía enviada" in capsys.readouterr().out
    assert mki_vigia._leer_pendiente(HOY) is None


def test_epilogo_jamas_rompe_el_sello(entorno, monkeypatch, capsys):
    def bomba():
        raise RuntimeError("explotó el epílogo")

    monkeypatch.setattr(mki_vigia, "enviar_retractacion_si_corresponde", bomba)
    snapshot._epilogo_vigia()  # no debe levantar jamás
    assert "epílogo del vigía falló" in capsys.readouterr().out


# ------------------------------------------------------------
# 5.0.2 — la alerta de noticias nombra el proceso colgado
# ------------------------------------------------------------
def test_noticias_nombra_proceso_colgado(entorno, monkeypatch):
    # El caso del 3–7 ago: un fetch sin timeout dejó mki_noticias.py vivo
    # 4 días; launchd no re-dispara un label con proceso vivo, y la alerta
    # "NO corrió hoy" no decía por qué. Ahora lo nombra.
    import costos
    monkeypatch.setattr(costos, "corridas_del_dia",
                        lambda origen=None, fecha=None: [])
    monkeypatch.setattr(mki_vigia, "_proceso_noticias_colgado",
                        lambda: "proceso 53783 vivo desde Mon Aug  3 17:52:38 2026")
    ok, detalle = mki_vigia.chequear_noticias()
    assert not ok
    assert "proceso 53783 vivo" in detalle
    assert "launchd no re-dispara" in detalle


def test_noticias_sin_proceso_mantiene_mensaje_simple(entorno, monkeypatch, tmp_path):
    import costos
    monkeypatch.setattr(costos, "corridas_del_dia",
                        lambda origen=None, fecha=None: [])
    monkeypatch.setattr(mki_vigia, "_proceso_noticias_colgado", lambda: None)
    # Sin archivo de log de noticias en absoluto: "no corrió" en su forma
    # más simple, sin depender del log real de la máquina.
    monkeypatch.setattr(mki_vigia, "RUTA_NOTICIAS_LOG",
                        str(tmp_path / "noticias.log"))
    ok, detalle = mki_vigia.chequear_noticias()
    assert not ok and detalle == "noticias: el job NO corrió hoy"


# ------------------------------------------------------------
# 5.0.3 — "corrió y NO completó" vs "NO corrió hoy" (acta 70, 1-sep):
# systemd mató mki-noticias.service por TimeoutStartSec después de que
# el job guardara 223 titulares pero antes de escribir una sola línea
# en el ledger de costos. El vigía decía "NO corrió hoy", que es falso.
# ------------------------------------------------------------
def _escribir_log_noticias(ruta: str, lineas: list) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        for linea in lineas:
            f.write(linea + "\n")


def test_noticias_corrio_y_no_completo_por_rastro_en_log(entorno, monkeypatch, tmp_path):
    """El caso real del 1-sep: ledger vacío, pero el log de hoy prueba que
    el job arrancó y completó la fase de descarga antes de que lo mataran."""
    import costos
    ruta_log = str(tmp_path / "noticias.log")
    hoy = date.today().isoformat()
    _escribir_log_noticias(ruta_log, [
        f"[{hoy}T21:50:01.051476+00:00] mki_noticias.py — gasto hoy 0.0000 / tope 0.50 USD",
        f"[{hoy}T22:17:44.187317+00:00] titulares nuevos guardados: 223",
    ])
    monkeypatch.setattr(mki_vigia, "RUTA_NOTICIAS_LOG", ruta_log)
    monkeypatch.setattr(costos, "corridas_del_dia",
                        lambda origen=None, fecha=None: [])
    monkeypatch.setattr(mki_vigia, "_proceso_noticias_colgado", lambda: None)
    monkeypatch.setattr(mki_vigia, "_estado_systemd_noticias", lambda: None)

    ok, detalle = mki_vigia.chequear_noticias()

    assert not ok
    assert "corrió y NO completó" in detalle
    assert "ledger" in detalle
    # Contraprueba: el mensaje viejo NO debe aparecer cuando hay rastro.
    assert "el job NO corrió hoy" not in detalle


def test_noticias_corrio_y_no_completo_refuerzo_systemd_nombra_la_hora(
        entorno, monkeypatch, tmp_path):
    """Cuando hay evidencia de systemd (solo Linux) y dice Result=timeout,
    el mensaje nombra la hora del kill — refuerzo opcional, no primario."""
    import costos
    ruta_log = str(tmp_path / "noticias.log")
    hoy = date.today().isoformat()
    _escribir_log_noticias(ruta_log, [
        f"[{hoy}T22:17:44.187317+00:00] titulares nuevos guardados: 223",
    ])
    monkeypatch.setattr(mki_vigia, "RUTA_NOTICIAS_LOG", ruta_log)
    monkeypatch.setattr(costos, "corridas_del_dia",
                        lambda origen=None, fecha=None: [])
    monkeypatch.setattr(mki_vigia, "_proceso_noticias_colgado", lambda: None)
    monkeypatch.setattr(mki_vigia, "_estado_systemd_noticias", lambda: {
        "Result": "timeout",
        "ExecMainStartTimestamp": "Tue 2026-09-01 17:50:00 -04",
        "ExecMainExitTimestamp": "Tue 2026-09-01 18:20:00 -04",
    })

    ok, detalle = mki_vigia.chequear_noticias()

    assert not ok
    assert "corrió y NO completó" in detalle
    assert "matado por timeout a las 18:20" in detalle


def test_noticias_no_corrio_sin_rastro_alguno_en_log(entorno, monkeypatch, tmp_path):
    """Sin ledger, sin proceso colgado y sin rastro de HOY en el log
    (el log puede tener líneas de otros días): el mensaje sigue siendo
    el "NO corrió hoy" original, sin falsos positivos."""
    import costos
    ruta_log = str(tmp_path / "noticias.log")
    _escribir_log_noticias(ruta_log, [
        "[2026-08-31T22:18:15.078492+00:00] resumen del día regenerado",
    ])
    monkeypatch.setattr(mki_vigia, "RUTA_NOTICIAS_LOG", ruta_log)
    monkeypatch.setattr(costos, "corridas_del_dia",
                        lambda origen=None, fecha=None: [])
    monkeypatch.setattr(mki_vigia, "_proceso_noticias_colgado", lambda: None)

    ok, detalle = mki_vigia.chequear_noticias()

    assert not ok and detalle == "noticias: el job NO corrió hoy"


def test_hora_desde_timestamp_systemd():
    assert mki_vigia._hora_desde_timestamp_systemd(
        "Tue 2026-09-01 18:20:00 -04") == "18:20"
    assert mki_vigia._hora_desde_timestamp_systemd(None) is None
    assert mki_vigia._hora_desde_timestamp_systemd("basura") is None


def test_estado_systemd_noticias_no_se_llama_en_tests_de_arriba(monkeypatch):
    """La función real dispara systemctl — nunca la ejecuta la suite: acá
    solo se prueba que ante un fallo (systemctl ausente) devuelve None sin
    romper, no que systemctl exista en la máquina que corre los tests."""
    import subprocess as sp

    def fake_run(*a, **k):
        raise FileNotFoundError("systemctl no existe (p.ej. macOS)")

    monkeypatch.setattr(sp, "run", fake_run)
    assert mki_vigia._estado_systemd_noticias() is None
