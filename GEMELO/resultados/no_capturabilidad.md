# La no capturabilidad como hipótesis — Frente C (PROPUESTA)

> **PROPUESTA — Frente C, octava corrida; pendiente de dictamen** · generado 2026-09-02T18:35:43.484814+00:00 · `python GEMELO/no_capturabilidad.py` --abrir-prueba

Pre-registro: `GEMELO/preregistro/frente_C.md`. Sin motor: predicción = signo del último cierre de NY anterior a la apertura local. Sesión = close/open − 1. Cartera direccional q = signo(pred)·sesión, sin costos. IC por bootstrap de bloques circulares de 10 fechas. Datos hasta la última barra completa (2026-08-25); ventana sellada ('2026-07-06', '2026-09-02') derivada del backup y embargada en sus dos bordes.

## Años de AJUSTE: 10146 filas, 1381 fechas

### H1 · estructural: el gap se acierta, la sesión no se captura

| cantidad | punto | IC95 (fechas) |
|---|---|---|
| ventaja_direccional_gap_pp | 17.396 | [14.9115, 19.9096] |
| ventaja_direccional_sesion_pp | -1.508 | [-3.4973, 0.4175] (contiene el cero) |
| retorno_medio_cartera_sesion_pp | -0.0845 | [-0.1418, -0.0302] |
| retorno_medio_si_el_gap_fuera_operable_pp | 0.731 | [0.6687, 0.7999] — **NO EJECUTABLE: exige comprar al cierre local ANTES de que exista el cierre de NY; su Sharpe/DSR saturan y no son un aprobado** |
| retorno_medio_siempre_largo_sesion_pp | 0.0029 | [-0.0516, 0.0578] (contiene el cero) |
| fraccion_aciertos_gap | 0.7141 | [0.6977, 0.7299] |

- McNemar gap: modelo 71.41% (Wilson filas [70.5, 72.3]) vs base 54.01%, b = 3271, c = 1506, McNemar p = 1.113120707246663e-143 — p y Wilson de FILAS: optimistas por clustering de día (unidad = fecha)
- McNemar sesión: modelo 47.86% (Wilson filas [46.9, 48.8]) vs base 49.37%, b = 2312, c = 2465, McNemar p = 0.02786325789466922 — p y Wilson de FILAS: optimistas por clustering de día (unidad = fecha)

### H2 · asimetría de magnitud

- Fracción de aciertos del gap: 0.7141 [0.6977, 0.7299]; contribución al retorno medio de la cartera: aciertos -0.0668 [-0.1132, -0.0248] pp, errores -0.0177 [-0.0416, 0.0054] (contiene el cero) pp.
- Diferencia E[q|acierto] − E[q|error]: -0.0316 [-0.1174, 0.0504] (contiene el cero) pp.
- **Veredicto H2:** REFUTADA EN SU PREMISA: los aciertos pierden más que los errores (signo contrario al postulado); la diferencia no se distingue de cero. El criterio original aplicado literalmente habría dado un FALSO POSITIVO por aritmética de signos.
- q medio dado acierto: -0.0936 [-0.1564, -0.0338]; dado error: -0.062 [-0.1408, 0.0138] (contiene el cero).
- Signos: q|acierto −, q|error −. Razón |E[q|error]| / |E[q|acierto]| (nulo 1, umbral 1,5): 0.662 [0.0516, 1.8988] (contiene el nulo 1.0); IC contiene ±1.5 — el criterio «≥ 1,5» aplicado literalmente daría un FALSO POSITIVO (E[q|acierto] ≤ 0 vuelve trivial la desigualdad).

### H3 · sobrerreacción (pendiente < 0) o deriva (> 0) de la sesión sobre la sorpresa

