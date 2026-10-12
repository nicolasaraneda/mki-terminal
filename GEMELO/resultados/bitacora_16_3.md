# Bitácora de la corrida 16-3 — la fuente única de las cifras publicadas, el README, la higiene de tests, R9, la pantalla de `/sellos` y el parche de `dinero/` (actas §93.4, §93.4-bis ii, §93.11, §93.12, §95.4, §99.5, §99.6, §99.8, §102.2, §102.4, §102.6)

> Domingo 11-oct-2026, de noche, con Nicolás presente. Encargo: `~/encargo.md` (escrito por el asistente del chat a las
> 15:40 sin leer el código; primer `date` de la corrida: 19:26:44). Orquestador: Fable 5.1, esfuerzo alto, elegidos al
> arrancar. Horas de Chile leídas de `date` (las que vienen de una salida de pytest o de un script llevan su propia
> marca). Nada se pusheó, nada se commiteó, nada se firmó, nada se operó; ninguna unidad de systemd se tocó; el sellador
> real no se corrió; las tres bases sólo en `mode=ro`; `motor.py`, `universo.py`, `snapshot.py`, `senales.py`, el vigía,
> la sonda, `mki_backup.py`, `mki_noticias.py`, `.env`, `corredor/` y los timers intactos; `dinero/` del árbol real
> intacto (su cambio va como parche, §4). La lista de permisos de §99.7 rigió y ningún permiso denegado se rodeó (dos
> denegaciones, §0.5).

**PRIMERA LÍNEA (estado al cierre): la 16-3 está APLICADA al árbol real (corte de método 20:59:44) y SIN commitear;
suite completa del árbol real con todas las bases después de aplicar: 1207 passed, 8 skipped, 1 xfailed, 0 failed (§6); 50
rutas para el commit (§9), antes de las 17:50 del lunes.** Desde el reporte de Telegram del lunes 18:25, la API y el
dashboard, las cifras de acierto salen de `backtest/linea_base.py` y excluyen las 8 filas del 28-sep (track record 30 d:
n 149 → 141 hoy; el lunes, 133 + k). El parche de `dinero/` queda como archivo, NO aplicado (`version_reglas_16_3.diff`,
sha256 `5acdb3e2…`; tarjeta §89). Tres dictámenes: auditor A APLICABLE CON EXIGENCIAS (cinco bloqueantes atendidas),
auditor C APLICABLE CON EXIGENCIAS (tres atendidas), curador RECHAZA sobre el estado de las 21:01 (tres bloqueantes y seis
observaciones atendidas, una declarada); guardián: §8.1. Tarjetas nuevas §82 a §89; acta de cierre §104.

---

## 0. Reloj, orientación y lecturas de sólo lectura

### 0.1 Reloj y timers (19:26:44 y 19:28:23)

`date`: `Sun Oct 11 19:26:44 -03 2026`. `git log --oneline -4`: `ad4b829` arriba (corrida 16-2 y actas §101 y §102,
camino T y B2 aplicados a mano), como el encargo exigía. `systemctl --user list-timers --no-pager`, sólo `mki-*`:

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

Ningún job `mki-*` dispara antes del lunes 12-oct a las 17:50 (confirmado otra vez a las 20:15: los mismos NEXT). El
plazo del encargo para aplicar al árbol real es el lunes a las 16:30; esta corrida aplica el domingo de noche, a más de
20 horas de cualquier disparo.

### 0.2 Árbol de git y bases (19:28:23 y 19:30:08)

`git status --short`: `M DECISIONES.md` (el acta §103 que Nicolás anexó antes de lanzar, +16 líneas), `M
data/backups/sello_dinero.csv`, `M data/sonda_cierre.csv`, `?? data/backups/sello_dinero_ext/ext_2026-10-09.{csv,meta.json}`
(lo commitea el backup del lunes). Nada de `.claude/`. Rama `main`. Un solo worktree (el árbol real).

Huellas de las tres bases al abrir (19:30:08; `sha256sum` y `stat`):

```
98a048de1dbd6d8c6f53821ad2e879c307cc1d536c64e0dfbb79f90b2f72ced8  senales.db            663552  2026-10-09 18:15:24.162450663 -0300
1829b61b0233b03e493939c5d4b8b56c803a0c6965042d8c9006cc4362336d4c  noticias.db         10498048  2026-10-09 18:06:41.685782190 -0300
2a016c523adf6542d5b44dd081c54bfa9bc54456c8c554cd6b69772f6585a636  dinero/sello_dinero.db 647168  2026-10-10 00:30:04.789922944 -0300
```

### 0.3 Suite completa al abrir (árbol real, HEAD `ad4b829` + acta §103, todas las bases)

19:30:08 → 19:38:16: **1151 passed, 8 skipped, 1 xfailed, 29 warnings, 0 failed, en 487,00 s** (`EXIT 0`). Igual al
número que el encargo esperaba. Salida en `dictamen_16_3/evidencia/suite_arbol_real_apertura.txt`.

### 0.4 Lo leído antes de escribir una línea de código (encargo §0.1 y §0.3)

`DECISIONES.md` §93 a §103 (10.108 líneas; las actas 93 a 103 ocupan las líneas 9692 a 10108 de ese estado del
archivo); `espera_firma.md` §73, §74, §76, §77, §78, §79, §80 y §81; `dictamen_15/informe_bloque1.md` (censo de
consumidores) y `auditor_bloque1.md` (B1: 8 de 160 filas invertidas en la ventana de 30 días al 29-sep);
`dictamen_16a/auditor_guarda_puntaje.md` (punto 1 de §78: `linea_base.py` no contiene «puntaje»; residuo de 32 filas con
`available_at == timestamp_utc` y 18 con NULL, que la regla no alcanza por diseño); la bitácora 16-1 (§0.5: copias de
bases denegadas; hecho (ii) de §80); la bitácora 16-2 (formato, receta, §9). Y el código: `senales.py:513-700` (las
seis), `backtest/linea_base.py` (cabecera, `cargar`, conocibilidad, dedup), `alertas.py:255-300`, `api/main.py:520-840`,
`app.py:820-840` y `:905-1690`, `mki_vigia.py:40-140`, `snapshot.py:55-110` y `:185-250` y `:336-395`,
`dinero/sello_dinero.py` entero, `tests/conftest.py`, `tests/test_api.py`, `tests/test_reporte.py`,
`tests/test_conocibilidad.py:540-600`, `tests/test_sello_dinero.py:618-760`, `tests/test_readme.py:100-235`,
`scripts/generar_readme.py`, `docs/readme/README.en.tmpl.md:386-412`, `frontend/src/vistas/SellosDinero.tsx`,
`frontend/src/lib/tipos.ts:584-645`, `api/CONTRATO.md` (§/api/hoy, /api/aperturas, /api/historial, /api/dinero/sellos,
enmienda 16-2).

**Censo de consumidores de las seis métricas (HEAD `ad4b829`, línea por línea; encargo §0.3):**

| función de `senales.py` | `alertas.py` | `api/main.py` | `app.py` |
|---|---|---|---|
| `metricas_apertura(dias=30)` | :278 (reporte, «Track record 30d») | :536 (`/api/hoy` `track_record`), :823 (`/api/historial` `metricas`) | :914 (tarjeta del hero, Hoy), :1583 (Historial) |
| `calibracion_intervalos()` | :287 («Cobertura del intervalo 80%») | :561 (`/api/aperturas` `calibracion`), :825 (`/api/historial`) | :1419 (badge de calibración), :1601 |
| `evolucion_aciertos_apertura()` | — | :806 (`/api/historial` `evolucion`) | :1618 (gráfico) |
| `ultimas_predicciones_apertura(limite)` | — | :807 (`limite=100`) | :1631 (`limite=50`) |
| `verificaciones_detalle()` | — | :760 (`_estadistica_track_record`: `wilson`, `calibracion_curva`, `por_region`, `por_regimen`) | — (ninguno) |
| `analisis_puntaje_ia(dias=90)` | — | :831 (`/api/historial` `puntaje_ia`, sin `datos`) | :1661 (tres métricas y el scatter) |

Nadie más las llama fuera de tests (`grep` sobre `*.py`; `cifras.py` y `scripts/generar_readme.py` leen de `lb.cargar()`).
En tests las nombran `tests/test_api.py:150-163` (paridad) y `:263,:288` (`verificaciones_detalle`), y
`tests/test_reporte.py:109,:112`.

**Qué entregaba `cargar()` y qué le faltaba para servir cada una:** `cargar()` devuelve `fecha, ticker,
apertura_estimada_pct, gap_pct, acierto_gap, error_gap_pp, retorno_real_pct, confianza_r2, intervalo80_pp, n_muestra,
beta, exchange, sesion_objetivo, available_at, regimen, sox_usado_pct, sox_fecha` (descarta `timestamp_utc` antes de
devolver, H4 de la 15), exige `gap_pct IS NOT NULL` siempre, no tiene ventana de días, ordena por `(fecha_senal,
ticker)` y **deduplica por defecto** (`DEDUP_OFICIAL = True`). Le faltaban: `acierto_direccion` y `error_pp` (el
retorno de sesión de `metricas_apertura`, `evolucion`, `ultimas`); `timestamp_utc` en la salida (`Emitida (UTC)` de
`ultimas`); `senales_ticker.apertura_estimada_pct` (el estimado SELLADO que usa `calibracion_intervalos`; MEDIDO igual a
`v.apertura_estimada_pct` en 490 de 490 filas, pero es el que la definición nombra); la ventana `date('now', '-N
days')` en SQL (30 y 90 días); las filas con `gap_pct` NULL (que `ultimas` no filtra; hoy 0 en la base); la rama SIN
deduplicar (encargo §1: la única diferencia permitida es la conocibilidad); y toda `verificacion_puntaje`
(`analisis_puntaje_ia`, §99.6: `linea_base.py` no contenía la palabra «puntaje»). De ahí las dos funciones hermanas
`cargar_vivas()` y `cargar_puntaje_vivo()` en el mismo módulo, que pasan por la misma `excluir_sin_conocibilidad()`
(§2).

