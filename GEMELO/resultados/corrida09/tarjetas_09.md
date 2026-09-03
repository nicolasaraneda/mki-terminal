# Las cuatro decisiones humanas, como tarjetas para firmar

**Corrida 09, Frente 2d — 3-sep-2026, cálculos iniciados 00:38 y cerrados
~00:45 (`TZ=America/Santiago date`).** Todo lo que sigue es de solo lectura
sobre datos: `senales.db` en `mode=ro`, `data/*.log`, `git log`/`git show`/
`git reflog` (ninguna operación de escritura), `systemd/*.timer`. No se
descargó nada. Cada afirmación lleva su estatus: **MEDIDO** (computado esta
noche sobre datos reales), **CITADO** (leído de un expediente, con su fecha),
**PROPUESTA** (recomendación o umbral candidato), **NO EVALUABLE** (no hay
dato con que medirlo, y se dice por qué).

**Convención de medición común a las cuatro tarjetas (MEDIDO):** track record
VIVO al 3-sep, `backtest.linea_base.cargar(hasta_sello=None, dedup=True)`
(regla de deduplicación firmada, D1) → 274 filas con `gap_pct`; convención
`excluir_cero` → **n = 269 filas, 38 fechas**, modelo 4.6.0, `legacy = 0`.
Ventaja = media de `acierto_gap − base_acierto` («siempre al alza» sobre las
mismas filas). Intervalo de **clúster de día** por
`GEMELO.bifurcaciones._bootstrap_dia` (4.000 réplicas, semilla por defecto),
al lado la t de clúster (`_ic_t_cluster`) y la permutación de signo por día
(`_p_permutacion_dia`). El McNemar de filas se publica al lado porque es el
test del diseño original, no porque decida. Esta cifra viva **no es** la
ventana sellada del README (n = 238, +9,7 pp de día [−7,2, +26,6], corte
28-ago): es la misma regla sin corte, y se publica con esa etiqueta.

**Cifra viva de referencia (MEDIDO, intento DSR nº 1):** 180/269 = 66,9 %
contra base 142/269 = 52,8 %; **ventaja +14,1 pp, IC de día [−2,3, +30,9]**,
t-clúster [−3,1, +31,4], p permutación de día 0,117 (McNemar de filas
b01 = 87, b10 = 49, p = 0,0015). Contiene el cero: sigue sin distinguirse de
cero con la unidad correcta.

---

## Tarjeta 1 — Regla de abstención por sello tardío

### Qué decidir en una frase

Si el proyecto adopta —en el retador, nunca en el 4.6.0 congelado— la regla
propuesta en la Etapa 5.0.2 («un sello tardío se abstiene de emitir
predicciones cuya sesión objetivo saltó una sesión completa»), y con qué
definición operativa de «tardío»: por **salto de sesión** (la del acta) o por
**hora de reloj**.

### Opciones

| | Opción | Definición de «sello tardío» | Dónde se aplica |
|---|---|---|---|
| **A** | Abstención por **salto de sesión** (texto literal de DECISIONES §4 de la 5.0.1/5.0.2) | entre `available_at` (cierre UTC del SOX usado) y la apertura de `sesion_objetivo` media una sesión entera del exchange que ya transó sin predicción; operativamente `sesion_objetivo ≠ proxima_sesion_despues_de(exchange, available_at)` | retador (GEMELO §4.2, Nivel 5); en el campeón sólo como **flag retrospectivo** de presentación (`abstenida_timing`), jamás re-emisión |
| **B** | Abstención por **hora de reloj** (PROPUESTA; el acta no fija umbral horario, así que se computan dos y se declara el que la calendario impone) | `timestamp_utc` ≥ 19:00 Chile (hora del vigía) / ≥ 20:30 Chile (re-chequeo). **Hallazgo MEDIDO:** el umbral que reproduce el salto de sesión es **20:00 Chile** = apertura de Seúl y Tokio (00:00 UTC; `calendarios.apertura_utc`), 21:00 para Taipéi, 03:00 del día siguiente para Fráncfort. Sobre los datos, «≥ 20:30» ≡ «≥ 20:00» (no hay ningún sello entre 20:00 y 20:30) | ídem |
| **C** | No adoptar ninguna regla; dejar el ítem como lo cierra el expediente 6B.2 («sin cambios desde 5.0.1, la vía es GEMELO») | — | — |

### Costo medido de cada opción sobre datos reales

**Qué abstendría cada definición, hasta hoy (MEDIDO, dedup=True, excluir_cero):**

| Definición | Filas abstenidas | Fechas | Aciertos que se van | Errores que se van | Base «al alza» en esas filas |
|---|---|---|---|---|---|
| **A** salto de sesión | **15 / 269** | 2 (05-jul: 8 · 05-ago: 7) | **3** | **12** | 12/15 |
| **B ≥ 19:00** | 32 / 269 | 6 (29-jul: 1 · 31-jul: 8 · 03-ago: 1 · 05-ago: 8 · 10-ago: 8 · 21-ago: 6) | 15 | 17 | 14/32 |
| **B ≥ 20:30 (≡ ≥ 20:00)** | 10 / 269 | 3 (29-jul: 1 · 03-ago: 1 · 05-ago: 8) | 4 | 6 | 7/10 |

Detalle por fecha de la definición A (hora local del sello, `sesion_objetivo`
sellada → sesión que `available_at` permitía):

| Fecha de emisión | Sello (Chile) | n | Objetivo sellada | Sesión correcta | Aciertos |
|---|---|---|---|---|---|
| 2026-07-05 (origen **manual**, domingo) | 06:06 | 8 | 2026-07-06 | 2026-07-03 | 2/8 |
| 2026-08-05 (programado) | 21:38 | 7 | 2026-08-07 | 2026-08-06 | 1/7 |

