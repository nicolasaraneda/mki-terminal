# El jardín de senderos que se bifurcan

*Cuánto de lo que este proyecto cree depende de sus elecciones de análisis y no de sus datos.*

> **EN DIEZ SEGUNDOS**
> 
> **1. Toda la información discriminante del track record es un 10-6 en 17 días.** Contra «siempre al alza» el modelo sólo puede diferir cuando predice BAJA: 121 de 238 filas, agrupadas en 17 días de emisión, de los que ganó 10, perdió 6 y empató 1 — binomial exacta **p = 0.45**. Eso se entiende sin estadística, y todo lo que sigue es la ruta formal hacia el mismo hecho.
> 
> **2.** Bajo la **regla de deduplicación firmada** la ventaja de la ventana es +9.7 pp (la publicada, anterior a la firma, es +6.5 pp); su intervalo honesto —clúster de día, que es la unidad real— es **[-7.2, +26.5] pp**. No es que el modelo falle: **el diseño no tiene potencia**. Frente al efecto de la regla la potencia es **18%** (frente al publicado, 8%), y detectarlo al 80% exigiría **25 pp, IC95 [17, 31]**.
> 
> **3.** Sobre eso, 192 formas legítimas de medir la misma ventana dan una ventaja entre -1.1 y +15.4 pp, y **0 de 192** con p < 0.05 por clúster (59 por la ruta publicada, que supone filas independientes). No sobrevive a todas las celdas ninguna afirmación sobre la ventaja del modelo. **El track record todavía no alcanza para juzgar al campeón, en ninguna dirección.**

- Generado: 2026-09-01T13:44:59.542128+00:00
- Fuente: `senales.db` en `mode=ro` · modelo 4.6.0 · `legacy = 0`
- Reproducible con un comando: `python -m GEMELO.bifurcaciones` (bootstrap de clústeres de día, semilla 0, 10000 réplicas; permutación de signo por día, 4000 permutaciones)
- **Dos anclas verificadas, y las dos abortan el informe si fallan.** (1) *Publicada*: sin la regla de deduplicación, la celda `excluir_cero · dentro · dentro · dentro · publicado · gap · 0.00` reproduce la ventana sellada del README (n=248, 66.1% contra 59.7%, +6.5 pp, b=72, c=56, p = 0.1849). (2) *Regla firmada*: la MISMA celda con la regla aplicada da n=238, +9.7 pp, b=72, c=49, **p = 0.0451** (exacta; 0.0455 por chi2). Esa es la celda ancla de esta matriz.
- **La firma produjo un TERCER desenlace.** Nicolás firmó conociendo dos: p = 0.1847 sin deduplicar y p = 0.0323 con `keep="last"`, que quedó prohibida. Su regla da **0.0451** — cruza α = 0.05, y no estaba a la vista al firmar. El criterio sigue siendo el correcto; el desenlace se declara porque una decisión informada por dos números que produce un tercero necesita esa nota.
- **Los dos cortes, sellados:** `publicado` = 243 filas (hasta `verificado_en` 2026-08-28, pinchado y estable); `vivo` = 251 filas, última señal 2026-08-27. El nivel `vivo` se mueve con el reloj, así que queda escrito qué era el día de la corrida: sin eso esta cifra heredaría la misma dependencia del reloj que el WS5 diagnosticó.
- **Ninguna cifra publicada se mueve.** La matriz mide alrededor de lo publicado, no en lugar de ello.

---

## EL VEREDICTO

**La cifra de la ventana bajo la regla firmada, con su intervalo honesto: +9.7 pp, IC95 de clúster de día [-7.2, +26.5] pp.** Ése es el número que faltaba, y explica todo lo que sigue: con un intervalo de 34 pp de ancho, esta ventana no separa al campeón de una constante — **y eso vale aunque McNemar cruce α**, que es exactamente la brecha que este informe existe para medir.

**0 de 192 celdas dan p < 0.05.** Ése es el cociente que se pidió medir. Pero el cociente no es un veredicto sobre el modelo: es un veredicto sobre el tamaño de la muestra, y la sección de potencia lo dice con números.

### Dónde vive la comparación, en enteros

Antes de cualquier estimador, la observación que hace legible todo lo demás y que no necesita que nadie confíe en un bootstrap: contra «siempre al alza» el modelo **sólo puede diferir en las filas donde predijo BAJA**. En las demás los dos dicen lo mismo y aportan exactamente cero a la ventaja.

| | |
|---|---|
| Filas del ancla | 238 |
| De ellas, filas de **disidencia** (el modelo predijo baja) | **121** |
| Aciertos del modelo en esas filas | 72 (59.5%) |
| Días con alguna disidencia | **17** de 34 |
| Días con saldo a favor / en contra / empatados | 10 / 6 / 1 |
| Binomial exacta sobre los días con saldo | **p = 0.45** |

Es decir: los **b = 72** y **c = 49** que sostienen el p de la regla no son 121 observaciones independientes. Son 10 días ganados contra 6 perdidos. **Un 10-6 no distingue nada**, y para verlo no hace falta ningún aparato: alcanza con contar. Todo el ICC, el bootstrap de clúster y la permutación de abajo son la ruta formal hacia este mismo hecho.

El estimador es el que respeta el **clúster de día**: las ~8 filas de una sesión son βᵢ·SOX sobre el MISMO movimiento del SOX, así que fallan y aciertan casi todas juntas. Computado sobre el ancla (238 filas en 34 días, 7.0 por día), el ICC por día de la diferencia pareada es **0.392** y el efecto de diseño **3.55**: **el n efectivo es 67, no 238.** El ICC es el estimador **ANOVA de una vía** (Fisher/Donner, con el tamaño ajustado m0 y no la media) y el deff usa el **tamaño de Kish**, Σn²/N — una sola procedencia para la cifra, declarada aquí: con clústeres desiguales Kish da 7.50 contra 7.00 de la media simple, y el deff pasa de 3.54 a 3.55. **Ese cambio vino de una corrección del `estadistico-adversario`**, que señaló que el docstring prometía Kish y el código usaba la media; la conclusión no se movió y la diferencia se deja escrita para que la cifra no tenga dos orígenes. La significancia se computa por permutación de signo a nivel de día (4000 permutaciones) y el IC por bootstrap de días enteros.

**Por la ruta publicada —McNemar, que supone las filas independientes— serían 59 de 192 celdas (30.7%)**, y 59 por la variante chi-cuadrado con corrección de continuidad de la que salen las cifras del README. La distancia entre 59 y 0 no la produce ninguna bifurcación de esta matriz: la produce un supuesto de independencia que los datos no cumplen. **El p publicado es el más generoso de los estimadores disponibles.**

**La ventaja sobre «siempre al alza» recorre [-1.1, +15.4] pp a lo largo de la matriz, con mediana +7.9 pp.** La misma ventana sellada, medida con siete decisiones que el proyecto ya tomó o dejó abiertas, admite un rango de 16.5 puntos porcentuales — 1.7× la cifra de la regla (+9.7 pp). En 94.8% de las celdas es positiva; en el resto, no.

**El eje que más mueve la cifra es `ventana_r2`.** Fijando los otros seis, recorrer sólo sus niveles mueve la ventaja una media de 7.3 pp (máximo 8.6 pp) y el p una media de 0.46; por la ruta publicada es además el único que hace cruzar α = 0.05, en 59 de 96 grupos. Le siguen `zona_muerta` (4.8 pp), `empate` (1.8 pp), `objetivo` (1.7 pp). El que menos mueve es `corte` (0.27 pp).

**Por definición y no por elección, `ventana_r2` es el que urge cerrar** — con la salvedad grande de la sección siguiente. El siguiente en urgencia es `zona_muerta`, y ése sí es una elección abierta que nadie tomó.

### ¿Y si el test simplemente no tiene potencia?

Un test que no puede rechazar nada tampoco es una medición, así que la pregunta hay que hacérsela y contestarla con números. Simulando sobre la estructura real de días —remuestreo de días enteros de los residuos observados, más un desplazamiento constante—:

| | |
|---|---|
| Potencia frente al efecto publicado (+6.5 pp) | **8%** |
| Efecto detectable al **50%** de potencia | 17.7 pp, IC95 [12.6, 21.8] |
| Efecto detectable al **80%** de potencia (el convencional) | **25.2 pp, IC95 [17.1, 31.3]** |
| Días con saldo informativo | 17 de 34 |

**La potencia frente al efecto que el proyecto publica es 8%, apenas por encima de α.** Con eso, el cero de celdas significativas estaba escrito de antemano por la estructura de los datos, no por el modelo. Y el número que hay que citar como umbral de diseño es el de 80% —25 pp—, no el de 50% (18 pp): confundirlos subestima a la mitad lo que hace falta.

**Los dos MDE llevan intervalo, y por la misma razón que todo lo demás.** Un MDE se deriva de la dispersión OBSERVADA entre días, y esa dispersión sale de 34 días, no de infinitos: tiene incertidumbre muestral. Los IC de arriba salen de remuestrear días enteros —la misma unidad de clúster y la misma semilla que el resto del informe— con 200 réplicas para el de 50% y 120 para el de 80%; réplicas degeneradas: 0% y 0%. **Limitación declarada:** el de 80% se busca por bisección sobre una curva de potencia SIMULADA, así que su intervalo arrastra ruido de Monte Carlo además del muestral; el de 50% bisecta sobre un p de permutación y no. En los dos casos el punto y las réplicas usan parámetros idénticos, para que el centro pertenezca a la distribución que lo rodea.


> Y lo que el intervalo agrega a la lectura: incluso en el extremo OPTIMISTA de la banda del 80% (17 pp), el diseño seguiría necesitando una ventaja 2.6× la publicada. **La conclusión no depende de dónde caiga el MDE dentro de su propia incertidumbre**, que es exactamente lo que un intervalo sirve para poder decir.

**Ésa es la lectura honesta del cociente, y es distinta de «el modelo no sirve».** Con 17 días informativos, este experimento no puede resolver todavía un efecto del tamaño que el modelo podría tener. El track record no está refutando al campeón; **está diciendo que aún no alcanza para juzgarlo**, y el supuesto de independencia era lo que hacía parecer que sí. Conviene contrastarlo con el MDE que el pre-registro secuencial derivó (8.96 pp): ese cálculo no lleva corrección de clúster, y el clúster lo multiplica por 2.8. Ese MDE se cita como referencia externa y NO se recomputa acá; su propio intervalo está en disputa (ver `mde_vs_observado.md`, que muestra que el [6.67, 11.32] publicado es el IC de E|gap| invertido y no el del MDE).

### El cociente, estratificado (y por qué hay que estratificarlo)

`ventana_r2 = dentro` **es el conjunto completo de datos**: no es una elección de análisis, es el default. `fuera` es la ablación que el criterio R2 pre-registra como prueba de estrés. Contarlas coequales mezclaría medio jardín con media ablación, así que el cociente va partido:

| conjunto | celdas | p_dia < 0.05 | McNemar < 0.05 | ventaja mediana pp | rango pp |
|---|---|---|---|---|---|
| **datos completos** (`ventana_r2 = dentro`) | 96 | **0** | 59 | +10.8 | [+6.8, +15.4] |
| ablación R2 (`ventana_r2 = fuera`) | 96 | **0** | 0 | +3.9 | [-1.1, +8.8] |

**Sacar la ventana R2 cuesta caro en el punto estimado, y barato en filas.** Pareando cada camino consigo mismo con los otros seis ejes fijos, la ventaja cae una mediana de 7.14 pp (dispersión ENTRE CAMINOS [5.97, 8.61] — eso es variación de análisis, no error de muestreo) a cambio de perder 36 filas de 206 (18%). En **6 de 96** caminos pareados la ventaja se vuelve NEGATIVA al quitarla.

**Pero eso es el punto, no la inferencia, y el frente no puede aplicarse a sí mismo una vara distinta de la que exige.** Con el MISMO estimador de clúster que gobierna todo el informe, la caída del camino ancla es **+7.09 pp con IC95 [-1.25, +17.78]**, y el 6% de las réplicas da una caída nula o negativa. **El intervalo roza el cero.** Así que la lectura correcta no es «R2 dispara por efecto demostrado», sino: el punto estimado dice que seis fechas sostienen el signo del track record, y el diseño no tiene resolución ni para confirmar eso.

Y aun por la ruta publicada, las 59 celdas significativas **no están repartidas por la matriz**: todas y cada una comparten un mismo nivel en este eje:

- `ventana_r2` = **dentro** — cero celdas significativas con otro valor

> **Esto y la tabla de influencia de más abajo son el MISMO hecho, no dos.** Para un eje de dos niveles, si las K celdas significativas comparten un nivel, entonces cada una forma grupo con su gemela no significativa y el conteo de «cruces» es K por identidad algebraica. Se dice acá para que la tabla no se lea como una confirmación independiente.

**Lo que sobrevive en las 192 celdas** — las únicas afirmaciones que el proyecto puede hacer hoy sin condicionarlas a una elección de análisis:

1. El modelo acierta más del 50%
2. El IC95 Wilson del modelo excluye el 50%
3. El MAE del modelo es menor que el de predecir 0.0
4. (sólo objetivo `gap`) La cobertura del intervalo 80% supera su nominal
5. (sólo objetivo `gap`) El IC95 de la cobertura excluye el 80% nominal (intervalos demasiado anchos)

**Y hay que leer las de acierto con su control al lado, porque solas engañan.** Hablan de superar una moneda, no de superar a la baseline. La baseline constante «siempre al alza» acierta también más del 50% en el 100.0% de las celdas: «acertar más de la mitad» describe sobre todo la ventana —un mercado que subió—, y el modelo lo hace con más holgura, que es una afirmación real pero mucho más chica que la publicada.

**La MAGNITUD merece su propio párrafo, porque es donde el modelo estuvo más cerca.** El campeón le gana a predecir 0.0 en punto estimado en **192 de 192** celdas (ΔMAE del ancla -0.455 pp, IC de clúster [-0.989, 0.041]). Pero con intervalo pareado y cluster-honesto excluye el cero en sólo **0 de 192**; por la ruta de bloques de filas —la que supone independencia— serían **120**. La misma brecha que en dirección, por la misma razón. **Robusto no es.**

**No sobrevive NINGUNA afirmación sobre la ventaja del modelo respecto de su baseline a las 192 celdas: ni direccional ni de magnitud, ni significativa ni con intervalo que excluya el cero, ni siquiera —en dirección— positiva en todas.** Lo único que sobrevive el modelo lo comparte con una constante o lo hereda de sus intervalos deliberadamente anchos. **Ese es el titular.**

Y, por contraste, **lo que NO sobrevive**: todo lo demás de la tabla de abajo, empezando por el veredicto de significancia — y por el signo mismo, que sólo es positivo en el 94.8% de las celdas.

---

## Qué es esto y qué no

Gelman y Loken (2013) describen el *garden of forking paths*: un analista honesto, que no está buscando un p pequeño, toma igual decenas de decisiones razonables —qué filas cuentan, cómo se puntúa un empate, qué ventana se excluye, cuándo se mira— y cada una podría haber sido otra. El p que publica es condicional a ese camino, pero se lee como si fuera incondicional. No hace falta mala fe: basta con no medir la dispersión.

Este proyecto tiene el material para medirla, porque documentó cada elección en su sitio. Lo que faltaba era el conteo. Esto **no es un análisis nuevo del modelo** ni un reproche a las decisiones: ninguna celda es «la buena», ninguna reemplaza a la publicada, y el resultado es la DISPERSIÓN, no un valor central.

La matriz tiene 192 caminos y 192 son computables. **Los ejes no son ortogonales y no se pretende que lo sean** — la regla de deduplicación y `filas_29jul` se tocan sobre las mismas fechas, `emision_parcial` toca tres de las cinco fechas de pares. Un producto cartesiano leído como si fueran caminos independientes sobrestimaría el tamaño del jardín; por eso el resultado se reporta como cociente y rango, y la tabla de influencia mide cada eje **con los demás fijos**, que es la lectura que el solapamiento no rompe.

**Reglas de la casa aplicadas.** Ningún estimador puntual sin intervalo: las tasas llevan Wilson; la ventaja, el MAE y su diferencia pareada, bootstrap de CLÚSTERES DE DÍA con semilla fija; la cobertura, Wilson. Y —DECISIONES.md §52— *una verificación que usa el mismo mecanismo que produjo la cifra no es una verificación*: el estimador principal sale del módulo de la skill `estadistica-evaluacion` (binomial exacta), no de `backtest/linea_base.py` (chi2 con corrección de continuidad), que es la ruta de lo publicado. Las dos se reportan.

### Las dos rutas de McNemar, comparadas

| Ruta | Implementación | Celdas con p < 0.05 |
|---|---|---|
| Binomial exacta (**la que se usa**) | `evaluacion.mcnemar_exact` | **59 / 192** |
| chi2 con corrección de continuidad (la publicada) | `backtest.linea_base.mcnemar` | 59 / 192 |

Diferencia media |p_exacto − p_chi2| = 0.0003; máxima 0.0005. Discrepan en el veredicto en 0 celdas de 192. La elección de ruta importa poco; se reporta igual, porque no declararla sería un eje más escondido.

### La vara independiente

DECISIONES.md §52: *una verificación que usa el mismo mecanismo que produjo la cifra no es una verificación*. Las dos cifras que sostienen este informe —el ancla y el colapso al sacar la ventana R2— se recalculan por una ruta con **su propia consulta, su propia selección de filas y su propia aritmética**, sin `cargar()`, sin `aplicar()` y sin `metricas()`. Lo único que comparte es `_conexion_ro`, que abre el archivo en solo lectura: el invariante de aislamiento del proyecto prohíbe que nada en `GEMELO/` abra `senales.db` por su cuenta, y abrir el archivo no es parte del mecanismo que produjo la cifra.

| cifra | n | modelo_pct | base_pct | ventaja_pp | b | c | p_exacto |
|---|---|---|---|---|---|---|---|
| ancla | 248 | 66.1 | 59.7 | 6.5 | 72 | 56 | 0.1847 |
| ancla_regla | 238 | 67.6 | 58.0 | 9.7 | 72 | 49 | 0.0451 |
| sin_ventana_r2 | 204 | 62.7 | 63.7 | -1.0 | 48 | 50 | 0.9196 |

