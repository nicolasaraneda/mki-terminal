"""Corrida 12, bloque 2.1 y bloque 5.4 — ninguna tarjeta de una vista del
riel de dinero muestra un número sin su estatus al lado.

No hay framework de tests de frontend en el proyecto (sin vitest: agregar
una dependencia exige acta), así que la regla se exige leyendo el TSX, como
ya hace `tests/test_dinero.py` con la palabra prohibida. El mecanismo es
estructural: `Card` renderiza el estatus con un solo componente (`Estatus`)
cuando recibe la prop `estatus`, y acá se exige que TODA `<Card` de las
vistas del riel la declare. ALCANCE REAL (director, corrida 12): sólo las vistas listadas en
VISTAS_RIEL; una vista nueva del riel que no se agregue a la lista NO se chequea.
Agregarla es parte de crearla."""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VISTAS = os.path.join(RAIZ, "frontend", "src", "vistas")
VISTAS_RIEL = ("RielDinero.tsx", "Rieles.tsx", "SellosDinero.tsx")


def _cards(src: str):
    """Cada etiqueta de apertura <Card ...> completa (puede ocupar varias líneas)."""
    return re.findall(r"<Card\b[^>]*>", src, flags=re.S)


def test_toda_card_de_una_vista_del_riel_declara_estatus():
    vistas = [v for v in VISTAS_RIEL if os.path.exists(os.path.join(VISTAS, v))]
    assert vistas, "no hay vistas del riel"
    for v in vistas:
        src = open(os.path.join(VISTAS, v), encoding="utf-8").read()
        cards = _cards(src)
        assert cards, f"{v}: sin tarjetas"
        sin = [c for c in cards if "estatus=" not in c]
        assert not sin, f"{v}: {len(sin)} tarjeta(s) sin estatus: {sin[0][:80]}"


def test_una_tarjeta_de_prosa_declara_SIN_CIFRAS_y_no_inventa_un_estatus_evidencial():
    """Bloqueante 4 del curador (corrida 12): exigir la prop en toda Card hizo
    que una tarjeta introductoria sin números llevara «MEDIDO / SIMULADO» a
    mano. Una tarjeta sin cifras declara SIN CIFRAS, explícito."""
    for v in VISTAS_RIEL:
        ruta = os.path.join(VISTAS, v)
        if not os.path.exists(ruta):
            continue
        src = open(ruta, encoding="utf-8").read()
        assert 'estatus="MEDIDO / SIMULADO"' not in src, f"{v}: estatus evidencial inventado para una tarjeta de prosa"
        for c in _cards(src):
            m = re.search(r'estatus="([^"]+)"', c)
            if m:
                assert m.group(1) in ("SIN CIFRAS",) or m.group(1).split(" ")[0] in (
                    "MEDIDO", "SIMULADO", "PROPUESTA", "REFUTADO", "RETIRADO", "DECISION_PENDIENTE"), (f"{v}: {m.group(1)}")


def test_las_frases_fijas_de_la_api_del_riel_tampoco_insinuan_resultado():
    """Observación del curador: la mayoría de las frases fijas viven en la API,
    no en el TSX. Mismo censo sobre el JSON servido."""
    import json
    from api.main import dinero_sellos, rieles
    prohibidas = ("rentable", "retorno esperado", "ganancia esperada", "confianza", "sostiene casi toda")
    for payload in (dinero_sellos(), rieles()):
        txt = json.dumps(payload, ensure_ascii=False, default=str).lower()
        for p in prohibidas:
            assert p not in txt, p
        # E1 nunca trae datos de ejemplo mientras esté NO EJECUTADO (pre-mortem 20)
        e1 = payload["datos"].get("E1")
        if e1 and e1.get("estado") == "NO EJECUTADO":
            assert e1["posiciones"] is None and e1["efectivo"] is None and e1["ejecuciones"] is None


def test_la_card_renderiza_el_estatus_con_el_componente_comun():
    src = open(os.path.join(RAIZ, "frontend", "src", "componentes", "Card.tsx"), encoding="utf-8").read()
    assert "estatus?: string" in src
    assert "{estatus && <Estatus valor={estatus} />}" in src


def test_contraprueba_el_detector_ve_una_card_sin_estatus():
    src = '<Card titulo="x" className="y">\n  <div>12,4 %</div>\n</Card>\n<Card estatus={d.estatus}>ok</Card>'
    cards = _cards(src)
    assert len(cards) == 2 and sum("estatus=" not in c for c in cards) == 1


def test_toda_vista_del_riel_evita_las_palabras_que_insinuan_resultado():
    """Bloque 5.3: ninguna frase fija puede sugerir ventaja, oportunidad
    rentable o resultado. «oportunidad» sólo con el estatus al lado (en la
    misma línea)."""
    prohibidas = ("rentable", "retorno esperado", "ganancia esperada", "confianza")
    for v in VISTAS_RIEL:
        ruta = os.path.join(VISTAS, v)
        if not os.path.exists(ruta):
            continue
        for i, linea in enumerate(open(ruta, encoding="utf-8"), 1):
            baja = linea.lower()
            for p in prohibidas:
                assert p not in baja, f"{v}:{i}: «{p}»"
            if "oportunidad" in baja:
                assert "estatus" in baja, f"{v}:{i}: «oportunidad» sin estatus en la misma línea"
