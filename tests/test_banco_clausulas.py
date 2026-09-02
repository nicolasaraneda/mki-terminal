# ============================================================
# tests/test_banco_clausulas.py — el banco de pruebas, probado
#
# Un banco de pruebas sin pruebas propias es una opinión con tablas. Lo
# que se fija acá es lo que hace que sus veredictos signifiquen algo:
#
#   · que REPRUEBA una cláusula que lee el resultado (contraprueba viva)
#   · que su PRUEBA 1b no depende de la declaración de la cláusula
#   · que REPRODUCE una cifra que otra vía ya midió (validación externa)
#   · que no ofrece en ninguna forma la regla PROHIBIDA por frescura
#   · que es de solo lectura y no muta lo que se le pasa
#   · que el hallazgo estructural (calza == a tiempo) se mide, no se cree
# ============================================================

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backtest.linea_base as lb                        # noqa: E402
from GEMELO import banco_clausulas as bc                # noqa: E402

solo_con_base = pytest.mark.skipif(
    not os.path.exists(lb.RUTA_SENALES), reason="sin senales.db")


@pytest.fixture(scope="module")
def base():
    return bc.cargar_base(hasta_sello=bc.CORTE_BANCO)


# ------------------------------------------------------------
# El banco tiene que poder reprobar
# ------------------------------------------------------------
@solo_con_base
def test_la_clausula_trampa_es_reprobada_por_la_prueba_1(base):
    """LA CONTRAPRUEBA. Si el banco no reprueba una cláusula que se queda
    con las filas que el modelo acertó, el banco no mide nada y todos sus
    aprobados son ruido."""
    r = bc.prueba_1_metadata(bc.CLAUSULA_TRAMPA, base, n_perm=25, n_boot=200)
    assert not r["pasa"]
    assert not r["1a_pasa"]          # la declara
    assert not r["1b_pasa"]          # y además se mide


@solo_con_base
def test_la_prueba_1b_no_confia_en_la_declaracion(base):
    """1b tiene que atrapar a una cláusula que LEE el resultado y MIENTE
    al declarar sus campos. Si 1b dependiera de la declaración, bastaría
    con no declarar nada para pasar."""
    mentirosa = bc.Clausula(
        nombre="mentirosa", texto="", operacionalizacion="", procedencia="",
        campos=("fecha", "ticker"),                     # declara metadata
        seleccionar=lambda df: df.index[df["acierto_gap"] == 1],  # lee gap
        es_candidata=False)
    r = bc.prueba_1_metadata(mentirosa, base, n_perm=25, n_boot=200)
    assert r["1a_pasa"], "la declaración mentirosa pasa 1a, como debe ser"
    assert not r["1b_pasa"], "1b tiene que atraparla igual"
    assert not r["pasa"]


@solo_con_base
def test_un_campo_no_clasificado_no_se_aprueba_por_omision(base):
    """El silencio no es una clasificación: un campo que no está ni en la
    lista de seguros ni en la de prohibidos reprueba 1a hasta que alguien
    lo clasifique."""
    rara = bc.Clausula(
        nombre="rara", texto="", operacionalizacion="", procedencia="",
        campos=("un_campo_que_nadie_clasifico",),
        seleccionar=lambda df: df.index, es_candidata=False)
    r = bc.prueba_1_metadata(rara, base, n_perm=5, n_boot=200)
    assert not r["1a_pasa"]
    assert r["1a_sin_clasificar"] == ["un_campo_que_nadie_clasifico"]


# ------------------------------------------------------------
# El banco tiene que medir bien lo que deja pasar
# ------------------------------------------------------------
@solo_con_base
def test_validacion_externa_c4b_reproduce_keep_first(base):
    """LA VALIDACIÓN EXTERNA. C4b, implementada acá de forma
    independiente, tiene que dar la cifra que `dedup_opciones.md` ya
    publicó para `keep="first"`. Si no reprodujera, el instrumento
    estaría mal y ningún veredicto suyo valdría."""
    sel = pd.Index(bc.C4B_MISMO_EVENTO.seleccionar(base))
    sub = base.loc[base.index.intersection(sel)]
    b, c = bc._bc(sub)
    assert len(sub) == bc.ANCLA_C4B["n"]
    assert (b, c) == (bc.ANCLA_C4B["b"], bc.ANCLA_C4B["c"])


