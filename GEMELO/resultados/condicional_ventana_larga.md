# La hipótesis condicional sobre la ventana larga — veredicto

> ## NO REFUTADA, Y MÁS DÉBIL DE LO QUE SUENA — Bajo los criterios congelados sobrevive, pero lo que la sostiene es casi una identidad algebraica, no una condición de mercado.
>
> **La ventaja NO está concentrada: está repartida — hasta un punto.** Quitando el 10% de fechas más favorables quedan **6.569 pp** con IC95 [4.717, 8.379], que excluye el cero; quitando el 20% la ventaja se da vuelta a **-1.937 pp**. El 100% de la ventaja neta vive en el 16.5% de las fechas, contra 0.64% bajo la nula de permutar el signo por fecha: la curva observada es mucho MÁS dispersa que la del azar, no más concentrada.
>
> **Sí hay condiciones que predicen fuera de muestra, y son las de magnitud.** 4 de 7 configuraciones cumplen el §4(a) congelado: `vol_sox_5`, `mag_sox`, `mag_predicha`, `CONJUNTO`. Las que no: `vol_sox_10`, `disp_asia`, `dias_trimestre`.
>
> **Julio-2026 cae del lado alto para `vol_sox_5`, `mag_sox`**, y del lado bajo para el resto — incluido el modelo conjunto.
>
> **El bloque de julio NO es excepcional en la ventana larga.** Su +40.91 pp está en el percentil **90.3** de todos los bloques contiguos de su mismo ancho, y hay **157** bloques históricos sin solape iguales o mejores. Su firma de condiciones sí es atípica (Mahalanobis en el percentil 100.0), pero el motor de esa distancia es `disp_asia` — una de las condiciones que NO discrimina, así que es una descripción, no una explicación. Ver §3.3.
>
> **La reconstrucción es FIEL al sello, y la brecha de 16 pp contra 6 pp no está en el mecanismo.** Sobre las 214 filas que comparten fecha de emisión Y sesión objetivo: 100.0% de predicciones con el mismo signo, 100.0% de gaps idénticos, dif 0.0 pp. **Los +6.2 pp de la ventana sellada son la resta de un bloque de julio de +40.9 pp, dos fechas de incidente de producción que cuestan −62.5 pp sobre 16 filas, y un resto de +4.1 pp (p=0.44)** — descomposición, no corrección: ninguna fila sellada se toca y ninguna cifra publicada se mueve.
>
> Intentos sumados: **8** (N acumulado 25 → **33**). NO EVALUABLE: **densidad_noticias**.

### Por qué `no refutada` aquí vale poco

1. **Lo único que discrimina es la MAGNITUD del movimiento del SOX**, y
   el mecanismo es casi una identidad: la predicción del campeón *es*
   beta × ese movimiento, así que cuando el SOX se mueve fuerte la
   apuesta se distingue más de `siempre al alza`. No es un hallazgo
   sobre el mercado; es aritmética del propio modelo.
2. **Las condiciones que aportarían información NUEVA son justo las que
   fallan** — dispersión asiática, distancia al trimestre y la ventana
   de volatilidad de 10 sesiones tienen el IC del AUC sobre 0.5.
3. **Las dos patas del criterio nunca se cumplen fuerte a la vez:** la
   condición más sólida en el §4(a) es la más floja en el §4(b), y al
   revés. Ver la §2.

Frente D de la segunda tanda (01-sep-2026). Ejecuta el pre-registro
`GEMELO/CONDICIONAL/DISEÑO.md (31-ago-2026, POST-HOC)` sobre la ventana larga reconstruida, que es el
único lugar del proyecto con potencia real: la ventana sellada tiene
n efectivo 68 (ICC 0.403, DEFF 3.63) y toda su información
discriminante es un 9-7 en 17 días.

**Esto no es el veredicto de la Etapa 5.1, no releva nada, no cambia
el modelo 4.6.0 y no mueve ninguna cifra publicada.** Es exploratorio
por construcción (§1 del pre-registro): como mucho, *no refutado*.

---

## 0. Cómo reproducirlo, y bajo qué reglas

```bash
source venv/bin/activate
python -m GEMELO.CONDICIONAL.condicional
```

