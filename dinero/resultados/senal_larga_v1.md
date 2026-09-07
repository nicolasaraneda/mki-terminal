# Señal larga v1 — resultado

> **PROPUESTA hasta el dictamen de `estadistico-adversario`.** Ninguna
> cifra de esta página entra al README ni sostiene ninguna afirmación
> del proyecto. No hay ninguna fila SELLADA de este riel: el track
> record prospectivo es del riel de medición, no de éste.

Pre-registrado en `GEMELO/preregistro/senal_larga_v1.md`, **commiteado
antes del cómputo** (commit `e368dad`). Tres especificaciones declaradas
por nombre, dos horizontes, agregación sobre todos los pares adyacentes
de la cadena. Registro de intentos del riel largo: **3**.

Generado 2026-09-07 UTC por `python -m dinero.senal_larga_reporte`.

## Procedimiento

- Ajuste **2018-09-05 → 2023-09-04**, prueba **2023-09-05 → 2026-09-04**, congelados antes de mirar.
- **Un solo ajuste y una sola evaluación**, no walk-forward expansivo:
  la auditoría mostró que el expansivo metía hasta el 36 % del último
  ajuste dentro del período de prueba mientras el reporte afirmaba lo
  contrario. Errata E2 del pre-registro, escrita antes de medir.
- Embargo: **5 días MÁS el horizonte MÁS el retardo de implementación**. Con etiquetas de *h* días solapadas, ajustar con
  un par cuya etiqueta llega más allá del inicio de la prueba es leer el
  futuro sin que ninguna guarda de «datos ≤ t» se queje.
- **Retardo de implementación: 1 día.** Se
  decide con el cierre de *t* y se entra al cierre de *t+1*. El auditor
  midió que este día mueve la etiqueta 3,6–4,0 pp de media, del mismo
  orden que el umbral de señal del juego conservador (3,49 pp).
- Composición de los eslabones: por **cobertura ≥ 98 % del período de
  ajuste**, decidida al principio de la muestra. La v1 la decidía con el
  último precio del archivo y eso era fuga de selección demostrada
  (errata E1: cambiaba el 42,9 % de las filas del panel).
- Sólo `dinero/datos/cierres_congelados.csv`. **Ninguna descarga.**
- Intervalos: bootstrap circular de bloques sobre **fechas de emisión**,
  bloque = horizonte, 2000 réplicas, semilla 20260907, α = 0.05.
- **Bloques efectivos del bootstrap** (h=20: **36.6 bloques**, h=60: **11.6 bloques**). Se declara porque
  un bootstrap de bloques con once bloques y pico no tiene la cobertura
  que su etiqueta del 95 % promete: medido sobre ruido iid con esta
  misma máquina, el ancho del intervalo varía entre 0,67 y 1,29 veces
  el que corresponde. Toda la inferencia a 60 días descansa sobre esos
  once bloques.

## Resultado

Las dos métricas van con **la misma firmeza**: cuál es la primaria
depende de la enmienda V1-bis, que espera firma. `✓` marca un intervalo
que **no** contiene el cero.

| Espec. | h | muestra | MAE modelo vs cero (pp) | Ganancia de MAE | Ganancia de CRPS | Dirección vs climatología | Ganancia de dirección |
|---|---:|---|---|---|---|---|---|
| **L1** | 20 | 5131 filas / 733 fechas | 8.885 vs 9.185 | +0.299 pp<br>[-0.122, +0.697] | +0.210 pp<br>[-0.072, +0.482] | 63.4 % vs 65.7 %<br>(5131 filas) | -2.339 pp<br>[-4.522, -0.429] ✓ |
| **L1** | 60 | 4851 filas / 693 fechas | 19.026 vs 20.956 | +1.931 pp<br>[-0.511, +4.150] | +1.684 pp<br>[+0.019, +3.213] ✓ | 70.8 % vs 70.8 %<br>(4851 filas)<br>**signo constante** | +0.000 pp<br>[+0.000, +0.000] |
| **L2** | 20 | 5131 filas / 733 fechas | 5.339 vs 5.351 | +0.011 pp<br>[-0.007, +0.030] | +0.010 pp<br>[-0.004, +0.025] | 51.6 % vs 51.3 %<br>(5131 filas) | +0.273 pp<br>[-4.658, +4.775] |
| **L2** | 60 | 4851 filas / 693 fechas | 11.670 vs 11.933 | +0.263 pp<br>[+0.080, +0.467] ✓ | +0.180 pp<br>[+0.041, +0.322] ✓ | 57.8 % vs 55.7 %<br>(4851 filas) | +2.061 pp<br>[-4.742, +10.226] |
| **L3** | 20 | 5131 filas / 733 fechas | 8.699 vs 9.185 | +0.486 pp<br>[+0.076, +0.880] ✓ | +0.337 pp<br>[+0.061, +0.609] ✓ | 65.7 % vs 65.7 %<br>(5131 filas)<br>**signo constante** | +0.000 pp<br>[+0.000, +0.000] |
| **L3** | 60 | 4851 filas / 693 fechas | 18.685 vs 20.956 | +2.272 pp<br>[-0.234, +4.728] | +2.011 pp<br>[+0.246, +3.830] ✓ | 70.8 % vs 70.8 %<br>(4851 filas)<br>**signo constante** | +0.000 pp<br>[+0.000, +0.000] |

