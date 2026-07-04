# ============================================================
# Etapa 4.5 - Alertas por Telegram
#   Envía notificaciones cuando el terminal detecta algo importante:
#   cambio de régimen, divergencia nueva, sentimiento extremo o alto buzz.
#   Sin configurar (sin token/chat en .env) todo funciona en silencio y la
#   UI muestra instrucciones. Registro anti-duplicados en SQLite.
# ============================================================

import os
import sqlite3
from datetime import date, datetime, timezone

import requests

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alertas.db")

UMBRAL_SENTIMIENTO_EXTREMO = 0.6


def esta_configurado() -> bool:
    """True si hay token de bot y chat id en el entorno (cargados desde .env)."""
    return bool(os.environ.get("TELEGRAM_BOT_TOKEN")) and bool(os.environ.get("TELEGRAM_CHAT_ID"))


INSTRUCCIONES = """
**Cómo activar las alertas por Telegram** (5 minutos, gratis):

1. Abre Telegram y busca **@BotFather** (el bot oficial de Telegram para crear bots).
2. Escríbele `/newbot`. Te pedirá un nombre (ej. *MKI Terminal*) y un nombre de
   usuario que termine en `bot` (ej. `mki_terminal_bot`).
3. BotFather te responderá con un **token** con esta pinta:
   `1234567890:AAF-abc123def456...` — cópialo.
4. Ahora necesitas tu **chat id**: busca **@userinfobot** en Telegram, escríbele
   cualquier cosa y te responderá con tu id (un número, ej. `123456789`).
5. Abre una conversación con TU bot recién creado (búscalo por su nombre de
   usuario) y mándale un mensaje cualquiera — sin esto, Telegram no deja que el
   bot te escriba primero.
6. Agrega estas dos líneas a tu archivo **`.env`** (junto a tu clave de Anthropic):
   ```
   TELEGRAM_BOT_TOKEN=1234567890:AAF-abc123def456...
   TELEGRAM_CHAT_ID=123456789
   ```
7. Vuelve a correr `python -m streamlit run app.py`. Listo: este panel cambiará
   solo y las alertas quedarán activas.
"""


# ------------------------------------------------------------
# Registro anti-duplicados
# ------------------------------------------------------------
def _init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alertas_enviadas (
            clave TEXT PRIMARY KEY,
            mensaje TEXT NOT NULL,
            enviado_en TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _ya_enviada(clave: str) -> bool:
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    existe = conn.execute(
        "SELECT 1 FROM alertas_enviadas WHERE clave = ?", (clave,)).fetchone()
    conn.close()
    return existe is not None


def _registrar(clave: str, mensaje: str) -> None:
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR IGNORE INTO alertas_enviadas (clave, mensaje, enviado_en) VALUES (?, ?, ?)",
        (clave, mensaje, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


# ------------------------------------------------------------
# Envío
# ------------------------------------------------------------
def enviar_mensaje(texto: str) -> tuple:
    """Envía un mensaje por Telegram. Devuelve (ok, detalle)."""
    if not esta_configurado():
        return False, "Telegram no está configurado (falta token o chat id en .env)."
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"},
            timeout=10,
        )
        if resp.status_code == 200 and resp.json().get("ok"):
            return True, "enviado"
        return False, f"Telegram respondió {resp.status_code}: {resp.text[:200]}"
    except requests.RequestException as e:
        return False, f"Error de red: {e}"


def _alerta_unica(clave: str, texto: str, enviadas: list) -> None:
    """Envía una alerta solo si su clave no se envió antes (anti-duplicados)."""
    if _ya_enviada(clave):
        return
    ok, _ = enviar_mensaje(texto)
    if ok:
        _registrar(clave, texto)
        enviadas.append(texto)


def alertar_si_corresponde(regimen_actual: str | None, regimen_anterior: str | None,
                           divergencias: list, sentimientos: dict, buzz: dict,
                           nombres: dict) -> list:
    """Evalúa las 4 condiciones de alerta y envía lo que corresponda (una sola vez
    por evento, gracias al registro anti-duplicados). Sin configuración, no hace
    nada. Devuelve la lista de textos enviados."""
    if not esta_configurado():
        return []
    hoy = date.today().isoformat()
    enviadas: list = []

    if (regimen_actual and regimen_anterior
            and regimen_actual != regimen_anterior):
        _alerta_unica(
            f"regimen:{hoy}:{regimen_actual}",
            f"⚠️ <b>Cambio de régimen del SOX</b>\n"
            f"{regimen_anterior} → <b>{regimen_actual}</b>",
            enviadas)

    for div in divergencias:
        _alerta_unica(
            f"divergencia:{hoy}:{div['par']}",
            f"↔️ <b>Divergencia activa: {div['par']}</b>\n{div['explicacion']}",
            enviadas)

    for ticker, valor in sentimientos.items():
        if abs(valor) > UMBRAL_SENTIMIENTO_EXTREMO and ticker in nombres:
            _alerta_unica(
                f"sentimiento:{hoy}:{ticker}",
                f"{'🟢' if valor > 0 else '🔴'} <b>Sentimiento extremo: "
                f"{nombres[ticker]}</b>\nSentimiento IA {valor:+.2f} "
                f"(umbral ±{UMBRAL_SENTIMIENTO_EXTREMO:.1f})",
                enviadas)

    for ticker, info in buzz.items():
        if info.get("buzz") and ticker in nombres:
            _alerta_unica(
                f"buzz:{hoy}:{ticker}",
                f"📣 <b>Alto buzz: {nombres[ticker]}</b>\n"
                f"{info['hoy']} titulares hoy vs {info['promedio_diario']:.1f}/día habituales",
                enviadas)

    return enviadas


def enviar_reporte_matinal(regimen: str | None, roca_chip: float | None,
                           sox_texto: str, sentimiento_sector: float | None,
                           lineas_apertura: list, divergencias: list) -> tuple:
    """Compone y envía el reporte matinal (botón manual en la portada Hoy).
    Devuelve (ok, detalle). Sin anti-duplicados: si el usuario aprieta el botón
    dos veces, recibe el reporte dos veces — es una acción explícita."""
    partes = ["☀️ <b>Reporte matinal — MKI Terminal</b>", ""]
    if regimen:
        partes.append(f"Régimen del SOX: <b>{regimen}</b>")
    if roca_chip is not None:
        partes.append(f"Salud de cadena Roca→Chip: <b>{roca_chip:.0f}/100</b>")
    partes.append(f"Último SOX real: {sox_texto}")
    if sentimiento_sector is not None:
        partes.append(f"Sentimiento del sector (IA): {sentimiento_sector:+.2f}")
    if lineas_apertura:
        partes.append("")
        partes.append("<b>Aperturas estimadas (Asia/Europa):</b>")
        partes.extend(lineas_apertura)
    if divergencias:
        partes.append("")
        partes.append("<b>Divergencias activas:</b>")
        partes.extend(f"• {d['par']}: z={d['z']:+.1f}" for d in divergencias)
    partes.append("")
    partes.append("<i>Herramienta de análisis — no constituye asesoría financiera.</i>")
    return enviar_mensaje("\n".join(partes))