**Las 17 filas de la tabla del acta (29-jul 7, 03-ago 3, 05-ago 7) se
reproducen exactamente en la rama sin deduplicar** (MEDIDO, dedup=False:
A = 25 filas = esas 17 + las 8 del 05-jul, que el acta no contaba porque
miraba sólo sellos nocturnos). De esas 17, **10 ya las retira la regla de
deduplicación firmada** (el lado viejo de los pares del 29-jul y 03-ago):
lo que la abstención agrega sobre D1 son **las 15 filas sin pareja**, que
son exactamente el conjunto de `filtrar_sesion_coherente` de `linea_base`.

**Cruce con `marcar_sesion` (MEDIDO):** la definición A y `sesion_calza ==
False` coinciden **15/15 por construcción** —son la misma condición escrita
dos veces: «medió una sesión entera que ya transó» ⇔ «la primera sesión
después de `available_at` no es la objetivo» (el caso «objetivo anterior a
la correcta» no existe: sería `no_verificable_timing` y ya está fuera).
Cruce de las definiciones horarias con A: **B ≥ 19:00** captura 7 de las 15
(las del 05-ago) y agrega 25 filas con sesión correcta (31-jul, 10-ago,
21-ago: sellos a las 19:40–19:45, antes de la apertura de Seúl); **B ≥
20:30** captura las mismas 7 y agrega 3 (29-jul y 03-ago, la fila
sobreviviente de cada par). **Ninguna definición horaria captura las 8 del
05-jul** (sello a las 06:06 de un domingo: tardío por el calendario, no por
el reloj).

**Ventaja sobre «siempre al alza» con y sin ellas (MEDIDO; cada fila es un
intento DSR):**

| Conjunto | n | días | modelo | base | ventaja | IC de día (boot 4.000) | t-clúster | p perm. día | McNemar filas |
|---|---|---|---|---|---|---|---|---|---|
| con todas (cifra viva) | 269 | 38 | 66,9 % | 52,8 % | **+14,1 pp** | **[−2,3, +30,9]** | [−3,1, +31,4] | 0,117 | b01 87 / b10 49, p 0,0015 |
| sin A (salto de sesión) | 254 | 37 | 69,7 % | 51,2 % | +18,5 pp | [+1,9, +34,8] | [+1,2, +35,8] | 0,043 | 84 / 37, p < 0,0001 |
| sin B ≥ 19:00 | 237 | 32 | 69,6 % | 54,0 % | +15,6 pp | [−2,5, +33,9] | [−3,5, +34,8] | 0,115 | 75 / 38, p 0,0007 |
| sin B ≥ 20:30 | 259 | 35 | 68,0 % | 52,1 % | +15,8 pp | [−0,8, +32,5] | [−1,7, +33,3] | 0,089 | 84 / 43, p 0,0004 |
| sólo B ≥ 19:00 | 32 | 6 | 46,9 % | 43,8 % | +3,1 pp | [−29,2, +34,6] | [−41,2, +47,5] | 1,000 | 12 / 11, p 1,0 |
| sólo A | 15 | 2 | 20,0 % | 80,0 % | −60,0 pp | **NO EVALUABLE** (k = 2 clústeres: el bootstrap de día sólo puede devolver los dos días) | — | — | 3 / 12, p 0,039 |
| rama histórica dedup=False, sin A | 254 | 37 | 69,7 % | 51,2 % | +18,5 pp | [+1,9, +34,8] | [+1,2, +35,8] | 0,043 | 84 / 37 |

**Lectura honesta, y es la parte que importa:**

1. **El intervalo «sin A» excluye el cero, y eso NO es evidencia a favor de
   la regla.** Las 7 filas del 05-ago son parte de la evidencia con que se
   escribió la regla (tabla del acta, 6-ago): quitarlas y ver que la ventaja
   sube es circular. Lo único fuera de muestra respecto del acta son las 8
   del 05-jul (2/8): un solo día. La ventaja «sin A» es una cifra de
   **selección retrospectiva** y se publica como tal, no como la cifra del
   campeón.
2. **El acta ya dijo lo que estos datos repiten:** las filas con salto
   aciertan poco (3/15) y, en la rama histórica, 6/25 — la magnitud es
   ciega porque el insumo tiene dos sesiones de edad. Pero con **k = 2
   fechas** no hay intervalo de día que publicar, y sin intervalo no hay
   afirmación.
3. **La definición horaria no es la regla.** B ≥ 19:00 abstendría 25 filas
   con sesión correcta (aciertan 12/25 y su ventaja sobre la base es +3,1 pp
   [−29,2, +34,6]: indistinguible de ruido y de la cifra viva). El reloj es
   un proxy malo del calendario; lo que decide es si Seúl/Tokio ya abrieron
   (20:00 Chile).

### Recomendación (PROPUESTA, para que el director de programa la dictamine)

**Opción A, con dos precisiones.** (i) La regla se adopta **sólo como flag
retrospectivo de presentación** en el campeón (`abstenida_timing`, fuera de
métricas, igual que `no_verificable_timing`) y como regla de emisión **sólo
en el retador** (GEMELO §4.2 Nivel 5), que es donde el acta ya la puso:
nada de esto toca el 4.6.0. (ii) Se fija de una vez que «tardío» se mide
por calendario (`proxima_sesion_despues_de(exchange, available_at)`) y no
por reloj, porque la condición ya existe en código como
`linea_base.sesion_correcta` y porque el umbral horario correcto es distinto
por bolsa. **Lo que no se hace:** publicar la ventaja «sin A» como cifra del
proyecto —es +18,5 pp por haber mirado—, ni mover el README.

**Nota sobre el parche `snapshot.py:140` (cola §1-bis):** si Nicolás firma
que `sesion_objetivo` se calcule desde `available_at`, el defecto que
produce las filas con salto **deja de ocurrir hacia adelante** y la regla A
queda como flag para el pasado. Son decisiones distintas: el parche corrige
a qué sesión apunta un sello tardío; la abstención decide si ese sello
emite. Con el parche y sin abstención, un sello a las 22:00 apuntaría a la
sesión de Seúl que ya abrió y caería en `no_verificable_timing` por la
regla maestra (hueco declarado, no fila contaminada).

