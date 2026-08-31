#!/usr/bin/env python3
"""
referencia.py — modelo de referencia del pipeline RTL y generador de vectores.

QUÉ ES Y QUÉ NO ES
------------------
Es una reimplementación AISLADA del álgebra que el RTL sintetiza. NO importa
`motor.py` ni ningún módulo del árbol de producción: RTL.md §4.2 lo prohíbe
explícitamente porque importarlo violaría la Regla Cero (motor.py intocable) y,
peor, haría que el "modelo de referencia" y el "sistema bajo prueba"
compartieran los mismos errores — que es exactamente lo que una referencia no
puede hacer.

`senales.db` se abre SIEMPRE en modo `ro`. Este archivo no escribe una sola
fila en ninguna base del proyecto.

EL ÁLGEBRA QUE SE REPLICA
-------------------------
El modelo campeón 4.6.0 es una sola combinación lineal SIN INTERCEPTO:

    apertura_estimada_pct = beta x ultimo_movimiento_no_cero_del_SOX

donde beta sale de una regresión rodante de 120 días hábiles. El intercepto
alfa de esa regresión se usa para calcular residuos, pero NO entra en la
predicción. Por eso F=1 en el RTL no es un caso degenerado de juguete: es
literalmente el campeón, una multiplicación.

DOS MODELOS, A PROPÓSITO
------------------------
  - `modelo_flotante`: float64, la "verdad de referencia" de RTL.md §4.2.
  - `modelo_entero`:   réplica BIT A BIT de la semántica del RTL (truncados,
                       anchos, envolvimientos y saturación incluidos).

Tener los dos es lo que separa dos preguntas que se confunden todo el tiempo:
"¿el RTL hace lo que creo que hace?" (RTL == modelo_entero, exacto) y "¿lo que
creo que hace se parece al álgebra real?" (modelo_entero vs modelo_flotante,
dentro de la tolerancia DECLARADA ANTES). Si solo hubiera un modelo y algo
fallara, no se sabría cuál de las dos preguntas falló.
"""

import csv
import os
import sqlite3
import sys
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BD = os.path.join(RAIZ, "senales.db")
DIR_VEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectores")

# --- Formatos de punto fijo (justificados en RTL.md §3 con datos medidos) ---
FRAC_FEATURE = 8    # Q8.8
FRAC_PESO = 14      # Q2.14
ANCHO = 16
MIN16, MAX16 = -(1 << 15), (1 << 15) - 1

# --- Parámetros del pipeline, iguales a los del RTL ---
N_VENTANA = 10
RECIPROCO_Q16 = 6554          # round(65536/10); el exacto es 6553.6
UMBRAL_ALZA = 128             # Q8.8 = +0.50 pp
UMBRAL_BAJA = -128            # Q8.8 = -0.50 pp
MANTENER, VENTA, COMPRA = 0, 1, 2

# Pesos de las features 1..5, DECLARADOS ACÁ Y ANTES DE CORRER NADA.
# Son arbitrarios a propósito: F>1 existe para medir cómo escala el ÁREA en la
# FPGA (RTL.md §2), no para afirmar que el modelo mejora con más features. El
# proyecto ya publicó en GEMELO/WS2b que agregar features no mejoró nada de
# forma detectable; inventar acá una ganancia sería contradecir su propio
# resultado negativo. Se eligen valores que no son potencias de dos para que
# nadie sospeche que el sintetizador podó una multiplicación (no puede: los
# pesos son registros cargados en tiempo de ejecución, no constantes).
PESOS_EXTRA = [0.3125, -0.1875, 0.1250, -0.0625, 0.0313]


# ----------------------------------------------------------------------------
# Aritmética de punto fijo. Cada función replica una construcción concreta de
# Verilog; el nombre dice cuál.
# ----------------------------------------------------------------------------

def a_q88(x):
    """float -> Q8.8 con saturación (redondeo al más cercano, en el generador)."""
    q = int(round(x * (1 << FRAC_FEATURE)))
    return max(MIN16, min(MAX16, q))


def a_q214(x):
    """float -> Q2.14 con saturación."""
    q = int(round(x * (1 << FRAC_PESO)))
    return max(MIN16, min(MAX16, q))


def de_q88(q):
    return q / float(1 << FRAC_FEATURE)


def de_q214(q):
    return q / float(1 << FRAC_PESO)


