# El diseño secuencial — pre-registro

**Estado: versión 6 — NO CONGELADA. QUINTO RECHAZO.**

> **El quinto dictamen del `estadistico-adversario` salió RECHAZADO**, y
> como era la condición del congelamiento, el documento no se congela.
> Está en `GEMELO/resultados/dictamen_17/estadistico_adversario.md` (977
> líneas), y el `curador-epistemico` rechazó además la primera redacción de
> esta misma v6 con doce bloqueantes
> (`dictamen_17/curador_epistemico.md`). Un rechazo bien explicado es un
> resultado y no se maquilla: esta línea lo dice antes que cualquier otra
> cosa.
>
> **Lo que el quinto dictamen confirmó, y es la parte difícil:** las
> **cuatro condiciones del cuarto rechazo están atendidas de verdad y no
> maquilladas**, y «el rechazo no viene de ellas». El documento **reproduce
> el día que se firma**, que era la vara textual del cuarto dictamen.
> También verificó en verde el DEFF de planificación (V̂ máximo 3.618 contra
> 3.6 supuesto), el ancla y su candado, las dos declaraciones de dirección
> de sesgo, y que los tests nuevos son de comportamiento. Y encontró que el
> error estándar de Bartlett para `ac1` es **conservador por 1.16** (el
> verdadero es 0.142 contra 0.164), después de intentar romperlo.
>
> **Por qué rechaza igual.** Tres defectos que esta corrida no buscaba:
>
> 1. **D1 — el documento declara congelado un estadístico cuyo clúster está
>    sin firmar, y la opción que él mismo recomienda contradice el texto
>    congelado.** §A3.2 congela «remuestreando FECHAS DE EMISIÓN»; la
>    opción que la tarjeta §91 recomienda cambia la clave a la sesión
>    objetivo. Firmarla dejaría falso un párrafo congelado e invalidaría la
>    tabla de exposición residual, y con ella la banda [0.046, 0.079], que
>    es el único ítem que los dictámenes 3 y 4 dejaron bloqueante. **No es
>    un número que no reproduce: es una incompatibilidad entre lo que se
>    declara congelado y lo que se pone a la firma.**
> 2. **D2 — `p_d` y `f` son la MISMA cantidad, y el abanico mezclaba
>    réplicas.** Verificado a 17 decimales sobre las 262 filas. El
>    documento metía los bordes del IC del MDE en Connor con `p_d` fija en
>    su punto, o sea combinando réplicas distintas del mismo remuestreo, y
>    **los dos extremos caían FUERA del intervalo honesto**. Corregido en
>    esta versión (§A3.1.d): con `p_d = f` por réplica, `N_max` da **mediana
>    1.920, IC95 [1.025, 4.153]**. El titular «dos años de diferencia entre
>    los dos bordes» y la fecha de 2029 eran artefactos del emparejamiento
>    y están **retirados**.
> 3. **D3 — la mitad de las fechas aporta `d_j` = 0 exacto**, y el proyecto
>    ya lo había medido el 2-sep sin que nadie volviera a citarlo: `f` por
>    fecha es perfectamente degenerado (19 fechas con 0, 18 con 1, ninguna
>    intermedia), así que **20 de 37 fechas no informan a `b−c`** y la
>    mirada 1 descansa en ~25 fechas informativas, no en ~51. Declarado en
>    §A3.2.
>
> **Once exigencias numeradas, las cinco primeras bloqueantes.** Su estado
> está en la tabla del final del documento y en la bitácora de la corrida
> 17. Las que esta versión atendió: **E2** (la propagación conjunta), **E8**
> (los grupos son 11 de DOS y 4 de CUATRO, no 15 pares), **E9**, **E10**,
> **E11**, y las partes declarativas de **E1**, **E3**, **E4** y **E5**. Las
> que **NO**: **E6** (poner número al pasivo de §A1 con el simulador) y
> **E7** (validar los tres estimadores que deciden contra verdad conocida).
> Las dos son corridas propias y están en tarjetas con su costo.
>
> **Y la observación final del dictamen, que no es una exigencia y es la que
> más conviene leer antes de firmar dos años de calendario:** D2 y D3 no son
> objeciones al plan, son la **descripción del experimento**. La pregunta
> direccional se juega **sólo en las noches en que el SOX baja y el modelo
> dice BAJA**; en las otras el campeón y la baseline son la misma cosa por
> construcción. Un diseño secuencial sobre la dirección es, a este ritmo,
> un diseño sobre la mitad de sus propias fechas.

> **Qué cambió del estado anterior.** La v5 estaba rechazada por cuarta vez
> y cerraba diciendo «no hay v6». La corrida 17 (25-oct-2026) atendió las
> cuatro condiciones que el cuarto dictamen puso para levantar el rechazo,
> corrigió en su sitio las cifras que habían dejado de reproducir y dejó en
> tarjetas con números las decisiones que son de Nicolás. **Esta corrida no
> congela nada**: el congelamiento es un acto de Nicolás y lo que sigue
> abierto está listado abajo, con su plazo.
>
> **Las cuatro condiciones, y en qué quedaron:**
>
> 1. **La regla de deduplicación — ATENDIDA EN PARTE, y el reparto cambió.**
>    Hay DOS reglas y la v5 las trataba como una. La de FILAS está
>    **firmada desde el 1-sep-2026** (`DECISIONES.md` §60 y §61) y no es
>    ninguna de las dos opciones que la v5 discutía: conserva la fila cuya
>    `sesion_objetivo` corresponde a su `available_at`, deja las dos cuando
>    las dos corresponden, y prohíbe elegir por frescura. Desde hoy los dos
>    lados usan esa regla, así que el defecto descalificante —parámetro
>    deduplicado contra estimador sin deduplicar— está cerrado. Lo que
>    queda abierto es la regla del **ESTIMADOR**: qué hace el estadístico
>    con los pares que la regla de filas CONSERVA. Está en
>    `mirada.REGLA_DEDUP_ESTIMADOR = None`, con candado y test, y en la
>    tarjeta §91.
> 2. **§A3.1.b con intervalos — ATENDIDA, y el resultado es peor de lo que
>    la v5 creía.** La razón 2 ya estaba retractada. La **razón 1 también
>    se cae cuando se le pone el intervalo**: la tasa de acierto que el
>    benchmark exige y la que la baseline consigue quedan a 0.1 pp una de
>    otra, con intervalos que se superponen. §A3.1.b lo dice ahí.
> 3. **El MDE en la escala del endpoint con su intervalo — ATENDIDA.**
>    Sobre la ventana antecedente ANCLADA y con la regla firmada:
>    **8.51 pp, IC95 [4.94, 13.09]** a 25 pb. El intervalo propaga DOS
>    insumos (`f` y E|gap|) por clústeres de día; el tercero, la simetría de
>    magnitudes, queda declarado **fuera** con su sensibilidad al lado.
> 4. **El ancla de `mde_desde_v6.py` — ATENDIDA.** El script ya no escribe
>    SQL: la ventana la define `ventana_antecedente.py` con dos cortes
>    explícitos, y hay tests de comportamiento que agrandan la base y
>    verifican que la medición no se mueve. **Y había un segundo archivo con
>    la misma falla, peor:** `diseno_secuencial.ac1_ventana_antecedente`
>    leía la base VIVA, así que correrlo hoy habría computado `ac1` sobre la
>    población — una mirada furtiva sin huella. Corregido.
>
> **La frase del cuarto dictamen sigue siendo la vara:** *un pre-registro
> que no reproduce el día que se firma no está congelado, está fechado.*
> **Y hay que decirla con una asimetría**, que el `curador-epistemico`
> obligó a declarar: la mitad del documento que vive en la **ventana
> antecedente** (el MDE, `p_d`, `ac1`, E|gap|) **sí reproduce**, porque está
> anclada por dos cortes y hay tests que lo fijan. La mitad que vive en el
> **calendario** (el ritmo, el MDE crítico, las cuatro fechas de cada
> mirada) **no reproduce mañana, y no debe**: la población crece todos los
> días hábiles, así que es una **medición puntual**, de la misma clase que
> las cifras de la §2 que el WS5 tuvo que anclar el 30-ago. Lo que necesita
> no es un ancla que la congele sino **su instante declarado**, y lo tiene:
> `GEMELO/resultados/tabla_firma_17.json`, sellado con su `medido_en`. Lo
> que falta son firmas; de cómputos falta volver a correr `tabla_firma.py`
> el día de la firma, porque sus cifras habrán cambiado.
>
> **LO QUE ESTA CORRIDA ENCONTRÓ Y NO ESTABA ENTRE LAS CUATRO
> CONDICIONES**, porque es lo que de verdad apura:
>
> * **El plazo ya empezó a correr y para parte del rango está vencido.** El
>   ritmo real de la población es **7.579 filas por día hábil** —medido por
>   conteo sobre 38 días hábiles, contra las 6.56 que la v5 proyectaba desde
>   la ventana antecedente—, así que todas las miradas caen antes de lo
>   escrito. **El MDE crítico —el valor por encima del cual la primera
>   mirada ya está vencida— es 11.09 pp como PUNTO, IC95 [8.93, 12.81]**, y
>   cae DENTRO del IC95 del MDE. Así que **cuál de las opciones arranca
>   vencida está indeterminado entre 8.92 y 12.79 pp**; lo que sí está
>   medido es que por encima de 12.79 pp lo está para todo el intervalo de
>   `f`, y el borde superior del IC del MDE (13.09 pp) queda por encima.
>   La tabla completa está en §A3.1.d y sale de `tabla_firma.py`.
> * **Las cifras de la v5 estaban calculadas sobre un conjunto de filas que
>   el proyecto retiró.** La decisión D1 de Nicolás (acta §78, 3-sep-2026)
>   derogó la rama sin deduplicar; sus cifras están en
>   `GEMELO/cifras_retiradas.md` y no se citan más. La v5 se escribió dos
>   días antes y toma de ahí su `p_d`, su E|r| y su ritmo. Todos
>   recomputados.
> * **El pasivo de §A1 está incompleto.** La tabla termina el 31-ago y
>   hubo al menos cuatro miradas más a la ventana antecedente después, una
>   de ellas una **publicación** (acta §78). Ver §A1.
> * **La población está expuesta por una vía que la v5 no contempla.** No
>   se computó ninguna ventaja sobre ella —`mirada.py` nunca corrió y
>   `miradas/registro.log` no existe—, pero la API publica fila por fila
>   `Gap real %` y `Acierto gap` de las 100 verificaciones más recientes,
>   que hoy son todas de la población. Con esas dos columnas y la fecha, el
>   estadístico entero es reconstruible por quien lea la página. Ver §A3.8.

**Lo que el acta de congelamiento dice es lo que se propone congelar**, y
cada parámetro que es decisión de Nicolás aparece ahí como **SIN FIRMAR**
con su tarjeta al lado. Escrito el 31-ago-2026 y corregido en su sitio el
25-oct-2026, antes de la primera mirada. Toda cifra sale de
`ventana_antecedente.py`, `mde_desde_v6.py`, `tabla_firma.py`,
`diseno_secuencial.py` y `fronteras.py`, versionados y reproducibles — la
lección operativa de `DECISIONES.md` §45. El registro de cambios de la v5 a
la v6 está al final, en tabla, como los de la v1 a la v4.

**Qué se PROPONE congelar (todo lo que no depende del MDE):** el α y su
banda, las fronteras de O'Brien-Fleming, **la FORMA del estadístico** y su
varianza cluster-robusta, la regla de futilidad, el pasivo declarado **como
PISO e incompleto** (§A1), las cinco cláusulas de ruptura y toda la
gobernanza. Nada de esto está congelado todavía: lo congela la firma.

> **Corrección del quinto dictamen (D1), y es la razón formal de su
> rechazo.** Esta línea decía «el estadístico y su varianza
> cluster-robusta», a secas, nueve líneas antes de decir que la regla del
> estimador «sí mueve la varianza y por lo tanto el estadístico». **No
> pueden ser las dos verdaderas.** Lo que se propone congelar es la
> **forma** del estadístico —`Z = [(b−c)/√(b+c)] / √V̂`, con `V̂`
> cluster-robusta re-estimada en cada mirada, el máximo de tres bloques,
> réplicas y semilla— y **NO la clave del clúster**, que es el parámetro de
> la tarjeta §91 y está SIN FIRMAR.
>
> **Y la incompatibilidad no se arregla con esta aclaración.** §A3.2 punto 3
> describe el procedimiento «remuestreando FECHAS DE EMISIÓN», y la opción
> que §91 recomienda cambia la clave a la sesión objetivo: si se firma, los
> bloques 5 y 10 corren sobre otro orden, el DEFF de planificación medido
> sobre clústeres de fecha de emisión pierde su interpretación, y **la tabla
> de exposición residual —y con ella la banda [0.046, 0.079]— deja de
> describir al estimador**. Esto es la exigencia **E1** y **no está
> resuelto**: resolverlo es recomputar la tabla de exposición para las DOS
> claves, que es una corrida de 20.000 réplicas por rama, o retirar la
> recomendación de §91. Las dos salidas son de Nicolás y están en la
> tarjeta §91.

**Qué queda abierto: CUATRO cosas, no una.** La v5 decía «una sola», el
MDE, y proponía un valor que el mismo día quedó **RETIRADO**
(`GEMELO/cifras_retiradas.md`, acta §56: se derivó en la escala del retorno
de sesión cuando el endpoint congelado es `acierto_gap`). Hoy las cuatro,
cada una con su tarjeta: el **MDE** (§90, y sólo mueve `N_max` y el
calendario, no toca ningún umbral), la **regla de deduplicación del
estimador** (§91, que sí mueve la varianza y por lo tanto el estadístico),
la **potencia** (§92) y la **población** (§93).

> **Texto de la era v3 (31-ago-2026), conservado y fechado.** Decía: «No
> congelarlo esta noche es el resultado, no una tarea pendiente. El
> documento fue rechazado tres veces por `estadistico-adversario` en el día
> en que se escribió... El tercero dejó una corrección que no es mecánica:
> el plan promete α = 0.05 y sobre el rango plausible de autocorrelación
> entrega entre **0.046 y 0.079** (la banda publicada; esta línea decía
> «0.048 y 0.080», que no coincidía con la banda que el resto del documento
> cita). Se puede arreglar declarando α = 0.10 de entrada, lo cual cambia el
> estándar científico con el que este proyecto va a juzgar su propio
> modelo. Esa es una decisión de Nicolás».
>
> **Esa decisión YA SE TOMÓ**: Nicolás firmó **α = 0.05 nominal con la banda
> publicada** el 31-ago-2026, y la sección siguiente la registra. El bloque
> se conserva porque es el origen de la decisión, no porque esté pendiente;
> leerlo como pendiente era una contradicción con el acta de la línea de
> abajo, y la cazó el `curador-epistemico`.