| parámetro | valor |
|---|---|
| Ventana | 2018-10-31 → 2026-08-31 |
| Fechas de emisión | 2030 |
| Filas de evaluación | 14000 |
| Convención de empate | excluir_cero |
| Filas con gap 0.00 excluidas | 713 |
| Filas duplicadas purgadas | 0 |
| Unidad de análisis | FECHA DE EMISIÓN (nunca la fila) |
| Embargo | 5 días |
| Splitter | walk-forward expansivo, corte = D - embargo, regla de GEMELO/control_lineal.py:180-181 |
| Semilla | 20260901 |
| Bootstrap | circular, 2000 réplicas, bloques de 10 FECHAS |
| Permutaciones | 5000 |
| Commit | c5cbb44 |

Y las huellas de las dependencias, porque esta corrida se hizo con
otros frentes editando `backtest/` y `GEMELO/` al mismo tiempo: el
mismo comando sobre otro árbol da otro número, y sin esto
`reproducible` sería una promesa vacía.

| archivo | sha256[:12] |
|---|---|
| backtest/baselines.py | d0146eca5f3d |
| backtest/datos.py | b5c8b34c1d37 |
| backtest/inferencia.py | 7e68ff0c41d2 |
| GEMELO/control_lineal.py | 56f66ae68179 |
| GEMELO/datos.py | b842d3fbabfc |
| GEMELO/features.py | 72c9f0fa29e4 |
| GEMELO/experimento.py | 6fc420f9f835 |
| GEMELO/ventana_larga.py | 3dc84756e094 |
| GEMELO/CONDICIONAL/condicional.py | 76555c77c143 |

### El clúster de día, RE-MEDIDO sobre la ventana larga

No se hereda el DEFF de la ventana sellada: se mide aquí de nuevo.

| fechas | filas | icc | cluster_kish | deff | n_efectivo |
|---|---|---|---|---|---|
| 2030 | 14000 | 0.3256 | 7.274 | 3.043 | 4601.3 |

Con DEFF **3.043**, las 14000 filas
valen **4601.3** observaciones independientes. Por eso
todo intervalo y todo p de este documento remuestrea FECHAS enteras.

### El test de causalidad, primero (§9 del pre-registro)

Cada condición se recalculó truncando el dataset en 12 fechas repartidas por toda la
ventana: **0 celdas con fuga**. Y la
CONTRAPRUEBA —una condición envenenada con `shift(-1)`— **sí fue
detectada**, así que el `pasa` no es el pase de un test que no
discrimina. Si la contraprueba no falla, el módulo se niega a correr.

---

## 1. La curva de concentración de la ventaja

Sobre 2030 fechas y 14000 filas, la ventaja total
del campeón reconstruido sobre `siempre al alza` es
**16.379 pp** ponderada por fila,
y **15.597 pp** como media por fecha, con
IC95 circular por fecha **[13.49, 17.77]** — que
**excluye el cero**.
Permutación de signo por día: p = 0.0.

- Fechas con neto positivo: **660** · negativo: **277** · cero: **1093**
- El **7.19%** de las fechas contiene el 50% de la ventaja neta
- El **12.56%**, el 80%
- El **16.5%**, el 100%

### Y por qué ese número, SOLO, no significa nada

Que el 16.5% de las fechas contenga el 100% de la ventaja suena a
concentración extrema, y leído solo no dice nada. Una ventaja
cercana a cero produce una curva extrema por pura ARITMÉTICA: las
fechas positivas suman el total y las negativas lo cancelan, así que
la cima sale minúscula aunque no haya ninguna estructura. La curva
solo es interpretable contra su nula, y la nula es la permutación de
signo por fecha que este frente exige: se conserva |b−c| de cada
fecha y se sortea su signo.

| curva | % fechas para el 100% del neto | % fechas para el 50% |
|---|---|---|
| observada | 16.5 | 7.19 |
| nula (signo permutado por fecha) | 0.64 (IC90 [0.1, 1.82]) | 0.34 |

**La curva observada es 26× MÁS DISPERSA que la del azar, no más concentrada.** Bajo la nula bastan 0.64% de las fechas para acumular el neto entero; en los datos hacen falta 16.5%. La lectura correcta es la contraria de la que sugería la pregunta: sobre ocho años la ventaja del campeón reconstruido **está repartida**, no vive en unos pocos días afortunados.

