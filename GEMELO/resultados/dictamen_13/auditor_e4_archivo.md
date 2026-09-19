# AUDITORÍA DE FUGA — E4 protege la base y no el disco (encargo 13 §3, bloque 1)

Alcance: `dinero/sello_dinero.py` (`congelar_extension`, `ultima_extension`,
`sellar`, `respaldar_extension`, `main`), `tests/test_sello_dinero.py`, y todo
`to_csv` / `open(...,"w")` / `copyfile` de `dinero/`.
Nada del repo fue modificado. Producto escrito: esta carpeta.

---

## 1. FUGAS DEMOSTRADAS

### F1 — `dinero/sello_dinero.py:304` y `:317` (`congelar_extension`) — el archivo que el sha sellado cita se reescribe

Mecanismo exacto: `main()` (líneas 650-660) hace

```
ruta, meta = congelar_extension(ext, base_meta["hasta"])   # ESCRIBE disco
...
r = sellar(ruta, meta)                                      # RECIÉN acá mira la base
```

`congelar_extension` calcula `hasta = str(ext.index.max().date())`, arma
`ruta = DIR_EXT/ext_{hasta}.csv` y hace `ext.to_csv(ruta)` + `json.dump(meta)`
**sin abrir la base**. El guardia E4 vive dentro de `sellar()` (líneas 500-519)
y para entonces el archivo ya fue pisado. Es una **fuga de disponibilidad** en
el sentido del mandato ampliado: la fila sellada sigue citando
`insumo_ext_sha256`, pero lo que hay en disco bajo ese nombre ya no es lo que
se selló, y la verificación tardía no puede reproducir el sello.

Reproducción en producción (leída de la máquina el 19-sep, no de memoria):

| dato | valor |
|---|---|
| `fecha_insumo` | 2026-09-09 |
| primer sello | `2026-09-10T00:00:04.881124+00:00`, sha `126e4f2c…`, 33 filas, `insumo_incompleto` |
| segundo disparo (timer) | `2026-09-10T03:30:04.599658+00:00`, sha `7300787b…` |
| fila en `divergencias_sello` | id 1, `decisiones_distintas = 1` |
| filas insertadas por el segundo | 0 (E4 correcto) |
| archivo en disco entre el 10-sep y el 19-sep | `7300787b…` ≠ el sellado |
| archivo en disco hoy | `126e4f2c…` (restaurado por Nicolás con `git checkout`) |
| contenido `7300787b…` | **no existe en ningún lado**: sólo su sha en la fila de divergencia |

Reproducción sintética, con base temporal y `DIR_EXT` temporal:
`test_e4_archivo.py::test_E4_archivo_un_segundo_sello_con_otro_insumo_no_toca_la_extension_sellada`.
El test recorre el camino de `main()` (`congelar_extension` + `sellar`), no
`sellar()` sola — `sellar()` no escribe archivos y desde ahí la fuga es
invisible, que es exactamente por qué la suite de la corrida 12 no la vio:
`test_E4_un_segundo_sello_con_otro_insumo_deja_rastro_y_no_inserta`
(tests/test_sello_dinero.py:222) fabrica las dos extensiones a mano en dos
directorios distintos y nunca ejerce `congelar_extension`.

### F2 — misma línea, variante idempotente — se reescribe incluso con el MISMO insumo

Si el segundo disparo trae el mismo insumo, `sellar()` devuelve `ya_sellada` y
no inserta, pero `congelar_extension` ya reescribió los dos archivos. El CSV
vuelve con bytes idénticos (el sha no lo delata); el `.meta.json` lleva
`congelado_en_utc` (línea 306) y además `solape_con_congelado`, así que en
producción —disparos separados por minutos— **cambia de sha**. Un archivo
sellado que se reescribe sin que nadie lo pida es la misma clase de defecto
aunque el contenido coincida: la constitución dice que las filas selladas
nunca se reescriben, y el insumo sellado es parte de la fila.
Test: `..._un_segundo_sello_con_el_MISMO_insumo_tampoco_reescribe_nada`.
Aviso metodológico: dentro de un test que corre en < 1 s los dos `meta.json`
caen en el mismo segundo y el sha coincide; la evidencia determinista de la
reescritura es el `st_mtime_ns`, y por eso `_huella_ext()` devuelve
`(sha256, mtime_ns)` y no sólo el sha.