## El α, decidido: 0.05 nominal con la banda publicada

**Decisión de Nicolás, 31-ago-2026.** El plan declara **α = 0.05
nominal** y publica **la banda [0.046, 0.079]** como limitación declarada,
con el compromiso —y el estimador ya escrito, §A3.2— de reestimarla cuando
el N permita acotar la autocorrelación.

**La razón, que es de estilo y no de estadística:** el proyecto publica su
incertidumbre en todo lo demás. Cada tasa de acierto lleva su Wilson, cada
predicción su intervalo del 80%, y cuando el n no alcanza la interfaz dice
"pendiente" en vez de rellenar. Declarar α = 0.10 para que la cifra fuera
"verdadera" habría sido **absorber la incertidumbre dentro de un número
más redondo**, que es exactamente lo contrario del estilo de la casa.

Se descartó explícitamente la recomendación que este documento hacía en su
v4 (subir a 0.10). La banda va en el cuerpo, no en nota al pie, con el
mecanismo que la produce y con el N que haría falta para cerrarla.

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

## El acta de congelamiento

Lo que un pre-registro tiene que poder mostrar dentro de dos años, sin que
nadie dependa de la memoria de nadie:

**NINGUNA LÍNEA DE ESTA TABLA PREDICA «CONGELADO» DE ESTE PRE-REGISTRO.** Es la plantilla del acta,
con lo ya decidido citado con su fuente y lo que falta marcado **SIN
FIRMAR** con la tarjeta que lo decide. El día que Nicolás firme, la receta
de congelamiento del final dice exactamente qué constante cambia en qué
archivo y qué línea de esta tabla se llena.

| | |
|---|---|
| **Fecha de congelamiento** | **SIN FIRMAR** — la pone la firma. El 2026-08-31 que esta línea traía era la fecha en que se *propuso* congelar, sobre un documento que nunca se congeló |
| **Commit base** | **SIN FIRMAR** — lo agrega el cierre de la corrida que aplique la firma |
| **α declarado** | **0.05 bilateral**, con la banda **[0.046, 0.079]** publicada (§A3.2). **DECIDIDO** por Nicolás el 31-ago-2026, ver la sección siguiente |
| **Familia de gasto de α** | O'Brien-Fleming, K=4 miradas equiespaciadas en información |
| **Umbrales** | 4.048 / 2.862 / 2.337 / 2.024 — α global exacto 0.04995. Verificados contra Jennison-Turnbull; no dependen del MDE |
| **Estadístico** | `Z = [(b−c)/√(b+c)] / √V̂`, V̂ = max sobre bloques (1,5,10), 200.000 sorteos, semilla 20260831 |
| **Clúster del estadístico** | **SIN FIRMAR** — tarjeta **§91**. Es la regla de deduplicación del ESTIMADOR (`mirada.REGLA_DEDUP_ESTIMADOR`), distinta de la regla de FILAS, que sí está firmada (§60 y §61) |
| **Regla de filas** | `backtest.linea_base.deduplicar_por_sesion`, **FIRMADA el 1-sep-2026** (actas §60 y §61). `keep="last"` PROHIBIDA |
| **Convención** | `excluir_cero`, congelada en `GEMELO/DISEÑO.md` §2.8 |
| **Población** | filas con fecha de emisión **posterior al 2026-08-31**. **La fecha de inicio es SIN FIRMAR** — tarjeta **§93**: el documento nunca se congeló, así que la población lleva casi dos meses acumulando bajo exposición declarada |
| **Ventana antecedente** | emisión ≤ 2026-08-31 **y** sello ≤ 2026-09-02, en `ventana_antecedente.py`. Los dos cortes, con el candado que verifica que la ventana está cerrada |
| **MDE** | **SIN FIRMAR** — tarjeta **§90**. Derivado en §A3.1: **8.51 pp, IC95 [4.94, 13.09]** a 25 pb, en la escala del endpoint. Sólo mueve `N_max` y el calendario. El **MDE crítico es 11.09 pp, IC95 [8.93, 12.81]**, y cae dentro del intervalo del MDE: **cuál opción arranca con la mirada 1 vencida está indeterminado entre 8.93 y 12.81 pp**, y P(vencida si se firma la regla del punto) = 0.0614 [0.0569, 0.0663] |
| **Potencia** | **SIN FIRMAR** — tarjeta **§92**: 0.80 con la varianza conocida, **≈0.75** descontando el sesgo de la regla del máximo. **Sin más decimales: el 12 % de inflación de `V̂` no tiene intervalo.** Hay que recomputar `N_max` o declarar la cifra baja |
| **`p_d` de planificación** | 0.4924 (129/262) sobre la ventana antecedente anclada con la regla firmada. Parámetro de estorbo: mueve N y fechas, no el α |
| **Pasivo de miradas anteriores** | **α ≥ 0.09, SIN EXTREMO SUPERIOR ESTABLECIDO** (exigencia E6/F10). El rango [0.09, 0.18] se computó sobre las doce miradas hasta el 31-ago y la cuenta está **incompleta** por cuatro miradas posteriores (§A1): agregar miradas SUBE el α, así que 0.18 no es un techo y publicarlo como rango diría menos de lo que el documento sabe |
| **Ritmo de acumulación** | **7.579 filas/día hábil**, MEDIDO por conteo sobre la población (288 filas en 38 días hábiles, 2026-09-01 a 2026-10-22) |
| **Validación externa** | Jennison-Turnbull (fronteras) y Armitage-McPherson-Rowe 1969 (pasivo) |
| **Dictámenes adversarios** | rechazado 4 veces y corregido 4 veces. **El quinto dictamen es la CONDICIÓN de este congelamiento y esta versión NO lo da por favorable**: su veredicto va en `GEMELO/resultados/dictamen_17/`, y si rechaza, el documento no se congela. El `curador-epistemico` rechazó la primera redacción de esta v6 con 12 bloqueantes, atendidos antes de cerrar |

**Los candados que hacen esto exigible, y los dos que NO existen.**
`mirada.py` tiene **dos** constantes en `None` y **se niega a computar**
mientras alguna siga así: `MDE_FIRMADO` y `REGLA_DEDUP_ESTIMADOR`. Correr
una mirada con un N_max que nadie fijó es elegir el tamaño de muestra
después de ver los datos; correrla con un clúster que nadie fijó es elegir
la varianza después de verlos, que es el denominador del mismo estadístico.
Los dos tienen test.

**Pero de los CUATRO parámetros sin firmar sólo dos tienen candado**, y hay
que decirlo porque el párrafo de arriba se lee como si el régimen entero
estuviera hecho estructura: la **potencia** (§92) vive en prosa, y la fecha
de inicio de la **población** (§93) **ya está escrita** en
`mirada.FECHA_CONGELAMIENTO = "2026-08-31"` y es operativa —el candado
estructural que descarta la ventana antecedente la necesita—, aunque el
acta la llame SIN FIRMAR. O sea que uno de los cuatro parámetros está
escrito en el código sin firma, por una razón buena, y eso es una asimetría
declarada y no un candado. Lo cazó el `curador-epistemico`.

## El punto de partida, que no se discute acá

Dos corridas de análisis pesado sobre la ventana sellada de entonces
terminaron en "no se puede decidir entre hay condición y es azar"
(`GEMELO/resultados/concentracion.md`). Eso no fue un fracaso del
análisis: **esa cantidad de filas no alcanza**. Más estadística sobre los mismos
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
| 5 | 26-ago | 184 | −3.3 pp (RETIRADA) | 0.60 | excluir_cero, subset R2 | `DECISIONES.md`:2199-2201 |
| 6 | ~27/28-ago | 223 | +4.0 pp | 0.4633 | excluir_cero (restatada) | README, commit `aa16a89` |
| 7 | 30-ago | 245 | +7.8 pp | 0.1158 | estricta | `DECISIONES.md`:3274 |
| 8 | 30-ago | 240 | +6.7 pp | 0.1849 (RETIRADA) | excluir_cero | `DECISIONES.md`:3282 |
| 9 | 30-ago | 253 | +7.5 pp | 0.1158 | estricta | `DECISIONES.md`:3586 |
| 10 | 30-ago | 253 | +5.5 pp | 0.2542 | verificador | `DECISIONES.md`:3587 |
| 11 | 30-ago | **248** | **+6.5 pp** | **0.1849** | **excluir_cero** — las tres RETIRADAS, ver la marca de abajo | `DECISIONES.md`:3588 |
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

> **Marca de retiro sobre la tabla de arriba (agregada el 25-oct-2026).**
> Las cifras de las filas 7 a 12 pertenecen a la rama de filas SIN
> deduplicar, que la decisión D1 de Nicolás **derogó** el 3-sep-2026 (acta
> §78) y cuyos valores quedaron **RETIRADOS** en
> `GEMELO/cifras_retiradas.md`. Se conservan acá porque esta tabla es el
> registro de **qué se miró**, y lo que se miró fue eso: borrarlas haría
> desaparecer la mirada junto con la cifra. No se citan como estado
> vigente en ninguna otra parte de este documento.

### Lo que la tabla NO cuenta, y es un hallazgo de la corrida 17

**La cuenta se corta el 31-ago y el proyecto siguió mirando la ventana
antecedente después.** Con el criterio implícito del propio documento —
cuentan las decisiones registradas, no cada refresco del verificador —
hubo al menos cuatro miradas más, todas con acta:

| Fecha | Qué se miró | Acta | Peso |
|---|---|---|---|
| 1-sep | las tres ramas de la regla de deduplicación, comparadas antes de firmar | §60 | tres cifras del mismo n |
| 1-sep | la rama confirmada, con su `b`/`c` y su p | §61 | **cambió el estadístico principal** |
| 3-sep | la rama confirmada **PUBLICADA** en el README y en once bloques más | §78 | **publicación**, no cómputo interno |
| 7/8-sep | la rama «+ coherencia», con su intervalo de clúster de día | §82.3 | cifra nueva, no publicada |

**La de §78 es la más cara de las cuatro y por una razón de clase, no de
grado: es una publicación.** Las otras tres son cómputos que quedaron en
actas; §78 movió la portada. El argumento que la v1 de este documento
hacía a su favor —«ninguna afirmación publicada depende de un p que haya
cruzado el umbral»— **ya no vale como estaba escrito**: la cifra publicada
desde el 3-sep tiene un McNemar de filas que cruza α, y lo que la sostiene
es que el intervalo de clúster de día contiene el cero y que **es ése el
que decide** (acta §61). La afirmación correcta hoy es más larga y más
débil: ninguna afirmación publicada depende de un **intervalo de clúster de
día** que excluya el cero.

**No se le pone cifra a esta ampliación, y la razón es la misma por la que
§A1 no le pone cifra a la objeción del piso:** las cuatro miradas son
sobre la ventana ANTECEDENTE, que es la que el pasivo cubre, y el modelo
browniano no admite dos miradas en la misma fracción de información. Lo que
sí se puede decir es la dirección: **el rango [0.09, 0.18] es un piso más
bajo de lo que era**, porque hay cuatro oportunidades más de cruzar un
umbral sobre casi las mismas filas. Que el `estadistico-adversario`
dictamine si eso admite un número; esta corrida no se lo inventa.

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
  la tasa de discordancia **`p_d = 129/262 = 0.4924`** que fija el n de
  Connor; el efecto de diseño `DEFF ≈ 3.6` medido sobre ellas; y el ritmo
  de acumulación, que fija el calendario.

  > **Corregido el 25-oct-2026, y las tres correcciones son de la misma
  > familia.** (a) El `p_d` que esta línea traía se computaba sobre la rama
  > de filas que la decisión D1 derogó el 3-sep (acta §78); el de ahora
  > sale de la ventana antecedente **anclada** con la regla de filas
  > firmada, por `mde_desde_v6.py`. (b) El ritmo ya no se proyecta desde la
  > ventana antecedente: la población tiene 38 días hábiles de historia y
  > el ritmo se **mide** ahí, por conteo (§A3.5). (c) De los tres, el
  > único que se recomputa en cada mirada es ninguno: los tres son de
  > planificación. Lo que se recomputa en cada mirada es `V̂` (§A3.2).
  >
  > **Se PUBLICA y se USA `b+c`, nunca `b−c`.** La suma es el parámetro de
  > estorbo que esta sección autoriza; la diferencia es la ventaja, y el
  > documento prohíbe **publicarla o usarla** sobre la ventana antecedente,
  > también como control. `mde_desde_v6.py` está escrito para que no pueda.
  >
  > **La redacción anterior decía «se computa … y NUNCA se computa», y era
  > inaplicable por construcción** (E10 del quinto dictamen): §A2 autoriza
  > `ac1`, y `ac1` se calcula sobre las contribuciones `d_j`, cuya suma
  > **ES** `b−c`. Prohibir computarla y autorizar `ac1` es una
  > contradicción. Lo exigible es la prohibición sobre **publicar y usar**,
  > que es donde está el costo en α, y así queda escrita.
  >
  > **Y `p_d` ES `f`, por identidad y no por coincidencia.** La baseline
  > siempre dice «al alza», así que el modelo sólo puede discordar de ella
  > donde dice BAJA; bajo `excluir_cero` el conjunto discordante **es** el
  > conjunto BAJA, y por lo tanto `p_d = f = 129/262 = 0.4924`. Decirlo
  > importa por dos razones: sin esto la igualdad de los dos números parece
  > un error de copia, y **con esto se ve que el mismo parámetro recibe dos
  > tratamientos** — `f` entra al MDE con su intervalo y `p_d` entra a
  > `N_max` como punto (§A3.3). El MDE crítico de §A3.1.d hereda de ahí su
  > propio intervalo.

> **QUÉ ESTADÍSTICO DECIDE, Y UNA ACTA QUE ESTE DOCUMENTO NO CITABA.**
> El acta **§61** (1-sep-2026, instrucción directa de Nicolás) decidió que
> **«para la ventana sellada, el estadístico principal del proyecto deja de
> ser el McNemar y pasa a ser el intervalo que respeta el clúster de día»**,
> y escribió al lado la frase que lo resume: **«cruzar α no es tener
> evidencia»**. La medición que la sostiene es dura: sobre la matriz de
> bifurcaciones recomputada tras la firma de la regla de filas, **59 de 192
> celdas cruzaban α por McNemar y 0 de 192 por el estimador de clúster**
> (201 de 768 contra 0 de 768 en la matriz PREVIA, con `dedup` todavía como
> eje), y la diferencia no la produce ninguna bifurcación de diseño sino el
> supuesto de independencia.
>
> Este documento se escribió el día anterior y **no citaba esa acta**. Hay
> que decir las dos cosas:
>
> * **En sustancia el plan está del lado correcto de §61.** El estadístico
>   de §A3.2 no es McNemar crudo: es McNemar **estudentizado por una
>   varianza cluster-robusta re-estimada en cada mirada**, y §A3.2 punto 6
>   obliga a reportar el intervalo siempre («un cruce sin intervalo no
>   cuenta como resultado»). `mirada.py` imprime el McNemar exacto
>   etiquetado «referencia, NO decide».
> * **En la letra no.** §A2 nombra «McNemar pareado» como el estadístico, y
>   ése es el nombre de la cosa que §61 degradó; y la regla de decisión del
>   plan sigue siendo un **cruce de umbral**, que es la forma contra la que
>   §61 escribió «cruzar α no es tener evidencia». Un lector de 2028 que
>   llegue por §A2 y no por §A3.2 va a leer lo que §61 prohibió.
>
> Corregido en su sitio: la letra de §A2 queda como está —es el estadístico
> que el plan congela— con esta nota al lado, y el `estadistico-adversario`
> dictamina si la tensión exige algo más que una nota. No se cambia la
> regla de decisión en esta corrida: cambiarla sería rehacer las fronteras,
> la potencia y el calendario, y eso no es una corrección sino un diseño
> nuevo.

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

