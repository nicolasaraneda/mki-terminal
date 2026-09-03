# El juez lineal bajo D3 — ¿los features disponibles traen magnitud? (novena corrida, 3-sep-2026)

> **PROPUESTA — juez lineal bajo D3, novena corrida; pendiente de dictamen del estadistico-adversario.** No es el veredicto 5.1. Pre-registro: `GEMELO/preregistro/juez_lineal_d3.md`. Generado 2026-09-03T16:50:45.515415+00:00.

- Filas selladas evaluadas: **262** en **37 días** (corte `2026-09-02`, `excluir_cero`, regla de deduplicación firmada). Panel de entrenamiento: 15027 filas; embargo 5 d; series descartadas por cobertura: [].
- Predichas por configuración: {'C1': 254, 'C2': 79, 'CAMPEON': 262}. α elegidos: {'C1': [100.0], 'C2': [100.0]}.
- Intentos del DSR: **36 declarados antes de correr**; registro al correr 352 → 388.
- Unidad: el día. IC95 por t de clúster (gl = k−1); p por permutación de signo de la suma diaria. «Supera» = IC excluye el cero Y p < 0,05.

## ventana sellada completa

### Cada modelo contra su vara de D3 (MAE contra predecir cero; CRPS contra la climatología causal; dirección contra «siempre al alza», secundaria)

| modelo | n · días | MAE modelo / cero (pp) | ganancia MAE (pp) | CRPS modelo / clim | ganancia CRPS | dirección (pp, ×100) |
|---|---|---|---|---|---|---|
| **C1** | 254 · 36 | 2.551 / 2.938 | +0.387 [+0.049, +0.725] · p día 0.021 · **SUPERA** | 1.995 / 2.295 | +0.300 [+0.007, +0.593] · p día 0.038 · **SUPERA** | +13.8 [-3.4, +30.9] · p día 0.120 · no supera |
| **C2** | 79 · 11 | 2.359 / 3.024 | +0.664 [+0.283, +1.046] · p día 0.007 · **SUPERA** | 1.839 / 2.295 | +0.455 [+0.116, +0.795] · p día 0.018 · **SUPERA** | +25.3 [-9.5, +60.2] · p día 0.190 · no supera |
| **CAMPEON** | 262 · 37 | 2.438 / 2.892 | +0.455 [-0.045, +0.954] · p día 0.075 · no supera | 1.842 / 2.253 | +0.411 [-0.038, +0.861] · p día 0.067 · no supera | +11.8 [-5.2, +28.9] · p día 0.177 · no supera |
| **CAMPEON@C1** | 254 · 36 | 2.380 / 2.938 | +0.558 [+0.089, +1.027] · p día 0.021 · **SUPERA** | 1.814 / 2.295 | +0.481 [+0.041, +0.922] · p día 0.024 · **SUPERA** | +13.8 [-3.4, +30.9] · p día 0.127 · no supera |
| **CAMPEON@C2** | 79 · 11 | 2.390 / 3.024 | +0.634 [-0.138, +1.406] · p día 0.098 · no supera | 1.666 / 2.295 | +0.629 [+0.025, +1.232] · p día 0.043 · **SUPERA** | +22.8 [-13.4, +59.0] · p día 0.250 · no supera |

### Pareadas sobre las filas que ambos predijeron (positivo = el primero mejor)

| par | n · días | Δ ganancia MAE (pp) | Δ ganancia CRPS | Δ dirección (pp) |
|---|---|---|---|---|
| **C2 - C1** | 79 · 11 | +0.200 [-0.088, +0.488] · p día 0.166 · no supera | +0.115 [-0.139, +0.368] · p día 0.358 · no supera | +2.5 [-3.0, +8.1] · p día 1.000 · no supera |
| **C1 - CAMPEON** | 254 · 36 | -0.171 [-0.375, +0.033] · p día 0.100 · no supera | -0.181 [-0.385, +0.023] · p día 0.076 · no supera | +0.0 [-9.2, +9.2] · p día 1.000 · no supera |
| **C2 - CAMPEON** | 79 · 11 | +0.030 [-0.450, +0.510] · p día 0.863 · no supera | -0.173 [-0.528, +0.182] · p día 0.302 · no supera | +2.5 [-3.0, +8.1] · p día 1.000 · no supera |

