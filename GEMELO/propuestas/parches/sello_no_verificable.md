# PROPUESTA — NO APLICADO. Parche E0.3 del sellador del riel de dinero: un disparo con timing roto no ocupa ni la fecha ni el cupo canónico

> **Estatus: PROPUESTA. `dinero/sello_dinero.py` del árbol real NO cambió** (sha256 `480fbdc9…`, idéntico a HEAD
> `2f73eb2`). El parche vive en `sello_no_verificable.diff`, escrito y probado en un worktree (`wt15_b3`) con copias
> de las bases y carpetas temporales; el sellador real no se ejecutó. Aplicarlo exige un acta posterior de Nicolás con
> la política (`politica_evidencia_no_verificable.md`) a la vista (acta §90.6; un cambio por noche al sellador, lejos
> de las 23:30 NY). Implementa el **camino T** de la política (tabla aparte, aditiva). Corrida 15, 29-sep-2026.

## Qué cambia, función por función (`dinero/sello_dinero.py`)

- **`VERSION_SELLO`** `"E0.2"` → `"E0.3"`. Es el corte de método sellado en cada fila nueva: desde E0.3 ninguna fila
  con timing roto entra en la tabla principal. `TABLA_SELLOS` / `TABLA_INTENTOS` nuevas constantes.
- **`_ddl_filas(tabla)`** (nuevo) + **`_DDL_DIVERGENCIAS`** + **`init_db`**: las 35 columnas y los dos disparadores
  de inmutabilidad salen de UNA definición; `init_db` la ejecuta para `sellos_dinero` y para la tabla nueva
  **`intentos_no_verificables`** (mismas columnas, misma `UNIQUE (fecha_insumo, ticker, juego)`, mismos
  `_ABORTA_MODIFICAR`/`_ABORTA_BORRAR`). Todo es `CREATE … IF NOT EXISTS`: sobre la base real sólo se AGREGA.
- **`evaluar_timing(disponibilidad_por_ticker, fecha_insumo, ahora_utc)`** (nuevo, puro): `avail` (máximo
  `available_at_utc` por ticker, o cierre por calendario), `sesion_obj`, `apertura_obj`, `timing_ok` =
  `avail < ahora < apertura`. La usan congelar y sellar: una sola fórmula (test lo verifica por el fuente).
- **`sello_previo`** misma firma, mira sólo `sellos_dinero`. **`intento_previo`** (nuevo) mira la tabla de intentos;
  base sin la tabla → `None`. Los dos delegan en `_cita_previa`/`_cita_en`.
- **`congelar_extension(…, ahora_utc=None)`**: decide el timing ANTES de escribir. Timing ok → como E0.2 (las tres
  ramas E4-bis intactas). Timing roto, fecha sin sello y sin intento → `ext_<fecha>.no_verificable.csv` +
  `.no_verificable.meta.json` con `cupo_canonico: false` y bloque `timing` (`available_at`, `emision_utc`,
  `apertura_objetivo_utc`, `sesion_objetivo`, `timing_ok`). Timing roto y fecha ya con intento → temporal fuera de
  `DIR_EXT`, `persistido: False`, `divergente_de = {archivo, sha256_intento, nota}`. Fecha ya sellada → E4-bis, sin
  cambio. Default de `ahora_utc`: el reloj (así lo llama `main()`).
- **`es_extension_no_verificable`** (nuevo) y `SUFIJO_NO_VERIFICABLE`. `es_extension_sellable`, `ultima_extension`
  y `--sin-red` NO cambian: un `.no_verificable.csv` nunca se levanta como insumo.
- **`sellar`**: `timing_ok = evaluar_timing(…)["timing_ok"] and not evidencia_no_verificable`, donde
  `evidencia_no_verificable` = meta con `cupo_canonico: false` o nombre `.no_verificable.csv` (la clase de la
  evidencia sólo puede endurecer el veredicto). Fecha con sello del mismo juego → `ya_sellada` / divergencia, como
  hoy. Timing roto: fecha con intento previo o con sello (otro juego) → fila en `divergencias_sello` (detalle dice
  «segundo intento no verificable…»), cero filas (mismo sha que el intento previo → `ya_intentada`, sin fila: R4);
  evidencia de nombre canónico → `rechazado_evidencia_canonica`, cero filas de sello/intento, fila en
  `divergencias_sello` (B1), archivo intacto; si no → inserta en `intentos_no_verificables`, resultado `intento_no_verificable`
  (mismas claves que `sellada`, más `tabla`). Timing ok → inserta en `sellos_dinero` como E0.2; un intento previo de
  la fecha NO cuenta como sello previo. La divergencia se factorizó en `_divergencia()` (misma fila que hoy, más
  `divergente_de` en el resultado).
