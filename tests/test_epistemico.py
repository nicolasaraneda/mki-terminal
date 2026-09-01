"""
tests/test_epistemico.py — cinco noches de errores, convertidas en tests.

Cada corrida autónoma del 31-ago/1-sep-2026 produjo una clase de error
metodológico propia, y ninguna dejó nada que impidiera repetirla. Las
retractaciones viven en prosa (`DECISIONES.md` §45 a §57, las bitácoras de
`GEMELO/resultados/`), y la prosa se olvida. Esto es lo mismo, ejecutable.

Los siete tests y el error histórico que cada uno previene:

  1. Vara de validación que comparte proveedor con lo validado.
  2. Retractación que vive sólo en un `.md` mientras el ejecutable que
     produjo la cifra la sigue imprimiendo.
  3. Intervalo publicado que contiene el nulo, presentado sin decirlo.
  4. Estimador puntual publicado como hallazgo, sin intervalo.
  5. Filas duplicadas en la ventana sellada.
  6. Cita por número de línea a `DECISIONES.md` que ya no apunta ahí.
  7. Cifra del README que no coincide con la del módulo árbitro, sin
     declarar con qué método se computó.
  8. Prueba de rendimiento que pasa en verde sobre un diseño roto, por no
     verificar corrección en la misma corrida.

**Nada de acá escribe** en ninguna base ni en la ruta de sellado. Los tests
1, 2, 3, 4, 6 y 8 son análisis estático sobre archivos; el 5 abre
`senales.db` en `mode=ro` por el helper del proyecto; el 7 lee el README y
llama a dos funciones puras. El 8 tiene además una parte ejecutable que
corre `micro/rtl/verificar_hueco.py` en un subproceso cuando hay toolchain
(simulación de Icarus sobre vectores ya congelados; su único efecto sobre el
árbol son artefactos en `micro/rtl/sim/`, que está en `.gitignore`) y se
salta cuando no lo hay. No se importa `motor.py`, no se toca la ruta de
sellado, no se abre ninguna base para escritura.

**Sobre los heurísticos.** Los tests 3 y 4 detectan patrones en prosa, y
eso no se puede hacer sin heurístico. La consigna que siguen, y que está
declarada en el docstring de cada uno: **preferir falsos negativos a
falsos positivos**. Un test epistémico que grita por todo se termina
desactivando, y entonces no previene nada. Cada detector se implementa
como una función pura sobre `(nombre, texto)` para que exista, al lado del
test real, una **contraprueba** que le inyecta el error histórico
sintético y verifica que el detector efectivamente lo caza. Un test que no
puede fallar no es un test: la corrida anterior tuvo cuatro tautológicos
que hubo que reescribir.
"""
from __future__ import annotations

import glob
import math
import os
import re
import sys

import pytest

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)
_ARBITRO = os.path.join(_RAIZ, ".claude", "skills", "estadistica-evaluacion",
                        "scripts")
if _ARBITRO not in sys.path:
    sys.path.insert(0, _ARBITRO)


# ==========================================================================
# Utilidades de alcance
# ==========================================================================
# El alcance está acotado a propósito. `DECISIONES.md` entero es histórico
# —cinco mil líneas de actas que describen correctamente el estado del día
# en que se escribieron— y barrerlo con los detectores 3 y 4 daría miles de
# falsos positivos sobre cifras ya retractadas en su sitio. Se barre entero
# sólo para el test 6, que es el único que no juzga contenido.
_PATRONES_RESULTADOS = (
    "GEMELO/resultados/*.md",
    "GEMELO/SECUENCIAL/*.md",
    "GEMELO/MICRO/*.md",
    "backtest/resultados/**/*.md",
)
_PATRONES_EJECUTABLES = (
    "GEMELO/**/*.py",
    "backtest/**/*.py",
)


def _leer(ruta: str) -> str:
    with open(ruta, encoding="utf-8") as fh:
        return fh.read()


def _expandir(patrones) -> list[str]:
    rutas: set[str] = set()
    for patron in patrones:
        rutas.update(glob.glob(os.path.join(_RAIZ, patron), recursive=True))
    return sorted(r for r in rutas if "__pycache__" not in r)


def _documentos_de_resultados() -> list[tuple[str, str]]:
    """Los `.md` de resultados. NO incluye `DECISIONES.md` (ver arriba)."""
    return [(os.path.relpath(r, _RAIZ), _leer(r))
            for r in _expandir(_PATRONES_RESULTADOS)]


def _ejecutables() -> list[tuple[str, str]]:
    """Los `.py` que producen esos resultados."""
    return [(os.path.relpath(r, _RAIZ), _leer(r))
            for r in _expandir(_PATRONES_EJECUTABLES)]


def _ventana(lineas: list[str], i: int, radio: int) -> str:
    return "\n".join(lineas[max(0, i - radio):i + radio + 1])


def _es_fila_de_tabla(linea: str) -> bool:
    """Las filas de tabla markdown se saltan en los detectores de prosa.

    No es una concesión: las tablas de resultados de este proyecto salen de
    scripts, ya traen su columna de intervalo y su columna de
    significancia, y no son "una afirmación presentada como hallazgo". El
    error histórico siempre estuvo en el texto que interpreta la tabla.
    """
    return linea.lstrip().startswith("|")


def _informe(hallazgos: list[tuple[str, int, str]]) -> str:
    return "\n".join(f"  {a}:{n}  {t.strip()[:140]}" for a, n, t in hallazgos)


# ==========================================================================
# 1. La vara que no era independiente
# ==========================================================================
_RE_CLAIM_INDEPENDENCIA = re.compile(
    r"vara independiente|validaci[oó]n independiente|verificaci[oó]n independiente|"
    r"medici[oó]n independiente|otra familia de m[eé]todo|validaci[oó]n externa",
    re.I,
)
# El único proveedor de precios que hay hoy en el repo. Toda columna
# sellada de precio sale de acá, así que una vara construida sobre él es,
# por definición, el mismo proveedor y el mismo campo recorridos de nuevo.
_RE_PROVEEDOR_UNICO = re.compile(r"yfinance|yf\.download|yahoo", re.I)
_RE_COLUMNA_SELLADA = re.compile(
    r"retorno_real_pct|gap_pct|columna sellada|base sellada|precio sellado|"
    r"E\|r\||senales\.db", re.I,
)
_MARCAS_DE_NEGACION = (
    "no es", "no lo es", "no lo era", "no era", "no valida", "no existe",
    "retract", "retirad", "no se sostiene", "reproducción", "reproduccion",
    "no independiente", "falso", "no una vara", "no una medición",
)


