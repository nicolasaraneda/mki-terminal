# El MDE contra la ventaja observada

*¿Es comparable el umbral de relevancia que el proyecto derivó de su propio criterio con el efecto que su propio track record midió? Y si lo es, ¿qué dice la comparación?*

> **EN DIEZ SEGUNDOS**
>
> **1.** **Sí viven en la misma escala**, y está verificado por un mecanismo distinto del que produjo el MDE: la ventaja publicada `+6.4516 pp` coincide a diez decimales con `(b−c)/n` de la tabla de McNemar y con la identidad `f·(2q−1)` que es el lado izquierdo de la desigualdad del MDE. Ni `b`, ni `c`, ni las tasas entran en el cómputo de `8.96`.
>
> **2.** **Pero NO comparten denominador.** El `8.96 pp` publicado se computa sobre filas deduplicadas y **sin ancla temporal**; la ventaja publicada, sobre las 248 filas ancladas a `verificado_en ≤ 2026-08-28`. Recomputado sobre **las mismas filas**, el MDE es **7.74 pp**; deduplicado *y* anclado, **9.10 pp**. Tres números, y el publicado es el único que se mueve con el reloj.
>
> **3.** **La afirmación fuerte que este frente venía a escribir —«no valdría la pena aunque fuera real»— NO se sostiene y queda refutada.** La diferencia pareada `δ_obs − MDE` es **−1.29 pp con IC95 [−18.92, +14.90]** (bootstrap de clústeres de día, mismas filas): **el intervalo contiene el cero**, o sea que la diferencia no se distingue de cero. `P(δ_obs < MDE) = 0.569`: una moneda. El experimento **no ordena** las dos cantidades.
>
> **4.** **Y el titular de la matriz es el opuesto del que se esperaba, y más fuerte.** Por punto estimado, **274 de 768** celdas superan el MDE de 8.96 y **425 de 768** superan su borde inferior de 6.67. Por intervalo, **0 de 768** lo superan, **0 de 768** quedan por debajo, y **768 de 768 lo contienen**. Ninguna celda del jardín distingue «irrelevante» de «relevante».

- Generado: 2026-09-01 · Frente D de la quinta corrida
- Fuente: `senales.db` en `mode=ro` vía `backtest.linea_base.cargar` · modelo 4.6.0 · `legacy = 0`
- **Reproducible con un comando:** `python GEMELO/SECUENCIAL/mde_vs_observado.py`. Toda cifra de este documento sale de ahí; ninguna está cableada en la prosa.
- Ancla: `hasta_sello = 2026-08-28`, convención `excluir_cero` → **n = 248 en 34 días**, modelo 66.1%, base 59.7%, ventaja +6.45 pp, b = 72, c = 56, McNemar exacto p = 0.1847. Reproduce el README y el ancla de `bifurcaciones.md`.
- **Ninguna cifra publicada se mueve.** Este documento mide *alrededor* de lo publicado.

---

## D1 — ¿Están en la misma escala del endpoint?

### D1a. La escala: SÍ, y con vara independiente

La regla de la casa prohíbe verificar recorriendo la misma conversión otra vez. Así que la escala no se comprueba recomputando `f · 2c / E|gap|`, sino atacando el **otro lado** de la desigualdad.

El MDE de §A3.1.c es una condición sobre una cantidad `δ` definida por la identidad `δ = f·(2q−1)`, con `f` la fracción de predicciones a la baja y `q = P(gap<0 | baja)`. Esa identidad es el lado izquierdo. El `8.96` es el lado derecho. **Si el lado izquierdo resulta ser numéricamente idéntico a la ventaja publicada, las dos cantidades viven en la misma escala** — y eso se puede comprobar con insumos que no participan del cómputo del MDE.