- **`exportar_csv`**: además `<ruta>_no_verificables.csv`; base sin la tabla → no escribe ese archivo.
- **`respaldar_extension`**: sin cambio; deriva el meta con `splitext`, y `ext_F.no_verificable` + `.meta.json` es
  exactamente el nombre que congelar escribe (test).
- **`estado()`**: clave nueva `intentos_no_verificables` (fechas distintas); ninguna clave existente cambia (la API
  las lee). **`main()`**: con `intento_no_verificable` exporta, respalda el par `.no_verificable` e imprime una
  línea clara; con `rechazado_evidencia_canonica` imprime y no escribe.

## Tests (`tests/test_sello_dinero.py`: 50 en verde; sección 5 nueva, secciones 2–4 adaptadas)

Adaptados, con el porqué en su docstring: `test_sellar_despues_de_la_apertura_queda_no_verificable` y
`test_un_insumo_desactualizado_no_cuenta_para_N` (filas a la tabla de intentos, `sellos_dinero` vacía);
`test_E4bis_sin_sello_previo_…` y `test_E4bis_sello_previo_no_filtra_por_juego` (pasan `ahora_utc`);
`_camino_main` llama `congelar_extension` con el reloj vía `_congelar` (shim que sobre E0.2 no pasa el instante,
para que la reproducción falle en HEAD por su aserción y no por `TypeError`); `_extension_sintetica(no_verificable=)`.
Ningún test se borró. Nuevos:
- `test_reproduccion_28sep_…`: disparo 1 a las 13:42 NY del lunes 14-sep con barra intradía; disparo 2 a las 23:30 NY
  con el cierre. El 2 sella (33 filas, `pendiente`, `cuenta_para_N=1`); las 33 del 1 en `intentos_no_verificables`
  con `no_verificable_timing`; `ext_2026-09-14.csv` = sha del 2; el par `.no_verificable` = sha del 1, meta con
  `cupo_canonico: false` y `timing`; `estado()` y `ultima_extension()` coherentes. **Rojo en HEAD (abajo).**
- `test_las_filas_del_intento_no_cambian_cuando_llega_el_sello_bueno`: volcado byte a byte + sha/mtime del par.
- `test_un_segundo_intento_no_verificable_deja_divergencia_y_ningun_archivo_nuevo`; `…sobre_una_fecha_ya_sellada_no_toca_nada`
  (divergencia con otro sha, `ya_sellada` con el mismo; canónico intacto por sha y mtime);
  `test_un_sello_tardio_va_a_intentos_y_un_disparo_posterior_tampoco_sella`.
- `test_los_intentos_no_verificables_no_se_reescriben_ni_se_borran` (disparadores); `…tiene_las_mismas_columnas…` (36 = id + 35).
- `test_sin_red_jamas_levanta_un_archivo_no_verificable`; `test_evaluar_timing_es_una_sola_formula…` (bordes: el
  cierre mismo y la apertura misma no son «antes»; sin meta cae al calendario; exige zona horaria; el fuente de
  `sellar` y `congelar_extension` llama `evaluar_timing(` y ya no `proxima_sesion_despues_de(`).
- Discordancia de reloj entre congelar y sellar: `…no_sella_aunque_el_reloj_del_sello_diga_ok` y
  `test_timing_roto_sobre_una_evidencia_canonica_se_rechaza_sin_escribir_filas`.
- `test_exportar_y_respaldar_cubren_el_par_no_verificable`; `test_estado_agrega_los_intentos_sin_cambiar_las_claves…`;
  `test_una_base_sin_la_tabla_de_intentos_se_lee_como_cero_intentos` (esquema E0.2 fabricado; el primer sello en
  escritura crea la tabla sin tocar lo existente); `test_las_filas_no_verificables_viejas_de_la_tabla_principal_siguen_ocupando_su_fecha`
  (fila E0.2 fabricada por INSERT, sin nombrar fecha: `sello_previo` la devuelve, el disparo entra por divergencia).
- Integridad permanente (política §5): `_citas_selladas(ruta_db, tabla)` por tabla, tabla ausente = cero intentos;
  `_verificar_clase_de_evidencia` (invariante 5.2); `_verificar_regla_del_corte` (una fila rota en la principal
  sólo con `version_sello` < E0.3, comparada como números); los dos tests reales parametrizados por tabla y dos
  nuevos sobre la base real; `test_integridad_de_punta_a_punta_con_intento_y_sello_de_la_misma_fecha`; contraprueba
  de la clase y del corte. Sobre la copia de la base real (14 fechas, 28-sep con `roto` E0.2): en verde.