### A3.1 El efecto mínimo de interés (MDE), derivado de V6

El MDE no se inventa: se deriva del único criterio económico que el
proyecto ya tiene congelado. **V6**, textual (`GEMELO/DISEÑO.md`:460-461):

> **V6 — Benchmark obligatorio.** Superar comprar SMH y no hacer nada,
> después de costos de 25 pb por lado, con barrido de sensibilidad.

Antes de la derivación, dos cosas que hubo que arreglar en los insumos.

#### A3.1.a El insumo estaba contaminado

El parámetro que mandaba **en la escala del retorno de sesión** era
**E|r|**, el retorno absoluto medio de la sesión objetivo. **Para el
endpoint congelado manda E|gap|** (§A3.1.c), y las cifras vigentes de los
dos están en la tabla de abajo. Lo que sigue se conserva porque el
HALLAZGO —la contaminación del insumo— es el mismo en las dos escalas:
medido sobre la ventana sin anclar y con `keep="first"`, E|r| daba
**4.02%**, y ese número estaba **inflado** por una razón que es un hallazgo
por derecho propio:

> **30 filas —el 11.0% de las 272 de la ventana antecedente anclada CON
> `excluir_cero` y SIN la regla de filas; con la regla son 262— son
> predicciones distintas que apuntan a
> la MISMA sesión objetivo.** Quince pares, sobre **cuatro** sesiones
> (31-jul, 5-ago, 12-ago, 18-ago): dos fechas de emisión consecutivas
> cuyo objetivo es la misma sesión, porque la sesión intermedia no
> existió. Comparten `gap_pct` y `retorno_real_pct` idénticos, y **entre
> ellas están los movimientos más grandes de toda la ventana**
> (000660.KS +29.95%, 005930.KS +26.81%, 3436.T +17.52%). Contadas dos
> veces, inflan cualquier media.
>
> **ERRATA (1-sep-2026).** Esta línea decía "cinco sesiones" y son
> **cuatro** — las cuatro que la propia línea enumera. Error de conteo
> mío, sin consecuencia sobre ninguna cifra (los 15 pares y las 30 filas
> son correctos), corregido acá y no en silencio porque el documento ya
> estaba commiteado (`d071821`). Lo encontró el forense del Frente A de la
> quinta corrida.
>
> **ERRATA de la errata (1-sep-2026, más tarde).** La primera redacción de
> esta nota **se insertó a mitad de la oración original y le partió el
> sentido**: el bloque quedaba diciendo "...de la quinta corrida. dos
> fechas de emisión consecutivas...". Lo cazó el `guardian-constitucion`.
> Reordenado: primero el texto original completo, después las notas. Una
> errata que rompe la frase que corrige es peor que el error que arregla.
>
> **Y el alcance creció después:** son **25** las filas con
> `sesion_objetivo` incorrecta, no 20 — las 10 de estos pares más **15
> huérfanas sin pareja**, que sólo se ven auditando las 279 filas selladas
> y no con un `GROUP BY ... HAVING COUNT>1`. Ver
> `GEMELO/resultados/parche_snapshot140.md`.

Bajo la regla de filas firmada, E|r| = **3.5556%**.

| Fuente | E\|r\| |
|---|---|
| ventana antecedente anclada, **sin** la regla de filas | 3.8666 % |
| ventana antecedente anclada, **con** la regla firmada | 3.5556 % |
| precio crudo de Yahoo, recomputado (una reproducción, no una vara) | 3.7724 % |

> **Las tres cifras se movieron el 25-oct-2026, y por dos razones que
> conviene separar.** (a) La ventana es otra: está **anclada** por los dos
> cortes de `ventana_antecedente.py`, y antes no estaba anclada por nada,
> así que crecía con el reloj. (b) La regla es otra: antes era un
> `drop_duplicates(keep="first")`, y ahora es la **regla firmada**
> (actas §60 y §61), que no arbitra por orden sino por correspondencia
> entre `sesion_objetivo` y `available_at` — y que conserva las DOS filas
> de un par de feriado, porque ahí no hay nada que arbitrar. Lo que **sí
> reproduce exacto** es el hallazgo: 30 filas, 15 pares, cuatro sesiones.
> Lo que no reproducía era el denominador y la regla.

> **RETRACTACIÓN (31-ago-2026, mismo día).** La primera redacción de este
> apartado llamaba a la tercera fila «vara independiente» y decía que
> «confirma la deduplicada y descarta la contaminada». **Las dos cosas son
> falsas y las retiro.**
>
> El cuarto dictamen lo midió: emparejada fila a fila contra la columna
> sellada, la desviación máxima es **0.0207 pp** y la media **0.0001 pp**
> sobre 234 filas. Es el **mismo proveedor, el mismo campo y la misma
> fórmula recorrida de nuevo**: una reproducción, no una medición
> independiente. Hereda cualquier error de proveedor, de ajuste o de
> `ffill`; sólo podría cazar un error de agregación.
>
> Y la razón de que dé 3.7594 en vez de 4.0231 **no es que descarte la
> contaminación**: es que promedia **otra población** (319 pares
> ticker-sesión de todo el calendario contra 246 en 37 sesiones objetivo).
> Restringida a las mismas filas da 3.7151% contra 3.6671% sellado —
> coincide porque *es* el número sellado.
>
> Esto es exactamente lo que la regla nueva de la casa prohíbe: **fabricar
> una vara que se le parezca a una independiente**. La regla dice que si
> no existe, se dice. Acá **no existe**: no hay en el repo una fuente de
> precios de otra familia con la que contrastar `retorno_real_pct`, y
> conseguirla es trabajo, no un `yf.download`.

**Lo que queda en pie de este apartado**, y no es poco: los 30 duplicados
son reales, están identificados uno por uno, e inflan E|r| de **3.5556 a
3.8666** sobre la ventana anclada con la regla firmada (3.72 a 4.02 en la
medición sin anclar de la v5, superada).
Eso se ve **dentro de la propia base sellada** y no necesitaba vara
externa. Lo que no queda en pie es la validación externa que decía tener.
Sale de `GEMELO/SECUENCIAL/mde_desde_v6.py`.

> Los 30 duplicados son la misma familia de problema que la pregunta
> pendiente de `DECISIONES.md` §33.8 sobre las 8 filas del 29-jul, pero
> **más grande de lo que esa pregunta suponía**: son 30 filas y **cuatro**
> sesiones, no 8 y una. Entra a `cola_decisiones.md` con ese alcance.
>
> **ERRATA (25-oct-2026).** Esta línea decía «cinco sesiones». Es la misma
> cifra que la ERRATA del 1-sep corrigió doce líneas más arriba, y **la
> corrección no alcanzó a esta copia**: el documento quedó diciendo cuatro
> en un párrafo y cinco en el siguiente durante casi dos meses. Es el
> defecto que el propio documento se reprocha —una tabla que vive en dos
> lugares se desactualiza en uno—, aplicado a una palabra. Corregido acá.
>
> **Y la pregunta de §33.8 ya no está pendiente**, que es el otro motivo
> para tocar este párrafo: las actas §60 y §61 del 1-sep-2026 la cerraron.
> La regla de filas firmada retira las filas del defecto de `snapshot.py`
> —entre ellas las del 29-jul— por correspondencia entre `sesion_objetivo`
> y `available_at`. Lo que sigue en cola no es esto: es la rama «+
> coherencia» de `cola_decisiones.md` §2a-ter, que retiraría además las
> filas SIN pareja que tampoco corresponden, y cuyo cableado al árbitro es
> la tarjeta §46 de `espera_firma.md`, abierta.

#### A3.1.b V6 no puede fijar el MDE — y con intervalos NINGUNA de las dos razones se sostiene

> **Rehecho el 25-oct-2026: es la condición 2 del cuarto dictamen.** El
> dictamen pidió intervalos para esta sección. Puestos, la razón 2 ya
> estaba retractada y **la razón 1 también se cae**. La conclusión de la
> sección —que V6 no puede fijar el MDE— **sigue en pie**, pero ya no la
> sostiene una medición: la sostiene un argumento estructural, que es más
> débil y más honesto. Las dos cosas se dicen abajo.

**Razón 1 — el benchmark de V6 lo domina su propio camino realizado.**
Sobre la misma ventana que la v5 usaba (3-jul a 28-ago), hoy el script mide
**SMH −8.47% en 40 sesiones**. Con un benchmark negativo, la tasa de
acierto necesaria para superarlo neto de 25 pb es **54.1%, IC95
[53.2, 55.2]**, y la tasa que la baseline de comprar y mantener consigue sobre
la ventana antecedente anclada es **54.2%, Wilson [48.1, 60.1]** — un
intervalo que **contiene el 50%**, o sea que en esta ventana la baseline
**no se distingue de una moneda**.

**Los dos intervalos se superponen**, así que la razón 1 se sostiene como
punto estimado y **no** como afirmación con intervalo.

> **Y «los dos puntos están a 0.1 pp uno de otro» queda RETIRADO** por la
> exigencia E9: la razón 1 **no tiene resolución para una brecha de ese
> tamaño**, y el dictamen midió tres defectos que la superan, cada uno:
>
> * **off-by-one**: `retorno_benchmark` divide por `len(v)` = 40 **cierres**
>   cuando 40 cierres son **39 retornos**. Mueve 0.08 pp — el tamaño mismo
>   de la brecha.
> * **modelo de costo incoherente**: la razón 1 cobra `2c` **cada sesión**,
>   mientras §A3.1.c —la subsección siguiente, la misma estrategia— cobra
>   `f·2c`. Mueve **3.57 pp**, o sea 36 veces la brecha.
> * **mezcla de escalas**: retorno compuesto contra media aritmética.
>
> **La conclusión sobrevive las cuatro variantes** —eso también lo midió el
> dictamen, y por eso la sección no se cae—, pero la frase de la brecha no
> describe nada. Lo que decide sigue siendo que los intervalos se superponen
> y que el de la baseline contiene el 50 %.

**Y lo del 50% no es una nota al pie: desarma la razón 1 todavía más**, y
lo cazó el escáner de §A3.1.b y no el autor. El argumento de la v5
descansaba en que la baseline tenía un margen cómodo sobre la tasa que el
benchmark exige; con el denominador correcto no hay margen, y el extremo
contra el que se compara no está establecido ni siquiera respecto de una
moneda. La v5 la presentaba como una brecha de casi cinco puntos
(«54.9% por debajo del 59.7%») y concluía «la baseline sola aprueba V6»:
eso ya no se puede decir así. Lo que se puede decir es que **no se
distingue si la baseline sola aprueba V6 o no**.

Dos correcciones de método que vienen con esto, y la segunda es la que
importa de verdad:

1. **La brecha de la v5 comparaba dos ventanas distintas — y la de hoy
   también, aunque menos.** El 59.7% salía de la rama de filas que la
   decisión D1 derogó el 3-sep (acta §78); el 54.2% de ahora sale de la
   ventana antecedente anclada con la regla firmada. Buena parte de los
   «casi cinco puntos» era el cambio de denominador, no el mercado.

   **Pero la comparación de hoy sigue mezclando ventanas, y hay que
   decirlo** (lo cazó el `curador-epistemico`): la tasa **necesaria**
   combina el retorno de SMH sobre el 3-jul–28-ago con E|r| sobre la ventana
   antecedente (emisión hasta el 31-ago), mientras la tasa **conseguida** es
   sólo de la ventana antecedente. Las dos poblaciones no coinciden. Y el
   IC95 [53.2, 55.2] de la tasa necesaria **propaga sólo E|r|** por los
   mismos clústeres de día, tratando el retorno de SMH como fijo — que es
   coherente con que sea un camino realizado, pero hay que declararlo.

   Por lo tanto **«los dos puntos están a 0.1 pp uno de otro» es una
   observación ilustrativa y NO la medición de una brecha.** Lo que decide
   no es la cercanía de los puntos: es que los intervalos se superponen y
   que el de la baseline contiene el 50%. Es el mismo defecto que el Frente
   D le encontró al MDE (`mde_vs_observado.md` D1b) — un lado sobre una
   población y el otro sobre otra—, sobreviviendo un nivel más arriba.
2. **El insumo de esta razón NO ESTÁ ANCLADO, y el 5.18% de la v5 queda
   explicado.** El retorno de SMH sale de una descarga de Yahoo en el
   momento de correr el script. Hoy da −8.47% en 40 barras donde la v5
   escribió −5.18% en 39, y la causa **está identificada, no supuesta**:

   - **40 es el número correcto de sesiones de XNYS entre el 3-jul y el
     28-ago de 2026**, verificado contra el calendario del propio proyecto
     y no contra una cuenta a mano (`exchange_calendars`: 40 sesiones, la
     primera el 6-jul y la última el 28-ago; el viernes 3-jul **no es
     sesión**, porque el 4 cae sábado y el feriado se observa el viernes
     anterior).
   - **Con 39 barras —las mismas 40 menos la última— el retorno da
     −5.1795%**, que es exactamente el −5.18% que la v5 publicó. Y la
     sesión que falta, la del 28-ago, movió **−3.47%**.

   O sea que **la fuente NO revisó nada**: la v5 midió cuando la última
   barra de su propia ventana todavía no había llegado, y publicó como
   «SMH en la ventana» un retorno que le faltaba el último día de la
   ventana. Eso es peor que una cifra que se mueve: es una cifra que
   describe una ventana distinta de la que su propio texto declara.

   La consecuencia es estructural y no se arregla con un intervalo: **una
   razón cuyo insumo se descarga en vivo no se puede pre-registrar**, y
   este caso muestra el modo de falla exacto — no hace falta que el
   proveedor corrija nada, basta con correr el script antes de que cierre
   el último día. Si esta razón va a seguir sosteniendo algo, la serie de
   SMH tiene que quedar sellada con su `available_at`, como el proyecto
   hace con todo lo demás; si no, la razón se cita como ilustración y no
   como fundamento. Va a la tarjeta §94.

