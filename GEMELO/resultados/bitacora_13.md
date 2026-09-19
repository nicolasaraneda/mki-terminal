# Bitácora de la decimotercera corrida — cerrar las fugas que E0 mostró en nueve noches, medir a qué hora existe el cierre, README en inglés desde el árbitro

**19-sep-2026, sábado, nocturna y sin supervisión.** Encargo: `~/encargo.md` (copiado a
`GEMELO/resultados/encargo_corrida_13.md`). Arranque **16:24 hora de Chile** (leído de `date`:
`Sat Sep 19 16:24:57 -03 2026`). HEAD al abrir: `2493bb9` (Backup diario 2026-09-18). Modelo:
Fable, esfuerzo alto, sin cambio a mitad de sesión.

- Nada se pushea. Nada se firma. Nada se opera. Ningún archivo protegido se toca. El sellador
  real (`python -m dinero.sello_dinero --sellar`) NO se corre bajo ninguna circunstancia.
  Ninguna credencial en logs, bitácora, tests ni artefactos.
- Ventanas: la de sellado del riel de medición (17:50–20:30 Chile) es de días hábiles y hoy es
  sábado — `systemctl --user list-timers` da el próximo disparo de `mki-noticias.timer` el lunes
  21-sep 17:50 −03; la regla se respeta igual en lo que se pueda y se anota si algo la cruza.
  La del sellador de dinero: `mki-sello-dinero.timer` instalado como timer de usuario,
  `OnCalendar=Mon..Fri 23:30 America/New_York`, último disparo sábado 19-sep 00:30 −03, **próximo
  martes 22-sep 00:30 −03** (leído de la máquina, no del encargo). Entre 00:00 y 01:00 Chile no se
  toca `dinero/` ni se abre `dinero/sello_dinero.db`.

## Bloque 0 — orientación y prerrequisitos (16:24 a 16:33, `date`; los agentes terminaron 16:27–16:28)

**Suite al abrir: 855 passed, 5 skipped, 1 xfailed, 29 warnings en 422,37 s** (`./mki tests`,
arrancó 16:25, terminó 16:33 según el log); `tests/test_motor.py` OK (todas las funciones del motor
sin look-ahead). El encargo esperaba 856 / 4 / 1 en `490f984`: **hay un test más saltado y uno
menos pasado**; se identifica en la corrida con `-rs` de este bloque 1 y se anota. Verde = sin fallos
no declarados: se cumple. Inventario de xfail esperado, declarado antes de leer la salida: 1.

**Prerrequisitos (0.7), leídos de la máquina y no del encargo:**

- **E0 en `dinero/sello_dinero.db` (solo lectura, `mode=ro`), copia textual del resumen:**

  ```
  sellos_dinero: 297 filas; divergencias_sello: 1 fila
  fecha_insumo  estado              cuenta_para_N  filas  insumo_ext_sha256 (12)  timestamp_utc
  2026-09-08    pendiente           1              33     89a5e296366c            2026-09-09T03:38:17.156824+00:00
  2026-09-09    insumo_incompleto   0              33     126e4f2c769b            2026-09-10T00:00:04.881124+00:00
  2026-09-10    pendiente           1              33     3cc65546079c            2026-09-11T03:30:04.598884+00:00
  2026-09-11    pendiente           1              33     69126fa20f7a            2026-09-12T03:30:04.091372+00:00
  2026-09-14    pendiente           1              33     74ebdd00920f            2026-09-15T03:30:03.996876+00:00
  2026-09-15    pendiente           1              33     edc60fad1da9            2026-09-16T03:30:04.961251+00:00
  2026-09-16    pendiente           1              33     664e4f49bf5f            2026-09-17T03:30:04.877326+00:00
  2026-09-17    pendiente           1              33     cbec21bacf1a            2026-09-18T03:30:05.039340+00:00
  2026-09-18    insumo_incompleto   0              33     e71b78214156            2026-09-19T03:30:04.782582+00:00
  contador COUNT(DISTINCT fecha_insumo) WHERE cuenta_para_N = 1: 7
  precio_ref_usd IS NULL: 31 filas del 2026-09-09 (todos menos SHECY y TOELY) y 1 fila del 2026-09-18 (TOELY)
  divergencias_sello: (1, '2026-09-09', '2026-09-10T03:30:04.599658+00:00',
    sha_sellado '126e4f2c769bae8c8a25a24b0afa55dd69196ccd45ceb50534de8920e45a57ca',
    sha_nuevo   '7300787b015b5f4e9245a8e6d380b42ee8cc3ff8399a1cda61d0771e81a6e4f8',
    decisiones_distintas 1, 'segundo sello del 2026-09-09 con otro insumo; 1 decisión(es) distinta(s);
    las filas selladas no se tocan', creado_en '2026-09-10T03:30:04.752105+00:00')
  ```
  Coincide con lo que el encargo dice que Nicolás vio el 19-sep: cuentan 08, 10, 11, 14, 15, 16 y 17;
  no cuentan 09 y 18 por `insumo_incompleto`; una divergencia; **contador 7 de 40** (E0 sella el sorteo
  sin información: prueba de maquinaria, no track record — §86.2). Todas las filas
  con `plataforma_version 5.1.0` y `version_sello E0.2`.
