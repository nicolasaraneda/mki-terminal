# Bitácora 04 — cuarta corrida autónoma, 31-ago/1-sep-2026

Continuación de `bitacora_nocturna.md`, `bitacora_02.md` y `bitacora_03.md`.
Una línea por hito, hora UTC.

**Lo que cambió respecto de la corrida anterior:** Nicolás tomó tres de las
decisiones que estaban bloqueando. **α = 0.05 nominal con la banda
[0.046, 0.079] publicada como limitación declarada** (opción 2, no la que
yo había recomendado: el argumento es que declarar α = 0.10 para que el
número sea "verdadero" sería absorber la incertidumbre en una cifra más
redonda, que es lo contrario del estilo de la casa — el proyecto publica
su incertidumbre en todo lo demás). **Placa: Digilent Arty A7-100T.** Y la
**arquitectura de dos modelos**: general en la A7, HFT más adelante en una
KR260.

**Regla nueva de la casa, ganada a golpes en la corrida anterior y que
gobierna toda esta:** una verificación que usa el mismo mecanismo que
produjo la cifra NO es una verificación. Toda cifra crítica se valida
contra una vara independiente, de otra familia de método. Si esa vara no
existe, se dice, en vez de fabricar una que se le parezca.

- 22:35 UTC — Arranque. Árbol limpio salvo los 8 CSV del job de las 18:15,
  que no son de ninguna tanda. `HEAD=3acb7b1`, 7 commits sin pushear.
  Despachado `orientador` con siete preguntas: el texto congelado de V6,
  los parámetros para derivar el MDE, las frases de `RTL.md`/`fpga.md` que
  presentan la FPGA como motor de backtesting, las dos afirmaciones
  refutadas con su cita original, el origen del 0.1849, el estado real de
  las piezas de réplica, y el ritmo de acumulación actualizado.
- 22:40 UTC — Despachado el Frente B completo (Vivado, síntesis para la
  XC7A100TCSG324-1, presupuesto y márgenes) a un `general-purpose`, con la
  advertencia de unidades del B0 explícita en el encargo: las 1.545
  "celdas" del iCE40 y las 101.440 del A7-100T no son la misma unidad, y
  compararlas crudas sería el error que la regla nueva busca evitar.
- 22:55 UTC — **Frente D resuelto, y el hallazgo es mejor que "el README
  está mal": ninguna de las dos cifras lo está.** El 0.1849 es el χ² de
  McNemar **con corrección de continuidad** (0.184898) y el 0.1847 es la
  **binomial exacta** (0.184683). Mismo par (b=72, c=56), mismo n, métodos
  distintos. No hay redondeo ni arrastre de por medio.
  - **Corrijo lo que escribí en la corrida anterior:** en `DECISIONES.md`
    §47 dije que el 0.1849 "se arrastró desde la medición de n=240". Es
    falso. Va errata fechada, porque §47 ya está commiteada en `09054cb`.
  - Verificado contra **varas independientes**, según la regla nueva: la
    binomial exacta recomputada con `fractions.Fraction` —aritmética
    racional exacta, otra familia que la suma en punto flotante del
    módulo— da idéntico; el χ² por `erfc` y por `2·(1−Φ(√x))`, dos caminos
    sin código compartido, dan idéntico. No se instaló `scipy`: no hacía
    falta y habría sido fabricar una tercera vara.
  - **No es una cifra, son cuatro, y es una regla escrita rota.** Los tres
    p de la ventana sellada (0.1158 / 0.2542 / 0.1849) y el de la línea
    base congelada (0.4633) salen todos de `backtest/linea_base.py:126`,
    que **reimplementa McNemar a mano** cuando `.claude/rules/backtest.md`
    :26-27 dice literal "No reimplementes Wilson, McNemar, DSR ni CRPS a
    mano". Atenuante que corresponde: `linea_base.py` es del 25-ago y la
    regla del 30-ago — la regla llegó después y nadie volvió a mirar el
    código que ya estaba.
  - **Y hay un choque entre dos reglas del propio proyecto**, que es lo
    que impide arreglarlo solo: `GEMELO/DISEÑO.md` §2.8 **congeló**
    `p = 0.4633` en un pre-registro. Migrar al árbitro la mueve a 0.4635,
    y un pre-registro congelado no se toca. Tres opciones escritas con su
    costo en `GEMELO/resultados/mcnemar_dos_rutas.md`; **recomiendo la A**
    (declarar el método al lado de cada p, no mover ningún dígito):
    ninguna conclusión cambia, el mayor Δ es 0.0003, y lo que falta es una
    palabra, no un número. **La decisión es de Nicolás.**
