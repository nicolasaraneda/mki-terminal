# ============================================================
# Parche de snapshot.py:140 como parche NO aplicado (corrida 09, frente 2b).
#
# El defecto: `ejecutar_snapshot` calcula `sesion_objetivo` con
# `calendarios.proxima_sesion_despues_de(exchange, ahora_utc)` — el reloj de
# pared del proceso — en vez de con `available_at` (cierre UTC de la sesión
# del SOX usada). Cuando el sello se atrasa y cruza medianoche/01h UTC, la
# asiática ya abrió y la fila apunta a la sesión SIGUIENTE.
#
# El parche vive en GEMELO/propuestas/parches/snapshot140.diff y NO está
# aplicado: snapshot.py es intocable. Este archivo prueba el parche sin
# tocarlo: copia snapshot.py a un directorio temporal, aplica el .diff sobre
# la copia (con `patch`; si no hay `patch`, por texto) y la importa con
# importlib bajo otro nombre de módulo (`snapshot_parcheado`). El original y
# la copia comparten `motor`, `senales`, `noticias` y `calendarios` (los
# mismos objetos de módulo), así que un monkeypatch sobre `motor.*` los
# controla a ambos por igual.
#
# Enfoque, y por qué éste: se ejecuta `ejecutar_snapshot` ENTERA (no una
# expresión extraída), porque lo que hay que fijar es que la línea que
# decide `sesion_objetivo` reciba `available_at` con el valor que la propia
# función calcula en :123-135 — extraer la expresión probaría el calendario,
# no el parche. Para que eso sea seguro:
#   · `senales.DB_PATH` apunta a una base temporal ANTES de cada llamada, y
#     un guardia lo verifica (nunca se escribe en senales.db real);
#   · el motor está enteramente reemplazado (sin red): puntaje_v0_al,
#     regimen_al, roca_chip_al, divergencias_al y prediccion_apertura_al
#     devuelven valores fijos; `salud_descarga` se reemplaza en los dos
#     módulos;
#   · el reloj de pared se controla sustituyendo `datetime` en el módulo
#     bajo prueba por una subclase cuyo `now()` es fijo (`date.today()` no se
#     toca: sólo decide la fecha de la fila, irrelevante aquí);
#   · `calendarios` es el REAL: no hay monkeypatch sobre él. Los valores
#     esperados se leen del calendario y además se fijan como literal.
#
# Los tests quedan en VERDE con snapshot.py sin parchear, que es su estado
# hoy. Si un día el parche se aplica, la contraprueba (que reproduce el
# defecto en el original) pierde su sujeto y se salta con ese motivo, igual
# que hace tests/test_hooks_propuestos.py con los hooks instalados.
#
# Cero intentos del DSR: no se evalúa ninguna hipótesis sobre retornos.
# ============================================================

import importlib.util
import os
import shutil
import subprocess
import sys
from datetime import datetime

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import calendarios  # noqa: E402  (real, sin monkeypatch)
import motor  # noqa: E402
import noticias  # noqa: E402
import senales  # noqa: E402
import snapshot  # noqa: E402

ORIGINAL = os.path.join(RAIZ, "snapshot.py")
DIFF = os.path.join(RAIZ, "GEMELO", "propuestas", "parches", "snapshot140.diff")

EXPRESION_VIEJA = "calendarios.proxima_sesion_despues_de(exchange, ahora_utc)"
EXPRESION_NUEVA = "exchange, datetime.fromisoformat(available_at))"


def _fuente_original() -> str:
    return open(ORIGINAL, encoding="utf-8").read()


# True mientras snapshot.py siga sin parchear (estado esperado hoy).
PARCHE_PENDIENTE = EXPRESION_VIEJA in _fuente_original()

# Tickers de los cinco exchanges del universo: los tres asiáticos son los
# que el defecto mueve; XETR y XNYS abren después de la 01:30 UTC y sirven
# de control de que el parche no toca lo que ya estaba bien.
TICKERS = ["005930.KS", "2330.TW", "8035.T", "IFX.DE", "NVDA"]
ASIATICOS = ["005930.KS", "2330.TW", "8035.T"]


