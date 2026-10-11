# Bitácora de la corrida 16-1 — el vigía y el riel de medición (actas §93.8, §93.9, §93.3 ii, §95.2 R2/R3, §99.8)

> Sábado 10-oct-2026, de noche, con Nicolás presente (acta §99.9). Encargo: `~/encargo.md` (escrito por el asistente del
> chat a las 22:30 sin leer el código). Orquestador: Fable 5.1, esfuerzo alto, elegidos al arrancar. Horas de Chile leídas
> de `date` (la primera, 22:17:51). Nada se pusheó, nada se commiteó, nada se firmó, nada se operó; ninguna unidad de
> systemd se tocó; el sellador real no se corrió; las bases reales se abrieron sólo en `mode=ro` (más `init_db()` del
> vigía real, que no corrió). Lista de permisos de §99.7 vigente: ningún permiso denegado se rodeó.

**PRIMERA LÍNEA (estado al cierre): los cuatro bloques están APLICADOS al árbol real (corte de método 10-oct-2026
23:12:48) y SIN commitear; el commit es de Nicolás (lista de 27 rutas en §8).** Dictamen del auditor APLICABLE CON
EXIGENCIAS con las tres bloqueantes de código atendidas antes de aplicar; suite completa del árbol real después: **1116
passed, 5 skipped, 1 xfailed, 0 failed**; guardián APROBADO CON EXIGENCIAS, las tres atendidas (§6.2, con una pausa de
sesión de ~14,5 h declarada entre la E1 y la E2). Ninguna fila sellada tocada, ninguna cifra publicada movida, ninguna
firma: lo que necesita decisión está en la tarjeta **§80**. Las copias de bases al worktree fueron denegadas por la
lista de permisos aunque estén en ella (§0.5). Predicciones falsables del lunes 12-oct en §7.

---

## 0. Reloj, orientación y lecturas de sólo lectura

### 0.1 Reloj y timers (22:17:51 y 22:18)

`date`: `Sat Oct 10 22:17:51 -03 2026`. `systemctl --user list-timers --no-pager` (copiado tal cual, sólo las unidades
`mki-*`):

```
NEXT                              LAST                              UNIT
Mon 2026-10-12 17:50:00 -03       Fri 2026-10-09 17:50:00 -03       mki-noticias.timer
Mon 2026-10-12 18:15:00 -03       Fri 2026-10-09 18:15:00 -03       mki-snapshot.timer
Mon 2026-10-12 18:25:00 -03       Fri 2026-10-09 18:25:00 -03       mki-reporte.timer
Mon 2026-10-12 18:40:00 -03       Fri 2026-10-09 18:40:00 -03       mki-backup.timer
Mon 2026-10-12 19:00:00 -03       Fri 2026-10-09 19:00:00 -03       mki-vigia.timer
Mon 2026-10-12 20:30:00 -03       Fri 2026-10-09 20:30:00 -03       mki-vigia-rechequeo.timer
Mon 2026-10-12 21:05:00 -03       Sat 2026-10-10 04:35:00 -03       mki-sonda-cierre.timer
Tue 2026-10-13 00:30:00 -03       Sat 2026-10-10 00:30:00 -03       mki-sello-dinero.timer
```

Ningún job `mki-*` dispara antes del lunes 12-oct a las 17:50, como §99.9 esperaba. (La sonda disparó por última vez el
sábado a las 04:35, dentro de su grilla `Tue..Sat 00..03 America/New_York`; su próximo pase es el lunes 21:05.)

### 0.2 Árbol de git y bases

`git log --oneline -6`: HEAD `864606c` «Backup diario 2026-10-09», sobre `f424e8d`, `d701d22`, `32e9ecb`, `f921df0`
(corrida 16b y actas §95–§97), `f5b659e` (corrida 16a). `git status --short`: `M DECISIONES.md` (actas §98 y §99
anexadas por Nicolás), `M data/backups/sello_dinero.csv`, `M data/sonda_cierre.csv`, `?? data/backups/sello_dinero_ext/
ext_2026-10-09.{csv,meta.json}`. Nada fuera de lo que el encargo §0.2 admite. Dos worktrees de la 16b seguían registrados
y `prunable` (`wt16b`, `wt16b_head`): se podan al cierre (§6.7).

Huellas de las tres bases **al abrir** (md5 a las ~22:18; sha256 a las 22:43:35, sin ningún job entre medio):

| base | md5 | sha256 |
|---|---|---|
| `senales.db` | `f76740dd5aa82caa317cef87265c883b` | `98a048de1dbd6d8c6f53821ad2e879c307cc1d536c64e0dfbb79f90b2f72ced8` |
| `noticias.db` | `f6b9e8a42c5c9ca158e36528f8a5f517` | `1829b61b0233b03e493939c5d4b8b56c803a0c6965042d8c9006cc4362336d4c` |
| `dinero/sello_dinero.db` | `412ceb07ec2f873770a36af78f3c095d` | `2a016c523adf6542d5b44dd081c54bfa9bc54456c8c554cd6b69772f6585a636` |

