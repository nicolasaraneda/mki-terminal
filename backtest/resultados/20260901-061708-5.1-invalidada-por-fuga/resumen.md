# ⛔ CORRIDA **INVALIDADA POR FUGA** — NO es el veredicto de la Etapa 5.1

**R3 de `GEMELO/DISEÑO.md` §6.2 dice: *«cualquier fuga detectada por el test de causalidad. Sin discusión y sin excepción»*. Se detectaron fugas DEMOSTRADAS y medidas en el arnés antes de correr. Ninguna cifra de este documento puede citarse como resultado del backtest:**

- **B-1 · el sentimiento usa juicios de IA que no existían.** `backtest/datos.py` corta por `titulares.fecha` (publicación) y **nunca mira `analisis.analizado_en`**. Medido sobre `noticias.db` en `mode=ro`: **3407 de 5094 análisis (66.9%)** se produjeron después de las 22:15 UTC del día de publicación; rezago máximo **320 días**; y el **primer análisis de IA que existe en el sistema es del 2026-07-04**, mientras los titulares arrancan el 2025-09-09. En la ventana declarada, casi 22 de 24 meses alimentan B4 y B5 con sentimiento construido con juicios que no existían el día de la emisión. El `grado B` lo declara pero **ninguna métrica lo excluye**, y `buzz` sale del mismo join sin grado ninguno.
- **B-2 · la guarda `ErrorLookAhead` es tautológica.** `backtest/baselines.py:182-184` y `:314-315` validan un frame que acaban de recortar con el MISMO predicado (`index.date <= fecha`), así que la condición de disparo es inalcanzable por construcción. Medido: **401.184 invocaciones en un walk-forward, cero capaces de disparar.** Y una fuga real (`shift(-1)`) desplaza VALORES, no el índice: la guarda no la ve. La prueba maestra `test_truncar_futuro_no_cambia_predicciones` cubre **una fecha y tres baselines**, así que una fuga en las cinco features exclusivas de B4/B5 es invisible para toda la suite.
- **B-3 · el mismo desenlace cuenta hasta 8 veces.** Varias emisiones consecutivas apuntan a la MISMA sesión objetivo en feriados largos y `motorbt` escribe una fila por emisión con el outcome repetido. Medido sobre la ventana declarada: **263 de 4160 filas (6.3%) son desenlaces duplicados**, con dos pares contados **8 veces** (`2330.TW` 2025-02-03 y 2026-02-23). Contamina el rank IC diario, la n de Wilson y los retornos de cartera; y `t_newey_west` usa **lag 5**, que no cubre un bloque de 8 duplicados perfectos: el t-stat del veredicto escalonado sale inflado.

Los números que siguen se publican **sólo** como evidencia de que la maquinaria corre punta a punta y como referencia para dimensionar la contaminación. **No son un veredicto y no aprueban ni reprueban ningún criterio.**

Estado del gatillo congelado (`backtest/DISEÑO.md` §11):

- **(a)** N ≥ 150 verificaciones limpias **Y** un cambio de régimen del SOX: 261 verificaciones limpias — CUMPLE la primera mitad —, pero el track record tiene **una sola etiqueta de régimen** (`Alcista · vol alta`, 38 snapshots, más 2 nulos). La conjunción **NO se cumple**.
- **(b)** 3 meses continuos desde el 25-jul-2026: faltan **54 días** (cae el 25-oct-2026). **NO se cumple**.

**El holdout en cuarentena NO se evaluó y queda INTACTO.** `GEMELO/DISEÑO.md` §6.1 V7 lo define como *evaluado una sola vez*: es un recurso irreversible y gastarlo con el gatillo sin cumplir lo quemaría para siempre. V7 queda NO EVALUABLE por esta razón, no por falta de maquinaria.

Expediente de la decisión pendiente: `GEMELO/resultados/gatillo_51.md`.

# Backtest MKI — 5.1-invalidada-por-fuga · 2024-09-02 → 2026-08-28

Generado 2026-09-01T06:17:08.744200+00:00 · commit bc35371 · descartes sin datos: 9

Parámetros: embargo 5 días · ventana entrenamiento 250 · reajuste cada 7 días

Bootstrap: circular de bloques (Politis & Romano 1994) · bloque 10 días · 2000 réplicas · semilla 20260901 · IC 95%


