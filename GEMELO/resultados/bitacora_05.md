# Bitácora 05 — quinta corrida autónoma, 1-sep-2026

Continuación de `bitacora_nocturna.md`, `02`, `03` y `04`. Una línea por
hito, **con hora local (Chile, UTC−4)**.

## Las firmas: una llegó, la otra no

**El encargo traía dos ranuras y las dos venían con el texto de plantilla
literal**, así que arranqué tratando a las dos como NO firmadas. Un
marcador de plantilla no es una firma, y leerlo como si lo fuera sería
exactamente la clase de licencia que este proyecto documenta como error.

**A los pocos minutos Nicolás mandó las firmas de verdad**, y confirmó las
dos lecturas:

- **Etapa 5.1: AUTORIZADA.** Se ejecuta el veredicto B0–B5 con los
  criterios congelados. Con una condición explícita suya que fija el orden
  del trabajo: *"Contá TODOS los intentos [...] reconstruidos desde las
  actas y **declarados antes de calcular nada**"*. Y: *"el veredicto se
  escribe con la misma firmeza si es negativo"*.
- **Deduplicación: NO firmada, y por una razón que mejora el encargo.**
  Textual: *"quiero el forense del origen del A1 antes de decidir qué es
  una fila"*. O sea: la regla no se elige entre consecuencias estadísticas
  sino a partir de qué produjo los duplicados. El Frente A ya estaba
  despachado exactamente así.

## Las tres reglas de la casa vigentes

1. Una verificación que usa el mismo mecanismo que produjo la cifra **no
   es una verificación**.
2. Una retractación en prosa **no es una retractación**: si el ejecutable
   sigue generando la cifra, no se retractó nada. **La corrección va al
   código primero.**
3. **Ningún estimador puntual sin intervalo**, y el intervalo se computa,
   no se estima de memoria.

## Hitos

- **01:32** — Arranque. `HEAD=d071821`, árbol limpio, 9 commits sin
  pushear. **Fuera de la ventana de sellado** (17:50-20:30 local), así que
  el trabajo pesado —matriz de bifurcaciones, backtest, síntesis, suite
  completa— entra ahora y no después de las 17:50.
- **01:33** — Despachado `orientador` con siete preguntas: los ejes de
  bifurcación documentados que todavía no conozco, el conteo de intentos
  para el DSR reconstruido desde las actas, el estado del arnés de
  backtest, qué se puede correr sobre la ventana larga, las seis
  condiciones candidatas, los tres documentos más citados, y qué logs de
  jobs existen para las fechas de los pares duplicados.
- **01:34** — **Frente A despachado a `integridad-datos`** (solo lectura,
  `mode=ro`): forense del origen par por par —¿misma fecha de emisión o
  distintas? ¿fila idéntica? ¿coinciden los `timestamp_utc`, que en dos
  sellados independientes nunca coinciden?—, cruce con los logs de los
  jobs y con `snapshots.origen`, y el chequeo grave de si se concentran en
  el bloque 15-23-jul. Más las **tres** ramas completas (`first`, `last`,
  sin deduplicar) con todas las cifras y sus intervalos.
- **01:35** — **Frente B despachado**: la matriz de bifurcaciones. Cinco
  ejes mínimos más los que encuentre documentados, cada celda con n,
  acierto, ventaja, McNemar, MAE y cobertura, y el cociente de celdas con
  p < 0,05 como resultado del frente. Código versionado en
  `GEMELO/bifurcaciones.py`, que es la lección de §45.
- **01:38** — **Frente C1 despachado con la autorización de la 5.1**, en
  tres fases de orden obligatorio: (1) reconstruir y **escribir en disco**
  el conteo de intentos antes de computar nada —si aparece uno más
  después, se agrega como corrección visible y no se reescribe el número—,
  (2) verificar el arnés punta a punta con un ensayo sobre subconjunto
  declarado, y sólo entonces (3) el veredicto, con cada baseline con su
  intervalo por bootstrap circular y el DSR con el N declarado.
- **01:40** — **Frente F despachado**: la suite de regresión epistémica,
  siete tests, uno por clase de error de las cinco corridas. Con dos
  condiciones que valen tanto como los tests: nombre en español diciendo
  qué error histórico previene y docstring con la fecha del caso real; y
  **si algo detecta un problema hoy —el de duplicados lo va a detectar—
  va `xfail` con razón explícita, no se ablanda para que pase.** Un test
  en verde que debería estar en rojo es peor que no tenerlo.
- **01:42** — **Frente E despachado**: implementar la ingesta ancha,
  confirmar los 11 ciclos y la baja de área, verificar que las 181 filas
  se siguen reproduciendo bit a bit, recalcular el techo de tickers, y dos
  variantes más del espacio de diseño con su costo medido. Más la errata
  de que la mejora también aplicaba a la Go Board — **con el foco puesto
  no en el iCE40 sino en por qué nadie preguntó**.
- **01:52** — **El orientador trajo algo que cambia el Frente C en
  caliente: el gatillo de la 5.1 NO está cumplido por ninguna de sus dos
  vías.** `backtest/DISEÑO.md`:226-233 lo congeló en el GATE B: (a) N≥150
  **Y un cambio de régimen del SOX observado**, o (b) tres meses desde el
  25-jul → **25-oct-2026**. Hoy N=261 cumple la primera mitad de (a), pero
  **no hay cambio de régimen**: `snapshots` tiene una sola etiqueta
  ("Alcista · vol alta", 38 filas) más 2 nulas. Y a la (b) le faltan ~54
  días.
  - **Casi meto la pata en mi propio chequeo**: mi primera consulta contó
    las 2 filas `NaN` como un régimen distinto y concluyó "cambio de
    régimen: SÍ". Es dato faltante, no otro régimen — el README ya lo dice
    ("1 sola etiqueta en 39 snapshots, la columna no tiene varianza"). Lo
    anoto porque es exactamente la clase de inferencia floja que las
    reglas de la casa existen para atajar, y esta vez la atajé yo.
  - **Por qué importa, y no es burocracia: V7 dice que el holdout se
    evalúa UNA SOLA VEZ** (`GEMELO/DISEÑO.md`:462). Es un recurso
    irreversible. Gastarlo con el gatillo sin cumplir lo quema para
    siempre.
  - **La instrucción de Nicolás contiene una contradicción que él casi
    seguro no conocía:** autorizó ejecutar el veredicto *"con los
    criterios congelados de `backtest/DISEÑO.md`, sin tocarlos"*, y **el
    gatillo ES uno de esos criterios**. Ejecutar hoy violaría el mismo
    documento que pidió respetar. No la resuelvo yo.
  - **Lo que hice:** mensaje al agente de C1 para que corra todo lo
    reversible —conteo declarado, arnés verificado, walk-forward completo
    con las seis baselines y sus intervalos, DSR con el N declarado— y
    **NO evalúe el holdout**. La corrida se sella por lo que es: veredicto
    completo con el gatillo no cumplido y el holdout intacto, dicho en la
    primera pantalla del `resumen.md` y no en una nota al pie. Así no se
    pierde el trabajo ni se gasta lo que no se puede recuperar, y la
    decisión —esperar al 25-oct o relevar la condición (a) por escrito—
    queda entera para Nicolás.
- **01:55** — Del orientador, para el conteo de intentos: el código
  (`GEMELO/relevo_asiatico.py`:76, con test que lo fija) sigue diciendo
  **25**, y la reconstrucción honesta desde las actas da **≥43**
  (`concentracion.md`:318-338, que declaró 25+7+3+8). Además
  `CONDICIONAL/DISEÑO.md` §7 declara subir "de 25 a 32" apoyándose en la
  base vieja, escrito en la misma corrida que encontró el 43. **La
  retractación de esa corrida fue sobre su conclusión, no sobre que los
  análisis se corrieron: por la regla del DSR cuentan igual.**
- **02:15** — **Frente A cerrado, y el forense dio vuelta la pregunta.**
  `dedup_opciones.md` escrito. Lo central: **los 30 duplicados no son un
  fenómeno, son dos, con orígenes distintos.**
  - **10 pares (31-jul y 5-ago): defecto de la ruta de sellado.**
    `snapshot.py`:140 calcula `sesion_objetivo` con `ahora_utc` —el reloj
    de pared, estampado en `:111`— en vez de con `available_at`. Si el
    sello cruza medianoche/01h UTC, salta a la sesión siguiente porque la
    asiática **ya abrió**. Verificado por mí en el código, no sólo
    reportado. Coincide con lo que la Etapa 5.0.1 ya había diagnosticado
    para el 29-jul y el 3-ago.
  - **5 pares (12-ago y 18-ago): feriados reales.** XTKS cerrado el
    11-ago, XKRX el 17-ago. **Ninguna anomalía de reloj: las dos
    emisiones están igualmente a tiempo, y ninguna es más legítima.**
  - **Por qué esto cambia la decisión de Nicolás:** una sola regla para
    los dos grupos sería arbitraria por construcción. Su instinto de
    pedir el origen antes de firmar era el correcto, y el forense lo
    justifica: en un grupo hay una fila fuera de especificación, en el
    otro no hay ninguna.
  - **El hecho que hay que mirar antes de firmar `keep="last"`**, medido
    y escrito como aritmética y no como sospecha: la fila **fresca nunca
    discrepa de la baseline** en estos 15 pares, mientras la **vieja
    discrepa 12 de 15 veces, 10 de ellas a favor de la baseline**.
    Descartar la vieja **retira selectivamente errores del modelo**. Ésa
    es la explicación mecánica de por qué esa rama da p = 0,032.
  - Verificado también que **ninguno de los 30 es una fila copiada** (el
    chequeo estructural de unicidad de `timestamp_utc` no tiene
    colisiones) y que **no se concentran en el bloque 15-23-jul**.
  - **Errata mía, corregida con fecha:** `DISEÑO.md` §A3.1.a decía "cinco
    sesiones" y son **cuatro**. Sin consecuencia sobre ninguna cifra, pero
    el documento ya estaba commiteado, así que va errata y no corrección
    silenciosa.
  - Lo que el forense **no** pudo determinar, y lo dice: la causa última
    del DarkWake, la exactitud de `exchange_calendars` contra fuente
    externa, y el dropout parcial del 17-ago. **Los logs de esas fechas ya
    rotaron y no existen.**
