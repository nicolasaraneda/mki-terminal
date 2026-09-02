"""El defecto de unidades del PSR/DSR (octava corrida, Frente A, A3).

`inferencia.var_sharpe` trabaja con el Sharpe POR PERÍODO. Los dos
llamadores del proyecto le pasaban el Sharpe ANUALIZADO con n = días, y el
z quedaba inflado por √252: bajo la nula el DSR superaba 0,95 en más de un
cuarto de las réplicas (`calibracion_instrumento.md`). Estos tests fijan
(1) la propiedad estadística con el umbral que corresponde al tamaño real
(~0,001, no 0,05) y (2) que NINGÚN llamador del repositorio pase a
`psr`/`dsr` algo que no esté en la lista blanca — recorriendo el repo
entero, no dos rutas escritas a mano (dictamen del adversario, 2-sep).
"""
import ast
import math
import os

import numpy as np

from backtest import inferencia as inf

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _tasa_dsr_bajo_nula(anualizar: float, N=40, T=250, n_rep=1000, semilla=11) -> float:
    rng = np.random.default_rng(semilla)
    rech = 0
    for _ in range(n_rep):
        r = rng.standard_t(4, size=(N, T)) * 0.01
        sh = r.mean(axis=1) / r.std(axis=1, ddof=1) * math.sqrt(anualizar)
        V = float(sh.var(ddof=1))
        try:
            rech += inf.dsr(float(sh.max()), T, 0.0, 3.0, N, V) >= 0.95
        except inf.ErrorUnidadSharpe:
            # la guarda de unidad atrapó un anualizado: en el defecto ese z
            # inflado habría dado DSR ≥ 0,95, así que cuenta como rechazo
            rech += 1
    return rech / n_rep


def test_el_dsr_por_periodo_tiene_el_tamano_teorico_no_el_5_por_ciento():
    """El tamaño teórico gaussiano de «DSR ≥ 0,95» a N = 40 es ~0,003; con
    1.000 réplicas se exige ≤ 0,01 (el ≤ 0,05 anterior pasaba con una tasa
    treinta veces mayor que la correcta)."""
    assert _tasa_dsr_bajo_nula(1) <= 0.01


def test_contraprueba_el_dsr_anualizado_si_rechaza_de_mas():
    """La contraprueba: con la unidad equivocada el tamaño se dispara.
    Si esto deja de fallar, alguien arregló `var_sharpe` para que acepte
    Sharpes anualizados, y entonces hay que revisar los llamadores."""
    assert _tasa_dsr_bajo_nula(252, n_rep=300) >= 0.15


def test_anualizar_es_la_inversa_exacta():
    assert inf.anualizar_sharpe(0.3459) == 0.3459 * math.sqrt(inf.PERIODOS_POR_ANIO)


# Lista BLANCA: (archivo relativo, expresiones permitidas como primer
# argumento de psr/dsr). Todo lo demás en el repo es un llamador ilegal.
LISTA_BLANCA = {
    "backtest/inferencia.py": {"sr"},                           # dsr llama a psr con su propio argumento por período
    "backtest/veredicto_51.py": {"sr_p"},
    "GEMELO/control_lineal.py": {"sr_p"},
    "GEMELO/no_capturabilidad.py": {"sr_p"},                    # DSR de la cartera contraria (Frente C)
    # calibracion.py A3 pasa A PROPÓSITO el anualizado (`sh_a`) para MEDIR el
    # defecto, etiquetado como tal, junto al por período (`sh_p[i]`).
    "GEMELO/simulador/calibracion.py": {"float(sh_a.max())", "float(sh_p[i])"},
    "GEMELO/simulador/potencia_por_metrica.py": set(),
}
EXCLUIDOS = ("tests/", "venv/", ".claude/", "node_modules/", "frontend/")


def _llamadas_psr_dsr(ruta):
    try:
        arbol = ast.parse(open(ruta, encoding="utf-8").read())
    except SyntaxError:
        return []
    out = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call) and getattr(nodo.func, "attr", "") in ("psr", "dsr"):
            primer = nodo.args[0] if nodo.args else None
            out.append(ast.unparse(primer) if primer is not None else "")
    return out


def test_ningun_llamador_del_repo_pasa_algo_fuera_de_la_lista_blanca():
    ilegales = {}
    for base, _, archivos in os.walk(RAIZ):
        rel_base = os.path.relpath(base, RAIZ).replace(os.sep, "/")
        if any((rel_base + "/").startswith(e) for e in EXCLUIDOS):
            continue
        for a in archivos:
            if not a.endswith(".py"):
                continue
            rel = (rel_base + "/" + a).lstrip("./")
            llamadas = _llamadas_psr_dsr(os.path.join(base, a))
            if not llamadas:
                continue
            permitidas = LISTA_BLANCA.get(rel)
            if permitidas is None or any(x not in permitidas for x in llamadas):
                ilegales[rel] = llamadas
    assert not ilegales, f"llamadores de psr/dsr fuera de la lista blanca: {ilegales}"


def test_los_llamadores_conocidos_existen_y_usan_sr_p():
    for rel in ("backtest/veredicto_51.py", "GEMELO/control_lineal.py"):
        v = _llamadas_psr_dsr(os.path.join(RAIZ, rel))
        assert v and all(a == "sr_p" for a in v), (rel, v)


def test_psr_y_dsr_rechazan_un_sharpe_anualizado():
    """La precondición del contrato: un |Sharpe| por período > 3 no existe
    en datos diarios; delata un anualizado y se rechaza en vez de inflar z."""
    import pytest
    assert inf.psr(0.35, 0.0, 30) < 1.0
    with pytest.raises(inf.ErrorUnidadSharpe):
        inf.psr(5.49, 0.0, 31)                       # el Sharpe anualizado del campeón del WS2b
    with pytest.raises(inf.ErrorUnidadSharpe):
        inf.dsr(5.49, 31, 0.0, 3.0, 9, 0.0641)
