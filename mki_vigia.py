# ============================================================
# El vigía del sistema (Etapa 5.0 WS2.7; retractación 5.0.1) —
# com.mki.vigia 19:00 hábiles + com.mki.vigia.rechequeo 20:30.
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
#
# 5.0.1 — una alerta jamás queda sin epílogo. Las noches del 29 y 31-jul
# el vigía alertó "NO se selló hoy" mientras snapshot.py seguía vivo
# reintentando; el sello llegó tarde (21:23 y 19:40) y la alerta quedó
# abierta para siempre. Ahora: si el snapshot no está sellado al pasar
# lista, queda el marcador data/vigia_pendiente.json y el pase de las
# 20:30 (--rechequeo) envía el epílogo — retractación si ya selló, o
# "sigue sin sellar". Si el sello llega aún más tarde, snapshot.py mismo
# envía la retractación al encontrar el marcador.
# ============================================================

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timezone

from dotenv import load_dotenv

load_dotenv()

import costos  # noqa: E402
from seguridad import enmascarar_secretos  # noqa: E402

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_REPORTE_LOG = os.path.join(DIRECTORIO, "data", "reporte.log")
RUTA_SNAPSHOT_LOG = os.path.join(DIRECTORIO, "data", "snapshot.log")
RUTA_PENDIENTE = os.path.join(DIRECTORIO, "data", "vigia_pendiente.json")
HORA_RECHEQUEO = "20:30"


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


def _proceso_noticias_colgado() -> str | None:
    """5.0.2 — si hay un mki_noticias.py vivo, launchd NO vuelve a disparar
    el job (un label = un proceso): el 3-ago un fetch sin timeout quedó
    colgado 4 días y "noticias no corrió" del 4 al 7 sin que la alerta
    dijera por qué. Devuelve 'proceso PID vivo desde ...' o None."""
    try:
        r = subprocess.run(["pgrep", "-f", "mki_noticias.py"],
                           capture_output=True, text=True, timeout=10)
        pid = r.stdout.strip().split("\n")[0] if r.stdout.strip() else None
        if not pid:
            return None
        r2 = subprocess.run(["ps", "-p", pid, "-o", "lstart="],
                            capture_output=True, text=True, timeout=10)
        inicio = r2.stdout.strip()
        return f"proceso {pid} vivo" + (f" desde {inicio}" if inicio else "")
    except Exception:
        return None


def chequear_noticias() -> tuple:
    corridas = costos.corridas_del_dia("noticias")
    if not corridas:
        colgado = _proceso_noticias_colgado()
        if colgado:
            return False, (f"noticias: el job NO corrió hoy — {colgado}; "
                           "launchd no re-dispara mientras siga vivo")
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
    # 5.0.3 — en modo sombra el backup NO commitea a propósito. Marcarlo
    # como falla era una falsa alarma diaria que ensuciaba la señal justo
    # en los días que hay que leer con cuidado: el vigía habría gritado
    # todas las noches de la ventana por el comportamiento correcto.
    import modo
    if modo.en_sombra():
        return True, "backup: sin commit por modo sombra (correcto)"
    r = subprocess.run(["git", "-C", DIRECTORIO, "log", "-1", "--format=%cs",
                        "--", "data/backups"], capture_output=True, text=True)
    ultima = r.stdout.strip()
    if ultima == date.today().isoformat():
        return True, "backup: commit de hoy presente"
    return False, f"backup: sin commit hoy (último: {ultima or 'ninguno'})"


# ------------------------------------------------------------
# 5.0.1 — snapshot en curso, marcador pendiente y retractación
# ------------------------------------------------------------
def _hay_proceso_snapshot() -> bool:
    """¿Hay un snapshot.py vivo AHORA? pgrep -f mira la línea de comando
    completa (cubre venv/bin/python snapshot.py y variantes)."""
    try:
        r = subprocess.run(["pgrep", "-f", "snapshot.py"],
                           capture_output=True, text=True, timeout=10)
        return bool(r.stdout.strip())
    except Exception:
        return False


