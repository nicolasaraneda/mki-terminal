# ============================================================
# Red de seguridad git REAL (Etapa 5.0 WS2.5) — com.mki.backup, 18:40
# hábiles, después del snapshot (18:15) que refresca los CSV.
#
# Hace UNA cosa: si data/backups/ cambió, lo commitea. La auditoría 13–24
# jul encontró que los CSV se commitearon una sola vez (5-jul) — la "red de
# seguridad versionada" no existía de verdad hasta este job.
#
# Alcance estricto: SOLO los paths de data/backups (el commit lleva pathspec,
# así que nada más entra aunque hubiera otras cosas staged). Jamás push:
# publicar es un acto manual del usuario.
#
# 5.1.0 / acta §90.8 (corrida 15) — EL BACKUP NO SE LE ADELANTA AL SELLO.
# El 28-sep-2026 el PC despertó de una suspensión y los ocho timers
# dispararon juntos a las 14:42 de Chile: este job commiteó «Backup diario
# 2026-09-28» (5321f6b) ANTES de que el día se sellara. Entre los jobs no
# hay dependencia: el orden lo daba sólo el reloj (18:40 > 18:15). Nicolás
# firmó la opción (c) de la tarjeta §64: el orden lo pone este archivo, sin
# tocar unidades instaladas. `decidir_commit()` es pura: con snapshot.py
# vivo nunca commitea (el sello y sus CSV se escriben en ese proceso), y en
# día de semana sin snapshot sellado se niega mientras el sello todavía
# pueda ocurrir (antes de las 18:15). Negarse no toca el índice y sale con
# 0, como en sombra: el vigía de las 19:00 alerta si el día termina sin
# commit. La base se LEE en `mode=ro`; no se importa `senales` (su
# `init_db()` hace DDL) ni `mki_vigia` (trae la red).
# ============================================================

import os
import sqlite3
import subprocess
import sys
from datetime import date, datetime, time, timezone
from urllib.parse import quote

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))

# La hora de `mki-snapshot.timer` (OnCalendar=Mon..Fri 18:15 America/Santiago)
# y de com.mki.snapshot.plist. Si el timer cambia, cambia acá:
# tests/test_backup_orden.py lee las dos plantillas y exige que coincidan.
# Es hora LOCAL del proceso; las unidades fijan TZ=America/Santiago.
HORA_SNAPSHOT_LOCAL = time(18, 15)

# ┌──────────────────────────────────────────────────────────────────────┐
# │ RAMA 5 — ELECCIÓN DE AGENTE, PENDIENTE DE FIRMA (el acta no la da).  │
# │ Día de semana, sin sello, pasada la hora y sin snapshot.py vivo:     │
# │ nada indica que el sello vaya a llegar. True = se commitea igual y   │
# │ el log lo dice («DÍA SIN SELLO»). False = «negarse siempre». Cambiar │
# │ de opción es tocar ESTA línea; las dos posiciones tienen test.       │
# └──────────────────────────────────────────────────────────────────────┘
COMMITEAR_DIA_SIN_SELLO = True

_DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado",
         "domingo")


def _git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", DIRECTORIO, *args],
                          capture_output=True, text=True)


def _ahora_local() -> datetime:
    """El reloj local del proceso, el MISMO que usa snapshot.py para la
    `fecha` de la tabla `snapshots` (`date.today()`). Se lee UNA vez por
    corrida: la fecha que se busca en la base y la del mensaje del commit
    salen de la misma lectura."""
    return datetime.now()


def _ruta_db() -> str:
    """Se arma al usarla y no al importar: los tests que mueven DIRECTORIO
    a una carpeta temporal no abren nunca la base real."""
    return os.path.join(DIRECTORIO, "senales.db")


