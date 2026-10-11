# Auditoría de fuga del `auditor-lookahead` sobre el camino T de §62 rebasado sobre el sellador de la 16b (corrida 16-2)

> Archivado por el orquestador tal como lo devolvió el agente (texto íntegro, sin recortes). Lanzado a las 15:27 de
> Chile del 11-oct-2026 sobre el worktree `wt162` (HEAD `c271822` + `camino_T_16_2.v1.diff`); devuelto a las **15:40:44**
> (hora de `date` del agente). Sus sondas están copiadas en `evidencia/sondas_auditor/`. Nada escrito en el proyecto.
> **Nota del orquestador:** el dictamen es sobre la etapa 1 (`dinero/sello_dinero.py` en `4b494966…`); el auditor midió
> que B2 entró al mismo worktree a las 15:30:41 mientras leía y que el único cambio fue dentro de `estado()`. Sus R1 y R2
> se plegaron al parche final (`camino_T_16_2.diff`, sellador en `610f5b05…` con sólo el camino T; `299a7627…` con los
> tres parches) a las 15:47; el addendum sobre B2 y sobre ese plegado va al final de este archivo.

---

# AUDITORÍA DE FUGA — camino T de §62 (§93.7, §99.2) rebasado sobre el sellador de la 16b, worktree `wt162`

**APLICABLE CON EXIGENCIAS** (2 bloqueantes de registro/secuencia, 5 recomendadas). El mecanismo hace lo que dice: ninguna ruta escribe en `sellos_dinero` con `timing_ok` falso, ninguna escribe ni reescribe un `ext_<fecha>.csv` canónico con timing roto, `--sin-red` no puede levantar un `.no_verificable.csv`, la tabla nueva tiene los dos disparadores, `init_db` es todo `IF NOT EXISTS`, y los cinco chequeos de integridad permanente pasan contra la base REAL en `mode=ro` con el módulo parcheado. Lo bloqueante no es el código: es que **el camino T cubre sólo una de las dos formas del disparo de recuperación**, y §99.2 eligió (a) descartando (b) y (c) sobre la premisa de que lo cubre.

Hora de `date` al abrir: **Sun Oct 11 15:27:33 -03 2026**.

---

## Artefacto auditado (y un movimiento que hay que declarar)

Leí `dinero/sello_dinero.py` del worktree con sha256 `4b4949667fb7c0d4b24016b8b32489761bacd09a6f0f439d24c493e993178414`. **A las 15:30:41 el archivo cambió bajo mi lectura** (sha pasó a `5b1641949eeb6ca855a12573524c57bf0265d3153f68ef2e4c94cedee3fdfcf7`) porque la etapa 2 (B2) se aplicó en el MISMO worktree; a las 15:31:40 aparecieron `b2_contrato_16_2.v1.diff`, `b2_api_16_2.v1.diff` y `cumulativo_16_2.v1.diff` en el scratchpad, y `git status` del worktree pasó a 8 archivos (`api/CONTRATO.md`, `api/main.py`, `frontend/src/lib/tipos.ts`, `tests/test_b2_intentos_visibles_16_2.py`).

Reconstruí la etapa 1 aplicando `camino_T_16_2.v1.diff` sobre `HEAD:dinero/sello_dinero.py`: da exactamente `4b494966…`, lo que leí. El diff etapa1 → worktree actual es **un solo bloque, íntegro dentro de `estado()`**: la clave `ultimo_intento` y su `SELECT … FROM intentos_no_verificables ORDER BY id DESC LIMIT 1` en el mismo `try/except OperationalError`. Nada en `congelar_extension`, `sellar`, `decidir`, `init_db`, `evaluar_timing`, `exportar_csv`, `respaldar_extension` ni `main`. Todas mis sondas corrieron después de las 15:30:41, así que ejercitaron un camino de sellado **byte a byte idéntico al de la etapa 1**. Mi dictamen es sobre `4b494966…`; **B2 no lo audité** (sale de mi alcance y va en sus propios diffs).

Prohibiciones respetadas, medidas al cerrar: `sha256(dinero/sello_dinero.py)` del árbol real = `cd0e70c8005143b2f6b63c62fb9e3f75b5303e083a936c98c13b86df6a8b2c25` = HEAD, sin cambio; `sha256(dinero/sello_dinero.db)` = `2a016c52…` idéntico al que leí a las 15:31:49; `find` de archivos más nuevos que las 15:27 en `dinero/` y `data/backups/` del árbol real: **vacío**; el inventario de `dinero/datos/sello/` byte a byte igual (`diff` IDÉNTICO); nunca `--sellar`; la base real se abrió sólo con `mode=ro` (jamás `conectar(solo_lectura=False)`, que habría creado la tabla nueva); ningún `git commit/push/reset`; ningún timer. Mis sondas viven en `.../scratchpad/probe_auditor/` y escribieron sólo en `tempfile.mkdtemp()`.

---

## Lo verificado

**Suite, con hora.** `Sun Oct 11 15:32:07` → `15:32:29 -03`, desde el worktree:
`venv/bin/python -m pytest tests/test_camino_T_16_2.py tests/test_sello_dinero.py tests/test_toely_fuera_insumo_e0.py -q -p no:cacheprovider -m "not red"` →
```
56 passed, 10 skipped in 21.46s
```
Coincide con tu cifra. **Los 10 saltados, con su razón literal (`-rs`), son todos por base/evidencia ausente:** 5× `test_sello_dinero.py:623` «sin base real en …/wt162/dinero/sello_dinero.db», 1× `:652`, 1× `:733`, 1× `:308` «todavía no hay extensión congelada», 1× `test_camino_T_16_2.py:260`, 1× `test_toely_fuera_insumo_e0.py:173`. **Esto importa: los cuatro tests de integridad permanente, que en la corrida 15 fueron pata central del dictamen, NO corrieron hoy** (§95.5: la copia de bases fue denegada). Los corrí a mano (abajo).

**Integridad permanente contra la base REAL, `mode=ro`, módulo parcheado** (sonda `p1_integridad_real.py`; `RUTA_DB`/`DIR_EXT`/`DIR_BACKUP_EXT` apuntados al árbol real):
```
filas de intentos: ('AUSENTE', 'no such table: intentos_no_verificables')
fechas en sellos_dinero: 22
A. integridad en DIR_EXT       : SIN FALLAS
B. integridad en DIR_BACKUP_EXT: SIN FALLAS
C. clase de evidencia (5.2)    : SIN FALLAS
rotas en la principal: [('2026-09-28','no_verificable_timing','roto','E0.2'), ('2026-10-07','no_verificable_timing','roto','E0.2')]
D. regla del corte (<E0.3)     : SIN FALLAS
E. congelado grande citado     : SIN FALLAS
```

**Tus hechos de la base real, reverificados uno por uno** (`mode=ro`, 15:32): 22 fechas ✓, 722 filas, cuentan para N **12** ✓, 3 divergencias (9-sep `decisiones_distintas`=1, 28-sep=0, 7-oct=0) ✓, 28-sep 33 filas `ts` `2026-09-28T17:43:01.001389Z` `available_at` `2026-09-28T20:00Z` sellador `480fbdc9` reglas `125a8602` ✓, 7-oct 32 filas `ts` `2026-10-07T13:31:04.897105Z` `available_at` `2026-10-07T20:00Z` apertura `2026-10-08T13:30Z` sellador `cd0e70c8` reglas `b6080eee` ✓, las dos `version_sello = E0.2` ✓, `intentos_no_verificables` ausente ✓. `sellos_dinero` tiene **36 columnas = id + las 35 de `_ddl_filas`**, paridad exacta hoy. La unidad instalada: `OnCalendar=Mon..Fri 23:30 America/New_York`, `Persistent=true`, `AccuracySec=1s`, `Type=oneshot`, sin `RemainAfterExit` ✓. **Una corrección a tu enunciado:** no hay 3 divergencias «y» 2 rotas como poblaciones disjuntas — el 28-sep y el 7-oct aparecen en las dos, que es justamente el modo de falla (la fecha quedó ocupada y el disparo bueno entró por divergencia).

**El disco real confirma el mecanismo:** `ext_2026-10-07.csv` tiene mtime `2026-10-07 10:31:03` y 14471 bytes — la matriz intradía de las 09:31 NY, que las 32 filas selladas citan; no existe `ext_2026-10-06.*`. Con camino T ese archivo habría nacido `ext_2026-10-07.no_verificable.csv` y el cupo canónico habría quedado libre.

