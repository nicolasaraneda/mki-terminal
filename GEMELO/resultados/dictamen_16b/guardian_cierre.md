# Dictamen del `guardian-constitucion` al cierre de la corrida 16b

> Transcrito por el orquestador (Fable 5.1) a las 20:15 de Chile del domingo 4-oct-2026, texto íntegro del agente
> (abierto 19:50:47, cerrado 20:10). **Nota del orquestador, posterior al dictamen:** las cuatro exigencias (E1 a E4)
> se cumplieron entre las 20:10 y las 20:12 en su sitio: la suite de cierre figura en la bitácora §4, §7 y §8 y en el
> acta §96.3; el apartamiento del «17:50» de §95.5 está declarado con sus tres razones en §96.1, en la bitácora §5 y en
> `ESTADO.md`; el latido del journal se cita en la ventana exacta 16:20:39 → 19:18:16 (**356** líneas, medido de nuevo);
> el 28-sep de `ESTADO.md` queda atribuido al timing. El «1042 passed» de la receta §5 lleva la marca PREDICCIÓN.
> El guardián no volvió a pasar sobre estos cuatro cambios de registro.
>
> **Nota de transcripción:** el hook de cifras retiradas (patrón «0 huecos» del mapa de instrumentos, D9 del 9-sep)
> bloqueó la escritura literal; las dos menciones del guardián a «0 huecos mayores de 60 s» del latido del journal
> (otro tema) van escritas «cero huecos». Nada más cambió.

---

# Dictamen del `guardian-constitucion` al cierre de la corrida 16b

> Revisión sobre el `git status` del árbol real después del último `Write` de la corrida: inicio **19:50:47**, cierre
> **20:10** del domingo 4-oct-2026 (horas de `date` del agente, no estimadas). HEAD `f5b659e`, rama `main`.
> La suite de cierre terminó dentro de esta revisión y la leí: **no hace falta declarar vigente la de apertura**.

```
DICTAMEN: CONFORME CON OBSERVACIONES
Rama: main   HEAD f5b659e (sin mover)   Archivos de código tocados: 0
Diff rastreado: 5 archivos, +1865 −13  ·  descontando data/: 3 documentos, +104 −13
Sin seguimiento (de la corrida): 7 archivos  ·  Parche archivado, NO aplicado: 4 archivos, +201 −8
```

Ningún RECHAZO. Cuatro exigencias antes del `git add`, todas de registro y precisión; ninguna toca código.

---

## 1. Lo verificado, con comando y cifra

**R0 — `motor.py` y la lógica de señales: INTOCADOS, y con ellos todo el perímetro del punto 1 del encargo.**
`git diff HEAD --name-only | grep -E '\.py$|\.json$|\.sh$|systemd|launchd'` → **vacío**.
`git status --porcelain -uall -- dinero tests api app.py motor.py snapshot.py senales.py universo.py alertas.py noticias.py mki_vigia.py mki_backup.py README.md .env corredor systemd launchd scripts .claude` → **vacío**. `version.py` fuera del diff: modelo 4.6.0 y plataforma 5.1.0 sin mover. `dinero/sello_dinero.py` del árbol conserva `sha256 480fbdc991679f2b06340bd4609dc08b3fd8c920cc4bc5eae1d03b93a39fbeab`, que es **el mismo que llevan selladas las filas** (`sellador_sha256` distintos en la base: `93db9b70dc70`, `480fbdc99167`); `dinero/reglas.json` conserva `125a8602a684939576278093b306add6a6fa7a0157389f71a5c0029455ab9ba0`, el único `reglas_sha256` de la tabla. **El parche no está aplicado: medido, no supuesto.**