### 0.3 Suite completa al abrir (árbol real, HEAD `864606c` + actas §98/§99)

**22:19:00 → 22:27:01: 1042 passed, 5 skipped, 1 xfailed, 29 warnings en 480,25 s, exit 0.** Exactamente el número que el
encargo esperaba. Advertencias conocidas (`Pandas4Warning` de `motor.py:215`, `starlette.testclient`, `GEMELO/transversal.py:260`).

### 0.4 Lo leído antes de escribir código (encargo §0.1)

`DECISIONES.md` §93 (93.3 ii, 93.4-bis, 93.8, 93.9, 93.14), §95 (95.2), §97, §98, §99; `espera_firma.md` §66 (B, C.2,
C.5, C.6, D.1, D.2), §67, §72, §74, §78; `bitacora_16a.md` (§3, §4.1, §6, §7); `dictamen_16a/auditor_guarda_puntaje.md`
(§6–§9, R2 y R3). Código: `snapshot.py`, `mki_vigia.py`, `mki_noticias.py`, `costos.py` enteros; `senales.py`
(`ya_existe_snapshot_hoy`, `info_snapshot_hoy`, `verificar_puntaje_pendientes`, `verificar_pendientes`,
`predicciones_selladas_del_dia`); `calendarios.py`; los tests `test_vigia.py`, `test_guarda_puntaje.py`,
`test_conocibilidad.py` (fixture `sellador`, guarda (b), H0), `test_autonomia.py` (fixture y reloj), `test_parche_
guardia_ancla_temporal.py`, `test_parche_snapshot140.py`, `test_razones_xfail.py` (cabecera). Lecturas de la máquina en
`mode=ro` (22:2x): 68 snapshots, **53 con `sox_fecha`**, **1 con `sox_fecha ≠ fecha`: el 7-sep-2026 (`sox_fecha`
4-sep), feriado de NYSE**; candidatas invertidas fuera de `verificacion_puntaje`: `2026-09-28: 24` y ninguna otra fecha;
`data/snapshot.log`: el AVISO de las 24 aparece en cada entrada del 5 al 9-oct, «verificador puntaje: 23/25/24/21
verificadas»; `data/costos_ia.log`: 7, 8 y 9-oct `freno_presupuesto` con 1020/1017/999 analizados y 1928/1124/340
pendientes; `data/noticias.log`: 20 líneas «credit balance is too low», la primera `2026-09-07T20:52:21Z`;
`data/vigia.log`: 9-oct «todo OK — sin alerta» y rechequeo «sin alerta pendiente»; no existe `data/vigia_pendiente.json`.

### 0.5 Worktree y permisos (encargo §0.4 y «Noche y reloj»)

- `git worktree add --detach …/scratchpad/wt161 HEAD` (entre las 22:25:06 y las 22:28:03; la orden compuesta que lo
  incluía con `date` fue denegada y se repitió sola, sin `date`).
- **Copiar las tres bases al worktree: DENEGADO dos veces** —primero con `cd <repo> && cp senales.db …` (las tres), después
  con exactamente `cp senales.db <wt>/`, `cp noticias.db <wt>/` y `cp dinero/sello_dinero.db <wt>/dinero/` (las tres),
  que son las formas que la lista de §99.7 permite—. No se insistió ni se rodeó. Consecuencia: rige el criterio §95.5
  (juzga la suite del árbol real con todas las bases, más un control sobre HEAD puro en el worktree). Hecho para Nicolás
  en la tarjeta **§80**.
- Enlazar `GEMELO/cache` y copiar las dos corridas selladas gitignoradas de `backtest/resultados/` al worktree
  (`ln -s` + `cp -r`, pedido una vez): **permitido** (~22:28). Sin ellas la 16a tuvo un rojo más en `test_backtest`.

---

## 1. Método, con horas (corte de método por bloque en §4)

- **22:28:03 → 22:35:19: suite completa del worktree sobre HEAD puro, sin bases** (línea base de rojos de entorno):
  **19 failed, 939 passed, 83 skipped, 1 xpassed, 6 errors, 434,37 s**. Los 25 rojos: `test_api` (6, los D*), `test_dinero`
  (2), `test_frontend_estatus` (1), `test_linea_base` (1), `test_readme` (9), `test_cifras_arbitro` (6 errores). Mismo
  conjunto que la 16a salvo `test_backtest`, que ahora pasa porque las corridas selladas sí se copiaron. Salida en
  `dictamen_16_1/evidencia/` (sólo el resumen; la salida completa de esta corrida no se archivó, la del control con
  cambios sí). **Hallazgo:** al terminar, el worktree tenía una `senales.db` (49 152 bytes) y una `noticias.db` (36 864)
  **vacías, creadas por la suite** (`init_db()` de un test que no parchea `DB_PATH`; zona ciega 7 del dictamen 16a, ahora
  medida): desde ese momento los tests `solo_con_base` no se saltan y corren sobre una base vacía. Se borraron antes de
  la corrida con cambios (22:40) para que la comparación por conjuntos tenga sentido; volverán a crearse en esa corrida.
