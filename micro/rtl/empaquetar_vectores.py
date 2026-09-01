#!/usr/bin/env python3
"""
empaquetar_vectores.py — re-empaqueta `vectores/mensajes.hex` (un byte por
línea) en palabras de B bytes, para la fuente interna desde BRAM.

NO TOCA `senales.db` NI GENERA VECTORES NUEVOS. Lee el archivo de bytes que
`referencia.py` ya produjo el 31-ago y lo re-agrupa; los 181 casos y sus
valores son exactamente los mismos. Esa separación es deliberada: regenerar
los vectores movería el denominador de 181 a 189 y con eso todas las tablas
publicadas en `SINTESIS.md` y `SINTESIS_A7.md` (declarado en §5 de ese
documento). Este script no tiene forma de hacer eso ni siquiera por error:
no importa `sqlite3` ni `referencia`.

Little-endian dentro de la palabra: el byte de índice más bajo del mensaje va
en los bits menos significativos, que es como `etapa_ingesta_ancha.v` lee
`palabra_dato[bl*8 +: 8]` y como el banco de pruebas ya lo alimentaba. Si esto
se invierte, los 181 vectores dejan de reproducir — o sea que el formato queda
verificado por la simulación, no por este comentario.
"""

import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
VEC = os.path.join(DIR, "vectores")
BYTES_MSG = 28


def leer_bytes(ruta):
    with open(ruta) as f:
        return [int(l.strip(), 16) for l in f if l.strip()]


def empaquetar(b):
    crudo = leer_bytes(os.path.join(VEC, "mensajes.hex"))
    if len(crudo) % BYTES_MSG:
        raise SystemExit("mensajes.hex no es multiplo de %d bytes" % BYTES_MSG)
    n_msg = len(crudo) // BYTES_MSG
    n_pal = -(-BYTES_MSG // b)
    nib = 2 * b
    salida = []
    for k in range(n_msg):
        msg = crudo[k * BYTES_MSG:(k + 1) * BYTES_MSG]
        for wi in range(n_pal):
            palabra = 0
            for bl in range(b):
                idx = wi * b + bl
                if idx < BYTES_MSG:
                    palabra |= msg[idx] << (8 * bl)
            salida.append("%0*x" % (nib, palabra))
    ruta = os.path.join(VEC, "mensajes_b%d.hex" % b)
    with open(ruta, "w") as f:
        f.write("\n".join(salida) + "\n")
    return ruta, n_msg, n_pal


def main():
    anchos = [int(a) for a in sys.argv[1:]] or [4, 28]
    for b in anchos:
        ruta, n_msg, n_pal = empaquetar(b)
        print("B=%-3d %d mensajes x %d palabras de %d bits -> %s"
              % (b, n_msg, n_pal, 8 * b, os.path.relpath(ruta, DIR)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
