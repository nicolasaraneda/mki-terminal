# ============================================================
# Tests del control lineal (Etapa 6.0.0 WS2b).
#
# Lo que protegen, por orden de importancia:
#  1. Que el walk-forward NO mire el futuro: ni la ridge, ni la elección
#     de alpha, ni la estandarización.
#  2. Que las tres configuraciones y el N declarado no se muevan sin que
#     alguien se entere — un DSR con el N mal contado miente hacia arriba.
#  3. Que el reporte se selle como NO-veredicto de la 5.1.
#
# Todo sintético: no se descarga nada ni se toca ninguna base.
# ============================================================

import inspect
import math
import os
import sys

import numpy as np
import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from GEMELO import control_lineal as cl


# ------------------------------------------------------------
# 1. Las configuraciones y el conteo de intentos
# ------------------------------------------------------------
def test_son_exactamente_tres_configuraciones():
    assert list(cl.CONFIGURACIONES) == ["C1", "C2", "C3"]


def test_C1_es_el_control_de_informacion():
    """C1 debe usar EXACTAMENTE el insumo del campeón: el SOX, t y t-1. Si
    alguien le añade una feature, deja de ser el control y la comparación
    C2 vs C1 deja de separar información de maquinaria."""
    assert cl.CONFIGURACIONES["C1"]["features"] == ("sox_t", "sox_t1")
    assert cl.CONFIGURACIONES["C1"]["agrupado"] is True


def test_C2_y_C3_usan_el_catalogo_completo_de_16():
    assert len(cl.FEATURES_COMPLETO) == 16
    assert cl.CONFIGURACIONES["C2"]["features"] == cl.FEATURES_COMPLETO
    assert cl.CONFIGURACIONES["C3"]["features"] == cl.FEATURES_COMPLETO
    assert cl.CONFIGURACIONES["C3"]["agrupado"] is False


def test_el_N_declarado_es_9_y_cuadra_con_las_configuraciones():
    """3 configuraciones + 6 baselines B0-B5 = 9, declarado ANTES de correr
    (§4.2 bis). Si alguien añade una cuarta variante sin subir N, este test
    lo caza: un DSR con el N mal contado miente hacia arriba."""
    assert cl.N_INTENTOS_DECLARADO == 9
    assert cl.N_INTENTOS_DECLARADO == len(cl.CONFIGURACIONES) + 6


# ------------------------------------------------------------
# 2. Ridge: mecánica
# ------------------------------------------------------------
def _datos(n=400, p=3, semilla=1):
    rng = np.random.default_rng(semilla)
    X = rng.normal(0, 1, (n, p))
    y = X @ np.array([1.5, -0.5, 0.0][:p]) + rng.normal(0, 1, n)
    return X, y


def test_ridge_recupera_los_coeficientes_con_alpha_pequena():
    X, y = _datos()
    m = cl.ajustar_ridge(X, y, alpha=1e-6)
    # coeficientes en unidades estandarizadas: el signo y el orden se conservan
    assert m["coef"][0] > 0 and m["coef"][1] < 0
    assert abs(m["coef"][0]) > abs(m["coef"][1]) > abs(m["coef"][2])


def test_mas_regularizacion_encoge_los_coeficientes():
    X, y = _datos()
    normas = [np.linalg.norm(cl.ajustar_ridge(X, y, a)["coef"])
              for a in (0.1, 1.0, 10.0, 100.0, 1000.0)]
    assert all(b < a for a, b in zip(normas, normas[1:]))


def test_la_estandarizacion_usa_solo_el_entrenamiento():
    """Estandarizar con estadísticos de todo el histórico filtraría
    información de evaluación por la puerta de atrás."""
    X, y = _datos()
    m = cl.ajustar_ridge(X[:200], y[:200], 1.0)
    assert m["mu"] == pytest.approx(X[:200].mean(axis=0))
    assert m["sd"] == pytest.approx(X[:200].std(axis=0))


def test_ridge_tolera_una_columna_constante():
    X, y = _datos()
    X[:, 2] = 7.0
    m = cl.ajustar_ridge(X, y, 1.0)
    assert np.isfinite(m["coef"]).all() and m["sigma"] > 0


def test_elegir_alpha_devuelve_uno_de_la_grilla():
    X, y = _datos(n=600)
    orden = np.arange(600)
    a = cl.elegir_alpha(X, y, orden)
    assert a in cl.ALPHAS_CV


