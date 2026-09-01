# El proyecto final de Arquitectura de Computadores — plan con hitos y evidencia

**Fecha:** 31-ago-2026. **Placa:** Digilent Arty A7-100T,
**XC7A100TCSG324-1**, ya comprada.
**Insumos medidos:** `GEMELO/MICRO/SINTESIS_A7.md` (el margen), `SINTESIS.md`
(el pipeline en iCE40), `RTL.md` (el diseño), `piso_de_latencia.md` (el
veredicto que define el alcance), `WSL2.md` (el piso de software contra el que
se compara).

> **El criterio de éxito ya existe y no se inventa acá:** la **reproducción bit
> a bit de las filas selladas** contra la referencia en Python. Está **cumplido
> en simulación, 181/181**, en las cuatro configuraciones y en los seis anchos
> de ingesta. **En silicio es el proyecto.**

---

## 1. Qué se implementa, y qué NO — dicho antes que el cronograma

**Se implementa:** el pipeline de decisión de cinco etapas que ya existe en
`micro/rtl/`, sintetizado, colocado, ruteado y **corriendo en la placa**,
alimentado por las **filas selladas reales** de `senales.db` precargadas en
BRAM, midiendo su propia latencia con un contador interno y sacando el sello
por UART.

**NO se implementa, y cada exclusión tiene una razón medida:**

| Fuera de alcance | Por qué |
|---|---|
| **La DDR3L** | La historia sellada entera son 5.292 B = **0,85% de la BRAM** del chip (`SINTESIS_A7.md` §3.2). Un controlador DDR agrega un MIG, un dominio de reloj y un cierre de temporización, **a cambio de nada** |
| **Ethernet** | §5 de este documento. Metería en la ruta de medición justamente el tipo de camino con cola que el proyecto existe para contrastar |
| **MicroBlaze / cualquier procesador blando** | El punto es que **no hay software** en la ruta de decisión. Poner una CPU adentro destruye la tesis |
| **Un feed de mercado real o un bróker** | Prohibido por la Constitución 5.0 (5) y, aparte, `piso_de_latencia.md` ya midió que no hay ventaja que capturar |
| **Entrenar o re-estimar beta en la FPGA** | `RTL.md` §5. Los pesos se calculan fuera y se cargan. Cuánto costaría está medido en `SINTESIS_A7.md` §4.3, por si el hito H5 se elige |
| **Optimizar para latencia mínima** | El proyecto demuestra que la latencia es **fija y conocida**, no que sea la más chica posible (`RTL.md` §5) |

**La decisión de arquitectura que el margen medido habilita y que se toma acá:
la fuente de datos es BRAM, y la ingesta es de 4 bytes por ciclo.** El puerto
natural de una BRAM de 36 Kb es de 32 bits, la latencia medida a B=4 es de
**11 ciclos** contra 32, el área **baja** (102 LUT6 contra 108) y el resultado
es **bit a bit idéntico** en los 181 vectores (`SINTESIS_A7.md` §4.1).

---

## 2. Los hitos, en orden, con su evidencia

Cada hito tiene: **qué se hace**, **qué demuestra**, **qué evidencia queda** y
una **predicción falsable escrita antes de correr**. El orden no es negociable:
cada uno es el insumo del siguiente.

### H0 — La herramienta *(bloqueado: es de Nicolás)*

**Qué.** Crear la cuenta AMD, firmar el formulario de control de exportación,
descargar Vivado **2026.1**, instalarlo **del lado Windows** (evita el
`usbipd-win` para el JTAG y evita que Ubuntu 26.04 no esté en la lista de
UG973 — ver `micro/TOOLCHAIN.md` §3.1), generar la **licencia BASIC gratuita**
y cargar un bitstream trivial que haga parpadear un LED.

**Qué demuestra.** Que la cadena entera —síntesis, P&R, bitstream, JTAG— está
cerrada. Nada más. Es el hito más aburrido y el único que bloquea a los otros
cinco.

