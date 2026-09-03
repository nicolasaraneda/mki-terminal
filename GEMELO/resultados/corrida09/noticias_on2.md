# Frente 2c — el timeout O(n²) del job de noticias: causa raíz corregida en el código

**Fecha:** 3-sep-2026, mañana (10:13–10:30 Chile, leído de `TZ=America/Santiago date`;
relanzamiento del frente tras la desaparición del agente anterior). Corrida 09.
**Archivos tocados:** `noticias.py`, `mki_noticias.py`, `tests/test_noticias_dedup_lineal.py`
(nuevo), este informe. Ningún intocable, ninguna base real escrita (todo sobre copias en
`/tmp/mki_on2/`), ningún git que escriba, cero red, cero API. **El job de las 17:50 de hoy
corre ya con este código** — ver §6 antes que nada.

## 0. Dudas sobre la seguridad del cambio (arriba, como pide el encargo)

1. **La primera corrida con el código nuevo es la más cara y ocurre hoy a las 17:50**: sin
   marca en `meta`, TODAS las filas son candidatas y la pasada por ventanas tarda
   **615 s medidos** (n=5286, copia de la base real, con la máquina compartiendo CPU con la
   suite de tests; 4.92 M comparaciones a 125 µs). Desde la segunda corrida el costo es el
   diario (§4: 34,7 s). Si systemd matara el job durante esa primera pasada, no pasa nada
   irreversible: la migración es UNA transacción (commit al final), la base queda como
   estaba y mañana se repite la misma pasada. Con 615 s + RSS + Haiku (2–3 min) el techo de
   1800 s tiene ≥ 15 min de holgura (§6). ESTATUS: MEDIDO el dedup; NO MEDIDA la fase RSS
   aislada (no se ejecutó `actualizar_titulares`: hace fetch).
2. **Cambio de comportamiento declarado** (era el riesgo de `parche_timeout_noticias.md` §d):
   un duplicado que reaparece **más de 10 días después de su original ya no se detecta**.
   Sobre la base real de hoy, la función vieja habría borrado 31 filas; la nueva borra 20
   (exactamente las de distancia ≤ 10 d) y deja 11 (distancias 11,9 – 138 d; §4). Esas 11
   filas son republicaciones de notas viejas con `fecha` vieja: entran dos veces al análisis
   Haiku (≈ 0,0005 USD cada una) y al sentimiento, donde el decaimiento 0,7^días con piso
   0,1 ya las pesa poco. Ampliar la ventana es cambiar una constante
   (`VENTANA_DEDUP_RETRO_DIAS`), pero la primera pasada escala con ella (§5).
3. **`meta` es una tabla nueva en `noticias.db`**: creada con `CREATE TABLE IF NOT EXISTS`
   en `init_db()` y en la propia migración; no altera ninguna tabla existente. Dos claves:
   `dedup_retro_ultimo_id` (marca, nunca retrocede) y `dedup_retro_corrido_en` (auditoría).
   Verificado con un test que arma una base "4.6" sin `meta` y comprueba que las columnas de
   las otras tablas no cambian.
4. **Los tests que tocan noticias no rompen**: 302 passed en los 17 archivos (§5).

## 1. Causa raíz (MEDIDO, acta §73 y parche §b, reproducido hoy sobre copia)

`noticias.actualizar_titulares()` llama a `migrar_noticias_v2()` en cada corrida, y esa
función comparaba cada titular contra TODOS los supervivientes anteriores del historial
completo con `difflib.SequenceMatcher` (umbral `UMBRAL_SIMILITUD_DUP = 0.85`): O(n²) con
n = filas totales. Reproducción de hoy sobre copia (`/tmp/mki_on2/noticias_vieja.db`,
`medir_vieja.py`, contador sobre `SequenceMatcher`):

| Versión vieja (completa) | valor |
|---|---|
| n (filas de `titulares`) | 5286 |
| comparaciones `SequenceMatcher` | 13 845 857 |
| tiempo | **2233,0 s** (37 min; el parche midió 1803,7 s el 2-sep con la máquina ociosa — hoy compartía CPU con la medición nueva y la suite) |
| duplicados borrados | 31 (ids 3307, 6142, 6166–6181, 6233–6236, 6279–6308, 6334–6339) |
| µs por comparación | 161 (hoy, máquina cargada) / 130 (parche, 2-sep) |

