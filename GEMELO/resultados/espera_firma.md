# Lo que espera tu firma

**Quince ítems. Ninguno lo puede decidir un agente.** Cada uno trae qué hay
que decidir en una frase, qué desbloquea, cuánto cuesta decidirlo, y las
opciones con su consecuencia. Donde hay recomendación, va marcada como tal;
donde no la hay, también se dice, y por qué.

**Están ordenados por costo de postergarlos un mes, no por tamaño.** El más
caro va primero aunque se resuelva en cinco minutos.

Leer todo y firmar todo: **~3 h 30**. Pero no hace falta.

---

## Si sólo tenés tiempo para tres

| # | | Por qué éste y no otro | Costo |
|---|---|---|---|
| **1** | **El parche de `snapshot.py:140`** | Es **el único que sigue haciendo daño hoy.** Los otros catorce son decisiones sobre datos que ya existen; éste agrega una fila mal etiquetada cada vez que un sello se atrasa, y las filas selladas no se reescriben nunca. Van 25. | **5 min** |
| **2** | **La cuenta AMD** | Es lo único que separa al proyecto de tener **Fmax, utilización de slices, cierre de temporización y bitstream** — o sea todos los hitos en silicio del ramo. Y ahora tiene **dos relojes**: el del ramo, que este documento sigue sin conocer, y uno nuevo de AMD (§2). | **20 min** |
| **3** | **Las 15 filas + publicar el README** | Van juntos y no son separables: publicar +9,7 pp sabiendo que hay una rama declarada de +14,3 pp sin resolver es peor que no publicar ninguna de las dos. | **20 min** |

**Los tres suman 45 minutos.** El cuarto y el quinto —la réplica y el MDE—
tienen relojes propios que conviene mirar aunque no los firmes hoy: la
réplica es la única cuyo costo de postergarla **ya se materializó una vez**
(el SSD que se llevó cuatro commits), y el MDE cuesta **cero hasta octubre e
infinito desde el 2026-11-19**.

---

## Antes de citar cualquier cifra de acá

Varias se movieron hoy. Tres advertencias que valen para todo el documento:

**La ventaja de la ventana sellada bajo la regla que firmaste es +9,7 pp con
p = 0,0451 sobre n = 238 — y su IC95 de clúster de día es [−7,2, +26,5], con
n efectivo 67, no 238.** Si citás el p, citá el intervalo pegado. **Cruzar α
no es tener evidencia.** Todo el peso de ese p son 10 días ganados contra 6
en 17 días informativos; un 10-6 no distingue nada, y para verlo no hace
falta ningún aparato. Por la ruta de clúster, **0 de 192** formas legítimas
de medir la misma ventana dan p < 0,05 (por la ruta que supone filas
independientes, 59).

**El conteo de intentos vigente, al 1-sep-2026, es 91** (el registro, hoy de
25 tramos con procedencia) **o 97** (el que declara en disco la corrida del
backtest, que suma 6 propios). **No es 25.** El README todavía dice 25 — ver
§7, y ver ahí también la prueba de que ese número no está quieto: la corrida
de la ventana condicional partió de 25 y publicó "N acumulado 25 → 33", y el
propio registro subió de 86 a 91 **mientras esta página esperaba firma**.

**La rama de +14,3 pp no tiene intervalo computado.** Por la tercera regla de
la casa, hasta que lo tenga es una consecuencia declarada, no un argumento.
Ver §3.

---

# 1. El parche de `snapshot.py:140`

**Qué hay que decidir:** si se aplica el parche que hace que
`sesion_objetivo` se calcule desde `available_at` —cuándo era conocible el
insumo— en lugar del reloj de pared del proceso.

**Qué desbloquea:** detiene la contaminación activa del track record. Es el
único ítem de la lista con un modo de falla **en curso**.

**Costo de decidirlo: 5 minutos.** No hay nada que investigar. El expediente
está en `GEMELO/resultados/parche_snapshot140.md` y llega en un estado poco
habitual:

- El diff **aplica limpio** — verificado con `patch --dry-run` contra el
  `snapshot.py` real, sin aplicarlo. Es **una sola expresión**: ni un import
  nuevo, ni un parámetro nuevo, ni un cálculo nuevo (`available_at` ya existe
  y ya tiene el valor correcto en ese punto).
- Trae **test de fijación y contraprueba**, y no como promesa: los dos fallan
  hoy contra el `snapshot.py` sin tocar, con el mismo síntoma
  (`assert '2026-07-31' == '2026-07-30'`), y los dos pasan contra una copia
  parcheada en `/tmp`. **Corregido en el ejecutable antes que en el texto**,
  que es la segunda regla de la casa.
- **La declaración del corte de método está escrita antes de aplicarse**, no
  después: qué significaba `sesion_objetivo` antes, qué significa después,
  desde cuándo, y cómo debe tratar cualquier análisis futuro las filas de
  cada lado. Está lista para pegarse en `DECISIONES.md` en cuanto sepas la
  fecha real y si bumpeás `PLATAFORMA_VERSION`.

**El dato que cambió desde la corrida anterior: son 25 filas afectadas, no
20.** La auditoría exhaustiva contra `senales.db` en `mode=ro` sobre las 279
filas con predicción sellada da 25 con `sesion_objetivo` objetivamente
distinto del que implica su propio `available_at`: **10** del lado viejo de
los pares ya documentados, más **15 sin pareja** que el método anterior no
podía ver porque buscaba duplicados y éstas no chocan con nada. **Las 25 ya
están `estado='verificada'` y ya contribuyen a las métricas selladas de hoy.**

| Opción | Consecuencia |
|---|---|
| **(a) Aplicar y declarar el corte con su fecha** | Deja de crecer. Las 25 filas viejas quedan como están para siempre (Constitución 5.0 punto 3): no hay backfill, hay errata. |
| (b) No aplicar | Una fila mala más por cada sello atrasado. El defecto es **invisible salvo que uno vaya a buscar duplicados por `sesion_objetivo`**, que nadie hizo en cinco corridas. |
| (c) Aplicar y además pedir un guardia | Lo mismo que (a), más que el vigía o un test lo detecte solo la próxima vez. |

**Recomendación, marcada como tal: (c), y (a) si querés cerrarlo hoy.** El
parche es de (a); el guardia es trabajo mío y no bloquea aplicarlo.

