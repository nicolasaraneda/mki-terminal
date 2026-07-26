# ============================================================
# Etapa 4.5 - Alertas por Telegram
#   Envía notificaciones cuando el terminal detecta algo importante:
#   cambio de régimen, divergencia nueva, sentimiento extremo o alto buzz.
#   Sin configurar (sin token/chat en .env) todo funciona en silencio y la
#   UI muestra instrucciones. Registro anti-duplicados en SQLite.
#
#   Como script tiene salida visible (antes terminaba en silencio):
#     python alertas.py            → estado: qué hay configurado y por qué
#                                    no se envió nada
#     python alertas.py reporte    → fuerza el reporte matinal AHORA
#     python alertas.py --help     → ayuda
# ============================================================

import os
import sqlite3
import time
from datetime import date, datetime, timezone

import requests

from seguridad import enmascarar_secretos, ultimos4

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
        return False, enmascarar_secretos(
            f"Telegram respondió {resp.status_code}: {resp.text[:200]}")
    except requests.exceptions.ConnectionError as e:
        # La petición NUNCA llegó al servidor (DNS caído, sin red): reenviar
        # no puede duplicar. Es el único caso que el CLI reintenta (4.7.3).
        # El texto de la excepción lleva la URL con el token — se enmascara
        # SIEMPRE (Etapa 5.0: así se fugó el token a reporte.log el 11-jul).
        return False, enmascarar_secretos(f"Error de conexión (el mensaje no salió): {e}")
    except requests.RequestException as e:
        # Timeout u otros: el mensaje PUDO haber llegado — jamás se reintenta
        # (un reporte duplicado fantasma es peor que uno perdido).
        return False, enmascarar_secretos(f"Error de red: {e}")


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


def etiqueta_senal(r2: float) -> str:
    """Etiqueta de señal para textos de Telegram, derivada SOLO de umbrales
    de R² histórico (Etapa 4.7.1 — mismos cortes que la API, ver DECISIONES):
    débil (R² < 0.10) · moderada (0.10–0.25) · fuerte (> 0.25)."""
    return "fuerte" if r2 > 0.25 else ("moderada" if r2 > 0.10 else "débil")


def enviar_reporte_matinal(regimen: str | None, roca_chip: float | None,
                           sox_texto: str, sentimiento_sector: float | None,
                           lineas_apertura: list, divergencias: list,
                           roca_fecha: str | None = None) -> tuple:
    """Compone y envía el reporte matinal (botón manual en la portada Hoy).
    Devuelve (ok, detalle). Sin anti-duplicados: si el usuario aprieta el botón
    dos veces, recibe el reporte dos veces — es una acción explícita.
    `roca_chip` es el valor SELLADO del último snapshot (Etapa 4.7.2 — nada
    de valores en vivo en el reporte); `roca_fecha` es la fecha del sello."""
    partes = ["☀️ <b>Reporte matinal — MKI Terminal</b>", ""]
    if regimen:
        partes.append(f"Régimen del SOX: <b>{regimen}</b>")
    if roca_chip is not None:
        sello = f" (sellado {roca_fecha})" if roca_fecha else ""
        partes.append(f"Salud de cadena Roca→Chip: <b>{roca_chip:.0f}/100</b>{sello}")
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


