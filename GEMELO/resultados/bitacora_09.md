# Bitácora 09 — novena corrida autónoma, noche del 2-sep al 3-sep-2026

Continuación de `bitacora_08.md`. Una línea por hito, **con hora local
(Chile, UTC−4) leída de `date` en cada hito**.

## Lo que gobierna esta corrida

Encargo: `~/encargo.md` (subido por Nicolás; copia en
`GEMELO/resultados/encargo_corrida_09.md`). Tres bloques con orden
estricto: (1) aplicar las decisiones D1 (rama del efecto = regla de
deduplicación firmada), D2 (convención del registro de intentos, §28) y D3
(métrica primaria del veredicto: magnitud —MAE contra cero, CRPS—;
dirección secundaria); (2) la deuda que sostiene la visión (importador
CSV, parche `snapshot.py:140` como `.diff`, O(n²) del job de noticias,
cuatro tarjetas firmables, diseño de la réplica, deuda estadística); (3)
la ruta al veredicto con la métrica correcta (§2 en el harness, juez
lineal bajo D3, días que faltan).

Límites: motor, senales, snapshot, universo, modo de emisión, `.env`,
timers intocables (parche `.diff` + test donde haga falta); filas selladas
jamás reescritas; ninguna cifra publicada se mueve sola (doce bloques);
ningún estimador sin intervalo; clúster de día; todo lo nuevo PROPUESTA
hasta el dictamen; nada pesado ni descargas entre 17:50 y 20:30; nada
pusheado. Cada hipótesis probada suma un intento al registro.

Cláusula que manda: **si una instrucción del encargo es ella misma el
defecto, no se ejecuta; se anota con la razón y se sigue.**

Ajuste de Nicolás antes de arrancar (23:45, en la sesión): para la tarjeta
de `Persistent=true` (2d) **no se lee el journal de systemd**; la evidencia
es `data/*.log` solamente y se anota. Para 1d se salta la lectura del hook
`guardia-reglas.py` (el orientador verificó que no menciona
`migracion-wsl`); se corrige `CLAUDE.md` y la línea 3 del frontmatter de
`.claude/agents/guardian-constitucion.md`, donde vive la deriva.

## Hitos

- **23:37** — Arranque. `HEAD=067ce16`, árbol limpio, 23:37 Chile: la
  ventana de sellado ya cerró (el sello del 2-sep está: `senales.db` mtime
  18:15). Suite completa y `orientador` lanzados en paralelo.
- **23:47** — Suite inicial en verde: **606 passed, 2 xfailed** en 5:02;
  `tests/test_motor.py` OK (betas, predicción, divergencias idénticas con y
  sin datos futuros). Número de partida: 606 + 2.
- **23:47** — Orientación (`orientador`, 48 lecturas). Tres hallazgos que
  cambian el encargo antes de tocar nada: (i) **el importador de CSV ya
  existe** (`scripts/restaurar_backup.py`, acta §42, 17 tests): el frente
  2a se convierte en verificación contra el criterio de aceptación del
  encargo, no en construcción; (ii) el hook `guardia-reglas.py` **no
  menciona** `migracion-wsl`; la deriva está en el frontmatter de
  `guardian-constitucion.md:3`; (iii) el test del Frente G no cubre el
  cambio de convención (prueba n+1 en abstracto): 1a lo completa primero.
  El árbitro hoy computa `dedup=False` al corte 28-ago.
- **00:05** — Seis agentes del bloque 2 lanzados en paralelo a las 23:58
  (2a importador, 2b parche :140, 2c O(n²) noticias, 2d tarjetas, 2e
  réplica, 2f deuda estadística). Bloque 1a en el contexto principal.
- **00:27** — **Incidente:** el límite de sesión de la API (reset 00:10)
  mató a cuatro agentes a mitad de trabajo (2a, 2b, 2d, 2f); 2e terminó
  (`GEMELO/diseno/replica.md`, 825 líneas) y 2c sigue. Quedaron archivos
  parciales (`tests/test_importador_roundtrip.py`,
  `tests/test_parche_snapshot140.py`, `GEMELO/resultados/corrida09/`): se
  relanzan los cuatro con la instrucción de retomar desde lo parcial y no
  fiarse de ello sin releerlo. Hallazgos de 2e que el orquestador registra:
  la skill `switch-titular` que cita `CLAUDE.md` **no existe** en
  `.claude/skills/` (el orden del switch vive en `modo-emision`); la
  réplica en sombra gasta presupuesto de IA (`mki_noticias.py` no consulta
  `modo`); `guardia_titular.py` y `titular.json` quedan diseñados sin
  prototipo.