- **Huellas antes de la primera escritura del bloque 1 (19:36:56 UTC = 16:36:56 −03):** `dinero/sello_dinero.db` sha256
  `30d4b988…a31e5ea3`, mtime 2026-09-19 00:30:04 −03; `senales.db` sha256 `d476b457…c259267`,
  mtime 2026-09-18 18:15:27 −03. Se vuelven a medir al cierre: tienen que ser idénticas.
- **`git status --short`:** exactamente lo esperado — `M data/backups/sello_dinero.csv` (33 filas
  nuevas del sello del 18-sep, que el job de backup commitea el lunes) y `??` en
  `dinero/datos/sello/ext_2026-09-{10,11,14,15,16,17,18}.{csv,meta.json}` y
  `data/backups/sello_dinero_ext/ext_2026-09-18.*`, más `README_en_borrador.md`. Ningún otro
  archivo modificado.
- **`README_en_borrador.md` EXISTE** en la raíz (10.010 bytes, 110 líneas, mtime 19-sep 16:22): el
  bloque 5 se hace con borrador.
- **Generador de README: NO existe** (re-verificado: `grep -rn "README" --include=*.py` fuera de
  `venv/` sólo da citas, tests y comentarios; ningún módulo escribe `README.md`). `README.md` es
  texto a mano. El bloque 5 empieza por la maquinaria.
- **Restauración del 09-sep (sección 2 del encargo), verificada y no repetida:**
  `dinero/datos/sello/ext_2026-09-09.csv` en disco sha256 `126e4f2c…` (mtime 19-sep 16:12, el
  `git checkout` de Nicolás) = `insumo_ext_sha256` de sus 33 filas = `git show 490f984:` de las dos
  copias. **El backup NO propagó la fuga** (verificación que pidió el pre-mortem): la copia
  `data/backups/sello_dinero_ext/ext_2026-09-09.csv` tiene mtime 9-sep 21:00 (la escribió el primer
  sello) y sha `126e4f2c…`; el disparo del 10-sep terminó en `divergencia_registrada` y `main()`
  sólo respalda cuando el resultado es `sellada`. Sólo existe un commit que toca esas rutas
  (`490f984`), con el sha correcto. El contenido `7300787b…` ya no existe en ninguna parte: sólo
  su sha en la fila de divergencia.
- **Las nueve extensiones en disco coinciden con la base:** el sha256 de cada
  `dinero/datos/sello/ext_<fecha>.csv` es igual al `insumo_ext_sha256` de sus filas, y las copias
  en `data/backups/sello_dinero_ext/` son byte a byte iguales (csv y meta) — leído con `sha256sum`
  antes de escribir ningún test.
- **El 18-sep (bloque 3.1):** la única fila con `precio_ref_usd IS NULL` es **TOELY** (Tokyo
  Electron, ADR de mostrador). En `ext_2026-09-18.csv` la columna TOELY está vacía en 08, 09, 10,
  11, 14, 15 y 18 de septiembre y tiene dato sólo en 16 y 17; su `ultimo_cierre` en el meta es
  2026-09-17. Y más: en `ext_2026-09-16.csv` (descargado el 17-sep 03:30 UTC) TOELY tenía dato en
  TODAS las sesiones del 08 al 16; en `ext_2026-09-17.csv` esas mismas fechas siguen en el índice con el
  cierre vacío (y el dato del 16 y del 17 es idéntico, `164.55…`). **MEDIDO: en dos descargas por la misma
  ruta separadas 24 h, los cierres de TOELY del 08 al 15 pasaron de estar a estar vacíos (n = 1 par, 1
  ticker). PROPUESTA: que el borrado ocurra en Yahoo y no en la ruta de descarga no se probó con una
  segunda vía.** El 09-sep a las 21:00 Chile, los ÚNICOS dos con dato eran SHECY y TOELY
  (los dos ADR de mostrador). Va a la tarjeta §58.
- Orientación (`orientador`, 16:27): §86 (líneas 9176–9190 de `DECISIONES.md`; 86.5: la fila del 9-sep se deja como está) firma §57 (86.1),
  §51 (86.2), §52 (86.3) y §53 (86.4). **La confirmación de la opción (a) del hallazgo 2
  (`.gitignore` para `dinero/datos/sello/`) NO consta en ningún documento** (§86, `espera_firma.md`,
  `cola_decisiones.md`, `bitacora_12.md`, `dictamen_12/`): sólo en la tabla del encargo, que dice
  «pendiente». `revision_corrida_12_2026-09-09.md` **no está en el repo**. La zona ciega Z1 del
  dictamen 12 nombra `visible_en` tres veces y **no lo define** (ni qué campo ni cómo se calcula).
  `DOCUMENTOS_PUBLICADOS` vive en `cifras.py:240` (README.md, estado_epistemico.md, la skill
  cifras-canonicas, VISION.md) — `README.es.md` no está; el chequeo 7 de `test_epistemico.py`
  nombra `README.md` a mano. Marcas de cita histórica que el escáner reconoce:
  `cifras.MARCAS_FUERTES = ("retirad", "errata", "derogad", "desmont", "refutad")` más el criterio
  del 7-sep (marcas ambiguas sólo exentan si el contexto nombra la cifra). Contadores: gap asiático
  354 (`GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO`), veredicto 5.1 declara 360
  (`backtest.veredicto_51.N_INTENTOS_51`), riel largo 3. `ESTADO.md` está fechado 9-sep y dice
  «1 sesión sellada de 40»: desactualización esperable, se corrige en el bloque 4.

