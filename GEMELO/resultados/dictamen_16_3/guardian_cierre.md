# Dictamen del `guardian-constitucion` sobre el cierre de la corrida 16-3

> Archivado por el orquestador tal como lo devolvió el agente (el agente no escribe archivos), con una sola edición
> declarada: las tres citas a `DECISIONES.md` por número de línea se reemplazaron por su sección (§104, §102.1), porque
> ese es exactamente el defecto que su B1 señala y `tests/test_epistemico.py` las habría cazado al archivarlo. Leído
> `date` al empezar: **2026-10-11 21:24:08 -03**; al terminar: **21:59:45 -03**. Árbol real, HEAD `ad4b829`, rama `main`,
> sin commitear. No escribió en ningún archivo ni base; las tres bases sólo en `mode=ro`; `venv/bin/python`. **Cómo se
> atendieron las dos bloqueantes y las siete de registro: bitácora 16-3 §8.**

## VEREDICTO

**APROBADO CON EXIGENCIAS.** Dos bloqueantes, siete de registro.

Rama `main`. Archivos: 27 modificados y 29 nuevos fuera de `data/` (56 en total; `git status --porcelain` muestra 40
entradas porque `GEMELO/resultados/dictamen_16_3/` cuenta como una y son 20 archivos). Líneas: +995 −131 en los
modificados fuera de `data/` (+5167 −131 contando `data/sonda_cierre.csv`, que aporta +4140) y 2116 líneas en los
archivos nuevos fuera de `data/` y del dictamen.

**Ninguna regla dura está rota.** No hay un solo hallazgo de clase RECHAZO: `motor.py`, `senales.py`, `snapshot.py`,
`universo.py` y el vigía son byte a byte HEAD; ninguna fila sellada se reescribe; no hay escritura a la base en el
camino publicado (al contrario, se retira); no hay empuje al remoto ni commit ni `pull`; no hay secreto; no se toca el
modo de emisión, `.env` ni los timers; los doce bloques de la ventana sellada no se mueven. Lo que impide el APROBADO
limpio es R6: **la suite no está en verde sobre el estado final del árbol**, y la causa está dentro de la corrida.

## EXIGENCIAS BLOQUEANTES

### B1. R6. Hay un rojo en el árbol real, nacido después de la suite de las 21:09:42, y el hook rechazará el commit

MEDIDO (21:36:32 a 21:41:21), sobre diecisiete archivos de test que leen documentos:

```
→ 1 failed, 418 passed, 1 skipped, 1 xfailed en 287,75 s, EXIT 1
FAILED tests/test_epistemico.py::test_ninguna_cita_por_numero_de_linea_a_decisiones_quedo_desplazada
  GEMELO/resultados/bitacora_16_3.md:428  §2 vive en (1109, 1166), la cita dice 10110-10110
  GEMELO/resultados/dictamen_16_3/curador_readme.md:83  §82 vive en (8660, 8667), la cita dice 10069-10069
```

Las dos citas son **factualmente correctas** (la primera apunta a la cabecera del acta §104 y la segunda al punto 102.1,
verificado con `sed`). El rojo es un falso positivo de ligadura: `detectar_citas_de_linea_desplazadas`
(`tests/test_epistemico.py:662`) toma con `_RE_SECCION_EN_LINEA.search(linea)` el **primer** `§N` de la línea entera, y en
las dos líneas ese primer `§` es otro (`(2) §2 decía…` en la bitácora, `§82 (17 de 56 días…)` en el dictamen del curador).
Falso positivo o no, **el test está rojo** y el hook pre-commit corre la suite: el commit de las 50 rutas será rechazado
tal como está el árbol.

Por qué nadie lo vio: el estado que la corrida declara seguro («después de esa suite sólo cambiaron documentos y la
plantilla del README») es cierto en cuanto al tipo de archivo y **falso en cuanto a la consecuencia**, porque la suite
también juzga documentos. MEDIDO por mtime: ningún `.py`, `.tsx` ni `.json` cambió después de las 21:09:42; sí cambiaron
ocho `.md` más `curador_readme.md` a las 21:19:48. Y el mapeo de quién los lee (`grep -rln` sobre `tests/`) da mucho más
que los tres archivos re-corridos: `api/CONTRATO.md` lo leen `test_api.py` y `test_b2_intentos_visibles_16_2.py`;
`espera_firma.md` lo lee `test_backup_orden.py`; `DECISIONES.md` lo leen once archivos de test, entre ellos el que se
cayó. Es exactamente el error que la memoria del proyecto «Citas por número de línea en DECISIONES.md» describe.

