# Bitácora 03 — tercera corrida autónoma, 31-ago-2026

Continuación de `bitacora_nocturna.md` (primera) y `bitacora_02.md`
(segunda). Una línea por hito, hora UTC.

**El punto de partida, presente todo el tiempo:** dos corridas de análisis
pesado sobre las mismas 248 filas selladas terminaron en "no se puede
decidir". Más estadística sobre los mismos datos da la misma respuesta.
Si en algún momento me descubro volviendo a analizar la ventana sellada
buscando que diga algo, eso se anota acá como la trampa que es.

- 18:55 UTC — Arranque. Árbol limpio, `HEAD=d85e3fc`, 5 commits sin
  pushear de las dos corridas anteriores, nada nuevo de Nicolás. Leídos
  el encabezado de corrección de `concentracion.md` y
  `cola_decisiones.md`. Despachado `orientador` con siete preguntas
  (pasivo de miradas al track record para el Frente A, ritmo de
  acumulación, resumen de RTL.md, el álgebra exacta de
  `prediccion_apertura_al` para el testbench, estado de las piezas de
  réplica, la contaminación point-in-time ya medida, y el estado del
  README frente a la concentración de julio).
- 18:58 UTC — Toolchain FPGA: `yosys`, `nextpnr-ice40`, `fpga-icestorm`,
  `iverilog` y `verilator` **existen en apt pero ninguno está
  instalado**, y `sudo` pide autenticación interactiva — no hay
  instalación system-wide posible desde el agente. Se intentará por vía
  sin root (OSS CAD Suite portable o extracción de .deb a `~/.local`).
- 19:05 UTC — Despachados en paralelo el Frente B (toolchain FPGA + RTL +
  testbench + síntesis real, agente `general-purpose`) y el Frente E
  (expediente point-in-time con investigación de proveedores). A ambos se
  les mandó después un mensaje con contexto que les ahorra trabajo: al de
  B, el álgebra exacta del modelo de referencia (`apertura_estimada_pct =
  beta × último_movimiento_no_cero_del_SOX`, sin intercepto, `motor.py:339`);
  al de E, el dato que cambia su eje — **la contaminación del 8.6% por
  revisión de Yahoo fue REFUTADA** por el WS4 (`auditoria_ws3.md:213-236`):
  era un artefacto del join, alineando por `sesion_objetivo` la
  coincidencia sube a 100% y la desviación a 0.00%. Lo que queda abierto
  es el sesgo de composición del universo, que datos PIT de precios no
  arreglan.
- 19:12 UTC — `orientador` completó. **A1 reconstruido: 12 miradas
  distintas a la ventaja de la ventana sellada, en 5 fechas, con 6 valores
  de n y 3 convenciones** — tabla completa con citas en el DISEÑO. Hueco
  declarado: entre el 26-jul (n=80) y el 25-ago (n=228) no hay registro de
  cuántas veces se miró el número intermedio, así que el pasivo real es
  ≥12, no exactamente 12.
- 19:20 UTC — **Frente A computado y escrito.** `GEMELO/SECUENCIAL/`
  con el script versionado (`diseno_secuencial.py`) y el pre-registro
  (`DISEÑO.md`). Resultados centrales:
  - **La inflación del pasivo: 0.091 de tasa de error real usando α=0.05
    nominal en cada una de las 12 miradas — ~1.8× el nominal.** Pero el
    p más chico jamás observado en la ventana sellada es 0.1158, así que
    **la inflación nunca produjo un falso positivo porque nunca hubo un
    positivo**: el pasivo es prospectivo, no retrospectivo. Eso se dice
    explícito en el documento.
  - Menú de MDE con su costo en calendario: +15.66pp → ene-2027; **+10pp
    (propuesto) → jul-2027**; +6.45pp → sep-2028; +5pp (el umbral de
    RELEVO.md) → feb-2030; +3pp → mar-2036. La elección del MDE queda
    marcada como decisión de Nicolás: cambia el horizonte por un factor
    de ocho.
  - Fronteras por Monte Carlo (200k réplicas, semilla declarada, con
    verificación independiente en otra semilla: ambas familias dan 0.051
    de tasa global, que es lo que prueba que están bien construidas).
    **Se elige O'Brien-Fleming**: llega al análisis final con α=0.0441
    (casi el nominal completo) contra 0.0186 de Pocock, y el escenario
    más probable dado lo que se sabe es que el efecto, si existe, se
    resuelva recién al final.
  - Cuatro miradas con fecha escrita: 2026-11-17, 2027-02-03,
    2027-04-22, y la final **2027-07-09**. Con regla de gobernanza
    explícita: entre miradas no se computa el estadístico, y si alguien
    lo computa igual, cuenta como mirada y se registra.
  - Futilidad no vinculante por potencia condicional <20%.
  - Cinco cláusulas de "si el diseño se rompe", escritas antes.
  - **A4, el número desalentador computado:** responder la hipótesis
    CONDICIONAL cuesta k=2 → sep-2028, k=4 → jul-2031, k=6 → ago-2034.
    Con este ritmo de acumulación esa pregunta no es contestable por esta
    vía en un plazo humano. Se publica igual.
