# Parche documental — consecuencias de la concentración de julio

**Este documento NO se aplica.** Es el parche completo, listo para que
Nicolás lo revise y decida qué entra, qué se reformula y qué se descarta.
Ningún archivo de los citados abajo fue tocado por este frente.

Depende de `GEMELO/resultados/concentracion.md` (Frente A, todavía en
revisión adversaria al escribir esto). Si esa revisión cambia el veredicto
de fondo, este parche se actualiza antes de proponerse — no se aplica un
parche basado en un hallazgo que la revisión haya tumbado.

> **ACTUALIZACIÓN: la revisión SÍ cambió el veredicto de fondo — este
> documento quedó DESACTUALIZADO, no se aplica tal cual.**
> `estadistico-adversario` y `auditor-lookahead` encontraron defectos
> serios en la v1 de `concentracion.md` (desglose por bolsa invertido,
> scan-statistic mal construido, y sobre todo: el criterio de la
> hipótesis condicional A4-A5 se evaluó contra un umbral distinto del
> pre-registrado, desviación no declarada que invertía el resultado). La
> v2 de `concentracion.md` retracta la conclusión "es puro azar" y la
> reemplaza por un veredicto más incómodo: la evidencia de hoy no
> alcanza para decidir entre "hay una condición" y "es azar". El bloque
> "R4 propuesto" de este parche (más abajo) está construido sobre el
> scan-statistic que resultó estar roto en su versión de anchos 3-10 —
> hay que revisarlo contra la versión corregida (ancho fijo) antes de
> proponérselo a Nicolás. **No se reescribió el resto de este documento
> por presupuesto de la corrida — queda marcado como pendiente de
> revisión, no como vigente.**

## Por qué hace falta un parche y no una corrección

**Las cifras del README no están mal.** 66.1%, 59.7%, +6.5pp, p=0.1849,
n=248: todas se recalculan hoy y dan exactamente eso. Lo que falta no es
una cifra — es la advertencia de que esa cifra, sola, invita a leer "el
modelo tiene una ventaja pequeña pero constante" cuando la evidencia de
`concentracion.md` dice que la ventaja observada es, con lo que hay hoy,
indistinguible de una racha de seis fechas sobre 34. Es el mismo patrón que
ya vivió el proyecto con la "contaminación por revisión" del WS3 (README
§"Larga", líneas 144-159): una limitación que en su momento no se conocía
del todo, corregida con fecha y sin vergüenza cuando se conoció.

## Bloques que se mueven — listados uno por uno

### 1. TL;DR en inglés (`README.md`, líneas 9-19)

**Hoy:**
> On the point-in-time sealed window (n=248) the edge is +6.5 pp with p =
> 0.1849: still not distinguishable from zero.

**Parche propuesto** (agrega una frase, no borra nada):
> On the point-in-time sealed window (n=248) the edge is +6.5 pp with p =
> 0.1849: still not distinguishable from zero — and a scan-statistic audit
> found that the entire advantage lives in a single 6-date window
> (15–23 Jul 2026), a concentration indistinguishable from chance under a
> block-permutation test (p≈0.55). See "Where the sealed edge actually
> lives" below.

### 2. Badge de la ventana sellada (`README.md`, línea 30)

**Hoy:** `ventana sellada · +6.5 pp · p=0.18 · n=248` (color ámbar).

**Parche propuesto:** el badge en sí no tiene espacio para matices — se
propone agregar, inmediatamente después, un badge chico adicional:
`concentración · 6/34 fechas · p≈0.55 (azar)`, mismo estilo visual que el
resto, para que nadie lea solo el primer badge y se quede con la lectura
incompleta. Alternativa más simple: cambiar el color del badge existente de
ámbar a un tono que ya señale "bajo escrutinio" (si el proyecto tiene esa
convención de color en otro lado — no se encontró una, así que esto
requeriría definir una).

### 3. Encabezado e intro de "Sellada" (`README.md`, líneas 114-120)

**Hoy:** "Emitida antes del hecho... la única evidencia point-in-time."

