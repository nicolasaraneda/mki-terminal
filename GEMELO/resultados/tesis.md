# La tesis de MKI Terminal — ¿sigue viva, y qué haría falta?

> **Procedencia.** Documento escrito por el agente `director-programa` en la
> séptima corrida autónoma (2-sep-2026, ~02:20 Chile), a pedido de la corrida
> y con la pregunta apuntada al proyecto entero. Su entorno no puede escribir
> archivos: lo transcribió la corrida **sin editar su texto**. Al pie va una
> **adenda medida** de la corrida (§6) que contradice en un punto la
> recomendación, con el número que el director declaró no haber computado.
> Ninguna de las dos partes decide nada: las decisiones que nombra llevan la
> firma de Nicolás.

*Documento de programa. Ninguna cifra se cita de memoria: cada una lleva su
archivo. Este documento **no decide nada** — propone un orden y marca lo que
lleva firma.*

---

## VEREDICTO EN CUATRO LÍNEAS

**La tesis está viva, pero no la que el proyecto creía tener.** El fenómeno
existe y está medido; **la captura está muerta y el propio proyecto la mató**;
el mecanismo del decaimiento es el activo real y **nunca fue estimado como lo
que es**. Y la restricción que manda hoy no es la señal: es que el instrumento
acumula ~2 observaciones efectivas por día sellado, así que su regla mide en
graduaciones de 16 a 25 pp un fenómeno de 10 a 16 pp.

---

## 0. Las tres patas, una por una

**(A) El fenómeno existe.** Sobre 520 días y 4.151 pares, el campeón acierta la
dirección del gap **69,0 %** [67,5 – 70,4] contra **55,4 %** de «siempre al
alza» —**+13,6 pp**, McNemar p ≈ 0— (`DECISIONES.md` §59, líneas 5422-5424).
Sobre ocho años y n = 14.618, **+15,66 pp** (`README.md`, tabla de la ventana
larga). Sobrevivió siete amenazas adversariales: calendarios con 0 violaciones
en 15.033 pares, precios ajustados con desviación máxima 0,00 % en 223 filas,
entrada tardía exactamente cero, salida acotada bajo 0,2 pp. **VIVA.**

**(B) La captura está muerta, y el proyecto la mató él mismo.** La cartera
long-short **pierde 40,7 % sin un solo punto básico de costo** (Sharpe bruto
−1,08); con 25 pb por lado, −95,6 %, contra **+137,1 %** de comprar SMH y no
hacer nada (`DECISIONES.md` §59, líneas 5424-5426). No es un problema de
costos: los costos rematan algo que ya venía perdiendo. **MUERTA, y publicada
como muerta.** Ese negativo es de los activos más valiosos del repositorio.

**(C) El mecanismo del decaimiento es el activo, y está a medio medir.** Las
tres bolsas que abren dentro de tres horas dan +19,1 / +16,8 / +15,4 pp; la
que abre 8,75 h después, +2,5 pp con p = 0,111 (`README.md`). La explicación
obvia —Asia toma el relevo— se pre-registró y se **refutó**: el SOX pierde
13,9 pp al alejarse y nada lo reemplaza (`relevo_asiatico.md`). **VIVO sobre
ocho años; sobre la ventana sellada no se confirma ni se refuta**, y ahí el
orden incluso se invierte (Fráncfort +9,1 pp, Seúl +0,0 pp, con intervalos
demasiado anchos para leerlos — `dos_ventanas.md` §5).

**(D) La pata que nadie contó: la metrología del propio instrumento.** El sello
tiene *«emitido antes»* y **no tiene *«reproducible después»***: guarda
derivados a dos decimales, no insumos (`fuente_canonica.md` §1). Yahoo no
reescribió un solo retorno en 8 años × 27 tickers (52.507 celdas) pero **sirve
estados distintos del mismo query**: retiró la sesión del 28-ago y cuatro
noches de agosto sirvió el `^SOX` sin la barra del 31-jul (§2.1). Y el ritmo:
**n efectivo 69 sobre 246 filas en 35 días, ICC 0,39, DEFF 3,56 → 1,97
observaciones efectivas por día sellado** (`horizonte.md`).