def test_elegir_alpha_no_usa_datos_posteriores_al_pliegue():
    """La CV es TEMPORAL y expansiva: alterar el futuro de la ventana no
    puede cambiar el alpha elegido a partir de su pasado."""
    X, y = _datos(n=800)
    orden = np.arange(800)
    a_completo = cl.elegir_alpha(X[:600], y[:600], orden[:600])
    y_sucio = y.copy()
    y_sucio[600:] = 1e6              # se ensucia SOLO el futuro
    a_con_futuro_sucio = cl.elegir_alpha(X[:600], y_sucio[:600], orden[:600])
    assert a_completo == a_con_futuro_sucio


# ------------------------------------------------------------
# 3. Walk-forward: el embargo y la ausencia de fuga
# ------------------------------------------------------------
def _panel(n_dias=900, tickers=("A", "B"), semilla=5):
    rng = np.random.default_rng(semilla)
    fechas = pd.bdate_range(end="2026-08-21", periods=n_dias)
    filas = []
    for f in fechas:
        sox = rng.normal(0, 1.2)
        for t in tickers:
            filas.append({"fecha": f, "ticker": t, "sox_t": sox,
                          "sox_t1": rng.normal(0, 1.2),
                          "gap_pct": 0.6 * sox + rng.normal(0, 1.0)})
    return pd.DataFrame(filas)


def test_el_walk_forward_respeta_el_embargo():
    """Ninguna fila con fecha posterior a (emisión − embargo) puede entrar
    al entrenamiento. Se comprueba ensuciando exactamente ese tramo."""
    panel = _panel()
    ev = panel[panel["fecha"] >= "2026-08-10"].copy()
    limpio = cl.correr_configuracion("C1", panel, ev, embargo_dias=5)

    sucio = panel.copy()
    dentro = ((sucio["fecha"] > pd.Timestamp("2026-08-05"))
              & (sucio["fecha"] <= pd.Timestamp("2026-08-21")))
    sucio.loc[dentro, "gap_pct"] = 1e4      # basura DENTRO del embargo
    con_basura = cl.correr_configuracion("C1", sucio, ev, embargo_dias=5)

    assert not limpio.empty
    # las predicciones del primer día evaluado no pueden haber cambiado
    a = limpio[limpio["fecha"] == limpio["fecha"].min()]["pred"].to_numpy()
    b = con_basura[con_basura["fecha"] == limpio["fecha"].min()]["pred"].to_numpy()
    assert a == pytest.approx(b, rel=1e-12)


def test_sin_embargo_la_basura_de_la_frontera_SI_contamina():
    """Contraprueba: el test de arriba tiene que poder fallar. Con embargo
    0 la misma basura entra al entrenamiento y mueve las predicciones."""
    panel = _panel()
    ev = panel[panel["fecha"] >= "2026-08-10"].copy()
    limpio = cl.correr_configuracion("C1", panel, ev, embargo_dias=0)
    sucio = panel.copy()
    dentro = ((sucio["fecha"] > pd.Timestamp("2026-08-05"))
              & (sucio["fecha"] <= pd.Timestamp("2026-08-09")))
    sucio.loc[dentro, "gap_pct"] = 1e4
    con_basura = cl.correr_configuracion("C1", sucio, ev, embargo_dias=0)
    f0 = limpio["fecha"].min()
    a = limpio[limpio["fecha"] == f0]["pred"].to_numpy()
    b = con_basura[con_basura["fecha"] == f0]["pred"].to_numpy()
    assert not np.allclose(a, b)


def test_el_walk_forward_nunca_entrena_con_el_futuro():
    """Alterar el panel DESPUÉS de la última fecha evaluada no puede
    cambiar ninguna predicción."""
    panel = _panel()
    ev = panel[(panel["fecha"] >= "2026-07-01")
               & (panel["fecha"] <= "2026-08-01")].copy()
    base = cl.correr_configuracion("C2" if False else "C1", panel, ev)
    futuro = panel.copy()
    futuro.loc[futuro["fecha"] > pd.Timestamp("2026-08-01"), "gap_pct"] = -1e4
    otro = cl.correr_configuracion("C1", futuro, ev)
    pd.testing.assert_frame_equal(base, otro)


def test_la_configuracion_por_ticker_entrena_por_separado():
    panel = _panel(n_dias=1200)
    ev = panel[panel["fecha"] >= "2026-08-10"].copy()
    ev = ev.assign(**{c: ev[c] for c in cl.FEATURES_COMPLETO if c in ev.columns})
    agrupado = cl.correr_configuracion("C1", panel, ev)
    # en agrupado, todos los tickers de un día comparten n_train
    por_dia = agrupado.groupby("fecha")["n_train"].nunique()
    assert (por_dia == 1).all()


