# Bitácora de la corrida 16-2 — el camino T de §62 rebasado sobre el sellador de la 16b, con B2 (actas §93.7, §99.2, §99.8)

> Domingo 11-oct-2026, de día, con Nicolás presente. Encargo: `~/encargo.md` (escrito por el asistente del chat a las
> 15:30 sin leer el código; primer `date` de la corrida: 15:15:38). Orquestador: Fable 5.1, esfuerzo alto, elegidos al
> arrancar. Horas de Chile leídas de `date`. Nada se pusheó, nada se commiteó, nada se firmó, nada se operó; ninguna
> unidad de systemd se tocó; el sellador real no se corrió; `dinero/sello_dinero.db` se abrió sólo en `mode=ro`; la
> lista de permisos de §99.7 rigió y ningún permiso denegado se rodeó. **`dinero/sello_dinero.py`, `dinero/reglas.json`,
> `api/` y `frontend/` del árbol real NO cambiaron**: todo se entrega como parches en `GEMELO/propuestas/parches/`.

**PRIMERA LÍNEA (estado al cierre): tres parches listos para la mano de Nicolás, en este orden: `camino_T_16_2.diff`,
`b2_contrato_16_2.diff`, `b2_api_16_2.diff`.** Aplican limpio sobre HEAD `c271822` (verificado en un worktree aparte,
huellas idénticas al de trabajo). Aplicarlos exige el acta de aplicación de §93.7 (párrafo para esa acta en §6) y debe
ocurrir ANTES del sello del martes 13-oct a las 00:30 Chile si se quiere que la primera noche con T sea la sesión del
12-oct. Dictamen del `auditor-lookahead`: APLICABLE CON EXIGENCIAS, con R1 y R2 plegadas y las dos bloqueantes (de acta y de secuencia) atendidas en §6 (§4). Suites: §5. Tarjeta nueva **§81**; acta de cierre **§101**.

---

## 0. Reloj, orientación y lecturas de sólo lectura

### 0.1 Reloj y timers (15:15:38)

`date`: `Sun Oct 11 15:15:38 -03 2026`. `systemctl --user list-timers --no-pager`, sólo las unidades `mki-*`:

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

Ningún job `mki-*` dispara antes del lunes 12-oct a las 17:50, como el encargo esperaba. El próximo sello de E0 es el
martes 13-oct a las 00:30 Chile (lunes 12-oct 23:30 NY). `mki-sello-dinero.timer`: `OnCalendar=Mon..Fri 23:30
America/New_York`, `Persistent=true`, `AccuracySec=1s`; el servicio es `Type=oneshot`.

### 0.2 Árbol de git

`git log --oneline -4`: HEAD `c271822` (corrida 16-1 y actas §98 a §100), sobre los backups `864606c`, `f424e8d`,
`d701d22`. `git status --short`: `M data/backups/sello_dinero.csv`, `M data/sonda_cierre.csv`,
`?? data/backups/sello_dinero_ext/ext_2026-10-09.{csv,meta.json}`: sólo `data/`, como el encargo admite. Un solo
worktree registrado (el árbol real).

### 0.3 Suite completa al abrir (árbol real, HEAD, todas las bases)

`venv/bin/python -m pytest tests/ -q -p no:cacheprovider`, lanzada 15:15:40: **1116 passed, 5 skipped, 1 xfailed,
29 warnings en 468,14 s, exit 0** (`dictamen_16_2/evidencia/suite_arbol_real_apertura.txt`). El número que el
encargo esperaba.

### 0.4 Lo leído antes de escribir una línea (encargo §0.1)

`DECISIONES.md` §90.6, §93 (93.7 con el texto B3), §96, §97, §98, §99 (99.1, 99.2, 99.7, 99.8), §100;
`espera_firma.md` §62, §75, §79, §80; `politica_evidencia_no_verificable.md`, `sello_no_verificable.md` y el `.diff`
(1324 líneas, leído entero); `dictamen_15/auditor_parche_sello.md`; `bitacora_16b.md` entera; `bitacora_16_1.md`
entera; `api/CONTRATO.md` entero. Código: `dinero/sello_dinero.py` entero (776 líneas, HEAD), `tests/test_sello_dinero.py`
entero (622), `tests/test_toely_fuera_insumo_e0.py`, `api/main.py` (`/api/dinero/sellos`), `frontend/src/lib/tipos.ts`
(`DatosSellosDinero`), `frontend/src/vistas/SellosDinero.tsx`, `tests/test_frontend_estatus.py`, `tests/test_dinero.py`
(aislamiento y endpoints), `GEMELO/propuestas/test_parches_en_worktree.py`, la unidad y el timer instalados de
`mki-sello-dinero`, el journal del 6 y 7-oct, `.claude/settings.local.json`.

### 0.5 Base real al abrir (`mode=ro`, 15:16)

Tablas: `sellos_dinero`, `divergencias_sello`, `sqlite_sequence`; **no existe `intentos_no_verificables`**. 22 fechas
selladas, todas `version_sello = E0.2`; cuentan para N: **12**. Las dos fechas quemadas (encargo §0.4):

| fecha | filas | `timestamp_utc` | `available_at` | apertura objetivo | `estado` | `sellador_sha256` | `reglas_sha256` | sin dato |
|---|---|---|---|---|---|---|---|---|
| 2026-09-28 | 33 | 17:43:01.001Z (14:43 Chile, 13:43 NY) | 2026-09-28T20:00Z | 2026-09-29T13:30Z | `no_verificable_timing` / `roto` | `480fbdc9…` | `125a8602…` | TOELY (último cierre 24-sep) |
| 2026-10-07 | 32 | 13:31:04.897Z (10:31 Chile, 09:31 NY) | 2026-10-07T20:00Z | 2026-10-08T13:30Z | `no_verificable_timing` / `roto` | `cd0e70c8…` | `b6080eee…` | SHECY (último cierre 6-oct) |