## R2: sin emisiones 2026-07-15..2026-07-23

### Cada modelo contra su vara de D3 (MAE contra predecir cero; CRPS contra la climatología causal; dirección contra «siempre al alza», secundaria)

| modelo | n · días | MAE modelo / cero (pp) | ganancia MAE (pp) | CRPS modelo / clim | ganancia CRPS | dirección (pp, ×100) |
|---|---|---|---|---|---|---|
| **C1** | 210 · 30 | 2.577 / 2.913 | +0.335 [-0.055, +0.726] · p día 0.093 · no supera | 2.036 / 2.281 | +0.245 [-0.094, +0.583] · p día 0.163 · no supera | +8.1 [-9.9, +26.1] · p día 0.396 · no supera |
| **C2** | 35 · 5 | 2.384 / 2.978 | +0.594 [-0.293, +1.481] · p día 0.178 · no supera | 1.884 / 2.206 | +0.323 [-0.402, +1.047] · p día 0.302 · no supera | +0.0 [-50.2, +50.2] · p día 1.000 · no supera |
| **CAMPEON** | 218 · 31 | 2.486 / 2.858 | +0.372 [-0.211, +0.955] · p día 0.198 · no supera | 1.900 / 2.231 | +0.330 [-0.194, +0.855] · p día 0.207 · no supera | +6.0 [-11.8, +23.8] · p día 0.535 · no supera |
| **CAMPEON@C1** | 210 · 30 | 2.418 / 2.913 | +0.494 [-0.054, +1.042] · p día 0.076 · no supera | 1.869 / 2.281 | +0.412 [-0.105, +0.929] · p día 0.114 · no supera | +8.1 [-9.9, +26.1] · p día 0.398 · no supera |
| **CAMPEON@C2** | 35 · 5 | 2.631 / 2.978 | +0.346 [-1.385, +2.078] · p día 0.618 · no supera | 1.808 / 2.206 | +0.398 [-0.842, +1.639] · p día 0.490 · no supera | +0.0 [-50.2, +50.2] · p día 1.000 · no supera |

### Pareadas sobre las filas que ambos predijeron (positivo = el primero mejor)

| par | n · días | Δ ganancia MAE (pp) | Δ ganancia CRPS | Δ dirección (pp) |
|---|---|---|---|---|
| **C2 - C1** | 35 · 5 | +0.341 [-0.203, +0.886] · p día 0.175 · no supera | +0.263 [-0.207, +0.734] · p día 0.175 · no supera | +0.0 [+0.0, +0.0] · p día 1.000 · no supera |
| **C1 - CAMPEON** | 210 · 30 | -0.159 [-0.397, +0.079] · p día 0.192 · no supera | -0.167 [-0.407, +0.073] · p día 0.165 · no supera | +0.0 [-11.2, +11.2] · p día 1.000 · no supera |
| **C2 - CAMPEON** | 35 · 5 | +0.248 [-0.674, +1.169] · p día 0.750 · no supera | -0.075 [-0.667, +0.516] · p día 0.678 · no supera | +0.0 [+0.0, +0.0] · p día 1.000 · no supera |

## Lectura (pre-registro §6; redacción exigida por el dictamen del adversario, 3-sep 12:49)

