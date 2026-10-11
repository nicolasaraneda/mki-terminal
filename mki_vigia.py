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
import sqlite3
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

import costos  # noqa: E402
from seguridad import enmascarar_secretos  # noqa: E402

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_REPORTE_LOG = os.path.join(DIRECTORIO, "data", "reporte.log")
RUTA_SNAPSHOT_LOG = os.path.join(DIRECTORIO, "data", "snapshot.log")
RUTA_NOTICIAS_LOG = os.path.join(DIRECTORIO, "data", "noticias.log")
RUTA_PENDIENTE = os.path.join(DIRECTORIO, "data", "vigia_pendiente.json")
HORA_RECHEQUEO = "20:30"

# Corrida 16-1 (acta §93.8 d): la línea fija con la que snapshot.py declara
# que se negó a sellar POR REGLA. Es un contrato con snapshot.py
# (`MARCA_NEGATIVA` allí); un test exige que los dos textos coincidan y que
# la salida real del sellador se lea desde aquí. Una negativa declarada NO
# es una falla: se informa con su propio mensaje y su propio epílogo.
MARCA_NEGATIVA = "NEGATIVA DECLARADA"
PREFIJO_NEGATIVA = "snapshot: NO sellado por negativa declarada"
_RE_NEGATIVA = re.compile(
    re.escape(MARCA_NEGATIVA) + r" \[(?P<codigo>[\w-]+)\] fecha=(?P<fecha>\S+) "
    r"sox_fecha=(?P<sox_fecha>\S+): (?P<texto>.*)$")

# Corrida 16-1 (acta §95.2 R3): una fila invertida (available_at >
# timestamp_utc) con fecha dentro de esta ventana es un evento NUEVO —las
# guardas de §90.1 (b) y §93.8 (b) debían impedirlo— y alerta; fuera de la
# ventana es el residuo conocido (hoy, las 24 del 28-sep-2026) y sólo se
# informa con su cuenta. La ventana cubre los 7 días que tarda una fila en
# ser candidata del verificador más tres para leerla.
DIAS_INVERSION_RECIENTE = 10


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def _instante(texto: str) -> datetime | None:
    """Instante con zona, o None si el texto no es una marca ISO legible
    (BL2 del dictamen 16-1: un valor ilegible se declara como FALLA, nunca
    puede tirar el pase y dejar mudo al vigía)."""
    try:
        t = datetime.fromisoformat(texto)
    except (ValueError, TypeError):
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def _negativa_declarada_en_log(hoy: date) -> dict | None:
    """La negativa declarada por la ÚLTIMA corrida de snapshot.py que
    aparece en data/snapshot.log, si es de HOY (la línea lleva la fecha
    del snapshot que no se selló). Si la última corrida no declaró ninguna
    —o el log no existe— devuelve None y «no sellado» sigue siendo falla.
    Mira la última cabecera porque manda la última corrida: una negativa
    de las 18:15 seguida de una corrida manual que falló sin declararla es
    una falla, no una negativa."""
    if not os.path.exists(RUTA_SNAPSHOT_LOG):
        return None
    with open(RUTA_SNAPSHOT_LOG, encoding="utf-8", errors="replace") as f:
        lineas = f.readlines()[-400:]
    inicio = None
    for i, linea in enumerate(lineas):
        if "snapshot.py (origen=" in linea:
            inicio = i
    if inicio is None:
        return None
    encontrada = None
    for linea in lineas[inicio:]:
        m = _RE_NEGATIVA.search(linea.strip())
        if m and m.group("fecha") == hoy.isoformat():
            encontrada = m.groupdict()
    return encontrada


def chequear_snapshot(hoy: date = None) -> tuple:
    import senales
    hoy = hoy or date.today()
    info = senales.info_snapshot_hoy()
    if not info:
        negativa = _negativa_declarada_en_log(hoy)
        if negativa:
            return True, (f"{PREFIJO_NEGATIVA} [{negativa['codigo']}]: "
                          f"{negativa['texto']}")
        return False, "snapshot: NO se selló hoy"
    return True, f"snapshot: sellado (origen {info['origen']})"


