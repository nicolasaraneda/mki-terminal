# Lo que espera tu firma

> **Actualizado el 28-sep-2026 (corrida 14).** El acta §88 (19-sep) firmó §43, §54, §58 (en
> parte), §59 (por remisión) y §60, y hasta la corrida 14 este archivo no lo reflejaba: los cinco
> encabezados llevan ahora su marca, **sin borrar el texto de la tarjeta**. La corrida 14 abrió
> §61 a §65. Lo anterior queda como estaba.
>
> **Actualizado el 8-sep-2026 (corrida 11).** Los seis ítems firmados en el acta §82
> (§45, §41, §55/§8, §42, §26 y 2a-ter/§3) salieron de la cola y quedaron como stubs con
> referencia a su acta; lo que sigue esperando no se tocó. **Firmado no es ejecutado:**
> la sección de abajo dice qué te queda a vos de cada firma.

## Firmado en §82, pendiente de ejecución por Nicolás

| Firma | Qué falta, y de quién es |
|---|---|
| §82.2 (§26, §1) | **Nota de la corrida 14 (`curador-epistemico`): `snapshot140.diff` ya está aplicado en producción** por el acta §84.1 —`snapshot.py:163` ancla la sesión objetivo en `available_at`, que es código vivo—, así que esta fila pide algo hecho. No se corrigió de paso; va al encargo 15. Texto original: **Aplicar el parche `snapshot140.diff` junto con el guardia `guardia_ancla_temporal.diff`** (§49), en el mismo acto, con bump de `PLATAFORMA_VERSION`. Los dos aplican juntos sobre copias (`tests/test_parche_guardia_ancla_temporal.py`). El conteo de la parte (d) está hecho: **0 filas** pasaron por la rama del `except` (bitácora 11, bloque 6). |
| §82.3 (2a-ter, §3) | El intervalo de clúster está computado (`intervalo_coherencia.md`): **contiene el cero en las tres rutas**, como predijo el acta. **Cablear** `filtrar_sesion_coherente` al árbitro y mover el README es decisión aparte, no firmada (§46). |
| §82.4 (§42) | Reconstruida. Espera los dictámenes del auditor y del adversario (en la bitácora 11); si exigen algo, entra a la corrida 12. Lo que abrió: §47 y §48. |
| §82.1, §82.5, §82.6 | Ejecutadas por completo (bloques 7 y 8; §82.6 no tenía nada que ejecutar). |


**Cuarenta y cinco ítems al 7-sep, más los cinco que abrió la corrida 11 (§46 a §50). Los cuatro últimos (§42 a §45) los abrió el CIERRE de la
corrida 10, no la corrida: salen de los dictámenes, y el §42 es el más caro de
postergar de todos los abiertos, porque hoy bloquea una vara pre-registrada.
Ninguno lo puede decidir un agente.** Cada uno trae qué hay
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

**Los tres suman 45 minutos.** *(Séptima corrida: el §16 —la copia
congelada de insumos— va en el mismo movimiento que el §1: dos cortes de
método, un solo bump. Sumale 10 minutos.)* El cuarto y el quinto —la réplica y el MDE—
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

**El conteo de intentos vigente es 100** (el registro, al 2-sep-2026, 23
tramos con procedencia: los 91 del 1-sep más los 9 de la séptima corrida,
registrados a posteriori por exigencia del adversario — ver §20) **o 106** (el
que declarará la próxima corrida del backtest, que suma 6 propios). **No es
25.** El README todavía dice 25 — ver
§7, y ver ahí también la prueba de que ese número no está quieto: la corrida
de la ventana condicional partió de 25 y publicó "N acumulado 25 → 33", y el
propio registro subió de 86 a 91 **mientras esta página esperaba firma**.

**La rama de +14,3 pp no tiene intervalo computado.** Por la tercera regla de
la casa, hasta que lo tenga es una consecuencia declarada, no un argumento.
Ver §3.

---

# 1. El parche de `snapshot.py:140` — FIRMADO (acta §82.2), PENDIENTE DE APLICAR (lo aplicás vos)

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

# 3. Las 15 filas sin pareja, y publicar (o no) el README — FIRMADO (acta §82.3, 7-sep-2026)

**Decidido: se retiran de las métricas** (2a-ter). La corrida 11 (bloque 4) computó el
intervalo de clúster de día que el §82.3 exigía antes de publicar:
`GEMELO/resultados/intervalo_coherencia.md`. **Queda a tu decisión, aparte:** cablear
`filtrar_sesion_coherente` al árbitro y mover el README (ver §46 abajo). El expediente
de esta tarjeta vive en la versión anterior de este archivo (git) y en el acta.

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

# 8. El método del McNemar, sin declarar — FIRMADO (acta §82.5, 7-sep-2026)

**Decidido: opción A**, declarar el método y no mover ninguna cifra. **Ejecutado en la
corrida 11 (bloque 8):** el README declara el test al lado de cada p y el `xfail` de
`tests/test_epistemico.py` se retiró. Nada queda pendiente de vos en este ítem.

# 9. El parche de honestidad del README, y si se reformula R2

**Qué hay que decidir:** dos cosas, y conviene no mezclarlas.

**(a)** Si se publica el parche que declara en el README que **la ventaja
sellada no se distingue de cero** y que su concentración en julio no está
establecida. **(b)** Si el criterio **R2** se reformula.

**Qué desbloquea:** el README y **tres archivos vivos de referencia**
—`cifras-canonicas`, `estadistica-evaluacion`, `estadistico-adversario.md`—
siguen citando +6,5 pp (cifra retirada el 3-sep-2026, acta §78) sin la advertencia. Cualquiera que lea el proyecto hoy
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

# 14. `CLAUDE.md` afirma que el Mac es titular — HECHO el 3-sep-2026 (encargo 09 §1d, opción (a))

> Corregido con nota fechada en la sección 5.0.3 de `CLAUDE.md` (el titular es este PC; `migracion-wsl` muerta; la skill `switch-titular` que citaba **no existe**: la cita pasa a `modo-emision`), y en el frontmatter de `.claude/agents/guardian-constitucion.md:3` (decía «rama migracion-wsl en el PC»). Lo de abajo queda como historia.

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

---

# Lo que agregó la séptima corrida (2-sep-2026)

Cinco ítems nuevos. Todos con expediente, ninguno con cifra publicada
movida. **Y una operación de un minuto que no es ítem:** `.env` está en
modo 644 (legible por todo el sistema); debería ser 600. Lo anotó el
guardián, lo verifiqué (`stat -c %a .env`), no lo toqué: es tuyo. El dictamen del `estadistico-adversario` sobre la noche entera está
en `GEMELO/resultados/dictamen_07/DICTAMEN.md`; las propuestas que rechazó
no aparecen acá.

# 16. Cuál es el campeón cuando el sello y la fuente discrepan — y la copia de insumos

**Qué hay que decidir:** dos cosas atadas. **(a)** Para la ventana sellada,
¿el campeón son las filas selladas (y el backtest las LEE en vez de
recomputarlas), o su reconstrucción desde el Yahoo de hoy? **(b)** ¿Se
construye la copia cruda de insumos al sellar (`GEMELO/INSUMOS/`, arnés
probado y no activado), que toca `snapshot.py` con corte de método?

**Qué desbloquea:** un veredicto 5.1 que no dependa de qué sirva Yahoo la
mañana del 25-oct, y un sello con la propiedad que hoy no tiene:
«reproducible después».

**Costo de decidirlo: 15 minutos.** Expediente:
`GEMELO/resultados/fuente_canonica.md` §4–§6.

**La evidencia, medida esta noche:** Yahoo no cambió un retorno en 8 años ×
27 tickers, pero sirve el mismo query en estados distintos (retiró el
28-ago; cuatro noches de agosto sirvió el `^SOX` sin la barra del 31-jul —
hipótesis M6, única barra de 130, residuo 4–8× el piso). Las 16 filas de
signo contrario ya están verificadas (15) en el track record vivo. Bajo
«Yahoo de hoy» el acierto vivo pasa de 64,86% [59,1, 70,2] a 64,49% [58,7,
69,9]: **b = 8, c = 7, p = 1,00 — la cifra no está en juego; la
reproducibilidad sí.**

| Opción (a) | Consecuencia |
|---|---|
| **Las filas selladas son el campeón; B2 las lee** *(recomendada)* | El 5.1 sobre lo sellado deja de depender de la fuente. Cambia `backtest/baselines.py`, no el sello. |
| La reconstrucción manda | 16 signos y 32 magnitudes cambian con el estado de la fuente, y pueden volver a cambiar. |
| No declarar | Dos objetos, ninguno manda: el statu quo que produjo el bloqueo. |

| Opción (b) | Consecuencia |
|---|---|
| **Sí, en el mismo bump que el parche de `snapshot.py:140`** *(recomendada)* | Una llamada protegida (nunca rompe el sello) + columna aditiva `insumos_sha256`; ~9 MB/año medidos (130 barras consumidas) o ~53 (panel de 3 años). |
| Sí, aparte | Dos cortes de método, dos bumps. |
| No | El sello sigue guardando derivados a dos decimales; M6 seguirá siendo inferencia. |

**Micro-decisión pegada, sin recomendación:** si la ventana larga se declara
dependiente de la fuente y cada corrida publica fecha y sha256 de su
descarga como parámetro sellado.

# 17. La frase de potencia del veredicto 5.1, escrita antes del 25-oct

**Qué hay que decidir:** si el resumen del veredicto 5.1 dice, por
construcción, que su potencia frente al efecto relevante (9 pp) es **0,36
[0,34, 0,37]** *(errata 2-sep 11:55: decía 0,34 [0,31, 0,37], la cifra de 1.000 simulaciones; la de 3.000 es la que cita su expediente. **Segunda errata, 15:20: ese 0,36 es de `horizonte.md`, instrumento que el dictamen A midió optimista; la cifra vigente es 0,31 [0,27, 0,35] del simulador calibrado — ver §22–23**)* con ~73 días sellados (MDE al 80%: 16,6 pp [11,0, 20,3]), o
si eso se escribe en `DECISIONES.md` antes del 25-oct sin tocar el arnés.

**Por qué es tuya:** tocar `veredicto_51.py` es tocar el arnés del 5.1, y
el propio expediente S-1 dice que moverlo la víspera es moverlo después de
ver el diseño. Hay que decidirlo ahora, no en octubre. Expediente:
`GEMELO/resultados/horizonte_veredicto.md`.

| Opción | Consecuencia |
|---|---|
| (a) La frase va al generador del resumen ahora, con acta | Un NO PASA del 25-oct nace con su potencia al lado. |
| **(b) No tocar el arnés; escribirla en `DECISIONES.md` antes del 25-oct** *(recomendada)* | Igual de honesto, sin mover el arnés. |
| (c) Nada | Un NO PASA se leerá como refutación. |

**Y lo que el dictamen agregó, y no es cómodo:** **R2 —el criterio de
rechazo congelado— dispara sobre el ancla del 31-ago**: sin el bloque
15–23 jul la ventaja queda en +2,5 pp, IC de día [−13,6, +19,2] (contiene
el cero), permutación p = 0,82. Está escrito; no lleva firma; conviene
saberlo antes de octubre.

# 18. Tres propuestas del Frente C sobre el estadístico principal — con dictamen

Las tres pasaron por el adversario. **Lo que se firma es si se adoptan.**

| | Propuesta | Dictamen | Qué haría falta |
|---|---|---|---|
| **C-1** | Ratificar el IC de clúster de día como principal y **no publicar decisiones binarias sobre la ventana sellada hasta que un MDE firmado las habilite** | **ENTRA sin condición** | una línea en `GEMELO/DISEÑO.md` |
| **C-2** | Agregar el proceso de apuestas anytime-valid (Waudby-Smith & Ramdas) como secundario: válido a cualquier instante de parada y bajo la autocorrelación que el Frente D no acota | ENTRA con cinco declaraciones (estimando distinto del ICD, σ̂² conservador, una cola, parámetros declarados antes, intento registrado — ya está) | un párrafo en `DISEÑO.md`; hoy K = 3,0 contra 20 |
| **C-3** | Que el **p** del McNemar de filas deje de ofrecerse por defecto en `duelo()`, `comparar_pareado()` y `control_lineal` — porque **su tamaño real es ≈ 0,31, no 0,05**, bajo el agrupamiento de día (DEFF 3,77) | ENTRA con el motivo cambiado | ~30 líneas en tres archivos; `b` y `c` siguen; el p se sigue calculando para la §2.8 congelada |

**Recomendación, marcada como tal:** las tres. Ninguna mueve una cifra.

# 19. El Frente D: la referencia de autocorrelación, y que no hay diseño robusto

**Qué hay que decidir:** si `GEMELO/SECUENCIAL/DISEÑO.md` cita, **como
medición de referencia y no como cota**, la autocorrelación de d_j sobre la
reconstrucción de dos años: AC1 −0,042, IC95 [−0,122, +0,041] (contiene el cero); en el tramo
solapado con la sellada, −0,180 ± 0,158 contra −0,176 ± 0,164; ciega a la
intermitencia de la fuente; y el α del plan bajo esa referencia en
**[0,031, 0,065]** contando el error de Monte Carlo. **La banda firmada
[0,046, 0,079] no se toca y no se re-discute.**

**Y el resultado negativo, verificado:** a 51–203 fechas **no existe
estadístico que entregue α = 0,05 plano bajo autocorrelación desconocida**
(bloques como unidad inflan por grados de libertad; Newey-West aplana pero
parte sesgado). Declarar la banda era la respuesta correcta.

**Sin recomendación entre citar o no:** es una línea de contexto en un
pre-registro que sigue sin congelar (§5 de la lista original).

# 20. El Frente E: un endpoint secundario, y una recomendación de programa

**(a)** Si se pre-registra la **pendiente de calibración** (magnitud
predicha → realizada; sellada 1,42 [0,65, 2,19], contiene 1) como endpoint
**secundario**, **contra la pendiente del control lineal y no contra 0**,
con «hay relación» y «está calibrado» como hipótesis separadas. Dictamen:
entra sólo así. El decaimiento como pendiente por hora fue **rechazado** (4
bolsas, 2 valores de margen: p mínimo alcanzable 1/13).

**(b)** La recomendación del `director-programa` (`GEMELO/resultados/tesis.md`):
**abandonar la captura de forma explícita; MKI como instrumento de
medición**; camino 1b (medir la pendiente entre bolsas) condicionado a una
medición que sigue sin hacerse; seguir sellando; los dos cortes de método
en un bump. Es una decisión de programa. **Sin recomendación de la corrida
más allá de la suya**, salvo una: la cola de firmas crece más rápido de lo
que se vacía, y él lo dijo primero.


---

# Lo que agregó la octava corrida (2-sep-2026)

Todo PROPUESTA; los dictámenes del `estadistico-adversario` por frente
están en `GEMELO/resultados/dictamen_08/`. Nada de esto movió una cifra
publicada. Lo que ya tenía tu firma pendiente (snapshot.py:140, el campeón
cuando sello y fuente discrepan, el timeout O(n²) de noticias, `.env` en
644) sigue arriba, tal cual.

## 22. La frase de potencia del 5.1, en dos versiones — elegí una (Frente E)

Medido en `GEMELO/simulador/potencia_por_metrica.{json,md}` (500 réplicas
por celda, semilla sellada; σ_pred de los intervalos sellados 4,3 pp).
Tres métricas, la misma ventana: **dirección** (acierto del signo del gap
contra «siempre al alza», permutación de signo por día), **MAE** (error
del gap contra el de la predicción cero) y **CRPS** (densidad predictiva
contra la climatología). Sobre las 35 fechas selladas de la calibración,
el z de cada una: dirección 1,1, MAE 1,7, CRPS 1,78.

**Versión «dirección» (la del diseño congelado, V1):**

> Con ~73 días sellados el 25-oct, la potencia para detectar una ventaja
> direccional verdadera de 9 pp es **0,31 [0,27, 0,35]**; de 6,5 pp,
> **0,19 [0,16, 0,23]**. Al efecto observado hacen falta **~229 días** para
> llegar a 0,80. El veredicto del 25-oct sobre la dirección será, con alta
> probabilidad, «no distinguible de cero» aunque la ventaja exista.

**Versión «magnitud» (contraste del campeón contra predecir cero y contra la climatología — NO es V4 ni V2, que comparan RETADOR contra campeón; lo que la muestra sí hace medible):**

> Con ~73 días sellados el 25-oct, la potencia para detectar que el modelo
> reduce el MAE del gap frente a la predicción cero es **0,90 [0,87,
> 0,92]**, y para el CRPS frente a la climatología **0,76 [0,72, 0,80]**.
> Al efecto observado, 0,80 se alcanza en **~95 días (MAE) / ~87 (CRPS)**.
> El 25-oct la magnitud SÍ puede hablar; la dirección no.

**Por qué las dos y no una:** la dirección es la pregunta que el diseño
hizo (V1) y la que el track record publica; la magnitud es la que la
muestra puede responder. Publicar sólo la segunda sería cambiar la pregunta
después de ver que la primera no tiene potencia; publicar sólo la primera
es callar que hay algo medible. La recomendación es publicar **las dos, en
ese orden**, con la palabra «potencia» y sin la palabra prohibida.

**Salvedad que manda (dictamen A, 2-sep):** el instrumento de potencia de
`horizonte.md` inyecta el efecto de forma homogénea y el adversario lo
midió **optimista** frente al simulador calibrado (diferencia media
+2,7 pp de potencia [1,9, 3,6] sobre 12 celdas). Las cifras de arriba son
del simulador, no de `horizonte.md`; la comparación pareada de la v2 de
`calibracion_instrumento.md` es la que fija cuánto.

Intentos del DSR de este frente: **3** (una métrica, un intento).

## 23. Tres propuestas con expediente (H1, H2, I) — `cola_decisiones.md` §23–25

> **Nota de la corrida 14 (acta §88.2):** **Z1 vive acá.** La §59 se cerró por remisión a este
> ítem: `visible_en` no es un campo del sellador, es la pregunta de H1. Mientras H1 no se decida,
> Z1 sigue abierta y es parte de este expediente.

Sello verificable por un tercero (segunda salida de red + copia de
insumos), pre-registro del RTL con criterio de muerte (y la corrección de
que 8,79 ms es un TCP a 1.1.1.1, no la FPGA), y V1-bis como ADICIÓN
fechada al criterio congelado. Las tres son tuyas; ninguna se construyó.

**Errata del §22 (2-sep, 14:50, dictamen E — NO CONCLUYENTE sobre las cifras
operativas):** (a) los «días para 0,80» van con intervalo o no van: el
extremo superior es **∞** en las tres métricas porque el IC del efecto
contiene el cero; (b) los 229 días son al +9,3 pp del ancla deduplicada, no
al +6,45 pp publicado (a ese efecto son ~480) ni a la rama +14,3 pp de
`cola_decisiones.md` §2a-ter (~100): **el mismo número vive entre ~100 y
~480 según una decisión que sigue en la cola** — ésa es la urgencia, no E;
(c) el 0,90 de MAE a 73 días es la potencia al efecto del GENERADOR; al
observado y bajo R2 es menor (banda en `potencia_por_metrica.md` v2);
**bajo R2 la magnitud tampoco habla el 25-oct**; (d) el 0,19 [0,16, 0,23]
viene de `calibracion_instrumento.json` A4/0.065, no de
`potencia_por_metrica.json`; (e) CRPS y MAE son UNA familia (98% de la
ganancia de CRPS es la media), y «predecir cero» no es la baseline pareada
(computado en la v2: la constante μ recupera el **7,3 %** de la ganancia de
MAE —el dictamen leyó el complemento, 0,405 es lo que el modelo gana SOBRE la
constante—); (f) intentos de E: **2**, no
3 (DIR es el endpoint congelado; el MAE ya está en el tramo ESTIM).
**§17 arriba y `cola_decisiones.md` §18 citan «potencia 0,36 [0,34, 0,37]» (cifra retirada, acta §75)
de `horizonte.md`, instrumento medido OPTIMISTA (+2,7 pp [1,8, 3,6],
dictamen A): con el simulador es 0,31 [0,27, 0,35].** La frase de dos
versiones no está lista para firma hasta que la rama del efecto se decida.

## 24. La ventana larga publicada (n = 14.618) está calculada sobre gaps con un defecto conocido — recompute para firma

El generador de gaps v1 omitía toda sesión posterior a un feriado LOCAL
(Tokio 4 de 101, Seúl 1 de 78, Taipéi 2 de 64, Fráncfort 2 de 31 sesiones
post-feriado presentes en v1; v2 las tiene todas). **Tamaño medido con la
señal cruda (dictamen B):** +670 filas (4,5 %) y las ventajas por bolsa se
mueven **−0,32 / +0,09 / +0,09 / +0,38 pp** (Tokio / Seúl / Taipéi /
Fráncfort), total −0,01 pp. **La n de la portada se mueve; las ventajas casi
no.** Recomputar con el modelo reconstruido mueve los doce bloques
(`cifras.py` los enumera) y lleva tu firma; hasta entonces el README publica
un n calculado sobre un defecto conocido desde hoy, y `cifras.Larga` lo
lleva escrito en su procedencia.

**Cifras v2 de `potencia_por_metrica.md` (15:02):** z por t de clúster
DIR 1,11 / MAE 1,69 / CRPS 1,76; días para 0,80 al efecto observado **223
[28, ∞) / 96 [20, ∞) / 88 [19, ∞)**; DIR al +6,45 pp publicado: 470; bajo R2:
2.728 / 175 / 200, todos [·, ∞). Potencia de MAE a 73 días: **0,90
(generador) / 0,86 (efecto observado) / 0,70 (bajo R2)**; CRPS 0,76 / 0,66 /
0,50; DIR 0,31 / 0,29 / 0,21. La frase del §22 se lee con esa banda o no se lee.

# Lo que agregó el bundle de agentes v2 (2-sep-2026, noche)

## 25. Instalar los dos hooks propuestos del bundle v2 — HECHO (2-sep-2026, noche)

**RESUELTO, no pendiente.** Nicolás corrió `bash
GEMELO/propuestas/hooks/instalar.sh`: los dos hooks vigentes son hoy copia byte a
byte de la propuesta (opción (a)), y `tests/test_hooks_propuestos.py` quedó
adaptado al estado post-instalación (10 tests, prueban el hook VIGENTE). Suite
completa `606 passed, 2 xfailed`. Acta `DECISIONES.md` §77. Lo que sigue abajo es
el texto original de la decisión, en pasado; se conserva como registro de qué se
firmaba, no como pendiente.


**Qué decidir, en una frase:** si `.claude/hooks/contexto-mki.sh` y
`guardia-reglas.py` pasan a ser las versiones de `GEMELO/propuestas/hooks/`
(el vigente más un bloque cada una; 0 líneas quitadas, verificado por
`diff` y por `tests/test_hooks_propuestos.py`, 8 tests).

**Qué desbloquea:** al abrir sesión, la rama del efecto con sus dos ramas
computables (n, p, Wilson) marcada DECISIÓN PENDIENTE, el conteo de intentos
del DSR y cuántos ítems esperan tu firma, leídos de la máquina; y el bloqueo
de reintroducir una cifra retirada en `.md` **y en `.py`** (regla de la casa
4). Hoy hay seis `.py` en HEAD que la propuesta cazaría al primer `Edit`
(`docs/bitacora_agentes_v2.md` §1 y §11).

**Costo:** `bash GEMELO/propuestas/hooks/instalar.sh` muestra los dos
`diff`, pide confirmación y copia. El arranque tarda ~4 s más. Zonas ciegas
declaradas en el docstring: sólo evalúa el texto nuevo del Edit/Write (falla
hacia denegar); un `.txt` o un heredoc por Bash no pasan por él.

**Por qué no lo hizo la sesión:** el hook vigente se protege a sí mismo,
`settings.json` deniega `Edit` sobre `.claude/hooks/` y el harness denegó la
escritura por Bash. Acta §76.

