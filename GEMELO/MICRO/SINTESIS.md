# El pipeline RTL, sintetizado — números reales y qué le erró la estimación

**Fecha:** 31-ago-2026. **Estado:** medido. Ya no es diseño.
**Insumo:** `GEMELO/MICRO/RTL.md` (el diseño en papel, con su tabla de
estimaciones §2). **Herramientas:** yosys 0.68+136, nextpnr-0.11.1,
Icarus Verilog 14.0 — todo sin root, ver `micro/TOOLCHAIN.md`.
**Código:** `micro/rtl/`. **Reproducible con:** `cd micro/rtl && make`.

> **Regla cero de este documento, heredada de `RTL.md`:** ninguna cifra se
> ajustó para que el pipeline quepa. Se midió qué exige y se comparó contra lo
> que hay. No entra, y eso es el resultado.

---

## 0. Resumen ejecutivo

1. **El RTL reproduce la referencia en el 100% de los casos** — 181 filas
   selladas reales de `senales.db`, en las cuatro configuraciones, bit a bit.
2. **La latencia es determinista: 32 ciclos, idénticos en los 181 vectores y
   en las cuatro configuraciones.** Es la predicción falsable de `fpga.md` §2
   y sobrevivió.
3. **El modelo campeón (F=1, `beta x SOX`) NO CABE en la Go Board.** Necesita
   1.545 celdas lógicas y el iCE40HX1K tiene 1.280. Sobran 265 (121% de la
   capacidad). `RTL.md` §2 decía que F=1 "cabe cómodo, deja 60-75% de margen"
   — se equivocó, y la §3 de acá explica exactamente por qué.
4. **La estimación de "+200 a +300 LUTs por multiplicador" está subestimada
   entre 2,6 y 3,9 veces.** Un multiplicador 16x16 con signo cuesta **774
   LUT4** medidos en aislamiento.
5. **Dos hallazgos contra el propio `RTL.md`**: la tolerancia declarada de
   0,00188 pp es inalcanzable por construcción (§5), y la afirmación de que
   la decisión discreta coincide "bit a bit" al 100% es falsa cerca del
   umbral (§6).
6. **Lo que sí cabe** es la variante "solo umbral, sin multiplicar": 742 de
   1.280 LCs (58%), a 114 MHz. Pero ésa no es el modelo del proyecto.

---

## 1. Qué se construyó

Las cinco etapas de `RTL.md` §1, una por archivo, en Verilog sintetizable:

| Archivo | Etapa |
|---|---|
| `micro/rtl/etapa_ingesta.v` | 1 — parser del mensaje de 28 bytes, byte por ciclo |
| `micro/rtl/etapa_features.v` | 2 — ventana rodante N=10 con suma corrida |
| `micro/rtl/etapa_puntaje.v` | 3 — MAC parametrizable en `N_FEATURES` |
| `micro/rtl/etapa_decision.v` | 4 — comparador doble BUY/HOLD/SELL |
| `micro/rtl/etapa_salida.v` | 5 — sello + contador de 48 bits + UART TX |
| `micro/rtl/pipeline_top.v` | las cinco cableadas + banco de pesos |
| `micro/rtl/sint_top.v` | envoltorio de placa (UART RX + serializador) |

Aritmética exactamente como la justifica `RTL.md` §3: **Q8.8** para features y
predicciones, **Q2.14** para pesos. No se cambió el formato.

Cuatro configuraciones, declaradas antes de medir:

| cfg | `N_FEATURES` | pesos | qué es |
|---|---|---|---|
| **F1** | 1 | sí | **el modelo campeón 4.6.0**: `apertura = beta x SOX`, una multiplicación, sin intercepto |
| **F3** | 3 | sí | generalización, para medir cómo escala el área |
| **F6** | 6 | sí | idem |
| **F1SP** | 1 | no | la fila "solo umbral, sin multiplicar" de `RTL.md` §2 |

**F3 y F6 no afirman nada sobre precisión.** Existen para medir área. El
proyecto ya publicó en `GEMELO/WS2b` que agregar features no mejoró nada de
forma detectable; inventar acá una ganancia contradiría su propio resultado
negativo. Los pesos extra son constantes arbitrarias declaradas en
`referencia.py` antes de correr.

