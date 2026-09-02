# El experimento natural de los feriados — Frente B1 (PROPUESTA)

> **PROPUESTA — Frente B1, octava corrida; pendiente de dictamen** · generado 2026-09-02T18:50:13.240441+00:00 · `python GEMELO/decaimiento_feriados.py` --abrir-prueba

Pre-registro: `GEMELO/preregistro/frente_B.md`. Sin motor: predicción = signo del último cierre de NY anterior a la apertura local. Δ = acierto del signo − «siempre al alza» (`excluir_cero`). IC por bootstrap de fechas; p por permutación de la etiqueta de condición entre fechas. Efecto relevante pre-declarado: 5.0 pp.

## Años de AJUSTE (2018-09-01 → 2023-12-31): 10438 filas, 1381 fechas (0 filas excluidas por insumo rancio: la serie del SOX no tenía la última sesión de NY del calendario)

| contraste | fechas cond / normal | Δ cond (pp) | Δ normal (pp) | diferencia (IC95 fechas iid) | IC95 bloques 20 | p perm | contra 0 / contra 5 pp |
|---|---|---|---|---|---|---|---|
| C1 · XETR: NY cerrada (n_ny=0) vs normal | 35 / 1294 | 2.86 | 3.94 | **-1.08** [-21.16, 20.0] | [-13.37, 11.27] (contiene el cero) | 1.0 | contiene el cero; contiene ±5 pp |
| C1 · XETR: vs normal SIN lunes (control h) | 35 / 1035 | 2.86 | 3.86 | **-1.01** [-21.05, 20.15] | [-13.65, 11.1] (contiene el cero) | 1.0 | contiene el cero; contiene ±5 pp |
| C1 · XETR: control |SOX| ESTANDARIZADO por 4 estratos (cortes del grupo normal) | [11, 15, 4, 5] | — | — | **-1.05** [-24.14, 24.37] | — | — | contiene el cero |
| C1 · XETR: control |SOX| truncado SIMÉTRICO a ≤ p75 de la condición (1.29) | 26 / 660 | 3.85 | -1.97 | **5.82** [-16.63, 30.5] | [-4.24, 15.93] (contiene el cero) | 0.7788 | contiene el cero; contiene ±5 pp |
| C1 · XETR: fracción de fechas cuyo insumo YA fue negociado por la sesión local anterior | n_ny=0: 1.0 · n_ny=1: 0.0 | | | **confusión estructural: C1 contrasta insumo no incorporado vs YA incorporado, no fresco vs viejo** | | | |
| C1 · XKRX: NY cerrada (n_ny=0) vs normal | 40 / 1208 | 12.5 | 16.27 | **-3.77** [-19.79, 12.33] | [-17.99, 10.26] (contiene el cero) | 0.7168 | contiene el cero; contiene ±5 pp |
| C1 · XKRX: vs normal SIN lunes (control h) | 40 / 975 | 12.5 | 15.55 | **-3.05** [-19.02, 13.24] | [-17.4, 10.94] (contiene el cero) | 0.7601 | contiene el cero; contiene ±5 pp |
| C1 · XKRX: control |SOX| ESTANDARIZADO por 4 estratos (cortes del grupo normal) | [14, 15, 4, 7] | — | — | **0.8** [-18.14, 18.81] | — | — | contiene el cero |
| C1 · XKRX: control |SOX| truncado SIMÉTRICO a ≤ p75 de la condición (1.354) | 30 / 636 | 6.67 | 4.05 | **2.62** [-13.49, 19.44] | [-9.75, 15.56] (contiene el cero) | 0.853 | contiene el cero; contiene ±5 pp |
| C1 · XKRX: fracción de fechas cuyo insumo YA fue negociado por la sesión local anterior | n_ny=0: 1.0 · n_ny=1: 0.0 | | | **confusión estructural: C1 contrasta insumo no incorporado vs YA incorporado, no fresco vs viejo** | | | |
| C1 · XTAI: NY cerrada (n_ny=0) vs normal | 41 / 1202 | 0.0 | 17.47 | **-17.47** [-36.21, 2.51] | [-26.45, -7.38] | 0.1222 | contiene el cero; contiene ±5 pp |
| C1 · XTAI: vs normal SIN lunes (control h) | 41 / 977 | 0.0 | 16.07 | **-16.07** [-35.17, 4.28] | [-25.25, -5.92] | 0.1467 | contiene el cero; contiene ±5 pp |
| C1 · XTAI: control |SOX| ESTANDARIZADO por 4 estratos (cortes del grupo normal) | [14, 15, 3, 9] | — | — | **-16.35** [-44.4, 12.03] | — | — | contiene el cero |
| C1 · XTAI: control |SOX| truncado SIMÉTRICO a ≤ p75 de la condición (1.55) | 30 / 703 | -3.33 | 5.41 | **-8.74** [-28.68, 11.91] | [-18.45, 0.98] (contiene el cero) | 0.5101 | contiene el cero; contiene ±5 pp |
| C1 · XTAI: fracción de fechas cuyo insumo YA fue negociado por la sesión local anterior | n_ny=0: 1.0 · n_ny=1: 0.0 | | | **confusión estructural: C1 contrasta insumo no incorporado vs YA incorporado, no fresco vs viejo** | | | |
| C1 · XTKS: NY cerrada (n_ny=0) vs normal | 43 / 1187 | -1.16 | 22.24 | **-23.41** [-39.96, -6.68] | [-34.39, -12.5] | 0.0057 | excluye el cero; excluye ±5 pp |
| C1 · XTKS: vs normal SIN lunes (control h) | 43 / 965 | -1.16 | 22.23 | **-23.39** [-39.85, -6.69] | [-33.76, -12.05] | 0.0037 | excluye el cero; excluye ±5 pp |
| C1 · XTKS: control |SOX| ESTANDARIZADO por 4 estratos (cortes del grupo normal) | [13, 17, 4, 9] | — | — | **-30.97** [-49.72, -11.95] | — | — | excluye el cero |
| C1 · XTKS: control |SOX| truncado SIMÉTRICO a ≤ p75 de la condición (1.837) | 32 / 775 | -1.56 | 15.18 | **-16.74** [-33.25, -0.82] | [-24.47, -8.8] | 0.0765 | excluye el cero; contiene ±5 pp |
| C1 · XTKS: fracción de fechas cuyo insumo YA fue negociado por la sesión local anterior | n_ny=0: 1.0 · n_ny=1: 0.0 | | | **confusión estructural: C1 contrasta insumo no incorporado vs YA incorporado, no fresco vs viejo** | | | |
| feriado local · XETR: n_ny≥2, insumo = último cierre | 21 / 1294 | -9.52 | 3.94 | **-13.47** [-31.82, 4.35] | [-20.16, -6.62] | 0.4204 | contiene el cero; contiene ±5 pp |
| feriado local · XETR: n_ny≥2, insumo = cierre ANTERIOR (viejo) | 21 / 1294 | -28.57 | -4.87 | **-23.7** [-50.6, 3.97] | [-32.46, -14.64] | 0.1507 | contiene el cero; contiene ±5 pp |
| feriado local · XETR: McNemar último vs anterior, MISMAS filas | n = 21 | 76.2 | 57.1 (base 85.7) | b = 7, c = 3 | — | **p = 0.3427817111479114** | filas como unidad: optimista por clustering de día |
| feriado local · XKRX: n_ny≥2, insumo = último cierre | 48 / 1208 | 18.75 | 16.27 | **2.48** [-14.29, 18.8] | [-11.16, 14.42] (contiene el cero) | 0.7878 | contiene el cero; contiene ±5 pp |
| feriado local · XKRX: n_ny≥2, insumo = cierre ANTERIOR (viejo) | 48 / 1208 | 14.58 | -7.22 | **21.8** [7.39, 36.04] | [9.82, 33.29] | 0.0202 | excluye el cero; supera 5 pp |
| feriado local · XKRX: McNemar último vs anterior, MISMAS filas | n = 96 | 69.8 | 65.6 (base 51.0) | b = 27, c = 23 | — | **p = 0.6713732405408726** | filas como unidad: optimista por clustering de día |
| feriado local · XTAI: n_ny≥2, insumo = último cierre | 40 / 1202 | 12.5 | 17.47 | **-4.97** [-27.47, 16.86] | [-16.97, 7.28] (contiene el cero) | 0.7133 | contiene el cero; contiene ±5 pp |
| feriado local · XTAI: n_ny≥2, insumo = cierre ANTERIOR (viejo) | 40 / 1202 | 10.0 | -3.16 | **13.16** [-5.17, 31.16] | [5.17, 21.25] | 0.2479 | contiene el cero; contiene ±5 pp |
| feriado local · XTAI: McNemar último vs anterior, MISMAS filas | n = 40 | 67.5 | 65.0 (base 55.0) | b = 10, c = 9 | — | **p = 1.0** | filas como unidad: optimista por clustering de día |
| feriado local · XTKS: n_ny≥2, insumo = último cierre | 65 / 1187 | 23.85 | 22.24 | **1.6** [-11.33, 14.44] | [-8.38, 12.55] (contiene el cero) | 0.842 | contiene el cero; contiene ±5 pp |
| feriado local · XTKS: n_ny≥2, insumo = cierre ANTERIOR (viejo) | 65 / 1187 | 10.0 | -4.13 | **14.13** [-1.57, 29.91] | [0.66, 29.06] | 0.0625 | contiene el cero; contiene ±5 pp |
| feriado local · XTKS: McNemar último vs anterior, MISMAS filas | n = 260 | 76.9 | 63.1 (base 53.1) | b = 84, c = 48 | — | **p = 0.0023163110616671325** | filas como unidad: optimista por clustering de día |
| C2 · XETR sin Tokio vs Asia completa | 64 / 1117 | 1.56 | 3.85 | **-2.29** [-21.57, 15.98] | [-22.79, 15.75] (contiene el cero) | 0.8665 | contiene el cero; contiene ±5 pp |
| C3 · XETR sin Seúl o sin Taipéi vs Asia completa | 81 / 1117 | 7.41 | 3.85 | **3.56** [-11.39, 18.91] | [-5.62, 12.49] (contiene el cero) | 0.6771 | contiene el cero; contiene ±5 pp |
| C2+C3 · XETR con 2 intermediarios vs 3 | 145 / 1117 | 4.83 | 3.85 | **0.98** [-11.19, 12.74] | [-11.52, 12.37] (contiene el cero) | 0.9013 | contiene el cero; contiene ±5 pp |

