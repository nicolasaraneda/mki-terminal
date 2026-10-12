# ============================================================
# tests/test_frescura.py — la guarda de frescura de snapshot.py (acta §93.8 b,
# corrida 16-1, 10-oct-2026) y la negativa declarada que el vigía reconoce
# (acta §93.8 d).
#
# El hueco que cierra, H0 de la tarjeta §72 (MEDIDO con test en la corrida
# 15): la guarda (b) de §90.1 se niega si la sesión de `sox_fecha` NO ha
# cerrado; con `sox_fecha` de la sesión ANTERIOR, ya cerrada, pasa y sella
# el snapshot de HOY con el cierre de AYER. Un despertar de mañana en día
# hábil (inventario §66 D.1) sellaría así y a las 18:15 diría «ya existe».
#
# La regla firmada (§93.8 b): si hoy es sesión de XNYS y `sox_fecha` no es
# hoy, no se sella. SIN margen horario (§72 C.2: desde el 2-nov-2026 la
# holgura entre las 18:15 de Chile y el cierre de XNYS es de 15 minutos y
# cualquier margen apagaría el sello). Fin de semana y feriado de XNYS no
# cambian de conducta (D.2 queda como estaba, sin firmar). `sox_fecha`
# vacío sigue por su rama (reloj de pared, con alerta del vigía: §84.2).
#
# Y la negativa se DECLARA: una línea fija en snapshot.log, con código,
# fecha y `sox_fecha`, que `mki_vigia.py` distingue de una falla (§93.8 d).
# La misma línea la emite la guarda (b), cuya condición no cambia.
#
# Fixture `sellador` reutilizada de tests/test_conocibilidad.py: snapshot.py
# REAL con el motor reemplazado, el reloj inyectado y `guardar_snapshot`
# convertido en espía. Sin red; la base real sólo en `mode=ro`.
# Cero intentos del DSR.
# ============================================================

import inspect
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import calendarios  # noqa: E402  (real)
import mki_vigia  # noqa: E402
import registro  # noqa: E402
import senales  # noqa: E402
import snapshot  # noqa: E402
from test_conocibilidad import (  # noqa: E402,F401  (la fixture se registra al importarla)
    CHILE, CIERRE_EVENTO, EMISION_EVENTO, FECHA_EVENTO, _a_las_1815_de_chile,
    _instante, sellador)

from bases_de_prueba import hay_filas, razon_sin_base  # noqa: E402  (corrida 16-3, R5)

BASE_REAL = os.path.join(RAIZ, "senales.db")
solo_con_base = pytest.mark.skipif(
    not hay_filas(BASE_REAL, "snapshots"), reason=razon_sin_base(BASE_REAL, "snapshots"))

# El escenario H0 de la tarjeta §72, con las mismas fechas que fijó la
# corrida 15: martes 29-sep-2026 a las 18:15 de Chile, y la fuente todavía
# entrega como último cierre del SOX el del lunes 28.
MARTES, LUNES = "2026-09-29", "2026-09-28"
# Un sábado y un feriado de XNYS (Labor Day) con su viernes anterior: la
# conducta en esos días no cambia. El 7-sep es, además, el único snapshot
# histórico con `sox_fecha` distinta de su fecha (consulta en el test de
# historia real).
SABADO, VIERNES = "2026-10-10", "2026-10-09"
FERIADO, VIERNES_PREVIO = "2026-09-07", "2026-09-04"


def test_el_escenario_es_el_que_dice_ser():
    assert calendarios.es_sesion("XNYS", MARTES) and calendarios.es_sesion("XNYS", LUNES)
    assert calendarios.sesion_anterior("XNYS", MARTES) == LUNES
    assert date.fromisoformat(SABADO).weekday() == 5
    assert not calendarios.es_sesion("XNYS", SABADO)
    assert not calendarios.es_sesion("XNYS", FERIADO)
    assert date.fromisoformat(FERIADO).weekday() == 0        # un lunes feriado
    assert calendarios.es_sesion("XNYS", VIERNES) and calendarios.es_sesion("XNYS", VIERNES_PREVIO)