**Qué exijo antes del commit:** (1) citar por sección en la bitácora (`§104`) y en `curador_readme.md` (`§102.1`), o aislar
la cita en una línea sin otro `§`; dejar `curador_readme.md` fuera del commit no quita el rojo, porque el detector barre
el disco. (2) Volver a correr: los 35 tests no bastan, y el conjunto de 17 archivos que corrí tampoco es garantía
suficiente; sobre el estado final exijo la **suite completa una vez más** más `venv/bin/python tests/test_motor.py`, y
que el número nuevo quede en la bitácora §6 con su hora. La regla general: **un documento tocado después de la suite
exige re-correr los tests que lo leen, no los que uno recuerda**, y el mapeo se saca con `grep`, no de memoria.

Lo verificado en verde: `test_fuente_unica_16_3.py`, `test_higiene_bases_16_3.py`, `test_integridad_no_verificable_16_3.py`,
`test_fallback_dashboard_16_3.py`, `test_reporte.py`, `test_frescura.py`, `test_segundo_sello.py`,
`test_importador_roundtrip.py`, `test_restaurar_backup.py` → **139 passed, EXIT 0** (21:43:44 a 21:43:56).
`tests/test_motor.py` → las seis funciones idénticas con y sin datos futuros en las tres fechas, EXIT 0.
`tsc --noEmit -p tsconfig.app.json` → **EXIT 0**.

### B2. R4 y R7. La lista de archivos para el commit está incompleta: 50 rutas declaradas contra 56 en el disco

MEDIDO comparando la lista de la bitácora §9 con el disco (`git status --porcelain`, expandiendo el directorio): en disco
y no en la lista, 6 (`dictamen_16_3/curador_readme.md`, `evidencia/aplicacion.txt`, `evidencia/aplicar_16_3.sh`,
`evidencia/badges_readme_salida.txt`, `evidencia/badges_y_readme.sh`, `evidencia/suite_arbol_real_despues.txt`); en la
lista y no en disco, ninguno. Dos de los seis no son opcionales: `curador_readme.md` es el tercer dictamen y el acta
§104.2 B lo cita por ruta, y `suite_arbol_real_despues.txt` es la evidencia de la B2 del auditor. Sumado mi propio
dictamen, la lista queda en **57 rutas**; la frase «(50 rutas; `git status --short` …)» hay que corregirla, porque
`--short` colapsa el directorio del dictamen en una línea. Revisados los dos guiones de evidencia por R2: el único
comando de git es `git diff --stat …`, de sólo lectura; sin empuje al remoto, sin `commit`, sin `rm`, sin `systemctl`.

## EXIGENCIAS DE REGISTRO