**La lectura conjunta:** el proyecto tiene un fenómeno real, un mecanismo
plausible, una negativa económica sólida, y un instrumento que **no puede
resolver su propio hallazgo antes de 2027**.

---

## 1. LOS CAMINOS REALES

### Camino 1 — MEDICIÓN. Abandonar la captura y quedarse con el instrumento.

Declarar formalmente que MKI mide un fenómeno de microestructura entre husos
horarios, que la pregunta de captura **ya está contestada y contestada que no**,
y que el objeto publicable es el mecanismo más sus negativos.

Tiene dos versiones, y la diferencia entre ellas es todo el documento.

**1a — Medición sin cambiar nada.** Publicar lo que hay: el escalón de cuatro
bolsas, el relevo refutado, la cartera que pierde, la ventana sellada que aún
no alcanza para juzgar nada. *Datos:* ninguno nuevo. *Tiempo:* una pasada de
reporte. *Dinero:* cero. *Riesgo:* bajo. **Ya está hecho en un 80 %.**

**1b — Medición con el estimando corregido.** Y acá está, a mi juicio, la
oportunidad más grande y no tomada del proyecto:

> **El activo del proyecto es una PENDIENTE (la ventaja cae con las horas de
> margen), y el proyecto la mide como un NIVEL (acierto contra «siempre al
> alza»).** Son dos estimandos distintos y tienen potencias radicalmente
> distintas.

El nivel tiene ~2 observaciones efectivas por día porque las 7-8 filas de una
fecha son βᵢ·SOX sobre el **mismo** movimiento del SOX: aciertan y fallan casi
todas juntas (`bifurcaciones.md`, sección del clúster de día). Ese factor común
es exactamente lo que **se cancela** en un contraste *dentro del mismo día,
entre bolsas de distinto margen*: Fráncfort-menos-Tokio de la misma emisión no
comparte el desenlace, solo el insumo. Cuatro bolsas con márgenes verificados
de 1,75 / 1,75 / 2,75 / 8,75 h son cuatro puntos del eje que interesa, y el
contraste pareado por día es el estimador natural de la pendiente.

Ese número **no existe hoy**. El +19,1 contra +2,5 pp está publicado como dos
mediciones separadas, sin intervalo sobre su diferencia, y sin haber tratado la
fecha de emisión como el bloque que es.

*Datos:* ninguno nuevo — la ventana larga ya tiene 1.955 filas de Fráncfort y
7.230 de Tokio (`README.md`). *Tiempo:* un frente, con pre-registro previo.
*Dinero:* cero. *Riesgo:* **es un intento del DSR y hay que declararlo antes**
(§4.2 bis); y el conteo ya va en 91 o 97 (`espera_firma.md` §7).

**Señal de que este camino está muerto:** si el ICC del contraste entre bolsas
resulta comparable al 0,39 del contraste contra la baseline, la ganancia de
potencia no existe y 1b colapsa en 1a. **Esa medición es barata y es lo primero
que hay que hacer, antes de comprometerse con el camino.** Segunda señal de
muerte: que la pendiente estimada con intervalo incluya la horizontal — ahí el
«escalón medido» pasa a ser un escalón no medido y el hallazgo central del
README se retracta.

### Camino 2 — CAPTURA POR OTRO HORIZONTE.

Lo que murió es una forma precisa: entrar en la subasta de apertura y salir al
cierre. La forma coherente con lo medido es la contraria —estar posicionado
**antes** de la apertura—, y eso exige riesgo nocturno y un instrumento
accesible a las 22:15 UTC. **Nada en el repositorio lo mide.**

*Datos:* intradía o al menos una serie operable en el momento de la emisión —
justo lo que el expediente PIT recomendó **no comprar, cero dólares**
(`espera_firma.md` §15). *Tiempo:* meses. *Dinero:* el único camino con costo
real. *Riesgo:* **el más alto del documento, y no es financiero: es de
postura.** Publicar una negativa de captura y reabrir la pregunta seis semanas
después, sin pre-registro nuevo y sin sumar el intento, es exactamente el
patrón que el rigor del proyecto existe para impedir.

**Señal de muerte:** que la versión nocturna también pierda en bruto sobre la
ventana larga. **Condición para siquiera abrirlo:** pre-registro propio,
declarado como pregunta nueva, con su N. Hoy no corresponde.

