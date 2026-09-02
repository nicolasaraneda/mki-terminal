# ⚠ CORRIDA DE VEREDICTO CON EL GATILLO **NO CUMPLIDO**

**Esto NO es el veredicto definitivo de la Etapa 5.1.** El gatillo congelado en `backtest/DISEÑO.md` §11 no está cumplido por ninguna de sus dos vías:

Estado del gatillo congelado (`backtest/DISEÑO.md` §11):

- **(a)** N ≥ 150 verificaciones limpias **Y** un cambio de régimen del SOX: 261 verificaciones limpias — CUMPLE la primera mitad —, pero el track record tiene **una sola etiqueta de régimen** (`Alcista · vol alta`, 38 snapshots, más 2 nulos). La conjunción **NO se cumple**.
- **(b)** 3 meses continuos desde el 25-jul-2026: faltan **54 días** (cae el 25-oct-2026). **NO se cumple**.

**Correcciones del arnés aplicadas antes de esta corrida** (la corrección va al ejecutable, no al texto):

- **B-1 CORREGIDA** — `SentimientoPIT` corta por `max(publicación, analizado_en) <= 22:15 UTC`: hacen falta LAS DOS marcas para que el juicio exista. (El acta lo había escrito como `min()`; con el mínimo el predicado colapsa al roto, porque `analizado_en` es posterior a la publicación por construcción — errata para DECISIONES.md.) `buzz` pasa por el mismo corte y estrena grado propio; el relleno neutro dejó de viajar como si fuera dato y se declara como **grado S**. Tests: `tests/test_backtest.py::test_b1_*` (5).
- **B-2 CORREGIDA** — el corte lo hace ahora `recortar_pit()`, que recibe la serie SIN recortar, y la guarda de verdad es el GATE DE CAUSALIDAD (`backtest/causalidad.py`): reconstruye el arnés entero —precios, OHLC **y noticias**— con la fuente truncada en D y exige predicción idéntica. Corre DENTRO de la corrida, sobre 12 fechas × 6 baselines, y la mata si algo se mueve. Contraprueba permanente: 10 tests parametrizados inyectan `shift(-1)` en cada feature —incluidas las cinco exclusivas de B4/B5— y exigen que el gate DISPARE. Una guarda sin contraprueba no es una guarda.

**Defectos del arnés ABIERTOS.** No son fugas temporales —R3 no los juzga— pero bloquean el veredicto igual, y decirlo separado es la diferencia entre *«el arnés tiene fuga»* y *«el arnés tiene la unidad de observación mal»*:

- **B-3 · el mismo desenlace cuenta hasta 8 veces.** Varias emisiones consecutivas apuntan a la MISMA sesión objetivo en feriados largos y `motorbt` escribe una fila por emisión con el outcome repetido. **No es fuga de futuro: es contaminación de la unidad de observación.** Se mide en cada corrida (`impacto_b3_duplicados`) y sigue SIN corregir.
- **B4 y B5 no son evaluables sobre la ventana larga.** No es un defecto del código sino de los datos que existen: el primer juicio de IA del sistema es del 2026-07-04 y la ventana empieza el 2024-09-02, así que con el corte honesto la enorme mayoría de sus filas se emiten con las tres features de noticias en el relleno neutro. Sus cifras NO contestan *«¿las noticias aportan?»*.
- **S-1 · el embargo purga días CORRIDOS, no jornadas.** Declarado y sin corregir; cambiarlo la víspera del veredicto sería mover el arnés después de haber visto el diseño.
- **S-3 · `estado_gatillo` se recibe, no se computa.**
- **No hay holdout MATERIAL.** La cuarentena de V7 es procedimental: no hay split, constante de fecha, archivo ni tabla que reserve datos. V7 no sólo no se evaluó — hoy no es evaluable.
- **La fuente no es point-in-time.** Yahoo reescribe la historia en silencio; se mide contra los sellos reales en cada corrida (`fidelidad_b2_vs_sellos`) y es una limitación de primer orden.

**El holdout en cuarentena NO se evaluó y queda INTACTO.** `GEMELO/DISEÑO.md` §6.1 V7 lo define como *evaluado una sola vez*: es un recurso irreversible y gastarlo con el gatillo sin cumplir lo quemaría para siempre. V7 queda NO EVALUABLE por esta razón, no por falta de maquinaria.