Coincide con la matriz y con el README en el ancla, y el colapso sin la ventana R2 (-1.0 pp, p = 0.9196) reproduce lo que el criterio R2 del pre-registro ya afirmaba del propio campeón.

---

## Los ejes

Un eje entra si cambia el CONJUNTO DE FILAS o el PUNTAJE, y sólo si es una elección documentada entre alternativas.

### 1. `dedup` — RETIRADO: dejó de ser un eje y pasó a ser una regla

El 1-sep-2026 Nicolás **firmó** la regla de deduplicación: *«la fila válida es la que tiene la sesión objetivo correcta según `available_at`, no la más reciente. El criterio es la corrección de la sesión, nunca la frescura»*, con `keep="last"` explícitamente **prohibida** porque el forense demostró que retira selectivamente errores del modelo. Un eje mide una elección viva; una regla firmada no lo es. La regla vive en `backtest.linea_base.deduplicar_por_sesion` y entra a esta matriz por la carga.

**Consecuencia declarada: la matriz pasó de 768 celdas a 192.** El veredicto se recomputó sobre las nuevas en vez de suponerse que no cambiaba.

La regla se implementa sola y **no lleva ninguna lista de fechas cableada** —una lista sería la regla escondiendo su propio criterio—: conservar la fila cuya `sesion_objetivo` coincide con `calendarios.proxima_sesion_despues_de(exchange, available_at)` separa por construcción los dos grupos del forense. En los 10 pares del defecto de reloj (31-jul, 5-ago) sólo una fila calza y la otra se retira; en los 5 de feriado real (12-ago, 18-ago) calzan las dos y no se descarta nada.

**La diferencia sustantiva con `keep="last"`, y hay que poder ver las dos cosas juntas.** El retiro NO es por frescura sino por no-correspondencia demostrable: esas 10 filas usan el cierre del SOX de `available_at` para puntuarse contra una sesión que está una sesión más allá, así que su `gap_pct` no es el gap que su insumo podía predecir. Es una justificación real y distinta. **Pero el efecto sobre el conteo tiene el mismo signo:** b queda en 72 sin cambio y c baja de 56 a 49 — de las 10 filas retiradas, 7 eran discordantes y **las 7 favorecían a la baseline; ninguna al modelo**. Es la misma asimetría que motivó prohibir la otra rama, y el lector tiene que poder juzgar las dos cosas a la vez.

**La opción que NO se puede tomar, y por qué.** Lo más completo sería **re-verificar** esas 10 filas contra su sesión objetivo correcta en vez de descartarlas. Eso exige recomputar valores sellados, y las filas selladas no se reescriben nunca (Constitución 5.0, punto 3). **Descartarlas se eligió por restricción, no por preferencia**, y conviene decirlo así.

**Lo que la regla NO cubre, y es una pregunta abierta.** Es una regla de DEDUPLICACIÓN: sólo arbitra entre filas que compiten. Recomputando la sesión sobre TODAS las filas —no sólo las duplicadas— hay **25 que no calzan**, y **15 de ellas no tienen pareja** (7 del 5-ago que apuntan a 08-07 debiendo apuntar a 08-06; 8 del 5-jul que apuntan a 07-06 debiendo apuntar a 07-03). La firma no las previó porque nadie sabía que existían, y descartarlas sin reemplazo es una operación distinta de la que se firmó. Quedan **dentro**, y la pregunta está abierta en `GEMELO/resultados/cola_decisiones.md`.

### 2. `empate` — convención de empate

- **Niveles:** `estricta` · `verificador` · `excluir_cero`
- **Cita:** backtest/linea_base.py, cabecera; DECISIONES.md §25.1 (línea 2149); congelada en `excluir_cero` por GEMELO/DISEÑO.md §2.8