### 0.5 Worktrees y permisos (19:35:40 a 19:40)

- `git worktree add --detach …/scratchpad/wt163 HEAD` (trabajo), `wt163_ctrl` (control HEAD puro), `wt163_diag`
  (diagnóstico del Bloque D) y, a las 20:0x, `wt163_dinero` (el parche de `dinero/`, aparte para que la suite del
  worktree de trabajo no lo arrastre). En los cuatro: `GEMELO/cache` enlazado al del árbol real y las corridas selladas
  gitignoradas de `backtest/resultados/` copiadas (permitido, como en la 16-1).
- **`cp senales.db …/wt163/` DENEGADO** (una vez, la forma exacta de la lista de §99.7; no se insistió con las otras dos
  bases ni se rodeó). Rige §95.5: juzga la suite del árbol real con todas las bases, con control sobre HEAD puro en el
  worktree (§4). Lectura del asistente del 11-oct (§102.3), PROBABLE: la regla `Edit(**/*.db)` del proyecto gana sobre
  el `allow`.
- Segunda denegación (20:08): `rm` de dos archivos que **mi propio test** había dejado en `data/backups/sello_dinero_ext/`
  DEL WORKTREE (`ext_2026-09-14.no_verificable.{csv,meta.json}`; §3 D, hallazgo). La regla protege `data/backups/**` y
  no distingue la copia del worktree. No se rodeó: los archivos quedan hasta el `git worktree remove` del cierre y el
  test de huérfanos de ese worktree los cuenta como rojo CONOCIDO (§4). El árbol real no los tiene (`ls` 19:51: 0
  archivos `.no_verificable` en `dinero/datos/sello/` y en `data/backups/sello_dinero_ext/`).

---

## 1. Método, con horas

| hora | qué |
|---|---|
| 19:26:44 | `date`; lectura del encargo entero. |
| 19:28:23 | `git log`, `git status`, `git branch`, `git worktree list`, `list-timers`. |
| 19:30:08 | huellas de las tres bases; suite de apertura lanzada en el árbol real (termina 19:38:16). |
| 19:30 a 19:38 | lectura (§0.4), en paralelo con la suite. |
| 19:35:40 | worktrees `wt163` y `wt163_ctrl`. |
| 19:38:42 | **medición «antes»** sobre la base real en `mode=ro`, replicando el SQL exacto de las seis (`evidencia/medir_antes.py` → `medicion_antes.txt`). |
| 19:39 | `cp senales.db` al worktree: denegado. |
| 19:40:32 → 19:48:40 | suite del worktree **HEAD puro** sin bases (control §95.5): 19 failed, 1044 passed, 90 skipped, 1 xpassed, 67 warnings, 6 errors (`evidencia/suite_worktree_HEAD_puro.txt`). |
| 19:40 → 19:48:41 | diagnóstico del Bloque D en `wt163_diag`: la suite con un plugin que anota qué test crea cada base (`evidencia/detector_bases.py`, `creadores_de_bases_en_worktree_sin_bases.tsv`). |
| 19:48:41 | `tests/test_fuente_unica_16_3.py` escrito; corrido sobre HEAD: **24 failed, 2 passed, 1 error** (`evidencia/pytest_fuente_unica_sobre_HEAD.txt`). Por causa: 18 por símbolo ausente (`lb.cargar_vivas` y las seis no existen en HEAD), 3 por su propia aserción contra código que SÍ existía (la API sirve la fila invertida; el reporte la cuenta; los consumidores llaman a `senales.*`), 3 de superficie (`MINIMO_OBSERVACIONES`, consumidores sin `linea_base`); los 2 verdes son controles. |
| 19:50 a 19:53 | código del Bloque A en `backtest/linea_base.py`; migración de `alertas.py`, `api/main.py`, `app.py`; adaptación de `tests/test_api.py` y `tests/test_reporte.py`. |
| 19:53:46 | **medición «después»** con las funciones nuevas del worktree sobre la base real (`evidencia/medir_despues.py` → `medicion_despues.txt`), más el efecto de la deduplicación (tarjeta §82). |
| 19:55 a 20:02 | el test de la API marcado `red` (el `meta` del envelope pide el régimen al motor: Yahoo); comentario del módulo sin «28-sep» (`test_la_exclusion_esta_activa_por_defecto_y_no_nombra_fechas` lo prohíbe); Bloques D, E y F escritos (19:59:33; `tsc --noEmit -p tsconfig.app.json`: exit 0). |
| 20:01:45 → 20:02:33 | tests nuevos + archivos tocados en el worktree: 290 passed, 10 failed, 6 errors; de los rojos, 8 son del control (sin bases) y 2 propios (§3 D), corregidos a las 20:11. |
| 20:04 | `auditor-lookahead` lanzado sobre el Bloque A; enmienda 16-3 de `api/CONTRATO.md`. |
| 20:09:04 | `tests/test_version_reglas_16_3.py` escrito en `wt163_dinero` y corrido sobre HEAD: **10 failed, 3 passed, 1 skipped** (`evidencia/pytest_version_reglas_sobre_HEAD.txt`). |
| 20:09 a 20:14 | código del parche de `dinero/`; tests del riel en el worktree: 117 passed, 3 failed (2 del control; 1 propio, un test que mezclaba dos escenarios en una carpeta: partido en dos, 14 passed, 1 skipped a las 20:14:22). |
| 20:14:22 | `version_reglas_16_3.diff` generado (405 líneas; sha256 `f164b232…`); `git apply --check` limpio sobre HEAD puro y sobre el árbol real. Suite completa del worktree de trabajo lanzada (termina en §4). |
| 20:16 | `auditor-lookahead` lanzado sobre el parche de `dinero/`. |
| 20:19 | receta `version_reglas_16_3.md`; tarjetas §82 a §89; esta bitácora. |
| 20:22 a 20:30 | borrador de la bitácora, guion de aplicación, `ESTADO.md`, borrador del acta. |
| 20:24:50 | dictamen del auditor A (§5.1); 20:31 a 20:43: las cinco bloqueantes atendidas (B3 medido en HEAD puro y en el árbol real: preexistente). |
| 20:35:24 | dictamen del auditor C (§5.2); 20:43 a 20:48: B1 corregida en código y test, diff regenerado (`5acdb3e2…`), rojos sobre HEAD retomados, preflight de R4 en HEAD. |
| 20:51:31 → 20:59:06 | tercera suite del worktree con el código final (§4). |
| **20:59:44** | **aplicación al árbol real** (§6); 21:00:01 → 21:00:22 badges, README, `tsc`, `test_motor.py`. |
| 21:01:21 → 21:09:42 | **suite completa del árbol real: 1207 passed, 8 skipped, 1 xfailed, 0 failed** (§6). |
| 21:01:24 → 21:12:57 | `curador-epistemico` (§5.3); 21:14 a 21:22: bloqueantes y observaciones atendidas, README regenerado, 35 tests en verde. |
| 21:22 | acta §104 anexada a `DECISIONES.md` (línea 10110); `ESTADO.md` a 50 líneas; esta bitácora cerrada salvo §8. |
| [cierre] | `guardian-constitucion`, exigencias, huellas finales, worktrees fuera (§8). |

---

## 2. Tabla «antes y después» de cada cifra publicada (encargo §1), base real en `mode=ro`, 11-oct-2026 19:38:42 (antes) y 19:53:46 (después); `date('now')` de SQLite = 2026-10-11

«Antes» = el SQL exacto de `senales.py` (HEAD) replicado en `mode=ro`; «después» = las funciones nuevas de
`backtest/linea_base.py` del worktree, apuntadas a la base real. **La única diferencia en las seis son las 8 filas del
28-sep-2026 con `available_at` (20:00Z) posterior a `timestamp_utc` (17:42:58Z)**, que la regla de conocibilidad retira.

