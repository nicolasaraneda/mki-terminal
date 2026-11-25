# ============================================================
# Tests de la corrida 17 (25-oct-2026) sobre `GEMELO/SECUENCIAL/`.
#
# Cubren las cuatro condiciones del cuarto dictamen al pre-registro
# secuencial, y están escritos como tests de COMPORTAMIENTO: ninguno
# reproduce la fórmula que prueba (eso fue el defecto N8 del tercer
# dictamen). En particular:
#
#   * el ancla temporal se prueba AGRANDANDO la base con una fila
#     sintética posterior al corte y verificando que la medición no se
#     mueve — que es exactamente el modo de falla de la condición 4;
#   * el candado de la regla del estimador se prueba intentando computar;
#   * las opciones de la regla se prueban sobre datos sintéticos con pares
#     PLANTADOS que apuntan a la misma sesión objetivo.
#
# Nada acá escribe en ninguna base ni corre `mirada.py` contra la base
# real: ejercitar el estadístico contra la población sería la mirada
# furtiva a la que §A3.8 le pone precio.
# ============================================================

import os
import sys

import numpy as np
import pandas as pd
import pytest

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAIZ)
sys.path.insert(0, os.path.join(_RAIZ, "GEMELO", "SECUENCIAL"))

from backtest import linea_base as lb                      # noqa: E402
from bases_de_prueba import hay_filas, razon_sin_base      # noqa: E402
from GEMELO.SECUENCIAL import mirada as M                  # noqa: E402
from GEMELO.SECUENCIAL import tabla_firma as TF            # noqa: E402
from GEMELO.SECUENCIAL import ventana_antecedente as VA    # noqa: E402

HAY_BASE = hay_filas(lb.RUTA_SENALES, "verificacion_apertura")
solo_con_base = pytest.mark.skipif(
    not HAY_BASE, reason=razon_sin_base(lb.RUTA_SENALES,
                                        "verificacion_apertura"))


# ------------------------------------------------------------
# Datos sintéticos
# ------------------------------------------------------------

def _frame(filas) -> pd.DataFrame:
    """Un frame con las columnas que la capa de medición entrega."""
    return pd.DataFrame(filas, columns=[
        "fecha", "ticker", "sesion_objetivo", "gap_pct", "acierto_gap",
        "base_acierto", "retorno_real_pct", "apertura_estimada_pct",
        "exchange", "available_at"])


def _con_pares() -> pd.DataFrame:
    """Dos fechas de emisión consecutivas que apuntan a la MISMA sesión
    objetivo para el mismo ticker: el par que el cuarto dictamen señaló.

    Las dos filas del par comparten `gap_pct` —comparten sesión— pero
    tienen `apertura_estimada_pct` distinta, porque se emitieron en días
    distintos. Es el caso que importa: el gap es el mismo y el acierto NO
    tiene por qué serlo.
    """
    f = []
    for d in ("2026-09-01", "2026-09-02", "2026-09-03"):
        for i in range(3):
            f.append([d, f"T{i}", f"S{d}", 1.0, 1, 1, 0.5, 0.4,
                      "XNYS", f"{d}T20:00:00+00:00"])
    # el par: emitido el 04 y el 07, los dos apuntan a la sesión del 08
    f.append(["2026-09-04", "PAR", "2026-09-08", -2.0, 1, 0, -1.0, -0.9,
              "XNYS", "2026-09-04T20:00:00+00:00"])
    f.append(["2026-09-07", "PAR", "2026-09-08", -2.0, 0, 0, -1.0, +0.9,
              "XNYS", "2026-09-07T20:00:00+00:00"])
    return _frame(f)


# ============================================================
# ventana_antecedente — el ancla (condición 4)
# ============================================================

