# El parche de honestidad — lo que el README no dice todavía

**Este documento NO se aplica.** Es el parche completo, listo para que
Nicolás lo revise y decida qué entra, qué se reformula y qué se descarta.
Ningún archivo de los citados abajo fue tocado.

> **Reemplaza a `GEMELO/resultados/parche_documental.md`, que quedó
> desactualizado.** Aquel se escribió antes de que dos auditorías
> corrigieran `concentracion.md`, y su propuesta de criterio R4 se apoyaba
> en un scan-statistic que después resultó estar mal construido en su
> versión de anchos 3-10. Este documento parte de la v2 corregida y
> desecha esa propuesta. `parche_documental.md` queda como registro
> histórico de la corrida anterior, no como parche vigente.

## El problema, en una frase

El README de hoy publica **+6.5 pp, p=0.1849, n=248** y dice honestamente
que no es distinguible de cero — pero **no dice dos cosas que el propio
proyecto ya midió y registró**:

1. **Toda la ventaja de esa cifra vive en 6 fechas de julio de 2026**
   (bloque 15-23-jul: n=44, +40.9 pp; el resto de la ventana: n=204,
   −1.0 pp). Medido cuatro veces por vías independientes
   (`GEMELO/resultados/concentracion.md` §A1).
2. **El campeón no pasa el criterio de rechazo R2 que el propio proyecto
   escribió** para descartar a un retador — en ninguna de las tres
   convenciones de medición. Registrado desde el 26-ago en
   `GEMELO/DISEÑO.md` §6.2, y actualizado con los datos de hoy en
   `concentracion.md` §A3.

**No es una cifra mal calculada. Es una omisión.** Y en un proyecto cuyo
producto es la honestidad estadística, una omisión pesa más que un error
aritmético: un error se corrige y se publica la errata; una omisión deja
al lector con una impresión que los propios datos del proyecto no
sostienen.

## Cómo quedaría la sección de la ventana sellada, diciéndolo

Propuesta concreta, en el tono del README. Se agrega **después** de la
tabla de la sección "Sellada — la única evidencia point-in-time" (hoy
líneas 122-132), antes de "Otras métricas". No cambia ninguna cifra de la
tabla:

> ### Dónde vive esa ventaja, y por qué importa
>
> El +6.5 pp de arriba no está repartido a lo largo de la ventana:
> **vive entero en seis fechas de emisión de julio.**
>
> | Sub-período | n | Ventaja | McNemar p |
> |---|---|---|---|
> | 15 al 23-jul-2026 (6 fechas) | 44 | **+40.9 pp** | 0.001 |
> | Las otras 28 fechas | 204 | **−1.0 pp** | 0.920 |
> | Ventana completa | 248 | +6.5 pp | 0.185 |
>
> Y el criterio de rechazo **R2** —escrito por este proyecto para
> descartar a un retador cuya ventaja dependa de esa misma ventana—
> **descalifica al campeón**: sin el bloque de julio queda en −1.0 pp
> (`excluir_cero`), +0.5 pp (`estricta`) o −1.9 pp (`verificador`).
> Ninguna de las tres es distinguible de cero. La regla se mantiene tal
> cual, deliberadamente: *que el titular tampoco la pase es un resultado
> sobre el titular, no un defecto del criterio*
> ([`DISEÑO.md` §6.2](GEMELO/DISEÑO.md)).
>
> **Lo que NO se puede afirmar, y se intentó dos veces:** que esa
> concentración sea puro azar. Un scan-statistic corregido por la
> búsqueda da p≈0.52 para el bloque; sin corregir por la búsqueda, 0.04.
> Toda la distancia entre esos dos números es el costo de haber elegido
> la ventana después de verla. Y la diferencia bloque-resto (+41.9 pp)
> tiene un IC95 de [−2.9, +86.0]: **al filo, ni ruido limpio ni señal
> limpia**. Dos corridas de análisis terminaron en el mismo lugar: con
> 248 filas y 34 fechas de emisión, **este track record todavía no tiene
> potencia para decidirlo**
> ([`concentracion.md`](GEMELO/resultados/concentracion.md)).
>
> Por eso existe ahora un
> [diseño secuencial pre-registrado](GEMELO/SECUENCIAL/DISEÑO.md) con
> fecha: **2027-07-17**, con tres miradas intermedias antes, umbrales
> escritos y una regla de futilidad. Es la primera vez que el proyecto
> tiene una fecha en la que va a saber algo, en vez de mirar el número
> cada vez que crece.

