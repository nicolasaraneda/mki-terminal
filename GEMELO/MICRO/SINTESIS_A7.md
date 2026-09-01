# La Arty A7-100T, medida — qué compra el margen y dónde está el cuello

**Fecha:** 31-ago-2026. **Estado:** medido, salvo lo que se marca como
ESTIMACIÓN y lo que se marca como CÁLCULO.
**Placa:** Digilent Arty A7-100T (original), **XC7A100TCSG324-1**. Ya comprada:
la pregunta "qué placa" está cerrada y este documento no la reabre.
**Insumos:** `GEMELO/MICRO/SINTESIS.md` (la corrida anterior, sobre iCE40),
`GEMELO/MICRO/RTL.md`, `GEMELO/MICRO/fpga.md`, `micro/rtl/`.
**Herramientas:** yosys 0.68+136, Icarus Verilog 14.0 (`micro/TOOLCHAIN.md`).
**Reproducible con:** `cd micro/rtl && make a7 && make ancho && make error-ancho`.

> **Regla que gobierna este documento:** una verificación que usa el mismo
> mecanismo que produjo la cifra NO es una verificación. Cada cifra crítica se
> contrasta contra una vara de otra familia de método, y donde esa vara no
> existe se dice que no existe en vez de fabricar una parecida.
>
> **Regla cero heredada:** ninguna cifra se ajustó para que algo quepa.
> `motor.py`, `senales.py`, `snapshot.py` y `universo.py` no se tocaron;
> `senales.db` se abrió siempre en `mode=ro`.

---

## 0. Resumen ejecutivo

1. **La comparación "1.545 contra 101.440" es inválida dos veces** (§1): la
   unidad no es la misma y el 101.440 ni siquiera es un recurso físico. La
   conversión correcta es **63.400 LUT6 y 126.800 flip-flops**, y está
   verificada contra DS180 con una prueba que no depende de mi memoria.
2. **Vivado NO se instaló, y el bloqueo no es técnico** (§2 y
   `micro/TOOLCHAIN.md` §3): hay 946 GB de disco libres, 31 GB de RAM y no
   hace falta root. El instalador está detrás de una **cuenta AMD + formulario
   de control de exportación**, que es un acto de identidad de Nicolás.
   **Todo lo que exija place & route sigue sin medirse: no hay Fmax, no hay
   utilización de slices, no hay reporte de temporización.**
3. **El cuello NO es ninguno de los tres candidatos, para la carga real.** El
   pipeline consume **224 bytes por sesión** (8 tickers × 28 B). La DDR3L
   entrega eso en **168 ns** y podría alimentar **47,6 millones de mensajes por
   segundo**; la plataforma emite **ocho por día**. El margen es de **11
   órdenes de magnitud** (§3.3).
4. **Si se pregunta cuánto diseño entra, el que topa primero es el DSP48E1, a
   240 tickers en paralelo** — medido sintetizando K instancias de verdad, con
   pendiente exactamente lineal entre K=1 y K=64 (§3.4). El universo tiene 8.
5. **La DDR3L es prescindible.** La historia sellada entera son **5.292 bytes**
   = **0,85% de la BRAM** del chip, y `senales.db` completa (397.312 B) entra
   en el **64% de la BRAM**. El proyecto puede correr sin tocar la memoria
   externa (§3.2).
6. **Ensanchar el punto fijo NO compra nada medible** (§4.4). Contra el álgebra
   en float64 el error cae 250× de Q8.8 a Q16.16; **contra la fila SELLADA se
   estanca en 0,027 pp y no se mueve**, porque quien manda ahí es el redondeo a
   dos decimales de la propia base, no el hardware. Costo de intentarlo: de 1 a
   4 DSP48E1 por multiplicación.
7. **La mejor compra del margen es la latencia, y es GRATIS** (§4.1). De los 32
   ciclos, **27 son la ingesta byte a byte** y sólo 5 son cómputo. Ensanchando
   el bus de entrada a 4 bytes/ciclo la latencia cae a **11 ciclos** y a 28
   bytes/ciclo a **5 ciclos** — con **181/181 bit a bit idénticos** en los seis
   anchos y **menos área** (108 → 93 LUT6), no más.
8. **El encargo preguntaba qué etapas están "serializadas por falta de
   espacio". La respuesta medida es NINGUNA** (§4.1). Las etapas 2 a 5 ya van
   encadenadas a un ciclo cada una. Lo único serializado es el parser, y no por
   presupuesto sino porque el diseño supuso un flujo de un byte por ciclo.
9. **Hallazgo contra el propio encargo:** el 0,063% que se pedía verificar
   **no está en `SINTESIS.md`** — está en `RTL.md` §3, y mide otra cosa
   (§4.4.1). `SINTESIS.md` §5 publica **0,16%**. Los dos números son correctos
   y miden operaciones distintas.
10. **Hallazgo contra la ficha de Digilent:** la viñeta de marketing dice
    "DDR3L @ 667 MHz" y la Tabla 2 del mismo manual dice "3000 ps (667 Mbps)".
    **Difieren en un factor 2 en las unidades** y gana la tabla, porque trae el
    período en picosegundos y es comprobable sola (§3.3).

---

## 1. B0 — La advertencia de unidades. Qué significa "cabe" en cada placa

Ésta es la sección que va antes de cualquier conclusión de margen, porque
comparar 1.545 contra 101.440 sería exactamente el error que la regla de la
casa existe para evitar.

### 1.1 Las tres unidades y por qué no son la misma

