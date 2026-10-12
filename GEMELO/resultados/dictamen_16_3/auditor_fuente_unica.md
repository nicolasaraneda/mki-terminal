# Auditoría de fuga y dictamen de corrección del `auditor-lookahead` sobre el Bloque A de la corrida 16-3: la fuente única de las cifras vivas publicadas (actas §93.4, §93.4-bis ii, §99.6)

> Archivado por el orquestador tal como lo devolvió el agente (el agente no escribe archivos). Lanzado a las 20:04 de
> Chile del 11-oct-2026 sobre el worktree `wt163` (HEAD `ad4b829` + los cambios de la corrida, sin commitear). Inicio
> **20:04:37**, cierre **20:24:50** (horas de `date` del agente, −03:00). Nada escrito en ningún árbol ni base; `senales.db`
> sólo en `mode=ro`; huellas de las tres bases idénticas a las de apertura al cerrar. **Cómo se atendieron las cinco
> bloqueantes: bitácora 16-3 §5.1.** El ERROR de B3 lo midió el orquestador después del dictamen: ocurre igual en HEAD
> puro y en el árbol real sin los cambios (preexistente; cerrado marcando el test `red`).

## VEREDICTO

**APLICABLE CON EXIGENCIAS** (cinco bloqueantes, ocho recomendadas).

El límite duro del encargo 16-3 §1 se cumple y lo demostré con mi propia medición, no con la del orquestador: **ninguna
cifra cambia por otra razón que las filas que la exclusión de conocibilidad retira.** No encontré fuga temporal en el
bloque. Las cinco bloqueantes son de declaración, de verificación en el árbol real y de higiene de tests, no de cifra.

## 1. Lo verificado (comando y cifra)

### 1.1 La prueba decisiva del §1: la cifra nueva es la vieja menos las 8 filas, y nada más (MEDIDO)

Construí en memoria una base idéntica a la real pero poblada **sólo con las filas que la regla deja pasar** (esquema
copiado de `sqlite_master`, filas copiadas desde `mode=ro`, sin borrar nada), corrí las funciones **reales de
`senales.py`** contra ella y las nuevas contra la base real en `mode=ro`, y comparé con `DataFrame.equals` (valores,
dtypes, nombres de columna **y orden de filas**) para los frames y por igualdad exacta de dict para las demás:

```
senales_ticker alcanzadas por la regla: 24 | fechas: ['2026-09-28']
insertadas en la base filtrada: {'senales_ticker': 1591, 'snapshots': 68, 'divergencias': 401,
                                 'verificacion_apertura': 482, 'verificacion_puntaje': 1366}
original intacto: 663552 bytes mtime 1791580524162450663

=== NUEVA(real) == VIEJA(real filtrada por la regla) ===
OK  metricas_apertura{'dias': 30}:  n=141 gap 63.8 MAE 4.07 | sesión 67.4 MAE 2.31  (ambas)
OK  metricas_apertura{'dias': 90}:  n=458 gap 65.7 MAE 2.98 | sesión 62.4 MAE 3.07  (ambas)
OK  metricas_apertura{'dias': 365}: n=482 gap 65.6 MAE 2.99 | sesión 62.7 MAE 3.07  (ambas)
OK  calibracion_intervalos{}:       n=482 cobertura 93.6  (ambas)
OK  evolucion_aciertos_apertura{}:  n_vieja=63 n_nueva=63 cols_iguales=True
OK  ultimas_predicciones_apertura{'limite': 50}:  n=50  cols_iguales=True
OK  ultimas_predicciones_apertura{'limite': 100}: n=100 cols_iguales=True
OK  ultimas_predicciones_apertura{'limite': 500}: n=482 cols_iguales=True
OK  verificaciones_detalle{}:       n_vieja=482 n_nueva=482 cols_iguales=True
OK  analisis_puntaje_ia{'dias': 90}:  n=1308 alto 0.31 bajo 1.58 corr -0.07  datos_equals=True
OK  analisis_puntaje_ia{'dias': 365}: n=1366 alto 0.05 bajo 1.42 corr -0.08  datos_equals=True

FALLOS: ninguno
```

Once configuraciones, incluidas ventanas 30/90/365 y límites 50/100/500. El caso `limite=500` compara la **secuencia
completa de 482 filas**: eso es la prueba empírica del orden, no una conjetura. `datos_equals=True` en
`analisis_puntaje_ia` prueba que la permutación del `sort_values` (quicksort, no estable, con 513 empates) es la misma,
índice por índice.

Antes/después publicados, reproducidos de forma independiente con las funciones reales de `senales.py` sobre un
respaldo en memoria de la base real:

| cifra | antes | después |
|---|---|---|
| `metricas_apertura(30)` | n 149, gap 62,4 %, MAE 3,95; sesión 65,1 %, MAE 2,31 | n 141, gap 63,8 %, MAE 4,07; sesión 67,4 %, MAE 2,31 |
| `calibracion_intervalos` | n 490, 93,5 % | n 482, 93,6 % |
| `evolucion` | 64 fechas, N 490 | 63 fechas, N 482 |
| `ultimas(100)` | 2026-09-21 a 2026-10-08 | 2026-09-18 a 2026-10-08 |
| `verificaciones_detalle` | 490 | 482 |
| `analisis_puntaje_ia(90)` | n 1308, 0,31 / 1,58 / −0,07 | idéntico |

Las cifras del orquestador son correctas al decimal.

### 1.2 Ventana, filtros, redondeo, columnas, dtypes (MEDIDO)

- Ventana: las dos fuentes usan la **misma expresión de SQLite** `fecha_senal >= date('now', '-N days')` (día UTC).
  `date('now')` al medir: `2026-10-11`; corte de 30 días `2026-09-11`.
- Filtros: `v.legacy = 0 AND v.modelo_version = ?` en las cinco de apertura; `gap_pct IS NOT NULL` en todas menos
  `ultimas` (replicado por `solo_con_gap=False`); en puntaje, `s.timestamp_utc IS NOT NULL AND s.modelo_version = ?` sin
  filtro de legacy, igual que la vieja.
- Redondeo: 1 decimal en porcentajes, 2 en MAE y en los tercios; sumas con `sum()` de Python sobre listas, igual que el
  `sum(f[i] for f in filas)` viejo.
