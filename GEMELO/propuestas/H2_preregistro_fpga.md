# H2 · Pre-registro del pipeline RTL, con criterio de muerte — PROPUESTA (2-sep-2026)

> **Es del ramo, no de la tesis de MKI** (`tesis.md` §1 Camino 6 y §2).
> Este documento existe para que el trabajo de FPGA tenga, como cada
> frente empírico del proyecto, una pregunta fijada antes, un éxito
> definido antes y una condición de abandono definida antes. Intentos del
> DSR: **0** — no prueba ninguna hipótesis sobre retornos.

## 0. Una cifra que el encargo trae mal, corregida antes de usarla

El encargo cita «un round trip de 8,79 ms» como si fuera una medición de
la placa. **No lo es**: es el p50 de un `connect()` TCP contra
1.1.1.1:443, medido por `bench_red` (`GEMELO/MICRO/piso_de_latencia.md`
§1-2, `micro/resultados/red.json`; p99 = 36,76 ms). Es la cifra que
sentencia que la captura en vivo es **NO VIABLE** (4 órdenes de magnitud
contra colocation), y ninguna placa la cambia. Va acá con esa procedencia
y **no se fusiona con las cifras RTL** (ciclos, LUTs, error de cuantización).

## 1. La pregunta, una sola

> ¿Un pipeline RTL sintetizado reproduce la predicción del modelo 4.6.0
> —signo e intervalo— sobre los vectores sellados, con un error de
> cuantización acotado de antemano y una latencia **determinística**
> contada en ciclos?

Lo que la pregunta NO es: «más rápido que el mercado» (refutado, §0),
«motor de backtesting» (ese encuadre nunca existió: `cola_decisiones.md`
§6), ni «mejora del modelo» (regla cero: `motor.py` intocable).

## 2. Lo que queda fijado antes de sintetizar nada más

1. **Vectores de referencia congelados.** Hoy `referencia.py` regenera
   vectores desde `senales.db` y quedaron **181 congelados contra 189
   sellados** (`espera_firma.md` §10): un pasivo que crece cada noche. Se
   fija UN conjunto: las filas selladas hasta una fecha declarada, su
   SHA-256 escrito acá, y **no se regenera nunca**. Cualquier fila
   posterior es un segundo conjunto con su propia fecha.
2. **Cota de error declarada.** `SINTESIS_A7.md`:538-540 da 0,00474 pp de
   error de cuantización y lo llama «vara independiente»; el guardián lo
   marcó **NO VERIFICADO** (`cola_decisiones.md` §12) porque nadie
   comprobó que las dos rutas no comparten el álgebra. Antes de citar la
   cota: la segunda ruta tiene que ser **otra familia de método** — una
   simulación bit-exacta del RTL contra el `float64` de `motor.py`, no
   el mismo emulador de punto fijo corrido dos veces (regla 1 de la casa).
3. **Éxito:** 100% de coincidencia de signo sobre los vectores congelados,
   |Δ| ≤ cota en el punto y en el ancho del intervalo, y una latencia
   reportada como **ciclos** (y ns al reloj declarado), jamás comparada
   con el mercado.
4. **Aislamiento:** nada del ramo importa de `motor.py` en tiempo de
   síntesis ni escribe en las bases; el test AST que protege al sello
   contra GEMELO se extiende a `GEMELO/MICRO/`.

## 3. Criterio de muerte (se declara ahora, se aplica sin discusión)

El frente se cierra —se archiva con lo que tenga, se declara terminado en
`cola_decisiones.md` y no se reabre sin un pre-registro nuevo— si ocurre
**cualquiera** de estas cosas:

- **M-1 · Plazo.** A los 90 días de instalado Vivado (la cuenta AMD bloquea
  todo, `cola_decisiones.md` §4) el pipeline no pasa el test de vectores
  de la §2.3. La fecha se escribe el día que Vivado corre.
- **M-2 · Contaminación.** Cualquier cifra de MKI (acierto, ventaja, MDE,
  potencia) aparece justificada, citada o «confirmada» por la FPGA. La
  dirección es una sola: el backtest valida al RTL, nunca al revés.
- **M-3 · Alcance.** El trabajo exige tocar `motor.py`, el camino del sello
  o el modo de emisión, o volver a la lectura «captura en vivo».
- **M-4 · Vara compartida.** Se comprueba que las «dos rutas» de la §2.2
  comparten el álgebra y no se construye una segunda ruta real: sin cota
  verificada no hay éxito medible, y un frente sin éxito medible no sigue.

## 4. Lo que decide Nicolás

- La cuenta AMD (bloquea todo; `espera_firma.md` «Los pasos, numerados»).
- La fecha de la §2.1 y con ella el conjunto de vectores.
- Si el ramo vive en este repositorio o aparte (`tesis.md`: «mantenerla
  separada es cuidarla»). Recomendación: **aparte**, con este pre-registro
  como único puente y la fecha de M-1 anotada en los dos lados.
