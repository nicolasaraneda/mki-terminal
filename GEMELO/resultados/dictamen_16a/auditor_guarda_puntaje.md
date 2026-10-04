# Auditoría de fuga del `auditor-lookahead` sobre la guarda de conocibilidad de `verificar_puntaje_pendientes` (corrida 16a)

> Archivado por el orquestador tal como lo devolvió el agente (el agente no escribe archivos). Lanzado a las 13:33 de
> Chile del 4-oct-2026 sobre el worktree `wt16a` (HEAD `902106e`); inicio del agente **13:33:54**, cierre **13:46:05**
> (horas de `date` del agente). Nada escrito en ningún árbol; `senales.db` del árbol real con tamaño y mtime idénticos
> al inicio y al cierre (`614400` bytes, `2026-10-02 18:15:16.400903857 -0300`, comprobado cinco veces).
>
> Nota del orquestador sobre la zona ciega 2 del dictamen («los 26 rojos del worktree están atribuidos, no probados»):
> después del cierre del auditor se corrió el control que pedía (los siete archivos rojos en el mismo worktree con el
> parche guardado con `git stash`, HEAD puro): 31 failed, 150 passed, 6 errors; **ningún rojo aparece sólo con el
> parche** (bitácora 16a §4.1, `evidencia/suite_worktree_HEAD_puro_7_archivos.txt`).

## VEREDICTO: APLICABLE CON EXIGENCIAS

La guarda hace lo que dice, en el lugar correcto, con la comparación correcta, con el radio de explosión exacto que el
encargo permite, y **no introduce ninguna fuga nueva**: el predicado lee dos columnas de tiempo selladas y nunca el
resultado (`retorno_5d_pct`), de modo que es ciego al desenlace. Las exigencias bloqueantes son de aplicación y de
declaración, no de diseño.

Aplicar hoy es, además, un **no-operativo conductual medido**: hoy el verificador tiene 3 candidatas (todas del 24-sep,
ninguna invertida); el lunes tiene 27, de las cuales 24 invertidas. La guarda no mueve nada hoy y muerde exactamente las
24 el lunes.

## 1. Lo verificado (comando y cifra)

1. **Identidad y aplicabilidad del parche.** sha256 del `git diff` del worktree = sha256 de
   `GEMELO/propuestas/parches/guarda_puntaje_16a.diff` = `641120072764a4579ba9cb7d322917dcc6fbb16123596dce3fa4cb2e593fe25b`.
   `git apply --check` sobre el árbol real: sin error.
2. **Límite duro del encargo (sólo `verificar_puntaje_pendientes`), probado por AST.** `git diff --stat`: `senales.py |
   42 +++---` (39 inserciones, 3 borrados); cuatro hunks, los cuatro dentro de la función. AST nuevo vs HEAD: funciones
   sólo en nuevo: ninguna; sólo en viejo: ninguna; con AST distinto: `['verificar_puntaje_pendientes']`; statements de
   módulo idénticos (16 vs 16); imports nuevos dentro de la función: ninguno. **Un solo nodo del árbol cambió.**
3. **Ninguna fila sellada se reescribe, probado por verbos SQL.** Verbos en literales de la función nueva: `{'INSERT':
   1, 'SELECT': 1}`; en HEAD: idénticos; `execute()`: 2 en ambas. Cero `UPDATE`, cero `DELETE`, cero DDL. La única
   escritura sigue siendo el `INSERT OR IGNORE`.
4. **NULL, igualdad, instantes.** `if disponible_en:` deja fuera NULL y cadena vacía; la query ya filtra `timestamp_utc
   IS NOT NULL`. `conocible > emitida` estricto: la igualdad no dispara, y la justificación del comentario se verificó
   en la fuente: `mki_vigia.py:97-101` alerta `available_at = reloj de pared` cuando `av is None or av == ts`.
   Instantes con zona (`fromisoformat` + `replace(tzinfo=utc)` si naive), como la guarda (a); el test texto-vs-instante
   fallaba sobre HEAD.
