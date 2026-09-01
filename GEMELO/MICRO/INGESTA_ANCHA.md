# La ingesta ancha, confirmada — el techo recalculado, dos variantes, y por qué nadie preguntó

**Fecha:** 1-sep-2026. **Estado:** medido, salvo lo que se marca como
ESTIMACIÓN, CÁLCULO o EXTRAPOLACIÓN.
**Placa:** Digilent Arty A7-100T, **XC7A100TCSG324-1**. Ya comprada.
**Insumos:** `GEMELO/MICRO/SINTESIS_A7.md` (la corrida anterior),
`GEMELO/MICRO/SINTESIS.md`, `GEMELO/MICRO/RTL.md`, `GEMELO/MICRO/fpga.md`.
**Herramientas:** yosys 0.68+136, nextpnr-ice40, Icarus Verilog 14.0.
**Reproducible con:** `cd micro/rtl && make ancho ancho-gate techo variantes multi demo huecos semillas`
(los ocho objetivos se corrieron enteros y sus registros quedan en
`micro/rtl/sim/` y `micro/rtl/sintesis/`, ambos gitignoreados y regenerables).

> **Regla que gobierna este documento.** Una verificación que usa el mismo
> mecanismo que produjo la cifra NO es una verificación. Las dos cifras que
> este frente tenía que confirmar —11 ciclos a 4 B/ciclo y 181/181 bit a bit—
> las produjo el RTL simulado leyendo el contador que vive dentro del propio
> diseño. Acá se cambiaron **las dos cosas a la vez**: otro instrumento (una
> cuenta de flancos del lado del banco, ciega al contador del DUT) y otro
> diseño bajo prueba (la **netlist mapeada a celdas**, iCE40 y Artix-7, donde
> ya no hay Verilog sino LUT6, CARRY4, FDRE y DSP48E1). Ver §1.2.
>
> **Regla cero heredada:** `motor.py`, `senales.py`, `snapshot.py` y
> `universo.py` no se tocaron; `senales.db` no se abrió ni una vez en este
> frente — los vectores son los de 31-ago y se re-agruparon, no se
> regeneraron (§7). Ninguna cifra se ajustó para que algo quepa.

---

## 0. Resumen ejecutivo

1. **Las dos cifras se CONFIRMAN, y con evidencia de dos familias que antes no
   existían** (§1). 11 ciclos a B=4, 5 a B=28, área que **baja** de 108 a 93
   LUT6, y **181/181 bit a bit en los seis anchos**. La novedad no es que se
   repita: es que ahora los 181 vectores y las latencias sobreviven también a
   la **simulación a nivel de compuerta sobre la netlist mapeada a celdas
   Artix-7 reales**, DSP48E1 incluido. Es la evidencia más dura disponible sin
   placa programada.
2. **El techo NO se movió: sigue siendo 240 tickers, y el cuello sigue siendo
   el DSP48E1** (§2). Medido sintetizando el barrido entero de nuevo con B=4 y
   B=28, no deducido. Y el resultado tiene una lectura que el número no dice:
   ensanchar la ingesta **agranda** la ventaja del DSP como cuello, porque baja
   LUT y FF por instancia y no toca el DSP. El techo de LUT6 sube de 817 a
   1.006 tickers; el de DSP no se mueve un ticker.
3. **La razón es estructural y ahora está medida: la latencia vive en el
   parser (contador + decodificador = LUT y FF) y el techo lo pone la cuenta de
   MULTIPLICACIONES** (§2.2). Replicar K pipelines multiplica las
   multiplicaciones una a una; ensanchar el bus no crea ni destruye ninguna.
   Son dos ejes ortogonales **de este diseño**, y se dice "de este diseño"
   porque es lo que se midió, no un teorema.
4. **Subir el techo por el camino obvio EMPEORA las cosas** (§2.3). Mapear el
   multiplicador a fabric (`-nodsp`) cuesta **685,8 LUT6 por ticker** medidos y
   baja el techo de 240 a **92**. Es un resultado negativo y se publica igual.
5. **El camino que sí lo sube es el que los propios documentos del proyecto
   nombraron tres veces sin construirlo** (§3.1): un pipeline con **tabla de
   pesos por instrumento**. Ocho instrumentos cuestan **1 DSP, 109 LUT6 y 358
   FF** contra los 8 DSP, 577 LUT6 y 2.688 FF de replicar ocho pipelines. Una
   tabla de **240 instrumentos** —treinta veces el universo— cuesta **3 DSP y
   119 LUT6**. El techo deja de ser una cuenta de DSP.
6. **La fuente interna desde memoria existe y funciona** (§3.2). `demo_top`
   reproduce las 181 filas selladas desde la memoria del chip con **un solo
   pulso de arranque**, sin UART, sin DDR3L y sin un pin de datos: **181/181
   bit a bit** a 11 ciclos (B=4) y a **5 ciclos (B=28)**. Es la primera
   configuración de todo el proyecto que usa BRAM (hasta hoy, cero en todas).
   Y es lo que vuelve realizable el B=28: 28 bytes en paralelo son 224 pines y
   la placa expone 32 señales por los Pmod.