def _ultimo_reintento_en_log(hoy: date) -> str | None:
    """Última línea de reintento del bloque de HOY en data/snapshot.log.
    Los anuncios de reintento se imprimen con flush=True — están en el log
    en tiempo real aunque el resto de la corrida siga bufferizado."""
    if not os.path.exists(RUTA_SNAPSHOT_LOG):
        return None
    with open(RUTA_SNAPSHOT_LOG, encoding="utf-8", errors="replace") as f:
        lineas = f.readlines()[-400:]
    inicio = None
    for i, linea in enumerate(lineas):
        if "snapshot.py (origen=" in linea and hoy.isoformat() in linea:
            inicio = i
    if inicio is None:
        return None
    reintentos = [ln.strip() for ln in lineas[inicio:] if "reintento" in ln]
    return reintentos[-1] if reintentos else None


def snapshot_en_curso(hoy: date = None) -> tuple:
    """(activo, detalle): ¿snapshot.py sigue corriendo? La prueba de "en
    curso" es el PROCESO vivo; el log solo aporta el detalle de qué pelea.
    El estado del sello viene SIEMPRE de senales.db, nunca de aquí."""
    hoy = hoy or date.today()
    if not _hay_proceso_snapshot():
        return False, "sin proceso de snapshot vivo"
    reintento = _ultimo_reintento_en_log(hoy)
    if reintento:
        m = re.search(r"descarga parcial \(([^)]+)\)", reintento)
        if m:
            return True, m.group(1)
        return True, "fallo total de descarga, reintentos largos en curso"
    return True, "proceso vivo, sin reintento anunciado en el log"


def _escribir_pendiente(hoy: date, fallas: list, reintentos_activos: bool) -> None:
    with open(RUTA_PENDIENTE, "w", encoding="utf-8") as f:
        json.dump({"fecha": hoy.isoformat(),
                   "creado_utc": datetime.now(timezone.utc).isoformat(),
                   "fallas": fallas,
                   "reintentos_activos": reintentos_activos},
                  f, ensure_ascii=False, indent=1)


