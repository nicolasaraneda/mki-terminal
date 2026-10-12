# Auditoría de fuga y de corrección del `auditor-lookahead` sobre el Bloque C de la corrida 16-3: el parche `version_reglas_16_3.diff` del riel de dinero (NO aplicado)

> Archivado por el orquestador tal como lo devolvió el agente (el agente no escribe archivos). Lanzado a las 20:16 de
> Chile del 11-oct-2026 sobre el worktree `wt163_dinero` (HEAD `ad4b829` + el parche, sin commitear) y el diff de
> `wt163/GEMELO/propuestas/parches/`. Reloj de apertura **20:19:03**, de cierre **20:35:24** (−03:00, `date` del agente).
> El parche no se aplicó a ningún árbol; la base real sólo en `mode=ro`; bases temporales en el scratchpad; `git status`
> del árbol real igual al de apertura. **El dictamen es sobre la versión del parche con sha256 `f164b232…`; las tres
> bloqueantes se atendieron después (B1 cambió el código y el test; B2 fue a la receta; B3 se retomó con el archivo
> final), y el diff que se entrega es otro (huella y detalle en `version_reglas_16_3.md` y en la bitácora §5.2).**

## VEREDICTO: APLICABLE CON EXIGENCIAS

Tres exigencias BLOQUEANTES, ninguna por fuga temporal: una por una frase falsa que el parche puede sellar en un campo
inmutable (camino no alcanzable hoy por `main()`), una por un preflight que convierte el riesgo de R4 en una casilla
verificada, y una porque la evidencia de rojos archivada no es del archivo de test que el parche embarca.

## Fugas demostradas

Ninguna. Esto es lo que probé y lo que esa prueba deja fuera.

1. Fuga de valor futuro (prueba maestra). `gate_previo_al_sello` sobre el insumo REAL de la noche (congelado
   `cierres_congelados.csv` sha `69ca7283…` más `dinero/datos/sello/ext_2026-10-09.csv`) con el módulo parchado:
   `[{'cortes': 2, 'dia': '2026-10-08', 'resultado': 'INVARIANTE'}, {'cortes': 6, 'dia': '2026-10-02', 'resultado':
   'INVARIANTE'}]`, idéntico al de HEAD. MEDIDO.
2. Invariancia al truncado, barrido ancho: `huella_decision` más `operables`, `excluidos_universo`, `insumo_completo`,
   `sin_dato`, `riel_apagado`, `presupuesto`, `juego` y los 32 `motivo` de la decisión, para las ÚLTIMAS 40 SESIONES del
   congelado, HEAD contra parche: sha256 del volcado idéntico,
   `31a47b386a7aa78706fa7a0a49c9090d972e08907f7efac3198e6f727faff1fe` en los dos. MEDIDO.
3. Contraprueba de que el gate puede fallar: `tests/test_sello_dinero.py:77-91` inyecta la fuga G3 (precio de referencia
   de d+1) y exige `ErrorLookAhead`, más la guarda `VACUO` de la línea 98. Verde con el parche. MEDIDO.
4. Efecto retroactivo: cero. Ninguna fila existente cambia (el parche no emite sentencias de modificación ni de borrado,
   y los cuatro disparadores de inmutabilidad siguen en la base). Las 722 filas selladas quedan con `reglas_version =
   0.2.0-PROPUESTA` y sus dos huellas; el relabel sólo marca filas FUTURAS. MEDIDO.
5. Regla maestra `available_at < timestamp_utc < apertura objetivo`: el parche no toca `evaluar_timing`, ni `estado`, ni
   `estado_timing`, ni `cuenta_para_N`, ni las tres columnas de tiempo. En la fila de un intento la ÚNICA columna que
   difiere de HEAD es `motivo`. MEDIDO (ver 1.4).

## Sospechas sin demostrar, y la que se volvió hallazgo