Conteo de (exchange, n_ny): {'XETR|n_ny=0': 35, 'XETR|n_ny=1': 1294, 'XETR|n_ny=2': 19, 'XETR|n_ny=3': 2, 'XKRX|n_ny=0': 41, 'XKRX|n_ny=1': 1217, 'XKRX|n_ny=2': 37, 'XKRX|n_ny=3': 6, 'XKRX|n_ny=4': 5, 'XKRX|n_ny=5': 1, 'XTAI|n_ny=0': 42, 'XTAI|n_ny=1': 1212, 'XTAI|n_ny=2': 24, 'XTAI|n_ny=3': 11, 'XTAI|n_ny=4': 1, 'XTAI|n_ny=7': 2, 'XTAI|n_ny=8': 2, 'XTKS|n_ny=0': 43, 'XTKS|n_ny=1': 1187, 'XTKS|n_ny=2': 54, 'XTKS|n_ny=3': 4, 'XTKS|n_ny=4': 6, 'XTKS|n_ny=7': 1}. Fechas C1 por exchange / unión / intersección: {'union': 46, 'interseccion': 29, 'por_exchange': {'XETR': 35, 'XKRX': 41, 'XTAI': 42, 'XTKS': 43}} (un experimento, no cuatro). Excluidas: 0 filas de la ventana sellada ['2026-07-06', '2026-09-02'] con embargo de 5 sesiones.

