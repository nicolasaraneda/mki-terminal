# ============================================================
# tests/test_vigia_16_1.py — el único toque al vigía de la corrida 16-1
# (10-oct-2026), con tres cambios firmados y uno de ledger:
#
#   B.1 Negativa declarada contra falla (acta §93.8 d). Si snapshot.py no
#       selló y en snapshot.log hay una negativa con su línea fija (bloque
#       A o guarda (b) de §90.1), el vigía dice «NO sellado por negativa
#       declarada: <motivo>» y NO lo cuenta como falla; sin negativa sigue
#       siendo falla. La alerta de negativa tiene epílogo: el re-chequeo de
#       las 20:30 cierra el caso con un mensaje, haya sello o no.
#   B.2 Los dos chequeos del ancla temporal (acta §93.9): `av == ts` (rama
#       del except, como hoy) Y `av > ts` (inversión, texto propio).
#   B.3 El predicado de la guarda de `verificacion_puntaje` (acta §95.2
#       R3): recomputado en `mode=ro`, informado; alerta sólo si una fila
#       invertida está DENTRO de la tabla o si aparece una fecha nueva.
#   D   `chequear_noticias` trata «0 analizados con error» como falla
#       (§93.3 ii; los tests del ledger están en test_noticias_ledger.py).
#
# Todo sintético: DB, marcador y logs en tmp_path; Telegram capturado
# (fixture `entorno` de tests/test_vigia.py). Ningún test manda un
# Telegram real ni toca senales.db. Cero intentos del DSR.
# ============================================================

import inspect
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import costos  # noqa: E402
import mki_vigia  # noqa: E402
import senales  # noqa: E402
import snapshot  # noqa: E402
from test_vigia import (  # noqa: E402,F401  (la fixture se registra al importarla)
    HOY, TS_TARDIO, _sellar_hoy, entorno)

AYER = HOY - timedelta(days=1)


def _cabecera(dia: date, hora_utc: str = "21:15:01") -> str:
    return (f"[{dia.isoformat()}T{hora_utc}.000000+00:00] snapshot.py "
            "(origen=programado, modelo=4.6.0, plataforma=5.1.0)\n")


def _linea_negativa(codigo: str, dia: date, sox_fecha: date, texto: str) -> str:
    return (f"  {snapshot.MARCA_NEGATIVA} [{codigo}] fecha={dia.isoformat()} "
            f"sox_fecha={sox_fecha.isoformat()}: {texto}\n")


def _escribir_log(lineas: str) -> None:
    with open(mki_vigia.RUTA_SNAPSHOT_LOG, "w", encoding="utf-8") as f:
        f.write(lineas)


def _log_con_negativa(codigo=None, dia=HOY, sox_fecha=AYER):
    codigo = codigo or snapshot.NEGATIVA_FRESCURA
    _escribir_log(_cabecera(dia)
                  + _linea_negativa(codigo, dia, sox_fecha,
                                    f"hoy {dia} es sesión de XNYS y el SOX es de {sox_fecha}")
                  + "  snapshot: {'snapshot': False, 'negativa': '" + codigo + "'}\n")


# ------------------------------------------------------------
# B.1 — leer la negativa del log
# ------------------------------------------------------------
def test_sin_log_no_hay_negativa(entorno):
    assert mki_vigia._negativa_declarada_en_log(HOY) is None


def test_lee_la_negativa_del_bloque_de_hoy(entorno):
    _log_con_negativa()
    n = mki_vigia._negativa_declarada_en_log(HOY)
    assert n["codigo"] == snapshot.NEGATIVA_FRESCURA
    assert n["fecha"] == HOY.isoformat() and n["sox_fecha"] == AYER.isoformat()
    assert AYER.isoformat() in n["texto"]


def test_la_negativa_de_ayer_no_vale_para_hoy(entorno):
    _log_con_negativa(dia=AYER, sox_fecha=AYER - timedelta(days=1))
    assert mki_vigia._negativa_declarada_en_log(HOY) is None


