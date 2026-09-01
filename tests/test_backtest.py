# ============================================================
# Tests del motor de backtest (Etapa 5.0 WS5 — DISEÑO.md §9/§10).
#
# Incluye el test de NO-LOOK-AHEAD del framework mismo (un dato futuro es
# rechazado; truncar el futuro no cambia ninguna predicción emitida) y el
# dry-run de humo sobre datos sintéticos, marcado NO-CONCLUYENTE.
# Todo sin red: FuenteCongelada inyectada con series sintéticas.
# ============================================================

import os
import sqlite3
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import pytest

from universo import (EXCHANGE_POR_TICKER, INDICE_LOCAL_POR_EXCHANGE,
                      MERCADOS_POR_ABRIR, PARES_FX, UNIVERSO)

from backtest import baselines as bl
from backtest import cartera, datos, emision, metricas, motorbt

FIN_DATOS = date(2026, 6, 30)      # las series sintéticas llegan hasta aquí
DIA_EMISION = date(2026, 5, 20)    # emisión de referencia para los tests


def _series_sinteticas(hasta: date = FIN_DATOS) -> pd.DataFrame:
    idx = pd.bdate_range(end=pd.Timestamp(hasta), periods=500)
    tickers = sorted(set(list(UNIVERSO.keys()) + ["^SOX"] + list(PARES_FX)
                         + list(INDICE_LOCAL_POR_EXCHANGE.values())))
    columnas = {}
    for t in tickers:
        rng = np.random.default_rng(abs(hash(t)) % (2**32))
        columnas[t] = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.018, len(idx))))
    return pd.DataFrame(columnas, index=idx)


def _ohlc_sintetico(series: pd.DataFrame) -> dict:
    ohlc = {}
    for t in MERCADOS_POR_ABRIR:
        close = series[t]
        rng = np.random.default_rng(abs(hash("open" + t)) % (2**32))
        open_ = close.shift(1) * (1 + rng.normal(0, 0.008, len(close)))
        ohlc[t] = pd.DataFrame({"Open": open_, "Close": close}).dropna()
    return ohlc


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    """Bases de producción fuera de alcance (rutas vacías) y resultados a
    un directorio temporal: el test jamás toca nada real."""
    monkeypatch.setattr(datos, "RUTA_SENALES", str(tmp_path / "no_senales.db"))
    monkeypatch.setattr(datos, "RUTA_NOTICIAS", str(tmp_path / "no_noticias.db"))
    monkeypatch.setattr(motorbt, "DIR_RESULTADOS", str(tmp_path / "resultados"))
    series = _series_sinteticas()
    return datos.FuenteCongelada(series=series, ohlc=_ohlc_sintetico(series))


# ------------------------------------------------------------
# No-look-ahead del framework
# ------------------------------------------------------------
def test_dato_futuro_es_rechazado():
    idx = pd.bdate_range(end=pd.Timestamp(FIN_DATOS), periods=10)
    df = pd.DataFrame({"x": range(10)}, index=idx)
    with pytest.raises(datos.ErrorLookAhead):
        datos.validar_sin_futuro(df, DIA_EMISION)  # trae fechas > emisión
    datos.validar_sin_futuro(df, FIN_DATOS)  # sin futuro: pasa


def test_guardia_activa_en_cada_acceso(entorno, monkeypatch):
    """La guardia validar_sin_futuro se ejecuta de verdad en los accesos
    point-in-time (si una regresión la eliminara, este test muere)."""
    llamadas = []
    original = bl.validar_sin_futuro

    def espia(df, fecha):
        llamadas.append(fecha)
        return original(df, fecha)

    monkeypatch.setattr(bl, "validar_sin_futuro", espia)
    with entorno:
        ctx = bl.ContextoRun(entorno)
        modelo = bl.B1Momentum(ctx)
        modelo.predecir(DIA_EMISION)
    assert len(llamadas) > 0


def test_truncar_futuro_no_cambia_predicciones(monkeypatch, tmp_path):
    """La prueba reina: las predicciones emitidas en D son BYTE-idénticas
    con y sin los datos posteriores a D en la fuente."""
    monkeypatch.setattr(datos, "RUTA_SENALES", str(tmp_path / "n1.db"))
    monkeypatch.setattr(datos, "RUTA_NOTICIAS", str(tmp_path / "n2.db"))
    completa = _series_sinteticas()
    recortada = completa[completa.index.date <= DIA_EMISION]

    resultados = {}
    for nombre_v, series in (("completa", completa), ("recortada", recortada)):
        fuente = datos.FuenteCongelada(series=series, ohlc=_ohlc_sintetico(series))
        with fuente:
            ctx = bl.ContextoRun(fuente)
            por_baseline = {}
            for clase in (bl.B1Momentum, bl.B2Produccion, bl.B3Cuant):
                pred = clase(ctx).predecir(DIA_EMISION)
                por_baseline[clase.nombre] = pred.round(6).to_dict("records")
            resultados[nombre_v] = por_baseline
    assert resultados["completa"] == resultados["recortada"]


