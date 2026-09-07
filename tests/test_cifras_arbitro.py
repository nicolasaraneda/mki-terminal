"""Reglas de la casa ejecutables (octava corrida, Frente G; novena, 1a).

1. Cada uno de los doce bloques que dependen de n aparece TEXTUALMENTE en
   su archivo con la cifra que el árbitro (`cifras.py`) computa hoy desde
   `senales.db` en `mode=ro` al instante pinchado.
2. Si n cambia en el árbitro, los doce fragmentos cambian: no se puede
   mover uno sin mover los otros once.
3. Si la CONVENCIÓN cambia (regla de deduplicación firmada ↔ rama
   derogada), los doce fragmentos cambian, y los de la rama derogada ya no
   están en ningún archivo (3-sep-2026, D1: el test del Frente G no cubría
   el cambio de convención; ahora lo cubre).
4. Ninguna cifra retirada (`GEMELO/cifras_retiradas.md`) reaparece en un
   documento publicado sin marca de retiro.
"""
import os

import pytest

import cifras

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def sellada():
    return cifras.sellada()


def test_el_arbitro_computa_la_ventana_sellada_publicada(sellada):
    """El README publica, desde el 3-sep-2026 (D1), n = 238, +9.7 pp con IC95
    de clúster de día [-7.2, +26.6] y McNemar de filas p = 0.0455 al instante
    pinchado `cifras.CORTE_README` (28-ago), bajo la regla de deduplicación
    firmada. El árbitro tiene que reproducirlo desde la base."""
    assert sellada["dedup"] is True and cifras.DEDUP_PUBLICADO is True
    assert sellada["n"] == 238 and sellada["dias"] == 34
    assert sellada["ventaja_pp"] == 9.7
    assert sellada["mcnemar_p"] == 0.0455 and sellada["mcnemar_p_exacta"] == 0.0451
    assert sellada["ventaja_ic_dia"] == [-7.2, 26.6]
    assert sellada["ventaja_ic_dia"][0] < 0 < sellada["ventaja_ic_dia"][1], "el IC de día contiene el cero"
    assert sellada["p_permutacion_dia"] > 0.05
    assert sellada["mae_modelo_pp"] == pytest.approx(2.52, abs=0.005)
    assert sellada["cobertura_80_pct"] == pytest.approx(92.9, abs=0.05)
    assert sellada["ratio_ancho"] == pytest.approx(2.19, abs=0.005)
    assert sellada["ratio_ancho_ic_dia"][0] <= 2.19 <= sellada["ratio_ancho_ic_dia"][1]


def test_todo_estimador_del_arbitro_lleva_intervalo(sellada):
    """Ningún estimador puntual sin intervalo computado (regla de la casa)."""
    pares = [("modelo_pct", "modelo_wilson"), ("base_pct", "base_wilson"),
             ("ventaja_pp", "ventaja_ic_dia"), ("ratio_ancho", "ratio_ancho_ic_dia"),
             ("retorno_pct", "retorno_wilson")]
    for punto, ic in pares:
        assert sellada[punto] is not None and sellada[ic] is not None, (punto, ic)
        assert sellada[ic][0] <= sellada[punto] <= sellada[ic][1], (punto, sellada[punto], sellada[ic])


def test_los_doce_bloques_estan_en_sus_archivos(sellada):
    faltan = []
    for archivo, fragmento in cifras.doce_bloques(sellada):
        texto = open(os.path.join(RAIZ, archivo), encoding="utf-8").read()
        if fragmento not in texto:
            faltan.append((archivo, fragmento))
    assert not faltan, "bloques que no coinciden con el árbitro:\n" + "\n".join(f"  {a}: {f}" for a, f in faltan)


def test_si_n_cambia_cambian_los_doce_bloques(sellada):
    otro = dict(sellada)
    otro["n"] = sellada["n"] + 1
    otro["modelo_aciertos"] += 1
    otro["base_aciertos"] += 1
    otro["modelo_pct"] = round(100 * otro["modelo_aciertos"] / otro["n"], 1)
    otro["base_pct"] = round(100 * otro["base_aciertos"] / otro["n"], 1)
    otro["ventaja_pp"] = round(otro["modelo_pct"] - otro["base_pct"], 1)
    otro["ventaja_ic_dia"] = [sellada["ventaja_ic_dia"][0] - 0.1, sellada["ventaja_ic_dia"][1] + 0.1]
    otro["mcnemar_p"] = round(sellada["mcnemar_p"] + 0.0001, 4)
    otro["mae_modelo_pp"] = round(sellada["mae_modelo_pp"] + 0.01, 2)
    otro["cobertura_80_pct"] = round(sellada["cobertura_80_pct"] + 0.1, 1)
    otro["ratio_ancho"] = round(sellada["ratio_ancho"] + 0.01, 2)
    a = cifras.doce_bloques(sellada)
    b = cifras.doce_bloques(otro)
    assert len(a) == 12 and len(b) == 12
    iguales = [x for x, y in zip(a, b) if x == y]
    assert not iguales, f"bloques que NO se mueven con n: {iguales}"


