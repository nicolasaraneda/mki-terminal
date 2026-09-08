# ============================================================
# dinero/cobertura_causal.py — cuánto de `cuenta_papel.py` y de
# `contabilidad.py` está cubierto POR CAUSALIDAD.
#
#   python -m dinero.cobertura_causal [etiqueta]
#
# Bloque 3 de la corrida 11. El traspaso de la corrida 10 dejó escrito que
# «la suite verde no cubre por causalidad ni cuenta_papel.py ni
# contabilidad.py: un verde de pytest hoy no es evidencia de ausencia de
# fuga». Esto lo vuelve un número, con la definición a la vista:
#
#   cobertura por causalidad = líneas ejecutables del módulo que ejecuta
#   al menos un test de INVARIANCIA AL TRUNCADO que PASA, sobre el total de
#   líneas ejecutables del módulo.
#
# Un test de truncado que falla (o está en xfail) ejecuta líneas pero no
# prueba nada de ellas: cuenta como «tocado», no como «cubierto». Se
# reportan las dos cifras para que la diferencia sea visible.
#
# Qué tests cuentan: SOLO los de la lista TESTS_DE_CAUSALIDAD, que son los
# que truncan la entrada y exigen que la salida no cambie. Un test de
# propiedad, de esquema o de aislamiento no dice nada sobre fuga temporal y
# no entra, aunque ejecute el módulo entero.
#
# No usa coverage.py (no está en requirements.txt): las líneas ejecutadas se
# recogen con sys.settrace y las ejecutables con los objetos de código
# compilados, que es lo mismo que hace coverage por debajo.
# ============================================================
from __future__ import annotations

import importlib
import json
import os
import sys
import traceback
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DINERO = os.path.dirname(os.path.abspath(__file__))
MODULOS = ("cuenta_papel", "contabilidad")
SALIDA_JSON = os.path.join(DIR_DINERO, "resultados", "cobertura_causal.json")

# Los tests de invariancia al truncado sobre el riel. Cada entrada es
# (módulo de test, nombre de la función). Se agregan acá cuando se escriben.
TESTS_DE_CAUSALIDAD = (
    ("tests.test_dinero", "test_el_universo_operable_no_puede_depender_del_futuro"),
    ("tests.test_dinero", "test_la_senal_sin_informacion_no_puede_sortearse_del_futuro"),
    ("tests.test_dinero", "test_la_orden_de_un_dia_no_puede_depender_del_cierre_de_ese_dia"),
    ("tests.test_dinero", "test_la_cuenta_en_papel_es_invariante_al_truncado"),
    ("tests.test_dinero", "test_contraprueba_una_fuga_inyectada_rompe_la_invariancia"),
)


def _ruta(modulo: str) -> str:
    return os.path.join(DIR_DINERO, modulo + ".py")


def lineas_ejecutables(ruta: str) -> set:
    """Números de línea con código, según los objetos de código compilados."""
    with open(ruta, encoding="utf-8") as f:
        codigo = compile(f.read(), ruta, "exec")
    lineas = set()
    pila = [codigo]
    while pila:
        co = pila.pop()
        for _, _, ln in co.co_lines():
            if ln is not None:
                lineas.add(ln)
        for k in co.co_consts:
            if hasattr(k, "co_code"):
                pila.append(k)
    # la primera línea de un módulo es su docstring/encabezado: no cuenta
    return {ln for ln in lineas if ln > 1}


def funciones(ruta: str) -> dict:
    """nombre → (línea inicial, línea final) de cada def de primer nivel."""
    import ast
    with open(ruta, encoding="utf-8") as f:
        arbol = ast.parse(f.read())
    out = {}
    for nodo in arbol.body:
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[nodo.name] = (nodo.lineno, nodo.end_lineno)
        elif isinstance(nodo, ast.ClassDef):
            for sub in nodo.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out[f"{nodo.name}.{sub.name}"] = (sub.lineno, sub.end_lineno)
    return out


def _correr_con_traza(fn, rutas: set) -> tuple:
    """Ejecuta `fn` recogiendo las líneas ejecutadas en `rutas`.
    Devuelve (paso: bool, error: str | None, lineas: {ruta: set})."""
    vistas = {r: set() for r in rutas}

    def tracer(frame, evento, arg):
        archivo = frame.f_code.co_filename
        if archivo in vistas:
            if evento == "line":
                vistas[archivo].add(frame.f_lineno)
            return tracer
        return tracer if evento == "call" else None

    sys.settrace(tracer)
    try:
        fn()
        return True, None, vistas
    except Exception as e:  # noqa: BLE001 — se reporta, no se esconde
        return False, f"{type(e).__name__}: {str(e)[:300]}", vistas
    finally:
        sys.settrace(None)