**Rojo en HEAD por conducta, no por firma** (tu `pytest_nuevos_sobre_HEAD.txt`, releído): 4 failed, 1 passed, 1 skipped; el que pasa es el (iv), declarado control en su propio docstring; los fallos son aserciones (`'sellada' == 'intento_no_verificable'`), no `TypeError` — el shim `_congelar` cumple su función.

**Causalidad y pureza de lo que E0.3 agrega** (sonda `p9_causalidad.py`):
- Todo `ultimo_cierre` de la disponibilidad es ≤ `fecha_insumo` en los tres cortes probados (5/6/7 sesiones), con SHECY rezagado una sesión como en el caso real: `avail` es **backward-only por construcción**.
- `evaluar_timing` es pura (dos llamadas idénticas) y `avail` nunca es el reloj de pared (`2026-09-14T20:00:00+00:00` ≠ `2026-09-14T17:43:01+00:00`).
- **Prueba maestra sobre el instante que decide tabla y nombre:** con la extensión de 5, 6 y 7 sesiones recortada en la misma fecha, `evaluar_timing` da el mismo dict (`timing_ok=False`, `avail=2026-09-14T20:00:00+00:00`) → **el veredicto de una fecha es invariante a que existan o no las sesiones posteriores**.
- Gate de invariancia con el `cfg` de la 16b bajo E0.3: `[{'INVARIANTE','2026-09-15',cortes 2},{'INVARIANTE','2026-09-09',cortes 6}]` y `INVARIANTE` con 3 y 2 cortes en dos días más. `exclusiones_insumo_e0.tickers == ['TOELY']` leído de `reglas.json`.

**Seis escenarios de timing roto en runtime** (sonda `p3_varios.py`, P4): `intento_no_verificable` / `ya_intentada` / `divergencia_registrada` / `intento_no_verificable` / `divergencia_registrada` / `intento_no_verificable`; **`rotas_en_principal = 0` en los seis**, y en los seis la lista de canónicos en `DIR_EXT` está vacía salvo el que había dejado un sello bueno anterior.

**`--sin-red`** (P6): con un canónico viejo nunca sellado → `rechazado_evidencia_canonica`, 0 filas, 1 fila en `divergencias_sello` (B1 de la corrida 15, funcionando). Con sólo el par `.no_verificable` en la carpeta, `ultima_extension()` devuelve **`None`** → `--sin-red` se niega con código 2; no hay forma de levantarlo como insumo.

---

## Fugas demostradas

**F1 — la zona ciega de la corrida 15, medida: la carrera rompe la integridad permanente, de forma IDÉNTICA en E0.2 y en E0.3. Preexistente, no nueva.** Sonda `p2_concurrencia.py`, corrida sobre `wt162` y sobre `wt162_head`:

| | E0.3 (parcheado) | E0.2 (HEAD puro) |
|---|---|---|
| A congela | `ext_2026-09-14.no_verificable.csv`, sha `684857bf` | `ext_2026-09-14.csv`, sha `684857bf` |
| B congela | **el mismo path**, sha `b221ed43` (pisa a A) | **el mismo path**, sha `b221ed43` (pisa a A) |
| A sella | `intento_no_verificable`, 32 filas citando `684857bf` | `sellada`, 32 filas citando `684857bf` |
| B sella | `divergencia_registrada`, 0 filas | `divergencia_registrada`, 0 filas |
| disco vs cita | `b221ed43` vs `684857bf` → **ROTA** | `b221ed43` vs `684857bf` → **ROTA** |

Y es peor que una cita huérfana: **las filas de A llevan los precios de B.** `sellar` hace `insumo(ruta_ext)`, que lee el CSV del disco, no el DataFrame que A descargó. Medido (`p2b_precios.py`): cierre congelado AMD 477.570007; A descargó ×0.98 = 468.018607; B ×0.97 = 463.242907; **la fila de A dice 463.242907**. El contenido de la fila y el sha que cita vienen de dos descargas distintas, y las filas son inmutables: el rojo del test de integridad sería permanente e irreparable.

**Mecanismo exacto:** entre `intento_previo`/`sello_previo` (en `congelar_extension`, líneas 451 y 467) y `_cita_en` (en `sellar`, 776/784) no hay atomicidad ni lock de archivo; el `open(ruta,"wb")` de la línea 478 pisa sin preguntar.
**Cómo reproducirlo:** `WT=<worktree> venv/bin/python probe_auditor/p2_concurrencia.py`.
**Clasificación: zona ciega aceptada, no bloqueante.** La unidad es `Type=oneshot`, timer único, sin `RemainAfterExit`: systemd no arranca una segunda instancia de la misma unidad mientras la primera está activa (un disparo de recuperación por boot y el `OnCalendar` siguiente son secuenciales; el sellado real tarda ~1–2 s, medido como delta entre el mtime de la extensión a las 00:30:03 y el `timestamp_utc` a las 03:30:04/05Z). **La única vía viva es un `--sellar` a mano en paralelo, que §99.7 prohíbe a los agentes y deja en la mano de Nicolás.** Camino T no la crea ni la agrava; al contrario, la amortigua: el rojo cae en una tabla que no cuenta para nada y `ext_<fecha>.csv` queda libre para el sello bueno, mientras en E0.2 la sesión queda corrompida **y** quemada.

**F2 — una fila de intento puede contradecirse a sí misma.** Sonda `p3_varios.py`, P3: congelar a las `19:59:55Z` (antes del cierre nominal `20:00:00Z` → `timing_ok` False, evidencia `.no_verificable`), sellar a las `20:00:05Z` (`evaluar_timing` da True). La clase de la evidencia endurece correctamente (`intento_no_verificable`), pero la fila que queda es:
```
available_at 2026-09-14T20:00:00+00:00 | timestamp_utc 2026-09-14T20:00:05+00:00
apertura_objetivo_utc 2026-09-15T13:30:00+00:00 | estado no_verificable_timing | estado_timing roto
regla maestra leída de la PROPIA fila: True   <- la fila se contradice
```
Un tercero que aplique la regla maestra a las tres columnas de la fila concluye que **debió ser verificable**. La explicación vive sólo en el bloque `timing` del meta `.no_verificable` (que registra `emision_utc = 19:59:55`, el reloj de congelar, no el de la fila). El par fila+meta sí explica; la fila sola, no. **Ventana de alcance:** `avail` tiene que caer entre los dos relojes, o sea ~1–2 s alrededor de las 20:00:00Z (EDT) / 21:00:00Z (EST): inalcanzable para el timer de las 23:30 NY, alcanzable para un boot de recuperación a las 15:59:59 NY. Recomendada, no bloqueante (la fila está fuera de toda métrica). Es la `duda 2` del implementador, ahora medida.

**F3 — `sellar` inserta filas que citan un archivo que `main()` borra. Preexistente, idéntica en E0.2 y E0.3.** Sonda `p10_juego.py`, en los dos worktrees: con `juego_activo` cambiado entre dos disparos de la misma `fecha_insumo` y otro insumo, `congelar_extension` manda el insumo al temporal (`persistido: False`, correcto por E4-bis), pero `previas` filtra por juego y queda vacío, así que `sellar` **inserta 32 filas en `sellos_dinero`** citando `ext_2026-09-14_divergente_…csv`, que `main()` borra:
```
juego conservador cita ext_2026-09-14.csv                 -> existe, sha OK
juego agresivo    cita ext_2026-09-14_divergente_….csv    -> *** EL ARCHIVO NO EXISTE: integridad ROTA ***
```
Recorrí todas las ramas: **el único camino donde `sellar` inserta con `persistido is False` es éste** (en las otras dos — fecha ya sellada mismo juego, e intento previo — sale por divergencia con 0 filas). Lo nombro acá porque camino T es el parche que convierte «el sha citado tiene que existir mañana» en invariante de DOS tablas, y una guarda de una línea lo cierra para siempre. Alcanzable sólo si una mano cambia `juego_activo` entre dos disparos del mismo día.