**Evidencia.** Versión exacta de Vivado, el archivo de licencia, y la placa
parpadeando.

**Por qué no lo hace Claude.** Crear una cuenta y firmar una declaración de
control de exportación es un acto de identidad, de la misma clase que pushear a
GitHub, que la Constitución 5.0 (5) ya reserva para Nicolás.

---

### H1 — Paridad de síntesis: la vara independiente

**Qué.** Correr el RTL **tal como está** por Vivado, target
`xc7a100tcsg324-1`, y comparar su reporte de utilización contra las cifras del
mapeo de yosys ya publicadas en `SINTESIS_A7.md` §3.1.

**Qué demuestra.** Es la aplicación literal de la regla de la casa: **todas las
cifras de Artix-7 del proyecto salieron de yosys, y una verificación con yosys
no sería una verificación.** Vivado es otra familia de herramienta, con otro
mapeador y otro empaquetador. **Éste es el hito que valida —o refuta— el
documento entero.** Y de paso entrega el **primer Fmax que el proyecto va a
tener en Artix-7**.

**Predicción falsable, escrita ANTES de correr:**

| Magnitud | Predicción | Cómo se falsa |
|---|---|---|
| DSP48E1 (F1) | **exactamente 1** | Vivado reporta ≠ 1 |
| LUT (F1) | 222 ± 50% (Vivado empaqueta distinto) | fuera de [111, 333] |
| FF (F1) | 569 ± 10% | fuera de [512, 626] |
| BRAM | **0** | Vivado infiere alguna |
| Fmax | **> 100 MHz** | cierra por debajo |
| Slices ocupados | **≥ 72** (el piso derivado) y **< 250** | fuera de rango |

**Si alguna falla, gana Vivado y se corrige `SINTESIS_A7.md` con una errata
fechada** — nunca al revés, y nunca reescribiendo el número viejo.

**Evidencia.** El `utilization report` y el `timing summary` de Vivado, más una
tabla de tres columnas: yosys · Vivado · diferencia.

---

### H2 — El pipeline en silicio, contra las filas selladas *(el criterio de éxito)*

**Qué.** Construir un **reproductor desde BRAM**: los mensajes de 28 bytes y
los pesos Q2.14 de las filas selladas, precargados en memoria de bloque vía
`$readmemh` sobre los mismos `vectores/mensajes.hex` y `vectores/pesos.hex` que
ya genera `referencia.py`. El reproductor alimenta el pipeline a **4 bytes por
ciclo**, y cada sello sale por **UART a 115200** con
`{id, decisión, puntaje, latencia_ciclos}`.

Ocupación de la BRAM, calculada: 181 × 224 bits de mensajes + 181 × 96 bits de
pesos ≈ **58 Kbit**, o sea **2 bloques de 36 Kb de los 135** disponibles.

**Qué demuestra.** **ESTO ES EL PROYECTO.** El criterio de aceptación es el que
ya existe y está cumplido en simulación: la salida capturada por UART tiene que
coincidir **bit a bit** con `vectores/esperado_F1.hex`, en las 181 filas.

**Predicción falsable:** 181/181 exactas. Cualquier discrepancia es un hallazgo
de silicio (un cruce de dominio de reloj, una BRAM mal inicializada, un
desajuste del UART) y **se investiga, no se tolera**.

**Dos honestidades que hay que arrastrar al informe y no dejar en el camino:**

1. **El criterio es contra el modelo ENTERO**, que es la semántica que el
   hardware promete. Contra el modelo en **float64** hay **2 filas de 181
   (1,1%) que deciden distinto** (`SINTESIS.md` §6): son casos que caen a
   milésimas del umbral de ±0,50 pp y la cuantización los deposita justo
   encima. **Eso no es un defecto del silicio y no se puede esconder detrás del
   181/181.**