**Si bumpeás `PLATAFORMA_VERSION` en el mismo movimiento**, el corte queda
auto-documentado para siempre en cada fila sellada y no depende de la memoria
de nadie. Si no, hay que anotar a mano el `timestamp_utc` del primer sello
posterior — **en el momento, no reconstruido después.**

---

# 2. La cuenta AMD para Vivado

**Qué hay que decidir:** nada. **Hay que hacer un trámite de veinte minutos**
que sólo podés hacer vos.

**Qué desbloquea, exactamente:** **Fmax, utilización de slices, cierre de
temporización y bitstream** — o sea, todos los hitos en silicio del proyecto
del ramo. Sin place & route todo lo demás queda marcado como estimación. La
placa **ya está comprada** (Arty A7-100T, `XC7A100TCSG324-1`), el disco
alcanza (946 GB libres), la RAM alcanza, no hace falta root y **la licencia
cuesta $0**. El bloqueo no es técnico: todos los instaladores redirigen a un
formulario de cuenta y control de exportación. **Es un acto de identidad, de
la misma clase que pushear.**

## Lo que verifiqué hoy con búsqueda web, porque los nombres cambiaron

**El nombre de la edición cambió dos veces y las dos veces quedó atrás en
nuestros documentos.** Esto es lo vigente, verificado contra la página de
descargas de AMD y contra la cobertura del cambio:

| Cuándo | Cómo se llama la edición gratis | Qué hace falta |
|---|---|---|
| Hasta 2013 | **WebPACK** | nada |
| 2021 – **2025.2** | **Vivado ML Standard Edition** | **nada — sin archivo de licencia** |
| **2026.1** en adelante (jun-2026) | se descarga **Vivado Design Edition** y se genera una licencia **BASIC** | **archivo de licencia + renovación anual** |

Desde 2026.1 AMD reemplazó el esquema de ediciones por cinco *tiers*:
**BASIC** (gratis, anual), **CORE** y **PRO** (pagos, anuales), **ENTERPRISE**
y **GOLD** (perpetuos). **BASIC cubre toda la serie 7, con la XC7A100T
adentro**, e incluye síntesis, implementación, generación de bitstream,
programación JTAG, XSIM limitado e ILA limitado (5 sondas). Quedan afuera
System ILA, bitstreams encriptados, DFX, compilación incremental y **los
reportes de cierre de temporización**.

> **Ojo con ese último**: si el hito del ramo exige el reporte de cierre de
> temporización y no sólo que el diseño cierre, verificalo antes de elegir
> versión — es una de las exclusiones declaradas de BASIC. Con 2025.2 no
> existe la duda.

**Cuánto pesa la descarga — la cifra que importa:** el instalador que hay que
bajar es el **web installer auto-extraíble, de ~230 a 350 MB**, no los 95 GB
que asusta en la página. Verificado en la página de descargas de 2025.2:

| | |
|---|---|
| Windows Self Extracting Web Installer (EXE) | **233,33 MB** |
| Linux Self Extracting Web Installer (BIN) | **346,7 MB** |
| Single File Download (SFD), todos los dispositivos, offline | 95,69 GB |

El web installer después baja **sólo los componentes que marques**. Marcando
Vivado + soporte de dispositivos **Artix-7 / serie 7 únicamente**, la
instalación queda en el orden de **20-30 GB**, contra ~250 GB del instalador
completo. **Con 946 GB libres, sobra por cualquiera de los dos caminos.**

## Los pasos, numerados

1. **Crear la cuenta** en <https://account.amd.com/> (o `login.amd.com`).
   Usá tu nombre y dirección reales: el formulario de exportación los cruza.
   *~5 min, más verificar el mail.*
2. **Entrar a** <https://www.amd.com/en/support/downloads/adaptive-socs-and-fpgas.html>
   (el viejo `xilinx.com/support/download.html` redirige ahí).
3. **Elegir versión.** Ver "Qué versión bajar" abajo — la decisión es de una
   línea y conviene tomarla antes de hacer clic.
4. **Clic en el Self Extracting Web Installer** de la plataforma elegida.
   Redirige al formulario de verificación de descarga: nombre, apellido,
   mail, dirección, país y rol. Poné **Student**. *~5 min.*
5. **Empieza la descarga** (~230-350 MB). **Si en cambio salta un aviso de
   control de exportación**, hay que completar el
   *export-compliance-review form* explicando que sos estudiante y para qué
   lo necesitás, y **esperar de 1 a 3 días hábiles** la aprobación por mail.
   Chile no suele dispararlo, pero **si lo dispara, el trámite deja de ser de
   hoy** — razón de más para empezarlo antes de necesitarlo.
6. **Correr el instalador.** Vuelve a pedir las credenciales de AMD.
7. **Marcar sólo Vivado + Artix-7 / serie 7.** Este paso es el que decide si
   bajás 20 GB o 250.
8. **Sólo si elegiste 2026.1+:** generar la licencia **BASIC** gratuita en el
   sitio de Product Licensing de AMD y apuntar Vivado ahí (Vivado License
   Manager o `XILINXD_LICENSE_FILE`). **Desde 2026.1 Vivado no arranca sin
   archivo de licencia, ni siquiera en BASIC.**

## Qué versión bajar, y en qué máquina

**Recomendación, marcada como tal: Vivado 2025.2, del archivo de versiones, e
instalado del lado Windows.**

**Por qué 2025.2 y no la última:** es la última versión con la Standard
Edition vieja — **gratis, sin archivo de licencia, sin renovación anual, sin
tiers y con Linux soportado sin discusión**. Elimina de un saque el paso 8,
la renovación, y la ambigüedad que sigue abajo. Para medir Fmax, slices,
temporización y bitstream de una Artix-7, 2025.2 no te falta en nada.

**Por qué del lado Windows, y son tres razones independientes que apuntan al
mismo lado:**

1. Este WSL2 es **Ubuntu 26.04**, que **no es plataforma soportada** por
   UG973 (22.04 / 24.04).
2. **JTAG desde WSL2 exige `usbipd-win`** — y sin JTAG no hay bitstream en la
   placa, que es el hito.