> Esto **no contradice** el hallazgo de la ventana sellada, lo pone en
> su sitio: en 34 fechas, que toda la ventaja viva en 6 días es lo que
> se espera de una muestra sin potencia (n efectivo 68). En 2030
> fechas, la misma medición muestra una ventaja repartida. Son la
> misma señal vista con dos potencias distintas — y con dos rivales
> distintos, que es la parte incómoda de la §3.4.

> Y una advertencia sobre este contraste, porque un revisor la haría:
> la nula aleatoriza el SIGNO, así que también destruye el hecho de que
> la ventaja media sea positiva. En rigor esta comparación confirma que
> la ventaja total es > 0 tanto como que está repartida. **La medida de
> concentración que no depende de eso es la tabla siguiente**, y es la
> que hay que mirar.

### La ventaja al quitar las mejores fechas — la medida que importa

Cada fila quita el X% de fechas más favorables y vuelve a medir, con IC
circular por bloques de fechas. Es la versión con potencia del criterio
R2 del `GEMELO/DISEÑO.md`, y no depende de ninguna nula.

| quitando_top_pct | fechas_quitadas | ventaja_pp_ponderada_por_fila | ventaja_pp_media_por_fecha | ic95_lo | ic95_hi | ic_excluye_cero |
|---|---|---|---|---|---|---|
| 1 | 20 | 15.412 | 14.758 | 12.559 | 16.963 | True |
| 5 | 102 | 11.203 | 11.132 | 9.16 | 13.265 | True |
| 10 | 203 | 6.189 | 6.569 | 4.717 | 8.379 | True |
| 20 | 406 | -2.887 | -1.937 | -3.645 | -0.328 | True |

**La ventaja aguanta que le quiten el 10% de las mejores fechas (6.569 pp, IC95 [4.717, 8.379]) y NO aguanta que le quiten el 20% (-1.937 pp).** Ese
es el grado real de concentración: ni `vive en seis días` ni `está
uniformemente repartida`. Vive en el mejor quinto de las fechas.
La curva completa (muestreada):

| pct_fechas | pct_del_neto |
|---|---|
| 0.1 | 0.7 |
| 0.2 | 1.4 |
| 0.49 | 3.49 |
| 0.99 | 6.98 |
| 2.02 | 14.3 |
| 5.02 | 35.59 |
| 10.0 | 66.46 |
| 14.98 | 92.89 |
| 20.0 | 113.78 |
| 25.02 | 129.66 |
| 30.0 | 138.12 |
| 40.0 | 140.34 |
| 50.0 | 140.34 |
| 60.0 | 140.34 |
| 70.0 | 140.34 |
| 80.0 | 140.34 |
| 90.0 | 137.11 |
| 100.0 | 100.0 |

---

## 2. ¿Las condiciones predicen los bloques altos FUERA DE MUESTRA?

Walk-forward expansivo, corte = D − 5 días, mínimo
250 fechas de entrenamiento. La etiqueta es
alto = ventaja de la fecha > mediana global (0.0 pp), congelada en la §4 y
calculada una sola vez. El §4(a) se cumple si el IC95 del AUC excluye
0.5 **o** si McNemar da p<0.05; ninguno de los dos umbrales se relajó.

| condición | fechas OOS | AUC | IC95 (bloques de fecha) | excluye 0.5 | p perm. | p perm. Holm | McNemar p | cond. mejor que trivial | cumple §4(a) | sobrevive Holm |
|---|---|---|---|---|---|---|---|---|---|---|
| vol_sox_5 | 1776 | 0.5419 | [0.5129, 0.5708] | True | 0.01 | 0.04 | 0.0 | False | True | True |
| vol_sox_10 | 1776 | 0.5131 | [0.4843, 0.5422] | False | 0.3896 | 1.0 | 0.0 | False | False | False |
| mag_sox | 1776 | 0.5978 | [0.5713, 0.6269] | True | 0.001 | 0.007 | 0.0 | False | True | True |
| disp_asia | 1776 | 0.5058 | [0.4759, 0.5344] | False | 0.7083 | 1.0 | 0.0 | False | False | False |
| dias_trimestre | 1776 | 0.5081 | [0.4778, 0.5377] | False | 0.5814 | 1.0 | 0.0 | False | False | False |
| mag_predicha | 1776 | 0.5809 | [0.5511, 0.6102] | True | 0.001 | 0.007 | 0.0 | False | True | True |
| CONJUNTO | 1776 | 0.5814 | [0.552, 0.6119] | True | 0.001 | 0.007 | 0.0 | False | True | True |

