# Manual de agentes de MKI Terminal (bundle v2, 2-sep-2026)

Los agentes viven en `.claude/agents/`, las skills en `.claude/skills/`, las
reglas por ruta en `.claude/rules/`, los hooks en `.claude/hooks/` y la suite
de regresión de agentes en `.claude/tests-agentes/`. **Techo: ocho agentes.**
Un agente cuesta fichas en cada sesión por su `description`; una skill cuesta
cero hasta que se invoca. Por eso lo que es procedimiento (escribir un acta,
correr el gate, cerrar la sesión) es skill, y lo que es juicio (dictaminar,
auditar, orientar) es agente.

Todos los agentes de rigor son de **solo lectura**: devuelven un dictamen, no
tocan el árbol. El único que escribe es `ingeniero-plataforma` (plataforma y
entorno, nunca el modelo), desde que el escriba se retiró. Ningún agente cambia el modo de emisión, toca timers, edita `.env`,
pushea ni reescribe una fila sellada: eso es de Nicolás, y el hook
`guardia-reglas.py` lo bloquea aunque el agente lo olvide.

## Los ocho

| agente | modelo | herramientas | cuándo se invoca |
|---|---|---|---|
| `orientador` | sonnet | lectura + Bash | al abrir sesión, al retomar, «dónde quedamos» |
| `director-programa` | opus | lectura (sin Bash) | antes de abrir un frente, para elegir entre dos cosas, y en **modo pre-mortem** sobre todo encargo antes de ejecutarlo |
| `guardian-constitucion` | opus | lectura + Bash | al cerrar cualquier tanda, antes de proponer un commit |
| `estadistico-adversario` | opus | lectura + Bash | antes de aceptar cualquier cifra, y para V1–V7 y R1–R3 |
| `auditor-lookahead` | opus | lectura + Bash | antes de aceptar una feature, una fuente de datos o una cifra de acierto |
| `curador-epistemico` | opus | lectura + Bash | **nuevo**: antes de cerrar una corrida y antes de que un documento salga del repo |
| `integridad-datos` | sonnet | lectura + Bash | antes y después de tocar bases; «cuántos sellos hay» |
| `ingeniero-plataforma` | sonnet | lectura + escritura + Bash | systemd, timers, WSL, venv, logs, vigía, modo de emisión |

Fuera del techo, como skills: `/acta-decision` (antes el agente
`escriba-decisiones`), `/cierre-sesion`, `/cifras-canonicas`,
`/estadistica-evaluacion`, `/gate`, `/modo-emision`.

## Qué cambió en el bundle v2 y por qué

Cada parche del 2-sep-2026 nace de un incidente concreto de las corridas 06
a 08. El texto viejo de cada agente se conserva; el parche va al final bajo
«Mandato ampliado (2-sep-2026)». Donde el texto viejo contradecía al parche,
quedó tachado con la nota «derogado 2-sep, ver abajo».