- 23:05 UTC — **Frente C: la premisa del encargo no se sostiene, y lo digo
  en vez de fabricar la corrección.** El encargo pedía corregir el encuadre
  de `RTL.md`/`fpga.md` porque "la A7-100T NO es un motor de backtesting".
  Verifiqué el texto: **ese encuadre equivocado no existe**. `RTL.md:16`
  dice "validado por backtest" —el backtest valida al RTL, no al revés—,
  las tres menciones de "backtest" en los dos archivos son de esa forma, y
  `fpga.md:24-26` dice literal que "la ventaja que el hardware ofrece no es
  'más rápido'... es **determinismo**". `fpga.md:50-51` incluso aclara que
  la comparación de throughput contra software "no es 'el hardware gana'
  por default; hay que medirlo". Fabricar una corrección para cumplir el
  encargo habría sido exactamente lo contrario de la regla nueva.
  - Lo que sí es real: las **dos afirmaciones refutadas**. Despachado
    `escriba-decisiones`, que las corrigió en su sitio en `RTL.md` con nota
    de errata fechada (la tolerancia de 0,00188 pp, inalcanzable, medido
    0,00474; y el "100% de coincidencia", falso: 2 de 181). El hallazgo
    conceptual quedó escrito: **lo discreto es MÁS frágil en la frontera,
    no inmune** — lo contrario de lo que razonaba el documento original.
- 23:10 UTC — **Frente E: `replica_una_pagina.md`.** Una página: qué se
  activa, qué cambia el día 1 y el mes 1, qué se rompe y cómo se vuelve
  atrás, cuánto tiempo cuesta, y la única regla que necesita firma (quién
  gana ante divergencia) con sus tres opciones y la consecuencia de cada
  una. **El dato incómodo que había que poner adelante:** la comparación
  diaria **no está automatizada** — sin construir un séptimo job, alguien
  tiene que acordarse de correrla todos los días, que es la misma clase de
  punto débil que el mecanismo existe para eliminar.