@solo_con_base
def test_el_hallazgo_estructural_se_mide_y_no_se_cree(base):
    """`sesion_calza` (criterio de la regla firmada) y `sello_a_tiempo`
    (criterio de la cláusula 3, leído contra la apertura) tienen que ser
    el MISMO indicador fila por fila. Es álgebra —`sesion_objetivo` se
    selló desde el reloj de pared— pero se fija medido, porque un
    argumento sobre código que nadie recompiló es una hipótesis.

    Si esto dejara de valer, el informe estaría afirmando una identidad
    que ya no existe, y hay que enterarse acá."""
    assert (base["sesion_calza"].astype(bool)
            == base["sello_a_tiempo"].astype(bool)).all()


@solo_con_base
def test_el_banco_no_muta_lo_que_se_le_pasa(base):
    """Solo lectura de verdad: correr todas las cláusulas no puede
    cambiar ni una celda de la base. Si mutara, la PRUEBA 3b —que
    justamente vigila eso— estaría vigilándose a sí misma."""
    antes = pd.util.hash_pandas_object(base, index=True).sum()
    for cl in bc.TODAS + (bc.CLAUSULA_TRAMPA,):
        cl.seleccionar(base)
    assert pd.util.hash_pandas_object(base, index=True).sum() == antes


@solo_con_base
def test_toda_seleccion_es_un_subconjunto(base):
    """Una cláusula selecciona filas; no inventa ninguna. Si devolviera
    un índice ajeno, «antes» y «después» dejarían de ser comparables."""
    for cl in bc.TODAS:
        assert set(cl.seleccionar(base)).issubset(set(base.index)), cl.nombre


# ------------------------------------------------------------
# Las reglas de la casa, aplicadas al propio banco
# ------------------------------------------------------------
def test_el_banco_no_ofrece_la_regla_prohibida_por_frescura():
    """Cuarta regla de la casa: un número retirado que sigue ofrecido en
    el código vuelve a circular. `keep="last"` está PROHIBIDA por la
    firma del 1-sep, así que este módulo no puede ofrecerla como código
    ejecutable — ni como llamada, ni como default, ni como opción.

    Se comprueba sobre el AST y no sobre el texto: el módulo NOMBRA la
    regla prohibida en su documentación, que es exactamente lo que hay
    que hacer con una prohibición, y un grep no distingue nombrarla de
    ofrecerla."""
    import ast
    with open(bc.__file__, encoding="utf-8") as fh:
        arbol = ast.parse(fh.read())
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call):
            for kw in nodo.keywords:
                if kw.arg == "keep" and isinstance(kw.value, ast.Constant):
                    assert kw.value.value != "last", (
                        "el banco ofrece keep='last', que la firma prohibió")


@solo_con_base
def test_ningun_estimador_puntual_sale_sin_intervalo(base):
    """Tercera regla de la casa, aplicada al propio banco: toda cifra que
    el banco reporta como punto tiene que traer su intervalo computado.
    Se verifica sobre las dos que podrían escaparse."""
    r = bc.prueba_2_bc(bc.C1_SOLO_MAC, base, n_boot=200)
    for lado in ("ventaja_antes", "ventaja_despues"):
        assert "lo" in r[lado] and "hi" in r[lado], lado
    a = bc.asociacion_criterio_acierto(
        base, bc.C1_SOLO_MAC.criterio(base).astype(bool), n_boot=200)
    assert a["ic95_cluster_dia"][0] is not None
    assert a["ic95_cluster_dia"][1] is not None