**Parche propuesto:** sin cambios en la frase — sigue siendo cierto que es
la única evidencia point-in-time. El matiz va en el bloque 5 (nueva
sección), no acá.

### 4. Tabla de resultados sellados (`README.md`, líneas 122-126)

**Sin cambios en los números.** Se recomiendan solo si Nicolás decide
adoptar una convención nueva de reporte (ver bloque 6 sobre R2/V-nuevo) —
hasta entonces, la tabla queda igual y el matiz vive en el texto alrededor.

### 5. Párrafo de "trayectoria" (`README.md`, líneas 127-131)

**Hoy:**
> Y que se vea que se mueve: el 25-ago, con n=223, era +4.0 pp con p =
> 0.4633. Cinco días y 25 filas después la ventaja subió 2.5 pp y el p
> bajó a menos de la mitad. Sigue sin cruzar el 5%, y se publica igual —
> con su fecha, para que dentro de tres meses se pueda leer la trayectoria
> y no solo el último número.

**Parche propuesto** (agrega una frase al final, seguir la misma lógica de
"se publica igual, con su fecha"):
> [...] para que dentro de tres meses se pueda leer la trayectoria y no
> solo el último número. **El 31-ago, una auditoría encontró que ese
> movimiento —de +4.0 a +6.5 pp— no fue un ascenso parejo: toda la
> ventaja de estas 248 filas vive en una sola racha de seis fechas de
> emisión (15 al 23 de julio, +40.9 pp ahí; −1.0 pp en las 28 fechas
> restantes). Un test de permutación no distingue esa racha de una
> coincidencia estadística (p≈0.55). Detalle completo en
> `GEMELO/resultados/concentracion.md`.**

### 6. "Otras métricas" — tabla y caveat (`README.md`, líneas 134-139)

**Parche propuesto:** agregar una fila, mismo formato que "Régimen: 1 sola
etiqueta... la columna no tiene varianza":

> | Concentración temporal | toda la ventaja en 6/34 fechas | scan-statistic p≈0.55: no distinguible de azar |

### 7. Nueva sección dedicada — "Dónde vive la ventaja sellada"

