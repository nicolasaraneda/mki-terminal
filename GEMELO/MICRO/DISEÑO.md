# GEMELO/MICRO — Diseño de la pista: microtrading y el piso de latencia

**Estado:** PRE-REGISTRO. Congelado antes de la primera línea de RTL y antes
de comprar hardware.
**Fecha:** 31-ago-2026
**Insumos:** hallazgo de decaimiento de GEMELO sobre la ventana larga
(n=14.618, ocho años reconstruidos) · `GEMELO/MICRO/WSL2.md` (piso de
latencia medido en esta máquina, 31-ago-2026) · proyecto final de
Arquitectura de Computadores de Nicolás (Nandland Go Board iCE40HX1K,
candidata Arty A7-100T)

Este documento se escribe **antes** de construir nada, en la misma tradición
que `backtest/DISEÑO.md` en el GATE B y que `GEMELO/DISEÑO.md` en la etapa
6.0.0. Los criterios de victoria y rechazo de las §5 y §6 se fijan aquí y no
se tocan después de ver resultados. Si esta pista pierde bajo estos
criterios, pierde.

Si alguna vez hace falta corregir un criterio ya congelado, el patrón es el
de `GEMELO/DISEÑO.md` §2.8: no se reescribe in situ. Se agrega una
subsección con fecha posterior, y esa subsección empieza con un párrafo
"Actualizado el DD-mmm: el criterio NO se movió, se corrigió la medición."
Las cifras de la versión original se conservan como se escribieron.

> **Regla cero:** `motor.py`, `senales.py`, `snapshot.py` y `universo.py` no
> se tocan por esta pista bajo ninguna circunstancia. El modelo 4.6.0 sigue
> sellando en producción sin enterarse de que esta pista existe. No se opera
> con dinero real ni se conecta a ningún broker. La elección de placa (Go
> Board vs Arty A7-100T) es decisión de Nicolás, y este documento no la
> resuelve ni la anticipa.

---

## 1. Por qué existe esta pista y en qué se distingue del modelo actual

MKI Terminal hoy predice a escala de **sesión**. `motor.py`, modelo 4.6.0
congelado, emite una vez de noche (`available_at`/`ts_emision` en
`snapshot.py`, ~22:15 UTC) y anticipa el **gap de apertura** de la sesión
objetivo del día siguiente en cada bolsa. La unidad de tiempo es horas: entre
la emisión y la apertura objetivo median entre 1.75 h (Tokio, Seúl, Taipéi) y
8.75 h (Fráncfort).

Microtrading es otra escala temporal **entera**: minutos o segundos, no
sesiones. No es una versión más rápida del modelo 4.6.0, es una pregunta
distinta, sobre un fenómeno distinto (movimiento intradía de alta frecuencia,
no gap overnight), con datos distintos (tick-level, no cierre/apertura
diarios) y con una restricción que el modelo de sesión nunca tuvo: el tiempo
de cómputo de la decisión compite con la vida útil de la señal. Por eso esta
pista vive en `GEMELO/MICRO/` y no en `GEMELO/` a secas: comparte la familia
de rigor (pre-registro, criterios congelados, denominador honesto) pero no
comparte modelo, datos, ni siquiera unidad de tiempo con el resto de GEMELO.

El modelo de señales congelado no se toca por esta pista bajo ninguna
circunstancia, lo diga o no la regla cero de arriba.

---

## 2. El hallazgo central de GEMELO y la hipótesis de decaimiento

Sobre la ventana larga (n=14.618, ocho años reconstruidos), el modelo le gana
a "siempre al alza" por **+19.1 pp en Tokio, +16.8 pp en Taipéi, +15.4 pp en
Seúl** (las tres a 1.75 h de la emisión) y por apenas **+2.5 pp (p=0.111, no
distinguible de cero) en Fráncfort**, que abre 8.75 h después. Cita textual
de `DECISIONES.md`, verificada: "En Fráncfort la ventaja no es distinguible
de cero, y la explicación es mecánica y medida: cuanto más tiempo pasa entre
la emisión y la apertura, menos queda del contagio."

