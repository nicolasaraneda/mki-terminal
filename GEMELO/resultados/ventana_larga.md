# ⚠ ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1

Es la **evaluación del retador** sobre la ventana larga (Etapa 6.0.0
WS3). El veredicto de la 5.1 es otra cosa y su distinción es precisa:
es el criterio **escalonado capa-contra-capa sobre B0→B5**, con sus
reglas congeladas en el GATE B, y su ejecución es **decisión humana**.

**Aquí NO se calcula el veredicto escalonado ni se emite juicio sobre
B0→B5.** El campeón reconstruido aparece SOLO como término de
comparación del retador.

---

# La ventana real — el mismo experimento con potencia estadística

- Generado: 2026-08-26T03:38:03.838160+00:00
- Ventana: **2018-08-27 → 2026-08-25** · 2076 fechas de emisión · **14711 filas de evaluación**
  (el WS2b tenía 215; esto es **68× más**)

## ⚠ LIMITACIÓN DE PRIMER ORDEN: esto NO es point-in-time

**Yahoo reescribe la historia en silencio.** Sus precios vienen
ajustados, y el ajuste se recalcula con cada dividendo y cada split
**posteriores**: la serie de 2019 que se descarga hoy no es la que
existía en 2019. Una reconstrucción a años vista está contaminada por
esa revisión, y la contaminación va en la dirección optimista.

**Y está MEDIDA, no solo declarada.** Ver la sección siguiente: se
comparan los gaps reconstruidos hoy contra los que el verificador
selló en su momento, fila por fila.

Esto NO es una nota al pie: es la limitación que gobierna la lectura
de todo lo que sigue. La única defensa real contra ella es el sellado
en vivo sobre datos que no existían cuando se escribió el código — que
el proyecto sí tiene, y que es exactamente la ventana de 223 filas del
WS2b. **La ventana larga da potencia; la ventana sellada da validez.**
Ninguna de las dos reemplaza a la otra.

## La contaminación por revisión, medida

Sobre las **198** filas comunes con el track
record sellado, la reconstrucción de hoy **coincide en el 91.4%** (a menos de 0.01 pp) y **difiere en 17**, con un máximo de **31.2212 pp**.

Cada fila que difiere es una revisión silenciosa entre el día del
sello y hoy. Fechas afectadas: 2026-07-29, 2026-08-03, 2026-08-05.

Las mayores diferencias:

| fecha | ticker | gap_pct_sellado | gap_pct_recon | dif |
|---|---|---|---|---|
| 2026-07-29 | 000660.KS | 28.3661 | -2.8551 | 31.2212 |
| 2026-07-29 | 005930.KS | 24.1546 | 2.6379 | 21.5167 |
| 2026-07-29 | 3436.T | 17.5214 | -0.0848 | 17.6062 |
| 2026-07-29 | 8035.T | 13.3997 | -2.0 | 15.3997 |
| 2026-08-05 | 3436.T | 4.5429 | -2.8222 | 7.3651 |

> **Esto NO se corrige.** Las filas selladas jamás se reescriben;
> si alguna resultara errónea, se documenta como errata. Lo que la
> tabla mide es cuánta confianza merece una reconstrucción a años
> vista — y la respuesta es: bastante, pero no toda.

## Parámetros sellados

| Parámetro | Valor |
|---|---|
| **N intentos declarado (DSR)** | **13** |
| Regla de conteo | un intento = (configuración × ventana de evaluación) con resultado reportable |
| Desglose | 6 (B0-B5) + 3 (C1-C3 ventana sellada) + 3 (C1-C3 ventana larga) + 1 (campeón ventana larga) |
| Embargo | 5 días |
| Ventana de entrenamiento | EXPANSIVA (todo el pasado disponible) |
| Alphas de la CV | [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0] |
| Pliegues de la CV temporal | 3 |
| Mínimo de entrenamiento | 250 filas |
| Semilla / bloque / alpha del bootstrap | 20260826 / 20 / 0.05 |
| Años de datos | 8 |
| Sub-ventana para la distribución | 200 filas |
| Campeón | motor.prediccion_apertura_al vía B2Produccion, con serie inyectada más profunda; ventana de betas 120 sesiones (idéntica a producción) |

