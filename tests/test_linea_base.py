# ============================================================
# Tests de backtest/linea_base.py (Etapa 6.0.0, §9).
#
# Dos cosas distintas se prueban aquí:
#  1. Que la MECÁNICA sea correcta — McNemar, convenciones de empate,
#     baselines por nivel, bloques — con datos sintéticos.
#  2. Que la REPRODUCCIÓN de la §2 siga dando lo mismo — sobre la base
#     real, si existe. Es el guardián de la afirmación "el harness
#     reproduce el pre-registro": si un día deja de hacerlo, se entera.
#
# Nada aquí escribe en ninguna base.
# ============================================================

import os
import sqlite3
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest import linea_base as lb

HAY_BASE = os.path.exists(lb.RUTA_SENALES)
solo_con_base = pytest.mark.skipif(not HAY_BASE, reason="senales.db no está (es gitignored)")


# ------------------------------------------------------------
# 1. McNemar — la variante importa
# ------------------------------------------------------------
def test_mcnemar_reproduce_el_p_del_documento():
    """67 vs 55 → 0.3193 es chi-cuadrado CON corrección de continuidad.
    Sin corrección daría 0.2773: si alguien cambia la variante, la cifra
    del pre-registro deja de reproducir y este test lo dice."""
    assert round(lb.mcnemar(67, 55, correccion=True), 4) == 0.3193
    assert round(lb.mcnemar(67, 55, correccion=False), 4) == 0.2773


def test_mcnemar_es_simetrico_y_trata_el_caso_sin_desacuerdos():
    assert lb.mcnemar(67, 55) == lb.mcnemar(55, 67)
    assert lb.mcnemar(0, 0) == 1.0        # sin desacuerdos no hay evidencia
    assert lb.mcnemar(5, 5) == 1.0        # empate perfecto


def test_mcnemar_detecta_una_diferencia_grande():
    assert lb.mcnemar(90, 10) < 0.001


# ------------------------------------------------------------
# 2. La convención del empate — el hallazgo central
# ------------------------------------------------------------
def _sintetico():
    """4 filas: una al alza, una a la baja, y DOS con gap exactamente 0."""
    return pd.DataFrame([
        {"fecha": "2026-09-01", "ticker": "A", "apertura_estimada_pct": 1.0,
         "gap_pct": 2.0, "acierto_gap": 1, "error_gap_pp": 1.0},
        {"fecha": "2026-09-01", "ticker": "B", "apertura_estimada_pct": -1.0,
         "gap_pct": -2.0, "acierto_gap": 1, "error_gap_pp": 1.0},
        {"fecha": "2026-09-02", "ticker": "A", "apertura_estimada_pct": 0.5,
         "gap_pct": 0.0, "acierto_gap": 1, "error_gap_pp": 0.5},
        {"fecha": "2026-09-02", "ticker": "B", "apertura_estimada_pct": -0.5,
         "gap_pct": 0.0, "acierto_gap": 0, "error_gap_pp": 0.5},
    ])


def test_las_tres_convenciones_dan_baselines_distintas():
    df = _sintetico()
    estricta = lb.aplicar_convencion(df, "estricta")
    verificador = lb.aplicar_convencion(df, "verificador")
    excluir = lb.aplicar_convencion(df, "excluir_cero")

    # gap > 0: solo la fila al alza
    assert estricta["base_acierto"].sum() == 1
    # gap >= 0: la fila al alza MÁS las dos de gap cero
    assert verificador["base_acierto"].sum() == 3
    # las de gap cero se van de ambos lados
    assert len(excluir) == 2 and excluir["base_acierto"].sum() == 1


def test_la_convencion_estricta_es_asimetrica_con_el_verificador():
    """El verificador de producción puntúa al campeón con `>=`
    (senales.py: acierto_gap = 1 si (est>=0) == (gap>=0)). La convención
    `estricta` usa `>` para la baseline: al campeón le da el acierto en un
    gap de cero y a la baseline no. Ese es el sesgo que se reporta."""
    df = _sintetico()
    e = lb.aplicar_convencion(df, "estricta")
    fila_cero_alza = e[(e["gap_pct"] == 0) & (e["apertura_estimada_pct"] > 0)]
    assert fila_cero_alza["acierto_gap"].iloc[0] == 1     # el campeón acierta
    assert fila_cero_alza["base_acierto"].iloc[0] == 0    # la baseline no