6. HALLAZGO (no es fuga temporal, es una frase falsa sellada). El camino de reserva de §81.3 (b) atribuye el veredicto de
   timing al reloj del SELLO cuando el meta de una evidencia `.no_verificable` no trae el bloque `timing`. Medido con
   evidencia `ext_2026-10-09.no_verificable.csv`, meta sin `timing`, sellada a `2026-10-10T03:30:04+00:00` (un instante
   cuyo propio timing es OK, verificado con `evaluar_timing(...)["timing_ok"] = True`): la fila queda con `motivo` =
   «…; timing roto decidido con emisión 2026-10-10T03:30:04+00:00: la regla available_at 2026-10-09T20:00:00+00:00 <
   emisión < apertura objetivo 2026-10-12T13:30:00+00:00 no se cumple (§81.3 b)». A ese instante la regla SÍ se cumple:
   lo que rompió el timing fue la clase de la evidencia, no el reloj citado. Fila inmutable, afirmación falsa, imposible
   de corregir luego. DEDUCIDO que hoy no es alcanzable por `main()` (ver 3.c). El test nuevo del camino de reserva
   bendecía ese camino sólo en el caso en que el reloj del sello TAMBIÉN está roto, así que no cazaba el caso falso.
7. R4 acopla dos perillas independientes. El raise se dispara cuando un nombre declarado no está en el CENSO, y la
   pertenencia al censo depende de `presupuesto.techo_usd`: medido, TOELY cuesta 71,83 USD al DESDE (2023-09-05), está
   en el censo con techo 500 (33 operables) y SALE del censo con techo 60 (12 operables). Bajar el techo firmado por
   debajo de unos 72 USD mataría la noche con un ValueError sin que nadie haya tocado la lista de exclusiones. Sospecha
   de operación, no de fuga.
8. Fuga de disponibilidad (mandato ampliado). TOELY es el caso vivo: la fuente dejó de servirlo y la fila firmada lo
   excluye. El parche no cambia la asimetría «emitido antes» contra «reproducible después», y R4 la vuelve ruidosa en
   vez de silenciosa, que es la dirección correcta. Queda sin cerrar quién gana si mañana el congelado se vuelve a
   congelar sin la columna TOELY: ahí el raise sí salta (medido, 3.b).

## 1. Lo verificado (comando y cifra)

1.1 Identidad del parche y encaje exacto. `sha256sum` del diff: `f164b232…`, el del encargo. `git rev-parse
HEAD:dinero/sello_dinero.py HEAD:dinero/reglas.json` en el árbol real devuelve `d1cdef8a860e90b0bb949b8e9f0944851d824862` y
`279d088491b933176927b8876e599657070f1d16`, exactamente las pre imágenes que declara el diff. `git apply --check` limpio
sobre el árbol real. `git apply --numstat`: `2 1 dinero/reglas.json`, `42 4 dinero/sello_dinero.py`, `295 0
tests/test_version_reglas_16_3.py`. En el worktree aplicado, `git hash-object` de los tres archivos devuelve las tres POST
imágenes del diff: el worktree es el post imagen exacto, sin un byte extra. MEDIDO.

1.2 Huellas tras aplicar (las de la receta, confirmadas para esa versión): `dinero/reglas.json`
`6f3715275dadc5279e3661a9fcc1dc64af799e0a140de3a7f3eff17765ab444a`, `dinero/sello_dinero.py` `f3025d86…`; con el método del
propio sellador, `S._sha256(S.__file__)` devuelve el mismo valor. MEDIDO. [Nota del orquestador: tras B1 el sellador
cambió; la huella final está en la receta.]

1.3 `estado()` sobre la base REAL en `mode=ro`, módulo de HEAD contra módulo parchado, proceso aparte cada uno. Claves de
HEAD, 13; del parche, 14. Nueva: `por_reglas_sha256`. Perdidas: ninguna. Las 13 comunes idénticas valor por valor; sha256
del subconjunto común igual en los dos: `eaf5ad7aa0f3ede51c628b117d0358b7079b7bad6047b6ca260ed4accddb7b32`. Totales: 722
filas, 22 sesiones, 12 cuentan para N, 0 intentos, 3 divergencias. Desglose nuevo:
`125a8602…` 0.2.0-PROPUESTA 18 sesiones, 9 cuentan, 594 filas, 2026-09-08 a 2026-10-02;
`b6080eee…` 0.2.0-PROPUESTA 4 sesiones, 3 cuentan, 128 filas, 2026-10-05 a 2026-10-09.
Sumas: 18+4 = 22, 9+3 = 12, 594+128 = 722, iguales a los totales. 594 = 18 por 33 y 128 = 4 por 32, consistente con
la salida de TOELY. MEDIDO.