**Opciones:** (a) instalar; (b) instalar sólo el bloque de arranque
(copiar `contexto-mki.sh` y no el guardia); (c) rechazar y borrar
`GEMELO/propuestas/hooks/`. Recomendación: (a); si el bloque 8 molesta en la
práctica, la marca de retiro dentro del texto nuevo lo levanta.

# Lo que agregó la novena corrida (noche del 2 al 3-sep-2026)

Las decisiones D1, D2 y D3 del encargo 09 **no esperan firma: ya están
aplicadas** (acta §78; `bitacora_09.md`). Lo que sigue es lo nuevo que sí la
espera, más lo que esta corrida cerró de la lista anterior (marcado arriba
en su ítem, con fecha, sin borrar).

## 26. Aplicar el parche de `snapshot.py:140` — FIRMADO (acta §82.2 a, b, c, d), PENDIENTE DE APLICAR junto con el guardia del §49

**Qué hay que decidir:** lo mismo que el §1 (aplicar el parche y declarar el
corte de método). Lo que cambió esta noche es que ya no hay nada que
preparar:

- `GEMELO/propuestas/parches/snapshot140.diff` aplica limpio contra el
  `snapshot.py` de `HEAD` (`git apply --check` rc=0); una sola expresión.
- `tests/test_parche_snapshot140.py` (6 tests, en la suite, VERDE con el
  archivo sin parchear): copia a tmp, aplica el diff, calendario real,
  fijación (sello tardío 01:30 UTC del 31-jul → 31-jul parcheado, 3-ago
  original) y no-regresión (sello 22:15 UTC → misma sesión).
- `GEMELO/resultados/corrida09/parche_snapshot140_tabla.md`: las **25 filas
  malas** (4 fechas de emisión: 07-05: 8, 07-29: 7, 08-03: 3, 08-05: 7; XTKS
  14, XKRX 6, XTAI 4, XETR 1), las 25 `verificada` (6 aciertos, 19 errores
  contra la sesión equivocada), **y bajo el parche las 25 serían
  `no_verificable_timing` y 0 verificables** — no 15 como decía la cola: es
  por construcción (la sesión sellada difiere de la correcta sólo si una
  sesión abrió entre `available_at` y la emisión, y ésa es la correcta, ya
  abierta). Ninguna fila nueva desde el 5-ago (los 20 sellos posteriores
  sellaron entre 22:15 y 23:45 UTC). La declaración del corte de método está
  lista para acta en la §5 de ese archivo.

| Opción | Consecuencia |
|---|---|
| **(a) Aplicar el diff + bump de `PLATAFORMA_VERSION`** *(recomendada)* | El corte queda auto-documentado en cada fila; las 25 viejas no se tocan (errata, no backfill). |
| (b) Aplicar sin bump | Hay que anotar a mano el `timestamp_utc` del primer sello posterior, en el momento. |
| (c) No aplicar | Cada sello tardío futuro produce una fila verificada contra una sesión que no era la suya. |

**Costo de decidirlo: 5 minutos.** La copia de insumos (`GEMELO/INSUMOS/`,
§16b) va en el mismo bump si se firma; no está en el diff.

## 27. `sqlite_sequence` duplicada en `senales.db` — limpiar o dejar (frente 2a)

**Qué hay que decidir:** si se limpian las 4 filas sobrantes de
`sqlite_sequence` (8 filas para 4 tablas; rowid 1-4 vivas con seq =
max(id), rowid 5-8 restos de la composición canónica del 30-ago, p. ej.
`verificacion_apertura = 253`). MEDIDO en `corrida09/importador_roundtrip.md`
§5. Riesgo de colisión de ids: **nulo** (SQLite usa `max(seq, MAX(rowid))+1`).
Es lo único de `senales.db` sin camino de vuelta por CSV, y **no es una fila
sellada** — pero es una escritura en la base sellada, así que es tuya.

| Opción | Consecuencia |
|---|---|
| **(a) Dejarla** *(recomendada)* | Cero riesgo; el importador ya la reconstruye bien (próximo id = max+1 en las 4 tablas). |
| (b) `DELETE` de las 4 filas sobrantes | Estético; una escritura en la base sellada fuera del sello. |

**Lo que el frente 2a cerró sin firma:** el importador (`scripts/restaurar_backup.py`,
acta §42) cumple el criterio de aceptación del encargo: 5 tablas, 2.301 = 2.301
filas, 25.082 celdas, **0 discrepancias**, `plataforma_version` 42/42 idénticas,
floats `repr`-exactos, ids surrogados 2.259/2.259; `tests/test_importador_roundtrip.py`
(16 tests) en la suite con contraprueba. Stale sin editar: `.claude/agents/integridad-datos.md:71`
(«cuando exista el importador») y `docs/RESTAURAR.md` §Pruebas (dice que sólo
`verificacion_puntaje` coincide; hoy coinciden las 5).

## 28. La réplica permanente — ocho decisiones en `GEMELO/diseno/replica.md` §8 (frente 2e)

Diseño escrito, sin código. Van a la cola (`cola_decisiones.md` §29) las ocho:
quién gana (rec. A: la titular siempre), qué máquina (rec. el Mac con
`caffeinate` en la ventana), retención (rec. 90 días para los `.md`; JSONL y
base sin límite), séptimo job de comparación a las 21:00 con alerta pasiva,
N = 5 días de PARIDAD para promover, marca `data/backups/titular.json`,
guardia de titular como `ExecStartPre` del reporte de las 18:25, y no cambiar
el default de `FECHA_CORTE`. Dos avisos medidos: la skill `switch-titular` que
cita el encargo **no existe** (el orden vive en `modo-emision`), y **la
réplica gasta presupuesto de IA** (`mki_noticias.py` no consulta `modo`).

## 29. La frase de potencia del 5.1, en dos versiones, con n, intervalo y fecha — REEMPLAZA al §22 (frentes 1b y 3c; v2 tras el dictamen)

Medido con el simulador calibrado (`horizonte.md` ruta 3, v2: 1.000 réplicas
por celda, α a 3.000, bisección con 3 semillas; `potencia_por_metrica.json`;
`corrida09/frase_potencia.md`). Ancla: cadena local a 31-ago con la regla
firmada, n = 246 en 35 días (**no** la canónica del README, 28-ago, n = 238:
divergencia declarada, misma regla, tres sellos más). Registro de intentos al
escribirla: 310. El §22 queda superado. **Dictamen 1b/3c (adversario, 12:20):**
la tabla y la pareada de la ruta 3 sostienen; el intervalo de «días para 0,80»
de la v1 no (medía sólo Monte Carlo con una semilla); la frase «cae antes del
25-oct» no sostiene y se retiró. Lo que sigue es la v2 con esas exigencias.

**Versión «dirección» (V1, secundaria bajo D3):**

> Con ~73 días sellados el 25-oct, la potencia para detectar una ventaja
> direccional verdadera de 9 pp es **0,30 [0,27, 0,33]**; de 6,5 pp, **0,18
> [0,16, 0,21]**. Para 0,80 hacen falta **≈263 días sellados a 9 pp** (rango
> Monte Carlo [229, 296]; banda paramétrica de la ruta 1: 248 [109, 370]) →
> **18-ago-2027** [25-jun-2027, 8-oct-2027 por MC], y ≈510 (ruta 1: 475
> [209, 709]) → 6-sep-2028 a 6,5 pp. El veredicto del 25-oct sobre la
> dirección será, con alta probabilidad, «no distinguible de cero» aunque la
> ventaja exista.

**Versión «magnitud» (V1-bis propuesta, primaria bajo D3):**

> Con ~73 días sellados el 25-oct, la potencia para detectar que el modelo
> reduce el MAE del gap frente a predecir cero está en la banda **0,90 / 0,86
> / 0,70** (generador de 9 pp [0,87, 0,92] / efecto observado [0,83, 0,89] /
> bajo R2 [0,66, 0,74]); para el CRPS frente a la climatología **0,76 [0,72,
> 0,80]**. Días para 0,80 en MAE **al efecto observado** (+0,44 pp, IC t de
> clúster [−0,09, +0,96]: contiene el cero): **96 [20, ∞) → 1-dic-2026**
> [27-ago-2026, ∞); bajo R2, 175. Si el efecto fuera el del generador de 9
> pp, ≈58 días (interpolación en log(D), verificada directa 0,80–0,82; sólo
> Monte Carlo). **Ninguna fecha encabeza:** el 25-oct fija ~73 días y lo
> que la muestra dice es la banda de potencia a ese horizonte; una fecha de
> 0,80 sólo vale condicional a un tamaño de efecto cuyo intervalo contiene
> el cero.

**Lo que hay que saber al firmar:** las dos van juntas y en ese orden;
ninguna al README sin firma; la magnitud contrasta campeón contra
cero/climatología (no es V2 ni V4); MAE y CRPS son una familia; «contra
cero» mide también la deriva del gap (m > 0 bajo ventaja nula el 54 %:
`tipo1_conjuncion_v1bis.json`) — para «habilidad» el adversario exige la
climatología causal (§30); la interpolación en log(D) no estaba prefijada
(lineal daría ≈61); la ruta 2 − ruta 3 sobre las 12 celdas de A4 da +2,45
[1,64, 3,27], comparable con el +2,67 [1,85, 3,55] del dictamen A (7 de las
28 celdas están en techo).

## 30. La enmienda V1-bis v2 — cambio de PREGUNTA, y un conflicto con D3 (frente 1c)

`GEMELO/preregistro/enmienda_v1bis.md` v2, con el dictamen pegado al pie.
El adversario dictaminó: **no es un cambio de vara, es un cambio de
pregunta** (qué demuestra el proyecto), firmable como tal. Lo que espera
firma: (1) adoptar V1-bis v2 como adición fechada bajo `DISEÑO.md` §6.1,
etiquetada como cambio de pregunta; (2) la **conjunción V1-bis ∧ V1** (si no,
afloja: un retador que gane en magnitud y pierda en dirección pasaría); (3)
salida α (el veredicto bajo V1-bis se evalúa sólo sobre sellos posteriores al
3-sep) o β (contaminación declarada); (4) V2 con IC de día, V4 como regla
general «todo nivel numérico del §6 es descriptivo», R1 y R2 sobre la métrica
primaria con la regla operativa «el IC de día sin 15–23 jul sigue excluyendo
el cero»; (5) **el conflicto: D3 dice «MAE contra predecir cero»; el
adversario exige que decida la climatología causal** porque «cero» mide la
deriva (54 % de m > 0 bajo ventaja nula). La v2 publica los dos y hace decidir
al de climatología; si preferís «cero», la enmienda vuelve a la v1 en ese punto
con el tipo I medido a la vista (MAE contra cero 0,04–0,05: correcto como
test; lo que mide es otra cosa). Hasta la firma, el juez lineal de esta
corrida es **EXPLORATORIO** (no computa como evidencia de R1).

## 31. La ventana del dedup retroactivo de noticias, y retirar el parche del timer (frente 2c)

El O(n²) está corregido en `noticias.py` (marca en tabla `meta`, ventana ±10
días; `corrida09/noticias_on2.md`). Dos cosas tuyas: (a) **ventana 10 vs 30
días**: 10 deja pasar 11 republicaciones de 11,9–138 días (≈ 0,0005 USD cada
una en Haiku; el decaimiento 0,7^días ya las pesa poco); 30 recupera 3 y
triplica el costo diario (~35 s → ~100 s); rec. 10. (b) **El parche
`TimeoutStartSec=2700` de `parche_timeout_noticias.md` queda innecesario y
no debería aplicarse**: hoy ≈ 13–15 min (primera pasada 615 s + RSS + Haiku),
desde mañana ≈ 5–6 min; 1.800 s alcanza. Confirmalo con la línea nueva del
log de hoy («dedup retroactivo: … en X s»).

## 32–35. Las cuatro tarjetas de `corrida09/tarjetas_09.md` (frente 2d)

Cada una con opciones, costo medido sobre datos reales, recomendación
PROPUESTA y «el día después». En una línea cada una:

- **32. Abstención por sello tardío.** Rec. **A** (salto de sesión, medido por
  calendario con `sesion_correcta`, no por reloj): 15/269 filas en 2 fechas
  (3 aciertos y 12 errores se irían); como flag retrospectivo en el campeón
  y regla de emisión sólo en el retador. B ≥ 19:00 abstendría 32; B ≥ 20:30 ≡
  ≥ 20:00 (apertura de Seúl) 10. La ventaja «sin A» no se publica.
- **33. Qué significa `ts_emision`.** `timestamp_utc` y `creado_en` son el
  mismo instante por construcción; ninguno dice cuándo la fila se hizo
  pública. Rec. `commiteado_en` (aditivo, una línea en `senales.guardar_snapshot`)
  + `publicado_en` escrito por backup y reporte llenando sólo el campo vacío,
  nunca cambiando un valor.
- **34. `Persistent=true`.** Journal no leído (tu restricción): sólo
  `data/*.log`, en UTC, desde el 25/26-ago. Rec. **M**: mantener en
  noticias, reporte, backup, vigía y re-chequeo; para snapshot, con el parche
  `:140` firmado `true` es seguro; sin él, `false` o guardia. Orden: primero
  el parche, no tocar timers.
- **35. Campeón cuando sello y fuente discrepan (28-ago).** Rec. **(a) las
  filas selladas son el campeón y B2 las lee, + C3 copia de insumos**, en el
  mismo bump que el parche `:140`. Escrito: el sello es «emitido antes»,
  no «reproducible después»; C3 le daría la segunda hacia adelante, nada
  hacia atrás.

## 36. Lo del frente 2f que espera firma

- `GEMELO/propuestas/parches/motor_concat.diff` (tres `sort=True`, byte-idéntico
  verificado por `tests/test_parche_motor_concat.py`, 10 passed): aplicar o no
  (`motor.py` es intocable; la regla cero manda).
- **`^VIX3M` sin datos en la caché desde el 17-jul**: con ffill acotado a 5 d,
  C2/C3 del WS2b sólo se reproducen sobre 79 filas. Verificar si Yahoo dejó de
  publicarlo (exige red: tuya) — afecta a toda re-corrida del WS2b/WS3 y al juez
  lineal (C2).
- Tarjetas Q1 (ventana larga a la convención congelada: parche del medidor +
  test ahora, re-corrida después), Q3 (errata en §32.5 de `DECISIONES.md`) y
  Q4 (IC en la fila de Fráncfort) en `corrida09/ws4_cinco_preguntas.md`.

## 37. Dictamen del `director-programa` sobre las recomendaciones de 2d y 2e (3-sep, 13:00)

Tarjetas: **T1 SUSCRIBE** (A como flag retrospectivo, regla sólo en el retador,
«sin A» no se publica); **T2 CAMBIA**: primero la alternativa barata
(`publicado_en` escrito por los jobs, sin tocar `senales.py`); `commiteado_en`
sólo si va en el mismo bump que `:140`, nunca como corte aparte sobre un
intocable; **T3 SUSCRIBE**; **T4 SUSCRIBE (a)**, y la copia de insumos C3 es un
frente nuevo que entra después de firmar `:140`, no la misma noche. Réplica
(§28 / cola §29): 1 SUSCRIBE (bloquea el resto); 2 SUSCRIBE sólo después de
firmadas 1 y 6; 3 SUSCRIBE; **4 AHORA NO** (un timer más en la única máquina
que emite: comparar a mano N días primero); 5 SUSCRIBE; 6 SUSCRIBE; **7
CAMBIA**: la guardia sólo en el vigía mientras haya una sola máquina (un
pre-paso nuevo que falla apaga el reporte del titular sin réplica que lo
cubra); 8 SUSCRIBE. Y el orden de firmas que propone: **primero V1-bis + §30,
después el parche `:140` con bump**; sobre el juez lineal, su objeción está
registrada en la nota de dependencia del pre-registro (corrió EXPLORATORIO
por orden del encargo, con los dos denominadores).


## 38. ¿El dedup nuevo de noticias obliga a mover `FEATURE_VERSION`? (6-Sep-2026, exigencia 4 del `guardian-constitucion`)

**Lo que nadie había dicho.** El §31 pregunta por la VENTANA del dedup
retroactivo. Lo que faltaba es dónde desemboca: `senales.py` sella
`puntaje_ia = puntaje_v0 × 0,7 + ((sentimiento + 1) / 2) × 0,3`. El
sentimiento de noticias entra con peso 0,3 en una columna **sellada**, y la
deduplicación lo alimenta. Cambiar su método es un corte de método **dentro**
de un insumo sellado, no una mejora interna del job.

**Medido en producción** (`data/noticias.log`, no sobre copia):

| corrida | comparaciones | duplicados borrados | duración |
|---|---|---|---|
| 3-sep 21:50 UTC (primera) | 4.921.843 | 20 | 615,9 s |
| 4-sep 21:50 UTC (diaria) | 445.139 | 13 | 54,0 s |

El sello de las 18:15 del 3-sep es el primero que descansa sobre el método
nuevo. Evidencia colateral de que el defecto era real: el job del 1-sep quedó
en «titulares guardados» sin analizar y el del 2-sep no pasó de la línea de
arranque.

**Lo que NO está en juego.** La señal verificada —`apertura_estimada_pct`, el
gap del track record— no depende de este insumo: el motor no lee noticias.
Ninguna fila sellada se reescribe. `MODELO_VERSION` no se toca.

**Opciones.**

1. **Mover `FEATURE_VERSION`** y declarar el corte en el acta: `puntaje_ia`
   antes y después del 3-sep no son la misma variable, y cualquier análisis
   que la use tiene que respetar el corte. Costo: una versión más que trazar;
   no reinicia el track record (eso sólo lo hace `MODELO_VERSION`).
2. **No moverlo** y dejar el corte declarado sólo en `DECISIONES.md` §78.4
   bis. Costo: dentro de un año, quien mida `puntaje_ia` a lo largo del
   tiempo no tiene cómo saber que el método cambió sin leer el acta.
3. **Volver la ventana ilimitada** (revierte el corte, reintroduce el O(n²)).
   Descartada salvo que la ventana misma se juzgue mal elegida en el §31.

**Recomendación.** La 1, y en el mismo acto que se resuelva el §31: la ventana
y el bump son la misma decisión mirada desde dos lados.

**El día después de la firma.** Si es la 1: `version.py` sube
`FEATURE_VERSION`, el acta declara el corte con su fecha, y las consultas que
agrupen `puntaje_ia` filtran por versión como ya hacen con `modelo_version`.
Si es la 2: no se toca nada y este ítem se cierra como decisión tomada, no
como pendiente olvidado.



---

## 39. Los tres juegos de parámetros del riel de dinero — cuál rige (corrida 10, bloque 3)

**Qué se decide.** Cuál de los tres juegos de `dinero/reglas.json` rige el riel
de dinero. Mientras no haya firma **rige `conservador`, por regla escrita del
encargo y NO por su resultado en la cuenta en papel**.

**Ninguno se inventó.** Cada número sale de una regla de derivación en
`dinero/derivacion.py`, y `tests/test_dinero.py` la recomputa y compara: mover
un número a mano pone la suite roja.

| | conservador | medio | agresivo |
|---|---:|---:|---:|
| umbral de señal | 3,49 pp | 1,99 pp | 0,91 pp |
| tope de posición | 25 % (K=4) | 33,3 % (K=3) | 50 % (K=2) |
| tenencia mínima | 60 días hábiles | 20 | 5 |
| presupuesto diario / semanal | 125 / 125 USD | 166,7 / 250 | 250 / 500 |
| apaga a una pérdida de | 15,6 % (1σ) | 23,4 % (1,5σ) | 31,2 % (2σ) |
| exige intervalo que no cruce cero | sí | sí | **no** |
| **comisiones medidas, % del capital** | **14–25 %** | **27–31 %** | **43 %** |
| instrumentos comprables con su tope | 7 de 36 | 8 de 36 | 13 de 36 |

**Lo que la cuenta en papel midió, y hay que leerlo con su límite.** La señal
que alimentó los tres **no tiene información** (sorteada, semilla declarada):
lo medido es fricción, no habilidad. El agresivo pierde contra `SMH` en las 4
pasadas del barrido con el intervalo entero bajo cero. Los otros dos no se
distinguen del cero. **Las columnas de resultado del barrido no son comparables
entre sí** —el deslizamiento cambia qué instrumento entra en el margen, o sea el
camino— y por eso no hay ranking en la tabla ni lo va a haber.

**Recomendación.** Ninguna. Este ítem existe precisamente para que la elección
no la haga quien vio los resultados. Lo que sí se recomienda es leer antes el
§40: con 500 dólares, el conservador gasta la cuarta parte del capital en
comisiones, y eso condiciona la respuesta más que cualquier preferencia de
riesgo.

**El día después de la firma.** `juego_activo` en `dinero/reglas.json` toma el
valor firmado y el acta lo declara con su fecha. Sin firma, no pasa nada: el
conservador ya rige.

---

## 40. El arancel real del corredor — el supuesto que hoy sostiene todo el riel de dinero

**Qué se decide.** Contra qué tarifario público se reemplaza el supuesto de
costo de `dinero/reglas.json`, que hoy es **SUPUESTO NO VERIFICADO**: 0,005 USD
por acción, mínimo 1,00 USD por orden, tope 1 % del monto, 5 pb de
deslizamiento por lado.

**Por qué no es un detalle.** Con esos números, **una orden de una acción de
menos de 100 USD paga exactamente el 1 %**, y rotar la cartera con 500 dólares
cuesta entre el 14 % y el 43 % del capital en comisiones. El criterio **M2** del
pre-registro (`dinero/preregistro_dinero.md` §3) mata el riel si la comisión
supera el 25 % del capital: **con el supuesto actual, M2 se dispara casi antes
de empezar**. Si el arancel real es distinto, cambia la conclusión del riel
entero, no un decimal.

**Lo que hace falta.** El tarifario publicado del corredor que Nicolás abra —no
hay cuenta, así que no hay tarifario que leer— y si ofrece **acciones
fraccionarias**, que es la otra mitad del problema: el ETF que el proyecto usa
de benchmark (`SMH`, 567,01 USD al 4-sep) **no se puede comprar entero con el
techo del presupuesto**.

**El día después de la firma.** Se actualiza la sección `costos` de
`dinero/reglas.json`, se regeneran `docs/universo_operable.md` y la cuenta en
papel con `python -m dinero.mapa` y `python -m dinero.cuenta_papel`, y el acta
declara qué cambió. Nada más depende de esto.

---

## 41. ¿Los registros de intentos se fusionan? — FIRMADO (acta §82.6, 7-sep-2026)

**Decidido: separados**; el riel integrador, descartado. Nada que ejecutar; la condición de
revisión (una pregunta que abarque los dos rieles) está escrita en el acta y en
`dinero/registro_intentos.FAMILIA_HERMANA`. Nada queda pendiente de vos.

## 42. ¿La cuenta en papel se reconstruye o se descarta? — FIRMADO (acta §82.4, 7-sep-2026)

**Decidido: opción A, reconstruir.** **Ejecutado en la corrida 11 (bloque 2):** E1, E3, E4,
E5, E6 aplicados en `dinero/`, gate de invariancia en verde, página republicada como v2
(`dinero/resultados/cuenta_papel.md`, PROPUESTA hasta los dictámenes). La errata del
8-sep a esta tarjeta (§82.4) se aplicó antes de que ningún frente la leyera. Ver §47 y
§48 abajo por lo que la reconstrucción abrió.

## 43. El período de M2, que hoy no se puede leer (cierre de la corrida 10) — **FIRMADA el 19-sep-2026 (acta §88.7 y §88.11 a §88.13)**