def test_los_dos_cortes_valen_lo_mismo_que_en_el_preregistro():
    """El corte de emisión es parte del pre-registro y no puede divergir
    del que `mirada.py` usa como frontera de la población."""
    assert VA.CORTE_EMISION == M.FECHA_CONGELAMIENTO == "2026-08-31"
    assert VA.CONVENCION == lb.CONVENCION_OFICIAL == "excluir_cero"


def test_la_medicion_no_se_mueve_si_la_base_crece_despues_del_corte(monkeypatch):
    """EL TEST DE LA CONDICIÓN 4, por comportamiento.

    Se le agrega a la base una fila sintética emitida DESPUÉS del corte de
    emisión y se verifica que la ventana antecedente no la deja entrar. Sin
    ancla —el estado anterior— esa fila entraba y movía el MDE, que es por
    lo que el cuarto dictamen midió tres valores distintos del mismo
    parámetro en tres días distintos.
    """
    base = _frame([
        ["2026-08-20", "A", "2026-08-21", 1.0, 1, 1, 0.5, 0.4, "XNYS", "x"],
        ["2026-08-31", "B", "2026-09-01", 2.0, 1, 1, 1.0, 0.8, "XNYS", "x"],
    ])
    intrusa = _frame([
        ["2026-10-22", "Z", "2026-10-23", 99.0, 0, 1, 99.0, -9.0, "XNYS", "x"],
    ])

    llamadas = {}

    def falso_cargar(hasta_sello=None, dedup=True, conocibilidad=True,
                     modelo_version=None):
        llamadas["hasta_sello"] = hasta_sello
        return pd.concat([base, intrusa], ignore_index=True)

    monkeypatch.setattr(lb, "cargar", falso_cargar)
    monkeypatch.setattr(VA, "cierre_de_ventana",
                        lambda: {"base": False, "tardias": 0,
                                 "ultima_verificacion": None})
    df = VA.cargar_antecedente()
    assert llamadas["hasta_sello"] == VA.CORTE_SELLO, (
        "la ventana tiene que pedir el corte de sello, no la base viva")
    assert set(df["ticker"]) == {"A", "B"}, "la fila posterior al corte entró"
    assert 99.0 not in set(df["gap_pct"])


def test_la_poblacion_sale_sin_columnas_de_resultado(monkeypatch):
    """El candado estructural de §A3.8: lo que no está no se puede computar.

    No es una convención de estilo. El número está a un comando de
    distancia y la regla escrita no alcanzó —`diseno_secuencial` tenía un
    lector de la base viva que computaba `ac1` sobre la población—, así que
    el cargador amputa.
    """
    monkeypatch.setattr(lb, "cargar",
                        lambda **kw: _con_pares())
    pob = VA.cargar_poblacion()
    assert len(pob), "el frame sintético cae entero en la población"
    for col in VA.COLUMNAS_DE_RESULTADO:
        assert col not in pob.columns, f"{col} sobrevivió a la amputación"
    for col in ("fecha", "ticker", "sesion_objetivo"):
        assert col in pob.columns, f"{col} hace falta para contar"


def test_fecha_para_filas_cuenta_dias_habiles_y_no_prorratea():
    """`diseno_secuencial.fecha_para_filas` multiplicaba por 7/5, que mete
    fines de semana a prorrata. Acá se cuenta día hábil por día hábil.

    Caso: el viernes 2026-10-23 con 10 filas, ritmo 1 fila por día hábil y
    objetivo 15 → 5 días hábiles → lunes 26, martes 27, miércoles 28,
    jueves 29, viernes 30.
    """
    f = VA.fecha_para_filas(objetivo=15, filas_por_dia_habil=1.0,
                            filas_hoy=10, ultima="2026-10-23")
    assert f.isoformat() == "2026-10-30"
    assert f.weekday() < 5
    assert VA.fecha_para_filas(5, 1.0, 10, "2026-10-23") is None, (
        "si ya se alcanzó, no hay fecha futura")


