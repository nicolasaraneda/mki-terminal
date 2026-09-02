"""Contrapruebas del clasificador de mutación de `GEMELO/fuente_canonica.py`.

Un clasificador que nunca discrepa confirma, no verifica: cada test inyecta
una mutación conocida y exige que se reporte con su nombre y su cuenta, y
uno exige que un reescalado por dividendo (niveles distintos, retornos
iguales) NO se cuente como mutación de la historia. Sin red, sin bases.
"""
import ast
import os

import numpy as np
import pandas as pd
import pytest

from GEMELO import fuente_canonica as fc

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _panel(n=300, semilla=7):
    rng = np.random.default_rng(semilla)
    idx = pd.bdate_range("2025-01-01", periods=n)
    niveles = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, size=(n, 2)), axis=0))
    return pd.DataFrame(niveles, index=idx, columns=["AAA", "BBB"])


def test_paridad_total_sin_mutacion():
    v = _panel()
    r = fc.clasificar_celdas(v, v.copy(), v.index.max().date().isoformat())
    for t in v.columns:
        assert r[t]["distinta"] == 0 and r[t]["retirada"] == 0
        assert r[t]["no_proporcional"] == 0 and r[t]["aparecida"] == 0
        assert r[t]["paridad"] == len(v)


def test_reescalado_por_dividendo_no_es_mutacion_de_retornos():
    """Niveles distintos en TODAS las celdas, retornos iguales: es lo que hace
    `auto_adjust` cuando aparece un dividendo nuevo. Cuenta como
    `proporcional`, jamás como `no_proporcional`."""
    v = _panel()
    n = v.copy()
    n["AAA"] = n["AAA"] * 0.98765
    r = fc.clasificar_celdas(v, n, v.index.max().date().isoformat())
    assert r["AAA"]["distinta"] == len(v) - 1            # la última fecha no cuenta como historia
    assert r["AAA"]["no_proporcional"] == 0
    assert r["AAA"]["retornos_cambiados"] == 0
    assert r["AAA"]["proporcional"] == len(v) - 2        # ni la última fecha ni el primer retorno (NaN)
    assert r["AAA"]["factor_reescalado"] == pytest.approx(0.98765, rel=1e-9)
    assert r["BBB"]["distinta"] == 0


def test_un_precio_revisado_cambia_dos_retornos_y_se_reporta():
    """Un cierre que cambia mueve el retorno de ese día Y el del siguiente:
    dos celdas `no_proporcional`, con la fecha revisada en la lista."""
    v = _panel()
    n = v.copy()
    d = v.index[150]
    n.loc[d, "BBB"] = n.loc[d, "BBB"] * 1.03
    r = fc.clasificar_celdas(v, n, v.index.max().date().isoformat())
    assert r["BBB"]["distinta"] == 1
    assert r["BBB"]["no_proporcional"] == 1          # una celda de nivel
    assert r["BBB"]["retornos_cambiados"] == 2       # dos retornos: el día y el siguiente
    assert d.date().isoformat() in r["BBB"]["fechas_no_proporcionales"]
    assert r["BBB"]["fechas_retornos_cambiados"][0] == d.date().isoformat()
    assert r["BBB"]["max_abs_dif_retorno"] > 1e-3


def test_barra_retirada_se_reporta_con_su_fecha():
    v = _panel()
    n = v.copy()
    d = v.index[100]
    n.loc[d, "AAA"] = np.nan
    r = fc.clasificar_celdas(v, n, v.index.max().date().isoformat())
    assert r["AAA"]["retirada"] == 1
    assert r["AAA"]["fechas_retiradas"] == [d.date().isoformat()]
    # y una fecha entera que desaparece del índice también es retiro
    n2 = v.drop(index=d)
    r2 = fc.clasificar_celdas(v, n2, v.index.max().date().isoformat())
    assert r2["AAA"]["retirada"] == 1 and r2["BBB"]["retirada"] == 1


def test_el_deslizamiento_de_la_ventana_no_cuenta_como_retiro():
    """`period="8y"` empieza más tarde cuando se baja más tarde: las primeras
    fechas de la caché faltan hoy por construcción, no por retiro."""
    v = _panel()
    n = v.iloc[5:].copy()
    r = fc.clasificar_celdas(v, n, v.index.max().date().isoformat())
    assert r["AAA"]["retirada"] == 0 and r["BBB"]["retirada"] == 0


def test_la_ultima_fecha_parcial_se_separa_de_la_historia():
    """La caché capturó Asia a medio día: la última celda es parcial. Eso se
    reporta aparte y NO como retorno mutado de la historia."""
    v = _panel()
    n = v.copy()
    d = v.index[-1]
    n.loc[d, "AAA"] = n.loc[d, "AAA"] * 1.02
    r = fc.clasificar_celdas(v, n, v.index.max().date().isoformat())
    assert r["AAA"]["no_proporcional"] == 0
    assert r["AAA"]["ultima_fecha_parcial_o_nueva"] == 1
    # y NO cuenta como historia distinta ni fabrica un "factor" (el adversario
    # cazó que la primera versión reportaba la barra viva como dividendo)
    assert r["AAA"]["distinta"] == 0
    assert r["AAA"]["factor_reescalado"] is None


def test_nada_de_la_ruta_de_sellado_importa_fuente_canonica():
    """La dirección que protege el sello: `motor`, `snapshot`, `senales`,
    `alertas`, `mki_vigia` no mencionan este módulo."""
    for nombre in ("motor.py", "snapshot.py", "senales.py", "alertas.py",
                   "mki_vigia.py", "mki_noticias.py", "mki_backup.py"):
        ruta = os.path.join(RAIZ, nombre)
        if not os.path.exists(ruta):
            continue
        arbol = ast.parse(open(ruta, encoding="utf-8").read())
        for nodo in ast.walk(arbol):
            if isinstance(nodo, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in nodo.names] + [getattr(nodo, "module", "") or ""]
                assert not any("fuente_canonica" in m or m.startswith("GEMELO") for m in mods), \
                    f"{nombre} importa {mods}"


def test_las_descargas_del_modulo_no_reescriben_la_cache():
    """Toda llamada a `descargar_cierres` del módulo pasa `usar_cache=False`:
    la caché es un testigo y un testigo que se sobreescribe deja de serlo."""
    fuente = open(fc.__file__, encoding="utf-8").read()
    arbol = ast.parse(fuente)
    llamadas = [n for n in ast.walk(arbol) if isinstance(n, ast.Call)
                and getattr(n.func, "attr", "") == "descargar_cierres"]
    assert llamadas, "el módulo debería descargar por GEMELO.datos.descargar_cierres"
    for ll in llamadas:
        kw = {k.arg: k for k in ll.keywords}
        assert "usar_cache" in kw and getattr(kw["usar_cache"].value, "value", None) is False