## Baselines

| B | n | %grado B | IC medio | t(NW) | MAE gap | Sharpe LS 25pb [IC95] | acum. LS 25pb |
|---|---|---|---|---|---|---|---|
| B0 | 4151 | 0.0% | 0.0 | nan | 1.847 | -5.44 [-7.00, -3.93] | -91.4% |
| B1 | 4151 | 0.0% | -0.0313 | -1.48 | 1.847 | -6.02 [-7.51, -4.65] | -92.3% |
| B2 | 4151 | 0.0% | 0.2328 | 11.21 | 1.543 | -6.98 [-8.38, -5.74] | -95.6% |
| B3 | 4151 | 0.0% | 0.2221 | 9.77 | 1.562 | -7.99 [-9.30, -6.77] | -96.8% |
| B4 | 4151 | 93.9% | 0.2213 | 9.92 | 1.575 | -8.08 [-9.54, -6.82] | -96.3% |
| B5 | 4151 | 93.9% | 0.2026 | 8.79 | 1.576 | -7.67 [-9.08, -6.46] | -95.6% |

**Benchmark obligatorio — comprar SMH y no hacer nada**: acumulado 137.1% · Sharpe 1.32 · MDD -32.6% — toda cartera se lee CONTRA esta línea (ajuste GATE B).


## Veredicto escalonado (capa vs capa)

| Capa | ΔIC | t(NW) | días | veredicto |
|---|---|---|---|---|
| B1 vs B0 | -0.0313 | -1.48 | 520 | no demostrado |
| B2 vs B1 | 0.2642 | 8.69 | 520 | aporta |
| B3 vs B2 | -0.0108 | -0.8 | 520 | no demostrado |
| B4 vs B3 | -0.0008 | -0.17 | 520 | no demostrado |
| B5 vs B4 | -0.0187 | -2.79 | 520 | no demostrado |

## Auditoría B2 vs sellos reales
260 predicciones comparadas · diferencia media 0.166 pp · máx 5.3 pp. las diferencias reflejan deriva de datos de la fuente entre el sello y hoy (hallazgo 4.7.1), no necesariamente un bug.


---
Herramienta de análisis — no constituye asesoría financiera. Diseño congelado en backtest/DISEÑO.md.


---

# Veredicto de la Etapa 5.1 — B0→B5

## ⛔ NO HAY VEREDICTO. R3 lo impide, y R3 no admite excepciones.

`GEMELO/DISEÑO.md` §6.2 **R3**: *«cualquier fuga detectada por el test de causalidad. Sin discusión y sin excepción.»* Se detectaron **tres** defectos demostrados y medidos en el arnés, uno de ellos una fuga temporal de manual. **El veredicto de la Etapa 5.1 espera** a que el arnés se arregle.

Además, el gatillo congelado del GATE B **no está cumplido por ninguna de sus dos vías** (`backtest/DISEÑO.md` §11), y el **holdout NO se gastó**. Expediente completo, con el conteo de intentos declarado antes de correr: `GEMELO/resultados/gatillo_51.md`.

## Tabla de criterios

| Criterio | Veredicto | Razón |
|---|---|---|
| **V1** | PASA (SOBRE DATOS CON FUGA — no vale) | Habilidad sobre 'siempre al alza' — cifra contaminada, ver abajo |
| **V2** | PASA (SOBRE DATOS CON FUGA — no vale) | CRPS vs el campeón — cifra contaminada |
| **V3** | PASA (SOBRE DATOS CON FUGA — no vale) | Cobertura del intervalo 80% — cifra contaminada |
| **V4** | NO PASA (SOBRE DATOS CON FUGA — no vale) | MAE del gap vs el campeón en ventana |
| **V5** | NO PASA (SOBRE DATOS CON FUGA — no vale) | DSR ≥ 0.95 con N declarado = 82 |
| **V6** | NO PASA (SOBRE DATOS CON FUGA — no vale) | Superar comprar SMH y no hacer nada, a 25 pb por lado |
| **V7** | NO EVALUABLE | Holdout en cuarentena — **deliberadamente NO gastado** |
| **R1** | NO EVALUABLE | Control lineal vs retador — no hay retador en esta corrida |
| **R2** | PASA | La ventaja sobrevive excluyendo 15–23 jul |
| **R3** | NO PASA | **Fuga detectada. Sin discusión y sin excepción.** |
| **veredicto_final_diseno_8** | NO AGREGA VALOR | El criterio de lectura del §8 |

