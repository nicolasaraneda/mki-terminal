# ============================================================
# Tests de GEMELO/bifurcaciones.py — la matriz de bifurcaciones.
#
# Tres cosas distintas se prueban aquí:
#  1. Que la MECÁNICA de los ejes sea correcta —deduplicación,
#     convenciones de empate, filtros de fecha, zona muerta, objetivo—
#     con datos sintéticos donde la respuesta se sabe a mano.
#  2. Que el ANCLA siga reproduciendo la ventana sellada del README.
#     Es el guardián del frente entero: si un día deja de reproducir, la
#     matriz queda sin referencia y hay que enterarse por un test, no por
#     un informe que ya se publicó.
#  3. Que el módulo sea de SOLO LECTURA, verificado por AST: si alguien
#     le mete un INSERT o un UPDATE, el test lo caza.
#
# Nada aquí escribe en ninguna base.
# ============================================================

import ast
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GEMELO import bifurcaciones as bf

HAY_BASE = os.path.exists(bf.RUTA_SENALES)
solo_con_base = pytest.mark.skipif(
    not HAY_BASE, reason="senales.db no está (es gitignored)")

RUTA_MODULO = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "GEMELO", "bifurcaciones.py")

CELDA_NEUTRA = {"dedup": "ninguna", "empate": "estricta",
                "ventana_r2": "dentro", "filas_29jul": "dentro",
                "emision_parcial": "dentro", "corte": "publicado",
                "objetivo": "gap", "zona_muerta": 0.00}


def _celda(**cambios):
    return {**CELDA_NEUTRA, **cambios}


def _sintetico() -> pd.DataFrame:
    """Cinco filas donde cada eje tiene un efecto que se puede contar a
    mano. Dos de ellas son un par duplicado con veredicto OPUESTO, que es
    el caso que hace que `dedup` valga un veredicto."""
    filas = [
        # par duplicado sobre la sesión 2026-07-31: gap idéntico, la
        # primera falla y la segunda acierta.
        ("2026-07-29", "AAA", "2026-07-31", 2.0, -1.0, 0, 3.0, 2.0),
        ("2026-07-30", "AAA", "2026-07-31", 2.0, 1.0, 1, 1.0, 2.0),
        # fila con gap exactamente 0 — la que separa las tres convenciones
        ("2026-08-04", "BBB", "2026-08-05", 0.0, 0.5, 1, 0.5, 0.0),
        # fila dentro de la ventana R2
        ("2026-07-20", "CCC", "2026-07-21", -1.0, -0.5, 1, 0.5, -1.0),
        # fila con predicción minúscula — la que quita la zona muerta
        ("2026-08-20", "DDD", "2026-08-21", 1.0, 0.10, 1, 0.9, 1.0),
    ]
    df = pd.DataFrame(filas, columns=[
        "fecha", "ticker", "sesion_objetivo", "gap_pct",
        "apertura_estimada_pct", "acierto_gap", "error_gap_pp",
        "retorno_real_pct"])
    df["acierto_direccion"] = df["acierto_gap"]
    df["error_pp"] = df["error_gap_pp"]
    df["intervalo80_pp"] = 5.0
    return df


# ------------------------------------------------------------
# 1. Mecánica de los ejes
# ------------------------------------------------------------
def test_dedup_elige_la_fila_correcta_del_par():
    """`first` se queda con la que falla, `last` con la que acierta. Es
    literalmente el defecto que tumbó el pre-registro secuencial."""
    df = _sintetico()
    primero = bf.aplicar(df, _celda(dedup="first"))
    ultimo = bf.aplicar(df, _celda(dedup="last"))
    ninguna = bf.aplicar(df, _celda(dedup="ninguna"))

    assert len(ninguna) == 5
    assert len(primero) == len(ultimo) == 4
    par_p = primero[primero["ticker"] == "AAA"]
    par_u = ultimo[ultimo["ticker"] == "AAA"]
    assert par_p["fecha"].item() == "2026-07-29"
    assert par_p["acierto"].item() == 0
    assert par_u["fecha"].item() == "2026-07-30"
    assert par_u["acierto"].item() == 1


