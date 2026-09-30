# BLOQUE 4 — `mki_backup.py` (acta §90.8, tarjeta §64) — informe de cierre

Worktree: `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/de320909-2c4c-4d19-9942-e7dc8900b9a2/scratchpad/wt15` (HEAD 2f73eb2). Archivos míos: `mki_backup.py` (modificado) y `tests/test_backup_orden.py` (nuevo). Ningún git de escritura, ningún systemd, `.env` no leído, la `senales.db` real no abierta (sólo la COPIA del worktree, inodo 34553 vs 107383 del real, y sólo en `mode=ro`).

**Sobre `tests/test_autonomia.py`: NO lo toqué.** Su diff (`git diff -- tests/test_autonomia.py`) agrega `_RelojTrasElCierre` y `monkeypatch.setattr(snapshot, "datetime", …)` en la fixture `entorno`, con docstring «Corrida 15 (acta §90.1 b): desde la guarda de conocibilidad, `ejecutar_snapshot` se niega a sellar si la sesión de `sox_fecha` no ha cerrado…». Es el bloque de `snapshot.py`, no el mío: no menciona `mki_backup`. Mis únicas escrituras en el worktree fueron `tests/test_backup_orden.py` (22:32:43) y `mki_backup.py` (22:33:34, 22:37:30, 23:02); el mtime de `test_autonomia.py` es 22:34:03, un instante en el que yo estaba corriendo pytest, no escribiendo. No lo revertí porque no es mi archivo: que lo confirme quien lleva el bloque de `snapshot.py`.

---

## 1. Diff completo de `mki_backup.py` y archivo de tests entero

### `git -C $WT diff -- mki_backup.py`

```diff
diff --git a/mki_backup.py b/mki_backup.py
index 7530400..f4dde95 100644
--- a/mki_backup.py
+++ b/mki_backup.py
@@ -9,21 +9,160 @@
 # Alcance estricto: SOLO los paths de data/backups (el commit lleva pathspec,
 # así que nada más entra aunque hubiera otras cosas staged). Jamás push:
 # publicar es un acto manual del usuario.
+#
+# 5.1.0 / acta §90.8 (corrida 15) — EL BACKUP NO SE LE ADELANTA AL SELLO.
+# El 28-sep-2026 el PC despertó de una suspensión y los ocho timers
+# dispararon juntos a las 14:42 de Chile: este job commiteó «Backup diario
+# 2026-09-28» (5321f6b) ANTES de que el día se sellara. Entre los jobs no
+# hay dependencia: el orden lo daba sólo el reloj (18:40 > 18:15). Nicolás
+# firmó la opción (c) de la tarjeta §64: el orden lo pone este archivo, sin
+# tocar unidades instaladas. `decidir_commit()` es pura y tiene cinco ramas;
+# en día de semana sin snapshot sellado se niega mientras el sello todavía
+# pueda ocurrir (antes de las 18:15, o con snapshot.py vivo). Negarse no
+# toca el índice y sale con 0, como en sombra: el vigía de las 19:00 alerta
+# si el día termina sin commit. La base se LEE en `mode=ro`; no se importa
+# `senales` (su `init_db()` hace DDL) ni `mki_vigia` (trae la red).
 # ============================================================
 
 import os
+import sqlite3
 import subprocess
 import sys
-from datetime import date, datetime, timezone
+from datetime import date, datetime, time, timezone
+from urllib.parse import quote
 
 DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
 
+# La hora de `mki-snapshot.timer` (OnCalendar=Mon..Fri 18:15 America/Santiago)
+# y de com.mki.snapshot.plist. Si el timer cambia, cambia acá:
+# tests/test_backup_orden.py lee las dos plantillas y exige que coincidan.
+# Es hora LOCAL del proceso; las unidades fijan TZ=America/Santiago.
+HORA_SNAPSHOT_LOCAL = time(18, 15)
+
+# ┌──────────────────────────────────────────────────────────────────────┐
+# │ RAMA 5 — ELECCIÓN DE AGENTE, PENDIENTE DE FIRMA (el acta no la da).  │
+# │ Día de semana, sin sello, pasada la hora y sin snapshot.py vivo:     │
+# │ nada indica que el sello vaya a llegar. True = se commitea igual y   │
+# │ el log lo dice («DÍA SIN SELLO»). False = «negarse siempre». Cambiar │
+# │ de opción es tocar ESTA línea; las dos posiciones tienen test.       │
+# └──────────────────────────────────────────────────────────────────────┘
+COMMITEAR_DIA_SIN_SELLO = True
+
+_DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado",
+         "domingo")
+
 
 def _git(*args) -> subprocess.CompletedProcess:
     return subprocess.run(["git", "-C", DIRECTORIO, *args],
                           capture_output=True, text=True)
 
 
+def _ahora_local() -> datetime:
+    """El reloj local del proceso, el MISMO que usa snapshot.py para la
+    `fecha` de la tabla `snapshots` (`date.today()`). Se lee UNA vez por
+    corrida: la fecha que se busca en la base y la del mensaje del commit
+    salen de la misma lectura."""
+    return datetime.now()
+
+
+def _ruta_db() -> str:
+    """Se arma al usarla y no al importar: los tests que mueven DIRECTORIO
+    a una carpeta temporal no abren nunca la base real."""
+    return os.path.join(DIRECTORIO, "senales.db")
+
+
+def _snapshot_sellado(fecha_local: date, ruta_db: str) -> bool:
+    """¿Hay fila en `snapshots` para esta fecha? La base se abre en
+    `mode=ro`: el backup no escribe en ella, y una ruta inexistente no crea
+    un archivo vacío. Todo lo que impida leer cuenta como NO sellado, con
+    su razón en el log."""
+    if not os.path.exists(ruta_db):
+        print(f"  snapshot de hoy: no se puede leer (la base no existe: "
+              f"{ruta_db}) — cuenta como NO sellado", flush=True)
+        return False
+    conn = None
+    try:
+        # quote(): un `?` o un `#` en la ruta cortarían la URI antes de mode=ro.
+        conn = sqlite3.connect(f"file:{quote(ruta_db)}?mode=ro", uri=True)
+        fila = conn.execute("SELECT 1 FROM snapshots WHERE fecha = ?",
+                            (fecha_local.isoformat(),)).fetchone()
+        return fila is not None
+    except sqlite3.Error as e:
+        print(f"  snapshot de hoy: no se pudo leer la base ({e}) — cuenta "
+              "como NO sellado", flush=True)
+        return False
+    finally:
+        if conn is not None:
+            conn.close()
+
+
+def _snapshot_vivo() -> bool:
+    """¿Hay un snapshot.py vivo AHORA? Misma técnica que el vigía
+    (`mki_vigia._hay_proceso_snapshot`), duplicada a propósito para no
+    importarlo. pgrep existe en Linux y en macOS."""
+    try:
+        r = subprocess.run(["pgrep", "-f", "snapshot.py"],
+                           capture_output=True, text=True, timeout=10)
+        return bool(r.stdout.strip())
+    except Exception:
+        return False
+
+
+def decidir_commit(ahora_local: datetime, snapshot_sellado_hoy: bool,
+                   snapshot_vivo: bool) -> tuple[bool, str]:
+    """(commitear, motivo). Función PURA: sin reloj, sin base, sin git.
+
+    El criterio para esperar un snapshot es «lunes a viernes en la fecha
+    local», NO «día hábil de NYSE»: el riel de medición sella en feriado de
+    NYSE (hay snapshot del 2026-09-07, Labor Day). Las reglas van en orden."""
+    dia = _DIAS[ahora_local.weekday()]
+    hora = ahora_local.strftime("%H:%M")
+    limite = HORA_SNAPSHOT_LOCAL.strftime("%H:%M")
+
+    # 1. Fin de semana: no hay snapshot que esperar. Lo que cambió (el
+    #    export del sellador de dinero de la noche del viernes) se versiona.
+    if ahora_local.weekday() >= 5:
+        return True, (f"fin de semana ({dia}): no hay snapshot que esperar; "
+                      "se commitea lo que haya cambiado en data/backups")
+
+    # 2. El caso normal de las 18:40.
+    if snapshot_sellado_hoy:
+        return True, "snapshot de hoy sellado: se commitea"
+
+    # 3. Disparo fuera de hora (despertar de una suspensión): es el 28-sep
+    #    a las 14:42.
+    if ahora_local.time() < HORA_SNAPSHOT_LOCAL:
+        return False, (
+            f"NO SE COMMITEA: {dia} sin snapshot sellado y son las {hora}, "
+            f"antes de las {limite} (hora del snapshot). El sello de hoy "
+            "todavía puede ocurrir y el backup no se le adelanta (acta "
+            "§90.8). data/backups queda sin tocar hasta el próximo disparo")
+
+    # 4. snapshot.py reintenta hasta ~60 min ante «sin datos de mercado».
+    if snapshot_vivo:
+        return False, (
+            f"NO SE COMMITEA: {dia} sin snapshot sellado a las {hora} y "
+            "snapshot.py sigue vivo (reintentando). El sello de hoy todavía "
+            "puede ocurrir y el backup no se le adelanta (acta §90.8). "
+            "data/backups queda sin tocar hasta el próximo disparo")
+
+    # 5. Sin sello y sin proceso que lo intente: nada indica que el sello
+    #    vaya a llegar. §90.8 pide ORDEN, no abstención: negarse acá no
+    #    ordena nada y deja 24 h o más sin copia versionada en una máquina
+    #    sin réplica (dictamen del director-programa, pre-mortem de la
+    #    corrida 15). ELECCIÓN DE AGENTE: ver la constante.
+    if COMMITEAR_DIA_SIN_SELLO:
+        return True, (
+            f"DÍA SIN SELLO: {dia}, son las {hora}, no hay snapshot sellado "
+            "de hoy ni snapshot.py vivo. Este commit NO contiene el sello de "
+            "hoy; se commitea igual para no dejar sin versionar los CSV del "
+            "día (verificaciones, export del sellador de dinero)")
+    return False, (
+        f"NO SE COMMITEA: día sin sello ({dia}, {hora}, sin snapshot sellado "
+        "de hoy ni snapshot.py vivo) y COMMITEAR_DIA_SIN_SELLO está en "
+        "False. data/backups queda sin tocar hasta el próximo día sellado")
+
+
 def main() -> int:
     from registro import rotar_log
     import modo