2. **El piso de reproducibilidad contra la fila sellada no lo pone el
   hardware**: `senales.db` guarda `apertura` y `beta` con dos decimales,
   ±0,005 pp, más grueso que el LSB de Q8.8. Ningún ancho de punto fijo lo
   cruza (`SINTESIS_A7.md` §4.4.2).

**Evidencia.** La captura cruda del UART, el script de comparación, y el
veredicto N/181. Es el artefacto que se entrega en el ramo.

---

### H3 — La medición que es la tesis: la latencia no tiene distribución

**Qué.** Con el reproductor de H2 en bucle, capturar el `latencia_ciclos` de
**miles** de decisiones repetidas y graficar la distribución.

**Qué demuestra.** Es la **predicción falsable de `fpga.md` §2**, literal:
**p50 = p99 = p99.9 = máximo**. En simulación ya sobrevivió (mín = máx en los
181 vectores, en las cuatro configuraciones y en los seis anchos). En silicio
es donde puede fallar de verdad, porque aparecen el oscilador real, los
dominios de reloj y el ruteo.

Y es donde la comparación cobra sentido: `WSL2.md` midió en esta misma máquina
un **piso de software de ~72-85 µs con cola**. El pipeline a 100 MHz con B=4
son **110 ns, sin cola**. **El argumento no es el promedio: es que 11 no tiene
distribución.**

**Si aparece cola, ESO es el hallazgo** y hay que encontrarle la causa (un
cruce de dominio mal sincronizado es la sospecha número uno). Un proyecto que
reporta la cola y la explica vale más que uno que la esconde.

**Evidencia.** El histograma —que debería tener **una sola barra**— y la tabla
de percentiles al lado de los del software.

---

### H4 — El barrido de ancho, en hardware

**Qué.** Repetir H2 y H3 para B ∈ {1, 2, 4, 7, 14, 28} y agregar la columna que
la simulación no puede dar: **el Fmax de cada uno**.

**Qué demuestra.** Convierte el resultado más contraintuitivo de
`SINTESIS_A7.md` §4.1 —que ensanchar el bus **baja la latencia 6,4× y el área
también baja**— de resultado de simulación a resultado de hardware. Y responde
la pregunta que la simulación tiene prohibida: **¿la ruta crítica empeora al
ensanchar?** El decodificador de palabra se achica pero el búfer se escribe más
ancho; no hay forma de saberlo sin P&R.

**Predicción falsable:** latencia = `ceil(28/B) + 4` exacta en los seis anchos,
y Fmax **no peor que a B=1** (la hipótesis es que el ensanchado no toca la ruta
crítica, que vive en el MAC).

**Evidencia.** La tabla de `SINTESIS_A7.md` §4.1 con dos columnas nuevas —Fmax
y slices— y el veredicto sobre la predicción.

---

### H5 — Alcance opcional *(la elección es de Nicolás)*

Dos caminos, medidos los dos, **incompatibles en el tiempo que tiene un ramo**:

**(a) Ancho — tabla de pesos por instrumento.** Un banco de pesos indexado por
`id_instrumento` (el campo ya viaja en el mensaje de 28 bytes y hoy sólo se usa
para sellar), sirviendo los **8 tickers de `MERCADOS_POR_ABRIR`** con **un solo
pipeline multiplexado**. Costo: una BRAM chica. Demuestra el sistema real
completo. **Es el camino barato y el que más se parece a MKI.**

**(b) Profundo — la regresión adentro del chip.** Las piezas del 4.6.0 completo
que hoy no existen: momentos rodantes de N=120, divisor y raíz. Costo medido
(`SINTESIS_A7.md` §4.3): **≈864 LUT6, ≈4.949 FF, 5 DSP48E1** — bajo el 4% del
chip. **Cabe. Que quepa no significa que valga la pena**, y hay una dificultad
real esperando: `motor` calcula en float64 sobre retornos porcentuales, y una
regresión de 120 puntos en punto fijo tiene problemas de rango y cancelación
que una multiplicación no tiene. **Es un proyecto entero, no un hito.**