**R1.** `data/sonda_cierre.csv` no lo commitea el backup del lunes, contra lo que decía la bitácora §9: `mki_backup.py:208`
y `:216` llevan pathspec `-- data/backups`, y `git log -- data/sonda_cierre.csv` muestra que lo commitearon las corridas
15 (`1a17eac`) y 14 (`fa7b5ba`), nunca el backup. Son +4140 líneas que se quedan en el limbo si nadie decide: dentro del
commit de la 16-3, o declarado y fuera. **R2.** Las cuentas de nodos de la bitácora §3 estaban viejas:
`test_fuente_unica_16_3.py` 32 (decía 26), `test_higiene_bases_16_3.py` 14 (decía 12), `test_integridad_…` 4,
`test_fallback_…` 6; la suma 56 cruza con el `+56` contra la apertura y con `1216 − 1160`. **R3.** La frase de estado
mental que el curador hizo borrar de la bitácora sobrevivía en la tarjeta §82 («se firmó por su mérito antes de
mirarlo»): misma redacción que la bitácora. **R4.** La consulta de §7.7 se lee como medición presente y hoy devuelve
cero filas (esas filas están `pendiente`); el hecho de fondo es verdadero sin el filtro de estado. **R5.** Regla 10,
inventario: dos cifras retiradas preexistentes en `.py` que el diff no toca (`backtest/linea_base.py`, comentario
histórico del `p` sin deduplicar; `tests/test_epistemico.py`, fixtures que prueban al árbitro); lo preexistente que el
diff no toca se inventaría y no rechaza (R7 prohíbe arreglarlo de paso). Causa estructural: `cifras.DOCUMENTOS_PUBLICADOS`
son cinco `.md`, así que el árbitro de la suite nunca mira un `.py` ni `backtest/`; ensancha el hallazgo 104.5 (5): una
clase entera de archivos está fuera. Va a tarjeta, no a esta tanda; confirmar o cambiar esa lectura es de Nicolás.
**R6.** El acta declaraba la cobertura por dictamen para A, B, C y F, y no en las viñetas de D y E (Z7 del auditor).
**R7.** Acoplamiento nuevo declarado y sin guarda: un `available_at` con ISO malformado en cualquier fila mata el reporte,
la API y la vista (`lb._instante_utc`); aceptado declarado porque arreglarlo toca camino de sellado con firma.

## LO VERIFICADO EN VERDE, CON COMANDO Y CIFRA

**R0.** `git diff motor.py` vacío. sha256 contra `git show HEAD:<f>`: `motor.py` `b3b75ffe…`, `senales.py` `494a8a4d…`,
`snapshot.py` `3cbbecaa…`, `universo.py` `df194e5e…`, `mki_vigia.py` `4f050974…`, IGUALES. Los catorce módulos del camino
de sellado y la plataforma, intactos. `version.py` en 4.6.0 y 5.1.0. `tests/test_motor.py` EXIT 0.

**R1.** Huellas al abrir (21:24) y al cerrar (21:59): `senales.db` `98a048de…`, `noticias.db` `1829b61b…`,
`dinero/sello_dinero.db` `2a016c52…`, idénticas a las de la bitácora §0.2 (19:30:08). Barrido de sentencias de
modificación, borrado, DDL, `if_exists`, `to_sql(`, `INSERT INTO` sobre las líneas agregadas del diff y los cinco archivos
nuevos de `tests/`: cero. El camino publicado deja de correr DDL sobre la base sellada (`linea_base._conexion_ro` abre
`mode=ro`, idéntica en código a `backtest.datos._conexion_ro`). Ningún cambio de esquema. Las 8 filas del 28-sep siguen
en `verificacion_apertura` (8) y `verificada`.

**R2.** Cero ocurrencias del empuje al remoto y de `git pull` en 17.691 líneas (diff, archivos nuevos, dictámenes,
evidencia). Sin `git commit` en ningún guion. `git log --oneline -3` en `ad4b829`; `git reflog -3` sin nada después.
Índice limpio.

**R3.** `main` en el árbol real y como base de los cuatro worktrees (detached en `ad4b829`). El cambio de comportamiento
del reporte del lunes está declarado (§104, bitácora §6, §7, §9). Titular único: no hay segundo emisor.

**R4.** El acta §104 cubre los seis bloques, dice la letra contra el hecho (B1 del auditor A), no firma nada; las ocho
tarjetas §82 a §89 cierran con «No se eligió nada» y cubren el encargo §7.4 (§83 = R6 + §80.5, §84 = R3, §85 = R7, §86 =
S2, §87 = F4, §88 = candado §81.5 b, §89 = el parche). Fusión §93.12 aplicada con textos conservados; §80 y §81
FIRMADAS. `ESTADO.md` 50 líneas.

**R5.** Barrido de secretos sobre las líneas agregadas: cero. Ningún `.db`, `.log`, `.env`, `.sqlite` en el conjunto.
`.env` 600 e ignorado; las tres bases ignoradas. `.claude/` sin cambios. `git diff | grep -i confianza`: cero.