def con_signo(valor, bits):
    """Interpreta los `bits` bits bajos de `valor` como entero con signo.

    Replica un truncamiento de ancho en Verilog (`x[N-1:0]` sobre un `reg
    signed`), que envuelve. No es lo mismo que saturar y por eso está separado
    de `saturar16`.
    """
    mascara = (1 << bits) - 1
    v = valor & mascara
    if v & (1 << (bits - 1)):
        v -= (1 << bits)
    return v


def desplazar_aritmetico(valor, n):
    """`>>>` de Verilog sobre un operando con signo.

    En Python `>>` sobre un entero negativo ya trunca hacia -infinito, que es
    exactamente lo que hace un desplazamiento aritmético en hardware. Se
    envuelve en una función igual para que el nombre diga la intención y nadie
    "arregle" el sesgo con un round() bienintencionado — ese sesgo es real y
    está medido.
    """
    return valor >> n


# ----------------------------------------------------------------------------
# El pipeline, replicado etapa por etapa
# ----------------------------------------------------------------------------

class ModeloEntero:
    """Réplica bit a bit del RTL, incluido el estado de la ventana rodante.

    El estado importa: la etapa 2 es la única con memoria, así que el resultado
    de un mensaje depende de los N_VENTANA anteriores. El banco de pruebas
    alimenta el DUT con el mismo stream y en el mismo orden — si no, la
    comparación no significaría nada.
    """

    def __init__(self, n_features, usar_pesos=True, n_ventana=N_VENTANA):
        self.n_features = n_features
        self.usar_pesos = usar_pesos
        self.n_ventana = n_ventana
        # Tras el reset la ventana está en cero. Los primeros n_ventana-1
        # mensajes tienen media sesgada hacia abajo. NO se corrige (ver el
        # comentario de calentamiento en etapa_features.v); se replica.
        self.ventana = [0] * n_ventana
        self.suma = 0
        self.w_suma = ANCHO + 5

    def features(self, f):
        """Etapa 2. `f` son las seis features empaquetadas del mensaje, en Q8.8."""
        f0 = f[0]
        # media = (suma * RECIPROCO_Q16) >>> 16, quedándose con 16 bits.
        # El bit-slice producto_media[31:16] del Verilog envuelve; se replica
        # con con_signo en vez de suponer que nunca desborda.
        producto = self.suma * RECIPROCO_Q16
        media = con_signo(desplazar_aritmetico(producto, 16), ANCHO)

        g = [0] * 6
        g[0] = f0
        # La resta de 16 bits del Verilog envuelve (el puerto es de 16 bits sin
        # saturación). Se replica el envolvimiento, no una versión "arreglada".
        g[1] = con_signo(f0 - media, ANCHO)
        g[2] = f[1]
        g[3] = f[2]
        g[4] = f[3]
        g[5] = f[4]

        # Actualización de la suma corrida: entra f0, sale el más viejo.
        sale = self.ventana[self.n_ventana - 1]
        self.suma = con_signo(self.suma + f0 - sale, self.w_suma)
        self.ventana = [f0] + self.ventana[:-1]
        return g

    def puntaje(self, g, w):
        """Etapa 3. Devuelve (puntaje_q88, saturo)."""
        prods = []
        for j in range(6):
            if j < self.n_features:
                if self.usar_pesos:
                    prods.append(con_signo(g[j] * w[j], ANCHO * 2))
                else:
                    prods.append(con_signo(g[j] << FRAC_PESO, ANCHO * 2))
            else:
                prods.append(0)
        acumulado = con_signo(sum(prods), ANCHO * 2 + 3)
        desplazado = desplazar_aritmetico(acumulado, FRAC_PESO)
        if desplazado > MAX16:
            return MAX16, True
        if desplazado < MIN16:
            return MIN16, True
        return desplazado, False

    @staticmethod
    def decision(puntaje_q88):
        """Etapa 4. Comparación ESTRICTA: el empate exacto cae en MANTENER."""
        if puntaje_q88 > UMBRAL_ALZA:
            return COMPRA
        if puntaje_q88 < UMBRAL_BAJA:
            return VENTA
        return MANTENER

    def procesar(self, f, w):
        g = self.features(f)
        p, sat = self.puntaje(g, w)
        return g, p, sat, self.decision(p)


