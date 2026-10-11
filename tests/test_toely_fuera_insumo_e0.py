"""Corrida 16b (4-oct-2026, acta §95.4): TOELY sale del universo del insumo de E0.

La fuente dejó de servir el ADR el 25-sep; desde la sesión del 29-sep cada
noche del sellador quedó `insumo_incompleto` sólo por TOELY y E0 no sumó
ninguna sesión desde la del 24-sep. Nicolás firmó sacarlo del universo del
insumo, sin sustituto y sin retorno, SIN aflojar la regla para los demás:
«insumo completo» sigue exigiendo todos los tickers del universo restante.

Lo que estos tests exigen: (1) un insumo al que le falta SÓLO TOELY es
completo (roja en HEAD: ahí da `insumo_incompleto`); (2) cualquier otro
faltante sigue siendo `insumo_incompleto`, cero tolerados; (3) TOELY con dato
en la fuente no vuelve al universo; (4) la exclusión vive en `reglas.json`
(la huella `reglas_sha256` de cada fila la distingue) y sólo la lee el
sellador: el censo (`universo_operable`) no la ve; (5) sin la clave, el
comportamiento es el anterior, o sea que la exclusión no está escondida en
el código; (6) el resto de las reglas del sellador (ventana horaria, gate de
invariancia) no cambia; (7) las filas selladas antes del cambio siguen con
TOELY y con la huella vieja. Base temporal en cada test: la real no se toca."""
import json
import os
import sqlite3
from datetime import datetime, timezone

import pandas as pd
import pytest

from dinero import cuenta_papel as CP
from dinero import precios
from dinero import sello_dinero as S
from dinero import universo_dinero as U

UTC = timezone.utc
SESION = "2026-09-08"                                  # misma sesión sintética que tests/test_sello_dinero.py
AHORA = datetime(2026, 9, 9, 3, 0, tzinfo=UTC)         # antes de la apertura objetivo (9-sep 13:30Z)
EXCLUIDO = "TOELY"
CLAVE = "exclusiones_insumo_e0"


@pytest.fixture(scope="module")
def base():
    return precios.cargar_congelado()