**R8.** `git status --short` de `dinero/`, `corredor/`, `systemd/`, `launchd/`, `scripts/`, `.claude/`, `.env`: vacío.
Los ocho timers `mki-*` con los NEXT de la bitácora §0.1. Nada instalado, modificado, reiniciado ni recargado. El
sellador real no corrió.

**R9.** Los doce bloques no se tocan (badges de ventana sellada y larga idénticos en el diff). Los dos badges que §90.4
manda releer, con los tres valores juntos: 1216, 5.1.0, 2026-10-11; `generar_readme.py --verificar` coincide. Cifras del
acta, de la bitácora §2 y del contrato contra `evidencia/medicion_antes.txt` y `medicion_despues.txt`: coinciden en todo.
Consulta de §7 sobre la base real: 141 por la definición vieja y 133 por la fuente única; `lb.metricas_apertura(dias=30)`
ya da n = 133 porque `date('now')` pasó a 2026-10-12 UTC, como la corrida anticipó; `verificacion_puntaje` con filas
invertidas: 0. Árbitro de cifras retiradas: vacío en los ocho documentos. `tesis.md` con las dos correcciones y sus marcas.
El parche de `dinero/`: sha256 `5acdb3e2…`, 428 líneas, `apply --check` EXIT 0, numstat `2 1 / 56 4 / 304 0`, 15 nodos.
R9 en `app.py`, la tarjeta de `/sellos` (`tsc` EXIT 0), `hay_filas`, la guarda del conftest y el test de integridad:
verificados por lectura y ejecución.

**Hechos de entorno.** La denegación del `cp` y el régimen §95.5 declarados y archivados; el `rm` denegado no se rodeó y
los dos archivos siguen sólo en el worktree; el árbol real no los tiene (`grep -c no_verificable` → 0 en las dos
carpetas); después de mis nueve archivos de pytest sobre el árbol real no apareció ningún respaldo nuevo (contraprueba
viva de la guarda). Los cuatro worktrees siguen en `git worktree list`; `wt163` va a necesitar `--force` por los
cambios sin commitear.

## Mi lectura de la regla 13

**No se activa.** (1) Parche aplicado a archivo protegido: no hay (`senales.py`, `motor.py`, `snapshot.py`, `universo.py`
byte a byte HEAD; la corrida construyó la capa de medición al lado y migró a los consumidores; las seis funciones viejas
quedan sin consumidor y no se borran, con un test por AST). (2) Parche no aplicado contra archivo protegido: tampoco
(`version_reglas_16_3.diff` toca `dinero/`, que no está en la lista; aun así cumple las dos condiciones de un parche
legítimo: test que lo cubre y tarjeta §89 con receta, sha256 y predicción).

## Mi lectura de la frontera

Acepto el reparto de la Z7 del auditor A. **Bloque D** (lo que no es frontera): en verde, 18 nodos corridos; la guarda
nació de un error propio de la corrida y el barrido cazó su propio archivo antes que a nadie. **Bloque E:** en verde con
el riesgo declarado donde debe estar («manda la última cabecera»), obtenido sin tocar el vigía y con el parser real del
vigía en un test. **Bloque F:** en verde, `tsc` EXIT 0 corrido por mí. **Y lo que la frontera dejó sin dueño:** ningún
auditor miró el estado del árbol posterior a las 21:09:42 (el curador dictaminó sobre las 21:01 y sus arreglos son
posteriores); ese tramo era mío y ahí estaba el rojo. Regla de la casa: **el último Write de una corrida también
necesita una suite, y la corrida no se cierra con la suite de antes del último Write.**

## Resumen operativo para el commit

No autorizado todavía; lo que falta es chico y de texto: (1) las dos citas por sección; (2) suite completa más
`test_motor.py` sobre el estado final, con el número y su hora en la bitácora §6; (3) la lista de §9 a 57 rutas con la
frase del conteo corregida; (4) decidir `data/sonda_cierre.csv`; (5) las de registro R2 a R7, ninguna bloquea. Hecho eso,
la tanda cumple la constitución: modelo en 4.6.0, motor y verificador intactos, ninguna fila sellada reescrita, nada
empujado, nada firmado, y una cifra publicada movida declarando antes cuánto, por qué, en qué dirección y contra qué
evidencia.