7. **Hallazgo que no se buscaba, y es el más incómodo de esta corrida**
   (§3.3): **el silencio de 8 ciclos entre mensajes no es una comodidad del
   banco de pruebas — es un requisito de corrección que nadie había escrito.**
   Con 0 ó 1 ciclos de hueco, **178 de 181 sellos salen mal, corridos un
   mensaje**… y **la latencia sigue dando 11 ciclos exactos y perfectamente
   constante**. Una prueba que sólo mirara la latencia habría pasado en verde.
   El mínimo medido es **2 ciclos**, igual en B=4 y B=28. Hay un guardia en el
   código desde hoy. De paso queda medido el **caudal espalda-con-espalda**,
   pendiente desde `SINTESIS.md` §9: **15,00 ciclos por mensaje con B=4** y
   **9,00 con B=28**, contando el reloj de la simulación entera y dividiendo —
   no convirtiendo una latencia en un caudal.
8. **La errata del iCE40, y su parte interesante** (§4). La mejora también
   aplicaba a la Go Board —el área baja ahí también, **1.198 → 1.184 celdas
   colocadas y ruteadas**— o sea que **no estaba bloqueada por falta de
   espacio**. Pero la explicación de por qué nadie preguntó no es la que se
   suponía: la opción estaba **escrita** desde el primer documento
   (`RTL.md` §1: *"un byte (o un word, si el bus lo permite)"*), condicionada a
   una precondición sobre un bus externo que nadie tenía, y **la precondición
   nunca se volvió a evaluar**. No fue una idea que no se tuvo: fue una idea
   **estacionada**.
9. **Qué tiene intervalo y qué no, medido** (§6). Las cuentas de celdas son
   determinísticas (4/4 idénticas) pero **sensibles al contexto de la
   invocación**; las celdas colocadas por nextpnr son determinísticas (10/10
   idénticas); **el Fmax NO lo es**: sobre 10 semillas va de **66,11 a 73,00
   MHz** en un caso y de **105,27 a 114,19 MHz** en el otro. Todo Fmax
   publicado por este proyecto es un estimador puntual de una semilla sola.

---

## 1. E1 — Las dos cifras, confirmadas y luego atacadas por otro lado

### 1.1 La reproducción directa

`make ancho` sobre los mismos 181 vectores de 31-ago (no se regeneraron: §7).

| B (bytes/ciclo) | palabras | latencia PREDICHA | latencia MEDIDA | LUT6 xc7 | FF xc7 | LUT4 iCE40 | bit a bit |
|---|---|---|---|---|---|---|---|
| **1 (control)** | 28 | 32 | **32** | 108 | 360 | 948 | **181/181** |
| 2 | 14 | 18 | **18** | 103 | 359 | 940 | **181/181** |
| **4** | 7 | 11 | **11** | **102** | 358 | 935 | **181/181** |
| 7 | 4 | 8 | **8** | 98 | 357 | 935 | **181/181** |
| 14 | 2 | 6 | **6** | 96 | 356 | 933 | **181/181** |
| **28** | 1 | 5 | **5** | **93** | 355 | 931 | **181/181** |

**Idénticas, celda por celda, a la tabla de `SINTESIS_A7.md` §4.1.** La
latencia es constante dentro de cada ancho (mín = máx sobre los 181 vectores).

**Errata sobre código commiteado — y no es un arreglo de paso: es el
entregable de esta sección.** `medir_a7.py` imprimía en esa tabla la columna
"latencia" calculando `ceil(28/B)+4` —la **fórmula**— bajo un encabezado que
decía *"están MEDIDAS en simulación… no calculadas"*. Los números coincidían
porque la predicción era correcta, y por eso nadie lo vio. Pero **el encargo
de este frente era confirmar esas latencias**, y una cifra calculada rotulada
como medida no confirma nada: es la regla de la casa fallando adentro de la
herramienta que produce la cifra. Establecer la procedencia **era** el trabajo,
no un desvío. Ahora el bloque **lee** la latencia de `sim/ancho.log` y escribe
`sin medir` si el log no está, o `NO CONST` si no fue constante, con las dos
columnas separadas (PREDICHA / MEDIDA). La corrección va al código, no a una
nota al pie. Es la cuarta errata de esta corrida y la única sobre código;
las otras tres, sobre documentos, están en la §4.1.

### 1.2 La vara de otra familia — dos instrumentos y tres diseños bajo prueba

Repetir la misma simulación con el mismo banco no confirma nada. Se cambiaron
las dos variables a la vez (`make ancho-gate`, `tb/tb_pipeline_gate.v`):

**(a) Otro INSTRUMENTO.** La latencia publicada sale del registro
`latencia_ciclos`, que produce un contador libre de 48 bits dentro de
`etapa_salida` — o sea, del propio diseño. El banco nuevo la mide además
**contando flancos de reloj**, sin mirar ese contador. La relación quedó
**escrita antes de correr**: el DUT mide de `inicio_mensaje` a
`decision_valida`, y `sello_valido` va un ciclo después, luego
`ciclos_banco == latencia_ciclos + 1`, exacto, para todo caso y todo ancho.
**Resultado: 0 desajustes en 181 × 3 anchos × 3 diseños.** Alcance honesto:
esto es independiente del *contador* del diseño, no de la noción de "ciclo" —
las dos cuentas comparten el mismo reloj, y decir otra cosa sería exactamente
el error que la regla existe para evitar.

**(b) Otro DISEÑO BAJO PRUEBA.** El mismo banco se compiló contra la
**netlist mapeada a celdas**, donde ya no hay parámetros, ni bucles, ni
aritmética de Verilog: sólo celdas y sus modelos de simulación.

