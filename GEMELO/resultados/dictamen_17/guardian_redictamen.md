# Re-dictamen de cierre de la corrida 17: guardian-constitucion

> **Nota de transcripción (orquestador de la corrida 18a, 25-nov-2026).** El `guardian-constitucion` no tiene
> herramienta de escritura: devolvió este dictamen como texto y el orquestador lo transcribe tal cual, sin editar
> su contenido. Lo único que no es del guardián en este archivo es esta nota y la sección final «Cierre», que
> escribe el orquestador y lo dice. El mandato que recibió es el textual del encargo 18a §2, más los límites duros
> del encargo §1 y la instrucción de forma de entrega. Sesión del orquestador: Fable 5.2, esfuerzo alto (leído de
> la salida de `/model` al abrir); el agente corre con el modelo de su definición
> (`.claude/agents/guardian-constitucion.md`, `model: opus`).

Encargo 18a. Árbol real `/home/nicolasaraneda/dev/mki-terminal`, rama `main`, HEAD `3631948`.

- **Inicio** (primer comando, `TZ=America/Santiago date`): `Wed Nov 25 16:20:44 -03 2026`
- **Cierre** (último comando): `Wed Nov 25 16:29:07 -03 2026`

```
DICTAMEN: OBSERVADO
Rama: main   Archivos: 16 de la tanda (8 modificados + 8 sin seguimiento; data/ fuera de la tanda)
Líneas: +6569 -490   (+2674 -490 seguidos según git diff HEAD --shortstat sin data/; +3895 en los 8 sin seguimiento)
```

Hay una sola razón para no aprobar: **O-1 quedó corregida en el código y no en el documento que se firma.** Ninguna regla dura está rota, así que no hay RECHAZO. La frontera de la errata es el commit: esto se corrige en su sitio antes de commitear y se re-verifica.

---

## 1. Las siete observaciones

### O-1: no está corregida del todo. El código está bien; el documento `DISEÑO.md` sigue mezclando dos generaciones.

**El código está corregido. Lo verifiqué así:**

- `GEMELO/SECUENCIAL/diseno_secuencial.py:141-180`: el factor vive en un solo lugar, `factor_secuencial()` con `@functools.lru_cache(maxsize=1)`, más `n_max_del_plan()`.
- `mirada.py:222` delega en `round(D.n_max_del_plan(mde, p_d=p_d))`.
- `tabla_firma.py:111` delega en `D.n_max_del_plan(...)`.
- Ejecuté `scratchpad/nmax_b.py` con `sqlite3.connect` reemplazado por una función que lanza error. Ninguna base se abrió.

| MDE (valor exacto de `tabla_firma_17.json`) | `mirada._n_max` | `mirada._n_max` (p_d por defecto) | `tabla_firma.n_max` | `mirada.plan` mirada 1 | sellado (N_max, mirada 1) |
|---|---|---|---|---|---|
| 4.942768 pp | 5836 | 5836 | 5836 | 1459 | (5836, 1459) |
| 8.512120 pp | 1962 | 1962 | 1962 | 490 | (1962, 490) |
| 10.000000 pp | 1419 | 1419 | 1419 | 355 | (1419, 355) |
| 13.089490 pp | 825 | 825 | 825 | 206 | (825, 206) |

- El p_d de los dos lados es el mismo número: `D.P_D_OBSERVADA` = p_d sellado = 0.49236641221374045 (= 129/262, `True`).
- Factor: 1.0263801871775526.
- Ojo con los valores redondeados a dos decimales (4,94 / 8,51 / 13,09): dan 5843 / 1963 / 825. Los dos lados coinciden igual, pero 1963 **no** es la cifra sellada; las cifras vigentes salen del MDE sin redondear.

**Mutación, en el worktree descartable** (`scratchpad/wt_guardian`, detach en HEAD, con los `.py` de la tanda y los dos archivos de test copiados y comparados con `cmp`):

- Línea base: `test_el_factor_secuencial_compra_de_verdad_la_potencia_080`, `1 passed`.
- Mutación A, en `mirada.py:222`: `_n_max` vuelve a hacer su propia cuenta, Connor × DEFF × `D.FACTOR_SECUENCIAL_CABLEADO_HASTA_LA_CORRIDA_17` (el factor retirado). Resultado: `1 failed`, `AssertionError: mirada.py y tabla_firma.py dan N_max distintos a 0.05: el factor volvió a vivir en dos lugares — assert 5690 == 5703` (`tests/test_secuencial_17.py:457`).
- Mutación B, en `tabla_firma.py:111`: `"n_max": n_iid * deff * FACTOR_SECUENCIAL_CABLEADO_HASTA_LA_CORRIDA_17`. Resultado: `1 failed`, mismo mensaje, `assert 5703 == 5690`.
- Después de cada mutación restauré el archivo y lo confirmé con `cmp`.
- El test recorre 5 / 7 / 10 / 15 pp, no los cuatro MDE del encargo. Esos cuatro los verifiqué por ejecución en la tabla de arriba.

**(c): el `1.0241` literal ya no se usa como factor en ningún consumidor de `N_max`.**

- Sobrevive como constante histórica con nombre: `diseno_secuencial.py:167` y `tabla_firma.py:69`.
- Aparece en comentarios o docstrings que lo nombran como retirado: `mirada.py:214`, `diseno_secuencial.py:126`, `tabla_firma.py:62`.
- **Excepción, `mirada.py:183`**: el comentario todavía dice «N_max por MDE, de `diseno_secuencial` (Connor × DEFF × 1.0241)», sin marca. El código de la línea 222 lo contradice. Es preexistente (línea 73 en HEAD), pero está en un archivo que el diff reescribió y describe la fórmula con el factor retirado.

