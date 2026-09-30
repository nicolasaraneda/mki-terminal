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


@pytest.mark.parametrize("fecha,hora,sellado", [
    (SABADO, (10, 0), False), (DOMINGO, (18, 40), False),
    (MARTES_29_SEP, (18, 40), True), (MARTES_29_SEP, (14, 42), True),
    (MARTES_29_SEP, (18, 15, 0), False), (MARTES_29_SEP, (19, 14), False),
    (FERIADO_NYSE, (18, 40), True),
])
def test_rama0_con_snapshot_vivo_nunca_se_commitea(fecha, hora, sellado):
    """La regla 0 va antes que todas: con snapshot.py vivo no se commitea,
    sea fin de semana, esté o no sellado el día. Razón (corrida 15, defecto
    2 del implementador del bloque 4): el sello se escribe ANTES de que ese
    proceso exporte los CSV a data/backups; el 28-sep pasaron 32 s entre la
    emisión (14:42:58) y el fin del proceso (14:43:30), y un backup que
    corre en esos segundos commitea CSV viejos con «sellado: sí». El
    diseño original dejaba pasar ese caso en las ramas 1 y 2; se cerró
    antes de aplicar, y por eso los tests de esas ramas se prueban con
    `snapshot_vivo=False`."""
    commitear, motivo = mki_backup.decidir_commit(
        _a_las(fecha, *hora), snapshot_sellado_hoy=sellado, snapshot_vivo=True)
    assert commitear is False
    assert motivo.startswith("NO SE COMMITEA")
    assert "snapshot.py sigue corriendo" in motivo


@pytest.mark.parametrize("hora", [(14, 42), (18, 14, 59), (18, 15), (18, 40), (23, 59)])
def test_rama2_dia_de_semana_sellado_commitea_a_cualquier_hora(hora):
    commitear, motivo = mki_backup.decidir_commit(
        _a_las(MARTES_29_SEP, *hora), snapshot_sellado_hoy=True,
        snapshot_vivo=False)
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
    """snapshot.py reintenta hasta ~60 min: el sello todavía puede ocurrir.
    (Desde la regla 0 el caso lo cubre «snapshot.py sigue corriendo».)"""
    for hora in ((18, 15, 0), (18, 40, 0), (19, 14, 0)):
        commitear, motivo = mki_backup.decidir_commit(
            _a_las(MARTES_29_SEP, *hora), snapshot_sellado_hoy=False,
            snapshot_vivo=True)
        assert commitear is False, hora
        assert motivo.startswith("NO SE COMMITEA")
        assert "corriendo" in motivo


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