## V6 — el benchmark obligatorio, y no está cerca

**Comprar SMH y no hacer nada: 137.1% acumulado, Sharpe 1.32, MDD -32.6%.**

| B | LS 10 pb | LS 25 pb | LS 50 pb | LO 25 pb | Sharpe LS 25 pb |
|---|---|---|---|---|---|
| B0 | -58.8% | **-91.4%** | -99.4% | -90.1% | -5.44 |
| B1 | -63.3% | **-92.3%** | -99.4% | -91.3% | -6.02 |
| B2 | -79.1% | **-95.6%** | -99.7% | -94.1% | -6.98 |
| B3 | -84.6% | **-96.8%** | -99.8% | -94.9% | -7.99 |
| B4 | -82.4% | **-96.3%** | -99.7% | -93.9% | -8.08 |
| B5 | -78.9% | **-95.6%** | -99.7% | -92.4% | -7.67 |

**Ninguna cartera, en ningún nivel de costos, en ningún lado, se acerca al benchmark.** El diseño ya lo había anticipado con *«una estrategia que sólo vive con 10 pb no aprueba»*: aquí no vive ninguna ni con 10 pb.

## V5 — Deflated Sharpe: cero, y el conteo de intentos no era el problema

| B | Sharpe LS 25 pb | días | skew | curtosis | PSR vs 0 | DSR N=26 | DSR N=44 | **DSR N=82** | DSR N=110 |
|---|---|---|---|---|---|---|---|---|---|
| B0 | -5.436 | 520 | -0.421 | 4.68 | 0.0 | 0.0 | 0.0 | **0.0** | 0.0 |
| B1 | -6.024 | 520 | -0.27 | 5.387 | 0.0 | 0.0 | 0.0 | **0.0** | 0.0 |
| B2 | -6.979 | 520 | -0.427 | 5.729 | 0.0 | 0.0 | 0.0 | **0.0** | 0.0 |
| B3 | -7.995 | 520 | -0.355 | 4.496 | 0.0 | 0.0 | 0.0 | **0.0** | 0.0 |
| B4 | -8.081 | 520 | -0.196 | 4.245 | 0.0 | 0.0 | 0.0 | **0.0** | 0.0 |
| B5 | -7.669 | 520 | -0.109 | 4.206 | 0.0 | 0.0 | 0.0 | **0.0** | 0.0 |

`V_intentos` = 1.1997 · umbral deflactado `SR0` = 2.6944 a N=82.

Los 520 días superan el mínimo de 60, así que el DSR **sí es interpretable** aquí — no hay que escribir NO INTERPRETABLE. Y lo que dice es **0.0000 en las seis baselines y en los cuatro valores de N**. Conviene decirlo sin adornos: **el conteo de intentos, que este expediente se tomó el trabajo de reconstruir desde 25 hasta 82, resultó no ser la restricción que decide.** Con Sharpe entre −5.4 y −8.1, ningún N habría cambiado el resultado. El conteo se declaró igual y antes de correr, porque su valor no depende de que termine siendo decisivo.

## Lo que sí se aprende, incluso con el arnés roto

Hay una asimetría que conviene mirar, porque la contaminación conocida va en la dirección de **favorecer** al modelo y aun así el resultado económico es demoledor:

| | |
|---|---|
| Acierto direccional del gap (B2) | **68.97%** (Wilson95 [67.54, 70.37]) vs base 55.43%, ventaja **13.55 pp**, McNemar p=0.0 |
| Cartera long-short **bruta, sin un solo punto básico de costo** | **−40.7 %** acumulado, Sharpe **−1.08** |
| Cartera long-only bruta | −19.8 % acumulado, Sharpe −0.24 |
| Arrastre puro de costos a 25 pb/lado sobre 520 días | −92.6 % |

**El modelo acierta la dirección del gap y aun así la cartera pierde el 41 % antes de costos.** No es un problema de costos: los costos rematan algo que ya venía perdiendo. Es la distinción que el propio proyecto tiene escrita desde la Etapa 4.6 —¿la señal EXISTE? ¿es CAPTURABLE?— medida ahora sobre dos años: **el gap existe y no es capturable.** Comprar en la subasta de apertura ya es tarde; el gap ocurrió antes de que se pudiera operar.

