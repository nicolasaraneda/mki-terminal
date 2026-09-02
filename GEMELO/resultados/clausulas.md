# El banco de pruebas de cláusulas, y las cuatro que estaban sobre la mesa

**Generado:** 2026-09-02 · `python -m GEMELO.banco_clausulas` · semilla 0 · `senales.db` en `mode=ro`.

**Este documento no aplica ninguna cláusula, no recomienda ninguna y no mueve ninguna cifra publicada.** Reporta lo que tres pruebas fijas dicen de cada una. Donde una falla, se dice cuál y con qué evidencia; donde pasan todas, también.

**El banco vale más que las cuatro respuestas.** Está escrito para recibir una cláusula como función (`Clausula` + `evaluar`), así que la quinta —la que todavía no existe— se evalúa sin tocar una línea de este módulo. Las cuatro de hoy son instancias.

---

## 0. La base, y la advertencia que va pegada a toda cifra de acá

- Ventana sellada **pinchada al 2026-08-31** (`hasta_sello`): **n = 256** filas bajo la convención congelada `excluir_cero`, **sin deduplicar** (`dedup=False`).
- **Por qué pinchada y no viva.** Este informe se corrió por primera vez el 1-sep-2026 contra la ventana VIVA, y esa misma noche el snapshot de las 18:15 selló un día más: la ventana pasó de 256 a 271 filas y la validación externa del banco —que reproduce una cifra publicada— se rompió sola. Toda cifra de acá es reproducible **porque el instante está pinchado**; contra la base viva no lo sería, y dejaría de serlo cada noche a las 18:15.
- **`dedup=False` está declarado, no elegido por comodidad:** las cláusulas bajo prueba son ellas mismas reglas de arbitraje o de población, y correrlas encima de la regla firmada mediría la composición de las dos, no la cláusula. La regla firmada entra como **C0**, de referencia, para que su propio movimiento esté en la misma tabla.
- **Las cifras de la base `dedup=False` son ANTERIORES a la firma del 1-sep.** Acá aparecen como *lo que la cláusula recibe*, nunca como cifra vigente. **La cifra vigente de la ventana sellada es la de la regla firmada: +9,7 pp, IC95 de clúster de día [−7,2, +26,5], n efectivo 67.** Un p sin ese intervalo al lado no se cita.
- **Cruzar α no es tener evidencia.** Todo p de este informe va con su intervalo de clúster; donde el intervalo contiene el cero, se dice con esas palabras.
- Ventana de solapamiento EVIDENCIADA (leída de `data/sombra/veredictos.jsonl`, no cableada): **2026-08-26, 2026-08-27**.

### La contraprueba del banco

Un banco que no puede reprobar nada no mide nada. `CLAUSULA_TRAMPA` lee `acierto_gap` a propósito y se queda con las filas que el modelo acertó. La PRUEBA 1 **la reprueba**: 1a REPRUEBA, 1b REPRUEBA. No es candidata y no cuenta como intento.

### La validación externa del banco

Que el banco reprueba lo que tiene que reprobar no prueba que MIDA bien lo que deja pasar. Así que además reproduce una cifra que otra vía ya midió: **C4b tiene que dar la cifra publicada de `keep="first"`** (`GEMELO/resultados/dedup_opciones.md` §A2, n = 241, b/c = 72/56). Obtenido: **n = 241, b/c = 72/56** → **reproduce**. Si no reprodujera, nada de lo demás valdría.

---

## 0 bis. Un hallazgo estructural que cambia cómo se lee la cláusula 3

**El criterio de la cláusula 3 —«selló a tiempo», leído contra la apertura de la sesión— y el criterio de la regla YA FIRMADA —«la sesión sellada calza con `available_at`»— son el MISMO indicador, fila por fila.**

Medido, no supuesto: coinciden en las **256 de 256** filas de la ventana (0 en desacuerdo). Las dos marcan exactamente las mismas **25** filas — las 25 del defecto de `snapshot.py:140` que el expediente `parche_snapshot140.md` §4 ya había censado por otra vía.

**Y tiene que ser así por álgebra, no por casualidad:** `sesion_objetivo` se selló como `proxima_sesion_despues_de(exchange, ahora_utc)`, así que calza con la sesión que implica `available_at` **si y sólo si** ninguna apertura cayó entre `available_at` y el instante del sello — que es literalmente «selló antes de que abriera». La medición está igual porque un argumento algebraico sobre código que nadie recompiló es una hipótesis.

**Consecuencia, y es la que hay que leer despacio:** todo lo que la PRUEBA 1c mide sobre la cláusula 3 vale, palabra por palabra, sobre el criterio de la regla que ya está firmada y aplicada. La pregunta «¿es metadata en la forma y resultado en el fondo?» no es una pregunta sobre una candidata: es una pregunta sobre lo que ya está corriendo. Este banco no la responde ni la usa para pedir nada — la deja escrita con su medición al lado.

---

## 1. El veredicto, en una tabla

Siete corridas: las **cuatro cláusulas del encargo** (la 3 en sus dos lecturas, C3a y C3b, y la 4 en las suyas, C4 y C4b), más la regla YA FIRMADA como referencia (C0).