# ------------------------------------------------------------
# Reproducción y controles
# ------------------------------------------------------------
def test_reproduccion_H0_con_la_fuente_atrasada_no_se_sella(sellador, capsys):
    """REPRODUCCIÓN (falla sobre HEAD, que sella). A las 18:15 de Chile del
    martes la fuente sirve el SOX del lunes: la sesión del lunes cerró hace
    un día, la guarda (b) pasa, y HEAD sella el snapshot del martes con el
    insumo del lunes. Con la guarda de frescura no se sella, no se llama a
    `guardar_snapshot`, el resultado trae la negativa con su código y en la
    salida queda la línea fija que lee el vigía."""
    reloj = _a_las_1815_de_chile(MARTES, segundos=3)
    assert reloj > calendarios.cierre_utc("XNYS", MARTES)    # el martes YA cerró
    resultado = sellador["sellar"](reloj, LUNES)
    assert resultado["snapshot"] is False, (
        f"snapshot.py selló el {MARTES} con sox_fecha={LUNES}: insumo de ayer")
    assert sellador["sellos"] == [], "guardar_snapshot fue llamado"
    assert resultado["negativa"] == snapshot.NEGATIVA_FRESCURA
    assert resultado["sox_fecha"] == LUNES and resultado["fecha"] == MARTES
    assert MARTES in resultado["motivo"] and LUNES in resultado["motivo"]
    salida = capsys.readouterr().out
    lineas = [l for l in salida.splitlines() if snapshot.MARCA_NEGATIVA in l]
    assert len(lineas) == 1, salida
    assert f"[{snapshot.NEGATIVA_FRESCURA}]" in lineas[0]
    assert f"fecha={MARTES}" in lineas[0] and f"sox_fecha={LUNES}" in lineas[0]


def test_control_dia_de_sesion_con_sox_fecha_de_hoy_sella_igual_que_antes(sellador, capsys):
    """CONTROL: el mismo martes a las 18:15 con el SOX del martes se sella
    exactamente como antes (sin negativa, sin línea en el log)."""
    reloj = _a_las_1815_de_chile(MARTES, segundos=3)
    resultado = sellador["sellar"](reloj, MARTES)
    assert resultado["snapshot"] is True, resultado
    assert "negativa" not in resultado
    sello = sellador["sellos"][0]
    assert sello["fecha"] == MARTES and sello["sox_fecha"] == MARTES
    assert sello["available_at"] == calendarios.cierre_utc("XNYS", MARTES).isoformat()
    assert snapshot.MARCA_NEGATIVA not in capsys.readouterr().out


def test_fin_de_semana_no_cambia_de_conducta(sellador, capsys):
    """D.2 del inventario §66 sigue sin firmar: un disparo en sábado con el
    SOX del viernes sella como antes (fecha sábado, insumo viernes). La
    guarda de frescura sólo rige en día de sesión de XNYS."""
    reloj = _a_las_1815_de_chile(SABADO)
    resultado = sellador["sellar"](reloj, VIERNES)
    assert resultado["snapshot"] is True, resultado
    sello = sellador["sellos"][0]
    assert sello["fecha"] == SABADO and sello["sox_fecha"] == VIERNES
    assert snapshot.MARCA_NEGATIVA not in capsys.readouterr().out


def test_feriado_de_xnys_no_cambia_de_conducta(sellador, capsys):
    """Labor Day: el job dispara (el timer no conoce los feriados de NYSE),
    la fuente sirve el viernes, y se sella como antes. Es el único caso
    histórico con `sox_fecha` ≠ fecha (7-sep-2026) y sigue siendo legítimo."""
    reloj = _a_las_1815_de_chile(FERIADO)
    resultado = sellador["sellar"](reloj, VIERNES_PREVIO)
    assert resultado["snapshot"] is True, resultado
    sello = sellador["sellos"][0]
    assert sello["fecha"] == FERIADO and sello["sox_fecha"] == VIERNES_PREVIO
    assert snapshot.MARCA_NEGATIVA not in capsys.readouterr().out


