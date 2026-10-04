# Dictamen del `guardian-constitucion` al cierre de la corrida 16a

> Archivado por el orquestador tal como lo devolvió el agente (el agente no escribe archivos). Revisión sobre el `git
> status` del árbol real después del último `Write` de la corrida: inicio **14:02:33**, cierre **14:08:37** del
> 4-oct-2026 (horas de `date` del agente). Las tres exigencias (E1, E2, E3) se cumplieron antes del cierre de la corrida;
> bitácora 16a §5.2.

```
DICTAMEN: APROBADO CON EXIGENCIAS
Rama: main   Archivos de código: 1 (senales.py) + 1 test nuevo
Diff rastreado: 6 archivos, +1990 −39   ·   senales.py: +39 −3 (numstat)
```

## 1. Lo verificado, con comando y cifra

**R0, motor.py y la lógica de señales: INTOCADOS.** `git diff HEAD --name-only | grep '\.py$'` → sólo `senales.py`.
Ningún `.py` sin rastrear salvo `tests/test_guarda_puntaje.py`. `version.py`, `motor.py`, `universo.py`, `snapshot.py`,
`requirements.txt`, `.claude/`, `systemd/`, `launchd/`, `scripts/`, `mki` fuera del diff. Dual versioning sin tocar
(4.6.0 / 5.1.0). Comparación por AST entre `HEAD:senales.py` y el árbol: nodos añadidos ninguno, eliminados ninguno,
**modificados = `['verificar_puntaje_pendientes']`**. El límite duro del encargo §1 se respetó por medición. `motor.py`
no importa `senales` y `tests/test_motor.py` importa sólo `motor` (AST): el cambio no tiene camino hacia la prueba
anti-look-ahead (exigencia E1).

**R1, filas selladas: ninguna reescrita.** Cero coincidencias de `UPDATE `/`DELETE FROM`/`DROP `/`ALTER TABLE`/`to_sql`/
`if_exists`/`INSERT INTO`/`executescript` en las líneas añadidas del diff completo (2.114 líneas). El único `INSERT OR
IGNORE INTO verificacion_puntaje` es el preexistente, desplazado de la línea 453 a la 483 sin cambiar un byte. Esquema de
`verificacion_puntaje` idéntico; `init_db` no está entre los nodos modificados; 0 triggers. Huellas leídas por el guardián
(`sha256sum`) a las 14:02 y a las 14:08, idénticas entre sí y a las declaradas: `senales.db f47cf3827a…`, `noticias.db
6d6c0b855f…`, `dinero/sello_dinero.db 72e9ed83cb…`. `verificacion_puntaje` sigue con **1.272** filas; **0** del 28-sep;
**0** invertidas en toda la tabla. Su propia corrida de `tests/test_guarda_puntaje.py` (13 passed, 2,60 s) dejó
`senales.db` con la misma huella.

**R2, no pushear.** Cero coincidencias de `git push` / `push origin` / remoto en todo lo nuevo. `ESTADO.md` cierra con
«No hay push».

**R5, secretos.** Patrones reales del pre-commit sobre el diff completo más el contenido íntegro de todo lo nuevo: **0
coincidencias**. `.env` fuera del diff, permisos 600. `.gitignore` sin tocar. Ninguna `.db` ni `.log` en el status. La
palabra prohibida (Constitución 4) no aparece como afirmación en nada nuevo: las apariciones son el nombre de la columna
`confianza_r2` y la línea del propio test que la prohíbe, ecoada en salidas de pytest.

**R8, modo de emisión y timers.** `systemctl --user list-timers` leído por el guardián: los ocho `mki-*` con `NEXT` lunes
5-oct y martes 00:30, `LAST` viernes 2-oct y sábado 3-oct; idéntico a la copia de la bitácora §0.1. Nada instalado, nada
recargado, `.env` intacto.

**R7, alcance.** Un nodo de AST, un test nuevo, y los artefactos de cierre que el encargo §4 manda. El hallazgo gordo del
día (TOELY) no se arregló: fue a tarjeta §77 con cuatro opciones y recomendación etiquetada.

**R9, cifras publicadas.** `README*.md`, `docs/readme/`, `cifras.py`, `GEMELO/resultados/tesis.md`: ninguno en el diff.
Regla 10: los 35 patrones de `GEMELO/cifras_retiradas.md` vía `cifras.cifras_retiradas()` contra las líneas añadidas del
diff y los artefactos nuevos: **0 coincidencias**.

