# Cierre de la corrida 11: revisión de alcance del `director-programa` y dictamen del `guardian-constitucion`

**8-sep-2026, 01:50 hora de Chile aprox. Textos de los agentes, archivados por el orquestador sin
editar el contenido (sólo formato). Lo que se corrigió en la misma corrida va marcado.**

## Director-programa: nada se revierte en bloque; tres correcciones y un gate sin cerrar

Los cuatro protegidos tienen mtime anterior a la corrida. En alcance y se quedan: el simulador del
instrumento, `intervalo_coherencia.py`, `cobertura_causal.py`, la reconstrucción, el parche del
guardia (no aplicado), el README (sólo método).

- `tests/test_razones_xfail.py`: no se revierte; era objeción de prioridad, no de legitimidad; el
  encargo lo pedía y cazó una razón podrida real. Deja una norma nueva (todo xfail exige predicado),
  que quede anotada como norma. *(Anotada en la bitácora.)*
- `api/main.py` y `api/CONTRATO.md`: en alcance. Sacar la frase «y una ventaja así no es plausible
  con datos públicos» de la nota de potencia, que es juicio editorial saliendo por una API.
  *(Corregido: la nota remite al pre-registro §2.1.)*
- `frontend/src/vistas/RielDinero.tsx`: publicaba «mínimo de 1 USD» (hoy 0,35) y una tabla de
  comisiones de una semilla sin la banda de 20. *(Corregido: el mínimo se lee del artefacto y la banda
  entre semillas va debajo de la tabla.)*
- `dinero/reglas.json`: en alcance; los umbrales bajaron por su regla y el riel tiene cero filas
  selladas. Con una sola semana prospectiva sellada sería mover la vara.
- `cierres_congelados_dia2.csv`: se queda; su `meta.json` decía «segundo día de censo» a secas.
  *(Corregido el motivo: misma sesión, no cuenta.)*
- `cuenta_papel.md` se contradecía (§1b mide con 20 semillas y §3 decía «sigue sin medirse»).
  *(Corregido en el generador y regenerado.)*
- Las exigencias del adversario aplicadas en la misma corrida son legítimas; dos reservas impresas:
  el brazo A1 se agregó después de ver el resultado, y las cifras re-corridas no volvieron a pasar por
  el adversario. Los dictámenes no existían como archivo. *(Archivados en `dictamen_11/`.)*
- Bloqueante: el acta §83.3 afirmaba que el dictamen del auditor estaba en la bitácora y no estaba.
  *(Llegó y está en la bitácora y en `dictamen_11/auditor_lookahead.md`.)*

Las dos no acatadas del pre-mortem se sostienen (la 3 nunca ató; la 12 se retira como objeción de
alcance y se mantiene como ranking). Mueve la aguja: bloque 1 (negativo sobre el propio instrumento),
bloque 4 (destraba la decisión del README), bloques 2+3 (cobertura causal 0 → 84,5 %). No mueve:
bloques 9, 10 día 2, 7, API/frontend, 6. Saldo de gobernanza negativo: seis firmas ejecutadas, cinco
nuevas abiertas.

## Guardián de la constitución: OBSERVADO, ningún rechazo

Cumple con evidencia ejecutada: archivos intocables idénticos a HEAD por sha256 (`motor.py`,
`senales.py`, `snapshot.py`, `universo.py`, y también `version.py`, `calendarios.py`, `alertas.py`,
`noticias.py`, `mki_vigia.py`); parche del guardia NO aplicado con test y en `espera_firma` §49;
`senales.db` con mtime 7-sep 18:15 y 0 sentencias de escritura en las líneas agregadas; ningún push
(último push 00:32:59, antes del arranque); rama `main`; `.env` fuera del diff; `modo.py` → titular;
README sin ninguna cifra movida; `cifras.reintroducciones()` 0 hallazgos en líneas agregadas;
`reglas.json` no viola nada (riel simulado, cero filas selladas, cambio ordenado por el encargo,
marcado PROPUESTA, derivados por su regla, §40 declarado sin firma); nada se firmó; registro de
intentos intacto; «confianza» ausente.

Observaciones: (1) no había verde de cierre en la bitácora *(corregido: la suite final con el árbol
quieto está en la bitácora)*; (2) el dictamen del auditor se declaraba existente y no existía
*(corregido)*; (3) `GEMELO/cifras_retiradas.md` no cubría «27 % / 57 %» ni «σ 2,54» *(corregido: dos
patrones nuevos, pensados en su conjugación)*; (4) la errata del 295 del §82.2 conviene al lado de la
cifra *(corregido: nota fechada en el §82.2)*. No verificado: permisos 600 de `.env` (el sandbox
denegó `stat`).