**Lo que SÍ queda en pie, y alcanza para la conclusión de la sección.** El
argumento estructural, que no necesita ninguna de las dos mediciones:
**V6 compara contra el camino REALIZADO de un benchmark, así que la vara
que impone depende de si SMH subió o bajó en la ventana.** Un umbral de
relevancia que cambia de valor según cómo le fue al benchmark no es un
efecto mínimo de interés: es una propiedad de la ventana. Eso vale con
intervalo o sin él, y es lo único de esta sección que se usa para decidir.

**Razón 2 — RETRACTADA el mismo día. No se sostiene.**

> La primera redacción decía: «el puente de la economía a los puntos de
> acierto está roto, y por un factor de 3.6», apoyándose en que los
> aciertos de las filas "baja" tienen |r| = 5.162% contra 3.870% de los
> errores (razón 1.33×), y en que `E[r|baja]` real (−1.059%) es 3.64×
> —cifra RETIRADA, `cifras_retiradas.md`, acta §56—
> más negativo que el −0.291% que predice la fórmula simétrica.
>
> **Le puse los intervalos que no le había puesto, y se cae:**
>
> | cifra | IC 95% | |
> |---|---|---|
> | razón de magnitudes 1.33× | **[0.89, 2.16]** | **incluye 1.0: la simetría NO está refutada** |
> | `E[r\|baja]` = −1.059% | **[−3.334, +1.059]** | incluye cero, y cubre −2c |
> | q = 53.9% | Wilson [45.3, 62.3] | incluye 50% |
>
> (bootstrap de bloques del módulo árbitro, bloque 20, 10.000 réplicas,
> semilla 7)
>
> **El "3.64×" —RETIRADA— ni siquiera tiene intervalo finito**, porque su
> denominador es `(2q−1)` y `q` no se distingue de 0.5.
>
> Publiqué un estimador puntual indistinguible del nulo y lo presenté como
> hallazgo — **la regla 1 del proyecto, rota en la sección escrita para
> prevenir exactamente eso**, y usada para rechazar un modelo. El
> documento imprimía la Wilson honesta de `q` una línea antes y dividía
> por `(2q−1)` a la línea siguiente.

**Lo que sí se puede decir, con la misma evidencia y sin sobrepasarla:**
la ventaja económica de este modelo **podría** venir de la magnitud más
que del signo —es la lectura compatible con lo que el proyecto ya publica
(MAE 2.98 vs 3.33, con la dirección sin distinguirse de cero)— pero **la
ventana sellada no alcanza para establecerlo**. Es una hipótesis, no un
hallazgo, y no puede sostener sola la conclusión de esta sección.

**Consecuencia para el MDE:** **la razón 1 NO se sostiene con intervalo**
(ver arriba: los intervalos se superponen, y encima comparan ventanas
distintas). Lo que alcanza para decir que V6 no fija el MDE en esta ventana
es el **argumento estructural** —V6 compara contra un camino realizado, así
que la vara depende de si el benchmark subió o bajó—, que no necesita
medición y que queda declarado como más débil que una cifra. La razón 2 se
retira. Y el rango [2, 7] pp que este
documento presentaba como "el supuesto que manda" **descansaba en la razón
2**, así que también se retira: sin ella, el MDE bajo magnitudes
simétricas es un número, no un rango con un extremo preferible.

#### A3.1.c La derivación que sí funciona, y su rango

Lo que sí se puede derivar sin depender del camino de SMH: **la ventaja
direccional mínima que paga sus propios costos de transacción.**

"Siempre al alza" como *estrategia* es comprar y mantener: no opera. El
modelo sólo difiere de ella en las filas donde dice BAJA — ahí sale (o se
pone corto) y paga `2c` por salir y volver. Con `f` = fracción de
predicciones a la baja y `q` = P(gap<0 | baja):

```
ventaja en puntos de acierto:  δ = (2q − 1) · f
condición económica:           E[gap | baja] < −2c
bajo magnitudes simétricas:    δ_min = f · 2c / E|gap|
```

> **LA ESCALA, corregida el 31-ago y recién ahora aplicada en toda la
> sección.** El endpoint congelado de §A2 es `acierto_gap`, así que la
> magnitud que paga el acierto es **E|gap|**, no E|r|. La v5 corrigió esto
> en su cabecera pero dejó el cuerpo de §A3.1.c en la escala del retorno de
> sesión, que es una de las contradicciones internas que la corrida 17
> tenía que cerrar. Las cifras de abajo están todas en la escala del
> endpoint y salen de `mde_desde_v6.py` sobre la ventana antecedente
> anclada.

Con `f = 0.4924` [0.3190, 0.6565] y `E|gap| = 2.8921%` [2.2250, 3.8368]:

| Costo por lado | MDE en la escala del endpoint | IC95 (clústeres de día) |
|---|---|---|
| 10 pb | 3.40 pp | [1.98, 5.24] |
| **25 pb (el caso base de V6)** | **8.51 pp** | **[4.94, 13.09]** |
| 50 pb | 17.02 pp | [9.89, 26.18] |

Bootstrap de **clústeres de día**: 10.000 réplicas, semilla **20260901**,
37 clústeres. Los tres parámetros están acá y en `mde_desde_v6.py`, y valen
lo mismo en los dos lugares. **Propagando sólo E|gap|** —lo que la v5
publicaba como el intervalo del MDE— el de 25 pb sale **[6.42, 11.06]**: se
imprime para que la diferencia entre un insumo y dos se vea, no para
citarse.

> **A qué supuesto es más sensible, con la jerarquía corregida.** La v5
> decía que el supuesto que manda es la **simetría de magnitudes**, y lo
> cuantificaba con una cifra que está **RETIRADA** (`cifras_retiradas.md`,
> acta §56): con intervalos, la razón de magnitudes incluye 1.0 y el
> cociente que la resumía no tiene intervalo finito, porque su denominador
> `(2q−1)` no se distingue de cero. Así que la jerarquía de la v5 no se
> puede sostener con el número que la sostenía.
>
> Lo que sí se mide: propagando `f` y E|gap| juntos, el MDE va de 4.94 a
> 13.09 pp — un factor de 2.6 dentro del intervalo, antes de tocar la
> simetría. **La simetría queda declarada FUERA del intervalo**, que es una
> de las tres salidas que el Frente D admitía
> (`GEMELO/resultados/mde_vs_observado.md` D3, condición 3), con su
> sensibilidad medida ahí: en la escala del endpoint la asimetría apunta al
> lado contrario que en la escala del retorno, y su intervalo incluye 1.0 en
> las dos. **Un efecto que cambia de signo con el instrumento no está
> establecido en ninguna dirección**, y por eso entra como supuesto y no
> como estimación. No se recomputa en esta corrida: estimarla condiciona en
> el acierto del modelo, y la corrida no recomputa ninguna cifra que
> dependa del acierto, tampoco en la ventana antecedente.

#### A3.1.d El número para firma: SIN FIRMAR, y el plazo ya corre

> **No hay un número propuesto. Hay un intervalo, y una fecha de
> vencimiento.**
>
> **MDE a 25 pb = 8.51 pp, IC95 [4.94, 13.09]**, en la escala del
> endpoint, sobre la ventana antecedente anclada, propagando `f` y E|gap|.
> La elección es de Nicolás: **tarjeta §90**.

**El valor que esta sección proponía está RETIRADO.** La v5 proponía un MDE
de 7 pp como «extremo conservador del rango [2, 7]»; esa cifra está en
`GEMELO/cifras_retiradas.md` desde el 31-ago-2026 (acta §56) porque **se
derivó en la escala del retorno de sesión** cuando el endpoint congelado es
`acierto_gap`. Y el rango [2, 7] que la justificaba **descansaba en la
razón 2**, retractada el mismo día. Las dos cosas se retiran juntas: el
número y el argumento que lo elegía.

**Lo que cuesta en calendario, al ritmo MEDIDO de la población** (7.579
filas por día hábil, por conteo; la v5 proyectaba 6.56 desde la ventana
antecedente, que era el único ritmo disponible cuando la población no
existía). Tabla completa, con el n de cada mirada, en §A3.5; acá el
resumen que la firma necesita:

**PRIMERO, el intervalo honesto de `N_max`** (exigencia E2 del quinto
dictamen). `p_d` **es** `f` (§A2), así que `N_max` y el MDE están acoplados
por la MISMA estimación y hay que propagarlos **dentro de cada réplica**
(`tabla_firma.propagacion_conjunta`, 10.000 réplicas de clústeres de día,
semilla 20260901):

| | mediana | IC95 |
|---|---|---|
| **`N_max`** | **1.920** | **[1.025, 4.153]** |
| mirada 1 (25 %) | 480 → **2026-11-27** | [256, 1.038] |
| mirada 2 (50 %) | 960 → 2027-02-24 | [513, 2.077] |
| mirada 3 (75 %) | 1.440 → 2027-05-24 | [769, 3.115] |
| **mirada 4 (final)** | **1.920 → 2027-08-20** | [1.025, 4.153] |

**P(la mirada 1 ya está vencida, si se firma la regla del punto derivado) =
0.0614, Wilson 95 % [0.0569, 0.0663].** Ésa es la cantidad bien definida, y
**reemplaza** al «el MDE crítico cae dentro del IC95», que ordenaba dos
cosas que el remuestreo no pone en la misma escala. **El nombre lleva su
condicional a propósito:** si la mirada 1 está vencida o no es, en rigor,
una función determinista del MDE **firmado**, y no hay MDE firmado; lo que
esta proporción mide es la fracción de remuestreos de los días de la ventana
antecedente en que el MDE derivado la dejaría debida.

**SEGUNDO, el abanico CONDICIONAL**, que responde otra pregunta: «si firmo
ESTE número, ¿cuándo mira el plan?». **No es un intervalo, y la primera
redacción de esta v6 lo presentaba como si lo fuera** — ése es el defecto
D2 del quinto dictamen, y los dos extremos de abajo caen **fuera** del
intervalo honesto de arriba:

| MDE | qué es (CONDICIONAL) | `N_max` | primera mirada | análisis final |
|---|---|---|---|---|
| 4.94 pp | si se firma el borde inferior del IC del MDE | 5.836 | 2027-05-27 | 2029-08-14 |
| **8.51 pp** | **si se firma el punto** | **1.962** | **2026-11-30** | **2027-08-27** |
| 11.09 pp | si se firma el MDE crítico (punto; [8.93, 12.81]) | 1.152 | **ya vencida** ⛔ | 2027-03-31 |
| 13.09 pp | si se firma el borde superior del IC del MDE | 825 | **ya vencida** ⛔ | 2027-01-29 |
| 10.00 pp | si se firma el valor de calendario | 1.419 | **2026-11-04** | 2027-05-20 |

> **Las dos filas de los bordes son condicionales y no bordes de nada**:
> combinan el MDE de una réplica con `p_d` del punto. Si lo que se quiere es
> «cuán largo puede salir el plan», el número es el IC de arriba
> ([1.025, 4.153] filas, o sea el análisis final entre **2027-03-08** y
> **2028-10-04**), **no** el 5.836 ni el **2029-08-14**, que quedan
> **RETIRADOS como intervalo** y se conservan sólo como respuesta
> condicional a «si se firma 4.94 pp».

**Y el hallazgo que hay que decir con todas las letras, porque no es el que
la v5 tenía:**

1. **El MDE crítico es 11.09 pp como PUNTO, IC95 [8.93, 12.81], y cae
   DENTRO del intervalo derivado.** Por encima de ese valor, el n de la
   primera mirada (0.25 · N_max) ya es menor que las filas que la población
   acumuló, así que **el plan arrancaría con una mirada debida**. §A3.8 dice
   que una mirada saltada no se recupera y que una «omitida» que en realidad
   se hizo es fraude: eso convierte esto en una condición que la firma tiene
   que conocer ANTES, no un detalle de calendario.

   **Y el crítico lleva intervalo por la misma razón que el MDE**, que es un
   punto que esta sección publicó mal en su primera redacción de hoy y que
   cazó el `curador-epistemico`: `N_max` depende de `p_d`, y **`p_d` ES
   `f`** —identidad estructural, ver §A2—, así que el crítico hereda el
   intervalo de `f`. Un umbral sin intervalo, en el documento cuya lección
   es que no se publica un punto sin intervalo, era el error en el sitio
   escrito para prevenirlo.

   Lo que el intervalo obliga a decir: **cuál de las opciones arranca
   vencida está indeterminado entre 8.93 y 12.81 pp.** Lo que SÍ está
   medido: **por encima de 12.81 pp la mirada 1 está vencida para todo el
   intervalo de `f`**, y el borde superior del IC del MDE (13.09 pp) está
   por encima de él. Dos efectos más lo mueven unas décimas en direcciones
   opuestas y quedan declarados: el conteo es un techo que no aplica
   `excluir_cero` (con 283 filas el crítico sube a ~11.19 pp) y cierra en la
   última fecha de emisión y no hoy (con una jornada hábil más, 296 filas,
   baja a ~10.94 pp).
2. **Con el punto estimado quedan cinco semanas**, y con el valor de
   calendario **diez días**. La v5 hablaba de 2028; el plazo real de la
   firma es noviembre de 2026.
3. **La tensión que la v5 declaró sigue existiendo pero cambió de signo.**
   Ya no es «el MDE derivado empuja la respuesta a 2028 y eso es demasiado
   lejos»: con el ritmo real, el punto derivado da el análisis final en
   **agosto de 2027**, y su intervalo honesto lo pone entre **marzo de 2027
   y octubre de 2028**. La tensión es entre el punto y su propio intervalo,
   no entre el MDE y el calendario.

   > **Esta línea decía, hasta el re-dictamen: «lo que empuja lejos es el
   > borde inferior del intervalo, que lleva el final a 2029».** Era la
   > frase retirada por E2 reinstalada a cuarenta líneas de su propia
   > retractación — exactamente la errata «cinco sesiones / cuatro
   > sesiones» que §A3.1.a narra, cometida de nuevo en la misma ronda que la
   > narra. El 2029 sale del emparejamiento incoherente y no es borde de
   > nada; el borde honesto es **2028-10-04**.
4. **§A3.1.d sigue exigiendo lo mismo, y ahora con un caso concreto:** si
   se firma un valor que no sale de la derivación —el 10 pp de calendario es
   el caso— **se declara como elección de calendario y no como derivación
   de V6**. Lo que no se puede es firmar un valor de calendario diciendo que
   sale de V6. El 10 pp, además, ya no está «por encima del MDE que V6
   exige»: está **por debajo del punto derivado**, así que el argumento
   accidental que lo defendía en la v5 tampoco vale.