- 19:25 UTC — Despachado `estadistico-adversario` sobre el diseño
  secuencial (con el encargo explícito de recomputar las fronteras y
  contrastarlas contra los valores de referencia de la literatura para
  K=4 y α=0.05, revisar el ajuste por DEFF sobre el n de McNemar, y
  buscar por dónde se puede colar multiplicidad no declarada).
- 19:28 UTC — Despachado `ingeniero-plataforma` para el Frente D (ensayo
  general de la réplica en entorno aislado + runbook de activación con
  vuelta atrás).
- 19:35 UTC — **Frente C escrito**: `GEMELO/resultados/parche_honestidad.md`,
  que reemplaza explícitamente al `parche_documental.md` de la corrida
  anterior (aquel se apoyaba en el scan-statistic que después resultó
  mal construido). Contiene: el texto propuesto para la sección nueva del
  README ("Dónde vive esa ventaja"), **los doce bloques que se mueven,
  uno por uno con archivo:línea** (incluidos los tres archivos vivos de
  referencia — `cifras-canonicas`, `estadistica-evaluacion`,
  `estadistico-adversario.md` — sin los cuales la próxima sesión vuelve a
  citar +6.5pp sin el matiz), y el argumento sobre si R2 debe
  reformularse. Ese último punto es el más delicado: **la ventana
  15-23-jul de R2 se eligió post-hoc y el scan-statistic corregido no la
  establece como especial**, así que R2 congela como vara permanente una
  ventana que no está establecida — pero R2 solo descarta, nunca aprueba,
  y bajarla justo cuando se descubre que el campeón tampoco la pasa sería
  exactamente lo que un pre-registro existe para impedir. Las dos
  lecturas quedan escritas con su argumento; la decisión, marcada como de
  Nicolás. Despachado `escriba-decisiones` para el acta.
- 19:50 UTC — **Frente D completo.** `scripts/ensayo_replica.py` (script
  versionado y re-ejecutable), `data/replica_ensayo/reporte_ensayo.md`
  (la salida real), §6 y §7 nuevas en `docs/REPLICA.md`, y
  `docs/RUNBOOK_REPLICA.md` (8 pasos + sección 0 de decisiones
  bloqueantes + vuelta atrás por paso + qué NO hace el runbook). El
  ensayo pasó 8 fechas sintéticas por los tres casos: PARIDAD (0 filas
  de divergencia), DIVERGENCIA en sus cuatro sabores (cómputo por beta
  0.38 vs 0.41, insumos por `sox_fecha`, existencia por sello ausente,
  existencia por conjunto de tickers), y las dos formas de "una no selló"
  (DIA_NO_COMPUTABLE y PENDIENTE_PUBLICACION), ambas con **cero filas de
  divergencia falsas**. 7 filas registradas en total, todas con
  `resuelto_como IS NULL`. **Cero hallazgos**: las piezas se comportaron
  exactamente como estaban diseñadas. Nada activado, 329 tests en verde.