> **La columna `cond. mejor que trivial` no es decorativa.** Un
> McNemar significativo puede significar que la condición es
> significativamente PEOR que el rival trivial. En la primera versión
> de este análisis faltaba esa comprobación de DIRECCIÓN, y las siete
> configuraciones pasaban el §4(a) — varias de ellas por ser malas.
> Corregido en el ejecutable.

> **Holm se informa AL LADO del criterio congelado, nunca en su
> lugar.** La §4(a) fija un umbral nominal por candidata y se aplica
> tal cual: un criterio congelado no se toca después de ver
> resultados. Pero siete configuraciones contra un 5% nominal dan ~30%
> de probabilidad de al menos un falso positivo, y este proyecto tiene
> un DSR justamente por eso. El §4(a) decide; Holm dice cuánto
> conviene creerle.

> **El rival del McNemar es la clase MAYORITARIA, no `siempre alto`.**
> Con el corte en la mediana y 1093 de 2030 fechas con ventaja
> exactamente 0, `alto` es la clase MINORITARIA (~33%). Un rival que
> dijera `alto` siempre acertaría el 33% y cualquier cosa le ganaría
> con p=0.0 — un hombre de paja que en la primera versión de este
> análisis hizo pasar el §4(a) a las SIETE configuraciones, incluidas
> tres cuyo AUC ni siquiera se despega de 0.5. Está corregido en el
> ejecutable, no en una nota: la clase mayoritaria se aprende
> expansivamente, con el mismo embargo que todo lo demás.

**Lo que discrimina es la MAGNITUD, y el mecanismo es casi
tautológico.** `mag_sox` (AUC 0.5978) y `mag_predicha` (AUC 0.5809) son esencialmente la misma
variable —la predicción del campeón ES beta × el movimiento del SOX—,
y lo que dicen es que cuando el SOX se mueve fuerte, la apuesta
direccional del modelo se distingue más de `siempre al alza`. Eso es
casi una identidad, no un descubrimiento sobre el mercado. Las
condiciones que aportarían información NUEVA —dispersión asiática,
distancia al trimestre, la ventana de volatilidad de 10 sesiones— son
exactamente las que **no** discriminan.

### §4(b): ¿cae julio del lado alto que la condición predijo?

| condición | fechas del bloque | predichas altas | percentil del score de julio | ventaja real julio (pp) | ventaja real resto (pp) | cumple §4(b) |
|---|---|---|---|---|---|---|
| vol_sox_5 | 7 | 7 | 89.7 | 25.0 | 15.92 | True |
| vol_sox_10 | 7 | 7 | 90.3 | 25.0 | 15.92 | True |
| mag_sox | 7 | 4 | 57.5 | 25.0 | 15.92 | True |
| disp_asia | 7 | 7 | 89.5 | 25.0 | 15.92 | True |
| dias_trimestre | 7 | 0 | 42.7 | 25.0 | 15.92 | False |
| mag_predicha | 7 | 3 | 58.2 | 25.0 | 15.92 | False |
| CONJUNTO | 7 | 3 | 46.3 | 25.0 | 15.92 | False |

> Con walk-forward expansivo toda fecha de 2026 está fuera de muestra
> por construcción: el requisito de la §4 (`el fold que contiene julio
> tiene que ser de prueba`) se cumple, y se verifica en la tabla, no se
> supone.

**Las dos patas del criterio no se cumplen a la vez con fuerza, y esa
es la lectura honesta.** La condición más sólida en el §4(a) —`mag_sox`, AUC 0.5978, Holm 0.007— es la más floja en
el §4(b): predice altas solo 4 de 7 fechas de julio, en
el percentil 57.5. Y al revés: `vol_sox_5` marca julio 7 de 7 en el percentil 90, pero es
la más floja del §4(a) (AUC 0.5419, Holm 0.04, al borde). Ninguna
condición es fuerte en las dos cosas a la vez.