**Recomendación, marcada como recomendación y no como decisión:** (a). Cierra
el sistema que el proyecto dice ser, con un costo acotado. (b) abre un frente
de aritmética que puede comerse el semestre y cuyo resultado —una beta en punto
fijo que no coincide con la de Python— sería un fracaso caro de explicar.

---

## 3. Qué evidencia queda al final

| Artefacto | De qué hito | Qué prueba |
|---|---|---|
| Reporte de utilización y temporización de Vivado | H1 | Que las cifras de yosys de todo el frente eran correctas — o que no lo eran |
| Bitstream + constraints (`.xdc`) versionados | H2 | Reproducibilidad: cualquiera rehace la medición |
| Captura cruda del UART, N filas | H2 | **El criterio de éxito**: N/181 bit a bit |
| Script de comparación captura ↔ `esperado_F1.hex` | H2 | Que la comparación es mecánica, no visual |
| Histograma de latencia, miles de repeticiones | H3 | **La tesis**: la latencia no tiene distribución |
| Tabla de percentiles hardware vs. software (`WSL2.md`) | H3 | El contraste que da sentido a la tesis |
| Tabla de ancho × (latencia, área, Fmax) | H4 | Que el ensanchado es gratis también en silicio |
| Las 2 filas que deciden distinto contra float64 | H2 | **Honestidad**: el resultado negativo se publica igual |

Todo eso ya tiene su lugar en el árbol: `micro/rtl/` para el RTL y los
scripts, `micro/resultados/` para las capturas, y `GEMELO/MICRO/` para los
documentos.

---

## 4. Riesgos, con su plan

| Riesgo | Probabilidad | Plan |
|---|---|---|
| **H0 no se hace** (la cuenta AMD) | La única que importa | **Bloquea todo.** No hay plan B: sin Vivado no hay bitstream para esta pieza |
| Vivado contradice a yosys en H1 | Media | **Gana Vivado.** Se corrige `SINTESIS_A7.md` con errata fechada. No invalida el proyecto: lo mejora |
| El diseño no cierra a 100 MHz | Baja — en iCE40, que es mucho más lento, cierra a 72 MHz | Bajar el reloj. La latencia **en ciclos** no cambia, y la tesis es sobre ciclos |
| Aparece cola en la latencia (H3) | Baja | **Es un hallazgo, no un fracaso.** Se investiga el cruce de dominio y se publica |
| El UART pierde bytes a 115200 | Media | Bajar el baudio o buferear. No toca la ruta de decisión ni la medición de latencia, que es interna |
| Se cae en la tentación de agregar Ethernet o DDR3L | **Alta** — están en la placa y llaman | §1 y §5. Están excluidos por escrito y con número, precisamente para esto |

---

## 5. La Ethernet 10/100 — por qué no afecta este rol y por qué SÍ afectaría al otro

**El dato, verificado en el manual de Digilent (§6), no de memoria:** la Arty
A7 lleva un **Texas Instruments DP83848J**, interfaz **MII**, **10/100 Mb/s**.
**No es gigabit**, y no hay forma de que lo sea: el PHY está soldado.

### 5.1 Por qué NO afecta a este proyecto

**Primero, y es lo decisivo: la Ethernet no está en la ruta de medición.** Lo
que el proyecto mide es la latencia **desde el primer byte que entra al
pipeline hasta que se afirma el sello**, con un **contador interno de la propia
FPGA** (`fpga.md` §2 lo especificó así a propósito, para no reintroducir el
problema de resolución de un reloj externo). Ese camino **no cruza el PHY**.
Meter Ethernet ahí adentro sería, literalmente, agregar a la medición un camino
con distribución y cola — **exactamente lo que el proyecto existe para
contrastar.**