def test_un_bloque_posterior_sin_negativa_la_anula(entorno):
    """Si después de la negativa hubo OTRA corrida de hoy que no la declaró
    (y tampoco selló, porque el vigía sólo pregunta cuando no hay sello),
    manda la última corrida: sin negativa, es falla."""
    codigo = snapshot.NEGATIVA_FRESCURA
    _escribir_log(_cabecera(HOY)
                  + _linea_negativa(codigo, HOY, AYER, "fuente atrasada")
                  + _cabecera(HOY, "22:40:00")
                  + "  snapshot: {'snapshot': False, 'motivo': 'sin datos de mercado'}\n")
    assert mki_vigia._negativa_declarada_en_log(HOY) is None


def test_reconoce_la_negativa_de_la_guarda_b(entorno):
    _log_con_negativa(codigo=snapshot.NEGATIVA_SESION_ABIERTA, sox_fecha=HOY)
    n = mki_vigia._negativa_declarada_en_log(HOY)
    assert n["codigo"] == snapshot.NEGATIVA_SESION_ABIERTA and n["sox_fecha"] == HOY.isoformat()


# ------------------------------------------------------------
# B.1 — los chequeos
# ------------------------------------------------------------
def test_chequeo_snapshot_sin_sello_y_sin_negativa_sigue_siendo_falla(entorno):
    assert mki_vigia.chequear_snapshot(HOY) == (False, "snapshot: NO se selló hoy")


def test_chequeo_snapshot_con_negativa_no_es_falla_y_lo_dice(entorno):
    _log_con_negativa()
    ok, detalle = mki_vigia.chequear_snapshot(HOY)
    assert ok is True
    assert detalle.startswith(mki_vigia.PREFIJO_NEGATIVA)
    assert "NO sellado por negativa declarada" in detalle
    assert snapshot.NEGATIVA_FRESCURA in detalle and AYER.isoformat() in detalle


def test_chequeo_snapshot_con_sello_ignora_el_log(entorno):
    _log_con_negativa()
    _sellar_hoy(TS_TARDIO)
    ok, detalle = mki_vigia.chequear_snapshot(HOY)
    assert ok and detalle.startswith("snapshot: sellado")


def test_chequeo_descarga_sin_snapshot_distingue_la_negativa(entorno):
    assert mki_vigia.chequear_descarga(HOY) == (False, "descarga: sin snapshot que revisar")
    _log_con_negativa()
    ok, detalle = mki_vigia.chequear_descarga(HOY)
    assert ok and "negativa declarada" in detalle


# ------------------------------------------------------------
# B.1 — el pase de las 19:00 con negativa: mensaje propio y marcador
# ------------------------------------------------------------
@pytest.fixture
def todo_lo_demas_ok(monkeypatch):
    monkeypatch.setattr(mki_vigia, "chequear_noticias", lambda: (True, "noticias: ok · 10 analizados · 0.0100 USD"))
    monkeypatch.setattr(mki_vigia, "chequear_reporte", lambda: (True, "reporte: enviado hoy"))
    monkeypatch.setattr(mki_vigia, "chequear_backup", lambda: (True, "backup: commit de hoy presente"))
    monkeypatch.setattr(mki_vigia, "_hay_proceso_snapshot", lambda: False)
    monkeypatch.setattr(mki_vigia, "rotar_log_vigia", lambda: None)


def test_pase_con_negativa_manda_un_mensaje_propio_y_deja_marcador(entorno, todo_lo_demas_ok):
    _log_con_negativa()
    assert mki_vigia.revision(HOY) == 0
    assert len(entorno) == 1
    texto = entorno[0]
    assert "NO sellado por negativa declarada" in texto
    assert snapshot.NEGATIVA_FRESCURA in texto
    assert "no es falla" in texto
    assert "re-chequeo a las 20:30" in texto
    assert "Falló hoy" not in texto          # ninguna falla: la descarga también está cubierta
    assert "🛑" not in texto                  # no es la alerta roja
    p = mki_vigia._leer_pendiente(HOY)
    assert p is not None and p["negativa"]["codigo"] == snapshot.NEGATIVA_FRESCURA