Expediente de la decisión pendiente: `GEMELO/resultados/gatillo_51.md`.

# Backtest MKI — 5.1-arnes-corregido-gatillo-incumplido · 2024-09-02 → 2026-08-28

Generado 2026-09-01T13:31:54.858933+00:00 · commit 6bb1f46 · descartes sin datos: 8

Parámetros: embargo 5 días · ventana entrenamiento 250 · reajuste cada 7 días

Bootstrap: circular de bloques (Politis & Romano 1994) · bloque 10 días · 2000 réplicas · semilla 20260901 · IC 95%

Gate de causalidad: **INVARIANTE** · 72 comparaciones (12 fechas × 6 baselines) · invariancia al truncado de precios, OHLC **y noticias** · contraprueba `shift(-1)` en la suite

Sentimiento point-in-time (B-1): el corte es `max(publicación, analizado_en) <= 22:15 UTC` — el juicio de la IA sólo existe cuando existe. 66.6% de los 6104 pares (titular × ticker) quedaron disponibles DESPUÉS de su publicación (rezago máximo 320 días); el primer dato disponible es del **2026-07-04** aunque el primer titular sea del 2025-09-09. Accesos a la feature con sentimiento real: **580**; sin ninguno (relleno neutro declarado, grado S): **8580**.


## Baselines

| B | n | %grado B | %grado S (sin noticias) | IC medio | t(NW) | MAE gap | Sharpe LS 25pb [IC95] | acum. LS 25pb |
|---|---|---|---|---|---|---|---|---|
| B0 | 4152 | 0.0% | 0.0% | 0.0 | nan | 1.846 | -5.44 [-7.00, -3.93] | -91.4% |
| B1 | 4152 | 0.0% | 0.0% | -0.0306 | -1.45 | 1.847 | -6.06 [-7.55, -4.66] | -92.4% |
| B2 | 4152 | 0.0% | 0.0% | 0.2331 | 11.21 | 1.543 | -6.97 [-8.37, -5.74] | -95.6% |
| B3 | 4152 | 0.0% | 0.0% | 0.2228 | 9.77 | 1.562 | -7.97 [-9.29, -6.76] | -96.8% |
| B4 | 4152 | 0.8% | 93.1% | 0.2216 | 9.87 | 1.564 | -7.97 [-9.29, -6.76] | -96.7% |
| B5 | 4152 | 0.8% | 93.1% | 0.2036 | 8.67 | 1.564 | -7.84 [-9.25, -6.66] | -96.0% |

**B4 y B5 NO son evaluables sobre esta ventana.** Filas emitidas SIN un solo juicio de IA disponible (B4: 93.1% · B5: 93.1%): sus tres features de noticias valen el relleno neutro 0.0 y la capa colapsa a la anterior. Sus cifras se leen como lo que son —la capa de precios con columnas constantes—, no como *«las noticias no aportan»*. **B0, B1, B2 y B3 no tocan el sentimiento y siguen evaluables sobre la ventana completa.**


**Benchmark obligatorio — comprar SMH y no hacer nada**: acumulado 137.1% · Sharpe 1.32 · MDD -32.6% — toda cartera se lee CONTRA esta línea (ajuste GATE B).


## Veredicto escalonado (capa vs capa)

| Capa | ΔIC | t(NW) | días | veredicto |
|---|---|---|---|---|
| B1 vs B0 | -0.0306 | -1.45 | 520 | no demostrado |
| B2 vs B1 | 0.2638 | 8.68 | 520 | aporta |
| B3 vs B2 | -0.0103 | -0.77 | 520 | no demostrado |
| B4 vs B3 | -0.0012 | -0.47 | 520 | no demostrado |
| B5 vs B4 | -0.0179 | -2.55 | 520 | no demostrado |

## Auditoría B2 vs sellos reales
261 predicciones comparadas · diferencia media 0.167 pp · máx 5.3 pp. las diferencias reflejan deriva de datos de la fuente entre el sello y hoy (hallazgo 4.7.1), no necesariamente un bug.


---
Herramienta de análisis — no constituye asesoría financiera. Diseño congelado en backtest/DISEÑO.md.


---

# Veredicto de la Etapa 5.1 — B0→B5

## R3: LIMPIO. Y aun así esto NO es el veredicto de la 5.1.

