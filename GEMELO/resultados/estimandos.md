# Estimandos alternativos — Frente E (PROPUESTA)

> **PROPUESTA — ningún estimando reemplaza al endpoint congelado sin firma y sin dictamen**

- Generado: 2026-09-02T06:18:23.541115+00:00 · `python GEMELO/SECUENCIAL/estimandos.py`
- IC95 y z por bootstrap de FECHAS enteras (clúster de día). «Días para 0,80» = días × (2,80/z)²: cota inferior optimista con sesgo de ganador, sirve para COMPARAR estimandos, no para prometer fechas.
- **Dictamen del `estadistico-adversario` (2-sep, `dictamen_07/DICTAMEN.md`): E4 y E4' RETIRADOS como estimandos con IC de fecha** — para un parámetro sobre h la unidad de replicación es la bolsa (4, con 2 valores de h): permutación exacta p = 0,231, p mínimo alcanzable 1/13; bootstrap de bolsas IC95 [−5,4, −1,4]. Las filas se conservan sólo como registro de lo que se computó; no son afirmaciones del proyecto. E-1 (E3) entra sólo pre-registrada contra el control lineal.

## ventana sellada viva hasta 2026-08-31 — 261 filas, 37 días

| estimando | punto | IC95 (día) | z | días para 0,80 al efecto observado |
|---|---|---|---|---|
| E0 dirección (endpoint actual), pp | 11.877 | [-4.418, 28.000] | 1.41 | 146 |
| E1 magnitud: |g| − |p−g|, pp | 0.456 | [-0.014, 0.941] | 1.88 | 83 |
| E2 gap capturado − siempre al alza, pp | 1.102 | [-0.026, 2.354] | 1.82 | 88 |
| E3 pendiente g ~ p | 1.421 | [0.648, 2.193] | 3.44 | 25 |
| E4 decaimiento: pp de ventaja por hora — **RETIRADO por dictamen** (unidad de replicación = bolsa; 4 bolsas, 2 valores de h; p mínimo 1/13). IC y z NO admisibles | -0.029 | [-4.256, 3.786] | -0.01 | 1406670 |
| E4' contraste Asia − Fráncfort, pp — **RETIRADO como pendiente**; publicable sólo como comparación de 4 bolsas, no como IC de fecha sobre el mecanismo | 0.518 | [-26.022, 29.545] | 0.04 | 219943 |

| bolsa | h | filas | E0 pp |
|---|---|---|---|
| XKRX | 1.75 | 64 | 6.25 |
| XTKS | 1.75 | 134 | 14.18 |
| XTAI | 2.75 | 28 | 14.29 |
| XETR | 8.75 | 35 | 11.43 |

## ventana larga reconstruida (B2, sep-2024 → ago-2026) — 3865 filas, 518 días

| estimando | punto | IC95 (día) | z | días para 0,80 al efecto observado |
|---|---|---|---|---|
| E0 dirección (endpoint actual), pp | 13.402 | [9.776, 17.020] | 7.35 | 75 |
| E1 magnitud: |g| − |p−g|, pp | 0.306 | [0.222, 0.396] | 6.97 | 84 |
| E2 gap capturado − siempre al alza, pp | 0.804 | [0.585, 1.038] | 7.11 | 80 |
| E3 pendiente g ~ p | 0.987 | [0.823, 1.162] | 11.28 | 32 |
| E4 decaimiento: pp de ventaja por hora — **RETIRADO por dictamen** (unidad de replicación = bolsa; 4 bolsas, 2 valores de h; p mínimo 1/13). IC y z NO admisibles | -1.608 | [-2.452, -0.773] | -3.78 | 284 |
| E4' contraste Asia − Fráncfort, pp — **RETIRADO como pendiente**; publicable sólo como comparación de 4 bolsas, no como IC de fecha sobre el mecanismo | 10.836 | [5.025, 16.685] | 3.68 | 300 |

| bolsa | h | filas | E0 pp |
|---|---|---|---|
| XKRX | 1.75 | 960 | 17.6 |
| XTKS | 1.75 | 1934 | 14.06 |
| XTAI | 2.75 | 468 | 12.18 |
| XETR | 8.75 | 503 | 3.98 |