| cláusula | P1 metadata | P1c asociación | P2 b/c | P2 exige mecanismo | P3a retroactivo | P3b ruta | veredicto |
|---|---|---|---|---|---|---|---|
| C0 | pasa | contiene cero | 72/56 → 72/49 | SÍ | 5/21 y 1/7 | pasa | no reprobada · COSTO RETROACTIVO en 3a · EXIGE MECANISMO en la PRUEBA 2 |
| C1 | pasa | contiene cero | 72/56 → 72/56 | no | 21/21 y 7/7 | pasa | PASA LAS TRES |
| C2 | pasa | contiene cero | 72/56 → 0/0 | no | 0/21 y 0/7 | pasa | no reprobada · COSTO RETROACTIVO en 3a · SIN PODER RESOLUTIVO (la población que deja no distingue al campeón de la baseline) |
| C3a | pasa | contiene cero | 72/56 → 72/49 | SÍ | 5/21 y 1/7 | pasa | no reprobada · COSTO RETROACTIVO en 3a · EXIGE MECANISMO en la PRUEBA 2 |
| C3b | pasa | IC contiene cero · p cruza α | 72/56 → 72/49 | SÍ | 5/21 y 1/7 | pasa | no reprobada · COSTO RETROACTIVO en 3a · EXIGE MECANISMO en la PRUEBA 2 |
| C4 | REPRUEBA | no aplica | 72/56 → 72/56 | no | 8/21 y 3/7 | pasa | REPROBADA en la PRUEBA 1 (lee el resultado) |
| C4b | pasa | no aplica | 72/56 → 72/56 | no | 7/21 y 3/7 | pasa | no reprobada · COSTO RETROACTIVO en 3a |


> C0 es la regla ya firmada y aplicada: está en la tabla como referencia, no como candidata.

---

## 2. Las dos preguntas del encargo, respondidas

### ¿Qué cláusula falla qué prueba?

- **C1 (era del Mac)** — no falla ninguna. Retira 16 filas y las 16 son CONCORDANTES: Δb = 0, Δc = 0. Es la única que no mueve nada de la estructura de discordancia, y sobre la ventana congelada retira cero filas, así que las anclas reproducen 21/21 y 7/7 incluso aplicada al pasado.
- **C2 (las dos máquinas)** — pasa la 1 y la 3b, pero deja **16 filas y CERO pares discordantes**. No dispara la alarma del b/c porque no queda nada sobre lo que haya asimetría. Eso no es un aprobado y el banco lo marca SIN PODER RESOLUTIVO: con 0 discordancias el duelo campeón-vs-baseline no distingue nada, en ninguna dirección.
- **C3a y C3b (la que selló a tiempo)** — pasan la 1a y la 1b, pasan la 3b, y **disparan la alarma de la PRUEBA 2**: Δb = 0, Δc = -7, y las 7 discordantes retiradas favorecen TODAS a la baseline (binomial exacta p = 0.0156). Es la misma firma que destapó `keep="last"`, y el banco no las acepta sin que alguien exhiba el mecanismo.
- **C4 (si son iguales, contar una vez)** — **REPROBADA en la PRUEBA 1** en su lectura literal: «iguales» sólo puede leerse sobre el desenlace, porque las dos filas de un par difieren en todo lo demás. Lo declara (1a) y además se mide (1b: la selección cambió en las 200 de 200 permutaciones del resultado). **Su segunda lectura, C4b —«iguales» = el mismo evento— pasa la 1**, y resulta ser exactamente el `keep="first"` ya medido.

### ¿La cláusula 3 correlaciona con el acierto?

**Medido, no supuesto — y la respuesta honesta tiene dos mitades que hay que leer juntas.**

| lectura de «a tiempo» | acierto a tiempo | acierto tarde | diferencia | IC95 clúster de día | p de permutación de día |
|---|---|---|---|---|---|
| C3a (antes de la apertura) | 70.1% (231) | 24.0% (25) | **+46.1 pp** | [-22.8, +70.3] | no aplica (el criterio varía dentro del día) |
| C3b (ventana 17:50–20:30) | 69.7% (228) | 32.1% (28) | **+37.6 pp** | [-23.0, +59.3] | **0.0319** (31 días contra 4) |

**Primera mitad: el punto es enorme y va en la dirección que importa.** Las filas selladas tarde aciertan el gap 24% contra 70% de las selladas a tiempo — una brecha de 46 pp. Un sello tardío usa datos distintos, y eso es exactamente el defecto de `snapshot.py:140`: la puntualidad NO es una etiqueta neutra pegada a la fila.

**Segunda mitad: no alcanza para establecerlo.** El IC95 de clúster de día **contiene el cero en las dos lecturas**, y en C3b la permutación de día cruza α (p = 0.0319) mientras el intervalo no excluye nada — **una discrepancia entre dos rutas de clúster, no una evidencia**. La razón es contable y no estadística: hay **28 filas tardías en 4 días**, y un puñado de clústeres no resuelve nada.

**La lectura que el banco deja escrita, sin recomendar:** con estos datos la cláusula 3 **no se puede declarar limpia de resultado**, y tampoco se puede declarar contaminada. El punto es demasiado grande para tratarlo como ruido y el intervalo demasiado ancho para tratarlo como hallazgo. **«No se puede descartar» es la parte que pesa**, porque el sentido del defecto —el sello tardío usa otros datos— ya está establecido por el código, no por estos números.

---

## C0 — la regla firmada (referencia, NO candidata)

> «dentro de cada par, la fila válida es la de sesión objetivo correcta según `available_at`, nunca la más fresca»

**Operacionalización.** `backtest.linea_base.deduplicar_por_sesion`, importada tal cual: el banco no la reimplementa

**Procedencia.** firmada el 1-sep-2026; DECISIONES.md, acta de la regla de deduplicación; ya APLICADA en el ejecutable

- Entra al banco para que su propio movimiento de b/c esté en la misma tabla que el de las candidatas. NO suma un intento: sus cifras ya están publicadas y la regla ya está aplicada.

### PRUEBA 1 — metadata