**F4 — el «una definición, no dos que puedan divergir» de `_ddl_filas` sólo vale para bases nacidas en E0.3.** `CREATE TABLE IF NOT EXISTS` sobre una tabla existente es un no-op: no agrega columnas. Sonda `p3_varios.py`, P7: fabriqué una `sellos_dinero` a la que le falta una columna, corrí `init_db`, y quedó `sellos=35 intentos=36` — **divergieron en silencio** (`{'insumo_completo'}`). Hoy es inocuo (medí paridad exacta en la base real: 36 = id + 35). Pero `test_la_tabla_de_intentos_tiene_las_mismas_columnas_que_la_principal` usa `S.conectar(entorno_temporal)`, una base **fresca de tmp** (línea 985): por construcción no puede ver una divergencia en la base real. El día que `_ddl_filas` gane una columna —y F2 pide justamente una— `sellos_dinero` de la base real no la recibe, el `INSERT INTO {tabla}` es compartido y lista explícita, y el sellado revienta o se parte según la tabla. No hay `_asegurar_columnas` en este módulo.

---

## Exigencias

### Bloqueantes

**B1. El acta que aplique tiene que declarar qué forma del disparo de recuperación cubre T y cuál no.** Medido (P5, abajo y en la pregunta 2): camino T salva los disparos de recuperación cuyo timing sale **roto** (el 7-oct: barra intradía con `available_at` futuro). **No salva los que salen con timing OK en un día sin sesión:** una recuperación el sábado con el cierre completo del viernes sella en `sellos_dinero` como `dia_sin_sesion`, `cuenta_para_N = 0`, y **ocupa la fecha del viernes para siempre**, exactamente igual que E0.2. §99.2 eligió (a) y descartó (b) `Persistent=false` y (c) las dos, con la razón «puesto que este ya habria salvado el 7 oct» — es cierto para la forma del 7-oct y **falso para la forma de fin de semana y de feriado entre semana**, que es la otra mitad de lo que `Persistent=true` produce. El acta no puede escribir «el camino T resuelve los disparos de recuperación» a secas; tiene que escribir las dos formas, cuál queda abierta, y que reabrirla (o volver sobre (b)/(c)) es acto posterior de Nicolás. Esto no pide una línea de código: pide no sobredeclarar cobertura, que es la misma disciplina del texto B3 de §93.7.

**B2. Camino T y B2 se aplican en la MISMA noche, o B2 primero; nunca camino T solo.** `camino_T_16_2.v1.diff` **no** incluye `ultimo_intento`: lo agrega la etapa 2, y lo agrega **dentro de `dinero/sello_dinero.py`**, así que consume el mismo presupuesto de «un cambio por noche al sellador» (§87 pre-mortem 3). Si se aplica camino T solo, queda en pie íntegra la F1 de mi dictamen de la corrida 15: una noche quemada se ve idéntica a un sábado — `sesiones_selladas` no se mueve, `ultimo` es el de anoche, y la API no sirve la clave nueva. Mi B2 de la corrida 15 sigue abierta hasta que `b2_contrato_16_2.diff` + `b2_api_16_2.diff` entren con el resto (y `api/CONTRATO.md` se enmienda antes, como dije entonces). Repito de la corrida 15, porque hoy vale igual: **aplicar el diff una noche y su exigencia la siguiente es la peor combinación.**

### Recomendadas

**R1. `sellar` se niega a insertar cuando `meta_ext.get("persistido") is False`** (cierra F3). Una línea antes de elegir tabla; ninguna rama legítima la pisa (lo recorrí: las otras dos salen por divergencia con 0 filas).

**R2. La paridad de columnas entre las dos tablas se verifica sobre la base REAL, no sobre una fresca** (cierra F4): mover la aserción de `test_la_tabla_de_intentos_tiene_las_mismas_columnas_que_la_principal` a la sección 4, donde empieza a correr en cuanto el sellador cree la tabla, con el `pytest.skip` declarado de R2 de la corrida 15. Y escribir en el encabezado de `_ddl_filas` que **agregar una columna ahí exige una migración aparte**, porque `IF NOT EXISTS` no la propaga a la tabla que ya existe.

**R3. La fila de intento tiene que poder explicarse sola** (cierra F2): el camino barato sin tocar el esquema es que el `motivo` de las filas de un intento, o una columna nueva `congelado_en_utc` (con la migración de R2 a la vista), diga el instante con el que se decidió el timing. Hoy una fila de `intentos_no_verificables` puede satisfacer la regla maestra en sus propias tres columnas y decir `estado_timing = roto`.

**R4. R1 de la corrida 15 sigue sin hacer:** un `ext_F.no_verificable.csv` congelado cuyo `sellar` nunca llegó (proceso muerto, red caída, gate que aborta) queda huérfano en `DIR_EXT`, citado por nadie e indistinguible del caso bueno. `main()` no lo declara. Integridad en la dirección archivos → filas, o una línea en `main()`.

**R5. Un lock de archivo en `DIR_EXT` entre congelar y sellar** (amortigua F1). No la hago bloqueante porque systemd no produce la concurrencia; la dejo escrita porque el único vector vivo es un `--sellar` a mano, y la receta de aplicación va a pedir uno.

**Cosmético, sin número:** la consulta `previas` de `sellar` (línea 762) dice `FROM sellos_dinero` literal mientras el resto del módulo usa `TABLA_SELLOS`.

---

## Las cuatro decisiones del implementador, releídas

**(i) Rechazo de evidencia canónica con timing roto.** Correcta y ahora completa. Medí la rama con `--sin-red` sobre un canónico viejo nunca sellado (P6): `rechazado_evidencia_canonica`, 0 filas en las dos tablas, **1 fila en `divergencias_sello`**, archivo intacto. B1 de la corrida 15 está plegado y funciona. Nota de alcance: esa rama es también el caso que vuelve a E0.3 estrictamente mejor que E0.2 en `--sin-red`, donde E0.2 habría sellado 32 filas rotas ocupando una fecha vieja.

**(ii) `ya_intentada` con el mismo sha.** Correcta (R4 de la corrida 15, plegada). Medida en P4 caso 2: `ya_intentada`, 0 filas, sin fila en `divergencias_sello`. Es lo que protege el único contador que la API sirve como alarma del modo de falla medido en §63 (re-disparo en el mismo minuto roto con el mismo insumo).

**(iii) Dos relojes en `main()`.** Sigo sosteniendo que es la decisión correcta y por una razón de fuga: unificarlos sellaría `timestamp_utc` con una hora anterior a la emisión real. Hoy agrego lo que en la corrida 15 era juicio por lectura y ahora está medido: la discordancia inversa produce **una fila que se contradice** (F2), y R5 de la corrida 15 —`main()` imprime `congelado_en_utc`, `timestamp_utc` y `delta_s` en toda rama, líneas 975-980— deja el cruce en el log pero **no en la fila sellada**, que es donde un tercero lo busca. De ahí R3.

**(iv) `VERSION_SELLO = E0.3`.** Correcto como corte de método y verificable sin memoria de nadie: `_verificar_regla_del_corte` compara versiones **como números** (`_version(v) >= (0,3)`), no como texto, y no nombra ninguna fecha. Lo corrí contra la base real: las dos filas rotas son `E0.2`, SIN FALLAS. Y es consistente con §99.5, que descartó (c) subir `VERSION_SELLO` para el marcador de reglas justamente por no chocar con este `E0.3`.

---

## Respuestas a las preguntas 1–6

**1. La zona ciega de la corrida 15: dos instancias concurrentes.**
Qué pasa exactamente, medido en las dos versiones (F1): A y B congelan sobre **el mismo path** (ninguna ve filas del otro, porque ninguno selló todavía), B pisa los bytes de A, A sella 32 filas citando SU sha mientras el archivo tiene los de B —y con **los precios de B**, porque `sellar` relee el disco— y B sale por divergencia con 0 filas. En base: 32 filas inmutables citando un sha que el disco no tiene, más 1 divergencia. En disco: un solo par de archivos, el del segundo.
**No es fuga nueva del camino T: es preexistente en E0.2 con el canónico, estructuralmente idéntica**, hasta el sha. Lo único que cambia es el nombre del archivo corrompido, y camino T la deja menos dañina (el rojo cae en una tabla fuera de toda métrica y el cupo canónico queda libre).
**Clasificación: zona ciega aceptada.** Razón: `Type=oneshot`, un solo timer, sin `RemainAfterExit`; systemd no arranca una segunda instancia de la misma unidad mientras la primera está activa, el disparo por `Persistent` y el `OnCalendar` siguiente son secuenciales, y la corrida real tarda ~1–2 s. La única vía viva es un `--sellar` a mano en paralelo, prohibido a los agentes por §99.7. No la hago bloqueante porque camino T no la introduce ni la empeora, y porque el bloqueo tendría que caer sobre E0.2, que es lo que está emitiendo. Queda R5 (lock) y la advertencia operativa: **la receta de aplicación no debe correr `--sellar` a mano sin verificar antes que el servicio no está activo.**