def test_la_guarda_b_de_90_1_sigue_igual_y_ahora_declara_su_negativa(sellador, capsys):
    """El evento del 28-sep (13:42 de Nueva York, `sox_fecha` del mismo día,
    sesión abierta): la guarda (b) se niega con el MISMO motivo de la
    corrida 15, y además deja la línea fija con su propio código. La
    frescura no interviene (sox_fecha == hoy)."""
    resultado = sellador["sellar"](_instante(EMISION_EVENTO), FECHA_EVENTO)
    assert resultado["snapshot"] is False and sellador["sellos"] == []
    assert "no ha cerrado" in resultado["motivo"] and "§90.1 b" in resultado["motivo"]
    assert resultado["cierre_utc"] == CIERRE_EVENTO
    assert resultado["negativa"] == snapshot.NEGATIVA_SESION_ABIERTA
    lineas = [l for l in capsys.readouterr().out.splitlines() if snapshot.MARCA_NEGATIVA in l]
    assert len(lineas) == 1
    assert f"[{snapshot.NEGATIVA_SESION_ABIERTA}]" in lineas[0]
    assert f"fecha={FECHA_EVENTO}" in lineas[0] and f"sox_fecha={FECHA_EVENTO}" in lineas[0]


def test_sin_sox_fecha_la_frescura_no_interviene(sellador, capsys):
    """`sox_fecha` vacío sigue por su rama (reloj de pared): sella, sin
    negativa, con el AVISO de ancla temporal que el vigía alerta (§84.2).
    Residuo declarado: la frescura no se puede juzgar sin `sox_fecha`."""
    resultado = sellador["sellar"](_a_las_1815_de_chile(MARTES), None)
    assert resultado["snapshot"] is True and "negativa" not in resultado
    salida = capsys.readouterr().out
    assert "AVISO ancla temporal" in salida and snapshot.MARCA_NEGATIVA not in salida


def test_si_el_calendario_falla_se_sella_como_antes_con_aviso(sellador, monkeypatch, capsys):
    """BL1 del dictamen 16-1: `calendarios.es_sesion` es una llamada nueva en
    el camino de sellado. Si el calendario revienta, la frescura no se
    puede juzgar y se sella como HEAD (degradación con AVISO, la misma
    dirección que la rama del `except` de `cierre_utc`); la excepción jamás
    sube a `main()`, donde se llevaría el verificador, los respaldos y el
    epílogo del vigía. Elección de agente a ratificar (tarjeta §80)."""
    def revienta(exchange, sesion):
        raise RuntimeError("calendario roto a propósito")
    monkeypatch.setattr(calendarios, "es_sesion", revienta)
    reloj = _a_las_1815_de_chile(MARTES, segundos=3)
    resultado = sellador["sellar"](reloj, LUNES)
    assert resultado["snapshot"] is True and "negativa" not in resultado
    salida = capsys.readouterr().out
    assert "AVISO frescura" in salida and "calendario" in salida
    assert snapshot.MARCA_NEGATIVA not in salida
    assert "roto a propósito" in salida             # el motivo queda en el log


def test_la_negativa_de_frescura_no_entra_al_bucle_de_reintentos(sellador, monkeypatch, capsys):
    """`main()` reintenta a los 20 y 40 min SÓLO ante «sin datos de
    mercado». Una fuente atrasada no se arregla esperando 20 minutos en
    este job (el riel de dinero sí espera; éste declara y termina): una sola
    llamada, ningún sleep, salida 0, y la negativa queda en el log."""
    sellador["preparar"](_a_las_1815_de_chile(MARTES, segundos=3), LUNES)
    monkeypatch.setattr(sys, "argv", ["snapshot.py"])
    monkeypatch.setattr(registro, "rotar_log", lambda *a, **k: None)
    monkeypatch.setattr(snapshot, "_epilogo_vigia", lambda: None)
    monkeypatch.setattr(senales, "verificar_pendientes",
                        lambda: ({"verificadas": 0},
                                 {"verificadas": 0, "excluidas": 0, "fechas_excluidas": []}))
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
    assert snapshot.MARCA_NEGATIVA in salida and f"[{snapshot.NEGATIVA_FRESCURA}]" in salida
    assert "la fuente no entregó datos" not in salida
    assert esperas == [] and len(intentos) == 1
    assert sellador["sellos"] == []