def detectar_varas_no_independientes(archivos) -> list[tuple[str, int, str]]:
    """Afirmaciones de independencia sobre una vara del único proveedor.

    Regla: si un texto afirma tener una vara independiente / de otra
    familia de método, y en su vecindad aparecen a la vez el proveedor
    único de precios y una columna sellada, la afirmación es falsa salvo
    que el propio texto la esté negando o retractando.
    """
    hallazgos = []
    for nombre, texto in archivos:
        lineas = texto.split("\n")
        for i, linea in enumerate(lineas):
            if not _RE_CLAIM_INDEPENDENCIA.search(linea):
                continue
            ctx = _ventana(lineas, i, 10)
            if not (_RE_PROVEEDOR_UNICO.search(ctx)
                    and _RE_COLUMNA_SELLADA.search(ctx)):
                continue
            if any(m in ctx.lower() for m in _MARCAS_DE_NEGACION):
                continue
            hallazgos.append((nombre, i + 1, linea))
    return hallazgos


def test_ninguna_vara_de_validacion_comparte_proveedor_con_lo_validado():
    """31-ago-2026, cuarta corrida autónoma.

    `GEMELO/SECUENCIAL/DISEÑO.md` §A3.1.a afirmaba haber validado E|r| —el
    retorno absoluto medio que fija el MDE— contra una "vara
    independiente", "de otra familia de método": el precio crudo de Yahoo,
    recomputado. Era el MISMO proveedor, el MISMO campo y la MISMA fórmula
    recorrida de nuevo. Emparejada fila a fila contra la columna sellada,
    la desviación media es 0,0001 pp sobre 234 filas: una reproducción, no
    una medición. Retractado el mismo día en §A3.1.a y registrado en
    `DECISIONES.md` §52, que convierte esto en regla de la casa: una
    verificación que usa el mismo mecanismo que produjo la cifra no es una
    verificación, y si la vara no existe se dice, en vez de fabricar una
    que se le parezca.

    Hoy no existe en el repo ninguna fuente de precios de otra familia con
    la que contrastar `retorno_real_pct`. Mientras eso siga así, toda
    afirmación de independencia sobre una vara de Yahoo es falsa.
    """
    hallazgos = detectar_varas_no_independientes(
        _documentos_de_resultados() + _ejecutables())
    assert not hallazgos, (
        "Se afirma independencia sobre una vara del único proveedor de precios "
        "del repo (Yahoo), contra una columna sellada que sale del mismo "
        "proveedor. Ver DECISIONES.md §52:\n" + _informe(hallazgos))


def test_contraprueba_el_detector_de_varas_caza_el_texto_historico():
    """La contraprueba del test anterior: el detector tiene que fallar.

    Se le da la redacción original del 31-ago-2026 —la que se retractó— y
    se verifica que la caza. Sin esto, el test de arriba podría estar en
    verde por no detectar nada nunca.
    """
    original = (
        "El parámetro que manda es E|r|, medido sobre las filas selladas.\n"
        "La tercera fila es la vara independiente: el precio crudo de Yahoo,\n"
        "recomputado desde cero, confirma la deduplicada y descarta la\n"
        "contaminada. La columna sellada retorno_real_pct queda validada.\n"
    )
    assert detectar_varas_no_independientes([("sintetico.md", original)])
    # Y con la retractación puesta, deja de cazarla: el detector distingue
    # afirmar de retractar, no sólo la presencia de las palabras.
    corregido = original.replace(
        "es la vara independiente", "NO es una vara independiente")
    assert not detectar_varas_no_independientes([("sintetico.md", corregido)])


# ==========================================================================
# 2. La retractación que vive sólo en prosa
# ==========================================================================
_RE_RETRACTACION = re.compile(r"RETRACTAD|RETRACTACI|retractad|retracta\b", re.I)
# Un token de afirmación retractada: o una frase citada entre comillas
# angulares (así se cita en este repo lo que se retracta), o un factor
# numérico con al menos dos decimales. Los factores de un decimal se
# descartan a propósito: "4×", "3.6×" aparecen en contextos ajenos y
# generaban ruido. Falso negativo antes que falso positivo.
_RE_TOKEN_RETRACTADO = re.compile(r"«([^»\n]{8,90})»|(\d+[.,]\d{2,})\s*×")
_MARCAS_DE_RETRACTACION = (
    "retract", "retirad", "no es", "no lo es", "no valida", "no existe",
    "no se sostiene", "ya no", "falso", "no lo era", "decía", "decia",
)


def _tokens_retractados(documentos) -> set[str]:
    """Lo que quedó retractado, leído de los propios `.md` de resultados."""
    tokens: set[str] = set()
    for _, texto in documentos:
        lineas = texto.split("\n")
        for i, linea in enumerate(lineas):
            if not _RE_RETRACTACION.search(linea):
                continue
            bloque = "\n".join(lineas[i:i + 40])
            for m in _RE_TOKEN_RETRACTADO.finditer(bloque):
                tok = (m.group(1) or (m.group(2) + "×")).strip()
                if "\n" in tok:
                    continue
                tokens.add(tok)
    return tokens


def _variantes(token: str) -> set[str]:
    """El repo escribe decimales con punto y con coma según el documento."""
    return {token, token.replace(",", "."), token.replace(".", ",")}


def detectar_retractaciones_solo_en_prosa(documentos, ejecutables):
    """Afirmaciones retractadas en un `.md` que un `.py` sigue imprimiendo.

    Si el token retractado aparece en el código sin ninguna marca de
    retractación en su vecindad (±12 líneas), el ejecutable sigue
    afirmando lo que el documento ya retiró.
    """
    tokens = _tokens_retractados(documentos)
    hallazgos = []
    for nombre, texto in ejecutables:
        lineas = texto.split("\n")
        for i, linea in enumerate(lineas):
            for token in tokens:
                if not any(v in linea for v in _variantes(token)):
                    continue
                ctx = _ventana(lineas, i, 12).lower()
                if any(m in ctx for m in _MARCAS_DE_RETRACTACION):
                    continue
                hallazgos.append((nombre, i + 1, f"[{token}] {linea}"))
                break
    return hallazgos


