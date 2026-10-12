"""Corrida 16-3, Bloque D.3 (§81.4, opción a, firmada en el acta §102.6 (4); R4
del dictamen 16-2 = R1 de la corrida 15): integridad en la dirección
ARCHIVOS → FILAS para la evidencia no verificable de E0.3.

Un par `ext_<fecha>.no_verificable.{csv,meta.json}` congelado por un proceso
que murió antes de sellar queda en `DIR_EXT` citado por nadie, indistinguible
del caso bueno. Los tests de integridad de la 15/16-2 van en la dirección
filas → archivos (lo que la base cita existe y tiene el sha); éste exige lo
recíproco: todo `.no_verificable.csv` en disco (evidencia y respaldo) está
citado por una fila de `intentos_no_verificables`. Si la base no tiene la
tabla (anterior a E0.3), cualquier `.no_verificable.csv` es huérfano por
definición. Sólo test: no toca el sellador."""
import os
import sqlite3
from datetime import datetime, timezone

import pandas as pd
import pytest

from dinero import precios
from dinero import sello_dinero as S

UTC = timezone.utc
BASE_HASTA = "2026-09-04"
SESIONES = ("2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11", "2026-09-14")
T_INTRADIA = datetime(2026, 9, 14, 17, 43, 1, tzinfo=UTC)       # 13:43 NY, bolsa abierta: timing roto


def huerfanos_no_verificables(dir_ext: str, ruta_db: str) -> list:
    """Nombres `ext_<fecha>.no_verificable.csv` presentes en `dir_ext` que
    ninguna fila de `intentos_no_verificables` cita en `insumo_ext_archivo`.
    Lee la base en `mode=ro`; sin base o sin la tabla, cita vacía."""
    en_disco = sorted(n for n in os.listdir(dir_ext) if S.es_extension_no_verificable(n)) if os.path.isdir(dir_ext) else []
    citados = set()
    if os.path.exists(ruta_db):
        con = S.conectar(ruta_db, solo_lectura=True)
        try:
            try:
                citados = {r[0] for r in con.execute(f"SELECT DISTINCT insumo_ext_archivo FROM {S.TABLA_INTENTOS}")}
            except sqlite3.OperationalError:
                citados = set()
        finally:
            con.close()
    return [n for n in en_disco if n not in citados]


@pytest.fixture(scope="module")
def base():
    return precios.cargar_congelado()


@pytest.fixture
def entorno_temporal(tmp_path, monkeypatch):
    db = str(tmp_path / "sello_dinero.db")
    monkeypatch.setattr(S, "DIR_EXT", str(tmp_path / "datos" / "sello"))
    monkeypatch.setattr(S, "RUTA_DB", db)
    monkeypatch.setattr(S, "DIR_BACKUP_EXT", str(tmp_path / "backups_ext"))
    monkeypatch.setattr(S, "RUTA_BACKUP_CSV", str(tmp_path / "sello_dinero.csv"))
    return db


def _ext(base, factor_ultima):
    ult = base.iloc[-1]
    ext = pd.DataFrame({pd.Timestamp(s): ult * 1.01 for s in SESIONES}).T
    ext.iloc[-1] = ult.values * factor_ultima
    ext.index.name = "Date"
    return ext


def test_sintetico_un_intento_sellado_no_deja_huerfano_y_un_archivo_sin_fila_si(entorno_temporal, base):
    db = entorno_temporal
    assert huerfanos_no_verificables(S.DIR_EXT, db) == []           # sin carpeta, sin base: nada
    ruta, meta = S.congelar_extension(_ext(base, 0.97), BASE_HASTA, ahora_utc=T_INTRADIA)
    assert S.es_extension_no_verificable(os.path.basename(ruta))
    # entre congelar y sellar el archivo está en disco y nadie lo cita todavía (es la
    # ventana de un proceso que muere): el detector lo ve
    assert huerfanos_no_verificables(S.DIR_EXT, db) == [os.path.basename(ruta)]
    r = S.sellar(ruta, meta, ahora_utc=T_INTRADIA, ruta_db=db)
    assert r["resultado"] == "intento_no_verificable" and r["filas_insertadas"] > 0
    assert huerfanos_no_verificables(S.DIR_EXT, db) == []           # citado por sus filas
    # `destino` explícito: el valor por defecto de `respaldar_extension` quedó ligado a la
    # carpeta real al importar el módulo, y el monkeypatch de DIR_BACKUP_EXT no lo alcanza
    # (hallazgo de esta corrida: sin esto, el test escribía en data/backups/ del árbol)
    S.respaldar_extension(ruta, destino=S.DIR_BACKUP_EXT)
    assert huerfanos_no_verificables(S.DIR_BACKUP_EXT, db) == []
    # un segundo .no_verificable.csv que ninguna fila cita (proceso muerto antes de sellar)
    huerfano = os.path.join(S.DIR_EXT, "ext_2026-09-16.no_verificable.csv")
    with open(huerfano, "wb") as f:
        f.write(b"Date,X\n2026-09-16,1\n")
    assert huerfanos_no_verificables(S.DIR_EXT, db) == ["ext_2026-09-16.no_verificable.csv"]


def test_sintetico_sin_la_tabla_todo_no_verificable_es_huerfano(tmp_path):
    """Base anterior a E0.3 (sin `intentos_no_verificables`): un
    `.no_verificable.csv` en disco no puede estar citado por nadie."""
    db = str(tmp_path / "vieja.db")
    con = sqlite3.connect(db)
    con.executescript(S._ddl_filas("sellos_dinero") + S._DDL_DIVERGENCIAS)
    con.commit(); con.close()
    carpeta = tmp_path / "ext"
    carpeta.mkdir()
    (carpeta / "ext_2026-09-28.no_verificable.csv").write_bytes(b"Date,X\n2026-09-28,1\n")
    (carpeta / "ext_2026-09-29.csv").write_bytes(b"Date,X\n2026-09-29,1\n")       # un canónico no cuenta acá
    assert huerfanos_no_verificables(str(carpeta), db) == ["ext_2026-09-28.no_verificable.csv"]


@pytest.mark.parametrize("directorio", ["DIR_EXT", "DIR_BACKUP_EXT"])
def test_integridad_en_disco_real_todo_no_verificable_esta_citado_por_una_fila(directorio):
    """Sobre la evidencia real y su respaldo versionado, en `mode=ro`. Hoy
    (antes del primer sello E0.3) la tabla no existe y no hay ningún
    `.no_verificable.csv` en disco: el test pasa vacío, y empieza a morder
    la primera vez que un disparo con timing roto congele uno."""
    carpeta = getattr(S, directorio)
    if not os.path.isdir(carpeta) and not os.path.exists(S.RUTA_DB):
        pytest.skip("sin evidencia ni base real en este checkout")
    huerfanos = huerfanos_no_verificables(carpeta, S.RUTA_DB)
    assert not huerfanos, ("PARAR Y REPORTAR (no borrar el archivo): evidencia no verificable que ninguna fila cita en "
                           f"{carpeta}: {huerfanos}")