| camino | valor | insumos |
|---|---|---|
| [A] diferencia cruda de tasas de acierto | **6.4516129032 pp** | `acierto_gap`, `base_acierto` |
| [B] `(b−c)/n` de la tabla de McNemar | **6.4516129032 pp** | b = 72, c = 56, n = 248 |
| [C] identidad del MDE `f·(2q−1)` | **6.4516129032 pp** | f = 0.516129, q = 0.562500 |

Coinciden a **diez decimales**, y `|[A]−[C]| = |[B]−[C]| = 0` exactamente. El puente además tiene una comprobación estructural que no depende de ningún estimador: **las filas donde el modelo difiere de «siempre al alza» son 128, y las filas donde el modelo predice BAJA son 128 — el mismo conjunto.** Es la razón algebraica de por qué la identidad tiene que valer, y verla en enteros vale más que verla en decimales.

**Veredicto D1a: misma escala, confirmada.** `b`, `c` y las dos tasas no entran en `f · 2c / E|gap|`; es una vara distinta, no la misma conversión repetida. Esto es lo que §A3.1.a **no** pudo ofrecer para `E|r|` y honestamente retractó.

Con el recordatorio de que `q` = 56.25% tiene **Wilson95 [47.6, 64.5]**, que incluye el 50%: la identidad es exacta, la cantidad que describe no se distingue del nulo.

### D1b. El denominador: NO

Misma escala no es mismo denominador, y acá no lo es. Tres veces.

| variante | filas | f | E\|gap\| | **MDE a 25 pb** | IC95 (sólo E\|gap\|) |
|---|---|---|---|---|---|
| **mismas filas que la cifra publicada** (n = 248, anclado, sin dedup) | 248 | 0.5161 | 3.3347% | **7.74 pp** | [5.28, 10.74] |
| dedup por sesión **y anclado** | 233 | 0.5494 | 3.0173% | **9.10 pp** | [6.84, 11.59] |
| **lo publicado** — dedup, **sin ancla** | 241 (hoy) | 0.5311 | 2.9650% | **8.96 pp** | [6.67, 11.32] |

Dos discrepancias, de distinto peso:

**1. La deduplicación.** Es una decisión de medición legítima y bien argumentada (§A3.1.a: 30 filas apuntan a la misma sesión objetivo que otra, y entre ellas están los movimientos más grandes). Pero **se aplica a un lado y no al otro**: el `+6.5 pp` publicado NO está deduplicado. Comparar un umbral deduplicado con un efecto no deduplicado es comparar poblaciones distintas. La diferencia no es cosmética: **1.36 pp de MDE**, más que la brecha entera que D2 quería declarar.

**2. La falta de ancla temporal, que es el defecto grave.** `mde_desde_v6.py:94-102` escribe su propio SQL en vez de llamar a `backtest.linea_base.cargar(hasta_sello=…)`. **El cuarto dictamen ya diagnosticó exactamente esto el 31-ago** (`DISEÑO.md`:34-41: «con corte 26-ago el MDE da 7.38 pp, con 28/30-ago 7.22, hoy 7.13») y lo puso como una de las cuatro condiciones para levantar el rechazo. **Hoy sigue sin arreglarse.** El `8.96` de hoy es, por construcción, un número distinto del `8.96` de mañana, y el pre-registro lo cita como si fuera un parámetro.

### D1c. El intervalo del MDE propaga un insumo de tres

`[6.67, 11.32]` no es el intervalo del MDE. **Es el intervalo de `E|gap|`, invertido.** Los otros dos insumos entran como certezas.

| eje | tratamiento actual | rango del MDE si se propaga |
|---|---|---|
| **E\|gap\|**, IC95 bloque-20 [2.4030, 4.8908]% | propagado | [5.28, 10.74] pp |
| **f**, Wilson95 [0.4542, 0.5776] | **punto** | sumado: [4.64, 12.02] pp |
| **simetría de magnitudes** | **certeza** | ver abajo |

**El tercer eje es el que manda, y es el único con cero propagación.** §A3.1.c lo dice con todas las letras: *«el supuesto que manda es el de simetría de magnitudes»*. Sin suponerla, la condición económica `E[gap|baja] < −2c` da

