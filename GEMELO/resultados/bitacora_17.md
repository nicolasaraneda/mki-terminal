# Bitácora de la corrida 17 — el pre-registro secuencial: cuatro condiciones atendidas, QUINTO RECHAZO

> **El resultado, antes de los hechos.** Las cuatro condiciones del cuarto
> dictamen están atendidas y el documento reproduce el día que se firma. El
> **quinto dictamen rechazó igual**, por tres defectos que esta corrida no
> buscaba, y el `curador-epistemico` rechazó antes la primera redacción con
> doce bloqueantes. **El pre-registro no se congela.** Un rechazo bien
> explicado es un resultado: §10.

**Domingo 25-oct-2026, de noche, con Nicolás presente.** Encargo:
`~/encargo.md`, leído entero antes de ejecutar nada. Excepción nocturna
firmada sin tope (acta §107.4 (4)).

**Todas las horas salen de `date`, leído en el momento.** Ninguna está
estimada: estimarlas produjo erratas en dos corridas anteriores.

## 0. Desvío declarado antes de nada: el modelo

El encargo dice «Modelo: Fable, esfuerzo alto, elegidos al arrancar y sin
cambiar a mitad de sesión». La sesión se abrió en **Opus 5 (1M de contexto)
con esfuerzo xhigh**, elegido al arrancar y **no cambiado** en toda la
corrida. Se cumple la condición operativa del encargo —elegido al arrancar,
sin cambiar— y no la letra del modelo. Queda declarado acá y en el acta de
cierre porque es un apartamiento de la letra, y la regla de la casa es que
un apartamiento se declara aunque sea inocuo.

## 1. Condiciones de arranque

| Hora (`date`) | Qué |
|---|---|
| 17:43:20 | `date` de apertura |
| 17:43:29 | `git log --oneline -6`: HEAD **`d034d39`** (backup del 23-oct) sobre `627cc1b`. **Coincide con lo esperado.** |
| 17:43:29 | `git status --short`: `M DECISIONES.md`, `M data/backups/sello_dinero.csv`, `M data/sonda_cierre.csv`, `?? data/backups/sello_dinero_ext/ext_2026-10-23.{csv,meta.json}`. **Sólo `data/` y `DECISIONES.md`, como el encargo esperaba.** Rama `main`. |
| 17:43:29 | `systemctl --user list-timers`: los **8 timers `mki-*`** instalados, último disparo el viernes 23-oct, próximo el lunes 26-oct 17:50. Ninguno disparó durante la corrida (domingo). **No se instaló, modificó, reinició ni recargó ninguna unidad.** |
| 17:43:47 | sha256 de las tres bases, **al abrir** (tabla en §9) |
| 17:43:52 → 17:51:09 | **Suite completa del árbol real al abrir: 1225 passed, 5 skipped, 1 xfailed, 0 failed** (436.21 s). **Idéntica a la referencia del 19-oct** (acta §107.1). Sin el patrón de la medianoche (§107.2): la suite empezó y terminó la misma tarde. |
| 17:49:07 | `git worktree add` del worktree de la corrida |

**Las bases no se pudieron copiar al worktree.** Se pidió una vez el
permiso de `cp` combinado y una vez solo; **denegado las dos veces**. Rige
el criterio **§95.5**: decide la suite del árbol real con todas las bases,
y se declara. Para las mediciones se usó un **enlace simbólico** a
`senales.db` dentro del worktree —uso de solo lectura por construcción,
todo el camino pasa por `mode=ro`— y se retiró antes de cualquier `pytest`
en el worktree, para que ningún test pudiera escribir en la base real. Las
huellas sha256 del cierre (§9) son la prueba de que no se escribió.

## 2. Orientación: lo leído antes de escribir una línea de código

`GEMELO/SECUENCIAL/DISEÑO.md` entero (1.178 líneas), `mirada.py`,
`mde_desde_v6.py`, `diseno_secuencial.py`, `fronteras.py`,
`mde_vs_observado.py` y su resultado publicado, `tests/test_secuencial.py`,
`tests/test_secuencial_07.py`, `backtest/linea_base.py` entero,
`tests/test_epistemico.py`, `cifras.py`, `GEMELO/cifras_retiradas.md`,
`.claude/hooks/guardia-reglas.py`, las actas §56, §60, §61, §78, §82,
§33.8, §95.5, §105, §106 y §107, y las tarjetas §82, §87, §88, §89 de
`espera_firma.md`. Más el agente `orientador` (ritual de `CLAUDE.md`) y las
skills `cifras-canonicas` y `estadistica-evaluacion`.

**El dictamen del cuarto rechazo NO está versionado.** No hay
`dictamen_05`/`dictamen_06`: los cuatro rechazos al documento central
ocurrieron el 31-ago antes de commitear y quedaron en la cabecera del
propio documento, en `DECISIONES.md` §56 y en `bitacora_04.md`. (El
«quinto rechazo» que sí existe en `dictamen_08/F.md` es de un frente
paralelo, el simulador, y no de este documento. No confundirlos.)

### 2.1 Estado de las cuatro condiciones, leído del código y del documento ANTES de tocar nada

| # | La condición, textual | Estado al abrir |
|---|---|---|
| (i) | congelar la regla de deduplicación, con su sensibilidad publicada | **ABIERTA, y mal planteada.** Hay DOS reglas. La de FILAS está FIRMADA desde el 1-sep (actas §60 y §61) y `cargar()` la aplica por defecto; la v5 no la cita y sigue discutiendo entre `keep="first"` y `keep="last"`, que no es ninguna de las dos. La del ESTIMADOR no existía como pregunta separada. |
| (ii) | rehacer §A3.1.b con intervalos | **ABIERTA.** La razón 2 ya estaba retractada con intervalos; la razón 1 no tenía ninguno. |
| (iii) | derivar el MDE en la escala del endpoint con su intervalo | **ABIERTA EN PARTE.** La cabecera de la v5 traía el valor y un intervalo; `mirada.py:65-71` ya declaraba que ese intervalo **era el de E\|gap\| invertido** y no el del MDE, y el Frente D lo había medido el 1-sep. El cuerpo del documento seguía en la escala del retorno de sesión. |
| (iv) | anclar `mde_desde_v6.py` con `hasta_sello`, arreglar las cifras que ya no reproducen, al menos un test | **ABIERTA, entera.** `cargar_filas()` escribía su propio SQL (`:94-102`), sin corte de fecha y **sin la exclusión de conocibilidad** que las cifras publicadas aplican desde el 29-sep. **Cero tests**: ningún archivo de `tests/` nombra `mde_desde_v6`. |

