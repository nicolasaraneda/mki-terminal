# ============================================================
# El guardia de la rama del `except` (acta §82.2 c), como parche NO aplicado
# (corrida 11, bloque 5). Diff: GEMELO/propuestas/parches/guardia_ancla_temporal.diff
#
# El defecto tiene una vía de escape: en snapshot.py `available_at` arranca
# valiendo `ts_emision` y sólo se reemplaza por el cierre de NYSE dentro de
# un `try` cuyo `except` es `pass`. Si `sox_fecha` viene vacío o `cierre_utc`
# falla, el parche del §26 se comporta idéntico al defecto y no deja marca.
# Y el mismo patrón vive en senales.py (verificador): un fallo del calendario
# deja la fila pendiente para siempre en silencio.
#
# El guardia propuesto —ALERTA DEL VIGÍA más línea de log, y no una marca en
# la fila— hace visible el paso por esas ramas:
#   · snapshot.py: en el except (y en el `else` de sox_fecha vacío) imprime
#     «AVISO ancla temporal: available_at cayó al reloj de pared»;
#   · mki_vigia.py: `chequear_ancla_temporal()` lee de la base las filas de
#     hoy con available_at == timestamp_utc (o NULL) y FALLA el chequeo;
#   · senales.py: el verificador cuenta `sin_calendario` y lo devuelve.
# Por qué alerta y no marca en la fila: la evidencia ya está en la base (la
# igualdad misma), así que no hace falta una columna nueva en filas selladas
# —una columna es un cambio de esquema en el camino de sellado— y una alerta
# llega esa misma noche a quien puede actuar; un test la caza en la suite.
#
# Este archivo prueba el parche SIN aplicarlo: copia los tres archivos a un
# directorio temporal, aplica el .diff sobre las copias y las importa bajo
# otro nombre. Los originales no se tocan. Mismo enfoque que
# tests/test_parche_snapshot140.py; y se prueba además que los DOS parches
# (§26 y este) aplican juntos sobre la misma copia, porque Nicolás los
# aplica en el mismo acto.
#
# Cero intentos del DSR.
# ============================================================
import importlib.util
import os
import shutil
import subprocess
import sys
from datetime import date

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import calendarios  # noqa: E402
import mki_vigia  # noqa: E402
import motor  # noqa: E402
import noticias  # noqa: E402
import senales  # noqa: E402
import snapshot  # noqa: E402

DIFF = os.path.join(RAIZ, "GEMELO", "propuestas", "parches", "guardia_ancla_temporal.diff")
DIFF_26 = os.path.join(RAIZ, "GEMELO", "propuestas", "parches", "snapshot140.diff")
ARCHIVOS = ("snapshot.py", "senales.py", "mki_vigia.py")
MARCA = "AVISO ancla temporal"

PARCHE_PENDIENTE = MARCA not in open(os.path.join(RAIZ, "snapshot.py"), encoding="utf-8").read()
TICKERS = ["005930.KS", "2330.TW", "NVDA"]


def _copias_parcheadas(directorio) -> dict:
    for a in ARCHIVOS:
        shutil.copyfile(os.path.join(RAIZ, a), os.path.join(str(directorio), a))
    if PARCHE_PENDIENTE:
        if not shutil.which("patch"):
            pytest.skip("no hay `patch` en esta máquina")
        p = subprocess.run(["patch", "-p1", "--forward", "-i", DIFF],
                           cwd=str(directorio), capture_output=True, text=True)
        assert p.returncode == 0, f"patch falló:\n{p.stdout}\n{p.stderr}"
    return {a: os.path.join(str(directorio), a) for a in ARCHIVOS}