def test_boot_dias_es_el_mismo_remuestreador_que_el_del_frente_d():
    """La duplicación del método queda EXIGIBLE en vez de silenciosa.

    `boot_dias` vive en `ventana_antecedente` y `_boot_dias` en
    `mde_vs_observado`. Son el mismo bootstrap de clústeres de día; si uno
    deriva, este test se entera.
    """
    from GEMELO.SECUENCIAL import mde_vs_observado as MVO
    df = _con_pares()
    x = df["gap_pct"].to_numpy(float)
    fn = lambda idx: float(x[idx].mean())
    a = VA.boot_dias(df, fn, n_boot=200, semilla=7)
    b = MVO._boot_dias(df, fn, n_boot=200, semilla=7)
    assert np.array_equal(a, b)


@solo_con_base
def test_la_ventana_antecedente_esta_cerrada():
    """`CORTE_SELLO` sólo vale si ninguna fila emitida hasta el corte de
    emisión se verificó después. Si alguna aparece, la ventana creció con el
    reloj y hay que subir el corte CON ACTA, no en silencio."""
    z = VA.cierre_de_ventana()
    assert z["tardias"] == 0, (
        f"{z['tardias']} verificación(es) tardía(s); la más nueva "
        f"{z.get('tardia_mas_nueva')}. Subir CORTE_SELLO con acta y volver a "
        "correr todo lo que depende de la ventana.")


# ============================================================
# mde_desde_v6 — el MDE y su intervalo (condiciones 2 y 3)
# ============================================================

def test_el_mde_escala_con_el_costo_y_cae_con_la_magnitud():
    """Comportamiento de la fórmula, no su reescritura: el MDE es
    proporcional al costo y decreciente en E|gap|."""
    from GEMELO.SECUENCIAL.mde_desde_v6 import mde_simetrico
    a = mde_simetrico(0.5, 0.03, 0.0025)
    assert mde_simetrico(0.5, 0.03, 0.0050) == pytest.approx(2 * a)
    assert mde_simetrico(0.5, 0.06, 0.0025) == pytest.approx(a / 2)
    assert mde_simetrico(1.0, 0.03, 0.0025) == pytest.approx(2 * a)


@solo_con_base
def test_el_mde_no_se_mueve_si_la_base_crece_despues_del_corte():
    """El mismo test de ancla, pero de punta a punta sobre el script.

    Dos mediciones con cortes de sello distintos —el del pre-registro y uno
    muy posterior— tienen que dar el MISMO número, porque el corte de
    EMISIÓN ya cierra la ventana. Antes de la corrida 17 este test no podía
    existir: el script no tenía corte.
    """
    from GEMELO.SECUENCIAL import mde_desde_v6 as MD
    a = MD.medir()
    corte_viejo = VA.CORTE_SELLO
    try:
        VA.CORTE_SELLO = "2027-12-31"
        b = MD.medir()
    finally:
        VA.CORTE_SELLO = corte_viejo
    assert a["n"] == b["n"]
    assert a["mde_pp"] == pytest.approx(b["mde_pp"])
    assert a["p_d"] == pytest.approx(b["p_d"])


@solo_con_base
def test_el_intervalo_conjunto_es_mas_ancho_que_el_de_un_solo_insumo():
    """La corrección de la condición 3, por comportamiento.

    El intervalo que la v5 publicaba propagaba sólo E|gap|. Propagar
    también `f` sólo puede ensanchar: si no lo hace, la propagación no está
    ocurriendo.
    """
    from GEMELO.SECUENCIAL import mde_desde_v6 as MD
    m = MD.medir()
    conj = m["mde_ic_pp"][1] - m["mde_ic_pp"][0]
    solo = m["mde_ic_solo_e_gap_pp"][1] - m["mde_ic_solo_e_gap_pp"][0]
    assert conj > solo, (f"conjunto {conj:.3f} no es más ancho que "
                         f"el de un insumo {solo:.3f}")