## Pre-mortem del `director-programa`, antes del bloque 1 (recibido 16:28, hora de `date`)

Doce instrucciones marcadas. Qué se hace con cada una, decidido ANTES del bloque 1:

| # | Instrucción marcada | Decisión del orquestador |
|---|---|---|
| 1 | 0.4 y 10.8 se contradicen: la suite final abre la base real (test de integridad) y una corrida nocturna cierra justo en 00:00–01:00 Chile | **Acatada.** La suite final y el cierre se corren FUERA de esa franja; el test de integridad abre la base en `mode=ro`. Hoy además es sábado y el próximo disparo es el martes 00:30, pero la franja se respeta igual. |
| 2 | 0.4 fija «00:30 Chile» como hora de pared; deja de ser cierto el 1-nov (NY vuelve a EST) | **Ejecutada con anotación.** La regla se lee del `OnCalendar` instalado (`Mon..Fri 23:30 America/New_York`) y la bitácora anota el próximo disparo real leído de `systemctl --user list-timers`. |
| 3 | 1.2 + 4.4 son DOS cambios al sellador en producción la misma noche, sin nadie despierto | **Acatada.** Esta noche se aplica sólo el arreglo de E4 (1.2). `visible_en` (4.4) NO se toca en el sellador: Z1 no está definida con precisión (orientador) y el encargo manda en ese caso escribir la pregunta en `espera_firma.md`. Un cambio por noche al sellador. |
| 4 | 1.3: un test de la suite acoplado a la base y a archivos de producción se pone rojo en checkouts sin base | **Acatada.** El test salta con razón declarada si no hay base o no hay extensiones; su rojo significa «parar y reportar», nunca «arreglar el archivo», y lo dice el docstring. |
| 5 | 1.4: «el archivo original sobrevivió en git» hay que verificarlo; el backup pudo propagar la fuga | **Verificada antes** (bloque 0): no la propagó. |
| 6 | 4.3: `git rm --cached` retira evidencia versionada apoyándose en una confirmación que ningún documento contiene, y `ext_2026-09-18.*` de backups aún no está commiteado | **NO ejecutada, anotada.** Sin firma escrita no se ejecuta. Condición para adelante: firma en `espera_firma.md`/acta y que cada `fecha_insumo` sellada tenga su par commiteado en `data/backups/sello_dinero_ext/`. |
| 7 | 2.2: «si no existe la etiqueta, se propone y se agrega al escáner» instala una norma de paso | **Ejecutada con anotación.** Existen `MARCAS_FUERTES`; si hiciera falta una marca nueva, se declara en el acta como norma instalada de paso (§85.8 bis) y aceptarla es acto de Nicolás. |
| 8 | 5.2: ampliar `DOCUMENTOS_PUBLICADOS` ensancha el perímetro del guardia y activa patrones inertes | **Ejecutada con anotación.** El escáner corre sobre el perímetro nuevo ANTES de tocar texto, para atribuir cualquier rojo al perímetro y no al README nuevo. |
| 9 | 5.3 → 5.4: un README a medias es peor que no empezar | **Acatada, regla de todo-o-nada declarada antes del primer byte:** si 5.3 se para, 5.4 queda NO INICIADO y `README.md` no se toca. |
| 10 | 3.3: `OnCalendar=Mon..Fri 17..23:00,30` incluye 23:30 NY, el minuto exacto en que el sellador baja su insumo | **Ejecutada con corrección declarada.** La propuesta usa `Mon..Fri 17..23:05,35 America/New_York` (desplazada 5 min: nunca coincide con el sellador) y la tarjeta §58 lo dice. |
| 11 | 3.2: «respuestas grabadas» que no existen; grabarlas exige una descarga | **Verificada antes:** las extensiones `ext_*.csv` ya son respuestas grabadas de yfinance (la matriz `Close` que devolvió cada noche). La sonda se diseña para recibir ese `DataFrame` y el test lo lee del disco. Sin red, sin descarga nueva. |
| 12 | Prioridad §11: `ESTADO.md` contradice a la base (1 vs 7) y va detrás del README | **Acatada.** 4.1 y 4.2 se hacen apenas cierre el bloque 1, antes del 5. |

Sin objeción del director: 0.2, 1.1, 1.5, 3.1, 3.4, 3.5, 4.5, 6 y la lista del §9.

**Instrucciones que el orquestador marca por su cuenta:** ninguna adicional al arrancar. El registro
de intentos del gap asiático (354) y el del riel largo (3) **no se tocan** salvo que un bloque pruebe
una hipótesis; se cuenta al cierre.

## Bloque 1 — la fuga de integridad que E4 dejó: el archivo en disco (16:33 a 17:02, `date`)

**El mecanismo, leído del código y no del encargo.** `main()` de `dinero/sello_dinero.py` llama a
`congelar_extension()` ANTES de `sellar()`; `congelar_extension()` escribía `ext_<hasta>.csv` y su
`.meta.json` sin mirar la base, y el guardia E4 vive dentro de `sellar()`. El 10-sep 03:30 UTC el
timer bajó un insumo del 09-sep distinto del sellado a las 00:00 UTC (ya traía el cierre del día):
E4 registró la divergencia (sha `7300787b…` contra `126e4f2c…`, 1 decisión distinta, 0 filas) y el
archivo sellado ya estaba pisado. Nueve días el disco citó un sha que no tenía. El contenido
`7300787b…` no existe en ningún lado.