- **00:38** — Relanzados 2a, 2b, 2d, 2f (00:28). **1a aplicado en el árbitro:**
  `cifras.sellada()` pasa a `dedup=True` (`DEDUP_PUBLICADO`), mismo corte
  28-ago, y cada estimador lleva ahora IC de clúster de día (bootstrap de
  día 4.000, t de clúster, permutación de signo por día), McNemar exacta al
  lado de la χ²cc, retorno de sesión con Wilson y el ratio de ancho con IC
  de día. Cifra publicada desde hoy: **n = 238, 34 días, 67,6% [61,5, 73,3]
  vs 58,0% [51,6, 64,1], +9,7 pp (9,66), IC95 de día [−7,2, +26,6]
  (contiene el cero), t de clúster [−8,1, +27,4], permutación de día p = 0,294, McNemar de filas
  0,0455 (exacta 0,0451; b 72, c 49), ICC 0,39, DEFF 3,55, n efectivo 67;
  MAE 2,52 vs 2,98 (−15,3%); cobertura 92,9%, ratio 2,19× [1,71, 2,78];
  retorno de sesión 62,1% [55,9, 68,0] (n 243).** Doce bloques movidos
  (README ×9, skill ×2, estado epistémico ×1) más los sitios fuera de los
  doce que la cifra vieja ocupaba: skill `estadistica-evaluacion` y su
  self-test (`evaluacion.py`: asserts 161/238, 138/238, mcnemar_exact(72,
  49) → 0,0451; el 1,84 de la demo de CRPS pasa a 2,19), agente
  `estadistico-adversario` (V1, V3, V4), `GEMELO/RELEVO.md` (×5 con
  errata fechada), `bifurcaciones.ANCLA` (nota: ancla histórica). Cuatro
  filas nuevas en `cifras_retiradas.md` (n = 248 / 164 y 148 de 248 /
  +6,5 pp / 0,1849 / 1,84×). **El test del Frente G se completa:**
  `test_si_la_convencion_cambia_cambian_los_doce_bloques_y_la_derogada_no_esta`
  (los doce fragmentos de `sellada(dedup=False)` difieren uno a uno y
  ninguno sobrevive sin marca) y `test_todo_estimador_del_arbitro_lleva_intervalo`.
  Defecto propio corregido: el fragmento 11 de la skill quedó partido en
  dos líneas; el test lo cazó. Verde: `test_cifras_arbitro` + `test_epistemico`
  + `test_bifurcaciones` + `test_hooks_propuestos` 66 passed, 2 xfailed;
  self-test de `evaluacion.py` en verde.
- **00:40** — **1d:** `CLAUDE.md` 5.0.3 con nota fechada (el titular es
  este PC; `migracion-wsl` muerta; la skill `switch-titular` no existe → la
  cita pasa a `modo-emision`); frontmatter de `guardian-constitucion.md:3`
  corregido. **3a:** `tests/test_linea_base.py` 34 passed — la §2 sigue
  reproduciendo en el harness (21/21, acta §25/§34.10); no hay nada que
  rehacer. **2a cerrado** (`corrida09/importador_roundtrip.md`): 5 tablas,
  2.301 = 2.301 filas, 25.082 celdas, 0 discrepancias, `plataforma_version`
  42/42; hallazgo: `sqlite_sequence` con 8 filas para 4 tablas (restos de la
  composición del 30-ago; riesgo nulo; firma). **2b cerrado**
  (`corrida09/parche_snapshot140_tabla.md`, `propuestas/parches/snapshot140.diff`,
  `tests/test_parche_snapshot140.py` 6 passed): 25 filas malas en 4 fechas
  (07-05: 8, 07-29: 7, 08-03: 3, 08-05: 7), las 25 `verificada`; **bajo el
  parche las 25 serían `no_verificable_timing` y 0 verificables** — corrige
  a la cola §2a-ter, que decía 15: las 10 del lado viejo también se
  emitieron después de la apertura correcta. Por construcción: sesión
  sellada ≠ correcta sólo si una sesión abrió en (available_at, ahora].
