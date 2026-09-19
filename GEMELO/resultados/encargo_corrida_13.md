# Encargo corrida 13: cerrar las fugas que E0 mostró en nueve noches, medir a qué hora existe el cierre, y hacer el README en inglés desde el árbitro

**Modelo:** Fable, esfuerzo alto, elegidos al arrancar y sin cambiar a mitad de sesión.

Leé este archivo entero antes de ejecutar nada. Corrida nocturna sin supervisión; Nicolás revisa a la mañana. **Nada se pushea. Nada se opera. Ninguna orden a ninguna cuenta. No se corre el sellador real (`python -m dinero.sello_dinero --sellar`) bajo ninguna circunstancia: E0 está en producción y lo corre el timer.**

E0 lleva nueve sesiones selladas sin intervención humana y la máquina dice contador 7 de 40 (se verifica en el punto 0.7; si la base dice otra cosa, manda la base). Esta corrida no agrega ninguna afirmación sobre ventaja, y sí cierra lo que esas nueve noches mostraron: una fuga de integridad en el sellador, una hora de sello que sigue siendo marginal, y un README que todavía no existe en inglés.

El orden de los bloques es estricto. Lo que no alcance queda como no iniciado en la bitácora, no a medias.

---

## 0. Orientación obligatoria

1. `orientador` reconstruye el estado. Orden de lectura: `DECISIONES.md` actas §85 y §86 primero (la §86 es del 9-sep a la noche y trae las firmas §51, §52, §53 y §57 con las razones de Nicolás), `ESTADO.md`, `GEMELO/resultados/estado_epistemico.md`, `espera_firma.md`, `cola_decisiones.md`, `bitacora_12.md`, `dictamen_12/`, `revision_corrida_12_2026-09-09.md` si está en el repo (si no, sus hallazgos están reproducidos en el bloque 2).
2. **Toda cifra se lee de la máquina**, nunca de memoria ni de este archivo. Si este archivo y la máquina no coinciden, manda la máquina y se anota errata. Este archivo lo escribió el asistente desde salidas de terminal pegadas en un chat; ya pasó dos veces que un encargo traía premisas falsas (corrida 12, bloque 6).
3. Suite completa antes de empezar; anotá el número. En `490f984` fueron 856 en verde, 4 saltados, 1 xfail. Si no está en verde, parás y reportás.
4. Ventana de sellado del riel de medición 17:50 a 20:30 hora de Chile: nada pesado. **Ventana del sellador de dinero: el timer `mki-sello-dinero.timer` dispara Mon..Fri a las 23:30 America/New_York (00:30 Chile en esta época) e importa `dinero/sello_dinero.py` tal como esté en disco en ese instante.** Regla dura: entre las 00:00 y las 01:00 hora de Chile no se modifica ningún archivo de `dinero/` ni se corre nada que abra `dinero/sello_dinero.db`. El orquestador consulta el reloj antes de tocar `dinero/`; si la corrida se lanza en fin de semana no hay disparo hasta el martes 00:30 Chile, pero la regla se cumple igual.
5. El registro de intentos se incrementa por cada hipótesis probada, incluidas las descartadas. Los contadores y registros siguen separados como en §82.
6. `director-programa` corre en modo pre-mortem sobre este encargo antes del bloque 1 y devuelve la lista de instrucciones que podrían ser ellas mismas el defecto. El orquestador no ejecuta una instrucción marcada sin anotarla.
7. **Chequeo de prerrequisitos, con salida escrita en la bitácora antes del bloque 1:**
   - Estado de E0 leído de `dinero/sello_dinero.db`: filas por `fecha_insumo`, `estado` y `cuenta_para_N`; contador `COUNT(DISTINCT fecha_insumo) WHERE cuenta_para_N = 1`; contenido de `divergencias_sello`. Se copia textual a la bitácora. Nicolás vio el 19-sep: cuentan 08, 10, 11, 14, 15, 16 y 17 de septiembre; no cuentan 09 y 18 por `insumo_incompleto`; una divergencia (09); contador 7. Si difiere, manda la base.
   - `git status --short`: se esperan sólo `data/backups/sello_dinero.csv` modificado y extensiones `??` en `dinero/datos/sello/` y `data/backups/sello_dinero_ext/`. Cualquier otro archivo modificado se anota y **no se toca**.
   - ¿Existe `README_en_borrador.md` en la raíz del repo? Nicolás tiene que copiarlo desde Downloads antes de lanzar. Si no existe, el bloque 5 se hace **sin borrador**: el generador y los guardias sí, el texto en inglés queda como no iniciado, y se declara. No se inventa un borrador.
   - ¿Existe generador de README? En la corrida 12 se verificó que **no**: `README.md` es texto a mano. Se re-verifica con `grep -rn "README" --include=*.py` fuera de `venv/` y se anota.