**R1 — ninguna fila sellada reescrita.** Las tres bases, antes y después de la suite de cierre, con la misma huella:
`dinero/sello_dinero.db 72e9ed83cb…` (mtime `1790998205`, 536 576 bytes — idénticos a los que midió el auditor, `1790998205.2400458` y 536576), `senales.db f47cf3827a…`, `noticias.db 6d6c0b855f…`; las tres iguales además a las del cierre de la 16a. `sellos_dinero`: **594 filas, 18 sesiones, 9 cuentan para N**, TOELY con 18 filas, 2 divergencias, cuatro triggers de inmutabilidad en pie. Cero coincidencias de `UPDATE `/`DELETE FROM`/`DROP `/`ALTER TABLE`/`to_sql(`/`if_exists`/`executescript` en las 2 922 líneas de todo lo nuevo (líneas añadidas del diff rastreado + bitácora + dictamen del auditor + el `.diff` + `ESTADO.md`). El parche sólo abre la base real en `?mode=ro` (un test, `test_las_filas_selladas_antes_del_cambio_siguen_con_toely_y_con_la_huella_vieja`); todo lo demás sella en `tmp_path`.

**R2 — nada pusheado, nada commiteado.** `git reflog -5`: el último commit es `f5b659e` del **4-oct 15:07:37**, anterior a esta corrida (primer `date` 16:20:39). `main...origin/main [ahead 4]`, exactamente los 4 de siempre (16a + tres backups), pendientes de la mano de Nicolás. Cero coincidencias de empuje remoto en todo lo nuevo. `ESTADO.md` cierra con «No hay push».

**R3 — rama y conducta.** `main`, titular, único emisor. La corrida **no cambia la conducta del árbol real**: no hay código nuevo. El cambio de conducta que el parche traería (universo del insumo de E0 de 33 a 32 desde la primera noche que lo use) está declarado con predicción falsable y consulta exacta en la bitácora §6 y en el acta §96.5.

**R5 — secretos.** Patrones reales del hook (`sk-ant-api…`, `…:AA…`) sobre las 2 922 líneas de todo lo nuevo: **0**. `.env` con permisos **600** y fuera del diff; `.gitignore` sin tocar; ninguna `.db` ni `.log` en el `status` (`git check-ignore` confirma `.env`, `senales.db`, `noticias.db`, `dinero/sello_dinero.db`).

**R8 — modo de emisión y timers.** `systemctl --user list-timers` leído por el guardián a las 19:51: los ocho `mki-*` con **NEXT** lunes 5-oct (17:50 · 18:15 · 18:25 · 18:40 · 19:00 · 20:30 · 21:05) y martes 6-oct 00:30, **LAST** viernes 2-oct y sábado 3-oct; idéntico a la copia de la bitácora §0.1. `~/.config/systemd/user/mki-*`: mtimes de 25-ago, 9-sep y 29-sep, **ninguno de hoy**. `data/sello_dinero.log`: **0** entradas de `2026-10-04`, mtime 3-oct 00:30:05. Ningún `--sellar` corrido. `.env` intacto.

**R6 — verdes.** Dos suites completas del árbol real, ambas archivadas con sus dos `date`:
- apertura (HEAD puro, antes de que existiera el `.diff`) 19:18:16 → **19:25:16**: `1032 passed, 5 skipped, 1 xfailed, 29 warnings in 419.95s`, `EXIT 0`;
- **cierre 19:50:10 → 19:57:14: `1032 passed, 5 skipped, 1 xfailed, 29 warnings in 423.89s`** (leída por el guardián; el proceso ya murió). Es la única corrida sobre **el árbol tal como se va a commitear**, con el `.diff` nuevo ya en `GEMELO/propuestas/parches/` — dato que no es decorativo: `tests/test_parche_*.py` recorren esa carpeta.
`python tests/test_motor.py` **no se corrió hoy**: este commit no toca una línea de Python, así que R6 no lo exige; la receta §5 sí lo exige después del `git apply`, y ahí es obligatorio.

**R7 — alcance.** El encargo pedía una sola cosa y la corrida hizo una sola cosa. Cero archivos de código en el árbol real, cero arreglos de paso. Los hallazgos del día no se arreglaron: V4 de §58, la sonda, `version_reglas` y la realización del sorteo fueron a la tarjeta §79 y a la corrida 16, no al diff. El límite duro «no se toca la sonda» se respetó y el motivo por el que el cambio igual no le llega está medido (lee su lista de `dinero/datos/cierres_congelados.meta.json`, 36 tickers, no importa nada de `dinero/`).