| Unidad | Qué es físicamente | Quién la reporta |
|---|---|---|
| **`ICESTORM_LC`** (iCE40) | **1 LUT4 + 1 flip-flop** (+ cadena de acarreo), empaquetados en la misma celda | `nextpnr-ice40`, tras place & route |
| **LUT6 / FF** (Artix-7) | Recursos **separados**: 4 LUT6 y 8 FF por slice | `yosys synth_xilinx`, y Vivado tras P&R |
| **"logic cell"** (Xilinx) | **Nada.** Es LUT6 × 1,6, una unidad de catálogo | La ficha comercial, nunca un sintetizador |

En el iCE40 la LUT y el flip-flop **comparten celda**: un registro sin lógica
combinacional detrás igual quema una LC entera. En el Artix-7 son recursos
independientes y se agotan por separado. **Un número de una columna no se puede
llevar a la otra por multiplicación.**

### 1.2 Los números, verificados contra DS180

Fuente primaria: **DS180 v2.6.1, 8-sep-2020, Tabla 4 "Artix-7 FPGA Feature
Summary by Device"**, fila `XC7A100T`, descargada y leída directamente:

| Campo | Valor |
|---|---|
| Logic Cells | **101.440** |
| CLB Slices | **15.850** |
| Max Distributed RAM | 1.188 Kb |
| **DSP48E1 Slices** | **240** |
| Block RAM: 18 Kb / 36 Kb / Max | 270 / **135** / **4.860 Kb** |
| CMTs · PCIe · GTPs · XADC | 6 · 1 · 8 · 1 |
| Max User I/O | 300 |

Y la **nota 1 de esa misma tabla**, literal:

> *"Each 7 series FPGA slice contains four LUTs and eight flip-flops; only some
> slices can use their LUTs as distributed RAM or SRLs."*

De donde:

$$15.850 \text{ slices} \times 4 = \mathbf{63.400 \text{ LUT6}}$$
$$15.850 \text{ slices} \times 8 = \mathbf{126.800 \text{ flip-flops}}$$

### 1.3 La vara independiente para el factor 1,6

Podría decir "el logic cell de Xilinx es LUT6 × 1,6" de memoria. **Eso no es
una verificación.** DS180 no enuncia el factor en ninguna parte: publica las
dos columnas y deja que el lector las divida. Así que la prueba se hace con la
tabla misma, sobre **los ocho dispositivos Artix-7 a la vez**:

| Dispositivo | Logic Cells | Slices | Slices × 4 | LC / (Slices×4) |
|---|---|---|---|---|
| XC7A12T | 12.800 | 2.000 | 8.000 | **1,600** |
| XC7A15T | 16.640 | 2.600 | 10.400 | **1,600** |
| XC7A25T | 23.360 | 3.650 | 14.600 | **1,600** |
| XC7A35T | 33.280 | 5.200 | 20.800 | **1,600** |
| XC7A50T | 52.160 | 8.150 | 32.600 | **1,600** |
| XC7A75T | 75.520 | 11.800 | 47.200 | **1,600** |
| **XC7A100T** | **101.440** | **15.850** | **63.400** | **1,600** |
| XC7A200T | 215.360 | 33.650 | 134.600 | **1,600** |

**Ocho de ocho dan 1,600 exacto.** Una relación que se cumple en ocho filas
independientes no es una coincidencia ni un recuerdo: es la definición,
recuperada de los datos. El "logic cell" es una **LUT4-equivalente** con la que
Xilinx expresa una LUT6, y por eso mismo **no corresponde a ningún recurso que
un sintetizador pueda reportar**.

### 1.4 Qué significa "cabe" en cada placa

**Go Board (iCE40HX1K).** Un solo criterio: `ICESTORM_LC ≤ 1.280` tras place &
route, y `nextpnr` lo dice o aborta. Es un veredicto **binario y duro**, y por
eso el "NO CABE" de `SINTESIS.md` §4 es firme.

**Arty A7-100T.** "Cabe" son **cuatro condiciones simultáneas más una quinta
que ninguna herramienta libre puede evaluar acá**:

1. LUT6 ≤ 63.400
2. Flip-flops ≤ 126.800
3. DSP48E1 ≤ 240
4. BRAM de 36 Kb ≤ 135
5. **…y que el place & route cierre**: LUT y FF no son independientes, se
   empaquetan de a 4 y 8 en el mismo slice. Un diseño con muchos registros y
   poca lógica puede agotar **slices** sin agotar ninguna de las dos cuentas
   crudas. Sin Vivado esto **no se puede verificar** y se declara.

Por eso, de todo lo que sigue, lo único que se afirma sin reservas son las
**cuentas de celdas del mapeo**. Un "cabe" del Artix-7 en este documento
significa "las cuatro cuentas dan holgadamente" y **no** "Vivado cerró".

### 1.5 La comparación honesta entre las dos placas

No se convierte nada. Se pone **el mismo diseño** medido en cada familia:

| | iCE40HX1K (Go Board) | XC7A100T (Arty A7) |
|---|---|---|
| Campeón F1, área | **1.545 ICESTORM_LC** (P&R) | 222 LUT6 + 569 FF + **1 DSP48E1** (mapeo) |
| Contra la capacidad | **120,7% — NO CABE** | 0,35% LUT · 0,45% FF · 0,42% DSP |
| Piso de slices (derivado) | — | ≥ 72 de 15.850 = **0,45%** |

La diferencia **no la explica el tamaño de la LUT**. La explica una sola cosa:
de esas 1.545 celdas del iCE40, **803 son el multiplicador** (`SINTESIS.md`
§4.1), y en el Artix-7 ese multiplicador cuesta **un bloque dedicado y cero
LUTs**. `fpga.md` §3 lo había dicho antes de medir nada — *"la fila que más
importa no es la de LUTs, es la de multiplicadores dedicados"* — y sigue siendo
la frase más exacta de todo el frente.