- **22:29 → 22:38: tests escritos ANTES del código**, en el scratchpad y sin tocar el worktree mientras corría la línea
  base: `tests/test_frescura.py` (bloque A, 268 líneas), `tests/test_puntaje_retorno.py` (C, 203),
  `tests/test_noticias_ledger.py` (D, 226), `tests/test_vigia_16_1.py` (B + D del vigía, 444).
- **22:38:07 → 22:38:12: los cuatro archivos corridos sobre HEAD sin el código** (`evidencia/pytest_nuevos_sobre_HEAD.txt`):
  **25 failed, 5 passed, 1 error de recolección** (`test_vigia_16_1.py` usa a nivel de módulo una constante que HEAD no
  tiene). Pasan en HEAD los 5 controles que deben pasar (escenario, «sin error sigue ok», «sin pendientes sigue ok», «el
  freno sigue freno», «el vigía sigue ok con freno y sin pendientes»). Las reproducciones legítimas fallan por su propia
  aserción: H0 (`snapshot.py selló el 2026-09-29 con sox_fecha=2026-09-28`), el retorno entero del verificador (`'int'
  object is not subscriptable`), el ledger del 7-sep (`resultado` «ok» con 0 analizados). El resto son superficie nueva
  (`MARCA_NEGATIVA`, `_negativa_declarada_en_log`, etc.).
- **22:39: código en el worktree** (`snapshot.py`, `senales.py`, `mki_vigia.py`, `mki_noticias.py`) y adaptación de cinco
  tests existentes: `test_conocibilidad.py` (el test de fijación de H0 sale —ahora H0 es una negativa, y su reproducción
  vive en `test_frescura.py`—; el stub de `verificar_pendientes` devuelve el dict nuevo), `test_guarda_puntaje.py` (lee
  `["verificadas"]` del dict), `test_parche_guardia_ancla_temporal.py` y `test_parche_snapshot140.py` (fijan `date.today()`
  del módulo bajo prueba: antes era «irrelevante», con la guarda de frescura decide; sin esto fallarían cualquier día de
  sesión de XNYS con `sox_fecha` histórico), `test_vigia.py` (la errata «launchd»).
- **22:39:57: primera corrida de los archivos tocados: 15 failed, 130 passed.** Dos defectos míos y uno de entorno: (1) la
  guarda de frescura disparaba con `sox_fecha` vacío (está al nivel de `if not pred.empty`, no dentro de `if sox_fecha`);
  corregido con `sox_fecha and …`; (2) el script de adaptación abortó en el segundo archivo (esperaba 10 ocurrencias y
  había 9) y dejó sin aplicar las adaptaciones (ii) a (v); (3) tres rojos de `test_conocibilidad` en la capa de medición
  por la base vacía del worktree (ver arriba).
- **22:40:48 → 22:40:54: segunda corrida de los diez archivos tocados: 141 passed, 12 skipped, 0 failed**
  (`evidencia/pytest_tocados_worktree.txt`).
- **22:41: diff completo** (modificados + nuevos) en `evidencia/diff_16_1.diff`, sha256
  `869fdf47d8d9a8cfb79bb9018c9f7724fa7c690af0f3da96b0262ddf5a794c18`; `git diff --stat`: 9 archivos, +386 −82, más 1141
  líneas en los cuatro tests nuevos. Huellas de los módulos en el worktree: `snapshot.py e1617af9…`, `senales.py
  494a8a4d…`, `mki_vigia.py c1bc7ba8…`, `mki_noticias.py e558b4d5…`.
- **22:41: suite completa del worktree con cambios** lanzada en segundo plano; **22:42: `auditor-lookahead`** lanzado sobre
  los bloques A, C y la parte del B que lee `senales.db`, con ocho preguntas obligatorias.
- **22:43: tarjeta §80** en `espera_firma.md` (cinco elecciones de agente y dos hechos de entorno).

---

## 2. Qué hace cada bloque (y qué elección de agente lleva; tarjeta §80)

**A. `snapshot.py` — guarda de frescura (§93.8 b).** Después de la guarda (b) de §90.1, cuya condición no cambia: si
`sox_fecha` existe, es distinta de `hoy` (`date.today()`, la misma fecha que lleva el snapshot) y `calendarios.es_sesion
("XNYS", hoy)`, no se sella. Compara dos FECHAS; sin margen horario, sin reloj (§72 C.2). Fin de semana y feriado de
XNYS no son sesión: ahí sella como antes (D.2 sigue sin firmar; el 7-sep histórico sigue siendo legítimo). `sox_fecha`
vacío: sigue sellando por su rama (elección 4 de §80). Las dos negativas imprimen la línea fija `NEGATIVA DECLARADA
[codigo] fecha=… sox_fecha=…: motivo` (`MARCA_NEGATIVA`, `NEGATIVA_SESION_ABIERTA`, `NEGATIVA_FRESCURA`) y devuelven
`negativa` en el dict; ninguna entra al bucle de reintentos de `main()` (el motivo no es «sin datos de mercado»).
`main()` imprime además la cuenta de excluidas del verificador de puntaje (bloque C).