- **00:42** — **1b** en marcha: `horizonte.py` gana la **ruta 3** (simulador
  calibrado del Frente A, 1.000 réplicas por celda, días para 0,80 por
  bisección, comparación pareada con la ruta 2) y corre en segundo plano.
  **3b:** pre-registro `GEMELO/preregistro/juez_lineal_d3.md` escrito y
  congelado (C1, C2, campeón; MAE contra cero, CRPS contra climatología
  causal, dirección secundaria; clúster de día; 36 intentos declarados);
  script `GEMELO/juez_lineal_d3.py` con descarga inutilizada; caché de 8
  años presente. `auditor-lookahead` despachado antes de la primera
  corrida. **1c:** `GEMELO/preregistro/enmienda_v1bis.md` escrito
  (reemplaza a la propuesta I: magnitud primaria, dirección secundaria,
  tabla V2–V7/R1–R3); adversario a despachar. **Errata propia, en el
  acto:** los tres hitos anteriores se escribieron con horas estimadas
  (00:40 / 01:05 / 01:20) en vez de leídas de `date`; `date` dio 00:42 al
  cerrar el tercero y se corrigieron a 00:38 / 00:40 / 00:42 — el mismo
  error que la séptima corrida tuvo que enmendar. Desde acá, cada hora se
  lee antes de escribirla.
- **00:48** — Dictamen del adversario sobre la enmienda V1-bis (v1): **NO
  SOSTIENE «cambio de vara que sólo endurece»: es un CAMBIO DE PREGUNTA**
  (cambia el denominador —de «siempre al alza» a «predecir cero», que en
  magnitud es el análogo del 50%—, la familia de endpoint, y saca la
  dirección del gating). Firmable como lo que es, tras cinco exigencias:
  denominador = climatología causal; borrar «sólo endurece» (un retador
  que gane en magnitud y pierda en dirección PASA bajo la v1 y no bajo
  V1: afloja) → conjunción V1-bis ∧ V1; declarar que el endpoint se eligió
  mirando la ventana (salidas α: sellos posteriores al 3-sep / β:
  contaminación declarada); tipo I de la conjunción con verdad conocida;
  fijar la clave del día (emisión, k = 34). Verificó: ganancia MAE del
  campeón contra cero +0,4547 pp, t de clúster [−0,087, +0,996] (k = 34;
  contiene el cero), p de día 0,10; contra la constante μ el modelo gana
  0,42 [−0,98, +0,13] (contiene el cero);
  **errata en `dictamen_08/E.md`: «93 %» → 7,2 %** (anotada al pie).
  Circularidad real con R1: el juez lineal de esta corrida queda
  **EXPLORATORIO** hasta la firma. La enmienda suma 1 intento.
- **00:50** — Tipo I medido con el simulador calibrado (generador con
  ventaja verdadera −0,01 pp, 1.000 réplicas;
  `corrida09/tipo1_conjuncion_v1bis.json`): a 73 días MAE 0,039 [0,029,
  0,053], CRPS 0,049, DIR 0,045, **MAE ∧ CRPS 0,021 [0,014, 0,032]**, MAE ∧
  DIR 0,009; a 250 días **CRPS contra climatología EN MUESTRA 0,075 [0,060,
  0,093]** (inflado: por eso la climatología causal); y **m > 0 bajo
  ventaja nula el 54 % [51, 57]**: «contra cero» mide la deriva del gap.
  Enmienda reescrita como **v2** con el dictamen pegado al pie: la
  climatología causal decide, cero se publica al lado, V1 bloqueante,
  regla operativa de R2 para métricas continuas, V4 como regla general,
  V6 nombrado como «el cambio de pregunta en una línea», plan secuencial
  v5 inválido para magnitud. **Conflicto con D3 declarado y no resuelto
  por un agente** (D3 dice «contra predecir cero»): `espera_firma` §30.
- **01:06** — `horizonte.py` terminó (EXIT 0). **Ruta 3 (simulador
  calibrado) manda:** potencia del 25-oct (73 días) a 9 pp **0,30 [0,27,
  0,33]**, a 6,5 pp 0,18 [0,16, 0,21]; días para 0,80: 9 pp **269 [229,
  275] → 27-ago-2027** [25-jun-2027, 6-sep-2027]; 6,5 pp 510 [490, 531] →
  6-sep-2028; 5 pp 811 → dic-2029; 12 pp 141 → feb-2027. **Pareada ruta 2
  − ruta 3 sobre 28 celdas: la ruta 2 por encima en 23, por debajo en 1
  (McNemar exacto p = 3e-6), +2,17 pp [1,55, 2,81]** — verificado con el
  simulador, no con la bitácora: el «+2,7» de la bitácora 08 era sobre 12
  celdas de A4 (+2,67 [1,85, 3,55]); sobre las 28 de `horizonte` es +2,17.
  Las rutas 1 y 2 quedan como referencia comparada; α empírico de la ruta
  3 entre 0,039 y 0,059 en los siete horizontes.