- Columnas y nombres: idénticos en las cuatro funciones que devuelven frame, verificado con `columns.tolist()`.
  `_COLUMNAS_ULTIMAS` reproduce el orden y los nueve nombres con tilde y símbolo. El frontend los consume tal cual
  (`frontend/src/vistas/Historial.tsx:290` `dataKey="% Aciertos gap"`, `:62` `f['Gap real %']`, `:80` `f['Emitida (UTC)']`),
  así que el contrato de pantalla no se mueve.
- dtypes: idénticos. `evolucion` `['str','float64','float64','int64']`; `ultimas`
  `['str','str','float64','float64','float64','int64','int64','str','str']`; `detalle`
  `['str','str','int64','int64','float64','float64','float64','str','float64','str']`; `analisis_puntaje_ia['datos']`
  `['float64','float64']` con el mismo índice.
- `apertura_estimada_pct`: la nueva sirve el de **`verificacion_apertura`** en `ultimas` y `detalle` (como la vieja) y el
  **sellado de `senales_ticker`** (`estimado_sellado`) en la calibración (como la vieja). No se cruzaron. Dato de
  contexto: hoy coinciden (0 de 490 filas discrepantes), así que el error habría sido invisible en esta base; el código lo
  hace bien de todas formas.

### 1.3 El orden de filas, que es lo que hace que las sumas y los tercios den lo mismo (MEDIDO)

`EXPLAIN QUERY PLAN` sobre las cuatro consultas viejas, en la base real `mode=ro`:

```
metricas_vieja: SEARCH verificacion_apertura USING INDEX sqlite_autoindex_verificacion_apertura_1 (fecha_senal>?)
ultimas_vieja:  SCAN v USING INDEX sqlite_autoindex_verificacion_apertura_1
puntaje_vieja:  SEARCH s USING INDEX sqlite_autoindex_senales_ticker_1 (fecha>?)
                SEARCH v USING INDEX sqlite_autoindex_verificacion_puntaje_1 (fecha_senal=? AND ticker=?)
detalle_vieja:  SCAN v USING INDEX sqlite_autoindex_verificacion_apertura_1
```

Las cuatro se sirven por el autoindex `(fecha_senal, ticker)` (la de puntaje maneja desde `senales_ticker`, cuyo
autoindex es `(fecha, ticker)`), que es exactamente el orden que la función nueva **fija** con `ORDER BY`. Afirmación
del comentario del módulo: verificada. Ver R3 sobre su fragilidad.

### 1.4 Los LEFT JOIN nuevos no pueden multiplicar filas (MEDIDO)

Esquema de la base real: `senales_ticker UNIQUE(fecha, ticker)`, `snapshots fecha TEXT PRIMARY KEY`,
`verificacion_apertura UNIQUE(fecha_senal, ticker)`, `verificacion_puntaje UNIQUE(fecha_senal, ticker)`. Los tres JOIN de
`cargar_vivas` y el de `cargar_puntaje_vivo` son sobre claves únicas: ninguna fila se duplica, y el `n` no puede
inflarse por el JOIN. Esto es lo que hace equivalente el cambio de `INNER JOIN` + `s.intervalo80_pp IS NOT NULL` (vieja
calibración) por `LEFT JOIN` + `notna()` (nueva).

### 1.5 La prueba maestra del mandato: invarianza a truncar el dataset en `t` (MEDIDO, con contraprueba)

Dos bases en memoria, una completa y una truncada en `t = 2026-09-15`, mismo código:

```
corte t = 2026-09-15
filas verificacion_apertura: completa 490 | truncada 365
evolucion  (fechas <= t): completa 48 vs truncada 48  | IDENTICAS: True
detalle    (filas  <= t): completa 365 vs truncada 365 | IDENTICAS: True
cargar_vivas(filas <= t): completa 365 vs truncada 365 | IDENTICAS: True
exclusion por fila: misma decision en las filas <= t: True
CONTRAPRUEBA (columna que depende del total de fechas): IDENTICAS: False (tiene que ser False)
```

El predicado de exclusión es **local a la fila** (`zip` sobre dos columnas selladas) y la agregación de `evolucion` es
por fecha: ninguna cifra de una fila depende de filas posteriores. La contraprueba inyecta una dependencia del futuro
y el test la caza, así que la prueba puede fallar.

Única excepción, por diseño y declarada: los tercios de `analisis_puntaje_ia` son un **ranking transversal de la
ventana** y sí cambian al truncar (`retorno_tercio_alto` 0,05 → −0,25 al truncar en `t`). Es una cifra de evaluación
sobre una ventana cerrada, no un insumo; ya era así antes del bloque. Va a zonas ciegas (Z5).

### 1.6 Fuga de sellado: los dos instantes que la regla lee son inmutables (MEDIDO)

Censo de toda sentencia de modificación sobre la tabla de señales en el repo (5 ocurrencias, todas en `senales.py:167,
338, 361, 385, 415`): **las cinco tocan sólo `estado`**. Ni `timestamp_utc` ni `available_at` se reescriben nunca
después del `INSERT`. El predicado de exclusión se computa sobre columnas selladas inmutables, así que su valor es el
mismo hoy que el día del sello: la exclusión **no es un filtro con información futura**, una fila pudo haber sido
excluida en el instante mismo en que se selló.

### 1.7 Fuga de calendario: los husos y los feriados son los reales (MEDIDO)

```
XKRX: 10-08:ABIERTA(00:00-06:30Z)  10-09:CERRADA  10-12:ABIERTA  10-13:ABIERTA
XTAI: 10-08:ABIERTA(01:00-05:30Z)  10-09:CERRADA  10-12:ABIERTA  10-13:ABIERTA
XTKS: 10-08:ABIERTA  10-09:ABIERTA  10-12:CERRADA  10-13:ABIERTA(00:00-06:30Z)
XETR: 10-08:ABIERTA(07:00-15:30Z)  10-09:ABIERTA  10-12:ABIERTA  10-13:ABIERTA
XNYS: las cinco ABIERTAS (13:30-20:00Z)
```

Seúl y Taipéi cerrados el viernes 9-oct; Tokio cerrado el lunes 12-oct (segundo lunes de octubre).
`proxima_sesion_despues_de` resuelve bien los seis casos de las filas pendientes: el «cierre de NY anterior» y la
«sesión objetivo» de cada fila pendiente son los reales y no un relleno. Ninguna cifra del bloque mezcla un dato de
Fráncfort con uno de Tokio: cada fila lleva su propio `exchange` y su propia `sesion_objetivo` sellados, y la cifra
agregada es un conteo de aciertos por fila, no una correlación entre husos.

### 1.8 Sólo lectura, y el reporte no llama al motor (MEDIDO)