def test_ninguna_retractacion_queda_solo_en_prosa_mientras_el_codigo_la_imprime():
    """31-ago-2026, cuarta corrida autónoma.

    `GEMELO/SECUENCIAL/DISEÑO.md` retractó dos afirmaciones —la "vara
    independiente" de §A3.1.a y el factor 3,64× de §A3.1.b— mientras
    `GEMELO/SECUENCIAL/mde_desde_v6.py`, el script del que salen esas
    mismas cifras, las seguía imprimiendo tal cual por stdout. Lo cazó el
    `guardian-constitucion`. Un documento retractado y un ejecutable que
    contradice al documento dejan al repo afirmando las dos cosas a la vez,
    y gana la que alguien corra.

    Registrado en `DECISIONES.md` §56 (puntos 2 y 3) y §52.

    Heurístico: los tokens se extraen de los bloques de retractación de los
    propios `.md` (frases entre «» y factores con dos decimales o más), y
    se exige una marca de retractación a ±12 líneas del sitio donde el
    código los menciona. No caza una retractación parafraseada sin ninguno
    de esos tokens — falso negativo asumido.
    """
    hallazgos = detectar_retractaciones_solo_en_prosa(
        _documentos_de_resultados(), _ejecutables())
    assert not hallazgos, (
        "Un ejecutable sigue imprimiendo una afirmación que un .md ya "
        "retractó, sin decirlo en el sitio:\n" + _informe(hallazgos))


def test_contraprueba_el_detector_caza_el_script_que_sigue_imprimiendo():
    """Contraprueba: se reconstruye el estado del 31-ago a las 23:30 UTC.

    Un `.md` con la retractación puesta y un `.py` que imprime la cifra
    retractada sin marca alguna. El detector tiene que cazarlo; y con la
    marca puesta, tiene que dejar de cazarlo.
    """
    doc = ("**Razón 2 — RETRACTADA el mismo día. No se sostiene.**\n"
           "> Decía que los datos «refutan la simetría de magnitudes por\n"
           "> 3.64×». Con intervalos la razón 1.33× incluye 1.0.\n")
    malo = ('def main():\n'
            '    print("los datos refutan la simetria por 3.64x")\n'
            '    print("razon de magnitudes 1.33× contra los errores")\n')
    assert detectar_retractaciones_solo_en_prosa(
        [("d.md", doc)], [("s.py", malo)])
    bueno = malo.replace("def main():",
                         'def main():\n    # RETRACTADO: no se sostiene.')
    assert not detectar_retractaciones_solo_en_prosa(
        [("d.md", doc)], [("s.py", bueno)])


# ==========================================================================
# 3. El punto sin intervalo, con el nulo adentro
# ==========================================================================
_RE_INTERVALO = re.compile(
    r"\[\s*([+-−]?\s*\d+(?:[.,]\d+)?)\s*(?:%|\s*pp)?\s*,"
    r"\s*([+-−]?\s*\d+(?:[.,]\d+)?)\s*(?:%|\s*pp)?\s*\]")
_MARCAS_DE_NULO_ADENTRO = (
    "incluye", "no está refutad", "no esta refutad", "no se distingue",
    "indistinguible", "no alcanza", "retract", "no significativ",
    "compatible con cero", "cubre", "pendiente", "no distinguible",
    "sin distinguirse", "al filo", "no excluye", "roza", "no permite",
    "no basta", "abarca", "consistente", "no concluyente", "no-concluyente",
    "atraviesa", "contiene el", "cruza", "no descarta",
    # Agregados el 1-sep-2026, quinta corrida: el detector marcó como
    # hallazgo la línea de `bifurcaciones.md` que dice "no separa al
    # campeón de una constante" — que ES un reconocimiento explícito de
    # que el intervalo contiene el nulo, sólo que con palabras que no
    # estaban en esta lista. Falso positivo por vocabulario corto, no por
    # lógica: el detector es correcto y le faltaba idioma.
    "no separa", "no distingue", "no separa al", "de 34 pp de ancho",
    "no puede resolver", "no resuelve",
)


def _a_float(s: str):
    s = s.replace("−", "-").replace(",", ".").replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return None


def _nulo_de_la_linea(linea: str) -> float:
    """Qué valor es "no hay efecto" para lo que esa línea publica.

    Razones y factores tienen nulo 1,0; tasas de acierto con Wilson lo
    tienen en 50%; diferencias, ventajas y errores, en 0.
    """
    low = linea.lower()
    if "×" in low or "razón" in low or "razon" in low or "factor" in low:
        return 1.0
    if "wilson" in low or "acierto" in low:
        return 50.0
    return 0.0


def detectar_intervalos_con_el_nulo_sin_declarar(documentos):
    """Intervalos publicados en prosa que contienen el nulo sin decirlo."""
    hallazgos = []
    for nombre, texto in documentos:
        lineas = texto.split("\n")
        for i, linea in enumerate(lineas):
            if _es_fila_de_tabla(linea):
                continue
            for m in _RE_INTERVALO.finditer(linea):
                lo, hi = _a_float(m.group(1)), _a_float(m.group(2))
                if lo is None or hi is None or lo >= hi:
                    continue
                nulo = _nulo_de_la_linea(linea)
                if not lo < nulo < hi:
                    continue
                ctx = " ".join(
                    x for x in lineas[max(0, i - 5):i + 6]
                    if not _es_fila_de_tabla(x)).lower()
                if any(t in ctx for t in _MARCAS_DE_NULO_ADENTRO):
                    continue
                hallazgos.append((nombre, i + 1, linea))
    return hallazgos


def test_ningun_intervalo_publicado_contiene_el_nulo_sin_decirlo():
    """31-ago-2026, cuarta corrida autónoma.

    `GEMELO/SECUENCIAL/DISEÑO.md` §A3.1.b publicó "los datos refutan la
    simetría de magnitudes por 3,64×" y usó eso para rechazar un modelo. Al
    ponerle los intervalos que no le había puesto: la razón de magnitudes
    1,33× tiene IC95 [0,89, 2,16], que **incluye 1,0** — la simetría no
    estaba refutada; `E[r|baja]` = −1,059% tiene IC95 [−3,334, +1,059], que
    incluye cero; y el 3,64× no tiene intervalo finito, porque su
    denominador (2q−1) no se distingue de cero. Un estimador puntual
    indistinguible del nulo, publicado como hallazgo, en la sección escrita
    para prevenir exactamente eso. Retractado el mismo día.

    Registrado en `DECISIONES.md` §56, punto 2.

    Heurístico, y acá importa la letra chica: se juzga la PROSA, no las
    tablas —las tablas de este proyecto salen de scripts y ya traen su
    columna de significancia—, el nulo se infiere de la línea (1,0 para
    razones y factores, 50% para tasas con Wilson, 0 en el resto), y basta
    con que el texto reconozca el hecho a ±5 líneas ("incluye cero", "al
    filo", "no se distingue"...) para que el detector calle. Prefiere el
    falso negativo: si la línea no dice explícitamente qué se está
    midiendo, asume nulo 0, que es el caso más benigno.
    """
    hallazgos = detectar_intervalos_con_el_nulo_sin_declarar(
        _documentos_de_resultados())
    assert not hallazgos, (
        "Intervalo publicado que contiene el valor nulo sin que el texto lo "
        "reconozca. Ver DECISIONES.md §56 punto 2:\n" + _informe(hallazgos))