### 2.2 Contradicciones internas de la v5, censadas antes de tocar nada

1. La cabecera retira el MDE de la escala del retorno; **§A3.1.c, §A3.1.d, §A3.5, §A5 y la tabla del acta lo siguen proponiendo.**
2. La tabla del acta dice «Fecha de congelamiento 2026-08-31» **sobre un documento que nunca se congeló**, y da un commit base.
3. «ac1 sobre **34** fechas» en un lugar y «sobre **35**» en otro, en el mismo documento.
4. El cierre dice «la primera mirada es el 2026-11-19 y no antes» — la fecha del MDE de *calendario*, no del que el documento proponía (que daba 2027-02-09).
5. El cierre dice «hay 0 filas nuevas»; al 22-oct la población tiene 288.
6. §A3.1.a: la ERRATA del 1-sep corrige «cinco sesiones» a cuatro, y **doce líneas más abajo el documento vuelve a decir cinco**. La corrección no alcanzó a su propia copia.
7. §A3.1.a cita §33.8 como «pregunta pendiente»; **las actas §60 y §61 la cerraron el 1-sep.**
8. §A2 nombra McNemar como el estadístico sin citar el acta **§61**, que al día siguiente de escribirse el documento decidió que McNemar deja de ser el estadístico principal de la ventana sellada.
9. Las cifras de estorbo (`p_d`, E\|r\|, ritmo) salen de la rama de filas que la decisión D1 **derogó** el 3-sep (acta §78). El documento se escribió dos días antes.

### 2.3 Las tres preguntas del encargo §0.3 (c), respondidas del código

- **¿`mirada.py` deduplica?** Hoy **sí, de rebote y sin saberlo**: `cargar_ventana_nueva()` llama a `cargar()`, que desde el 1-sep aplica la regla de filas firmada por defecto. El «defecto descalificante» del cuarto dictamen —parámetro deduplicado contra estimador sin deduplicar— se cerró solo, por un cambio en un módulo que `mirada.py` no es dueño. **Y se invirtió:** el que NO aplicaba la regla firmada era `mde_desde_v6.py`, con `drop_duplicates(keep="first")`.
- **¿Cómo agrupa los clústeres?** Por **fecha de emisión** (`groupby("fecha")`).
- **¿`backtest.linea_base.cargar` tiene `hasta_sello`?** **Sí**, y corta por `verificado_en` — no por fecha de emisión, que es la partición del pre-registro. De ahí que la ventana antecedente necesite **dos** cortes y no uno.

## 3. Bloque A — que el documento reproduzca desde sus scripts (condición 4)

**Lo hecho.** `mde_desde_v6.py` dejó de escribir SQL. La ventana la define
el módulo nuevo `GEMELO/SECUENCIAL/ventana_antecedente.py`, con dos cortes
explícitos (**emisión ≤ 2026-08-31**, de §A2; **sello ≤ 2026-09-02**,
medido: la última verificación de una fila emitida hasta el corte de
emisión) y un **candado** —`cierre_de_ventana()`— que cuenta las
verificaciones tardías y se niega a devolver una ventana distinta en
silencio. Hoy: **0 tardías**, última verificación de la ventana
`2026-09-02T22:15:11Z`.

**Y había un SEGUNDO archivo con la misma falla, peor.**
`diseno_secuencial.ac1_ventana_antecedente()` llamaba a `cargar()` **sin
ancla**, o sea leía el track record VIVO. `ac1` es una función del acierto:
correr esa función hoy habría computado una cifra prohibida **sobre la
población**, sin dejar línea en `miradas/registro.log`, porque ese registro
sólo lo escribe `mirada.py`. Se encontró **antes de correrla** y se ancló.
Censo de los cuatro lectores sin ancla que quedan en `GEMELO/SECUENCIAL/`
(`autocorrelacion.py:119`, `estimandos.py:139`, `trayectoria.py:152`, y el
corregido): los tres primeros leen la base viva en sus `main()`/`salida1()`
y **no los llama ningún test** —verificado— así que la suite no mira; pero
correrlos a mano hoy sería una mirada. Va al acta de cierre como hallazgo.

### 3.1 Tabla de reproducción: cada cifra de la v5, la de hoy, y si reproduce

Todas las de «hoy» salen de `ventana_antecedente.py`, `mde_desde_v6.py`,
`tabla_firma.py` y `diseno_secuencial.py`, corriendo.