*(Nota de unidades del otro lado: `iCE40HX1K` = 1.280 Logic Cells, cada una
"LUT + Flip-Flop" según la hoja de datos iCE40 LP/HX de Lattice. La cuenta de
`ICESTORM_LC` de `nextpnr` es esa misma celda. Acá sí coinciden la unidad de
catálogo y la del sintetizador, que es justamente lo que NO pasa del lado de
Xilinx.)*

---

## 2. B1 — La consecuencia de no tener Vivado

El detalle completo está en `micro/TOOLCHAIN.md` §3. Lo que hay que saber para
leer este documento:

- La edición que cubre la XC7A100T hoy es el **tier BASIC, gratis**, con
  renovación anual sin costo. Los nombres "WebPACK" y "Standard Edition"
  quedaron **retirados** con el modelo de tiers que arrancó en 2026.1.
- **No se instaló.** El bloqueo no es disco (946 GB libres), ni RAM (31 GB), ni
  root (Vivado instala en `$HOME`): es la **cuenta AMD + formulario de control
  de exportación** que guarda cada descarga.
- **Consecuencia dura:** sin place & route no hay **Fmax**, no hay utilización
  real de slices, no hay reporte de temporización y no hay bitstream. Todo lo
  de las §3 y §4 es **mapeo tecnológico**: más duro que una cuenta a mano,
  más blando que Vivado. Se publica como lo que es.

---

## 3. B2 — El presupuesto real y el cuello verdadero

### 3.1 El presupuesto, medido

`yosys synth_xilinx -family xc7 -flatten`, top = `sint_top` (el envoltorio de
placa: pipeline + UART RX + carga de pesos), reproducido de `SINTESIS.md` §7 y
extendido con BRAM y CARRY4:

| cfg | DSP48E1 | LUT6 | FF | CARRY4 | BRAM | %DSP | %LUT | %FF | %BRAM |
|---|---|---|---|---|---|---|---|---|---|
| F1SP | 0 | 189 | 522 | 32 | **0** | 0,00% | 0,30% | 0,41% | 0,00% |
| **F1 (campeón)** | **1** | **222** | **569** | 32 | **0** | **0,42%** | **0,35%** | **0,45%** | **0,00%** |
| F3 | 4 | 347 | 892 | 51 | **0** | 1,67% | 0,55% | 0,70% | 0,00% |
| F6 | 7 | 504 | 1.132 | 51 | **0** | 2,92% | 0,79% | 0,89% | 0,00% |

**Sin Fmax**, y no por olvido: exige place & route.

Dato que la corrida anterior no había reportado y que resulta decisivo:
**BRAM = 0 en las cuatro configuraciones**. La ventana rodante de 10 valores
vive en flip-flops (160 bits), muy por debajo del punto en que una BRAM
conviene. El diseño de hoy **no toca la memoria de bloque ni una vez**.

### 3.2 Candidato 2: la BRAM — sobra por dos órdenes de magnitud

| | bits | vs 4.976.640 bits de BRAM |
|---|---|---|
| Un mensaje del formato de wire | 224 | 0,0045% |
| Una sesión completa (8 tickers × 28 B) | 1.792 | 0,036% |
| **Toda la historia sellada** (189 filas × 28 B = 5.292 B) | 42.336 | **0,85%** — 2 bloques de 36 Kb de 135 |
| `senales.db` **entera** (397.312 B) | 3.178.496 | **63,9%** |

*(4.860 Kb de DS180 con Kb = 1.024 bits → 4.976.640 bits = 607,5 KiB.)*

**La base de datos completa del proyecto entra en la BRAM del chip.** No es una
curiosidad: es la que decide la arquitectura de la demo del ramo. El vector de
validación se puede precargar en BRAM y reproducirse desde adentro, sin DDR3L,
sin controlador de memoria, sin MIG y sin el riesgo de temporización que
arrastra una interfaz DDR. **La BRAM no es el cuello: es la que elimina un
cuello.**

### 3.3 Candidato 3: el ancho de banda de la DDR3L — el cálculo que decide

**Primero, la unidad, porque la ficha del fabricante se contradice a sí misma.**
El manual de referencia de la Arty A7 dice en la lista de características
(pág. 6): *"256MB DDR3L with a 16-bit bus @ 667MHz"*. Pero su **Tabla 2**
(pág. 18), "DDR3L settings for the Arty A7", dice:

| Campo | Valor |
|---|---|
| Memory type | DDR3 SDRAM |
| **Max. clock period** | **3000 ps (667 Mbps data rate)** |
| Memory part | MT41K128M16JT-125 |
| Recommended Input Clock Period | 6000 ps (166,667 MHz) |

**Las dos frases difieren en un factor 2 en las unidades.** 3000 ps de período
son **333,33 MHz de reloj de memoria**; DDR transfiere en los dos flancos, o
sea **666,67 Mb/s por pin de datos** — que es exactamente lo que dice la tabla
("667 Mbps"), y **no** 667 MHz. **Gana la tabla**, por el criterio de la casa:
trae el período en picosegundos, así que es comprobable sin creerle a nadie.
La viñeta de marketing confunde MHz con Mb/s.

**El cálculo:**

$$16 \text{ bits} \times 666{,}67 \text{ Mb/s/pin} = 10{,}667 \text{ Gb/s} = \mathbf{1.333 \text{ MB/s}}$$

*(= 1,242 GiB/s. Es el **pico teórico**: refresco, cambios de fila, vueltas del
bus y la eficiencia del MIG lo bajan. Un 60-70% sostenido, ~800-930 MB/s, es lo
típico, pero eso es **ESTIMACIÓN** — sin placa no se midió y no se afirma.)*

