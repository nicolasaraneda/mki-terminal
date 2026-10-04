# ============================================================
# tests/test_guarda_puntaje.py — la guarda de conocibilidad en
# `senales.verificar_puntaje_pendientes` (corrida 16a, 4-oct-2026).
# Acta §93.4-bis (i) de DECISIONES.md, firmada por Nicolás el 4-oct-2026.
#
# El hecho que lo origina: la corrida 15 puso la guarda (a) de §90.1 en el
# verificador de APERTURA; el auditor de esa corrida (B2) midió que el
# verificador de PUNTAJE no la tiene: su consulta toma toda fila con
# `fecha <= date('now','-7 días')` y sólo excluye `legacy_pre_4.6`, así que
# una fila que declara su insumo conocible (`available_at`) DESPUÉS de haber
# sido emitida (`timestamp_utc`) entra a `verificacion_puntaje` como válida.
#
# La regla (encargo 16a §2.2): `verificar_puntaje_pendientes` no verifica
# ninguna fila con `available_at > timestamp_utc`. Misma comparación de
# INSTANTES con zona que la guarda de apertura; NULL no dispara; la
# igualdad tampoco. Como `verificacion_puntaje` no tiene columna de estado
# (ni se cambia el esquema), la fila excluida NO se escribe, el verificador
# declara la cuenta por su log, y el `estado` de `senales_ticker` no se toca.
#
# Lo que este archivo NO prueba, a propósito: la regla maestra de timing
# (emisión antes de la apertura de la sesión objetivo) en este verificador.
# El acta §93.4 la deja abierta; hay un test que la deja PINCHADA como
# ausente para que, cuando se agregue, falle a propósito y se actualice.
#
# Reglas de la casa: ningún test escribe en senales.db; lo que escribe,
# escribe en `tmp_path` con `senales.DB_PATH` parcheado y un guardia lo
# comprueba antes. La base real se abre sólo en `mode=ro` o para copiarla.
# Sin red: `senales._ohlc_local` está reemplazado. Cero intentos del DSR.
# ============================================================

import inspect
import os
import shutil
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import calendarios  # noqa: E402  (real)
import senales  # noqa: E402

BASE_REAL = os.path.join(RAIZ, "senales.db")
HAY_BASE = os.path.exists(BASE_REAL)
solo_con_base = pytest.mark.skipif(
    not HAY_BASE, reason="sin senales.db: no hay historia sellada que leer")

# Una fecha sintética que YA cumple los 7 días que exige la consulta del
# verificador, calculada y no escrita: la guarda es por regla, no por fecha.
FECHA_SENAL = (date.today() - timedelta(days=14)).isoformat()
EMISION = f"{FECHA_SENAL}T21:15:00+00:00"            # 18:15 de Chile, aprox.
INSUMO_POSTERIOR = f"{FECHA_SENAL}T23:00:00+00:00"   # conocible DESPUÉS de emitir
INSUMO_ANTERIOR = (date.fromisoformat(FECHA_SENAL) - timedelta(days=1)).isoformat() \
    + "T20:00:00+00:00"                               # conocible ANTES de emitir
CIERRES = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0]
RETORNO_5D_ESPERADO = round((CIERRES[senales.DIAS_FORWARD_PUNTAJE] / CIERRES[0] - 1) * 100, 4)


def _ro(ruta: str) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)


def _instante(texto: str) -> datetime:
    t = datetime.fromisoformat(texto)
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def _guardia_base_temporal(tmp_path) -> None:
    """Jamás contra la base real: se comprueba antes de cada escritura."""
    assert senales.DB_PATH.startswith(str(tmp_path)), senales.DB_PATH
    assert os.path.abspath(senales.DB_PATH) != os.path.abspath(BASE_REAL)


def _ohlc_falso():
    """Reemplazo de `senales._ohlc_local`: siete sesiones hábiles desde la
    fecha pedida, cierres 100..106 (retorno a 5 días = +5,0 %). Cero red.
    Registra cada llamada: una fila excluida no debe llegar a la red."""
    llamadas = []

    def falso(ticker, desde):
        llamadas.append((ticker, desde))
        idx = pd.bdate_range(desde, periods=len(CIERRES))
        return pd.DataFrame({"Open": CIERRES, "Close": CIERRES}, index=idx)
    falso.llamadas = llamadas
    return falso