### Qué se hace el día después de la firma

1. **Nicolás:** dictamen escrito en `DECISIONES.md` (skill `acta-decision`)
   con la definición firmada (A) y el nombre del estado (`abstenida_timing`).
2. **Agente (backtest/GEMELO):** en `backtest/linea_base.py` una función
   `marcar_abstencion(df)` que reutilice `marcar_sesion` (no una segunda
   implementación); test que la 15/15 coincidencia con `sesion_calza` se
   mantenga y que las 17 filas del acta se reproduzcan en `dedup=False`.
3. **Agente:** columna «abstenida (retrospectivo)» en el informe de
   `linea_base` y en `/historial`, con su n y sin ventaja publicada mientras
   k < 3 fechas. Ningún UPDATE en `senales.db`: el flag se computa al leer.
4. **GEMELO:** la regla entra al retador como configuración declarada
   ANTES de correr (cuenta como intento DSR, §4.2 bis).
5. Si además se firma el parche `:140`: va con bump de `PLATAFORMA_VERSION`
   y corte de método fechado (ver `parche_snapshot140_tabla.md`, esta
   corrida).

---

## Tarjeta 2 — Qué significa `ts_emision`

### Qué decidir en una frase

Si se agrega a `snapshots` (y por herencia a `senales_ticker`) un campo
aditivo que registre cuándo la fila se hizo **pública**, dado que hoy
`timestamp_utc` y `creado_en` son el mismo instante por construcción y
ningún campo dice cuándo la predicción salió del disco de esta máquina.

### Opciones

| | Opción | Qué cambia | Regla cero |
|---|---|---|---|
| **1** | No hacer nada | `ts_emision` sigue estampado antes del cómputo; la publicación se reconstruye de `git log` y `reporte.log` como esta noche | intacta |
| **2** | Campo aditivo **`commiteado_en`** (instante del `COMMIT` sqlite) — la opción 2 del expediente 6B.1 | cierra la brecha del 06-ago (44 min entre estampa y commit sqlite); no dice nada de publicación externa | intacta (migración aditiva `_asegurar_columnas`) |
| **2-bis** | Campo aditivo **`publicado_en`** (PROPUESTA de esta tarjeta): el instante en que el Telegram del día se envió con esa fila (`alertas.enviar_mensaje` ok) y/o el hash del commit de `mki_backup.py` que la contiene, escritos por los jobs de reporte y backup, **nunca por `snapshot.py`** | hace visible lo que hoy sólo `git log` cuenta; los dos jobs ya corren después del sello | intacta: `snapshot.py`, `senales.py` no se tocan; el job de backup escribe una columna aditiva por `UPDATE ... WHERE publicado_en IS NULL` (nunca reescribe un valor) |
| **3** | Mover `ts_emision` a justo antes de guardar | cambia qué filas pasan la regla maestra hacia adelante | **la toca**: propuesta formal en DECISIONES, firma de Nicolás |

### Costo medido de cada opción sobre datos reales

**Los campos reales (MEDIDO, `PRAGMA table_info` en `mode=ro`):**

- `snapshots`: `fecha, creado_en, regimen, roca_chip, timestamp_utc, origen,
  modelo_version, feature_version, universo_version, ventana_betas,
  descarga_ok, descarga_total, descarga_caidos, plataforma_version,
  sox_usado_pct, sox_fecha`.
- `senales_ticker`: `id, fecha, ticker, puntaje_v0, sentimiento_ia,
  puntaje_ia, apertura_estimada_pct, confianza_r2, timestamp_utc, exchange,
  sesion_objetivo, available_at, estado, intervalo80_pp, n_muestra,
  modelo_version, beta`. **No tiene `creado_en`.**

**Qué mide cada uno y en qué orden se estampa (leído de `snapshot.py`
:100-160 y `senales.py` :209-240, sin editar):**

| Orden | Instante | Campo | Qué mide |
|---|---|---|---|
| 0 | antes | — | descarga + reintentos parciales 60/120 s (`salud_descarga`, :100-109) |
| 1 | `snapshot.py:111-112` | `ahora_utc` → `ts_emision` | **reloj de pared DESPUÉS de descargar y ANTES de computar** el modelo |
| 2 | :114-121 | — | `puntaje_v0_al`, `regimen_al`, `roca_chip_al`, `divergencias_al`, `prediccion_apertura_al` |
| 3 | :126-134 | `available_at` | `cierre_utc("XNYS", sox_fecha)`: **no es un reloj, es calendario** — cuándo era conocible el insumo |
| 4 | :140 | `sesion_objetivo` | `proxima_sesion_despues_de(exchange, ahora_utc)` con el reloj del paso 1 (el defecto de la cola §1-bis) |
| 5 | `senales.py:229-235` | `snapshots.creado_en` **= `timestamp_utc`** | el mismo string se pasa dos veces al `INSERT`; `senales_ticker.timestamp_utc` = el mismo string |
| 6 | fuera de la base | commit de `mki_backup.py` 18:40 · Telegram 18:25 | la **publicación**, no registrada en ninguna columna |

**Retraso `timestamp_utc → creado_en` (MEDIDO):** 41 snapshots con
`timestamp_utc` (42 en total; 1 legacy sin él). **Mediana 0 s, p90 0 s,
máximo 0 s; ninguna fecha difiere.** `senales_ticker.timestamp_utc` −
`snapshots.timestamp_utc`: 945 filas, 0 distintas. **El campo no mide un
retraso: mide la misma variable con dos nombres.** El episodio del 06-ago
(estampa 18:24:52, commit sqlite ~19:08 según el acta 5.0.2) es invisible
en la base: el sello del 06-ago dice `creado_en = timestamp_utc =
18:24:52`. Esto es lo que la opción 2 arregla y la 1 no.

