# Las 15 huérfanas — forense

**Fecha:** 1-sep-2026, sexta corrida. **Estado:** forense cerrado.
**NO se propone ninguna regla acá**, por encargo explícito: el forense
anterior descubrió que los 30 duplicados eran **dos fenómenos distintos** y
eso cambió la decisión. Primero se entiende, después se decide.

> **Nota de procedencia.** El forense lo hizo el agente `integridad-datos`,
> cuyo entorno le prohíbe escribir archivos de informe; entregó todo en su
> reporte y este archivo lo transcribe. Las cifras son **recuentos
> exhaustivos** sobre las filas existentes, no muestras, así que **no
> llevan intervalo** — la regla 3 pide intervalo para estimadores, y un
> censo no lo es.

## 0. Verificación independiente del punto de partida

Recalculó `proxima_sesion_despues_de(exchange, available_at)` sobre las
**279 filas** con predicción real y comparó contra lo sellado, **sin usar
`ahora_utc` en ningún punto** — o sea que no reprodujo el mecanismo que
produjo el error, y por eso cuenta como verificación bajo la regla 1.

```
total filas con predicción real: 279
total mal calculadas: 25
  2026-07-05  8      2026-07-29  7
  2026-08-03  3      2026-08-05  7
```

Confirma el 25 y su partición: **10 en pares** (07-29 + 08-03) y **15
huérfanas** (07-05 + 08-05).

## 1. Los dos grupos

**Grupo A — 7 filas, emisión 2026-08-05.** `origen=programado`,
`plataforma_version=5.0.1`. Sellado a las **01:38 UTC del 06-ago** tras
disparar a las 18:20 Chile: el Mac se re-durmió durante los reintentos.
Apuntan a 08-07 cuando correspondía 08-06. **Sin pareja porque el snapshot
del 06-ago sufrió caída total** (§4).

**Grupo B — 8 filas, emisión 2026-07-05.** `origen=manual`,
`plataforma_version=NULL` — y eso **no es dato faltante**: la constante no
existía todavía, se introdujo el 25-jul. Apuntan a 07-06 cuando
correspondía **07-03**. Sin pareja porque **no hubo ningún otro sello esa
semana**: 07-02 y 07-03 sin snapshots, 07-04 sólo una fila
`legacy_pre_4.6`, 07-06 tampoco.

**El fenómeno ya estaba caracterizado tres semanas antes.** El acta de la
Etapa 5.0.2 (8-ago) reconstruyó el 05-ago desde los logs y anotó, en
tiempo real, *"7 saltaron a la sesión del 07"*. Lo que faltaba no era la
observación: era ponerle nombre de línea de código.

## 2. La hipótesis de Nicolás, contrastada

**Parte 1 — "corresponden a un período en que sólo el Mac registraba":
CONFIRMADA sin ambigüedad.** Calendario reconstruido desde `version.py`
(git log), `DECISIONES.md` y `docs/REACTIVACION.md` — no desde `ESTADO.md`,
que es un resumen. Los dos grupos caen **semanas antes del 25-ago**, cuando
el PC en su encarnación actual **no existía todavía**.

**Parte 2 — "las diferencias aparecen cuando ambas registraban a la vez":
CONFIRMADA, y con evidencia de esta misma semana.** En
`data/sombra/comparacion_2026-08-26.md`, durante la ventana de sombra: el
Mac selló **1 h 51 min tarde**, cruzando la medianoche UTC
(`timestamp_utc = 2026-08-27T00:05:50Z`) mientras el PC selló a horario. Es
**exactamente el defecto de `snapshot.py:140`**, y el reporte de paridad lo
capturó como hallazgo de nivel 2 en `sesion_objetivo` **para 6 de los 8
tickers** — los de apertura 00:00 UTC; XTAI (01:00) y XETR (07:00) no se
vieron afectados, consistente con la aritmética. Al día siguiente, 31 min
tarde **sin cruzar ninguna apertura**, no hay hallazgo: el disparador es
**cruzar la medianoche UTC, no la tardanza en sí**.

> **Y esta instancia NO está entre las 25.** La regla de composición
> canónica (`fecha ≥ 2026-08-26 → canónico el PC`) eligió para ese día el
> lado del PC, que casualmente es el correcto. **El defecto disparó esta
> misma semana, en pleno registro dual, y es invisible en el recuento sólo
> porque la composición canónica lo tapó al elegir la copia buena.** No
> porque haya dejado de ocurrir.