@pytest.fixture
def base_puntaje(monkeypatch, tmp_path):
    """Base TEMPORAL con el esquema real, red reemplazada y dos helpers:
    sembrar una fila de `senales_ticker` con `puntaje_ia`, y leer lo que
    quedó en `verificacion_puntaje` y los estados de `senales_ticker`."""
    monkeypatch.setattr(senales, "DB_PATH", str(tmp_path / "senales_puntaje.db"))
    _guardia_base_temporal(tmp_path)
    senales.init_db()
    ohlc = _ohlc_falso()
    monkeypatch.setattr(senales, "_ohlc_local", ohlc)

    def sembrar(ticker: str, timestamp_utc: str, available_at, estado=None,
                fecha: str = FECHA_SENAL, sesion_objetivo=None, exchange="XKRX"):
        _guardia_base_temporal(tmp_path)
        conn = senales.get_connection()
        conn.execute(
            """INSERT INTO senales_ticker
               (fecha, ticker, puntaje_v0, sentimiento_ia, puntaje_ia,
                timestamp_utc, exchange, sesion_objetivo, available_at, estado,
                modelo_version)
               VALUES (?, ?, 0.5, 0.2, 0.35, ?, ?, ?, ?, ?, ?)""",
            (fecha, ticker, timestamp_utc, exchange, sesion_objetivo,
             available_at, estado, senales.MODELO_VERSION))
        conn.commit()
        conn.close()

    def leer():
        conn = _ro(senales.DB_PATH)
        estados = dict(conn.execute("SELECT ticker, estado FROM senales_ticker"))
        verificadas = {t: r for t, r in conn.execute(
            "SELECT ticker, retorno_5d_pct FROM verificacion_puntaje")}
        conn.close()
        return estados, verificadas

    return {"sembrar": sembrar, "leer": leer, "ohlc": ohlc}


def test_el_escenario_es_el_que_dice_ser():
    """Premisas: la fecha sintética ya cumple los 7 días de la consulta; la
    inversión es de ORDEN entre instantes y no de formato."""
    assert FECHA_SENAL <= (date.today() - timedelta(days=7)).isoformat()
    assert _instante(INSUMO_POSTERIOR) > _instante(EMISION)
    assert _instante(INSUMO_ANTERIOR) < _instante(EMISION)
    assert RETORNO_5D_ESPERADO == 5.0


# ------------------------------------------------------------
# Reproducción y controles
# ------------------------------------------------------------
def test_reproduccion_una_fila_con_la_inversion_no_entra_a_verificacion_puntaje(base_puntaje):
    """REPRODUCCIÓN (falla sobre HEAD, que la verifica). Una fila con
    `puntaje_ia`, de hace más de 7 días, que declara su insumo conocible
    DESPUÉS de su emisión, no se escribe en `verificacion_puntaje`, no se
    cuenta como verificada y no gasta una llamada a la red."""
    base_puntaje["sembrar"]("005930.KS", EMISION, INSUMO_POSTERIOR)
    verificados = senales.verificar_puntaje_pendientes()
    estados, verificadas = base_puntaje["leer"]()
    assert "005930.KS" not in verificadas, (
        f"la fila con available_at ({INSUMO_POSTERIOR}) posterior a su "
        f"timestamp_utc ({EMISION}) entró a verificacion_puntaje con "
        f"retorno {verificadas.get('005930.KS')!r}: el verificador la procesó como válida")
    assert verificados == 0
    assert base_puntaje["ohlc"].llamadas == [], (
        "la fila excluida llegó a la descarga: la guarda tiene que ir ANTES de la red")


def test_control_la_misma_fila_sin_la_inversion_se_verifica_igual(base_puntaje):
    """CONTROL: idéntica, salvo que el insumo era conocible ANTES de la
    emisión. Se verifica como siempre, con el retorno a 5 días de siempre."""
    base_puntaje["sembrar"]("005930.KS", EMISION, INSUMO_ANTERIOR)
    verificados = senales.verificar_puntaje_pendientes()
    estados, verificadas = base_puntaje["leer"]()
    assert verificadas == {"005930.KS": RETORNO_5D_ESPERADO}
    assert verificados == 1
    assert base_puntaje["ohlc"].llamadas == [("005930.KS", FECHA_SENAL)]


