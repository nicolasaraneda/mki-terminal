# ============================================================
# tests/test_noticias_ledger.py — «0 analizados con error» no es «ok»
# (acta §93.3 ii; tarjeta §74; corrida 16-1, 10-oct-2026).
#
# El hecho (MEDIDO en la corrida 15): del 7-sep al 2-oct-2026 la API de
# Anthropic rechazó cada llamada por falta de crédito («Your credit balance
# is too low…»), `mki_noticias.py` cortó el bucle en la excepción y
# registró `resultado: ok` con `analizados: 0`; el vigía repitió «noticias:
# ok · 0 analizados · 0.0000 USD» durante 22 días. Un fallo de crédito era
# invisible por Telegram.
#
# La regla firmada: cuando el análisis falla, el ledger `data/costos_ia.log`
# registra un `resultado` distinto de `ok` y de `freno_presupuesto`, con el
# TIPO del error y el lote, y SIN el texto de la respuesta de la API (puede
# traer identificadores). `freno_presupuesto` sigue siendo OK; «sin
# pendientes» sigue siendo OK. El vigía (`chequear_noticias`) trata el
# error como falla.
#
# Todo sintético: `mki_noticias.main()` entero con noticias.py, la API,
# Telegram, el ledger y el log reemplazados. Sin red, sin .env leído por el
# test (la clave es un literal falso), sin tocar noticias.db real.
# ============================================================

import json
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import alertas  # noqa: E402
import costos  # noqa: E402
import mki_noticias  # noqa: E402
import mki_vigia  # noqa: E402
import noticias  # noqa: E402
import registro  # noqa: E402

TEXTO_API = ("Error code: 400 - {'type': 'error', 'error': {'type': "
             "'invalid_request_error', 'message': 'Your credit balance is too low "
             "to access the Anthropic API.'}, 'request_id': 'req_011CSINTETICO'}")


class BadRequestError(Exception):
    """Mismo nombre que la clase del SDK; el test no importa `anthropic`."""
    status_code = 400


class _Usage:
    input_tokens = 1000
    output_tokens = 500


class _ConnFalsa:
    def commit(self):
        pass

    def close(self):
        pass


@pytest.fixture
def corrida(monkeypatch, tmp_path):
    """Prepara `mki_noticias.main()` con TODO reemplazado. Devuelve un
    helper que fija el comportamiento de `_analizar_lote` por lote, corre
    `main()` y devuelve (código de salida, última línea del ledger)."""
    ledger = str(tmp_path / "costos_ia.log")
    monkeypatch.setattr(costos, "RUTA_LOG", ledger)
    monkeypatch.setenv("NOTICIAS_PRESUPUESTO_USD_DIA", "0.50")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-clave-falsa-de-test")
    monkeypatch.setattr(registro, "rotar_log", lambda *a, **k: None)
    monkeypatch.setattr(noticias, "migrar_noticias_v2", lambda: {})
    monkeypatch.setattr(noticias, "actualizar_titulares", lambda: 5)
    monkeypatch.setattr(noticias, "get_connection", lambda: _ConnFalsa())
    monkeypatch.setattr(noticias, "guardar_analisis", lambda conn, r: None)
    monkeypatch.setattr(noticias, "generar_resumen_dia", lambda client: "")
    enviados = []
    monkeypatch.setattr(alertas, "enviar_mensaje",
                        lambda texto: (enviados.append(texto), (True, "enviado"))[1])
    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", lambda api_key=None: object())

    def correr(pendientes: int, falla_en_lote: int = None):
        lote_tam = mki_noticias.TAM_LOTE
        monkeypatch.setattr(
            noticias, "obtener_titulares_sin_analizar",
            lambda conn: [{"id": i, "titular": f"t{i}", "tickers": ""}
                          for i in range(pendientes)])
        llamadas = []

        def analizar(client, lote):
            llamadas.append(len(lote))
            if falla_en_lote is not None and len(llamadas) == falla_en_lote:
                raise BadRequestError(TEXTO_API)
            return ([{"titular_id": item["id"]} for item in lote], _Usage())
        monkeypatch.setattr(noticias, "_analizar_lote", analizar)
        codigo = mki_noticias.main()
        with open(ledger, encoding="utf-8") as f:
            lineas = [json.loads(l) for l in f if l.strip()]
            f.seek(0)
            crudo = f.read()
        assert lineas, "el ledger quedó vacío"
        return codigo, lineas[-1], crudo, llamadas, enviados, lote_tam

    return correr


# ------------------------------------------------------------
# Reproducción del 7-sep y controles
# ------------------------------------------------------------
def test_reproduccion_7_sep_excepcion_en_el_lote_1_no_es_ok(corrida):
    """REPRODUCCIÓN (falla sobre HEAD, que registra `ok`). 25 pendientes,
    la API rechaza el primer lote: 0 analizados y un `resultado` que no es
    `ok` ni `freno_presupuesto`, con el tipo del error y el lote."""
    codigo, registro_, crudo, llamadas, _, _ = corrida(pendientes=25, falla_en_lote=1)
    assert codigo == 0                      # el job termina; lo que cambia es el registro
    assert llamadas == [20]
    assert registro_["analizados"] == 0
    assert registro_["resultado"] not in ("ok", "freno_presupuesto"), registro_
    assert registro_["resultado"] == mki_noticias.RESULTADO_ERROR_ANALISIS
    assert registro_["error_tipo"] == "BadRequestError"
    assert registro_["error_lote"] == 1
    assert registro_["error_http"] == 400
    assert registro_["pendientes_restantes"] == 25