**Dictamen del `auditor-lookahead`** (`dictamen_13/auditor_e4_archivo.md`; lanzado tras las huellas de las 16:36:56 y recibido a los 334 s según el propio agente): dos fugas
demostradas — F1 (otro insumo pisa el archivo sellado) y **F2, que el encargo no traía: con el
MISMO insumo también se reescribían los dos archivos** (demostrado por `mtime`; que el meta cambie de sha
en producción por `congelado_en_utc` distinto es inferencia del auditor, no ejecutada). Test de reproducción escrito ANTES de la corrección,
camino de `main()` (congelar + sellar), base y carpeta temporales: `FF. 2 failed, 1 passed` sobre
el código de la corrida 12 (salida pegada en el dictamen). Por qué la suite de la 12 no lo vio: su
test E4 fabricaba las dos extensiones a mano en dos carpetas y nunca ejercía `congelar_extension`.
**Opción dictaminada: (A) con una pieza de (B).** Con la fecha ya sellada no se escribe NINGÚN
archivo de esa fecha en `dinero/datos/sello/` (ni el canónico ni uno «divergente»); el sha del
insumo divergente se calcula en memoria, y el `detalle` de `divergencias_sello` declara que apunta
a un contenido no conservado. Razones del auditor: (B) hace auditable un insumo que nadie selló a
cambio de abrir una ruta de escritura nueva sobre la carpeta de la evidencia (la misma que el 4.3
quiere sacar de git), y su `ultima_extension()` de entonces habría levantado el divergente al día
siguiente con `--sin-red`. **Error propio detectado:** el orquestador había implementado (B) en el
worktree antes del dictamen (con el filtro de nombre que neutralizaba el riesgo de
`ultima_extension`); se descartó y se implementó (A). El diff de (B) quedó en el scratchpad, no en
el repo. **R4 del auditor, tampoco en el encargo:** E4 filtra por `juego`, así que un cambio de
`juego_activo` habría vuelto a sellar (y a escribir) una fecha ya sellada; el guardia nuevo mira
sólo la fecha y el test permanente exige UN sha por `fecha_insumo` sin filtrar por juego. **R5:**
el congelado grande también se verifica contra `insumo_base_sha256`.

**La corrección (E4-bis), desarrollada y probada en un `git worktree` temporal desde HEAD `2493bb9`
con copias de las bases y de las extensiones sin trackear:** `sello_previo(fecha, ruta_db)` (solo
lectura); `congelar_extension(…, ruta_db)` → sin sello: como siempre; sello con el mismo sha: no
escribe nada (ni bytes idénticos) y devuelve lo que hay; sello con otro sha: temporal fuera de
`DIR_EXT`, `meta["persistido"] = False`, `main()` lo borra tras `sellar()`; `sellar()` escribe en
`detalle` «contenido divergente NO conservado … sha_nuevo es el de un contenido que ya no existe»;
`main()` exporta el CSV (la tabla de divergencias también se versiona) y NO respalda nada en una
divergencia; `es_extension_sellable()` restringe `--sin-red` a `ext_YYYY-MM-DD.csv`. Suite completa
en el worktree (16:50:39 a 16:57:47, `date`): **865 passed, 1 failed, 5 skipped, 1 xfailed** — el
fallo era `test_backtest.py::test_los_N_historicos_de_la_banda_reproducen_los_resumenes_sellados`
porque dos corridas selladas de `backtest/resultados/` están gitignoradas y el worktree no las
tenía; copiadas, `test_backtest.py` 49 passed (terminó a las 17:02:11 según `date`, la misma marca
de la aplicación que sigue). `tests/test_motor.py` OK. El quinto skip
respecto de los 4 del encargo es `test_epistemico.py:824` («las dos rutas coinciden a la precisión
publicada»): depende de la cadena sellada viva, no de esta corrida.

**Aplicado al árbol real a las 17:02:11 (`date`), fuera de la ventana 00:00–01:00 Chile;** después,
`test_sello_dinero.py` + `test_dinero.py`: 70 passed. **Huellas:** `dinero/sello_dinero.db`
sha256 `30d4b988…` antes y después, mtime 00:30:04 del 19-sep sin cambio; `senales.db`
`d476b457…` sin cambio; `ext_2026-09-09.csv` `126e4f2c…`. El sellador pasa de sha `93db9b70…` a
`480fbdc9…`: desde el próximo sello (martes 22-sep 00:30 Chile) las filas nuevas llevarán ese
`sellador_sha256`, campo declarado (E6), no reescritura. Tests nuevos en `tests/test_sello_dinero.py`
(sección 3: los tres del auditor + cuatro de la forma de la corrección; sección 4: integridad
permanente sobre la base REAL en `mode=ro` para `dinero/datos/sello/`, `data/backups/sello_dinero_ext/`
y el congelado grande, con skip declarado si no hay base y contraprueba de que ve un archivo
pisado). Hoy pasan sobre la base real: las nueve fechas citan lo que el disco tiene. Dado el sha
registrado en `divergencias_sello` y la restauración del 19-sep, el chequeo sobre `2026-09-09` **habría
fallado** entre el 10-sep 00:30 y el 19-sep 16:12 hora de Chile — inferencia, no ejecución.

## Bloque 2 — reintroducciones preexistentes de cifras retiradas (en paralelo con la suite del bloque 1, 16:50–17:02; sin marca propia de `date`)