Potencia de C2+C3 calculada (semiancho del IC95 al multiplicar las fechas de condición): x1: 145 fechas → ±11.73 pp; x6: 870 fechas → ±5.87 pp; x10: 1450 fechas → ±5.27 pp; x23: 3335 fechas → ±4.88 pp. Refutar H_dis exige semiancho < 5 pp; DECIDIR entre H_dis y H_abs exige semiancho < 2,5 pp. Multiplicando sólo las fechas de condición el semiancho NO baja de ~±5 pp ni a ×23 (el grupo normal también acota): con feriados asiáticos la pregunta no se decide en ningún horizonte razonable (×23 son más de un siglo de feriados).

## Años de PRUEBA (2024-01-01 → 2026-08-31): 4830 filas, 643 fechas (8 filas excluidas por insumo rancio: la serie del SOX no tenía la última sesión de NY del calendario)

| contraste | fechas cond / normal | Δ cond (pp) | Δ normal (pp) | diferencia (IC95 fechas iid) | IC95 bloques 20 | p perm | contra 0 / contra 5 pp |
|---|---|---|---|---|---|---|---|
| C1 · XETR: NY cerrada (n_ny=0) vs normal | 19 / 596 | 21.05 | 5.2 | **15.85** [-7.72, 40.83] | [-8.12, 41.0] (contiene el cero) | 0.3692 | contiene el cero; contiene ±5 pp |
| C1 · XETR: vs normal SIN lunes (control h) | 19 / 474 | 21.05 | 4.22 | **16.83** [-6.55, 42.09] | [-6.33, 39.78] (contiene el cero) | 0.2742 | contiene el cero; contiene ±5 pp |
| C1 · XETR: control |SOX| ESTANDARIZADO por 4 estratos (cortes del grupo normal) | [3, 6, 5, 5] | — | — | **16.52** [-7.41, 41.95] | — | — | contiene el cero |
| C1 · XETR: control |SOX| truncado SIMÉTRICO a ≤ p75 de la condición (2.285) | 14 / 422 | 21.43 | 0.0 | **21.43** [-8.56, 50.96] | [-8.33, 50.24] (contiene el cero) | 0.2964 | contiene el cero; contiene ±5 pp |
| C1 · XETR: fracción de fechas cuyo insumo YA fue negociado por la sesión local anterior | n_ny=0: 1.0 · n_ny=1: 0.0 | | | **confusión estructural: C1 contrasta insumo no incorporado vs YA incorporado, no fresco vs viejo** | | | |
| C1 · XKRX: NY cerrada (n_ny=0) vs normal | 20 / 553 | 15.0 | 18.1 | **-3.1** [-28.33, 21.7] | [-28.48, 22.44] (contiene el cero) | 0.842 | contiene el cero; contiene ±5 pp |
| C1 · XKRX: vs normal SIN lunes (control h) | 20 / 443 | 15.0 | 16.95 | **-1.95** [-27.4, 23.25] | [-27.43, 23.96] (contiene el cero) | 0.9955 | contiene el cero; contiene ±5 pp |
| C1 · XKRX: control |SOX| ESTANDARIZADO por 4 estratos (cortes del grupo normal) | [5, 6, 4, 5] | — | — | **-1.43** [-23.4, 21.47] | — | — | contiene el cero |
| C1 · XKRX: control |SOX| truncado SIMÉTRICO a ≤ p75 de la condición (2.088) | 15 / 379 | 26.67 | 9.78 | **16.89** [-12.95, 46.99] | [-11.36, 45.94] (contiene el cero) | 0.3317 | contiene el cero; contiene ±5 pp |
| C1 · XKRX: fracción de fechas cuyo insumo YA fue negociado por la sesión local anterior | n_ny=0: 1.0 · n_ny=1: 0.0 | | | **confusión estructural: C1 contrasta insumo no incorporado vs YA incorporado, no fresco vs viejo** | | | |
| C1 · XTAI: NY cerrada (n_ny=0) vs normal | 17 / 542 | 23.53 | 14.39 | **9.14** [-16.77, 36.73] | [-16.79, 36.36] (contiene el cero) | 0.5639 | contiene el cero; contiene ±5 pp |
| C1 · XTAI: vs normal SIN lunes (control h) | 17 / 437 | 23.53 | 13.27 | **10.26** [-15.79, 37.0] | [-15.72, 37.38] (contiene el cero) | 0.5684 | contiene el cero; contiene ±5 pp |
| C1 · XTAI: control |SOX| ESTANDARIZADO por 4 estratos (cortes del grupo normal) | [4, 5, 4, 4] | — | — | **8.21** [-14.59, 30.86] | — | — | contiene el cero |
| C1 · XTAI: control |SOX| truncado SIMÉTRICO a ≤ p75 de la condición (1.942) | 12 / 355 | 41.67 | 4.79 | **36.88** [8.78, 65.14] | [9.34, 65.26] | 0.0785 | excluye el cero; supera 5 pp |
| C1 · XTAI: fracción de fechas cuyo insumo YA fue negociado por la sesión local anterior | n_ny=0: 1.0 · n_ny=1: 0.0 | | | **confusión estructural: C1 contrasta insumo no incorporado vs YA incorporado, no fresco vs viejo** | | | |
| C1 · XTKS: NY cerrada (n_ny=0) vs normal | 24 / 546 | 4.17 | 18.45 | **-14.28** [-31.51, 2.27] | [-24.03, -4.44] | 0.1665 | contiene el cero; contiene ±5 pp |
| C1 · XTKS: vs normal SIN lunes (control h) | 24 / 448 | 4.17 | 18.46 | **-14.29** [-31.41, 2.05] | [-24.38, -4.68] | 0.1525 | contiene el cero; contiene ±5 pp |
| C1 · XTKS: control |SOX| ESTANDARIZADO por 4 estratos (cortes del grupo normal) | [6, 8, 5, 5] | — | — | **-15.51** [-32.05, -1.06] | — | — | excluye el cero |
| C1 · XTKS: control |SOX| truncado SIMÉTRICO a ≤ p75 de la condición (1.942) | 18 / 355 | 11.11 | 10.86 | **0.25** [-18.85, 18.66] | [-18.31, 19.07] (contiene el cero) | 1.0 | contiene el cero; contiene ±5 pp |
| C1 · XTKS: fracción de fechas cuyo insumo YA fue negociado por la sesión local anterior | n_ny=0: 1.0 · n_ny=1: 0.0 | | | **confusión estructural: C1 contrasta insumo no incorporado vs YA incorporado, no fresco vs viejo** | | | |
| feriado local · XETR: n_ny≥2, insumo = último cierre | 10 / 596 | 40.0 | 5.2 | **34.8** [4.46, 65.64] | [4.46, 65.47] | 0.1345 | excluye el cero; contiene ±5 pp |
| feriado local · XETR: n_ny≥2, insumo = cierre ANTERIOR (viejo) | 10 / 596 | 40.0 | -1.34 | **41.34** [10.67, 72.85] | [10.84, 72.01] | 0.0557 | excluye el cero; supera 5 pp |
| feriado local · XETR: McNemar último vs anterior, MISMAS filas | n = 10 | 90.0 | 90.0 (base 50.0) | b = 0, c = 0 | — | **p = 1.0** | filas como unidad: optimista por clustering de día |
| feriado local · XKRX: n_ny≥2, insumo = último cierre | 26 / 553 | 3.85 | 18.1 | **-14.25** [-38.19, 8.81] | [-29.87, 1.33] (contiene el cero) | 0.1972 | contiene el cero; contiene ±5 pp |
| feriado local · XKRX: n_ny≥2, insumo = cierre ANTERIOR (viejo) | 26 / 553 | -3.85 | -10.23 | **6.38** [-16.88, 29.44] | [-5.39, 17.9] (contiene el cero) | 0.6026 | contiene el cero; contiene ±5 pp |
| feriado local · XKRX: McNemar último vs anterior, MISMAS filas | n = 52 | 65.4 | 57.7 (base 61.5) | b = 13, c = 9 | — | **p = 0.5224312849615644** | filas como unidad: optimista por clustering de día |
| feriado local · XTAI: n_ny≥2, insumo = último cierre | 22 / 542 | 31.82 | 14.39 | **17.43** [-6.11, 40.41] | [8.27, 26.22] | 0.2259 | contiene el cero; contiene ±5 pp |
| feriado local · XTAI: n_ny≥2, insumo = cierre ANTERIOR (viejo) | 22 / 542 | 22.73 | -11.99 | **34.72** [3.2, 64.88] | [23.41, 46.21] | 0.018 | excluye el cero; contiene ±5 pp |
| feriado local · XTAI: McNemar último vs anterior, MISMAS filas | n = 22 | 81.8 | 72.7 (base 50.0) | b = 6, c = 4 | — | **p = 0.7518296340458492** | filas como unidad: optimista por clustering de día |
| feriado local · XTKS: n_ny≥2, insumo = último cierre | 33 / 546 | 4.55 | 18.45 | **-13.9** [-30.54, 2.47] | [-24.01, -3.68] | 0.1207 | contiene el cero; contiene ±5 pp |
| feriado local · XTKS: n_ny≥2, insumo = cierre ANTERIOR (viejo) | 33 / 546 | -6.06 | -8.4 | **2.34** [-15.61, 19.83] | [-9.7, 14.47] (contiene el cero) | 0.8398 | contiene el cero; contiene ±5 pp |
| feriado local · XTKS: McNemar último vs anterior, MISMAS filas | n = 132 | 69.7 | 59.1 (base 65.2) | b = 43, c = 29 | — | **p = 0.12550647143746915** | filas como unidad: optimista por clustering de día |
| C2 · XETR sin Tokio vs Asia completa | 29 / 504 | -6.9 | 3.97 | **-10.86** [-31.83, 11.93] | [-25.58, 4.32] (contiene el cero) | 0.4579 | contiene el cero; contiene ±5 pp |
| C3 · XETR sin Seúl o sin Taipéi vs Asia completa | 47 / 504 | 21.28 | 3.97 | **17.31** [-2.44, 36.71] | [2.21, 34.93] | 0.1077 | contiene el cero; contiene ±5 pp |
| C2+C3 · XETR con 2 intermediarios vs 3 | 76 / 504 | 10.53 | 3.97 | **6.56** [-9.06, 22.02] | [-5.93, 19.27] (contiene el cero) | 0.4569 | contiene el cero; contiene ±5 pp |