`test_las_funciones_nuevas_abren_la_base_solo_en_modo_ro` recorre el AST y exige que ninguna de las ocho funciones llame
a `connect`/`get_connection`/`init_db`, y que el módulo no importe `senales`. Lo confirmé por lectura: todas pasan por
`_conexion_ro` (`mode=ro`). Esto **mejora** el estado anterior: las seis viejas corrían `init_db()` (DDL, apertura en
escritura) sobre la base sellada en cada llamada de la API, del reporte y del dashboard.
`test_las_seis_no_modifican_la_base_que_leen` compara bytes y `st_mtime_ns`.

### 1.9 La suite, literal

Lo exigido por el encargo, desde el worktree:

```
$ cd <wt163> && venv/bin/python -m pytest tests/test_fuente_unica_16_3.py tests/test_reporte.py \
    tests/test_linea_base.py tests/test_conocibilidad.py -q -p no:cacheprovider
FAILED tests/test_linea_base.py::test_el_corte_congelado_recupera_exactamente_las_228_filas
1 failed, 72 passed, 19 skipped, 1 warning in 5.72s
```

Subconjunto ampliado, con `-m "not red"` (no saqué la red: eran las 20:17 de Chile, dentro de la franja 17:50-20:30 que
la guarda de `tests/conftest.py` protege; domingo, sin jobs):

```
$ ... tests/test_fuente_unica_16_3.py tests/test_reporte.py tests/test_linea_base.py \
      tests/test_conocibilidad.py tests/test_api.py tests/test_bifurcaciones.py \
      tests/test_frescura.py tests/test_guarda_puntaje.py -q -p no:cacheprovider -m "not red"
FAILED tests/test_linea_base.py::test_el_corte_congelado_recupera_exactamente_las_228_filas
FAILED tests/test_api.py::test_D1_la_friccion_del_juego_activo_viaja_como_objeto_con_banda
FAILED tests/test_api.py::test_D3_la_sigma_servida_y_el_MDE80_no_comparten_oracion
FAILED tests/test_api.py::test_D9_el_mapa_no_se_sirve_sin_presupuesto_ni_modo
FAILED tests/test_api.py::test_D11_que_lo_mata_no_dice_que_R2_no_esta_recomputado
FAILED tests/test_api.py::test_D12_D13_cobertura_con_wilson_y_etiqueta_de_regimen
FAILED tests/test_api.py::test_D15_los_dos_denominadores_de_la_senal_larga_van_separados
ERROR tests/test_api.py::test_paridad_roca_chip_contra_snapshot - Failed: REG...
7 failed, 133 passed, 33 skipped, 6 deselected, 25 warnings, 1 error in 21.29s
```

**Diagnóstico de cada rojo, contra el control de HEAD que el propio orquestador archivó** (worktree a HEAD puro sin
bases: `19 failed, 1044 passed, 90 skipped, 6 errors`):

- Los **7 de 7 FAILED están en la lista del control de HEAD**: no los causa el Bloque A. Los seis de `test_api` (`D1,
  D3, D9, D11, D12_D13, D15`) revientan en `api/main.py:1179` `_estado_rieles()`, que necesita `dinero/sello_dinero.db` y
  corridas selladas que el worktree no tiene.
- El rojo de `test_linea_base` sí tiene causa nombrable y está en el alcance: lo produce el `senales.db` **stub de 0
  filas** que la propia suite crea en la raíz del worktree (49.152 bytes, mismo tamaño en `wt163` y en `wt163_ctrl`). La
  compuerta de la línea 195 es `if not os.path.exists(...)`, así que **no se salta** y asevera `0 == 228`. Reproduje la
  aserción en sólo lectura contra la base real: `len(_congelado()) = 228`, `excluir_cero = 223`, `len(cargar(dedup=False))
  = 482 >= 228`. La aserción es correcta; la compuerta es la que falla. Ver B4.
- El **ERROR no está en el control de HEAD**: es la guarda `_vigilar_red` de `tests/conftest.py` diciendo que
  `test_paridad_roca_chip_contra_snapshot`, que **no lleva `@pytest.mark.red`**, tocó la red. Candidato a regresión del
  fixture `_bases_de_la_api` nuevo. Ver B3. [Nota del orquestador: medido después, ocurre igual en HEAD puro y en el
  árbol real sin los cambios bajo `-m "not red"`; preexistente.]

Línea base del árbol real que el orquestador archivó antes de tocar nada (19:30 a 19:38): **`1151 passed, 8 skipped,
1 xfailed, 29 warnings in 487.00s`, EXIT 0**. Es contra ésa que hay que comparar al aplicar.

**No corrí el subconjunto contra la base real con rutas parcheadas.** Abstención deliberada, por la cláusula del encargo
(«si dudas, no los corras: dilo»): para que los tests `solo_con_base` vieran la historia real habría tenido que forzar
`lb.RUTA_SENALES`, `senales.DB_PATH` y `bases_de_prueba.RUTA_SENALES` antes de la recolección, y uno de esos tests llama
a `senales.verificar_apertura_pendientes()`. El riesgo de escribir en la base sellada no vale la confirmación, sobre
todo porque la hice yo con una prueba más estricta (1.1). Consecuencia declarada: **la conducta del bloque sobre
historia real está atestiguada por mis mediciones, no por la suite.** Ver B2.

### 1.10 Lo que `senales.py` no cambió (MEDIDO)

`senales.py` es **byte a byte idéntico** en el worktree, en el árbol real y en HEAD: md5
`5bb705dca0f2b9b74ebada02e725a3ba` en los tres. `git diff senales.py` vacío. La regla cero se respeta.

## 2. Exigencias

### BLOQUEANTES

**B1. El acta de aplicación tiene que decir que §93.4 nombró `cargar()` y que el bloque no implementó `cargar()`.** El
texto firmado de §93.4 dice literalmente: «La API, el reporte de Telegram y el dashboard (93.4-bis ii) leen sus
métricas de `backtest/linea_base.py::cargar()`». `cargar()` lleva `dedup=DEDUP_OFICIAL` (True) por defecto: aplicarlo al
pie de la letra habría deduplicado y movido el `n` de las cifras de toda la historia, que es lo que el encargo 16-3 §1
prohíbe. El bloque resolvió la contradicción a favor del §1 creando `cargar_vivas()` (sin dedup) y mandando la
deduplicación a firma. **La resolución es la correcta**, pero la tarjeta §82 declara «la deduplicación no se aplica» sin
decir que la letra firmada nombraba la función que sí deduplica. Sin esa frase, el acta registra como «aplicado según
§93.4» algo que no es la letra de §93.4, y Nicolás ratifica sin ver que hubo una contradicción entre su firma y el
encargo. Magnitud exacta a declarar en la misma frase, MEDIDA por mí: 10 filas, calibración y detalle 482 → 472,
acierto del gap de toda la historia 65,6 % → 66,3 %, ventana de 30 días 141 → 141.