## Salida del test de reproducción fallando en HEAD (sellador sin modificar, 23:09 Chile)

```
$ venv/bin/python -m pytest "tests/test_sello_dinero.py::test_reproduccion_28sep_un_disparo_intradia_no_quema_la_sesion_ni_el_cupo_canonico" -q -p no:cacheprovider
F                                                                        [100%]
>       assert r2["resultado"] == "sellada", (
            "EL 28-SEP: el disparo bueno de las 23:30 NY no selló porque la fecha quedó ocupada por el "
            f"intento intradía (resultado={r2['resultado']!r}, filas_insertadas={r2.get('filas_insertadas')})")
E       AssertionError: EL 28-SEP: el disparo bueno de las 23:30 NY no selló porque la fecha quedó ocupada por el intento intradía (resultado='divergencia_registrada', filas_insertadas=0)
E       assert 'divergencia_registrada' == 'sellada'
tests/test_sello_dinero.py:700: AssertionError
1 failed in 1.10s
```

## Conteo final en verde

`Tue Sep 29 23:22:03 -03 2026` — `tests/test_sello_dinero.py tests/test_dinero.py tests/test_sonda_cierre.py
tests/test_frontend_estatus.py`: **118 passed** (`-m "not red"`; 50 son del sellador). Antes, a las 23:16:
`test_api.py test_readme.py test_epistemico.py test_secuencial_07.py`: 127 passed, **2 failed y 1 error
PREEXISTENTES, ajenos al parche**: `test_readme.py::…contador_de_e0…` y `…son_lo_que_el_generador_produce`
(README.md en HEAD no contiene «count towards N»; ninguno de los dos archivos que leen está en el diff) y
`test_api.py::test_paridad_roca_chip_contra_snapshot` (abre red a Yahoo sin `@pytest.mark.red`; no toca `dinero/`).
Aislamiento AST (`test_dinero.py`) en verde. `/api/dinero/sellos` leído en vivo contra la copia de la base sin la
tabla nueva: responde igual y la lectura NO crea la tabla.

## Cómo se aplica (cuando un acta lo firme)

`git apply --check GEMELO/propuestas/parches/sello_no_verificable.diff && git apply GEMELO/propuestas/parches/sello_no_verificable.diff`
sobre HEAD `2f73eb2` limpio (verificado: `apply --check -R` contra el worktree y `apply --cached --check` contra el
índice en HEAD). Después, la suite del sellador (`tests/test_sello_dinero.py`) fuera de la ventana de sellado. La
tabla nueva aparece en `dinero/sello_dinero.db` en el primer sello en escritura (aditivo).

**`sellador_sha256` cambia**: las filas nuevas llevan la huella del módulo parcheado (`2d603251…` en el worktree; la
definitiva será la del archivo aplicado), no `480fbdc9…`. No es reescritura: las filas viejas conservan la suya.

## Exigencias del auditor plegadas (dictamen APLICABLE CON EXIGENCIAS; plegadas a las 23:42 Chile del 29-sep-2026)

- **B1 (bloqueante):** la rama `rechazado_evidencia_canonica` de `sellar` ya deja rastro: una fila en
  `divergencias_sello` con `sha_sellado = sha_nuevo` = sha del insumo rechazado, `decisiones_distintas = 0` y un
  `detalle` que dice qué es cada cosa y lleva `available_at`, `emision` y `apertura_objetivo`. Redacción corregida
  respecto del texto dictado: dice «NINGUNA fila escrita en sellos_dinero ni en intentos_no_verificables (sólo esta,
  en divergencias_sello)», porque la fila sí se escribe. `main()` exporta en esa rama. Test nuevo:
  `test_un_rechazo_por_evidencia_canonica_deja_fila_en_divergencias_y_cero_en_las_dos_tablas` (reemplaza al
  `…se_rechaza_sin_escribir_filas` de la primera versión).
- **R4:** un segundo intento con el MISMO sha devuelve `{"resultado": "ya_intentada", …}`, cero filas, sin fila en
  `divergencias_sello` (simétrico con `ya_sellada`). Con OTRO sha sigue siendo divergencia.
  `test_un_sello_tardio_va_a_intentos_y_un_disparo_posterior_tampoco_sella` adaptado con el porqué; la duda 3 de
  abajo queda resuelta por esta vía (la política §2.4 la enmienda el orquestador).