**Y el tamaño del efecto pone a julio en su sitio:** la ventaja real
media de las fechas de julio es 25.0 pp
contra 15.92 pp del
resto de la ventana larga. Es un bloque bueno, no un bloque de otro
mundo — nueve puntos por encima de un día cualquiera, no cuarenta.

---

## 3. ¿El bloque de julio es de la misma especie que los históricos?

### 3.1 El scan statistic, donde sí hay potencia

La ventana sellada dio p≈0.55–0.65 sobre 34 fechas. Aquí es el mismo
estadístico —máximo de la ventaja sobre ventanas contiguas de 3 a 10 fechas— sobre 2030 fechas.

| mejor bloque de la ventana larga | ancho | ventaja | p del scan | nula (mediana) |
|---|---|---|---|---|
| 2018-12-19 → 2018-12-21 | 3 | 100.0 pp | 0.9444 | 100.0 pp IC90 [95.83, 100.0] |

> **⚠ ESTE SCAN ESTÁ SATURADO Y SU p NO SE PUEDE LEER COMO
> EVIDENCIA.** Sobre la ventana larga el campeón reconstruido saca
> ventaja media de dos dígitos, así que hay muchísimos bloques de 3
> fechas donde acierta 7/7 y `siempre al alza` 0/7: el estadístico
> toca su techo de 100 pp tanto en los datos como bajo la nula, y
> el p=0.9444 sale de comparar dos saturaciones. Se
> publica porque estaba declarado, marcado como lo que es. El
> estadístico que SÍ se puede leer va abajo.

### 3.2 Julio contra TODOS los bloques de su mismo ancho

El estadístico no saturado: dónde cae julio en la distribución de la
ventaja de **todos** los bloques contiguos del mismo ancho, en ocho
años. No hay máximos, no hay saturación, no hay libertad de elegir la
ventana: el ancho lo fija julio.

| bloque | fechas | ventaja reconstruida | percentil entre bloques de su ancho |
|---|---|---|---|
| 2026-07-15 → 2026-07-23 | 7 | 40.91 pp | 90.3 |

| ancho | n_bloques | mediana_pp | p90_pp | p95_pp | p99_pp | max_pp | pct_bloques_>=_julio |
|---|---|---|---|---|---|---|---|
| 7 | 2024 | 15.09 | 40.41 | 47.94 | 61.37 | 83.33 | 9.7 |

**En ocho años hay 157
bloques sin solape iguales o mejores que el de julio.** Los mejores:

| ancho | desde | hasta | ventaja_pp |
|---|---|---|---|
| 3 | 2018-12-19 | 2018-12-21 | 100.0 |
| 3 | 2019-11-19 | 2019-11-21 | 100.0 |
| 3 | 2022-03-03 | 2022-03-07 | 100.0 |
| 3 | 2022-09-20 | 2022-09-22 | 100.0 |
| 3 | 2022-10-06 | 2022-10-10 | 100.0 |
| 3 | 2026-03-26 | 2026-03-30 | 100.0 |
| 3 | 2019-07-31 | 2019-08-02 | 91.67 |
| 3 | 2022-01-19 | 2022-01-21 | 91.67 |
| 3 | 2022-06-08 | 2022-06-10 | 91.67 |
| 3 | 2021-03-02 | 2021-03-04 | 91.3 |

### 3.3 La firma: ¿julio se parece a los bloques altos históricos?

Las condiciones se estandarizan con media y desviación calculadas
SOLO con datos anteriores a julio-2026 — el bloque que se juzga no
participa en su propia estandarización.

| condición | julio (z) | media de los bloques altos históricos (z) |
|---|---|---|
| vol_sox_5 | 0.829 | 0.263 |
| vol_sox_10 | 0.978 | 0.095 |
| mag_sox | 0.269 | 0.406 |
| disp_asia | 2.913 | 0.174 |
| dias_trimestre | 1.064 | -0.152 |
| mag_predicha | 0.393 | 0.329 |

