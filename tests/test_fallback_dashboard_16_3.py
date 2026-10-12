"""Corrida 16-3, Bloque E (R9 del dictamen 16-1, acta §102.2): la negativa
declarada del fallback del dashboard llega a `data/snapshot.log` con el mismo
motivo legible que la del job, y el vigía la lee con su parser de siempre.

`app.py` es un script de Streamlit y no se importa en un test: la función
`_anotar_negativa_en_snapshot_log` se extrae de su fuente por AST y se
ejecuta con los mismos nombres que tiene en el módulo (`snapshot_mod`,
`MODELO_VERSION`, `date`). El vigía (`mki_vigia`) no se toca: se le pasa el
log temporal por su `RUTA_SNAPSHOT_LOG`."""
import ast
import os
import sys
from datetime import date, datetime, timezone

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import mki_vigia  # noqa: E402
import snapshot as snapshot_mod  # noqa: E402
from version import MODELO_VERSION  # noqa: E402

RUTA_APP = os.path.join(RAIZ, "app.py")


def _funcion_de_app(nombre: str):
    fuente = open(RUTA_APP, encoding="utf-8").read()
    arbol = ast.parse(fuente)
    nodo = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef) and n.name == nombre)
    codigo = ast.get_source_segment(fuente, nodo)
    espacio = {"snapshot_mod": snapshot_mod, "MODELO_VERSION": MODELO_VERSION, "date": date,
               "datetime": datetime, "os": os}
    exec(compile(codigo, RUTA_APP, "exec"), espacio)
    return espacio[nombre]


@pytest.fixture
def anotar():
    return _funcion_de_app("_anotar_negativa_en_snapshot_log")


RESULTADOS = {
    snapshot_mod.NEGATIVA_FRESCURA: {
        "snapshot": False, "negativa": snapshot_mod.NEGATIVA_FRESCURA,
        "motivo": "hoy FECHA es sesión de XNYS y el último cierre del SOX que sirve la fuente es de AYER: insumo no "
                  "fresco — no se sella (acta §93.8 b)",
        "fecha": "FECHA", "sox_fecha": "AYER", "emision_utc": "2026-10-12T20:03:00+00:00", "descarga": "28/28"},
    snapshot_mod.NEGATIVA_SESION_ABIERTA: {
        "snapshot": False, "negativa": snapshot_mod.NEGATIVA_SESION_ABIERTA,
        "motivo": "la sesión del SOX usada no ha cerrado: sox_fecha FECHA cierra a las 2026-10-12T20:00:00+00:00 y la "
                  "emisión es de las 2026-10-12T17:42:00+00:00 — no se sella (acta §90.1 b)",
        "sox_fecha": "FECHA", "cierre_utc": "2026-10-12T20:00:00+00:00", "emision_utc": "2026-10-12T17:42:00+00:00",
        "descarga": "28/28"},
}


def _con_fecha(resultado: dict, hoy: date) -> dict:
    ayer = hoy.replace(day=hoy.day)  # misma fecha: lo que importa es el texto FECHA → hoy
    out = {k: (v.replace("FECHA", hoy.isoformat()).replace("AYER", "2026-10-09") if isinstance(v, str) else v)
           for k, v in resultado.items()}
    return out


@pytest.mark.parametrize("codigo", sorted(RESULTADOS))
def test_reproduccion_la_negativa_del_fallback_queda_en_snapshot_log_y_el_vigia_la_lee(anotar, tmp_path, monkeypatch, codigo):
    """REPRODUCCIÓN (rojo sobre HEAD por símbolo ausente: app.py no tenía la
    función; la conducta que fija es que, sin ella, el vigía no ve nada)."""
    hoy = date.today()
    log = str(tmp_path / "snapshot.log")
    monkeypatch.setattr(mki_vigia, "RUTA_SNAPSHOT_LOG", log)
    assert mki_vigia._negativa_declarada_en_log(hoy) is None          # sin el log, el vigía no ve negativa
    resultado = _con_fecha(RESULTADOS[codigo], hoy)
    assert anotar(resultado, log, datetime(2026, 10, 12, 21, 3, tzinfo=timezone.utc)) is True
    texto = open(log, encoding="utf-8").read()
    assert "snapshot.py (origen=dashboard" in texto                    # la cabecera que el vigía busca
    assert f"{snapshot_mod.MARCA_NEGATIVA} [{codigo}] fecha={hoy.isoformat()}" in texto
    leida = mki_vigia._negativa_declarada_en_log(hoy)
    assert leida is not None and leida["codigo"] == codigo
    assert leida["texto"] == resultado["motivo"]                        # el MISMO motivo legible que el job
    assert leida["sox_fecha"] == str(resultado["sox_fecha"])