5. **La guarda va antes de la red.** `continue` antes de `_ohlc_local`; el test asserta `ohlc.llamadas == []`.
6. **Test nuevo corrido por el auditor en el worktree:** `12 passed, 1 skipped in 2.72s`.
7. **Los 5 rojos sobre HEAD, uno por uno:** `reproduccion_…_no_entra`, `compara_instantes_y_no_texto` y
   `no_depende_del_estado` fallan por su propia aserción de conducta (reproducciones genuinas); `declara_la_cuenta` y
   `es_por_regla_y_no_por_fecha` fallan por la superficie nueva (la línea de aviso, `available_at` en el fuente). **3 de
   5 son reproducción de conducta y 2 son especificación de superficie nueva.**
8. **Suite del worktree: NO verde, y por qué.** `20 failed, 929 passed, 82 skipped, 1 xpassed, 6 errors · EXIT 1`
   contra el árbol real de las 13:31:14 `1019 passed, 5 skipped, 1 xfailed · EXIT 0`. Aritmética: 1025 recolectados en
   el real; 1038 en el worktree; diferencia 13 = los tests del archivo nuevo. Rojos por artefactos gitignorados
   ausentes: la `senales.db` del worktree es de 48 K y VACÍA (creada por la propia suite a las 13:33:53 vía
   `init_db()`, ruta documentada en `tests/test_backup_orden.py:830`); `dinero/sello_dinero.db` ausente;
   `backtest/resultados` 76 K vs 6,0 M. Los siete archivos rojos tienen 0 menciones de `verificar_puntaje_pendientes`,
   `verificacion_puntaje` o `verificar_pendientes`. 82 saltados vs 5: 77 se saltan solos por falta de base.

## 2. Pregunta obligatoria (§2.4): ¿otra ruta por la que una fila invertida llegue a `verificacion_puntaje`?

Censo de escritores (grep en todo el repo, sin `venv/` ni `node_modules`): `senales.py:97` (DDL), `:433` (lectura, el
candidateo), **`:453` `INSERT OR IGNORE INTO verificacion_puntaje`, único escritor de producción**, `:633`
(`analisis_puntaje_ia`, lectura); `snapshot.py:42` (export a CSV); `scripts/restaurar_backup.py:149-166` (DDL + carga
desde CSV a base nueva); `tests/test_importador_roundtrip.py:492` (base sintética). Un solo camino hasta el escritor:
`senales.py:466 verificar_pendientes()` → llamado por `snapshot.py:300` y por el fallback del dashboard `app.py:828`.
(Nota del orquestador, exigencia E2 del guardián: los números de línea de `senales.py` de este párrafo son los de HEAD
`902106e`, medidos por el auditor ANTES del parche; en el árbol que se commitea se desplazan +30: el `INSERT` está en
la **483**, `verificar_pendientes()` en la **500** y `analisis_puntaje_ia` en la **663**. `:97` y `:433` no cambian.)

**Respuesta: NO existe otra ruta de producción.** Ni la API, ni `dinero/`, ni `GEMELO/`, ni `backtest/`, ni el vigía,
ni la sonda escriben en la tabla: todos abren `senales.db` en `mode=ro`. La guarda en un punto cierra los dos caminos.

Dos salvedades: (1) `scripts/restaurar_backup.py` es un escritor, pero a una base NUEVA en ruta temporal, y replica el
CSV tal cual sin aplicar la guarda; hoy `data/backups/senales_verificacion_puntaje.csv` tiene **0 filas del 28-sep de
1.272**; si un día entraran filas invertidas y después se promoviera una restauración a base titular, volverían sin pasar
por la guarda: ruta condicional y humana. (2) **La exclusión es un predicado, no un estado**: `available_at >
timestamp_utc` se recomputa en cualquier momento desde dos columnas selladas; cualquier fila que llegue por una ruta
imprevista sigue siendo detectable en `mode=ro`. Medido hoy: el cruce `verificacion_puntaje ⋈ senales_ticker WHERE
available_at > timestamp_utc` da **0**. Ninguna de las 1.272 filas ya escritas está invertida.