Distancia de Mahalanobis de julio al centro de las firmas
históricas: **6.021** — percentil
**100.0** de la propia distribución de los
30 bloques altos históricos
(mediana 2.089, p95
4.196).

**Veredicto de la firma: julio NO es de la misma especie** que los bloques altos históricos — y el motor de esa distancia
es una sola condición, `disp_asia`, en z≈+2.9.

> **Con qué fuerza se puede decir esto: poca.** Una Mahalanobis con
> 30 bloques de referencia en
> 6 dimensiones estima una covarianza con
> pocos grados de libertad, y el percentil 100 en esa escala
> significa `el más lejano de treinta`, no `imposible`. Además
> `disp_asia` es precisamente una de las condiciones que **no**
> discrimina fuera de muestra (§2, AUC 0.506, IC incluye 0.5): que
> julio tenga un valor extremo en una variable sin poder predictivo
> es una descripción, no una explicación. La lectura defendible es
> **julio fue un bloque grande pero ordinario en MAGNITUD (percentil
> 90 entre bloques de su ancho) con una dispersión asiática
> inusualmente alta** — y nada de eso lo convierte en evidencia de
> una condición identificable.

### 3.4 Verificación por OTRO mecanismo: las filas selladas

Regla de la casa: una verificación que usa el mismo mecanismo que
produjo la cifra no es una verificación. La reconstrucción sale de
Yahoo hoy; esto sale de `senales.db` en `mode=ro`, sellado en su
momento. Son dos caminos distintos.

| tramo | n | fechas | b | c | ventaja_pp | mcnemar_p |
|---|---|---|---|---|---|---|
| bloque julio | 44 | 6 | 24 | 6 | 40.9 | 0.0014 |
| resto | 212 | 29 | 48 | 50 | -0.9 | 0.9196 |
| ventana completa | 256 | 35 | 72 | 56 | 6.2 | 0.1847 |

La reconstrucción da **40.91 pp** sobre el
bloque de julio y el sello da **40.9 pp** sobre las mismas 44 filas. Dos caminos de cómputo distintos,
el mismo número: el bloque de julio **existe** y no es un artefacto
de ninguno de los dos mecanismos. Lo que este documento discute no
es si existe, sino si es **excepcional** — y no lo es.

### 3.5 La reconciliación: 16 pp contra 6 pp

Sobre la ventana larga el campeón reconstruido saca **16.4 pp** sobre
`siempre al alza`; sobre la ventana sellada saca **6.2 pp**. Publicar el
primero sin explicar el segundo sería lo que este proyecto no hace.
La medición que lo dirime es **las mismas filas**.

#### Primero, un error de emparejamiento que vale la pena contar

La clave semántica de una fila es la **sesión objetivo**, no la
fecha de emisión — y por eso la advertencia sobre el 91.4% de
`ventana_larga.py` es correcta. Pero emparejar SOLO por sesión
objetivo tampoco alcanza, y esto no estaba anotado en ninguna
parte: la emisión sellada del 2026-07-05
apunta a una sesión que **no es la siguiente**, porque la corrida
intermedia falló y dejó sus filas vacías. Una reconstrucción que
asume `la emisión de D anticipa la sesión siguiente` empareja esa
sesión con una emisión POSTERIOR, y le regala un día entero de SOX
que el sello no tuvo.

Con ese emparejamiento la reconstrucción salía 5.2 pp por encima
del sello, con 13 de 14 desacuerdos de signo a su favor
(p=0.0018) — **la firma perfecta de una fuga, y no había ninguna**.
Era el emparejamiento comparando dos predicciones hechas con un día
de diferencia. La comparación honesta exige las DOS claves: misma
sesión objetivo **y** misma fecha de emisión.

Filas descartadas por desfase de emisión: **25**, en las fechas 2026-07-05, 2026-07-29, 2026-08-03, 2026-08-05.

#### Y entonces, con las dos claves:

| medición | n | fechas | acierto_pct | base_pct | ventaja_pp | ic95_por_fecha |
|---|---|---|---|---|---|---|
| reconstruida · ventana larga (8 años) | 14000 | 2030 | 71.0 | 54.7 | 16.4 | [13.49, 17.77] |
| reconstruida · MISMAS FILAS que el sello | 214 | 34 | 72.0 | 56.1 | 15.9 | [6.13, 28.19] |
| SELLADA · las mismas filas | 214 | 34 | 72.0 | 56.1 | 15.9 | [6.13, 28.19] |