def test_contraprueba_el_detector_caza_el_nulo_adentro_no_declarado():
    """Contraprueba: la razón 1,33× con su IC [0,89, 2,16] presentada como
    hallazgo. El detector tiene que cazarla, y tiene que callarse en cuanto
    el texto admite que el intervalo incluye 1,0.
    """
    malo = ("La razón de magnitudes es 1.33×, IC95 [0.89, 2.16], y con eso\n"
            "los datos refutan la simetría por un factor de 3.64×.\n")
    assert detectar_intervalos_con_el_nulo_sin_declarar([("s.md", malo)])
    bueno = malo.replace("y con eso", "que incluye 1.0, así que")
    assert not detectar_intervalos_con_el_nulo_sin_declarar([("s.md", bueno)])


# ==========================================================================
# 4. El estimador puntual sin intervalo
# ==========================================================================
_VERBOS_DE_HALLAZGO = (
    "mde", "refuta", "refutan", "demuestra", "establece", "prueba que",
    "ventaja mínima", "ventaja minima", "efecto mínimo", "efecto minimo",
    "descarta", "confirma",
)
_RE_PUNTO_EN_NEGRITA = re.compile(
    r"\*\*\s*[+-−~]?\s*\d+(?:[.,]\d+)?\s*(?:pp|%|×)\s*\*\*")
_RE_MDE_CON_VALOR = re.compile(
    r"MDE[^.\n]{0,40}?(?:=|de|es|:|propuesto|firmad\w*)\s*\*{0,2}\s*~?\s*"
    r"\d+(?:[.,]\d+)?\s*pp", re.I)
# "Con el MDE de 7 pp la fecha es X" proyecta un escenario; "MDE = 7 pp"
# lo afirma. La preposición condicional al frente es la diferencia.
_RE_MDE_CONDICIONAL = re.compile(
    r"(?:^|[\s(*—–-])(?:con|si|bajo|para|suponiendo|asumiendo)\s+"
    r"(?:el\s+|un\s+)?MDE", re.I)
_RE_HAY_INTERVALO = re.compile(
    r"IC\s*95|IC95|Wilson|intervalo|bootstrap|\[\s*[+-−]?\s*\d|±")
# Un MDE citado como escenario, como sensibilidad o ya retirado no es un
# estimador publicado: es una hipótesis o una retractación. "propuesto" NO
# está en esta lista a propósito: "PROPUESTO PARA FIRMA: MDE = 7 pp" es
# exactamente la frase del caso histórico, y exentarla vaciaría el test.
_MARCAS_DE_ESCENARIO = (
    "retirad", "retractad", "sin firmar", "si mde", "hipót",
    "hipot", "sensibilidad", "no hay número", "no hay numero", "no firmad",
)


def detectar_puntos_sin_intervalo(documentos):
    """Estimadores publicados como hallazgo, sin intervalo a la vista.

    Dos reglas, las dos sobre prosa:
      (a) una magnitud en negrita con unidad (pp, %, ×) en una línea que
          además contiene un verbo de hallazgo;
      (b) un MDE con valor, que es la familia exacta del caso histórico.
    En los dos casos se exige una marca de intervalo a ±4 líneas.
    """
    hallazgos = []
    for nombre, texto in documentos:
        lineas = texto.split("\n")
        for i, linea in enumerate(lineas):
            if _es_fila_de_tabla(linea):
                continue
            low = linea.lower()
            regla_a = (_RE_PUNTO_EN_NEGRITA.search(linea)
                       and any(v in low for v in _VERBOS_DE_HALLAZGO))
            regla_b = bool(_RE_MDE_CON_VALOR.search(linea)
                           and not _RE_MDE_CONDICIONAL.search(linea))
            if not (regla_a or regla_b):
                continue
            ctx = _ventana(lineas, i, 4)
            if _RE_HAY_INTERVALO.search(ctx):
                continue
            if regla_b and any(m in ctx.lower() for m in _MARCAS_DE_ESCENARIO):
                continue
            hallazgos.append((nombre, i + 1, linea))
    return hallazgos


def test_ningun_estimador_se_publica_como_hallazgo_sin_su_intervalo():
    """31-ago/1-sep-2026, cuarta corrida autónoma.

    El MDE en la escala del endpoint quedó escrito como "~7,96 o ~8,96 pp",
    **cableado como texto en cinco artefactos, sin que lo computara ningún
    script y sin intervalo** — en el acta de la corrida cuya lección era
    exactamente que un estimador puntual sin intervalo no se publica. Lo
    cazó el `guardian-constitucion` en su segundo dictamen. Hoy lo computa
    `GEMELO/SECUENCIAL/mde_desde_v6.py` con el bootstrap de bloques del
    módulo árbitro, y lo que reemplaza al número es un rango: 8,96 pp con
    IC95 [6,67, 11,32].

    Registrado en `DECISIONES.md` §56 ("Y hay una corrección sobre esta
    misma acta, del mismo día"). La regla escrita está en
    `.claude/rules/backtest.md`: "Ningún estimador puntual sin intervalo".

    Heurístico: sólo dispara sobre prosa (no tablas) cuando hay una
    magnitud en negrita con unidad junto a un verbo de hallazgo, o cuando
    hay un MDE con valor. Un MDE citado como escenario ("si MDE = 7 pp"),
    como sensibilidad, o ya retirado, queda exento: es hipótesis, no cifra
    publicada. Prefiere el falso negativo: una cifra sin negritas y sin
    verbo de hallazgo no se caza.
    """
    hallazgos = detectar_puntos_sin_intervalo(_documentos_de_resultados())
    assert not hallazgos, (
        "Estimador puntual publicado como hallazgo sin intervalo. Ver "
        ".claude/rules/backtest.md y DECISIONES.md §56:\n" + _informe(hallazgos))


def test_contraprueba_el_detector_caza_el_mde_cableado_sin_intervalo():
    """Contraprueba: el MDE del 31-ago, tal como estaba escrito."""
    malo = ("PROPUESTO PARA FIRMA. En la escala del endpoint el número es\n"
            "otro: el MDE es 8.96 pp a 25 pb por lado.\n")
    assert detectar_puntos_sin_intervalo([("s.md", malo)])
    bueno = malo.replace("8.96 pp a 25 pb",
                         "8.96 pp, IC95 [6.67, 11.32], a 25 pb")
    assert not detectar_puntos_sin_intervalo([("s.md", bueno)])


