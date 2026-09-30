# ============================================================
# tests/test_conocibilidad.py — el término de conocibilidad del riel de
# medición (corrida 15, bloque 1). Actas §90.1 y §90.2 de DECISIONES.md,
# firmadas por Nicolás el 29-sep-2026.
#
# El hecho que lo origina: el 28-sep-2026 el PC despertó de una suspensión
# y snapshot.py selló a las 13:42 de Nueva York, con la bolsa abierta. 24
# filas de `senales_ticker` quedaron con `available_at` (20:00 UTC, el
# cierre de la sesión del SOX usada) POSTERIOR a su `timestamp_utc` (17:42
# UTC, la emisión): el sello declara conocible su insumo 2 h 17 min después
# de existir. Nada lo detectó (acta §89.1).
#
# Cuatro bloques, uno por punto del encargo:
#   1.1  guarda (a): el verificador no verifica una fila con la inversión;
#   1.2  guarda (b): snapshot.py no sella si la sesión de `sox_fecha` no
#        ha cerrado al instante de emisión (margen CERO);
#   1.3  exclusión (d): la capa de medición deja fuera toda fila con la
#        inversión, por regla y sin nombrar ninguna fecha;
#   1.4  las dos anclas de `sesion_objetivo` (§84.1 vs §90.2) sobre toda la
#        historia sellada. MEDICIÓN, no permiso: ver el bloque.
#
# Reglas de este archivo, que son las de la casa:
#   · Ningún test escribe en senales.db, noticias.db ni
#     dinero/sello_dinero.db. Lo que escribe, escribe en `tmp_path` con
#     `senales.DB_PATH` parcheado, y un guardia lo comprueba antes.
#   · Toda lectura de la base real es `mode=ro`. La única vez que la base
#     real se abre como archivo es para COPIARLA a `tmp_path`.
#   · Sin red: `senales._ohlc_local` y el motor están reemplazados, y
#     `motor._datos_crudos` revienta si alguien llega hasta él.
#   · `calendarios` es el REAL, sin monkeypatch salvo donde el test dice
#     que lo rompe a propósito.
#
# Cero intentos del DSR: no se evalúa ninguna hipótesis sobre retornos.
# ============================================================

import os
import shutil
import sqlite3
import sys
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import calendarios  # noqa: E402  (real)
import motor  # noqa: E402
import noticias  # noqa: E402
import registro  # noqa: E402
import senales  # noqa: E402
import snapshot  # noqa: E402
from backtest import linea_base as lb  # noqa: E402

BASE_REAL = os.path.join(RAIZ, "senales.db")
HAY_BASE = os.path.exists(BASE_REAL)
solo_con_base = pytest.mark.skipif(
    not HAY_BASE, reason="sin senales.db: no hay historia sellada que leer")

CHILE = ZoneInfo("America/Santiago")
NUEVA_YORK = ZoneInfo("America/New_York")

# El evento, con sus instantes reales (acta §89.1).
FECHA_EVENTO = "2026-09-28"
EMISION_EVENTO = "2026-09-28T17:42:58.943983+00:00"   # 13:42 de Nueva York
CIERRE_EVENTO = "2026-09-28T20:00:00+00:00"           # cierre de XNYS ese día
SESION_OBJETIVO_EVENTO = "2026-09-29"


def _ro(ruta: str) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)


def _instante(texto: str) -> datetime:
    t = datetime.fromisoformat(texto)
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def _guardia_base_temporal(tmp_path) -> None:
    """Jamás contra la base real: se comprueba antes de cada escritura."""
    assert senales.DB_PATH.startswith(str(tmp_path)), senales.DB_PATH
    assert os.path.abspath(senales.DB_PATH) != os.path.abspath(BASE_REAL)


# ============================================================
# 1.1 — Guarda (a): el verificador (acta §90.1 a)
# ============================================================
def _ohlc_falso(exchange: str, sesion_obj: str):
    """Reemplazo de `senales._ohlc_local`: la sesión anterior y la objetivo,
    con valores que dan gap −1,0 % y retorno de sesión −2,0 %. Cero red."""
    sesion_ant = calendarios.sesion_anterior(exchange, sesion_obj)
    llamadas = []

    def falso(ticker, desde):
        llamadas.append((ticker, desde))
        return pd.DataFrame({"Open": [100.0, 99.0], "Close": [100.0, 98.0]},
                            index=pd.to_datetime([sesion_ant, sesion_obj]))
    falso.llamadas = llamadas
    return falso


@pytest.fixture
def base_verificador(monkeypatch, tmp_path):
    """Base TEMPORAL con el esquema real y un helper para sembrar una fila
    `pendiente`. La red del verificador queda reemplazada."""
    monkeypatch.setattr(senales, "DB_PATH", str(tmp_path / "senales_verificador.db"))
    _guardia_base_temporal(tmp_path)
    senales.init_db()
    ohlc = _ohlc_falso("XKRX", SESION_OBJETIVO_EVENTO)
    monkeypatch.setattr(senales, "_ohlc_local", ohlc)

    def sembrar(ticker: str, timestamp_utc: str, available_at, estado="pendiente"):
        _guardia_base_temporal(tmp_path)
        conn = senales.get_connection()
        conn.execute(
            """INSERT INTO senales_ticker
               (fecha, ticker, puntaje_v0, apertura_estimada_pct, confianza_r2,
                timestamp_utc, exchange, sesion_objetivo, available_at, estado,
                intervalo80_pp, n_muestra, modelo_version, beta)
               VALUES (?, ?, 0.5, -1.32, 0.3, ?, 'XKRX', ?, ?, ?, 2.0, 120, ?, 0.81)""",
            (FECHA_EVENTO, ticker, timestamp_utc, SESION_OBJETIVO_EVENTO,
             available_at, estado, senales.MODELO_VERSION))
        conn.commit()
        conn.close()

    def leer():
        conn = _ro(senales.DB_PATH)
        estados = dict(conn.execute("SELECT ticker, estado FROM senales_ticker"))
        verificadas = [t for (t,) in conn.execute(
            "SELECT ticker FROM verificacion_apertura ORDER BY ticker")]
        conn.close()
        return estados, verificadas

    return {"sembrar": sembrar, "leer": leer, "ohlc": ohlc}