def _importar(ruta: str, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = modulo
    spec.loader.exec_module(modulo)
    return modulo


# ------------------------------------------------------------
# 0. Los dos parches aplican, y aplican JUNTOS
# ------------------------------------------------------------
@pytest.mark.skipif(not PARCHE_PENDIENTE, reason="el guardia ya está aplicado")
def test_el_diff_del_guardia_y_el_del_26_aplican_juntos_sobre_copias(tmp_path):
    if not shutil.which("patch"):
        pytest.skip("no hay `patch`")
    for a in ARCHIVOS:
        shutil.copyfile(os.path.join(RAIZ, a), tmp_path / a)
    for diff in (DIFF, DIFF_26):
        p = subprocess.run(["patch", "-p1", "--forward", "-i", diff],
                           cwd=str(tmp_path), capture_output=True, text=True)
        assert p.returncode == 0, f"{os.path.basename(diff)} falló:\n{p.stdout}\n{p.stderr}"
    fuente = open(tmp_path / "snapshot.py", encoding="utf-8").read()
    assert MARCA in fuente
    assert "datetime.fromisoformat(available_at))" in fuente
    # y los originales siguen intactos
    assert MARCA not in open(os.path.join(RAIZ, "snapshot.py"), encoding="utf-8").read()


# ------------------------------------------------------------
# Entorno: motor fijo, DB temporal, sin red
# ------------------------------------------------------------
@pytest.fixture
def entorno(monkeypatch, tmp_path):
    copias = _copias_parcheadas(tmp_path)
    snap_g = _importar(copias["snapshot.py"], "snapshot_guardia")
    vigia_g = _importar(copias["mki_vigia.py"], "mki_vigia_guardia")
    monkeypatch.setattr(noticias, "sentimiento_promedio_por_ticker", lambda: {})
    monkeypatch.setattr(motor, "puntaje_v0_al",
                        lambda fecha: pd.DataFrame({"Ticker": TICKERS, "Puntaje v0": [0.1] * len(TICKERS)}))
    monkeypatch.setattr(motor, "regimen_al", lambda fecha: {"etiqueta": "test"})
    monkeypatch.setattr(motor, "roca_chip_al", lambda fecha: {"valor": 50.0})
    monkeypatch.setattr(motor, "divergencias_al", lambda fecha: [])
    sin_red = lambda fecha: {"ok_n": 1, "total": 1, "caidos": [], "completa": True}  # noqa: E731
    for m in (snapshot, snap_g):
        monkeypatch.setattr(m, "salud_descarga", sin_red)
    db = str(tmp_path / "senales_guardia.db")
    monkeypatch.setattr(senales, "DB_PATH", db)
    assert senales.DB_PATH.startswith(str(tmp_path))
    assert os.path.abspath(senales.DB_PATH) != os.path.join(RAIZ, "senales.db")

    def prediccion(sox_fecha):
        def pred(fecha, ventana=motor.VENTANA_BETAS_DEFAULT, dias_earnings=None):
            return pd.DataFrame([{
                "Ticker": t, "Apertura estimada %": -1.0, "R2": 0.3,
                "Intervalo80 pp": 2.0, "N muestra": 120, "Beta de contagio": 0.5,
                "SOX usado %": -0.8, "SOX fecha": sox_fecha} for t in TICKERS])
        monkeypatch.setattr(motor, "prediccion_apertura_al", pred)

    def filas_hoy():
        conn = senales.get_connection()
        f = conn.execute("SELECT ticker, timestamp_utc, available_at FROM senales_ticker "
                         "WHERE apertura_estimada_pct IS NOT NULL").fetchall()
        conn.close()
        return f

    return {"snap": snap_g, "vigia": vigia_g, "prediccion": prediccion, "filas": filas_hoy,
            "copias": copias}


# ------------------------------------------------------------
# 1. Camino feliz: hay sox_fecha, cierre_utc funciona → sin aviso, vigía OK
# ------------------------------------------------------------
def test_camino_feliz_sin_aviso_y_vigia_en_verde(entorno, capsys):
    entorno["prediccion"]("2026-09-04")
    r = entorno["snap"].ejecutar_snapshot("test")
    assert r["snapshot"] is True and r["predicciones"] == len(TICKERS)
    assert MARCA not in capsys.readouterr().out
    filas = entorno["filas"]()
    assert all(av != ts and av is not None for _, ts, av in filas)
    ok, detalle = entorno["vigia"].chequear_ancla_temporal(date.today())
    assert ok, detalle
    assert f"{len(TICKERS)}/{len(TICKERS)}" in detalle


# ------------------------------------------------------------
# 2. cierre_utc falla → la rama del except se toma → AVISO + vigía FALLA
# ------------------------------------------------------------
def test_si_cierre_utc_falla_el_aviso_sale_y_el_vigia_falla(entorno, capsys, monkeypatch):
    entorno["prediccion"]("2026-09-04")

    def revienta(exchange, sesion):
        raise RuntimeError("calendario roto a propósito")
    monkeypatch.setattr(calendarios, "cierre_utc", revienta)
    r = entorno["snap"].ejecutar_snapshot("test")
    assert r["snapshot"] is True
    salida = capsys.readouterr().out
    assert MARCA in salida and "cierre_utc" in salida
    filas = entorno["filas"]()
    assert filas and all(av == ts for _, ts, av in filas), "el ancla quedó en reloj de pared"
    ok, detalle = entorno["vigia"].chequear_ancla_temporal(date.today())
    assert not ok
    assert f"{len(TICKERS)}/{len(TICKERS)}" in detalle and "reloj de pared" in detalle


# ------------------------------------------------------------
# 3. sox_fecha vacío → mismo destino, por el `else`
# ------------------------------------------------------------
def test_si_no_hay_sox_fecha_el_aviso_sale_igual(entorno, capsys):
    entorno["prediccion"](None)
    entorno["snap"].ejecutar_snapshot("test")
    salida = capsys.readouterr().out
    assert MARCA in salida and "sox_fecha" in salida
    ok, _ = entorno["vigia"].chequear_ancla_temporal(date.today())
    assert not ok


# ------------------------------------------------------------
# 4. Contraprueba: el ORIGINAL no avisa y el vigía original no sabe mirar
# ------------------------------------------------------------
@pytest.mark.skipif(not PARCHE_PENDIENTE, reason="el guardia ya está aplicado")
def test_contraprueba_el_original_calla(entorno, capsys, monkeypatch):
    entorno["prediccion"]("2026-09-04")

    def revienta(exchange, sesion):
        raise RuntimeError("calendario roto a propósito")
    monkeypatch.setattr(calendarios, "cierre_utc", revienta)
    snapshot.ejecutar_snapshot("test")
    assert MARCA not in capsys.readouterr().out
    assert not hasattr(mki_vigia, "chequear_ancla_temporal")


# ------------------------------------------------------------
# 5. El tercer tragador: el verificador cuenta y dice el fallo del calendario
# ------------------------------------------------------------
def test_el_verificador_cuenta_los_fallos_del_calendario(entorno, capsys, monkeypatch):
    senales_g = _importar(entorno["copias"]["senales.py"], "senales_guardia")
    monkeypatch.setattr(senales_g, "DB_PATH", senales.DB_PATH)
    entorno["prediccion"]("2026-09-04")
    entorno["snap"].ejecutar_snapshot("test")   # deja filas pendientes en la DB temporal

    def revienta(exchange, sesion):
        raise RuntimeError("calendario roto a propósito")
    monkeypatch.setattr(calendarios, "apertura_utc", revienta)
    r = senales_g.verificar_apertura_pendientes()
    assert r["sin_calendario"] == len(TICKERS), r
    assert r["verificadas"] == 0 and r["no_verificables"] == 0
    salida = capsys.readouterr().out
    assert "AVISO verificador" in salida and "queda pendiente" in salida
    # y las filas siguen pendientes: no se inventó nada
    conn = senales.get_connection()
    estados = [e for (e,) in conn.execute("SELECT estado FROM senales_ticker "
                                          "WHERE apertura_estimada_pct IS NOT NULL")]
    conn.close()
    assert estados and all(e == senales.ESTADO_PENDIENTE for e in estados)
