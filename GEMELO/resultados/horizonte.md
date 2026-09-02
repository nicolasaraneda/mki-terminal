# ¿Es medible en principio? — Frente B (séptima corrida)

- Generado: 2026-09-02T13:37:57.423791+00:00 · `python GEMELO/SECUENCIAL/horizonte.py`
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

## R2 sobre este ancla (excluir 15–23 jul, criterio congelado)

- n = 202, ventaja **2.5 pp**, IC95 de día [-13.64, 19.23] (contiene el cero), McNemar de filas p = 0.675 (b = 48, c = 43), permutación de día p = 0.8248. **R2 DISPARA sobre este ancla: sin el bloque 1 la ventaja no se distingue de cero por ninguna ruta.**
- Cadencia 0.897 sellos/día hábil, Wilson [0.764, 0.959]: la fecha de los 9 pp va de 2027-07-05 a 2027-09-21 por cadencia sola; con el gasto de α del plan secuencial (×1.0241, DISEÑO.md §A3.3) son 254 días.

## Estacionariedad mínima: las dos mitades de la ventana (ojo: el bloque 1 de R2 está entero en la primera)

| mitad | días | filas | ventaja | IC95 de día |
|---|---|---|---|---|
| primera_mitad | 17 | 120 | 19.17 pp | [-3.51, 44.07] |
| segunda_mitad | 18 | 126 | 0.0 pp | [-21.57, 20.47] |