# ------------------------------------------------------------
# Aplicar el parche sobre una COPIA
# ------------------------------------------------------------
def _aplicar_por_texto(ruta: str) -> None:
    """Fallback si no hay `patch`: el mismo cambio de una expresión."""
    fuente = open(ruta, encoding="utf-8").read()
    assert fuente.count(EXPRESION_VIEJA) == 1
    fuente = fuente.replace(
        EXPRESION_VIEJA,
        "calendarios.proxima_sesion_despues_de(\n"
        "                    exchange, datetime.fromisoformat(available_at))")
    open(ruta, "w", encoding="utf-8").write(fuente)


def _copia_parcheada(directorio) -> str:
    """Copia snapshot.py a `directorio` y aplica el .diff sobre la copia.
    Devuelve la ruta de la copia. El archivo real no se toca."""
    destino = os.path.join(str(directorio), "snapshot.py")
    shutil.copyfile(ORIGINAL, destino)
    if not PARCHE_PENDIENTE:
        return destino  # ya está aplicado en el original: la copia lo hereda
    if shutil.which("patch"):
        p = subprocess.run(["patch", "-p1", "--forward", "-i", DIFF],
                           cwd=str(directorio), capture_output=True, text=True)
        assert p.returncode == 0, f"patch falló:\n{p.stdout}\n{p.stderr}"
    else:
        _aplicar_por_texto(destino)
    fuente = open(destino, encoding="utf-8").read()
    assert EXPRESION_NUEVA in fuente and EXPRESION_VIEJA not in fuente
    return destino


def _importar(ruta: str, nombre: str):
    """Importa un archivo .py bajo un nombre de módulo propio."""
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = modulo
    spec.loader.exec_module(modulo)
    return modulo


# ------------------------------------------------------------
# Entorno controlado: motor fijo, DB temporal, reloj de pared fijo
# ------------------------------------------------------------
class _RelojFalso(datetime):
    """`datetime.now()` fijo dentro del módulo bajo prueba. Es subclase de
    datetime, así que `fromisoformat` y `pd.Timestamp` siguen funcionando."""
    _instante = None

    @classmethod
    def now(cls, tz=None):
        return cls._instante if tz else cls._instante.replace(tzinfo=None)


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    monkeypatch.setattr(noticias, "sentimiento_promedio_por_ticker", lambda: {})
    monkeypatch.setattr(motor, "puntaje_v0_al",
                        lambda fecha: pd.DataFrame(
                            {"Ticker": TICKERS, "Puntaje v0": [0.1] * len(TICKERS)}))
    monkeypatch.setattr(motor, "regimen_al", lambda fecha: {"etiqueta": "test"})
    monkeypatch.setattr(motor, "roca_chip_al", lambda fecha: {"valor": 50.0})
    monkeypatch.setattr(motor, "divergencias_al", lambda fecha: [])
    sin_red = lambda fecha: {"ok_n": 1, "total": 1, "caidos": [], "completa": True}  # noqa: E731

    parcheado = _importar(_copia_parcheada(tmp_path), "snapshot_parcheado")
    modulos = {"original": snapshot, "parcheado": parcheado}
    for m in modulos.values():
        monkeypatch.setattr(m, "salud_descarga", sin_red)

    def fijar_prediccion(sox_fecha: str):
        """El anticipador usa un SOX cuyo cierre fue `sox_fecha`: eso fija
        `available_at` por la misma vía que snapshot.py:129-135."""
        def pred(fecha, ventana=motor.VENTANA_BETAS_DEFAULT, dias_earnings=None):
            return pd.DataFrame([{
                "Ticker": t, "Apertura estimada %": -1.0, "R2": 0.3,
                "Intervalo80 pp": 2.0, "N muestra": 120, "Beta de contagio": 0.5,
                "SOX usado %": -0.8, "SOX fecha": sox_fecha} for t in TICKERS])
        monkeypatch.setattr(motor, "prediccion_apertura_al", pred)

    def sellar(version: str, reloj_utc_iso: str) -> dict:
        """Corre `ejecutar_snapshot` de la versión pedida con el reloj de
        pared fijo, contra una DB temporal propia. Devuelve
        {ticker: (sesion_objetivo, timestamp_utc, available_at)}."""
        m = modulos[version]
        _RelojFalso._instante = datetime.fromisoformat(reloj_utc_iso)
        monkeypatch.setattr(m, "datetime", _RelojFalso)
        db = str(tmp_path / f"senales_{version}.db")
        monkeypatch.setattr(senales, "DB_PATH", db)
        # Guardia: jamás contra la base real.
        assert senales.DB_PATH.startswith(str(tmp_path))
        assert os.path.abspath(senales.DB_PATH) != os.path.join(RAIZ, "senales.db")
        resultado = m.ejecutar_snapshot("test")
        assert resultado["snapshot"] is True, resultado
        assert resultado["predicciones"] == len(TICKERS)
        conn = senales.get_connection()
        filas = conn.execute(
            "SELECT ticker, sesion_objetivo, timestamp_utc, available_at "
            "FROM senales_ticker WHERE sesion_objetivo IS NOT NULL").fetchall()
        conn.close()
        return {t: (s, ts, av) for t, s, ts, av in filas}

    return {"prediccion": fijar_prediccion, "sellar": sellar}


