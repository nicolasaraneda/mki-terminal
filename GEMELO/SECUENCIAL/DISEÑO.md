# El diseño secuencial — pre-registro

**Estado: versión 4 — NO CONGELADO.** Es un pre-registro *terminado en su
aritmética* y **bloqueado por una decisión que no es de un agente**: con
qué α se declara (ver "La decisión que bloquea el congelamiento", abajo).
Escrito el 31-ago-2026, antes de la próxima mirada al track record
sellado. Toda cifra de este documento sale de
`GEMELO/SECUENCIAL/diseno_secuencial.py` y `GEMELO/SECUENCIAL/fronteras.py`,
versionados y reproducibles — es la lección operativa que dejó
`DECISIONES.md` §45.

> **No congelarlo esta noche es el resultado, no una tarea pendiente.** El
> documento fue rechazado **tres veces** por `estadistico-adversario` en el
> día en que se escribió. Los tres rechazos fueron correctos y los tres
> están corregidos. El tercero dejó, además de diez correcciones
> mecánicas, una que no lo es: el plan promete α = 0.05 y sobre el rango
> plausible de autocorrelación entrega entre 0.048 y 0.080. Se puede
> arreglar declarando α = 0.10 de entrada, lo cual **cambia el estándar
> científico con el que este proyecto va a juzgar su propio modelo**. Esa
> es una decisión de Nicolás, de la misma clase que el MDE, y un agente no
> la toma dentro de otra tarea.

## La decisión que bloquea el congelamiento

**Qué hay que elegir:** el α declarado del plan, entre dos opciones
costeadas.

| | α = 0.05 (lo que dice hoy) | α = 0.10 |
|---|---|---|
| ¿La promesa es verdadera? | **No** en todo el rango: entrega 0.046–0.079 según la autocorrelación | **Sí** en todo el rango plausible |
| Qué exige declarar | el residuo, con su tabla (está en §A3.2) | nada extra |
| Costo | un pre-registro que declara que no puede cumplir su propia promesa | un umbral más laxo, y decirlo de frente |
| Umbrales | los de §A3.4 | hay que recomputarlos (la maquinaria ya está) |

**Recomendación, marcada como tal:** α = 0.10, combinado con mover la
primera mirada a ~100 fechas en vez de ~51. Las dos son baratas, las dos
hacen verdadera la promesa, y la segunda **no cuesta alfa** —omitir o
retrasar una mirada solo puede bajarlo, que es la regla 2 que §A3.8 ya
tiene escrita— además de mejorar justo donde el bootstrap es más débil.
El argumento de fondo: esto es la primera mirada seria a una pregunta
abierta, no una presentación regulatoria, y un α de 0.10 honesto vale más
que un 0.05 con letra chica.

**Mientras esto no se decida, el resto del documento vale igual:** las
fronteras, el pasivo, el tamaño de muestra, la futilidad, el calendario y
los tres candados de `mirada.py` no dependen de esa elección. Lo que
depende son los umbrales de §A3.4, y recomputarlos es un comando.

> **Por qué hay una versión 3, y por qué se corrigió en su sitio.** Este
> documento fue **rechazado dos veces por `estadistico-adversario` el
> mismo día en que se escribió**, antes de commitearse y antes de que
> ningún número saliera del repo. La v1 congelaba fronteras con un α real
> de 0.05122 creyéndolo 0.05. La v2 arregló eso y siete defectos más, y
> fue rechazada porque su corrección del defecto grave **mudó el problema
> en vez de resolverlo**: cambió un α que dependía de un DEFF supuesto por
> un α que depende de una autocorrelación supuesta.
>
> La frontera de la errata es el commit: lo que nunca se publicó se
> corrige en su lugar, no se le agrega una nota. Los dos §§ de registro al
> final —"Lo que la v1 decía mal" y "La v2 también fue rechazada"— dejan
> los veinte cambios en tabla, para que la corrección sea auditable sin
> tener que confiar en esta frase.
>
> **A partir del congelamiento, esta regla cambia:** ninguna sección se
> reescribe; una corrección se agrega como subsección nueva con fecha
> posterior, y dice explícitamente si el criterio se movió o solo se
> corrigió la medición.

> **Regla cero de este documento:** el problema que resuelve no es "cuál
> es la ventaja" — es que **el proyecto viene mirando la misma cifra cada
> vez que crece, y eso tiene un costo estadístico que nadie declaró
> nunca**. Un diseño secuencial no hace que los datos digan más: hace que
> lo que digan sea interpretable. Si este documento se usa para justificar
> mirar más seguido, se está usando al revés.

## El punto de partida, que no se discute acá

Dos corridas de análisis pesado sobre las mismas 248 filas selladas
terminaron en "no se puede decidir entre hay condición y es azar"
(`GEMELO/resultados/concentracion.md`). Eso no fue un fracaso del
análisis: **248 filas no alcanzan**. Más estadística sobre los mismos
datos da la misma respuesta. Este diseño es la consecuencia lógica de
eso: si la pregunta se va a responder alguna vez, se responde con datos
NUEVOS y con las reglas escritas antes, no con más vueltas sobre los
mismos.

Queda firme y fuera de discusión acá: el campeón no pasa su propio
criterio de rechazo R2, y la ventana sellada completa sigue sin
distinguirse de cero.

## De dónde salen los números, y contra qué se validan

Las fronteras y las tasas de error de este documento **no salen de Monte
Carlo.** Salen de la recursión numérica de Armitage-McPherson
(`fronteras.py`), y se validan contra **dos varas externas
independientes**, no contra sí mismas:

| Vara externa | Qué valida | Resultado |
|---|---|---|
| Jennison & Turnbull (2000), α=0.05 bilateral | el cómputo de **fronteras** | Pocock K=4: 2.362 vs 2.361 publicado · OBF c_B K=4: 2.024 vs 2.024 |
| Armitage, McPherson & Rowe (1969), tabla 2 | el cómputo del **pasivo** | K=2 0.0834/0.083 · K=3 0.1070/0.107 · K=4 0.1267/0.126 · K=5 0.1419/0.142 · K=10 0.1931/0.193 |

Son dos caminos distintos del mismo código y se validan por separado a
propósito: el que calcula fronteras y el que calcula la inflación de
mirar no son el mismo cómputo, y un error en uno no aparece en el otro.