### Salida literal del test (hoy, como se exigía: TIENE QUE FALLAR)

```
$ cd /home/nicolasaraneda/dev/mki-terminal
$ venv/bin/python -m pytest .../scratchpad/auditor_e4/test_e4_archivo.py -q -p no:cacheprovider
FF.                                                                      [100%]

E   AssertionError: FUGA E4-archivo: congelar_extension() reescribió la extensión de una
    fecha ya sellada con otro insumo; el sha de la base deja de apuntar a lo que hay en disco
E   Differing items:
E   {'ext_2026-09-08.csv': ('d71adcbb…', 1789846806510591337)} !=
E   {'ext_2026-09-08.csv': ('7ad36c77…', 1789846806113722844)}
E   {'ext_2026-09-08.meta.json': ('22db3792…', 1789846806518876167)} !=
E   {'ext_2026-09-08.meta.json': ('83da5e53…', 1789846806296537266)}

E   AssertionError: FUGA E4-archivo (variante idempotente): la extensión de una fecha ya
    sellada se reescribe aunque el insumo sea el mismo
E   Differing items:
E   {'ext_2026-09-08.csv': ('7ad36c77…', 1789846807000838038)} !=
E   {'ext_2026-09-08.csv': ('7ad36c77…', 1789846806798904609)}
E   {'ext_2026-09-08.meta.json': ('23dcefd2…', 1789846807009808616)} !=
E   {'ext_2026-09-08.meta.json': ('83da5e53…', 1789846806807886298)}

=========================== short test summary info ============================
FAILED test_e4_archivo.py::test_E4_archivo_un_segundo_sello_con_otro_insumo_no_toca_la_extension_sellada
FAILED test_e4_archivo.py::test_E4_archivo_un_segundo_sello_con_el_MISMO_insumo_tampoco_reescribe_nada
2 failed, 1 passed in 1.85s
```

El tercer test (`..._el_respaldo_en_backups_tampoco_cambia`) **pasa hoy**, y pasa
por accidente: `main()` sólo llama `respaldar_extension` cuando
`r["resultado"] == "sellada"` (línea 662), así que el disparo divergente del
10-sep no pisó `data/backups/sello_dinero_ext/ext_2026-09-09.csv`. Esa es la
única razón por la que el contenido `126e4f2c…` sobrevivió además de en git.
Se deja el test para fijar por contrato lo que hoy es un accidente feliz.

---

## 2. DICTAMEN: (A) o (B)

**Dictamen: (A) con una pieza de (B) obligatoria.**

Recomendación operativa, en una línea: **cuando `fecha_insumo` ya tiene filas
selladas, no se escribe ningún archivo de esa fecha — ni el canónico ni uno
divergente — y el sha divergente se calcula EN MEMORIA para la fila de
`divergencias_sello`.**

Razones, en el orden en que pesan:

1. **El sha citado tiene que apuntar a algo que exista mañana (E5), y (B) sólo
   lo cumple a medias.** (B) hace que el sha *divergente* sea auditable, pero
   el sha *sellado* ya está cubierto por `data/backups/sello_dinero_ext/` +
   git. Lo que se gana con (B) es la evidencia de un insumo que **nadie selló
   y que no respalda ninguna cifra publicada**. Lo que se arriesga es la
   integridad del insumo que sí sella. El intercambio no está parejo.

2. **(B) contamina un sello futuro por la vía de `ultima_extension()`, y está
   verificado, no supuesto.** `ultima_extension` (línea 326) filtra por
   `startswith("ext_")` + `endswith(".csv")` y toma `sorted(...)[-1]`.
   Comprobado en la máquina: `sorted(['ext_2026-09-08.csv',
   'ext_2026-09-08_divergente_20260909T033000Z.csv'])[-1]` devuelve el
   divergente (`_` = 0x5F ordena después de `.` = 0x2E), y lo mismo con
   cualquier otro separador. Como la divergencia ocurre siempre sobre la fecha
   MÁS RECIENTE, el archivo divergente domina el orden y `--sin-red` sellaría
   la noche siguiente con el insumo que E4 rechazó. (B) sin tocar
   `ultima_extension` **convierte una fuga de integridad en una fuga de insumo
   al sello**: estrictamente peor que la de hoy.