- **1a (declarativa).** Campos declarados: `exchange`, `available_at`, `sesion_objetivo`, `ticker`. Ninguno prohibido, ninguno sin clasificar → **pasa**.
- **1b (medida: invarianza).** Se permutaron los campos de resultado 200 veces; la selección cambió en **0** (IC95 Wilson de la fracción [0.000, 0.019]) → **pasa**: la cláusula no lee el desenlace.

- **1c (medida: asociación criterio↔acierto).** Filas con criterio: 231, acierto 70.1% (Wilson [63.9, 75.7] — **optimista**, supone filas independientes). Sin criterio: 25, acierto 24.0%.
  **Diferencia +46.1 pp, IC95 de clúster de día [-22.8, +70.3]**; sin p de permutación de día (el criterio varía dentro de un mismo día: la permutación de etiqueta de día no es el test correcto y no se reporta un p que no aplica); en su lugar, la fracción de réplicas bootstrap del otro lado del cero es **0.030** — no es un p y no se cita como uno.
  ICC del acierto 0.431, efecto de diseño 3.82 → **n efectivo 67** sobre 35 días.
  **el intervalo CONTIENE el cero y no hay permutación de día válida (el criterio varía dentro del día), así que el intervalo es la única ruta: con estos datos no se puede distinguir asociación de ausencia de asociación — no es un permiso, es una falta de resolución, y con un punto de +46.1 pp la parte que pesa es que tampoco se puede descartar.**

### PRUEBA 2 — la del b/c

| | n | b | c | ventaja | IC95 clúster | p exacta |
|---|---|---|---|---|---|---|
| antes | 256 | 72 | 56 | +6.2 pp | [-10.2, +23.0] | 0.1847 |
| después | 246 | 72 | 49 | +9.3 pp | [-7.2, +26.3] | 0.0451 |

**Δb = +0 · Δc = -7.** Retiró 10 filas: 0 discordantes a favor del MODELO (`b`), 7 a favor de la BASELINE (`c`), 3 concordantes.

De las 7 discordantes retiradas, **7 favorecían a la baseline** (100%, IC95 Wilson [65%, 100%], binomial exacta contra una moneda p = 0.0156).

> **EXIGE MECANISMO** — mueve `c` y NO mueve `b`; todas las discordantes retiradas tienen el mismo signo. Es la firma que destapó `keep="last"`. No queda refutada por esto: queda pendiente de que alguien exhiba por qué el defecto que corrige es asimétrico, ANTES de aceptarla y por impecable que suene el razonamiento.

### PRUEBA 3 — anclas

Sobre `cargar(hasta_sello=2026-08-24, dedup=False)` (228 filas), la cláusula retira **10**.

- **3a — costo retroactivo.** §2 (`estricta`): **5/21** · línea base §2.8 (`excluir_cero`): **1/7**. **NO reproducen.** Rotas en §2: ['n (verificaciones 4.6.0)', 'modelo: aciertos', 'modelo: acierto de gap %', 'baseline: aciertos', 'baseline: acierto de gap %', 'ventaja pp', 'McNemar b10', 'McNemar p', 'MAE modelo', 'MAE predecir 0.0', 'MAE predecir la media', 'cobertura del intervalo 80%', 'ratio ancho/error', 'R² sellado medio', 'zona muerta 0.25: n', 'zona muerta 0.25: ventaja pp']; en la línea base: ['n', 'modelo: acierto %', 'baseline: acierto %', 'ventaja pp', 'McNemar b10', 'McNemar p']. Si la cláusula se adoptara, la rama histórica `dedup=False` tendría que seguir existiendo y habría que declarar cuál afirmación se reproduce por cuál ruta.
- **3b — ruta del ancla preservada (FATAL si falla).** Recargando el ancla desde cero después de correr la cláusula: §2 **21/21**, línea base **7/7**; base sin mutar: **sí**. **PASA.**

**Veredicto del banco: no reprobada · COSTO RETROACTIVO en 3a · EXIGE MECANISMO en la PRUEBA 2.**

---

## C1 — considerar las filas de cuando cerraba sólo el Mac

> «considerar las filas de cuando cerraba sólo el Mac»

**Operacionalización.** conserva las filas cuya `fecha` cae en la era en que el Mac era la única máquina que sellaba: `fecha <= 2026-08-25` y fuera de la ventana de solapamiento evidenciada. El corte sale del documento de composición canónica y se corrobora contra `plataforma_version`, que está sellada por fila.

**Procedencia.** propuesta de Nicolás, sexta corrida: construir la regla desde el historial de máquinas

- Es una cláusula de POBLACIÓN, no de arbitraje: no elige entre dos filas que compiten, elige una era entera. Las 25 filas del defecto de `snapshot.py:140` son TODAS de la era del Mac, así que esta cláusula las conserva a las 25.

### PRUEBA 1 — metadata

- **1a (declarativa).** Campos declarados: `fecha`, `maquina`, `solapamiento`, `plataforma_version`. Ninguno prohibido, ninguno sin clasificar → **pasa**.
- **1b (medida: invarianza).** Se permutaron los campos de resultado 200 veces; la selección cambió en **0** (IC95 Wilson de la fracción [0.000, 0.019]) → **pasa**: la cláusula no lee el desenlace.

- **1c (medida: asociación criterio↔acierto).** Filas con criterio: 240, acierto 65.0% (Wilson [58.8, 70.8] — **optimista**, supone filas independientes). Sin criterio: 16, acierto 75.0%.
  **Diferencia -10.0 pp, IC95 de clúster de día [-42.9, +23.5]**; p de permutación de etiqueta de día = **0.8051** (33 días con criterio contra 2 sin).
  ICC del acierto 0.431, efecto de diseño 3.82 → **n efectivo 67** sobre 35 días.
  **el intervalo CONTIENE el cero y la permutación de día no cruza α: con estos datos no se puede distinguir asociación de ausencia de asociación — no es un permiso, es una falta de resolución, y con un punto de -10.0 pp la parte que pesa es que tampoco se puede descartar.**

