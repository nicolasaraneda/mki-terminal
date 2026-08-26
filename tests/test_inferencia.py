# ============================================================
# Tests de backtest/inferencia.py (Etapa 6.0.0 WS1).
#
# Dos capas:
#  1. Valores de referencia — que los números salgan exactos contra tablas
#     conocidas. Es lo que permite auditar la bisección sin coeficientes
#     mágicos.
#  2. Tests de PROPIEDAD — que las funciones se comporten como la teoría
#     dice, para cualquier entrada. Son los que de verdad protegen: un
#     valor de referencia se puede acertar por casualidad, una monotonía
#     sobre 20 puntos no.
#
# Funciones puras: no se toca ninguna base ni se descarga nada.
# ============================================================

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest import inferencia as inf


# ------------------------------------------------------------
# 1. Valores de referencia
# ------------------------------------------------------------
@pytest.mark.parametrize("x, esperado", [
    (0.0, 0.5), (1.0, 0.8413447461), (1.96, 0.9750021049),
])
def test_Phi_reproduce_valores_tabulados(x, esperado):
    assert round(inf.Phi(x), 10) == esperado


@pytest.mark.parametrize("p, esperado", [
    (0.975, 1.9599639845), (0.95, 1.6448536270),
])
def test_Phi_inv_reproduce_valores_tabulados(p, esperado):
    assert round(inf.Phi_inv(p), 10) == esperado


@pytest.mark.parametrize("N, V, esperado", [
    (2, 0.25, 0.2598776721), (2, 1.0, 0.5197553443),
    (5, 0.25, 0.5962970005), (6, 0.25, 0.6500703939),
    (10, 0.25, 0.7872991507), (20, 0.25, 0.9503539756),
])
def test_sr0_deflacionado_reproduce_la_referencia(N, V, esperado):
    assert round(inf.sr0_deflacionado(N, V), 10) == esperado


@pytest.mark.parametrize("sr, n, skew, kurt, var, se", [
    (1.0, 1000, 0.0, 3.0, 0.001501501502, 0.0387492129),
    (1.0, 1000, -0.5, 6.0, 0.002752752753, 0.0524666823),
    (0.5, 252, 0.0, 3.0, 0.004482071713, 0.0669482764),
])
def test_var_sharpe_reproduce_la_referencia(sr, n, skew, kurt, var, se):
    assert round(inf.var_sharpe(sr, n, skew, kurt), 12) == var
    assert round(inf.se_sharpe(sr, n, skew, kurt), 10) == se


def test_dsr_reproduce_la_referencia():
    assert round(inf.dsr(0.5, 1000, 0.0, 3.0, 6, 0.25), 10) == 0.0000038746


# ------------------------------------------------------------
# 2. Propiedades — Phi
# ------------------------------------------------------------
def test_Phi_y_su_inversa_son_inversas():
    for p in (0.001, 0.05, 0.25, 0.5, 0.75, 0.95, 0.999):
        assert inf.Phi(inf.Phi_inv(p)) == pytest.approx(p, abs=1e-12)


def test_Phi_es_monotona_y_simetrica():
    xs = [-3.0, -1.0, -0.1, 0.0, 0.1, 1.0, 3.0]
    valores = [inf.Phi(x) for x in xs]
    assert valores == sorted(valores)
    for x in (0.3, 1.0, 2.5):
        assert inf.Phi(-x) == pytest.approx(1 - inf.Phi(x), abs=1e-14)


def test_Phi_inv_rechaza_fuera_del_dominio():
    for p in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(ValueError):
            inf.Phi_inv(p)


# ------------------------------------------------------------
# 3. Propiedades — PSR
# ------------------------------------------------------------
@pytest.mark.parametrize("sr, n, skew, kurt", [
    (1.0, 1000, 0.0, 3.0), (0.3, 60, -1.2, 8.0),
    (2.5, 5000, 0.7, 4.5), (0.01, 30, 0.0, 3.0),
])
def test_psr_es_exactamente_medio_cuando_sr_iguala_la_referencia(sr, n, skew, kurt):
    """Propiedad estructural: la incertidumbre no mueve el punto medio,
    solo la pendiente con que se sale de él."""
    assert inf.psr(sr, sr, n, skew, kurt) == 0.5


def test_psr_crece_con_el_sharpe_y_decrece_con_la_referencia():
    # Se prueba en la zona INFORMATIVA: con SR muy por encima de la
    # referencia, Phi satura en 1.0 y la monotonía deja de ser estricta
    # (ver test_phi_satura_y_un_psr_de_1_no_es_certeza).
    base = inf.psr(0.60, 0.50, 1000, 0.0, 3.0)
    assert inf.psr(0.65, 0.50, 1000, 0.0, 3.0) > base
    assert inf.psr(0.60, 0.55, 1000, 0.0, 3.0) < base