- Pendiente sesión ~ sorpresa (gap − β·SOX; β in-sample (descriptiva)): -0.031 [-0.0753, 0.0113] (contiene el cero); IC no contiene ±0.1, todo el IC bajo el umbral; con β de la primera mitad del ajuste: -0.0321 [-0.0761, 0.0098] (contiene el cero); IC no contiene ±0.1, todo el IC bajo el umbral
- Cortes de tercil de s: [-0.3581, 0.4241] (calculados aquí)
- Pendiente sesión ~ gap: -0.0721 [-0.1081, -0.0374]; IC contiene ±0.1
- Sesión media por tercil de sorpresa: bajo 0.0355 [-0.0544, 0.1222] (contiene el cero); medio -0.0196 [-0.0898, 0.0488] (contiene el cero); alto -0.0072 [-0.0827, 0.0679] (contiene el cero); diferencia alto − bajo: -0.0427 [-0.1469, 0.0583] (contiene el cero)
- sesión ≡ total − gap por identidad exacta (sin Open independiente): la pendiente sesión~gap es indistinguible de la atenuación −Var(ε)/Var(g) por error de medición del gap (testigos de dos añadas: gaps del 2-sep, cierres del 26-ago).
- **Veredicto H3:** No se detecta relación de la sesión con la sorpresa respecto de β (IC contiene el cero). Sobre el gap crudo la pendiente es negativa pero confundida con error de medición y su irrelevancia (|pendiente| < 0,1) sólo se establece donde TODO el IC queda bajo 0,1.

### Sensibilidad al bloque del bootstrap (IC95 por bloque de 1/5/10/20/40/60 fechas)

| bloque | ventaja sesión (pp) | q medio (pp) | pendiente sesión~gap | pendiente sesión~sorpresa |
|---|---|---|---|---|
| 1 | [-3.4925, 0.5237] | [-0.1413, -0.0296] | [-0.1175, -0.0278] | [-0.0986, 0.0362] |
| 5 | [-3.4296, 0.412] | [-0.1396, -0.0295] | [-0.1135, -0.0299] | [-0.0785, 0.0164] |
| 10 | [-3.4973, 0.4175] | [-0.1418, -0.0302] | [-0.1081, -0.0374] | [-0.0753, 0.0113] |
| 20 | [-3.4271, 0.4433] | [-0.1391, -0.0329] | [-0.1031, -0.0406] | [-0.0699, 0.0069] |
| 40 | [-3.2951, 0.1958] | [-0.1354, -0.0373] | [-0.1017, -0.0417] | [-0.0714, 0.0043] |
| 60 | [-3.2163, 0.128] | [-0.1362, -0.0347] | [-0.0986, -0.0439] | [-0.0721, 0.0028] |

### Costos: la cartera direccional y su CONTRARIA (lo que H1 implica), bloque 20

| pb por lado | direccional (pp/día) | contraria (pp/día) |
|---|---|---|
| 0 | -0.0845 [-0.1391, -0.0329] | 0.0845 [0.0329, 0.1391] |
| 5 | -0.1845 [-0.2391, -0.1329] | -0.0155 [-0.0671, 0.0391] (contiene el cero) |
| 10 | -0.2845 [-0.3391, -0.2329] | -0.1155 [-0.1671, -0.0609] |
| 25 | -0.5845 [-0.6391, -0.5329] | -0.4155 [-0.4671, -0.3609] |

Punto muerto de la contraria: **4.23 pb por lado**; Sharpe por período de la contraria 0.0714; DSR por N: {'14': 0.82, '29': 0.724, '100': 0.549, '160': 0.485} (V = 1/T (teórica); N incluye el registro de la máquina; 25 pb por lado = la vara de la casa). La contraria muere por costos y por multiplicidad: es la mitad que cierra el argumento de no capturabilidad.

### Robustez (bloque 20)

- q medio dejando un año fuera: sin 2018: [-0.1385, -0.0307]; sin 2019: [-0.1589, -0.0413]; sin 2020: [-0.1352, -0.0255]; sin 2021: [-0.1318, -0.0241]; sin 2022: [-0.1391, -0.0174]; sin 2023: [-0.1555, -0.0311]
- q medio dejando un ticker fuera: sin 000660.KS: [-0.122, -0.0203]; sin 005930.KS: [-0.139, -0.0291]; sin 2330.TW: [-0.1499, -0.0379]; sin 3436.T: [-0.1325, -0.0312]; sin 4063.T: [-0.1486, -0.0405]; sin 6857.T: [-0.1343, -0.03]; sin 8035.T: [-0.1329, -0.0286]; sin IFX.DE: [-0.1564, -0.0404]
- q medio por ticker (heterogéneo: sólo los que excluyen el cero pierden por sí solos): 000660.KS -0.1937 [-0.2996, -0.0926]; 005930.KS -0.1 [-0.1689, -0.0333]; 2330.TW -0.0292 [-0.0944, 0.0375] (contiene el cero); 3436.T -0.1111 [-0.2065, -0.0193]; 4063.T -0.0202 [-0.0999, 0.0543] (contiene el cero); 6857.T -0.104 [-0.1944, -0.0137]; 8035.T -0.1168 [-0.2065, -0.0298]; IFX.DE -0.0077 [-0.1236, 0.1043] (contiene el cero)
- q medio winsorizado al 0,5%: -0.086 [-0.1409, -0.035]

