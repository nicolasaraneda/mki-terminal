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
