#!/usr/bin/env python3
"""
medir_techo.py — ¿se movió el techo de 240 tickers al bajar la latencia?

LA PREGUNTA. `SINTESIS_A7.md` §3.4 midió el techo de replicación con la
ingesta byte a byte: 240 tickers, con el DSP48E1 topando primero (FF a 375,
LUT6 a 817). La ingesta ancha baja el área por instancia. ¿Sube el techo?

LO QUE ESTE ARCHIVO NO HACE. No razona la respuesta. "El DSP no cambia, luego
el techo no cambia" es una deducción, y en este proyecto una deducción sobre
mapeo tecnológico ya falló una vez: `SINTESIS.md` §3.4 midió que el área de un
pipeline NO es la suma de sus partes. El sintetizador comparte, poda y duplica
lógica de formas que no se adivinan. Así que se sintetiza el barrido entero
otra vez, con B=4, y el techo se lee de la pendiente MEDIDA.

TRES BLOQUES:
  1. techo    — barrido de K con B=1 (control, tiene que reproducir 240) y B=4
  2. sin_dsp  — qué pasa si el multiplicador NO usa DSP48E1 (`-nodsp`): es la
                primera de las dos formas de subir el techo, y su costo se mide
  3. Las cifras de síntesis son DETERMINÍSTICAS: el mismo yosys sobre el mismo
     Verilog da el mismo entero siempre. No llevan intervalo y decir lo
     contrario sería inventar variabilidad donde no la hay. Lo que sí es
     incierto es la EXTRAPOLACIÓN de la pendiente más allá del último K medido,
     y eso se declara en el reporte como extrapolación, no como medición.
"""

import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

from medir_a7 import (A7_BRAM36, A7_DSP, A7_FF, A7_LUT6, celdas,  # noqa: E402
                      resumen_xc7, yosys)

FUENTES_ANCHO = ["etapa_ingesta_ancha.v", "etapa_features.v", "etapa_puntaje.v",
                 "etapa_decision.v", "uart_tx.v", "etapa_salida.v",
                 "pipeline_top_ancho.v", "multi_top_ancho.v"]

FUENTES_BYTE = ["etapa_ingesta.v", "etapa_features.v", "etapa_puntaje.v",
                "etapa_decision.v", "uart_tx.v", "etapa_salida.v",
                "pipeline_top.v", "multi_top.v"]


def sintetizar(top, defines, fuentes, extra=""):
    ds = " ".join("-D%s" % d for d in defines)
    fs = " ".join(fuentes)
    guion = ("read_verilog -I. %s %s; synth_xilinx -family xc7 -flatten %s-top %s"
             % (ds, fs, extra + " " if extra else "", top))
    out, err = yosys(guion, timeout=3600)
    if out is None:
        return None, err
    c = celdas(out)
    r = resumen_xc7(c)
    # Se adjunta la cuenta CRUDA de celdas. La columna "BRAM" del resumen suma
    # RAMB18E1 y RAMB36E1, que NO son la misma primitiva: un RAMB36 son 36 Kb y
    # un RAMB18 la mitad. Publicar "4 BRAM" sin decir cuáles es un dato que
    # nadie puede reconstruir después, y el porcentaje contra los 135 bloques de
    # 36 Kb queda sobreestimado. El guardián marcó exactamente esto.
    r["_celdas"] = c
    return r, None


def memoria(r):
    """Desglose de primitivas de memoria, para no publicar 'BRAM 4' a secas."""
    c = r.get("_celdas", {})
    b18, b36 = c.get("RAMB18E1", 0), c.get("RAMB36E1", 0)
    if not b18 and not b36:
        return "0", 0.0
    partes = []
    if b36:
        partes.append("%dx RAMB36E1" % b36)
    if b18:
        partes.append("%dx RAMB18E1" % b18)
    # Equivalente en bloques de 36 Kb, que es la unidad de DS180 Tabla 4.
    return " + ".join(partes), b36 + b18 / 2.0


def pendiente_y_topes(medidas):
    """Pendiente entre el primer y el ULTIMO K medido, igual que medir_a7.py."""
    (k0, r0), (k1, r1) = medidas[0], medidas[-1]
    d = float(k1 - k0)
    m = {rec: (r1[rec] - r0[rec]) / d for rec in ("lut", "ff", "dsp")}
    cap = {"lut": A7_LUT6, "ff": A7_FF, "dsp": A7_DSP}
    topes = sorted(((rec, int(cap[rec] / m[rec])) for rec in m if m[rec] > 0),
                   key=lambda t: t[1])
    return m, topes, (k0, k1)