- 19:52 UTC — **Frente E completo**, y es el frente que más ahorra
  dinero de los cinco. `GEMELO/resultados/expediente_pit.md` (575
  líneas). Hallazgos:
  - **La contaminación por revisión de precios es CERO, no 8.6%** — el
    WS4 ya había demostrado que el 8.6% era un artefacto del join
    (`auditoria_ws3.md:213-236`); alineando por `sesion_objetivo` la
    desviación es 0.00% sobre 223 filas.
  - Y lo que sostiene la conclusión **no es la muestra, es un teorema**:
    el factor de ajuste escala `open(t)` y `close(t−1)` por igual, y el
    objetivo es un cociente — vale para las 14.618 filas, no solo para
    las 223 verificables. La verificación empírica confirma el teorema,
    no extrapola una tasa.
  - **Ninguna conclusión publicada depende críticamente del PIT de
    precios.** Para borrar los +15.66pp haría falta que el 15.7% de las
    filas estuvieran contaminadas a favor del modelo; la regla de tres
    sobre 0/223 acota en ≤1.35% — 11.6× de holgura.
  - Lo que sigue abierto es **otra cosa**: la composición del universo
    (sesgo de supervivencia), y **datos PIT de precios no la arreglan**.
  - Diez proveedores consultados con precio verificado (EODHD $19.99/mes,
    Sharadar $9-39, Tiingo $30, Norgate $270-787/año, Databento
    $199-4.500, LSEG/FactSet sin precio público). **Ninguno de los diez
    vende precios point-in-time de grado (a) para las cuatro bolsas, y
    ninguno vende constituyentes históricos del ^SOX.**
  - **Recomendación (marcada como tal): no comprar nada, cero dólares.**
    No porque sea caro: el problema medible está cerrado por un teorema y
    el problema abierto no está a la venta.
  - Tres hallazgos propios: (a) la frase "la contaminación va en la
    dirección optimista" de `ventana_larga.md:26` apunta al lado
    equivocado (ruido no correlacionado atenúa, no infla); (b) queda un
    canal residual sin medir: fechas ex de dividendos sobre la sesión
    objetivo (~0.9% de filas), medible gratis; (c) **una mina**:
    `GEMELO/ventana_larga.py:314-345` sigue emitiendo la cifra refutada y
    `tests/test_ventana_larga.py:186` la exige por test — re-correr el
    WS3 republicaría la falsedad.
- 20:05 UTC — **`estadistico-adversario` RECHAZÓ el diseño secuencial.**
  Ocho defectos, tres de ellos sobre números que el pre-registro iba a
  congelar. El de fondo, y la lección: **la v1 sacaba las fronteras de un
  Monte Carlo y las verificaba con el mismo generador en otra semilla.**
  Eso no detecta el sesgo del generador, solo lo vuelve a medir. La
  verificación interna daba 0.0507 y el documento lo leyó como
  confirmación de que la frontera estaba bien; era el sesgo mismo. El α
  real de las fronteras congeladas era **0.05122**, no 0.05.
