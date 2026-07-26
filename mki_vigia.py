# ============================================================
# El vigía del sistema (Etapa 5.0 WS2.7) — com.mki.vigia, 19:00 hábiles.
#
# Verifica que el día operativo ocurrió COMPLETO:
#   1. ¿snapshot sellado hoy?          (senales.db)
#   2. ¿salud de descarga 100%?        (columnas selladas WS2.2)
#   3. ¿corrió el job de noticias?     (registro de costos WS2.4)
#   4. ¿salió el reporte de Telegram?  (data/reporte.log)
#   5. ¿se commiteó el backup?         (git log de data/backups)
#
# Si algo falló → UN mensaje de Telegram de ALERTA (distinto del reporte
# diario) diciendo exactamente qué. El sistema deja de fallar en silencio.
# El vigía solo LEE — jamás corrige nada por su cuenta.
# ============================================================

import os
import subprocess
import sys
from datetime import date, datetime, timezone

from dotenv import load_dotenv

load_dotenv()

import costos  # noqa: E402
from seguridad import enmascarar_secretos  # noqa: E402

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_REPORTE_LOG = os.path.join(DIRECTORIO, "data", "reporte.log")


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def chequear_snapshot() -> tuple:
    import senales
    info = senales.info_snapshot_hoy()
    if not info:
        return False, "snapshot: NO se selló hoy"
    return True, f"snapshot: sellado (origen {info['origen']})"


def chequear_descarga() -> tuple:
    import senales
    senales.init_db()
    conn = senales.get_connection()
    fila = conn.execute(
        "SELECT descarga_ok, descarga_total, descarga_caidos FROM snapshots "
        "WHERE fecha = ?", (date.today().isoformat(),)).fetchone()
    conn.close()
    if fila is None:
        return False, "descarga: sin snapshot que revisar"
    ok_n, total, caidos = fila
    if ok_n is None:
        return True, "descarga: snapshot sin dato de salud (pre-5.0)"
    if ok_n == total:
        return True, f"descarga: {ok_n}/{total} completa"
    return False, f"descarga: {ok_n}/{total} DEGRADADA (caídos: {caidos})"


def chequear_noticias() -> tuple:
    corridas = costos.corridas_del_dia("noticias")
    if not corridas:
        return False, "noticias: el job NO corrió hoy"
    ultima = corridas[-1]
    resultado = ultima.get("resultado", "?")
    if resultado == "rss_fallo":
        return False, "noticias: corrió pero el RSS falló"
    detalle = (f"noticias: {resultado} · {ultima.get('analizados', 0)} analizados "
               f"· {ultima.get('costo_usd', 0):.4f} USD")
    return True, detalle


def chequear_reporte() -> tuple:
    hoy = date.today().isoformat()
    if not os.path.exists(RUTA_REPORTE_LOG):
        return False, "reporte: no existe data/reporte.log"
    with open(RUTA_REPORTE_LOG, encoding="utf-8", errors="replace") as f:
        colas = f.readlines()[-120:]
    # El CLI del reporte imprime "[YYYY-MM-DD...] Reporte enviado" (5.0).
    if any("Reporte enviado" in linea and hoy in linea for linea in colas):
        return True, "reporte: enviado hoy"
    # Compatibilidad con el formato pre-5.0 ("Reporte enviado HH:MM" sin
    # fecha): se acepta si el log se escribió hoy.
    mtime_hoy = date.fromtimestamp(os.path.getmtime(RUTA_REPORTE_LOG)).isoformat() == hoy
    if mtime_hoy and any("Reporte enviado" in linea for linea in colas[-15:]):
        return True, "reporte: enviado hoy (formato pre-5.0)"
    return False, "reporte: NO hay envío registrado hoy"


def chequear_backup() -> tuple:
    r = subprocess.run(["git", "-C", DIRECTORIO, "log", "-1", "--format=%cs",
                        "--", "data/backups"], capture_output=True, text=True)
    ultima = r.stdout.strip()
    if ultima == date.today().isoformat():
        return True, "backup: commit de hoy presente"
    return False, f"backup: sin commit hoy (último: {ultima or 'ninguno'})"


def main() -> int:
    from registro import rotar_log
    rotar_log(os.path.join(DIRECTORIO, "data", "vigia.log"))
    hoy = date.today()
    if hoy.weekday() >= 5:
        _log("fin de semana — nada que vigilar")
        return 0
    _log("mki_vigia.py — revisión del día operativo")
    resultados = [chequear_snapshot(), chequear_descarga(), chequear_noticias(),
                  chequear_reporte(), chequear_backup()]
    for ok, detalle in resultados:
        _log(f"  {'OK ' if ok else 'FALLA'} {detalle}")
    fallas = [d for ok, d in resultados if not ok]
    bien = [d.split(":")[0] for ok, d in resultados if ok]
    if not fallas:
        _log("todo OK — sin alerta")
        return 0

    import alertas
    texto = (f"🛑 <b>VIGÍA MKI — {hoy.isoformat()}</b>\n"
             + "Falló hoy:\n" + "\n".join(f"· {f}" for f in fallas)
             + (f"\nOK: {', '.join(bien)}" if bien else ""))
    ok, detalle = alertas.enviar_mensaje(texto)
    _log(f"alerta Telegram: {'enviada' if ok else 'NO enviada — ' + detalle}")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        _log(f"ERROR no manejado: {enmascarar_secretos(str(e))}")
        sys.exit(1)