> **FIRMADA (§88.7, §88.11, §88.12, §88.13).** M2 se lee en **%/año** (opción c); umbral **8,3 %/año**
> (25/3); el **deslizamiento no cuenta**; acumulado desde el primer aporte con **primera lectura
> válida a las 52 semanas**; **cuenta congelada como estado aparte** que no cuenta como M2 cumplida.
> Redactada como **§9 de `dinero/preregistro_dinero.md`** por la corrida 14 (bloque 4.4), en estado
> PROPUESTA — y el `estadistico-adversario` la dictaminó **NO APLICABLE: FALTAN DEFINICIONES**, con un
> defecto de redacción que la corrida corrigió antes de que llegara acá (afirmaba que el umbral «no
> endurece ni ablanda», y es **3× más duro** a 52 semanas: `medio` pasa de 0/20 a **19/20** semillas).
>
> **Son SEIS las definiciones que faltan, no cuatro** (la primera versión de esta nota listaba cuatro; lo
> corrigió el `curador-epistemico`, porque omitía justamente la urgente):
>
> 1. **El denominador durante la rampa de aportes.** La bifurcación real es **ponderado por tiempo o no**
>    (las otras dos opciones son numéricamente la misma para todo h ≥ 5). Factor 1,0375× con el calendario
>    actual, **1,957× si el flujo fuera sostenido** — más que toda la distancia entre `conservador` y
>    `medio`. Las cifras de la §9 ya usan «aportado a la fecha de lectura».
> 2. **Qué es exactamente «congelada»**, y la cifra «5 de 20» **no mide el concepto que el acta firmó**:
>    el código usa «26 semanas sin movimiento» y §88.13 define un **estado de caja**; sólo se implementó
>    una de las dos condiciones que pedía E4, y la caja se verificó a mano en 2 de las 5 semillas.
> 3. **Si una cuenta congelada mata la pista o sólo sale del cómputo.** §88.13 firma una **tercera** cosa
>    («estado aparte, y se informa como tal»); E13 pedía que **disparara** M2. La diferencia decide si el
>    riel muere o se pausa.
> 4. **Dónde vive el contador de «lecturas de criterio»** (§88.14 lo deja sin dueño).
> 5. **URGENTE — qué es «el primer aporte».** Es el cero de *h* y la identidad del denominador, y no está
>    definido. Con la cuenta IBKR **ya fondeada con 5,00 USD** (§88.10), bajo la letra de la enmienda
>    **dos órdenes al mínimo dan 14 %/año y M2 DISPARA**; las mismas cinco órdenes sobre 500 USD dan
>    0,35 %/año. **Cien veces de diferencia según qué aporte cuente**, y toca la validez de la propia
>    enmienda: si *h* ya arrancó con ese fondeo, puede estar llegando tarde a su propio reloj.
> 6. **La convención de anualización** (`× 52/h` lineal) **no está firmada**: §88.7 firmó «tasa anualizada
>    (%/año)» y el factor lineal es una elección de módulo — la que produce el sesgo que premia a la
>    cuenta que dejó de operar.
>
> Más cuatro huecos menores (D7 a D10) en `dictamen_14/adversario_m2.md`. Y una advertencia del adversario
> que no bloquea el texto: mientras `GEMELO/simulador/` no tenga múltiples trayectorias de mercado,
> **ninguna afirmación de la forma «M2 dispara cuando debe» está autorizada**.
> **El texto original de la tarjeta no se borra:**

*(Encabezado anterior, conservado: FIRMADO el 8-sep (§84.4.5) y declarado NO APLICABLE el 9-sep:
vuelve con la pregunta exacta.)*

> **Nota 9-sep-2026 (corrida 12, bloque 8.1).** Recomputado sobre la v2 (`GEMELO/resultados/m2_periodo.md`,
> 20 semillas): conservador 3,9 % a 52 semanas [3,56, 4,58], 8,6 % a 104, 12,4 % a 156 (techo 13,1 %),
> **no cruza el 25 % en ningún horizonte**; medio 26,6 % a 156 (17 de 20 semillas cruzan). Tasa anualizada
> del conservador **3,9 %/año**, estable a través de los tres horizontes. El adversario
> (`dictamen_12/adversario_43_periodo_m2.md`) declaró la firma **NO APLICABLE**: el 25 % no tiene unidad
> de período (numerador flujo, denominador fijo en 500 USD), el «horizonte pre-registrado» que la firma
> invoca no existe (el §2 escribe un piso prospectivo de duración), y elegirlo con las tres respuestas a
> la vista es lo que el §5 declara ilegítimo aunque acá sea inerte. **Se computaron 12 lecturas y se eligió
> 1** (declarado). **La pregunta exacta que vuelve:** ¿en qué unidad (%/año es la única invariante al
> período) y contra qué umbral se lee M2, y sobre qué ventana de la cuenta prospectiva? Más la condición de
> supervivencia operativa (5 de 20 semillas conservadoras se congelan y M2 las puntúa bajo por la razón
> equivocada) y si el deslizamiento cuenta (§7 B (ii)). Recomendación del adversario: **(c)**, umbral
> re-declarado en %/año ANTES de la primera fila prospectiva; enmienda en `preregistro_dinero.md` §8.
> Dónde vive el contador de «lecturas de criterio» (distinto del DSR) es también tuyo.


> **Nota 8-sep-2026 (corrida 11):** las cifras de esta tarjeta (14 % a 43 %; 10,1 %, 21,8 % y
> 14,8 % de peor ventana móvil de 52 semanas) son de la cuenta v1 RETIRADA por fuga y **no se
> citan**; con la v2 hay que recomputarlas, con banda entre semillas, antes de firmar el
> período. Lo que la v2 ya dice: el juego por defecto gasta 12,4 % sobre 156 semanas (mediana
> de 20 semillas), la mitad de la vara; ver `preregistro_dinero.md` §7. La pregunta sigue
> siendo la misma.

**Qué hay que decidir en una frase.** M2 dispara si la comisión acumulada supera
el 25 % del capital aportado «en el período», y hay que decir **qué período**.

**Por qué no es cosmético.** El pre-registro concluía que M2 estaba «a punto de
dispararse antes de empezar» citando el 14 % a 43 % (cifra retirada el 7-sep-2026, `dictamen_10/auditor_lookahead.md` E8), que está medido sobre **156
semanas**. Sobre la ventana de **52 semanas** que la §2 declara como período de
evaluación, **ningún juego llega al 25 %**: la peor ventana móvil de 52 semanas
da 10,1 %, 21,8 % y 14,8 %. Recién a 104 semanas se dispara, y sólo para dos
juegos. O sea que **la conclusión publicada estaba invertida**, y encima la
cifra que la sostenía está retirada por fuga.

**Cuánto cuesta decidirlo.** 5 minutos.

**Opciones.** (a) M2 se mide sobre las mismas 52 semanas del criterio —coherente
con el resto del §2, y entonces M2 **no** está por dispararse—. (b) M2 se mide
sobre la vida entera de la cuenta —más conservador, y entonces sí dispara, pero
compara contra un umbral pensado para un año—. (c) M2 se reescribe como tasa
anualizada, que es lo que la pregunta de fondo quiere saber.

**Recomendación: (c)**, porque una comisión acumulada sin período no es una
cantidad comparable con nada. Pero requiere recomputar sobre una cuenta sin
fuga, así que va **después** del §42.

---

## 44. M4 reescrita bajo multiplicidad, o M4 es decorativa (cierre de la corrida 10)

**Qué hay que decidir en una frase.** M4 dispara si la señal larga «no supera
**ninguna** de sus dos varas»; con 30 contrastes correlacionados a α = 0,05 esa
es una barra que el ruido puro pasa la mayoría de las veces, así que **M4 casi
nunca va a disparar**, y un criterio de rechazo que no rechaza no es un
criterio.

**Lo que ya se midió.** La familia real de esta página son **30 contrastes**
(cinco por celda), no 24: la cuenta vieja dejaba los seis de dirección fuera de
su propia corrección. Con Holm sobre los 30, **ninguno cruza α = 0,05**. El
reporte ahora lo computa él mismo y lo publica salga lo que salga.

**Cuánto cuesta decidirlo.** 15 minutos.

**Opciones.** (a) M4 se reescribe sobre la familia **corregida**: dispara si
ningún contraste sobrevive a Holm —hoy dispararía—. (b) M4 se reescribe sobre
**una** métrica primaria declarada por adelantado, que es lo que la enmienda
V1-bis (§30) decide para el otro riel: entonces M4 y V1-bis se firman juntas.
(c) M4 se retira y se declara que el riel no tiene criterio de rechazo por esta
vía.

**Recomendación: (b)**, porque hace que las dos ramas del proyecto usen la misma
convención y porque V1-bis ya está esperando firma. Y una nota que conviene no
perder: **con la familia corregida, M4 dispararía hoy.**

---

## 45. ¿El registro de intentos del riel largo pasa de 3 a 30? — FIRMADO (acta §82.1, 7-sep-2026)

**Decidido: opción (a), dos contadores declarados por separado**, y el aviso va donde el
3 se publica. **Ejecutado en la corrida 11 (bloque 7):** `dinero/senal_larga_reporte.py`
emite la nota con los dos números computados y el reporte se regeneró sin mover ninguna
celda. Nada queda pendiente de vos.



# Lo que agregó la corrida 11 (8-sep-2026)

## 46. Cablear (o no) la rama de coherencia al árbitro, y qué publica el README

**Qué hay que decidir en una frase.** Firmaste retirar las 15 filas (§82.3). Falta decir si
`backtest.linea_base.filtrar_sesion_coherente` pasa a aplicarse por defecto en `cargar()`
y en `cifras.sellada()`, y con eso el README pasa de n = 238 / +9,7 pp a n = 223 / +14,3 pp.

**El dato que faltaba, ya computado** (`GEMELO/resultados/intervalo_coherencia.md`, corte
2026-08-28, `excluir_cero`): la rama de coherencia da +14,3 pp con IC95 percentil de día
[−1,4, +32,1], t de clúster [−3,5, +32,2], permutación de día p = 0,111, ICC 0,42, DEFF 3,71,
n efectivo 60, sobre 33 días. **El intervalo contiene el cero en las tres rutas**, como el
acta predijo antes de computar. El retiro se lleva un día entero (5-jul, 8 filas) y mutila
otro (5-ago, 7 de 8), y los dos eran informativos con Σ = −4 cada uno. **Bajo R2 (sin el
15–23 jul) la rama cae a +7,8 pp, [−9,1, +25,6], permutación p = 0,433: hereda intacta la
ventana afortunada y se apaga igual que la regla firmada (+2,6 pp, p = 0,821).** Y +14,3 pp
es otro estimando (ventaja restringida a filas con sesión coherente), no «+9,7 medido mejor».

**Cuánto cuesta decidirlo.** 10 minutos. Ejecutarlo: los doce bloques del README se mueven
en el mismo acto (regla de la casa), media corrida.

**Opciones.** (a) Cablear y publicar 223 / +14,3 con su intervalo al lado. (b) No cablear:
el README sigue en 238 / +9,7 y la rama queda como consecuencia declarada. (c) Cablear
recién cuando el parche del §26 esté aplicado, para que el filtro y la regla maestra
operativa entren juntos. **Recomendación, marcada como tal: (c)**, porque el argumento del
§82.3 es que a esas filas las descarta la regla maestra, y la regla maestra sólo dispara
con el parche aplicado.

## 47. El presupuesto del riel de dinero, con la tabla a la vista (§82.7) — FIRMADO EN PARTE (acta §84.4.6 y 7, 8-sep-2026): piso ENTERAS y N = 40; el MONTO sigue abierto

> **Nota 9-sep-2026 (corrida 12):** aplicado en `regla_aporte_y_dimensionamiento.md` §5-bis y en el sellador
> (`dinero/sello_dinero.py`: el presupuesto con que se decide viaja dentro de cada fila, PROPUESTA). El monto de E2
> no se fijó (§84.4.7): ver §52 abajo.

**Qué hay que decidir en una frase.** Cuánto capital propio y en qué modo de compra.

**La tabla** (`docs/universo_operable.md`, «Censo por presupuesto y modo de compra», arancel
del §40): enteras 100 USD **7 de 36**, 250 USD **13**, 500 USD **29** (`MSFT` al borde),
1000 USD **33**; fraccionarias 36 de 36 a cualquier monto, con fricción de ida y vuelta
del 2 % que no se diluye, contra 0,70 USD fijos en enteras (cruce en 35 USD por orden). El
segundo día de censo NO aportó sesión nueva (el 7-sep fue feriado en NYSE): sigue siendo
censo de un solo día.

**Cuánto cuesta decidirlo.** 15 minutos con la tabla. **Recomendación:** ninguna; la firma
del escalonamiento (§82.7) dice capital propio y rango original.

## 48. La reconstrucción cambió el arancel de `reglas.json` y sus derivados, y el §40 sigue sin firma

**Qué pasó.** El encargo ordenó reconstruir con el arancel del insumo §40 (Pro Tiered,
enteras: 0,0035 / 0,35 / 1 %). `reglas.json` pasó a `0.2.0-PROPUESTA` y los parámetros
derivados se recomputaron por su regla: umbral conservador 3,49 → **1,35 pp**, medio
1,99 → 0,79, agresivo 0,91 → 0,38; apagado con σ hasta 2023-09-05 (14,17 %): 15,6 → 14,2,
23,4 → 21,3, 31,2 → 28,3. Con umbrales más bajos el diseño emite 200 a 450 órdenes en 156
semanas y la fricción da 12 % a 28 % del capital: **la manda el número de órdenes, no el
arancel** (lo que el §82.4 anticipó, leído después de computar).

**Qué hay que decidir.** (a) Firmar el §40 como arancel del riel (con la restricción de
SmartRouting). (b) Si los umbrales derivados tan bajos son lo que querés, o si k (2 / 1,5 / 1)
se revisa; revisarlo después de ver la cuenta es un grado de libertad y hay que declararlo
como tal si se hace.

## 49. El guardia de la rama del `except` (§82.2 c) — FIRMADO Y APLICADO (acta §84.2, 8-sep-2026)

> **Nota 9-sep-2026:** el parche está aplicado desde `1508fad`; la máquina lo confirma (`mki_vigia.py::chequear_ancla_temporal`). El texto de abajo describe el estado anterior.

`GEMELO/propuestas/parches/guardia_ancla_temporal.diff` toca `snapshot.py` (aviso en el
log cuando `available_at` cae al reloj de pared, por `except` o por `sox_fecha` vacío),
`mki_vigia.py` (chequeo `chequear_ancla_temporal`: filas de hoy con
`available_at == timestamp_utc` disparan la alerta) y `senales.py` (el verificador cuenta y
declara `sin_calendario`, el tercer tragador de excepciones). Elegí **alerta del vigía más
log, y no marca en la fila**: la evidencia ya está en la base y una columna nueva es cambio
de esquema en filas selladas. Test: `tests/test_parche_guardia_ancla_temporal.py` (6 tests,
sobre copias; verifica que los dos parches aplican juntos). **Se aplica en el mismo acto que
el §26.** Hoy el agujero es teórico: 0 de 319 filas 4.6.0 pasaron por la rama (bloque 6).

## 50. El instrumento del riel de dinero sub-cubre bajo la nula

`GEMELO/resultados/instrumento_dinero.md` (PROPUESTA): `contabilidad.comparar` discrimina
(criterio pre-declarado cumplido en las tres magnitudes), pero a 52 semanas el tamaño
bilateral es 0,086 [0,074, 0,099] contra 0,05 y la cobertura 0,914 [0,901, 0,926] contra
0,95; con ρ = 0,2 la cobertura baja a 0,885. Es el mismo defecto del percentil que el Frente
A midió en el riel de medición. **Cambiar el estimador después de ver la cobertura es un
grado de libertad**: la opción (t de bloques, más réplicas, bloque distinto) es tuya, y hasta
entonces cada `✓` de la cuenta en papel se lee sabiendo que el nominal 95 % es ~91 %.

## 51. Qué señal sella E0, y si las filas de la sonda cuentan para N (corrida 12, 9-sep-2026) — FIRMADA el 9-sep-2026 (acta §86.2): opción (a), la sonda etiquetada «prueba de maquinaria, no track record» hasta N = 40

**Qué hay que decidir en una frase.** El sellador prospectivo (`dinero/sello_dinero.py`) sella la
decisión del juego por defecto alimentado por la **sonda sin información** de la cuenta en papel,
porque el riel de dinero no tiene ninguna señal con ventaja medida (L1 refutada, WS2b negativo). El
encargo lo ordenó así («la decisión sale de `cuenta_papel`»); el pre-mortem marcó que 40 filas de
ruido publicadas como track record es el defecto. Se selló igual **con `senal_fuente` en cada fila y
el contador rotulado «prueba de maquinaria, no track record»**.

**Opciones.** (a) Seguir sellando la sonda hasta N = 40: E0 prueba maquinaria (timestamps,
available_at, inmutabilidad, timer) y se declara así; las filas nunca se leen como habilidad.
(b) Sellar la señal larga L1 (REFUTADA) para tener filas prospectivas de la hipótesis que se
puso a prueba, con su etiqueta. (c) No sellar ninguna señal hasta que exista una con estatus, y
que E0 se cierre sólo con la maquinaria probada. **Consecuencia de cambiar:** reinicia el
contador de N.

**Estado al 9-sep-2026 00:38:** la primera sesión ya está sellada con la sonda (33 filas, 0 compras,
`cuenta_para_N = 1` de 40). **Recomendación:** (a) con la etiqueta, porque lo que E0 compra es la maquinaria y eso no depende
de la señal; y decidir (b) o (c) después de ver las primeras filas es exactamente el grado de
libertad que el sellado existe para cerrar. **Cuánto cuesta decidirlo:** 10 minutos.

## 52. La ventana para fijar el monto de E2 «sin mirar resultados» se cerró con la primera fila (corrida 12) — FIRMADA el 9-sep-2026 (acta §86.3): opción (a), monto de E2 = 500 USD, fijado después de la primera fila de E0 (grado de libertad declarado frente a la regla 5.4, que no se enmienda); E1 completo antes de E2, E2 sólo con vara; cambios de monto sólo por acta firmada antes de E2 y durante la ventana de E2 el monto no se mueve

La regla de aporte 5.4 dice que el monto se fija ANTES de conocer el resultado de E0 y E1. El
§84.4.7 decidió no fijarlo en la corrida 12, y la corrida 12 selló la primera fila. Desde el
9-sep-2026 cualquier monto que se fije se fija sabiendo algo de E0 (aunque sea que la maquinaria
anduvo). **Qué hay que decidir:** fijarlo ahora con esa declaración, o reescribir la regla 5.4
para que el monto se fije antes de E2 y no antes de E0 (con la razón escrita). Ninguna de las dos
es cosmética: la primera es un grado de libertad declarado; la segunda es una enmienda a una regla
propuesta. **Recomendación:** ninguna; es tuya.

> **Insumo para la reevaluación del monto (corrida 13, encargo §8.3; no es tarjeta, no fija nada):**
> `GEMELO/resultados/universo_por_presupuesto.md` (PROPUESTA, descriptivo, dictamen del adversario en
> `dictamen_13/adversario_universo_presupuesto.md`): por presupuesto de 100 a 500 USD, cuántos de los 36 verificados
> alcanzan una acción entera al último cierre congelado (7 a 100 USD, 13 a 250, 29 a 500), la membresía en DESDE con la
> que juega la cuenta a cada techo (18 a 33), las semillas conservadoras congeladas antes de 156 semanas (5 de 20 a
> 500 USD, reproducción de la corrida 12) y la fricción a 156 semanas condicionada a vivas / congeladas. La tabla no se
> lee en columna (las filas no son pareadas: cambia la membresía).

## 53. Instalar el timer del sellador E0 (`GEMELO/propuestas/systemd/mki-sello-dinero.{service,timer}`) — FIRMADA el 9-sep-2026 (acta §86.4): instalado por Nicolás; la hora pasó de 21:00 Santiago a `Mon..Fri 23:30 America/New_York` tras la primera noche (34 de 36 columnas faltaban a las 21:00). El encargo 13 manda producir el dato de la sonda; elegir la hora siguiente sigue en espera de firma (§58)

`Mon..Fri 21:00 America/Santiago`, argumentado en el archivo (fuera de la ventana 17:50–20:30; ≥ 3 h
después del cierre de NYSE todo el año; ≥ 12 h antes de la apertura objetivo). **Instalar un timer es
acto tuyo.** Hasta entonces el sello se corre a mano (`python -m dinero.sello_dinero --sellar`) o no
se corre, y los días sin sello no cuentan para N. Costo de postergarlo: cada noche sin timer es una
sesión menos hacia N = 40.

## 54. `ibapi`: la dependencia autorizada (D-C bis) no es instalable con licencia verificada desde PyPI — **FIRMADA el 19-sep-2026 (acta §88.8)**

> **FIRMADA (§88.8), opción (a), con su condición a la vista:** Nicolás instala el `ibapi` oficial
> del zip de IBKR, **licencia no comercial leída por él**, y entonces se descomenta la línea de
> `requirements.txt`. El Gateway va **dentro de WSL** con la versión Linux (§88.9). Estado de la
> cuenta al 19-sep: solicitud completa y fondeada con 5,00 USD, **todavía en revisión** (§88.10);
> **E1 no empieza hasta el correo de aprobación**. La corrida 14 no tocó `corredor/`, no instaló
> `ibapi` y no abrió ninguna conexión. Texto original conservado:

Hallazgo de la corrida 12 (bloque 4.1, fuentes en la bitácora): el cliente Python oficial de la TWS
API se distribuye desde `interactivebrokers.github.io` (API 10.50, 26-ago-2026) bajo la «TWS API
Non-Commercial License» con aceptación previa; el `ibapi` de PyPI es 9.81.1.post1 (dic-2020). Por eso
`requirements.txt` lleva la versión fijada **como línea comentada** y el adaptador (`corredor/ibkr.py`)
importa `ibapi` de forma perezosa. **Qué hay que decidir:** (a) instalarlo vos desde el zip oficial
(aceptando la licencia; ¿el uso del proyecto cabe en «no comercial / herramientas internas»?), y
entonces la línea se descomenta con la versión real; (b) otra ruta oficial (Client Portal Web API,
descartada en §84.4.2 por la sesión que expira). No se revirtió D-C bis: se anota.

## 55. Automatizar el método de los parches (`GEMELO/propuestas/test_parches_en_worktree.py`)

Aplica cada `.diff` de `GEMELO/propuestas/parches/` sobre un `git worktree` temporal y corre ahí los
tests de aislamiento (lección del `snapshot140.diff`, `docs/manual-agentes.md`). Toca `.git/worktrees`
y tarda segundos por parche: instalarlo en la suite es decisión tuya. Hasta entonces se corre a mano.

## 56. La distribución de k bajo la nula para la señal larga (re-dictamen D15)

El bloque `senal_larga` publica «1 de 6 celdas gana sin corregir» y «30 contrastes»; el adversario
exige que ningún «k de m» se publique sin la distribución de k bajo la nula con el ICC medido. La
corrida 12 separó los denominadores y declaró `k_bajo_la_nula: null`; **computarla es una corrida de
simulación (≈ el Frente A del riel de medición) y es un intento más del registro del riel largo**.
Decidir si se hace y cuándo.

## 57. Confirmar la definición operativa de «sesión que cuenta para N = 40» (una línea) — FIRMADA el 9-sep-2026 (acta §86.1): la definición queda tal como está en código; las sesiones perdidas no se recuperan con un segundo sello

N = 40 lo firmaste (§84.4.7); la definición de qué sesión cuenta la escribió la corrida 12
(`regla_aporte_y_dimensionamiento.md` §5-bis, `dinero/sello_dinero.py`): sólo una fila `pendiente`
(available_at < timestamp_utc < apertura objetivo, por calendario) de un día con sesión en Nueva
York, con el insumo en la sesión inmediatamente anterior a la objetivo y COMPLETO (33 de 33 con
cierre). Días sin sesión, sellos tardíos e insumos incompletos o desactualizados se sellan igual y no
cuentan. Es la definición conservadora; es una definición de agente sobre una cifra tuya, y por eso
se confirma con una línea o se cambia (y cambiarla reinicia el contador).