def test_las_tres_convenciones_de_empate_difieren_solo_en_la_fila_cero():
    df = _sintetico()
    est = bf.aplicar(df, _celda(empate="estricta"))
    ver = bf.aplicar(df, _celda(empate="verificador"))
    exc = bf.aplicar(df, _celda(empate="excluir_cero"))

    assert len(est) == len(ver) == 5
    assert len(exc) == 4          # la fila de gap == 0 se va de ambos lados
    cero_est = est[est["ticker"] == "BBB"]["base_acierto"].item()
    cero_ver = ver[ver["ticker"] == "BBB"]["base_acierto"].item()
    assert cero_est == 0          # `>`  no le regala el empate
    assert cero_ver == 1          # `>=` sí
    # y fuera de esa fila las dos convenciones coinciden
    otras = est["ticker"] != "BBB"
    assert (est.loc[otras, "base_acierto"].to_numpy()
            == ver.loc[otras, "base_acierto"].to_numpy()).all()


def test_filtros_de_fecha_y_zona_muerta_quitan_exactamente_lo_suyo():
    df = _sintetico()
    assert len(bf.aplicar(df, _celda(ventana_r2="fuera"))) == 4
    assert "2026-07-20" not in set(
        bf.aplicar(df, _celda(ventana_r2="fuera"))["fecha"])

    assert len(bf.aplicar(df, _celda(filas_29jul="fuera"))) == 4
    assert "2026-07-29" not in set(
        bf.aplicar(df, _celda(filas_29jul="fuera"))["fecha"])

    zm = bf.aplicar(df, _celda(zona_muerta=0.25))
    assert len(zm) == 4 and "DDD" not in set(zm["ticker"])


def test_quitar_el_29jul_hace_que_first_y_last_coincidan():
    """El enredo entre ejes es real y el orden declarado lo produce: si el
    29-jul sale, el par se queda con una sola fila."""
    df = _sintetico()
    a = bf.aplicar(df, _celda(filas_29jul="fuera", dedup="first"))
    b = bf.aplicar(df, _celda(filas_29jul="fuera", dedup="last"))
    assert len(a) == len(b) == 4
    assert (a["acierto"].to_numpy() == b["acierto"].to_numpy()).all()


def test_el_objetivo_cambia_las_columnas_puntuadas():
    df = _sintetico().copy()
    df.loc[df["ticker"] == "AAA", "acierto_direccion"] = 0
    df.loc[df["ticker"] == "AAA", "retorno_real_pct"] = -9.0
    gap = bf.aplicar(df, _celda(objetivo="gap"))
    ret = bf.aplicar(df, _celda(objetivo="retorno_sesion"))
    assert (gap["real"].to_numpy() == df["gap_pct"].to_numpy()).all()
    assert (ret["real"].to_numpy() == df["retorno_real_pct"].to_numpy()).all()
    # y con el retorno cambiado, la baseline cambia de veredicto en AAA
    assert ret[ret["ticker"] == "AAA"]["base_acierto"].sum() == 0


# ------------------------------------------------------------
# 2. Métricas — intervalos presentes y coherentes
# ------------------------------------------------------------
def _grande() -> pd.DataFrame:
    """El sintético estirado por encima de `MINIMO_FILAS`, sobre varios
    días, que es lo que la inferencia de clúster necesita para no
    degenerar."""
    base = _sintetico()
    trozos = []
    for i in range(8):
        t = base.copy()
        t["fecha"] = t["fecha"].str[:8] + f"{10 + i:02d}"
        t["sesion_objetivo"] = t["fecha"]
        t["ticker"] = t["ticker"] + str(i)
        trozos.append(t)
    return pd.concat(trozos, ignore_index=True)


def test_ninguna_metrica_puntual_sale_sin_intervalo():
    m = bf.metricas(bf.aplicar(_grande(), CELDA_NEUTRA), n_boot=200)
    assert m["n"] >= bf.MINIMO_FILAS
    for punto, lo, hi in (("modelo_pct", "modelo_lo", "modelo_hi"),
                          ("base_pct", "base_lo", "base_hi"),
                          ("ventaja_pp", "ventaja_lo", "ventaja_hi"),
                          ("mae", "mae_lo", "mae_hi"),
                          ("mae_cero", "mae_cero_lo", "mae_cero_hi"),
                          ("dmae", "dmae_lo", "dmae_hi"),
                          ("dmae", "dmae_bloque_lo", "dmae_bloque_hi"),
                          ("cobertura_pct", "cobertura_lo", "cobertura_hi"),
                          ("cobertura_pct", "cobertura_dia_lo",
                           "cobertura_dia_hi")):
        assert lo in m and hi in m, f"{punto} sin intervalo"
        assert m[lo] <= m[hi], f"{punto}: intervalo invertido"