**El documento no está corregido. `GEMELO/SECUENCIAL/DISEÑO.md` mantiene dos generaciones vivas, que es exactamente el defecto de O-1:**

1. **`DISEÑO.md:1517-1522`, tabla nueva (no existe en HEAD: `git show HEAD:… | grep -c "354 → 2026-11-04"` da 0).**
   - Las miradas 1 a 3 llevan los n de la generación vieja: a 10 pp **354 / 708 / 1.062** (0,25/0,50/0,75 × 1.416); a 8,51 pp **979 / 1.468**, con fecha 2027-05-28.
   - La fila 4 lleva el `N_max` nuevo (1.962 / 1.419).
   - Lo sellado en `tabla_firma_17.json` es **355 / 710 / 1.064** y **981 / 1.472 → 2027-05-31**.
   - El «354 a 10 pp» es literalmente la cifra que O-1 cazó, y quedó reintroducida en el documento.
2. **`DISEÑO.md:1372` y `1375`, preexistentes sin marca.**
   - Dicen «con el factor **1.0241** (drift requerido 2.8352…)» y llevan el encabezado `N_max (×1.0241)` sobre una columna que el diff rehízo con el factor computado: 1.912 × 1,02638 = 1.962; con 1,0241 daría 1.958.
   - Debajo, «la potencia del plan es 0.80 exacta», que con ese factor es falso (0,7991, `diseno_secuencial.py:129`).
   - La fila F6 del registro de cambios (`DISEÑO.md:2126`) sí documenta la corrección, pero el cuerpo de §A3.3 no la lleva.

Por eso la afirmación de la bitácora §10.5 («Todos los documentos quedaron en una sola generación») y la de DECISIONES §108.13-bis («Las cifras vigentes quedaron en una sola generación») **no son ciertas para `DISEÑO.md`**.

**Qué falta antes de aprobar:** rehacer `DISEÑO.md:1519-1521` desde `tabla_firma_17.json` y corregir en su sitio `DISEÑO.md:1372-1375` (factor, drift y encabezado). Es corrección antes del commit, no errata.

### O-2: corregida. Verificado así

El IC95 [8.93, 12.81] del MDE crítico está en las cuatro copias que nombra la errata del curador:

| Copia | Dónde |
|---|---|
| El documento | `DISEÑO.md:131`, `:285`, `:1010`, `:1025` |
| La tarjeta §90 | `espera_firma.md:3391`, `:3403` |
| La bitácora | `bitacora_17.md:196`, `:597` |
| El ejecutable | `tabla_firma.py:298` (`mde_critico_ic_pp`) y `:370-371` (lo imprime) |

- Además está en DECISIONES §108.6 (`:10371`).
- La fila B11 de `dictamen_17/curador_epistemico.md:32` lleva su «ERRATA de esta tabla, 25-oct más tarde» a la vista.
- `tabla_firma_17.json`: `mde_critico_ic_pp` = [8.9275…, 12.8071…].
- Las filas de tabla `bitacora_17.md:192` y `espera_firma.md:3383` dicen «(punto)» y llevan el IC en la prosa inmediata.

### O-3: corregida. Verificado así

- Fila nueva en `GEMELO/cifras_retiradas.md:73`, patrón `2029-08-10` (fecha artefacto RETIRADA el 25-oct). `cifras.cifras_retiradas()` la carga: mi barrido la cazó como patrón (36 patrones).
- La tarjeta §90 (`espera_firma.md:3386-3389`) la marca «está RETIRADO» y declara que argumentaba desde ella.
- No queda ninguna aparición sin marca en un `.md` o `.py` de la tanda. Las que hay están en `dictamen_17/estadistico_adversario.md:585,855` y `re_dictamen.md:227`, y son el expediente que la retira.
- No aparece en ningún `.py`.

**Hallazgo lateral, no es O-3:** las cifras de reemplazo del intervalo honesto discrepan en un día entre documentos.

- `cifras_retiradas.md:73` y `DISEÑO.md:1018,1066,1838-1839` dicen 2027-03-08 → 2028-10-04.
- `bitacora_17.md:180-181` y `espera_firma.md:3370,3389` dicen 2027-03-09 → 2028-10-05.
- `DISEÑO.md:1860` da mediana **2027-08-19**; el resto y el JSON sellado (`fecha_de_la_mediana`) dan 2027-08-20.
- Para corregir en su sitio junto con O-1. No recomputé cuál de las dos es la buena (ver NO VERIFICADO).

### O-4: corregida. Verificado así

- `DECISIONES.md:10361` (dentro de §108.2-ter): «**PENDIENTE, y la redacción anterior de esta línea lo daba por hecho (exigencia O-4…)**», con la razón (`veredicto_51.py` alimenta el README y tiene tests propios) y el orden invertido («primero se aplica, después se declara aplicado»).
- §108.16 (`:10399`) lo repite.
- La máquina confirma que no se aplicó: `backtest/veredicto_51.py:100` sigue en `N_INTENTOS_PREVIO = 354`, y `git status` no muestra cambios en `backtest/` ni en `GEMELO/relevo_asiatico.py`.

### O-5: corregida. Verificado así

- `DECISIONES.md:10351` (§108.2) declara el enlace simbólico a `senales.db` en el worktree, su uso solo-lectura y su retiro con `unlink` antes de cualquier `pytest`.
- `find . -type l` (sin `venv`/`node_modules`) en el árbol real sale vacío.