- 20:40 UTC — **Diseño corregido y vuelto a congelar (v2).** Se escribió
  `GEMELO/SECUENCIAL/fronteras.py`: recursión de Armitage-McPherson por
  integración numérica, **sin Monte Carlo y sin semilla**, con validación
  contra **dos varas externas** (Jennison-Turnbull para fronteras;
  Armitage-McPherson-Rowe 1969 tabla 2 para el pasivo — son cómputos
  distintos y se validan por separado a propósito). Reproduce ambas
  tablas publicadas. Los ocho defectos, corregidos:
  - **D1** fronteras exactas **2.362** (Pocock) y **4.048 / 2.862 / 2.337
    / 2.024** (OBF), α global 0.04995.
  - **D2** la potencia real con N=1.450 es **0.7906**, no 0.80 (el umbral
    final del plan es 2.024, no el 1.96 de muestra fija). **N_max sube a
    1.485.** Publicadas las características operativas que faltaban:
    P(futilidad | H₀) = 0.853 y P(futilidad | H₁) = 0.083 — el canje, con
    sus dos números al lado.
  - **D3, el grave** — el DEFF ya no se congela dentro del estadístico. Se
    pre-registra la **fórmula**: `Z = [(b−c)/√(b+c)] / √V̂`, con V̂
    cluster-robusta re-estimada en cada mirada remuestreando FECHAS con
    `inferencia._remuestrear_circular`. Medido: con el DEFF congelado en
    3.6, si el verdadero fuera 4.6 el α real sería 0.088 y si fuera 7.26,
    0.193. Un α que se mueve entre 0.02 y 0.19 según un parámetro
    estimado a ojo no es un α controlado.
  - **D4** corregido el "nunca hubo un positivo": es cierto de la cifra
    principal (p mínimo 0.1158) y **falso de los subgrupos** — bloque
    0.001, Tokio 0.021, Seúl 0.031, los tres retractados. Ese es el falso
    positivo que la inflación no declarada predice, y ya ocurrió.
  - **D5** el pasivo es un **rango, no un número**: piso 0.0905 con solo
    lo reconstruido, techo 0.1779 poblando el hueco 26-jul/25-ago (que es
    el tramo que MÁS infla, por estar menos correlacionado con hoy).
    **α ∈ [0.09, 0.18], 1.8× a 3.6× el nominal.** Citar solo el piso
    habría sido el mismo error que el documento reprocha.
  - **D6** §A4 publica **tres** precios para tres preguntas: interacción
    5.799 filas (ene-2030), el de la v1 3.513 (sep-2028, y **supone
    efecto homogéneo, que es la nula de la pregunta condicional**), y
    concentración total 864 (mar-2027).
  - **D7** las 248 filas no entran en el estadístico ni en la decisión,
    pero sí como **tres parámetros de estorbo** (p_d, DEFF, ritmo). Decir
    "no se usan ni como prior" y usarlas tres veces no se sostiene.
  - **D8** gobernanza con precio: **una sola mirada furtiva lleva el α de
    0.050 a 0.094** (dos → 0.121, tres → 0.137). Más tres reglas
    operativas, y la primera está cumplida: **`mirada.py` escrito hoy**,
    no en noviembre, con tres candados estructurales (descarta por
    construcción toda fila anterior al congelamiento — hoy descarta 253 y
    computa sobre 0; se niega a computar si faltan filas; `mode=ro`).
    22 tests nuevos en `tests/test_secuencial.py`, en verde.
  - Nota honesta: el revisor computó 0.7953 / ~1.520 y este repo computa
    0.7906 / 1.485, por dos caminos que coinciden en 0.0005. Diferencia
    de tercer decimal, misma conclusión. Se congela el del código
    versionado.
  - **La corrección se hizo en su sitio, no como errata fechada**: la v1
    nunca se commiteó ni salió del repo. La frontera de la errata es el
    commit. El §"Lo que la v1 decía mal" deja los ocho cambios en tabla
    para que la corrección sea auditable sin confiar en esta frase.
- 20:45 UTC — **Frente B completo** (agente `general-purpose`). Toolchain
  OSS CAD Suite portable en `~/.local/opt` **sin root**: yosys 0.68,
  nextpnr-ice40, icestorm, iverilog 14, verilator 5.051. `nextpnr-xilinx`
  NO está en el suite, así que **para Artix-7 no hay place & route ni
  Fmax** — se usó `yosys synth_xilinx -family xc7`, marcado como más
  blando que Vivado. RTL de cinco etapas en `micro/rtl/`: **181/181 filas
  selladas reales reproducidas bit a bit** en cuatro configuraciones, y
  **latencia de 32 ciclos idéntica en los 181 vectores** — la predicción
  falsable de `fpga.md` §2 sobrevivió (el banco marca fallo si min≠max);
  la cuenta a mano decía 33 y ganó el arnés. **Dos discrepancias contra
  `RTL.md`**: la tolerancia declarada de 0,00188 pp es inalcanzable
  (medido 0,00474; se derivó para la operación equivocada) y el §4.4
  afirma que la decisión discreta coincide 100% cuando **2 de 181 (1,1%)
  deciden distinto** — lo discreto es *más* frágil en la frontera, no
  inmune. **Veredicto de síntesis: el campeón NO cabe en la Go Board** —
  1.545 LCs contra 1.280 (120,7%). El error de estimación central: un
  multiplicador 16×16 con signo cuesta **774 LUT4, no 200-300**
  (descartada la explicación alternativa midiendo la variante de 8 bits:
  escala como W²). Aviso metodológico aparte: **sumar estimaciones por
  etapa subestima un 45%**, que es como `RTL.md` §2 construyó sus
  totales. Lo único que cabe es F1SP (solo umbral): 742/1.280 = 58,0%,
  Fmax 114,19 MHz (nextpnr) / 114,59 (icetime). En Artix-7: 1 DSP48E1 y 0,35% de LUTs. Bloqueos honestos:
  placa física, y **throughput espalda-con-espalda NO medido** (el banco
  inserta 8 ciclos de silencio para que la latencia sea limpia).
  Entregables: `micro/TOOLCHAIN.md`, `micro/rtl/`, `GEMELO/MICRO/SINTESIS.md`.