| Cifra | v5 | hoy | ¿Reproduce? |
|---|---|---|---|
| filas duplicadas en la ventana antecedente | 30 filas, 15 pares, **4** sesiones | 30, 15, 4 | **SÍ, exacto** |
| umbrales OBF | 4.048 / 2.862 / 2.337 / 2.024 | iguales | **SÍ** |
| fronteras contra Jennison-Turnbull | 2.362 y 2.024 | iguales (test en verde) | **SÍ** |
| inflación contra Armitage-McPherson-Rowe | 5 valores | iguales (test en verde) | **SÍ** |
| pasivo, rango | [0.09, 0.18] | igual | **SÍ** (pero la cuenta está incompleta: §A1) |
| potencia idealizada | 0.80 | 0.8000 | **SÍ** |
| potencia con la regla del máximo | «~0.76», sin script | **0.7537**, con script y test | aproximada; la v5 era optimista |
| filas de la ventana antecedente | 256, 39 días hábiles, 35 fechas | **272** sin la regla de filas; **262** con ella y `excluir_cero`; **37** fechas | **NO** — la ventana no tenía ancla y creció |
| fechas de `ac1` | 34 en un lugar, 35 en otro | **37** | **NO** (era la contradicción «34 contra 35») |
| `ac1` | −0.135 ± 0.171 / −0.134 ± 0.169 | **−0.176 ± 0.164** | **NO** |
| `p_d` | 128/248 = 0.516 | **129/262 = 0.4924** | **NO** — rama de filas derogada (§78) |
| `f` (fracción «baja») | 0.531 | **0.4924** [0.3190, 0.6565] | **NO** |
| E\|r\| con duplicados | 4.0231 % | **3.8666 %** | **NO** |
| E\|r\| deduplicada | 3.7242 % (`keep="first"`) | **3.5556 %** (regla firmada) | **NO** — otra regla y otra ventana |
| E\|gap\| deduplicada | 2.9650 % | **2.8921 %** [2.2250, 3.8368] | **NO** |
| E\|r\| reproducción desde Yahoo | 3.7594 % | **3.7724 %** | casi; es una descarga en vivo |
| MDE a 25 pb, escala del endpoint | 8.96 pp, IC95 [6.67, 11.32] | **8.51 pp, IC95 [4.94, 13.09]** | **NO**, y el intervalo medía otra cosa (un insumo de tres) |
| Connor, n iid a 10 pp | 403 | **384** | **NO** (`p_d`) |
| × DEFF 3.6 | 1.450 | **1.383** | **NO** |
| `N_max` a 10 pp | 1.485 | **1.419** | **NO** |
| ritmo de acumulación | 6.56 filas/día hábil (proyectado) | **7.579** (población, MEDIDO) | **NO** — proyectado contra medido |
| SMH en la ventana | −5.18 % en 39 sesiones | **−8.47 % en 40** | **NO** — insumo no anclado (tarjeta §94) |
| tasa de acierto necesaria a 25 pb | 54.9 % | **54.1 %** [53.2, 55.2] | **NO** |
| tasa de la baseline | 59.7 % | **54.2 %** Wilson [48.1, 60.1] | **NO** — era de otra ventana |

**Veintiuna cifras de la v5 no reproducen y seis sí.** Las seis que
reproducen son exactamente las que el cuarto dictamen había verificado en
verde, más el hallazgo de los duplicados. Las veintiuna que no tienen
**una sola causa en común**: el documento tomaba sus parámetros de una
ventana sin ancla y de una rama de filas que el proyecto derogó dos días
después de escribirlo.

**Tests nuevos para `mde_desde_v6.py`** (antes tenía cero), todos de
comportamiento:
`test_el_mde_no_se_mueve_si_la_base_crece_despues_del_corte` (mueve
`CORTE_SELLO` un año y exige el mismo n, el mismo MDE y el mismo `p_d`),
`test_el_intervalo_conjunto_es_mas_ancho_que_el_de_un_solo_insumo`,
`test_p_d_del_plan_es_la_que_mide_el_script`,
`test_el_mde_escala_con_el_costo_y_cae_con_la_magnitud`.

## 4. Bloque B — el MDE en la escala del endpoint, y la tabla de la firma

**MDE a 25 pb = 8.51 pp, IC95 [4.94, 13.09]**, propagando `f` y E|gap|
**juntos** por bootstrap de clústeres de día (10.000 réplicas, semilla
20260901, 37 clústeres). Propagando sólo E|gap| sale **[6.42, 11.06]**, que
es lo que la v5 publicaba como «el intervalo del MDE». El tercer eje, la
simetría de magnitudes, queda **declarado fuera** con su sensibilidad en
`mde_vs_observado.md` D1c; no se recomputó porque estimarla condiciona en
el acierto del modelo, y el encargo prohíbe recomputar cualquier cifra que
dependa del acierto, también en la ventana antecedente.

**La tabla para la tarjeta** (`tabla_firma.py`; ritmo MEDIDO por conteo:
288 filas en 38 días hábiles, 7.579 filas/día hábil):

**El intervalo HONESTO** (`p_d` = `f` por réplica): `N_max` mediana
**1.920**, IC95 **[1.025, 4.153]**; mirada 1 mediana **480 → 2026-11-27**,
IC95 [256, 1.038]; análisis final mediana **2027-08-20**, entre 2027-03-09 y
2028-10-05. **P(mirada 1 ya vencida, si se firma la regla del punto
derivado) = 0.0614, Wilson [0.0569, 0.0663].**

**El abanico CONDICIONAL** —no es un intervalo; sus bordes caen FUERA del
honesto— que responde «si firmo ESTE número, ¿cuándo mira el plan?»:

| Si se firma | qué es (CONDICIONAL) | `N_max` | mirada 1 | mirada 2 | mirada 3 | final |
|---|---|---|---|---|---|---|
| 4.94 pp | borde inferior del IC del MDE | 5.836 | 2027-05-27 | 2028-02-22 | 2028-11-16 | 2029-08-14 |
| **8.51 pp** | **el punto** | **1.962** | **2026-11-30** | 2027-03-01 | 2027-05-31 | **2027-08-27** |
| 10.00 pp | elección de calendario | 1.419 | **2026-11-04** | 2027-01-08 | 2027-03-16 | 2027-05-20 |
| 11.09 pp | el MDE crítico (punto) | 1.152 | **YA VENCIDA** | 2026-12-15 | 2027-02-05 | 2027-03-31 |
| 13.09 pp | borde superior del IC del MDE | 825 | **YA VENCIDA** | 2026-11-16 | 2026-12-23 | 2027-01-29 |

**El hallazgo de este bloque, y es el que apura toda la corrida: el MDE
crítico es 11.09 pp como punto, IC95 [8.93, 12.81], y cae DENTRO del IC95
del MDE.** Por encima de ese
valor el n de la mirada 1 ya es menor que las 288 filas contadas, así que
el plan arrancaría con una mirada debida. **Ninguna mirada cae dentro de
una semana de hoy**, pero dos caen dentro de seis semanas y dos ya
vencieron: ésa es la urgencia real de la firma.

**Cómo se contó el ritmo, declarado.** Por conteo sobre
`cargar_poblacion()`, que devuelve las filas **sin columnas de resultado**;
sin `excluir_cero`, porque `gap_pct == 0` es una función de `gap_pct`. Es
por lo tanto un **techo** del n del plan, así que las fechas salen más
TEMPRANAS que las reales — la dirección correcta de equivocarse cuando lo
que está en juego es un plazo. El sesgo, medido donde sí se puede computar
(la ventana antecedente): **1.87 %**. Con y sin la regla de filas firmada
el conteo de la población es **el mismo, 288**: la regla no retira ninguna
fila ahí, porque todos sus pares son de feriado.