def _snapshot_sellado(fecha_local: date, ruta_db: str) -> bool:
    """¿Hay fila en `snapshots` para esta fecha? La base se abre en
    `mode=ro`: el backup no escribe en ella, y una ruta inexistente no crea
    un archivo vacío. Todo lo que impida leer cuenta como NO sellado, con
    su razón en el log."""
    if not os.path.exists(ruta_db):
        print(f"  snapshot de hoy: no se puede leer (la base no existe: "
              f"{ruta_db}) — cuenta como NO sellado", flush=True)
        return False
    conn = None
    try:
        # quote(): un `?` o un `#` en la ruta cortarían la URI antes de mode=ro.
        conn = sqlite3.connect(f"file:{quote(ruta_db)}?mode=ro", uri=True)
        fila = conn.execute("SELECT 1 FROM snapshots WHERE fecha = ?",
                            (fecha_local.isoformat(),)).fetchone()
        return fila is not None
    except sqlite3.Error as e:
        print(f"  snapshot de hoy: no se pudo leer la base ({e}) — cuenta "
              "como NO sellado", flush=True)
        return False
    finally:
        if conn is not None:
            conn.close()


def _snapshot_vivo() -> bool:
    """¿Hay un snapshot.py vivo AHORA? Misma técnica que el vigía
    (`mki_vigia._hay_proceso_snapshot`), duplicada a propósito para no
    importarlo. pgrep existe en Linux y en macOS."""
    try:
        r = subprocess.run(["pgrep", "-f", "snapshot.py"],
                           capture_output=True, text=True, timeout=10)
        return bool(r.stdout.strip())
    except Exception:
        return False


def decidir_commit(ahora_local: datetime, snapshot_sellado_hoy: bool,
                   snapshot_vivo: bool) -> tuple[bool, str]:
    """(commitear, motivo). Función PURA: sin reloj, sin base, sin git.

    El criterio para esperar un snapshot es «lunes a viernes en la fecha
    local», NO «día hábil de NYSE»: el riel de medición sella en feriado de
    NYSE (hay snapshot del 2026-09-07, Labor Day). Las reglas van en orden."""
    dia = _DIAS[ahora_local.weekday()]
    hora = ahora_local.strftime("%H:%M")
    limite = HORA_SNAPSHOT_LOCAL.strftime("%H:%M")

    # 0. Con snapshot.py vivo NUNCA se commitea, sea el día que sea y esté
    #    o no la fila de hoy en la base: el sello se escribe ANTES de que
    #    ese proceso exporte los CSV a data/backups (main() de snapshot.py:
    #    sello → epílogo del vigía → verificador → respaldo), así que un
    #    backup que corre en esos segundos commitea CSV viejos bajo un
    #    nombre que promete el sello de hoy (el 28-sep fueron 32 s entre la
    #    emisión, 14:42:58, y el fin del proceso, 14:43:30). Es la regla de
    #    ORDEN en su forma más simple: el backup no corre encima del
    #    snapshot. Un pgrep con falso positivo (otro proceso con
    #    «snapshot.py» en su línea de comando) sólo produce un día sin
    #    commit que el vigía de las 19:00 reporta: falla hacia lo visible.
    if snapshot_vivo:
        return False, (
            f"NO SE COMMITEA: snapshot.py sigue corriendo ({dia} {hora}). "
            "El sello y sus CSV se escriben en ese proceso y el backup no se "
            "le adelanta (acta §90.8). data/backups queda sin tocar hasta el "
            "próximo disparo")

    # 1. Fin de semana: no hay snapshot que esperar. Lo que cambió (el
    #    export del sellador de dinero de la noche del viernes) se versiona.
    if ahora_local.weekday() >= 5:
        return True, (f"fin de semana ({dia}): no hay snapshot que esperar; "
                      "se commitea lo que haya cambiado en data/backups")

    # 2. El caso normal de las 18:40.
    if snapshot_sellado_hoy:
        return True, "snapshot de hoy sellado: se commitea"

    # 3. Disparo fuera de hora (despertar de una suspensión): es el 28-sep
    #    a las 14:42.
    if ahora_local.time() < HORA_SNAPSHOT_LOCAL:
        return False, (
            f"NO SE COMMITEA: {dia} sin snapshot sellado y son las {hora}, "
            f"antes de las {limite} (hora del snapshot). El sello de hoy "
            "todavía puede ocurrir y el backup no se le adelanta (acta "
            "§90.8). data/backups queda sin tocar hasta el próximo disparo")

    # 4. (Absorbida por la regla 0: un snapshot.py vivo reintentando ante
    #    «sin datos de mercado» ya devolvió arriba.)

    # 5. Sin sello y sin proceso que lo intente: nada indica que el sello
    #    vaya a llegar. §90.8 pide ORDEN, no abstención: negarse acá no
    #    ordena nada y deja 24 h o más sin copia versionada en una máquina
    #    sin réplica (dictamen del director-programa, pre-mortem de la
    #    corrida 15). ELECCIÓN DE AGENTE: ver la constante.
    if COMMITEAR_DIA_SIN_SELLO:
        return True, (
            f"DÍA SIN SELLO: {dia}, son las {hora}, no hay snapshot sellado "
            "de hoy ni snapshot.py vivo. Este commit NO contiene el sello de "
            "hoy; se commitea igual para no dejar sin versionar los CSV del "
            "día (verificaciones, export del sellador de dinero)")
    return False, (
        f"NO SE COMMITEA: día sin sello ({dia}, {hora}, sin snapshot sellado "
        "de hoy ni snapshot.py vivo) y COMMITEAR_DIA_SIN_SELLO está en "
        "False. data/backups queda sin tocar hasta el próximo día sellado")