| Diseño bajo prueba | B=1 | B=4 | B=28 |
|---|---|---|---|
| RTL | 181/181 · 32 ciclos | 181/181 · **11 ciclos** | 181/181 · 5 ciclos |
| **Netlist iCE40** (SB_LUT4, SB_DFF, SB_CARRY) | 181/181 · 32 | 181/181 · **11** | 181/181 · 5 |
| **Netlist Artix-7** (LUT6, CARRY4, FDRE, **DSP48E1**) | 181/181 · 32 | 181/181 · **11** | 181/181 · 5 |

**Las 181 filas selladas y la latencia sobreviven al mapeo tecnológico en las
dos familias de celdas.** Es la evidencia más dura que se puede producir sin
programar la placa: no prueba temporización (eso exige P&R, §6), pero sí que
el diseño que el sintetizador realmente emite calcula lo mismo que el RTL.

### 1.3 Veredicto de E1

**CONFIRMADO, sin matices.** Los 11 ciclos a B=4, los 5 a B=28, la caída de
área de 108 a 93 LUT6 y las 181 filas bit a bit. Nada se rompió, así que el
hallazgo de esta sección es sólo la confirmación — y la nueva batería de
pruebas que la sostiene, que sí es nueva.

---

## 2. E2 — El techo recalculado

### 2.1 El barrido, medido otra vez entero

No se dedujo. `SINTESIS.md` §3.4 ya había medido que el área de un pipeline
**no** es la suma de sus partes (45% de diferencia en iCE40), así que suponer
que "el DSP no cambia, luego el techo no cambia" habría sido repetir el error
estructural que ese hallazgo documentó. Se sintetizaron 21 configuraciones
(`make techo`), empezando por el **control**:

| | pendiente MEDIDA por ticker (K=1 → K=64) | techo DSP | techo FF | techo LUT6 |
|---|---|---|---|---|
| **B=1 (control)** | 77,5 LUT6 · 338,0 FF · **1,00 DSP** | **240** | 375 | 817 |
| **B=4** | 72,0 LUT6 · 336,0 FF · **1,00 DSP** | **240** | 377 | 880 |
| **B=28** | 63,0 LUT6 · 333,0 FF · **1,00 DSP** | **240** | 380 | 1.006 |

El control reproduce la tabla de `SINTESIS_A7.md` §3.4 (240 / 375 / 817) — sin
esa fila, las otras dos no significarían nada.

> *(Diferencia de una LUT y su causa, porque callarla sería peor que decirla:
> `SINTESIS_A7.md` §3.4 publica **4.964** LUT6 en K=64 y acá salen **4.963**.
> No es ruido: se rastreó. Ver §6.1 — depende de qué archivos irrelevantes
> estén en el `read_verilog`. La pendiente redondea a 77,5 con los dos valores
> y ninguna conclusión se mueve.)*

### 2.2 La respuesta, con el porqué

**El techo NO cambió: 240 tickers en los tres anchos, con el DSP48E1 topando
primero en los tres.** Y la lectura útil es la contraria a la intuitiva:
**ensanchar la ingesta hace que el DSP sea MÁS dominante como cuello**, porque
baja lo único que la ingesta toca —LUT y FF— y no toca el DSP. El segundo
recurso pasa de estar a 1,56× del primero (375 vs 240) a estar a 1,58× (380 vs
240), y el tercero de 3,4× a 4,2×.

**Por qué, dicho como mecanismo y no como coincidencia.** La latencia de este
diseño vive en el **parser**: un contador de palabras y un decodificador de
escritura, que son LUT y flip-flops. El techo lo pone la cuenta de
**multiplicaciones**, una por pipeline replicado, porque cada pipeline lleva su
propio `beta × SOX`. Ensanchar el bus no crea ni destruye una sola
multiplicación. Son dos ejes ortogonales **en este diseño** — y se dice "en
este diseño" y no "en general" porque es lo que se midió.

### 2.3 Qué costaría subirlo — camino (i): el multiplicador sin DSP

Si el DSP es el que topa, lo directo es no gastar uno por ticker.
`synth_xilinx -nodsp` obliga a mapear el 16×16 con signo a LUT6 y CARRY4:

| K | DSP | LUT6 | FF |
|---|---|---|---|
| 1 | 0 | 686 | 336 |
| 8 | 0 | 5.491 | 2.688 |
| 16 | 0 | 10.973 | 5.376 |

**Costo marginal medido: 685,8 LUT6 por ticker.** Techo resultante: **92
tickers** (lo pone LUT6). **El camino obvio baja el techo 2,6 veces.** Es
consistente con lo que `SINTESIS.md` §4.1 ya había medido en el iCE40 —el
multiplicador solo cuesta 803 celdas ahí— y cierra la pregunta por la negativa.

### 2.4 Qué costaría subirlo — camino (ii): dejar de replicar

El que funciona es el otro, y es la Variante 1 de la §3.1: **un pipeline con
tabla de pesos**. Un solo DSP48E1 sirve a T instrumentos, y el techo deja de
ser una cuenta de DSP para pasar a ser el tamaño de la tabla, que es
prácticamente gratis:

**Todo lo que sigue es a B=4**, y hay que decirlo porque si no parece
contradecir a `SINTESIS_A7.md` §3.4:

| a B=4 bytes/ciclo | 8 tickers replicados | 8 en la tabla | 240 en la tabla |
|---|---|---|---|
| DSP48E1 | **8** | **1** | **3** |
| LUT6 | 577 | **109** | 119 |
| FF | 2.688 | **358** | 343 |
| BRAM | 0 | 0 | 1 (RAMB18E1) |