El WS5 (relevo asiático) matiza esa lectura, y el matiz importa más que el
hallazgo bruto: no es que el efecto decaiga solo por horas transcurridas. Es
que el SOX pierde poder predictivo con la distancia **y nada lo reemplaza**.
La información que "completaría" el relato en Fráncfort (Asia fresca del día
siguiente) no es conocible al momento de la emisión. El decaimiento no es
una curva suave de un solo factor perdiendo fuerza: es un factor perdiendo
fuerza sin sucesor.

**La hipótesis para esta pista, formulada antes de mirar ningún dato de alta
frecuencia:**

> Si la propagación de información decae con el tiempo transcurrido en la
> escala de HORAS ya medida en GEMELO (SOX→Asia, SOX→Europa), entonces debería
> existir una ventaja informacional análoga, aunque menor en magnitud y de
> vida media mucho más corta, en la escala de MINUTOS o SEGUNDOS: por ejemplo,
> tras una sorpresa observable en el book de un ticker correlacionado, o tras
> un movimiento del futuro del índice que un ticker de la cadena todavía no
> reflejó.

**Qué la refutaría, dicho antes de construir nada:** si no hay ninguna
asimetría de información explotable por debajo del piso de latencia
alcanzable con el hardware disponible, o si el piso de latencia de la
plataforma resulta mayor que la vida media del efecto informacional, la
hipótesis es indistinguible de ruido y **la pista muere ahí**, no después de
construir hardware. La sección 6 fija ese criterio en R1 sin dejarlo como
intuición.

---

## 3. La pregunta de investigación

**¿Existe una ventaja direccional explotable, medible con datos históricos de
alta frecuencia, en una ventana de decisión de entre 1 y 60 segundos tras un
evento de mercado observable, que sea mayor que el piso de latencia de
ejecución alcanzable con el hardware disponible (Nandland Go Board
iCE40HX1K, o eventualmente una Arty A7-100T)?**

Es la única pregunta que esta pista intenta responder. No es "explorar
microtrading", ni "hacer un proyecto de FPGA que haga trading": es esa frase,
falsable, con un umbral (el piso de latencia medido) contra el cual medirse.

---

## 4. El proyecto de Arquitectura de Computadores — dónde converge y dónde diverge

Nicolás cursa Arquitectura de Computadores. Su proyecto final es implementar
en RTL (Verilog/VHDL, hardware descriptivo) un pipeline de decisión de
trading intradía, validado con un backtest sobre datos históricos.

**Plataforma de partida:** Nandland Go Board, FPGA Lattice iCE40HX1K, ~1280
LUTs. Es una FPGA muy pequeña, de entrada.

**Candidata en evaluación:** Digilent Arty A7-100T, FPGA Xilinx Artix-7
XC7A100T, ~101.000 celdas lógicas / ~15.850 slices — dos órdenes de magnitud
más grande que la Go Board.

**La elección de placa es de Nicolás.** Este documento no la decide, no la
recomienda, y no la necesita decidida para congelarse: los criterios de la
§5 y §6 se formulan en términos del piso de latencia medido, sea cual sea la
placa donde se mida.

**Este pre-registro sirve a dos objetivos a la vez, y hay que decir dónde
divergen:**

| | Objetivo (a): pista de investigación GEMELO/MICRO | Objetivo (b): proyecto de Arquitectura de Computadores |
|---|---|---|
| Qué se evalúa | Si hay evidencia estadística de ventaja económica real | Si el pipeline RTL está correctamente diseñado, verificado y con pipelining razonable |
| Condición de éxito | V1–V5 de la §5, sin excepción | Backtest de respaldo funcionando y RTL correcto, **sin importar el resultado de (a)** |
| Qué pasa si la ventaja es nula o negativa | Fracasa (a) | (b) no fracasa: es un resultado de arquitectura de computadores válido igual |
| Quién lo evalúa | Esta pista, con los mismos estándares que el resto de GEMELO | El curso, con los estándares de esa materia |

**Dicho sin ambigüedad:** el proyecto académico tiene éxito con un pipeline
RTL correcto y bien validado aunque la ventaja económica sea nula o
negativa. Se evalúa la implementación, el diseño, el pipelining, la
verificación contra el backtest de referencia — no el PnL. La pista de
investigación de GEMELO/MICRO, en cambio, solo tiene éxito si hay evidencia
estadística de ventaja real, bajo los criterios de la §5. Un resultado
negativo en (a) **no es un fracaso de (b)**, y nadie debe medir el proyecto
de la materia con la vara de la pista de investigación, ni al revés.