Sobre esas **214** filas: **100.0%** de las predicciones con el mismo signo, **100.0%** de los gaps idénticos a menos de 0.01 pp, **cero** desacuerdos de
signo.

**LA RECONSTRUCCIÓN ES FIEL. Sobre las 214 filas que comparten fecha de emisión Y sesión objetivo: 100.0% de las predicciones con el mismo signo, 100.0% de los gaps idénticos, y la misma ventaja (dif 0.0 pp). No hay fuga ni revisión silenciosa que explique nada, porque no hay nada que explicar. Las 25 filas que NO se pueden parear son las de emisiones desfasadas, y son un hallazgo aparte.**

> Y de paso queda medido lo que el aviso decía: emparejando por la
> clave correcta la coincidencia con el sello es del **100%**, no
> del 91.4% que `GEMELO/ventana_larga.py`:214 sigue calculando
> emparejando por `["fecha","ticker"]`. Esa cifra está refutada y
> este documento no la republica.

#### Dónde está entonces la brecha entre las dos ventanas

No en el mecanismo. La ventana sellada, partida en sus tramos:

| tramo | n | fechas | acierto_pct | base_pct | ventaja_pp | mcnemar_p |
|---|---|---|---|---|---|---|
| TODA la ventana sellada (la cifra vigente) | 256 | 35 | 65.6 | 59.4 | 6.2 | 0.1847 |
| bloque 2026-07-15 → 2026-07-23 | 44 | 6 | 81.8 | 40.9 | 40.9 | 0.0014 |
| fechas con incidente de producción | 28 | 4 | 32.1 | 82.1 | -50.0 | 0.0066 |
| todo lo demás | 184 | 25 | 66.8 | 60.3 | 6.5 | 0.2007 |

Los +6.2 pp de la ventana sellada son la resta de tres cosas muy
distintas: un bloque de julio de +40.9 pp, dos fechas de incidente
de producción que cuestan −62.5 pp sobre 16 filas, y un resto de
+4.1 pp con p=0.44 que es lo que el modelo hace un día cualquiera.

> **Esto NO es una corrección ni una retractación, y el tramo `sin
> incidentes` NO es el resultado.** Las filas selladas jamás se
> reescriben y ninguna cifra publicada se mueve: los +6.2 pp de la
> ventana completa siguen siendo la cifra de la ventana completa, y
> el 65.8% / +5.3 pp del README sigue vigente. Quitar los días malos
> de un track record es exactamente la trampa que este proyecto no
> comete. Es una DESCOMPOSICIÓN: dice de dónde viene el número, no
> lo sustituye.

> Lo que además cambia entre las dos ventanas es **el rival**:
> `siempre al alza` acierta 54.7% en ocho años y
56.1% en el tramo sellado. La misma habilidad rinde menos ventaja cuando
> el rival es más duro. Por eso la regla de la casa exige comparar
> **sobre las mismas filas**.

---

## 4. Lo que quedó NO EVALUABLE, y por qué

**Condición 4 del pre-registro (§3.4), `densidad_noticias`: NO
EVALUABLE.** Dos razones independientes, ambas medidas aquí, no
supuestas:

1. **Fuga B-1.** la condición usa `relevancia`, salida del análisis de IA; el camino de features corta por fecha de publicación y nunca mira `analisis.analizado_en`. El primer juicio de IA es del `2026-07-04 16:30:47.305899+00:00`, sobre titulares que empiezan el `2025-09-09`. El retraso, medido en varios umbrales — cada uno con su definición a la vista, para que dos cifras verdaderas medidas con criterios distintos no parezcan contradecirse:

| criterio | valor |
|---|---|
| pct analizado despues de publicar | 100.0 |
| pct analizado mas de 2h tarde | 92.0 |
| pct analizado mas de 24h tarde | 32.4 |
| pct analizado mas de 7d tarde | 6.2 |
| retraso mediano horas | 11.8 |