def test_pase_sin_negativa_sigue_siendo_la_alerta_roja(entorno, todo_lo_demas_ok):
    assert mki_vigia.revision(HOY) == 0
    assert len(entorno) == 1
    assert "🛑" in entorno[0] and "snapshot: NO se selló hoy" in entorno[0]
    assert "negativa" not in entorno[0]
    p = mki_vigia._leer_pendiente(HOY)
    assert p is not None and p.get("negativa") is None


def test_pase_con_negativa_y_otra_falla_las_separa(entorno, todo_lo_demas_ok, monkeypatch):
    _log_con_negativa()
    monkeypatch.setattr(mki_vigia, "chequear_reporte", lambda: (False, "reporte: NO hay envío registrado hoy"))
    assert mki_vigia.revision(HOY) == 0
    texto = entorno[0]
    assert "NO sellado por negativa declarada" in texto
    assert "Falló hoy" in texto and "reporte: NO hay envío" in texto
    assert "OK:" in texto and "snapshot" not in texto.split("OK:")[1]


def test_pase_todo_ok_sigue_en_silencio(entorno, todo_lo_demas_ok):
    _sellar_hoy(TS_TARDIO)
    assert mki_vigia.revision(HOY) == 0
    assert entorno == []
    assert mki_vigia._leer_pendiente(HOY) is None


# ------------------------------------------------------------
# B.1 — el epílogo de las 20:30 cierra el caso, haya sello o no
# ------------------------------------------------------------
def test_rechequeo_con_negativa_y_sin_sello_cierra_el_caso(entorno, monkeypatch):
    monkeypatch.setattr(mki_vigia, "_hay_proceso_snapshot", lambda: False)
    mki_vigia._escribir_pendiente(HOY, [], False,
                                  negativa={"codigo": snapshot.NEGATIVA_FRESCURA,
                                            "texto": "fuente atrasada"})
    assert mki_vigia.rechequeo(HOY) == 0
    assert len(entorno) == 1
    texto = entorno[0]
    assert "sigue sin sellar" in texto and "negativa declarada" in texto
    assert "caso cerrado" in texto.lower()
    assert "llegará la retractación" not in texto       # la promesa de la rama de falla
    assert "no habrá retractación" not in texto         # BL3: tampoco se promete lo contrario
    assert "20:30" not in texto or "a las " in texto    # hora real, no el literal
    # BL3 del dictamen 16-1: el marcador QUEDA. Un sello manual posterior
    # retracta por `_epilogo_vigia`, y ningún mensaje queda contradicho.
    assert mki_vigia._leer_pendiente(HOY) is not None


def test_tras_el_cierre_de_caso_un_sello_manual_retracta(entorno, monkeypatch):
    """BL3: la secuencia completa. 20:30 sin sello (caso cerrado por hoy),
    después un sello manual: `snapshot._epilogo_vigia()` encuentra el
    marcador y envía la retractación."""
    monkeypatch.setattr(mki_vigia, "_hay_proceso_snapshot", lambda: False)
    mki_vigia._escribir_pendiente(HOY, [], False,
                                  negativa={"codigo": snapshot.NEGATIVA_FRESCURA,
                                            "texto": "fuente atrasada"})
    assert mki_vigia.rechequeo(HOY) == 0
    _sellar_hoy(TS_TARDIO)
    snapshot._epilogo_vigia()
    assert len(entorno) == 2 and "recuperado: snapshot sellado" in entorno[1]
    assert mki_vigia._leer_pendiente(HOY) is None


def test_rechequeo_con_negativa_y_sello_tardio_retracta(entorno):
    _sellar_hoy(TS_TARDIO)
    mki_vigia._escribir_pendiente(HOY, [], False,
                                  negativa={"codigo": snapshot.NEGATIVA_FRESCURA,
                                            "texto": "fuente atrasada"})
    assert mki_vigia.rechequeo(HOY) == 0
    assert len(entorno) == 1 and "recuperado: snapshot sellado" in entorno[0]
    assert mki_vigia._leer_pendiente(HOY) is None