- **02:20** — El defecto de `snapshot.py` entra a la cola como **§1-bis**,
  arriba de casi todo, por una razón que lo distingue del resto: **los
  otros ítems son decisiones sobre datos que ya existen; éste sigue
  ocurriendo.** Cada sello que se atrase produce una fila más con la
  sesión objetivo equivocada. No lo toco —está en la ruta de sellado— y
  además su corrección crea por construcción un corte de método con fecha,
  que se declara antes y no se descubre después.
- **01:45** — Cinco frentes corriendo en paralelo más el orientador.
  Quedan D (MDE contra ventaja observada) y G (lo que espera firma), que
  dependen de los resultados de B y A, y C2 (la condicional sobre la
  ventana larga), que espera a que C1 libere el arnés.
- **02:40** — **Frente F cerrado: `tests/test_epistemico.py`, 14 tests, 12
  en verde y 2 en `xfail`.** Cinco noches de errores convertidos en
  memoria ejecutable.
  - **Los detectores no son tautológicos, y lo verifiqué:** cada uno
    heurístico trae una **contraprueba** que le inyecta el texto histórico
    original —la redacción real que se retractó el 31-ago— y comprueba que
    lo caza; y después le pone la corrección y comprueba que **se calla**.
    O sea que el detector distingue afirmar de retractar, no la mera
    presencia de las palabras. Es el mismo patrón que el proyecto ya usa
    en la prueba de causalidad, que inyecta un `shift(-1)` para demostrar
    que el test puede fallar.
  - **Los dos `xfail` están rojos a propósito y su razón lo dice:** el de
    duplicados (30/256, la regla no está firmada) y el del McNemar (las
    dos rutas son correctas; **falta declarar el método**, no corregir una
    cifra). Los dos apuntan a decisión de Nicolás, y las razones aclaran
    que ablandarlos borraría el hallazgo, y que si pasan a XPASS hay que
    sacar el marcador.
  - **Calibración: cero falsos positivos sobre el corpus completo**, con
    dos afinados que vale la pena registrar — el detector de "punto sin
    intervalo" exime `"si MDE = 7 pp"` (escenario) pero **no** exime
    `"PROPUESTO PARA FIRMA: MDE = 7 pp"`, que es literalmente la frase del
    caso histórico.
  - **Y el reporte honesto de lo que NO se pudo convertir en test**, que
    vale tanto como los tests: **el análisis que nunca se guardó como
    código versionado** (el defecto raíz de la segunda corrida). Un test
    estático no puede detectar la ausencia de un archivo que nunca se
    escribió — no hay nada que escanear. De ahí cuelga la segunda que
    tampoco se pudo: **desviarse de un criterio pre-registrado congelado
    sin declararlo**, que sólo es detectable si el análisis está
    versionado. Misma raíz. **La barrera que sí funcionaría no es un test
    sino un hook de pre-commit**, y eso es decisión de proceso: el agente
    hizo bien en no instalarlo solo.
- **02:28** — **Frente C1 cerrado y es el resultado más grande de la
  corrida: NO HAY VEREDICTO. R3 disparó.** El criterio congelado
  (`GEMELO/DISEÑO.md` §6.2) dice *"cualquier fuga detectada por el test de
  causalidad. Sin discusión y sin excepción"*. La fase 2 encontró tres
  defectos **demostrados y medidos**, así que el veredicto de la 5.1
  espera. Ningún criterio se movió, reinterpretó ni ablandó.
  - **Lo primero que hay que decir, porque es lo que más tranquiliza: la
    fuga NO está en `motor.py`.** Anti-look-ahead 18/18, regla maestra con
    0 violaciones sobre 172×4 emisiones. **El modelo que sella está
    limpio.** Lo que estaba roto es el arnés de backtest.
  - **B-1, la fuga real:** `backtest/datos.py` corta el sentimiento por
    `titulares.fecha` (publicación) y **nunca mira `analisis.analizado_en`**.
    Medido: **3.407 de 5.094 análisis (66,9%) se produjeron tarde**, rezago
    máximo **320 días**, y **el primer juicio de IA del sistema es del
    2026-07-04** mientras los titulares arrancan el 2025-09-09. Casi 22 de
    24 meses alimentaban B4 y B5 con juicios que **no existían el día de
    la emisión**.
  - **B-2, y es el más incómodo: la guarda no guarda.**
    `validar_sin_futuro` valida un frame que acaba de recortar **con el
    mismo predicado**, así que su condición de disparo es inalcanzable por
    construcción. Medido: **401.184 invocaciones, cero capaces de
    disparar.** Y una fuga real desplaza VALORES, no el índice: no la ve
    ni aunque pudiera.
  - **B-3:** 263 de 4.160 filas (6,3%) son desenlaces duplicados, con dos
    pares contados **8 veces**. Es el mismo fenómeno que el Frente A
    encontró en la ventana sellada, acá en la ventana larga.
  - **B-4, corregido en el código:** `evaluacion.mcnemar_exact`
    **desbordaba con n ≥ 1024** —el denominador `2.0**n` pasa el rango del
    float— así que la rama declarada exacta hasta 2000 reventaba en todo
    el tramo 1024-2000 y nunca llegaba al fallback. Arreglado en espacio
    logarítmico. **Lo verifiqué yo contra una vara de otra familia**:
    aritmética racional exacta con `Fraction`, sin un solo float. Coincide
    a 1e-13 en todo el tramo, las cuatro anclas históricas reproducen, y
    el borde del umbral es continuo (1998/2000/2002). El umbral declarado
    de 2000 no se movió: **lo que se corrigió es que ahora se cumple**.
  - **El conteo de intentos, escrito a las 01:42 antes de correr nada:
    N = 82**, con desglose sumando por sumando y los **28 candidatos
    excluidos listados** para que la exclusión sea auditable. Hallazgo de
    paso: **cuatro documentos del repo declaran cuatro N distintos** —25,
    26, 32 y 43— **y el único ejecutable dice el más bajo.**
  - **La corrida se selló `INVALIDADA POR FUGA`** en la primera pantalla,
    no como NO-CONCLUYENTE ni como "5.1" a secas. **El holdout quedó
    intacto**, V7 NO EVALUABLE por decisión y no por falta de maquinaria.
  - **Lo que sí se aprende, y es un hallazgo limpio que sobrevive a la
    invalidación:** el campeón acierta la dirección del gap **69,0%
    [67,5, 70,4]** contra 55,4% de la baseline, y la cartera **pierde
    40,7% sin un solo punto básico de costo**. SMH hizo **+137,1%** contra
    la mejor cartera en **−91,4%**. **El gap existe y no es capturable.**
    Eso es exactamente lo que el proyecto venía sospechando y nunca había
    medido de punta a punta.
  - **DSR = 0,0000 en las seis baselines y en los cuatro N** — o sea que
    **el conteo de intentos no era la restricción**, y el agente lo dice
    aunque le costó reconstruirlo.
  - **Dos cosas que el agente reporta contra sí mismo**, y las registro
    porque esa es la conducta que se quiere: introdujo un defecto propio
    (`--etiqueta 5.1` desde el CLI se autoproclama veredicto), y **su
    predicción sobre B-3 salió al revés** — deduplicar *sube* la ventaja y
    el t-stat, no los baja.
- **02:35** — Avisado el Frente B: `GEMELO/bifurcaciones.py` abre
  `sqlite3` directo y **rompe el invariante de aislamiento del GEMELO**,
  dejando la suite en 409/1. No es formalidad: `senales.db` es la base que
  sella, y un `connect` directo puede abrir en escritura. Le pasé también
  el arreglo del árbitro y el hallazgo de los dos fenómenos del Frente A,
  por si le cambia una celda.
