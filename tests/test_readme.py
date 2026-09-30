"""Corrida 13, bloque 5 — los dos README salen del árbitro por el generador.

Lo que estos tests fijan: que `README.md` (inglés) y `README.es.md` (español)
son byte a byte lo que `scripts/generar_readme.py` produce desde sus
plantillas y `cifras.py`; que un marcador sin fuente rompe la generación;
que la plantilla inglesa usa exactamente los marcadores de la española (más
el N objetivo de E0, que sólo la inglesa publica); que los NÚMEROS de las dos
páginas son el mismo multiconjunto (una traducción que redondea distinto es
una cifra movida); que el vocabulario prohibido no entra; que los enlaces
relativos existen y que cada README enlaza al otro en su primera línea.

Corrida 15 (29-sep-2026), bloque 2. Tres firmas cambian lo que se fija acá:
el README deja de llevar el contador vivo de E0 (acta §90.3); los badges
`tests` y `plataforma` son valores congelados con su fecha a la vista (acta
§90.4); y el N de intentos del DSR y el «N× la muestra» de la ventana larga
salen de marcadores (acta §88.5 i y iii)."""
import builtins
import datetime
import json
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
# 2. Las plantillas: mismos marcadores; la inglesa suma sólo el N objetivo de E0
# ------------------------------------------------------------
def test_la_plantilla_inglesa_usa_los_marcadores_de_la_espanola_mas_el_n_objetivo_de_e0():
    """Desde el acta §90.3 el único marcador de E0 que queda es la constante
    firmada `e0_N_objetivo`; los cuatro del contador se retiraron.
    `corte_readme` sigue permitido como estaba (no lo usa ninguna plantilla
    hoy): esta corrida no aprieta lo que no se firmó."""
    es = set(G.marcadores_de(_plantilla("README.es.tmpl.md")))
    en = set(G.marcadores_de(_plantilla("README.en.tmpl.md")))
    assert not (es - en), f"marcadores del español que la inglesa no publica: {sorted(es - en)}"
    extra = en - es
    assert extra <= {"e0_N_objetivo", "corte_readme"}, sorted(extra)


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
    """La sección «Execution rail» sólo existe en inglés (tarjeta §65: no hay
    nada en español con que compararla, y escribirla es contenido nuevo que
    ninguna acta firmó)."""
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
# 4. Vocabulario y enlaces
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


# ------------------------------------------------------------
# 5. E0 sin contador vivo (acta §90.3, firma de la tarjeta §65, opción b)
# ------------------------------------------------------------
_RUTA_CSV_DINERO = os.path.join(RAIZ, "data", "backups", "sello_dinero.csv")
_CONTADOR_RETIRADO = {"e0_sesiones_selladas", "e0_cuentan_para_N", "e0_ultima_fecha_insumo", "e0_no_cuentan"}


def _seccion_e0(texto):
    ini = texto.find("## Execution rail")
    assert ini >= 0, "README.md perdió la sección «Execution rail»"
    fin = texto.find("\n## ", ini + 5)
    return texto[ini:fin] if fin > 0 else texto[ini:]