# ==========================================================================
# 5. Las filas duplicadas de la ventana sellada
# ==========================================================================
def _filas_selladas_excluir_cero():
    """La ventana sellada canónica, en SOLO LECTURA.

    Va por `backtest.datos._conexion_ro`, que es el helper que el proyecto
    ya usa para abrir `senales.db` en `mode=ro`. Este test no escribe.
    """
    import pandas as pd
    from backtest.datos import RUTA_SENALES, _conexion_ro

    if not os.path.exists(RUTA_SENALES):
        pytest.skip("senales.db no está en esta máquina")
    conn = _conexion_ro(RUTA_SENALES)
    try:
        df = pd.read_sql_query(
            """
            SELECT v.fecha_senal, v.ticker, s.sesion_objetivo, v.gap_pct
              FROM verificacion_apertura v
              LEFT JOIN senales_ticker s
                     ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
             WHERE v.legacy = 0 AND v.modelo_version = '4.6.0'
               AND v.gap_pct IS NOT NULL
            """, conn)
    finally:
        conn.close()
    return df[df["gap_pct"] != 0].copy()


@pytest.mark.xfail(
    reason="DECISIONES.md §56 punto 1: los 30 duplicados existen y la regla "
           "de deduplicación NO está congelada. keep='first' da +6,64 pp "
           "(p=0,1847) y keep='last' da +9,96 pp (p=0,0323): elegir cuál "
           "conservar mueve el veredicto, así que es decisión de Nicolás y "
           "está en cola_decisiones.md. Este test queda ROJO a propósito "
           "hasta que esa decisión se tome; ablandarlo para que pase sería "
           "borrar el hallazgo. Si pasa a XPASS, el problema se resolvió y "
           "hay que sacar este marcador.")
def test_ninguna_prediccion_sellada_comparte_sesion_objetivo_con_otra():
    """31-ago-2026, cuarta corrida autónoma.

    30 de las 256 filas de la ventana sellada (11,7%) apuntan a la MISMA
    `sesion_objetivo` que otra fila: quince pares sobre cinco sesiones
    (31-jul, 5-ago, 12-ago, 18-ago), dos fechas de emisión consecutivas
    cuyo objetivo es la misma sesión porque la intermedia no existió.
    Comparten `gap_pct` y `retorno_real_pct` idénticos y entre ellas están
    los movimientos más grandes de toda la ventana (+29,95%, +26,81%,
    +17,52%): contadas dos veces inflan cualquier media —E|r| pasa de 3,72%
    a 4,02%— y contaminan cualquier estadístico pareado.

    El defecto que esto tumbó: `mde_desde_v6.py` deduplicaba y `mirada.py`
    no, así que el mismo resultado caía en dos clústeres distintos. Fue la
    razón descalificante del cuarto rechazo del diseño secuencial.

    Es la misma familia que la pregunta pendiente de `DECISIONES.md` §33.8
    sobre el 29-jul, pero más grande: 30 filas y cinco sesiones, no 8 y una.
    """
    df = _filas_selladas_excluir_cero()
    dup = df[df.duplicated(subset=["ticker", "sesion_objetivo"], keep=False)]
    assert dup.empty, (
        f"{len(dup)} de {len(df)} filas selladas ({len(dup)/len(df):.1%}) "
        f"comparten (ticker, sesión objetivo) con otra fila, sobre "
        f"{dup['sesion_objetivo'].nunique()} sesiones objetivo distintas.")


# ==========================================================================
# 6. La cita por número de línea que se desplazó
# ==========================================================================
_RE_CITA_LINEA = re.compile(
    r"DECISIONES\.md`?\s*:\s*(\d+)(?:\s*-\s*(\d+))?")
_RE_SECCION_EN_LINEA = re.compile(r"§\s*(\d+)(?:\.(\d+))?")
_RE_TOKEN_DISTINTIVO = re.compile(r"\d+[.,]\d+|\b\d{2,}\b|\b[A-ZÁÉÍÓÚÑ]{4,}\b")
# Los números de OTRAS citas no son tokens del contenido: si no se
# quitaran, la cita se "verificaría" contra los números de sus vecinas.
_RE_CUALQUIER_CITA = re.compile(r"[\w./áéíóúñÁÉÍÓÚÑ-]+\.(?:md|py)`?\s*:\s*\d+(?:\s*-\s*\d+)?")
_TOKENS_NO_DISTINTIVOS = {"DECISIONES", "GEMELO", "SECUENCIAL", "MICRO",
                          "CONDICIONAL", "RELEVO", "README", "CLAUDE", "ESTADO"}
_EXCLUIR_DE_LA_BUSQUEDA = ("/venv/", "/node_modules/", "/.git/", "/frontend/",
                           "__pycache__", "/tests/test_epistemico.py")


def _archivos_que_pueden_citar() -> list[tuple[str, str]]:
    fuera = []
    for patron in ("**/*.md", "**/*.py"):
        for ruta in glob.glob(os.path.join(_RAIZ, patron), recursive=True):
            if any(x in ruta for x in _EXCLUIR_DE_LA_BUSQUEDA):
                continue
            fuera.append((os.path.relpath(ruta, _RAIZ), _leer(ruta)))
    return sorted(set(fuera))


def _tokens_del_entorno(lineas: list[str]) -> set[str]:
    texto = _RE_CUALQUIER_CITA.sub(" ", " ".join(lineas))
    return {t for t in _RE_TOKEN_DISTINTIVO.findall(texto)
            if t not in _TOKENS_NO_DISTINTIVOS}


def _indice_de_secciones(lineas: list[str]) -> dict[str, tuple[int, int]]:
    """(inicio, fin) por sección de `DECISIONES.md`, en números de línea."""
    marcas = []
    for i, linea in enumerate(lineas):
        m = re.match(r"#{2,3}\s+(\d+)(?:\.(\d+))?[.\s]", linea)
        if m:
            clave = m.group(1) + ("." + m.group(2) if m.group(2) else "")
            marcas.append((clave, i + 1))
    idx = {}
    for j, (clave, ini) in enumerate(marcas):
        fin = marcas[j + 1][1] - 1 if j + 1 < len(marcas) else len(lineas)
        idx.setdefault(clave, (ini, fin))
    return idx