def test_el_escenario_del_verificador_es_el_que_dice_ser():
    """Premisas de los tests de abajo, leídas del calendario real: la sesión
    objetivo existe, abrió DESPUÉS de la emisión (la regla maestra de timing
    NO la descarta: si lo hiciera, el test de reproducción pasaría por la
    razón equivocada) y ya cerró con su margen de publicación."""
    assert calendarios.es_sesion("XKRX", SESION_OBJETIVO_EVENTO)
    apertura = calendarios.apertura_utc("XKRX", SESION_OBJETIVO_EVENTO)
    assert _instante(EMISION_EVENTO) < apertura
    assert calendarios.sesion_ya_cerro("XKRX", SESION_OBJETIVO_EVENTO)
    assert calendarios.cierre_utc("XNYS", FECHA_EVENTO).isoformat() == CIERRE_EVENTO
    assert _instante(CIERRE_EVENTO) > _instante(EMISION_EVENTO)


def test_reproduccion_el_verificador_no_verifica_una_fila_con_la_inversion(base_verificador):
    """REPRODUCCIÓN (falla sobre HEAD, que la verifica). Una fila `pendiente`
    emitida a las 17:42 UTC que declara su insumo conocible a las 20:00 UTC
    pasa a `no_verificable_timing`, no escribe nada en
    `verificacion_apertura` y se cuenta en `no_verificables`."""
    base_verificador["sembrar"]("005930.KS", EMISION_EVENTO, CIERRE_EVENTO)
    resultado = senales.verificar_apertura_pendientes()
    estados, verificadas = base_verificador["leer"]()
    assert estados["005930.KS"] == senales.ESTADO_NO_VERIFICABLE, (
        f"la fila con available_at ({CIERRE_EVENTO}) posterior a su "
        f"timestamp_utc ({EMISION_EVENTO}) quedó en estado "
        f"{estados['005930.KS']!r}: el verificador la procesó como válida")
    assert verificadas == [], (
        f"el verificador escribió en verificacion_apertura una fila con la "
        f"inversión: {verificadas}")
    assert resultado["no_verificables"] == 1, resultado
    assert resultado["verificadas"] == 0, resultado


def test_control_la_misma_fila_sin_la_inversion_se_verifica(base_verificador):
    """CONTROL: idéntica, salvo que el insumo era conocible ANTES de la
    emisión (el cierre de la sesión anterior). Se verifica como siempre."""
    cierre_previo = calendarios.cierre_utc(
        "XNYS", calendarios.sesion_anterior("XNYS", FECHA_EVENTO)).isoformat()
    assert _instante(cierre_previo) < _instante(EMISION_EVENTO)
    base_verificador["sembrar"]("005930.KS", EMISION_EVENTO, cierre_previo)
    resultado = senales.verificar_apertura_pendientes()
    estados, verificadas = base_verificador["leer"]()
    assert estados["005930.KS"] == senales.ESTADO_VERIFICADA
    assert verificadas == ["005930.KS"]
    assert resultado["verificadas"] == 1 and resultado["no_verificables"] == 0
    conn = _ro(senales.DB_PATH)
    gap, retorno = conn.execute(
        "SELECT gap_pct, retorno_real_pct FROM verificacion_apertura").fetchone()
    conn.close()
    assert (gap, retorno) == (-1.0, -2.0)


@pytest.mark.parametrize("available_at", [None, EMISION_EVENTO],
                         ids=["available_at NULL", "available_at == timestamp_utc"])
def test_la_guarda_no_dispara_con_available_at_nulo_ni_igual(base_verificador, available_at):
    """NULL no dispara. La IGUALDAD tampoco: es la rama del `except` de
    snapshot.py (available_at cayó al reloj de pared), que tiene su propia
    alerta en el vigía (acta §84.2). La guarda es de ORDEN estricto."""
    base_verificador["sembrar"]("005930.KS", EMISION_EVENTO, available_at)
    resultado = senales.verificar_apertura_pendientes()
    estados, verificadas = base_verificador["leer"]()
    assert estados["005930.KS"] == senales.ESTADO_VERIFICADA
    assert verificadas == ["005930.KS"]
    assert resultado["no_verificables"] == 0


def test_la_guarda_compara_instantes_y_no_texto(base_verificador):
    """`2026-09-28T16:00:00-04:00` ES las 20:00 UTC. Como TEXTO ordena antes
    que `2026-09-28T17:42:58…+00:00` y la inversión pasaría muda; como
    instante es posterior. La guarda compara datetimes con zona."""
    mismo_cierre_otro_huso = "2026-09-28T16:00:00-04:00"
    assert mismo_cierre_otro_huso < EMISION_EVENTO                # como texto
    assert _instante(mismo_cierre_otro_huso) > _instante(EMISION_EVENTO)
    base_verificador["sembrar"]("005930.KS", EMISION_EVENTO, mismo_cierre_otro_huso)
    resultado = senales.verificar_apertura_pendientes()
    estados, verificadas = base_verificador["leer"]()
    assert estados["005930.KS"] == senales.ESTADO_NO_VERIFICABLE
    assert verificadas == []
    assert resultado["no_verificables"] == 1


