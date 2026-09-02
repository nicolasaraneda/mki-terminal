"""Tests de los cuatro módulos de la séptima corrida en `GEMELO/SECUENCIAL/`
(`horizonte`, `trayectoria`, `autocorrelacion`, `estimandos`). Exigidos por
el guardián al cierre: 1.056 líneas de estadística nueva producían cifras
en documentos de resultados sin un solo test. Sin red, sin bases: se
prueban las funciones puras contra valores cerrados y series sintéticas, y
el aislamiento de los cuatro respecto de la ruta de sellado.
"""
import ast
import math
import os

import numpy as np
import pytest

from GEMELO.SECUENCIAL import autocorrelacion as ac
from GEMELO.SECUENCIAL import estimandos as es
from GEMELO.SECUENCIAL import horizonte as hz
from GEMELO.SECUENCIAL import trayectoria as tr

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------- horizonte ----------------
def test_potencia_analitica_bajo_la_nula_es_alfa():
    assert hz.potencia_analitica(0.0, 0.05) == pytest.approx(0.05, abs=1e-9)


def test_dias_para_potencia_y_mde_son_inversas():
    se, k = 0.0855, 35
    for delta in (0.05, 0.065, 0.09, 0.12):
        D = hz.dias_para_potencia(delta, se, k)
        assert hz.mde_a(D, se, k) == pytest.approx(delta, rel=1e-9)
        # y a esos días la potencia analítica es 0,80
        assert hz.potencia_analitica(delta, se * math.sqrt(k / D)) == pytest.approx(0.80, abs=1e-6)


def test_el_se_escala_como_uno_sobre_raiz_de_dias():
    se, k = 0.08, 35
    assert hz.mde_a(4 * k, se, k) == pytest.approx(hz.mde_a(k, se, k) / 2, rel=1e-9)


def test_la_simulacion_bajo_la_nula_no_rechaza_de_mas():
    """Días sintéticos con media cero: el α empírico de la permutación de signo
    por día queda cerca del nominal (Wilson holgado para 200 réplicas)."""
    rng = np.random.default_rng(1)
    grupos = [rng.normal(0, 1, size=7) for _ in range(35)]
    a = hz.potencia_simulada(grupos, 0.0, 35, n_sim=200, n_perm=400)
    assert 0.01 <= a <= 0.11


def test_la_simulacion_detecta_un_efecto_grande():
    rng = np.random.default_rng(2)
    grupos = [rng.normal(0, 1, size=7) for _ in range(35)]
    assert hz.potencia_simulada(grupos, 1.0, 35, n_sim=100, n_perm=400) > 0.95


# ---------------- trayectoria ----------------
def test_binomial_bilateral_valores_conocidos():
    assert tr._binomial_bilateral(0, 0) == 1.0
    assert tr._binomial_bilateral(5, 10) == pytest.approx(1.0)
    assert tr._binomial_bilateral(0, 10) == pytest.approx(2 / 1024)
    assert tr._binomial_bilateral(6, 17) == pytest.approx(0.3323, abs=1e-3)   # el «11-6»


def test_el_proceso_de_apuestas_es_valido_y_conservador():
    """Bajo la nula exacta (x ≡ μ₀) el capital no crece; con x ≡ 1 crece
    monótono; y nunca es ≤ 0 (λ < 1/μ₀ garantiza 1 + λ(x−μ₀) > 0)."""
    K0 = tr.proceso_apuestas(np.full(40, 0.5))
    assert np.allclose(K0, 1.0)
    K1 = tr.proceso_apuestas(np.ones(40))
    assert np.all(np.diff(K1) > 0) and K1[-1] > 20
    Kmin = tr.proceso_apuestas(np.zeros(200))
    assert np.all(Kmin > 0)


def test_el_proceso_de_apuestas_no_rechaza_de_mas_bajo_la_nula():
    """Anytime-valid: P(sup K_t ≥ 1/α) ≤ α. Con 300 series nulas de 60 días,
    los cruces de 20 tienen que ser pocos (cota 0,05; holgura de MC)."""
    rng = np.random.default_rng(3)
    cruces = sum(tr.proceso_apuestas(rng.uniform(0, 1, size=60)).max() >= 20 for _ in range(300))
    assert cruces / 300 <= 0.08