**El matiz que hay que decir con todas las letras:** el registro dual **no
causa** el defecto — es un bug de un solo proceso, atado a si su propio
reloj de pared cruza la apertura UTC antes de terminar de sellar, y
dispara igual con una máquina sola. Lo que el registro dual **sí hace es
volverlo visible** como discrepancia entre fuentes. Leída así —"el registro
dual es la condición que revela, no la causa"— la hipótesis queda
confirmada con evidencia, no con inferencia.

## 3. ¿Un fenómeno o varios?

**A nivel de mecanismo de código: uno solo.** Recalcular desde
`available_at` explica el **100%** de las 25 y también la instancia del
26-ago, sin ningún caso residual.

**A nivel de huella en los datos hay tres ejes, y uno corrige el encargo:**

1. **Elegibilidad de verificación — y acá el encargo estaba corto.** Se
   creía que sólo las 8 de julio pasarían a `no_verificable_timing`.
   Verificado: **las 7 de agosto también**. Con `available_at` corregido,
   la sesión correcta (08-06) **ya había abierto** cuando el proceso selló
   (01:38 UTC). La diferencia entre grupos es de **severidad, no de
   resultado**: agosto queda a mitad de la sesión correcta, julio con la
   sesión **ya cerrada por completo**. **En este eje las 15 dan el mismo
   desenlace.**
2. **Por qué falta la pareja — acá sí difieren**, y el encuadre previo era
   correcto: agosto por un defecto *distinto* que borró la fila fresca;
   julio porque no hubo con qué chocar.
3. **Un cuarto tipo de huella, nuevo:** la divergencia cruzada Mac-PC del
   26-ago, visible sólo por haber dos fuentes, y **absorbida
   silenciosamente por la composición canónica**.

**Y el riesgo simétrico que hay que tener a la vista:** una corrección que
toque `sesion_objetivo` **sin tocar `estado`** dejaría 15 filas
"corregidas" pero **todavía contando como `verificada`** en las métricas,
cuando las 15 dejarían de serlo bajo la regla maestra vigente desde la
Etapa 4.6.

## 4. Qué pasó el 2026-08-06 — no era una incógnita

**Ya estaba reconstruido y documentado en `DECISIONES.md` desde el 8-ago**,
23 días antes de esta corrida. La reconstrucción, con logs que hoy ya
rotaron:

1. 18:24:48 Chile — arranque tarde; descarga 28/28 en 4 s.
2. 18:24:52 — se estampa `ts_emision` y arranca el cómputo. **El Mac se
   re-duerme: el proceso queda congelado ~44 minutos**, con el timestamp
   ya escrito y nada más en la base.
3. ~19:08 — despierta. El TTL de 15 min de la caché expiró, y la
   re-descarga en red inestable **falla para 12 tickers + `^KS11` + `^SOX`**.
4. `prediccion_apertura_al` necesita `^SOX`: devuelve vacío → **0
   predicciones**, `sox_usado_pct`/`sox_fecha` NULL. `regimen` y
   `roca_chip` sí quedaron bien porque se calcularon **antes** del
   congelamiento.
5. **La salud sellada (28/28) describe el lote de las 18:24 que las
   predicciones nunca llegaron a usar** — el acta lo llama, con razón,
   "hallazgo de honestidad".

> **Y acá hay un hallazgo de proceso que vale por sí solo.** Tres
> documentos de la capa GEMELO —`cola_decisiones.md`, `bifurcaciones.md` y
> `espera_firma.md`— marcan el 06-ago como **"cabo suelto anotado y no
> investigado"**. La respuesta existía hacía tres semanas en
> `DECISIONES.md`. **Ninguno de los tres lo cruzó.** La memoria
> institucional estaba escrita y la capa que la necesitaba no la leyó.

## Lo que NO se pudo determinar

- La atribución fina **Yahoo-real vs. red-dormida** para los 12 tickers que
  fallaron el 06-ago: los logs primarios rotaron y no están en git
  (verificadas las dos cosas).
- La fecha exacta en que murió el SSD del PC viejo. Sólo que fue antes del
  25-ago y que **ese PC nunca llegó a sellar en producción**.

## Resumen para quien decida sobre las 15

- Ambos grupos son de la era **sólo-Mac**, confirmado contra el calendario
  real de versiones.
- El registro dual **no causa** el defecto pero **sí lo revela** — con
  evidencia fresca del 26-ago, **fuera del recuento de 25**.
- Las 15 **comparten mecanismo y comparten desenlace de verificación** (las
  15, no 8, caerían en `no_verificable_timing`); difieren sólo en **por qué
  carecen de pareja**.
- El 06-ago **no es una incógnita**: está resuelto desde el 8-ago, y la
  desconexión documental es parte del hallazgo.