> **Aviso, porque acá es fácil leer una contradicción que no existe.** Los
> 577 LUT6 y 2.688 FF de la primera columna son **K=8 a B=4** (§2.1).
> `SINTESIS_A7.md` §3.4 publica para K=8 los valores **622 LUT6 y 2.704 FF**,
> que son **K=8 a B=1** — la ingesta byte a byte. Las dos filas son correctas y
> miden anchos distintos. **Ninguna tabla de este documento se puede comparar
> con una de `SINTESIS_A7.md` sin verificar primero que hablan del mismo B.**

**Treinta veces el universo de MKI cuesta tres DSP de 240.** Dos de esos tres
no son el modelo: son la aritmética de direcciones de la tabla (`slot × 6`),
que yosys mapea a DSP porque le sale gratis; con un paso de 8 en vez de 6
serían desplazamientos. **Se nombra y no se arregla** — el arreglo cambia el
diseño y la medición de hoy es del diseño de hoy.

---

## 3. E3 — Dos variantes más del espacio de diseño

**Cómo se eligieron.** No por lo que impresiona. Se eligieron las dos piezas
que **los propios documentos del proyecto nombran como faltantes** y que nadie
había construido:

- `SINTESIS_A7.md` §4.2: *"Lo que el margen sí habilita en esta línea, y que
  hoy no existe: un **banco de pesos por instrumento** … indexado por
  `id_instrumento` — el campo ya viaja en el mensaje de 28 bytes y hoy sólo se
  usa para sellar."*
- `SINTESIS_A7.md` §3.5: *"la forma correcta de servir 8 tickers no es 8
  pipelines: es **uno multiplexado en el tiempo**."*
- `multi_top.v`, en su encabezado: *"ALTERNATIVA NO IMPLEMENTADA, Y ES LA QUE
  PROBABLEMENTE CORRESPONDE."*
- `SINTESIS_A7.md` §8, último pendiente: *"**La ingesta ancha desde BRAM**: hoy
  la fuente del testbench es el propio banco de pruebas. Un reproductor desde
  BRAM es RTL nuevo y no está escrito."*

Tres documentos apuntan a la primera y uno a la segunda. Además, la segunda es
la que decide si el ancho de bus sirve de algo: sin fuente interna, B=28 es una
cifra bonita e irrealizable.

### 3.1 Variante 1 — tabla de pesos por instrumento (`pipeline_top_multi.v`)

**Costo real medido**, B=4, F=1, `synth_xilinx -family xc7 -flatten`:

| T (instrumentos) | DSP48E1 | LUT6 | FF | CARRY4 | BRAM |
|---|---|---|---|---|---|
| 1 (equivale al banco único de hoy) | 1 | 103 | 358 | 26 | 0 |
| 2 | 1 | 103 | 358 | 27 | 0 |
| **8 (el universo real)** | **1** | **109** | **358** | 30 | **0** |
| 16 | 1 | 129 | 358 | 32 | 0 |
| 64 | 1 | 129 | 343 | 32 | 1 |
| 240 | 3 | 119 | 343 | 29 | 1 |

**Los ocho tickers de MKI cuestan +6 LUT6 sobre el banco único. Seis.** Y cero
DSP, cero FF y cero BRAM de más. A partir de T=64 la tabla se va a memoria de
bloque y los flip-flops **bajan**.

**Validación, y por qué el test no es trivial.** Programar sólo el slot
correcto y ver que sale bien no distingue una tabla de un registro único:
cualquier decodificador roto que devuelva siempre la única entrada escrita
pasaría. Así que antes de cada caso se escriben **los T slots**: el del
instrumento del mensaje con su peso real y **todos los demás con un señuelo**
(`peso ^ 0x5A5A`). Resultado: **181/181 bit a bit** en T=1, 8 y 16, latencia
**11 ciclos** sin cambio, y `id_sellado` correcto en los 181.

**Contraprueba, porque un banco que nunca falla no prueba nada.** Con
`-DCFG_SABOTAJE_SLOT` el decodificador se rompe a propósito (slot forzado a 0).
El test **falla en 160 de 181**. Los 21 que no fallan son exactamente los 21
casos cuyo `id_instrumento` es 0 y que por lo tanto **deben** dar slot 0. O sea
que la discriminación es **160/160 de los casos discriminables**: el test
detecta el error en el 100% de las filas donde el error es detectable.

**Alcance honesto — lo que esta variante NO resuelve.** `etapa_features`
mantiene una ventana rodante que es estado **por instrumento**. En la
configuración campeona (F=1) da igual: la única feature usada es `g0 = f0`,
función pura del mensaje, y el sintetizador ni conserva la ventana. Pero con
F≥2 la feature `g1` usa la media rodante y multiplexar en el tiempo **sin
replicar la ventana mezclaría la historia de dos tickers** — un error de
corrección, no de área. Está escrito en el encabezado del módulo porque el
campeón no lo expone y es de las cosas que se descubren tarde.

### 3.2 Variante 2 — el sistema autónomo desde memoria (`fuente_bram.v` + `demo_top.v`)

Un pulso de `arrancar` y el chip reproduce las 181 filas selladas desde su
propia memoria —los 28 bytes de cada mensaje **y** los seis pesos de cada caso,
porque la beta rodante cambia fecha a fecha y un banco cargado una vez no
reproduce nada—, las pasa por el pipeline y emite 181 sellos. Sin UART de
entrada, sin banco de pruebas, sin DDR3L y sin un solo pin de datos.

**Costo real medido:**