## 58. A qué hora dispara el sellador de dinero, y qué es «insumo completo» (corrida 13, 19-sep-2026) — **FIRMADA EN PARTE el 19-sep-2026 (acta §88.1)**

> **Regla de decisión PROPUESTA en `GEMELO/propuestas/regla_58.md`, sellada el 29-sep-2026 a las
> 23:08:17 de Chile con sha256 `ca2ccd536f9d956c2b4a8404ec800341f29e4a0e1f1cd20720c08eca15b9a436`,
> antes del primer dato de madrugada** (primer disparo de la franja: 01:05 del 30-sep) y antes de las
> 00:35, así que la noche del 29-sep es la primera candidata y el plazo es la sesión del 26-oct-2026
> (acta §91.3; dictamen y re-dictamen del `estadistico-adversario` en
> `dictamen_15/adversario_regla58.md`; anexo 1 fechado en `regla_58_anexo_1.md`, sha256
> `2c9eec1de7ae5f98b4a2908312e19f9d42f7ef335520c1739abb6347118f5fc6`). **Firmarla es de Nicolás.**
> Lo que la regla dejó escrito y esta tarjeta no decía: (1) **toda hora candidata de (b) es posterior
> a la medianoche de Nueva York, y con el código vigente una emisión así en día sin sesión da
> `dia_sin_sesion` y no cuenta (MEDIDO con funciones puras): (b) perdería viernes y vísperas de
> feriado, 4 de cada 20 sesiones, salvo que el acta que la aplique lo resuelva; la frase de abajo
> «(b) no reinicia el contador, la definición de "cuenta" no cambia» vale sólo para una hora anterior
> a la medianoche**; (2) por eso la rama (b) lleva umbral 5 de 10 (el punto de empate) y las demás 3
> de 10, con la convención de límite inferior de Wilson fijada; (3) con la tasa del antecedente
> (3 de 11 sesiones incompletas a las 23:30 NY, [9,7 · 56,6] %) la regla indica (b) con probabilidad
> 0,11: es conservadora a propósito y lo dice; (4) K = 10 noches válidas, una sola lectura, y el
> procedimiento para mover el timer sin que dispare al activar (sección 6).
>
> **FIRMADA EN PARTE (§88.1):** «opción (a) por ahora» — el timer sigue en
> `Mon..Fri 23:30 America/New_York` y **§57 no cambia**. La elección entre **(b)** (mover el sellador
> más tarde) y **(c)** sigue **ABIERTA** y espera 5 a 10 noches de dato de la sonda.
>
> **Estado del dato al 28-sep (corrida 14, bloque 1.6, DESCRIPTIVO):** **4 noches** con sesión
> (sesiones NY 21, 22, 23 y 24-sep). Las cuatro coinciden **ticker por ticker** con lo que el meta
> del sello vio a las 23:30 NY, por dos vías independientes: 21 y 24-sep completas (36/36, todos a
> las 23:35 y 21:35 respectivamente), 23-sep con **TOELY** faltando y 22-sep con **34 de 36
> faltando a las 23:35 NY**, que es la hora más tardía que la sonda mira hoy. La noche del 22 es
> justamente la que ninguna decisión sobre (b) o (c) puede usar: **no se sabe a qué hora
> aparecieron, sólo que fue después de la última observación disponible.** Por eso la corrida 14
> propone la franja de madrugada (`Tue..Sat 00..03:05,35 America/New_York`, plantilla en
> `GEMELO/propuestas/systemd/`, **no instalada**); instalarla es acto de Nicolás, y agrega el doble
> de tráfico a yfinance en la máquina de la que depende la cadena de sellos.
>
> **Cómo leer el artefacto `sonda_cierre_resumen.md` antes de decidir:** su filtro descarta
> **observaciones** hechas antes del cierre de su sesión, **no noches**. Que el 2026-09-28 no aparezca en
> la tabla «Por noche» es porque su única observación al generarlo era la de las 13:42; las ocho sondas
> post-cierre de esa noche sí entrarían. **Excluir el 28 del conteo de noches es un juicio declarado, no
> una consecuencia del código** — y su razón no es la higiene sino que para esa fecha **no va a existir
> la segunda vía** (el sellador de las 00:30 entra por divergencia y no persiste ningún meta nuevo, así
> que el único `disponibilidad.por_ticker` en disco es el intradía). Costo de declinarla: **un día**, no
> una semana.
>
> **Dato nuevo de la noche del 28, de la primera sonda con el código corregido (21:05 Chile = 20:05 NY):
> 1 de 36 tickers tenía el cierre del 28-sep, cuatro horas DESPUÉS del cierre.** Es peor, a esa hora, que la
> noche del 22-sep. DESCRIPTIVO, n = 1 noche, y **no mueve la regla**: siguen siendo 4 noches completas. Pero
> apunta en la misma dirección que el 22-sep: **la hora que hoy tiene el sellador puede estar sistemáticamente
> antes de que la fuente publique**, y eso es lo que (b) y (c) existen para decidir.
>
> **Con 4 noches no se escribió ninguna recomendación.** Y queda declarada la tentación que se
> declinó: con las sondas de esta noche el 28-sep sería la quinta noche, pero el 28 es la noche
> contaminada (sonda de las 13:42 con el mercado abierto) y la que el sellador marcó
> `no_verificable_timing`. Cruzar el umbral con la peor noche del registro sería usar el dato para
> pasar la vara. **No se cuenta.** Texto original conservado:

**El dato, leído de la máquina el 19-sep (MEDIDO).** Nueve sesiones selladas por el timer sin intervención
humana (la del 9-sep, con el timer todavía en 21:00 Santiago); contador 7 de 40 (E0 sella el sorteo
**sin información**: prueba de maquinaria, no track record — §86.2). Dos no contaron por
`insumo_incompleto`: el 9-sep (timer a las 21:00 Chile, 34 de las 36 columnas de la extensión vacías —
la extensión trae 36 tickers, el universo operable sellado son 33—; los únicos con dato eran **SHECY y
TOELY, los dos ADR de mostrador**) y el 18-sep (timer a las 23:30 de Nueva York, **una sola columna vacía: TOELY**, Tokyo
Electron, ADR OTC; su último cierre en la extensión era el 17-sep). Y algo más que la hora: en la
extensión descargada el 17-sep 03:30 UTC, TOELY tenía cierre en TODAS las sesiones del 08 al 16 de
septiembre; en la descargada 24 h después, esas mismas fechas siguen en el índice pero con el cierre
VACÍO, y sólo 16 y 17 traen dato (idéntico los dos días: `164.55…`, candidato a cotización rezagada,
presencia no es frescura). **MEDIDO:** en dos descargas por la misma ruta separadas 24 h, los cierres de
TOELY del 08 al 15 pasaron de estar a estar vacíos (n = 1 par de descargas, 1 ticker); las filas
selladas del 10, 11, 14 y 15 con `cuenta_para_N = 1` son la evidencia independiente, desde la base, de que
esos cierres existían al sellar. **PROPUESTA:** que el borrado ocurra en Yahoo y no en la ruta de descarga
(yfinance/caché) no se probó con una segunda vía. Con la definición firmada en §57 (33 de 33 con cierre),
una columna alcanza para perder la sesión, y ese ticker ya la perdió una vez en nueve noches.

**Qué existe para decidir con dato y no con otro argumento.** La sonda `GEMELO/sonda_cierre.py`
(sin red en sus tests; no sella, no toca `dinero/`, no abre ninguna base) pregunta a yfinance qué
tickers ya tienen el cierre de hoy y lo anota en `data/sonda_cierre.csv`; el resumen
`GEMELO/sonda_cierre_resumen.py` da por ticker la hora mediana y máxima a la que apareció el cierre
y por noche la hora en que estuvieron los 36. La unidad propuesta
`GEMELO/propuestas/systemd/mki-sonda-cierre.{service,timer}` dispara `Mon..Fri 17..23:05,35
America/New_York` (cada media hora desde las 17:05 hasta las 23:35 NY, **desplazada cinco minutos
para no coincidir nunca con el sellador de las 23:30**; `Persistent=false`, una sonda atrasada no
sirve). Validada con `systemd-analyze calendar`. **Instalarla es acto tuyo**; su primera corrida
real también. Hasta que corra unas noches no hay dato; con 5–10 noches ya hay una mediana y un
máximo por ticker.

**Las tres opciones, con sus consecuencias:**

- **(a) Mantener 23:30 NY y §57 tal cual.** Nada cambia; el contador sigue. Consecuencia: cada
  noche en que un ADR OTC publique tarde (o Yahoo retire una sesión) se pierde, y la sonda medirá
  cuántas son. Con 1 pérdida en 9 noches (MEDIDO; Wilson 95 % [0,02, 0,44]), N = 40 tardaría entre
  ~41 y ~71 noches hábiles en vez de 40 (PROPUESTA: ~45 es el punto, no una predicción); si los cierres
  siguen vaciándose, puede ser peor. No reinicia nada. N = 40 compra maquinaria probada, no habilidad.
- **(b) Mover el timer a una hora más tarde que la sonda justifique.** Consecuencia: acta nueva con
  la hora y el dato de la sonda que la sostiene; la regla maestra sigue holgada (la apertura
  objetivo es 09:30 NY del día siguiente, así que incluso 02:00 NY deja 7,5 h). No reinicia el
  contador (la definición de «cuenta» no cambia). Límite: si el cierre de un ADR OTC no existe en
  yfinance a NINGUNA hora de la noche (lo que el 17→18-sep sugiere para TOELY), mover la hora no
  lo arregla.
- **(c) Redefinir «completo» por ticker:** la sesión cuenta si el insumo está fresco y completo para
  los operables con dato, y el ticker rezagado queda `sin_dato` en su fila (como hoy, pero sin
  arrastrar la sesión). Consecuencia: cambia una regla firmada el 9-sep (§57 / §86.1); hay que
  decidir si reinicia el contador (las 7 sesiones que cuentan hoy también contarían bajo (c), y
  las 2 perdidas NO se recuperan: la regla de §86.1 «sesiones perdidas no se recuperan» se
  mantiene aunque cambie la definición hacia adelante) y desde qué fecha rige. Riesgo: un
  ticker que se atrase siempre deja de estar en el experimento sin que nadie lo decida.

**Recomendación del agente, etiquetada como tal:** correr la sonda 5–10 noches ANTES de elegir
entre (b) y (c); mientras tanto (a). Si la sonda muestra que TOELY/SHECY aparecen a una hora
estable, (b); si muestra que no aparecen o que Yahoo los reescribe, (c) con la fecha de vigencia
escrita. **Cuánto cuesta decidirlo:** instalar la sonda, 5 minutos; leer el resumen, 10 minutos.
**No se eligió nada en esta corrida.**

## 59. `visible_en` en el sellador de dinero: la zona ciega Z1 del dictamen 12 no la define (corrida 13) — **CERRADA POR REMISIÓN al §23, el 19-sep-2026 (acta §88.2)**

> **CERRADA POR REMISIÓN (§88.2):** «candidato (3)» — Z1 **no es un campo del sellador**, es la
> pregunta del §23 / H1. **No se agrega ningún campo.** Z1 queda abierta hasta que se decida H1, y
> vive en el §23 de esta lista. La corrida 14 no tocó el sellador. Texto original conservado:

El `auditor-lookahead` de la corrida 12 dejó abierta la zona ciega Z1, nombrada como «sellado
(`visible_en`)» y como «`ts_emision` se estampa al entrar y no hay `visible_en`», tres veces, **sin
definir qué campo es ni cómo se calcula**. El encargo 13 (bloque 4.4) mandó agregarlo con test si
el dictamen lo definía con precisión y, si no, escribir la pregunta acá y no inventar. No lo
define. Además el pre-mortem del director marcó que dos cambios al sellador en producción la misma
noche (E4-bis y esto) son un sospechoso de más: E4-bis se aplicó; esto no se toca.

**La pregunta exacta.** ¿Qué instante quiere Z1 que se selle? Candidatos, con lo que cada uno
costaría: (1) **el instante en que la fila queda commiteada en la base** (`creado_en` ya existe:
es el reloj de pared al armar la fila, ~150 ms después de `timestamp_utc`; se podría estampar
DESPUÉS del `commit` con una segunda columna, pero una fila inmutable no admite un UPDATE, así que
sería una tabla aparte o un campo que se calcula antes del commit y por tanto no lo prueba);
(2) **el instante en que el CSV exportado quedó commiteado en git** (`commiteado_en`, el nombre que
`expedientes.md` §2 usa): eso lo sabe `git log` de `data/backups/sello_dinero.csv`, no la base, y
el job de backup corre a las 18:40 Chile del día siguiente, ~18 h después de la emisión: sería un
campo derivado en el export, no en la fila; (3) **un tercero que reciba el sha de la fila antes de
la apertura** (`H1_sello_verificable.md`, §23 de esta lista): es el único que hace la marca
verificable desde afuera, y es una decisión de diseño que ya espera firma. Si Z1 es (3), no es un
campo del sellador: es el §23. Si es (1) o (2), decí cuál y se implementa con test en worktree;
ninguno de los tres prueba nada que `timestamp_utc < apertura_objetivo` + el commit diario de
`data/backups/` no prueben ya, y eso también hay que decirlo.

## 60. Confirmar la opción (a) del hallazgo 2 de la revisión del 9-sep: `.gitignore` para `dinero/datos/sello/` (corrida 13) — **FIRMADA el 19-sep-2026 (acta §88.3)**

> **FIRMADA (§88.3):** opción (a), confirmada por escrito («para efectos de legibilidad»), y
> **ejecutada por Nicolás** en el commit de firmas. Verificado por la corrida 14:
> `git check-ignore -v dinero/datos/sello/…` responde `.gitignore:45:dinero/datos/sello/`, y
> `git ls-files dinero/datos` sólo lista los cuatro archivos del congelado grande. Texto original
> conservado:

El encargo 13 (§2, tabla) dice que la opción (a) —una línea en `.gitignore` para
`dinero/datos/sello/`, con `data/backups/sello_dinero_ext/` como única copia versionada— quedó
«pendiente de confirmación explícita en el chat». El `orientador` no encontró esa confirmación en
ningún documento (§86, esta lista, `cola_decisiones.md`, `bitacora_12.md`, `dictamen_12/`), así que el
punto 4.3 **NO se ejecutó** (pre-mortem del director, ítem 6). Dos cosas que pesan antes de firmar:
(i) `git rm --cached` de `ext_2026-09-08.*` y `ext_2026-09-09.*` retira de git la copia que salvó al
09-sep de la fuga E4 (la restauración del 19-sep fue un `git checkout` de ESA ruta); con (a), la
única red pasa a ser `data/backups/sello_dinero_ext/`, que el job de backup commitea al día
siguiente, y hoy `ext_2026-09-18.*` todavía no está commiteado ahí. (ii) Desde la corrida 13 el
test permanente `test_integridad_*` verifica las dos carpetas contra la base en cada suite, así que
la inconsistencia se ve al día siguiente aunque git no la guarde. **Opciones:** (a) tal como estaba
(una línea de `.gitignore` + `git rm --cached` de los cuatro archivos), con la condición de que cada
`fecha_insumo` sellada tenga su par commiteado en backups antes; (b) dejar `dinero/datos/sello/`
sin versionar pero sin `git rm --cached` de lo ya rastreado (las dos primeras fechas quedan en
git como están, las siguientes no); (c) versionar TODO `dinero/datos/sello/` (unos 13 KB por
noche) y aceptar dos copias. Sin firma escrita acá o en acta, no se ejecuta ninguna.

---

## 61. El riel de medición sella sin el término de conocibilidad, y el 28-sep-2026 lo demostró (corrida 14) — **FIRMADA el 29-sep-2026 (acta §90.1): opciones (a), (b) y (d), sin efecto retroactivo**

> **FIRMADA (§90.1) y APLICADA por la corrida 15** (bitácora 15, sección 2): (a) la guarda
> `available_at <= timestamp_utc` en `senales.py::verificar_apertura_pendientes()`, (b) `snapshot.py`
> se niega a sellar si `available_at > emisión` (margen cero, por dictamen del director: el margen de
> 2 h de `sesion_ya_cerro` es de verificación y apagaría el sello diario), (d) la exclusión por regla
> en `backtest/linea_base.py::cargar()`. Las 24 filas del 28-sep conservan su estado; ninguna cifra
> publicada cambió. El corte de método es la hora de aplicación al árbol real que declara el acta
> §92. Lo que la aplicación dejó abierto está en las tarjetas §71 (el ancla de §90.2, detenida), §72
> (la guarda es necesaria y no suficiente) y §73 (las métricas vivas que no pasan por la exclusión).

**El hecho, MEDIDO y dictaminado — con una inferencia marcada.** El 28-sep-2026 los ocho timers
dispararon juntos a las **14:42:52** (medido, journal). **Que la máquina volviera de suspensión, y a las
14:40, es INFERENCIA y no hecho registrado:** WSL2 no anota suspend/resume, lo medido es el hueco del
journal entre `2026-09-25T02:16:24` y `2026-09-28T14:42:52` más el `systemd[317]` sobreviviente más el
uptime, y **la ventana sólo se acota a [vie 02:16, vie 17:50]**; las «14:40» vienen del encargo, no de
una medición. Lo exigió el `auditor-lookahead` y lo marcó el `curador-epistemico`. `snapshot.py` selló a las **17:42:58 UTC = 13:42 de
Nueva York, con NYSE abierto**. Las 24 filas de `senales_ticker` de ese día llevan
`available_at = 2026-09-28T20:00:00+00:00` (el cierre) y `timestamp_utc = 2026-09-28T17:42:58Z`:
el sello **declara que su insumo fue conocible 2 h 17 min después de que la fila ya existía**.
`SELECT fecha, COUNT(*) FROM senales_ticker WHERE available_at > timestamp_utc GROUP BY fecha`
devuelve **una sola fecha en toda la historia sellada**: ésa, con 24 filas. Confirmado en dos
fuentes independientes (la base y el CSV versionado de HEAD, que antes del evento da 0 inversiones).

**No es look-ahead** —la fila usó MENOS información de la que declara, y `tests/test_motor.py` pasa
sus 18 casos— pero el `auditor-lookahead` dictaminó
`FILAS INVÁLIDAS ENTRARON COMO VÁLIDAS`, por tres razones medidas:

1. El sello de conocibilidad es **aritméticamente imposible**, y ese campo existe justamente para
   que un tercero verifique la conocibilidad.
2. **La predicción no es reproducible desde el registro sellado.** Las 8 predicciones del día son
   exactamente `beta × (−1,63)`, donde −1,63 es `sox_usado_pct`, una lectura intradía de las 13:42
   NY que el registro etiqueta `sox_fecha = 2026-09-28`. Quien reproduzca leerá el cierre real del
   28-sep y obtendrá otro escalar. Y como **las 8 betas son positivas**, si el retorno del cierre
   real tiene signo opuesto a −1,63, **las 8 direcciones predichas se invierten**.
3. La fila es inválida **según una regla que el proyecto ya tiene escrita y aplicada en el otro
   riel**: `dinero/sello_dinero.py` exige `available_at < timestamp_utc < apertura` y marcó sus 33
   filas del mismo evento `estado_timing='roto'`, `no_verificable_timing`, `cuenta_para_N=0`.
   `senales.py::verificar_apertura_pendientes()` tiene **una sola** guarda, `emitida >= apertura`,
   y nunca compara `available_at` contra `timestamp_utc`.

**Y hay un canal de look-ahead en el mismo camino que esta tarjeta pide firmar, que el auditor encontró,
midió NULO en efecto, y hasta ahora vivía sólo en su dictamen** (lo trajo acá el `curador-epistemico`,
porque «el §61 pide firmar una regla justo sobre ese camino»): `snapshot.py:163` elige la sesión objetivo
con `proxima_sesion_despues_de(exchange, available_at)`, o sea **ancla en un instante que el 28-sep estaba
2 h 17 min en el FUTURO de la emisión**. Medido con ancla=emisión contra ancla=`available_at`: da
`2026-09-29` bajo las dos para XKRX, XTKS, XTAI, XETR y XNYS, así que **no alteró ninguna
`sesion_objetivo` en esta fecha** — pero, con las palabras del auditor, es «coincidencia de esta fecha, no
garantía». Es código vivo, aplicado por el acta §84.1. **Quien firme una opción de esta tarjeta debería
decidir también si ese ancla se mueve a la emisión**, porque hoy la regla nueva se escribiría sobre un
camino que sigue anclando en el futuro.

**Tres guardas que existen y no lo vieron, cada una por su razón:**
- `mki_vigia.py` chequea `av is None or av == ts` — **igualdad, no orden**: una inversión la pasa
  muda. Y además esa noche corrió 5,6 s ANTES de que las filas existieran (los ocho timers en el
  mismo segundo), registrando «OK ancla temporal: sin predicciones selladas hoy que revisar».
- `tests/test_motor.py` trunca con `df[df.index.date <= fecha]`, **inclusive**: la barra parcial de
  `fecha` está en las dos ramas con el mismo valor y **se cancela**. El test es estructuralmente
  incapaz de ver una barra no liquidada EN `t`. Su verde sigue siendo válido para lo que mide.
- `descarga_ok = 28/28` sólo exige que cada ticker tenga algún dato en los últimos 7 días; nada
  dice sobre si la última barra es un cierre liquidado.

**Qué está y qué no está contaminado, con precisión.** Nada publicado: `cifras.CORTE_README` es
`2026-08-28` y `verificacion_apertura` no tiene ninguna fila del 28-sep. Lo futuro sí: las 8 filas
entran a `verificacion_apertura` cuando cierren las sesiones del 29-sep, las 24 entran a
`verificacion_puntaje` alrededor del 5-oct, y `backtest/linea_base.py::sesion_correcta` las acepta
porque el sello falso es **auto-consistente** con la `sesion_objetivo` sellada.

**Y no hay auto-corrección posible:** `senales.ya_existe_snapshot_hoy()` compara
`fecha = date.today()`, así que el disparo de las 18:15 devuelve «ya existe snapshot de hoy» y no
re-sella. **Las filas de las 13:42 NY son el registro permanente del 28-sep.**

**Opciones.** Ninguna se implementó: todas tocan el camino de sellado o las métricas.

> **Aviso del `guardian-constitucion`: dos de estas cuatro opciones tocan la Constitución, y la
> tarjeta tiene que decirlo con esas palabras.** Las opciones **(a) y (c) chocan con el punto (3) de la
> Constitución 5.0 de `CLAUDE.md`** («las filas selladas JAMÁS se reescriben — los errores históricos
> se vuelven erratas fechadas en `DECISIONES.md`»). Firmar (a) con efecto retroactivo **es enmendar la
> constitución**, no sólo cambiar código, y eso se firma como enmienda o no se firma. **(d) es la única
> que deja el camino de sellado intacto.**

- **(a) Agregar el término que falta al verificador**: una fila con `available_at > timestamp_utc`
  pasa a `no_verificable_timing`, igual que en el riel de dinero. **Agregar la guarda ENDURECE la regla
  maestra**, así que hacia adelante es admisible en especie; lo que toca la constitución es el efecto
  **retroactivo** sobre las 24 filas del 28-sep, que es cambiar el `estado` de filas ya selladas —cosa
  que el proyecto sí hace en el ciclo de vida `pendiente→verificada` pero **nunca para invalidar**.
  Coste: toca `senales.py`, que es camino de sellado, y cambia el significado de las filas futuras
  respecto de las ya selladas, lo que hay que declarar **antes** y no descubrir después.
- **(b) Guarda de ventana en el job**, antes de sellar: `snapshot.py` se niega a sellar si la sesión
  de `sox_fecha` no ha cerrado. Coste: toca `snapshot.py`; y un día en que la fuente se atrase
  dejaría de sellar en vez de sellar mal — hay que decidir si eso es mejor.