### Camino 3 — EL RELOJ. Esperar a que la ventana sellada tenga potencia.

*Datos:* los que ya llegan solos. *Dinero:* cero. *Tiempo:* medido esta noche
(`horizonte.md`): **9 pp → 248 días sellados → ~jul-2027; 6,5 pp → 475 días →
~jul-2028; 5 pp → 803 días → ~dic-2029.** El veredicto del 25-oct tendrá ~73
días: **MDE al 80 % ≈ 16,6 pp**.

*Riesgo:* **la cadena de sellos.** Una sola máquina emitiendo, cuyo disco ya
falló una vez y se llevó cuatro commits. Y el instrumento no es reproducible
hacia atrás mientras C3 no exista.

**Señal de muerte:** llega el cambio de régimen y la ventaja en el régimen
nuevo queda centrada en cero con un intervalo que excluya el +15,66 pp de la
ventana larga. Segunda señal, más incómoda: **ya hay una grieta** — primera
mitad de la ventana +19,17 pp, segunda mitad **0,0 pp**, con intervalos que se
solapan (`horizonte.md`). No prueba nada todavía; si en 2027 sigue así,
prueba mucho.

**Este camino no es opcional: corre debajo de todos los demás y cuesta cero.**
Lo único que hay que hacer es no romperlo.

### Camino 4 — POTENCIA CON VALIDEZ. Volver usable la ventana larga.

La ventana larga da 59× la muestra y no es point-in-time. Tres cosas la
defienden hoy: el teorema del factor de ajuste (el objetivo es un cociente y el
factor se cancela), 0 retornos cambiados en 52.507 celdas, y la reconstrucción
**fiel al sello: 100 % de signos iguales y gaps idénticos sobre 214 filas**
(`condicional_ventana_larga.md` §3.5). Lo que le falta: composición histórica
del universo —**declarada NO EVALUABLE**, y ninguno de los diez proveedores
tasados vende constituyentes históricos— y ahora la intermitencia de estados.

*Qué exige:* la copia cruda congelada al sellar (**C3**: ~60 líneas, ~15 MB/año,
una columna aditiva `insumos_sha256`, corte de método con fecha) y declarar la
ventana larga **dependiente de la fuente, con fecha y sha256 de descarga**
(`fuente_canonica.md` §5 y §6). *Dinero:* cero. *Riesgo:* **toca
`snapshot.py`**, o sea lleva firma de Nicolás y bump de plataforma.

**Señal de muerte:** que un testigo muestre que la fuente revisó **retornos** —
no niveles— a tasa material. Ahí la ventana larga deja de ser evidencia y el
proyecto se queda solo con la sellada, es decir con el Camino 3 y su calendario.

### Camino 5 — EL RETADOR. Que GEMELO gane.

*Estado medido:* el retador lineal fue negativo; las 14 features extra no
agregan nada detectable sobre la ventana sellada (+2,8 pp, p = 0,3613) y agregan
poco y significativo sobre la larga (+1,3 pp, p = 0,0003); **C1 acierta la
dirección en las MISMAS filas que el campeón** (`README.md`, sección de
información expandida). Quedan por construir β en espacio de estados, pooling
jerárquico, régimen latente y densidad predictiva.

**Y acá hay un hecho estructural que conviene ver antes de invertir una hora
más:** REL-V4 exige una ventaja retador-menos-campeón con **IC95 que excluya el
cero** (`RELEVO.md` §3.1), sobre una ventana cuyos intervalos hoy miden 34 pp de
ancho. **El relevo es inalcanzable por construcción hasta que el Camino 3 o el
4 entreguen potencia.** No porque nadie sea lo bastante bueno: porque la regla
no se puede satisfacer con esta graduación.

*Riesgo del éxito, que es el que nadie mira:* un retador que gana obliga a un
switch de producción, a dos series nunca mezcladas, y a una válvula de
reversión que el propio `RELEVO.md` §7 declara **débil a n mínimo**.

**Señal de muerte: ya está emitiendo.** «Nadie pasa V1 bajo R2» (WS2b), y el
campeón mismo tampoco: excluyendo el bloque 15-23 jul queda en **−1,0 pp,
p = 0,9196**.