## 1. Límites duros

- **No se tocan `motor.py`, `senales.py`, `snapshot.py`, `universo.py`**, el modo de emisión, `.env`, los timers instalados ni `systemd/`. Lo que los necesite se entrega como parche NO aplicado con test en `GEMELO/propuestas/parches/` y va a `espera_firma.md`. Unidades de systemd nuevas van a `GEMELO/propuestas/systemd/` como propuesta; instalarlas es acto de Nicolás.
- **`dinero/sello_dinero.py` no es protegido, pero está en producción.** Todo cambio se desarrolla y prueba primero en un `git worktree` temporal con la suite completa contra esa copia (el método del `test_parches_en_worktree.py` propuesto en la corrida 12, se use o no ese archivo), y recién después se aplica al árbol real, fuera de la ventana del punto 0.4. Ningún cambio al sellador puede alterar una fila ya sellada ni el valor de `cuenta_para_N` de ninguna sesión pasada: test que compare la base antes y después byte a byte.
- No se reescribe ninguna fila sellada, de ningún riel. No se corre el sellador real. Los tests del sellador usan una base propia temporal, nunca `dinero/sello_dinero.db`.
- Ninguna cifra publicada se mueve sola. Ningún estimador puntual sin intervalo. Todo lo nuevo se etiqueta PROPUESTA hasta el dictamen del `estadistico-adversario`, con el estatus renderizado donde se muestre.
- Una verificación que usa el mismo mecanismo que produjo la cifra no es verificación.
- **No se firma nada.** Lo que necesite decisión va a `espera_firma.md` con tarjeta de opciones y consecuencias.
- Ninguna credencial en logs, bitácora, tests ni artefactos. Ninguna dependencia nueva.
- No se descarga nada de yfinance en la ventana de sellado del riel de medición; la sonda del bloque 3 se construye y se prueba contra datos grabados, y su primera corrida real la decide Nicolás al instalarla.

## 2. Lo que Nicolás dejó decidido (acta §86 del 9-sep, y confirmación del 19-sep)

Se ejecuta, no se discute. Si un frente encuentra que una decisión no se sostiene, lo escribe como hallazgo y no la revierte.

| Decisión | Qué implica |
|---|---|
| §85.9: las seis normas del director del §85.8 bis están aceptadas | Son normas del proyecto; nada las relaja |
| §57: cuenta para N sólo la fila `pendiente` con insumo fresco y completo; sesiones perdidas no se recuperan | El bloque 3 **no** cambia esta definición. Lo que mide va a una tarjeta nueva |
| §51: E0 sigue sellando el sorteo sin información etiquetado hasta N = 40 | No se toca la señal del sellador |
| §52: monto de E2 = 500 USD, E1 completo antes, E2 sólo con vara; cambios sólo por acta antes de E2 | El bloque 6 produce la tabla para esa reevaluación; no fija nada |
| §53: timer del sellador a Mon..Fri 23:30 America/New_York, instalado y commiteado | No se cambia la hora. El bloque 3 produce el dato para decidirla con acta |
| Hallazgo 2 de la revisión, extensiones en `dinero/datos/sello/`: **opción (a), una línea de `.gitignore`**, `data/backups/` queda como única copia versionada | Bloque 4, punto 3. **Pendiente de confirmación explícita de Nicolás en el chat; si al lanzar esta línea sigue diciendo «pendiente», el punto 4.3 no se ejecuta y se anota** |
| La restauración de `dinero/datos/sello/ext_2026-09-09.{csv,meta.json}` a su versión sellada la hizo Nicolás el 19-sep con `git checkout` (sha `126e4f…`, igual al de la base) | Punto de partida del bloque 1; se verifica, no se repite |

## 3. Bloque 1 (PRIMERO). La fuga de integridad que E4 dejó: el archivo en disco

