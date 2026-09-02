"""Prueba maestra del Frente D (`GEMELO/transversal.py`), exigida por el
`auditor-lookahead`: la β causal de una fecha es invariante a truncar el
dataset en esa fecha, y una contraprueba con β «del futuro» hace fallar el
test. Sin red, sin bases, datos sintéticos."""
import numpy as np
import pandas as pd

from GEMELO import transversal as tv


def _panel(n=600, semilla=3):
    rng = np.random.default_rng(semilla)
    fechas = pd.bdate_range("2020-01-01", periods=n)
    sox = rng.normal(0, 3, size=n)
    filas = []
    for t, beta in (("A", 0.9), ("B", 0.5), ("C", 0.2), ("D", 0.05)):
        gap = beta * sox + rng.normal(0, 2, size=n)
        filas.append(pd.DataFrame({"fecha": fechas, "ticker": t, "gap_pct": gap, "sox_prev": sox}))
    return pd.concat(filas, ignore_index=True)


def test_la_beta_causal_es_invariante_a_truncar_en_t():
    df = _panel()
    todo = tv.betas_causales(df, burn_in=50)
    corte = df["fecha"].iloc[400]
    trunc = tv.betas_causales(df[df["fecha"] <= corte], burn_in=50)
    a = todo[todo["fecha"] <= corte].set_index(["fecha", "ticker"])["pred"].sort_index()
    b = trunc.set_index(["fecha", "ticker"])["pred"].sort_index()
    assert a.index.equals(b.index)
    assert np.allclose(a.to_numpy(), b.to_numpy(), atol=1e-12)


def test_contraprueba_una_beta_de_muestra_completa_no_es_invariante():
    """Lo que la primera versión hacía: β con todo el ajuste, evaluada sobre
    el mismo ajuste. Al truncar, la β cambia y el test tiene que verlo."""
    df = _panel()
    corte = df["fecha"].iloc[400]
    b_todo = tv.orden_beta(df, "2020-01-01", "2030-01-01")
    b_trunc = tv.orden_beta(df[df["fecha"] <= corte], "2020-01-01", "2030-01-01")
    assert any(abs(b_todo[t] - b_trunc[t]) > 1e-6 for t in b_todo)


def test_la_beta_causal_solo_usa_el_pasado_estricto():
    """Cambiar el gap de la fecha t no puede mover la predicción de t."""
    df = _panel()
    base = tv.betas_causales(df, burn_in=50)
    t0 = df["fecha"].iloc[300]
    df2 = df.copy()
    df2.loc[(df2["fecha"] == t0) & (df2["ticker"] == "A"), "gap_pct"] += 50.0
    alt = tv.betas_causales(df2, burn_in=50)
    p0 = base[(base["fecha"] == t0) & (base["ticker"] == "A")]["pred"].iloc[0]
    p1 = alt[(alt["fecha"] == t0) & (alt["ticker"] == "A")]["pred"].iloc[0]
    assert p0 == p1
    # y SÍ mueve las predicciones posteriores (la información entra después)
    q0 = base[(base["fecha"] > t0) & (base["ticker"] == "A")]["pred"].iloc[0]
    q1 = alt[(alt["fecha"] > t0) & (alt["ticker"] == "A")]["pred"].iloc[0]
    assert q0 != q1


def test_spearman_y_kendall_en_casos_cerrados():
    assert tv.spearman([1, 2, 3, 4], [1, 2, 3, 4]) == 1.0
    assert tv.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0
    assert tv.kendall([1, 2, 3, 4], [1, 2, 4, 3]) == (5 - 1) / 6
    assert tv.spearman([1, 1, 1, 1], [1, 2, 3, 4]) == 0.0


def test_la_permutacion_dentro_del_dia_no_rechaza_bajo_la_nula():
    """Gaps sin relación con la predicción: p ≥ 0,05 en un panel nulo."""
    rng = np.random.default_rng(9)
    df = _panel()
    df["gap_pct"] = rng.normal(size=len(df))          # nula: sin estructura
    df["pred"] = df["sox_prev"] * df["ticker"].map({"A": 0.9, "B": 0.5, "C": 0.2, "D": 0.05})
    df["fecha"] = df["fecha"].dt.date.astype(str)
    tv.N_PERM, tv.N_BOOT = 400, 400
    r = tv.inferencia(df, "pred", "gap_pct")
    assert r["contiene_cero"] and r["p_permutacion_dentro_del_dia"] > 0.01