### O-6: corregida. Verificado así

- §108.13 (`DECISIONES.md:10385`) dice «las **ocho** tarjetas (§90 a §97)».
- §108.15 (`:10397`) dice «**OCHO** tarjetas nuevas».
- `grep "seis tarjetas"` solo aparece en `bitacora_17.md:570`, la fila que describe O-6.

### O-7: corregida. Verificado así

`mirada.py:146-151` dice: «bajo la regla de filas FIRMADA, son 5 grupos de dos (10 filas); los 15 de dos (30 filas) son la rama SIN esa regla, o sea la que D1 derogó, y citarla acá sin decirlo —como hacía este comentario— …». La rama derogada está nombrada como tal.

---

## 2. El defecto que podría haber traído O-1 (`lru_cache`): no lo hay

Lo comprobé así:

- **Nada se esconde en la clave del caché.** `factor_secuencial()` no recibe argumentos (`diseno_secuencial.py:142`). Lo que varía por llamada (`p_d` y `deff`) se multiplica **fuera** del caché, en `n_max_del_plan` (`:180`). Por eso `propagacion_conjunta` puede variar `p_d` réplica a réplica sin que el caché le devuelva un valor ajeno.
- **Lo confirmé ejecutando:** `cache_info()` da `hits=17, misses=1`, y los cuatro `N_max` sellados se reproducen exactos con el caché caliente.
- **Nadie llama esperando otro factor.** Hay un solo llamador, `n_max_del_plan`. `tabla_firma.py:76-77` lo lee una vez al importarse. Ningún test ni módulo reasigna ni parchea `D.FRACCIONES` o `D.UMBRALES_OBF`; el grep de `monkeypatch`/`setattr` sobre esos nombres sale vacío. La contraprueba del test usa la constante retirada directamente, no el caché.
- **Hay una sola copia del módulo.** `TF.D is sys.modules["diseno_secuencial"]` da `True`, así que existe un solo caché. Aunque hubiera dos, la función es pura y devolvería el mismo float, que además es inmutable.

**Riesgo latente, preexistente y no causado por el caché, que anoto como pendiente:** `mirada.py:194,196` vuelve a declarar `UMBRALES_OBF` y `FRACCIONES`, y `diseno_secuencial.py:182,341` tiene las suyas. El factor se computa con las de `D` y la mirada decide con las suyas. Hoy los valores son idénticos, pero ningún test fija `M.UMBRALES_OBF == D.UMBRALES_OBF` (los tests de `:392` y `test_secuencial.py:321` comparan contra `M`, o sea contra sí mismos). Es la misma clase de defecto que O-1, sobre los insumos del factor. No se arregla de paso (R7).

---

## 3. Reglas duras re-verificadas

**R0 y R13, intocables.** Comparé sha256 del árbol de trabajo contra `git show origin/main:<f>` (origin/main = `627cc1b`). Los catorce archivos salen IGUAL:

- `motor.py`, `senales.py`, `snapshot.py`, `universo.py`, `version.py`, `calendarios.py`, `noticias.py`
- `alertas.py`, `app.py`, `mki_backup.py`, `mki_vigia.py`, `backtest/linea_base.py`
- Más dos que agregué: `backtest/veredicto_51.py` y `modo.py`

`git diff --stat origin/main -- api/ dinero/ corredor/ systemd/ launchd/ .claude/ scripts/ mki` sale vacío. `git diff --name-only origin/main HEAD` solo trae `data/backups/`. No hay `.diff` contra archivos protegidos en la tanda.

**R1, sin escrituras a base.** Barrí el diff completo (`git diff HEAD` sin `data/`, más los 8 archivos sin seguimiento prefijados como añadidos) buscando `UPDATE`, `DELETE FROM`, `DROP`, `ALTER TABLE`, `INSERT`, `.to_sql(`, `if_exists`, `executescript`, `.commit()`, `os.remove`, `unlink(`, `mode=rw`/`rwc` y `sqlite3.connect`: **cero coincidencias en líneas añadidas**.

- La única escritura a archivo nueva es `tabla_firma.py:4308-4309`, el JSON de `--sellar`, que no es una base.
- `ventana_antecedente.py` lee solo por `lb._conexion_ro` / `lb.cargar` (`backtest/linea_base.py:141`, `mode=ro`).
- Huellas de las tres bases antes y después de la suite del orquestador (`suite_18a.log`), idénticas: `efa48f01…` senales.db, `97ee6454…` noticias.db, `07aed706…` sello_dinero.db. Al cerrar volví a leerlas y siguen igual.

**Candados abortando, verificados por ejecución sin riesgo de cómputo sobre la población:**

- Corrí `mirada.ejecutar(1)` en el worktree, que no tenía ninguna base, con `sqlite3.connect` y `cargar_ventana_nueva` reemplazados por funciones que lanzan error.
- Sin MDE: `SystemExit: MDE SIN FIRMAR, y hoy NO hay número propuesto.`
- Con `MDE_FIRMADO = 0.0851` puesto solo en memoria: `SystemExit: REGLA DE DEDUPLICACIÓN DEL ESTIMADOR SIN FIRMAR.`
- Ninguno de los dos llegó al cargador. `_guard_versiones` es puro (`mirada.py:491-514`).
- Tests de los candados en el worktree: `3 passed` (`test_el_mde_sin_firmar_bloquea_la_mirada`, `test_la_regla_del_estimador_sin_firmar_bloquea_la_mirada`, `test_la_regla_prohibida_no_se_puede_elegir`).
- En el árbol real, `mirada.MDE_FIRMADO = None` (`:86`) y `REGLA_DEDUP_ESTIMADOR = None` (`:136`). La firma de §90 (§109.4 (3)) **todavía no está en el código**, lo cual es correcto: el código no se cambia en esta tanda.
- Los tests que desbloquean candados parchean `cargar_ventana_nueva` con datos sintéticos, y un fixture autouse (`tests/test_secuencial.py:41-55`) desvía `DIR_ACTAS` y `RUTA_REGISTRO`.
- `GEMELO/SECUENCIAL/miradas/` **no existe** ni al empezar (16:20:44) ni al terminar (16:29:07).

