# El instrumento contra un patrón conocido — Frente A v2 (PROPUESTA, octava corrida)

> PROPUESTA — Frente A v2, octava corrida; reescrito tras el dictamen del adversario. Generado 2026-09-02T18:12:04.958314+00:00. Pre-registro: `GEMELO/preregistro/frente_A.md`.
> **Versión 2, reescrita el 2-sep-2026 después del dictamen del `estadistico-adversario`** sobre la
> versión 1 (NO SOSTIENE tal como estaba escrita): semilla de bootstrap por réplica, cuatro estimadores
> de IC, matriz bajo la alternativa, DSR en las dos unidades con tamaño teórico, comparación pareada
> con `horizonte.md`, y la sensibilidad a ν, c y a la dependencia entre días que el pre-registro
> prometía y la v1 no entregó.

**Ancla de calibración:** ancla = cadena LOCAL a CORTE_REGLA_FIRMADA (31-ago), NO la ventana canónica publicada (n = 248, cadena compuesta): n = 246 filas en 35 días,
ICC 0.3925, DEFF 3.5595, n efectivo 69.11. sd de la suma por día
3.489, n̄ 7.029. Registro de intentos 100
(N del 5.1: 106).

## Generadores (verdad medida 8 veces a 200.000 días, con intervalo)

| δ objetivo | b | c | verdad δ (pp) | IC95 verdad | ICC objetivo | ICC logrado | fuera de tol. 0,005 |
|---|---|---|---|---|---|---|---|
| 0.0 | 0.5156 | 5.5312 | **-0.135** | [-0.203, -0.068] | 0.3925 | 0.4014 | **SÍ** |
| 0.05 | 0.875 | 5.1562 | **4.987** | [4.917, 5.057] | 0.3925 | 0.4034 | **SÍ** |
| 0.065 | 0.9688 | 4.9688 | **6.323** | [6.256, 6.39] | 0.3925 | 0.3987 | **SÍ** |
| 0.09 | 1.1562 | 4.6875 | **8.967** | [8.904, 9.031] | 0.3925 | 0.405 | **SÍ** |

**Piso idiosincrático (30% de σ):** en los tickers marcados la parte común β²(b²·esc² + c²) excede
la σ total sellada y el piso ata: la sd simulada del gap queda por ENCIMA de la real e **infla la
dependencia intra-día simulada** (dirección del sesgo: hace ver el estimador de clúster más necesario
de lo que los datos justifican).

| generador | ticker | σ sellada | √común | piso ata | sd simulada | exceso |
|---|---|---|---|---|---|---|
| 0.0 | 000660.KS | 7.169 | 5.327 | no | 7.169 | 0.0% |
| 0.0 | 005930.KS | 5.751 | 4.035 | no | 5.751 | 0.0% |
| 0.0 | 2330.TW | 1.981 | 2.104 | **SÍ** | 2.186 | 10.4% |
| 0.0 | 3436.T | 4.879 | 4.34 | no | 4.879 | 0.0% |
| 0.0 | 4063.T | 1.662 | 1.988 | **SÍ** | 2.049 | 23.3% |
| 0.0 | 6857.T | 4.226 | 3.668 | no | 4.226 | 0.0% |
| 0.0 | 8035.T | 3.968 | 3.608 | no | 3.968 | 0.0% |
| 0.0 | IFX.DE | 2.487 | 0.533 | no | 2.487 | -0.0% |
| 0.05 | 2330.TW | 1.981 | 2.146 | **SÍ** | 2.227 | 12.4% |
| 0.05 | 4063.T | 1.662 | 2.028 | **SÍ** | 2.088 | 25.6% |
| 0.065 | 2330.TW | 1.981 | 2.145 | **SÍ** | 2.226 | 12.4% |
| 0.065 | 4063.T | 1.662 | 2.027 | **SÍ** | 2.087 | 25.6% |
| 0.09 | 2330.TW | 1.981 | 2.193 | **SÍ** | 2.272 | 14.7% |
| 0.09 | 4063.T | 1.662 | 2.072 | **SÍ** | 2.131 | 28.2% |