**Contra lo que el pipeline necesita, que es la cuenta que el encargo pedía:**

| Magnitud | Valor | A pico de DDR3L |
|---|---|---|
| Un mensaje (una predicción de un ticker) | 28 B | 21 ns |
| **Una sesión** (8 tickers de `MERCADOS_POR_ABRIR`) | **224 B** | **168 ns** |
| Toda la historia sellada (189 filas) | 5.292 B | **3,97 µs** |
| Mensajes/s para **saturar** la DDR3L | **47,6 millones/s** | 100% |
| Lo que la plataforma **emite de verdad** | **8 por día** = 9,3 × 10⁻⁵ /s | **1,9 × 10⁻¹²** del pico |

**Margen: 5,1 × 10¹¹.** La DDR3L entrega la historia sellada entera del
proyecto en **3,97 µs**, que es **una vez y media la latencia de una sola
decisión** a 12 MHz (2,67 µs).

**Dónde SÍ topa la DDR3L, con número.** Un pipeline alimentado a B bytes por
ciclo a 100 MHz demanda B × 100 MB/s. Igualando a 1.333 MB/s:

$$B_{\text{crítico}} = \frac{1.333 \text{ MB/s}}{100 \text{ MB/s por byte/ciclo}} = \mathbf{13{,}33 \text{ bytes/ciclo}}$$

O sea: **un solo pipeline con ingesta de 14 bytes/ciclo o más ya excede la
DDR3L**. Es el único escenario de todo este estudio donde la memoria externa
es el límite, y es un escenario sintético — la §4.1 muestra que el ancho útil
está muy por debajo.

### 3.4 Candidato 1: los 240 DSP48E1 — el que topa primero, medido

Se sintetizaron **K instancias reales** del pipeline (`micro/rtl/multi_top.v`),
una por ticker, cada una con su propio flujo de bytes y su propio banco de
pesos, para que el sintetizador no pueda fusionarlas:

| K | DSP48E1 | LUT6 | FF | CARRY4 | %DSP | %LUT | %FF |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 80 | 338 | 24 | 0,42% | 0,13% | 0,27% |
| 2 | 2 | 157 | 676 | 48 | 0,83% | 0,25% | 0,53% |
| 4 | 4 | 312 | 1.352 | 96 | 1,67% | 0,49% | 1,07% |
| **8** (el universo real) | **8** | **622** | **2.704** | 192 | **3,33%** | **0,98%** | **2,13%** |
| 16 | 16 | 1.238 | 5.408 | 384 | 6,67% | 1,95% | 4,26% |
| 32 | 32 | 2.487 | 10.816 | 768 | 13,33% | 3,92% | 8,53% |
| 64 | 64 | 4.964 | 21.632 | 1.536 | 26,67% | 7,83% | 17,06% |

**Costo marginal medido entre K=1 y K=64: 77,5 LUT6 · 338,0 FF · 1,00 DSP48E1
por ticker.** La pendiente es lineal en las siete medidas — el mapeo no
comparte nada entre instancias, que es lo que se esperaba y lo que confirma que
las instancias son independientes de verdad.

Extrapolando esa pendiente medida:

| Recurso | Tope |
|---|---|
| **DSP48E1** | **240 tickers** ← el que topa primero |
| Flip-flops | 375 tickers |
| LUT6 | 817 tickers |

*(La pendiente se lee entre dos K medidos y no dividiendo un total por K,
porque `SINTESIS.md` §3.4 ya midió que el área de un pipeline no es la suma de
sus partes. Acá resultó aditiva; eso es un resultado, no un supuesto.)*

### 3.5 Veredicto de B2

**Para la carga real de MKI, el cuello no es ninguno de los tres.** Es la
**tasa de llegada de los datos**: una sesión del SOX por día. Ninguna FPGA
cambia eso, y decir lo contrario sería exactamente lo que
`GEMELO/MICRO/piso_de_latencia.md` ya descartó con evidencia.

**Para la pregunta "cuánto diseño entra", el cuello es el DSP48E1, a 240
pipelines replicados** — 30 veces el universo de 8 tickers. La BRAM sobra por
dos órdenes de magnitud y la DDR3L por once; la DDR3L sólo se vuelve el límite
en una configuración sintética (ingesta ≥ 14 bytes/ciclo en un solo pipeline)
que la §4.1 muestra que no hace falta.

**Y hay una lectura más útil que "cuál de los tres":** la replicación espacial
es la respuesta a *cuánto cabe*, no a *cuánto hace falta*. Un solo pipeline a
100 MHz entrega una decisión con **5 a 32 ciclos de latencia**, o sea entre 50 y
320 ns cada una. El sistema emite **ocho por día**. La forma correcta de servir
8 tickers no es 8 pipelines: es **uno multiplexado en el tiempo**, y sobra tanto
que ni siquiera hace falta multiplexar bien.

*(Se dice "latencia" y no "throughput" a propósito: el throughput sostenido
espalda-con-espalda **sigue sin medirse** — `SINTESIS.md` §9 —, porque el banco
inserta 8 ciclos de silencio entre mensajes. Convertir una latencia en un
caudal sería justo el tipo de inferencia que este proyecto no se permite. Para
ocho mensajes diarios no hace falta medirlo para saber que sobra.)*

---

## 4. B3 — Qué compra el margen, ordenado por lo que le sirve al proyecto

El orden es por utilidad para MKI y para el ramo, **no** por lo que impresiona.
Por eso (d) va primero y (a) va último.

### 4.1 (d) La latencia — lo único que compra algo de verdad, y sale gratis

