# La parte FPGA — qué haría el hardware, qué cabe, qué no

Sin comprar nada y sin asumir una placa. Este documento responde tres cosas:
qué haría el hardware que el software no puede, qué habría que medir para
demostrarlo, y qué cabe en un iCE40HX1K frente a un Artix-7. La elección de
placa es de Nicolás — se marca donde corresponde, no se resuelve acá.

## 1. Qué haría el hardware que el software no puede

`GEMELO/MICRO/WSL2.md` midió, en esta plataforma, dos límites que no son de
implementación sino estructurales al modelo de ejecución: un **piso de
despertar del planificador de ~72-85 µs** (constante, no importa cuánto se
pida dormir por debajo) y una **cola de interrupción** de la CPU virtual que
infla ocasionalmente una syscall trivial de 290 ns a más de 50 µs. Ninguno
de los dos existe por accidente de código: existen porque el sistema
operativo decide cuándo correr qué, y un hipervisor decide cuándo el
sistema operativo tiene la CPU de verdad.

Una FPGA no tiene sistema operativo. Un pipeline de decisión en RTL es un
circuito: recibe una entrada en un flanco de reloj y produce una salida un
número FIJO de flancos de reloj después, siempre el mismo número, porque
así lo describe la lógica sintetizada. No hay planificador que reasigne la
lógica a otra tarea, no hay hipervisor, no hay interrupción que robe un
ciclo. La ventaja que el hardware ofrece no es "más rápido" en el sentido
de nanosegundos más chicos — es **determinismo**: la latencia de decisión
es una constante conocida en tiempo de diseño, no una distribución con cola.

## 2. Qué habría que medir para demostrarlo

La demostración correcta no es una sola cifra de latencia — es la
comparación de **formas de distribución**, exactamente en el mismo formato
que usa el resto de este arnés (percentiles, nunca medias):

- **Latencia de decisión, en ciclos de reloj y en tiempo real** (ciclos ×
  periodo del reloj de la placa). Medida con un contador de ciclos interno
  que arranca al recibir el primer bit del mensaje y se detiene al afirmar
  la señal de decisión — no con un reloj externo, que reintroduciría el
  mismo problema de resolución que ya se documentó en `bench_reloj`.
- **La forma de la distribución sobre miles de decisiones repetidas.** La
  predicción falsable es que en hardware **p50 = p99 = p99.9 = máximo**
  (o difieren solo por el jitter del oscilador de la placa, que para un
  cristal de cuarzo típico de una placa de desarrollo es del orden de
  partes por millón — muchísimo más chico que los ~75 µs medidos acá en
  software). Si la distribución en hardware muestra cola, algo del diseño
  RTL tiene una ruta no determinística (un cruce de dominio de reloj mal
  sincronizado, por ejemplo) y ESO sería el hallazgo, no un detalle menor.
- **Throughput sostenido de parseo del mensaje binario**, mensajes por
  segundo con el pipeline corriendo a la frecuencia de reloj de la placa,
  comparado contra el `bench_mensaje.c` de software (488M msgs/s en esta
  máquina, ver `WSL2.md`) — la comparación honesta no es "el hardware gana"
  por default; hay que medirlo.
- **Reporte de utilización del sintetizador** (LUTs, BRAM, y multiplicadores
  dedicados usados vs. disponibles) — es la evidencia dura de qué cupo y
  qué no, no una estimación a ojo.

> **ERRATA (1-sep-2026), medido en `GEMELO/MICRO/INGESTA_ANCHA.md` §4.2.**
> Las cuatro viñetas de arriba son correctas y se cumplieron. Lo que hay que
> anotar es lo que **no** está en ellas, y que explica un año de ceguera: la
> figura de mérito que esta sección le asigna a la latencia es la **forma de
> la distribución** —*"p50 = p99 = p99.9 = máximo"*—, o sea la **varianza**.
> Nunca la **magnitud**. Y **32 ciclos cumplen esa predicción exactamente
> igual de bien que 11**. El número de la latencia jamás estuvo bajo presión
> de optimización porque sólo tenía que ser *constante*, no *chico*: se lo
> midió mucho, con el único instrumento que no podía detectar que sobraba.
> Medido después: 27 de los 32 ciclos eran la ingesta byte a byte, y
> ensanchar el bus los baja a 11 (o a 5) **bajando el área** y sin tocar la
> propiedad de determinismo — 181/181 filas selladas bit a bit en los seis
> anchos, con latencia mín = máx en cada uno.
>
> **La predicción falsable de esta sección sigue en pie y sigue siendo la
> correcta.** Lo que se agrega es que una figura de mérito de varianza deja
> la magnitud sin dueño, y que conviene declarar las dos.
>
> **Y una que sí corrige un número.** Esta sección pide medir la latencia "en
> ciclos de reloj **y en tiempo real** (ciclos × periodo del reloj de la
> placa)". El segundo factor no es determinístico: el Fmax que reporta
> `nextpnr` **depende de la semilla del colocador**. Medido sobre 10
> semillas: el F1SP de `SINTESIS.md` §4 va de **105,27 a 114,19 MHz** (el
> 114,19 publicado es la semilla 1), y el pipeline de ingesta ancha va de
> **66,11 a 73,00 MHz**. Las celdas colocadas, en cambio, salieron
> **idénticas en las 10 semillas**. O sea: las cuentas de celdas son
> determinísticas y no llevan intervalo; **todo Fmax de este proyecto es un
> estimador puntual de una sola realización del colocador** y debería citarse
> con su dispersión. Ninguna conclusión publicada se mueve (105,27 MHz siguen
> siendo 8,8 veces los 12 MHz del oscilador de la Go Board).