- **01:10 → 10:05** — **Segundo incidente del límite de sesión** (reset
  05:10): murieron el auditor de look-ahead del juez lineal (sin dictamen)
  y el agente 2d (que ya había escrito `tarjetas_09.md` completo a las
  00:49); 2c y 2f sobrevivieron y terminaron a las 10:30 y 10:08. La
  corrida «nocturna» pasa a la mañana; la ventana de sellado (17:50–20:30)
  sigue lejos y nada pesado corre en ella.
- **10:30** — **2c cerrado** (`corrida09/noticias_on2.md`, `noticias.py`,
  `mki_noticias.py`, `tests/test_noticias_dedup_lineal.py` 7 tests; 302
  passed sobre los 17 archivos que tocan noticias): marca
  `dedup_retro_ultimo_id` en tabla aditiva `meta`; sólo las filas nuevas
  son candidatas y cada una se compara contra ±10 días de su `fecha` en
  las dos direcciones. MEDIDO sobre copia: vieja n = 5.286, 13,8 M
  comparaciones, **2.233 s**, 31 borrados; nueva primera pasada 4,9 M,
  **615 s**, 20 borrados; corrida diaria **34,7 s** (282 k); segunda pasada
  0,15 s. Los 11 que la nueva ya no borra están a 11,9–138 días de su
  original (comportamiento declarado). **`TimeoutStartSec=1800` alcanza;
  el parche a 2.700 s queda innecesario.** La primera corrida con el código
  es hoy 17:50 (≈ 13–15 min); una sola transacción: si la matan, la base
  queda intacta. Defecto propio del agente, corregido antes de medir:
  candidatura por `fecha` detectaba 1 de 20 (los titulares del día traen
  fechas viejas) → candidatura por `id`.
- **10:08** — **2f cerrado**. Parte 1 (`corrida09/ic_dmae_recomputados.md`):
  los artefactos del WS2b no guardan filas; recomputado desde caché con
  descarga bloqueada; **C1 reproduce** (215 filas; C1 vs campeón −0,1325 pp
  contra −0,1327 publicado), IC de clúster de día [−0,324, +0,035]
  (contiene el cero);
  **C2/C3 sólo parciales (79 filas, 11 días): `^VIX3M` no tiene datos en
  la caché desde el 17-jul** y con ffill acotado a 5 d las 14 features
  extra quedan NaN (hallazgo abierto: ¿Yahoo dejó de publicarlo?); WS3 NO
  EVALUABLE sin red. Contra cero: campeón +0,375 [−0,201, +0,955], C1 +0,362
  [−0,055, +0,803] — cada intervalo contiene el cero: **nadie mejora
  a cero de forma distinguible al nivel de día** (el bloque de filas de C1 sí lo excluía: la unidad cambia la
  respuesta). Ninguna conclusión del WS2b cambia; erratas al pie de
  `control_lineal.md` y `ventana_larga.md`. Parte 2:
  `propuestas/parches/motor_concat.diff` (`sort=True` preserva: pandas 3
  ordena hoy) + `tests/test_parche_motor_concat.py` **10 passed**
  (byte-idéntico en `betas_al`, `prediccion_apertura_al`,
  `divergencias_al`, `datos_cadena_al`, `roca_chip_al`; el warning
  desaparece). Parte 3 (`corrida09/ws4_cinco_preguntas.md`): Q5 MEDIDA —
  la regla firmada **ya sacó** 7 de las 8 filas del 29-jul; vivo n = 269
  +14,1 [−2,3, +30,9], sin las 8 +13,8 [−2,9, +30,7] (cada intervalo
  contiene el cero); Q2 resuelta en
  código (no por el acta §68: errata añadida); Q1, Q3, Q4 como tarjetas.
  Intentos: 14.