@solo_con_base
def test_p_d_del_plan_es_la_que_mide_el_script():
    """Una constante de planificación que no reproduce desde su script es
    la condición 4 otra vez, un nivel más abajo."""
    import diseno_secuencial as D
    from GEMELO.SECUENCIAL import mde_desde_v6 as MD
    assert D.P_D_OBSERVADA == pytest.approx(MD.medir()["p_d"], abs=5e-4)


# ============================================================
# mirada — la regla del estimador (condición 1)
# ============================================================

def test_la_regla_del_estimador_sin_firmar_bloquea_la_mirada():
    """El segundo candado. Elegir cómo se agrupan los clústeres después de
    ver los datos es elegir la varianza después de verlos."""
    assert M.REGLA_DEDUP_ESTIMADOR is None, "si cambió, la firma ya ocurrió"
    with pytest.raises(SystemExit) as exc:
        M._guard_regla_estimador()
    assert "SIN FIRMAR" in str(exc.value)
    with pytest.raises(SystemExit):
        M.aplicar_regla_estimador(_con_pares())


def test_la_regla_prohibida_no_se_puede_elegir():
    """`keep_last` está en la lista para que conste que se consideró, no
    para poder usarse: el acta §60 la prohibió."""
    assert "keep_last" in M.REGLAS_DEDUP_ESTIMADOR
    assert "keep_last" in M.REGLAS_PROHIBIDAS
    with pytest.raises(SystemExit) as exc:
        M._guard_regla_estimador("keep_last")
    assert "PROHIBIDA" in str(exc.value)


def test_cada_opcion_hace_lo_que_dice_sobre_pares_plantados():
    df = _con_pares()
    assert len(df) == 11

    ambas, clave = M.aplicar_regla_estimador(df, "conservar_ambas")
    assert len(ambas) == 11 and clave == "fecha"
    # el par cae en DOS clústeres distintos: el defecto del cuarto dictamen
    par = ambas[ambas["ticker"] == "PAR"]
    assert par["fecha"].nunique() == 2
    assert par["sesion_objetivo"].nunique() == 1

    porses, clave = M.aplicar_regla_estimador(
        df, "clusterizar_por_sesion_objetivo")
    assert len(porses) == 11 and clave == "sesion_objetivo"
    assert porses[porses["ticker"] == "PAR"]["sesion_objetivo"].nunique() == 1

    col, clave = M.aplicar_regla_estimador(df, "colapsar_el_par")
    assert len(col) == 10 and clave == "fecha"
    assert (col["ticker"] == "PAR").sum() == 1
    # sobrevive la emisión más temprana, nunca la más fresca
    assert col[col["ticker"] == "PAR"]["fecha"].iloc[0] == "2026-09-04"


def test_colapsar_y_keep_first_son_la_misma_operacion():
    """Las dos opciones que la tarjeta enumera por separado coinciden, y el
    código lo dice en vez de fingir que son dos ramas."""
    df = _con_pares()
    a, ka = M.aplicar_regla_estimador(df, "colapsar_el_par")
    b, kb = M.aplicar_regla_estimador(df, "keep_first")
    assert ka == kb
    pd.testing.assert_frame_equal(a, b)


