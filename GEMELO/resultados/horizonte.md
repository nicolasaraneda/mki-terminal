# ¿Es medible en principio? — Frente B (séptima corrida; ruta 3 añadida en la novena, 3-sep-2026)

> PROPUESTA. Desde el 3-sep-2026 la **ruta 3 (simulador calibrado)** es la que manda: el dictamen A de la octava corrida midió que la ruta 2 (δ constante sumado a cada fila) es OPTIMISTA. Las rutas 1 y 2 quedan como referencia comparada. Registro de intentos al correr: 310.

- Generado: 2026-09-03T15:36:13.572630+00:00 · `python GEMELO/SECUENCIAL/horizonte.py`
- Ancla: `hasta_sello = 2026-08-31`, `excluir_cero` → **n = 246 en 35 días** (2026-07-05 → 2026-08-27, 39 días hábiles, cadencia 0.897 sellos/día hábil)
- Ventaja 9.35 pp, IC95 de día [-7.2, 26.32] (contiene el cero), SE de día **8.55 pp** (IC95 del SE, bootstrap anidado: [5.67, 10.45]); ICC 0.3925, DEFF 3.5595, n efectivo 69.1106 → **1.97 observaciones efectivas por día sellado**
- Regímenes presentes en la ventana: ['Alcista · vol alta']

## Ruta 1 · analítica (SE ∝ 1/√días)

| efecto | días sellados (IC95) | años de sellado | fecha estimada (IC95) | potencia hoy |
|---|---|---|---|---|
| **5.0 pp** | 803 [354, 1199] | 3.55 | 2029-12-07 [2028-01-06, 2031-08-18] | 0.09 |
| **6.5 pp** | 475 [209, 709] | 2.1 | 2028-07-14 [2027-05-26, 2029-07-13] | 0.118 |
| **9.0 pp** | 248 [109, 370] | 1.1 | 2027-07-26 [2026-12-22, 2028-02-01] | 0.183 |
| **12.0 pp** | 139 [61, 208] | 0.62 | 2027-02-05 [2026-10-07, 2027-05-25] | 0.289 |

## MDE por horizonte

| días | fecha | MDE 80% (IC95) | MDE 50% |
|---|---|---|---|
| 35 | 2026-08-27 | **24.0 pp** [15.9, 29.3] | 16.8 pp |
| 73 | 2026-10-26 | **16.6 pp** [11.0, 20.3] | 11.6 pp |
| 125 | 2027-01-14 | **12.7 pp** [8.4, 15.5] | 8.9 pp |
| 250 | 2027-07-29 | **9.0 pp** [5.9, 10.9] | 6.3 pp |
| 500 | 2028-08-22 | **6.3 pp** [4.2, 7.7] | 4.4 pp |
| 750 | 2029-09-17 | **5.2 pp** [3.4, 6.3] | 3.6 pp |
| 1000 | 2030-10-10 | **4.5 pp** [3.0, 5.5] | 3.1 pp |

## Ruta 2 · simulación (días reales remuestreados, permutación de signo por día)

| días | α empírico (δ=0) | δ=5.0 pp | δ=6.5 pp | δ=9.0 pp | δ=12.0 pp |
|---|---|---|---|---|---|
| 35 | 0.055 [0.048, 0.064] | 0.09 [0.08, 0.1] | 0.11 [0.103, 0.126] | 0.17 [0.154, 0.181] | 0.29 [0.269, 0.302] |
| 73 | 0.048 [0.041, 0.057] | 0.14 [0.129, 0.154] | 0.21 [0.194, 0.223] | 0.35 [0.338, 0.372] | 0.55 [0.531, 0.567] |
| 125 | 0.053 [0.046, 0.062] | 0.20 [0.187, 0.216] | 0.30 [0.286, 0.319] | 0.53 [0.512, 0.547] | 0.78 [0.76, 0.79] |
| 250 | 0.050 [0.042, 0.058] | 0.36 [0.347, 0.382] | 0.55 [0.53, 0.566] | 0.82 [0.806, 0.833] | 0.97 [0.965, 0.977] |
| 500 | 0.045 [0.038, 0.053] | 0.62 [0.606, 0.64] | 0.83 [0.817, 0.844] | 0.99 [0.98, 0.989] | 1.00 [0.999, 1.0] |
| 750 | 0.053 [0.045, 0.061] | 0.79 [0.776, 0.805] | 0.95 [0.944, 0.959] | 1.00 [0.998, 1.0] | 1.00 [0.999, 1.0] |
| 1000 | 0.052 [0.045, 0.061] | 0.89 [0.881, 0.903] | 0.99 [0.984, 0.992] | 1.00 [0.999, 1.0] | 1.00 [0.999, 1.0] |

## Ruta 3 · simulador calibrado (Frente A; el efecto entra por β·SOX, no como δ constante) — LA QUE MANDA

- Generadores calibrados al ICC observado 0.3925 (b, c por δ: δ=0.0: b=0.5156, c=5.5312, δ=5.0: b=0.875, c=5.1562, δ=6.5: b=0.9688, c=4.9688, δ=9.0: b=1.1562, c=4.6875, δ=12.0: b=1.375, c=4.3125); verdad medida por generador (pp): {'0.0': -0.01, '5.0': 5.04, '6.5': 6.36, '9.0': 8.97, '12.0': 11.94}; 1000 réplicas por celda, Wilson.