def main() -> int:
    from registro import rotar_log
    import modo
    rotar_log(os.path.join(DIRECTORIO, "data", "backup.log"))
    print(f"[{datetime.now(timezone.utc).isoformat()}] mki_backup.py", flush=True)
    print(f"  {modo.descripcion()}", flush=True)
    # 5.0.3 — en sombra no se commitea NADA: dos máquinas commiteando los
    # mismos CSV sobre la misma historia es exactamente lo que la ventana
    # debe evitar. Ni siquiera se toca el índice de git (sin `git add`):
    # el árbol de trabajo es el código que los timers ejecutan.
    if modo.en_sombra():
        print("  modo sombra: NO se commitea (comportamiento correcto, "
              "no es una falla)", flush=True)
        return 0
    # 5.1.0 / §90.8 — la decisión va DESPUÉS de la sombra y ANTES de
    # `git add`. Las tres entradas quedan en el log: quien lo lea puede
    # rehacer la decisión a mano.
    ahora = _ahora_local()
    sellado = _snapshot_sellado(ahora.date(), _ruta_db())
    vivo = _snapshot_vivo()
    print(f"  fecha local {ahora.date().isoformat()} "
          f"({_DIAS[ahora.weekday()]}) {ahora.strftime('%H:%M:%S')} · "
          f"snapshot de hoy sellado: {'sí' if sellado else 'no'} · "
          f"snapshot.py vivo: {'sí' if vivo else 'no'}", flush=True)
    commitear, motivo = decidir_commit(ahora, sellado, vivo)
    print(f"  {motivo}", flush=True)
    if not commitear:
        return 0
    r = _git("add", "--", "data/backups")
    if r.returncode:
        print(f"  git add falló: {r.stderr.strip()}")
        return 1
    if _git("diff", "--cached", "--quiet", "--", "data/backups").returncode == 0:
        print("  sin cambios en data/backups — nada que commitear")
        return 0
    mensaje = f"Backup diario {ahora.date().isoformat()}"
    r = _git("commit", "-m", mensaje, "--", "data/backups")
    if r.returncode:
        print(f"  git commit falló: {r.stderr.strip() or r.stdout.strip()}")
        return 1
    print(f"  commit creado: {mensaje}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
