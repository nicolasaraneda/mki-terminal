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