El verificador puntúa al campeón con `>=` y la baseline de la §2.1 usaba `>`: dos reglas para los dos lados. `gap == 0.00` exacto es la firma del ffill de feriados (Supuesto #1); 4 de las 5 filas son 2330.TW. **Alcance declarado:** esa justificación documenta el objetivo `gap`. Bajo `objetivo = retorno_sesion` el nivel `excluir_cero` descarta las filas con `retorno_real_pct == 0` —otras 4 filas, otro fenómeno— sin acta que lo respalde; el eje se aplica igual por simetría, y se dice.

### 3. `ventana_r2` — bloque 15-23 jul 2026

- **Niveles:** `dentro` · `fuera`
- **Cita:** GEMELO/DISEÑO.md §6.2 (criterio R2); DECISIONES.md §25.2 (líneas 2188-2195); backtest/linea_base.py:VENTANA_R2

R2 descarta a un retador si su ventaja desaparece al excluir esa ventana. Se operacionaliza por RANGO DE FECHAS y no por índice de bloque porque el reparto interno de los bloques publicados NO REPRODUCE: se probaron cuatro órdenes de fila y ninguno lo da.

### 4. `filas_29jul` — las 8 filas del 29-jul

- **Niveles:** `dentro` · `fuera`
- **Cita:** DECISIONES.md §33.8 (líneas 2963-2973); Etapa 5.0.2 §4 (líneas 1011-1025 y tabla 1240-1247)

Pregunta abierta y explícitamente **no decidida**: «si las 8 filas del 29-jul (sesión saltada) deben seguir en las métricas — que es la decisión de abstención pendiente desde la 5.0.2». Mientras no se decida, están dentro por omisión, que es una elección tanto como sacarlas. De las 8, sólo 7 saltaron sesión (0/7 en gap); IFX.DE conservó su objetivo natural y acertó. El eje quita las 8, que es lo que la pregunta dice literalmente.

### 5. `emision_parcial` — fechas con emisión parcial

- **Niveles:** `dentro` · `fuera`
- **Cita:** **Hallazgo de este frente**, medido sobre `senales_ticker`; precedente en la errata de descarga (DECISIONES.md líneas 664-686 y 1113-1119)

Cinco fechas emitieron menos de las 8 predicciones de apertura habituales porque la descarga no trajo todos los tickers. La composición de esos días no es aleatoria: es la que el proveedor entregó. La errata de julio afirma que «el costo fue de COBERTURA, no de veracidad»; este eje es precisamente la prueba de esa afirmación. Tres de las cinco fechas son además fechas de pares duplicados, así que este eje y la regla de deduplicación se tocan — a propósito y a la vista.

### 6. `corte` — corte de sello

- **Niveles:** `publicado` (2026-08-28, la ventana del README) · `vivo` (toda la base)
- **Cita:** backtest/linea_base.py:CORTE_SECCION_2; DECISIONES.md §34.10 (líneas 3184-3196) y §47 (líneas 4163-4171)

El track record crece: contrastar una cifra congelada contra una base viva compara numerador fijo con denominador móvil. El proyecto se pisó con esto dos veces (WS5 el 30-ago; cuarto dictamen el 31-ago). Y ya lleva SIETE valores de n publicados (184, 223, 228, 240, 245, 248, 253) — hoy 261, el octavo. Elegir CUÁNDO mirar es una bifurcación, y el §47 ya la contabilizó como α ∈ [0.09, 0.18].

### 7. `objetivo` — cuál de los dos objetivos se puntúa

- **Niveles:** `gap` · `retorno_sesion`
- **Cita:** CLAUDE.md y senales.py («double objective»); DECISIONES.md §32.6 (líneas 2828-2832) y §37.6 (línea 3606)

El verificador sella los dos por predicción: `gap_pct` (¿existe la señal?) y `retorno_real_pct` (¿es capturable?), cada uno con su acierto y su error, en la MISMA fila. El proyecto publica los dos, pero el titular cita el gap — y §32.6 dice con todas sus letras que «el gap es precisamente lo que no se puede capturar». Elegir cuál se titula es una bifurcación.

### 8. `zona_muerta` — abstenerse bajo un umbral de |predicción|

- **Niveles:** `0.00` (sin zona muerta) · `0.25` (el umbral publicado)
- **Cita:** backtest/linea_base.py:UMBRALES_ZONA_MUERTA; GEMELO/DISEÑO.md §2.4; DECISIONES.md línea 2138

La §2.4 publica seis umbrales y cita el de 0.25 con n=184 y +8.2 pp. **Esa cifra NO reproduce bajo el corte de esta matriz** —con el resto del ancla, `zona_muerta=0.25` deja n≈197— porque salió de otro corte de sello y otra convención de empate; se cita como contexto del eje, no como reproducción. Cada nivel se compara contra SU PROPIA baseline sobre las filas que sobreviven — comparar contra la global cambiaría el denominador y regalaría ventaja. Se toman dos niveles: ninguno y el publicado.

### La evidencia del eje retirado, computada

Los 15 pares que apuntan a la misma sesión objetivo, **antes** de aplicar la regla (corte `2026-08-28`). `aciertos_gap` cuenta sobre el total de `filas`: donde vale la mitad, las dos emisiones del par predijeron signos opuestos sobre un gap idéntico. La regla firmada retira una fila de cada uno de los 10 pares de 31-jul y 5-ago, y no toca los 5 de 12-ago y 18-ago.

| sesion_objetivo | pares | filas | emitidas_en | aciertos_gap |
|---|---|---|---|---|
| 2026-07-31 | 7 | 14 | 2026-07-29 y 2026-07-30 | 7 |
| 2026-08-05 | 3 | 6 | 2026-08-03 y 2026-08-04 | 6 |
| 2026-08-12 | 4 | 8 | 2026-08-10 y 2026-08-11 | 4 |
| 2026-08-18 | 1 | 2 | 2026-08-14 y 2026-08-17 | 1 |

### La evidencia del eje 5, computada

| fecha | emitidas | tickers |
|---|---|---|
| 2026-07-13 | 4 | 2330.TW, 4063.T, 6857.T, IFX.DE |
| 2026-07-21 | 6 | 000660.KS, 005930.KS, 3436.T, 4063.T, 6857.T, 8035.T |
| 2026-08-03 | 4 | 2330.TW, 3436.T, 4063.T, IFX.DE |
| 2026-08-12 | 5 | 005930.KS, 3436.T, 4063.T, 8035.T, IFX.DE |
| 2026-08-17 | 4 | 005930.KS, 3436.T, 8035.T, IFX.DE |


### Orden de aplicación (declarado, porque importa)

1. `corte` (en la carga)
2. `objetivo`: elige el par (acierto, valor real, error) sellado
3. filtros de filas: `ventana_r2`, `filas_29jul`, `emision_parcial`, `zona_muerta`
4. `empate` (puntaje, y descarte si `excluir_cero`)

Deduplicar DESPUÉS de filtrar es deliberado: si el 29-jul sale, la sesión del 31-jul se queda con la fila del 30-jul y `first` y `last` coinciden. Ese enredo entre ejes es real; la matriz debe mostrarlo, no esconderlo invirtiendo el orden.

---

## Candidatos que NO son ejes, y por qué

Declarar un eje descartado importa tanto como incluirlo: un eje omitido en silencio es exactamente el grado de libertad que Gelman y Loken describen. Cada descarte va con su cita y con su medición, no con una afirmación.

| candidato | cita | por qué no |
|---|---|---|
| regla de deduplicación | La firma de Nicolás del 1-sep-2026 (acta en DECISIONES.md); el forense en GEMELO/resultados/dedup_opciones.md; la implementación en backtest/linea_base.py:deduplicar_por_sesion | **YA NO ES UN EJE: es una regla FIRMADA.** «La fila válida es la que tiene la sesión objetivo correcta según `available_at`, no la más reciente; el criterio es la corrección de la sesión, nunca la frescura», con `keep="last"` PROHIBIDA. Se aplica en la carga, así que la matriz pasó de 768 celdas a 192. Lo que la regla NO cubre —15 filas sin pareja que tampoco calzan— queda dentro y abierto en `cola_decisiones.md`. |
| residualización sí/no | CLAUDE.md y motor.py: `divergencias_al` residualiza contra índice local + FX por defecto, «simple spread kept for comparison»; DECISIONES.md líneas 1384-1391 y §30.2 (línea 2568) | NO ES UN EJE DE ESTA MATRIZ. Las divergencias residualizadas alimentan `z_divergencia` y de ahí las baselines B3-B5; NO entran a `prediccion_apertura_al`, que es β·SOX. Aunque entraran, variarlas exigiría re-emitir, y las filas selladas no se reescriben (Constitución 5.0, punto 3). |
| ventana de betas (120 sesiones) | CLAUDE.md y motor.py: `betas_al` «rolling window, default 120 trading days», sellada en `snapshots.ventana_betas`; DECISIONES.md §32.2 (línea 2760) | NO COMPUTABLE sobre filas selladas: está horneada dentro de `apertura_estimada_pct`. Verificado abajo que toma UN SOLO valor en toda la ventana, así que ni siquiera hay variación histórica que explotar. Sí es un eje para la ventana larga reconstruida. |
| ffill de feriados (Supuesto #1) | CLAUDE.md, «Data conventions»; DECISIONES.md §25.1 (línea 2149) | YA ESTÁ EN LA MATRIZ, dentro del eje `empate`: el ffill es la CAUSA de `gap_pct == 0.00` y toda la bifurcación vive en cómo se puntúan esas filas. No se cuenta dos veces. |
| estado `sin_datos_mercado` | CLAUDE.md, extras sellados 5.0; senales.py: «nunca entra a `verificacion_apertura`»; DECISIONES.md líneas 712-721 | NO ES UN EJE: esas filas no llegan al conjunto que la matriz mide. El umbral que las produce (5 sesiones del calendario real) es una elección documentada, pero gobierna la EMISIÓN, no la medición. Conteo verificado abajo. |
| estado `no_verificable_timing` | CLAUDE.md, LA REGLA MAESTRA (Etapa 4.6): «kept for audit, excluded from ALL metrics»; DECISIONES.md líneas 1011-1013 | NO ES UN EJE, y hoy además está VACÍO: cero filas lo llevan. En particular el 29-jul no produjo ninguna, así que filtrar por ese estado no quita nada. Y la regla maestra no es una elección de análisis sino una restricción. |
| tickers con `duplicado_de` (TSM → 2330.TW) | universo.py: «TSM counts once via 2330.TW»; DECISIONES.md líneas 167-174 | NO ES UN EJE en este conjunto: TSM no emite predicción de apertura y no aparece en ninguna fila verificada. Verificado abajo. |
| MINIMO_OBSERVACIONES | senales.py: `calibracion_intervalos()` devuelve «pendiente» por debajo del umbral | NO ES UN EJE: es un umbral de PRESENTACIÓN (decide si se MUESTRA la cobertura, no qué filas la componen), y toda ventana de esta matriz lo supera con holgura. La cobertura se computa igual en cada celda y se reporta con su Wilson, que dice lo mismo sin ocultar. |
| filas canónicas en días de solapamiento titular/sombra | docs/SOMBRA.md; DECISIONES.md §36.1 (líneas 3382-3385) y §36.7 (líneas 3491-3494) | YA DECIDIDO Y APLICADO, no abierto: «fecha <= 2026-08-25 → canónico el MAC; fecha >= 2026-08-26 → canónico el PC». Movió n de 245 a 253 y la ventaja de +6.7 a +6.5 pp. La base local ya está en su forma canónica y tiene UNA sola fila por (fecha, ticker) —verificado abajo—, así que no queda bifurcación DENTRO de esta base. |
| desglose por bolsa / región | DECISIONES.md §33.2 (líneas 2885-2895), §34.2 (líneas 3012-3015), §47 (líneas 4176-4181) | DELIBERADAMENTE FUERA. Es un desglose de SUBGRUPOS, no una bifurcación de la cifra titular, y el propio proyecto ya registró que esas miradas produjeron falsos positivos retractados (Tokio p=0.021, Seúl p=0.031, «ninguno sobrevive Bonferroni ×8») y que «si alguna decisión se tomara mirándolo, N sube a 31 y hay que decirlo». Meterlos aquí fabricaría significancia, que es el pecado que esta matriz mide. |
| regla de abstención por sello tardío, alcance completo (17 filas) | DECISIONES.md, Etapa 5.0.2 §4 (líneas 1225-1247): 29-jul 7 · 03-ago 3 · 05-ago 7, «4/17 (23.5%)» contra «15/15» de las frescas | PARCIALMENTE COMPUTADO. Las 15 filas rancias que TIENEN pareja fresca son exactamente las que retira la regla firmada, así que ya las cubre. Las de 05-ago no tienen pareja («no hubo, hueco del 06») y no se pueden identificar desde columnas selladas. Se intentó reconstruirlas comparando `sesion_objetivo` contra `calendarios.proxima_sesion_despues_de` a la hora nominal de sello: NO REPRODUCE (difiere en las 261 filas), así que se descarta en vez de publicar una identificación que no se sostiene. |

**Comprobaciones que sostienen la tabla:**

- Estados en `senales_ticker`: {'(NULL)': 618, 'verificada': 261, 'legacy_pre_4.6': 22, 'pendiente': 16, 'sin_datos_mercado': 2}
- Filas `sin_datos_mercado`: **2** — ninguna llega a `verificacion_apertura` con gap.
- Filas `no_verificable_timing`: **0** — el estado existe y hoy está vacío.
- Filas `legacy_pre_4.6`: **22** — excluidas por `cargar()` vía `legacy = 0` y `modelo_version`.
- TSM (`duplicado_de` 2330.TW) en filas verificadas: **0**; predicciones de apertura que emite TSM: **0**.
- `snapshots.ventana_betas` toma los valores [120.0] en toda la ventana: no hay variación histórica que explotar aunque se quisiera.
- Duplicados exactos de (fecha, ticker) en `senales_ticker`: **0** — la base local ya está en su forma canónica, así que el solapamiento titular/sombra no es una bifurcación DENTRO de esta base.

---

## Qué eje mueve el veredicto

Para cada eje, manteniendo **todos los demás fijos**, cuánto se mueve la métrica al recorrer sólo los niveles de ese eje. `rango_ventaja_pp` es la media (sobre los grupos de los otros ejes) del máximo menos el mínimo dentro del grupo, y es lo que ordena la tabla. `cruza_p_dia` cuenta los grupos en que ese eje por sí solo hace cruzar α = 0.05 con inferencia de clúster: es **cero en todos los ejes**, y ese cero no es un empate — es el veredicto del frente otra vez. `cruza_mcnemar` es el mismo conteo por la ruta publicada, y ahí sí se separa.

| eje | niveles | rango_ventaja_pp | rango_ventaja_max_pp | rango_p | rango_p_max | grupos | cruza_p_dia | cruza_mcnemar |
|---|---|---|---|---|---|---|---|---|
| ventana_r2 | 2 | 7.28 | 8.61 | 0.46 | 0.62 | 96 | 0 | 59 |
| zona_muerta | 2 | 4.77 | 6.41 | 0.24 | 0.49 | 96 | 0 | 33 |
| empate | 3 | 1.79 | 2.72 | 0.11 | 0.27 | 64 | 0 | 11 |
| objetivo | 2 | 1.65 | 4.26 | 0.09 | 0.29 | 96 | 0 | 13 |
| emision_parcial | 2 | 1.61 | 2.47 | 0.08 | 0.19 | 96 | 0 | 13 |
| filas_29jul | 2 | 0.54 | 0.78 | 0.03 | 0.09 | 96 | 0 | 7 |
| corte | 2 | 0.27 | 0.57 | 0.01 | 0.05 | 96 | 0 | 1 |


### Dónde viven las celdas significativas

Nivel por nivel: de las celdas que contienen ese nivel, cuántas dan p < 0.05. Un nivel que concentra el 0% y su alternativa que concentra todo no es un matiz — es el veredicto entero colgando de esa elección.

| eje | nivel | celdas | p_dia<0.05 | McNemar<0.05 | ventaja mediana pp | ventaja min pp | ventaja max pp |
|---|---|---|---|---|---|---|---|
| empate | estricta | 64 | 0 | 25 | 8.7 | 1.5 | 15.4 |
| empate | verificador | 64 | 0 | 14 | 7.1 | -1.1 | 14.9 |
| empate | excluir_cero | 64 | 0 | 20 | 8.0 | 0.0 | 15.0 |
| ventana_r2 | dentro | 96 | 0 | 59 | 10.8 | 6.8 | 15.4 |
| ventana_r2 | fuera | 96 | 0 | 0 | 3.9 | -1.1 | 8.8 |
| filas_29jul | dentro | 96 | 0 | 28 | 7.9 | -0.5 | 15.4 |
| filas_29jul | fuera | 96 | 0 | 31 | 7.8 | -1.1 | 15.3 |
| emision_parcial | dentro | 96 | 0 | 29 | 7.9 | -0.5 | 15.4 |
| emision_parcial | fuera | 96 | 0 | 30 | 7.9 | -1.1 | 15.3 |
| corte | publicado | 96 | 0 | 29 | 7.9 | -1.1 | 15.4 |
| corte | vivo | 96 | 0 | 30 | 7.6 | -1.0 | 15.3 |
| objetivo | gap | 96 | 0 | 30 | 7.9 | -1.1 | 15.4 |
| objetivo | retorno_sesion | 96 | 0 | 29 | 7.9 | -0.5 | 15.3 |
| zona_muerta | 0.0 | 96 | 0 | 13 | 5.4 | -1.1 | 10.9 |
| zona_muerta | 0.25 | 96 | 0 | 46 | 9.5 | 3.8 | 15.4 |


---

## Qué sobrevive en TODAS las celdas

Cada fila es una afirmación que el proyecto podría querer hacer. Sobrevive sólo la que se cumple en el 100% de las celdas; cualquier otra hay que condicionarla, en voz alta, a la elección de análisis que la sostiene.

| afirmación | celdas | % | sobrevive |
|---|---|---|---|
| La ventaja sobre «siempre al alza» es positiva | 182/192 | 94.8 | no |
| La ventaja es significativa con inferencia de clúster de día (p_dia < 0.05) | 0/192 | 0.0 | no |
| La ventaja es significativa por McNemar, que supone filas independientes | 59/192 | 30.7 | no |
| El IC95 de la ventaja (clúster de día) excluye el cero | 0/192 | 0.0 | no |
| Los IC95 Wilson del modelo y de la baseline se solapan | 173/192 | 90.1 | no |
| El modelo acierta más del 50% | 192/192 | 100.0 | SÍ |
| El IC95 Wilson del modelo excluye el 50% | 192/192 | 100.0 | SÍ |
| (control) La baseline «siempre al alza» acierta más del 50% | 192/192 | 100.0 | SÍ |
| (control) El IC95 Wilson de la baseline excluye el 50% | 122/192 | 63.5 | no |
| El MAE del modelo es menor que el de predecir 0.0 | 192/192 | 100.0 | SÍ |
| El IC95 PAREADO de ΔMAE excluye el cero (clúster de día) | 0/192 | 0.0 | no |
| El IC95 PAREADO de ΔMAE excluye el cero (bloques de filas, la ruta que supone independencia) | 120/192 | 62.5 | no |
| (sólo objetivo `gap`) La cobertura del intervalo 80% supera su nominal | 96/96 | 100.0 | SÍ |
| (sólo objetivo `gap`) La cobertura cae en la banda [76%, 84%] que exige V3 | 0/96 | 0.0 | no |
| (sólo objetivo `gap`) El IC95 de la cobertura excluye el 80% nominal (intervalos demasiado anchos) | 96/96 | 100.0 | SÍ |


---

## La matriz completa

192 celdas, ordenadas por `p_dia`. `p_dia` es la permutación de signo por día (4000 permutaciones) y es el estimador titular; `p_exacto` y `p_chi2` son las rutas de McNemar, que suponen filas independientes. `ventaja_*`, `mae*` y `dmae*` llevan IC por bootstrap de CLÚSTERES DE DÍA (10000 réplicas, semilla 0); las tasas llevan Wilson. `dmae` es la diferencia PAREADA entre el MAE del modelo y el de predecir 0.0 — que es la comparación válida: las dos series se miden sobre las mismas filas y están muy correlacionadas, así que enfrentar dos IC no pareados no prueba nada.

> **Los días por celda van de 20 a 35** (mediana 27), y el día es la unidad muestral del estimador titular: el piso de 30 filas está en la unidad equivocada y se declara como tal. Ninguna celda quedó por debajo de 20 días, pero eso salió así, no se impuso.

> **`ventaja_lo > 0` y `p_dia < 0.05` no son duales** y pueden discrepar: el primero es un percentil de bootstrap y el segundo una permutación de signo. En esta matriz discrepan en 0 celda(s). Se listan las dos filas en la tabla de supervivientes porque miden cosas parecidas, no la misma.

> **Wilson supone filas independientes y aquí no lo son**, así que `modelo_lo/hi` y `base_lo/hi` son OPTIMISTAS. Se conservan porque son la convención publicada y hacen falta para comparar; lo que decide el veredicto va por clúster de día.

> **Sobre la cobertura bajo `objetivo = retorno_sesion`.** El intervalo del 80% se construyó para el GAP. Medir su cobertura contra el retorno de sesión responde «¿está calibrado para el objetivo capturable?», que es una pregunta legítima y distinta; no es la cobertura publicada y no debe citarse como tal.

| empate | ventana_r2 | filas_29jul | emision_parcial | corte | objetivo | zona_muerta | n | dias | modelo_pct | modelo_lo | modelo_hi | base_pct | base_lo | base_hi | ventaja_pp | ventaja_lo | ventaja_hi | p_dia | b | c | p_exacto | p_chi2 | mae | mae_lo | mae_hi | mae_cero | mae_cero_lo | mae_cero_hi | dmae | dmae_lo | dmae_hi | dmae_bloque_lo | dmae_bloque_hi | n_cobertura | cobertura_pct | cobertura_lo | cobertura_hi | cobertura_dia_lo | cobertura_dia_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| estricta | dentro | dentro | dentro | vivo | gap | 0.25 | 195 | 31 | 71.28 | 64.57 | 77.17 | 56.41 | 49.39 | 63.18 | 14.87 | -2.21 | 32.63 | 0.1205 | 66 | 37 | 0.0055 | 0.0058 | 2.60 | 1.95 | 3.46 | 3.15 | 2.26 | 4.37 | -0.55 | -1.19 | 0.07 | -1.23 | -0.23 | 195 | 91.79 | 87.09 | 94.89 | 83.18 | 97.91 |
| estricta | dentro | dentro | dentro | publicado | gap | 0.25 | 188 | 30 | 71.81 | 64.99 | 77.75 | 56.38 | 49.24 | 63.27 | 15.43 | -2.16 | 33.85 | 0.1262 | 66 | 37 | 0.0055 | 0.0058 | 2.64 | 1.96 | 3.50 | 3.20 | 2.30 | 4.43 | -0.57 | -1.20 | 0.07 | -1.27 | -0.24 | 188 | 91.49 | 86.62 | 94.69 | 82.97 | 97.86 |
| estricta | dentro | fuera | dentro | publicado | gap | 0.25 | 187 | 29 | 71.66 | 64.81 | 77.63 | 56.68 | 49.52 | 63.58 | 14.97 | -2.72 | 34.02 | 0.1295 | 65 | 37 | 0.0072 | 0.0075 | 2.65 | 1.98 | 3.53 | 3.22 | 2.32 | 4.46 | -0.57 | -1.21 | 0.06 | -1.27 | -0.24 | 187 | 91.44 | 86.55 | 94.66 | 82.70 | 97.85 |
| estricta | dentro | fuera | dentro | vivo | gap | 0.25 | 194 | 30 | 71.13 | 64.40 | 77.05 | 56.70 | 49.67 | 63.48 | 14.43 | -2.51 | 32.46 | 0.1315 | 65 | 37 | 0.0072 | 0.0075 | 2.61 | 1.95 | 3.47 | 3.16 | 2.27 | 4.35 | -0.55 | -1.17 | 0.07 | -1.23 | -0.23 | 194 | 91.75 | 87.02 | 94.86 | 83.25 | 97.91 |
| verificador | dentro | dentro | dentro | vivo | gap | 0.25 | 195 | 31 | 71.28 | 64.57 | 77.17 | 56.92 | 49.91 | 63.67 | 14.36 | -2.69 | 32.18 | 0.1350 | 65 | 37 | 0.0072 | 0.0075 | 2.60 | 1.95 | 3.46 | 3.15 | 2.26 | 4.37 | -0.55 | -1.19 | 0.07 | -1.23 | -0.23 | 195 | 91.79 | 87.09 | 94.89 | 83.18 | 97.91 |
| excluir_cero | dentro | dentro | dentro | vivo | gap | 0.25 | 194 | 31 | 71.13 | 64.40 | 77.05 | 56.70 | 49.67 | 63.48 | 14.43 | -2.69 | 32.31 | 0.1350 | 65 | 37 | 0.0072 | 0.0075 | 2.61 | 1.95 | 3.47 | 3.16 | 2.27 | 4.39 | -0.55 | -1.20 | 0.07 | -1.24 | -0.24 | 194 | 91.75 | 87.02 | 94.86 | 83.09 | 97.89 |
| verificador | dentro | dentro | dentro | publicado | gap | 0.25 | 188 | 30 | 71.81 | 64.99 | 77.75 | 56.91 | 49.77 | 63.79 | 14.89 | -2.67 | 33.33 | 0.1392 | 65 | 37 | 0.0072 | 0.0075 | 2.64 | 1.96 | 3.50 | 3.20 | 2.30 | 4.43 | -0.57 | -1.20 | 0.07 | -1.27 | -0.24 | 188 | 91.49 | 86.62 | 94.69 | 82.97 | 97.86 |
| excluir_cero | dentro | dentro | dentro | publicado | gap | 0.25 | 187 | 30 | 71.66 | 64.81 | 77.63 | 56.68 | 49.52 | 63.58 | 14.97 | -2.69 | 33.52 | 0.1392 | 65 | 37 | 0.0072 | 0.0075 | 2.65 | 1.97 | 3.51 | 3.22 | 2.31 | 4.45 | -0.58 | -1.22 | 0.07 | -1.27 | -0.24 | 187 | 91.44 | 86.55 | 94.66 | 82.84 | 97.84 |
| verificador | dentro | fuera | dentro | publicado | gap | 0.25 | 187 | 29 | 71.66 | 64.81 | 77.63 | 57.22 | 50.05 | 64.09 | 14.44 | -3.26 | 33.51 | 0.1442 | 64 | 37 | 0.0093 | 0.0097 | 2.65 | 1.98 | 3.53 | 3.22 | 2.32 | 4.46 | -0.57 | -1.21 | 0.06 | -1.27 | -0.24 | 187 | 91.44 | 86.55 | 94.66 | 82.70 | 97.85 |
| excluir_cero | dentro | fuera | dentro | publicado | gap | 0.25 | 186 | 29 | 71.51 | 64.63 | 77.51 | 56.99 | 49.80 | 63.89 | 14.52 | -3.28 | 33.69 | 0.1442 | 64 | 37 | 0.0093 | 0.0097 | 2.66 | 1.98 | 3.54 | 3.24 | 2.32 | 4.49 | -0.58 | -1.23 | 0.06 | -1.28 | -0.26 | 186 | 91.40 | 86.48 | 94.64 | 82.61 | 97.83 |
| verificador | dentro | fuera | dentro | vivo | gap | 0.25 | 194 | 30 | 71.13 | 64.40 | 77.05 | 57.22 | 50.18 | 63.97 | 13.92 | -3.03 | 31.98 | 0.1450 | 64 | 37 | 0.0093 | 0.0097 | 2.61 | 1.95 | 3.47 | 3.16 | 2.27 | 4.35 | -0.55 | -1.17 | 0.07 | -1.23 | -0.23 | 194 | 91.75 | 87.02 | 94.86 | 83.25 | 97.91 |
| excluir_cero | dentro | fuera | dentro | vivo | gap | 0.25 | 193 | 30 | 70.98 | 64.22 | 76.93 | 56.99 | 49.94 | 63.78 | 13.99 | -3.06 | 32.12 | 0.1450 | 64 | 37 | 0.0093 | 0.0097 | 2.62 | 1.95 | 3.49 | 3.18 | 2.28 | 4.38 | -0.56 | -1.19 | 0.07 | -1.24 | -0.24 | 193 | 91.71 | 86.96 | 94.83 | 83.16 | 97.88 |
| estricta | dentro | fuera | fuera | vivo | retorno_sesion | 0.25 | 177 | 26 | 71.19 | 64.12 | 77.35 | 55.93 | 48.57 | 63.04 | 15.25 | -4.30 | 35.06 | 0.1690 | 62 | 35 | 0.0080 | 0.0083 | 3.73 | 2.96 | 4.65 | 4.19 | 3.13 | 5.49 | -0.46 | -1.05 | 0.10 | -1.28 | 0.02 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | fuera | vivo | gap | 0.25 | 178 | 27 | 68.54 | 61.39 | 74.91 | 54.49 | 47.16 | 61.64 | 14.04 | -3.98 | 33.33 | 0.1737 | 62 | 37 | 0.0154 | 0.0159 | 2.72 | 2.01 | 3.65 | 3.17 | 2.23 | 4.52 | -0.45 | -1.11 | 0.19 | -1.20 | -0.11 | 178 | 91.01 | 85.90 | 94.39 | 81.72 | 97.74 |
| estricta | dentro | dentro | fuera | publicado | gap | 0.25 | 171 | 26 | 69.01 | 61.72 | 75.46 | 54.39 | 46.91 | 61.67 | 14.62 | -4.23 | 34.10 | 0.1790 | 62 | 37 | 0.0154 | 0.0159 | 2.76 | 2.03 | 3.70 | 3.23 | 2.25 | 4.57 | -0.47 | -1.16 | 0.20 | -1.23 | -0.12 | 171 | 90.64 | 85.34 | 94.16 | 81.25 | 97.56 |
| estricta | dentro | fuera | fuera | publicado | retorno_sesion | 0.25 | 170 | 25 | 71.18 | 63.96 | 77.46 | 55.88 | 48.37 | 63.13 | 15.29 | -4.88 | 35.72 | 0.1817 | 61 | 35 | 0.0103 | 0.0107 | 3.79 | 3.00 | 4.74 | 4.30 | 3.21 | 5.63 | -0.51 | -1.10 | 0.07 | -1.34 | -0.06 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | fuera | vivo | retorno_sesion | 0.25 | 178 | 27 | 70.79 | 63.72 | 76.97 | 56.18 | 48.84 | 63.26 | 14.61 | -4.85 | 34.55 | 0.1887 | 62 | 36 | 0.0112 | 0.0116 | 3.77 | 2.98 | 4.71 | 4.22 | 3.14 | 5.54 | -0.45 | -1.04 | 0.10 | -1.25 | 0.01 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | fuera | vivo | gap | 0.25 | 177 | 26 | 68.36 | 61.18 | 74.76 | 54.80 | 47.45 | 61.95 | 13.56 | -4.40 | 32.90 | 0.1932 | 61 | 37 | 0.0197 | 0.0202 | 2.73 | 2.02 | 3.66 | 3.19 | 2.25 | 4.54 | -0.46 | -1.16 | 0.19 | -1.20 | -0.12 | 177 | 90.96 | 85.82 | 94.36 | 81.61 | 97.71 |
| verificador | dentro | dentro | fuera | vivo | gap | 0.25 | 178 | 27 | 68.54 | 61.39 | 74.91 | 55.06 | 47.72 | 62.18 | 13.48 | -4.57 | 32.78 | 0.1942 | 61 | 37 | 0.0197 | 0.0202 | 2.72 | 2.01 | 3.65 | 3.17 | 2.23 | 4.52 | -0.45 | -1.11 | 0.19 | -1.20 | -0.11 | 178 | 91.01 | 85.90 | 94.39 | 81.72 | 97.74 |
| excluir_cero | dentro | dentro | fuera | vivo | gap | 0.25 | 177 | 27 | 68.36 | 61.18 | 74.76 | 54.80 | 47.45 | 61.95 | 13.56 | -4.60 | 32.95 | 0.1942 | 61 | 37 | 0.0197 | 0.0202 | 2.73 | 2.01 | 3.66 | 3.19 | 2.24 | 4.55 | -0.46 | -1.13 | 0.19 | -1.21 | -0.12 | 177 | 90.96 | 85.82 | 94.36 | 81.61 | 97.73 |
| excluir_cero | dentro | fuera | fuera | publicado | retorno_sesion | 0.25 | 167 | 25 | 71.86 | 64.60 | 78.13 | 56.89 | 49.30 | 64.16 | 14.97 | -5.49 | 35.63 | 0.1975 | 60 | 35 | 0.0134 | 0.0138 | 3.83 | 3.03 | 4.79 | 4.38 | 3.28 | 5.70 | -0.54 | -1.13 | 0.04 | -1.37 | -0.11 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | fuera | publicado | gap | 0.25 | 170 | 25 | 68.82 | 61.51 | 75.31 | 54.71 | 47.20 | 62.00 | 14.12 | -4.57 | 33.54 | 0.1975 | 61 | 37 | 0.0197 | 0.0202 | 2.77 | 2.03 | 3.73 | 3.25 | 2.28 | 4.65 | -0.48 | -1.17 | 0.19 | -1.24 | -0.13 | 170 | 90.59 | 85.26 | 94.12 | 80.81 | 97.59 |
| verificador | dentro | dentro | fuera | publicado | gap | 0.25 | 171 | 26 | 69.01 | 61.72 | 75.46 | 54.97 | 47.49 | 62.24 | 14.04 | -4.79 | 33.53 | 0.2012 | 61 | 37 | 0.0197 | 0.0202 | 2.76 | 2.03 | 3.70 | 3.23 | 2.25 | 4.57 | -0.47 | -1.16 | 0.20 | -1.23 | -0.12 | 171 | 90.64 | 85.34 | 94.16 | 81.25 | 97.56 |
| excluir_cero | dentro | dentro | fuera | publicado | gap | 0.25 | 170 | 26 | 68.82 | 61.51 | 75.31 | 54.71 | 47.20 | 62.00 | 14.12 | -4.82 | 33.73 | 0.2012 | 61 | 37 | 0.0197 | 0.0202 | 2.77 | 2.04 | 3.71 | 3.25 | 2.27 | 4.60 | -0.48 | -1.18 | 0.20 | -1.25 | -0.13 | 170 | 90.59 | 85.26 | 94.12 | 81.18 | 97.55 |
| excluir_cero | dentro | fuera | fuera | vivo | retorno_sesion | 0.25 | 173 | 26 | 71.68 | 64.55 | 77.86 | 57.23 | 49.77 | 64.36 | 14.45 | -5.56 | 34.52 | 0.2029 | 60 | 35 | 0.0134 | 0.0138 | 3.78 | 2.99 | 4.72 | 4.29 | 3.23 | 5.60 | -0.50 | -1.09 | 0.05 | -1.32 | -0.05 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | dentro | vivo | retorno_sesion | 0.25 | 194 | 30 | 67.53 | 60.65 | 73.72 | 54.64 | 47.61 | 61.49 | 12.89 | -5.10 | 31.68 | 0.2082 | 63 | 38 | 0.0165 | 0.0169 | 3.75 | 3.05 | 4.59 | 4.04 | 3.04 | 5.23 | -0.29 | -0.86 | 0.28 | -1.09 | 0.18 | 0 |  |  |  |  |  |
| verificador | dentro | fuera | fuera | vivo | gap | 0.25 | 177 | 26 | 68.36 | 61.18 | 74.76 | 55.37 | 48.01 | 62.50 | 12.99 | -4.97 | 32.34 | 0.2117 | 60 | 37 | 0.0250 | 0.0255 | 2.73 | 2.02 | 3.66 | 3.19 | 2.25 | 4.54 | -0.46 | -1.16 | 0.19 | -1.20 | -0.12 | 177 | 90.96 | 85.82 | 94.36 | 81.61 | 97.71 |
| excluir_cero | dentro | fuera | fuera | vivo | gap | 0.25 | 176 | 26 | 68.18 | 60.98 | 74.61 | 55.11 | 47.73 | 62.27 | 13.07 | -5.06 | 32.53 | 0.2117 | 60 | 37 | 0.0250 | 0.0255 | 2.74 | 2.02 | 3.68 | 3.21 | 2.26 | 4.57 | -0.47 | -1.17 | 0.19 | -1.22 | -0.12 | 176 | 90.91 | 85.74 | 94.33 | 81.50 | 97.69 |
| estricta | dentro | dentro | fuera | publicado | retorno_sesion | 0.25 | 171 | 26 | 70.76 | 63.55 | 77.06 | 56.14 | 48.65 | 63.36 | 14.62 | -5.62 | 35.71 | 0.2152 | 61 | 36 | 0.0144 | 0.0148 | 3.83 | 3.04 | 4.79 | 4.33 | 3.23 | 5.66 | -0.50 | -1.09 | 0.08 | -1.31 | -0.07 | 0 |  |  |  |  |  |
| verificador | dentro | fuera | fuera | publicado | gap | 0.25 | 170 | 25 | 68.82 | 61.51 | 75.31 | 55.29 | 47.79 | 62.57 | 13.53 | -5.20 | 33.14 | 0.2159 | 60 | 37 | 0.0250 | 0.0255 | 2.77 | 2.03 | 3.73 | 3.25 | 2.28 | 4.65 | -0.48 | -1.17 | 0.19 | -1.24 | -0.13 | 170 | 90.59 | 85.26 | 94.12 | 80.81 | 97.59 |
| excluir_cero | dentro | fuera | fuera | publicado | gap | 0.25 | 169 | 25 | 68.64 | 61.30 | 75.15 | 55.03 | 47.50 | 62.33 | 13.61 | -5.26 | 33.33 | 0.2159 | 60 | 37 | 0.0250 | 0.0255 | 2.78 | 2.04 | 3.74 | 3.27 | 2.29 | 4.68 | -0.49 | -1.18 | 0.18 | -1.26 | -0.13 | 169 | 90.53 | 85.18 | 94.09 | 80.70 | 97.56 |
| excluir_cero | dentro | dentro | fuera | vivo | retorno_sesion | 0.25 | 174 | 27 | 71.26 | 64.14 | 77.47 | 57.47 | 50.04 | 64.58 | 13.79 | -6.03 | 33.91 | 0.2209 | 60 | 36 | 0.0184 | 0.0189 | 3.82 | 3.02 | 4.77 | 4.31 | 3.24 | 5.65 | -0.50 | -1.08 | 0.06 | -1.30 | -0.05 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | dentro | vivo | retorno_sesion | 0.25 | 195 | 31 | 67.18 | 60.31 | 73.38 | 54.87 | 47.86 | 61.69 | 12.31 | -5.65 | 30.24 | 0.2239 | 63 | 39 | 0.0223 | 0.0228 | 3.78 | 3.09 | 4.64 | 4.07 | 3.08 | 5.29 | -0.29 | -0.87 | 0.29 | -1.06 | 0.17 | 0 |  |  |  |  |  |
| excluir_cero | dentro | dentro | fuera | publicado | retorno_sesion | 0.25 | 168 | 26 | 71.43 | 64.18 | 77.72 | 57.14 | 49.58 | 64.38 | 14.29 | -6.25 | 35.58 | 0.2334 | 60 | 36 | 0.0184 | 0.0189 | 3.87 | 3.07 | 4.84 | 4.40 | 3.31 | 5.75 | -0.54 | -1.13 | 0.05 | -1.34 | -0.12 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | dentro | publicado | gap | 0.00 | 243 | 34 | 67.49 | 61.37 | 73.07 | 56.79 | 50.50 | 62.87 | 10.70 | -5.91 | 27.24 | 0.2374 | 75 | 49 | 0.0244 | 0.0248 | 2.48 | 1.95 | 3.17 | 2.91 | 2.19 | 3.92 | -0.44 | -0.96 | 0.05 | -0.90 | -0.20 | 243 | 93.00 | 89.08 | 95.59 | 85.89 | 98.02 |
| estricta | dentro | fuera | dentro | publicado | retorno_sesion | 0.25 | 187 | 29 | 67.38 | 60.37 | 73.69 | 54.55 | 47.39 | 61.52 | 12.83 | -6.04 | 32.22 | 0.2377 | 62 | 38 | 0.0210 | 0.0214 | 3.81 | 3.09 | 4.66 | 4.14 | 3.11 | 5.36 | -0.33 | -0.93 | 0.26 | -1.15 | 0.15 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | dentro | vivo | gap | 0.00 | 251 | 35 | 66.93 | 60.90 | 72.46 | 56.57 | 50.39 | 62.56 | 10.36 | -5.84 | 26.97 | 0.2387 | 75 | 49 | 0.0244 | 0.0248 | 2.45 | 1.93 | 3.14 | 2.87 | 2.18 | 3.86 | -0.42 | -0.93 | 0.06 | -0.88 | -0.17 | 251 | 93.23 | 89.42 | 95.73 | 86.14 | 98.16 |
| verificador | dentro | fuera | fuera | publicado | retorno_sesion | 0.25 | 170 | 25 | 71.18 | 63.96 | 77.46 | 57.65 | 50.13 | 64.83 | 13.53 | -6.82 | 34.50 | 0.2502 | 60 | 37 | 0.0250 | 0.0255 | 3.79 | 3.00 | 4.74 | 4.30 | 3.21 | 5.63 | -0.51 | -1.10 | 0.07 | -1.34 | -0.06 | 0 |  |  |  |  |  |
| verificador | dentro | fuera | fuera | vivo | retorno_sesion | 0.25 | 177 | 26 | 71.19 | 64.12 | 77.35 | 58.19 | 50.83 | 65.21 | 12.99 | -6.78 | 33.15 | 0.2512 | 60 | 37 | 0.0250 | 0.0255 | 3.73 | 2.96 | 4.65 | 4.19 | 3.13 | 5.49 | -0.46 | -1.05 | 0.10 | -1.28 | 0.02 | 0 |  |  |  |  |  |
| excluir_cero | dentro | fuera | dentro | vivo | retorno_sesion | 0.25 | 190 | 30 | 67.89 | 60.96 | 74.12 | 55.79 | 48.68 | 62.67 | 12.11 | -6.38 | 31.18 | 0.2532 | 61 | 38 | 0.0265 | 0.0270 | 3.80 | 3.08 | 4.66 | 4.13 | 3.11 | 5.32 | -0.33 | -0.90 | 0.24 | -1.12 | 0.15 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | dentro | publicado | gap | 0.00 | 242 | 33 | 67.36 | 61.22 | 72.95 | 57.02 | 50.73 | 63.10 | 10.33 | -6.48 | 26.89 | 0.2559 | 74 | 49 | 0.0300 | 0.0305 | 2.48 | 1.97 | 3.19 | 2.93 | 2.22 | 3.96 | -0.44 | -0.96 | 0.05 | -0.90 | -0.21 | 242 | 92.98 | 89.04 | 95.57 | 85.71 | 98.02 |
| estricta | dentro | dentro | dentro | publicado | retorno_sesion | 0.25 | 188 | 30 | 67.02 | 60.02 | 73.34 | 54.79 | 47.65 | 61.73 | 12.23 | -6.32 | 31.41 | 0.2579 | 62 | 39 | 0.0281 | 0.0286 | 3.84 | 3.11 | 4.69 | 4.16 | 3.15 | 5.37 | -0.32 | -0.91 | 0.26 | -1.12 | 0.14 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | dentro | vivo | gap | 0.00 | 250 | 34 | 66.80 | 60.75 | 72.34 | 56.80 | 50.60 | 62.79 | 10.00 | -5.91 | 26.23 | 0.2584 | 74 | 49 | 0.0300 | 0.0305 | 2.45 | 1.94 | 3.14 | 2.88 | 2.19 | 3.87 | -0.42 | -0.93 | 0.05 | -0.89 | -0.18 | 250 | 93.20 | 89.38 | 95.71 | 86.23 | 98.11 |
| excluir_cero | dentro | fuera | dentro | publicado | retorno_sesion | 0.25 | 184 | 29 | 67.93 | 60.88 | 74.25 | 55.43 | 48.21 | 62.43 | 12.50 | -6.81 | 32.09 | 0.2592 | 61 | 38 | 0.0265 | 0.0270 | 3.84 | 3.11 | 4.71 | 4.20 | 3.17 | 5.43 | -0.36 | -0.95 | 0.23 | -1.18 | 0.12 | 0 |  |  |  |  |  |
| excluir_cero | dentro | dentro | dentro | vivo | retorno_sesion | 0.25 | 191 | 31 | 67.54 | 60.61 | 73.78 | 56.02 | 48.93 | 62.87 | 11.52 | -6.74 | 29.80 | 0.2594 | 61 | 39 | 0.0352 | 0.0357 | 3.83 | 3.13 | 4.70 | 4.15 | 3.15 | 5.39 | -0.33 | -0.91 | 0.25 | -1.10 | 0.13 | 0 |  |  |  |  |  |
| verificador | dentro | dentro | fuera | vivo | retorno_sesion | 0.25 | 178 | 27 | 70.79 | 63.72 | 76.97 | 58.43 | 51.08 | 65.41 | 12.36 | -7.45 | 32.77 | 0.2727 | 60 | 38 | 0.0334 | 0.0339 | 3.77 | 2.98 | 4.71 | 4.22 | 3.14 | 5.54 | -0.45 | -1.04 | 0.10 | -1.25 | 0.01 | 0 |  |  |  |  |  |
| excluir_cero | dentro | dentro | dentro | publicado | retorno_sesion | 0.25 | 185 | 30 | 67.57 | 60.52 | 73.90 | 55.68 | 48.47 | 62.65 | 11.89 | -6.91 | 31.32 | 0.2784 | 61 | 39 | 0.0352 | 0.0357 | 3.88 | 3.13 | 4.73 | 4.23 | 3.22 | 5.44 | -0.35 | -0.94 | 0.24 | -1.15 | 0.11 | 0 |  |  |  |  |  |
| verificador | dentro | dentro | fuera | publicado | retorno_sesion | 0.25 | 171 | 26 | 70.76 | 63.55 | 77.06 | 57.89 | 50.40 | 65.04 | 12.87 | -7.83 | 34.36 | 0.2837 | 60 | 38 | 0.0334 | 0.0339 | 3.83 | 3.04 | 4.79 | 4.33 | 3.23 | 5.66 | -0.50 | -1.09 | 0.08 | -1.31 | -0.07 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | fuera | vivo | retorno_sesion | 0.00 | 230 | 29 | 65.22 | 58.86 | 71.08 | 54.35 | 47.89 | 60.66 | 10.87 | -6.90 | 29.57 | 0.2872 | 71 | 46 | 0.0261 | 0.0265 | 3.35 | 2.70 | 4.15 | 3.70 | 2.82 | 4.81 | -0.35 | -0.82 | 0.07 | -0.93 | -0.02 | 0 |  |  |  |  |  |
| excluir_cero | dentro | dentro | dentro | publicado | gap | 0.00 | 238 | 34 | 67.65 | 61.46 | 73.27 | 57.98 | 51.63 | 64.08 | 9.66 | -7.17 | 26.55 | 0.2937 | 72 | 49 | 0.0451 | 0.0455 | 2.52 | 1.99 | 3.23 | 2.98 | 2.24 | 3.99 | -0.45 | -0.99 | 0.04 | -0.92 | -0.22 | 238 | 92.86 | 88.86 | 95.49 | 85.65 | 97.98 |
| excluir_cero | dentro | dentro | dentro | vivo | gap | 0.00 | 246 | 35 | 67.07 | 60.98 | 72.64 | 57.72 | 51.48 | 63.73 | 9.35 | -7.20 | 26.32 | 0.2967 | 72 | 49 | 0.0451 | 0.0455 | 2.49 | 1.96 | 3.19 | 2.93 | 2.22 | 3.93 | -0.44 | -0.96 | 0.06 | -0.90 | -0.19 | 246 | 93.09 | 89.21 | 95.64 | 85.84 | 98.12 |
| verificador | dentro | fuera | dentro | vivo | retorno_sesion | 0.25 | 194 | 30 | 67.53 | 60.65 | 73.72 | 56.70 | 49.67 | 63.48 | 10.82 | -7.50 | 30.00 | 0.2979 | 61 | 40 | 0.0460 | 0.0466 | 3.75 | 3.05 | 4.59 | 4.04 | 3.04 | 5.23 | -0.29 | -0.86 | 0.28 | -1.09 | 0.18 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | fuera | publicado | retorno_sesion | 0.00 | 222 | 28 | 65.32 | 58.84 | 71.27 | 54.50 | 47.93 | 60.92 | 10.81 | -7.59 | 29.91 | 0.3007 | 70 | 46 | 0.0323 | 0.0327 | 3.39 | 2.73 | 4.23 | 3.78 | 2.89 | 4.91 | -0.39 | -0.86 | 0.06 | -0.96 | -0.03 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | fuera | vivo | retorno_sesion | 0.00 | 231 | 30 | 64.94 | 58.58 | 70.80 | 54.55 | 48.10 | 60.84 | 10.39 | -6.93 | 28.81 | 0.3014 | 71 | 47 | 0.0338 | 0.0342 | 3.38 | 2.73 | 4.19 | 3.72 | 2.84 | 4.82 | -0.34 | -0.80 | 0.09 | -0.90 | -0.02 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | fuera | vivo | gap | 0.00 | 231 | 30 | 64.50 | 58.14 | 70.39 | 54.98 | 48.53 | 61.26 | 9.52 | -7.08 | 26.79 | 0.3074 | 71 | 49 | 0.0548 | 0.0552 | 2.53 | 1.98 | 3.27 | 2.87 | 2.14 | 3.95 | -0.35 | -0.88 | 0.15 | -0.86 | -0.08 | 231 | 92.64 | 88.53 | 95.35 | 84.98 | 97.90 |
| verificador | dentro | fuera | dentro | publicado | retorno_sesion | 0.25 | 187 | 29 | 67.38 | 60.37 | 73.69 | 56.15 | 48.98 | 63.07 | 11.23 | -7.81 | 30.98 | 0.3122 | 61 | 40 | 0.0460 | 0.0466 | 3.81 | 3.09 | 4.66 | 4.14 | 3.11 | 5.36 | -0.33 | -0.93 | 0.26 | -1.15 | 0.15 | 0 |  |  |  |  |  |
| verificador | dentro | dentro | dentro | vivo | retorno_sesion | 0.25 | 195 | 31 | 67.18 | 60.31 | 73.38 | 56.92 | 49.91 | 63.67 | 10.26 | -7.96 | 28.72 | 0.3142 | 61 | 41 | 0.0594 | 0.0599 | 3.78 | 3.09 | 4.64 | 4.07 | 3.08 | 5.29 | -0.29 | -0.87 | 0.29 | -1.06 | 0.17 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | dentro | vivo | retorno_sesion | 0.00 | 250 | 34 | 62.40 | 56.25 | 68.17 | 53.20 | 47.01 | 59.29 | 9.20 | -7.38 | 26.12 | 0.3182 | 72 | 49 | 0.0451 | 0.0455 | 3.40 | 2.78 | 4.14 | 3.62 | 2.79 | 4.66 | -0.22 | -0.69 | 0.22 | -0.77 | 0.12 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | fuera | publicado | gap | 0.00 | 223 | 29 | 65.02 | 58.56 | 70.98 | 55.16 | 48.60 | 61.54 | 9.87 | -7.76 | 27.60 | 0.3204 | 71 | 49 | 0.0548 | 0.0552 | 2.56 | 1.99 | 3.31 | 2.92 | 2.14 | 3.99 | -0.36 | -0.90 | 0.16 | -0.88 | -0.11 | 223 | 92.38 | 88.13 | 95.19 | 84.65 | 97.84 |
| excluir_cero | dentro | fuera | fuera | publicado | retorno_sesion | 0.00 | 218 | 28 | 66.06 | 59.54 | 72.01 | 55.50 | 48.87 | 61.95 | 10.55 | -8.26 | 29.96 | 0.3209 | 69 | 46 | 0.0398 | 0.0402 | 3.44 | 2.76 | 4.27 | 3.85 | 2.94 | 5.00 | -0.41 | -0.89 | 0.03 | -0.99 | -0.06 | 0 |  |  |  |  |  |
| excluir_cero | dentro | fuera | fuera | vivo | retorno_sesion | 0.00 | 225 | 29 | 65.78 | 59.36 | 71.67 | 55.56 | 49.02 | 61.90 | 10.22 | -7.86 | 29.33 | 0.3282 | 69 | 46 | 0.0398 | 0.0402 | 3.39 | 2.73 | 4.22 | 3.78 | 2.89 | 4.91 | -0.39 | -0.85 | 0.04 | -0.96 | -0.06 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | fuera | publicado | retorno_sesion | 0.00 | 223 | 29 | 65.02 | 58.56 | 70.98 | 54.71 | 48.15 | 61.11 | 10.31 | -8.44 | 29.39 | 0.3282 | 70 | 47 | 0.0415 | 0.0420 | 3.42 | 2.74 | 4.24 | 3.80 | 2.89 | 4.90 | -0.38 | -0.85 | 0.07 | -0.93 | -0.04 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | fuera | vivo | gap | 0.00 | 230 | 29 | 64.35 | 57.97 | 70.26 | 55.22 | 48.76 | 61.51 | 9.13 | -7.39 | 26.52 | 0.3327 | 70 | 49 | 0.0663 | 0.0667 | 2.54 | 2.00 | 3.29 | 2.88 | 2.14 | 3.99 | -0.35 | -0.89 | 0.15 | -0.86 | -0.09 | 230 | 92.61 | 88.48 | 95.33 | 84.78 | 97.84 |
| estricta | dentro | fuera | dentro | publicado | retorno_sesion | 0.00 | 242 | 33 | 62.40 | 56.14 | 68.26 | 53.31 | 47.02 | 59.49 | 9.09 | -8.63 | 26.91 | 0.3344 | 71 | 49 | 0.0548 | 0.0552 | 3.44 | 2.83 | 4.21 | 3.70 | 2.83 | 4.74 | -0.25 | -0.73 | 0.20 | -0.80 | 0.11 | 0 |  |  |  |  |  |
| verificador | dentro | dentro | dentro | publicado | retorno_sesion | 0.25 | 188 | 30 | 67.02 | 60.02 | 73.34 | 56.38 | 49.24 | 63.27 | 10.64 | -8.12 | 30.27 | 0.3344 | 61 | 41 | 0.0594 | 0.0599 | 3.84 | 3.11 | 4.69 | 4.16 | 3.15 | 5.37 | -0.32 | -0.91 | 0.26 | -1.12 | 0.14 | 0 |  |  |  |  |  |
| estricta | dentro | fuera | fuera | publicado | gap | 0.00 | 222 | 28 | 64.86 | 58.38 | 70.84 | 55.41 | 48.83 | 61.80 | 9.46 | -8.48 | 27.27 | 0.3394 | 70 | 49 | 0.0663 | 0.0667 | 2.57 | 2.01 | 3.35 | 2.94 | 2.17 | 4.02 | -0.36 | -0.91 | 0.15 | -0.89 | -0.11 | 222 | 92.34 | 88.08 | 95.16 | 84.68 | 97.77 |
| verificador | dentro | dentro | dentro | publicado | gap | 0.00 | 243 | 34 | 67.49 | 61.37 | 73.07 | 58.85 | 52.57 | 64.85 | 8.64 | -7.72 | 25.23 | 0.3402 | 72 | 51 | 0.0709 | 0.0713 | 2.48 | 1.95 | 3.17 | 2.91 | 2.19 | 3.92 | -0.44 | -0.96 | 0.05 | -0.90 | -0.20 | 243 | 93.00 | 89.08 | 95.59 | 85.89 | 98.02 |
| excluir_cero | dentro | fuera | dentro | publicado | gap | 0.00 | 237 | 33 | 67.51 | 61.31 | 73.15 | 58.23 | 51.87 | 64.33 | 9.28 | -7.63 | 26.32 | 0.3407 | 71 | 49 | 0.0548 | 0.0552 | 2.53 | 2.00 | 3.25 | 2.99 | 2.26 | 4.03 | -0.46 | -0.99 | 0.04 | -0.93 | -0.22 | 237 | 92.83 | 88.81 | 95.47 | 85.48 | 97.98 |
| verificador | dentro | dentro | dentro | vivo | gap | 0.00 | 251 | 35 | 66.93 | 60.90 | 72.46 | 58.57 | 52.39 | 64.49 | 8.37 | -7.84 | 24.91 | 0.3464 | 72 | 51 | 0.0709 | 0.0713 | 2.45 | 1.93 | 3.14 | 2.87 | 2.18 | 3.86 | -0.42 | -0.93 | 0.06 | -0.88 | -0.17 | 251 | 93.23 | 89.42 | 95.73 | 86.14 | 98.16 |
| excluir_cero | dentro | fuera | dentro | vivo | gap | 0.00 | 245 | 34 | 66.94 | 60.83 | 72.53 | 57.96 | 51.70 | 63.97 | 8.98 | -7.20 | 25.60 | 0.3467 | 71 | 49 | 0.0548 | 0.0552 | 2.50 | 1.97 | 3.19 | 2.94 | 2.23 | 3.93 | -0.44 | -0.96 | 0.05 | -0.90 | -0.20 | 245 | 93.06 | 89.17 | 95.62 | 86.02 | 98.06 |
| excluir_cero | dentro | dentro | fuera | vivo | retorno_sesion | 0.00 | 226 | 30 | 65.49 | 59.08 | 71.38 | 55.75 | 49.23 | 62.08 | 9.73 | -7.96 | 28.63 | 0.3479 | 69 | 47 | 0.0507 | 0.0512 | 3.42 | 2.76 | 4.24 | 3.80 | 2.91 | 4.91 | -0.38 | -0.84 | 0.05 | -0.94 | -0.06 | 0 |  |  |  |  |  |
| excluir_cero | dentro | dentro | fuera | publicado | retorno_sesion | 0.00 | 219 | 29 | 65.75 | 59.25 | 71.72 | 55.71 | 49.09 | 62.13 | 10.05 | -9.05 | 29.38 | 0.3494 | 69 | 47 | 0.0507 | 0.0512 | 3.46 | 2.77 | 4.29 | 3.87 | 2.95 | 4.98 | -0.41 | -0.88 | 0.04 | -0.96 | -0.06 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | dentro | vivo | retorno_sesion | 0.00 | 251 | 35 | 62.15 | 56.01 | 67.93 | 53.39 | 47.21 | 59.46 | 8.76 | -7.66 | 25.97 | 0.3522 | 72 | 50 | 0.0568 | 0.0573 | 3.42 | 2.81 | 4.17 | 3.64 | 2.81 | 4.67 | -0.22 | -0.68 | 0.22 | -0.75 | 0.12 | 0 |  |  |  |  |  |
| excluir_cero | dentro | fuera | dentro | publicado | retorno_sesion | 0.00 | 238 | 33 | 63.03 | 56.73 | 68.91 | 54.20 | 47.86 | 60.41 | 8.82 | -9.02 | 26.89 | 0.3582 | 70 | 49 | 0.0663 | 0.0667 | 3.48 | 2.85 | 4.26 | 3.76 | 2.89 | 4.79 | -0.28 | -0.75 | 0.18 | -0.83 | 0.08 | 0 |  |  |  |  |  |
| excluir_cero | dentro | fuera | dentro | vivo | retorno_sesion | 0.00 | 245 | 34 | 62.86 | 56.65 | 68.67 | 54.29 | 48.03 | 60.41 | 8.57 | -8.44 | 25.82 | 0.3609 | 70 | 49 | 0.0663 | 0.0667 | 3.44 | 2.81 | 4.20 | 3.69 | 2.85 | 4.74 | -0.25 | -0.72 | 0.19 | -0.81 | 0.08 | 0 |  |  |  |  |  |
| estricta | dentro | dentro | dentro | publicado | retorno_sesion | 0.00 | 243 | 34 | 62.14 | 55.90 | 68.00 | 53.50 | 47.22 | 59.67 | 8.64 | -8.94 | 26.38 | 0.3762 | 71 | 50 | 0.0686 | 0.0690 | 3.47 | 2.84 | 4.23 | 3.72 | 2.87 | 4.77 | -0.25 | -0.72 | 0.21 | -0.78 | 0.10 | 0 |  |  |  |  |  |
| excluir_cero | dentro | dentro | fuera | vivo | gap | 0.00 | 226 | 30 | 64.60 | 58.17 | 70.54 | 56.19 | 49.68 | 62.51 | 8.41 | -8.44 | 26.32 | 0.3827 | 68 | 49 | 0.0957 | 0.0961 | 2.57 | 2.02 | 3.33 | 2.94 | 2.19 | 4.04 | -0.36 | -0.91 | 0.14 | -0.88 | -0.10 | 226 | 92.48 | 88.29 | 95.25 | 84.68 | 97.84 |
| verificador | dentro | fuera | dentro | publicado | gap | 0.00 | 242 | 33 | 67.36 | 61.22 | 72.95 | 59.09 | 52.80 | 65.10 | 8.26 | -8.20 | 24.90 | 0.3877 | 71 | 51 | 0.0850 | 0.0854 | 2.48 | 1.97 | 3.19 | 2.93 | 2.22 | 3.96 | -0.44 | -0.96 | 0.05 | -0.90 | -0.21 | 242 | 92.98 | 89.04 | 95.57 | 85.71 | 98.02 |
| excluir_cero | dentro | dentro | fuera | publicado | gap | 0.00 | 218 | 29 | 65.14 | 58.60 | 71.15 | 56.42 | 49.78 | 62.84 | 8.72 | -9.39 | 26.92 | 0.3962 | 68 | 49 | 0.0957 | 0.0961 | 2.61 | 2.03 | 3.36 | 2.99 | 2.19 | 4.09 | -0.38 | -0.93 | 0.16 | -0.91 | -0.12 | 218 | 92.20 | 87.87 | 95.07 | 84.35 | 97.79 |
| excluir_cero | dentro | dentro | dentro | vivo | retorno_sesion | 0.00 | 246 | 35 | 62.60 | 56.40 | 68.41 | 54.47 | 48.23 | 60.58 | 8.13 | -8.64 | 25.65 | 0.3972 | 70 | 50 | 0.0824 | 0.0828 | 3.47 | 2.84 | 4.22 | 3.72 | 2.88 | 4.76 | -0.25 | -0.71 | 0.19 | -0.79 | 0.09 | 0 |  |  |  |  |  |
| verificador | dentro | fuera | dentro | vivo | gap | 0.00 | 250 | 34 | 66.80 | 60.75 | 72.34 | 58.80 | 52.61 | 64.72 | 8.00 | -7.75 | 24.24 | 0.3989 | 71 | 51 | 0.0850 | 0.0854 | 2.45 | 1.94 | 3.14 | 2.88 | 2.19 | 3.87 | -0.42 | -0.93 | 0.05 | -0.89 | -0.18 | 250 | 93.20 | 89.38 | 95.71 | 86.23 | 98.11 |
| excluir_cero | dentro | dentro | dentro | publicado | retorno_sesion | 0.00 | 239 | 34 | 62.76 | 56.48 | 68.64 | 54.39 | 48.06 | 60.59 | 8.37 | -9.50 | 26.32 | 0.3992 | 70 | 50 | 0.0824 | 0.0828 | 3.51 | 2.87 | 4.28 | 3.78 | 2.93 | 4.84 | -0.27 | -0.74 | 0.19 | -0.81 | 0.08 | 0 |  |  |  |  |  |
| verificador | dentro | dentro | fuera | publicado | retorno_sesion | 0.00 | 223 | 29 | 65.02 | 58.56 | 70.98 | 56.50 | 49.94 | 62.84 | 8.52 | -10.31 | 27.83 | 0.4164 | 69 | 50 | 0.0985 | 0.0989 | 3.42 | 2.74 | 4.24 | 3.80 | 2.89 | 4.90 | -0.38 | -0.85 | 0.07 | -0.93 | -0.04 | 0 |  |  |  |  |  |
| verificador | dentro | dentro | fuera | vivo | retorno_sesion | 0.00 | 231 | 30 | 64.94 | 58.58 | 70.80 | 56.71 | 50.26 | 62.94 | 8.23 | -9.17 | 26.96 | 0.4199 | 69 | 50 | 0.0985 | 0.0989 | 3.38 | 2.73 | 4.19 | 3.72 | 2.84 | 4.82 | -0.34 | -0.80 | 0.09 | -0.90 | -0.02 | 0 |  |  |  |  |  |
| verificador | dentro | fuera | fuera | publicado | retorno_sesion | 0.00 | 222 | 28 | 65.32 | 58.84 | 71.27 | 56.31 | 49.73 | 62.67 | 9.01 | -9.82 | 28.18 | 0.4249 | 69 | 49 | 0.0798 | 0.0803 | 3.39 | 2.73 | 4.23 | 3.78 | 2.89 | 4.91 | -0.39 | -0.86 | 0.06 | -0.96 | -0.03 | 0 |  |  |  |  |  |
| verificador | dentro | fuera | fuera | vivo | retorno_sesion | 0.00 | 230 | 29 | 65.22 | 58.86 | 71.08 | 56.52 | 50.06 | 62.77 | 8.70 | -8.70 | 27.83 | 0.4281 | 69 | 49 | 0.0798 | 0.0803 | 3.35 | 2.70 | 4.15 | 3.70 | 2.82 | 4.81 | -0.35 | -0.82 | 0.07 | -0.93 | -0.02 | 0 |  |  |  |  |  |
| estricta | fuera | dentro | dentro | publicado | gap | 0.25 | 153 | 24 | 67.97 | 60.22 | 74.85 | 59.48 | 51.56 | 66.93 | 8.50 | -9.55 | 27.89 | 0.4326 | 46 | 33 | 0.1766 | 0.1770 | 2.73 | 1.90 | 3.77 | 3.18 | 2.10 | 4.68 | -0.45 | -1.23 | 0.27 | -1.31 | -0.10 | 153 | 90.20 | 84.45 | 93.97 | 79.76 | 97.93 |
| excluir_cero | dentro | fuera | fuera | vivo | gap | 0.00 | 225 | 29 | 64.44 | 58.00 | 70.41 | 56.44 | 49.91 | 62.76 | 8.00 | -8.85 | 25.93 | 0.4346 | 67 | 49 | 0.1141 | 0.1145 | 2.58 | 2.03 | 3.35 | 2.95 | 2.18 | 4.07 | -0.36 | -0.92 | 0.14 | -0.88 | -0.10 | 225 | 92.44 | 88.23 | 95.23 | 84.51 | 97.81 |
| estricta | fuera | dentro | dentro | vivo | gap | 0.25 | 160 | 25 | 67.50 | 59.91 | 74.27 | 59.38 | 51.63 | 66.68 | 8.12 | -9.26 | 27.10 | 0.4374 | 46 | 33 | 0.1766 | 0.1770 | 2.68 | 1.88 | 3.69 | 3.11 | 2.06 | 4.58 | -0.43 | -1.18 | 0.27 | -1.24 | -0.09 | 160 | 90.62 | 85.11 | 94.24 | 80.47 | 98.03 |
| verificador | dentro | dentro | fuera | vivo | gap | 0.00 | 231 | 30 | 64.50 | 58.14 | 70.39 | 57.14 | 50.70 | 63.36 | 7.36 | -9.09 | 24.79 | 0.4404 | 68 | 51 | 0.1421 | 0.1425 | 2.53 | 1.98 | 3.27 | 2.87 | 2.14 | 3.95 | -0.35 | -0.88 | 0.15 | -0.86 | -0.08 | 231 | 92.64 | 88.53 | 95.35 | 84.98 | 97.90 |
| verificador | dentro | dentro | fuera | publicado | gap | 0.00 | 223 | 29 | 65.02 | 58.56 | 70.98 | 57.40 | 50.84 | 63.71 | 7.62 | -9.81 | 25.61 | 0.4434 | 68 | 51 | 0.1421 | 0.1425 | 2.56 | 1.99 | 3.31 | 2.92 | 2.14 | 3.99 | -0.36 | -0.90 | 0.16 | -0.88 | -0.11 | 223 | 92.38 | 88.13 | 95.19 | 84.65 | 97.84 |
| excluir_cero | dentro | fuera | fuera | publicado | gap | 0.00 | 217 | 28 | 64.98 | 58.42 | 71.01 | 56.68 | 50.03 | 63.10 | 8.29 | -10.05 | 26.49 | 0.4474 | 67 | 49 | 0.1141 | 0.1145 | 2.62 | 2.05 | 3.41 | 3.00 | 2.22 | 4.10 | -0.38 | -0.93 | 0.15 | -0.92 | -0.12 | 217 | 92.17 | 87.81 | 95.05 | 84.33 | 97.73 |
| verificador | dentro | fuera | dentro | publicado | retorno_sesion | 0.00 | 242 | 33 | 62.40 | 56.14 | 68.26 | 54.96 | 48.66 | 61.10 | 7.44 | -10.43 | 25.51 | 0.4649 | 70 | 52 | 0.1234 | 0.1238 | 3.44 | 2.83 | 4.21 | 3.70 | 2.83 | 4.74 | -0.25 | -0.73 | 0.20 | -0.80 | 0.11 | 0 |  |  |  |  |  |
| verificador | dentro | fuera | dentro | vivo | retorno_sesion | 0.00 | 250 | 34 | 62.40 | 56.25 | 68.17 | 55.20 | 49.00 | 61.24 | 7.20 | -9.45 | 24.51 | 0.4664 | 70 | 52 | 0.1234 | 0.1238 | 3.40 | 2.78 | 4.14 | 3.62 | 2.79 | 4.66 | -0.22 | -0.69 | 0.22 | -0.77 | 0.12 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | dentro | publicado | gap | 0.25 | 153 | 24 | 67.97 | 60.22 | 74.85 | 60.13 | 52.22 | 67.55 | 7.84 | -10.21 | 27.33 | 0.4676 | 45 | 33 | 0.2127 | 0.2129 | 2.73 | 1.90 | 3.77 | 3.18 | 2.10 | 4.68 | -0.45 | -1.23 | 0.27 | -1.31 | -0.10 | 153 | 90.20 | 84.45 | 93.97 | 79.76 | 97.93 |
| excluir_cero | fuera | dentro | dentro | publicado | gap | 0.25 | 152 | 24 | 67.76 | 59.97 | 74.68 | 59.87 | 51.93 | 67.32 | 7.89 | -10.32 | 27.41 | 0.4676 | 45 | 33 | 0.2127 | 0.2129 | 2.74 | 1.90 | 3.79 | 3.20 | 2.11 | 4.71 | -0.46 | -1.25 | 0.27 | -1.32 | -0.09 | 152 | 90.13 | 84.36 | 93.93 | 79.73 | 97.92 |
| estricta | fuera | fuera | dentro | vivo | gap | 0.25 | 159 | 24 | 67.30 | 59.67 | 74.10 | 59.75 | 51.98 | 67.05 | 7.55 | -10.13 | 26.45 | 0.4691 | 45 | 33 | 0.2127 | 0.2129 | 2.70 | 1.91 | 3.70 | 3.13 | 2.09 | 4.61 | -0.43 | -1.17 | 0.27 | -1.25 | -0.09 | 159 | 90.57 | 85.02 | 94.20 | 80.37 | 97.95 |
| verificador | fuera | dentro | dentro | vivo | gap | 0.25 | 160 | 25 | 67.50 | 59.91 | 74.27 | 60.00 | 52.26 | 67.27 | 7.50 | -9.88 | 26.38 | 0.4744 | 45 | 33 | 0.2127 | 0.2129 | 2.68 | 1.88 | 3.69 | 3.11 | 2.06 | 4.58 | -0.43 | -1.18 | 0.27 | -1.24 | -0.09 | 160 | 90.62 | 85.11 | 94.24 | 80.47 | 98.03 |
| excluir_cero | fuera | dentro | dentro | vivo | gap | 0.25 | 159 | 25 | 67.30 | 59.67 | 74.10 | 59.75 | 51.98 | 67.05 | 7.55 | -9.94 | 26.62 | 0.4744 | 45 | 33 | 0.2127 | 0.2129 | 2.69 | 1.89 | 3.70 | 3.13 | 2.07 | 4.62 | -0.44 | -1.20 | 0.27 | -1.26 | -0.09 | 159 | 90.57 | 85.02 | 94.20 | 80.36 | 98.01 |
| verificador | dentro | dentro | dentro | vivo | retorno_sesion | 0.00 | 251 | 35 | 62.15 | 56.01 | 67.93 | 55.38 | 49.19 | 61.40 | 6.77 | -9.80 | 24.15 | 0.4809 | 70 | 53 | 0.1488 | 0.1491 | 3.42 | 2.81 | 4.17 | 3.64 | 2.81 | 4.67 | -0.22 | -0.68 | 0.22 | -0.75 | 0.12 | 0 |  |  |  |  |  |
| verificador | dentro | dentro | dentro | publicado | retorno_sesion | 0.00 | 243 | 34 | 62.14 | 55.90 | 68.00 | 55.14 | 48.86 | 61.27 | 7.00 | -10.69 | 25.10 | 0.4814 | 70 | 53 | 0.1488 | 0.1491 | 3.47 | 2.84 | 4.23 | 3.72 | 2.87 | 4.77 | -0.25 | -0.72 | 0.21 | -0.78 | 0.10 | 0 |  |  |  |  |  |
| estricta | fuera | fuera | dentro | publicado | gap | 0.25 | 152 | 23 | 67.76 | 59.97 | 74.68 | 59.87 | 51.93 | 67.32 | 7.89 | -10.37 | 27.59 | 0.4904 | 45 | 33 | 0.2127 | 0.2129 | 2.74 | 1.91 | 3.80 | 3.20 | 2.11 | 4.71 | -0.46 | -1.23 | 0.29 | -1.32 | -0.10 | 152 | 90.13 | 84.36 | 93.93 | 79.75 | 97.90 |
| estricta | fuera | fuera | fuera | vivo | retorno_sesion | 0.25 | 148 | 21 | 70.27 | 62.47 | 77.05 | 61.49 | 53.45 | 68.94 | 8.78 | -12.23 | 29.87 | 0.4931 | 43 | 30 | 0.1597 | 0.1602 | 3.58 | 2.71 | 4.63 | 3.99 | 2.79 | 5.49 | -0.42 | -1.10 | 0.24 | -1.37 | 0.09 | 0 |  |  |  |  |  |
| verificador | dentro | fuera | fuera | vivo | gap | 0.00 | 230 | 29 | 64.35 | 57.97 | 70.26 | 57.39 | 50.93 | 63.61 | 6.96 | -9.48 | 24.35 | 0.4951 | 67 | 51 | 0.1671 | 0.1673 | 2.54 | 2.00 | 3.29 | 2.88 | 2.14 | 3.99 | -0.35 | -0.89 | 0.15 | -0.86 | -0.09 | 230 | 92.61 | 88.48 | 95.33 | 84.78 | 97.84 |
| verificador | dentro | fuera | fuera | publicado | gap | 0.00 | 222 | 28 | 64.86 | 58.38 | 70.84 | 57.66 | 51.08 | 63.97 | 7.21 | -10.71 | 25.23 | 0.5021 | 67 | 51 | 0.1671 | 0.1673 | 2.57 | 2.01 | 3.35 | 2.94 | 2.17 | 4.02 | -0.36 | -0.91 | 0.15 | -0.89 | -0.11 | 222 | 92.34 | 88.08 | 95.16 | 84.68 | 97.77 |
| verificador | fuera | fuera | dentro | vivo | gap | 0.25 | 159 | 24 | 67.30 | 59.67 | 74.10 | 60.38 | 52.62 | 67.65 | 6.92 | -10.74 | 25.93 | 0.5094 | 44 | 33 | 0.2543 | 0.2545 | 2.70 | 1.91 | 3.70 | 3.13 | 2.09 | 4.61 | -0.43 | -1.17 | 0.27 | -1.25 | -0.09 | 159 | 90.57 | 85.02 | 94.20 | 80.37 | 97.95 |
| excluir_cero | fuera | fuera | dentro | vivo | gap | 0.25 | 158 | 24 | 67.09 | 59.43 | 73.93 | 60.13 | 52.34 | 67.43 | 6.96 | -10.76 | 26.00 | 0.5094 | 44 | 33 | 0.2543 | 0.2545 | 2.71 | 1.92 | 3.71 | 3.15 | 2.10 | 4.65 | -0.44 | -1.19 | 0.27 | -1.26 | -0.10 | 158 | 90.51 | 84.93 | 94.16 | 80.26 | 97.93 |
| verificador | fuera | fuera | dentro | publicado | gap | 0.25 | 152 | 23 | 67.76 | 59.97 | 74.68 | 60.53 | 52.59 | 67.95 | 7.24 | -11.04 | 27.05 | 0.5259 | 44 | 33 | 0.2543 | 0.2545 | 2.74 | 1.91 | 3.80 | 3.20 | 2.11 | 4.71 | -0.46 | -1.23 | 0.29 | -1.32 | -0.10 | 152 | 90.13 | 84.36 | 93.93 | 79.75 | 97.90 |
| excluir_cero | fuera | fuera | dentro | publicado | gap | 0.25 | 151 | 23 | 67.55 | 59.73 | 74.50 | 60.26 | 52.30 | 67.72 | 7.28 | -11.18 | 27.15 | 0.5259 | 44 | 33 | 0.2543 | 0.2545 | 2.75 | 1.92 | 3.81 | 3.22 | 2.12 | 4.74 | -0.47 | -1.25 | 0.28 | -1.33 | -0.10 | 151 | 90.07 | 84.26 | 93.89 | 79.73 | 97.89 |
| estricta | fuera | dentro | fuera | vivo | retorno_sesion | 0.25 | 149 | 22 | 69.80 | 62.01 | 76.60 | 61.74 | 53.74 | 69.16 | 8.05 | -12.93 | 29.58 | 0.5316 | 43 | 31 | 0.2007 | 0.2010 | 3.62 | 2.74 | 4.71 | 4.03 | 2.83 | 5.56 | -0.41 | -1.11 | 0.24 | -1.32 | 0.09 | 0 |  |  |  |  |  |
| estricta | fuera | fuera | fuera | publicado | retorno_sesion | 0.25 | 141 | 20 | 70.21 | 62.21 | 77.14 | 61.70 | 53.47 | 69.31 | 8.51 | -13.99 | 30.77 | 0.5394 | 42 | 30 | 0.1945 | 0.1949 | 3.64 | 2.73 | 4.77 | 4.11 | 2.86 | 5.68 | -0.47 | -1.16 | 0.21 | -1.46 | 0.01 | 0 |  |  |  |  |  |
| excluir_cero | fuera | fuera | fuera | vivo | retorno_sesion | 0.25 | 144 | 21 | 70.83 | 62.95 | 77.64 | 63.19 | 55.07 | 70.63 | 7.64 | -13.70 | 29.33 | 0.5591 | 41 | 30 | 0.2351 | 0.2353 | 3.63 | 2.75 | 4.72 | 4.10 | 2.89 | 5.61 | -0.47 | -1.15 | 0.18 | -1.42 | 0.02 | 0 |  |  |  |  |  |
| estricta | fuera | dentro | fuera | publicado | retorno_sesion | 0.25 | 142 | 21 | 69.72 | 61.72 | 76.67 | 61.97 | 53.77 | 69.54 | 7.75 | -14.65 | 30.22 | 0.5599 | 42 | 31 | 0.2416 | 0.2418 | 3.68 | 2.80 | 4.81 | 4.15 | 2.89 | 5.70 | -0.47 | -1.16 | 0.22 | -1.42 | 0.01 | 0 |  |  |  |  |  |
| estricta | fuera | fuera | dentro | vivo | retorno_sesion | 0.25 | 159 | 24 | 67.92 | 60.32 | 74.68 | 61.01 | 53.25 | 68.24 | 6.92 | -12.96 | 27.11 | 0.5746 | 44 | 33 | 0.2543 | 0.2545 | 3.59 | 2.78 | 4.58 | 3.94 | 2.82 | 5.36 | -0.35 | -0.99 | 0.27 | -1.26 | 0.13 | 0 |  |  |  |  |  |
| excluir_cero | fuera | fuera | fuera | publicado | retorno_sesion | 0.25 | 138 | 20 | 71.01 | 62.96 | 77.93 | 63.04 | 54.74 | 70.64 | 7.97 | -15.11 | 30.56 | 0.5761 | 41 | 30 | 0.2351 | 0.2353 | 3.69 | 2.75 | 4.83 | 4.20 | 2.94 | 5.78 | -0.52 | -1.20 | 0.17 | -1.50 | -0.03 | 0 |  |  |  |  |  |
| estricta | fuera | dentro | fuera | publicado | gap | 0.25 | 142 | 21 | 65.49 | 57.36 | 72.81 | 59.15 | 50.93 | 66.90 | 6.34 | -13.04 | 26.81 | 0.5869 | 42 | 33 | 0.3557 | 0.3556 | 2.85 | 1.97 | 3.97 | 3.28 | 2.11 | 4.91 | -0.43 | -1.26 | 0.35 | -1.35 | -0.06 | 142 | 89.44 | 83.30 | 93.49 | 78.08 | 97.74 |
| estricta | fuera | dentro | dentro | vivo | retorno_sesion | 0.25 | 160 | 25 | 67.50 | 59.91 | 74.27 | 61.25 | 53.52 | 68.45 | 6.25 | -13.55 | 26.45 | 0.5909 | 44 | 34 | 0.3082 | 0.3082 | 3.63 | 2.80 | 4.65 | 3.97 | 2.84 | 5.42 | -0.35 | -0.98 | 0.27 | -1.22 | 0.12 | 0 |  |  |  |  |  |
| estricta | fuera | dentro | fuera | vivo | gap | 0.25 | 149 | 22 | 65.10 | 57.15 | 72.29 | 59.06 | 51.03 | 66.63 | 6.04 | -12.12 | 25.68 | 0.5934 | 42 | 33 | 0.3557 | 0.3556 | 2.79 | 1.95 | 3.87 | 3.20 | 2.08 | 4.80 | -0.41 | -1.21 | 0.34 | -1.28 | -0.04 | 149 | 89.93 | 84.05 | 93.80 | 79.22 | 97.86 |
| excluir_cero | fuera | dentro | fuera | publicado | retorno_sesion | 0.25 | 139 | 21 | 70.50 | 62.45 | 77.45 | 63.31 | 55.04 | 70.86 | 7.19 | -15.79 | 30.22 | 0.5951 | 41 | 31 | 0.2888 | 0.2888 | 3.73 | 2.82 | 4.88 | 4.24 | 2.98 | 5.79 | -0.51 | -1.20 | 0.17 | -1.47 | -0.03 | 0 |  |  |  |  |  |
| estricta | fuera | fuera | dentro | publicado | retorno_sesion | 0.25 | 152 | 23 | 67.76 | 59.97 | 74.68 | 61.18 | 53.25 | 68.56 | 6.58 | -13.73 | 27.89 | 0.5976 | 43 | 33 | 0.3019 | 0.3019 | 3.65 | 2.80 | 4.68 | 4.05 | 2.91 | 5.50 | -0.41 | -1.06 | 0.24 | -1.32 | 0.05 | 0 |  |  |  |  |  |
| excluir_cero | fuera | dentro | fuera | vivo | retorno_sesion | 0.25 | 145 | 22 | 70.34 | 62.46 | 77.18 | 63.45 | 55.36 | 70.85 | 6.90 | -14.69 | 28.95 | 0.6021 | 41 | 31 | 0.2888 | 0.2888 | 3.67 | 2.77 | 4.78 | 4.14 | 2.91 | 5.66 | -0.46 | -1.16 | 0.19 | -1.38 | 0.01 | 0 |  |  |  |  |  |
| estricta | fuera | fuera | fuera | publicado | gap | 0.25 | 141 | 20 | 65.25 | 57.08 | 72.61 | 59.57 | 51.32 | 67.32 | 5.67 | -13.64 | 25.85 | 0.6311 | 41 | 33 | 0.4160 | 0.4158 | 2.86 | 1.98 | 4.02 | 3.30 | 2.12 | 4.95 | -0.44 | -1.26 | 0.38 | -1.35 | -0.07 | 141 | 89.36 | 83.19 | 93.45 | 77.86 | 97.79 |
| estricta | fuera | dentro | dentro | publicado | retorno_sesion | 0.25 | 153 | 24 | 67.32 | 59.54 | 74.25 | 61.44 | 53.54 | 68.78 | 5.88 | -14.60 | 26.97 | 0.6323 | 43 | 34 | 0.3620 | 0.3619 | 3.69 | 2.85 | 4.74 | 4.09 | 2.94 | 5.53 | -0.40 | -1.07 | 0.23 | -1.29 | 0.04 | 0 |  |  |  |  |  |
| verificador | fuera | fuera | fuera | vivo | retorno_sesion | 0.25 | 148 | 21 | 70.27 | 62.47 | 77.05 | 64.19 | 56.20 | 71.46 | 6.08 | -14.94 | 27.78 | 0.6331 | 41 | 32 | 0.3492 | 0.3491 | 3.58 | 2.71 | 4.63 | 3.99 | 2.79 | 5.49 | -0.42 | -1.10 | 0.24 | -1.37 | 0.09 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | fuera | publicado | gap | 0.25 | 142 | 21 | 65.49 | 57.36 | 72.81 | 59.86 | 51.64 | 67.56 | 5.63 | -13.70 | 26.09 | 0.6336 | 41 | 33 | 0.4160 | 0.4158 | 2.85 | 1.97 | 3.97 | 3.28 | 2.11 | 4.91 | -0.43 | -1.26 | 0.35 | -1.35 | -0.06 | 142 | 89.44 | 83.30 | 93.49 | 78.08 | 97.74 |
| excluir_cero | fuera | dentro | fuera | publicado | gap | 0.25 | 141 | 21 | 65.25 | 57.08 | 72.61 | 59.57 | 51.32 | 67.32 | 5.67 | -13.82 | 26.28 | 0.6336 | 41 | 33 | 0.4160 | 0.4158 | 2.86 | 1.97 | 3.98 | 3.30 | 2.12 | 4.95 | -0.44 | -1.28 | 0.34 | -1.36 | -0.08 | 141 | 89.36 | 83.19 | 93.45 | 78.01 | 97.73 |
| excluir_cero | fuera | fuera | dentro | publicado | retorno_sesion | 0.25 | 149 | 23 | 68.46 | 60.61 | 75.37 | 62.42 | 54.42 | 69.79 | 6.04 | -14.67 | 27.74 | 0.6361 | 42 | 33 | 0.3557 | 0.3556 | 3.69 | 2.82 | 4.74 | 4.13 | 2.98 | 5.58 | -0.45 | -1.10 | 0.20 | -1.36 | 0.01 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | fuera | vivo | gap | 0.25 | 149 | 22 | 65.10 | 57.15 | 72.29 | 59.73 | 51.71 | 67.27 | 5.37 | -12.75 | 24.83 | 0.6378 | 41 | 33 | 0.4160 | 0.4158 | 2.79 | 1.95 | 3.87 | 3.20 | 2.08 | 4.80 | -0.41 | -1.21 | 0.34 | -1.28 | -0.04 | 149 | 89.93 | 84.05 | 93.80 | 79.22 | 97.86 |
| excluir_cero | fuera | dentro | fuera | vivo | gap | 0.25 | 148 | 22 | 64.86 | 56.89 | 72.09 | 59.46 | 51.41 | 67.03 | 5.41 | -12.84 | 25.00 | 0.6378 | 41 | 33 | 0.4160 | 0.4158 | 2.80 | 1.96 | 3.89 | 3.22 | 2.10 | 4.83 | -0.42 | -1.23 | 0.34 | -1.28 | -0.05 | 148 | 89.86 | 83.95 | 93.76 | 79.08 | 97.83 |
| excluir_cero | fuera | fuera | dentro | vivo | retorno_sesion | 0.25 | 155 | 24 | 68.39 | 60.70 | 75.19 | 62.58 | 54.74 | 69.81 | 5.81 | -14.65 | 26.54 | 0.6421 | 42 | 33 | 0.3557 | 0.3556 | 3.64 | 2.81 | 4.65 | 4.04 | 2.91 | 5.47 | -0.41 | -1.04 | 0.22 | -1.30 | 0.06 | 0 |  |  |  |  |  |
| estricta | fuera | fuera | fuera | vivo | gap | 0.25 | 148 | 21 | 64.86 | 56.89 | 72.09 | 59.46 | 51.41 | 67.03 | 5.41 | -12.84 | 25.17 | 0.6468 | 41 | 33 | 0.4160 | 0.4158 | 2.81 | 1.96 | 3.89 | 3.22 | 2.11 | 4.78 | -0.41 | -1.22 | 0.34 | -1.28 | -0.05 | 148 | 89.86 | 83.95 | 93.76 | 79.22 | 97.89 |
| verificador | fuera | fuera | fuera | publicado | retorno_sesion | 0.25 | 141 | 20 | 70.21 | 62.21 | 77.14 | 63.83 | 55.63 | 71.30 | 6.38 | -16.44 | 29.08 | 0.6488 | 41 | 32 | 0.3492 | 0.3491 | 3.64 | 2.73 | 4.77 | 4.11 | 2.86 | 5.68 | -0.47 | -1.16 | 0.21 | -1.46 | 0.01 | 0 |  |  |  |  |  |
| excluir_cero | fuera | dentro | dentro | vivo | retorno_sesion | 0.25 | 156 | 25 | 67.95 | 60.27 | 74.76 | 62.82 | 55.01 | 70.01 | 5.13 | -15.06 | 25.77 | 0.6666 | 42 | 34 | 0.4222 | 0.4220 | 3.68 | 2.83 | 4.72 | 4.08 | 2.93 | 5.53 | -0.40 | -1.03 | 0.22 | -1.27 | 0.05 | 0 |  |  |  |  |  |
| excluir_cero | fuera | dentro | dentro | publicado | retorno_sesion | 0.25 | 150 | 24 | 68.00 | 60.17 | 74.94 | 62.67 | 54.70 | 70.00 | 5.33 | -15.50 | 26.90 | 0.6683 | 42 | 34 | 0.4222 | 0.4220 | 3.73 | 2.88 | 4.80 | 4.17 | 3.02 | 5.63 | -0.44 | -1.11 | 0.19 | -1.32 | 0.00 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | fuera | publicado | retorno_sesion | 0.25 | 142 | 21 | 69.72 | 61.72 | 76.67 | 64.08 | 55.92 | 71.51 | 5.63 | -17.22 | 28.76 | 0.6753 | 41 | 33 | 0.4160 | 0.4158 | 3.68 | 2.80 | 4.81 | 4.15 | 2.89 | 5.70 | -0.47 | -1.16 | 0.22 | -1.42 | 0.01 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | fuera | vivo | retorno_sesion | 0.25 | 149 | 22 | 69.80 | 62.01 | 76.60 | 64.43 | 56.47 | 71.67 | 5.37 | -15.89 | 27.56 | 0.6771 | 41 | 33 | 0.4160 | 0.4158 | 3.62 | 2.74 | 4.71 | 4.03 | 2.83 | 5.56 | -0.41 | -1.11 | 0.24 | -1.32 | 0.09 | 0 |  |  |  |  |  |
| verificador | fuera | fuera | fuera | publicado | gap | 0.25 | 141 | 20 | 65.25 | 57.08 | 72.61 | 60.28 | 52.04 | 67.98 | 4.96 | -14.29 | 25.17 | 0.6808 | 40 | 33 | 0.4828 | 0.4825 | 2.86 | 1.98 | 4.02 | 3.30 | 2.12 | 4.95 | -0.44 | -1.26 | 0.38 | -1.35 | -0.07 | 141 | 89.36 | 83.19 | 93.45 | 77.86 | 97.79 |
| excluir_cero | fuera | fuera | fuera | publicado | gap | 0.25 | 140 | 20 | 65.00 | 56.79 | 72.40 | 60.00 | 51.72 | 67.74 | 5.00 | -14.38 | 25.34 | 0.6808 | 40 | 33 | 0.4828 | 0.4825 | 2.88 | 1.99 | 4.03 | 3.32 | 2.13 | 4.98 | -0.45 | -1.28 | 0.38 | -1.37 | -0.07 | 140 | 89.29 | 83.07 | 93.40 | 77.78 | 97.76 |
| estricta | fuera | dentro | dentro | vivo | gap | 0.00 | 207 | 29 | 63.77 | 57.02 | 70.01 | 59.90 | 53.11 | 66.34 | 3.86 | -12.08 | 20.10 | 0.6911 | 51 | 43 | 0.4705 | 0.4703 | 2.50 | 1.88 | 3.30 | 2.83 | 2.00 | 3.99 | -0.33 | -0.92 | 0.22 | -0.86 | -0.09 | 207 | 92.75 | 88.39 | 95.56 | 84.65 | 98.47 |
| verificador | fuera | fuera | fuera | vivo | gap | 0.25 | 148 | 21 | 64.86 | 56.89 | 72.09 | 60.14 | 52.09 | 67.67 | 4.73 | -13.42 | 24.48 | 0.6993 | 40 | 33 | 0.4828 | 0.4825 | 2.81 | 1.96 | 3.89 | 3.22 | 2.11 | 4.78 | -0.41 | -1.22 | 0.34 | -1.28 | -0.05 | 148 | 89.86 | 83.95 | 93.76 | 79.22 | 97.89 |
| excluir_cero | fuera | fuera | fuera | vivo | gap | 0.25 | 147 | 21 | 64.63 | 56.61 | 71.89 | 59.86 | 51.79 | 67.44 | 4.76 | -13.51 | 24.66 | 0.6993 | 40 | 33 | 0.4828 | 0.4825 | 2.82 | 1.96 | 3.91 | 3.24 | 2.12 | 4.82 | -0.42 | -1.24 | 0.34 | -1.29 | -0.06 | 147 | 89.80 | 83.85 | 93.72 | 79.16 | 97.87 |
| estricta | fuera | dentro | dentro | publicado | gap | 0.00 | 199 | 28 | 64.32 | 57.45 | 70.65 | 60.30 | 53.37 | 66.84 | 4.02 | -13.02 | 21.35 | 0.6998 | 51 | 43 | 0.4705 | 0.4703 | 2.54 | 1.90 | 3.36 | 2.88 | 2.04 | 4.07 | -0.34 | -0.96 | 0.22 | -0.90 | -0.10 | 199 | 92.46 | 87.94 | 95.38 | 84.34 | 98.44 |
| verificador | fuera | fuera | dentro | publicado | retorno_sesion | 0.25 | 152 | 23 | 67.76 | 59.97 | 74.68 | 63.16 | 55.25 | 70.41 | 4.61 | -15.86 | 26.53 | 0.7186 | 42 | 35 | 0.4944 | 0.4941 | 3.65 | 2.80 | 4.68 | 4.05 | 2.91 | 5.50 | -0.41 | -1.06 | 0.24 | -1.32 | 0.05 | 0 |  |  |  |  |  |
| verificador | fuera | fuera | dentro | vivo | retorno_sesion | 0.25 | 159 | 24 | 67.92 | 60.32 | 74.68 | 63.52 | 55.80 | 70.60 | 4.40 | -15.92 | 25.30 | 0.7213 | 42 | 35 | 0.4944 | 0.4941 | 3.59 | 2.78 | 4.58 | 3.94 | 2.82 | 5.36 | -0.35 | -0.99 | 0.27 | -1.26 | 0.13 | 0 |  |  |  |  |  |
| estricta | fuera | fuera | dentro | vivo | gap | 0.00 | 206 | 28 | 63.59 | 56.83 | 69.86 | 60.19 | 53.38 | 66.63 | 3.40 | -12.62 | 19.67 | 0.7333 | 50 | 43 | 0.5341 | 0.5338 | 2.51 | 1.89 | 3.29 | 2.84 | 2.02 | 4.00 | -0.33 | -0.90 | 0.22 | -0.86 | -0.08 | 206 | 92.72 | 88.33 | 95.54 | 84.79 | 98.54 |
| estricta | fuera | fuera | dentro | publicado | gap | 0.00 | 198 | 27 | 64.14 | 57.25 | 70.49 | 60.61 | 53.66 | 67.15 | 3.54 | -13.16 | 20.49 | 0.7398 | 50 | 43 | 0.5341 | 0.5338 | 2.55 | 1.90 | 3.38 | 2.90 | 2.04 | 4.06 | -0.35 | -0.94 | 0.22 | -0.90 | -0.11 | 198 | 92.42 | 87.88 | 95.36 | 84.13 | 98.45 |
| estricta | fuera | fuera | fuera | vivo | retorno_sesion | 0.00 | 192 | 24 | 63.54 | 56.53 | 70.02 | 59.90 | 52.83 | 66.57 | 3.65 | -15.10 | 22.40 | 0.7468 | 47 | 40 | 0.5203 | 0.5201 | 3.22 | 2.47 | 4.13 | 3.53 | 2.52 | 4.80 | -0.31 | -0.85 | 0.19 | -0.99 | 0.06 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | dentro | publicado | retorno_sesion | 0.25 | 153 | 24 | 67.32 | 59.54 | 74.25 | 63.40 | 55.52 | 70.62 | 3.92 | -16.77 | 25.47 | 0.7538 | 42 | 36 | 0.5716 | 0.5713 | 3.69 | 2.85 | 4.74 | 4.09 | 2.94 | 5.53 | -0.40 | -1.07 | 0.23 | -1.29 | 0.04 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | dentro | vivo | retorno_sesion | 0.25 | 160 | 25 | 67.50 | 59.91 | 74.27 | 63.75 | 56.06 | 70.80 | 3.75 | -16.28 | 24.38 | 0.7651 | 42 | 36 | 0.5716 | 0.5713 | 3.63 | 2.80 | 4.65 | 3.97 | 2.84 | 5.42 | -0.35 | -0.98 | 0.27 | -1.22 | 0.12 | 0 |  |  |  |  |  |
| estricta | fuera | fuera | fuera | publicado | retorno_sesion | 0.00 | 184 | 23 | 63.59 | 56.42 | 70.20 | 60.33 | 53.12 | 67.11 | 3.26 | -15.76 | 23.37 | 0.7806 | 46 | 40 | 0.5900 | 0.5898 | 3.27 | 2.50 | 4.19 | 3.62 | 2.59 | 4.89 | -0.36 | -0.91 | 0.15 | -1.03 | 0.03 | 0 |  |  |  |  |  |
| estricta | fuera | dentro | fuera | vivo | retorno_sesion | 0.00 | 193 | 25 | 63.21 | 56.21 | 69.70 | 60.10 | 53.06 | 66.75 | 3.11 | -15.08 | 21.76 | 0.8018 | 47 | 41 | 0.5943 | 0.5940 | 3.25 | 2.52 | 4.17 | 3.56 | 2.56 | 4.84 | -0.31 | -0.85 | 0.19 | -0.96 | 0.05 | 0 |  |  |  |  |  |
| excluir_cero | fuera | dentro | dentro | publicado | gap | 0.00 | 194 | 28 | 64.43 | 57.48 | 70.83 | 61.86 | 54.85 | 68.40 | 2.58 | -14.74 | 20.33 | 0.8208 | 48 | 43 | 0.6752 | 0.6750 | 2.59 | 1.94 | 3.44 | 2.96 | 2.10 | 4.16 | -0.36 | -0.99 | 0.22 | -0.93 | -0.12 | 194 | 92.27 | 87.64 | 95.26 | 83.89 | 98.39 |
| excluir_cero | fuera | fuera | fuera | publicado | retorno_sesion | 0.00 | 180 | 23 | 64.44 | 57.22 | 71.07 | 61.67 | 54.39 | 68.46 | 2.78 | -16.86 | 23.03 | 0.8225 | 45 | 40 | 0.6646 | 0.6644 | 3.31 | 2.53 | 4.25 | 3.71 | 2.65 | 4.98 | -0.39 | -0.94 | 0.12 | -1.06 | -0.01 | 0 |  |  |  |  |  |
| excluir_cero | fuera | fuera | fuera | vivo | retorno_sesion | 0.00 | 187 | 24 | 64.17 | 57.08 | 70.69 | 61.50 | 54.36 | 68.17 | 2.67 | -16.22 | 22.11 | 0.8248 | 45 | 40 | 0.6646 | 0.6644 | 3.27 | 2.50 | 4.21 | 3.62 | 2.60 | 4.91 | -0.36 | -0.90 | 0.14 | -1.02 | 0.01 | 0 |  |  |  |  |  |
| excluir_cero | fuera | dentro | dentro | vivo | gap | 0.00 | 202 | 29 | 63.86 | 57.03 | 70.17 | 61.39 | 54.52 | 67.83 | 2.48 | -13.64 | 19.23 | 0.8248 | 48 | 43 | 0.6752 | 0.6750 | 2.55 | 1.91 | 3.36 | 2.90 | 2.05 | 4.07 | -0.34 | -0.95 | 0.22 | -0.88 | -0.10 | 202 | 92.57 | 88.11 | 95.45 | 84.26 | 98.43 |
| estricta | fuera | fuera | dentro | vivo | retorno_sesion | 0.00 | 206 | 28 | 61.65 | 54.85 | 68.02 | 59.22 | 52.40 | 65.71 | 2.43 | -14.98 | 20.10 | 0.8365 | 48 | 43 | 0.6752 | 0.6750 | 3.26 | 2.55 | 4.12 | 3.52 | 2.56 | 4.70 | -0.27 | -0.77 | 0.21 | -0.87 | 0.08 | 0 |  |  |  |  |  |
| estricta | fuera | dentro | fuera | publicado | retorno_sesion | 0.00 | 185 | 24 | 63.24 | 56.09 | 69.86 | 60.54 | 53.35 | 67.30 | 2.70 | -16.22 | 22.40 | 0.8435 | 46 | 41 | 0.6683 | 0.6680 | 3.30 | 2.54 | 4.26 | 3.65 | 2.63 | 4.97 | -0.35 | -0.92 | 0.17 | -1.00 | 0.03 | 0 |  |  |  |  |  |
| estricta | fuera | dentro | fuera | vivo | gap | 0.00 | 193 | 25 | 61.66 | 54.63 | 68.23 | 59.59 | 52.54 | 66.26 | 2.07 | -14.50 | 19.00 | 0.8545 | 47 | 43 | 0.7520 | 0.7518 | 2.58 | 1.92 | 3.45 | 2.89 | 2.01 | 4.12 | -0.31 | -0.94 | 0.27 | -0.89 | -0.04 | 193 | 92.23 | 87.57 | 95.23 | 83.80 | 98.39 |
| estricta | fuera | dentro | fuera | publicado | gap | 0.00 | 185 | 24 | 62.16 | 54.99 | 68.84 | 60.00 | 52.81 | 66.79 | 2.16 | -15.17 | 19.79 | 0.8648 | 47 | 43 | 0.7520 | 0.7518 | 2.62 | 1.96 | 3.51 | 2.95 | 2.05 | 4.27 | -0.33 | -0.98 | 0.28 | -0.94 | -0.06 | 185 | 91.89 | 87.05 | 95.03 | 82.81 | 98.31 |
| estricta | fuera | fuera | dentro | publicado | retorno_sesion | 0.00 | 198 | 27 | 61.62 | 54.68 | 68.11 | 59.60 | 52.64 | 66.19 | 2.02 | -15.98 | 21.13 | 0.8763 | 47 | 43 | 0.7520 | 0.7518 | 3.31 | 2.57 | 4.20 | 3.61 | 2.64 | 4.81 | -0.31 | -0.82 | 0.19 | -0.92 | 0.05 | 0 |  |  |  |  |  |
| excluir_cero | fuera | dentro | fuera | publicado | retorno_sesion | 0.00 | 181 | 24 | 64.09 | 56.87 | 70.72 | 61.88 | 54.63 | 68.64 | 2.21 | -17.13 | 22.34 | 0.8795 | 45 | 41 | 0.7465 | 0.7463 | 3.35 | 2.56 | 4.32 | 3.74 | 2.69 | 5.08 | -0.39 | -0.95 | 0.13 | -1.03 | -0.01 | 0 |  |  |  |  |  |
| estricta | fuera | dentro | dentro | vivo | retorno_sesion | 0.00 | 207 | 29 | 61.35 | 54.57 | 67.72 | 59.42 | 52.62 | 65.88 | 1.93 | -15.60 | 19.89 | 0.8803 | 48 | 44 | 0.7547 | 0.7545 | 3.29 | 2.57 | 4.14 | 3.55 | 2.61 | 4.72 | -0.26 | -0.77 | 0.21 | -0.85 | 0.07 | 0 |  |  |  |  |  |
| excluir_cero | fuera | dentro | fuera | vivo | retorno_sesion | 0.00 | 188 | 25 | 63.83 | 56.75 | 70.36 | 61.70 | 54.58 | 68.35 | 2.13 | -16.67 | 21.32 | 0.8858 | 45 | 41 | 0.7465 | 0.7463 | 3.30 | 2.55 | 4.24 | 3.65 | 2.64 | 4.94 | -0.35 | -0.89 | 0.16 | -0.99 | 0.00 | 0 |  |  |  |  |  |
| estricta | fuera | fuera | fuera | vivo | gap | 0.00 | 192 | 24 | 61.46 | 54.41 | 68.05 | 59.90 | 52.83 | 66.57 | 1.56 | -15.62 | 18.23 | 0.8985 | 46 | 43 | 0.8323 | 0.8321 | 2.59 | 1.92 | 3.43 | 2.90 | 2.03 | 4.12 | -0.31 | -0.95 | 0.27 | -0.89 | -0.04 | 192 | 92.19 | 87.51 | 95.21 | 83.85 | 98.44 |
| excluir_cero | fuera | fuera | dentro | vivo | gap | 0.00 | 201 | 28 | 63.68 | 56.83 | 70.02 | 61.69 | 54.81 | 68.13 | 1.99 | -14.15 | 18.58 | 0.9045 | 47 | 43 | 0.7520 | 0.7518 | 2.56 | 1.93 | 3.36 | 2.91 | 2.07 | 4.09 | -0.35 | -0.94 | 0.21 | -0.89 | -0.10 | 201 | 92.54 | 88.05 | 95.43 | 84.41 | 98.51 |
| estricta | fuera | fuera | fuera | publicado | gap | 0.00 | 184 | 23 | 61.96 | 54.76 | 68.66 | 60.33 | 53.12 | 67.11 | 1.63 | -15.76 | 19.57 | 0.9063 | 46 | 43 | 0.8323 | 0.8321 | 2.64 | 1.96 | 3.50 | 2.96 | 2.06 | 4.23 | -0.33 | -0.98 | 0.26 | -0.94 | -0.06 | 184 | 91.85 | 86.99 | 95.00 | 83.15 | 98.37 |
| verificador | fuera | dentro | dentro | vivo | gap | 0.00 | 207 | 29 | 63.77 | 57.02 | 70.01 | 62.32 | 55.55 | 68.64 | 1.45 | -14.04 | 17.65 | 0.9083 | 48 | 45 | 0.8358 | 0.8357 | 2.50 | 1.88 | 3.30 | 2.83 | 2.00 | 3.99 | -0.33 | -0.92 | 0.22 | -0.86 | -0.09 | 207 | 92.75 | 88.39 | 95.56 | 84.65 | 98.47 |
| excluir_cero | fuera | fuera | dentro | publicado | gap | 0.00 | 193 | 27 | 64.25 | 57.27 | 70.67 | 62.18 | 55.16 | 68.72 | 2.07 | -14.77 | 19.61 | 0.9093 | 47 | 43 | 0.7520 | 0.7518 | 2.60 | 1.95 | 3.45 | 2.97 | 2.10 | 4.16 | -0.37 | -0.98 | 0.22 | -0.94 | -0.12 | 193 | 92.23 | 87.57 | 95.23 | 83.77 | 98.40 |
| excluir_cero | fuera | fuera | dentro | vivo | retorno_sesion | 0.00 | 201 | 28 | 62.19 | 55.32 | 68.60 | 60.70 | 53.80 | 67.19 | 1.49 | -16.18 | 19.70 | 0.9145 | 46 | 43 | 0.8323 | 0.8321 | 3.31 | 2.58 | 4.18 | 3.61 | 2.64 | 4.81 | -0.31 | -0.81 | 0.17 | -0.91 | 0.03 | 0 |  |  |  |  |  |
| excluir_cero | fuera | fuera | dentro | publicado | retorno_sesion | 0.00 | 194 | 27 | 62.37 | 55.38 | 68.89 | 60.82 | 53.81 | 67.42 | 1.55 | -16.75 | 21.13 | 0.9165 | 46 | 43 | 0.8323 | 0.8321 | 3.35 | 2.60 | 4.26 | 3.69 | 2.70 | 4.90 | -0.34 | -0.86 | 0.17 | -0.95 | 0.01 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | dentro | publicado | gap | 0.00 | 199 | 28 | 64.32 | 57.45 | 70.65 | 62.81 | 55.92 | 69.23 | 1.51 | -15.15 | 18.81 | 0.9175 | 48 | 45 | 0.8358 | 0.8357 | 2.54 | 1.90 | 3.36 | 2.88 | 2.04 | 4.07 | -0.34 | -0.96 | 0.22 | -0.90 | -0.10 | 199 | 92.46 | 87.94 | 95.38 | 84.34 | 98.44 |
| estricta | fuera | dentro | dentro | publicado | retorno_sesion | 0.00 | 199 | 28 | 61.31 | 54.39 | 67.80 | 59.80 | 52.86 | 66.36 | 1.51 | -16.35 | 20.10 | 0.9203 | 47 | 44 | 0.8341 | 0.8339 | 3.34 | 2.61 | 4.24 | 3.64 | 2.70 | 4.86 | -0.30 | -0.83 | 0.18 | -0.90 | 0.05 | 0 |  |  |  |  |  |
| excluir_cero | fuera | dentro | dentro | publicado | retorno_sesion | 0.00 | 195 | 28 | 62.05 | 55.07 | 68.57 | 61.03 | 54.03 | 67.59 | 1.03 | -17.13 | 20.00 | 0.9550 | 46 | 44 | 0.9161 | 0.9161 | 3.38 | 2.64 | 4.30 | 3.71 | 2.77 | 4.96 | -0.33 | -0.85 | 0.15 | -0.93 | 0.01 | 0 |  |  |  |  |  |
| excluir_cero | fuera | dentro | dentro | vivo | retorno_sesion | 0.00 | 202 | 29 | 61.88 | 55.02 | 68.30 | 60.89 | 54.02 | 67.36 | 0.99 | -16.85 | 19.37 | 0.9613 | 46 | 44 | 0.9161 | 0.9161 | 3.34 | 2.60 | 4.21 | 3.64 | 2.69 | 4.81 | -0.30 | -0.80 | 0.17 | -0.89 | 0.03 | 0 |  |  |  |  |  |
| verificador | fuera | fuera | fuera | publicado | gap | 0.00 | 184 | 23 | 61.96 | 54.76 | 68.66 | 63.04 | 55.87 | 69.68 | -1.09 | -18.48 | 17.39 | 1.0000 | 43 | 45 | 0.9152 | 0.9151 | 2.64 | 1.96 | 3.50 | 2.96 | 2.06 | 4.23 | -0.33 | -0.98 | 0.26 | -0.94 | -0.06 | 184 | 91.85 | 86.99 | 95.00 | 83.15 | 98.37 |
| verificador | fuera | fuera | fuera | vivo | gap | 0.00 | 192 | 24 | 61.46 | 54.41 | 68.05 | 62.50 | 55.47 | 69.04 | -1.04 | -17.71 | 15.62 | 1.0000 | 43 | 45 | 0.9152 | 0.9151 | 2.59 | 1.92 | 3.43 | 2.90 | 2.03 | 4.12 | -0.31 | -0.95 | 0.27 | -0.89 | -0.04 | 192 | 92.19 | 87.51 | 95.21 | 83.85 | 98.44 |
| verificador | fuera | fuera | fuera | vivo | retorno_sesion | 0.00 | 192 | 24 | 63.54 | 56.53 | 70.02 | 62.50 | 55.47 | 69.04 | 1.04 | -17.71 | 20.83 | 1.0000 | 45 | 43 | 0.9152 | 0.9151 | 3.22 | 2.47 | 4.13 | 3.53 | 2.52 | 4.80 | -0.31 | -0.85 | 0.19 | -0.99 | 0.06 | 0 |  |  |  |  |  |
| verificador | fuera | fuera | fuera | publicado | retorno_sesion | 0.00 | 184 | 23 | 63.59 | 56.42 | 70.20 | 62.50 | 55.32 | 69.17 | 1.09 | -18.48 | 20.65 | 1.0000 | 45 | 43 | 0.9152 | 0.9151 | 3.27 | 2.50 | 4.19 | 3.62 | 2.59 | 4.89 | -0.36 | -0.91 | 0.15 | -1.03 | 0.03 | 0 |  |  |  |  |  |
| verificador | fuera | fuera | dentro | vivo | gap | 0.00 | 206 | 28 | 63.59 | 56.83 | 69.86 | 62.62 | 55.84 | 68.94 | 0.97 | -14.75 | 17.22 | 1.0000 | 47 | 45 | 0.9170 | 0.9170 | 2.51 | 1.89 | 3.29 | 2.84 | 2.02 | 4.00 | -0.33 | -0.90 | 0.22 | -0.86 | -0.08 | 206 | 92.72 | 88.33 | 95.54 | 84.79 | 98.54 |
| verificador | fuera | fuera | dentro | publicado | gap | 0.00 | 198 | 27 | 64.14 | 57.25 | 70.49 | 63.13 | 56.22 | 69.54 | 1.01 | -15.31 | 18.08 | 1.0000 | 47 | 45 | 0.9170 | 0.9170 | 2.55 | 1.90 | 3.38 | 2.90 | 2.04 | 4.06 | -0.35 | -0.94 | 0.22 | -0.90 | -0.11 | 198 | 92.42 | 87.88 | 95.36 | 84.13 | 98.45 |
| excluir_cero | fuera | dentro | fuera | vivo | gap | 0.00 | 188 | 25 | 61.70 | 54.58 | 68.35 | 61.17 | 54.05 | 67.85 | 0.53 | -16.16 | 17.74 | 1.0000 | 44 | 43 | 1.0000 | 1.0000 | 2.64 | 1.96 | 3.51 | 2.96 | 2.07 | 4.23 | -0.33 | -0.98 | 0.27 | -0.92 | -0.05 | 188 | 92.02 | 87.25 | 95.11 | 83.33 | 98.35 |
| excluir_cero | fuera | dentro | fuera | publicado | gap | 0.00 | 180 | 24 | 62.22 | 54.95 | 68.98 | 61.67 | 54.39 | 68.46 | 0.56 | -17.20 | 18.54 | 1.0000 | 44 | 43 | 1.0000 | 1.0000 | 2.69 | 2.00 | 3.59 | 3.03 | 2.11 | 4.37 | -0.35 | -1.02 | 0.28 | -0.95 | -0.08 | 180 | 91.67 | 86.71 | 94.89 | 82.49 | 98.27 |
| verificador | fuera | dentro | fuera | publicado | gap | 0.00 | 185 | 24 | 62.16 | 54.99 | 68.84 | 62.70 | 55.54 | 69.35 | -0.54 | -17.71 | 16.85 | 1.0000 | 44 | 45 | 1.0000 | 1.0000 | 2.62 | 1.96 | 3.51 | 2.95 | 2.05 | 4.27 | -0.33 | -0.98 | 0.28 | -0.94 | -0.06 | 185 | 91.89 | 87.05 | 95.03 | 82.81 | 98.31 |
| verificador | fuera | dentro | fuera | vivo | gap | 0.00 | 193 | 25 | 61.66 | 54.63 | 68.23 | 62.18 | 55.16 | 68.72 | -0.52 | -16.20 | 16.13 | 1.0000 | 44 | 45 | 1.0000 | 1.0000 | 2.58 | 1.92 | 3.45 | 2.89 | 2.01 | 4.12 | -0.31 | -0.94 | 0.27 | -0.89 | -0.04 | 193 | 92.23 | 87.57 | 95.23 | 83.80 | 98.39 |
| verificador | fuera | dentro | fuera | vivo | retorno_sesion | 0.00 | 193 | 25 | 63.21 | 56.21 | 69.70 | 62.69 | 55.69 | 69.21 | 0.52 | -18.13 | 19.17 | 1.0000 | 45 | 44 | 1.0000 | 1.0000 | 3.25 | 2.52 | 4.17 | 3.56 | 2.56 | 4.84 | -0.31 | -0.85 | 0.19 | -0.96 | 0.05 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | fuera | publicado | retorno_sesion | 0.00 | 185 | 24 | 63.24 | 56.09 | 69.86 | 62.70 | 55.54 | 69.35 | 0.54 | -18.75 | 20.22 | 1.0000 | 45 | 44 | 1.0000 | 1.0000 | 3.30 | 2.54 | 4.26 | 3.65 | 2.63 | 4.97 | -0.35 | -0.92 | 0.17 | -1.00 | 0.03 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | dentro | publicado | retorno_sesion | 0.00 | 199 | 28 | 61.31 | 54.39 | 67.80 | 61.81 | 54.90 | 68.28 | -0.50 | -18.39 | 18.23 | 1.0000 | 46 | 47 | 1.0000 | 1.0000 | 3.34 | 2.61 | 4.24 | 3.64 | 2.70 | 4.86 | -0.30 | -0.83 | 0.18 | -0.90 | 0.05 | 0 |  |  |  |  |  |
| verificador | fuera | dentro | dentro | vivo | retorno_sesion | 0.00 | 207 | 29 | 61.35 | 54.57 | 67.72 | 61.84 | 55.06 | 68.18 | -0.48 | -18.04 | 17.77 | 1.0000 | 46 | 47 | 1.0000 | 1.0000 | 3.29 | 2.57 | 4.14 | 3.55 | 2.61 | 4.72 | -0.26 | -0.77 | 0.21 | -0.85 | 0.07 | 0 |  |  |  |  |  |
| verificador | fuera | fuera | dentro | publicado | retorno_sesion | 0.00 | 198 | 27 | 61.62 | 54.68 | 68.11 | 61.62 | 54.68 | 68.11 | 0.00 | -17.82 | 19.14 | 1.0000 | 46 | 46 | 1.0000 | 1.0000 | 3.31 | 2.57 | 4.20 | 3.61 | 2.64 | 4.81 | -0.31 | -0.82 | 0.19 | -0.92 | 0.05 | 0 |  |  |  |  |  |
| verificador | fuera | fuera | dentro | vivo | retorno_sesion | 0.00 | 206 | 28 | 61.65 | 54.85 | 68.02 | 61.65 | 54.85 | 68.02 | 0.00 | -17.35 | 17.99 | 1.0000 | 46 | 46 | 1.0000 | 1.0000 | 3.26 | 2.55 | 4.12 | 3.52 | 2.56 | 4.70 | -0.27 | -0.77 | 0.21 | -0.87 | 0.08 | 0 |  |  |  |  |  |
| excluir_cero | fuera | fuera | fuera | publicado | gap | 0.00 | 179 | 23 | 62.01 | 54.72 | 68.80 | 62.01 | 54.72 | 68.80 | 0.00 | -17.68 | 18.89 | 1.0000 | 43 | 43 | 1.0000 | 1.0000 | 2.70 | 2.01 | 3.59 | 3.05 | 2.12 | 4.35 | -0.35 | -1.01 | 0.26 | -0.96 | -0.09 | 179 | 91.62 | 86.64 | 94.86 | 82.49 | 98.31 |
| excluir_cero | fuera | fuera | fuera | vivo | gap | 0.00 | 187 | 24 | 61.50 | 54.36 | 68.17 | 61.50 | 54.36 | 68.17 | 0.00 | -17.11 | 17.11 | 1.0000 | 43 | 43 | 1.0000 | 1.0000 | 2.65 | 1.97 | 3.51 | 2.98 | 2.09 | 4.21 | -0.33 | -0.98 | 0.27 | -0.93 | -0.06 | 187 | 91.98 | 87.19 | 95.08 | 83.33 | 98.37 |


---

## Lo que este frente NO computó

- **Residualización y ventana de betas.** Son parámetros del MOTOR, no de la capa de medición: variarlos exige re-emitir las predicciones, y las filas selladas no se reescriben (Constitución 5.0, punto 3). Fuera por construcción, no por olvido.
- **Qué hacer con las 15 filas SIN pareja cuya `sesion_objetivo` tampoco calza con su `available_at`.** Se cuentan y se declaran (arriba, en el eje retirado), pero NO se retiran: la regla firmada arbitra entre filas que compiten y estas 15 están solas. Descartarlas sin reemplazo es otra decisión y es de Nicolás — está abierta en `cola_decisiones.md`. Nota: en el caso del 5-jul la sesión correcta (07-03) YA HABÍA CERRADO al sellar, así que con el ancla temporal buena esas 8 filas caerían en `no_verificable_timing`. **No las descartaría un criterio nuevo: las descartaría la regla maestra que el proyecto ya tiene.**
- **Una corrección de multiplicidad sobre las celdas.** A propósito: comparten casi todas las filas y un Bonferroni ingenuo sobre ellas no significaría nada. El resultado de este frente es el COCIENTE y el RANGO, no un p corregido.
- **Un intervalo alrededor de los cocientes de celdas** («59/192», «0/192»). No se pone, y no por olvido: las 192 celdas son un CENSO exhaustivo y determinista sobre un solo conjunto de datos, no una muestra de un universo de caminos. No hay proceso de muestreo binomial que genere esa fracción, así que un Wilson encima supondría 192 Bernoulli independientes — exactamente el supuesto de independencia que este informe rechaza dos secciones más arriba, y el mismo argumento que descarta Bonferroni. La incertidumbre real vive en los datos, y la llevan los intervalos de cada celda.
- **El desglose por bolsa**, por la razón de la tabla de no-ejes: meterlo fabricaría significancia, que es el pecado que esta matriz mide.

---

## El registro de intentos

Regla de la casa: **cada configuración evaluada cuenta como intento**, incluidas las descartadas. Este frente evaluó 192 configuraciones de MEDICIÓN, no de modelo: no eligió features, no ajustó parámetros y no seleccionó una variante ganadora. Por eso NO se suma como 192 intentos al `N_intentos` del DSR, que cuenta selección de modelo.

**Pero la exposición existe y se declara:** este informe publica celdas individuales que alguien podría citar sueltas —la de ventaja máxima (+15.4 pp), o la propia celda ancla bajo la regla firmada (+9.7 pp, p = 0.0451)—. **Citar cualquier celda individual como resultado del proyecto mueve `N_intentos` y hay que decirlo en el mismo párrafo en que se la cita.** El resultado de este frente es el COCIENTE, el RANGO y la lista de supervivientes; ninguna celda suelta lo es.