def barrido(etiqueta, top, fuentes, defines_base, ks, extra=""):
    print("   %-5s %5s %8s %8s %8s | %6s %6s %6s"
          % ("K", "DSP", "LUT6", "FF", "CARRY", "%DSP", "%LUT", "%FF"))
    print("   " + "-" * 70)
    medidas = []
    for k in ks:
        r, err = sintetizar(top, defines_base + ["CFG_K=%d" % k], fuentes, extra)
        if r is None:
            print("   %-5d FALLO: %s" % (k, err))
            continue
        medidas.append((k, r))
        print("   %-5d %5d %8d %8d %8d | %5.2f%% %5.2f%% %5.2f%%"
              % (k, r["dsp"], r["lut"], r["ff"], r["carry"],
                 100.0 * r["dsp"] / A7_DSP, 100.0 * r["lut"] / A7_LUT6,
                 100.0 * r["ff"] / A7_FF))
    if len(medidas) < 2:
        return None
    m, topes, (k0, k1) = pendiente_y_topes(medidas)
    print()
    print("   Pendiente MEDIDA entre K=%d y K=%d (costo marginal por ticker):" % (k0, k1))
    print("     %.1f LUT6   %.1f FF   %.2f DSP48E1" % (m["lut"], m["ff"], m["dsp"]))
    print("   Techo por recurso (EXTRAPOLANDO esa pendiente mas alla de K=%d):" % k1)
    for nombre, n in topes:
        print("     %-8s -> %d tickers" % (nombre.upper(), n))
    print("   >>> [%s] el que topa PRIMERO es %s, a %d tickers."
          % (etiqueta, topes[0][0].upper(), topes[0][1]))
    print()
    return {"medidas": medidas, "pendiente": m, "topes": topes}


def bloque_techo(ks=(1, 2, 4, 8, 16, 32, 64)):
    print("=" * 92)
    print("1. EL TECHO CON LA INGESTA ANCHA — ¿se movio respecto de los 240?")
    print("=" * 92)
    print("   Control primero: B=1 tiene que reproducir la tabla de SINTESIS_A7.md")
    print("   §3.4 (240 tickers por DSP). Si no la reproduce, la comparacion de")
    print("   abajo no significa nada y hay que arreglar eso antes que nada.")
    print()
    res = {}
    print("   --- B=1 byte/ciclo (CONTROL: pipeline_top + multi_top originales) ---")
    res["B1"] = barrido("B=1", "multi_top", FUENTES_BYTE,
                        ["CFG_NF=1", "CFG_PESOS=1"], ks)
    for b in (4, 28):
        print("   --- B=%d bytes/ciclo (multi_top_ancho) ---" % b)
        res["B%d" % b] = barrido("B=%d" % b, "multi_top_ancho", FUENTES_ANCHO,
                                 ["CFG_NF=1", "CFG_PESOS=1", "CFG_B=%d" % b], ks)
    return res


def bloque_sin_dsp(ks=(1, 2, 4, 8, 16)):
    print("=" * 92)
    print("2. SUBIR EL TECHO (i): el multiplicador SIN DSP48E1  (`synth_xilinx -nodsp`)")
    print("=" * 92)
    print("   Si el DSP es el que topa, la forma directa de subir el techo es no")
    print("   gastar un DSP por ticker. `-nodsp` obliga a mapear el 16x16 con")
    print("   signo a LUT6 y CARRY4. El techo pasa a ponerlo LUT6 o FF, y lo que")
    print("   hay que medir es a cuanto y a que costo por ticker.")
    print()
    return barrido("B=4 sin DSP", "multi_top_ancho", FUENTES_ANCHO,
                   ["CFG_NF=1", "CFG_PESOS=1", "CFG_B=4"], ks, extra="-nodsp")


FUENTES_MULTI = ["etapa_ingesta_ancha.v", "etapa_features.v", "etapa_puntaje.v",
                 "etapa_decision.v", "uart_tx.v", "etapa_salida.v",
                 "pipeline_top_multi.v"]

FUENTES_DEMO = ["etapa_ingesta_ancha.v", "etapa_features.v", "etapa_puntaje.v",
                "etapa_decision.v", "uart_tx.v", "etapa_salida.v",
                "pipeline_top_ancho.v", "fuente_bram.v", "demo_top.v"]


