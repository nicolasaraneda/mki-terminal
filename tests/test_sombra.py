# ============================================================
# Tests de la Etapa 5.0.3 — modo sombra (Fase 3 de la reactivación) y comparador.
#
# Lo que estos tests protegen es una sola cosa: que la máquina sombra NO
# emita nada hacia afuera, y que el comparador no regale paridad. Todo
# sintético — sin red, sin Telegram, sin tocar senales.db real.
# ============================================================

import json
import os
import sys
from datetime import date

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import alertas
import comparar_sombra as cs
import mki_backup
import mki_vigia
import modo


@pytest.fixture
def sombra(monkeypatch, tmp_path):
    """Máquina en modo sombra, con el log de interceptación en tmp."""
    monkeypatch.setenv("MKI_MODO", "sombra")
    ruta = tmp_path / "sombra_telegram.log"
    monkeypatch.setattr(modo, "RUTA_SOMBRA_TELEGRAM", str(ruta))
    return ruta


@pytest.fixture
def titular(monkeypatch):
    monkeypatch.delenv("MKI_MODO", raising=False)


# ------------------------------------------------------------
# A. Interceptación de Telegram
# ------------------------------------------------------------
def test_en_sombra_telegram_no_sale_a_la_red(sombra, monkeypatch):
    """El requisito central: nada sale a la red. requests.post explota si
    alguien lo llama — si el test pasa, es porque NADIE lo llamó."""
    def explota(*a, **k):
        raise AssertionError("¡se intentó enviar a la red estando en sombra!")
    monkeypatch.setattr(alertas.requests, "post", explota)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token-de-prueba-sin-forma-de-secreto")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "999")

    ok, detalle = alertas.enviar_mensaje("reporte de prueba")

    assert ok is True          # el resto del sistema debe seguir su curso normal
    assert "sombra" in detalle
    assert "reporte de prueba" in sombra.read_text(encoding="utf-8")