```
δ_min = 2f · (2c − (A−W)/2) / (A + W)
```

con `A` = |gap| medio cuando el modelo acierta la baja y `W` = |gap| medio cuando se equivoca. Con `A = W` se reduce exactamente a `f·2c/E|gap|` (hay self-test). Medido sobre el ancla:

| | |
|---|---|
| A (\|gap\| cuando acierta la baja) | **2.8481%** |
| W (\|gap\| cuando se equivoca) | **3.4917%** |
| razón A/W | **0.816×**, IC95 bloque-20 **[0.402, 2.130]** — incluye 1.0 |
| MDE con las magnitudes **observadas** | **13.38 pp** (contra 7.74 simétrico) |
| MDE en el borde inferior de la razón (0.402) | 29.73 pp |
| MDE en el borde superior de la razón (2.130) | −10.89 pp |

**Un rango de −10.9 a +29.7 pp sobre un solo eje, contra el [6.67, 11.32] que se publica.** El intervalo publicado es angosto porque mide un insumo y da por sabidos los otros dos, incluido el que su propio texto declara dominante.

Y hay un hallazgo de paso que merece decirse: **en la escala del endpoint la asimetría apunta al lado contrario del que la razón 2 retractada suponía.** En la escala del retorno de sesión la magnitud media era mayor en los aciertos que en los errores (razón 1.33×); en la escala de `acierto_gap` es mayor en los errores (razón 0.816×). Que el signo se dé vuelta al cambiar de endpoint es la confirmación empírica de que la razón 2 hizo bien en retractarse: un efecto que cambia de signo con el instrumento no está establecido en ninguna dirección. El IC [0.402, 2.130] lo dice solo.

### El defecto de nombre, que no es cosmético

La sección se titula «El efecto mínimo de interés (MDE), **derivado de V6**», y su propia §A3.1.b concluye que **V6 no puede fijar el MDE**. Lo que `8.96` deriva no es V6: es un umbral de **autofinanciamiento** — la ventaja direccional mínima que paga sus propios 25 pb. Es una cantidad razonable y es la única derivable sin depender del camino realizado de SMH; pero **no es el criterio congelado que el proyecto cree estar honrando**, y el título dice que sí. Con el agravante de que el umbral de autofinanciamiento en la escala `gap` describe una **operación de overnight** (cerrar en el cierre previo, abrir en la apertura objetivo), que no es la estrategia contra la que V6 pide comparar (comprar SMH y mantener). Cambiar el endpoint para respetar §A2 fue correcto; el costo, no declarado, es que la derivación pasó a hablar de otra estrategia.

---

## D2 — Si son comparables, ¿cae el efecto observado por debajo del umbral?

**La afirmación que este frente venía a escribir con todas las letras es la que hay que refutar con todas las letras.**

La tentación es aritmética y fuerte: `+6.5 < 6.67`, el efecto observado cae 0.17 pp por debajo del borde inferior del umbral de relevancia; luego «no valdría la pena aunque fuera real». **Eso es una comparación punto contra punto**, y es exactamente el error que este proyecto ya se pilló cometiendo dos veces. Un MDE se compara contra un intervalo, no contra un punto — y aquí hay dos intervalos, no uno.

`δ_obs` y el MDE se estiman sobre **las mismas 248 filas**, así que su diferencia admite bootstrap **pareado**. Nadie lo había hecho. Es la única forma honesta de hacer la pregunta:

| cantidad | punto | IC95 clúster de día (34 días, 10.000 rep., semilla 20260901) |
|---|---|---|
| ventaja observada `δ_obs` | +6.45 pp | **[−10.36, +23.14]** (ancho 33.5 pp) |
| MDE sobre las mismas filas | 7.74 pp | **[4.54, 12.38]** |
| **`δ_obs` − MDE, pareado** | **−1.29 pp** | **[−18.92, +14.90]** — contiene el cero |

