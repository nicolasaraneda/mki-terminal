# Auditoría de fuga del `auditor-lookahead` sobre el bloque 1 de la corrida 15

> Archivado por el orquestador tal como lo devolvió el agente (resumen fiel; el agente no escribe
> archivos). Lanzado a las 23:10 de Chile del 29-sep-2026 sobre el worktree `wt15`; devuelto a las
> **23:17:32** (hora de `date` del agente). Su salida de pytest: `scratchpad/aud15/pytest_verificacion.txt`
> (sesión). Nada escrito en ningún árbol.

## Veredicto

**APLICABLE CON EXIGENCIAS.** Las tres guardas son correctas y ninguna apaga un sello bueno mañana; lo
que NO se puede afirmar después de aplicarlas es que la fuga esté cerrada: `metricas_apertura()` sigue
contando hoy las 8 filas invertidas y `verificar_puntaje_pendientes()` va a absorber las 24 alrededor
del 5-oct. La exclusión (d) vive sólo en la capa de medición del retador; el camino que alimenta
Telegram, dashboard y API no pasa por ahí.

## 1. Lo verificado

- **Suite pedida, corrida por el auditor:** `test_conocibilidad.py` 28 passed en 3,75 s;
  `test_autonomia.py` 9 passed; vecinos `test_parche_guardia_ancla_temporal.py`,
  `test_parche_snapshot140.py`, `test_reporte.py`, `test_api.py`: 41 passed, 4 skipped.
- **Reproducciones sobre HEAD:** de los 12 rojos de `pytest_HEAD.txt`, **7** fallan por su propia
  aserción (reproducciones legítimas: el verificador, instantes contra texto, el sello con la sesión
  abierta, el bucle de reintentos, la medición sintética, la medición real, el orden exclusión→dedup);
  los otros **5** fallan por `AttributeError`/`TypeError` (la API nueva no existe en HEAD): son tests
  de la superficie nueva, no reproducciones. Que quede dicho: 7, no 12.
- **Aislamiento:** md5 y mtime al nanosegundo de `senales.db` y `noticias.db` idénticos antes y después
  (worktree y árbol real); guardia propia `_guardia_base_temporal()` antes de cada `INSERT`; las tres
  fixtures parchean `senales.DB_PATH` y `base_medicion` además `lb.RUTA_SENALES`; los cinco tests con
  base real la abren en `mode=ro` salvo el de corte de método, que copia y compara `st_size`/`st_mtime_ns`;
  red: `motor._datos_crudos` → `pytest.fail`, `senales._ohlc_local` reemplazado; `GEMELO/cache`
  (symlink al árbol real) sin tocar (archivo más nuevo del 1-sep). Zona ciega: sin censo de red.
- **Guarda (a):** compara instantes con zona (el test usa `-04:00`); NULL e igualdad no disparan; el
  `SELECT` filtra `estado = 'pendiente'` y el `UPDATE` usa el `id` de esa consulta; `INSERT INTO
  verificacion_apertura` sólo existe en `verificar_apertura_pendientes` (aguas abajo de la guarda) y
  en dos tests; `SET estado` en cinco sitios, todos de `senales.py`. Orden de las guardas: después de
  la regla maestra y antes de `sesion_ya_cerro`, así que la fila invertida se marca el mismo día.
- **Guarda (b):** `cierre_utc` devuelve UTC con zona (1.377 de 1.377 `timestamp_utc` y `available_at`
  terminan en `+00:00`); los últimos 12 sellos reales tienen +75,1 min de holgura salvo el 28-sep
  (−137,0); regímenes del año: abr-ago +135, sep-oct +75, **nov-mar +15**, mar-abr +75; la rama del
  `except` sigue sellando; el motivo nuevo rompe el bucle de reintentos en la primera vuelta; **`main()`
  devuelve 0 en un día en que se negó a sellar: systemd ve éxito, sólo el vigía avisa.** Fallback del
  dashboard (`app.py:831-832`): se reintenta en cada rerun y recomputa el motor completo mientras la
  guarda se niegue; **el fallback deja de poder sellar con NYSE abierta**, comportamiento correcto que
  hay que decir.
- **Exclusión (d):** por regla (el test prohíbe `2026-09-28`, `28-sep`, `28 de sep` en el fuente);
  alcance exacto 24 filas, 1 fecha, 8 con verificación; `arbitro_antes.json` contra `arbitro_despues.json`
  clave por clave: `sellada`, `larga`, `doce_bloques`, `bloques_readme_en` y las ventanas §2, regla
  firmada y README con `dedup` True y False **idénticas**; sólo cambian las claves `VIVO_*` (n 409 → 402,
  gap 66,7 → 67,2 %, ventaja 12,5 → 12,9 pp, n crudo 429 → 421), ninguna publicada. Orden
  exclusión→dedup correcto (el inverso abriría sesgo de selección hacia abajo). Extender a las betas de
  `salud_r2_regimen_beta` es «toda fila», no regla nueva; `snapshots` no tiene columna `available_at`
  (verificado con `PRAGMA table_info`), así que el `regimen` del 28-sep sigue contando en §2.7,
  declarado.