def test_psr_crece_con_mas_observaciones():
    """El mismo Sharpe con más historia es más creíble."""
    assert (inf.psr(1.0, 0.5, 2000, 0.0, 3.0)
            > inf.psr(1.0, 0.5, 250, 0.0, 3.0))


# ------------------------------------------------------------
# 4. Propiedades — la corrección de Lo
# ------------------------------------------------------------
def test_asimetria_negativa_y_colas_gruesas_ensanchan_la_varianza():
    """LA RAZÓN DE SER de la corrección: con el MISMO sr y n, retornos con
    skew negativa y curtosis alta tienen un Sharpe MENOS preciso. Sin esto,
    un Sharpe se presenta con más seguridad de la que tiene."""
    normal = inf.var_sharpe(1.0, 1000, skew=0.0, kurt=3.0)
    feo = inf.var_sharpe(1.0, 1000, skew=-0.5, kurt=6.0)
    assert feo > normal
    # y por tanto el PSR es MENOR: menos confianza en la misma habilidad
    assert (inf.psr(0.60, 0.50, 1000, -0.5, 6.0)
            < inf.psr(0.60, 0.50, 1000, 0.0, 3.0))


def test_var_sharpe_exige_al_menos_dos_observaciones():
    with pytest.raises(ValueError):
        inf.var_sharpe(1.0, 1, 0.0, 3.0)


# ------------------------------------------------------------
# 5. Propiedades — el umbral deflactado
# ------------------------------------------------------------
def test_sr0_crece_monotonamente_con_el_numero_de_intentos():
    """Más intentos, vara más alta. Es el punto entero del DSR."""
    valores = [inf.sr0_deflacionado(N, 0.25) for N in range(2, 40)]
    assert all(b > a for a, b in zip(valores, valores[1:]))


def test_sr0_crece_monotonamente_con_la_varianza_entre_intentos():
    valores = [inf.sr0_deflacionado(10, v) for v in
               (0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0)]
    assert all(b > a for a, b in zip(valores, valores[1:]))


def test_con_un_solo_intento_no_hay_nada_que_deflactar():
    """N<2 → SR0 = 0 por definición, y el DSR se reduce al PSR contra cero."""
    assert inf.sr0_deflacionado(1, 0.25) == 0.0
    assert (inf.dsr(0.8, 500, 0.0, 3.0, 1, 0.25)
            == inf.psr(0.8, 0.0, 500, 0.0, 3.0))


def test_el_dsr_baja_cuando_se_confiesan_mas_intentos():
    """El mismo Sharpe, declarando más búsqueda, vale menos."""
    valores = [inf.dsr(0.7, 1000, 0.0, 3.0, N, 0.25) for N in (5, 10, 20, 50)]
    assert all(b < a for a, b in zip(valores, valores[1:]))


def test_N_intentos_es_obligatorio_y_no_tiene_default():
    """Un DSR con un N que alguien olvidó actualizar miente hacia arriba.
    Obligar a escribirlo en cada llamada es la defensa."""
    import inspect
    for fn, param in ((inf.sr0_deflacionado, "N_intentos"),
                      (inf.dsr, "N_intentos")):
        p = inspect.signature(fn).parameters[param]
        assert p.default is inspect.Parameter.empty, fn.__name__


def test_phi_satura_y_un_psr_de_1_no_es_certeza():
    """Documentado a propósito: por encima de z ~ 8.3, Phi devuelve 1.0
    EXACTO en doble precisión. Un PSR o un DSR que salga 1.0 significa
    "más allá de lo que el doble distingue", no "certeza" — y en la zona
    saturada la monotonía deja de ser estricta. Quien lea un 1.000 en un
    informe tiene que saber esto."""
    assert inf.Phi(8.3) == 1.0
    assert inf.psr(1.2, 0.5, 1000, 0.0, 3.0) == inf.psr(1.0, 0.5, 1000, 0.0, 3.0) == 1.0
    # ...mientras que en la zona informativa sí es estricta
    assert inf.psr(0.65, 0.5, 1000, 0.0, 3.0) > inf.psr(0.60, 0.5, 1000, 0.0, 3.0)


def test_sr0_rechaza_entradas_imposibles():
    with pytest.raises(ValueError):
        inf.sr0_deflacionado(0, 0.25)
    with pytest.raises(ValueError):
        inf.sr0_deflacionado(5, -0.1)


# ------------------------------------------------------------
# 6. El bootstrap de bloques — el test que de verdad lo prueba
# ------------------------------------------------------------
SEMILLA = 20260826