def test_el_readme_no_lleva_contador_vivo_de_e0_y_remite_a_la_copia_versionada():
    """Reemplaza a `test_el_contador_de_e0_del_readme_es_el_de_la_copia_versionada`,
    RETIRADO por el acta §90.3. Aquel test exigía que README.md publicara el
    conteo de sesiones selladas de `data/backups/sello_dinero.csv`; el backup
    mueve ese CSV cada noche y nada regenera el README, así que la página se
    desincronizaba sola y la suite se ponía roja sola (dos rojos al abrir y
    al cerrar la corrida 14). Razón de Nicolás al firmar la opción (b): «para
    evitar riesgos innecesarios, evitamos rojos o posibles errores de codigo
    nuevo». Lo que se fija ahora es lo contrario: que el contador NO esté."""
    # (a) ninguna plantilla usa marcadores de E0, salvo la constante firmada
    for nombre in ("README.es.tmpl.md", "README.en.tmpl.md"):
        de_e0 = {m for m in G.marcadores_de(_plantilla(nombre)) if m.startswith("e0_")}
        assert de_e0 <= {"e0_N_objetivo"}, f"{nombre}: marcadores de contador de E0: {sorted(de_e0)}"
    # (b) la página no lleva el patrón del contador
    texto = _leer("README.md")
    assert not re.search(r"\*\*\d+\*\*\s+count\s+towards\s+N", texto), "README.md volvió a llevar un contador de E0"
    assert not re.search(r"Sealed\s+prospective\s+sessions\s+so\s+far", texto)
    # (c) remite a la copia versionada, y la copia existe
    assert "](data/backups/sello_dinero.csv)" in _seccion_e0(texto)
    assert os.path.exists(_RUTA_CSV_DINERO)
    # la constante firmada sigue saliendo del sellador
    assert G.valores()["e0_N_objetivo"] == "40"
    assert re.search(r"counts\s+towards\s+N\s*=\s*40\b", _seccion_e0(texto))


def test_el_generador_no_abre_el_csv_del_riel_de_dinero(monkeypatch):
    """(d) del acta §90.3: si el generador no lee el CSV, el README no puede
    volver a depender de lo que el sellador escriba esta noche. Se espía
    `open` y además se anota, por si algún `except` se traga la excepción."""
    abiertos = []
    real = builtins.open

    def espia(ruta, *a, **k):
        if "sello_dinero.csv" in str(ruta):
            abiertos.append(str(ruta))
            raise AssertionError(f"el generador abrió {ruta}")
        return real(ruta, *a, **k)

    monkeypatch.setattr(builtins, "open", espia)
    v = G.valores()
    G.generar(escribir=False, v=v)
    assert not abiertos, abiertos
    assert not (_CONTADOR_RETIRADO & set(v)), sorted(_CONTADOR_RETIRADO & set(v))
    assert [k for k in v if k.startswith("e0_")] == ["e0_N_objetivo"]
    assert not hasattr(G, "contador_e0") and not hasattr(G, "RUTA_CSV_DINERO")


def test_la_fecha_de_inicio_de_e0_es_la_de_la_primera_fila_sellada():
    """«since AAAA-MM-DD» es una afirmación publicada: se contrasta con la
    copia versionada. Es estable porque una fila sellada jamás se reescribe;
    el test (no el generador) es el que abre el CSV."""
    import csv
    with open(_RUTA_CSV_DINERO, encoding="utf-8") as f:
        primera = min(fila["fecha_insumo"] for fila in csv.DictReader(f))
    m = re.search(r"\*\*E0 in progress\*\* \(since (\d{4}-\d{2}-\d{2})\)", _leer("README.md"))
    assert m, "la viñeta de E0 no declara desde cuándo"
    assert m.group(1) == primera


# ------------------------------------------------------------
# 6. Badges congelados con fecha a la vista (acta §90.4, opción b)
#
# A propósito NINGÚN test exige que el N del badge sea el conteo vivo de la
# suite ni que la versión sea la de `version.py`: son valores congelados, y
# un test así se pondría rojo con cada test nuevo, que es lo que el acta
# quiso evitar. Lo que se fija es que el badge diga lo que dice el JSON y
# que lleve la fecha en que se leyó.
# ------------------------------------------------------------
def _badges_json():
    with open(os.path.join(RAIZ, "docs", "readme", "badges_congelados.json"), encoding="utf-8") as f:
        return json.load(f)


def _linea_badge(texto, nombre):
    lineas = [l for l in texto.split("\n") if l.startswith(f"![{nombre}](https://img.shields.io/badge/")]
    assert len(lineas) == 1, f"se esperaba un badge «{nombre}», hay {len(lineas)}"
    return lineas[0]