# ------------------------------------------------------------
# 4. Métricas
# ------------------------------------------------------------
def test_crps_normal_en_el_centro_es_el_valor_conocido():
    """CRPS(N(0,1), 0) = 2·φ(0) − 1/√π."""
    esperado = 2 / math.sqrt(2 * math.pi) - 1 / math.sqrt(math.pi)
    assert cl.crps_normal([0.0], [0.0], [1.0])[0] == pytest.approx(esperado, abs=1e-9)


def test_crps_empeora_al_alejarse_y_escala_con_sigma():
    a = cl.crps_normal([0.0], [0.0], [1.0])[0]
    b = cl.crps_normal([2.0], [0.0], [1.0])[0]
    c = cl.crps_normal([0.0], [0.0], [2.0])[0]
    assert b > a and c > a


def test_el_acierto_usa_la_convencion_del_verificador():
    """(pred >= 0) == (gap >= 0), la misma de senales.py."""
    assert list(cl._acierto([1.0, -1.0, 0.0], [2.0, 1.0, 0.0])) == [1, 0, 1]


def test_mcnemar_reproduce_la_variante_con_correccion():
    assert round(cl._mcnemar(67, 55), 4) == 0.3193


def test_comparar_usa_solo_las_filas_que_ambos_predijeron():
    """Comparar sobre conjuntos distintos mezclaría la diferencia de modelo
    con la de cobertura."""
    a = pd.DataFrame({"fecha": ["d1", "d2"], "ticker": ["A", "A"],
                      "pred": [1.0, 1.0], "gap_pct": [1.0, -1.0],
                      "sigma": [1.0, 1.0]})
    b = pd.DataFrame({"fecha": ["d1"], "ticker": ["A"], "pred": [-1.0],
                      "gap_pct": [1.0], "sigma": [1.0]})
    r = cl.comparar(a, b, "A", "B")
    assert r["n"] == 1


def test_el_sharpe_con_pocos_dias_se_declara_NO_INTERPRETABLE():
    """Un Sharpe anualizado sobre 30 días es un artefacto de multiplicar
    por √252, y el DSR satura en 1.0000 — que se leería como que V5 está
    superado. El instrumento debe negarse, no emitir el número."""
    res = {"X": {"sharpe_ls_sin_costos": 5.7, "dias": 30},
           "Y": {"sharpe_ls_sin_costos": 5.5, "dias": 30}}
    # El N va explícito desde el 1-sep-2026: `inferencia_sharpe` dejó de
    # tener default. Ver su docstring — el default de 9 regalaba 0.63 de
    # umbral y daba vuelta V5 a Sharpe realista.
    filas = cl.inferencia_sharpe(res, n_intentos=9)
    assert all(f["interpretable"] is False for f in filas)
    assert all(f["dsr"] == "NO INTERPRETABLE" for f in filas)
    assert cl.MINIMO_DIAS_SHARPE >= 60


def test_con_dias_suficientes_el_dsr_si_se_reporta():
    res = {"X": {"sharpe_ls_sin_costos": 0.8, "dias": 500},
           "Y": {"sharpe_ls_sin_costos": 0.4, "dias": 500}}
    # El N va explícito desde el 1-sep-2026: `inferencia_sharpe` dejó de
    # tener default. Ver su docstring — el default de 9 regalaba 0.63 de
    # umbral y daba vuelta V5 a Sharpe realista.
    filas = cl.inferencia_sharpe(res, n_intentos=9)
    assert all(isinstance(f["dsr"], float) for f in filas)
    assert all(f["N_intentos"] == 9 for f in filas)


def test_R2_se_aplica_por_fechas_y_puede_descartar():
    df = pd.DataFrame({
        "fecha": pd.to_datetime(["2026-07-16"] * 10 + ["2026-08-05"] * 10),
        "ticker": ["A"] * 20,
        "pred": [1.0] * 10 + [1.0] * 10,
        "gap_pct": [1.0] * 10 + [-1.0] * 10,
        "sigma": [1.0] * 20,
    })
    completo = cl._acierto(df["pred"], df["gap_pct"]).mean()
    r2 = cl.evaluar_r2(df, "X")
    assert r2["n"] == 10                     # se excluyó la ventana de julio
    assert r2["acierto_pct"] == 0.0          # fuera de ella, todo falla
    assert completo == 0.5
    assert cl.VENTANA_R2 == ("2026-07-15", "2026-07-23")