**B2. La suite completa del árbol real, después de aplicar, contra la línea base archivada.** La corrida del worktree no
puede zanjar nada: 19 de los tests pertinentes se SALTAN por falta de base poblada, uno pasa **vacuamente** (B4) y el
stub de 0 filas cambia qué se salta. Exigible: `venv/bin/python -m pytest tests/ -q` en el árbol real, comparado contra
la apertura (`1151 passed, 8 skipped, 1 xfailed`, EXIT 0), más `python tests/test_motor.py` (que pytest no recolecta),
más las huellas de las tres bases antes y después. Rige «un verde antes del sello no es un verde»: fuera de la franja
17:50-20:30 de Chile.

**B3. El ERROR de la guarda de red hay que cerrarlo, no heredarlo.** `tests/test_api.py::test_paridad_roca_chip_contra_snapshot`
no lleva `@pytest.mark.red` y la guarda `_vigilar_red` registró que tocó la red en `wt163`; el control de HEAD no
muestra ese ERROR. El marcador `red` existe precisamente para que `scripts/guarda_red.sh` y el hook puedan excluir esos
tests **dentro de la franja en que el sistema sella**: un test que sale a Yahoo sin declararlo es un test que no se puede
dejar fuera de esa ventana. Hipótesis (DEDUCIDA, hay que MEDIRLA): el fixture `_bases_de_la_api` nuevo copia sólo si la
base real existe; en un árbol sin bases la API queda sin snapshot sellado y la paridad de `roca_chip` cae al motor en
vivo. En el árbol real, con bases pobladas, probablemente no dispara. Exigible: MEDIR en el árbol real; si dispara, o se
marca `red` o se arregla el fixture. No se aplica con un ERROR de la guarda de red abierto.

**B4. Las dos compuertas sin migrar de `tests/test_linea_base.py` (líneas 195 y 204).** La corrida escribió
`tests/bases_de_prueba.py` con el criterio correcto («la tabla que el test lee tiene filas», en `mode=ro`, sin crear
nada) y migró el marcador `solo_con_base` del mismo archivo, pero dejó dos compuertas de cuerpo de función con el viejo
`if not os.path.exists(lb.RUTA_SENALES): pytest.skip(...)`. Con el stub de 0 filas: la línea 195 **falla** (`0 == 228`) y la
línea 204, `test_la_base_viva_ya_creció_por_encima_del_corte`, **pasa vacuamente** (`0 >= 0`). Ese segundo caso es el
peor: un test cuyo propósito declarado es detectar que «la base se vació o el sellado se detuvo» pasa precisamente
cuando la base está vacía. Exigible: las dos compuertas a `hay_filas(lb.RUTA_SENALES, "verificacion_apertura")`, y un
censo de si quedan otras `os.path.exists` con la misma función en el resto de `tests/`.

**B5. La nueva dependencia del reporte de Telegram respecto de que el motor sea IMPORTABLE.** MEDIDO: envenené el import
de `motor` con un `MetaPathFinder` y `alertas.componer_reporte_sellado()` **revienta con `ImportError`**; `_cli_reporte`
(línea 359) lo llama sin `try/except`, así que el job de las 18:25 muere con traceback y no se envía reporte alguno, no
sólo la línea del track record. Causa: `backtest/linea_base.py` importa `RUTA_SENALES` y `_conexion_ro` de
`backtest/datos.py`, que importa `motor` a nivel de módulo. Antes del bloque, el reporte sólo necesitaba `senales` y
`noticias`: la garantía constitucional es «un test fulmina todas las funciones del motor y el reporte igual compone», y
el test nuevo `test_el_reporte_sigue_sin_llamar_al_motor_con_la_fuente_nueva` fulmina las **funciones**, no el
**import**, así que no cubre esto. Atenuantes MEDIDOS: `import alertas` (0,08 s), `import snapshot` (0,40 s) e `import
mki_vigia` no arrastran `backtest.linea_base`, el import perezoso en frío cuesta 0,39 s, y el fallo es ruidoso y el
vigía lo caza por la línea ISO de `reporte.log`. Exigible una de dos, a elección del implementador: (a) desacoplar, que
son dos símbolos triviales (`RUTA_SENALES` y `_conexion_ro`) y hoy arrastran `motor`, `yfinance`, `exchange_calendars` y
`numpy`; o (b) declarar el modo de falla nuevo en la tarjeta §82 y fijarlo con un test que envenene el import (no la
función) y verifique la conducta elegida. Lo que **no** es aceptable es un `try/except` que caiga a las seis viejas de
`senales.py`: eso republicaría la cifra contaminada en silencio.

### RECOMENDADAS

**R1. Ningún test fija la equivalencia `lb` vs `senales` sobre la base REAL.** `tests/test_fuente_unica_16_3.py` la fija
sobre bases sintéticas de 8 y 9 filas; `tests/test_api.py` perdió su contraste independiente al pasar `esperado` de
`senales.*` a `lb.*` (queda comprobando la capa de serialización de la API, que es legítimo, pero ya no cruza dos
implementaciones). La equivalencia sobre 490 filas reales la atestigua hoy sólo mi medición de §1.1. Recomendado:
archivar esa medición como evidencia en el acta, y mejor, un test `solo_con_base` que la repita (la técnica del respaldo
en memoria con `CREATE` + `INSERT` desde `mode=ro` no escribe nada y no necesita permisos).

**R2. El juego sintético no ejercita un empate de puntaje EN el borde del tercio.** `FILAS_SANAS` da puntajes ordenados
0,1 · 0,2 · 0,4 · 0,4 · 0,4 · 0,6 · 0,7 · 0,9 con `corte = max(1, 8//3) = 2`: ningún empate cae sobre ninguno de los dos
cortes. El borde es el único lugar donde el `sort_values` de pandas (quicksort, no estable) podría divergir si el orden
de entrada cambiara. En la base real hay 513 empates y coincide hoy (`datos_equals=True`), pero el test no lo protege.
Recomendado: una fila más que ponga un empate justo sobre el corte.

