"""Corrida 16-3 (11-oct-2026): la fuente única de las cifras publicadas
(actas §93.4, §93.4-bis ii y §99.6).

Hasta esta corrida el reporte de Telegram, la API y el dashboard leían sus
cifras de acierto de seis consultas directas de `senales.py` que NO pasaban
por la regla de conocibilidad (acta §90.1 d): las 8 filas verificadas del
28-sep-2026, selladas con la sesión del SOX abierta, contaban en el track
record de 30 días (dictamen_15/auditor_bloque1.md, B1). Desde acá las seis
cifras salen de `backtest/linea_base.py`, que las retira.

Lo que estos tests exigen (encargo 16-3, §1 y §2.3), escritos ANTES del
código y rojos sobre HEAD por su propia aserción donde la superficie ya
existía (la API y el reporte) y por símbolo ausente donde no (las funciones
nuevas de `linea_base`):
  (i)  para cada una de las seis cifras, la fuente nueva EXCLUYE una fila
       invertida sintética (`available_at > timestamp_utc`) y, sin filas
       invertidas, da EXACTAMENTE lo mismo que la función vieja de
       `senales.py`: mismo n, mismo redondeo, mismas columnas, mismo orden;
  (ii) la API (`/api/historial`) y el reporte de Telegram sirven la cifra sin
       la fila invertida;
  (iii) la fuente nueva es de sólo lectura: no crea la base ni la abre en
       escritura (las seis viejas corrían `init_db()` en cada llamada);
  (iv) ningún consumidor publicado (`alertas.py`, `api/main.py`, `app.py`)
       sigue llamando a las seis de `senales.py`;
  (v)  lo que NO cambia queda fijado: la deduplicación firmada (1-sep) no se
       aplica a las cifras vivas (no está firmada para ellas; tarjeta §82) y
       el mínimo de observaciones es el de `senales.py`.
Base temporal en cada test: la real no se abre."""
import ast
import os
import sqlite3
import sys
from datetime import date, timedelta

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import noticias  # noqa: E402
import senales  # noqa: E402
from backtest import linea_base as lb  # noqa: E402

MV = senales.MODELO_VERSION
HOY = date.today()
SEIS = ("metricas_apertura", "calibracion_intervalos", "evolucion_aciertos_apertura",
        "ultimas_predicciones_apertura", "verificaciones_detalle", "analisis_puntaje_ia")
CONSUMIDORES = ("alertas.py", os.path.join("api", "main.py"), "app.py")


def _d(hace_dias: int) -> str:
    return (HOY - timedelta(days=hace_dias)).isoformat()


# ------------------------------------------------------------
# Siembra: una base sintética con el esquema real, en tmp
# ------------------------------------------------------------
def _crear(ruta: str) -> None:
    real = senales.DB_PATH
    senales.DB_PATH = ruta
    try:
        senales.init_db()
    finally:
        senales.DB_PATH = real