def test_rechequeo_sin_negativa_conserva_la_conducta_de_5_0_1(entorno, monkeypatch):
    monkeypatch.setattr(mki_vigia, "_hay_proceso_snapshot", lambda: False)
    mki_vigia._escribir_pendiente(HOY, ["snapshot: NO se selló hoy"], False)
    assert mki_vigia.rechequeo(HOY) == 0
    assert "sigue sin sellar" in entorno[0] and "llegará la retractación" in entorno[0]
    assert mki_vigia._leer_pendiente(HOY) is not None   # el marcador queda


def test_rechequeo_con_negativa_pero_proceso_vivo_no_cierra(entorno, monkeypatch):
    """Caso raro (una corrida manual en curso a las 20:30): no se cierra lo
    que todavía puede sellar; se informa y el marcador queda."""
    monkeypatch.setattr(mki_vigia, "_hay_proceso_snapshot", lambda: True)
    mki_vigia._escribir_pendiente(HOY, [], True,
                                  negativa={"codigo": snapshot.NEGATIVA_FRESCURA,
                                            "texto": "fuente atrasada"})
    assert mki_vigia.rechequeo(HOY) == 0
    assert "reintentos aún activos" in entorno[0]
    assert mki_vigia._leer_pendiente(HOY) is not None


def test_el_marcador_viejo_sin_campo_negativa_se_lee_igual(entorno):
    """Compatibilidad: un marcador escrito por la versión anterior (sin la
    clave) no rompe nada."""
    import json
    with open(mki_vigia.RUTA_PENDIENTE, "w", encoding="utf-8") as f:
        json.dump({"fecha": HOY.isoformat(), "creado_utc": "x",
                   "fallas": ["snapshot: NO se selló hoy"], "reintentos_activos": False}, f)
    p = mki_vigia._leer_pendiente(HOY)
    assert p is not None and p.get("negativa") is None


# ------------------------------------------------------------
# B.2 — ancla temporal: igualdad Y orden
# ------------------------------------------------------------
def _filas_hoy(filas) -> None:
    senales.init_db()
    conn = senales.get_connection()
    for ticker, ts, av in filas:
        conn.execute("""INSERT INTO senales_ticker
                        (fecha, ticker, apertura_estimada_pct, timestamp_utc, available_at)
                        VALUES (?, ?, 1.0, ?, ?)""", (HOY.isoformat(), ticker, ts, av))
    conn.commit()
    conn.close()


TS = f"{HOY.isoformat()}T21:15:00+00:00"
AV_ANTES = f"{HOY.isoformat()}T20:00:00+00:00"
AV_DESPUES = f"{HOY.isoformat()}T23:00:00+00:00"


def test_ancla_sin_filas(entorno):
    ok, d = mki_vigia.chequear_ancla_temporal(HOY)
    assert ok and "sin predicciones" in d


def test_ancla_orden_correcto_es_ok(entorno):
    _filas_hoy([("NVDA", TS, AV_ANTES), ("MU", TS, AV_ANTES)])
    ok, d = mki_vigia.chequear_ancla_temporal(HOY)
    assert ok and "2/2" in d


@pytest.mark.parametrize("av", [None, TS], ids=["NULL", "igual"])
def test_ancla_la_rama_del_except_sigue_alertando(entorno, av):
    _filas_hoy([("NVDA", TS, av), ("MU", TS, AV_ANTES)])
    ok, d = mki_vigia.chequear_ancla_temporal(HOY)
    assert not ok
    assert "reloj de pared" in d and "1/2" in d and "NVDA" in d
    assert "POSTERIOR" not in d


def test_ancla_la_inversion_alerta_con_texto_propio(entorno):
    """El caso del 28-sep: `available_at` 2 h 17 min POSTERIOR a
    `timestamp_utc`; el vigía decía «OK ancla temporal». Ahora falla con un
    texto distinto del de la rama del except."""
    _filas_hoy([("NVDA", TS, AV_DESPUES), ("MU", TS, AV_DESPUES), ("TSM", TS, AV_ANTES)])
    ok, d = mki_vigia.chequear_ancla_temporal(HOY)
    assert not ok
    assert "POSTERIOR" in d and "2/3" in d and "NVDA" in d and "MU" in d
    assert "reloj de pared" not in d


