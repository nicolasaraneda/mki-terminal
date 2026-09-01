# ============================================================
# Tests del WS5 — la hipótesis del relevo asiático (Etapa 6.0.0).
#
# Lo que protegen, en orden de gravedad:
#
#  1. LA TRAMPA. Para un objetivo asiático su propio índice local es casi
#     circular (Samsung está DENTRO del KOSPI). Si se colara, E2 luciría
#     espectacular en Asia por la razón equivocada y la prueba de simetría
#     concluiría lo contrario de lo que los datos dicen. Va como test, no
#     como comentario — y con CONTRAPRUEBA, para que el test pueda fallar.
#  2. LA CAUSALIDAD DE FRÁNCFORT, demostrada contra los calendarios reales
#     en vez de asumida.
#  3. EL HALLAZGO ESTRUCTURAL: la sesión asiática FRESCA (día D+1) NO es
#     conocible a la emisión. Se fija para que no se pierda en silencio.
#  4. Que la convención `excluir_cero` de la §2.8 SÍ se aplica — la que el
#     WS3 no aplicó.
#  5. Que el N del DSR se CALCULA desde un registro con procedencia,
#     y que ningún sello histórico puede volver a ser el N vigente.
#  6. Que el carácter POST-HOC está declarado y la regla de decisión se
#     aplica mecánicamente, no a ojo.
#
# Nada aquí toca bases, filas selladas ni el camino de sellado.
# ============================================================

import ast
import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import calendarios
from universo import EXCHANGE_POR_TICKER, MERCADOS_POR_ABRIR

from GEMELO import control_lineal as cl
from GEMELO import datos
from GEMELO import relevo_asiatico as ra


# ============================================================
# 1. LA TRAMPA — el índice propio NUNCA alimenta a su propia bolsa
# ============================================================
def test_E2_nunca_incluye_el_indice_de_la_bolsa_del_objetivo():
    """Samsung está dentro del KOSPI y TSMC dentro del TWSE: alimentar
    `ks11_ret` a `005930.KS` no es 'el relevo asiático', es una parte del
    propio retorno del objetivo entrando por la puerta de atrás."""
    for bolsa, propio in ra.INDICE_POR_EXCHANGE.items():
        assert propio not in ra.features_e2(bolsa), \
            f"{propio} se coló en E2 de {bolsa}: E2 sería circular"


def test_la_exclusion_se_aplica_a_TODAS_las_bolsas_del_universo():
    """Si mañana entra un ticker de una bolsa nueva, este test obliga a
    declarar su índice antes de que E2 pueda ser circular ahí."""
    bolsas = {EXCHANGE_POR_TICKER[t] for t in MERCADOS_POR_ABRIR}
    assert bolsas <= set(ra.INDICE_POR_EXCHANGE), \
        f"bolsas sin índice declarado: {bolsas - set(ra.INDICE_POR_EXCHANGE)}"


def test_contraprueba_sin_la_exclusion_el_indice_propio_SI_estaria():
    """Un test anti-trampa que no puede fallar no prueba nada. Se
    reconstruye el conjunto SIN la regla y se verifica que ahí el índice
    propio sí aparece — luego la regla está haciendo trabajo."""
    for bolsa in ("XKRX", "XTAI", "XTKS"):
        propio = ra.INDICE_POR_EXCHANGE[bolsa]
        assert propio in ra.FEATURES_ASIA          # sin la regla, entraría
        assert propio not in ra.features_e2(bolsa)  # con la regla, no


def test_XETR_conserva_los_tres_indices_asiaticos():
    """Fráncfort es el caso de la hipótesis: ninguno de los tres índices
    asiáticos es su índice local, así que E2 los lleva los tres."""
    assert ra.features_e2("XETR") == ra.FEATURES_ASIA


def test_E1_es_exactamente_el_control_de_informacion_del_WS2b():
    """E1 tiene que ser el MISMO insumo que el campeón. Si alguien lo
    redefine, la comparación E2 vs E1 deja de significar lo que dice."""
    for bolsa in ra.INDICE_POR_EXCHANGE:
        assert ra.configuraciones(bolsa)["E1"]["features"] == \
            cl.FEATURES_SOLO_SOX == ("sox_t", "sox_t1")