**Esto es lo que la v1 no tenía, y es el defecto de fondo que la hundió.**
La v1 sacaba las fronteras de un cuantil de Monte Carlo y las verificaba
con el mismo generador, el mismo `n_sim` y el mismo modelo, en otra
semilla. Eso no puede detectar el sesgo del generador: solo lo vuelve a
medir. La verificación interna daba 0.0507 y el documento lo leyó como
confirmación de que la frontera estaba bien construida. Era el sesgo
mismo. El α real de las fronteras que la v1 iba a congelar era **0.05122**.

---

## A1. El pasivo — cuántas veces se miró, y cuánto costó

Reconstruido de `DECISIONES.md`, `README.md` y el historial de commits.
**Doce miradas distintas a la ventaja de la ventana sellada contra su
baseline, en cinco fechas, con seis valores de n y tres convenciones de
empate:**

| # | Fecha | n | Ventaja | McNemar p | Convención | Fuente |
|---|---|---|---|---|---|---|
| 1 | 25-ago | 228 | +5.3 pp | 0.32 | estricta | `GEMELO/DISEÑO.md` §2 |
| 2 | 26-ago | 228 | +5.3 pp | 0.3193 | estricta | `DECISIONES.md`:2162 |
| 3 | 26-ago | 228 | +3.1 pp | 0.5854 | verificador | `DECISIONES.md`:2163 |
| 4 | 26-ago | 223 | +4.0 pp | 0.4633 | **excluir_cero** | `DECISIONES.md`:2164 |
| 5 | 26-ago | 184 | −3.3 pp | 0.60 | excluir_cero, subset R2 | `DECISIONES.md`:2199-2201 |
| 6 | ~27/28-ago | 223 | +4.0 pp | 0.4633 | excluir_cero (restatada) | README, commit `aa16a89` |
| 7 | 30-ago | 245 | +7.8 pp | 0.1158 | estricta | `DECISIONES.md`:3274 |
| 8 | 30-ago | 240 | +6.7 pp | 0.1849 | excluir_cero | `DECISIONES.md`:3282 |
| 9 | 30-ago | 253 | +7.5 pp | 0.1158 | estricta | `DECISIONES.md`:3586 |
| 10 | 30-ago | 253 | +5.5 pp | 0.2542 | verificador | `DECISIONES.md`:3587 |
| 11 | 30-ago | **248** | **+6.5 pp** | **0.1849** | **excluir_cero (canónica)** | `DECISIONES.md`:3588 |
| 12 | 31-ago | 248 | desglose por bloque | 0.001 / 0.920 | excluir_cero | `concentracion.md` (retractado) |

Las doce lecturas usan **siete valores distintos de n** (184, 223, 228,
240, 245, 248, 253). Para la inflación cuentan siete, no doce: dos
lecturas de la MISMA cifra no son dos oportunidades de cruzar un umbral.

**El tramo que NO se puede reconstruir, declarado:** entre el 26-jul
(n=80, cuando solo se publicaba la tasa cruda sin baseline) y el 25-ago
(n=228, la primera medición contra baseline) no hay registro de cuántas
veces se miró el número intermedio. `DECISIONES.md` registra decisiones
autónomas, no cada refresco del verificador. Por diseño, ese mes es un
hueco: **el pasivo real es ≥12 miradas, no exactamente 12.**

### Cuánto infla eso el falso positivo — y es un RANGO, no un número

El hueco no es un detalle de redacción: **son justamente las miradas que
más inflan**, porque comparten menos filas con las de hoy y por lo tanto
están menos correlacionadas con ellas. Un número único acá sería el mismo
error que este documento le reprocha al proyecto.

| Escenario | α real usando el umbral nominal 0.05 en cada mirada |
|---|---|
| **PISO** — solo las 12 reconstruidas (7 n distintos) | **0.0905** (1.8× el nominal) |
| + 2 miradas en el hueco | 0.1343 (2.7×) |
| + 4 miradas en el hueco | 0.1479 (3.0×) |
| + 8 miradas en el hueco | 0.1605 (3.2×) |
| **ESCENARIO ALTO** — una mirada en cada fecha de emisión desde n=80 | **0.1779** (3.6×) |

> **El rango honesto es α ∈ [0.09, 0.18], o sea entre 1.8× y 3.6× el
> nominal declarado.** El 0.09 es un piso, y citarlo solo sería citar el
> extremo que más favorece al proyecto.

**Por qué "escenario alto" y no "techo".** No hay techo finito: el mismo
cómputo anclado más atrás da 0.199 desde n=60, 0.225 desde n=40, 0.261
desde n=20 — bajo monitoreo continuo con n→0 el α tiende a 1. El 0.1779
depende de anclar en **n=80**, y ese ancla es un supuesto, defendible por
el registro (antes del 26-jul no se publicaba ni la tasa cruda, y la
primera comparación contra baseline fue el 25-ago) pero supuesto al fin.
Llamarlo "techo" habría sido presentar una elección como si fuera una
cota.

El piso, por su parte, dedupica por `n`. La regla escrita es "dos lecturas
de la MISMA cifra"; la implementada es "el mismo n", y a n=228, 248 y 253
hay convenciones distintas, que son cifras distintas. **La objeción es
correcta en principio y no tiene un número al lado, a propósito:** el
modelo browniano no admite dos miradas en la misma fracción de información
—entre ellas el incremento es cero y el estadístico es literalmente el
mismo—, así que "recomputar sin deduplicar" no está definido, no vale
cero. Lo que sí se puede decir es de qué tamaño sería el efecto: tres
convenciones sobre las mismas filas están casi perfectamente
correlacionadas entre sí, mucho más que dos n distintos, así que aportan
menos que cualquiera de los escalones de la tabla. El piso sigue siendo un
piso.

La inflación satura lejos de un Bonferroni ingenuo (12 × 0.05 = 0.60)
porque las miradas comparten casi todas las filas. Pero **está igual de
lejos del 0.05 que se declaró.**

### Lo que hay que decir a favor — con la corrección que la v1 no hizo

La v1 decía: *"ninguna de esas doce miradas se acercó siquiera a cruzar
el umbral; la inflación no produjo ningún falso positivo porque nunca
hubo un positivo."* **Esa frase es falsa como está escrita**, y la
corrección importa porque es el argumento entero.

Es cierto de la **cifra principal**: el p más chico jamás observado para
la ventaja global de la ventana sellada es 0.1158, más del doble de 0.05.

Es **falso de los subgrupos**, y los subgrupos se miraron en la misma
sesión con la misma libertad. `concentracion.md` reporta:

| Subgrupo mirado | n | p | Qué pasó después |
|---|---|---|---|
| Bloque 15-23-jul-2026 (6 fechas) | 44 | **0.001** | retractado |
| XTKS (Tokio) | 24 | **0.021** | no sobrevive Bonferroni ×8 |
| XKRX (Seúl) | 10 | **0.031** | no sobrevive Bonferroni ×8 |

**Tres p por debajo de 0.05 aparecieron, se creyeron lo suficiente como
para escribir una conclusión encima, y hubo que retractarlos.** Ese es
exactamente el falso positivo que la inflación no declarada predice, y ya
ocurrió — no es un riesgo futuro, es el historial reciente del proyecto.

Lo que queda en pie del argumento original, y sigue importando: **ninguna
afirmación publicada hoy en el README depende de un p que haya cruzado el
umbral**, porque la cifra publicada nunca lo cruzó. El pasivo no invalida
la portada. Pero tampoco es puramente prospectivo, que es lo que la v1
sostenía.

---

## A2. La pregunta, en forma decidible

> **H₀:** sobre emisiones selladas NUEVAS, la tasa de acierto direccional
> del modelo 4.6.0 y la de "siempre al alza" son iguales.
> **H₁ (bilateral):** difieren.
> **Estadístico:** McNemar pareado sobre las mismas filas, convención
> `excluir_cero` (la congelada en `GEMELO/DISEÑO.md` §2.8), estudentizado
> por una varianza cluster-robusta re-estimada en cada mirada — la
> fórmula exacta está en §A3.2 y es parte del pre-registro.

**"Nuevas" significa: filas con `fecha` de emisión posterior al
2026-08-31**, la fecha de congelamiento de este documento.