3. **Un hallazgo nuevo de hoy, y está en disputa:** el cambio de 2026.1 fue
   cubierto como que **el tier BASIC gratuito quedaba restringido a Windows**,
   empujando a Linux al tier CORE (USD 1.200-1.800/año). Otra fuente sostiene
   que, tras el rechazo de la comunidad, **la tabla actual de AMD lista
   Windows y Linux en todos los tiers, BASIC incluido**. **No pude resolverlo
   contra la página de licenciamiento de AMD: dio timeout en todos los
   intentos.** Lo dejo declarado como contestado en vez de elegir una de las
   dos.

**Lo bueno es que la decisión es robusta a esa duda:** instalar del lado
Windows es correcto bajo cualquiera de las dos lecturas, y bajar 2025.2 hace
que la pregunta ni siquiera se aplique. **Las dos recomendaciones se sostienen
sin necesidad de resolver el hecho en disputa** — por eso las recomiendo aun
sabiendo que ese punto quedó abierto.

**Fuentes de lo anterior:** página de descargas de AMD (versión, opciones y
tamaños exactos; requiere sign-in, redirige a `member/forms/download/xef.html`),
la documentación de AMD sobre las opciones de licenciamiento y el tiering de
2026.1, y la cobertura del cambio en prensa técnica y foros. **Lo único que
no pude verificar de primera mano es la disponibilidad de Linux en BASIC**,
por los timeouts citados.

**Costo de postergarlo:** sigue dependiendo del cronograma de la materia, que
este documento **sigue sin conocer. Es dato que falta, no indecisión** — y es
lo único que impide poner este ítem primero sin discusión.

---

# 3. Las 15 filas sin pareja, y publicar (o no) el README

**Van juntos y no son separables.** Por eso están en un solo ítem.

## 3.1 — Qué hay que decidir

**Si además de deduplicar se retiran las 15 filas que están solas y mal.**

La regla que firmaste **no las cubre, y no por descuido: por construcción.**
La regla arbitra **entre dos filas que compiten** por el mismo
`(ticker, sesión objetivo)` y siempre deja una. **Estas 15 no compiten con
nada.** No hay hermana correcta que conservar, así que retirarlas es
**descartar sin reemplazo**, que es una operación distinta de la que firmaste.
Por eso quedó explícitamente sin decidir, para que la resuelvas con el mismo
criterio que usaste para las otras diez y no por omisión.

**Qué son las 15:**

| Emisión | Sesión sellada | Sesión que implica `available_at` | Filas | Por qué quedó sin pareja |
|---|---|---|---|---|
| 2026-08-05 | 2026-08-07 | **2026-08-06** | 7 | El snapshot del 08-06 tuvo **caída total de datos**: no hubo fila fresca con la cual chocar. |
| 2026-07-05 | 2026-07-06 | **2026-07-03** | 8 | Sello **manual** con casi 3 días de atraso, saltando un feriado de XNYS y un fin de semana. El salto no es de una sesión sino de tres. |

## 3.2 — La cifra, marcada como consecuencia y no como argumento

| | n | ventaja | b/c | p exacta | IC95 de clúster |
|---|---|---|---|---|---|
| Regla firmada (ya aplicada en el ejecutable) | 238 | +9,7 pp | 72/49 | 0,0451 | **[−7,2, +26,5]**, n efectivo 67 |
| **+ coherencia (no aplicada)** | **223** | **+14,3 pp** | **69/37** | **0,0024** | **no computado** |

**Tres cosas sobre esa tabla, y las tres importan más que los números:**

**Primera: el IC de la fila de abajo no existe todavía.** Por la tercera regla
de la casa, un estimador puntual sin intervalo no se cita como evidencia.
Pedime que lo compute antes de que ese +14,3 pp entre a cualquier
razonamiento — y tené presente que el ancla de 238 filas ya tenía n efectivo
**67**: sacar 15 filas más saca a lo sumo un par de días de clúster, así que
**no hay razón para esperar que el intervalo se angoste de forma material.**

**Segunda: el retiro es asimétrico, otra vez.** `c` cae de 49 a 37 y `b` sólo
de 72 a 69. Es el mismo patrón que produjo el 0,0451: de las 10 filas que
retiró la regla firmada, **7 eran discordantes y las 7 favorecían a la
baseline, ninguna al modelo.** Que la corrección correcta siga empujando en la
dirección que le conviene al modelo es exactamente la clase de cosa que hay
que mirar de frente antes de firmar, no después.

**Tercera, y es la que puede decidir el ítem sola:** las 8 filas del 5-jul
**no necesitan un criterio nuevo para salir**. Con el ancla temporal correcta,
su sesión (07-03) ya había cerrado cuando el proceso selló (07-05T10:06 UTC),
así que **la regla maestra que el proyecto tiene desde la Etapa 4.6 las manda
a `no_verificable_timing` por sí sola.** No las descartaría un criterio nuevo:
las descartaría el criterio que ya está escrito. Hoy están contadas como
`verificada` sólo porque el ancla estaba mal.

| Opción | Consecuencia |
|---|---|
| **(a)** Retirar las 15 | Rama +14,3 pp. Es descartar sin reemplazo: una extensión de la regla, no la regla. |
| **(b)** Dejarlas | Las 15 siguen contando como si su `sesion_objetivo` fuera correcto. |
| **(c)** Tratar sólo las 8 del 5-jul | **No inventa criterio: aplica la regla maestra.** Las 7 del 5-ago quedan para decidir aparte. |

**Recomendación, marcada como tal: la (c).** Es la única que no extiende
ninguna regla — sólo deja de blindar 8 filas contra un criterio que el
proyecto ya tiene desde la 4.6 y que estaba mal aplicado por el ancla. Las
otras dos siguen disponibles después, con el IC ya computado y sin la presión
de resolverlo junto con la publicación.

## 3.3 — Y de ahí, publicar o no

El parche de `parche_dedup.md` (trece bloques, escrito y no aplicado) movería
la cifra publicada de **+6,5 pp a +9,7 pp**. Hoy el README, la skill
`cifras-canonicas`, `estadistica-evaluacion` y `estadistico-adversario.md`
**siguen citando +6,5 pp sin la advertencia** — y por la cuarta regla de la
casa, un número que sigue ofrecido vuelve a circular.