Las dos con `insumo_completo = 0`, `cuenta_para_N = 0`, `estado_dia = sesion`. Tres divergencias registradas (9-sep,
28-sep, 7-oct), las dos últimas con `decisiones_distintas = 0` y «contenido divergente NO conservado». Journal de
`mki-sello-dinero`: disparo normal a las 00:30 del 6-oct (systemd[317]); boot nuevo; disparo de recuperación a las
**10:30:55 del 7-oct** (systemd[319]), terminado 10:31:05. El 6-oct no tiene filas (§99.1).

### 0.6 Worktrees y permisos

- `wt162` (trabajo) y `wt162_head` (control, HEAD puro), creados 15:19 sobre `c271822`; `venv` y `GEMELO/cache`
  enlazados, las dos corridas selladas de `backtest/resultados/` copiadas (permitido, como en la 16-1).
- **Copiar `dinero/sello_dinero.db` al worktree: DENEGADO** (una vez, con la forma exacta `cp dinero/sello_dinero.db <wt>/dinero/`
  de la lista de §99.7). No se insistió. Rige §95.5: juzga la suite del árbol real con las bases y el control sobre HEAD
  puro en el worktree. Consecuencia: los tests de integridad sobre la base real se saltan en los worktrees.
- `wt162_check` (15:31): HEAD puro donde se aplicaron los tres parches en orden desde los `.diff`, para verificar que
  lo que se entrega reproduce byte a byte el worktree de trabajo.

---

## 1. Método, con horas

- **15:19:40 `git apply --check` del parche viejo sobre HEAD: exit 0.** `git apply --3way`: «Applied patch to
  'dinero/sello_dinero.py' cleanly», ídem `tests/test_sello_dinero.py`, cero marcas de conflicto. Hallazgo: el rebase
  es **semántico, no mecánico**: la 16b no tocó ninguna línea de contexto del parche de la 15, pero sus tests nuevos
  (sección 5) fijaban `== 33` y el universo es de 32.
- **15:20: 15 literales `33` de la sección 5 y de dos tests adaptados pasan a `N_OPERABLES`** (la constante que la 16b
  dejó en el archivo; el comentario histórico «marcó las 33 filas» del 28-sep se conserva, era cierto entonces).
- **15:21 a 15:23: `tests/test_camino_T_16_2.py` escrito ANTES de tocar código propio** (271 líneas; el único código
  en el worktree era el del parche de la 15 aplicado por `git apply`): (i) el 28-sep con los relojes reales
  (17:43:01Z) sobre 32 operables; (ii) **el 7-oct**: recuperación a las 13:31:04Z del martes con la barra intradía y
  SHECY sin dato, la sesión del lunes sin ningún disparo; (iii) TOELY con T (no entra a la tabla de intentos; su
  ausencia no vuelve incompleto un intento; otro faltante sí lo vuelve); (iv) recuperación en sábado con el cierre del
  viernes (control: pasa también sobre HEAD); (v) la base real en `mode=ro`: las filas rotas de la principal son
  anteriores al corte y siguen ocupando su fecha. Helper `_congelar` con `inspect.signature` para que HEAD falle por
  conducta y no por `TypeError`.
- **15:24:15, HEAD puro (`wt162_head`): 4 failed, 1 passed, 1 skipped** (`evidencia/pytest_nuevos_sobre_HEAD.txt`).
  Los cuatro por conducta: «EL 28-SEP: … resultado='divergencia_registrada'», «EL 7-OCT: … resultado=
  'divergencia_registrada'», y dos `'sellada' == 'intento_no_verificable'`. El que pasa es el control del sábado; el
  saltado, el de la base real ausente.
- **15:24:20, worktree con el parche: 1 failed, 55 passed, 10 skipped.** El rojo: `test_toely_fuera_insumo_e0.py::
  test_la_ventana_horaria_sigue_mandando_con_toely_fuera` (`KeyError: 'insumo_completo'`): sellaba TARDE con evidencia
  de nombre canónico, que en E0.3 es `rechazado_evidencia_canonica` (cero filas, decisión 1 del implementador). Es la
  única interacción mecánica entre la 16b y T: **adaptado** a las 15:26 con el porqué en su docstring (la evidencia
  nace `.no_verificable`, como la escribe `congelar_extension` con timing roto; lo que fija no cambia: insumo completo
  con sólo TOELY faltante y la regla maestra mandando; gana `resultado == intento_no_verificable` y
  `excluidos_universo == ["TOELY"]`). → 9 passed, 1 skipped.
- **15:27:30: etapa 1 congelada** (`camino_T_16_2.diff`). Un error propio corregido en el acto: el primer `git add -A`
  del worktree incluyó los dos enlaces simbólicos (`venv`, `GEMELO/cache`: los patrones del `.gitignore` llevan barra
  final y no cazan un enlace); se sacaron del índice con `git rm --cached` y el diff se regeneró. Huella del sellador
  con sólo el camino T: `4b4949667fb7c0d4b24016b8b32489761bacd09a6f0f439d24c493e993178414`.
- **15:27: `auditor-lookahead` lanzado** sobre el worktree, con las seis preguntas obligatorias (§4). **15:27: suite
  completa de control sobre HEAD puro** (`wt162_head`, sin bases) en segundo plano.
- **15:29: B2, etapa 2: la enmienda 16-2 de `api/CONTRATO.md` PRIMERO** (45 líneas: las tres claves nuevas de
  `datos.E0`, su fuente, lo que un intento nunca toca, la regla «se muestra como lo que es, nunca como sello», el
  comportamiento con la tabla ausente). Congelada como `b2_contrato_16_2.diff` antes de tocar la API.
- **15:30: B2, etapa 3:** `estado()` gana `ultimo_intento` (mismas claves que `ultimo`, `None` sin tabla o sin
  intentos; la lectura no crea la tabla); `/api/dinero/sellos` sirve `intentos_no_verificables`, `ultimo_intento` y
  `nota_intentos` dentro de `E0` (constante `NOTA_INTENTOS_E0`; la API no computa: lee `estado()`); `tipos.ts` refleja
  las tres claves y extrae `UltimoSelloDinero` como interfaz nombrada (`ultimo_sello` y `ultimo_intento` la comparten).
  `tests/test_b2_intentos_visibles_16_2.py` (8 tests): `estado()` con y sin tabla, el último intento por `id` con dos
  fechas, la API con un intento adentro (nunca entra a `sesiones_selladas`, `filas`, `ultimo_sello` ni
  `decisiones_proxima_apertura`), la API con una base anterior a E0.3 (0 y `null`, y la lectura NO crea la tabla),
  las claves viejas de `E0` intactas, el contrato y los tipos declaran las tres claves, la frase nueva no insinúa
  resultado, y la API lee de `estado()` y no consulta la base por su cuenta.