- **02:38** — El Frente E terminó **sin entregar informe** ("espero al
  guardián antes de reportar"), que es un malentendido: el dictamen se
  pide una vez sobre la tanda completa, al cierre, y **necesita su
  resultado para poder juzgarlo**. Se lo pedí de nuevo. Su acta §58 ya
  está escrita, así que el trabajo existe.
- **02:45** — **Frente E cerrado, y es el frente que mejor aplicó las
  reglas de la casa — mejor que yo.** `GEMELO/MICRO/INGESTA_ANCHA.md`,
  acta §58, ocho targets reproducibles.
  - **E1 confirmado: 11 ciclos a B=4, 5 a B=28, área bajando 108 → 93
    LUT6, 181/181 bit a bit en los seis anchos.** Pero lo que importa es
    **cómo** lo verificó: *"repetir la misma simulación con el mismo banco
    no verifica nada"*, así que cambió **las dos** variables — un banco
    nuevo que cuenta flancos, **ciego al contador interno** del que salía
    la cifra original, con la relación `banco = DUT + 1` escrita **antes**
    de correr; y simulación **a nivel de compuerta sobre la netlist
    mapeada**, iCE40 y Artix-7 con DSP48E1 reales. 0 desajustes.
  - **Errata sobre código, y es la regla 1 fallando adentro de la
    herramienta:** `medir_a7.py` imprimía la latencia **calculada**
    (`ceil(28/B)+4`) bajo un encabezado que decía *"están MEDIDAS en
    simulación, no calculadas"*. Coincidían porque la predicción era
    correcta — **y una cifra calculada rotulada como medida no confirma
    nada**. Ahora lee del log de simulación y escribe `sin medir` si no
    está.
  - **E2: el techo sigue en 240 y el cuello es independiente de la
    latencia**, con la lectura contraintuitiva medida: **ensanchar
    agranda** el dominio del DSP como cuello, porque baja lo único que la
    ingesta toca. Sintetizó 21 configuraciones en vez de deducirlo, porque
    el propio proyecto ya midió que el área de un pipeline no es la suma
    de sus partes.
  - **E3, y el hallazgo que no buscaba es el más incómodo de la corrida:**
    el silencio de 8 ciclos entre mensajes **no era una comodidad del
    banco, es un requisito de corrección que nadie había escrito**. Con 0
    ó 1 ciclos salen **178 de 181 sellos mal** — y **la latencia sigue
    dando 11 ciclos exactos y perfectamente constante**. Una prueba que
    sólo mirara la latencia habría pasado en verde. Guardia puesto.
  - **E4, y llega más lejos que mi hipótesis.** La mejora también bajaba
    el área en la Go Board (1.198 → 1.184 tras place & route), y **dice lo
    que la errata no dice**: no la rescata, el F1 completo son 1.545
    contra 1.280. Sobre por qué nadie preguntó encontró tres capas, y la
    tercera es la mía con el mecanismo preciso: las cinco alternativas del
    espacio de diseño **eran todas restas**, y *"un marco que sólo admite
    sacrificios no puede contener una opción que mejora dos cosas y no
    cuesta nada"*. **Y el remate: la opción estaba escrita en el primer
    documento** — `RTL.md` §1 dice "un byte **(o un word, si el bus lo
    permite)**". La idea se tuvo, se condicionó a un hecho futuro, y nadie
    volvió a evaluarla cuando el hecho llegó. **La regla que sale: una
    idea condicionada a un hecho futuro necesita dueño y fecha de
    revisión, o se convierte en una decisión tomada por omisión.**
  - **Y aplicó la regla 3 midiendo en vez de suponer:** las cuentas de
    celdas son determinísticas (4/4 y 10/10 corridas idénticas), pero **el
    Fmax NO lo es** — sobre 10 semillas F1SP va de **105,27 a 114,19
    MHz**. Todo Fmax publicado por el proyecto es un estimador puntual de
    una realización del colocador. Y de paso: el `icetime` de 114,59 MHz
    **parecía la vara independiente y no lo es** — no coloca, mide la ruta
    crítica del `.asc` de esa misma semilla.
  - **Dos abstenciones correctas:** no tocó la afirmación de los 0,00474
    pp que el guardián marcó (§12 de la cola), y **no regeneró `ESTADO.md`
    a propósito**, citando el acta §57 — que es exactamente la falta que
    cometí yo en la corrida anterior. El agente aprendió del acta.
- **02:52** — Un `guardian-constitucion` que el propio Frente E había
  pedido devolvió **OBSERVADO** con un solo punto abierto, y lo levanté:
  el acta §58 ahora **declara por escrito** que no regeneró `ESTADO.md` a
  propósito, con su razón. El argumento del guardián es el hallazgo del
  propio frente aplicado a sí mismo: *"igualar por omisión también se
  escribe"*, y un `ESTADO.md` no regenerado sin dueño ni fecha es un
  paréntesis sin dueño.
  - Señaló además que `evaluacion.py` —la **skill compartida** que
    gobierna toda la estadística del proyecto— estaba modificado **sin
    declarar por ningún frente**. Verifiqué: **sí está declarado**, en el
    acta §59 del Frente C1, que es su dueño. El guardián no había leído
    tan lejos. Lo dejo anotado porque la observación era correcta como
    procedimiento aunque el hecho no se sostuviera: un archivo de skill
    compartida modificado en un árbol con dos frentes es exactamente lo
    que hay que mirar dos veces.
  - Su verificación independiente encontró **un cuarto conteo distinto de
    la suite** (403, 408, 409, 411): la inestabilidad por dos frentes
    escribiendo el mismo árbol no es una excusa, es un hecho reproducido.
    El único fallo sigue siendo `GEMELO/bifurcaciones.py` abriendo
    `sqlite3` directo.
- **02:58** — **Frente B cerrado, y es el hallazgo metodológico más
  importante que produjo el proyecto.** `GEMELO/resultados/bifurcaciones.md`
  (283 KB) y `GEMELO/bifurcaciones.py`. Arregló además el aislamiento que
  había roto: la suite queda **413 passed, 2 xfailed, 0 failed**.
  - **Ocho decisiones de análisis documentadas dan 768 formas legítimas de
    medir la misma ventana sellada.** La ventaja recorre **[−4,4, +18,1]
    pp** — un rango de 22,5 pp alrededor de los +6,5 publicados, con
    mediana +7,3.
  - **El veredicto: 0 de 768 celdas dan p < 0,05** con inferencia que
    respeta el clúster de día. **Por la ruta publicada, que supone filas
    independientes, serían 201.** Y esto es lo que hay que leer despacio:
    **la diferencia entre 201 y 0 no la produce ninguna bifurcación — la
    produce el supuesto de independencia.** El p publicado es el más
    generoso de los estimadores disponibles.
  - **Verifiqué por mi cuenta el número que sostiene todo**, porque si el
    DEFF está mal el frente entero se cae. Computé el ICC por ANOVA de una
    vía, que es otra familia de método que el bootstrap de fechas del
    frente: **ICC 0,4034 contra 0,403 reportado; DEFF 3,539 contra 3,54;
    n efectivo 70,1 contra 70.** (El frente pasó después a DEFF **3,63**
    y n efectivo **68**: el ICC no cambió, cambió el tamaño de clúster que
    entra al DEFF —Kish, Σn²/N, en vez de la media simple—, corrección del
    `estadistico-adversario`. Las dos cifras son defendibles y la
    conclusión no se mueve.) Y converge con el DEFF 3,6 que el diseño
    secuencial venía usando para planificar, obtenido por otra vía todavía.
    **El n efectivo es 70, no 248.**
  - **La lectura honesta, y NO es "el modelo no sirve":** el frente se
    preguntó si el test tiene potencia y lo contestó con un número. **El
    MDE de la permutación por día es 18,0 pp al 50% de potencia, IC95
    [13,5, 21,4]**, y al 80% —el umbral convencional de diseño— **25,6 pp,
    IC95 [18,1, 30,6]**; la ventaja publicada es +6,5 y la potencia frente
    a ella, **11%**. O sea que el test **sí rechaza**, pero necesita cerca
    de cuatro veces el efecto publicado. (Los dos MDE llevan intervalo por
    bootstrap de días enteros desde la revisión del 1-sep: salen de 34
    días, no de infinitos.)
    **El track record no está refutando al campeón: está diciendo que
    todavía no alcanza para juzgarlo**, y el supuesto de independencia era
    lo que hacía parecer que sí.
  - **Qué sobrevive a las 768 celdas:** ninguna afirmación sobre la
    ventaja del modelo respecto de su baseline — ni direccional ni de
    magnitud. Lo único que sobrevive (que el modelo acierta más del 50% y
    que su Wilson excluye el 50%, ambos 768/768) **lo comparte con una
    constante**. En magnitud estuvo más cerca: le gana a predecir 0,0 en
    754 de 768, pero con intervalo cluster-honesto excluye el cero en
    **9 de 768** contra 419 por la ruta que supone independencia.
  - **El eje que más mueve el veredicto es `ventana_r2`** (7,4 pp de media,
    y el único que hace cruzar α por la ruta publicada), seguido de
    `zona_muerta` (4,6) y `dedup` (3,3). El que menos, `corte` (0,27).
  - **Diseño del frente, que hay que registrar:** el código **aborta antes
    de escribir** si la celda ancla no reproduce el README exacto
    (n=248, 66,1% vs 59,7%, +6,5 pp, b=72, c=56, p=0,1849). Y **declara
    que los ejes no son ortogonales** en vez de fingirlo, por eso reporta
    cociente y rango y mide cada eje con los demás fijos.
  - **Erratas de tipeo corregidas antes de commitear** (el documento no
    estaba commiteado, así que se corrige en su sitio): seis apariciones
    de "576" donde la matriz es de 768.