Sobre 262 filas / 37 días, **C1 supera a predecir cero en la ventana completa** (MAE +0.387 [+0.049, +0.725] · p día 0.021 · **SUPERA**) **pero la ventaja NO sobrevive a R2** (criterio congelado: MAE +0.335 [-0.055, +0.726] · p día 0.093 · no supera); **no supera al campeón sobre las mismas filas** (C1 − campeón, MAE -0.171 [-0.375, +0.033] · p día 0.100 · no supera: contiene el cero, punto a favor del campeón), y **sobre esas mismas 254 filas el campeón supera a cero más que C1** (campeón@C1: MAE +0.558 [+0.089, +1.027] · p día 0.021 · **SUPERA**; la celda del campeón sobre sus 262 filas —MAE +0.455 [-0.045, +0.954] · p día 0.075 · no supera— no es comparable con la de C1: las 8 filas que C1 no predice son el domingo 5-jul, donde el campeón perdió contra cero). La información extra (C2 − C1, 79 filas / 11 días) no trae magnitud detectable en ningún sentido: potencia nula, no ausencia. **Conclusión honesta:** los features disponibles no traen señal de magnitud detectable con esta ventana que sea distinta de la que ya porta SOX(t, t−1) ni robusta a R2. C1 agrupada emite una sola predicción por día (signo del SOX con magnitud encogida por la ridge, α = 100): por eso C1 − campeón en dirección es 0,000 exacto. La potencia de magnitud al efecto observado es 0,86 [0,83, 0,89] el 25-oct (`espera_firma` §29); ninguna fecha se afirma. Este juez es EXPLORATORIO (V1-bis sin firma; endpoint elegido tras ver la ventana; sin hash de commit anterior a la corrida) y no computa como evidencia de R1.

## Lo que este diseño no puede decir (pre-registro §7)

Un solo régimen sellado; el campeón está en muestra (sus β se estimaron sobre esta misma historia); la climatología causal es agrupada (no por ticker; el adversario midió que sesga A FAVOR de los modelos por +0,012 [+0,000, +0,023] de CRPS, sin cambiar ninguna celda); la normal subestima colas (CRPS = cota optimista para todos por igual). ICC/DEFF por celda en el JSON; un DEFF < 1 (p. ej. C2 − C1 en dirección) es un ICC negativo con pocos clústeres, no un error. Embargo en días calendario. CSV por fila en `corrida09/juez_lineal_d3_filas_*.csv`.


## Dictamen del `estadistico-adversario` (3-sep-2026, 12:49 Chile), pegado sin editar salvo formato

**VEREDICTO:** cifras del informe **SOSTIENEN** (las 36 celdas reproducen al 4.º decimal recomputando por fila desde caché + `senales.db` en mode=ro; CRPS por fila contra `evaluacion.crps_normal` |dif| máx 3,6e-15); la lectura «C1 supera a cero y el campeón no» **NO SOSTIENE**; la pregunta de fondo (¿traen magnitud los features?) **NO CONCLUYENTE**, con R2 activada contra C1.

**(1) Lectura ilegítima.** C1 (254 filas) y el campeón (262) no están sobre las mismas filas: las 8 que C1 no predice son el domingo 5-jul (snapshot manual 10:06 UTC, SOX ffill del 2-jul por feriado del 3-jul; predicciones −4,9…−0,4 con gaps +1…+3,4): ahí el campeón perdió −2,84 pp/fila contra cero. Sobre las **mismas 254 filas** el campeón SUPERA: MAE +0,558 [+0,089, +1,027] p 0,021; CRPS +0,481 [+0,041, +0,922] p 0,024 — más que C1. Un día flipa la celda (37 días, ICC 0,5–0,6, ~55 obs. efectivas). Anchura: sobre filas comunes la razón de IC es ≈1,25×, proporcional a la amplitud (sd de la predicción 1,85 vs 1,48: la ridge con α = 100 encoge; correlación diaria 0,87). C1 agrupada emite **una sola predicción por día**: «signo del SOX con magnitud encogida»; por eso C1 − campeón en dirección es 0,000 exacto con ICC 1,0. La única comparación legítima es la pareada: −0,171 [−0,375, +0,033] p 0,10 (contiene el cero; punto a favor del campeón). Contraste con `evaluacion.block_bootstrap` sobre medias diarias (bloque 5, 10.000): C1 +0,341 [+0,073, +0,605]; C1 − campeón −0,203 [−0,345, −0,044] — sensibilidad, no decide; no hay estimador bajo el cual C1 sea mejor que el campeón.

