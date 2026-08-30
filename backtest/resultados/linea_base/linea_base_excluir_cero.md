# Línea base del campeón 4.6.0 — reproducción de la §2

- Generado: 2026-08-30T23:05:31.245012+00:00
- Fuente: `senales.db` en `mode=ro` (autoridad), NO los CSV de respaldo
- Convención de empate: **excluir_cero**
- Filas: **n = 248** · 2026-07-05 → 2026-08-26

## Las tres convenciones de empate, juntas

Hay 5 filas con `gap_pct == 0.0` exacto (apertura idéntica al cierre
previo: la firma del ffill de feriados; 4 de las 5 son 2330.TW). El
verificador puntúa al campeón con `>=` y le da el acierto; la
baseline original de la §2.1 usaba `>` y no se lo daba — dos reglas
distintas para los dos lados. La §2.8 congeló `excluir_cero`; las
tres se muestran igual, porque la elección debe quedar a la vista:

| convencion | n | modelo_pct | base_pct | ventaja_pp | mcnemar | p |
|---|---|---|---|---|---|---|
| estricta | 253 | 66.0 | 58.5 | 7.5 | 75 vs 56 | 0.1158 |
| verificador | 253 | 66.0 | 60.5 | 5.5 | 72 vs 58 | 0.2542 |
| excluir_cero | 248 | 66.1 | 59.7 | 6.5 | 72 vs 56 | 0.1849 |


## Línea base OFICIAL (§2.8, congelada)

Convención congelada: **`excluir_cero`** — las filas con `gap_pct == 0.00` se excluyen de ambos lados (artefactos del ffill de feriados). La exclusión vive en esta capa de medición; `senales.py` no se toca.

| campo | congelado (§2.8) | harness | veredicto |
|---|---|---|---|
| n | 223.0 | 248.0 | NO COINCIDE |
| modelo: acierto % | 65.9 | 66.1 | NO COINCIDE |
| baseline: acierto % | 61.9 | 59.7 | NO COINCIDE |
| ventaja pp | 4.0 | 6.5 | NO COINCIDE |
| McNemar b01 | 64.0 | 72.0 | NO COINCIDE |
| McNemar b10 | 55.0 | 56.0 | NO COINCIDE |
| McNemar p | 0.4633 | 0.1849 | NO COINCIDE |

> **La línea oficial ya NO coincide con lo congelado.** Eso es un hallazgo, no algo que ajustar en el documento.

## Contraste con el pre-registro original (§2, convención `estricta`)

**4 de 21 afirmaciones reproducen.** Se evalúan bajo `estricta` porque es la convención con que se escribieron; la §2.8 las corrige, no las desmiente.

| afirmación | documento | harness | veredicto |
|---|---|---|---|
| n (verificaciones 4.6.0) | 228.0 | 253.0 | NO REPRODUCE |
| modelo: aciertos | 150.0 | 167.0 | NO REPRODUCE |
| modelo: acierto de gap % | 65.8 | 66.0 | NO REPRODUCE |
| baseline: aciertos | 138.0 | 148.0 | NO REPRODUCE |
| baseline: acierto de gap % | 60.5 | 58.5 | NO REPRODUCE |
| ventaja pp | 5.3 | 7.5 | NO REPRODUCE |
| McNemar b01 | 67.0 | 75.0 | NO REPRODUCE |
| McNemar b10 | 55.0 | 56.0 | NO REPRODUCE |
| McNemar p | 0.3193 | 0.1158 | NO REPRODUCE |
| MAE modelo | 3.064 | 2.932 | NO REPRODUCE |
| MAE predecir 0.0 | 3.423 | 3.2688 | NO REPRODUCE |
| MAE predecir la media | 3.395 | 3.2718 | NO REPRODUCE |
| cobertura del intervalo 80% | 89.5 | 90.5 | NO REPRODUCE |
| ratio ancho/error | 1.77 | 1.86 | NO REPRODUCE |
| R² sellado medio | 0.1635 | 0.1641 | NO REPRODUCE |
| zona muerta 0.25: n | 184.0 | 198.0 | NO REPRODUCE |
| zona muerta 0.25: ventaja pp | 8.2 | 11.1 | NO REPRODUCE |
| etiquetas de régimen distintas | 1.0 | 1.0 | reproduce |
| snapshots sellados | 35.0 | 35.0 | reproduce |
| |Δβ| medio | 0.043 | 0.0427 | reproduce |
| |Δβ| como % del nivel | 8.0 | 7.8 | reproduce |

> Las que no reproducen son **hallazgos**. El pre-registro NO se
> edita para que cuadren: manda el harness y la corrección se
> documenta aparte, con fecha posterior (DECISIONES.md §23).

## §2.1 — El edge real

| | Acierto de gap | IC95 Wilson |
|---|---|---|
| Modelo 4.6.0 | **66.1%** (164/248) | [60.0 – 71.7] |
| "Siempre al alza", mismas filas | **59.7%** (148/248) | [53.5 – 65.6] |
| **Ventaja** | **+6.5 pp** | — |

McNemar sobre los desacuerdos: el modelo acierta donde la baseline
falla **72** veces; la baseline donde el modelo falla
**56**. **p = 0.1849** (chi-cuadrado con corrección de continuidad).

## §2.2 — Dónde está la ventaja, en el tiempo