**Errata sobre el acta §107.1.** El conteo aproximado del chat daba **296**
filas al 22-oct y 7.79 por día hábil. La máquina da **288** y 7.579. La
diferencia son exactamente las **8 filas del 28-sep** que la regla de
conocibilidad retira (acta §90.1 d) y que el filtro del chat no aplicaba.
Manda la máquina.

**§A3.1.d, lo que el encargo manda dejar escrito sin elegir:** si se firma
un valor que no sale de la derivación —el 10 pp es el caso— **se declara
como elección de calendario y no como derivación de V6**. Y queda dicho que
el argumento accidental que defendía al 10 pp en la v5 («está por encima de
lo que V6 exige») **ya no vale**: hoy está por debajo del punto derivado.

## 5. Bloque C — la regla de deduplicación del estimador

**La pregunta no era la que el documento creía.** Hay dos reglas: la de
FILAS, **firmada el 1-sep** (actas §60 y §61), y la del ESTIMADOR, que es
la que falta. Implementada en `mirada.py` detrás de
`REGLA_DEDUP_ESTIMADOR = None`, con candado (`_guard_regla_estimador`) y
tests.

**Conteo por opción** (`tabla_firma.py --reglas`; ninguna ventaja, ningún
p, en ninguna de las dos ventanas):

| Opción | clúster | n población | clústeres | filas/día hábil | n antecedente | clústeres |
|---|---|---|---|---|---|---|
| `conservar_ambas` (lo de hoy) | `fecha` | 288 | 36 | 7.579 | 267 | 37 |
| `clusterizar_por_sesion_objetivo` | `sesion_objetivo` | 288 | **38** | 7.579 | 267 | 39 |
| `colapsar_el_par` = `keep_first` | `fecha` | **265** | 36 | **6.974** | 262 | 37 |
| `keep_last` | — | **PROHIBIDA** (acta §60) | — | — | — | — |

**Las dos columnas de `n` están SIN `excluir_cero`**, porque la convención es una función de `gap_pct` y
la población no se mira; conviene decirlo porque el 262 de la última fila **no es** el mismo 262 de la ventana
antecedente con `excluir_cero` y `conservar_ambas` — son dos recetas distintas que dan el mismo entero por
coincidencia. Receta de cada columna: población = emisión > 2026-08-31, regla de filas firmada, sin convención;
antecedente = emisión ≤ 2026-08-31 y sello ≤ 2026-09-02, regla de filas firmada, sin convención.


**Pares que apuntan a la misma sesión objetivo, contados en las dos
ventanas:**

| Ventana | filas en pares | grupos | sesiones objetivo | fechas de emisión |
|---|---|---|---|---|
| antecedente, antes de la regla de filas | 30 | 15 | 4 (31-jul, 5-ago, 12-ago, 18-ago) | 8 |
| antecedente, después de la regla de filas | 10 | 5 | 2 (12-ago, 18-ago) | 4 |
| **población** | **38** (13,2 %) | **15: 11 de DOS filas y 4 de CUATRO** | 5 (24-sep, 28-sep, 6-oct, 12-oct, 13-oct) | 10 |

**Cuatro hallazgos de este bloque:**

1. **El problema es MÁS GRANDE en la población que en la ventana
   antecedente**, y la regla de filas firmada no retira ninguna de las 38:
   son todos pares de feriado, las dos filas corresponden a su
   `available_at`. Es el hecho de la tarjeta §87 visto desde el estadístico.
2. **Las cinco opciones del encargo son CUATRO.** «Colapsar el par» y
   `keep="first"` son la misma operación: colapsar exige decir qué fila
   sobrevive, y la única que no elige por frescura es la más temprana. La
   otra lectura —agregar las dos filas— necesitaría una regla de empate
   para un acierto binario, o sea una convención nueva, y la convención
   está congelada (§A3.7 cláusula 4). El código comparte rama y lo dice, en
   vez de fingir dos.
3. **`clusterizar_por_sesion_objetivo` no «junta los pares»: reasigna todos
   los clústeres.** Fusiona los pares pero PARTE las fechas de emisión en
   que las bolsas no abren a la vez; el neto es **+2 clústeres**, no menos.
   Por conteo no se puede saber si sube o baja `V̂`. **Sobre datos
   sintéticos sí**, y se midió: con pares de contribución idéntica, `V̂` por
   sesión objetivo es **~2×** `V̂` por fecha de emisión. O sea que el
   clúster por fecha de emisión **subestima la varianza en un factor 2
   sobre los pares**, que es la queja del cuarto dictamen con número y en
   el único terreno donde se puede medir sin gastar α.
4. **Una corrección al cuarto dictamen.** Dice que los pares tienen
   «resultado idéntico». Es cierto del GAP y no tiene por qué serlo del
   ACIERTO: comparten `gap_pct` porque comparten sesión, pero se emitieron
   en días distintos y con predicciones distintas. Lo que McNemar puntúa es
   el acierto. **No se midió si difieren** —es una función del acierto— y
   queda como posibilidad lógica que la elección tiene que contemplar.

**La elección por principio y no por resultado.** Esta corrida **no
recomputó ni agregó ninguna ventaja ni ningún p por opción**. La v5 ya
publicó en su cabecera los dos p de `keep="first"` contra `keep="last"`
sobre la ventana antecedente, así que **están a la vista de quien firma**;
la tarjeta §91 lo declara y el `estadistico-adversario` dictamina qué
consecuencia tiene eso.

**Cruce declarado con §82.1 y §87** en la tarjeta: son decisiones
distintas. §82.1 decide si la regla de filas se aplica a las cifras vivas
publicadas (firmado el 18-oct que no); §87, qué hacer con las 16 filas de
días sin sesión de XNYS; §91, cómo agrupa los clústeres el estadístico del
pre-registro — y no mueve ninguna cifra publicada.

## 6. Bloque D — §A3.1.b con intervalos