---

## 5. Criterios de victoria — CONGELADOS

Se fijan ahora, sin resultados a la vista, con el mismo rigor que el resto de
GEMELO (Wilson, McNemar, denominador honesto, corrección por intentos vía
DSR cuando aplique — ver `.claude/skills/estadistica-evaluacion/` y
`GEMELO/DISEÑO.md` §4.2 bis para el protocolo de conteo).

- **V1 — Ventaja direccional medible.** En la ventana de decisión definida en
  la §3 (1 a 60 segundos post-evento), la regla de decisión implementable en
  hardware le gana a una baseline honesta (por ejemplo "mantener posición sin
  reaccionar" o "seguir el movimiento del instrumento correlacionado sin
  ningún procesamiento") evaluada **sobre las mismas filas**, con McNemar
  **p < 0.05**, denominador declarado, sobre datos tick-level reales — nunca
  simulados ni sintéticos.
- **V2 — Piso de latencia compatible.** El piso de latencia medido de la
  plataforma de referencia (hardware real, no una capa de virtualización) es
  al menos un **orden de magnitud menor** que la vida media medida o
  estimada del efecto informacional bajo estudio. Sin esto, V1 puede ser
  cierto y la plataforma igual no puede capturarlo.
- **V3 — Conteo de intentos declarado.** Si se evalúa más de una
  configuración de regla de decisión, ventana de reacción, o umbral de
  activación, cada una cuenta como un intento para el Deflated Sharpe, con
  **N declarado antes de correr ninguna**, siguiendo el mismo protocolo que
  `GEMELO/DISEÑO.md` §4.2 bis. Un N contado después de ver resultados no
  sirve, aquí tampoco.
- **V4 — Correctitud funcional del RTL.** El pipeline RTL reproduce las
  mismas decisiones que una implementación de referencia en software sobre
  el mismo backtest, dentro de una **tolerancia declarada por adelantado**
  (por ejemplo: mismo signo de decisión en el 100% de los casos, y magnitud
  dentro de un error de cuantización de punto fijo explícitamente acotado).
  La tolerancia se fija antes de correr la comparación, no después de ver
  cuánto difieren.
- **V5 — Latencia end-to-end medida en hardware real.** El tiempo entre la
  llegada del evento de mercado al pipeline y la decisión emitida se mide en
  la FPGA real, no en simulación de timing ni en una capa virtualizada. Una
  cifra de latencia que solo existe en simulación no cuenta para V2.

---

## 6. Criterios de rechazo — CONGELADOS

El retador de esta pista (la hipótesis de la §2, no ninguna variante
particular de ella) se descarta si:

- **R1 — mata la pista completa, no una variante.** Si el piso de latencia
  medido de la plataforma de referencia (o de cualquier plataforma de FPGA
  de gama de estudiante disponible) es **mayor en orden de magnitud** que la
  vida media medida o estimada del efecto informacional, **la pista completa
  se cierra como NO CONCLUYENTE PERMANENTE para esta generación de hardware**.
  No se sigue empujando distintas variantes de regla de decisión, ni distintos
  eventos de mercado, ni distintas ventanas de reacción: si el piso de la
  máquina es estructuralmente más lento que la vida del fenómeno, ninguna
  variante lo arregla. Esto es exactamente lo que ya se observó en miniatura
  en `GEMELO/MICRO/WSL2.md`: un piso de despertar de ~72–85 µs que no se
  mueve por más corto que se pida dormir por debajo de él. Si el equivalente
  en hardware real resulta igual de rígido frente a la vida media del efecto,
  R1 se activa y la pista termina ahí.
- **R2 — degradación explícita por falta de datos.** Si no hay ninguna
  fuente de datos de alta frecuencia (tick-level o mejor) disponible sin
  costo prohibitivo para validar la hipótesis de la §2, la pista **se
  degrada** a "proyecto de arquitectura de computadores sin componente de
  investigación validada", y se declara así de manera explícita en vez de
  forzar una conclusión sobre datos que no alcanzan el nivel necesario.
- **R3 — el RTL no reproduce la referencia.** Si el pipeline RTL no cumple
  V4 (correctitud funcional dentro de la tolerancia declarada), no hay base
  para atribuirle a la implementación en hardware ningún resultado de la §5:
  se corrige el RTL o se documenta la discrepancia, pero no se reporta una
  latencia ni una ventaja económica sobre un pipeline que no está probado
  correcto.
- **R4 — fuga detectada.** Cualquier fuga de información (mirar datos
  posteriores al instante de decisión, en el sentido del test de causalidad
  que ya rige el resto de `GEMELO/` y `backtest/`) invalida el resultado sin
  discusión y sin excepción.

---

## 7. Qué NO se hace en esta etapa

- **No se compra hardware.** Ni la Go Board ni la Arty A7-100T se adquieren
  como parte de este documento.
- **No se elige la placa.** Esa decisión es de Nicolás, marcada
  explícitamente como tal en la §4. Este documento no la anticipa ni la
  condiciona.
- **No se toca `motor.py` ni la lógica de señales de producción.** Tampoco
  `senales.py`, `snapshot.py` ni `universo.py`. Regla cero, sin excepción.
- **No se opera con dinero real ni se conecta a ningún broker.** En ningún
  momento de esta pista.
- **No se construye el pipeline RTL todavía.** Este documento es anterior a
  la primera línea de RTL. Escribir RTL antes de que exista este
  pre-registro sería exactamente el error que el pre-registro existe para
  impedir.

---

## 8. Riesgos declarados, antes de medir

**El más incómodo primero: que el piso de latencia alcanzable con esta
plataforma (o con cualquier plataforma de hardware de estudiante) haga la
pregunta irrelevante.** Es decir, que aunque exista una ventaja
informacional real a escala de microsegundos, ninguna implementación con
este presupuesto y este hardware pueda capturarla antes de que se disipe —
con lo cual la pregunta de investigación de la §3 es correcta, pero la
plataforma disponible no puede responderla. Ya hay evidencia preliminar y
medida de esto: el arnés de medición en `micro/` (ver
`GEMELO/MICRO/WSL2.md`) midió en esta máquina (WSL2 sobre Windows) un piso de
despertar del planificador de **~72–85 microsegundos, constante
independientemente de cuánto se pida dormir por debajo de esa cifra**. Es
evidencia de que medir con software de uso general sobre una capa de
virtualización no puede caracterizar regímenes de latencia por debajo de la
decena de microsegundos. No demuestra todavía nada sobre la FPGA real (que
no corre bajo WSL2), pero establece el patrón que R1 vigila: un piso que no
cede sin importar cuánto se le pida.

Otros riesgos, declarados antes de que se materialicen:

1. **Los datos de mercado disponibles hoy en MKI son de cierre diario / gap
   de apertura, NO tick-level.** No hay todavía ninguna fuente de datos de
   alta frecuencia identificada para validar la hipótesis con datos reales.
   V1 puede terminar siendo **no evaluable por falta de datos, no por falta
   de señal** — y esas dos cosas no se deben confundir en el reporte final.
2. **Confundir "el proyecto de la materia funciona" con "hay ventaja
   económica" es el sesgo más fácil de cometer acá.** La §4 ya lo separa en
   una tabla; este riesgo es que, en la práctica, sea tentador reportar el
   éxito de (b) como si fuera evidencia a favor de (a). No lo es, y no se
   debe reportar así.
3. **El efecto de decaimiento medido en GEMELO es sobre una asimetría
   informacional específica** (SOX→bolsas asiáticas/europeas, con un
   mecanismo de propagación entre mercados y zonas horarias medido y
   documentado). Extrapolarlo a la escala de microsegundos dentro de UN SOLO
   mercado es una **analogía**, no una demostración. La hipótesis de la §2
   se apoya en esa analogía a propósito, y hay que decirlo así de explícito
   cada vez que se cite.

---

## 9. Lo primero que hay que hacer

**Identificar si existe una fuente de datos tick-level accesible sin costo
prohibitivo, antes de escribir una sola línea de RTL.** Sin esa fuente, V1 no
es evaluable y R2 se activa por definición. Ningún otro paso de esta pista
(diseño del pipeline, elección de placa, medición de piso de latencia en
hardware real) empieza antes que eso.