- 20:47 UTC — Despachado `estadistico-adversario` por SEGUNDA vez sobre
  el diseño ya corregido. Nota de gobernanza propia: **el rechazo vino
  del adversario estadístico, no del guardián.** La regla de "dos
  RECHAZADOS seguidos y se abandona" cuenta dictámenes del
  `guardian-constitucion`, que todavía no vio nada de esta tanda.
- 21:05 UTC — **`cola_decisiones.md` actualizada** y reordenada por costo
  de postergar. Cerró un ítem (datos point-in-time, con recomendación de
  cero dólares), se destrabó otro (la réplica: ya no falta ninguna pieza
  técnica, falta la firma), y abrieron tres: **el MDE del diseño
  secuencial** —que entra directo al puesto 2, porque a partir del
  2026-11-19 el costo de postergarla pasa a ser infinito: el diseño
  arranca con el MDE que esté escrito—, las dos afirmaciones refutadas de
  `RTL.md`, y la mina de `ventana_larga.py`. La elección de placa FPGA
  dejó de ser una estimación y pasó a tener síntesis real detrás.
- 21:10 UTC — **351 tests en verde** (329 de antes + 22 nuevos del
  secuencial). Árbol revisado: `micro/rtl/.gitignore` ya excluye `sim/` y
  `sintesis/`, así que de los ~140 MB de productos de síntesis se
  commitean **201 KB** de fuente y vectores. Es exactamente el defecto que
  el guardián marcó en la primera corrida (binarios de `micro/bin`), y esta
  vez vino prevenido de fábrica.
- 21:12 UTC — Despachado `escriba-decisiones` para las actas §47 a §51
  (secuencial, síntesis RTL, expediente PIT, ensayo de réplica, parche de
  honestidad). `DECISIONES.md` estaba sin tocar: el `escriba` despachado a
  las 19:35 para el acta del Frente C no llegó a escribir.
- 21:20 UTC — Verificadas una por una las citas `archivo:línea` de
  `parche_honestidad.md` contra el README vivo: las siete siguen exactas.
  Corregida la única cifra que la v2 del secuencial desplazó: la fecha del
  hito pasó de **2027-07-09 a 2027-07-17** (dos ocurrencias), porque N_max
  subió de 1.450 a 1.485 al arreglar la potencia. Las entradas de las
  19:20 de esta bitácora conservan las cifras de la v1 a propósito: son
  el registro de lo que se computó entonces, y la entrada de las 20:40
  es la que dice en qué se corrigieron.
- 21:35 UTC — **Actas §47 a §51 escritas** (505 líneas en `DECISIONES.md`):
  el diseño secuencial con su lección de método, la síntesis del RTL con
  las dos afirmaciones refutadas, el expediente PIT con la recomendación
  de cero dólares, el ensayo de réplica, y el parche de honestidad
  preparado y no aplicado. El `escriba` reportó dos verificaciones: el
  conteo de 22 tests cuadra (12 sueltos + 4 y 6 de dos parametrizados), y
  detectó las fechas viejas del secuencial dando vueltas. Corregida la
  nota que dejó: **no era una inconsistencia sin resolver.** El parche ya
  estaba corregido, y la bitácora conserva las fechas de la v1 a propósito
  — una bitácora que se reescribe hacia atrás deja de ser una bitácora.
  Eso quedó escrito en el acta §47.