def test_la_guarda_solo_mira_filas_pendientes(base_verificador):
    """CORTE DE MÉTODO sobre datos sintéticos: una fila con la inversión que
    el verificador YA procesó (`verificada`) o que nunca tuvo estado no
    cambia. La guarda no tiene efecto retroactivo (acta §90.1: «la opción
    (a) con efecto retroactivo NO se firma»)."""
    base_verificador["sembrar"]("005930.KS", EMISION_EVENTO, CIERRE_EVENTO,
                                estado="verificada")
    base_verificador["sembrar"]("000660.KS", EMISION_EVENTO, CIERRE_EVENTO,
                                estado=None)
    resultado = senales.verificar_apertura_pendientes()
    estados, verificadas = base_verificador["leer"]()
    assert estados == {"005930.KS": "verificada", "000660.KS": None}
    assert verificadas == []
    assert resultado["no_verificables"] == 0 and resultado["verificadas"] == 0
    assert base_verificador["ohlc"].llamadas == []


def _volcado_del_evento(ruta: str) -> tuple:
    conn = _ro(ruta)
    try:
        senales_dia = conn.execute(
            "SELECT * FROM senales_ticker WHERE fecha = ? ORDER BY id",
            (FECHA_EVENTO,)).fetchall()
        verificaciones = conn.execute(
            "SELECT * FROM verificacion_apertura WHERE fecha_senal = ? ORDER BY id",
            (FECHA_EVENTO,)).fetchall()
    finally:
        conn.close()
    return senales_dia, verificaciones


@solo_con_base
def test_corte_de_metodo_las_filas_del_evento_no_se_tocan(monkeypatch, tmp_path):
    """CORTE DE MÉTODO sobre la historia real (acta §90.1 a): la guarda rige
    para filas `pendiente` al momento de correr. Las 24 filas del 28-sep ya
    fueron procesadas por el verificador del 29-sep (8 `verificada`, 16 sin
    estado) y conservan su estado byte a byte.

    El verificador NUEVO corre sobre una COPIA de la base en `tmp_path`; la
    base real se abre sólo para copiarla y para leerla en `mode=ro`."""
    real_antes = os.stat(BASE_REAL)
    senales_real, verif_real = _volcado_del_evento(BASE_REAL)
    if not senales_real:
        pytest.skip(f"la base no tiene filas selladas del {FECHA_EVENTO}")

    copia = str(tmp_path / "senales_copia.db")
    shutil.copy(BASE_REAL, copia)
    monkeypatch.setattr(senales, "DB_PATH", copia)
    _guardia_base_temporal(tmp_path)
    monkeypatch.setattr(senales, "_ohlc_local", lambda *a, **k: pd.DataFrame())

    antes = _volcado_del_evento(copia)
    assert repr(antes) == repr((senales_real, verif_real))   # la copia es la base
    # El test tiene sujeto: las filas que compara SON las de la inversión.
    en_el_dia = {(f, t) for f, t in _claves_invertidas_por_sql(copia)
                 if f == FECHA_EVENTO}
    assert len(en_el_dia) == len(antes[0]) > 0

    senales.verificar_apertura_pendientes()

    despues = _volcado_del_evento(copia)
    assert repr(despues) == repr(antes), "el verificador nuevo tocó filas ya procesadas"
    # y la base real no se enteró de nada
    real_despues = os.stat(BASE_REAL)
    assert (real_antes.st_size, real_antes.st_mtime_ns) == (
        real_despues.st_size, real_despues.st_mtime_ns)


# ============================================================
# 1.2 — Guarda (b): snapshot.py (acta §90.1 b)
# ============================================================
TICKERS = ["005930.KS", "2330.TW", "8035.T", "IFX.DE", "NVDA"]


class _RelojFalso(datetime):
    """`datetime.now()` fijo dentro de snapshot.py. Subclase de datetime:
    `fromisoformat` y las comparaciones siguen funcionando."""
    _instante = None

    @classmethod
    def now(cls, tz=None):
        return cls._instante if tz else cls._instante.replace(tzinfo=None)


class _FechaFalsa(date):
    _hoy = None

    @classmethod
    def today(cls):
        return cls._hoy


def _a_las_1815_de_chile(dia: str, segundos: int = 0) -> datetime:
    """El instante UTC del disparo del job (18:15 de Chile) de ese día,
    calculado con la base de husos y no con un desfase escrito a mano."""
    return datetime.combine(date.fromisoformat(dia), time(18, 15, segundos),
                            tzinfo=CHILE).astimezone(timezone.utc)