**El N subió de 9 a 13** porque re-evaluar las mismas tres
configuraciones sobre una ventana distinta produce un segundo conjunto
de resultados publicables entre los cuales se puede elegir — y elegir
entre resultados es lo que el DSR deflacta. La regla se declaró en
`GEMELO/DISEÑO.md` §4.2 bis **antes** de correr nada.

## ASIMETRÍA DECLARADA — no supuesta

El retador entrena con ventana **expansiva** sobre toda la historia
previa; el campeón usa **120 sesiones rodantes**. Es una diferencia
real de maquinaria y parte de lo que se mide. Por eso C1 existe: mismo
insumo que el campeón, maquinaria nueva. **La comparación que responde
la pregunta de la información es C2 vs C1.**

## El catálogo de features NO es constante en la ventana

| feature | desde | hasta | n | cobertura |
|---|---|---|---|---|
| sox_t | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| sox_t1 | 2018-08-29 | 2026-08-26 | 2084 | 0.999 |
| es_ret | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| nq_ret | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| krw_ret | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| twd_ret | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| jpy_ret | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| eurusd_ret | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| ks11_ret | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| twii_ret | 2018-08-28 | 2026-08-26 | 2060 | 0.988 |
| n225_ret | 2018-08-28 | 2026-08-26 | 2083 | 0.999 |
| gdaxi_ret | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| vix_dln | 2018-08-28 | 2026-08-26 | 2085 | 1.0 |
| credit_ratio | 2018-08-27 | 2026-08-26 | 2086 | 1.0 |
| vol_regime | 2019-09-10 | 2026-08-26 | 1815 | 0.87 |

Descartadas por la compuerta del 80%:

| ticker | cobertura |
|---|---|
| ^VIX3M | 0.0 |


## Resultados por configuración

| config | n | acierto_pct | base_pct | ventaja_pp | mcnemar_b01 | mcnemar_b10 | mcnemar_p | mae | crps | sharpe_ls_sin_costos | dias | alpha_mediana | n_train_mediano |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 14711 | 70.6 | 54.2 | 16.4 | 4363 | 1950 | 0.0 | 1.0428 | 0.7921 | 9.296 | 2033 | 300.0 | 7649.0 |
| C2 | 12628 | 72.7 | 54.3 | 18.4 | 3886 | 1564 | 0.0 | 1.0346 | 0.7883 | 9.855 | 1745 | 300.0 | 6549.0 |
| C3 | 10879 | 73.1 | 54.1 | 19.1 | 3408 | 1335 | 0.0 | 0.9879 | 0.7505 | 10.584 | 1520 | 100.0 | 929.0 |
| CAMPEON | 14711 | 70.1 | 54.2 | 15.9 | 4445 | 2106 | 0.0 | 1.0346 | 0.8515 | 9.129 | 2033 |  |  |

## Comparaciones pareadas

| par | n | acierto_a_pct | acierto_b_pct | ventaja_pp | mcnemar | mcnemar_p | mae_a | mae_b | delta_mae | delta_mae_ic | ic_excluye_cero |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C2 vs C1 | 12628 | 72.7 | 71.5 | 1.3 | 1039 vs 879 | 0.0003 | 1.0346 | 1.0588 | 0.0242 | [0.0264, 0.0924] | True |
| C3 vs C1 | 10879 | 73.1 | 71.6 | 1.5 | 1071 vs 907 | 0.0002 | 0.9879 | 1.0581 | 0.0702 | [0.1114, 0.1584] | True |
| C3 vs C2 | 10879 | 73.1 | 73.2 | -0.1 | 545 vs 551 | 0.88 | 0.9879 | 1.0263 | 0.0385 | [0.0788, 0.1135] | True |
| C1 vs CAMPEON | 14711 | 70.6 | 70.1 | 0.5 | 640 vs 566 | 0.0355 | 1.0428 | 1.0346 | -0.0081 | [-0.0464, 0.0156] | False |
| C2 vs CAMPEON | 12628 | 72.7 | 70.9 | 1.9 | 1204 vs 966 | 0.0 | 1.0346 | 1.0497 | 0.0152 | [-0.0062, 0.0554] | False |
| C3 vs CAMPEON | 10879 | 73.1 | 71.1 | 2.1 | 1161 vs 935 | 0.0 | 0.9879 | 1.0463 | 0.0585 | [0.0661, 0.1295] | True |