def test_E3_es_exactamente_la_union_de_E1_y_E2():
    for bolsa in ra.INDICE_POR_EXCHANGE:
        c = ra.configuraciones(bolsa)
        assert set(c["E3"]["features"]) == \
            set(c["E1"]["features"]) | set(c["E2"]["features"])


def test_son_exactamente_TRES_configuraciones():
    """No se añade una cuarta: subiría N y esa tentación es literalmente el
    sesgo que el DSR mide."""
    for bolsa in ra.INDICE_POR_EXCHANGE:
        assert set(ra.configuraciones(bolsa)) == {"E1", "E2", "E3"}


# ============================================================
# 2. CAUSALIDAD DE FRÁNCFORT — demostrada, no asumida
# ============================================================
def test_la_apertura_de_XETR_ocurre_despues_del_cierre_asiatico_del_dia_D():
    """La condición dura de la hipótesis, contra los calendarios históricos
    reales de `calendarios.apertura_utc` y los cierres sellados en
    `datos.CATALOGO` — no contra una tabla escrita a mano."""
    sesiones = [s.strftime("%Y-%m-%d")
                for s in pd.bdate_range("2019-01-07", "2026-08-21", freq="W-WED")]
    probadas = 0
    for s in sesiones:
        if not calendarios.es_sesion("XETR", s):
            continue
        d = ra.disponibilidad_relevo(s)
        asiaticas = [f for f in d["series"]
                     if f["barra"] == "D" and f["serie"] in ra.FEATURES_ASIA_TICKERS]
        assert len(asiaticas) == 3
        for f in asiaticas:
            assert f["conocible_a_la_emision"], (s, f)
            assert f["h_antes_de_apertura_XETR"] > 0, (s, f)
        probadas += 1
    assert probadas > 300, f"solo {probadas} sesiones probadas"


def test_el_helper_de_causalidad_responde_sobre_sesiones_reales():
    for s in ("2026-08-26", "2023-03-15", "2019-11-06"):
        if calendarios.es_sesion("XETR", s):
            assert ra.causalidad_xetr_ok(s)


# ============================================================
# 3. EL HALLAZGO ESTRUCTURAL — la sesión FRESCA no es conocible
# ============================================================
def test_la_sesion_asiatica_fresca_del_dia_D1_NO_es_conocible_a_la_emision():
    """El relato del relevo describe la sesión asiática que ocurre ENTRE el
    cierre del SOX y la apertura de Fráncfort — la del día D+1, que cierra
    ~30 min antes de que XETR abra. Esa sesión NO existe a las 22:15 UTC
    del día D. Este test fija el hallazgo: la versión fuerte de la
    hipótesis NO es testeable bajo la restricción de emisión del sistema.
    """
    d = ra.disponibilidad_relevo("2026-08-26")
    frescas = [f for f in d["series"]
               if f["barra"] == "D+1" and f["serie"] in ra.FEATURES_ASIA_TICKERS]
    assert len(frescas) == 3
    for f in frescas:
        assert not f["conocible_a_la_emision"], f
        assert f["h_antes_de_la_emision"] < 0, f      # aún no existía
        assert f["h_antes_de_apertura_XETR"] > 0, f   # pero cierra antes


def test_el_insumo_asiatico_conocible_es_MAS_VIEJO_que_el_SOX():
    """La otra mitad que la hipótesis no menciona: a la emisión, el ^SOX
    del día D tiene ~1.25 h y el ^KS11 del día D ~15.75 h. El insumo
    asiático disponible es el MÁS VIEJO, no el más fresco."""
    d = ra.disponibilidad_relevo("2026-08-26")
    por = {(f["serie"], f["barra"]): f for f in d["series"]}
    sox = por[("^SOX", "D")]["h_antes_de_la_emision"]
    for tk in ra.FEATURES_ASIA_TICKERS:
        assert por[(tk, "D")]["h_antes_de_la_emision"] > sox, tk
    assert sox == pytest.approx(1.25)


