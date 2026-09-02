# Bitácora 07 — séptima corrida autónoma, 2-sep-2026

Continuación de `bitacora_06.md`. Una línea por hito, **con hora local
(Chile, UTC−4)**. Corrida nocturna, sin nadie esperando: se prefiere
profundidad sobre cobertura.

## Lo que gobierna esta corrida

Licencia creativa en el planteo, **ninguna** en lo que se afirma. Regla
quinta, vigente sólo esta noche: **todo lo nuevo se etiqueta PROPUESTA** y
no entra a cifra publicada, criterio congelado ni documento de resultados
sin pasar por `estadistico-adversario`. Si lo rechaza, se registra la
propuesta y el rechazo, y se sigue.

Límites que no se relajan: ninguna decisión de Nicolás se toma; motor,
senales, snapshot, universo, modo de emisión, `.env`, timers y `CLAUDE.md`
no se tocan; filas selladas no se reescriben; nada se pushea; regla de los
doce bloques; staging explícito por archivo; ventana 17:50–20:30 sin carga
pesada; dictamen del guardián antes de cerrar cada tanda.

## Las cuatro reglas de la casa

1. Una verificación con el mismo mecanismo que produjo la cifra **no es una
   verificación**.
2. Una retractación en prosa no es una retractación: **la corrección va al
   ejecutable**.
3. **Ningún estimador puntual sin intervalo**, y el intervalo se computa.
4. **Un número retirado que sigue ofrecido en el código vuelve a circular.**

## Hitos

- **01:40** — Arranque. `HEAD=a724ee3`, árbol limpio, modo `titular` según
  `modo.py`, 6 timers instalados. Fuera de la ventana de sellado. Leídos
  `ESTADO.md`, `bitacora_06.md`, `espera_firma.md` (812 líneas) y
  `cola_decisiones.md` (869 líneas).
- **01:42** — `orientador` despachado en segundo plano. Mientras trabaja,
  **Fase 0 (calibración)** sin abrir las actas que explican los tres
  defectos. Contaminación declarada de entrada: la lectura obligatoria
  (`cola_decisiones.md` §14) ya describe el defecto 2 casi entero.