def test_regla_maestra_en_sesion_objetivo():
    """La apertura objetivo es SIEMPRE posterior a la emisión (calendarios
    reales, incluido el cruce de fecha de Seúl)."""
    for instante in emision.emisiones(date(2026, 7, 13), date(2026, 7, 17)):
        for ex in ("XKRX", "XTKS", "XTAI", "XETR", "XNYS"):
            sesion, apertura, _ = emision.sesion_objetivo(ex, instante)
            assert apertura > instante, (ex, sesion)


# ------------------------------------------------------------
# Cartera y métricas
# ------------------------------------------------------------
def test_cartera_costos_exactos():
    df = pd.DataFrame([
        {"fecha_emision": "2026-05-20", "ticker": f"T{i}", "est": est,
         "capturable_pct": cap}
        for i, (est, cap) in enumerate([(2.0, 1.0), (1.0, 0.5), (0.5, 0.2),
                                        (0.1, 0.0), (-1.0, -0.4), (-2.0, -0.8)])
    ])
    series = cartera.retornos_cartera(df, costo_pb=25)
    # top-3 long: media(1.0, 0.5, 0.2) − 2·25pb = 0.5667 − 0.5 = 0.0667
    assert series["long_only"].iloc[0] == pytest.approx(0.5667 - 0.5, abs=1e-3)
    # LS terciles (2 por lado): 0.5·media(1.0,0.5) − 0.5·media(−0.4,−0.8) − 0.5
    assert series["long_short"].iloc[0] == pytest.approx(
        0.5 * 0.75 - 0.5 * (-0.6) - 0.5, abs=1e-3)


def test_veredicto_escalonado():
    fechas = pd.date_range("2026-01-01", periods=120)
    rng = np.random.default_rng(7)
    base = pd.Series(rng.normal(0.0, 0.02, 120), index=fechas)
    ics = {"B0": base * 0, "B1": base + 0.05, "B2": base + 0.05}
    filas = metricas.veredicto_escalonado(ics)
    por_capa = {f["capa"]: f for f in filas}
    assert por_capa["B1 vs B0"]["veredicto"] == "aporta"        # +0.05 constante
    assert por_capa["B2 vs B1"]["veredicto"] == "no demostrado"  # delta 0


def test_ic_constante_es_cero():
    df = pd.DataFrame([{"fecha_emision": "2026-05-20", "ticker": f"T{i}",
                        "est": 0.0, "gap_pct": g}
                       for i, g in enumerate([1.0, -0.5, 0.3, 0.8])])
    ic = metricas.rank_ic_diario(df)
    assert ic.iloc[0] == 0.0  # sin ordenamiento no hay información


# ------------------------------------------------------------
# Solo lectura y dry-run de humo
# ------------------------------------------------------------
def test_conexion_ro_rechaza_escrituras(tmp_path):
    ruta = tmp_path / "prueba.db"
    rw = sqlite3.connect(ruta)
    rw.execute("CREATE TABLE x (a INTEGER)")
    rw.commit()
    rw.close()
    ro = datos._conexion_ro(str(ruta))
    with pytest.raises(sqlite3.OperationalError):
        ro.execute("INSERT INTO x VALUES (1)")
    ro.close()


def test_dry_run_humo_no_concluyente(entorno):
    reporte = motorbt.correr(date(2026, 5, 4), date(2026, 5, 15),
                             cuales=("B0", "B1", "B2", "B3"),
                             etiqueta="humo-sintetico", fuente=entorno)
    assert reporte["no_concluyente"] is True
    assert set(reporte["baselines"]) == {"B0", "B1", "B2", "B3"}
    for b in reporte["baselines"].values():
        assert b["n_pares"] > 0
        assert b["mae_gap_pp"] is not None
    assert reporte["benchmark_smh"]["ticker"] == "SMH"
    assert reporte["benchmark_smh"]["acumulado_pct"] is not None
    assert any(v["capa"] == "B1 vs B0" for v in reporte["veredicto_escalonado"])
    ruta = reporte["ruta"]
    with open(os.path.join(ruta, "resumen.md"), encoding="utf-8") as f:
        resumen = f.read()
    assert "NO-CONCLUYENTE" in resumen
    assert "SMH" in resumen
    assert os.path.exists(os.path.join(ruta, "metricas.json"))


