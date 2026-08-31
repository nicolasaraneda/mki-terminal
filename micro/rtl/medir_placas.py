#!/usr/bin/env python3
"""
medir_placas.py — cuánto ocupa el diseño en cada placa candidata.

DOS MEDICIONES, CON DISTINTO GRADO DE DUREZA. La diferencia importa y se
declara en la salida para que nadie las cite como si fueran lo mismo.

1. iCE40, celdas lógicas colocadas y ruteadas (DURA).
   El problema práctico: en el iCE40HX1K (1.280 LCs) las configuraciones con
   multiplicador NO ENTRAN, y nextpnr aborta con "no BELs remaining" sin
   decir cuántas celdas habrían hecho falta. "No cabe" sin cifra es un
   veredicto flojo. Así que se coloca el MISMO netlist en un iCE40HX8K
   (7.680 LCs, misma arquitectura, mismo LUT4, misma ausencia de DSP) sólo
   para LEER el número, y se compara ese número contra los 1.280 de la Go
   Board. El HX8K acá es un instrumento de medición, no una placa propuesta.

2. Artix-7, celdas del mapeo tecnológico (MENOS DURA, y se dice).
   OSS CAD Suite NO trae `nextpnr-xilinx` (verificado: los nextpnr incluidos
   son ice40, ecp5, machxo2, nexus, gowin, generic y himbaechel). Sin P&R no
   hay utilización real ni Fmax. Lo que SÍ se puede es correr `synth_xilinx`,
   que mapea a celdas Artix-7 de verdad — DSP48E1, LUT6, CARRY4 — y contarlas.
   Es mucho mejor que la cuenta a mano que se haría si no, y es peor que un
   reporte de Vivado. Se publica como lo que es.
"""

import os
import re
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
YOSYS = os.environ.get("YOSYS", "yosys")
NEXTPNR = os.environ.get("NEXTPNR", "nextpnr-ice40")

FUENTES = ["etapa_ingesta.v", "etapa_features.v", "etapa_puntaje.v",
           "etapa_decision.v", "uart_tx.v", "uart_rx.v", "etapa_salida.v",
           "pipeline_top.v", "sint_top.v"]

CONFIGS = [(1, 1, "F1", "campeon 4.6.0: beta x SOX, un multiplicador"),
           (3, 1, "F3", "generalizacion, 3 features ponderadas"),
           (6, 1, "F6", "generalizacion, 6 features ponderadas"),
           (1, 0, "F1SP", "solo umbral, SIN multiplicar")]

HX1K_LC = 1280      # Nandland Go Board
HX8K_LC = 7680      # solo instrumento de medicion
A7_LUTS = 63400     # Arty A7-100T, segun fpga.md §3
A7_DSP = 240


def correr(cmd, **kw):
    return subprocess.run(cmd, cwd=DIR, capture_output=True, text=True, **kw)


def netlist(nf, up, destino, familia):
    fuentes = " ".join(FUENTES)
    if familia == "ice40":
        synth = "synth_ice40 -top sint_top -json %s" % destino
    else:
        synth = "synth_xilinx -family xc7 -flatten -top sint_top"
    guion = "read_verilog -I. -DCFG_NF=%d -DCFG_PESOS=%d %s; %s" % (
        nf, up, fuentes, synth)
    return correr([YOSYS, "-p", guion])


def celdas(salida):
    blk = salida.split("Printing statistics")[-1].split("design hierarchy")[0]
    c = {}
    for m in re.finditer(r"^\s+(\d+)\s+(\w+)\s*$", blk, re.M):
        c[m.group(2)] = int(m.group(1))
    return c


def medir_ice40():
    print("=== 1. iCE40 — celdas logicas COLOCADAS Y RUTEADAS (medicion dura) ===")
    print("El netlist se coloca en un HX8K solo para poder LEER el numero: en el")
    print("HX1K de la Go Board nextpnr aborta sin decir cuanto falto. Misma")
    print("arquitectura, mismo LUT4, misma ausencia de DSP.")
    print()
    print("%-6s %8s %9s %9s  %s" % ("cfg", "LCs", "de 1280", "veredicto", "Fmax"))
    print("-" * 78)
    filas = []
    for nf, up, nombre, _d in CONFIGS:
        json_p = os.path.join("sintesis", "placas_%s.json" % nombre)
        r = netlist(nf, up, json_p, "ice40")
        if r.returncode != 0:
            print("%-6s  FALLO en yosys" % nombre)
            continue
        p = correr([NEXTPNR, "--hx8k", "--package", "ct256",
                    "--json", json_p, "--asc", os.devnull,
                    "--freq", "12", "--seed", "1"])
        salida = p.stdout + p.stderr
        m = re.search(r"ICESTORM_LC:\s+(\d+)/\s*(\d+)", salida)
        fs = re.findall(r"Max frequency for clock '[^']+':\s+([\d.]+)\s+MHz", salida)
        if not m:
            print("%-6s  FALLO en nextpnr" % nombre)
            continue
        lc = int(m.group(1))
        pct = 100.0 * lc / HX1K_LC
        cabe = "CABE" if lc <= HX1K_LC else "NO CABE"
        fmax = "%.2f MHz" % float(fs[-1]) if fs else "-"
        print("%-6s %8d %8.1f%% %9s  %s" % (nombre, lc, pct, cabe, fmax))
        filas.append((nombre, lc, cabe))
    print()
    for nombre, lc, cabe in filas:
        if cabe == "NO CABE":
            print("  %s: sobran %d LCs sobre las %d de la Go Board (%.1fx la capacidad)."
                  % (nombre, lc - HX1K_LC, HX1K_LC, lc / float(HX1K_LC)))
    print()


def medir_artix():
    print("=== 2. Artix-7 (xc7) — celdas del MAPEO, sin place & route ===")
    print("OSS CAD Suite no trae nextpnr-xilinx, asi que no hay utilizacion real")
    print("ni Fmax. Estas son celdas Artix-7 de verdad contadas tras synth_xilinx.")
    print("NO es un reporte de Vivado y no se debe citar como tal.")
    print()
    print("%-6s %8s %7s %6s %9s %9s" %
          ("cfg", "DSP48E1", "LUTs", "FF", "%LUT A7", "%DSP A7"))
    print("-" * 78)
    for nf, up, nombre, _d in CONFIGS:
        r = netlist(nf, up, None, "xc7")
        if r.returncode != 0:
            print("%-6s  FALLO en yosys" % nombre)
            continue
        c = celdas(r.stdout)
        lut = sum(v for k, v in c.items() if re.fullmatch(r"LUT[1-6]|INV", k))
        ff = sum(v for k, v in c.items() if k.startswith("FD"))
        dsp = c.get("DSP48E1", 0)
        print("%-6s %8d %7d %6d %8.2f%% %8.2f%%" %
              (nombre, dsp, lut, ff,
               100.0 * lut / A7_LUTS, 100.0 * dsp / A7_DSP))
    print()
    print("  Nota: el DSP de mas respecto de N_FEATURES es el multiplicador por")
    print("  constante de la media rodante (suma x 65536/N) de etapa_features.")
    print()


def main():
    que = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if que in ("todo", "ice40"):
        medir_ice40()
    if que in ("todo", "artix"):
        medir_artix()
    return 0


if __name__ == "__main__":
    sys.exit(main())
