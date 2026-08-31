#!/usr/bin/env python3
"""
reportar_sintesis.py — extrae los números REALES de los logs de yosys,
nextpnr e icetime, y verifica que lo que se midió sea lo que se cree.

No inventa ni redondea nada: cada cifra sale de una línea del log, y el log
queda en `sintesis/` para que cualquiera la vuelva a leer.

LA VERIFICACIÓN QUE JUSTIFICA ESTE ARCHIVO
------------------------------------------
Una medición de área tiene un modo de fallo silencioso: si el sintetizador
puede probar que una entrada es constante, poda la lógica que dependía de ella
y devuelve un número MEJOR que el real. Pasó de verdad en este proyecto — la
primera versión de `sint_top.v` dejaba la carga de pesos sin conectar y yosys
borró el multiplicador, reportando 295 LUTs para F=1.

Por eso acá no se confía: se cuenta cuántos multiplicadores sobreviven en el
netlist ANTES del mapeo tecnológico y se compara contra N_FEATURES. Si no
coinciden, el reporte lo grita en vez de publicar la cifra bonita.
"""

import json
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
DIR_SINT = os.path.join(DIR, "sintesis")

# Recursos del iCE40HX1K, del catálogo de Lattice (los mismos que cita
# GEMELO/MICRO/fpga.md §3). No son medidos por nosotros: son la capacidad de
# la placa contra la que se compara.
HX1K_LUTS = 1280
HX1K_FF = 1280      # cada celda lógica del iCE40 lleva un LUT4 y un flip-flop
HX1K_BRAM = 16      # bloques de 4 Kbit


def leer(ruta):
    if not os.path.exists(ruta):
        return ""
    with open(ruta, errors="replace") as fh:
        return fh.read()


def stats_yosys(texto):
    """Cuenta de celdas del último bloque `Printing statistics` del log."""
    bloques = texto.split("Printing statistics")
    if len(bloques) < 2:
        return {}
    cuerpo = bloques[-1]
    celdas = {}
    for linea in cuerpo.splitlines():
        m = re.match(r"\s+(\d+)\s+(SB_\w+|\$\w+)\s*$", linea)
        if m:
            celdas[m.group(2)] = celdas.get(m.group(2), 0) + int(m.group(1))
        if "Executing CHECK pass" in linea:
            break
    return celdas


def multiplicadores_en_log(texto):
    """Cuántos multiplicadores REALES sobrevivieron hasta el mapeo.

    No se cuenta sobre la tabla de `stat` porque para cuando yosys imprime la
    última, los `$mul` ya se convirtieron en SB_LUT4 y no queda rastro. Se
    cuenta sobre la traza del pase `alumacc`, que emite exactamente una línea

        creating $macc model for ...$mul$etapa_puntaje.v:NNN ($mul).

    por cada multiplicador que llegó vivo a esa altura. Es el único punto del
    flujo donde el dato está y es inequívoco.

    Si esta cuenta da menos que N_FEATURES con USAR_PESOS=1, alguna entrada se
    volvió constante y el sintetizador podó lógica: la medición de área NO
    VALE y hay que decirlo, no publicarla.
    """
    return len(re.findall(r"creating \$macc model for .*?\(\$mul\)", texto))


def utilizacion_nextpnr(texto):
    """Tabla `Info: Device utilisation:` del log de nextpnr."""
    uso = {}
    for m in re.finditer(r"Info:\s+(\S+):\s+(\d+)/\s*(\d+)\s+(\d+)%", texto):
        uso[m.group(1)] = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
    return uso


def fmax_nextpnr(texto):
    """Frecuencia máxima estimada por el análisis de tiempos de nextpnr."""
    ms = re.findall(r"Max frequency for clock\s+'([^']+)':\s+([\d.]+)\s+MHz", texto)
    return [(n, float(v)) for n, v in ms]


def fmax_icetime(texto):
    m = re.search(r"Total path delay:\s+([\d.]+)\s+ns\s+\(([\d.]+)\s+MHz\)", texto)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None


def error_nextpnr(texto):
    """Si nextpnr falló, POR QUÉ. El fallo es un resultado, no un accidente."""
    for linea in texto.splitlines():
        if linea.startswith("ERROR:"):
            return linea.strip()
    return None