## 2. Exigencias

### BLOQUEANTES (de texto: ninguna cambia el código aplicado)

**B1. No se puede escribir que la fuga quedó cerrada.** Medido hoy: `metricas_apertura(30)` n = 160, de
ellas 8 con inversión; alimentan `alertas.py:278` (Telegram), `app.py:914` y `:1583`, `api/main.py:536`
y `:823`. Texto: «La exclusión (d) rige en la capa de medición del retador (`backtest/linea_base.py`).
El camino de producción (`senales.metricas_apertura`, `senales.calibracion_intervalos`) NO la aplica:
al 29-sep-2026, 8 de las 160 filas de su ventana de 30 días son filas con `available_at >
timestamp_utc`. La cifra que muestran hoy el dashboard, la API y el reporte de Telegram las incluye.
Extender la exclusión a ese camino es una decisión separada y no está firmada.»

**B2. `verificar_puntaje_pendientes()` va a escribir las 24 filas, y hay fecha.** Su consulta filtra
`s.fecha <= date('now','-7 days')` y sólo excluye `legacy_pre_4.6`: **no aplica la regla maestra ni la
de conocibilidad**. Hoy: 0 filas del 28-sep en `verificacion_puntaje`; 24 con `puntaje_ia`. Desde el
**5-oct-2026** entran. Antes hay que decidir, y es de Nicolás: (i) la misma guarda de (a) en
`verificar_puntaje_pendientes` (que además le daría la regla maestra), o (ii) declarar por escrito que
`verificacion_puntaje` no es track record y por eso no se protege. No bloquea aplicar; bloquea cerrar
sin una de las dos frases.

**B3. El texto firmado del §90.1 (b) contiene una afirmación que la medición desmiente** («un día con la
fuente atrasada deja de sellar en vez de sellar mal»). Precisión fechada para el acta: «la condición
implementada (`available_at > ts_emision`, margen cero) protege contra sellar con la sesión del SOX
ABIERTA. No protege contra sellar con el SOX de una sesión ANTERIOR ya cerrada: ese caso pasa la guarda
y sella. Fijado en `tests/test_conocibilidad.py::test_hallazgo_una_fuente_atrasada_pasa_la_guarda_y_sella`.»

**B4. La premisa con la que el encargo justifica el §90.2 es falsa, con contraejemplo en la base.**
Garantizar `available_at <= emisión` no garantiza que la sesión siguiente a `available_at` abra después
de la emisión. `005930.KS` del 2026-07-29: `available_at` 29-jul 20:00Z, emisión 30-jul 01:23Z (la guarda
(b) pasa), y la sesión de XKRX siguiente al cierre del SOX abre el 30-jul 00:00Z, antes de la emisión.
La «puerta» que §90.2 quiere cerrar sigue abierta con (b) puesta.

### RECOMENDADAS

**R1.** Un observador independiente de la guarda (b) en el vigía: además de `av == ts`, `av > ts`
(texto exacto en el dictamen original; comparar instantes). **R2 (aplicada por el orquestador antes de
aplicar):** el barrido de husos del test estaba clavado a 2026; ahora recorre el año en curso y el
siguiente hasta donde llegue el calendario. Y que la tarjeta diga: **desde el lunes 2-nov-2026 la
holgura entre las 18:15 de Chile y el cierre de XNYS es de 15 minutos.** **R3.** El día que (b) se
niegue, el vigía de las 19:00 alerta dos fallas y la retractación de las 20:30 nunca llega (sólo se
envía con sello): una alerta sin epílogo, lo que la 5.0.1 prometió que no volvería a pasar. **R4.**
Declarar el rerun del dashboard. **R5.** Las reproducciones son 7, no 12.

## 3. H0, H2 y H3

**H0, REAL, gravedad MEDIA, cubierto por test.** No es fuga de futuro (el insumo viejo era conocible);
el daño es una predicción emitida con información de ayer, indistinguible en el sello. La defensa que
existe es `sox_fecha` sellado en la fila; nadie lo mira hoy. Tarjeta, con B3 encima del acta.

**H2, REAL, gravedad MEDIA-BAJA, más acotado de lo que parece.** Para toda bolsa cuya sesión esté
abierta al emitir, `sesion_objetivo` (anclada en `available_at`) es esa misma sesión y la regla maestra
la marca `no_verificable_timing`: el ticker contaminado es el que se cae solo. Lo que queda contaminado
y nadie filtra: la fila de `snapshots` (`regimen`, `roca_chip`) y el `puntaje_v0` de `senales_ticker`,
que viajan al reporte, al dashboard y al conteo de regímenes de §2.7; la `beta` de un ticker con sesión
cerrada cuyo par tenga barra parcial; y un sello de 24 filas todas `no_verificable_timing` (día perdido
en silencio). Esas filas no son reproducibles por un tercero: eso es lo que hay que escribir, no «usó
datos del futuro».