def test_el_clustter_por_sesion_objetivo_junta_al_par_y_eso_mueve_v_hat():
    """La dirección del efecto, medida sobre datos SINTÉTICOS.

    Se plantan pares cuyas dos filas tienen contribución idéntica. Agrupando
    por fecha de emisión caen en clústeres distintos y el remuestreador las
    trata como independientes; agrupando por sesión objetivo caen juntas y
    su correlación entra en `V̂`. Si la queja del cuarto dictamen es
    correcta, `V̂` por sesión objetivo tiene que ser MAYOR.

    Se mide acá y no sobre la población porque computar `V̂` sobre la
    población es la mirada que §A3.8 cobra.
    """
    filas = []
    for j in range(20):
        d1 = f"2026-09-{2*j+1:02d}"
        d2 = f"2026-09-{2*j+2:02d}"
        ses = f"S{j:02d}"
        # Las DOS filas del par tienen la misma contribución, y los pares
        # alternan de signo. La alternancia hace falta: si todos los
        # clústeres valen lo mismo, la varianza remuestreada es cero y el
        # estimador entra —correctamente— en su rama degenerada, que no es
        # lo que este test quiere medir.
        mod, base = (1, 0) if j % 2 == 0 else (0, 1)
        filas.append([d1, "PAR", ses, -1.0, mod, base, -1.0, -0.5, "XNYS", "x"])
        filas.append([d2, "PAR", ses, -1.0, mod, base, -1.0, -0.5, "XNYS", "x"])
    df = _frame(filas)
    v_fecha = M.varianza_cluster(df, "fecha")
    v_sesion = M.varianza_cluster(df, "sesion_objetivo")
    assert v_fecha["degenerado"] is None and v_sesion["degenerado"] is None
    assert v_sesion["fechas"] == 20, "20 sesiones objetivo"
    assert v_fecha["fechas"] == 40, "40 fechas de emisión"
    assert v_sesion["v_hat"] > v_fecha["v_hat"], (
        f"V̂ por sesión {v_sesion['v_hat']:.3f} no supera a "
        f"V̂ por fecha {v_fecha['v_hat']:.3f}: si esto falla, la queja del "
        "cuarto dictamen no se sostiene como está escrita")
    # Y el tamaño del efecto, que es lo que la tarjeta necesita: con pares
    # perfectamente correlacionados el clúster por fecha de emisión
    # subestima la varianza en un factor ~2, porque parte cada par en dos
    # clústeres que el remuestreador trata como independientes.
    assert v_sesion["v_hat"] / v_fecha["v_hat"] == pytest.approx(2.0, rel=0.15)


def test_pares_misma_sesion_reporta_la_distribucion_de_tamanos():
    """E8 del quinto dictamen. La función imprimía «N filas en M grupos» al
    lado de una prosa que decía «pares», y en la población hay grupos de
    CUATRO: 38 filas en 15 grupos no son 15 pares. El entero que contradecía
    al texto se imprimía junto al texto.
    """
    filas = []
    # un grupo de DOS
    for d in ("2026-09-01", "2026-09-02"):
        filas.append([d, "DOS", "2026-09-03", 1.0, 1, 1, 0.5, 0.4, "XNYS", "x"])
    # un grupo de CUATRO
    for d in ("2026-09-07", "2026-09-08", "2026-09-09", "2026-09-10"):
        filas.append([d, "CUATRO", "2026-09-11", 1.0, 1, 1, 0.5, 0.4,
                      "XNYS", "x"])
    # una fila sola, que no entra a ningún grupo
    filas.append(["2026-09-14", "SOLA", "2026-09-15", 1.0, 1, 1, 0.5, 0.4,
                  "XNYS", "x"])
    r = VA.pares_misma_sesion(_frame(filas))
    assert r["filas_en_pares"] == 6, "2 + 4, y la fila sola no cuenta"
    assert r["grupos"] == 2
    assert r["reparto_por_tamano"] == {2: 1, 4: 1}
    assert r["grupo_mas_grande"] == 4
    # la aritmética que nadie cruzó: grupos × 2 NO es filas en grupos
    assert r["filas_en_pares"] != 2 * r["grupos"]


def test_contribuciones_por_fecha_sigue_siendo_el_alias_declarado():
    df = _con_pares()
    assert np.array_equal(M.contribuciones_por_fecha(df),
                          M.contribuciones(df, "fecha"))


# ============================================================
# tabla_firma — N_max, el calendario y el MDE crítico
# ============================================================

