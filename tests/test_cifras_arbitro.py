"""Reglas de la casa ejecutables (octava corrida, Frente G).

1. Cada uno de los doce bloques que dependen de n aparece TEXTUALMENTE en
   su archivo con la cifra que el árbitro (`cifras.py`) computa hoy desde
   `senales.db` en `mode=ro` al instante pinchado.
2. Si n cambia en el árbitro, los doce fragmentos cambian: no se puede
   mover uno sin mover los otros once.
3. Ninguna cifra retirada (`GEMELO/cifras_retiradas.md`) reaparece en un
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
    """El README publica n = 248, +6.5 pp, p = 0.1849 al instante pinchado
    `cifras.CORTE_README` (28-ago; `CORTE_SECCION_2` es el 24-ago, n = 223):
    el árbitro tiene que reproducirlo desde la base."""
    assert sellada["n"] == 248
    assert sellada["ventaja_pp"] == 6.5
    assert sellada["mcnemar_p"] == 0.1849
    assert sellada["mae_modelo_pp"] == pytest.approx(2.98, abs=0.005)
    assert sellada["cobertura_80_pct"] == pytest.approx(90.3, abs=0.05)


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
    otro["mcnemar_p"] = round(sellada["mcnemar_p"] + 0.0001, 4)
    otro["mae_modelo_pp"] = round(sellada["mae_modelo_pp"] + 0.01, 2)
    otro["cobertura_80_pct"] = round(sellada["cobertura_80_pct"] + 0.1, 1)
    a = cifras.doce_bloques(sellada)
    b = cifras.doce_bloques(otro)
    assert len(a) == 12 and len(b) == 12
    iguales = [x for x, y in zip(a, b) if x == y]
    assert not iguales, f"bloques que NO se mueven con n: {iguales}"


def test_ninguna_cifra_retirada_vuelve_a_un_documento_publicado():
    retiradas = cifras.cifras_retiradas()
    assert len(retiradas) >= 10, "el registro de cifras retiradas está vacío o no se lee"
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