| cifra publicada | dónde | antes | después | diferencia, fila por fila |
|---|---|---|---|---|
| `metricas_apertura(30)` n | Telegram, `/api/hoy`, `/api/historial`, dashboard | 149 | **141** | las 8 del 28-sep (ventana desde 2026-09-11) |
| gap: % aciertos / MAE pp | ídem | 62,4 / 3,95 | **63,8 / 4,07** | de las 8, acierto_gap 3 (000660.KS, 005930.KS, 4063.T) y 5 errores (2330.TW gap 0,00; 3436.T 2,32; 6857.T 0,27; 8035.T 4,37; IFX.DE 2,35); sus errores de gap: 0,58, 0,51, 0,53, 3,40, 0,57, 1,19, 5,28, 2,40 pp |
| retorno de sesión: % aciertos / MAE pp | ídem | 65,1 / 2,31 | **67,4 / 2,31** | de las 8, acierto_direccion 2 (000660.KS, 4063.T); errores 1,15, 1,90, 0,53, 1,74, 0,28, 1,45, 6,65, 4,88 pp |
| `calibracion_intervalos` n / cobertura % | Telegram, `/api/aperturas`, `/api/historial`, dashboard | 490 / 93,5 | **482 / 93,6** | las 8 (7 dentro del intervalo, 8035.T fuera) |
| `evolucion_aciertos_apertura` fechas / N | `/api/historial`, dashboard | 64 / 490 | **63 / 482** | desaparece la fila `2026-09-28` (gap 37,5 %, sesión 25,0 %, N 8) |
| `ultimas_predicciones_apertura(100)` ventana | `/api/historial` | 2026-09-21 … 10-08 | **2026-09-18 … 10-08** | salen las 8 del 28-sep; entran las 8 más antiguas siguientes (18-sep). Con `limite=50` (dashboard): sin cambio (30-sep … 08-oct, 0 invertidas dentro) |
| `verificaciones_detalle` n / aciertos gap | `/api/historial` (`wilson`, curva, `por_region`, `por_regimen`) | 490 / 319 | **482 / 316** | XETR 63 → 62, XKRX 118 → 116, XTAI 60 → 59, XTKS 249 → 245; el régimen «sin régimen sellado» (8) desaparece |
| `analisis_puntaje_ia(90)` n / tercio alto / bajo / corr | `/api/historial`, dashboard | 1308 / 0,31 / 1,58 / −0,07 | **igual** | 0 filas invertidas dentro de `verificacion_puntaje` (la guarda de la 16a las dejó fuera); 32 filas con igualdad `available_at == timestamp_utc` y 0 NULL siguen dentro, por diseño (§78 (3)) |

**Lo que NO cambia, verificado:** ventana (`date('now', ?)`), filtros (`legacy = 0`, `modelo_version`, `gap_pct IS NOT
NULL` salvo en `ultimas`), redondeo (1 y 2 decimales), nombres de columna y dtypes (`evolucion`: `Fecha` str, dos
`float64`, `N` int64), y el **orden de filas**: las consultas viejas sirven por el índice único `(fecha_senal, ticker)`
(`EXPLAIN QUERY PLAN`, MEDIDO: `SEARCH … USING INDEX sqlite_autoindex_verificacion_apertura_1`), y las nuevas ordenan
igual; `ultimas(100)` y `verificaciones_detalle` dan el MISMO orden que la vieja sin las invertidas (MEDIDO,
`medicion_despues.txt`). El puntaje tiene 513 empates sobre 1308 filas y los tercios dependen del orden de entrada:
igual orden, mismos tercios.

**Dirección del efecto, declarada:** de las 8 filas retiradas el modelo acertaba 3 en gap (37,5 %) y 2 en sesión (25 %);
la exclusión sube las tasas vivas del campeón (+1,4 pp en gap, +2,3 pp en sesión) y EMPEORA el MAE del gap (3,95 → 4,07
pp: las 8 tenían MAE 1,81 pp). Orden de método, DECLARADO en el acta §90.1 d: la regla se firmó por su mérito el 29-sep
a las 18:29 y no por la magnitud del daño. Zona ciega Z2 del auditor de esta corrida, DECLARADA: la firma es 14 minutos
posterior a que el verificador de las 18:15 escribiera las 8 filas, y la magnitud estaba en la bitácora 14 §9, así que la
dirección del efecto era computable por quien redactó la regla; no es demostrable en ninguna dirección.

**Deduplicación (informativo; tarjeta §82):** la regla firmada retiraría 10 filas de toda la historia (2026-07-29 y
2026-08-03), 0 en la ventana de 30 días: calibración 482 → 472, detalle 482 → 472 (gap 65,6 % → 66,3 %), track record
30 d 141 → 141. No se aplica a las cifras vivas (encargo §1); decisión en la tarjeta.

---

## 3. Qué hace cada bloque, y las elecciones de agente

### A. La fuente única (`backtest/linea_base.py`, sección «LAS CIFRAS VIVAS PUBLICADAS»)
- `cargar_vivas(modelo_version, dias=None, solo_con_gap=True)`: `verificacion_apertura` con `senales_ticker` y
  `snapshots`, nunca legacy, una `modelo_version`, ventana opcional en SQL con la misma expresión de `senales.py`,
  columnas de las seis cifras (incluye `estimado_sellado` = `senales_ticker.apertura_estimada_pct`, `timestamp_utc`,
  `available_at`, `regimen`, `id`), orden `(fecha_senal, ticker)`, y `excluir_sin_conocibilidad()` al final. Sin base:
  frame vacío con las columnas, sin crear nada. `cargar_puntaje_vivo(modelo_version, dias=90)`: lo mismo para
  `verificacion_puntaje`.
- Las seis funciones, con los MISMOS nombres y firmas que en `senales.py`, con el mismo cálculo (sumas en el orden de la
  consulta, `round` a 1 y 2 decimales, `MINIMO_OBSERVACIONES = 5` atado por test al de `senales.py`; `senales` no se
  importa: la capa de medición no cuelga del módulo que escribe la base).
- **Elecciones del agente:** (1) no deduplicar las cifras vivas (tarjeta §82.1); (2) `senales.py` byte a byte igual; las
  seis quedan sin consumidor publicado y un test lo fija (§82.2); (3) el import de `linea_base` en `alertas.py` es
  perezoso, dentro de `componer_reporte_sellado`, porque `backtest/datos.py` importa `motor` y `alertas` lo cargan
  `snapshot.py` y el vigía: el reporte importa el motor y no lo llama (test de la 5.0 en pie, más uno nuevo por la ruta
  nueva); (4) en `api/main.py` y `app.py` el import es de módulo (los dos ya importan `motor`).
- Consumidores: `alertas.py:283,:292`; `api/main.py:29` (import), `:540`, `:565`, `:765`, `:811`, `:812`, `:828`, `:830`,
  `:836`; `app.py:28` (import), `:915`, `:1420`, `:1584`, `:1602`, `:1619`, `:1632`, `:1662` (líneas del worktree).
- `api/CONTRATO.md`: enmienda 16-3, sólo valores (ninguna forma cambia), con la tabla de arriba resumida y una nota de
  forma preexistente: `evolucion` y `ultimas` se sirven con las claves de las columnas del DataFrame (`Fecha`, `% Aciertos
  gap`, …), que el frontend consume así, y no con las minúsculas que el bloque de `/api/historial` escribió en su día.
- Tests (`tests/test_fuente_unica_16_3.py`, 32 nodos tras las exigencias del auditor): por cifra, igualdad exacta con la vieja sin invertidas y
  exclusión de una fila invertida sintética (dos bases en tmp, idénticas salvo la fila); misma regla que el árbitro
  (`cargar_vivas` y `cargar(dedup=False)` retiran el mismo conjunto; NULL e igualdad no disparan); misma ventana de
  días; la API (`/api/historial`, marcado `red`) y el reporte de Telegram no cuentan la invertida; el reporte sigue sin
  llamar al motor; sin base, «datos insuficientes» n=0 y no se crea nada; las seis no modifican la base (tamaño, mtime y
  bytes); por AST, las funciones nuevas no llaman `connect`/`get_connection`/`init_db` y el módulo no importa `senales`;
  por AST, ningún consumidor publicado llama a las seis de `senales`; el mínimo es el de `senales.py`; la deduplicación
  declarada (§82.1).

### B. El README y los textos
- `docs/readme/README.en.tmpl.md` (la plantilla española no tiene sección de riel): E0 con el texto firmado en §93.11.3
  («On trading nights when the machine is awake, it emits and seals.»), la declaración del universo de §95.4 (desde la
  sesión del 2026-10-05, TOELY fuera del insumo, sin sustituto y sin retorno; las filas se distinguen por
  `reglas_sha256`), y «a power cut» entre las causas de una noche perdida (los del 6 y 7-oct, §99.1); E1 con el texto
  corregido de §102.5: «The IBKR account is approved and verified, and the paper-trading user exists; the gateway is
  not set up yet.» **Difiere del texto firmado en §93.11.2 por un hecho posterior (§95.3, el usuario de práctica existe
  desde el 4-oct), tal como manda el encargo §3.2.** E0 ya remitía sólo al CSV versionado (§93.11.1 aplicado en la 15;
  la errata a §90.3 está en §93.11.1). Los números nuevos quedan dentro de la sección de E0, que el test de paridad
  numérica entre los dos README excluye.
- `GEMELO/resultados/tesis.md:161`: «59×» → «61× la muestra sellada (14.618 / 238, el marcador `larga_veces` del
  generador)», con errata fechada en el mismo párrafo. `larga_veces` leído de la máquina: 61 (`generar_readme.py
  --valores`, 19:5x).
- Badges (§90.4): [se completan al aplicar: `tests_recolectados` leído con `pytest tests/ --collect-only -q` sobre el
  árbol real con los tests nuevos, `plataforma_version` de `version.py` (5.1.0), `leido_el` 2026-10-11; los tres juntos].
- Fusión de tarjetas (§93.12), en `espera_firma.md`: §74 FUNDIDA (resuelta de hecho por §93.2 y §99.1; su resumen va al
  «Primero» de `ESTADO.md`), §69 FUNDIDA (pierde la tarjeta; la línea de la skill `gate` la aplica Nicolás), §72 FUNDIDA
  en la fila 2 de §66 (H0 cerrada por la frescura; H2 y D.2 siguen), §70 FUNDIDA en la fila 4 de §66 (sus tres
  elecciones firmadas en §93.10). Los textos no se borran. §80 y §81 marcadas FIRMADAS en el acta §102 (y §81 aplicada,
  acta §103).