3. **(B) agrega una ruta de escritura nueva a `dinero/datos/sello/`, que es
   justo lo que el bloque 4.3 quiere sacar de git.** Más archivos por noche
   ruidosa, sin dueño y sin política de retención.

4. **Lo que (B) tiene de bueno y hay que quedarse: el `detalle` de la
   divergencia debe decir qué es ese sha.** Hoy dice sólo «segundo sello del
   2026-09-09 con otro insumo; 1 decisión(es) distinta(s); las filas selladas
   no se tocan». Bajo (A) el contenido se pierde a propósito, y un sha que no
   apunta a nada tiene que **declararlo**, no dejar creer que es recuperable.
   Propuesta de texto para `detalle`, en la misma fila: `"contenido NO
   conservado (decisión A, acta §…): el archivo sellado no se reescribe y el
   insumo divergente no se persiste; este sha es el de un contenido que ya no
   existe"`, más `decisiones_distintas` y, si se quiere auditabilidad barata,
   dos campos derivados calculables en memoria (`filas`, `tickers_con_dato`).
   Eso da trazabilidad sin un archivo nuevo.

5. **Segundo disparo con el MISMO sha (F2): tampoco se escribe.** No es
   cosmético. Si no se escribe, `ext_<fecha>.csv` y su `.meta.json` conservan
   su `mtime` original, y el mtime es la única marca que dice cuándo la
   evidencia se materializó — el mandato exige distinguir «emitido antes» de
   «reproducible después», y un mtime pisado borra esa distinción. Además
   `congelado_en_utc` dentro del meta es lo único que fecha el congelado: hoy
   se sobreescribe con la hora del reintento y el meta miente sobre su propio
   origen.

Forma sugerida (no aplicada; el encargo exige worktree + suite + ventana):
`congelar_extension` recibe un parámetro nuevo (p. ej. `ya_sellado: set[str]`
o una función `sellada(fecha) -> bool`) o bien `main()` calcula `hasta`
ANTES de escribir —el `hasta` sale del índice, no del disco— consulta la base
y corta ahí. **La consulta a la base no debe vivir dentro de
`congelar_extension`**: esa función hoy es pura respecto de la base y meterle
una conexión la vuelve no testeable sin base. Lo limpio es que `main()`
pregunte y decida, y que `congelar_extension` gane un guardia defensivo que
**se niegue a sobrescribir un archivo existente** salvo `permitir_sobrescribir=True`
(el estado terminal correcto: el error es ruidoso, no silencioso).

**Riesgo residual declarado de (A):** si el insumo divergente fuera el
CORRECTO y el sellado el defectuoso, (A) destruye la única copia del bueno. El
mandato ya resolvió ese empate: *«el campeón cuando sello y fuente discrepan
es el que Nicolás firmó»*. La corrección de un sello es una fila nueva o una
errata fechada, nunca la recuperación silenciosa del insumo descartado.

---

## 3. OTRAS RUTAS POR LAS QUE UN `ext_<fecha>` SELLADO PUEDE CAMBIAR

Censo completo de escrituras en `dinero/` (`grep -rn "to_csv|open(...,\"w\")|copyfile|shutil\.|os.replace|os.remove|json.dump"`):