Esto no es un veredicto, porque R3 lo prohíbe. Pero es la dirección en la que el arreglo del arnés tendrá que ser sorprendente para cambiar algo.

## B-3 medido: y la contaminación va al revés de lo que supuse

Releyendo las MISMAS filas con los desenlaces duplicados colapsados por `(ticker, sesión objetivo)`:

| B | filas | ventaja pp | IC medio | t(NW) | MAE |
|---|---|---|---|---|---|
| B0 | 4151 → 3888 | — → — | 0.0 → 0.0 | nan → nan | 1.847 → 1.784 |
| B1 | 4151 → 3888 | -1.9 → -1.78 | -0.0313 → -0.0399 | -1.48 → -1.91 | 1.847 → 1.784 |
| B2 | 4151 → 3888 | 13.55 → 14.29 | 0.2328 → 0.2457 | 11.21 → 11.65 | 1.543 → 1.47 |
| B3 | 4151 → 3888 | 12.96 → 13.53 | 0.2221 → 0.2436 | 9.77 → 11.03 | 1.562 → 1.486 |
| B4 | 4151 → 3888 | 12.19 → 12.83 | 0.2213 → 0.2403 | 9.92 → 10.93 | 1.575 → 1.495 |
| B5 | 4151 → 3888 | 12.33 → 12.96 | 0.2026 → 0.2244 | 8.79 → 10.05 | 1.576 → 1.496 |

**La auditoría predijo que los duplicados INFLABAN el t-stat. Medido, hacen lo contrario:** al deduplicar, la ventaja sube, el IC sube y el t(NW) sube en todas las capas. El defecto es real —la unidad de observación está mal y hay que arreglarla igual—, pero su dirección no era la que supuse, y decirlo es parte del trabajo. Corregir el arnés no va a rescatar estos números: va a empeorarlos un poco más del lado económico.

## La fuente no es point-in-time, y esta vez está medido

`B2` contra las predicciones realmente selladas por producción, 260 filas: diferencia mediana **0.03 pp**, media **0.1656 pp**, máxima **5.3 pp**. Toda la discrepancia vive en una sola fecha, **2026-08-28** (media 3.6186 pp); sin ella, la media cae a **0.07 pp** y el máximo a 0.61 pp.

La causa, verificada contra la fuente: **Yahoo borró la sesión del 2026-08-28 de `^SOX`, `SMH` y `^GSPC`** (`NVDA` sí la tiene). Producción la vivió y la selló —`sox_fecha` 2026-08-28, `sox_usado_pct` −3.47—; hoy esa barra no existe y el backtest reconstruye ese día con el SOX del 27 (+2.33 %), **invirtiendo el signo de las ocho acciones**. La barra desaparecida es también la del **benchmark obligatorio SMH**.

Es la primera vez que la limitación *«esto no es point-in-time»* se mide sobre el camino del backtest, y su magnitud no es un decimal: da vuelta una sección transversal entera.

---

## Qué hay que arreglar antes de que exista un veredicto

En este orden, y el primer entregable de cada punto es el **test**, no el arreglo. Ver §3.10 del expediente.

1. **B-1** — cortar el sentimiento por `min(titulares.fecha, analisis.analizado_en)` contra el instante de emisión. Hoy `buzz` no tiene grado ninguno.
2. **B-2** — parametrizar la prueba maestra sobre **B0–B5 × ≥10 fechas** y añadir la contraprueba `shift(-1)` como test permanente: que el test pueda fallar es parte del test.
3. **B-3** — deduplicar por `(ticker, sesión objetivo)` o declarar la sesión objetivo como unidad de observación.
4. **S-1** — contar sesiones del calendario, no días corridos, y sellar las efectivamente purgadas.
5. **S-3** — computar `estado_gatillo` en vez de recibirlo.
6. Construir un **holdout material**: hoy la cuarentena es sólo procedimental.

---
Herramienta de análisis — no constituye asesoría financiera. Criterios congelados en `backtest/DISEÑO.md` §8 y `GEMELO/DISEÑO.md` §6; ninguno fue modificado para esta corrida.