- Revisión del `curador-epistemico` sobre el README generado: [al cierre].

### C. El parche de `dinero/` (NO aplicado): `GEMELO/propuestas/parches/version_reglas_16_3.{diff,md}`
- Construido en `wt163_dinero` (HEAD puro + el parche): `version_reglas` 0.3.0-PROPUESTA con nota fechada (§99.5); R4
  (la exclusión revienta ante un ticker que no está en el censo, `ValueError` que lo nombra); §81.3 (b) (las filas de un
  intento llevan en `motivo` el instante con que se decidió el timing: el de congelar si la evidencia nació
  `.no_verificable`, si no el del sello; el motivo de E3 se conserva delante; sin cambio de esquema, test de columnas);
  R2 (`estado()` gana `por_reglas_sha256`, aditivo; la API no lo sirve y un test lo fija).
- Tests escritos antes (15 nodos): sobre HEAD 10 rojos por su aserción, 3 verdes de control, 1 saltado (base real);
  con el parche 14 passed, 1 skipped en el worktree (la base real no está). Los seis archivos del riel en el worktree
  (`test_sello_dinero`, `test_toely_fuera_insumo_e0`, `test_camino_T_16_2`, `test_b2_intentos_visibles_16_2`,
  `test_dinero` y el nuevo): 117 passed, 12 skipped, 2 failed, los dos del control (`test_dinero::…salen_del_arbitro`,
  `…sirven_lo_que_el_contrato_dice`, artefactos gitignorados ausentes).
- Versión dictaminada: sha256 `f164b232971cef4e1e2ccb981d967b226852d7eeb77a8039dc803d094ea968f3` (405 líneas). **Versión
  final, tras B1 del auditor (20:43 a 20:48): `5acdb3e2967e794cf21c981cb83544a5958222fba053fa1635f0e48b584667cd`** (428
  líneas, +362/−5: `2 1`, `56 4`, `304 0`); `git apply --check` limpio sobre HEAD puro (`wt163_ctrl`) y sobre el árbol real
  (HEAD + lo sin commitear); pre imágenes `d1cdef8a…` y `279d0884…`. Huellas tras aplicar: `dinero/reglas.json`
  `6f3715275dadc5279e3661a9fcc1dc64af799e0a140de3a7f3eff17765ab444a`, `dinero/sello_dinero.py`
  `2a9c2d57f9c4cbf5eb925526549e565a481c5d6678aadeb2a9227034812280f6` (igual por `S._sha256`). Lo que cambió entre las dos
  versiones: la nota del camino de reserva de §81.3 (b) (meta sin bloque `timing`) cita `congelado_en_utc` y la clase de la
  evidencia en vez del reloj del sello, con el caso falso fijado por test (`test_sin_bloque_timing_la_fila_cita_la_clase…`);
  el comentario de `estado()` declara el alcance de `por_reglas_sha256`; el test de la base real compara por hash y por
  rangos disjuntos, no por posición. Rojos sobre HEAD con el archivo FINAL (B3): **10 por su aserción, 4 verdes de control,
  1 saltado** (`evidencia/pytest_version_reglas_sobre_HEAD.txt`, retomado a las 20:48). Preflight de R4 sobre HEAD en
  `mode=ro` (20:48): censo 33, TOELY dentro, `decidir` 32 operables con `excluidos_universo = ['TOELY']`, gate
  `INVARIANTE` (2 y 6 cortes). Receta (con los once puntos de R6 del auditor) y predicción falsable en el `.md`. Dictamen:
  §5.2. Quién y qué noche: tarjeta §89.

### D. Higiene de tests (R5 y hecho (ii) de §80; §81.4 a)
- **Diagnóstico (MEDIDO, `wt163_diag`, 19:40 a 19:48):** en un árbol sin bases, el ÚNICO creador de `senales.db` y
  `noticias.db` es `tests/test_api.py`: los 22 tests que pegan a la API (`TestClient`) hacen que la API corra
  `senales.init_db()` / `noticias.init_db()` sobre la ruta real (`creadores_de_bases_en_worktree_sin_bases.tsv`: el
  primero, `test_envelope_en_todos_los_endpoints`, crea las dos; después de cada test el detector las borraba para ver
  al siguiente). Ningún otro archivo las crea. `dinero/sello_dinero.db` no la crea nadie.
- **Corrección:** `tests/test_api.py` gana un fixture de módulo (`_bases_de_la_api`, autouse): con las bases reales
  presentes, la API lee durante ese módulo una COPIA en tmp de cada una (la real deja de abrirse en escritura desde los
  tests de la API); sin ellas, rutas temporales que `init_db()` crea en tmp. `esperado` y `servido` leen la misma copia:
  la paridad no cambia. Precedente de copiar la base real a tmp desde un test: `test_conocibilidad` (corrida 15).
- **R5:** `tests/bases_de_prueba.py` (ayuda, no test) con `hay_filas(ruta, tabla)` en `mode=ro`; los seis marcadores
  `solo_con_base` (`test_linea_base`, `test_conocibilidad`, `test_bifurcaciones`, `test_banco_clausulas` →
  `verificacion_apertura`; `test_frescura` → `snapshots`; `test_guarda_puntaje` → `senales_ticker`) preguntan por la
  tabla con filas y no por el archivo. Un sexto marcador (`test_banco_clausulas.py`) no estaba en la lista del encargo:
  lo cazó el test que barre todos.
- **Guarda permanente** (`tests/conftest.py`, fixture autouse): si al terminar un test existe una base que no existía al
  empezarlo, o un archivo nuevo bajo `data/backups/`, el test falla nombrando qué creó. En el árbol real (bases
  presentes) no hace nada. La segunda mitad nació de un **hallazgo de esta corrida:** mi test sintético de huérfanos
  llamó `respaldar_extension(ruta)` y escribió `ext_2026-09-14.no_verificable.*` en `data/backups/sello_dinero_ext/`
  del worktree, porque `respaldar_extension` tiene `destino=DIR_BACKUP_EXT` ligado como argumento por defecto al importar
  y el monkeypatch de `DIR_BACKUP_EXT` no lo alcanza. Corregido en el test (`destino=` explícito) y convertido en regla.
  Tests: `tests/test_higiene_bases_16_3.py` (14 nodos: `hay_filas`, los marcadores, el barrido de compuertas con su
  contraprueba, contrapruebas de los dos detectores, el fixture de `test_api`).
- **§81.4 (a):** `tests/test_integridad_no_verificable_16_3.py`: todo `.no_verificable.csv` en `DIR_EXT` y en
  `DIR_BACKUP_EXT` está citado por una fila de `intentos_no_verificables` (sin la tabla, todo `.no_verificable.csv` es
  huérfano); sintéticos (la ventana entre congelar y sellar se ve; un archivo sin fila se ve; sin tabla) y real
  (`mode=ro`; hoy pasa vacío: 0 archivos y la tabla no existe; empieza a morder con el primer disparo de timing roto en
  E0.3). Sólo test: el sellador no se toca.

### E. R9: la negativa del fallback del dashboard llega a `snapshot.log`
- Forma elegida (la más chica que no toca el vigía): `app.py` guarda el resultado de `ejecutar_snapshot("dashboard")`
  (antes lo descartaba) y, si trae `negativa`, `_anotar_negativa_en_snapshot_log()` deja en `data/snapshot.log` el MISMO
  bloque que deja el job (cabecera `snapshot.py (origen=dashboard, …) [fallback del dashboard, app.py]`, que es lo que el
  vigía usa para encontrar la última corrida, y la línea fija de `MARCA_NEGATIVA` con código, fecha, `sox_fecha` y
  motivo), una sola vez por sesión del navegador (`st.session_state`; Streamlit reejecuta el archivo en cada
  interacción). Un `OSError` al escribir no tumba el dashboard: lo dice en pantalla. El vigía no se toca.
- Tests (`tests/test_fallback_dashboard_16_3.py`, 6 nodos): la función se extrae de `app.py` por AST y se ejecuta con
  los nombres del módulo (un script de Streamlit no se importa); el log resultante lo lee el parser REAL del vigía
  (`mki_vigia._negativa_declarada_en_log`) para los dos códigos; `chequear_snapshot` lo clasifica como negativa y no como
  falla; sin negativa no se escribe nada; una negativa de otro día no se lee como de hoy; `app.py` captura el resultado
  y anota una vez por sesión.
- Declarado: la «última cabecera» manda (semántica preexistente del vigía para una corrida manual): si el job falló sin
  negativa y el fallback del dashboard después se negó por regla, el vigía ve la negativa. Y la fecha de la negativa
  `sesion_sox_abierta` no viaja en el dict: se usa `date.today()`, el mismo reloj que `ejecutar_snapshot`.

### F. La tarjeta de `/sellos` (§81.6 a)
- `frontend/src/vistas/SellosDinero.tsx`: dentro de la Card de E0 (que ya declara su estatus), un bloque «Intentos no
  verificables (E0.3, disparos fuera de hora)» con «intentos no verificables: N; último: fecha, hora (Chile)» o «último:
  ninguno», la frase `nota_intentos` y la fuente. Con una base anterior a E0.3 la API manda 0 y null: la tarjeta dice 0
  sin error (`?? 0`). `tsc --noEmit -p tsconfig.app.json`: exit 0 (19:59:33, con `node_modules` del árbol real
  enlazado al worktree). Sin palabras que insinúen resultado (`test_frontend_estatus` lo barre).

---

## 4. Suites: control HEAD puro, worktree con cambios, árbol real