---

## 2. Validación: el RTL contra la referencia

Protocolo de `RTL.md` §4, cumplido paso por paso.

**Vector:** las **181 filas selladas** de `senales_ticker` con `beta` y
`apertura_estimada_pct` no nulas (24 fechas, 8 tickers), serializadas al
formato de 28 bytes. `senales.db` se abrió en modo `ro`; nada se escribió.

**Cómo se recuperó el insumo del modelo.** El campeón es
`apertura = beta x ultimo_movimiento_no_cero_del_SOX`, y la base guarda
`apertura` y `beta` pero no el movimiento del SOX. Se despeja: si la identidad
vale para todos los tickers de una fecha, `apertura/beta` tiene que dar lo
mismo para todos. **Da lo mismo** — dispersión mediana entre tickers de 0,070
pp, máxima 0,292 pp — y esa dispersión residual se explica enteramente por el
redondeo a dos decimales con que la base guarda ambos campos (con `beta=0,08`,
un redondeo de 0,005 en `apertura` ya arrastra un 6% relativo). Se estima por
mínimos cuadrados por el origen, que pondera por `beta²` y deja mandar a las
betas grandes. **La coincidencia entre tickers es, de paso, una verificación
independiente de que el álgebra reimplementada es la correcta.**

**Referencia:** `micro/rtl/referencia.py`, float64, **aislada**. No importa
`motor.py` — lo prohíbe `RTL.md` §4.2 y la Regla Cero. Implementa DOS modelos
a propósito: `ModeloFlotante` (la verdad de referencia) y `ModeloEntero`
(réplica bit a bit de la semántica del RTL). Tener los dos separa dos
preguntas que se confunden: *¿el RTL hace lo que creo?* y *¿lo que creo se
parece al álgebra real?*

**Resultado:**

| cfg | casos | fallos | latencia min | latencia max | veredicto |
|---|---|---|---|---|---|
| F1 | 181 | **0** | 32 | 32 | OK |
| F3 | 181 | **0** | 32 | 32 | OK |
| F6 | 181 | **0** | 32 | 32 | OK |
| F1SP | 181 | **0** | 32 | 32 | OK |

**La latencia es idéntica en los 181 vectores y en las cuatro
configuraciones.** Es exactamente la predicción falsable que `fpga.md` §2
formuló — *"p50 = p99 = p99.9 = máximo"* — y el banco de pruebas la comprueba
explícitamente: si `min != max`, marca fallo. A 12 MHz son **2,67 µs**, contra
el piso de software de ~72-85 µs **con cola** que midió `WSL2.md`. La ventaja
no es la media: es que 32 no tiene distribución.

*(La cuenta a mano del diseño decía 33 ciclos. El banco midió 32 — se contaba
el ciclo del byte 0 dos veces. Se corrigió la cuenta, no la medición.)*

---

## 3. Los números de síntesis, etapa por etapa, contra la estimación

Cada etapa sintetizada **como su propio top**, para que ninguna entrada se
vuelva constante y no haya nada que podar. Estimaciones transcritas
literalmente de `RTL.md` §2.

| Etapa | LUT4 medidos | FF | estimación §2 | veredicto |
|---|---|---|---|---|
| Ingesta (parser 28 bytes) | **44** | 230 | 100-150 | **SOBREESTIMADA 2,3x** |
| Estado/features (N=10) | **318** | 262 | 50-100 | **SUBESTIMADA 3,2x** |
| Puntaje F=1 sin pesos (umbral) | **1** | 34 | 20-30 | SOBREESTIMADA 20x |
| Puntaje F=1 con peso (campeón) | **781** | 37 | 220-330 | **SUBESTIMADA 2,4x** |
| Puntaje F=3 | **2.424** | 115 | 620-930 | **SUBESTIMADA 2,6x** |
| Puntaje F=6 | **5.019** | 211 | 1.220-1.830 | **SUBESTIMADA 2,7x** |
| Decisión (comparador doble) | **8** | 3 | 15-25 | SOBREESTIMADA 1,9x |
| Salida (contador 48b + UART TX) | **142** | 233 | 100-150 | **DENTRO del rango** |
| *(uart_tx solo)* | 34 | 22 | — | — |
| *(uart_rx solo, envoltorio)* | 42 | 33 | — | — |