Escaneo con `cifras.reintroducciones()` (el mismo instrumento del test) sobre los archivos que la
revisión nombró: `cifras.py` 2, `tests/test_bifurcaciones.py` 2, `espera_firma.md` 3,
`cola_decisiones.md` 6, `DECISIONES.md` 53. Veredicto por caso:

| dónde | qué | veredicto | acción |
|---|---|---|---|
| `cifras.py:46` | comentario «(era n = 248)» junto a `CORTE_README` | cita histórica sin marca fuerte («era» es ambigua y el contexto no repite el patrón) | marca «cifra RETIRADA el 3-sep-2026, acta §78» en el comentario |
| `cifras.py:273` | comentario que explica `MARCAS_FUERTES` con el 91,4 % | cita histórica de la propia regla | «(cifra retirada, acta §68)» en la misma línea |
| `tests/test_bifurcaciones.py:241/246` | docstring y `assert` con 0.1849 / 0.1847 | **ejecutable con la cifra**, pero no la publica: prueba que las dos rutas de McNemar difieren sobre el par (72, 56) de la rama derogada | docstring con «cifras RETIRADAS … acta §78» y comentario en el `assert`; el número se queda porque es la prueba de método |
| `espera_firma.md` 463, 911, 1349 | +6,5 pp; potencia 0,36 [0,34, 0,37]; 14 % a 43 % | citas históricas en tarjetas anteriores al retiro | «(cifra retirada …, acta §…)» en la misma línea |
| `cola_decisiones.md` 203, 242, 475, 495, 502, 1036 | 0,1849 (×3), +6,5 pp (×2), 0,36 [0,34, 0,37] | ídem | ídem; en la tabla del §2a la fila «sin deduplicar» dice «rama derogada y cifras retiradas, acta §78» |
| `DECISIONES.md` (53 líneas) | actas §47–§78 citando 0.1849, +6.5, 91.4 %, −3.3 pp, «saturó»… | **actas históricas: no se reescriben.** `DECISIONES.md` no está en `DOCUMENTOS_PUBLICADOS` por diseño (es la historia, con sus erratas fechadas al lado) | **no se tocan**; se declara acá y en el acta. Si Nicolás quiere que el escáner las cubra, es una norma nueva |

Después de las etiquetas, el escáner da 0 en los cuatro archivos vivos. **No hizo falta ninguna marca
nueva** (`MARCAS_FUERTES` ya reconoce «retirad»/«derogad»): no se instaló ninguna norma de paso. Las
ediciones se hicieron con la herramienta que el hook `guardia-reglas.py` (bloque 8) inspecciona, y el
hook las dejó pasar porque el texto nuevo trae la marca en la misma línea.

## Bloque 3 — la sonda: a qué hora existe el cierre en yfinance (en paralelo con el bloque 1; tests verdes 17:05 y unidades escritas antes de las 17:10, `date`)

- **3.1, el 18-sep:** `precio_ref_usd IS NULL` sólo en **TOELY** (Tokyo Electron, ADR OTC); en
  `ext_2026-09-18.csv` la columna TOELY está vacía en 08, 09, 10, 11, 14, 15 y 18-sep y tiene dato en
  16 y 17; `ultimo_cierre` 2026-09-17. Y el hallazgo que no pedía el encargo: en `ext_2026-09-16.csv`
  (17-sep 03:30 UTC) TOELY tenía dato en TODAS las sesiones 08–16; en `ext_2026-09-17.csv` (24 h
  después) las mismas fechas traen el cierre vacío. **MEDIDO** (un par de descargas por la misma ruta, un
  ticker); que sea Yahoo y no la ruta de descarga es **PROPUESTA** sin segunda vía. El 9-sep a las 21:00 Chile los únicos con dato eran SHECY y
  TOELY (los dos ADR de mostrador). Está en la tarjeta §58.
- **3.2, la sonda** `GEMELO/sonda_cierre.py`: `observar(cierres, ahora_utc)` es función pura de
  (respuesta, instante); `descargar()` es la única función con red; `registrar()` hace append a
  `data/sonda_cierre.csv` (columnas: `timestamp_utc, hora_ny, sesion_ny, ticker, ultima_fecha_close,
  es_sesion_de_hoy, close_ultimo, n_filas_respuesta`); `--desde-csv` permite observar una matriz ya
  grabada sin red. Lee los 36 tickers del meta del congelado como texto. No sella, no escribe en
  `dinero/`, no abre bases, no importa `dinero`, `sqlite3` ni el camino de sellado (test AST). **La
  respuesta grabada del test es `ext_2026-09-18.csv`** (lo que yfinance devolvió el 19-sep 03:30 UTC):
  35 de 36 con cierre de hoy, TOELY con último cierre 17-sep. Sin descarga nueva.
- **3.3, la unidad propuesta** `GEMELO/propuestas/systemd/mki-sonda-cierre.{service,timer}`:
  `OnCalendar=Mon..Fri 17..23:05,35 America/New_York` (desplazada 5 min respecto de lo que pedía el
  encargo, para no coincidir con el sellador de las 23:30: pre-mortem ítem 10), `Persistent=false`.
  `systemd-analyze calendar`: forma normalizada `Mon..Fri *-*-* 17..23:05,35:00 America/New_York`,
  próximo disparo lunes 21-sep 18:05 −03. **No instalada.** El timer también trae la alternativa
  `20..23:05,35` por si Nicolás no quiere descargas en la ventana del riel de medición.