def bloque_tabla(ts=(1, 2, 8, 16, 64, 240)):
    """VARIANTE 1: un pipeline con tabla de pesos de T instrumentos."""
    print("=" * 92)
    print("3. VARIANTE 1 — UN pipeline con TABLA de pesos de T instrumentos (B=4)")
    print("=" * 92)
    print("   Es la segunda forma de subir el techo, y la que los documentos del")
    print("   proyecto nombran tres veces sin construirla. Un solo DSP48E1 sirve a")
    print("   los T instrumentos; el techo deja de ser una cuenta de DSP y pasa a")
    print("   ser el tamano de la tabla. Referencia contra la que hay que leerlo:")
    print("   K replicado gasta 1 DSP y ~72 LUT6 y 336 FF POR TICKER.")
    print()
    print("   %-5s %5s %7s %7s %7s %6s | %6s %6s %6s"
          % ("T", "DSP", "LUT6", "FF", "CARRY", "BRAM", "%DSP", "%LUT", "%FF"))
    print("   " + "-" * 74)
    medidas = []
    for t in ts:
        r, err = sintetizar("pipeline_top_multi",
                            ["CFG_NF=1", "CFG_PESOS=1", "CFG_B=4", "CFG_T=%d" % t],
                            FUENTES_MULTI)
        if r is None:
            print("   %-5d FALLO: %s" % (t, err))
            continue
        medidas.append((t, r))
        print("   %-5d %5d %7d %7d %7d %6d | %5.2f%% %5.2f%% %5.2f%%"
              % (t, r["dsp"], r["lut"], r["ff"], r["carry"], r["bram"],
                 100.0 * r["dsp"] / A7_DSP, 100.0 * r["lut"] / A7_LUT6,
                 100.0 * r["ff"] / A7_FF))
    if len(medidas) >= 2:
        (t0, r0), (t1, r1) = medidas[0], medidas[-1]
        d = float(t1 - t0)
        print()
        print("   Costo marginal MEDIDO por instrumento en la tabla (T=%d a T=%d):"
              % (t0, t1))
        print("     %.2f LUT6   %.2f FF   %.3f DSP48E1"
              % ((r1["lut"] - r0["lut"]) / d, (r1["ff"] - r0["ff"]) / d,
                 (r1["dsp"] - r0["dsp"]) / d))
    print()
    return medidas


def bloque_demo(bs=(4, 28)):
    """VARIANTE 2: el sistema autonomo con la fuente interna desde memoria."""
    print("=" * 92)
    print("4. VARIANTE 2 — SISTEMA AUTONOMO: fuente interna + pipeline (demo_top)")
    print("=" * 92)
    print("   Reproduce las 181 filas selladas desde memoria del chip. Es lo que")
    print("   hace realizable B=28 (5 ciclos): 28 bytes en paralelo son 224 pines y")
    print("   la placa expone 32 senales por los Pmod. Adentro no hay pines.")
    print("   Ojo con la columna BRAM: hasta hoy TODAS las configuraciones del")
    print("   proyecto daban BRAM=0 (SINTESIS_A7.md §3.1). Esta es la primera que")
    print("   usa memoria de bloque, y por eso se mide en vez de suponerla.")
    print()
    print("   %-24s %5s %7s %7s %7s %7s | %-22s %8s"
          % ("configuracion", "DSP", "LUT6", "FF", "CARRY", "LUT4ice",
             "memoria (primitivas)", "eq.36Kb"))
    print("   " + "-" * 92)
    ref = {}
    for b in bs:
        r, err = sintetizar("pipeline_top_ancho",
                            ["CFG_NF=1", "CFG_PESOS=1", "CFG_B=%d" % b],
                            FUENTES_ANCHO[:-1])
        if r is None:
            print("   %-24s FALLO: %s" % ("pipeline solo B=%d" % b, err))
            continue
        ref[b] = r
        desc, eq36 = memoria(r)
        print("   %-24s %5d %7d %7d %7d %7s | %-22s %7.1f  (%.2f%%)"
              % ("pipeline solo B=%d" % b, r["dsp"], r["lut"], r["ff"],
                 r["carry"], "-", desc, eq36, 100.0 * eq36 / A7_BRAM36))
    for b in bs:
        # La ruta del .hex NO va por -D: `demo_top.v` la elige con un generate
        # por B, y el porque esta escrito ahi.
        defs = ["CFG_NF=1", "CFG_PESOS=1", "CFG_B=%d" % b, "CFG_NMSG=181"]
        r, err = sintetizar("demo_top", defs, FUENTES_DEMO)
        if r is None:
            print("   %-24s FALLO: %s" % ("demo_top B=%d" % b, err))
            continue
        desc, eq36 = memoria(r)
        print("   %-24s %5d %7d %7d %7d %7s | %-22s %7.1f  (%.2f%%)"
              % ("demo_top B=%d" % b, r["dsp"], r["lut"], r["ff"], r["carry"],
                 "-", desc, eq36, 100.0 * eq36 / A7_BRAM36))
        if b in ref:
            print("   %-24s   costo de la fuente: %+d DSP, %+d LUT6, %+d FF, %+.1f bloques de 36Kb"
                  % ("", r["dsp"] - ref[b]["dsp"], r["lut"] - ref[b]["lut"],
                     r["ff"] - ref[b]["ff"], eq36 - memoria(ref[b])[1]))
    print()
    print("   Los +DSP de la fuente NO son el modelo: son las multiplicaciones")
    print("   constantes de la aritmetica de direcciones (idx*N_PAL, idx*6), que")
    print("   yosys mapea a DSP48E1 porque le salen gratis. Con paso 8 serian")
    print("   desplazamientos. Se nombra y no se arregla: arreglarlo cambia el")
    print("   diseno que hoy esta medido.")
    print()


BLOQUES = {"techo": bloque_techo, "sin_dsp": bloque_sin_dsp,
           "tabla": bloque_tabla, "demo": bloque_demo}


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