### 3.1 El error central: el costo de un multiplicador

Medido **en aislamiento**, fuera del pipeline, donde nada lo contamina
(`micro/rtl/costo_multiplicador.v`, target `make multiplicador`):

| variante | LUT4 | CARRY |
|---|---|---|
| **16x16 con signo → 32 bits** | **774** | 28 |
| 16x16 sin signo → 32 bits | 679 | 28 |
| 16x16 con signo, resultado truncado a 16 | 326 | 12 |
| 8x8 con signo → 16 bits | 177 | 11 |

**774 LUTs, contra los 200-300 estimados: entre 2,6 y 3,9 veces.**

Antes de acusar a la estimación había que descartar la explicación
alternativa. La sospecha razonable era que Verilog estuviera generando un
multiplicador de 32x32 en vez de 16x16: el ancho de los operandos lo determina
el CONTEXTO de la asignación, así que `p[31:0] <= a[15:0] * b[15:0]` extiende
ambos operandos a 32 bits antes de multiplicar. **La variante de 8 bits
descarta esa excusa:** 177 x (16/8)² = 708, del mismo orden que 774. El costo
escala como W², o sea que yosys sí construye un 16x16 honesto. **La estimación
simplemente estaba mal.** Mirando los números, 200-300 LUTs es lo que cuesta
un multiplicador de 8 o 10 bits — parece una regla de la casa calibrada para
un ancho más chico que el que este diseño necesita.

El costo marginal **dentro** del pipeline es aún un poco mayor por el árbol de
sumas y la saturación: (2.424−781)/2 = **822 LUTs** por feature adicional entre
F=1 y F=3, y (5.019−2.424)/3 = **865** entre F=3 y F=6.

### 3.2 El otro error: la etapa 2

**318 LUTs contra 50-100 estimados.** La estimación del §2 describe la etapa
como *"dos sumadores, no N"* — y esa parte es correcta, la suma corrida cuesta
lo que dice. Lo que la estimación no contó es que **la media exige dividir por
N**, y N=10 no es potencia de dos, así que no sale de un desplazamiento. Se
resuelve con un multiplicador por constante (`suma x 65536/10`), que es mucho
más barato que un multiplicador general pero no es gratis. La estimación
presupuso implícitamente una ventana de tamaño potencia de dos sin decirlo.

### 3.3 Dónde acertó

**La etapa de salida: 142 LUTs contra 100-150 estimados, dentro del rango.**
Es la fila más fácil de inflar (un UART "de mentira" habría medido 20 LUTs), y
por eso se sintetizó con el UART TX de verdad, a 115200 baudios, adentro.

La ingesta y la decisión salieron **más baratas** que lo estimado, y por la
razón que el propio diseño anticipó: un `case` sobre un contador de byte con
índices constantes por rama es cableado puro, no un shifter.

### 3.4 Un aviso metodológico que vale más que cualquiera de las filas

**La suma de las etapas medidas por separado da 1.307 LUTs para F=1. El
pipeline completo, aplanado y optimizado globalmente, da 1.892 — un 45% más.**

O sea: estimar un pipeline sumando estimaciones por etapa **subestima
sistemáticamente**, incluso si cada estimación individual fuera perfecta. El
mapeo tecnológico global duplica lógica para cerrar tiempos y el resultado no
es aditivo. `RTL.md` §2 construyó sus totales exactamente así. **Es un error
estructural del método, no de los números.**

---

## 4. El veredicto: ¿cabe en la Go Board?

Celdas lógicas **colocadas y ruteadas** por nextpnr (medición dura). El
netlist se colocó en un iCE40**HX8K** sólo para poder LEER el número: en el
HX1K nextpnr aborta con `no BELs remaining` sin decir cuántas celdas faltaron.
Misma arquitectura, mismo LUT4, misma ausencia de DSP. **El HX8K acá es un
instrumento de medición, no una placa propuesta.**