def informe(cfg, nf, usar_pesos):
    y_pipe = leer(os.path.join(DIR_SINT, "yosys_pipe_%s.log" % cfg))
    y_sint = leer(os.path.join(DIR_SINT, "yosys_sint_%s.log" % cfg))
    n_log = leer(os.path.join(DIR_SINT, "nextpnr_%s.log" % cfg))
    i_log = leer(os.path.join(DIR_SINT, "icetime_%s.log" % cfg))

    r = {"config": cfg, "n_features": nf, "usar_pesos": usar_pesos}

    # --- Guardia contra el podado silencioso ---
    # Cuenta esperada = los N_FEATURES del MAC, MÁS el multiplicador por
    # constante de la media rodante de `etapa_features` (suma * RECIPROCO_Q16).
    #
    # Ese "+1" solo aparece con N_FEATURES >= 2, y la razón es un hallazgo por
    # derecho propio: la única salida de la ventana rodante es g1, que el MAC
    # consume recién a partir de la segunda feature. Con N_FEATURES = 1 la
    # ventana entera —registro de desplazamiento, suma corrida y recíproco— es
    # lógica muerta y yosys la borra. O sea que el área medida con F=1 NO
    # incluye la etapa 2, y compararla contra la fila "Total F=1" de RTL.md §2
    # (que sí la cuenta) sería comparar dos cosas distintas. Por eso además se
    # miden las etapas por separado (`make etapas`).
    n_mul = multiplicadores_en_log(y_pipe)
    r["multiplicadores_vistos"] = n_mul
    esperados = (nf if usar_pesos else 0) + (1 if nf >= 2 else 0)
    r["multiplicadores_esperados"] = esperados
    r["ventana_podada"] = (nf < 2)
    r["medicion_valida"] = (n_mul == esperados)

    for etiqueta, log in (("pipeline", y_pipe), ("placa", y_sint)):
        c = stats_yosys(log)
        r[etiqueta] = {
            "SB_LUT4": c.get("SB_LUT4", 0),
            "SB_CARRY": c.get("SB_CARRY", 0),
            "flipflops": sum(v for k, v in c.items() if k.startswith("SB_DFF")),
            "SB_RAM40_4K": c.get("SB_RAM40_4K", 0),
            "celdas": c,
        }

    r["nextpnr_utilizacion"] = utilizacion_nextpnr(n_log)
    r["nextpnr_fmax"] = fmax_nextpnr(n_log)
    r["nextpnr_error"] = error_nextpnr(n_log)
    d, f = fmax_icetime(i_log)
    r["icetime_ns"] = d
    r["icetime_mhz"] = f
    return r


def imprimir(r):
    cfg = r["config"]
    print("=== %s (N_FEATURES=%d, pesos=%s) ==="
          % (cfg, r["n_features"], r["usar_pesos"]))

    if not r["medicion_valida"]:
        print("  !! MEDICION INVALIDA: yosys vio %d multiplicadores y se esperaban %d."
              % (r["multiplicadores_vistos"], r["multiplicadores_esperados"]))
        print("  !! Alguna entrada se volvio constante y la logica se podo.")
        print("  !! NO publicar estas cifras de area.")
    else:
        print("  guardia de podado: OK (%d multiplicadores en el netlist)"
              % r["multiplicadores_vistos"])

    p = r["pipeline"]
    s = r["placa"]
    print("  yosys, pipeline_top solo : %4d LUT4  %4d FF  %3d CARRY  %d BRAM"
          % (p["SB_LUT4"], p["flipflops"], p["SB_CARRY"], p["SB_RAM40_4K"]))
    print("  yosys, sint_top (placa)  : %4d LUT4  %4d FF  %3d CARRY  %d BRAM"
          % (s["SB_LUT4"], s["flipflops"], s["SB_CARRY"], s["SB_RAM40_4K"]))
    print("  costo del envoltorio     : %4d LUT4  %4d FF"
          % (s["SB_LUT4"] - p["SB_LUT4"], s["flipflops"] - p["flipflops"]))

    if r["nextpnr_error"]:
        print("  place & route: FALLO -> %s" % r["nextpnr_error"])
    elif r["nextpnr_utilizacion"]:
        for k, (u, t, pc) in sorted(r["nextpnr_utilizacion"].items()):
            print("  P&R %-14s: %5d / %5d  (%d%%)" % (k, u, t, pc))
    for nombre, v in r["nextpnr_fmax"]:
        print("  Fmax nextpnr '%s': %.2f MHz" % (nombre, v))
    if r["icetime_mhz"]:
        print("  icetime: ruta critica %.2f ns -> %.2f MHz"
              % (r["icetime_ns"], r["icetime_mhz"]))

    lut = p["SB_LUT4"]
    print("  ocupacion del pipeline solo en iCE40HX1K: %d/%d = %.1f%%"
          % (lut, HX1K_LUTS, 100.0 * lut / HX1K_LUTS))
    print()


CONFIGS = {"F1": (1, True), "F3": (3, True), "F6": (6, True), "F1SP": (1, False)}


def main():
    pedidos = sys.argv[1:] or list(CONFIGS)
    todos = []
    for cfg in pedidos:
        if cfg not in CONFIGS:
            print("configuracion desconocida: %s" % cfg)
            continue
        nf, up = CONFIGS[cfg]
        r = informe(cfg, nf, up)
        imprimir(r)
        todos.append(r)

    if len(todos) > 1:
        with open(os.path.join(DIR_SINT, "resumen.json"), "w") as fh:
            json.dump(todos, fh, indent=2, ensure_ascii=False)
        print("resumen escrito en sintesis/resumen.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