def _extension(tmp_path, base, sin_dato=(), no_verificable=False):
    """Copia de `_extension_sintetica` de test_sello_dinero.py: una sesión,
    precios = último cierre × 1.01, `sin_dato` deja NaN esos tickers.
    `no_verificable` (corrida 16-2, E0.3) la escribe como `congelar_extension`
    escribe la evidencia de un disparo con timing roto: `.no_verificable.csv`
    y `cupo_canonico: false` en el meta."""
    ult = base.iloc[-1]
    ext = pd.DataFrame({pd.Timestamp(SESION): ult * 1.01}).T
    for t in sin_dato:
        ext.loc[pd.Timestamp(SESION), t] = float("nan")
    ext.index.name = "Date"
    ruta = str(tmp_path / f"ext_{SESION}{'.no_verificable' if no_verificable else ''}.csv")
    ext.to_csv(ruta)
    meta = {"sha256": S._sha256(ruta), "hasta": SESION, "tickers": list(ext.columns),
            "desde": SESION, "extiende_a": {"hasta": "2026-09-04"},
            "disponibilidad": {"exchange": "XNYS", "por_ticker": precios.disponibilidad_por_ticker(ext)}}
    if no_verificable:
        meta["cupo_canonico"] = False
    with open(ruta.replace(".csv", ".meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f)
    return ruta, meta


def _sellar(tmp_path, base, sin_dato=(), ahora=AHORA, no_verificable=False):
    ruta, meta = _extension(tmp_path, base, sin_dato, no_verificable=no_verificable)
    db = str(tmp_path / "s.db")
    return S.sellar(ruta, meta, ahora_utc=ahora, ruta_db=db), db


def _tickers_sellados(db) -> set:
    con = sqlite3.connect(db)
    try:
        return {r[0] for r in con.execute("SELECT DISTINCT ticker FROM sellos_dinero").fetchall()}
    finally:
        con.close()


# ------------------------------------------------------------
# 1. Reproducción: falta sólo TOELY (lo que pasó del 29-sep al 2-oct)
# ------------------------------------------------------------
def test_reproduccion_si_falta_solo_toely_el_insumo_es_completo_y_cuenta(tmp_path, base):
    r, db = _sellar(tmp_path, base, sin_dato=(EXCLUIDO,))
    assert r["insumo_completo"] is True and r["sin_dato"] == []
    assert r["estado"] == S.ESTADO_PENDIENTE and r["cuenta_para_N"] == 1
    assert r["excluidos_universo"] == [EXCLUIDO]        # B3 del auditor 16b: el log de la noche dice por qué son 32
    assert EXCLUIDO not in _tickers_sellados(db)


# ------------------------------------------------------------
# 2. Cero faltantes tolerados: cualquier otro ticker sigue mandando
# ------------------------------------------------------------
@pytest.mark.parametrize("sin_dato", [("AMD",), ("AMD", EXCLUIDO), ("KLAC", "NVDA", EXCLUIDO)])
def test_cualquier_otro_faltante_sigue_siendo_insumo_incompleto(tmp_path, base, sin_dato):
    r, db = _sellar(tmp_path, base, sin_dato=sin_dato)
    esperados = sorted(set(sin_dato) - {EXCLUIDO})
    assert r["insumo_completo"] is False and sorted(r["sin_dato"]) == esperados
    assert r["estado"] == S.ESTADO_INSUMO_INCOMPLETO and r["cuenta_para_N"] == 0
    con = sqlite3.connect(db)
    motivos = dict(con.execute("SELECT ticker, motivo FROM sellos_dinero WHERE ultimo_cierre_ticker != ?",
                               (SESION,)).fetchall())
    con.close()
    assert sorted(motivos) == esperados
    assert all("sin dato en el insumo" in m for m in motivos.values())
    assert EXCLUIDO not in _tickers_sellados(db)        # ni como faltante ni como nada


# ------------------------------------------------------------
# 3. TOELY con dato en la fuente NO vuelve (sin retorno, §95.4)
# ------------------------------------------------------------
def test_toely_presente_en_la_fuente_no_vuelve_al_universo(tmp_path, base):
    assert EXCLUIDO in base.columns                     # el insumo lo sigue trayendo: el congelado tiene la columna
    r, db = _sellar(tmp_path, base)                     # todos con dato, TOELY incluido
    assert r["insumo_completo"] is True and r["cuenta_para_N"] == 1
    sellados = _tickers_sellados(db)
    assert EXCLUIDO not in sellados
    assert sellados == set(CP.universo_operable(base, U.reglas(), hasta=CP.DESDE)) - {EXCLUIDO}


# ------------------------------------------------------------
# 4. La exclusión vive en reglas.json y sólo la lee el sellador
# ------------------------------------------------------------
def test_la_exclusion_vive_en_reglas_y_el_censo_no_la_ve(base):
    cfg = U.reglas()
    assert cfg[CLAVE]["tickers"] == [EXCLUIDO]
    censo = CP.universo_operable(base, cfg, hasta=CP.DESDE)
    assert EXCLUIDO in censo                            # universo_operable.json, m2_periodo, universo_por_presupuesto: intactos
    d = S.decidir(base, "2026-09-04")
    assert EXCLUIDO not in d["operables"] and d["excluidos_universo"] == [EXCLUIDO]
    assert sorted(d["operables"] + [EXCLUIDO]) == censo
    assert all(f["ticker"] != EXCLUIDO for f in d["filas"])


def test_sin_la_clave_en_reglas_el_comportamiento_es_el_anterior(base):
    """La exclusión no está escondida en el código: quitada la clave, TOELY
    vuelve a estar en el universo y un insumo sin él es incompleto."""
    cfg = {k: v for (k, v) in U.reglas().items() if k != CLAVE}
    d = S.decidir(base, "2026-09-04", cfg=cfg)
    assert EXCLUIDO in d["operables"] and d["excluidos_universo"] == []


# ------------------------------------------------------------
# 5. El resto de las reglas del sellador no cambia
# ------------------------------------------------------------
def test_la_ventana_horaria_sigue_mandando_con_toely_fuera(tmp_path, base):
    """ADAPTADO en la corrida 16-2 (camino T, acta §93.7): un disparo con timing
    roto ya no deja fila en `sellos_dinero`; su evidencia nace `.no_verificable`
    y sus filas van a `intentos_no_verificables`. Lo que este test fija no
    cambia: el insumo con sólo TOELY faltante es completo, y la regla maestra
    sigue mandando sobre eso (cuenta_para_N = 0). Con la evidencia de nombre
    canónico y timing roto, E0.3 rechaza sin escribir filas
    (`rechazado_evidencia_canonica`): ésa es la rama que este test NO prueba."""
    tarde = datetime(2026, 9, 9, 14, 0, tzinfo=UTC)    # después de la apertura objetivo (9-sep 13:30Z)
    r, _ = _sellar(tmp_path, base, sin_dato=(EXCLUIDO,), ahora=tarde, no_verificable=True)
    assert r["insumo_completo"] is True                 # el insumo sí está completo...
    assert r["timing_ok"] is False and r["cuenta_para_N"] == 0   # ...pero la regla maestra sigue mandando
    assert r["resultado"] == "intento_no_verificable" and r["excluidos_universo"] == [EXCLUIDO]   # E0.3


def test_el_gate_de_invariancia_sigue_en_pie(base):
    for dia in ("2026-08-20", "2026-06-15"):
        g = S.verificar_invariancia_decision(base, dia, futuros=5)
        assert g["resultado"] == "INVARIANTE" and g["cortes"] == 6


# ------------------------------------------------------------
# 6. Sin efecto retroactivo: la base real, en sólo lectura
# ------------------------------------------------------------
def test_las_filas_selladas_antes_del_cambio_siguen_con_toely_y_con_la_huella_vieja():
    if not os.path.exists(S.RUTA_DB):
        pytest.skip("sin dinero/sello_dinero.db en este árbol (gitignorada)")
    con = sqlite3.connect(f"file:{S.RUTA_DB}?mode=ro", uri=True)
    try:
        n, hasta = con.execute("SELECT COUNT(*), MAX(fecha_insumo) FROM sellos_dinero WHERE ticker=?",
                               (EXCLUIDO,)).fetchone()
        assert n > 0 and hasta < "2026-10-05"            # las 18 sesiones hasta el 2-oct lo llevan; desde el 5-oct no
        huellas = {r[0] for r in con.execute(
            "SELECT DISTINCT reglas_sha256 FROM sellos_dinero WHERE fecha_insumo < '2026-10-05'").fetchall()}
        assert S._sha256(U.RUTA_REGLAS) not in huellas    # la huella nueva distingue las filas de aquí en adelante
        triggers = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='trigger'").fetchall()}
        assert {"sellos_dinero_inmutable_1", "sellos_dinero_inmutable_2"} <= triggers
    finally:
        con.close()
