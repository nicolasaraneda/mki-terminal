#!/usr/bin/env python3
"""
medir_ancho_error.py — ¿qué compra ensanchar el punto fijo? (B3a)

LA PREGUNTA, BIEN PLANTEADA
---------------------------
`GEMELO/MICRO/RTL.md` §3 midió que cuantizar a Q8.8 introduce un error máximo
de 0,00188 pp, que es el 0,063% del MAE publicado del gap (2,98 pp). El encargo
pedía "subir el ancho hasta que esa pérdida desaparezca".

Antes de subir nada hay que preguntarse contra QUÉ desaparecería. Hay dos
referencias posibles y dan respuestas opuestas:

  (1) contra el álgebra en float64  -> el error baja con cada bit, sin piso;
  (2) contra la fila SELLADA        -> hay un piso que NINGÚN ancho cruza,
      porque `senales.db` guarda `apertura_estimada_pct` y `beta` con DOS
      DECIMALES. Ese redondeo vale +-0,005 pp y es MÁS GRUESO que el LSB de
      Q8.8 (0,0039 pp). El dato de referencia ya está cuantizado más grueso
      que el hardware que se lo compara.

Éste es el mismo argumento que `SINTESIS.md` §5 ya había encontrado por otro
camino, y acá se mide de frente: se barre el ancho y se muestran las dos
curvas juntas.

Se abre `senales.db` en modo `ro` y se reutiliza el cargador de datos de
`referencia.py` (no se duplica la lectura). La aritmética de F=1 sí se
reimplementa acá —es UNA multiplicación con desplazamiento— porque
`referencia.ModeloEntero` está fijado en 16 bits a propósito y ensancharlo
movería el modelo con el que se validaron las 181 filas publicadas.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import referencia  # noqa: E402


# (etiqueta, ancho feature, frac feature, ancho peso, frac peso)
FORMATOS = [
    ("Q8.8 / Q2.14   (HOY)", 16, 8, 16, 14),
    ("Q10.10 / Q2.18",       20, 10, 20, 18),
    ("Q12.12 / Q2.22",       24, 12, 24, 22),
    ("Q14.14 / Q2.26",       28, 14, 28, 26),
    ("Q16.16 / Q2.30",       32, 16, 32, 30),
]

# Resolución con que senales.db guarda apertura_estimada_pct y beta: los dos
# campos salen de un round(x, 2) en motor.py. El error de almacenamiento es
# por lo tanto de hasta media unidad del último decimal.
PISO_BASE_PP = 0.005


def cuantizar(x, frac, ancho):
    q = int(round(x * (1 << frac)))
    lo, hi = -(1 << (ancho - 1)), (1 << (ancho - 1)) - 1
    return max(lo, min(hi, q))


def main():
    filas = referencia.cargar_filas_selladas()
    sox, _diag = referencia.sox_por_fecha(filas)

    casos = []
    for fecha, ticker, ap, beta, _i, _n, _mv, _g in filas:
        casos.append((fecha, ticker, sox[fecha], beta, ap))

    print("=== Ensanchar el punto fijo: qué mejora y qué no (F=1, beta x SOX) ===")
    print("    n = %d filas selladas con beta y apertura (senales.db, modo ro)" % len(casos))
    print()
    print("    Columna A: error del entero contra el ÁLGEBRA en float64.")
    print("    Columna B: error del entero contra la FILA SELLADA de la base.")
    print("    La base guarda ambos campos con 2 decimales: piso de +-%.3f pp."
          % PISO_BASE_PP)
    print()
    print("    %-22s %6s %12s %12s | %12s %12s %8s"
          % ("formato", "LSB", "A: max pp", "A: medio pp",
             "B: max pp", "B: medio pp", "signos"))
    print("    " + "-" * 96)

    for etiqueta, wf, ff, wp, fp in FORMATOS:
        err_a, err_b, signos = [], [], 0
        for _fecha, _ticker, s, beta, ap in casos:
            qs = cuantizar(s, ff, wf)
            qb = cuantizar(beta, fp, wp)
            # producto en Q(ff+fp), de vuelta a Q(ff) por desplazamiento
            # aritmético — la misma semántica de etapa_puntaje.v (truncado).
            p_ent = (qs * qb) >> fp
            p_pp = p_ent / float(1 << ff)
            err_a.append(abs(p_pp - s * beta))
            err_b.append(abs(p_pp - ap))
            if (p_pp > 0) != (ap > 0) and abs(ap) > PISO_BASE_PP:
                signos += 1
        lsb = 1.0 / (1 << ff)
        print("    %-22s %6.5f %12.6f %12.6f | %12.6f %12.6f %8d"
              % (etiqueta, lsb, max(err_a), sum(err_a) / len(err_a),
                 max(err_b), sum(err_b) / len(err_b), signos))

    print()
    print("    LECTURA: la columna A baja con cada bit — es lo que uno espera.")
    print("    La columna B se ESTANCA: no hay ancho que la baje, porque el que")
    print("    manda ahi no es el hardware sino el redondeo a dos decimales de la")
    print("    propia base. Ensanchar el punto fijo mejora la fidelidad contra un")
    print("    algebra que nadie sello, y no mejora la fidelidad contra lo que si")
    print("    se sello. Ver GEMELO/MICRO/SINTESIS_A7.md §4.4.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