def test_el_json_de_los_badges_tiene_fecha_iso_valida_y_declara_su_fuente():
    b = _badges_json()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", b["leido_el"]), b["leido_el"]
    datetime.date.fromisoformat(b["leido_el"])          # revienta si no es una fecha del calendario
    assert isinstance(b["tests_recolectados"], int) and not isinstance(b["tests_recolectados"], bool)
    assert b["tests_recolectados"] > 0
    assert re.fullmatch(r"\d+\.\d+\.\d+", b["plataforma_version"]), b["plataforma_version"]
    assert b["comando_tests"] == "pytest tests/ --collect-only -q"
    assert b["fuente_plataforma"] == "version.py: PLATAFORMA_VERSION"
    assert "§90.4" in b["nota"] and "CONGELADOS" in b["nota"]


def test_los_dos_readme_llevan_en_los_badges_los_valores_congelados_y_su_fecha():
    b = _badges_json()
    fecha_url = b["leido_el"].replace("-", "--")
    assert G.valores()["badge_leido_el_url"] == fecha_url
    assert fecha_url.replace("--", "-") == b["leido_el"] and "-" not in fecha_url.replace("--", "")
    tests = (f"![tests](https://img.shields.io/badge/tests-{b['tests_recolectados']}"
             f"%20recolectados%20al%20{fecha_url}-2ea44f?style=flat-square)")
    plataforma = (f"![plataforma](https://img.shields.io/badge/plataforma-{b['plataforma_version']}"
                  f"%20al%20{fecha_url}-22d3ee?style=flat-square)")
    for rel in ("README.md", "README.es.md"):
        texto = _leer(rel)
        assert _linea_badge(texto, "tests") == tests, rel
        assert _linea_badge(texto, "plataforma") == plataforma, rel


def test_los_literales_viejos_ya_no_estan_en_los_badges():
    """Acta §88.5 (ii): `tests-650` con «passing» y `plataforma-5.0.3` eran
    literales vencidos, iguales en las dos páginas. «passing» no vuelve: el
    número es de recolección y cuenta también los saltados y los xfail."""
    for rel in ("README.md", "README.es.md",
                os.path.join("docs", "readme", "README.en.tmpl.md"),
                os.path.join("docs", "readme", "README.es.tmpl.md")):
        texto = _leer(rel)
        tests, plataforma = _linea_badge(texto, "tests"), _linea_badge(texto, "plataforma")
        assert not re.search(r"tests-650(?!\d)", tests), rel
        assert "passing" not in tests, rel
        assert not re.search(r"plataforma-5\.0\.3(?!\d)", plataforma), rel


def test_un_json_de_badges_mal_formado_rompe_la_generacion(tmp_path):
    bueno = _badges_json()
    for clave, malo in (("leido_el", "2026-13-40"), ("leido_el", "30-09-2026"), ("tests_recolectados", "932"),
                        ("tests_recolectados", True), ("plataforma_version", "5.1")):
        ruta = tmp_path / f"badges_{clave}.json"
        ruta.write_text(json.dumps({**bueno, clave: malo}), encoding="utf-8")
        with pytest.raises(G.FuenteIlegible, match=clave):
            G.badges_congelados(str(ruta))


# ------------------------------------------------------------
# 7. Las erratas del acta §88.5 que salen de marcadores: (i) y (iii)
# ------------------------------------------------------------
def test_el_n_de_intentos_del_readme_es_el_de_veredicto_51():
    """El generador lee `backtest/veredicto_51.py` como texto; acá se
    contrasta con el módulo importado, que es lo que la máquina usa."""
    from backtest import veredicto_51 as V
    v = G.valores()
    assert v["n_intentos_previo"] == str(V.N_INTENTOS_PREVIO)
    assert v["n_intentos_51"] == str(V.N_INTENTOS_51) == str(V.N_INTENTOS_PREVIO + V.N_INTENTOS_NUEVOS)
    frase = re.compile(rf"(?<!\d){V.N_INTENTOS_PREVIO}\s+\(`backtest/veredicto_51\.py: N_INTENTOS_PREVIO`;\s+{V.N_INTENTOS_51}\s")
    for rel in ("README.md", "README.es.md"):
        assert frase.search(_leer(rel)), f"{rel}: el N de intentos publicado no es el de backtest/veredicto_51.py"
    for nombre in ("README.en.tmpl.md", "README.es.tmpl.md"):
        plantilla = _plantilla(nombre)
        assert "{{n_intentos_previo}}" in plantilla and "{{n_intentos_51}}" in plantilla, nombre
        assert not re.search(r"(?<![\d.,])(352|358)(?![\d.,])", plantilla), f"{nombre}: el N vencido sigue escrito a mano"


