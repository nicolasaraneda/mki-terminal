# Dictamen del `guardian-constitucion` — cierre de la corrida 16-2

> Archivado por el orquestador tal como lo devolvió el agente (texto íntegro). Lanzado a las 16:04 de Chile del
> 11-oct-2026 sobre el árbol real (HEAD `c271822`, `main`); devuelto a las **16:24:36**. Sus cuatro exigencias (E1 a E4,
> todas documentales) y la observación O1 se corrigieron en su sitio antes del commit (bitácora 16-2 §8); los dos
> marcadores que el dictamen nombra (`__GUARDIAN__`, `__WORKTREES__`) se rellenaron después.

---

**APROBADO CON EXIGENCIAS**

Rama: `main` · HEAD: `c271822` (sin commits nuevos; reflog tope = `c271822`, 14:57:42) · Archivos de la corrida: 28 (+ este dictamen = 29) · Diff contra HEAD: +4392 −36, de los cuales −36/+71 son `ESTADO.md` regenerado y 4172 líneas son `data/` ajeno a la corrida.
`date` al abrir: **Sun Oct 11 16:04:41 -03 2026** · `date` al cerrar: **Sun Oct 11 16:24:36 -03 2026**.

Cuatro exigencias, todas documentales: ninguna toca el código, los parches, las bases ni la operación. No hay un solo RECHAZO. El árbol real está donde la corrida dice que está.

## 1. Archivos protegidos — VERDE, medido

`git diff HEAD --stat` por ruta sobre las 23 rutas protegidas: **cero diff en todas**. `git status --porcelain -uall` restringido a esas rutas: **vacío** (ni un archivo sin seguimiento dentro de ellas).

Huellas exigidas, idénticas al carácter:
```
cd0e70c8005143b2f6b63c62fb9e3f75b5303e083a936c98c13b86df6a8b2c25  dinero/sello_dinero.py
b6080eee4351ed433aeb5a124ec4603dcb3db3b3278b1791c40ee8a4ad0abc6c  dinero/reglas.json
```
`.env`: modo **600**, mtime **30-ago-2026 19:23** (no se tocó), ignorado por `.gitignore:2` (`.env*`). `senales.db`, `noticias.db` y `*.db` ignorados (líneas 15, 14, 12). `motor.py`, `senales.py`, `snapshot.py`, `universo.py`, `version.py`, `calendarios.py`, `alertas.py`, los tres jobs, `dinero/`, `api/`, `frontend/`, `tests/`, `backtest/`, `GEMELO/sonda_cierre.py`, `README.md`, `docs/`, `corredor/`, `systemd/`, `launchd/`, `.claude/`: intactos. **R0 en verde por medición, no por declaración.**

## 2. Bases, timers y actos de operación — VERDE, medido

Las tres bases, byte a byte iguales a la apertura de la 16-1:
```
98a048de1dbd6d8c6f53821ad2e879c307cc1d536c64e0dfbb79f90b2f72ced8  senales.db
1829b61b0233b03e493939c5d4b8b56c803a0c6965042d8c9006cc4362336d4c  noticias.db
2a016c523adf6542d5b44dd081c54bfa9bc54456c8c554cd6b69772f6585a636  dinero/sello_dinero.db
```
Medidas al abrir y al cerrar mi revisión: idénticas las dos veces.

- `systemctl --user list-timers --all`: 8 unidades `mki-*`, última ejecución **vie 09-oct** (noticias/snapshot/reporte/backup/vigía/rechequeo) y **sáb 10-oct** (sonda 04:35, sello-dinero 00:30). **Ninguna disparó hoy.** Próximo: lun 12-oct 17:50.
- mtimes de las unidades en `~/.config/systemd/user/`: la más reciente es **29-sep-2026**. Ningún timer tocado.
- `dinero/datos/sello/`: el archivo más nuevo es `ext_2026-10-09.{csv,meta.json}` del **10-oct 00:30:02** (el timer del sábado). **Nada nuevo desde las 15:15.**
- `data/sello_dinero.log` mtime **10-oct 00:30:04**: el sellador real no se ejecutó. **Ningún `--sellar`.**
- Sin commits y sin ningún comando de publicación remota en todo el material nuevo (grep en los tres `.diff`, bitácora, dictamen y líneas agregadas a actas: cero aciertos). **R1, R2 y R8 en verde.**