**El diagnóstico primero.** `pipeline_top.v` desglosa los 32 ciclos medidos:
**27 son la ingesta byte a byte** y **5 son las cuatro etapas restantes**. O
sea que **el 84% de la latencia determinista que este proyecto exhibe no es
cómputo: es el ancho del bus de entrada.**

**El encargo preguntaba qué etapas están hoy "serializadas por falta de espacio"
y ahora podrían ir en paralelo. La respuesta medida es: NINGUNA.** Las etapas 2
a 5 ya corren encadenadas, un ciclo cada una, y ninguna se partió por
presupuesto de LUTs. Lo único serializado es el parser, y no por falta de
espacio sino porque el diseño supuso un flujo de un byte por ciclo (un UART).
La premisa de la pregunta era falsa y se dice en vez de contestarla igual.

**Lo que sí se midió.** Se construyó `micro/rtl/etapa_ingesta_ancha.v`
(parametrizada en B bytes por ciclo) y `pipeline_top_ancho.v`, que instancia
**las mismas etapas 2 a 5, sin un solo cambio**. La predicción
`latencia = ceil(28/B) + 4` quedó escrita **antes** de correr, y el banco de
pruebas falla si no se cumple.

| B (bytes/ciclo) | palabras | **latencia MEDIDA** | a 100 MHz | LUT6 | FF | LUT4 iCE40 | bit a bit |
|---|---|---|---|---|---|---|---|
| **1 (hoy)** | 28 | **32 ciclos** | 320 ns | 108 | 360 | 948 | **181/181** |
| 2 | 14 | **18 ciclos** | 180 ns | 103 | 359 | 940 | **181/181** |
| **4** | 7 | **11 ciclos** | 110 ns | **102** | 358 | 935 | **181/181** |
| 7 | 4 | **8 ciclos** | 80 ns | 98 | 357 | 935 | **181/181** |
| 14 | 2 | **6 ciclos** | 60 ns | 96 | 356 | 933 | **181/181** |
| 28 | 1 | **5 ciclos** | 50 ns | **93** | 355 | 931 | **181/181** |

Tres cosas que hay que leer juntas:

1. **La fila B=1 da 32 ciclos exactos**, que es lo que `tb_pipeline.v` ya había
   medido sobre el `pipeline_top` original. **Ése es el control**: prueba que
   la variante no cambió nada más que la ingesta. Sin esa fila, ninguna de las
   otras cinco significaría nada.
2. **Las 181 filas selladas reproducen bit a bit en los seis anchos**, y la
   latencia es constante dentro de cada uno (mín = máx en los 181 vectores). La
   propiedad que el proyecto afirma tener **sobrevive** al ensanchado.
3. **El área BAJA**: 108 → 93 LUT6 en Artix-7, 948 → 931 LUT4 en iCE40. Menos
   estados de contador y menos decodificador. **La latencia no se compró con
   área: se compró con nada.**

**Y esto no necesitaba la placa nueva.** También baja en el iCE40. Nadie lo
había medido porque nadie lo había preguntado, no porque no cupiera. Es el
hallazgo más incómodo de esta corrida y por eso va primero.

**El límite realista, dicho sin adornos.** Un bus externo de 28 bytes son 224
pines. El chip tiene 300 I/O de usuario como máximo (DS180 Tabla 4), pero **la
placa expone muchísimos menos**: el manual de Digilent (§10) dice que cada uno
de los cuatro conectores Pmod entrega *"eight logic signals"* — **32 señales en
total** — más los conectores de shield Arduino/chipKIT, del orden de unas
decenas más. **Un ingreso paralelo ancho desde afuera es imposible en esta
placa, y ninguna placa de esta clase lo permitiría.** Donde sí
es directamente realizable es con una **fuente interna**: reproducir las filas
selladas desde BRAM (§3.2), que es exactamente la arquitectura de la demo del
ramo. **B=4 (32 bits) es el punto sensato**: latencia 11 ciclos, área menor que
hoy, y realizable incluso con una fuente externa.

### 4.2 (c) Varios tickers en paralelo — 240, y el número no es el interesante

Medido en la §3.4: **240 tickers antes de topar con el DSP48E1**, con las 8
posiciones del universo real ocupando el **3,33% de los DSP, 0,98% de las LUT y
2,13% de los flip-flops**.

Pero el número útil es el otro: **el universo entero de MKI (8 tickers) usa 8
de 240 DSP**, y todavía sobran 232. Y aun eso es sobredimensionar, porque
`RTL.md` §5 ya excluye del alcance entrenar nada en la FPGA y el sistema emite
8 predicciones por día. **La replicación espacial responde una pregunta que la
carga real no hace.**

Lo que el margen sí habilita en esta línea, y que hoy no existe: un
**banco de pesos por instrumento** en vez del registro único de configuración
que `pipeline_top.v` documenta como decisión de alcance. Con 240 DSP y 135
BRAM eso deja de ser una restricción y pasa a ser una tabla indexada por
`id_instrumento` — el campo ya viaja en el mensaje de 28 bytes y hoy sólo se
usa para sellar.

### 4.3 (b) El 4.6.0 COMPLETO — qué le falta al RTL, y cuánto cuesta

**Qué replica hoy el RTL:** `apertura_estimada_pct = beta × movimiento_SOX`, en
Q8.8, con **beta entrando ya calculada** por un registro de configuración. Eso
es el **punto** de la predicción y nada más.

**Qué le falta para ser el 4.6.0 completo.** Leyendo `motor.betas_al` y
`motor.prediccion_apertura_al` (sólo lectura, no se tocaron):