@pytest.fixture
def sellador(monkeypatch, tmp_path):
    """snapshot.py REAL con el motor reemplazado, el reloj inyectado por
    monkeypatch de `snapshot.datetime` / `snapshot.date` (ninguna firma
    cambia) y `senales.guardar_snapshot` convertido en espía."""
    monkeypatch.setattr(senales, "DB_PATH", str(tmp_path / "senales_sellador.db"))
    _guardia_base_temporal(tmp_path)
    monkeypatch.setattr(noticias, "sentimiento_promedio_por_ticker", lambda: {})
    monkeypatch.setattr(motor, "puntaje_v0_al",
                        lambda fecha: pd.DataFrame(
                            {"Ticker": TICKERS, "Puntaje v0": [0.1] * len(TICKERS)}))
    monkeypatch.setattr(motor, "regimen_al", lambda fecha: {"etiqueta": "test"})
    monkeypatch.setattr(motor, "roca_chip_al", lambda fecha: {"valor": 50.0})
    monkeypatch.setattr(motor, "divergencias_al", lambda fecha: [])
    monkeypatch.setattr(motor, "salud_datos_al",
                        lambda fecha: {"ok": True, "tickers_revisados": 0})
    monkeypatch.setattr(motor, "_datos_crudos",
                        lambda tickers: pytest.fail("el test llegó a la red"))
    monkeypatch.setattr(snapshot, "salud_descarga",
                        lambda fecha: {"ok_n": 28, "total": 28, "caidos": [],
                                       "completa": True})
    monkeypatch.setattr(senales, "ya_existe_snapshot_hoy", lambda: False)
    sellos = []

    def espia(**kw):
        sellos.append(kw)
        return True
    monkeypatch.setattr(senales, "guardar_snapshot", espia)

    def preparar(reloj_utc: datetime, sox_fecha):
        assert reloj_utc.tzinfo is not None
        _RelojFalso._instante = reloj_utc
        _FechaFalsa._hoy = reloj_utc.astimezone(CHILE).date()
        monkeypatch.setattr(snapshot, "datetime", _RelojFalso)
        monkeypatch.setattr(snapshot, "date", _FechaFalsa)

        def pred(fecha, ventana=motor.VENTANA_BETAS_DEFAULT, dias_earnings=None):
            return pd.DataFrame([{
                "Ticker": t, "Apertura estimada %": -1.0, "R2": 0.3,
                "Intervalo80 pp": 2.0, "N muestra": 120, "Beta de contagio": 0.5,
                "SOX usado %": -1.63, "SOX fecha": sox_fecha} for t in TICKERS])
        monkeypatch.setattr(motor, "prediccion_apertura_al", pred)

    def sellar(reloj_utc: datetime, sox_fecha) -> dict:
        preparar(reloj_utc, sox_fecha)
        return snapshot.ejecutar_snapshot("programado")

    return {"sellar": sellar, "preparar": preparar, "sellos": sellos}


def test_reproduccion_no_sella_con_la_sesion_del_sox_abierta(sellador):
    """REPRODUCCIÓN (falla sobre HEAD, que sella). Reloj a las 13:42 de
    Nueva York del lunes 28-sep-2026, `sox_fecha` de ese mismo día: la
    sesión no ha cerrado. No se sella, `guardar_snapshot` no se llama y el
    motivo lo dice en español llano."""
    reloj = datetime(2026, 9, 28, 13, 42, 58, 943983,
                     tzinfo=NUEVA_YORK).astimezone(timezone.utc)
    assert reloj.isoformat() == EMISION_EVENTO
    resultado = sellador["sellar"](reloj, FECHA_EVENTO)
    assert resultado["snapshot"] is False, (
        f"snapshot.py selló a las {reloj.isoformat()} con sox_fecha="
        f"{FECHA_EVENTO}, cuya sesión cierra a las {CIERRE_EVENTO}: "
        f"{resultado}")
    assert sellador["sellos"] == [], "guardar_snapshot fue llamado"
    motivo = resultado["motivo"]
    assert "no ha cerrado" in motivo
    assert FECHA_EVENTO in motivo             # sox_fecha
    assert CIERRE_EVENTO in motivo            # el cierre UTC
    assert EMISION_EVENTO in motivo           # la hora de emisión
    assert motivo != "sin datos de mercado"
    assert "sin datos de mercado" not in motivo


def test_sella_a_las_1815_de_chile_del_mismo_dia(sellador):
    """ASERCIÓN ESCRITA ANTES DEL CÓDIGO y no ajustada al resultado: a las
    18:15 de Chile del 28-sep (21:15 UTC) la sesión del 28 cerró hace 1 h
    15 min. SELLA. Si la guarda usara el margen de 2 h de
    `calendarios.sesion_ya_cerro`, este test sería rojo."""
    reloj = _a_las_1815_de_chile(FECHA_EVENTO, segundos=3)
    assert reloj.isoformat() == "2026-09-28T21:15:03+00:00"
    resultado = sellador["sellar"](reloj, FECHA_EVENTO)
    assert resultado["snapshot"] is True, resultado
    assert resultado["predicciones"] == len(TICKERS)
    assert len(sellador["sellos"]) == 1
    sello = sellador["sellos"][0]
    assert sello["available_at"] == CIERRE_EVENTO
    assert sello["timestamp_utc"] == reloj.isoformat()
    assert sello["fecha"] == FECHA_EVENTO
    assert sello["sox_fecha"] == FECHA_EVENTO


# Los cuatro cruces de huso del año entre Santiago y Nueva York. Las 18:15
# de Chile son las 22:15 UTC en el invierno de Chile y las 21:15 UTC en su
# verano; XNYS cierra a las 20:00 UTC en el verano de Nueva York y a las
# 21:00 UTC en su invierno. La holgura mínima del año es de 15 minutos.
CRUCES_DE_HUSO = [
    ("2026-07-15", "2026-07-15T20:00:00+00:00", "2026-07-15T22:15:00+00:00"),
    ("2026-01-15", "2026-01-15T21:00:00+00:00", "2026-01-15T21:15:00+00:00"),
    ("2026-03-16", "2026-03-16T20:00:00+00:00", "2026-03-16T21:15:00+00:00"),
    ("2026-11-05", "2026-11-05T21:00:00+00:00", "2026-11-05T21:15:00+00:00"),
]


@pytest.mark.parametrize("dia,cierre,disparo", CRUCES_DE_HUSO,
                         ids=[c[0] for c in CRUCES_DE_HUSO])