**Qué pasó, leído de la máquina el 19-sep.** El 10-sep a las 00:30 Chile el timer disparó sobre la sesión del 9-sep ya sellada, con un insumo distinto (ya traía el cierre del día). El guardia E4 hizo lo correcto con la base: registró una fila en `divergencias_sello` y no insertó nada. Pero **sobreescribió `dinero/datos/sello/ext_2026-09-09.csv` y su `.meta.json`** con el insumo nuevo: el sha del archivo en disco pasó a `7300787b…` mientras las filas selladas citan `126e4f2c…`. La evidencia sobrevivió porque el sha está en la base y el archivo original en git, pero el árbol quedó inconsistente nueve días. Es una fuga: la escritura del archivo de extensión ocurre antes o al margen del chequeo de E4.

1. `auditor-lookahead` reproduce la fuga en un test con base temporal: sellar una sesión, volver a llamar al sellador el mismo día con un insumo distinto, y exigir que **ni la base ni ningún archivo de `dinero/datos/sello/` de esa sesión cambien** (comparación de sha antes y después). Hoy ese test tiene que fallar; se escribe primero.
2. Corrección en el sellador: cuando E4 detecta segundo sello con otro insumo, no escribe ninguna extensión ni meta de esa fecha. Si el diseño exige guardar el insumo divergente, va a un archivo con nombre distinto (por ejemplo sufijo `_divergente_<timestamp>`) y la fila de `divergencias_sello` lo cita. No se elige a ciegas: el auditor dictamina cuál de las dos y por qué.
3. **Test de integridad permanente:** para cada `fecha_insumo` sellada, el sha256 de `dinero/datos/sello/ext_<fecha>.csv` es igual al `insumo_ext_sha256` de sus filas. Corre en la suite. Hoy, con la restauración de Nicolás, tiene que pasar; si no pasa para alguna fecha, se para y se reporta, no se «arregla» el archivo.
4. Mismo test sobre `data/backups/sello_dinero_ext/` si el export copia la extensión ahí; si el export escribe otra cosa, se documenta qué.
5. Método del punto 1.2: el cambio se prueba en worktree con la suite completa antes de aplicarse (límite duro), y se aplica fuera de la ventana 00:00 a 01:00 Chile.

Salida: `dictamen_13/auditor_e4_archivo.md`, tests en `tests/test_sello_dinero.py`, bitácora con los sha antes y después.

## 4. Bloque 2. Reintroducciones preexistentes de cifras retiradas (hallazgo 1 de la revisión)

Anotadas por el guardián en la corrida 12, fuera de su alcance entonces: `cifras.py:46` y `:273`, `tests/test_bifurcaciones.py:241` y `:246`, y citas en `DECISIONES.md`, `espera_firma.md` y `cola_decisiones.md`. Los números de línea pueden haberse movido; se buscan por contenido contra `GEMELO/cifras_retiradas.md`.

1. Una por una: ¿es una cita histórica con etiqueta (permitida) o una cifra viva sin etiqueta (reintroducción)? Veredicto por caso en la bitácora.
2. Las reintroducciones se corrigen en el ejecutable primero (`cifras.py`, tests) y después en el texto. Las citas históricas reciben la etiqueta que el escáner de `test_epistemico.py` reconoce, si existe tal etiqueta; si no existe, se propone el patrón y se agrega al escáner con test.
3. `guardian-constitucion` re-dictamina el conjunto al cierre.

## 5. Bloque 3. La sonda: a qué hora existe el cierre en yfinance

**Por qué.** Dos de nueve sesiones no contaron por `insumo_incompleto`: el 9-sep a las 21:00 Chile faltaban 34 de 36 columnas; el 18-sep a las 23:30 de Nueva York faltaba **una sola columna**, y con la definición firmada en §57 una columna alcanza para perder la sesión. La hora se eligió con un argumento que no sobrevivió a la primera noche; la siguiente hora se elige con dato, no con otro argumento.

