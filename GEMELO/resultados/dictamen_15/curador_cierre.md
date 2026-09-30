# Dictamen del `curador-epistemico` al cierre de la corrida 15

> Archivado por el orquestador tal como lo devolvió el agente. Lanzado a las 23:44 del 29-sep,
> muerto por el segundo corte de cuota, retomado a las 10:31 del 30-sep y devuelto a las
> **10:34:54** (hora de `date` del agente). Qué se hizo con cada exigencia está al final.

**DICTAMEN: RECHAZADO (4 bloqueantes).** Textos revisados: `ESTADO.md` (50 líneas), `estado_epistemico.md` (encabezado y bloque «Corrida 15»), `README.md` sección «Execution rail» y badges, `DECISIONES.md` §92, `bitacora_15.md`, `espera_firma.md` (§58, §61 a §65 y §66 a §76), `cola_decisiones.md`, cabecera de `regla_58.md`. Afirmaciones con estatus explícito o inequívoco: la casi totalidad. Palabra «confianza»: sólo en `README.es.md:304`, la frase que la prohíbe. El 39 de `roca_chip` no aparece en ningún README; en `ESTADO.md`, §68 y el estado epistémico va rotulado DESCRIPTIVO sin dictamen. Cabecera de `regla_58.md`: sin defecto; nada va a anexo.

## Bloqueantes

1. `README.md`, viñeta E0 regenerada: «every trading night the machine emits and seals»: la máquina no sella todas las noches (la sesión del 25-sep sin filas, las 33 del 28-sep `no_verificable_timing`). Es frase pública nueva. Texto propuesto por el curador: «on NYSE trading nights the machine emits and seals … Nights are missed: no rows were sealed on 2026-09-25, and the 2026-09-28 rows were sealed out of hours and count for nothing.»
2. `README.md`, viñeta E1: «No practice account and no gateway exist yet»; el acta §91.9 dice «usuario de práctica por activar». Texto propuesto: «No gateway exists yet and no order has ever been sent; the practice user is pending activation (acta §91.9, 2026-09-29).»
3. `bitacora_15.md`: el acta §92.12 declara cuatro errores propios y la bitácora rotula uno. Marcar los tres en su sitio (0.10, sección 7, 1.2) con el texto propuesto.
4. `estado_epistemico.md`, bloque «Corrida 15»: los ítems (ii) y (iii) encabezan «DEMOSTRADO» dentro de una sección de PROPUESTAS y contra la tabla del documento (DEMOSTRADA = verificada por un mecanismo distinto del que la produjo, o por censo). Reemplazos: «MEDIDO y APLICADO (dictamen `auditor-lookahead`: APLICABLE CON EXIGENCIAS)» y «MEDIDO por censo de la base». (iv) CONTESTADO queda.

## Recomendadas

5. `ESTADO.md`: «pausada» → «no corrió … que fuera suspensión y no apagado es INFERENCIA». 6. La holgura de 15 min con sus fechas (2-nov-2026 a 12-mar-2027, MEDIDO). 7. La señal de mañana rotulada «PREDICCIÓN falsable, no medición». 8. La suite con hora. 9. `cola_decisiones.md`: «~250 titulares» sin denominador → «los pendientes pasaron de 260 a 3.672 en 22 días (MEDIDO)». 10. `bitacora_15.md` remite a una «sección 6.5» que no existe. 11. `README.md`: «61× the sample» sin el denominador a la vista → «61× the sealed sample (14,618 / 238)».

## Zonas ciegas declaradas

No abrió bases ni corrió tests (los conteos y huellas los tomó como declarados); no leyó `data/sonda_cierre.csv` ni `.log`; no corrió `modo.py`; no leyó los dictámenes de `dictamen_15/` (juzgó las citas que la bitácora y el acta hacen de ellos); no auditó el cuerpo sellado de `regla_58.md`; los cuatro huecos del acta §92 seguían sin llenar.

## Qué hizo el orquestador (nota del orquestador, 10:39 del 30-sep)

Las cuatro bloqueantes aplicadas. En la 1 se usó una formulación sin fechas, para que la página no se venza sola como el contador que §90.3 retiró: «on NYSE trading nights the machine emits and seals … nights get missed (a paused machine, an incomplete input) and a missed night is never recovered»; la 2 con el texto del curador citando el acta. Las recomendadas 5 a 11 aplicadas todas (la 11 en los dos idiomas, con los marcadores `{{larga_n}}` y `{{n}}` para que el denominador salga del árbitro; el test del cociente se ajustó). README regenerado a las 10:39:01, `--verificar` exit 0, suite completa relanzada.