- **3.4, el resumen** `GEMELO/sonda_cierre_resumen.py`: por (noche, ticker) la primera sonda que vio el
  cierre; por ticker mediana/mínima/máxima y noches sin cierre hasta la última sonda; por noche la
  hora en que estuvieron todos o quiénes faltaron. Probado con un CSV sintético de tres noches y tres
  tickers (A siempre 17:05; B 19:35/20:05/19:35; C 22:05, 22:05, nunca) más una sonda de sábado que
  se ignora. Sin datos reales todavía: **no se generó ningún artefacto con cifras**.
- Tests: `tests/test_sonda_cierre.py`, 16 passed (incluye el de la unidad con `systemd-analyze`).
- **3.5, tarjeta §58** escrita con el dato, las tres opciones (a)/(b)/(c) con consecuencias y la
  recomendación etiquetada (correr la sonda 5–10 noches antes de elegir entre (b) y (c)). No se
  eligió nada.

## Bloque 5 — README en inglés, con generador primero (17:05 a 17:25, `date`; dictámenes después)

**Regla de todo-o-nada declarada antes del primer byte** (pre-mortem ítem 9): si el 5.3 no daba
byte a byte, el 5.4 quedaba NO INICIADO y `README.md` no se tocaba.

1. **Generador** `scripts/generar_readme.py`: plantillas `docs/readme/README.es.tmpl.md` y
   `README.en.tmpl.md` con marcadores `{{clave}}`; `valores()` los llena desde `cifras.sellada()`
   (33 claves), `cifras.larga()` (16, incluida la tabla por bolsa) y el contador de E0 leído de
   `data/backups/sello_dinero.csv` (la copia VERSIONADA de la base, para que el README sea regenerable
   en cualquier checkout) más `N_OBJETIVO_E0` del sellador como texto. Un marcador sin clave revienta con
   `MarcadorSinFuente` que lo nombra (test). `--verificar` compara con el disco sin escribir.
2. **Plantilla española derivada mecánicamente del README.md de esta mañana:** 24 sustituciones de
   texto exacto (cada una verificada como única antes de sustituir) → 46 marcadores distintos, 64
   ocurrencias; `render(plantilla) == README.md` **byte a byte: True**. `README.es.md` = ese README + la
   primera línea `[English version](README.md)` (única diferencia, declarada; el 5.5 pide el enlace
   cruzado). Lo que quedó LITERAL en la plantilla y no sale del árbitro: los aciertos por bolsa de la
   ventana larga (72.9 %, 53.8 %…, `cifras.larga()` no los guarda), las tablas del WS5 y del WS2b/WS3, las
   cifras de la auditoría WS4, el «~0.93» de `calibracion_instrumento.md`, la línea base del 25-ago
   (n=223, +4.0, 0.4633), la rama derogada con su errata, y los dos badges desactualizados `tests-650` y
   `plataforma-5.0.3` (**hallazgo, no corregido: ninguna cifra publicada se mueve sola**; los dos README
   los llevan igual). Cada cifra literal es una deuda declarada del árbitro, no una cifra a mano nueva.
3. **Guardias extendidos a los dos archivos:** `cifras.DOCUMENTOS_PUBLICADOS` incluye `README.es.md`; los
   nueve bloques del README pasan a `README.es.md` (`doce_bloques` sigue siendo doce) y una función nueva
   `cifras.bloques_readme_en()` da los nueve en inglés para `README.md`, del mismo dict (si n cambia,
   cambian los dos README o ninguno); `test_epistemico` chequeo 7 (p sin método) corre sobre los dos; la
   cita por línea de `GEMELO/bifurcaciones.py` pasa de «README.md líneas 124-126» (ya desplazada: la tabla
   vivía en 139–143) a «README.es.md líneas 139-143» (verificado). Escáner de reintroducciones sobre el
   perímetro nuevo ANTES de tocar texto (pre-mortem ítem 8): 0 en `README.es.md`.
4. **`README.md` en inglés** desde `README.en.tmpl.md`, escrita por un agente traductor con reglas
   ejecutables: mismos marcadores (más los cuatro de E0), ningún número distinto, negativos con la misma
   firmeza, vocabulario vigilado, TL;DR copiado verbatim (ya estaba en inglés), sección nueva «Execution
   rail (paper only)» con E0 en curso (contador desde la copia versionada: 9 selladas, 7 cuentan de 40,
   última 2026-09-18), E1 no ejecutado, E2 no iniciado y ninguna afirmación positiva. El borrador de
   Nicolás aportó el tono y UNA frase de apertura; sus ~40 placeholders sin fuente en el árbitro NO se
   llenaron: se descartaron con sus frases (regla del propio borrador). `tests/test_readme.py` (10 tests):
   generador reproduce los dos README; marcador sin fuente revienta; marcadores en↔es; los bloques del
   árbitro NO están escritos a mano en las plantillas y sí salen al renderizar; **paridad numérica: el
   multiconjunto de tokens numéricos de las dos páginas es idéntico** (fuera de la sección de E0);
   vocabulario prohibido (`confidence`/`confianza`/`alpha`; `edge`/`opportunity`/`returns` con estatus a
   ±2 líneas); enlaces cruzados en la primera línea; enlaces relativos existentes; contador de E0 = CSV.
   `README_en_borrador.md` queda sin trackear (es de Nicolás; no se borra ni se commitea).