**La elección es de Nicolás.** Este documento aporta la derivación, su
intervalo, el supuesto que queda fuera del intervalo, el costo en
calendario de cada opción y el valor a partir del cual el plan arranca
vencido.

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
>    datos de esa mirada**, remuestreando **la CLAVE DEL CLÚSTER — que es
>    un parámetro SIN FIRMAR, no una constante de este punto** (ver abajo)
>    — con `backtest.inferencia._remuestrear_circular` (el remuestreador
>    circular del proyecto), en **tres longitudes de bloque congeladas:
>    `BLOQUES_FECHAS = (1, 5, 10)`**, con `N_DRAWS = 200_000` y
>    `SEMILLA_BOOTSTRAP = 20260831`. Los tres parámetros están acá y en
>    `mirada.py`, y valen lo mismo en los dos lugares.
>
>    > **LA CLAVE DEL CLÚSTER NO ESTÁ CONGELADA**, y esto es lo que levanta
>    > el defecto D1 del quinto dictamen (exigencia F11). Hasta el
>    > re-dictamen este punto decía «remuestreando FECHAS DE EMISIÓN» en
>    > mayúsculas, dentro del bloque que declara «lo que se pre-registra es
>    > la fórmula» — y la opción que la tarjeta §91 **recomienda** cambia la
>    > clave a la **sesión objetivo**. Firmarla dejaba falso un párrafo que
>    > el acta propone congelar, y **manda la norma, no la cabecera**.
>    >
>    > La clave es `mirada.REGLA_DEDUP_ESTIMADOR`, en `None`, con candado y
>    > test. Las dos ramas posibles son `fecha` (de emisión) y
>    > `sesion_objetivo`. **Lo que se propone congelar acá es todo lo
>    > demás**: la forma del estadístico, los tres bloques, las réplicas, la
>    > semilla y la regla del máximo. Ninguna frontera, ni el α, ni la
>    > futilidad, ni el calendario dependen de la clave.
>    >
>    > **Y lo que sí depende, declarado:** la tabla de exposición residual
>    > de más abajo **se computó sólo para la clave por fecha de emisión**.
>    > Si se firma la otra, esa tabla —y con ella la banda [0.046, 0.079]—
>    > deja de describir al estimador y hay que recomputarla antes de
>    > congelar (tarjeta §97). El DEFF de planificación 3.6, medido sobre
>    > clústeres de fecha de emisión, pierde igualmente su interpretación.
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
   mirada —y **~25 informativas**, ver la declaración de la degeneración más
   abajo— eso **no se arregla con un estimador mejor**: es el límite del
   n, y es un límite más estrecho que el que esta línea suponía. Es la razón por la que este documento **no está congelado** — ver el
   bloque de la era v3 y la sección «El α, decidido» al principio. (Esta
   línea remitía a una sección llamada «La decisión que bloquea el
   congelamiento», que no existe: la decisión del α se tomó el 31-ago y lo
   que bloquea hoy son las cuatro firmas.)

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
ninguna ventaja): **ac1 = −0.176 ± 0.164 sobre 37 fechas**, sobre la
ventana anclada y con la regla de filas firmada.

> **La historia de esta cifra es el mejor ejemplo de la condición 4, y hay
> que contarla entera.** La v5 citaba «−0.135 ± 0.171 sobre 34 fechas» en
> un lugar y «−0.134 ± 0.169 sobre 35 fechas» en otro: ésa es la
> contradicción «34 contra 35» que el cuarto dictamen señaló, y la causa no
> era un error de transcripción. `ac1_ventana_antecedente()` llamaba a
> `cargar()` **sin ancla**, así que medía «la ventana sellada de hoy» — y
> «hoy» se movía. Con 34 fechas daba un número y con 35 otro, los dos
> correctos el día en que se midieron y ninguno reproducible después.
>
> **Para el 25-oct-2026 ese defecto había dejado de ser un número que se
> mueve: era una mirada.** `ac1` es una función del acierto, y la base viva
> hoy incluye las filas de la población. Correr esa función habría
> computado `ac1` sobre las filas que el estadístico todavía no miró, **sin
> dejar línea en `miradas/registro.log`** —porque ese registro sólo lo
> escribe `mirada.py`—, que es exactamente la mirada furtiva a la que §A3.8
> le pone precio. Esta corrida la encontró antes de correrla y la ancló por
> los dos cortes de `ventana_antecedente.py`. El número de arriba es el
> primero que sale de una ventana cerrada, y no se mueve más.

El signo es
negativo, que es la dirección benigna. **Y la frase que esta línea traía era
falsa, por exigencia E3:** decía que «los datos de hoy no distinguen 0 de
+0.2», y con el propio error estándar del documento el límite superior al
95 % es **+0.145**, o sea que **+0.2 SÍ queda excluido**. Lo que los datos
no distinguen es 0 de +0.145. El «±0.164» es **un error estándar**, o sea
cobertura ≈68 %, no un intervalo del 95 %: el dictamen midió además que el
EE verdadero bajo el patrón de ceros real es **0.142**, así que Bartlett es
conservador por un factor 1.16. Así que el argumento "está
medido y da negativo" no alcanza y no se usa.

> **LA DEGENERACIÓN, declarada por exigencia E3 del quinto dictamen, y el
> proyecto ya la había medido.** `f` por fecha de emisión es
> **perfectamente degenerado** en la ventana antecedente: 19 fechas con
> `f = 0` y 18 con `f = 1`, ninguna intermedia — el modelo sigue el signo
> del SOX de la noche, así que o todos los tickers de una fecha dicen BAJA
> o ninguno. Consecuencia: **20 de las 37 fechas aportan `d_j` = 0
> EXACTO**, y sólo 17 informan a `b − c`.
>
> Eso **tumba el «~51 fechas»** con el que esta sección y §A3.4 argumentan
> la confiabilidad de `V̂` en la primera mirada: son del orden de **25
> fechas informativas**, no 51. Y `GEMELO/resultados/secuencial_v5.md`
> (2-sep-2026) ya lo decía textualmente —«54 % de las 35 fechas contribuyen
> exactamente cero», «el eje es inerte»— en una línea que **ninguna versión
> de este documento citó**. Se cita acá.
>
> **Lo que eso le hace al aparato de §A3.2, dicho sin ablandar:** el eje de
> autocorrelación al que está indexada toda esta sección —y la banda
> [0.046, 0.079]— lo midió el simulador calibrado como **inerte** bajo el
> proceso que describe estos datos. Y en el único dato real `V̂` sale
> {bloque 1: **3.618**, bloque 5: 2.517, bloque 10: 2.652}: **el máximo lo
> alcanza el bloque 1**, así que la regla del máximo paga 4.6 pp de potencia
> por un seguro que en esta ventana no cubre nada. Reconciliar la banda con
> ese hallazgo es parte de **E3** y **no está hecho**: es una corrida de
> simulación propia, y está en la tarjeta §97.

Un rasgo estructural que amortigua, y que no se diseñó a propósito: **la
mirada donde `V̂` es menos confiable (la 1, con ~51 fechas y **~25
informativas**) es la que
tiene el umbral más alto (4.048).** El conservadurismo temprano de
O'Brien-Fleming y la debilidad del bootstrap están anti-correlacionados, y
eso es parte de por qué la exposición de la tabla no es peor. Se dice como
observación cualitativa, verificable en la propia tabla de umbrales de
§A3.4; **no se le pone cifra** porque descomponer el α global por mirada
es un cómputo que no está en este repo.

**Qué obliga esto en cada acta:** reportar `ac1` con su EE. Si sale
distinguible de cero, `mirada.py` lo dice en el acta y el veredicto no se
lee sin ese dato al lado.

#### El estimador de reestimación, declarado ahora y no cuando haga falta

α = 0.05 se congela **con la banda [0.046, 0.079] declarada**, y con el
compromiso de reestimarla cuando el N permita acotar la autocorrelación.
Ese compromiso no vale nada si el estimador se elige el día que se cumple,
así que se declara acá:

> **Estimador.** `ac1` = autocorrelación de lag 1 de las contribuciones
> por fecha `d_j`, calculada como
> `Σ(d_j − d̄)(d_{j+1} − d̄) / Σ(d_j − d̄)²` sobre las fechas acumuladas,
> ordenadas por sesión objetivo. Implementado en
> `mirada.autocorrelacion_lag1`, ya escrito y con test.
>
> **Error estándar.** `1/√m` con `m` = número de fechas. Es la
> aproximación de Bartlett bajo la nula de independencia, que es la nula
> que importa acá.
>
> **Cuándo se reestima la banda.** Cuando `2·EE < 0.10`, es decir cuando
> `m ≥ 400` fechas — el punto en que el intervalo de `ac1` deja de cubrir
> a la vez 0 y +0.20, que es la ambigüedad que hoy obliga a publicar la
> banda entera. Con 37 fechas en la ventana antecedente, eso **no ocurre
> dentro de este diseño**: 400 fechas son unos 8 años. Se dice para que
> nadie lea "se reestimará" como si fuera pronto.
>
> **Qué se hace mientras tanto:** cada acta publica `ac1` con su EE y la
> banda se cita entera. La banda **no se estrecha** por una `ac1` puntual
> que dé chica: un estimador con EE de 0.164 que devuelve −0.176 no
> autoriza a elegir el extremo bueno de la banda.

**Y por qué α queda en 0.05 y no en 0.10** (decisión de Nicolás, 31-ago):
el proyecto publica su incertidumbre en todo lo demás —Wilson en cada tasa
de acierto, intervalo del 80% en cada predicción, "pendiente" cuando no
alcanza el n—. Subir el α declarado a 0.10 para que la cifra sea
"verdadera" sería **absorber la incertidumbre dentro de un número más
redondo**, que es exactamente lo contrario. Se declara 0.05 nominal, se
publica la banda al lado, y el lector ve las dos cosas.

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

Dos cosas más quedan PROPUESTAS PARA CONGELAR acá, porque son elecciones y
no consecuencias:

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
pareado, `p_d` fija en la observada:

- n bajo independencia: **384 filas**.
- n corregido por agrupamiento (×DEFF 3.6): **1.383 filas** — pero ese es
  el n de un test de **muestra fija**.

> **Los dos n se movieron el 25-oct-2026** y no porque cambiara la
> fórmula: el `p_d` que los produce se computaba sobre la rama de filas que
> la decisión D1 derogó el 3-sep (acta §78). Con el `p_d` de la ventana
> antecedente anclada y la regla firmada, 403 pasa a 384 y 1.450 a 1.383.
> Los umbrales, la futilidad y el α **no se mueven**: no dependen de `p_d`.

**Un plan secuencial con ese mismo n NO tiene potencia 0.80: tiene
0.7906.** La razón es directa y la v1 la pasó por alto: el umbral final
del plan es 2.024, no el 1.96 de muestra fija. Esa diferencia se paga en
N o se paga en potencia; no hay una tercera opción.

Se elige pagarla en N, con el **factor secuencial computado** por
`diseno_secuencial.factor_secuencial()`: (drift requerido por el plan /
drift de muestra fija)², con 2.802 de muestra fija. Su valor y el drift
requerido no se cablean en esta prosa: quedan sellados en
`GEMELO/resultados/tabla_firma_17.json` (`factor_secuencial` y
`potencia.drift_requerido`). Ese factor **no depende del MDE**:

| MDE | n iid (Connor) | ×DEFF 3.6 | **N_max** (× factor secuencial computado) |
|---|---|---|---|
| 4.94 pp (borde inferior del IC95) | 1.579 | 5.686 | **5.836** |
| **8.51 pp (el punto derivado, §A3.1)** | **531** | **1.912** | **1.962** |
| 10 pp (elección de calendario) | 384 | 1.383 | **1.419** |
| 11.09 pp (**el MDE crítico**) | 312 | 1.122 | **1.152** |
| 13.09 pp (borde superior del IC95) | 223 | 803 | **825** |

Con eso la potencia del plan es 0.80 exacta — **bajo el estadístico
idealizado, con la varianza conocida.**

> **La tabla se rehizo entera el 25-oct-2026, y es CONDICIONAL.** Las dos
> filas que traía se computaban con un `p_d` de la rama de filas derogada, y
> una de ellas con un MDE retirado. Ahora el abanico recorre el intervalo
> del MDE más el valor de calendario y sale de `tabla_firma.py`.
>
> **Pero NO es un intervalo de `N_max`**, y la primera redacción de esta
> nota decía «ahora el abanico es el intervalo del MDE completo», que
> invitaba a leerlo así (defecto F2 del re-dictamen). Cada fila combina el
> MDE de una réplica con `p_d` del punto, y **`p_d` ES `f`**: las filas de
> los bordes **no son bordes de nada**. El intervalo honesto de `N_max` es
> **[1.025, 4.153]** y está en §A3.1.d.

> **Lo único que el MDE mueve son N_max y las fechas.** Las fronteras de
> §A3.4, el estadístico de §A3.2, la regla de futilidad, el pasivo y toda
> la gobernanza **son independientes del MDE** y quedan fuera del alcance de
> su firma, pase lo que pase con él. Las fronteras de O'Brien-Fleming dependen sólo del
> número de miradas y del α, no del tamaño del efecto.

**Y esa última aclaración importa, porque la regla del máximo se come esta
corrección.** Tomar `max` sobre tres estimadores ruidosos está sesgado
hacia arriba: infla `V̂` ~12% aun cuando no hay nada que corregir, lo cual
es la dirección segura para el α y la dirección cara para la potencia.
Medido por `tabla_firma.potencia_del_plan`, con test: la potencia realizada
con `max(1,5,10)` es **0.7537**, contra 0.8000 idealizada. O sea: **la regla
del máximo cuesta 4.6 pp de potencia y la corrección de N_max reparaba 0.94
pp.** El arreglo del estimador se come **casi cinco veces** el arreglo del
tamaño de muestra. (La v5 escribía «~0.76» y «~1.7 pp», sin script: eran
optimistas, y se corrigen acá en su sitio porque este documento nunca se
publicó como congelado.)

Eso **no está resuelto en este documento**, y se dice en vez de
disimularse. Hay dos salidas y las dos son de Nicolás, porque las dos
mueven el calendario o el estándar:

1. **Recomputar N_max** contando el sesgo del máximo — más filas, más
   tarde.
2. **Declarar que la potencia del plan es ≈0.75 y no 0.80**, que es la
   salida barata y honesta: significa que si la ventaja real es de 10 pp,
   el diseño la detecta tres de cada cuatro veces en vez de cuatro de cada
   cinco.

Va junto con la decisión del α (ver el principio del documento): son la
misma familia de elección y conviene tomarlas de una vez.