def test_convencion_desconocida_revienta():
    with pytest.raises(ValueError):
        lb.aplicar_convencion(_sintetico(), "inventada")


# ------------------------------------------------------------
# 3. Duelo, zona muerta y bloques
# ------------------------------------------------------------
def test_duelo_cuenta_los_desacuerdos_en_el_sentido_correcto():
    df = lb.aplicar_convencion(_sintetico(), "estricta")
    d = lb.duelo(df)
    assert d["n"] == 4
    assert d["modelo_aciertos"] == 3 and d["base_aciertos"] == 1
    # b01 = el modelo acierta donde la baseline falla
    assert d["mcnemar_b01"] == 2 and d["mcnemar_b10"] == 0


def test_duelo_vacio_no_revienta():
    assert lb.duelo(pd.DataFrame(columns=["acierto_gap", "base_acierto"]))["n"] == 0


def test_la_zona_muerta_usa_su_propia_baseline_en_cada_nivel():
    """Comparar cada umbral contra la baseline GLOBAL cambiaría el
    denominador y regalaría ventaja. Cada nivel se mide contra la baseline
    de las filas que sobreviven a ese umbral."""
    df = lb.aplicar_convencion(_sintetico(), "estricta")
    zm = lb.zona_muerta(df, umbrales=(0.0, 0.75))
    global_base = zm[zm["umbral"] == 0.0]["base_pct"].iloc[0]
    filtrado = zm[zm["umbral"] == 0.75]
    # con |pred| >= 0.75 sobreviven solo las dos primeras filas
    assert filtrado["n"].iloc[0] == 2
    assert filtrado["base_pct"].iloc[0] == 50.0 != global_base


def test_los_bloques_parten_de_a_40_y_el_ultimo_queda_corto():
    df = pd.DataFrame({
        "fecha": [f"2026-09-{1 + i // 30:02d}" for i in range(90)],
        "acierto_gap": [1] * 90, "base_acierto": [0] * 90,
    })
    b = lb.por_bloques(df, tam=40)
    assert list(b["n"]) == [40, 40, 10]


def test_duelo_excluyendo_saca_la_ventana():
    df = lb.aplicar_convencion(_sintetico(), "estricta")
    assert lb.duelo_excluyendo(df, "2026-09-02", "2026-09-02")["n"] == 2


# ------------------------------------------------------------
# 4. Solo lectura por construcción
# ------------------------------------------------------------
@solo_con_base
def test_la_conexion_es_de_solo_lectura():
    """backtest/ es de solo lectura por construcción y sigue siéndolo."""
    conn = lb._conexion_ro(lb.RUTA_SENALES)
    try:
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("CREATE TABLE prueba_escritura (x INTEGER)")
    finally:
        conn.close()


@solo_con_base
def test_cargar_no_modifica_la_base():
    antes = os.stat(lb.RUTA_SENALES)
    lb.cargar()
    despues = os.stat(lb.RUTA_SENALES)
    assert (antes.st_size, antes.st_mtime) == (despues.st_size, despues.st_mtime)


def test_el_modulo_no_abre_ninguna_conexion_de_escritura():
    fuente = open(lb.__file__, encoding="utf-8").read()
    assert "sqlite3.connect(" not in fuente   # solo vía datos._conexion_ro
    assert "get_connection" not in fuente     # ese es el camino de escritura


# ------------------------------------------------------------
# 5. La reproducción de la §2 — guardián de la afirmación
# ------------------------------------------------------------
@solo_con_base
def test_la_seccion_2_reproduce_entera_con_la_convencion_del_documento():
    df = lb.aplicar_convencion(lb.cargar(), "estricta")
    contraste = lb.contrastar(df)
    fallan = contraste[contraste["veredicto"] != "reproduce"]
    assert fallan.empty, f"dejaron de reproducir:\n{fallan.to_string(index=False)}"