**B. `mki_vigia.py` — un solo toque.** (1) `_negativa_declarada_en_log(hoy)` lee la última cabecera de `snapshot.log` y
busca en ese bloque la línea fija con `fecha=hoy`; `chequear_snapshot(hoy)` devuelve `(True, "snapshot: NO sellado por
negativa declarada [codigo]: motivo")` —no es falla— y `chequear_descarga(hoy)` acompaña; `revision(hoy)` (el cuerpo de
`main()`, separado para poder probarlo en fin de semana) manda un mensaje 🟡 propio con la negativa, «no es falla» y el
anuncio del re-chequeo, deja el marcador con la negativa, y `rechequeo()` cierra el caso: retractación si hay sello,
«caso cerrado… no habrá retractación» con la hora real si no (consume el marcador; elección 3 de §80); con proceso vivo
no cierra. Sin negativa, todo sigue como en 5.0.1. (2) `chequear_ancla_temporal` prueba `av == ts` (texto de siempre) Y
`av > ts` por instantes con zona (texto propio: «available_at POSTERIOR a timestamp_utc … inversión»), y nombra las dos si
coinciden. (3) `chequear_guarda_puntaje(hoy)`, séptimo chequeo del pase: `mode=ro`, predicado del verificador sin el
filtro de 7 días (elección 2), informa «N fila(s) invertida(s) fuera de verificacion_puntaje (fecha: n, …); M dentro»;
alerta si M > 0 o si alguna fecha está dentro de `DIAS_INVERSION_RECIENTE = 10` días (elección 1). Errata «launchd»
corregida en el mensaje del proceso colgado. (D) `resultado == "error_analisis"` del ledger es falla, con tipo y lote.

**C. `senales.py`.** `verificar_puntaje_pendientes` devuelve `{"verificadas", "excluidas", "fechas_excluidas"}`; qué
escribe no cambia (ni `verificacion_puntaje` ni `estado`); la línea de AVISO sigue igual. `verificar_pendientes`
propaga. Llamadores: `snapshot.py:main` (adaptado) y `app.py:828` (ignora el retorno; no se toca).

**D. `mki_noticias.py`.** En el `except` del lote: `error = {error_tipo: type(e).__name__, error_lote, error_http:
status_code si es int}`; `resultado` = `freno_presupuesto` / `error_analisis` / `ok`; el texto de la excepción sigue
yendo sólo a `noticias.log`, enmascarado. `RESULTADO_ERROR_ANALISIS = "error_analisis"`.

---

## 3. Suite del worktree con cambios y comparación por conjuntos

**22:41:36 → 22:48:48: 19 failed, 1004 passed, 84 skipped, 1 xpassed, 67 warnings, 6 errors, 431,76 s**
(`evidencia/suite_worktree_con_cambios.txt`). Diferencia de conjuntos contra la línea base de HEAD puro (§1): **los 25
rojos son exactamente los mismos 25** (`diff` de las listas `FAILED`/`ERROR` ordenadas: vacío). Rojos que aparecen SÓLO
con el cambio: **ninguno**. Verdes nuevos: +65 (1004 − 939), que son los cuatro archivos de tests nuevos y lo adaptado.
El `1 xpassed` es el mismo de la 16a (`test_epistemico.py`, no estricto, atribuido a artefactos ausentes); en el árbol
real se espera `1 xfailed`. Los 25 rojos del worktree siguen siendo los de bases ausentes (api, dinero, readme,
cifras_arbitro, linea_base, frontend_estatus), ninguno de los cuales nombra `snapshot`, `verificar_puntaje`, `vigia` ni
`noticias` en su primera línea `E`. Por el criterio §95.5, **juzga la suite del árbol real después de aplicar (§5).**

## 4. Dictamen del auditor y aplicación al árbol real (corte de método)

### 4.1 Dictamen (`dictamen_16_1/auditor_16_1.md`, 22:42:41 → 23:00:27): APLICABLE CON EXIGENCIAS

Por bloque: **A APLICABLE CON EXIGENCIAS, C APLICABLE, B APLICABLE CON EXIGENCIAS**, D sin objeciones. **Ninguna fuga
de valor futuro demostrada.** Lo que midió: 308 sesiones de XNYS barridas con `exchange_calendars` hasta fin de 2027 a
las 18:15 de Chile (márgenes 15 min × 125, 75 × 73, 135 × 107, 195 × 3, ninguno ≤ 0); por el código real, 250 sesiones
con fuente fresca → sella en todas, 250 con fuente atrasada → niega en todas; 40 disparos de recuperación a las 08:00 →
40 negativas `insumo_no_fresco`; historia real en `mode=ro`: 53 snapshots con `sox_fecha`, 52 en día de sesión, **0 con
`sox_fecha ≠ fecha` en día de sesión** (la cifra que pedía el encargo; antes: 0 de 44 al 29-sep); predicado B.3 sobre la
base real: 24 invertidas, todas del 28-sep, 24 fuera y 0 dentro, idéntico al conjunto del verificador en la ventana común,
y la ventana de 10 días NO dispara el lunes 12-oct (límite 2-oct); `test_motor.py` en el worktree, verde. Cuatro
bloqueantes y nueve recomendadas. Zona ciega que vale la pena repetir: la guarda decide con lo que la fuente sirve EN EL
INSTANTE y eso no es reproducible después (el 28-ago sellado con `sox_fecha` 28-ago no existe hoy en la descarga).