def es_negativa(detalle: str) -> bool:
    return detalle.startswith(PREFIJO_NEGATIVA)


def chequear_descarga(hoy: date = None) -> tuple:
    import senales
    hoy = hoy or date.today()
    senales.init_db()
    conn = senales.get_connection()
    fila = conn.execute(
        "SELECT descarga_ok, descarga_total, descarga_caidos FROM snapshots "
        "WHERE fecha = ?", (hoy.isoformat(),)).fetchone()
    conn.close()
    if fila is None:
        if _negativa_declarada_en_log(hoy):
            return True, "descarga: sin snapshot que revisar (negativa declarada)"
        return False, "descarga: sin snapshot que revisar"
    ok_n, total, caidos = fila
    if ok_n is None:
        return True, "descarga: snapshot sin dato de salud (pre-5.0)"
    if ok_n == total:
        return True, f"descarga: {ok_n}/{total} completa"
    return False, f"descarga: {ok_n}/{total} DEGRADADA (caídos: {caidos})"


def chequear_ancla_temporal(hoy: date = None) -> tuple:
    """Guardia del acta §82.2 (c), corrida 11: ninguna predicción sellada
    hoy puede tener `available_at` igual a su `timestamp_utc`. Si lo tiene,
    la rama del `except` de snapshot.py (available_at) se tomó —sox_fecha
    vacío o `cierre_utc` falló—, el ancla temporal es reloj de pared, y con
    el parche del §26 aplicado la sesión objetivo se eligió como en el
    defecto. Se lee de la base, no del log: la evidencia es la igualdad.

    Corrida 16-1 (acta §93.9, tarjeta §67): la igualdad NO es orden. El
    28-sep-2026 las 24 filas tenían `available_at` 2 h 17 min POSTERIOR a
    `timestamp_utc` y este chequeo dijo «OK». Ahora prueba las dos cosas:
    `av == ts` (rama del except, como siempre) Y `av > ts` (inversión: el
    insumo se declara conocible después de la emisión), cada una con su
    texto. Los instantes se comparan con zona, no como texto."""
    import senales
    senales.init_db()
    hoy = hoy or date.today()
    conn = senales.get_connection()
    filas = conn.execute(
        "SELECT ticker, timestamp_utc, available_at FROM senales_ticker "
        "WHERE fecha = ? AND apertura_estimada_pct IS NOT NULL",
        (hoy.isoformat(),)).fetchall()
    conn.close()
    if not filas:
        return True, "ancla temporal: sin predicciones selladas hoy que revisar"
    de_pared = [t for t, ts, av in filas if not av or av == ts]
    ilegibles, invertidas = [], []
    for t, ts, av in filas:
        if not av or av == ts:
            continue
        conocible, emitida = _instante(av), _instante(ts)
        if conocible is None or emitida is None:
            ilegibles.append(t)
        elif conocible > emitida:
            invertidas.append(t)
    problemas = []
    if ilegibles:
        problemas.append(f"{len(ilegibles)}/{len(filas)} filas con available_at o "
                         f"timestamp_utc ILEGIBLES ({', '.join(ilegibles)}) — no se pudo "
                         f"evaluar el orden")
    if de_pared:
        problemas.append(f"{len(de_pared)}/{len(filas)} filas con "
                         f"available_at = reloj de pared ({', '.join(de_pared)}) — "
                         f"la rama del except de snapshot.py se tomó; ver snapshot.log")
    if invertidas:
        problemas.append(f"{len(invertidas)}/{len(filas)} filas con "
                         f"available_at POSTERIOR a timestamp_utc ({', '.join(invertidas)}) — "
                         f"inversión: el insumo se declara conocible después de la "
                         f"emisión; las guardas de §90.1 (b) y §93.8 (b) no la frenaron")
    if problemas:
        return False, "ancla temporal: " + " · ".join(problemas)
    return True, f"ancla temporal: {len(filas)}/{len(filas)} filas con cierre del SOX"