## 3. Los tres parches — VERDE, verificado en mi propio worktree

Huellas de los `.diff`, idénticas a las que §6.1 manda comparar:
```
48addf80bc5eecced63af4f916be1eea075834051f0ce4bdfb9aa36d0768f4d4  camino_T_16_2.diff
ad864726cf91e2d50f2430cd3f9351d9cff1dfc657a8398304f682c0a0abf45f  b2_contrato_16_2.diff
9b4c45d43c848bff11383bf5955a6cfeb748d700f1b08f73fb696b95283e32b5  b2_api_16_2.diff
```
`git worktree add --detach` propio sobre HEAD: `--check` + `apply` **limpios los tres, en orden** (6 pasos, exit 0). Worktrees removidos al terminar.

**Conducta del camino T, leída y medida:**
- Archivos tocados: `camino_T` → `dinero/sello_dinero.py` + 3 tests; `b2_contrato` → sólo `api/CONTRATO.md`; `b2_api` → `api/main.py`, `dinero/sello_dinero.py`, `tipos.ts`, 1 test nuevo. **Nada fuera de lo declarado. No toca `senales.py` ni `snapshot.py`: el camino de sellado del riel de medición queda fuera.**
- **Ninguna ruta inserta en `sellos_dinero` con `timing_ok` falso.** Sobre el archivo aplicado: `tabla = TABLA_SELLOS` (línea 778) → `if not timing_ok: tabla = TABLA_INTENTOS` (782) → **un solo** `INSERT INTO {tabla}` (843). No hay reasignación posterior ni un segundo INSERT a la principal en código de producción.
- **7 `CREATE` agregados, los 7 con `IF NOT EXISTS`; cero sin la guarda.**
- **UPDATE/DELETE:** sólo tres apariciones, todas legítimas — el `BEFORE UPDATE`/`BEFORE DELETE` de los disparadores de inmutabilidad, y un test que verifica que abortan (`pytest.raises(IntegrityError, match="no se reescriben")` / `"no se borran"`). **Ninguna fila sellada se reescribe ni se borra.**
- `import GEMELO` / `from GEMELO`: **cero**. Mención de `motor`: **cero**.
- `VERSION_SELLO = "E0.3"` en el archivo aplicado.
- **Reproducido por mí en mi worktree:** `test_sello_dinero + test_camino_T_16_2 + test_b2_intentos_visibles_16_2 + test_toely_fuera_insumo_e0` → **66 passed, 11 skipped**, exactamente lo que declara §4.1.
- `tests/test_motor.py`: **exit 0 en el árbol real y exit 0 en el worktree con los tres parches**. El anti-look-ahead sigue verde con T puesto.

## 4. Actas, tarjetas, palabra y cifras — VERDE, medido

- **Aditividad estricta:** `git diff HEAD` de `DECISIONES.md`, `espera_firma.md` y `sello_no_verificable.md` → **cero líneas `-`** en los tres. §101 anexada al final (hunk `@@ -9944,3 +9944,120 @@`, archivo 10063 líneas); §81 al final (`@@ -3088,3 +3088,69 @@`); la nota SUPERADO al inicio del `.md` del parche viejo, sin borrar nada.
- `ESTADO.md`: **49 líneas** ≤ 50.
- **Etiquetas evidenciales en §101:** 101.1 (HECHO, no aplicado), 101.2 (DISEÑO), 101.3 (MEDIDO), 101.4 (MEDIDO), 101.5 (PREDICCIÓN falsable), 101.6 (errores propios), 101.7 (abierto). Regla 12 cumplida; las cifras nuevas van con n y procedencia (p. ej. «n = 0 casos de la segunda forma en 22 fechas selladas»).
- **Palabra prohibida:** 7 apariciones, **las 7 en posición de lista de prohibidas o de negación** — la frase del contrato que la prohíbe, la tupla `PROHIBIDAS` del test, la lista ampliada del auditor que declara su ausencia, y tres salidas de pytest. Una de esas salidas es la de **HEAD puro** (línea 985), lo que prueba que el constructo precede a la corrida. **Cero usos como afirmación.** Ausente en lo agregado a actas y ESTADO.
- **Regla 10, cifras retiradas:** corrí `cifras.reintroducciones()` del propio proyecto sobre los **24 archivos nuevos completos** (los tres `.diff`, bitácora, dictamen del auditor, las 5 salidas de suite, los 4 pytest, los 2 scripts de plegado, las 8 sondas) **y sobre todas las líneas agregadas** a actas/ESTADO: **0 reintroducciones**, sin necesidad de invocar la exención de ±2 líneas en ningún caso. La corrida no introduce ni toca una cifra retirada en ningún `.py`.
- **Secretos:** grep de `sk-ant`, `sk-…`, `bot…:`, `AKIA`, `ghp_`, `xoxb-`, `BEGIN …`, asignaciones de token/clave/chat_id en todo el material nuevo → **cero**. `git status -uall` filtrado por `.db|.env|.log` → **vacío**. **R5 en verde.**