### Por exchange (Fráncfort no es contemporáneo de Asia)

| exchange | filas | ventaja gap (pp) | ventaja sesión (pp) | q medio (pp) | pendiente sesión~sorpresa |
|---|---|---|---|---|---|
| XETR | 1343 | 3.8719 [0.2978, 7.3734] | 0.4468 [-3.4252, 4.3931] (contiene el cero) | -0.0077 [-0.1222, 0.1033] (contiene el cero) | -0.0839 [-0.1741, -0.0017] |
| XKRX | 2468 | 16.41 [13.0026, 19.8797] | -1.4992 [-4.564, 1.454] (contiene el cero) | -0.1468 [-0.2328, -0.0689] | -0.0256 [-0.1028, 0.0576] (contiene el cero) |
| XTAI | 1225 | 16.1633 [12.4061, 20.2449] | 4.0816 [0.2449, 7.9184] | -0.0292 [-0.0913, 0.0348] (contiene el cero) | -0.0344 [-0.1161, 0.0519] (contiene el cero) |
| XTKS | 5110 | 21.7221 [18.9144, 24.5844] | -3.3659 [-6.1572, -0.7426] | -0.0879 [-0.1633, -0.0149] | -0.0143 [-0.0736, 0.0481] (contiene el cero) |

## Años de PRUEBA: 4715 filas, 643 fechas

### H1 · estructural: el gap se acierta, la sesión no se captura

| cantidad | punto | IC95 (fechas) |
|---|---|---|
| ventaja_direccional_gap_pp | 15.5885 | [12.2853, 18.9333] |
| ventaja_direccional_sesion_pp | -2.7359 | [-5.5051, -0.0212] |
| retorno_medio_cartera_sesion_pp | -0.1139 | [-0.2081, -0.026] |
| retorno_medio_si_el_gap_fuera_operable_pp | 1.0273 | [0.8584, 1.2177] — **NO EJECUTABLE: exige comprar al cierre local ANTES de que exista el cierre de NY; su Sharpe/DSR saturan y no son un aprobado** |
| retorno_medio_siempre_largo_sesion_pp | 0.0914 | [0.0056, 0.1789] |
| fraccion_aciertos_gap | 0.7116 | [0.6868, 0.7354] |

- McNemar gap: modelo 71.16% (Wilson filas [69.8, 72.4]) vs base 55.57%, b = 1369, c = 634, McNemar p = 1.8984787050194342e-60 — p y Wilson de FILAS: optimistas por clustering de día (unidad = fecha)
- McNemar sesión: modelo 47.38% (Wilson filas [46.0, 48.8]) vs base 50.12%, b = 937, c = 1066, McNemar p = 0.004236105541895307 — p y Wilson de FILAS: optimistas por clustering de día (unidad = fecha)

### H2 · asimetría de magnitud

- Fracción de aciertos del gap: 0.7116 [0.6868, 0.7354]; contribución al retorno medio de la cartera: aciertos -0.0847 [-0.1519, -0.0201] pp, errores -0.0293 [-0.0739, 0.0113] (contiene el cero) pp.
- Diferencia E[q|acierto] − E[q|error]: -0.0175 [-0.1517, 0.1309] (contiene el cero) pp.
- **Veredicto H2:** REFUTADA EN SU PREMISA: los aciertos pierden más que los errores (signo contrario al postulado); la diferencia no se distingue de cero. El criterio original aplicado literalmente habría dado un FALSO POSITIVO por aritmética de signos.
- q medio dado acierto: -0.119 [-0.2177, -0.0283]; dado error: -0.1015 [-0.2452, 0.0385] (contiene el cero).
- Signos: q|acierto −, q|error −. Razón |E[q|error]| / |E[q|acierto]| (nulo 1, umbral 1,5): 0.8528 [0.0542, 3.5157] (contiene el nulo 1.0); IC contiene ±1.5 — el criterio «≥ 1,5» aplicado literalmente daría un FALSO POSITIVO (E[q|acierto] ≤ 0 vuelve trivial la desigualdad).