**Qué papel juegan exactamente las 248 filas de hoy** (la v1 decía "no
entran en ningún cómputo, ni siquiera como prior", y eso no era exacto):

- **NO entran en el estadístico ni en la decisión.** Ninguna fila sellada
  hasta el 2026-08-31 aporta un solo grado de libertad a ninguna de las
  cuatro miradas. Esto es lo que importa y se mantiene.
- **SÍ entran como parámetros de estorbo (*nuisance*)**, y hay tres:
  la tasa de discordancia `p_d = 128/248 = 0.516` que fija el n de
  Connor; el efecto de diseño `DEFF ≈ 3.6` medido sobre ellas; y el ritmo
  de 6.5 filas por día hábil que fija el calendario.

La diferencia no es cosmética. Un parámetro de estorbo mal estimado
mueve el N y las fechas, **no mueve el α ni el veredicto** — y los tres
son cantidades que no dependen de si hay o no ventaja. Pero decir "no se
usan para nada" y después usarlas tres veces es la clase de afirmación
que un pre-registro no puede permitirse. Si el p_d de la ventana nueva
resulta muy distinto, el N se recalcula (ver A3.5, cláusula 6), no el
umbral.

Se declara bilateral a propósito, aunque la expectativa sea positiva: si
el modelo resultara peor que la constante de forma sistemática, eso es un
hallazgo tanto o más importante, y un diseño unilateral lo tiraría a la
basura por construcción.

---

## A3. El diseño

### A3.1 El efecto mínimo de interés (MDE), y por qué esta elección es de Nicolás

El MDE fija TODO el calendario. Con los parámetros medidos del proyecto
(p_d=0.516, DEFF=3.6, ritmo de 6.5 filas/día hábil), para un test de
**muestra fija**:

| Efecto a detectar | n filas (con DEFF) | ≈ fechas | Se alcanza |
|---|---|---|---|
| +15.66 pp (el de la ventana larga) | 586 | 81 | ene-2027 |
| **+10 pp (propuesto)** | **1.450** | **200** | **jul-2027** |
| +6.45 pp (el punto estimado sellado hoy) | 3.497 | 481 | sep-2028 |
| +5 pp (el umbral de relevo de `RELEVO.md`) | 5.825 | 802 | feb-2030 |
| +3 pp | 16.196 | 2.229 | mar-2036 |

**Propuesta razonada: +10 pp.** Los argumentos, para que se pueda
discutir con ellos y no con una corazonada:

1. Diseñar para +15.66 pp sería diseñar para el efecto de la ventana
   larga, que la ventana sellada ya no reproduce — se llegaría rápido a
   una respuesta sobre un efecto que probablemente no existe a ese
   tamaño.
2. Diseñar para +5 pp es defendible (es el umbral que `RELEVO.md` ya
   declaró como margen mínimo accionable) pero empuja la respuesta a
   2030. **Un diseño cuya respuesta llega en 2030 tiene alta probabilidad
   de romperse antes de completarse** (§A3.5), y un diseño que se rompe
   no responde nada.
3. +10 pp deja la respuesta dentro de un año. Si el efecto real es menor,
   el diseño **no lo va a detectar y va a declarar futilidad** — y eso
   también es una respuesta: "si hay ventaja, es menor que 10 pp", con un
   intervalo que la acota. Eso es más de lo que el proyecto sabe hoy.

**La elección final del MDE es de Nicolás, no de este documento.** Cambia
el horizonte entre cinco meses y tres años y medio; es exactamente la
clase de decisión que el encargo prohíbe que tome un agente. Lo que este
documento aporta es el menú con su costo calculado.

### A3.2 El estadístico, escrito — y por qué el DEFF NO se congela adentro

Este apartado es la corrección más importante de la v2. La v1 congelaba
`DEFF = 3.6` como si fuera una constante del mundo. No lo es: es una
estimación, con un rango medido de 2.5 a 3.6 y un extremo teórico en 7.26
(ρ=1, todas las filas de una fecha perfectamente redundantes). Y un α que
depende de una estimación no es un α controlado:

| Si el DEFF verdadero fuera… | …el α real del plan sería |
|---|---|
| 2.50 | 0.0170 |
| **3.60 (el supuesto)** | **0.0500** |
| 4.60 | 0.0876 |
| 5.83 | 0.1366 |
| 7.26 (extremo teórico ρ=1) | 0.1931 |

**Un α que se mueve entre 0.02 y 0.19 según un parámetro estimado a ojo
no controla nada.** El documento se llama "pre-registro" precisamente
porque promete un α de 0.05, y con el DEFF congelado esa promesa era
condicional a acertarle a un número que nadie puede verificar hasta el
final.

Lo que se pre-registra en cambio es la **fórmula**, no el valor:

> En cada mirada *k*, sobre las filas acumuladas hasta esa fecha:
>
> 1. Se computan los discordantes de McNemar `b` (modelo acierta, base
>    falla) y `c` (base acierta, modelo falla) bajo `excluir_cero`.
> 2. El estadístico **sin corregir** es `Z₀ = (b − c) / √(b + c)`.
> 3. `V̂ₖ`, el factor de varianza cluster-robusta, se **re-estima con los
>    datos de esa mirada**, remuestreando FECHAS DE EMISIÓN con
>    `backtest.inferencia._remuestrear_circular` (el remuestreador
>    circular del proyecto), en **tres longitudes de bloque congeladas:
>    `BLOQUES_FECHAS = (1, 5, 10)`**, con `N_DRAWS = 200_000` y
>    `SEMILLA_BOOTSTRAP = 20260831`. Los tres parámetros están acá y en
>    `mirada.py`, y valen lo mismo en los dos lugares.
> 4. **`V̂ₖ` es el MÁXIMO de los tres.** Tomar el máximo solo puede
>    inflar la varianza, o sea solo puede BAJAR el α: cuesta potencia y no
>    puede regalar un falso positivo. Es una regla fija, no una elección
>    del día de la mirada.
> 5. **El estadístico de la mirada es `Zₖ = Z₀ / √V̂ₖ`**, y se compara
>    contra el umbral de la tabla de §A3.4.
> 6. **Se reporta siempre el intervalo**, no solo el veredicto. Un cruce
>    sin intervalo no cuenta como resultado. Y se reporta **siempre la
>    autocorrelación lag-1 de `d_j` con su error estándar**, por la razón
>    del apartado que sigue.

#### El eje al que este estimador es ciego, y cuánto cuesta

Esto es una limitación declarada del diseño, no un detalle de
implementación. **Un bootstrap que sortea fechas corrige la dependencia
DENTRO de la fecha y es estructuralmente ciego a la dependencia ENTRE
fechas contiguas.** Si esa existe, `V̂` sale corta y `Z` sale inflado.

Y el proyecto tiene dos afirmaciones propias de que esa dependencia
existe: el bloque de **seis fechas consecutivas** del 15-23-jul (§A1), y
el criterio **R2**, que *es* una afirmación sobre estructura entre fechas
contiguas.

α global del plan entero, simulado bajo H₀ con un AR(1) en `d_j`
(`diseno_secuencial.alfa_plan_bajo_correlacion`, 20.000 réplicas, IC de
Wilson al 95%, semilla congelada):

| autocorrelación real de `d_j` | con bloque 1 solo | **con max(1, 5, 10)** | reduce |
|---|---|---|---|
| +0.00 | 0.0551 [0.0520, 0.0583] | **0.0458 [0.0430, 0.0488]** | 17% |
| +0.10 | 0.0847 [0.0809, 0.0886] | **0.0598 [0.0566, 0.0632]** | 29% |
| +0.20 | 0.1251 [0.1206, 0.1298] | **0.0700 [0.0665, 0.0736]** | 44% |
| +0.30 | 0.1771 [0.1719, 0.1825] | **0.0791 [0.0755, 0.0830]** | 55% |

Tres cosas hay que leer de esa tabla, y las dos últimas son las incómodas:

1. **Con bloque 1 solo —un bootstrap de clúster puro— el diseño no
   cumplía lo que promete.** A una autocorrelación de apenas +0.10 el α
   pasaba a 0.085. Esa versión fue rechazada por eso.
2. **La reducción NO es pareja, y decir "~60% en todos los niveles" era
   falso.** Es 17% donde el proyecto midió que está la autocorrelación, y
   llega a 55% solo en el extremo. La versión anterior de este documento
   citaba el mejor caso como si fuera el promedio — el mismo vicio que le
   reprocha al proyecto en §A1.
3. **No la elimina.** A ac1=+0.30 queda un α de 0.079, y aun a
   autocorrelación cero queda en 0.046. Con ~51 fechas en la primera
   mirada eso **no se arregla con un estimador mejor**: es el límite del
   n. Es la razón por la que este documento **no está congelado** — ver
   "La decisión que bloquea el congelamiento" al principio.

Dos declaraciones de método sobre esa tabla, para que no haya que
confiar en ella:

- **20.000 réplicas y no 1.200.** La versión anterior publicaba cuatro
  decimales sobre 1.200 réplicas; dos corridas independientes de la misma
  cantidad caían a ambos lados del nominal. Una tabla que no puede
  distinguir 0.045 de 0.066 no puede sostener una afirmación sobre α.
- **600 sorteos en el bootstrap interno, no los 200.000 que usa
  `mirada.py`.** 200.000 × 4 miradas × 20.000 réplicas es inviable. El
  sesgo de usar menos está medido y su dirección es conocida: menos
  sorteos → más ruido en `V̂` → más sesgo hacia arriba del máximo → menos
  cruces, o sea **la tabla sale optimista**, no pesimista. Con 400 sorteos
  el sesgo en Z era de 0.15–0.49%; con 600 es menor. Se declara en vez de
  esconderse.

Lo medido sobre la ventana antecedente, como parámetro de estorbo de
varianza (misma clase de acto que `p_d` y el DEFF, ver §A2 — no se computa
ninguna ventaja): **ac1 = −0.135 ± 0.171 sobre 34 fechas.** El signo es
negativo, que es la dirección benigna; pero el error estándar dice que
**los datos de hoy no distinguen 0 de +0.2**, así que el argumento "está
medido y da negativo" no alcanza y no se usa.

Un rasgo estructural que amortigua, y que no se diseñó a propósito: **la
mirada donde `V̂` es menos confiable (la 1, con ~51 fechas) es la que
tiene el umbral más alto (4.048).** El conservadurismo temprano de
O'Brien-Fleming y la debilidad del bootstrap están anti-correlacionados, y
eso es parte de por qué la exposición de la tabla no es peor. Se dice como
observación cualitativa, verificable en la propia tabla de umbrales de
§A3.4; **no se le pone cifra** porque descomponer el α global por mirada
es un cómputo que no está en este repo.

**Qué obliga esto en cada acta:** reportar `ac1` con su EE. Si sale
distinguible de cero, `mirada.py` lo dice en el acta y el veredicto no se
lee sin ese dato al lado.

#### Un residuo menor, declarado sin número porque no lo tiene

La afirmación "re-estimar la varianza degrada la potencia, no el α" vale
si `V̂` es **proporcional entre miradas**. Si deriva, las fracciones de
información dejan de ser exactamente 0.25/0.50/0.75/1.00 y el α real se
mueve. **No se publica una cifra para esto porque no está computada en
este repo**, y una cifra sin código atrás es exactamente lo que este
documento le reprochó dos veces a sus versiones anteriores. Lo que se
declara es la dirección y el orden de magnitud esperados: es de segundo
orden frente a la exposición por correlación serial de la tabla de arriba,
que es el término dominante.

El arreglo canónico sería una función de gasto de Lan-DeMets evaluada
sobre la información observada. **No se implementa acá**: agregar una capa
que nadie de este proyecto probó nunca, para corregir un residuo que no
está medido, cambia un error acotado por uno desconocido.

Dos cosas más quedan congeladas acá, porque son elecciones y no
consecuencias:

- **Se usa el Z asintótico estudentizado, NO `mcnemar_exact`.** El exacto
  es conservador y su conservadurismo no está caracterizado bajo
  clustering: mezclarlo con una frontera calibrada para el asintótico
  daría un α real desconocido y menor que el nominal. Se pierde potencia
  sin poder decir cuánta. El exacto se puede reportar al lado como
  referencia; no decide.
- **El DEFF=3.6 sigue usándose para UNA sola cosa: planificar** — elegir
  N_max y las fechas del calendario. Si el clustering verdadero resulta
  mayor, el diseño llega a su fecha final con menos información efectiva
  de la planeada y por lo tanto con menos potencia. **Eso degrada la
  potencia, no el α**, y es el error que se puede tolerar: se declara y
  se reporta el intervalo, que va a salir más ancho.

### A3.3 Tamaño de muestra y potencia — con la corrección de la v2

Con MDE=10 pp, α=0.05 bilateral, fórmula de Connor (1987) para McNemar
pareado, p_d fija en la observada:

- n bajo independencia: **403 filas**.
- n corregido por agrupamiento (×DEFF 3.6): **1.450 filas** — pero ese es
  el n de un test de **muestra fija**.

**Un plan secuencial con ese mismo n NO tiene potencia 0.80: tiene
0.7906.** La razón es directa y la v1 la pasó por alto: el umbral final
del plan es 2.024, no el 1.96 de muestra fija. Esa diferencia se paga en
N o se paga en potencia; no hay una tercera opción.

Se elige pagarla en N:

> **N_max = 1.485 filas** (drift requerido 2.8352 contra 2.802 de muestra
> fija; factor 1.0241). Con eso la potencia del plan es 0.80 exacta —
> **bajo el estadístico idealizado, con la varianza conocida.**

**Y esa última aclaración importa, porque la regla del máximo se come esta
corrección.** Tomar `max` sobre tres estimadores ruidosos está sesgado
hacia arriba: infla `V̂` ~12% aun cuando no hay nada que corregir, lo cual
es la dirección segura para el α y la dirección cara para la potencia.
Medido: la potencia realizada con `max(1,5,10)` es **~0.76**, contra
~0.78 con bloque 1 solo. O sea: **la regla del máximo cuesta ~1.7 pp de
potencia y la corrección de N_max reparaba 0.94 pp.** El arreglo del
estimador se come al doble el arreglo del tamaño de muestra.

Eso **no está resuelto en este documento**, y se dice en vez de
disimularse. Hay dos salidas y las dos son de Nicolás, porque las dos
mueven el calendario o el estándar:

1. **Recomputar N_max** contando el sesgo del máximo — más filas, más
   tarde.
2. **Declarar que la potencia del plan es ~0.76 y no 0.80**, que es la
   salida barata y honesta: significa que si la ventaja real es de 10 pp,
   el diseño la detecta tres de cada cuatro veces en vez de cuatro de cada
   cinco.

Va junto con la decisión del α (ver el principio del documento): son la
misma familia de elección y conviene tomarlas de una vez.

### A3.4 Gasto de alfa: O'Brien-Fleming

Fronteras exactas por recursión numérica, validadas contra la literatura
(ver "De dónde salen los números"):

| Mirada | Información | n filas | Pocock: Z / α nominal | **O'Brien-Fleming: Z / α nominal** |
|---|---|---|---|---|
| 1 | 25% | 371 | 2.362 / 0.01819 | **4.048 / 0.00005** |
| 2 | 50% | 742 | 2.362 / 0.01819 | **2.862 / 0.00420** |
| 3 | 75% | 1.114 | 2.362 / 0.01819 | **2.337 / 0.01943** |
| 4 (final) | 100% | 1.485 | 2.362 / 0.01819 | **2.024 / 0.04297** |

α global exacto: Pocock 0.04996, OBF 0.04995. (La v1 congelaba
2.354/4.026/2.847/2.324/2.013, que dan **0.05122**.)

**Se elige O'Brien-Fleming.** Pocock detecta antes un efecto grande, pero
paga con un umbral final de 0.01819 — un efecto que llega justo al final,
que es el escenario más probable dado todo lo que se sabe, se perdería.
OBF casi no gasta alfa temprano (0.00005 en la primera mirada) y llega al
análisis final con 0.04297, casi el nominal completo. **Para una pregunta
que el proyecto lleva meses sin poder responder, conservar la potencia
del final importa más que la velocidad.**

### A3.5 Las miradas, con su fecha exacta — escritas, no decididas sobre la marcha

| Mirada | n filas | Fecha estimada | Umbral \|Z\| (OBF) |
|---|---|---|---|
| 1 | 371 | **2026-11-19** | 4.048 |
| 2 | 742 | **2027-02-07** | 2.862 |
| 3 | 1.114 | **2027-04-28** | 2.337 |
| 4 (final) | 1.485 | **2027-07-17** | 2.024 |

**La mirada la dispara el n, no la fecha.** Las fechas son estimaciones
al ritmo actual (6.5 filas/día hábil); si el ritmo cambia, se mueven las
fechas y **no** los n.

### A3.6 Futilidad — cuándo se para por no haber nada

Frontera **NO vinculante** (parar es una opción, no una obligación; no
consume alfa), por potencia condicional bajo el MDE < 20%:

| Mirada | n filas | Se puede declarar futilidad si Z observado < |
|---|---|---|
| 1 | 371 | −1.662 |
| 2 | 742 | +0.016 |
| 3 | 1.114 | +1.033 |

Leído en castellano: en la primera mirada solo se para si el modelo va
claramente PEOR que la constante; para la tercera, basta con que no haya
una tendencia positiva razonable para que seguir acumulando ya casi no
pueda cambiar el resultado.

**Características operativas del plan completo** (lo que la v1 no
publicaba, y es lo que dice si el diseño sirve o no):

| | Valor |
|---|---|
| Potencia, sin parar por futilidad | 0.8000 |
| Potencia, parando en la frontera de futilidad | 0.7914 |
| P(parar por futilidad \| H₁ cierta) — el costo | **0.0828** |
| P(parar por futilidad \| H₀ cierta) — el beneficio | **0.8531** |

Es la fila del medio la que justifica la frontera: **si de verdad hay una
ventaja de 10 pp, la futilidad la aborta por error el 8% de las veces**.
A cambio, si no hay nada, el 85% de las veces el diseño lo dice antes de
llegar a 2027-07-17. Ese es el canje, con sus dos números al lado.

### A3.7 Si el diseño se rompe — escrito antes de que pase

1. **Cambio de `MODELO_VERSION`** (un relevo, `GEMELO/RELEVO.md`): el
   diseño **termina ahí**, sin excepción. Las filas del modelo nuevo no
   son la misma población. Se reporta el resultado parcial con su n, se
   declara terminado por cambio de modelo, y el modelo nuevo arranca su
   propio diseño desde cero.
2. **Cambio de universo** (`UNIVERSO_VERSION`): si cambia la composición
   de tickers, el diseño continúa **solo si** el cambio afecta a menos
   del 10% de las filas acumuladas; si es más, mismo tratamiento que el
   punto 1.
3. **Hueco de sellado** (la máquina no selló varios días): las fechas
   faltantes simplemente no existen; el diseño se estira en calendario
   pero no cambia en n. Se actualiza la fecha estimada de cada mirada, no
   el n de cada mirada. Un hueco NO es motivo para adelantar una mirada.
4. **Cambio de convención de medición**: prohibido. La convención está
   congelada en `excluir_cero`. Si alguien encuentra una razón para
   cambiarla, el diseño termina y se rehace — no se recalcula sobre la
   marcha.
5. **Cualquiera de estos casos se registra en `DECISIONES.md` con acta**,
   con el n alcanzado y el resultado parcial. Un diseño abortado que se
   publica es un resultado; uno que se abandona en silencio es un sesgo.
6. **NUEVA (v2) — el p_d de la ventana nueva resulta muy distinto:** si
   en la mirada 1 la tasa de discordancia observada se aparta de 0.516 en
   más de ±0.08, se **recalcula N_max** con el p_d nuevo y se reescriben
   las fechas de las miradas 2 a 4. Los **umbrales no se tocan**: las
   fracciones de información t_k siguen siendo 0.25/0.50/0.75/1.00 del
   N_max nuevo. Recalcular el N por un parámetro de estorbo no gasta
   alfa; recalcular un umbral sí, y por eso está prohibido.

### A3.8 Gobernanza — con precio, no con prosa

La regla es la misma de la v1: **entre miradas no se computa el
estadístico**, y si alguien lo computa igual —y va a pasar, porque el
número está a un comando de distancia— esa consulta **cuenta como mirada
y se registra**. Lo que la v1 no tenía es el precio:

| Miradas furtivas a α nominal 0.05 | α real del plan |
|---|---|
| 0 (el plan como está escrito) | 0.0500 |
| 1 | **0.0939** |
| 2 | 0.1214 |
| 3 | 0.1368 |

**Una sola mirada furtiva casi duplica el α del plan.** No lo degrada un
poco: lo lleva de 0.05 a 0.094, que es peor que el pasivo entero de las
doce miradas históricas.

Tres reglas operativas que le dan cuerpo a esto:

1. **El script de la mirada se escribe AHORA**, junto con este documento,
   no en noviembre — y está escrito: `GEMELO/SECUENCIAL/mirada.py`, con
   sus tests en `tests/test_secuencial.py`. Un script que se escribe el
   día de la mirada es un script que se escribe viendo los datos. Su
   salida se commitea en la fecha del calendario, cruce o no cruce:

   ```bash
   python -m GEMELO.SECUENCIAL.mirada --mirada 1 --escribir
   ```

   Tiene tres candados estructurales, para que no se lo pueda usar mal:
   descarta por construcción toda fila anterior al congelamiento (hoy
   descarta las 253 y computa sobre 0); **se niega a computar el
   estadístico si el n todavía no llegó** al de la mirada, y dice cuánto
   falta; y abre `senales.db` en `mode=ro` a través de
   `backtest.linea_base`. El camino de cómputo está probado sobre datos
   sintéticos —incluido el caso ρ=1, donde V̂ tiene que dar ≈7— porque
   ejercitarlo contra las filas viejas sería exactamente lo prohibido.
2. **Una mirada saltada no se recupera.** Si la fecha pasa sin ejecutarla,
   esa mirada se declara omitida en el registro y el plan sigue con las
   que quedan. Omitir una mirada solo puede *reducir* el α, nunca
   aumentarlo, así que es seguro — pero tiene que quedar escrito, porque
   una mirada "omitida" que en realidad se hizo y no gustó es fraude.
3. **Cualquier análisis de sensibilidad tipo R2 sobre la ventana nueva
   cuenta como mirada.** Excluir un subconjunto de fechas y volver a
   computar es mirar otra vez: es exactamente lo que produjo los tres p
   retractados de §A1. Si se quiere hacer, se declara y se paga.

---

## A4. Lo que este diseño NO puede responder

**Mide si hay ventaja. No mide si la ventaja es condicional.** Son
preguntas distintas y la segunda es mucho más cara. La v1 publicaba un
solo número para esto y **el número que publicaba respondía la pregunta
equivocada**: calculaba cuánto cuesta detectar el MDE *dentro* de cada
subgrupo, lo cual **supone que el efecto es homogéneo entre subgrupos** —
que es precisamente la hipótesis nula de la pregunta condicional.

Los tres precios, para k=2 (una condición, alto/bajo):

| Pregunta | α | Qué supone | n filas | Se alcanzaría en |
|---|---|---|---|---|
| **(a) Interacción** — "la ventaja DIFIERE entre los dos grupos" | 0.05 | grupos de igual tamaño, igual `p_d`, y **MDE de interacción = 10 pp** | **5.799** | **ene-2030** |
| (b) MDE dentro de cada subgrupo (Bonferroni k=2) | 0.025 | efecto homogéneo entre grupos | 3.513 | sep-2028 |
| (c) "¿el grupo A tiene efecto?", con el efecto al doble | 0.025 | todo el efecto concentrado en A | 864 | mar-2027 |

**Solo (a) responde "¿es condicional?".** Cuesta 4× el efecto principal
porque una diferencia de diferencias tiene el doble de varianza y cada
grupo tiene la mitad de las filas. Tres advertencias sobre esa fila, para
que no se lea como un menú comparable:

- **(a) no supone "nada".** Supone grupos de igual tamaño, igual tasa de
  discordancia en los dos, y —lo más pesado— que el efecto de interacción
  que interesa detectar es del mismo tamaño (10 pp) que el efecto
  principal. Una interacción de 10 pp es un efecto mucho más grande que
  un efecto principal de 10 pp.
- **Los α no son los mismos.** (a) usa 0.05 porque es una sola prueba
  pre-especificada; (b) y (c) usan 0.025 por Bonferroni sobre dos
  subgrupos. Comparar los tres n sin ver esa columna es comparar peras
  con manzanas, y por eso la columna está.
- **(c) no es el piso de esta pregunta.** Detectar 20 pp dentro del grupo
  A establece que A tiene efecto; **no dice nada sobre A ≠ B**, que es lo
  que (a) mide. Se publica porque es informativo —incluso el escenario más
  favorable imaginable pide 864 filas nuevas— pero es el precio de **otra**
  pregunta, y esa pregunta sí se puede responder por otra vía.

Y para más subgrupos, en el caso (b), que es el que escala peor:

| Diseño condicional | n filas | Se alcanzaría en |
|---|---|---|
| k=4 (cuatro estratos) | 8.247 | **jul-2031** |
| k=6 (las seis condiciones candidatas de `GEMELO/CONDICIONAL/DISEÑO.md`) | 13.437 | **ago-2034** |

**Los números son desalentadores y por eso se publican.** La hipótesis
condicional que la corrida anterior intentó probar y terminó retractando
no fracasó por un error de método (aunque hubo errores de método): fracasó
porque **con este ritmo de acumulación, esa pregunta no es contestable
por esta vía en un plazo humano**. Un número desalentador computado vale
más que una intención: si alguien quiere responder la pregunta
condicional, ahora sabe que necesita otra fuente de datos, otro ritmo de
emisión, o aceptar que no se va a responder.

---

## A5. La fecha en que el proyecto va a saber algo

**2027-07-17**, si nada rompe el diseño y el ritmo de sellado se
mantiene. Antes de eso hay tres momentos en que podría saberlo: el
2026-11-19 (solo si el efecto es enorme), el 2027-02-07 y el 2027-04-28.

Y hay un cuarto desenlace, el más probable de todos según lo que el
proyecto sabe hoy: que en alguna de esas tres fechas el diseño declare
**futilidad** y la respuesta sea "si hay ventaja, es menor que 10 pp".
Bajo H₀ eso pasa el 85% de las veces, y suele pasar temprano.

Que exista una fecha —una sola, escrita, con un umbral escrito al lado—
es el punto de todo este documento. Hoy el proyecto no tiene ninguna: el
número se mira cuando crece, se comenta, y no hay ningún criterio previo
que diga qué contaría como respuesta.

---

## Lo que la v1 decía mal — registro de la corrección

`estadistico-adversario` rechazó la v1 el 31-ago-2026, antes del commit.
Su veredicto textual: *"no es 'tirar y rehacer': la arquitectura es
correcta y cuatro de los seis bloques de cómputo verifican exactos. Pero
un pre-registro congela sus números, y tres de los que se van a congelar
están mal."*

| # | Qué decía la v1 | Qué dice la v2 | Sección |
|---|---|---|---|
| D1 | Fronteras 2.354 / 4.026·2.847·2.324·2.013, α "0.051 confirmado" | 2.362 / 4.048·2.862·2.337·2.024, α exacto 0.04995 | A3.4 |
| D2 | "N=1.450, potencia 0.80" | N=1.450 da potencia 0.7906; N_max=1.485 da 0.80 | A3.3 |
| D3 | DEFF=3.6 congelado dentro del estadístico | fórmula pre-registrada con varianza re-estimada en cada mirada | A3.2 |
| D4 | "nunca hubo un positivo" | tres p<0.05 en subgrupos, retractados | A1 |
| D5 | "el pasivo es 0.091" | rango [0.09, 0.18]; 0.09 es el piso | A1 |
| D6 | un solo n para la pregunta condicional (3.513) | tres n para tres preguntas (5.799 / 3.513 / 864) | A4 |
| D7 | "las 248 no entran ni como prior" | no entran en el estadístico; sí como tres parámetros de estorbo | A2 |
| D8 | gobernanza en prosa | precio de la mirada furtiva + tres reglas operativas | A3.8 |

Lo que el revisor verificó exacto y **no** cambió: la estructura de
correlación `Z_k = B(t_k)/√t_k`, la implementación de Connor (403 filas),
la derivación de la futilidad y la aritmética del calendario.

### La v2 también fue rechazada — qué encontró el segundo dictamen

`estadistico-adversario` verificó los seis bloques de cómputo por dos
caminos independientes (recursión de Gauss-Legendre y Monte Carlo de
4.000.000 de réplicas) y confirmó D1, D2, D4, D5, D6, D7 y D8. Pero
rechazó la v2, y por una razón que hay que escribir sin ablandar:

> **D3 no estaba corregido: estaba mudado.** Se sacó el DEFF de adentro
> del estadístico y se puso en su lugar un estimador de varianza que
> promete un α de 0.05 y lo entrega **sólo si la autocorrelación entre
> fechas es cero** — un supuesto no declarado, imposible de acotar con 34
> fechas, y que las dos afirmaciones propias del proyecto (el bloque de 6
> fechas y el criterio R2) contradicen. Es el mismo argumento con el que
> este documento hundió a su propia v1.

| # | Qué decía la v2 | Qué dice la v3 | Sección |
|---|---|---|---|
| E1 | `BLOQUE_FECHAS = 1` (bootstrap de clúster puro) | `BLOQUES_FECHAS = (1, 5, 10)`, `V̂` = el máximo, con la exposición residual **medida y declarada** | A3.2 |
| E2 | §A3.2 nombraba `evaluacion.block_bootstrap`; el código llamaba a otra función | el documento describe el código que existe, y congela bloques, réplicas y semilla | A3.2 |
| E3 | `N_DRAWS = 5000` (±0.023 de Z sobre un umbral de 2.024) | 200.000 (±0.003) | A3.2 |
| E4 | `ZeroDivisionError` con varianza remuestreada nula | rama degenerada declarada, con test | `mirada.py` |
| E5 | la rama degenerada devolvía un dict sin las claves que se le leían | juego de claves idéntico siempre, con test | `mirada.py` |
| E6 | la cláusula 1 de A3.7 era prosa que el código no conocía | guard de `MODELO_VERSION`/`UNIVERSO_VERSION` que aborta | A3.7 |
| E7 | `--escribir` sobrescribía el acta en silencio | append-only: falla si el acta existe | A3.8 |
| E8 | correr sin `--escribir` no dejaba huella | toda corrida que computa deja línea en `miradas/registro.log` | A3.8 |
| E9 | se aplicaba el umbral del plan a cualquier n ≥ n_k sin avisar | aviso con la `t` real al lado | `mirada.py` |
| E10 | "TECHO" del pasivo | "escenario alto", con el ancla en n=80 declarada | A1 |
| E11 | §A4 (a) "Qué supone: nada"; α mezclados; (c) mal etiquetado | los tres supuestos escritos, columna de α, (c) re-etiquetado | A4 |
| E12 | el documento afirmaba una verificación por Monte Carlo que no existía en el repo | `fronteras.verificacion_mc`, versionada y con su IC | A3.4 |

**El hallazgo que más vale de los doce es E1, y no porque se haya
arreglado.** Se arregló a medias —la regla del máximo reduce la exposición
entre 17% y 55% según el nivel, y no la elimina—, y esa media está
publicada con su tabla en §A3.2. Que el arreglo fuera parcial es
justamente lo que el tercer dictamen convirtió en el motivo para NO
congelar.

### La v3 también fue rechazada — y por qué el documento no se congela

Tercer dictamen, misma disciplina. Verificó exactas las fronteras, el
pasivo, Connor, la futilidad, el calendario, los tres candados de
`mirada.py` y las dos validaciones externas. Lo que rompió fue **la única
tabla nueva de la v3**, que era su razón de ser:

| # | Qué decía la v3 | Qué dice la v4 |
|---|---|---|
| N1 | tabla de exposición residual que **no reproducía** desde el script sembrado (7 de 8 celdas) | recomputada con 20.000 réplicas; las cifras del documento salen del código |
| N2 | cuatro decimales sobre **1.200 réplicas**, sin intervalos — dos corridas de la misma cantidad caían a ambos lados del nominal | 20.000 réplicas, **IC de Wilson dentro de la tabla** |
| N3 | "corta ~60% en todos los niveles" | **17% / 29% / 44% / 55%** — la frase citaba el mejor caso como si fuera el promedio |
| N4 | N_max=1.485 daba potencia 0.80 | la regla del máximo cuesta ~1.7 pp de potencia y **reabre D2**; declarado, con sus dos salidas, ambas de Nicolás |
| N5 | `UNIVERSO_ESPERADO = None`, "se completa en la primera mirada" | `"4.6.0"`, hoy, con test — una constante que se completa después no está congelada |
| N6 | cinco cifras sin fuente en el repo (una de ellas impresa en el acta) | computadas o retiradas; no hay tercera opción |
| N7 | cinco comentarios describiendo la regla de la v2, uno de ellos emitido al acta | corregidos; la tabla vive en UN solo lugar |
| N8 | cuatro tests tautológicos, y ninguno sobre la simulación | reescritos como tests de comportamiento, más cuatro nuevos sobre la simulación |

**El defecto de fondo del tercer rechazo no es ninguno de esos ocho.** Es
que el documento declaraba α = 0.05, publicaba al lado que entrega hasta
0.079, y **no fijaba ninguna regla de decisión para ese caso** — sólo
"reportar la autocorrelación". Eso no es un criterio: es un descargo con
promesa de criterio futuro, y un criterio decidido después de ver datos es
exactamente lo que un pre-registro existe para prohibir.

Por eso este documento **no se congela**. La salida —declarar α = 0.10, y
mover la primera mirada a ~100 fechas— está costeada al principio, y es
una decisión de Nicolás.

Dos precisiones del segundo dictamen que corrigen a este documento y al
primero:

- La "nota honesta sobre la nota honesta" de más arriba **le daba la razón
  a quien no la tenía**: 0.7953 y N_max≈1520 no los reproduce nadie. La
  potencia real es 0.7905–0.7906 y N_max = 1485, por integración, por
  Monte Carlo de 4M y por el script de este repo.
- Sobre el c_B de O'Brien-Fleming los dos caminos discrepan en el tercer
  decimal (2.0240 acá, 2.0222 por Gauss-Legendre). La familia congelada
  gasta 0.04995 por un camino, 0.04991 por el otro y 0.05001 ± 0.0002 por
  Monte Carlo. La diferencia en α es de 1e-4 y no mueve nada, pero queda
  dicha.

Una nota honesta sobre la nota honesta: el revisor computó la potencia en
0.7953 y N_max en ~1.520; este documento computa 0.7906 y 1.485, por dos
caminos (integración y Monte Carlo de 400.000 réplicas, que coinciden en
0.0005). La diferencia es de tercer decimal y **no cambia ninguna
conclusión** — las dos dicen lo mismo, que es que la v1 no tenía potencia
0.80. Se congela 1.485 porque es el que sale del código versionado de
este repo.

---

## Qué NO se hace en este documento

- No se toca `motor.py`, `senales.py`, `snapshot.py`, `universo.py`, ni
  ninguna fila sellada.
- No se decide el MDE definitivo (§A3.1), que es de Nicolás y cambia el
  horizonte por un factor de ocho.
- No se re-analiza la ventana sellada actual. Las 248 filas de hoy son
  antecedente; este documento las usa como parámetros de estorbo (§A2) y
  no computa ninguna cifra de ventaja sobre ellas — el propio encargo de
  esta corrida marcó volver a analizarlas como "la trampa de esta etapa".
- **No se ejecuta ninguna mirada.** `mirada.py` existe y corre, pero hoy
  devuelve "TODAVÍA NO": hay 0 filas nuevas y hacen falta 371. La primera
  mirada es el 2026-11-19 y no antes.
- **No se avisa solo cuando se alcanza un n.** No hay job ni timer que
  dispare la mirada; la fecha hay que recordarla. Es la deuda que este
  documento deja abierta, y está declarada como tal.