**Un hecho que conviene tener a la vista al ratificar:** firmaste conociendo
dos desenlaces, 0,1847 sin deduplicar y 0,0323 con `keep="last"` (que quedó
prohibida). **Tu regla produjo un tercero, 0,0451, que cruza α y no estaba
sobre la mesa.** El criterio sigue siendo el correcto — el desenlace se
declara porque una decisión informada por dos números que produce un tercero
necesita esa nota.

| Opción | Consecuencia |
|---|---|
| (a) Publicar +9,7 pp ahora | Publica sabiendo que hay una rama declarada de +14,3 pp sin resolver. |
| **(b)** Resolver §3.1 y publicar una sola vez | Una sola errata, una sola pasada. |
| (c) Publicar +9,7 con las advertencias pegadas | Honesto, pero sigue siendo publicar dos veces. |

**Recomendación, marcada como tal: la (b).** No por prolijidad: publicar +9,7
pp mientras una rama de +14,3 pp está declarada y sin resolver es **peor que
no publicar ninguna de las dos**, porque deja en la portada una cifra que
sabemos incompleta.

**Y pase lo que pase con el número, la advertencia va pegada:** +9,7 pp con
IC95 de clúster [−7,2, +26,5] y n efectivo 67. **Con un intervalo de 34 pp de
ancho, esta ventana no separa al campeón de una constante.** El track record
no está refutando al campeón: está diciendo que **todavía no alcanza para
juzgarlo**, en ninguna dirección.

---

# 4. La réplica: quién gana ante una divergencia

**Qué hay que decidir:** ante una divergencia entre la máquina titular y la
réplica, **cuál de las dos filas es la oficial.**

**Qué desbloquea:** salir de tener **una sola máquina emitiendo** — la misma
cuyo disco de sistema ya falló una vez y se llevó cuatro commits. Es el único
ítem de la lista cuyo costo de postergarlo **ya se materializó**.

**Costo de decidirlo: 10 minutos.** Las otras tres decisiones del runbook (qué
máquina, confirmar el titular en el acta, la política de retención) son
mecánicas una vez tomada ésta. **Ésta es la que bloquea.** Activar después es
"una tarde", casi toda esperando que el Mac selle una vez en frío.

**La réplica en una página está en `GEMELO/resultados/replica_una_pagina.md`
— no lo repito acá.** Lo que hay que saber para firmar cabe en cuatro líneas:
la pieza técnica ya no es el cuello (el ensayo general pasó ocho fechas
sintéticas con **cero divergencias falsas**); el riesgo de fondo es uno solo,
que la réplica emita, y tiene **tres capas ya probadas** contra eso; la vuelta
atrás es apagar seis timers; y hay **una cosa que hoy no existe y conviene
saber antes de firmar: la comparación no está automatizada**, así que hasta
que se construya el séptimo job **alguien tiene que acordarse de correrla
todos los días** — que es justo la clase de punto débil que este mecanismo
existe para eliminar.

| Opción | Consecuencia |
|---|---|
| **A. La titular gana siempre, sin excepción** | Simple, auditable, y **nunca reescribe una fila sellada**. Si la titular se equivoca, la réplica lo deja documentado pero no lo corrige solo. |
| B. Gana la de mejor salud de descarga | Puede corregir errores reales de datos. **Pero decide en caliente, y elegir la fila que se sella según un criterio evaluado ese mismo día es una puerta abierta a que el criterio se ajuste al resultado.** |
| C. Divergencia = no se sella ese día | Máxima pureza, peor costo: **convierte cada problema de la réplica en un agujero del track record de la titular.** Es darle a la réplica poder de veto sobre producción. |

**Recomendación, marcada como tal: la A.** Es la que preserva la regla
constitucional de que una fila sellada jamás se reescribe, y la única que no
le da a un mecanismo nuevo poder sobre el experimento que lleva corriendo
desde julio. **Las otras dos se pueden adoptar más adelante con evidencia; la
A no cierra ninguna puerta.**

---

# 5. El MDE — la cifra que fija el calendario del proyecto

**Qué hay que decidir:** qué efecto mínimo se declara de interés. **Esa cifra
sola fija la fecha en que el proyecto sabrá si su ventaja es real.**

**Qué desbloquea:** congela `GEMELO/SECUENCIAL/DISEÑO.md`. Sin congelar **no
sirve**: todo su valor es haber fijado las reglas antes de ver los datos.
`mirada.py` tiene candado (`MDE_FIRMADO = None`) y se niega a computar.

**Costo de decidirlo: 30 minutos, pero es elección de valores, no cálculo.**

| MDE | El proyecto responde en |
|---|---|
| +10 pp | jul-2027 |
| +8 pp | ene-2028 |
| +7 pp | jun-2028 |
| +6 pp | ene-2029 |
| +5 pp (umbral de `RELEVO.md`) | feb-2030 |

**Recomendación, marcada como tal: +10 pp.** Diseñar para +5 pp es defendible
pero empuja la respuesta a 2030, y **un diseño que tarda tres años y medio
tiene alta probabilidad de romperse antes de completarse — y un diseño que se
rompe no responde nada.** Dicho eso, es una elección de valores sobre qué
ventaja valdría la pena, no un cálculo, y por eso no la toma un agente.

**Tres cosas que hay que saber antes de firmar, y ninguna es cómoda:**

- **El 7 pp quedó RETIRADO** (derivado en la escala del retorno de sesión
  cuando el endpoint congelado es `acierto_gap`). El reemplazo propuesto fue
  8,96 pp con IC95 [6,67, 11,32] — **y ese intervalo fue objetado: no es el
  del MDE, es el de E|gap| invertido.** Hoy `mirada.py` tiene
  `MDE_PROPUESTO = None`: **no hay número puesto para firmar.**
- **El pasivo de haber mirado la misma cifra cada vez que crecía, sin
  declararlo, es α entre 0,09 y 0,18** — de 1,8× a 3,6× el 0,05 declarado.
- **`mde_desde_v6.py` sigue sin ancla temporal** (escribió su propio SQL sin
  `hasta_sello`), y era una de las cuatro condiciones para levantar el rechazo
  del 31-ago. **El 8,96 de hoy no es el de mañana**, y el pre-registro lo cita
  como parámetro.