### H3 · sobrerreacción (pendiente < 0) o deriva (> 0) de la sesión sobre la sorpresa

- Pendiente sesión ~ sorpresa (gap − β·SOX; β congelada del ajuste): -0.03 [-0.0909, 0.0277] (contiene el cero); IC no contiene ±0.1, todo el IC bajo el umbral
- Cortes de tercil de s: [-0.3581, 0.4241] (CONGELADOS del ajuste)
- Pendiente sesión ~ gap: -0.0465 [-0.0911, -0.0004]; IC no contiene ±0.1, todo el IC bajo el umbral
- Sesión media por tercil de sorpresa: bajo 0.0946 [-0.0362, 0.2245] (contiene el cero); medio 0.0638 [-0.0639, 0.1993] (contiene el cero); alto 0.1059 [-0.0144, 0.2399] (contiene el cero); diferencia alto − bajo: 0.0113 [-0.1442, 0.1699] (contiene el cero)
- sesión ≡ total − gap por identidad exacta (sin Open independiente): la pendiente sesión~gap es indistinguible de la atenuación −Var(ε)/Var(g) por error de medición del gap (testigos de dos añadas: gaps del 2-sep, cierres del 26-ago).
- **Veredicto H3:** No se detecta relación de la sesión con la sorpresa respecto de β (IC contiene el cero). Sobre el gap crudo la pendiente es negativa pero confundida con error de medición y su irrelevancia (|pendiente| < 0,1) sólo se establece donde TODO el IC queda bajo 0,1.

### Sensibilidad al bloque del bootstrap (IC95 por bloque de 1/5/10/20/40/60 fechas)

| bloque | ventaja sesión (pp) | q medio (pp) | pendiente sesión~gap | pendiente sesión~sorpresa |
|---|---|---|---|---|
| 1 | [-5.447, -0.1705] | [-0.2122, -0.0167] | [-0.103, 0.0101] | [-0.1001, 0.0398] |
| 5 | [-5.3262, 0.022] | [-0.2028, -0.0195] | [-0.0994, 0.0094] | [-0.0951, 0.0379] |
| 10 | [-5.5051, -0.0212] | [-0.2081, -0.026] | [-0.0911, -0.0004] | [-0.0909, 0.0277] |
| 20 | [-5.5929, 0.0419] | [-0.1989, -0.0315] | [-0.0853, -0.0071] | [-0.0863, 0.025] |
| 40 | [-5.7012, 0.2321] | [-0.1909, -0.0391] | [-0.0835, -0.009] | [-0.0877, 0.0245] |
| 60 | [-5.9592, 0.4266] | [-0.1885, -0.0352] | [-0.0832, -0.0109] | [-0.0862, 0.023] |

### Costos: la cartera direccional y su CONTRARIA (lo que H1 implica), bloque 20

| pb por lado | direccional (pp/día) | contraria (pp/día) |
|---|---|---|
| 0 | -0.1139 [-0.1989, -0.0315] | 0.1139 [0.0315, 0.1989] |
| 5 | -0.2139 [-0.2989, -0.1315] | 0.0139 [-0.0685, 0.0989] (contiene el cero) |
| 10 | -0.3139 [-0.3989, -0.2315] | -0.0861 [-0.1685, -0.0011] |
| 25 | -0.6139 [-0.6989, -0.5315] | -0.3861 [-0.4685, -0.3011] |

Punto muerto de la contraria: **5.7 pb por lado**; Sharpe por período de la contraria 0.0906; DSR por N: {'14': 0.712, '29': 0.594, '100': 0.408, '160': 0.347} (V = 1/T (teórica); N incluye el registro de la máquina; 25 pb por lado = la vara de la casa). La contraria muere por costos y por multiplicidad: es la mitad que cierra el argumento de no capturabilidad.