`P(δ_obs < MDE)` en el remuestreo = **0.569**. Una moneda ligeramente cargada.

Y contra los umbrales publicados directamente: `P(δ_obs < 6.67 pp) = 0.521`, `P(δ_obs < 8.96 pp) = 0.621`.

**Veredicto D2: la afirmación NO se sostiene y queda refutada.** El experimento no ordena las dos cantidades. Con `n` efectivo ≈ 68 (ICC 0.403, deff 3.63) y toda la información discriminante concentrada en **17 días con un 9-7**, la ventana no puede decir si el efecto está por encima o por debajo de su propio umbral de relevancia. El `0.17 pp` de brecha es **tres órdenes de magnitud más chico que el ancho del intervalo que lo rodea**.

Obsérvese también que el IC del MDE es más angosto que el de `δ_obs` — no porque el MDE se conozca mejor, sino porque **su intervalo mide un insumo de tres** (D1c). Si se le propagaran los otros dos, la comparación sería todavía menos resoluble, nunca más.

**Lo que sí se puede afirmar, y es más chico:** el punto estimado del efecto observado está del lado bajo de su umbral de relevancia, y ni siquiera eso es robusto a la elección de denominador — con el MDE recomputado sobre las mismas filas (7.74 pp) la brecha es 1.29 pp; con el publicado (8.96) es 2.51 pp; con el dedup anclado (9.10) es 2.65 pp. **Ninguna de las tres se distingue de cero.**

---

## D3 — ¿Cuál es la comparación válida?

Son comparables en escala, así que D3 no reemplaza a D2. Pero la comparación válida tiene tres condiciones que hoy no se cumplen, y vale escribirlas porque son la lista de trabajo:

1. **Mismas filas de los dos lados.** O se deduplica el efecto observado también, o el MDE se computa sin deduplicar. Mezclar es lo que hoy se hace. La regla de deduplicación está en `cola_decisiones.md` como decisión abierta de Nicolás; hasta que se cierre, **la comparación se reporta en las tres variantes o no se reporta**.
2. **MDE anclado.** `mde_desde_v6.py` debe cargar por `backtest.linea_base.cargar(hasta_sello=…)`. Un umbral que cambia todos los días no es un umbral.
3. **Intervalo del MDE que propague sus tres insumos**, o —si el supuesto de simetría se quiere mantener como supuesto y no como estimación— que lo declare **fuera** del intervalo y publique la sensibilidad de D1c al lado. Lo que no se puede es publicar `[6.67, 11.32]` como «el intervalo del MDE».

Y una condición de fondo, que ninguna de las tres arregla: **el MDE debería fijarse sobre datos que no son los que después se juzgan.** Hoy `f` y `E|gap|` salen de la misma ventana sellada cuyo efecto se compara contra el umbral que producen. Para un pre-registro cuya población son las filas **posteriores al 2026-08-31** eso es aceptable —el umbral se congela antes de ver esos datos—, pero hay que decirlo: el umbral hereda las peculiaridades de julio-agosto de 2026, incluida la ventana R2.

---

## D4 — La consecuencia sobre las 768 celdas

La pregunta encargada era: ¿alguna de las 768 celdas supera el MDE? Y la hipótesis de trabajo era que ninguna, y que ése sería el titular.

**Por punto estimado, la premisa es falsa** — y hay que decirlo antes que nada:

| umbral | celdas con punto > umbral | IC95 **entero** por encima | IC95 **entero** por debajo | IC95 **contiene** el umbral |
|---|---|---|---|---|
| **6.67 pp** (borde inferior publicado) | **425 / 768** (55.3%) | **0 / 768** | **0 / 768** | **768 / 768** |
| 7.74 pp (MDE, mismas filas) | 359 / 768 | **0 / 768** | **0 / 768** | **768 / 768** |
| **8.96 pp** (MDE publicado) | **274 / 768** (35.7%) | **0 / 768** | **0 / 768** | **768 / 768** |
| 11.32 pp (borde superior publicado) | 152 / 768 | **0 / 768** | **0 / 768** | **768 / 768** |