def test_el_delta_mae_es_pareado_y_no_una_resta_de_dos_medias_sueltas():
    """El defecto que el `estadistico-adversario` cazó: comparar el IC del
    MAE del modelo contra el MAE de cero como punto desnudo es inválido
    dos veces. `dmae` tiene que ser la media de la diferencia fila a fila."""
    d = bf.aplicar(_grande(), CELDA_NEUTRA)
    m = bf.metricas(d, n_boot=200)
    esperado = float((d["error"] - d["real"].abs()).mean())
    assert abs(m["dmae"] - esperado) < 1e-9
    assert abs(m["dmae"] - (m["mae"] - m["mae_cero"])) < 1e-9


def test_la_permutacion_por_dia_reproduce_su_valor_analitico():
    """Con k días de suma idéntica y no nula, el único modo de igualar o
    superar |suma observada| es que TODOS los signos coincidan: dos
    vectores de 2^k. O sea p = 2/2^k, más la corrección +1. Se verifica
    contra la aritmética, no contra otra corrida del mismo código."""
    for k in (6, 8, 10):
        grupos = [np.array([1.0, 1.0]) for _ in range(k)]
        p = bf._p_permutacion_dia(grupos, n_perm=200_000)
        esperado = 2.0 / (2 ** k)
        assert abs(p - esperado) < 4 * esperado, (k, p, esperado)
    # y nunca devuelve 0 exacto: la corrección +1 de Phipson-Smyth
    assert bf._p_permutacion_dia([np.array([1.0])] * 20, n_perm=500) > 0


def test_el_bootstrap_de_dia_estima_la_razon_de_sumas_no_la_media_de_medias():
    """Con clústeres de tamaños distintos, la media global es la razón de
    sumas. Promediar medias por día pesaría igual un día de 1 fila que uno
    de 8, y aquí los días parciales existen."""
    grupos = [np.array([1.0]), np.array([0.0, 0.0, 0.0])]
    punto, lo, hi = bf._bootstrap_dia(grupos, n_boot=500)
    assert abs(punto - 0.25) < 1e-12      # 1/4, no 0.5
    assert lo <= punto <= hi


def test_el_p_de_permutacion_por_dia_esta_en_el_rango_valido():
    d = bf.aplicar(_grande(), CELDA_NEUTRA)
    grupos = bf._por_dia(d, (d["acierto"] - d["base_acierto"]).to_numpy(float))
    p = bf._p_permutacion_dia(grupos)
    assert 0 < p <= 1.0


@solo_con_base
def test_sobre_datos_reales_el_cluster_es_mas_conservador_que_mcnemar():
    """En el ancla —34 días heterogéneos— ignorar el clúster infla la
    significancia. Es el defecto central que este frente reporta: si un
    día dejara de cumplirse, el titular hay que reescribirlo."""
    d = bf.aplicar(bf.cargar_filas(bf.CORTE_PUBLICADO), bf.CELDA_ANCLA)
    m = bf.metricas(d, n_boot=2000)
    assert m["dias"] == 34
    assert m["p_dia"] > m["p_exacto"], (m["p_dia"], m["p_exacto"])
    assert m["p_dia"] > bf.ALFA          # el ancla NO es significativa
    ancho_dia = m["ventaja_hi"] - m["ventaja_lo"]
    assert ancho_dia > 0