**Sello → primer commit del CSV que contiene la fila (MEDIDO, `git log`
+ `git show` sobre `data/backups/senales_senales_ticker.csv`, 23 commits;
hora Chile):**

| Fecha sellada | Sello | Primer commit que la contiene | Horas |
|---|---|---|---|
| 05-jul (manual) | dom 06:06 | `2bd3192` dom 05-jul 15:49 | 9,7 |
| 08-jul → 24-jul (12 sellos) | 18:15–18:27 | `230b545` sáb 25-jul 21:16 (commit manual único) | 27 → 411 |
| 27-jul | 18:15 | `ab661e2` mar 28-jul 18:40 | 24,4 |
| 28-jul | 18:30 | `ab661e2` mar 28-jul 18:40 | 0,16 |
| **29-jul** | **21:23** | `b046fd0` jue 30-jul 18:53 | **21,5** |
| 30-jul | 18:15 | `b046fd0` 30-jul 18:53 | 0,63 |
| **31-jul** | **19:40** | `862213b` lun 03-ago 18:48 | **71,1** |
| **03-ago** | **22:57** | `db92d36` mar 04-ago 18:49 | **19,9** (el commit de 18:48 del 03-ago fue **antes** del sello: llevó el CSV sin la fila) |
| 04-ago | 18:19 | `7b36d91` mié 05-ago 18:48 | 24,5 |
| **05-ago** | **21:38** | `39193da` jue 06-ago 18:40 | **21,0** (ídem: el commit de 18:48 del 05-ago no la tenía) |
| 06-ago | 18:24 | `f637532` vie 07-ago 18:56 | 24,5 |
| 07-ago | 18:21 | `f637532` 07-ago 18:56 | 0,58 |
| **10-ago** | **19:45** | `ab52df9` mar 11-ago 18:50 | **23,1** |
| 11-ago · 14-ago · 18-ago · 19-ago · 20-ago · 24-ago · 25-ago | 18:15–18:27 | mismo día 18:40–18:49 | 0,2–0,6 |
| 12-ago · 13-ago · 17-ago | 18:19–18:27 | día siguiente 18:40 | 24,2–24,4 (**sello a tiempo y commit al día siguiente: el backup de esas noches no commiteó**; causa NO EVALUABLE sin los logs del Mac) |
| **21-ago** | **19:41** | `6b886e5` lun 24-ago 18:49 | **71,1** |
| 26-ago (sombra en PC; titular Mac) | 18:15 | `7ad1313` jue 27-ago 18:45 | 24,5 |
| 27-ago | 18:15 | `28710b2` sáb 29-ago 19:15 (manual, Mac) | 49,0 |
| 28-ago | 18:15 | `7d42d9b` lun 31-ago 18:40 (primer backup del PC titular) | 72,4 |
| 31-ago · 01-sep · 02-sep (PC titular) | 18:15:03 | mismo día **18:40:00** | 0,42 |

Resumen: **n = 41, mediana 24,4 h, p90 243 h, máximo 411 h, mínimo 0,16 h.**
La mediana es un día entero porque en julio el backup automático no existía
(un commit manual el 25-jul) y porque un sello tardío o un backup que no
commitea empuja la fila al commit siguiente. Desde que el PC es titular
(31-ago): 24,9 min constantes, tres de tres.

**Commit ≠ público (NO EVALUABLE en general):** el commit es local; lo
público es el push manual de Nicolás y el Telegram. `git reflog show
origin/main` en esta máquina sólo empieza el 30-ago (`fetch`) y desde
entonces muestra pushes a las 21:53 (2-sep, backup de 18:40), 01:30, 09:01,
23:36…: **el push llega entre 3 y 15 horas después del commit**, y del Mac no
hay reflog acá. El Telegram sí queda en `reporte.log`: «Reporte enviado
18:25» las seis noches del PC (26-ago → 2-sep). Para un sello tardío, el
reporte de 18:25 se compone **antes** del sello y declara «sin dato sellado
hoy» —la predicción de esa noche nunca sale por Telegram— (CITADO, diseño
del reporte 2.0; sin log del Mac para el 29-jul, 03-ago, 05-ago: NO
EVALUABLE fila por fila).

**Consecuencia para la regla maestra (MEDIDO sobre las tres fechas
críticas):** las filas del 03-ago (sello 22:57 Chile = 02:57 UTC del 04) y
del 05-ago (21:38 Chile) apuntan a sesiones del 05 y del 07-ago que abrían
a las 20:00 Chile del día siguiente; su primer commit fue a las 18:49/18:40
de ese día siguiente, **71 y 80 minutos antes de la apertura objetivo**. La
regla maestra las aceptó por `timestamp_utc` (correcto: el sello precede al
evento); ningún campo dice que estuvieron 20 horas sin salir del disco.

### Recomendación (PROPUESTA, para que el director de programa la dictamine)

**Opción 2 + 2-bis, en la misma migración aditiva; opción 3 no.**
`commiteado_en` lo estampa `senales.guardar_snapshot` en el `INSERT`
(única línea nueva en la ruta de sellado: `datetime.now()` al lado del
`timestamp_utc` que ya recibe) y cierra la brecha del 06-ago; `publicado_en`
lo escriben `mki_backup.py` (sha del commit que contiene la fecha) y el
reporte (`telegram_enviado_en`), que ya corren después y **fuera** de la ruta
de sellado, con `UPDATE ... WHERE ... IS NULL` para que una fila nunca cambie
de valor. Con eso el sello nombra tres instantes distintos que hoy colapsan
en uno: **decidido** (`timestamp_utc`), **escrito** (`commiteado_en`),
**público** (`publicado_en`). La regla maestra sigue usando el primero.

Alternativa más barata si no se quiere tocar `senales.py` ni siquiera
aditivamente: sólo 2-bis (los dos jobs escriben; `commiteado_en` se aproxima
por el log de `snapshot.py`, que desde la 5.0.3 imprime la hora de arranque
y el resultado en segundos —esta noche: arranque 22:15:00.9 UTC, sello
22:15:03—).