**R9 y regla 10 — cifras publicadas y retiradas.** `README*.md`, `docs/readme/`, `cifras.py`, `tesis.md`: ninguno en el diff; ninguna cifra publicada se mueve. Los **35** patrones de `GEMELO/cifras_retiradas.md` vía `cifras.cifras_retiradas()` contra las 2 922 líneas de todo lo nuevo: **0 coincidencias**. Ningún `.py` nuevo ni tocado, así que la lectura instalada de la regla 10 («introduce o toca») no tiene dónde morder, y no hay nada que inventariar.

**R4 y regla 12 — actas y etiquetas.** El acta **§96** cubre los cinco puntos que la corrida tenía que declarar, cada uno etiquetado: 96.1 HECHO (no aplicado, con el porqué), 96.2 DISEÑO, 96.3 MEDIDO (dictamen del auditor), 96.4 DECLARADO (B1, B2, B5), 96.5 PREDICCIÓN falsable, 96.6 errores del orquestador escritos por él mismo, 96.7 lo abierto. Sin firmas, como corresponde. La tarjeta **§79** de `espera_firma.md` lleva las cuatro decisiones con opciones, consecuencia, lo que se pierde y recomendación etiquetada, cierra con **«No se eligió nada»** y tiene un addendum del auditor posterior a su redacción que también cierra sin elegir. Ninguna asimetría Mac/PC nueva (no hay Mac; no hay dependencia, intérprete ni variable de entorno nueva). `ESTADO.md` = **50 líneas exactas**. La palabra prohibida por la Constitución 4: **0 apariciones** en todo lo nuevo.

**Regla 13 — parche a archivo protegido.** El `.diff` no toca `motor.py`, `snapshot.py`, `senales.py` ni `universo.py`; toca `dinero/sello_dinero.py` y `dinero/reglas.json`. Aun así cumple las dos condiciones que la regla protege: **trae sus tests dentro** (`tests/test_toely_fuera_insumo_e0.py`, 10 tests, escritos antes de la corrección, 8 rojos sobre HEAD) y **está listado en `espera_firma.md`** (§79, con la ruta exacta). Nada se aplicó a un archivo protegido.

**Regla 14 — ningún supuesto donde el encargo pedía un cómputo.** El único valor que el orquestador declaró sin medir (la realización del sorteo) lo confiesa él mismo en §96.6(2) y lo midió el auditor antes del cierre. El punto 0.4 del encargo (leer el código antes de escribir) está cumplido y sus cuatro respuestas son verificables en el código.

**Las cifras del acta contra la máquina, leídas por el guardián.** `.diff` `sha256 e8989db56742c593aa75c3ac3e6f0f25ec4a9dceaefd60bb8524938d6127d9b6` ✓ · `git apply --check` limpio sobre `f5b659e` ✓ · `git apply --numstat` = `6+0` reglas.json, `14+0` sello_dinero.py, `9+8` test_sello_dinero.py, `172+0` test nuevo = **+201 −8 en cuatro archivos** ✓ (coincide con §96.1) · **apliqué el parche sobre una copia de HEAD fuera del repo** y los dos hashes post-aplicación salen exactos: `reglas.json b6080eee4351ed433aeb5a124ec4603dcb3db3b3278b1791c40ee8a4ad0abc6c` ✓ y `sello_dinero.py cd0e70c8005143b2f6b63c62fb9e3f75b5303e083a936c98c13b86df6a8b2c25` ✓, con `version_reglas` sin mover («0.2.0-PROPUESTA») y `VERSION_SELLO = "E0.2"` ✓ (sin choque con el `E0.3` del parche T) · base real: 594 filas / 18 sesiones / 9 cuentan / 33 por sesión / 1 `reglas_sha256` / 2 `sellador_sha256` / 2 divergencias ✓ · **las 7 sesiones con TOELY como único faltante son 18-sep, 23-sep, 28-sep, 29-sep, 30-sep, 1-oct y 2-oct** ✓, y como la del 28-sep es `no_verificable_timing`, «contarían 15 de 18 y no 9» y «6 quedan donde están» reproducen exactamente (R5 del auditor, que corrige a §95.4 con fecha posterior: así se hace) · citas por línea correctas: `universo_dinero.py:178` es el `Candidato("TOELY", …)` ✓ y `sonda_cierre.py:65` es `def tickers_operables` ✓.