2. **Cobertura.** `titulares` empieza el 2025-09-09: no hay noticias para la inmensa mayoría de las fechas de emisión de la ventana larga 2018→2026: `titulares` va de `2025-09-09T12:45:56+00:00` a `2026-08-31T21:59:00+00:00` (5096 filas), contra una ventana que empieza en 2018-10-31.

La §5 R4 del pre-registro obliga a descartar una condición con fuga,
no a reportarla con una advertencia. Se descarta. Y como el §4.2 bis
define un intento como `(configuración × ventana) **con resultado
reportable**`, la condición 4 **no suma al DSR**.

> El arreglo de la fuga lo está haciendo otro frente sobre
> `backtest/datos.py`. Aunque quede arreglado, la razón 2 sigue en pie:
> sobre 2018→2026 esta condición no es medible.

---

## 5. El conteo de intentos

| intento | ventana | cuenta |
|---|---|---|
| vol_sox_5 | ventana larga, walk-forward | 1 |
| vol_sox_10 | ventana larga, walk-forward | 1 |
| mag_sox | ventana larga, walk-forward | 1 |
| disp_asia | ventana larga, walk-forward | 1 |
| dias_trimestre | ventana larga, walk-forward | 1 |
| mag_predicha | ventana larga, walk-forward | 1 |
| CONJUNTO | ventana larga, walk-forward (ridge sobre las 6) | 1 |
| scan statistic de bloques | ventana larga (declarado 01-sep-2026) | 1 |

**N acumulado: 25 → 33**
(+8).

Tres precisiones sobre el conteo, porque contarlo a conveniencia es
exactamente el sesgo que el DSR existe para corregir:

1. El pre-registro §7 había declarado +7 (seis condiciones + el
   conjunto). Aquí son +8 por dos correcciones que se compensan y una
   que no: la condición 4 **no cuenta** (sin resultado reportable); las
   dos ventanas de volatilidad (5 y 10) **se reportan por separado**, y
   la §7 ya previó que en ese caso el N sube; y el **scan statistic de
   la §3.1 se declara HOY** como intento nuevo, que el pre-registro no
   había contado.
2. La curva de concentración de la §1 **no** cuenta como intento: no
   ajusta ninguna configuración ni elige entre resultados. Es
   descriptiva.
3. Subir el N es la dirección conservadora: deflacta más, no menos.

---

## 6. Deudas y advertencias declaradas

- **`GEMELO/ventana_larga.py`:314-345 sigue ofreciendo una cifra de
  contaminación ya refutada** (el 91.4% de coincidencia con el track
  record sellado). Sale de emparejar por `["fecha","ticker"]` cuando
  corresponde por sesión objetivo. **No se republica aquí**, y este
  documento no la usa en ninguna parte. Queda anotada como deuda de la
  regla de la casa #4: un número retirado que sigue ofrecido en el
  código vuelve a circular. El arreglo va al ejecutable, no a un
  párrafo — no se hizo en este frente para no pisar el trabajo en curso
  sobre `backtest/`.
- **La ventana larga NO es point-in-time.** Yahoo reescribe la historia
  en silencio y el ajuste se recalcula con cada dividendo y split
  posteriores. La ventana larga da POTENCIA; la ventana sellada da
  VALIDEZ. Ninguna reemplaza a la otra. Todo hallazgo de este documento
  es sobre una reconstrucción, y el hallazgo central —que no hay
  condición identificable— es del tipo que la contaminación haría MÁS
  fácil de contradecir, no más fácil de sostener.
- El corte alto/bajo es la **mediana global** de la ventana, congelada
  en la §4: arrastra un componente in-sample. Se respetó porque estaba
  congelado; su efecto sería sobreestimar la discriminación, y aun así
  no se encontró ninguna.
- La condición 3 lee `vs. índice local + FX` como retorno del índice
  llevado a USD (convención #2: los pares son unidades por 1 USD).
  Residualizar un índice contra sí mismo es degenerado; la lectura se
  declara aquí, no se esconde.

---
Herramienta de análisis — no constituye asesoría financiera.
Pre-registro congelado en `GEMELO/CONDICIONAL/DISEÑO.md`.
**No es el veredicto de la Etapa 5.1** y no autoriza ningún cambio de
modelo: 4.6.0 sigue sellando sin enterarse de que esto existe.