- **(c) Dejar las 24 filas como están y documentar la errata**, sin tocar código, aceptando que 8
  predicciones no reproducibles entren a las métricas del modelo 4.6.0. Es la forma que el punto (3) de
  la Constitución prescribe para un error histórico (errata fechada, la fila no se toca). Coste: es
  exactamente lo que el otro riel decidió NO hacer con las suyas del mismo evento.
- **(d) Excluir sólo esas 24 filas por fecha en la capa de medición** (como `excluir_cero` de la
  §2.8 del GEMELO, que vive en la medición y no en `senales.py`), dejando el camino de sellado
  intacto. Coste: la exclusión es una decisión por fecha y hay que escribir su criterio ANTES, o es
  elegir qué filas cuentan después de verlas.

**EL ORDEN IMPORTA, y es lo primero que hay que leer de esta tarjeta: la magnitud NO decide la
regla.** Lo marcó el `director-programa` al revisar el cierre. Si las filas se retiran sólo cuando el
signo salió mal, eso es **elegir qué filas cuentan después de verlas** — la fuga de selección que el
auditor advirtió que esta auditoría podía crear, entrando por la puerta que una tarjeta mal ordenada
deja abierta. **La regla se firma por su mérito** —es la que el otro riel ya aplica, y agregarla
ENDURECE la regla maestra, nunca la ablanda— **y después se lee el daño.** Lo que sigue es el daño.

**El daño, MEDIDO a las 17:31 del 28-sep (sección 9 de `bitacora_14.md`).** Se pudo medir porque el
cierre de NYSE es a las 17:00 de Chile y la ventana prohibida empieza a las 17:50; y no había riesgo,
porque el sello del 28 ya existía y `ya_existe_snapshot_hoy()` garantiza que las 18:15 no lo rehacen.
Recomputado con funciones puras, sin escribir ninguna base:

> **PROVISIONAL, y hay que leerlo antes de la tabla.** El job de las 18:15 marcó
> `8035.T` con un salto de **−80 %** el 28-sep (`data/snapshot.log:147`: «revisar split/dato corrupto»;
> `salud_datos_al` con umbral 0,40). 8035.T cotiza cerca de **55.000 yenes** y −80 % es exactamente un
> **split 5:1** — INFERIDO, con evidencia fuerte y sin el cierre a la vista, porque medirlo exigía bajar
> datos dentro de la ventana prohibida. Como 8035.T es eslabón de un nivel de tres sobre cinco niveles de
> peso igual, un desplazamiento de −80 pp en su `mom20` mueve el crudo de la cadena **(80/3)/5 = 5,33 pp**,
> y el salto observado del crudo es 6,44 pp: **ese solo ticker explica ~83 %**. Por eso **el 17, los 27
> puntos y la lectura «chica en el canal lineal, grande en el agregado» quedan PROVISIONALES** hasta
> contrastar 8035.T (después de las 20:30: mirar su `Close` del 25 y del 28 y recién entonces releer
> `roca_chip_al`). Lo levantó el `curador-epistemico`. **Nada de esto mejora la fila:** un insumo corrupto
> *además* de intradía no la arregla, y el veredicto no se apoya en la magnitud.
>
> Y **el 0,11 pp de la fila «peor predicción» no mide el efecto de la barra parcial**: con 0,02 pp de
> desvío en el escalar, el máximo propagable es 0,81 × 0,02 = **0,016 pp**. El 0,11 existe porque **la
> beta de 8035.T se reestimó** (0,56 → ≈0,497) — el mismo ticker marcado. **Entre los siete tickers sin
> dato marcado la peor diferencia es 0,03 pp**, y ése es el número que mide la barra parcial.

| cifra | sellado 13:42 NY | recomputado post cierre | dif. |
|---|---|---|---|
| `sox_usado_pct` | −1,63 | **−1,61** | 0,02 pp, **mismo signo** |
| direcciones de las 8 predicciones | — | — | **0 invertidas de 8** |
| peor predicción (8035.T) | −0,91 | −0,80 | **0,11 pp** |
| `regimen` | `Alcista · vol baja` | `Alcista · vol baja` | **idéntico** |
| **`roca_chip`** (percentil del año) | **44** | **17** *(PROVISIONAL)* | **27 puntos** *(PROVISIONAL)* |

**Dos sospechas del auditor no se materializaron en esta fecha** (no se invirtió ninguna dirección, y el
cambio de etiqueta de volatilidad respecto del 24-sep es real y no un artefacto — aunque la coincidencia
de una etiqueta binaria es evidencia débil por construcción, con un margen de 1,3: vol 37,5 contra mediana
38,8). **No «quedan refutadas»:** el mecanismo sigue ahí, porque con las 8 betas positivas un día en que la
barra intradía y el cierre caigan a distinto lado del cero invierte las ocho direcciones a la vez. Y las
dos estaban en su dictamen bajo «SOSPECHAS SIN DEMOSTRAR», **fuera** de los cuatro fundamentos del
veredicto.

**Lo que esta medición APORTA en contra de las filas, y es lo que más pesa: CONFIRMA la
no-reproducibilidad.** El dictamen la deducía; un tercero reprodujo y obtuvo −1,61 y 17. En su dictamen
complementario el auditor **ratificó el veredicto sin cambio de forma y con fuerza neta MAYOR**. Su
argumento, que es más fuerte que «el daño fue chico» y hay que firmarlo con él a la vista: **el argumento
a favor de esta regla no puede ser la magnitud**, porque el canal donde el daño resultó grande
(`roca_chip`) es justamente el que nadie puso primero. «Una regla que dependa de que alguien jerarquice
bien los canales ex ante falla la primera vez que alguien jerarquiza mal, y esta corrida es esa primera
vez.» **La regla se sostiene en la violación de orden, ex ante, sin consultar el daño.**

**Y sigue SIN MEDIR lo que más filas tiene en juego:** `puntaje_v0`, `puntaje_ia` y `divergencias` del
28-sep. `puntaje_ia` es el campo de las **24** filas —no de las 8— que entran a `verificacion_puntaje`
alrededor del **5-oct**. Esa diferencia **ya no se puede medir**: la barra parcial de las 13:42 no existe
más, así que sólo se puede medir el valor correcto de hoy, nunca el desvío.
**Y aparece la que nadie había buscado:** `roca_chip` se movió 27 puntos — **PROVISIONAL**, ver el aviso
de arriba: el 28 hubo una caída brusca del ratio roca→chip (crudo −2,8 % contra +2,6 a +3,6 los cuatro días
anteriores), y **~83 % de ese movimiento lo explica el `8035.T` que el propio sistema marcó**. Es una cifra
que la pantalla muestra y que el reporte de Telegram ya publicó como 44.

**Y la no-reproducibilidad es IRREVERSIBLE, medido la misma noche.** La sonda de las 20:05 NY mostró que
**35 de 36 tickers ya no tenían la barra del 28-sep** que sí estaba a las 13:42: yfinance retiró la barra
intradía provisional al cerrar la sesión. O sea que **el insumo que las 24 filas citan ya no lo sirve la
fuente**. La zona ciega #10 del auditor —«esta comparación no se puede repetir nunca»— pasó de declarada a
medida (`bitacora_14.md` sección 11).

Salvedades que van pegadas al número: **la columna «recomputado» no es reproducible por nadie** —se corrió
sin dejar script ni log, y el auditor verificó su coherencia interna y la aceptó «por la palabra de la
bitácora»—; **−1,61 tampoco es necesariamente el cierre liquidado** (se leyó
31 min después de la campana, y esta misma corrida midió que en 2 de 4 noches no todos los tickers
tienen su cierre en yfinance ni a las 23:35 NY); y es **una** fecha, en un día que cayó fuerte al
final, así que no dice cuánto se desvía una barra parcial en general.

---

## 62. Qué debe hacer el sellador de dinero con un disparo fuera de hora que deja una fecha «sellada» en estado no verificable (corrida 14) — **FIRMADA EN PARTE el 29-sep-2026 (acta §90.6): (a) y (d), con la política de retención escrita antes; aplicación pendiente de acta posterior**

> **FIRMADA EN PARTE (§90.6).** La corrida 15 escribió la política de retención
> (`GEMELO/propuestas/parches/politica_evidencia_no_verificable.md`) y el parche NO APLICADO
> (`sello_no_verificable.diff` con sus tests y su `.md`). **Hallazgo de la política, leído del
> código: la opción (a) tal como está firmada no se puede implementar**, porque `sellos_dinero` tiene
> `UNIQUE (fecha_insumo, ticker, juego)` y las filas no verificables y las buenas de una fecha no
> pueden convivir; el parche toma el camino T (tabla aparte `intentos_no_verificables`, aditiva) y
> deja el camino M (migrar el esquema, que reescribe la tabla) sin implementar. Ver la tarjeta §75.
> `dinero/sello_dinero.py` del árbol real no cambió.

**El hecho.** El 28-sep a las 14:42:52 el sellador disparó con la bolsa abierta y escribió 33 filas
con `fecha_insumo` 2026-09-28, `estado='no_verificable_timing'`, `estado_timing='roto'`,
`cuenta_para_N=0`, más `ext_2026-09-28.{csv,meta.json}`. El guardia E4 hizo su trabajo. Pero
`sello_previo()` **no distingue `pendiente` de `no_verificable_timing`**: sólo pregunta si la fecha
tiene filas. Leído el código, a las 23:30 NY del 28 el sellador bajará el cierre final, el sha
diferirá del intradía, entrará por la rama de divergencia y escribirá **cero filas**. La sesión del
lunes 28 se pierde, igual que la del viernes 25 (que se perdió por el apagón, en los tres rieles).

**La consecuencia que agrava el caso:** `ext_2026-09-28.csv` es la evidencia que 33 filas citan por
sha256, y **es una matriz de precios de media sesión**. Por diseño de E4-bis (opción A del auditor,
corrida 13) el archivo de una fecha ya sellada no se reescribe nunca. Así que el cupo de evidencia
de esa fecha queda ocupado permanentemente por un insumo que E4 ya rechazó, y `mki-backup` lo
commitea.

**Opciones.**
- **(a) Que `sello_previo()` distinga estados:** una fecha cuyas únicas filas son
  `no_verificable_timing` cuenta como no sellada, y el sellador de las 23:30 puede sellarla bien.
  Coste: hay que definir qué pasa con las 33 filas viejas (¿conviven dos sellos de la misma fecha
  con estados distintos?) y toca `dinero/sello_dinero.py`.
- **(b) `Persistent=false` en `mki-sello-dinero.timer`.** Coste: **no sirve para este caso** y hay
  que decirlo — ver §63: un disparo atrasado por suspensión ocurre igual. Sí evitaría el caso
  distinto de que el manager se reinicie.
- **(c) Dejarlo como está y aceptar la pérdida.** Coste: cada despertar fuera de hora quema una
  sesión de N, y además quema el archivo de evidencia de esa fecha.
- **(d) (agregada por el pre-mortem) Que un sello no verificable no reclame el cupo de evidencia:**
  escribir `ext_<fecha>.no_verificable.csv`, o no escribir `ext_` cuando `timing_ok` es falso. Coste:
  es una ruta de escritura nueva sobre la carpeta de la evidencia, que es lo que E4-bis cerró a
  propósito; habría que escribir su política de retención.

Sin (d) la tarjeta se firma resolviendo el problema chico y deja el grande.

---

## 63. La supresión de un disparo atrasado no es configurable en systemd: la guarda va en el job (corrida 14) — **FUNDIDA en la tarjeta 66 por el acta §91.5 (29-sep-2026)**

> **FUNDIDA (§91.5):** su premisa, sus tres opciones para la sonda y su errata de `Description=`
> viven ahora en la tarjeta §66 (inventario de los ocho jobs), sección F. El texto de abajo se
> conserva tal cual.
>
> **Nota del `director-programa` al cierre de la corrida 14: esto es más una PREMISA que una tarjeta.**
> Su contenido —no hay knob de systemd, la guarda va en el job— es lo que sostiene la opción (b) de §61
> y la (a) de §62, y su única decisión propia (si el job de la sonda debe marcar la fila al escribir) es
> menor, porque el lado lector **ya está aplicado**. Recomienda **fundir esa decisión en §61 y §62** y
> dejar este ítem como hallazgo medido del acta §89.5, para no diluir con cinco tarjetas una cola que se
> ordena por costo y tiene tres decisiones. **Fundirla o no es de Nicolás**; hasta entonces queda acá,
> con la recomendación a la vista.

**Medido.** `~/.config/systemd/user/mki-sonda-cierre.timer` lleva `Persistent=false` y **disparó
igual** a las 14:42:52 del 28-sep, 36 filas a las 13:42 NY con el mercado abierto. `Persistent=`
gobierna una sola cosa: recuperar disparos perdidos **mientras el manager no estaba corriendo**. El
manager nunca se cayó (`systemd[317]` a los dos lados del fin de semana; `uptime` «up 5 days»). Lo
que pasó es que la máquina estuvo suspendida, el reloj de pared siguió, la hora venció y el timer
corrió al reanudar. **Ninguna directiva de `[Timer]` desactiva eso.** El journal de WSL2 no registra
suspend/resume: el evento se reconstruye del hueco más el PID sobreviviente.

Por lo tanto la pregunta «qué timers deberían llevar `Persistent=false`» no tiene la respuesta que
busca, y la defensa tiene que ser **una guarda de ventana en el job**. El riel de dinero ya la tiene
(E4); el riel de medición no (§61); la sonda tampoco.

**Opciones para la sonda** (el sellador va por §62 y el riel de medición por §61):
- **(a) Guarda en el script:** `sonda_cierre.main()` se niega a escribir si la hora NY no cae en la
  grilla. Barato; se pierde la fila y con ella la evidencia de que hubo un despertar.
- **(b) Guarda en el lector:** la fila se escribe y el resumen la rotula fuera de grilla. No pierde
  evidencia, y **es la única que arregla el dato que ya está en disco**. *Aplicada en parte por la
  corrida 14*: `sonda_cierre_resumen` ya descarta y DECLARA las observaciones anteriores al cierre
  de su sesión (las 36 del 28-sep). Falta decidir si además el job debe marcarlas al escribir.
- **(c) Nada, y aceptar una fila fuera de grilla por despertar.**

**Errata que sale de la misma lectura, no corregible por un agente:** las dos unidades instaladas
(`mki-sonda-cierre.timer` y `mki-sello-dinero.timer`) siguen diciendo **«PROPUESTA no instalada»**
en su `Description=`, visible en `systemctl status`. Están instaladas y corriendo. La plantilla del
repo se corrigió en la corrida 14; la unidad instalada la edita Nicolás.

---

## 64. Entre los ocho jobs no hay ninguna dependencia: el orden lo da sólo el reloj (corrida 14) — **FIRMADA el 29-sep-2026 (acta §90.8): opción (c)**

> **FIRMADA (§90.8) y APLICADA por la corrida 15:** `mki_backup.py` se niega a commitear si el
> snapshot del día no está sellado o si `snapshot.py` está vivo, y lo registra en su log (bitácora 15,
> sección 4; `tests/test_backup_orden.py`). Lo que el acta no definía (día de semana sin sello que ya
> no puede llegar; fin de semana) quedó como elección de agente en la tarjeta §70.

**Medido**, del journal del 28-sep:

```
14:42:52  Starting   los ocho mki-*
14:42:53  Finished   mki-backup          ← un segundo después de arrancar
14:43:01  Finished   mki-sello-dinero
14:43:30  Finished   mki-snapshot
```

`mki-backup.timer` no declara `After=` ni `Requires=`. Con todos disparando en el mismo segundo,
backup ganó. Resultado: el commit `5321f6b`, llamado **«Backup diario 2026-09-28»**, **no contiene
el sello de ese día**, y los seis CSV que snapshot y el sellador escribieron después quedaron sin
commitear. Es un artefacto publicado cuyo nombre no describe su contenido. En operación normal el
orden se cumple sólo porque 18:40 > 18:15.

Medido y tranquilizador: `mki_backup.py` commitea con pathspec (`commit -m … -- data/backups`), así
que nada fuera de `data/backups/` se cuela.

**Opciones:** (a) `After=mki-snapshot.service mki-sello-dinero.service` en `mki-backup.service`
—no basta `After=` si no hay `Requires=`, hay que escribir la semántica exacta—; (b) mover backup
más tarde, que no resuelve el caso del despertar simultáneo; (c) que `mki_backup.py` se niegue a
commitear si el snapshot del día no está sellado; (d) nada, y aceptar que un despertar produce un
commit mal nombrado. Toca unidades instaladas: no se aplicó nada.

---

## 65. El README lleva un contador vivo que nada regenera (corrida 14) — **FIRMADA el 29-sep-2026 (acta §90.3 opción b, §90.4 opción b)**

> **FIRMADA (§90.3, §90.4) y APLICADA por la corrida 15** (bitácora 15, sección 3): el README no
> lleva contador; la viñeta de E0 remite al CSV versionado; los badges `tests` y `plataforma` son
> valores congelados con la fecha de lectura dentro del badge (`docs/readme/badges_congelados.json`);
> los dos rojos de `tests/test_readme.py` desaparecen. **Errata del acta §90.3:** pide remitir a
> `/salud`, y `/salud` no muestra el riel de dinero; lo muestra `/sellos`. La mención se quitó;
> apuntar a `/sellos` es decisión de Nicolás (tarjeta §76).

**Medido.** La suite abrió y cerró la corrida 14 con **dos rojos**:
`tests/test_readme.py::test_los_dos_readme_son_lo_que_el_generador_produce` y
`::test_el_contador_de_e0_del_readme_es_el_de_la_copia_versionada`. La causa no es una regresión:
`README.md` publica **cuatro** valores del 19-sep a la vez —«9 sesiones selladas, de las cuales 7
cuentan para N = 40; las que no (2026-09-09, 2026-09-18) … última sesión de insumo sellada:
2026-09-18»— y `contador_e0()` hoy da `sesiones_selladas 14`, `cuentan_para_N 9`, **cinco** fechas
que no cuentan y `ultima_fecha_insumo 2026-09-28`. El timer mueve ese contador cada noche y **nada
regenera el README**, así que la página se vence sola y la suite se pone roja sola.

`README.es.md` pasa el test del generador por una razón que también es hallazgo: **la sección de E0
no existe en español.** `README.md` tiene `## Execution rail (paper only)` entre «The laboratory» y
«Audit every figure»; `README.es.md` va de «El laboratorio» directo a «Auditar cada cifra». Eso es
lo que hace que el test de paridad numérica entre idiomas la excluya (la deuda que el director de la
corrida 13 anotó): **no es un hueco del test, es que no hay nada en español con que comparar.**
Extender el test exige primero escribir la sección en español, que es contenido nuevo en una página
publicada y no lo firmó ninguna acta.

**Opciones para el contador:** (a) que el job de backup diario regenere los README después de
commitear (los pone en el árbol todos los días, y habría que decidir si commitea el README también);
(b) que el README **no** lleve el contador vivo y remita a `/salud` o al CSV versionado; (c) que el
contador quede congelado con su fecha a la vista («al 19-sep-2026: 9 de las cuales 7…»); (d) nada, y
aceptar dos rojos permanentes en la suite, que es lo peor porque vuelve el rojo invisible.

**Opciones para los badges `tests-650` y `plataforma-5.0.3`** (§88.5 firmó reemplazarlos por valores
leídos de la máquina, «de preferencia generados»; reales hoy: la suite recolecta **904** tests bajo `tests/` (leído de `pytest tests/ --collect-only -q`;
`pytest --collect-only -q` sin alcance da **907**, porque suma tres casos parametrizados de
`GEMELO/propuestas/`) y
`PLATAFORMA_VERSION` es **5.1.0**): (a) generados desde un artefacto declarado, lo que obliga a
decidir quién produce ese artefacto y cuándo —la única fuente del número de tests es correr la
suite—; (b) congelados con su fecha a la vista; (c) retirados. El acta firmó reemplazarlos, **no**
quitarlos, así que (c) necesita firma nueva. La corrida 14 no escribió código de badges a propósito
(el director lo marcó como rama lateral: máquina nueva para un badge).

---

## 66. Inventario de los ocho jobs ante un disparo fuera de hora, con una novena fila para el cambio de calendario de un timer (corrida 15) — funde §63

> Bloque 5 de la corrida 15, redactado por un agente de sólo lectura e integrado por el orquestador con las
> correcciones que siguen entre corchetes; §63 queda marcada «FUNDIDA en la tarjeta 66 por el acta §91.5» sin
> borrar su texto.
>
> **Recomendación del `director-programa` al cierre (`dictamen_15/director_cierre.md`), para la firma:** de las
> once tarjetas de la corrida 15, fundir **§72** en la fila 2 de esta tabla y **§70** en la fila 4 (son la
> misma decisión, qué hace cada job fuera de hora, partida en tres documentos); sacar **§74** de la cola de
> firmas porque es un acto de cinco minutos y no una decisión (queda en el «Primero» de `ESTADO.md`); y no dar
> tarjeta propia a **§69**. Quedarían siete: §66 (con §70 y §72 adentro), §71, §73, §75, §76, §67, §68. El
> orquestador no las fundió al cierre porque el acta §92, la bitácora y `ESTADO.md` ya las citan por número. Sólo lectura: ningún archivo del repo se tocó, ninguna
> unidad de systemd se operó, ningún job ni test se corrió. Lecturas hechas el **29-sep-2026 entre las 22:11 y
> las 22:43 de Chile** (hora leída de `date` antes de cada consulta; la ejecución se cortó ~22:40 por cuota de
> la API y se retomó a las 23:01), sobre el árbol real en `HEAD = 2f73eb2` (`main`): **las guardas que la
> corrida 15 planifica NO estaban en ese árbol al leer**; donde se dice qué hará un job con ellas va marcado
> **PLANIFICADO en la corrida 15** y es deducción, no observación. Bases abiertas sólo con
> `sqlite3.connect('file:...?mode=ro', uri=True)`, fuera del tramo 00:15–00:50. `data/sonda_cierre.csv` y
> `data/sonda_cierre.log` se leyeron filtrados por `timestamp_utc < 2026-09-30T04:00:00Z` (acta §91.3):
> ninguna fila de madrugada existía ni se leyó (última lectura 22:27). Cada cifra lleva su fuente.

**Qué hay que decidir, en una frase.** Para cada uno de los ocho jobs, si ante un disparo fuera de su hora
**se niega**, **marca** o **sigue igual**; y qué procedimiento rige un **cambio de calendario** de un timer
instalado, que el 29-sep disparó la sonda a las 18:38:57 sin que nadie lo pidiera.

**Qué desbloquea.** Cierra §63 (fundida acá). Pone en contexto las tres guardas que la corrida 15 planifica
(§90.1 b, §90.8, y la (a) del verificador) y las dos que no toca (vigía, sonda). Da el procedimiento sin el
cual mover la hora del sellador (§58 b/c) puede quemar una sesión de N en el acto (§91.7, tercer punto).

**Cuánto cuesta decidirlo.** ~25 minutos de lectura. Nueve decisiones chicas; tres ya están firmadas
(§90.1 b, §90.6, §90.8) y acá sólo se las sitúa. **Las dos filas con más en juego son la 2 (snapshot) y la 9.**

---

### A. Los dos eventos, MEDIDOS

**A.1 El 28-sep-2026, 14:42:52 Chile (13:42 de Nueva York, NYSE abierta).** `journalctl --user`, `-o short-precise`,
las ocho unidades. Arrancaron en 59 ms, **en el orden alfabético de sus nombres de unidad** (n = 1; no se verificó
que sea regla): backup .702, noticias .704, reporte .706, sello-dinero .708, snapshot .709, sonda .710,
vigia-rechequeo .734, vigia .761.

