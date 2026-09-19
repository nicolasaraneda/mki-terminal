#!/usr/bin/env python3
"""scripts/generar_readme.py — el generador de los README desde el árbitro.

Corrida 13 (19-sep-2026), bloque 5 (decisión D-E de la corrida 12). Regla:
**toda cifra de evaluación del README, en cualquier idioma, sale de
`cifras.py`**; ninguna se escribe a mano. Las plantillas viven en
`docs/readme/README.es.tmpl.md` y `docs/readme/README.en.tmpl.md` y llevan
marcadores `{{clave}}`; este script las llena y escribe `README.es.md` y
`README.md`. Un marcador sin clave en el árbitro ROMPE la generación con un
error que lo nombra (`MarcadorSinFuente`); una clave que ninguna plantilla
usa no es error.

    python scripts/generar_readme.py               # escribe los dos README
    python scripts/generar_readme.py --verificar   # no escribe: compara con lo que hay en disco (exit 1 si difiere)
    python scripts/generar_readme.py --valores     # lista clave → valor renderizado

Qué sale del árbitro y en qué formato (el formato es parte del contrato: una
traducción que redondea distinto es una cifra movida):
  · ventana sellada: `cifras.sellada()` (computada desde senales.db en mode=ro
    en el corte `CORTE_README`);
  · ventana larga: `cifras.larga()` (congelada con procedencia);
  · contador de E0: `data/backups/sello_dinero.csv` (la copia VERSIONADA de la
    base del riel de dinero, para que el README sea regenerable en cualquier
    checkout), N objetivo de `dinero/sello_dinero.py` como texto.
Lo que NO está en el árbitro queda LITERAL en la plantilla, en los dos idiomas
por igual (el test de paridad numérica de tests/test_readme.py exige que sean los
mismos tokens); su procedencia está censada en el dictamen del adversario de la
corrida 13 (GEMELO/resultados/dictamen_13/adversario_readme.md) y es deuda
declarada del árbitro, no una cifra a mano nueva.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import cifras  # noqa: E402

DIR_PLANTILLAS = os.path.join(RAIZ, "docs", "readme")
PLANTILLAS = {"README.es.md": "README.es.tmpl.md", "README.md": "README.en.tmpl.md"}
RUTA_CSV_DINERO = os.path.join(RAIZ, "data", "backups", "sello_dinero.csv")
RUTA_SELLADOR = os.path.join(RAIZ, "dinero", "sello_dinero.py")
_RE_MARCADOR = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


class MarcadorSinFuente(KeyError):
    pass


def _url(valor: str) -> str:
    """Codificación para el badge de shields.io: + → %2B, − (U+2212) → %E2%88%92, … → %E2%80%A6."""
    return valor.replace("+", "%2B").replace("−", "%E2%88%92").replace("…", "%E2%80%A6")


def _ic(par, dec=1, signo=True) -> str:
    fmt = f"{{:+.{dec}f}}" if signo else f"{{:.{dec}f}}"
    return "[" + fmt.format(par[0]) + ", " + fmt.format(par[1]) + "]"


def _miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def contador_e0(ruta_csv: str = RUTA_CSV_DINERO) -> dict:
    """Sesiones selladas del riel de dinero según la copia versionada."""
    if not os.path.exists(ruta_csv):
        return {"sesiones_selladas": 0, "cuentan_para_N": 0, "no_cuentan": [], "ultima_fecha_insumo": None}
    fechas, cuentan = set(), set()
    with open(ruta_csv, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            fechas.add(fila["fecha_insumo"])
            if fila.get("cuenta_para_N") == "1":
                cuentan.add(fila["fecha_insumo"])
    return {"sesiones_selladas": len(fechas), "cuentan_para_N": len(cuentan),
            "no_cuentan": sorted(fechas - cuentan),
            "ultima_fecha_insumo": max(fechas) if fechas else None}


def n_objetivo_e0(ruta: str = RUTA_SELLADOR) -> int:
    with open(ruta, encoding="utf-8") as f:
        m = re.search(r"^N_OBJETIVO_E0\s*=\s*(\d+)", f.read(), re.M)
    return int(m.group(1))


def valores() -> dict:
    c = cifras.sellada()
    L = cifras.larga()
    e0 = contador_e0()
    v = {
        # --- ventana sellada (cifras.sellada) ---
        "n": str(c["n"]),
        "dias": str(c["dias"]),
        "corte_readme": cifras.CORTE_README,
        "ventaja_pp": f"{c['ventaja_pp']:+.1f}",
        "ventaja_pp_url": _url(f"{c['ventaja_pp']:+.1f}"),
        "ventaja_ic_dia": _ic(c["ventaja_ic_dia"]),
        "ventaja_ic_dia_url": _url(f"−{abs(c['ventaja_ic_dia'][0]):.1f}…{c['ventaja_ic_dia'][1]:+.1f}"),
        "ventaja_ic_t_cluster": _ic(c["ventaja_ic_t_cluster"]),
        "modelo_pct": f"{c['modelo_pct']:.1f}",
        "modelo_aciertos": str(c["modelo_aciertos"]),
        "modelo_wilson": f"[{c['modelo_wilson'][0]:.1f} – {c['modelo_wilson'][1]:.1f}]",
        "base_pct": f"{c['base_pct']:.1f}",
        "base_aciertos": str(c["base_aciertos"]),
        "base_wilson": f"[{c['base_wilson'][0]:.1f} – {c['base_wilson'][1]:.1f}]",
        "mcnemar_p": f"{c['mcnemar_p']:.4f}",
        "mcnemar_p_exacta": f"{c['mcnemar_p_exacta']:.4f}",
        "icc": f"{c['icc']:.2f}",
        "deff": f"{c['deff']:.2f}",
        "n_efectivo": f"{c['n_efectivo']:.0f}",
        "p_permutacion_dia": f"{c['p_permutacion_dia']:.2f}",
        "retorno_pct": f"{c['retorno_pct']:.1f}",
        "retorno_wilson": f"[{c['retorno_wilson'][0]:.1f}–{c['retorno_wilson'][1]:.1f}]",
        "retorno_n": str(c["retorno_n"]),
        "mae_modelo_pp": f"{c['mae_modelo_pp']:.2f}",
        "mae_cero_pp": f"{c['mae_cero_pp']:.2f}",
        "mae_ganancia_pp": f"{c['mae_ganancia_pp']:+.2f}",
        "mae_ganancia_ic_t_dia": _ic(c["mae_ganancia_ic_t_dia"], dec=2),
        "mae_ganancia_p_dia": f"{c['mae_ganancia_p_dia']:.2f}",
        "cobertura_80_pct": f"{c['cobertura_80_pct']:.1f}",
        "ratio_ancho": f"{c['ratio_ancho']:.2f}",
        "ratio_ancho_ic_dia": _ic(c["ratio_ancho_ic_dia"], dec=2, signo=False),
        # --- ventana larga (cifras.larga, congelada con procedencia) ---
        "larga_n": _miles(L.n),
        "larga_ventaja_pp": f"{L.ventaja_pp:+.2f}",
        "larga_ventaja_pp_url": _url(f"{L.ventaja_pp:+.2f}"),
        "larga_p_francfort": f"{L.p_francfort:.3f}",
        # --- riel de dinero (copia versionada de la base + texto del sellador) ---
        "e0_sesiones_selladas": str(e0["sesiones_selladas"]),
        "e0_cuentan_para_N": str(e0["cuentan_para_N"]),
        "e0_ultima_fecha_insumo": str(e0["ultima_fecha_insumo"]),
        "e0_no_cuentan": (", ".join(e0["no_cuentan"]) if e0["no_cuentan"] else "none so far"),
        "e0_N_objetivo": str(n_objetivo_e0()),
    }
    for nombre, exchange, n, ventaja, margen in L.por_bolsa:
        clave = {"XTKS": "tokio", "XTAI": "taipei", "XKRX": "seul", "XETR": "francfort"}[exchange]
        v[f"larga_{clave}_n"] = _miles(n)
        v[f"larga_{clave}_ventaja_pp"] = f"{ventaja:+.1f}"
        v[f"larga_{clave}_margen_h"] = f"{margen:.2f}"
    return v


def render(plantilla: str, v: dict | None = None) -> str:
    v = valores() if v is None else v
    faltan = sorted({m for m in _RE_MARCADOR.findall(plantilla) if m not in v})
    if faltan:
        raise MarcadorSinFuente(f"marcadores sin clave en el árbitro: {faltan}")
    return _RE_MARCADOR.sub(lambda m: v[m.group(1)], plantilla)


def marcadores_de(plantilla: str) -> list:
    return sorted(set(_RE_MARCADOR.findall(plantilla)))


def generar(escribir: bool = True, v: dict | None = None) -> dict:
    """Renderiza las dos plantillas. Devuelve {destino: (texto_generado, coincide_con_disco)}."""
    v = valores() if v is None else v
    salida = {}
    for destino, plantilla in PLANTILLAS.items():
        ruta_t = os.path.join(DIR_PLANTILLAS, plantilla)
        ruta_d = os.path.join(RAIZ, destino)
        with open(ruta_t, encoding="utf-8") as f:
            texto = render(f.read(), v)
        actual = open(ruta_d, encoding="utf-8").read() if os.path.exists(ruta_d) else None
        if escribir and actual != texto:
            with open(ruta_d, "w", encoding="utf-8") as f:
                f.write(texto)
        salida[destino] = (texto, actual == texto)
    return salida


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="genera README.es.md y README.md desde las plantillas y el árbitro")
    ap.add_argument("--verificar", action="store_true", help="no escribe; exit 1 si el disco difiere de lo generado")
    ap.add_argument("--valores", action="store_true", help="lista clave → valor")
    a = ap.parse_args(argv)
    if a.valores:
        for k, val in valores().items():
            print(f"{k} = {val}")
        return 0
    r = generar(escribir=not a.verificar)
    distintos = [d for d, (_, ok) in r.items() if not ok]
    for d, (_, ok) in r.items():
        print(f"{d}: {'coincide con el disco' if ok else ('escrito' if not a.verificar else 'DIFIERE del disco')}")
    return 1 if (a.verificar and distintos) else 0


if __name__ == "__main__":
    raise SystemExit(main())
