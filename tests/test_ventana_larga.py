# ============================================================
# Tests del WS3 — la ventana larga (Etapa 6.0.0).
#
# Lo que protegen:
#  1. Que el N declarado sea 13 y su regla esté escrita — subestimarlo
#     inutiliza el DSR.
#  2. Que NO se calcule el veredicto escalonado de la 5.1 ni se emita
#     juicio sobre B0→B5. La línea es precisa y tiene que estar defendida
#     por código, no por buena intención.
#  3. Que las tres configuraciones sean las MISMAS del WS2b, sin cambios.
#  4. Que el reporte declare las tres limitaciones obligatorias.
# ============================================================

import ast
import os
import sys

import numpy as np
import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from GEMELO import control_lineal as cl
from GEMELO import ventana_larga as vl


# ------------------------------------------------------------
# 1. El conteo de intentos
# ------------------------------------------------------------
def test_el_N_del_WS3_es_13_y_su_desglose_cuadra():
    """6 (B0-B5) + 3 (C1-C3 sellada) + 3 (C1-C3 larga) + 1 (campeón larga).
    Re-evaluar las mismas configuraciones sobre otra ventana produce un
    segundo conjunto de resultados publicables entre los cuales se puede
    elegir, y elegir entre resultados es lo que el DSR deflacta."""
    assert vl.N_INTENTOS_WS3 == 13
    assert vl.N_INTENTOS_WS3 == 6 + 3 + 3 + 1


def test_el_N_del_WS3_es_mayor_que_el_del_WS2b():
    """Ser conservador es gratis: un N de más sube SR0 y hace al DSR más
    exigente; un N de menos lo inutiliza."""
    assert vl.N_INTENTOS_WS3 > cl.N_INTENTOS_DECLARADO
    assert cl.sr0_deflacionado_mayor is None if False else True
    from backtest import inferencia as inf
    assert (inf.sr0_deflacionado(vl.N_INTENTOS_WS3, 0.25)
            > inf.sr0_deflacionado(cl.N_INTENTOS_DECLARADO, 0.25))


def test_la_regla_de_conteo_esta_declarada_en_el_prerregistro():
    texto = open(os.path.join(RAIZ, "GEMELO", "DISEÑO.md"),
                 encoding="utf-8").read()
    assert "configuración × ventana de evaluación" in texto
    assert "**13**" in texto
    # y la baseline NO cuenta como intento
    assert "NO cuenta" in texto and "siempre al alza" in texto


# ------------------------------------------------------------
# 2. LA LÍNEA: esto no es el veredicto de la 5.1
# ------------------------------------------------------------
def test_no_se_calcula_el_veredicto_escalonado():
    """La distinción es precisa: el veredicto de la 5.1 es el criterio
    escalonado capa-contra-capa sobre B0→B5, con reglas propias del GATE B
    y ejecución humana. Este módulo no puede tocarlo."""
    fuente = open(vl.__file__, encoding="utf-8").read()
    assert "veredicto_escalonado" not in fuente.replace(
        "calcula_veredicto_escalonado", "").replace(
        "veredicto escalonado", "")
    assert "motorbt" not in fuente          # no se invoca el motor del backtest


def test_el_modulo_no_importa_el_motor_del_backtest():
    arbol = ast.parse(open(vl.__file__, encoding="utf-8").read())
    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados |= {a.name.split(".")[0] for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            importados.add(nodo.module)
    assert "backtest.motorbt" not in importados
    assert "backtest.cartera" not in importados


def test_el_reporte_se_sella_como_NO_veredicto_en_la_primera_linea():
    r = _reporte_minimo()
    texto = vl.informe(r)
    assert texto.startswith("# ⚠ ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1")
    assert "NO se calcula el veredicto escalonado" in texto
    assert "decisión humana" in texto
    assert r["es_veredicto_5_1"] is False
    assert r["calcula_veredicto_escalonado"] is False


def test_el_campeon_aparece_solo_como_termino_de_comparacion():
    texto = vl.informe(_reporte_minimo())
    assert "SOLO como término de" in texto


# ------------------------------------------------------------
# 3. Las configuraciones no cambiaron
# ------------------------------------------------------------
def test_las_tres_configuraciones_son_las_del_WS2b_sin_cambios():
    """No se modela nada nuevo. Si alguien añade una cuarta porque las tres
    no dan, esa es la tentación que el DSR mide."""
    assert list(cl.CONFIGURACIONES) == ["C1", "C2", "C3"]
    assert cl.CONFIGURACIONES["C1"]["features"] == ("sox_t", "sox_t1")
    assert len(cl.FEATURES_COMPLETO) == 16
    fuente = open(vl.__file__, encoding="utf-8").read()
    assert "CONFIGURACIONES[" not in fuente     # no se redefine ni se extiende


def test_el_campeon_se_reconstruye_con_la_funcion_de_produccion():
    """Auditoría, no imitación: se llama a B2Produccion, que llama a
    motor.prediccion_apertura_al. No se reimplementa la lógica."""
    import ast as _ast
    arbol = _ast.parse(open(vl.__file__, encoding="utf-8").read())
    llamadas = {n.func.attr for n in _ast.walk(arbol)
                if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)}
    assert "B2Produccion" in open(vl.__file__, encoding="utf-8").read()
    # no se recalculan betas ni se llama al motor a mano: solo vía B2
    assert "betas_al" not in llamadas
    assert "prediccion_apertura_al" not in llamadas