- **00:49** — **2d cerrado** (`corrida09/tarjetas_09.md`, 548 líneas,
  escrito antes de que el agente muriera; **journal no leído**, evidencia
  `data/*.log` en UTC desde el 25/26-ago, declarado). T1 abstención: A
  (salto de sesión) abstendría **15/269** filas (2 fechas; 3 aciertos, 12
  errores se van); B ≥ 19:00 32/269; B ≥ 20:30 ≡ ≥ 20:00 (apertura de Seúl)
  10/269; rec. A como flag retrospectivo en el campeón y regla sólo en el
  retador; la ventaja «sin A» (+18,5) NO se publica: es por haber mirado.
  T2 `ts_emision`: `timestamp_utc` y `creado_en` son el mismo instante por
  construcción; rec. `commiteado_en` (aditivo en `senales.py`) +
  `publicado_en` escrito por backup/reporte llenando sólo el campo vacío,
  nunca cambiando un valor. T3 `Persistent=true`: rec. M (mantener en 5;
  snapshot depende del parche `:140`: con parche `true` es seguro). T4
  campeón: rec. (a) las filas selladas + C3 copia de insumos en el mismo
  bump; «emitido antes» ≠ «reproducible después», escrito. Intentos: 7.
- **11:22** — Retomo tras el límite. `frase_potencia.py`
  (`corrida09/frase_potencia.md`): **dirección** 0,30 [0,27, 0,33] el
  25-oct, 269 días [229, 275] → 27-ago-2027; **magnitud** (MAE contra
  cero) 0,90 [0,87, 0,92] con el generador de 9 pp y 0,86 [0,83, 0,89] al
  efecto observado; potencia 0,80 en **58 días [54, 62] → 1-oct-2026**
  [25-sep, 8-oct] por el simulador (**ANTES del 25-oct**) y 96 [20, ∞) →
  1-dic-2026 al efecto observado (DESPUÉS); bajo R2 175 días. **Esa frase
  quedó retirada por el dictamen de las 12:20** (ver ese hito): la
  comparación ANTES/DESPUÉS no está ordenada cuando el intervalo del efecto
  contiene el cero. Auditor de
  look-ahead del juez lineal relanzado.
- **12:20** — Dictamen del adversario sobre 1b/3c (con otro modelo: el
  de `opus` cayó tres veces por 529): la tabla de potencia y la pareada de
  la ruta 3 **SOSTIENEN**; el intervalo «269 [229, 275]» **NO** (Wilson de
  celda invertida por bisección con una semilla: sólo Monte Carlo, y ni
  ése completo — verificó a tres semillas que 269 cruza 0,80 con una y no
  con las otras dos); la frase «58 [54, 62] → cae ANTES del 25-oct» **NO
  SOSTIENE** (condicional a un efecto MAE de 0,48 pp que el observado +0,44
  [−0,09, +0,96], que contiene el cero, no distingue; ANTES/DESPUÉS entre
  una fecha fija y una cantidad con IC [20, ∞) no está ordenado). Exigido y
  aplicado: bisección con 3 semillas y etiqueta «sólo Monte Carlo; banda
  paramétrica = ruta 1»; α de la ruta 3 a 3.000; pareada con las 12 celdas
  de A4 (+2,45 [1,64, 3,27], comparable con +2,67 [1,85, 3,55]) y las 7
  celdas en techo declaradas; ancla (31-ago, n 246) y N (310) declarados
  en la frase; log(D) vs lineal (58 vs 61) declarado; ninguna fecha
  encabeza. HOR-1b = 1 intento, correcto.
- **12:35** — `horizonte.py` v2 terminó (55 min). Días para 0,80 a 9 pp:
  **≈263** (mediana de 3 semillas; rango de semillas [252, 269]; rango MC
  [229, 296]; ruta 1 paramétrica 248 [109, 370]) → 18-ago-2027; 6,5 pp
  ≈510 [467, 580]; 5 pp ≈811; 12 pp ≈141. α de la ruta 3 a 3.000: entre
  0,041 y 0,058. `frase_potencia.md` v2 regenerada: banda de potencia de
  la magnitud a 73 días **0,90 / 0,86 / 0,70**, 96 [20, ∞) días al efecto
  observado → 1-dic-2026, ≈58 si el efecto fuera el del generador.
  `espera_firma` §29 reescrito. El auditor del juez lineal (4.º intento,
  lanzado 11:28) sigue sin responder.