# ============================================================
# 4. LA CONVENCIÓN DEL EMPATE — aplicada, a diferencia del WS3
# ============================================================
def _frame(gaps, preds):
    return pd.DataFrame({"fecha": pd.to_datetime(["2026-01-05"] * len(gaps)),
                         "ticker": [f"T{i}" for i in range(len(gaps))],
                         "pred": preds, "gap_pct": gaps,
                         "sigma": [1.0] * len(gaps),
                         "alpha": [1.0] * len(gaps),
                         "n_train": [500] * len(gaps)})


def test_excluir_cero_descarta_las_filas_de_gap_exacto_cero():
    d = _frame([0.0, 2.0, -2.0, 0.0], [1.0, 1.0, -1.0, -1.0])
    assert len(ra.excluir_cero(d)) == 2
    assert (ra.excluir_cero(d)["gap_pct"] != 0).all()


def test_el_WS5_corrige_el_sesgo_que_el_WS3_dejo_pasar():
    """Con una fila de gap == 0.00, `cl.evaluar` se la regala al modelo
    (`pred>=0`) y se la niega a la baseline (`gap>0`). El WS5 la excluye de
    AMBOS lados y la asimetría desaparece."""
    d = _frame([0.0, 2.0, -2.0, -1.0], [1.0, 1.0, -1.0, 1.0])
    ws3 = cl.evaluar(d, "X")
    ws5 = ra.evaluar(d, "X")
    assert ws3["n"] == 4 and ws5["n"] == 3
    assert ws3["ventaja_pp"] > ws5["ventaja_pp"], \
        "la convención del WS3 debe inflar la ventaja; si no, el test miente"


def test_sin_filas_de_gap_cero_ambas_convenciones_coinciden():
    """El filtro no puede cambiar nada donde no hay empates: si lo hiciera,
    estaría tocando filas legítimas."""
    d = _frame([1.0, 2.0, -2.0, -1.0], [1.0, 1.0, -1.0, 1.0])
    assert ra.evaluar(d, "X") == cl.evaluar(d, "X")


def test_comparar_tambien_aplica_la_convencion():
    a = _frame([0.0, 2.0, -2.0], [1.0, 1.0, -1.0])
    b = _frame([0.0, 2.0, -2.0], [-1.0, 1.0, -1.0])
    assert ra.comparar(a, b, "A", "B")["n"] == 2
    assert cl.comparar(a, b, "A", "B")["n"] == 3


# ============================================================
# 5. EL N DECLARADO
# ============================================================
def test_el_N_acumulado_SE_CALCULA_y_no_se_escribe():
    """La versión anterior de este test decía `assert N_INTENTOS_WS5 == 25`.

    Eso no protegía el número: lo hacía **inmune a la corrección**
    mientras cuatro documentos del repo declaraban 25 / 26 / 32 / 43 / 82.
    Es la cuarta regla de la casa —un número retirado que sigue ofrecido
    en el código vuelve a circular— y el test era el mecanismo que lo
    ofrecía.

    Lo que se fija ahora es la PROPIEDAD, no el valor: el N vigente es la
    suma del registro y de ninguna otra parte. Agregar un intento es
    agregar una fila; el número se recalcula solo y este test sigue
    verde sin tocarlo, que es exactamente lo que antes no pasaba.
    """
    assert ra.N_INTENTOS_ACUMULADO == sum(f[0] for f in ra.REGISTRO_INTENTOS)
    # y no hay ningún literal suelto: el módulo no puede declarar el
    # acumulado por asignación directa de un entero
    import inspect, re
    fuente = inspect.getsource(ra)
    assert not re.search(r"^N_INTENTOS_ACUMULADO\s*=\s*\d", fuente, re.M)


def test_cada_tramo_del_registro_de_intentos_cita_su_evidencia():
    """Un conteo sin procedencia no es auditable: es una cifra de memoria
    con otro traje. Cada fila declara cuántos, qué se evaluó y dónde vive
    el resultado que alguien miró."""
    assert len(ra.REGISTRO_INTENTOS) >= 15
    for n, tramo, que, fuente in ra.REGISTRO_INTENTOS:
        assert isinstance(n, int) and n >= 1, tramo
        assert tramo and que, tramo
        # la fuente apunta a un archivo o a un acta, con localizador
        assert (":" in fuente or "§" in fuente or fuente.endswith(".md")), tramo