- **03:10** — **El Frente B siguió trabajando después de mi commit y el
  titular cambió — para mucho mejor.** Pasó **dos rondas de
  `estadistico-adversario`**: la primera lo rechazó por usar McNemar
  —ignorando el mismo clúster que el informe invocaba— y por comparar el
  MAE contra un punto sin intervalo. La segunda verificó las correcciones
  con su propio código y encontró cuatro defectos más, todos corregidos.
  - **Actualizo lo que reporté a las 02:58**, que citaba deff 3,54 y n
    efectivo 70: la versión revisada da **deff 3,63 y n efectivo 68**. No
    es una errata sino el análisis afinándose bajo revisión adversaria; mi
    verificación por ANOVA daba 3,539 sobre la versión anterior y sigue
    siendo consistente. **La conclusión no se mueve: el n efectivo es del
    orden de 70, no de 248.**
  - **Y el titular nuevo es más simple y más duro que el de la matriz.**
    La cifra publicada de +6,5 pp tiene un intervalo honesto de
    **[−10,5, +23,3] pp**. Con ese ancho el experimento **no distingue al
    campeón de una constante ni de un modelo el triple de bueno**.
  - **El hecho que lo sostiene, y lo verifiqué yo:** el modelo sólo puede
    diferir de "siempre al alza" cuando predice BAJA. Son **128 de 248
    filas, agrupadas en 17 días de emisión, de los que ganó 9 y perdió 7**
    (uno empatado), **p = 0,80**. Reproduje los cinco números exactos.
    **Toda la información discriminante que el track record acumuló en dos
    meses es un 9-7 en 17 días.** Ése es el tamaño real de la evidencia, y
    dicho así no hace falta ninguna estadística para entenderlo.
  - **La potencia frente al efecto publicado es 11%**, y el MDE va con su
    nivel siempre pegado: **18,0 pp al 50% de potencia y 25 pp al 80%**.
    Reportarlo a los dos niveles fue una de las correcciones que pidió el
    adversario, y tiene razón — **un MDE sin su potencia no es
    interpretable**, es un número suelto.
  - **El eje `dedup=solo_reloj` que le sugerí** —deduplicar sólo los 10
    pares de reloj, no los 5 de feriado— da **+9,66 pp con p = 0,0451**,
    justo sobre el umbral. **El frente lo declara explícitamente como
    agregado DESPUÉS de ver la matriz de tres niveles**, que es la
    conducta correcta: un eje que aparece después de mirar y que además
    cruza α es exactamente el que hay que marcar.
  - **Nueve candidatos quedaron documentados como NO-ejes** con su cita y
    su medición, y tres cosas quedaron sin computar y dichas: la
    residualización y la ventana de betas están horneadas en las filas
    selladas y variarlas exigiría re-emitir; y el alcance completo de la
    abstención por sello tardío **no reprodujo**, así que lo descartó en
    vez de publicarlo.
  - 27 tests nuevos en `tests/test_bifurcaciones.py`.
- **03:25** — **La suite epistémica se pagó sola en la misma corrida en
  que se escribió, y cazó a otro frente.** Al correr la suite completa
  sobre el informe nuevo de bifurcaciones, dos detectores saltaron. Los
  miré uno por uno en vez de ablandarlos:
  - **Falso positivo, y era un hueco real del detector:** marcó la línea
    que dice "+6.5 pp, IC95 [−10.5, +23.3]" como intervalo con el nulo
    adentro sin declarar. Pero la línea **sí** lo declara — dice "esta
    ventana **no separa** al campeón de una constante". El detector no
    tenía "no separa" en su vocabulario de reconocimiento. **La lógica
    era correcta y le faltaba idioma**; le agregué seis formas
    equivalentes, con el comentario de por qué.
  - **VERDADERO POSITIVO contra el Frente B, y no lo ablando:** el MDE se
    publica como **punto pelado** —18,0 pp al 50% y 25 pp al 80%— en tabla
    y en el resumen, **sin intervalo**. Y un MDE derivado de la dispersión
    observada entre días **tiene incertidumbre muestral**: sale de 34
    días, no de infinitos. La regla 3 lo cubre de lleno.
  - **La ironía vale registrarla:** el informe rechaza con razón el
    supuesto de independencia en todo lo demás, y **sus dos cifras de
    diseño quedaron sin la incertidumbre que le exige al resto**. Le pedí
    al frente que las compute por bootstrap de días —la misma unidad de
    clúster que ya usa— o que publique la razón si sale inestable, que
    también cumple la regla.
  - Corregí además mi propia bitácora, que citaba los MDE sin su nivel de
    potencia en la misma línea: **un MDE sin su potencia no es
    interpretable**, es un número suelto. Ahora van pegados.
- **03:45** — **El Frente B cerró el hueco del MDE y de paso explicó mi
  propia discrepancia.**
  - **Los dos MDE ahora llevan intervalo**, por bootstrap de días enteros
    con la misma semilla: **18,0 pp [13,5 · 21,4]** al 50% y **25,6 pp
    [18,1 · 30,6]** al 80%. No salió caro ni inestable (~70 s), así que
    hay número y no excusa. Y la lectura que el intervalo habilita es la
    que importa: **aun en el extremo optimista de la banda (18 pp), el
    diseño seguiría necesitando 2,8× la ventaja publicada.** La conclusión
    **no depende de dónde caiga el MDE dentro de su propia
    incertidumbre**, que es exactamente para lo que sirve tener el
    intervalo.
  - **Y el arreglo destapó algo que el frente manejó bien:** en un fixture
    sintético el punto cae **fuera** de su intervalo de percentiles. No es
    error de cálculo, es sesgo de la distribución bootstrap cuando los
    remuestreos son más heterogéneos que la muestra. **En vez de asertarlo
    para que no moleste**, `ic_mde` devuelve ahora `punto_dentro` y el
    informe **lo declara si ocurre**. Sobre los datos reales no ocurre, y
    hay test que lo vigila.
  - **Por qué mi verificación del DEFF daba 3,539 y la suya 3,63**, que
    era mi pregunta abierta: **el ICC es idéntico (0,403 por las dos
    vías)** — que es lo que importaba verificar. Lo que difiere es el
    resumen de tamaño de clúster: yo usé la **media simple** (7,29) y el
    frente usa el **tamaño de Kish**, Σn²/N (7,52). **Kish es el correcto
    cuando los clústeres son de tamaño desigual**, y acá los días tienen
    de 4 a 8 filas. Lo recomputé: 3,537 con media simple, **3,626 con
    Kish**, n efectivo **68,4**. Su versión es la que corresponde.
  - Y el cambio vino de una **corrección del `estadistico-adversario`**,
    que vio que el docstring prometía Kish y el código usaba la media —
    la misma clase de desajuste entre lo declarado y lo ejecutado que esta
    corrida viene cazando en todos lados.
  - **El 9-7 pasó a ser lo primero que se lee** del informe, antes que el
    intervalo y que el cociente. Coincido: todo lo demás —ICC, bootstrap,
    permutación— es la ruta formal hacia ese mismo hecho.
  - 30 tests en `tests/test_bifurcaciones.py`, tres de ellos nuevos para
    guardar el hueco que se acaba de cerrar.
- **04:05** — **Frente D cerrado, y REFUTÓ la hipótesis que yo le di.**
  Eso es exactamente lo que un adversario debe hacer, y lo registro como
  el resultado que es.
  - **Lo que yo pedí que dijera "con todas las letras":** que el efecto
    observado (+6,5) cae bajo el borde inferior del MDE (6,67), o sea que
    "no valdría la pena aunque fuera real". **Lo refutó**: eso es punto
    contra punto, una brecha de **0,17 pp dentro de un intervalo de 33,5
    pp de ancho**. La comparación pareada —que nadie había hecho, y que es
    posible justo porque las dos cantidades salen de las mismas filas— da
    **P(δ_obs < MDE) = 0,569**. **El experimento no ordena las dos
    cantidades.** Escribirlo habría sido cometer, en la sección escrita
    para prevenirlo, el error que el proyecto ya se pilló dos veces.
  - **La escala SÍ coincide, y lo verificó por la vía correcta:** no
    recorrió `f·2c/E|gap|` otra vez, **atacó el otro lado de la
    desigualdad**. La identidad `δ = f·(2q−1)` da 6,4516129032 pp, igual a
    `(b−c)/n` y a la diferencia cruda de tasas, **a diez decimales**. Ni
    b, ni c, ni las tasas entran en el cómputo del MDE.
  - **El titular de D4 es el inverso del esperado y más fuerte.** Por
    punto, **274 de 768** celdas superan 8,96 y **425** superan 6,67. Pero
    **0 de 768 lo superan por intervalo, 0 quedan por debajo, y 768 de 768
    lo contienen.** Ancho medio de los IC: **37,7 pp**. Ninguna de las 768
    formas legítimas de medir esta ventana puede decidir si el efecto es
    relevante o irrelevante.
  - **Y el párrafo que se gana su lugar:** MDE de **relevancia** ≈ 8-9 pp
    contra MDE de **detectabilidad** 25,6 pp al 80%. **El diseño no puede
    ver el efecto más chico que le importaría.** Hay una franja entera de
    8 a 25 pp de efectos económicamente relevantes e **invisibles** para
    esta ventana. Por eso el cero de celdas significativas **no es
    evidencia sobre el modelo: estaba escrito de antemano**.
  - **Y juzgó el MDE que le di, que era parte del encargo:** el
    `[6,67, 11,32]` **no es el intervalo del MDE, es el de E|gap|
    invertido** — `f` entra como punto y la simetría de magnitudes entra
    como certeza, siendo el eje que el propio §A3.1.c declara "el supuesto
    que manda". Además **el signo de la asimetría se da vuelta al cambiar
    de endpoint** (1,33× en retorno de sesión, 0,816× en gap), que es
    confirmación empírica de que la razón 2 hizo bien en retractarse.