| agente | parche | lección que lo originó |
|---|---|---|
| `curador-epistemico` (nuevo) | exige etiqueta evidencial (MEDIDO, PROPUESTA, REFUTADO, RETIRADO, DECISIÓN PENDIENTE) en cada oración de un documento público, y que la prosa no diga más que la cifra del árbitro | en agosto el README llamó «hallazgo central» al decaimiento del efecto con la distancia: una curva de cuatro puntos que circuló como hecho y que Hong Kong e India refutaron en la octava corrida. El adversario juzgaba cifras y el guardián reglas; nadie juzgaba frases |
| `guardian-constitucion` | reglas 10 a 14: cifras retiradas también en `.py`; corrección al ejecutable antes que al texto; etiquetas y n e intervalo en todo número nuevo; parches a archivos protegidos sólo como `.diff` con test y en `espera_firma.md`; un supuesto no reemplaza un cómputo | corrida 08: la justificación retractada seguía impresa por tres ejecutables (O1); una rama de `calibracion.py` contaba un supuesto como resultado (O2, A3) |
| `estadistico-adversario` | análisis dimensional obligatorio; verdad conocida antes que observada (simulador); distribución de k bajo la nula; clúster siempre; cantidades no ordenables; conteo de intentos; fuera de muestra con pre-registro fechado | corrida 08: Sharpe anualizado en varianza por período (el DSR aprobaba el 25 % de las réplicas bajo la nula); «0 de 192» que la nula produce el 75 % de las veces; iid que cubre 0,69; el MDE contra el observado que el diseño no ordena, dos veces |
| `auditor-lookahead` | fugas que no son de tiempo: disponibilidad, calendario, por el propio modelo, por el analista | 28-ago: Yahoo retiró la sesión y una verificación tardía no la reproduce; condiciones «predictoras» que eran β por el movimiento del SOX |
| `director-programa` | modo pre-mortem del encargo; urgencia contra ambición | «ejecutá la 5.1 con los criterios congelados» cuando el gatillo es uno de ellos; «afirmá que el efecto cae bajo el MDE»; el backlog del 31-ago con los dos órdenes casi inversos. Además se derogó su párrafo sobre el decaimiento como «hallazgo central» (refutado, Frente B) |
| `orientador` | cinco líneas leídas de la máquina: rama del efecto con n e intervalo, intentos del DSR, verdes de la última suite, cifras retiradas del mes, lo que espera firma con días de espera | corrida 08: el encargo citaba 86 intentos y la máquina decía 100; la rama del efecto está indeterminada por un factor ~5 |
| `integridad-datos` | deriva de fuente: disponibilidad, valores, filas por sello atrasado, respaldo probado | 28-ago; las 25 filas de `snapshot.py:140`; un backup nunca restaurado no es un backup |
| `ingeniero-plataforma` | duplicidad de emisores; ventana de sellado 17:50 a 20:30 | el Mac no se puede mirar desde acá; la suite satura CPU y `mki-noticias` tiene dos minutos de margen |
| `escriba-decisiones` → `/acta-decision` | el cuerpo entero del agente (estilo de la casa, cuatro formatos, pre-registro, dónde se escribe) se fusionó en la skill; el agente se borró | costo de fichas por sesión; el procedimiento ya vivía en la skill |

Dos parches piden cosas que hoy no existen en la máquina, y se anotó en el
propio agente: el guardián no tiene la herramienta `Agent` (la delegación al
curador la hace el orquestador), y el «número de verdes de la última suite»
no está registrado en ningún artefacto (el orientador lo reporta desde la
bitácora, diciendo que es de documento).

## El hook de arranque y el guardia (propuesta, no instalada)

El encargo pedía que `contexto-mki.sh` imprimiera al arrancar, leídas de la
máquina, la rama del efecto con su cifra, el conteo de intentos del DSR y
cuántos ítems esperan firma; y que `guardia-reglas.py` bloqueara la
reintroducción de una cifra retirada en `.md` y en `.py`. **El hook vigente se
protege a sí mismo** (`settings.json` deniega `Edit` sobre `.claude/hooks/`, y
el harness denegó también la escritura por Bash desde la sesión), así que las
dos versiones nuevas viven en `GEMELO/propuestas/hooks/` como el vigente más
un bloque cada una, sin quitar nada. Las instala Nicolás:

```
bash GEMELO/propuestas/hooks/instalar.sh
```

`tests/test_hooks_propuestos.py` prueba la propuesta como subproceso: nada del
vigente se quita; deniega la cifra retirada en `.py` y en `.md`; deja pasar
con marca de retiro; exime `GEMELO/cifras_retiradas.md` y
`.claude/tests-agentes/`; declara que un `.txt` o un heredoc por Bash no pasan
por el bloque. Con la propuesta instalada, el arranque tarda ~4 s más (el
árbitro computa dos ramas desde `senales.db` en `mode=ro`).

## La suite de regresión de agentes

`.claude/tests-agentes/`: un caso por agente de rigor, cada archivo con el
insumo, el veredicto esperado y el dictamen real pegado debajo con fecha. Los
casos son incidentes reales (unidades del Sharpe, «0 de 192», el MDE, la
cifra retirada en un `.py`, la corrección en prosa, el 28-ago, «ejecutá la
5.1», el «hallazgo central»). Se corre invocando al agente con el insumo
pegado en el prompt y la orden de **no leer el directorio** (contiene el
veredicto esperado). **Un agente que falla su caso no se da por instalado.**
Resultados de la primera corrida en `docs/bitacora_agentes_v2.md`.

## Lo que sigue esperando a Nicolás

- Instalar los hooks propuestos (`instalar.sh`), o rechazarlos.
- Las `description` de `guardian-constitucion` («rama migracion-wsl en el
  PC») y de `ingeniero-plataforma` («el switch está a medias») están
  desactualizadas; el cuerpo de ambos ya dice lo correcto. No se tocaron
  porque el encargo prohibía borrar texto existente.
- `CLAUDE.md` no nombra al `curador-epistemico` en su lista de agentes (el
  encargo pedía dejar intacto el resto del repo).