### PRUEBA 2 — la del b/c

| | n | b | c | ventaja | IC95 clúster | p exacta |
|---|---|---|---|---|---|---|
| antes | 256 | 72 | 56 | +6.2 pp | [-10.2, +23.0] | 0.1847 |
| después | 240 | 72 | 56 | +6.7 pp | [-10.7, +23.9] | 0.1847 |

**Δb = +0 · Δc = +0.** Retiró 16 filas: 0 discordantes a favor del MODELO (`b`), 0 a favor de la BASELINE (`c`), 16 concordantes.

> No dispara la alarma del b/c.

### PRUEBA 3 — anclas

Sobre `cargar(hasta_sello=2026-08-24, dedup=False)` (228 filas), la cláusula retira **0**.

- **3a — costo retroactivo.** §2 (`estricta`): **21/21** · línea base §2.8 (`excluir_cero`): **7/7**. Los dos pre-registros siguen reproduciendo con la cláusula aplicada también al pasado.
- **3b — ruta del ancla preservada (FATAL si falla).** Recargando el ancla desde cero después de correr la cláusula: §2 **21/21**, línea base **7/7**; base sin mutar: **sí**. **PASA.**

**Veredicto del banco: PASA LAS TRES.**

---

## C2 — considerar las de cuando cerraban ambas máquinas

> «considerar las de cuando cerraban ambas máquinas»

**Operacionalización.** conserva las filas cuya `fecha` está en la ventana de solapamiento EVIDENCIADA, leída de `data/sombra/veredictos.jsonl` (veredicto PARIDAD o DIVERGENCIA ⇒ sellaron las dos). No se cablea ninguna fecha.

**Procedencia.** propuesta de Nicolás, sexta corrida: construir la regla desde el historial de máquinas

- LIMITACIÓN DECLARADA: la ventana evidenciada no es necesariamente la ventana real. `comparar_sombra.py` REHÚSA por diseño las fechas <= 2026-08-24 (bases copiadas), así que un solapamiento anterior no dejaría rastro comparable. La cláusula se evalúa sobre lo que hay evidencia de que pasó.

### PRUEBA 1 — metadata

- **1a (declarativa).** Campos declarados: `fecha`, `solapamiento`, `era`. Ninguno prohibido, ninguno sin clasificar → **pasa**.
- **1b (medida: invarianza).** Se permutaron los campos de resultado 200 veces; la selección cambió en **0** (IC95 Wilson de la fracción [0.000, 0.019]) → **pasa**: la cláusula no lee el desenlace.

- **1c (medida: asociación criterio↔acierto).** Filas con criterio: 16, acierto 75.0% (Wilson [50.5, 89.8] — **optimista**, supone filas independientes). Sin criterio: 240, acierto 65.0%.
  **Diferencia +10.0 pp, IC95 de clúster de día [-23.5, +42.9]**; p de permutación de etiqueta de día = **0.8049** (2 días con criterio contra 33 sin).
  ICC del acierto 0.431, efecto de diseño 3.82 → **n efectivo 67** sobre 35 días.
  **el intervalo CONTIENE el cero y la permutación de día no cruza α: con estos datos no se puede distinguir asociación de ausencia de asociación — no es un permiso, es una falta de resolución, y con un punto de +10.0 pp la parte que pesa es que tampoco se puede descartar.**

### PRUEBA 2 — la del b/c

| | n | b | c | ventaja | IC95 clúster | p exacta |
|---|---|---|---|---|---|---|
| antes | 256 | 72 | 56 | +6.2 pp | [-10.2, +23.0] | 0.1847 |
| después | 16 | 0 | 0 | +0.0 pp | [+0.0, +0.0] | 1.0000 |

**Δb = -72 · Δc = -56.** Retiró 240 filas: 72 discordantes a favor del MODELO (`b`), 56 a favor de la BASELINE (`c`), 112 concordantes.

De las 128 discordantes retiradas, **56 favorecían a la baseline** (44%, IC95 Wilson [35%, 52%], binomial exacta contra una moneda p = 0.1847).

> No dispara la alarma del b/c.

> **SIN PODER RESOLUTIVO.** La población que deja (16 filas, 0 + 0 pares discordantes) no distingue al campeón de la baseline: sin discordancias el duelo no tiene nada que medir, y una ventaja con IC [0, 0] es la ausencia de medición, no una medición de ausencia. El piso declarado del proyecto es 30 filas.

### PRUEBA 3 — anclas

Sobre `cargar(hasta_sello=2026-08-24, dedup=False)` (228 filas), la cláusula retira **228**.

- **3a — costo retroactivo.** §2 (`estricta`): **0/21** · línea base §2.8 (`excluir_cero`): **0/7**. **NO reproducen.** Rotas en §2: ['(la cláusula deja la ventana histórica VACÍA: ninguna afirmación tiene filas sobre las que medirse)']; en la línea base: ['(ídem)']. Si la cláusula se adoptara, la rama histórica `dedup=False` tendría que seguir existiendo y habría que declarar cuál afirmación se reproduce por cuál ruta.
- **3b — ruta del ancla preservada (FATAL si falla).** Recargando el ancla desde cero después de correr la cláusula: §2 **21/21**, línea base **7/7**; base sin mutar: **sí**. **PASA.**

**Veredicto del banco: no reprobada · COSTO RETROACTIVO en 3a · SIN PODER RESOLUTIVO (la población que deja no distingue al campeón de la baseline).**

---

## C3a — preferir la que selló a tiempo (antes de la apertura)

> «preferir la que selló a tiempo»

