"""cifras.py — el módulo árbitro de toda cifra publicada de MKI Terminal.

Octava corrida (2-sep-2026), Frente G: reglas de la casa ejecutables.

Regla: una cifra publicada tiene UNA fuente, con n e intervalo, y los
documentos la citan desde acá — o un test falla cuando el documento y el
árbitro no coinciden. Este módulo NO inventa cifras: las de la ventana
sellada se COMPUTAN desde `senales.db` (mode=ro) en el instante pinchado
`backtest.linea_base.CORTE_SECCION_2`; las de la ventana larga están
CONGELADAS aquí con su procedencia (recomputarlas exige una descarga y
mueve los doce bloques: lleva firma).

Uso:
    from cifras import sellada, larga, doce_bloques
    c = sellada()             # dict con n, acierto, base, ventaja, IC, p, MAE, cobertura…
    for archivo, fragmento in doce_bloques(c): ...

El test `tests/test_cifras_arbitro.py` fija que cada uno de los doce bloques
aparece textualmente en su archivo, que cambiar n en el árbitro cambia los
doce, y que ninguna cifra RETIRADA (`GEMELO/cifras_retiradas.md`) vuelve a
aparecer en un documento publicado.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

_RAIZ = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------
# Ventana sellada: computada, no escrita
# ------------------------------------------------------------
# El instante en que el README publicó su ventana sellada (n = 248): distinto
# de `CORTE_SECCION_2` (24-ago, la línea base de la §2.8, n = 223) y de
# `CORTE_REGLA_FIRMADA` (31-ago). Tres instantes pinchados, tres nombres.
CORTE_README = "2026-08-28"


def sellada(hasta_sello: str | None = None) -> dict:
    """Las cifras de la ventana sellada bajo la convención canónica
    (`excluir_cero`), SIN deduplicar (lo publicado en el README) y al
    instante pinchado del README. Toda cifra lleva su n y su intervalo."""
    from backtest import linea_base as lb
    corte = hasta_sello or CORTE_README
    df = lb.aplicar_convencion(lb.cargar(hasta_sello=corte, dedup=False), lb.CONVENCION_OFICIAL)
    d = lb.duelo(df)
    m = lb.magnitud(df)
    cal = lb.calibracion(df)
    n = d["n"]
    f = lambda x: float(x) if x is not None else None   # sin np.float64 en el JSON
    return {
        "hasta_sello": corte, "convencion": lb.CONVENCION_OFICIAL, "dedup": False,
        "n": n, "dias": int(df["fecha"].nunique()),
        "modelo_aciertos": int(d["modelo_aciertos"]), "modelo_pct": f(d["modelo_pct"]), "modelo_wilson": [f(x) for x in d["modelo_wilson"]],
        "base_aciertos": int(d["base_aciertos"]), "base_pct": f(d["base_pct"]), "base_wilson": [f(x) for x in d["base_wilson"]],
        "ventaja_pp": f(d["ventaja_pp"]), "mcnemar_p": f(d["mcnemar_p"]), "b": int(d["mcnemar_b01"]), "c": int(d["mcnemar_b10"]),
        "mae_modelo_pp": f(m["mae_modelo"]), "mae_cero_pp": f(m["mae_cero"]),
        "mae_mejora_pct": round(100 * (m["mae_modelo"] / m["mae_cero"] - 1), 1),
        "cobertura_80_pct": f(cal.get("cobertura_pct")), "ratio_ancho": f(cal.get("ratio_ancho_error")),
        "procedencia": "backtest.linea_base.{cargar,aplicar_convencion,duelo,magnitud,calibracion} en mode=ro",
    }


# ------------------------------------------------------------
# Ventana larga: congelada con procedencia (no recomputable sin descarga)
# ------------------------------------------------------------
@dataclass(frozen=True)
class Larga:
    n: int = 14618
    ventaja_pp: float = 15.66
    por_bolsa: tuple = (("Tokio", "XTKS", 7230, 19.1, 1.75), ("Taipéi", "XTAI", 1807, 16.8, 2.75),
                        ("Seúl", "XKRX", 3626, 15.4, 1.75), ("Fráncfort", "XETR", 1955, 2.5, 8.75))
    p_francfort: float = 0.111
    procedencia: str = ("GEMELO/ventana_larga.py sobre el caché de gaps v1 (26-ago-2026); README.md:46-49 y :146. "
                        "ADVERTENCIA (2-sep-2026, acta de la octava corrida): el caché v1 omitía toda sesión "
                        "posterior a un feriado local (~4,5% de las filas); recomputar mueve los doce bloques y lleva firma.")


def larga() -> Larga:
    return Larga()


# ------------------------------------------------------------
# Los doce bloques que se mueven con n
# ------------------------------------------------------------
def doce_bloques(c: dict) -> list:
    """(archivo, fragmento) que DEBE aparecer textualmente en el archivo para
    la cifra vigente. Si n cambia en el árbitro, los doce fragmentos cambian
    (test), y cada archivo tiene que actualizarse — o no se mueve ninguno."""
    n = c["n"]
    v = f"{c['ventaja_pp']:+.1f}".replace("+", "+")
    return [
        ("README.md", f"sealed window (n={n})"),                                          # 1 TL;DR
        ("README.md", f"**{v} pp with p = {c['mcnemar_p']:.4f}"),                         # 2 TL;DR cifra
        ("README.md", f"n%3D{n}"),                                                        # 3 badge
        ("README.md", f"**{c['modelo_pct']:.1f}%** ({c['modelo_aciertos']}/{n})"),        # 4 tabla modelo
        ("README.md", f"**{c['base_pct']:.1f}%** ({c['base_aciertos']}/{n})"),            # 5 tabla base
        ("README.md", f"**{v} pp** | **McNemar p = {c['mcnemar_p']:.4f}**"),              # 6 tabla ventaja
        ("README.md", f"| Otras métricas (n={n}) |"),                                     # 7 otras métricas
        ("README.md", f"**{c['mae_modelo_pp']:.2f} pp** vs **{c['mae_cero_pp']:.2f}**"),   # 8 MAE
        ("README.md", f"{c['cobertura_80_pct']:.1f}% (nominal 80%)"),                     # 9 cobertura
        (".claude/skills/cifras-canonicas/SKILL.md", f"**{n}** | **{c['modelo_pct']:.1f}%** | **{c['base_pct']:.1f}%** | **{v} pp** | **{c['mcnemar_p']:.4f}**"),  # 10 skill
        (".claude/skills/cifras-canonicas/SKILL.md", f"MAE del gap {c['mae_modelo_pp']:.2f} contra {c['mae_cero_pp']:.2f}"),   # 11 skill MAE
        ("GEMELO/resultados/estado_epistemico.md", f"+{c['ventaja_pp']:.1f} pp, n = {n}".replace(".", ",")),  # 12 estado epistémico (coma decimal)
    ]


# ------------------------------------------------------------
# Cifras retiradas: legibles por máquina desde GEMELO/cifras_retiradas.md
# ------------------------------------------------------------
RUTA_RETIRADAS = os.path.join(_RAIZ, "GEMELO", "cifras_retiradas.md")
DOCUMENTOS_PUBLICADOS = ("README.md", "GEMELO/resultados/estado_epistemico.md",
                         ".claude/skills/cifras-canonicas/SKILL.md")


def cifras_retiradas() -> list:
    """Filas de la tabla de `GEMELO/cifras_retiradas.md`: cada una con el
    patrón (regex) que NO debe reaparecer en un documento publicado, el
    contexto y el acta que la retiró."""
    out = []
    if not os.path.exists(RUTA_RETIRADAS):
        return out
    for linea in open(RUTA_RETIRADAS, encoding="utf-8"):
        if not linea.startswith("| `"):
            continue
        celdas = [x.strip() for x in linea.strip().strip("|").split(" | ")]
        if len(celdas) < 4 or celdas[0] in ("`patrón`",):
            continue
        out.append({"patron": celdas[0].strip("`"), "contexto": celdas[1], "retirada": celdas[2],
                    "acta": celdas[3], "reemplazo": celdas[4] if len(celdas) > 4 else ""})
    return out


def reintroducciones(texto: str, retiradas: list | None = None) -> list:
    """Cifras retiradas que aparecen en `texto` sin una marca de retiro a
    ±2 líneas («retirad», «errata», «era», «decía», «es falsa», «desmont»…).
    Lo que usa el test y el hook propuesto."""
    retiradas = retiradas if retiradas is not None else cifras_retiradas()
    lineas = texto.split("\n")
    hallazgos = []
    for i, linea in enumerate(lineas):
        ctx = " ".join(lineas[max(0, i - 2):i + 3]).lower()
        if any(m in ctx for m in ("retirad", "errata", "decía", "decia", "era ", "refutad", "corregid",
                                  "es falsa", "falso", "desmont")):
            continue
        for r in retiradas:
            if re.search(r["patron"], linea):
                hallazgos.append((i + 1, r["patron"], linea.strip()[:100]))
    return hallazgos
