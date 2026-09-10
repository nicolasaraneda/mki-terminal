# El instrumento del riel de dinero contra una verdad conocida — bloque 1, corrida 11 (PROPUESTA)

> **PROPUESTA — bloque 1 de la corrida 11; hasta el dictamen del estadistico-adversario.** Dictamen del `estadistico-adversario` del 8-sep: sostiene con exigencias (aplicadas y re-corridas; las cifras re-corridas no volvieron a pasar por él). Generado 2026-09-09T02:53:45.069542+00:00 por `python -m GEMELO.simulador.instrumento_dinero`. Declaración previa en `GEMELO/resultados/bitacora_11.md` (bloque 1), escrita antes de correr.
>
> **SIMULADO.** Ninguna cifra de esta página es un resultado sobre datos reales; ninguna entra al README. Intentos del DSR: 0.

## Qué se prueba

- **Instrumento:** dinero.contabilidad.comparar (bootstrap circular de bloques de 4 semanas, 2000 réplicas, α = 0.05) + regla §2.3 del pre-registro: IC excluye 0 y punto > 0. Se llama la función tal como está en el código.
- **Verdad:** d_t = δ + σ·ε_t, ε t de Student nu=4 estandarizada, AR(1) ρ. La base son retornos semanales reales de SMH remuestreados iid (irrelevantes para el estadístico).
- **Magnitudes declaradas antes:** δ ∈ [0.0, 0.25, 0.5, 1.0] pp/semana (dinero/preregistro_dinero.md §2.1, tabla del 7-sep-2026). Horizontes [52, 104, 156] semanas. 2000 réplicas por celda, semilla 20260908, semilla del bootstrap por réplica.
- **σ medida, no supuesta:** **2.704 pp/semana**, IC95 por bootstrap de semanas [2.4773, 2.8951], banda entre sorteos de cartera [1.9108, 4.0162] (200 carteras de K = 4 entre 33 operables, 156 semanas, 2023-09-05 a 2026-09-04). La σ = 2,54 de la tabla §2.1 del pre-registro NO se usa: es cifra de la cuenta con fuga, retirada.
- Precios: `cierres_congelados.csv`, sha256 `69ca7283ae18fd37…`, congelado 2026-09-07T01:47:34+00:00.

## Veredicto, por el criterio escrito antes

**Criterio:** piso de Wilson de la detección bajo δ > 0 supera el techo de Wilson de la falsa detección bajo δ = 0, celda base a 52 semanas, para al menos una de las tres magnitudes declaradas.

Falsa detección bajo δ = 0 (celda base, 52 semanas): 0.046 [0.038, 0.057].

| δ (pp/sem) | piso Wilson detección | techo Wilson falsa detección | ¿discrimina? |
|---|---|---|---|
| +0.25 | 0.122 | 0.057 | **SÍ** |
| +0.50 | 0.323 | 0.057 | **SÍ** |
| +1.00 | 0.772 | 0.057 | **SÍ** |

**El instrumento DISCRIMINA.** Consecuencia: la corrida sigue. Y **NO está calibrado a α = 0,05**: tamaño bilateral 0.086 [0.074, 0.099] contra 0,05 a 52 semanas (brazo de calibración, abajo).

## Calibración (brazo agregado DESPUÉS de ver el resultado, exigencia A1 del adversario)

El criterio de fallo pre-declarado sólo podía fallar por falta de potencia, nunca por
descalibración. Este brazo se agrega a posteriori y se declara así: usable a α = 0,05 sólo
si el Wilson del tamaño bilateral contiene 0,05 y el de la cobertura contiene 0,95. La
potencia cerrada se recomputa al tamaño real medido (exigencia A5): la brecha
«simulada > cerrada» de la tabla de abajo es exactamente el tamaño inflado.

