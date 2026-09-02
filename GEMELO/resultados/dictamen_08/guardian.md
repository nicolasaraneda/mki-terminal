# Dictamen del `guardian-constitucion` · cierre de la octava corrida (2-sep-2026, 15:25)

> Texto del agente, condensado por el orquestador sin cambiar hallazgos. Sobre el árbol de trabajo completo antes de los commits. Suite corrida por el guardián: 596 passed, 2 xfailed; `tests/test_motor.py` en verde.

```
DICTAMEN: OBSERVADO   Rama: main   Archivos: 17 modificados + 53 untracked   Líneas: +974 −78
RECHAZOS: ninguno. Ninguna regla dura se rompió.
```

## Verificado en verde

R0 motor y lógica de señales intactos (`motor.py`, `senales.py`, `snapshot.py`, `universo.py`, `version.py`, `alertas.py`, `noticias.py`, `calendarios.py`, `app.py`, `api/`, `frontend/` no aparecen en el diff). R1 filas selladas: `senales.db` mtime 2026-09-01 18:15:31 sin cambio antes ni después de la suite; ningún `UPDATE`/`DELETE`/`to_sql` en el diff; el árbitro corta en `verificado_en <= 2026-08-28`, así que el sello de esta noche no puede mover n = 248. R2 sin push. R3 rama `main`. R5 sin secretos ni `.db`/`.log`/`.env` en los untracked. R8 `.env`, `systemd/`, `launchd/`, `mki`, `scripts/` intactos. R9 README sin cambios; árbitro recomputado = README (n 248, +6,5, 0,1849, 2,98/3,33, 90,3 %, 1,84); banda [0,046, 0,079] intacta; `GEMELO/DISEÑO.md` y `backtest/DISEÑO.md` sin modificar (V1-bis es adición fechada). Hooks y `settings.json` intactos; la extensión no instalada. (a) el `resumen.md` del 5.1 sólo recibió la ERRATA al pie. (b) `ErrorUnidadSharpe` restringe el dominio, no la pureza: `psr`/`dsr` siguen deterministas y sin I/O. (c) `_bootstrap_dia(semilla=SEMILLA)` con default fijo reproduce lo publicado; `_ic_t_cluster` aditivo; `np.trapezoid` cubierto por numpy 2.4.6 fijado. (d) 100 → 286 / 292 consistente en tres sitios, dirección conservadora. (f) testigo B2 descargado a las 14:50 (fuera de la ventana), sha256 verificado. La edición de `evaluacion.py` (1,77 → 1,84) es un script de skill, no un hook: **permitida**, alinea un docstring rancio a la canónica.

## Observaciones (las siete marcadas se aplicaron antes del commit)

- **O1 (bloqueante, aplicada).** La justificación desmentida («un Sharpe anualizado sobre pocos días es un artefacto… saturan en 1,0000») seguía viva en tres ejecutables: `backtest/veredicto_51.py` (comentario de `MINIMO_DIAS_SHARPE` y **texto del reporte del veredicto 5.1**) y el generador `GEMELO/ventana_larga.py`. Regla de la casa #2 incumplida por la corrida que la escribió; «1,0000» y «saturan» no estaban en `cifras_retiradas.md`.
- **O2 (bloqueante, aplicada).** En `calibracion.py` la rama `anualizado` de A3 contaba una `ErrorUnidadSharpe` como rechazo «porque habría sido ≥ 0,95»: un supuesto en el lugar de un cómputo, en la dirección favorable y circular (la guarda nació de esta medición). Se computa sin la guarda.
- **O3 (aplicada).** El acta §75(3) decía que la v2 de E estaba en curso y que el artefacto seguía «pendiente de dictamen»: falso, el artefacto era la v2 con su sección de correcciones.
- **O4 (aplicada).** `potencia_por_metrica.md` se contradecía (cabecera v1, sección v2) y su primera tabla publicaba 223 / 96 / 88 como puntos desnudos.
- **O5 (aplicada).** La cadena 0,34 → 0,36 → 0,31 quedó rota: `cifras_retiradas.md` ofrecía 0,36 como reemplazo y `espera_firma.md` §17 lo citaba mientras §23 decía 0,31; ni 0,36 ni «saturan» estaban en el registro.
- **O6 (declarada, no retro-escrita).** `decaimiento_feriados.lock` lleva fecha y razón pero no `sha256_anterior` (el candado nació en la re-apertura); el acta lo dice.
- **O7 (aplicada).** `frente_D.md` numeraba dos veces «Enmienda 2».
- **O8 (aplicada).** `b2_nuevos_ohlc.csv.gz` no estaba en el índice de `testigos_fuente/README.md`; y conviven dos convenciones de sha (csv en claro vs `.gz`) sin declararlo.
- **O9.** `.env` en 644: R5 no queda satisfecha hasta el `chmod 600` (de Nicolás; el sandbox del guardián no pudo verificar el modo).
- **O10.** `ESTADO.md` perdió el bloque «deuda con modo de falla activo» (`snapshot.py:140`); sigue primero en `espera_firma.md` §1.
- **O11.** `CLAUDE.md` describe al Mac como titular y a este PC en sombra; `ESTADO.md` dice lo contrario. Es de Nicolás.
- **Menores.** `cifras.py` computaba un `ses` sin usar (aplicado); docstring del test con `CORTE_SECCION_2` donde el código usa `CORTE_README` (aplicado); la guarda de `psr` no valida `sr_ref`; las constantes nuevas quedaron bajo el banner del bootstrap en `inferencia.py`; el ratio 1,84× no es ninguno de los doce bloques: agregarlo como bloque trece cambia el contrato del árbitro y es de Nicolás.

## No verificado

Permisos de `.env` (sandbox); el verde de las 15:10 caduca si la tanda cruza las 18:15; el acta §75 se modificó durante la revisión (citas por línea a revalidar).