- **Control, HEAD puro, sin bases (`wt163_ctrl`, 19:40:32 → 19:48:40):** 19 failed, 1044 passed, 90 skipped, 1 xpassed,
  6 errors. Rojos: `test_api` D1, D3, D9, D11, D12_D13, D15; `test_dinero` (2); `test_frontend_estatus` (1);
  `test_linea_base::…228_filas`; `test_readme` (9); errores: `test_cifras_arbitro` (6). Todos por artefactos
  gitignorados ausentes (bases, `dinero/resultados/*.json`, README generado).
- **Worktree de trabajo con los cambios (`wt163`, sin bases reales; con las `senales.db`/`noticias.db` VACÍAS que el
  primer `pytest` de `test_api.py` dejó a las 19:53):**
  - 1.ª corrida (20:14:23 → 20:22:03): 33 failed, 1094 passed, 75 skipped, 1 xpassed, 6 errors. Catorce rojos más que el
    control: el conocido (huérfanos, los dos archivos fugados) y **13 de `test_importador_roundtrip.py` (11) y
    `test_restaurar_backup.py` (2)**, que saltaban por `isfile` y, con la base vacía presente desde la recolección,
    compararon 0 filas contra la restauración (en el control la base la creaba `test_api` DURANTE la corrida, después de
    la recolección, y saltaban). HALLAZGO: R5 los alcanzaba y no estaban en la lista del encargo; migrados a `hay_filas`.
  - 2.ª corrida (20:26:39 → 20:34:24, tras migrarlos): **20 failed, 1092 passed, 91 skipped, 1 xpassed, 6 errors; el
    conjunto de rojos es el del control más exactamente UNO, el conocido** (`comm` de las dos listas,
    `evidencia/suite_worktree_con_cambios_2.txt`).
  - 3.ª corrida, con las exigencias del auditor aplicadas (B3, B4, B5, R2, R3, R4), 20:51:31 → 20:59:06: **19 failed,
    1096 passed, 95 skipped, 0 xpassed, 6 errors**; el conjunto de rojos es el del control MENOS uno
    (`test_linea_base::…228_filas`, que ahora salta bien por B4 en vez de asertar `0 == 228` sobre la base vacía) MÁS
    el conocido (`evidencia/suite_worktree_con_cambios_3.txt`). El `1 xpassed` del control (el `xfail` de
    `test_epistemico` sobre la base vacía) desaparece porque ese test ahora salta sin base con filas.
- **Árbol real después de aplicar:** §6.

---

## 5. Dictámenes

### 5.1 `auditor-lookahead` sobre el Bloque A (`dictamen_16_3/auditor_fuente_unica.md`, 20:04:37 → 20:24:50): APLICABLE CON EXIGENCIAS

Verificó por su cuenta el límite duro del §1 con una base en memoria poblada sólo con las filas que la regla deja
pasar y las funciones REALES de `senales.py` contra ella: once configuraciones (ventanas 30/90/365, límites 50/100/500)
iguales por `DataFrame.equals` (valores, dtypes, columnas y ORDEN) y por igualdad de dict; `datos_equals=True` en el
puntaje (misma permutación con 513 empates). Prueba maestra de invarianza a truncar en `t` con contraprueba; los dos
instantes que la regla lee no se reescriben nunca (censo de las cinco sentencias de modificación de `senales_ticker`:
todas tocan sólo `estado`); calendarios reales (Seúl y Taipéi cerrados el 9-oct, Tokio el 12). Cinco BLOQUEANTES, las
cinco atendidas antes de aplicar:
- **B1** (acta y tarjeta): decir que la letra de §93.4 nombraba `cargar()`, que deduplica, y que el bloque implementó
  `cargar_vivas()` sin dedup para cumplir el §1 del encargo → tarjeta §82.1 reescrita y acta §104.2 A.
- **B2**: suite completa del árbol real contra la línea base archivada, `test_motor.py`, huellas → §6.
- **B3**: ERROR de la guarda de red en `test_api.py::test_paridad_roca_chip_contra_snapshot` bajo `-m "not red"`. MEDIDO
  por el orquestador (20:31): ocurre igual en HEAD puro y en el árbol real SIN los cambios (`/api/hoy` pide el régimen
  al motor; en la suite completa lo tapaba la caché que calienta `test_envelope`, marcado `red`): preexistente, no del
  fixture. Cerrado marcando el test `red` con esa medición en el comentario.
- **B4**: dos compuertas `if not os.path.exists(lb.RUTA_SENALES)` en `test_linea_base.py` (una pasaba VACUAMENTE con la
  base vacía: `0 >= 0`) → `HAY_BASE` por filas; censo extendido: `test_epistemico.py:554` y `test_segundo_sello.py:330`
  tenían la misma compuerta → `hay_filas`; el barrido de `test_higiene_bases_16_3.py` caza ahora también las compuertas
  de cuerpo (`_COMPUERTA_POR_ARCHIVO`).
- **B5**: el reporte de Telegram pasaba a exigir que `motor` fuera IMPORTABLE (`backtest/datos.py` lo importa a nivel de
  módulo; el auditor lo midió envenenando el import: `componer_reporte_sellado()` reventaba con `ImportError` y
  `_cli_reporte` no lo protege). Resuelto por la opción (a): `linea_base.py` define sus propios `RUTA_SENALES` y
  `_conexion_ro` (dos símbolos triviales) y ya no importa `backtest.datos`; test en SUBPROCESO con el import de `motor`
  envenenado desde el arranque: el reporte compone y «motor» no entra a `sys.modules`; test por AST de que el módulo no
  importa `backtest.datos` ni `motor`; `test_el_modulo_no_abre_ninguna_conexion_de_escritura` adaptado (la única llamada
  a `sqlite3.connect` es la del `mode=ro`).
Recomendadas: R2 (empate en el borde del tercio en el juego sintético: fila agregada, con test que exige el empate), R3
(la equivalencia compara en orden canónico y el orden exacto va en un test aparte, declarado dependiente del plan de
SQLite), R4 (copia de las bases en `test_api` por la API de respaldo de sqlite desde `mode=ro`, no `shutil.copy`), R5
(«retira 8 y admite 8 más antiguas» en contrato y tarjeta), R6 (la dirección completa del efecto, con el MAE en contra y
las dos reglas pendientes en la misma dirección) → tarjeta §82; R7 (tres copias del predicado) y R8 (ISO malformado
revienta) → declaradas en §82, sin código; R1 (equivalencia sobre la base REAL fijada por un test) → no hecha en la
16-3: la atestigua la medición del auditor, archivada; queda en §82 como deuda. Zonas ciegas Z1 a Z8 en el dictamen;
Z7 (el worktree mezcla bloques): este dictamen cubre el Bloque A y los archivos de la frontera que tocó por B3 y B4
(`tests/conftest.py`, `tests/bases_de_prueba.py`, `tests/test_api.py`); los Bloques D, E y F no tienen dictamen de
auditor (son tests, un bloque de `app.py` que no toca el sellado, y una tarjeta de pantalla) y los revisa el guardián.

### 5.2 `auditor-lookahead` sobre el parche de `dinero/` (`dictamen_16_3/auditor_version_reglas.md`, 20:19:03 → 20:35:24): APLICABLE CON EXIGENCIAS

Sobre la versión `f164b232…`. Sin fuga demostrada: gate `INVARIANTE` sobre el insumo real (2 y 6 cortes) idéntico a HEAD;
sha256 del volcado de 40 huellas de decisión con sus 32 motivos idéntico en HEAD y parche; `estado()` sobre la base real
en `mode=ro`, módulo de HEAD contra parchado, 13 claves comunes byte a byte iguales (sha `eaf5ad7a…`) y el desglose nuevo
suma los totales (22 sesiones, 12 cuentan, 722 filas); cuatro escenarios de `sellar` sobre bases temporales con el insumo
real del 9-oct, en los que la ÚNICA columna que difiere es `motivo` de un intento; `_divergencia` nunca mira `motivo`;
las reglas numéricas no se mueven (sha del dict sin la versión y la nota, idéntico). Tres BLOQUEANTES, las tres
atendidas antes de cerrar: **B1** (el camino de reserva, meta sin `timing`, atribuía el veredicto al reloj del sello y
podía sellar una frase FALSA en un campo inmutable, medido con un sello a un instante con timing OK; hoy no alcanzable
por `main()`, porque `congelar_extension` siempre escribe el bloque y `--sin-red` sólo levanta canónicos; corregido con
la opción (a): cita la clase de la evidencia y `congelado_en_utc`, y el caso falso quedó fijado por test); **B2**
(preflight de R4 antes de aplicar y gate después: en la receta, y el preflight sobre HEAD corrido el 11-oct 20:48);
**B3** (los rojos sobre HEAD retomados con el archivo final: 10/4/1, con los cuatro controles nombrados). Recomendadas:
R1 (alcance de `por_reglas_sha256`) declarado en el código y la receta; R2 (test de la base real por hash y rangos, no
por posición) aplicada; R3 (`motivo` compuesto, al CSV versionado) declarado; R4 (separar universo de censo en el raise:
`techo_usd` bajo ~72 USD sacaría a TOELY del censo) y R5 (el riel de dinero no tiene vigía) → tarjeta §89; R6 (once
puntos para la receta) → receta. Zonas ciegas Z1 a Z9 en el dictamen (Z2: E0.3 todavía no selló nada real y el punto 3
del parche toca ese camino; Z7: la elección de reventar contra el censo la hizo quien ya sabe que TOELY es el único
excluido).