def test_en_sombra_se_intercepta_aunque_no_haya_telegram_configurado(sombra, monkeypatch):
    """La interceptación va ANTES del chequeo de configuración: el log de
    sombra debe registrar todo lo que la máquina habría emitido."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    ok, _ = alertas.enviar_mensaje("alerta del vigía")
    assert ok is True
    assert "alerta del vigía" in sombra.read_text(encoding="utf-8")


def test_de_titular_si_sale_a_la_red(titular, monkeypatch):
    """Contraprueba: sin MKI_MODO el envío real ocurre. Si este test fallara,
    la sombra estaría apagando Telegram para todos, incluido el Mac."""
    llamadas = []

    class RespFalsa:
        status_code = 200
        def json(self): return {"ok": True}

    monkeypatch.setattr(alertas.requests, "post",
                        lambda *a, **k: llamadas.append(a) or RespFalsa())
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token-de-prueba-sin-forma-de-secreto")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "999")
    ok, _ = alertas.enviar_mensaje("hola")
    assert ok is True and len(llamadas) == 1


def test_el_log_de_sombra_enmascara_secretos(sombra, monkeypatch):
    """El log de sombra pasa por enmascarar_secretos como todo lo que acaba
    en un archivo. El fake NO necesita forma de token real: el enmascarado
    va por el VALOR de la variable de entorno (len >= 8), no por su forma.
    La ruta por patrón —defensa en profundidad para secretos que no están en
    el entorno— la cubre tests/test_seguridad.py, que es el archivo que por
    eso lleva la exclusión en el hook pre-commit."""
    falso = "token-de-prueba-sin-forma-de-secreto"
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", falso)
    alertas.enviar_mensaje(f"token: {falso}")
    contenido = sombra.read_text(encoding="utf-8")
    assert falso not in contenido          # no se filtró
    assert "…reto" in contenido            # y se enmascaró, no se borró


def test_mki_modo_ilegible_cae_a_sombra_no_a_titular(monkeypatch):
    """Falla segura: un typo jamás puede convertir al PC en segundo titular."""
    monkeypatch.setenv("MKI_MODO", "sombrra")
    assert modo.en_sombra() is True
    assert modo.valor_crudo_invalido() == "sombrra"


def test_sin_variable_es_titular(titular):
    assert modo.en_sombra() is False
    assert modo.modo_actual() == modo.MODO_TITULAR


# ------------------------------------------------------------
# B. El backup no commitea en sombra
# ------------------------------------------------------------
def test_backup_en_sombra_no_commitea(sombra, monkeypatch, tmp_path):
    """Ni commit ni `git add`: en sombra no se toca el índice de git."""
    llamadas = []
    monkeypatch.setattr(mki_backup, "_git",
                        lambda *a: llamadas.append(a) or pytest.fail("git en sombra"))
    monkeypatch.setattr(mki_backup, "DIRECTORIO", str(tmp_path))
    os.makedirs(tmp_path / "data", exist_ok=True)
    assert mki_backup.main() == 0
    assert llamadas == []


def test_backup_de_titular_si_intenta_commitear(titular, monkeypatch, tmp_path):
    """Contraprueba: el Mac debe seguir commiteando."""
    llamadas = []

    class R:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(mki_backup, "_git", lambda *a: llamadas.append(a) or R())
    monkeypatch.setattr(mki_backup, "DIRECTORIO", str(tmp_path))
    os.makedirs(tmp_path / "data", exist_ok=True)
    mki_backup.main()
    assert llamadas and llamadas[0][0] == "add"


# ------------------------------------------------------------
# C. El vigía ya no da la falsa alarma del backup
# ------------------------------------------------------------
def test_vigia_no_marca_falla_por_backup_en_sombra(sombra):
    ok, detalle = mki_vigia.chequear_backup()
    assert ok is True
    assert "sombra" in detalle


def test_vigia_de_titular_sigue_chequeando_el_backup(titular):
    """El chequeo real debe seguir vivo en el titular: la corrección de la
    falsa alarma no puede haber apagado el chequeo para todos."""
    ok, detalle = mki_vigia.chequear_backup()
    assert "backup:" in detalle
    assert "sombra" not in detalle


# ------------------------------------------------------------
# D. El comparador
# ------------------------------------------------------------
FECHA_OK = "2026-08-26"     # posterior al corte


def _snap(fecha=FECHA_OK, **cambios):
    fila = {"fecha": fecha, "creado_en": f"{fecha}T22:00:00.118402+00:00",
            "regimen": "Alcista · vol alta", "roca_chip": 50.0,
            "timestamp_utc": f"{fecha}T22:00:00.118402+00:00",
            "origen": "programado",
            "modelo_version": "4.6.0", "feature_version": "4.6.0",
            "universo_version": "4.6.0", "ventana_betas": 120.0,
            "descarga_ok": 28.0, "descarga_total": 28.0, "descarga_caidos": None,
            "plataforma_version": "5.0.2", "sox_usado_pct": -2.7,
            "sox_fecha": fecha}
    fila.update(cambios)
    return fila


def _sombra_snap(fecha=FECHA_OK, **cambios):
    """La fila de la SOMBRA tal como sale en la realidad: sellada por su
    cuenta, así que NO comparte microsegundos con la del titular, y lleva su
    propia plataforma_version. Los tests de paridad usan esta — usar la misma
    fila en los dos lados dispararía (con razón) la huella de base copiada."""
    base = {"creado_en": f"{fecha}T22:00:04.771903+00:00",
            "timestamp_utc": f"{fecha}T22:00:04.771903+00:00",
            "plataforma_version": "5.0.3"}
    base.update(cambios)
    return _snap(fecha=fecha, **base)


def _ticker(ticker="2330.TW", fecha=FECHA_OK, **cambios):
    fila = {"fecha": fecha, "ticker": ticker, "puntaje_v0": 0.57,
            "sentimiento_ia": 0.4488513020729087, "puntaje_ia": 0.6163,
            "apertura_estimada_pct": -1.03, "confianza_r2": 0.2846,
            "timestamp_utc": f"{fecha}T22:00:00+00:00", "exchange": "XTAI",
            "sesion_objetivo": "2026-08-27",
            "available_at": f"{fecha}T20:00:00+00:00", "estado": "pendiente",
            "intervalo80_pp": 2.66, "n_muestra": 120.0,
            "modelo_version": "4.6.0", "beta": 0.38}
    fila.update(cambios)
    return fila


def _montar(monkeypatch, snap_sombra, tickers_sombra):
    """Sustituye la lectura local por datos sintéticos (la base real jamás
    se toca en los tests)."""
    def falso(tabla, fecha):
        if tabla == "snapshots":
            return pd.DataFrame([snap_sombra] if snap_sombra else [])
        return pd.DataFrame(tickers_sombra)
    monkeypatch.setattr(cs, "leer_tabla_local", falso)


def test_rechaza_fechas_anteriores_al_corte(monkeypatch):
    """La paridad sobre bases copiadas es trivial y NO es evidencia."""
    _montar(monkeypatch, _sombra_snap(), [_ticker()])
    for f in ("2026-08-24", "2026-08-20", "2026-07-01"):
        res = cs.comparar_fecha(f, pd.DataFrame([_snap(fecha=f)]),
                                pd.DataFrame([_ticker(fecha=f)]))
        assert res["veredicto"] == cs.VEREDICTO_NO_COMPUTABLE
        assert "corte" in res["motivo"].lower()


def test_el_corte_es_inclusive():
    assert cs.FECHA_CORTE == date(2026, 8, 24)


def test_paridad_cuando_todo_coincide(monkeypatch):
    _montar(monkeypatch, _sombra_snap(), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_PARIDAD
    assert res["hallazgos"] == []


def test_nivel1_una_diferencia_minima_de_beta_es_hallazgo(monkeypatch):
    """0.01 en beta es la diferencia MÁS PEQUEÑA representable en el campo
    sellado. No es ruido de coma flotante: es evidencia de insumos
    distintos, y tiene que romper la paridad."""
    _montar(monkeypatch, _sombra_snap(), [_ticker(beta=0.39)])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker(beta=0.38)]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA
    h = [x for x in res["hallazgos"] if x["campo"] == "beta"]
    assert len(h) == 1 and h[0]["nivel"] == 1
    assert h[0]["delta"] == pytest.approx(0.01)


def test_nivel1_ruido_de_float_puro_no_rompe_paridad(monkeypatch):
    """La contracara: 1e-15 relativo SÍ es ruido y no debe gritar."""
    _montar(monkeypatch, _sombra_snap(), [_ticker(apertura_estimada_pct=-1.03)])
    res = cs.comparar_fecha(
        FECHA_OK, pd.DataFrame([_snap()]),
        pd.DataFrame([_ticker(apertura_estimada_pct=-1.03 + 1e-15)]))
    assert res["veredicto"] == cs.VEREDICTO_PARIDAD


def test_nivel1_cubre_apertura_r2_intervalo_y_puntaje(monkeypatch):
    for campo, valor in (("apertura_estimada_pct", -1.5), ("confianza_r2", 0.30),
                         ("intervalo80_pp", 3.0), ("puntaje_v0", 0.60)):
        _montar(monkeypatch, _sombra_snap(), [_ticker(**{campo: valor})])
        res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                                pd.DataFrame([_ticker()]))
        assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA, campo
        assert any(h["campo"] == campo and h["nivel"] == 1 for h in res["hallazgos"])


def test_nivel2_n_muestra_148_vs_147_rompe_paridad(monkeypatch):
    """La firma exacta de la divergencia del 14-ago. Es el hallazgo más
    diagnóstico disponible: un desfase de una sesión en los precios."""
    _montar(monkeypatch, _sombra_snap(), [_ticker(n_muestra=147.0)])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker(n_muestra=148.0)]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA
    assert any(h["campo"] == "n_muestra" and h["nivel"] == 2
               for h in res["hallazgos"])


def test_nivel2_sox_fecha_distinta_rompe_paridad(monkeypatch):
    """Si las máquinas usaron cierres del SOX de días distintos, todo lo
    demás da igual."""
    _montar(monkeypatch, _sombra_snap(sox_fecha="2026-08-25"), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap(sox_fecha="2026-08-26")]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA


def test_nivel2_regimen_y_roca_chip(monkeypatch):
    _montar(monkeypatch, _sombra_snap(regimen="Bajista · vol baja"), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA


def test_nivel2_conjunto_de_tickers_y_numero_de_predicciones(monkeypatch):
    _montar(monkeypatch, _sombra_snap(), [_ticker("2330.TW")])
    res = cs.comparar_fecha(
        FECHA_OK, pd.DataFrame([_snap()]),
        pd.DataFrame([_ticker("2330.TW"), _ticker("005930.KS")]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA
    campos = {h["campo"] for h in res["hallazgos"]}
    assert "tickers_sellados" in campos
    assert "numero_de_predicciones" in campos


def test_nivel3_plataforma_distinta_NO_es_divergencia(monkeypatch):
    """5.0.2 en el Mac y 5.0.3 en el PC es legítimo y está registrado en
    DECISIONES.md §8. Si esto rompiera la paridad, la ventana entera daría
    divergencia todas las noches por la razón equivocada."""
    _montar(monkeypatch, _sombra_snap(plataforma_version="5.0.3"), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK,
                            pd.DataFrame([_snap(plataforma_version="5.0.2")]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_PARIDAD
    assert any(h["campo"] == "plataforma_version" for h in res["esperadas"])


def test_nivel3_timestamps_y_noticias_no_rompen_paridad(monkeypatch):
    _montar(monkeypatch,
            _snap(timestamp_utc="2026-08-26T22:04:11+00:00",
                  creado_en="2026-08-26T22:04:11+00:00"),
            [_ticker(timestamp_utc="2026-08-26T22:04:11+00:00",
                     sentimiento_ia=0.99, puntaje_ia=0.11, estado="verificada")])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_PARIDAD
    campos = {h["campo"] for h in res["esperadas"]}
    assert {"timestamp_utc", "sentimiento_ia", "puntaje_ia", "estado"} <= campos


POSTERIOR = "2026-08-27"   # el titular ya publicó ESTE día


def test_dia_no_computable_si_el_titular_no_sello(monkeypatch):
    """'Nada = nada' jamás es paridad. La ausencia es DEFINITIVA porque el
    titular ya publicó sellos de una fecha posterior."""
    _montar(monkeypatch, _sombra_snap(), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap(fecha=POSTERIOR)]),
                            pd.DataFrame([_ticker(fecha=POSTERIOR)]))
    assert res["veredicto"] == cs.VEREDICTO_NO_COMPUTABLE
    assert "titular" in res["motivo"].lower()
    assert "definitiva" in res["motivo"].lower()


def test_dia_no_computable_si_no_sello_ninguna(monkeypatch):
    _montar(monkeypatch, None, [])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap(fecha=POSTERIOR)]),
                            pd.DataFrame([_ticker(fecha=POSTERIOR)]))
    assert res["veredicto"] == cs.VEREDICTO_NO_COMPUTABLE
    assert "tampoco" in res["motivo"].lower()


# ------------------------------------------------------------
# D bis. Huella de base copiada (cinturón y tirantes con FECHA_CORTE)
# ------------------------------------------------------------
def test_huella_de_copia_se_rechaza_aunque_la_fecha_sea_posterior_al_corte(monkeypatch):
    """Dos máquinas que sellan por separado NO comparten microsegundos. Si
    coinciden creado_en, timestamp_utc y plataforma_version, es la MISMA
    fila copiada — y el comparador se niega aunque la fecha esté pasado el
    corte, sin depender de que nadie se acuerde de subir la constante."""
    _montar(monkeypatch, _snap(), [_ticker()])          # ¡la MISMA fila!
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    assert date.fromisoformat(FECHA_OK) > cs.FECHA_CORTE   # el corte NO aplica
    assert res["veredicto"] == cs.VEREDICTO_NO_COMPUTABLE
    assert "copiada" in res["motivo"].lower()
    assert "FECHA_CORTE" in res["motivo"]


def test_la_huella_exige_los_tres_campos(monkeypatch):
    """Con los timestamps iguales pero plataforma distinta NO se dispara la
    huella: es el caso real de la ventana si dos sellos cayeran en el mismo
    microsegundo. La comparación sigue su curso normal."""
    _montar(monkeypatch, _snap(plataforma_version="5.0.3"), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap(plataforma_version="5.0.2")]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_PARIDAD


def test_los_dos_mecanismos_son_independientes(monkeypatch):
    """Cinturón y tirantes: basta que se dispare UNO. Fecha anterior al
    corte con filas claramente distintas → rechazo por corte."""
    f = "2026-08-20"
    _montar(monkeypatch, _sombra_snap(fecha=f), [_ticker(fecha=f)])
    res = cs.comparar_fecha(f, pd.DataFrame([_snap(fecha=f)]),
                            pd.DataFrame([_ticker(fecha=f)]))
    assert res["veredicto"] == cs.VEREDICTO_NO_COMPUTABLE
    assert "corte" in res["motivo"].lower()


# ------------------------------------------------------------
# D ter. PENDIENTE_PUBLICACION — el Mac pushea después de las 20:30
# ------------------------------------------------------------
def test_pendiente_publicacion_cuando_la_ausencia_es_ambigua(monkeypatch):
    """Sin fila del titular y sin sellos suyos posteriores, no se puede
    distinguir 'no selló' de 'selló y aún no pusheó'. Quemar el día ahí
    sería perderlo por un push que todavía no llegó."""
    _montar(monkeypatch, _sombra_snap(), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame(columns=["fecha"]),
                            pd.DataFrame(columns=["fecha", "ticker"]))
    assert res["veredicto"] == cs.VEREDICTO_PENDIENTE
    assert "push" in res["motivo"].lower()


def test_pendiente_se_resuelve_al_llegar_el_push(monkeypatch):
    """Re-ejecutable: la misma fecha, con la fila del titular ya publicada,
    da veredicto definitivo. Es lo que lo separa de DIA_NO_COMPUTABLE."""
    _montar(monkeypatch, _sombra_snap(), [_ticker()])
    antes = cs.comparar_fecha(FECHA_OK, pd.DataFrame(columns=["fecha"]),
                              pd.DataFrame(columns=["fecha", "ticker"]))
    assert antes["veredicto"] == cs.VEREDICTO_PENDIENTE
    despues = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                                pd.DataFrame([_ticker()]))
    assert despues["veredicto"] == cs.VEREDICTO_PARIDAD


def test_pendiente_no_suma_ni_rompe_la_racha(monkeypatch, tmp_path):
    ruta = tmp_path / "veredictos.jsonl"
    filas = [{"fecha": "2026-08-26", "veredicto": "PARIDAD", "motivo": ""},
             {"fecha": "2026-08-27", "veredicto": "PENDIENTE_PUBLICACION", "motivo": ""},
             {"fecha": "2026-08-28", "veredicto": "PARIDAD", "motivo": ""}]
    ruta.write_text("\n".join(json.dumps(f) for f in filas), encoding="utf-8")
    monkeypatch.setattr(cs, "RUTA_VEREDICTOS", str(ruta))
    salida = cs.contador()
    assert "días con PARIDAD: 2" in salida
    assert "racha actual: 2/3" in salida
    assert "SIN CERRAR" in salida and "2026-08-27" in salida


def test_el_contador_usa_la_ultima_corrida_de_cada_fecha(monkeypatch, tmp_path):
    """Un día pendiente que se re-ejecuta se resuelve: la corrida posterior
    manda sobre la anterior."""
    ruta = tmp_path / "veredictos.jsonl"
    filas = [{"fecha": "2026-08-26", "veredicto": "PENDIENTE_PUBLICACION", "motivo": ""},
             {"fecha": "2026-08-26", "veredicto": "PARIDAD", "motivo": ""}]
    ruta.write_text("\n".join(json.dumps(f) for f in filas), encoding="utf-8")
    monkeypatch.setattr(cs, "RUTA_VEREDICTOS", str(ruta))
    salida = cs.contador()
    assert "días con PARIDAD: 1" in salida
    assert "SIN CERRAR" not in salida


def test_si_la_sombra_no_sella_es_DIVERGENCIA_no_dia_perdido(monkeypatch):
    """El titular selló y la sombra no: eso es la sombra fallando, y no
    puede esconderse como día no computable."""
    _montar(monkeypatch, None, [])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA


def test_diferencia_de_esquema_se_reporta_como_tal(monkeypatch):
    snap_sin_columna = _sombra_snap()
    del snap_sin_columna["sox_fecha"]
    _montar(monkeypatch, snap_sin_columna, [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    assert res["veredicto"] == cs.VEREDICTO_DIVERGENCIA
    assert any(h["ambito"] == "esquema" for h in res["hallazgos"])


# ------------------------------------------------------------
# E. Reporte y contador
# ------------------------------------------------------------
def test_el_reporte_declara_el_criterio_y_la_procedencia(monkeypatch):
    _montar(monkeypatch, _sombra_snap(), [_ticker()])
    res = cs.comparar_fecha(FECHA_OK, pd.DataFrame([_snap()]),
                            pd.DataFrame([_ticker()]))
    texto = cs.componer_reporte(res, "abc123", hubo_fetch=True)
    for esperado in ("PARIDAD", "Criterio aplicado", "abc123", "mode=ro",
                     "Fecha de corte", "1e-09", "n_muestra"):
        assert esperado in texto, esperado


def test_el_contador_no_cuenta_los_dias_no_computables(monkeypatch, tmp_path):
    ruta = tmp_path / "veredictos.jsonl"
    filas = [{"fecha": "2026-08-26", "veredicto": "PARIDAD", "motivo": ""},
             {"fecha": "2026-08-27", "veredicto": "DIA_NO_COMPUTABLE", "motivo": ""},
             {"fecha": "2026-08-28", "veredicto": "PARIDAD", "motivo": ""}]
    ruta.write_text("\n".join(json.dumps(f) for f in filas), encoding="utf-8")
    monkeypatch.setattr(cs, "RUTA_VEREDICTOS", str(ruta))
    salida = cs.contador()
    assert "días con PARIDAD: 2" in salida
    assert "racha actual: 2/3" in salida


def test_una_divergencia_vuelve_la_racha_a_cero(monkeypatch, tmp_path):
    ruta = tmp_path / "veredictos.jsonl"
    filas = [{"fecha": "2026-08-26", "veredicto": "PARIDAD", "motivo": ""},
             {"fecha": "2026-08-27", "veredicto": "DIVERGENCIA", "motivo": ""}]
    ruta.write_text("\n".join(json.dumps(f) for f in filas), encoding="utf-8")
    monkeypatch.setattr(cs, "RUTA_VEREDICTOS", str(ruta))
    assert "racha actual: 0/3" in cs.contador()


def test_el_comparador_nunca_hace_pull():
    """Blindaje del pendiente #3: `git pull` alteraría bajo los pies el
    árbol que los timers ejecutan esa misma noche."""
    fuente = open(cs.__file__, encoding="utf-8").read()
    assert '"pull"' not in fuente and "'pull'" not in fuente