| configuración | DSP48E1 | LUT6 | FF | CARRY4 | memoria (primitivas) | equivalente en bloques de 36 Kb |
|---|---|---|---|---|---|---|
| pipeline solo, B=4 | 1 | 102 | 358 | 26 | **0** | 0 — 0,00% |
| **`demo_top` B=4** | 3 | 160 | 362 | 29 | **1× RAMB36E1 + 3× RAMB18E1** | **2,5 — 1,85%** |
| pipeline solo, B=28 | 1 | 93 | 355 | 25 | **0** | 0 — 0,00% |
| **`demo_top` B=28** | 2 | 168 | 309 | 30 | **1× RAMB36E1** | **1,0 — 0,74%** |

**Las primitivas van desglosadas y no como un "4 BRAM" a secas, a propósito:
un RAMB36E1 son 36 Kb y un RAMB18E1 la mitad, así que sumarlas y compararlas
contra los 135 bloques de 36 Kb de DS180 sobreestima la ocupación.** Sumadas
crudas darían 4 bloques = 2,96%; la cuenta correcta es **2,5 equivalentes =
1,85%**. El desglose sale de `make variantes` y queda en
`micro/rtl/sintesis/variantes.log`.

**Es la primera configuración de todo el proyecto que usa BRAM.**
`SINTESIS_A7.md` §3.1 subrayaba que las cuatro configuraciones daban BRAM = 0.

**Validación: 181/181 bit a bit** contra el mismo `esperado_F1.hex`, a **11
ciclos** con B=4 y a **5 ciclos** con B=28 — con el banco de pruebas sin
alimentar un solo byte. Que los 181 coincidan es además la única prueba de que
el re-empaquetado a palabras de B bytes no invirtió nada.

**Esto es lo que vuelve realizable el B=28.** `SINTESIS_A7.md` §4.1 lo había
dicho como límite: 28 bytes en paralelo son 224 pines, el chip tiene 300 I/O de
usuario y **la placa expone 32 señales por los cuatro Pmod**. Adentro no hay
pines. Los 5 ciclos dejan de ser una cifra de catálogo.

**Dos cosas que hay que declarar del número de BRAM.** (1) Los +2 y +1 DSP son
otra vez la aritmética de direcciones de la fuente (`idx × N_PAL`, `idx × 6`),
no el modelo. (2) **yosys poda legítimamente los bits de la ROM que el pipeline
nunca lee** — `ts_ns`, `lado`, `flags` y `reservado` no alimentan nada, o sea
12 de los 28 bytes son lógica muerta en este diseño. La cifra de BRAM es la de
la porción viva, **no** la de guardar el registro de 28 bytes completo. Quien
quiera lo segundo tiene que medirlo aparte.

### 3.3 Hallazgo que no se buscaba: el hueco entre mensajes es de corrección

`SINTESIS.md` §9 y `SINTESIS_A7.md` §3.5 describen los 8 ciclos de silencio
entre mensajes como algo que el banco inserta *"para que la latencia se mida
limpia"*. Con la fuente interna el hueco pasó a ser un parámetro, así que se
barrió (`make huecos`):

| HUECO | B=4 | B=28 |
|---|---|---|
| 0 | **178/181 MAL** | **178/181 MAL** |
| 1 | **178/181 MAL** | **178/181 MAL** |
| 2 | 0 fallos | 0 fallos |
| 3, 8 | 0 fallos | 0 fallos |

**El silencio hace algo más que dejar medir limpio: es un requisito de
corrección que nadie había escrito.** El escritor de pesos del mensaje k+1
pisa el banco antes de que `etapa_puntaje` haya muestreado el peso del mensaje
k, y los sellos salen **corridos un mensaje** (se ve en la salida: el puntaje
esperado del caso 9 aparece en el sello 8). El mínimo es **2 ciclos** y es el
mismo en los dos anchos, o sea que no depende del bus sino de la profundidad
del pipeline entre `msg_valido` y el muestreo del peso.

**Lo peor del hallazgo, y la razón de que vaya en el resumen ejecutivo: la
latencia seguía dando 11 ciclos exactos y perfectamente determinista mientras
178 de 181 resultados estaban mal.** La propiedad que este proyecto exhibe
—latencia constante— **no implica corrección**, y una prueba que sólo mirara la
latencia habría pasado en verde. La corrección fue al código antes que a esta
prosa: `fuente_bram.v` aborta en elaboración si `HUECO < 2`, con la cifra
medida en el mensaje, y hay un bypass explícito para poder volver a medir la
zona insegura.

**De paso, la primera medición de caudal espalda-con-espalda del proyecto**
(pendiente desde `SINTESIS.md` §9). Se cuenta el reloj de la simulación
completa —181 mensajes, 0 fallos— y se divide, que es una medición de caudal y
no una latencia convertida en caudal (esa conversión sigue prohibida y sigue
sin hacerse):

| | ciclos totales | menos 29 de arranque y cola | **por mensaje** |
|---|---|---|---|
| B=4, HUECO=2 (el mínimo seguro) | 2.744 | 2.715 = 181 × 15 | **15,00** |
| B=4, HUECO=8 (como estaba) | 3.830 | 3.801 = 181 × 21 | 21,00 |
| B=28, HUECO=2 | 1.658 | 1.629 = 181 × 9 | **9,00** |
| B=28, HUECO=8 | 2.744 | 2.715 = 181 × 15 | 15,00 |

Los cuatro dan el entero exacto, que es lo que corresponde a una máquina de
estados sin caminos dependientes del dato: `6` ciclos de recarga de pesos +
`ceil(28/B)` de mensaje + `HUECO`. **Con la tabla de pesos de la §3.1 los 6
ciclos de recarga desaparecerían** —en el sistema real cada ticker tiene una
beta por día y ocho mensajes por día—, pero eso **no se midió**: los 181
vectores son 181 pares (ticker, fecha) y cada uno trae su propia beta, así que
con estos vectores la recarga es inevitable. Se dice en vez de estimarlo.