@solo_con_base
def test_los_limites_de_los_bloques_reproducen_aunque_los_porcentajes_no():
    """Hallazgo registrado: las FECHAS y los n de la §2.2 reproducen; los
    PORCENTAJES por bloque no, bajo ningún orden de filas probado. Este
    test fija el hallazgo para que no se pierda ni se 'arregle' solo."""
    df = lb.aplicar_convencion(lb.cargar(), "estricta")
    cb = lb.contrastar_bloques(df)
    limites = cb[cb["campo"] == "límites"]
    assert (limites["veredicto"] == "reproduce").all()
    porcentajes = cb[cb["campo"] != "límites"]
    assert (porcentajes["veredicto"] == "NO REPRODUCE").any()


@solo_con_base
def test_la_ventaja_del_campeon_cambia_segun_la_convencion():
    """El hallazgo de fondo, fijado: la cifra titular de +5.3 pp depende de
    tratar los 5 gaps de cero de forma asimétrica. Con la convención del
    propio verificador la ventaja es menor."""
    base = lb.cargar()
    estricta = lb.duelo(lb.aplicar_convencion(base, "estricta"))
    verificador = lb.duelo(lb.aplicar_convencion(base, "verificador"))
    assert estricta["ventaja_pp"] == 5.3
    assert verificador["ventaja_pp"] < estricta["ventaja_pp"]
    assert verificador["mcnemar_p"] > estricta["mcnemar_p"]


@solo_con_base
def test_el_campeon_no_pasaria_su_propia_regla_R2():
    """R2 (§6.2) descarta al retador si su ventaja desaparece al excluir la
    ventana 15-23 jul. Al campeón, esa prueba lo deja en ventaja NEGATIVA."""
    df = lb.aplicar_convencion(lb.cargar(), "estricta")
    r2 = lb.duelo_excluyendo(df, *lb.VENTANA_R2)
    assert r2["ventaja_pp"] < 0


@solo_con_base
def test_el_informe_se_compone_en_las_tres_convenciones():
    base = lb.cargar()
    for c in lb.CONVENCIONES:
        texto = lb.componer_informe(base, c)
        assert "Contraste con el pre-registro" in texto
        assert "mode=ro" in texto


# ------------------------------------------------------------
# 6. La línea base OFICIAL congelada en la §2.8
# ------------------------------------------------------------
def test_la_convencion_oficial_es_excluir_cero():
    """§2.8 congeló `excluir_cero`. Si alguien cambia el default, este test
    lo dice: la convención es una decisión congelada, no una preferencia."""
    assert lb.CONVENCION_OFICIAL == "excluir_cero"


@solo_con_base
def test_la_linea_base_oficial_coincide_con_lo_congelado():
    """n=223 · 65.9% · 61.9% · +4.0 pp · 64 vs 55 · p=0.4633 (§2.8)."""
    df = lb.aplicar_convencion(lb.cargar(), lb.CONVENCION_OFICIAL)
    tabla = lb.contrastar_linea_oficial(df)
    mal = tabla[tabla["veredicto"] != "coincide"]
    assert mal.empty, f"la línea oficial se movió:\n{mal.to_string(index=False)}"


@solo_con_base
def test_la_conclusion_de_fondo_vale_en_las_TRES_convenciones():
    """El punto de la §2.1 no depende de la convención elegida: bajo las
    tres, la ventaja del campeón sobre una constante NO es distinguible de
    cero. Si alguna diera p < 0.05, la corrección de la §2.8 habría cambiado
    la conclusión y no solo la cifra."""
    base = lb.cargar()
    for c in lb.CONVENCIONES:
        d = lb.duelo(lb.aplicar_convencion(base, c))
        assert d["mcnemar_p"] > 0.05, c


@solo_con_base
def test_senales_db_conserva_su_scoring_original():
    """La exclusión de los empates vive en la capa de MEDICIÓN. El valor
    sellado `acierto_gap` sigue siendo el del verificador (`>=`), incluido
    en las filas de gap cero: si esto cambiara, se habría reescrito el
    significado de filas ya selladas."""
    df = lb.cargar()
    ceros = df[df["gap_pct"] == 0]
    assert len(ceros) == 5
    con_pred_al_alza = ceros[ceros["apertura_estimada_pct"] >= 0]
    assert (con_pred_al_alza["acierto_gap"] == 1).all()