**2. Disparo de recuperación en un día sin sesión.** Medido (P5):

| escenario | resultado | fecha ocupada | N | ¿T interviene? |
|---|---|---|---|---|
| sábado, cierre del viernes completo | `sellada`, `estado dia_sin_sesion`, `timing_ok True`, `sesion_obj` lunes | **sí**, el viernes, en `sellos_dinero` | 0 | **no** |
| jueves feriado 26-nov, cierre del 25 (media sesión, 18:00Z) | `sellada`, `dia_sin_sesion`, `timing_ok True`, `sesion_obj` 27-nov | **sí**, el 25-nov | 0 | **no** |
| sábado, fuente atrasada una sesión (jueves) | `intento_no_verificable`, `timing_ok False` | **no**: la fecha queda libre | 0 | **sí** |

**¿Hay algún caso donde T cambie el resultado respecto de E0.2?** Sí, el tercero: insumo atrasado una sesión → E0.2 ocupaba la fecha vieja en la tabla principal, T la deja libre. **¿Hay alguno donde una fecha quede ocupada de una forma que E0.2 no ocupaba? No, y es demostrable por construcción:** T sólo actúa cuando `timing_ok` es falso, y en ese caso escribe estrictamente menos que E0.2 (nada en `sellos_dinero`, y un nombre de archivo nuevo, `.no_verificable`, que ninguna versión anterior usó y con el que nada puede chocar). La ocupación bajo T es un subconjunto de la de E0.2.
**El hallazgo de esta pregunta, y la razón de B1:** los dos primeros casos ocupan la fecha **con timing OK**, y la queman por `estado_dia == "sin_sesion"`, que se evalúa sobre `fecha_sello` (el día de la EMISIÓN en el calendario de NY) y no sobre la sesión objetivo. Esa emisión es prospectiva de verdad —sábado 14:00Z < lunes 13:30Z, con el cierre completo del viernes— y queda con `cuenta_para_N = 0` por una regla que mira el día del emisor, no la verificabilidad. Es E0.2/§57 firmado tal como está y **T no lo toca**; el test (iv) lo fija bien y su docstring lo dice («igual que en E0.2: T sólo actúa con timing roto», «pasa también sobre HEAD (control)»), que es lo correcto. Lo que no puede pasar es que el acta lo omita. El feriado entre semana agrega un detalle: si la sesión anterior ya estaba sellada con los mismos bytes el disparo del feriado sale `ya_sellada` y no cuesta nada; si el disparo de la víspera se perdió, el del feriado ocupa la fecha de la víspera como `dia_sin_sesion` y la quema.

**3. Exclusión de TOELY (§95.4) × camino T.** No se cruzan en ningún punto que produzca un resultado nuevo, y lo verifiqué por los cuatro lugares que preguntás:
- **¿Alguna fila de intento podría llevar TOELY? No.** La exclusión vive en `decidir` (líneas 580-581), después de `universo_operable` y **antes del sorteo**, y las filas de las DOS tablas salen del mismo `dec["filas"]`. `excluidos` es `set(reglas) & set(operables)` con la membresía fijada en `DESDE`, así que no depende de `fecha_insumo`. Medido: `test_toely_tampoco_entra_a_la_tabla_de_intentos…` y mi P4 → 32 filas, `TOELY not in _tickers(db, intentos)`.
- **`insumo_completo` en un intento:** se calcula igual que en un sello y es independiente de la tabla. Verificado en los dos sentidos: sólo TOELY sin barra → `insumo_completo = 1`, `sin_dato = []`; AMD+TOELY sin barra → `insumo_completo = 0`, `sin_dato = ['AMD']`. En el intento del 7-oct reproducido, SHECY sin barra → `insumo_completo = 0` y `estado = no_verificable_timing` (el timing manda en la cadena de `if`, correcto).
- **`excluidos_universo` en el retorno `intento_no_verificable`:** sí, está. Vive en el `return` común de `sellar` (línea 841), no en una rama, así que B3 de la 16b —«32 porque así se firmó», al log de cada noche— vale igual para un intento. Medido en los cuatro tests nuevos y en mis sondas.
- **`decisiones_distintas` en una divergencia contra un intento previo de 33 filas: no puede ocurrir.** `intentos_no_verificables` no existe en la base real (medido), así que toda fila de intento nacerá ≥ E0.3, o sea después del corte de TOELY: las divergencias contra un intento comparan 32 contra 32. El problema de §96.4 B5 (`decisiones_distintas ≈ 33` por ausencia de TOELY y resorteo, no comparable con el 1 del 9-sep y el 0 del 28-sep) sigue vivo **sólo** para `_divergencia(TABLA_SELLOS, …)` contra las 18 fechas de 33 filas, y eso es §96.4 ya declarado, no algo que T agregue.
- **El sorteo:** `decidir` corre idéntico en las dos tablas; la base no entra en el sorteo. Consecuencia que vale escribir: el intento y el sello bueno de la misma fecha comparten la **realización** del sorteo (mismo número de sesiones en el insumo → mismo estado del rng) y difieren sólo en los precios. En el 7-oct real eso se ve: `decisiones_distintas = 0` en la divergencia, con dos insumos distintos.

**4. Lo de siempre.**
- *¿Alguna ruta escribe en `sellos_dinero` con `timing_ok` falso?* **No.** Por el fuente: `tabla = TABLA_SELLOS; if not timing_ok: tabla = TABLA_INTENTOS`, y el único `INSERT` de filas usa `{tabla}`; `timing_ok = timing["timing_ok"] and not evidencia_no_verificable` (la clase de la evidencia sólo endurece). En runtime: seis escenarios, `rotas_en_principal = 0` en todos. Contra la base real: las dos únicas filas rotas son `E0.2`.
- *¿Alguna reescribe o escribe `ext_<fecha>.csv` canónico con timing roto?* **No.** El canónico se escribe sólo si `timing_ok`; con timing roto el nombre es `.no_verificable` (fecha limpia) o un temporal fuera de `DIR_EXT` (fecha con intento). Con sello previo y mismo sha y los dos archivos presentes hay retorno temprano sin escribir; en cualquier otra combinación con sello previo, temporal. Medido: lista de canónicos vacía en los seis escenarios de P4, salvo el que dejó un sello bueno anterior.
- *¿`--sin-red` puede levantar un `.no_verificable.csv`?* **No.** `_NOMBRE_EXTENSION_SELLABLE = ^ext_\d{4}-\d{2}-\d{2}\.csv$` no casa. Medido: con sólo el par nv en la carpeta, `ultima_extension()` → `None` y `main()` sale con código 2.
- *¿La tabla nueva tiene los dos disparadores?* **Sí**, del mismo `_ddl_filas`: `{tabla}_inmutable_1` BEFORE UPDATE y `_2` BEFORE DELETE, con `RAISE(ABORT, …)`. La base real tiene hoy sólo los cuatro de `sellos_dinero` y `divergencias_sello` (medido), y los dos nuevos nacen con la tabla.
- *¿`init_db` es todo `IF NOT EXISTS`?* **Sí**: 6 sentencias `CREATE`, las 6 con `IF NOT EXISTS` (grep sobre el fuente). Con la advertencia de F4: es aditivo a nivel de tabla, **no** a nivel de columna.
- *¿Los tests escribieron sólo en tmp?* **Sí.** En el árbol real: `find` más nuevo que las 15:27 en `dinero/` y `data/backups/` **vacío**, `diff` del inventario de `dinero/datos/sello/` IDÉNTICO, sha de la base real sin cambio. En el worktree: no hay `.db` ni `dinero/datos/sello/`; `find` de archivos más nuevos que las 15:31 en `wt162/data` y `wt162/dinero` vacío salvo `__pycache__`. El fixture `entorno_temporal` del archivo nuevo parchea `DIR_EXT`, `RUTA_DB`, `DIR_BACKUP_EXT` **y `RUTA_BACKUP_CSV`** (R3 de la corrida 15, presente, línea 67). Mis sondas sólo en `tempfile.mkdtemp()`.
- *¿Hay fuga temporal en algún instante que decide tabla o nombre?* **No la encontré, y probé la propiedad maestra sobre ese instante exacto** (P9 punto 3): con la extensión de 5, 6 y 7 sesiones recortada en la misma fecha, `evaluar_timing` devuelve el mismo dict. `avail` es backward-only por construcción (todo `ultimo_cierre` ≤ `fecha_insumo`, medido en tres cortes) y nunca es el reloj de pared. `evaluar_timing` es pura y pide zona horaria. **Lo que la prueba NO cubre:** `fecha_insumo` se deriva de `cierres.index.max()`, así que agregar sesiones posteriores cambia qué fecha se sella — eso no es fuga (es sellar otro `t`), pero significa que la propiedad sólo se puede enunciar «para una `fecha_insumo` fija», y así la probé.
- *¿`available_at` sigue siendo computado por calendario y no observado, y eso ahora decide a qué tabla va la fila?* **Sí a las dos, y lo subo a fuga de sellado declarada.** `avail` es `max(available_at_utc)` de la disponibilidad, que es el **cierre UTC por calendario** de la última sesión con dato de cada ticker: nunca el instante en que la fuente publicó el dato. Hoy decide tabla, nombre de archivo y ocupación de la fecha. La dirección del error es conservadora —una barra cuyo cierre nominal no ocurrió se rechaza, que es justo lo que atrapó el 7-oct— pero **el error inverso es invisible**: un dato completo cuyo cierre nominal ya pasó y que la fuente publicó tarde pasa el gate sin que nada lo registre. Ningún campo guarda cuándo la fila se hizo observable. En la corrida 15 declaré que esta zona ciega subía de categoría; hoy la declaro otra vez y agrego que el 7-oct la vuelve asimétrica en la práctica: **todo el resultado del disparo depende de si yfinance ya emitió una barra intradía para el día en curso**, una propiedad de la fuente que nadie observa ni registra. Un boot a las 08:00 NY (sin barra del día) habría sellado el 6-oct bien; el boot de las 09:31 (con barra) produjo el intento del 7-oct. T amortigua la consecuencia; la dependencia queda.