- **15:31:03: `test_b2…`, `test_camino_T…` y los endpoints: 18 passed, 1 skipped, 2 failed de ENTORNO**
  (`test_frontend_estatus::test_las_frases_fijas…` y `test_dinero::test_los_tres_endpoints…`: `KeyError: 'gap_pct'` en
  `rieles()`, que lee `senales.db`, ausente en el worktree; los dos están en la línea base de rojos de HEAD puro de la
  16-1 y de esta corrida, §5). La frase nueva se cubre con un test propio sobre el payload de `dinero_sellos()`.
- **15:31:40: etapa 3 congelada** (`b2_api_16_2.diff`); **los tres parches aplicados en orden sobre HEAD limpio en
  `wt162_check`: `--check` y `apply` limpios los tres; las ocho huellas sha256 de los archivos tocados son IDÉNTICAS
  a las del worktree de trabajo.** `tsc --noEmit -p tsconfig.app.json` sobre el `tipos.ts` parcheado: exit 0 (15:31:43).
- **15:31:40: suite completa del worktree con los tres parches** en segundo plano (§5). **15:32:58: los siete tests
  de aislamiento del arnés de parches** (`test_el_camino_de_sellado_no_importa_GEMELO`, `…no_importa_dinero`,
  `test_dinero_no_importa_el_camino_de_sellado`, `test_gemelo_no_importa_el_camino_de_sellado`, órdenes reales,
  palabra prohibida, SIMULADO) sobre `wt162_check`: **7 passed**.
- **15:33:** `sello_no_verificable.md` (la nota del parche de la 15) recibe una nota fechada «SUPERADO» que remite a
  los tres parches nuevos; el `.diff` viejo se conserva como historia.

---

## 2. Qué hace cada parche

### 2.1 `camino_T_16_2.diff` (1797 líneas tras plegar R1/R2; `dinero/sello_dinero.py`, `tests/test_sello_dinero.py`, `tests/test_toely_fuera_insumo_e0.py`, `tests/test_camino_T_16_2.py` nuevo)

El mecanismo es EXACTAMENTE el de la corrida 15 (`sello_no_verificable.md` lo describe función por función; nada de
eso cambió): `VERSION_SELLO = "E0.3"`; `_ddl_filas(tabla)` + `init_db` crea `intentos_no_verificables` con las
mismas 35 columnas, la misma `UNIQUE` y los mismos disparadores, todo `IF NOT EXISTS`; `evaluar_timing()` una sola
fórmula para congelar y sellar; `congelar_extension(…, ahora_utc=None)` decide el timing antes de escribir y con
timing roto escribe `ext_<fecha>.no_verificable.csv` + meta con `cupo_canonico: false` y el bloque `timing`;
`sellar()` con timing roto inserta en la tabla de intentos (`intento_no_verificable`), rechaza la evidencia canónica
con timing roto dejando fila en `divergencias_sello` (B1), `ya_intentada` con el mismo sha (R4), divergencia con
otro; `exportar_csv` agrega `<ruta>_no_verificables.csv`; `estado()` agrega `intentos_no_verificables`; `main()`
imprime los dos relojes y su delta (R5) y respalda el par `.no_verificable`. **Las cuatro decisiones del implementador
de la 15 se conservan tal cual** (rechazo de la evidencia canónica con timing roto; `ya_intentada` con el mismo sha
en vez de divergencia; dos relojes en `main()`; `VERSION_SELLO` a E0.3 y `sellador_sha256` nuevo en las filas nuevas)
**y B1, R2, R3, R4 y R5 siguen plegadas**; ninguna dejó de aplicar sobre el código de la 16b. Lo que la 16b firmó
(§95.4, §97) no se toca: TOELY sigue fuera por `exclusiones_insumo_e0`, cero faltantes tolerados, sin retorno, el
sorteo como lo hace el parche de la 16b; `excluidos_universo` viaja también en el retorno `intento_no_verificable`
porque `sellar()` lo construye con el mismo diccionario.

Interacción TOELY × T, medida con tests: la exclusión se aplica en `decidir()`, ANTES de que `sellar()` elija la
tabla, así que un intento tiene 32 filas sin TOELY, `sin_dato` nunca lo nombra, y un intento con sólo TOELY sin barra
lleva `insumo_completo = 1` (test (iii)); un faltante distinto sigue siendo `insumo_completo = 0` también en un
intento. Un `decisiones_distintas` de una divergencia contra un intento de 33 filas anterior al corte no puede
ocurrir: la tabla de intentos nace con E0.3, después de la 16b.

### 2.2 `b2_contrato_16_2.diff` (53 líneas; sólo `api/CONTRATO.md`)

La enmienda 16-2, escrita antes de tocar la API (regla de la capa). §1 del encargo B.

### 2.3 `b2_api_16_2.diff` (370 líneas; `dinero/sello_dinero.py::estado`, `api/main.py`, `frontend/src/lib/tipos.ts`, `tests/test_b2_intentos_visibles_16_2.py` nuevo)

`estado()` es de sólo lectura y la API no es el sellador (dictamen 15, B2): no consume el presupuesto de «un cambio
por noche al sellador». Pero toca `dinero/sello_dinero.py`, así que **la huella definitiva del sellador depende de
aplicar los tres**: `610f5b05…` con sólo el camino T, `299a7627…` con los tres (corregido por la E1 del guardián: la
primera versión de este párrafo traía las huellas de la etapa 1 anterior al plegado de R1/R2). La vista `/sellos` no muestra las
claves nuevas (tarjeta §81).

Huellas tras aplicar los tres, verificables con `sha256sum` (idénticas en el worktree de trabajo y en un worktree fresco donde se aplicaron los tres `.diff` finales en orden, 16:01:05):