def _esperada(exchange: str, available_at: str) -> str:
    """La sesión que la fila DEBÍA apuntar, leída del calendario real."""
    return calendarios.proxima_sesion_despues_de(
        exchange, datetime.fromisoformat(available_at))[0]


# ------------------------------------------------------------
# 0. El diff aplica limpio contra el snapshot.py real (sin aplicarlo)
# ------------------------------------------------------------
@pytest.mark.skipif(not PARCHE_PENDIENTE, reason="el parche ya está aplicado en snapshot.py")
def test_el_diff_aplica_limpio_sin_tocar_el_archivo_real():
    assert os.path.exists(DIFF)
    p = subprocess.run(["git", "apply", "--check", DIFF], cwd=RAIZ,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert EXPRESION_VIEJA in _fuente_original()  # sigue sin aplicar


# ------------------------------------------------------------
# (a) Sello tardío: fijación en la copia parcheada + contraprueba en el original
# ------------------------------------------------------------
SOX_TARDIO = "2026-07-30"                   # cierre XNYS 20:00 UTC del 30-jul
RELOJ_TARDIO = "2026-07-31T01:30:00+00:00"  # el proceso sella a la 01:30 UTC


def test_fijacion_sello_tardio_apunta_a_la_sesion_de_available_at(entorno):
    """Sello a la 01:30 UTC del 31-jul con insumo conocible desde las 20:00
    UTC del 30-jul: KRX/TWSE/TSE ya abrieron su sesión del 31-jul. La copia
    parcheada debe sellar la sesión que `available_at` implica (31-jul), no
    la que el reloj de pared alcanza (3-ago)."""
    entorno["prediccion"](SOX_TARDIO)
    filas = entorno["sellar"]("parcheado", RELOJ_TARDIO)
    assert len(filas) == len(TICKERS)
    for t, (sesion, ts, available_at) in filas.items():
        assert available_at == "2026-07-30T20:00:00+00:00"
        assert ts == RELOJ_TARDIO  # timestamp_utc sigue siendo el reloj de pared
        exchange = snapshot.EXCHANGE_POR_TICKER[t]
        assert sesion == _esperada(exchange, available_at), (t, sesion)
    for t in ASIATICOS:
        assert filas[t][0] == "2026-07-31"
    assert filas["IFX.DE"][0] == "2026-07-31"
    assert filas["NVDA"][0] == "2026-07-31"


def test_fijacion_sello_tardio_la_regla_maestra_lo_deja_fuera(entorno):
    """Efecto correcto de construcción: con el ancla buena, la sesión
    elegida (31-jul, abre 00:00/01:00 UTC) ya había abierto cuando el proceso
    selló (01:30 UTC). La regla maestra del verificador la haría
    `no_verificable_timing`. Se declara aquí con el calendario real; no se
    corre el verificador (necesita red)."""
    entorno["prediccion"](SOX_TARDIO)
    filas = entorno["sellar"]("parcheado", RELOJ_TARDIO)
    for t in ASIATICOS:
        sesion, ts, _ = filas[t]
        apertura = calendarios.apertura_utc(snapshot.EXCHANGE_POR_TICKER[t], sesion)
        assert datetime.fromisoformat(ts) >= apertura, (t, ts, apertura)
    # XETR y XNYS abren después de la 01:30 UTC: siguen siendo verificables.
    for t in ["IFX.DE", "NVDA"]:
        sesion, ts, _ = filas[t]
        apertura = calendarios.apertura_utc(snapshot.EXCHANGE_POR_TICKER[t], sesion)
        assert datetime.fromisoformat(ts) < apertura


@pytest.mark.skipif(not PARCHE_PENDIENTE,
                    reason="el parche ya está aplicado: la contraprueba no tiene sujeto")
def test_contraprueba_el_original_salta_a_la_sesion_siguiente(entorno):
    """El snapshot.py real, sin parchear, reproduce el defecto: a la 01:30
    UTC del 31-jul los tres asiáticos aterrizan en 2026-08-03 (la sesión
    siguiente al 31-jul, que ya abrió), distinta de la que `available_at`
    sostiene. XETR y XNYS no se mueven porque abren más tarde ese mismo día."""
    entorno["prediccion"](SOX_TARDIO)
    filas = entorno["sellar"]("original", RELOJ_TARDIO)
    for t in ASIATICOS:
        sesion, _, available_at = filas[t]
        assert sesion == "2026-08-03", (t, sesion)
        assert sesion != _esperada(snapshot.EXCHANGE_POR_TICKER[t], available_at)
    assert filas["IFX.DE"][0] == "2026-07-31"
    assert filas["NVDA"][0] == "2026-07-31"


# ------------------------------------------------------------
# (b) Sello a tiempo: las dos versiones sellan LA MISMA sesión (no regresión)
# ------------------------------------------------------------
SOX_A_TIEMPO = "2026-09-01"                   # cierre XNYS 20:00 UTC
RELOJ_A_TIEMPO = "2026-09-01T22:15:03+00:00"  # 18:15 Chile (UTC-4), el sello real


def test_no_regresion_sello_a_tiempo_sella_lo_mismo(entorno):
    entorno["prediccion"](SOX_A_TIEMPO)
    parcheado = entorno["sellar"]("parcheado", RELOJ_A_TIEMPO)
    original = entorno["sellar"]("original", RELOJ_A_TIEMPO)
    assert set(parcheado) == set(original) == set(TICKERS)
    for t in TICKERS:
        assert parcheado[t][0] == original[t][0] == "2026-09-02", (t, parcheado[t], original[t])
        assert parcheado[t][1] == original[t][1] == RELOJ_A_TIEMPO
        assert parcheado[t][2] == original[t][2] == "2026-09-01T20:00:00+00:00"


def test_no_regresion_sin_sox_fecha_las_dos_versiones_coinciden(entorno):
    """Camino de fallback de :131-135: sin `sox_fecha`, available_at ==
    ts_emision y la expresión parcheada es idéntica a la vieja."""
    entorno["prediccion"](None)
    parcheado = entorno["sellar"]("parcheado", RELOJ_TARDIO)
    original = entorno["sellar"]("original", RELOJ_TARDIO)
    for t in TICKERS:
        assert parcheado[t] == original[t]
        assert parcheado[t][2] == RELOJ_TARDIO  # available_at cayó al reloj de pared