`GEMELO/DISEÑO.md` §6.2 **R3**: *«cualquier fuga detectada por el test de causalidad. Sin discusión y sin excepción.»* El test de causalidad existe ahora de verdad —invariancia al truncado de precios, OHLC **y noticias**, con contraprueba `shift(-1)` que lo hace fallar a propósito— y sobre **72 comparaciones (12 fechas × 6 baselines)** no detecta ninguna fuga. **R3 no dispara.**

Lo que impide el veredicto ahora es otra cosa, y hay que decirlo con la misma firmeza: el **gatillo congelado del GATE B no está cumplido** (`backtest/DISEÑO.md` §11) y quedan **defectos abiertos del arnés que no son fugas temporales** pero sí contaminan la unidad de observación. El **holdout NO se gastó**.

Expediente completo, con el conteo de intentos declarado antes de correr: `GEMELO/resultados/gatillo_51.md`.

## Tabla de criterios

| Criterio | Veredicto | Razón |
|---|---|---|
| **V1** | PASA (GATILLO NO CUMPLIDO — no es el veredicto de la 5.1) | Habilidad sobre 'siempre al alza' en las MISMAS filas |
| **V2** | PASA (GATILLO NO CUMPLIDO — no es el veredicto de la 5.1) | CRPS vs el campeón, IC de bootstrap circular |
| **V3** | PASA (GATILLO NO CUMPLIDO — no es el veredicto de la 5.1) | Cobertura empírica del intervalo 80% |
| **V4** | NO PASA (GATILLO NO CUMPLIDO — no es el veredicto de la 5.1) | MAE del gap vs el campeón en ventana |
| **V5** | NO PASA (GATILLO NO CUMPLIDO — no es el veredicto de la 5.1) | DSR ≥ 0.95 con N declarado = 92 |
| **V6** | NO PASA (GATILLO NO CUMPLIDO — no es el veredicto de la 5.1) | Superar comprar SMH y no hacer nada, a 25 pb por lado |
| **V7** | NO EVALUABLE | Holdout en cuarentena — **deliberadamente NO gastado** |
| **R1** | NO EVALUABLE | Control lineal vs retador — no hay retador en esta corrida |
| **R2** | PASA | La ventaja sobrevive excluyendo 15–23 jul |
| **R3** | PASA | **Gate de causalidad INVARIANTE — no dispara.** |
| **veredicto_final_diseno_8** | NO AGREGA VALOR | El criterio de lectura del §8 |

## B-1 corregido — y lo que sobrevive al corte honesto

El sentimiento ya no se corta por la fecha de PUBLICACIÓN del titular sino por `max(publicación, analizado_en)`: hacen falta **las dos** marcas para que el juicio exista. (El acta lo había escrito como `min()`; con el mínimo el predicado colapsa al roto, porque `analizado_en` es posterior a la publicación por construcción. La corrección va al ejecutable.)

- Pares (titular × ticker) en `noticias.db`: **6104**, de los cuales **66.6%** quedaron disponibles DESPUÉS de su publicación (rezago máximo 320 días).
- Primer dato de IA disponible en el sistema: **2026-07-04**. Primer titular publicado: 2025-09-09.
- Accesos distintos (ticker × fecha × set de columnas) a la feature de sentimiento con dato REAL: **580** de 9160 (**6.33%**). El resto se resolvió con el relleno neutro 0.0, declarado como **grado S**.

**El denominador que importa — filas EMITIDAS, no accesos a la caché:**

| B | filas | con sentimiento real | %|
|---|---|---|---|
| B4 | 4152 | 288 | 6.94% |
| B5 | 4152 | 288 | 6.94% |

### B4 y B5 NO son evaluables sobre esta ventana

Con el corte honesto, **B4: 93.1% de sus filas sin ninguna noticia disponible** · **B5: 93.1% de sus filas sin ninguna noticia disponible**. Sus tres features de noticias valen la constante 0.0 en esas filas, así que la capa colapsa a la anterior. Sus cifras se leen como *«la capa de precios con columnas constantes»*, **jamás** como *«las noticias no aportan»*: esa pregunta no se puede contestar con dos años de datos porque el sistema sólo tiene noticias analizadas desde 2026-07-04.

**B0, B1, B2 y B3 no tocan el sentimiento y siguen evaluables sobre la ventana completa.** Que dos baselines de seis no sean evaluables no es que el backtest no lo sea.


## V6 — el benchmark obligatorio