def _inversiones_puntaje(ruta_db: str) -> tuple:
    """El predicado de la guarda de `verificar_puntaje_pendientes`, recomputado
    en `mode=ro` sobre `ruta_db`: filas con `puntaje_ia`, no legacy, cuyo
    `available_at` es un instante POSTERIOR a `timestamp_utc`. Igual que el
    verificador: NULL o cadena vacía es «sin dato» (no cuenta), la igualdad
    no cuenta, los instantes se comparan con zona. Sin el filtro de 7 días.
    Devuelve tres dicts fecha → n: fuera de `verificacion_puntaje`, dentro,
    e ilegibles (marcas no parseables, que el verificador no distingue y
    acá se declaran). Lanza `sqlite3.Error` si la base no se puede leer."""
    import senales
    conn = sqlite3.connect(f"file:{ruta_db}?mode=ro", uri=True)
    try:
        filas = conn.execute(f"""
            SELECT s.fecha, s.ticker, s.timestamp_utc, s.available_at,
                   v.id IS NOT NULL AS dentro
            FROM senales_ticker s
            LEFT JOIN verificacion_puntaje v
              ON v.fecha_senal = s.fecha AND v.ticker = s.ticker
            WHERE s.puntaje_ia IS NOT NULL
              AND s.timestamp_utc IS NOT NULL AND s.available_at IS NOT NULL
              AND (s.estado IS NULL OR s.estado != '{senales.ESTADO_LEGACY}')
            ORDER BY s.fecha, s.ticker""").fetchall()
    finally:
        conn.close()
    fuera, dentro, ilegibles = {}, {}, {}
    for fecha, ticker, ts, av, esta_dentro in filas:
        if not av or av == ts:
            continue
        conocible, emitida = _instante(av), _instante(ts)
        if conocible is None or emitida is None:
            ilegibles[fecha] = ilegibles.get(fecha, 0) + 1
            continue
        if conocible <= emitida:
            continue
        destino = dentro if esta_dentro else fuera
        destino[fecha] = destino.get(fecha, 0) + 1
    return fuera, dentro, ilegibles


def chequear_guarda_puntaje(hoy: date = None) -> tuple:
    """Corrida 16-1 (acta §95.2 R3; dictamen 16a §7): recomputa en `mode=ro`
    el predicado de la guarda de `verificar_puntaje_pendientes` —filas con
    `puntaje_ia` que declaran su insumo conocible DESPUÉS de su emisión
    (available_at > timestamp_utc)— y dice cuántas siguen fuera de
    `verificacion_puntaje` y cuántas están dentro. No depende del log que
    rota ni de ninguna columna nueva. Sin alerta cuando el residuo es el
    conocido (fechas viejas, todas fuera); con alerta si una invertida está
    DENTRO (la guarda fue vencida) o si aparece una fecha NUEVA (dentro de
    `DIAS_INVERSION_RECIENTE` días: un sello que las guardas debían
    impedir). Sin el filtro de 7 días del verificador, a propósito: una
    inversión fresca no debe esperar una semana para verse."""
    import senales
    hoy = hoy or date.today()
    try:
        fuera, dentro, ilegibles = _inversiones_puntaje(senales.DB_PATH)
    except sqlite3.Error as e:
        return False, (f"guarda puntaje: no se pudo leer la base en solo lectura "
                       f"({enmascarar_secretos(str(e))})")
    n_fuera, n_dentro = sum(fuera.values()), sum(dentro.values())
    if ilegibles:
        detalle = ", ".join(f"{f}: {n}" for f, n in sorted(ilegibles.items()))
        return False, (f"guarda puntaje: {sum(ilegibles.values())} fila(s) con available_at o "
                       f"timestamp_utc ILEGIBLES ({detalle}) — el predicado no se pudo "
                       f"evaluar en ellas; {n_fuera} invertida(s) fuera, {n_dentro} dentro")
    if not fuera and not dentro:
        return True, "guarda puntaje: 0 filas con available_at > timestamp_utc, fuera o dentro de verificacion_puntaje"
    limite = (hoy - timedelta(days=DIAS_INVERSION_RECIENTE)).isoformat()
    nuevas = sorted(f for f in set(fuera) | set(dentro) if f > limite)
    detalle_fuera = ", ".join(f"{f}: {n}" for f, n in sorted(fuera.items()))
    resumen = (f"{n_fuera} fila(s) invertida(s) fuera de verificacion_puntaje"
               + (f" ({detalle_fuera})" if fuera else "") + f"; {n_dentro} dentro")
    if dentro:
        detalle_dentro = ", ".join(f"{f}: {n}" for f, n in sorted(dentro.items()))
        return False, (f"guarda puntaje: {n_dentro} fila(s) con available_at > timestamp_utc "
                       f"DENTRO de verificacion_puntaje ({detalle_dentro}) — la guarda de "
                       f"§93.4-bis (i) fue vencida; {resumen}")
    if nuevas:
        return False, (f"guarda puntaje: fecha NUEVA con inversión ({', '.join(nuevas)}), "
                       f"sellada hace menos de {DIAS_INVERSION_RECIENTE} días — las guardas de "
                       f"§90.1 (b) y §93.8 (b) debían impedirlo; ver snapshot.log; {resumen}")
    return True, f"guarda puntaje: {resumen} (residuo conocido, sin fecha nueva)"


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


