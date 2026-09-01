#!/usr/bin/env python3
"""
medir_a7.py — el presupuesto de la Arty A7-100T (XC7A100TCSG324-1), medido.

QUÉ ES ESTA MEDICIÓN Y QUÉ NO ES
--------------------------------
`yosys synth_xilinx -family xc7` mapea a celdas Artix-7 REALES — DSP48E1,
LUT6, CARRY4, FDCE, RAMB18E1 — y permite contarlas. NO es place & route: no
hay utilización de slices, no hay Fmax, no hay reporte de Vivado. Se publica
como lo que es, y `micro/TOOLCHAIN.md` §3 explica por qué no hay más.

La conversión de unidades vive en GEMELO/MICRO/SINTESIS_A7.md §1 y no se
repite acá; lo único que hay que saber para leer la salida es que el XC7A100T
tiene 63.400 LUT6 y 126.800 flip-flops REALES (15.850 slices x 4 LUT + 8 FF,
DS180 Tabla 4 y su nota 1), y que las "101.440 celdas lógicas" del catálogo
son LUT6 x 1,6 — una unidad de marketing que no se puede comparar con nada
que salga de un sintetizador.

CINCO BLOQUES, CADA UNO RESPONDE UNA PREGUNTA DISTINTA
-----------------------------------------------------
  1. presupuesto  — qué ocupa el pipeline tal cual está hoy
  2. multiplicador— cuántos DSP48E1 cuesta multiplicar, POR ANCHO
  3. anchos       — qué cuesta ensanchar el punto fijo (B3a)
  4. tickers      — cuántas instancias entran antes de topar (B3c)
  5. faltante     — qué cuesta lo que hoy NO está y el 4.6.0 completo exige
"""

import os
import re
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
YOSYS = os.environ.get("YOSYS", "yosys")

# --- Capacidades verificadas contra DS180 v2.6.1 Tabla 4 (XC7A100T) ---
A7_SLICES = 15850
A7_LUT6 = A7_SLICES * 4          # 63.400
A7_FF = A7_SLICES * 8            # 126.800
A7_DSP = 240
A7_BRAM36 = 135
A7_BRAM_KB = 4860
HX1K_LC = 1280                   # iCE40HX1K de la Nandland Go Board

FUENTES = ["etapa_ingesta.v", "etapa_features.v", "etapa_puntaje.v",
           "etapa_decision.v", "uart_tx.v", "uart_rx.v", "etapa_salida.v",
           "pipeline_top.v", "sint_top.v", "multi_top.v"]


def yosys(guion, timeout=1800):
    try:
        r = subprocess.run([YOSYS, "-p", guion], cwd=DIR, capture_output=True,
                           text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout)[-300:]
    return r.stdout, None


def celdas(salida):
    """Cuenta de celdas del bloque final de estadísticas."""
    blk = salida.split("Printing statistics")[-1].split("design hierarchy")[0]
    c = {}
    for m in re.finditer(r"^\s+(\d+)\s+(\S+)\s*$", blk, re.M):
        c[m.group(2)] = int(m.group(1))
    return c