> **Puesto en cifra el 25-oct-2026 (tarjeta §92).** El «~0.76» que esta
> sección declaraba ahora tiene su número y su script: propagando la
> inflación medida del 12% al drift requerido, la potencia del plan es
> **0.7537** contra **0.8000** idealizada (`tabla_firma.potencia_del_plan`,
> con test). O sea que la pérdida es de **4.6 pp de potencia**, no de 1.7:
> el «~0.76» de la v5 era optimista. Con la salida 2, lo que hay que
> declarar es que el diseño detecta su MDE **tres de cada cuatro veces**.
>
> **Y lo que cuesta la salida 1, también con su número:** recuperar 0.80
> exige subir el drift en √1.12, lo que multiplica `N_max` por 1.12 — unas
> **235 filas más** con el MDE del punto (1.962 → 2.197), que al ritmo
> medido son **31 días hábiles**: el análisis final pasaría de 2027-08-27 a
> octubre de 2027. Es la primera vez que las dos salidas tienen el mismo
> tipo de cifra al lado, que es lo que hacía falta para poder elegir.
>
> **El costo NO es parejo**, y por eso la tabla por MDE vive en la tarjeta
> §92 y no acá. Sobre el intervalo HONESTO de `N_max` ([1.025, 4.153]
> filas) recuperar 0.80 cuesta entre **16 y 66 días hábiles**. **El «13 a
> 92» que esta nota traía estaba construido sobre los extremos del
> emparejamiento retirado** —o sea sobre cifras que no son bordes de nada—,
> y erraba por un factor 1.4 en los dos extremos: lo cazó el re-dictamen
> (defecto N2), en la misma ronda que retiró el emparejamiento. Esta
> decisión **depende de la de §90** y no al revés.

### A3.4 Gasto de alfa: O'Brien-Fleming

Fronteras exactas por recursión numérica, validadas contra la literatura
(ver "De dónde salen los números"):

| Mirada | Información | Pocock: Z / α nominal | **O'Brien-Fleming: Z / α nominal** |
|---|---|---|---|
| 1 | 25% | 2.362 / 0.01819 | **4.048 / 0.00005** |
| 2 | 50% | 2.362 / 0.01819 | **2.862 / 0.00420** |
| 3 | 75% | 2.362 / 0.01819 | **2.337 / 0.01943** |
| 4 (final) | 100% | 2.362 / 0.01819 | **2.024 / 0.04297** |

**Estos umbrales no dependen del MDE y son los que el acta propone
congelar.** La columna de
n filas se movió a §A3.5, que es donde el MDE la determina.

α global exacto: Pocock 0.04996, OBF 0.04995. (La v1 iba a congelar
2.354/4.026/2.847/2.324/2.013, que dan **0.05122**.)

**Se elige O'Brien-Fleming.** Pocock detecta antes un efecto grande, pero
paga con un umbral final de 0.01819 — un efecto que llega justo al final,
que es el escenario más probable dado todo lo que se sabe, se perdería.
OBF casi no gasta alfa temprano (0.00005 en la primera mirada) y llega al
análisis final con 0.04297, casi el nominal completo. **Para una pregunta
que el proyecto lleva meses sin poder responder, conservar la potencia
del final importa más que la velocidad.**

### A3.5 Las miradas, con su fecha exacta — escritas, no decididas sobre la marcha

**El ritmo ya no se proyecta: se mide donde ocurre.** La v5 lo estimaba
desde la ventana antecedente (256 filas en 39 días hábiles al 31-ago)
porque la población no existía. Hoy la población tiene 38 días hábiles de
historia, y contarla es legítimo —un conteo no es una mirada—, así que el
ritmo sale de ahí:

> **288 filas en 38 días hábiles (2026-09-01 a 2026-10-22) en 36 fechas de
> emisión = 7.579 filas por día hábil.** Es **15% más rápido** que lo
> proyectado, así que todas las miradas caen antes de lo escrito.

Dos declaraciones de método sobre ese conteo, las dos incómodas y las dos
necesarias:

1. **El conteo NO aplica `excluir_cero`**, porque `gap_pct == 0` es una
   función de `gap_pct` y sobre la población no se computa ninguna. Es por
   lo tanto un **techo** del n del plan: la convención sólo puede retirar
   filas. Las fechas que salen de él son entonces **más tempranas** que las
   reales, que es la dirección correcta de equivocarse cuando lo que está
   en juego es un plazo de firma. La magnitud del sesgo se mide donde sí se
   puede: en la ventana antecedente la convención retira el **1.87%**.
2. **El conteo del acta §107.1 daba 296 filas y no 288.** La diferencia son
   exactamente las **8 filas del 28-sep** que la regla de conocibilidad
   retira (acta §90.1 d): el conteo aproximado del chat no la aplicaba.
   El acta declara su propio conteo «sin deduplicar», así que en principio
   habría DOS diferencias y no una; atribuirla a una sola es correcto porque
   **la regla de filas firmada no retira ninguna fila de la población**,
   verificado por conteo (`ritmo_poblacion()` da 288 con la regla y 288 sin
   ella: todos sus pares son de feriado y las dos filas corresponden).
   Manda la máquina, y queda como errata en el acta de cierre.

La tabla completa —el n de cada mirada y su fecha, para todo el abanico de
MDE— sale de `tabla_firma.py` y está en §A3.1.d. Acá el par que enmarca la
decisión:

| Mirada | Umbral \|Z\| | **si MDE = 8.51 pp** (el punto) | si MDE = 10 pp (calendario) |
|---|---|---|---|
| 1 | 4.048 | 490 → **2026-11-30** | 355 → 2026-11-04 |
| 2 | 2.862 | 981 → **2027-03-01** | 710 → 2027-01-08 |
| 3 | 2.337 | 1.472 → **2027-05-31** | 1.064 → 2027-03-16 |
| 4 (final) | 2.024 | 1.962 → **2027-08-27** | 1.419 → 2027-05-20 |

**La mirada la dispara el n, no la fecha.** Las fechas son estimaciones al
ritmo medido; si el ritmo cambia, se mueven las fechas y **no** los n. Y la
cláusula 3 de §A3.7 sigue valiendo: un hueco de sellado estira el
calendario y no adelanta ninguna mirada.

> **Lo que esta sección NO resuelve, y es la deuda que la v5 declaró y
> sigue abierta:** nada avisa cuando la población se acerca al n de una
> mirada. Con el ritmo medido, el aviso dejó de ser cómodo y pasó a ser
> necesario: la primera mirada del valor de calendario cae a diez días de
> hoy. La propuesta más chica —un chequeo que sólo cuenta filas, sin tocar
> el vigía— está en la tarjeta **§95**.

### A3.6 Futilidad — cuándo se para por no haber nada

Frontera **NO vinculante** (parar es una opción, no una obligación; no
consume alfa), por potencia condicional bajo el MDE < 20%:

| Mirada | Se puede declarar futilidad si Z observado < |
|---|---|
| 1 | −1.662 |
| 2 | +0.016 |
| 3 | +1.033 |

**También independientes del MDE:** dependen de la fracción de
información y del umbral final, no del tamaño del efecto.

Leído en castellano: en la primera mirada solo se para si el modelo va
claramente PEOR que la constante; para la tercera, basta con que no haya
una tendencia positiva razonable para que seguir acumulando ya casi no
pueda cambiar el resultado.

**Características operativas del plan completo** (lo que la v1 no
publicaba, y es lo que dice si el diseño sirve o no), **bajo el estadístico
idealizado, con la varianza conocida** — la misma etiqueta que lleva la
tabla de §A3.3, y que esta tabla no llevaba:

| | Valor |
|---|---|
| Potencia, sin parar por futilidad | 0.8000 |
| Potencia, parando en la frontera de futilidad | 0.7914 |
| P(parar por futilidad \| H₁ cierta) — el costo | **0.0828** |
| P(parar por futilidad \| H₀ cierta) — el beneficio | **0.8531** |

> **Y si §92 se firma por la salida 2, esta tabla se recomputa.** La
> frontera de futilidad es independiente del MDE (depende de la fracción de
> información y del umbral final), pero se calibró a potencia 0.80; con la
> potencia declarada en 0.7537 los cuatro números de arriba se mueven. No se
> recomputan acá porque la firma todavía no existe, y recomputarlos contra
> una potencia que puede cambiar sería trabajo que hay que rehacer.

Es la fila del medio la que justifica la frontera: **si de verdad hay una
ventaja igual al MDE, la futilidad la aborta por error el 8% de las
veces**.
A cambio, si no hay nada, el 85% de las veces el diseño lo dice antes de
llegar a 2027-05-19 (con el MDE de calendario) o a 2027-08-27 (con el punto
derivado); el 2027-07-17 que esta línea traía salía de la tabla de fechas
que la corrida 17 retiró de `mirada.py`, al ritmo superado. Ese es el canje,
con sus dos números al lado.

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
   en la mirada 1 la tasa de discordancia observada se aparta de 0.4924 en
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
poco: lo lleva de 0.05 a 0.094, que es peor que el **PISO** del pasivo
histórico (0.0905) y bastante menor que su escenario alto (0.1779).
Compararlo contra «el pasivo entero», como decía esta línea, era compararlo
contra el extremo que más favorece al proyecto — lo que §A1 prohíbe doce
páginas antes.

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
   hoy descartaría las 262 de la ventana antecedente y tendría 288 de
   población, y aun así no computa, porque los dos candados siguen en
   `None`); **se niega a computar el
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

#### La exposición de la población, censada el 25-oct-2026

El documento se escribió suponiendo que la población empezaba a acumular el
día del congelamiento. **No se congeló, y la población lleva casi dos meses
creciendo mientras el proyecto publicaba sobre ella todos los días
hábiles.** Lo que sigue sale de leer el CÓDIGO, no los valores.

**Lo que se puede afirmar con evidencia estructural, y es menos de lo que
parece: nadie corrió `mirada.py`.** La carpeta
`GEMELO/SECUENCIAL/miradas/` **no existe**, y con ella no existe
`registro.log`, que es la huella que toda corrida que computa deja; ninguna
acta de `DECISIONES.md` registra una mirada; y los dos candados habrían
abortado cualquier intento.

**Lo que NO se puede afirmar: que nadie computó la ventaja.** El argumento
de la huella es ciego a cualquier cómputo que no pase por `mirada.py`, y
este mismo documento lo prueba: §A3.2 cuenta que
`ac1_ventana_antecedente()` habría computado sobre la población **sin dejar
línea en `registro.log`**, porque ese registro sólo lo escribe `mirada.py`.
La ausencia de la carpeta establece una cosa y no la otra.

**Lo que SÍ se publica sobre la población, por superficie:**

| Superficie | Qué sirve, del código | Alcance |
|---|---|---|
| Reporte de Telegram, 18:25, todos los días hábiles | `linea_base.metricas_apertura(dias=30)`: `n`, acierto del gap %, acierto de sesión %, MAE | ventana de 30 días — hoy **toda** de la población |
| `/api/historial` · `/historial` · dashboard | `evolucion_aciertos_apertura()`: acierto del gap y de sesión **por fecha**, con su `N` | **toda** la historia, fecha por fecha |
| `/api/historial` · `/historial` · dashboard | `ultimas_predicciones_apertura(limite=100)`: fila por fila, `Gap real %`, `Acierto gap`, `Estimado %`, `Sesión objetivo`, `Emitida (UTC)` | las **100** verificaciones más recientes — hoy todas de la población |
| `/api/historial` | Wilson del acierto del gap y desgloses **por región y por régimen** | toda la historia |
| `/api/rieles` | ventaja contra la base, su intervalo de clúster de día, McNemar y la rama R2 | **un SUBCONJUNTO ESTRICTO de la ventana antecedente**: corta en `verificado_en ≤ 2026-08-28` (`cifras.CORTE_README`), tres días antes del corte de emisión de la ventana |
| `README.md` | los doce bloques | **sólo la ventana antecedente** |

**Qué parte del estadístico de McNemar se puede reconstruir con eso — sin
reconstruirlo, que es lo que esta sección hace y no hace:**

> **Todo, sobre las 100 filas más recientes.** `ultimas` sirve por fila
> `Gap real %` y `Acierto gap`. Con la primera se deriva exactamente
> `base_acierto = (gap > 0)` y se aplica `excluir_cero`; la segunda es el
> acierto del modelo. De ahí salen `b` y `c`, y con `Fecha` salen los
> clústeres de día, o sea también `V̂` y `Z`. **El estadístico entero del
> pre-registro es reconstruible por quien lea la página**, sobre ese
> subconjunto.
>
> **Sobre el resto de la población, no.** `evolucion` da el acierto del
> modelo por fecha pero no el de la baseline, así que `b − c` no sale; el
> agregado de 30 días, lo mismo. Y la única superficie que publica la
> ventaja de verdad está anclada a la ventana antecedente.

**Lo que esto cuesta — y el quinto dictamen demostró que la segunda mitad de
este párrafo era falsa.** La redacción anterior decía: «un α no se infla
porque se publiquen los insumos; se infla cuando una regla de decisión se
aplica repetidamente, y nadie la aplicó … y la diferencia no tiene cifra».
**La primera mitad es correcta; la segunda no, y la diferencia SÍ tiene
cifra** (exigencia E5):

> **La regla de decisión no está COMPLETA.** Le faltan cuatro parámetros
> firmados —cinco, contando el residuo de coherencia— y por lo menos dos
> deciden: el **MDE** fija `n₁`, o sea cuándo se mira por primera vez; y la
> **regla del estimador** fija la clave del clúster, o sea `V̂`, que es el
> denominador del estadístico. **Elegir esos dos después de que los
> desenlaces de la población están publicados no es «mirar a escondidas»:
> es ADAPTAR EL DISEÑO SOBRE DATOS OBSERVADOS**, que es la cosa que un
> pre-registro existe para impedir. Y no es hipotético: la superficie que lo
> permite la lee todos los días hábiles la misma persona que firma.
>
> **Cuánto, en su forma DÉBIL primero, que es la que no depende de ninguna
> cifra por computar:** el abanico de §A3.1.d pone **cinco** primeras
> miradas sobre la mesa (1.459 / 490 / 355 / 288 / 206 filas). Firmar el MDE
> después de la exposición es elegir un punto de parada dentro de una
> familia declarada, y eso es formalmente el mismo acto que la mirada
> furtiva que la tabla de arriba ya tarifa. Por lo tanto, **con UNA sola
> selección equivalente el α del plan ya es ≥ 0.0939** — eso sale de la
> propia tabla y es seguro. **Con las cinco, del orden de 0.12–0.14.** El
> valor exacto es un máximo sobre cinco planes, lo computa `fronteras.py` y
> **no está computado**: es parte de E5. La forma débil se escribe primero a
> propósito, para que lo que se concluya de acá no se caiga si el exacto
> resulta ser 0.11 en vez de 0.14.
>
> **Y la exposición es PEOR de lo que esta sección declaraba.**
> `ultimas_predicciones_apertura(100)` sirve también **`Estimado %`**, que
> con la identidad de §A2 (`discordante ⟺ estimado < 0`) da `b+c` fila por
> fila: el estadístico queda **sobre-determinado**, con chequeo cruzado
> interno, no apenas reconstruible. *Atenuante que esta sección no se
> adjudicaba:* esas filas se sirven **sin** la regla de filas firmada
> (tarjeta §82.1), así que quien reconstruya cae sobre un conjunto de filas
> distinto del del plan.