**Las dos razones caen.** La razón 2 ya estaba retractada. La razón 1,
puesta a intervalo: tasa necesaria **54.1 % [53.2, 55.2]** contra tasa de
la baseline **54.2 % Wilson [48.1, 60.1]** — **los intervalos se superponen
y los puntos distan 0.1 pp**. La v5 la presentaba como una brecha de casi
cinco puntos; buena parte de esa brecha **era el cambio de denominador**:
el 59.7 % salía de la rama de filas derogada.

**Y un tercer hecho, que lo cazó el escáner de `test_epistemico.py` y no el
autor:** el Wilson de la baseline **contiene el 50 %**, o sea que en esta
ventana la baseline tampoco se distingue de una moneda. Eso no refuerza la
razón 1: la desarma más.

**Lo que no admite intervalo, y por qué.** El retorno de SMH es un camino
**realizado**, no una estimación de un retorno esperado: no hay parámetro
del que sea muestra, y ponerle intervalo supondría que la ventana es un
sorteo de un proceso estacionario, que es justo lo que la razón 1 niega.
**Pero hay un problema peor que la falta de intervalo:** el insumo se
descarga en vivo de Yahoo y **no está anclado**, así que la razón 1 **no se
puede pre-registrar**. Hoy da −8.47 % en 40 barras donde la v5 escribió
−5.18 % en 39, y **la causa está identificada, no supuesta**: (a)
`exchange_calendars` confirma que **40 es el número correcto** de sesiones
de XNYS entre el 3-jul y el 28-ago de 2026 (el viernes 3-jul no es sesión);
(b) **con 39 barras —las mismas 40 menos la última— el retorno da
−5.1795 %**, que es exactamente el −5.18 % de la v5, y la sesión que falta,
la del 28-ago, movió −3.47 %. **La fuente no revisó nada:** la v5 midió
cuando la última barra de su propia ventana todavía no había llegado, y
publicó, bajo la etiqueta del retorno de SMH en la ventana, un retorno al que le faltaba el último día
de la ventana. Es el modo de falla exacto de un insumo sin ancla: no hace
falta que el proveedor corrija nada, basta con correr el script antes de que
cierre el último día. Tarjeta **§94**.

**Lo que queda en pie, y alcanza:** el argumento **estructural**, que no
necesita ninguna medición — V6 compara contra el camino realizado de un
benchmark, así que la vara que impone depende de si SMH subió o bajó. Un
umbral que cambia según cómo le fue al benchmark no es un MDE. **La
conclusión de §A3.1.b sobrevive; la evidencia que la sostenía, no.**

## 7. Bloque E — lo que la v5 dejó abierto

**E.1 Potencia.** 0.8000 idealizada contra **0.7537** con la regla del
máximo: **4.6 pp** de pérdida, no los ~1.7 que la v5 declaraba. Y el costo
de la otra salida, también en cifra: recuperar 0.80 exige ×1.12 sobre
`N_max`, o **+235 filas** con el MDE del punto (1.962 → 2.197), **31 días
hábiles**, final de 2027-08-27 a **2027-10-11**. Tarjeta **§92**.

**E.2 Exposición de la población.** Censo leído del CÓDIGO en §A3.8 del
documento y en la tarjeta **§93**. Resumen: **nadie computó el estadístico**
—`GEMELO/SECUENCIAL/miradas/` no existe, ninguna acta registra una mirada,
y el candado del MDE habría abortado— pero la API publica **fila por fila
`Gap real %` y `Acierto gap` de las 100 verificaciones más recientes**, hoy
todas de la población. Con esas dos columnas y la fecha, **b, c, los
clústeres de día, `V̂` y `Z` son reconstruibles** sobre ese subconjunto.
Sobre el resto de la población no: `evolucion` publica el acierto del
modelo por fecha pero no el de la baseline. La ventaja y el McNemar que la
API sí sirve (`/api/rieles`) están anclados a la **ventana antecedente**.
Lo que se destruye no es el α —nadie aplicó la regla de decisión— sino la
**verificabilidad** de «nadie miró». El adversario dictamina si eso admite
un número.

**E.3 Aviso por conteo.** Propuesto y **no instalado**, tarjeta **§95**: un
script de solo lectura que imprime filas contadas, n de la próxima mirada y
días hábiles que faltan, leyendo por `cargar_poblacion()` (sin columnas de
resultado, así que no puede computar un resultado ni por error). La forma
recomendada es **una línea en `./mki estado`**: cero jobs nuevos, cero
timers, **sin tocar el vigía**, que el encargo prohíbe.

## 8. Bloque F — la versión 6, y Bloque G — el quinto dictamen

La v6 está escrita con **corrección en su sitio** y **registro de cambios
en tabla de 25 filas** (F1 a F25) al final del documento, más el **acta de
congelamiento como plantilla** —cada parámetro de Nicolás como SIN FIRMAR
con su tarjeta— y la **receta de congelamiento**, que no se ejecuta.
**Ninguna línea del documento dice «congelado»** sobre el pre-registro; se
corrigió incluso un «se congela 1.485» que sobrevivía en el registro de la
v3.

El quinto dictamen del `estadistico-adversario` y la revisión del
`curador-epistemico` están en §10.

## 9. Cierre: huellas, aplicación y suites

**Las tres bases, sha256 al abrir (17:43:47):**

| Base | sha256 |
|---|---|
| `senales.db` | `80cd6882c6bad9fa8989a4f062e63fb9ef5cdfd1165dbe19f9ed3f793d9b603b` |
| `noticias.db` | `36a96c36f81262ebcfe41a0659101dad3aeefd23378fada15eab3bf94817fb3e` |
| `dinero/sello_dinero.db` | `7900d28f48a0b243586f60ba22e35dd5f9ad880fb8b28b874a69a75d2841844e` |

### 9.1 Nota de método sobre el `DECISIONES.md` del worktree

El worktree se creó sobre HEAD, que **no incluye el acta §107** (Nicolás la
anexó sin commitear). Por eso el acta §108 se anexó **directamente al
`DECISIONES.md` del árbol real** y el del worktree **no se copió nunca**:
copiarlo habría borrado §107. Queda escrito porque es el tipo de pérdida
silenciosa que un worktree invita a cometer.

### 9.2 Aplicación al árbol real, huellas de cierre y suites

