"""Corrida 13, bloque 5 — los dos README salen del árbitro por el generador.

Lo que estos tests fijan: que `README.md` (inglés) y `README.es.md` (español)
son byte a byte lo que `scripts/generar_readme.py` produce desde sus
plantillas y `cifras.py`; que un marcador sin fuente rompe la generación;
que la plantilla inglesa usa exactamente los marcadores de la española (más
el contador de E0, que sólo la inglesa publica); que los NÚMEROS de las dos
páginas son el mismo multiconjunto (una traducción que redondea distinto es
una cifra movida); que el vocabulario prohibido no entra; que los enlaces
relativos existen y que cada README enlaza al otro en su primera línea."""
import os
import re
import sys
from collections import Counter

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import generar_readme as G  # noqa: E402

_RE_NUM = re.compile(r"\d+(?:[.,]\d+)*")


def _leer(rel):
    with open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return f.read()


def _plantilla(nombre):
    return _leer(os.path.join("docs", "readme", nombre))


# ------------------------------------------------------------
# 1. El generador reproduce los dos README y revienta con un marcador sin fuente
# ------------------------------------------------------------
def test_los_dos_readme_son_lo_que_el_generador_produce():
    r = G.generar(escribir=False)
    distintos = [d for d, (_, ok) in r.items() if not ok]
    assert not distintos, f"README desincronizado con su plantilla o con el árbitro: {distintos} (correr scripts/generar_readme.py)"


def test_un_marcador_sin_clave_en_el_arbitro_rompe_la_generacion():
    with pytest.raises(G.MarcadorSinFuente, match="no_existe"):
        G.render("n = {{n}}, x = {{no_existe}}")
    assert G.render("n = {{n}}") == f"n = {G.valores()['n']}"


def test_toda_clave_del_arbitro_rinde_texto_no_vacio():
    v = G.valores()
    assert all(isinstance(x, str) and x for x in v.values()), {k: x for k, x in v.items() if not x}


# ------------------------------------------------------------
# 2. Las plantillas: mismos marcadores; la inglesa suma sólo el contador de E0
# ------------------------------------------------------------
def test_la_plantilla_inglesa_usa_los_marcadores_de_la_espanola_mas_el_contador_e0():
    es = set(G.marcadores_de(_plantilla("README.es.tmpl.md")))
    en = set(G.marcadores_de(_plantilla("README.en.tmpl.md")))
    assert not (es - en), f"marcadores del español que la inglesa no publica: {sorted(es - en)}"
    extra = en - es
    assert extra <= {"e0_sesiones_selladas", "e0_cuentan_para_N", "e0_N_objetivo", "e0_ultima_fecha_insumo", "e0_no_cuentan", "corte_readme"}, sorted(extra)


def test_los_doce_bloques_y_los_nueve_en_ingles_vienen_de_marcadores():
    """Los fragmentos que el árbitro vigila tienen que estar en las
    PLANTILLAS con marcadores, no como texto: si estuvieran escritos a mano
    coincidirían hoy y se desincronizarían mañana."""
    import cifras
    c = cifras.sellada()
    v = G.valores()
    es, en = _plantilla("README.es.tmpl.md"), _plantilla("README.en.tmpl.md")
    for archivo, fragmento in cifras.doce_bloques(c) + cifras.bloques_readme_en(c):
        if archivo not in ("README.es.md", "README.md"):
            continue
        plantilla = es if archivo == "README.es.md" else en
        assert fragmento not in plantilla, f"{archivo}: el fragmento está escrito a mano en la plantilla: {fragmento}"
        assert fragmento in G.render(plantilla, v), f"{archivo}: el fragmento no sale al renderizar: {fragmento}"