**Las tres bloqueantes de código, atendidas entre las 23:03 y las 23:11 en el mismo worktree:**
- **BL1** (F1): `calendarios.es_sesion` estaba sin proteger en el camino de sellado; una excepción ahí se llevaba el
  verificador, los respaldos y el epílogo del vigía. Dirección elegida y declarada (tarjeta §80, elección 6): degradar
  como HEAD —se sella, con `AVISO frescura` en `snapshot.log`—, la misma de la rama del `except` de `cierre_utc`. Test
  `test_si_el_calendario_falla_se_sella_como_antes_con_aviso`.
- **BL2** (F2): un `available_at` no parseable lanzaba `ValueError`, que subía por `revision()` hasta el `except` del
  módulo: el vigía moría MUDO. Ahora `_instante` devuelve `None` ante texto ilegible; `chequear_ancla_temporal` y
  `chequear_guarda_puntaje` lo declaran como FALLA con texto propio («ILEGIBLES»), y la cadena vacía se trata como «sin
  dato», igual que el verificador (la única diferencia de predicado que el auditor nombró). El predicado quedó en un
  helper `_inversiones_puntaje(ruta_db)` que devuelve fuera/dentro/ilegibles por fecha. Tests: dos por chequeo.
- **BL3** (F3): el cierre de caso de las 20:30 consumía el marcador y un sello manual posterior no podía retractar un
  mensaje publicado (el defecto que 5.0.2 prohibió). Ahora el marcador QUEDA, el texto dice «caso cerrado por hoy… si un
  sello manual llegara más tarde, snapshot.py avisará», y hay un test de la secuencia completa (20:30 sin sello →
  sello manual → `_epilogo_vigia` retracta). La elección 3 de §80 se reescribió en consecuencia.
- **Recomendadas hechas de paso:** R1 (test que ata los dos predicados sobre la misma siembra: `excluidas`/
  `fechas_excluidas` del verificador = conjunto del vigía filtrado a 7 días), R2 (la referencia del test de conducta de
  escritura es el commit `864606c`, no `HEAD`: discriminante también después del commit), R4 (la cifra del comentario de
  `snapshot.py`: «0 de 44 al 29-sep, 0 de 52 al 10-oct», no «0 de 45»), R8 (`test_el_pin_de_fecha_es_una_sesion_de_xnys`).
  **No hechas**, para decidir dónde van (final de §80): R3, R5, R6, R7, R9.
- **BL4**: la suite del árbol real con las bases, §5.

**23:11:43 → 23:11:50: los diez archivos tocados en el worktree, con las exigencias: 149 passed, 12 skipped, 0 failed**
(`evidencia/pytest_tocados_worktree.txt`, regenerado). **23:11:55: evidencia de HEAD regenerada con los tests FINALES**
sobre la copia `head161` del auditor (los cuatro módulos verificados iguales a HEAD por sha256): **24 failed, 7 passed, 1
skipped, 1 error de recolección** (`evidencia/pytest_nuevos_sobre_HEAD.txt`; reemplaza la versión no final que el
auditor señaló). Los 7 que pasan en HEAD son los controles y las dos fijaciones de conducta de escritura.

El artefacto aplicado NO es byte a byte el auditado (como en la 16b, O1): el delta entre `diff_16_1.diff` (auditado,
`869fdf47…`) y `diff_16_1_final.diff` (aplicado, `93c5fec1a47b5b2fdf14e6e3393ae54a5f5dabeafee8951d348751f741659439`)
está en `evidencia/delta_auditado_a_final.diff` (430 líneas de `diff`, que son las tres bloqueantes, R1/R2/R4/R8 y sus
tests). `git diff --stat` final: 9 archivos, +449 −83, más los cuatro tests nuevos. El auditor no volvió a pasar sobre el
artefacto final; lo lee el guardián (§6).

### 4.2 Aplicación al árbol real — **corte de método: 10-oct-2026, 23:12:48 (Chile, −03:00)**