class ModeloFlotante:
    """La misma álgebra en float64. La 'verdad de referencia' de RTL.md §4.2."""

    def __init__(self, n_features, usar_pesos=True, n_ventana=N_VENTANA):
        self.n_features = n_features
        self.usar_pesos = usar_pesos
        self.n_ventana = n_ventana
        self.ventana = [0.0] * n_ventana

    def procesar(self, f, w):
        """`f` y `w` acá vienen en float, sin cuantizar."""
        media = sum(self.ventana) / float(self.n_ventana)
        g = [f[0], f[0] - media, f[1], f[2], f[3], f[4]]
        self.ventana = [f[0]] + self.ventana[:-1]
        if self.usar_pesos:
            p = sum(g[j] * w[j] for j in range(self.n_features))
        else:
            p = sum(g[j] for j in range(self.n_features))
        umbral = UMBRAL_ALZA / float(1 << FRAC_FEATURE)
        if p > umbral:
            d = COMPRA
        elif p < -umbral:
            d = VENTA
        else:
            d = MANTENER
        return g, p, d


# ----------------------------------------------------------------------------
# Datos reales: reconstrucción del insumo del modelo desde las filas selladas
# ----------------------------------------------------------------------------

def cargar_filas_selladas():
    """Lee `senales.db` en modo ro. Nunca escribe.

    Devuelve las filas con beta y apertura no nulas, ordenadas de forma
    determinista para que el stream del banco de pruebas sea reproducible.
    """
    if not os.path.exists(BD):
        raise SystemExit("no existe %s — no se puede generar el vector real" % BD)
    con = sqlite3.connect("file:%s?mode=ro" % BD, uri=True)
    filas = list(con.execute("""
        SELECT s.fecha, s.ticker, s.apertura_estimada_pct, s.beta,
               s.intervalo80_pp, s.n_muestra, s.modelo_version, v.gap_pct
          FROM senales_ticker s
          LEFT JOIN verificacion_apertura v
                 ON v.fecha_senal = s.fecha AND v.ticker = s.ticker
         WHERE s.beta IS NOT NULL
           AND s.apertura_estimada_pct IS NOT NULL
         ORDER BY s.fecha, s.ticker
    """))
    con.close()
    return filas


def sox_por_fecha(filas):
    """Recupera el movimiento del SOX que originó cada día de predicciones.

    Es un despeje, no una fuente nueva: si apertura = beta x sox para TODOS los
    tickers de una fecha, entonces sox = apertura/beta para cada uno y los
    valores tienen que coincidir. Coinciden salvo por el redondeo con que la
    base guarda apertura y beta (dos decimales cada uno), que para betas chicas
    infla el error relativo — beta=0.08 con apertura redondeada a 0.01 ya
    arrastra un 6%.

    Por eso NO se promedia: se estima por mínimos cuadrados por el origen,
      sox = sum(a_i b_i) / sum(b_i^2),
    que pondera por beta^2 y deja que las betas grandes —las de menor error
    relativo— manden. El desacuerdo residual entre tickers se reporta como
    diagnóstico en vez de esconderse: es la evidencia de que el despeje es
    correcto, y su tamaño es una cota del ruido de redondeo de la base.
    """
    por_fecha = defaultdict(list)
    for fecha, ticker, ap, beta, _i, _n, _mv, _g in filas:
        por_fecha[fecha].append((ap, beta))

    sox, diagnostico = {}, {}
    for fecha, pares in por_fecha.items():
        num = sum(a * b for a, b in pares)
        den = sum(b * b for a, b in pares)
        est = num / den if den > 0 else 0.0
        implicitos = [a / b for a, b in pares if abs(b) > 1e-9]
        sox[fecha] = est
        diagnostico[fecha] = {
            "n": len(pares),
            "estimado": est,
            "min_implicito": min(implicitos) if implicitos else None,
            "max_implicito": max(implicitos) if implicitos else None,
            "dispersion": (max(implicitos) - min(implicitos)) if implicitos else None,
        }
    return sox, diagnostico


def construir_casos():
    """Arma el stream de casos: un mensaje de 28 bytes por fila sellada."""
    filas = cargar_filas_selladas()
    sox, diag = sox_por_fecha(filas)
    fechas = sorted(sox.keys())
    idx_fecha = {f: i for i, f in enumerate(fechas)}
    tickers = sorted({r[1] for r in filas})
    idx_ticker = {t: i for i, t in enumerate(tickers)}

    casos = []
    for fecha, ticker, ap, beta, inter, n, mv, gap in filas:
        i = idx_fecha[fecha]
        # f0 es el insumo REAL del modelo campeón: el movimiento del SOX
        # conocido al emitir. f1..f4 son el mismo movimiento REZAGADO 1..4
        # sesiones — datos reales y causales (ya conocidos en la fecha de
        # emisión), no ruido inventado. Antes del inicio de la serie el rezago
        # es 0.0, que es lo que un acumulador recién reseteado ve de todos
        # modos.
        rezagos = [sox[fechas[i - k]] if i - k >= 0 else 0.0 for k in range(1, 5)]
        f_float = [sox[fecha]] + rezagos + [0.0]
        w_float = [beta] + PESOS_EXTRA
        casos.append({
            "fecha": fecha, "ticker": ticker,
            "id_instrumento": idx_ticker[ticker],
            "apertura_sellada": ap, "beta": beta,
            "intervalo80_pp": inter, "n_muestra": n,
            "modelo_version": mv, "gap_pct": gap,
            "f_float": f_float, "w_float": w_float,
            "f_q88": [a_q88(x) for x in f_float],
            "w_q214": [a_q214(x) for x in w_float],
        })
    return casos, diag, fechas, tickers