def test_sella_a_las_1815_de_chile_en_todos_los_husos_del_anio(sellador, dia, cierre, disparo):
    """A las 18:15:00 EN PUNTO de Chile —el peor caso— el job sella en los
    cuatro cruces de huso. Los literales se contrastan contra el calendario
    y la base de husos, para que el test no afirme una hora inventada."""
    assert calendarios.cierre_utc("XNYS", dia).isoformat() == cierre
    reloj = _a_las_1815_de_chile(dia)
    assert reloj.isoformat() == disparo
    resultado = sellador["sellar"](reloj, dia)
    assert resultado["snapshot"] is True, resultado
    assert sellador["sellos"][0]["available_at"] == cierre


def test_el_margen_cero_nunca_frena_al_job_y_el_de_dos_horas_si():
    """Por qué la condición es `available_at > emisión` con MARGEN CERO y no
    `calendarios.sesion_ya_cerro` (margen de 2 h): ese margen es criterio de
    VERIFICACIÓN, no de insumo (GEMELO/datos.py:57-59). Barrido de todas las
    sesiones de XNYS del año en curso y del siguiente (hasta donde llegue el
    calendario, que se extiende un año desde hoy) contra el disparo de las
    18:15 de Chile: el R2 del auditor de la corrida 15 pidió que el barrido no
    quedara clavado a 2026, porque la holgura mínima del ciclo (15 min) empieza
    el 2-nov-2026 y vuelve cada invierno de Nueva York."""
    cal = calendarios._calendario("XNYS")
    holguras = {}
    anio = date.today().year
    fin = min(pd.Timestamp(f"{anio + 1}-12-31"), pd.Timestamp(cal.last_session))
    for s in cal.sessions_in_range(f"{anio}-01-01", fin):
        dia = s.date().isoformat()
        holgura = _a_las_1815_de_chile(dia) - calendarios.cierre_utc("XNYS", dia)
        holguras[dia] = holgura.total_seconds() / 60
    assert len(holguras) > 240
    peor = min(holguras, key=holguras.get)
    assert holguras[peor] > 0, (
        f"el {peor} el job de las 18:15 dispara ANTES del cierre de XNYS: "
        f"la guarda (b) no sellaría un día normal")
    bajo_dos_horas = [d for d, m in holguras.items() if m < 120]
    assert bajo_dos_horas, "con margen de 2 h el job sellaría igual: revisar el dictamen"
    # Documentado, no clavado: hoy la holgura mínima es de 15 min y el margen
    # de 2 h apagaría el sello en más de la mitad de las sesiones del año.
    assert len(bajo_dos_horas) > len(holguras) / 2


def test_la_rama_del_except_sigue_sellando(sellador, monkeypatch, capsys):
    """Si `cierre_utc` falla, `available_at` queda IGUAL a la emisión (reloj
    de pared) y se sella como hoy: la guarda es de orden estricto. Esa rama
    tiene su propia alerta en el vigía (acta §84.2)."""
    def revienta(exchange, sesion):
        raise RuntimeError("calendario roto a propósito")
    monkeypatch.setattr(calendarios, "cierre_utc", revienta)
    reloj = _instante(EMISION_EVENTO)
    resultado = sellador["sellar"](reloj, FECHA_EVENTO)
    assert resultado["snapshot"] is True, resultado
    sello = sellador["sellos"][0]
    assert sello["available_at"] == sello["timestamp_utc"] == EMISION_EVENTO
    assert "AVISO ancla temporal" in capsys.readouterr().out


def test_sin_sox_fecha_sigue_sellando(sellador):
    reloj = _instante(EMISION_EVENTO)
    resultado = sellador["sellar"](reloj, None)
    assert resultado["snapshot"] is True, resultado
    sello = sellador["sellos"][0]
    assert sello["available_at"] == sello["timestamp_utc"] == EMISION_EVENTO


def test_el_motivo_nuevo_no_entra_al_bucle_de_reintentos(sellador, monkeypatch, capsys):
    """`main()` reintenta a los 20 y 40 min SÓLO ante «sin datos de
    mercado». Negarse a sellar porque la sesión no cerró no es una falla de
    descarga: reintentar no cierra una sesión. `main()` entera, con el
    reloj del evento: una sola llamada a `ejecutar_snapshot`, ningún sleep."""
    sellador["preparar"](_instante(EMISION_EVENTO), FECHA_EVENTO)
    monkeypatch.setattr(sys, "argv", ["snapshot.py"])
    monkeypatch.setattr(registro, "rotar_log", lambda *a, **k: None)
    monkeypatch.setattr(snapshot, "_epilogo_vigia", lambda: None)
    monkeypatch.setattr(senales, "verificar_pendientes",
                        lambda: ({"verificadas": 0}, 0))
    monkeypatch.setattr(snapshot, "respaldar_a_csv", lambda: [])
    esperas = []
    monkeypatch.setattr(snapshot.time, "sleep", lambda s: esperas.append(s))
    intentos = []
    original = snapshot.ejecutar_snapshot

    def contado(*a, **k):
        intentos.append((a, k))
        return original(*a, **k)
    monkeypatch.setattr(snapshot, "ejecutar_snapshot", contado)

    assert snapshot.main() == 0
    salida = capsys.readouterr().out
    assert "no ha cerrado" in salida, salida
    assert "la fuente no entregó datos" not in salida
    assert esperas == [], f"main() durmió {esperas} s: entró al bucle de reintentos"
    assert len(intentos) == 1
    assert sellador["sellos"] == []