El último párrafo importa tanto como los dos primeros: **una limitación
publicada sin un plan para resolverla es una queja; con el plan al lado,
es un instrumento funcionando.** Es el mismo movimiento que el README ya
hizo con la corrección del WS3 (líneas 207-228).

## Los doce bloques que se mueven

La regla de la casa: mover una cifra obliga a mover todas las que
dependen de ella, y moverlas a medias deja una portada internamente
inconsistente. Acá **no se mueve ninguna cifra** — se agrega contexto —
pero el barrido es el mismo, porque el contexto tiene que aparecer en
todos los lugares donde alguien lee la cifra sin él.

| # | Bloque | Archivo:línea | Qué cambia |
|---|---|---|---|
| 1 | TL;DR en inglés | `README.md`:16-17 | Agregar, tras "still not distinguishable from zero", que toda la ventaja vive en 6 fechas y que el campeón no pasa su propio R2 |
| 2 | Badge de la ventana sellada | `README.md`:30 | Badge adicional al lado: `concentración · 6/34 fechas`, o cambiar el color del existente si se define esa convención |
| 3 | Tabla de resultados sellados | `README.md`:124-126 | **Sin cambios en los números.** Solo la nueva subsección debajo |
| 4 | Nueva subsección "Dónde vive esa ventaja" | `README.md`, tras :132 | El texto propuesto arriba |
| 5 | Párrafo de trayectoria | `README.md`:127-131 | Agregar que el ascenso de +4.0 a +6.5 pp no fue parejo: entra casi entero en una racha de seis fechas |
| 6 | Tabla "Otras métricas" | `README.md`:134-139 | Fila nueva, mismo formato que "Régimen: una sola etiqueta": `Concentración temporal / toda la ventaja en 6 de 34 fechas / scan-statistic corregido p≈0.52: no se puede afirmar que sea azar ni que no lo sea` |
| 7 | Sección de roadmap | `README.md`:372 | Agregar el diseño secuencial con su fecha (2027-07-17) como hito verificable |
| 8 | `cifras-canonicas` | `.claude/skills/cifras-canonicas/SKILL.md`:36-43 | La fuente de verdad que toda sesión futura consulta. Sin esto, la próxima sesión —incluida la próxima de este agente— vuelve a citar +6.5 pp sin el matiz |
| 9 | `estadistica-evaluacion` | `.claude/skills/estadistica-evaluacion/SKILL.md`:75-76 | Cita las mismas cifras vigentes como referencia; enlace cruzado a la #8 en vez de duplicar el texto |
| 10 | `estadistico-adversario` | `.claude/agents/estadistico-adversario.md`:47 | El agente que hace estas auditorías tiene que tener el matiz de entrada, no que se lo repitan cada vez |
| 11 | `ESTADO.md` | ya actualizado | Registra la retractación desde la corrida anterior. Verificar que siga coherente tras aplicar 1-10 |
| 12 | `DECISIONES.md` | acta nueva | El acta que registra el parche (borrador abajo) |

**Lo que NO se toca, y por qué:** `backtest/resultados/linea_base/*.md` y
`data/sombra/switch_20260830.md` son reportes fechados, point-in-time,
generados por una corrida concreta. Reescribirlos violaría el mismo
principio que protege las filas selladas: un reporte fechado es un hecho
histórico, no una cifra viva. Si hace falta, se les agrega errata con
fecha posterior en `DECISIONES.md`.

## ¿Hay que revisar algún criterio de GEMELO?

**El argumento, para que Nicolás decida con él y no con una impresión.**

R2 dice: *"el retador se descarta si su ventaja desaparece al excluir la
ventana 15–23 jul, que sostiene casi toda la ventaja del campeón"*. La
premisa fáctica es correcta y está medida. Pero hay un problema de
construcción que las dos corridas de análisis dejaron a la vista:

**Esa ventana se eligió porque se veía extrema.** El scan-statistic
corregido por búsqueda (p≈0.52) dice que encontrar una ventana de 6
fechas así de extrema, entre 34 fechas, es lo que pasa la mitad de las
veces por azar. Y la contigüidad no aporta nada: elegir 6 fechas
cualesquiera al azar, sin exigir que sean consecutivas, da el mismo p
(0.042 contra 0.042). **Entonces R2 congela, como vara permanente, una
ventana de fechas que no está establecida como especial.**