**Comprar SMH y no hacer nada: 137.1% acumulado, Sharpe 1.32, MDD -32.6%.**

| B | LS 10 pb | LS 25 pb | LS 50 pb | LO 25 pb | Sharpe LS 25 pb |
|---|---|---|---|---|---|
| B0 | -58.8% | **-91.4%** | -99.4% | -90.1% | -5.44 |
| B1 | -63.8% | **-92.4%** | -99.4% | -91.3% | -6.06 |
| B2 | -79.0% | **-95.6%** | -99.7% | -94.1% | -6.97 |
| B3 | -84.5% | **-96.8%** | -99.8% | -94.9% | -7.97 |
| B4 | -84.3% | **-96.7%** | -99.8% | -94.9% | -7.97 |
| B5 | -80.9% | **-96.0%** | -99.7% | -92.7% | -7.84 |

**Ninguna cartera, en ningún nivel de costos, supera al benchmark.** El diseño ya lo había anticipado con *«una estrategia que sólo vive con 10 pb no aprueba»*.

## V5 — Deflated Sharpe con el N declarado

| B | Sharpe LS 25 pb | días | skew | curtosis | PSR vs 0 | DSR N=26 | DSR N=44 | DSR N=82 | DSR N=86 | DSR N=92 | DSR N=110 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | -5.436 | 520 | -0.421 | 4.68 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| B1 | -6.062 | 520 | -0.268 | 5.408 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| B2 | -6.969 | 520 | -0.425 | 5.722 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| B3 | -7.974 | 520 | -0.35 | 4.491 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| B4 | -7.966 | 520 | -0.323 | 4.738 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| B5 | -7.84 | 520 | -0.065 | 4.225 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

`V_intentos` = 1.1812 · umbral deflactado `SR0` = 2.7183 a N=92.

Los 520 días de retornos superan el mínimo de 60: el DSR **es interpretable**.

Sharpe long-short a 25 pb observado: de -7.974 a -5.436.

El conteo de intentos se declaró en **N = 92** ANTES de correr, con banda [26, 44, 82, 86, 92, 110], y no se movió después de ver un solo resultado.

## V1 — dirección del gap contra 'siempre al alza', mismas filas

| B | n | acierto % | Wilson 95% | base % | ventaja pp | McNemar p |
|---|---|---|---|---|---|---|
| B0 | — | — | — | — | — | — |
| B1 | 4150 | 53.59% | [52.07, 55.1] | 55.54% | -1.95 | 0.0002 |
| B2 | 4120 | 69.0% | [67.58, 70.4] | 55.61% | 13.4 | 0.0 |
| B3 | 4152 | 68.38% | [66.95, 69.77] | 55.56% | 12.81 | 0.0 |
| B4 | 4152 | 68.3% | [66.87, 69.7] | 55.56% | 12.74 | 0.0 |
| B5 | 4152 | 68.35% | [66.92, 69.75] | 55.56% | 12.79 | 0.0 |

## Defectos ABIERTOS del arnés — no son fugas, y bloquean igual

- **B-3 · el mismo desenlace cuenta hasta 8 veces.** Varias emisiones consecutivas apuntan a la MISMA sesión objetivo en feriados largos y `motorbt` escribe una fila por emisión con el outcome repetido. **No es fuga de futuro: es contaminación de la unidad de observación.** Se mide en cada corrida (`impacto_b3_duplicados`) y sigue SIN corregir.
- **B4 y B5 no son evaluables sobre la ventana larga.** No es un defecto del código sino de los datos que existen: el primer juicio de IA del sistema es del 2026-07-04 y la ventana empieza el 2024-09-02, así que con el corte honesto la enorme mayoría de sus filas se emiten con las tres features de noticias en el relleno neutro. Sus cifras NO contestan *«¿las noticias aportan?»*.
- **S-1 · el embargo purga días CORRIDOS, no jornadas.** Declarado y sin corregir; cambiarlo la víspera del veredicto sería mover el arnés después de haber visto el diseño.
- **S-3 · `estado_gatillo` se recibe, no se computa.**
- **No hay holdout MATERIAL.** La cuarentena de V7 es procedimental: no hay split, constante de fecha, archivo ni tabla que reserve datos. V7 no sólo no se evaluó — hoy no es evaluable.
- **La fuente no es point-in-time.** Yahoo reescribe la historia en silencio; se mide contra los sellos reales en cada corrida (`fidelidad_b2_vs_sellos`) y es una limitación de primer orden.