**Sub-decisión que va pegada:** la regla de varianza cuesta ~1,7 pp de
potencia. O se recompensa con más filas (y la respuesta llega más tarde), o
**se declara que la potencia del plan es ~0,76 y no 0,80. La segunda es barata
y honesta** — recomendada.

**Costo de postergarlo: cero hasta octubre. Desde el 2026-11-19, infinito** —
ese día, o el documento está congelado, o cualquier cifra que se mire es una
mirada más sin declarar.

---

# 6. Los 5 pares de feriado real — calendario y universo

**Qué hay que decidir:** qué hace el sistema cuando emite una predicción cuya
sesión objetivo natural cae con **la bolsa cerrada**, y dos emisiones
consecutivas apuntan legítimamente a la misma sesión.

**Qué desbloquea:** nada operativo — **pero el conteo crece solo.** Cada
feriado de XTKS o XKRX en día hábil produce un par nuevo. Hoy pesa 10 filas de
253 (4,0%).

**Costo de decidirlo: 20 minutos** (más la redacción del corte de método si
elegís la opción 2).

**Esto no es el defecto del §1.** Verificado: ninguna de las diez filas de
estos cinco pares aparece en la lista de 25 — **sus dos emisiones están
igualmente a tiempo y las dos son correctas.** Es un problema de diseño del
sistema, no de deduplicación ni de medición.

**La evidencia:** 2026-08-12 (4 pares, `3436.T` `4063.T` `6857.T` `8035.T`,
XTKS cerrado el 11-ago) y 2026-08-18 (1 par, `005930.KS`, XKRX cerrado el
17-ago). Las dos filas de cada par comparten `gap_pct` **idéntico** y
**discrepan en `acierto_gap` en los 5 pares, sin excepción**: contarlas dos
veces mete el mismo desenlace de mercado dos veces en el denominador, con dos
veredictos contrarios que se cancelan.

| Opción | Consecuencia |
|---|---|
| 1. Dejarlas las dos, como hoy | Honesto, pero pesa un desenlace de mercado el doble que los demás. |
| 2. No emitir si la sesión objetivo ya tiene una predicción viva para ese ticker | Toca la ruta de sellado: **decisión con corte de método y fecha.** |
| 3. Promediar o marcar el par en la capa de medición | Barato y reversible, **pero inventa una fila que nadie emitió.** |

**Sin recomendación, deliberadamente.** Es una decisión de diseño del sistema,
no de medición, y vos mismo lo mandaste acá por esa razón.

**Nota de acoplamiento:** el defecto **B-3** del arnés de la 5.1 (263 de 4.160
filas con desenlaces duplicados, dos pares contados **8 veces**) es este mismo
fenómeno sobre la ventana larga. **Conviene decidirlos juntos.**

---

# 7. `README.md`:253 dice "Va en 25". El registro da 91

**Qué hay que decidir:** si se corrige la portada pública.

**Qué desbloquea:** coherencia entre la cifra publicada y el ejecutable.

**Costo de decidirlo: 5 minutos.**

El texto dice, literal: *"**El N del DSR se declara antes de cada corrida y
solo sube.** Va en 25…"*. **El registro verificado da 91** —calculado como
suma de `REGISTRO_INTENTOS`, 25 tramos con procedencia línea a línea, ya no un
entero mágico— **y la corrida del backtest declara 97** (91 del registro más
6 propios).

> **El número se movió mientras este ítem esperaba firma, y eso es el
> hallazgo.** Cuando se escribió esta página el registro daba **86** sobre 20
> tramos. El banco de cláusulas del 1-sep agregó **cinco tramos** (C1, C2,
> C3a, C3b, C4) y lo dejó en **91**; `backtest/veredicto_51.py` acompañó
> (`N_INTENTOS_PREVIO = 91`, `N_INTENTOS_51 = 97`). Nada de esto fue una
> corrección: el registro hizo exactamente lo que promete hacer, subir cada
> vez que se evalúa una configuración más. **Cualquier entero que se clave hoy
> en la portada estará viejo la próxima vez que se evalúe algo** — que es el
> argumento para la opción (d), abajo, y la razón por la que las opciones (a)
> y (b) quedan escritas con su fecha.

**Y no es un número dormido.** La corrida de la ventana condicional de esta
mañana publicó *"Intentos sumados: 8 (N acumulado 25 → 33)"*: **partió del 25
de la portada.** Es la cuarta regla de la casa observada en vivo — un número
retirado que sigue ofrecido en el código vuelve a circular, y ya circuló hoy.

**Contexto de por qué importa, y está medido:** `GEMELO/control_lineal.py`
tenía `n_intentos` con default 9 mientras `backtest/inferencia.py` había
quitado ese mismo default a propósito, con acta y con test.
**`SR0(9) = 0,9986` contra `SR0(86) = 1,6266`: regalaba 0,63 de umbral, y a
Sharpe anualizado de 1,2-1,5 el criterio V5 se daba vuelta de PASA a NO
PASA.** Ya está corregido. El del README no.

| Opción | Consecuencia |
|---|---|
| (a) Actualizar a **91 al 1-sep-2026** con nota de procedencia | La cifra del registro, auditable línea a línea. Nace con fecha de vencimiento: el próximo tramo la deja vieja. |
| (b) Actualizar a **97 al 1-sep-2026** | El N que declara en disco la corrida del 5.1, antes de computar nada. Mismo vencimiento. |
| (c) Dejarlo y anotar errata fechada | El 25 sigue en la portada y sigue propagándose, como propagó hoy. |
| **(d) Publicar la fuente, no el entero** | La portada dice de dónde sale el N (`REGISTRO_INTENTOS`, N tramos con procedencia) y cita el valor **con su fecha**. Es la única que no vuelve a envejecer sola. |

**El propio texto promete que el N "solo sube", así que (a), (b) y (d) son las
tres consistentes con lo publicado. Dejarlo en 25 es lo único que lo
contradice.** No recomiendo entre 91 y 97 porque depende de qué convención
declares canónica. Sí recomiendo, marcado como tal, **que no quede en 25**, y
—viendo que el número se movió dos veces en una semana— **que la forma sea la
(d)**: cualquiera de las otras vuelve a esta misma cola dentro de un mes.

---

# 8. El método del McNemar, sin declarar