**La pausa de tres horas, medida por el guardián y no tomada de la bitácora.** `journalctl | grep -c "Clock change detected"` entre 16:20 y 19:20: **360 latidos, cero huecos mayores de 60 s**, primero 16:20:14 y último 19:19:44. **La máquina no se suspendió: la sesión esperó.** La causa que el acta §96 declara para el vencimiento del reloj es cierta y está verificada de forma independiente (ver la observación O4 sobre el número exacto).

---

## 2. Exigencias, antes del `git add` (cuatro, ninguna toca código)

- **E1 (R7, lista del commit — la que fija el veredicto).** `GEMELO/resultados/dictamen_16b/evidencia/suite_arbol_real_cierre.txt` **existe en el árbol y falta en la lista de la bitácora §8**. No es un detalle de prolijidad: la suite de apertura corrió a las 19:18, **antes** de que el `.diff` existiera (19:43), y la de cierre es la única que corrió sobre el árbol exacto que se va a commitear, con el parche nuevo ya en `GEMELO/propuestas/parches/` —carpeta que los `tests/test_parche_*.py` recorren—. Si no entra, queda un artefacto sin seguimiento que la corrida 16 tendrá que explicar. **Añadir esa línea a §8.** Con ella la lista queda exacta: comparada con `git status --porcelain -uall` menos `data/backups/` y `data/sonda_cierre.csv`, coincide archivo por archivo, con la única diferencia prevista de que `guardian_cierre.md` aún no existía cuando se escribió. Ni un archivo de más: `data/backups/sello_dinero.csv`, `data/backups/sello_dinero_ext/ext_2026-10-02.{csv,meta.json}` y `data/sonda_cierre.csv` son del sellador y de la sonda del 2 y 3-oct y están correctamente fuera.
- **E2 (R4/R6, registro).** La bitácora §7 remite la suite de cierre a «la línea final de este archivo» y **esa línea no lleva el número**. Medido por el guardián: **1032 passed, 5 skipped, 1 xfailed, 0 failed, 423,89 s, 19:50:10 → 19:57:14**, idéntico a la apertura. Escribirlo en §7 (y, si el acta cita suites, en §96.3, que hoy sólo cita la de apertura).
- **E3 (R4, el plazo).** **§95.5, firmada, dice literalmente que «si la 16b no queda commiteada antes de las 17:50 del 4-oct, la sesión del 5-oct se pierde igual».** El acta §96.1, la bitácora §5 y `ESTADO.md` sostienen lo contrario —que aplicar antes del lunes 23:30 NY todavía salva la sesión— y lo sostienen **con razón**, pero sin declarar que se apartan de la letra de un acta firmada. Hay que escribir el porqué, que es medible y es el siguiente: (a) **el sellador lee el árbol de trabajo, no git**, así que lo que salva la sesión es el `git apply`, y el commit es para el registro; (b) el plazo operativo real es el disparo de `mki-sello-dinero`, martes 6-oct 00:30 Chile (confirmado en `list-timers`); (c) el hook no bloquea un commit de hoy: `bash scripts/guarda_red.sh` devuelve **1 = fuera de la ventana** a las 20:07 de un domingo, porque «día hábil» es lunes a viernes. Y conviene añadir el reverso, que es una trampa operativa real: **si el commit se deja para el lunes entre 17:50 y 20:30, el hook lo rechaza.**
- **E4 (precisión; la frontera de la errata es el commit).** Dos números que no reproducen tal como están escritos, los dos inocuos en el fondo y los dos corregibles en su sitio: (i) el latido del journal, declarado como «**366** líneas cada 30 s» en la bitácora y en §96, da **356** en la ventana exacta que esas mismas líneas declaran (16:20:39 → 19:18:16) y **360** en 16:20 → 19:20; el número de 366 corresponde a una ventana más ancha que la citada. La conclusión no se mueve (cero huecos > 60 s), así que basta declarar la ventana o poner el número que le corresponde. (ii) `ESTADO.md` dice «las del 28-sep al 2-oct no cuentan (TOELY, §95.4)»: la sesión del **28-sep** está sellada `no_verificable_timing`, y su causa vinculante es el timing, no TOELY (el propio §96.3 la trata bien al contar «6 de ellas»).