- **04:20** — **Arreglados dos de los tres defectos vivos que señaló el
  Frente D**, los dos del mismo linaje que esta corrida viene cazando:
  - **El `8.96` estaba cableado como literal en `bifurcaciones.py`**, y
    encima se dividía por él para producir un "2,8×" publicado. **Es el
    sexto artefacto con el patrón que el guardián cazó en cinco el
    31-ago.** Pasó a constante nombrada, con el comentario de por qué y la
    aclaración de que se cita como referencia externa y no se recomputa.
  - **`mirada.py` ofrecía firmar el 7 pp RETIRADO** (`poner 0.07 cuando
    Nicolás firme`). Un número retirado que sigue ofrecido en el código es
    cómo vuelve a circular. Ahora `MDE_PROPUESTO = None` y el candado dice
    la verdad completa: **hoy NO hay número para firmar**, y explica por
    qué el 7 y el 8,96 quedaron los dos fuera.
  - Al hacerlo **rompí el módulo** —`PLAN` se materializaba al importar y
    con `None` reventaba— y lo arreglé: `PLAN` ya no existe como global.
    Fabricar un plan por defecto "para poder inspeccionarlo" es
    exactamente cómo un número retirado vuelve a circular. Quien quiera un
    plan hipotético llama a `plan(0.07)` explícito y se hace cargo.
  - **El tercero NO lo arreglo y lo dejo señalado**: `mde_desde_v6.py`
    sigue sin ancla temporal, que era una de las cuatro condiciones para
    levantar el rechazo del 31-ago. **El 8,96 de hoy no es el de mañana**,
    y el pre-registro lo cita como parámetro. Va a la cola.

---

# SEGUNDA TANDA — 1-sep-2026, desde las 09:00

## Las firmas que llegaron, y una regla nueva

**Deduplicación: FIRMADA, y la firma es mejor que cualquiera de las tres
ramas que yo había computado.** Nicolás separa los dos grupos porque
tienen orígenes distintos, que es exactamente lo que el forense encontró:

- **Grupo del defecto de `snapshot.py` (10 pares, 31-jul y 5-ago):** la
  fila válida es **la que tiene la sesión objetivo correcta según
  `available_at`**, no la más reciente. **El criterio es la corrección de
  la sesión, nunca la frescura.**
- **Grupo de feriados reales (5 pares, 12-ago y 18-ago):** las dos
  emisiones están igualmente a tiempo, así que **no es un problema de
  deduplicación**. Que una predicción apunte a una sesión con la bolsa
  cerrada es una pregunta de **calendario y de universo**, y va a la cola
  como ítem propio.
- **QUEDA PROHIBIDO `keep="last"`** o cualquier regla equivalente por
  frescura: el forense demostró que **retira selectivamente errores del
  modelo**, y ésa es la explicación mecánica de por qué esa rama daba
  p = 0,032.
- **Decisión tomada conociendo ambos desenlaces**, con p = 0,1847 y
  p = 0,032 a la vista. Va así en el acta.

**Gatillo de la 5.1: NO se releva.** Se espera al **25-oct-2026**, que es
la condición (b) y se cumple sola. Su razón, que vale registrar: *relevar
la (a) después de haber visto que N se cumple y el régimen no sería mover
un criterio congelado habiendo mirado.* **El holdout sigue intacto.**

## La cuarta regla de la casa, ganada anoche

> **UN NÚMERO RETIRADO QUE SIGUE OFRECIDO EN EL CÓDIGO VUELVE A
> CIRCULAR.** Toda cifra retractada se retira también de los valores por
> defecto, las constantes y las firmas de función.

Se ganó con `mirada.py`, que ofrecía `poner 0.07` cuando el 7 pp estaba
retirado hacía horas, y con el `8.96` cableado en `bifurcaciones.py`
—sexto artefacto con el mismo patrón—. Las tres anteriores siguen
vigentes.

## Hitos

- **09:02** — Arranque de la segunda tanda. `HEAD=a49ad76`, árbol limpio,
  14 commits sin pushear. **Fuera de la ventana de sellado**, así que el
  cómputo pesado (C2 sobre 14.618 observaciones, re-corrida de la matriz,
  backtest) entra ahora.
- **09:03** — **El encargo llega cortado**: se interrumpe en el título del
  Frente E, "EL CONTEO DE INTENTOS", sin cuerpo. Por contexto el alcance
  es inequívoco —el código dice `N_INTENTOS_WS5 = 25` con un test que lo
  fija, la prosa declara ≥43 y el Frente C1 de anoche declaró 82— así que
  lo trabajo con ese alcance y **lo marco como inferido, no como
  encargado**. Si Nicolás quería otra cosa ahí, esto se corrige barato.
- **09:05** — **Frente C despachado a `ingeniero-plataforma`**: preparar
  el parche de `snapshot.py:140` **sin aplicarlo**. Con las tres piezas
  que lo hacen accionable en un minuto —el diff exacto, el test que fija
  el comportamiento correcto y **el test-contraprueba que falla hoy**— y
  con lo que más importa: **la declaración del corte de método escrita
  ANTES de aplicarlo**, porque corregir cómo se calcula `sesion_objetivo`
  cambia el significado de las filas futuras respecto de las selladas, y
  las selladas no se reescriben nunca.
- **09:07** — **Frente B despachado**: las dos fugas que quedaron sin
  arreglar y que bloquean el veredicto del 25-oct. La **B-1** (el corte
  del sentimiento por publicación en vez de `analizado_en`) con el encargo
  explícito de **cuantificar cuántas observaciones sobreviven al corte
  honesto** — si casi ninguna, la consecuencia es que B4 y B5 **no son
  evaluables** sobre la ventana larga y hay que decirlo. La **B-2** (la
  guarda tautológica) con la exigencia de una **contraprueba que inyecte
  una fuga conocida**: una guarda sin contraprueba no es una guarda, es la
  regla 1 en otro traje.
- **09:10** — **Frente D despachado**: C2, la condicional sobre la ventana
  larga, con dos condiciones innegociables. **(a) Toda inferencia respeta
  el clúster de día** — después de anoche, un análisis de la ventana larga
  que asuma filas independientes no se acepta. **(b)** Si alguna condición
  candidata usa sentimiento, **hereda la fuga B-1**: o espera el arreglo,
  o corta por `analizado_en`, o la declara NO EVALUABLE. Las tres son
  aceptables; publicarla sin decirlo, no.
- **09:12** — **Frente E despachado al adversario estadístico.** Es el
  caso más puro de la cuarta regla: **un número mal que un test
  protegía** — el test hacía al 25 inmune a la corrección en vez de
  protegerlo de la corrupción. Con el criterio de Nicolás como norma: *la
  retractación de la segunda corrida fue sobre su conclusión, no sobre que
  los análisis se corrieron; por la regla del DSR cuentan igual.*
- **09:14** — **Frente F despachado**: el silencio de 8 ciclos como
  requisito escrito, con el test que lo fija **y que falle por la razón
  correcta** (sellos corridos, no un timeout), más la lección epistémica.
  Con una advertencia explícita: si no encuentra una forma de detectarla
  que no grite por todo, **que lo diga y proponga otra** — anoche hubo que
  reescribir cuatro tests tautológicos por eso.
- **09:16** — Cinco frentes en paralelo más el orientador. Falta despachar
  el **A** (aplicar la deduplicación firmada), que espera la respuesta del
  orientador sobre **dónde vive la capa de medición** y **si `available_at`
  alcanza** para recomputar cuál sesión objetivo era la correcta. Si no
  alcanzara, cambiaría cómo se implementa la firma, así que no lo lanzo a
  ciegas.
- **09:20** — El orientador trajo dos cosas que cambian frentes en
  caliente.
  - **Para el Frente B: el acta dice `min()` y la causalidad exige
    `max()`.** `DECISIONES.md`:5459-5460 escribe el arreglo de B-1 como
    "cortar por `min(titulares.fecha, analisis.analizado_en)`", y eso
    **reproduciría el corte roto** en vez de corregirlo: `analizado_en` es
    posterior a `fecha` por construcción (`datos.py`:188), así que el
    mínimo es casi siempre `fecha`. Lo que la causalidad exige es el
    **máximo** — una observación es utilizable recién cuando ocurrieron
    **las dos** cosas. Es el `available_at` de la ruta de sellado aplicado
    al sentimiento. Avisado al frente; el acta lleva errata al cierre.
  - Y un dato que separa bien la consecuencia: **sólo B4 y B5 usan
    sentimiento**. Si el corte honesto colapsa las observaciones, "B4/B5
    no evaluables" es muy distinto de "el backtest no es evaluable", y hay
    que decirlo separado.
