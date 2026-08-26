# Línea base del campeón 4.6.0 — reproducción de la §2

- Generado: 2026-08-26T01:34:14.996811+00:00
- Fuente: `senales.db` en `mode=ro` (autoridad), NO los CSV de respaldo
- Convención de empate: **excluir_cero**
- Filas: **n = 223** · 2026-07-05 → 2026-08-21

## Las tres convenciones de empate, juntas

Hay 5 filas con `gap_pct == 0.0` exacto (apertura idéntica al cierre
previo: la firma del ffill de feriados; 4 de las 5 son 2330.TW). El
verificador puntúa al campeón con `>=` y le da el acierto; la
baseline original de la §2.1 usaba `>` y no se lo daba — dos reglas
distintas para los dos lados. La §2.8 congeló `excluir_cero`; las
tres se muestran igual, porque la elección debe quedar a la vista:

| convencion | n | modelo_pct | base_pct | ventaja_pp | mcnemar | p |
|---|---|---|---|---|---|---|
| estricta | 228 | 65.8 | 60.5 | 5.3 | 67 vs 55 | 0.3193 |
| verificador | 228 | 65.8 | 62.7 | 3.1 | 64 vs 57 | 0.5854 |
| excluir_cero | 223 | 65.9 | 61.9 | 4.0 | 64 vs 55 | 0.4633 |


## Línea base OFICIAL (§2.8, congelada)

Convención congelada: **`excluir_cero`** — las filas con `gap_pct == 0.00` se excluyen de ambos lados (artefactos del ffill de feriados). La exclusión vive en esta capa de medición; `senales.py` no se toca.

| campo | congelado (§2.8) | harness | veredicto |
|---|---|---|---|
| n | 223.0 | 223.0 | coincide |
| modelo: acierto % | 65.9 | 65.9 | coincide |
| baseline: acierto % | 61.9 | 61.9 | coincide |
| ventaja pp | 4.0 | 4.0 | coincide |
| McNemar b01 | 64.0 | 64.0 | coincide |
| McNemar b10 | 55.0 | 55.0 | coincide |
| McNemar p | 0.4633 | 0.4633 | coincide |


## Contraste con el pre-registro original (§2, convención `estricta`)

**21 de 21 afirmaciones reproducen.** Se evalúan bajo `estricta` porque es la convención con que se escribieron; la §2.8 las corrige, no las desmiente.

| afirmación | documento | harness | veredicto |
|---|---|---|---|
| n (verificaciones 4.6.0) | 228.0 | 228.0 | reproduce |
| modelo: aciertos | 150.0 | 150.0 | reproduce |
| modelo: acierto de gap % | 65.8 | 65.8 | reproduce |
| baseline: aciertos | 138.0 | 138.0 | reproduce |
| baseline: acierto de gap % | 60.5 | 60.5 | reproduce |
| ventaja pp | 5.3 | 5.3 | reproduce |
| McNemar b01 | 67.0 | 67.0 | reproduce |
| McNemar b10 | 55.0 | 55.0 | reproduce |
| McNemar p | 0.3193 | 0.3193 | reproduce |
| MAE modelo | 3.064 | 3.0636 | reproduce |
| MAE predecir 0.0 | 3.423 | 3.4227 | reproduce |
| MAE predecir la media | 3.395 | 3.3951 | reproduce |
| cobertura del intervalo 80% | 89.5 | 89.5 | reproduce |
| ratio ancho/error | 1.77 | 1.77 | reproduce |
| R² sellado medio | 0.1635 | 0.1635 | reproduce |
| zona muerta 0.25: n | 184.0 | 184.0 | reproduce |
| zona muerta 0.25: ventaja pp | 8.2 | 8.2 | reproduce |
| etiquetas de régimen distintas | 1.0 | 1.0 | reproduce |
| snapshots sellados | 35.0 | 35.0 | reproduce |
| |Δβ| medio | 0.043 | 0.0427 | reproduce |
| |Δβ| como % del nivel | 8.0 | 7.8 | reproduce |

## §2.1 — El edge real

| | Acierto de gap | IC95 Wilson |
|---|---|---|
| Modelo 4.6.0 | **65.9%** (147/223) | [59.5 – 71.8] |
| "Siempre al alza", mismas filas | **61.9%** (138/223) | [55.4 – 68.0] |
| **Ventaja** | **+4.0 pp** | — |

McNemar sobre los desacuerdos: el modelo acierta donde la baseline
falla **64** veces; la baseline donde el modelo falla
**55**. **p = 0.4633** (chi-cuadrado con corrección de continuidad).

