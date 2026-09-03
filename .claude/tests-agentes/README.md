# Suite de regresión de agentes

Un caso por agente de rigor, cada uno un archivo con **el insumo** y **el
veredicto esperado**. Los casos salen de incidentes reales de las corridas 06
a 08; el veredicto esperado es lo que el agente debió decir esa vez y no dijo,
o dijo tarde. Un agente que falla su caso **no se da por instalado**: se
corrige el parche de mandato y se repite.

## Cómo se corre un caso

1. Se invoca al agente con el bloque **Insumo** del caso pegado en el prompt,
   con la instrucción de **no leer `.claude/tests-agentes/`** (el archivo
   contiene el veredicto esperado y leerlo contamina la prueba).
2. El dictamen real se pega al final del mismo archivo, bajo «Dictamen real»,
   con fecha, sin editarlo.
3. Se compara contra «Veredicto esperado» y se anota PASA / FALLA en la tabla
   de abajo y en la bitácora de la tanda.

Los insumos hipotéticos (diffs no aplicados, fragmentos de código de una
versión anterior) están marcados como tales dentro del caso; el agente
dictamina sobre el texto que recibe, no sobre el árbol.

## Casos

| caso | agente | incidente | esperado |
|---|---|---|---|
| `adversario-unidades.md` | estadistico-adversario | corrida 08, Frente A3: Sharpe anualizado en varianza por período | RECHAZADO (NO SOSTIENE) por unidades |
| `adversario-192.md` | estadistico-adversario | corrida 08, A2: «0 de 192» sin nula | OBSERVADO (NO CONCLUYENTE), pide la nula |
| `adversario-mde.md` | estadistico-adversario | corridas 05 y 08: «el efecto cae bajo el MDE» | se niega y explica |
| `guardian-retirada.md` | guardian-constitucion | corrida 08, O1: la justificación retractada seguía en tres ejecutables | RECHAZADO |
| `guardian-prosa-primero.md` | guardian-constitucion | corrida 08: corrección al texto sin corregir el módulo | OBSERVADO |
| `auditor-disponibilidad.md` | auditor-lookahead | 28-ago: Yahoo retiró la sesión | distingue «emitido antes» de «reproducible después» |
| `director-premortem.md` | director-programa | «ejecutá la 5.1 con los criterios congelados» | marca la instrucción: el gatillo es un criterio |
| `curador-hallazgo.md` | curador-epistemico | README de agosto: «el hallazgo central» | reetiqueta PROPUESTA y luego REFUTADO con fecha |

Este directorio está **exento** del bloque de cifras retiradas del hook
propuesto (`GEMELO/propuestas/hooks/guardia-reglas.py`): los casos
reintroducen cifras retiradas a propósito para probar al guardián.

## Resultados

Ver la tabla al final de `docs/bitacora_agentes_v2.md` y la sección
«Dictamen real» de cada caso.