# ------------------------------------------------------------
# Los TRES estados del sello de una corrida (Etapa 5.1)
#
# Colapsarlos en dos —humo / veredicto— es lo que permitiría que una
# corrida ejecutada antes de que el gatillo se cumpla se leyera como el
# veredicto definitivo. El aviso va en la PRIMERA pantalla del resumen.
# ------------------------------------------------------------
def _resumen_de(reporte) -> str:
    with open(os.path.join(reporte["ruta"], "resumen.md"), encoding="utf-8") as f:
        return f.read()


def test_estado_1_humo_lleva_el_aviso_de_no_concluyente(entorno):
    reporte = motorbt.correr(date(2026, 5, 4), date(2026, 5, 15),
                             cuales=("B0", "B1"), etiqueta="humo-sintetico",
                             fuente=entorno)
    assert reporte["no_concluyente"] is True
    assert "NO-CONCLUYENTE" in _resumen_de(reporte).split("\n")[0]


def test_estado_2_gatillo_incumplido_lo_declara_en_la_primera_pantalla(entorno):
    """Una corrida con veredicto pero con el gatillo sin cumplir NO es
    NO-CONCLUYENTE ni es el veredicto definitivo: es su propio estado, y
    tiene que decirlo arriba de todo junto con el holdout sin gastar."""
    gatillo = {
        "cumplido": False,
        "vias": ["(a) N>=150 SÍ, cambio de régimen NO — una sola etiqueta",
                 "(b) faltan 54 días (25-oct-2026)"],
        "holdout_intacto": True,
        "expediente": "GEMELO/resultados/gatillo_51.md",
    }
    reporte = motorbt.correr(date(2026, 5, 4), date(2026, 5, 15),
                             cuales=("B0", "B1"),
                             etiqueta="5.1-gatillo-incumplido",
                             fuente=entorno, estado_gatillo=gatillo)
    assert reporte["no_concluyente"] is False
    assert reporte["estado_gatillo"] == gatillo
    resumen = _resumen_de(reporte)
    primera_pantalla = "\n".join(resumen.split("\n")[:25])
    assert "NO CUMPLIDO" in primera_pantalla
    assert "NO es el veredicto definitivo" in primera_pantalla
    assert "holdout" in primera_pantalla.lower()
    assert "INTACTO" in primera_pantalla
    # y NO se disfraza de corrida de humo ni de veredicto pleno
    assert "NO-CONCLUYENTE" not in resumen
    assert "CORRIDA DE VEREDICTO — Etapa 5.1" not in resumen


def test_estado_3_veredicto_pleno_solo_sin_gatillo_pendiente(entorno):
    reporte = motorbt.correr(date(2026, 5, 4), date(2026, 5, 15),
                             cuales=("B0", "B1"), etiqueta="5.1",
                             fuente=entorno,
                             estado_gatillo={"cumplido": True})
    assert reporte["no_concluyente"] is False
    resumen = _resumen_de(reporte)
    assert "CORRIDA DE VEREDICTO — Etapa 5.1" in resumen.split("\n")[0]
    assert "NO-CONCLUYENTE" not in resumen


# ============================================================
# Migración del bootstrap al circular (Etapa 6.0.0 WS1 · DECISIONES.md §28)
# ============================================================
import inspect as _inspect

import numpy as _np
import pandas as _pd

from backtest import inferencia as _inf
from backtest import metricas as _met


def _serie(n=200, semilla=3):
    return _pd.Series(_np.random.default_rng(semilla).normal(0.05, 1.0, n))


