# Informe del implementador del bloque 2, el README (corrida 15) — archivado por el orquestador

> Resumen fiel del informe del agente (worktree `wt15`, HEAD `2f73eb2`). Horas de `date` del agente:
> estado inicial 22:27 (`--verificar` exit 1, el rojo conocido de §65); generador corrido 22:33:57
> (`--verificar` exit 0); `tests/test_readme.py` 22:34:25 (19 en verde); contrapruebas 22:35:16 (23
> en verde, archivo fuera del worktree); vigilantes de `cifras.py` 22:35:44 (27 passed, 1 skipped,
> 1 xfailed); corte de cuota ~22:40; reanudación 23:02:31 con las mismas tres comprobaciones en verde
> y `--collect-only` en 1024 (con los tests de los otros bloques).

## Archivos

`scripts/generar_readme.py` (+125/−?), `docs/readme/README.en.tmpl.md` (23 líneas),
`docs/readme/README.es.tmpl.md` (10), `tests/test_readme.py` (10 → 19 tests),
`docs/readme/badges_congelados.json` (nuevo), `README.md` y `README.es.md` regenerados. `cifras.py`
no se tocó ni hizo falta.

## Qué cambió

- **§90.3.** `valores()` ya no llama a `contador_e0()`; la función, la constante `RUTA_CSV_DINERO` y
  `import csv` se eliminaron (nadie más los usaba: grep en todo el repo incluidos `api/` y `tests/`).
  Las claves `e0_sesiones_selladas`, `e0_cuentan_para_N`, `e0_ultima_fecha_insumo` y `e0_no_cuentan`
  desaparecen; `e0_N_objetivo` (40, leído como texto del sellador) queda. La viñeta de E0 en inglés:
  «E0 in progress (since 2026-09-08) … A sealed session counts towards N = 40 only if it was sealed
  on time, on a trading day, with complete and fresh input. This page carries no running count: the
  sealed rows live in `data/backups/sello_dinero.csv`, the exported copy of the sealing database
  that the daily backup job versions.» **La frase sobre `/salud` se quitó** porque `/salud` no muestra
  el riel de dinero (`frontend/src/vistas/Salud.tsx` → `/api/salud` → `_operacion()`, `api/main.py:348-420`:
  los 5 jobs, descarga sellada, verificaciones, presupuesto IA y tamaños de bases); el estado de E0 lo
  sirve `/api/dinero/sellos` (`api/main.py:1352`) y lo muestra la vista `/sellos`
  (`SellosDinero.tsx`). No se puso `/sellos` en su lugar: no está firmado.
- **§90.4.** `docs/readme/badges_congelados.json` (`tests_recolectados`, `plataforma_version`,
  `leido_el`, `comando_tests`, `fuente_plataforma`, `nota`), validado en forma por
  `badges_congelados()`; claves `badge_tests_n`, `badge_plataforma`, `badge_leido_el_url` (fecha con
  guiones dobles para shields.io). Badges en las dos plantillas:
  `tests-{{badge_tests_n}}%20recolectados%20al%20{{badge_leido_el_url}}` y
  `plataforma-{{badge_plataforma}}%20al%20{{badge_leido_el_url}}`. «passing» → «recolectados» porque
  N cuenta saltados y xfail. Ningún test exige N ni versión vivos.
- **§88.5 (i).** `n_intentos_dsr()` lee como texto `N_INTENTOS_PREVIO` y `N_INTENTOS_NUEVOS` de
  `backtest/veredicto_51.py` y exige que `N_INTENTOS_51 = N_INTENTOS_PREVIO + N_INTENTOS_NUEVOS`
  siga escrito así; si no, `FuenteIlegible`. Hoy 354 y 360. Marcadores `{{n_intentos_previo}}` y
  `{{n_intentos_51}}` en las dos plantillas.
- **§88.5 (iii).** `{{larga_veces}}` = `f"{L.n / c['n']:.0f}"` (hoy 14.618 / 238 → 61). El
  dictamen 13 (`adversario_readme.md`, punto 5) define un único valor: 14.618/238 = 61,4×; 59× era
  14.618/248, el n derogado. Ninguna otra aparición de «59×» en las plantillas.

## Tests nuevos en `tests/test_readme.py`

Sección 5 (§90.3): `test_el_readme_no_lleva_contador_vivo_de_e0_y_remite_a_la_copia_versionada` (con la
razón del retiro del test viejo en el docstring), `test_el_generador_no_abre_el_csv_del_riel_de_dinero`
(espía de `builtins.open`), `test_la_fecha_de_inicio_de_e0_es_la_de_la_primera_fila_sellada` («since»
= `min(fecha_insumo)` del CSV). Sección 6 (§90.4): el JSON tiene fecha ISO válida y declara su fuente;
los dos README llevan los valores congelados y la fecha; los literales viejos (`tests-650`,
«passing», `plataforma-5.0.3`) ya no están; un JSON mal formado rompe la generación. Sección 7
(§88.5): el N de intentos del README es el de `veredicto_51` (importado, contrastado con el texto); el
generador revienta si faltan los literales; las veces de la ventana larga son el cociente del árbitro.
Eliminado: `test_el_contador_de_e0_del_readme_es_el_de_la_copia_versionada`. Renombrado:
`..._mas_el_contador_e0` → `..._mas_el_n_objetivo_de_e0` (extras permitidos `e0_N_objetivo`,
`corte_readme`).

## Diff de los dos README

`README.es.md`: los dos badges; «59× la muestra» → «61× la muestra»; «Va en 352 … 358» → «354 … 360».
`README.md`: lo mismo más la viñeta de E0. La desincronización previa del disco (contador del 19-sep:
9 / 7 / 2026-09-09, 2026-09-18 / 2026-09-18 contra 14 / 9 / cinco fechas / 2026-09-28 que rendía la
plantilla) vivía íntegra en la viñeta reemplazada. Ninguna otra línea cambia.

## Lo que el agente dejó dicho, sin adorno

1. El JSON quedó con N = 932 (22:29); a las 23:02 el mismo comando daba 1024. **Se relee al cierre**
   con el comando `pytest tests/ --collect-only -q | tail -1` en el árbol real, se cambian los tres
   valores juntos y se corre el generador (después de las 00:50).
2. `GEMELO/resultados/tesis.md:161` sigue diciendo «La ventana larga da 59× la muestra»: fuera de sus
   archivos, no tocado.
3. «with the six from 5.1» / «con los seis del 5.1» es prosa literal de `N_INTENTOS_NUEVOS = 6`.
4. Frases del README que afirman algo no verificado hoy, no cambiadas: E1 «No practice account and
   no gateway exist yet» (el acta §91.9 dice usuario de práctica por activar) y «the adapter refuses
   in code … and a test proves it»; E0 «every trading night» (la sesión del 25-sep no tiene filas);
   la apertura sólo en inglés «built to be unable to lie to its own author».
5. Cosmético: una línea corta en el README rendido por el ancho del marcador.
6. Un test marcado `red` de `test_backtest.py` no se corrió (deselected). `corte_readme` sigue
   permitido como extra aunque ninguna plantilla lo use. El test de la sección 7 rechaza «352» y
   «358» sueltos en las plantillas.
7. La sección «Execution rail» no quedó vacía de contenido verificable: no hace falta tarjeta por ese
   motivo.