def test_el_vigia_clasifica_la_negativa_del_fallback_como_negativa_y_no_como_falla(anotar, tmp_path, monkeypatch):
    import senales
    hoy = date.today()
    log = str(tmp_path / "snapshot.log")
    monkeypatch.setattr(mki_vigia, "RUTA_SNAPSHOT_LOG", log)
    monkeypatch.setattr(senales, "info_snapshot_hoy", lambda: None)   # sin sello hoy
    ok, detalle = mki_vigia.chequear_snapshot(hoy)
    assert (ok, detalle) == (False, "snapshot: NO se selló hoy")        # sin negativa anotada: falla
    anotar(_con_fecha(RESULTADOS[snapshot_mod.NEGATIVA_FRESCURA], hoy), log, datetime.now(timezone.utc))
    ok, detalle = mki_vigia.chequear_snapshot(hoy)
    assert ok is True and mki_vigia.es_negativa(detalle)
    assert f"[{snapshot_mod.NEGATIVA_FRESCURA}]" in detalle and "insumo no fresco" in detalle


def test_sin_negativa_no_se_escribe_nada(anotar, tmp_path):
    log = str(tmp_path / "snapshot.log")
    assert anotar({"snapshot": True, "predicciones": 8}, log, datetime.now(timezone.utc)) is False
    assert anotar({"snapshot": False, "motivo": "sin datos de mercado"}, log, datetime.now(timezone.utc)) is False
    assert not os.path.exists(log)


def test_una_negativa_de_otro_dia_no_se_lee_como_de_hoy(anotar, tmp_path, monkeypatch):
    """Misma regla que para el job: la línea lleva la fecha del snapshot que
    no se selló y el vigía sólo acepta la de HOY."""
    hoy = date.today()
    log = str(tmp_path / "snapshot.log")
    monkeypatch.setattr(mki_vigia, "RUTA_SNAPSHOT_LOG", log)
    r = dict(RESULTADOS[snapshot_mod.NEGATIVA_FRESCURA], fecha="2026-10-09", sox_fecha="2026-10-08",
             motivo="hoy 2026-10-09 es sesión de XNYS y el último cierre del SOX que sirve la fuente es de 2026-10-08")
    anotar(r, log, datetime.now(timezone.utc))
    assert mki_vigia._negativa_declarada_en_log(hoy) is None


def test_app_captura_el_resultado_del_fallback_y_anota_una_vez_por_sesion():
    """El bloque del fallback guarda el dict que devuelve `ejecutar_snapshot`
    (antes lo descartaba), pregunta por `negativa`, y la anotación va detrás
    de una llave de `st.session_state` (Streamlit re-ejecuta el archivo en
    cada interacción). El vigía no se toca."""
    fuente = open(RUTA_APP, encoding="utf-8").read()
    arbol = ast.parse(fuente)
    asignaciones = [n for n in ast.walk(arbol) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                    and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "ejecutar_snapshot"]
    assert asignaciones, "app.py sigue descartando el resultado de ejecutar_snapshot('dashboard')"
    assert "negativa_anotada" in fuente and "_anotar_negativa_en_snapshot_log(" in fuente
    assert "data\", \"snapshot.log\"" in fuente
    assert not any(ast.dump(n).find("mki_vigia") >= 0 for n in ast.walk(arbol)), "app.py no importa el vigía"