**Operacionalización.** arbitraje dentro de cada grupo `(ticker, sesion_objetivo)` duplicado: conserva la fila cuyo `timestamp_utc` es anterior a la apertura UTC de la sesión que su propio `available_at` implica. Si ninguna o todas cumplen, el grupo queda intacto. Las filas sin pareja no se tocan.

**Procedencia.** propuesta de Nicolás, sexta corrida; la puntualidad como criterio de arbitraje

- ES LA CLÁUSULA QUE HAY QUE MIRAR DE FRENTE: es metadata en la forma —un timestamp contra un calendario— pero la puntualidad puede correlacionar con el acierto, porque un sello tardío usa datos distintos. La PRUEBA 1c lo MIDE en vez de suponerlo.

### PRUEBA 1 — metadata

- **1a (declarativa).** Campos declarados: `ticker`, `sesion_objetivo`, `timestamp_utc`, `available_at`, `exchange`, `sello_a_tiempo`. Ninguno prohibido, ninguno sin clasificar → **pasa**.
- **1b (medida: invarianza).** Se permutaron los campos de resultado 200 veces; la selección cambió en **0** (IC95 Wilson de la fracción [0.000, 0.019]) → **pasa**: la cláusula no lee el desenlace.

- **1c (medida: asociación criterio↔acierto).** Filas con criterio: 231, acierto 70.1% (Wilson [63.9, 75.7] — **optimista**, supone filas independientes). Sin criterio: 25, acierto 24.0%.
  **Diferencia +46.1 pp, IC95 de clúster de día [-22.8, +70.3]**; sin p de permutación de día (el criterio varía dentro de un mismo día: la permutación de etiqueta de día no es el test correcto y no se reporta un p que no aplica); en su lugar, la fracción de réplicas bootstrap del otro lado del cero es **0.030** — no es un p y no se cita como uno.
  ICC del acierto 0.431, efecto de diseño 3.82 → **n efectivo 67** sobre 35 días.
  **el intervalo CONTIENE el cero y no hay permutación de día válida (el criterio varía dentro del día), así que el intervalo es la única ruta: con estos datos no se puede distinguir asociación de ausencia de asociación — no es un permiso, es una falta de resolución, y con un punto de +46.1 pp la parte que pesa es que tampoco se puede descartar.**

### PRUEBA 2 — la del b/c

| | n | b | c | ventaja | IC95 clúster | p exacta |
|---|---|---|---|---|---|---|
| antes | 256 | 72 | 56 | +6.2 pp | [-10.2, +23.0] | 0.1847 |
| después | 246 | 72 | 49 | +9.3 pp | [-7.2, +26.3] | 0.0451 |

**Δb = +0 · Δc = -7.** Retiró 10 filas: 0 discordantes a favor del MODELO (`b`), 7 a favor de la BASELINE (`c`), 3 concordantes.

De las 7 discordantes retiradas, **7 favorecían a la baseline** (100%, IC95 Wilson [65%, 100%], binomial exacta contra una moneda p = 0.0156).

> **EXIGE MECANISMO** — mueve `c` y NO mueve `b`; todas las discordantes retiradas tienen el mismo signo. Es la firma que destapó `keep="last"`. No queda refutada por esto: queda pendiente de que alguien exhiba por qué el defecto que corrige es asimétrico, ANTES de aceptarla y por impecable que suene el razonamiento.

### PRUEBA 3 — anclas

Sobre `cargar(hasta_sello=2026-08-24, dedup=False)` (228 filas), la cláusula retira **10**.

- **3a — costo retroactivo.** §2 (`estricta`): **5/21** · línea base §2.8 (`excluir_cero`): **1/7**. **NO reproducen.** Rotas en §2: ['n (verificaciones 4.6.0)', 'modelo: aciertos', 'modelo: acierto de gap %', 'baseline: aciertos', 'baseline: acierto de gap %', 'ventaja pp', 'McNemar b10', 'McNemar p', 'MAE modelo', 'MAE predecir 0.0', 'MAE predecir la media', 'cobertura del intervalo 80%', 'ratio ancho/error', 'R² sellado medio', 'zona muerta 0.25: n', 'zona muerta 0.25: ventaja pp']; en la línea base: ['n', 'modelo: acierto %', 'baseline: acierto %', 'ventaja pp', 'McNemar b10', 'McNemar p']. Si la cláusula se adoptara, la rama histórica `dedup=False` tendría que seguir existiendo y habría que declarar cuál afirmación se reproduce por cuál ruta.
- **3b — ruta del ancla preservada (FATAL si falla).** Recargando el ancla desde cero después de correr la cláusula: §2 **21/21**, línea base **7/7**; base sin mutar: **sí**. **PASA.**

**Veredicto del banco: no reprobada · COSTO RETROACTIVO en 3a · EXIGE MECANISMO en la PRUEBA 2.**

---

## C3b — preferir la que selló a tiempo (dentro de la ventana operativa 17:50–20:30)

> «preferir la que selló a tiempo»

**Operacionalización.** idéntica a C3a salvo la definición de «a tiempo»: aquí es que el sello cayó dentro de la ventana operativa declarada del proyecto, 17:50–20:30 hora de Chile.

**Procedencia.** segunda lectura de la misma cláusula 3; se evalúa aparte porque una operacionalización distinta es una cláusula distinta y suma su propio intento

- Las dos lecturas no son equivalentes: un sello a las 21:00 de Chile está fuera de la ventana operativa y sin embargo llega holgado antes de que abra Seúl. Evaluar sólo una de las dos sería elegir la definición sin decirlo.

### PRUEBA 1 — metadata