Por copia desde el worktree (los nueve archivos modificados estaban en HEAD en el árbol real, verificado por sha256 antes
de copiar; los cuatro nuevos no existían). Un solo instante para los cuatro bloques: `stat -c '%y'` de `snapshot.py`
23:12:48.857, `senales.py` .860, `mki_vigia.py` .861, `mki_noticias.py` .864, y los nueve tests entre .866 y .880.
Huellas sha256 (primeros 16) del árbol real = worktree, los 13: `snapshot.py 3cbbecaadbe1ab0e`, `senales.py
494a8a4daf90ead4`, `mki_vigia.py 4f05097431202542`, `mki_noticias.py e558b4d5fad8d0da`, `test_conocibilidad.py
78d60502ed5b215d`, `test_guarda_puntaje.py 74ef4468116142f9`, `test_parche_guardia_ancla_temporal.py 80428b1d22ee8db9`,
`test_parche_snapshot140.py 1f9e11ec954e4113`, `test_vigia.py f8d480a67e9bceb1`, `test_frescura.py 9064640dce56700b`,
`test_puntaje_retorno.py f7b922e704c52de7`, `test_noticias_ledger.py fa9596bf935a876f`, `test_vigia_16_1.py
d3321c94c2936c99`. (Después del guardián, la E2 cambió un docstring de `test_frescura.py`: su huella final es
`1082ddc437daec58`, §6.2.) Reversión, si la suite de §5 diera un rojo que no sea de entorno: restaurar los nueve modificados
desde `git show HEAD:<archivo>` y borrar los cuatro nuevos. La evidencia del worktree se copió a
`GEMELO/resultados/dictamen_16_1/evidencia/`.

## 5. Suite del árbol real después de aplicar (BL4): VERDE

**23:13:32 → 23:21:18: 1116 passed, 5 skipped, 1 xfailed, 29 warnings, 0 failed, 464,14 s, exit 0**
(`evidencia/suite_arbol_real_despues.txt`). Contra la apertura (1042 passed, 5 skipped, 1 xfailed): **+74 verdes, 0 rojos
nuevos**, mismos 5 saltados y el mismo `1 xfailed` (no pasó a `xpassed`). Recolectados: 1122 (eran 1048): el badge
congelado `tests_recolectados` (hoy 1025 en `docs/readme/badges_congelados.json`, §90.4) queda desfasado en +97; lo
actualiza la 16-3 con el README, como ya estaba previsto. Las advertencias son las conocidas (29, las mismas de la
apertura). **23:21:18 → 23:21:27: `venv/bin/python tests/test_motor.py`: las seis funciones del motor idénticas con y sin
datos futuros en las tres fechas (2026-09-10, 2026-07-12, 2026-04-13)** (`evidencia/test_motor_anti_lookahead.txt`).
Los tests `solo_con_base` que el worktree saltaba corrieron acá sobre la base real: en particular
`test_historia_real_la_guarda_no_habria_rechazado_ningun_sello_de_dia_de_sesion` (53 sellos con `sox_fecha`, 0
rechazables) y `test_corte_de_metodo_sobre_la_historia_real` de la 16a, ahora con el retorno dict. **Orden de los hechos (O1 del
guardián):** este número se midió ANTES de redactar el acta §100, `ESTADO.md` y los §4–§8 de esta bitácora, que van en el
mismo commit; los seis archivos de tests que leen `DECISIONES.md` pasan con el acta ya escrita (104 passed, 1 skipped,
1 xfailed, medido por el guardián), y el hook pre-commit corre la suite entera con las 27 rutas stageadas: ése es el
juez final.

## 6. Cierre: guardián, exigencias atendidas, huellas al cerrar, worktrees

### 6.1 Guardián (`dictamen_16_1/guardian_cierre.md`, 23:24:00 → 00:14:08 del 11-oct): APROBADO CON EXIGENCIAS

Ningún rechazo. Verificó: archivos protegidos sin diff (`motor.py`, `universo.py`, `version.py`, `calendarios.py`,
`alertas.py`, `mki_backup.py`, `dinero/`, la sonda, `api/`, `app.py`, `backtest/`, README, `docs/`, timers); ninguna
sentencia de escritura nueva; las tres bases con las huellas de apertura después de toda la corrida; regla 10 (35
patrones de cifras retiradas) con 0 coincidencias; secretos 0; la palabra prohibida 0 en lo nuevo; actas y tarjetas puramente
aditivas (+139 y +67, −0); la identidad del artefacto (`git archive HEAD` + `git apply diff_16_1_final.diff` reproduce
los 13 sha256 del árbol real); el delta auditado → final leído por conducta, archivo por archivo, sin nada fuera de
BL1/BL2/BL3/R1/R2/R4/R8; la aritmética de la suite (1042 + 74 = 1116, 1048 + 74 = 1122, cierra exacto); las 27 rutas.
Tres exigencias documentales: **E1** los worktrees que el acta daba por podados no lo estaban; **E2**
`tests/test_frescura.py:267` reintroducía «0 de 45» sin marca de errata; **E3** el acta decía 1141 líneas de tests
nuevos (conteo de las 22:38) donde lo aplicado tenía 1238. Observaciones: O1 (el verde archivado precede a la
documentación que va en el mismo commit; midió que los seis tests que leen `DECISIONES.md` pasan con el acta §100:
104 passed, 1 skipped, 1 xfailed), O2 (el auditor no volvió a pasar sobre el artefacto final; lo leyó él), O3 («0 de
45» sobrevive en tres lugares preexistentes: `DECISIONES.md:9716`, `espera_firma.md:2447` y `:2715`; no se tocan; la
expresión no está en `GEMELO/cifras_retiradas.md`), O4 (regla 12: las cifras nuevas son censos, no estimadores), O5
(higiene: `test_vigia_16_1.py` apunta a `data/no_existe.db` real para forzar el error de apertura; `ESTADO.md` en 50
líneas justas).