**R2.** Sin `git push` en ninguna línea añadida; el barrido de R1 incluyó el patrón. No hice ni push, ni pull, ni commit, ni add, ni stash.

**R3.** `git branch --show-current` da `main`. La tanda no cambia el comportamiento de emisión: no toca la ruta de sellado ni `dinero/`.

**R5.** `.env` tiene permisos `600` y está en `.gitignore:2`. `senales.db`, `noticias.db` y `*.db` están ignorados. Ninguna base ni log en la tanda. El barrido de patrones de token y clave en las líneas añadidas sale vacío.

**R6, verdes.** Uso la salida del orquestador, `suite_18a.log`: `1252 passed, 5 skipped, 1 xfailed, 29 warnings in 492.21s` (`FIN_PYTEST 2026-11-25 16:28:54 -03`), igual a la referencia de §108.13. `tests/test_motor.py`: «RESULTADO: todas las funciones del motor pasan el test de no-contaminación». `FIN 2026-11-25 16:29:03 -03`.

**R7.** El parche a `tests/test_secuencial.py` hace lo que §108.13 declara: el candado nuevo (`monkeypatch` de `REGLA_DEDUP_ESTIMADOR`), el `p_d` corregido (403 → 384) y los `N_max` 2905 / 1419, más `faltan` = 355 − 70. Sigue fuera de la tanda, y está bien: `horizonte.py:65` (`FACTOR_OBF = 1.0241`, factor retirado) y `horizonte.md`, declarados abiertos en §108.16.

**R8.** No se toca `.env`, ni los timers, ni el modo. La única mención de `systemctl` en las líneas añadidas es la bitácora citando una lectura (`list-timers`).

**R10, cifras retiradas.** Pasé `cifras.reintroducciones()` por los 16 archivos de la tanda y separé lo añadido de lo preexistente con los hunks del diff. Lo añadido:

- `2029-08-10` en `dictamen_17/estadistico_adversario.md:585,855` y `re_dictamen.md:227`: es el expediente que retira la cifra, no una reintroducción.
- `DECISIONES.md:10429` (§109.4 (7), del 25-nov, **no es de la corrida 17**): el patrón `MDE…7 pp` choca con una decisión firmada (7 pp como elección de calendario), no con el MDE retirado de la escala del retorno. Es un falso positivo del patrón; lo inventarío para Nicolás.
- Ninguna cifra retirada en un `.py` introducido o tocado.
- Lo preexistente en DECISIONES.md (≈50 coincidencias de actas viejas) queda inventariado y no rechaza.

**R4 y R11.** El ejecutable se corrigió primero; lo que falta es el documento (O-1). El diff no trae ninguna asimetría Mac/PC nueva.

**R14.** El factor pasó de supuesto cableado a cómputo, y es lo que verifiqué. Sigue habiendo una constante derivada del factor retirado sin recomputar, aunque es preexistente:

- `mirada.py:195`, `Z_FUTILIDAD = (-1.662, 0.016, 1.033)`, salió del drift viejo 2,8352.
- Con el drift computado (2,8383), `z_futilidad` da (−1,667, 0,014, 1,032). Lo calculé con funciones puras, sin base.
- La futilidad no es vinculante y no consume α, pero `mirada.py` la imprime y aplica.
- `tests/test_secuencial.py:140` también usa 2,8352.
- Queda como pendiente para tarjeta, no como corrección de paso.

---

## 4. Observaciones (lo que falta antes de aprobar)

- **O-1 (R4/R9) `GEMELO/SECUENCIAL/DISEÑO.md:1519-1521`.** Las miradas 1 a 3 en la generación vieja (354 / 708 / 1.062 a 10 pp; 979 / 1.468 y 2027-05-28 a 8,51 pp) en la misma tabla que la fila 4 nueva. Rehacer desde `tabla_firma_17.json` (355 / 710 / 1.064; 981 / 1.472 → 2027-05-31).
- **O-1 `DISEÑO.md:1372-1375`.** El factor retirado 1.0241, el drift 2.8352 y el encabezado `(×1.0241)` sobre una columna computada con 1.026380, más «potencia 0.80 exacta». Corregir en su sitio.
- **O-1 `mirada.py:183`.** El comentario describe `N_max` como «Connor × DEFF × 1.0241» (factor retirado). Corregirlo o marcarlo como retirado.
- **Lateral (mismo barrido) `DISEÑO.md:1860` contra `:1838`, y `bitacora_17.md:180-181` / `espera_firma.md:3370,3389` contra `cifras_retiradas.md:73`.** La mediana es 2027-08-19 o 2027-08-20, y los bordes 2027-03-08/09 y 2028-10-04/05. Una sola generación de fechas, confirmada contra la máquina.
- Después de estas correcciones, `bitacora_17.md` §10.5 y DECISIONES §108.13-bis pueden volver a decir «una sola generación». Hoy no es cierto.

## 5. Pendientes inventariados (no son de esta tanda, R7)