5. Dictámenes del `curador-epistemico` y del `estadistico-adversario` sobre el inglés: abajo, en
   «Dictámenes de cierre».

## Bloque 6 — universo operable por presupuesto, con acciones enteras (17:03 a 17:13, `date`)

`GEMELO/universo_por_presupuesto.py` → `GEMELO/resultados/universo_por_presupuesto.{md,json}`, estatus
PROPUESTA. Por presupuesto de 100 a 500 USD de a 50: tickers que alcanzan una acción entera al último
cierre congelado (`construir_mapa` del riel, piso de comisión incluido), posiciones simultáneas (una
entera de cada una, las más baratas primero) y semillas del juego conservador congeladas antes de 156
semanas (definición de `m2_periodo.lecturas_m2`, E4 del §43), K = 20, Wilson sobre K, fricción a 156 como
mediana [mín, máx]. **Verificación contra la corrida 12: a 500 USD, 5 de 20 congeladas — COINCIDE** (misma
función y mismas semillas: es reproducción, no verificación independiente; el adversario lo dice). Lectura
cruda: 7 de 36 alcanzan a 100 USD, 13 a 250, 29 a 500; posiciones simultáneas 4 → 8; la fracción de
congeladas NO es monótona (12, 17, 7, 12, 7, 5, 4, 3, 5 de 20) porque `universo_operable` depende del techo y
a cada presupuesto la cuenta juega con otra membresía. Ninguna fila fija el monto de E2. Dictamen del
adversario: abajo.

## Bloque 4 — bookkeeping que las firmas del §86 dejaron pendiente (17:05 a 17:12, `date`; 4.5 después de las 20:30)

- **4.1** `espera_firma.md`: §51, §52, §53 y §57 marcadas FIRMADA en la cabecera con fecha 9-sep-2026 y
  referencia a §86.2, §86.3, §86.4 y §86.1 respectivamente, con una línea de lo firmado; el texto de cada
  tarjeta no se borró. §43 sigue abierta. Tarjetas nuevas: **§58** (hora del sellador y definición de
  «completo», con el dato, tres opciones y recomendación etiquetada), **§59** (`visible_en`: Z1 no está
  definida; la pregunta exacta con tres candidatos), **§60** (la confirmación de la opción (a) del hallazgo 2
  no consta en ningún documento: la pregunta con tres opciones).
- **4.2** `cola_decisiones.md`: sección «Qué movió la decimotercera corrida» al cierre (abajo). `ESTADO.md`:
  contador de E0 leído de la base (7 de 40, 9 sesiones selladas) al cierre.
- **4.3 NO EJECUTADO** (pre-mortem ítem 6; §60). Ni `.gitignore` ni `git rm --cached`.
- **4.4** `visible_en`: el dictamen 12 nombra Z1 tres veces y no define el campo ni su cálculo → pregunta
  en §59, nada en el sellador (un cambio por noche: pre-mortem ítem 3).
- **4.5** regenerar `bifurcaciones.{md,csv}` con las 4.000 réplicas del árbitro: se corre después de las
  20:30 (fuera de la ventana del riel de medición, aunque hoy sea sábado) y se compara cifra por cifra
  con el artefacto de 10.000; ver el cierre.

**Bloque 6, tras el adversario (17:23 a 17:30, `date`).** Dictamen `dictamen_13/adversario_universo_presupuesto.md`:
NO hasta corregir cinco cosas de rotulado y columnas (ninguna de cómputo): (1) «verificación» → reproducción
determinista, valor leído de `m2_periodo.json`; (2) la no monotonía es cambio de universo (operables en DESDE
18 → 33 por techo), no ruido: columna nueva y prohibición de leer en columna; (3) la mediana de fricción de la
mezcla invertía el orden (a 150 USD la cuenta viva paga ~23 % y a 400 ~14,5 %; la mezcla decía 12,0 % y 14,15 %):
fricción condicionada a vivas / congeladas con su n; (4) Wilson rotulado como error de simulación sobre UN camino;
(5) tres poblaciones y tres fechas separadas en dos tablas. No bloqueantes aplicadas: «posiciones simultáneas» →
cota superior nominal; tabla rotulada DESCRIPTIVA (sin verdad conocida para el estimador); registro de intentos del
riel largo 3 → 4; el insumo del §8.3 bajo §52 en `espera_firma.md`. Artefacto regenerado (17:30:33 UTC−3): 5 de 20 a
500 USD reproduce; sin cifra nueva sobre ventaja. **Puede publicarse como PROPUESTA.**

## Dictámenes de cierre (archivados en `GEMELO/resultados/dictamen_13/`)

- `auditor_e4_archivo.md` (bloque 1): dos fugas demostradas con test previo; opción A; nota fechada sobre F2.
- `curador_bitacora_y_tarjetas.md`: RECHAZADO al inicio (8 bloqueantes, todos aplicados: rótulos MEDIDO/PROPUESTA,
  contador con su etiqueta, intervalo de la proyección, cabeceras §52/§53 ajustadas al acta, horas con procedencia).
- `adversario_readme.md`: cifras IDÉNTICAS inglés ≡ español ≡ árbitro; dos bloqueantes de la página en ambos
  idiomas (contador de E0 desde HEAD, resuelto en la redacción y pendiente del commit del CSV; N de intentos
  352/358 contra 354/360, errata pendiente de Nicolás).
