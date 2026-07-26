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


def _hora_chile(ts_iso: str) -> str:
    """Hora local de Chile 'HH:MM' de un timestamp ISO UTC."""
    try:
        from zoneinfo import ZoneInfo
        dt = datetime.fromisoformat(ts_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(ZoneInfo("America/Santiago")).strftime("%H:%M")
    except Exception:
        return (ts_iso or "")[11:16] + " UTC"


def componer_reporte_sellado(fecha: str = None) -> str:
    """El reporte diario 2.0 (Etapa 5.0 WS3): TODO sale de lo SELLADO en
    senales.db y del cache de noticias.db — jamás recompone una señal en
    vivo. Si un campo sellado viene vacío, el reporte LO DICE en vez de
    rellenarlo (el bug del 22-jul, donde el reporte "tapó" el hueco de
    régimen recalculando, no puede repetirse por construcción)."""
    import html

    import noticias
    import senales
    from universo import nombre
    from version import MODELO_VERSION, PLATAFORMA_VERSION

    fecha = fecha or date.today().isoformat()
    snap = senales.snapshot_del_dia(fecha)
    partes = []

    # --- Cabecera con versionado dual
    if snap:
        partes.append(f"<b>MKI</b> · {fecha} · sellado {_hora_chile(snap['timestamp_utc'])} "
                      f"Chile · plataforma {snap.get('plataforma_version') or PLATAFORMA_VERSION} "
                      f"/ modelo {snap.get('modelo_version') or MODELO_VERSION}")
    else:
        partes.append(f"<b>MKI</b> · {fecha} · ⚠ sin snapshot sellado hoy · "
                      f"plataforma {PLATAFORMA_VERSION} / modelo {MODELO_VERSION}")

    # --- Bloque sellado: régimen, SOX, Roca→Chip, salud de descarga
    partes.append("")
    if snap:
        partes.append(f"Régimen: {snap['regimen'] or 'sin dato sellado hoy ⚠'}")
        if snap.get("sox_usado_pct") is not None:
            partes.append(f"SOX: {snap['sox_usado_pct']:+.2f}% "
                          f"(sesión del {snap.get('sox_fecha') or '—'})")
        else:
            partes.append("SOX: sin dato sellado")
        partes.append(f"Roca→Chip: {snap['roca_chip']:.0f}/100"
                      if snap.get("roca_chip") is not None
                      else "Roca→Chip: sin dato sellado hoy ⚠")
        if (snap.get("descarga_ok") is not None
                and snap["descarga_ok"] < (snap.get("descarga_total") or 0)):
            partes.append(f"Descarga: {snap['descarga_ok']}/{snap['descarga_total']} ⚠ "
                          f"caídos: {snap.get('descarga_caidos') or '—'}")
    else:
        partes.append("Régimen / SOX / Roca→Chip: sin sello hoy — nada que reportar ⚠")

    # --- Predicciones selladas (top por |estimado|)
    partes.append("")
    preds = senales.predicciones_selladas_del_dia(fecha)
    if preds:
        partes.append("<b>Aperturas selladas</b> (top por |estimado|):")
        for p in preds[:5]:
            est, int80 = p["apertura_estimada_pct"], p["intervalo80_pp"] or 0.0
            linea = (f"· {nombre(p['ticker'])} {est:+.1f}% "
                     f"[80%: {est - int80:+.1f},{est + int80:+.1f}]")
            if p.get("beta") is not None:
                linea += f" β{p['beta']:.2f}"
            if p.get("r2") is not None:
                linea += f" R²{p['r2']:.2f}"
            if p.get("n_muestra") is not None:
                linea += f" n{p['n_muestra']}"
            linea += f" → {p['sesion_objetivo']}"
            partes.append(linea)
        partes.append(f"{len(preds)} selladas en total · emitidas "
                      f"{_hora_chile(preds[0]['timestamp_utc'])} Chile, antes "
                      f"de la apertura objetivo")
    else:
        partes.append("Aperturas: sin predicciones selladas hoy ⚠")

    # --- Track record vivo: MISMOS números que el dashboard (misma consulta
    #     a la DB — senales.metricas_apertura / calibracion_intervalos)
    partes.append("")
    m = senales.metricas_apertura(dias=30)
    if m.get("suficiente"):
        partes.append(f"<b>Track record</b> (modelo {MODELO_VERSION}, 30d): "
                      f"N={m['n']} · gap {m['gap']['pct_aciertos']:.1f}% · "
                      f"sesión {m['retorno_sesion']['pct_aciertos']:.1f}% · "
                      f"MAE {m['gap']['mae_pp']:.2f}/{m['retorno_sesion']['mae_pp']:.2f} pp")
    else:
        partes.append(f"<b>Track record</b>: {m['n']} verificaciones — "
                      f"datos insuficientes")
    cal = senales.calibracion_intervalos()
    partes.append(f"Cobertura del intervalo 80%: {cal['cobertura_pct']:.1f}% "
                  f"(n={cal['n']})" if cal.get("suficiente")
                  else "Cobertura del intervalo 80%: pendiente")

    # --- Noticias top por relevancia (cache de noticias.db)
    top = noticias.titulares_top_relevancia(3)
    if top:
        partes.append("")
        partes.append("<b>Noticias</b> (top relevancia hoy):")
        partes.extend(f"· ({t['sentimiento']:+.1f}) {html.escape(t['titular'][:110])}"
                      for t in top)

    partes.append("")
    partes.append("<i>Herramienta de análisis — no constituye asesoría financiera.</i>")
    return "\n".join(partes)


def enviar_reporte_sellado() -> tuple:
    """Compone el reporte 2.0 desde lo sellado y lo envía. Es lo que usan
    tanto el job de las 18:25 como el botón del dashboard: UN compositor,
    UN mensaje. Sin anti-duplicados: forzarlo dos veces lo envía dos veces
    (acción explícita, decisión 4.5)."""
    return enviar_mensaje(componer_reporte_sellado())


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
    """Envía el reporte 2.0. La composición es 100% desde lo SELLADO
    (componer_reporte_sellado): el CLI, el job de launchd y el botón del
    dashboard mandan EXACTAMENTE el mismo mensaje. Cero motor en vivo."""
    if not esta_configurado():
        print("NO enviado: Telegram no está configurado "
              "(falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en .env).")
        raise SystemExit(1)
    # texto compuesto UNA vez: cada reintento envía el mensaje idéntico
    texto = componer_reporte_sellado()
    print(f"[{datetime.now(timezone.utc).isoformat()}] reporte compuesto "
          f"desde el sello ({len(texto)} caracteres)")
    ok, detalle = enviar_mensaje(texto)
    # Reintento breve (4.7.3) SOLO si la petición nunca salió — típico al
    # despertar el Mac con la red aún caída. Sin fantasmas: timeouts y
    # errores de Telegram no se reintentan.
    for espera in (60, 120):
        if ok or not detalle.startswith("Error de conexión"):
            break
        print(f"Sin red — reintento en {espera}s…", flush=True)
        time.sleep(espera)
        ok, detalle = enviar_mensaje(texto)
    if ok:
        # La fecha ISO en esta línea es la que el vigía busca (WS2.7).
        print(f"[{datetime.now(timezone.utc).isoformat()}] Reporte enviado "
              f"{datetime.now():%H:%M}")
    else:
        print(f"[{datetime.now(timezone.utc).isoformat()}] NO enviado: {detalle}")
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