| # | Ruta | Alcanza a un `ext_<fecha>` sellado | ¿Al test permanente (encargo 1.3)? |
|---|---|---|---|
| R1 | `sello_dinero.py:304` `ext.to_csv(ruta)` | **SÍ** — F1/F2 | sí, es la fuga |
| R2 | `sello_dinero.py:317` `json.dump(meta)` | **SÍ** — F1/F2 | sí |
| R3 | `sello_dinero.py:591` `shutil.copyfile` (`respaldar_extension`) | **SÍ, condicional** — pisa la copia versionada sin preguntar; hoy sólo se invoca con `resultado == "sellada"` | sí (tercer test, hoy verde: fija el accidente) |
| R4 | `sello_dinero.py:500-501` — E4 filtra `AND juego = ?` | **SÍ, latente**: si `reglas.json` cambia `juego_activo`, un segundo disparo del mismo `fecha_insumo` con otro juego NO ve las filas previas, devuelve `sellada`, y entonces R1+R2+R3 se disparan los tres sobre la fecha ya sellada, respaldo incluido | sí — el test debe ser por `fecha_insumo`, **sin** filtrar por juego |
| R5 | `precios.py:113` + `:140` (`precios.congelar`) | NO toca `ext_*`, pero reescribe `cierres_congelados.csv` y su meta: rompería `insumo_base_sha256` de TODA fila sellada | sí, como chequeo hermano: `insumo_base_sha256` sellado == `precios.meta_congelado()["sha256"]` |
| R6 | `mapa.py:478-481`, `cuenta_papel.py:815-818`, `senal_larga_reporte.py:814-817`, `cobertura_causal.py:202` | NO (escriben a `dinero/resultados/`) | no |
| R7 | `sello_dinero.py:573` (`exportar_csv`) | NO (escribe `data/backups/sello_dinero.csv`), y H8 ya impide pisar el CSV real desde una base temporal | no |
| R8 | Fuera de Python: `git checkout` / `git rm --cached` / la línea de `.gitignore` del bloque 4.3 | **SÍ** — la restauración del 19-sep fue exactamente esto | no es cubrible por test; ver zonas ciegas |

Forma del test permanente del punto 1.3, para que cubra R1-R4 de una vez:
para **cada** `(fecha_insumo, insumo_ext_archivo, insumo_ext_sha256)` distinto
de `sellos_dinero` (base real en `mode=ro`, **sin** filtrar por juego ni por
estado), exigir `_sha256(DIR_EXT/insumo_ext_archivo) == insumo_ext_sha256` y
lo mismo en `DIR_BACKUP_EXT` (punto 1.4). Hoy eso pasa para las nueve fechas
—verificado: 09-08 `89a5e296`, 09-09 `126e4f2c`, 09-10 `3cc65546`,
09-11 `69126fa2`, 09-14 `74ebdd00`, 09-15 `edc60fad`, 09-16 `664e4f49`,
09-17 `cbec21ba`, 09-18 `e71b7821`, idénticos en disco y en
`data/backups/sello_dinero_ext/`—. Añadir: si una `fecha_insumo` tiene más de
un `insumo_ext_sha256` en `sellos_dinero`, eso es un fallo del test aunque los
archivos existan (R4). Y que el test **falle**, no que saltee, si el archivo
no está: «no está» es el modo de falla que estamos persiguiendo.

---

## 4. SOSPECHAS SIN DEMOSTRAR

- **La ventana entre `ts_emision` y el commit.** `sellar` estampa
  `ts_emision` (línea 469) y `creado_en` (línea 497) antes del `INSERT`; en
  las nueve filas reales la diferencia es de milisegundos, pero el incidente
  del 6-ago (44 min entre estampado y commit en el riel de medición) dice que
  esto no está cerrado. Prueba que lo resolvería: un campo `visible_en` —
  zona ciega Z1 del dictamen de la corrida 12, que el encargo enruta a su
  bloque 4.4. No es de este bloque.
- **Que el contenido `7300787b…` fuera el «bueno».** El 09-sep quedó
  `insumo_incompleto` con el primer insumo; el segundo ya traía el cierre del
  día. No es demostrable en ninguna dirección: el contenido no existe. Queda
  como evidencia perdida, y es el argumento más fuerte de (B) — y aun así no
  alcanza, por el punto 2.2.
- **`descargar_extension` usa `period="30d"` de reloj de pared**, no un
  calendario: el conjunto de sesiones que trae depende de cuándo corre. No es
  fuga de futuro, pero `decidir` declara (docstring, líneas 352-356) que la
  sonda depende del NÚMERO de sesiones entre DESDE y el día. Prueba que lo
  resolvería: sellar dos veces la misma fecha con extensiones de distinto
  largo y comparar la huella de decisión. Fuera del alcance de este bloque.