@solo_con_base
def test_la_semilla_hace_reproducible_el_intervalo(base):
    """Un bootstrap sin semilla no reproduce; con semilla, dos corridas
    tienen que dar el mismo intervalo hasta el último dígito."""
    crit = bc.C1_SOLO_MAC.criterio(base).astype(bool)
    a = bc.asociacion_criterio_acierto(base, crit, n_boot=300)
    b = bc.asociacion_criterio_acierto(base, crit, n_boot=300)
    assert a["ic95_cluster_dia"] == b["ic95_cluster_dia"]


@solo_con_base
def test_la_atribucion_de_maquina_tiene_dos_varas(base):
    """El corte del documento de composición y `plataforma_version`
    —sellada fila por fila— tienen que coincidir. Si dejaran de hacerlo,
    la identidad de máquina dependería de la memoria de un documento y
    `cargar_base` aborta. Acá se fija que la comprobación existe y pasa."""
    bc._verificar_corroboracion_maquina(base)
    assert set(base["maquina"].unique()) <= {"MAC", "PC"}


@solo_con_base
def test_la_ventana_de_solapamiento_se_lee_de_la_evidencia(base):
    """No se cablea ninguna fecha: la ventana sale de
    `data/sombra/veredictos.jsonl`. Un día con veredicto
    DIA_NO_COMPUTABLE (el titular no selló) NO es solapamiento."""
    v = bc.ventana_solapamiento()
    assert "2026-08-28" not in v, "el 28-ago el titular no selló"
    assert set(base.loc[base["solapamiento"], "fecha"].unique()) <= set(v)


# ------------------------------------------------------------
# Los veredictos, fijados
# ------------------------------------------------------------
@solo_con_base
def test_la_prueba_3b_es_la_fatal_y_la_3a_no(base):
    """Separar 3a de 3b no es una concesión: la regla YA FIRMADA falla 3a
    —toca filas anteriores al corte— y sin embargo es la regla vigente.
    Si el banco tratara 3a como fatal, reprobaría lo que el proyecto ya
    decidió, y ese veredicto no diría nada útil sobre una candidata."""
    r = bc.evaluar(bc.C0_REGLA_FIRMADA, base, n_boot=200, n_perm_inv=5)
    assert not r["prueba_3"]["3a_pasa"]
    assert r["prueba_3"]["3b_pasa"]
    assert not r["veredicto"].startswith("REPROBADA")


@solo_con_base
def test_la_alarma_del_bc_dispara_donde_disparo_con_keep_last(base):
    """La firma que destapó `keep="last"`: `c` se mueve, `b` no, y las
    discordantes retiradas van todas en el mismo sentido. Se fija sobre
    la cláusula 3, que la reproduce."""
    r = bc.prueba_2_bc(bc.C3A_A_TIEMPO_APERTURA, base, n_boot=200)
    assert r["delta_b"] == 0
    assert r["delta_c"] < 0
    assert r["retiradas_tipo_b"] == 0
    assert r["exige_mecanismo"]


@solo_con_base
def test_una_poblacion_sin_discordancias_no_pasa_por_limpia(base):
    """C2 deja 16 filas y CERO pares discordantes. Sin discordancias la
    alarma de asimetría no puede dispararse — y eso no es un aprobado.
    El banco tiene que llamarlo por su nombre."""
    r = bc.prueba_2_bc(bc.C2_AMBAS, base, n_boot=200)
    assert r["b_despues"] + r["c_despues"] == 0
    assert r["sin_poder_resolutivo"]
    assert not r["exige_mecanismo"]     # no dispara, y por eso hace falta el otro


@solo_con_base
def test_las_dos_lecturas_de_la_clausula_4_dan_veredictos_opuestos(base):
    """«Iguales» sobre el desenlace lee el resultado; «iguales» sobre la
    identidad del evento no. La palabra es toda la cláusula, y el banco
    tiene que distinguirlas en vez de promediarlas."""
    a = bc.prueba_1_metadata(bc.C4_IGUALES_UNA_VEZ, base, n_perm=25, n_boot=200)
    b = bc.prueba_1_metadata(bc.C4B_MISMO_EVENTO, base, n_perm=25, n_boot=200)
    assert not a["pasa"]
    assert b["pasa"]
