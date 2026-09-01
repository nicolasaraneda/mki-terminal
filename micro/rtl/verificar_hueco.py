#!/usr/bin/env python3
"""
verificar_hueco.py — el requisito R1 de `GEMELO/MICRO/RTL.md` §7, ejecutable.

QUÉ FIJA
--------
R1 dice que entre dos mensajes tiene que haber al menos DOS ciclos de
silencio, y que por debajo de ese mínimo el diseño produce sellos malos
aunque la latencia siga siendo perfecta. Este script lo verifica en las dos
direcciones, que es lo que separa un requisito de una anécdota:

  A. CONTROL — con el hueco en el mínimo (2), el diseño reproduce las 181
     filas selladas bit a bit y la latencia da el entero predicho.
  B. LA ROTURA — con el hueco por DEBAJO del mínimo (1), la reproducción bit
     a bit se rompe.
  C. EL GUARDIA — sin el bypass explícito, la elaboración aborta antes de
     simular nada.

POR QUÉ B NO ALCANZA CON "FALLA"
--------------------------------
Un test que falla por cualquier razón no prueba nada. Un error de sintaxis,
un archivo de vectores ausente, un timeout de la simulación o el propio
guardia del punto C harían fallar el punto B exactamente igual de rojo, y
ninguno de esos rojos diría nada sobre el hueco. Así que B verifica el MODO
de falla, no el hecho de fallar:

  B1. la compilación tiene que TERMINAR BIEN (si no, no se probó nada);
  B2. la simulación tiene que CORRER ENTERA — 181 sellos recogidos, ningún
      TIMEOUT: si el banco se colgara, los sellos malos no existirían;
  B3. la LATENCIA tiene que seguir siendo la misma y perfectamente
      determinista (min == max == el entero predicho). Esto no es un extra:
      es EL punto. La prueba de rendimiento pasa en verde sobre el diseño
      roto, y este script exige que siga pasando para poder afirmarlo;
  B4. los fallos tienen que ser TODOS del modo del hueco corto: la decisión
      sellada correcta y el puntaje no ("sellos contradictorios" == fallos).
      Cualquier otro reparto significa que se rompió otra cosa.

QUÉ TIENE INTERVALO Y QUÉ NO
----------------------------
Nada de lo que mide este script lo tiene, y la razón es que no hay de dónde
sacarlo: la simulación de Icarus sobre vectores fijos es DETERMINÍSTICA —
no hay semilla, no hay reloj de pared, no hay orden de scheduling que
cambie el resultado — así que 178, 181 y 11 son los mismos números en cada
corrida y un intervalo sobre ellos sería inventado. La cifra de esta pista
que SÍ es variable es el Fmax de nextpnr (105,27 a 114,19 MHz sobre 10
semillas, `make semillas`), y este script no lo toca.

No abre `senales.db` ni ninguna base: consume los vectores ya congelados en
`vectores/`. No escribe nada fuera de `sim/`.
"""

import os
import re
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
DIR_SIM = os.path.join(DIR, "sim")

FUENTES = ["etapa_ingesta_ancha.v", "etapa_features.v", "etapa_puntaje.v",
           "etapa_decision.v", "uart_tx.v", "etapa_salida.v",
           "pipeline_top_ancho.v", "fuente_bram.v", "demo_top.v",
           "tb/tb_demo.v"]

N_CASOS = 181

# PREDICCIONES, escritas acá y no calculadas de la corrida. Vienen de la
# medición del 1-sep-2026 (`GEMELO/MICRO/INGESTA_ANCHA.md` §3.3 y la precisión
# del modo de falla en el encabezado de `fuente_bram.v`). Si el diseño cambia y
# estos números se mueven, este script tiene que fallar y alguien tiene que
# venir a mirar: por eso están cableados y no derivados.
HUECO_MINIMO = 2
HUECO_DEL_BANCO = 8          # el default de `fuente_bram.v`, no el mínimo
FALLOS_ESPERADOS = 178       # de 181, con HUECO 0 o 1, en los dos anchos
CORRIDOS_ESPERADOS = 131     # de los 178: los que además coinciden con k+1


def latencia_predicha(b):
    """ceil(28/B) + 4 — la predicción de `tb/tb_demo.v`, no una medición."""
    return (28 + b - 1) // b + 4


