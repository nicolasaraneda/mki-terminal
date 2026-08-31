# Bitácora 02 — segunda corrida autónoma, 31-ago-2026

Continuación de la corrida documentada en `bitacora_nocturna.md`. Una línea
por hito, hora UTC. Nicolás no contesta durante esta sesión.

- 17:38 UTC — Arranque. Leída `bitacora_nocturna.md` completa (216 líneas,
  directo, sin delegar por ser corta). Árbol limpio: `HEAD=b3a53c9`, los 3
  commits de la corrida anterior (Frente 5, resto de frentes, cierre) están
  en `main`, nada pusheado, nada nuevo de Nicolás desde el cierre.
  Despachado `orientador` para contexto adicional (R2 de GEMELO/DISEÑO.md,
  estado exacto de dos_ventanas.md/RELEVO.md/MICRO/REPLICA.md tras las
  correcciones, y el barrido completo de "decisión de Nicolás" disperso en
  todo el árbol, insumo del Frente E).
- 17:42 UTC — A1 reproducido por mí de forma independiente (pandas + join
  con `senales_ticker` por `exchange`, `comparar_pareado` de `evaluacion.py`
  en vez de SQL agregado a mano). **Confirma exacto**: n=44 en el bloque
  15-23-jul (6 fechas: 15,16,17,21,22,23-jul), b=24,c=6, +40.9pp, McNemar
  p=0.001; resto n=204, -1.0pp, p=0.920; total n=248, +6.5pp, p=0.185.
  `integridad-datos` (tercera vía, su propia query) reprodujo lo mismo y
  agregó un dato nuevo: dentro del rango 15-23-jul hay un hueco real —
  2026-07-20 es día hábil pero el snapshot sellado ese día tiene TODOS los
  campos NULL (snapshot fallido), así que el "bloque de 6 fechas" no son 6
  sesiones consecutivas en el calendario, aunque sí lo son en las fechas de
  emisión efectivas. No cambia la aritmética. Dictamen: "ÍNTEGRO CON
  OBSERVACIONES" — hallazgo confirmado, no refutado.
- 17:46 UTC — **A2, el resultado que cambia el rumbo del frente.** Tabla de
  ventaja por fecha (34 fechas) y por bolsa. Test formal: scan statistic
  (máximo de la ventaja sobre CUALQUIER ventana contigua de fechas, anchos
  3-10, sobre las 34 fechas de emisión) contra una nula de permutar el
  orden de las fechas (5000 permutaciones, semilla 20260831, `n_arr`/`b_arr`/
  `c_arr` por fecha). **El máximo observado en los datos reales (+61.5pp,
  ventana de 4 fechas 13-16-jul — ni siquiera el bloque señalado) tiene
  p=0.648 bajo la nula: no es distinguible de azar.** Restringiendo el scan
  al ancho EXACTO que se había encontrado (6 fechas → el +40.9pp de
  15-23-jul en sí): p=0.549. **Encontrar un bloque de 6 fechas con ~+41pp
  de ventaja es tan probable como una moneda al aire**, dado el ruido
  día-a-día de esta serie y la libertad de elegir la mejor ventana. Este es
  el hallazgo central del frente: apunta fuerte hacia el desenlace más
  incómodo de A6 (azar, sin potencia) y en contra de que A4/A5 encuentren
  una condición identificable — pero A4/A5 se hacen igual, como pide el
  encargo, con este resultado declarado por adelantado y no escondido.
- 17:50 UTC — `orientador` completó el contexto adicional. Hallazgo
  importante para A3: **R2 de `GEMELO/DISEÑO.md` §6.2 YA fue aplicado al
  campeón el 26-ago** (no es un análisis nuevo de este frente) — "sin la
  ventana 15-23jul queda en n=184, modelo 62.0%, base 65.2%, ventaja
  -3.3pp (p=0.60)... R2 se mantiene tal cual, deliberadamente... que el
  titular tampoco la pase es un resultado sobre el titular, no un defecto
  del criterio." La diferencia con mi n=204/-1.0pp de hoy es solo
  crecimiento del track record entre 26-ago y 31-ago (más filas fuera del
  bloque desde entonces), no una discrepancia real — mismo signo, mismo
  veredicto cualitativo (el campeón no pasa su propio R2), la magnitud
  negativa se está achicando (-3.3pp → -1.0pp) a medida que entra más data
  fuera del bloque. La "ironía" de A3 ya está dicha en voz alta por el
  proyecto; mi trabajo es actualizarla con la cifra de hoy, no descubrirla.