def _rastro_noticias_hoy_en_log(hoy: str = None) -> bool:
    """5.0.3 — evidencia PRIMARIA de solo lectura (no red, no systemd,
    funciona igual en Linux y macOS): ¿hay en data/noticias.log una línea
    de HOY que pruebe que el job arrancó y completó al menos la fase de
    descarga ("titulares nuevos guardados")? Distingue "no corrió" de
    "corrió y no completó" incluso cuando systemd mató el proceso antes
    de que llegara a escribir una sola línea en el ledger de costos — el
    caso del 1-sep (acta 70): 223 titulares guardados a las 18:17:44,
    ninguna corrida en data/costos_ia.log ese día."""
    if not os.path.exists(RUTA_NOTICIAS_LOG):
        return False
    hoy = hoy or date.today().isoformat()
    with open(RUTA_NOTICIAS_LOG, encoding="utf-8", errors="replace") as f:
        lineas = f.readlines()[-400:]
    return any("titulares nuevos guardados" in linea and hoy in linea
               for linea in lineas)


def _estado_systemd_noticias() -> dict | None:
    """Refuerzo OPCIONAL, solo Linux/systemd. macOS (launchd) no tiene
    equivalente — por eso la evidencia primaria es SIEMPRE el log, nunca
    esto. Nunca se ejecuta en los tests (inyectable via monkeypatch);
    ante cualquier falla o ausencia de systemctl, devuelve None y el
    mensaje se arma solo con el log."""
    try:
        r = subprocess.run(
            ["systemctl", "--user", "show", "mki-noticias.service",
             "-p", "Result", "-p", "ExecMainStartTimestamp",
             "-p", "ExecMainExitTimestamp"],
            capture_output=True, text=True, timeout=10)
        if r.returncode != 0 or not r.stdout.strip():
            return None
        datos = {}
        for linea in r.stdout.strip().splitlines():
            if "=" in linea:
                clave, valor = linea.split("=", 1)
                datos[clave] = valor
        return datos or None
    except Exception:
        return None


def _hora_desde_timestamp_systemd(valor: str) -> str | None:
    """'Tue 2026-09-01 18:20:00 -04' → '18:20'. None si no matchea."""
    if not valor:
        return None
    m = re.search(r"\d{4}-\d{2}-\d{2} (\d{2}:\d{2}):\d{2}", valor)
    return m.group(1) if m else None