| Hora (`date`) | Qué |
|---|---|
| **19:30:06** | **CORTE DE MÉTODO**, leído con `date` inmediatamente antes de copiar. Catorce archivos del worktree al árbol real; `DECISIONES.md` del worktree **NO** se copió (§9.1) |
| 19:30:06 | fin de la copia |
| 19:30:1x | acta §108 anexada al `DECISIONES.md` del árbol real. Verificado después: §107 sigue presente (1 aparición), §108 es la última |
| 19:30:20 → *(ver abajo)* | suite completa del árbol real, con las tres bases |
| 19:30:3x | `venv/bin/python tests/test_motor.py`: **todas las funciones del motor pasan el test de no-contaminación**, en las dos fechas de prueba |
| 19:30:5x | enlace simbólico a `senales.db` retirado del worktree con `unlink` |

**Huellas sha256 de las tres bases, AL CERRAR** (19:30:56), contra las de la
apertura (17:43:47):

| Base | sha256 al cerrar | ¿idéntica? |
|---|---|---|
| `senales.db` | `80cd6882c6bad9fa8989a4f062e63fb9ef5cdfd1165dbe19f9ed3f793d9b603b` | **SÍ** |
| `noticias.db` | `36a96c36f81262ebcfe41a0659101dad3aeefd23378fada15eab3bf94817fb3e` | **SÍ** |
| `dinero/sello_dinero.db` | `7900d28f48a0b243586f60ba22e35dd5f9ad880fb8b28b874a69a75d2841844e` | **SÍ** |

**Las tres idénticas: esta corrida no escribió en ninguna base.** Hay además
un control intermedio a las 18:46:21, también idéntico, tomado mientras el
enlace simbólico estaba puesto.

**Los diez archivos intocables, verificados byte a byte contra HEAD con
`git diff --quiet HEAD --`:** `motor.py`, `senales.py`, `snapshot.py`,
`universo.py`, `alertas.py`, `backtest/linea_base.py`, `app.py`,
`mki_backup.py`, `mki_vigia.py` y `cifras.py`. **Los diez sin cambios.**

**Suite completa del árbol real al cerrar (19:30:20 → 19:38:29, 488,21 s):**

> **1252 passed, 5 skipped, 1 xfailed, 0 failed.**

**Y la contabilidad del delta cierra al entero**, que es lo que hace esta
suite informativa en vez de decorativa:

| | |
|---|---|
| al abrir (17:43:52 → 17:51:09, 436,21 s) | 1225 passed, 5 skipped, 1 xfailed, 0 failed |
| al cerrar (19:30:20 → 19:38:29) | **1252** passed, 5 skipped, 1 xfailed, 0 failed |
| **tras las correcciones del guardián** (20:32:41 → 20:46:21, 820,85 s) | **1252** passed, 5 skipped, 1 xfailed, **0 failed** |
| delta | **+27 passed**, 0 en saltados, 0 en xfail, **0 rojos** |
| `tests/test_secuencial_17.py` aporta | **27 tests** (`--collect-only`) |

**1225 + 27 = 1252 exacto.** O sea que el archivo nuevo explica el delta
entero y **ningún test preexistente cambió de resultado** — ni los seis de
`tests/test_secuencial.py` que esta corrida modificó (43 tests antes y
después), ni los de `test_epistemico.py` que barren los documentos. Los 5
saltados son los mismos (§91 no se invoca) y el xfail es el mismo.

**El patrón de la medianoche (§107.2) no apareció y no podía:** las dos
suites empezaron y terminaron la misma tarde, lejos de las 00:00.

## 10. Dictámenes: los DOS rechazaron, y los dos tenían razón

### 10.1 `curador-epistemico` — RECHAZADO, 12 bloqueantes, todos atendidos

Sobre la **primera redacción** de la v6. 482 oraciones de prosa y 212 filas
de tabla barridas; 54 afirmaciones con etiqueta ausente o incorrecta, 25
bloqueantes en 12 hallazgos. Dictamen completo y tabla de atención en
`GEMELO/resultados/dictamen_17/curador_epistemico.md`.

Los tres que más valieron: **B11** (el MDE crítico publicado como punto
cuando el documento tenía el intervalo de `f` en la mano — pasa a 11.09 pp
[8.93, 12.81]); **B12** (las tres frases que prohibían la palabra
«congelado» eran falsas: cuatro líneas la predicaban del propio
pre-registro); y **B6** (el comentario de `mirada.py` pegado a la constante
que recibe la firma ofrecía una cifra retirada). Tres de los doce (B3, B4,
B5) ya estaban arreglados cuando el dictamen llegó: el curador leyó mientras
la corrida ponía las marcas de retiro en su sitio.

### 10.2 `estadistico-adversario` — **RECHAZADO. Quinto rechazo.**

977 líneas, en `dictamen_17/estadistico_adversario.md`. **Las cuatro
condiciones del cuarto dictamen están atendidas «de verdad y no
maquilladas»** y el documento «reproduce el día que se firma», que era la
vara textual. **El rechazo no viene de ellas.** Viene de tres defectos que
esta corrida no buscaba:

- **D1.** El documento declaraba congelado un estadístico cuyo **clúster
  está sin firmar**, y la opción que él mismo recomienda (§91) cambia la
  clave del clúster. Firmarla dejaría falso un párrafo congelado e
  invalidaría la tabla de exposición residual y con ella **la banda
  [0.046, 0.079]**, el único ítem que los dictámenes 3 y 4 dejaron
  bloqueante. **Es la razón formal del rechazo**, y no es un número que no
  reproduce: es una incompatibilidad entre lo congelado y lo que se firma.
- **D2.** **`p_d` y `f` son la MISMA cantidad** (verificado a 17 decimales
  sobre las 262 filas; `b+c` = 129 = exactamente las filas BAJA), y el
  abanico metía los bordes del IC del MDE en Connor con `p_d` fija en su
  punto: **réplicas distintas del mismo remuestreo**, con los dos extremos
  del documento cayendo FUERA del intervalo honesto.
- **D3.** **20 de 37 fechas aportan `d_j` = 0 exacto** (`f` por fecha es
  perfectamente degenerado: 19 con 0, 18 con 1, ninguna intermedia), así que
  la mirada 1 descansa en ~25 fechas informativas y no en ~51 — y
  `secuencial_v5.md` **ya lo había medido el 2-sep** en una línea que
  ninguna versión del documento citó.