| # | Falta | Por qué importa |
|---|---|---|
| 1 | **La regresión rodante de 120 sesiones**: `beta = cov(x,y)/var(x)`, `alfa = mean(y) − beta·mean(x)` | Es de dónde SALE beta. Hoy entra por puerto. `RTL.md` §5 lo excluyó del alcance a propósito |
| 2 | **`r2 = corr(x,y)²`** | Va sellado en cada fila y alimenta la etiqueta de calidad |
| 3 | **`resid_std` y el intervalo del 80% = 1,2816 × σ** | **La Constitución 5.0 (4) obliga a mostrar incertidumbre junto a toda señal.** Sin esto el pipeline emite el punto pero **no puede emitir una fila sellada completa** |
| 4 | **`ultimo_movimiento_no_cero`** del SOX | La selección del insumo (saltar feriados ffilleados) hoy es off-chip |
| 5 | **`n_muestra`** y el mínimo de 40 observaciones | Es un criterio de admisión, no de cálculo |
| 6 | **Tabla de pesos por instrumento** | Hoy hay un banco único: un instrumento por vez |
| 7 | **Redondeo decimal a 2 cifras** | La base guarda decimal; el RTL es binario. Ver §4.4 |
| 8 | **Ausencia de dato** (`NaN`, ticker sin beta) | `motor` descarta filas; el RTL no tiene noción de "sin dato" |
| 9 | **Régimen, earnings, `available_at`, `sesion_objetivo`** | Son de la capa de sellado, no del cálculo. **Fuera de alcance por diseño**, no por espacio |

**Los puntos 1 a 3 son los que exigen silicio nuevo**, y son los que se
midieron. Las piezas no existían en `micro/rtl/`; se escribieron aisladas en
`micro/rtl/costo_a7.v` y se sintetizaron solas:

| Pieza | DSP48E1 | LUT6 | FF | CARRY4 | LUT4 iCE40 | vs HX1K |
|---|---|---|---|---|---|---|
| Divisor 32/32 **combinacional** (cota superior) | 0 | 1.297 | 32 | 416 | 809 | 63% |
| **Divisor 32/32 restaurador, 32 ciclos fijos** | 0 | **173** | 199 | 11 | 205 | 16% |
| **Raíz cuadrada 48→24, 24 ciclos fijos** | 0 | **176** | 149 | 15 | 196 | 15% |
| Momentos rodantes N=20 (Σx, Σy, Σxy, Σx²) | 4 | 293 | 832 | 48 | 3.950 | 309% |
| Momentos rodantes N=60 | 4 | 293 | 2.112 | 48 | 3.951 | 309% |
| **Momentos rodantes N=120** (la ventana real) | **4** | **293** | **4.032** | 48 | **3.954** | **309%** |

**Veredicto: sí cabe, y con enormidad de margen.** Sumando el pipeline actual
(222 LUT6, 569 FF, 1 DSP) con las piezas que faltan:

$$\approx 222 + 173 + 176 + 293 = \mathbf{864 \text{ LUT6}} \ (1{,}4\%) \qquad
\approx 569 + 199 + 149 + 4.032 = \mathbf{4.949 \text{ FF}} \ (3{,}9\%) \qquad
\mathbf{5 \text{ DSP48E1}} \ (2{,}1\%)$$

**Y hay que decir en qué sentido esa suma es floja:** `SINTESIS.md` §3.4 midió
que sumar áreas por etapa **subestima sistemáticamente** (45% en iCE40). Aun
con un 50% de castigo el total queda por debajo del 6% del chip. **La
conclusión aguanta la corrección; el método de la suma sigue siendo malo y por
eso se declara en vez de presentarlo como medición.**

**El contraste que resume la compra:** los mismos momentos rodantes de N=120
son **3.954 LUT4 en el iCE40 = 309% de la Go Board entera**. La regresión sola
—una sola de las nueve piezas faltantes— **es tres veces la placa vieja**. En
la Arty A7 es el 0,46% de las LUT y el 3,2% de los flip-flops.

**Lo que NO se midió y hay que decirlo:** ninguna de estas piezas se conectó al
pipeline ni se validó contra `motor.py`. **Se midió su costo, no su
corrección.** Reproducir `betas_al` bit a bit contra Python es trabajo, no
una consecuencia de que quepa. Y hay una dificultad real esperándolo: `motor`
calcula en float64 sobre retornos porcentuales, y una regresión de 120 puntos
en punto fijo tiene problemas de rango y cancelación que una multiplicación no
tiene. **Eso es un proyecto, y está en el plan del ramo (`PROYECTO_RAMO.md`),
no en este documento.**

### 4.4 (a) Ensanchar el punto fijo — no compra nada, y se puede demostrar

#### 4.4.1 Primero, la cifra que el encargo pedía verificar

El encargo pedía verificar "el 0,063% del MAE publicado" **en `SINTESIS.md`**.

**Ese número no está en `SINTESIS.md`.** Está en **`RTL.md` §3**, y mide otra
cosa. Los dos números existen, los dos son correctos, y miden operaciones
distintas:

| Cifra | Dónde | Qué mide | Verificación |
|---|---|---|---|
| **0,00188 pp = 0,063% del MAE** | `RTL.md` §3 | Error de cuantizar **UN** valor a Q8.8 | 0,00188 / 2,98 = 0,000631 ✔ |
| **0,00474 pp = 0,16% del MAE** | `SINTESIS.md` §5 | Error del **puntaje entero completo** contra float64 (producto de dos cuantizados + truncado) | 0,00474 / 2,98 = 0,00159 ✔ |

El MAE del gap de **2,98 pp** es el publicado en `README.md` (línea 137), que
es la fuente de verdad de cifras del proyecto. **Las dos aritméticas dan.**