def test_el_mde_mueve_n_pero_nunca_los_umbrales():
    """Lo que el pre-registro promete. Se prueba como invariante y no
    contra dos n cableados: los dos que estaban cableados se derivaron con
    un `p_d` de la rama de filas que la decisión D1 derogó.
    """
    p_chico = M.plan(0.05)
    p_grande = M.plan(0.15)
    assert p_chico[4][0] > p_grande[4][0], "N_max decrece con el MDE"
    for p in (p_chico, p_grande):
        assert [p[k][1] for k in (1, 2, 3, 4)] == list(M.UMBRALES_OBF)
        assert [p[k][2] for k in (1, 2, 3, 4)] == list(M.Z_FUTILIDAD)
    # y las fracciones de información siguen siendo las del plan
    assert [p_chico[k][0] / p_chico[4][0] for k in (1, 2, 3, 4)] == \
        pytest.approx(list(M.FRACCIONES), abs=1e-3)


def test_las_tablas_de_n_max_y_de_fechas_quedaron_vacias_a_proposito():
    """Dos diccionarios con los valores viejos adentro son una invitación a
    firmar uno de los dos."""
    assert M.N_MAX_POR_MDE == {}
    assert M.FECHAS_POR_MDE == {}


def test_el_mde_critico_es_el_punto_donde_la_primera_mirada_ya_vencio():
    """Comportamiento: en el MDE crítico, el n de la mirada 1 coincide con
    las filas ya contadas; un poco por encima está vencida y un poco por
    debajo no."""
    p_d, filas = 0.49, 288
    critico = TF.mde_critico(p_d, filas)
    n_en_el_critico = 0.25 * TF.n_max(critico, p_d)["n_max"]
    assert n_en_el_critico == pytest.approx(filas, rel=1e-3)
    assert 0.25 * TF.n_max(critico * 1.05, p_d)["n_max"] < filas
    assert 0.25 * TF.n_max(critico * 0.95, p_d)["n_max"] > filas


def test_la_potencia_no_acepta_argumentos_que_no_lee():
    """E4 del quinto dictamen: `potencia_del_plan(mde, p_d)` tomaba dos
    argumentos y no leía ninguno. Una firma que acepta lo que ignora invita
    a creer que la cifra es condicional a ellos, y la potencia del plan no
    depende del MDE: el MDE se paga en `N_max`."""
    import inspect
    assert not inspect.signature(TF.potencia_del_plan).parameters
    with pytest.raises(TypeError):
        TF.potencia_del_plan(0.10, 0.49)


def test_el_factor_secuencial_compra_de_verdad_la_potencia_080():
    """F7 del re-dictamen: el test anterior era TAUTOLÓGICO.

    Evaluaba la potencia en el drift que la bisección acababa de despejar
    para dar 0.80, así que `potencia_idealizada` era 0.80 por construcción —
    independiente de `FACTOR_SECUENCIAL`, de `N_max`, de `p_d` y del MDE— y
    el test no podía fallar. Era el defecto N8 del tercer dictamen («cuatro
    tests tautológicos») reintroducido dentro de la función que la exigencia
    E4 venía a arreglar.

    Éste sí puede fallar, y de hecho **fallaba** con el factor cableado en
    1.0241, que daba 0.7991: lo que fija es que el factor COMPRE la potencia
    que el plan promete. Si las fronteras cambian y el factor no se
    recomputa, este test se entera.
    """
    p = TF.potencia_del_plan()
    assert p["potencia_idealizada"] == pytest.approx(0.80, abs=5e-4), (
        "el drift que FACTOR_SECUENCIAL compra no da la potencia del plan")
    # y el factor NO es el valor cableado hasta la corrida 17
    assert TF.FACTOR_SECUENCIAL != TF.FACTOR_SECUENCIAL_CABLEADO_HASTA_LA_CORRIDA_17
    assert TF.FACTOR_SECUENCIAL == pytest.approx(TF.factor_secuencial())
    # EL FACTOR VIVE EN UN SOLO LUGAR, y éste es el test que lo exige
    # (dictamen de cierre, O-1): tenerlo en dos dejó dos generaciones de
    # `N_max` vivas, o sea dos respuestas a «¿con qué n se dispara la mirada
    # 1?» entre el script que CORRE la mirada y la tabla que se FIRMA.
    import diseno_secuencial as D
    assert TF.FACTOR_SECUENCIAL == pytest.approx(D.factor_secuencial())
    for mde in (0.05, 0.07, 0.10, 0.15):
        assert M._n_max(mde) == round(TF.n_max(mde, D.P_D_OBSERVADA)["n_max"]), (
            f"mirada.py y tabla_firma.py dan N_max distintos a {mde}: "
            "el factor volvió a vivir en dos lugares")
    # contraprueba: con el factor viejo la potencia NO llega a 0.80
    import diseno_secuencial as D
    from evaluacion import norm_ppf
    malla = D.Malla(D.FRACCIONES, m=2001, ancho=7.0)
    viejo = (norm_ppf(0.975) + norm_ppf(0.80)) * (
        TF.FACTOR_SECUENCIAL_CABLEADO_HASTA_LA_CORRIDA_17 ** 0.5)
    p_viejo, _ = D.potencia_secuencial(malla, list(D.UMBRALES_OBF), viejo)
    assert p_viejo < 0.80 - 5e-4, (
        "si el factor viejo diera 0.80, la corrección de N3 no tendría objeto")