### Camino 6 — INSTRUMENTO DE INGENIERÍA (FPGA / RTL).

`piso_de_latencia.md` §4 ya lo dictaminó: la lectura «captura de microtrading en
vivo» es **NO VIABLE** —la distancia es de órdenes de magnitud, no de grado, y
una placa más grande es más FPGA, no más colocation—; la lectura «pipeline RTL
validado por backtest» queda abierta y es legítima. *Dinero:* la placa ya está
comprada y Vivado 2025.2 es gratis. **Es un camino del ramo, no de la tesis de
MKI.** Su único acoplamiento con MKI es una trampa: `referencia.py` regenera
vectores desde `senales.db` (181 congelados contra 189 sellados,
`espera_firma.md` §10). Ese acoplamiento es un pasivo.

---

## 2. LO QUE NO ES UN CAMINO, AUNQUE LO PAREZCA

1. **Otra convención de medición, otro eje, otra regla de dedup.** El jardín de
   192 celdas ya midió la dispersión: la ventaja recorre [−1,1, +15,4] pp *[nota de la corrida: rango de puntos estimados, cada uno con un IC que contiene el cero]* y
   **0 de 192 celdas dan p < 0,05 por clúster**. Otra celda mueve el punto
   dentro de un rango ya medido y **no mueve el intervalo**. Es la rama lateral
   más cómoda que ofrece el repositorio: entretenida, técnicamente exigente,
   estéril.
2. **Más features.** Medido y publicado: no agregan nada detectable, y C1 = el
   campeón en dirección. Es la tentación que el propio DSR existe para castigar.
3. **Más tickers por día.** Sube n y **no sube n efectivo**: el DEFF se lo come.
   Parece progreso y es dilución.
4. **Una segunda fuente de datos (C4).** No resuelve cuál es canónica —**suma un
   voto**— y necesitaría igual el congelado de C3. Y el expediente PIT
   recomendó no gastar.
5. **Re-correr el veredicto 5.1 antes de arreglar el arnés.** R3 disparó por
   fuga; una corrida hoy produce una referencia contaminada, no un veredicto.
6. **Explicar el bloque de julio.** Está en el percentil 90,3 entre bloques de
   su ancho y hay **157 bloques históricos sin solape iguales o mejores**
   (`condicional_ventana_larga.md` §3.2). Explicarlo es narrativa, no medición.
7. **Publicar el +9,7 pp como un avance.** Cruza α por la ruta que supone filas
   independientes; por la ruta de clúster su intervalo es [−7,2, +26,5] con n
   efectivo 67. **Publicarlo como progreso sería el daño más grande que el
   proyecto puede hacerse a sí mismo**, porque contradiría en la portada la
   postura que sostiene todo lo demás.

---

## 3. RECOMENDACIÓN

> **RECOMENDACIÓN, marcada como tal: Camino 1b, con el Camino 4 como
> infraestructura habilitante y el Camino 3 corriendo debajo a costo cero.
> Abandonar la captura de forma explícita y declarada. No abrir el Camino 2 ni
> el 5 en este ciclo.**

En una frase: **MKI es un instrumento de medición de una propagación entre husos
horarios; su hallazgo es una pendiente; hay que medir la pendiente como
pendiente, y hay que darle al sello la mitad que le falta para que dentro de dos
años lo medido siga siendo reproducible.**

**Orden de operaciones, y no es negociable el primero:**

1. **Que el titular siga sellando.** Es lo único irrecuperable: un día no sellado
   no se sella después. La réplica es la decisión de 10 minutos con el costo de
   postergarla **ya materializado una vez** (`espera_firma.md` §4).
2. **Los dos cortes de método que tocan el sello, en un solo movimiento y un
   solo bump:** el parche de `snapshot.py:140` (único con modo de falla en
   curso, 25 filas y creciendo) y la copia congelada C3. **Los dos llevan firma
   de Nicolás; ningún agente los toca.**
3. **Medir el ICC del contraste entre bolsas sobre la ventana larga.** Barato,
   sin firma, y **decide si la recomendación se sostiene**.
4. Solo entonces, el pre-registro de la pendiente, con su intento declarado.