def test_ancla_compara_instantes_y_no_texto(entorno):
    """El mismo instante posterior, escrito en otro huso, ordena ANTES como
    texto: la comparación es de datetimes con zona."""
    posterior_en_otro_huso = datetime.fromisoformat(AV_DESPUES).astimezone(
        timezone(timedelta(hours=-4))).isoformat()
    assert posterior_en_otro_huso < TS                                     # como texto
    _filas_hoy([("NVDA", TS, posterior_en_otro_huso)])
    ok, d = mki_vigia.chequear_ancla_temporal(HOY)
    assert not ok and "POSTERIOR" in d


def test_ancla_una_marca_ilegible_es_falla_y_no_excepcion(entorno):
    """BL2 del dictamen 16-1: un `available_at` no parseable no puede tirar
    el pase y dejar mudo al vigía; es FALLA con texto propio."""
    _filas_hoy([("NVDA", TS, "no-es-una-fecha"), ("MU", TS, AV_ANTES)])
    ok, d = mki_vigia.chequear_ancla_temporal(HOY)
    assert not ok and "ILEGIBLES" in d and "NVDA" in d and "1/2" in d


def test_ancla_cadena_vacia_es_reloj_de_pared(entorno):
    _filas_hoy([("NVDA", TS, "")])
    ok, d = mki_vigia.chequear_ancla_temporal(HOY)
    assert not ok and "reloj de pared" in d and "ILEGIBLES" not in d


def test_ancla_las_dos_ramas_a_la_vez_nombran_las_dos(entorno):
    _filas_hoy([("NVDA", TS, TS), ("MU", TS, AV_DESPUES), ("TSM", TS, AV_ANTES)])
    ok, d = mki_vigia.chequear_ancla_temporal(HOY)
    assert not ok
    assert "reloj de pared" in d and "POSTERIOR" in d
    assert "NVDA" in d and "MU" in d


# ------------------------------------------------------------
# B.3 — el predicado de la guarda de verificacion_puntaje, en mode=ro
# ------------------------------------------------------------
def _sembrar_puntaje(fecha: str, ticker: str, ts: str, av, estado=None,
                     en_verificacion: bool = False) -> None:
    senales.init_db()
    conn = senales.get_connection()
    conn.execute("""INSERT INTO senales_ticker
                    (fecha, ticker, puntaje_ia, timestamp_utc, available_at, estado)
                    VALUES (?, ?, 0.3, ?, ?, ?)""", (fecha, ticker, ts, av, estado))
    if en_verificacion:
        conn.execute("""INSERT INTO verificacion_puntaje
                        (fecha_senal, ticker, puntaje_ia, retorno_5d_pct, verificado_en)
                        VALUES (?, ?, 0.3, 1.0, 'x')""", (fecha, ticker))
    conn.commit()
    conn.close()


VIEJA = (HOY - timedelta(days=mki_vigia.DIAS_INVERSION_RECIENTE + 10)).isoformat()
RECIENTE = (HOY - timedelta(days=3)).isoformat()


def _inv(fecha: str) -> tuple:
    return f"{fecha}T17:42:00+00:00", f"{fecha}T20:00:00+00:00"   # av > ts


def _sana(fecha: str) -> tuple:
    return f"{fecha}T21:15:00+00:00", f"{fecha}T20:00:00+00:00"   # av < ts


def test_guarda_puntaje_sin_filas_invertidas(entorno):
    _sembrar_puntaje(VIEJA, "NVDA", *_sana(VIEJA))
    ok, d = mki_vigia.chequear_guarda_puntaje(HOY)
    assert ok and d.startswith("guarda puntaje:") and "0 fila" in d