| job | arranque → fin (journal) | qué hizo, con su fuente |
|---|---|---|
| `mki-vigia-rechequeo` | 14:42:52.734 → 14:42:53.303 | «sin alerta pendiente de hoy — nada que re-chequear» (`data/vigia.log:216-217`). Corrió **antes** de que el vigía escribiera el marcador (17:42:55.339Z). |
| `mki-backup` | 14:42:52.702 → 14:42:53.790 | commit `5321f6b` «Backup diario 2026-09-28», AuthorDate `2026-09-28T14:42:53-03:00`: **3 archivos, +340** — `sello_dinero.csv` (+33 filas del insumo 2026-09-24, timestamp 2026-09-25T03:30:04Z) y `ext_2026-09-24.{csv,meta.json}`; **ningún** `senales_*` (`git show --stat`). Es el material que el backup del viernes 25, que nunca corrió, habría commiteado. `data/backup.log:67-69`. |
| `mki-vigia` | 14:42:52.761 → 14:42:56.648 | `data/vigia.log:218-226`: **4 FALLA** (snapshot NO se selló; descarga sin snapshot; noticias NO corrió — «proceso 39845 vivo desde Mon Sep 28 14:42:51»; reporte NO hay envío) y **2 OK** («backup: commit de hoy presente» — sostenido por `5321f6b`, de 2 s antes —; «ancla temporal: sin predicciones selladas hoy que revisar»); marcador escrito; **alerta Telegram enviada 17:42:56.18Z**. |
| `mki-reporte` | 14:42:52.706 → 14:42:56.985 | `data/reporte.log:45-46`: compuesto 17:42:55.500Z, **400 caracteres**, «Reporte enviado 14:42» (17:42:56.46Z): **3,4 s antes de que el sello existiera**. |
| `mki-sonda-cierre` | 14:42:52.710 → 14:42:58.587 | **36 filas**, `timestamp_utc 2026-09-28T17:42:55.212430Z`, `hora_ny 13:42`, `sesion_ny 2026-09-28`, 35 con `es_sesion_de_hoy = 1` (CSV filtrado); `data/sonda_cierre.log:33` «13:42 NY · sesión 2026-09-28 · 35/36 · faltan: ['TOELY']». |
| `mki-sello-dinero` | 14:42:52.708 → 14:43:01.401 | `data/sello_dinero.log:441-469`: `sellada`, `fecha_insumo 2026-09-28`, `timestamp_utc 17:43:01.001Z`, `available_at 20:00Z`, **`no_verificable_timing` / `roto` / `cuenta_para_N 0`**, `insumo_completo false` (TOELY), **33 filas**, `ext_2026-09-28.csv` (sha `2e984469…`) escrito y respaldado. Base (ro): 33 filas en ese estado. |
| `mki-snapshot` | 14:42:52.709 → 14:43:30.755 (43 s, sin reintentos) | `data/snapshot.log:133-140`: **selló** `{'snapshot': True, 'predicciones': 8, 'regimen': 'Alcista · vol baja', 'roca_chip': 44, 'descarga': '28/28'}`; **envió la retractación del vigía 17:43:07.30Z** (:135-136, `_epilogo_vigia`); verificador apertura 9, puntaje 44; 8 CSV; **salud de datos OK (27 tickers)** (:140). Base (ro): `snapshots` 2026-09-28 `timestamp_utc 17:42:58.943983Z`, `sox_usado_pct −1,63`, `sox_fecha 2026-09-28`; `senales_ticker`: **24 filas con `available_at > timestamp_utc`, única fecha así en la tabla**. |
| `mki-noticias` | 14:42:52.704 → 14:45:21.298 | `data/noticias.log:120-125`: dedup (9 duplicados), **286 titulares nuevos** (17:45:19Z), «análisis falló en el lote 1: Error code: 400 … credit balance is too low», **analizados 0 de 3361, costo 0,0000 USD**; ledger `data/costos_ia.log:39` `resultado 'ok'`, `costo_usd 0.0`. |

Telegram ese día: **cuatro mensajes, tres fuera de hora en 11 s** (alerta 17:42:56.18Z, reporte 17:42:56.46Z,
retractación 17:43:07.30Z) y el reporte de las 18:25. La bitácora 14 §0-bis.9 titula «dos mensajes»: la
retractación es el tercero. **Orden de fin:** la bitácora 14 (§0-bis.8, §64, acta §89.6) dice que backup
«terminó primero»; el journal dice que **`mki-vigia-rechequeo` terminó primero (14:42:53.303) y backup segundo
(14:42:53.790)**: backup fue el primero **de los que escriben**. Errata menor, candidata.

**A.2 A la hora normal, el mismo día (todo medido).** noticias 17:50:00 → 17:52:40: 96 nuevos, la misma falla
400, 0 USD (`noticias.log:126-131`). **snapshot 18:15:00 → 18:15:14: `{'snapshot': False, 'motivo': 'ya existe
snapshot de hoy'}`**, verificador apertura 0, puntaje 4, salud: «Tokyo Electron (8035.T): salto de −80 % el
2026-09-28 — revisar split/dato corrupto» (`snapshot.log:141-147`). reporte 18:25:00 → 18:25:02: **831
caracteres**, «Reporte enviado 18:25» (`reporte.log:47-48`). backup 18:40:00: **`f7b65e0`**, 9 archivos, +813 −22,
con `ext_2026-09-28.{csv,meta.json}` y la fila de `snapshots` del 28 (`git show --stat`). vigía 19:00:00: **todo OK**,
incluido «ancla temporal: 8/8 filas con cierre del SOX» sobre las 8 filas invertidas (`vigia.log:227-234`;
`mki_vigia.py:97` prueba `av == ts`). rechequeo 20:30:00: sin marcador (`vigia.log:235-236`). sonda 21:05 → 00:35
Chile, ocho pases: 1/36 a las 20:05–21:05 NY, 35/36 de 21:35 a 23:35 NY (`sonda_cierre.log:34-41`). **sellador
00:30:00 → 00:30:04 del 29: `divergencia_registrada`, 0 filas, `decisiones_distintas 0`** (`sello_dinero.log:473-482`);
base (ro): `divergencias_sello` id 2, `fecha_insumo 2026-09-28`, `timestamp 2026-09-29T03:30:04.346Z`;
`sellos_dinero` 462 filas, 14 fechas, **9 cuentan**. La predicción de la bitácora 14 §0-bis.2 se cumplió.

**A.3 El 29-sep-2026, 18:38:57 Chile (17:38 NY, 98 min después de la campana), cambio de calendario.** Journal
(`systemd[317]`, mismo proceso, así que el orden de las marcas es el orden de emisión): `.165914` «Reload
requested from client PID 91601 ('systemctl')» · `.274150` «Reloading finished in 106 ms» · **`.327292` «Starting
mki-sonda-cierre.service»** · `.330093` «Stopped mki-sonda-cierre.timer» · `.330127` «Stopping…» · `.330264`
«Started mki-sonda-cierre.timer» · `18:38:59.973` Finished. `systemctl show`: `Persistent=no`,
`ActiveEnterTimestamp 18:38:57`. Último disparo antes del cambio: **29-sep 00:35:00** Chile (journal). Escribió
**36 filas**, `timestamp_utc 2026-09-29T21:38:57.684Z`, `hora_ny 17:38`, `sesion_ny 2026-09-29`, **35/36 con la
barra de hoy** (`sonda_cierre.log:42`); a las 20:05, 20:35 y 21:05 NY, **1/36** (`:43-45`).

**A.4 Censo, todo el journal retenido (desde 2026-08-24T23:14).** 212 arranques de `mki-*.service`; **10 fuera
del calendario instalado**: los 8 del 28-sep, el de la sonda del 29-sep, y **uno el 25-ago 19:34:41**
(`mki-vigia-rechequeo`, 2 min después de instalar los timers; compatible con un arranque manual de prueba; no
investigado). Tres activaciones de timers **sin** disparo inmediato: 25-ago 19:32:41 (instalación, sin stamp),
19-sep 22:26:43 (la sonda, primera vez), 20-sep 02:05:59 (arranque del manager, los ocho). Ninguna cambió un
calendario con historia. **n = 1 despertar, n = 1 cambio de calendario.**

**A.5 La suspensión, acotada por dos relojes (INFERENCIA con dos medidas que coinciden).** El kernel invitado
arrancó el 20-sep 02:05:59 (journal, primer mensaje de `systemd[317]`). A las 22:27:49 del 29-sep,
`CLOCK_MONOTONIC = CLOCK_BOOTTIME = 551.798,7 s` (6 d 9 h 16 min) contra **850.910 s de reloj de pared** desde ese
arranque: **3 d 11 h 05 min que ningún reloj del invitado contó** — y `BOOTTIME = MONOTONIC` dice que el invitado
no vio suspensión propia: la VM fue pausada desde afuera. Si fue una sola pausa terminada a las 14:42:52 del 28,
empezó **≈ 25-sep 03:37**. El journal del SISTEMA lo confirma por otra vía: `systemd-resolved: Clock change
detected` cada 30 s, con un único hueco mayor a 2 min entre el 20-sep y hoy, **del 2026-09-25 03:37:10 al
2026-09-28 14:42:52** (medido por el orquestador, bitácora 15 §0.10; ±30 s). La ventana «[vie 02:16, vie 17:50]»
de la corrida 14 queda superada: la pausa empezó a las **03:37 del viernes 25**. Lo que sigue sin registro es la
causa: que fue una suspensión del host es testimonio de Nicolás (acta §91.5), no un evento del journal.

---

### B. Tabla principal

| # | job (OnCalendar, `Persistent`) | 1. qué hizo el 28-sep a las 14:42 | a su hora normal | 2. guarda al cerrar la corrida 15 | 3. costo MEDIDO (n = 1) | 4. recomendación del agente |
|---|---|---|---|---|---|---|
| 1 | `mki-noticias` (`Mon..Fri 17:50 America/Santiago`, true) | RSS: 286 titulares; 1 llamada IA rechazada (400 crédito); 0 USD | 96 titulares; misma falla; 0 USD | **ninguna de ventana**; tope diario 0,50 USD con freno entre lotes + timeout de red | 0 USD, nada publicado, nada perdido | (iii) nada para la ventana; el problema del job es otro (E.1) |
| 2 | `mki-snapshot` (`Mon..Fri 18:15`, true) | **selló** 24 filas con barra intradía; `roca_chip` 44; `available_at` 2 h 17 min posterior a la emisión | «ya existe snapshot de hoy»; no re-sella | **PLANIFICADO**: (b) se niega si `available_at > emisión`; (a) verificador marca; (d) medición excluye; [el ancla de §90.2 quedó DETENIDA: las dos anclas difieren en 33 filas, tarjeta §71] | 24 filas selladas con insumo no reproducible; sesión del 28 sin sello con cierre; publicadas por reporte y API | (i) exactamente como está firmada: sin margen, sin reloj de pared; frescura y fin de semana como decisión aparte (D) |
| 3 | `mki-reporte` (`Mon..Fri 18:25`, true) | reporte de 400 caracteres con huecos declarados, 3,4 s antes del sello | 831 caracteres desde el sello de las 13:42 NY: «sellado 14:42 Chile», SOX −1,63, Roca→Chip 44 | **ninguna**; sin anti-duplicados por diseño | 2 mensajes en Telegram: 1 de ruido, 1 con cifras de barra parcial; nada perdido | (ii) marcar: el mismo mensaje con la línea «disparo fuera de hora» |
| 4 | `mki-backup` (`Mon..Fri 18:40`, true) | commit `5321f6b` «Backup diario 2026-09-28» **sin nada del 28** | `f7b65e0`, 9 archivos, con la matriz de media sesión | **APLICADO** §90.8: se niega si el snapshot del día no está sellado o si `snapshot.py` está vivo; [fin de semana y día sin sello final: commitea, elección de agente, tarjeta §70] | 1 commit con nombre que no describe su contenido; nada perdido | (i) como está firmada; en fin de semana la misma regla (posterga, no pierde) [la corrida implementó lo contrario: §70] |
| 5 | `mki-vigia` (`Mon..Fri 19:00`, true) | 4 FALLA + 2 OK (uno sostenido por el commit prematuro); alerta enviada; retractada por snapshot.py 11 s después | todo OK, incluida el ancla temporal sobre las 8 filas invertidas | sólo exención de fin de semana; **no se toca en esta corrida** (tarjeta: `av == ts` Y `av > ts`) | 1 alerta falsa + 1 retractación; nada perdido | (ii) marcar «pase fuera de hora», en la misma tanda que `av == ts`; **no** (i): un vigía que calla por una guarda mal escrita es el peor falso negativo de la tabla |
| 6 | `mki-vigia-rechequeo` (`Mon..Fri 20:30`, true) | nada: corrió 2 s antes del marcador | nada: el marcador ya estaba consumido | por construcción sólo actúa con marcador de HOY | 0 | (ii) que el texto use la hora real y no el literal `20:30`, al tocar el vigía |
| 7 | `mki-sonda-cierre` (`Mon..Fri 20..23:05,35` + `Tue..Sat 00..03:05,35 America/New_York`, **false**) | 36 filas a las 13:42 NY, bolsa abierta; el lector las descarta y declara | 8 pases normales | job: ninguna; lector: descarta sólo «antes del cierre»; **no se toca en esta corrida** | 36 filas pre-cierre (28) descartadas + **36 post-cierre fuera de grilla (29) que el lector NO descarta** | (ii) el lector rotula y excluye «fuera de grilla», corrida 16; `regla_58.md` lo dice desde esta noche |
| 8 | `mki-sello-dinero` (`Mon..Fri 23:30 America/New_York`, true) | 33 filas `no_verificable_timing` + `ext_2026-09-28.*` de media sesión | divergencia, 0 filas, 0 decisiones distintas | E4 marca (en producción); §90.6 (a)+(d) **firmado, NO aplicado** | sesión del 28 fuera de N (9 cuentan); cupo de evidencia ocupado y versionado | (ii) tal como está firmada en §90.6; hasta aplicarla la exposición es la del 28-sep |
| 9 | cambio de calendario (`daemon-reload` + `restart`) | — | — | ninguna: **`Persistent=false` no lo impidió** (medido) | 36 filas fuera de grilla el 29-sep, que contaminan la noche del 29 en el dato de §58 | procedimiento (P1)+(P2) escrito en `systemd/INSTALACION.md`; (P0) antes de mover la hora del sellador |

---

### C. Fichas por job

**C.1 `mki-noticias`.** *Hizo:* lo de A.1/A.2. Interacción medida por horas: el snapshot selló a las 17:42:58Z, **antes**
de que noticias escribiera (dedup 17:43:33Z, titulares 17:45:19Z): el sello del 28 usó el caché de noticias anterior
a esa corrida. *Guarda:* ninguna de ventana; tiene el tope diario con freno entre lotes (`mki_noticias.py:91-100,
118-121`) y `socket.setdefaulttimeout(30)` (:36-37). *Costo:* 0 USD, 0 llamadas cobradas (1 intentada y rechazada);
si hubiera crédito el techo es el tope de `.env` (código, no medido). *Opciones:* (i) negarse antes de las 17:50
Chile — un despertar de la mañana no corre y el pase normal de las 17:50 sí, así que no pierde nada; una guarda mal
escrita (huso) lo apaga todos los días y lo detecta el vigía («noticias: el job NO corrió hoy»). Con la no elegida se
pierde: nada medible. (ii) marcar `fuera_de_hora` en el ledger. (iii) nada: un pase extra bajo tope. **Recomendación
del agente: (iii).** Lo que este job necesita no es una ventana: ver E.1.

**C.2 `mki-snapshot`.** *Hizo:* A.1/A.2. Hoy las 8 filas con predicción están `verificada` (verificador del 29-sep
18:15, `snapshot.log:150` `'verificadas': 9`) y hay **8 filas en `verificacion_apertura` con `fecha_senal 2026-09-28`**
(consulta ro), que es lo que la (d) planificada excluirá por regla. *Guarda hoy:* ninguna de conocibilidad ni de
ventana; sólo la idempotencia por fecha (`senales.py:181-187`, `snapshot.py:93-94`) y la regla maestra del verificador,
que compara sólo `emitida >= apertura` (`senales.py:334`). **PLANIFICADO en la corrida 15:** (b), (a), (d) y el ancla
en la emisión, tal como firmó §90.1/§90.2.
*Medido sobre la historia, para dimensionar el falso negativo de la (b):* 45 snapshots con `sox_fecha` sellado
(27-jul → 29-sep). Margen emisión − cierre de la sesión de `sox_fecha`: **negativo en 1 solo (28-sep, −137 min)**;
mínimo positivo 75,1 min (14-sep); **15 de 45 por debajo de 120 min** (todos desde el 8-sep, con Chile en UTC−3).
Calculado con `exchange_calendars`: **del 2-nov-2026 al 12-mar-2027 el margen es de 15 minutos** (18:15 Chile =
21:15 UTC contra cierre 21:00 UTC en EST); vuelve a 75 min el 15-mar y a 135 min el 5-abr-2027. Consecuencia: la (b)
**sin margen** habría rechazado exactamente 1 de 45 (el 28-sep) y cero sellos buenos; una (b) que reusara el margen
de publicación de 2 h de `calendarios.sesion_ya_cerro` (`calendarios.py:94`, default `margen_horas=2.0`) habría
rechazado 16 de 45 y **rechazaría todos los días de noviembre a marzo**: una sesión irrecuperable por día. Ese es el
costo de una guarda mal escrita en este job, y por eso la ventana de este job no puede ser de reloj de pared.
*Costo medido:* 24 filas selladas con un insumo que la fuente ya no sirve (bitácora 14 §11.3), 8 ya verificadas,
1 fila de `snapshots` con `roca_chip` 44 y régimen desde barra parcial, publicadas por el reporte de las 18:25 y por
`/` y `/cadena`; y la sesión del 28 sin sello con cierre. n = 1.
*Sobre el 44 contra 17 (PROVISIONAL, y hay un dato nuevo):* `snapshot.log:140` — el bloque de las 17:42Z, el que
selló el 44 — dice **«salud de datos: OK (27 tickers)»**; el de las 21:15Z marca 8035.T con −80 % (:146-147); el del
29-sep 21:15Z vuelve a **OK y sella `roca_chip` 50** (:149, :153). O sea que el salto **no estaba en la descarga con
la que se selló el 44** y ya no estaba el 29; el 17 se recomputó a las 20:31Z, entre esas dos lecturas. INFERENCIA:
el 17 es compatible con haberse calculado con el salto presente. Sigue PROVISIONAL: nadie releyó `roca_chip_al` del
28 con la fuente ya corregida, y este bloque no descarga.
*Opciones:* (i) negarse **[PLANIFICADO (b)]**. Con la no elegida se pierde: (ii) marcar al sellar (estado no
verificable en el sello, como E4) **sin** tocar la idempotencia deja la fecha quemada igual — el mismo problema que §62
en el otro riel —, así que (ii) sólo vale si `ya_existe_snapshot_hoy()` distingue estados; (iii) nada: cada despertar
con bolsa abierta sella 24 filas inválidas y quema la sesión. **Recomendación del agente: (i) exactamente como está
firmada — sin margen de publicación y sin ventana de reloj de pared —, y los dos huecos de D.1 y D.2 (frescura, fin
de semana) como decisión aparte con sus cuentas a la vista.**

**C.3 `mki-reporte`.** *Hizo:* A.1/A.2. El texto no queda en ningún log en modo titular (sólo el largo), así que
el contenido se deduce del código: a las 14:42, «⚠ sin snapshot sellado hoy», «Régimen / SOX / Roca→Chip: sin sello
hoy», «Aperturas: sin predicciones selladas hoy», track record 30 d y cobertura (`alertas.py:230-231, 250, 273,
278-290`); a las 18:25, cabecera **«sellado 14:42 Chile»**, «SOX: −1.63 % (sesión del 2026-09-28)», «Roca→Chip: 44/100»,
8 predicciones «emitidas 14:42 Chile, antes de la apertura objetivo» (`:226-228, 238-239, 242, 269-271`; valores de
`snapshots`). **El mensaje publicó su propia hora de emisión.** *Guarda:* ninguna; sin anti-duplicados por diseño
(`alertas.py:305-310`). Al cerrar la corrida 15, igual; la (b) del snapshot le quita la fuente del segundo daño.
*Costo medido:* dos mensajes, uno de ruido (verdadero en ese segundo) y uno con cifras de barra parcial. Nada perdido.
*Recuperabilidad, leída del código:* `./mki reporte` reenvía el mismo día; `componer_reporte_sellado()` usa
`date.today()` y el CLI no acepta fecha (`alertas.py:220, 345-373`): pasado el día no hay reenvío de esa fecha. Un
falso negativo acá cuesta la publicación del día si nadie lo ve antes de la medianoche; el vigía lo grita a las 19:00
(`mki_vigia.py:199-213`). *Opciones:* (i) negarse antes de las 18:25 Chile — un despertar de mañana no manda nada;
uno de la tarde, después de las 18:25, manda (tardío, legítimo); mal escrita, apaga el reporte y lo detecta el vigía.
Con la no elegida se pierde: la anotación en el propio mensaje. (ii) marcar: el mismo mensaje con «disparo fuera de
hora (14:42; programado 18:25)» — **nunca pierde un envío; un error en la marca sólo etiqueta mal**. (iii) nada.
**Recomendación del agente: (ii).**

**C.4 `mki-backup`.** *Hizo:* A.1/A.2. Efecto colateral medido: el commit de las 14:42:53 hizo que el vigía de las
14:42:55 diera «OK backup: commit de hoy presente» (`vigia.log:223`; `mki_vigia.py:224-229` mira `git log -1
--format=%cs -- data/backups`): **un OK sostenido por un commit que no contenía el sello del día.** *Guarda hoy:*
ninguna (`mki_backup.py:41-49`, pathspec). **PLANIFICADO** §90.8. Un feriado de NYSE en día hábil **sí** tiene snapshot
(7-sep se selló con `sox_fecha` 4-sep: consulta ro), así que lo que §90.8 deja por definir es el fin de semana, que
hoy sólo llega por catch-up o por cambio de calendario. *Costo medido:* un commit en el historial con un nombre que
no describe su contenido; nada perdido (todo entró en `f7b65e0`). *Opciones:* (i) negarse **[PLANIFICADO]** — mal
escrita, en un día sin sello real posterga el export del sellador de esa noche al día siguiente: **posterga, no
pierde**. (ii) marcar: commitear con «Backup parcial <fecha> (antes del sello)» — artefacto mal formado pero bien
nombrado. (iii) nada. **Recomendación del agente: (i) como está firmada, con la misma regla en fin de semana (sin
snapshot ese día, no commitea; el lunes lo hace).**

**C.5 `mki-vigia`.** *Hizo:* A.1/A.2. La retractación la envió `snapshot.py` (`snapshot.py:219-231`), no el
rechequeo; su texto (deducido, `mki_vigia.py:338-344`): «recuperado: snapshot sellado (emisión 14:42, confirmada a las
14:43), descarga 28/28, predicciones 8» — retracta el conjunto consumiendo el marcador; las FALLAs de noticias y
reporte no se nombran. La alerta vivió **11,1 s**. *Guarda:* sólo la exención de fin de semana (`mki_vigia.py:405-407`).
No se toca en esta corrida. *Interacción con la (b) planificada [DEDUCIDO]:* en un próximo despertar con la bolsa
abierta el snapshot se niega, el vigía alerta «NO se selló» y deja el marcador, y la retractación recién sale cuando
el snapshot de las 18:15 sella (`_epilogo_vigia`): **la alerta falsa pasa de 11 s a ~3,5 h abierta**. Si el despertar es
después de las 18:15 con bolsa cerrada, el snapshot sella tarde y la secuencia es la del 28-sep. *Costo medido:* una
alerta falsa y una retractación; nada perdido. *Opciones:* (i) negarse a pasar lista antes de las 19:00 Chile — con la
no elegida se pierde nada medible, pero **si la guarda está mal el vigía calla, y el vigía es la alarma**; sólo
`/salud` lo cubriría. (ii) marcar: pasar lista igual y decir en la alerta «pase fuera de hora (14:42; programado
19:00): los jobs de hoy pueden no haber corrido todavía»; o evaluar cada chequeo sólo si su hora programada ya pasó
(exige duplicar seis horas en el código: dos fuentes de verdad). (iii) nada. **Recomendación del agente: (ii), en
la misma tanda que arregle `av == ts` (un solo toque al vigía); no (i).**