1.4 Filas, HEAD contra parche, sobre bases TEMPORALES construidas con el insumo REAL del 9-oct. Cuatro escenarios:
(i) timing OK a `2026-10-10T03:30:04Z`: `sellada`, 32 filas en los dos; 36 columnas idénticas; filas idénticas campo por
campo quitando reloj, huellas, versión e id; el conjunto de `motivo` distintos es idéntico. (ii) evidencia
`.no_verificable` (congelada 13:43 NY, sellada 2 s después): `intento_no_verificable`, 32 filas en la tabla de intentos y
0 en `sellos_dinero` en los dos; la ÚNICA columna que difiere es `motivo`; la nota cita `2026-10-09T17:43:01+00:00`, el
reloj de congelar, NO el del sello (`17:43:03`): F2 bien resuelta en este camino. Segundo disparo con el mismo insumo:
`ya_intentada` en los dos. Sello bueno de las 23:30 después del intento: `sellada`, 32 filas, idénticas a HEAD. (iii)
evidencia canónica con timing roto: `rechazado_evidencia_canonica` en los dos, 0 filas, 1 divergencia con el MISMO
`detalle`. (iv) segundo intento con OTRO insumo: `divergencia_registrada`, `decisiones_distintas = 2`, 0 filas, igual en
los dos: `_divergencia` compara `decision` y `acciones_regla`, nunca `motivo`. MEDIDO.

1.5 Las reglas numéricas no se mueven. `U.reglas()` es un `json.load` desnudo, sin validación de esquema, así que la clave
nueva `version_reglas_nota` no puede romper nada. sha256 del diccionario de reglas quitando sólo `version_reglas` y
`version_reglas_nota`: `f0e9d4cc0e683603f296dc703b2dc2038803d9b120a416231a6ac97b7cd2cb95`, idéntico en HEAD y parche.
`umbral_senal_pp` conservador = 1.35 y `techo_usd` = 500.0 en los dos. MEDIDO.

1.6 Tests, salida literal. Los cinco existentes más el nuevo, en el worktree parchado: `2 failed, 119 passed, 12 skipped`;
los dos rojos (`test_dinero::…sirven_lo_que_el_contrato_dice`, `…salen_del_arbitro`, `KeyError: 'gap_pct'`) NO son del
parche: sobre `wt163_ctrl` (HEAD sin el parche) los mismos dos; en el ÁRBOL REAL (con `senales.db`) `2 passed`, con
mtimes de las bases sin cambio. Causa: artefactos gitignorados ausentes en el worktree. El archivo nuevo solo: `14
passed, 1 skipped` (el de la base real). `tests/test_senal_larga.py`, que también lee `reglas.json`: `80 passed`. MEDIDO.

1.7 La API y el contrato no se mueven. `grep -c por_reglas_sha256 api/main.py api/CONTRATO.md` → 0 y 0. `/api/dinero/sellos`
arma `E0` clave por clave. `frontend/src` sin `reglas_version`, `version_reglas` ni `por_reglas`. `_CLAVES_ULTIMO` no
incluye `motivo`, así que `ultimo_intento` no expone la nota; `filas_ultimo_sello` consulta sólo `sellos_dinero`, que no
lleva nota. MEDIDO.

1.8 El export sí cambia, en el archivo correcto. `exportar_csv` sobre la base del intento escribe
`…_no_verificables.csv` con 32 filas y la nota dentro. El CSV publicado `data/backups/sello_dinero.csv` no cambia de
forma. `data/backups/sello_dinero_no_verificables.csv` todavía NO existe: el primer intento lo creará, con un `motivo`
de unos 300 caracteres por fila. MEDIDO.