Siguiendo el precedente exacto del propio README (DECISIONES.md §35.5: "Va
en el README con sección propia. Es la clase de cosa que un README suele
omitir, y es justo la que sostiene el resto de sus afirmaciones"), este
hallazgo pide su propia sección, no un footnote. Ubicación propuesta:
inmediatamente después de la sección "Sellada" (después de la línea 132),
antes de "Larga". Contenido: la tabla del bloque vs. resto de
`concentracion.md` §A1, el resultado del scan-statistic de §A2, la cita
textual de R2/§6.2 de `GEMELO/DISEÑO.md` (la ironía de A3, ya reconocida
por el proyecto el 26-ago) y el veredicto de §A6, con el mismo tono que el
resto del README: mide, declara, no se disculpa.

### 8. `.claude/skills/cifras-canonicas/SKILL.md`

Es la fuente de verdad que toda sesión futura consulta antes de citar una
cifra — si no se actualiza, cualquier sesión futura (incluida yo mismo en
la próxima corrida) va a citar +6.5pp sin el matiz. Agregar, en la sección
"La ventana sellada", una línea: "**Concentración declarada (31-ago):**
la ventaja completa vive en 6 fechas (15-23-jul); ver
`GEMELO/resultados/concentracion.md`. No cambia las cifras de la tabla,
cambia cómo se leen."

### 9. `.claude/skills/estadistica-evaluacion/SKILL.md` (líneas 75-76)

Mismo argumento que el bloque 8: cita la misma cifra vigente como
referencia de auto-verificación del módulo. Agregar una línea equivalente
o un enlace cruzado a la skill de `cifras-canonicas` en vez de duplicar el
texto.

### 10. `.claude/agents/estadistico-adversario.md` (línea 47)

Cita la cifra vigente como ancla de ejemplo para el propio agente
adversario — el agente que en esta misma corrida encontró la
concentración (indirectamente, revisando `dos_ventanas.md`). Actualizar
para que el propio agente que hace estas auditorías tenga el matiz
presente de entrada, no que dependa de que alguien se lo repita cada vez.

## Lo que NO se toca — y por qué

- `backtest/resultados/linea_base/linea_base_excluir_cero.md` y
  `data/sombra/switch_20260830.md`: son reportes fechados, point-in-time,
  generados por una corrida específica. Reescribirlos violaría el mismo
  principio que protege las filas selladas — un reporte fechado es un
  hecho histórico ("esto es lo que decía el 30-ago"), no una cifra viva.
  Si hace falta, se les agrega una errata con fecha posterior en
  `DECISIONES.md`, nunca se editan en el archivo mismo.
- Las filas de `senales.db`: no aplica, nada de esto toca una fila
  sellada. La concentración es una LECTURA de filas ya selladas, no un
  cambio de ninguna de ellas.

## ¿Algún criterio de GEMELO (V1-V7, R1-R3) tiene que revisarse?

**No hace falta bajar ni subir ningún criterio existente — R2 ya está
haciendo exactamente su trabajo.** R2 fue escrito para descartar a un
retador cuya ventaja desapareciera al excluir el bloque 15-23-jul, y el
26-ago el propio proyecto ya lo aplicó al campeón y decidió no ablandarlo.
Este frente no descubre un hueco en R2 — lo confirma funcionando.

**Lo que SÍ vale la pena que Nicolás considere, como criterio NUEVO, no
como reemplazo de ninguno existente** — decisión suya, no de este
documento:

> **R4 (propuesta) — la ventaja no sobrevive un test de concentración
> temporal.** Si un scan-statistic (máximo de la ventaja sobre cualquier
> ventana contigua de fechas, contra una nula de permutación) no puede
> distinguir el mejor bloque de la serie de lo que produciría el azar
> (p > 0.05, o el umbral que se fije), la ventaja agregada no cuenta como
> evidencia de una señal repetible — sea del campeón o de un retador.

**Por qué esto no es "mover la barra hasta donde ya está el que queremos
aprobar"** (la razón por la que el proyecto se resiste, con razón, a
ablandar criterios): R2 ya es más estricto que esta propuesta y el
campeón tampoco lo pasa — R4 no bajaría ni subiría nada respecto al
campeón, describiría con más precisión el MISMO defecto que R2 ya
detecta, en una forma que generaliza (no depende de saber de antemano cuál
es "el bloque sospechoso", lo encuentra buscando entre todos). Es una
mejora de instrumento, no un ajuste de vara. La palabra final —si se
adopta, con qué umbral, y si reemplaza o complementa a R2— es de Nicolás.

## El acta, redactada y lista para aprobar

*(Para que `escriba-decisiones` la use tal cual si Nicolás aprueba este
parche — no se despachó a escribirla en `DECISIONES.md` porque este
documento entero está condicionado a su aprobación.)*

> **Sección propuesta — "Errata: la ventaja sellada no es constante,
> vive en 6 fechas."** Fecha: [la que Nicolás apruebe]. Un scan-statistic
> sobre las 34 fechas de emisión de la ventana sellada (`excluir_cero`,
> n=248) encontró que el 100% de la ventaja agregada (+6.5pp) proviene de
> 6 fechas del 15 al 23-jul-2026 (n=44, +40.9pp); el resto de la ventana
> (n=204, 28 fechas) da −1.0pp. Un test de permutación (5.000 réplicas)
> no distingue ese bloque de lo que produce el azar sobre una serie de 34
> observaciones ruidosas (p≈0.55). El mismo patrón se repite en la
> ventana larga reconstruida (p≈0.42 sobre 2.031 fechas). Una hipótesis
> condicional pre-registrada (`GEMELO/CONDICIONAL/DISEÑO.md`) encontró una
> señal de magnitud genuina pero ya conocida (§2.4) que además falla en
> predecir julio específicamente. Ninguna cifra publicada estaba mal
> calculada; la lectura de "ventaja constante" no sobrevive esta
> auditoría. Detalle completo en `GEMELO/resultados/concentracion.md`.
> No se tocó `motor.py` ni ninguna fila sellada. El README se actualiza en
> los puntos listados en `GEMELO/resultados/parche_documental.md`.