## La tercera vara: climatología causal — **AGREGADA DESPUÉS DE VER EL RESULTADO**

Hay que decirlo primero y sin adorno: **esta sección se agregó después**
de leer la tabla de arriba. El pre-registro §5 declaraba dos varas de
MAGNITUD —predecir cero y la línea base aburrida— y la de arriba es la
primera. **La segunda no se corrió en esta corrida** (ver la conclusión).
El §5 declaraba además, en su último párrafo, la climatología **para
DIRECCIÓN**: eso estaba pre-registrado. Lo que se agrega post-hoc acá es
la climatología de **magnitud**. Se agrega una tercera porque la de arriba es débil por una
razón que el propio adversario del proyecto ya había dictaminado antes de
esta corrida (`espera_firma.md` §30): **«predecir cero» no es neutro en un
mercado que sube**. Cero está sistemáticamente por debajo de la media
incondicional, así que cualquier modelo que aprenda el intercepto le gana
sin saber nada de la cadena.

La climatología causal es esa media: el promedio de la etiqueta **en el
período de ajuste**, en el espacio propio de cada especificación
(residual para L2, crudo para L1 y L3). Es una constante, no mira el
futuro, y es la vara que hay que ganarle para poder decir «la cadena
anticipa».

Se agrega una vara MÁS DIFÍCIL después de ver un resultado favorable. La
dirección de la enmienda importa: endurecer la prueba tras un positivo no
es lo mismo que ablandarla tras un negativo, y por eso se publica en vez
de reescribir el pre-registro. `✗` marca un intervalo enteramente por
DEBAJO del cero: el modelo pierde contra la constante.

| Espec. | h | MAE modelo vs climatología (constante) | Ganancia de MAE | Ganancia de CRPS |
|---|---:|---|---|---|
| **L1** | 20 | 8.885 vs 8.697 (+2.22 pp) | -0.188 pp<br>[-0.336, -0.039] ✗ | -0.126 pp<br>[-0.236, -0.015] ✗ |
| **L1** | 60 | 19.026 vs 18.837 (+7.04 pp) | -0.189 pp<br>[-0.447, +0.078] | -0.167 pp<br>[-0.380, +0.035] |
| **L2** | 20 | 5.339 vs 5.350 (-0.05 pp) | +0.010 pp<br>[-0.008, +0.029] | +0.010 pp<br>[-0.005, +0.025] |
| **L2** | 60 | 11.670 vs 11.899 (-0.33 pp) | +0.229 pp<br>[+0.054, +0.424] ✓ | +0.170 pp<br>[+0.033, +0.323] ✓ |
| **L3** | 20 | 8.699 vs 8.697 (+2.22 pp) | -0.002 pp<br>[-0.056, +0.045] | +0.001 pp<br>[-0.039, +0.034] |
| **L3** | 60 | 18.685 vs 18.837 (+7.04 pp) | +0.152 pp<br>[-0.589, +0.908] | +0.159 pp<br>[-0.400, +0.730] |

## Veredicto

### Lo que dice la regla pre-registrada §6, aplicada tal cual

**L1 queda REFUTADA.** La regla dice: «si L1 no le gana a predecir
cero en MAE, con intervalo que excluya el cero, en ninguno de los dos
horizontes, la forma simple de la hipótesis queda refutada». Es
exactamente lo que pasó:
- L1 a 20 días: ganancia +0.299 pp, IC [-0.122, +0.697] — contiene el cero.
- L1 a 60 días: ganancia +1.931 pp, IC [-0.511, +4.150] — contiene el cero.