- `mirada.Z_FUTILIDAD` derivada del drift viejo (`mirada.py:195`, `tests/test_secuencial.py:140`).
- Duplicación de `UMBRALES_OBF` y `FRACCIONES` entre `mirada.py:194,196` y `diseno_secuencial.py:182,341`, sin un test que las ate.
- `horizonte.py:65` y `horizonte.md:71` con el factor retirado (ya abierto en §108.16).
- Choque del patrón `MDE…7 pp` de `cifras_retiradas.md:41` con la firma §109.4 (7).

## 6. NO VERIFICADO

- **El conteo «5 grupos de dos (10 filas)» de O-7.** Verifiqué que la rama derogada está nombrada, no el número: contarlo exige leer la ventana antecedente en `senales.db` y la consigna era no abrir bases.
- **Cuál de las dos generaciones de fechas del intervalo honesto es la correcta** (…-08 / …-04 contra …-09 / …-05; mediana 08-19 contra 08-20). Hay que correr `tabla_firma` o `propagacion_conjunta` contra la base y no lo hice. El JSON sellado solo trae `fecha_de_la_mediana` = 2027-08-20, no los bordes.
- **Los «once lugares» de O-1 uno por uno.** El dictamen original no está en un archivo propio y no tengo la lista. Barrí por valores de la generación vieja (1.416, 1.958, 354, 979, 1.468, 708, 1.062, 2.8352, 0.7991) en los documentos y módulos de la tanda; lo que apareció está arriba.
- **La amputación de `cargar_poblacion()` columna por columna.** No la repetí, porque no estaba en el mandato del re-dictamen. Se apoya en el test `test_la_poblacion_sale_sin_columnas_de_resultado`, en verde en la suite.
- Siguen sin verificar, como en el dictamen original: el 12 % de inflación de `V̂`, E6, E7 y la tabla de exposición residual.
- No corrí la suite completa yo mismo; uso `suite_18a.log`.

## 7. Verificado en verde

- (a) Los cuatro `N_max` iguales en los dos consumidores, por ejecución.
- (b) El test de igualdad existe y falla ante las dos mutaciones.
- (c) en código.
- (d) Las cuatro copias del IC del crítico.
- (e) La fila de `cifras_retiradas.md`.
- (f) «ocho» en §108.13 y §108.15.
- (g) Rama derogada nombrada en `mirada.py`.
- O-2 a O-7.
- Los catorce intocables, byte a byte, contra `origin/main`.
- Cero escrituras a base en el diff.
- Los dos candados abortan por ejecución.
- Suite 1252/5/1/0 y anti-look-ahead del motor en verde.
- Huellas de las tres bases idénticas.
- `miradas/` ausente.
- Sin push, `main`, sin secretos, timers y `.env` intactos.

**Limpieza del worktree.** `git worktree remove --force …/scratchpad/wt_guardian` y `git worktree prune`. `git worktree list` muestra solo el árbol real `3631948 [main]`. `git status --short` da las mismas 18 rutas que al empezar, y no escribí nada en el árbol real.

Archivos de trabajo, fuera del árbol, ninguno es parte del dictamen:
- `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/38542fe4-0738-49e3-a1f2-236ef1da7e8a/scratchpad/nmax_a.py`
- `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/38542fe4-0738-49e3-a1f2-236ef1da7e8a/scratchpad/nmax_b.py`
- `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/38542fe4-0738-49e3-a1f2-236ef1da7e8a/scratchpad/candados.py`
- `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/38542fe4-0738-49e3-a1f2-236ef1da7e8a/scratchpad/r10.py`
- `/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/38542fe4-0738-49e3-a1f2-236ef1da7e8a/scratchpad/diff_tanda.txt`

---

## Cierre (escrito por el orquestador de la corrida 18a, no por el guardián)

**Veredicto del re-dictamen: OBSERVADO.** Seis observaciones corregidas (O-2 a O-7) y una no del todo: O-1 está
corregida en el código (factor en un solo lugar, los dos consumidores delegan, el test falla ante las dos
mutaciones) y **no** en `GEMELO/SECUENCIAL/DISEÑO.md`, que conserva dos generaciones de cifras en la tabla de
§A3.3 y el factor viejo en su prosa, más un comentario en `mirada.py:183`. Ninguna regla dura rota.

**Consecuencia, por la letra del encargo 18a §1:** una observación no quedó corregida, así que **no se corrige en
esta corrida, se reporta y se para**. La corrida 17 **no se puede commitear todavía**: la condición de §108.13-bis
y §109.4 (2) es el re-dictamen sin observaciones abiertas, y hay una. La corrección es otra corrida, con su propio
re-dictamen después.

**Lectura de contraste del orquestador (sólo lectura, no es un segundo dictamen).** Leídas `DISEÑO.md:1368-1378` y
`:1512-1524`, `mirada.py:181-184` y `:220-223`, y `tabla_firma_17.json`: lo que el guardián cita está en esas
líneas tal como lo cita, y las miradas 1 a 3 del JSON sellado (punto y elección de calendario) son las que él da
como vigentes. La discrepancia de un día entre fechas del intervalo honesto también aparece por `grep` en las
líneas que nombra. Las horas del guardián son compatibles con los mtimes de sus archivos de trabajo (16:21:35 a
16:25:33) y con la duración del agente.

**Suite del árbol real, dos corridas, las dos antes de la ventana de las 17:50:**