**5. El 7-oct reproducido: ¿el test (ii) reproduce de verdad el mecanismo?** **Sí, las cuatro piezas, y las verifiqué contra las filas reales:**
- *Barra intradía de la mañana con un ticker sin dato:* `_ext(..., sin_dato=("SHECY",))` deja NaN en la última sesión → `ultimo_cierre_ticker` del ticker = la sesión anterior. El test lo asevera (`sin_barra[0] == LUNES`); la fila real tiene `ultimo_cierre_ticker = 2026-10-06`, una sesión antes del `fecha_insumo = 2026-10-07`. Coincide.
- *`available_at` futuro respecto del reloj:* el test exige `2026-09-15T20:00:00+00:00` con emisión `13:31:04Z`; la fila real tiene `available_at 2026-10-07T20:00Z` con `timestamp_utc 2026-10-07T13:31:04.897105Z`. **Misma hora de reloj al segundo**, y el fallo es en la desigualdad izquierda (`avail < ahora` falso), que es el mecanismo exacto.
- *Apertura objetivo del día siguiente:* `2026-09-16T13:30Z`; la real, `2026-10-08T13:30Z`. Coincide.
- *Sesión anterior sin filas:* el test exige `sello_previo(LUNES) is None and intento_previo(LUNES) is None` y la lista de tickers vacía en las dos tablas. Reproduce que el 6-oct no tiene filas.
- *Hora de Chile vs NY:* correcta. Septiembre y octubre de 2026 están los dos en EDT (UTC−4, el cambio es el 1-nov) y Chile en UTC−3 desde el 6-sep, así que `13:31:04Z` es `09:31 NY` y `10:31 Chile` en las dos fechas, consistente con el disparo del journal a las 10:30:55 Chile y los ~9 s hasta la emisión. El docstring lo dice bien.
- *`fecha_sello`:* el test lo asevera (`fecha_sello_ny == MARTES`), derivado del calendario de NY y no del huso del host (E2).
**Lo que se le escapa, para que quede escrito:** (a) el 09:31 NY real es **un minuto después de la apertura del 7-oct**, y el test no distingue ese detalle porque es irrelevante al mecanismo (la apertura objetivo es la del 8-oct); (b) no cubre el boot **pre-apertura** sin barra del día, que con el mismo `Persistent=true` da `timing_ok` y sella la sesión anterior bien — es el caso que explica por qué el 7-oct falló por un margen de minutos, y el que muestra que el resultado cuelga de la fuente; (c) usa fechas sintéticas de septiembre, así que no ejercita ningún cambio de horario de verano ni feriado (lo cubrí yo en P5, incluido el 26-nov con media sesión a 18:00Z); (d) el 28-sep y el 7-oct reales no son reproducibles desde la fuente, y ningún test puede.

**6. Los números, con hora.** Todos míos, desde el worktree con `venv/bin/python -m pytest … -q -p no:cacheprovider -m "not red"`:
- `15:32:07`→`15:32:29 -03`: `tests/test_camino_T_16_2.py tests/test_sello_dinero.py tests/test_toely_fuera_insumo_e0.py` → **`56 passed, 10 skipped in 21.46s`**. Confirma tu cifra. Con `-rs`, los 10 saltados son todos por base real o extensión congelada ausentes (`§95.5`), listados arriba.
- Repetición con `-rs` a las `15:33`: **`56 passed, 10 skipped in 22.00s`**.
- Integridad permanente contra la base real en `mode=ro` con el módulo parcheado (lo que los saltados no probaron): **5 chequeos, SIN FALLAS** en los 5.
- Sondas propias: `p1_integridad_real.py`, `p2_concurrencia.py` (×2 versiones), `p2b_precios.py`, `p3_varios.py` (P3–P8), `p9_causalidad.py`, `p10_juego.py` (×2 versiones). Todas en `.../scratchpad/probe_auditor/`.
- No corrí la suite completa del árbol real ni del worktree: queda como zona ciega declarada (abajo).

---

## Aplicabilidad

**Aplicable la misma noche, con B1 escrito en el acta y B2 en el mismo `git apply`.** Concretamente:
1. **B2 manda sobre la secuencia:** `camino_T_16_2.diff` + `b2_contrato_16_2.diff` + `b2_api_16_2.diff` en la misma aplicación (el `cumulativo_16_2.v1.diff` de las 15:31:40 parece ser justo eso; no lo audité). Camino T solo deja en pie la F1 de la corrida 15.
2. **R1 y R2 son de una y de pocas líneas y este es el momento** (R1 cierra una integridad rota demostrada; R2 protege la migración que R3 va a pedir). Si no entran hoy, van a tarjeta con fecha, no al olvido.
3. **Lejos de las 23:30 NY**, y hoy domingo el próximo disparo del sellador es el **martes 13-oct a las 00:30 Chile** (§99.9), así que la ventana es amplia. Antes de cualquier `--sellar` a mano de verificación: comprobar que el servicio no está activo (F1).
4. **Qué esperar la primera noche después de aplicarlo:** `intentos_no_verificables` aparece en `dinero/sello_dinero.db` con **0 filas** y sus dos disparadores; `sellos_dinero` crece +32; nace `data/backups/sello_dinero_no_verificables.csv` vacío con cabecera y el backup lo commitea; `version_sello = 'E0.3'` y `sellador_sha256` nuevo (la huella definitiva es la del archivo aplicado, no la del worktree); `SELECT version_sello, estado_timing, COUNT(*)` sigue dando `roto` sólo en `E0.2`, 2 fechas; `dinero/datos/sello/` con el par canónico nuevo y **ningún** `.no_verificable.*` si la noche fue normal; `estado()` con `intentos_no_verificables: 0` y `ultimo_intento: null`; y los **2 tests de integridad parametrizados por la tabla nueva dejan de saltar** (R2 de la corrida 15).
5. **Lo que no hay que esperar:** que el 28-sep o el 7-oct se recuperen. Sus filas se quedan en `sellos_dinero` con `E0.2`, `ext_2026-09-28.csv` y `ext_2026-10-07.csv` siguen siendo las matrices de media sesión y de la mañana, y N sigue en 12. §86.1 y §99.2 ya lo dicen; el acta tiene que repetirlo.

---

## Zonas ciegas