| cfg | LCs necesarias | de las 1.280 del HX1K | veredicto | Fmax |
|---|---|---|---|---|
| **F1SP** (solo umbral) | **742** | 58,0% | **CABE** | 114,19 MHz |
| **F1** (campeón: beta x SOX) | **1.545** | 120,7% | **NO CABE** — sobran 265 | 71,97 MHz |
| **F3** | **3.738** | 292,0% | **NO CABE** — 2,9x la placa | 69,01 MHz |
| **F6** | **6.483** | 506,5% | **NO CABE** — 5,1x la placa | 64,76 MHz |

**F1SP confirmado sobre el HX1K-tq144 real**: place & route exitoso,
**742/1.280 ICESTORM_LC (57%)**, 8/96 SB_IO, 0 BRAM, **Fmax 114,19 MHz**
(nextpnr) y **114,59 MHz** con `icetime` (ruta crítica 8,73 ns). Con creces
por encima de los 12 MHz del oscilador de la Go Board.

> **ERRATA (1-sep-2026), medido en `GEMELO/MICRO/INGESTA_ANCHA.md` §6.2.**
> **A la columna Fmax de esta tabla le falta su dispersión.** Los cuatro
> valores salen de `--seed 1`, y el Fmax de `nextpnr` **depende de la semilla
> del colocador**. Medido sobre 10 semillas con el mismo netlist F1SP sobre
> el mismo hx1k-tq144: **105,27 a 114,19 MHz** (el 114,19 sale en 8 de las
> 10; la media es 112,47). O sea que el número publicado es el modal, no un
> valor único. **La conclusión no se mueve**: incluso la peor semilla son 8,8
> veces los 12 MHz del oscilador.
>
> **Y alcanza también al `icetime` del párrafo de arriba.** Los 114,59 MHz
> (ruta crítica 8,73 ns) salen del `.asc` que produjo esa misma `--seed 1`:
> `icetime` no coloca nada, mide la ruta crítica de **una colocación ya
> hecha**, así que arrastra íntegra la dependencia de la semilla. Es otra
> herramienta pero no es otra realización, y por lo tanto **tampoco es la vara
> independiente** del número de nextpnr: las dos cifras miran el mismo
> `--seed 1`. Se anota acá para que nadie las cite como dos mediciones que se
> confirman entre sí.
>
> **Lo que sí es determinístico y por eso NO lleva intervalo: las celdas
> colocadas.** Las 742 salieron idénticas en las 10 semillas. La distinción
> importa — inventarle un intervalo a una cuenta de celdas sería tan
> deshonesto como omitírselo a un Fmax. Las cuatro filas se dejan como están;
> lo que se agrega es cómo hay que leerlas.

### 4.1 Qué etapa la revienta, y por cuánto

**La etapa de puntaje, sin ninguna duda.** Es la única diferencia entre F1SP
(cabe, 742 LCs) y F1 (no cabe, 1.545 LCs): **el multiplicador solo agrega 803
LCs**, y la placa entera tiene 1.280.

`RTL.md` §2 concluyó que *"F=1 cabe cómodo en el iCE40HX1K: deja 60-75% de
margen"*. **Es cierto para la fila que la tabla llamó F=1 — "solo umbral, sin
multiplicar" — y es falso para el modelo campeón.** La confusión está en la
tabla misma: rotuló como F=1 una configuración *sin multiplicación*, cuando el
campeón 4.6.0 con una sola feature **es** una multiplicación (`beta x SOX`).
Corregida esa correspondencia, la tabla del §2 no tiene ninguna fila que
describa al campeón: su fila más cercana es "Total F=3" (750-1.150 LUTs), y el
campeón real mide 1.892 LUTs aplanado.

### 4.2 Qué habría que sacrificar para que entre — DECISIÓN DE NICOLÁS

Se listan las opciones con su costo medido o calculado. **Este documento no
elige ninguna, y tampoco decide si se compra placa.**