## 5. Aritmética y receta — VERDE, medido por mí

| magnitud | declarado | medido por mí |
|---|---|---|
| recolectados, HEAD puro | 1122 | **1122** (`--collect-only` en el árbol real) |
| recolectados, con los tres parches | 1160 | **1160** (`--collect-only` en mi worktree) |
| delta | +38 | **+38** |
| HEAD puro, sin bases | 1012 passed | **1012** (última línea del archivo) |
| tres parches finales, sin bases | 1044 passed | **1044**; +32 contra HEAD |
| predicción del árbol real aplicado | 1151 + 8 + 1 | **= 1160**, cierra contra lo recolectado |
| suite de cierre del árbol real | 1116 / 5 / 1, exit 0 | **1116 passed, 5 skipped, 1 xfailed, 490.66 s, exit=0**, última línea `16:12:53` — idéntica a la apertura (468.14 s) |

`§6.1` usa **`venv/bin/python`** en las dos invocaciones (pytest y `test_motor.py`) y `node_modules/.bin/tsc` para el frontend: **nunca `python` desnudo**. Verificada la coincidencia de **§7 con §101.5**: sesión 12-oct `pendiente`, `insumo_completo=1`, `cuenta_para_N=1`, 32 filas sin TOELY, `E0.3`, `sellador 299a7627…`, `reglas b6080eee…`, contador 12→13, tabla con 0 filas y 2 disparadores, CSV vacío con cabecera, ningún `.no_verificable.*`, `estado()` con `0`/`null`. **Concuerdan.**

## 6. Horas contra mtimes — VERDE dentro de tolerancia (una excepción, O1)

| declarado | mtime / sello interno | delta |
|---|---|---|
| `camino_T_16_2.diff` 15:49:51 | 15:49:50 | 1 s |
| `b2_api_16_2.diff` 16:00–16:01 | 16:01:00 | ok |
| `sello_no_verificable.md` 15:33 | 15:32:24 | 36 s |
| tarjeta §81 15:54 | 15:54:28 | 28 s |
| `ESTADO.md` 15:58 | 15:58:11 | 11 s |
| acta §101 16:03 | 16:03:16 | 16 s |
| suite HEAD puro fin 15:34:55 | última línea 15:34:55 | 0 s |
| suite parches v1 fin 15:39:22 | última línea 15:39:22 / mtime 15:39:35 | 13 s |
| suite parches finales fin 15:56:38 | última línea 15:56:38 / mtime 15:57:10 | 32 s |
| R1 sin guarda 15:48:16 | 15:48:54 | 38 s |
| sellador worktree final 15:48:15 | 15:48:54 | 39 s |
| suite de cierre 16:04:41→16:12:53 | última línea 16:12:53, mtime 16:12:53 | 0 s |
| bases al cerrar 16:13:02 | bitácora escrita 16:13:17 | 15 s |
| dictamen del auditor, 344 líneas | **344 líneas** | exacto |

**Verifiqué expresamente el orden de escritura de §8**, porque una medición prerredactada es un modo de falla que esta casa ya tuvo: la suite de cierre terminó a las **16:12:53** y la bitácora se escribió a las **16:13:17** — después. Las líneas `__SUITE_CIERRE__` y `__BASES__` son medición, no anticipación. `__GUARDIAN__` y `__WORKTREES__` siguen abiertos por diseño.