def _serie_iid(n=4000, mu=0.05, sd=1.0, semilla=SEMILLA):
    return np.random.default_rng(semilla).normal(mu, sd, n)


def _serie_ar1(phi, n=4000, mu=0.05, semilla=SEMILLA + 1):
    e = np.random.default_rng(semilla).normal(0.0, 1.0, n)
    y = np.empty(n)
    y[0] = e[0]
    for i in range(1, n):
        y[i] = phi * y[i - 1] + e[i]
    return y + mu


def test_sobre_serie_iid_el_ic_de_bloques_se_parece_al_analitico():
    x = _serie_iid()
    r = inf.bootstrap_bloques(x, semilla=1, bloque=20, anualizar=1)
    sr = inf.sharpe(x, anualizar=1)
    se = inf.se_sharpe(sr, len(x), 0.0, 3.0)
    ancho_analitico = 2 * 1.9599639845 * se
    ancho_bloques = r["hi"] - r["lo"]
    assert 0.75 < ancho_bloques / ancho_analitico < 1.35


@pytest.mark.parametrize("phi", [0.6, 0.8])
def test_con_autocorrelacion_el_ic_de_bloques_es_ESTRICTAMENTE_mas_ancho(phi):
    """EL test del bootstrap. Sobre un AR(1) con phi alto, remuestrear en
    bloques preserva la dependencia y el IC se ensancha; remuestrear iid la
    destruye y el IC sale falsamente estrecho. Si NO sale más ancho, el
    bloque no está haciendo nada y la implementación está mal."""
    y = _serie_ar1(phi)
    bloques = inf.bootstrap_bloques(y, semilla=1, bloque=20, anualizar=1)
    iid = inf.bootstrap_bloques(y, semilla=1, bloque=1, anualizar=1)
    ancho_bloques = bloques["hi"] - bloques["lo"]
    ancho_iid = iid["hi"] - iid["lo"]
    assert ancho_bloques > ancho_iid
    assert ancho_bloques / ancho_iid > 1.3   # y por un margen claro


def test_bloque_uno_es_el_bootstrap_iid():
    """Degenera exactamente en el iid, lo que hace la comparación trivial."""
    x = _serie_iid(n=500)
    r = inf.bootstrap_bloques(x, semilla=7, bloque=1, anualizar=1)
    assert r["bloque"] == 1 and r["n"] == 500
    assert r["lo"] < r["sharpe"] < r["hi"]


def test_el_bootstrap_es_reproducible_con_la_misma_semilla():
    x = _serie_iid(n=1000)
    a = inf.bootstrap_bloques(x, semilla=42, bloque=10, anualizar=1)
    b = inf.bootstrap_bloques(x, semilla=42, bloque=10, anualizar=1)
    c = inf.bootstrap_bloques(x, semilla=43, bloque=10, anualizar=1)
    assert (a["lo"], a["hi"]) == (b["lo"], b["hi"])
    assert (a["lo"], a["hi"]) != (c["lo"], c["hi"])


def test_la_semilla_es_obligatoria():
    """Sin estado global de numpy: un IC que cambia entre corridas no puede
    decidir si un modelo gana."""
    import inspect
    p = inspect.signature(inf.bootstrap_bloques).parameters["semilla"]
    assert p.default is inspect.Parameter.empty


def test_el_ic_es_mas_ancho_cuanto_menor_es_alpha():
    x = _serie_iid(n=2000)
    a90 = inf.bootstrap_bloques(x, semilla=3, bloque=20, alpha=0.10, anualizar=1)
    a99 = inf.bootstrap_bloques(x, semilla=3, bloque=20, alpha=0.01, anualizar=1)
    assert (a99["hi"] - a99["lo"]) > (a90["hi"] - a90["lo"])


def test_series_degeneradas_no_revientan():
    for serie in ([], [1.0], [2.0] * 50):
        r = inf.bootstrap_bloques(serie, semilla=1, bloque=20, anualizar=1)
        assert math.isnan(r["lo"]) or r["n_validos"] == 0


def test_bootstrap_rechaza_parametros_invalidos():
    x = _serie_iid(n=200)
    with pytest.raises(ValueError):
        inf.bootstrap_bloques(x, semilla=1, bloque=0)
    with pytest.raises(ValueError):
        inf.bootstrap_bloques(x, semilla=1, alpha=0.0)


# ------------------------------------------------------------
# 7. El módulo es puro
# ------------------------------------------------------------
def test_el_modulo_no_toca_bases_ni_disco():
    fuente = open(inf.__file__, encoding="utf-8").read()
    for prohibido in ("sqlite3", "open(", "to_csv", "read_sql", "requests"):
        assert prohibido not in fuente, prohibido