# ------------------------------------------------------------
# El productor y el consumidor de la línea fija son el mismo texto
# ------------------------------------------------------------
def test_el_vigia_lee_la_negativa_que_snapshot_escribe(sellador, monkeypatch, tmp_path, capsys):
    """Integración productor → consumidor: la salida REAL de snapshot.py
    (cabecera de `main()` incluida) se vuelca a un snapshot.log temporal y
    `mki_vigia._negativa_declarada_en_log` la reconoce con su código, fecha
    y sox_fecha. Ningún texto se duplica a mano en el test."""
    sellador["preparar"](_a_las_1815_de_chile(MARTES, segundos=3), LUNES)
    monkeypatch.setattr(sys, "argv", ["snapshot.py"])
    monkeypatch.setattr(registro, "rotar_log", lambda *a, **k: None)
    monkeypatch.setattr(snapshot, "_epilogo_vigia", lambda: None)
    monkeypatch.setattr(senales, "verificar_pendientes",
                        lambda: ({"verificadas": 0},
                                 {"verificadas": 0, "excluidas": 0, "fechas_excluidas": []}))
    monkeypatch.setattr(snapshot, "respaldar_a_csv", lambda: [])
    assert snapshot.main() == 0
    ruta = str(tmp_path / "snapshot.log")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(capsys.readouterr().out)
    monkeypatch.setattr(mki_vigia, "RUTA_SNAPSHOT_LOG", ruta)
    negativa = mki_vigia._negativa_declarada_en_log(date.fromisoformat(MARTES))
    assert negativa is not None
    assert negativa["codigo"] == snapshot.NEGATIVA_FRESCURA
    assert negativa["fecha"] == MARTES and negativa["sox_fecha"] == LUNES
    assert LUNES in negativa["texto"]
    # Otro día no la hereda: la negativa es de SU fecha.
    assert mki_vigia._negativa_declarada_en_log(date.fromisoformat(LUNES)) is None


def test_la_marca_es_una_sola_en_los_dos_modulos():
    assert mki_vigia.MARCA_NEGATIVA == snapshot.MARCA_NEGATIVA
    assert snapshot.NEGATIVA_FRESCURA != snapshot.NEGATIVA_SESION_ABIERTA


# ------------------------------------------------------------
# Forma de la guarda: por regla, sin margen, sin fechas
# ------------------------------------------------------------
def test_la_guarda_no_agrega_margen_horario_ni_nombra_fechas():
    """§72 C.2: cualquier margen horario rompe el sello desde el 2-nov-2026.
    La guarda compara dos FECHAS (`sox_fecha` contra hoy) y pregunta al
    calendario si hoy es sesión; no mira el reloj, no resta horas, no
    nombra el evento."""
    fuente = inspect.getsource(snapshot.ejecutar_snapshot)
    codigo = "\n".join(l for l in fuente.splitlines() if not l.strip().startswith("#"))
    assert "es_sesion" in codigo and "NEGATIVA_FRESCURA" in codigo
    assert "margen_horas" not in codigo and "sesion_ya_cerro" not in codigo
    assert "timedelta(" not in codigo
    assert "2026-" not in codigo and "-sep" not in codigo and "-nov" not in codigo


@solo_con_base
def test_historia_real_la_guarda_no_habria_rechazado_ningun_sello_de_dia_de_sesion():
    """Cuenta histórica (§66 D.1 escribió «0 de 45» al 29-sep —errata fechada
    en el acta §100.2: eran 0 de 44 sellos de día de sesión, sobre 45 con
    sox_fecha—; al 10-oct, 0 de 52 sobre 53): ningún
    snapshot sellado en día de sesión de XNYS tiene `sox_fecha` distinta de
    su fecha. Es la cifra que el encargo pide medir y, desde ahora, un
    invariante: con la guarda aplicada ninguna fila así puede volver a
    sellarse. Los `sox_fecha` NULL (sellos anteriores a 5.0) no se juzgan.
    Base real en `mode=ro`."""
    conn = sqlite3.connect(f"file:{BASE_REAL}?mode=ro", uri=True)
    try:
        filas = conn.execute(
            "SELECT fecha, sox_fecha FROM snapshots WHERE sox_fecha IS NOT NULL "
            "ORDER BY fecha").fetchall()
    finally:
        conn.close()
    if not filas:
        pytest.skip("senales.db sin sellos con sox_fecha (base vacía, p. ej. en un worktree)")
    assert len(filas) >= 45
    rechazados = [(f, s) for f, s in filas
                  if s != f and calendarios.es_sesion("XNYS", f)]
    assert rechazados == [], rechazados
    distintos = [(f, s) for f, s in filas if s != f]
    assert all(not calendarios.es_sesion("XNYS", f) for f, _ in distintos), distintos