**R3. El test de equivalencia depende de un orden que las consultas viejas no fijan.** `senales.metricas_apertura` **no
tiene `ORDER BY`**; `ultimas` y `detalle` ordenan sólo por fecha. Hoy el plan de SQLite usa el autoindex `(fecha_senal,
ticker)` en las cuatro (MEDIDO, §1.3), y por eso el bloque acierta. En otra versión de SQLite, tras un `ANALYZE`, o en el
Mac, el plan puede cambiar y `test_sin_filas_invertidas_la_fuente_nueva_da_exactamente_lo_mismo_que_senales` se pondría
rojo por una razón ajena al bloque (compara con `DataFrame.equals`, que es sensible al orden). El código nuevo **mejora**
el estado anterior porque fija el orden; el test es el que hereda la fragilidad. Recomendado: para los frames, comparar
también como multiconjunto ordenado, o que la réplica del test imponga el `ORDER BY` explícito que el plan hoy regala.

**R4. `shutil.copy` sobre la base viva en el fixture `_bases_de_la_api`.** Una copia tomada mientras el escritor de las
18:15 tiene una transacción abierta puede salir rota y producir un rojo espurio. Recomendado: la API de respaldo de
sqlite desde una conexión `mode=ro` (`src.backup(destino)`), que es la técnica que usé en esta auditoría: atómica, sin
riesgo y con el mismo resultado.

**R5. `ultimas_predicciones_apertura` no retira 8 filas: retira 8 y admite 8 más antiguas.** El `LIMIT` se aplica DESPUÉS
de la exclusión, que es el orden correcto, y por eso la ventana del límite 100 corre de 21-sep a 18-sep. La tarjeta y la
enmienda del contrato dicen la mitad. Recomendado: «retira 8 y, por el `LIMIT` fijo, admite 8 más antiguas».

**R6. La tarjeta §82 publica la mitad favorable de la dirección del efecto.** Declara «de las 8, el modelo acertaba 3
(37,5 %); la exclusión mejora la cifra viva del campeón». Faltan los tres números que **fortalecen** la defensa y que
medí: (i) el MAE del gap se mueve en contra (3,95 → 4,07 pp), porque las 8 filas retiradas tenían MAE 1,81 pp, mejor que
el 3,95 de la ventana: la regla no está optimizando nada; (ii) 37,5 % es ruido de un día, no una anomalía (17 de los 56
días con n ≥ 8 están en o por debajo de esa tasa; la distribución diaria tiene p25 = 38 % y mediana 75 %; `P(≤3 aciertos
en 8 | p = 0,624) = 0,139`); (iii) la deduplicación pendiente **también** favorece al campeón (+0,75 pp: 65,6 % → 66,3 %,
porque sus 10 filas tienen acierto 3/10). Ese último punto merece una frase propia: **dos reglas de higiene pendientes
apuntan en la misma dirección.** No es evidencia de nada por sí solo, y la razón es estructural (una regla que retira
filas selladas en condiciones anómalas retira días malos, porque los días anómalos son malos), pero un auditor posterior
va a notar el patrón y es mejor que lo encuentre escrito.

**R7. Tres copias del predicado de conocibilidad.** `senales.py` lo tiene dos veces en línea (verificador de apertura,
líneas 357-360; verificador de puntaje, líneas 471-474) y ahora `lb.sin_conocibilidad` es la tercera. Verifiqué que son
semánticamente idénticas por lectura y con una batería de 6 casos (`None`, uno de los dos `None`, igualdad exacta, naive
leído como UTC, offset `-03:00` equivalente, cadena vacía): las tres parsean ISO, leen naive como UTC, disparan con `>`
estricto y no disparan con NULL ni con igualdad. El auditor de la 16a ya recomendó una sola copia; la tercera sube la
apuesta, porque una deriva entre la guarda del ESCRITOR y la exclusión del MEDIDOR sería invisible.

**R8. `lb._instante_utc` revienta con texto ISO malformado** (`ValueError: Invalid isoformat string: 'basura'`, MEDIDO
con tres cadenas). Antes del bloque las cifras publicadas nunca parseaban esas dos columnas: sumaban columnas de SQL.
Ahora un solo `available_at` malformado en cualquier parte de la historia mata el reporte, la ruta de la API y la vista
del dashboard. Probabilidad baja (`snapshot.py` escribe con `isoformat()`), pero es un acoplamiento nuevo entre higiene
del dato y cifra publicada. Recomendado: declararlo, o tratar el texto ilegible como «no se puede juzgar» (que es la
semántica que la regla ya eligió para NULL y para la igualdad) y declarar la cuenta.

## 3. Respuestas a las preguntas a-e

### (a) ¿Puede la exclusión introducir sesgo de selección DIRECCIONAL que favorezca al campeón?

**Sí, y la dirección es favorable al campeón en las dos cifras de titular. MEDIDO:**

```
filas retiradas: 8 | fechas: ['2026-09-28']
  acierto_gap 3/8 = 37.5% | acierto_sesion 2/8 = 25.0%
  MAE gap de las retiradas 1.81 pp | MAE sesion 2.32 pp
ventana 30d: con las retiradas n=149 gap 62.4% MAE 3.95
             sin las retiradas n=141 gap 63.8% MAE 4.07
  DIRECCION: gap +1.4 pp | sesion +2.3 pp | MAE gap +0.12 pp (positivo = peor)
```

Tres cosas que hay que decir juntas, o la respuesta engaña:

1. **La dirección es favorable en el acierto y adversa en el error.** El gap sube +1,4 pp y la sesión +2,3 pp, pero el MAE
   del gap **empeora** 0,12 pp, porque las 8 filas retiradas tenían MAE 1,81 pp (mejor que el 3,95 de la ventana). Una
   regla construida para favorecer al campeón habría movido las dos en la misma dirección. Ésta no.
2. **La magnitud es ruido de un día.** `P(≤3 aciertos en 8 | p = 0,624) = 0,139` a una cola; y entre los 56 días con n ≥
   8, **17** tienen una tasa de acierto del gap igual o inferior al 37,5 %. La distribución de la tasa diaria es min 0 %,
   p25 38 %, mediana 75 %, p75 100 %, max 100 %. El 28-sep es un día malo del montón, sentado en el percentil 25, no un
   atípico. Las 8 filas son además de **un solo día**, así que su n efectivo es ~1 día: en la escala en que la propia
   `cifras.py` mide (ICC y `deff` por clúster de día) este movimiento no es distinguible de cero.