*(La exigencia equivalente a la E3 de la 16a —que `guardian_cierre.md` exista antes del `git add`— la cumple este archivo.)*

---

## 3. Sobre no haber aplicado fuera del reloj: la decisión fue correcta, y por qué

El encargo puso la aplicación bajo el rótulo «**Reloj (manda sobre todo lo demás)**» con una hora absoluta (16:45) y escribió la salida alternativa completa: dejar el parche en `GEMELO/propuestas/parches/` con tests y dictamen, y decirlo en la primera línea de la bitácora. Eso es exactamente lo que hay. El precedente de §94.3 no autoriza lo contrario, lo cierra: sus cuatro bordes fijan que, **faltando cualquiera**, manda la letra, y aquí fallan dos de los cuatro.

- **Borde (a) — «el obstáculo fue una denegación de permiso, no un resultado adverso»: NO APLICA.** En la 16a el obstáculo era un permiso que no se podía obtener; aquí el obstáculo **es el plazo mismo**. Saltarlo no habría sido sortear un impedimento externo: habría sido derogar la regla que el encargo declaró soberana.
- **Borde (d) — «el cambio es aditivo sobre un verificador y no escribe nada»: FALLA.** Esto no es una guarda sobre un verificador: es el **camino de sellado**, `sello_dinero.decidir`, el que escribe las filas de E0. Es la zona donde la Constitución es más dura, no menos.
- Bordes (b) y (c) sí se cumplen (28 h hasta el disparo; `git apply -R` revierte en un comando), y por eso el parche es perfectamente aplicable **mañana, por la mano de Nicolás, con su acta**. Lo que no era aceptable era que lo decidiera el orquestador contra el reloj.

Hay además una razón sustantiva, no sólo formal: la **B4 del auditor** dice que el juez de este parche es la suite del árbol real, porque la del worktree no cubre `api/` ni `test_dinero.py`. A las 19:50 esa suite **todavía no se había corrido con el parche** —no se ha corrido nunca—. Aplicar al árbol que emite, a última hora de un domingo, un cambio al camino de sellado sin el juez que el propio auditor designó, habría sido peor que perder una noche.

**El costo está medido y declarado:** si el parche no entra antes del martes 00:30 Chile, la sesión del 5-oct sale `insumo_incompleto` por TOELY, E0 sigue en 9 de 40, y será la octava sesión que TOELY se lleva. §95.5 lo previó y §96.1 lo escribe. **El guardián no tiene reparos con la decisión; los reparos son los de la E3, sobre cómo quedó declarado el plazo que la sustituye.**

---

## 4. Sobre la receta de aplicación de la bitácora §5

**Respeta las reglas.** Commitea Nicolás; no hay un solo empuje remoto en ninguna parte; el orden es el correcto (`git apply --check` antes de `git apply`, huellas, **suite completa del árbol real**, **`tests/test_motor.py`**, `git status` para que el test nuevo no se quede fuera del commit); nombra el revert de un comando y dice qué archivos se suman al commit. El número esperado reproduce en aritmética: 1032 + 10 = **1042 passed** y 1038 + 10 = **1048 recolectados**; conviene marcarlo como **PREDICCIÓN**, que es lo que es, porque esa suite no se ha corrido nunca (regla 12).

Tres cosas que le faltan y que pido junto con la E3: que diga que **lo que salva la sesión es el `git apply` y no el commit** (el sellador lee el árbol de trabajo); que avise del **hook entre 17:50 y 20:30 del lunes**; y que recuerde que el test `test_las_filas_selladas_antes_del_cambio_siguen_con_toely_y_con_la_huella_vieja` **sólo puede estar verde con el parche aplicado** —esto último sí está escrito, y está bien escrito—.

Recomendación menor, sin rango de exigencia: los dos worktrees de la corrida siguen registrados (`git worktree list` muestra `…/scratchpad/wt16b` y `…/wt16b_head`, los dos en `f5b659e` detached, el primero con el parche aplicado en su árbol). No afectan al commit ni a nada que emita, pero cuando el scratchpad desaparezca quedará metadata muerta en `.git/worktrees`: un `git worktree prune` en algún momento de la 16.

---

## 5. Observaciones que no bloquean, anotadas para la 16