## 5. VERIFICADO LIMPIO (qué probé, con qué comando, qué salió)

- **La base real no cambió y E4 funcionó en el incidente**: `sqlite3
  file:dinero/sello_dinero.db?mode=ro` — 9 `fecha_insumo`, 33 filas cada una,
  1 fila en `divergencias_sello` (09-09), `COUNT(DISTINCT fecha_insumo) WHERE
  cuenta_para_N=1` = **7**. Coincide con lo que Nicolás vio el 19-sep. Alcance
  de esta prueba: dice que la base está intacta HOY; no dice nada sobre lo que
  pasó entre el 10 y el 19 en disco.
- **Integridad sha hoy**: script propio sobre la base en `mode=ro` — las 9
  fechas coinciden en `dinero/datos/sello/` y en
  `data/backups/sello_dinero_ext/` (tabla arriba). Alcance: es el estado
  POSTERIOR a la restauración de Nicolás; no prueba que el sistema mantenga la
  invariante, sólo que hoy se cumple. Por eso el test permanente.
- **El respaldo versionado nunca fue pisado**: `ls -la
  data/backups/sello_dinero_ext/` — `ext_2026-09-09.csv` con mtime `Sep 9
  21:00` (= 2026-09-10T00:00 UTC, el primer sello), no `Sep 10 00:30`.
- **`congelar_extension` no tiene otros llamadores**: `grep -rn
  "congelar_extension|respaldar_extension|ultima_extension|DIR_EXT"
  --include=*.py .` → sólo `main()` y tests.
- **El orden de `sorted()` en `ultima_extension`**: comprobado en el intérprete
  (punto 2.2). No es una conjetura sobre ASCII.

## 6. ZONAS CIEGAS

- **Z-A. El contenido `7300787b…` es irrecuperable.** Ninguna prueba puede
  decir si el insumo divergente era mejor que el sellado. Es la fuga de
  disponibilidad del mandato, ya consumada.
- **Z-B. No hay marca de «cuándo se hizo visible» ningún archivo.** El `mtime`
  es lo único, y es reescribible y no viaja en git. Dos disparos en el mismo
  segundo son indistinguibles.
- **Z-C. Git no es un guardia.** Los `ext_*` del 10 al 18 están `??` (sin
  seguir); si el bloque 4.3 los agrega a `.gitignore`, **git deja de ser la
  red de seguridad que salvó al 09-sep** y `data/backups/sello_dinero_ext/`
  queda como única copia — lo que hace R3 (`respaldar_extension` pisando sin
  preguntar) más grave, no menos. Esto es un insumo para el bloque 4.3, no una
  objeción a él.
- **Z-D. Nada de esto audita el TIMER.** El test corre `congelar_extension` y
  `sellar` en proceso; no reproduce dos instancias de `systemd` compitiendo.
  Si el timer y una corrida manual se solapan, hay una carrera sobre el mismo
  archivo que ningún test de este bloque ve.
- **Z-E. Fuga por el analista, declarada.** Este test lo escribió alguien que
  ya vio el incidente del 10-sep. Reproduce la fuga conocida; no dice nada
  sobre las que no se manifestaron todavía.
- **Z-F. Yahoo revisa la historia sin avisar.** `_solape_contra_congelado`
  (E7) detecta reajustes sólo sobre las sesiones que solapan con el congelado;
  el propio `advertencia` del meta lo dice: los cierres no son point-in-time.
  Ninguna conclusión de este dictamen depende de que lo fueran.


---

**Nota del orquestador (19-sep-2026, tras el dictamen del `curador-epistemico`):** en F2 lo demostrado por el test es la reescritura (mtime); que el `.meta.json` cambie de sha en producción por un `congelado_en_utc` distinto es inferencia del auditor, no ejecutada. La corrección (opción A) no escribe nada con la fecha sellada, así que cubre los dos casos.