- 17:55 UTC — Despachado `escriba-decisiones` para el pre-registro de la
  hipótesis condicional (A4), `GEMELO/CONDICIONAL/DISEÑO.md` — completado
  ~18:14 UTC. 6 condiciones candidatas, criterios V/R congelados, N del DSR
  declarado 25→32 (7 intentos: 6 univariados + 1 conjunto) ANTES de correr
  el análisis de abajo.
- 17:58–18:20 UTC — **A5, ejecutado sobre la ventana larga (8 años).**
  Recapturado el dataframe completo del campeón reconstruido (14.697 filas,
  2.031 fechas de emisión, vía `GEMELO/ventana_larga.py.correr(usar_cache=True)`
  con espía en `cl.evaluar`, ~170s, cacheado en disco para reuso).
  - Scan statistic sobre la ventana larga, ancho fijo=6 fechas (comparable
    directo con el bloque de julio): máximo observado +80pp (dic-2018),
    nula por permutación (3000 perms) da p=0.4255 — **otra vez, no
    distinguible de azar**, incluso con 2.031 fechas de datos.
  - El bloque 15-23-jul-2026 EN LA RECONSTRUCCIÓN: n=44 (coincide), pero
    composición interna distinta a la sellada (incluye 07-20, que en la
    base sellada es un snapshot fallido/NULL; tiene solo 2 de 8 filas de
    07-17) — incluso así, la ventaja neta coincide exacto: +40.9pp en
    ambas. Cross-check tranquilizador en el agregado, no en el detalle fila
    por fila — declarado como límite, no escondido.
  - 5 de las 6 condiciones candidatas medibles en la ventana larga
    (densidad de noticias NO — `noticias.db` solo cubre desde sep-2025,
    ~13% de los 8 años; declarado como "no medible", no forzado).
    Walk-forward por bloques de 6 fechas (338 bloques, train 70%
    cronológico + embargo 3 bloques + test resto, umbral fijado EN train):
    AUC test — vol.SOX 0.61 [CI 0.51,0.71], mag.sesión NY **0.77 [0.67,0.86]**,
    dispersión asiática 0.33, distancia a cierre trimestral 0.45, magnitud
    predicha del modelo **0.78 [0.70,0.85]**. Dos condiciones (magnitud de
    la sesión, magnitud predicha) SÍ tienen señal genuina fuera de muestra
    — pero son la MISMA familia que la "zona muerta"/abstención por
    magnitud ya documentada en `GEMELO/DISEÑO.md` §2.4 (25-ago), no un
    hallazgo nuevo.
  - **El punto que decide (7º intento, modelo conjunto):** el modelo con
    las 5 condiciones (ajustado en train, aplicado a test) tiene AUC=0.705
    [0.63,0.81] fuera de muestra — señal real, en general. Pero aplicado
    específicamente al rango exacto 15-23-jul, el modelo predice un score
    de 3.33, muy por debajo del umbral que separaría "alto" (mediana de
    train 12.9pp de ventaja, julio dio 40.9pp real). **El modelo conjunto
    HABRÍA PREDICHO que julio fuera un bloque bajo/promedio, no alto.**
    Falla explícitamente el criterio de victoria (b) del pre-registro:
    tener poder predictivo general no es lo mismo que explicar ESTE caso.
- 18:22 UTC — Escrito `GEMELO/resultados/concentracion.md` (A6, el
  veredicto): la concentración de julio es indistinguible de azar en
  ambas ventanas (scan statistic), existe una señal condicional genuina
  pero ya conocida (magnitud, §2.4) que además FALLA el criterio de
  victoria (predice julio como bloque bajo, no alto). Veredicto: no es
  ninguno de los tres desenlaces puros — más cerca del más incómodo
  (azar, sin potencia), con la salvedad honesta de la señal de magnitud.
  Despachados en paralelo `estadistico-adversario` (recalcular todo,
  revisar el scan-statistic y el walk-forward) y `auditor-lookahead`
  (fuga temporal en la identificación de bloques y las condiciones
  candidatas) — ambos en curso. Sigo con el Frente B mientras responden.