1.9 Censo y R4. Congelado real hasta 2026-09-04, sha `69ca7283…`, 36 columnas, versionado en git y sin ruta de escritura
en el código. `CP.DESDE = 2023-09-05`. Censo: 33 operables, TOELY dentro. `decidir`: 32 operables, `excluidos_universo =
['TOELY']`, igual en HEAD y parche. Con el congelado sin la columna TOELY: HEAD sigue en silencio (32 operables,
`excluidos_universo = []`), el parche revienta con `ValueError … ['TOELY']`, tanto en `decidir` como en
`gate_previo_al_sello`. MEDIDO.

1.10 Estado del riel al auditar. La base real tiene tablas `divergencias_sello`, `sellos_dinero`, `sqlite_sequence`:
`intentos_no_verificables` NO EXISTE todavía. Las 722 filas son `E0.2`, con tres poblaciones de `sellador_sha256`
(`480fbdc9…` 297, `93db9b70…` 297, `cd0e70c8…` 128) y dos de `reglas_sha256`. `is-active mki-sello-dinero.service` =
`inactive`; próxima pasada `Tue 2026-10-13 00:30:00 -03`, última `Sat 2026-10-10 00:30:00 -03`, `Result=success`. La unidad
instalada no está en `systemd/` del repo (se instaló a mano) y manda `OnCalendar=Mon..Fri 23:30 America/New_York`, con
stdout y stderr a `data/sello_dinero.log`. MEDIDO.

## 2. Exigencias

### BLOQUEANTES

**B1. Arreglar el instante del camino de reserva de §81.3 (b), o declararlo con su test.** Hoy, si el meta de una evidencia
`.no_verificable` no trae bloque `timing`, la fila sella una afirmación falsa (medida en 6). Dos descargos aceptables: (a)
en ese caso citar `meta_ext["congelado_en_utc"]`, que existe en TODO meta, y decir que el veredicto lo fijó la clase de la
evidencia y no el reloj; o (b) dejarlo, declararlo en el acta y agregar al test el caso falso. Lo que NO es aceptable es
dejarlo sin test y sin acta: la fila es inmutable y la frase no se puede corregir después.

**B2. Preflight de R4 antes de aplicar, y gate después.** Antes del `git apply`, con `mode=ro` y el módulo de HEAD:
`decidir` sobre el insumo vivo tiene que devolver `excluidos_universo == ["TOELY"]` y 32 operables, y TOELY tiene que
estar en `CP.universo_operable(base, cfg, hasta=CP.DESDE)` (33). Después del `git apply`, correr `gate_previo_al_sello`
sobre el último ext y confirmar `INVARIANTE` sin ValueError. Razón: el modo de falla de R4 es una noche perdida INVISIBLE
en la base (medido en el camino de `main()`: muere en el gate, cero filas, cero intentos, cero divergencias, base ni
creada) y el vigía no mira el riel de dinero (`grep -n "dinero\|sello_dinero" mki_vigia.py`: cero resultados).

**B3. Volver a tomar la evidencia de rojos con el archivo de test FINAL, antes de commitear, y declarar cuáles son
controles.** La evidencia archivada nombraba un test que ya no existía (partido en dos) y el archivo que embarca el parche
tiene 15 tests. Cuenta correcta del archivo final sobre HEAD: 10 rojos por su propia aserción, 4 verdes de control
(`test_R4_toely_sigue_saliendo…`, `test_las_filas_de_un_sello_no_llevan_la_nota…`, `test_sin_cambio_de_esquema…`,
`test_la_api_no_sirve_el_desglose…`), 1 saltado.

### RECOMENDADAS