### Qué se hace el día después de la firma

1. **Nicolás:** acta con los nombres de las columnas y su semántica
   (`acta-decision`); decide si `commiteado_en` entra en `senales.py`
   (aditivo) o se aproxima por log.
2. **Agente:** `.diff` NO aplicado para `senales.py` (`_asegurar_columnas` +
   una línea en el `INSERT`) con test sobre copia parcheada en directorio
   temporal, más el test de que `timestamp_utc` de las filas existentes no
   cambia byte a byte (las selladas no se reescriben: las columnas nuevas
   nacen `NULL` = «ausencia declarada»).
3. **Agente (`ingeniero-plataforma`):** `mki_backup.py` escribe
   `publicado_en`/`commit_sha` tras `git commit`; el reporte escribe
   `telegram_enviado_en` tras `ok=True`; el vigía agrega el chequeo «sello de
   hoy sin `publicado_en` a las 19:00».
4. **Agente:** `/historial` y el reporte muestran los tres instantes;
   `comparar_sombra` y `linea_base` los ignoran (no son insumo de ninguna
   métrica).
5. La opción 3 queda donde está: propuesta formal, sin tocar.

---

## Tarjeta 3 — Qué corridas perdidas se descartan en vez de ejecutarse tarde (`Persistent=true`)

### Qué decidir en una frase

Para cada uno de los seis timers systemd (todos con `Persistent=true`,
`systemd/*.timer` línea 12; `OnCalendar` Mon..Fri en hora de Chile), si una
corrida perdida por máquina apagada/suspendida se **ejecuta tarde al
volver** (statu quo) o se **descarta** (`Persistent=false`), sabiendo que un
snapshot tardío produce filas con la sesión objetivo equivocada (Tarjeta 1).

**Límite declarado:** la evidencia es **sólo `data/*.log`** (restricción de
Nicolás: `journalctl` no se leyó; `systemctl` no se ejecutó). Los logs están
en **UTC** (líneas `[2026-…T22:15:00…+00:00]`); Chile está en UTC−4 en toda
la ventana (`date` da `-04`), así que los nominales son: noticias 21:50 ·
snapshot 22:15 · reporte 22:25 · backup 22:40 · vigía 23:00 · re-chequeo
00:30 UTC del día siguiente. Los logs de esta máquina **empiezan el 25/26-ago**
(reactivación en PC; no hay `.log.1` en `data/`); todo lo anterior es del
Mac y no está acá.

### Opciones

| | Opción | Qué pasa con una corrida perdida |
|---|---|---|
| **K** | Mantener `Persistent=true` en los 6 (statu quo) | corre al reactivarse la máquina, a la hora que sea; si se perdieron varias, corren **todas seguidas** (el «efecto estampida» del expediente 6B.3, sin evidencia de haber ocurrido) |
| **D** | `Persistent=false` en los 6 | se pierde; el día queda como hueco declarado |
| **M** | Mixto (PROPUESTA): `Persistent=true` sólo donde correr tarde no cambia el significado de lo producido; `false` (o `true` con guardia horaria dentro del job) donde sí | ver tabla de costo |

### Costo medido de cada opción sobre datos reales

**(1) Corridas fuera de su horario nominal por más de 5 minutos según
`data/*.log` (MEDIDO, 26-ago → 2-sep, 6 jobs × 6 días hábiles):**

| Job | Corridas en el log | Fuera de nominal > 5 min | Detalle |
|---|---|---|---|
| noticias 17:50 | 6 | **0** (arranque 21:50:00–21:50:01 UTC) | pero **2 corridas incompletas**: 01-sep guarda 223 titulares a las 22:17:44 UTC y no vuelve a escribir (sin «analizados», sin «resumen»); 02-sep sólo escribe la cabecera de 21:50 y nada más. El vigía las marcó «FALLA noticias: el job NO corrió hoy» y alertó por Telegram las dos noches. No hay proceso `mki_noticias.py` vivo ahora (`pgrep`). **Esto no es Persistent: es un job que arranca a tiempo y muere o cuelga; causa NO EVALUABLE sin journal.** |
| snapshot 18:15 | 6 | **0** (22:15:00.9–01.2 UTC; sello 3 s después) | 8 predicciones y 28/28 descargas las seis noches |
| reporte 18:25 | 6 | **0** (22:25:00.9–01.3 UTC) | «Reporte enviado 18:25» ×6 |
| backup 18:40 | 6 | **0** (22:40:00.2–00.9 UTC) | 3 en sombra sin commit (correcto), 3 con commit |
| vigía 19:00 | 6 | **0** (23:00:00.2–00.9 UTC) | 4 «todo OK», 2 alertas (noticias) |
| re-chequeo 20:30 | 8 | **0 por más de 5 min**; **1 por 4 min 41 s**: 25-ago 23:34:41 UTC (20:34:41 Chile), «sin alerta pendiente» | `CLAUDE.md` describe ese disparo (GATE A-bis, arranque en frío) como «20:30:00 +157 ms»; el log dice 20:34:41. Discrepancia registrada, no resuelta acá |

**Lista de corridas perdidas y ejecutadas tarde por `Persistent=true` en
esta máquina: vacía.** No hay ni un caso medido. **El costo de la opción
K/D no se puede medir sobre corridas de systemd: se estima por analogía con
los sellos tardíos del Mac (launchd), cuya consecuencia sobre las filas es
la misma sea cual sea la causa del atraso.**

**(2) El análogo: hora de emisión de los 41 sellos según `senales.db`
(MEDIDO; `timestamp_utc` en Chile, desvío respecto de 18:15). Ojo: es la
hora de la ESTAMPA, después de descargar (paso 1 de la Tarjeta 2), no la de
arranque del job:**

