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
HORA_LOCAL = datetime.fromisoformat(TS_TARDIO).astimezone().strftime("%H:%M")


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
    assert f"recuperado: sellado {HORA_LOCAL}, descarga 28/28" in entorno[0]
    assert mki_vigia._leer_pendiente(HOY) is None  # consumido
    # Segundo llamado: sin pendiente → silencio (jamás duplica).
    assert mki_vigia.enviar_retractacion_si_corresponde(HOY) is False
    assert len(entorno) == 1


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
    assert len(entorno) == 1 and "recuperado: sellado" in entorno[0]
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