def test_control_una_fila_legacy_sigue_excluida(base_puntaje):
    """CONTROL: la exclusión que ya existía (`legacy_pre_4.6`) sigue
    operando, con o sin inversión."""
    base_puntaje["sembrar"]("005930.KS", EMISION, INSUMO_ANTERIOR,
                            estado=senales.ESTADO_LEGACY)
    base_puntaje["sembrar"]("000660.KS", EMISION, INSUMO_POSTERIOR,
                            estado=senales.ESTADO_LEGACY)
    verificados = senales.verificar_puntaje_pendientes()
    _, verificadas = base_puntaje["leer"]()
    assert verificadas == {} and verificados == 0
    assert base_puntaje["ohlc"].llamadas == []


@pytest.mark.parametrize("available_at", [None, EMISION],
                         ids=["available_at NULL", "available_at == timestamp_utc"])
def test_la_guarda_no_dispara_con_available_at_nulo_ni_igual(base_puntaje, available_at):
    """NULL no dispara. La IGUALDAD tampoco: es la rama del `except` de
    snapshot.py (available_at cayó al reloj de pared), que tiene su propia
    alerta en el vigía (acta §84.2). Misma semántica que la guarda (a)."""
    base_puntaje["sembrar"]("005930.KS", EMISION, available_at)
    verificados = senales.verificar_puntaje_pendientes()
    _, verificadas = base_puntaje["leer"]()
    assert verificadas == {"005930.KS": RETORNO_5D_ESPERADO}
    assert verificados == 1


def test_la_guarda_compara_instantes_y_no_texto(base_puntaje):
    """El mismo instante escrito en otro huso ordena ANTES como texto y
    DESPUÉS como instante. La guarda compara datetimes con zona, como la de
    apertura; una comparación SQL de cadenas la dejaría pasar muda."""
    posterior_en_otro_huso = _instante(INSUMO_POSTERIOR).astimezone(
        timezone(timedelta(hours=-4))).isoformat()
    assert posterior_en_otro_huso < EMISION                       # como texto
    assert _instante(posterior_en_otro_huso) > _instante(EMISION)  # como instante
    base_puntaje["sembrar"]("005930.KS", EMISION, posterior_en_otro_huso)
    verificados = senales.verificar_puntaje_pendientes()
    _, verificadas = base_puntaje["leer"]()
    assert verificadas == {} and verificados == 0


def test_la_guarda_no_depende_del_estado_y_no_lo_cambia(base_puntaje):
    """A diferencia de la guarda de apertura, que opera sobre filas
    `pendiente` de SU máquina de estados, ésta mira sólo los dos instantes:
    la inversión excluye igual con estado `verificada`, sin estado o
    `no_verificable_timing`. Y el verificador de puntaje no escribe
    `estado`: los tres quedan como estaban. (Las 24 filas del evento son 8
    `verificada` y 16 sin estado; ninguna está en `verificacion_puntaje`.)"""
    base_puntaje["sembrar"]("005930.KS", EMISION, INSUMO_POSTERIOR,
                            estado=senales.ESTADO_VERIFICADA)
    base_puntaje["sembrar"]("000660.KS", EMISION, INSUMO_POSTERIOR, estado=None)
    base_puntaje["sembrar"]("2330.TW", EMISION, INSUMO_POSTERIOR,
                            estado=senales.ESTADO_NO_VERIFICABLE)
    base_puntaje["sembrar"]("NVDA", EMISION, INSUMO_ANTERIOR,
                            estado=senales.ESTADO_VERIFICADA)
    verificados = senales.verificar_puntaje_pendientes()
    estados, verificadas = base_puntaje["leer"]()
    assert verificadas == {"NVDA": RETORNO_5D_ESPERADO}
    assert verificados == 1
    assert estados == {"005930.KS": senales.ESTADO_VERIFICADA, "000660.KS": None,
                       "2330.TW": senales.ESTADO_NO_VERIFICABLE,
                       "NVDA": senales.ESTADO_VERIFICADA}