3. **Por qué la regla está a salvo aunque la dirección sea favorable:** se firmó por su mérito y el acta lo dejó escrito
   antes de cualquier resultado. §90.1 d, 29-sep-2026: «Criterio escrito antes de aplicarlo, y es por regla, no por fecha:
   no se nombra el 28-sep en el código», y «la regla se firma por su mérito (es la que el otro riel ya aplica y endurece
   la regla maestra), no por la magnitud del daño medido en la sección 9 de la bitácora 14, que además quedó PROVISIONAL
   por 8035.T». Verifiqué que el código cumple la letra: `sin_conocibilidad` no menciona ninguna fecha; hoy alcanza 24
   filas de `senales_ticker` (8 verificadas) y las alcanzaría igual mañana si volviera a pasar.

**Residuo honesto, que va a zonas ciegas (Z2):** el acta misma registra que «el verificador de las 18:15 del 29-sep ya
escribió las 8 filas del 28-sep en `verificacion_apertura` ANTES de esta firma (la firma es de las 18:29)», y la magnitud
estaba en la bitácora 14 §9. La dirección era computable por quien redactó la regla, en una ventana de 14 minutos. No es
demostrable en ninguna de las dos direcciones; se declara.

### (b) ¿Queda alguna ruta PUBLICADA leyendo las seis viejas o `verificacion_apertura` directo para una cifra de acierto?

**No. Censo completo, MEDIDO** (`grep` por las seis funciones y por `verificacion_apertura`/`acierto_*` en todo el repo,
excluyendo `venv/` y `tests/`):

| ruta | estado |
|---|---|
| `alertas.py` | limpia. `lb.metricas_apertura(dias=30)` (:283), `lb.calibracion_intervalos()` (:292). Cero llamadas a `senales.*` de las seis |
| `api/main.py` | limpia. `lb.*` en :540, :565, :765, :811, :812, :828, :830, :836. Los Wilson y los desgloses (:776, :794) agrupan el frame de `lb.verificaciones_detalle()` de :765 |
| `app.py` | limpia. `lb.*` en :951, :1456, :1620, :1638, :1655, :1668, :1698 |
| `frontend/` | limpia por construcción: consume las claves del JSON, nunca computa una señal. Verifiqué que las claves que lee (`% Aciertos gap`, `Gap real %`, `Emitida (UTC)`, `track_record.*`) son exactamente las que la fuente nueva sirve |
| `mki_vigia.py` | **cero coincidencias** con las seis y con `verificacion_apertura`. No publica cifra de acierto |
| `cifras.py` | limpia, y por dos vías independientes. Su única lectura directa (`:131-134`) se cruza con `how="inner"` (`:137`) contra `crudo = lb.cargar(hasta_sello=CORTE_README, dedup=True)`, que ya pasó por la exclusión; y además su corte es `CORTE_README = 2026-08-28`, anterior al 28-sep, así que las 8 filas quedan fuera de su ventana de todos modos |
| `scripts/generar_readme.py` | limpia. No toca `senales.py` ni la base: toda cifra sale de `cifras.sellada()` y `cifras.larga()` |
| `snapshot.py` | sólo nombra `verificacion_apertura` en `TABLAS_BACKUP_SENALES` (:41), para el respaldo CSV. No es una cifra |
| `replica.py`, `comparar_sombra.py` | cero coincidencias |

Las seis de `senales.py` quedan definidas y **sin consumidor publicado**.
`test_ningun_consumidor_publicado_llama_a_las_seis_de_senales` lo fija por AST sobre los tres archivos, con contraprueba
de que el detector ve una llamada real.

**Matiz que hay que declarar y que la tarjeta §82 ya declara:** quedan dos familias de cifra publicada con convención
distinta. La ventana sellada del README (`cifras.py`, corte 28-ago, **con** deduplicación) y las cifras vivas (**sin**
deduplicación). Difieren en 10 filas de julio y agosto, y difieren así desde el 1-sep-2026. El bloque no crea esa
diferencia; la hereda y la pone a firma.

### (c) ¿Puede el import perezoso romper `snapshot.py` o `mki_vigia.py`?

**No rompe el import de ninguno de los dos. Sí introduce un modo de falla nuevo en el reporte. MEDIDO:**

```
import alertas: 0.08s   | backtest.linea_base en sys.modules? False | motor? False
import snapshot: 0.40s  | backtest.linea_base en sys.modules? False
import mki_vigia: 0.00s | backtest.linea_base en sys.modules? False
import perezoso backtest.linea_base EN FRIO: 0.39s
arrastra: motor, yfinance, exchange_calendars, api.utilidades, backtest.datos, backtest.emision, numpy
```

El import perezoso cumple su propósito: `snapshot.py` y `mki_vigia.py` importan `alertas` y **no** pagan nada.
`backtest/datos.py` importa `motor`, `calendarios`, `universo`, `numpy`, `pandas` y `backtest.emision` a nivel de módulo
(y `backtest/emision.py` sólo `calendarios`), y `linea_base` añade `api.utilidades`; ninguno hace red ni escritura al
importarse, y nada reemplaza `motor._datos_crudos` por importar (eso sólo pasa dentro del gestor de contexto
`FuenteCongelada`).

Lo que sí cambia: `componer_reporte_sellado()` ahora exige que `import motor` **funcione**. Con el motor roto al
importar, revienta con `ImportError` (medido, §2 B5), y `_cli_reporte` no lo protege: el job de las 18:25 muere entero.
Contra `test_jamas_llama_al_motor`: ese test y el nuevo `test_el_reporte_sigue_sin_llamar_al_motor_con_la_fuente_nueva`
fulminan las **funciones** del motor y el reporte compone bien, porque la fuente nueva no las llama. La garantía que se
debilita es la del **import**, no la de la llamada, y ningún test la cubre. Es B5.

### (d) ¿La decisión de NO deduplicar está declarada con exactitud y sin exceso?

**Sí, con exactitud: verifiqué los cinco números de la tarjeta §82 y los cinco coinciden. MEDIDO:**

```
cargar(dedup=True) n: 472 | cargar(dedup=False) n: 482
filas que la dedup retiraria, TODA la historia: 10
fechas: ['2026-07-29', '2026-08-03']
detalle: 7 filas del 2026-07-29 (000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T)
       + 3 del 2026-08-03 (2330.TW, 3436.T, 4063.T)
auditar_dedup: pares 23 | pares_resueltos 10 | pares_las_dos_calzan 13 | pares_sin_criterio 0

calibracion n hoy: 482 -> con dedup: 472
detalle   n hoy: 482 -> con dedup: 472   (acierto del gap 65.6% -> 66.3%)
metricas(30) n hoy: 141 -> con dedup: 141
evolucion fechas hoy: 63 -> con dedup: 63
corte de 30 dias: 2026-09-11 | retiradas dentro de la ventana: 0
acierto_gap de las filas que la dedup retiraria: 3 / 10
```