**Lo que el adversario intentó romper y AGUANTÓ**, dicho con la misma
firmeza: el techo del conteo sin `excluir_cero` y su dirección; el ancla y
su candado (verificó que no existe la fila que podría dispararlo); el DEFF
de planificación (V̂ máximo **3.618** contra 3.6 supuesto); y el error
estándar de Bartlett para `ac1`, donde **su hipótesis era la equivocada**:
corrió 20.000 réplicas bajo H₀ con el patrón de ceros real y el EE verdadero
es **0.142** contra 0.164, o sea que Bartlett es **conservador** por 1.16.

**Conteo de intentos:** el adversario declara su propia mirada —computó `b`
y `c` por separado sobre la ventana antecedente para verificar la identidad
de D2, sin publicar `b−c` ni su p— y suma **4 intentos: 354 → 358**.

### 10.3 Qué se atendió de las once exigencias

Tabla completa en el documento, al final. Resumen: **ATENDIDAS** E2, E8, E9,
E10, E11 y las partes declarativas de E1, E3, E4 y E5. **NO ATENDIDAS** E6
(poner número al pasivo) y E7 (validar los tres estimadores contra verdad
conocida), más las piezas de E1 y E3 que caen en la misma corrida de
simulación. Las dos están en tarjetas nuevas, **§96** y **§97**, con su
costo y con la recomendación de hacer §97 **antes** del congelamiento.

**Lo que esta corrida cambió por el dictamen y conviene leer con atención:**
la recomendación de la tarjeta **§93 pasó de (a) a (b)**. Con el α del plan
medido en el orden de **0.12–0.14** bajo la opción (a), elegirla sin la
cifra sería hacer por omisión lo que el proyecto rechazó por decisión el
31-ago, cuando descartó subir el α a 0.10 por considerarlo un cambio de
estándar científico.

### 10.4 El re-dictamen

El encargo manda repetir el dictamen una vez. Se le pidió al MISMO agente
—contexto intacto— un **delta** sobre las exigencias atendidas, en vez de un
dictamen nuevo: qué atención es real y qué es cosmética, si alguna
corrección introdujo un defecto nuevo, y si el documento describe su propio
estado con honestidad. Resultado en
`dictamen_17/re_dictamen.md`.

## 10.5 El dictamen de cierre del `guardian-constitucion`: OBSERVADO, y lo que cazó

**Veredicto: OBSERVADO.** Ninguna regla dura roto —los trece intocables byte
a byte (agregó `version.py`, `calendarios.py` y `noticias.py` a los diez que
yo había verificado), ningún `UPDATE`/`DELETE`/`INSERT`/`to_sql` en las 2.529
líneas nuevas, sin push, `main`, sin secretos, timers sin tocar, los dos
candados abortando **verificados por ejecución**, y la amputación de
`cargar_poblacion()` enumerada columna por columna: las doce que sobreviven
son todas del lado de la predicción. **Siete observaciones**, las tres
primeras sobre el papel desde el que Nicolás firma. **Las siete corregidas en
su sitio antes del commit** — la frontera de la errata es el commit.

**O-1 es la que importa, y es el defecto de esta corrida cometido por la
corrección que lo arreglaba.** Al computar el factor secuencial (N3 del
re-dictamen) lo arreglé en `tabla_firma.py` y **no en `mirada._n_max`**, que
seguía multiplicando por el `1.0241` cableado. Resultado medido por el
guardián: **el n que dispara la mirada 1 a 10 pp era 354 si se le preguntaba
a `mirada.py` —el script que CORRE la mirada— y 355 si se le preguntaba a
`tabla_firma.py` —la tabla que se FIRMA**. Dos generaciones de `N_max` vivas
a la vez, repartidas en once lugares. Es textualmente la vara del cuarto
dictamen, fallando sobre la cantidad de la que depende la firma.

**Cómo quedó cerrado, y no con un reemplazo de cifras:** el factor vive ahora
en **un solo lugar** (`diseno_secuencial.factor_secuencial` y
`n_max_del_plan`), los dos consumidores delegan, y hay un **test que recorre
cuatro MDE y exige que `mirada.py` y `tabla_firma.py` den el MISMO `N_max`** —
si el factor vuelve a vivir en dos sitios, la suite se entera. Todos los
documentos quedaron en una sola generación; el barrido está abajo.

| # | Qué cazó | Qué se hizo |
|---|---|---|
| **O-1** | dos generaciones de `N_max` en once lugares, incluido el ejecutable | factor en un solo lugar, los dos delegan, test que prohíbe la divergencia, y todos los documentos en una generación |
| **O-2** | el bloqueante B11 del curador registrado como atendido en cuatro copias y atendido en dos: la tarjeta y la bitácora publicaban el crítico como punto desnudo | el IC [8.93, 12.81] en las **cuatro**, y la fila del dictamen del curador corregida con su errata a la vista |
| **O-3** | la corrida retiraba cifras y no agregaba una fila al registro; la tarjeta §90 imprimía la fecha artefacto en negrita **y argumentaba desde ella** | fila nueva en `GEMELO/cifras_retiradas.md`, marca en su sitio, y el argumento de la tarjeta rehecho |
| **O-4** | el registro de intentos subió en prosa y no en la máquina, y el acta lo daba por hecho | declarado **PENDIENTE** en el acta §108.2-ter y §108.16, con el orden invertido y la razón de no aplicarlo ahora |
| **O-5** | el acta no declaraba el enlace simbólico; la bitácora sí | declarado en el acta §108.2: es decisión de método y va ahí |
| **O-6** | §108.13 decía «seis tarjetas» y §108.15 «ocho» | ocho en las dos |
| **O-7** | `mirada.py` citaba «15 de dos» para la ventana antecedente, que es la rama que D1 derogó, sin decirlo | corregido: **5 grupos de dos** bajo la regla firmada, con la rama derogada nombrada como tal |