**Lo que además se destruye, y sigue sin tener cifra:** la verificabilidad
de «nadie miró». El proyecto puede mostrar que no hay registro de ninguna
mirada y que su herramienta nunca corrió; no puede mostrar que nadie hizo la
resta con lo publicado.

**Las opciones son de Nicolás y están en la tarjeta §93**, con el costo en
calendario de cada una medido por conteo. Esta sección no elige, y el
`estadistico-adversario` dictamina si la exposición admite un número.

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

> **DECLARADO (25-oct-2026): las fechas de esta sección NO se
> recomputaron.** Salen del ritmo proyectado de la v5 (6.56 filas por día
> hábil, contando desde cero) y no del ritmo medido de la población (7.579,
> contando desde 288). Al ritmo medido **caen antes** — la fila (a), por
> ejemplo, cerca de septiembre de 2029 en vez de enero de 2030. Se declara
> en vez de recomputarse porque la conclusión de la sección no depende del
> año exacto sino del orden de magnitud: la pregunta condicional no es
> contestable por esta vía en un plazo humano, y eso vale con los dos
> ritmos. La dirección del error es **pesimista**, que es el lado seguro.

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

**No hay una fecha, y hay dos maneras de decir cuál es el rango. Las dos
están abajo, y conviene no confundirlas** — confundirlas fue el defecto D2
del quinto dictamen.

**(1) El rango HONESTO**, con `p_d = f` propagada por réplica (§A3.1.d), al
ritmo medido de la población:

> **el análisis final cae con mediana en 2027-08-20** y su IC95 va de
> **2027-03-08 a 2028-10-04** (`N_max` [1.025, 4.153] filas); la primera
> mirada, mediana **2026-11-27**, IC95 [256, 1.038] filas. **P(la mirada 1
> ya está vencida, si se firma la regla del punto derivado) = 0.0614**,
> Wilson 95 % [0.0569, 0.0663].

**(2) La respuesta CONDICIONAL a cada valor que se podría firmar**, que es
la pregunta que la firma hace de verdad. **No es un rango**: cada fila
combina el MDE de una réplica con `p_d` del punto, y las dos filas de los
bordes caen fuera del intervalo de (1):

| Si se firma | el análisis final cae en | y la primera mirada |
|---|---|---|
| 4.94 pp — borde inferior del IC del MDE | 2029-08-14 | 2027-05-27 |
| **8.51 pp — el punto derivado** | **2027-08-27** | 2026-11-30 |
| 10 pp — elección de calendario | 2027-05-19 | 2026-11-04 |
| 13.09 pp — borde superior del IC del MDE | 2027-01-29 | **ya vencida** |

> **RETIRADO por E2 del quinto dictamen: «dos años de diferencia entre los
> dos bordes del mismo intervalo».** Esa frase, y el **2029-08-10** que la
> sostenía, eran un artefacto de emparejar el MDE de una réplica con `p_d`
> del punto. **Con la propagación coherente** (`p_d = f` por réplica) el
> análisis final cae con mediana en **2027-08-19**, y `N_max` en IC95
> [1.025, 4.153] filas: la dispersión es **real pero menor**, y el 2029 no
> es borde de nada. La tabla de arriba se conserva como respuesta
> CONDICIONAL a cada valor que se podría firmar, que es la pregunta que la
> firma hace.

Lo que sí queda: la v5 escribía esta sección como si la elección fuera entre
«derivar» y «elegir por calendario», y con el intervalo medido el punto
derivado da una fecha **más temprana** que el valor de calendario que la v5
trataba como el atajo.

Y hay un cuarto desenlace, el más probable de todos según lo que el
proyecto sabe hoy: que en alguna de las tres miradas intermedias el diseño
declare **futilidad** y la respuesta sea «si hay ventaja, es menor que el
MDE firmado». Bajo H₀ eso pasa el 85% de las veces. **Que suela pasar
temprano es una expectativa y no una cifra**: descomponer la futilidad por
mirada es un cómputo que no está en este repo, igual que la descomposición
del α de §A3.2, y por la misma razón no se le pone número.

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
| D1 | Fronteras 2.354 / 4.026·2.847·2.324·2.013, α "0.051 confirmado" (las que la v1 **iba a** congelar) | 2.362 / 4.048·2.862·2.337·2.024, α exacto 0.04995 | A3.4 |
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
0.80. Se adoptó 1.485 porque era el que salía del código versionado de
este repo.

> **Nota de la v6 (25-oct-2026).** Esta línea decía «se congela 1.485». No
> se congeló nada: el documento nunca llegó a congelarse, y además ese
> `N_max` quedó superado cuando `p_d` se recomputó sobre la ventana
> anclada (§A3.3). Se corrige el verbo porque **ninguna línea de este
> documento puede decir «congelado»** mientras falten las cuatro firmas.

---

## Qué NO se hace en este documento

- No se toca `motor.py`, `senales.py`, `snapshot.py`, `universo.py`, ni
  ninguna fila sellada.
- No se decide el MDE definitivo (§A3.1), que es de Nicolás y cambia el
  horizonte por un factor de ocho.
- No se re-analiza la ventana antecedente. Sus **262 filas** (emisión hasta
  el 2026-08-31, sello hasta el 2026-09-02, `excluir_cero`, regla de filas
  firmada) son antecedente; este documento las usa como parámetros de
  estorbo (§A2) y **no computa ninguna cifra de ventaja sobre ellas, ni
  como control** — el encargo de la corrida que escribió este documento ya
  marcó volver a analizarlas como «la trampa de esta etapa», y
  `mde_desde_v6.py` está escrito para que no pueda.
- **No se ejecuta ninguna mirada, y hoy ni siquiera podría.** `mirada.py`
  tiene **dos** constantes sin firmar (`MDE_FIRMADO` y
  `REGLA_DEDUP_ESTIMADOR`) y se niega a computar con cualquiera de las dos
  en `None`. La carpeta `miradas/` no existe: nunca corrió.
- **No se avisa solo cuando se alcanza un n**, y con el ritmo medido eso
  dejó de ser cómodo. No hay job ni timer que dispare la mirada; la fecha
  hay que recordarla, y la primera mirada del valor de calendario cae a
  diez días de hoy. La propuesta más chica está en la tarjeta **§95** y
  **no se instala en esta corrida**.
- **No se congela nada.** Esta versión deja el documento *listo* para
  firma: cada parámetro que es decisión de Nicolás aparece como SIN FIRMAR
  en el acta de congelamiento, con su tarjeta, y la receta del final dice
  qué cambia el día que firme. Ninguna línea de este documento dice
  «congelado».

---

## La v5 también fue rechazada — registro de la corrección a la v6

Cuarto dictamen del `estadistico-adversario`, 31-ago-2026, sin versionar
como `dictamen_XX`: quedó en la cabecera de este documento, en
`DECISIONES.md` §56 y en `GEMELO/resultados/bitacora_04.md`. La v6 la
escribió la corrida 17 el 25-oct-2026. **Nada de lo retirado se borró sin
dejar su línea acá.**

| # | Qué decía la v5 | Qué dice la v6 | Sección |
|---|---|---|---|
| F1 | «versión 5 — NO CONGELADO. Rechazado por cuarta vez. No hay v6» | «versión 6 — NO CONGELADA. **QUINTO RECHAZO**», con las cuatro condiciones atendidas, los tres defectos nuevos del quinto dictamen y el estado de sus once exigencias | cabecera |
| F2 | el acta de congelamiento con fecha **2026-08-31** y commit base `7d42d9b` | las dos líneas en **SIN FIRMAR**: la fecha la pone la firma, y lo que había era la fecha en que se *propuso* congelar | acta |
| F3 | el MDE como «único parámetro abierto» | **cuatro** parámetros SIN FIRMAR con su tarjeta: MDE (§90), regla del estimador (§91), potencia (§92) y población (§93) | acta |
| F4 | la regla de deduplicación como **una** decisión abierta entre `keep="first"` y `keep="last"` | **dos** reglas: la de FILAS está FIRMADA desde el 1-sep (§60, §61) y no es ninguna de esas dos; la del ESTIMADOR es la que falta | §A3.1.a, §A2 |
| F5 | `mde_desde_v6.py` con su propio SQL y sin ancla temporal | la ventana la define `ventana_antecedente.py` con **dos cortes** (emisión 2026-08-31, sello 2026-09-02) y un candado que verifica que está cerrada; tests de comportamiento | §A2, §A3.1 |
| F6 | `p_d = 128/248 = 0.516`, de la rama de filas derogada el 3-sep (acta §78) | **`p_d = 129/262 = 0.4924`** sobre la ventana anclada con la regla firmada | §A2 |
| F7 | `ac1` citada en dos valores contradictorios («34 contra 35 fechas»), por un lector de base sin ancla | **−0.176 ± 0.164 sobre 37 fechas**, y el lector anclado. El defecto había pasado de «cifra que se mueve» a **mirada furtiva sobre la población** | §A3.2 |
| F8 | E\|r\| con/sin duplicados 4.0231 / 3.7242 %, con `keep="first"` | 3.8666 / **3.5556 %** sobre la ventana anclada y con la regla firmada; el hallazgo (30 filas, 15 pares, 4 sesiones) **reproduce exacto** | §A3.1.a |
| F9 | §A3.1.c derivada en la escala del **retorno de sesión**, con sus tablas | toda la sección en la escala del **endpoint** (`acierto_gap`), que es lo que §A2 congela y lo que la cabecera de la v5 ya decía sin aplicarlo | §A3.1.c |
| F10 | «cinco sesiones» en el párrafo de `cola_decisiones`, contradiciendo a la ERRATA del 1-sep doce líneas más arriba | **cuatro**, y la errata de la errata declarada | §A3.1.a |
| F11 | §33.8 citada como «pregunta pendiente» | **cerrada** por §60 y §61; lo que sigue en cola es la rama «+ coherencia» (§2a-ter, tarjeta §46) | §A3.1.a |
| F12 | «una razón se sostiene, la otra fue retractada» | **ninguna de las dos se sostiene con su intervalo**: los intervalos de la razón 1 se superponen y sus puntos distan 0.1 pp. La conclusión sobrevive por un argumento estructural, declarado más débil | §A3.1.b |
| F13 | SMH −5.18% en 39 sesiones, sin intervalo y sin declararlo | **−8.47% en 40 sesiones** hoy, con la razón por la que no lleva intervalo **y** el hallazgo de que su insumo **no está anclado y no se puede pre-registrar** (tarjeta §94) | §A3.1.b |
| F14 | el MDE propuesto, derivado en la escala equivocada, **RETIRADO** desde el 31-ago (acta §56) | **8.51 pp, IC95 [4.94, 13.09]** con dos insumos propagados y el tercero declarado fuera | §A3.1.d |
| F15 | el intervalo del MDE propagaba **un** insumo de tres y se publicaba como si fuera el intervalo del MDE entero | propaga **dos** por clústeres de día; el de un insumo se imprime al lado, etiquetado, y hay test de que el conjunto es más ancho | §A3.1.c/d |
| F16 | Connor 403 filas, ×DEFF 1.450, `N_max` 1.485 y 3.039 | **384 / 1.383 / 1.419**, y el abanico condicional completo; el factor secuencial se COMPUTA (1,026380) en vez de cablearse | §A3.3 |
| F17 | ritmo **6.56 filas/día hábil**, proyectado desde la ventana antecedente | **7.579**, MEDIDO por conteo sobre la población (288 filas en 38 días hábiles), con el sesgo de no aplicar `excluir_cero` declarado y acotado (1.87%) | §A3.5 |
| F18 | las fechas de las miradas en dos tuplas cableadas en `mirada.py` | computadas por `tabla_firma.py` al ritmo medido, contando día hábil por día hábil en vez de prorratear por 7/5 | §A3.5 |
| F19 | «la primera mirada es el 2026-11-19 y no antes» — la fecha de un MDE que el propio documento retiraba | el **MDE crítico, 11.09 pp [8.93, 12.81]**, dentro del IC95 del MDE, con P(vencida) = 0.0614 [0.0569, 0.0663] | §A3.1.d, §A5 |
| F20 | potencia «~0.76» sin cifra ni script | **0.7537** contra 0.8000, con script y test, y el costo de la salida 1 también en cifra (+235 filas, 31 días hábiles) | §A3.3 |
| F21 | el pasivo de §A1 cerrado el 31-ago, con «≥12 miradas» | **cuatro miradas más** listadas con su acta, una de ellas una **publicación** (§78), y el argumento «ninguna afirmación publicada depende de un p que cruzó» corregido | §A1 |
| F22 | la tabla de §A1 citando cifras de la rama derogada sin marca | marca de retiro sobre las filas 7 a 12, con la razón para conservarlas | §A1 |
| F23 | §A2 nombrando McNemar sin citar el acta **§61**, que lo degradó como estadístico principal al día siguiente de escribirse | §61 citada, con lo que el plan honra y lo que no, y la decisión de no cambiar la regla de decisión en esta corrida | §A2 |
| F24 | la exposición de la población no contemplada | censo por superficie leído del código, y el hallazgo de que el estadístico entero es **reconstruible** sobre las 100 filas más recientes que la API publica | §A3.8 |
| F25 | `N_MAX_POR_MDE` y `FECHAS_POR_MDE` con los valores viejos adentro | vaciados a propósito, con test: dos diccionarios con valores viejos son una invitación a firmar uno de los dos | `mirada.py` |

### Correcciones del 25-nov-2026 al texto de la v6 (O-1, re-dictamen del guardián, 25-nov)

El re-dictamen del `guardian-constitucion` del 25-nov-2026
(`GEMELO/resultados/dictamen_17/guardian_redictamen.md`) encontró que la
corrección de O-1 había llegado al código y no a dos lugares de este
documento. Se corrigieron en su sitio ese mismo día (corrida 18a-bis),
antes del commit; las cifras nuevas se leyeron de
`GEMELO/resultados/tabla_firma_17.json` (medido el 2026-10-25) y no se
recomputó nada.

| # | Qué decía | Qué dice | Sección |
|---|---|---|---|
| G1 | la prosa nombraba el factor cableado 1.0241 con su drift requerido 2.8352 (contra 2.802 de muestra fija), y el encabezado de la columna de `N_max` decía ×1.0241, sobre una columna que ya estaba computada con el factor nuevo | nombra el factor secuencial computado por `diseno_secuencial.factor_secuencial()` y remite su valor y el drift requerido al artefacto sellado, sin cablearlos en la prosa; el encabezado dice × factor secuencial computado. Las cifras de la columna no cambian. Razón: O-1, re-dictamen del guardián, 25-nov | §A3.3 |
| G2 | miradas 1 a 3 del par que enmarca la decisión con los n de la generación del factor cableado: a 8.51 pp, 979 y 1.468 → 2027-05-28; a 10 pp, 354 / 708 / 1.062 (en la misma tabla que la fila 4, que ya llevaba el `N_max` vigente) | a 8.51 pp, 981 y 1.472 → 2027-05-31; a 10 pp, 355 / 710 / 1.064. Las demás celdas de la tabla no cambian. Razón: O-1, re-dictamen del guardián, 25-nov | §A3.5 |