| Desvío | Sellos | Fechas |
|---|---|---|
| ≤ 5 min | 21 | — |
| 5–16 min | 14 | 09/13/15/20/21/22/23-jul, 28-jul, 06/07-ago, 13/17/20-ago (descarga + reintentos parciales de 60/120 s, o retraso de launchd: NO EVALUABLE sin los logs del Mac) |
| **≥ 60 min** | **6** | **29-jul 21:23 · 31-jul 19:40 · 03-ago 22:57 · 05-ago 21:38 · 10-ago 19:45 · 21-ago 19:41** (todos Mac; DarkWake/re-sleep y Yahoo según DECISIONES 5.0.1) |

De los 6 sellos ≥ 60 min: los **3 anteriores a las 20:00 Chile** (31-jul,
10-ago, 21-ago) apuntaron a la sesión correcta (0 filas con salto, 22 filas,
aciertan 11/22); los **3 posteriores a las 20:00** (29-jul, 03-ago, 05-ago)
produjeron **17 filas con salto de sesión, 4/17 aciertos** (rama histórica;
tras D1 quedan 7, 1/7). **La frontera medida es la apertura de Seúl/Tokio,
20:00 Chile, no las 18:15 del timer.**

**(3) Por job: qué se pierde si `Persistent=false` y qué cuesta correr
tarde con `true`:**

| Job | `false` (se pierde) | `true` (corre tarde) | Costo medido |
|---|---|---|---|
| **snapshot** | ningún sello ese día → hueco declarado en el track record y «sin dato sellado hoy» en Telegram; 0 filas contaminadas | sello con hora real; **si cruza las 20:00 Chile, las filas asiáticas apuntan a la sesión siguiente** (defecto `:140`) → filas con salto | 17 filas / 3 fechas en la historia, 4/17; con D1: 7 filas, 1/7 (Tarjeta 1). Con el parche `:140` firmado, un sello después de las 20:00 caería en `no_verificable_timing` (hueco, no contaminación) y `Persistent=true` deja de costar filas |
| **noticias** | titulares del día sin analizar; el sello de 18:15 (si corrió) ya no los usaba; el día siguiente los recoge (dedup + presupuesto diario) | corre tarde; si corre **después** del sello, no alimenta ese sello (lee la caché). Costo de IA: acotado por el tope diario (`costos.py`), y una fecha nueva rearma el tope | 0 filas; costo USD ≤ tope (0,50) |
| **reporte** | no hay Telegram ese día | compone desde el sello: si corre antes del sello dice «sin dato sellado hoy»; si después, reporte veraz pero tarde | 0 filas; el reporte nunca inventa (test del reporte 2.0) |
| **backup** | la fila espera al commit del día siguiente (el patrón ya visto 12/13/17-ago: 24 h) | commit tarde, mismo contenido; `mki_backup.py` commitea sólo `data/backups` | 0 filas; publicación +24 h (Tarjeta 2) |
| **vigía 19:00** | sin revisión ese día; una falla real no se avisa | alerta tarde; si corre después de un sello tardío, no ve nada raro | 0 filas; el hueco lo cubre parcialmente el re-chequeo |
| **re-chequeo 20:30** | una alerta abierta se queda sin epílogo (salvo que `snapshot.py` mismo la retracte: `_epilogo_vigia`) | retractación tarde | 0 filas |

**Estampida (6B.3):** si la máquina vuelve después de las 20:30 con las seis
corridas perdidas, con `Persistent=true` corren todas en el mismo minuto.
Sobre las bases, `snapshot` es idempotente (`ya_existe_snapshot_hoy`), el
backup commitea sólo si hay cambios, y noticias respeta el tope; el orden
relativo es el que systemd elija. **Ninguna corrida así ha ocurrido en esta
máquina (MEDIDO en logs); la auditoría de idempotencia de los 6 jobs sigue
sin hacerse (opción 2 del expediente).**

### Recomendación (PROPUESTA, para que el director de programa la dictamine)

**Opción M:** `Persistent=true` se **mantiene** en noticias, reporte, backup,
vigía y re-chequeo (correr tarde no cambia el significado de lo que producen
y perderlos cuesta observabilidad). Para **snapshot**, la decisión depende
de la Tarjeta 1 y del parche `:140`: **con el parche firmado, `true` es
seguro** (un sello tardío no contamina: cae en `no_verificable_timing`);
**sin el parche, `false`** —o `true` con una guardia en `snapshot.py` que
se niegue a emitir después de la apertura de Seúl— es lo que evita más
filas con salto. Como la guardia toca `snapshot.py` (regla cero) y el parche
también, **el orden sensato es firmar primero el parche y no tocar los
timers**. Mover timers es de Nicolás (`modo-emision`); esta tarjeta no los
toca.

### Qué se hace el día después de la firma

1. **Nicolás:** decide el orden (parche `:140` → timers) y, si cambia algún
   `Persistent`, edita `systemd/*.timer` y reinstala con `bash
   systemd/instalar.sh` (operación suya, no de un agente).
2. **`ingeniero-plataforma`:** la auditoría de idempotencia de solo lectura
   del expediente 6B.3 (cada job dos veces seguidas sobre una copia de las
   bases en directorio temporal), ANTES de cualquier `RandomizedDelaySec`.
3. **`ingeniero-plataforma`:** la causa de las dos corridas incompletas de
   noticias (01/02-sep) —esto sí puede mirarse en el journal, **por
   Nicolás**—; mientras tanto el vigía ya lo está avisando.
4. **Agente:** resolver la discrepancia 20:30:00 vs 20:34:41 del 25-ago
   (CLAUDE.md vs `vigia.log`) en la próxima acta de entorno.

---

## Tarjeta 4 — Cuál es el campeón cuando sello y fuente discrepan (caso del 28-ago)

### Qué decidir en una frase

Si, para la ventana sellada, **el campeón son las filas selladas** (y el
backtest B2 las LEE en vez de recomputarlas desde Yahoo) o su
**reconstrucción** desde la fuente de hoy —y, pegada, si se activa la copia
cruda de insumos al sellar (`GEMELO/INSUMOS/`, arnés probado y no activado).