Conteo de (exchange, n_ny): {'XETR|n_ny=0': 19, 'XETR|n_ny=1': 597, 'XETR|n_ny=2': 8, 'XETR|n_ny=3': 2, 'XKRX|n_ny=0': 20, 'XKRX|n_ny=1': 553, 'XKRX|n_ny=2': 20, 'XKRX|n_ny=3': 3, 'XKRX|n_ny=4': 1, 'XKRX|n_ny=5': 1, 'XKRX|n_ny=6': 1, 'XTAI|n_ny=0': 20, 'XTAI|n_ny=1': 552, 'XTAI|n_ny=2': 15, 'XTAI|n_ny=3': 4, 'XTAI|n_ny=7': 1, 'XTAI|n_ny=8': 2, 'XTKS|n_ny=0': 24, 'XTKS|n_ny=1': 546, 'XTKS|n_ny=2': 28, 'XTKS|n_ny=3': 3, 'XTKS|n_ny=4': 2}. Fechas C1 por exchange / unión / intersección: {'union': 24, 'interseccion': 16, 'por_exchange': {'XETR': 19, 'XKRX': 20, 'XTAI': 20, 'XTKS': 24}} (un experimento, no cuatro). Excluidas: 348 filas de la ventana sellada ['2026-07-06', '2026-09-02'] con embargo de 5 sesiones.

Potencia de C2+C3 calculada (semiancho del IC95 al multiplicar las fechas de condición): x1: 76 fechas → ±15.83 pp; x6: 456 fechas → ±8.23 pp; x10: 760 fechas → ±7.19 pp; x23: 1748 fechas → ±6.4 pp. Refutar H_dis exige semiancho < 5 pp; DECIDIR entre H_dis y H_abs exige semiancho < 2,5 pp. Multiplicando sólo las fechas de condición el semiancho NO baja de ~±5 pp ni a ×23 (el grupo normal también acota): con feriados asiáticos la pregunta no se decide en ningún horizonte razonable (×23 son más de un siglo de feriados).

**Lectura pre-registrada:** H_dis y H_abs coinciden en C1 (ambas: la ventaja cae); difieren en C2/C3 (H_dis: nada; H_abs: sube ≥ 5 pp). Si el IC de C2/C3 contiene 0 y 5 pp, no se distinguen con estos datos.