Dos lecturas legítimas, y la elección es de Nicolás:

- **Dejar R2 como está.** Es un criterio conservador: solo descarta,
  nunca aprueba. Una vara demasiado estricta produce falsos negativos
  (rechazar un retador bueno), que en este proyecto es el error barato:
  el campeón se queda, no pasa nada. Y bajarla ahora, justo cuando se
  descubrió que el campeón tampoco la pasa, es exactamente la clase de
  movimiento que un pre-registro existe para impedir.
- **Reformularla sin ablandarla:** en vez de una ventana de fechas fija
  elegida post-hoc, exigir que la ventaja del retador sobreviva al
  recorte de **su propio** bloque más favorable, identificado con el
  mismo procedimiento para todos (así se compara peras con peras y no
  depende de una fecha que se eligió mirando al campeón). Eso es
  **igual de estricto o más**, y no hereda el problema de construcción.
  `GEMELO/RELEVO.md` ya tiene un REL-V5 que apunta en esa dirección.

**Marcado como decisión de Nicolás.** Los criterios congelados no se
mueven por conveniencia — pero descubrir que la vara no era lo que se
creía tampoco es conveniencia. La diferencia entre las dos cosas es
quién decide y con qué argumento a la vista; por eso el argumento está
escrito acá entero, con el número que lo sostiene, y la decisión no se
toma en este documento.

## El acta, redactada y lista para aprobar

**Este acta NO está vigente y NO se agregó a `DECISIONES.md`.** Es el texto
que se copiaría tal cual si Nicolás aprueba el parche completo. Mientras no
haya aprobación, vive únicamente acá, en `GEMELO/resultados/parche_honestidad.md`,
condicionado por entero a esa decisión.

---

## §XX — Parche de honestidad del README: la concentración de julio y el R2 no superado (`GEMELO/resultados/parche_honestidad.md`)

**Fecha:** a completar el día de la aprobación (número de sección a asignar
en ese momento; el resto del archivo usa numeración correlativa).

**Qué se decidió.** Publicar en el README dos hechos que el proyecto ya
había medido y no decía: que toda la ventaja de la ventana sellada vive en
seis fechas de julio de 2026, y que el campeón no supera su propio criterio
de rechazo R2 en ninguna de las tres convenciones de medición del proyecto.

**Por qué.** El README publicaba, para la ventana sellada, +6.5 pp, McNemar
p=0.1849, n=248, con la honestidad correcta de decir que esa cifra no es
distinguible de cero. Lo que no decía es que la cifra completa depende, casi
en su totalidad, de un bloque de seis fechas. Medido cuatro veces por vías
independientes (`GEMELO/resultados/concentracion.md`, §A1): el bloque del 15
al 23 de julio de 2026 (n=44) da +40.9 pp, McNemar p=0.001; el resto de la
ventana (n=204, las otras 28 fechas) da −1.0 pp, p=0.920.

Sobre esa misma base, el criterio de rechazo R2 (`GEMELO/DISEÑO.md`, §6.2,
registrado desde el 26 de agosto y actualizado en `concentracion.md`, §A3)
descalifica al campeón en las tres convenciones de medición del proyecto:
−1.0 pp bajo `excluir_cero`, +0.5 pp bajo `estricta`, −1.9 pp bajo
`verificador`. Ninguna de las tres es distinguible de cero.

Ninguna de estas dos cifras es nueva ni corrige un cálculo previo: las dos
ya estaban en el repositorio, fechadas, medidas con el mismo rigor que el
proyecto exige para todo lo demás. Lo que no había era que el README, la
vitrina pública, las dijera. No es una cifra mal calculada, es una omisión
de contexto, y en un proyecto cuyo producto es la honestidad estadística esa
distinción importa: un error se corrige y se publica la errata, mientras que
una omisión deja al lector con una impresión que los propios datos del
proyecto no sostienen.