**Dos propiedades distintas, dichas con todas sus letras:** el sello es
**«emitido antes»** (timestamps: `timestamp_utc` precede a la apertura
objetivo, verificable por la regla maestra) y **no es «reproducible
después»** (nadie puede hoy recomputar desde la fuente la fila que se selló,
porque la fuente no sirve el mismo estado). Hoy el sello tiene la primera y
no la segunda. La copia de insumos (`GEMELO/INSUMOS/`, candidata C3) le
daría la segunda hacia adelante; nada se la da hacia atrás.

### Opciones

| | Opción | Qué es el campeón en la ventana sellada | Qué cambia |
|---|---|---|---|
| **(a)** | **Las filas selladas son el campeón; B2 las lee** (C2/C5 del expediente) | lo que está en `senales_ticker` | `backtest/baselines.py` lee donde hay fila sellada y recomputa sólo antes del sello (y como test de paridad); el 5.1 sobre lo sellado deja de depender de Yahoo |
| **(b)** | **La reconstrucción manda** (C1) | lo que Yahoo sirva el día de la corrida | 16 signos y 32 magnitudes cambian con el estado de la fuente, y pueden volver a cambiar; el sello queda como «lo que se dijo» y no como «lo que se evalúa» |
| **(c)** | No declarar | dos objetos, ninguno manda | el statu quo que produjo el bloqueo (cola §17) |
| **+ C3** | Copia cruda de insumos al sellar | — | toca `snapshot.py` (una llamada protegida) + columna aditiva `insumos_sha256` + bump de plataforma; ~9 MB/año (130 barras consumidas) o ~53 MB/año (panel de 3 años), **medidos** (`fuente_canonica.md` §5.1, 2-sep) |

### Costo medido de cada opción sobre datos reales

**El caso del 28-ago, paso a paso (MEDIDO en `senales.db` esta noche +
CITADO del expediente `fuente_canonica.md` §3 y `docs/SEGUNDO_SELLO.md`
§0, ambos del 1/2-sep; no se descargó nada):**

1. **Qué selló el 28-ago (MEDIDO):** snapshot `2026-08-28T22:15:03Z`,
   `sox_fecha = 2026-08-28`, `sox_usado_pct = −3,47`; 8 predicciones a la
   sesión del 31-ago, todas negativas (000660.KS −3,19 · 005930.KS −2,38 ·
   2330.TW −1,24 · 3436.T −2,59 · 4063.T −1,14 · 6857.T −2,13 · 8035.T −2,12
   · IFX.DE −0,32), betas 0,09–0,92. Verificadas el 01-sep: los 8 gaps
   fueron negativos (−0,70 a −6,72) → **8/8 aciertos**.
2. **Qué selló el 31-ago (MEDIDO):** `sox_usado_pct = +0,57` (31 vs 28), 8
   predicciones positivas a la sesión del 01-sep (+0,04 a +0,50). Gaps del
   01-sep todos negativos (−0,20 a −3,85) → **0/8** (IFX.DE se verificó el
   02-sep; el expediente decía 0/7 con 1 pendiente: ya son 0/8).
3. **Qué sirve la fuente hoy (CITADO, 1-sep 16:12 UTC, cuatro formas de
   pedirla):** Yahoo **no tiene barra de `^SOX` para el 28-ago**; 10 de 19
   símbolos revisados la perdieron. Reconstruido, el 28-ago vale +2,33 %
   (27-ago) y el 31-ago −2,92 % (31 vs 27): **las 16 emisiones cambian de
   signo y las 32 magnitudes (16 aperturas + 16 betas) cambian**. Los dos
   sellos, tomados con 72 h de diferencia, implican el mismo cierre del 28
   (banda [11.469,26, 11.470,24]): **la producción vio un dato real que la
   fuente retiró**, no un dato roto.
4. **La regla maestra no está en juego:** las 16 filas fueron emitidas
   antes de sus aperturas objetivo (22:15 UTC → 00:00 UTC del día hábil
   siguiente). Lo que está en juego es qué se evalúa.

**La cifra viva bajo cada opción (MEDIDO, misma convención de cabecera;
la sustitución invierte el acierto de las 16 filas, que es exactamente lo
que el expediente mide como «signo contrario» — intento DSR):**

| Opción | Aciertos | Ventaja sobre «al alza» | IC de día | p perm. día | McNemar de la sustitución |
|---|---|---|---|---|---|
| **(a)** sello | 180/269 = 66,9 % | +14,1 pp | [−2,3, +30,9] | 0,117 | — |
| **(b)** reconstrucción | 180/269 = 66,9 % | +14,1 pp | [−2,3, +30,8] | 0,117 | **b = 8, c = 8, p = 1,00** (el 28 pierde 8, el 31 gana 8) |
| **(c)** no declarar | las dos, según qué corrida se mire | — | — | — |

Con la convención del expediente (2-sep, sin `excluir_cero`, IFX.DE del 31
aún pendiente): 179/276 = 64,86 % [59,1, 70,2] → 178/276 = 64,49 % [58,7,
69,9], b = 8, c = 7, p = 1,00; MAE 2,827 → 2,892 pp en esas 15 filas
(CITADO). **La cifra no se mueve en nada distinguible de cero bajo ninguna
convención; lo que se mueve es la reproducibilidad.** Y en la ventana del
README (corte 28-ago, n = 238) **ninguna de las 16 filas entra**: nada
publicado cambia bajo (a) ni bajo (b).

**Lo que cuesta (c), medido en corridas:** `backtest/resumen.md` ya
reprodujo producción dentro de 0,05 pp de media **excepto** el 28-ago
(3,62 pp de media, CITADO §5.4); `ventana_larga`, `CONDICIONAL` y cualquier
veredicto 5.1 cuya ventana incluya el 28-ago reconstruyen hoy un campeón de
signo contrario al sellado en dos fechas. Cada corrida futura puede dar otro
resultado si la fuente cambia de estado otra vez (ocurrió en una ventana de
≈18 h, ≥ 3 días después de nacer la barra: CITADO §0.2).