`SINTESIS.md` §5 ya había explicado por qué el segundo es 2,5 veces el primero:
la tolerancia de `RTL.md` se derivó para la operación equivocada. **La cifra
correcta para "cuánto se pierde por el punto fijo del pipeline" es 0,16%, no
0,063%.** El encargo citaba la que corresponde a otra operación.

#### 4.4.2 Contra qué "desaparecería" la pérdida — la pregunta que decide

Hay dos referencias posibles y **dan respuestas opuestas**. Medido sobre las
**189 filas selladas** de hoy (`micro/rtl/medir_ancho_error.py`, `mode=ro`):

| Formato | LSB | **A**: máx vs float64 | A: medio | **B**: máx vs fila SELLADA | B: medio | signos cambiados |
|---|---|---|---|---|---|---|
| **Q8.8 / Q2.14 (hoy)** | 0,00391 | **0,004740** | 0,002032 | **0,027344** | 0,005885 | 0 |
| Q10.10 / Q2.18 | 0,00098 | 0,001236 | 0,000483 | 0,027344 | 0,005584 | 0 |
| Q12.12 / Q2.22 | 0,00024 | 0,000272 | 0,000117 | 0,026855 | 0,005566 | 0 |
| Q14.14 / Q2.26 | 0,00006 | 0,000077 | 0,000033 | 0,026794 | 0,005571 | 0 |
| **Q16.16 / Q2.30** | 0,00002 | **0,000019** | 0,000008 | **0,026749** | 0,005572 | 0 |

*(La columna A a Q8.8 da **0,004740 pp**, idéntica al valor que `SINTESIS.md`
§5 midió sobre 181 filas por otro camino — el arnés de simulación. Dos métodos
distintos, mismo número: eso es la vara independiente.)*

**La columna A cae 250 veces. La columna B no se mueve.** El error contra lo
que el proyecto realmente selló pasa de 0,027344 a 0,026749 pp: una mejora del
**2,2%** a cambio de duplicar el ancho.

**Por qué.** `senales.db` guarda `apertura_estimada_pct` y `beta` con **dos
decimales** (`round(x, 2)` en `motor.py`). El error de almacenamiento es de
hasta **±0,005 pp**, que es **más grueso que el LSB de Q8.8** (0,0039 pp).
**El dato de referencia ya está cuantizado más grueso que el hardware que se le
compara.** Ensanchar el punto fijo mejora la fidelidad contra un álgebra que
nadie selló, y no mejora la fidelidad contra lo que sí se selló.

#### 4.4.3 Y cuánto costaría intentarlo igual

Medido sobre `etapa_puntaje` sola, con los anchos sobrescritos por macro:

| Formato | F | DSP48E1 | LUT6 | FF | LUT4 iCE40 | vs HX1K |
|---|---|---|---|---|---|---|
| **Q8.8 / Q2.14 (hoy)** | 1 | **1** | 17 | 37 | 781 | 61% |
| Q12.12 / Q2.22 | 1 | **2** | 25 | 53 | 1.766 | 138% |
| Q16.16 / Q2.30 | 1 | **4** | 80 | 69 | 3.054 | 239% |
| Q8.8 / Q2.14 | 6 | 6 | 230 | 211 | 5.019 | 392% |
| Q12.12 / Q2.22 | 6 | 12 | 334 | 315 | 11.113 | 868% |
| Q16.16 / Q2.30 | 6 | 24 | 715 | 419 | 18.887 | 1476% |

**El salto de DSP no es lineal y hay una razón física**, verificada contra
DS180 Tabla 4 nota 2: *"Each DSP slice contains a pre-adder, a 25 x 18
multiplier, an adder, and an accumulator"*. Medido en aislamiento:

| Multiplicador con signo | DSP48E1 | LUT6 | LUT4 iCE40 |
|---|---|---|---|
| 8 × 8 | 1 | 0 | 177 |
| **16 × 16 (hoy)** | **1** | **0** | 774 |
| **25 × 18 (el nativo del DSP48E1)** | **1** | **0** | 1.298 |
| 18 × 18 | 1 | 0 | 975 |
| 24 × 24 | **2** | 0 | 1.764 |
| 25 × 25 | **2** | 0 | 1.898 |
| **32 × 32** | **4** | 47 | 3.050 |

**Q8.8 vive dentro del multiplicador nativo con margen de sobra; Q16.16 lo
excede y cuesta cuatro DSP y LUTs además.** El punto fijo elegido en `RTL.md`
§3 resulta, sin haberlo buscado, **exactamente el ancho que la placa comprada
hace gratis**.

**Conclusión de (a): no hay ancho que haga desaparecer la pérdida, porque la
pérdida que queda no es del hardware.** La única forma de bajar la columna B
sería que la base guardara más decimales, y eso **no se puede hacer**: la
Constitución 5.0 (3) prohíbe reescribir filas selladas, así que el piso de
±0,005 pp de las 189 filas ya existentes es permanente. **La aritmética se
queda en Q8.8 y el motivo ahora está medido, no supuesto.**

---

## 5. Qué es medición y qué es estimación en este documento