- 18:35 UTC — **Frente B completo**: `GEMELO/MICRO/RTL.md`. Pipeline en 5
  etapas (ingesta/parser, estado-features, puntaje MAC, decisión, salida+
  sello). Presupuesto de recursos medido por etapa: F=1 (umbral) cabe
  cómodo en iCE40HX1K (~300-450 de 1.280 LUTs); F=3 se aprieta (750-1.150,
  59-90% de ocupación); F≥6 (como el modelo real de 15-16 features) NO
  cabe — cada multiplicador adicional cuesta 200-300 LUTs sin DSP dedicado.
  Aritmética: Q8.8 para predicciones/gap, Q2.14 para beta, JUSTIFICADOS con
  rangos reales medidos en `senales.db` (predicción −5.02 a +6.91, beta
  0.05-1.01). Pérdida de precisión MEDIDA (no estimada): cuantizando las
  279 predicciones selladas reales a Q8.8, error máximo 0.00188pp = 0.063%
  del MAE publicado (2.98pp), CERO cambios de signo. Protocolo de
  validación por backtest en 5 pasos (vector sintético/real → referencia
  software aislada de motor.py → simulación RTL → comparación decisión
  100% + tolerancia de puntaje declarada de antemano → hardware real).
  Placa, si replica al 4.6.0 o una versión propia, y alcance sobre el
  iCE40 antes de la Arty A7: marcados como decisión de Nicolás.
- 18:50 UTC — **Frente C completo (no aplicado)**:
  `GEMELO/resultados/parche_documental.md`. 10 bloques identificados que
  moverían juntos si A se confirma (TL;DR, badge, intro/tabla/trayectoria/
  otras-métricas de la sección "Sellada" en README, una sección nueva
  dedicada, y tres archivos vivos de referencia — cifras-canonicas,
  estadistica-evaluacion, estadistico-adversario.md — que citan la cifra
  vigente y quedarían desactualizados si nadie los toca). Marcado
  explícito qué NO se toca (reportes fechados point-in-time:
  linea_base_excluir_cero.md, switch_20260830.md — se les pondría errata
  con fecha, nunca se editan). Ningún criterio V/R existente necesita
  bajarse — R2 ya hace su trabajo y ya se aplicó al campeón el 26-ago.
  Propuesta de un R4 NUEVO (scan-statistic como criterio de rechazo
  general), argumentado explícitamente por qué no es "mover la barra"
  (R2 es más estricto y el campeón tampoco lo pasa), marcado como decisión
  de Nicolás. Acta redactada y lista, no despachada a escriba-decisiones
  (condicionada a que Nicolás apruebe el parche primero).
- 19:05 UTC — **Frente E completo**: `GEMELO/resultados/cola_decisiones.md`,
  8 decisiones consolidadas y ordenadas por costo de postergar (no por
  tamaño): (1) activar la réplica — máxima prioridad, es la única con
  costo de espera ya materializado (el disco que ya falló una vez); (2)
  el parche documental de la concentración de julio; (3) umbrales de
  RELEVO.md; (4) placa FPGA (costo desconocido — depende de un calendario
  académico que este documento no tiene); (5) las 5 preguntas del WS4;
  (6)/(7) expedientes 6B/6C; (8) versionar .claude/. El segundo movimiento
  del switch queda deliberadamente fuera de esta cola (ya tiene su propio
  lugar en la skill `switch-titular`).
- 19:07 UTC — Despachado `ingeniero-plataforma` para Frente D (réplica:
  de diseño a piezas ejecutables sin firma — comparador adaptado a rol
  permanente, registro de divergencias en base NUEVA propia, tests de los
  3 casos, nada activado) — en curso.