@@ -38,6 +177,20 @@ def main() -> int:
         print("  modo sombra: NO se commitea (comportamiento correcto, "
               "no es una falla)", flush=True)
         return 0
+    # 5.1.0 / §90.8 — la decisión va DESPUÉS de la sombra y ANTES de
+    # `git add`. Las tres entradas quedan en el log: quien lo lea puede
+    # rehacer la decisión a mano.
+    ahora = _ahora_local()
+    sellado = _snapshot_sellado(ahora.date(), _ruta_db())
+    vivo = _snapshot_vivo()
+    print(f"  fecha local {ahora.date().isoformat()} "
+          f"({_DIAS[ahora.weekday()]}) {ahora.strftime('%H:%M:%S')} · "
+          f"snapshot de hoy sellado: {'sí' if sellado else 'no'} · "
+          f"snapshot.py vivo: {'sí' if vivo else 'no'}", flush=True)
+    commitear, motivo = decidir_commit(ahora, sellado, vivo)
+    print(f"  {motivo}", flush=True)
+    if not commitear:
+        return 0
     r = _git("add", "--", "data/backups")
     if r.returncode:
         print(f"  git add falló: {r.stderr.strip()}")
@@ -45,7 +198,7 @@ def main() -> int:
     if _git("diff", "--cached", "--quiet", "--", "data/backups").returncode == 0:
         print("  sin cambios en data/backups — nada que commitear")
         return 0
-    mensaje = f"Backup diario {date.today().isoformat()}"
+    mensaje = f"Backup diario {ahora.date().isoformat()}"
     r = _git("commit", "-m", mensaje, "--", "data/backups")
     if r.returncode:
         print(f"  git commit falló: {r.stderr.strip() or r.stdout.strip()}")
```

Desvíos respecto del diseño, declarados: (a) la ruta de la base es `_ruta_db()` = `DIRECTORIO/senales.db` armada al usarla, no una constante `RUTA_DB` fijada al importar — `tests/test_sombra.py` mueve `DIRECTORIO` a `tmp_path`, y con una constante de import esos tests habrían abierto la base real (en ro, pero real). Puntos de inyección: `_ahora_local`, `_snapshot_vivo`, `_snapshot_sellado`, `_git`, `DIRECTORIO`, `COMMITEAR_DIA_SIN_SELLO`. (b) `quote(ruta_db)` en la URI: un `?` o `#` en la ruta cortaría el `mode=ro` (test con carpeta «Mis Proyectos #1 ¿50%?»). (c) El mensaje del commit usa `ahora.date()` en vez de `date.today()`: misma cadena, una sola lectura de reloj por corrida (test).

### `tests/test_backup_orden.py` (entero; 49 funciones, 83 casos)