**C.6 `mki-vigia-rechequeo`.** *Hizo:* nada, las dos veces. *Guarda:* sólo actúa con marcador de HOY
(`mki_vigia.py:289-299, 352-374`). *Costo medido:* 0. *Lo que no pasó por 27 ms [DEDUCIDO, n = 0]:* con el orden
inverso habría encontrado el marcador y, con el snapshot todavía corriendo, enviado «sigue sin sellar a las 20:30:
reintentos aún activos» a las 14:42 — la hora es el literal `HORA_RECHEQUEO` (`mki_vigia.py:46, 368-370`).
*Opciones:* (i) negarse antes de las 20:30 del día del marcador; (ii) que el texto lleve la hora real; (iii) nada.
**Recomendación del agente: (ii) al tocar el vigía; nada aparte.**

**C.7 `mki-sonda-cierre`.** *Hizo:* A.1/A.2/A.3. *Lo que el lector hace con eso, calculado en memoria con
`GEMELO.sonda_cierre_resumen.resumen()` sobre el CSV filtrado, sin escribir:* noche del 28 — descarta las 36 de las
13:42 (anteriores al cierre) y las declara; aparición 21:35 para 34 tickers, 20:05 para 1, ninguna para TOELY.
**Noche del 29 — NO descarta las 36 de las 17:38** (posteriores al cierre de las 16:00) **y les atribuye la aparición:
«17:38» para 35 tickers**, cuando a las 20:05, 20:35 y 21:05 esos mismos tickers no tenían la barra. El filtro de la
corrida 14 (`sonda_cierre_resumen.py:104-120`) cubre «antes del cierre», no «fuera de grilla»; la aparición se toma
como mínimo (`:128-130`). **Esto contamina la noche del 29 en el dato de §58 si no se filtra.** *Guarda:* ninguna en
el job (`sonda_cierre.py:180-198`). No se toca en esta corrida (primera noche de madrugada; deudas (3) y (4) a la 16).
*Costo medido:* 36 filas pre-cierre (28-sep) descartadas y declaradas; 36 post-cierre fuera de grilla (29-sep) que
entran como aparición. Nada perdido; algo agregado que hay que filtrar. n = 2 disparos. *Y un dato que nadie
buscaba (DESCRIPTIVO, n = 1):* a las 17:38 NY, 98 min después de la campana, **la barra fechada hoy existía para
35/36 y a las 20:05 no (1/36)**: la retirada de la barra intradía ocurre **después** de las 17:38 NY, no «al cerrar la
sesión» como escribe la bitácora 14 §11.3 (errata candidata). *Opciones (las de §63, actualizadas):* (i) el job se
niega fuera de grilla (minuto fuera de {05, 35} u hora fuera de las franjas) — con la no elegida se pierde la fila y
con ella la evidencia: el dato de las 17:38 no existiría. (ii) el lector rotula y excluye «fuera de grilla» además de
«antes del cierre», declarándolas — **la única que arregla lo que ya está en disco (72 filas)**. (iii) nada: cada
disparo fuera de grilla posterior al cierre entra como aparición. **Recomendación del agente: (ii), en la corrida 16
junto con las deudas (3) y (4); y que `regla_58.md` diga desde esta noche que la noche del 29 lleva una observación
fuera de grilla.**

**C.8 `mki-sello-dinero`.** *Hizo:* A.1/A.2. *Guarda:* E4 marca (`sello_dinero.py:557-564`); `sello_previo()` no
distingue estados (`:287-304`), así que la fecha queda ocupada (`:346-363, 580-602`). §62/§90.6 (a)+(d) **firmado, no
aplicado**; al cerrar la corrida 15, PROPUESTA de política y parche en worktree, aplicación por acta posterior.
*Costo medido:* sesión del 28 fuera de N (contador 9), con **0 de 33 decisiones distintas** entre la barra intradía y el
cierre (la base lo dice); cupo de evidencia `ext_2026-09-28.*` ocupado por una matriz de media sesión, versionado en
`f7b65e0`. n = 1. *Opciones:* (i) negarse antes de escribir (sin fila y sin `ext_` cuando `ahora < cierre de la sesión
de hasta`) — deja la fecha libre para las 23:30 NY; con la no elegida se pierde el rastro en la base (queda en journal
y log) y es un camino nuevo en el sellador («un cambio por noche», §87). (ii) marcar **[E4, en producción]** + §62
(a)+(d) **[firmado]** — la fecha no queda quemada y el evento queda registrado. (iii) nada: cada despertar quema una
sesión de N y un cupo de evidencia. **Recomendación del agente: (ii) tal como está firmada en §90.6; hasta que se
aplique, la exposición es exactamente la del 28-sep.**

---

### C.9 Novena fila: cambio de calendario de un timer instalado

**Hechos, MEDIDOS (A.3).** El service arrancó **53 ms después** del fin de la recarga y **2,8 ms ANTES** del
`Stopped`/`Started` del timer. **`Persistent=false` no lo impidió** (`systemctl show`: `Persistent=no`).

**Cálculo (`systemd-analyze calendar`, systemd 259.5-0ubuntu3.4, sin tocar unidades).** Base = último disparo
(2026-09-29 00:35:00 Chile) + expresión nueva `Tue..Sat 00..03:05,35 America/New_York` → próximo **2026-09-29
01:05:00 −03, «21h ago»** (pasado a las 18:38:57). Misma base + expresión vieja `Mon..Fri 20..23:05,35` → 21:05:00
(futuro). Base = 18:38:57 + expresión nueva → 30-sep 01:05:00 (futuro). **Computado desde el último disparo, el
próximo caía en el pasado; computado desde el reinicio, en el futuro. La máquina hizo lo primero.**

**Lo que el manual documenta y lo que no (`man systemd.timer`, esta máquina).** `Persistent=` (p. 190-193): «When
the timer is activated, the service unit is triggered immediately if it would have been triggered at least once
during the time when the timer was inactive» — sólo para `true`. `OnCalendar=` (p. 106-108): un timer que venció
mientras el sistema dormía «will catch up and process all timers that triggered while the system was sleeping», y
si venció varias veces «will only result in a single service activation» — **es la premisa de §63, ahora con cita:
documentado y sin directiva que lo apague.** `DeferReactivation=` (p. 168-175): por defecto «the timer schedules
the next elapse based on the previous trigger time» y un elapse en el pasado «causing it to immediately trigger».
**No documenta** qué hace `daemon-reload` ni `restart` con un timer `Persistent=false` que cambió de calendario.

**INFERENCIA desde el orden del journal, no probada:** el disparo lo produjo la **recarga** (`daemon-reload`), que
releyó la unidad con el calendario nuevo y rearmó el timer desde el último disparo recordado; el `restart` llegó
cuando el service ya había arrancado. La hipótesis del acta §91.7/§91.8 (fue el `restart`) es compatible con el
segundo, no con el orden de las líneas. Distinguirlo exige una prueba en una unidad, prohibida en este bloque. Si
la inferencia es correcta, **evitar el `restart` no protege**: la recarga es obligatoria para cargar la unidad
editada.

**Opciones de procedimiento.** (P0) Medir la semántica —reload solo, restart, stop → editar → reload → start, con
`Persistent=` true y false— en una unidad desechable que ejecute `/bin/true`, un sábado: 15 minutos, acto de Nicolás,
fuera de esta corrida. (P1) Antes de cambiar un calendario: `systemctl --user list-timers` → columna `LAST` de esa
unidad; `systemd-analyze calendar --base-time='<LAST>' '<expresión nueva>'`; **si «From now» dice «ago», el cambio
dispara en el acto**: elegir otro momento u otra expresión, o aceptar el disparo sabiendo qué hace ese job (tabla de
abajo). (P2) Elegir el momento por job. (P3) Parar el timer antes de editar y recargar, y arrancarlo después: **no
probado**; para `true` el manual dice que al activar se dispara si hubo elapse durante la inactividad y no dice desde
qué base se computa; para `false` no dice nada. (P4) La guarda en el job (filas 1-8) es la única defensa que no
depende del procedimiento.

**Momentos en que un disparo inmediato es inocuo, por job [DEDUCIDO del código y de lo medido; n = 0 salvo donde se dice]:**
noticias: cualquiera (cuesta a lo sumo el tope). snapshot: día hábil después del sello (→ «ya existe snapshot de
hoy», **medido** 28-sep 18:15); **nunca sábado ni domingo**: sin exención de fin de semana en el código (`grep
weekday|is_session` vacío en `snapshot.py`) sellaría un snapshot con fecha sábado, `sox_fecha` viernes y objetivo
lunes, duplicando el del viernes; la (b) planificada lo deja pasar (historial: 2 de 60 snapshots en fin de semana,
4 y 5-jul, pre-4.6). reporte: después de las 18:25 (duplica el mismo texto). backup: después de las 18:40 (sin
cambios, no commitea). vigía y rechequeo: sábado o domingo (exentos) o después de su hora con el día en OK. sonda: no
hay momento inocuo hasta que el lector filtre fuera de grilla; el menos malo, un sábado de día (la fila va a la
sesión del viernes, post-cierre, y contamina esa noche). sellador: **entre las 00:35 y las 10:00 de Chile, de martes a
sábado** (fecha ya sellada → `ya_sellada` o divergencia sin pérdida); **nunca con la bolsa abierta** (E4 la marca y
quema la fecha) **ni entre el cierre y las 23:30 NY** (sellaría temprano con timing ok y lo que selle queda).

**Recomendación del agente:** (P1)+(P2) como procedimiento escrito en `systemd/INSTALACION.md`, y (P0) **antes** de
mover la hora del sellador por §58 (b)/(c), porque ahí un disparo inmediato quema una sesión de N.

---

### D. Huecos que quedan DESPUÉS de la corrida 15 [DEDUCIDOS del código; n = 0 eventos]

**D.1 Frescura.** Despertar de mañana en día hábil (antes de la apertura de NYSE, p. ej. 09:00 Chile): el snapshot se
dispara (catch-up de ayer), `date.today()` es hoy, `sox_fecha` es ayer (sesión cerrada) → la (b) pasa → sella el
snapshot de HOY con el cierre de AYER; a las 18:15 «ya existe» → **la sesión de hoy queda sellada con insumo viejo y el
verificador la acepta** (emisión antes de la apertura objetivo, `available_at < emisión`). El riel de dinero tiene
`insumo_fresco` para exactamente esto (`sello_dinero.py:559-571`); el de medición no. Cuenta histórica: **0 de 45**
snapshots con `sox_fecha ≠ fecha` en día de sesión XNYS (el único distinto, 7-sep, es feriado de NYSE). Opción posible:
negarse si hoy es sesión XNYS y `sox_fecha ≠ hoy` — cero falsos negativos históricos; un día con Yahoo atrasado dejaría
de sellar, el mismo trato que la (b).

**D.2 Fin de semana.** snapshot, reporte, backup y noticias no tienen exención de fin de semana en el código; sólo el
`Mon..Fri` del timer los frena. Un disparo inmediato en sábado (cambio de calendario, restart, o catch-up si la
máquina despierta el sábado después de perder el viernes) sella un snapshot con fecha sábado. Si el sello del viernes
existe, duplica su predicción (mismo insumo, mismo objetivo lunes); si el viernes se perdió, lo recupera con fecha
sábado (timing válido). Ningún exchange del universo abre sábado o domingo.

**D.3** La alerta del vigía con la (b): ~3,5 h abierta en vez de 11 s (C.5). **D.4** El rechequeo con el orden
inverso (C.6). **D.5** La sonda fuera de grilla post-cierre (C.7). **D.6** El sellador hasta aplicar §90.6 (C.8).
**D.7** El margen de 15 min desde el 2-nov para cualquier guarda que agregue margen (C.2).

---

### E. Hallazgos de paso, fuera del alcance, no corregidos

**E.1 `mki-noticias` no analiza nada desde el 7-sep, y todo dice «ok».** `data/noticias.log` tiene **17** líneas «análisis
falló en el lote 1: Error code: 400 … Your credit balance is too low to access the Anthropic API» (la primera en la
línea 39, `2026-09-07T20:52:21Z`); `data/costos_ia.log` líneas 25-41: **17 corridas seguidas con `analizados 0`, `costo_usd
0.0` y `resultado 'ok'`**, `pendientes_restantes` de 260 a **3.672**; la última con análisis fue el 4-sep (línea 24: 214
analizados, 0,116103 USD). El ledger dice «ok» porque `mki_noticias.py:123-128` corta el bucle en la excepción y
`:149-152` registra «ok» igual; el vigía repite «noticias: ok · 0 analizados · 0.0000 USD» (`vigia.log:230, 240`).
Consecuencia deducida, NO medida: `sentimiento_promedio_por_ticker()` alimenta el sello (`snapshot.py:180`) con análisis
de hasta el 4-sep bajo decaimiento 0,7^días y piso 0,1: los `sentimiento_ia`/`puntaje_ia` sellados desde el 7-sep se
apoyan en titulares viejos. No está en `DECISIONES.md` (grep: sólo el §79 sobre los créditos de la corrida 09). Va a
tarjeta o acta; este inventario no lo decide.

**E.2** `data/sombra_telegram.log` tiene mtime `2026-08-28 18:25:01 −04:00` (`ls --time-style=full-iso`): es del 28 de
**agosto**, el último reporte en sombra antes del switch del 30-ago (`reporte.log:5-6`). Cierra el ítem de diagnóstico
que el curador dejó en la corrida 14 («mtime de las 18:25 en una máquina titular»): mismo día, otro mes.

**E.3** El dictamen del auditor cita `mki_vigia.py:99` para `av == ts`; en el árbol actual es la línea **97**.

**E.4** Las dos unidades instaladas siguen con su `Description=` errada (`systemctl cat`): la sonda dice «la franja
de madrugada no está instalada» y el sellador «PROPUESTA no instalada». Edición manual de Nicolás (§90.9, §91.7).

---

### F. Lo que de §63 queda absorbido acá

1. Su premisa —**no hay directiva de `[Timer]` que suprima un disparo vencido durante una suspensión, y
   `Persistent=` gobierna otra cosa**— pasa a ser la premisa de las nueve filas, ahora **con cita del manual**
   (`OnCalendar=`, catch-up al reanudar con una sola activación) además de la medición del 28-sep.
2. Sus tres opciones para la sonda (guarda en el script / guarda en el lector / nada) son las (i)/(ii)/(iii) de la
   fila 7, con el dato nuevo de que el lector hoy no cubre «fuera de grilla post-cierre» (29-sep, 17:38 NY).
3. Lo que remitía a §61 y §62 quedó firmado en §90.1 y §90.6; acá sólo se sitúa.
4. Su errata de `Description=` sigue vigente (E.4).
5. Su hallazgo de que «el evento se reconstruye del hueco más el PID sobreviviente» se afina en A.5: dos relojes
   independientes acotan la pausa al viernes 25 a las 03:37, ±30 s.
Nada de §63 se pierde; el orquestador la marca FUNDIDA.

---

### G. Lo que este inventario NO midió

- **Hay un solo despertar y un solo cambio de calendario.** Ninguna tasa, ninguna extrapolación.
- **La suspensión es inferencia.** WSL2 no anota suspend/resume; lo medido son dos relojes que coinciden (A.5) y el
  hueco del journal del sistema (medido por el orquestador, bitácora 15 §0.10). La causa (suspensión del host) es
  testimonio. Los logs del lado Windows no se leyeron. El cómputo de A.5 supone una sola pausa.
- **Los textos de Telegram no existen en ningún log en modo titular**: sólo largos (`reporte.log`) y «enviada»
  (`vigia.log`, `snapshot.log`). Qué decían se deduce del código y del sello.
- **Cuál de `daemon-reload`/`restart` disparó la sonda el 29-sep**: inferido del orden de las líneas, no probado.
- **Cómo se comportan los jobs con las guardas planificadas**: deducido; el árbol leído era `2f73eb2`, sin ellas.
- **Los escenarios de la mañana y del sábado (D.1, D.2)**: deducidos, cero eventos.
- **Cuánto habría gastado noticias con crédito**: no medido.
- `puntaje_v0`, `puntaje_ia` y `divergencias` del 28-sep: siguen sin medir (bitácora 14 §9.5-bis); el 44 contra 17 de
  `roca_chip` sigue PROVISIONAL, con el dato nuevo de C.2.
- No se abrieron `noticias.db` ni `alertas.db`; no se corrió ningún job, ningún test ni ninguna función del motor;
  no se leyó `.env`; el journal del sistema no lo leyó este bloque (sólo cita el dato del orquestador).
- El arranque fuera de calendario del 25-ago (A.4) no se investigó.

**No se eligió nada.**

---

## 67. El vigía prueba igualdad (`av == ts`) y no orden: las dos guardas, no una (corrida 15)

**El hecho.** `mki_vigia.py::chequear_ancla_temporal()` (líneas ~79-101) alerta cuando alguna
predicción sellada hoy tiene `available_at` igual a `timestamp_utc`: es la guardia del acta §82.2 (c)
para la rama del `except` de `snapshot.py`, donde `available_at` cae al reloj de pared. El 28-sep
las 24 filas tenían `available_at` 2 h 17 min POSTERIOR a `timestamp_utc` y el vigía dijo
«OK ancla temporal: 8/8 filas con cierre del SOX». Probaba igualdad; la inversión no es igualdad.

**Por qué no se tocó en la corrida 15.** El encargo lo delegó al `director-programa`, que dictaminó
VA A TARJETA por dos razones (`dictamen_15/director_premortem.md`, §2): (a) es el único módulo del
bloque 1 que habla por Telegram, y no se toca la alarma la misma noche en que se cambia lo vigilado
(`snapshot.py` y `senales.py`); (b) la instrucción del encargo («pasa a probar orden, `av <= ts`»)
era una REGRESIÓN escondida: reemplazar la igualdad por el orden apaga la detección de la rama del
`except`, que es un defecto distinto y real. Con las guardas (a) y (b) de §90.1 aplicadas, una fila
con `available_at > timestamp_utc` ya no puede sellarse, así que la urgencia es baja.

**Opciones.**
- **(a) Los dos chequeos**: `av == ts` (rama del `except`, alerta como hoy) Y `av > ts` (inversión,
  alerta nueva con su propio texto). Cambia un mensaje de Telegram; test para cada rama. Es la
  recomendación del director, etiquetada como tal.
- **(b) Sólo orden (`av <= ts`)**, como decía el encargo. Coste: pierde la detección de la rama del
  `except`, que hoy es la única marca de que `available_at` es reloj de pared.
- **(c) Nada**: las guardas del bloque 1 ya impiden que la inversión se selle; el vigía sigue ciego
  al caso, pero el caso ya no puede nacer. Coste: si el bloque 1 se revirtiera, nadie avisaría.

**De paso, sólo si se toca el vigía:** la errata cosmética de su mensaje, que dice «launchd» en una
máquina con systemd (bitácora 14, 0-bis.9).

**No se eligió nada.**

---

## 68. 8035.T: la fuente sirvió un split 5:1 a medias, el sistema no ajusta splits por su cuenta y el aviso de salud no frena el sello (corrida 15)

**MEDIDO, 29-sep 22:26 Chile, sólo lectura contra yfinance.** La fuente sirve para 8035.T (Tokyo
Electron) un `Stock Splits = 5.0` con fecha 2026-09-29 (hora de Tokio). Con eso, la serie que sirve
HOY es consistente: cierre del 25-sep 11.304, del 28-sep 11.264, variación **−0,35 %**. El aviso
«salto de −80 % el 2026-09-28» que `salud_datos_al` escribió en `data/snapshot.log:147` a las 18:15
del 28-sep era la fuente sirviendo, en ese momento, el 28 ya dividido por 5 y el 25 todavía sin
dividir (o al revés): un artefacto transitorio de la fuente aplicando el ajuste a medias. El 29-sep a
las 18:15 la salud volvió a «OK (27 tickers)» y el aviso no se repitió.

**`roca_chip` del 28-sep releído con la serie de hoy** (`motor.roca_chip_al(date(2026,9,28))`,
función pura, sin base ni escritura): **39**, crudo +2,6 %. DESCRIPTIVO. Contra: 44 sellado a las
13:42 NY con la barra intradía; 17 recomputado por la corrida 14 a las 17:31 del 28 con el artefacto
del split (bitácora 14, 9.4, PROVISIONAL desde entonces). Los otros días reproducen lo sellado: 24-sep
42 = 42 sellado; 29-sep 50 = 50 sellado. **El 17 era el artefacto; la brecha real entre lo sellado y
lo recomputado es 44 contra 39.** La fila sellada no se toca (Constitución 5.0, punto 3).

**Hallazgo, no corrección.** `motor.py` confía en `auto_adjust=True` de la fuente y no ajusta splits
por su cuenta; `salud_datos_al` detecta un salto > 40 % y lo escribe en el log, pero **no frena el
sello ni lo marca**: si el 28-sep el snapshot se hubiera sellado a las 18:15 (no lo hizo: ya estaba
sellado a las 13:42), `roca_chip` habría quedado sellado con el artefacto. `motor.py` es intocable
(regla cero).

**Opciones.**
- **(a) Nada.** Frecuencia medida: 1 artefacto de split en 60 snapshots (n = 1; Wilson 95 % para
  1/60: [0,3 · 8,9] %). Coste: un sello con `roca_chip` (y `puntaje_v0`) contaminado el día que una
  fuente aplique un split a medias en la ventana de las 18:15.
- **(b) `snapshot.py` se niega a sellar si `salud_datos_al` reporta un salto > 40 %** en un ticker de la
  cadena. Coste: un día de sello perdido por cada artefacto (o por cada salto real de 40 %, que en
  esta cadena no se ha visto); toca camino de sellado, exige acta y método de worktree.
- **(c) `snapshot.py` sella igual y persiste el aviso en la fila** (columna aditiva), para que el
  reporte y `/salud` lo muestren al lado del número. Coste: columna nueva; no evita la contaminación,
  la declara.

**No se eligió nada.** Cierra lo que §90.9 y §91.9 dejaron abierto sobre 8035.T y el 17 PROVISIONAL.

---

## 69. La skill `gate` sigue importando `scipy` y `sklearn`: la edición la denegó el clasificador de permisos (corrida 15)

**El hecho.** El acta §91.4 firmó la deuda (5) de la corrida 14. El 29-sep a las 22:26 el orquestador
intentó la edición de una línea en `.claude/skills/gate/SKILL.md` y la herramienta `Edit` fue
denegada por el clasificador de permisos de la sesión («Self-Modification»). La deuda (6), en
`.claude/skills/cierre-sesion/SKILL.md`, sí se aplicó en la misma tanda: la misma herramienta la
aceptó. Una barrera puesta a propósito no se rodea con otra herramienta.

**Lo que hay.** `GEMELO/propuestas/skills/gate_gate_de_entorno.md`: la línea vieja, la línea nueva
(`import pandas,numpy,yfinance,exchange_calendars,fastapi`), y la medición de que la nueva corre en
esta máquina. Aplicarla es un `Edit` de una línea que hace Nicolás.

**Opciones.** (a) Aplicar la línea propuesta. (b) Dejar la skill como está y aceptar un gate que falla
por diseño. **No se eligió nada.**

---

## 70. `mki_backup.py`: qué hace un día de semana sin sello cuando ya no puede llegar, y en fin de semana (corrida 15)

**Lo firmado (§90.8).** El backup se niega a commitear si el snapshot del día no está sellado, y lo
registra en su log. Aplicado en la corrida 15 con una función pura de cinco ramas y 83 casos de test
(`tests/test_backup_orden.py`), más una regla 0 que el implementador encontró necesaria: **con
`snapshot.py` vivo nunca se commitea**, porque el sello se escribe antes de que ese proceso exporte los
CSV (el 28-sep, 32 s entre la emisión y el fin del proceso).