def compilar_y_correr(b, hueco, bypass, etiqueta):
    """Devuelve (rc_compilacion, rc_simulacion, salida)."""
    os.makedirs(DIR_SIM, exist_ok=True)
    vvp_out = os.path.join(DIR_SIM, "tb_huecogate_%s.vvp" % etiqueta)
    cmd = ["iverilog", "-g2012", "-I.", "-Ivectores",
           "-DCFG_B=%d" % b, "-DCFG_HUECO=%d" % hueco]
    if bypass:
        cmd.append("-DCFG_PERMITIR_HUECO_INSEGURO")
    cmd += ["-o", vvp_out] + FUENTES
    try:
        c = subprocess.run(cmd, cwd=DIR, capture_output=True, text=True,
                           timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, 127, "no se pudo compilar: %s" % e
    if c.returncode != 0:
        return c.returncode, 127, (c.stdout or "") + (c.stderr or "")
    try:
        s = subprocess.run(["vvp", vvp_out], cwd=DIR, capture_output=True,
                           text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 0, 127, "no se pudo simular: %s" % e
    return 0, s.returncode, (s.stdout or "") + (s.stderr or "")


def entero(salida, patron):
    m = re.search(patron, salida)
    return int(m.group(1)) if m else None


def leer(salida):
    return {
        "vistos": entero(salida, r"sellos recogidos\s*:\s*(\d+)"),
        "fallos": entero(salida, r"fallos bit a bit\s*:\s*(\d+)"),
        "corridos": entero(salida, r"sellos corridos \+1\s*:\s*(\d+)"),
        "contradictorios": entero(salida, r"sellos contradictorios\s*:\s*(\d+)"),
        "lat_min": entero(salida, r"latencia DUT min/max\s*:\s*(\d+) /"),
        "lat_max": entero(salida, r"latencia DUT min/max\s*:\s*\d+ / (\d+)"),
        "timeout": "TIMEOUT" in salida,
    }


def main():
    os.environ["PATH"] = (os.path.expanduser("~/.local/opt/oss-cad-suite/bin")
                          + os.pathsep + os.environ.get("PATH", ""))
    fallas = []

    def exigir(cond, texto):
        print("    %-5s %s" % ("OK" if cond else "FALLA", texto))
        if not cond:
            fallas.append(texto)

    print("=== R1 de RTL.md §7: el hueco mínimo entre mensajes ===")
    print("    predicciones cableadas ANTES de correr:")
    print("      minimo seguro = %d ciclos; el banco usa %d por default"
          % (HUECO_MINIMO, HUECO_DEL_BANCO))
    print("      por debajo del minimo: %d de %d sellos mal, %d de ellos"
          % (FALLOS_ESPERADOS, N_CASOS, CORRIDOS_ESPERADOS))
    print("      corridos al caso k+1, y la LATENCIA INTACTA")
    print("    todas estas cifras son deterministas (simulacion sobre vectores")
    print("    fijos, sin semilla): no llevan intervalo, y se dice a proposito.")

    for b in (4, 28):
        lat = latencia_predicha(b)

        # --- A. CONTROL: en el mínimo, todo bien -----------------------------
        print("")
        print("  [A] B=%d, HUECO=%d (el minimo) — sin bypass" % (b, HUECO_MINIMO))
        rc_c, rc_s, out = compilar_y_correr(b, HUECO_MINIMO, False, "a_b%d" % b)
        d = leer(out)
        exigir(rc_c == 0, "compila")
        exigir(rc_s == 0, "la simulacion termina bien")
        exigir(d["vistos"] == N_CASOS, "recoge los %d sellos" % N_CASOS)
        exigir(d["fallos"] == 0, "0 fallos bit a bit")
        exigir(d["lat_min"] == lat and d["lat_max"] == lat,
               "latencia %d/%d ciclos, determinista" % (lat, lat))

        # --- B. LA ROTURA, y por la razón correcta ---------------------------
        inseguro = HUECO_MINIMO - 1
        print("  [B] B=%d, HUECO=%d (bajo el minimo) — con bypass explicito"
              % (b, inseguro))
        rc_c, rc_s, out = compilar_y_correr(b, inseguro, True, "b_b%d" % b)
        d = leer(out)
        # B1: si no compiló, no se probó nada.
        exigir(rc_c == 0, "B1 compila (si no, el rojo no diria nada del hueco)")
        # B2: tiene que haber corrido entera.
        exigir(not d["timeout"], "B2 no hay TIMEOUT")
        exigir(d["vistos"] == N_CASOS,
               "B2 la simulacion corre entera: %s sellos recogidos" % d["vistos"])
        # La rotura en sí.
        exigir(d["fallos"] == FALLOS_ESPERADOS,
               "la reproduccion bit a bit SE ROMPE: %s fallos (predicho %d)"
               % (d["fallos"], FALLOS_ESPERADOS))
        exigir(rc_s != 0, "el banco marca FALLA (codigo de salida distinto de 0)")
        # B3: el rendimiento sigue verde. Este es el punto del requisito.
        exigir(d["lat_min"] == lat and d["lat_max"] == lat,
               "B3 la LATENCIA sigue en %d/%d, determinista, con %s sellos mal"
               % (lat, lat, d["fallos"]))
        # B4: el modo de falla es el del hueco corto y ningun otro.
        exigir(d["contradictorios"] == d["fallos"],
               "B4 los %s fallos son TODOS del modo esperado (decision correcta,"
               " puntaje del peso de k+1)" % d["fallos"])
        exigir(d["corridos"] == CORRIDOS_ESPERADOS,
               "B4 %s de ellos coinciden ademas con el sello de k+1 (predicho %d)"
               % (d["corridos"], CORRIDOS_ESPERADOS))

        # --- C. EL GUARDIA ---------------------------------------------------
        print("  [C] B=%d, HUECO=%d — SIN bypass: tiene que abortar" % (b, inseguro))
        rc_c, rc_s, out = compilar_y_correr(b, inseguro, False, "c_b%d" % b)
        exigir(rc_c == 0, "compila (el guardia es de elaboracion, no de sintaxis)")
        exigir(rc_s != 0, "aborta")
        exigir("fuente_bram: HUECO=" in out, "y aborta CON el mensaje del guardia")
        exigir(leer(out)["vistos"] is None, "sin recoger un solo sello")

    print("")
    if fallas:
        print("VEREDICTO: FALLA — %d comprobaciones" % len(fallas))
        for f in fallas:
            print("    - %s" % f)
        return 1
    print("VEREDICTO: OK — R1 se sostiene en B=4 y B=28, y el diseño se rompe")
    print("           por la razon declarada, no por otra.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
