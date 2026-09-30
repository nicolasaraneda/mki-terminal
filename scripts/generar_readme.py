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
  · ventana larga: `cifras.larga()` (congelada con procedencia); el «N× la
    muestra» de su título es el cociente `cifras.larga().n / cifras.sellada()['n']`
    en el mismo formato entero que tenía el literal (acta §88.5 iii: el
    literal anterior era un resto de la rama sin deduplicar, derogada por D1;
    dictamen_13/adversario_readme.md punto 5);
  · riel de dinero (E0): SÓLO el N objetivo, leído de `dinero/sello_dinero.py`
    como texto. **El README ya no lleva contador vivo** (acta §90.3, firma de
    la tarjeta §65, opción b): el sellador mueve `data/backups/sello_dinero.csv`
    cada noche y nada regenera el README, así que la página se vencía sola y
    la suite se ponía roja sola. Este generador NO abre ese CSV; la página
    remite a él con un enlace;
  · N de intentos del DSR: `backtest/veredicto_51.py`, leído COMO TEXTO
    (`N_INTENTOS_PREVIO` y `N_INTENTOS_PREVIO + N_INTENTOS_NUEVOS`), sin
    importar el módulo (acta §88.5 i: manda la máquina). Si el literal no
    está donde se lo espera, el generador revienta nombrándolo: no adivina;
  · badges `tests` y `plataforma`: `docs/readme/badges_congelados.json` (acta
    §90.4, opción b). Son valores CONGELADOS con su fecha de lectura a la
    vista; este generador no corre la suite ni lee `version.py`. Dos
    decisiones de redacción, con su razón:
      (i) el badge decía «passing» y dice «recolectados», porque N sale de
          `pytest tests/ --collect-only -q` y cuenta también los saltados y
          los xfail: «passing» al lado de un conteo de recolección diría
          más que la cifra;
      (ii) la fecha va DENTRO del badge, idéntica en los dos idiomas, para no
          agregar prosa nueva en español y para que la paridad numérica
          entre las dos páginas se mantenga. Va con los guiones duplicados
          (`2026--09--30`) porque en un badge estático de shields.io el
          guion simple separa campos.
Lo que NO está en el árbitro queda LITERAL en la plantilla, en los dos idiomas
por igual (el test de paridad numérica de tests/test_readme.py exige que sean los
mismos tokens); su procedencia está censada en el dictamen del adversario de la
corrida 13 (GEMELO/resultados/dictamen_13/adversario_readme.md) y es deuda
declarada del árbitro, no una cifra a mano nueva.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import cifras  # noqa: E402

DIR_PLANTILLAS = os.path.join(RAIZ, "docs", "readme")
PLANTILLAS = {"README.es.md": "README.es.tmpl.md", "README.md": "README.en.tmpl.md"}
RUTA_SELLADOR = os.path.join(RAIZ, "dinero", "sello_dinero.py")
RUTA_VEREDICTO = os.path.join(RAIZ, "backtest", "veredicto_51.py")
RUTA_BADGES = os.path.join(DIR_PLANTILLAS, "badges_congelados.json")
_RE_MARCADOR = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


class MarcadorSinFuente(KeyError):
    pass


class FuenteIlegible(ValueError):
    """La fuente de una cifra existe pero no dice lo que el generador espera
    leer. Se revienta nombrando el archivo y lo que faltó: publicar un valor
    adivinado es peor que no publicar."""


def _url(valor: str) -> str:
    """Codificación para el badge de shields.io: + → %2B, − (U+2212) → %E2%88%92, … → %E2%80%A6."""
    return valor.replace("+", "%2B").replace("−", "%E2%88%92").replace("…", "%E2%80%A6")


def _ic(par, dec=1, signo=True) -> str:
    fmt = f"{{:+.{dec}f}}" if signo else f"{{:.{dec}f}}"
    return "[" + fmt.format(par[0]) + ", " + fmt.format(par[1]) + "]"


def _miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def n_objetivo_e0(ruta: str = RUTA_SELLADOR) -> int:
    with open(ruta, encoding="utf-8") as f:
        m = re.search(r"^N_OBJETIVO_E0\s*=\s*(\d+)", f.read(), re.M)
    return int(m.group(1))