def _sembrar(ruta: str, fecha: str, ticker: str, *, est=-1.0, gap=-1.5, ret=-2.0, acierto_gap=1,
             acierto_dir=1, err_gap=0.5, err=1.0, int80=2.0, exchange="XKRX", regimen="Alcista · vol alta",
             emision=None, available=None, puntaje=None, retorno_5d=None, verificada=True,
             sesion=None, verificado_en=None) -> None:
    """Una fila sellada con su verificación de apertura (y de puntaje si se
    pide). Por defecto el insumo es conocible ANTES de la emisión; una fila
    invertida se siembra pasando `available` posterior a `emision`."""
    emision = emision or f"{fecha}T21:15:04+00:00"
    available = f"{fecha}T20:00:00+00:00" if available is None else available
    sesion = sesion or (date.fromisoformat(fecha) + timedelta(days=1)).isoformat()
    conn = sqlite3.connect(ruta)
    conn.execute("INSERT OR IGNORE INTO snapshots (fecha, creado_en, timestamp_utc, origen, regimen, modelo_version) "
                 "VALUES (?, ?, ?, 'programado', ?, ?)", (fecha, emision, emision, regimen, MV))
    conn.execute("""INSERT INTO senales_ticker
        (fecha, ticker, puntaje_v0, puntaje_ia, apertura_estimada_pct, confianza_r2, timestamp_utc, exchange,
         sesion_objetivo, available_at, estado, intervalo80_pp, n_muestra, modelo_version, beta)
        VALUES (?, ?, 0.5, ?, ?, 0.3, ?, ?, ?, ?, ?, ?, 120, ?, 0.5)""",
                 (fecha, ticker, puntaje, est, emision, exchange, sesion, available,
                  "verificada" if verificada else "pendiente", int80, MV))
    if verificada:
        conn.execute("""INSERT INTO verificacion_apertura
            (fecha_senal, ticker, apertura_estimada_pct, retorno_real_pct, acierto_direccion, error_pp,
             gap_pct, acierto_gap, error_gap_pp, verificado_en, modelo_version, legacy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                     (fecha, ticker, est, ret, acierto_dir, err, gap, acierto_gap, err_gap,
                      verificado_en or f"{sesion}T21:15:14+00:00", MV))
    if puntaje is not None and retorno_5d is not None:
        conn.execute("""INSERT INTO verificacion_puntaje (fecha_senal, ticker, puntaje_ia, retorno_5d_pct, verificado_en)
                        VALUES (?, ?, ?, ?, ?)""", (fecha, ticker, puntaje, retorno_5d, f"{sesion}T21:15:14+00:00"))
    conn.commit()
    conn.close()


# Un juego de filas variado: tres fechas dentro de la ventana de 30 días, una
# fuera de ella (y dentro de la de 90), dos bolsas, dos regímenes, aciertos y
# errores mezclados, empates de puntaje (los tercios dependen del orden).
FILAS_SANAS = [
    dict(fecha=_d(2), ticker="005930.KS", est=-1.9, gap=-0.7, ret=-1.1, acierto_gap=1, acierto_dir=1, err_gap=1.2, err=0.8,
         int80=2.4, puntaje=0.4, retorno_5d=1.5),
    dict(fecha=_d(2), ticker="000660.KS", est=2.6, gap=-1.4, ret=0.3, acierto_gap=0, acierto_dir=1, err_gap=4.0, err=2.3,
         int80=3.1, puntaje=0.7, retorno_5d=-0.5),
    dict(fecha=_d(2), ticker="2330.TW", est=-0.8, gap=0.0, ret=-0.2, acierto_gap=0, acierto_dir=1, err_gap=0.8, err=0.6,
         int80=1.9, exchange="XTAI", puntaje=0.4, retorno_5d=0.9),
    dict(fecha=_d(9), ticker="005930.KS", est=0.5, gap=2.3, ret=1.7, acierto_gap=1, acierto_dir=1, err_gap=1.8, err=1.2,
         int80=2.2, regimen="Alcista · vol baja", puntaje=0.1, retorno_5d=-2.2),
    dict(fecha=_d(9), ticker="8035.T", est=-2.1, gap=4.4, ret=6.7, acierto_gap=0, acierto_dir=0, err_gap=6.5, err=8.8,
         int80=2.8, exchange="XTKS", regimen="Alcista · vol baja", puntaje=0.9, retorno_5d=3.1),
    dict(fecha=_d(16), ticker="IFX.DE", est=0.3, gap=2.4, ret=4.9, acierto_gap=1, acierto_dir=1, err_gap=2.1, err=4.6,
         int80=1.5, exchange="XETR", puntaje=0.4, retorno_5d=0.0),
    dict(fecha=_d(16), ticker="6857.T", est=0.3, gap=0.3, ret=1.5, acierto_gap=1, acierto_dir=1, err_gap=0.0, err=1.2,
         int80=None, exchange="XTKS", puntaje=0.6, retorno_5d=0.4),   # sin intervalo sellado: fuera de la calibración
    dict(fecha=_d(45), ticker="4063.T", est=-1.1, gap=-1.1, ret=-0.3, acierto_gap=1, acierto_dir=1, err_gap=0.0, err=0.8,
         int80=2.0, exchange="XTKS", puntaje=0.2, retorno_5d=5.0),    # fuera de la ventana de 30 días
    # R2 del auditor 16-3: con nueve filas el corte del tercio es 3 y el tercer puntaje más bajo es un
    # 0.4 EMPATADO con los tres siguientes: el tercio bajo depende del orden de entrada, como en la base real
    dict(fecha=_d(23), ticker="000660.KS", est=1.2, gap=0.9, ret=1.1, acierto_gap=1, acierto_dir=1, err_gap=0.3, err=0.1,
         int80=2.6, puntaje=0.4, retorno_5d=2.5),
]
# La fila invertida: emitida con la sesión abierta (el 28-sep-2026 en miniatura),
# dentro de la ventana de 30 días, con fecha propia para que cambie también la evolución.
INVERTIDA = dict(fecha=_d(5), ticker="3436.T", est=-1.0, gap=2.3, ret=-0.6, acierto_gap=0, acierto_dir=1, err_gap=3.3,
                 err=0.4, int80=2.0, exchange="XTKS", emision=f"{_d(5)}T17:42:58+00:00",
                 available=f"{_d(5)}T20:00:00+00:00", puntaje=0.5, retorno_5d=-4.0)


@pytest.fixture
def bases(tmp_path):
    """Dos bases idénticas salvo por la fila invertida: `sin` no la tiene,
    `con` sí. Devuelve (ruta_sin, ruta_con)."""
    sin, con = str(tmp_path / "sin_invertida.db"), str(tmp_path / "con_invertida.db")
    for ruta in (sin, con):
        _crear(ruta)
        for f in FILAS_SANAS:
            _sembrar(ruta, **f)
    _sembrar(con, **INVERTIDA)
    return sin, con


def _apuntar(monkeypatch, ruta_senales: str, ruta_lb: str) -> None:
    monkeypatch.setattr(senales, "DB_PATH", ruta_senales)
    monkeypatch.setattr(lb, "RUTA_SENALES", ruta_lb)
    if hasattr(lb, "_MEMO_SESION"):
        monkeypatch.setattr(lb, "_MEMO_SESION", {})


def _ordenado(df: pd.DataFrame) -> pd.DataFrame:
    """El mismo frame con las filas en un orden canónico (fecha, ticker), para
    comparar valores, columnas y dtypes sin depender del plan de SQLite."""
    claves = [c for c in ("Fecha", "fecha_senal", "Ticker", "ticker") if c in df.columns]
    if not claves:
        return df.sort_values(list(df.columns), kind="stable").reset_index(drop=True)
    return df.sort_values(claves, kind="stable").reset_index(drop=True)


def _igual(a, b, orden: bool = False) -> bool:
    if isinstance(a, pd.DataFrame) or isinstance(b, pd.DataFrame):
        if not (isinstance(a, pd.DataFrame) and isinstance(b, pd.DataFrame)):
            return False
        return a.equals(b) if orden else _ordenado(a).equals(_ordenado(b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_igual(a[k], b[k], orden) for k in a)
    return a == b


LLAMADAS = {"metricas_apertura": dict(dias=30), "calibracion_intervalos": {}, "evolucion_aciertos_apertura": {},
            "ultimas_predicciones_apertura": dict(limite=50), "verificaciones_detalle": {},
            "analisis_puntaje_ia": dict(dias=90)}


# ------------------------------------------------------------
# (i) Cada cifra: igual a la vieja sin invertidas; excluye la invertida
# ------------------------------------------------------------
@pytest.mark.parametrize("cifra", SEIS)
def test_sin_filas_invertidas_la_fuente_nueva_da_exactamente_lo_mismo_que_senales(bases, monkeypatch, cifra):
    """Mismo n, mismo redondeo, mismas columnas con sus nombres y dtypes, mismos
    valores fila por fila (comparación en orden canónico: el orden en que
    SQLite sirve la consulta vieja no está fijado por ella, R3 del auditor;
    el orden lo fija el test siguiente, declarado como dependiente del plan)."""
    sin, _ = bases
    _apuntar(monkeypatch, sin, sin)
    vieja = getattr(senales, cifra)(**LLAMADAS[cifra])
    nueva = getattr(lb, cifra)(**LLAMADAS[cifra])
    assert _igual(vieja, nueva), f"{cifra}: vieja {vieja!r}\nnueva {nueva!r}"
    if isinstance(vieja, dict):
        assert vieja.get("suficiente") is True, "el juego de filas tiene que superar el mínimo para que la comparación diga algo"


@pytest.mark.parametrize("cifra", ("evolucion_aciertos_apertura", "ultimas_predicciones_apertura", "verificaciones_detalle"))
def test_el_orden_de_filas_es_el_que_sqlite_sirve_hoy_por_el_indice_unico(bases, monkeypatch, cifra):
    """Las consultas viejas no fijan el orden dentro de una fecha; SQLite lo
    sirve por el índice único (fecha_senal, ticker) y la fuente nueva lo FIJA
    con ORDER BY. Este test compara el orden exacto y es, a sabiendas,
    dependiente del plan de consulta de la versión de SQLite del venv: si un
    día se pone rojo solo, el que cambió es el plan, no la cifra (R3)."""
    sin, _ = bases
    _apuntar(monkeypatch, sin, sin)
    vieja = getattr(senales, cifra)(**LLAMADAS[cifra])
    nueva = getattr(lb, cifra)(**LLAMADAS[cifra])
    assert _igual(vieja, nueva, orden=True), f"{cifra}: el orden difiere\nvieja {vieja!r}\nnueva {nueva!r}"


def test_el_puntaje_sintetico_tiene_un_empate_en_el_borde_del_tercio(bases, monkeypatch):
    """R2 del auditor: la equivalencia de los tercios sólo dice algo si un
    empate cae sobre el corte (en la base real hay 513 empates sobre 1308)."""
    sin, _ = bases
    _apuntar(monkeypatch, sin, sin)
    datos = lb.cargar_puntaje_vivo(dias=90)["puntaje"].sort_values().tolist()
    corte = max(1, len(datos) // 3)
    assert datos[corte - 1] == datos[corte], f"sin empate en el borde del tercio bajo: {datos}"


@pytest.mark.parametrize("cifra", SEIS)
def test_cada_cifra_excluye_la_fila_invertida_sintetica(bases, monkeypatch, cifra):
    """Con la fila invertida en la base, la fuente nueva da lo que la vieja da
    SIN ella: la única diferencia permitida entre las dos fuentes son las
    filas que la regla de conocibilidad retira (encargo 16-3, §1)."""
    sin, con = bases
    _apuntar(monkeypatch, sin, con)
    esperado = getattr(senales, cifra)(**LLAMADAS[cifra])     # la vieja, sobre la base SIN la invertida
    obtenido = getattr(lb, cifra)(**LLAMADAS[cifra])          # la nueva, sobre la base CON la invertida
    assert _igual(esperado, obtenido), f"{cifra}: esperado {esperado!r}\nobtenido {obtenido!r}"
    # y la vieja sobre la base CON la invertida sí la cuenta: la diferencia existe y es esa fila
    _apuntar(monkeypatch, con, con)
    vieja_con = getattr(senales, cifra)(**LLAMADAS[cifra])
    if cifra in ("metricas_apertura", "calibracion_intervalos", "analisis_puntaje_ia"):
        assert vieja_con["n"] == obtenido["n"] + 1
    elif cifra == "evolucion_aciertos_apertura":
        assert INVERTIDA["fecha"] in vieja_con["Fecha"].tolist() and INVERTIDA["fecha"] not in obtenido["Fecha"].tolist()
    elif cifra == "ultimas_predicciones_apertura":
        assert INVERTIDA["ticker"] in vieja_con["Ticker"].tolist() and INVERTIDA["ticker"] not in obtenido["Ticker"].tolist()
    else:
        assert len(vieja_con) == len(obtenido) + 1 and INVERTIDA["ticker"] not in obtenido["ticker"].tolist()


def test_la_exclusion_de_las_cifras_vivas_es_la_misma_regla_que_la_del_arbitro(bases, monkeypatch):
    """`cargar_vivas` y `cargar` pasan por la MISMA `excluir_sin_conocibilidad`:
    el conjunto (fecha, ticker) que una retira es el que la otra retira. NULL
    y la igualdad no disparan (misma semántica que el verificador)."""
    _, con = bases
    _apuntar(monkeypatch, con, con)
    vivas = set(zip(lb.cargar_vivas()["fecha_senal"], lb.cargar_vivas()["ticker"]))
    arbitro = set(zip(lb.cargar(dedup=False)["fecha"], lb.cargar(dedup=False)["ticker"]))
    assert vivas == arbitro
    assert (INVERTIDA["fecha"], INVERTIDA["ticker"]) not in vivas
    assert lb.sin_conocibilidad("2026-09-28T21:15:00+00:00", None) is False
    assert lb.sin_conocibilidad("2026-09-28T21:15:00+00:00", "2026-09-28T21:15:00+00:00") is False


def test_la_ventana_de_dias_es_la_misma_expresion_de_sqlite_que_en_senales(bases, monkeypatch):
    """`date('now', '-30 days')` sobre `fecha_senal`, día UTC: la fila de hace
    45 días queda fuera de la ventana de 30 y dentro de la de 90, en las dos
    fuentes por igual."""
    sin, _ = bases
    _apuntar(monkeypatch, sin, sin)
    assert lb.metricas_apertura(dias=30)["n"] == senales.metricas_apertura(dias=30)["n"] == len(FILAS_SANAS) - 1
    assert lb.metricas_apertura(dias=90)["n"] == senales.metricas_apertura(dias=90)["n"] == len(FILAS_SANAS)
    assert "4063.T" not in lb.cargar_vivas(dias=30)["ticker"].tolist()


# ------------------------------------------------------------
# (ii) Los consumidores publicados: la API y el reporte de Telegram
# ------------------------------------------------------------
@pytest.mark.red  # el `meta` del envelope pide el régimen al motor: llega a query*.finance.yahoo.com
def test_reproduccion_la_api_historial_no_cuenta_la_fila_invertida(bases, monkeypatch):
    """REPRODUCCIÓN (rojo sobre HEAD, que sirve las seis de senales.py): con
    la fila invertida en la base, `/api/historial` sirve n sin ella en
    `metricas`, `calibracion`, `wilson`, `puntaje_ia`, y no la lista en
    `ultimas` ni la suma en `evolucion` ni en los desgloses."""
    from fastapi.testclient import TestClient
    from api.main import app
    sin, con = bases
    _apuntar(monkeypatch, con, con)
    datos = TestClient(app).get("/api/historial").json()["datos"]
    _apuntar(monkeypatch, sin, sin)
    esperado = senales.metricas_apertura(dias=30)
    assert datos["metricas"]["n"] == esperado["n"], (
        f"/api/historial sirve n={datos['metricas']['n']} en el track record de 30 días: cuenta la fila "
        f"invertida; sin ella son {esperado['n']}")
    assert datos["metricas"]["gap"] == esperado["gap"]
    assert datos["calibracion"]["n"] == senales.calibracion_intervalos()["n"]
    assert datos["wilson"]["gap"]["n"] == len(senales.verificaciones_detalle())
    assert datos["puntaje_ia"]["n"] == senales.analisis_puntaje_ia(dias=90)["n"]
    assert INVERTIDA["ticker"] not in [u["Ticker"] for u in datos["ultimas"]]
    assert INVERTIDA["fecha"] not in [e["Fecha"] for e in datos["evolucion"]]
    assert sum(f["n"] for f in datos["por_region"]) == len(senales.verificaciones_detalle())


def test_reproduccion_el_reporte_de_telegram_no_cuenta_la_fila_invertida(bases, monkeypatch, tmp_path):
    """REPRODUCCIÓN (rojo sobre HEAD): el bloque «Track record (30d)» del
    reporte sellado dice N sin la fila invertida, y la cobertura del 80% se
    calcula sin ella. El reporte sigue sin llamar al motor."""
    import alertas
    sin, con = bases
    monkeypatch.setattr(noticias, "DB_PATH", str(tmp_path / "noticias.db"))
    noticias.init_db()
    _apuntar(monkeypatch, con, con)
    texto = alertas.componer_reporte_sellado()
    _apuntar(monkeypatch, sin, sin)
    m, cal = senales.metricas_apertura(dias=30), senales.calibracion_intervalos()
    assert f"N={m['n']} ·" in texto, f"el reporte no dice N={m['n']}:\n{texto}"
    assert f"gap {m['gap']['pct_aciertos']:.1f}%" in texto
    assert f"Cobertura del intervalo 80%: {cal['cobertura_pct']:.1f}% (n={cal['n']})" in texto


def test_el_reporte_sigue_sin_llamar_al_motor_con_la_fuente_nueva(bases, monkeypatch, tmp_path):
    """La fuente nueva vive en backtest/, cuyo `datos.py` importa el motor: el
    reporte lo IMPORTA (perezosamente) pero no lo LLAMA. Es la garantía de
    `test_jamas_llama_al_motor`, repetida acá para la ruta nueva."""
    import alertas
    import motor
    sin, _ = bases
    monkeypatch.setattr(noticias, "DB_PATH", str(tmp_path / "noticias.db"))
    noticias.init_db()
    _apuntar(monkeypatch, sin, sin)

    def bomba(*a, **k):
        raise RuntimeError("el reporte llamó al motor en vivo")
    for fn in ("regimen_al", "roca_chip_al", "prediccion_apertura_al", "divergencias_al", "betas_al",
               "puntaje_v0_al", "_datos_crudos"):
        monkeypatch.setattr(motor, fn, bomba)
    texto = alertas.componer_reporte_sellado()
    assert f"N={senales.metricas_apertura(dias=30)['n']} ·" in texto


def test_el_reporte_compone_aunque_el_motor_no_sea_importable(bases, tmp_path):
    """B5 del auditor 16-3: `backtest/datos.py` importa el motor; si la fuente
    nueva lo arrastrara, un `import motor` roto mataría el reporte de las
    18:25 entero, no sólo la línea del track record. La fuente vive sin
    `backtest.datos`. Se prueba en un SUBPROCESO con el import de `motor`
    envenenado desde el arranque (envenenarlo en este proceso rompería al
    resto de la suite)."""
    import subprocess
    import sys as _sys
    sin, _ = bases
    noticias_tmp = str(tmp_path / "noticias.db")
    guion = f"""
import sys
class Veneno:
    def find_spec(self, nombre, ruta, destino=None):
        if nombre == "motor" or nombre.startswith("motor."):
            raise ImportError("motor envenenado a propósito (B5, corrida 16-3)")
        return None
sys.meta_path.insert(0, Veneno())
sys.path.insert(0, {RAIZ!r})
import noticias, senales
noticias.DB_PATH = {noticias_tmp!r}; noticias.init_db()
senales.DB_PATH = {sin!r}
from backtest import linea_base as lb
lb.RUTA_SENALES = {sin!r}
assert "motor" not in sys.modules, "la fuente única arrastró el motor"
import alertas
texto = alertas.componer_reporte_sellado()
assert "Track record" in texto and "N=" in texto, texto
print("OK", lb.metricas_apertura(dias=30)["n"])
"""
    r = subprocess.run([_sys.executable, "-c", guion], capture_output=True, text=True, timeout=120, cwd=RAIZ)
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stdout.strip().startswith("OK ")


def test_la_fuente_unica_no_importa_backtest_datos_ni_el_motor():
    arbol = ast.parse(open(os.path.join(RAIZ, "backtest", "linea_base.py"), encoding="utf-8").read())
    modulos = set()
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            modulos |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            modulos.add(n.module)
    assert "backtest.datos" not in modulos and "motor" not in modulos, sorted(modulos)


# ------------------------------------------------------------
# (iii) Sólo lectura: ni crea la base ni la abre en escritura
# ------------------------------------------------------------
def test_sin_base_las_seis_dicen_datos_insuficientes_y_no_crean_nada(tmp_path, monkeypatch):
    ruta = str(tmp_path / "no_existe.db")
    _apuntar(monkeypatch, ruta, ruta)
    assert lb.metricas_apertura(dias=30) == {"suficiente": False, "n": 0}
    assert lb.calibracion_intervalos() == {"suficiente": False, "n": 0}
    assert lb.evolucion_aciertos_apertura().columns.tolist() == ["Fecha", "% Aciertos gap", "% Aciertos sesión", "N"]
    assert lb.evolucion_aciertos_apertura().empty
    u = lb.ultimas_predicciones_apertura(limite=50)
    assert u.empty and u.columns.tolist() == ["Fecha", "Ticker", "Estimado %", "Gap real %", "Sesión real %",
                                              "Acierto gap", "Acierto sesión", "Sesión objetivo", "Emitida (UTC)"]
    assert lb.verificaciones_detalle().empty
    a = lb.analisis_puntaje_ia(dias=90)
    assert (a["suficiente"], a["n"]) == (False, 0) and a["datos"].empty
    assert not os.path.exists(ruta), "la fuente nueva creó la base que las viejas creaban con init_db()"


def test_las_seis_no_modifican_la_base_que_leen(bases, monkeypatch):
    sin, _ = bases
    _apuntar(monkeypatch, sin, sin)
    antes = os.stat(sin)
    with open(sin, "rb") as f:
        bytes_antes = f.read()
    for cifra in SEIS:
        getattr(lb, cifra)(**LLAMADAS[cifra])
    despues = os.stat(sin)
    with open(sin, "rb") as f:
        bytes_despues = f.read()
    assert (antes.st_size, antes.st_mtime_ns) == (despues.st_size, despues.st_mtime_ns)
    assert bytes_antes == bytes_despues


def test_las_funciones_nuevas_abren_la_base_solo_en_modo_ro():
    fuente = open(os.path.join(RAIZ, "backtest", "linea_base.py"), encoding="utf-8").read()
    arbol = ast.parse(fuente)
    nombres = {n.name for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)}
    assert set(SEIS) | {"cargar_vivas", "cargar_puntaje_vivo"} <= nombres
    for fn in [n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef) and n.name in set(SEIS) | {"cargar_vivas", "cargar_puntaje_vivo"}]:
        llamadas = {c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", None)
                    for c in ast.walk(fn) if isinstance(c, ast.Call)}
        assert "connect" not in llamadas and "get_connection" not in llamadas and "init_db" not in llamadas, fn.name
    assert "import senales" not in fuente and "from senales" not in fuente, (
        "la capa de medición no importa el módulo que escribe la base")


# ------------------------------------------------------------
# (iv) Ningún consumidor publicado sigue leyendo las seis de senales.py
# ------------------------------------------------------------
def _llamadas_a_senales(ruta: str) -> set:
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    return {n.attr for n in ast.walk(arbol)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "senales"}


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_ningun_consumidor_publicado_llama_a_las_seis_de_senales(consumidor):
    """Las seis siguen existiendo en senales.py (no se borran en la 16-3,
    tarjeta §82) pero ningún consumidor publicado las llama: el reporte, la
    API y el dashboard leen de `backtest.linea_base`."""
    ruta = os.path.join(RAIZ, consumidor)
    usadas = _llamadas_a_senales(ruta) & set(SEIS)
    assert not usadas, f"{consumidor} sigue leyendo {sorted(usadas)} de senales.py"
    fuente = open(ruta, encoding="utf-8").read()
    assert "linea_base" in fuente, f"{consumidor} no lee de backtest.linea_base"


def test_contraprueba_el_detector_ve_una_llamada_a_senales(tmp_path):
    ruta = tmp_path / "x.py"
    ruta.write_text("import senales\nm = senales.metricas_apertura(dias=30)\n", encoding="utf-8")
    assert _llamadas_a_senales(str(ruta)) & set(SEIS) == {"metricas_apertura"}


# ------------------------------------------------------------
# (v) Lo que NO cambia queda fijado
# ------------------------------------------------------------
def test_el_minimo_de_observaciones_es_el_de_senales():
    assert lb.MINIMO_OBSERVACIONES == senales.MINIMO_OBSERVACIONES == 5


def test_la_deduplicacion_firmada_no_se_aplica_a_las_cifras_vivas_y_queda_declarada(tmp_path, monkeypatch):
    """La regla de deduplicación (1-sep-2026) rige en el árbitro (`cargar`,
    dedup por defecto). Para las cifras vivas NO está firmada: §93.4 nombra
    sólo la conocibilidad, y aplicarla movería el n de las cifras de toda la
    historia por otra razón, lo que el encargo 16-3 prohíbe. Este test fija
    lo DECLARADO (tarjeta §82); si Nicolás firma la deduplicación para las
    cifras vivas, este test cambia con esa firma, no antes."""
    ruta = str(tmp_path / "pares.db")
    _crear(ruta)
    _apuntar(monkeypatch, ruta, ruta)
    # el par del defecto de snapshot.py: dos emisiones de días distintos que apuntan a la
    # MISMA sesión objetivo; la de la emisión tardía (martes 01:23Z) no «calza» con la sesión
    # que sigue a su available_at y la deduplicación la retira; la otra sí calza
    _sembrar(ruta, "2026-07-28", "005930.KS", emision="2026-07-28T21:15:00+00:00",
             available="2026-07-28T20:00:00+00:00", sesion="2026-07-29")
    _sembrar(ruta, "2026-07-27", "005930.KS", emision="2026-07-28T01:23:34+00:00",
             available="2026-07-27T20:00:00+00:00", sesion="2026-07-29")
    for f in FILAS_SANAS[:4]:
        _sembrar(ruta, **f)
    con_dedup, sin_dedup = lb.cargar(), lb.cargar(dedup=False)
    assert len(sin_dedup) == len(con_dedup) + 1, "la siembra no reproduce un par que la regla retire"
    assert len(lb.cargar_vivas()) == len(sin_dedup)
    assert len(lb.verificaciones_detalle()) == len(sin_dedup)
    assert lb.calibracion_intervalos()["n"] == senales.calibracion_intervalos()["n"] == len(sin_dedup)