def test_si_la_convencion_cambia_cambian_los_doce_bloques_y_la_derogada_no_esta(sellada):
    """D1 (3-sep-2026): la rama sin deduplicar está derogada. Sus doce
    fragmentos tienen que diferir de los vigentes uno por uno, y ninguno
    puede seguir en su archivo."""
    derogada = cifras.sellada(dedup=False)
    assert derogada["n"] != sellada["n"], "la convención no cambia n: el test no distingue nada"
    a = cifras.doce_bloques(sellada)
    b = cifras.doce_bloques(derogada)
    iguales = [x for x, y in zip(a, b) if x == y]
    assert not iguales, f"bloques que NO se mueven con la convención: {iguales}"
    sobreviven = []
    for archivo, fragmento in b:
        texto = open(os.path.join(RAIZ, archivo), encoding="utf-8").read()
        for i, linea in enumerate(texto.split("\n")):
            if fragmento in linea and not cifras._tiene_marca_de_retiro(texto.split("\n"), i):
                sobreviven.append((archivo, i + 1, fragmento))
    assert not sobreviven, "fragmentos de la convención derogada sin marca de retiro:\n" + \
        "\n".join(f"  {a}:{l}: {f}" for a, l, f in sobreviven)


def test_ninguna_cifra_retirada_vuelve_a_un_documento_publicado():
    retiradas = cifras.cifras_retiradas()
    assert len(retiradas) >= 14, "el registro de cifras retiradas está vacío o no se lee"
    hallazgos = {}
    for doc in cifras.DOCUMENTOS_PUBLICADOS:
        texto = open(os.path.join(RAIZ, doc), encoding="utf-8").read()
        h = cifras.reintroducciones(texto, retiradas)
        if h:
            hallazgos[doc] = h
    assert not hallazgos, f"cifras retiradas reintroducidas: {hallazgos}"


def test_contraprueba_el_detector_caza_una_reintroduccion():
    texto = "La ventana larga tiene 8,6% de contaminación por revisión de precios.\n"
    assert cifras.reintroducciones(texto)
    texto_ok = "Errata: el 8,6% de contaminación era un artefacto del join; corregido a 0,00%.\n"
    assert not cifras.reintroducciones(texto_ok)
    texto_d1 = "Sobre la ventana sellada (n=248) la ventaja es +6.5 pp con p = 0.1849.\n"
    assert cifras.reintroducciones(texto_d1), "la rama derogada por D1 no está registrada"


# ============================================================
# La heurística de la marca de retiro, endurecida el 7-sep-2026
# (exigencia 3 del `guardian-constitucion`, corrida 10).
#
# La versión anterior exentaba cualquier línea con una palabra ambigua a ±2
# líneas. En la corrida 10 una «corregida» que hablaba de OTRO tema exentó
# una reintroducción real del 91,4 % en un documento generado, y el falso
# verde lo cazó un lector y no la máquina. Estos dos tests son la
# contraprueba: uno demuestra que el instrumento sabe ponerse rojo, el otro
# que la exención legítima sigue funcionando.
# ============================================================
def test_una_marca_ambigua_que_habla_de_otra_cosa_ya_no_exenta():
    """El falso verde del 7-sep, reproducido: la palabra «corregida» dos
    líneas más abajo hablaba de supervivencia, no de la cifra."""
    import cifras
    retiradas = [{"patron": r"91[,.]4\s?%", "contexto": "x", "fecha": "y",
                  "acta": "z", "reemplazo": "w"}]
    texto = ("midió la contaminación en el riel de medición (198 filas,\n"
             "91,4 % de coincidencia, máximo 31,2 pp) y va en dirección\n"
             "optimista.\n"
             "- **Supervivencia, NO corregida.** Los 36 tickers son los que\n"
             "  existen hoy.\n")
    hallazgos = cifras.reintroducciones(texto, retiradas)
    assert hallazgos, (
        "la marca ambigua «corregida», que habla de otro tema, no puede "
        "exentar una reintroducción: ése fue el falso verde del 7-sep-2026")
    assert hallazgos[0][0] == 2


def test_una_marca_fuerte_sigue_exentando_la_historia():
    """El README cuenta la historia de sus propias cifras retiradas y eso
    no puede ponerse rojo."""
    import cifras
    retiradas = [{"patron": r"91[,.]4\s?%", "contexto": "x", "fecha": "y",
                  "acta": "z", "reemplazo": "w"}]
    texto = ("La cifra está RETIRADA desde el 1-sep-2026.\n"
             "Decía 91,4 % de coincidencia sobre 198 filas.\n"
             "Con la clave correcta da 100 % sobre 214.\n")
    assert cifras.reintroducciones(texto, retiradas) == []
    # Y una marca ambigua SÍ exenta cuando el contexto nombra la cifra dos
    # veces, o sea cuando la marca habla de ella y no de otra cosa.
    texto2 = ("El 91,4 % era el número anterior.\n"
              "Hoy el 91,4 % no se usa.\n")
    assert cifras.reintroducciones(texto2, retiradas) == []