def test_el_bootstrap_cubre_la_cola_de_la_serie():
    """EL test de la migración. Se construye una serie cuya señal vive
    ENTERA en las últimas observaciones. Un bootstrap circular la recupera;
    el esquema anterior —inicios en [0, n-bloque)— no podía empezar un
    bloque ahí y submuestreaba la cola. En una serie financiera la cola es
    lo más reciente, que es lo que más pesa al juzgar una estrategia."""
    x = _np.zeros(200)
    x[-5:] = 10.0                      # media real = 0.25
    n, bloque, draws = len(x), 10, 4000

    rng = _np.random.default_rng(0)
    ini = rng.integers(0, n, size=(draws, n // bloque))
    idx = (ini[:, :, None] + _np.arange(bloque)[None, None, :]) % n
    media_circular = float(x[idx.reshape(draws, -1)[:, :n]].mean())

    rng2 = _np.random.default_rng(0)
    ini2 = rng2.integers(0, n - bloque, size=(draws, n // bloque))
    idx2 = ini2[:, :, None] + _np.arange(bloque)[None, None, :]
    media_no_circular = float(x[idx2.reshape(draws, -1)[:, :n]].mean())

    assert media_circular == pytest.approx(x.mean(), abs=0.02)
    assert media_no_circular < 0.5 * x.mean()   # el viejo pierde la cola


def test_bootstrap_sharpe_exige_semilla_explicita():
    """Ni constante de módulo ni default: quien llama la pasa, y la corrida
    la sella en su reporte (DISEÑO.md §9 pide determinismo, no ocultación)."""
    p = _inspect.signature(_met.bootstrap_sharpe).parameters["semilla"]
    assert p.default is _inspect.Parameter.empty
    assert not hasattr(_met, "SEMILLA_BOOTSTRAP")


def test_bootstrap_sharpe_no_redondea():
    """El redondeo es presentación y vive en la capa de presentación."""
    lo, hi = _met.bootstrap_sharpe(_serie(), semilla=500)
    assert (round(lo, 2) != lo) or (round(hi, 2) != hi)


def test_bootstrap_sharpe_es_reproducible_y_depende_de_la_semilla():
    s = _serie()
    assert (_met.bootstrap_sharpe(s, semilla=500)
            == _met.bootstrap_sharpe(s, semilla=500))
    assert (_met.bootstrap_sharpe(s, semilla=500)
            != _met.bootstrap_sharpe(s, semilla=501))


def test_bootstrap_sharpe_respeta_el_alpha():
    s = _serie(n=400)
    a90 = _met.bootstrap_sharpe(s, semilla=500, alpha=0.10)
    a99 = _met.bootstrap_sharpe(s, semilla=500, alpha=0.01)
    assert (a99[1] - a99[0]) > (a90[1] - a90[0])


def test_bootstrap_sharpe_conserva_los_valores_congelados_del_diseno():
    """backtest/DISEÑO.md §8.5 congela bloques de 10 días y 2.000 réplicas.
    La migración cambió el MÉTODO (circular), no la parametrización."""
    par = _inspect.signature(_met.bootstrap_sharpe).parameters
    assert par["bloque"].default == 10
    assert par["replicas"].default == 2000


def test_bootstrap_sharpe_devuelve_None_con_pocos_dias():
    assert _met.bootstrap_sharpe(_serie(n=10), semilla=500) is None


def test_bootstrap_sharpe_delega_en_inferencia():
    """Un solo bootstrap en el repo: si metricas volviera a tener el suyo,
    volverían a divergir."""
    fuente = open(_met.__file__, encoding="utf-8").read()
    assert "inferencia.bootstrap_bloques" in fuente
    assert "rng.integers" not in fuente      # ya no remuestrea por su cuenta


def test_la_corrida_sella_semilla_y_alpha_del_bootstrap():
    from datetime import date as _date
    r = motorbt.correr(_date(2026, 7, 1), _date(2026, 7, 8),
                       cuales=("B0",), etiqueta="dry-run", escribir=False,
                       semilla_bootstrap=77, alpha_bootstrap=0.05)
    bs = r["parametros"]["bootstrap"]
    assert bs["semilla"] == 77 and bs["alpha"] == 0.05
    assert bs["bloque_dias"] == 10 and bs["replicas"] == 2000
    assert "circular" in bs["metodo"]
    md = motorbt._resumen_md(r)
    assert "semilla 77" in md and "IC 95%" in md


def test_el_redondeo_del_intervalo_vive_en_presentacion():
    assert motorbt._ic((-2.092099002889191, 0.27820064420958623)) == "[-2.09, 0.28]"
    assert motorbt._ic(None) == "—"


def test_la_errata_del_registro_historico_esta_al_pie_y_no_reescribe():
    """El resumen histórico conserva sus cifras; la errata se añade al pie."""
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "backtest", "resultados",
                        "20260726-032635-humo-legacy", "resumen.md")
    texto = open(ruta, encoding="utf-8").read()
    assert "ERRATA documentada" in texto
    assert "NO circular" in texto
    assert "NO-CONCLUYENTE" in texto
    # las cifras originales siguen ahí
    assert "B2 vs B1 | 0.384 | 2.57 | 35 | aporta" in texto