## §2.2 — Dónde está la ventaja, en el tiempo

| bloque | desde | hasta | n | modelo_pct | base_pct | ventaja_pp |
|---|---|---|---|---|---|---|
| 0 | 2026-07-05 | 2026-07-15 | 40 | 77.5 | 65.0 | 12.5 |
| 1 | 2026-07-15 | 2026-07-24 | 40 | 77.5 | 47.5 | 30.0 |
| 2 | 2026-07-24 | 2026-07-31 | 40 | 57.5 | 60.0 | -2.5 |
| 3 | 2026-07-31 | 2026-08-10 | 40 | 65.0 | 77.5 | -12.5 |
| 4 | 2026-08-10 | 2026-08-18 | 40 | 70.0 | 70.0 | 0.0 |
| 5 | 2026-08-18 | 2026-08-21 | 23 | 34.8 | 43.5 | -8.7 |

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
| 5 | límites | 2026-08-18→2026-08-21 n=28 | 2026-08-18→2026-08-21 n=23 | NO REPRODUCE |
| 5 | modelo % | 42.9 | 34.8 | NO REPRODUCE |
| 5 | base % | 32.1 | 43.5 | NO REPRODUCE |

### R2 de la §6.2, operacionalizado por fechas

R2 descarta al retador si su ventaja desaparece al excluir el bloque 1 (2026-07-15–2026-07-23). El ÍNDICE de bloque depende del orden de las filas; el RANGO DE FECHAS no, así que la regla solo es aplicable por fechas. Al propio campeón, esa misma prueba le da:

- Sin la ventana: n = 179, modelo 62.0%, base 67.0%, **ventaja -5.0 pp** (McNemar p = 0.3964).

## §2.4 — Zona muerta: abstenerse bajo un umbral

Cada nivel contra **su propia** baseline sobre las filas que
sobreviven — compararlo contra la baseline global cambiaría el
denominador y regalaría ventaja.

| umbral | n | modelo_pct | base_pct | ventaja_pp | mcnemar_p | descartado_pct |
|---|---|---|---|---|---|---|
| 0.0 | 223.0 | 65.9 | 61.9 | 4.0 | 0.4633 | 0.0 |
| 0.15 | 202.0 | 68.8 | 62.4 | 6.4 | 0.259 | 9.0 |
| 0.25 | 183.0 | 71.0 | 63.4 | 7.7 | 0.198 | 18.0 |
| 0.3 | 179.0 | 71.5 | 64.2 | 7.3 | 0.2325 | 20.0 |
| 0.5 | 149.0 | 69.8 | 66.4 | 3.4 | 0.668 | 33.0 |
| 0.75 | 134.0 | 73.9 | 67.2 | 6.7 | 0.3619 | 40.0 |

## §2.5 — Magnitud: lo que la baseline no puede dar

| Predictor | MAE del gap |
|---|---|
| Modelo 4.6.0 | **3.1244 pp** |
| Predecir 0.0 | 3.4995 pp |
| Predecir la media histórica (1.435) | 3.4434 pp |

Mejora sobre predecir cero: **10.7%**.

## §2.6 — Cortes por bolsa

| exchange | n | modelo_pct | base_pct | ventaja_pp | r2_medio | mae |
|---|---|---|---|---|---|---|
| XTKS | 116 | 68.1 | 62.1 | 6.0 | 0.178 | 2.74 |
| XKRX | 54 | 64.8 | 68.5 | -3.7 | 0.173 | 5.3 |
| XETR | 29 | 65.5 | 55.2 | 10.3 | 0.005 | 1.9 |
| XTAI | 24 | 58.3 | 54.2 | 4.2 | 0.251 | 1.57 |

## §2.7 — Intervalos, régimen y estabilidad de β

- **Calibración:** cobertura empírica **89.2%** contra un nominal de 80.0% (n=223), ancho medio 5.49 pp frente a error absoluto medio 3.12 pp — **1.76× más anchos de lo necesario**.
- **Régimen:** **1** etiqueta(s) distinta(s) en los 35 snapshots sellados (34 con modelo 4.6.0; el de 2026-07-04 es pre-versionado, `modelo_version` NULL) → ['Alcista · vol alta']
- **R² sellado medio:** 0.1618
- **Estabilidad de β:** salto medio entre días consecutivos 0.0427 sobre un nivel medio de 0.5442 — **7.8% del nivel, por día**. Mediana 0.01; el 11.3% de los 141 pares salta más de 0.10; máximo 0.28.