## A1 · Cobertura del IC95 (semilla de bootstrap por réplica)

**Criterio de refutación congelado en el pre-registro:** «cobertura del IC de día < 93% con IC que
excluya 95%» refuta la hipótesis de que el instrumento de clúster está calibrado. Evaluado sobre el
estimador percentil, COMPUTADO celda a celda (no afirmado): δ = -0.135 pp → cobertura 0.9308 [0.926, 0.936]: NO se cumple literalmente (cobertura ≥ 0,93 aunque el IC excluye 0,95); δ = 8.967 pp → cobertura 0.9325 [0.927, 0.937]: NO se cumple literalmente (cobertura ≥ 0,93 aunque el IC excluye 0,95).
El adversario, con otro flujo de réplicas, midió 0,9271/0,9275 y el criterio SÍ se cumplía. **Un criterio
cuya decisión cambia con la semilla al tercer decimal es un criterio en el filo, y se dice así.** Lo que
no depende de la semilla: el percentil sub-cubre (IC que excluye 0,95 en las dos celdas y en las dos
mediciones) y la t de clúster con gl = k−1 cubre ~0,95. La corrección es cambiar el estimador; la
elección del estimador DESPUÉS de ver la cobertura es un grado de libertad que se declara como eje
(`bifurcaciones.NO_EJES`).

| verdad δ | réplicas | percentil | IC95 | básico | IC95 | **t de clúster** | IC95 | iid filas | IC95 |
|---|---|---|---|---|---|---|---|---|---|
| -0.135 pp | 10000 | 0.9308 | [0.926, 0.936] | 0.9317 | [0.927, 0.936] | **0.9491** | [0.945, 0.953] | **0.6885** | [0.679, 0.698] |
| 8.967 pp | 10000 | 0.9325 | [0.927, 0.937] | 0.9334 | [0.928, 0.938] | **0.9508** | [0.946, 0.955] | **0.6879** | [0.679, 0.697] |

Anchos medios (pp): δ=-0.135: percentil 32.42, t de clúster 34.49, iid 17.5; δ=8.967: percentil 32.21, t de clúster 34.27, iid 17.36

Percentil-t: medido por el adversario (0,9335), no arregla; BCa: no probado.

## A2 · Las 192 celdas bajo la nula Y bajo la alternativa

| verdad | réplicas | media de celdas p<0,05 | tasa por celda [IC sobre réplicas] | **P(0 de 192)** | IC95 | P(≥1) |
|---|---|---|---|---|---|---|
| delta_0 | 300 | 10.57 | 0.0551 [0.0381, 0.0756] | **0.7467** | [0.695, 0.793] | 0.2533 |
| delta_6.5pp | 200 | 21.52 | 0.1121 [0.0822, 0.1439] | **0.63** | [0.561, 0.694] | 0.37 |
| delta_9pp | 200 | 31.1 | 0.162 [0.1276, 0.1998] | **0.465** | [0.397, 0.534] | 0.535 |

**La frase que sobrevive:** «0 de 192» es prácticamente no informativo: la nula lo produce el 74.7% de las veces y una ventaja verdadera de ~9 pp el 46.5% — cociente de verosimilitudes **1.61**. La v1 decía «la mitad de las veces»: era falsa.
Salvedad: es la nula INTERCAMBIABLE (qué tickers faltan y qué fechas caen en R2 se sortean), no la
dependencia real entre ejes y datos.

## A3 · DSR bajo la nula: las dos unidades

`anualizado` = el defecto (Sharpe·√252 con n = T, lo que los dos llamadores hacían hasta el 2-sep);
`por período` = la corrección. La regla V5 (DSR de al menos 0,95) no tiene tamaño 5%: su tamaño teórico gaussiano
es P(max_N Z > E[max_N Z] + 1,645). La elección de V es de primer orden a N chico.