- 23:30 UTC — **Frente A1: el MDE, derivado de V6. Y el insumo estaba
  contaminado.**
  - **Hallazgo grande, y no era el que buscaba: 30 de 256 filas (11,7%)
    apuntan a la MISMA sesión objetivo que otra.** Quince pares sobre cinco
    sesiones (31-jul, 5-ago, 12-ago, 18-ago): dos fechas de emisión
    consecutivas cuyo objetivo es la misma sesión porque la intermedia no
    existió. Comparten `gap_pct` y `retorno_real_pct` idénticos, y **entre
    ellas están los movimientos más grandes de toda la ventana** (+29,95%,
    +26,81%, +17,52%). Es la misma familia que la pregunta pendiente de
    §33.8 sobre las 8 filas del 29-jul, pero **más grande de lo que esa
    pregunta suponía**.
  - E|r| con duplicados da 4,02%; deduplicado 3,72%. Bajé el precio crudo
    de los ocho tickers y recomputé el retorno diario desde cero: da
    **3,7594%**.
    **[RETRACTADO a las 00:35 — acá escribí que eso era "otra familia de
    método" y que "confirma la deduplicada y descarta la contaminada". Las
    dos cosas son falsas: es el mismo proveedor, el mismo campo y la misma
    fórmula, con desviación media de 0,0001 pp emparejada. Era una
    reproducción, no una vara independiente. Y la diferencia con 4,02% es
    sobre todo que promedia otra población. Escribí "la regla nueva
    funcionó" en la misma línea en que la estaba rompiendo.]**
  - **V6 no puede fijar el MDE. (De las dos razones que escribí acá, la
    segunda quedó RETRACTADA a las 00:35; la primera se sostiene sola.)** (1) **SMH cayó
    5,18%** en la ventana, así que la tasa de acierto necesaria para
    superarlo neto de 25 pb es **54,9% — por debajo del 59,7% de la
    baseline**: en esta ventana la baseline sola aprueba V6 y V6 no exige
    nada del modelo. Un MDE que depende de si el benchmark subió o bajó no
    es un MDE. (2) El puente de la economía a puntos de acierto exige
    simetría de magnitudes, y los datos la refutan **por 3,64×**.
  - **[RETRACTADO a las 00:35 — ver esa entrada. La razón de magnitudes
    tiene IC95 [0,89, 2,16], que incluye 1,0: la simetría NO está
    refutada. Lo de abajo queda como registro de lo que creí entonces.]**
    **La causa de (2) sería un hallazgo por derecho propio:** en las filas
    donde el modelo dice BAJA, los aciertos tienen |r| = 5,162% y los
    errores 3,870% — razón **1,33×**. Cuando acierta, el movimiento es más
    grande. **La ventaja económica viene de la MAGNITUD, no del signo**, y
    la tasa de acierto direccional en esas filas es 53,9% Wilson [45,3,
    62,3], que incluye 50%. Es coherente con lo ya publicado (MAE 2,98 vs
    3,33) y tiene una consecuencia dura: **este diseño mide dirección, y
    el valor económico no está ahí.**
  - **Lo que sí se deriva:** δ_min = f·2c/E|r|. Da **2,85 / 7,13 / 14,26
    pp** a 10/25/50 pb bajo magnitudes simétricas, y 0,78 / 1,96 / 3,92 con
    la asimetría observada. **Propuesto para firma: 7 pp**, el extremo
    conservador — diseñar para 2 pp apuesta a que la ventaja de magnitud
    persiste, y eso nunca se probó de forma prospectiva.
  - **El supuesto que manda NO es E|r|** (rango 6,6–8,2 pp) sino el de
    simetría de magnitudes (rango 2–7 pp).
  - **La tensión, dicha con todas las letras:** 7 pp mueve la respuesta de
    2027-07-14 a **2028-06-10**, y el diseño ya tiene escrito que un plan
    de años tiene alta probabilidad de romperse antes de completarse. Se
    puede firmar 7 pp y aceptar 2028, o firmar 10 pp declarando que es
    calendario y no derivación. **Lo que no se puede es firmar 10 pp
    diciendo que sale de V6.**
- 23:45 UTC — **Frente A2/A3.** α = 0.05 congelado con la banda en el
  cuerpo, el **estimador de reestimación declarado ahora** (`ac1` de lag 1
  sobre `d_j`, EE de Bartlett 1/√m, se reestima cuando `2·EE < 0.10`, o sea
  m ≥ 400 fechas — que **con el ritmo actual son ~8 años, y se dice para
  que nadie lea "se reestimará" como si fuera pronto**). Fechas recomputadas
  con el ritmo real (6,56 filas/día hábil, y 6,18 si se deduplican).
  **Acta de congelamiento** con fecha, commit, α, umbrales, estadístico,
  población, pasivo y ritmo. Y el candado que lo hace exigible: `mirada.py`
  tiene `MDE_FIRMADO = None` y **se niega a computar** — las fronteras, el
  estadístico y la futilidad **no dependen del MDE** y quedan congelados
  igual. 43 tests del secuencial, 372 en la suite completa.
  Despachado el cuarto dictamen, que es la condición del congelamiento.
- 00:20 UTC — **Frente B completo, y es el frente más productivo de la
  tanda.** Entregables: `GEMELO/MICRO/SINTESIS_A7.md`,
  `GEMELO/MICRO/PROYECTO_RAMO.md`, `micro/TOOLCHAIN.md` §3.1, y RTL nuevo.
  - **B0, las unidades:** verificado contra DS180 v2.6.1 — el A7-100T tiene
    **15.850 slices = 63.400 LUT6 y 126.800 FF**; los 101.440 son cifra de
    marketing. La vara independiente del factor 1,6 no fue la memoria:
    Logic Cells / (Slices×4) da **1,600 exacto en los ocho dispositivos
    Artix-7**. Comparar 1.545 contra 101.440 falla dos veces.
  - **B2, el cuello:** **BRAM = 0** en las cuatro configuraciones. Para la
    carga real **no topa ninguno de los tres** candidatos — el cuello es la
    tasa de llegada de los datos: el pipeline consume 224 B por sesión, que
    la DDR3L entrega en 168 ns, y saturarla exigiría 47,6 M msg/s contra
    los 8 por día que emite la plataforma. Para "cuánto diseño entra", el
    **DSP48E1 topa primero, a 240 tickers**. Y la historia sellada entera
    es **0,85% de la BRAM**: la DDR3L es prescindible.
  - **B3, y la mejor compra es gratis:** 27 de los 32 ciclos eran la
    ingesta byte a byte. La ingesta ancha baja la latencia de **32 a 11
    ciclos** (4 B/ciclo) y a 5 (28 B/ciclo), con **181/181 bit a bit en los
    seis anchos** y B=1 reproduciendo 32 como control — y el área **baja**
    (108 → 93 LUT6). También bajaba en el iCE40: **no estaba bloqueado por
    espacio, sólo nadie lo había preguntado.** El 4.6.0 completo **cabe**
    (≈864 LUT6, 1,4%), y esa misma pieza es **309% de la Go Board entera**.
    Subir el punto fijo **no compra nada**: contra float64 el error cae
    250×, pero contra la fila sellada se estanca, porque la base guarda con
    2 decimales — el redondeo del sello es más grueso que el LSB de Q8.8.
  - **Bloqueo honesto:** Vivado no se pudo instalar, y **no por disco, RAM,
    root ni licencia** (el tier BASIC cubre toda la serie 7 y cuesta $0).
    Todos los instaladores exigen cuenta AMD y formulario de control de
    exportación: **es un acto de identidad de Nicolás, de la misma clase
    que pushear.** Sin place & route no hay Fmax, utilización de slices ni
    bitstream, y todo eso queda marcado como estimación.
- 00:35 UTC — **CUARTO RECHAZO del diseño secuencial. No se congela, y no
  hay v6:** la instrucción era registrar y parar. Es el rechazo más duro de
  los cuatro **porque dos de los tres defectos nuevos son míos y de hoy**.
  - **El descalificante, y la ironía duele:** la v5 descubrió la
    contaminación de los 30 duplicados y **corrigió el parámetro pero no el
    estimador**. `mde_desde_v6.py` deduplica; `mirada.py` no, y agrupa por
    fecha de emisión — los pares tienen fechas distintas y resultado
    idéntico, así que caen en clústeres distintos y V̂ es ciega justo a la
    dependencia que acabo de descubrir. Y dejé abierta la elección de qué
    fila conservar, que vale **la diferencia entre veredictos opuestos**:
    `keep="first"` → p = 0,1847; `keep="last"` → **p = 0,0323**. Un
    argumento de una palabra, no declarado, cruza el umbral. Descubrir la
    contaminación estuvo bien; congelar antes de decidir qué hacer con
    ella, no.
  - **Mío, y es el que más me importa:** la "razón 2" de §A3.1.b —que los
    datos refutaban la simetría de magnitudes por 3,64×— **no tenía
    intervalo, y muere cuando se le pone**. Lo verifiqué con el módulo
    árbitro: la razón de magnitudes da IC95 **[0,89, 2,16]**, que incluye
    1,0; E[r|baja] incluye cero y cubre −2c; y el 3,64× **no tiene
    intervalo finito** porque su denominador (2q−1) no se distingue de
    cero. Publiqué un punto indistinguible del nulo como hallazgo, **en la
    sección escrita para prevenir exactamente eso**, y lo usé para rechazar
    un modelo. El documento imprimía la Wilson honesta de q una línea antes
    y dividía por (2q−1) a la siguiente. Retractado en su sitio.
  - **Mío también: la "vara independiente" no era independiente.** Mismo
    proveedor, mismo campo, misma fórmula; desviación máxima 0,0207 pp y
    media 0,0001 pp sobre 234 filas emparejadas. Era una reproducción. Y la
    razón de que diera 3,7594 en vez de 4,0231 no era descartar la
    contaminación sino **promediar otra población** (319 pares contra 246).
    **La regla nueva se cobró una pieza el mismo día en que se escribió, y
    la pieza era mía.** Retractado.
  - **Reproducibilidad:** el documento dejó de reproducir desde sus propios
    scripts el día del congelamiento y se contradecía a sí mismo (34 vs 35
    fechas). Causa raíz: `mde_desde_v6.py` escribe su propio SQL en vez de
    usar `linea_base.cargar(hasta_sello=...)`, o sea **sin ancla
    temporal** — la misma dependencia del reloj que el WS5 diagnosticó y
    arregló el 30-ago, reintroducida en el archivo más nuevo.
  - **Y el 7 pp queda retirado:** lo derivé en la escala del retorno de
    sesión, pero el endpoint congelado es `acierto_gap`. En la escala
    correcta es **8,96 pp con IC95 [6,67, 11,32]**.
  - Corregidos sólo los errores factuales baratos que no son decisiones de
    diseño: los comentarios rancios (`max(bloque 1, bloque 5)` → `(1,5,10)`),
    el ritmo (6,5 → 256/39 con la variante deduplicada declarada al lado) y
    la contradicción 34/35. **No intenté una v6.**
  - La frase del dictamen que resume el estado: *un pre-registro que no
    reproduce el día que se firma no está congelado, está fechado.*
- 00:55 UTC — Actas **§52 a §56** escritas: la regla de verificación
  independiente, α = 0.05 con su banda, la placa y la arquitectura de dos
  modelos, el McNemar de dos rutas con la errata sobre §47, y el cuarto
  rechazo. El `escriba` reportó una salvedad correcta: **las
  especificaciones de la KR260 no están en ningún documento del repo**, así
  que las dejó atribuidas a Nicolás en esta corrida y no a una fuente
  documental que no existe. `cola_decisiones.md` reordenada y `ESTADO.md`
  regenerado. 372 tests en verde.

- 01:20 UTC — **El guardián RECHAZÓ la tanda, con dos exigencias, y las
  dos son correctas.**
  - **La primera es la que enseña:** las retractaciones estaban en prosa
    en el `DISEÑO.md` pero **no habían llegado al artefacto**.
    `mde_desde_v6.py` seguía imprimiendo "vara INDEPENDIENTE", "confirma
    la deduplicada, descarta la contaminada", "los datos la refutan por
    3.64×" y "PROPUESTO PARA FIRMA: MDE = 7 pp" — todas retractadas en el
    documento y todas vivas en el ejecutable que las genera. Dicho por el
    guardián: *"la retractación en prosa es ejemplar [...] pero el
    ejecutable que genera esos números reimprime el estimador puntual sin
    intervalo — exactamente la infracción que la retractación describe. Es
    la única pieza donde la retractación es cosmética, y es la que
    cuenta."* Corregido: el docstring lleva la retractación entera,
    `e_abs_independiente()` pasó a llamarse **`e_abs_reproduccion()`** con
    la medición que prueba que no es independiente, y las cuatro secciones
    de salida ahora imprimen la retractación con sus intervalos.
  - **La segunda me deja peor:** al regenerar `ESTADO.md` **borré la
    "errata pendiente de registrar"** de `MKI_MODO` sin registrarla en
    ninguna parte. Un recordatorio de errata que desaparece sin
    convertirse en errata es peor que no haberlo anotado: deja el repo
    afirmando algo falso y sin rastro de que alguien lo supo. Escrita como
    **§57**, con su alcance: `CLAUDE.md` repite la afirmación y **no se
    corrigió a propósito** —gobierna cómo trabaja el agente y esa edición
    la tiene que ver Nicolás—, así que quedó como §11 de la cola.
  - Regla que sale de esto y vale más que el caso: **una errata pendiente
    sólo se saca de `ESTADO.md` escribiéndola en `DECISIONES.md` en el
    mismo movimiento.** `ESTADO.md` se regenera; lo que vive sólo ahí
    desaparece en el próximo cierre.
  - Atendidas también sus dos observaciones: marcadores de retractación en
    la bitácora sobre las cifras muertas, y `ESTADO.md` declarado como
    archivo de la tanda. Barrido de `3.64` y "vara independiente":
    ninguna ocurrencia viva fuera de su contexto de retractación.
    Re-despachado el dictamen.

- 01:45 UTC — **Segundo dictamen: OBSERVADO, no rechazado.** Las dos
  exigencias verificadas una por una como cumplidas. Quedaban tres
  correcciones de texto, y una era sustantiva:
  - Dos títulos que seguían afirmando lo que su propio cuerpo retractaba
    24 líneas más abajo (`A3.1.a ...y la vara independiente lo mostró`,
    `A3.1.b ...hay dos razones medidas`). Texto sin commitear: corregido
    en su sitio.
  - **La sustantiva, y es del mismo linaje que todo lo demás de esta
    corrida:** el "~7,96 / ~8,96 pp" del MDE en la escala del endpoint
    estaba **cableado como string en cinco artefactos, sin computarlo
    ningún script y sin intervalo** — y entraba a `DECISIONES.md`, que es
    permanente, en la corrida cuya lección es exactamente que un estimador
    puntual sin intervalo no se publica. Contradecía además el propio
    docstring del script ("toda cifra de §A3.1 sale de correr este
    archivo"). **Ahora lo computa `mde_desde_v6.py`** con bootstrap de
    bloques del módulo árbitro: **8,96 pp, IC95 [6,67, 11,32]**, sobre
    E|gap| = 2,9650% [2,3456, 3,9813]. Lo que reemplaza al 7 pp es un
    rango, no un punto.
  - El guardián dejó además un **NO VERIFICADO que hay que registrar**:
    `SINTESIS_A7.md`:538-540 afirma "dos métodos distintos, mismo número:
    eso es la vara independiente" sobre los 0,00474 pp, y **nadie
    comprobó si el arnés de `SINTESIS.md` §5 y `medir_ancho_error.py` son
    familias de método realmente distintas o el mismo álgebra de
    cuantización recorrida dos veces**. Con la regla §52 puesta, esa frase
    merece una medición explícita antes de sostenerse. Queda anotado, sin
    tocar: viene en verde de la corrida anterior y no se reabre de paso.

---

## Handoff

**Qué quedó hecho.** Dos decisiones de Nicolás quedaron ejecutadas y con
acta (α = 0.05 con su banda; placa A7-100T y arquitectura de dos modelos).
El Frente B midió la placa de verdad y encontró que **la mejor mejora
disponible es gratis** —la ingesta ancha baja la latencia de 32 a 11
ciclos con el área bajando— y que el cuello no es ninguno de los tres
candidatos obvios. El McNemar quedó resuelto: **ninguna de las dos cifras
está mal, son dos tests**, y lo que hay debajo es una regla escrita rota
con su atenuante. La réplica tiene su página de una carilla para firmar en
cinco minutos. Las dos afirmaciones refutadas de `RTL.md` tienen errata.

**Qué quedó a medias, y a propósito.** El pre-registro secuencial **no se
congeló**: cuarto rechazo, y la instrucción era registrar y parar. No hay
v6. Lo que lo tumbó fue, sobre todo, **un defecto que introduje al
corregir otro**: descubrí que el 11,7% de las filas están duplicadas,
corregí el parámetro y no el estimador, y dejé abierta una elección de una
palabra que mueve el veredicto de p = 0,18 a p = 0,03. Descubrir la
contaminación estuvo bien; congelar antes de decidir qué hacer con ella,
no.

**El siguiente paso concreto.** Nicolás revisa el diff y pushea. Después,
por costo de postergar: **firmar la regla de deduplicación** —es nueva,
urgente, y mientras esté abierta cualquier análisis de la ventana sellada
tiene un grado de libertad sin declarar—, **firmar la activación de la
réplica**, y **crear la cuenta AMD**, que es lo único que separa al
proyecto del place & route y por lo tanto de todos los hitos del ramo.

**Lo que la corrida enseñó.** La regla nueva de la casa se cobró una pieza
el mismo día en que se escribió, y la pieza era mía: declaré haber
validado E|r| contra una "vara independiente" que era el mismo proveedor,
el mismo campo y la misma fórmula recorrida de nuevo. Y en la misma
sección publiqué un cociente indistinguible del nulo como si fuera un
hallazgo, imprimiendo el intervalo honesto una línea antes y dividiendo
por él a la siguiente. **Las dos veces el error fue el mismo: querer que
el dato dijera algo, y dejar de preguntarle si podía decirlo.** Por eso la
regla se escribe, y por eso el adversario se despacha aunque uno crea que
esta vez sí.