def test_el_ledger_no_lleva_el_texto_de_la_respuesta_de_la_api(corrida):
    """El texto completo puede traer identificadores (request_id) y va sólo
    al log del job, enmascarado; al ledger viaja el TIPO, nada más."""
    _, _, crudo, _, _, _ = corrida(pendientes=25, falla_en_lote=1)
    assert "req_011CSINTETICO" not in crudo
    assert "credit balance" not in crudo and "Error code" not in crudo
    assert "BadRequestError" in crudo


def test_control_sin_error_sigue_siendo_ok(corrida):
    _, registro_, crudo, llamadas, _, _ = corrida(pendientes=25)
    assert llamadas == [20, 5]
    assert registro_["resultado"] == "ok" and registro_["analizados"] == 25
    assert "error_tipo" not in registro_ and "error_tipo" not in crudo


def test_control_sin_pendientes_sigue_siendo_ok(corrida):
    _, registro_, _, llamadas, _, _ = corrida(pendientes=0)
    assert llamadas == []
    assert registro_["resultado"] == "ok"
    assert registro_["analizados"] == 0 and registro_["pendientes_restantes"] == 0


def test_control_freno_de_presupuesto_sigue_siendo_freno(corrida, monkeypatch):
    """Con el tope ya gastado antes de arrancar, el freno manda, como hoy."""
    monkeypatch.setattr(costos, "estado_presupuesto",
                        lambda: {"fecha": "x", "gasto_usd": 0.5, "tope_usd": 0.5,
                                 "restante_usd": 0.0, "agotado": True})
    _, registro_, _, llamadas, enviados, _ = corrida(pendientes=25)
    assert llamadas == []
    assert registro_["resultado"] == "freno_presupuesto"
    assert any("freno de presupuesto" in t for t in enviados)


def test_error_en_el_segundo_lote_conserva_lo_analizado_y_nombra_el_lote(corrida):
    _, registro_, _, llamadas, _, _ = corrida(pendientes=45, falla_en_lote=2)
    assert llamadas == [20, 20]
    assert registro_["resultado"] == mki_noticias.RESULTADO_ERROR_ANALISIS
    assert registro_["analizados"] == 20 and registro_["error_lote"] == 2
    assert registro_["pendientes_restantes"] == 25


def test_un_error_sin_status_code_registra_el_tipo_y_nada_mas(corrida, monkeypatch):
    class RedCaida(Exception):
        pass

    def analizar(client, lote):
        raise RedCaida("timeout hacia api.anthropic.com")
    pendientes = [{"id": 1, "titular": "t", "tickers": ""}]
    monkeypatch.setattr(noticias, "obtener_titulares_sin_analizar", lambda conn: pendientes)
    monkeypatch.setattr(noticias, "_analizar_lote", analizar)
    # `corrida` ya preparó el resto; se corre main() directo.
    assert mki_noticias.main() == 0
    with open(costos.RUTA_LOG, encoding="utf-8") as f:
        ultima = json.loads([l for l in f if l.strip()][-1])
    assert ultima["resultado"] == mki_noticias.RESULTADO_ERROR_ANALISIS
    assert ultima["error_tipo"] == "RedCaida" and ultima["error_http"] is None
    assert "timeout" not in json.dumps(ultima)


# ------------------------------------------------------------
# El vigía lo trata como falla
# ------------------------------------------------------------
def _vigia_con_ledger(monkeypatch, registro_: dict) -> tuple:
    monkeypatch.setattr(costos, "corridas_del_dia", lambda origen=None, fecha=None: [registro_])
    return mki_vigia.chequear_noticias()


def test_el_vigia_falla_con_error_de_analisis(corrida, monkeypatch):
    _, registro_, _, _, _, _ = corrida(pendientes=25, falla_en_lote=1)
    ok, detalle = _vigia_con_ledger(monkeypatch, registro_)
    assert not ok
    assert "análisis FALLÓ" in detalle or "analisis FALLO" in detalle
    assert "BadRequestError" in detalle and "lote 1" in detalle
    assert "0 analizados" in detalle and "25" in detalle


def test_el_vigia_sigue_ok_con_freno_y_sin_pendientes(monkeypatch):
    ok, detalle = _vigia_con_ledger(monkeypatch, {
        "resultado": "freno_presupuesto", "analizados": 1020, "costo_usd": 0.509})
    assert ok and "freno_presupuesto" in detalle
    ok, detalle = _vigia_con_ledger(monkeypatch, {
        "resultado": "ok", "analizados": 0, "costo_usd": 0.0, "pendientes_restantes": 0})
    assert ok and "0 analizados" in detalle


def test_el_vigia_con_el_ledger_del_7_sep_ya_no_dice_ok(monkeypatch):
    """La forma vieja del registro (resultado ok, 0 analizados, pendientes
    260) sigue leyéndose OK: el ledger histórico no se reescribe y el vigía
    no puede inferir el error de un registro que no lo trae. Lo que cambia
    es que un registro NUEVO con error ya no tiene esa forma."""
    ok, _ = _vigia_con_ledger(monkeypatch, {
        "resultado": "ok", "analizados": 0, "costo_usd": 0.0, "pendientes_restantes": 260})
    assert ok
    ok, detalle = _vigia_con_ledger(monkeypatch, {
        "resultado": mki_noticias.RESULTADO_ERROR_ANALISIS, "analizados": 0,
        "costo_usd": 0.0, "pendientes_restantes": 260,
        "error_tipo": "BadRequestError", "error_lote": 1, "error_http": 400})
    assert not ok and "BadRequestError" in detalle