**(2)** Conjunción «IC t de clúster excluye el cero Y p de día < 0,05» = §4 literal; clave del día = fecha de emisión; R2 por fecha de emisión inclusiva. Correcto.

**(3) R2 cambia la conclusión:** C1 pasa a +0,335 [−0,055, +0,726] p 0,094 (MAE) y +0,245 [−0,094, +0,583] p 0,163 (CRPS): su ganancia vive en la misma ventana que la del campeón. Conclusión honesta del §6: la de la sección «Lectura» de arriba. No afirmar «efecto por debajo/encima del MDE»: no son ordenables.

**(4)** La climatología agrupada sesga A FAVOR de los modelos, y poco: CRPS(clim agrupada) − CRPS(clim por ticker) = +0,0115 [+0,0004, +0,0226] p 0,039; campeón vs clim por ticker +0,400 [−0,046, +0,847] (vs +0,411). Ninguna celda cambia. La σ sellada del campeón (mediana 4,17) es 2,1× la sd climatológica: su CRPS está castigado por el intervalo ancho (V3 92,9 %).

**(5) EXPLORATORIO: correcto, por tres razones:** V1-bis sin firma (circularidad con R1); endpoint elegido tras ver la ventana (declarado); y **no existe hash de commit anterior a la corrida** (pre-registro y script untracked; mtimes 12:43:38 POSTERIORES al JSON de 12:42:00). Las horas de la bitácora (12:52/12:58/13:00) no salieron del reloj: corregidas por errata. Lo que sí puede leerse como exploratorio: (a) C1 y el campeón tienen el mismo signo fila a fila (ICC 1,0); (b) la ganancia de magnitud de ambos se concentra en 15–23 jul; (c) C2 − C1 sobre 11 días no dice nada en ningún sentido.

**(6) Intentos:** 310 al correr = 286 + 24 tramos posteriores; 346 con JUEZ-3b (36, condicionado a que no haya existido corrida anterior a la enmienda: declarado en el pre-registro §Trazabilidad: ninguna). **Este dictamen suma +6** (ADV-3b) → 352.

**CAMBIOS EXIGIDOS, aplicados en esta regeneración (mismo código de hipótesis y semilla; reproduce las 36 celdas):** (i) lectura retirada; celda campeón@C1 al lado; pareada como única comparación. (ii) commit de pre-registro + script + test antes de cualquier re-corrida; horas reemplazadas por `generado_utc` y mtimes; declarado qué cambió a las 12:43:38. (iii) DIR ×100. (iv) `allow_nan=False`; nota sobre DEFF < 1. (v) +6 ADV-3b y la declaración. (vi) CSV por fila en `corrida09/`.

**CRITERIOS (retador = C1, exploratorio):** V1 +13,8 pp [−3,4, +30,9] p 0,12 → NO PASA · V2 CRPS vs campeón −0,181 [−0,385, +0,023] → NO PASA · V3 NO EVALUABLE (C1 sin cobertura computada) · V4 2,551 vs 2,438 sobre 254 filas → NO PASA · V5 NO EVALUABLE (< 60 días) · V6, V7 NO EVALUABLE · R1 pareada contiene el cero, punto a favor del campeón → NO SE ACTIVA (no cuenta hasta V1-bis firmada) · **R2 SE ACTIVA sobre C1** · R3 la fuga del 1-sep corregida antes de correr; trazabilidad temporal no verificable → NO SE ACTIVA, con reserva.