**Incertidumbre explícita.** Mi argumento de que el contraste entre bolsas tiene
más potencia es **estructural, no medido**: el factor común del SOX se cancela.
Puede fallar por dos razones concretas — la cobertura de Fráncfort en la ventana
sellada es de 33 filas sobre 248 (`dos_ventanas.md` §5), y la diferencia entre
bolsas puede arrastrar su propio clúster de día. **No lo computé y no lo voy a
citar como si lo hubiera computado.**

**Qué me haría cambiar de opinión, en concreto:**

- ICC del contraste entre bolsas ≈ 0,39 → la recomendación cae a 1a + 3:
  publicar, esperar, no gastar intentos.
- Un cambio de régimen antes del 25-oct con la ventaja sosteniéndose → el
  Camino 3 se abarata mucho y la urgencia de 1b baja.
- Un testigo que muestre revisión de **retornos** en la fuente → el Camino 4
  muere y con él la única ventana con potencia.
- Que la pendiente, medida con intervalo, incluya la horizontal → **se retracta
  el hallazgo central del README**, y ese sería el resultado más valioso que
  este proyecto podría producir este año.

---

## 4. QUÉ DE LO QUE EL PROYECTO HACE HOY MUEVE LA AGUJA

**Mueve, y mucho:**

- **La cadena de sellos.** Es la única evidencia prospectiva y crece lineal. Todo
  lo demás se puede hacer después; esto no.
- **El Frente B de esta noche (`horizonte.md`).** Convirtió «no sabemos si esto
  es medible» en un calendario con fechas. Es lo más valioso producido en dos
  noches, porque es lo que permite decidir entre esperar y rediseñar.
- **El Frente A de esta noche (`fuente_canonica.md`).** Encontró que el sello
  tiene la mitad de su propiedad, y diseñó la otra mitad sin tomarse la decisión.
- **Los negativos publicados:** la cartera que pierde, el relevo refutado, WS2b,
  R3 disparando sobre el arnés del 5.1. **Estos son el activo**, no el número de
  acierto.
- **`bifurcaciones.md`.** Retiró la ilusión de que la ventana sellada ya había
  dicho algo. Un instrumento que sabe que no puede medir todavía vale más que
  uno que cree que sí.

**Mueve poco, o mueve después:**

- **El segundo sello.** Como está diseñado hoy compara contra un derivado
  (`sox_usado_pct`, dos decimales, solo `^SOX`). **Su valor está condicionado a
  que C3 exista primero**; con el panel completo su resolución pasa de «el
  último retorno del SOX» a cada celda de cada serie. **Es correcto y está en el
  orden equivocado.**
- **La réplica.** No mueve el estimando, pero protege lo irrecuperable. Su pieza
  débil está declarada: **la comparación no está automatizada**, así que hasta
  el séptimo job alguien tiene que acordarse a diario — justo la clase de punto
  débil que el mecanismo existe para eliminar.

**No mueve la aguja de MKI:**

- **La FPGA.** Es del ramo, es legítima, y su único vínculo con MKI hoy es un
  pasivo (181 contra 189). Mantenerla separada es cuidarla.
- **GEMELO como fábrica de retadores.** El relevo es inalcanzable por
  construcción con esta graduación (§1, Camino 5). **GEMELO como laboratorio de
  medición y auditoría sí mueve** — de ahí salió todo lo valioso de las últimas
  cuatro noches. Es la función lo que hay que renombrar, no el directorio.

**Y dos cosas que el proyecto hace y que hoy le cuestan más de lo que le rinden:**

1. **El recurso escaso ya no son las horas de agente: son las firmas de
   Nicolás.** Hay quince ítems esperando, unas 3 h 30 de lectura
   (`espera_firma.md`), y tres de ellos tienen modo de falla activo. Seis
   corridas produciendo decisiones más rápido de lo que una persona puede
   firmarlas no es rendimiento: **es una cola**. La sexta y la séptima corrida
   agregaron ítems a esa cola más rápido de lo que la vaciaron.
2. **Los intentos del DSR son un consumible y se están gastando sin
   presupuesto.** El registro pasó de 25 a 33 a 91, y el veredicto declara 97;
   el README todavía dice 25. Cada configuración evaluada deflacta más el
   resultado que algún día se quiera publicar. **Es el argumento cuantitativo
   más fuerte contra «una configuración más»**, y hoy nadie lo está usando como
   presupuesto.