def test_guarda_puntaje_informa_el_residuo_conocido_sin_alertar(entorno):
    """Las filas invertidas de una fecha vieja, fuera de la tabla: es el
    estado esperado y estable (hoy, las 24 del 28-sep). Se informa con
    cuenta y fechas, sin alerta."""
    for t in ("NVDA", "MU", "TSM"):
        _sembrar_puntaje(VIEJA, t, *_inv(VIEJA))
    _sembrar_puntaje(VIEJA, "AMD", *_sana(VIEJA), en_verificacion=True)
    ok, d = mki_vigia.chequear_guarda_puntaje(HOY)
    assert ok, d
    assert "3 fila(s)" in d and f"{VIEJA}: 3" in d and "fuera" in d
    assert "0 dentro" in d


def test_guarda_puntaje_alerta_si_una_invertida_esta_dentro(entorno):
    """La guarda de la 16a fue vencida: una fila invertida llegó a
    `verificacion_puntaje`. Falla siempre, sea de la fecha que sea."""
    _sembrar_puntaje(VIEJA, "NVDA", *_inv(VIEJA), en_verificacion=True)
    _sembrar_puntaje(VIEJA, "MU", *_inv(VIEJA))
    ok, d = mki_vigia.chequear_guarda_puntaje(HOY)
    assert not ok
    assert "DENTRO" in d and "1" in d and VIEJA in d


def test_guarda_puntaje_alerta_con_una_fecha_nueva(entorno):
    """Una inversión reciente es un evento nuevo (las guardas de §90.1 b
    debían impedirlo): alerta aunque esté fuera de la tabla."""
    _sembrar_puntaje(VIEJA, "NVDA", *_inv(VIEJA))
    _sembrar_puntaje(RECIENTE, "MU", *_inv(RECIENTE))
    ok, d = mki_vigia.chequear_guarda_puntaje(HOY)
    assert not ok
    assert "NUEVA" in d and RECIENTE in d


def test_guarda_puntaje_ignora_legacy_null_e_igualdad(entorno):
    _sembrar_puntaje(VIEJA, "NVDA", *_inv(VIEJA), estado=senales.ESTADO_LEGACY)
    _sembrar_puntaje(VIEJA, "MU", f"{VIEJA}T21:15:00+00:00", None)
    _sembrar_puntaje(VIEJA, "TSM", f"{VIEJA}T21:15:00+00:00", f"{VIEJA}T21:15:00+00:00")
    ok, d = mki_vigia.chequear_guarda_puntaje(HOY)
    assert ok and "0 fila" in d


def test_guarda_puntaje_compara_instantes_y_no_texto(entorno):
    ts = f"{VIEJA}T21:15:00+00:00"
    av = datetime.fromisoformat(f"{VIEJA}T23:00:00+00:00").astimezone(
        timezone(timedelta(hours=-4))).isoformat()
    assert av < ts
    _sembrar_puntaje(VIEJA, "NVDA", ts, av)
    ok, d = mki_vigia.chequear_guarda_puntaje(HOY)
    assert ok and "1 fila(s)" in d


def test_guarda_puntaje_una_marca_ilegible_es_falla_y_no_excepcion(entorno):
    """BL2 del dictamen 16-1."""
    _sembrar_puntaje(VIEJA, "NVDA", f"{VIEJA}T21:15:00+00:00", "no-es-una-fecha")
    _sembrar_puntaje(VIEJA, "MU", *_inv(VIEJA))
    ok, d = mki_vigia.chequear_guarda_puntaje(HOY)
    assert not ok and "ILEGIBLES" in d and f"{VIEJA}: 1" in d
    assert "1 invertida(s) fuera" in d


def test_guarda_puntaje_cadena_vacia_es_sin_dato_como_en_el_verificador(entorno):
    _sembrar_puntaje(VIEJA, "NVDA", f"{VIEJA}T21:15:00+00:00", "")
    ok, d = mki_vigia.chequear_guarda_puntaje(HOY)
    assert ok and "0 fila" in d