def test_el_verificador_declara_la_cuenta_de_filas_excluidas(base_puntaje, capsys):
    """`verificacion_puntaje` no admite un estado sin cambiar el esquema, así
    que la exclusión se declara por el log del job (snapshot.log): una línea
    con la cuenta y las fechas. Sin fila excluida, ninguna línea."""
    base_puntaje["sembrar"]("005930.KS", EMISION, INSUMO_POSTERIOR)
    base_puntaje["sembrar"]("000660.KS", EMISION, INSUMO_POSTERIOR)
    base_puntaje["sembrar"]("NVDA", EMISION, INSUMO_ANTERIOR)
    senales.verificar_puntaje_pendientes()
    salida = capsys.readouterr().out
    lineas = [l for l in salida.splitlines() if "AVISO verificador puntaje" in l]
    assert len(lineas) == 1, salida
    assert "2 fila(s)" in lineas[0] and FECHA_SENAL in lineas[0], lineas[0]
    assert "available_at > timestamp_utc" in lineas[0]

    # Segunda corrida: las excluidas siguen sin estar en la tabla (el LEFT
    # JOIN las vuelve a candidatear), así que la declaración se repite y la
    # tabla no cambia. NVDA ya está y no se repite.
    senales.verificar_puntaje_pendientes()
    salida = capsys.readouterr().out
    assert sum("AVISO verificador puntaje" in l for l in salida.splitlines()) == 1
    _, verificadas = base_puntaje["leer"]()
    assert verificadas == {"NVDA": RETORNO_5D_ESPERADO}


def test_sin_filas_excluidas_el_verificador_no_declara_nada(base_puntaje, capsys):
    """Sin inversión no hay línea: el aviso existe sólo cuando hay algo que
    declarar, para que una línea en snapshot.log sea siempre un hecho."""
    base_puntaje["sembrar"]("NVDA", EMISION, INSUMO_ANTERIOR)
    base_puntaje["sembrar"]("005930.KS", EMISION, None)
    verificados = senales.verificar_puntaje_pendientes()
    assert verificados == 2
    assert "AVISO verificador puntaje" not in capsys.readouterr().out


def test_la_guarda_es_por_regla_y_no_por_fecha():
    """El código del verificador no nombra el evento: ninguna fecha
    literal (acta §90.1 d, mismo criterio)."""
    fuente = inspect.getsource(senales.verificar_puntaje_pendientes)
    assert "2026-" not in fuente and "28-sep" not in fuente
    assert "available_at" in fuente and "timestamp_utc" in fuente


# ------------------------------------------------------------
# Lo que NO se agregó, pinchado (acta §93.4: la regla maestra queda abierta)
# ------------------------------------------------------------
def test_pin_la_regla_maestra_no_esta_en_este_verificador(base_puntaje):
    """PIN, no permiso. El encargo 16a prohíbe agregar la regla maestra a
    este verificador (acta §93.4 la deja abierta). Una fila emitida DESPUÉS
    de la apertura de su sesión objetivo, pero con el insumo conocible antes
    de la emisión, hoy SÍ entra a `verificacion_puntaje`. Cuando la regla
    maestra se agregue, este test debe fallar y reescribirse en el mismo
    acto: así la ausencia queda a la vista y no en la memoria de nadie.

    Magnitud del hueco, MEDIDA por el auditor el 4-oct-2026 en la base real
    (`mode=ro`): 0 filas emitidas tarde han entrado nunca a
    `verificacion_puntaje` (1.272 filas), y 0 de las 27 candidatas del
    5-oct lo están. El hueco es real en el código y vacío en el dato a esa
    fecha; deja de serlo el día que un sello tardío vuelva a ocurrir. El
    auditor recomendó (R4, dictamen 16a) escribir este pin como
    `xfail(strict=True)` sobre la conducta deseada, con entrada en
    `tests/test_razones_xfail.py`; eso toca un archivo fuera del alcance de
    la 16a y queda para la corrida 16."""
    sesion = date.fromisoformat(FECHA_SENAL) + timedelta(days=1)
    while not calendarios.es_sesion("XKRX", sesion.isoformat()):
        sesion += timedelta(days=1)
    apertura = calendarios.apertura_utc("XKRX", sesion.isoformat())
    emision_tardia = (apertura + timedelta(hours=3)).isoformat()
    insumo = (apertura - timedelta(hours=10)).isoformat()
    assert _instante(insumo) < _instante(emision_tardia)
    assert _instante(emision_tardia) >= apertura        # viola la regla maestra
    base_puntaje["sembrar"]("005930.KS", emision_tardia, insumo,
                            sesion_objetivo=sesion.isoformat())
    verificados = senales.verificar_puntaje_pendientes()
    _, verificadas = base_puntaje["leer"]()
    assert verificadas == {"005930.KS": RETORNO_5D_ESPERADO} and verificados == 1
    assert "calendarios" not in inspect.getsource(senales.verificar_puntaje_pendientes)