---

## 4. E4 — La errata, y por qué nadie preguntó

### 4.1 La errata (medida)

**La mejora también aplicaba a la Go Board.** El área baja ahí también, y no
sólo en el mapeo (948 → 931 LUT4) sino **después de place & route**, que es el
veredicto duro que `SINTESIS.md` §4 usa:

| diseño, colocado y ruteado en hx8k-ct256 | ICESTORM_LC |
|---|---|
| `pipeline_top` original (B=1) | 1.195 |
| `pipeline_top_ancho` B=1 — **control** | 1.198 |
| `pipeline_top_ancho` B=2 | 1.190 |
| **`pipeline_top_ancho` B=4** | **1.184** |
| `pipeline_top_ancho` B=7 | 1.182 |

El control queda a 3 celdas (0,25%) del original: la variante no cambió nada
material. **De B=1 a B=4 se ahorran 14 celdas colocadas (1,2%) y se bajan 21 de
los 32 ciclos.** O sea que **la ingesta ancha no estaba bloqueada por falta de
espacio en el iCE40: ahí también salía gratis.**

**Aviso de unidades, porque acá es fácil sumar peras con manzanas.** Estas
cinco filas son el **pipeline solo**. Las 1.545 celdas que `SINTESIS.md` §4
publica para F1 son el **envoltorio de placa** (`sint_top`: pipeline + UART RX
+ carga de pesos + serializador del sello), que es otro objeto. Los dos números
no se restan ni se comparan de frente: lo único que esta tabla sostiene es el
**delta entre anchos del mismo objeto**, que es lo que la errata necesita.

**Y hay que decir lo que la errata NO dice.** Esto **no** rescata a la Go
Board. El campeón F1 completo —el envoltorio— mide 1.545 celdas contra las
1.280 del HX1K, y un ahorro de 14 celdas no mueve ese veredicto ni de cerca. El
hallazgo no es "ahora entra": es que **la pregunta nunca se hizo, y la
respuesta era gratis en las dos placas**.

Las erratas fechadas quedaron escritas en su sitio: `RTL.md` §1 y §2,
`fpga.md` §2 y §4, `SINTESIS.md` §4 y §4.2.

### 4.2 Por qué nadie preguntó — la parte que importa

La sospecha del encargo era que el diseño se pensó como *"entra o no entra"* en
una placa chica, y que esa pregunta de sí/no ocupó el lugar de *"¿cuál es la
mejor forma de esto?"*. **Esa hipótesis es correcta en dirección, y los
documentos permiten decir algo más específico y peor.** Tres capas, en orden
de qué tan incómoda es cada una.

**Capa 1 — el marco de la medición era el ÁREA, y en ese marco la ingesta era
invisible por barata.** `RTL.md` §2 presupuesta la ingesta en *"~100-150
LUTs"*, y `fpga.md` §4 la despacha como *"comparadores y registros de
desplazamiento — barato, cabe cómodo en cualquiera de las dos placas"*. Todas
las tablas de `RTL.md` §2, `SINTESIS.md` §3 y §4 y `fpga.md` §3 son tablas de
área. Una etapa clasificada como barata no vuelve a mirarse en un marco de
área. Pero **la ingesta no era el 84% del área: era el 84% de la latencia**, y
para eso no había tabla.

**Capa 2 — la latencia sí era el entregable, pero su figura de mérito era la
VARIANZA, no la magnitud.** `fpga.md` §2 formula la predicción falsable del
proyecto: *"en hardware p50 = p99 = p99.9 = máximo"*. Eso es una afirmación
sobre la **forma de la distribución**. **32 ciclos la cumple exactamente igual
de bien que 11.** El número nunca estuvo bajo presión de optimización porque
sólo tenía que ser *constante*, no *chico*. Ésta es, creo, la explicación
principal: no es que nadie mirara la latencia — se la miró mucho —, es que se
la miró con el único instrumento que no podía detectar que sobraba.

**Capa 3 — la que más incomoda: la enumeración del espacio de diseño SÍ se
hizo, y aun así la opción no apareció.** `SINTESIS.md` §4.2 se titula *"Qué
habría que sacrificar para que entre"* y lista cinco opciones (a) a (e). Las
cinco son **restas**: angostar la aritmética, un multiplicador serie más lento,
sacrificar el UART y el contador, degradar el modelo, comprar otra placa. **Un
marco que sólo admite sacrificios no puede contener una opción que mejora dos
cosas a la vez y no cuesta nada.** La ingesta ancha baja la latencia *y* baja
el área: en la gramática de esa sección, no es una opción — es una categoría
que no existe. Ahí es donde la sospecha del encargo acierta de lleno, y el
mecanismo es más preciso que "la pregunta de sí/no ocupó el lugar": la pregunta
de sí/no **definió la forma gramatical** de las respuestas admisibles.

**Y el remate, que es lo que convierte esto en un hallazgo y no en una moraleja:
la opción estaba escrita desde el principio.** `RTL.md` §1, primer documento de
la pista, describiendo la etapa 1:

> *"una máquina de estados que corre un byte **(o un word, si el bus lo
> permite)** por ciclo"*