El contagio directo entre eslabones adyacentes, que es la forma más
simple de la hipótesis y la que había que descartar antes de
complicar nada, **no aparece**.

### Lo que sobrevive a la vara dura

Antes de nombrar ninguna: **estos intervalos son SIN corregir por
multiplicidad**, y la sección siguiente muestra qué queda de ellos
cuando se corrige. Se listan igual, porque esconderlos sería elegir
qué mostrar según el resultado.

- **L2 a 60 días en MAE:** +0.229, IC [+0.054, +0.424] (sin corregir).
- **L2 a 60 días en CRPS:** +0.170, IC [+0.033, +0.323] (sin corregir).

Y pierden contra la constante, con intervalo enteramente por debajo
del cero: L1 a 20 días en MAE, L1 a 20 días en CRPS.

### Multiplicidad: la familia completa son 30 contrastes, no 24

La cuenta vieja de esta página decía 24 (3 especificaciones × 2
horizontes × 2 varas × 2 métricas) y dejaba **los seis contrastes de
dirección fuera de su propia corrección de multiplicidad**. `medir()`
produce cinco intervalos por celda: la familia son 30.
Con Holm sobre esa familia, que no supone independencia entre
contrastes —y acá no la hay, comparten filas, fechas y
especificaciones—:

| Contraste | p crudo | p de Holm | ¿cruza α = 0,05? |
|---|---:|---:|---|
| L2 h=60 MAE vs cero | 0.0030 | 0.0900 | no |
| L2 h=60 CRPS vs cero | 0.0060 | 0.1740 | no |
| L2 h=60 MAE vs climatologia | 0.0060 | 0.1740 | no |
| L2 h=60 CRPS vs climatologia | 0.0060 | 0.1740 | no |
| L1 h=20 direccion vs climatologia | 0.0090 | 0.2340 | no |
| L1 h=20 MAE vs climatologia | 0.0130 | 0.3250 | no |
| L3 h=20 MAE vs cero | 0.0170 | 0.4080 | no |
| L3 h=20 CRPS vs cero | 0.0180 | 0.4140 | no |
| L3 h=60 CRPS vs cero | 0.0220 | 0.4840 | no |
| L1 h=20 CRPS vs climatologia | 0.0250 | 0.5250 | no |
| L1 h=60 CRPS vs cero | 0.0470 | 0.9400 | no |
| L3 h=60 MAE vs cero | 0.0830 | 1.0000 | no |
| L1 h=60 CRPS vs climatologia | 0.1110 | 1.0000 | no |
| L1 h=60 MAE vs cero | 0.1310 | 1.0000 | no |
| L1 h=20 CRPS vs cero | 0.1330 | 1.0000 | no |
| L1 h=20 MAE vs cero | 0.1480 | 1.0000 | no |
| L1 h=60 MAE vs climatologia | 0.1520 | 1.0000 | no |
| L2 h=20 CRPS vs cero | 0.1710 | 1.0000 | no |
| L2 h=20 CRPS vs climatologia | 0.1920 | 1.0000 | no |
| L2 h=20 MAE vs cero | 0.2450 | 1.0000 | no |
| L2 h=20 MAE vs climatologia | 0.3000 | 1.0000 | no |
| L3 h=60 CRPS vs climatologia | 0.5660 | 1.0000 | no |
| L2 h=60 direccion vs climatologia | 0.6140 | 1.0000 | no |
| L3 h=60 MAE vs climatologia | 0.6550 | 1.0000 | no |
| L2 h=20 direccion vs climatologia | 0.9150 | 1.0000 | no |
| L3 h=20 MAE vs climatologia | 0.9520 | 1.0000 | no |
| L3 h=20 CRPS vs climatologia | 0.9630 | 1.0000 | no |
| L1 h=60 direccion vs climatologia | 1.0000 | 1.0000 | no |
| L3 h=20 direccion vs climatologia | 1.0000 | 1.0000 | no |
| L3 h=60 direccion vs climatologia | 1.0000 | 1.0000 | no |

