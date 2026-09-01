# ============================================================
# tests/test_condicional.py — las guardas del Frente D.
#
# Tres cosas se prueban aquí, y cada una existe por una regla que ya se
# violó una vez en este proyecto:
#
#  1. EL SPLITTER NO ES NUEVO. `dividir_walkforward` tiene que producir el
#     MISMO conjunto de entrenamiento, fecha por fecha, que el walk-forward
#     expansivo con embargo ya publicado de `GEMELO/control_lineal.py`. El
#     pre-registro prohíbe reimplementar purge y embargo a mano; esto lo
#     comprueba en vez de prometerlo.
#
#  2. LA INFERENCIA RESPETA EL CLÚSTER DE DÍA. Un intervalo calculado fila
#     por fila sobre datos agrupados es el error que ya invalidó la primera
#     versión de `dos_ventanas.md`. Se prueba que el bootstrap de este
#     módulo produce intervalos MÁS ANCHOS que uno que ignora el clúster,
#     sobre datos con clúster inyectado a propósito.
#
#  3. EL TEST DE CAUSALIDAD DISCRIMINA. Un test que nunca falla no prueba
#     nada: se comprueba que una condición envenenada con `shift(-1)` lo
#     hace fallar.
# ============================================================

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GEMELO import control_lineal as cl
from GEMELO.CONDICIONAL import condicional as cd


# ------------------------------------------------------------
# 1. El splitter es el de la casa, no uno nuevo
# ------------------------------------------------------------
def test_splitter_coincide_con_control_lineal():
    """Mismo conjunto de entrenamiento, fecha por fecha, que el que arma
    `control_lineal.correr_configuracion` en sus líneas 180-181."""
    fechas = pd.bdate_range("2020-01-01", "2023-12-31")
    splits = cd.dividir_walkforward(fechas, embargo_dias=cd.EMBARGO_DIAS,
                                    minimo_train=10)
    assert splits, "el splitter no produjo particiones"
    for train, i in splits:
        d = fechas[i]
        # LA regla de control_lineal, escrita tal cual está allá:
        corte = pd.Timestamp(d) - pd.Timedelta(days=cd.EMBARGO_DIAS)
        esperado = fechas <= corte
        assert np.array_equal(train, esperado)
        # y la consecuencia que importa: nada del train toca el test
        assert fechas[train].max() <= corte < d


def test_splitter_reproduce_el_train_de_correr_configuracion():
    """Verificación por el mecanismo REAL: se corre la función publicada de
    `control_lineal` sobre un panel sintético y se comprueba que las filas
    que usó para entrenar cada fecha son exactamente las que este splitter
    habría seleccionado."""
    fechas = pd.bdate_range("2021-01-01", "2023-06-30")
    rng = np.random.default_rng(7)
    panel = pd.DataFrame({
        "fecha": np.repeat(fechas, 3),
        "ticker": list(["A", "B", "C"]) * len(fechas),
        "sox_t": rng.normal(size=len(fechas) * 3),
        "sox_t1": rng.normal(size=len(fechas) * 3),
        "gap_pct": rng.normal(size=len(fechas) * 3),
    })
    evaluacion = panel[panel["fecha"] >= "2022-06-01"]
    out = cl.correr_configuracion("C1", panel, evaluacion,
                                  embargo_dias=cd.EMBARGO_DIAS)
    assert not out.empty
    for f in out["fecha"].unique()[:20]:
        corte = pd.Timestamp(f) - pd.Timedelta(days=cd.EMBARGO_DIAS)
        n_esperado = int((panel["fecha"] <= corte).sum())
        n_real = int(out[out["fecha"] == f]["n_train"].iloc[0])
        assert n_real == n_esperado, (f, n_real, n_esperado)


def test_embargo_no_se_redeclara():
    """`EMBARGO_DIAS` viene de `backtest.baselines`, no de una constante
    propia. Si alguien la copia, este test lo caza."""
    from backtest.baselines import EMBARGO_DIAS as canonico
    assert cd.EMBARGO_DIAS is canonico or cd.EMBARGO_DIAS == canonico
    fuente = open(cd.__file__, encoding="utf-8").read()
    assert "EMBARGO_DIAS = 5" not in fuente, \
        "el embargo está redeclarado a mano en vez de importado"


