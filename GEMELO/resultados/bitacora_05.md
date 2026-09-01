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
    n efectivo 70,1 contra 70.** Y converge con el DEFF 3,6 que el diseño
    secuencial venía usando para planificar, obtenido por otra vía todavía.
    **El n efectivo es 70, no 248.**
  - **La lectura honesta, y NO es "el modelo no sirve":** el frente se
    preguntó si el test tiene potencia y lo contestó con un número. **El
    MDE de la permutación por día es 18,0 pp**, y la ventaja publicada es
    +6,5. O sea que el test **sí rechaza**, pero necesita casi el triple.
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

