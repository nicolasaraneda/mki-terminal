# ============================================================
# Tests del enmascaramiento de secretos (Etapa 5.0 — WS1).
# Todos los secretos de este archivo son FALSOS, inventados para el test.
# ============================================================

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seguridad import enmascarar_secretos, ultimos4  # noqa: E402

TOKEN_FALSO = "1112223334:AAFakeFakeFakeFakeFake-123"
CLAVE_FALSA = "sk-ant-api03-FaKeFaKeFaKeFaKeFaKeFaKeFaKe-XYZ9"
CHAT_FALSO = "5556667778"


def test_ultimos4():
    assert ultimos4(TOKEN_FALSO) == "…-123"
    assert ultimos4("") == "(vacío)"


def test_enmascara_valores_del_entorno(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN_FALSO)
    monkeypatch.setenv("TELEGRAM_CHAT_ID", CHAT_FALSO)
    monkeypatch.setenv("ANTHROPIC_API_KEY", CLAVE_FALSA)
    texto = (f"POST https://api.telegram.org/bot{TOKEN_FALSO}/sendMessage "
             f"chat_id={CHAT_FALSO} clave={CLAVE_FALSA}")
    salida = enmascarar_secretos(texto)
    assert TOKEN_FALSO not in salida
    assert CHAT_FALSO not in salida
    assert CLAVE_FALSA not in salida
    # Los últimos 4 sí quedan, para poder identificar QUÉ secreto era.
    assert "…-123" in salida and "…7778" in salida and "…XYZ9" in salida


def test_enmascara_patrones_sin_entorno(monkeypatch):
    # Defensa en profundidad: aunque el secreto NO esté en el entorno,
    # cualquier cosa con pinta de token/clave se enmascara igual.
    for var in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    texto = (f"error con url /bot{TOKEN_FALSO}/x y clave {CLAVE_FALSA} adentro")
    salida = enmascarar_secretos(texto)
    assert TOKEN_FALSO not in salida
    assert CLAVE_FALSA not in salida


def test_texto_limpio_pasa_intacto():
    texto = "Reporte enviado 18:25 · régimen alcista · SOX +1.25%"
    assert enmascarar_secretos(texto) == texto
    assert enmascarar_secretos("") == ""


def test_error_dns_real_queda_limpio(monkeypatch):
    # Reproduce la forma exacta de la línea que fugó el token a
    # data/reporte.log el 11-jul (con token falso).
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN_FALSO)
    linea = (
        "NO enviado: Error de red: HTTPSConnectionPool(host='api.telegram.org',"
        f" port=443): Max retries exceeded with url: /bot{TOKEN_FALSO}/sendMessage"
        " (Caused by NameResolutionError('Failed to resolve api.telegram.org'))")
    salida = enmascarar_secretos(linea)
    assert TOKEN_FALSO not in salida
    assert "api.telegram.org" in salida  # el diagnóstico útil se conserva