## R2 con potencia: distribución de la ventaja por sub-ventana

Con siete semanas, excluir una era casi una anécdota. Con años de
datos la pregunta de R2 —¿la ventaja está repartida o vive en unas
pocas ventanas afortunadas?— se responde midiendo la ventaja en
sub-ventanas de 200 filas y mirando su
distribución. `media_sin_la_mejor` y `media_sin_el_mejor_decil` son
la versión con potencia del criterio.

| config | n_subventanas | tam_subventana | ventaja_media_pp | ventaja_mediana_pp | desv_pp | pct_subventanas_positivas | mejor_pp | peor_pp | media_sin_la_mejor_pp | media_sin_el_mejor_decil_pp |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 73 | 200 | 16.41 | 17.5 | 10.08 | 94.5 | 41.5 | -7.5 | 16.06 | 14.55 |
| C2 | 63 | 200 | 18.33 | 17.5 | 9.11 | 100.0 | 40.5 | 2.5 | 17.98 | 16.5 |
| C3 | 54 | 200 | 19.1 | 18.25 | 8.27 | 100.0 | 36.0 | 5.0 | 18.78 | 17.74 |
| CAMPEON | 73 | 200 | 15.9 | 16.0 | 10.21 | 90.4 | 37.0 | -10.0 | 15.61 | 13.98 |

## ⚠ El Sharpe de estas tablas NO es capturable

`sharpe_ls_sin_costos` se construye sobre el **gap**, y el gap es
precisamente lo que NO se puede capturar: es el salto entre el cierre
previo y la apertura, y nadie transa a ese precio. El proyecto ya lo
sabe — por eso su verificador mide el **doble objetivo**: `gap_pct`
responde *¿existe la señal?* y `retorno_real_pct` responde *¿es
capturable?*.

Un Sharpe de dos cifras sobre gaps es **ficción económica**, no un
hallazgo. Se reporta porque el PSR y el DSR necesitan una serie de
retornos, y se marca así para que nadie lo lea como rendimiento. La
prueba económica de verdad es V6 (SMH, 25 pb por lado) y no está
hecha aquí.

## PSR y DSR

Con menos de 60 días de retornos el PSR y el
DSR se reportan como **NO INTERPRETABLE**: un Sharpe anualizado sobre
una muestra diminuta es un artefacto de multiplicar por √252, y el
PSR y el DSR **saturan en 1.0000** — que se leería como que V5 está
superado cuando significa que el instrumento no aplica.

| config | sharpe | dias | interpretable | psr_vs_cero | sr0_deflacionado | dsr | N_intentos | V_intentos |
|---|---|---|---|---|---|---|---|---|
| C1 | 9.296 | 2033 | True | 1.0 | 1.1186 | 1.0 | 13 | 0.4312 |
| C2 | 9.855 | 1745 | True | 1.0 | 1.1186 | 1.0 | 13 | 0.4312 |
| C3 | 10.584 | 1520 | True | 1.0 | 1.1186 | 1.0 | 13 | 0.4312 |
| CAMPEON | 9.129 | 2033 | True | 1.0 | 1.1186 | 1.0 | 13 | 0.4312 |

**`V_intentos` se estima con la varianza de los Sharpe disponibles
aquí**, no con los de B0→B5 (corrida legacy no comparable,
DECISIONES.md §28.5). Un V subestimado da un SR0 menor y un DSR más
alto del que corresponde: la cifra es una cota superior.

**El CRPS usa una predictiva NORMAL**, primera pasada declarada.
`sharpe_ls_sin_costos` es long-short equiponderado **sin costos**: NO
es la prueba del benchmark obligatorio (V6, que exige SMH y 25 pb por
lado).

---
Herramienta de análisis — no constituye asesoría financiera.
Diseño congelado en GEMELO/DISEÑO.md. **No es el veredicto de la 5.1**
y **no calcula el veredicto escalonado de B0→B5.**