def test_los_dos_predicados_coinciden_sobre_la_misma_siembra(entorno, monkeypatch):
    """R1 del dictamen 16-1 (S3): el predicado está escrito dos veces —en el
    verificador y en el vigía— y este test los ata. Misma base: la cuenta
    y las fechas que `verificar_puntaje_pendientes` declara excluidas son
    exactamente las del vigía restringidas a la ventana de 7 días del
    verificador. Red reemplazada por un marco vacío: nada se escribe."""
    import pandas as pd
    monkeypatch.setattr(senales, "_ohlc_local", lambda *a, **k: pd.DataFrame())
    for t in ("NVDA", "MU"):
        _sembrar_puntaje(VIEJA, t, *_inv(VIEJA))
    _sembrar_puntaje(VIEJA, "TSM", *_sana(VIEJA))
    _sembrar_puntaje(VIEJA, "AMD", f"{VIEJA}T21:15:00+00:00", None)
    _sembrar_puntaje(RECIENTE, "INTC", *_inv(RECIENTE))       # fuera de la ventana de 7 días
    _sembrar_puntaje(VIEJA, "ASML", *_inv(VIEJA), estado=senales.ESTADO_LEGACY)
    r = senales.verificar_puntaje_pendientes()
    fuera, dentro, ilegibles = mki_vigia._inversiones_puntaje(senales.DB_PATH)
    limite = (HOY - timedelta(days=7)).isoformat()
    en_ventana = {f: n for f, n in fuera.items() if f <= limite}
    assert r["excluidas"] == sum(en_ventana.values()) == 2
    assert r["fechas_excluidas"] == sorted(en_ventana) == [VIEJA]
    assert dentro == {} and ilegibles == {}
    assert fuera == {VIEJA: 2, RECIENTE: 1}                  # el vigía ve además la reciente


def test_guarda_puntaje_abre_la_base_en_solo_lectura_y_no_la_cambia(entorno):
    fuente = inspect.getsource(mki_vigia._inversiones_puntaje)
    assert "mode=ro" in fuente
    assert "UPDATE" not in fuente and "INSERT" not in fuente and "DELETE" not in fuente
    _sembrar_puntaje(VIEJA, "NVDA", *_inv(VIEJA))
    antes = sqlite3.connect(senales.DB_PATH).execute("SELECT * FROM senales_ticker").fetchall()
    mki_vigia.chequear_guarda_puntaje(HOY)
    despues = sqlite3.connect(senales.DB_PATH).execute("SELECT * FROM senales_ticker").fetchall()
    assert antes == despues


def test_guarda_puntaje_sin_base_no_rompe_el_pase(entorno, monkeypatch):
    monkeypatch.setattr(senales, "DB_PATH", os.path.join(str(os.path.dirname(mki_vigia.RUTA_PENDIENTE)), "no_existe.db"))
    ok, d = mki_vigia.chequear_guarda_puntaje(HOY)
    assert not ok and "guarda puntaje" in d


def test_el_pase_incluye_la_guarda_puntaje(entorno, todo_lo_demas_ok, monkeypatch):
    _sellar_hoy(TS_TARDIO)
    _sembrar_puntaje(VIEJA, "NVDA", *_inv(VIEJA), en_verificacion=True)
    assert mki_vigia.revision(HOY) == 0
    assert len(entorno) == 1 and "guarda puntaje" in entorno[0] and "DENTRO" in entorno[0]


# ------------------------------------------------------------
# Errata «launchd» (§67, bitácora 14 0-bis.9)
# ------------------------------------------------------------
def test_el_mensaje_del_proceso_colgado_ya_no_dice_launchd(entorno, monkeypatch):
    monkeypatch.setattr(costos, "corridas_del_dia", lambda origen=None, fecha=None: [])
    monkeypatch.setattr(mki_vigia, "_proceso_noticias_colgado",
                        lambda: "proceso 53783 vivo desde Mon Aug  3 17:52:38 2026")
    ok, detalle = mki_vigia.chequear_noticias()
    assert not ok and "proceso 53783 vivo" in detalle
    assert "launchd" not in detalle
    assert "no re-dispara" in detalle


def test_ningun_texto_que_viaja_por_telegram_nombra_launchd():
    """Los comentarios pueden contar la historia del Mac; los textos que
    salen por Telegram describen esta máquina (systemd)."""
    assert "launchd no re-dispara" not in inspect.getsource(mki_vigia)