- 22:10 UTC — **Segundo RECHAZO del `estadistico-adversario` sobre el
  diseño secuencial, y tiene razón.** Verificó los seis bloques por dos
  caminos propios (Gauss-Legendre y Monte Carlo de 4M) y confirmó D1, D2,
  D4, D5, D6, D7 y D8. Pero: **D3 no estaba corregido, estaba mudado.**
  Saqué el DEFF de adentro del estadístico y puse en su lugar un bootstrap
  que sortea FECHAS — que corrige la dependencia DENTRO de la fecha y es
  estructuralmente **ciego a la dependencia ENTRE fechas**. O sea: cambié
  un α que dependía de un DEFF supuesto por un α que depende de una
  autocorrelación supuesta. Es literalmente el argumento con el que este
  documento hundió a su propia v1.
  - Lo medí simulando el plan ENTERO bajo H0 (umbrales OBF por mirada, V̂
    re-estimada en cada una). Con bloque 1 solo: α = 0.054 / 0.086 / 0.138
    / 0.193 para ac1 = 0 / +0.10 / +0.20 / +0.30. **Peor de lo que el
    revisor estimó.**
  - Y medí la autocorrelación real sobre la ventana antecedente, como
    parámetro de estorbo de varianza (misma clase que p_d y el DEFF, ya
    declarada en §A2): **ac1 = −0.135 ± 0.171 sobre 34 fechas** —
    idéntico a lo que midió el revisor por su cuenta. El signo es benigno
    pero el EE dice que los datos **no distinguen 0 de +0.2**, así que
    "está medido y da negativo" no alcanza y no se usa como argumento.
  - **La corrección: `BLOQUES_FECHAS = (1, 5, 10)` y V̂ = el máximo.**
    Tomar el máximo solo puede inflar la varianza, o sea solo puede bajar
    el α. Medido: **0.048 / 0.057 / 0.072 / 0.080**. Corta la exposición
    ~60% en todos los niveles y **NO la elimina**. Con 53 fechas en la
    primera mirada eso no se arregla con un estimador mejor: es el límite
    del n, y va **declarado con su tabla** en §A3.2 en vez de escondido.
  - Hallazgo estructural que nadie diseñó a propósito: **la mirada donde
    V̂ es menos confiable (la 1, ~53 fechas) es la que tiene el umbral más
    alto (4.048)**. El conservadurismo temprano de O'Brien-Fleming y la
    debilidad del bootstrap están anti-correlacionados. Con 204 fechas la
    exposición residual prácticamente desaparece (α=0.058 aun a ac1=+0.30).
  - Los otros once (E2 a E12): §A3.2 ahora describe el código que existe
    y no otro; `N_DRAWS` 5.000 → **200.000** (la semilla congelada valía
    ±0.023 de Z sobre un umbral de 2.024); los **dos crashes** que el
    revisor reprodujo —`ZeroDivisionError` con varianza nula, y la rama
    degenerada que devolvía un dict sin las claves que se le leían, o sea
    la única rama que fallaba era la que existía para el caso raro—;
    **guard de `MODELO_VERSION`** (la cláusula 1 de A3.7 era prosa que el
    código no conocía); acta **append-only** y registro de toda corrida
    que compute, con o sin `--escribir`; aviso cuando el n excede al del
    plan; "TECHO" → "escenario alto" con el ancla en n=80 declarada (no
    hay techo finito: desde n=20 da 0.26); §A4 con sus tres supuestos
    escritos, la columna de α y el (c) re-etiquetado; y
    **`verificacion_mc`**, porque el documento afirmaba tener una
    verificación por Monte Carlo que no existía en el repo — el módulo
    declaraba `SEMILLA` y `N_SIM` sin usarlas.