- **12:40** — **Dictamen del `auditor-lookahead` sobre el juez lineal (5.º
  intento; los cuatro anteriores: límite de API, 529 ×2, uno colgado una
  hora sin escribir).** Sin fuga de valor futuro; **una fuga de
  disponibilidad demostrada**: la caché de cierres se bajó el 1-sep a las
  13:16 UTC y su fila del 1-sep trae `^SOX` en NaN (→ `sox_t = 0` por ffill)
  y barras intradía parciales de ES, NQ, VIX, GDAXI, EURUSD, TWD — el sello
  del 1-sep (7 filas) habría entrado con features no conocibles a las 22:15
  UTC; y **una selección de filas estructural**: con `^VIX3M` muerto desde
  el 17-jul, C2 sólo puede predecir fechas ≤ 24-jul (~88 filas, ~44 bajo
  R2): la selección la hace la disponibilidad del dato. Verificado limpio:
  `panel.fecha` es la emisión (no la sesión) y el embargo purga por
  construcción; α y σ del ridge sólo con el pasado; 0 filas con
  `intervalo80_pp` nulo o cero; 0 filas con sesión objetivo posterior a su
  verificación. Aplicado ANTES de correr (Enmienda 1 del pre-registro): se
  descarta toda fecha posterior a la última barra completa de `^SOX` en la
  caché cruda y se sella sha256 + mtime de cada caché; `verificar=True`;
  C2 tal cual con lectura restringida a filas comunes (no se crea «C2 sin
  vix_term»: sería la cuarta configuración); `assert` sobre σ del campeón;
  embargo declarado en días calendario; `tests/test_juez_lineal_d3.py` fija
  la guarda de descarga. Juez lanzado a las 12:41 (test 12:41:54; JSON 12:42:00).
- **12:42** — **Juez lineal bajo D3 corrido** (`corrida09/juez_lineal_d3.{md,json}`;
  EXPLORATORIO hasta la firma de V1-bis). 262 filas en 37 días (la fecha del
  1-sep excluida por la caché parcial: 7 filas); panel 15.027 filas; C1
  predice 254, C2 79 (11 días, ≤ 24-jul), campeón 262. **Ventana completa:
  C1 supera a predecir cero en MAE (+0,387 pp, t de clúster [+0,049, +0,725],
  p de día 0,021) y a la climatología causal en CRPS (+0,300 [+0,007,
  +0,593], p 0,038); el campeón NO supera (MAE +0,455 [−0,045, +0,954], p
  0,075: contiene el cero; CRPS +0,411 [−0,038, +0,861]); C1 − campeón −0,171
  [−0,375, +0,033] (contiene el cero); C2 − C1 +0,200 [−0,088, +0,488], p
  0,17 (contiene el cero); dirección: nadie supera. Bajo R2 (sin 15–23
  jul): nadie supera nada** (C1 MAE +0,335 [−0,055, +0,726], p 0,093).
  Registro de intentos 310 → **346** (JUEZ-3b, los 36 declarados antes de
  correr); 5.1: 352. Adversario despachado sobre el resultado.
- **12:44** — **Director de programa: ADELANTE con dos correcciones de
  texto; nada de código se revierte.** §7 del encargo respetado (sin 5.1,
  sin retador, intocables intactos, sin descarga, sin fuente nueva; 2c
  cambió `noticias.py`/`mki_noticias.py` como se pidió). Corregido:
  `estadistico-adversario.md` decía «V1 queda como secundaria» —aplicaba
  D3 al mandato del juez antes de la firma de V1-bis—: ahora «V1 sigue
  bloqueante hasta la firma»; y la cola §32 referencia el archivo de las
  tarjetas por su ruta. **Objeción registrada y no revertida:** el director
  habría dejado el juez lineal sin correr hasta firmar §30 (su vara
  primaria depende de «cero vs climatología», no firmado); el encargo §3b
  ordenaba correrlo y corrió EXPLORATORIO con los dos denominadores
  publicados; la nota de dependencia quedó en el pre-registro y la decisión
  de si computa es de Nicolás. Aguja: 1a, 2b, 2c, el dictamen «cambio de
  pregunta» y el tipo I medido. Rama: la réplica de 825 líneas, la ruta 3
  al detalle de semillas, Q1/Q3/Q4. Dictámenes sobre las recomendaciones
  en `espera_firma` §37 (T2 y réplica 4 y 7 cambian). Lo único que sigue:
  ver el vigía tras el 17:50 de hoy; después firmar V1-bis + §30 y luego el
  parche `:140`.