# ------------------------------------------------------------
# Corte de método sobre la historia real (copia; la base real en mode=ro)
# ------------------------------------------------------------
def _volcado(ruta: str) -> tuple:
    conn = _ro(ruta)
    try:
        verificaciones = conn.execute(
            "SELECT * FROM verificacion_puntaje ORDER BY id").fetchall()
        invertidas = conn.execute(
            "SELECT * FROM senales_ticker WHERE available_at > timestamp_utc "
            "ORDER BY id").fetchall()
        candidatas_invertidas = conn.execute(f"""
            SELECT s.fecha, s.ticker FROM senales_ticker s
            LEFT JOIN verificacion_puntaje v
              ON v.fecha_senal = s.fecha AND v.ticker = s.ticker
            WHERE s.puntaje_ia IS NOT NULL AND v.id IS NULL
              AND s.timestamp_utc IS NOT NULL
              AND (s.estado IS NULL OR s.estado != '{senales.ESTADO_LEGACY}')
              AND s.fecha <= date('now', '-7 days')
              AND s.available_at > s.timestamp_utc
            ORDER BY s.fecha, s.ticker""").fetchall()
    finally:
        conn.close()
    return verificaciones, invertidas, candidatas_invertidas


@solo_con_base
def test_corte_de_metodo_sobre_la_historia_real(monkeypatch, tmp_path, capsys):
    """La guarda rige para lo que el verificador procese desde que se
    aplique: ninguna fila existente de `verificacion_puntaje` se modifica ni
    se borra, ningún `estado` de `senales_ticker` cambia, y las filas
    invertidas que ya cumplen los 7 días se declaran excluidas, en el número
    exacto que da la consulta de referencia. Corre sobre una COPIA con la
    red reemplazada por un marco vacío (así lo único que puede escribir es
    la guarda, y la guarda no escribe)."""
    real_antes = os.stat(BASE_REAL)
    verif_real, invertidas_real, candidatas_real = _volcado(BASE_REAL)
    if not invertidas_real:
        pytest.skip("la base no tiene filas con available_at > timestamp_utc")

    copia = str(tmp_path / "senales_copia.db")
    shutil.copy(BASE_REAL, copia)
    monkeypatch.setattr(senales, "DB_PATH", copia)
    _guardia_base_temporal(tmp_path)
    monkeypatch.setattr(senales, "_ohlc_local", lambda *a, **k: pd.DataFrame())

    antes = _volcado(copia)
    assert repr(antes) == repr((verif_real, invertidas_real, candidatas_real))

    verificados = senales.verificar_puntaje_pendientes()
    salida = capsys.readouterr().out

    despues = _volcado(copia)
    assert verificados == 0
    assert repr(despues[0]) == repr(antes[0]), "verificacion_puntaje cambió"
    assert repr(despues[1]) == repr(antes[1]), "una fila invertida de senales_ticker cambió"
    if candidatas_real:
        fechas = sorted({f for f, _ in candidatas_real})
        assert f"{len(candidatas_real)} fila(s)" in salida, salida
        assert all(f in salida for f in fechas), salida
    else:
        assert "AVISO verificador puntaje" not in salida
    real_despues = os.stat(BASE_REAL)
    assert (real_antes.st_size, real_antes.st_mtime_ns) == (
        real_despues.st_size, real_despues.st_mtime_ns)