```
299a7627f289e70f8ae3cb83166672c451f0921ca88c21450a87892ae3963d93  dinero/sello_dinero.py
fa7d0651bca496119c25aa4e3480c4288057937c5a0267f76fb4fea69f5b1c2b  api/main.py
9b40b49790837321a3fc011e8cb84e307d66d26a2ac186745a0fb9be86ceed86  api/CONTRATO.md
1a690ee8c2ef9d8ef093930bc4e614c844f3cbccd8764b2caafa2f57f3da48f1  frontend/src/lib/tipos.ts
01dcd57b5e4359c53bc82be6bd06cfff18f5c5f9ed7521fa21a8aefd8f79daeb  tests/test_sello_dinero.py
6a3ecb4b5ab31ebc9d11b9f6250200f8f4f6b98bb13c53133fef3d20aa974cb3  tests/test_toely_fuera_insumo_e0.py
05ab8999ada6a70b378c63c0e8eef952f8b21f4ec108d3c37d3a6d11c794ba48  tests/test_camino_T_16_2.py
5d817300c35c308f10368dfef1174dc83cbc6a5612a58f4a2d2a890b0add75fd  tests/test_b2_intentos_visibles_16_2.py
```

---

## 3. Lo que se descartó, y por qué

- **Unificar los dos relojes de `main()`** (una lectura, pasada a congelar y sellar): no, por la misma razón de fuga de
  la corrida 15 (adelantaría `timestamp_utc` al instante previo al gate). R5 mide el delta en el log.
- **Un candado de archivo** contra dos instancias concurrentes: no se agregó. Es la zona ciega que el auditor
  declaró en la 15 y vuelve a juzgar acá (§4); la unidad es `Type=oneshot` con un solo timer y la lista de permisos
  prohíbe `--sellar` a los agentes, así que la única vía a dos instancias es un `--sellar` manual de Nicolás con el
  timer corriendo. Si el auditor lo hace bloqueante, se pliega; si no, va a la tarjeta.
- **Mostrar las claves nuevas en `/sellos`**: no en esta corrida (decisión de pantalla, tarjeta §81); los tipos sí se
  reflejan para que el contrato y el frontend no diverjan.
- **Mover `version_reglas`**: no, por §99.5 (va en la 16-3; un solo cambio al sellador por noche).

---

## 4. Dictamen del `auditor-lookahead` (15:27:33 a 15:40:44): APLICABLE CON EXIGENCIAS

`dictamen_16_2/auditor_camino_T.md`, íntegro, con sus sondas en `evidencia/sondas_auditor/`. Dictaminó la etapa 1
(sellador `4b494966…`) y midió que B2 entró al mismo worktree a las 15:30:41 bajo su lectura, con el único cambio
dentro de `estado()` (lo declara; B2 va en el addendum, §4.2). Lo que verificó: ninguna ruta escribe en `sellos_dinero`
con `timing_ok` falso (fuente + 6 escenarios en runtime con 0 filas rotas en la principal); ningún canónico se escribe
ni reescribe con timing roto; `--sin-red` no levanta un `.no_verificable.csv` (sale con código 2); los dos disparadores
nacen con la tabla; `init_db` es todo `IF NOT EXISTS`; **los 5 chequeos de integridad permanente contra la base REAL en
`mode=ro` con el módulo parcheado: SIN FALLAS** (lo que los 10 saltados del worktree no probaron); la prueba maestra
sobre el instante que decide tabla y nombre (`evaluar_timing` invariante a las sesiones posteriores, `avail` backward-only
y nunca el reloj de pared); el gate de invariancia INVARIANTE con el `cfg` de la 16b; el test (ii) reproduce las cuatro
piezas del 7-oct contra las filas reales (misma hora de reloj al segundo, `available_at` futuro, apertura del día
siguiente, sesión anterior sin filas). Dos bloqueantes, ninguna de código:
- **B1 (acta):** el camino T cubre UNA de las dos formas del disparo de recuperación, la de timing roto (28-sep, 7-oct).
  La otra, timing OK en día sin sesión (sábado con el cierre del viernes; feriado de XNYS con el cierre de la víspera),
  sella en la principal como `dia_sin_sesion`, `cuenta_para_N = 0`, y ocupa la fecha para siempre, igual que E0.2
  (medido en P5, incluido el 26-nov con media sesión). §99.2 descartó (b) y (c) con una razón cierta para la primera
  forma y falsa para la segunda. El acta de aplicación no puede decir «T resuelve los disparos de recuperación» a
  secas. → párrafo del acta (§6.2) y tarjeta §81.2.
- **B2 (secuencia):** camino T y B2 en la MISMA aplicación, nunca el camino T solo (una noche quemada se vería idéntica
  a un sábado: F1 de la corrida 15 en pie). → receta (§6.1): los tres `.diff` en un acto.
Cuatro fugas demostradas con sonda, ninguna nueva de T: **F1** la carrera entre dos instancias rompe la integridad de
forma idéntica en E0.2 y E0.3 (A y B congelan sobre el mismo path; la fila de A lleva los precios de B porque `sellar`
relee el disco) y es inalcanzable por el timer (`Type=oneshot`, timer único): zona ciega aceptada, R5; **F2** una fila
de intento puede satisfacer la regla maestra en sus tres columnas y decir `roto` si el cierre nominal cae entre los dos
relojes (ventana de 1 a 2 s): R3; **F3** un cambio de `juego_activo` entre dos disparos de la misma fecha insertaba 32
filas citando el temporal que `main()` borra, idéntico en E0.2: R1; **F4** `IF NOT EXISTS` no propaga una columna nueva
a la tabla real, y el test de paridad corría sobre una base fresca: R2. Recomendadas R1 a R5 y un cosmético.

### 4.1 Lo plegado antes de cerrar (15:47 a 15:50; script `evidencia/plegar_R1_R2.py`, idéntico en los dos worktrees)