1. **Fuga por el analista, declarada y sin defensa.** El camino T lo diseñó, lo probó y lo rebasó quien ya vio el 28-sep y el 7-oct, y el único criterio que mide su valor —cuántas sesiones cuentan para N— es el que el parche mejora. Ningún test lo detecta. La única defensa es que E0.3 no se aplica retroactivamente y que el corte de método es una versión sellada en cada fila.
2. **La fecha de la carrera (F1) no es alcanzable por el timer, pero el juicio «systemd no arranca dos instancias» es leído de la unidad y de la semántica de systemd, no medido:** no tengo permiso de tocar timers y no lo probé en vivo.
3. **`main()` sigue sin ser testeable y no se ejecutó.** `sellar` y `respaldar_extension` ligan `RUTA_DB`/`DIR_BACKUP_EXT` al importar. Las ramas de export/respaldo y las dos líneas de relojes (R5) son juicio por lectura.
4. **`available_at` es computado por calendario, no observado**, y ahora decide tabla, nombre de archivo y ocupación de la fecha. Nada registra cuándo la fila se hizo visible. El error conservador se ve; el inverso (dato completo publicado tarde) es invisible.
5. **Nada de esto es point-in-time.** yfinance reajusta la historia sin avisar (el propio meta lo declara: «cierres ajustados retroactivamente por yfinance: no point-in-time»), y el 28-sep y el 7-oct **no son reproducibles desde la fuente**: la evidencia es el par de archivos sellado y su sha, no la fuente. Fuga de disponibilidad en el sentido del mandato: lo que se emitió antes está probado; lo reproducible después, no.
6. **Yahoo de verdad no se probó** (red parcheada en toda la suite y en todas mis sondas); `descargar_extension` es la única función que toca red y nadie la ejecutó.
7. **Los 10 saltados.** Sin `.db` ni `dinero/datos/sello/` en el worktree (§95.5, copia denegada), la suite no probó integridad permanente, ni la base real, ni `ultima_extension` sobre evidencia real. Lo cubrí a mano con `mode=ro` y el módulo parcheado, pero **mi sonda no es el test**: no corre en el hook ni en CI, y la diferencia importa.
8. **No corrí la suite completa** (ni del árbol real ni del worktree), así que no puedo decir nada sobre regresiones fuera de los tres archivos del sellador — y menos sobre B2, que toca `api/main.py` y `frontend/src/lib/tipos.ts`. El paralelo de §96.3 (26 rojos idénticos en worktree-con-parche y worktree-HEAD-puro por artefactos gitignorados ausentes) no está medido hoy.
9. **B2 (etapa 2) no está auditado.** Entró al worktree a las 15:30:41, mi dictamen es sobre `4b494966…`, y lo único que verifiqué de B2 es que su cambio al sellador queda íntegro dentro de `estado()` (sólo lectura, `mode=ro`) y no toca el camino de sellado.
10. **F2, F3 y F4 son huecos que ningún test del parche cubre**; los tres los encontré con sondas propias, no con la suite.
11. **La base real no se modificó y tampoco se copió**, así que el comportamiento del parche sobre 722 filas verdaderas en escritura no se probó: `init_db` creando la tabla sobre la base real es juicio por lectura más la simulación de P7.
12. **Intentos del DSR que consume este dictamen: 0.**

**Hora de `date` al cerrar: Sun Oct 11 15:40:44 -03 2026.**

---

### Archivos relevantes (rutas absolutas)
- Parcheado, etapa 1 auditada: `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/e5b2a82d-fdff-4991-be0e-3e74650ec9b1/scratchpad/wt162/dinero/sello_dinero.py` (hoy ya con B2; la etapa 1 reconstruida está en `.../scratchpad/probe_auditor/e1/dinero/sello_dinero.py`, sha `4b494966…`)
- Diff etapa 1: `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/e5b2a82d-fdff-4991-be0e-3e74650ec9b1/scratchpad/camino_T_16_2.v1.diff`
- Tests: `.../scratchpad/wt162/tests/test_camino_T_16_2.py`, `.../tests/test_sello_dinero.py`, `.../tests/test_toely_fuera_insumo_e0.py`
- Mis sondas: `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/e5b2a82d-fdff-4991-be0e-3e74650ec9b1/scratchpad/probe_auditor/` (`p1_integridad_real.py`, `p2_concurrencia.py`, `p2b_precios.py`, `p3_varios.py`, `p9_causalidad.py`, `p10_juego.py`, más `db_antes.txt`/`sello_antes.txt`/`t0.txt` como testigos de aislamiento)
- Árbol real, no tocado: `/home/nicolasaraneda/dev/mki-terminal/dinero/sello_dinero.py` (`cd0e70c8…`), `/home/nicolasaraneda/dev/mki-terminal/dinero/sello_dinero.db` (`2a016c52…`)

---

## Qué hizo el orquestador después (nota del orquestador, 15:47 a 15:50)

R1 (guarda `persistido is False` en `sellar`, con fila en `divergencias_sello` y resultado `rechazado_insumo_no_persistido`;
`main()` exporta en esa rama), R2 (advertencia en `_ddl_filas`; test de paridad de columnas sobre la base real con
`pytest.skip` declarado; contraprueba de F4) y el cosmético (`FROM {TABLA_SELLOS}`) se plegaron a `camino_T_16_2.diff`
(script `plegar_R1_R2.py`, archivado en `evidencia/`). El test de reproducción de F3 se escribió antes y falló sobre el
camino T sin la guarda por su aserción (`filas_insertadas=32`; `evidencia/pytest_R1_sobre_camino_T_sin_guarda.txt`).
B1 va al párrafo del acta de aplicación (bitácora §6) y B2 a la receta (los tres parches en el mismo acto). R3, R4 y R5
van a la tarjeta §81. El addendum del auditor sobre B2 y sobre el plegado se anexa abajo.

---

# ADDENDUM al dictamen del `auditor-lookahead` — segunda pasada, corrida 16-2: B2, y el delta de R1/R2 plegado al camino T

> Archivado por el orquestador tal como lo devolvió el agente (segunda pasada, 15:49:56 a 15:55:19). Después de este
> addendum el orquestador plegó R6 (las 21 claves en `UltimoSelloDinero`, con test) a `b2_api_16_2.diff` (script
> `evidencia/plegar_R6.py`); el auditor no volvió a pasar sobre ese cambio, que es sólo de tipos y de test.

**APLICABLE — los tres parches aplicados juntos. Cero bloqueantes de CÓDIGO.** R1 cierra F3 sin pisar ninguna rama legítima (10 ramas recorridas, integridad en pie en las 10), R2 prueba F4 y su contraprueba muerde, y B2 no toca el camino de sellado más que `estado()`, no puede crear la tabla al leer, no contamina ningún contador y no insinúa resultado. Mi **B2 de dictamen queda CERRADA**; mi **B1 sigue en pie** y es de acta, no de código. Una R nueva, chica.

Hora de `date` al abrir esta pasada: **Sun Oct 11 15:49:56 -03 2026**.

## Lo verificado, con números y hora

**Artefactos, huellas propias.** Los tres `.diff` finales en `GEMELO/propuestas/parches/`: `camino_T_16_2.diff` `48addf80bc5eecced63af4f916be1eea075834051f0ce4bdfb9aa36d0768f4d4`, `b2_contrato_16_2.diff` `ad864726cf91e2d50f2430cd3f9351d9cff1dfc657a8398304f682c0a0abf45f`, `b2_api_16_2.diff` `04b018165cfa81701b00ba33524ed52856115de7b5537a782df897473431b525` (nota del orquestador: ésta es la huella ANTES de plegar R6; la final está en la bitácora §2.3).

**Camino T solo deja el sellador en `610f5b05…`: confirmado por reconstrucción.** Apliqué `camino_T_16_2.diff` (sólo la ruta `dinero/sello_dinero.py`) sobre `HEAD:dinero/sello_dinero.py` en un directorio aparte → `610f5b054aaae1304a58d9979dc6a87e98886a93b84669fb6a276a07efa5c8b7`, exactamente lo que declarás. **Discrepancia con tu enunciado:** `wt162_e1/dinero/sello_dinero.py` **no** está en ese estado — tiene `299a7627f289e70f8ae3cb83166672c451f0921ca88c21450a87892ae3963d93`, idéntico a `wt162`, o sea la pila completa con B2. El `.diff` es lo que dice; ese directorio no. Lo que auditė como «camino T solo» es mi reconstrucción, no `wt162_e1`.

**Los tres parches aplican en orden sobre HEAD limpio y reproducen el worktree byte a byte.** Clon nuevo en `c271822`, `git apply --check` OK en los tres, aplicados en orden, y las **8 huellas** coinciden con el worktree: `dinero/sello_dinero.py 299a7627…`, `api/main.py fa7d0651…`, `api/CONTRATO.md 9b40b497…`, `frontend/src/lib/tipos.ts 587e20f3…`, `tests/test_sello_dinero.py 01dcd57b…`, `tests/test_camino_T_16_2.py 05ab8999…`, `tests/test_b2_intentos_visibles_16_2.py dc9ce61e…`, `tests/test_toely_fuera_insumo_e0.py 6a3ecb4b…`. Verificado por mí, no leído de tu reporte.