**Un defecto que la corrección de O-1 introdujo y que cazó la suite, no un
agente.** Poner el factor en un solo lugar hizo que `n_max_del_plan` lo
computara **en cada llamada**, y `propagacion_conjunta` computa un `N_max`
por cada una de las 10.000 réplicas: una llamada cuesta ~6,4 s (bisección de
60 pasos sobre una integración de 2.001 puntos), o sea **unas 18 horas**. La
suite se colgó al 68 % y hubo que matarla. Memoizado con
`functools.lru_cache(maxsize=1)`: 3,4 s la primera llamada y 0,001 s las
10.000 siguientes, con `N_max` idéntico. **Se puede memoizar porque la
función es pura y sus insumos son constantes del pre-registro**: si alguna
cambiara, el diseño terminó y hay que decirlo con acta (§A3.7), no recomputar
el factor a mitad de un proceso. Queda dicho porque una corrección que arregla
la corrección anterior es exactamente lo que esta corrida viene registrando.

**Lo que el guardián dejó como NO VERIFICADO**, y queda como tal: el 12 % de
inflación de `V̂` (necesita la corrida de §92), E6 y E7 (no están), y la tabla
de exposición residual (20.000 réplicas). Y una lectura de la regla 10 que
es de Nicolás: qué hacer con cifras que una corrida declara retiradas en
prosa sin agregarlas al registro. Esta corrida agregó la fila de la fecha
artefacto y **no** la del factor, con su razón escrita en el acta §108.16.

## 11. Lo que Nicolás tiene que firmar, en orden de urgencia

| # | Tarjeta | Qué decide | Deja de poder tomarse sin costo el… |
|---|---|---|---|
| 1 | **§90 — el MDE** | el único parámetro del que dependen `N_max` y todo el calendario | **2026-11-04** si quiere el valor de calendario (10 pp); **2026-11-30** si quiere el punto derivado (8.51 pp). **Por encima del MDE crítico —11.09 pp como punto, IC95 [8.93, 12.81]— ya está vencido hoy**, y el crítico sube cada día hábil que pasa |
| 2 | **§91 — la regla del estimador** | cómo agrupa los clústeres el estadístico; mueve `V̂`, que es el denominador del veredicto | **antes de la primera mirada** que fije §90 (la más temprana posible, 2026-11-04). Si §90 sale por encima del MDE crítico, **hoy** |
| 3 | **§93 — la población** | si cuenta desde el 2026-09-01 con la exposición declarada, o si empieza al congelar | **antes de la primera mirada**. Cada día hábil que pasa agrega ~7.6 filas a la población expuesta, así que la opción (b) se encarece sola |
| 4 | **§92 — la potencia** | declarar 0.7537 o pagar +235 filas y 31 días hábiles | **antes de la primera mirada**, porque la salida 1 mueve `N_max` y con él las cuatro fechas |
| 5 | **§97 — validar los estimadores** | correr el `Z` del plan, la cobertura del IC del MDE y la equivalencia con §61 contra verdad conocida; y recomputar la tabla de exposición para la clave por sesión objetivo | **antes del congelamiento**, y antes que §91: sin la pieza de E1, firmar la opción que §91 recomienda **invalida la banda [0.046, 0.079]** |
| 6 | **§95 — el aviso por conteo** | dónde se ve el contador que avisa que una mirada vence | sin plazo formal, pero **su utilidad vence con la primera mirada**: un aviso que llega después de la fecha no avisa nada |
| 7 | **§96 — el pasivo con número** | computar P(al menos un cruce), o escribir la línea del acta como «α ≥ 0.09, sin extremo superior establecido» | **sin plazo** para el número; la línea del acta, antes de firmar, porque el acta no puede congelar como rango algo declarado incompleto |
| 8 | **§94 — la serie de SMH** | sellar el insumo de la razón 1 o bajarle el estatus | **sin plazo**: no bloquea el congelamiento. Sólo vuelve a importar si alguna vez V6 se usa para fijar un umbral |

**Las cuatro primeras bloquean el congelamiento. La §97 no lo bloquea
formalmente pero lo condiciona:** es la que convierte la banda y los
umbrales de declarados en medidos, y la que puede descubrir que la regla del
máximo no se justifica en esta ventana. El quinto dictamen la recomienda
antes del congelamiento, y esta bitácora también.

**Y una cosa que ya no es una tarjeta sino un hecho que conviene leer antes
de firmar dos años de calendario** (observación final del quinto dictamen,
no exigencia): D2 y D3 no son objeciones al plan, son la **descripción del
experimento**. La pregunta direccional se juega **sólo en las noches en que
el SOX baja y el modelo dice BAJA**; en las otras el campeón y la baseline
son la misma cosa por construcción. Un diseño secuencial sobre la dirección
es, a este ritmo, **un diseño sobre la mitad de sus propias fechas**.

## 12. Rutas para el commit

Una por línea. **Sin `data/`**: esta corrida no tocó nada ahí, y lo de
`data/` que aparece modificado en el árbol es del backup diario y de la
sonda, que los commitea su propio job.

```
DECISIONES.md
GEMELO/cifras_retiradas.md
GEMELO/SECUENCIAL/DISEÑO.md
GEMELO/SECUENCIAL/diseno_secuencial.py
GEMELO/SECUENCIAL/mde_desde_v6.py
GEMELO/SECUENCIAL/mirada.py
GEMELO/SECUENCIAL/tabla_firma.py
GEMELO/SECUENCIAL/ventana_antecedente.py
GEMELO/resultados/bitacora_17.md
GEMELO/resultados/dictamen_17/curador_epistemico.md
GEMELO/resultados/dictamen_17/estadistico_adversario.md
GEMELO/resultados/dictamen_17/re_dictamen.md
GEMELO/resultados/espera_firma.md
GEMELO/resultados/tabla_firma_17.json
tests/test_secuencial.py
tests/test_secuencial_17.py
```

**Lo que NO entra, y por qué:** `data/backups/sello_dinero.csv`,
`data/sonda_cierre.csv` y `data/backups/sello_dinero_ext/ext_2026-10-23.*`
estaban modificados o sin seguimiento **al abrir** la corrida y son de los
jobs del riel, no de acá.

**Errata 25-nov-2026 (acta §109.4 (2)):** la frase sobre `data/` es falsa para `data/sonda_cierre.csv`; el backup no la commitea y entra a mano en un commit aparte (§105.3 (d)).