**Lo que la copia C3 compra y no compra (CITADO §5.5):** compra
«reproducible después» desde el primer sello con copia; no compra el pasado
(los 45 residuos de julio y el cierre exacto del 28-ago están perdidos y se
declaran perdidos) ni una segunda opinión sobre si el dato era correcto.

### Recomendación (PROPUESTA, para que el director de programa la dictamine)

**(a) + C3, en el mismo bump que el parche `:140`.** (a) porque es la única
opción bajo la cual el objeto que se evalúa es el objeto que se emitió, y el
5.1 sobre lo sellado pasa a ser independiente de lo que sirva Yahoo el
25-oct; el costo en cifra es cero medido (b = c = 8). C3 porque, sin ella,
(a) declara al sello campeón pero **nadie puede volver a computarlo**: es
«emitido antes» sin «reproducible después» para siempre, y cada noche que
pasa sin copia es una noche más que sólo se podrá inferir (como M6) y nunca
leer. Tres cortes de método (parche `:140`, columnas de la Tarjeta 2, copia
C3) en **un solo** `PLATAFORMA_VERSION` cuestan lo mismo que uno.
**Micro-decisión sin recomendación:** si la ventana larga publica fecha y
sha256 de su descarga como parámetro sellado (convención de reporte:
de Nicolás).

### Qué se hace el día después de la firma

1. **Nicolás:** acta con «el campeón de la ventana sellada son las filas
   selladas» y la fecha desde la cual existe copia de insumos
   (`acta-decision`); bump de `PLATAFORMA_VERSION` con los cortes de método
   que firme.
2. **Agente (backtest):** `backtest/baselines.py` B2 lee `senales_ticker`
   (`mode=ro`) donde hay fila sellada y recomputa sólo antes; test de
   paridad que compara recomputo vs sello **y declara** `BARRA_RETIRADA`
   cuando difieren en vez de fallar; footnote-errata en el `resumen.md`
   existente (nunca se recomputa el run viejo).
3. **Agente (`.diff` no aplicado + test sobre copia):** la llamada protegida
   `insumos.congelar(motor._cache, fecha)` al final de `ejecutar_snapshot`,
   la columna `insumos_sha256`, `data/insumos/` en el pathspec de
   `mki_backup.py`, y el chequeo del vigía «sello sin copia». **Aplicar el
   diff es de Nicolás.**
4. **Agente:** `docs/SEGUNDO_SELLO.md` pasa a comparar contra el panel
   completo (veredicto nuevo `INTERMITENTE`), sin cambiar la regla R-A («la
   primera gana siempre»).
5. **Nadie:** el README no se toca — ninguna cifra publicada cambia bajo (a).

---

## Cierre del frente

**(a) Archivos creados/modificados:** únicamente
`GEMELO/resultados/corrida09/tarjetas_09.md` (este documento). Los scripts
de cálculo vivieron en `/tmp/tarjetas09_calc.py` y `/tmp/tarjetas09_calc2.py`
(fuera del repo, a propósito: el encargo pide un único documento); la
receta está descrita en la cabecera y en cada tarjeta y se reproduce con
`linea_base.cargar(hasta_sello=None, dedup=True)` → `marcar_sesion` →
`aplicar_convencion("excluir_cero")` → `duelo` + `_bootstrap_dia(…, 4000)`
sobre `acierto_gap − base_acierto` agrupado por `fecha`.

**(b) Intentos del DSR consumidos: 7** — cada ventaja con intervalo
publicada sobre retornos reales: (1) cifra viva con todas, (2) sin A, (3)
sin B ≥ 19:00, (4) sin B ≥ 20:30, (5) sólo B ≥ 19:00, (6) rama dedup=False
sin A, (7) cifra viva bajo la opción (b) de la Tarjeta 4. «Sólo A» no
cuenta: no se publicó intervalo (k = 2). Ninguno es un modelo nuevo; todos
son particiones retrospectivas del campeón y se declaran para que el conteo
no se haga a conveniencia.

**(c) Qué quedó abierto:**
- La causa de las dos corridas incompletas de `mki_noticias.py` (01 y
  02-sep): sólo el journal la tiene, y el journal es de Nicolás.
- La discrepancia 20:30:00 (CLAUDE.md, GATE A-bis) vs 20:34:41 (`vigia.log`)
  del re-chequeo del 25-ago.
- Por qué el backup del Mac no commiteó las noches del 12, 13 y 17-ago (sello
  a tiempo, commit al día siguiente): sin logs del Mac, NO EVALUABLE.
- La auditoría de idempotencia de los 6 jobs (expediente 6B.3, opción 2)
  sigue sin hacerse.
- La ventaja «sin abstención» es una selección retrospectiva: si se quiere
  una cifra de la regla, sale del retador con la regla declarada antes de
  correr, no de acá.

**(d) Errores propios, cometidos y corregidos:**
- Primer intento de cómputo con `python` sin activar el venv (comando no
  encontrado); corregido activando `venv/`.
- `pgrep -af` con el patrón de los jobs devolvió mi propia shell (la línea
  de comando contenía el patrón); corregido con `pgrep -fl` filtrando
  `bash`/`pgrep`: no hay job vivo.
- Partí de 19:00 y 20:30 como umbrales horarios «naturales» (vigía y
  re-chequeo); los datos mostraron que el umbral que gobierna es la
  apertura de Seúl/Tokio (20:00 Chile) y que 20:30 ≡ 20:00 sobre estos
  sellos. Se publican los dos computados y se declara el tercero como
  hallazgo, no como un tercer intento.
- Estuve por citar «n = 248» del expediente del 2-sep como cifra viva;
  está retirada desde hoy (acta §78, `cifras_retiradas.md`): la sustituí por
  la de la convención firmada (n = 238 en el README; n = 269 vivo acá) y
  cito la del expediente sólo con su fecha y su convención.