- 22:20 UTC — **Contaminación propia, encontrada y arreglada.** Dos tests
  de veredicto escribieron en el registro de auditoría REAL del diseño
  (`GEMELO/SECUENCIAL/miradas/registro.log`), una de las líneas con
  "CRUZA LA FRONTERA". Es exactamente la clase de cosa que este diseño
  existe para impedir: el día que haya una mirada de verdad, nadie podría
  distinguir cuál línea es real. Borrado el log, y aislamiento por
  fixture `autouse` para que proteja también a los tests que alguien
  escriba después sin acordarse, más un test que verifica que la ruta real
  no tenga entradas sintéticas. **362 tests en verde** (33 del secuencial).
- 22:25 UTC — Hallazgo del revisor que NO se aplica y queda en la cola:
  `evaluacion.mcnemar_exact(72, 56)` devuelve **0.1847**, no el **0.1849**
  publicado en el README, en `cifras-canonicas` y siete veces en
  `DECISIONES.md` — se arrastró desde la medición de n=240. No cambia
  ninguna conclusión (0.18 sigue lejos de 0.05), pero **la regla del
  proyecto es que el módulo es el árbitro**. Cae bajo la regla de los doce
  bloques: lleva la firma de Nicolás, no la mía.
- 23:15 UTC — **TERCER RECHAZO, y acá cambio de estrategia.** El revisor
  verificó exactas las fronteras, el pasivo, Connor, la futilidad, el
  calendario y los tres candados. Lo que rompió fue **la única tabla nueva
  de la v3**, que era su razón de ser: no reproducía desde el script
  sembrado (7 de 8 celdas), publicaba cuatro decimales sobre **1.200
  réplicas** sin intervalos —dos corridas de la misma cantidad caían a
  ambos lados del nominal—, y la frase "corta ~60% en todos los niveles"
  estaba contradicha por su propia tabla.
  - Recomputada con **20.000 réplicas e IC de Wilson**: la reducción real
    es **17% / 29% / 44% / 55%**. Es 17% justo donde el proyecto midió que
    está la autocorrelación, y 55% solo en el extremo. **Yo estaba citando
    el mejor caso como si fuera el promedio** — el mismo vicio que el
    documento le reprocha al proyecto en su §A1.
  - **N4, el que más duele:** la regla del máximo cuesta ~1,7 pp de
    potencia y la corrección de N_max que hice para D2 reparaba 0,94 pp.
    **El arreglo del estimador se come al doble el arreglo del tamaño de
    muestra.** Declarado, con sus dos salidas.
  - Los demás: `UNIVERSO_ESPERADO` congelado en "4.6.0" (una constante de
    pre-registro que "se completa después" no está congelada y su guard es
    código muerto); las **cinco cifras sin fuente en el repo** computadas o
    retiradas —una de ellas la imprimía el acta, o sea el día de la mirada
    iba a citar una medición inexistente—; `FECHAS_POR_MIRADA` sale ahora
    del calendario y no "a ojo" (el redondeo iba en dirección optimista);
    cinco comentarios rancios; y **cuatro tests tautológicos reescritos**
    como tests de comportamiento —el de append-only nunca ejercitaba la
    rama que decía proteger— más cuatro nuevos sobre la simulación, que
    era el único cómputo sin vara externa y sin test. 40 tests.