> **ERRATA (1-sep-2026), medido en `GEMELO/MICRO/INGESTA_ANCHA.md` §4.**
> **A esta lista le falta una opción, y la falta es estructural, no un
> olvido.** Las cinco opciones (a) a (e) son **restas**: angostar la
> aritmética, un multiplicador más lento, sacrificar el UART y el contador,
> degradar el modelo, comprar otra placa. El título de la sección —"qué habría
> que **sacrificar** para que entre"— no sólo enmarcó la pregunta: definió la
> **forma gramatical** de las respuestas admisibles. **Un marco que sólo
> admite sacrificios no puede contener una opción que mejora dos cosas a la
> vez y no cuesta nada.**
>
> La opción que faltaba: **ensanchar el bus de la ingesta**. Baja la latencia
> de 32 a 11 ciclos (4 B/ciclo) o a 5 (28 B/ciclo) **y baja el área**, en las
> dos placas. Medido en el iCE40, colocado y ruteado: **1.198 → 1.184
> ICESTORM_LC** de B=1 a B=4, con las **181 filas selladas bit a bit**. O sea
> que **en la Go Board tampoco estaba bloqueada por falta de espacio: ahí
> también salía gratis, y nadie lo midió porque nadie lo preguntó.**
>
> **Lo que esta errata NO dice.** No rescata a la Go Board: el F1 completo son
> 1.545 celdas contra 1.280 y 14 celdas no mueven ese veredicto. La §4 sigue
> firme. El hallazgo es sobre el método, no sobre el resultado — y por qué la
> pregunta no se formuló está desarrollado en `INGESTA_ANCHA.md` §4.2.

- **(a) Angostar la aritmética.** Un multiplicador 8x8 cuesta 177 LUTs en vez
  de 774. Sustituyendo, F=1 quedaría cerca de 1.288 LUTs — **todavía al
  filo de los 1.280, y sin contar el envoltorio de placa (330 LUTs más).**
  Probablemente no alcanza. Y tiene un costo aparte: Q4.4 da una resolución de
  0,0625 pp contra los 0,0039 de Q8.8, lo que **invalidaría la justificación
  medida de `RTL.md` §3** y obligaría a rehacerla con los datos reales.
- **(b) Multiplicador serie en vez de paralelo.** Un multiplicador de
  desplazar-y-sumar cuesta del orden de 16 veces menos área a cambio de 16
  ciclos de latencia. **La latencia seguiría siendo determinista** (32 → ~48
  ciclos fijos), que es la propiedad que el proyecto quiere demostrar. Es, con
  diferencia, la opción técnicamente más limpia y **no se midió** — sería el
  siguiente trabajo si se elige este camino.
- **(c) Sacrificar el UART y el contador de 48 bits.** Ahorra ~180 LUTs. No
  alcanza, y además el contador ES el instrumento de medición del proyecto.
- **(d) Quedarse en F1SP** (solo umbral) y declarar que el proyecto de la
  materia implementa un pipeline de decisión que **no** es el modelo de MKI.
  `RTL.md` §6 ya marcó esta opción como legítima y como decisión de Nicolás.
- **(e) Comprar una Arty A7-100T.** Ver §7.

---

## 5. Hallazgo: la tolerancia declarada en `RTL.md` §3 es inalcanzable

`RTL.md` §3 midió que cuantizar las 279 predicciones selladas a Q8.8 da un
**error absoluto máximo de 0,00188 pp**, y §4.4 adoptó ese número como la
tolerancia del puntaje intermedio, declarada antes de comparar.

**Medido sobre las 181 filas, el error del puntaje del RTL contra la
referencia en float64 es de 0,00474 pp — 2,5 veces la tolerancia declarada.**

No es un error del RTL: es que **la tolerancia se derivó para la operación
equivocada.** 0,00188 pp es el error de cuantizar *un* valor. El puntaje es el
producto de *dos* valores cuantizados (feature Q8.8 y peso Q2.14) más el
truncado del desplazamiento de vuelta a Q8.8. Tres fuentes, no una.

Se midió también qué parte es del truncado, corriendo el mismo vector con
redondeo al más cercano:

| F | modo | error máx (pp) | decisiones distintas | sesgo medio (pp) |
|---|---|---|---|---|
| 1 | truncado (lo que hace el RTL) | 0,004740 | 2 | **−0,001958** |
| 1 | redondeo al más cercano | 0,003114 | 1 | −0,000102 |
| 3 | truncado | 0,004658 | 0 | −0,001527 |
| 3 | redondeo | 0,003861 | 0 | +0,000523 |
| 6 | truncado | 0,004466 | 0 | −0,001480 |
| 6 | redondeo | 0,004391 | 0 | +0,000591 |

El sesgo del truncado es **−0,00196 pp**, que es medio LSB de Q8.8 (0,00195)
con una exactitud que da un poco de gracia — el comentario del diseño en
`etapa_puntaje.v` lo predijo y la medición lo confirma. **El redondeo elimina
el sesgo pero NO baja el error máximo por debajo de 0,00188 pp:** ningún modo
de redondeo lo logra, porque el problema es la cuantización de los operandos,
no la del resultado.

**Qué hacer con esto es decisión de Nicolás**, y `RTL.md` §6 ya lo había
marcado como decisión suya ("la tolerancia como criterio de aceptación formal
del proyecto"). La opción honesta es corregir la tolerancia a la operación
correcta (0,005 pp cubre lo medido con margen), documentando la corrección con
fecha posterior — **nunca reescribir el 0,00188 como si siempre hubiera dicho
otra cosa.**

**Contexto que hace todo esto irrelevante para las cifras publicadas:** el
error de 0,00474 pp es el **0,16% del MAE publicado del gap (2,98 pp)**, y
sobre las 181 filas **ninguna predicción cambió de signo**. Contra la
predicción SELLADA, el pipeline F=1 reproduce con error medio 0,0061 pp y
máximo 0,027 pp — **y ese piso no lo pone la aritmética del RTL sino la propia
base, que guarda `apertura` y `beta` con dos decimales: ±0,005 pp, más grueso
que el LSB de Q8.8.**

---

## 6. Hallazgo: la decisión discreta NO coincide al 100%

`RTL.md` §4.4 afirma:

> *"la decisión es discreta —BUY/HOLD/SELL— así que 'bit a bit' y 'dentro de
> tolerancia' coinciden acá: o es la misma decisión o no lo es"*

**Es falso, y en la dirección contraria a la que sugiere.** Sobre las 181
filas, con F=1, **2 casos (1,1%) deciden distinto** que la referencia en
float64:

| fecha | ticker | puntaje flotante | puntaje entero | decisión float | decisión entera |
|---|---|---|---|---|---|
| 2026-08-21 | 000660.KS | −0,500242 pp | −0,50000 pp | VENTA | MANTENER |
| 2026-08-25 | 4063.T | +0,503109 pp | +0,50000 pp | COMPRA | MANTENER |

Los dos casos son el mismo caso: el puntaje real cae **a milésimas del umbral**
(±0,50 pp) y la cuantización lo deposita exactamente **sobre** el umbral, donde
la comparación estricta lo manda a MANTENER.

**La lección es general y va contra la intuición del §4.4:** que una salida sea
discreta no la vuelve inmune al error de cuantización — la vuelve **más
frágil** cerca de la frontera de decisión. Un error de 0,003 pp en una
magnitud continua es despreciable; el mismo error a 0,003 pp de un umbral
invierte la salida por completo. Sobre un vector con más masa cerca del umbral
la tasa de discrepancia sería mayor.

Con redondeo al más cercano los casos bajan de 2 a 1: **mitiga, no resuelve.**

**Nada de esto invalida el RTL:** contra el modelo ENTERO —que es la semántica
que el hardware promete— la coincidencia es de 181/181 bit a bit en las cuatro
configuraciones. Lo que falla es la afirmación de `RTL.md` de que la
discretización protege de la cuantización.

---

## 7. Artix-7: qué margen daría

**`nextpnr-xilinx` NO viene en OSS CAD Suite** (verificado: los nextpnr
incluidos son ice40, ecp5, machxo2, nexus, gowin, generic, himbaechel), así
que **no hay place & route, no hay utilización real y no hay Fmax.** No se
forzó.

Lo que sí se pudo hacer es correr `yosys synth_xilinx -family xc7`, que mapea a
celdas Artix-7 **reales** y permite contarlas. Es más duro que una cuenta a
mano y **más blando que un reporte de Vivado**; se publica como lo que es.

| cfg | DSP48E1 | LUTs | FF | % LUTs de 63.400 | % DSP de 240 |
|---|---|---|---|---|---|
| F1SP | 0 | 189 | 522 | 0,30% | 0% |
| **F1 (campeón)** | **1** | **222** | 569 | **0,35%** | **0,42%** |
| F3 | 4 | 347 | 892 | 0,55% | 1,67% |
| F6 | 7 | 504 | 1.132 | 0,79% | 2,92% |

*(El DSP de más respecto de `N_FEATURES` es el multiplicador por constante de
la media rodante de la etapa 2.)*

**`RTL.md` §2 acertó de lleno acá**: dijo que en una Arty A7-100T *"cualquiera
de las tres filas es trivial"* y que F=6 usaría *"6 de los 240 disponibles
(2,5%)"*. Medido: 7 DSPs, **2,92%**. La estimación erró por un DSP, y el que
faltaba es el que la §3.2 explica.

El contraste es la cifra que resume el frente entero: **el mismo diseño pasa de
no caber en una placa a ocupar el 0,35% de la otra**, porque en el iCE40 el
multiplicador cuesta 774 LUTs y en el Artix-7 cuesta **un bloque dedicado y
cero LUTs**. `fpga.md` §3 ya lo había dicho — *"la fila que más importa no es
la de LUTs, es la de multiplicadores dedicados"* — y la medición lo confirma
sin matices.

---

## 8. Marcado explícitamente como decisión de Nicolás

1. **Qué placa.** Sigue sin resolverse acá, igual que en `fpga.md` §5 y
   `RTL.md` §6. Lo que cambia es que ahora la decisión tiene números medidos:
   el campeón necesita 1.545 LCs y la Go Board tiene 1.280.
2. **Si se sacrifica algo para entrar en el iCE40** — y cuál de las cinco
   opciones de la §4.2. Ninguna se eligió acá.
3. **Si el pipeline replica al 4.6.0 o es un modelo propio declarado como
   distinto.** `RTL.md` §6 ya lo marcaba; la medición lo vuelve urgente,
   porque replicar al 4.6.0 es justamente lo que no entra.
4. **Qué hacer con la tolerancia de 0,00188 pp** (§5): corregirla con una
   errata fechada, o mantenerla y declarar que el criterio de aceptación es la
   coincidencia de decisiones contra el modelo entero.
5. **Si vale la pena medir el multiplicador serie** de la §4.2(b) antes de
   decidir sobre la placa. Es la única opción que preserva la aritmética
   justificada Y el determinismo, y no está medida.

---

## 9. Qué queda pendiente

- **El paso 5 del protocolo de `RTL.md` §4**: medición sobre placa física.
  Falta la placa, no la herramienta.
- **Throughput espalda-con-espalda.** El banco de pruebas inserta 8 ciclos de
  silencio entre mensajes para que la medición de latencia sea limpia (si no,
  el `inicio_mensaje` del mensaje k+1 pisa el registro del mensaje k). El
  throughput sostenido es otra pregunta y **no se midió**: decir que sí sería
  mentir sobre el experimento que se corrió.
  > **DOS VECES SUPERADO (1-sep-2026).** (1) El caudal **ya se midió**, con la
  > fuente interna: 15,00 ciclos por mensaje en B=4 y 9,00 en B=28
  > (`INGESTA_ANCHA.md` §3.3), contando el reloj de la corrida entera y no
  > convirtiendo una latencia. (2) Y lo más importante: **los 8 ciclos no son
  > para medir limpio.** Son un requisito de corrección, con mínimo medido en
  > 2 — por debajo, 178 de 181 sellos salen mal mientras la latencia sigue
  > perfecta. Queda escrito y numerado como R1 en `RTL.md` §7 y verificado por
  > `make hueco-gate`. Esta frase se deja como estaba porque describe lo que
  > se creía al escribirla, y es el ejemplo del que salió el requisito.
- **Multiplicador serie** (§4.2b), sin medir.
- **Artix-7 con place & route real**, que exige `nextpnr-xilinx` + `prjxray` o
  Vivado.