**Suite, con hora.** `15:51:46` → `15:52:12 -03`, desde el worktree, `venv/bin/python -m pytest tests/test_camino_T_16_2.py tests/test_sello_dinero.py tests/test_toely_fuera_insumo_e0.py tests/test_b2_intentos_visibles_16_2.py -q -p no:cacheprovider -m "not red" -rs`:
```
66 passed, 11 skipped, 1 warning in 24.82s
```
Contra mi corrida de la primera pasada (`56 passed, 10 skipped`): **+10 passed** (8 del archivo de B2, 2 nuevos en `test_sello_dinero.py` — el de F3 y la contraprueba de R2) y **+1 skipped** (la paridad de columnas sobre la base real, línea 755, que salta con razón declarada hasta que el sellador cree la tabla). Los 11 saltados siguen siendo todos por base real o extensión congelada ausentes. El único warning es `StarletteDeprecationWarning` de `fastapi.testclient`, ajeno.

**Prohibiciones, medidas al cerrar:** `sha256(dinero/sello_dinero.db)` del árbol real = `2a016c52…`, idéntico al de la primera pasada; `sha256(dinero/sello_dinero.py)` real = `cd0e70c8…` = HEAD; `find` de archivos más nuevos que las 15:49 en `dinero/` y `data/backups/` del árbol real: **vacío**; nunca `--sellar`; la base real sólo `mode=ro`; el worktree sigue sin `.db`. Escribí un test mutante en el worktree para la mutación de R2 y **lo borré** (verificado ausente). Mis sondas nuevas: `probe_auditor/q1_ramas_con_guarda.py`, `q2_b2.py`, `probe_auditor/e2/`, `probe_auditor/tres/`.

## Respuestas

### (a) La guarda R1: ¿cierra F3 sin pisar ninguna rama legítima?

**Sí. Recorrí las diez ramas alcanzables de `sellar` con la guarda puesta** (sonda `q1_ramas_con_guarda.py`; `sel`/`int`/`div` = filas en `sellos_dinero` / `intentos_no_verificables` / `divergencias_sello`; «integridad» = toda cita apunta a un archivo que existe con el sha citado, medido con el `DIR_EXT` de cada caso):

| # | escenario | resultado | sel | int | div | integridad | `persistido` |
|---|---|---|---|---|---|---|---|
| 1 | sello normal (timing ok, fecha limpia) | `sellada` | 32 | 0 | 0 | OK | True |
| 2 | intento (timing roto, fecha limpia) | `intento_no_verificable` | 0 | 32 | 0 | OK | True |
| 3 | mismo juego, MISMO sha | `ya_sellada` | 32 | 0 | 0 | OK | True |
| 4 | mismo juego, OTRO sha | `divergencia_registrada` | 32 | 0 | 1 | OK | False |
| 5 | intento previo, MISMO sha | `ya_intentada` | 0 | 32 | 0 | OK | False |
| 6 | intento previo, OTRO sha | `divergencia_registrada` | 0 | 32 | 1 | OK | False |
| 7 | timing roto, sello previo de OTRO juego | `divergencia_registrada` | 32 | 0 | 1 | OK | False |
| 8 | canónico con timing roto (`--sin-red` tarde) | `rechazado_evidencia_canonica` | 0 | 0 | 1 | OK | True |
| 9 | **OTRO juego, OTRO sha (F3)** | **`rechazado_insumo_no_persistido`** | 32 | 0 | 1 | **OK** | False |
| 10 | **OTRO juego, MISMO sha (legítima)** | **`sellada`** | **64** | 0 | 0 | **OK** | True |

La fila 10 es la que decide la pregunta: es la única rama legítima donde el juego cambia y la fecha ya está sellada, y **sigue sellando** (64 filas = 32+32, dos juegos conviviendo por la `UNIQUE (fecha_insumo, ticker, juego)`), porque ahí `congelar_extension` devuelve el canónico existente con `persistido` True y la guarda es un no-op. Las filas 4, 5, 6 y 7 llegan con `persistido` False pero **retornan antes** de la guarda (divergencia o `ya_intentada`), así que la guarda es inalcanzable en ellas: el comentario del código («todas las ramas legítimas ya salieron arriba con cero filas») es exacto. **La guarda sólo se alcanza con `persistido` False en la configuración de F3 y en ninguna otra.** Integridad en pie en las diez (corrección de método: mi primera corrida de esta sonda dio tres falsos `ROTA` porque leí `S.DIR_EXT` después del bucle, siendo un global que cada caso reasigna; la rehice guardando el directorio por caso).

Lo único que la guarda «pierde» es un segundo sello de otro juego **con otro insumo** — y ese insert nunca fue sano: citaba un temporal que `main()` borra. Refusar es lo consistente con E4-bis, que cerró a propósito la escritura de un divergente en la carpeta de evidencia; la alternativa (persistir el insumo con un nombre calificado por juego) abriría otra vez esa ruta.

**`decisiones_distintas = NULL` es lo honesto; no pongas 0.** Medido: se guarda como NULL de SQL de verdad (`typeof = null`), la columna es nullable (`PRAGMA`: `notnull = 0`), y **ningún consumidor la agrega** — `grep` en `api/` y `frontend/src/` del worktree: cero referencias; `estado()` sólo hace `COUNT(*)` sobre `divergencias_sello`. Un 0 ahí afirmaría «los dos insumos decidieron igual», que es una afirmación sustantiva y en este caso vacía: no hay filas del mismo juego con que comparar. Los tres valores que la base real ya tiene son sustantivos (1 el 9-sep, 0 el 28-sep y el 7-oct), así que un 0 fabricado se mezclaría con ellos; NULL se distingue. En el CSV de `exportar_csv` el NULL sale como celda vacía, que también es más honesto que un 0. El `detalle` lo declara en texto («decisiones_distintas es NULL porque no hay filas del mismo juego con que comparar»). Correcto como está.

*Observación sin número:* el `detalle` de la guarda afirma la causa («cambio de `juego_activo` entre dos disparos de la misma fecha»). Hoy es la única causa posible (lo medí). Si alguna rama futura llegara a la guarda por otro camino, el detalle la mal-rotularía. No pido cambiarlo; lo dejo escrito.

### (b) B2

- **¿Toca el camino de sellado en algo más que `estado()`?** **No.** `diff` de camino-T-solo (`610f5b05…`) contra el worktree final (`299a7627…`) sobre `dinero/sello_dinero.py`: **dos hunks, los dos íntegros dentro de `estado()`** (la clave `ultimo_intento` en el `vacio` y en el return, y el `SELECT … FROM intentos_no_verificables ORDER BY id DESC LIMIT 1` en el mismo `try/except OperationalError` que el COUNT). Nada en `congelar_extension`, `sellar`, `decidir`, `init_db`, `evaluar_timing`, `_ddl_filas`, `exportar_csv`, `respaldar_extension` ni `main`.
- **¿La API puede crear la tabla al leer?** **No**, verificado contra una base E0.2 fabricada sin pasar por `init_db` (sonda `q2_b2.py`): tablas antes `['divergencias_sello','sellos_dinero','sqlite_sequence']`, `estado()` responde `filas 0 / intentos_no_verificables 0 / ultimo_intento None`, `GET /api/dinero/sellos` → **200** con las 13 claves de `E0`, y después: **tablas idénticas, `mtime` idéntico y `sha256` del archivo de base idéntico**. `conectar(solo_lectura=True)` abre con `mode=ro` y no llama `init_db`; `estado()` además ni abre si el archivo no existe. Lo verifiqué por mi cuenta, no sólo por su test.
- **¿`ultimo_intento` puede mezclarse con `ultimo_sello` en algún contador?** **No.** Con SOLO un intento sellado (32 filas en la tabla aparte): `filas = 0`, `sesiones_selladas = 0`, `sesiones_que_cuentan_para_N = 0`, `divergencias_registradas = 0`, `intentos_no_verificables = 1`, `ultimo = None`; y por la API: `E0.estado = "SIN FILAS"`, `ultimo_sello = None`, `decisiones_proxima_apertura = 0`. Las tres consultas de conteo nombran `FROM sellos_dinero` explícitamente. `set(ultimo_intento) == set(_CLAVES_ULTIMO)`: True (21 claves). La enmienda del contrato lo escribe además en prosa («Un intento nunca entra a `sesiones_selladas`, `sesiones_que_cuentan_para_N`, `filas`, `ultimo_sello` ni `decisiones_proxima_apertura`»), y el código lo cumple.
- **¿Alguna frase nueva insinúa resultado?** **No.** Pasé el payload entero con un intento adentro contra una lista más amplia que la del test (`confianza`, `rentable`, `retorno esperado`, `ganancia esperada`, `sostiene casi toda`, `probable`, `seguro`, `garantiz`, `exito`, `promete`, `ventaja`): el único acierto es `ventaja` y está en el `que_es` **preexistente**, en negación («Nada de esta pantalla mueve plata ni afirma una ventaja»). `NOTA_INTENTOS_E0` no contiene ninguna: describe la regla incumplida, dice «no cuentan para N», «no ocupan la fecha ni el cupo de evidencia» y declara el caso de la base anterior a E0.3. **`confianza`, prohibida en todo el sistema, no aparece.** La enmienda se escribió antes de la API y el test `test_el_contrato_y_los_tipos_del_frontend_declaran_las_tres_claves` lo fuerza buscando «Enmienda 16-2» en `api/CONTRATO.md`.