# ----------------------------------------------------------------------------
# Serialización al formato de wire de 28 bytes
# ----------------------------------------------------------------------------

def empaquetar_mensaje(caso, ts_ns):
    """Arma los 28 bytes little-endian del formato de `bench_mensaje.c`.

    El FORMATO no se tocó: sigue siendo ts_ns u64 / id u32 / precio_fp i64 /
    cantidad i32 / lado u8 / flags u8 / reservado u16, en las mismas
    posiciones. Lo que cambia es qué SIGNIFICA el payload en este vector de
    validación: `precio_fp` transporta cuatro features Q8.8 empaquetadas y
    `cantidad` otras dos. Está declarado acá y en micro/TOOLCHAIN.md; no es un
    formato nuevo escondido dentro de uno viejo.
    """
    f = caso["f_q88"]
    u16 = lambda v: v & 0xFFFF
    precio = (u16(f[0]) | (u16(f[1]) << 16) | (u16(f[2]) << 32) | (u16(f[3]) << 48))
    cantidad = (u16(f[4]) | (u16(f[5]) << 16))

    b = bytearray(28)
    b[0:8] = ts_ns.to_bytes(8, "little")
    b[8:12] = caso["id_instrumento"].to_bytes(4, "little")
    b[12:20] = precio.to_bytes(8, "little")
    b[20:24] = cantidad.to_bytes(4, "little")
    b[24] = 0            # lado: sin uso en este pipeline, se sella en 0
    b[25] = 0            # flags: idem
    b[26:28] = (0).to_bytes(2, "little")
    return bytes(b)


# ----------------------------------------------------------------------------
# Generación de los archivos que consume el banco de pruebas
# ----------------------------------------------------------------------------

CONFIGURACIONES = [
    ("F1", 1, True),
    ("F3", 3, True),
    ("F6", 6, True),
    ("F1SP", 1, False),   # sin pesos: la variante "solo umbral" de RTL.md §2
]