def _leer_pendiente(hoy: date) -> dict | None:
    """El marcador de OTRA fecha se ignora (una alerta jamás cruza de día:
    al amanecer siguiente el epílogo que no llegó ya no tiene sentido)."""
    if not os.path.exists(RUTA_PENDIENTE):
        return None
    try:
        with open(RUTA_PENDIENTE, encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    return datos if datos.get("fecha") == hoy.isoformat() else None


def _consumir_pendiente() -> None:
    try:
        os.remove(RUTA_PENDIENTE)
    except FileNotFoundError:
        pass


def enviar_retractacion_si_corresponde(hoy: date = None) -> bool:
    """Si el vigía dejó una alerta pendiente HOY y el snapshot YA está
    sellado, envía la retractación y consume el marcador. La llaman el
    pase de las 20:30 y snapshot.py tras un sello tardío — solo la
    retractación cierra la alerta.

    5.0.2 — el mensaje distingue EMISIÓN de CONFIRMACIÓN. El 6-ago el
    snapshot se congeló ~44 min entre estampar timestamp_utc (18:24) y
    commitear la fila (~19:08): la retractación dijo "sellado 18:24"
    mientras el reporte de las 18:40 decía —con razón— "sin snapshot
    sellado hoy". timestamp_utc es la emisión sellada; que el sello YA es
    visible lo prueba esta misma lectura, y esa es la hora que cierra la
    contradicción. Además declara cuántas predicciones viajaron en el
    sello: un día "recuperado" con 0 predicciones no es un día normal."""
    hoy = hoy or date.today()
    if _leer_pendiente(hoy) is None:
        return False
    import senales
    info = senales.info_snapshot_hoy()
    if not info:
        return False
    import alertas
    ts = info.get("timestamp_utc") or info.get("creado_en")
    hora_emision = alertas._hora_chile(ts)
    hora_confirmada = alertas._hora_chile(datetime.now(timezone.utc).isoformat())
    ok_n, total = info.get("descarga_ok"), info.get("descarga_total")
    descarga = f"{ok_n}/{total}" if ok_n is not None else "sin dato de salud"
    caidos = info.get("descarga_caidos")
    n_pred = len(senales.predicciones_selladas_del_dia(hoy.isoformat()))
    texto = (f"✅ <b>VIGÍA MKI — retractación {hoy.isoformat()}</b>\n"
             f"recuperado: snapshot sellado (emisión {hora_emision}, "
             f"confirmada a las {hora_confirmada}), descarga {descarga}"
             + (f" (caídos: {caidos})" if caidos else "")
             + f", predicciones {n_pred}"
             + ("" if n_pred else
                " ⚠ — el sello no trae ninguna: la próxima sesión queda sin cobertura"))
    ok, detalle = alertas.enviar_mensaje(texto)
    _log(f"retractación Telegram: {'enviada' if ok else 'NO enviada — ' + detalle}")
    if ok:
        _consumir_pendiente()
    return ok


def rechequeo(hoy: date) -> int:
    """Pase de las 20:30: el epílogo de la alerta de las 19:00. Sin
    marcador de hoy → silencio absoluto (el job launchd corre a diario)."""
    _log("mki_vigia.py --rechequeo — pase de las 20:30")
    if _leer_pendiente(hoy) is None:
        _log("sin alerta pendiente de hoy — nada que re-chequear")
        return 0
    import senales
    if senales.info_snapshot_hoy():
        ok = enviar_retractacion_si_corresponde(hoy)
        return 0 if ok else 1
    # Sigue sin sellar: se dice, y el marcador QUEDA — si el sello llega
    # más tarde por su cuenta, snapshot.py enviará la retractación.
    activo, detalle = snapshot_en_curso(hoy)
    estado = (f"reintentos aún activos ({detalle})" if activo
              else "sin proceso de snapshot vivo")
    texto = (f"🟠 <b>VIGÍA MKI — re-chequeo {hoy.isoformat()}</b>\n"
             f"sigue sin sellar a las {HORA_RECHEQUEO}: {estado}. "
             "Si sella más tarde, llegará la retractación.")
    import alertas
    ok, det = alertas.enviar_mensaje(texto)
    _log(f"epílogo Telegram: {'enviado' if ok else 'NO enviado — ' + det}")
    return 0 if ok else 1


def componer_alerta(hoy: date, resultados: list, en_curso: tuple) -> str:
    """Texto de la alerta de las 19:00. Si el snapshot no selló, la línea
    anuncia el re-chequeo de las 20:30 — y si hay reintentos EN CURSO, lo
    dice en vez de dar el día por perdido (5.0.1)."""
    fallas = []
    for ok, d in resultados:
        if ok:
            continue
        if d.startswith("snapshot:"):
            if en_curso[0]:
                d = ("snapshot: NO sellado — aún peleando con la descarga, "
                     f"reintentos activos ({en_curso[1]}) — "
                     f"re-chequeo a las {HORA_RECHEQUEO}")
            else:
                d = f"{d} — re-chequeo a las {HORA_RECHEQUEO}"
        fallas.append(d)
    bien = [d.split(":")[0] for ok, d in resultados if ok]
    return (f"🛑 <b>VIGÍA MKI — {hoy.isoformat()}</b>\n"
            + "Falló hoy:\n" + "\n".join(f"· {f}" for f in fallas)
            + (f"\nOK: {', '.join(bien)}" if bien else ""))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="El vigía MKI — revisión del día operativo")
    parser.add_argument("--rechequeo", action="store_true",
                        help="pase de las 20:30: epílogo de la alerta pendiente (5.0.1)")
    args = parser.parse_args(argv)
    hoy = date.today()
    if hoy.weekday() >= 5:
        _log("fin de semana — nada que vigilar")
        return 0
    if args.rechequeo:
        return rechequeo(hoy)

    from registro import rotar_log
    rotar_log(os.path.join(DIRECTORIO, "data", "vigia.log"))
    _log("mki_vigia.py — revisión del día operativo")
    resultados = [chequear_snapshot(), chequear_descarga(), chequear_noticias(),
                  chequear_reporte(), chequear_backup()]
    for ok, detalle in resultados:
        _log(f"  {'OK ' if ok else 'FALLA'} {detalle}")
    if all(ok for ok, _ in resultados):
        _log("todo OK — sin alerta")
        return 0

    sin_sellar = not resultados[0][0]
    en_curso = snapshot_en_curso(hoy) if sin_sellar else (False, "")
    if sin_sellar:
        _escribir_pendiente(hoy, [d for ok, d in resultados if not ok], en_curso[0])
        _log(f"marcador escrito — el pase de las {HORA_RECHEQUEO} enviará el epílogo")

    import alertas
    texto = componer_alerta(hoy, resultados, en_curso)
    ok, detalle = alertas.enviar_mensaje(texto)
    _log(f"alerta Telegram: {'enviada' if ok else 'NO enviada — ' + detalle}")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        _log(f"ERROR no manejado: {enmascarar_secretos(str(e))}")
        sys.exit(1)