- **R1:** en `sellar`, justo antes del INSERT, `if meta_ext.get("persistido") is False:` → ninguna fila; una fila en
  `divergencias_sello` con `sha_sellado` = la cita que ocupaba la fecha, `sha_nuevo` = el insumo, `decisiones_distintas =
  NULL` (no hay filas del mismo juego con que comparar; se declara en el detalle) y resultado
  `rechazado_insumo_no_persistido`; `main()` exporta e imprime en esa rama. Test de reproducción de F3 escrito ANTES y
  corrido sobre el camino T sin la guarda: **`AssertionError: F3: sellar insertó filas con juego 'agresivo' … filas_insertadas=32`**
  (`evidencia/pytest_R1_sobre_camino_T_sin_guarda.txt`, 15:48:16).
- **R2:** advertencia en el docstring de `_ddl_filas` (agregar una columna exige migración aparte); test de paridad de
  columnas sobre la base REAL en la sección 4 (salta con razón mientras la tabla no exista; corre la primera noche con
  E0.3); contraprueba que fabrica una `sellos_dinero` sin `insumo_completo`, corre `init_db` y muestra que el
  verificador lo ve y que una base nacida en E0.3 pasa (36 columnas).
- **Cosmético:** `FROM {TABLA_SELLOS}` en la consulta `previas`.
- Nota sobre los mtimes (O1 del guardián): en la regeneración de las 15:48 los tres `.diff` se reescribieron en disco
  (`b2_contrato_16_2.diff` tiene mtime 15:48:54 con la MISMA huella `ad864726…` de las 15:29); lo que §1 registra, que
  el contrato se congeló antes de tocar la API, se sostiene por la huella, no por el mtime.
- **15:48:15: `test_sello_dinero.py tests/test_camino_T_16_2.py tests/test_b2_intentos_visibles_16_2.py tests/test_toely_fuera_insumo_e0.py`: 66 passed, 11 skipped** (`evidencia/pytest_sellador_worktree_final.txt`).
- `camino_T_16_2.diff` regenerado desde un worktree fresco (HEAD + v1 + script); B2 aplica encima sin cambios; los tres
  verificados otra vez en orden sobre HEAD limpio con las ocho huellas idénticas al worktree de trabajo (15:49:51). Sin
  plegar: R3, R4, R5 (tarjeta §81.3 a 81.5).
- **R6 del addendum (16:00):** `UltimoSelloDinero` de `tipos.ts` declaraba 12 campos contra las 21 de `_CLAVES_ULTIMO`
  (deriva preexistente de `ultimo_sello`, heredada por `ultimo_intento`): la interfaz pasa a las 21 y el test de B2 exige
  `campos == set(S._CLAVES_ULTIMO)` (script `evidencia/plegar_R6.py`). `tsc --noEmit` exit 0; `test_b2…` 8 passed.
  `b2_api_16_2.diff` regenerado (370 líneas) y los tres parches verificados otra vez en orden sobre HEAD limpio con las
  ocho huellas idénticas (16:01:05). La suite completa del worktree (§5) corrió ANTES de R6: lo que R6 toca son un
  tipo y una aserción, cubiertos por `tsc` y por el archivo de B2 corridos después.

### 4.2 Addendum del auditor sobre B2 y sobre el plegado

Segunda pasada (15:49:56 a 15:55:19), anexada al mismo archivo: **APLICABLE, cero bloqueantes de código.** R1 cierra F3
sin pisar ninguna rama legítima (las diez ramas alcanzables de `sellar` recorridas con la guarda puesta, integridad en
pie en las diez; la rama legítima «otro juego, MISMO sha» sigue sellando 32 + 32); `decisiones_distintas = NULL` es lo
honesto y ningún consumidor lo agrega; B2 no toca el camino de sellado más que `estado()` (dos hunks), la API no puede
crear la tabla al leer (base E0.2 fabricada: tablas, mtime y sha idénticos tras el GET), ningún contador mezcla un
intento con un sello, ninguna frase nueva insinúa resultado; la contraprueba de R2 muerde (mutación probada). **B2 del
dictamen CERRADA** con los tres parches juntos; **B1 sigue en pie y es de acta** (§6.2). Una recomendada nueva, R6
(las 21 claves en el tipo), plegada después del addendum (§4.1). Discrepancia que el auditor señaló y se acepta: el
worktree `wt162_e1` contenía la pila completa y no «el camino T solo»; su reconstrucción del camino T solo dio
`610f5b05…`, la misma huella que acá se declara.

---

## 5. Suites

| suite | resultado | archivo |
|---|---|---|
| árbol real, apertura, HEAD, todas las bases (15:15:40 → 15:23:28) | **1116 passed, 5 skipped, 1 xfailed, 0 failed**, 468,14 s | `evidencia/suite_arbol_real_apertura.txt` |
| worktree HEAD puro, sin bases (15:27:30 → 15:34:55) | 19 failed, 1012 passed, 84 skipped, 1 xpassed, 6 errors | `evidencia/suite_worktree_HEAD_puro_sin_bases.txt` |
| worktree con los tres parches v1 (antes de R1/R2), sin bases (15:31:40 → 15:39:22) | 19 failed, 1042 passed, 89 skipped, 1 xpassed, 6 errors | `evidencia/suite_worktree_con_parches_sin_bases.txt` |
| worktree con los tres parches FINALES, sin bases (15:48:5x → 15:56:38) | **19 failed, 1044 passed, 90 skipped, 1 xpassed, 6 errors**, 463,27 s | `evidencia/suite_worktree_con_parches_finales_sin_bases.txt` |
| tests nuevos sobre HEAD puro (15:24:15) | 4 failed (por conducta), 1 passed (control), 1 skipped | `evidencia/pytest_nuevos_sobre_HEAD.txt` |
| test de F3 sobre el camino T sin R1 (15:48:16) | 1 failed (por conducta), 1 passed | `evidencia/pytest_R1_sobre_camino_T_sin_guarda.txt` |
| sellador + camino T + B2 + TOELY, worktree final (15:48:15) | 66 passed, 11 skipped | `evidencia/pytest_sellador_worktree_final.txt` |
| aislamiento del arnés de parches sobre HEAD + los tres (15:32:58) | 7 passed | — |