### B-3 medido sobre ESTA corrida

Las MISMAS filas releídas colapsando los desenlaces duplicados por `(ticker, sesión objetivo)`:

| B | filas | ventaja pp | IC medio | t(NW) | MAE |
|---|---|---|---|---|---|
| B0 | 4152 → 3889 | — → — | 0.0 → 0.0 | nan → nan | 1.846 → 1.784 |
| B1 | 4152 → 3889 | -1.95 → -1.83 | -0.0306 → -0.0392 | -1.45 → -1.88 | 1.847 → 1.784 |
| B2 | 4152 → 3889 | 13.4 → 14.13 | 0.2331 → 0.2461 | 11.21 → 11.65 | 1.543 → 1.47 |
| B3 | 4152 → 3889 | 12.81 → 13.37 | 0.2228 → 0.2443 | 9.77 → 11.03 | 1.562 → 1.486 |
| B4 | 4152 → 3889 | 12.74 → 13.27 | 0.2216 → 0.243 | 9.87 → 11.14 | 1.564 → 1.489 |
| B5 | 4152 → 3889 | 12.79 → 13.32 | 0.2036 → 0.2286 | 8.67 → 10.26 | 1.564 → 1.488 |

La unidad de observación sigue mal y hay que arreglarla; la lectura de la dirección del efecto se hace sobre estas cifras, no sobre las de ninguna corrida anterior.

## La fuente no es point-in-time, y está medido

`B2` contra las predicciones realmente selladas por producción, 261 filas: diferencia mediana **0.03 pp**, media **0.1669 pp**, máxima **5.3 pp**. La peor fecha es **2026-08-28** (media 3.2312 pp); sin ella la media cae a **0.07 pp** y el máximo a 0.61 pp.

**Yahoo reescribe la historia en silencio**: la serie que se descarga hoy no es la que existía el día del sello. Es una limitación de primer orden del backtest entero, no una nota al pie.

---

## Qué queda por arreglar antes de que exista un veredicto

En este orden, y el primer entregable de cada punto es el **test**, no el arreglo:

1. ~~**B-1** — cortar el sentimiento por `analizado_en`.~~ **HECHO** (`max(publicación, analizado_en)`); `buzz` pasa por el mismo corte y tiene grado propio.
2. ~~**B-2** — prueba maestra sobre B0–B5 × ≥10 fechas y contraprueba `shift(-1)` permanente.~~ **HECHO** (`backtest/causalidad.py` + 10 contrapruebas parametrizadas).
3. **B-3** — deduplicar por `(ticker, sesión objetivo)` o declarar la sesión objetivo como unidad de observación. **ABIERTO.**
4. **S-1** — contar sesiones del calendario, no días corridos, y sellar las efectivamente purgadas. **ABIERTO.**
5. **S-3** — computar `estado_gatillo` en vez de recibirlo. **ABIERTO.**
6. Construir un **holdout material**: hoy la cuarentena es sólo procedimental. **ABIERTO.**

---
Herramienta de análisis — no constituye asesoría financiera. Criterios congelados en `backtest/DISEÑO.md` §8 y `GEMELO/DISEÑO.md` §6; ninguno fue modificado para esta corrida.

---

## ERRATA documentada (añadida el 2-sep-2026, octava corrida) — NO se recalculó nada

**Las cifras de arriba se conservan exactamente como se generaron.** Los
PSR/DSR de esta corrida se calcularon con el **Sharpe ANUALIZADO** pasado a
`inferencia.psr`/`dsr`, cuya unidad es el Sharpe POR PERÍODO: el z estaba
inflado por √252 (Frente A de la octava corrida, A3). **Los veredictos de
este documento no cambian, pero por suerte y no por corrección:** los Sharpes
de B0–B5 son NEGATIVOS (−5,4 a −8,0), así que el DSR es 0,0 en cualquier
unidad, y `sr0` es invariante (V_p = V/252 ⇒ sr0_p = sr0/√252). V5 estaba
mal calibrado en la dirección PERMISIVA para cualquier retador futuro con
Sharpe positivo. Corregido en `backtest/veredicto_51.py` (el productor
entrega el Sharpe por período); test en `tests/test_unidades_sharpe.py`.