**Ninguno de los 30 contrastes cruza α = 0,05 bajo
Holm.** Ni los positivos ni los negativos. Es el resultado que
gobierna esta página y va antes que cualquier celda suelta.

Un p de bootstrap con 2000 réplicas no puede bajar de 0.0005: un p que
aparece en ese piso quiere decir «ninguna réplica cruzó», no cero.

### Ablación anual, la que el pre-registro del riel exige

`dinero/preregistro_dinero.md` exige que un positivo sobreviva a sacar
la ventana que lo sostiene. Es la forma exacta del **R2** de
`GEMELO/DISEÑO.md`. La v1 de esta página admitía no haberla corrido;
acá está corrida, sobre la ganancia de MAE contra la climatología, para
**todas** las celdas y no sólo para las que convienen.

| Espec. | h | año sacado | ganancia sin ese año | ¿excluye el cero? | sólo ese año |
|---|---:|---|---|---|---|
| **L1** | 20 | 2023 | -0.172 pp [-0.341, -0.005] (651 fechas) | sí | -0.317 pp (82 fechas) |
| **L1** | 20 | 2024 | -0.271 pp [-0.479, -0.068] (481 fechas) | sí | -0.032 pp (252 fechas) |
| **L1** | 20 | 2025 | -0.140 pp [-0.325, +0.037] (483 fechas) | no, **contiene el cero** | -0.282 pp (250 fechas) |
| **L1** | 20 | 2026 | -0.179 pp [-0.317, -0.031] (584 fechas) | sí | -0.226 pp (149 fechas) |
| **L1** | 60 | 2023 | -0.233 pp [-0.491, +0.030] (611 fechas) | no, **contiene el cero** | +0.138 pp (82 fechas) |
| **L1** | 60 | 2024 | -0.210 pp [-0.599, +0.174] (441 fechas) | no, **contiene el cero** | -0.152 pp (252 fechas) |
| **L1** | 60 | 2025 | -0.132 pp [-0.440, +0.180] (443 fechas) | no, **contiene el cero** | -0.290 pp (250 fechas) |
| **L1** | 60 | 2026 | -0.171 pp [-0.369, +0.038] (584 fechas) | no, **contiene el cero** | -0.288 pp (109 fechas) |
| **L2** | 20 | 2023 | +0.012 pp [-0.009, +0.033] (651 fechas) | no, **contiene el cero** | -0.008 pp (82 fechas) |
| **L2** | 20 | 2024 | +0.018 pp [-0.008, +0.045] (481 fechas) | no, **contiene el cero** | -0.006 pp (252 fechas) |
| **L2** | 20 | 2025 | +0.007 pp [-0.017, +0.032] (483 fechas) | no, **contiene el cero** | +0.017 pp (250 fechas) |
| **L2** | 20 | 2026 | +0.004 pp [-0.010, +0.019] (584 fechas) | no, **contiene el cero** | +0.036 pp (149 fechas) |
| **L2** | 60 | 2023 | +0.262 pp [+0.063, +0.486] (611 fechas) | sí | -0.017 pp (82 fechas) |
| **L2** | 60 | 2024 | +0.226 pp [-0.011, +0.497] (441 fechas) | no, **contiene el cero** | +0.234 pp (252 fechas) |
| **L2** | 60 | 2025 | +0.211 pp [+0.019, +0.418] (443 fechas) | sí | +0.262 pp (250 fechas) |
| **L2** | 60 | 2026 | +0.211 pp [+0.033, +0.412] (584 fechas) | sí | +0.329 pp (109 fechas) |
| **L3** | 20 | 2023 | +0.013 pp [-0.037, +0.064] (651 fechas) | no, **contiene el cero** | -0.120 pp (82 fechas) |
| **L3** | 20 | 2024 | +0.010 pp [-0.062, +0.083] (481 fechas) | no, **contiene el cero** | -0.025 pp (252 fechas) |
| **L3** | 20 | 2025 | -0.040 pp [-0.108, +0.024] (483 fechas) | no, **contiene el cero** | +0.071 pp (250 fechas) |
| **L3** | 20 | 2026 | +0.003 pp [-0.046, +0.049] (584 fechas) | no, **contiene el cero** | -0.020 pp (149 fechas) |
| **L3** | 60 | 2023 | +0.323 pp [-0.453, +1.141] (611 fechas) | no, **contiene el cero** | -1.119 pp (82 fechas) |
| **L3** | 60 | 2024 | +0.183 pp [-0.833, +1.331] (441 fechas) | no, **contiene el cero** | +0.097 pp (252 fechas) |
| **L3** | 60 | 2025 | +0.062 pp [-0.933, +1.181] (443 fechas) | no, **contiene el cero** | +0.312 pp (250 fechas) |
| **L3** | 60 | 2026 | +0.019 pp [-0.491, +0.493] (584 fechas) | no, **contiene el cero** | +0.867 pp (109 fechas) |