- **1a (declarativa).** Campos declarados: `ticker`, `sesion_objetivo`, `timestamp_utc`, `sello_en_ventana`. Ninguno prohibido, ninguno sin clasificar → **pasa**.
- **1b (medida: invarianza).** Se permutaron los campos de resultado 200 veces; la selección cambió en **0** (IC95 Wilson de la fracción [0.000, 0.019]) → **pasa**: la cláusula no lee el desenlace.

- **1c (medida: asociación criterio↔acierto).** Filas con criterio: 228, acierto 69.7% (Wilson [63.5, 75.3] — **optimista**, supone filas independientes). Sin criterio: 28, acierto 32.1%.
  **Diferencia +37.6 pp, IC95 de clúster de día [-23.0, +59.3]**; p de permutación de etiqueta de día = **0.0319** (31 días con criterio contra 4 sin).
  ICC del acierto 0.431, efecto de diseño 3.82 → **n efectivo 67** sobre 35 días.
  **DISCREPANCIA ENTRE RUTAS: la permutación de etiqueta de día cruza α (p = 0.0319) pero el IC95 de clúster CONTIENE el cero. Cruzar α no es tener evidencia. Con 4 día(s) del lado minoritario la asociación no se puede establecer NI descartar — y el punto (+37.6 pp) es lo bastante grande como para que 'no se puede descartar' sea la parte que pesa.**

### PRUEBA 2 — la del b/c

| | n | b | c | ventaja | IC95 clúster | p exacta |
|---|---|---|---|---|---|---|
| antes | 256 | 72 | 56 | +6.2 pp | [-10.2, +23.0] | 0.1847 |
| después | 246 | 72 | 49 | +9.3 pp | [-7.2, +26.3] | 0.0451 |

**Δb = +0 · Δc = -7.** Retiró 10 filas: 0 discordantes a favor del MODELO (`b`), 7 a favor de la BASELINE (`c`), 3 concordantes.

De las 7 discordantes retiradas, **7 favorecían a la baseline** (100%, IC95 Wilson [65%, 100%], binomial exacta contra una moneda p = 0.0156).

> **EXIGE MECANISMO** — mueve `c` y NO mueve `b`; todas las discordantes retiradas tienen el mismo signo. Es la firma que destapó `keep="last"`. No queda refutada por esto: queda pendiente de que alguien exhiba por qué el defecto que corrige es asimétrico, ANTES de aceptarla y por impecable que suene el razonamiento.

### PRUEBA 3 — anclas

Sobre `cargar(hasta_sello=2026-08-24, dedup=False)` (228 filas), la cláusula retira **10**.

- **3a — costo retroactivo.** §2 (`estricta`): **5/21** · línea base §2.8 (`excluir_cero`): **1/7**. **NO reproducen.** Rotas en §2: ['n (verificaciones 4.6.0)', 'modelo: aciertos', 'modelo: acierto de gap %', 'baseline: aciertos', 'baseline: acierto de gap %', 'ventaja pp', 'McNemar b10', 'McNemar p', 'MAE modelo', 'MAE predecir 0.0', 'MAE predecir la media', 'cobertura del intervalo 80%', 'ratio ancho/error', 'R² sellado medio', 'zona muerta 0.25: n', 'zona muerta 0.25: ventaja pp']; en la línea base: ['n', 'modelo: acierto %', 'baseline: acierto %', 'ventaja pp', 'McNemar b10', 'McNemar p']. Si la cláusula se adoptara, la rama histórica `dedup=False` tendría que seguir existiendo y habría que declarar cuál afirmación se reproduce por cuál ruta.
- **3b — ruta del ancla preservada (FATAL si falla).** Recargando el ancla desde cero después de correr la cláusula: §2 **21/21**, línea base **7/7**; base sin mutar: **sí**. **PASA.**

**Veredicto del banco: no reprobada · COSTO RETROACTIVO en 3a · EXIGE MECANISMO en la PRUEBA 2.**

---

## C4 — si son iguales, contar una vez

> «si son iguales, contar una vez»

**Operacionalización.** dentro de cada grupo `(ticker, sesion_objetivo)` duplicado, si las filas coinciden en `acierto_gap` y en `gap_pct` —lo que el duelo puntúa— se conserva una sola, la de emisión MÁS ANTIGUA. Si no coinciden, el grupo queda intacto.

**Procedencia.** propuesta de Nicolás, sexta corrida

- El desempate declarado (la más antigua) es inmaterial para b/c por construcción —las dos filas puntúan idéntico— pero NO para el MAE, porque `error_gap_pp` sí difiere entre ellas. Quedarse con la fresca sería `keep="last"` entrando por la ventana.

- Esta cláusula LEE `acierto_gap` para decidir. La PRUEBA 1 lo va a marcar, y ése es exactamente el punto del banco.

### PRUEBA 1 — metadata

- **1a (declarativa).** Campos declarados: `ticker`, `sesion_objetivo`, `fecha`, `acierto_gap`, `gap_pct`. **REPRUEBA** — prohibidos: `acierto_gap`, `gap_pct`; sin clasificar: `(ninguno)`.
- **1b (medida: invarianza).** Se permutaron los campos de resultado 200 veces; la selección cambió en **200** (IC95 Wilson de la fracción [0.981, 1.000]) → **REPRUEBA**: la selección depende del desenlace, diga lo que diga su declaración.

- **1c (asociación criterio↔acierto).** No aplicable: la cláusula no define un criterio por fila.

### PRUEBA 2 — la del b/c

| | n | b | c | ventaja | IC95 clúster | p exacta |
|---|---|---|---|---|---|---|
| antes | 256 | 72 | 56 | +6.2 pp | [-10.2, +23.0] | 0.1847 |
| después | 253 | 72 | 56 | +6.3 pp | [-10.4, +23.2] | 0.1847 |