**Comparación por conjuntos (criterio §95.5):** los 25 rojos del worktree con parches son **exactamente los mismos 25** de
HEAD puro (`diff` de las listas ordenadas: vacío): `test_api` (6), `test_cifras_arbitro` (6 errores), `test_readme` (9),
`test_dinero` (2), `test_frontend_estatus` (1), `test_linea_base` (1), todos por bases y artefactos gitignorados
ausentes. **Ningún rojo aparece sólo con los parches.** Con los parches finales (R1/R2 plegadas) el conjunto de 25 rojos vuelve a ser idéntico al de HEAD puro (`diff` vacío, 15:57:10); +32 verdes contra HEAD puro (1044 − 1012) y +6 saltados (los que piden la base real ausente). Recolectados: **1160 con los tres parches
contra 1122 en HEAD (+38 tests)**. La suite del worktree final corrió sobre un `tests/test_sello_dinero.py` que difería
del entregado en UNA línea en blanco final (quitada a las 15:49 para que `git apply` no avise de whitespace; huella final
`01dcd57b…`).

**El árbol real NO recibió código** (sólo parches, dictamen, bitácora, tarjeta, acta): la suite del árbol real al cierre
es la de apertura y se vuelve a correr al cierre para el registro (§8). **PREDICCIÓN para la suite del árbol real con los
tres parches aplicados (nunca corrida):** 1160 recolectados; **1151 passed, 8 skipped, 1 xfailed, 0 failed** (los 5
saltados de hoy, más los 2 parametrizados de integridad de la tabla de intentos y la paridad de columnas sobre la base
real, que saltan con razón declarada hasta la primera noche con E0.3). Si da otra cosa, manda la máquina.

---

## 6. Entrega para la mano de Nicolás

### 6.1 Receta de aplicación (antes del martes 13-oct a las 00:30 Chile; fuera de 17:50 a 20:30 del lunes para el commit)

Los tres parches **en el mismo acto y en este orden** (B2 del auditor: nunca el camino T solo). Antes de nada, por R5:
`systemctl --user is-active mki-sello-dinero.service` tiene que decir `inactive`.

```bash
cd ~/dev/mki-terminal
git status --short                                             # sólo data/ y lo de la 16-2 ya commiteado o por commitear
P=GEMELO/propuestas/parches
sha256sum $P/camino_T_16_2.diff $P/b2_contrato_16_2.diff $P/b2_api_16_2.diff
#   48addf80bc5eecced63af4f916be1eea075834051f0ce4bdfb9aa36d0768f4d4  camino_T_16_2.diff
#   ad864726cf91e2d50f2430cd3f9351d9cff1dfc657a8398304f682c0a0abf45f  b2_contrato_16_2.diff
#   9b4c45d43c848bff11383bf5955a6cfeb748d700f1b08f73fb696b95283e32b5  b2_api_16_2.diff
for d in camino_T_16_2 b2_contrato_16_2 b2_api_16_2; do git apply --check $P/$d.diff || break; done
date                                                           # ESTA es la hora del corte de método (acta)
git apply $P/camino_T_16_2.diff && git apply $P/b2_contrato_16_2.diff && git apply $P/b2_api_16_2.diff
sha256sum dinero/sello_dinero.py api/main.py api/CONTRATO.md frontend/src/lib/tipos.ts \
          tests/test_sello_dinero.py tests/test_toely_fuera_insumo_e0.py tests/test_camino_T_16_2.py \
          tests/test_b2_intentos_visibles_16_2.py                # las ocho huellas de §2.3
venv/bin/python -m pytest tests/ -q                            # PREDICCIÓN: 1151 passed, 8 skipped, 1 xfailed, 0 failed (1160 recolectados)
venv/bin/python tests/test_motor.py                            # anti-look-ahead del motor, en verde
(cd frontend && node_modules/.bin/tsc --noEmit -p tsconfig.app.json)   # exit 0
git status --short                                             # dos tests nuevos sin seguimiento: van en el commit
```

Si la suite real da un rojo que no sea de entorno, **reversión en orden inverso**:
`git apply -R $P/b2_api_16_2.diff && git apply -R $P/b2_contrato_16_2.diff && git apply -R $P/camino_T_16_2.diff`
(y borrar los dos tests nuevos que quedaron sin seguimiento). La tabla `intentos_no_verificables` **no existe hasta el
primer sello en escritura** (`init_db` desde `conectar()`): aplicar y revertir no toca la base.

**Lista exacta de archivos para el commit de la APLICACIÓN** (además de la de esta corrida, §9): `dinero/sello_dinero.py`,
`api/main.py`, `api/CONTRATO.md`, `frontend/src/lib/tipos.ts`, `tests/test_sello_dinero.py`,
`tests/test_toely_fuera_insumo_e0.py`, `tests/test_camino_T_16_2.py`, `tests/test_b2_intentos_visibles_16_2.py`, más el
acta de aplicación en `DECISIONES.md`. El hook pre-commit corre la suite entera (~8 min); entre 17:50 y 20:30 de un día
hábil la rechaza.

### 6.2 Para el acta de aplicación (§93.7): lo que Nicolás tiene que tener a la vista al firmar

El acta fija **fecha y hora del corte de método** (la del `date` previo al `git apply`, o el `stat -c '%y'` de
`dinero/sello_dinero.py` si ese paso se saltó, como en §98.1) y declara: **(1) las cuatro decisiones del implementador
de la corrida 15**, conservadas tal cual (rechazo de la evidencia canónica con timing roto, con fila en
`divergencias_sello`; `ya_intentada` con el mismo sha, sin fila; dos relojes en `main()`, con el delta medido en el log;
`VERSION_SELLO = E0.3` y `sellador_sha256` nuevo en las filas nuevas, sin reescribir ninguna vieja); **(2) el texto B3 de
§93.7**, literal: el camino T **sustituye** el mecanismo de §90.6 (a), no lo implementa; `sello_previo()` no distingue
estados y no hace falta que lo haga; el efecto firmado se cumple; el mecanismo es otro; **(3) el corte de método es
`VERSION_SELLO = E0.3`**, y la huella del sellador que las filas nuevas llevan es la del archivo APLICADO con los tres
parches (`299a7627f289e70f8ae3cb83166672c451f0921ca88c21450a87892ae3963d93`; con sólo el camino T sería `610f5b05…`,
que no es la combinación firmada); **(4) lo que cambia del dictamen de la corrida 15 al de hoy:** las bloqueantes de
código de la 15 (B1) y sus recomendadas R2 a R5 están plegadas desde entonces; el dictamen nuevo agrega **R1 y R2 plegadas**
(guarda `persistido`, paridad de columnas sobre la base real) y dos bloqueantes que no son de código: **B1, la cobertura
declarada sin exceso**: el camino T cubre el disparo de recuperación con timing roto (el 28-sep y el 7-oct) y NO el que
cae con timing OK en un día sin sesión, que sigue sellando `dia_sin_sesion` en la principal y ocupando la fecha (§57 tal
como está; tarjeta §81.2); **B2, la secuencia**: los tres parches en el mismo acto. **(5)** Lo que no cambia: las sesiones
del 28-sep, 6-oct y 7-oct siguen perdidas (§57, §86.1, §99.2); N sigue en 12 hasta el primer sello con E0.3;
`version_reglas` no se mueve (§99.5, 16-3); el timer no se toca.