# ------------------------------------------------------------
# 2. La inferencia respeta el clúster de día
# ------------------------------------------------------------
def test_bootstrap_por_fecha_es_mas_ancho_que_ignorar_el_cluster():
    """Datos con clúster inyectado: 7 filas por fecha que comparten un
    efecto de día grande. Un IC que trate las filas como independientes
    sale artificialmente angosto; el de este módulo, que remuestrea FECHAS
    enteras en bloques circulares, tiene que salir claramente más ancho."""
    rng = np.random.default_rng(11)
    n_fechas, por_fecha = 300, 7
    efecto_dia = rng.normal(0, 5.0, n_fechas)
    filas = np.repeat(efecto_dia, por_fecha) + rng.normal(0, 0.5,
                                                          n_fechas * por_fecha)
    # (a) el error: IC de la media tratando filas como independientes
    se_filas = filas.std(ddof=1) / np.sqrt(len(filas))
    ancho_ingenuo = 2 * 1.96 * se_filas
    # (b) lo correcto: bootstrap circular de bloques DE FECHAS
    ic = cd.ic_media_por_fecha(efecto_dia)
    ancho_correcto = ic["hi"] - ic["lo"]
    assert ancho_correcto > ancho_ingenuo * 1.5, (ancho_correcto, ancho_ingenuo)


def test_deff_detecta_el_cluster_inyectado():
    """El DEFF medido tiene que ser claramente > 1 cuando hay clúster, y
    ~1 cuando no lo hay. Si no distingue, no sirve para justificar nada."""
    rng = np.random.default_rng(13)
    n_fechas, k = 250, 7
    fechas = np.repeat(pd.bdate_range("2022-01-03", periods=n_fechas), k)

    p_dia = rng.uniform(0.05, 0.95, n_fechas)          # fuerte efecto de día
    con = pd.DataFrame({"fecha": fechas,
                        "acierto": rng.binomial(1, np.repeat(p_dia, k))})
    sin = pd.DataFrame({"fecha": fechas,
                        "acierto": rng.binomial(1, 0.5, n_fechas * k)})
    assert cd.deff_por_fecha(con)["deff"] > 2.0
    assert cd.deff_por_fecha(sin)["deff"] < 1.5


def test_permutacion_de_signo_es_por_dia_no_por_fila():
    """La permutación de signo del módulo opera sobre un vector de FECHAS.
    Se comprueba que, con una señal por día débil pero filas muchas, el p
    por fecha NO es el p que daría permutar filas — el segundo es
    anticonservador y es justamente el que el frente prohíbe."""
    rng = np.random.default_rng(17)
    n_fechas, k = 120, 8
    por_fecha = rng.normal(0.4, 3.0, n_fechas)         # señal débil por día
    filas = np.repeat(por_fecha, k)                    # sin ruido: clúster puro
    p_fecha = cd.permutacion_signo_por_fecha(por_fecha)["p_dos_colas"]
    p_fila = cd.permutacion_signo_por_fecha(filas)["p_dos_colas"]
    assert p_fecha >= p_fila, (p_fecha, p_fila)


def test_bootstrap_auc_remuestrea_fechas_completas():
    """Cada réplica del IC del AUC tiene que mover score y etiqueta juntos:
    si se remuestrearan por separado, el AUC de la réplica sería 0.5 en
    promedio y el IC contendría 0.5 siempre. Con una señal perfecta, el IC
    tiene que quedar íntegramente por encima de 0.5."""
    rng = np.random.default_rng(19)
    s = rng.normal(size=400)
    y = (s > 0).astype(int)          # separación perfecta
    ic = cd.ic_auc_por_fecha(s, y)
    assert ic["auc"] > 0.99
    assert ic["lo"] > 0.9 and ic["excluye_0.5"]