### 5.3 `curador-epistemico` (`dictamen_16_3/curador_readme.md`, 21:01:24 → 21:12:57): RECHAZA, atendido

Sobre el estado de las 21:01 (con la suite real todavía corriendo). Verificó las dos frases firmadas al carácter
(§93.11.3 y §102.5), los badges contra la máquina (1216, 5.1.0), el riel E0 contra el CSV sellado (primera fila
2026-09-08; 18 fechas con 33 filas y `125a8602…`, 4 con 32 y `b6080eee…`; TOELY tope el 24-sep; 12 cuentan), la enmienda
del contrato cifra por cifra contra `evidencia/`, el 61× contra `larga_veces`, §80 y §81 contra las actas, y las
predicciones de §7. Tres BLOQUEANTES, atendidas (21:14 a 21:22): (1) `ESTADO.md` y esta bitácora citaban el acta §104
antes de que existiera → el acta está escrita (§104, al final de `DECISIONES.md`); (2) §2 decía que la regla se firmó «antes de mirar»
la dirección del efecto, una frase sobre un estado mental que el auditor había desmentido en Z2 → reescrita con lo que
el auditor midió (orden de método DECLARADO; dirección computable al redactar, DECLARADA); (3) `tesis.md:172` ofrecía una
cifra retirada el 2-sep (la estimación de MB/año del camino C3) sin marca → reemplazada por el valor medido con su
errata; `cifras.reintroducciones` da limpio en los siete documentos tocados. Observaciones: O1 («a power cut» sin estatus
→ DEDUCIDO del journal, §99.1, en el README), O2 (TOELY «muerto» contra «rezagado crónico» → añadido el 18 y el 23-sep,
§96.3), O4 (`ESTADO.md` nombraba tres sesiones perdidas → 10 de 22 no cuentan y dos noches sin filas), O5 (p25 sin método
→ rango por método), O6 («mismo denominador» → misma DEFINICIÓN del denominador), O7 («la cifra del campeón» → la tasa de
gap de toda la historia viva), O8 (los dos huecos de la bitácora, llenos). **O3, declarada y NO atendida:** publicar la
proporción de noches perdidas de E0 choca con la firma de §93.11.1 (b), «esta página no lleva contador»; la cifra queda en
el acta §104.2 B (22 fechas selladas, 12 cuentan, 10 no, dos noches sin filas). O9 a O11: nada que cambiar. Después de
los arreglos: README regenerado y verificado; `test_readme.py`, `test_cifras_arbitro.py` y `test_frontend_estatus.py`: 35
passed (21:19:48); el código no cambió después de la suite completa de §6.

---

## 6. Aplicación al árbol real: **corte de método 11-oct-2026, 20:59:44 (Chile, −03:00)**

Con el dictamen del auditor sobre el Bloque A (APLICABLE CON EXIGENCIAS, las cinco bloqueantes atendidas, §5.1), el del
parche de `dinero/` (que no se aplica, §5.2) y la tercera suite del worktree a la vista (§4: el conjunto de rojos es el
del control menos el de las 228 filas más el único conocido), los archivos entraron al árbol real por copia desde el
worktree en un solo acto (`stat -c '%y'`: `backtest/linea_base.py` 20:59:44.705 el primero, la bitácora 20:59:44.923 la
última; 33 rutas más la carpeta `dictamen_16_3/`), a más de 20 horas del próximo disparo de un job (lunes 17:50). Antes de
copiar, huellas de las tres bases iguales a las de apertura (§0.2). El guion de aplicación y su salida están en
`evidencia/` (`aplicar_16_3.sh`, `aplicacion.txt`).

| archivo aplicado | sha256 |
|---|---|
| `backtest/linea_base.py` | `6a095c1b71163397c677248d3b43da899ebb9cf77fb281841da08df8ebe265d5` |
| `alertas.py` | `b3c25f9f51f1f5b709f1d7a121e6cb302dc5fbd94628de40015b53c2839e9e81` |
| `api/main.py` | `692ced3929f48d7a96ec0bdcdef63def9af9f355b27575cb9398c41032766a02` |
| `api/CONTRATO.md` | `ef6bcdf29f78c99446694ba94d45e9634ab04daa15dc21957b8c79eef2d5a217` |
| `app.py` | `f7d5f967d7b16412e80696a6926af16fb8bb5d01f2e9a35636a817e137a20fc5` |
| `frontend/src/vistas/SellosDinero.tsx` | `abe668c5a602f2ada64f9ef585c5f0fa5bf8547a7184854a8ca1b2813ea2a087` |
| `docs/readme/README.en.tmpl.md` | `b0e4c3fcbcf025b81188d25021343dfdde4d7308867059d483e9e28adaa205c4` |
| `tests/conftest.py` | `5e228200f6efe71fcdaca77cb40a9652861338387808ed82ad4c0128a260173c` |
| `tests/bases_de_prueba.py` | `386e4b8cc520ede0e9a8cb6ab2ebab481ad992b331164457ff350b6f137a4841` |
| `tests/test_fuente_unica_16_3.py` | `036b2ee788d9e57a9d6dacbc67621b038fadddc354ebee0cef129305e0fd4ed5` |
| `tests/test_higiene_bases_16_3.py` | `4e00c09b5a5faea5569aa7f6d4607e591785627e6262d3c3f1289f2a177700b1` |
| `tests/test_integridad_no_verificable_16_3.py` | `b2c7513054ebd2cd66e993aa0ebb6e42ead9fd588615b060d2516e3f50bad591` |
| `tests/test_fallback_dashboard_16_3.py` | `684c24923a2f91afd7acc6a392e1ea5f5011baee720f16a601d49e45b2448a33` |
| `tests/test_api.py` | `3c5ef4bbba7a52df4f72b7cf8b96295e7094f3da902e6b89a29a48b16b708ddc` |
| `tests/test_reporte.py` | `f1bc0a864e51536121bdff63bd4ed4f18005de73f2cd48c1f17eb8fc9bc7e8c9` |
| `tests/test_linea_base.py` | `4089c970b610280e1c767e03830706f320a85130f9c7237bc5c461a572561aad` |
| `tests/test_conocibilidad.py` | `39fb00f8a4ea8e72a978fec04a76bb98b9ef506346fa2a7603f6fc044e595608` |
| `tests/test_frescura.py` | `68e6882ec484264b12b97f62fbd2f83fef2266fead483002c9189a3168cb1152` |
| `tests/test_guarda_puntaje.py` | `d53bcf923fcf421d3a45ea31a0dc10cd4fb7ffdfa048f0adb8c42227efe1e99a` |
| `tests/test_bifurcaciones.py` | `8ae146caf4d6df6641aac68e39c1205262a96e689560e088b4dd4f49dea0d5c4` |
| `tests/test_banco_clausulas.py` | `66033d74795d8658c29c0dfba22f41fc3d87dc30a63c72880c68dc59af357231` |
| `tests/test_epistemico.py` | `776158fdb1dabc3876317a672b70c022ec8264cbd85de6830c6e0bf4c3b0a09d` |
| `tests/test_importador_roundtrip.py` | `6507ec5fb759f1312028f7ef05b1f5912c309a927b860d6ea9bb6dd6f699681c` |
| `tests/test_restaurar_backup.py` | `100acddb61b110f6e12c78dcb518ebd58e969f8d9855da434af008d0a9ce67c1` |
| `tests/test_segundo_sello.py` | `5ad3babfc921c81d8f7d33ef799d303ffe8fe30a14ac2b1e76aabd54351bee84` |
| `GEMELO/resultados/tesis.md` | `75a79aa917863758fc589e227fdc74f2d47382e4aaeb26b781b60649527906eb` |
| `GEMELO/resultados/espera_firma.md` | `fe0c5be7ddd1a5a5717584e8afb4d22f91b6efd5938266ac2fad1a5bc2ed781b` |
| `GEMELO/propuestas/parches/version_reglas_16_3.diff` | `5acdb3e2967e794cf21c981cb83544a5958222fba053fa1635f0e48b584667cd` |
| `GEMELO/propuestas/parches/version_reglas_16_3.md` | `b40eea9c5dced650d73df0ecb5643891591a9185623888f056c06913c599a983` |
| `ESTADO.md` | `31f719cb044e80fa2cca21652d75b75e71a6b8fd2bb6bd14e9a91d3c92e28c03` |
| `GEMELO/resultados/bitacora_16_3.md` | `69d043358f976bed8ff49f469473faaf8bc3bb0d91dddafc2d1bc604825ae24d` |

Después de copiar (21:00:01 a 21:00:22, guion `badges_y_readme.sh`):
- `pytest tests/ --collect-only -q` sobre el árbol real: **1216 tests recolectados** (eran 1025 al 29-sep; +191: los
  cinco archivos nuevos de la 16-3, los de la 16-1 y la 16-2 que el badge no había recogido). `docs/readme/badges_congelados.json`
  con los TRES valores juntos (§90.4): `tests_recolectados` 1216, `plataforma_version` 5.1.0 (leído de `version.py`),
  `leido_el` 2026-10-11.
- `scripts/generar_readme.py`: README.es.md y README.md escritos; `--verificar`: los dos coinciden con el disco. Diff del
  README.md: los dos badges y las viñetas de E0 y E1 (§3 B); del README.es.md: sólo los dos badges.
