# La regla de deduplicación — forense del origen y las tres ramas completas

**Fecha:** 2026-09-01 · **Autor:** agente de solo lectura, Frente A de la
quinta corrida · **Alcance:** `GEMELO/SECUENCIAL/DISEÑO.md` §A3.1.a,
`GEMELO/resultados/cola_decisiones.md` §2a, `DECISIONES.md` §33.8.

**Este documento no aplica ninguna regla, no toca ninguna base y no
commitea nada.** `senales.db` y `noticias.db` se leyeron en `mode=ro`.
Ningún archivo salvo este fue escrito. Es forense y consecuencias; la
elección sigue siendo de Nicolás.

**Fuente de todas las cifras:** `backtest.linea_base.cargar()` (autoridad,
`senales.db` en `mode=ro`) más una columna extra (`sesion_objetivo`) leída
con la misma conexión de solo lectura, más
`.claude/skills/estadistica-evaluacion/scripts/evaluacion.py` para Wilson
y McNemar exacto — no se reimplementó ninguno de los dos. Ventana viva al
2026-09-01: **n = 256** filas selladas bajo la convención congelada
`excluir_cero` (§2.8), 2026-07-05 → 2026-08-27. Es más reciente que la
corrida anterior (256 también, pero el N pudo moverse un par de filas por
verificaciones nuevas); donde una cifra no calce exactamente con
`cola_decisiones.md` §2a, es por esa razón y no por un error de método —
ambos $b/c$ coinciden exactamente (72/56 y 70/46), que es lo que importa.

---

## A1. Forense del origen

### A1.0 — Primera corrección al informe anterior: son CUATRO sesiones, no cinco

`GEMELO/SECUENCIAL/DISEÑO.md` §A3.1.a dice "quince pares, sobre cinco
sesiones (31-jul, 5-ago, 12-ago, 18-ago)" — y esa lista tiene **cuatro**
fechas, no cinco. Verificado directamente contra `senales_ticker` (todos
los estados, no solo `verificada`, para no dejar pasar un descarte
silencioso):

```sql
SELECT ticker, sesion_objetivo, COUNT(*) FROM senales_ticker
GROUP BY ticker, sesion_objetivo HAVING COUNT(*) > 1
```

Resultado: **30 filas, 15 pares, exactamente 4 sesiones objetivo**:
`2026-07-31` (7 pares), `2026-08-05` (3 pares), `2026-08-12` (4 pares),
`2026-08-18` (1 par). No hay una quinta. Es una errata de conteo del
documento anterior — no de este informe, que la corrige aquí sin editar
aquel (la frontera de la errata es su propio commit, no el mío).

### A1.1 — El chequeo estructural del microsegundo: NO hay colisión

`comparar_sombra.py` usa como chequeo estructural que dos filas selladas
de forma independiente nunca comparten `creado_en`/`timestamp_utc`. Sobre
las 40 filas de `snapshots`:

```python
snaps['timestamp_utc'].nunique()  # 39 de 40 no nulos
```

El "39 de 40" no es una colisión: es el snapshot pre-versionado del
2026-07-04, con `timestamp_utc IS NULL` (documentado en otras partes del
repo como fila pre-`MODELO_VERSION`). Excluyendo el nulo, **cero
colisiones** entre snapshots distintos. Los 30 duplicados de este informe
**no son la misma fila sellada dos veces**: son **8 snapshots distintos,
cada uno con su propio `timestamp_utc` único** (29-jul, 30-jul, 3-ago,
4-ago, 10-ago, 11-ago, 14-ago, 17-ago), cuyo `sesion_objetivo` calculado
coincide de a pares. Es un fenómeno de **destino**, no de **origen**: cada
fila es una predicción real, emitida una sola vez, con su propio sello.

### A1.2 — Caracterización fila por fila: mismo `(ticker, sesión objetivo)`, fechas de emisión consecutivas, NUNCA la misma fecha de emisión

Los 15 pares son siempre `(fecha_senal, ticker)` **distintos** —dos
emisiones en fechas de calendario consecutivas (o casi: 14/17-ago, porque
15–16 son fin de semana)— que aterrizan en la misma `sesion_objetivo`.
Ningún par comparte `fecha_senal`. Campo por campo, sobre las 30 filas:

| Campo | ¿Igual entre las dos filas del par? |
|---|---|
| `fecha_senal` (emisión) | **Nunca** — siempre distinta, un día hábil de diferencia |
| `timestamp_utc`, `available_at`, `verificado_en` | **Nunca** — cada fila con su propio sello |
| `apertura_estimada_pct`, `beta`, `confianza_r2` | **Siempre distintos** — el modelo corrió con datos de otro día |
| `estado` | **Siempre `verificada`** en las 30 — ninguna quedó pendiente ni `sin_datos_mercado` |
| `modelo_version` | **Siempre `4.6.0`**, sin excepción, en las dos filas de cada par |
| `gap_pct`, `retorno_real_pct` | **Siempre idénticos** dentro del par — comparten el mismo desenlace de mercado, es la definición del fenómeno |
| `acierto_gap` | **Distinto en 13 de 15 pares** (la fila vieja y la nueva no siempre coinciden en dirección); igual en 2 (`2330.TW` y `4063.T`, ambas del 5-ago, y `3436.T` del 5-ago — las 3 filas del grupo 08-05 aciertan las dos veces) |

No hay una sola fila con campos idénticos entre las dos del par salvo el
desenlace de mercado (`gap_pct`/`retorno_real_pct`, que es un dato del
mundo, no del modelo) y el propio `(ticker, sesión objetivo)`. Esto
descarta por sí solo la hipótesis "fila copiada" o "reintento que
reescribió la misma fila": son dos predicciones genuinamente distintas.

### A1.3 — El mecanismo, encontrado en el código, no supuesto

`snapshot.py:140` calcula la sesión objetivo así:

```python
ahora_utc = datetime.now(timezone.utc)      # línea 111, ANTES de descargar/computar
...
sesion_obj, _, _ = calendarios.proxima_sesion_despues_de(exchange, ahora_utc)
```

`proxima_sesion_despues_de(exchange, instante)` devuelve la primera sesión
de esa bolsa cuya apertura es **posterior a `instante`** (`calendarios.py:42`).
El comentario del propio `snapshot.py` (línea 87-89) dice que la sesión
objetivo es "la próxima sesión de esa bolsa cuya apertura es posterior a
**la emisión**" — pero "la emisión" ahí se implementa como el instante de
**reloj de pared en que el proceso llegó a esa línea**, no como
`available_at` (el cierre del SOX que alimenta la predicción, que es el
ancla conceptual correcta según la regla maestra de `CLAUDE.md`). En
operación normal ambos instantes caen del mismo lado de la medianoche UTC
y el resultado es indistinguible. **Cuando el snapshot se sella tarde —
cruzando la apertura de una bolsa asiática— dejan de serlo**, y
`proxima_sesion_despues_de` salta honestamente a la sesión siguiente,
porque la que tenía que ser la sesión objetivo ya abrió antes de que el
código preguntara.

Esto reproduce exactamente, con el código delante, el mecanismo que
`DECISIONES.md` (Etapa 5.0.1, "Auditoría de sellos tardíos 29–31 jul") ya
había diagnosticado por otra vía (lectura de logs, hoy rotados y ya no
disponibles) para el caso del 29-jul. **No cito esa auditoría a ciegas:
verifiqué hoy, de forma independiente, la parte que sigue siendo
verificable** — el código y los timestamps sellados — y coincide.

### A1.4 — Dos orígenes distintos, no uno: el hallazgo central de este forense

Cruzando los 15 pares con (a) el reloj del sello (`timestamp_utc` del
snapshot) y (b) si la bolsa intermedia estaba realmente cerrada, según
`exchange_calendars` (la misma librería de la que depende `calendarios.py`
— ver limitación en §A1.6), aparecen **dos mecanismos que la lectura
anterior trató como uno solo**:

| Sesión objetivo | Pares | Emisión vieja | Emisión fresca | ¿Bolsa intermedia realmente cerrada? | Mecanismo |
|---|---|---|---|---|---|
| **2026-07-31** | 7 (KRX×2, TWSE×1, TSE×4) | 2026-07-29 → sellada **2026-07-30T01:23:34 UTC** | 2026-07-30 → sellada 2026-07-30T22:15:10 UTC (normal) | **NO** — XKRX, XTAI y XTKS operaron el 07-30 | **Sello tardío cruza la medianoche/las 01h UTC**: `ahora_utc` (01:23) ya es posterior a la apertura de KRX (00:00 UTC) y XTKS (00:00 UTC) y XTAI (~01:00 UTC) del 07-30, así que `proxima_sesion_despues_de` salta honestamente al 07-31. IFX.DE (XETR abre 07:00 UTC) NO saltó — es la prueba de que el mecanismo es el reloj, no el calendario |
| **2026-08-05** | 3 (TWSE×1, TSE×2) | 2026-08-03 → sellada **2026-08-04T02:57:44 UTC** | 2026-08-04 → sellada 2026-08-04T22:19:47 UTC (normal) | **NO** — XTAI y XTKS operaron el 08-04 | **Mismo mecanismo**, más severo (sello 2h57m tras medianoche). Nota aparte: 000660.KS, 005930.KS, 6857.T y 8035.T no tienen NINGUNA fila el 08-03 (`sesion_objetivo` NULL) — cayeron por completo ese día (fallo de descarga por ticker), así que no pueden duplicarse: menos filas afectadas de las que el mecanismo por sí solo habría producido |
| **2026-08-12** | 4 (TSE×4) | 2026-08-10 → sellada 2026-08-10T23:45:34 UTC (normal, no cruza medianoche) | 2026-08-11 → sellada 2026-08-11T22:17:14 UTC (normal) | **SÍ** — XTKS cerrado el 2026-08-11 (verificado con `exchange_calendars.get_calendar("XTKS").is_session("2026-08-11")` → `False`) | **Feriado real de mercado.** KRX y TWSE, que sí operaron el 08-11, NO duplicaron ese día (000660.KS, 005930.KS, 2330.TW targetearon 08-11 sin problema) — la prueba de que aquí no hay reloj involucrado |
| **2026-08-18** | 1 (KRX×1) | 2026-08-14 → sellada 2026-08-14T22:15:06 UTC (normal) | 2026-08-17 → sellada 2026-08-17T22:27:13 UTC (normal) | **SÍ** — XKRX cerrado el 2026-08-17 | **Feriado real de mercado**, igual que el anterior. `000660.KS` no aparece como par porque falta por completo del sello del 08-17 (dropout parcial de tickers ese día — 4 de 7 asiáticos ausentes; asunto aparte, no forma parte del fenómeno de duplicación) |

**Conclusión de origen: 10 de los 15 pares (20 de las 30 filas) son un
efecto del reloj de un sello tardío** — el mismo fenómeno, con evidencia
de código, que `DECISIONES.md` ya asoció al DarkWake del Mac en 29-jul y
03-ago (descargas parciales de Yahoo con reintentos que se congelaron
horas). **Los otros 5 pares (10 filas) son feriados de mercado reales**,
sin ninguna anomalía de reloj — la sesión intermedia no existió porque el
mercado local estaba genuinamente cerrado, y ambas emisiones son igual de
"a tiempo" respecto de su propio `available_at`.

Esta distinción **no estaba en el forense anterior**, que trató las 30
filas como una sola familia ("la sesión intermedia no existió", sin decir
por qué). Importa porque cambia el argumento de diseño en §A3 más abajo:
no hay una sola pregunta ("first, last o both"), hay dos poblaciones con
argumentos de origen distintos.

### A1.5 — Chequeo pedido: ¿se concentran en el bloque 15–23-jul (+40,9 pp)?

**No.** Las cuatro sesiones objetivo (31-jul, 5-ago, 12-ago, 18-ago) caen
todas **después** del bloque 15–23-jul. Verificado también numéricamente
en §A2: la ventaja **dentro** de la ventana R2 (44 filas, +40,9 pp) es
**idéntica en las tres ramas** — dedup no le quita ni le pone una sola
fila a ese bloque, porque ninguno de los 15 pares tiene su
`sesion_objetivo` ahí. El hallazgo de este informe es independiente del
hallazgo de la ventaja concentrada.

### A1.6 — Qué se verificó hoy de forma independiente y qué se sigue citando

Para cumplir la regla de la casa ("si no hay vara independiente, decilo"):

- **Verificado hoy, de forma independiente, con evidencia propia**: los 30
  registros y sus 15 pares (SQL directo sobre `senales.db` en `mode=ro`);
  la unicidad estructural de `timestamp_utc` en `snapshots`; el código de
  `snapshot.py`/`calendarios.py` que produce el salto de sesión; los
  metadatos de sello (`origen=programado`, `descarga_ok/total=28/28`,
  `sox_fecha`, `plataforma_version`) de los 8 snapshots involucrados; el
  hueco del commit "Backup diario 2026-07-29" en `git log` (no existe —
  salta de 28-jul a 30-jul), consistente con un sello que llegó después de
  la ventana del job de backup (18:40 Chile) esa noche; y el estado real
  de apertura de XKRX/XTAI/XTKS en las 12 fechas relevantes vía
  `exchange_calendars`.