| Corrida | Inicio | Fin de pytest | Resultado | `tests/test_motor.py` |
|---|---|---|---|---|
| 1, en paralelo con el guardián, sin este archivo en el árbol | 16:20:41 | 16:28:54 (492,21 s) | **1252 passed, 5 skipped, 1 xfailed, 0 failed** | verde (línea RESULTADO; fin 16:29:03) |
| 2, con este archivo ya en el árbol (sin la sección Cierre) | 16:33:10 | 16:40:48 (457,64 s) | **1252 passed, 5 skipped, 1 xfailed, 0 failed** | verde, código de salida 0 (fin 16:40:56) |

Igual a la referencia de §108.13; ningún saltado de más ni de menos, así que no hay nada que clasificar con §91.
Las huellas sha256 de `senales.db`, `noticias.db` y `dinero/sello_dinero.db` son idénticas antes y después de cada
corrida y entre las dos (`efa48f01…`, `97ee6454…`, `07aed706…`). Declarado: en la corrida 1 el código de salida
que quedó en el registro era el de `tail` y no el de Python; por eso la corrida 2 lo captura directo. Y declarado:
el encargo ordena la suite después del re-dictamen; la corrida 1 se lanzó en paralelo para que el guardián tuviera
los verdes a la vista (su regla R6), lo que no cambia ningún resultado.

**Horas (todas de `date`, hora de Chile, 25-nov-2026).** Arranque de la sesión 16:19:20. Guardián: 16:20:44 a
16:29:07 por sus propias lecturas; su informe ya estaba entregado a las 16:31:06. Transcripción de este archivo:
entre las 16:31:06 y las 16:33:10. Este cierre se escribe después de las 16:41:01.

**Arranque (encargo §0), tal cual.** HEAD `3631948`; modificados o sin seguimiento sólo las 16 rutas de la
bitácora 17 §12 más cuatro bajo `data/`; la última acta es §109; los ocho timers `mki-*` instalados y ninguno
disparó durante la corrida (el próximo, noticias 17:50). **`GEMELO/SECUENCIAL/miradas/` no existe** (`ls`: No such
file or directory), ni al arrancar (16:19) ni después del guardián (16:31); no hay `registro.log` que contar.

**La lista del commit (`~/mki/git/archivos_17.txt`, 17 rutas) es exacta contra `git status --short`:** las 17
existen y son exactamente las 17 rutas modificadas o sin seguimiento fuera de `data/`; no sobra ni falta ninguna.
Fuera de la lista quedan sólo `data/backups/sello_dinero.csv`, `data/sonda_cierre.csv` y
`data/backups/sello_dinero_ext/ext_2026-11-24.{csv,meta.json}`. La lista es exacta, pero no se usa hoy.

**Lo que esta corrida NO hizo, y por qué.**
- **La errata de la bitácora 17 §12 (encargo §3.2) no se escribió.** La orden de parar llegó antes; queda
  pendiente para la corrida que corrija O-1, que de todos modos tiene que tocar esa bitácora. Este archivo es el
  único que la corrida 18a escribió en el árbol.
- No se corrigió nada, no se commiteó, no se pusheó, no se firmó, no se escribió acta (§109.5), no se tocó
  systemd ni ninguna base, y no se ejecutó ninguna mirada.
- **Para que Nicolás lo sepa sin leerlo entre líneas:** el guardián verificó los candados ejecutando
  `mirada.ejecutar(1)` dentro de su worktree descartable, que no tenía ninguna base, y con el cargador y
  `sqlite3.connect` reemplazados por funciones que lanzan error; los dos candados abortaron antes de llegar al
  cargador. No fue contra la base real y no computó nada, pero es una ejecución de esa función y se declara.
- No quedó ningún worktree (`git worktree list`: sólo el árbol real) ni ningún enlace simbólico.

**Diferencias entre el encargo y la máquina, anotadas.** (1) El mandato pide los cuatro `N_max` para los MDE
redondeados a dos decimales; el guardián muestra que las cifras selladas salen del MDE sin redondear y que con el
redondeo uno de los cuatro difiere en una fila de la cifra sellada, igual en los dos consumidores. (2) El mandato
habla de trece intocables; el guardián comparó catorce archivos. (3) El plan de §109.5 fechaba esta corrida el
jueves 26; se ejecutó el miércoles 25, que el encargo también admitía.

---

> **Nota de transcripción (orquestador de la corrida 18a-bis, 25-nov-2026).** Lo que sigue es la segunda
> verificación del `guardian-constitucion`, pedida por el encargo 18a-bis §3.2 y transcrita tal cual, sin editar.
> La hizo el mismo agente de la primera pasada, retomado con su contexto. Corrigió el orquestador (16:55 a 16:58)
> y verificó el guardián: dos actos y dos agentes. Dos datos del orquestador para leerla: (1) los tests del
> registro `tests_18a_bis.log` son nueve archivos, censados con `grep`: `test_secuencial.py`,
> `test_secuencial_17.py`, `test_secuencial_07.py`, `test_epistemico.py`, `test_cifras_arbitro.py`,
> `test_sonda_cierre.py`, `test_backup_orden.py`, `test_ventana_larga.py` y `test_backtest.py`; (2) la frase de la
> bitácora 17 §12 que la errata corrige está en `bitacora_17.md`, líneas 622 a 624 (la que atribuye lo de `data/`
> al backup diario y a la sonda), que el guardián deja como no confirmada en su punto 6.

## Segunda verificación (25-nov, corrida 18a-bis)

- Inicio (`TZ=America/Santiago date`, primer comando): `Wed Nov 25 16:58:13 -03 2026`
- Cierre (último comando): `Wed Nov 25 17:02:52 -03 2026`