**Segundo: el caudal es ridículo comparado con el enlace.** El sistema emite
**8 predicciones por día** = 224 bytes.

| | a 10 Mb/s | a 100 Mb/s |
|---|---|---|
| Una trama mínima de Ethernet (84 B en el cable, con preámbulo, cabecera, FCS e IPG) | 67,2 µs | **6,7 µs** |
| Una sesión entera (8 tramas) | 538 µs | **54 µs** |
| **Toda la historia sellada** (189 filas) | 12,7 ms | **1,3 ms** |

Aun **en el extremo lento de 10 Mb/s**, la jornada entera de trabajo del
sistema viaja en medio milisegundo. La restricción real es **una sesión del SOX
por día**, y ningún PHY cambia eso.

**Tercero: el proyecto ni siquiera la necesita.** El vector entra por BRAM
(§2, H2) y el sello sale por UART. **La Ethernet queda sin usar, y está bien.**

### 5.2 Por qué SÍ afectaría a un rol de ejecución

Un rol de ejecución —recibir mercado en vivo y mandar una orden— pone la red
**adentro del presupuesto de latencia**, y ahí la diferencia es de orden de
magnitud:

- Una trama mínima tarda **6,7 µs** en el cable a 100 Mb/s y **0,67 µs** a
  1 Gb/s. **Un orden de magnitud, y se paga dos veces**: entrada y salida.
- El MII de un PHY 10/100 es un bus de **nibble a 25 MHz**; un PHY gigabit
  (GMII/RGMII) mueve un byte a 125 MHz. La serialización es cinco veces más
  lenta antes de contar nada más.
- Y un PHY 10/100 típico **almacena y reenvía**; los gigabit con un MAC serio
  hacen paso directo.

**Pero acá está lo que hay que decir, y es lo que evita que este párrafo suene
a excusa:** el número que mata al rol de ejecución **no es el del PHY**.
`GEMELO/MICRO/piso_de_latencia.md` ya midió que la lectura de "captura en vivo"
**muere por 3 o 4 órdenes de magnitud**, y la Ethernet aporta **uno**.
Cambiarla por gigabit dejaría el rol de ejecución **igual de muerto**, sólo que
por 2-3 órdenes en vez de 3-4.

Hay una forma más limpia de verlo, con los números de este documento: la
decisión del pipeline tarda **110 ns** (11 ciclos a 100 MHz). Una trama mínima
tarda **6,7 µs** a 100 Mb/s y **0,67 µs** a gigabit. O sea que **en cualquier
configuración con red, el enlace domina por un factor de entre 6 y 61, y el
pipeline nunca es el cuello.** Ésa es exactamente la razón por la que este
proyecto **no** es un proyecto de ejecución, y por la que la Ethernet 10/100 no
le quita nada: **el rol que la placa cumple acá es el de un instrumento de
arquitectura, y un instrumento se mide contra su propio contador de ciclos, no
contra un cable.**

---

## 6. Lo que este documento NO decide

1. **Si H5 se hace, y cuál de los dos caminos** (§2, H5). Hay recomendación,
   no decisión.
2. **Si la Go Board sigue en juego.** El F1SP cabe en ella (742/1.280 LCs,
   114 MHz) y una comparación de dos arquitecturas es un buen capítulo — o una
   distracción. Es alcance académico.
3. **Cuál es el criterio de aceptación FORMAL que la materia evalúa.**
   `RTL.md` §6 y `SINTESIS.md` §8.4 ya lo marcaban. Este plan usa "181/181 bit
   a bit contra el modelo entero" porque es el que ya está cumplido en
   simulación y es mecánicamente verificable, pero **elegirlo como criterio del
   ramo es una decisión académica, no técnica**.
4. **Qué hacer con la tolerancia de 0,00188 pp** de `RTL.md` §3. Sigue abierta
   y ahora con más evidencia (`SINTESIS_A7.md` §4.4).