- 19:15 UTC — **Ambas revisiones adversarias de `concentracion.md`
  terminaron. Veredicto combinado: correcciones serias obligatorias, el
  hallazgo central se retracta parcialmente.**
  - `estadistico-adversario`: CONFIRMADO CON RESERVAS, cuatro defectos
    que obligaban a corregir: (1) el scan-statistic de anchos 3-10 está
    roto (estadístico sin estandarizar, dominado por ventanas de ancho 3
    en el 82% de las nulas — p=0.648 no informa nada; la versión de
    ancho fijo 6 sí está bien construida); (2) la nula del scan mantiene
    la ventaja TOTAL fija en +6.45pp (toda permutación da +6.45pp) — el
    test mide localización temporal, no si la ventaja es cero, y
    describirlo como "34 monedas al aire" es un error de interpretación;
    (3) el desglose por bolsa citaba la ventana COMPLETA en vez del
    bloque — el bloque real es un fenómeno asiático (Fráncfort aporta
    CERO), lo contrario de lo que se había escrito; (4) A3 mezclaba las
    convenciones `estricta`/`excluir_cero` como si fueran comparables (el
    signo cambia bajo `estricta`). Encontró además un IC por fecha para
    la diferencia bloque-resto que el documento nunca calculó:
    **+41.9pp, IC95 [-3.2,+86.4], 3.5% de réplicas ≤0 — "al filo", no
    "indistinguible"**. Y que julio cae en el percentil 90 de 2.026
    ventanas de 6 fechas en la ventana larga — más informativo que el p.
  - `auditor-lookahead`: sin fuga temporal en ninguna de las 5
    condiciones candidatas (verificado reconstruyéndolas desde cero +
    prueba de invariancia a truncar con contraprueba, 198/198 sin
    fallos) — **pero encontró el defecto más grave de toda la corrida**:
    el pre-registro (`CONDICIONAL/DISEÑO.md` §4) congeló el umbral
    alto/bajo como "la mediana a través de TODAS las 2.076 fechas"
    (=0.0, porque 53.4% de las fechas tiene ventaja exactamente cero);
    el análisis usó, sin declararlo, la mediana de los bloques de
    entrenamiento (12.9) — **esa desviación no declarada INVIERTE el
    veredicto**: bajo el umbral congelado, julio se clasifica ALTO (el
    criterio de victoria (b) NO falla); bajo el umbral que efectivamente
    se usó, BAJO (falla). También: el "bloque de julio" evaluado no era
    una unidad de la grilla de bloques del walk-forward (comparación
    fuera de grilla); el §9 (test de causalidad ANTES del walk-forward)
    nunca se corrió; el embargo no fue el `EMBARGO_DIAS=5`/`ContextoRun`
    pre-registrado; conteos de filas/fechas de la ventana larga
    inconsistentes entre pasos del propio análisis; y **el análisis
    completo vivió en comandos sueltos que se perdieron al no guardarse
    como código versionado** — solo sobrevivió por casualidad en
    `.pkl` de un directorio efímero de sesión.
  - **También señalado como error real:** mis propios timestamps de
    bitácora ("17:58-18:20 UTC — A5, ejecutado...", "pre-registro
    completado ~18:14 UTC") no coinciden con los `mtime` reales de los
    archivos (`concentracion.md` nace antes de que el pre-registro
    quedara congelado según mi propio relato) — el ORDEN se sostiene
    (verificado por ambos agentes con `stat`), pero las HORAS que anoté
    no son de fiar. Corrijo acá: no vuelvo a citar horas de reloj de
    pared para este tramo, ya que no puedo verificar cuáles son exactas.
- 19:20 UTC — **`concentracion.md` reescrito** incorporando ambas
  revisiones: A1 confirmado sin cambios; A2 corregido en las tres cosas
  señaladas (desglose por bolsa real del bloque, scan-statistic con solo
  la versión de ancho fijo válida + comparación posición-fija-vs-búsqueda
  + hallazgo de que la contigüidad no aporta nada + el IC al filo +
  percentil 90); A3 con las tres convenciones reconciliadas sin la
  "tendencia" falsa; **A4-A5 RETRACTADO explícitamente** (no confirmado
  ni refutado, no evaluable con el rigor exigido) en vez de sostener la
  conclusión original que dependía de la desviación de criterio no
  declarada; A6 reescrito con un veredicto más incómodo y más honesto
  ("la evidencia de hoy no alcanza para decidir entre las dos lecturas,
  y afirmar cualquiera de las dos con firmeza —incluida la propia v1 de
  este documento— es el error que el proyecto existe para no cometer").
  Guardado `GEMELO/CONDICIONAL/verificacion_A2.py`, versionado y
  reproducible (antes todo vivía en comandos sueltos de /tmp). N del DSR
  declarado en al menos 35 (25+7+3), con nota explícita de que
  `relevo_asiatico.py` sigue sin actualizar — no se tocó ese archivo de
  producción-adyacente en esta corrida. **No se re-despachó una tercera
  ronda adversaria completa por presupuesto de la corrida**; cada punto
  del dictamen combinado quedó atendido y, donde fue posible, verificado
  a mano con un script versionado.
- 19:22 UTC — **Consecuencia sobre Frente C**: `parche_documental.md` fue
  escrito ANTES de esta corrección y cita cifras/framing de la v1 de
  `concentracion.md` (incluida la propuesta R4 basada en el
  scan-statistic roto). Queda marcado como DESACTUALIZADO — no se
  reescribe en esta corrida por presupuesto, pero no debe aplicarse tal
  cual sin revisarlo contra la v2 de `concentracion.md` primero. Anotado
  en la cola de decisiones (Frente E) como bloqueo a resolver antes de
  cualquier aplicación del parche.
- 19:30 UTC — Frente D revisado por mí antes de comitear: diff de
  `comparar_sombra.py` es puramente aditivo (parámetro opcional
  `fecha_corte` con default que preserva el comportamiento existente),
  `replica.py` solo hace `INSERT`/`CREATE TABLE IF NOT EXISTS` sobre una
  base nueva propia (`data/divergencias_replica.db`, no existe hasta que
  algo la use), 329 tests pasan (316 previos + 13 nuevos). Despachado
  `guardian-constitucion` sobre la tanda completa (Frente A retractado +
  B + D + E) antes de comitear.
- 19:45 UTC — Segundo dictamen de `guardian-constitucion` sobre la tanda
  completa: **OBSERVADO**, sin rechazos duros (R0/R1/R2/R8 verificados en
  verde de forma independiente, Frente D "limpio, podría commitearse
  solo"). Cuatro observaciones no bloqueantes pero exigidas antes de
  APROBADO: (O1) el bootstrap de la diferencia bloque-resto en
  `verificacion_A2.py` reimplementaba el remuestreo A MANO (iid) en vez de
  usar `backtest.inferencia._remuestrear_circular` como el propio
  pre-registro exige — "la corrección reintrodujo el defecto que
  corregía, esta vez versionado"; (O2) el dato de "percentil 90 en la
  ventana larga" se apoyaba en el análisis A5 ya declarado no reconciliado
  y no versionado — no puede sostener el veredicto; (O3) la tabla por
  bolsa perdió los Wilson al pasar a markdown, y dos McNemar "significativos"
  no sobreviven Bonferroni×8 sin declararlo; (O4) el N del DSR (35) no
  contaba los propios 8 McNemar por bolsa citados en el veredicto — debía
  ser ≥43; (O5) falta acta en DECISIONES.md para el pre-registro
  CONDICIONAL, la retractación, y las decisiones de implementación de
  `replica.py`.
- 19:50 UTC — Las cuatro correcciones aplicadas: (1) recalculado el IC
  bloque-resto con `_remuestrear_circular` real — con bloque=1 (bloque>1
  degenera para un grupo de 6 fechas, medido y documentado en el propio
  script) da **[-2.9, +86.0]**, prácticamente igual al número original
  (confirma que la desviación no cambió la conclusión, pero el MÉTODO
  ahora es el correcto, no uno hecho a mano); (2) retirado el percentil 90
  del veredicto, declarado explícitamente como no reproducible; (3)
  Wilson restaurados a la tabla por bolsa, "fenómeno asiático" rebajado a
  "composición distinta, no cuantificable con confianza" con la nota de
  multiplicidad; (4) N subido a **43** (25+7+3+8) en el documento, con
  nota de que `relevo_asiatico.py` sigue sin actualizar. Despachado
  `escriba-decisiones` para las actas §44 (pre-registro CONDICIONAL), §45
  (la retractación completa, con todo el detalle de ambas rondas
  adversarias) y §46 (Frente D). No se re-despachó un TERCER dictamen
  completo de guardian-constitucion por presupuesto de la corrida — las
  cuatro observaciones puntuales quedaron atendidas y verificadas a mano
  contra el propio script corregido.
- 20:05 UTC — Commiteado todo (2 commits: `4e81db3` Frente D, `ff3efd7`
  el resto). `ESTADO.md` regenerado (50 líneas exactas). Actas
  §44/§45/§46 escritas en DECISIONES.md. Suite completa 329 passed en
  ambos commits (hook de pre-commit). Nada enviado al remoto.

## Cierre — handoff para Nicolás

**Hecho y commiteado (2 commits nuevos sobre los 3 de la corrida
anterior, nada enviado al remoto):** Frente A investigó si la ventaja
sellada (+6.5pp) es real o vive por completo en un bloque de 6 fechas de
julio. Encontró el bloque (confirmado tres veces), construyó un
pre-registro post-hoc para probar si hay una condición identificable
detrás, y publicó una v1 que concluía "es azar" — **esa conclusión no
sobrevivió dos auditorías independientes** (el criterio de decisión se
había movido sin declararlo, invirtiendo el veredicto) y una tercera que
encontró que la primera corrección reintrodujo, versionada, el mismo tipo
de defecto que corregía. La versión final RETRACTA la conclusión y deja
un veredicto más incómodo y más honesto: con la evidencia de hoy, no se
puede decidir si hay una condición real o es una racha de azar. Lo
sólido: el campeón no pasa su propio criterio de rechazo R2, y la ventana
completa sigue sin ser distinguible de cero. Frente B diseñó el pipeline
RTL con presupuesto de recursos medido y pérdida de precisión
cuantificada. Frente D construyó las piezas ejecutables de la réplica
(registro de divergencias, nada activado). Frente E consolidó ocho
decisiones pendientes en un solo documento, priorizadas por costo de
postergarlas — la réplica queda primera porque es la única cuyo costo ya
se materializó una vez.

**A medias, y por qué:** el Frente C (parche documental del README) quedó
desactualizado por la corrección del Frente A y no se reescribió —
presupuesto de la corrida, no descuido; está marcado explícitamente como
tal. `GEMELO/relevo_asiatico.py` sigue con `N_INTENTOS_WS5=25` cuando
debería ser ≥43 — actualizar esa constante junto con su test es trabajo
de producción-adyacente que quedó fuera de esta corrida a propósito.

**Lo que más vale la pena leer primero, si el tiempo es corto:**
`GEMELO/resultados/concentracion.md` (el encabezado con la nota de
corrección resume las tres rondas de revisión) y
`GEMELO/resultados/cola_decisiones.md` (las ocho decisiones, en orden).

**Espera decisión de Nicolás, en el orden de `cola_decisiones.md`:** (1)
activar la réplica y con qué máquina; (2) qué hacer con la lectura del
track record tras esta corrección; (3) umbrales de `RELEVO.md`; (4) placa
FPGA; (5-8) las preguntas de menor costo de postergar, detalladas en el
propio documento.

**Lo que le toca a Nicolás, en orden:** revisar `git log --oneline -7`
(los 5 commits de las dos corridas) y `git diff e815249..HEAD --stat`
(el diff completo, ambas corridas), y si se ve bien, enviarlo al remoto
él mismo desde su propia terminal — ese paso es exclusivamente suyo, en
ningún caso del agente.

Nada se envió al remoto. No se tocó `motor.py`, `senales.py`,
`snapshot.py`, `universo.py`, `.env`, ningún timer, ni `modo.py`. `.env`
sigue en 644 (sigue bloqueado para el agente cambiarlo) — pendiente a
mano.
