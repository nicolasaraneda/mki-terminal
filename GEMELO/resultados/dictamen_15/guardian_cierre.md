# Dictamen del `guardian-constitucion` al cierre de la corrida 15

> Archivado por el orquestador tal como lo devolvió el agente (resumen fiel de la tabla y textual en la
> exigencia). Lanzado a las 10:48 del 30-sep-2026 sobre el diff completo, después del último `Write` de
> contenido y con el `git status` del momento; devuelto a las **10:56:11** (hora de `date` del agente).

**VEREDICTO: APROBADO CON EXIGENCIAS (1).** En el vocabulario del guardián es OBSERVADO: la exigencia se aplica y el commit sale. Rama `main`, HEAD `2f73eb2`, nada commiteado. 20 archivos modificados y 13 nuevos; +2.427 −143 sobre lo rastreado; 2.480 líneas de diff leídas enteras (excluidos `data/sonda_cierre.csv` y `data/backups/sello_dinero.csv`, de los timers).

## Tabla regla por regla

| # | Regla | Veredicto | Cita |
|---|---|---|---|
| R0 | `motor.py` / lógica de señales | VERDE | `git diff --stat` no los lista; ningún import nuevo a ellos en las líneas `+`. |
| R0-bis | Aislamiento GEMELO ↔ sellado | VERDE | `grep GEMELO snapshot.py senales.py motor.py universo.py alertas.py` vacío; `snapshot.py:159-163` declara por qué no escribe ese nombre. |
| R1 | Filas selladas jamás reescritas | VERDE | Único `UPDATE` nuevo `senales.py:361-362`, idéntico byte a byte al de la regla maestra (`:338-339`) y sobre el mismo conjunto (`estado = 'pendiente'`); 0 `DELETE FROM`, `DROP`, `ALTER TABLE`, `to_sql`, `if_exists` en el diff. El único `DELETE FROM` del árbol nuevo está en el parche NO aplicado, dentro de un `pytest.raises(IntegrityError)`. |
| R1-bis | Las 24 filas del 28-sep | VERDE, medido | `mode=ro`: `(None, 16)`, `('verificada', 8)`. |
| R2 | Sin push, pull ni git destructivo | VERDE | 0 coincidencias; `git log -1` en `2f73eb2`; lo único escrito en `.git/` es `worktree remove` + `prune` de los dos worktrees del scratchpad, declarado. |
| R3 | Rama | VERDE | `main`. |
| R4 | Actas | AMARILLO, la exigencia | El acta §92 nombra todas las decisiones de comportamiento buscadas (regla 0 del backup con costo medido, `COMMITEAR_DIA_SIN_SELLO`, reloj fijo de `test_autonomia`, `monkeypatch` de `test_sombra`, betas de `salud_r2_regimen_beta`, orden exclusión→dedup, generador del README, frases nuevas del README). Falla la última frase de §92.4 «Ningún contenido nuevo en español»: falsa desde la recomendada 11 del curador (`README.es.md:178`). |
| R5 | Secretos | VERDE | 5 patrones sobre 2.480 líneas: 0; `.env*` en `.gitignore`; ningún `.db`, `.log`, `.env`, `venv/` en el status. |
| R6 | Verdes | VERDE, con salvedad cerrada por él | Dos suites 1019/5/1/0 más `test_motor.py`; `DECISIONES.md` y la bitácora se escribieron después del último verde: corrió `test_epistemico.py` y `test_razones_xfail.py`: 21 passed, 1 skipped, 1 xfailed. |
| R7 | Alcance | VERDE | Lo que el encargo mandaba y nada más; hallazgos de camino anotados sin tocar; §90.2 detenido; vigía a tarjeta; once elecciones de agente en tarjetas, ninguna firmada por omisión. |
| R8 | Modo y timers | VERDE | Ni una unidad ni `launchd/` en el status; `.env` no tocado; las menciones de `systemctl` son prosa de procedimiento para Nicolás. |
| R9 | Cifras que dependen de n | VERDE | `n = 238` sin mover; badges `sellada` y `larga` idénticos; lo movido está firmado; `--verificar` exit 0; los doce bloques siguen saliendo de marcadores. |
| R10 | Cifras retiradas | VERDE, con inventario | `cifras.reintroducciones()` sobre 39 archivos: 54 coincidencias, todas preexistentes en HEAD (53 en actas viejas de `DECISIONES.md`, 1 en un comentario de `linea_base.py:196`), ninguna tocada por el diff; 0 en todo lo nuevo. |
| R11 | Corrección al ejecutable primero | VERDE | El contador se retiró del generador; el «59×» y el «352» son marcadores con `FuenteIlegible`; las guardas son código con test rojo en HEAD y el acta §92.9 es la errata que los acompaña. |
| R12 | Etiquetas | VERDE | Todo número nuevo publicado es censo o cociente con procedencia; los dos «DEMOSTRADO» rechazados por el curador ya no están; las cuatro bloqueantes y las siete recomendadas del curador, aplicadas. |
| R13 | Parches a archivos protegidos | VERDE, con lectura declarada | El único `.diff` nuevo toca `dinero/sello_dinero.py` y su test, no está aplicado (sha256 de HEAD verificado) y está en tarjeta. Lectura declarada para Nicolás: los cambios aplicados a `snapshot.py` y `senales.py` no son «un parche» de la carpeta de propuestas saltándose el hook sino la ejecución directa de la firma §90.1 con auditor y test rojo en HEAD; si Nicolás quiere la lectura literal, el diff es RECHAZADO y la corrida 16 va a encontrar la misma pregunta. |
| R14 | Supuestos en lugar de cómputos | VERDE | El margen de 2 h se midió y refutó; §90.2 se detuvo por censo; los tamaños de la política se midieron; el «897» se releyó. |
| Extra | Reglas de la noche | VERDE | Aplicaciones a las 23:22:17 y 23:30:25 del 29 y 10:39:01 del 30, fuera del tramo 00:15 a 00:50 y de la ventana 17:50 a 20:30; `dinero/sello_dinero.py` intacto; los dos sellos con sha256 y hora verificados. |

## Exigencia

**E1 (R4).** `DECISIONES.md`, última frase del acta §92.4: reemplazar «Ningún contenido nuevo en español.» por «Ninguna sección nueva en español: la única prosa española que cambió es el título de la ventana larga, que al aplicar la recomendada 11 del curador pasó de «59× la muestra» a «61× la muestra sellada (14.618 / 238)», con el denominador saliendo de los marcadores `{{larga_n}}` y `{{n}}` del árbitro (bitácora 15 §9.2, entrada de las 10:34:54; `dictamen_15/curador_cierre.md`, recomendada 11).» No exige correr nada. Aplicado esto, **APROBADO PARA COMMIT**.

## Lo que no pudo verificar

Las dos suites de la noche (worktree y árbol real) las tomó de sus archivos por nombre y tamaño; el cuerpo sellado de `regla_58.md` y el de `sello_no_verificable.diff` los verificó por hash y alcance, no afirmación por afirmación; las líneas nuevas de `data/sonda_cierre.csv` y `data/backups/sello_dinero.csv` no las leyó (acta §91.3; mtimes de los timers); y la conducta real de hoy a las 18:15, 18:40 y 19:00, que ningún test puede dar: el diff rige hoy aunque no se commitee.

**Hora de cierre: 10:56:11 del 30-sep-2026.**

## Qué hizo el orquestador (nota del orquestador)

E1 aplicada a las 10:57 con el texto exacto. Ninguna otra edición después del dictamen salvo la sección 9.5 de la bitácora y la nota del acta §92.10.