- **NO verificado de forma independiente hoy — se cita `DECISIONES.md`**:
  la causa raíz última del sello tardío (DarkWake del Mac, fallos
  puntuales de Yahoo con red sana, los tiempos exactos de despertar) sale
  de logs de los jobs (`data/*.log`) que **ya rotaron** (2 MB × 2 copias)
  y no cubren julio/agosto — hoy solo contienen desde el 26-ago. La
  reconstrucción de ESE detalle se apoya en el trabajo ya escrito en
  `DECISIONES.md` (Etapa 5.0.1, 03-ago-2026), que sí tuvo esos logs
  delante en su momento. Lo que yo aporto de nuevo es el mecanismo de
  CÓDIGO que explica por qué un sello tardío produce específicamente este
  síntoma (duplicado de sesión), y la confirmación de que 10 de los 15
  pares encajan en ese mecanismo mientras 5 no.
- **Vara parcialmente compartida, declarada como tal**: el chequeo de
  feriados usa `exchange_calendars`, la MISMA librería de la que depende
  `calendarios.py` en producción. Confirma que el calendario que la
  plataforma usa internamente es autoconsistente (KRX/XTKS cerrados esos
  días según su propia fuente), pero **no** es una fuente externa
  independiente (un almanaque de feriados de otro proveedor). Si esa
  librería tuviera un error de calendario para Japón/Corea en 2026, este
  chequeo no lo detectaría — se declara la limitación en vez de
  presentarlo como una confirmación externa.

---

## A2. Las tres ramas, completas

Ventana: `senales.db` en `mode=ro`, convención `excluir_cero` (§2.8),
n base = 256. Dedup por `(ticker, sesión objetivo)`, ordenado por fecha de
emisión ascendente: `keep="first"` conserva la emisión vieja,
`keep="last"` la fresca. "Sin deduplicar" es el estado de hecho hoy — las
30 filas cuentan las dos, como cualquier otra predicción.

| | **`keep="first"`** (emisión temprana) | **`keep="last"`** (emisión tardía) | **Sin deduplicar** (lo que hay hoy) |
|---|---|---|---|
| n | **241** | **241** | **256** |
| Modelo: aciertos de gap | 155/241 = **64,3%** | 163/241 = **67,6%** | 168/256 = **65,6%** |
| Modelo: IC95 Wilson | [58,1%, 70,1%] | [61,5%, 73,2%] | [59,6%, 71,2%] |
| Baseline "siempre al alza": aciertos | 139/241 = **57,7%** | 139/241 = **57,7%** | 152/256 = **59,4%** |
| Baseline: IC95 Wilson | [51,4%, 63,7%] | [51,4%, 63,7%] | [53,3%, 65,2%] |
| **Ventaja** | **+6,64 pp** | **+9,96 pp** | **+6,25 pp** |
| McNemar b (modelo acierta, baseline falla) | 72 | 70 | 72 |
| McNemar c (baseline acierta, modelo falla) | 56 | 46 | 56 |
| McNemar p — χ² con corrección de continuidad (`backtest/linea_base.mcnemar`) | 0,1849 | 0,0327 | 0,1849 |
| McNemar p — binomial exacta (`evaluacion.mcnemar_exact`) | 0,1847 | 0,0323 | 0,1847 |
| MAE del gap (modelo) | 2,7662 pp | 2,4983 pp | 2,9383 pp |
| MAE de predecir cero | 2,9650 pp | 2,9650 pp | 3,2756 pp |
| Cobertura empírica del intervalo 80% | 92,5% | 92,9% | 90,6% |
| Ratio ancho/error del intervalo | 1,99× | 2,21× | 1,87× |
| n dentro de la ventana R2 (15–23 jul) | 44 | 44 | 44 |
| Ventaja dentro de R2 | **+40,9 pp** (las tres ramas, idéntico) | +40,9 pp | +40,9 pp |
| n fuera de R2 | 197 | 197 | 212 |
| Ventaja fuera de R2 | **−1,0 pp** | **+3,0 pp** | **−0,9 pp** |
| McNemar p fuera de R2 (χ² cc) | 0,9195 | 0,5898 | 0,9195 |