**R1.** Declarar el alcance de `por_reglas_sha256`: agrupa SÓLO `sellos_dinero` y SÓLO por reglas; la población de MÉTODO
es `sellador_sha256` (hoy 3 contra 2; 4 contra 3 después de aplicar). **R2.** Despegar de posiciones el test de la base
real (si una fecha anterior se sellara con reglas nuevas, el orden por `MIN(fecha_insumo)` mete la nueva en medio).
**R3.** Declarar que `motivo` de un intento pasa a ser un campo compuesto (por qué «nada» y por qué el timing está roto,
pegados con «; »), que viaja al CSV versionado de no verificables, que nace con el primer intento. **R4.** Separar las
dos causas del raise de R4: nombre fuera del UNIVERSO declarado (error de tipeo) contra nombre fuera del CENSO
(consecuencia de otra regla firmada, por ejemplo `techo_usd`). **R5.** El riel de dinero no tiene vigía (medido): o el
vigía gana un chequeo («día hábil sin fila, sin intento y sin divergencia en `sello_dinero.db`»), o la receta incorpora
la revisión de la mañana siguiente con `--estado` y `journalctl --user -u mki-sello-dinero`. **R6.** Lo que le falta a la
receta: en 3.e.

## 3. Respuestas

**3.a ¿Mueve alguna cifra publicada o alguna fila sellada?** NO, y lo verifiqué yo (1.3, 1.4). Fuera de la base: las
apariciones de `0.2.0-PROPUESTA` viven sólo en documentos de resultados ya sellados y en DECISIONES.md, que no se tocan;
en código los únicos lectores de la versión son `GEMELO/universo_por_presupuesto.py:166` y `GEMELO/m2_periodo.py:173`, que
la imprimen en artefactos que se regeneran a mano. Zona ciega: si esos dos artefactos se regeneran después de aplicar,
dirán 0.3.0-PROPUESTA con números idénticos, y nada avisa de la diferencia.

**3.b ¿Puede reventar R4 en producción sin que nadie edite reglas.json?** Hoy NO. El censo es fijo: el congelado está
versionado y nada lo escribe; `universo_operable(hasta, cfg, hasta=CP.DESDE)` decide con pasado congelado. Con el congelado
y el cfg reales el censo es 33 y TOELY está dentro, así que el raise NO puede saltar la noche del 13-oct ni ninguna otra
con el árbol como está. Si saltara (nombre mal escrito; techo bajo ~72 USD; recongelar sin TOELY): muere en el gate, la
base ni se crea, cero filas, cero intentos, cero divergencias, y el único rastro es el traceback en
`data/sello_dinero.log` más el estado de la unidad. La evidencia canónica ya quedó escrita antes del gate; un reintento la
reescribe. De ahí B2 y R4.

**3.c ¿La nota puede cambiar algo?** No cambia la decisión, ni su huella, ni el gate, ni la idempotencia, ni la
divergencia (sha de las 40 huellas con sus motivos idéntico; `ya_intentada` con el mismo insumo; `decisiones_distintas =
2` igual en los dos). CSV: el publicado no cambia; la nota aparece en `…_no_verificables.csv`. Sobre el instante: con
bloque `timing` el instante es el CORRECTO (el reloj de congelar); sin bloque `timing` el instante era el del SELLO y era
INCORRECTO en principio (6, B1). Dato que acota el daño: toda fila que llega a `intentos_no_verificables` tiene
`evidencia_no_verificable = True` (las ramas con evidencia canónica y timing roto retornan antes con cero filas), así que
el camino «reloj del sello» es código muerto en producción y el camino de reserva sólo se activa si el meta no trae
`timing`; `congelar_extension` SIEMPRE lo escribe cuando el timing está roto, y `--sin-red` sólo levanta nombres canónicos:
hoy el camino de reserva no es alcanzable por `main()`. En `rechazado_evidencia_canonica` la nota no interviene.

**3.d Secuencia y choque con E0.3.** No hay choque: las pre imágenes del diff SON los blobs de HEAD `ad4b829`, que ya
contiene el camino T. Los hunks caen en `decidir`, en `sellar` (tras el retorno de `rechazado_insumo_no_persistido` y en
el `INSERT`) y en `estado()`; ninguno toca `VERSION_SELLO`, `evaluar_timing`, `congelar_extension`, los `_cita_en` ni las
ramas de E0.3. Tests existentes que fijen literales de `reglas_sha256` o `version_reglas`: NINGUNO.