**Y ahí se cae.** sacando 2024 del período de prueba, la ganancia de L2 a 60 días pasa a contener el cero.
Es la misma forma que el R2 tiene en el riel de medición: la
significancia cabalga una ventana. **Una celda que necesita un año
concreto para excluir el cero no es un hallazgo, es esa ventana.**

### Lo que hay que decir de la métrica de dirección

En L1 a 60 días, L3 a 20 días, L3 a 60 días **la predicción nunca cambia de signo**: el modelo dice «sube»
todos los días del período de prueba. Su acierto direccional es
idéntico al de la climatología por construcción, y la ganancia de
+0,000 pp con intervalo [0, 0] **no es un empate: es una métrica
vacía**. Publicar ese cero como si fuera un resultado sería el
mismo error que el proyecto ya cometió una vez al publicar un PSR
saturado como si fuera certeza. (Nota de precisión: ese diagnóstico
está **RETIRADO** —`dictamen_08/A.md` A3—: la saturación resultó ser
un **defecto de unidades**, no un hecho de muestra corta, y con la
unidad correcta daba 0,95–0,96. La lección sobrevive; la explicación
que se le ponía, no.)

Y van los discordantes con su McNemar exacto, que la v1 no publicaba.
La regla de la casa pide **b, c y p siempre**, porque un p de filas al
lado de un intervalo de fecha que contiene el cero es el síntoma de que
las filas de un mismo día no son observaciones independientes: es
exactamente lo que le pasa al riel de medición.

| Espec. | h | b (gana el modelo) | c (gana la climatología) | McNemar exacto (filas) | IC de fecha |
|---|---:|---:|---:|---:|---|
| **L1** | 20 | 64 | 184 | 1.235e-14 | [-4.522, -0.429] — excluye el cero |
| **L1** | 60 | 0 | 0 | 1 | [+0.000, +0.000] — **contiene el cero** |
| **L2** | 20 | 965 | 951 | 0.7665 | [-4.658, +4.775] — **contiene el cero** |
| **L2** | 60 | 771 | 671 | 0.009109 | [-4.742, +10.226] — **contiene el cero** |
| **L3** | 20 | 0 | 0 | 1 | [+0.000, +0.000] — **contiene el cero** |
| **L3** | 60 | 0 | 0 | 1 | [+0.000, +0.000] — **contiene el cero** |

**L2 a 60 días es el caso a mirar:** McNemar de filas 0.009109 contra un intervalo de fecha que
contiene el cero. Manda el intervalo de fecha. La fila no es la
unidad de observación de este diseño.

Y **L1 a 20 días acierta MENOS que la climatología**: 63.4 % contra 65.7 %, -2.339 pp con IC [-4.522, -0.429], que no
contiene el cero **sin corregir**. Pero la simetría vale para el
negativo igual que para el positivo: bajo Holm sobre la familia
completa su p ajustado es 0.2340, o sea que **tampoco es
distinguible de cero**. La refutación de L1 no depende de este
número: depende de la regla §6, que sólo mira MAE contra cero y se
cumple sola.

### La conclusión

La forma simple de la hipótesis —el contagio directo, L1— **está
refutada por su propia regla pre-registrada**. Eso se sostiene solo
y no depende de nada de lo que sigue.

De las 6 celdas, **1 le gana a la climatología
causal con el intervalo sin corregir**. Y esa celda **no sobrevive**
a las dos pruebas que esta misma página le corre:

1. **Multiplicidad.** Sobre la familia completa de 30 contrastes, ninguno cruza α = 0,05 bajo
   Holm. El positivo tampoco.
2. **Ablación anual.** Sacando 2024 del período de prueba, L2 a 60 días pasa a contener el cero. La ventaja cabalga una ventana,
   que es la forma exacta del R2.