**Nota técnica, no una elección**: `keep="first"` y "sin deduplicar" dan
exactamente el mismo par McNemar (72/56) porque, fila a fila, en los 15
pares la fila **fresca** (`keep="last"`) *nunca* discrepa de la baseline
dentro de este conjunto de duplicados: en 10 pares la fresca acierta
donde la baseline también acierta, en 2 pares ambas fallan igual, y en 3
pares (el grupo 5-ago) las dos filas del par aciertan siempre. La fila
**vieja**, en cambio, discrepa de la baseline en 12 de los 15 pares — 10
veces a favor de la baseline (`c`, la vieja falla y la baseline acierta) y
2 a favor del modelo (`b`, la vieja acierta y la baseline falla).
Consecuencia mecánica, no interpretación: **cualquier regla que descarte
la fila vieja retira selectivamente 10 desacuerdos desfavorables al
modelo y solo 2 favorables**, y por eso `keep="last"` no es un cambio
neutro de qué fila usar — cambia la composición de qué errores cuentan.
Esto es aritmética verificable sobre las 15 filas de §A1.2, no un
argumento a favor de ninguna rama.

> **Los p-valores de arriba son CONSECUENCIA de la regla elegida, nunca el
> argumento para elegirla.** Léanse después de leer el forense de A1, no
> antes. `keep="first"` y "sin deduplicar" dejan la ventaja por debajo de
> 0,05 (p ≈ 0,185); `keep="last"` la cruza (p ≈ 0,032). Ningún agente
> eligió mirar el p antes de fijar el método — las tres ramas están acá,
> completas, para que la elección se haga con las consecuencias a la
> vista y no al revés.

---

## Lo que el origen sugiere — separado de las consecuencias, y con su propio límite

**Si el origen sugiere algo, sugiere que la pregunta está mal planteada
como una sola regla para las 15 pares**, porque hay dos orígenes:

- Para los **10 pares del reloj tardío** (31-jul y 5-ago): la fila vieja
  usa un insumo de dos días de antigüedad para una sesión que, cuando se
  emitió, ya se sabía saltada — es exactamente la situación que
  `DECISIONES.md` (Etapa 5.0.2 §4) describe como "estructuralmente fuera
  de especificación" en su propuesta —**NO implementada**— de abstención
  por sello tardío. Ese argumento, ya escrito por el proyecto y no por
  este informe, favorece **`keep="last"`** para estos 10 pares
  específicamente: no por el p que produce, sino porque la fila vieja no
  responde a la pregunta que la regresión de contagio está diseñada para
  responder (próxima sesión tras el cierre del SOX usado).
- Para los **5 pares de feriado real** (12-ago y 18-ago): ninguna de las
  dos filas está "fuera de especificación" — cada una es la respuesta
  correcta a su propio `available_at`, y la coincidencia de destino es
  un accidente de calendario, no un defecto de una de las dos. Ahí el
  origen **no** favorece ni a la vieja ni a la fresca; si acaso, favorece
  tratarlas como "dos pronósticos distintos del mismo evento" (la tercera
  opción, contar las dos), que es simétrica.

Esto es una lectura de un argumento **ya existente y no implementado**
en el repo (la propuesta de abstención de la 5.0.2), aplicada aquí solo
como forense — **no es una recomendación de este informe para 4.6.0 ni
para la capa de medición**, y no toca `motor.py` ni `senales.py`. La
decisión de si el origen pesa más que la simetría del método, y si vale
la pena tratar los 15 pares con dos reglas distintas en vez de una,
sigue siendo de Nicolás.

## Qué no se puede determinar con la evidencia disponible

- **La causa última del sello tardío** (por qué el Mac se durmió esas dos
  noches específicas) no se puede re-verificar hoy: los logs de esos días
  ya rotaron. Se cita `DECISIONES.md`, no se re-deriva.
- **Si `exchange_calendars` tiene el feriado correcto** para XTKS
  (11-ago) y XKRX (17-ago) en 2026 no se puede confirmar contra una
  fuente externa al proyecto: es la misma librería que usa producción.
  Es autoconsistente, no independiente.
- **Por qué faltan por completo 4 de 7 tickers asiáticos en el sello del
  17-ago** (000660.KS, 2330.TW, 4063.T, 6857.T) es una anomalía de datos
  aparte, no investigada en este informe porque no participa en ningún
  par duplicado — se deja anotada para quien mire salud de datos de esa
  fecha.
- **Si existieran más pares fuera de la ventana de 256 filas** (en
  legacy, en pendientes, o en el futuro) no se puede descartar sin
  repetir este mismo chequeo cada vez que la ventana crezca — no es una
  propiedad que, una vez medida, quede fija.