**El paréntesis está ahí.** La idea se tuvo. Lo que pasó fue que se la
**condicionó a una precondición** —"si el bus lo permite"— sobre un bus externo
que en ese momento no existía, porque no había placa. El default de un byte se
congeló como implementación, la precondición quedó pendiente de un hecho futuro,
y **nadie volvió a evaluarla cuando el hecho llegó**. No fue una idea que no se
tuvo: fue una idea **estacionada en una condición sin dueño**.

Lo cual cierra el círculo de la peor manera posible: cuando por fin se evaluó
la condición (esta corrida y la anterior), resultó que **era falsa para un bus
externo** —224 pines contra 32 señales de Pmod— **e irrelevante para uno
interno**, y que la fuente interna era exactamente la arquitectura que
`SINTESIS_A7.md` §3.2 ya recomendaba para la demo del ramo por otros motivos.
**La precondición era respondible desde el día en que se escribió, cambiando de
dónde vienen los datos.** Lo que faltó no fue información ni espacio: faltó
alguien que le pusiera fecha de revisión a un paréntesis.

**La lección operativa, en una línea:** una idea condicionada a un hecho futuro
necesita un dueño y una fecha, o se convierte en una decisión tomada por
omisión. Es el mismo género de deuda que el proyecto ya sabe manejar cuando la
escribe en `DECISIONES.md` — sólo que ésta vivía en un paréntesis.

---

## 5. Qué se construyó en este frente

| Archivo | Qué es |
|---|---|
| `micro/rtl/tb/tb_pipeline_gate.v` | Banco con instrumento independiente; compila contra RTL y contra netlist mapeada |
| `micro/rtl/multi_top_ancho.v` | K pipelines de ingesta ancha, para el barrido del techo |
| `micro/rtl/pipeline_top_multi.v` | **Variante 1**: tabla de pesos por instrumento (+ sabotaje para la contraprueba) |
| `micro/rtl/tb/tb_pipeline_multi.v` | Su banco, con señuelos en los slots que no corresponden |
| `micro/rtl/fuente_bram.v` | **Variante 2**: reproductor de las 181 filas desde memoria + guardia de HUECO |
| `micro/rtl/demo_top.v` | El sistema autónomo: fuente + pipeline, un pulso y 181 sellos |
| `micro/rtl/tb/tb_demo.v` | Su banco, que no alimenta datos |
| `micro/rtl/empaquetar_vectores.py` | Re-agrupa `mensajes.hex` en palabras de B bytes. **No toca `senales.db`** |
| `micro/rtl/medir_techo.py` | Barridos de techo, `-nodsp`, tabla y demo |
| `micro/rtl/medir_a7.py` | Corregido: la columna de latencia se lee de la simulación (§1.1) |
| `micro/rtl/Makefile` | Objetivos `ancho-gate`, `multi`, `demo`, `huecos`, `techo`, `variantes`, `semillas`, `empaquetar` |

---

## 6. Qué es determinístico, qué tiene intervalo y qué no se midió

**La regla:** ningún estimador puntual sin intervalo **donde haya
variabilidad**. En síntesis muchas cifras son determinísticas y ahí inventar un
intervalo sería tan deshonesto como omitirlo donde corresponde. Así que se
**midió** cuáles son cuáles en vez de suponerlo.

### 6.1 Determinísticas — no llevan intervalo

| Magnitud | Evidencia |
|---|---|
| **Cuentas de celdas del mapeo** (LUT6/FF/DSP/CARRY4/BRAM) | 4 corridas idénticas de `multi_top` K=64: **4/4 exactamente iguales** |
| **Celdas colocadas por nextpnr** (`ICESTORM_LC`) | 10 semillas de `pipeline_top_ancho` B=4: **1.184 en las 10**. F1SP: **742 en las 10** |
| **Latencias en ciclos** | mín = máx sobre los 181 vectores, en 6 anchos, con 2 instrumentos y 3 diseños bajo prueba |

**PERO — una advertencia que hay que llevarse.** Determinística no es lo mismo
que invariante. La cuenta de celdas del mapeo **depende de qué archivos estén
en el `read_verilog`, aunque no participen de la jerarquía**: el mismo
`multi_top` K=64 da **4.964** LUT6 con la lista de `medir_a7.py` (que arrastra
`uart_rx.v` y `sint_top.v`) y **4.963** con la lista mínima. Es un 0,02% y no
mueve nada, pero significa que **una cifra de síntesis es reproducible sólo
junto con su invocación completa**, no sólo con su módulo. Se documenta porque
la próxima diferencia de este tipo puede no ser de una LUT.

### 6.2 NO determinísticas — llevan su dispersión o no se citan

| Magnitud | 10 semillas de nextpnr |
|---|---|
| **Fmax, `pipeline_top_ancho` B=4 (hx8k-ct256)** | **66,11 – 73,00 MHz**, media 69,74 · el rango es el **9,9%** de la media |
| **Fmax, F1SP (hx1k-tq144, la fila que dice CABE)** | **105,27 – 114,19 MHz**, media 112,47 |

**Consecuencia directa sobre lo publicado:** los Fmax de `SINTESIS.md` §4
(114,19 · 71,97 · 69,01 · 64,76 MHz) salen de `--seed 1` y son **estimadores
puntuales de una sola realización del colocador**. La conclusión que sostienen
—que F1SP corre muy por encima de los 12 MHz del oscilador de la Go Board—
aguanta con holgura incluso en el peor de las diez semillas (105,27 MHz es 8,8
veces 12 MHz). **La conclusión sobrevive; el número, tal como está publicado,
le falta su dispersión.** Errata fechada en `SINTESIS.md` §4.