## 7. B1 del auditor, sin sobredeclaración — VERDE

La cobertura acotada está escrita en los **tres** sitios que corresponden, y en ninguno se estira:
- **§101.4**, viñeta B1: cubre la forma de timing roto (28-sep, 7-oct) y **«NO cubre la de timing OK en un día sin sesión»**, con el porqué (`estado_dia` mira el día de la emisión en el calendario de NY), la consecuencia (`dia_sin_sesion`, `cuenta_para_N = 0`, ocupa la fecha para siempre, igual que E0.2), la **precisión fechada a §99.2** («cierto para la primera forma y no para la segunda»), `n = 0` casos observados en 22 fechas, y la cota honesta de que la ocupación bajo T es un subconjunto de la de E0.2.
- **bitácora §6.2**, para el acta de aplicación: «el acta no puede decir "T resuelve los disparos de recuperación" a secas».
- **tarjeta §81.2**, con las tres opciones y recomendación etiquetada, sin elegir.

El acta **no sobredeclara**: §101.1 dice «HECHO, no aplicado»; declara que la tabla nueva nace con el primer sello en escritura; nombra la zona ciega de `available_at` (§72, no firmado) y la fuga por el analista «declarada y sin defensa». §101.6 inventaría cuatro errores propios, incluido que el worktree del auditor contenía la pila completa. Eso es lo que esta casa pide.

---

## EXIGENCIAS

**E1 — `bitacora_16_2.md` §2.3: dos de las ocho huellas están viejas, y son las que la receta manda comparar.**
Medido en un worktree fresco mío sobre HEAD `c271822` con los tres `.diff` finales aplicados en orden:
```
299a7627f289e70f8ae3cb83166672c451f0921ca88c21450a87892ae3963d93  dinero/sello_dinero.py     (§2.3 dice 5b1641949eeb6ca8…)
01dcd57b5e4359c53bc82be6bd06cfff18f5c5f9ed7521fa21a8aefd8f79daeb  tests/test_sello_dinero.py (§2.3 dice 4952c655c30c94f8…)
```
Las otras seis coinciden. Además, la prosa de §2.3 («la huella definitiva del sellador … `4b494966…` con sólo el camino T») también es la de la v1: **medí el camino T solo y da `610f5b054aaae1304a58d9979dc6a87e98886a93b84669fb6a276a07efa5c8b7`**, que es exactamente lo que dicen §4.2, §6.2 y §101.2. Y la afirmación de §2.3 de que las ocho se verificaron idénticas en un worktree fresco a las 16:01:05 queda **falsada para esas dos**.
Por qué es exigencia y no observación: **§6.1 instruye a Nicolás a comparar las ocho contra «las ocho huellas de §2.3»**. Una aplicación correcta le va a mostrar dos discrepancias y puede hacerle abortar un estado bueno. Corregir la tabla y la prosa de §2.3 a los valores medidos. **El acta §101.2 ya está bien y es la que manda**; lo que hay que mover es la bitácora.

**E2 — `bitacora_16_2.md` §2.1 declara `camino_T_16_2.diff` de «1661 líneas»; son 1797** (`wc -l`). El acta §101.1 dice 1797, correcto. §2.1 quedó del estado previo a la regeneración de las 15:49:50 (plegado de R1/R2). Corregir §2.1.

**E3 — `bitacora_16_2.md` §9 se titula «lista exacta» y no lo es.** Falta `GEMELO/resultados/dictamen_16_2/evidencia/plegar_R6.py` (existe, mtime 15:59:01, citado en §4.1 como el script de R6), y la entrada `sondas_auditor/ (6 archivos .py)` son **8** (`p1`, `p2`, `p2b`, `p3`, `p9`, `p10`, `q1`, `q2`) — con lo que **§9 se contradice con §8**, que dice «sus ocho sondas». Cuenta real de archivos de esta corrida: **28** (29 con este dictamen); las 21 entradas de §9 cubren 27. Agregar `plegar_R6.py` y corregir 6→8. En la práctica nada se perdería si el directorio se agrega entero, pero §9 es la lista que el acta cita y §101.7 cuenta «21 rutas».