**3.e Qué le falta a la receta.** (1) Fijar la PRE imagen: `git rev-parse HEAD:dinero/sello_dinero.py` =
`d1cdef8a860e90b0bb949b8e9f0944851d824862` y `HEAD:dinero/reglas.json` = `279d088491b933176927b8876e599657070f1d16`, con
`git status --porcelain dinero/` vacío. (2) `sha256sum` del diff antes de aplicar y `git apply --numstat` (3 archivos).
(3) El preflight y el postflight de B2. (4) La reversa escrita: `git apply -R` del MISMO archivo si la suite da un rojo
que no sea de entorno, y qué se pierde (la noche siguiente). (5) `pgrep -f "dinero.sello_dinero"` además de `is-active`:
una corrida manual no aparece en `is-active` del oneshot. (6) El número del contador, leído ANTES de aplicar (hoy 12; la
noche del 13-oct lo deja en 13 si cuenta; el primer sello con el parche debería dejarlo en 14). (7) Declarar que aplicar
crea una CUARTA población de `sellador_sha256` mientras `por_reglas_sha256` muestra TRES. (8) Volver a correr la suite
DESPUÉS de la ventana 17:50 a 20:30 y dejar el `./mki auditoria` en el mismo bloque; sin `SKIP_TESTS=1`. (9) B3. (10) La
verificación de la mañana siguiente, con la consulta exacta en `mode=ro`. (11) Las dos horas con `date`, antes y después
del `git apply`.

## 4. Zonas ciegas

Z1. La suite completa con el parche NO se corrió en el árbol real, por diseño. Z2. E0.3 todavía no selló nada real: la
tabla `intentos_no_verificables` NO EXISTE en la base real; el punto 3 del parche toca el camino que nunca corrió contra la
base real (medido con bases temporales construidas con el insumo real del 9-oct). Z3. Fuga de sellado, sin resolver y sin
empeorar: ninguna columna registra cuándo la fila se hizo VISIBLE. Z4. Fuga de revisión silenciosa: los cierres son
ajustados por yfinance y no son point in time; las huellas hacen reproducible el INSUMO, no la realidad de aquel día. Z5.
Fuga de disponibilidad: si el congelado se vuelve a congelar sin TOELY, con el parche la noche muere; quién gana es
decisión firmada de Nicolás. Z6. Fuga de calendario, heredada: no reaudité `available_at` ni `apertura_objetivo_utc`; el
parche los deja idénticos a HEAD. Z7. Fuga por el analista: la elección de reventar contra el CENSO y no contra el
UNIVERSO la hizo alguien que ya sabe que TOELY es el único nombre excluido hoy. Z8. No audité el riel de medición ni
`motor.py`; no corrí `tests/test_motor.py` en esta tanda (la receta sí lo exige). Z9. Mi propia corrida tuvo un rojo por
la razón equivocada (`FileNotFoundError` al mover el test de carpeta); lo declaro porque es el modo de falla que B3 pide
cerrar.

## 5. Resumen en una línea

Sin fuga demostrada y sin una cifra publicada movida (722 filas, 22 sesiones, 12 que cuentan, claves anteriores de
`estado()` idénticas con sha `eaf5ad7a…`, gate `INVARIANTE` con 2 y 6 cortes, 40 huellas idénticas y 14 passed más 1
skipped en el test nuevo), el parche es APLICABLE con tres exigencias bloqueantes: arreglar o declarar con test el
instante del camino de reserva de §81.3 (b), que hoy puede sellar una frase falsa en un campo inmutable; hacer el
preflight de R4 porque su modo de falla es una noche perdida invisible en una base que ningún vigía mira; y volver a
tomar los rojos sobre HEAD con el archivo de test final, porque el archivado es de una versión de 14 tests y el parche
embarca 15.