def test_hallazgo_una_fuente_atrasada_pasa_la_guarda_y_sella(sellador):
    """HALLAZGO DOCUMENTADO, no corregido (va a tarjeta). El acta §90.1 (b)
    dice que con esta guarda «un día con la fuente atrasada deja de sellar
    en vez de sellar mal». La condición firmada para esta corrida
    (`available_at > emisión`) NO produce eso: si a las 18:15 de Chile del
    martes la fuente todavía entrega como último movimiento el del LUNES,
    `sox_fecha` es el lunes, su sesión cerró hace un día, la guarda pasa y
    se sella con insumo viejo. Este test fija el comportamiento para que
    el hueco tenga un número de línea y no viva en la memoria de nadie."""
    martes, lunes = "2026-09-29", "2026-09-28"
    assert calendarios.sesion_anterior("XNYS", martes) == lunes
    reloj = _a_las_1815_de_chile(martes, segundos=3)
    assert reloj > calendarios.cierre_utc("XNYS", martes)   # el martes YA cerró
    resultado = sellador["sellar"](reloj, lunes)
    assert resultado["snapshot"] is True, resultado
    sello = sellador["sellos"][0]
    assert sello["sox_fecha"] == lunes
    assert sello["available_at"] == CIERRE_EVENTO           # insumo de ayer


# ============================================================
# 1.3 — Exclusión (d): la capa de medición (acta §90.1 d)
# ============================================================
def _claves_invertidas_por_sql(ruta: str, solo_verificadas: bool = False) -> set:
    """El conjunto de referencia, por la consulta que usó el auditor."""
    conn = _ro(ruta)
    try:
        if solo_verificadas:
            filas = conn.execute(
                """SELECT s.fecha, s.ticker FROM senales_ticker s
                   JOIN verificacion_apertura v
                     ON v.fecha_senal = s.fecha AND v.ticker = s.ticker
                   WHERE s.available_at > s.timestamp_utc""").fetchall()
        else:
            filas = conn.execute(
                "SELECT fecha, ticker FROM senales_ticker "
                "WHERE available_at > timestamp_utc").fetchall()
    finally:
        conn.close()
    return set(filas)


@pytest.fixture
def base_medicion(monkeypatch, tmp_path):
    """Base sintética en `tmp_path` con el esquema real, leída por
    `backtest.linea_base` a través de su `RUTA_SENALES` (mode=ro)."""
    ruta = str(tmp_path / "senales_medicion.db")
    monkeypatch.setattr(senales, "DB_PATH", ruta)
    _guardia_base_temporal(tmp_path)
    senales.init_db()
    monkeypatch.setattr(lb, "RUTA_SENALES", ruta)
    monkeypatch.setattr(lb, "_MEMO_SESION", {})

    def sembrar(fecha, ticker, timestamp_utc, available_at, sesion, verificada=True):
        _guardia_base_temporal(tmp_path)
        conn = senales.get_connection()
        conn.execute(
            """INSERT INTO senales_ticker
               (fecha, ticker, puntaje_v0, apertura_estimada_pct, confianza_r2,
                timestamp_utc, exchange, sesion_objetivo, available_at, estado,
                intervalo80_pp, n_muestra, modelo_version, beta)
               VALUES (?, ?, 0.5, -1.0, 0.3, ?, 'XKRX', ?, ?, ?, 2.0, 120, ?, 0.5)""",
            (fecha, ticker, timestamp_utc, sesion, available_at,
             "verificada" if verificada else None, lb.MODELO_VERSION))
        if verificada:
            conn.execute(
                """INSERT INTO verificacion_apertura
                   (fecha_senal, ticker, apertura_estimada_pct, retorno_real_pct,
                    acierto_direccion, error_pp, gap_pct, acierto_gap,
                    error_gap_pp, verificado_en, modelo_version, legacy)
                   VALUES (?, ?, -1.0, -2.0, 1, 1.0, -1.5, 1, 0.5, ?, ?, 0)""",
                (fecha, ticker, f"{sesion}T21:15:14+00:00", lb.MODELO_VERSION))
        conn.commit()
        conn.close()

    return sembrar


def test_reproduccion_la_medicion_deja_fuera_la_fila_con_la_inversion(base_medicion):
    """REPRODUCCIÓN (falla sobre HEAD, que carga las dos). De dos filas
    verificadas, una con la inversión: `cargar()` trae sólo la otra."""
    base_medicion("2026-09-24", "005930.KS", "2026-09-24T21:15:04+00:00",
                  "2026-09-24T20:00:00+00:00", "2026-09-25")
    base_medicion(FECHA_EVENTO, "005930.KS", EMISION_EVENTO, CIERRE_EVENTO,
                  SESION_OBJETIVO_EVENTO)
    df = lb.cargar(dedup=False)
    fechas = sorted(df["fecha"].tolist())
    assert fechas == ["2026-09-24"], (
        f"la capa de medición cargó {fechas}: la fila del {FECHA_EVENTO} "
        f"declara su insumo conocible ({CIERRE_EVENTO}) después de emitida "
        f"({EMISION_EVENTO}) y entra a las métricas")
    assert sorted(lb.cargar()["fecha"].tolist()) == ["2026-09-24"]


@solo_con_base
def test_reproduccion_la_medicion_no_trae_filas_invertidas_de_la_base_real():
    """REPRODUCCIÓN sobre la historia real (falla sobre HEAD con las 8 del
    28-sep): ninguna fila que `cargar()` entrega está en el conjunto de la
    inversión."""
    invertidas = _claves_invertidas_por_sql(BASE_REAL, solo_verificadas=True)
    for dedup in (False, True):
        df = lb.cargar(dedup=dedup)
        cargadas = set(zip(df["fecha"], df["ticker"]))
        dentro = sorted(cargadas & invertidas)
        assert dentro == [], (
            f"cargar(dedup={dedup}) entrega {len(dentro)} filas con "
            f"available_at > timestamp_utc: {dentro}")