## 3. Dictamen sobre la elección del §2.2: CORRECTA, y la evidencia es más fuerte de lo que el agente argumentó

Medición en la base real sobre las 24 filas del 28-sep: **16 sin estado, sin `apertura_estimada_pct` y sin
`sesion_objetivo`** (la query del verificador de apertura exige ambas `IS NOT NULL`: esas 16 nunca pertenecieron a esa
máquina de estados y jamás pasarán por ella; escribirles `no_verificable_timing` sería fabricar un estado para filas que
ninguna máquina reclama y contaminar `conteo_por_estado()`); **las otras 8 están `verificada`** (reescribir su estado
viola el corte de método de §90.1 y la Constitución 5.0 punto 3). La alternativa descartada no era sólo fea: era
estructuralmente imposible sin inventar. La elección es la única compatible con las reglas firmadas.

Qué se pierde, nombrado: (1) no queda registro por fila en la base; la declaración vive en stdout → `data/snapshot.log`
(verificado en la unidad instalada, `StandardOutput/StandardError=append:`), y ese log rota (`registro.py:17`, 2 MB × 2):
la declaración es efímera; mitigación estructural: la exclusión es función pura de dos columnas selladas, recomputable
para siempre, epistémicamente mejor que un flag almacenado. (2) Si el llamador es el dashboard (`app.py:828`), la línea
va a la consola de Streamlit y se pierde. (3) La cuenta no viaja en el valor de retorno (`-> int`), asimetría con el
verificador de apertura; corregirla toca la firma y dos llamadores. (4) La fila queda candidata para siempre y se
re-declara cada corrida; atenuado porque la línea imprime las fechas. (5) El verificador de puntaje ignora por completo la
máquina de estados de apertura, y ya lo hacía: hay **2 filas en `verificacion_puntaje` cuyo `senales_ticker.estado` es
`sin_datos_mercado`**; no lo introduce este parche, lo hereda y lo hace explícito.

## 4. El PIN de la regla maestra

**La regla maestra NO está en el diff**, confirmado por tres vías (verbos SQL y `execute()` idénticos a HEAD; sin
`calendarios` ni `apertura_utc` en la función, que el propio test asserta; AST cambiado sólo en el bloque de la guarda).

**Juicio del `test_pin_la_regla_maestra_no_esta_en_este_verificador`: honesto, pero con la polaridad invertida. No
entroniza la debilidad; la documenta mal.** Su verde asserta como esperada la conducta tolerante a la fuga. El proyecto ya
tiene el modismo correcto: `xfail(strict=True)` sobre la conducta deseada (`tests/test_dinero.py:567`, con el guardia de
`tests/test_razones_xfail.py`); escrito así, la aserción documentaría la regla correcta y el estado del test el hueco.
**Y le falta la magnitud**, medida: filas de `verificacion_puntaje` por estado de su `senales_ticker`: sin estado 875 ·
verificada 395 · `sin_datos_mercado` 2 · `no_verificable_timing` 0; candidatas del 5-oct por estado: sin estado 16 ·
verificada 11 · `no_verificable_timing` 0. **El hueco es real en el código y está VACÍO en el dato**: 0 filas emitidas
tarde han entrado nunca, 0 de las 27 candidatas del lunes lo están. Eso hace defendible el diferimiento de §93.4 y es la
cifra que debería estar en el docstring, fechada.

## 5. Mediciones en la base real (`mode=ro`)

- (a) Filas con `available_at > timestamp_utc`: **24**, todas del 2026-09-28, todas con `puntaje_ia`; 16 sin estado + 8
  `verificada`; las 24 invertidas también por instantes.