def test_el_acumulado_supera_a_los_sellos_historicos_y_endurece_el_DSR():
    """Ser conservador es gratis: un N de más sube SR0 y hace al DSR más
    exigente; un N de menos lo inutiliza. Los sellos históricos (WS3=13,
    WS5=25) se conservan para reproducir sus reportes, pero NINGUNO puede
    volver a ser el N vigente."""
    from GEMELO import ventana_larga as vl
    from backtest import inferencia as inf
    assert ra.N_ACUMULADO_WS3 == 13            # sello histórico, congelado
    assert ra.N_INTENTOS_WS5 == 25             # sello histórico, congelado
    assert ra.N_INTENTOS_WS5 == ra.N_ACUMULADO_WS3 + 3 * 2 * 2
    assert ra.N_INTENTOS_ACUMULADO > ra.N_INTENTOS_WS5 > vl.N_INTENTOS_WS3
    for previo in (vl.N_INTENTOS_WS3, ra.N_INTENTOS_WS5):
        assert (inf.sr0_deflacionado(ra.N_INTENTOS_ACUMULADO, 0.25)
                > inf.sr0_deflacionado(previo, 0.25))


def test_el_reporte_emite_el_N_vigente_y_no_el_sello_retirado():
    """Cuarta regla de la casa aplicada al reporte: el 25 puede quedar
    como sello histórico, pero no puede ser lo que el reporte publica."""
    import inspect
    fuente = inspect.getsource(ra)
    # el sello nunca alimenta el parámetro que el reporte imprime
    assert '"N_intentos_declarado": N_INTENTOS_ACUMULADO' in fuente
    assert '"N_intentos_declarado": N_INTENTOS_WS5' not in fuente


def test_el_prerregistro_declara_el_N_y_la_regla_antes_del_reporte():
    ruta = os.path.join(RAIZ, "GEMELO", "resultados", "preregistro_ws5.md")
    texto = open(ruta, encoding="utf-8").read()
    plano = " ".join(texto.split())        # el markdown envuelve líneas
    assert "DECLARADO ANTES DE CORRER NADA" in texto
    assert "**25**" in texto
    assert "POST-HOC" in texto
    assert "configuración × ventana de evaluación" in plano
    # la trampa, nombrada en el pre-registro y no solo en el código
    assert "Samsung está dentro del KOSPI" in texto
    # la contaminación del holdout, declarada
    assert "cuarentena **parcial**" in texto or "cuarentena PARCIAL" in texto


# ============================================================
# 6. POST-HOC y la regla de decisión, aplicada mecánicamente
# ============================================================
def _par(estrato, ventaja, p):
    return {"par": "E2 vs E1", "estrato": estrato, "porcion": "holdout",
            "ventaja_pp": ventaja, "mcnemar_p": p, "n": 500}


def test_la_regla_de_decision_cubre_las_cuatro_ramas_declaradas():
    """La regla del §6 del pre-registro se aplica desde el dato, no a ojo."""
    mejora, no = (2.0, 0.001), (0.1, 0.90)
    casos = {
        ("XETR_si", "ASIA_no"): (mejora, no, "NO REFUTADA"),
        ("XETR_si", "ASIA_si"): (mejora, mejora, "REFUTADA (capacidad)"),
        ("XETR_no", "ASIA_si"): (no, mejora, "REFUTADA (al revés de lo predicho)"),
        ("XETR_no", "ASIA_no"): (no, no, "REFUTADA (ausencia)"),
    }
    for _, (x, a, esperado) in casos.items():
        v = ra.veredicto([_par("XETR", *x), _par("ASIA", *a)])
        assert v["veredicto"] == esperado, (x, a, v)


def test_una_ventaja_positiva_pero_no_significativa_NO_es_mejora():
    """«E2 mejora a E1» exige ventaja > 0 Y p < 0.05. Sin el segundo
    requisito, cualquier ruido positivo pasaría por hallazgo."""
    v = ra.veredicto([_par("XETR", 3.0, 0.20), _par("ASIA", 0.1, 0.9)])
    assert v["veredicto"] == "REFUTADA (ausencia)"
    assert v["E2_mejora_E1_en_XETR"] is False