**El titular es el de la segunda columna, no el de la primera, y es más fuerte que el que se buscaba:**

> **Ninguna de las 768 celdas tiene un intervalo que supere el MDE. Ninguna tiene un intervalo que quede por debajo. Las 768 lo contienen — los cuatro umbrales, en las cuatro columnas.**

Es decir: **ni una sola de las 768 formas legítimas de medir esta ventana puede decidir si el efecto del campeón es económicamente relevante o irrelevante.** No es que el jardín conteste «no»; es que el jardín no contesta. El ancho medio de los IC de la matriz es **37.7 pp** (mínimo 31.5, máximo 53.4), y los cuatro umbrales caben cómodamente dentro de cualquiera de ellos.

Y las dos lecturas hay que ponerlas juntas, porque leídas por separado cada una engaña:

- **«274 de 768 superan el MDE»** invita a concluir que el modelo es relevante en un tercio de los caminos. Es la lectura de punto, y es la que este documento existe para no hacer.
- **«0 de 768 lo superan por intervalo»** invita a concluir que el modelo es irrelevante. También es falsa: 0 de 768 quedan *por debajo* con la misma vara.

Para contexto, el resto de la matriz apunta al mismo lugar: **0/768 celdas con `p_dia < 0.05`**, **1/768 con IC de ventaja que excluya el cero** (y su borde inferior es 0.59 pp), **766/768 con IC que contiene el cero**. Un experimento que no distingue el efecto de cero tampoco lo va a distinguir de 8.96.

### Los dos MDE no son la misma cosa, y su cociente es el resultado

Esto merece su propio párrafo porque se confunden con facilidad y miden cosas opuestas:

| | qué es | valor | de dónde sale |
|---|---|---|---|
| **MDE de relevancia** | el efecto mínimo que **valdría la pena** | 8.96 pp publicado · 7.74 pp sobre las mismas filas | derivación económica de §A3.1.c |
| **MDE de detectabilidad** | el efecto mínimo que el diseño **puede ver** | 18.0 pp al 50% de potencia · **25.0 pp al 80%** | permutación por día en `bifurcaciones.py` |

**El segundo es 2.8× el primero** (por el umbral publicado; 3.2× por el de las mismas filas). Eso es un resultado, no una nota al pie:

> **El diseño no puede detectar el efecto más chico que le importaría.** Hay una franja entera —de ~8 a ~25 pp— de efectos que serían económicamente relevantes y que este experimento, con esta ventana, no vería. La potencia frente al efecto publicado es **11%**, apenas por encima de α.

De ahí se sigue lo único que este frente puede afirmar sin condicionales: **el cero de celdas significativas no es evidencia sobre el modelo. Estaba escrito de antemano por la estructura de los datos.** Y también se sigue por qué el diseño secuencial existe: un umbral de relevancia por debajo del umbral de detectabilidad es la definición formal de «hacen falta más datos».

**Con la reserva que corresponde:** el `18.0` y el `25.0` están publicados en `bifurcaciones.md` **sin intervalo**, lo cual viola la regla 1 de la casa igual que la violaría cualquier otro punto. El código en el árbol de trabajo (`bifurcaciones.py`:1179 y 1337, sin commitear) ya computa `ic50`/`ic80`; **el informe publicado es 9 minutos anterior a ese arreglo y todavía no lo refleja.** Este documento usa el `2.8×` como orden de magnitud, no como cifra, y no debe citarse hasta que el informe se regenere.

---

## Lo que hay que arreglar en el código, no en la prosa

La regla 2 de la casa dice que una retractación en prosa no es una retractación. Tres defectos vivos, ninguno arreglado por este frente porque los tres tocan artefactos de otros:

1. **`GEMELO/SECUENCIAL/mde_desde_v6.py:94-102` sigue sin ancla temporal.** Diagnosticado el 31-ago, listado como una de las cuatro condiciones para levantar el rechazo, no corregido. El `8.96` cambia con el reloj. **Es el defecto grave.**
2. **`GEMELO/bifurcaciones.py:1381` y `:1383` tienen el `8.96` cableado como literal**, y la línea 1383 divide por él (`mde80/8.96`) para producir el «2.8×» que el informe publica. Es exactamente el patrón que el guardián ya cazó («el MDE estaba cableado como string en cinco artefactos»), sobreviviendo en un sexto. No se toca acá porque ese archivo tiene cambios sin commitear de otro frente; **se señala para que lo arregle quien lo tiene abierto.**
3. **`GEMELO/SECUENCIAL/mirada.py:64`**: `MDE_FIRMADO = None  # poner 0.07 (o 0.10) cuando Nicolás firme`. El comentario ofrece firmar el **7 pp que está retirado**. El candado funciona; su instrucción, no.

Y una inconsistencia interna del pre-registro que no es de código: **`DISEÑO.md` §A3.1.c y §A3.1.d siguen presentando `7.13 pp` y «MDE = 7 pp propuesto para firma» como el estado vigente**, contradichos sólo por el bloque de rechazo de las líneas 43-49 y por el acta de congelamiento de la línea 148, que también dice «propuesto 7 pp». Un documento congelado tiene tres valores distintos para su único parámetro abierto, en tres lugares. La regla que el propio documento se dio —«a partir del congelamiento ninguna sección se reescribe; una corrección se agrega como subsección nueva con fecha posterior»— es la que resuelve esto, y todavía no se aplicó.

---

## Lo que este documento NO puede decir

- **No puede decir si el modelo supera el umbral de relevancia.** Ése es el resultado.
- **No puede validar `E|gap|` contra una fuente independiente.** §A3.1.a ya estableció que no existe hoy en el repo una familia de precios distinta con la que contrastar; lo mismo vale para `gap_pct`. Se dice en vez de fabricar una.
- **No puede propagar la incertidumbre de la simetría de magnitudes *dentro* del MDE de forma defendible**, sólo mostrar su sensibilidad. Con la razón A/W indistinguible de 1.0 y de 2.1, un intervalo conjunto sería honesto pero tan ancho que no informaría — y decir eso *es* la información.
- **No puede juzgar si `8.96` es el número correcto para firmar.** La firma es de Nicolás. Lo que este frente aporta es que **`8.96` no es hoy un número reproducible**, y que un parámetro que no reproduce no se firma.

---

## Reglas de la casa aplicadas

- **Ningún estimador puntual sin intervalo.** Wilson para `q` y `f`; bootstrap de bloques de 20 para `E|gap|` y la razón de magnitudes; bootstrap de **clústeres de día** para la ventaja, el MDE y su diferencia pareada. Los intervalos se computan, no se estiman de memoria.
- **El denominador honesto es la baseline sobre las mismas filas**, jamás el 50% ni el cero. Toda la sección D1a existe para verificar precisamente eso.
- **Comparación pareada con McNemar**, con b = 72, c = 56, p exacto = 0.1847 reportados.
- **Bootstrap de bloques, nunca iid** — y donde la unidad real es el día, de clústeres de día, que es más conservador que el bloque de 20 filas (que acá daría [−4.84, +22.58] en vez de [−10.36, +23.14] — cada uno contiene el cero, y el de filas lo hace con 6 pp menos de ancho, que es justamente el angostamiento falso que la regla prohíbe).
- **Una verificación que usa el mismo mecanismo que produjo la cifra no es una verificación.** D1a ataca el lado opuesto de la desigualdad, con insumos (`b`, `c`, las tasas) que no participan del cómputo del MDE.
- **La corrección va al código primero.** Todo lo que este documento afirma sale de `GEMELO/SECUENCIAL/mde_vs_observado.py`, versionado, con self-test.
