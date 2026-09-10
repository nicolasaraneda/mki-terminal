# Lo que espera tu firma

> **Actualizado el 8-sep-2026 (corrida 11).** Los seis ítems firmados en el acta §82
> (§45, §41, §55/§8, §42, §26 y 2a-ter/§3) salieron de la cola y quedaron como stubs con
> referencia a su acta; lo que sigue esperando no se tocó. **Firmado no es ejecutado:**
> la sección de abajo dice qué te queda a vos de cada firma.

## Firmado en §82, pendiente de ejecución por Nicolás

| Firma | Qué falta, y de quién es |
|---|---|
| §82.2 (§26, §1) | **Aplicar el parche `snapshot140.diff` junto con el guardia `guardia_ancla_temporal.diff`** (§49), en el mismo acto, con bump de `PLATAFORMA_VERSION`. Los dos aplican juntos sobre copias (`tests/test_parche_guardia_ancla_temporal.py`). El conteo de la parte (d) está hecho: **0 filas** pasaron por la rama del `except` (bitácora 11, bloque 6). |
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
**§17 arriba y `cola_decisiones.md` §18 citan «potencia 0,36 [0,34, 0,37]»
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

## 43. El período de M2, que hoy no se puede leer (cierre de la corrida 10) — FIRMADO el 8-sep (§84.4.5) y declarado NO APLICABLE el 9-sep: vuelve con la pregunta exacta

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
dispararse antes de empezar» citando el 14 % a 43 %, que está medido sobre **156
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

## 51. Qué señal sella E0, y si las filas de la sonda cuentan para N (corrida 12, 9-sep-2026)

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

## 52. La ventana para fijar el monto de E2 «sin mirar resultados» se cerró con la primera fila (corrida 12)

La regla de aporte 5.4 dice que el monto se fija ANTES de conocer el resultado de E0 y E1. El
§84.4.7 decidió no fijarlo en la corrida 12, y la corrida 12 selló la primera fila. Desde el
9-sep-2026 cualquier monto que se fije se fija sabiendo algo de E0 (aunque sea que la maquinaria
anduvo). **Qué hay que decidir:** fijarlo ahora con esa declaración, o reescribir la regla 5.4
para que el monto se fije antes de E2 y no antes de E0 (con la razón escrita). Ninguna de las dos
es cosmética: la primera es un grado de libertad declarado; la segunda es una enmienda a una regla
propuesta. **Recomendación:** ninguna; es tuya.

## 53. Instalar el timer del sellador E0 (`GEMELO/propuestas/systemd/mki-sello-dinero.{service,timer}`)

`Mon..Fri 21:00 America/Santiago`, argumentado en el archivo (fuera de la ventana 17:50–20:30; ≥ 3 h
después del cierre de NYSE todo el año; ≥ 12 h antes de la apertura objetivo). **Instalar un timer es
acto tuyo.** Hasta entonces el sello se corre a mano (`python -m dinero.sello_dinero --sellar`) o no
se corre, y los días sin sello no cuentan para N. Costo de postergarlo: cada noche sin timer es una
sesión menos hacia N = 40.

## 54. `ibapi`: la dependencia autorizada (D-C bis) no es instalable con licencia verificada desde PyPI

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

## 57. Confirmar la definición operativa de «sesión que cuenta para N = 40» (una línea)

N = 40 lo firmaste (§84.4.7); la definición de qué sesión cuenta la escribió la corrida 12
(`regla_aporte_y_dimensionamiento.md` §5-bis, `dinero/sello_dinero.py`): sólo una fila `pendiente`
(available_at < timestamp_utc < apertura objetivo, por calendario) de un día con sesión en Nueva
York, con el insumo en la sesión inmediatamente anterior a la objetivo y COMPLETO (33 de 33 con
cierre). Días sin sesión, sellos tardíos e insumos incompletos o desactualizados se sellan igual y no
cuentan. Es la definición conservadora; es una definición de agente sobre una cifra tuya, y por eso
se confirma con una línea o se cambia (y cambiarla reinicia el contador).