**Sin exceso**, con una salvedad y un añadido:

- La salvedad es B1: la declaración es exacta en la magnitud pero omite que la letra de §93.4 nombraba `cargar()`, que
  deduplica.
- El añadido es R6: las 10 filas tienen acierto 3/10 contra el 65,6 % del conjunto, así que la deduplicación **también**
  subiría la cifra publicada (+0,75 pp). La tarjeta da el 65,6 % → 66,3 % pero no lo nombra como lo que es: la segunda
  regla de higiene pendiente que apunta a favor del campeón.
- Un dato que la tarjeta no trae y que conviene al §82: `auditar_dedup` sobre el conjunto vivo declara **23 filas sin
  pareja cuya `sesion_objetivo` no calza con su `available_at`** (y 33 que no calzan en total). La regla firmada no las
  toca por diseño (arbitra entre dos filas que compiten, no descarta sin reemplazo). Son más que las 10 que la dedup
  retiraría, y siguen dentro de la cifra publicada.
- «0 en la ventana de 30 días» sobrevive al lunes, pero **no porque no haya duplicados**: el lunes aparecen tres pares
  nuevos dentro de la ventana, y sobrevive porque son del caso «calzan las dos», que la regla conserva deliberadamente
  (ver (e)).

### (e) ¿Qué pasa el lunes 12-oct a las 18:25 y a las 19:00?

**La predicción del encargo es correcta al decimal. MEDIDO:**

```
ventana >= 2026-09-12: antes de excluir 141 | despues 133
  gap 67.7% MAE 4.04 | sesion 70.7% MAE 2.20

pendientes hoy: 11
  2026-10-08  000660.KS  XKRX  objetivo 2026-10-12
  2026-10-08  005930.KS  XKRX  objetivo 2026-10-12
  2026-10-08  2330.TW    XTAI  objetivo 2026-10-12
  2026-10-09  000660.KS  XKRX  objetivo 2026-10-12
  2026-10-09  005930.KS  XKRX  objetivo 2026-10-12
  2026-10-09  2330.TW    XTAI  objetivo 2026-10-12
  2026-10-09  IFX.DE     XETR  objetivo 2026-10-12
  2026-10-09  3436.T     XTKS  objetivo 2026-10-13
  2026-10-09  4063.T     XTKS  objetivo 2026-10-13
  2026-10-09  6857.T     XTKS  objetivo 2026-10-13
  2026-10-09  8035.T     XTKS  objetivo 2026-10-13
  por fecha de senal: 3 del 8-oct, 8 del 9-oct | por objetivo: 7 el 12-oct, 4 el 13-oct
  ninguna invertida (sin_conocibilidad = False en las 11)
```

**Consulta exacta para verificar la predicción el lunes** (en `mode=ro`, sin escribir nada; `date('now','-30 days')` dará
`2026-09-12` desde las 00:00 UTC del 12-oct, y el reporte de las 18:25 de Chile son las 21:25 UTC del mismo día UTC):

```sql
-- las 133 de piso, replicando la ventana del lunes y aplicando la regla en Python
SELECT v.acierto_gap, v.error_gap_pp, v.acierto_direccion, v.error_pp,
       s.timestamp_utc, s.available_at
  FROM verificacion_apertura v
  LEFT JOIN senales_ticker s ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
 WHERE v.legacy = 0 AND v.modelo_version = '4.6.0' AND v.gap_pct IS NOT NULL
   AND v.fecha_senal >= '2026-09-12'
 ORDER BY v.fecha_senal, v.ticker;
-- filtrar con backtest.linea_base.sin_conocibilidad(timestamp_utc, available_at) == False
-- equivalente de una línea, ya con la fuente nueva:
--   lb.RUTA_SENALES = '<ruta>/senales.db'; lb.metricas_apertura(dias=30)
```

**Corrección a la predicción, por precisión de redacción, no de cifra:** `n = 133` es el **piso**, el valor si el
verificador del lunes no escribe ninguna fila. El job de las 18:15 corre el verificador **antes** del reporte de las
18:25, así que el reporte del lunes leerá `133 + k`:

- Las **7 con objetivo 2026-10-12** se pueden verificar el lunes: sus sesiones cierran 06:30 UTC (XKRX), 05:30 UTC (XTAI)
  y 15:30 UTC (XETR), todas con mucho más que el margen de 2 h antes de las 21:15 UTC del job. Si Yahoo sirve los seis
  cierres, `k = 7` y el lunes el reporte dice **n = 140**.
- Las **4 de XTKS con objetivo 2026-10-13** no pueden: Tokio está cerrado el lunes 12 (segundo lunes de octubre, MEDIDO
  con `exchange-calendars`). Se verifican el martes.
- Las 8 filas con `fecha_senal = 2026-09-11` salen de la ventana, y el 133 **ya** las excluye.
- Ninguna de las 11 es invertida, y la guarda (a) de §90.1 está **viva** en `senales.py:357-360`, así que el lunes no
  puede entrar ninguna fila invertida nueva a `verificacion_apertura`. La exclusión de la capa de medición queda como
  cinturón y tirantes para las 8 históricas.

**El vigía de las 19:00** no toca ninguna de las seis cifras (cero coincidencias en el censo de (b)), así que el bloque no
cambia su conducta. Dos cosas suyas siguen igual y no son de este bloque: sigue corriendo DDL sobre la base sellada dos
veces por día hábil (tarjeta §83) y sigue alertando la igualdad `available_at == timestamp_utc`.

**Hallazgo lateral que destapa el lunes, para el `estadistico-adversario`, no para mí:** porque Seúl y Taipéi cerraron el
viernes 9-oct, las emisiones del 8-oct y del 9-oct de `000660.KS`, `005930.KS` y `2330.TW` apuntan **a la misma sesión
objetivo, el 12-oct**. Son tres pares duplicados nuevos **dentro** de la ventana de 30 días. La regla de deduplicación
firmada **no** los retira: medí que los dos miembros de cada par «calzan» con su `available_at`, que es el caso de
feriado que la regla conserva a propósito. Consecuencia estadística, no de fuga: desde el lunes la cifra viva de 30 días
cuenta **dos veces** la sesión del 12-oct de Seúl y de Taipéi para el mismo ticker. El `n` sube en 3 sin tres
observaciones independientes. Es el mismo hecho que la tarjeta §87 nombra para los pares de feriado del 5-jul y del
7-sep.

