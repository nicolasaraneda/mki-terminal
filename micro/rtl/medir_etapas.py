#!/usr/bin/env python3
"""
medir_etapas.py — sintetiza CADA ETAPA POR SEPARADO y la contrasta contra la
estimación de `GEMELO/MICRO/RTL.md` §2, fila por fila.

POR QUÉ POR SEPARADO
--------------------
La tabla del §2 estima etapa por etapa. Contrastarla contra el total del
pipeline completo mezcla dos efectos y no permite decir DÓNDE se equivocó la
estimación — que es exactamente lo que se pide.

Y hay una razón más fuerte, descubierta midiendo: con N_FEATURES=1 la ventana
rodante de la etapa 2 es lógica MUERTA (su única salida, g1, la consume el MAC
recién a partir de la segunda feature) y yosys la borra entera. O sea que el
total medido con F=1 no incluye la etapa 2, mientras que la fila "Total, F=1"
de RTL.md sí la cuenta. Compararlas de frente sería comparar dos cosas
distintas. Sintetizada sola, la etapa 2 no tiene cómo desaparecer.

Cada etapa se sintetiza como su propio top: sus entradas son puertos, así que
ninguna se vuelve constante y no hay nada que podar.
"""

import os
import re
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
HX1K_LUTS = 1280

FUENTES = ["etapa_ingesta.v", "etapa_features.v", "etapa_puntaje.v",
           "etapa_decision.v", "uart_tx.v", "uart_rx.v", "etapa_salida.v",
           "pipeline_top.v"]

# (etiqueta, módulo top, defines, estimación de RTL.md §2 en LUTs, FF estimados)
# Las estimaciones se transcriben LITERALMENTE de la tabla del §2. No se
# reinterpretan ni se ajustan: si una fila no aplica tal cual, se dice al
# comparar, no se corrige la estimación para que quede mejor.
ETAPAS = [
    ("ingesta (parser 28 bytes)",        "etapa_ingesta",  [], (100, 150), 224),
    ("estado/features (N=10)",           "etapa_features", [], (50, 100), 160),
    ("puntaje F=1 SIN pesos (umbral)",   "etapa_puntaje",  ["CFG_NF=1", "CFG_PESOS=0"], (20, 30), 16),
    ("puntaje F=1 CON peso (campeon)",   "etapa_puntaje",  ["CFG_NF=1", "CFG_PESOS=1"], (220, 330), 48),
    ("puntaje F=3 CON pesos",            "etapa_puntaje",  ["CFG_NF=3", "CFG_PESOS=1"], (620, 930), 112),
    ("puntaje F=6 CON pesos",            "etapa_puntaje",  ["CFG_NF=6", "CFG_PESOS=1"], (1220, 1830), 208),
    ("decision (comparador doble)",      "etapa_decision", [], (15, 25), 8),
    ("salida (contador 48b + UART TX)",  "etapa_salida",   [], (100, 150), 80),
    ("uart_tx solo",                     "uart_tx",        [], (None, None), None),
    ("uart_rx solo (envoltorio placa)",  "uart_rx",        [], (None, None), None),
]

# etapa_puntaje necesita parámetros; se pasan por macro igual que en el
# Makefile. Los defaults de los módulos ya vienen de `CFG_NF`/`CFG_PESOS`.
PARAM_POR_MACRO = {
    "etapa_puntaje": "N_FEATURES/USAR_PESOS",
}


def sintetizar(top, defines):
    yosys = os.environ.get("YOSYS", "yosys")
    ds = " ".join("-D%s" % d for d in defines)
    guion = "read_verilog -I. %s %s; synth_ice40 -top %s" % (
        ds, " ".join(FUENTES), top)
    try:
        r = subprocess.run([yosys, "-p", guion], cwd=DIR,
                           capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout)[-400:]

    salida = r.stdout
    bloque = salida.split("Printing statistics")[-1]
    celdas = {}
    for linea in bloque.splitlines():
        m = re.match(r"\s+(\d+)\s+(SB_\w+)\s*$", linea)
        if m:
            celdas[m.group(2)] = int(m.group(1))
        if "Executing CHECK pass" in linea:
            break
    n_mul = len(re.findall(r"creating \$macc model for .*?\(\$mul\)", salida))
    return {
        "luts": celdas.get("SB_LUT4", 0),
        "carry": celdas.get("SB_CARRY", 0),
        "ff": sum(v for k, v in celdas.items() if k.startswith("SB_DFF")),
        "bram": celdas.get("SB_RAM40_4K", 0),
        "mul": n_mul,
    }, None


def veredicto(medido, rango):
    lo, hi = rango
    if lo is None:
        return "(sin estimacion en RTL.md)"
    if medido < lo:
        return "SOBREESTIMADA  x%.2f (medido %d < %d)" % (lo / float(medido) if medido else 0, medido, lo)
    if medido > hi:
        return "SUBESTIMADA    x%.2f (medido %d > %d)" % (medido / float(hi), medido, hi)
    return "DENTRO del rango estimado"


def main():
    print("=== Sintesis POR ETAPA, iCE40HX1K (yosys + synth_ice40) ===")
    print("Estimaciones transcritas de GEMELO/MICRO/RTL.md §2.")
    print()
    print("%-34s %6s %6s %6s %5s  %s"
          % ("etapa", "LUT4", "FF", "CARRY", "MUL", "estimacion RTL.md §2"))
    print("-" * 118)

    filas = []
    for etiqueta, top, defines, rango, ff_est in ETAPAS:
        r, err = sintetizar(top, defines)
        if r is None:
            print("%-34s  FALLO: %s" % (etiqueta, err.replace("\n", " ")[:60]))
            continue
        est = "%d-%d" % rango if rango[0] is not None else "-"
        print("%-34s %6d %6d %6d %5d  %-10s %s"
              % (etiqueta, r["luts"], r["ff"], r["carry"], r["mul"], est,
                 veredicto(r["luts"], rango)))
        filas.append((etiqueta, r, rango, ff_est))

    print()
    print("Capacidad del iCE40HX1K (Nandland Go Board): %d LUTs." % HX1K_LUTS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