# Conteo esperado HOY, documentado y pinchado a su instante para que un
# sello nuevo no lo vuelva rojo: al 29-sep-2026 la regla alcanza 24 filas de
# `senales_ticker`, todas de una sola fecha, y 8 de ellas tienen fila en
# `verificacion_apertura` (las escribió el verificador del 29-sep a las
# 18:15, antes de la firma de las 18:29: acta §90). El test de conjunto
# contra conjunto, en cambio, corre sobre la base VIVA.
CORTE_CENSO_INVERSION = "2026-09-29"
CENSO_INVERSION = {"filas": 24, "fechas": 1, "con_verificacion": 8}


@solo_con_base
def test_A_la_exclusion_alcanza_exactamente_las_filas_de_la_consulta():
    """Test A. Conjunto contra conjunto: lo que la regla alcanza (comparando
    INSTANTES) es exactamente lo que devuelve la consulta del auditor
    (`WHERE available_at > timestamp_utc`, que compara TEXTO). Coinciden
    porque toda la historia está sellada en `+00:00`; si un día dejaran de
    coincidir, manda la comparación de instantes y este test lo dice."""
    alcanzadas = lb.filas_sin_conocibilidad()
    por_regla = set(zip(alcanzadas["fecha"], alcanzadas["ticker"]))
    por_sql = _claves_invertidas_por_sql(BASE_REAL)
    assert por_regla == por_sql, (
        f"sólo la regla: {sorted(por_regla - por_sql)}; "
        f"sólo la consulta: {sorted(por_sql - por_regla)}")
    verificadas = set(zip(alcanzadas.loc[alcanzadas["con_verificacion"], "fecha"],
                          alcanzadas.loc[alcanzadas["con_verificacion"], "ticker"]))
    assert verificadas == _claves_invertidas_por_sql(BASE_REAL, solo_verificadas=True)

    al_corte = alcanzadas[alcanzadas["fecha"] <= CORTE_CENSO_INVERSION]
    assert len(al_corte) == CENSO_INVERSION["filas"]
    assert al_corte["fecha"].nunique() == CENSO_INVERSION["fechas"]
    assert int(al_corte["con_verificacion"].sum()) == CENSO_INVERSION["con_verificacion"]

    aud = lb.auditar_conocibilidad()
    assert aud["filas_alcanzadas"] == len(alcanzadas)
    assert aud["con_verificacion_apertura"] == len(verificadas)
    assert aud["fechas"] == sorted(alcanzadas["fecha"].unique().tolist())


def test_B_sin_inversiones_la_exclusion_alcanza_cero(base_medicion):
    """Test B. Base sintética sin inversiones —incluida una fila con
    `available_at` IGUAL a la emisión, la rama del `except`—: alcanza 0 y
    `cargar()` entrega todo."""
    base_medicion("2026-09-23", "005930.KS", "2026-09-23T21:15:03+00:00",
                  "2026-09-23T20:00:00+00:00", "2026-09-24")
    base_medicion("2026-09-24", "005930.KS", "2026-09-24T21:15:04+00:00",
                  "2026-09-24T21:15:04+00:00", "2026-09-25")
    base_medicion("2026-09-24", "MU", "2026-09-24T21:15:04+00:00",
                  "2026-09-24T20:00:00+00:00", None, verificada=False)
    assert len(lb.filas_sin_conocibilidad()) == 0
    aud = lb.auditar_conocibilidad()
    assert aud["filas_alcanzadas"] == 0 and aud["fechas"] == []
    assert len(lb.cargar(dedup=False)) == 2
    assert len(lb.cargar(dedup=False, conocibilidad=False)) == 2


def test_la_exclusion_corre_antes_que_la_deduplicacion(base_medicion, monkeypatch):
    """Una fila con la inversión está fuera de TODA métrica: tampoco
    arbitra un par. Si la deduplicación corriera primero, la fila inválida
    podría ganarle el par a una válida y después caer ella, y se perderían
    las dos. El orden es exclusión primero."""
    base_medicion(FECHA_EVENTO, "005930.KS", EMISION_EVENTO, CIERRE_EVENTO,
                  SESION_OBJETIVO_EVENTO)
    base_medicion("2026-09-25", "005930.KS", "2026-09-25T21:15:04+00:00",
                  "2026-09-25T20:00:00+00:00", SESION_OBJETIVO_EVENTO)
    # La inválida «calza» y la válida no: el peor caso para el orden.
    monkeypatch.setattr(
        lb, "sesion_correcta",
        lambda ex, av: SESION_OBJETIVO_EVENTO if av == CIERRE_EVENTO else "2026-09-28")
    df = lb.cargar()
    assert df["fecha"].tolist() == ["2026-09-25"]


def test_la_exclusion_esta_activa_por_defecto_y_no_nombra_fechas():
    """El criterio firmado es POR REGLA, no por fecha: el código de la capa
    de medición no nombra el día del evento."""
    assert lb.CONOCIBILIDAD_OFICIAL is True
    fuente = open(lb.__file__, encoding="utf-8").read()
    for prohibido in (FECHA_EVENTO, "28-sep", "28 de sep"):
        assert prohibido not in fuente, f"linea_base.py nombra {prohibido!r}"
    assert "§90.1" in fuente


