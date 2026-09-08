## 82. Seis firmas de Nicolás del 7-sep-2026, y el presupuesto que quedó abierto por un censo hecho para otro rango

**BORRADOR.** Este archivo es una propuesta de acta escrita por asistencia. No
es el acta hasta que Nicolás la revise, la corrija donde haga falta y la pegue
en `DECISIONES.md`. Las cifras que aparecen se leen de `cifras.py` antes de
pegarse; ninguna se cita desde acá.

Contexto: sesión de lectura del 7-sep-2026, después del cierre de la ventana de
sellado. Las decisiones se tomaron con las tarjetas de `espera_firma.md` y
`cola_decisiones.md` a la vista, y con hallazgos de código que no estaban en
ninguna tarjeta. El inventario completo de lo que quedó abierto está en
`GEMELO/resultados/inventario_abierto_2026-09-07.md`.

### 82.1 §45: dos contadores declarados por separado, y el aviso va también donde el número se publica

**Decidido: opción (a), y con alcance ampliado.**

`N_INTENTOS_RIEL_LARGO = 3` cuenta **especificaciones** (L1, L2, L3). La familia
de contrastes que gobierna la multiplicidad son **30**, y eso el ejecutable ya
lo computa desde el §81.3: `dinero/senal_larga_reporte.py` publica la
corrección de Holm sobre los 30 salga lo que salga.

Los dos números se declaran por separado y ninguno reemplaza al otro. La
decisión **no cambia una línea de código**: escribe lo que el ejecutable ya
hace.

**Razón de Nicolás, que es la que manda y va más allá de la taxonomía:** un
lector del repositorio que ve un 3 solo se lleva una idea equivocada de cuánto
se buscó. La coherencia entre documento y ejecutable no es un fin en sí; el fin
es que quien lea después no se enrede.

**Alcance:** por esa misma razón, el aviso **no va sólo a esta acta**. Donde el
3 aparezca publicado tiene que aparecer al lado que la multiplicidad que
gobierna el resultado se computa sobre 30. Si el lector tiene que venir hasta
`DECISIONES.md` para entender el número, la decisión no cumplió su propio
objetivo.

**Lo que sigue prohibido:** dejar el 3 solo, sin decir sobre qué se computa la
multiplicidad. Era la única opción que la propia tarjeta declaraba
indefendible, y era la que regía por omisión.

### 82.2 §26 y §1: el parche de `snapshot.py:140` se aplica entero, con bump, con guardia y con conteo

**Decidido: las cuatro partes.**

**(a) Se aplica el diff.** `sesion_objetivo` pasa a calcularse desde
`available_at`, o sea desde cuándo era conocible el insumo, en vez del reloj de
pared del proceso.

La razón principal no es que deje de producir filas mal apuntadas. Es lo que se
encontró leyendo el código en esta sesión: **la regla maestra del proyecto no
puede disparar mientras el defecto exista.** `senales.py:325` compara
`emitida >= apertura` donde `apertura` es la de `sesion_objetivo`, y
`sesion_objetivo` se elegía por ser la primera que abre después del mismo
instante de emisión. La condición es falsa por construcción. Empíricamente: **0
filas en `no_verificable_timing` sobre 295**. La garantía sobre la que descansa
el track record entero era hasta hoy una tautología. El parche es lo que la
vuelve operativa por primera vez.

**(b) Con bump de `PLATAFORMA_VERSION`.** Razón de Nicolás: orden y
legibilidad. Cada fila nueva lleva grabado de qué lado del corte está, sin que
nadie tenga que acordarse. La alternativa obligaba a anotar a mano el
`timestamp_utc` del primer sello posterior, esa misma noche.

**Esto no reinicia el track record.** `MODELO_VERSION` sigue en 4.6.0. Los dos
versionados están separados a propósito.

**(c) Con guardia.** Esta parte **no estaba en el menú del §26**; venía del §1 y
se había perdido, y el hallazgo que la justifica salió del código en esta
sesión.