| N | T | anualizado (defecto) | IC95 | **por período, V incl. ganador** | IC95 | V sin ganador | V = 1/T | tamaño teórico |
|---|---|---|---|---|---|---|---|---|
| 100 | 518 | 0.2657 | [0.252, 0.28] | **0.0013** | [0.001, 0.003] | 0.0027 | 0.0022 | 0.00163 |
| 106 | 518 | 0.2617 | [0.248, 0.276] | **0.0005** | [0.0, 0.002] | 0.0018 | 0.0022 | 0.00158 |
| 106 | 250 | 0.2275 | [0.215, 0.241] | **0.0005** | [0.0, 0.002] | 0.0018 | 0.001 | 0.00158 |
| 9 | 518 | 0.3862 | [0.371, 0.401] | **0.0005** | [0.0, 0.002] | 0.016 | 0.007 | 0.00751 |
| 9 | 30 | 0.1883 | [0.176, 0.201] | **0.0005** | [0.0, 0.002] | 0.0143 | 0.0055 | 0.00751 |

## A4 · Potencia: simulador, `horizonte.md` y una tercera ruta cerrada

| δ verdad | días | simulador | IC95 | normal cerrada (sd real) | horizonte.md |
|---|---|---|---|---|---|
| 4.99 | 35 | 0.072 | [0.052, 0.098] | 0.092 | 0.08966666666666667 |
| 4.99 | 73 | 0.136 | [0.109, 0.169] | 0.138 | 0.14133333333333334 |
| 4.99 | 125 | 0.184 | [0.152, 0.22] | 0.203 | 0.20133333333333334 |
| 4.99 | 250 | 0.314 | [0.275, 0.356] | 0.357 | 0.36433333333333334 |
| 4.99 | 475 | 0.532 | [0.488, 0.575] | 0.593 | — |
| 4.99 | 803 | 0.794 | [0.756, 0.827] | 0.814 | — |
| 6.32 | 35 | 0.092 | [0.07, 0.121] | 0.121 | 0.11366666666666667 |
| 6.32 | 73 | 0.194 | [0.162, 0.231] | 0.201 | 0.208 |
| 6.32 | 125 | 0.276 | [0.239, 0.317] | 0.31 | 0.30233333333333334 |
| 6.32 | 250 | 0.5 | [0.456, 0.544] | 0.544 | 0.5483333333333333 |
| 6.32 | 475 | 0.762 | [0.723, 0.797] | 0.814 | — |
| 6.32 | 803 | 0.954 | [0.932, 0.969] | 0.96 | — |
| 8.97 | 35 | 0.158 | [0.129, 0.193] | 0.189 | 0.16733333333333333 |
| 8.97 | 73 | 0.306 | [0.267, 0.348] | 0.341 | 0.355 |
| 8.97 | 125 | 0.508 | [0.464, 0.552] | 0.527 | 0.5296666666666666 |
| 8.97 | 250 | 0.78 | [0.742, 0.814] | 0.818 | 0.8196666666666667 |
| 8.97 | 475 | 0.956 | [0.934, 0.971] | 0.977 | — |
| 8.97 | 803 | 0.996 | [0.986, 0.999] | 0.999 | — |

**Comparación pareada** (12 celdas): simulador por debajo en 12, por encima en 0; McNemar exacto p = 0.000488; diferencia media horizonte − simulador **2.67 pp** [1.84, 3.55].
**No son dos rutas independientes:** la potencia del test de signo por día es función de un escalar
(δ·n̄·√D / sd de la suma por día) al que el simulador fue calibrado; la normal cerrada lo reproduce con
sólo dos números reales. La brecha sistemática tiene causa: `horizonte.potencia_simulada` suma un δ
CONSTANTE a cada fila; el simulador entrega δ por el canal de información (concentrado en los días de
|S| grande), que es lo fiel. **La tabla de potencia de `horizonte.md`, las fechas de horizonte derivadas
y la «potencia 0,36 [0,34, 0,37]» del 25-oct son OPTIMISTAS** por la diferencia medida arriba.