1. **Primero, el 18-sep:** leer de la base qué ticker quedó sin precio (`precio_ref_usd IS NULL`) y de `ext_2026-09-18.csv` qué columna estaba vacía. Anotarlo. Si es un ADR OTC (como SHECY o TOELY, que el 9-sep fueron los únicos que sí tenían dato a las 21:00), eso es información sobre cómo Yahoo publica por venue y va a la tarjeta.
2. **Sonda** `GEMELO/sonda_cierre.py` (o donde el ingeniero de plataforma prefiera fuera de `dinero/`): para cada ticker del universo operable pide a yfinance los últimos días y registra en `data/sonda_cierre.csv` una fila por ticker y corrida con: timestamp UTC, hora de Nueva York, última fecha con `Close` no nulo, y si esa fecha es la sesión de hoy. **No sella, no toca `dinero/`, no abre `sello_dinero.db`.** Test contra respuestas grabadas (sin red).
3. Unidad de systemd **propuesta** en `GEMELO/propuestas/systemd/mki-sonda-cierre.{service,timer}` con `__MKI_DIR__`, `OnCalendar=Mon..Fri 17..23:00,30 America/New_York` (cada media hora desde las 17:00 hasta las 23:30 hora de Nueva York) y `Persistent=false` (una sonda atrasada no sirve). Se verifica con `systemd-analyze calendar` que la expresión es válida. No se instala.
4. Script de resumen `GEMELO/sonda_cierre_resumen.py` que, con el CSV de varias noches, produzca por ticker la hora mediana y máxima a la que apareció el cierre, y por noche la hora en que estuvieron los 36. Se prueba con un CSV sintético de tres noches.
5. **Tarjeta nueva en `espera_firma.md`, §58**, con el dato del punto 1 y la pregunta exacta: (a) mantener 23:30 NY y §57 tal cual, aceptando las sesiones perdidas que la sonda mida; (b) mover el timer a una hora más tarde que la sonda justifique; (c) redefinir «completo» por ticker (la sesión cuenta y el ticker rezagado queda `sin_dato`), lo que cambia una regla firmada el 9-sep y reinicia o no el contador según lo que Nicolás decida. Consecuencias de cada una escritas. Recomendación del agente etiquetada como tal. No se elige.

## 6. Bloque 4. Bookkeeping que las firmas del §86 dejaron pendiente

1. `espera_firma.md`: §51, §52, §53 y §57 se marcan firmadas con fecha 9-sep y referencia a §86.1 a §86.4, sin borrar el texto. §43 sigue abierta.
2. `cola_decisiones.md`: lo mismo. `ESTADO.md` con el contador de E0 leído de la base en una línea.
3. **Sólo si la sección 2 lo confirma:** una línea en `.gitignore` para `dinero/datos/sello/`, y `git rm --cached` de lo que ya esté rastreado ahí (las extensiones del 08 y 09), con nota en la bitácora de que la copia versionada es `data/backups/sello_dinero_ext/`. El test de integridad del bloque 1 sigue corriendo sobre `dinero/datos/sello/` en disco.
4. `visible_en` en el sellador, zona ciega Z1 del `auditor-lookahead` de la corrida 12: se lee la definición exacta en `dictamen_12/auditor_lookahead_sello_dinero.md`. Si Z1 define qué campo falta y cómo se calcula, se agrega con test, en worktree primero, fuera de la ventana. Si el dictamen no lo define con precisión suficiente, se escribe la pregunta en `espera_firma.md` y no se inventa.
5. Regenerar `GEMELO/resultados/bifurcaciones.md` y `.json` con las 4.000 réplicas unificadas en la corrida 12, y verificar que ninguna cifra publicada cambia más allá del último decimal; si cambia, errata con fecha, no corrección silenciosa.

## 7. Bloque 5. README en inglés, con generador primero

Decisión D-E de la corrida 12, no iniciada entonces por dos premisas falsas del encargo (no había generador; el borrador no estaba en el repo). Esta vez el orden es el correcto: **primero la maquinaria, después el texto.**