- **09:25** — **Frente A: computé yo la consecuencia de la firma antes de
  despacharlo, y hay que decirla con todas las letras.**
  - **La regla firmada se implementa sola.** Recomputando
    `proxima_sesion_despues_de(exchange, available_at)` fila por fila,
    **exactamente 10 filas no calzan** con su `sesion_objetivo` sellada, y
    son **exactamente** las de 31-jul y 5-ago — el grupo del defecto. En
    el grupo de feriados **las dos filas de cada par calzan**, así que la
    regla no descarta nada ahí. **Separa los dos grupos por construcción**,
    sin lista de fechas cableada. `available_at` está poblado en las 30,
    sin nulos, y se calcula independientemente de la línea defectuosa.
  - **Y el resultado cruza el umbral:**

    | rama | n | ventaja | b/c | p |
    |---|---|---|---|---|
    | sin deduplicar (hoy) | 248 | +6,45 pp | 72/56 | 0,1847 |
    | **REGLA FIRMADA** | **238** | **+9,66 pp** | **72/49** | **0,0451** |
    | `keep="last"` (prohibida) | 233 | +10,30 pp | 70/46 | 0,0323 |
    | `keep="first"` | 233 | +6,87 pp | 72/56 | 0,1847 |

  - **Nicolás firmó "conociendo ambos desenlaces, con 0,1847 y 0,032 a la
    vista" — pero 0,0451 no era ninguno de los dos.** Es un tercer
    desenlace que su propia regla produce y que no estaba sobre la mesa.
    Lo reporto antes que nada porque es exactamente el tipo de cosa que no
    se entierra.
  - **El mecanismo, igual de claro:** `b` queda en **72 sin cambio** y `c`
    baja de **56 a 49**. Las 10 filas retiradas contenían **7 pares
    discordantes y los 7 favorecían a la baseline; cero al modelo.** Es la
    misma asimetría que motivó prohibir `keep="last"`.
  - **La diferencia sustantiva, que sostiene la firma:** acá el retiro no
    es por frescura sino por **corrección demostrable** — esas 10 filas
    tienen una `sesion_objetivo` que no corresponde a su `available_at`,
    así que su `gap_pct` se midió **contra la sesión equivocada**. No son
    predicciones peores: son **desenlaces mal etiquetados**. El criterio
    firmado sigue siendo el correcto; lo que hay que registrar es que su
    consecuencia numérica no era la que estaba a la vista.
  - **Y la opción que no se puede tomar:** lo completo sería
    **re-verificar** esas 10 filas contra su sesión correcta en vez de
    descartarlas, pero eso exige recomputar valores sellados y **las filas
    selladas no se reescriben nunca**. Se descarta por restricción, no por
    preferencia, y así queda escrito.
- **10:05** — **Frente E cerrado: el conteo es 86, y el hallazgo no pedido
  es peor que el que fue a buscar.**
  - **N = 86**, calculado como **suma de un registro de 20 tramos con
    procedencia línea a línea**. El entero mágico dejó de existir:
    `N_INTENTOS_ACUMULADO = sum(f[0] for f in REGISTRO_INTENTOS)`.
    Agregar un intento ahora es agregar una fila.
  - **El test era el mecanismo que lo mantenía corto.** No protegía al 25
    de corromperse: **lo protegía de corregirse.** Es la cuarta regla en
    su forma más limpia. El test nuevo fija la **propiedad** —que el N sea
    la suma, que cada tramo cite evidencia— y trae **tres contrapruebas**
    que fallan por la razón correcta.
  - **Dos correcciones al 82 del Frente C1, de signo opuesto:** −1 por un
    experimento **declarado y nunca corrido** (contarlo contradice la
    regla de arbitraje: nadie miró un resultado), −1 por una condición
    declarada **no medible**, y **+6 por los bloques de 40 filas** — que
    es el caso de manual, porque de ahí salió la ventana 15-23-jul que R2
    congeló como vara permanente: **una decisión sí se tomó mirándolos**.
  - **Ningún veredicto cambia, y la razón es incómoda:** *donde el DSR
    pasa, pasa porque el Sharpe es ficticio; donde no pasa, no pasa porque
    el Sharpe es negativo. Nunca porque el umbral esté bien calibrado.*
    Verificó además el DSR de la 5.1 a **N = 1** —sin deflactar nada— y
    **sigue 0,0000 en las seis baselines**: el conteo no era la
    restricción, y ahora está demostrado más fuerte de lo que se dijo.
  - **Y el hallazgo NO pedido, que sí puede voltear un veredicto:**
    `GEMELO/control_lineal.py`:363 tenía `n_intentos: int =
    N_INTENTOS_DECLARADO` con **9**, y `experimento.py`:134 lo llamaba
    **sin pasar N**. Mientras tanto `backtest/inferencia.py`:127 había
    quitado ese mismo default **a propósito, con acta (§26.1) y con un
    test que lo exige**. **La defensa estaba anulada desde adentro.**
    Medido: `SR0(9) = 0,9986` contra `SR0(86) = 1,6266` — **el default
    regalaba 0,63 de umbral**, y a Sharpe anualizado de 1,2-1,5 el
    veredicto **V5 se daba vuelta de PASA a NO PASA**.
- **10:15** — **Cerré yo ese vector**, que era de cinco minutos y valía
  más que casi todo lo demás: quité el default de `inferencia_sharpe`, el
  N va explícito en `experimento.py`, y agregué un test que fija la
  propiedad —**la firma no puede volver a tener default**— con la
  medición en el docstring.
  - Al hacerlo apareció un **import circular** (`relevo_asiatico` ya
    importa de `experimento`), resuelto con import diferido. **Ese ciclo
    es, en sí, la evidencia de que el registro merece módulo propio**, que
    es justo lo que el Frente E propuso y no instaló por riesgo de
    conflicto. Queda con su costo en la cola.
  - `README.md`:253 dice **"Va en 25"** en la portada pública. **No lo
    toco**: es cifra publicada y lleva tu firma.
- **10:20** — **Frente C cerrado, y encontró MÁS filas de las
  documentadas: 25, no 20.** Auditó las 279 filas selladas recomputando
  desde `available_at`, no sólo las que aparecían duplicadas.
  - **15 son nuevas y NO tienen pareja**, invisibles al `GROUP BY ...
    HAVING COUNT>1` de anoche: 7 del 5-ago (el snapshot del 6-ago tuvo
    **caída total de datos**) y 8 del 5-jul (un sello manual con **casi 3
    días** de atraso).
  - **Y eso abre un hueco en la firma:** la regla de Nicolás está escrita
    para **arbitrar entre dos filas que compiten**. Estas 15 están solas y
    mal. Aplicarla literalmente las descartaría **sin reemplazo**, que es
    otra operación. Avisado al Frente A: que compute la cifra y **no
    decida**.
  - **Un detalle que muestra el sistema funcionando:** en el caso del
    5-jul la sesión correcta **ya había cerrado** al sellar, así que con
    el ancla buena esas 8 pasarían a `no_verificable_timing`. **No las
    descarta un criterio nuevo: las descarta el criterio que el proyecto
    ya tenía.**
  - El parche aplica limpio (`patch --dry-run` verificado), la
    contraprueba **falla hoy** como debe, y el **corte de método está
    escrito antes de aplicarse**. `snapshot.py` sin tocar: 0 líneas de
    diff.
- **10:25** — **Frente F cerrado, y su hallazgo le pega al propio criterio
  de verificación del proyecto.**
  - El requisito quedó escrito como **R1** (mínimo 2 ciclos de silencio) y
    **R2** (ninguna medición de latencia se publica sin la comparación bit
    a bit de la misma corrida), con un preámbulo que vale por sí solo:
    *un requisito que sólo existe como el default de un parámetro no es un
    requisito, es una coincidencia que todavía no falló.*
  - **El mecanismo salió más fino que anoche:** el **puntaje** sellado del
    mensaje k es `feature(k) × beta(k+1)` — **178 de 178 fallos exactos**,
    o sea el modo de falla es **único, no un desorden** — mientras la
    **decisión** sellada es la correcta, **181 de 181**. **El sello se
    contradice a sí mismo.**
  - **Y el agravante es el hallazgo:** como la decisión sale bien, **una
    comprobación restringida a la decisión —la vara que `RTL.md` §4
    defendía como la que importa— también habría pasado 181/181 en
    verde.** El criterio de verificación preferido del proyecto era ciego
    a esto.
  - El test verifica **por qué** falla, con dos comprobaciones que
    descartan los rojos que no prueban nada (compilación, timeout), y
    **contraprueba del propio gate**.
  - **Descartó una forma de detector midiéndola antes de tirarla:** un
    detector de prosa daría positivo en **76 de 110 líneas (69%)**. *Un
    detector que grita en dos de cada tres se desactiva y no previene
    nada.*
  - **Y dejó señalada una trampa latente:** `referencia.py` construye hoy
    **189 casos** contra los **181 congelados** en `parametros.vh`.
    Cualquier cosa que lo toque regenera los vectores con 189 y **mueve en
    silencio todas las cifras publicadas como "181 filas"**. No lo tocó.