---

## 7. Predicción falsable para el sello del martes 13-oct a las 00:30 Chile (si los tres parches están aplicados)

**Sesión del 12-oct sellada en `sellos_dinero`** con `version_sello = E0.3`, `sellador_sha256 =
299a7627f289e70f8ae3cb83166672c451f0921ca88c21450a87892ae3963d93`, `reglas_sha256 = b6080eee…` (sin cambio),
**32 filas** sin TOELY, `estado = pendiente`, `insumo_completo = 1`, `cuenta_para_N = 1`, `timestamp_utc` ≈
`2026-10-13T03:30:0xZ`, `available_at = 2026-10-12T20:00:00+00:00`, `sesion_objetivo = 2026-10-13`; **el contador de
sesiones que cuentan pasa de 12 a 13**. Salvo que falte OTRO ticker: entonces `insumo_incompleto` con ese nombre en el
motivo, 32 filas, contador en 12. La tabla **`intentos_no_verificables` existe con 0 filas** y sus dos disparadores;
`estado()` devuelve `intentos_no_verificables: 0` y `ultimo_intento: null`, y `/api/dinero/sellos` los sirve dentro de
`E0`. Nace **`data/backups/sello_dinero_no_verificables.csv` vacío con cabecera** (las 36 columnas), que el backup del
martes 18:40 commitea. `dinero/datos/sello/` gana el par canónico `ext_2026-10-12.{csv,meta.json}` y **ningún**
`.no_verificable.*`. En `data/sello_dinero.log`: la línea `relojes: congelado_en_utc=… timestamp_utc=… delta_s=…` (R5
de la 15) y `"excluidos_universo": ["TOELY"]`. Las filas rotas de la principal siguen siendo 2 fechas, ambas `E0.2`.
**Si los parches NO están aplicados:** 32 filas `E0.2`, sellador `cd0e70c8…`, contador 12 → 13 igual (la noche normal
no distingue las dos versiones), sin tabla nueva ni CSV nuevo, y la causa es la mano, no el sellador. **Qué falsaría la
corrida:** una fila `E0.3` con `estado_timing = roto` en `sellos_dinero`; un `.no_verificable.*` en una noche normal;
`intentos_no_verificables` ausente con el parche aplicado; la API sin las tres claves; un rojo en la suite real que no
sea de entorno.

Consulta exacta (`mode=ro`), martes 13-oct en la mañana:

```bash
cd ~/dev/mki-terminal && venv/bin/python - <<'EOF2'
import sqlite3, os
con = sqlite3.connect("file:dinero/sello_dinero.db?mode=ro", uri=True)
print("tablas:", [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")])
for r in con.execute("""SELECT fecha_insumo, estado, estado_timing, insumo_completo, cuenta_para_N, COUNT(*), version_sello,
       substr(sellador_sha256,1,12), substr(reglas_sha256,1,12), timestamp_utc, available_at FROM sellos_dinero
       WHERE fecha_insumo >= '2026-10-08' GROUP BY fecha_insumo ORDER BY fecha_insumo"""):
    print(r)
print("cuentan para N:", con.execute("SELECT COUNT(DISTINCT fecha_insumo) FROM sellos_dinero WHERE cuenta_para_N=1").fetchone()[0])
print("rotas en la principal:", con.execute("SELECT fecha_insumo, version_sello FROM sellos_dinero WHERE estado_timing='roto' GROUP BY fecha_insumo").fetchall())
try:
    print("intentos:", con.execute("SELECT COUNT(*) FROM intentos_no_verificables").fetchone()[0],
          "| disparadores:", con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND tbl_name='intentos_no_verificables'").fetchone()[0])
except sqlite3.OperationalError as e:
    print("intentos: SIN TABLA (parche no aplicado o sellador sin correr):", e)
print("csv no_verificables:", os.path.exists("data/backups/sello_dinero_no_verificables.csv"))
print("nv en disco:", sorted(a for a in os.listdir("dinero/datos/sello") if "no_verificable" in a))
EOF2
grep -n "relojes:\|INTENTO NO VERIFICABLE\|RECHAZADO" data/sello_dinero.log | tail -3
curl -s localhost:8000/api/dinero/sellos | venv/bin/python -c "import json,sys; e=json.load(sys.stdin)['datos']['E0']; print({k: e.get(k) for k in ('sesiones_que_cuentan_para_N','intentos_no_verificables','ultimo_intento')})"
```

Hoy (11-oct, 15:33) la misma consulta devuelve: tablas `divergencias_sello`, `sellos_dinero`, `sqlite_sequence`; última
sesión 2026-10-09 `pendiente` `E0.2` `cd0e70c80051`; cuentan para N 12; rotas 2026-09-28 y 2026-10-07 (`E0.2`);
`intentos: SIN TABLA`; csv `False`; `nv en disco: []`.

---

## 8. Cierre

- Dictamen del auditor archivado íntegro con su addendum (`dictamen_16_2/auditor_camino_T.md`, 344 líneas) y sus ocho
  sondas (`evidencia/sondas_auditor/`). R1, R2, R6 y el cosmético plegados; B1 en el acta de aplicación (§6.2) y en la
  tarjeta §81.2; B2 en la receta (§6.1). R3, R4 y R5 en la tarjeta §81.