- **12:49** — **Errata propia, cazada por el adversario:** los cuatro
  hitos anteriores (auditor, juez lanzado, juez corrido, director) llevaban
  horas escritas sin leer `date` (12:52 / 12:58 / 13:00 / 13:05); los
  mtimes y el `generado_utc` del JSON dan 12:40 / 12:41 / 12:42:00 /
  12:44, y así quedan corregidos arriba. Es la segunda vez en esta corrida
  (la primera a las 00:42). Los mtimes de `juez_lineal_d3.py` y del
  pre-registro (12:43:38) son POSTERIORES al JSON porque después de correr
  se cambió la firma de la lambda de `_prohibir_descarga` (para el test) y
  se agregó la nota de dependencia del director: el código que corrió ya
  contenía los exigidos 1, 2 y 4 (los `parametros` del JSON lo muestran) y
  no hubo ninguna corrida anterior a la Enmienda 1 (un solo JSON).
- **12:50** — **Dictamen del adversario sobre el juez:** cifras SOSTIENEN
  (36 celdas reproducidas al 4.º decimal); **la lectura «C1 supera y el
  campeón no» NO SOSTIENE**: no son las mismas filas (C1 no predice el
  domingo 5-jul, 8 filas donde el campeón perdió −2,84 pp/fila contra
  cero); **sobre las 254 comunes el campeón supera a cero más que C1**
  (MAE +0,558 [+0,089, +1,027], p 0,021); la única comparación legítima es
  la pareada (−0,171 [−0,375, +0,033]: contiene el cero, a favor del
  campeón); C1 agrupada emite una sola predicción por día (signo del SOX
  encogido: C1 − campeón en dirección 0,000 exacto); **R2 se activa sobre
  C1**; la climatología agrupada sesga a favor de los modelos +0,012
  [+0,000, +0,023] sin mover celdas. Pregunta de fondo **NO CONCLUYENTE**.
  Aplicado en la regeneración (mismo código de hipótesis y semilla: las 36
  celdas reproducen; no suma intentos): celda campeón@C1, lectura honesta
  del §6, DIR ×100, JSON sin NaN, CSV por fila, trazabilidad en el
  pre-registro. Registro **352** (+6 ADV-3b); 5.1: 358.
- **12:58** — Suite completa (tercera pasada de la corrida): **649 passed,
  2 xfailed** en 5:05 (partió de 606 + 2; 43 tests nuevos: importador
  round-trip 16, parche `:140` 6, dedup lineal de noticias 7, parche
  `motor_concat` 10, juez lineal 2, árbitro +2); `tests/test_motor.py` OK.
  Guardián y curador (relanzado: el primero quedó colgado) en curso.
- **13:05** — **Cierre sin dos dictámenes: se agotaron los créditos de la
  API** y murieron el `guardian-constitucion` y el `curador-epistemico`
  (dos intentos), además del 4.º auditor que ya había sido reemplazado. El
  guardián se sustituye por **verificación mecánica propia, con evidencia**:
  `git diff --stat` sobre `motor.py`, `senales.py`, `snapshot.py`,
  `universo.py`, `version.py`, `calendarios.py` **vacío**; `.env`, `systemd/`
  y `launchd/` no aparecen en `git status`; `senales.db` conserva mtime
  2026-09-02 18:15:28 y 413.696 bytes y `data/backups/` está limpio;
  `.claude/hooks` sin cambios; rama `main`, nada por delante del remoto
  (nada pusheado); `ESTADO.md` 50 líneas; el test del árbitro en verde.
  Revisión de seguridad del único código de producción que cambió
  (`noticias.py`, corre hoy 17:50): `CREATE TABLE IF NOT EXISTS meta`
  aditivo, sin `DROP` ni `ALTER`, los dos `DELETE` son los que la función
  ya tenía (borra el duplicado y su análisis), un solo `commit()` al final
  — una transacción, como declara el informe. **Lo que NO se obtuvo y
  queda pendiente para Nicolás: el dictamen del guardián y el del curador
  epistémico sobre los textos públicos.** Curaduría propia parcial: la
  frase «antes del 25-oct» quedó marcada como retirada también en su hito;
  `ESTADO.md` y `estado_epistemico.md` ya leen el juez con la celda de
  filas comunes; ninguna cifra retirada reaparece (test).