**DICTAMEN: APROBADO.** O-1 queda corregida también en el documento. Las tablas de `DISEÑO.md` coinciden con `tabla_firma_17.json` celda por celda, cada cambio tiene su fila en el registro, el diff no sale del alcance de §1 y las reglas duras siguen en verde. Lo único que no cumple el criterio al pie de la letra es `horizonte.py:65`, y no bloquea (motivo en §2). Rama `main`, HEAD `3631948`.

### 1. Diff de esta corrida, contra las copias de las 16:55

Las comparé yo con `diff` y `cmp` contra `scratchpad/antes_18a_bis/`:

- **`DISEÑO.md` cambia en cuatro lugares:**
  - La prosa de §A3.3 (ex 1372-1373, hoy 1372-1377) ya no nombra un valor: remite a `factor_secuencial()` y al artefacto sellado.
  - El encabezado de la tabla (ex 1375, hoy 1379) pasa a `× factor secuencial computado`.
  - En la tabla de §A3.5 (ex 1519-1521, hoy 1523-1525) cambian las tres filas de miradas 1 a 3.
  - Se agrega la subsección de registro con las filas G1 y G2 (hoy 2073-2087).
- **`mirada.py`:** cambia solo el comentario de la línea 183, que ahora ocupa 183-184. El código no se toca.
- **`bitacora_17.md`:** una línea de errata al final de §12 (650), la que pide el acta §109.4 (2).
- **Sin cambios** (`cmp` idéntico): `espera_firma.md` y `guardian_redictamen.md`.
- **Nada más cambió en el árbol:**
  - `git status --short` da las mismas 18 rutas que en la primera pasada. `guardian_redictamen.md` está dentro de `dictamen_17/`, que ya figuraba como ruta sin seguimiento.
  - `find -newermt '2026-11-25 16:54'` devuelve los tres archivos de arriba y seis `micro/rtl/sim/tb_huecogate_*.vvp`. Esos seis son de las 16:59:02, ignorados por `micro/rtl/.gitignore:5`, los produce `micro/rtl/verificar_hueco.py` durante la corrida de tests del orquestador, y no entran al commit.
- **Alcance:** todo lo que cambió está dentro de §1 (puntos 1, 2, 3 y 5, más la errata autorizada). No se tocó nada de lo excluido: las fechas que difieren en un día, `Z_FUTILIDAD`, `UMBRALES_OBF`/`FRACCIONES` y el patrón `MDE 7 pp`.

### 2. Barrido

Comando: `grep -rnE "(^|[^0-9.,])(354|708|1[.,]062|979|1[.,]468)([^0-9]|$)|2027-05-28|1[.,]0241"` sobre `GEMELO/SECUENCIAL/` y `GEMELO/resultados/espera_firma.md`.

| Aparición | Clase | Por qué |
|---|---|---|
| `mirada.py:215` | H | docstring: el factor cableado (retirado) como historia del defecto |
| `mirada.py:217` | H | `354 acá y 355 allá`: cita del defecto O-1 |
| `DISEÑO.md:2086` (G1) | H | registro de cambios: qué decía |
| `DISEÑO.md:2087` (G2) | H | registro de cambios: los n viejos como qué decía |
| `DISEÑO.md:2126` (E11) | H | `354 → 358` es el registro de intentos, otra cantidad |
| `DISEÑO.md:2145` (F6) | H | registro de cambios: el valor cableado `no reproducía` |
| `diseno_secuencial.py:126`, `:135` | H | comentario de la historia del defecto |
| `diseno_secuencial.py:167` | H | constante histórica con nombre (`…_CABLEADO_HASTA_LA_CORRIDA_17`) |
| `tabla_firma.py:62` | H | comentario: el valor viejo, que no reproduce |
| `horizonte.py:65` | **V, preexistente** | `FACTOR_OBF = 1.0241` usado como factor (valor retirado), con un comentario que remite a `DISEÑO.md §A3.3`, donde ya no figura |

En `espera_firma.md`: ninguna aparición. En la tabla, ningún valor de la generación vieja presentado como vigente, salvo `horizonte.py:65`.

**`horizonte.py:65`** no está en el diff ni en la lista del commit (idéntico a HEAD). No consume `N_max`: alimenta `horizonte.json` y `horizonte.md`, no `mirada.py` ni `tabla_firma.py`. El acta §108.16 lo declara abierto y reserva la decisión a Nicolás. Arreglarlo acá sería un arreglo oportunista que R7 prohíbe, así que no bloquea. Queda inventariado.

Consecuencia menor de esta corrida: el comentario de `horizonte.py:65` ahora apunta a un §A3.3 que ya no muestra ese valor. Va con la decisión de §108.16.

### 3. Tablas de `DISEÑO.md` contra `tabla_firma_17.json`

Coinciden todas las celdas.

**§A3.3 (1381-1385), columnas `n_iid`, `n_con_deff` y `N_max`:**

| MDE | DISEÑO.md | json |
|---|---|---|
| 4.94 | 1.579 / 5.686 / 5.836 | 1579 / 5686 / 5836 |
| 8.51 | 531 / 1.912 / 1.962 | 531 / 1912 / 1962 |
| 10 | 384 / 1.383 / 1.419 | 384 / 1383 / 1419 |
| 11.09 | 312 / 1.122 / 1.152 | 312 / 1122 / 1152 |
| 13.09 | 223 / 803 / 825 | 223 / 803 / 825 |

La afirmación de la línea 1386, `potencia del plan es 0.80 exacta`, coincide con `potencia_idealizada` = 0.8000008 del json.