El defecto tiene una vía de escape: `available_at` arranca valiendo
`ts_emision` y sólo se reemplaza por el cierre de NYSE dentro de un `try` cuyo
`except` es `pass`. Si `sox_fecha` viene vacío o `cierre_utc` falla, **el parche
aplicado se comporta idéntico al defecto y no deja marca**. Los seis tests del
expediente pasan los dos por el camino feliz.

**Razón de Nicolás:** esa alarma puede ser la diferencia entre perder de vista
un error importante.

**Corrección a la premisa que acompañó la decisión, y se escribe porque el
proyecto registra sus propios errores de razonamiento:** durante la sesión se
argumentó que el equipo corriendo 24/7 como servidor, sin actualizaciones en la
ventana de sellado, evita que el problema vuelva. Eso vale para los sellos
tardíos causados por el DarkWake, cuya causa última el forense no pudo
determinar. **No vale para los dos casos que producen las 15 filas del 82.3:**
ocho vienen de un sello manual con casi tres días de atraso, o sea de una
persona, y siete de que el snapshot del 2026-08-06 perdió el 100 % de sus
predicciones, o sea de la fuente. Ninguna de las dos la previene un servidor.
La decisión no cambia; la razón que la sostiene sí.

**(d) Se cuenta cuántas filas pasaron por la rama del `except`.** Nadie lo sabe
hoy. Si son cero, el agujero es teórico. Si no son cero, hay filas cuyo
`available_at` es reloj de pared, que es un problema distinto de las 25 y que
nadie ha contado. Es cómputo, no firma, y va a la corrida 11.

### 82.3 2a-ter: se retiran las 15 filas, y la razón no es el número

**Decidido: se retiran de las métricas.**

Son 15 predicciones evaluadas contra una sesión que no era la suya. Ocho del
2026-07-05, que apuntan a 07-06 cuando debían apuntar a 07-03, por un sello
manual con casi tres días de atraso. Siete del 2026-08-05, que apuntan a 08-07
cuando debían apuntar a 08-06, porque el snapshot del 08-06 tuvo caída total de
datos.

**Texto de Nicolás, que es el criterio:** *«Se eliminan las 15 filas que fueron
evaluadas por error, no porque nos favorezca, sino porque sin mirar el
resultado, provienen de un error, y en este proyecto no nos regiremos por
errores.»*

**Por qué el argumento se sostiene sin el número.** En el caso del 5-jul la
sesión correcta ya había cerrado al sellar. Esas filas no las descarta un
criterio nuevo: **las descarta la regla maestra que el proyecto tiene desde la
Etapa 4.6**, y que hasta el 82.2 no podía dispararse. El argumento es anterior
al cómputo y no depende de él.

**Lo que hay que declarar igual, y con firmeza.** El retiro favorece al
proyecto, y es la tercera corrección consecutiva que empuja el resultado para
el mismo lado: la prohibición de `keep="last"`, la regla firmada del 3-sep, y
ésta. La explicación mecánica no requiere suponer nada turbio, y es que una
fila puntuada contra el día equivocado pierde sistemáticamente contra una
baseline direccional en un mercado que sube más veces de las que baja. La tasa
de acierto de la baseline sobre estas 15 no se distingue de su tasa
incondicional bajo un intervalo por fila, y ese intervalo es optimista porque
trata 15 filas de dos días como independientes cuando el proyecto mide DEFF
3,55. **Compatible con azar no es lo mismo que demostrado**, y con n = 15 sobre
dos días no se puede exigir más.

**Consecuencia de calendario, que la firma no cambia.** La rama de coherencia
**no se publica** hasta que tenga su intervalo de clúster de día computado. La
tercera regla de la casa manda: hasta entonces es una consecuencia declarada y
no un argumento. El cómputo va a la corrida 11.