def detectar_citas_de_linea_desplazadas(archivos, decisiones: str):
    """Citas `DECISIONES.md:N` que ya no apuntan a lo que dicen.

    Cascada, de la comprobación más fuerte a la más débil:
      1. Si la cita trae `§N.M`, las líneas citadas tienen que caer dentro
         de esa sección.
      2. Si no, algún token distintivo del entorno de la cita (un decimal o
         una palabra en mayúsculas) tiene que aparecer en el rango citado.
      3. Si no hay tokens, al menos la línea tiene que existir y no estar
         vacía.
    """
    dl = decisiones.split("\n")
    secciones = _indice_de_secciones(dl)
    hallazgos = []
    for nombre, texto in archivos:
        lineas = texto.split("\n")
        for i, linea in enumerate(lineas):
            for m in _RE_CITA_LINEA.finditer(linea):
                ini = int(m.group(1))
                fin = int(m.group(2)) if m.group(2) else ini
                if fin > len(dl) or ini < 1:
                    hallazgos.append(
                        (nombre, i + 1, f"cita fuera del archivo: {ini}-{fin}"))
                    continue
                citado = "\n".join(dl[max(0, ini - 3):fin + 2])
                sec = _RE_SECCION_EN_LINEA.search(linea)
                if sec:
                    clave = sec.group(1) + ("." + sec.group(2)
                                            if sec.group(2) else "")
                    rango = secciones.get(clave)
                    if rango and not (rango[0] <= ini and fin <= rango[1]):
                        hallazgos.append(
                            (nombre, i + 1,
                             f"§{clave} vive en {rango}, la cita dice {ini}-{fin}"))
                    continue
                # La línea que cita, primero. Sólo si no aporta ningún
                # token propio se mira a las vecinas — mirarlas siempre
                # hace que una fila de tabla se "verifique" contra la de
                # al lado, que es un falso positivo puro.
                tokens = _tokens_del_entorno(lineas[i:i + 1])
                if not tokens:
                    tokens = _tokens_del_entorno(lineas[max(0, i - 1):i + 2])
                if tokens:
                    if not any(any(v in citado for v in _variantes(t))
                               for t in tokens):
                        hallazgos.append(
                            (nombre, i + 1,
                             f"nada de {sorted(tokens)[:5]} está en "
                             f"DECISIONES.md:{ini}-{fin}"))
                elif not "".join(dl[ini - 1:fin]).strip():
                    hallazgos.append(
                        (nombre, i + 1, f"DECISIONES.md:{ini}-{fin} está vacío"))
    return hallazgos


def test_ninguna_cita_por_numero_de_linea_a_decisiones_quedo_desplazada():
    """Error crónico, visto al menos dos veces el 30-ago-2026.

    `DECISIONES.md` se escribe insertando actas, así que cualquier cita
    interna por número de línea **queda desplazada por el propio acta que
    la cita**: el número se verifica antes de escribir, se escribe, y la
    escritura lo invalida. El 30-ago pasó dos veces en la misma tanda —una
    cita a §30.5 se corrigió a 2605-2623 y el bloque nuevo, cinco líneas
    más largo, la dejó en 2610-2628. Hay una memoria del proyecto sobre
    esto ("Citas por número de línea en DECISIONES.md"), y la regla que
    dejó es: citar por sección, que es estable, y verificar el número
    DESPUÉS de aplicar la edición, no antes.

    Es el único test del archivo que barre `DECISIONES.md` entero, porque
    es el único que no juzga contenido: sólo comprueba que la cita apunte
    a donde dice.
    """
    decisiones = _leer(os.path.join(_RAIZ, "DECISIONES.md"))
    hallazgos = detectar_citas_de_linea_desplazadas(
        _archivos_que_pueden_citar(), decisiones)
    assert not hallazgos, (
        "Citas a DECISIONES.md por número de línea que ya no apuntan a lo "
        "que dicen. Citá por sección (§N.M) y reverificá el número DESPUÉS "
        "de escribir:\n" + _informe(hallazgos))


def test_contraprueba_el_detector_caza_una_cita_desplazada():
    """Contraprueba: se simula la inserción de un acta.

    Se cita una línea por su contenido, se le insertan líneas arriba —que
    es literalmente lo que hace escribir un acta nueva— y se verifica que
    el detector caza el desplazamiento.
    """
    decisiones = ("## 1. Primera\n"
                  "el dato clave es 0.1849 sobre la ventana\n"
                  "## 2. Segunda\n"
                  "otra cosa\n")
    citante = [("x.md", "El 0.1849 sale de `DECISIONES.md`:2, la ventana.\n")]
    assert not detectar_citas_de_linea_desplazadas(citante, decisiones)
    desplazado = "## 0. Acta nueva\ntexto\ntexto\n" + decisiones
    assert detectar_citas_de_linea_desplazadas(citante, desplazado)


# ==========================================================================
# 7. El README contra el módulo árbitro
# ==========================================================================
_RE_P_PUBLICADA = re.compile(r"McNemar\s*p\s*[=≈]\s*(\d+(?:\.\d+)?)", re.I)
_RE_METODO_DECLARADO = re.compile(
    r"χ²|chi2|chi-cuadrado|correcci[oó]n de continuidad|continuity|"
    r"binomial exacta|exact", re.I)


def detectar_p_publicadas_sin_metodo(readme: str):
    """p de McNemar publicadas sin decir con qué test se computaron."""
    lineas = readme.split("\n")
    hallazgos = []
    for i, linea in enumerate(lineas):
        if not _RE_P_PUBLICADA.search(linea):
            continue
        if _RE_METODO_DECLARADO.search(_ventana(lineas, i, 3)):
            continue
        hallazgos.append((("README.md"), i + 1, linea))
    return hallazgos


@pytest.mark.xfail(
    reason="DECISIONES.md §55 y GEMELO/resultados/mcnemar_dos_rutas.md: las "
           "dos rutas son CORRECTAS y son tests distintos, así que no hay "
           "cifra errónea que arreglar — falta declarar el método. Elegir "
           "entre la opción A (declarar y no mover nada, recomendada), la B "
           "(migrar al árbitro y mover cuatro cifras publicadas) y la C "
           "(migrar hacia adelante, congelar hacia atrás) es decisión de "
           "Nicolás, y mover una cifra publicada lleva su firma. Rojo a "
           "propósito hasta entonces.")