def test_las_dos_rutas_de_mcnemar_se_reportan_y_no_son_la_misma():
    """DECISIONES.md §55: 0.1849 por chi2, 0.1847 exacto. Las dos son
    correctas y el informe debe llevar las dos."""
    m = bf.metricas(bf.aplicar(_grande(), CELDA_NEUTRA), n_boot=200)
    assert "p_exacto" in m and "p_chi2" in m and "p_dia" in m
    assert bf.mcnemar_exact(72, 56) != bf.mcnemar_chi2(72, 56)
    assert abs(bf.mcnemar_chi2(72, 56) - 0.1849) < 0.0005
    assert abs(bf.mcnemar_exact(72, 56) - 0.1847) < 0.0005


def test_la_ventaja_es_la_diferencia_pareada_sobre_las_mismas_filas():
    d = bf.aplicar(_grande(), CELDA_NEUTRA)
    m = bf.metricas(d, n_boot=200)
    esperada = 100 * (d["acierto"].mean() - d["base_acierto"].mean())
    assert abs(m["ventaja_pp"] - esperada) < 1e-9
    assert m["n"] == len(d)


# ------------------------------------------------------------
# 3. El ancla — el guardián del frente
# ------------------------------------------------------------
@solo_con_base
def test_el_ancla_reproduce_la_ventana_sellada_del_readme():
    """La celda `ninguna · excluir_cero · dentro · dentro · dentro ·
    publicado · gap · 0.00` ES la cifra publicada. El corte va pinchado en
    `CORTE_PUBLICADO`, así que esto NO depende del reloj: si falla, o
    cambió la base o cambió el código."""
    bases = {"publicado": bf.cargar_filas(bf.CORTE_PUBLICADO)}
    fallos = bf._verificar_ancla(bases)
    assert not fallos, "el ancla dejó de reproducir:\n  " + "\n  ".join(fallos)


@solo_con_base
def test_el_corte_publicado_no_se_mueve_con_el_track_record():
    """Lo que hace confiable al ancla: `publicado` está pinchado y `vivo`
    crece. Si algún día son iguales, el eje `corte` dejó de medir algo."""
    pub = bf.cargar_filas(bf.CORTE_PUBLICADO)
    vivo = bf.cargar_filas(None)
    assert len(pub) == 253, f"la ventana publicada cambió de tamaño: {len(pub)}"
    assert len(vivo) >= len(pub)


@solo_con_base
def test_las_filas_duplicadas_siguen_ahi_y_son_las_documentadas():
    """§A3.1.a: quince pares que apuntan a la misma sesión objetivo. Si
    esto cambia, el eje 1 hay que volver a documentarlo."""
    df = bf.cargar_filas(bf.CORTE_PUBLICADO)
    dup = df[df.duplicated(["ticker", "sesion_objetivo"], keep=False)]
    assert len(dup) == 30
    assert dup.groupby(["ticker", "sesion_objetivo"]).ngroups == 15


# ------------------------------------------------------------
# 4. Solo lectura, verificado por AST
# ------------------------------------------------------------
def test_el_modulo_no_escribe_en_ninguna_base():
    fuente = open(RUTA_MODULO, encoding="utf-8").read()
    arbol = ast.parse(fuente)
    sospechosas = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str):
            s = nodo.value.upper()
            for verbo in ("INSERT ", "UPDATE ", "DELETE ", "DROP ",
                          "CREATE TABLE", "ALTER "):
                if verbo in s:
                    sospechosas.append(verbo.strip())
    assert not sospechosas, f"SQL de escritura en el módulo: {sospechosas}"


def test_el_modulo_solo_entra_a_la_base_por_las_puertas_de_solo_lectura():
    fuente = open(RUTA_MODULO, encoding="utf-8").read()
    assert "_conexion_ro" in fuente
    # Invariante del proyecto: NADA en GEMELO/ abre senales.db por su
    # cuenta. `sqlite3.connect` sin uri queda en modo escritura por
    # omisión sobre la base que sella en producción.
    assert "sqlite3.connect" not in fuente, (
        "conexión directa: las únicas vías son `backtest.datos."
        "_conexion_ro` y `backtest.linea_base.cargar`")


def test_la_semilla_del_bootstrap_es_fija_y_declarada():
    """Un bootstrap sin semilla no reproduce, y §45 dice que un análisis
    que no se reproduce termina retractado."""
    assert isinstance(bf.SEMILLA, int)
    d = bf.aplicar(_grande(), CELDA_NEUTRA)
    a = bf.metricas(d, n_boot=300)
    b = bf.metricas(d, n_boot=300)
    assert a["ventaja_lo"] == b["ventaja_lo"]
    assert a["mae_hi"] == b["mae_hi"]


