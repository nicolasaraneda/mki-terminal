# ============================================================
# Modo de operación de la máquina (Etapa 5.0.3 — modo sombra (Fase 3 de la reactivación))
#
# Durante la migración del Mac al PC hay DOS máquinas corriendo el mismo
# código sobre la misma historia. Solo una puede ser TITULAR: la que manda
# el reporte de Telegram y commitea los respaldos. La otra corre en
# SOMBRA: sella igual en su senales.db —ese sello es el objeto mismo de la
# comparación— pero no emite nada hacia afuera.
#
#   MKI_MODO=sombra   → máquina sombra
#   MKI_MODO ausente  → titular (el Mac hoy; el PC después del switch)
#
# QUÉ INTERCEPTA LA SOMBRA
#   · Telegram: reporte, alertas del vigía y retractaciones se escriben a
#     data/sombra_telegram.log y NO salen a la red (alertas.enviar_mensaje
#     es el único punto de salida del sistema — se intercepta ahí).
#   · Backup: mki_backup.py no commitea (solo lo registra en su log).
#
# QUÉ NO CAMBIA
#   · snapshot.py sella normalmente. Si la sombra no sellara no habría nada
#     que comparar, y comparar es el propósito entero de la ventana.
#
# FALLA SEGURA ANTE TYPO
#   Un `MKI_MODO=sombrra` que cayera silenciosamente a titular convertiría
#   al PC en un segundo titular esa misma noche: Telegram duplicado y
#   commits en paralelo. Por eso un valor RECONOCIDO manda, y un valor
#   puesto pero ilegible cae a SOMBRA con aviso ruidoso, nunca a titular.
#   Ausente sigue siendo titular (el Mac no define la variable y no debe
#   tener que definirla). Mismo criterio que el tope de gasto de costos.py,
#   que ante .env ilegible cae al valor conservador.
# ============================================================

import os
from datetime import datetime, timezone

from dotenv import load_dotenv

# snapshot.py y mki_backup.py no cargan .env por su cuenta (sí lo hacen el
# vigía, noticias y el dashboard). Cargarlo aquí hace que el modo se lea
# igual desde cualquier entrypoint. load_dotenv NO pisa lo que ya está en
# el entorno, así que `MKI_MODO=sombra python ...` sigue mandando.
load_dotenv()

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_SOMBRA_TELEGRAM = os.path.join(DIRECTORIO, "data", "sombra_telegram.log")

MODO_TITULAR = "titular"
MODO_SOMBRA = "sombra"

_RECONOCIDOS = {MODO_TITULAR, MODO_SOMBRA}


def modo_actual() -> str:
    """Devuelve 'titular' o 'sombra'. Ver la nota de falla segura arriba."""
    crudo = os.environ.get("MKI_MODO", "").strip().lower()
    if not crudo:
        return MODO_TITULAR
    if crudo in _RECONOCIDOS:
        return crudo
    return MODO_SOMBRA


def valor_crudo_invalido() -> str | None:
    """El valor de MKI_MODO si está puesto y NO es reconocible, si no None.
    Los entrypoints lo usan para avisar en su log en vez de fallar callados."""
    crudo = os.environ.get("MKI_MODO", "").strip()
    if crudo and crudo.lower() not in _RECONOCIDOS:
        return crudo
    return None


def en_sombra() -> bool:
    return modo_actual() == MODO_SOMBRA


def descripcion() -> str:
    """Una línea legible para logs y para `./mki estado`."""
    invalido = valor_crudo_invalido()
    if invalido:
        return (f"modo: SOMBRA (MKI_MODO={invalido!r} no se reconoce; "
                "se cae a sombra por seguridad — nada sale a la red)")
    if en_sombra():
        return "modo: SOMBRA — Telegram interceptado, backup sin commit"
    return "modo: TITULAR — Telegram y commits activos"


def registrar_telegram_interceptado(texto: str) -> None:
    """Escribe a data/sombra_telegram.log el mensaje que NO se envió.

    El texto pasa por enmascarar_secretos como todo lo que llega a un log
    (regla de seguridad.py). Nunca levanta: que el registro falle no puede
    convertirse en un envío real ni tumbar el job que lo llamó.
    """
    try:
        from seguridad import enmascarar_secretos
        os.makedirs(os.path.dirname(RUTA_SOMBRA_TELEGRAM), exist_ok=True)
        ahora = datetime.now(timezone.utc).isoformat()
        with open(RUTA_SOMBRA_TELEGRAM, "a", encoding="utf-8") as f:
            f.write(f"\n=== {ahora} · INTERCEPTADO (modo sombra, no salió a la red) ===\n")
            f.write(enmascarar_secretos(texto or "") + "\n")
    except Exception:
        pass