El log del 1-sep confirma la cronología: inicio 21:50:01 UTC, «titulares nuevos guardados:
223» a las 22:17:44 (27 min 43 s de migración + RSS), kill a los 1800 s durante Haiku. El
2-sep: inicio 21:50:00 UTC y ninguna línea más — murió dentro de la migración
(7,16e-5 × 5286² = 2000 s > 1800). Hoy la base tiene las mismas 5286 filas del 2-sep.

## 2. Diseño elegido y por qué (PROPUESTA, implementada)

Opción **(b)+(c) combinadas, con ventana de (a)**: una marca en la tabla `meta`
(`dedup_retro_ultimo_id`) recuerda hasta qué `id` se procesó; sólo las filas con `id` mayor
son candidatas; cada candidata se compara sólo con las filas cuya `fecha` cae dentro de
±`VENTANA_DEDUP_RETRO_DIAS = 10` días de la suya. Sin marca (primera corrida) todas las
filas son candidatas: una pasada completa por ventanas, lineal en n, sin asumir nada sobre
migraciones anteriores.

- Por qué no (a) sola (ventana temporal respecto de "ahora"): se midió y **falla**. Las 223
  filas que insertó el job del 1-sep tienen `fecha` de publicación entre el 11-may y el
  1-sep (Google News devuelve notas viejas). Una primera versión con candidatas =
  `fecha ≥ ahora − 10 d` encontró **1** duplicado de los 20 alcanzables: los otros 19 son
  filas nuevas con `fecha` vieja, invisibles para un filtro por fecha. La candidatura tiene
  que ser por `id` (orden de inserción); la ventana es sólo para elegir CONTRA qué comparar.
  Error propio, corregido antes de medir de nuevo (§8d).
- Por qué no (c) sola (migración completa una vez): esa "una vez" sería hoy a las 17:50 y
  dura 30–37 min: moriría a los 1800 s, sin commit, y se repetiría cada día. La primera
  pasada tiene que ser lineal también.
- «El más antiguo sobrevive» en las DOS direcciones, como la función vieja: paso (1) la
  candidata se compara con las anteriores vivas de su ventana (si hay una, la candidata es la
  réplica); paso (2) con las POSTERIORES ya procesadas de su ventana (una candidata con
  `fecha` más antigua desplaza a la réplica posterior y borra su análisis). El caso existe en
  la base real: el id 3307 (viejo) es réplica de la fila nueva 6294, 0,47 d más antigua por
  `fecha`; la vieja y la nueva lo borran las dos.
- Orden de recorrido y desempate idénticos a la vieja (`ORDER BY fecha ASC, id ASC`);
  titulares normalizados vacíos ni se comparan ni cuentan como vistos, como antes.
- **El retag (`tickers_estrictos`) sigue global**: O(n) y **0,13 s con n=5286** (MEDIDO);
  `es_titular_relevante` sobre toda la tabla, 0,013 s. No hacía falta restringirlos.
- `_desplazar_fecha_iso` parsea la `fecha` ISO que escribe `_fecha_entrada`; las 5286 filas
  tienen el mismo formato `AAAA-MM-DDTHH:MM:SS+00:00` (MEDIDO). Si alguna no parseara, la
  ventana de esa fila sería nula (se compara sólo contra su misma marca de tiempo), nunca una
  excepción.
- Esquema: aditivo e idempotente (`_asegurar_tabla_meta`, llamada desde `init_db()` y desde
  la migración). Nada de `ALTER TABLE`.
- `mki_noticias.py`: llama a `migrar_noticias_v2()` ANTES del RSS y escribe en el log
  «dedup retroactivo: {...} en X s» — desde hoy la duración de esta fase queda medida en
  `data/noticias.log`. `actualizar_titulares()` la vuelve a llamar (sin cambios en su
  interfaz): la segunda pasada no tiene candidatas y cuesta 0 comparaciones, 0,15 s.

## 3. Qué cambia de comportamiento (DECLARADO)

| Caso | Vieja (completa) | Nueva (incremental por ventana) |
|---|---|---|
| Réplica ≤ 10 d después del original | borra la réplica y su análisis | igual |
| Réplica insertada después pero con `fecha` más antigua | conserva la más antigua, borra la otra | igual (paso 2) |
| Réplica **> 10 d** después del original | borra la réplica | **no la detecta** (queda; entra al análisis) |
| Cadenas A~B~C con A–C fuera de ventana | depende del orden | puede diferir; en la base real de hoy no ocurre: nueva ⊆ vieja exactamente |
| Costo por corrida | ~7,16e-5·n² s, crece sin techo | ≈ candidatas × filas en ±10 d: no depende de n |