def test_sin_el_par_del_holdout_el_veredicto_es_NO_COMPUTABLE():
    """Nunca se inventa un veredicto con datos que faltan."""
    assert ra.veredicto([_par("XETR", 2.0, 0.01)])["veredicto"] == "NO COMPUTABLE"
    assert ra.veredicto([])["veredicto"] == "NO COMPUTABLE"


def test_el_modulo_declara_POST_HOC_en_su_cabecera():
    fuente = open(os.path.join(RAIZ, "GEMELO", "relevo_asiatico.py"),
                  encoding="utf-8").read()
    assert "POST-HOC" in fuente[:2500]
    assert "NO ES CONFIRMATORIO" in fuente[:2500]


# ============================================================
# 7. La línea con la 5.1, y el aislamiento — defendidos por código
# ============================================================
def _importados(ruta):
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    mods = set()
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            mods |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module)
    return mods


def test_el_modulo_no_importa_el_motor_del_backtest_ni_la_cartera():
    mods = _importados(os.path.join(RAIZ, "GEMELO", "relevo_asiatico.py"))
    assert "backtest.motorbt" not in mods
    assert "backtest.cartera" not in mods


def test_no_se_invoca_el_veredicto_escalonado():
    fuente = open(os.path.join(RAIZ, "GEMELO", "relevo_asiatico.py"),
                  encoding="utf-8").read()
    assert "veredicto_escalonado" not in fuente.replace(
        "calcula_veredicto_escalonado", "").replace(
        "veredicto escalonado", "")
    assert "motorbt" not in fuente


def test_el_camino_de_sellado_no_importa_el_WS5():
    """La dirección que protege el sello: un fallo aquí no puede tocar
    snapshot.py."""
    for archivo in ("motor.py", "senales.py", "snapshot.py", "alertas.py",
                    "app.py"):
        fuente = open(os.path.join(RAIZ, archivo), encoding="utf-8").read()
        assert "relevo_asiatico" not in fuente, archivo


def test_no_se_toca_universo_py():
    """Sacar IFX.DE porque aporta poco sería quitar el dato incómodo, y
    además es cambio de universo → UNIVERSO_VERSION → modelo congelado."""
    assert len(MERCADOS_POR_ABRIR) == 8
    assert "IFX.DE" in MERCADOS_POR_ABRIR


# ============================================================
# 8. El parámetro `cfg` añadido a control_lineal es RETROCOMPATIBLE
# ============================================================
def _panel(n_dias=600, tickers=("A", "B"), semilla=7):
    rng = np.random.default_rng(semilla)
    fechas = pd.bdate_range(end="2026-08-21", periods=n_dias)
    filas = []
    for f in fechas:
        sox = rng.normal(0, 1.2)
        for t in tickers:
            filas.append({"fecha": f, "ticker": t, "sox_t": sox,
                          "sox_t1": rng.normal(0, 1.2),
                          "ks11_ret": rng.normal(0, 1.0),
                          "gap_pct": 0.5 * sox + rng.normal(0, 1.0)})
    return pd.DataFrame(filas)


def test_cfg_None_reproduce_exactamente_el_comportamiento_anterior():
    """El parámetro es aditivo: con `cfg=None` la configuración sale de
    CONFIGURACIONES, igual que antes del WS5."""
    panel = _panel()
    ev = panel[panel["fecha"] >= "2026-05-01"]
    por_nombre = cl.correr_configuracion("C1", panel, ev)
    explicita = cl.correr_configuracion("C1", panel, ev,
                                        cfg=cl.CONFIGURACIONES["C1"])
    assert not por_nombre.empty
    pd.testing.assert_frame_equal(por_nombre.reset_index(drop=True),
                                  explicita.reset_index(drop=True))