**Qué hay que decidir:** cuál de tres salidas se toma ante el hecho de que el
proyecto tiene **dos árbitros para la misma pregunta, y ninguno está mal.**

**Qué desbloquea:** cierra un `xfail` puesto a propósito en rojo en
`tests/test_epistemico.py`, y cierra una regla escrita rota.

**Costo de decidirlo: 10 minutos** bajo A; **~1 h** si elegís B.

**El hallazgo, y no es el que se creía:** el 0,1849 del README es el **χ² de
McNemar con corrección de continuidad** (0,184898) y el 0,1847 del módulo es
la **binomial exacta** (0,184683). Mismo par (b=72, c=56), mismo n, **métodos
distintos, ninguno mal.**

**No es una cifra, son cuatro** —los tres p de la ventana sellada (0,1158 /
0,2542 / 0,1849) y el de la línea base congelada (0,4633)— y todas salen de
`backtest/linea_base.py:126`, **que reimplementa McNemar a mano cuando
`.claude/rules/backtest.md`:26-27 dice literal que no se reimplemente.**
*Atenuante:* `linea_base.py` es del 25-ago y la regla del 30-ago; la regla
llegó después y nadie volvió a mirar el código que ya estaba.

**Lo que traba el arreglo obvio:** `GEMELO/DISEÑO.md` §2.8 **congeló**
p = 0,4633 en un pre-registro. Migrar al árbitro la mueve a 0,4635, y un
pre-registro congelado no se toca. **Chocan dos reglas del propio proyecto.**

| Opción | Consecuencia |
|---|---|
| **A. Declarar el método al lado de cada p, sin mover ningún dígito** | Cero cifras movidas, pre-registro intacto. Queda una excepción viva a una regla escrita. |
| B. Migrar al árbitro y mover las cuatro | Coherencia total. **Precedente incómodo: un pre-registro que se mueve.** |
| C. Migrar hacia adelante, congelar hacia atrás | Sin errata sobre el pre-registro, pero convive un corte de método que hay que explicar cada vez. |

**Recomendación, marcada como tal: la A.** Ninguna conclusión cambia — el
mayor Δ es 0,0003 — y el χ² con corrección de continuidad no es el método
malo. **Lo que falta es una palabra, no un número.** Obliga igual a escribir
la excepción en `.claude/rules/backtest.md`: **una regla con una excepción no
escrita es una regla que se vuelve a romper.**

---

# 9. El parche de honestidad del README, y si se reformula R2

**Qué hay que decidir:** dos cosas, y conviene no mezclarlas.

**(a)** Si se publica el parche que declara en el README que **la ventaja
sellada no se distingue de cero** y que su concentración en julio no está
establecida. **(b)** Si el criterio **R2** se reformula.

**Qué desbloquea:** el README y **tres archivos vivos de referencia**
—`cifras-canonicas`, `estadistica-evaluacion`, `estadistico-adversario.md`—
siguen citando +6,5 pp sin la advertencia. Cualquiera que lea el proyecto hoy
—**incluida una sesión futura de este mismo agente**— cita la cifra sin el
matiz que la vuelve honesta.

**Costo de decidirlo: 20 minutos.** El parche está escrito con **doce bloques,
uno por uno con archivo:línea**, en `GEMELO/resultados/parche_honestidad.md`.

**Recomendación sobre (a), marcada como tal: aplicarlo.** Es barato, no cambia
ninguna cifra, sólo agrega contexto. **Y conviene agruparlo en una sola pasada
de reporte con §11 y con las cinco preguntas del WS4** (§15).

**Sobre (b), R2, no hay recomendación, y es a propósito.** La ventana 15-23
jul de R2 se eligió post-hoc y el scan-statistic corregido **no la establece
como especial** — argumento para reformularlo. Pero **R2 sólo descarta, nunca
aprueba, y bajarlo justo cuando se descubre que el campeón tampoco lo pasa
sería exactamente lo que un pre-registro existe para impedir.** Las dos
lecturas están escritas con su argumento; la elección es tuya.

---

# 10. La trampa latente de `referencia.py`: 189 casos contra 181 congelados

**Qué hay que decidir:** si se pone un pin explícito del N o un guardia propio
en `micro/rtl/referencia.py`.

**Qué desbloquea:** nada. **Es una trampa armada, no una deuda** — y ésa es
justamente la razón para tocarla ahora y no cuando salte.

**Costo de decidirlo: 10 minutos.**