## 4. Medición antes / después (MEDIDO, copias de `noticias.db` en `/tmp/mki_on2/`, sin red ni API)

| | n | candidatas | comparaciones | segundos | borrados |
|---|---|---|---|---|---|
| Vieja, completa | 5286 | 5286 | 13 845 857 | **2233,0** | 31 |
| Nueva, **primera corrida** (sin marca — lo que corre hoy 17:50) | 5286 | 5286 | 4 921 843 | **615,1** | 20 |
| Nueva, **corrida diaria** (marca en 6116: candidatas = las 223 filas que insertó el job del 1-sep) | 5286 | 223 | 282 354 | **34,7** | 20 |
| Nueva, segunda pasada inmediata (idempotencia) | 5266 | 0 | 0 | 0,15 | 0 |

Equivalencia sobre la base real: los 20 ids que borra la nueva (3307, 6169–6173, 6175–6177,
6179–6181, 6236, 6283, 6285, 6306–6308, 6338, 6339) son un subconjunto de los 31 de la
vieja; los 11 restantes (6142, 6166, 6167, 6233, 6235, 6279, 6282, 6286, 6295, 6301, 6334)
tienen su original a 34,4 / 22,0 / 62,0 / 61,0 / 84,0 / 14,1 / 96,5 / 60,0 / 11,9 / 22,5 /
138,0 días de distancia — todos fuera de la ventana, ninguno dentro. Con ventana de 30 d se
recuperarían 3 de los 11 (14,1; 22,0; 22,5 d), a ~3× el costo.

Escala esperada desde mañana (PROPUESTA a partir de lo medido): ~200 candidatas/día ×
~1400 filas en ±10 d ≈ 280 k comparaciones ≈ 35 s, constante mientras el ritmo diario de
titulares lo sea; si el ritmo diario se duplica, el costo diario se cuadruplica (es
cuadrático en el ritmo, lineal en nada más), pero no en el historial.

## 5. Tests (`tests/test_noticias_dedup_lineal.py`, 7 tests, 1,8 s)

1. `test_comparaciones_por_corrida_no_crecen_con_el_historial`: base sintética (20
   titulares/día, `SequenceMatcher` reemplazado por un contador), N=400 y 2N=800 filas de
   historial + 20 nuevas. Corrida diaria: **3850 comparaciones en los dos casos** (idénticas,
   ≤ 20 × 220). Primera corrida: 59 900 → 139 900 (lineal: cada fila extra ≤ una ventana;
   2N < 2,5× N). Referencia vieja, reimplementada verbatim en el test: 87 990 → 335 790
   (≈ 3,8×, cuadrática). Cifras verificadas corriendo el cuerpo del test aparte.
2. `test_equivalencia_dentro_de_la_ventana_y_caso_declarado`: réplicas sembradas dentro
   (A, 2 d), fuera (C, 18 d) y con fecha invertida (D); `nueva ⊆ vieja`, `{A, D} ⊆ nueva`,
   `vieja − nueva == {C}` — el caso declarado, con su justificación en el test.
3. `test_candidata_mas_antigua_desplaza_a_replica_ya_procesada`: paso (2) tras la marca,
   con borrado del análisis de la réplica.
4. `test_se_borra_el_analisis_de_la_replica_y_queda_el_del_original`.
5. `test_idempotente_y_marca_en_meta`: segunda corrida = 0 candidatas, 0 comparaciones,
   0 borrados, mismas filas; marca = id máximo visto.
6. `test_esquema_meta_es_aditivo_e_idempotente`: base "4.6" sin `meta` → `init_db()` dos
   veces + migración; aparece `meta`, las otras tablas conservan sus columnas.
7. `test_actualizar_titulares_sigue_pasando_por_la_migracion` (lee el código, sin red).

Un error de diseño del test, corregido: el primer vocabulario sintético (`palabraNNN`)
generaba duplicados accidentales en cadena (difflib ve parecidos los prefijos comunes) y
hacía que la nueva borrara filas que la vieja no; con vocabulario de letras al azar la
equivalencia es exacta. Registrado en el propio test.