def chequear_noticias() -> tuple:
    corridas = costos.corridas_del_dia("noticias")
    if not corridas:
        colgado = _proceso_noticias_colgado()
        if colgado:
            # Errata «launchd» corregida en la corrida 16-1 (§67): esta
            # máquina corre systemd; la regla es la misma en los dos.
            return False, (f"noticias: el job NO corrió hoy — {colgado}; "
                           "el planificador no re-dispara el job mientras su proceso siga vivo")
        if _rastro_noticias_hoy_en_log():
            refuerzo = ""
            estado = _estado_systemd_noticias()
            if estado and estado.get("Result") == "timeout":
                hora = _hora_desde_timestamp_systemd(estado.get("ExecMainExitTimestamp"))
                refuerzo = f" — matado por timeout a las {hora}" if hora else " — matado por timeout"
            return False, ("noticias: corrió y NO completó (rastro en el log, "
                           "sin registro en el ledger de costos)" + refuerzo)
        return False, "noticias: el job NO corrió hoy"
    ultima = corridas[-1]
    resultado = ultima.get("resultado", "?")
    if resultado == "rss_fallo":
        return False, "noticias: corrió pero el RSS falló"
    if resultado == "error_analisis":
        # Corrida 16-1 (acta §93.3 ii, tarjeta §74): del 7-sep al 2-oct-2026
        # la API rechazó cada llamada por falta de crédito y el ledger decía
        # «ok · 0 analizados» 20 veces seguidas. «0 analizados con error» es
        # falla; «0 analizados sin pendientes» y el freno siguen siendo OK.
        return False, (f"noticias: corrió pero el análisis FALLÓ "
                       f"({ultima.get('error_tipo', '?')} en el lote {ultima.get('error_lote', '?')}) "
                       f"· {ultima.get('analizados', 0)} analizados · "
                       f"pendientes {ultima.get('pendientes_restantes', '?')}")
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