# ------------------------------------------------------------
# 3. Paridad numérica entre los dos README
# ------------------------------------------------------------
def _sin_seccion_e0(texto):
    """La sección «Execution rail» sólo existe en inglés (contador de E0)."""
    ini = texto.find("## Execution rail")
    if ini < 0:
        return texto
    fin = texto.find("\n## ", ini + 5)
    return texto[:ini] + (texto[fin:] if fin > 0 else "")


def _numeros(texto):
    return Counter(t.replace(",", ".") for t in _RE_NUM.findall(texto))


def test_los_numeros_del_readme_en_ingles_son_los_del_espanol():
    """Una traducción que redondea distinto, omite o agrega un número es una
    cifra movida. Se compara el multiconjunto de tokens numéricos de las dos
    páginas (coma decimal normalizada a punto), fuera de la sección de E0."""
    en = _numeros(_sin_seccion_e0(_leer("README.md")))
    es = _numeros(_leer("README.es.md"))
    solo_en = en - es
    solo_es = es - en
    assert not solo_en and not solo_es, f"sólo en inglés: {dict(solo_en)} · sólo en español: {dict(solo_es)}"


# ------------------------------------------------------------
# 4. Vocabulario, enlaces, contador de E0
# ------------------------------------------------------------
_ESTATUS_EN = ("not distinguishable", "NOT distinguishable", "PROPOSAL", "MEASURED", "REFUTED", "TESTED AND FAILED",
               "no measured", "not a track record", "machinery test", "RETIRED", "no real money")


def test_el_readme_en_ingles_no_usa_el_vocabulario_prohibido():
    texto = _leer("README.md")
    assert not re.search(r"confidence|confianza", texto, re.I), "la palabra prohibida está en README.md"
    assert not re.search(r"\balpha\b", texto, re.I)
    sueltas = []
    lineas = texto.split("\n")
    for i, linea in enumerate(lineas, 1):
        # el estatus tiene que estar en la misma frase o a ±2 líneas (el TL;DR va en líneas de ~70 caracteres)
        ventana = " ".join(lineas[max(0, i - 3):i + 2]).lower()
        if re.search(r"\b(opportunit(y|ies)|edge|returns)\b", linea, re.I) and not any(s.lower() in ventana for s in _ESTATUS_EN):
            sueltas.append((i, linea.strip()[:100]))
    assert not sueltas, "«edge/opportunity/returns» sin estatus al lado:\n" + "\n".join(f"  {i}: {l}" for i, l in sueltas)


def test_cada_readme_enlaza_al_otro_en_su_primera_linea():
    assert "README.es.md" in _leer("README.md").split("\n", 1)[0]
    assert "README.md" in _leer("README.es.md").split("\n", 1)[0]


def test_los_enlaces_relativos_de_los_dos_readme_existen():
    rotos = []
    for rel in ("README.md", "README.es.md"):
        for destino in re.findall(r"\]\(([^)\s#]+)(?:#[^)]*)?\)", _leer(rel)):
            if destino.startswith(("http://", "https://", "mailto:")):
                continue
            if not os.path.exists(os.path.join(RAIZ, destino)):
                rotos.append((rel, destino))
    assert not rotos, f"enlaces relativos rotos: {rotos}"


def test_el_contador_de_e0_del_readme_es_el_de_la_copia_versionada():
    e0 = G.contador_e0()
    v = G.valores()
    assert v["e0_cuentan_para_N"] == str(e0["cuentan_para_N"]) and v["e0_sesiones_selladas"] == str(e0["sesiones_selladas"])
    assert v["e0_N_objetivo"] == "40"
    texto = _leer("README.md")
    assert re.search(rf"\*\*{e0['cuentan_para_N']}\*\*\s+count\s+towards\s+N\s*=\s*40", texto), "el contador de E0 del README no es el de la copia versionada"
    assert e0["cuentan_para_N"] <= e0["sesiones_selladas"]
    assert len(e0["no_cuentan"]) == e0["sesiones_selladas"] - e0["cuentan_para_N"]
    for fecha in e0["no_cuentan"]:
        assert fecha in texto