- **09:40** — **ERROR DE PROCESO MÍO, y lo registro porque es del tipo que
  esta corrida viene cazando en otros.** Vengo commiteando con
  `git add -A` en un árbol con **seis agentes escribiendo en paralelo**.
  A las 09:21 eso barrió `backtest/datos.py` y `backtest/causalidad.py`
  —trabajo a medio terminar del Frente B— dentro del commit `6bb1f46`,
  **cuyo mensaje no los menciona**. El agente lo detectó y me lo dijo.
  - **Un commit cuyo mensaje no describe lo que contiene es exactamente
    la clase de desfase que el proyecto documenta como errata**, y encima
    lo produje con el mismo hábito cómodo que el resto de la corrida
    estuvo desarmando en el código ajeno.
  - **No reescribo la historia**: `6bb1f46` queda, y esta entrada es su
    errata. Los dos archivos estaban completos y la suite pasa, así que el
    estado es coherente; lo que estuvo mal fue el mensaje y el método.
  - **Cambio la práctica para lo que queda:** staging **explícito por
    archivo**, nunca `git add -A` mientras haya agentes vivos. Es más
    lento y es el precio de que cada commit diga la verdad.
- **09:45** — **Frente B cerrado, y es el resultado que desbloquea el
  25-oct: R3 QUEDÓ LIMPIO.**
  - **B-1 corregida con `max(publicación, analizado_en)`**, no con el
    `min()` que decía el acta — y hay un test que **falla si alguien
    vuelve al mínimo**. La errata de `DECISIONES.md`:5459-5460 queda para
    el cierre, ahora con la evidencia.
  - **Cuántas observaciones sobreviven al corte honesto: 288 de 4.152, el
    6,94%.** 40 de 520 días. **Consecuencia con todas las letras: B4 y B5
    NO son evaluables sobre la ventana larga** — el 93,1% de sus filas se
    emite con las tres features de noticias en la constante 0,0, así que
    la capa colapsa a la anterior.
  - **Y la distinción que salva la lectura:** sus cifras se leen como *"la
    capa de precios con columnas constantes"*, **jamás** como *"las
    noticias no aportan"*. Son cosas distintas y confundirlas sería
    publicar una conclusión sobre noticias que el dato no sostiene.
  - **B0, B1, B2 y B3 no tocan sentimiento y siguen evaluables** sobre la
    ventana completa. **Son dos baselines de seis, no el backtest.**
  - **B-2: la guarda ahora puede disparar, y se demuestra.**
    `recortar_pit()` recibe la serie **sin recortar**, y
    `backtest/causalidad.py` reconstruye el arnés entero con la fuente
    cortada y exige predicción idéntica, **corriendo dentro de
    `motorbt.correr`**. La contraprueba con `shift(-1)` **dispara 10 de
    10**, incluidas las cinco features exclusivas de B4/B5. Y hay un test
    que prueba que **la guarda vieja no habría visto ese `shift(-1)`**.
  - **R3 PASA: gate INVARIANTE sobre 72 comparaciones** (12 fechas × 6
    baselines). Corrida en
    `backtest/resultados/20260901-133154-5.1-arnes-corregido-gatillo-incumplido/`,
    con **N = 92** declarado en disco antes de computar (86 del registro
    del Frente E + 6).
  - **Y el resultado que importa: corregir la fuga NO cambió el
    desenlace.** B4 pasó de IC 0,2213 a 0,2216 y de MAE 1,575 a 1,564 —
    **el sentimiento con fuga tampoco estaba aportando**. La conclusión
    económica es la misma: el gap existe (69% de acierto direccional) y
    **no es capturable**.
  - **Regla 4 aplicada por su cuenta:** `ventana_larga.py` imprimía
    n=215/p=0,36, ya superado; y `veredicto_51._md` tenía **cableadas las
    cifras de la corrida invalidada** y las habría reimpreso en el reporte
    nuevo. Reescrito para generarse desde el JSON.
  - **Abiertos y declarados en la primera pantalla:** B-3 (263 desenlaces
    duplicados, que **no es fuga temporal** y por eso R3 no lo juzga, pero
    bloquea igual), S-1, S-3, **no existe holdout material** (la cuarentena
    de V7 es procedimental) y la fuente **no es point-in-time**.
- **10:00** — **Frente A cerrado: la regla firmada está en el ejecutable, y
  el veredicto de la matriz NO cambia.**
  - **Implementada sin lista de fechas**, como corresponde: el criterio es
    `sesion_objetivo == proxima_sesion_despues_de(exchange, available_at)`
    aplicado **sólo dentro de pares**. Los dos grupos se separan por
    construcción — 10 pares donde una fila calza, 5 donde calzan las dos y
    **la regla se abstiene sola**.
  - **Y preservó las anclas históricas**, que es lo que yo no había
    pedido y hacía falta: `dedup=False` reproduce las afirmaciones
    congeladas anteriores a la firma (§2 n=228 y §2.8 n=223, **21/21 y
    7/7**). Una regla nueva que rompiera la reproducción de un
    pre-registro habría sido un problema peor que el que resuelve.
  - **Las cifras:** `excluir_cero` n=238, +9,7 pp, p=0,0451. MAE mejora a
    **2,52 vs 2,98 (−15,3%)**. **Y la cobertura EMPEORA**: 92,9% con ratio
    2,19× contra 90,3% y 1,84×. Es el único indicador que la regla mueve
    en contra, **y el frente lo reporta igual**.
  - **La matriz: 0 de 192 celdas** con p < 0,05 por clúster (antes 0 de
    768; el eje cayó y la matriz se redujo). **El veredicto no cambia.**
  - **Su lectura sobre la defensibilidad es la que hay que citar**, y la
    adopto entera: la regla es defendible **por una razón que no es el
    p** —hay un desajuste demostrable entre insumo y objetivo—, pero se
    cita **siempre con tres advertencias pegadas**. La segunda es la que
    importa: **cruzar α no es tener evidencia.** Con el estimador que
    respeta el clúster de día la ventana queda en **+9,7 pp con IC95
    [−7,2, +26,5]**, n efectivo **67 y no 238**, y **0 de 192** celdas
    significativas. Todo el peso discriminante es un **10-6 en 17 días**
    (binomial p = 0,45). **McNemar cruza porque supone una independencia
    que los datos no tienen.**
- **10:05** — **Dos correcciones del Frente A hacia mí, las dos justas.**
  - **Mi encuadre de "desenlaces mal etiquetados" era impreciso y lo
    corrijo.** El `gap_pct` de esas 10 filas **es el gap correcto de la
    sesión que declararon**. Lo que está mal es el **pareo
    insumo↔objetivo**: la predicción es β·SOX(t) puntuada contra el gap de
    t+2. Sigue siendo razón real para descartar, pero es más precisa, y la
    precisión importa cuando el descarte mueve un p.
  - **Y un error mío que rompió código commiteado.** Al arreglar el `8.96`
    cableado en `bifurcaciones.py` usé un ancla —`def _bloque_potencia(`—
    **que no existe en ese archivo**, con un `if` que hizo que la
    inserción de la constante **no ocurriera en silencio**, mientras los
    dos reemplazos que la usan **sí se aplicaron**. Commiteé un
    `NameError` en `a49ad76`: `python -m GEMELO.bifurcaciones` reventaba
    antes de escribir nada. **No lo verifiqué.**
    - Es exactamente la clase de defecto que esta corrida viene cazando en
      código ajeno, cometido por mí en el acto de arreglar otro: **una
      guarda que protege de un duplicado y a cambio produce un archivo
      roto.**
    - Y el frente encontró **por qué la suite no lo atajó**: los tests
      llamaban a `construir_matriz` pero **nunca a `componer_informe`**.
      Un generador de informes que lanza `NameError` pasaba en verde.
  - **También corrigió mi conteo:** no son 10 las filas que no calzan sino
    **25**, coincidiendo con el Frente C por vía independiente. Las 15
    singletons **no las toca la regla**, porque deduplica y no filtra por
    coherencia — y quedan en la cola con su cifra (**n=223, +14,3 pp,
    69/37, p=0,0024**), sin decidir.
  - **Cuatro módulos heredan la regla sin haber sido tocados** y sus
    cifras se moverán si se re-corren. Declarado en el acta §60.