- (b) Candidatas con `date('2026-10-05','-7 days')`: **27** = {2026-09-24: 3, 2026-09-28: 24}; invertidas: 24. Las 3
  del 24-sep no están invertidas (`available_at 20:00:00 < timestamp_utc 21:15:04`): control de la predicción falsable.
- (c) Filas del 28-sep hoy en `verificacion_puntaje`: **0**. Total: 1.272; `MAX(fecha_senal) = 2026-09-24`.
- (d) Hoy el parche es un no-operativo: 3 candidatas, 0 invertidas.
- (e) Sanidad de formatos entre las 27 candidatas: 0 vacíos, 0 no parseables, 0 NULL, 0 igualdades. La guarda no puede
  lanzar `ValueError` sobre el conjunto del lunes.
- (f) El residuo que la guarda deja pasar: de 1.413 filas con `puntaje_ia`, 1.339 con `available_at < timestamp_utc`,
  24 invertidas (excluidas), **32 con igualdad** (reloj de pared) y **18 con `available_at` NULL**: 50 filas con
  conocibilidad no demostrada siguen entrando; coherente con la guarda (a) por diseño; el vigía alerta la igualdad, no el
  NULL.
- (g) La cifra que esto protege: `analisis_puntaje_ia(dias=90)`, n = 1.254 hoy, servida en `api/main.py:831` y
  `app.py:1661`. **`backtest/linea_base.py` no contiene la palabra `puntaje`**: la fuente única de §93.4 NO cubre esta
  cifra; esta guarda es hoy su única protección. Hueco a nombrar en la corrida 16.

## 6. Exigencias BLOQUEANTES (antes de commitear)

- **B1.** El commit tiene que incluir `tests/test_guarda_puntaje.py` (el diff no lo trae).
- **B2.** La suite del árbol real tiene que quedar verde y su salida literal archivada; línea base de hoy 13:31:14:
  `1019 passed, 5 skipped, 1 xfailed · EXIT 0`; después de aplicar se recolectan 1038. El `1 xfailed` del real apareció
  como `1 xpassed` en el worktree (`tests/test_epistemico.py:572`, no estricto, atribuido a artefactos ausentes); si en
  el árbol real pasa a `xpassed`, hay que mirarlo (`--runxfail`).
- **B3.** Declarar que el badge congelado de tests queda desfasado: `docs/readme/badges_congelados.json::
  tests_recolectados = 1025`; con el archivo nuevo son 1038 (+13). El valor publicado no se mueve (§90.4, README fuera
  del alcance); la actualización va en la 16 cambiando los tres valores juntos.
- **B4.** Verificar la aplicación por hash: `git diff senales.py | sha256sum` =
  `641120072764a4579ba9cb7d322917dcc6fbb16123596dce3fa4cb2e593fe25b`; `git status --short` sin otro archivo de código.

## 7. Exigencias RECOMENDADAS (corrida 16)

- **R1.** Una sola copia de la comparación de instantes (hoy duplicada en los dos verificadores): un helper de módulo,
  fuera del límite de hoy.
- **R2.** Que la cuenta de excluidas viaje en el retorno, no sólo en stdout.
- **R3.** Que alguien automático lea la exclusión: el vigía o `/salud` pueden recomputar el predicado en `mode=ro`, sin
  columna nueva y sin depender de un log que rota.
- **R4.** Convertir el PIN a `xfail(strict=True)` sobre la conducta deseada, con la magnitud medida y fechada en su
  razón; verificar con `--runxfail`.
- **R5.** Hacer discriminante el test de historia real: hoy `candidatas_invertidas = 0` y toma la rama `else`; con
  `_ohlc_local` vacío sus aserciones de invariancia son tautológicas; sólo la del AVISO distingue guarda de cortocircuito,
  y sólo desde el 5-oct.