def medir(etiqueta: str = "") -> dict:
    if RAIZ not in sys.path:
        sys.path.insert(0, RAIZ)
    rutas = {m: os.path.abspath(_ruta(m)) for m in MODULOS}
    ejecutables = {m: lineas_ejecutables(r) for m, r in rutas.items()}
    tocadas = {m: set() for m in MODULOS}
    cubiertas = {m: set() for m in MODULOS}
    tests = []
    for mod_test, nombre in TESTS_DE_CAUSALIDAD:
        try:
            mt = importlib.import_module(mod_test)
            fn = getattr(mt, nombre)
        except (ImportError, AttributeError):
            tests.append({"test": f"{mod_test}::{nombre}", "estado": "NO EXISTE"})
            continue
        # el xfail de pytest no aplica acá: se llama la función desnuda
        fn_desnuda = getattr(fn, "__wrapped__", fn)
        paso, error, vistas = _correr_con_traza(fn_desnuda, set(rutas.values()))
        marcado_xfail = any(getattr(m, "name", "") == "xfail"
                            for m in getattr(fn, "pytestmark", []))
        for m, r in rutas.items():
            tocadas[m] |= vistas[r]
            if paso:
                cubiertas[m] |= vistas[r]
        tests.append({"test": f"{mod_test}::{nombre}",
                      "estado": "PASA" if paso else "FALLA",
                      "xfail_declarado": marcado_xfail,
                      "error": error,
                      "lineas_tocadas": {m: len(vistas[r]) for m, r in rutas.items()}})
    por_modulo = {}
    for m in MODULOS:
        ej = ejecutables[m]
        fns = funciones(rutas[m])
        tabla = {}
        for nombre, (a, b) in fns.items():
            cuerpo = {ln for ln in ej if a <= ln <= b}
            if not cuerpo:
                continue
            tabla[nombre] = {
                "lineas": len(cuerpo),
                "tocada_pct": round(100 * len(cuerpo & tocadas[m]) / len(cuerpo), 1),
                "cubierta_pct": round(100 * len(cuerpo & cubiertas[m]) / len(cuerpo), 1),
            }
        por_modulo[m] = {
            "lineas_ejecutables": len(ej),
            "tocadas_por_tests_de_truncado": len(ej & tocadas[m]),
            "cubiertas_por_tests_de_truncado_que_pasan": len(ej & cubiertas[m]),
            "tocada_pct": round(100 * len(ej & tocadas[m]) / len(ej), 1) if ej else None,
            "cobertura_causal_pct": round(100 * len(ej & cubiertas[m]) / len(ej), 1) if ej else None,
            "funciones": tabla,
            "sin_cubrir": sorted(n for n, t in tabla.items() if t["cubierta_pct"] < 100.0),
        }
    return {
        "generado_en_utc": datetime.now(timezone.utc).isoformat(),
        "etiqueta": etiqueta,
        "definicion": ("cobertura por causalidad = líneas ejecutables que ejecuta al menos "
                       "un test de invariancia al truncado QUE PASA / líneas ejecutables. "
                       "'tocada' cuenta también los tests que fallan o están en xfail."),
        "tests": tests,
        "modulos": por_modulo,
    }


def tabla(r: dict) -> str:
    L = [f"cobertura por causalidad — {r['etiqueta'] or 'sin etiqueta'} ({r['generado_en_utc'][:19]}Z)"]
    for t in r["tests"]:
        L.append(f"  {t['estado']:9s} {t['test']}" + (f"  — {t['error']}" if t.get("error") else ""))
    for m, d in r["modulos"].items():
        L.append(f"  {m}.py: {d['lineas_ejecutables']} líneas ejecutables · tocadas "
                 f"{d['tocadas_por_tests_de_truncado']} ({d['tocada_pct']} %) · cubiertas por causalidad "
                 f"{d['cubiertas_por_tests_de_truncado_que_pasan']} (**{d['cobertura_causal_pct']} %**)")
        for n, f in d["funciones"].items():
            L.append(f"      {n:34s} {f['lineas']:4d} líneas · tocada {f['tocada_pct']:5.1f} % · cubierta {f['cubierta_pct']:5.1f} %")
    return "\n".join(L)


def main(argv=None) -> dict:
    argv = sys.argv[1:] if argv is None else argv
    etiqueta = argv[0] if argv else ""
    r = medir(etiqueta)
    os.makedirs(os.path.dirname(SALIDA_JSON), exist_ok=True)
    # se acumulan las mediciones: antes y después tienen que convivir
    historial = []
    if os.path.exists(SALIDA_JSON):
        with open(SALIDA_JSON, encoding="utf-8") as f:
            historial = json.load(f).get("mediciones", [])
    historial.append(r)
    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump({"mediciones": historial}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(tabla(r))
    return r


if __name__ == "__main__":
    main()
