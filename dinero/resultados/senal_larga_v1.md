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

## Resultado

Las dos métricas van con **la misma firmeza**: cuál es la primaria
depende de la enmienda V1-bis, que espera firma. `✓` marca un intervalo
que **no** contiene el cero.

| Espec. | h | muestra | MAE modelo vs cero (pp) | Ganancia de MAE | Ganancia de CRPS | Dirección vs climatología | Ganancia de dirección |
|---|---:|---|---|---|---|---|---|
| **L1** | 20 | 5131 filas / 733 fechas | 8.885 vs 9.185 | +0.299 pp<br>[-0.122, +0.697] | +0.002 <br>[-0.001, +0.005] | 63.4 % vs 65.7 %<br>(5131 filas) | -2.339 pp<br>[-4.522, -0.429] ✓ |
| **L1** | 60 | 4851 filas / 693 fechas | 19.026 vs 20.956 | +1.931 pp<br>[-0.511, +4.150] | +0.017 <br>[+0.000, +0.032] ✓ | 70.8 % vs 70.8 %<br>(4851 filas)<br>**signo constante** | +0.000 pp<br>[+0.000, +0.000] |
| **L2** | 20 | 5131 filas / 733 fechas | 5.339 vs 5.351 | +0.011 pp<br>[-0.007, +0.030] | +0.000 <br>[-0.000, +0.000] | 51.6 % vs 51.3 %<br>(5131 filas) | +0.273 pp<br>[-4.658, +4.775] |
| **L2** | 60 | 4851 filas / 693 fechas | 11.670 vs 11.933 | +0.263 pp<br>[+0.080, +0.467] ✓ | +0.002 <br>[+0.000, +0.003] ✓ | 57.8 % vs 55.7 %<br>(4851 filas) | +2.061 pp<br>[-4.742, +10.226] |
| **L3** | 20 | 5131 filas / 733 fechas | 8.699 vs 9.185 | +0.486 pp<br>[+0.076, +0.880] ✓ | +0.003 <br>[+0.001, +0.006] ✓ | 65.7 % vs 65.7 %<br>(5131 filas)<br>**signo constante** | +0.000 pp<br>[+0.000, +0.000] |
| **L3** | 60 | 4851 filas / 693 fechas | 18.685 vs 20.956 | +2.272 pp<br>[-0.234, +4.728] | +0.020 <br>[+0.002, +0.038] ✓ | 70.8 % vs 70.8 %<br>(4851 filas)<br>**signo constante** | +0.000 pp<br>[+0.000, +0.000] |

## La tercera vara: climatología causal — **AGREGADA DESPUÉS DE VER EL RESULTADO**

Hay que decirlo primero y sin adorno: **esta sección se agregó después**
de leer la tabla de arriba. El pre-registro §5 declaraba dos varas —
predecir cero y la línea base aburrida— y la de arriba es la que estaba
declarada. Se agrega una tercera porque la de arriba es débil por una
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
| **L1** | 20 | 8.885 vs 8.697 (+2.22 pp) | -0.188 pp<br>[-0.336, -0.039] ✗ | -0.001 <br>[-0.002, -0.000] ✗ |
| **L1** | 60 | 19.026 vs 18.837 (+7.04 pp) | -0.189 pp<br>[-0.447, +0.078] | -0.002 <br>[-0.004, +0.000] |
| **L2** | 20 | 5.339 vs 5.350 (-0.05 pp) | +0.010 pp<br>[-0.008, +0.029] | +0.000 <br>[-0.000, +0.000] |
| **L2** | 60 | 11.670 vs 11.899 (-0.33 pp) | +0.229 pp<br>[+0.054, +0.424] ✓ | +0.002 <br>[+0.000, +0.003] ✓ |
| **L3** | 20 | 8.699 vs 8.697 (+2.22 pp) | -0.002 pp<br>[-0.056, +0.045] | +0.000 <br>[-0.000, +0.000] |
| **L3** | 60 | 18.685 vs 18.837 (+7.04 pp) | +0.152 pp<br>[-0.589, +0.908] | +0.002 <br>[-0.004, +0.007] |

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

- **L2 a 60 días en MAE:** +0.229, IC [+0.054, +0.424].
- **L2 a 60 días en CRPS:** +0.002, IC [+0.000, +0.003].

Y pierden contra la constante, con intervalo enteramente por debajo
del cero: L1 a 20 días en MAE, L1 a 20 días en CRPS.

### Lo que hay que decir de la métrica de dirección

En L1 a 60 días, L3 a 20 días, L3 a 60 días **la predicción nunca cambia de signo**: el modelo dice «sube»
todos los días del período de prueba. Su acierto direccional es
idéntico al de la climatología por construcción, y la ganancia de
+0,000 pp con intervalo [0, 0] **no es un empate: es una métrica
vacía**. Publicar ese cero como si fuera un resultado sería el mismo
error que publicar un PSR saturado en 1,0000 como si fuera certeza.

Y **L1 a 20 días acierta MENOS que la climatología**: 63.4 % contra 65.7 %, -2.339 pp con IC [-4.522, -0.429], que no
contiene el cero. Es un resultado negativo, y va con la misma
firmeza con que se publicaría uno positivo.

### La conclusión

De las 6 celdas (tres especificaciones × dos
horizontes), **1 le gana a la climatología causal** y el
resto no, o pierde. La forma simple de la hipótesis —el contagio
directo, L1— **está refutada por su propia regla pre-registrada**.

Lo que queda en pie es chico y hay que decir de qué tamaño: la mejor
celda mejora el MAE en 0.229 pp sobre una base de 11.9 pp, o sea del orden del **2 %**
relativo. La dirección, en esa misma celda, no se distingue del cero.

**Esto no autoriza nada.** Tres razones, todas medidas en esta misma
corrida:

1. Esta página tiene **24 contrastes** (3 especificaciones × 2
   horizontes × 2 varas × 2 métricas). La cuenta en papel del bloque 4
   midió que un diseño así produce un intervalo que excluye el cero en
   el **21 % de los casos con una señal que no tiene información**.
2. El pre-registro del riel (`dinero/preregistro_dinero.md` §2.5) exige
   que un positivo sobreviva **ablación de la ventana que lo sostiene**
   —del tipo R2, que hoy descalifica al propio campeón del riel de
   medición— y el dictamen del adversario. Ninguna de las dos cosas se
   hizo acá.
3. Los sesgos que no se pudieron corregir —supervivencia, la fuente no
   point-in-time, `VRT` como SPAC durante el 17,8 % de la muestra—
   **empujan todos en dirección optimista**, y son del orden de la
   mejora medida.

## Lo que este bloque NO puede concluir, declarado antes de correrlo

- **El DSR sale NO INTERPRETABLE pase lo que pase.** A 60 días hábiles
  sobre 8 años quedan del orden de 33 observaciones no solapadas por par;
  no hay potencia. Se declara y no se imprime un número que mentiría.
- **Los datos no son point-in-time.** La fuente reajusta la historia
  hacia atrás por splits y dividendos; `GEMELO/resultados/ventana_larga.md`
  midió la contaminación en el riel de medición (198 filas comunes,
  91,4 % de coincidencia, máximo 31,2 pp) y va en dirección optimista.
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