# ------------------------------------------------------------
# 5. El reporte y el aislamiento
# ------------------------------------------------------------
def test_el_reporte_se_sella_como_NO_veredicto_de_la_5_1():
    from GEMELO import experimento
    r = {"es_veredicto_5_1": False, "generado_utc": "x", "n_sellado": 223,
         "n_panel": 10, "parametros": {
             "N_intentos_declarado": 9, "desglose_N": "d", "embargo_dias": 5,
             "ventana_entrenamiento": "EXPANSIVA", "alphas_cv": [1.0],
             "pliegues_cv": 3, "minimo_entrenamiento": 250,
             "semilla_bootstrap": 1, "bloque_bootstrap": 20,
             "alpha_bootstrap": 0.05, "anios_datos": 8,
             "convencion_empate": "excluir_cero (§2.8)"},
         "descartadas_por_cobertura": [], "resultados": {}, "pares": [],
         "inferencia_sharpe": [], "r2_por_configuracion": [],
         "alpha_por_fold": {}}
    texto = experimento.informe(r)
    assert texto.startswith("# ⚠ ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1")
    assert "sigue sin cumplirse" in texto
    assert r["es_veredicto_5_1"] is False


def test_el_reporte_declara_la_asimetria_de_ventana():
    """El retador entrena sobre años; el campeón usa 120 sesiones rodantes.
    Es parte de lo que se mide y tiene que estar escrito, no supuesto."""
    from GEMELO import experimento
    fuente = open(experimento.__file__, encoding="utf-8").read()
    assert "ASIMETRÍA DECLARADA" in fuente
    assert "120 sesiones rodantes" in fuente


def test_el_reporte_sella_todos_los_parametros():
    from GEMELO import experimento
    fuente = open(experimento.__file__, encoding="utf-8").read()
    for clave in ("N_intentos_declarado", "embargo_dias", "alphas_cv",
                  "semilla_bootstrap", "bloque_bootstrap", "alpha_bootstrap",
                  "ventana_entrenamiento"):
        assert clave in fuente, clave


def test_control_lineal_no_importa_el_camino_de_sellado():
    """Por AST y no por grep: el docstring del módulo NOMBRA senales.py y
    snapshot.py para decir que no los toca, y un grep de texto se tragaría
    justo esa frase. Lo que importa son los imports reales."""
    import ast
    arbol = ast.parse(open(cl.__file__, encoding="utf-8").read())
    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados |= {a.name.split(".")[0] for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            importados.add(nodo.module.split(".")[0])
    assert importados <= {"math", "numpy", "pandas", "backtest"}, importados


def test_control_lineal_no_escribe_ni_descarga():
    """El modelado es puro: recibe features y etiquetas ya construidas."""
    fuente = open(cl.__file__, encoding="utf-8").read()
    for prohibido in ("sqlite3", "get_connection", "yf.download",
                      "to_csv", "open("):
        assert prohibido not in fuente, prohibido


def test_el_camino_de_sellado_no_importa_GEMELO():
    """LA dirección que importa para el sello: un fallo en GEMELO no puede
    tocar snapshot.py. Se comprueba al revés de como se suele mirar."""
    for archivo in ("snapshot.py", "senales.py", "alertas.py", "motor.py",
                    "mki_backup.py", "mki_vigia.py", "mki_noticias.py"):
        ruta = os.path.join(RAIZ, archivo)
        if os.path.exists(ruta):
            assert "GEMELO" not in open(ruta, encoding="utf-8").read(), archivo


def test_inferencia_sharpe_no_tiene_valor_por_defecto_para_el_N():
    """1-sep-2026, quinta corrida. Cuarta regla de la casa.

    `inferencia_sharpe` tenía `n_intentos: int = N_INTENTOS_DECLARADO` (9)
    y `experimento.py` la llamaba sin pasar N, consumiendo a ciegas el
    conteo más rancio del repo — mientras `backtest/inferencia.py` había
    quitado ese mismo default a propósito, con acta (§26.1) y con un test
    que lo exige. La defensa estaba anulada desde adentro.

    Medido: SR0(9) = 0.9986 contra SR0(86) = 1.6266. El default regalaba
    0.63 de umbral, y a Sharpe anualizado de 1.2-1.5 el veredicto V5 se
    daba vuelta de PASA a NO PASA. Era un vector vivo.
    """
    import inspect
    from GEMELO import control_lineal as cl
    p = inspect.signature(cl.inferencia_sharpe).parameters["n_intentos"]
    assert p.default is inspect.Parameter.empty, (
        "`n_intentos` volvió a tener valor por defecto. Un DSR con un N que "
        "alguien olvidó actualizar miente, y miente hacia arriba.")