- `tsc --noEmit -p tsconfig.app.json` en `frontend/`: exit 0.
- `venv/bin/python tests/test_motor.py`: las seis funciones del motor idénticas con y sin datos futuros en las tres
  fechas de prueba (2026-09-11, 2026-07-13, 2026-04-14), «sin look-ahead bias».
- **Suite completa del árbol real con todas las bases (B2 del auditor), 21:01:21 → 21:09:42: 1207 passed, 8 skipped,
  1 xfailed, 0 failed, 29 warnings, en 500,13 s, `EXIT 0`** (`evidencia/suite_arbol_real_despues.txt`). Contra la
  apertura (1151 passed, 8 skipped, 1 xfailed): +56 en verde, que son los tests nuevos de la corrida (1216
  recolectados contra 1160); el mismo `1 xfailed` de `test_epistemico`, los mismos 8 saltados, las mismas 29
  advertencias conocidas (`Pandas4Warning` de `motor.py:215`, `starlette.testclient`, `GEMELO/transversal.py:260`).
- Huellas de las tres bases después de aplicar y de regenerar (21:01): idénticas a las de apertura (`98a048de…`,
  `1829b61b…`, `2a016c52…`).

---

## 7. Predicciones falsables para el lunes 12-oct-2026 (escritas antes de aplicar; `mode=ro`)

El lunes a las 18:15 el verificador procesa las 11 predicciones `pendiente` de hoy: **7 con sesión objetivo 2026-10-12**
(000660.KS, 005930.KS y 2330.TW emitidas el 8-oct, con el 9-oct feriado en Seúl y Taipéi; 000660.KS, 005930.KS, 2330.TW e
IFX.DE emitidas el 9-oct) y 4 de XTKS con objetivo 2026-10-13 (feriado en Tokio el 12), que se verifican el martes. La
ventana de 30 días del lunes (`date('2026-10-12', '-30 days')` = 2026-09-12) deja fuera las 8 filas del 11-sep.

**Base, sin las verificaciones nuevas (hoy, `fecha_senal >= 2026-09-12`):** por la definición vieja n = 141; por la fuente
única **n = 133, gap 67.7 % y MAE 4.04 pp, sesión 70.7 % y MAE 2.2 pp**. Sea k el número de las 7 que el verificador
cierre el lunes con `gap_pct` (k = 7 si Yahoo sirve las aperturas; las dos emisiones de 000660.KS y de 005930.KS para la
misma sesión son el par de feriado y las dos cuentan).