**H3, REAL, gravedad ALTA, el único que causa daño ahora.** B1 y B2. Y un hallazgo más:
**`verificar_puntaje_pendientes` tampoco aplica la REGLA MAESTRA** (su único filtro es
`estado != 'legacy_pre_4.6'`): `verificacion_puntaje` viene acumulando desde siempre filas que el
verificador de apertura habría descartado por timing. Excede el bloque 1 y el acta §90; tarjeta propia.

## 4. Las 33 filas del 1.4

Bajo la regla maestra, el ancla `available_at` elige en las 33 una sesión que ya estaba abierta al
emitir: serían `no_verificable_timing`, fuera de métricas y visibles. El ancla de emisión elige la
siguiente, que es la sellada (filas anteriores al parche de §84.1), hoy `verificada` y dentro de las
métricas, algunas con errores enormes (28,37, 24,15, 17,52 pp el 29-jul). Bajo §84.1 el ancla correcta
es `available_at`, y las 33 son residuo de código viejo.

**Aplicar §90.2 tal como está firmada pierde** la protección automática contra el sello tardío: cada
sello que cruza la medianoche UTC volvería a producir 7 u 8 filas verificables con la sesión objetivo
dos días después del insumo, y pares duplicados (**22 pares (ticker, sesión) repetidos sobre 7
sesiones** en `anclas_detalle.txt`), descargando en la deduplicación lo que la regla maestra resolvía
gratis. Demostrado sobre la historia. **Dejarlo como está pierde** la honestidad del campo
`sesion_objetivo` en el sello tardío: la fila se sella y el reporte de las 18:25 la publica diciendo que
anticipa una sesión que ya está abierta; sólo el verificador la degrada horas después. Y la guarda (b)
no la cierra (B4). **Lectura del auditor, para que Nicolás decida con ella:** las dos anclas atacan
síntomas distintos del sello tardío; para un track record que se defiende de sí mismo, producir filas
visiblemente inválidas es el error barato. La tercera puerta, que ninguna ancla cierra: negarse a
sellar cuando la emisión cae fuera de una ventana declarada respecto del cierre del SOX (la regla de
abstención por sello tardío, PROPUESTA en `DECISIONES.md`, sin implementar). Verificado: la única línea
nueva de `snapshot.py` es la guarda (b); el bloque del parche snapshot140 sigue anclando en
`available_at`, intacto.

## 5. Aplicación esta noche y señales tempranas

Se puede aplicar (a), (b) y (d) esta noche: las tres son más restrictivas que lo que hay, ninguna
reescribe una fila sellada, ninguna mueve una cifra publicada, y el margen de mañana es de 75 minutos
(los 15 empiezan el 2-nov). Lo que no se puede es aplicar y decir que la fuga se cerró.

- **Mañana 18:15 (sello):** `data/snapshot.log` con `'snapshot': True` y `'predicciones': 24`. Si trae
  `False` con «la sesión del SOX usada no ha cerrado», leer `sox_fecha`, `cierre_utc` y `emision_utc`;
  si la diferencia es de minutos, el problema es el margen. Que NO aparezca «la fuente no entregó datos
  — reintento»: si aparece, el motivo se coló al bucle.
- **18:25 (reporte):** sin sello debe decir «sin dato sellado hoy»; si dice una cifra, hay un camino
  que no lee del sello.
- **19:00 (vigía):** en el día bueno, silencio y «ancla temporal: 24/24 filas con cierre del SOX»; si
  dice «reloj de pared», se tomó la rama del `except` y la guarda quedó inerte. En el día malo, dos
  fallas, y la alerta no se retracta a las 20:30 (R3).
- **Comprobación de un minuto post-sello:** `SELECT fecha, count(*) FROM senales_ticker WHERE fecha =
  date('now') AND available_at > timestamp_utc` debe devolver 0.

## 6. Zonas ciegas declaradas

No corrió la suite completa (prohibido); no dictaminó los bloques 2 y 4; sin censo de red; H2 razonado,
no simulado; toda la aritmética de calendarios es la de hoy, no point-in-time; **fuga por el analista,
como siempre:** las guardas y los 28 tests los escribió alguien que ya vio el evento con sus instantes
exactos (`CENSO_INVERSION = {"filas": 24, …}` confirma un conteo conocido, no lo descubre); la única
defensa real es el sellado en vivo desde mañana. Zona ciega estructural sin cambios: `ts_emision` se
estampa antes del cómputo y nada registra cuándo la fila se hizo visible; la guarda (b) la hereda en la
dirección segura.