### 6.2 Exigencias atendidas, con una pausa de sesión declarada

- **E1, 00:18:01 del 11-oct:** `git worktree remove --force wt161` y `git worktree prune`; `git worktree list` muestra sólo
  el árbol real. Hecho antes de escribir este párrafo; el acta §100.5 (iv) lleva la hora.
- **Pausa de sesión:** la llamada siguiente a la de las 00:18:01 leyó `date` a las **14:49:12 del domingo 11-oct**. La
  sesión del orquestador estuvo detenida ~14,5 h entre dos llamadas (el mismo mecanismo de la 16b). Sin consecuencia
  sobre el encargo, que no tiene reloj duro, ni sobre la máquina: ningún job `mki-*` disparó (domingo; los ocho timers
  siguen con su último disparo del 9 y 10-oct), y las tres bases siguen con las huellas de apertura (abajo). Queda
  declarado porque las horas de E2/E3 son del domingo a la tarde.
- **E2, 14:49:12:** el docstring de `test_historia_real_la_guarda_no_habria_rechazado_ningun_sello_de_dia_de_sesion`
  cita «0 de 45» con la errata fechada en la misma línea (0 de 44 al 29-sep sobre 45 con `sox_fecha`; 0 de 52 sobre 53
  al 10-oct). Sólo docstring; `tests/test_frescura.py` → **13 passed** (14:49:12 → 14:49:17). No se repitió la suite
  completa por un docstring: el hook pre-commit la corre entera (O1/O6 del guardián).
- **E3:** el acta §100.3 da las tres cifras (1141 escritas antes del código; 1238 tras el auditor; 1240 tras E2).
- **Huellas que E2 movió, recomputadas en el árbol real:** `tests/test_frescura.py` ahora `1082ddc437daec58` (era
  `9064640dce56700b` en §4.2), 268 → 270 líneas; los cuatro tests nuevos suman 1240. `diff_16_1_final.diff` regenerado
  desde el árbol real (el worktree ya no existe): sha256
  `e22f806030d739960e2b75f9447a93789f7f05d09193ecf6c80da5b7c178c2af` (era `93c5fec1…`, el que el guardián verificó
  byte a byte contra el árbol; la única diferencia es el docstring de E2); `delta_auditado_a_final.diff` 436 líneas
  (eran 430). Los otros doce sha256 de §4.2 no cambian.

### 6.3 Huellas de las tres bases al cerrar (14:49:17 del 11-oct)

`senales.db 98a048de1dbd6d8c…`, `noticias.db 1829b61b0233b03e…`, `dinero/sello_dinero.db 2a016c523adf6542…`:
**idénticas a las de apertura (§0.2)**, después de la corrida entera, las suites, el auditor y el guardián. Ninguna
base se escribió. `git status --short`: 22 entradas, las mismas que vio el guardián.

### 6.4 Lo que esta corrida NO hizo, para que no viva en la memoria de nadie

Las recomendadas R3, R5, R6, R7 y R9 del auditor (final de §80); F4 y S1/S2 (acta §100.4); C.6 (ii) del inventario
(hora real en el rechequeo sin negativa, §80.5); O5 del guardián; el badge `tests_recolectados` (+97, a la 16-3). No se
tocó nada fuera del encargo §1. Las tres copias de bases al worktree quedaron denegadas (§0.5).

## 7. Predicciones falsables para el lunes 12-oct-2026 (escritas antes de cerrar; coinciden con las del auditor)

Supuesto: el commit de Nicolás entra antes de las 17:50 del lunes (si no, el árbol real igual lleva el código aplicado
—los jobs leen el árbol, no el commit— y las predicciones valen igual; sólo cambia que el backup de las 18:40 encontrará
el árbol sucio, lo que `mki_backup.py` tolera porque commitea sólo `data/backups/` por pathspec). El 12-oct es sesión de
XNYS (verificado con `calendarios.es_sesion`), holgura 75 min.

**Snapshot 18:15 (`data/snapshot.log`, entrada `[2026-10-12T21:15:0x+00:00] snapshot.py (origen=programado…)`):**
1. NO aparece `NEGATIVA DECLARADA` en el bloque (la fuente sirve el SOX del 12-oct, como las últimas 52 sesiones de día
   hábil). Si apareciera `[insumo_no_fresco]`, es un falso rechazo y hay que medir por qué `sox_fecha` quedó atrás.
2. Aparece exactamente `  verificador puntaje: N verificadas, 24 excluidas por conocibilidad (fechas: 2026-09-28)`,
   precedida de la línea `AVISO verificador puntaje: 24 fila(s) …` de la 16a (no la reemplaza). `N` depende de la red.