## 4. Zonas ciegas declaradas

**Z1. Fuga de sellado, residual, y ahora con número.** MEDIDO: en los 67 snapshots que llevan los dos instantes,
`creado_en` es **idéntico** a `timestamp_utc` (mediana 0,0 s, p90 0,0 s, max 0,0 s; 0 con brecha > 60 s). `creado_en` no
es el instante de escritura: es el mismo estampado, copiado. **No existe ningún campo en la base que registre cuándo una
fila se hizo visible.** Por eso la regla de conocibilidad puede cazar una sola de las dos formas del problema: la que
medí que caza es «la disponibilidad DECLARADA es posterior al estampado» (la firma del 28-sep, 24 filas, margen mínimo
medido `ts − av = −8.221 s`, dos horas diecisiete). Es estructuralmente ciega a la simétrica: «el estampado precede al
cómputo real», que es el precedente del 6-ago documentado en CLAUDE.md (estampa 18:24, escritura ~19:08, 44 minutos de
congelamiento). En una fila así, `available_at` se computa del calendario y sigue siendo nominalmente válido, así que la
regla **no dispara**. Este bloque no ensancha esa ceguera, pero tampoco la estrecha, y la cifra que publica descansa
sobre ella.

**Z2. Fuga por el analista, sobre la regla.** §90.1 d se firmó el 29-sep a las 18:29 de Chile, **14 minutos después** de
que el verificador de las 18:15 ya hubiera escrito las 8 filas en `verificacion_apertura`, y la magnitud estaba en la
bitácora 14 §9 (marcada PROVISIONAL por 8035.T). El acta declara el orden de método explícitamente, que es la defensa
correcta y la única disponible para una regla que nace de un incidente. Pero la dirección del efecto (3/8) era
computable por quien redactó la regla en el momento de redactarla. No es demostrable en ninguna dirección. Se declara.

**Z3. Fuga por el analista, sobre este bloque.** Las seis funciones, el juego de filas sintéticas y los umbrales de los
tests los diseñó un agente que ya vio la ventana sellada y ya conoce las 8 filas que la exclusión retira. `INVERTIDA` en
el test está construida como «el 28-sep-2026 en miniatura». Eso es lo correcto para un test de reproducción y es, al
mismo tiempo, la zona ciega: nada aquí es un hallazgo fuera de muestra. La única defensa es el sellado en vivo.

**Z4. Fuga de revisión silenciosa y de disponibilidad.** Las cifras 482 / 141 descansan sobre `gap_pct`, `acierto_gap` y
`error_gap_pp` computados en el instante de la verificación, con precios descargados ese día. Yahoo revisa la historia
sin avisar, y el incidente del 28-ago es el precedente de que un dato disponible al sellar puede dejar de ser
reproducible después. Este bloque no vuelve a descargar nada, así que es inmune por construcción: lee filas selladas.
Pero las cifras que sirve **no son point-in-time respecto de la fuente**, y una verificación tardía podría no
reproducirlas.

**Z5. `analisis_puntaje_ia` es la única cifra publicada que NO es invariante a truncar.** MEDIDO: truncando en
`2026-09-15`, `retorno_tercio_alto` pasa de 0,05 a −0,25. Los tercios son un ranking transversal de la ventana. Es
inherente a un estadístico de ranking sobre una ventana cerrada, es anterior a este bloque y es una cifra de
**evaluación**, no un insumo: esa cifra nunca puede alimentar un modelo, y si alguna vez se usa como feature, es fuga.

**Z6. 32 de las 1.308 filas del puntaje están exactamente en el borde que la regla no juzga.** MEDIDO: en las cifras
vivas de apertura (482 y 141) hay **0** filas con `timestamp_utc` o `available_at` nulos y **0** con igualdad. En el
puntaje (1.308) hay **32 con `available_at == timestamp_utc`** al instante, que la regla deliberadamente no retira (rama
del `except` de `snapshot.py`, con su alerta en el vigía, §84.2); coincide con el residuo de 32 que el acta §94.4 ya
declaró. Y la exclusión en el puntaje es hoy **no operativa**: 1.366 filas antes y después, porque la guarda de la 16a
ya no deja entrar invertidas.

**Z7. El worktree mezcla el Bloque A con otros bloques de la corrida.** Mi dictamen cubre el Bloque A. En el mismo
worktree viven cambios ajenos (`app.py` R9, `SellosDinero.tsx`, tests de higiene e integridad, `tests/conftest.py`,
`tests/bases_de_prueba.py`, dos archivos `ext_2026-09-14.no_verificable.*` sin seguimiento y `GEMELO/cache`). No los
auditié. Si el diff se commitea entero, el acta tiene que decir qué dictamen cubre cada parte; `tests/conftest.py`,
`tests/bases_de_prueba.py` y `tests/test_api.py` quedan en la frontera y los toqué sólo por B3 y B4.

**Z8. Lo que mis propias pruebas no cubren.** (i) No corrí el subconjunto contra la base real con rutas parcheadas. (ii)
Todo lo que medí es con **un** motor de SQLite y **una** versión de pandas, los del `venv` del árbol real; la
equivalencia de orden (R3) y la permutación del quicksort con empates (R2) no están garantizadas en otra máquina, y el
Mac corre los mismos archivos. (iii) No salí a la red (`-m "not red"`), así que B3 queda DEDUCIDA y no MEDIDA en el
árbol real. (iv) Todo censo de rutas publicadas es un `grep` más una lectura: una llamada construida por reflexión no la
vería; no encontré ninguna, pero el censo es un piso, no un techo.

## 5. Resumen en una línea

El bloque cumple el límite duro del §1 y lo demostré en 11 configuraciones sobre la base real con igualdad exacta de
frames y de dicts (la cifra nueva es la vieja menos las 8 filas del 28-sep, nada más), pasa la prueba maestra de
invarianza a truncar con contraprueba, y no introduce fuga temporal; queda APLICABLE CON EXIGENCIAS por cinco razones
que no son de cifra: declarar que §93.4 nombró `cargar()` y el bloque implementó otra cosa (B1), correr la suite real
contra la línea base archivada (B2), cerrar el ERROR de la guarda de red (B3), terminar de migrar dos compuertas que hoy
dejan un test pasando vacuamente (B4) y resolver que el reporte de Telegram ahora muere si el motor no es importable (B5).