- **O1. El artefacto auditado no es el artefacto archivado.** El auditor dictaminó sobre `sha256 766afa4d…`; el `.diff` que queda es `e8989db…`, regenerado a las 19:43 para incorporar su propia exigencia **B3**. El orquestador lo declara en la cabecera del dictamen, que es lo correcto, y el delta lo leí yo línea por línea: tres líneas en el retorno de `sellar()` (`"excluidos_universo": dec.get("excluidos_universo", [])` más dos de comentario) y un `assert` en el test de reproducción. Es pura propagación al log, no cambia una decisión. Pero **el auditor no volvió a pasar sobre el artefacto final**: queda dicho.
- **O2. Pudrición del parche.** Mientras no se aplique, el `.diff` envejece contra HEAD. La carpeta ya tiene tres `.diff` viejos con su `tests/test_parche_*.py` que los vigila, y el 16b no lo tiene (tampoco lo tiene el parche T de §62). La barrida genérica ya existe propuesta y sin firmar (`GEMELO/propuestas/test_parches_en_worktree.py`), así que no pido nada nuevo: si el parche no entra antes del martes, esto pasa a ser un ítem de la 16.
- **O3. El 99,81 % de casillas del sorteo** es una enumeración determinista sobre el congelado, no una muestra: no le corresponde intervalo, y su n es derivable (40 sesiones × 32). Cumple la regla 12 tal como está.
- **O4.** La honestidad del acta sobre la **fuga por el analista** (§96.3, «el cambio mejora mecánicamente la tasa de sesiones que cuentan y se firmó sabiéndolo») y la corrección fechada a §95.4 por las sesiones del 18 y 23-sep son ejemplares. Lo anoto porque es lo que hace creíble al resto.

---

## 6. No verificado por el guardián, y qué haría falta

Las dos suites de worktree (leí las salidas archivadas y el conjunto de 26 rojos, no las volví a correr; los worktrees siguen montados si alguien quiere rehacerlo); las mediciones internas del auditor (99,81 % de casillas; 30 vs 25 compras en 40 sesiones del congelado), que exigen correr el sellador sobre la base congelada; la hora `16:20:39` del primer `date`, que tomo de la bitácora aunque el latido del journal y el nacimiento del pytest de apertura la corroboran por los dos extremos; y el contenido del encargo tal como Nicolás lo guardó a las 16:19:50 (lo leí del archivo, no comparé con el original del chat).

---

## 7. Verificado en verde (resumen)

R0 (cero `.py` tocados; perímetro completo del encargo §1 intacto, medido archivo por archivo) · R1 (tres huellas idénticas antes y después, 594/18/9, triggers en pie, cero verbos de escritura nuevos) · R2 (HEAD sin mover desde las 15:07:37, nada empujado) · R3 (`main`, titular, conducta del árbol real sin cambio) · R4 (§96 con sus siete bloques etiquetados y sin firmas; §79 sin elegir nada; `ESTADO.md` 50 líneas) · R5 (0 secretos, `.env` 600 y fuera del diff) · R6 (dos suites completas del árbol real, 1032/5/1/0 las dos, la de cierre sobre el árbol que se commitea) · R7 (una sola cosa hecha; los cuatro hallazgos a tarjeta, no al diff) · R8 (ocho timers idénticos, unidades sin mtime de hoy, ningún `--sellar`, log sin entrada del 4-oct) · R9 + regla 10 (ninguna cifra publicada movida; 35 patrones retirados → 0) · regla 11 (no aplica: no hay prosa que corrija a un ejecutable) · regla 12 (etiquetas, n y «No se eligió nada») · regla 13 (parche con tests y listado en `espera_firma.md`; ningún archivo protegido tocado) · regla 14 (el único valor declarado sin medir fue medido por el auditor y confesado en §96.6).

**Veredicto: CONFORME CON OBSERVACIONES.** Cumplidas E1, E2, E3 y E4, el commit puede salir con la lista de la bitácora §8 **más** `evidencia/suite_arbol_real_cierre.txt` y este dictamen. Lo que decide Nicolás: aplicar el parche antes del martes 00:30 Chile (tarjeta §79.1), y las otras tres decisiones de §79.