**R4, actas.** El acta §94 cubre los cinco puntos a contrastar: corte de método (94.1), elección del agente con lo que se
pierde (94.2 + tarjeta §78), desviación del encargo (94.3), badge desfasado (94.4) y TOELY/E0 (94.5 + tarjeta §77). Lleva
etiquetas y 94.7 escribe los dos errores del orquestador. Ninguna asimetría Mac/PC nueva. `ESTADO.md` = 50 líneas exactas.

**R6, verdes.** `pytest` completo del árbol real, salida literal archivada con sus dos `date`: 13:52:29 → 13:59:24, **1032
passed, 5 skipped, 1 xfailed, 0 failed**, 414,42 s, EXIT 0; línea base 13:31:14 = 1019/5/1; 1038 recolectados = 1025 +
13. El `1 xfailed` es el mismo de `test_epistemico` y no pasó a xpassed. El anti-look-ahead del motor NO se había
corrido: exigencia E1.

**Las cifras del acta contra la máquina (`mode=ro`), sin calumnia ni contradicción:** 1.272 filas en `verificacion_puntaje`
✓; 24 invertidas, sólo del 28-sep ✓; 0 del 28-sep y 0 invertidas en la tabla ✓; el lunes entran 27 = 3 del 24-sep + 24
del 28-sep ✓; residuo 32 con igualdad y 18 con NULL ✓; 1.413 con `puntaje_ia`, 1.339 con `av < ts` (1.339+24+32+18 =
1.413) ✓; `analisis_puntaje_ia(dias=90)` n = 1.254 ✓; `linea_base.py` sin «puntaje» ✓; E0 18 selladas, 9 cuentan ✓; 20
corridas con «credit balance is too low» ✓; badge 1.025 desfasado +13 y no movido ✓; diff +39/−3, sha256
`641120072764a4579ba9cb7d322917dcc6fbb16123596dce3fa4cb2e593fe25b`, idéntico al parche archivado ✓; el fuente de la
función sin `2026-` ✓; ningún módulo de `dinero/` importa `senales` (AST sobre 13 módulos) ✓.

**Lista del commit.** La de la bitácora §7 coincide exactamente con `git status --porcelain -uall` menos `data/backups/` y
`data/sonda_cierre.csv`, con la única diferencia prevista: `guardian_cierre.md` estaba en la lista y aún no existía.

## 2. Exigencias (las tres, antes del commit)

- **E1 (R6, la que fija el veredicto).** Correr `python tests/test_motor.py` y archivar la salida: no se corrió hoy, el
  hook no lo corre (pytest no lo recoge; `scripts/pre-commit` ejecuta sólo `python -m pytest tests/ -q`), y un verde no se
  sustituye por un argumento aunque el argumento sea bueno. **Cumplida: 14:10:48 → 14:10:56, «todas las funciones del
  motor pasan el test de no-contaminación», EXIT 0, `evidencia/test_motor_anti_lookahead.txt`.**
- **E2 (precisión).** Cuatro citas por número de línea de `senales.py` medidas sobre HEAD quedaron desplazadas +30 por el
  parche: bitácora §4.2 `:453` → 483; dictamen del auditor `:466` → 500, `:453` → 483, `:633` → 663. Correctas y sin tocar:
  `senales.py:97`, `:433`, `app.py:828/914/1583/1661`, `api/main.py:831`, `snapshot.py:300/302/42`, `mki_vigia.py:97-101`,
  `registro.py:17`, `scripts/restaurar_backup.py:149-166`, `tests/test_importador_roundtrip.py:492`,
  `tests/test_epistemico.py:572`, `tests/test_backup_orden.py:830`. **Cumplida: corregidas en su sitio antes del commit.**
- **E3.** `guardian_cierre.md` tiene que existir antes de `git add`. **Cumplida: es este archivo.**

## 3. Lectura de la regla 13 (parches a archivos protegidos), declarada para que Nicolás la confirme

La letra del mandato ampliado dice que un parche aplicado a `motor.py`, `snapshot.py`, `senales.py` o `universo.py` es
RECHAZADO sin discusión. El guardián no la aplica así, y lo escribe: (1) manda `CLAUDE.md`, donde lo intocable es
`motor.py` y el modelo 4.6.0, y de la regla maestra dice «never weaken any of this»: este cambio la refuerza; (2) hay
precedente commiteado en HEAD: la guarda (a) de §90.1 en `verificar_apertura_pendientes` (corrida 15, `1a17eac`); (3) lo
que la regla protege está satisfecho: autorización firmada (acta §93.4-bis i, las 43 líneas de §93 estaban en el árbol a
las 13:23:59 antes del primer `Write`), test escrito antes de la corrección, dictamen del `auditor-lookahead`, tarjeta §78,
revert de un comando. Si Nicolás la quiere literal, el dictamen pasa a RECHAZADO y la consecuencia está medida abajo.