- **R6.** §72, sin firmar, es la raíz: `available_at` es calculado por convención, no observado; la guarda compara una
  conocibilidad declarada.

## 8. Zonas ciegas

1. La guarda nunca se ejecutó contra las 24 filas reales (el test de historia real se salta en el worktree). El
   predicado exacto se evaluó sobre los valores reales en `mode=ro` (24/24 invertidas por instantes, 0 no parseables),
   pero la ruta de código no corrió sobre ellas.
2. Los 26 rojos del worktree están atribuidos, no probados (ver la nota del orquestador arriba: el control se corrió
   después).
3. La declaración de la exclusión es efímera y depende del llamador.
4. Fragilidad heredada: un `available_at` o `timestamp_utc` no parseable lanza `ValueError` en el bucle y, con el
   `commit()` al final, se pierden los `INSERT` de esa corrida (propiedad de HEAD y del verificador de apertura).
5. Igualdad y NULL siguen pasando: 32 + 18 filas; el NULL sin alerta.
6. Nada en este parche es point-in-time respecto de la fuente: `_ohlc_local` descarga hoy la historia de hace cinco
   sesiones; la guarda protege el orden de conocibilidad del insumo, no la reproducibilidad del objetivo.
7. La suite abre la base sellada en modo escritura (DDL vía `init_db()`); ningún test llama `verificar_puntaje_pendientes`
   sin parchear `DB_PATH` (comprobación por grep, no prohibición mecánica).
8. Dirección del efecto sobre la cifra publicada, no medida: las 24 se sellaron con NYSE abierto, así que su
   `puntaje_ia` incorpora información del mismo día; la expectativa es que `analisis_puntaje_ia` quede igual o peor,
   nunca mejor. Predicción falsable: si tras el 5-oct la correlación publicada mejorara, hay que explicar por qué.
9. **Fuga por el analista, declarada:** la guarda, sus tests y la elección del §2.2 las diseñó un agente que ya vio el
   evento y sus marcas exactas; el auditor leyó la misma ventana. Defensa estructural verificada: el predicado es ciego al
   desenlace. Sin defensa: el momento (aplicar el domingo anterior al día en que las 24 entrarían), firmado por Nicolás en
   §93.4-bis (i). La única defensa real sigue siendo el sellado en vivo.
10. Fuga de especificación y de calendario: este parche no crea ninguna feature ni toca calendarios; la exigencia sobre
    `_ohlc_local` (ffill en feriados, supuesto #1) sigue abierta, fuera del alcance de hoy.

## 9. Predicción falsable que este dictamen respalda (martes 6-oct, `mode=ro`)

```sql
SELECT COUNT(*) FROM verificacion_puntaje WHERE fecha_senal = '2026-09-28';                 -- esperado 0
SELECT COUNT(*) FROM verificacion_puntaje v JOIN senales_ticker s
  ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
 WHERE s.available_at > s.timestamp_utc;                                                     -- esperado 0
SELECT fecha_senal, COUNT(*) FROM verificacion_puntaje
 WHERE fecha_senal >= '2026-09-24' GROUP BY 1;                                               -- esperado 2026-09-24: 3
-- grep "AVISO verificador puntaje" data/snapshot.log → "24 fila(s) ... fechas: 2026-09-28"
```

Si (1) o (2) dan distinto de 0, la guarda no quedó aplicada o entró por otra ruta. Si (4) está vacío y (1) da 0, el
verificador no corrió.

**Resumen en una línea:** el parche es correcto, mínimo (un nodo del AST), ciego al desenlace, sin escritura nueva, con
reproducción de conducta genuina en 3 de los 5 rojos de HEAD, y aplicarlo hoy no mueve ninguna cifra de hoy; lo que falta
es que entre al commit con su test, que la suite del árbol real quede verde contra la línea base, y que el desfase +13
del badge congelado quede declarado. **APLICABLE CON EXIGENCIAS.**
