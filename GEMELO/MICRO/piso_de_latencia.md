# El veredicto del piso de latencia

Este documento responde la pregunta que `GEMELO/MICRO/DISEÑO.md` (§8) marcó
como el riesgo más incómodo, con las mediciones de `micro/` y
`GEMELO/MICRO/WSL2.md` en la mano: **¿qué piso de latencia haría falta para
que la pregunta de investigación tenga sentido, y a qué distancia está esta
plataforma de ese piso?**

La respuesta corta, dicha con toda la firmeza que pide el encargo: **para la
lectura de "microtrading" como captura en vivo de una ventaja informacional
de microsegundos-a-segundos, la distancia es de varios órdenes de magnitud y
no la cierra ni comprar una Arty A7. Para la lectura de "pipeline RTL de
decisión validado por backtest" del proyecto de Arquitectura de
Computadores, la pregunta SÍ tiene sentido y no depende de este piso.** Son
dos preguntas distintas y el pre-registro las separó a propósito
(`DISEÑO.md` §4). Este documento trata cada una por separado.

## 1. Qué exige la lectura de "captura en vivo"

Explotar en vivo una asimetría informacional de vida corta requiere que la
cadena completa — llega el dato, se decide, se envía la orden, se ejecuta —
sea más rápida que la vida media del efecto. La industria de trading de alta
frecuencia (información pública, de arquitectura de sistemas, no una cifra
de este proyecto) resuelve esto con **colocation** (el servidor de decisión
vive en el mismo datacenter que el motor de emparejamiento de la bolsa,
conectado por un cross-connect de fibra de unos pocos metros) y **FPGAs con
NICs de kernel-bypass**, alcanzando latencias de punta a punta del orden de
cientos de nanosegundos a unos pocos microsegundos. Eso es lo que "rápido"
significa en ese régimen: no es una cifra arbitraria, es lo que exige
competir contra otros participantes que ya operan ahí.

Ninguna de esas dos condiciones está disponible acá. No hay colocation
(dato disponible: `bench_red` midió un round trip de **connect() TCP contra
un endpoint público — 1.1.1.1:443 — de p50 = 8.79 ms, p99 = 36.76 ms**, ver
`micro/resultados/red.json`) y no hay ninguna fuente de datos de mercado
tick-level identificada (riesgo (i) del §8 de `DISEÑO.md`).

## 2. La distancia medida, en órdenes de magnitud

| Capa | Lo que se necesitaría (HFT colocado, referencia de industria) | Lo que se midió acá | Distancia |
|---|---|---|---|
| Red, dato→decisión | cientos de ns a bajos µs (cross-connect colocado) | 8.79 ms (p50), a internet público, sin colocation | **~4 órdenes de magnitud** |
| Despertar de un proceso / planificación | sub-µs (kernel de baja latencia, tickless, aislamiento de núcleo) | ~75 µs de piso constante, medido en `bench_jitter` (ver `WSL2.md`) | **~2 órdenes de magnitud** |
| Syscall trivial, caso típico | decenas de ns (sin virtualización) | 290 ns p50, pero cola hasta 57.459 ns | el cuerpo está cerca; **la cola está ~2-3 órdenes de magnitud por encima** |
| Parseo de un mensaje de mercado | irrelevante frente a lo anterior: `bench_mensaje` mide 1 ns/mensaje en promedio de lote, 488M msgs/s en la pasada completa — esta capa **no es el cuello de botella**, nunca lo fue | 1 ns/mensaje (p50) | sin brecha — esta parte ya sobra |

La fila que sentencia el veredicto es la primera: la red. Ningún ajuste de
software, ningún RTL, ninguna FPGA cambia una latencia de red de milisegundos
determinada por no tener colocation. Es una brecha estructural, no una
brecha de implementación.

## 3. Qué SÍ es alcanzable, y qué pregunta responde

Lo que el arnés muestra que ESTA plataforma puede hacer con solidez: parsear
mensajes de mercado a throughput de cientos de millones por segundo (sobra
margen), acceder a memoria con la jerarquía de caché esperada (L1 ~1 ns/salto,
L2 ~3 ns, L3 ~24-29 ns, RAM ~94-98 ns — sin anomalías, la memoria se comporta
como memoria), y ejecutar una syscall trivial en ~290 ns típico. Ninguna de
esas cifras es el cuello de botella de un sistema de microtrading en vivo: el
cuello de botella es la red y el planificador, medidos arriba, y ninguno de
los dos se resuelve dentro del alcance de este proyecto.

Lo que SÍ tiene sentido, y es exactamente lo que el proyecto de Arquitectura
de Computadores necesita: **un pipeline RTL que tome decisiones más rápido
que una implementación equivalente en software, medido y demostrado con un
backtest sobre datos históricos, sin pretender que esa velocidad se traduzca
en una ventaja económica capturable en un mercado real sin colocation.** Esa
pregunta no depende del piso de red medido arriba porque nunca se conecta a
un mercado en vivo — el dinero real y las órdenes a un bróker ya están
excluidos por la Constitución 5.0 del proyecto MKI (punto 5), y el proyecto
académico no los necesita para tener éxito.

## 4. Veredicto formal, contra los criterios de `DISEÑO.md`

- **Lectura "captura en vivo de una ventaja de microtrading"**: dispara el
  criterio de rechazo que mata la pista completa (R1 de `DISEÑO.md`) — la
  distancia entre el piso medido y el piso que la pregunta exige es de
  órdenes de magnitud, no de grado. **Se declara NO VIABLE con el
  presupuesto y la infraestructura de este proyecto, ahora y
  previsiblemente con cualquier próxima placa de estudiante** (una Arty
  A7-100T es más FPGA, no más colocation, no más ancho de banda de red, no
  menos milisegundos de internet público — el cuello de botella no está en
  la FPGA). Esto se publica como negativo, con la misma firmeza que un
  hallazgo positivo: un negativo temprano acá vale más que meses de RTL
  sobre una premisa que la red ya refutó.
- **Lectura "pipeline RTL validado por backtest, ejercicio de
  arquitectura"**: NO choca con ningún criterio de rechazo — es una
  pregunta de ingeniería (¿el hardware decide más rápido y de forma
  verificable?), no una pregunta de mercado en vivo, y el piso medido acá
  no la invalida. Queda abierta y es la que este proyecto puede,
  legítimamente, seguir persiguiendo.

## 5. Lo que este documento NO decide

No decide si Nicolás sigue con el proyecto de Arquitectura de Computadores
bajo la lectura (2) — eso ya tiene sentido de por sí, con independencia de
esta pista de GEMELO. Tampoco decide qué placa comprar (`fpga.md` trata esa
pregunta y la deja marcada como decisión de Nicolás). Lo único que este
documento cierra es la pregunta que le tocaba: si la pista de "microtrading
como ventaja económica capturable" tiene piso para sostenerse, y la
respuesta, medida, es que no.