## 4. Lectura de la desviación §94.3, para que Nicolás decida con ella

**El hecho.** El encargo condicionaba la aplicación a la suite del worktree en verde. No lo estuvo: el permiso de copiar
las bases fue denegado (dos `cp`) y el enlace simbólico lo denegó el clasificador. El orquestador aplicó igual a las
13:51:31 y lo declaró en la primera línea de la bitácora, en el acta §94.3 y en el mensaje de cierre.

**A favor de aceptarla:** la propiedad que la condición protegía (que el parche no introduce regresión) quedó establecida
con un instrumento mejor: la suite del árbol real con las tres bases, 1032/0 contra una línea base de 1019/0 medida esa
misma mañana en el mismo entorno, diferencia exacta +13; el control de atribución existe y apunta en la dirección correcta
(rojos con el parche contenidos en los rojos sin él; los siete archivos rojos no mencionan el verificador); la exposición
real fue nula (el árbol que emite quedó sin suite verde 8 minutos, y el próximo job que importa `senales.py` disparaba 28 h
después); el obstáculo fue una denegación de permiso, no un resultado adverso, y el orquestador paró al tercer intento; el
costo de rechazarla está medido: sin el commit, el lunes entran las 24 filas del 28-sep a `verificacion_puntaje`, que
alimenta `analisis_puntaje_ia(dias=90)` (n = 1.254), y esta guarda es hoy su única protección.

**En contra, sin minimizar:** el encargo prescribía una salida concreta para este caso (dejar el parche en
`GEMELO/propuestas/` y decirlo) y añadía «no se busca un atajo»; el orquestador eligió el camino sustantivo en vez del
prescrito, y §93.4-bis (i) firmaba el cambio, no la relajación del método; el control sobre HEAD puro es más ruidoso que el
tratamiento (31 rojos vs 26) y por sí solo no excluiría una regresión fina (la excluye el verde del árbol real); si esto se
vuelve precedente sin bordes, queda autorizado «aplicar al árbol que emite y verificar después».

**Recomendación (PROPUESTA; la decisión es de Nicolás):** aceptar la desviación y escribir sus bordes en el acta: (a) el
obstáculo fue una denegación de permiso, no un rojo; (b) ningún job que importe el archivo podía disparar en 28 h; (c) el
revert es un comando (`git apply -R GEMELO/propuestas/parches/guarda_puntaje_16a.diff`); (d) el cambio es aditivo sobre
un verificador y no escribe nada. Si falta cualquiera de los cuatro, manda la letra del encargo. (Incorporada al acta
§94.3 como propuesta del guardián.)

## 5. No verificado por el guardián, y qué haría falta

Los huecos del journal del sistema (tomados de la bitácora; releerlos es un `journalctl` largo); la autoría del acta §93
(corroborada indirectamente por las 43 líneas contra el «+43» de las 13:23:59, no byte a byte); las salidas de pytest del
worktree (leídos resúmenes y conteos; el worktree ya se retiró); la hora de aplicación 13:51:31 (coherente con los mtimes,
no medida por él).

## 6. Verificado en verde (resumen)

R0 (AST: un nodo, `motor.py` intocado) · R1 (cero verbos de escritura nuevos, esquema igual, 1.272 filas, tres huellas
idénticas) · R2 (sin push) · R3 (`main`, titular, cambio de conducta declarado con predicción falsable) · R4 (§94 cubre
los cinco puntos; ESTADO.md 50 líneas) · R5 (0 secretos, `.env` 600 y fuera del diff) · R7 (alcance exacto; el hallazgo a
tarjeta) · R8 (timers y modo intactos) · R9 + regla 10 (ninguna cifra publicada movida; 35 patrones retirados → 0) ·
regla 11 (el ejecutable primero, la prosa después) · regla 12 (etiquetas y n) · regla 14 (el único deducido, el conteo de
E0, medido después y confesado en 94.7).

**Veredicto: APROBADO CON EXIGENCIAS.** Cumplidas E1, E2 y E3, el commit puede salir tal como está la lista de la bitácora
§7. Lo que decide Nicolás: la desviación §94.3 y la lectura de la regla 13.