```python
# ============================================================
# Tests del orden entre el backup y el sello (plataforma 5.1.0, acta §90.8,
# corrida 15; tarjeta §64 de GEMELO/resultados/espera_firma.md).
#
# EL DEFECTO QUE ESTOS TESTS REPRODUCEN. El 28-sep-2026 el PC despertó de
# una suspensión y los ocho timers dispararon juntos a las 14:42 de Chile.
# `mki_backup.py` terminó un segundo después de arrancar y commiteó «Backup
# diario 2026-09-28» (5321f6b) ANTES de que el día se sellara: un artefacto
# publicado cuyo nombre no describe su contenido. Entre los jobs no hay
# dependencia; el orden lo daba sólo el reloj (18:40 > 18:15).
#
# QUÉ PROTEGEN. (1) La función pura `decidir_commit`, rama por rama.
# (2) Que negarse no toque el índice de git ni una vez. (3) Que la sombra
# siga ganándole a todo. (4) Que el backup LEA la base y jamás la escriba
# (`mode=ro`). (5) Que la hora contra la que se decide sea la de la
# plantilla del timer, y no una cifra que alguien recuerda.
#
# Todo sintético: reloj inyectado, base temporal en `tmp_path`, `_git` y
# `pgrep` espiados. Ningún test ejecuta git, ni abre la `senales.db` real,
# ni toca la red.
# ============================================================

import ast
import os
import plistlib
import re
import sqlite3
import subprocess
import sys
from datetime import date, datetime, time, timedelta

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import mki_backup

# Fechas con nombre. Verificadas abajo contra el calendario (un test que
# llama «lunes» a un martes prueba otra cosa que la que dice).
LUNES_28_SEP = date(2026, 9, 28)       # el día del despertar
MARTES_29_SEP = date(2026, 9, 29)
FERIADO_NYSE = date(2026, 9, 7)        # Labor Day: lunes, sin sesión en XNYS
LUNES_COMUN = date(2026, 9, 14)
SABADO = date(2026, 10, 3)
DOMINGO = date(2026, 10, 4)


def _a_las(fecha: date, h: int, m: int, s: int = 0) -> datetime:
    return datetime.combine(fecha, time(h, m, s))


class _R:
    """Resultado de git de mentira."""
    def __init__(self, returncode: int = 0):
        self.returncode = returncode
        self.stdout = ""
        self.stderr = ""


@pytest.fixture
def titular(monkeypatch):
    monkeypatch.delenv("MKI_MODO", raising=False)


@pytest.fixture
def git_espia(monkeypatch):
    """Anota cada llamada a `_git` y simula que data/backups SÍ cambió
    (`diff --cached --quiet` devuelve 1): así un commit que el código
    intente queda a la vista, no escondido tras un «sin cambios»."""
    llamadas = []

    def falso(*args):
        llamadas.append(args)
        return _R(1 if args[0] == "diff" else 0)

    monkeypatch.setattr(mki_backup, "_git", falso)
    return llamadas


def _crear_base(carpeta, fechas=(), con_tabla=True) -> str:
    """Base temporal con el esquema mínimo de `snapshots` (senales.py)."""
    ruta = os.path.join(str(carpeta), "senales.db")
    conn = sqlite3.connect(ruta)
    if con_tabla:
        conn.execute("CREATE TABLE snapshots (fecha TEXT PRIMARY KEY, "
                     "creado_en TEXT NOT NULL)")
        for f in fechas:
            conn.execute("INSERT INTO snapshots (fecha, creado_en) VALUES (?, ?)",
                         (f, f"{f}T21:15:03.118402+00:00"))
    else:
        conn.execute("CREATE TABLE otra_cosa (x INTEGER)")
    conn.commit()
    conn.close()
    return ruta


def _montar(monkeypatch, tmp_path, ahora, selladas=(), vivo=False,
            con_base=True, estricto=True):
    """Máquina de mentira para `main()`: carpeta, base, reloj y pgrep.

    `estricto=False` sólo lo usa el test de reproducción: en HEAD los
    atributos `_ahora_local` y `_snapshot_vivo` todavía no existen, y con
    `raising=True` el test fallaría por AttributeError — la razón
    equivocada. Los demás tests van estrictos: si alguien renombra un punto
    de inyección, fallan ruidosamente en vez de leer el reloj de verdad."""
    monkeypatch.setattr(mki_backup, "DIRECTORIO", str(tmp_path))
    os.makedirs(tmp_path / "data", exist_ok=True)
    if con_base:
        _crear_base(tmp_path, selladas)
    monkeypatch.setattr(mki_backup, "_ahora_local", lambda: ahora,
                        raising=estricto)
    monkeypatch.setattr(mki_backup, "_snapshot_vivo", lambda: vivo,
                        raising=estricto)


# ------------------------------------------------------------
# 0. Las fechas de este archivo son lo que dicen ser
# ------------------------------------------------------------
def test_las_fechas_con_nombre_caen_en_el_dia_que_dicen():
    assert LUNES_28_SEP.weekday() == 0
    assert MARTES_29_SEP.weekday() == 1
    assert FERIADO_NYSE.weekday() == 0
    assert LUNES_COMUN.weekday() == 0
    assert SABADO.weekday() == 5
    assert DOMINGO.weekday() == 6


# ------------------------------------------------------------
# A. REPRODUCCIÓN del 28-sep-2026 14:42 (escrito ANTES del cambio)
# ------------------------------------------------------------
def test_reproduccion_28_sep_despertar_a_las_14_42_no_commitea(
        titular, git_espia, monkeypatch, tmp_path, capsys):
    """Titular, lunes 28-sep-2026 14:42 local, sin snapshot de hoy (la
    base tiene sellado hasta el viernes anterior). El backup NO debe tocar
    git. Contra el `mki_backup.py` de HEAD 2f73eb2 este test FALLA porque
    HEAD hace add + diff + commit: es el commit 5321f6b."""
    _montar(monkeypatch, tmp_path, _a_las(LUNES_28_SEP, 14, 42),
            selladas=("2026-09-24", "2026-09-25"), estricto=False)

    codigo = mki_backup.main()

    assert git_espia == [], (
        "el backup tocó git antes de que el día se sellara (el defecto del "
        f"28-sep-2026, acta §90.8): {git_espia}")
    assert codigo == 0          # negarse es el comportamiento correcto
    salida = capsys.readouterr().out
    assert "NO SE COMMITEA" in salida
    assert "14:42" in salida and "18:15" in salida


def test_los_puntos_de_inyeccion_existen():
    """El test de reproducción inyecta con `raising=False` (ver `_montar`).
    Este es su seguro: si un punto de inyección desaparece, se sabe acá."""
    for nombre in ("_ahora_local", "_snapshot_vivo", "_snapshot_sellado",
                   "_ruta_db", "_git", "decidir_commit", "DIRECTORIO",
                   "HORA_SNAPSHOT_LOCAL", "COMMITEAR_DIA_SIN_SELLO"):
        assert hasattr(mki_backup, nombre), nombre


# ------------------------------------------------------------
# B. `decidir_commit`, rama por rama (función pura, sin E/S)
# ------------------------------------------------------------
@pytest.mark.parametrize("fecha", [SABADO, DOMINGO])
@pytest.mark.parametrize("hora", [(0, 5), (10, 0), (14, 42), (18, 40), (23, 59)])
def test_rama1_fin_de_semana_commitea(fecha, hora):
    """No hay snapshot que esperar: lo que cambió en data/backups (el
    export del sellador de dinero de la noche del viernes) se versiona."""
    commitear, motivo = mki_backup.decidir_commit(
        _a_las(fecha, *hora), snapshot_sellado_hoy=False, snapshot_vivo=False)
    assert commitear is True
    assert "fin de semana" in motivo
    assert not motivo.startswith("DÍA SIN SELLO")


def test_rama1_va_primero_el_fin_de_semana_no_mira_el_proceso():
    """El ORDEN de las reglas es el del diseño: en sábado se commitea
    aunque haya un snapshot.py vivo. Consecuencia conocida y declarada en
    el informe de la corrida 15 (un despertar en sábado con `Persistent=`
    dispara los ocho juntos y esta regla no ordena nada). Si el diseño
    cambia, este test cambia con él."""
    commitear, _ = mki_backup.decidir_commit(
        _a_las(SABADO, 10, 0), snapshot_sellado_hoy=False, snapshot_vivo=True)
    assert commitear is True


@pytest.mark.parametrize("hora", [(14, 42), (18, 14, 59), (18, 15), (18, 40), (23, 59)])
@pytest.mark.parametrize("vivo", [False, True])
def test_rama2_dia_de_semana_sellado_commitea_a_cualquier_hora(hora, vivo):
    commitear, motivo = mki_backup.decidir_commit(
        _a_las(MARTES_29_SEP, *hora), snapshot_sellado_hoy=True,
        snapshot_vivo=vivo)
    assert commitear is True
    assert "sellado" in motivo
    assert not motivo.startswith("DÍA SIN SELLO")


def test_rama2_el_caso_normal_de_las_18_40():
    commitear, _ = mki_backup.decidir_commit(
        _a_las(MARTES_29_SEP, 18, 40), snapshot_sellado_hoy=True,
        snapshot_vivo=False)
    assert commitear is True


def test_rama3_las_14_42_sin_sello_se_niega():
    """Exactamente el 28-sep: disparo fuera de hora, el sello aún puede
    ocurrir."""
    commitear, motivo = mki_backup.decidir_commit(
        _a_las(LUNES_28_SEP, 14, 42), snapshot_sellado_hoy=False,
        snapshot_vivo=False)
    assert commitear is False
    assert motivo.startswith("NO SE COMMITEA")
    assert "14:42" in motivo and "18:15" in motivo and "§90.8" in motivo


def test_rama3_las_14_42_sin_sello_con_proceso_vivo_tambien_se_niega():
    """El despertar simultáneo visto desde el otro lado: snapshot.py ya
    arrancó cuando el backup mira. Se niega igual."""
    commitear, _ = mki_backup.decidir_commit(
        _a_las(LUNES_28_SEP, 14, 42), snapshot_sellado_hoy=False,
        snapshot_vivo=True)
    assert commitear is False


def test_rama3_borde_18_14_59_sin_sello_se_niega():
    for ahora in (_a_las(MARTES_29_SEP, 18, 14, 59),
                  datetime(2026, 9, 29, 18, 14, 59, 999999)):
        commitear, motivo = mki_backup.decidir_commit(
            ahora, snapshot_sellado_hoy=False, snapshot_vivo=False)
        assert commitear is False, ahora
        assert motivo.startswith("NO SE COMMITEA")


def test_rama3_nunca_commitea_sin_sello_antes_de_la_hora_en_dia_de_semana():
    """Barrido: los cinco días de semana, cada minuto de 00:00 a 18:14,
    con y sin proceso vivo. Ni uno commitea."""
    for d in range(5):
        fecha = LUNES_28_SEP + timedelta(days=d)
        assert fecha.weekday() == d
        for minuto in range(18 * 60 + 15):
            ahora = _a_las(fecha, minuto // 60, minuto % 60)
            for vivo in (False, True):
                commitear, _ = mki_backup.decidir_commit(ahora, False, vivo)
                assert commitear is False, (ahora, vivo)


def test_rama4_las_18_15_00_sin_sello_con_proceso_vivo_se_niega():
    """snapshot.py reintenta hasta ~60 min: el sello todavía puede ocurrir."""
    for hora in ((18, 15, 0), (18, 40, 0), (19, 14, 0)):
        commitear, motivo = mki_backup.decidir_commit(
            _a_las(MARTES_29_SEP, *hora), snapshot_sellado_hoy=False,
            snapshot_vivo=True)
        assert commitear is False, hora
        assert motivo.startswith("NO SE COMMITEA")
        assert "vivo" in motivo


def test_rama5_las_18_40_sin_sello_sin_proceso_commitea_y_lo_dice():
    """ELECCIÓN DE AGENTE (el acta no la da; va a tarjeta). El día ya no
    puede sellar: se commitea para no dejar los CSV sin versionar, y el
    motivo dice con todas las letras que el commit NO contiene el sello."""
    commitear, motivo = mki_backup.decidir_commit(
        _a_las(MARTES_29_SEP, 18, 40), snapshot_sellado_hoy=False,
        snapshot_vivo=False)
    assert commitear is True
    assert motivo.startswith("DÍA SIN SELLO:")
    assert "NO contiene el sello" in motivo
    assert "18:40" in motivo


def test_rama5_borde_18_15_00_sin_sello_sin_proceso_commitea():
    commitear, motivo = mki_backup.decidir_commit(
        _a_las(MARTES_29_SEP, 18, 15, 0), snapshot_sellado_hoy=False,
        snapshot_vivo=False)
    assert commitear is True
    assert motivo.startswith("DÍA SIN SELLO:")


def test_rama5_negarse_siempre_es_UNA_constante(monkeypatch):
    """La opción A de la tarjeta («negarse siempre que no haya sello en día
    de semana») es poner `COMMITEAR_DIA_SIN_SELLO = False`. Se prueba acá
    para que cambiar de opción no sea escribir código nuevo sin test."""
    monkeypatch.setattr(mki_backup, "COMMITEAR_DIA_SIN_SELLO", False)
    commitear, motivo = mki_backup.decidir_commit(
        _a_las(MARTES_29_SEP, 18, 40), snapshot_sellado_hoy=False,
        snapshot_vivo=False)
    assert commitear is False
    assert motivo.startswith("NO SE COMMITEA")
    assert "día sin sello" in motivo.lower()
    # y las demás ramas no se mueven con la constante
    assert mki_backup.decidir_commit(_a_las(SABADO, 10, 0), False, False)[0] is True
    assert mki_backup.decidir_commit(_a_las(MARTES_29_SEP, 18, 40), True, False)[0] is True
    assert mki_backup.decidir_commit(_a_las(LUNES_28_SEP, 14, 42), False, False)[0] is False
    assert mki_backup.decidir_commit(_a_las(MARTES_29_SEP, 18, 40), False, True)[0] is False


@pytest.mark.parametrize("hora,sellado,vivo", [
    ((14, 42), False, False),      # rama 3
    ((18, 14, 59), False, False),  # rama 3, borde
    ((18, 15), False, True),       # rama 4
    ((18, 40), False, False),      # rama 5
    ((18, 40), True, False),       # rama 2
    ((14, 42), True, False),       # rama 2 fuera de hora
])
def test_feriado_de_nyse_en_dia_de_semana_es_un_dia_de_semana_cualquiera(
        hora, sellado, vivo):
    """El riel de medición SELLA en feriado de NYSE (hay snapshot del
    2026-09-07, Labor Day): el criterio para esperar un snapshot es «lunes
    a viernes en la fecha local», no «día hábil de XNYS». El feriado decide
    lo mismo que un lunes común, entrada por entrada."""
    en_feriado = mki_backup.decidir_commit(_a_las(FERIADO_NYSE, *hora), sellado, vivo)
    en_comun = mki_backup.decidir_commit(_a_las(LUNES_COMUN, *hora), sellado, vivo)
    assert en_feriado == en_comun


def test_feriado_de_nyse_con_y_sin_sello():
    assert mki_backup.decidir_commit(
        _a_las(FERIADO_NYSE, 18, 40), True, False)[0] is True
    assert mki_backup.decidir_commit(
        _a_las(FERIADO_NYSE, 14, 42), False, False)[0] is False
    commitear, motivo = mki_backup.decidir_commit(
        _a_las(FERIADO_NYSE, 18, 40), False, False)
    assert commitear is True and motivo.startswith("DÍA SIN SELLO:")


def test_decidir_commit_es_pura(monkeypatch):
    """Sin E/S: con git, sqlite, pgrep y el reloj dinamitados, decide
    igual. Y la misma entrada da la misma salida."""
    def explota(*a, **k):
        raise AssertionError("decidir_commit hizo E/S")
    monkeypatch.setattr(mki_backup, "_git", explota)
    monkeypatch.setattr(mki_backup, "_snapshot_sellado", explota)
    monkeypatch.setattr(mki_backup, "_snapshot_vivo", explota)
    monkeypatch.setattr(mki_backup, "_ahora_local", explota)
    monkeypatch.setattr(mki_backup.subprocess, "run", explota)
    monkeypatch.setattr(mki_backup.sqlite3, "connect", explota)
    for ahora in (_a_las(SABADO, 10, 0), _a_las(LUNES_28_SEP, 14, 42),
                  _a_las(MARTES_29_SEP, 18, 40)):
        for sellado in (False, True):
            for vivo in (False, True):
                a = mki_backup.decidir_commit(ahora, sellado, vivo)
                b = mki_backup.decidir_commit(ahora, sellado, vivo)
                assert a == b
                assert isinstance(a[0], bool) and isinstance(a[1], str) and a[1]


# ------------------------------------------------------------
# C. `_snapshot_sellado`: lee la base, jamás la escribe
# ------------------------------------------------------------
def test_sellado_con_la_fila_de_hoy(tmp_path):
    ruta = _crear_base(tmp_path, ("2026-09-28", "2026-09-29"))
    assert mki_backup._snapshot_sellado(MARTES_29_SEP, ruta) is True


def test_sellado_sin_la_fila_de_hoy(tmp_path):
    """El sello de AYER no cuenta como sello de hoy."""
    ruta = _crear_base(tmp_path, ("2026-09-25", "2026-09-28"))
    assert mki_backup._snapshot_sellado(MARTES_29_SEP, ruta) is False
    assert mki_backup._snapshot_sellado(date(2026, 9, 30), ruta) is False
    assert mki_backup._snapshot_sellado(LUNES_28_SEP, ruta) is True


def test_sellado_con_la_tabla_vacia(tmp_path):
    ruta = _crear_base(tmp_path, ())
    assert mki_backup._snapshot_sellado(MARTES_29_SEP, ruta) is False


def test_sellado_contra_una_ruta_inexistente(tmp_path, capsys):
    """No sellado, con su razón en el log, y SIN crear el archivo (abrir
    en escritura lo habría creado vacío)."""
    ruta = str(tmp_path / "no_existe.db")
    assert mki_backup._snapshot_sellado(MARTES_29_SEP, ruta) is False
    assert not os.path.exists(ruta)
    assert os.listdir(tmp_path) == []
    salida = capsys.readouterr().out
    assert "no existe" in salida and "no_existe.db" in salida


def test_sellado_contra_una_base_sin_la_tabla(tmp_path, capsys):
    ruta = _crear_base(tmp_path, con_tabla=False)
    assert mki_backup._snapshot_sellado(MARTES_29_SEP, ruta) is False
    salida = capsys.readouterr().out
    assert "snapshots" in salida            # sqlite nombra la tabla que falta
    # y no la creó: init_db() de senales.py sí la habría creado
    conn = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    tablas = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    conn.close()
    assert tablas == {"otra_cosa"}


def test_sellado_contra_un_archivo_que_no_es_una_base(tmp_path, capsys):
    ruta = tmp_path / "senales.db"
    ruta.write_bytes(b"esto no es sqlite " * 64)
    antes = ruta.read_bytes()
    assert mki_backup._snapshot_sellado(MARTES_29_SEP, str(ruta)) is False
    assert ruta.read_bytes() == antes
    assert "no se pudo leer" in capsys.readouterr().out


def test_la_base_se_abre_en_mode_ro_y_la_conexion_no_puede_escribir(
        tmp_path, monkeypatch):
    """Se espía la conexión que el código abre DE VERDAD: la URI lleva
    `mode=ro` y `uri=True`, y sobre esa misma conexión un DDL es rechazado
    por sqlite. No es una promesa del comentario: es la conexión."""
    ruta = _crear_base(tmp_path, ("2026-09-29",))
    connect_real = sqlite3.connect
    vistas = []

    class _Espia:
        def __init__(self, conn):
            self._conn = conn

        def execute(self, *a, **k):
            return self._conn.execute(*a, **k)

        def close(self):
            with pytest.raises(sqlite3.OperationalError, match="readonly"):
                self._conn.execute("CREATE TABLE intruso (x INTEGER)")
            vistas[-1]["rechazo_escritura"] = True
            self._conn.close()

    def espia(*args, **kwargs):
        vistas.append({"args": args, "kwargs": kwargs})
        return _Espia(connect_real(*args, **kwargs))

    monkeypatch.setattr(mki_backup.sqlite3, "connect", espia)
    assert mki_backup._snapshot_sellado(MARTES_29_SEP, ruta) is True

    assert len(vistas) == 1
    uri = vistas[0]["args"][0]
    assert uri.startswith("file:") and uri.endswith("?mode=ro"), uri
    assert vistas[0]["kwargs"].get("uri") is True
    assert vistas[0].get("rechazo_escritura") is True


def test_la_lectura_no_deja_huella_en_disco(tmp_path):
    """Archivo y carpeta SIN permiso de escritura: igual responde, el
    archivo queda byte a byte y con el mismo mtime, y no aparece ningún
    `-journal`, `-wal` ni `-shm` al lado."""
    if os.geteuid() == 0:
        pytest.fail("este test quita permisos de escritura y como root no "
                    "prueba nada; se corre como usuario normal")
    carpeta = tmp_path / "solo_lectura"
    carpeta.mkdir()
    ruta = _crear_base(carpeta, ("2026-09-29",))
    contenido = open(ruta, "rb").read()
    mtime = os.stat(ruta).st_mtime_ns
    os.chmod(ruta, 0o444)
    os.chmod(carpeta, 0o555)
    try:
        assert mki_backup._snapshot_sellado(MARTES_29_SEP, ruta) is True
        assert mki_backup._snapshot_sellado(LUNES_28_SEP, ruta) is False
        assert sorted(os.listdir(carpeta)) == ["senales.db"]
        assert os.stat(ruta).st_mtime_ns == mtime
        assert open(ruta, "rb").read() == contenido
    finally:
        os.chmod(carpeta, 0o755)
        os.chmod(ruta, 0o644)


def test_una_ruta_con_caracteres_de_uri_se_lee_igual(tmp_path):
    """Espacio, `#`, `?` y `%` en la ruta (un Mac con «Mis Proyectos»): sin
    escapar, `?` cortaría la ruta y `mode=ro` apuntaría a otro archivo."""
    carpeta = tmp_path / "Mis Proyectos #1 ¿50%?"
    carpeta.mkdir()
    ruta = _crear_base(carpeta, ("2026-09-29",))
    assert mki_backup._snapshot_sellado(MARTES_29_SEP, ruta) is True
    assert sorted(os.listdir(carpeta)) == ["senales.db"]


def test_la_ruta_de_la_base_sigue_a_DIRECTORIO(monkeypatch, tmp_path):
    """La ruta se arma al usarla, no al importar: los tests que mueven
    `DIRECTORIO` a una carpeta temporal (tests/test_sombra.py) no abren
    nunca la base real."""
    monkeypatch.setattr(mki_backup, "DIRECTORIO", str(tmp_path))
    assert mki_backup._ruta_db() == os.path.join(str(tmp_path), "senales.db")


# ------------------------------------------------------------
# D. `_snapshot_vivo`: pgrep, con techo de tiempo y sin levantar jamás
# ------------------------------------------------------------
def test_vivo_usa_pgrep_f_con_timeout_de_10_s(monkeypatch):
    vistas = []

    class Salida:
        stdout = "4321\n"

    def falso(cmd, **kwargs):
        vistas.append((cmd, kwargs))
        return Salida()

    monkeypatch.setattr(mki_backup.subprocess, "run", falso)
    assert mki_backup._snapshot_vivo() is True
    assert vistas[0][0] == ["pgrep", "-f", "snapshot.py"]
    assert vistas[0][1].get("timeout") == 10


def test_vivo_sin_proceso_es_false(monkeypatch):
    class Salida:
        stdout = "\n"
    monkeypatch.setattr(mki_backup.subprocess, "run", lambda *a, **k: Salida())
    assert mki_backup._snapshot_vivo() is False


@pytest.mark.parametrize("excepcion", [
    FileNotFoundError("pgrep"),
    subprocess.TimeoutExpired(cmd="pgrep", timeout=10),
    PermissionError("pgrep"),
    RuntimeError("cualquier otra cosa"),
])
def test_vivo_ante_cualquier_excepcion_es_false(monkeypatch, excepcion):
    def explota(*a, **k):
        raise excepcion
    monkeypatch.setattr(mki_backup.subprocess, "run", explota)
    assert mki_backup._snapshot_vivo() is False


# ------------------------------------------------------------
# E. `main()`: negarse no toca git; commitear no cambia de forma
# ------------------------------------------------------------
@pytest.mark.parametrize("ahora,vivo,rama", [
    (_a_las(LUNES_28_SEP, 14, 42), False, "rama 3"),
    (_a_las(LUNES_28_SEP, 14, 42), True, "rama 3 con proceso vivo"),
    (_a_las(MARTES_29_SEP, 18, 14, 59), False, "rama 3, borde"),
    (_a_las(MARTES_29_SEP, 18, 15, 0), True, "rama 4, borde"),
    (_a_las(MARTES_29_SEP, 18, 40), True, "rama 4"),
    (_a_las(FERIADO_NYSE, 14, 42), False, "rama 3 en feriado de NYSE"),
])
def test_negarse_no_llama_a_git_NI_UNA_VEZ(titular, monkeypatch, tmp_path,
                                           capsys, ahora, vivo, rama):
    """Ni `add` (no se toca el índice: el árbol de trabajo es el código
    que los timers ejecutan), ni `diff`, ni `commit`. Y sale con 0: el
    vigía de las 19:00 es el que alerta si el día termina sin commit."""
    llamadas = []
    monkeypatch.setattr(
        mki_backup, "_git",
        lambda *a: llamadas.append(a) or pytest.fail(f"git al negarse ({rama}): {a}"))
    _montar(monkeypatch, tmp_path, ahora, selladas=("2026-09-25",), vivo=vivo)

    assert mki_backup.main() == 0

    assert llamadas == [], rama
    salida = capsys.readouterr().out
    assert "  NO SE COMMITEA" in salida, rama
    assert "commit creado" not in salida


def test_negarse_tampoco_toca_git_si_falta_la_base(titular, monkeypatch,
                                                  tmp_path, capsys):
    """Base inexistente = no sellado. Antes de las 18:15 se niega y el log
    dice las dos cosas: por qué no hay sello y por qué no commitea."""
    llamadas = []
    monkeypatch.setattr(mki_backup, "_git",
                        lambda *a: llamadas.append(a) or pytest.fail("git"))
    _montar(monkeypatch, tmp_path, _a_las(LUNES_28_SEP, 14, 42), con_base=False)
    assert mki_backup.main() == 0
    assert llamadas == []
    salida = capsys.readouterr().out
    assert "no existe" in salida and "NO SE COMMITEA" in salida
    assert not os.path.exists(tmp_path / "senales.db")


def test_caso_normal_18_40_sellado_commitea_con_el_mensaje_de_siempre(
        titular, git_espia, monkeypatch, tmp_path, capsys):
    _montar(monkeypatch, tmp_path, _a_las(MARTES_29_SEP, 18, 40),
            selladas=("2026-09-28", "2026-09-29"))

    assert mki_backup.main() == 0

    assert git_espia == [
        ("add", "--", "data/backups"),
        ("diff", "--cached", "--quiet", "--", "data/backups"),
        ("commit", "-m", "Backup diario 2026-09-29", "--", "data/backups"),
    ]
    salida = capsys.readouterr().out
    assert "commit creado: Backup diario 2026-09-29" in salida
    assert "DÍA SIN SELLO" not in salida
    assert "NO SE COMMITEA" not in salida


def test_caso_normal_sin_cambios_no_commitea_pero_si_mira(
        titular, monkeypatch, tmp_path, capsys):
    """El camino de siempre sigue igual cuando data/backups no cambió."""
    llamadas = []
    monkeypatch.setattr(mki_backup, "_git",
                        lambda *a: llamadas.append(a) or _R(0))
    _montar(monkeypatch, tmp_path, _a_las(MARTES_29_SEP, 18, 40),
            selladas=("2026-09-29",))
    assert mki_backup.main() == 0
    assert [ll[0] for ll in llamadas] == ["add", "diff"]
    assert "nada que commitear" in capsys.readouterr().out


def test_rama5_dia_sin_sello_commitea_y_el_log_lo_dice_con_prefijo(
        titular, git_espia, monkeypatch, tmp_path, capsys):
    _montar(monkeypatch, tmp_path, _a_las(MARTES_29_SEP, 18, 40),
            selladas=("2026-09-25", "2026-09-28"), vivo=False)

    assert mki_backup.main() == 0

    assert [ll[0] for ll in git_espia] == ["add", "diff", "commit"]
    assert git_espia[-1] == ("commit", "-m", "Backup diario 2026-09-29",
                             "--", "data/backups")
    lineas = capsys.readouterr().out.splitlines()
    marcadas = [l for l in lineas if l.startswith("  DÍA SIN SELLO:")]
    assert len(marcadas) == 1, lineas
    assert "NO contiene el sello" in marcadas[0]


def test_rama5_con_la_constante_en_false_main_se_niega(
        titular, monkeypatch, tmp_path, capsys):
    """Opción A de la tarjeta, de punta a punta."""
    llamadas = []
    monkeypatch.setattr(mki_backup, "_git",
                        lambda *a: llamadas.append(a) or pytest.fail("git"))
    monkeypatch.setattr(mki_backup, "COMMITEAR_DIA_SIN_SELLO", False)
    _montar(monkeypatch, tmp_path, _a_las(MARTES_29_SEP, 18, 40),
            selladas=("2026-09-28",), vivo=False)
    assert mki_backup.main() == 0
    assert llamadas == []
    assert "  NO SE COMMITEA" in capsys.readouterr().out


@pytest.mark.parametrize("fecha", [SABADO, DOMINGO])
def test_fin_de_semana_main_commitea_sin_snapshot(titular, git_espia,
                                                  monkeypatch, tmp_path,
                                                  capsys, fecha):
    _montar(monkeypatch, tmp_path, _a_las(fecha, 10, 0),
            selladas=("2026-10-02",))
    assert mki_backup.main() == 0
    assert [ll[0] for ll in git_espia] == ["add", "diff", "commit"]
    assert git_espia[-1][2] == f"Backup diario {fecha.isoformat()}"
    salida = capsys.readouterr().out
    assert "fin de semana" in salida
    assert "DÍA SIN SELLO" not in salida


def test_el_mensaje_y_la_decision_salen_del_mismo_reloj(
        titular, git_espia, monkeypatch, tmp_path):
    """Una sola lectura del reloj por corrida: la fecha que se busca en
    `snapshots` y la del mensaje del commit no pueden ser distintas (un
    backup que cruza la medianoche entre las dos lecturas nombraría un día
    y habría mirado el sello de otro)."""
    lecturas = []

    def reloj():
        lecturas.append(1)
        return _a_las(MARTES_29_SEP, 18, 40)

    _montar(monkeypatch, tmp_path, None, selladas=("2026-09-29",))
    monkeypatch.setattr(mki_backup, "_ahora_local", reloj)
    consultadas = []
    sellado_real = mki_backup._snapshot_sellado
    monkeypatch.setattr(
        mki_backup, "_snapshot_sellado",
        lambda f, r: consultadas.append(f) or sellado_real(f, r))

    assert mki_backup.main() == 0

    assert len(lecturas) == 1
    assert consultadas == [MARTES_29_SEP]
    assert git_espia[-1][2] == "Backup diario 2026-09-29"


def test_el_log_registra_las_tres_entradas_de_la_decision(
        titular, git_espia, monkeypatch, tmp_path, capsys):
    """«Y lo registra en su log» (§90.8): quien lea data/backup.log puede
    rehacer la decisión a mano."""
    _montar(monkeypatch, tmp_path, _a_las(LUNES_28_SEP, 14, 42),
            selladas=("2026-09-25",), vivo=True)
    mki_backup.main()
    salida = capsys.readouterr().out
    assert "2026-09-28" in salida and "lunes" in salida and "14:42" in salida
    assert "sellado: no" in salida
    assert "snapshot.py vivo: sí" in salida


# ------------------------------------------------------------
# F. La sombra sigue ganándole a todo
# ------------------------------------------------------------
@pytest.mark.parametrize("ahora", [
    _a_las(LUNES_28_SEP, 14, 42), _a_las(MARTES_29_SEP, 18, 40),
    _a_las(SABADO, 10, 0)])
def test_sombra_devuelve_antes_de_decidir_nada(monkeypatch, tmp_path, capsys,
                                               ahora):
    """En sombra `main()` sale ANTES de la decisión: no lee el reloj, no
    abre la base, no corre pgrep y no toca git — ni siquiera con el
    snapshot de hoy sellado, que en titular commitearía."""
    monkeypatch.setenv("MKI_MODO", "sombra")
    monkeypatch.setattr(mki_backup, "DIRECTORIO", str(tmp_path))
    os.makedirs(tmp_path / "data", exist_ok=True)
    _crear_base(tmp_path, (ahora.date().isoformat(),))
    tocados = []

    def dinamita(nombre):
        def f(*a, **k):
            tocados.append(nombre)
            raise AssertionError(f"en sombra se llamó a {nombre}")
        return f

    for nombre in ("_git", "_ahora_local", "_snapshot_sellado",
                   "_snapshot_vivo", "decidir_commit"):
        monkeypatch.setattr(mki_backup, nombre, dinamita(nombre))

    assert mki_backup.main() == 0

    assert tocados == []
    assert "modo sombra: NO se commitea" in capsys.readouterr().out


def test_mki_modo_ilegible_tampoco_commitea(monkeypatch, tmp_path):
    """Un typo cae a sombra (modo.py) y por lo tanto tampoco decide nada."""
    monkeypatch.setenv("MKI_MODO", "sombrra")
    llamadas = []
    monkeypatch.setattr(mki_backup, "_git",
                        lambda *a: llamadas.append(a) or pytest.fail("git"))
    _montar(monkeypatch, tmp_path, _a_las(MARTES_29_SEP, 18, 40),
            selladas=("2026-09-29",))
    assert mki_backup.main() == 0
    assert llamadas == []


# ------------------------------------------------------------
# G. La constante contra las plantillas de los timers
# ------------------------------------------------------------
def _on_calendar(nombre: str) -> tuple:
    """(días, hora, zona) del `OnCalendar=` de una plantilla de systemd.
    Sólo sabe leer «Mon..Fri HH:MM[:SS] Zona»; ante cualquier otra forma
    FALLA con un mensaje que dice qué hacer — no se salta."""
    ruta = os.path.join(RAIZ, "systemd", nombre)
    assert os.path.exists(ruta), (
        f"no existe la plantilla {ruta}: HORA_SNAPSHOT_LOCAL ya no tiene "
        "contra qué verificarse")
    with open(ruta, encoding="utf-8") as f:
        lineas = [l.strip() for l in f if l.strip().startswith("OnCalendar=")]
    assert len(lineas) == 1, (
        f"{nombre}: se esperaba UNA línea OnCalendar= y hay {len(lineas)} "
        f"({lineas}). Con más de un disparo diario, una sola hora en "
        "mki_backup.HORA_SNAPSHOT_LOCAL deja de describir al timer")
    m = re.fullmatch(
        r"OnCalendar=(\S+)\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s+(\S+)", lineas[0])
    assert m, (
        f"{nombre}: formato de OnCalendar no reconocido: {lineas[0]!r}. "
        "Este test sabe leer «Mon..Fri HH:MM Zona». Si la plantilla cambió "
        "de forma, hay que enseñarle la nueva Y revisar a mano "
        "mki_backup.HORA_SNAPSHOT_LOCAL")
    dias, h, mi, s, zona = m.groups()
    return dias, time(int(h), int(mi), int(s or 0)), zona


def test_la_hora_del_snapshot_es_la_de_la_plantilla_del_timer():
    dias, hora, zona = _on_calendar("mki-snapshot.timer")
    assert hora == mki_backup.HORA_SNAPSHOT_LOCAL, (
        f"systemd/mki-snapshot.timer dispara a las {hora} y "
        f"mki_backup.HORA_SNAPSHOT_LOCAL dice {mki_backup.HORA_SNAPSHOT_LOCAL}: "
        "si el timer cambió, la constante cambia con él")
    assert dias == "Mon..Fri", (
        f"el snapshot ya no es de lunes a viernes ({dias}): la regla de fin "
        "de semana de decidir_commit hay que volver a pensarla")
    assert zona == "America/Santiago", zona


def test_la_constante_es_un_time_sin_zona():
    assert isinstance(mki_backup.HORA_SNAPSHOT_LOCAL, time)
    assert mki_backup.HORA_SNAPSHOT_LOCAL.tzinfo is None


def test_el_backup_dispara_despues_de_la_hora_del_snapshot():
    """Si alguien adelanta el backup a antes de las 18:15, el caso normal
    pasaría a ser la rama 3 y el backup se negaría todos los días."""
    dias, hora, zona = _on_calendar("mki-backup.timer")
    assert hora > mki_backup.HORA_SNAPSHOT_LOCAL, hora
    assert dias == "Mon..Fri" and zona == "America/Santiago"


def test_el_servicio_del_backup_corre_en_hora_de_chile():
    """`_ahora_local()` lee el reloj LOCAL del proceso y lo compara con la
    hora del timer, que está declarada en hora de Chile. Coinciden porque
    la unidad fija TZ; si esa línea se va, la comparación queda a merced de
    la zona del sistema."""
    for nombre in ("mki-backup.service", "mki-snapshot.service"):
        with open(os.path.join(RAIZ, "systemd", nombre), encoding="utf-8") as f:
            texto = f.read()
        assert "Environment=TZ=America/Santiago" in texto, nombre


def test_la_plantilla_de_launchd_dice_la_misma_hora():
    """El Mac corre este mismo archivo: su plantilla tiene que coincidir."""
    ruta = os.path.join(RAIZ, "launchd", "com.mki.snapshot.plist")
    assert os.path.exists(ruta), ruta
    with open(ruta, "rb") as f:
        plist = plistlib.load(f)
    disparos = plist.get("StartCalendarInterval")
    assert isinstance(disparos, list) and disparos, (
        "com.mki.snapshot.plist: StartCalendarInterval no es la lista de "
        f"disparos que este test sabe leer ({disparos!r})")
    assert sorted(d["Weekday"] for d in disparos) == [1, 2, 3, 4, 5]
    for d in disparos:
        assert time(d["Hour"], d["Minute"]) == mki_backup.HORA_SNAPSHOT_LOCAL, d


# ------------------------------------------------------------
# H. Aislamiento: el backup no arrastra el camino de sellado
# ------------------------------------------------------------
def _importados(ruta: str) -> set:
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    out = set()
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            out |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module.split(".")[0])
    return out


def test_el_backup_no_importa_senales_ni_el_vigia():
    """`senales.ya_existe_snapshot_hoy()` llama a `init_db()` (DDL) y abre
    en escritura; `mki_vigia` trae `alertas` y la red. El backup pregunta
    por el sello con su propia consulta de una línea y su propio pgrep."""
    importados = _importados(mki_backup.__file__)
    for prohibido in ("senales", "mki_vigia", "snapshot", "motor", "alertas",
                      "noticias", "calendarios"):
        assert prohibido not in importados, prohibido
    assert importados <= {"os", "sqlite3", "subprocess", "sys", "datetime",
                          "urllib", "registro", "modo"}, importados


def test_el_backup_jamas_publica():
    """Publicar es un acto manual de Nicolás (Constitución, punto 5). En el
    archivo no existe el verbo como argumento de git."""
    fuente = open(mki_backup.__file__, encoding="utf-8").read()
    for verbo in ('"push"', "'push'", '"pull"', "'pull'"):
        assert verbo not in fuente, verbo
```

---

## 2. Reproducción FALLANDO sobre HEAD, después todo en verde

`date` antes de la corrida contra HEAD: **Tue Sep 29 22:32:49 -03 2026** (`mki_backup.py` sin modificar, `git diff --stat` vacío, HEAD 2f73eb2). Salida guardada en `scratchpad/b4_repro_en_HEAD.txt`:

```
F                                                                        [100%]
__________ test_reproduccion_28_sep_despertar_a_las_14_42_no_commitea __________
git_espia = [('add', '--', 'data/backups'), ('diff', '--cached', '--quiet', '--', 'data/backups'),
             ('commit', '-m', 'Backup diario 2026-09-29', '--', 'data/backups')]
>       assert git_espia == [], (...)
E       AssertionError: el backup tocó git antes de que el día se sellara (el defecto del
        28-sep-2026, acta §90.8): [('add', ...), ('diff', ...), ('commit', '-m', 'Backup diario 2026-09-29', ...)]
E         Left contains 3 more items, first extra item: ('add', '--', 'data/backups')
----------------------------- Captured stdout call -----------------------------
[2026-09-30T01:32:50.212913+00:00] mki_backup.py
  modo: TITULAR — Telegram y commits activos
  commit creado: Backup diario 2026-09-29
FAILED tests/test_backup_orden.py::test_reproduccion_28_sep_despertar_a_las_14_42_no_commitea
1 failed in 0.09s
```

Falla por la razón correcta: HEAD hace add + diff + commit con reloj inyectado a las 14:42 sin sello (y, de paso, nombra el commit con `date.today()` real, ignorando el reloj).

Después del cambio: `date` **22:33:47** → `tests/test_backup_orden.py`: **83 passed in 0.13s**. Última corrida (con las ediciones de comentarios): `date` **23:02:51** → `test_backup_orden.py` + `test_sombra.py`: **120 passed** (83 + 37). El archivo tiene 49 funciones de test, 83 casos con parametrización. El mismo archivo corrido con `TZ=Pacific/Honolulu` y `TZ=Pacific/Kiritimati` (reloj del proceso en otro día/hora): 83 passed las dos veces — el archivo no depende del reloj real.

**Contraprueba por mutantes** (script `scratchpad/b4_mutantes.py`, sobre COPIAS en el scratchpad, sin git): 14 de 14 mutantes muertos — sin `mode=ro` (1 rojo: el test espía de la conexión; el test de permisos NO lo mata porque sqlite cae solo a lectura ante archivo no escribible), constante 18:40 (7), `<=` en el borde (2), fin de semana no commitea (14), `git add` antes de decidir (14), sombra ya no gana (4), mensaje con otro reloj (2), ruta sin `quote` (1), rama 4 ignora el proceso (3), sello siempre True (13), pgrep fallido = vivo (4), rama 5 sin prefijo (4), negarse con salida 1 (9), `import senales` (1).

**Ensayo en seco con reloj real** (`scratchpad/b4_ensayo_en_seco.py`, `_git` espiado, COPIA de la base del worktree en `mode=ro`, 22:38): `_snapshot_sellado(2026-09-07)` = True (confirma el sello en Labor Day), 2026-09-25 (viernes) = False, 2026-09-28 = True, 2026-09-29 = True; `_snapshot_vivo()` real = False; `main()` escribió en el log `fecha local 2026-09-29 (martes) 22:38:27 · snapshot de hoy sellado: sí · snapshot.py vivo: no` / `snapshot de hoy sellado: se commitea` / `commit creado: Backup diario 2026-09-29`; la base quedó con el mismo mtime y tamaño y sin `-journal`/`-wal` al lado. `journal_mode` de la base: `delete`.

Verificado además (lectura de archivo, sin systemctl): las unidades INSTALADAS en `~/.config/systemd/user/` dicen `OnCalendar=Mon..Fri 18:15 America/Santiago` (snapshot) y `18:40` (backup), igual que las plantillas; el único `ExecStart` con `snapshot.py` en su línea de comando es el del snapshot.

---

## 3. Tests vecinos

Corrida final, `date` **23:03:00 → 23:04:34**, `-m "not red"` (0 deseleccionados: ninguno de estos archivos marca red):
`tests/test_backup_orden.py tests/test_sombra.py tests/test_autonomia.py tests/test_vigia.py tests/test_secuencial_07.py tests/test_fuente_canonica.py tests/test_insumos.py tests/test_sonda_cierre.py tests/test_corredor.py tests/test_dinero.py tests/test_control_lineal.py tests/test_gemelo_datos.py` → **316 passed, 1 warning** (starlette, ajeno).

Nota: la primera corrida de vecinos (22:35) tuvo **1 rojo ajeno**: `tests/test_control_lineal.py::test_el_camino_de_sellado_no_importa_GEMELO`, porque `snapshot.py` (bloque de otro agente) contenía la cadena «GEMELO/datos.py:57-59» en un comentario (línea 157) y ese test hace `"GEMELO" not in fuente` sobre `snapshot.py`, `senales.py`, …, `mki_backup.py`. A las 23:03 ya no estaba (0 ocurrencias): lo corrigió su dueño. `mki_backup.py` nunca tuvo la cadena; tampoco tiene la palabra prohibida, ni el test.

**Un vecino que va a ponerse rojo según la hora, y que NO puedo tocar:** `tests/test_sombra.py::test_backup_de_titular_si_intenta_commitear` (línea 127) parchea `_git` y `DIRECTORIO` y espera `llamadas[0][0] == "add"` con el reloj REAL. Con el cambio, en `tmp_path` no hay base → «no sellado» → la decisión depende de la hora: lunes a viernes antes de las 18:15 se niega (rojo); desde las 18:15 con un `snapshot.py` vivo (pgrep real, sin parchear) se niega (rojo); el resto del tiempo commitea (verde). Lo demostré sin tocar el archivo: `TZ=Pacific/Honolulu` (martes 15:37 para el proceso) → **FAILED** con el log `NO SE COMMITEA: martes sin snapshot sellado y son las 15:37, antes de las 18:15…`; con el reloj de Chile (22:4x) → passed. **Parche de tres líneas** (probado en una copia del test en el scratchpad, verde bajo Honolulu), para quien lleve `test_sombra.py`, a insertar después de `monkeypatch.setattr(mki_backup, "DIRECTORIO", str(tmp_path))`:

```python
    # 5.1.0 / §90.8: el caso normal de las 18:40, para que el test no dependa del reloj
    monkeypatch.setattr(mki_backup, "_ahora_local", lambda: datetime(2026, 9, 29, 18, 40))
    monkeypatch.setattr(mki_backup, "_snapshot_sellado", lambda fecha, ruta: True)
    monkeypatch.setattr(mki_backup, "_snapshot_vivo", lambda: False)
```
(y `from datetime import date, datetime` en la cabecera). Hasta que se aplique, la suite corrida un día hábil antes de las 18:15 —el hook de pre-commit, por ejemplo— tendrá ese rojo.

---

## 4. Texto para la tarjeta (rama 5)

**Contexto.** Firmado (§90.8): el backup se niega si el snapshot del día no está sellado. Lo que el acta no dice: qué hacer un día de semana en que, pasadas las 18:15, no hay sello ni `snapshot.py` vivo. Las otras cuatro ramas no están en discusión.

**Opción A — negarse siempre que no haya sello en día de semana.** El backup sólo commitea en fin de semana o con el sello de hoy en la base. Se gana: ningún «Backup diario D» existe sin el sello de D; el nombre siempre describe el contenido, que es la queja literal de §64; y no hay carrera (abajo). Se pierde: un día de semana sin sello queda sin commit hasta el próximo día sellado, y los CSV que sí cambiaron ese día (verificaciones de las 18:15, `sello_dinero.csv` de las 00:30) esperan 24 h o más sin copia versionada, en una máquina sin réplica.

**Opción B — la implementada (`COMMITEAR_DIA_SIN_SELLO = True`).** Commitea igual y el log local dice «DÍA SIN SELLO: … este commit NO contiene el sello de hoy». Se gana: los CSV del día quedan versionados el mismo día. Se pierde: (i) el mensaje del commit no cambia (así lo pide el diseño), de modo que en la historia publicada ese commit es indistinguible de uno normal; la marca vive sólo en `data/backup.log`, que no se versiona; (ii) «sin proceso vivo» es un `pgrep` en un instante: si el sello llega más tarde —un `snapshot.py --origen manual` esa noche, el fallback del dashboard, o un despertar simultáneo después de las 18:15 en que el backup mira antes de que systemd haya lanzado el snapshot— el commit precede al sello, que es el defecto del 28-sep otra vez, ahora sólo después de las 18:15.

**Lo que el dato sostiene** (copia de `senales.db` del worktree, 4-jul a 29-sep, 62 días de semana): 4 días sin ninguna fila en `snapshots` (6, 7 y 10-jul; 25-sep) — en el 25-sep la máquina estaba suspendida y el backup tampoco corrió; 6 días con sello emitido después de las 18:40 (29 y 31-jul, 3, 5, 10 y 21-ago; piso: el 6-ago se confirmó a las ~19:08 y `creado_en` no lo captura), todos de la era del Mac. En esos 6 la rama 4 (proceso vivo) niega bajo A y bajo B por igual; A y B sólo difieren en los días sin sello y sin proceso, y en la carrera del despertar, que no medí. No hay dato para decir cuál de los dos costos pesa más.

---

## 5. Defectos del diseño y lo que no pude verificar

1. **`test_sombra.py::test_backup_de_titular_si_intenta_commitear` queda atado al reloj** (sección 3). Es la única regresión conocida y el parche está arriba.
2. **La rama 2 mira la fila de `snapshots`, pero lo que se commitea son los CSV, que `snapshot.py` exporta DESPUÉS del sello** (`main()` de HEAD: sello → `_epilogo_vigia` → `verificar_pendientes` → `respaldar_a_csv`). El 28-sep: emisión 14:42:58, proceso terminado 14:43:30 — 32 s en que «sellado = sí» y los CSV aún viejos. En un despertar simultáneo que caiga en esa ventana, la rama 2 commitea CSV sin el sello y el log dice «sellado: se commitea». Lo implementé tal cual el diseño (rama 2 ignora `snapshot_vivo`); la corrección obvia es que la rama 2 exija además `not snapshot_vivo`, o que se compare el mtime de `data/backups/snapshots.csv` con `creado_en`. No medido en producción.
3. **La rama 1 ignora `snapshot_vivo`.** Un despertar en sábado, con `Persistent=true` recuperando los timers del viernes, dispara los ocho juntos y el backup commitea de inmediato haga lo que haga el snapshot (que además sellaría con `fecha` = sábado; eso es de §61/§62, no mío). Está fijado en un test con esa consecuencia declarada en el docstring.
4. **La rama 4 no reintenta.** El timer dispara una vez: un sello tardío (19:10) deja el día sin commit; el vigía de las 19:00 dice «backup: sin commit hoy» y la retractación de las 20:30 cubre sólo al snapshot (`enviar_retractacion_si_corresponde` lee `info_snapshot_hoy`, no el backup). Bajo HEAD esos días recibían un commit a las 18:40 sin el sello (el defecto §64); ahora no reciben ninguno hasta el día siguiente. Lo comparten A y B.
5. **`pgrep -f snapshot.py`** da falsos positivos (cualquier proceso con esa cadena en su línea de comando: un editor, un `git diff -- snapshot.py`, la shell de un agente corriendo tests que lo nombren) → a las 18:40 el backup se niega (rama 4): conservador y visible por el vigía. Da falsos negativos: el fallback del dashboard sella dentro del proceso de Streamlit/API y pgrep no lo ve; y ante excepción de `subprocess` devuelve `False` (diseño), es decir «no vivo» → rama 5 commitea: es la dirección MENOS conservadora, la contraria a la filosofía de `modo.py`. Mi `date`/`pgrep` reales lo probaron sólo en este PC.
6. **Zona horaria.** `_ahora_local()` es el reloj local del proceso y se compara con 18:15 de Chile: coincide porque las unidades fijan `TZ=America/Santiago` (test contra la plantilla) y launchd usa la zona del sistema del Mac. Un `python mki_backup.py` a mano desde una shell con otra TZ decide con ESA hora. No verificado en el Mac (ni `pgrep` bajo launchd).
7. **`mode=ro` sobre `journal_mode=delete`**: si `snapshot.py` tiene el lock de escritura en ese instante, la lectura espera hasta 5 s (timeout por defecto de sqlite3) y falla → «NO sellado» → con proceso vivo, se niega: correcto por construcción. Un journal caliente tras un crash también cuenta como no sellado.
8. Un sello fuera de hora (como el 28-sep 14:42:58, que bajo §90.1 b ya no debería ocurrir) cuenta como «sellado» y el backup commitea a cualquier hora posterior; es coherente con «orden», no con «hora».
9. No verificado: la carrera del punto 2 y la de la rama 5 bajo systemd real (nada de systemd, por regla); el comportamiento en un despertar real; `TimeoutStartSec=120` del backup alcanza (pgrep 10 s + sqlite 5 s).

Archivos: `$WT/mki_backup.py`, `$WT/tests/test_backup_orden.py`. Evidencias en el scratchpad: `b4_repro_en_HEAD.txt`, `b4_verde.txt`, `b4_mutantes.txt`, `b4_vecinos.txt`, `b4_vecinos_final.txt`, `b4_sombra_reloj.txt`, `b4_ensayo_en_seco.txt`, `b4_frecuencias.txt`, `b4_sombra_parche/test_parche_propuesto_sombra.py`.