def test_el_generador_revienta_si_veredicto_51_no_trae_los_literales(tmp_path):
    sin_previo = tmp_path / "sin_previo.py"
    sin_previo.write_text("N_INTENTOS_NUEVOS = 6\nN_INTENTOS_51 = N_INTENTOS_PREVIO + N_INTENTOS_NUEVOS\n", encoding="utf-8")
    with pytest.raises(G.FuenteIlegible, match="N_INTENTOS_PREVIO"):
        G.n_intentos_dsr(str(sin_previo))
    no_literal = tmp_path / "no_literal.py"
    no_literal.write_text("N_INTENTOS_PREVIO = len(REGISTRO)\nN_INTENTOS_NUEVOS = 6\n"
                          "N_INTENTOS_51 = N_INTENTOS_PREVIO + N_INTENTOS_NUEVOS\n", encoding="utf-8")
    with pytest.raises(G.FuenteIlegible, match="N_INTENTOS_PREVIO"):
        G.n_intentos_dsr(str(no_literal))
    otra_suma = tmp_path / "otra_suma.py"
    otra_suma.write_text("N_INTENTOS_PREVIO = 354\nN_INTENTOS_NUEVOS = 6\nN_INTENTOS_51 = 400\n", encoding="utf-8")
    with pytest.raises(G.FuenteIlegible, match="N_INTENTOS_51"):
        G.n_intentos_dsr(str(otra_suma))
    bien = tmp_path / "bien.py"
    bien.write_text("N_INTENTOS_PREVIO = 10   # comentario\nN_INTENTOS_NUEVOS = 2\n"
                    "N_INTENTOS_51 = N_INTENTOS_PREVIO + N_INTENTOS_NUEVOS      # 12\n", encoding="utf-8")
    assert G.n_intentos_dsr(str(bien)) == {"previo": 10, "con_los_del_51": 12}


def test_las_veces_de_la_ventana_larga_son_el_cociente_de_los_dos_n_del_arbitro():
    """Acta §88.5 (iii): el literal del título era el cociente contra el n de
    la rama sin deduplicar (derogada por D1). Ahora sale de los dos n del
    árbitro, con el formato entero que tenía. No se fija el número: si el
    corte del README se mueve con firma, el cociente se mueve con él."""
    import cifras
    veces = f"{cifras.larga().n / cifras.sellada()['n']:.0f}"
    v = G.valores()
    assert v["larga_veces"] == veces
    # El curador de la corrida 15 exigió el denominador a la vista: el título
    # lleva los dos n del árbitro entre paréntesis, en los dos idiomas.
    assert f"### Long — reconstructed, {veces}× the sealed sample ({v['larga_n']} / {v['n']})" in _leer("README.md")
    assert f"### Larga — reconstruida, {veces}× la muestra sellada ({v['larga_n']} / {v['n']})" in _leer("README.es.md")
    for nombre in ("README.en.tmpl.md", "README.es.tmpl.md"):
        plantilla = _plantilla(nombre)
        assert "{{larga_veces}}×" in plantilla, nombre
        assert not re.search(r"\d\s?[×x] (the sealed sample|la muestra sellada)", plantilla), f"{nombre}: el cociente está escrito a mano"