def test_la_potencia_con_la_regla_del_maximo_es_menor_que_la_idealizada():
    """El agujero de §A3.3: la regla del máximo infla `V̂` y eso se paga en
    potencia, no en α."""
    p = TF.potencia_del_plan()
    assert p["potencia_con_regla_del_maximo"] < p["potencia_idealizada"]
    assert 0.70 < p["potencia_con_regla_del_maximo"] < 0.80


@solo_con_base
def test_los_extremos_del_abanico_caen_fuera_del_intervalo_honesto():
    """F8 del re-dictamen, y fija la afirmación que el documento publica.

    `p_d` ES `f`, así que meter el borde del IC del MDE en Connor con `p_d`
    en su punto combina réplicas distintas del mismo remuestreo. El
    documento afirma que **los dos extremos del abanico caen FUERA del
    intervalo honesto**; sin este test eso es prosa que nada sujeta.
    """
    c = TF.propagacion_conjunta()
    lo, hi = c["n_max_ic"]
    assert lo < c["n_max_mediana"] < hi
    t = TF.tabla()
    n_max_abanico = [f["n_max"] for f in t["filas"]]
    assert min(n_max_abanico) < lo, (
        f"el extremo bajo del abanico ({min(n_max_abanico)}) tendría que "
        f"caer por debajo del IC honesto ({lo:.0f})")
    assert max(n_max_abanico) > hi, (
        f"el extremo alto del abanico ({max(n_max_abanico)}) tendría que "
        f"caer por encima del IC honesto ({hi:.0f})")
    # y P(vencida) viaja con su Wilson y con su glosa condicional
    w_lo, w_hi = c["p_vencida_wilson"]
    assert w_lo < c["p_mirada1_vencida"] < w_hi
    assert "condicional" in c["p_vencida_glosa"]


# ============================================================
# Aislamiento: la capa de investigación no toca la de sellado
# ============================================================

@pytest.mark.parametrize("modulo", ["ventana_antecedente", "tabla_firma",
                                    "mde_desde_v6"])
def test_ningun_modulo_nuevo_importa_la_ruta_de_sellado(modulo):
    fuente = open(os.path.join(_RAIZ, "GEMELO", "SECUENCIAL", f"{modulo}.py"),
                  encoding="utf-8").read()
    for prohibido in ("import motor", "from motor", "import snapshot",
                      "from snapshot", "import senales", "from senales",
                      "import alertas", "from alertas"):
        assert prohibido not in fuente, f"{modulo} importa {prohibido}"