1. **Reporte de Telegram de las 18:25:** «Track record (modelo 4.6.0, 30d): N=133+k · gap … · sesión … · MAE …». La N
   es la de esta consulta y NO la de la vieja (que daría 141+k, con las 8 del 28-sep, hasta el 28-oct):
   ```sql
   SELECT COUNT(*) FROM verificacion_apertura v
   LEFT JOIN senales_ticker s ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
   WHERE v.legacy = 0 AND v.modelo_version = '4.6.0' AND v.gap_pct IS NOT NULL
     AND v.fecha_senal >= date('2026-10-12', '-30 days')
     AND NOT (s.available_at > s.timestamp_utc);          -- la N del reporte; sin el NOT da la vieja (+8)
   ```
   «Cobertura del intervalo 80%: … (n=482+k')», con k' las de las 7 con intervalo sellado (todas lo tienen): n ≥ 482.
   Si el reporte dijera N=141+k o n=490+k', el reporte no lee de la fuente única.
2. **`/api/historial` (y `/api/hoy` `track_record`):** `metricas.n` igual a la N del reporte; `calibracion.n` igual a la
   cobertura del reporte; `wilson.gap.n` = 482 + k; `evolucion` sin la fila `2026-09-28`; `ultimas` (100) sin ninguna fila
   del 28-sep; `por_region` y `por_regimen` suman 482 + k y no traen «sin régimen sellado» por el 28-sep;
   `puntaje_ia.n` = 1288 + p, con p las filas nuevas de `verificacion_puntaje` del lunes (candidatas: 24 del 5-oct, 2 del
   1-oct, 3 del 2-oct; p ≤ 29) y **0 invertidas dentro** (hoy 1308 con la ventana de hoy). Comprobación de las
   invertidas: `SELECT COUNT(*) FROM verificacion_puntaje v JOIN senales_ticker s ON s.fecha = v.fecha_senal AND s.ticker =
   v.ticker WHERE s.available_at > s.timestamp_utc;` → 0.
3. **Dashboard (Streamlit, si se abre):** las mismas cifras que la API (misma función); la tarjeta «Track record gap
   (30d)» con el mismo n. Si alguien lo abre y el fallback se niega por regla, `data/snapshot.log` tendrá un bloque
   `snapshot.py (origen=dashboard, …) [fallback del dashboard, app.py]` con la línea `NEGATIVA DECLARADA […]` (R9); el lunes
   normal NO tendrá ese bloque porque el job de las 18:15 sella antes.
4. **Las 8 filas del 28-sep siguen en `verificacion_apertura`** (`SELECT COUNT(*) FROM verificacion_apertura WHERE
   fecha_senal = '2026-09-28'` → 8) y siguen `verificada`: ninguna fila sellada se reescribe; sólo dejan de contar.
5. **Vigía 19:00:** sin cambio por la 16-3 (no se tocó); las predicciones de la 16-1 (`bitacora_16_1.md` §7) siguen vigentes.
6. **`/sellos`:** «intentos no verificables: 0; último: ninguno» hasta el primer disparo con timing roto en E0.3 (la tabla
   nace el martes 00:30 con 0 filas, acta §103.6).
7. **Hallazgo lateral del auditor, para el adversario (tarjeta §87):** de las 7 verificaciones del lunes, las de 000660.KS,
   005930.KS y 2330.TW emitidas el 8 y el 9-oct apuntan a la misma sesión (12-oct): tres pares de feriado dentro de la
   ventana, que la deduplicación firmada conserva (los dos calzan). El n sube en 3 sin tres observaciones
   independientes. Consulta, PARA DESPUÉS del verificador del lunes (hoy esas filas están `pendiente` y devuelve 0; sin el
   filtro de estado ya devuelve las tres): `SELECT ticker, sesion_objetivo, COUNT(*) FROM senales_ticker WHERE fecha IN
   ('2026-10-08', '2026-10-09') AND estado = 'verificada' GROUP BY 1, 2 HAVING COUNT(*) > 1;` → tres filas con 2.

---

## 8. Cierre

### 8.1 `guardian-constitucion` (`dictamen_16_3/guardian_cierre.md`, 21:24:08 → 21:59:45): APROBADO CON EXIGENCIAS

Ninguna regla dura rota: `motor.py`, `senales.py`, `snapshot.py`, `universo.py` y el vigía byte a byte HEAD (sha256
contra `git show HEAD:`); huellas de las tres bases idénticas a las de apertura al abrir y al cerrar su revisión; cero
sentencias de modificación o DDL en las líneas agregadas; cero empujes al remoto, `pull` o `commit` en 17.691 líneas;
índice limpio; `main`; sin secretos; sin cambios en `dinero/`, `corredor/`, `systemd/`, `.claude/`, `.env`; los ocho
timers con los NEXT de §0.1; los doce bloques de la ventana sellada intactos; el acta sin firmas y con la letra de §93.4
contra el hecho; las tarjetas §82 a §89 cubren el encargo §7.4. Regla 13: no se activa (ningún archivo protegido tocado;
el parche de `dinero/` lleva test y tarjeta). Frontera: acepta la Z7 del auditor A y juzga en verde D, E y F. **Dos
BLOQUEANTES:** (B1) un rojo NUEVO en el árbol real, nacido después de la suite de las 21:09:42:
`test_epistemico::test_ninguna_cita_por_numero_de_linea_a_decisiones_quedo_desplazada`, por dos citas a `DECISIONES.md`
por número de línea (en esta bitácora §5.3 y en `curador_readme.md`) escritas en líneas que llevan otro `§` antes, que el
detector toma como la sección citada; factualmente correctas, pero rojas; y la lección: los 35 tests que se volvieron a
correr tras el curador no eran los que leen los documentos tocados (`DECISIONES.md` lo leen once archivos de test;
`api/CONTRATO.md`, dos; `espera_firma.md`, uno). (B2) la lista de §9 decía 50 rutas y en disco había 56 (el `--short`
colapsa la carpeta del dictamen), más su propio dictamen: 57. **Siete de registro:** R1 `data/sonda_cierre.csv` no lo
commitea el backup (pathspec `data/backups`; lo commitearon a mano las corridas 14 y 15); R2 las cuentas de nodos de §3
estaban viejas (32, 14, 4, 6 = 56); R3 la frase de estado mental sobrevivía en la tarjeta §82; R4 la consulta de §7.7
devuelve 0 hoy (las filas están `pendiente`); R5 inventario de dos cifras retiradas preexistentes en `.py` que el diff no
toca, con la causa estructural (el árbitro de la suite sólo mira cinco `.md`); R6 la cobertura por dictamen faltaba en
las viñetas D y E del acta; R7 el acoplamiento del ISO malformado, aceptado declarado.

### 8.2 Exigencias atendidas, suite final y huellas al cerrar

- **B1:** las dos citas pasaron a sección (`§104`, `§102.1`); `grep "DECISIONES.md:[0-9]"` sobre los documentos nuevos y
  tocados: 0. Suite completa del árbol real sobre el estado FINAL, más `tests/test_motor.py`: [número y hora abajo, en
  8.3]. Regla que queda escrita: un documento tocado después de la suite exige volver a correr los tests que lo leen,
  censados con `grep`, no de memoria; y el último Write también necesita una suite.
- **B2:** §9 regenerado desde `git status --porcelain` con la carpeta del dictamen expandida: 57 rutas, incluido
  `guardian_cierre.md`, y la frase del conteo corregida.
- **R1:** §9 dice ahora lo que es: `data/sonda_cierre.csv` (+4.140 líneas desde el 29-sep) no lo commitea el backup;
  dentro de este commit o declarado fuera, decisión de Nicolás. **R2:** cuentas de §3 corregidas (32, 14, 4, 6). **R3:**
  §82 con la misma redacción que §2 (orden de método DECLARADO; dirección computable al redactar, DECLARADA). **R4:**
  §7.7 dice «para después del verificador del lunes; hoy devuelve 0». **R5:** hallazgo (6) del acta §104.5; tarjeta en
  una corrida posterior. **R6:** cobertura por dictamen en las viñetas D y E del acta. **R7:** ya declarado en §82 (iii).
- Los cuatro worktrees (`wt163`, `wt163_ctrl`, `wt163_diag`, `wt163_dinero`) removidos (`--force` en `wt163`, por los
  cambios sin commitear y los dos archivos fugados, que mueren con él) y podados: [hora en 8.3].

### 8.3 Cierre

- **Suite completa del árbol real sobre el estado FINAL (B1 del guardián), 22:07:58 → 22:15:53: 1207 passed, 8 skipped,
  1 xfailed, 0 failed, 29 warnings, en 474,48 s, `EXIT 0`** (`evidencia/suite_arbol_real_final.txt`); igual a la de las
  21:09:42 en número: el rojo de `test_epistemico` que el guardián midió a las 21:41 ya no está. `tests/test_motor.py`
  después: las seis funciones del motor idénticas con y sin datos futuros, `EXIT 0` (`evidencia/test_motor_final.txt`).
- Después de esa suite sólo se tocaron esta sección (§8.3), §9 y la línea de la suite final en el acta §104.1: por la
  regla del guardián, se volvieron a correr los diez archivos de tests que leen `DECISIONES.md` o esta bitácora
  (censados con `grep -rln`), más `test_readme.py` y `test_cifras_arbitro.py`: **277 passed, 1 skipped, 1 xfailed, 0
  failed, en 271,37 s** (22:16:55 → 22:21:26). Esta línea y el conteo de §9 (59 rutas, con las dos evidencias de la
  suite final) son el último Write; después de ellos se volvió a correr `tests/test_epistemico.py` (el que lee esta
  bitácora en busca de citas por número de línea): 17 passed, 1 skipped, 1 xfailed in 5.04s (22:21:57).
- Huellas de las tres bases al cerrar (22:16:14), idénticas a las de apertura (§0.2):
  `senales.db` `98a048de1dbd6d8c6f53821ad2e879c307cc1d536c64e0dfbb79f90b2f72ced8`, `noticias.db`
  `1829b61b0233b03e493939c5d4b8b56c803a0c6965042d8c9006cc4362336d4c`, `dinero/sello_dinero.db`
  `2a016c523adf6542d5b44dd081c54bfa9bc54456c8c554cd6b69772f6585a636`.
- Worktrees removidos (`--force` en `wt163`) y podados a las 22:07:58; `git worktree list` sólo muestra el árbol real,
  `ad4b829 [main]`. `git log --oneline -1`: `ad4b829`; nada commiteado, nada pusheado.

### 8.1 Lo que esta corrida NO hizo, para que no viva en la memoria de nadie
- No aplicó el parche de `dinero/` (`version_reglas_16_3.diff`): queda para una noche sin otro cambio al sellador
  (tarjeta §89); `dinero/` del árbol real está byte a byte como HEAD.
- No tocó `senales.py` (las seis funciones viejas siguen ahí, sin consumidor publicado; tarjeta §82.2), ni el vigía (R6,
  §80.5 y S2 van en un toque con firma, §83 y §86), ni `snapshot.py` (R3, §84).
- No aplicó la deduplicación firmada a las cifras vivas (§82.1) ni ninguna regla nueva sobre las 16 filas de días sin
  sesión (F4, §87): las dos mueven cifras y son decisión de Nicolás.
- No regeneró `backtest/resultados/linea_base/*.md` (el informe del árbitro; su `cargar()` no cambió).
- No pudo borrar los dos archivos que su propio test fugó al `data/backups/` DEL WORKTREE (`rm` denegado; mueren con el
  worktree) ni las `senales.db`/`noticias.db` vacías que el primer `pytest` de `test_api.py` dejó en el worktree a las
  19:53 (antes de su fixture); el árbol real no tiene ninguno de los cuatro.

---

## 9. Lista exacta de archivos para el commit (una ruta por línea; el commit lo hace Nicolás, antes de las 17:50 del lunes)

```
DECISIONES.md
ESTADO.md
GEMELO/propuestas/parches/version_reglas_16_3.diff
GEMELO/propuestas/parches/version_reglas_16_3.md
GEMELO/resultados/bitacora_16_3.md
GEMELO/resultados/dictamen_16_3/auditor_fuente_unica.md
GEMELO/resultados/dictamen_16_3/auditor_version_reglas.md
GEMELO/resultados/dictamen_16_3/curador_readme.md
GEMELO/resultados/dictamen_16_3/evidencia/aplicacion.txt
GEMELO/resultados/dictamen_16_3/evidencia/aplicar_16_3.sh
GEMELO/resultados/dictamen_16_3/evidencia/badges_readme_salida.txt
GEMELO/resultados/dictamen_16_3/evidencia/badges_y_readme.sh
GEMELO/resultados/dictamen_16_3/evidencia/creadores_de_bases_en_worktree_sin_bases.tsv
GEMELO/resultados/dictamen_16_3/evidencia/detector_bases.py
GEMELO/resultados/dictamen_16_3/evidencia/medicion_antes.txt
GEMELO/resultados/dictamen_16_3/evidencia/medicion_despues.txt
GEMELO/resultados/dictamen_16_3/evidencia/medir_antes.py
GEMELO/resultados/dictamen_16_3/evidencia/medir_despues.py
GEMELO/resultados/dictamen_16_3/evidencia/pytest_fuente_unica_sobre_HEAD.txt
GEMELO/resultados/dictamen_16_3/evidencia/pytest_version_reglas_sobre_HEAD.txt
GEMELO/resultados/dictamen_16_3/evidencia/suite_arbol_real_apertura.txt
GEMELO/resultados/dictamen_16_3/evidencia/suite_arbol_real_despues.txt
GEMELO/resultados/dictamen_16_3/evidencia/suite_arbol_real_final.txt
GEMELO/resultados/dictamen_16_3/evidencia/suite_worktree_HEAD_puro.txt
GEMELO/resultados/dictamen_16_3/evidencia/suite_worktree_con_cambios_1.txt
GEMELO/resultados/dictamen_16_3/evidencia/suite_worktree_con_cambios_2.txt
GEMELO/resultados/dictamen_16_3/evidencia/suite_worktree_con_cambios_3.txt
GEMELO/resultados/dictamen_16_3/evidencia/test_motor_final.txt
GEMELO/resultados/dictamen_16_3/guardian_cierre.md
GEMELO/resultados/espera_firma.md
GEMELO/resultados/tesis.md
README.es.md
README.md
alertas.py
api/CONTRATO.md
api/main.py
app.py
backtest/linea_base.py
docs/readme/README.en.tmpl.md
docs/readme/badges_congelados.json
frontend/src/vistas/SellosDinero.tsx
tests/bases_de_prueba.py
tests/conftest.py
tests/test_api.py
tests/test_banco_clausulas.py
tests/test_bifurcaciones.py
tests/test_conocibilidad.py
tests/test_epistemico.py
tests/test_fallback_dashboard_16_3.py
tests/test_frescura.py
tests/test_fuente_unica_16_3.py
tests/test_guarda_puntaje.py
tests/test_higiene_bases_16_3.py
tests/test_importador_roundtrip.py
tests/test_integridad_no_verificable_16_3.py
tests/test_linea_base.py
tests/test_reporte.py
tests/test_restaurar_backup.py
tests/test_segundo_sello.py
```

(59 rutas: `git status --porcelain` del árbol real al cierre con la carpeta `dictamen_16_3/` expandida archivo por
archivo, sin `data/`; B2 del guardián: el `--short` colapsa la carpeta en una línea y de ahí salió un conteo corto de 50.)
`DECISIONES.md` lleva el acta §103 (anexada por Nicolás antes de lanzar) y la de cierre §104. **Lo que queda fuera y
quién lo commitea (R1 del guardián):** `data/backups/sello_dinero.csv` y `data/backups/sello_dinero_ext/ext_2026-10-09.{csv,meta.json}`
los commitea el backup del lunes 18:40 (pathspec `data/backups`); **`data/sonda_cierre.csv` NO lo commitea el backup**
(está fuera de esa carpeta; lo commitearon las corridas 14 y 15, a mano): +4.140 líneas de la sonda desde el 29-sep que
quedan en la mano de Nicolás, dentro de este commit o declaradas fuera. El hook pre-commit corre la suite (~8 min; 1216
recolectados): conviene commitear el domingo de noche o el lunes antes de las 17:50; entre 17:50 y 20:30 de un día hábil
el hook lo rechaza (regla de la casa). El parche `GEMELO/propuestas/parches/version_reglas_16_3.diff` va en el commit
como ARCHIVO (no aplicado): `dinero/` del árbol real no está en esta lista porque no cambió.