---

## 5. LO QUE ESTE DOCUMENTO NO HACE

- **No decide.** El corte de método de C3, el parche de `snapshot.py:140`, el
  MDE, la regla canónica del segundo sello y la réplica llevan firma de Nicolás.
- **No toca el modo de emisión ni los timers.** El switch ya se hizo y ésta es
  la única máquina que emite.
- **No mueve ninguna cifra publicada** y no propone moverla.
- **No computó el contraste entre bolsas.** Lo propone y declara que no lo midió.
- **No autoriza ningún intento del DSR.** El del Camino 1b se declara antes de
  correrse, o no se corre.

*Herramienta de análisis y aprendizaje — no constituye asesoría financiera.*

---

## 6. ADENDA MEDIDA de la corrida (2-sep-2026, 02:21; reescrita 03:10 tras el dictamen) — el número que el director no computó, y por qué tampoco lo resuelve esta medición

El director condicionó su recomendación (1b) a una medición que declaró no
haber hecho: si el contraste entre bolsas no gana potencia frente al nivel,
«la recomendación cae a 1a + 3». **Esa medición existe desde las 02:19 de
esta misma noche**, hecha ANTES de leer su documento y con otra vara
(`GEMELO/SECUENCIAL/estimandos.py`, IC por bootstrap de fechas enteras,
mismo clúster de día para todos los estimandos; PROPUESTA pendiente de
dictamen). Sobre la ventana larga reconstruida (518 fechas, B2 = motor de
producción):

| estimando | punto | IC95 (fechas) | z | días para potencia 0,80 al efecto observado |
|---|---|---|---|---|
| nivel: ventaja direccional vs "siempre al alza" | +13,4 pp | [9,8, 17,0] | **7,35** | **75** |
| mecanismo: contraste Asia − Fráncfort | +10,8 pp | [5,0, 16,7] | 3,68 | 300 |
| mecanismo: pendiente de la ventaja por hora de margen | −1,61 pp/h | [−2,45, −0,77] | 3,78 | 284 |

**Lo que la primera redacción de esta adenda concluía —«el contraste tiene
la mitad de la señal-a-ruido del nivel y necesita ~4× más fechas; por la
cláusula del director, 1b cae a 1a + 3 + 4»— fue RECHAZADO por el
`estadistico-adversario` (dictamen §E, `dictamen_07/DICTAMEN.md`), y se
retira.** El motivo: el z del mecanismo está computado con la **fecha** como
unidad de replicación, pero el parámetro del mecanismo (la pendiente sobre
h) tiene como unidad la **bolsa**, y hay cuatro con sólo dos valores de h.
Con la bolsa como unidad, la permutación exacta da p = 0,231 y el p mínimo
alcanzable es 1/13; el bootstrap de bolsas da un IC tres veces más ancho.
Y el `README.md` ya lo decía en la línea 60: con n = 4 bolsas no se ajusta
una curva. **El cociente «4×» no tiene interpretación, así que la
contradicción con 1b no queda establecida — ni a favor ni en contra.**

Lo que sí queda medido y publicable: la tabla por bolsa con Wilson por
bolsa, el contraste Asia − Fráncfort **declarado como comparación de cuatro
bolsas** (+10,8 pp [5,0, 16,7] con clúster de fecha sobre la larga; +0,5 pp
[−26, +30] sobre la sellada, un intervalo que contiene el cero, donde el orden se invierte), y la frase de que
el mecanismo, sobre 37 días sellados, no tiene señal. **La condición del
director —«medir el ICC del contraste entre bolsas sobre la ventana larga»—
sigue sin hacerse como él la formuló** (contraste pareado por día entre
bolsas de la misma emisión); lo que se midió esta noche es otra cosa y no lo
reemplaza. La recomendación 1b queda **condicional y sin resolver**, como él
la dejó; los intentos de esta noche ya están en el registro (tramos TRAY y
ESTIM). El orden de operaciones 1 → 2 (seguir sellando; los dos cortes de
método en un solo bump) queda intacto.