3. `snapshots` del 12-oct con `sox_fecha = 2026-10-12`; 8 filas de predicción con `available_at =
   2026-10-12T20:00:00+00:00` y `timestamp_utc` ≈ 21:15 UTC.

**Vigía 19:00 (`data/vigia.log`):**
4. Siete líneas de chequeo, en este orden: snapshot sellado, descarga 28/28, noticias (`freno_presupuesto` o `ok`;
   NO `error_analisis`), reporte, backup, `OK  ancla temporal: 8/8 filas con cierre del SOX`, y la nueva:
   `  OK  guarda puntaje: 24 fila(s) invertida(s) fuera de verificacion_puntaje (2026-09-28: 24); 0 dentro (residuo
   conocido, sin fecha nueva)` (cadena reproducida hoy contra la base real con `hoy = 2026-10-12`, dos veces).
5. `todo OK — sin alerta`; no existe `data/vigia_pendiente.json`; **20:30:** `sin alerta pendiente de hoy`.

**Noticias 17:50 (`data/costos_ia.log`):** la línea del 12-oct trae `resultado` `freno_presupuesto` u `ok`, sin claves
`error_*`; si la API fallara, traería `error_analisis` + `error_tipo` + `error_lote` y el vigía diría FALLA.

**Qué falsaría la corrida:** `NEGATIVA DECLARADA` con la fuente al día; `fecha NUEVA con inversión`; `0 dentro` distinto
de 0; una cuenta de excluidas distinta de 24 o con otra fecha sin que se haya sellado una fila nueva; un `ERROR no
manejado` en `vigia.log`.

**Consulta exacta para Nicolás, martes 13-oct en la mañana, sólo lectura:**

```bash
cd ~/dev/mki-terminal && grep -n "NEGATIVA DECLARADA\|verificador puntaje:" data/snapshot.log | tail -3
grep -n "guarda puntaje\|ancla temporal\|NEGATIVA\|todo OK\|ERROR" data/vigia.log | tail -6
tail -1 data/costos_ia.log | cut -c1-200
venv/bin/python - <<'EOF'
import sqlite3
s = sqlite3.connect("file:senales.db?mode=ro", uri=True)
print("snapshot 12-oct (fecha, sox_fecha, ts):", s.execute("SELECT fecha, sox_fecha, timestamp_utc FROM snapshots WHERE fecha='2026-10-12'").fetchall())
print("invertidas dentro de verificacion_puntaje (se espera 0):", s.execute("""SELECT COUNT(*) FROM verificacion_puntaje v JOIN senales_ticker t
   ON t.fecha = v.fecha_senal AND t.ticker = v.ticker WHERE t.available_at > t.timestamp_utc""").fetchone()[0])
EOF
```

## 8. Lista exacta de archivos para el commit (una ruta por línea; el commit lo hace Nicolás)

```
DECISIONES.md
ESTADO.md
snapshot.py
senales.py
mki_vigia.py
mki_noticias.py
tests/test_conocibilidad.py
tests/test_guarda_puntaje.py
tests/test_parche_guardia_ancla_temporal.py
tests/test_parche_snapshot140.py
tests/test_vigia.py
tests/test_frescura.py
tests/test_puntaje_retorno.py
tests/test_noticias_ledger.py
tests/test_vigia_16_1.py
GEMELO/resultados/bitacora_16_1.md
GEMELO/resultados/espera_firma.md
GEMELO/resultados/dictamen_16_1/auditor_16_1.md
GEMELO/resultados/dictamen_16_1/guardian_cierre.md
GEMELO/resultados/dictamen_16_1/evidencia/diff_16_1.diff
GEMELO/resultados/dictamen_16_1/evidencia/diff_16_1_final.diff
GEMELO/resultados/dictamen_16_1/evidencia/delta_auditado_a_final.diff
GEMELO/resultados/dictamen_16_1/evidencia/pytest_nuevos_sobre_HEAD.txt
GEMELO/resultados/dictamen_16_1/evidencia/pytest_tocados_worktree.txt
GEMELO/resultados/dictamen_16_1/evidencia/suite_worktree_con_cambios.txt
GEMELO/resultados/dictamen_16_1/evidencia/suite_arbol_real_despues.txt
GEMELO/resultados/dictamen_16_1/evidencia/test_motor_anti_lookahead.txt
```

(27 rutas.) `DECISIONES.md` lleva las actas §98 y §99 (anexadas por Nicolás antes de lanzar) y la de cierre §100.
**No incluye** `data/backups/sello_dinero.csv`, `data/backups/sello_dinero_ext/ext_2026-10-09.{csv,meta.json}` ni
`data/sonda_cierre.csv` (los commitea el backup del lunes 18:40, como siempre). El hook pre-commit corre la suite (~8
min): con los 27 archivos stageados el resultado esperado es el de §5. Conviene commitear el domingo o el lunes antes de
las 17:50: entre 17:50 y 20:30 de un día hábil el hook lo rechaza (regla de la casa).