def generar():
    os.makedirs(DIR_VEC, exist_ok=True)
    casos, diag, fechas, tickers = construir_casos()
    n = len(casos)

    # --- mensajes.hex: 28 bytes por caso, un byte por línea ---
    with open(os.path.join(DIR_VEC, "mensajes.hex"), "w") as fh:
        for k, c in enumerate(casos):
            for byte in empaquetar_mensaje(c, ts_ns=k * 1000):
                fh.write("%02x\n" % byte)

    # --- pesos.hex: 6 palabras de 16 bits por caso ---
    with open(os.path.join(DIR_VEC, "pesos.hex"), "w") as fh:
        for c in casos:
            for w in c["w_q214"]:
                fh.write("%04x\n" % (w & 0xFFFF))

    # --- esperado_<cfg>.hex y el CSV legible ---
    resumen = {}
    for nombre, nf, usar_pesos in CONFIGURACIONES:
        ent = ModeloEntero(nf, usar_pesos)
        flo = ModeloFlotante(nf, usar_pesos)
        filas_csv, saturaciones = [], 0
        peor_abs, peor_caso = 0.0, None
        discrepancias_decision = 0

        with open(os.path.join(DIR_VEC, "esperado_%s.hex" % nombre), "w") as fh:
            for c in casos:
                g_e, p_e, sat, d_e = ent.procesar(c["f_q88"], c["w_q214"])
                w_f = c["w_float"] if usar_pesos else [1.0] * 6
                g_f, p_f, d_f = flo.procesar(c["f_float"], w_f)

                # {decision[1:0], puntaje[15:0]} en una palabra de 32 bits: el
                # banco de pruebas verifica las dos cosas de una sola lectura.
                fh.write("%08x\n" % ((d_e << 16) | (p_e & 0xFFFF)))

                err = abs(de_q88(p_e) - p_f)
                if err > peor_abs:
                    peor_abs, peor_caso = err, (c["fecha"], c["ticker"])
                if sat:
                    saturaciones += 1
                if d_e != d_f:
                    discrepancias_decision += 1

                filas_csv.append({
                    "fecha": c["fecha"], "ticker": c["ticker"],
                    "id_instrumento": c["id_instrumento"],
                    "beta": c["beta"], "sox_estimado": c["f_float"][0],
                    "apertura_sellada": c["apertura_sellada"],
                    "puntaje_entero_q88": p_e,
                    "puntaje_entero_pp": round(de_q88(p_e), 6),
                    "puntaje_flotante_pp": round(p_f, 6),
                    "error_abs_pp": round(err, 8),
                    "decision_entero": d_e, "decision_flotante": d_f,
                    "saturo": int(sat),
                })

        with open(os.path.join(DIR_VEC, "casos_%s.csv" % nombre), "w", newline="") as fh:
            wcsv = csv.DictWriter(fh, fieldnames=list(filas_csv[0].keys()))
            wcsv.writeheader()
            wcsv.writerows(filas_csv)

        resumen[nombre] = {
            "n": n, "n_features": nf, "usar_pesos": usar_pesos,
            "error_max_pp": peor_abs, "peor_caso": peor_caso,
            "saturaciones": saturaciones,
            "discrepancias_decision": discrepancias_decision,
            "filas": filas_csv,
        }

    # --- parametros.vh: el banco de pruebas no debe hardcodear el conteo ---
    with open(os.path.join(DIR_VEC, "parametros.vh"), "w") as fh:
        fh.write("// Generado por referencia.py. No editar a mano.\n")
        fh.write("`define N_CASOS %d\n" % n)
        fh.write("`define N_VENTANA %d\n" % N_VENTANA)
        fh.write("`define RECIPROCO_Q16 %d\n" % RECIPROCO_Q16)

    return casos, diag, resumen, fechas, tickers


def main():
    casos, diag, resumen, fechas, tickers = generar()
    print("=== vectores generados desde senales.db (modo ro) ===")
    print("  casos (filas selladas con beta y apertura): %d" % len(casos))
    print("  fechas: %d   tickers: %d" % (len(fechas), len(tickers)))
    print()

    print("--- diagnóstico del despeje del SOX ---")
    print("  (dispersión = desacuerdo entre tickers del mismo día; es ruido de")
    print("   redondeo de la base, no del modelo — ver docstring de sox_por_fecha)")
    disp = [d["dispersion"] for d in diag.values() if d["dispersion"] is not None]
    print("  dispersión máxima sobre %d fechas: %.5f pp" % (len(diag), max(disp)))
    print("  dispersión mediana: %.5f pp" % sorted(disp)[len(disp) // 2])
    print()

    print("--- cuantización: entero vs flotante, por configuración ---")
    for nombre, r in resumen.items():
        print("  %-5s F=%d pesos=%-5s  err_max=%.6f pp  saturaciones=%d  "
              "decisiones_distintas=%d"
              % (nombre, r["n_features"], r["usar_pesos"],
                 r["error_max_pp"], r["saturaciones"],
                 r["discrepancias_decision"]))
        if r["peor_caso"]:
            print("        peor caso: %s %s" % r["peor_caso"])

    # --- Contraste contra la fila sellada, que es la prueba que de verdad
    # importa para F=1: ¿el pipeline reproduce la predicción publicada? ---
    r1 = resumen["F1"]
    errs = [abs(f["puntaje_entero_pp"] - f["apertura_sellada"]) for f in r1["filas"]]
    signos = sum(1 for f in r1["filas"]
                 if (f["puntaje_entero_pp"] > 0) != (f["apertura_sellada"] > 0)
                 and abs(f["apertura_sellada"]) > 0.005)
    print()
    print("--- F=1 contra la predicción SELLADA (apertura_estimada_pct) ---")
    print("  n = %d" % len(errs))
    print("  error absoluto máximo : %.6f pp" % max(errs))
    print("  error absoluto medio  : %.6f pp" % (sum(errs) / len(errs)))
    print("  cambios de signo      : %d" % signos)
    print("  NOTA: la base guarda apertura y beta con DOS DECIMALES. El piso de")
    print("  reproducibilidad no es la aritmética del RTL sino el redondeo de la")
    print("  propia base: +-0.005 pp, MAS GRUESO que el LSB de Q8.8 (0.0039 pp).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