@solo_con_base
def test_la_exclusion_no_mueve_ninguna_ventana_congelada():
    """Ninguna cifra publicada cambia: las filas que la regla alcanza son
    posteriores a los tres instantes pinchados (la §2, la regla firmada y
    el corte del README), así que en esas ventanas la rama con exclusión y
    la rama sin ella entregan EXACTAMENTE las mismas filas."""
    import cifras
    for corte in (lb.CORTE_SECCION_2, lb.CORTE_REGLA_FIRMADA, cifras.CORTE_README):
        for dedup in (False, True):
            con = lb.cargar(hasta_sello=corte, dedup=dedup)
            sin = lb.cargar(hasta_sello=corte, dedup=dedup, conocibilidad=False)
            assert len(con) > 0
            assert con.reset_index(drop=True).equals(sin.reset_index(drop=True)), (
                f"la exclusión movió la ventana congelada {corte} (dedup={dedup})")


@solo_con_base
def test_el_informe_declara_la_exclusion_con_su_contador():
    """La exclusión queda a la vista en lo que el módulo publica, con el
    contador de filas alcanzadas, como ya se hace con la deduplicación."""
    aud = lb.auditar_conocibilidad()
    texto = lb.componer_informe(lb.cargar(), lb.CONVENCION_OFICIAL)
    assert "## La regla de conocibilidad, aplicada" in texto
    assert "available_at > timestamp_utc" in texto
    assert f"| Filas de `senales_ticker` alcanzadas | **{aud['filas_alcanzadas']}** |" in texto
    assert (f"| De ellas, con fila en `verificacion_apertura` | "
            f"**{aud['con_verificacion_apertura']}** |") in texto


# ============================================================
# 1.4 — Las dos anclas de `sesion_objetivo` sobre la historia sellada
# ============================================================
# El acta §84.1 (8-sep-2026) ancló la sesión objetivo en `available_at`. El
# acta §90.2 (29-sep-2026) firma volver a anclar en el instante de EMISIÓN.
# El encargo de la corrida 15 condiciona el cambio: si sobre la historia
# sellada las dos anclas dan sesiones distintas en ALGUNA fila, la línea de
# snapshot.py NO se toca y la tabla de diferencias va a Nicolás.
#
# MEDIDO el 29-sep-2026: las dos anclas DIFIEREN en 33 filas de 5 fechas.
# El punto 1.4 quedó DETENIDO y snapshot.py sigue anclando en
# `available_at`. Este test NO autoriza nada: fija la medición, pinchada a
# su instante, para que quien decida la tenga reproducible.
CORTE_HISTORIA_ANCLAS = "2026-09-29"
DIFERENCIAS_ENTRE_ANCLAS = {
    "2026-07-05": 8,   # sello de domingo con el SOX del jueves 2 (feriado el 3)
    "2026-07-29": 7,   # sello tardío, 01:23 UTC del 30: Asia ya había abierto
    "2026-08-03": 3,   # sello tardío, 02:57 UTC del 4
    "2026-08-05": 7,   # sello tardío, 01:38 UTC del 6
    "2026-09-07": 8,   # feriado de NYSE (Labor Day): el SOX usado es del viernes 4
}


def _sesion_con_ancla(exchange: str, instante: str):
    return calendarios.proxima_sesion_despues_de(exchange, _instante(instante))[0]


def _historia_con_las_dos_anclas() -> pd.DataFrame:
    conn = _ro(BASE_REAL)
    try:
        df = pd.read_sql_query(
            """SELECT fecha, ticker, exchange, timestamp_utc, available_at,
                      sesion_objetivo, estado
               FROM senales_ticker
               WHERE sesion_objetivo IS NOT NULL AND timestamp_utc IS NOT NULL
                 AND available_at IS NOT NULL
                 AND (estado IS NULL OR estado != ?)
                 AND fecha <= ?
               ORDER BY fecha, ticker""",
            conn, params=[senales.ESTADO_LEGACY, CORTE_HISTORIA_ANCLAS])
    finally:
        conn.close()
    df["sesion_ancla_available_at"] = [
        _sesion_con_ancla(e, a) for e, a in zip(df["exchange"], df["available_at"])]
    df["sesion_ancla_emision"] = [
        _sesion_con_ancla(e, t) for e, t in zip(df["exchange"], df["timestamp_utc"])]
    df["inversion"] = [
        _instante(a) > _instante(t)
        for a, t in zip(df["available_at"], df["timestamp_utc"])]
    return df


@solo_con_base
def test_historia_las_dos_anclas_difieren_y_por_eso_la_linea_no_se_toco():
    df = _historia_con_las_dos_anclas()
    if df.empty:
        pytest.skip("la base no tiene historia sellada con sesión objetivo")
    difieren = df[df["sesion_ancla_available_at"] != df["sesion_ancla_emision"]]
    por_fecha = difieren.groupby("fecha").size().to_dict()
    assert por_fecha == DIFERENCIAS_ENTRE_ANCLAS, (
        "la medición del 29-sep-2026 cambió:\n"
        + difieren.to_string(index=False))
    # En las 33, la sesión SELLADA es la del ancla de emisión: o son
    # anteriores al parche del §84.1 (8-sep-2026), o son del día anterior.
    assert (difieren["sesion_objetivo"] == difieren["sesion_ancla_emision"]).all()
    assert difieren["fecha"].max() < "2026-09-08"
    # Y en toda la historia al corte, el ancla de emisión reproduce la
    # sesión sellada fila por fila; la de `available_at`, no.
    assert (df["sesion_objetivo"] == df["sesion_ancla_emision"]).all()
    assert int((df["sesion_objetivo"] != df["sesion_ancla_available_at"]).sum()) == 33
    # Las filas con la inversión, aparte: en ellas las dos anclas coinciden
    # («coincidencia de esa fecha, no garantía», acta §90.2).
    invertidas = df[df["inversion"]]
    assert len(invertidas) == 8 and set(invertidas["fecha"]) == {FECHA_EVENTO}
    assert (invertidas["sesion_ancla_available_at"]
            == invertidas["sesion_ancla_emision"]).all()