def _escribir_pendiente(hoy: date, fallas: list, reintentos_activos: bool,
                        negativa: dict | None = None) -> None:
    """`negativa` (corrida 16-1): la negativa declarada que motivó la alerta,
    si la hubo; el pase de las 20:30 la usa para cerrar el caso."""
    with open(RUTA_PENDIENTE, "w", encoding="utf-8") as f:
        json.dump({"fecha": hoy.isoformat(),
                   "creado_utc": datetime.now(timezone.utc).isoformat(),
                   "fallas": fallas,
                   "reintentos_activos": reintentos_activos,
                   "negativa": negativa},
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
    pendiente = _leer_pendiente(hoy)
    if pendiente is None:
        _log("sin alerta pendiente de hoy — nada que re-chequear")
        return 0
    import senales
    if senales.info_snapshot_hoy():
        ok = enviar_retractacion_si_corresponde(hoy)
        return 0 if ok else 1
    import alertas
    activo, detalle = snapshot_en_curso(hoy)
    negativa = pendiente.get("negativa")
    if negativa and not activo:
        # Corrida 16-1 (acta §93.8 d; tarjeta §72 (i)): la alerta de una
        # negativa declarada tiene epílogo aunque NO haya sello. Nadie va a
        # reintentar (las negativas no entran al bucle de reintentos), así
        # que el mensaje cierra el caso por hoy, con la hora real. El
        # marcador QUEDA (BL3 del dictamen 16-1): si un sello manual llegara
        # más tarde, snapshot.py envía la retractación y ningún mensaje
        # publicado queda contradicho por la base (precedente 5.0.2).
        hora = alertas._hora_chile(datetime.now(timezone.utc).isoformat())
        texto = (f"🟡 <b>VIGÍA MKI — re-chequeo {hoy.isoformat()}</b>\n"
                 f"sigue sin sellar a las {hora}: la negativa declarada "
                 f"[{negativa.get('codigo', '?')}] sigue en pie ({negativa.get('texto', '')}) "
                 "y no hay proceso de snapshot vivo. Caso cerrado por hoy: la sesión "
                 "queda sin sello en el riel de medición. Si un sello manual llegara "
                 "más tarde, snapshot.py avisará.")
        ok, det = alertas.enviar_mensaje(texto)
        _log(f"epílogo Telegram (negativa, caso cerrado): {'enviado' if ok else 'NO enviado — ' + det}")
        return 0 if ok else 1
    # Sigue sin sellar: se dice, y el marcador QUEDA — si el sello llega
    # más tarde por su cuenta, snapshot.py enviará la retractación.
    estado = (f"reintentos aún activos ({detalle})" if activo
              else "sin proceso de snapshot vivo")
    texto = (f"🟠 <b>VIGÍA MKI — re-chequeo {hoy.isoformat()}</b>\n"
             f"sigue sin sellar a las {HORA_RECHEQUEO}: {estado}. "
             "Si sella más tarde, llegará la retractación.")
    ok, det = alertas.enviar_mensaje(texto)
    _log(f"epílogo Telegram: {'enviado' if ok else 'NO enviado — ' + det}")
    return 0 if ok else 1


def componer_alerta(hoy: date, resultados: list, en_curso: tuple) -> str:
    """Texto de la alerta de las 19:00. Si el snapshot no selló, la línea
    anuncia el re-chequeo de las 20:30 — y si hay reintentos EN CURSO, lo
    dice en vez de dar el día por perdido (5.0.1).

    Corrida 16-1 (acta §93.8 d): si el snapshot NO selló por una negativa
    declarada, el mensaje es otro —amarillo, no rojo—: dice la negativa con
    su motivo, deja claro que no es falla, y anuncia el re-chequeo que cierra
    el caso. Las fallas de los demás chequeos, si las hay, van aparte."""
    negativa = next((d for ok, d in resultados if es_negativa(d)), None)
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
    bien = [d.split(":")[0] for ok, d in resultados if ok and not es_negativa(d)]
    if negativa is not None:
        return (f"🟡 <b>VIGÍA MKI — {hoy.isoformat()}</b>\n"
                f"{negativa}\n"
                f"(no es falla: snapshot.py se negó a sellar por regla; "
                f"re-chequeo a las {HORA_RECHEQUEO} cierra el caso)"
                + ("\nFalló hoy:\n" + "\n".join(f"· {f}" for f in fallas) if fallas else "")
                + (f"\nOK: {', '.join(bien)}" if bien else ""))
    return (f"🛑 <b>VIGÍA MKI — {hoy.isoformat()}</b>\n"
            + "Falló hoy:\n" + "\n".join(f"· {f}" for f in fallas)
            + (f"\nOK: {', '.join(bien)}" if bien else ""))


def rotar_log_vigia() -> None:
    from registro import rotar_log
    rotar_log(os.path.join(DIRECTORIO, "data", "vigia.log"))


def revision(hoy: date) -> int:
    """El pase de las 19:00 para la fecha `hoy`. Separado de `main()` en
    la corrida 16-1 para poder probarlo cualquier día (main() exime el fin
    de semana con el reloj real)."""
    rotar_log_vigia()
    _log("mki_vigia.py — revisión del día operativo")
    resultados = [chequear_snapshot(hoy), chequear_descarga(hoy), chequear_noticias(),
                  chequear_reporte(), chequear_backup(), chequear_ancla_temporal(hoy),
                  chequear_guarda_puntaje(hoy)]
    negativa = next((d for ok, d in resultados if es_negativa(d)), None)
    for ok, detalle in resultados:
        marca = "NEGATIVA" if es_negativa(detalle) else ("OK " if ok else "FALLA")
        _log(f"  {marca} {detalle}")
    if all(ok for ok, _ in resultados) and negativa is None:
        _log("todo OK — sin alerta")
        return 0

    sin_sellar = not resultados[0][0] or negativa is not None
    en_curso = snapshot_en_curso(hoy) if sin_sellar else (False, "")
    if sin_sellar:
        detalle_negativa = None
        if negativa is not None:
            leida = _negativa_declarada_en_log(hoy) or {}
            detalle_negativa = {"codigo": leida.get("codigo", "?"),
                                "texto": leida.get("texto", negativa)}
        _escribir_pendiente(hoy, [d for ok, d in resultados if not ok], en_curso[0],
                            negativa=detalle_negativa)
        _log(f"marcador escrito — el pase de las {HORA_RECHEQUEO} enviará el epílogo")

    import alertas
    texto = componer_alerta(hoy, resultados, en_curso)
    ok, detalle = alertas.enviar_mensaje(texto)
    _log(f"alerta Telegram: {'enviada' if ok else 'NO enviada — ' + detalle}")
    return 0 if ok else 1


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
    return revision(hoy)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        _log(f"ERROR no manejado: {enmascarar_secretos(str(e))}")
        sys.exit(1)