| semanas | tamaño bilateral [Wilson] | cobertura IC media [Wilson] | cobertura IC sd [Wilson] | ¿usable a α = 0,05? | α real | potencia cerrada al α real (0,25 / 0,50 / 1,00) | MDE80 pp/semana a α 0,05 [banda σ] | MDE80 al α real [banda σ] | pp/año suma / capitalizado (α 0,05) |
|---|---|---|---|---|---|---|---|---|---|
| 52 | 0.086 [0.074, 0.099] | 0.914 [0.901, 0.926] | 0.783 [0.765, 0.801] | **NO** | 0.086 | 0.147 / 0.351 / 0.829 | **1.05** [0.7424, 1.5603] | 0.96 [0.678, 1.425] | 55 / 72 |
| 104 | 0.067 [0.056, 0.078] | 0.933 [0.922, 0.944] | 0.821 [0.803, 0.837] | **NO** | 0.067 | 0.186 / 0.520 / 0.974 | **0.74** [0.5249, 1.1033] | 0.71 [0.5015, 1.0541] | 39 / 47 |
| 156 | 0.064 [0.054, 0.075] | 0.936 [0.925, 0.946] | 0.850 [0.833, 0.865] | **NO** | 0.064 | 0.242 / 0.675 / 0.997 | **0.61** [0.4286, 0.9009] | 0.58 [0.4126, 0.8673] | 32 / 37 |

**La corrida 11 habría cruzado este brazo a 52 semanas**: el instrumento discrimina pero no
está calibrado a α = 0,05 (exigencia A1, declarado). El MDE80 dice en número lo que el
pre-registro decía en prosa: a 52 semanas la regla §2.3 sólo detecta una ventaja del orden de
1.05 pp/semana (banda [0.7424, 1.5603] según la σ del sorteo; 0.96 al α real), o sea 55 pp/año como suma aritmética y 72 pp capitalizados: una ventaja así no es plausible con datos
públicos. La banda del MDE viene de la banda entre sorteos de σ y no es un IC de muestreo (D5, D6).
La σ de estos MDE es la ANCLA del simulador (2.704 pp/semana), no la σ realizada de la cuenta v2.

**Contraste con la σ realizada de la cuenta reconstruida** (exigencias A6/C6): la cuenta v2 da σ = 2.336 pp/semana, IC [1.9952, 2.6686] (156 semanas, `conservador` vs `SMH`); el ancla 2.704 queda por encima del techo de ese IC, o sea el ancla es CONSERVADORA (menos potencia, criterio más difícil) y es un
proxy estructural distinto (cartera estática de 4, siempre invertida, sin caja ni rotación).
La cobertura del IC de la sd (columna de arriba) es lo que decide si ese intervalo de σ se
puede usar: el bloque 1 original validó sólo el IC de la media.

**ρ medido** (exigencia A4): AC1 de la diferencia semanal, mediana 0.0 con banda entre sorteos [-0.1904, 0.1637]: el barrido a ρ = 0,2 cubre el borde de lo compatible.

## La mitad nula y la mitad con ventaja, en el mismo cuadro

Detección = IC excluye 0 y punto > 0 (regla §2.3). Excluye 0 = bilateral, cualquier signo (el tamaño del test en la fila δ = 0). Cobertura = el IC contiene la δ verdadera. Segunda ruta = potencia normal cerrada Φ(δ√T/σ − 1,96) con la misma σ y ρ = 0.

### Celda base (σ medida, ρ = 0), 52, 104 y 156 semanas