def test_cfg_explicita_cambia_las_features_efectivamente_usadas():
    """Y cuando se pasa una cfg distinta, se usa: si no, todo el WS5
    estaría corriendo E1 tres veces sin que nadie lo notara."""
    panel = _panel()
    ev = panel[panel["fecha"] >= "2026-05-01"]
    e1 = cl.correr_configuracion("E1", panel, ev,
                                 cfg={"features": ("sox_t", "sox_t1"),
                                      "agrupado": True})
    e2 = cl.correr_configuracion("E2", panel, ev,
                                 cfg={"features": ("ks11_ret",),
                                      "agrupado": True})
    m = e1.merge(e2, on=["fecha", "ticker"], suffixes=("_1", "_2"))
    assert len(m) > 0
    assert not np.allclose(m["pred_1"], m["pred_2"])


# ============================================================
# 9. EL IC DEL ΔMAE — hallazgo colateral del WS5
# ============================================================
def _par_sintetico(semilla=3, n=400):
    rng = np.random.default_rng(semilla)
    base = pd.DataFrame({"fecha": pd.bdate_range("2024-01-01", periods=n),
                         "ticker": ["A"] * n,
                         "gap_pct": rng.normal(0, 1, n),
                         "sigma": [1.0] * n, "alpha": [1.0] * n,
                         "n_train": [500] * n})
    a = base.copy(); a["pred"] = a["gap_pct"] * 0.5 + rng.normal(0, .3, n)
    b = base.copy(); b["pred"] = b["gap_pct"] * 0.2 + rng.normal(0, .8, n)
    return a, b


def test_el_IC_del_WS2b_esta_en_OTRA_escala_que_el_punto_estimado():
    """HALLAZGO: `cl.comparar` imprime un `delta_mae` en pp junto a un
    intervalo que sale del bootstrap del SHARPE. Este test FIJA el
    hallazgo: si alguien lo arregla en `cl` sin documentarlo, falla."""
    a, b = _par_sintetico()
    viejo = cl.comparar(a, b, "A", "B")
    lo, hi = viejo["delta_mae_ic"]
    assert not (lo <= viejo["delta_mae"] <= hi), \
        "si el punto ya cae dentro, el hallazgo del WS5 dejó de ser cierto"


def test_el_WS5_publica_el_IC_en_la_escala_del_punto_estimado():
    a, b = _par_sintetico()
    r = ra.comparar(a, b, "A", "B")
    lo, hi = r["ic_delta_mae_pp"]
    assert lo <= r["delta_mae"] <= hi
    assert "delta_mae_ic" not in r          # renombrado, para que no confunda
    assert "ic_sharpe_dmae" in r            # pero conservado, por continuidad


def test_las_dos_escalas_deciden_SIEMPRE_lo_mismo():
    """La equivalencia que salva las conclusiones previas: `sd > 0`
    conserva el signo réplica a réplica, así que «el IC excluye el cero»
    es el mismo evento en las dos escalas. Se comprueba sobre varias
    semillas, no sobre una."""
    for semilla in range(12):
        a, b = _par_sintetico(semilla=semilla, n=300)
        r = ra.comparar(a, b, "A", "B")
        assert r["ic_excluye_cero"] == r["ic_pp_excluye_cero"], semilla


def test_bootstrap_media_y_bootstrap_bloques_comparten_el_sorteo():
    """Si divergieran, dos intervalos del mismo dato dejarían de ser
    comparables sin que nadie lo notara."""
    from backtest import inferencia as inf
    rng = np.random.default_rng(11)
    x = rng.normal(0.3, 1.0, 500)
    m = inf.bootstrap_media(x, semilla=7, bloque=20, alpha=0.05)
    s = inf.bootstrap_bloques(x, semilla=7, bloque=20, alpha=0.05, anualizar=1)
    assert m["media"] == pytest.approx(float(x.mean()))
    assert m["lo"] < m["media"] < m["hi"]
    # misma decisión, distinta escala
    assert (m["lo"] > 0) == (s["lo"] > 0)


def test_bootstrap_media_es_reproducible_y_exige_semilla():
    from backtest import inferencia as inf
    x = np.random.default_rng(2).normal(0, 1, 200)
    assert inf.bootstrap_media(x, semilla=5) == inf.bootstrap_media(x, semilla=5)
    with pytest.raises(TypeError):
        inf.bootstrap_media(x)