**Lo que el acta no da, y esta corrida eligió provisionalmente (elección de agente, a confirmar).**

1. **Día de semana, sin sello, pasadas las 18:15, sin `snapshot.py` vivo.** Implementado: **commitea
   igual** y el log dice «DÍA SIN SELLO: … este commit NO contiene el sello de hoy»
   (`COMMITEAR_DIA_SIN_SELLO = True`, constante con test en las dos posiciones). Razón: §90.8 pide
   ORDEN, no abstención; negarse ahí no ordena nada y deja 24 h o más sin copia versionada en una
   máquina sin réplica (dictamen del director, pre-mortem 15). Se pierde con B: el mensaje del commit
   no distingue ese día (la marca vive sólo en `data/backup.log`, no versionado), y un sello que
   llegue después por mano (`--origen manual`, fallback del dashboard) queda detrás del commit.
   **Opción A, negarse siempre:** se gana que ningún «Backup diario D» exista sin el sello de D; se
   pierde la copia versionada de los CSV que sí cambiaron ese día hasta el próximo día sellado.
   Dato (base del worktree, 4-jul a 29-sep, 62 días de semana): 4 días sin fila en `snapshots`; 6 con
   sello después de las 18:40, todos de la era del Mac. No hay dato para decir cuál costo pesa más.
2. **Fin de semana.** Implementado: **commitea** (no hay snapshot que esperar; lo que cambió es el
   export del sellador de dinero de la noche del viernes). El inventario (§66) recomendaba lo
   contrario: la misma regla que en semana, negarse sin snapshot de ese día (posterga, no pierde).
   Sólo llega un backup en fin de semana por catch-up de `Persistent=` o por un cambio de calendario.
3. **La regla 0, «con `snapshot.py` vivo nunca se commitea», que el orquestador agregó después del
   informe del implementador y que el director marcó al cierre como más ancha que lo firmado.**
   §90.8 firma ORDEN (no adelantarse al sello); la regla 0 además se niega cuando el sello YA existe
   pero el proceso sigue vivo exportando los CSV (los 32 s del 28-sep), y cuando el snapshot está
   reintentando tarde. **Costo medido (`dictamen_15/informe_bloque4.md`, base del worktree, 4-jul a
   29-sep):** 6 días con sello emitido después de las 18:40 (29 y 31-jul, 3, 5, 10 y 21-ago, todos de
   la era del Mac) en que la regla 0 se habría negado a las 18:40 y, como el backup no reintenta,
   esos días habrían quedado sin commit hasta el día siguiente, en una máquina sin réplica; bajo el
   código anterior recibían un commit con los CSV viejos (el defecto de §64). **Opciones:** (a) la
   regla 0 como está (orden estricto; un día de sello tardío queda sin copia versionada 24 h y el
   vigía lo dice); (b) regla 0 sólo cuando NO hay sello (la rama 4 original), y con sello commitear
   aunque el proceso siga vivo (acepta la carrera de 32 s: un commit con los CSV de antes del export,
   que el commit del día siguiente completa); (c) que el backup reintente una vez a los 5 minutos si
   el proceso está vivo (cambia la unidad o el job: toca el timer o suma un `sleep` en un job de un
   segundo). **Recomendación del orquestador, etiquetada:** (a), porque el costo es un día sin copia
   que el vigía grita, y el de (b) es un commit que miente en silencio.

**No se eligió nada:** las tres elecciones son de una línea o una constante y tienen test.

---

## 71. §90.2, el ancla de `snapshot.py:163`: DETENIDA, las dos anclas difieren en 33 filas de 5 fechas (corrida 15)

**Lo firmado (§90.2, opción a).** La sesión objetivo se ancla en el instante de emisión y no en
`available_at`. El encargo 15 mandaba probar primero sobre toda la historia sellada que las dos anclas
dan la misma `sesion_objetivo`, y **parar y reportar si alguna difiere**. Difieren.

**MEDIDO** (base real en `mode=ro`, 439 filas con `sesion_objetivo`, no legacy, hasta el 29-sep; tabla
completa en `dictamen_15/informe_bloque1.md`): **33 filas, 5 fechas.** El ancla de emisión reproduce la
`sesion_objetivo` sellada en 439 de 439 (es la que regía antes de §84.1 en esas fechas); el ancla de
`available_at` difiere en esas 33. Tres familias: (A) sellos tardíos que cruzaron la apertura asiática
(29-jul 01:23Z, 3-ago 02:57Z, 5-ago 01:38Z: 17 filas), justo el defecto que §84.1 corrigió y la
deduplicación arbitra; (B) el sello manual del domingo 5-jul con el SOX del jueves 2 (8 filas); (C) el
feriado de NYSE del 7-sep con `sox_fecha` 4-sep (8 filas). Las 24 filas del 28-sep coinciden bajo las
dos anclas. Test permanente pinchado al corte: `test_historia_las_dos_anclas_difieren_y_por_eso_la_linea_no_se_toco`.

**Lo que pierde cada camino, para decidir.** Con la guarda (b) aplicada, `available_at <= emisión`
siempre, así que anclar en `available_at` ya no puede anclar en el futuro; las dos anclas sólo
difieren cuando la emisión es posterior a la apertura de la sesión que sigue a `available_at`
(sello tardío o feriado de NYSE). Ahí: **ancla `available_at` (la vigente)** = la fila queda
`no_verificable_timing` (se pierde; nunca cuenta un insumo viejo); **ancla emisión (§90.2)** = la
fila es verificable con insumo viejo y forma par con la del día siguiente (lo que §84.1 desarmó).

**Dictamen del `auditor-lookahead` (`dictamen_15/auditor_bloque1.md`, secciones 2 y 4), que corrige la
premisa del encargo.** El encargo justificaba §90.2 con «ahora que la guarda (b) garantiza
`available_at <= emisión`». Eso no garantiza que la sesión siguiente a `available_at` abra después de
la emisión: contraejemplo real, `005930.KS` del 29-jul, `available_at` 29-jul 20:00Z, emisión 30-jul
01:23Z (la guarda (b) pasa) y la sesión de XKRX siguiente abre el 30-jul 00:00Z, antes de la emisión.
**La «puerta entreabierta» que §90.2 quiso cerrar sigue abierta con (b) puesta, y §90.2 tampoco la
cierra: la mueve.** Aplicar §90.2 tal como está firmada volvería a producir, en cada sello tardío que
cruce la medianoche UTC, 7 u 8 filas verificables con la sesión objetivo dos días después del insumo,
y pares duplicados (22 pares (ticker, sesión) repetidos sobre 7 sesiones en la historia) que hoy
arbitra la deduplicación. Dejarlo como está pierde la honestidad del campo `sesion_objetivo` en el
sello tardío hasta que el verificador lo degrada. Lectura del auditor, etiquetada como tal: para un
track record que se defiende de sí mismo, producir filas visiblemente inválidas es el error barato; y
la única puerta que cierra el caso completo es la que ninguna ancla toca: **negarse a sellar cuando la
emisión cae fuera de una ventana declarada respecto del cierre del SOX** (la regla de abstención por
sello tardío, PROPUESTA en `DECISIONES.md` desde la 5.0.2, sin implementar).

**Opciones.** (a) Mantener el ancla en `available_at` y dejar §90.2 sin aplicar (errata fechada al acta).
(b) Aplicar §90.2 por su propio mérito, con la consecuencia medida arriba, y decidir qué hace la
deduplicación con los pares. (c) La regla de abstención por sello tardío (ventana declarada respecto
del cierre del SOX), que vuelve cosmética la discusión del ancla; toca camino de sellado y es
candidata del retador. **No se eligió nada; la línea 163 no se tocó.**

---

## 72. La guarda (b) es necesaria y no suficiente: fuente atrasada, `^SOX` sin barra, fin de semana (corrida 15)

**Lo firmado y aplicado (§90.1 b):** `snapshot.py` se niega a sellar si `available_at > emisión`
(la sesión de `sox_fecha` no cerró). Rechaza exactamente el caso del 28-sep y ninguno de los 45
snapshots históricos con `sox_fecha` (inventario §66, C.2). Tres huecos que quedan, medidos o
deducidos, ninguno firmado:

1. **H0, fuente atrasada (MEDIDO con test).** Con `sox_fecha` de la sesión ANTERIOR, ya cerrada, la
   guarda pasa y se sella con insumo viejo. El acta §90.1 (b) dice que «un día con la fuente atrasada
   deja de sellar»: esta guarda no lo produce. Un despertar de mañana en día hábil (D.1 del
   inventario) sellaría el snapshot de HOY con el cierre de AYER y a las 18:15 diría «ya existe».
   Cuenta histórica: 0 de 45 snapshots con `sox_fecha` distinta de la fecha en día de sesión. El riel
   de dinero tiene `insumo_fresco` para esto; el de medición no.
2. **H2, `^SOX` sin barra y las acciones con barra (DEDUCIDO, n = 0).** La guarda mira sólo
   `sox_fecha`; si en un despertar con la bolsa abierta `^SOX` aún no tiene barra del día pero las
   acciones sí, se sellan `puntaje_v0`, `regimen`, `roca_chip` y divergencias sobre barras intradía con
   `available_at < emisión`.
3. **D.2, fin de semana (DEDUCIDO).** `snapshot.py` no tiene exención de fin de semana; sólo el
   `Mon..Fri` del timer lo frena. Un disparo en sábado sella un snapshot con fecha sábado, `sox_fecha`
   viernes y objetivo lunes.

**Tres consecuencias más de la guarda aplicada, dichas por el auditor para que nadie las descubra en
vivo.** (i) El día que la guarda se niegue, `main()` de `snapshot.py` devuelve 0 (systemd ve éxito) y
el vigía de las 19:00 alerta dos fallas («snapshot: NO se selló hoy» y «descarga: sin snapshot que
revisar») cuya retractación de las 20:30 **nunca llega**, porque sólo se envía cuando hay sello: una
alerta sin epílogo, lo que la 5.0.1 prometió que no volvería a pasar. (ii) El fallback del dashboard
(`app.py:832`) ya no puede sellar mientras NYSE esté abierta (correcto: antes sellaba una barra
intradía) y recomputa el motor entero en cada rerun mientras la guarda se niegue. (iii) **Desde el
lunes 2-nov-2026 la holgura entre las 18:15 de Chile y el cierre de XNYS es de 15 minutos** (Chile
UTC−3, Nueva York UTC−5): cualquier guarda que agregue margen la rompe, y la (b) con margen cero no.
**Precisión al acta §90.1 (b), fechada:** la condición implementada protege contra sellar con la sesión
del SOX ABIERTA; no protege contra sellar con el SOX de una sesión ANTERIOR ya cerrada (H0).

**Opciones.** (a) Nada: los tres casos exigen un despertar o un cambio de calendario, y el inventario
mide n = 1 despertar. (b) Guarda de frescura: negarse si hoy es sesión de XNYS y `sox_fecha` no es
hoy (cero falsos negativos históricos; un día con Yahoo atrasado deja de sellar, el mismo trato que
la (b)). (c) Guarda de ventana en el job, como el riel de dinero: negarse fuera de una franja horaria
declarada; toca camino de sellado y hereda el problema del margen de 15 min desde el 2-nov (C.2).
(d) Que la alerta del vigía distinga «NO sellado por falla» de «NO sellado por negativa declarada»
leyendo el motivo de `snapshot.log` (junto con la tarjeta §67, un solo toque al vigía).
**No se eligió nada.**

---

## 73. Lo que la regla de conocibilidad (§90.1 d) NO alcanza: las métricas vivas de `senales.py`, y `verificacion_puntaje` (corrida 15)

**Aplicado:** la exclusión de toda fila con `available_at > timestamp_utc` vive en
`backtest/linea_base.py::cargar()` y alcanza al árbitro, al informe de la línea base y a todo lo que
carga por `cargar()`. Ninguna cifra publicada cambió (corte 28-ago).

**Lo que no pasa por ahí, censado (`dictamen_15/informe_bloque1.md`):** `senales.py::metricas_apertura`,
`calibracion_intervalos`, `evolucion_aciertos_apertura`, `ultimas_predicciones_apertura`,
`verificaciones_detalle` y `analisis_puntaje_ia`, que alimentan el reporte de Telegram (track record
de 30 días), la API (`/historial`, `/`) y `app.py`. **Hoy las 8 filas del 28-sep cuentan en esas
cifras vivas.** Y `verificar_puntaje_pendientes` no tiene guarda de conocibilidad: las 24 filas del
28-sep con `puntaje_ia` entrarán a `verificacion_puntaje` alrededor del 5-oct. El acta §90.1 (a)
nombra sólo `verificar_apertura_pendientes`, y se aplicó literal; `senales.py` es camino de sellado y
se toca sólo en lo firmado.

**MEDIDO por el auditor (`dictamen_15/auditor_bloque1.md`, B1 y B2 y H3):** `metricas_apertura(30)`
tiene hoy n = 160 y **8** de esas filas son las invertidas del 28-sep; las muestran `alertas.py:278`
(Telegram), `app.py:914` y `:1583`, `api/main.py:536` y `:823`. Y `verificar_puntaje_pendientes` no
aplica **ni la regla de conocibilidad ni la regla maestra** (su único filtro es
`estado != 'legacy_pre_4.6'`): `verificacion_puntaje` viene acumulando desde siempre filas que el
verificador de apertura habría descartado por timing. Texto del auditor para el acta: «La exclusión
(d) rige en la capa de medición del retador. El camino de producción NO la aplica: al 29-sep-2026, 8
de las 160 filas de su ventana de 30 días son filas con `available_at > timestamp_utc`. La cifra que
muestran hoy el dashboard, la API y el reporte de Telegram las incluye. Extender la exclusión a ese
camino es una decisión separada y no está firmada.»

**Opciones.** (a) Extender la guarda (a) a `verificar_puntaje_pendientes` (misma comparación de
instantes, antes del 5-oct) y filtrar `available_at <= timestamp_utc` en las seis consultas de
métricas de `senales.py`: un cambio pequeño en camino de sellado, con acta y método de worktree.
(b) Que la API y el reporte lean sus métricas de `linea_base.cargar()` en vez de `senales.py`: toca
más y cambia la fuente de una cifra publicada por Telegram. (c) Nada: declarar que las cifras vivas
de 30 días incluyen esas 8 filas hasta que salgan de la ventana (28-oct) y que `verificacion_puntaje`
las tendrá para siempre, fuera de toda cifra publicada. **No se eligió nada.** Vence el ~5-oct para la
parte de `verificacion_puntaje`.

---

## 74. `mki-noticias` no analiza nada desde el 7-sep-2026: la API de Anthropic rechaza cada llamada por falta de crédito, y todo dice «ok» (corrida 15)

**MEDIDO** (inventario del bloque 5 y verificado por el orquestador): `data/noticias.log` tiene **17**
líneas «análisis falló en el lote 1: Error code: 400 … Your credit balance is too low to access the
Anthropic API», la primera el `2026-09-07T20:52:21Z` y la última el `2026-09-29T20:52:10Z`;
`data/costos_ia.log` muestra 17 corridas seguidas con `analizados 0`, `costo_usd 0.0` y `resultado
'ok'`, con `pendientes` de 260 a 3.672. La última corrida con análisis fue el 4-sep (214 analizados,
0,116 USD). El ledger dice «ok» porque `mki_noticias.py` corta el bucle en la excepción y registra
«ok» igual; el vigía repite «noticias: ok · 0 analizados · 0.0000 USD». **No está en `DECISIONES.md`.**

**Consecuencia DEDUCIDA, no medida:** `sentimiento_promedio_por_ticker()` alimenta el sello con
análisis de hasta el 4-sep bajo decaimiento 0,7^días con piso 0,1: los `sentimiento_ia` y
`puntaje_ia` sellados desde el 7-sep se apoyan en titulares viejos, y `verificacion_puntaje` los
verifica igual. Los titulares RSS sí se guardan (286 el 28-sep).

**Opciones.** (a) Reponer crédito en la cuenta de la API (acto de Nicolás) y dejar que el job retome;
los 3.672 pendientes se analizan bajo el tope diario de 0,50 USD en varios días. (b) Además, que el
ledger y el vigía distingan «0 analizados con error» de «0 analizados sin pendientes» (un cambio en
`mki_noticias.py` y en `chequear_noticias`, con test): hoy un fallo de crédito es invisible por
Telegram. (c) Nada. **No se eligió nada.** Este es el hallazgo con más días acumulados de la corrida:
22 días sin análisis sin que ninguna alarma lo dijera.

---

---

## 75. §62 después del código: la política de retención y el parche E0.3 NO APLICADO, con una bifurcación que el acta §90.6 no vio (corrida 15)

**Lo firmado (§90.6).** Opciones (a) y (d) de §62, con la política de retención escrita antes de cualquier
código; aplicarlo exige un acta posterior con la política a la vista, un cambio por noche al sellador.

**Lo entregado.** `GEMELO/propuestas/parches/politica_evidencia_no_verificable.md` (la política, escrita a
las 22:32 antes del parche) y `sello_no_verificable.diff` + `sello_no_verificable.md` (el parche, 1.250
líneas de diff sobre `dinero/sello_dinero.py` y `tests/test_sello_dinero.py`, 50 tests del sellador en
verde en el worktree, test de reproducción del 28-sep rojo en HEAD por su propia aserción). Dictamen del
`auditor-lookahead` en `dictamen_15/auditor_parche_sello.md`. **`dinero/sello_dinero.py` del árbol real no
cambió** (sha256 `480fbdc9…`, el de HEAD).

**La bifurcación, HALLAZGO leído del código.** La opción (a) tal como está firmada («`sello_previo()`
distingue estados; una fecha cuyas únicas filas son `no_verificable_timing` cuenta como no sellada; las
filas viejas se conservan») **no se puede implementar**: `sellos_dinero` declara
`UNIQUE (fecha_insumo, ticker, juego)`, y las 33 filas no verificables y las 33 buenas de una misma fecha
no pueden convivir en esa tabla. Dos caminos:
- **M, migrar el esquema**: cambiar la restricción exige crear la tabla de nuevo, copiar las filas y borrar la
  vieja, con los disparadores de inmutabilidad levantados mientras dura. Reescribe físicamente todas las filas
  selladas. No se implementó.
- **T, tabla aparte** (lo que hace el parche): un disparo con timing roto no escribe en `sellos_dinero`; sus
  filas van a `intentos_no_verificables` (mismas 35 columnas, misma `UNIQUE`, mismos disparadores, creada con
  `IF NOT EXISTS`, aditiva) y su evidencia a `ext_<fecha>.no_verificable.csv` + meta con `cupo_canonico:
  false`; el nombre canónico queda libre y el disparo de las 23:30 sella como cualquier otro. Con T, la (a)
  firmada se cumple por otro mecanismo y `sello_previo()` no necesita distinguir estados para ninguna fecha
  nueva; para el 28-sep no serviría igual (la `UNIQUE`), y esa sesión sigue perdida.

**Cuatro decisiones del implementador dentro de T, declaradas para el acta que lo aplique:** (1) evidencia
congelada con nombre canónico y timing roto al sellar (apertura cruzada entre las dos lecturas del reloj, o
`--sin-red` sobre un canónico nunca sellado): **rechazo** sin escribir filas (`rechazado_evidencia_canonica`),
porque una fila de intentos citando un canónico rompe el invariante 5.2 de la política; alternativa: que
`sellar` copie el contenido al par `.no_verificable` (escritura nueva desde `sellar`). (2) Un segundo intento
no verificable con el MISMO sha deja fila en `divergencias_sello` (el sello con el mismo sha sigue siendo
`ya_sellada` sin fila): asimetría declarada. (3) Dos relojes siguen existiendo en `main()`. (4)
`VERSION_SELLO` pasa a `E0.3` y `sellador_sha256` cambia en las filas nuevas (no es reescritura).

**Dictamen del `auditor-lookahead` (`dictamen_15/auditor_parche_sello.md`): APLICABLE CON EXIGENCIAS.**
Ninguna fuga temporal; dos fugas de auditabilidad: (F1, BLOQUEANTE) la rama de rechazo de la decisión (1)
no dejaba rastro en ninguna tabla, y con los dos relojes de `main()` es alcanzable (ya se midió una brecha
de 44 min el 6-ago); (F2) un `.no_verificable.csv` congelado por un proceso que murió antes de sellar queda
citado por nadie. **Plegadas al parche por el implementador antes del cierre de la corrida** (B1: el rechazo
deja fila en `divergencias_sello`; R2, R3, R5; y R4: un segundo intento con el mismo sha devuelve
`ya_intentada` sin fila, con la política §2.4 enmendada). **Quedan para el acta que lo aplique:** B2 (un
intento no verificable tiene que ser visible fuera del log: `estado()` con `ultimo_intento`, la API sirviendo
`intentos_no_verificables` y `ultimo_intento` dentro de `E0`, y `api/CONTRATO.md` enmendado antes; no consume
el presupuesto de un cambio por noche al sellador) y B3 (el acta escribe que **sustituye** el mecanismo de
§90.6 (a), no que lo implementa: «`sello_previo()` NO distingue estados y no hace falta que lo haga; el efecto
firmado se cumple; el mecanismo es otro; el corte de método es `VERSION_SELLO = E0.3`»). Zona ciega
declarada por el auditor y no probada: dos instancias concurrentes del sellador entre `congelar` y `sellar`.

**Qué falta para aplicarlo.** Un acta que elija T o M (o ninguno), fije el corte de método (fecha y hora de
aplicación), resuelva B2 y escriba B3; la aplicación con `git apply` sobre HEAD limpio, fuera de las 23:30
NY, y la suite del sellador después. La primera noche: la tabla nueva con 0 filas y `sellos_dinero` +33;
nace `data/backups/sello_dinero_no_verificables.csv` vacío con cabecera. **No se eligió nada.**

---

## 76. El README después de §90.3: tres frases que la máquina no sostiene hoy, y a qué vista remitir (corrida 15)

**Lo aplicado** (§90.3, §90.4, §88.5) está en la bitácora 15, sección 3, y en `dictamen_15/informe_bloque2.md`.
Al aplicarlo, el implementador verificó frase por frase la sección «Execution rail (paper only)» y dejó
tres cosas sin tocar porque no las firmó ningún acta:

1. **`/salud` no muestra el riel de dinero.** El acta §90.3 pide que la página remita «al CSV versionado y a
   `/salud`»; `/salud` (`api/main.py:348-420`, `Salud.tsx`) muestra los cinco jobs, la descarga sellada, las
   verificaciones, el presupuesto de IA y los tamaños de las bases. El estado de E0 lo sirve
   `/api/dinero/sellos` y lo muestra la vista **`/sellos`**. La mención a `/salud` se quitó (manda la máquina).
   **Opciones:** (a) remitir a `/sellos`; (b) dejar sólo el CSV. Errata del acta §90.3 en cualquiera de las dos.
2. **E1: «No practice account and no gateway exist yet».** El acta §91.9 dice «E1 (licencia del `ibapi` por
   leer y usuario de práctica por activar)» y §90.9 «cuenta de IBKR aprobada». La frase puede estar vencida a
   medias; sólo Nicolás sabe el estado de la cuenta. **Opciones:** (a) dejarla hasta que E1 arranque; (b)
   reescribirla con el estado real, firmado.
3. **E0: «every trading night the machine emits and seals»**: la sesión del 25-sep no tiene filas (suspensión)
   y la del 28 quedó `no_verificable_timing`. «Every» dice más que el registro. **Opciones:** (a) «on trading
   nights the machine is awake»; (b) dejarla y aceptar la imprecisión. El texto viene del encargo 15 literal.

También: `GEMELO/resultados/tesis.md:161` sigue diciendo «59× la muestra» (fuera de los archivos del bloque).
**No se eligió nada.**