**Verificado hoy contra el repo y contra la base en `mode=ro`:**
`micro/rtl/vectores/parametros.vh` dice `` `define N_CASOS 181 ``, y
`esperado_F1.hex` y `mensajes_b28.hex` tienen exactamente 181 líneas. Pero
`referencia.py` **no lee ese número: lo regenera desde `senales.db`**, y la
base ya tiene **189** filas selladas con beta y apertura. **Cualquier cosa que
toque ese módulo regenera los vectores con 189 y mueve en silencio todas las
cifras publicadas como "181 filas"** — y el testbench las compararía contra un
`esperado_*.hex` que ya no corresponde.

| Opción | Consecuencia |
|---|---|
| (a) Pin explícito de N=181 con su fecha de congelamiento | Las cifras publicadas quedan reproducibles. |
| (b) Guardia/test que falle si el conteo se mueve | Igual, y además avisa. |
| (c) Regenerar a 189 | **Mueve todas las cifras publicadas como "181 filas". Lleva acta, no se hace de paso.** |
| (d) Dejarlo | La trampa sigue armada. |

**Recomendación, marcada como tal: (a) y (b) juntas** — el pin fija la cifra
publicada, el guardia impide que alguien la mueva sin darse cuenta. La (c) es
la única que arrastra cifras publicadas y por eso no se hace de paso.

**Nota de acoplamiento:** este mismo 181-vs-189 es lo que pone en duda la
frase de `GEMELO/MICRO/SINTESIS_A7.md`:538-540 —*"dos métodos distintos, mismo
número: eso es la vara independiente"*, sobre los 0,00474 pp de error de
cuantización—. **Nadie comprobó si el arnés de 181 filas y el de 189 son
familias de método realmente distintas o el mismo álgebra recorrida dos
veces** — que es la primera regla de la casa. Recomendación: **medirlo antes de
volver a citar esa frase; si comparten el álgebra, la frase se retracta.** No
es grave: es el precio de tener la regla. Y es una **afirmación de haber
verificado**, que son las que se citan sin volver a mirarlas.

---

# 11. Dos artefactos que publican una cifra ya refutada

**Qué hay que decidir:** autorizar una corrida, y autorizar un arreglo de
código+test en una sola pasada.

**Costo de decidirlo: 5 minutos.** El trabajo es mío y es chico.

**(a) `GEMELO/resultados/ventana_larga.{md,json}` publican el 91,4%** de
coincidencia **que ya está refutado**: con la clave correcta (`sesion_objetivo`,
no `["fecha","ticker"]`) da **100% sobre 214 filas, 0 diferencias**. El
ejecutable **ya está corregido con errata**; los artefactos quedan stale hasta
que alguien re-corra el módulo. **Costo: una corrida.**

> Al citarlo hay que arrastrar la lectura correcta, que el frente dejó
> escrita: esto **no prueba que Yahoo no revise la historia**, sólo que **no
> la revisó en el tramo auditable de 2026.**

**(b) `GEMELO/ventana_larga.py`:314-345 sigue emitiendo la cifra de
contaminación del 8,6% ya refutada, y `tests/test_ventana_larga.py`:186 la
exige por contrato.** Es el único ítem de la lista **con un modo de falla
activo en el código**: cualquiera que re-corra el WS3 —una sesión futura, un
`pytest` de rutina que alguien lea— **republica la falsedad, y el test
confirma que está bien.**

**Recomendación, marcada como tal: corregir el código y el test juntos, en una
sola pasada y con acta.** Dejar el código corregido con el test viejo, o al
revés, **es peor que el estado actual.**

---

# 12. El hook de pre-commit

**Qué hay que decidir:** si se instala un hook que **rechace un `.md` de
resultados que no cite un `.py` versionado del mismo frente.**

**Qué desbloquea:** nada hoy. **Es prevención**, y es la única clase de error
que resistió al barrido que convirtió en test seis de las siete clases de las
cinco corridas.

**Costo de decidirlo: 15 minutos.**

**De dónde sale:** la raíz de la segunda corrida — el análisis completo vivió
en comandos sueltos de una sesión que se perdió, y **sólo se pudo auditar
porque unos archivos intermedios sobrevivieron por casualidad en un directorio
temporal.**

**Por qué ningún test lo ataja:** un test estático **no puede detectar la
ausencia de un archivo que nunca se escribió. No hay nada que escanear.** Y el
sustituto obvio —"toda cifra publicada nombra el script que la produce"— o es
tautológico o dispara sobre medio repo, y **un test epistémico que grita por
todo se termina desactivando.**

**Y de ahí cuelga una segunda clase, también sin test posible:** desviarse de
un criterio pre-registrado congelado sin declararlo — el umbral congelado en
0,0 mientras el análisis usaba 12,9 de un subconjunto de entrenamiento, **del
que dependía la conclusión publicada.** Detectarlo exige comparar lo que el
código **usó** contra lo que el pre-registro **congeló**, y eso sólo es
posible si el análisis está versionado. **Misma raíz.**

**Recomendación:** el agente que lo propuso **no lo instaló solo, e hizo
bien** — un hook que rechaza commits cambia cómo trabaja todo el mundo, y eso
lleva firma. **No recomiendo entre instalarlo o no**, porque es de proceso y no
técnica. Lo que sí recomiendo, marcado como tal: **el candidato menor, que no
necesita tu firma y lo puedo hacer yo** — un test AST que exija que todo
script de resultados que lea `senales.db` ancle la lectura con `hasta_sello`.
Sin eso, `mde_desde_v6.py` **dejó de reproducir el día que se firmaba.**

**Costo de postergarlo: bajo pero mal distribuido** — no pasa nada hasta que
pasa, y cuando pasa cuesta dos rondas de auditoría y una retractación, que es
exactamente lo que costó en agosto.

---

# 13. El registro de intentos, en módulo propio

**Qué hay que decidir:** si el registro se mueve a
`GEMELO/registro_intentos.py` para que `relevo_asiatico`, `control_lineal`,
`ventana_larga` y `veredicto_51` importen del mismo sitio.

**Qué desbloquea:** una casa única para el N del DSR. Hoy hay cuatro
consumidores y un ciclo de imports parcheado.

**Costo de decidirlo: 5 minutos. Costo de implementarlo: ~40 minutos y un
import nuevo en cuatro archivos** — es trabajo mío, no tuyo. **Propuesto y no
instalado**, a propósito, por riesgo de conflicto con otros frentes.

**La evidencia a favor está medida, no supuesta:** al pasar el N explícito
apareció un **import circular** que hubo que resolver con import diferido.
**Ese ciclo es, en sí mismo, el síntoma de que el registro no tiene casa.**

| Opción | Consecuencia |
|---|---|
| (a) Moverlo ahora | 40 min míos; cierra el ciclo. |
| (b) Moverlo cuando se vuelva a tocar alguno de los cuatro | Gratis hoy; el import diferido queda como deuda visible. |
| (c) Dejarlo | El ciclo sigue, y el N sigue teniendo cuatro puertas. |

**Recomendación, marcada como tal: (b).** La evidencia a favor de mover es
real pero no urge, y hacerlo pegado al próximo cambio de esos archivos evita
el conflicto que hizo que no se instalara hoy. **Va naturalmente junto con
§7**, que es la otra mitad del mismo problema.

---

# 14. `CLAUDE.md` afirma que el Mac es titular

**Qué hay que decidir:** cómo se corrige la sección de la Etapa 5.0.3, que
dice que el Mac *"stays **titular**"* y que `MKI_MODO=sombra` vive en la línea
18 de `.env`. **Las dos son falsas hoy.**

**Qué desbloquea:** nada operativo. Pero **toda sesión nueva arranca leyendo
que la máquina en la que corre no es la titular** — exactamente la clase de
desfase que el proyecto documenta como errata en vez de cometer.

**Costo de decidirlo: 5 minutos.**

**Por qué no lo arregla un agente:** `CLAUDE.md` es el documento que gobierna
cómo trabaja el agente en cada sesión. Cambiarlo **cambia el comportamiento de
todas las sesiones futuras**: es una edición que se ve, no un arreglo de paso.

**Precedente que conviene tener presente:** esta misma afirmación **ya
sobrevivió dos corridas** como "errata pendiente de registrar" en `ESTADO.md`,
hasta que alguien la borró **sin registrarla**.

| Opción | Consecuencia |
|---|---|
| **(a)** Corregir la sección con una nota fechada | La próxima sesión lee la verdad, y queda el rastro de cuándo cambió. |
| (b) Reescribir la sección entera | Más limpio, más caro, y pierde el rastro. |
| (c) Dejarla y anotar la errata en otro lado | Ya se intentó. Duró dos corridas y se perdió. |

**Recomendación, marcada como tal: (a), en el mismo movimiento en que toques
`CLAUDE.md` por cualquier otra razón.**

**Micro-decisión pegada:** el segundo movimiento del switch —apagar los timers
del Mac, quitar `MKI_MODO` del PC— **se dejó afuera de esta lista a propósito**
porque ya tiene su expediente completo en la skill `switch-titular`. **Si
querés verlo priorizado junto con el resto, decilo y entra.**

---

# 15. Los agrupables: siete ítems que no bloquean nada

**Todos juntos: ~30 minutos.** Ninguno tiene reloj propio. Los pongo últimos
por eso, no porque no importen.

| | Qué decidir | Nota |
|---|---|---|
| **Datos point-in-time** | Aceptar formalmente **no comprar nada, cero dólares** (diez proveedores tasados con precio verificado). | Se firma tranquilo: **lo que sostiene la conclusión no es la muestra, es un teorema** — el factor de ajuste escala `open(t)` y `close(t−1)` por igual y el objetivo es un cociente. Vale para las 14.618 filas, no sólo para las 223 verificables. **Queda abierto aparte** lo que esto NO arregla: composición del universo y sesgo de supervivencia — **ninguno de los diez vende constituyentes históricos del ^SOX.** Canal residual gratis que nadie midió: fechas ex-dividendo sobre la sesión objetivo (~0,9% de filas). |
| **Umbrales de `RELEVO.md`** | Si el margen de **5 pp** y el **n≥150 / 60 días** son los correctos. | Recomendación: **no dejarlo para el día que aparezca un candidato** — para entonces, un pre-registro fijado bajo presión deja de ser un pre-registro. El costo de postergarlo **no es lineal**: pasa de "no urgente" a "bloqueante" de un día para otro. Si querés un criterio R4, hay que rehacerlo: el que había cayó con `parche_documental.md`. |
| **Las cinco preguntas del WS4** | Convención de la ventana larga, §32.5 refutado, cómo se reporta Fráncfort, y si las 8 filas del 29-jul siguen en las métricas. | **Agrupar con §9 y §11 en una sola pasada de reporte.** Llevan abiertas desde antes del 26-ago sin romper nada. |
| **B4 y B5 sobre la ventana larga** | Si se evalúa al retador con **cuatro** baselines sobre la ventana larga y las seis sólo sobre el tramo con juicios reales. | Al corregir la fuga B-1 **sobreviven 288 de 4.152 filas (6,94%)**. **La distinción que hay que preservar al citarlo:** eso se lee como *"la capa de precios con columnas constantes"*, **jamás** como *"las noticias no aportan"*. B0-B3 no tocan sentimiento y **siguen evaluables**: son **dos baselines de seis, no el backtest**. Corregir la fuga **no cambió el desenlace**. **No urge hasta el 25-oct.** |
| **Los cuatro defectos del arnés de la 5.1** | Cuáles se tocan **antes** del veredicto del 25-oct. | **B-3** es el §6 sobre la ventana larga → decidir juntos. **S-1** (el embargo purga días corridos, no jornadas) es la que más claramente lleva firma: **cambiarlo la víspera del veredicto sería mover el arnés después de haber visto el diseño** — la prosa se inclina a no tocarlo. **S-3** y el **holdout material** (hoy la cuarentena es sólo procedimental, y V7 dice que se evalúa una sola vez: es un recurso irreversible). |
| **Expedientes 6B y 6C** | Visibilidad de `ts_emision`; auditar idempotencia de los 6 jobs ante una estampida de timers; alcance del pin de pandas. | La estampida **nadie la investigó nunca, ni se sabe si es un problema real** — y la opción de solo lectura se puede hacer en cualquier sesión. Para 6C: escribir el test de estabilidad de los sitios de `pd.concat` **antes** de decidir el alcance. |
| **`.claude/` versionado o local** | Cuál preferís. | **Es una preferencia, no un riesgo.** |

---

## Lo que NO está acá, porque no lleva firma

Trabajo mío, listado para que no se cuele a esta lista y para que sepas que
está anotado: **por qué el snapshot del 2026-08-06 perdió el 100% de sus
predicciones** (anomalía aparte, no investigada); la **errata de
`DECISIONES.md`:5459-5460**, que escribe el arreglo de B-1 con `min()` cuando
la causalidad exige `max()` (ya corregido en el ejecutable con test que falla
si alguien vuelve al mínimo — falta la errata en el acta); la **errata del
commit `6bb1f46`**, cuyo mensaje no menciona dos archivos que el `git add -A`
barrió; la **errata de `DISEÑO.md` §A3.1.a** ("cinco sesiones" → son cuatro,
sin consecuencia sobre ninguna cifra); el **ancla temporal de
`mde_desde_v6.py`** (va pegado al §5); y los **cuatro módulos que heredan la
regla de dedup sin haber sido tocados**, cuyas cifras se moverán si se
re-corren.

---

## Lo que se cerró en esta tanda, para que no lo busques

Etapa **5.1 AUTORIZADA**, con la condición de contar todos los intentos
declarados antes de calcular nada, y de escribir el veredicto con la misma
firmeza si es negativo · **Gatillo de la 5.1: NO se releva**, se espera al
**25-oct-2026**; el holdout sigue intacto · **Regla de deduplicación FIRMADA y
aplicada**, con `keep="last"` **prohibida** · **α = 0,05 nominal**, banda
[0,046, 0,079] publicada · **Placa: Arty A7-100T**, arquitectura de dos
modelos · las dos afirmaciones de `RTL.md`, corregidas en su sitio con errata
fechada · **PIT cerrada** con recomendación de no gastar (falta sólo aceptarla,
§15).