1. **Generador**: `scripts/generar_readme.py` (o el nombre que la convención del repo prefiera) que toma una plantilla con marcadores `{{clave}}` y los llena desde `cifras.py`, el árbitro. Toda cifra del README, en cualquier idioma, sale de ahí; ninguna se escribe a mano. Un marcador sin clave en el árbitro rompe la generación con error explícito.
2. **Guardias extendidos a los dos archivos**: `DOCUMENTOS_PUBLICADOS` (o como se llame la lista que hoy cubre `README.md`) incluye `README.md` y `README.es.md`; los escáneres de `test_epistemico.py` corren sobre ambos; la cita por línea que hoy hay en `bifurcaciones.py` (la revisión la ubicó cerca de la línea 99; se busca por contenido) se actualiza si el número de línea cambia. Test que falle si alguno de los dos README tiene una cifra que no está en el árbitro.
3. **`README.es.md`**: el `README.md` actual íntegro, generado por la misma plantilla si es posible sin cambiar ninguna cifra (verificar byte a byte que el texto generado coincide con el actual salvo los marcadores; si no coincide, se para y se anota qué difiere).
4. **`README.md` en inglés**, sólo si `README_en_borrador.md` existe (punto 0.7): el borrador es estructura y tono, no fuente de ningún número. Los negativos con la misma firmeza que en español: la ventaja sellada indistinguible de cero con su intervalo de clúster y su n efectivo, la no capturabilidad, el riel de dinero con su contador de E0 y sin ninguna afirmación positiva. `curador-epistemico` dictamina cada frase; `estadistico-adversario` verifica que cada cifra del inglés sea idéntica a la del español y a la del árbitro. Una traducción que redondea distinto es una cifra movida.
5. Enlaces internos que esperaban español en `README.md`: se revisan uno por uno. Enlace cruzado en la primera línea de cada README.
6. Ni «opportunity», ni «edge», ni «alpha», ni «returns» sin el estatus al lado. El curador tiene la última palabra sobre el vocabulario.

## 8. Bloque 6. Universo operable por presupuesto, con acciones enteras

Para la reevaluación del monto de E2 que el §86.3 prevé por acta antes de E2. **No fija nada.**

1. Tabla `GEMELO/resultados/universo_por_presupuesto.md` y `.json`: para presupuestos de 100 a 500 USD de a 50, cuántos y cuáles tickers del universo operable alcanzan una acción entera al último cierre congelado, cuántas posiciones simultáneas caben, y la fracción de semillas del juego conservador que se congelan a cada presupuesto (la corrida 12 midió 5 de 20 a 500; se verifica ese número contra el artefacto y se extiende).
2. Con estatus PROPUESTA hasta el adversario; intervalo donde haya estimación.
3. Va a `espera_firma.md` como insumo de la reevaluación, no como tarjeta.

## 9. Lo que esta corrida NO hace

- No corre el sellador real ni abre `dinero/sello_dinero.db` para escribir.
- No cambia la hora del timer ni la definición de §57. Produce el dato y la tarjeta.
- No fija ni mueve el monto de E2.
- No instala timers ni unidades de systemd.
- No envía órdenes ni toca el corredor; E1 espera la cuenta y una sesión diurna.
- No afirma, en ningún idioma, que exista una ventaja.
- No cablea §46, no firma el `motor_concat.diff`, no toca §82.7.
- No escribe un borrador de README en inglés si Nicolás no lo dejó.

## 10. Cierre

1. `GEMELO/resultados/bitacora_13.md` por bloque: qué se hizo, qué se encontró con n e intervalo, dictámenes, qué quedó abierto, **errores propios detectados**.
2. `estado_epistemico.md` sólo con afirmaciones que pasaron por el adversario; el contador de E0 leído de la base.
3. `espera_firma.md` y `cola_decisiones.md` actualizados sin borrar lo que sigue esperando; §58 nueva.
4. Conteo de intentos.
5. Acta en `DECISIONES.md` en la sección siguiente a la §86, redactada por `escriba-decisiones` sin firmar nada.
6. `ESTADO.md` dentro de sus 50 líneas.
7. `guardian-constitucion` dictamina el diff completo; `director-programa` revisa alcance y revierte lo que se salió. Si el director instala una norma «de paso», la declara en el acta como en §85.8 bis; aceptarla es acto de Nicolás.
8. Suite completa en verde con el número final. Verificá que el test de integridad del bloque 1 corre y pasa sobre la base real en modo lectura.
9. Escaneo de secretos del pre-commit antes de cerrar. **No hagas push.**
10. Dejá el árbol sin cambios en `dinero/` entre las 00:00 y la 01:00 Chile si la corrida sigue abierta a esa hora.

## 11. Prioridad si el tiempo no alcanza

Bloque 1 siempre: es una fuga en producción. Después el 3, porque cada noche sin sonda es una noche sin dato para decidir la hora. Después el 5, porque es la cara del repo. El 2, el 4 y el 6 se reparten donde quepan; el 4.3 sólo con la confirmación.

Si una instrucción de este encargo te parece que es ella misma el defecto, no la ejecutes: anotala en la bitácora con la razón y seguí.