| δ | σ | ρ | semanas | **detección** [Wilson] | excluye 0 [Wilson] | cobertura [Wilson] | cobertura IC sd | punto ± sd | ancho medio | normal cerrada (α 0,05) |
|---|---|---|---|---|---|---|---|---|---|---|
| +0.00 | 2.70 | 0.0 | 52 | **0.046** [0.038, 0.057] | 0.086 [0.074, 0.099] | 0.914 [0.901, 0.926] | 0.783 | -0.006 ± 0.378 | 1.36 | 0.025 |
| +0.25 | 2.70 | 0.0 | 52 | **0.136** [0.122, 0.152] | 0.142 [0.128, 0.159] | 0.921 [0.908, 0.932] | 0.784 | +0.249 ± 0.376 | 1.37 | 0.098 |
| +0.50 | 2.70 | 0.0 | 52 | **0.344** [0.323, 0.365] | 0.345 [0.325, 0.367] | 0.921 [0.909, 0.932] | 0.772 | +0.494 ± 0.375 | 1.36 | 0.265 |
| +1.00 | 2.70 | 0.0 | 52 | **0.790** [0.772, 0.808] | 0.790 [0.772, 0.808] | 0.924 [0.912, 0.935] | 0.780 | +0.993 ± 0.370 | 1.36 | 0.760 |
| +0.00 | 2.70 | 0.0 | 104 | **0.034** [0.026, 0.042] | 0.067 [0.056, 0.078] | 0.933 [0.922, 0.944] | 0.821 | -0.003 ± 0.267 | 1.00 | 0.025 |
| +0.25 | 2.70 | 0.0 | 104 | **0.182** [0.166, 0.200] | 0.185 [0.169, 0.203] | 0.938 [0.927, 0.948] | 0.821 | +0.251 ± 0.258 | 1.00 | 0.154 |
| +0.50 | 2.70 | 0.0 | 104 | **0.501** [0.480, 0.523] | 0.501 [0.480, 0.523] | 0.936 [0.925, 0.946] | 0.835 | +0.489 ± 0.262 | 1.00 | 0.470 |
| +1.00 | 2.70 | 0.0 | 104 | **0.957** [0.947, 0.965] | 0.957 [0.947, 0.965] | 0.941 [0.929, 0.950] | 0.819 | +1.002 ± 0.266 | 1.00 | 0.965 |
| +0.00 | 2.70 | 0.0 | 156 | **0.032** [0.025, 0.040] | 0.064 [0.054, 0.075] | 0.936 [0.925, 0.946] | 0.850 | +0.004 ± 0.221 | 0.83 | 0.025 |
| +0.25 | 2.70 | 0.0 | 156 | **0.227** [0.209, 0.245] | 0.228 [0.210, 0.246] | 0.934 [0.923, 0.945] | 0.853 | +0.242 ± 0.222 | 0.83 | 0.210 |
| +0.50 | 2.70 | 0.0 | 156 | **0.648** [0.627, 0.669] | 0.648 [0.627, 0.669] | 0.935 [0.924, 0.945] | 0.856 | +0.493 ± 0.222 | 0.83 | 0.637 |
| +1.00 | 2.70 | 0.0 | 156 | **0.991** [0.985, 0.994] | 0.991 [0.985, 0.994] | 0.946 [0.935, 0.955] | 0.839 | +1.001 ± 0.214 | 0.83 | 0.996 |

### Sensibilidad: σ a la mitad, 52 semanas

| δ | σ | ρ | semanas | **detección** [Wilson] | excluye 0 [Wilson] | cobertura [Wilson] | cobertura IC sd | punto ± sd | ancho medio | normal cerrada (α 0,05) |
|---|---|---|---|---|---|---|---|---|---|---|
| +0.00 | 1.35 | 0.0 | 52 | **0.038** [0.031, 0.048] | 0.075 [0.064, 0.087] | 0.925 [0.913, 0.936] | 0.776 | -0.005 ± 0.185 | 0.68 | 0.025 |
| +0.25 | 1.35 | 0.0 | 52 | **0.336** [0.316, 0.357] | 0.337 [0.317, 0.358] | 0.910 [0.897, 0.922] | 0.787 | +0.244 ± 0.192 | 0.68 | 0.265 |
| +0.50 | 1.35 | 0.0 | 52 | **0.794** [0.776, 0.811] | 0.794 [0.776, 0.811] | 0.931 [0.919, 0.941] | 0.777 | +0.500 ± 0.184 | 0.68 | 0.760 |
| +1.00 | 1.35 | 0.0 | 52 | **0.993** [0.988, 0.996] | 0.993 [0.988, 0.996] | 0.922 [0.909, 0.933] | 0.788 | +0.997 ± 0.185 | 0.69 | 1.000 |

### Sensibilidad: σ al doble, 52 semanas