**Δb = +0 · Δc = +0.** Retiró 3 filas: 0 discordantes a favor del MODELO (`b`), 0 a favor de la BASELINE (`c`), 3 concordantes.

> No dispara la alarma del b/c.

### PRUEBA 3 — anclas

Sobre `cargar(hasta_sello=2026-08-24, dedup=False)` (228 filas), la cláusula retira **3**.

- **3a — costo retroactivo.** §2 (`estricta`): **8/21** · línea base §2.8 (`excluir_cero`): **3/7**. **NO reproducen.** Rotas en §2: ['n (verificaciones 4.6.0)', 'modelo: aciertos', 'modelo: acierto de gap %', 'baseline: aciertos', 'baseline: acierto de gap %', 'MAE modelo', 'MAE predecir 0.0', 'MAE predecir la media', 'cobertura del intervalo 80%', 'ratio ancho/error', 'R² sellado medio', 'zona muerta 0.25: n', 'zona muerta 0.25: ventaja pp']; en la línea base: ['n', 'modelo: acierto %', 'baseline: acierto %', 'ventaja pp']. Si la cláusula se adoptara, la rama histórica `dedup=False` tendría que seguir existiendo y habría que declarar cuál afirmación se reproduce por cuál ruta.
- **3b — ruta del ancla preservada (FATAL si falla).** Recargando el ancla desde cero después de correr la cláusula: §2 **21/21**, línea base **7/7**; base sin mutar: **sí**. **PASA.**

**Veredicto del banco: REPROBADA en la PRUEBA 1 (lee el resultado).**

---

## C4b — si son iguales, contar una vez (lectura de metadata: «iguales» = el mismo evento)

> «si son iguales, contar una vez»

**Operacionalización.** «iguales» NO se lee sobre el desenlace sino sobre la identidad del evento: dos filas del mismo `(ticker, sesion_objetivo)` son dos pronósticos del MISMO evento y se cuenta uno. Desempate declarado y NO por frescura: la emisión más antigua.

**Procedencia.** segunda lectura de la cláusula 4, evaluada para no reportar sólo la lectura menos favorable. Resulta ser EXACTAMENTE la regla `keep="first"` que la cola de decisiones ya midió (n=241, +6,64 pp, p=0,1847), así que **NO suma un intento nuevo**: es un intento ya contado, y reproducirlo sirve de validación externa del banco

- Es la lectura que NO lee el resultado, y por eso pasa la PRUEBA 1 donde C4 la reprueba. La diferencia entre C4 y C4b no es de grado: es qué significa «iguales», y esa palabra es toda la cláusula.

- El desempate por la más antigua está declarado. Su espejo por frescura está PROHIBIDO por la firma del 1-sep y este módulo no lo ofrece en ninguna forma — un número retirado que sigue ofrecido en el código vuelve a circular.

- Sus cifras son la VALIDACIÓN EXTERNA del banco: si no reprodujeran n=241 y b/c 72/56, el instrumento estaría mal y nada de lo demás valdría.

### PRUEBA 1 — metadata

- **1a (declarativa).** Campos declarados: `ticker`, `sesion_objetivo`, `fecha`. Ninguno prohibido, ninguno sin clasificar → **pasa**.
- **1b (medida: invarianza).** Se permutaron los campos de resultado 200 veces; la selección cambió en **0** (IC95 Wilson de la fracción [0.000, 0.019]) → **pasa**: la cláusula no lee el desenlace.

- **1c (asociación criterio↔acierto).** No aplicable: la cláusula no define un criterio por fila.

### PRUEBA 2 — la del b/c

| | n | b | c | ventaja | IC95 clúster | p exacta |
|---|---|---|---|---|---|---|
| antes | 256 | 72 | 56 | +6.2 pp | [-10.2, +23.0] | 0.1847 |
| después | 241 | 72 | 56 | +6.6 pp | [-11.0, +24.4] | 0.1847 |

**Δb = +0 · Δc = +0.** Retiró 15 filas: 0 discordantes a favor del MODELO (`b`), 0 a favor de la BASELINE (`c`), 15 concordantes.

> No dispara la alarma del b/c.

### PRUEBA 3 — anclas

Sobre `cargar(hasta_sello=2026-08-24, dedup=False)` (228 filas), la cláusula retira **15**.

- **3a — costo retroactivo.** §2 (`estricta`): **7/21** · línea base §2.8 (`excluir_cero`): **3/7**. **NO reproducen.** Rotas en §2: ['n (verificaciones 4.6.0)', 'modelo: aciertos', 'modelo: acierto de gap %', 'baseline: aciertos', 'baseline: acierto de gap %', 'ventaja pp', 'MAE modelo', 'MAE predecir 0.0', 'MAE predecir la media', 'cobertura del intervalo 80%', 'ratio ancho/error', 'R² sellado medio', 'zona muerta 0.25: n', 'zona muerta 0.25: ventaja pp']; en la línea base: ['n', 'modelo: acierto %', 'baseline: acierto %', 'ventaja pp']. Si la cláusula se adoptara, la rama histórica `dedup=False` tendría que seguir existiendo y habría que declarar cuál afirmación se reproduce por cuál ruta.
- **3b — ruta del ancla preservada (FATAL si falla).** Recargando el ancla desde cero después de correr la cláusula: §2 **21/21**, línea base **7/7**; base sin mutar: **sí**. **PASA.**

**Veredicto del banco: no reprobada · COSTO RETROACTIVO en 3a.**

---

---

## Cómo se evalúa la QUINTA cláusula

Sin tocar una línea de `GEMELO/banco_clausulas.py`. Se construye un `Clausula` y se lo pasa a `evaluar`:

```python
from GEMELO.banco_clausulas import Clausula, cargar_base, evaluar

C5 = Clausula(
    nombre="C5 — <la cláusula, en una línea>",
    texto="<como la escribió quien la propuso>",
    operacionalizacion="<cómo se traduce a código, explícito: una "
                       "traducción distinta es OTRA cláusula>",
    procedencia="<quién la propuso y dónde consta>",
    campos=("fecha", "exchange", ...),   # los que LEE, declarados
    seleccionar=lambda df: df.index[...],  # devuelve el índice que sobrevive
    criterio=lambda df: df["<indicador binario por fila>"],  # o None
)

df = cargar_base(hasta_sello=CORTE_BANCO)
r = evaluar(C5, df)          # las tres pruebas, con sus intervalos
print(r["veredicto"])
```

**Tres obligaciones que el banco impone y no se pueden esquivar:**

1. `campos` hay que declararlo, y un campo que no esté clasificado como seguro o prohibido **reprueba 1a**: el silencio no es una clasificación. Pero declarar bien tampoco alcanza — **1b permuta el desenlace y mide**, así que una declaración mentirosa se cae igual (hay un test que lo fija con una cláusula que declara metadata y lee el gap).
2. `seleccionar` devuelve un ÍNDICE, no un DataFrame. Eso obliga a que la cláusula sea una selección de filas y no una transformación, y es lo que hace que las filas retiradas se puedan mirar de a una en la PRUEBA 2.
3. La corrida **suma un intento** y hay que agregarlo a `REGISTRO_INTENTOS` con su procedencia. Si la quinta se evalúa en dos operacionalizaciones, son dos.

---

## Lo que este banco NO decide

- **Cuál cláusula adoptar.** El banco reporta tres pruebas; el criterio de aceptación es de Nicolás. Una cláusula marcada EXIGE MECANISMO no está refutada: está pendiente de que alguien exhiba por qué el defecto que corrige es asimétrico.
- **Qué pasa con las 15 huérfanas.** Eso es el forense de otro frente (`GEMELO/resultados/huerfanas.md`) y no entra acá: este banco evalúa cláusulas, no decide cuál se aplica a qué población.
- **Si la operacionalización es la correcta.** Una cláusula en castellano no es ejecutable hasta que alguien la traduce, y la traducción es discutible. Cada una lleva la suya escrita; una traducción distinta es una cláusula distinta y suma su propio intento.

## Los intentos que suma esta corrida

**Cinco**: C1, C2, C3a, C3b y C4. Van como una fila del registro estructurado de `GEMELO/relevo_asiatico.py` (`REGISTRO_INTENTOS`, ahora 21 tramos), con su procedencia. **No se escribió ningún entero nuevo**: `N_INTENTOS_ACUMULADO` se calcula como la suma del registro, y esa suma pasó de **86 a 91**.

**Lo que eso arrastra, declarado acá porque un número que sigue ofrecido vuelve a circular:**

- `backtest/veredicto_51.py:N_INTENTOS_PREVIO` estaba en 86 y un test lo ata al registro precisamente para que no se separe en silencio. Se actualizó a **91** (y `N_INTENTOS_51` a 97). Subir N sólo hace el DSR **más** exigente, nunca más favorable: el NO-CONCLUYENTE de la corrida ya sellada no puede darse vuelta por esto.
- El resumen ya sellado de la corrida `20260901-133154-5.1-arnes-corregido-gatillo-incumplido` declaró **N = 92 antes de correr** y **no se reescribe**: era el registro en SU instante. Por eso 92 quedó explícitamente conservado en `BANDA_N`, para que ese resumen siga siendo reproducible columna a columna.
- **Queda una decisión abierta que no es de este frente:** el arreglo elegido fue subir la constante. La alternativa —y es la que el proyecto ya usa en `CORTE_SECCION_2`— es **pinchar el instante en vez de mover el número**: que `N_INTENTOS_PREVIO` quede declarado como «el registro al 2026-09-01 13:31» y que el test compare contra esa foto, no contra la suma viva. Eso saca a los dos números del choque de una vez y para siempre, en lugar de obligar a una edición cada vez que el registro crece. No se hizo acá porque es un rediseño del módulo del veredicto 5.1, que es otro frente.
- Siguen diciendo **86** como cifra vigente `GEMELO/resultados/espera_firma.md` (§«Antes de citar cualquier cifra de acá») y `GEMELO/resultados/cola_decisiones.md` (tabla de apertura). Son documentos ya commiteados de otros frentes y este informe **no los edita** — la frontera de la errata es el commit. Quien los cite hoy tiene que citar 91. (Se citan por sección y no por línea a propósito: un número de línea lo desplaza la próxima edición del documento citado, que es un error crónico ya fijado por un test del proyecto.)

C3a y C3b cuentan **por separado** aunque sean la misma cláusula en castellano: una operacionalización distinta es una configuración distinta, y evaluar dos y reportar una sería elegir la definición sin decirlo.

NO suman, y se declara para que la exclusión sea auditable:

- **C0**, la regla firmada: ya está evaluada, publicada y aplicada. Entra como referencia.
- **C4b**: resulta ser exactamente `keep="first"`, ya contado en el registro (fila `COLA`, 2 intentos). Contarlo otra vez sería inflar el N por haberlo mirado desde otro nombre.
- **`CLAUSULA_TRAMPA`**: es la contraprueba del instrumento. De ella no se lee ningún resultado sobre el modelo.
- **Las mediciones de la PRUEBA 1c** (asociación criterio↔acierto), la validación externa y los chequeos estructurales: son diagnóstico del método, no configuraciones predictivas — la misma clase de exclusión que el registro ya declara para el MDE y las fronteras de gasto de alpha.