Así que la lectura correcta de esta página **no es «sobrevive una
celda»**: es que, corregido por su propia familia y sometido a la
ablación que el pre-registro del riel exige, **no queda ninguna
afirmación positiva en pie**. La magnitud, además, es del orden del
2 % relativo, y la dirección de esa misma celda no se distingue del
cero ni siquiera sin corregir.

**Esto no autoriza nada.** Cuatro razones, todas medidas en esta
misma corrida:

1. La familia de esta página son **30 contrastes**,
   y ninguno pasa Holm. La cuenta vieja decía 24 y dejaba los seis
   de dirección fuera de su propia corrección.
2. La ablación anual, corrida acá y no diferida, muestra de qué
   ventana depende el único positivo sin corregir.
3. **La segunda vara pre-registrada NO se evaluó.** El §5 del
   pre-registro declara dos: predecir cero (la de arriba) y **la
   línea base aburrida, aporte semanal a `SMH`, a la que se llega
   pasando la señal por `dinero/decision.py` y la cuenta en papel**.
   Esa segunda no se corrió en esta corrida, y mientras no se corra
   la regla de refutación del §6 («si ninguna de las tres supera a
   ninguna de las dos varas») y el criterio M4 del pre-registro del
   riel **no se pueden dar por leídos**. Se agrega que hoy la cuenta
   en papel está RETIRADA por fuga demostrada, así que esa vara no
   se puede correr hasta que la cuenta se reconstruya.
4. Los sesgos que no se pudieron corregir —supervivencia, la fuente
   no point-in-time, `VRT` como SPAC durante el 17,8 % de la
   muestra— **empujan todos en dirección optimista**, y son del
   orden de la mejora medida.

Sobre la tasa de falsos positivos: la v1 de esta página citaba acá
el «21 % de los casos» de la cuenta en papel. Se retira por dos
razones. Primera, era de **otro diseño** (24 comparaciones
semanales de carteras que comparten sorteo y flujo de caja, con
bloques de 4 semanas), no de esta página, que son 30 contrastes con bloques por fecha de emisión;
la tasa de tipo I de ESTE diseño **no está medida**. Segunda, la
cuenta en papel tiene **fuga temporal demostrada**
(`dictamen_10/auditor_lookahead.md`, F1 a F4) y ninguna de sus
cifras se puede citar. Lo que ocupa su lugar no es una tasa
prestada: es la corrección de Holm, computada sobre esta familia.

## Lo que este bloque NO puede concluir, declarado antes de correrlo

- **El DSR sale NO INTERPRETABLE pase lo que pase.** A 60 días hábiles
  sobre 8 años quedan del orden de 33 observaciones no solapadas por par;
  no hay potencia. Se declara y no se imprime un número que mentiría.
- **Los datos no son point-in-time.** La fuente reajusta la historia
  hacia atrás por splits y dividendos. El proyecto midió esa
  contaminación en el riel de medición y, con la clave correcta
  (`sesion_objetivo`), dio **100 % de coincidencia sobre 214 filas, 0
  diferencias**. La cifra de «91,4 % sobre 198 filas» que
  `ventana_larga.md` todavía publica está **RETIRADA desde el
  1-sep-2026** (`GEMELO/cifras_retiradas.md`, `espera_firma.md` §11a):
  salía de cruzar por `[fecha, ticker]` en vez de por la sesión
  objetivo. Eso **no** prueba que la fuente no revise su historia: sólo
  que no la revisó en el tramo auditable de 2026. El sesgo sigue
  declarado y sigue yendo en dirección optimista.
- **Supervivencia, NO corregida.** Los 36 tickers son los que existen
  hoy: ninguna deslistada, ninguna adquirida, ninguna quebrada. El sesgo
  de SELECCIÓN por precio sí se corrigió (errata E1); éste no se puede
  con este archivo.
- **Identidad del instrumento.** `VRT` fue el SPAC GS Acquisition hasta
  feb-2020: durante 358 sesiones (17,8 % de la muestra) su σ diaria fue
  0,59 % contra 3,86 % después. Un tercio de «demanda final» es, en el
  primer quinto del ajuste, un fideicomiso.
- **Fuga por el analista.** Los ocho eslabones, su orden, los pares y las
  tres especificaciones los diseñó alguien que ya vio 2018–2026. Ninguna
  prueba de este repositorio lo detecta; la única defensa es el sellado
  en vivo, y este riel tiene **cero filas selladas**.