**Predicción escrita antes de computarlo, para que la revisión sea legítima:**
es esperable que ese intervalo contenga el cero, como lo contiene el de la
regla firmada.

### 82.4 §42: la cuenta en papel se reconstruye, y la tarjeta se corrige antes

**Decidido: opción A, reconstruir.**

**Razón de Nicolás:** descartarla plantea un problema futuro y reemplazarla por
algo más chico es una solución a medias. La tarjeta agrega la razón estructural:
una vara declarada en un pre-registro y nunca evaluada envenena la regla de
refutación que la nombra.

**Corrección obligatoria a la tarjeta, previa a ejecutar.** La columna de la
opción A afirma que el signo de la conclusión ya se sabe que aguanta y cita un
movimiento del 27 % al 57 % en el juego medio. **Esas cifras son de la cuenta
con las cuatro fugas y están retiradas**; ninguna cifra de esa página se puede
citar. Y afirmar hacia dónde se va a mover un resultado antes de recalcularlo
es la posición desde la cual una reconstrucción se acomoda sola a lo esperado.
**Esa frase se saca antes de que ningún agente lea la tarjeta.**

**Orden de ejecución, fijado por el `auditor-lookahead` y no alterable:** el
test de truncación primero, y ya está escrito. Después membresía acotada por
fecha, sorteo desde datos anteriores a la ventana, retardo de implementación en
las dos patas, sigma del interruptor sin futuro, y cablear `ErrorLookAhead` al
riel. Recién después republicar. **No se calcula un solo MAE antes de que el
auditor corra.**

**Nota derivada del insumo del §40 del mismo día:** si la cuenta reconstruida
vuelve a producir una fricción del orden de la mitad del capital, el sospechoso
principal es el número de operaciones del diseño y no el arancel. Con 0,70
dólares de ida y vuelta sobre 100, llegar a esa proporción requiere del orden de
ochenta idas y vueltas, y el horizonte declarado del riel es de semanas.

### 82.5 §55: se declara con qué test se computó cada p, y no se mueve ninguna cifra

**Decidido: opción A.**

El README publica un p para la ventana sellada y el módulo árbitro
(`evaluacion.mcnemar_exact`) devuelve otro sobre el mismo par de discordantes.
**Ninguno de los dos está mal:** uno es el χ² de McNemar con corrección de
continuidad de Edwards y el otro es la prueba exacta. Son tests distintos, los
dos legítimos.

**Razón de Nicolás:** al no estar ninguna mal, basta con decir cuál se usó.

No se migra nada y no se mueve ninguna cifra publicada. Lo que se agrega es la
declaración del método al lado de cada p.

**Cabo que esto puede cerrar de paso, sin darlo por hecho:** el traspaso de la
corrida 10 y `espera_firma.md` difieren en el p titular y en el último decimal
del intervalo. La hipótesis es que sea esta misma pareja de rutas. Hay que
confirmarlo contra `cifras.py`, no suponerlo.

### 82.6 §41: los dos registros de intentos quedan separados, y el riel integrador se descarta

**Decidido: opción 1, separados.** Cada familia deflacta por sus propios
intentos. `dinero/registro_intentos.N_INTENTOS_RIEL_LARGO` y
`GEMELO/relevo_asiatico.N_INTENTOS_ACUMULADO` no se suman.

**El argumento que la sostiene** es el de la tarjeta y es sustantivo: los dos
rieles no comparten estimando, ni horizonte, ni universo. Uno prueba hipótesis
sobre el gap de una noche en Tokio, Taipéi y Seúl; el otro sobre retornos a 20
y 60 días hábiles de instrumentos de Estados Unidos. El DSR deflacta por
intentos sobre **la misma** búsqueda, y éstas no lo son.

**Lo que NO es argumento y se declara para que nadie lo use después.** La
tarjeta menciona que mover `N_INTENTOS_ACUMULADO` dispara la regla de los doce
bloques dependientes. Eso es un costo operativo, no una razón epistémica, y
esta decisión **no se apoya en él**. Si el argumento sustantivo cayera, el costo
de los doce bloques no lo sostendría.