- **R2:** `_citas_selladas` hace `pytest.skip("la base real todavía no tiene intentos_no_verificables: cero
  intentos, nada que verificar")` cuando falta la tabla, en vez de devolver `[]`; los dos tests de integridad
  parametrizados por tabla saltan hoy para esa tabla (2 skipped) y dejan de saltar cuando el sellador la cree.
  `test_integridad_ninguna_tabla_cita_la_evidencia_de_la_otra` verifica siempre la mitad de `sellos_dinero`
  (`_tabla_existe` decide la otra mitad).
- **R3:** `entorno_temporal` parchea además `S.RUTA_BACKUP_CSV` a `tmp_path`, así la guarda H8 de `exportar_csv` no
  puede escribir en `data/backups/` real desde un test futuro.
- **R5:** `main()` imprime en toda rama `relojes: congelado_en_utc=… timestamp_utc=… delta_s=…` (los resultados
  `ya_sellada` y `divergencia_registrada` ganaron la clave `timestamp_utc` para eso); el cruce entre los dos relojes
  queda medido en el log del sellador, no inferido.
- No se hizo **B2** (API y CONTRATO.md): va aparte, a tarjeta.
- Conteo tras plegar: `Tue Sep 29 23:42:02 -03 2026` — `tests/test_sello_dinero.py tests/test_dinero.py`
  (`-m "not red"`): **89 passed, 2 skipped** (los de R2). Diff regenerado (1323 líneas), `apply --check -R` y
  `apply --cached --check` contra HEAD `2f73eb2`: OK. Sha del sellador parcheado en el worktree: `2c33f0c7…`.

## Lo que este parche NO hace

- No toca el 28-sep: sus 33 filas siguen en `sellos_dinero` citando `ext_2026-09-28.csv`; la sesión sigue perdida.
- No implementa la (a) del acta como se firmó (`sello_previo` distinguiendo estados): con T no hace falta para
  ninguna fecha nueva, y para el 28-sep no serviría (`UNIQUE`). Es la decisión que el acta que aplique debe ver.
- No cambia qué sesión cuenta para N (§57), ni evita el disparo fuera de hora (§63), ni el timer.
- No hace testeable `main()`: `sellar` y `respaldar_extension` toman `RUTA_DB`/`DIR_BACKUP_EXT` como defaults ligados
  al importar, así que un test que llame `main()` escribiría en la base real aunque parchee los globales. Se
  reprodujo su camino con `_camino_main` (congelar + sellar) y las ramas de export/respaldo con llamadas directas.

## Dudas y riesgos

1. **Caso que la política no contempla, resuelto acá por rechazo:** evidencia congelada con nombre canónico
   (timing ok en `congelar_extension`) y timing roto en `sellar` —la apertura se cruzó en los segundos entre las
   dos, o `--sin-red` levantó un canónico nunca sellado—. El parche no escribe ninguna fila (`rechazado_evidencia_canonica`)
   y deja el canónico huérfano en disco. Alternativas que el acta puede preferir: (i) filas en intentos citando el
   canónico (rompe §5.2 y pondría rojo permanente el test de integridad), (iv) que `sellar` copie el contenido al par
   `.no_verificable` (una escritura nueva desde `sellar` en la carpeta de evidencia). Tras B1 el rastro del disparo
   queda en `divergencias_sello` (antes sólo en el log).
2. **Dos relojes** siguen existiendo (congelar y sellar leen `datetime.now` por separado en `main()`); se optó por no
   unificarlos para no adelantar `timestamp_utc` al instante previo al gate. La discordancia inversa (NV al congelar,
   ok al sellar) va a intentos por la clase de la evidencia, y esa fila lleva `estado_timing = roto` con instantes que
   por sí solos se verían «ok»: la explicación está en el `timing` del meta que cita.
3. (Resuelta por R4.) Un segundo intento con el MISMO sha es `ya_intentada`, sin fila, simétrico con `ya_sellada`;
   la política §2.4 se enmienda aparte.
4. `sha_sellado` de `divergencias_sello` guarda el sha de un intento cuando lo que ocupaba la fecha era un intento;
   el `detalle` lo declara. La columna no cambió de nombre.
5. `api/CONTRATO.md` no se tocó (la clave nueva de `estado()` no sale por la API); `docs/`/`README` tampoco.
6. No verificado: el timer real, dos instancias concurrentes, y el comportamiento con Yahoo de verdad (red parcheada).