| días | α empírico (δ=0) | δ=5.0 pp | δ=6.5 pp | δ=9.0 pp | δ=12.0 pp |
|---|---|---|---|---|---|
| 35 | 0.037 [0.031, 0.044] | 0.07 [0.058, 0.091] | 0.10 [0.081, 0.118] | 0.17 [0.149, 0.196] | 0.27 [0.24, 0.294] |
| 73 | 0.048 [0.041, 0.056] | 0.13 [0.114, 0.157] | 0.18 [0.162, 0.21] | 0.30 [0.273, 0.33] | 0.49 [0.462, 0.524] |
| 125 | 0.044 [0.037, 0.052] | 0.17 [0.144, 0.19] | 0.27 [0.245, 0.3] | 0.51 [0.477, 0.539] | 0.75 [0.718, 0.772] |
| 250 | 0.053 [0.046, 0.062] | 0.34 [0.315, 0.374] | 0.51 [0.481, 0.543] | 0.78 [0.756, 0.807] | 0.96 [0.952, 0.975] |
| 500 | 0.051 [0.044, 0.059] | 0.57 [0.54, 0.601] | 0.79 [0.768, 0.818] | 0.97 [0.962, 0.982] | 1.00 [0.996, 1.0] |
| 750 | 0.053 [0.045, 0.061] | 0.75 [0.726, 0.78] | 0.93 [0.916, 0.947] | 1.00 [0.994, 1.0] | 1.00 [0.996, 1.0] |
| 1000 | 0.054 [0.046, 0.063] | 0.86 [0.834, 0.877] | 0.98 [0.969, 0.987] | 1.00 [0.996, 1.0] | 1.00 [0.996, 1.0] |

**Días sellados para potencia 0,80 (bisección sobre el simulador, 3 semillas). El intervalo es SÓLO error de Monte Carlo** (rango de las semillas y Wilson de celda); no propaga b, c, ICC ni el SE de día: **la banda paramétrica es la de la ruta 1** (dictamen 1b, 3-sep-2026).

| efecto | días (mediana de 3 semillas) | rango de semillas | rango MC (Wilson) | fecha estimada [rango MC] | ruta 1 (paramétrica) |
|---|---|---|---|---|---|
| **5.0 pp** | 811 | [799, 846] | [759, 936] | 2029-12-20 ['2029-10-01', '2030-07-03'] | 803 [354, 1199] |
| **6.5 pp** | 510 | [505, 516] | [467, 580] | 2028-09-06 ['2028-06-30', '2028-12-25'] | 475 [209, 709] |
| **9.0 pp** | 263 | [252, 269] | [229, 296] | 2027-08-18 ['2027-06-25', '2027-10-08'] | 248 [109, 370] |
| **12.0 pp** | 141 | [141, 147] | [130, 167] | 2027-02-09 ['2027-01-22', '2027-03-22'] | 139 [61, 208] |

**Comparación pareada ruta 2 − ruta 3** sobre 28 celdas (mismo δ, mismo D): ruta 2 por encima en 23, por debajo en 1 (McNemar exacto p = 3e-06); diferencia media **+2.17 pp** de potencia, IC95 [1.55, 2.81] (descriptivo). 7 celdas están en techo (las dos rutas ≥ 0.97: δ=9.0 D=500, δ=12.0 D=500, δ=9.0 D=750, δ=12.0 D=750, δ=6.5 D=1000, δ=9.0 D=1000, δ=12.0 D=1000) y su diferencia es 0 por construcción. Sobre las **12 celdas que comparte con A4** (`calibracion_instrumento.md`): **+2.45 pp** [1.64, 3.27], comparable con el +2,67 [1,85, 3,55] de A4. α de la ruta 3 a 3000 réplicas; potencias a 1000. Si el intervalo está sobre cero, la ruta 2 es optimista y las fechas de las rutas 1 y 2 son cotas inferiores.

## R2 sobre este ancla (excluir 15–23 jul, criterio congelado)

- n = 202, ventaja **2.5 pp**, IC95 de día [-13.64, 19.23] (contiene el cero), McNemar de filas p = 0.675 (b = 48, c = 43), permutación de día p = 0.8248. **R2 DISPARA sobre este ancla: sin el bloque 1 la ventaja no se distingue de cero por ninguna ruta.**
- Cadencia 0.897 sellos/día hábil, Wilson [0.764, 0.959]: la fecha de los 9 pp va de 2027-07-05 a 2027-09-21 por cadencia sola; con el gasto de α del plan secuencial (×1.0241, DISEÑO.md §A3.3) son 254 días.

## Estacionariedad mínima: las dos mitades de la ventana (ojo: el bloque 1 de R2 está entero en la primera)

| mitad | días | filas | ventaja | IC95 de día |
|---|---|---|---|---|
| primera_mitad | 17 | 120 | 19.17 pp | [-3.51, 44.07] |
| segunda_mitad | 18 | 126 | 0.0 pp | [-21.57, 20.47] |