def test_auc_coincide_con_la_definicion_de_mann_whitney():
    rng = np.random.default_rng(23)
    s = rng.normal(size=200)
    y = rng.binomial(1, 0.4, 200)
    pos, neg = s[y == 1], s[y == 0]
    fuerza_bruta = np.mean([(1.0 if a > b else 0.5 if a == b else 0.0)
                            for a in pos for b in neg])
    assert abs(cd.auc(s, y) - fuerza_bruta) < 1e-9


# ------------------------------------------------------------
# 3. El test de causalidad discrimina
# ------------------------------------------------------------
def _feats_sinteticas(n: int = 900) -> pd.DataFrame:
    rng = np.random.default_rng(29)
    idx = pd.bdate_range("2019-01-02", periods=n)
    return pd.DataFrame({
        "sox_t": rng.normal(0, 0.012, n),
        "ks11_ret": rng.normal(0, 0.010, n),
        "twii_ret": rng.normal(0, 0.011, n),
        "n225_ret": rng.normal(0, 0.009, n),
        "krw_ret": rng.normal(0, 0.004, n),
        "twd_ret": rng.normal(0, 0.003, n),
        "jpy_ret": rng.normal(0, 0.004, n),
    }, index=idx)


def test_condiciones_son_invariantes_a_truncar_en_t():
    assert cd.test_causalidad(_feats_sinteticas())["celdas_con_fuga"] == 0


def test_la_contraprueba_del_test_de_causalidad_falla_de_verdad():
    """El corazón de la regla de la casa #1: un test que no puede fallar no
    es un test. Se le da al módulo una `construir_condiciones` que mira el
    futuro y tiene que reventar."""
    feats = _feats_sinteticas()
    original = cd.construir_condiciones
    try:
        def con_fuga(f, camp=None):
            g = f.copy()
            g["sox_t"] = g["sox_t"].shift(-1)      # el futuro
            return original(g, camp)
        cd.construir_condiciones = con_fuga
        with pytest.raises(cd.ErrorFuga) as exc:
            cd.test_causalidad(feats)
        # y falla POR LA RAZÓN CORRECTA: fuga detectada, no contraprueba rota
        assert "fuga detectada" in str(exc.value), str(exc.value)
    finally:
        cd.construir_condiciones = original


def test_dias_a_fin_de_trimestre_es_conocible_y_correcto():
    from datetime import date
    assert cd._dias_habiles_a_fin_de_trimestre(date(2026, 3, 31)) == 1
    assert cd._dias_habiles_a_fin_de_trimestre(date(2026, 3, 30)) == 2
    assert cd._dias_habiles_a_fin_de_trimestre(date(2026, 12, 31)) == 1
    # 1-ene-2027 mira al 31-mar-2027, no hacia atrás
    assert cd._dias_habiles_a_fin_de_trimestre(date(2027, 1, 1)) > 50


# ------------------------------------------------------------
# 4. Aislamiento: nada del camino de sellado importa este frente
# ------------------------------------------------------------
def test_el_camino_de_sellado_no_importa_condicional():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for archivo in ("motor.py", "senales.py", "snapshot.py", "alertas.py",
                    "universo.py", "noticias.py"):
        texto = open(os.path.join(raiz, archivo), encoding="utf-8").read()
        assert "CONDICIONAL" not in texto, f"{archivo} importa el frente D"


def test_bases_solo_en_modo_lectura():
    fuente = open(cd.__file__, encoding="utf-8").read()
    assert fuente.count("mode=ro") >= 2
    for prohibido in ("INSERT ", "UPDATE ", "DELETE ", "DROP ", "CREATE TABLE"):
        assert prohibido not in fuente, f"escritura en base: {prohibido}"


def test_ningun_estimador_puntual_sin_intervalo():
    """Regla de la casa #3. Las tres funciones que producen un estimador
    puntual reportable devuelven su intervalo en el mismo diccionario."""
    rng = np.random.default_rng(31)
    x = rng.normal(0.3, 1.0, 300)
    assert {"media", "lo", "hi"} <= set(cd.ic_media_por_fecha(x))
    y = (x + rng.normal(0, 1, 300) > 0).astype(int)
    assert {"auc", "lo", "hi"} <= set(cd.ic_auc_por_fecha(x, y))
    assert {"observado", "p_dos_colas"} <= set(cd.permutacion_signo_por_fecha(x))