- `curador_readme_ingles.md`: RECHAZADO al inicio; B1–B4 aplicados (frase de apertura, negativo de la
  capturabilidad en las dos páginas, las dos sesiones que no cuentan nombradas, contador desde el CSV exportado),
  «edge» → «advantage», viñeta de la palabra prohibida reescrita, «to prove» → «to test».
- `adversario_universo_presupuesto.md` (bloque 6): cinco bloqueantes de rotulado, aplicados.

## Cierre

- **4.5 `bifurcaciones`: corrido a las 17:28 y REVERTIDO.** Con 4.000 réplicas el ancla se mueve sólo en el último
  decimal ([−7,2, +26,5] → [−7,2, +26,6]; cada uno contiene el cero), pero el nivel `vivo` del corte creció de 251
  filas (27-ago) a 371 (17-sep) y la matriz pasa de «0 de 192 celdas con p < 0,05 por clúster» a «20 de 192» y de
  [−1,1, +15,4] a [−1,1, +20,2] pp (cada rango contiene el cero; cifras NO DICTAMINADAS, fuera del repo):
  eso es una MEDICIÓN NUEVA sobre una cadena más larga, no un cambio de réplicas, y el encargo prohíbe afirmaciones
  nuevas sobre ventaja esta noche. El artefacto quedó como en HEAD; la corrida de 4.000 se guardó fuera del repo;
  la decisión (pinchar `vivo` o tratarlo como medición nueva con dictamen e intento) va a la cola (acta §87.4).
  Se corrió a las 17:28, antes de la ventana 17:50–20:30 (sábado, sin sello), sin esperar a las 20:30 como decía
  el bloque 4: cambio de plan declarado, no cruzó la ventana.
- **Conteo de intentos:** gap asiático 354 (sin cambio), veredicto 5.1 360 (sin cambio), riel largo 3 → 4 (el
  `director-programa` lo marcó como norma instalada de paso: declarada en §87.9, aceptarla es de Nicolás).
- **Director (cierre):** ADELANTE, nada de código a revertir; tres correcciones de etiqueta aplicadas (§87.9 norma
  de paso; cifras de bifurcaciones marcadas NO DICTAMINADAS en §87.4; no publicar README.md sin commitear el CSV
  del riel). Desvío declarado: el ítem 12 del pre-mortem (4.1/4.2 antes del 5) se cumplió en paralelo, no antes
  (§87.10). Deuda vista por el director: el test de paridad excluye la sección de E0 (sólo en inglés).
- `estado_epistemico.md` con la entrada de la corrida 13 (sólo lo que pasó por el adversario o el curador);
  `cola_decisiones.md` con «Qué movió la decimotercera corrida»; `ESTADO.md` regenerado (49 líneas); acta §87.
- **Errores propios detectados:** (1) implementé la opción B antes del dictamen del auditor (descartada);
  (2) escribí horas estimadas en los bloques 2 y 3 (corregido tras el curador: paralelismo declarado, sin horas
  propias); (3) «19:36:56 UTC, antes de tocar nada» era después del bloque 0; (4) la frase sobre Yahoo decía más
  que lo observado; (5) el 4.5 no era «regenerar»: lo descubrí al comparar, no antes de correr.
- **Guardián (árbol de las 17:41): APTO PARA QUE NICOLÁS LO MIRE** (`dictamen_13/guardian_y_director_cierre.md`), con
  dos condiciones: el número final de la suite completa y los tres sha256 reverificados al momento del commit
  (abajo), y la decisión de Nicolás sobre si la regla 10 alcanza a un archivo publicado NUEVO que hereda cifras
  vencidas (badges, «59×», N 352/358) en vez de moverlas solo. Pendiente no arreglado en esta tanda: un `assert`
  de guarda en `_camino_main` (tests/test_sello_dinero.py), que llama a `congelar_extension` contra el global.
- Secretos: 0 coincidencias con el patrón del pre-commit en todo lo cambiado y lo nuevo. Sin push.
- `README_en_borrador.md` sigue sin trackear (es el borrador de Nicolás; ni se borra ni se commitea).
- **Suite completa final (`./mki tests`, 17:40:14 a 17:47:28 según `date`): 891 passed, 5 skipped, 1 xfailed, 29
  warnings en 425,01 s; `tests/test_motor.py` OK.** De 855 al abrir a 891: +36 tests nuevos (sellador E4-bis e
  integridad, sonda, README, bloques en inglés). Una corrida previa (17:31–17:39) dio 890 passed y 1 rojo del guardia
  epistémico sobre esta misma bitácora (un intervalo con el cero sin la marca que el escáner reconoce): corregido y
  reejecutada entera. El test de integridad del bloque 1 corre y pasa sobre la base real en `mode=ro`. Los 5 skipped:
  los cuatro de parches ya aplicados y `test_epistemico.py:824` (las dos rutas de McNemar coinciden a la precisión
  publicada sobre la cadena viva). El xfail es el declarado.
- **Huellas al cierre (17:47:36, `date`):** `dinero/sello_dinero.db` `30d4b988…` (= apertura), `senales.db`
  `d476b457…` (= apertura), `ext_2026-09-09.csv` `126e4f2c…`. Worktree temporal retirado (`git worktree prune`).
- Cierre a las 17:47 hora de Chile, sábado: antes de la ventana 17:50–20:30 y lejos de la 00:00–01:00. Nada
  en `dinero/` se toca desde las 17:02. Sin push.