def test_toda_p_publicada_declara_con_que_test_se_computo():
    """31-ago-2026, cuarta corrida autónoma, Frente D.

    El README publica McNemar p = 0.1849 para la ventana sellada; el módulo
    árbitro (`evaluacion.mcnemar_exact`) devuelve 0.1847 sobre el mismo par
    de discordantes. **Ninguna de las dos está mal**: 0.1849 es el χ² de
    McNemar con corrección de continuidad de Edwards
    (`backtest/linea_base.py:126`) y 0.1847 es la binomial exacta
    bilateral. Mismo par (b, c), mismo n, métodos distintos — verificados
    los dos contra varas de otra familia (aritmética racional exacta con
    `Fraction` para la binomial; `erfc` y `2·(1−Φ(√x))` para el χ²).

    Por eso este test NO exige que una de las dos cambie: exige que el
    método esté **declarado** al lado de la cifra. Publicar "p = 0.1849"
    sin decir qué test es fue lo que permitió que la discrepancia pasara
    inadvertida cinco días. Son cuatro cifras publicadas por la misma ruta
    no-árbitro (0.1158, 0.2542, 0.1849 y el 0.4633 de la línea base
    congelada), y `.claude/rules/backtest.md`:26-27 dice literal: "No
    reimplementes Wilson, McNemar, DSR ni CRPS a mano".

    El test primero **comprueba en vivo** que las dos rutas discrepan sobre
    el par real de la ventana sellada; sólo si discrepan exige la
    declaración de método.
    """
    import backtest.linea_base as LB
    from evaluacion import mcnemar_exact

    df = LB.cargar()
    if df.empty:
        pytest.skip("senales.db no está en esta máquina")
    duelo = LB.duelo(LB.aplicar_convencion(df, LB.CONVENCION_OFICIAL))
    b, c = duelo["mcnemar_b01"], duelo["mcnemar_b10"]

    p_publicada = LB.mcnemar(b, c)          # la ruta que produce el README
    p_arbitro = mcnemar_exact(b, c)         # el módulo árbitro del proyecto

    if math.isclose(round(p_publicada, 4), round(p_arbitro, 4)):
        pytest.skip("las dos rutas coinciden a la precisión publicada; "
                    "no hay discrepancia que declarar")

    hallazgos = detectar_p_publicadas_sin_metodo(
        _leer(os.path.join(_RAIZ, "README.md")))
    assert not hallazgos, (
        f"Sobre el par real de la ventana sellada (b={b}, c={c}) la ruta del "
        f"README da {p_publicada:.4f} y el módulo árbitro {p_arbitro:.4f}. "
        f"Las dos son correctas, son tests distintos — pero el README no "
        f"dice cuál publica:\n" + _informe(hallazgos))


def test_contraprueba_el_detector_caza_la_p_sin_metodo():
    """Contraprueba del detector del README, y de que la declaración
    efectivamente lo satisface."""
    malo = "**+6.5 pp con McNemar p = 0.1849: no distinguible de cero.**\n"
    assert detectar_p_publicadas_sin_metodo(malo)
    bueno = ("**+6.5 pp con McNemar p = 0.1849 (χ² con corrección de "
             "continuidad): no distinguible de cero.**\n")
    assert not detectar_p_publicadas_sin_metodo(bueno)


# ==========================================================================
# El candado del archivo: nada de acá escribe
# ==========================================================================
def test_este_archivo_no_escribe_en_ninguna_base_ni_toca_el_sellado():
    """Invariante estructural del propio archivo.

    Siete tests que leen el repo y una base no pueden convertirse, por un
    descuido futuro, en algo que escriba. Se comprueba sobre el texto
    fuente: nada de `motor.py`, `snapshot.py` ni `senales.py`, ninguna
    escritura, y el único acceso a `senales.db` es por el helper de solo
    lectura.
    """
    fuente = _leer(os.path.abspath(__file__))
    # Los prohibidos se arman por partes: escritos enteros, este test se
    # cazaría a sí mismo al leer su propio archivo.
    prohibidos = ["import " + p for p in ("motor", "snapshot", "senales")]
    prohibidos += ["ejecutar_" + "snapshot", "INSER" + "T ", "UPDAT" + "E ",
                   "DELET" + "E ", "to_" + "sql", "commi" + "t()"]
    for prohibido in prohibidos:
        assert prohibido not in fuente, f"este archivo no puede usar {prohibido!r}"
    assert "_conexion_ro" in fuente, (
        "el acceso a senales.db tiene que ir por el helper de solo lectura")


# ==========================================================================
# 8. La prueba de rendimiento que pasa en verde sobre un diseño roto
# ==========================================================================
# Los bancos de pruebas del pipeline RTL. El alcance es DELIBERADAMENTE
# angosto: no todos los archivos que miden algo en el repo, sólo los cinco
# bancos de `micro/rtl/tb/`, que son los que producen las cifras de latencia
# y de caudal que `GEMELO/MICRO/` publica.
_PATRONES_BANCOS_RTL = ("micro/rtl/tb/*.v",)

# Un banco MIDE ciclos si nombra la latencia, el caudal o su propio contador.
_RE_BANCO_MIDE_CICLOS = re.compile(
    r"latencia|LAT_ESPERADA|caudal|ciclos_tb", re.I)
# Y VERIFICA corrección si lee el vector esperado, lo compara y cuenta fallos.
# Las tres marcas juntas, no una: `esperado` solo aparece en cualquier
# comentario, y una comparación sola puede ser de un contador contra sí mismo.
_RE_BANCO_LEE_ESPERADO = re.compile(
    r"\$readmemh\s*\(\s*`?\w*ESPERAD|esperado\s*\[", re.I)
_RE_BANCO_COMPARA = re.compile(r"!==|!=")
_RE_BANCO_CUENTA_FALLOS = re.compile(r"\bfallos\b")
# La salida declarada, para el banco que a propósito sólo mide (no existe
# ninguno hoy). Pedirla por escrito es el punto: R2 no prohíbe medir sin
# verificar, prohíbe hacerlo sin decirlo.
_RE_BANCO_EXENTO = re.compile(r"R2-EXENTO", re.I)


def detectar_bancos_que_miden_sin_verificar(archivos):
    """Bancos que miden ciclos y no comparan los sellos contra el esperado.

    Consigna del archivo: preferir falsos negativos. Un banco se marca sólo
    si mide ciclos Y le falta alguna de las tres marcas de verificación Y no
    declara la salida `R2-EXENTO`. Un banco que verifica de una forma que
    este detector no reconoce puede agregar la marca con su razón: eso lo
    vuelve una decisión escrita, que es todo lo que se pide.
    """
    hallazgos = []
    for nombre, texto in archivos:
        if not _RE_BANCO_MIDE_CICLOS.search(texto):
            continue
        if _RE_BANCO_EXENTO.search(texto):
            continue
        faltan = []
        if not _RE_BANCO_LEE_ESPERADO.search(texto):
            faltan.append("no lee el vector esperado")
        if not _RE_BANCO_COMPARA.search(texto):
            faltan.append("no compara")
        if not _RE_BANCO_CUENTA_FALLOS.search(texto):
            faltan.append("no cuenta fallos")
        if faltan:
            hallazgos.append((nombre, 0, "mide ciclos pero " + ", ".join(faltan)))
    return hallazgos