# ------------------------------------------------------------
# CLI — solo visibilidad; la lógica de qué se envía y cuándo no cambia.
# Como biblioteca (import alertas desde app.py) nada de esto se ejecuta.
# ------------------------------------------------------------
def _cli_estado() -> None:
    """Muestra el estado y explica por qué esta invocación no envió nada."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if esta_configurado():
        # Solo los últimos 4 caracteres de cada secreto (Etapa 5.0).
        print(f"Telegram configurado: token {ultimos4(token)} · "
              f"chat id {ultimos4(chat)} (leídos desde .env)")
    else:
        faltan = [n for n, v in (("TELEGRAM_BOT_TOKEN", token),
                                 ("TELEGRAM_CHAT_ID", chat)) if not v]
        print(f"Telegram NO configurado: falta {' y '.join(faltan)} en .env")
        print("Instrucciones: panel Telegram de la portada Hoy (Streamlit).")
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    hoy = date.today().isoformat()
    n_hoy = conn.execute("SELECT COUNT(*) FROM alertas_enviadas WHERE clave LIKE ?",
                         (f"%:{hoy}:%",)).fetchone()[0]
    conn.close()
    print(f"Alertas automáticas ya registradas hoy: {n_hoy}")
    print()
    print("No se envió nada: sin subcomando, este script solo muestra el estado.")
    print("  · Reporte matinal:      python alertas.py reporte")
    print("    (equivale al botón 'Enviar reporte matinal' de la portada Hoy)")
    print("  · Alertas automáticas (régimen, divergencias, sentimiento, buzz):")
    print("    las evalúa el dashboard al abrirse, con registro anti-duplicados.")


def _cli_reporte() -> None:
    """Fuerza el reporte matinal: composición idéntica a la del botón de
    app.py (mismas fuentes, mismos formatos), con salida visible. El
    Roca→Chip es el SELLADO del último snapshot en senales.db (4.7.2)."""
    if not esta_configurado():
        print("NO enviado: Telegram no está configurado "
              "(falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en .env).")
        raise SystemExit(1)
    # imports pesados solo aquí: como biblioteca, alertas.py sigue liviano
    import motor
    import noticias
    import senales
    from api.utilidades import dias_a_proximos_earnings
    from universo import ACCIONES, nombre

    hoy = date.today()
    print("Componiendo el reporte (motor + noticias + snapshot sellado)…")
    regimen = motor.regimen_al(hoy)
    roca_sellada = senales.historial_roca_chip(dias=365)
    pred = motor.prediccion_apertura_al(
        hoy, dias_earnings=dias_a_proximos_earnings(ACCIONES))
    if pred is not None and not pred.empty:
        sox_texto = (f"{pred.iloc[0]['SOX usado %']:+.2f}% "
                     f"(sesión del {pred.iloc[0]['SOX fecha']})")
        lineas = [f"• {nombre(p['Ticker'])}: {p['Apertura estimada %']:+.2f}% "
                  f"(señal {etiqueta_senal(float(p['R2']))})"
                  for _, p in pred.iterrows()]
    else:
        sox_texto, lineas = "sin datos", []
    # argumentos compuestos UNA vez: cada reintento envía el mismo mensaje
    argumentos = dict(
        regimen=regimen["etiqueta"] if regimen else None,
        roca_chip=(float(roca_sellada.iloc[-1]["Roca→Chip"])
                   if not roca_sellada.empty else None),
        roca_fecha=(str(roca_sellada.iloc[-1]["Fecha"])
                    if not roca_sellada.empty else None),
        sox_texto=sox_texto,
        sentimiento_sector=noticias.sentimiento_promedio_sector(),
        lineas_apertura=lineas,
        divergencias=[d for d in motor.divergencias_al(hoy) if d["activa"]],
    )
    ok, detalle = enviar_reporte_matinal(**argumentos)
    # Reintento breve (4.7.3) SOLO si la petición nunca salió — típico al
    # despertar el Mac con la red aún caída. Sin fantasmas: timeouts y
    # errores de Telegram no se reintentan.
    for espera in (60, 120):
        if ok or not detalle.startswith("Error de conexión"):
            break
        print(f"Sin red — reintento en {espera}s…", flush=True)
        time.sleep(espera)
        ok, detalle = enviar_reporte_matinal(**argumentos)
    if ok:
        print(f"Reporte enviado {datetime.now():%H:%M}")
    else:
        print(f"NO enviado: {detalle}")
        raise SystemExit(1)


if __name__ == "__main__":
    import argparse

    # Como script nadie cargó .env todavía (app.py lo hace por su cuenta);
    # sin esto, el token y el chat id jamás llegan a os.environ.
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="alertas.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Alertas por Telegram del MKI Terminal.\n\n"
            "Sin subcomando muestra el ESTADO (configuración leída de .env, "
            "alertas ya\nregistradas hoy) y no envía nada. Las alertas "
            "automáticas (cambio de régimen,\ndivergencias, sentimiento "
            "extremo, buzz) las evalúa el dashboard al abrirse —\neste "
            "script no las dispara."),
        epilog=("ejemplos:\n"
                "  python alertas.py            estado, sin enviar nada\n"
                "  python alertas.py reporte    envía el reporte matinal ahora\n"))
    parser.add_argument(
        "comando", nargs="?", choices=["estado", "reporte"], default="estado",
        help="estado (default): diagnóstico sin enviar · reporte: fuerza el "
             "reporte matinal (igual al botón de la portada Hoy)")
    args = parser.parse_args()
    _cli_reporte() if args.comando == "reporte" else _cli_estado()