### Robustez (bloque 20)

- q medio dejando un año fuera: sin 2024: [-0.2296, -0.0124]; sin 2025: [-0.2627, -0.0234]; sin 2026: [-0.1728, -0.0079]
- q medio dejando un ticker fuera: sin 000660.KS: [-0.1919, -0.0283]; sin 005930.KS: [-0.1829, -0.0133]; sin 2330.TW: [-0.2175, -0.0373]; sin 3436.T: [-0.2032, -0.0332]; sin 4063.T: [-0.2224, -0.0415]; sin 6857.T: [-0.1778, -0.0153]; sin 8035.T: [-0.1881, -0.0224]; sin IFX.DE: [-0.2248, -0.0389]
- q medio por ticker (heterogéneo: sólo los que excluyen el cero pierden por sí solos): 000660.KS -0.1409 [-0.3515, 0.0612] (contiene el cero); 005930.KS -0.2267 [-0.3824, -0.0842]; 2330.TW -0.015 [-0.1092, 0.0728] (contiene el cero); 3436.T -0.0989 [-0.291, 0.0921] (contiene el cero); 4063.T -0.0013 [-0.113, 0.1022] (contiene el cero); 6857.T -0.2355 [-0.4402, -0.0487]; 8035.T -0.185 [-0.3489, -0.0188]; IFX.DE -0.0081 [-0.1794, 0.1619] (contiene el cero)
- q medio winsorizado al 0,5%: -0.1109 [-0.1919, -0.0302]

### Por exchange (Fráncfort no es contemporáneo de Asia)

| exchange | filas | ventaja gap (pp) | ventaja sesión (pp) | q medio (pp) | pendiente sesión~sorpresa |
|---|---|---|---|---|---|
| XETR | 622 | 6.2701 [1.4469, 10.9365] | 0.8039 [-4.3408, 6.2701] (contiene el cero) | -0.0081 [-0.1912, 0.1761] (contiene el cero) | -0.1748 [-0.3663, 0.0699] (contiene el cero) |
| XKRX | 1156 | 16.955 [12.4352, 21.5029] | -5.8824 [-10.6716, -1.3793] | -0.1833 [-0.356, -0.03] | 0.0129 [-0.0521, 0.0748] (contiene el cero) |
| XTAI | 543 | 16.0221 [10.4972, 21.3628] | -1.6575 [-6.814, 3.4991] (contiene el cero) | -0.015 [-0.1082, 0.0716] (contiene el cero) | -0.0019 [-0.0836, 0.0892] (contiene el cero) |
| XTKS | 2394 | 17.2515 [13.3442, 21.0834] | -2.381 [-6.028, 1.298] (contiene el cero) | -0.1304 [-0.25, -0.0147] | -0.0272 [-0.0947, 0.0502] (contiene el cero) |

## Colisión de procedencia con la cifra canónica de disipación

signo crudo del SOX sobre toda la ventana reconstruida (incluye fechas selladas, reconstruidas desde testigos, no desde senales.db) — NO es la cifra canónica del README (modelo 4.6.0, n = 14.618) — ventana ['2018-09-06', '2026-08-25'], 15198 filas.

| exchange | ventaja gap signo-SOX (pp) | McNemar |
|---|---|---|
| XETR | 4.7264 [1.8905, 7.5622] | b = 509, c = 414, p = 0.0019744574694399086 |
| XKRX | 16.6352 [13.7148, 19.4145] | b = 1167, c = 550, p = 5.475040376740103e-50 |
| XTAI | 16.0951 [12.8872, 19.3031] | b = 560, c = 269, p = 7.338181199044576e-24 |
| XTKS | 20.3885 [18.0916, 22.7569] | b = 2524, c = 960, p = 1.6424535296098583e-154 |

El README publica Fráncfort **+2,5 pp, p = 0,111** con el MODELO 4.6.0 reconstruido (n = 14.618): otra población y otro predictor. No es contradicción; es procedencia distinta, y se dice acá para que la portada no quede inconsistente.

## Intentos del DSR

Intervalos publicados: ajuste 52, prueba 51, total **107**. un intento por intervalo publicado (la casa yerra hacia arriba); el 14 declarado a mano queda retirado.