def n_intentos_dsr(ruta: str = RUTA_VEREDICTO) -> dict:
    """N de intentos del DSR, leído como texto de `backtest/veredicto_51.py`
    (acta §88.5 i). No se importa el módulo: arrastra el backtest entero y el
    generador tiene que poder correr en cualquier checkout.

    Se exigen TRES líneas: los dos literales y la definición de
    `N_INTENTOS_51` como su suma. Si alguien redefine `N_INTENTOS_51` de otra
    manera, la suma que publicaría el README dejaría de ser el N que usa la
    máquina; en ese caso se revienta en vez de publicar."""
    with open(ruta, encoding="utf-8") as f:
        texto = f.read()
    leido = {}
    for nombre in ("N_INTENTOS_PREVIO", "N_INTENTOS_NUEVOS"):
        m = re.search(rf"^{nombre}[ \t]*=[ \t]*(\d+)[ \t]*(?:#.*)?$", texto, re.M)
        if m is None:
            raise FuenteIlegible(f"{ruta}: no se encontró el literal entero `{nombre} = <n>` a comienzo de línea")
        leido[nombre] = int(m.group(1))
    if re.search(r"^N_INTENTOS_51[ \t]*=[ \t]*N_INTENTOS_PREVIO[ \t]*\+[ \t]*N_INTENTOS_NUEVOS[ \t]*(?:#.*)?$", texto, re.M) is None:
        raise FuenteIlegible(f"{ruta}: `N_INTENTOS_51` ya no está definido como "
                             "`N_INTENTOS_PREVIO + N_INTENTOS_NUEVOS`; el generador no adivina la suma")
    return {"previo": leido["N_INTENTOS_PREVIO"],
            "con_los_del_51": leido["N_INTENTOS_PREVIO"] + leido["N_INTENTOS_NUEVOS"]}


def badges_congelados(ruta: str = RUTA_BADGES) -> dict:
    """Los dos badges congelados (acta §90.4): cuántos tests recolecta la
    suite y qué versión de plataforma había, EL DÍA en que se leyeron. No se
    regeneran solos; los actualiza quien relea la máquina, junto con la fecha.
    Se valida la forma porque un badge mal formado no rompe nada a la vista:
    shields.io dibuja igual lo que le llegue."""
    with open(ruta, encoding="utf-8") as f:
        b = json.load(f)
    n, version, leido_el = b.get("tests_recolectados"), b.get("plataforma_version"), b.get("leido_el")
    if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
        raise FuenteIlegible(f"{ruta}: `tests_recolectados` tiene que ser un entero positivo, vino {n!r}")
    if not isinstance(version, str) or re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        raise FuenteIlegible(f"{ruta}: `plataforma_version` tiene que ser texto X.Y.Z, vino {version!r}")
    if not isinstance(leido_el, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", leido_el) is None:
        raise FuenteIlegible(f"{ruta}: `leido_el` tiene que ser una fecha ISO AAAA-MM-DD, vino {leido_el!r}")
    try:
        datetime.date.fromisoformat(leido_el)
    except ValueError as e:
        raise FuenteIlegible(f"{ruta}: `leido_el` no es una fecha del calendario: {leido_el!r}") from e
    return {"tests_recolectados": n, "plataforma_version": version, "leido_el": leido_el}


def valores() -> dict:
    c = cifras.sellada()
    L = cifras.larga()
    intentos = n_intentos_dsr()
    badges = badges_congelados()
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
        # cuántas veces la muestra sellada cabe en la larga: cociente de los dos n
        # del árbitro, entero como el literal que reemplaza (acta §88.5 iii)
        "larga_veces": f"{L.n / c['n']:.0f}",
        # --- riel de dinero: sólo la constante firmada, ningún contador (acta §90.3) ---
        "e0_N_objetivo": str(n_objetivo_e0()),
        # --- N de intentos del DSR, texto de backtest/veredicto_51.py (acta §88.5 i) ---
        "n_intentos_previo": str(intentos["previo"]),
        "n_intentos_51": str(intentos["con_los_del_51"]),
        # --- badges congelados con fecha a la vista (acta §90.4) ---
        "badge_tests_n": str(badges["tests_recolectados"]),
        "badge_plataforma": badges["plataforma_version"],
        # shields.io: en un badge estático el guion simple separa campos
        "badge_leido_el_url": badges["leido_el"].replace("-", "--"),
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