## 3. Qué cabe en cada placa

| | Nandland Go Board (Lattice iCE40HX1K) | Digilent Arty A7-100T (Xilinx Artix-7 XC7A100T) |
|---|---|---|
| LUTs | ~1.280 | ~63.400 (celdas lógicas ~101.000) |
| Multiplicadores dedicados (DSP) | **ninguno** | 240 (DSP48E1) |
| Memoria de bloque | 16 × 4 Kbit (64 Kbit total) | 135 × 36 Kbit (~4.860 Kbit) |
| Orden de magnitud de diferencia | — | **~50× más LUTs, DSP dedicado que el iCE40 no tiene en absoluto** |

La fila que más importa para un pipeline de decisión no es la de LUTs — es
la de **multiplicadores dedicados**. Cualquier score de decisión que sea
más que un umbral fijo (una regresión, un promedio ponderado, cualquier
combinación lineal de features, que es exactamente la forma del modelo que
GEMELO viene evaluando) necesita multiplicar. El iCE40HX1K no tiene
multiplicador de hardware: cada multiplicación hay que construirla a partir
de LUTs, y un multiplicador de, por ejemplo, 16×16 bits sin optimizar cuesta
un número de LUTs del orden de cientos — una fracción importante del
presupuesto total de 1.280 antes de contar el resto del pipeline (parseo de
mensaje, máquina de estados de decisión, interfaz de E/S, buffers). El
Artix-7 resuelve la misma multiplicación con un solo DSP48E1, sin gastar
ni un LUT, y tiene 240 de esos bloques disponibles.

## 4. El mínimo que la pregunta exige

Para responder la pregunta de investigación de este pre-registro (§1-2 de
`DISEÑO.md`) el pipeline mínimo necesita, como piso:

1. Un **parser** del mensaje binario de formato fijo (comparadores y
   registros de desplazamiento — barato, cabe cómodo en cualquiera de las
   dos placas).

   > **ERRATA (1-sep-2026).** "Barato" es cierto **en área** y falso en
   > **latencia**: medido, el parser es **27 de los 32 ciclos**. Y su forma
   > —un byte por ciclo— no la impuso el presupuesto de LUTs de ninguna de
   > las dos placas, sino el supuesto de que la fuente sería un UART. Ver
   > `INGESTA_ANCHA.md` §4 y la errata de `RTL.md` §1.
2. Un **núcleo de decisión** con al menos una comparación contra umbral —
   eso también cabe en el iCE40HX1K sin problema. Pero si la pregunta de
   investigación exige algo más cercano al modelo real (una combinación
   ponderada de más de una señal, que es la forma mínima no trivial de
   "decisión" que vale la pena demostrar en RTL), hace falta al menos una
   multiplicación de ancho razonable — y ahí el iCE40HX1K empieza a estar
   al límite o directamente corto, según cuántas señales se combinen.
3. Un **contador de ciclos** para el timestamp determinístico de la
   decisión — trivial en cualquiera de las dos placas.
4. Una **interfaz de E/S** (UART o GPIO) para demostrar el pipeline
   completo de punta a punta — trivial en ambas.

**Conclusión de esta sección, sin elegir placa:** si el pipeline de decisión
se queda en comparación contra umbral, el iCE40HX1K de la Go Board alcanza y
sobra, y no hace falta gastar en una placa nueva para responder la pregunta
mínima. Si el pipeline necesita una combinación ponderada de más de una o
dos señales de entrada — que es la forma más honesta de acercarse a lo que
el modelo de MKI realmente hace — el presupuesto de LUTs del iCE40HX1K se
vuelve el cuello de botella del diseño antes que la pregunta de
investigación, y ahí una Arty A7-100T remueve esa restricción con margen de
sobra (50× LUTs, multiplicadores dedicados que el iCE40 no tiene).

## 5. Lo que es decisión de Nicolás

- **Qué placa comprar, y cuándo.** Este documento no lo resuelve. Da la
  evidencia (la tabla de la §3) para que la decisión se tome informada, no
  a ciegas.
- **Cuánto pipeline vale la pena construir sobre el iCE40HX1K actual antes
  de justificar el gasto de una Arty A7** — es una decisión de alcance del
  proyecto de la materia, no una decisión técnica que este documento pueda
  cerrar.
- **Si el pipeline se simplifica a comparación contra umbral para caber en
  el hardware actual, o si se diseña para el modelo completo asumiendo una
  placa más grande** — ambas son legítimas para el proyecto académico
  (`DISEÑO.md` §4 ya marcó que el proyecto de la materia tiene éxito con un
  pipeline RTL correcto, sea cual sea su complejidad, independientemente de
  si hay ventaja económica capturable — ver `piso_de_latencia.md` §4).