def test_ningun_banco_de_pruebas_mide_ciclos_sin_comparar_bit_a_bit():
    """1-sep-2026, segunda tanda, Frente F. `GEMELO/MICRO/RTL.md` §7, R2.

    El error histórico: entre mensajes, el reproductor de `fuente_bram.v`
    dejaba 8 ciclos de silencio que dos documentos describían como una
    comodidad del banco ("para que la latencia se mida limpia"). Barriendo
    el parámetro resultó ser un requisito de corrección: con 0 ó 1 ciclos,
    **178 de los 181 sellos salen mal** — y **la latencia sigue dando 11
    ciclos exactos y perfectamente determinista** mientras eso pasa. La
    latencia era el entregable científico de esa pista, se la midió mucho, y
    era ciega a que el diseño producía basura.

    La lección excede al RTL y es la que este test codifica: **una prueba de
    rendimiento que no verifica corrección puede pasar en verde sobre un
    diseño roto.** Agravante medido el mismo día: la DECISIÓN sellada salía
    correcta en 181 de 181 (el puntaje era el que se calculaba con el peso
    del caso siguiente), así que una comprobación restringida a la decisión
    —la vara que `RTL.md` §4 punto 4 defendía como la que importa— también
    habría pasado en verde. Sólo la comparación bit a bit del puntaje lo
    cazó.

    FORMA QUE SE DESCARTÓ, y por qué. La primera idea fue un detector de
    prosa sobre `GEMELO/MICRO/*.md`: cifras de ciclos/MHz/ns publicadas sin
    una afirmación de corrección cerca. Se implementó y se midió antes de
    descartarlo: **76 de 110 líneas con cifra darían positivo**, casi todas
    legítimas (tablas de área, presupuestos, texto de diseño). Un detector
    que grita en el 69% de los casos se desactiva y entonces no previene
    nada. Éste, en cambio, corre sobre una población de cinco archivos con
    una convención propia, y hoy da cero.

    El contraejemplo EJECUTABLE de la lección vive en `micro/rtl`
    (`make hueco-gate`) y lo comprueba el test de más abajo cuando hay
    toolchain; esta parte es estática a propósito, para que corra en
    cualquier máquina.
    """
    bancos = [(os.path.relpath(r, _RAIZ), _leer(r))
              for r in _expandir(_PATRONES_BANCOS_RTL)]
    assert bancos, "no se encontró ningún banco en micro/rtl/tb/"
    hallazgos = detectar_bancos_que_miden_sin_verificar(bancos)
    assert not hallazgos, (
        "Bancos que miden ciclos sin comparar los sellos contra el vector "
        "esperado. Una cifra de latencia que sale de una corrida que no "
        "verificó corrección no dice nada (RTL.md §7, R2):\n"
        + _informe(hallazgos))


def test_contraprueba_el_detector_caza_el_banco_que_solo_mide_latencia():
    """Contraprueba: el detector tiene que cazar la forma histórica."""
    solo_mide = (
        "module tb_rapido;\n"
        "  always @(posedge clk) if (sello_valido) begin\n"
        "    if (latencia_ciclos < lat_min) lat_min = latencia_ciclos;\n"
        "  end\n"
        "  initial $display(\"latencia %0d/%0d\", lat_min, lat_max);\n"
        "endmodule\n")
    assert detectar_bancos_que_miden_sin_verificar([("tb_rapido.v", solo_mide)])

    # El mismo banco con la comparación puesta ya no se marca.
    completo = solo_mide.replace(
        "  end\n",
        "    if (puntaje_sellado !== esperado[vistos][15:0]) fallos = fallos + 1;\n"
        "  end\n")
    assert not detectar_bancos_que_miden_sin_verificar([("tb_ok.v", completo)])

    # Un banco que no mide ciclos no es asunto de R2.
    assert not detectar_bancos_que_miden_sin_verificar(
        [("tb_area.v", "module tb_area; endmodule\n")])

    # Y la salida declarada tiene que funcionar, si no el detector fuerza a
    # desactivarlo entero cuando aparezca el primer caso legítimo.
    exento = "// R2-EXENTO: mide caudal puro, la corrección la fija tb_demo.\n" + solo_mide
    assert not detectar_bancos_que_miden_sin_verificar([("tb_caudal.v", exento)])


def test_el_contraejemplo_ejecutable_del_hueco_sigue_en_pie():
    """1-sep-2026, Frente F. La lección, demostrada en vez de afirmada.

    `micro/rtl/verificar_hueco.py` corre el pipeline con el hueco por debajo
    del mínimo y comprueba las dos mitades del hallazgo a la vez: que la
    reproducción bit a bit **se rompe** (178 de 181) y que la latencia
    **sigue siendo perfecta** (11/11 en B=4, 5/5 en B=28) mientras eso pasa.
    Y verifica que la rotura es POR ESA RAZÓN — compila, corre entera, 181
    sellos recogidos, el 100% de los fallos en el modo esperado — porque un
    rojo de timeout o de compilación habría sido igual de rojo sin probar
    nada.

    Se salta sin toolchain: en una máquina sin OSS CAD Suite no hay nada que
    ejecutar, y el detector estático de más arriba es el que corre en todas.
    """
    import shutil
    import subprocess

    guion = os.path.join(_RAIZ, "micro", "rtl", "verificar_hueco.py")
    if not os.path.exists(guion):
        pytest.skip("micro/rtl/verificar_hueco.py no está en esta máquina")
    oss = os.path.expanduser("~/.local/opt/oss-cad-suite/bin")
    entorno = dict(os.environ, PATH=oss + os.pathsep + os.environ.get("PATH", ""))
    if not shutil.which("iverilog", path=entorno["PATH"]):
        pytest.skip("sin iverilog: el contraejemplo ejecutable no corre acá")

    r = subprocess.run([sys.executable, guion], cwd=os.path.dirname(guion),
                       capture_output=True, text=True, timeout=600, env=entorno)
    assert r.returncode == 0, (
        "el contraejemplo del hueco dejó de sostenerse:\n" + r.stdout + r.stderr)
    assert "B3 la LATENCIA sigue en" in r.stdout, (
        "el gate ya no comprueba que la latencia queda verde con los sellos "
        "mal, que es la mitad que hace a la lección")
