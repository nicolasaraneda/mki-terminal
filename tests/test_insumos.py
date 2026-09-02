"""Contrapruebas del arnés de la copia congelada de insumos
(`GEMELO/INSUMOS/insumos.py`). Sin red, sin bases, sin tocar `data/`.

Lo que fijan: el hash es reproducible y sólo depende del contenido; la copia
es aditiva (nunca reescribe); el contraste nombra una barra retirada, un
retorno cambiado y un reescalado por dividendo con su nombre; la
intermitencia (presente, ausente, presente) se lee en vez de inferirse; el
módulo no importa nada de la ruta de sellado y nada de la ruta de sellado
lo importa; y el costo en disco se MIDE, no se estima.
"""
import ast
import os

import numpy as np
import pandas as pd
import pytest

from GEMELO.INSUMOS import insumos as ins

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _frames(n=750, series=32, semilla=3, quitar=None, escalar=None, mover=None):
    rng = np.random.default_rng(semilla)
    idx = pd.bdate_range("2023-09-01", periods=n)
    niveles = 100 * np.exp(np.cumsum(rng.normal(0, 0.012, size=(n, series)), axis=0))
    panel = pd.DataFrame(niveles, index=idx, columns=[f"S{i:02d}" for i in range(series)])
    if quitar:
        for s, d in quitar:
            panel.loc[panel.index[d], s] = np.nan
    if escalar:
        for s, f in escalar:
            panel[s] = panel[s] * f
    if mover:
        for s, d, f in mover:
            panel.loc[panel.index[d], s] = panel.loc[panel.index[d], s] * f
    ohlc = pd.DataFrame({"Open": panel["S00"].to_numpy() * 0.99, "Close": panel["S00"].to_numpy()},
                        index=idx)
    return {"cierres": panel, "S00": ohlc}


def test_el_hash_es_reproducible_y_solo_depende_del_contenido(tmp_path):
    a = ins.congelar(_frames(), "2026-09-01", str(tmp_path / "a"))
    b = ins.congelar(_frames(), "2026-09-02", str(tmp_path / "b"))
    assert a["sha256"] == b["sha256"]
    c = ins.congelar(_frames(mover=[("S05", 100, 1.001)]), "2026-09-03", str(tmp_path / "c"))
    assert c["sha256"] != a["sha256"]
    panel, h = ins.leer("2026-09-01", str(tmp_path / "a"))
    assert h == a["sha256"] and panel.shape == (750, 32)


def test_la_copia_es_aditiva_y_no_reescribe(tmp_path):
    ins.congelar(_frames(), "2026-09-01", str(tmp_path))
    with pytest.raises(ins.YaCongelado):
        ins.congelar(_frames(mover=[("S01", 10, 2.0)]), "2026-09-01", str(tmp_path))


def test_el_contraste_nombra_cada_clase_de_mutacion(tmp_path):
    d = str(tmp_path)
    ins.congelar(_frames(), "2026-09-01", d)
    ins.congelar(_frames(quitar=[("S03", 700)],            # una barra retirada
                         escalar=[("S07", 0.987)],         # un dividendo
                         mover=[("S11", 500, 1.02)]),      # un precio revisado
                 "2026-09-02", d)
    r = ins.contrastar("2026-09-01", "2026-09-02", d)
    assert r["series"]["S03"]["veredicto"] == "BARRA_RETIRADA"
    assert r["series"]["S07"]["veredicto"] == "PARIDAD_REESCALADA"
    assert r["series"]["S11"]["veredicto"] == "RETORNO_CAMBIADO"
    assert r["series"]["S00"]["veredicto"] == "PARIDAD"
    assert r["conteo"]["PARIDAD"] == 29
    assert r["sha256_a"] != r["sha256_b"]


def test_una_barra_que_va_y_vuelve_se_lee_como_intermitente(tmp_path):
    d = str(tmp_path)
    ins.congelar(_frames(), "2026-08-13", d)
    ins.congelar(_frames(quitar=[("S09", 400)]), "2026-08-14", d)
    ins.congelar(_frames(), "2026-08-17", d)
    ins.congelar(_frames(quitar=[("S09", 400)]), "2026-08-19", d)
    ins.congelar(_frames(), "2026-08-21", d)
    inter = ins.intermitencia(["2026-08-13", "2026-08-14", "2026-08-17", "2026-08-19", "2026-08-21"], d)
    assert len(inter) == 1
    assert inter[0]["serie"] == "S09"
    assert inter[0]["ausente_en"] == ["2026-08-14", "2026-08-19"]
    # y sin el patrón no hay hallazgo
    assert ins.intermitencia(["2026-08-13", "2026-08-17", "2026-08-21"], d) == []


def test_el_costo_en_disco_se_mide(tmp_path):
    """750 barras × 32 series (3 años del panel de producción): la cifra del
    expediente §5.5 (~60 KB/día, ~15 MB/año) era una estimación; acá se mide."""
    r = ins.congelar(_frames(), "2026-09-01", str(tmp_path))
    assert r["filas"] == 750 * 32 + 750 * 2
    assert r["bytes"] < 300_000, r["bytes"]
    # por año de sellos, a ~250 sellos: debe caber en decenas de MB
    assert r["bytes"] * 250 < 60_000_000


def _imports(ruta):
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    mods = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            mods += [a.name for a in nodo.names]
        elif isinstance(nodo, ast.ImportFrom):
            mods.append(nodo.module or "")
    return mods


def test_el_modulo_no_importa_la_ruta_de_sellado_ni_descarga():
    mods = _imports(ins.__file__)
    for prohibido in ("motor", "snapshot", "senales", "alertas", "yfinance", "sqlite3"):
        assert not any(m == prohibido or m.startswith(prohibido + ".") for m in mods), mods


def test_nada_de_la_ruta_de_sellado_importa_insumos():
    for nombre in ("motor.py", "snapshot.py", "senales.py", "alertas.py",
                   "mki_vigia.py", "mki_noticias.py", "mki_backup.py"):
        ruta = os.path.join(RAIZ, nombre)
        if os.path.exists(ruta):
            assert not any("INSUMOS" in m or "insumos" in m for m in _imports(ruta)), nombre


def test_ningun_timer_ni_el_mki_lo_invocan():
    for carpeta in ("systemd", "launchd"):
        d = os.path.join(RAIZ, carpeta)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            texto = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read()
            assert "insumos" not in texto.lower(), f"{carpeta}/{f} menciona insumos"
    assert "insumos" not in open(os.path.join(RAIZ, "mki"), encoding="utf-8").read().lower()