## A5 · Sensibilidad del DGP (lo que el pre-registro prometió)

**Seis puntos del DGP que la v1 no declaraba:** (1) el shock U entra por las MISMAS β que S — la covarianza
intra-día es de rango 1 con las cargas que el campeón conoce: la forma más benigna de clúster inexplicado;
(2) no había dependencia ENTRE días (S, U, ε iid en d) — la intercambiabilidad exacta que el bootstrap de
día y la permutación necesitan; medida abajo con AR(1); (3) la β verdadera es la que usa el campeón, sin
error de estimación (la rodante real de 120 sesiones es autocorrelada); (4) el piso del 30% ata en los
tickers de la tabla de arriba; (5) el ICC logrado queda fuera de la tolerancia 0,005 de `calibrar_c` en
los generadores marcados (la bisección se detiene en el ruido de Monte Carlo); (6) el pre-registro decía
«c y la escala de S ajustados al ICC y al SE de día»: el código calibra SÓLO c al ICC; la escala del SOX
se lee del sello y el SE de día no se persigue.

**Puntos que siguen sin intervalo, declarados:** `icc_sim` (medido una vez a 80.000 días) y `escala_sox`, que se lee
del sello sobre las fechas con `sox_usado_pct` (una fracción de las 35: ~15% de error estándar) y entra al DGP como punto.

| ν | verdad (pp) | percentil | t de clúster | iid |
|---|---|---|---|---|
| 4 | -0.113 | 0.9277 [0.918, 0.936] | 0.946 [0.937, 0.954] | 0.7037 |
| 6 | 0.286 | 0.9277 [0.918, 0.936] | 0.9457 [0.937, 0.953] | 0.678 |
| 10 | 0.641 | 0.9253 [0.915, 0.934] | 0.941 [0.932, 0.949] | 0.6817 |
| 30 | 0.747 | 0.929 [0.919, 0.938] | 0.9493 [0.941, 0.957] | 0.684 |

| factor de c | c | ICC simulado | verdad (pp) | percentil | t de clúster |
|---|---|---|---|---|---|
| 0.5 | 2.7656 | 0.1358 | -0.067 | 0.9297 | 0.9533 |
| 1.5 | 8.2969 | 0.5941 | -0.613 | 0.93 | 0.9447 |

**Dependencia entre días (AR(1) en S y U; AC1 real −0,13 ± 0,17, ρ = 0,2 es compatible):**

| ρ | verdad (pp) | percentil | t de clúster | tamaño de la permutación de día | IC95 |
|---|---|---|---|---|---|
| 0.0 | -0.156 | 0.933 | 0.9477 | **0.0473** | [0.04, 0.056] |
| 0.2 | -0.115 | 0.9 | 0.9283 | **0.0613** | [0.053, 0.07] |
| 0.4 | 0.097 | 0.8557 | 0.8863 | **0.1037** | [0.093, 0.115] |

**Lectura:** el simulador publicado no podía detectar el modo de fallo que los datos dejan abierto
(dependencia entre días) porque asumía que no existe. Con ρ > 0 el tamaño de la permutación de día sube por
encima de 0,05 y la cobertura cae: es un riesgo DECLARADO del instrumento, no resuelto.

## Lo que este frente SÍ sostiene

- El estimador iid de filas cubre ~0,70 donde promete 0,95: inservible, sin margen.
- El defecto de unidades del PSR/DSR es real, verificado contra el código y la teoría; la corrección es
  aritméticamente correcta y su tamaño por período coincide con el teórico.
- El δ logrado se re-mide a 200.000 días en vez de suponerse igual al objetivo.
- El percentil de día con k = 35 sub-cubre ~2,3 pp; la t de clúster con gl = k−1 corrige.