| Afirmación | Estado |
|---|---|
| Celdas del mapeo en XC7A100T (LUT6/FF/DSP/BRAM/CARRY4) | **MEDIDO** — `yosys synth_xilinx -family xc7` |
| Latencias de 32/18/11/8/6/5 ciclos y 181/181 bit a bit | **MEDIDO** — Icarus sobre los 181 vectores reales |
| Costo de multiplicadores, divisor, raíz y momentos | **MEDIDO** — síntesis aislada por módulo |
| Escalado a K tickers y tope de 240 | **MEDIDO** hasta K=64, **EXTRAPOLADO** de ahí a 240 con la pendiente medida |
| Error de cuantización por ancho (columnas A y B) | **MEDIDO** sobre 189 filas selladas |
| Capacidades del XC7A100T y del DSP48E1 | **VERIFICADO** contra DS180 v2.6.1 Tabla 4 |
| DDR3L: 1.333 MB/s de pico | **CÁLCULO** sobre la Tabla 2 del manual de Digilent |
| DDR3L: 800-930 MB/s sostenidos | **ESTIMACIÓN** — sin placa no se midió |
| **Fmax en Artix-7** | **NO EXISTE** — exige place & route (Vivado o nextpnr-xilinx) |
| **Utilización de slices tras P&R** | **NO EXISTE** — el "piso de slices" es una cota, no una predicción |
| **Que el diseño cierre temporización a X MHz** | **NO EXISTE** |
| Corrección de las piezas del 4.6.0 completo | **NO MEDIDA** — se midió su costo, no que calculen bien |

**Cambio de denominador que hay que declarar:** las tablas de simulación usan
**181** filas (el vector generado el 31-ago para `SINTESIS.md`) y la §4.4.2 usa
**189** (las que hay hoy en `senales.db`, que siguió sellando). No se
regeneraron los vectores a propósito, para que las cifras publicadas en
`SINTESIS.md` se puedan comparar de frente. Regenerar con `make vectores`
moverá los 181 a 189 y con eso todas las tablas de simulación.

---

## 6. Marcado explícitamente como decisión de Nicolás

1. **Crear la cuenta AMD y aceptar el formulario de control de exportación**
   para descargar Vivado. Es un acto de identidad, de la misma clase que
   pushear a GitHub, y la Constitución 5.0 (5) ya reserva esa clase para él.
   **Sin esto no hay Fmax, no hay bitstream y no hay placa programada.**
2. **Si el pipeline crece hacia el 4.6.0 completo o se queda en el campeón.**
   La §4.3 dice que cabe con margen enorme y enumera las nueve piezas
   faltantes. **No dice que valga la pena**, y `RTL.md` §5 ya lo había excluido
   del alcance del ramo. Es alcance académico, no una restricción técnica.
3. **El ancho de la ingesta.** B=4 es el punto sensato (11 ciclos, menos área,
   realizable con fuente externa); B=28 da 5 ciclos pero sólo con fuente
   interna desde BRAM. Ninguno se eligió acá.
4. **Qué hacer con la tolerancia de 0,00188 pp** — sigue abierta desde
   `SINTESIS.md` §8.4. La §4.4 agrega evidencia: ningún ancho la alcanza y el
   piso lo pone la base, no el hardware.
5. **Si se mide el multiplicador serie** de `SINTESIS.md` §4.2(b). Con la placa
   comprada **la razón que lo motivaba desapareció**: era para hacer entrar el
   campeón en el iCE40. Se marca por completitud, no porque haga falta.
6. **Si el proyecto del ramo usa la Go Board para algo.** El F1SP (solo umbral)
   cabe en ella con 742/1.280 LCs y 114 MHz. Tener dos placas habilita una
   comparación de arquitecturas que ninguna sola permite — y también puede ser
   una distracción. Es alcance, no técnica.

---

## 7. Discrepancias encontradas, sin corregir en su fuente

Se listan acta por acta. Ninguna se arregló en el documento original: las tres
son de documentos ya publicados y les corresponde una errata fechada, no una
reescritura silenciosa.

1. **`RTL.md` §3 y el encargo de esta corrida citan 0,063%; `SINTESIS.md` §5
   mide 0,16%.** No es una contradicción: son dos operaciones distintas y las
   dos aritméticas dan. Lo que sí es un error es citar el 0,063% como "la
   pérdida del pipeline" — la del pipeline es 0,16% (§4.4.1).
   **Estado: ya cerrada en su fuente.** `RTL.md` recibió el mismo 31-ago dos
   **erratas fechadas** (§3 y §4) que dicen exactamente esto y dejan el texto
   original arriba de cada nota. Esta corrida lo encontró por un camino
   distinto —el barrido de anchos de la §4.4— y llega a la misma conclusión.
   **Dos rutas independientes al mismo hallazgo es la mejor confirmación que
   había disponible.**
2. **El manual de la Arty A7 se contradice a sí mismo en las unidades de la
   DDR3L**: "@ 667MHz" en la lista de características contra "3000 ps
   (667 Mbps)" en la Tabla 2. Factor 2. Gana la tabla (§3.3). Es del
   fabricante, no del proyecto — se anota para que nadie cite los 667 MHz.
3. **La creencia extendida de que Vivado 2026.1 sacó Linux del tier gratis está
   contradicha por las dos fuentes primarias de AMD** consultadas hoy. Detalle
   en `micro/TOOLCHAIN.md` §3.

---

## 8. Qué queda pendiente

- **Place & route real** (Fmax, slices, temporización, bitstream). Bloqueado
  por la §6.1.
- **Medición sobre placa física** — paso 5 del protocolo de `RTL.md` §4. Ahora
  falta la herramienta y el JTAG, ya no la placa.
- **Throughput espalda-con-espalda.** Sigue sin medirse, igual que en
  `SINTESIS.md` §9: el banco inserta 8 ciclos de silencio entre mensajes para
  que la latencia se mida limpia.
- **Corrección** (no costo) de las piezas del 4.6.0 completo: reproducir
  `betas_al` en punto fijo contra `motor.py` en float64.
- **La ingesta ancha desde BRAM**: hoy la fuente del testbench es el propio
  banco de pruebas. Un reproductor desde BRAM es RTL nuevo y no está escrito.