def resumen_xc7(c):
    lut = sum(v for k, v in c.items() if re.fullmatch(r"LUT[1-6]|INV", k))
    ff = sum(v for k, v in c.items() if k.startswith("FD"))
    return {
        "lut": lut,
        "ff": ff,
        "dsp": c.get("DSP48E1", 0),
        "carry": c.get("CARRY4", 0),
        "bram": c.get("RAMB18E1", 0) + c.get("RAMB36E1", 0),
        # Cota INFERIOR de slices: Vivado empaqueta 4 LUT y 8 FF por slice, y
        # sólo en el mejor caso. No es una predicción de utilización; es el
        # piso por debajo del cual es imposible que quede.
        "slices_piso": max(-(-lut // 4), -(-ff // 8)),
    }


def resumen_ice40(c):
    return {
        "lut": c.get("SB_LUT4", 0),
        "ff": sum(v for k, v in c.items() if k.startswith("SB_DFF")),
        "carry": c.get("SB_CARRY", 0),
        "bram": c.get("SB_RAM40_4K", 0),
        "dsp": 0,
    }


def sint(top, defines=(), fuentes=None, familia="xc7", flatten=True):
    fs = " ".join(fuentes if fuentes is not None else FUENTES)
    ds = " ".join("-D%s" % d for d in defines)
    if familia == "xc7":
        cmd = "synth_xilinx -family xc7 %s-top %s" % ("-flatten " if flatten else "", top)
    else:
        cmd = "synth_ice40 -top %s" % top
    out, err = yosys("read_verilog -I. %s %s; %s" % (ds, fs, cmd))
    if out is None:
        return None, err
    c = celdas(out)
    return (resumen_xc7(c) if familia == "xc7" else resumen_ice40(c)), None


# ---------------------------------------------------------------------------
# 1. Presupuesto del pipeline tal como está hoy
# ---------------------------------------------------------------------------
CONFIGS = [("F1", 1, 1, "campeon 4.6.0: beta x SOX"),
           ("F3", 3, 1, "generalizacion 3 features"),
           ("F6", 6, 1, "generalizacion 6 features"),
           ("F1SP", 1, 0, "solo umbral, sin multiplicar")]


def bloque_presupuesto():
    print("=" * 92)
    print("1. PRESUPUESTO EN XC7A100T — celdas del mapeo (SIN place & route)")
    print("=" * 92)
    print("   Capacidad real: %d LUT6, %d FF, %d DSP48E1, %d BRAM de 36 Kb (%d Kb)."
          % (A7_LUT6, A7_FF, A7_DSP, A7_BRAM36, A7_BRAM_KB))
    print("   top = sint_top (el envoltorio de placa: pipeline + UART RX + carga de pesos)")
    print()
    print("   %-6s %5s %6s %6s %6s %6s | %7s %7s %7s %7s"
          % ("cfg", "DSP", "LUT6", "FF", "CARRY", "BRAM",
             "%DSP", "%LUT", "%FF", "%BRAM"))
    print("   " + "-" * 86)
    for nombre, nf, up, _d in CONFIGS:
        r, err = sint("sint_top", ["CFG_NF=%d" % nf, "CFG_PESOS=%d" % up])
        if r is None:
            print("   %-6s FALLO: %s" % (nombre, err))
            continue
        print("   %-6s %5d %6d %6d %6d %6d | %6.2f%% %6.2f%% %6.2f%% %6.2f%%"
              % (nombre, r["dsp"], r["lut"], r["ff"], r["carry"], r["bram"],
                 100.0 * r["dsp"] / A7_DSP, 100.0 * r["lut"] / A7_LUT6,
                 100.0 * r["ff"] / A7_FF, 100.0 * r["bram"] / A7_BRAM36))
    print()


# ---------------------------------------------------------------------------
# 2. Cuántos DSP48E1 cuesta multiplicar, por ancho
# ---------------------------------------------------------------------------
MULS_A7 = ["mul_a7_w8", "mul_a7_w16", "mul_a7_25x18", "mul_a7_w18",
           "mul_a7_w24", "mul_a7_w25", "mul_a7_w32"]


def bloque_multiplicador():
    print("=" * 92)
    print("2. COSTO DE UN MULTIPLICADOR, POR ANCHO — Artix-7 vs iCE40")
    print("=" * 92)
    print("   El DSP48E1 lleva un multiplicador de 25x18 (DS180 Tabla 4 nota 2).")
    print("   Todo lo que exceda ese tamaño se descompone en varios DSP. El salto")
    print("   NO es lineal y es el numero que decide si conviene ensanchar.")
    print()
    print("   %-14s %5s %6s %6s | %8s %8s"
          % ("modulo", "DSP", "LUT6", "FF", "LUT4 ice", "CARRY"))
    print("   " + "-" * 62)
    for m in MULS_A7:
        a, ea = sint(m, fuentes=["costo_a7.v"], familia="xc7")
        i, ei = sint(m, fuentes=["costo_a7.v"], familia="ice40")
        if a is None:
            print("   %-14s FALLO xc7: %s" % (m, ea))
            continue
        print("   %-14s %5d %6d %6d | %8s %8s"
              % (m, a["dsp"], a["lut"], a["ff"],
                 i["lut"] if i else "-", i["carry"] if i else "-"))
    print()


# ---------------------------------------------------------------------------
# 3. Qué cuesta ensanchar el punto fijo (B3a)
# ---------------------------------------------------------------------------
# (etiqueta, ancho feature, frac feature, ancho peso, frac peso)
ANCHOS = [("Q8.8 / Q2.14   (HOY)", 16, 8, 16, 14),
          ("Q12.12 / Q2.22",       24, 12, 24, 22),
          ("Q16.16 / Q2.30",       32, 16, 32, 30)]


def bloque_anchos():
    print("=" * 92)
    print("3. ENSANCHAR EL PUNTO FIJO — etapa_puntaje sola, por ancho")
    print("=" * 92)
    print("   Se sintetiza SOLO etapa_puntaje: es donde vive la aritmetica, y")
    print("   sintetizarla aislada evita que el resto del pipeline diluya el efecto.")
    print("   El resto del pipeline NO se barre porque etapa_features desempaqueta")
    print("   el payload con recortes de 16 bits fijos por el formato de wire de 28")
    print("   bytes (que esta congelado) — ensanchar ahi exige cambiar el formato,")
    print("   que es otra decision y no esta tomada.")
    print()
    print("   %-22s %3s %5s %6s %6s | %8s %8s"
          % ("formato", "F", "DSP", "LUT6", "FF", "LUT4 ice", "vs 1280"))
    print("   " + "-" * 74)
    for etiqueta, wf, ff_, wp, fp in ANCHOS:
        for nf in (1, 6):
            defs = ["CFG_NF=%d" % nf, "CFG_PESOS=1",
                    "MKI_ANCHO_FEATURE=%d" % wf, "MKI_FRAC_FEATURE=%d" % ff_,
                    "MKI_ANCHO_PESO=%d" % wp, "MKI_FRAC_PESO=%d" % fp]
            a, ea = sint("etapa_puntaje", defs, fuentes=["etapa_puntaje.v"])
            i, _ = sint("etapa_puntaje", defs, fuentes=["etapa_puntaje.v"],
                        familia="ice40")
            if a is None:
                print("   %-22s %3d FALLO: %s" % (etiqueta, nf, ea))
                continue
            luti = i["lut"] if i else 0
            print("   %-22s %3d %5d %6d %6d | %8d %7.0f%%"
                  % (etiqueta, nf, a["dsp"], a["lut"], a["ff"], luti,
                     100.0 * luti / HX1K_LC))
    print()


# ---------------------------------------------------------------------------
# 4. Cuántos tickers en paralelo (B3c)
# ---------------------------------------------------------------------------
def bloque_tickers(ks=(1, 2, 4, 8, 16, 32, 64)):
    print("=" * 92)
    print("4. REPLICACION ESPACIAL — K pipelines en paralelo, uno por ticker")
    print("=" * 92)
    print("   El margen por instancia se lee de la PENDIENTE medida entre dos K, no")
    print("   de dividir un total por K: SINTESIS.md §3.4 ya midio que el area de un")
    print("   pipeline no es la suma de sus partes (45% de diferencia en iCE40).")
    print()
    print("   %-5s %5s %7s %7s %7s | %6s %6s %6s"
          % ("K", "DSP", "LUT6", "FF", "CARRY", "%DSP", "%LUT", "%FF"))
    print("   " + "-" * 66)
    medidas = []
    for k in ks:
        r, err = sint("multi_top", ["CFG_K=%d" % k, "CFG_NF=1", "CFG_PESOS=1"])
        if r is None:
            print("   %-5d FALLO: %s" % (k, err))
            continue
        medidas.append((k, r))
        print("   %-5d %5d %7d %7d %7d | %5.2f%% %5.2f%% %5.2f%%"
              % (k, r["dsp"], r["lut"], r["ff"], r["carry"],
                 100.0 * r["dsp"] / A7_DSP, 100.0 * r["lut"] / A7_LUT6,
                 100.0 * r["ff"] / A7_FF))
    if len(medidas) >= 2:
        (k0, r0), (k1, r1) = medidas[0], medidas[-1]
        d = float(k1 - k0)
        m_lut = (r1["lut"] - r0["lut"]) / d
        m_ff = (r1["ff"] - r0["ff"]) / d
        m_dsp = (r1["dsp"] - r0["dsp"]) / d
        print()
        print("   Pendiente medida entre K=%d y K=%d (costo marginal por ticker):"
              % (k0, k1))
        print("     %.1f LUT6   %.1f FF   %.2f DSP48E1" % (m_lut, m_ff, m_dsp))
        topes = []
        if m_dsp > 0:
            topes.append(("DSP48E1", int(A7_DSP / m_dsp)))
        if m_lut > 0:
            topes.append(("LUT6", int(A7_LUT6 / m_lut)))
        if m_ff > 0:
            topes.append(("FF", int(A7_FF / m_ff)))
        topes.sort(key=lambda t: t[1])
        print("   Tope por recurso, extrapolando esa pendiente:")
        for nombre, n in topes:
            print("     %-8s -> %d tickers" % (nombre, n))
        print("   El que topa PRIMERO es %s, a %d tickers." % (topes[0][0], topes[0][1]))
    print()


# ---------------------------------------------------------------------------
# 5. Lo que hoy no está: las piezas del 4.6.0 completo (B3b)
# ---------------------------------------------------------------------------
FALTANTE = [
    ("div32_comb",  "divisor 32/32 combinacional (cota superior)"),
    ("div32_serie", "divisor 32/32 restaurador, 32 ciclos fijos"),
    ("sqrt48",      "raiz cuadrada 48->24 bits, 24 ciclos fijos"),
]


def bloque_faltante():
    print("=" * 92)
    print("5. LO QUE FALTA PARA EL 4.6.0 COMPLETO — costo de cada pieza ausente")
    print("=" * 92)
    print("   motor.betas_al necesita cov/var (division), corr^2 (division) y")
    print("   resid_std (raiz + division). motor.prediccion_apertura_al necesita")
    print("   ademas 1,2816 x resid_std. Ninguna de esas piezas existe hoy en")
    print("   micro/rtl/: el pipeline recibe beta YA CALCULADA. Ver SINTESIS_A7.md §4.3.")
    print()
    print("   %-28s %5s %6s %6s %6s | %9s"
          % ("pieza", "DSP", "LUT6", "FF", "CARRY", "LUT4 ice"))
    print("   " + "-" * 72)
    for mod, desc in FALTANTE:
        a, ea = sint(mod, fuentes=["costo_a7.v"])
        i, _ = sint(mod, fuentes=["costo_a7.v"], familia="ice40")
        if a is None:
            print("   %-28s FALLO: %s" % (desc, ea))
            continue
        print("   %-28s %5d %6d %6d %6d | %9s"
              % (desc, a["dsp"], a["lut"], a["ff"], a["carry"],
                 i["lut"] if i else "-"))
    # N no entra por macro (es un parameter del modulo), asi que se fija con
    # `chparam` ANTES de la sintesis. Funciona acá y no en el Makefile del
    # pipeline porque `chparam` deriva un modulo con nombre nuevo y rompe el
    # `hierarchy -top` posterior sólo cuando el modulo tocado NO es el top.
    for n in (20, 60, 120):
        guion_a = ("read_verilog -I. costo_a7.v; chparam -set N %d momentos_rodantes; "
                   "synth_xilinx -family xc7 -flatten -top momentos_rodantes" % n)
        out, err = yosys(guion_a)
        if out is None:
            print("   momentos rodantes N=%-3d FALLO: %s" % (n, err))
            continue
        r = resumen_xc7(celdas(out))
        guion_i = ("read_verilog -I. costo_a7.v; chparam -set N %d momentos_rodantes; "
                   "synth_ice40 -top momentos_rodantes" % n)
        out_i, _ = yosys(guion_i)
        ri = resumen_ice40(celdas(out_i)) if out_i else None
        print("   %-28s %5d %6d %6d %6d | %9s"
              % ("momentos rodantes N=%d" % n, r["dsp"], r["lut"], r["ff"],
                 r["carry"], ri["lut"] if ri else "-"))
    print()


# ---------------------------------------------------------------------------
# 6. Qué cuesta ensanchar el bus de entrada (B3d)
# ---------------------------------------------------------------------------
FUENTES_ANCHO = ["etapa_ingesta_ancha.v", "etapa_features.v", "etapa_puntaje.v",
                 "etapa_decision.v", "uart_tx.v", "etapa_salida.v",
                 "pipeline_top_ancho.v"]


def bloque_ingesta(bs=(1, 2, 4, 7, 14, 28)):
    print("=" * 92)
    print("6. ENSANCHAR EL BUS DE ENTRADA — la palanca REAL de la latencia")
    print("=" * 92)
    print("   De los 32 ciclos de latencia, 27 son la ingesta byte a byte y 5 son")
    print("   las cuatro etapas siguientes. La latencia de este pipeline no la pone")
    print("   el computo: la pone el ancho del bus. Latencia = ceil(28/B) + 4.")
    print("   Las latencias de la ultima columna estan MEDIDAS en simulacion sobre")
    print("   los 181 vectores reales (tb/tb_pipeline_ancho.v), no calculadas.")
    print()
    print("   %-3s %8s %6s %6s %6s | %8s %8s | %s"
          % ("B", "palabras", "DSP", "LUT6", "FF", "LUT4 ice", "FF ice", "latencia"))
    print("   " + "-" * 78)
    for b in bs:
        n_pal = -(-28 // b)
        a, ea = sint("pipeline_top_ancho", ["CFG_B=%d" % b, "CFG_NF=1", "CFG_PESOS=1"],
                     fuentes=FUENTES_ANCHO)
        i, _ = sint("pipeline_top_ancho", ["CFG_B=%d" % b, "CFG_NF=1", "CFG_PESOS=1"],
                    fuentes=FUENTES_ANCHO, familia="ice40")
        if a is None:
            print("   %-3d FALLO: %s" % (b, ea))
            continue
        print("   %-3d %8d %6d %6d %6d | %8s %8s | %d ciclos"
              % (b, n_pal, a["dsp"], a["lut"], a["ff"],
                 i["lut"] if i else "-", i["ff"] if i else "-", n_pal + 4))
    print()


BLOQUES = {
    "presupuesto": bloque_presupuesto,
    "multiplicador": bloque_multiplicador,
    "anchos": bloque_anchos,
    "tickers": bloque_tickers,
    "faltante": bloque_faltante,
    "ingesta": bloque_ingesta,
}


def main():
    pedidos = sys.argv[1:] or list(BLOQUES)
    for p in pedidos:
        if p not in BLOQUES:
            print("bloque desconocido: %s (hay: %s)" % (p, ", ".join(BLOQUES)))
            return 2
        BLOQUES[p]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