**Lo que el dictamen verificó en verde y la v6 NO tocó:** las fronteras
contra las dos varas externas, la tabla de exposición residual de §A3.2 (8
de 8 celdas y sus Wilson), la derivación de la futilidad, la contabilidad
de la inflación de §A1 contra Armitage-McPherson-Rowe, los tres candados
estructurales de `mirada.py` y la exclusión de la ventana antecedente del
estadístico.

**Una cosa que la v6 declara sin recomputar, y hay que decirlo acá.** La
tabla de exposición residual de §A3.2 se computó con las fechas por mirada
que salen del ritmo de la ventana antecedente (51, 101, 152, 203). Con el
ritmo medido serían otras, y más fechas es un bootstrap mejor y por lo
tanto un α simulado **más bajo**: no recomputarla deja la tabla
**pesimista** sobre la propia exposición del plan, que es la dirección
honesta de equivocarse. Recomputarla es una corrida de 20.000 réplicas y va
a la cola en vez de hacerse a medias.

---

## Las once exigencias del quinto dictamen, y su estado

Las cinco primeras son bloqueantes: sin ellas no hay v7. Esta versión
atendió las que no exigen una corrida de simulación propia; las dos que sí
están en tarjetas con su costo, porque hacerlas a medias es peor que
declararlas.

| # | Exigencia | Estado |
|---|---|---|
| **E1** | resolver D1: o la clave del clúster es un parámetro con sus dos ramas y la tabla de exposición se recomputa para las DOS, o se retira la recomendación de §91; y la cabecera deja de decir congelado el estadístico mientras el clúster esté sin firmar | **ATENDIDA EN PARTE.** La cabecera y el acta corregidas: se propone congelar la FORMA del estadístico, no la clave. **Falta** recomputar la tabla de exposición para la clave por sesión objetivo — 20.000 réplicas por rama, tarjeta §97 |
| **E2** | rehacer el abanico con `p_d` = `f` por réplica; publicar la identidad; retirar el 2029-08-10 y «dos años de diferencia» | **ATENDIDA, y el re-dictamen verificó que el cómputo reproduce exacto.** `tabla_firma.propagacion_conjunta`: `N_max` mediana **1.920**, IC95 [1.025, 4.153]. La identidad `p_d ≡ f` publicada en §A2. Las dos frases retiradas **en §A3.1.d, §A5, §A3.3 y en el script y el artefacto sellado** — el re-dictamen cazó que la primera corrección no había llegado a tres de esas copias (F1, F2, F4) |
| **E3** | declarar la degeneración, citar `secuencial_v5.md`, reconciliar la banda, corregir «no distinguen 0 de +0.2» y declarar la cobertura del ± | **ATENDIDA EN PARTE.** Declarada la degeneración (20 de 37 fechas con `d_j` = 0), citado el archivo del 2-sep, corregida la frase (el límite al 95 % es +0.145) y declarado que el ± es un error estándar. **Falta** reconciliar la banda con el hallazgo de que el eje es inerte — tarjeta §97 |
| **E4** | la potencia con intervalo o sin cuatro decimales; reconciliar las dos mediciones; que `potencia_del_plan` deje de aceptar lo que no lee | **ATENDIDA EN PARTE.** La firma ya no acepta argumentos (con test), y la cifra se cita **≈0.75**. **Falta** reconciliar 1.7 pp simulada contra 4.6 pp analítica — tarjeta §92 |
| **E5** | población: elegir la opción (b) de §93, o publicar el α real | **ATENDIDA como declaración; la ELECCIÓN es de Nicolás.** §A3.8 publica que el α del plan es del orden de **0.12–0.14** bajo la opción (a), y por qué. El valor exacto (máximo sobre cinco planes, `fronteras.py`) **no está computado** — tarjeta §93 |
| E6 | el pasivo de §A1 con número o con cota de un lado; retirar «un piso más bajo de lo que era» | **ATENDIDA la cota de un lado** (F10): la frase está retirada y la línea del acta dice ahora **«α ≥ 0.09, sin extremo superior establecido»**, no un rango. **El NÚMERO sigue sin computar**: exige una corrida con `simulador/proceso.py` — tarjeta §96 |
| E7 | verdad conocida antes que verdad observada, para los tres estimadores que deciden | **NO ATENDIDA.** Es la exigencia más grande y la más importante de las no bloqueantes: hoy ninguno de los tres se verificó contra nada más que contra sí mismo — tarjeta §97 |
| E8 | corregir la descripción de los grupos; reportar la distribución de tamaños; declarar el quinto ítem sin firmar | **ATENDIDA.** 11 de DOS y 4 de CUATRO, en el documento, en las glosas y en la tarjeta; `pares_misma_sesion` reporta el reparto, con test; la rama «+ coherencia» declarada como quinto ítem |
| E9 | arreglar la razón 1 o bajarle el estatus; retirar «los dos puntos están a 0.1 pp» | **ATENDIDA bajándole el estatus**, que es la salida que §A3.1.b ya tomaba: la frase retirada y los tres defectos de resolución declarados. Arreglar el cómputo es la tarjeta §94 |
| E10 | hacer aplicable la prohibición de §A2 y renombrar el estadístico en la letra de §61 | **ATENDIDA la prohibición** (pasa a «publicar y usar», porque `Σ d_j` ES `b−c`). **El renombre NO**: cambiar la letra de §A2 toca la sección que el acta propone congelar, y el dictamen pide además una validación que no existe — tarjeta §97 |
| E11 | arreglar la receta; sumar al registro de intentos las cuatro filas del dictamen | **ATENDIDA la receta** (las firmas van en un acta NUEVA; §90, §91 y §93 de `DECISIONES.md` están ocupadas). Las cuatro filas del registro de intentos (N = 354 → **358**) van al acta de cierre |

**La SEGUNDA pasada del dictamen (`dictamen_17/re_dictamen.md`): sigue
RECHAZADO, y «el rechazo se estrechó mucho».** Verificó que el cómputo de E2
reproduce exacto y que §A3.1.d y §A5 «quedaron ejemplares»; cerró **E8 sin
reservas**; y encontró que **la primera corrección de E2 no había llegado a
tres copias de su propia afirmación, ni al script, ni al artefacto sellado**
— la misma errata que §A3.1.a narra, cometida de nuevo en la ronda que la
narra. Dejó once exigencias **mecánicas** (F1 a F11), ninguna de las cuales
exige una simulación, y dijo que con ellas **el documento queda sin
bloqueantes salvo E6 y E7**. Esta versión las aplicó todas:

| # | Qué pedía | Qué se hizo |
|---|---|---|
| F1 | borrar el punto 3 de §A3.1.d, que reinstalaba el 2029 a cuarenta líneas de su retractación | reescrito, con la errata declarada en su sitio |
| F2 | rotular la tabla de §A3.3 y cambiar «ahora el abanico es el intervalo del MDE completo» | rotulada CONDICIONAL; la frase corregida |
| F3 | recomputar el «13 a 92 días hábiles», construido sobre el emparejamiento retirado | **16 a 66**, sobre el IC honesto de `N_max` |
| F4 | llevar la propagación conjunta y P(vencida) a `tabla()`, `markdown()`, `--json` y al JSON **sellado** | hechas las cuatro; el `markdown()` imprime el intervalo honesto PRIMERO y el abanico rotulado después |
| F5 | actualizar las dos filas del acta que se quedaron atrás del cuerpo | la fila de la potencia pasa a ≈0.75; la del MDE lleva el IC del crítico y P(vencida) |
| F6 | reconciliar `FACTOR_SECUENCIAL` o declarar la potencia 0.7991 | **se computa** desde `diseno_secuencial` (1.026380); el 1.0241 cableado no reproducía y queda al lado |
| F7 | reemplazar el test tautológico de potencia | reemplazado por uno que evalúa la potencia en el drift que el factor **compra**, con contraprueba de que el factor viejo falla |
| F8 | test de comportamiento de `propagacion_conjunta` | fija que los dos extremos del abanico caen **fuera** de `n_max_ic`, y que P(vencida) viaja con su Wilson |
| F9 | P(vencida) con su Wilson y con el nombre condicionado | **0.0614, Wilson [0.0569, 0.0663]**, y el nombre dice con su condicional explícito (si se firma la regla del punto derivado) |
| F10 | corregir las dos filas sobre-reportadas y escribir el pasivo como cota de un lado | hechas; el acta dice **α ≥ 0.09, sin extremo superior establecido** |
| **F11** | §A3.2 punto 3: la clave del clúster pasa a ser el parámetro SIN FIRMAR que ya es en el acta | **hecho — es la que levanta el bloqueante D1**, y no toca ninguna frontera |

**Lo que el quinto dictamen verificó en verde y no hay que volver a tocar:**
las cuatro condiciones del cuarto rechazo, atendidas de verdad; que el
documento reproduce el día que se firma; el DEFF de planificación (V̂ máximo
3.618 contra 3.6 supuesto); el ancla y su candado, incluido que no existe la
fila que podría dispararlo; el techo del conteo sin `excluir_cero` y su
dirección; el error estándar de Bartlett para `ac1`, que resultó
**conservador** por 1.16; y que los tests nuevos son de comportamiento.

---

## Receta de congelamiento — escrita para el día en que Nicolás firme

**No se ejecuta en esta corrida.** Es la lista de lo que cambia, para que
el congelamiento sea un acto chico y verificable en vez de una corrida de
descubrimiento.

**Precondición.** Las firmas escritas y fechadas en **un acta NUEVA** de
`DECISIONES.md`: MDE, regla del estimador, potencia, población y —quinto
ítem, que la primera redacción de esta v6 no contaba— la rama «+
coherencia» de `cola_decisiones.md` §2a-ter. Si falta una, no se congela
nada: los candados abortan y está bien que aborten.

> **CUIDADO CON LOS NÚMEROS, y es la exigencia E11 del quinto dictamen.**
> §90 a §95 son **tarjetas de `GEMELO/resultados/espera_firma.md`**, no
> actas. En `DECISIONES.md` los números §90, §91 y §93 **ya están ocupados**
> por actas de septiembre y octubre sobre otras cosas. La primera redacción
> de esta receta decía «las firmas escritas en `DECISIONES.md`: MDE (§90)
> …», que dirigía la firma a casillas ocupadas. Las firmas van en **un acta
> nueva**, con el número que siga al último, y el acta cita las tarjetas por
> su número de `espera_firma.md` diciendo de qué archivo son.

**Qué constante cambia, en qué archivo:**

| Firma | Tarjeta (`espera_firma.md`) | Archivo | Qué se escribe |
|---|---|---|---|
| MDE | §90 | `GEMELO/SECUENCIAL/mirada.py` | `MDE_FIRMADO = <valor en proporción>` |
| Regla del estimador | §91 | `GEMELO/SECUENCIAL/mirada.py` | `REGLA_DEDUP_ESTIMADOR = "<una de REGLAS_DEDUP_ESTIMADOR, nunca una de REGLAS_PROHIBIDAS>"`. **Si se firma `clusterizar_por_sesion_objetivo`, antes hay que recomputar la tabla de exposición residual de §A3.2 para esa clave** (E1): si no, la banda [0.046, 0.079] deja de describir al estimador |
| Potencia | §92 | este documento, §A3.3 | la salida elegida; si es la 1, además el factor en `tabla_firma`, con acta |
| Población | §93 | este documento, acta y §A2 | la fecha de inicio, y si cambia, `ventana_antecedente.CORTE_EMISION` y `mirada.FECHA_CONGELAMIENTO` **a la vez** (hay test de que son iguales) |
| Rama «+ coherencia» | §46 | capa de medición | si se firma, mueve el stock, el ritmo y las cuatro fechas: hay que volver a correr `tabla_firma.py` |

**Qué líneas del acta de congelamiento se llenan:** «Fecha de
congelamiento», «Commit base», «Clúster del estadístico», «MDE»,
«Potencia» y la fecha de inicio de «Población». Cada una con el número de
la firma que la autoriza.

**Qué tests fijan que el documento y el código dicen lo mismo** (censados
con `grep`, no de memoria, el día que se aplique):

- `tests/test_secuencial_17.py::test_los_dos_cortes_valen_lo_mismo_que_en_el_preregistro`
  — el corte de emisión no puede divergir entre los dos archivos.
- `tests/test_secuencial_17.py::test_p_d_del_plan_es_la_que_mide_el_script`
  — la constante de planificación reproduce desde su script.
- `tests/test_secuencial.py::test_el_mde_sin_firmar_bloquea_la_mirada` y
  `tests/test_secuencial_17.py::test_la_regla_del_estimador_sin_firmar_bloquea_la_mirada`
  — **los dos CAMBIAN DE SENTIDO con la firma**: hoy afirman que el candado
  aborta, y después de firmar tienen que afirmar que el valor firmado es el
  que está escrito. Reescribirlos es parte de la receta, no un efecto
  colateral.
- `tests/test_secuencial_17.py::test_las_tablas_de_n_max_y_de_fechas_quedaron_vacias_a_proposito`
  — si la firma vuelve a poblar `N_MAX_POR_MDE`, este test lo dice.

**El test sobre datos sintéticos que confirma que `mirada.py` deja de
negarse** — y que **nunca corre contra la base real**:

```python
def test_con_las_constantes_firmadas_la_mirada_computa(monkeypatch, tmp_path):
    """Con el MDE y la regla firmados, y un frame SINTÉTICO que alcanza el n
    de la mirada, `ejecutar` computa en vez de abortar. Sobre datos
    sintéticos: ejercitar el estadístico contra la población es la mirada."""
    monkeypatch.setattr(M, "MDE_FIRMADO", <el valor firmado>)
    monkeypatch.setattr(M, "REGLA_DEDUP_ESTIMADOR", "<la regla firmada>")
    df = _df_sintetico(n_fechas=..., por_fecha=..., ventaja=...)
    monkeypatch.setattr(M, "cargar_ventana_nueva", lambda: (df, 0))
    monkeypatch.setattr(M, "RUTA_REGISTRO", str(tmp_path / "r.log"))
    s = M.ejecutar(1)
    assert "z" in s and s["regla_estimador"] == "<la regla firmada>"
```

**Lo que la receta NO autoriza.** Correr la mirada. La mirada la dispara el
n y se ejecuta en su fecha de calendario, con `--escribir`, y su acta se
commitea cruce o no cruce (§A3.8 regla 1). Congelar y mirar son dos actos
distintos y conviene que sean dos días distintos.