**Y alcanza al `icetime`, que parecía la vara independiente y no lo es.**
`SINTESIS.md` §4 publica junto al Fmax de nextpnr un *"114,59 MHz con
`icetime` (ruta crítica 8,73 ns)"*, y la coincidencia invita a leerlos como dos
mediciones que se confirman. **No lo son:** `icetime` no coloca nada — mide la
ruta crítica de **una colocación ya hecha**, el `.asc` de esa misma `--seed 1`.
Es otra herramienta pero **no es otra realización**, así que arrastra íntegra la
dependencia de la semilla y no aporta una familia de evidencia distinta. Es el
mismo error de forma que la §1.2 existe para no cometer.

*(Nota sobre qué clase de incertidumbre es ésta: la semilla no muestrea nada
físico, es un parámetro del algoritmo de colocación. Por eso se publica el
**rango observado sobre 10 semillas** y no un intervalo de confianza sobre un
"Fmax verdadero" — ese objeto no existe con estas herramientas. Con Vivado y
placa habría además variabilidad de proceso y temperatura, que es otra cosa y
tampoco se midió.)*

### 6.3 EXTRAPOLACIÓN, no medición

- **El techo de 240 tickers.** Medido hasta K=64; de ahí a 240 es la pendiente
  medida, extrapolada. Vale para los tres anchos y para el `-nodsp`.
- **El techo de 92 tickers sin DSP.** Medido hasta K=16.
- **La tabla de T=240.** Sintetizada, **no simulada**. La validación bit a bit
  llega a T=16.

### 6.4 NO EXISTE, por falta de place & route en Artix-7

Vivado no está instalado y el bloqueo no es técnico: exige cuenta AMD y
formulario de control de exportación, que es un acto de identidad de Nicolás
(`SINTESIS_A7.md` §6.1, `micro/TOOLCHAIN.md` §3). Por lo tanto:

- **Fmax en Artix-7.** No existe. Los Fmax de este documento son **de iCE40**,
  vía nextpnr, y no se pueden trasladar.
- **Utilización real de slices tras P&R.** No existe. El "piso de slices" es
  una cota inferior, no una predicción.
- **Que el diseño cierre temporización a X MHz.** No existe. Ni para el
  pipeline, ni para la tabla de 240, ni para la fuente con BRAM — y ésta última
  es la que más lo pediría, porque una BRAM tiene su propio retardo de lectura.
- **Bitstream y medición sobre placa.** No existen.
- **El costo en BRAM de guardar el registro de 28 bytes completo.** El medido
  es el de la porción viva (§3.2).

---

## 7. Denominador y trazabilidad de los vectores

Los 181 vectores son **los mismos de 31-ago**. `empaquetar_vectores.py` los
re-agrupa en palabras de B bytes y nada más: no importa `sqlite3` ni
`referencia.py`, así que **no puede** regenerarlos ni por error. Es deliberado
— regenerar movería el denominador de 181 a 189 y con eso todas las tablas de
simulación ya publicadas en `SINTESIS.md` y `SINTESIS_A7.md`, que es
exactamente lo que `SINTESIS_A7.md` §5 declara que no se hizo. **En este frente
`senales.db` no se abrió ni una vez, ni siquiera en `mode=ro`.**

---

## 8. Marcado explícitamente como decisión de Nicolás

1. **El ancho de la ingesta.** Sigue abierto (`SINTESIS_A7.md` §6.3), pero la
   evidencia cambió: **B=28 dejó de ser irrealizable**. Con la fuente interna
   los 5 ciclos existen y están validados bit a bit. B=4 sigue siendo el punto
   que además funciona con fuente externa.
2. **Si el proyecto adopta la tabla de pesos por instrumento.** Cuesta 6 LUT6
   para los ocho tickers del universo y elimina la restricción de "un
   instrumento por bitstream". Este documento mide que es casi gratis; **no
   dice que haya que hacerlo**.
3. **Si `demo_top` es la arquitectura de la demo del ramo.** Funciona y es
   autónoma. Es alcance académico, no técnica.
4. **Arreglar los 2 DSP de la aritmética de direcciones** (paso 8 en vez de 6).
   Trivial, y cambia un diseño que hoy está medido.
5. **Crear la cuenta AMD para Vivado.** Sin cambios respecto de
   `SINTESIS_A7.md` §6.1: sin eso no hay Fmax en Artix-7, ni temporización, ni
   bitstream.

---

## 9. Qué queda pendiente

- **Place & route real en Artix-7.** Bloqueado por la §8.5.
- **Simular la tabla en T=64 y T=240.** Hoy la validación bit a bit llega a 16.
- **La ventana rodante por instrumento**, si el pipeline pasa de F=1 (§3.1).
- **El costo en BRAM del registro de 28 bytes completo**, si alguna vez hay que
  guardar el mensaje entero y no sólo la porción que el pipeline lee.
- **Corrección** (no costo) de las piezas del 4.6.0 completo: sigue pendiente
  desde `SINTESIS_A7.md` §8.
- **El caudal sin recarga de pesos.** Los 15 y 9 ciclos por mensaje de la §3.3
  incluyen 6 ciclos de recarga que con la tabla de la §3.1 no harían falta.
  Medirlo exige vectores donde varios mensajes compartan beta, y los 181 de hoy
  no lo son.

*(Se cierra, en cambio, un pendiente que venía de `SINTESIS.md` §9 y se
repetía en `SINTESIS_A7.md` §8: el **throughput sostenido espalda-con-espalda**
ya no está sin medir — §3.3. Lo que sigue sin medirse es el de la §3.1.)*