**E4 — tarjeta §81 remite dos veces a la sección equivocada.** §81.1 dice «La receta exacta está en la bitácora 16-2 **§5**» y §81.5 «(va en la receta de la bitácora **§5**)». La receta vive en **§6.1**; §5 es la tabla de suites. (§81.1 «el párrafo de la bitácora §6» sí está bien, y el rango «§5 a §6» de `ESTADO.md` sobrevive.) Corregir las dos citas a §6.1. Es justo el modo de falla que la memoria del proyecto registra: las citas por sección se desplazan cuando se anexa, y hay que reverificarlas después de escribir.

## OBSERVACIONES

**O1 — mtime de `b2_contrato_16_2.diff`: 15:48:54, contra el «15:29 congelada» de §1.** La huella coincide con la receta, así que lo que §1 registra —que el contrato se congeló *antes* de tocar la API, que es la regla de la capa— se sostiene; el archivo en disco se reescribió en la tanda de regeneración de las 15:48, que la bitácora sólo declara para `camino_T` («B2 aplica encima sin cambios»). Una cláusula en §4.1 evita que el mtime se lea mañana como si el contrato se hubiera escrito después de la API.

**O2 — el verde de cierre es un verde sobre documentos.** El árbol real no recibió código, así que 1116/5/1 es legítimamente el mismo de la apertura y basta para esta tanda. La cifra **1151/8/1 es una PREDICCIÓN nunca corrida** y está etiquetada como tal en §5, §6.1 y §101.3. Que quede dicho acá también: la corre la mano que aplique, y si da otra cosa manda la máquina.

**O3 — la zona ciega que ahora carga peso.** `available_at` es computado por calendario y no observado, y **desde E0.3 decide tabla, nombre de archivo y ocupación de la fecha**: dejó de ser un asunto de métricas y pasó a ser parte del sellado. El acta lo declara en §101.4 y la tarjeta en §81(ii). No hay nada que corregir; lo anoto porque es lo que yo miraría primero si el martes algo sale raro.

**O4 — hallazgo, no cambio (R7).** El badge `tests_recolectados` sigue desfasado (`ESTADO.md`, Deuda) y ahora quedará 1122 vs 1160 cuando se apliquen los parches. Está asignado a la 16-3 (§93.14). Correctamente **no** se arregló de paso.

**O5 — alcance limpio.** El árbol real contiene exactamente lo que el encargo autorizaba y nada más: 8 rutas de la corrida + el directorio `dictamen_16_2/` + las 4 de `data/` que son del backup y están declaradas como ajenas en §9. Ni un arreglo oportunista. Los cuatro worktrees de la corrida (`wt162`, `wt162_check`, `wt162_e1`, `wt162_head`) siguen registrados sobre `c271822`, a la espera de `__WORKTREES__`; los dos míos ya los removí.

## NO VERIFICADO

- **El contenido de `.env`**: el sistema de permisos denegó `stat` y lectura directa. Verifiqué lo que sí se puede: modo 600, mtime 30-ago-2026, ignorado por `.gitignore`, cero diff. No puedo afirmar nada sobre las variables de adentro, y tampoco debo.
- **La predicción del martes 13-oct** (§7 / §101.5) es falsable por construcción pero **no medida**: se verifica el martes con la consulta de §7 en `mode=ro`.
- **La forma (ii) del disparo de recuperación** (timing OK en día sin sesión) no la reproduje yo; la midió el auditor en tres escenarios. La acepto como suya y queda declarada, no asumida.

---

**Veredicto.** Nada de lo que la constitución protege se movió: `motor.py` y la lógica de señales intactos, ninguna fila sellada tocada, ninguna base escrita, ningún timer, ningún `--sellar`, ninguna publicación remota, ningún secreto, rama `main`, actas aditivas con etiquetas, cero cifras retiradas, suites verdes y reproducidas por mí. Los tres parches aplican limpio en mi propio worktree y se comportan como dicen comportarse. Lo que falta son cuatro correcciones de documento, **y la E1 importa de verdad**: es la tabla que Nicolás va a usar como criterio al aplicar, y dos de sus ocho huellas le dirían que algo salió mal cuando todo salió bien. Con E1 a E4 corregidas antes del commit —la frontera de la errata es el commit—, esto se firma como APROBADO.

Cerrado: **Sun Oct 11 16:24:36 -03 2026**.