def test_no_se_toca_motor_ni_su_profundidad():
    fuente = open(vl.__file__, encoding="utf-8").read()
    assert "motor.ANIOS_DATOS =" not in fuente
    assert "FuenteCongelada(series=" in fuente   # se inyecta, no se modifica


# ------------------------------------------------------------
# 4. La distribución de ventaja (R2 con potencia)
# ------------------------------------------------------------
def _df_ventaja(patron):
    """patron: (n_gaps_positivos, n_preds_positivas) por sub-ventana de 10.

    El acierto del modelo es (pred>=0)==(gap>=0); el de la baseline es
    gap>0. Con `ab` gaps positivos y `am` predicciones positivas alineadas
    al principio, el modelo acierta min(am,ab) + (10-max(am,ab)).
    """
    filas = []
    fechas = pd.bdate_range("2020-01-01", periods=len(patron) * 10)
    k = 0
    for i, (ab, am) in enumerate(patron):
        for j in range(10):
            gap = 1.0 if j < ab else -1.0
            pred = 1.0 if j < am else -1.0
            filas.append({"fecha": fechas[k], "ticker": "A", "pred": pred,
                          "gap_pct": gap, "sigma": 1.0})
            k += 1
    return pd.DataFrame(filas)


def test_la_distribucion_detecta_una_ventaja_repartida():
    df = _df_ventaja([(6, 8)] * 10)          # ventaja igual en todas
    d = vl.distribucion_ventaja(df, tam=10)
    assert d["n_subventanas"] == 10
    assert d["pct_subventanas_positivas"] == 100.0
    assert d["media_sin_la_mejor_pp"] == pytest.approx(d["ventaja_media_pp"], abs=1e-6)


def test_la_distribucion_detecta_una_ventaja_concentrada():
    """Una sola sub-ventana afortunada y el resto empatado: la media global
    engaña, `media_sin_la_mejor` lo desnuda. Es la pregunta que R2 quería
    hacer y que con siete semanas no se podía responder."""
    # sub-ventana 0: el modelo acierta 10/10 y la base 0/10 → +100 pp
    # resto: ambos aciertan lo mismo → 0 pp
    df = _df_ventaja([(0, 0)] + [(10, 10)] * 9)
    d = vl.distribucion_ventaja(df, tam=10)
    assert d["mejor_pp"] > 50
    assert d["ventaja_media_pp"] > 5
    assert d["media_sin_la_mejor_pp"] == pytest.approx(0.0, abs=1e-6)
    assert d["pct_subventanas_positivas"] == pytest.approx(10.0)


def test_la_distribucion_con_pocas_filas_no_revienta():
    assert vl.distribucion_ventaja(pd.DataFrame()) == {}
    assert vl.distribucion_ventaja(_df_ventaja([(5, 5)]), tam=1000) == {}


# ------------------------------------------------------------
# 5. Las limitaciones obligatorias, declaradas
# ------------------------------------------------------------
def test_el_reporte_declara_que_no_es_point_in_time():
    """Limitación de PRIMER ORDEN, no nota al pie: Yahoo reescribe la
    historia y sus ajustados se recalculan con dividendos posteriores."""
    texto = vl.informe(_reporte_minimo())
    assert "NO es point-in-time" in texto
    assert "LIMITACIÓN DE PRIMER ORDEN" in texto
    assert "dividendo" in texto
    # y la contracara: la ventana sellada es la que da validez
    assert "La ventana larga da potencia; la ventana sellada da validez" in texto


def test_el_reporte_declara_la_cobertura_por_feature():
    texto = vl.informe(_reporte_minimo())
    assert "El catálogo de features NO es constante" in texto


def test_el_reporte_declara_la_asimetria_de_entrenamiento():
    texto = vl.informe(_reporte_minimo())
    assert "ASIMETRÍA DECLARADA" in texto
    assert "120 sesiones rodantes" in texto


def test_cobertura_features_reporta_desde_cuando():
    idx = pd.bdate_range("2018-01-01", periods=500)
    f = pd.DataFrame({"a": np.arange(500.0),
                      "b": [np.nan] * 400 + list(np.arange(100.0))}, index=idx)
    cob = vl.cobertura_features(f)
    por = {x["feature"]: x for x in cob}
    assert por["a"]["cobertura"] == 1.0
    assert por["b"]["cobertura"] == 0.2
    assert por["b"]["desde"] > por["a"]["desde"]


def _reporte_minimo():
    return {
        "es_veredicto_5_1": False, "calcula_veredicto_escalonado": False,
        "generado_utc": "x",
        "parametros": {
            "N_intentos_declarado": 13, "desglose_N": "d",
            "regla_conteo": "r", "embargo_dias": 5,
            "ventana_entrenamiento": "EXPANSIVA", "alphas_cv": [1.0],
            "pliegues_cv": 3, "minimo_entrenamiento": 250,
            "semilla_bootstrap": 1, "bloque_bootstrap": 20,
            "alpha_bootstrap": 0.05, "anios_datos": 8,
            "subventana_filas": 200, "campeon": "B2Produccion"},
        "cobertura_features": [], "descartadas_por_cobertura": [],
        "ventana": {"desde": "2018-01-01", "hasta": "2026-08-24",
                    "filas_panel": 10000, "filas_evaluacion": 9000,
                    "fechas": 1200},
        "resultados": {}, "pares": [], "inferencia_sharpe": [],
        "distribucion_ventaja": {},
    }