**Y el reconocimiento incómodo, con la misma firmeza que el resto.** La opción
fusionada es, por texto de la propia tarjeta, la lectura conservadora y la que
más cuesta pasar. Separados es la opción **menos exigente** de las dos. Se
elige por el argumento de arriba y no por ser la más cómoda, y se deja escrito
que es la más cómoda para que la revisión futura tenga el dato.

**Condición de revisión, declarada antes y no después.** Si alguna vez el
proyecto formula, publica o deja implícita una pregunta que abarque a los dos
rieles a la vez, del tipo «¿la cadena de semiconductores es predecible?»,
entonces bajo esa lectura los dos DSR están inflados y **esta decisión hay que
revisarla antes de calcular cualquier DSR**, no después de verlo. El vínculo ya
está escrito en `dinero/registro_intentos.FAMILIA_HERMANA` para que la pregunta
no se pierda.

**El riel integrador se descarta, y se registra el porqué.** Durante la sesión
se propuso un tercer riel que estudiara la relación entre los dos y fuera
sumando los rieles independientes a medida que aparecieran. Se descartó por dos
razones. La primera es que sumar los intentos de los rieles **es** la opción
fusionada, o sea la contraria a la que se acaba de firmar; se llegaría a ella
por otra puerta. La segunda es estadística: un riel que estudia la relación
entre dos rieles sólo puede formularse después de ver los resultados de ambos,
así que toda hipótesis suya nace mirando lo que ya salió, y tendría que nacer
con registro propio, con la declaración de ser posterior a lo que estudia, y
con una corrección **más dura** que la de cualquiera de los dos, no más blanda.

Se escribe acá, y no se borra, porque una propuesta descartada con su razón
vale más que una propuesta que nunca se escribió: si alguien la vuelve a
proponer, va a encontrar por qué se cayó.

### 82.7 Lo que esta sesión dejó abierto, y por qué

**El presupuesto del riel de dinero.** Nicolás eligió fracciones, por la razón
correcta de que hay instrumentos cuya unidad entera no cabe en un presupuesto
chico. Pero el censo de 7 de 36 instrumentos alcanzables **se computó con piso
de 100 dólares**, y el presupuesto declarado subió a un rango de 500 a 1000. A
ese tamaño el censo es otro y nadie lo computó. La decisión queda pendiente
hasta que la corrida 11 regenere `docs/universo_operable.md` con el modo de
compra como parámetro y el presupuesto real.

**Y una cuestión que precede a todo lo anterior:** apareció un tercero
dispuesto a aportar capital. `REGLAS_DE_CAPITAL.md` establece cero deuda y
capital **enteramente discrecional**, y que el plazo de recuperación nunca es
insumo del dimensionamiento. Capital de un tercero no cumple esa condición
aunque el tercero acepte perderlo: trae un plazo implícito y una asimetría de
consecuencias que es exactamente la presión que esas reglas existen para
excluir.

Además hay una pregunta que este proyecto no puede responderse solo: qué
requisitos regulatorios tiene en Chile operar con fondos de terceros. No es un
detalle que se resuelva con un acuerdo de palabra.

**Y el hecho que manda sobre todo esto:** al 7-sep-2026 el riel de dinero no
tiene ninguna ventaja medida, cero filas selladas prospectivas, la cuenta en
papel retirada y su única señal refutada por su propia regla pre-registrada.
**Nada de lo que existe hoy justifica capital de un tercero.** Lo que el
proyecto necesita de acá a la corrida 12 son filas selladas prospectivas de
tamaño cero, y ésas cuestan cero pesos.

El escalonamiento se firma con capital propio y con el rango original. El
aporte de un tercero, si va, entra en una etapa donde haya algo medido, con
`REGLAS_DE_CAPITAL.md` enmendado **antes** y no después.