Suite: `python -m pytest tests/test_noticias_dedup_lineal.py $(grep -l noticias tests/*.py)`
→ **302 passed, 20 warnings, 239,5 s** (17 archivos: el nuevo + test_api, test_autonomia,
test_backtest, test_condicional, test_control_lineal, test_fuente_canonica,
test_gemelo_datos, test_importador_roundtrip, test_insumos, test_parche_snapshot140,
test_replica, test_reporte, test_restaurar_backup, test_secuencial_07, test_sombra,
test_vigia). `python -c "import noticias, mki_noticias"` importa. El job NO se ejecutó.

## 6. Nota para `espera_firma` — el parche del timer queda innecesario (PROPUESTA)

Con esta corrección, el presupuesto de la corrida de hoy (17:50) es: primera pasada del
dedup ≤ 615 s (MEDIDO, cota alta: máquina cargada) + fase RSS (NO MEDIDA aislada; el ajuste
cuadrático del parche la absorbe dentro de ±3 % de ~1500 s, es decir ≲ 1–2 min) + Haiku
2–3 min (histórico, parche §b) ≈ **13–15 min < 30 min**. Desde mañana: ~35 s + RSS + Haiku
≈ **5–6 min**, constante en el historial. **`TimeoutStartSec=1800` alcanza; el parche a
2700 s de `GEMELO/resultados/parche_timeout_noticias.md` §e ya no hace falta y no debería
aplicarse** — subir el techo escondería una regresión futura de esta misma fase. La
confirmación es empírica y llega esta tarde: la línea nueva «dedup retroactivo: {...} en
X s» en `data/noticias.log` y la línea «titulares nuevos guardados» a menos de 15 min del
inicio. Si no aparece, la causa NO es esta función (queda medida en el log) y hay que
mirar RSS/Haiku.

Decisión que sí es de Nicolás: la ventana (10 d, la misma del dedup de inserción). Subirla a
30 d multiplica el costo diario por ~3 (≈ 100 s) y recupera hoy 3 de las 11 réplicas
perdidas; una vez puesta la marca, cambiar la constante sólo afecta a las corridas diarias.

## 7. Estatus de cada afirmación

MEDIDO: todo §1, §4, §5, el retag 0,13 s, el formato único de `fecha`, los 20/31 ids y sus
distancias. PROPUESTA: el diseño (§2), la escala futura (§4 último párrafo), §6.
NO EVALUABLE hasta la corrida de hoy: la duración real de la fase RSS y el wall clock total.

## 8. Cierre del preámbulo

(a) **Creados:** `tests/test_noticias_dedup_lineal.py`, `GEMELO/resultados/corrida09/noticias_on2.md`.
**Modificados:** `noticias.py` (`init_db` crea `meta`; `_asegurar_tabla_meta`/`_leer_meta`/
`_escribir_meta`; `VENTANA_DEDUP_RETRO_DIAS`; `_desplazar_fecha_iso`;
`_deduplicar_retro_incremental`; `migrar_noticias_v2` reescrita — misma firma, dict con más
claves; import de `timedelta`), `mki_noticias.py` (llamada medida y logueada a
`migrar_noticias_v2()` antes del RSS). Temporales en `/tmp/mki_on2/` (copias de la base,
`medir_vieja.py`, `medir_nueva.py`, JSON de resultados), fuera del repo.
(b) **Intentos del DSR: 0** (ninguna hipótesis sobre retornos).
(c) **Abierto:** confirmar esta tarde con el log la duración real; decidir la ventana (10 vs
30 d); retirar formalmente el parche del timer del expediente anterior; el `.diff` de
`parche_timeout_noticias.md` §e queda sin aplicar y debería marcarse como superado.
(d) **Errores propios corregidos:** (i) primera versión con candidatas por `fecha ≥ ahora −
10 d` — detectaba 1 de 20 porque las filas nuevas traen `fecha` vieja; se pasó a candidatura
por `id` (§2); (ii) la marca podía retroceder cuando el id máximo era un borrado — ahora
`max(máx id, marca anterior)`; (iii) vocabulario sintético con prefijo común que fabricaba
duplicados accidentales en el test (§5); (iv) un intento de aplicar la edición por `bash
heredoc` fue bloqueado por el hook de reglas (contenía `DELETE`/`UPDATE` sobre `titulares`,
que ya existían en la función vieja) — se editó con la herramienta de edición, no se rodeó el
hook; (v) la primera medición de la nueva se lanzó en primer plano y murió al límite de 2
min de la herramienta: se relanzó en segundo plano.