### (c) ¿La contraprueba de R2 prueba F4 o algo trivial?

**Prueba F4, y lo prueba de la manera correcta: tiene su propio anti-trivialidad, y lo mordí.** La contraprueba fabrica una `sellos_dinero` a la que le falta `insumo_completo`, **asevera que la carencia existe** (`assert ("insumo_completo","INTEGER") not in _columnas(...), "la contraprueba no fabricó la carencia"`), corre `S.conectar(db)` → `init_db`, y exige que el verificador levante `PARAR Y REPORTAR`; después muestra que una base nacida en E0.3 pasa con 36 columnas. Eso es exactamente F4: `init_db` crea `intentos_no_verificables` completa y **deja corta** `sellos_dinero`, porque `CREATE TABLE IF NOT EXISTS` es un no-op.

Lo que podía volverla trivial es que la fabricación dejara de funcionar (el `.replace()` depende de una línea del fuente con su comentario inline) y el test pasara por otra razón. Lo probé con una **mutación**: cambié la cadena del `replace` por una que no existe, copié el archivo mutado al worktree y corrí sólo ese test:
```
E  AssertionError: la contraprueba no fabricó la carencia
FAILED tests/test_mutante_auditor_tmp.py::test_contraprueba_la_paridad_de_columnas_ve_una_base_vieja_a_la_que_init_db_no_le_agrega_la_columna
1 failed, 52 deselected in 0.68s
```
Falla **ruidosa y con el diagnóstico correcto**, no en silencio. (Test mutante borrado del worktree; verificado ausente.) El verificador compara nombre **y tipo, en orden**, así que también vería una reordenación o un cambio de tipo, no sólo una ausencia. Y la mitad que corre sobre la base real salta con razón declarada hasta la primera noche con E0.3, que es lo que pedí.

**El rojo de R1 sin la guarda, releído** (`pytest_R1_sobre_camino_T_sin_guarda.txt`): `AssertionError: F3: sellar insertó filas con juego 'agresivo' que citan un archivo que main() borra (resultado='sellada', filas_insertadas=32)` — rojo por su propia aserción sobre el camino T sin guarda, no por un `TypeError`. Correcto.

### (d) Mis B1 y B2

- **B2 (secuencia): CERRADA.** Los tres parches aplican en orden sobre HEAD limpio, reproducen el worktree en las 8 huellas, y el cambio de B2 al sellador vive dentro de `estado()`. Aplicándolos **juntos** se consume un solo cambio al sellador por noche, el contrato queda enmendado antes que la API, y la F1 de mi dictamen de la corrida 15 —una noche quemada indistinguible de un sábado— queda cerrada: `intentos_no_verificables`, `ultimo_intento` y `nota_intentos` salen por `/api/dinero/sellos`. Si por cualquier razón se aplicara camino T solo, B2 vuelve a estar abierta.
- **B1 (acta): SIGUE EN PIE, y es de texto.** Nada en esta segunda tanda la toca. El acta tiene que escribir que camino T salva los disparos de recuperación cuyo timing sale **roto** (la forma del 7-oct) y **no** los que salen con timing OK en un día sin sesión (sábado o feriado entre semana: `sellada` / `dia_sin_sesion` / `cuenta_para_N = 0`, fecha ocupada, idéntico a E0.2 — medido en mi primera pasada, P5). §99.2 descartó (b) y (c) con la razón «ya habría salvado el 7 oct», cierta para una forma y falsa para la otra.
- **¿Queda algo bloqueante de CÓDIGO? No.**

## Exigencias que quedan

**R6 (nueva, chica).** `UltimoSelloDinero` de `frontend/src/lib/tipos.ts` declara **12 campos**; `_CLAVES_ULTIMO` y la enmienda del contrato declaran **21**. Faltan en el tipo: `creado_en`, `estado_dia`, `estado_timing`, `fecha_sello`, `insumo_completo`, `insumo_ext_archivo`, `reglas_sha256`, `sellador_sha256`, `version_sello`. La deriva es **preexistente** (el tipo venía así para `ultimo_sello`; el parche sólo lo extrajo a una interfaz), pero `ultimo_intento` la hereda, y para un intento los dos campos que faltan y más importan son justamente **`estado_timing`** (lo que lo distingue de un sello) y **`insumo_ext_archivo`** (lo que dice que la evidencia es `.no_verificable`). El test nuevo verifica que las tres claves de `E0` estén y que `ultimo_intento: UltimoSelloDinero | null` exista, pero no que la interfaz cubra las 21. Completar el tipo (o declarar en el contrato que `tipos.ts` sirve un subconjunto y cuál) antes de que alguien construya la vista `/sellos`. No bloquea: `tsc --noEmit` da 0 porque un subconjunto es TypeScript válido, y el riesgo es de pantalla, no de sello.

**Siguen en pie de mi dictamen, sin cambio:** R3 (la fila de intento tiene que poder explicarse sola: la discordancia inversa de relojes deja una fila que satisface la regla maestra en sus propias tres columnas y dice `estado_timing = roto`; R2 abrió el camino al declarar que una columna nueva exige migración con acta, así que R3 ahora tiene una receta), R4 (el `.no_verificable` huérfano que `main()` no declara, R1 de la corrida 15) y R5 (lock entre congelar y sellar, que amortigua F1). Las tres a tarjeta con fecha si no entran hoy.

## Zonas ciegas de esta pasada

Las once de mi dictamen siguen igual. Agrego: (1) **no corrí la suite completa** ni medí el paralelo worktree-con-parches contra worktree-HEAD-puro, así que no puedo decir nada sobre regresiones fuera de los cuatro archivos de test que corrí — y B2 toca `api/main.py` y `frontend/src/lib/tipos.ts`, cuyos tests de paridad de API (`test_api.py`, `test_frontend_estatus.py`) no ejecuté; (2) **no corrí `tsc --noEmit`** (tomo tu «exit 0» como tu medición, no como la mía); (3) la vista `/sellos` no muestra las claves nuevas (decisión de pantalla a firma), así que lo que B2 vuelve visible hoy es la API y no la pantalla; (4) `main()` sigue sin ser testeable y la rama nueva `rechazado_insumo_no_persistido` de `main()` es juicio por lectura; (5) `wt162_e1` no contiene el estado que su nombre sugiere, así que si alguien reaudita «camino T solo» desde ese directorio va a auditar la pila completa.

**Hora de `date` al cerrar: Sun Oct 11 15:55:19 -03 2026.**

### Archivos (rutas absolutas)
- Parches finales: `/home/nicolasaraneda/dev/mki-terminal/GEMELO/propuestas/parches/camino_T_16_2.diff`, `.../b2_contrato_16_2.diff`, `.../b2_api_16_2.diff`
- Worktree con los tres: `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/e5b2a82d-fdff-4991-be0e-3e74650ec9b1/scratchpad/wt162` (sellador `299a7627…`)
- Camino T solo, reconstruido por mí: `.../scratchpad/probe_auditor/e2/dinero/sello_dinero.py` (`610f5b05…`)
- Clon de verificación de los tres parches: `.../scratchpad/probe_auditor/tres/repo`
- Mis sondas de esta pasada: `.../scratchpad/probe_auditor/q1_ramas_con_guarda.py`, `.../q2_b2.py`, `.../trivial/t.py` (el mutante de R2)