**§A3.5 (1523-1526), n → fecha:**

| Mirada | 8.51 pp en DISEÑO.md | 8.51 pp en json | 10 pp en DISEÑO.md | 10 pp en json |
|---|---|---|---|---|
| 1 | 490 → 2026-11-30 | 490 / 2026-11-30 | 355 → 2026-11-04 | 355 / 2026-11-04 |
| 2 | 981 → 2027-03-01 | 981 / 2027-03-01 | 710 → 2027-01-08 | 710 / 2027-01-08 |
| 3 | 1.472 → 2027-05-31 | 1472 / 2027-05-31 | 1.064 → 2027-03-16 | 1064 / 2027-03-16 |
| 4 | 1.962 → 2027-08-27 | 1962 / 2027-08-27 | 1.419 → 2027-05-20 | 1419 / 2027-05-20 |

**§A3.1.d, abanico (1008-1012), `N_max` / primera mirada / análisis final:**

| MDE | Valores (DISEÑO.md = json) |
|---|---|
| 4.94 | 5.836 / 2027-05-27 / 2029-08-14 |
| 8.51 | 1.962 / 2026-11-30 / 2027-08-27 |
| 11.09 | 1.152 / ya vencida (json: `ALCANZADO`) / 2027-03-31 |
| 13.09 | 825 / ya vencida (json: `ALCANZADO`) / 2027-01-29 |
| 10.00 | 1.419 / 2026-11-04 / 2027-05-20 |

**Propagación conjunta (985-989), contra `conjunta` del json:**

| Fila | Valores en DISEÑO.md | Coincide con json |
|---|---|---|
| `N_max` | 1.920 [1.025, 4.153] | sí |
| Mirada 1 | 480 → 2026-11-27 [256, 1.038] | sí |
| Mirada 2 | 960 → 2027-02-24 [513, 2.077] | sí |
| Mirada 3 | 1.440 → 2027-05-24 [769, 3.115] | sí |
| Mirada 4 | 1.920 → 2027-08-20 | sí |

Los valores del json están redondeados al entero.

La prosa nueva remite a `factor_secuencial` y a `potencia.drift_requerido`, y las dos claves existen en el json: 1.0263801871775526 y 2.8382978439331055.

### 4. Registro de cambios

- **G1 (`DISEÑO.md:2086`)** cubre el cambio de prosa y encabezado de §A3.3: qué decía, qué dice, la sección y la razón `O-1, re-dictamen del guardián, 25-nov`.
- **G2 (`:2087`)** cubre las tres filas de §A3.5, con los mismos campos.
- El comentario de `mirada.py` no lleva fila. Es correcto: el registro es del documento, y §1.5 lo pide solo para `DISEÑO.md`.
- La errata de la bitácora se declara a sí misma en su propia línea.

### 5. Reglas duras

- **Intocables:** los catorce archivos de la primera pasada salen `IGUAL` (14 de 14) comparando el sha256 de `git show origin/main:<f>` con el del árbol. `git diff --stat origin/main -- api/ dinero/ corredor/ systemd/ launchd/ .claude/ scripts/ mki` sale vacío.
- **Cero escrituras a base:**
  - El diff de esta corrida es texto: un comentario en `.py` y prosa y tablas en `.md`. No hay ninguna línea de código nueva.
  - Huellas de las tres bases en `tests_18a_bis.log`, antes (líneas 2-4) y después (líneas 15-17), idénticas: `efa48f01…` senales.db, `97ee6454…` noticias.db, `07aed706…` sello_dinero.db.
- **Candados**, verificados leyendo el código, sin ejecutar nada:
  - `mirada.py:86` `MDE_FIRMADO = None` y `:136` `REGLA_DEDUP_ESTIMADOR = None`.
  - `ejecutar()` llama a `plan()` y a `_guard_regla_estimador()` antes de `cargar_ventana_nueva()`. Esta corrida no tocó código de `mirada.py`: el diff es solo las líneas 183-184.
  - Los tests que los fijan (`test_secuencial.py`, `test_secuencial_17.py`) están dentro de la corrida del orquestador.
- **Verdes:** `tests_18a_bis.log` da `285 passed, 1 skipped, 1 xfailed in 269.68s`, `RC_PYTEST=0`, `FIN 2026-11-25 17:02:40 -03`. Las huellas de los cuatro archivos editados registradas en el log coinciden con el árbol al cierre (`e893da1c…`, `881f3cde…`, `9123920e…`, `c40a10bf…`), así que los tests corrieron sobre el texto final.
- **Otros:** `GEMELO/SECUENCIAL/miradas/` no existe al cierre. No hubo worktree, ni bases abiertas, ni push, pull, commit, add o stash, ni cambios en systemd o `.env`.

### 6. NO VERIFICADO

- **La suite completa sobre el texto final.** No se corrió en esta corrida; la corre el hook del commit. El verde de arriba es parcial: 9 archivos de test.
- **Los candados por ejecución.** Esta vez los verifiqué solo leyendo el código y con los tests del log, como pedía el encargo. La verificación por ejecución es la de la primera pasada, sobre un `mirada.py` cuyo código no cambió.
- **Qué tests contiene `tests_18a_bis.log`.** El log no lista los archivos, así que me apoyo en el censo que declara el orquestador.
- **El texto de la frase que corrige la errata de §12.** No encontré literalmente `lo commitean su propio job` en el §12 actual; la frase más cercana es `son de los jobs del riel, no de acá` (`bitacora_17.md:645-647`). La errata es coherente con esa frase, pero no confirmé que sea la que el acta §109.4 (2) cita.