- **01:43** — **Fase 0 cerrada. Resultado: 2 cazados solo, 1 con pista, 0 sin
  cazar.** Detalle, para que Nicolás sepa dónde soy fuerte y dónde no:
  - **Defecto 1 — cazado solo.** `backtest/datos.py:validar_sin_futuro`
    (versión `7182a5f`). El mecanismo: el llamador recortaba con
    `index.date <= fecha` y después le pedía a la guarda que comprobara
    `index.max() > fecha` sobre el frame ya recortado; la condición de
    disparo es inalcanzable por construcción. Lo deduje del llamador
    original en el commit; **la cifra (401.184 invocaciones) la da el
    docstring actual del código**, no la deduje yo. Vale como "solo"
    porque el docstring es código, no acta, pero lo declaro.
  - **Defecto 2 — con pista.** `GEMELO/control_lineal.py:inferencia_sharpe`
    tenía `n_intentos: int = N_INTENTOS_DECLARADO` (=9) en `da5e6e1` y
    `bd6d153`; `6bb1f46` lo quitó. La pista vino de la lectura obligatoria.
    **Cuantificación propia**, con `backtest/inferencia.sr0_deflacionado`:
    SR0 escala con √V, así que el cociente no depende de V:
    SR0(86)/SR0(9) = **1,63×** (a V=1: 1,52 → 2,48; a la V medida ≈0,43:
    0,9986 → 1,6266, Δ = 0,63 de umbral). Con N=97, SR0 = 1,655 a esa V.
    Un Sharpe anualizado entre 1,0 y 1,6 pasaba V5 con el default y no lo
    pasa con el N real. *(N=97 era el vigente a esa hora; a las 03:00 el
    registro pasó a 100 y el 5.1 a 106.)*
  - **Defecto 3 — cazado solo (con las dos cifras del enunciado como
    pista).** Reconstruido desde `senales.db` (`mode=ro`) y una descarga
    fresca de `^SOX`: producción selló `sox_usado_pct = −3,47` el 28-ago y
    `+0,57` el 31-ago; el Yahoo de hoy **no tiene la barra del 28-ago** y
    da −2,92 para el 31 (retorno de dos días). El 3,49 del 31-ago sale
    directo (0,57 − (−2,92)). **La premisa falsa:** que el `ffill` del
    motor "rellenaría" el 28-ago con el cierre del 27 y produciría un
    movimiento 0,00, de donde la diferencia sería |−3,47 − 0| = 3,47.
    Es falsa por dos razones independientes: (i) `_precios_hasta` hace
    `.ffill()` sobre el índice que la fuente devuelve — **rellena celdas
    NaN, no crea fechas**; una sesión retirada de la fuente no deja fila
    que rellenar, y `_hasta(28-ago)` termina en el 27; (ii) aunque
    existiera una fila con 0,00, `ultimo_movimiento_no_cero()` la
    saltaría por diseño (Supuesto #1). Por las dos vías el motor al
    28-ago usa el **+2,33 del 27-ago**, y la diferencia real es
    |−3,47 − 2,33| = **5,80 pp**. Reproduce.
  - **Lectura sobre mí:** fuerte en reconstruir mecanismos desde el código
    y los datos; el riesgo está en que la lectura obligatoria me entrega
    respuestas ya digeridas y no siempre puedo separar lo que deduje de lo
    que leí. Lo declaro cada vez que pase.
- **01:50** — Plan de la noche fijado en la lista de tareas (A→G, Fase 4,
  cierre). `ingeniero-plataforma` despachado con la Fase 4 operativa
  (timeout de `mki-noticias` con evidencia histórica, parche preparado y NO
  aplicado; vigía «NO corrió» vs «corrió y no completó», con test).
  Instrucción explícita: no tocar timers instalados ni `systemd/`.
- **01:52** — **Frente A abierto.** Hallazgo de camino, antes de medir nada:
  `GEMELO/cache/` (gitignored) guarda **fotos involuntarias de la fuente**:
  dos paneles de 8 años con `mtime` 26-ago 04:22Z (8 y 27 tickers) y dos
  del 1-sep 13:07Z/13:16Z (37 series, con FX e índices). Son testigos de
  cómo servía Yahoo esos días. Nadie los había usado como tal.
  - Con ellos, la ventana en que desapareció la barra del 28-ago se
    **estrecha**: `docs/SEGUNDO_SELLO.md` la acotaba en ~18 h (31-ago
    22:15Z → 1-sep 16:12Z). La corrida del backtest `20260901-061708`
    (frozen source bajado antes de las 06:17Z) ya reconstruye el 28-ago
    con el signo dado vuelta, y las cachés de las 13:07Z tienen `^SOX`
    NaN ese día. **Ventana: ≤ 8 h, entre 22:15Z y 06:17Z.**
- **01:58** — `GEMELO/fuente_canonica.py` escrito: cinco testigos (M1
  cachés, M2 `sox_usado_pct`, M3 verificaciones, M4 emisiones contra el
  motor de hoy, M5 censo de huecos). `senales.db` en `mode=ro`, cachés no
  reescritas (`usar_cache=False` en toda descarga; el test lo fija por
  AST). Primera corrida: **M4 diverge en 90 de 287 filas**, muchas más
  que las 16 del 28/31-ago. Y M1 reportaba 1.534 retornos «no
  proporcionales» en 000660.KS — **era mi tolerancia**, relativa al
  retorno (1e-6 × |r|) y por debajo del ruido de float32. Corregida a
  1e-6 absoluto (0,0001 pp).
- **02:02** — **M1 limpio: sobre 8 años × 27 tickers (52.507 celdas), entre
  el 26-ago y hoy Yahoo no cambió UN SOLO retorno diario** (max |Δr| =
  1,2e-6, ruido de float), **no retiró ninguna barra y no apareció
  ninguna**. Cambió niveles en 1.962 celdas y todas son el reescalado
  proporcional de un dividendo bajo `auto_adjust` (factor constante por
  ticker: 005930.KS 0,98679, 6857.T 1,01478…). El teorema del expediente
  PIT, observado en vivo: niveles mutan, retornos no. Los «5 días
  retirados» de 2018 eran el deslizamiento de `period="8y"`; las
  «celdas nuevas» del 26-ago eran Asia a medio día al capturar. Las dos
  cosas están separadas en el clasificador, con contraprueba.
- **02:04** — **Entonces ¿de dónde salen las 90 divergencias de M4?** FX e
  índices no mutaron (caché del 1-sep 13:07Z vs hoy: 0 celdas distintas
  en EUR/JPY/KRW/TWD=X, ^KS11, ^N225, ^TWII, ^GDAXI, ^SOX). Probé la
  hipótesis «FX caído al sellar» (betas en moneda local): **no reproduce**
  (0,94 vs 0,73 sellado). Probé «faltan las últimas k barras» de SOX,
  acciones o FX: no reproduce.
- **02:05** — **Fuerza bruta: quitar UNA barra del `^SOX` por vez (130
  candidatas) y ver cuál deja las betas más cerca de las selladas.**
  Resultado, y es el hallazgo del frente: **la ausencia de la barra del
  `^SOX` del 2026-07-31 explica sola las cuatro fechas** —08-12, 08-14,
  08-19, 08-20— bajando el desvío máximo de beta de 0,25–0,27 a
  **0,026–0,042**. Las fechas vecinas (08-13, 08-17, 08-18, 08-21)
  reproducen 8/8 con la fuente de hoy. **La fuente sirvió el mismo query
  con y sin esa barra en la misma semana.** No es «reescribió la
  historia» ni «retiró una sesión»: es **intermitencia**. Va al script
  como M6, hipótesis ejecutable y etiquetada como tal: el testigo directo
  (una copia del `^SOX` de esas noches) no existe.
- **02:06** — **Y una consecuencia que `ESTADO.md` ya no describe bien:** las
  16 filas del 28/31-ago con signo contrario estaban `pendiente` el 1-sep
  al mediodía; el sello de las 18:15 verificó 15 de ellas. **Hoy están
  dentro del track record vivo (n=276).** El README sigue intacto porque
  su cifra está anclada al 28-ago; pero «ninguna cifra publicada se mueve»
  vale para el ancla, no para la base viva. Bajo «Yahoo de hoy» como
  canónica, el acierto vivo pasa de 64,86% a 64,49% y **15 filas cambian
  de acierto**. Bajo «la copia sellada» no se mueve nada, por definición.
- **02:09** — **Frente A cerrado en su parte medible.** Entregables:
  `GEMELO/fuente_canonica.py` (M1–M6, 26 s, `mode=ro`),
  `resultados/fuente_canonica.{json,md}` + `fuente_canonica_medicion.md`,
  `tests/test_fuente_canonica.py` (8 contrapruebas: un dividendo no es
  mutación, un precio revisado mueve dos retornos, una barra retirada se
  nombra, el deslizamiento de `period="8y"` no cuenta, la última fecha
  parcial se separa, nada del sellado importa el módulo, ninguna descarga
  reescribe la caché). Y **las cuatro cachés preservadas** comprimidas en
  `resultados/testigos_fuente/` con sha256 y README: un `ventana_larga.py`
  de rutina con TTL vencido las habría sobreescrito, y son la única
  evidencia de cómo servía Yahoo el 26-ago y el 1-sep.
  - La primera contraprueba me corrigió: mi clasificador contaba «celdas
    no proporcionales» y el test pedía «retornos cambiados» — un precio
    revisado es UNA celda y DOS retornos. Son dos cuentas distintas y
    ahora las dos existen. Y la tolerancia de retorno subió de 1e-6 a
    5e-6 porque el ruido de float32 medido llega a 1,3e-6.
  - **Lo que espera firma** (§6 del expediente): cuál es el campeón cuando
    sello y fuente discrepan; si se construye la copia cruda de insumos
    (toca `snapshot.py`, mismo bump que el parche de `:140`); si la
    ventana larga se declara fechada con hash de descarga.
- **02:13** — **Frente B cerrado.** `GEMELO/SECUENCIAL/horizonte.py` (60 s;
  dos rutas: analítica 1/√D y simulación con días reales remuestreados +
  permutación de signo por día; ancla pinchada al 31-ago, n=246 en 35
  días). `resultados/horizonte.{json,md}` y el veredicto en
  `horizonte_veredicto.md`. Las cifras: **~2 observaciones efectivas por
  día sellado**; 9 pp → ~250 días (jul-2027); 6,5 pp → ~475 (jul-2028);
  5 pp → ~800 (dic-2029). Coincide con la tabla del `DISEÑO.md` por otra
  vía. **El 25-oct el 5.1 tendrá ~73 días y MDE al 80% de 16,6 pp
  [11,0, 20,3]: potencia 0,36 frente a 9 pp.** Un NO PASA ese día no será evidencia de
  ausencia y hay que escribirlo antes de correrlo.
  - **La respuesta a la pregunta dura, en las dos direcciones:** como
    aparato estadístico NO es subpotente estructuralmente (n efectivo
    lineal); como instrumento para responder antes de que la respuesta
    deje de importar, SÍ hoy; y para «¿el efecto persiste?» es ciego por
    construcción hasta que haya un segundo régimen (hay uno). Primera
    mitad +19,2 pp, segunda **0,0 pp**, intervalos solapados: no es
    evidencia de cambio, es la forma exacta del problema.
  - Colateral: α empírico del test de permutación de signo por día = 0,083
    a 35 días (n_sim 300). Levemente anticonservador con pocos días. Va al
    expediente del Frente C.
- **02:13** — `director-programa` despachado con la pregunta del Frente F
  sobre el proyecto entero, con los hechos de A y B en el encargo.
- **02:16** — **Frente C computado** (`GEMELO/SECUENCIAL/trayectoria.py`, 4 s;
  PROPUESTA). Siete candidatos sobre la trayectoria real por prefijos de
  fecha (10 → 37 días, track record vivo): McNemar de filas, IC de clúster
  de día, permutación de signo por día, t sobre medias diarias, posterior
  bayesiana con prior escéptica N(0, 5 pp²), proceso de apuestas
  anytime-valid (Waudby-Smith & Ramdas) y signo de los días. **Resultado:
  el McNemar de filas cruzó el umbral 3 veces y «decide» en 21 de 28
  prefijos; los seis candidatos de nivel día cruzaron CERO veces y ninguno
  decide hoy.** La fragilidad no es del estadístico: es de tomar la fila
  como unidad. El día del 28-ago (8 discordantes a favor) movió el McNemar
  de 0,0365 a 0,0063 y el t de medias diarias de 0,117 a 0,067; el IC de
  día siguió conteniendo el cero ([−4,3, +29,3]); el capital anytime-valid
  quedó en 3,0 contra el 20 que decidiría.
- **02:19** — **Frente E computado** (`GEMELO/SECUENCIAL/estimandos.py`, 7 min;
  PROPUESTA). Seis estimandos con la misma vara: IC de fechas y «días para
  potencia 0,80 al efecto observado» (cota inferior optimista, sirve para
  comparar, no para prometer). Sobre la ventana sellada: dirección z=1,41;
  magnitud (|g|−|p−g|) z=1,88; gap capturado continuo z=1,82; **pendiente de
  calibración g~p = 1,42 [0,65, 2,19], z=3,44** — la magnitud predicha ordena
  la realizada, y es el único estimando que hoy excluye el cero con clúster
  de día. El decaimiento DENTRO de la ventana sellada: z≈0 (sin señal en 35
  días). Sobre la ventana larga reconstruida (518 fechas): dirección z=7,4;
  **decaimiento −1,6 pp de ventaja por hora de margen [−2,45, −0,77], z=3,8**;
  contraste Asia − Fráncfort +10,8 pp [5,0, 16,7]. **El estimando de
  mecanismo tiene ~4× menos señal por día que el de nivel** (D80 284 vs 75).
- **02:20** — **Frente D computado** (`GEMELO/SECUENCIAL/autocorrelacion.py`,
  2 min; PROPUESTA). **Salida 1 (prior de la ventana larga): AC1 = −0,042 sobre
  518 fechas, IC95 por bootstrap de bloques [−0,122, +0,041]** (contiene el cero: AC1 no se distingue de 0); por año
  −0,014 / −0,080 / −0,007; la sellada da −0,176 ± 0,164, compatible. Con
  la cota superior +0,04, el α del plan cae de la banda [0,046, 0,079] a
  ≈[0,046, 0,05] — se está verificando con el simulador del propio diseño en
  segundo plano. **Salida 2 (familia robusta): no existe a estos tamaños.**
  Bloques de 10/20 fechas como unidad inflan α a 0,09/0,12 ya con φ=0 (2–5
  unidades en la primera mirada: grados de libertad); Newey-West L=5 aplana
  la pendiente (0,064 → 0,084 entre φ=0 y 0,3) pero parte sesgado. El
  bootstrap de fechas con máximo sobre bloques que el plan ya usa está
  entre los dos. **La salida que sobrevive es la 1, y es un prior, no una
  medición de la ventana sellada: eso es lo que el adversario tiene que
  juzgar.**
- **02:21** — **`director-programa` entregó el documento del Frente F**
  (transcrito a `resultados/tesis.md` con procedencia). Su veredicto: la
  tesis está viva pero no la que el proyecto creía; la captura está muerta y
  el proyecto la mató; el activo es el mecanismo del decaimiento. Recomienda
  (marcado) el camino 1b —medir la PENDIENTE como estimando, no el nivel—
  con el argumento estructural de que el contraste entre bolsas cancela el
  factor común del SOX, y declara que **no lo computó**. **Yo sí lo
  computé en el Frente E, antes de leerlo, y no le da la razón:** sobre 518
  fechas el contraste Asia − Fráncfort tiene z=3,7 contra z=7,4 del nivel;
  el mecanismo necesita ~4× más días. Su propia cláusula «qué me haría
  cambiar de opinión» se dispara: la recomendación cae a 1a + 3. Va como
  adenda medida al pie de su documento, sin tocar su texto.
- **02:28** — El simulador del propio diseño (`alfa_plan_bajo_correlacion`,
  2.000 réplicas) en las cotas del prior: α = 0,039 [0,031, 0,048] a
  AC1 = −0,042; 0,047 a 0; **0,0545 [0,045, 0,065] a +0,041**. La banda
  firmada [0,046, 0,079] no se toca; la cota externa la reduce a
  ≈[0,039, 0,055] si el adversario la admite. Propuestas C, D y E escritas
  en `resultados/propuestas_cde.md`, cada una con script, cifras, costo y
  «qué no puede decir». `tesis.md` transcrita con la adenda medida.
  **Despacho al `estadistico-adversario` con las tres.**
- **02:29** — **Me cacé una cifra de memoria.** La línea de E por bolsa en
  `propuestas_cde.md` tenía cuatro números que no salían del `.json`
  (escribí «XETR +12,0 (39)» y el archivo dice +11,4 (35); XKRX +6,3 y no
  +14,1). Lo vi al verificar contra `estimandos.json` antes de despachar.
  Corregido en su sitio con nota. Es exactamente el error que la casa
  prohíbe y la razón por la que cada cifra debe tener un archivo antes de
  escribirse, no después.
- **02:31** — `estadistico-adversario` despachado con A, B, C, D, E y la
  adenda de la tesis. Mientras juzga: **borrador de
  `resultados/estado_epistemico.md`** (Fase 3), una página con seis
  estatus (demostrada / acotada / contestada / retractada / no evaluable /
  propuesta), 20 afirmaciones, cada cifra verificada contra su archivo
  antes de escribirla (README, actas §59/§61/§64/§69/§70, expedientes de
  esta noche). Sin la palabra prohibida (grep). Va al guardián y al
  adversario antes de darse por buena.
- **02:34** — **Fase 4, `veredicto_51.py`: el 92 suelto de `BANDA_N` queda
  pinchado al instante.** Los N históricos pasan a
  `N_DECLARADO_POR_CORRIDA` (82 → corrida invalidada, 92 → corrida de las
  13:31) y `N_REGISTRO_AL_20260901_MEDIODIA` (86); `BANDA_N` se construye
  desde ellos. Test nuevo en `tests/test_backtest.py`: cada N histórico se
  contrasta contra `parametros_declarados.N_intentos` del `veredicto.json`
  sellado de su corrida — si el número se mueve, el artefacto lo desmiente.
  2/2 verdes. **Forense de las 15 huérfanas: NO quedó pendiente** —
  `resultados/huerfanas.md` dice «forense cerrado» (sexta corrida, Frente
  C). Nada que hacer.
- **02:37** — **El diseño del congelado de insumos dejó de ser prosa:**
  `GEMELO/INSUMOS/insumos.py` (no activado: nadie lo llama, test que lo
  fija) con `congelar` aditivo + sha256, `leer`, `contrastar` (PARIDAD /
  BARRA_RETIRADA / RETORNO_CAMBIADO / PARIDAD_REESCALADA / …) e
  `intermitencia` (presente-ausente-presente sobre ≥3 copias: la clase que
  M6 sólo pudo inferir). `tests/test_insumos.py`: 8 contrapruebas verdes.
  - **Y me corrigió el costo.** El expediente decía «~60 KB/día, ~15
    MB/año» a ojo; medido sobre el panel real de 37 series: **213 KB/día,
    ~53 MB/año** para 3 años (los precios no comprimen), **36 KB/día, ~9
    MB/año** para las 130 barras que el modelo consume. Corregido en el
    expediente con la nota. Era «lo único no medido del documento» y
    estaba mal por 3,7×.
- **02:50** — **La suite epistémica me cazó dos veces.** (1) El detector de
  retractaciones en prosa tomó "siempre al alza" entre comillas angulares
  en mis documentos como token retractado y lo encontró en 20 sitios del
  código: falso positivo por mi tipografía; cambiado a comillas rectas en
  los documentos nuevos. (2) **`test_ningun_estimador_se_publica_como_
  hallazgo_sin_su_intervalo`: el «MDE al 80% de 16,6 pp» del Frente B iba
  en negrita sin intervalo.** Tenía razón: el MDE y los «días para
  potencia» se derivan del SE de día, y ese SE tiene su propia
  incertidumbre. Agregado un bootstrap anidado (`ic_se_dia`) en
  `horizonte.py`: SE 8,0 pp [5,7, 10,5] → **9 pp: 248 días [109, 370]
  (jul-2027, entre dic-2026 y feb-2028); 25-oct: MDE 16,6 pp [11,0,
  20,3]**. Los intervalos son anchos porque 35 días estiman mal su propia
  varianza, y eso también es un hallazgo. Corregido en `horizonte.md`,
  `horizonte_veredicto.md`, `estado_epistemico.md` y en esta bitácora.
- **02:55** — **ERRATA DE ESTA BITÁCORA, y es información sobre mí.** Las
  horas de los hitos entre «01:50» y «02:50» **no las leí del reloj: las
  estimé**, y las estimé mal por un factor de ~4 (había escrito de 02:00 a
  06:30 para trabajo que ocurrió entre 01:50 y 02:50). Lo descubrí al
  correr `date` antes del cierre: 02:54. Reconstruidas desde los `mtime`
  de cada entregable y el `generado_en_utc` de cada `.json`
  (`fuente_canonica.py` 02:07, `trayectoria.json` 02:16Z→local 02:16,
  `estimandos.json` 02:18, `veredicto_51.py` 02:34, `insumos.py` 02:36,
  `estado_epistemico.md` 02:46) y corregidas en su sitio. Las tres
  primeras (01:40, 01:42, 01:43) sí venían de `date`. **La regla «hora por
  hito» exige leer el reloj en cada hito; no lo hice y el resultado fue una
  cronología inventada con cara de precisa.** Desde acá, cada hito lleva
  `date`.
- **02:56** — Suite completa (534 tests): **1 fallo, mío**:
  `test_gemelo_no_escribe_en_ninguna_base` — `GEMELO/fuente_canonica.py`
  importaba `sqlite3` directamente. Corregido: la lectura va por
  `backtest.datos._conexion_ro`, la capa auditada, como el resto de GEMELO.
  `mtime` de las dos bases intactos antes y después de la suite.
- **03:00** — **Dictamen del `estadistico-adversario` sobre A–E** (texto
  íntegro en `resultados/dictamen_07/DICTAMEN.md`, sus 16 scripts de
  verificación preservados al lado). **Global: NO CONCLUYENTE, hacia el
  lado negativo.** Lo que rechazó, lo que observó y lo que verificó, con
  lo que hice en cada caso:
  - **RECHAZADO — el α empírico 0,083 del Frente B era ruido de Monte
    Carlo:** con n_sim 3.000 da 0,056 [0,048, 0,065]; y
    `_p_permutacion_dia` re-sembraba igual en cada réplica (una sola
    matriz de signos para 300 réplicas). Corregido en el ejecutable:
    semilla inyectable en `bifurcaciones._p_permutacion_dia` (default
    intacto), semilla por réplica y n_sim 1.000 con Wilson en
    `horizonte.py`. El 0,083 se retira de los tres archivos.
  - **RECHAZADO — E-2, el decaimiento como pendiente por hora con IC:** la
    unidad de replicación del mecanismo es la BOLSA (4, con sólo 2 valores
    distintos de h), no la fecha; permutación exacta p = 0,231, p mínimo
    alcanzable 1/13; y el README ya lo decía en la línea 60 («con n = 4
    bolsas no se puede ajustar una curva»). **Mi «4× menos señal por día»
    contra la recomendación 1b de la tesis no queda establecido**: la
    adenda de `tesis.md` se reescribe.
  - **OBSERVADO — M1:** las «1.962 celdas reescaladas por dividendos» eran
    1.953 de UN solo ticker (000660.KS, factor 0,999783) más 9 barras
    parciales del 26-ago; los tres «factores» que cité (005930.KS 0,9868…)
    eran la barra viva de Tokio a medio día, no dividendos — dos cachés a
    95 s de distancia lo prueban. Clasificador corregido (la última fecha
    fuera de `distinta` y del factor) con contraprueba nueva.
  - **OBSERVADO — MAE:** «2,827 → 2,897» mezclaba dos denominadores; con
    las 15 filas es 2,827 → 2,892. Y lo que faltaba decir: el par McNemar
    de esa sustitución es b=8, c=7, **p = 1,0**: la pregunta constitucional
    importa por reproducibilidad, no porque mueva la cifra.
  - **OBSERVADO — R2 dispara sobre el ancla del Frente B y yo lo llamé
    «mitades»:** sin el bloque 15–23 jul, +9,3 → +2,5 pp, IC de día
    [−13,6, +19,2] (contiene el cero), permutación p = 0,82. Es una vara de rechazo congelada
    y hay que nombrarla. Agregada al script y al veredicto.
  - **OBSERVADO — C-3 tiene otro motivo, mejor:** el McNemar de filas no es
    frágil, tiene la escala inflada por √DEFF (z_MCN/z_ICD = 1,87 vs
    √3,77 = 1,94); su α real a 5% nominal es ≈ 0,31. Computado en
    `trayectoria.py`. C-1 entra sin condición; C-2 con cinco
    declaraciones; C-3 con el motivo cambiado.
  - **D-1 NO ENTRA como «cota externa»**: entra como medición de
    referencia, con el chequeo que decide y que yo no había hecho —la
    reconstrucción en el mismo tramo que la sellada da AC1 −0,180 ± 0,158
    contra −0,176 ± 0,164—, ciega a la intermitencia de M6, y con el α del
    plan en [0,031, 0,065] contando el error de Monte Carlo. La banda
    firmada no se toca. D.2 verificado y se publica tal cual.
  - **E-1 entra sólo pre-registrada contra la pendiente del control lineal**
    (C1), no contra 0, con las dos hipótesis separadas, y con el 2,6× [1,5,
    4,8] de la larga como respaldo (en la sellada el cociente es 5,5× con
    IC [0,7, 1.379]: no distingue nada).
  - **VERIFICADO:** M1 (0 retornos, por otra ruta y con mejor cobertura), M6
    (única barra de 130, brecha 0,035–0,057 al segundo; sigue hipótesis con
    residuo 4–8× el piso), las 15 filas, el ancla y las tres rutas del
    Frente B, C celda por celda, D.1 y D.2, E aritméticamente.
  - **Registro de intentos:** exigió que las configuraciones de C y E entren
    antes de cualquier DSR. Hecho: tramos TRAY (4) y ESTIM (5), registro
    91 → 100; `veredicto_51.N_INTENTOS_PREVIO` acompaña (test).
  - Nota de proceso que él mismo hizo constar: `horizonte.md` cambió bajo
    auditoría (mis intervalos anidados). Juzgó la versión de las 02:48.
- **03:06** — Correcciones del dictamen aplicadas y regeneradas. Cifras
  finales: **α empírico 0,058 [0,045, 0,074] a 35 días** (1.000
  simulaciones, semilla por réplica; en 73–1.000 días 0,043–0,059, todos con
  IC que contiene 0,05: el test está calibrado; el «anticonservador» se
  retira); **potencia 0,34 [0,31, 0,37] el 25-oct**; **R2 dispara sobre el
  ancla** (+2,5 pp, IC de día [−13,6, +19,2], contiene el cero; b=48, c=43, p=0,675,
  permutación 0,82); cadencia 0,897 [0,76, 0,96] → los 9 pp entre jul y
  sep-2027 por cadencia, 254 días con el gasto OBF ×1,0241. M1: 1.953
  celdas, un ticker, factor 0,999783, 26 tickers con 0. Trayectoria: ICC
  0,42, DEFF 3,77, **α real del McNemar de filas 0,313**. Autocorrelación:
  tramo solapado −0,180 ± 0,158; rango honesto del α del plan [0,031,
  0,065]. Documentos A, B, C/D/E, G y la adenda de la tesis reescritos en
  su sitio; el dictamen íntegro y sus scripts en `dictamen_07/`.
- **09:00** — **Fase 4 operativa entregada por `ingeniero-plataforma`.**
  - **Vigía:** `chequear_noticias()` distingue «NO corrió» (sin rastro en
    log ni ledger), «corrió y NO completó» (rastro de hoy en
    `data/noticias.log` sin corrida en el ledger; si systemd dice
    `Result=timeout`, nombra la hora del kill) y «colgado» (5.0.2). Firma
    intacta; refuerzo systemd inyectable y nunca requerido; 7 tests nuevos
    con contraprueba en `tests/test_vigia.py` (25 verdes).
  - **Timeout de `mki-noticias`, con la causa raíz que nadie había medido:**
    el cuello no es Haiku (2–3 min estables) ni la red; es
    `noticias.migrar_noticias_v2()`, que compara por similitud
    (`difflib.SequenceMatcher`) **todo el historial de `noticias.db`**
    (5.286 filas desde 2025-09-09) en cada corrida: O(n²), 13,8 millones
    de comparaciones, 1.804 s replicados en `mode=ro`. La serie histórica
    (26-ago 22:09 → 27-ago 24:24 → 28-ago 27:51 → 31-ago 28:15 → 1-sep
    ≥30:00 TIMEOUT) ajusta `wall ≈ 7,16e-5 × N²` a ±3%. **No es
    estacionaria: un percentil de duraciones no sirve; con el techo actual
    el job vuelve a morir en días.** Propuesto `TimeoutStartSec=2700` (45
    min, termina antes del backup de las 18:40) como parche temporal, y la
    solución real —acotar la migración a una ventana— declarada como
    cambio de comportamiento de `noticias.py`, de Nicolás. Diff y comandos
    en `resultados/parche_timeout_noticias.md`. **Nada aplicado;
    `systemd/` y `launchd/` intactos.**
  - *(Hora leída de `date` esta vez. El agente tardó 7 h 12 min en dos
    tareas acotadas —el grueso, replicar el bucle O(n²) contra la base real
    para medir los 1.804 s—; entre las 03:13 y las 09:00 esta corrida no
    hizo nada más que esperar, y esa espera sin plan B es una de las cosas
    que van en la sección final.)*
- **09:06** — Suite completa (09:00–09:05): **539 passed, 2 xfailed, 1
  failed** — el fallo era mío y de un `.md`: un intervalo de AC1 en
  `espera_firma.md` §19 sin la marca «contiene el cero». Corregido;
  `test_epistemico.py` 17 verdes. `mtime` de las dos bases intactos antes y
  después. `ESTADO.md` regenerado en **exactamente 50 líneas**, las cuatro
  reglas adentro (una línea cada una, sin blancos entre secciones): el tope
  se cumple sin sacar nada; propongo que el tope quede. **Despacho al
  `guardian-constitucion`** con la tanda entera y la declaración de que no
  escribí actas en `DECISIONES.md` esta noche: que dictamine si el cierre
  las exige.
- **09:35** — **Dictamen del `guardian-constitucion`: OBSERVADO, sin
  rechazos.** Verificó en verde R0 (todo lo intocable idéntico a HEAD), R1
  (`mtime` de las bases = el sello de anoche, antes y después de correr él
  mismo la suite: 540 passed, 2 xfailed), R2, R3, R5, R7, R8 (timers
  intactos, nada nuevo se autoejecuta), y que `bifurcaciones.py` no mueve
  ninguna cifra (el default de la semilla es idéntico). Observó, y en cada
  caso tenía razón: (1) **cero actas en `DECISIONES.md`** — el cierre las
  exige, por lo menos cuatro; (2) el comentario `# 97` de `veredicto_51.py`
  con el valor ya en 106; (3) el rechazo de E-2 sobrevivía sin marca en el
  `.md` generado de `estimandos`; (4) el α reemplazado a 1.000 simulaciones
  cuando el adversario pidió ≥ 3.000, y una línea del veredicto que todavía
  citaba «n_sim = 300»; (5) `espera_firma.md:48` decía 91/97 en el commit
  que pone 100/106; (6) **los cuatro módulos de `SECUENCIAL/` no tenían
  test**; (7) los 9 intentos se registraron después de correr — desviación
  del pre-registro §4.2 bis que hay que nombrar como tal; (8) la asimetría
  Mac/PC del vigía (refuerzo systemd) declarada sólo en un docstring; (9)
  fuera del diff: `.env` en 644, operación de Nicolás. Y una decisión que
  pidió acta y no marcha atrás: `fuente_canonica.py` importa `motor`
  (puro), contra la prosa de `CLAUDE.md` pero no contra la regla que los
  tests aplican.
- **09:44** — Aplicado todo lo del guardián salvo las actas (en manos del
  `escriba-decisiones`, §71–§74): comentario corregido; E4/E4' marcados
  RETIRADO en `estimandos.md` (regenerado desde el `.json` con
  `--solo-informe`, sin recomputar); `horizonte.py` a **3.000
  simulaciones**: α 0,055 [0,048, 0,064] a 35 días, potencia 0,36 [0,34,
  0,37] frente a 9 pp el 25-oct — propagado a los cinco documentos;
  `espera_firma.md` con 100/106; **`tests/test_secuencial_07.py`, 17
  tests** (identidades cerradas de potencia/MDE, α de la simulación bajo la
  nula, validez y conservadurismo del proceso de apuestas, AR(1)
  recuperado, HAC ≡ z iid a L=0, identidades de los estimandos por fila, y
  aislamiento de los cuatro módulos). Horas leídas de `date`.
- **09:46** — **Actas §71–§74 escritas por el `escriba-decisiones`** (439
  líneas, `DECISIONES.md` 6806–7244, append puro): la fuente canónica y la
  decisión de aislamiento; el registro 91 → 100 **a posteriori**, nombrado
  como desviación del pre-registro §4.2 bis; `BANDA_N` pinchada; la
  semilla inyectable; el vigía con su asimetría Mac/PC declarada y no
  igualada; el timeout O(n²); las propuestas con dictamen, los retiros y la
  errata de horas. Reportó dos cosas que valen: que la tensión
  prosa/código del aislamiento de GEMELO sigue sin resolver (CLAUDE.md es
  de Nicolás), y que no pudo verificar «`.env` 644» desde el árbol — lo
  verifiqué yo: `stat -c %a .env` → 644. Anotado en `espera_firma.md` como
  operación de Nicolás.
- **09:58** — **Segundo pase del guardián: OBSERVADO → APROBADO con una
  sola corrección**, que apliqué en su sitio: el acta §72 había quedado
  congelada en el estado de las 03:06 (α a 1.000 simulaciones) y
  contradecía al artefacto que cita — «el mismo patrón que bautizó a
  76ed2cf», dijo, y tenía razón: el escriba escribió a las 09:46 con una
  cifra que yo había reemplazado a las 09:44. Corregida a 3.000
  simulaciones, 0,055 [0,048, 0,064], `generado_en` real. Todo lo demás en
  verde: append puro en `DECISIONES.md` (md5 de las 6.804 líneas previas
  idéntico), 557 tests corridos por él, `mtime` de las bases intactos,
  alcance exacto. Agrupación de commits: la suya, en su orden (vigía;
  registro y semilla; corrida GEMELO; actas y estado). Nada se pushea.

## Handoff — lo que resolví, lo que propuse, lo que rechazó el adversario, lo que espera firma

### Resuelto (medido, con script, con contraprueba)

- **Frente A — cuánta historia mutó.** `GEMELO/fuente_canonica.py` (M1–M6) +
  `tests/test_fuente_canonica.py` (8) + las cuatro cachés preservadas en
  `resultados/testigos_fuente/`. Yahoo **no cambió un retorno diario en 8
  años × 27 tickers** (52.507 celdas; 1.953 niveles de UN ticker reescalados
  por 0,999783); **sí sirve el mismo query en estados distintos**: retiró la
  sesión del 28-ago (ventana ≤ 8 h, no 18) y **cuatro noches de agosto sirvió
  el `^SOX` sin la barra del 31-jul** (hipótesis M6: única barra de 130,
  residuo 4–8× el piso). El sello del 28-ago tenía razón 8/8 con el dato que
  la fuente después retiró. Las 16 filas de signo contrario ya están
  verificadas (15) en el track record vivo: b=8, c=7, p=1,0 — importa por
  reproducibilidad, no por la cifra. **El sello tiene «emitido antes» y no
  «reproducible después».** Expediente con cinco candidatas y el diseño de
  la copia de insumos: `resultados/fuente_canonica.md`. **El diseño ya es
  ejecutable:** `GEMELO/INSUMOS/insumos.py` + `tests/test_insumos.py` (8), no
  activado, costo medido (9 MB/año para las 130 barras consumidas).
- **Frente B — ¿medible en principio?** `GEMELO/SECUENCIAL/horizonte.py` +
  `resultados/horizonte_veredicto.md`. **No es subpotente estructuralmente**
  (~2 obs. efectivas por día sellado, n efectivo lineal) **pero responde en
  años**: 9 pp → 248 días [109, 370] (jul-2027, entre dic-2026 y feb-2028);
  6,5 → 475 [209, 709]; 5 → 803 [354, 1.199]. El 25-oct: MDE 16,6 pp [11,0,
  20,3], potencia 0,34 [0,31, 0,37] frente a 9 pp. **Y es ciego a «¿el
  efecto persiste?» con un solo régimen.** R2 dispara sobre el ancla.
- **Fase 4:** `BANDA_N` pinchada al instante con test contra el
  `veredicto.json` sellado; forense de huérfanas ya estaba cerrado; registro
  de intentos 91 → 100 con los de esta noche.
- **Fase 3:** `resultados/estado_epistemico.md`, 20 afirmaciones con estatus.

### Propuesto (etiquetado, con dictamen del adversario al pie)

- **C-1** ratificar el IC de clúster de día y no publicar decisiones binarias
  hasta MDE firmado — **entra sin condición.**
- **C-2** proceso de apuestas anytime-valid como secundario — **entra con
  cinco declaraciones** (y con el mejor argumento, que dio el adversario: es
  válido bajo la autocorrelación que D no acota).
- **C-3** quitar el p del McNemar de filas como salida por defecto — **entra
  con el motivo cambiado: α real ≈ 0,31, no «fragilidad».**
- **D-1** la autocorrelación de la reconstrucción como referencia — **no entra
  como «cota»; entra como medición**, con el chequeo del tramo solapado
  (−0,180 ± 0,158 vs −0,176 ± 0,164) y el α del plan en [0,031, 0,065]. La
  banda firmada [0,046, 0,079] no se toca. **D.2: a 51–203 fechas no existe
  estadístico con α = 0,05 plano bajo φ desconocida — verificado.**
- **E-1** pendiente de calibración como endpoint secundario — **entra sólo
  contra el control lineal**, hipótesis separadas.
- **Tesis (`resultados/tesis.md`, `director-programa`):** la captura está
  muerta y el proyecto la mató; el activo es el mecanismo; recomienda 1b
  (medir la pendiente entre bolsas) condicionado a una medición que sigue
  sin hacerse; seguir sellando; los dos cortes de método en un solo bump.

### Rechazado por el adversario (registrado, no re-litigado)

- **α empírico 0,083** del test de permutación de signo por día: ruido de
  Monte Carlo (n_sim 300 + semilla fija por réplica). Corregido en el
  ejecutable: 0,058 [0,045, 0,074]. El test está calibrado.
- **E-2, el decaimiento como pendiente por hora con IC:** la unidad de
  replicación es la bolsa (4, con 2 valores de h); p mínimo alcanzable 1/13;
  el README ya lo decía. **Y con eso cae mi adenda «4× menos señal» contra
  la recomendación 1b**: la contradicción no queda establecida.
- **La clasificación de M1** como estaba escrita: «1.962 celdas, todas
  dividendos, varios tickers» era 1.953 de un ticker más barras vivas;
  corregido con contraprueba.

### Qué espera firma, en orden de urgencia

1. **El parche de `snapshot.py:140` + la copia congelada de insumos, en un
   solo bump** (`espera_firma.md` §1 + §16). Único modo de falla activo, y
   la mitad del sello que falta.
2. **Cuál es el campeón cuando sello y fuente discrepan** (§16a): las filas
   selladas, recomendado. Desbloquea un 5.1 independiente de la fuente.
3. **La frase de potencia del 5.1 antes del 25-oct** (§17): 0,34 [0,31,
   0,37]; y saber que R2 dispara sobre el ancla.
4. **La réplica** (§4): el único costo ya materializado.
5. **C-1/C-2/C-3, D-1 como referencia, E-1** (§18–§20): ninguna mueve una
   cifra.
6. **El MDE del secuencial** (§5): cero hasta octubre, infinito desde el
   19-nov.
7. **El timeout de `mki-noticias`** y el resto de la Fase 4 operativa: ver la
   entrada de cierre de esta bitácora.

## Qué me resultó difícil de este proyecto, y por qué

Nadie lo pidió antes; a Nicolás le sirve.

1. **Leer el reloj.** Escribí cinco horas de hitos que ocurrieron en una.
   No fue un error de aritmética: fue que la instrucción «hora por hito» la
   ejecuté como «hora plausible por hito» sin notar la diferencia hasta que
   un `date` la mostró. El proyecto está lleno de reglas que existen porque
   un agente hizo exactamente eso con una cifra; yo lo hice con el tiempo.
   Desde entonces cada hito lleva `date`, y la errata está en su sitio.
2. **Separar lo que deduje de lo que leí.** La lectura obligatoria entrega
   respuestas digeridas (el defecto 2 de la calibración estaba casi entero
   en la cola). Puedo declararlo, pero no siempre puedo saber cuánto de una
   «deducción» mía era recuerdo de un párrafo.
3. **Las cifras de memoria se me escapan en la prosa, no en el código.**
   Dos veces esta noche: cuatro números por bolsa que no salían del `.json`
   y un costo «~15 MB/año» que al medirlo era 53. Las dos las cacé yo, pero
   después de escribirlas. La regla correcta es la que ya tiene el proyecto
   —cada cifra con su archivo ANTES de escribirla— y aun sabiéndola la
   violé donde el texto fluía.
4. **La tolerancia numérica es una decisión, no un detalle.** Mi primer
   clasificador reportó 1.534 retornos «mutados» de un ticker por poner
   1e-6 relativo donde el ruido de float32 es 1,3e-6 absoluto. El hallazgo
   central del Frente A dependía de ese número, y estuvo mal durante veinte
   minutos.
5. **La unidad de replicación.** Computé z y «días para potencia» del
   mecanismo de decaimiento con la fecha como unidad cuando la unidad es la
   bolsa, y hay cuatro. El README lo decía en una línea. Es el error más
   caro de la noche porque produjo una conclusión de programa (contra la
   recomendación 1b) que después hubo que retirar, y no lo vi porque la
   aritmética era impecable.
6. **Los tests epistémicos del repo son adversarios de verdad.** Me pararon
   cuatro veces: por un token entre comillas angulares, por un MDE sin
   intervalo, por intervalos que contenían el cero sin decirlo, por importar
   `sqlite3` desde GEMELO. Cada vez tenían razón, y cada vez lo que exigían
   era barato de dar. Lo difícil no fue cumplirlos: fue aceptar que un
   documento «terminado» no lo está hasta que pasa por ellos.
7. **El agente más lento es el que hace el trabajo más aburrido.** El
   ingeniero de plataforma llevaba más de una hora con dos tareas acotadas
   mientras el adversario juzgaba cinco frentes en 25 minutos. No sé por qué;
   sí sé que no debí dejar la única tarea operativa de la noche sin
   plan B hasta el final.
8. **El proyecto castiga la creatividad exactamente donde promete
   premiarla.** La licencia era «sé creativo en el planteo, nunca en lo que
   se afirma». De seis propuestas, cuatro entraron con condiciones y dos se
   cayeron; las que entraron entraron porque el adversario las reescribió
   mejor de lo que yo las había planteado (C-3, C-2). La creatividad que
   sobrevivió fue la de mirar cosas que ya estaban ahí —las cachés como
   testigos, el `veredicto.json` como pinchazo— no la de inventar
   estimandos.

*(Fase 4 operativa, para el handoff: el vigía ya distingue «no corrió» de
«corrió y no completó» (commit 1); el timeout de `mki-noticias` tiene
causa raíz O(n²) y parche a 2.700 s preparado, NO aplicado —
`parche_timeout_noticias.md`—; `ESTADO.md` cabe en 50 líneas con las
cuatro reglas y propongo que el tope quede; `BANDA_N` pinchada; huérfanas ya
cerradas; `.env` en 644, operación de Nicolás. Y una cosa que esta corrida
NO hizo y anota: el job de noticias volverá a morir en días si no se
aplica el parche o se acota la migración — hoy corre a las 17:50 con el
techo viejo.)*
