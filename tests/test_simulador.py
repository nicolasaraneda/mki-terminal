"""Contrapruebas del simulador con verdad conocida (`GEMELO/simulador/`).
Sin red; la única lectura del sello es `calibrar_desde_sellado` en mode=ro,
que se evita acá con parámetros sintéticos."""
import ast
import os

import numpy as np
import pytest

from GEMELO.simulador import proceso as pr

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _p(b=1.0, c=0.0):
    t = ["A", "B", "C", "D", "E", "F", "G", "H"]
    return pr.Parametros(tickers=t, beta={k: v for k, v in zip(t, [0.9, 0.7, 0.36, 0.75, 0.34, 0.63, 0.62, 0.09])},
                         mu={k: 0.5 for k in t}, sigma={k: 4.0 for k in t}, escala_sox=3.3,
                         tamanos=[8, 8, 7, 4, 8, 8, 6, 8], b=b, c=c)


def test_el_esquema_es_el_de_las_filas_selladas():
    df = pr.simular(_p(), 50, np.random.default_rng(0))
    for col in ("dia", "ticker", "apertura_estimada_pct", "gap_pct", "acierto_gap", "error_gap_pp",
                "retorno_real_pct", "acierto_direccion", "error_pp"):
        assert col in df.columns
    assert df.groupby("dia").size().tolist()[:8] == [8, 8, 7, 4, 8, 8, 6, 8]


def test_la_ventaja_es_monotona_en_b_y_negativa_en_b_cero():
    vs = [pr.ventaja_esperada(_p(b=b), n_dias=20000) for b in (0.0, 0.5, 1.0, 2.0)]
    assert vs[0] < 0                      # con deriva positiva, sin información se pierde
    assert all(x < y for x, y in zip(vs, vs[1:]))


def test_calibrar_b_encuentra_delta_cero_y_nueve():
    for objetivo in (0.0, 0.09):
        p = _p()
        p.b = pr.calibrar_b(p, objetivo, n_dias=20000, tol=0.003)
        assert pr.ventaja_esperada(p, n_dias=60000, semilla=5) == pytest.approx(objetivo, abs=0.01)


def test_el_shock_de_dia_sube_el_icc():
    icc0 = pr.icc_de_aciertos(pr.simular(_p(c=0.0), 3000, np.random.default_rng(1)))["icc"]
    icc1 = pr.icc_de_aciertos(pr.simular(_p(c=6.0), 3000, np.random.default_rng(1)))["icc"]
    assert icc1 > icc0 + 0.1


def test_la_varianza_marginal_del_gap_se_conserva():
    """σ_total de cada ticker es un dato del sello: el simulador la reproduce
    descontando la parte común (salvo el piso)."""
    p = _p(b=1.0, c=3.0)
    df = pr.simular(p, 40000, np.random.default_rng(2))
    for t in p.tickers:
        assert df[df.ticker == t]["gap_pct"].std() == pytest.approx(4.0, rel=0.1)
    assert all(v <= 4.0 for v in pr.sigma_idiosincratica(p).values())


def test_reproducible_con_semilla():
    a = pr.simular(_p(), 30, np.random.default_rng(7))
    b = pr.simular(_p(), 30, np.random.default_rng(7))
    assert a.equals(b)


def test_el_simulador_no_importa_la_ruta_de_sellado():
    for nombre in ("proceso.py", "calibracion.py"):
        ruta = os.path.join(RAIZ, "GEMELO", "simulador", nombre)
        arbol = ast.parse(open(ruta, encoding="utf-8").read())
        mods = []
        for n in ast.walk(arbol):
            if isinstance(n, ast.Import):
                mods += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                mods.append(n.module or "")
        for prohibido in ("motor", "snapshot", "senales", "alertas", "sqlite3", "yfinance"):
            assert not any(m == prohibido or m.startswith(prohibido + ".") for m in mods), (nombre, mods)


# ------------------------------------------------------------
# Agregados el 2-sep-2026 tras el dictamen del adversario (Frente A)
# ------------------------------------------------------------
def test_el_piso_idiosincratico_se_declara_cuando_ata():
    """El test de varianza marginal usaba σ = 4 uniforme, donde el piso del
    30% nunca ata; en lo real ata en 2 de 8 tickers (2330.TW, 4063.T) y la
    sd simulada del gap queda por ENCIMA de la sellada. Acá se fija que
    (a) con σ chica el piso ata y `calibracion.piso_idiosincratico` lo
    marca, y (b) el exceso de sd es positivo y se reporta."""
    from GEMELO.simulador import calibracion as cal
    from GEMELO.simulador import proceso as pr
    q = pr.Parametros(tickers=("A", "B"), beta={"A": 1.0, "B": 1.0}, mu={"A": 0.0, "B": 0.0},
                      sigma={"A": 1.0, "B": 8.0}, escala_sox=1.0, tamanos=[2], b=1.0, c=3.0)
    filas = {f["ticker"]: f for f in cal.piso_idiosincratico(q)}
    assert filas["A"]["piso_ata"] and filas["A"]["exceso_pct"] > 0
    assert not filas["B"]["piso_ata"] and filas["B"]["exceso_pct"] == 0.0


def test_rho_cero_reproduce_el_generador_publicado_y_rho_positivo_correlaciona_dias():
    from GEMELO.simulador import proceso as pr
    base = pr.Parametros(tickers=("A",), beta={"A": 1.0}, mu={"A": 0.0}, sigma={"A": 4.0},
                         escala_sox=1.0, tamanos=[1], b=1.0, c=1.0)
    a = pr.simular(base, 500, np.random.default_rng(3))
    b = pr.simular(pr.Parametros(**{**base.__dict__, "rho": 0.0}), 500, np.random.default_rng(3))
    assert np.allclose(a["gap_pct"], b["gap_pct"])
    c = pr.simular(pr.Parametros(**{**base.__dict__, "rho": 0.6}), 20000, np.random.default_rng(3))
    s = c["sox"].to_numpy()
    ac1 = np.corrcoef(s[:-1], s[1:])[0, 1]
    assert 0.5 < ac1 < 0.7


def test_t_de_cluster_y_cuantil_t_sin_scipy():
    from GEMELO import bifurcaciones as bf
    assert abs(bf._t_ppf(0.975, 34) - 2.0322) < 1e-3
    assert abs(bf._t_ppf(0.975, 2) - 4.3027) < 1e-3
    rng = np.random.default_rng(1)
    g = [rng.normal(0.1, 1.0, size=k) for k in rng.integers(4, 9, size=35)]
    punto, lo, hi = bf._ic_t_cluster(g)
    p2, lo2, hi2 = bf._bootstrap_dia(g, 400, semilla=7)
    assert punto == p2 and lo < punto < hi
    assert (hi - lo) > (hi2 - lo2) * 0.9          # la t con gl = k−1 no es más angosta que el percentil


def test_bootstrap_dia_con_semilla_distinta_da_intervalo_distinto():
    from GEMELO import bifurcaciones as bf
    rng = np.random.default_rng(2)
    g = [rng.normal(0.0, 1.0, size=6) for _ in range(35)]
    a = bf._bootstrap_dia(g, 200)
    b = bf._bootstrap_dia(g, 200, semilla=99)
    assert a[0] == b[0] and (a[1], a[2]) != (b[1], b[2])