**Qué NO se puede afirmar, con el mismo peso que lo anterior.** Que esa
concentración sea puro azar. El scan-statistic corregido por la búsqueda de
la ventana da p≈0.52; sin corregir por esa búsqueda, da 0.04. Toda la
distancia entre esos dos números es el costo de haber elegido la ventana
después de haberla visto extrema. La diferencia entre el bloque y el resto
de la ventana (+41.9 pp) tiene un intervalo de confianza al 95%, por
bootstrap circular de bloques, de [−2.9, +86.0]: al filo, ni ruido limpio ni
señal limpia. El proyecto no toma partido entre "hay una condición de
mercado identificable" y "es una racha de azar" (ver también la
retractación del §45 sobre este mismo punto): ambas lecturas quedan
abiertas, y el README lo dice así de explícito.

**Qué se descartó y por qué.** Mover alguna de las cifras publicadas en el
README: se descartó de plano, porque ninguna estaba mal calculada. Mover un
número correcto para acomodar una narrativa sería exactamente el error que
este parche existe para evitar. Lo que se agrega es contexto, en los doce
bloques que este mismo documento enumera más arriba (seis puntos del
README, dos skills del proyecto, un agente, `ESTADO.md` y esta acta), sin
tocar ninguna cifra de ninguna tabla.

También se descartó resolver, dentro de esta misma acta, si el criterio R2
debe reformularse: el argumento existe y está completo, pero la decisión no
se toma acá (ver "Qué queda abierto").

Este acta, una vez aprobada, reemplaza a `GEMELO/resultados/parche_documental.md`,
que quedó desactualizado: se había escrito antes de dos auditorías que
corrigieron `concentracion.md`, y su propuesta de un criterio R4 se apoyaba
en un scan-statistic que después resultó estar mal construido en su versión
de anchos 3 a 10. `parche_documental.md` queda como registro histórico de
esa corrida anterior, no como parche vigente.

**Qué queda abierto.** Si el criterio R2 debe reformularse queda,
explícitamente, como decisión de Nicolás, no resuelta por esta acta. El
argumento completo vive en `GEMELO/resultados/parche_honestidad.md`, con dos
lecturas legítimas: (a) dejar R2 tal como está, por ser un criterio
conservador que solo descarta y nunca aprueba, de modo que ablandarlo justo
cuando se descubre que el propio campeón tampoco lo pasa sería el tipo de
movimiento que un pre-registro existe para impedir; (b) reformularlo sin
ablandarlo, exigiendo que la ventaja de cualquier retador sobreviva al
recorte de su propio bloque más favorable (identificado con el mismo
procedimiento para todos los candidatos), en vez de depender de una ventana
de fechas fija elegida después de haberla visto extrema, que el
scan-statistic no logra establecer como especial (p≈0.52 corregido por
búsqueda). Ambas lecturas son legítimas y esta acta no elige entre ellas.

Tampoco resuelve si la concentración de julio corresponde a una condición
de mercado identificable o a una racha de azar (ver §44 y §45): el diseño
secuencial descrito abajo existe justamente porque hoy no hay potencia
suficiente para decidirlo.

**Deuda declarada, y por qué existe un plan al lado de la limitación.** El
proyecto venía mirando la misma cifra de la ventana sellada cada vez que
crecía, sin declarar cada mirada como un intento independiente: un pasivo
de al menos 12 miradas no declaradas, que infla el error de tipo I real a
0.091 (frente al 0.05 nominal, aproximadamente 1.8 veces). Esto nunca
produjo un falso positivo publicado: el p más chico observado en cualquiera
de esas miradas fue 0.1158. Pero que no haya hecho daño hasta ahora no es
evidencia de que el procedimiento sea sano, y por eso existe
`GEMELO/SECUENCIAL/DISEÑO.md`: un diseño secuencial pre-registrado, con
fecha de decisión final el 9 de julio de 2027 y tres miradas intermedias
antes de esa fecha, cada una con su propio umbral escrito de antemano. Es la
primera vez que el proyecto tiene una fecha en la que va a saber algo, en
vez de mirar el número cada vez que crece.

**Cómo se revierte.** Mientras esta acta no esté aprobada, es un borrador
dentro de `GEMELO/resultados/parche_honestidad.md` y se puede reescribir
libremente. Si Nicolás aprueba el parche y esta acta se copia a
`DECISIONES.md`, queda sujeta a la misma regla que todo lo demás en ese
archivo: la frontera de la errata es el commit. Antes de comitear la copia,
cualquier ajuste se corrige directamente en el sitio; una vez comiteada y
publicada, una corrección posterior se documenta como errata fechada, nunca
como reescritura del acta original.