- **10:08** — **Frente D cerrado, y da vuelta la sospecha que el proyecto
  arrastraba hace tres corridas.**
  - **La ventaja NO está concentrada: está MÁS DISPERSA que el azar.** El
    100% del neto vive en el 16,5% de las fechas, contra **0,64%** bajo la
    nula de signo permutado. Sobre 2.030 fechas y 14.000 filas, con DEFF
    re-medido sobre esta ventana y no heredado (ICC 0,326, **DEFF 3,04**,
    n efectivo 4.601).
  - **Y la medida que no depende de ninguna nula:** quitando el 10% de
    mejores fechas queda **+6,6 pp [4,7 · 8,4]**, que excluye cero;
    quitando el 20% **se da vuelta a −1,9 pp**. La ventaja vive en el
    mejor quinto de las fechas — **ni "seis días" ni repartida**.
  - **¿Predicen fuera de muestra? Sí, y casi tautológicamente**, que es la
    respuesta más útil y la menos cómoda. Cuatro de siete cumplen el
    §4(a), pero **lo que discrimina es la magnitud del movimiento del SOX,
    y la predicción del campeón ES beta × ese movimiento**: es aritmética
    del modelo, no un hallazgo de mercado. **Las condiciones con
    información nueva son exactamente las que fallan** (`disp_asia`,
    `dias_trimestre`, `vol_sox_10`).
  - **Julio no es de otra especie.** +40,91 pp reconstruido contra +40,9
    sellado —dos mecanismos independientes— pero está en el **percentil
    90,3** de los bloques contiguos de su ancho y hay **157 bloques
    históricos sin solape iguales o mejores**. Su firma es atípica, pero el
    motor es `disp_asia`, una de las que **no** discrimina: descripción,
    no explicación.
  - **La reconciliación de las dos ventanas, que era la pregunta:**
    pareando por fecha de emisión **y** sesión objetivo (214 filas), 100%
    mismo signo y gaps idénticos. **La reconstrucción es fiel.** Y los
    +6,2 pp sellados se descomponen en julio +40,9 (44 filas), **dos
    fechas de incidente de producción −62,5 pp (16 filas)**, y un resto de
    **+4,1 pp con p = 0,44** (196 filas).
  - **Cinco errores propios, corregidos en el ejecutable y reportados**, y
    cuatro habrían producido conclusiones falsas publicables. El más
    instructivo: parear sólo por sesión objetivo produjo una **firma de
    fuga perfecta** (13 de 14 desacuerdos, p = 0,0018) que era **pura
    ilusión** — la emisión del 5-ago apunta al 7-ago porque **la corrida
    del 6 falló**, así que comparaba predicciones hechas con un día de
    diferencia. **Es el defecto de `snapshot.py` apareciendo disfrazado de
    fuga.**
  - **El 91,4% quedó refutado y corregido en el ejecutable**: con la clave
    correcta da **100% sobre 214 filas, 0 diferencias**. Con errata en el
    código. **`ventana_larga.md` y `.json` siguen publicando el 91,4% y
    quedan stale** hasta que alguien re-corra ese módulo. Y la advertencia
    de lectura que agregó: **esto no prueba que Yahoo no revise la
    historia, sólo que no la revisó en el tramo auditable de 2026.**
  - `densidad_noticias` **NO EVALUABLE**, por dos razones y no una: la
    fuga B-1, y **cobertura** — `titulares` arranca en 2025-09-09 contra
    una ventana que empieza en 2018. **Aunque se arregle la fuga, la
    segunda razón sigue en pie.**
- **10:12** — **Mi `git add -A` fue peor de lo que dije.** No sólo barrió
  trabajo en curso: en el caso del Frente D barrió una **versión temprana
  y BUGGEADA** —la del McNemar contra un hombre de paja y el pareo por
  sesión— hacia `6bb1f46`. Durante unas horas el repo tuvo commiteada una
  versión de `condicional.py` que producía conclusiones falsas. La
  correcta se commitea ahora. **El staging explícito no era una
  formalidad.**
- **10:35** — **Dos detectores nuevos en la suite epistémica, uno por cada
  error nuevo de esta tanda — y el segundo me enseñó algo sobre el
  primero.**
  - **`test_ninguna_funcion_de_inferencia_ofrece_un_N_de_intentos_por_defecto`**
    — busca **por nombre de parámetro**, no por módulo, para que una
    tercera función de inferencia quede cubierta sin que nadie se acuerde
    de este test. **Contraprueba: reintroduje el default de 9 y falla.**
  - **`test_todo_modulo_de_analisis_importa_sin_reventar`** — y acá está
    la lección. Le hice la contraprueba borrando la constante que yo mismo
    había olvidado insertar, **y NO falla**: un `NameError` dentro de una
    f-string vive en el cuerpo de una función y sólo revienta **cuando
    alguien la llama**, no al importar. **Mi test no habría cazado mi
    propio bug.**
  - **No lo ablandé ni lo tiré: le corregí el docstring para que diga lo
    que NO hace**, con la contraprueba que lo demuestra. Sirve para la
    familia vecina —sintaxis, imports circulares, constantes de nivel de
    módulo— y eso vale; presentarlo como más habría sido exactamente el
    vicio que la suite existe para cazar.
  - Lo que sí cazaría el caso original es una resolución de nombres tipo
    `pyflakes`, y **verifiqué que no hay ningún linter instalado** en el
    venv. Agregar dependencia es decisión con acta: queda **propuesto y no
    instalado**. Y anoto la otra mitad de la defensa, que es más barata y
    ya se sabe cuál es: **que los tests llamen a las funciones que generan
    informes** — `construir_matriz` sí, `componer_informe` no, y por ese
    hueco pasó el error.
- **10:40** — **Frente G cerrado. `espera_firma.md`, quince ítems, y los
  tres primeros suman 45 minutos.**
  - **El nombre de la edición de Vivado se movió dos veces y las dos veces
    nuestros documentos quedaron atrás.** Hasta **2025.2** es *Vivado ML
    Standard Edition*, gratis y **sin archivo de licencia**; desde
    **2026.1** son cinco tiers y **BASIC** cubre la serie 7, también
    gratis. Y **la descarga pesa 230-350 MB, no 95 GB** — los 95,69 GB son
    sólo el instalador offline con todos los dispositivos.
  - **Dos hallazgos nuevos, y uno afecta al ramo:** desde 2026.1 Vivado
    **no arranca sin archivo de licencia ni en BASIC**, y **BASIC excluye
    los reportes de cierre de temporización**, que es uno de los hitos.
  - **Y una disputa que NO resolvió, y eso es lo correcto:** hay cobertura
    de que BASIC quedaría restringido a Windows, empujando Linux a un tier
    pago, contra otra fuente que dice lo contrario. **La página de
    licenciamiento de AMD dio timeout en todos los intentos**, así que lo
    dejó **declarado como contestado en vez de elegir una lectura.**
  - **Por eso su recomendación es doblemente robusta:** bajar **2025.2 del
    archivo** (sin licencia, sin tiers, Linux sin discusión) e instalar
    **del lado Windows**. Las dos se sostienen bajo **cualquiera** de las
    dos lecturas, y el lado Windows ya tenía dos razones previas
    independientes.
  - **Riesgo de calendario nuevo:** si el país dispara la revisión de
    control de exportación son **1 a 3 días hábiles**. El trámite deja de
    ser "de hoy".
  - **Dos cosas verificadas contra el repo, no contra los documentos:**
    `parametros.vh` congela `N_CASOS 181` y los `.hex` tienen 181 líneas
    mientras `senales.db` ya da **189** — **la trampa de `referencia.py`
    está confirmada de primera mano**. Y **el 25 del README no está
    dormido: la corrida condicional de esta mañana publicó "N acumulado 25
    → 33" partiendo de la cifra de la portada.** Es la cuarta regla de la
    casa observada **en vivo, hoy**.

---

## Handoff

**Qué quedó hecho.** Los seis frentes cerrados y commiteados, más el
cierre. **R3 quedó limpio**: las dos fugas del arnés corregidas, con
contraprueba que dispara 10/10, y el veredicto del 25-oct desbloqueado.
La regla de deduplicación firmada **está en el ejecutable**, preservando
las anclas históricas (21/21 y 7/7). El conteo de intentos pasó de un
entero mágico a un **registro de 20 tramos con procedencia (N=86)**, y de
paso se cerró **un vector vivo que daba vuelta V5**. El parche de
`snapshot.py` está listo con test, contraprueba y **la declaración del
corte de método escrita antes de aplicarse**. La suite epistémica va en
**19 tests**.

**Los tres resultados que cambian lo que el proyecto puede afirmar.**
Primero: **la ventana sellada no alcanza para juzgar nada** — n efectivo
**67**, y toda su información discriminante es **un 10-6 en 17 días**.
Segundo: **cruzar α no es tener evidencia** — la regla firmada da
p=0,0451 pero su IC95 de clúster es **[−7,2, +26,5]**. Tercero, y da
vuelta tres corridas de sospecha: **la ventaja no está concentrada, está
más dispersa que el azar**, y **julio no es de otra especie** (157 bloques
históricos iguales o mejores). Lo que sí queda firme: **el gap existe (69%
direccional) y no es capturable**.

**Qué quedó a medias, y por qué.** Las **15 filas sin pareja** que la
firma no previó —nadie sabía que existían— quedan con su cifra computada
y **sin decidir**: la regla arbitra entre dos filas que compiten y éstas
están solas. **B4 y B5 no son evaluables** sobre la ventana larga (sólo
6,94% sobrevive al corte honesto), y eso se lee como "la capa de precios
con columnas constantes", **jamás** como "las noticias no aportan". Y
`ventana_larga.{md,json}` quedan **stale** publicando el 91,4% ya
refutado: el ejecutable está corregido, los artefactos no.

**Dos errores míos, registrados.** Commiteé con `git add` masivo en un
árbol con seis agentes: barrí trabajo en curso de dos frentes, **uno en
versión buggeada**. Y commiteé un `NameError` al arreglar el `8.96`
cableado, usando un ancla inexistente y sin verificar. Cambié a staging
explícito por archivo.

**Qué espera decisión, en orden.** Todo está en
`GEMELO/resultados/espera_firma.md`, resoluble en una sentada. Los tres
primeros suman 45 minutos: **el parche de `snapshot.py`** (5 min, el único
que sigue haciendo daño hoy), **la cuenta AMD** (20 min, desbloquea todos
los hitos en silicio) y **las 15 filas + publicar el README** (20 min,
acoplados: publicar +9,7 pp con una rama declarada de +14,3 pp sin
resolver es peor que no publicar ninguna).

**Comandos exactos.** El de publicación (`git push origin main`) lo corrés vos,
como siempre. Para ver lo de hoy: `python -m GEMELO.bifurcaciones`,
`python -m GEMELO.CONDICIONAL.condicional`, `python -m pytest tests/ -q`.