# ---------------- autocorrelacion ----------------
def test_las_autocorrelaciones_recuperan_un_ar1():
    rng = np.random.default_rng(4)
    phi, n = 0.4, 20000
    x = np.empty(n)
    x[0] = rng.normal()
    for i in range(1, n):
        x[i] = phi * x[i - 1] + rng.normal()
    a = ac.autocorrelaciones(x, 3)
    assert a[0] == pytest.approx(phi, abs=0.03)
    assert a[1] == pytest.approx(phi ** 2, abs=0.03)


def test_hac_con_rezago_cero_es_la_z_iid_y_los_bloques_reducen_a_la_suma():
    rng = np.random.default_rng(5)
    d = rng.normal(size=200)
    z_dia = ac._z_dia(d)
    z_hac0 = ac._z_hac(d, 0)
    # HAC con L=0 usa varianza poblacional (n) y DIA muestral (n−1): difieren en √(n/(n−1))
    assert z_hac0 == pytest.approx(z_dia * math.sqrt(200 / 199), rel=1e-9)
    assert ac._z_bloque(d, 100) == 0.0          # 2 bloques: no puede cruzar
    assert abs(ac._z_bloque(d, 10)) < 4


def test_el_ic_de_ac1_por_bloques_contiene_el_valor_de_un_ar1():
    rng = np.random.default_rng(6)
    phi, n = 0.3, 600
    x = np.empty(n)
    x[0] = rng.normal()
    for i in range(1, n):
        x[i] = phi * x[i - 1] + rng.normal()
    lo, hi = ac.ic_ac1_bootstrap_bloques(x, bloque=20, n_boot=300)
    assert lo < phi < hi


# ---------------- estimandos ----------------
def test_la_pendiente_recupera_una_relacion_lineal_exacta():
    import pandas as pd
    df = pd.DataFrame({"x": np.arange(10.0), "y": 3.0 + 1.42 * np.arange(10.0)})
    assert es._pendiente(df, "x", "y") == pytest.approx(1.42, rel=1e-12)
    assert math.isnan(es._pendiente(pd.DataFrame({"x": [1.0, 1.0], "y": [1.0, 2.0]}), "x", "y"))


def test_los_estimandos_por_fila_tienen_las_identidades_declaradas():
    import pandas as pd
    df = pd.DataFrame({"apertura_estimada_pct": [1.0, -1.0, -1.0, 2.0],
                       "gap_pct": [2.0, -3.0, 1.0, -1.0],
                       "exchange": ["XTKS", "XKRX", "XTAI", "XETR"],
                       "fecha": ["d"] * 4})
    out = es._preparar(df)
    # E0: (modelo acierta) − (siempre al alza acierta) ∈ {−1, 0, 1}
    assert out["E0"].tolist() == [0.0, 1.0, -1.0, 0.0]
    # E2 sólo es ≠ 0 en las bajas predichas: g·(signo p − 1) = −2g
    assert out["E2"].tolist() == [0.0, 6.0, -2.0, 0.0]
    assert out["h"].tolist() == [1.75, 1.75, 2.75, 8.75]


# ---------------- aislamiento de los cuatro ----------------
@pytest.mark.parametrize("modulo", [hz, tr, ac, es])
def test_ningun_modulo_nuevo_importa_la_ruta_de_sellado(modulo):
    arbol = ast.parse(open(modulo.__file__, encoding="utf-8").read())
    mods = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            mods += [a.name for a in nodo.names]
        elif isinstance(nodo, ast.ImportFrom):
            mods.append(nodo.module or "")
    for prohibido in ("snapshot", "senales", "alertas", "mki_vigia", "mki_noticias",
                      "mki_backup", "app", "sqlite3", "yfinance"):
        assert not any(m == prohibido or m.startswith(prohibido + ".") for m in mods), (modulo.__name__, mods)
    # la lectura de lo sellado va por la capa auditada
    assert any(m.startswith("backtest") for m in mods)