| bloque | desde | hasta | n | modelo_pct | base_pct | ventaja_pp |
|---|---|---|---|---|---|---|
| 0 | 2026-07-05 | 2026-07-15 | 40 | 77.5 | 65.0 | 12.5 |
| 1 | 2026-07-15 | 2026-07-24 | 40 | 77.5 | 47.5 | 30.0 |
| 2 | 2026-07-24 | 2026-07-31 | 40 | 57.5 | 60.0 | -2.5 |
| 3 | 2026-07-31 | 2026-08-10 | 40 | 65.0 | 77.5 | -12.5 |
| 4 | 2026-08-10 | 2026-08-18 | 40 | 70.0 | 70.0 | 0.0 |
| 5 | 2026-08-18 | 2026-08-25 | 40 | 42.5 | 30.0 | 12.5 |
| 6 | 2026-08-26 | 2026-08-26 | 8 | 100.0 | 100.0 | 0.0 |

### Contraste bloque a bloque

4 de 18 celdas reproducen.

| bloque | campo | documento | harness | veredicto |
|---|---|---|---|---|
| 0 | límites | 2026-07-05→2026-07-15 n=40 | 2026-07-05→2026-07-15 n=40 | reproduce |
| 0 | modelo % | 75.0 | 77.5 | NO REPRODUCE |
| 0 | base % | 67.5 | 65.0 | NO REPRODUCE |
| 1 | límites | 2026-07-15→2026-07-23 n=40 | 2026-07-15→2026-07-24 n=40 | NO REPRODUCE |
| 1 | modelo % | 82.5 | 77.5 | NO REPRODUCE |
| 1 | base % | 42.5 | 47.5 | NO REPRODUCE |
| 2 | límites | 2026-07-24→2026-07-30 n=40 | 2026-07-24→2026-07-31 n=40 | NO REPRODUCE |
| 2 | modelo % | 57.5 | 57.5 | reproduce |
| 2 | base % | 62.5 | 60.0 | NO REPRODUCE |
| 3 | límites | 2026-07-31→2026-08-10 n=40 | 2026-07-31→2026-08-10 n=40 | reproduce |
| 3 | modelo % | 67.5 | 65.0 | NO REPRODUCE |
| 3 | base % | 72.5 | 77.5 | NO REPRODUCE |
| 4 | límites | 2026-08-10→2026-08-18 n=40 | 2026-08-10→2026-08-18 n=40 | reproduce |
| 4 | modelo % | 62.5 | 70.0 | NO REPRODUCE |
| 4 | base % | 77.5 | 70.0 | NO REPRODUCE |
| 5 | límites | 2026-08-18→2026-08-21 n=28 | 2026-08-18→2026-08-25 n=40 | NO REPRODUCE |
| 5 | modelo % | 42.9 | 42.5 | NO REPRODUCE |
| 5 | base % | 32.1 | 30.0 | NO REPRODUCE |

### R2 de la §6.2, operacionalizado por fechas

R2 descarta al retador si su ventaja desaparece al excluir el bloque 1 (2026-07-15–2026-07-23). El ÍNDICE de bloque depende del orden de las filas; el RANGO DE FECHAS no, así que la regla solo es aplicable por fechas. Al propio campeón, esa misma prueba le da:

- Sin la ventana: n = 204, modelo 62.7%, base 63.7%, **ventaja -1.0 pp** (McNemar p = 0.9195).

## §2.4 — Zona muerta: abstenerse bajo un umbral

Cada nivel contra **su propia** baseline sobre las filas que
sobreviven — compararlo contra la baseline global cambiaría el
denominador y regalaría ventaja.

| umbral | n | modelo_pct | base_pct | ventaja_pp | mcnemar_p | descartado_pct |
|---|---|---|---|---|---|---|
| 0.0 | 248.0 | 66.1 | 59.7 | 6.5 | 0.1849 | 0.0 |
| 0.15 | 220.0 | 67.7 | 59.1 | 8.6 | 0.1018 | 11.0 |
| 0.25 | 197.0 | 69.5 | 58.9 | 10.7 | 0.0554 | 21.0 |
| 0.3 | 193.0 | 69.9 | 59.6 | 10.4 | 0.0675 | 22.0 |
| 0.5 | 163.0 | 68.1 | 60.7 | 7.4 | 0.2566 | 34.0 |
| 0.75 | 146.0 | 72.6 | 61.6 | 11.0 | 0.1017 | 41.0 |

## §2.5 — Magnitud: lo que la baseline no puede dar

| Predictor | MAE del gap |
|---|---|
| Modelo 4.6.0 | **2.9839 pp** |
| Predecir 0.0 | 3.3347 pp |
| Predecir la media histórica (1.2868) | 3.3158 pp |

Mejora sobre predecir cero: **10.5%**.

## §2.6 — Cortes por bolsa

| exchange | n | modelo_pct | base_pct | ventaja_pp | r2_medio | mae |
|---|---|---|---|---|---|---|
| XTKS | 128 | 68.0 | 59.4 | 8.6 | 0.179 | 2.64 |
| XKRX | 60 | 65.0 | 65.0 | 0.0 | 0.174 | 5.0 |
| XETR | 33 | 66.7 | 57.6 | 9.1 | 0.005 | 1.87 |
| XTAI | 27 | 59.3 | 51.9 | 7.4 | 0.253 | 1.48 |

## §2.7 — Intervalos, régimen y estabilidad de β

- **Calibración:** cobertura empírica **90.3%** contra un nominal de 80.0% (n=248), ancho medio 5.5 pp frente a error absoluto medio 2.98 pp — **1.84× más anchos de lo necesario**.
- **Régimen:** **1** etiqueta(s) distinta(s) en los 39 snapshots sellados (38 con modelo 4.6.0; el de 2026-07-04 es pre-versionado, `modelo_version` NULL) → ['Alcista · vol alta']
- **R² sellado medio:** 0.1626
- **Estabilidad de β:** salto medio entre días consecutivos 0.0369 sobre un nivel medio de 0.5472 — **6.7% del nivel, por día**. Mediana 0.01; el 9.2% de los 173 pares salta más de 0.10; máximo 0.28.