- 23:20 UTC — **El documento NO se congela, y eso es el resultado, no una
  tarea pendiente.** El defecto de fondo del tercer rechazo no es ninguno
  de los ocho: es que el plan declara α = 0.05, publica al lado que
  entrega hasta 0.079, y **no fija ninguna regla de decisión para ese
  caso**. Eso no es un criterio, es un descargo con promesa de criterio
  futuro — y un criterio decidido después de ver datos es exactamente lo
  que un pre-registro existe para prohibir.
  - La salida que recomienda el revisor, y que comparto, es **declarar
    α = 0.10 y mover la primera mirada a ~100 fechas**. Pero eso **cambia
    el estándar científico con el que el proyecto va a juzgar su propio
    modelo**, y es de la misma clase que el MDE: decisión de Nicolás.
    Costeada y escrita al principio del DISEÑO y en `cola_decisiones.md`
    §2a, que pasa a ser la decisión bloqueante.
  - Nota de gobernanza: la regla del encargo ("dos RECHAZADOS seguidos y
    se abandona") cuenta dictámenes del `guardian-constitucion`. Estos tres
    son del adversario estadístico, y el propio revisor recomendó
    **corregir, no abandonar**, con el argumento de que la superficie rota
    se achicó en cada ronda: v1 las fronteras, v2 el estimador, v3 una
    tabla de ocho celdas. Es convergencia, no deriva. Aun así **paro acá**:
    lo que queda no es un defecto que se pueda corregir sin tomar una
    decisión que no me corresponde.
- 23:40 UTC — **Dictamen del `guardian-constitucion`: OBSERVADO, ningún
  rechazo.** Verificó en verde lo que importa: los once módulos de la ruta
  de sellado **idénticos a HEAD** uno por uno, el anti-look-ahead del motor
  corrido a mano, cero escrituras a filas selladas, `DECISIONES.md` como
  **append puro** (623 inserciones, 0 borrados), todas las lecturas en
  `mode=ro`, ningún push, los cinco frentes con acta, README y `.claude/`
  intactos, y **0,70 MB de 143 MB** entrando al repo desde `micro/rtl/`.
  Confirmó por su cuenta el hallazgo del McNemar (0,1847) y lo llamó "R9
  bien ejecutado" por NO haberlo aplicado.
  - Tres observaciones, las tres atendidas: (1) había visto **dos fallos
    intermitentes** en `test_backtest` y `test_api` — corrí la suite
    completa **tres veces seguidas en verde** y los dos tests señalados
    **5/5**, con el sello de las 18:15 ya terminado y ningún job vivo: la
    correlación era con la concurrencia del job, no contaminación entre
    tests; (2) faltaba **declarar la asimetría del toolchain FPGA** —
    escrita en el acta §48, con la decisión de NO igualarla y su condición
    de retiro; (3) los **8 CSV de `data/backups/`** son del job de las
    18:15 y no de la tanda — quedaron fuera del commit por pathspec
    explícito, que es su carril.
  - Lo que NO se toca: `.env` está en **644** y la regla pide 600. Es
    operación de Nicolás y va por su carril; queda en `ESTADO.md`.
- 23:50 UTC — **Commit `09054cb`**, 45 archivos, con el hook corriendo la
  suite (369 en verde). **Nada pusheado**: `git push origin main` es de
  Nicolás. `ESTADO.md` regenerado.

---

## Handoff

**Qué quedó hecho.** Cinco frentes cerrados con expediente: el diseño
secuencial (terminado en su aritmética, tres rechazos adversarios
corregidos), la síntesis RTL real —que mató la hipótesis de que el campeón
entra en la Go Board—, el expediente point-in-time con recomendación de
cero dólares, el ensayo general de la réplica con cero hallazgos, y el
parche de honestidad preparado. Actas §47-§51, `cola_decisiones.md`
reordenada, commit `09054cb` sin pushear.

**Qué quedó a medias, y a propósito.** El pre-registro secuencial **no se
congeló**. No es una tarea pendiente: es que lo que falta ya no es un
defecto corregible sin tomar una decisión que no me corresponde. El plan
promete α=0.05 y entrega entre 0.046 y 0.079 según una autocorrelación que
34 fechas no alcanzan a acotar; la salida limpia es declarar α=0.10 y
mover la primera mirada a ~100 fechas, y eso cambia el estándar con el que
el proyecto va a juzgar su propio modelo.

**El siguiente paso concreto.** Nicolás revisa el diff y pushea. Después,
en este orden por costo de postergar: firmar la activación de la réplica
(§1 de la cola, la única cuyo costo de espera ya se materializó una vez), y
decidir α y MDE del secuencial (§2) **antes del 2026-11-19** — llegado ese
día, o el documento está congelado y la mirada vale, o no lo está y
cualquier cifra que se mire es una mirada más sin declarar.

**Lo que la corrida enseñó, y excede a este proyecto:** una verificación
que usa el mismo mecanismo que produjo la cifra no es una verificación.
Los tres rechazos del secuencial son la misma lección en tres capas —el
Monte Carlo validándose contra sí mismo, el estimador ciego al eje que no
remuestrea, y la tabla que citaba su mejor caso como si fuera el promedio.