- Acta de cierre: **§101** en `DECISIONES.md`, sin firmas (16:03). Tarjeta nueva: **§81** en `espera_firma.md` (15:54).
  `ESTADO.md` regenerado (49 líneas, 15:58). La nota del parche de la 15 marcada SUPERADA (15:33).
- Suite de cierre del árbol real (código intacto; sólo documentos, parches y evidencia nuevos): **1116 passed, 5 skipped, 1 xfailed, 0 failed, 490,66 s** (16:04:41 → 16:12:53;
  `evidencia/suite_arbol_real_cierre.txt`), igual que la apertura; corrió con el acta §101, la tarjeta §81, la bitácora y
  los tres `.diff` ya en el árbol (los tests que leen `DECISIONES.md` pasan con el acta escrita).
- Guardián: `guardian-constitucion` (16:04:41 a 16:24:36, `dictamen_16_2/guardian_cierre.md`): **APROBADO CON EXIGENCIAS**,
  cuatro exigencias documentales, ninguna de código, parches, bases ni operación, **corregidas en su sitio a las 16:29**
  (la frontera de la errata es el commit): E1 dos huellas viejas en §2.3 (eran las de la etapa 1 antes de R1/R2; ahora
  `299a7627…` y `01dcd57b…`, las que el acta §101.2 ya decía); E2 el largo del diff en §2.1 (1797, no 1661); E3 la lista
  §9 (faltaba `plegar_R6.py`; las sondas son 8, no 6; §101.7 pasa de 21 a 22 rutas); E4 dos citas «§5» de la tarjeta §81
  que debían decir §6.1. O1 (mtime de `b2_contrato_16_2.diff`) declarada en §4.1. Lo que el guardián midió por su cuenta:
  23 rutas protegidas sin diff, las tres bases byte a byte iguales, ningún timer ni `--sellar`, los tres parches aplican
  limpio en su propio worktree con 66 passed / 11 skipped y `test_motor.py` exit 0 con T puesto, aditividad estricta de
  actas y tarjetas, 0 reintroducciones de cifras retiradas sobre 24 archivos nuevos, 0 secretos, la aritmética de suites
  cierra (1151 + 8 + 1 = 1160). Estas correcciones son posteriores a la suite de cierre (16:12:53) y sólo tocan texto;
  el hook pre-commit corre la suite entera otra vez: ése es el juez final (O1 del guardián de la 16-1).
- Worktrees: `wt162`, `wt162_check`, `wt162_e1`, `wt162_head` removidos con `git worktree remove --force` y `git worktree
  prune` a las 16:29:43; `git worktree list` muestra sólo el árbol real. Los tres de verificación (`wt162_chk2/3/4`, `wt162_e0`)
  se removieron al terminar cada verificación; los dos del guardián, él mismo.
- Bases reales al cerrar: `senales.db 98a048de1dbd6d8c…`, `noticias.db 1829b61b0233b03e…`, `dinero/sello_dinero.db 2a016c523adf6542…`
  (16:13:02): **idénticas a las de apertura de la 16-1**, después de la corrida entera, las suites, el auditor y el guardián.
  Ninguna base se escribió.

### 8.1 Lo que esta corrida NO hizo, para que no viva en la memoria de nadie

R3, R4 y R5 del auditor (tarjeta §81.3 a 81.5); la pantalla `/sellos` (§81.6); mover `version_reglas` (§99.5, 16-3);
tocar el timer o `Persistent=` (§81.2 lo deja a Nicolás); correr el sellador real, `--sin-red` incluido; probar Yahoo de
verdad; correr la suite del árbol real CON los parches (es la predicción de §5 y la corre la mano que aplique). La copia
de `dinero/sello_dinero.db` al worktree quedó denegada (§0.6).


## 9. Lista exacta de archivos para el commit de esta corrida (sin código de producción; el commit lo hace Nicolás)

```
DECISIONES.md
ESTADO.md
GEMELO/propuestas/parches/camino_T_16_2.diff
GEMELO/propuestas/parches/b2_contrato_16_2.diff
GEMELO/propuestas/parches/b2_api_16_2.diff
GEMELO/propuestas/parches/sello_no_verificable.md
GEMELO/resultados/bitacora_16_2.md
GEMELO/resultados/espera_firma.md
GEMELO/resultados/dictamen_16_2/auditor_camino_T.md
GEMELO/resultados/dictamen_16_2/guardian_cierre.md
GEMELO/resultados/dictamen_16_2/evidencia/suite_arbol_real_apertura.txt
GEMELO/resultados/dictamen_16_2/evidencia/suite_arbol_real_cierre.txt
GEMELO/resultados/dictamen_16_2/evidencia/suite_worktree_HEAD_puro_sin_bases.txt
GEMELO/resultados/dictamen_16_2/evidencia/suite_worktree_con_parches_sin_bases.txt
GEMELO/resultados/dictamen_16_2/evidencia/suite_worktree_con_parches_finales_sin_bases.txt
GEMELO/resultados/dictamen_16_2/evidencia/pytest_nuevos_sobre_HEAD.txt
GEMELO/resultados/dictamen_16_2/evidencia/pytest_R1_sobre_camino_T_sin_guarda.txt
GEMELO/resultados/dictamen_16_2/evidencia/pytest_sellador_worktree_antes_de_adaptar_16b.txt
GEMELO/resultados/dictamen_16_2/evidencia/pytest_sellador_worktree_final.txt
GEMELO/resultados/dictamen_16_2/evidencia/plegar_R1_R2.py
GEMELO/resultados/dictamen_16_2/evidencia/plegar_R6.py
GEMELO/resultados/dictamen_16_2/evidencia/sondas_auditor/   (8 archivos .py: p1, p2, p2b, p3, p9, p10, q1, q2)
```

**No incluye** `data/backups/sello_dinero.csv`, `data/backups/sello_dinero_ext/ext_2026-10-09.{csv,meta.json}` ni
`data/sonda_cierre.csv` (los commitea el backup del lunes 18:40). Si Nicolás aplica los tres parches antes de commitear,
se suman los ocho archivos de §6.1 y el acta de aplicación.