| δ | σ | ρ | semanas | **detección** [Wilson] | excluye 0 [Wilson] | cobertura [Wilson] | cobertura IC sd | punto ± sd | ancho medio | normal cerrada (α 0,05) |
|---|---|---|---|---|---|---|---|---|---|---|
| +0.00 | 5.41 | 0.0 | 52 | **0.047** [0.039, 0.057] | 0.092 [0.081, 0.106] | 0.907 [0.894, 0.919] | 0.774 | -0.027 ± 0.773 | 2.73 | 0.025 |
| +0.25 | 5.41 | 0.0 | 52 | **0.078** [0.067, 0.091] | 0.099 [0.086, 0.112] | 0.916 [0.903, 0.927] | 0.796 | +0.254 ± 0.748 | 2.74 | 0.052 |
| +0.50 | 5.41 | 0.0 | 52 | **0.136** [0.122, 0.152] | 0.140 [0.125, 0.156] | 0.925 [0.913, 0.936] | 0.774 | +0.500 ± 0.746 | 2.73 | 0.098 |
| +1.00 | 5.41 | 0.0 | 52 | **0.345** [0.324, 0.366] | 0.346 [0.326, 0.368] | 0.920 [0.907, 0.931] | 0.789 | +0.992 ± 0.741 | 2.74 | 0.265 |

### Sensibilidad: dependencia entre semanas ρ = 0,2, 52 semanas

| δ | σ | ρ | semanas | **detección** [Wilson] | excluye 0 [Wilson] | cobertura [Wilson] | cobertura IC sd | punto ± sd | ancho medio | normal cerrada (α 0,05) |
|---|---|---|---|---|---|---|---|---|---|---|
| +0.00 | 2.70 | 0.2 | 52 | **0.054** [0.045, 0.065] | 0.101 [0.089, 0.115] | 0.899 [0.885, 0.911] | 0.773 | +0.004 ± 0.460 | 1.58 | 0.025 |
| +0.25 | 2.70 | 0.2 | 52 | **0.134** [0.119, 0.149] | 0.144 [0.130, 0.161] | 0.894 [0.880, 0.907] | 0.765 | +0.230 ± 0.454 | 1.56 | 0.098 |
| +0.50 | 2.70 | 0.2 | 52 | **0.296** [0.277, 0.317] | 0.299 [0.280, 0.320] | 0.909 [0.896, 0.921] | 0.764 | +0.500 ± 0.453 | 1.56 | 0.265 |
| +1.00 | 2.70 | 0.2 | 52 | **0.676** [0.656, 0.697] | 0.676 [0.656, 0.697] | 0.907 [0.894, 0.919] | 0.760 | +0.985 ± 0.451 | 1.56 | 0.760 |

## Lectura, y lo que no se puede leer

- **Tamaño bajo la nula** (bilateral, 52 semanas): 0.086 [0.074, 0.099] contra un nominal de 0,05; cobertura 0.914 [0.901, 0.926] contra 0,95. Si el intervalo de la cobertura excluye 0,95, el instrumento sub- o sobre-cubre y eso se declara, no se corrige acá (la elección del estimador después de ver la cobertura es un grado de libertad).
- δ = +0.25: detección 0.136 [0.122, 0.152] contra 0.098 de la normal cerrada.
- δ = +0.50: detección 0.344 [0.323, 0.365] contra 0.265 de la normal cerrada.
- δ = +1.00: detección 0.790 [0.772, 0.808] contra 0.760 de la normal cerrada.
- **Regla (exigencia A7):** el largo del bloque del bootstrap NO se barre después de haber visto la cobertura sin declararlo como grado de libertad; cambiar el estimador es decisión de Nicolás (`espera_firma.md` §50).
- **Lo que esto NO valida:** el camino que produce las series de valor (cuenta_papel, correr_estrategia, valorizar): eso es de los bloques 2 y 3. Una σ medida sobre carteras sorteadas de 4 instrumentos es un proxy declarado de la dispersión de una cuenta que todavía no existe sin fuga; por eso se barre en 0,5σ y 2σ.
- La fila ρ = 0,2 dice qué pasa si las semanas no son intercambiables; el bloque de 4 semanas del instrumento es lo que debería absorberlo, y el cuadro mide cuánto absorbe.
