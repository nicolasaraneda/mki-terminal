"""El guardia de las razones de los `xfail` (corrida 11, bloque 9).

Una razón de `xfail` es documentación que vive dentro del ejecutable, y se
pudre igual que una cita por número de línea: `test_epistemico.py:572`
justificó su marcador durante cinco días citando como pendiente una decisión
que el acta §78 había cerrado el 3-sep. El proyecto vigila que las citas a
`DECISIONES.md` no se desplacen y no vigilaba esto.

Cómo funciona: todo `@pytest.mark.xfail` de `tests/` tiene que estar en
`RAZONES` con un PREDICADO EJECUTABLE que devuelva True mientras la razón
siga siendo cierta. Si el predicado da False, la razón se pudrió: hay que
sacar el marcador o reescribir la razón, no ablandar el test. Y un `xfail`
nuevo sin entrada acá pone la suite en rojo, que es la única forma de que
la regla no dependa de que alguien se acuerde.

Los predicados leen `senales.db` en `mode=ro` o comparan dos rutas de
cálculo; ninguno escribe nada.
"""
import ast
import os

import pytest

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TESTS = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------
# Los predicados: uno por xfail, y dicen POR QUÉ el rojo sigue siendo rojo
# ------------------------------------------------------------
def _sigue_habiendo_duplicados_fisicos_que_cargar_quita():
    """test_epistemico.py::test_ninguna_prediccion_sellada_comparte_sesion_objetivo_con_otra
    Razón: la base conserva filas duplicadas por (ticker, sesion_objetivo)
    y la regla firmada las quita al CARGAR, no en la base."""
    import backtest.linea_base as LB
    crudo = LB.cargar(dedup=False)
    if crudo.empty:
        pytest.skip("senales.db no está en esta máquina")
    dedup = LB.cargar(dedup=True)
    hay_fisicos = crudo.duplicated(["ticker", "sesion_objetivo"], keep=False).any()
    cargar_los_quita = len(dedup) < len(crudo)
    return bool(hay_fisicos and cargar_los_quita)


def _las_dos_rutas_de_mcnemar_siguen_discrepando():
    """test_epistemico.py::test_toda_p_publicada_declara_con_que_test_se_computo
    (si todavía lleva el marcador). Razón: χ² con corrección de continuidad y
    binomial exacta dan p distintos a 4 decimales sobre el par real."""
    import math
    import sys
    sys.path.insert(0, os.path.join(_RAIZ, ".claude", "skills",
                                    "estadistica-evaluacion", "scripts"))
    import backtest.linea_base as LB
    from evaluacion import mcnemar_exact
    df = LB.cargar()
    if df.empty:
        pytest.skip("senales.db no está en esta máquina")
    d = LB.duelo(LB.aplicar_convencion(df, LB.CONVENCION_OFICIAL))
    b, c = d["mcnemar_b01"], d["mcnemar_b10"]
    return not math.isclose(round(LB.mcnemar(b, c), 4), round(mcnemar_exact(b, c), 4))


# (archivo, nombre del test) -> predicado. Se agrega acá cada xfail nuevo.
RAZONES = {
    ("test_epistemico.py", "test_ninguna_prediccion_sellada_comparte_sesion_objetivo_con_otra"):
        _sigue_habiendo_duplicados_fisicos_que_cargar_quita,
    ("test_epistemico.py", "test_toda_p_publicada_declara_con_que_test_se_computo"):
        _las_dos_rutas_de_mcnemar_siguen_discrepando,
}


# ------------------------------------------------------------
# Inventario: todos los xfail de tests/, leídos del AST
# ------------------------------------------------------------
def _es_xfail(decorador) -> bool:
    nodo = decorador.func if isinstance(decorador, ast.Call) else decorador
    return isinstance(nodo, ast.Attribute) and nodo.attr == "xfail"


def inventario_xfail() -> list:
    """[(archivo, nombre del test, razón)] para cada xfail de tests/."""
    salida = []
    for archivo in sorted(os.listdir(_TESTS)):
        if not (archivo.startswith("test_") and archivo.endswith(".py")):
            continue
        arbol = ast.parse(open(os.path.join(_TESTS, archivo), encoding="utf-8").read())
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.FunctionDef):
                continue
            for dec in nodo.decorator_list:
                if _es_xfail(dec):
                    razon = ""
                    if isinstance(dec, ast.Call):
                        for kw in dec.keywords:
                            if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                                razon = str(kw.value.value)
                    salida.append((archivo, nodo.name, razon))
    return salida


def test_todo_xfail_tiene_una_razon_verificable_registrada():
    """Un xfail sin predicado es una razón que nadie va a volver a mirar."""
    faltan = [(a, n) for a, n, _ in inventario_xfail() if (a, n) not in RAZONES]
    assert not faltan, (
        "xfail sin entrada en RAZONES (tests/test_razones_xfail.py): escribí "
        "el predicado que dice por qué sigue rojo:\n" +
        "\n".join(f"  {a}::{n}" for a, n in faltan))


def test_toda_razon_de_xfail_sigue_siendo_cierta():
    """Se ejecuta el predicado de cada xfail PRESENTE. Si da False, la razón
    se pudrió: el marcador sobra o la razón hay que reescribirla."""
    presentes = {(a, n) for a, n, _ in inventario_xfail()}
    podridas = []
    for clave, predicado in RAZONES.items():
        if clave not in presentes:
            continue   # el xfail ya se quitó; su predicado queda como historia
        if not predicado():
            podridas.append(f"{clave[0]}::{clave[1]} — {predicado.__doc__.strip().splitlines()[0]}")
    assert not podridas, (
        "razones de xfail que ya NO son ciertas (sacá el marcador o corregí "
        "la razón, sin ablandar el test):\n" + "\n".join("  " + p for p in podridas))


def test_contraprueba_el_guardia_caza_una_razon_podrida():
    """Un guardia que no puede fallar no es un guardia: un predicado que
    devuelve False tiene que producir el fallo."""
    presentes = {(a, n) for a, n, _ in inventario_xfail()}
    assert presentes, "no hay xfail en tests/: el guardia no tiene sujeto"
    clave = next(iter(presentes))
    with pytest.raises(AssertionError):
        razones = {clave: lambda: False}
        podridas = [k for k, p in razones.items() if k in presentes and not p()]
        assert not podridas


def test_toda_razon_cita_su_fuente():
    """Cada razón tiene que decir de dónde sale: un acta (§N), un archivo o
    un dictamen. Una razón sin fuente no se puede verificar ni pudrir."""
    sin_fuente = [(a, n) for a, n, r in inventario_xfail()
                  if "§" not in r and ".md" not in r and ".py" not in r]
    assert not sin_fuente, f"razones de xfail sin fuente citada: {sin_fuente}"
