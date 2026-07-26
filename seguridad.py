# ============================================================
# Etapa 5.0 - Enmascaramiento de secretos en logs y salida
#   Regla: un secreto jamás se imprime completo. Cualquier texto que
#   pueda terminar en un log, en pantalla o en un mensaje (detalles de
#   error incluidos) pasa por enmascarar_secretos() antes de salir;
#   de un secreto solo se muestran sus últimos 4 caracteres.
#
#   Contexto: el 11-jul un error de DNS de requests imprimió la URL
#   completa de Telegram (que lleva el token del bot) a data/reporte.log.
#   Este módulo existe para que esa clase de fuga sea imposible.
# ============================================================

import os
import re

# Variables de entorno cuyo VALOR es un secreto.
VARIABLES_SENSIBLES = ("ANTHROPIC_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")

# Patrones de secretos reconocibles aunque NO estén en el entorno
# (defensa en profundidad): claves de Anthropic y tokens de bot de Telegram.
_PATRONES = (
    re.compile(r"sk-ant-[A-Za-z0-9_-]{16,}"),
    # Sin \b inicial: en una URL "/bot<token>" no hay frontera de palabra
    # entre "bot" y los dígitos — y ese es exactamente el contexto real.
    re.compile(r"\d{8,12}:AA[A-Za-z0-9_-]{16,}"),
)


def ultimos4(valor: str) -> str:
    """Representación segura de un secreto: solo sus últimos 4 caracteres."""
    if not valor:
        return "(vacío)"
    return f"…{valor[-4:]}"


def enmascarar_secretos(texto: str) -> str:
    """Devuelve `texto` con todo secreto conocido reemplazado por su versión
    enmascarada: primero los valores reales de las variables sensibles del
    entorno, después cualquier cosa con pinta de clave o token."""
    if not texto:
        return texto
    for nombre in VARIABLES_SENSIBLES:
        valor = os.environ.get(nombre, "")
        if valor and len(valor) >= 8 and valor in texto:
            texto = texto.replace(valor, ultimos4(valor))
    for patron in _PATRONES:
        texto = patron.sub(lambda m: ultimos4(m.group(0)), texto)
    return texto