# ------------------------------------------------------------
# 5. La matriz, entera
# ------------------------------------------------------------
def test_la_matriz_cubre_el_producto_cartesiano_completo():
    esperadas = int(np.prod([len(v) for v in bf.EJES.values()]))
    assert esperadas == 576
    # sin tocar la base: se cuenta el producto, no se computa
    combos = 1
    for niveles in bf.EJES.values():
        assert len(set(niveles)) == len(niveles), "nivel repetido en un eje"
        combos *= len(niveles)
    assert combos == esperadas


@solo_con_base
def test_la_vara_independiente_coincide_con_la_matriz():
    """§52: la verificación tiene que venir de otra familia de método. La
    ruta independiente es SQL crudo + aritmética a mano; si se separa de
    la matriz, una de las dos está mal y hay que enterarse."""
    indep = bf.ancla_por_ruta_independiente()["ancla"]
    for campo in ("n", "b", "c"):
        assert indep[campo] == bf.ANCLA[campo], campo
    for campo in ("modelo_pct", "base_pct", "ventaja_pp"):
        assert abs(indep[campo] - bf.ANCLA[campo]) <= 0.05, campo


@solo_con_base
def test_sin_la_ventana_r2_la_ventaja_se_da_vuelta():
    """El hallazgo central del frente, por la ruta independiente: al
    sacar el bloque 15-23 jul la ventaja deja de ser positiva."""
    fuera = bf.ancla_por_ruta_independiente()["sin_ventana_r2"]
    assert fuera["ventaja_pp"] < 0
    assert fuera["p_exacto"] > 0.5


@solo_con_base
def test_la_matriz_se_construye_y_ninguna_celda_queda_sin_p():
    mat, ctx = bf.construir_matriz(n_boot=200)
    assert len(mat) == 576
    # el contexto del corte `vivo` se sella, porque se mueve con el reloj
    assert ctx["filas_publicado"] == 253
    assert ctx["filas_vivo"] >= ctx["filas_publicado"]
    assert ctx["ultima_fecha_vivo"]
    assert mat["n"].min() >= 2, "hay celdas con n < 2 entrando al conteo"
    assert mat["p_exacto"].notna().all()
    assert mat["p_chi2"].notna().all()
    assert mat["ventaja_lo"].le(mat["ventaja_hi"]).all()


@solo_con_base
def test_el_test_de_permutacion_por_dia_tiene_potencia_declarada():
    """El «0 de 576» sólo significa algo si el test PUEDE rechazar. Se
    mide el efecto mínimo detectable sobre la estructura real de días: si
    fuera infinito, el cociente no diría nada del modelo."""
    d = bf.aplicar(bf.cargar_filas(bf.CORTE_PUBLICADO), bf.CELDA_ANCLA)
    g = bf._por_dia(d, (d["acierto"] - d["base_acierto"]).to_numpy(float))
    mde = bf.mde_permutacion_dia(g, n_perm=2000)
    assert np.isfinite(mde) and 0 < mde < 100
    # y por encima del MDE el test efectivamente rechaza
    todo = np.concatenate(g)
    centrados = [x - todo.mean() + 1.5 * mde / 100 for x in g]
    assert bf._p_permutacion_dia(centrados, n_perm=4000) < bf.ALFA


def test_el_icc_de_anova_reproduce_casos_conocidos():
    """ICC = 0 si los días son intercambiables; ICC alto si cada día es
    constante y los días difieren. Se verifica contra los dos extremos,
    que se conocen sin calcular nada."""
    rng = np.random.default_rng(7)
    sin_estructura = [rng.normal(size=8) for _ in range(30)]
    assert abs(bf.icc_y_deff(sin_estructura)["icc"]) < 0.15

    todo_dentro = [np.full(8, float(j)) for j in range(30)]
    assert bf.icc_y_deff(todo_dentro)["icc"] > 0.95
    assert bf.icc_y_deff(todo_dentro)["deff"] > 6      # tam_medio 8 → ~8
