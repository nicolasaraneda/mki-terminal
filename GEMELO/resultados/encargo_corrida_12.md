# Encargo corrida 12: cerrar la 11 con el adversario, sellar la primera fila prospectiva del riel de dinero, y conectar la máquina al corredor en papel

**Modelo:** Fable, esfuerzo alto, elegidos al arrancar y sin cambiar a mitad de sesión.

Leé este archivo entero antes de ejecutar nada. Corrida nocturna sin supervisión; Nicolás revisa a la mañana. **Nada se pushea. Nada se opera con dinero. Ninguna orden va a una cuenta real.**

Esta es la corrida más ambiciosa hasta ahora y por eso tiene más condiciones de suspensión que las anteriores. La ambición está en qué se construye: la máquina emitiendo y sellando una decisión del riel de dinero antes de la apertura, la máquina enviando una orden a la cuenta de práctica del corredor y leyendo su propia ejecución sin que nadie toque nada, y una pantalla que muestra las dos cosas con su estatus. La ambición **no** está en qué se afirma: al cierre de esta corrida el proyecto sigue sin ninguna ventaja medida, y lo publica igual.

El orden de los bloques es estricto. Si el tiempo no alcanza, se cierra limpiamente lo abierto y lo restante queda como no iniciado en la bitácora. Un frente a medias sin bitácora es peor que uno no empezado.

---

## 0. Orientación obligatoria

1. `orientador` reconstruye el estado. Orden de lectura: `DECISIONES.md` actas §82 y §83 primero, después `ESTADO.md`, `GEMELO/resultados/estado_epistemico.md`, `GEMELO/resultados/inventario_abierto_2026-09-07.md` (si no existe, anotalo como hallazgo y seguí), `espera_firma.md`, `cola_decisiones.md`, `bitacora_11.md`, `dictamen_11/`, `GEMELO/propuestas/regla_aporte_y_dimensionamiento.md` y `criterio_corredor_prerregistro.md`.
2. **Toda cifra se lee de la máquina**, nunca de memoria ni de este archivo. Si este archivo y la máquina no coinciden, manda la máquina y se anota errata.
3. Suite completa antes de empezar; anotá el número. Si no está en verde, parás y reportás.
4. Ventana de sellado 17:50 a 20:30 hora de Chile: nada pesado, ninguna descarga, ninguna conexión al corredor.
5. El registro de intentos se incrementa por cada hipótesis probada, incluidas las descartadas. Los dos contadores del §82.1 y los dos registros del §82.6 siguen separados.
6. `director-programa` corre en modo pre-mortem sobre este encargo antes del bloque 1 y devuelve la lista de instrucciones que podrían ser ellas mismas el defecto. Ya pasó cinco veces. El orquestador no ejecuta una instrucción marcada sin anotarla.
7. **Chequeo de prerrequisitos, con salida escrita en la bitácora antes del bloque 1:**
   - ¿Está aplicado el parche del §26 con el guardia del §49? Se verifica preguntándole al código (`PLATAFORMA_VERSION` igual a 5.1.0 en `version.py` y `chequear_ancla_temporal` presente en `mki_vigia.py`), no a las actas. Nicolás lo aplicó el 8-sep por la tarde (acta §84); si la máquina dice otra cosa, manda la máquina y **el bloque 3 queda suspendido entero**, y se declara. Verificá además que el primer sello con `plataforma_version = 5.1.0` existe en `snapshots` y anotá su `timestamp_utc` en la bitácora: es el marcador del corte de método del §84.1.
   - ¿Existen credenciales de cuenta de práctica del corredor en el entorno? Se verifica que las variables existan, **sin imprimirlas ni copiarlas a ningún archivo**. Si no existen, el bloque 4 se construye contra réplica grabada y E1 queda como no ejecutado.
   - ¿Responde el gateway del corredor en el puerto declarado? Un intento de conexión de lectura, sin órdenes, con tiempo de espera corto. Si no responde, mismo tratamiento que el punto anterior.

## 1. Límites duros

- **No se tocan `motor.py`, `senales.py`, `snapshot.py`, `universo.py`**, el modo de emisión, `.env` ni los timers. Lo que los necesite se entrega como parche NO aplicado con test, en `GEMELO/propuestas/parches/`, y va a `espera_firma.md`. Un timer nuevo para el riel de dinero es una unidad de systemd **propuesta**, no instalada.
- No se reescribe ninguna fila sellada, de ningún riel.
- Ninguna cifra publicada se mueve sola.
- Ningún estimador puntual sin intervalo computado. Clúster de día siempre que haya más de un ticker por fecha.
- Todo lo nuevo se etiqueta PROPUESTA hasta el dictamen del `estadistico-adversario`, **y el estatus se renderiza en toda pantalla que muestre la cifra**, no sólo en el artefacto.
- Una verificación que usa el mismo mecanismo que produjo la cifra no es verificación.
- La corrección va al ejecutable antes que al texto.
- **No se firma nada.** Lo que necesite decisión que no esté en las actas va a `espera_firma.md`.
- **Ninguna orden a una cuenta que no sea de práctica.** El adaptador del corredor tiene que negarse en código a conectarse a un puerto o cuenta que no sea de práctica, con test que lo demuestre, antes de enviar la primera orden.
- Ninguna credencial en logs, en bitácora, en tests ni en artefactos.
- Nada de código de terceros sin licencia verificada. La única dependencia nueva admitida es la que el bloque 4 declara, y sólo si Nicolás la autorizó en la sección 2.

## 2. Lo que Nicolás dejó decidido para esta corrida

Se ejecuta, no se discute. Si un frente encuentra que una decisión no se sostiene, lo escribe como hallazgo y no la revierte.

Decididas el 8-sep-2026 por la tarde, con las tarjetas de opciones y consecuencias a la vista. `escriba-decisiones` las lleva al acta con la razón de Nicolás donde la escribió; donde no la escribió, el acta dice «eligió la opción con la consecuencia declarada en la tarjeta» y no inventa una razón.

| Decisión | Qué implica |
|---|---|
| D-B: la corrida 12 hace **E0 y E1 en papel**, no E2 | Bloques 3 y 4. Cero dinero real |
| D-C: ruta al corredor **TWS API a través de IB Gateway, librería oficial `ibapi`** | Bloque 4 |
| D-C bis: dependencia `ibapi` **autorizada**, con versión fijada en `requirements.txt` y acta | Bloque 4, punto 7 |
| D-D: coautoría: **el historial NO se reescribe**; la atribución se apaga hacia adelante en la configuración (acto de Nicolás, archivo protegido) | El bloque 7 no existe. Ninguna cita por SHA cambia |
| D-E: **README en inglés como `README.md`**, español íntegro a `README.es.md` | Bloque 6 |
| D-F §43: el período de M2 es **el horizonte pre-registrado de la vara**. Elegido conociendo qué resultado daba cada alternativa; eso va escrito en el acta | Bloque 8 |
| D-F §47: piso por posición **acciones enteras**. `SMH` no cabe y el riel se compara contra él sin poder tomarlo, declarado | Bloques 3 y 8 |
| D-F E0: **N = 40 sesiones** selladas prospectivas cierran E0. Fijado antes de la primera fila; no se mueve | Bloque 3, punto 6 |
| Commit de la corrida 11 hecho: `82f488e` en `main` | Punto de partida; se verifica con `git log` |
| El monto de E2 **no se fija** en esta corrida | Bloque 8, punto 2 |

## 3. Bloque 1 (PRIMERO). El hueco de la corrida 11: el re-dictamen

**Por qué va primero.** En la corrida 11 el adversario dictaminó, se aplicaron sus exigencias, se re-corrió, y las cifras re-corridas nunca volvieron a pasar por él. Las que hoy sirve la API no fueron juzgadas en la forma en que están. Nada de esta corrida publica ni muestra una cifra del riel hasta que esto cierre.

1. `estadistico-adversario` juzga **cada cifra que sirve `api/main.py` del riel de dinero y cada cifra de `bitacora_11.md`** en su estado actual: fricción por juego, cobertura, tamaño y cobertura del instrumento, intervalo de la rama de coherencia. Verdicto por cifra: se sostiene, se sostiene con etiqueta, o se retira.
2. **G3, la contraprueba de la fuga de 1 día por `precios_ref`.** El auditor la demostró a mano (inyectó `fila_m = cierres.iloc[i+1]` en `correr_estrategia` y el gate con dos cortes a dedo no la vio; con 11 cortes la veían 2). Con cortes densos sería un test no determinista, así que se diseña como **prueba de borde**: se elige el corte exactamente en un día en que hay una decisión (se lee de `Libro.decisiones`, no se adivina), se inyecta la fuga por un parámetro del riel y no editando el código a mano, y el test exige `ErrorLookAhead` en ese corte. Es distinta de la contraprueba que ya existe (`test_contraprueba_una_fuga_inyectada_rompe_la_invariancia`, que inyecta por `fabrica_senales`): esa prueba fuga por la señal, G3 prueba fuga por el precio con que se dimensiona. Las dos quedan.
3. **G8, `available_at` por ticker en el `.meta.json` del congelado.** El congelado no es point-in-time (zona ciega Z3 del auditor). Se sella, por ticker, desde cuándo estuvo disponible cada serie en el archivo congelado, en el `.meta.json` de los dos congelados, con test que lo exija para todo congelado nuevo. No se reescribe ningún CSV.
4. Las quince objeciones del pre-mortem de la corrida 11 están respondidas una por una en la bitácora 11; dos quedaron "no acatadas con constancia" (la 3 y la 12). Se verifica que la constancia sigue siendo cierta y no se reabre nada.
5. **El gate, modo diagnóstico.** La contraprueba por `fabrica_senales` ya existe y Nicolás la corrió. Lo que falta es que el gate pueda devolver el mapa completo de cortes rotos en vez del primero (hallazgo 5 de la revisión), como opción, sin cambiar el comportamiento por defecto ni el `raise`.

Salida: `dictamen_12/re_dictamen_corrida_11.md`. Lo que se retire entra a `cifras_retiradas.md` y el hook lo bloquea.

## 4. Bloque 2. Los hallazgos de la revisión del diff que quedaron abiertos

Son seis y están en el traspaso del 8-sep; se reproducen acá para que no dependan de otro archivo.

1. **Estatus en pantalla.** `RielDinero.tsx` muestra cifras PROPUESTA sin marcarlas. Decisión de diseño que **sí** podés tomar porque no mueve cifras: el estatus se lee del artefacto y se renderiza en un componente común para todas las tarjetas. Ninguna tarjeta puede mostrar un número sin estatus al lado; test de frontend que lo exija.
2. **Cuarto tragador de excepciones**: `_comisiones_juego_activo` en `api/main.py` termina en `except Exception: return None`. Se reemplaza por manejo explícito de las excepciones que de verdad ocurren, con registro. Buscá en el mismo pase si hay un quinto: `grep -rn "except Exception" --include=*.py` fuera de `venv/` y listá cada uno con su veredicto.
3. **El comentario del pre-registro cambió sin acta** («antes de esta corrida» a «antes de la primera corrida»). La corrección es correcta; `escriba-decisiones` la registra como errata con fecha.
4. **El nombre del corredor desapareció del código** y quedó «un corredor con acceso desde Chile». Buscá en `dictamen_11/` si el curador lo exigió. Si lo exigió, se escribe la regla y se cumple; si no, el nombre vuelve, porque una perífrasis que evita nombrar la fuente hace más difícil verificarla.
5. Resuelto en el bloque 1, punto 5.
6. **Discrepancia de intervalos, ya explicada en la bitácora 11 y no resuelta en el código:** los dos intervalos de la regla firmada son dos métodos (percentil de día y t de clúster) y el último decimal difiere porque `cifras.py` usa 4.000 réplicas de bootstrap y `bifurcaciones` 10.000 por defecto. Dos módulos que computan la misma cifra con distinto número de réplicas es una cifra que puede moverse sola. Se unifica el número de réplicas en un solo lugar del árbitro, se declara, y se verifica que ninguna cifra publicada cambia más allá del último decimal; si cambia, es errata con fecha. Cada intervalo publicado lleva su método al lado.
7. **El mismo `pd.concat` del `motor_concat.diff`, fuera de `motor.py`.** El pre-commit del 8-sep mostró la advertencia de pandas sobre el orden por defecto al concatenar índices de fechas en `api/main.py` (líneas 666 a 668) y `backtest/baselines.py` (línea 154), además de `motor.py:215`. `motor.py` es protegido y su parche espera prueba de identidad de salida; los otros dos no son protegidos y reciben el mismo tratamiento en esta corrida: `sort` explícito con el valor que reproduce la salida actual, y un test que compare la salida antes y después byte a byte. Si la salida cambia con cualquiera de los dos valores, se para y se anota: eso sería un hallazgo sobre el cálculo, no sobre la advertencia.
8. **Erratas de versión que dejó el bump a 5.1.0** (acta §84.3): `.claude/rules/plataforma.md:26` y `.claude/agents/ingeniero-plataforma.md:52` dicen que 5.0.3 quedó congelada al sellar la primera fila; se corrigen con nota fechada que remita al §84, sin borrar la historia. `scripts/ensayo_replica.py:78` lleva `"5.0.3"` en duro: se verifica si es un dato de ensayo (se deja y se comenta) o una comparación contra la versión viva (se lee de `version.py`).
9. **Errata del `snapshot140.diff`, para la bitácora y para el método de los parches.** El diff aplicaba limpio y sus 6 tests sobre copias pasaban, pero al aplicarse al archivo real hizo fallar `test_el_camino_de_sellado_no_importa_GEMELO` por dos líneas de comentario que citaban rutas de `GEMELO/`. Nicolás lo corrigió a mano el 8-sep antes del commit. Lección que se escribe en `docs/manual-agentes.md` o donde viva el procedimiento de parches: todo parche no aplicado a un archivo protegido se prueba también aplicándolo sobre una copia del árbol entero y corriendo la suite completa contra esa copia, no sólo sus propios tests. Si existe una forma barata de automatizarlo (un test que aplique cada `.diff` de `GEMELO/propuestas/parches/` sobre un `git worktree` temporal y corra los tests de aislamiento), se propone; no se instala sin firma.

## 5. Bloque 3. E0: la primera fila sellada prospectiva del riel de dinero

**Condición de entrada:** parche del §26 y guardia del §49 aplicados (chequeo del punto 0.7). Si no, este bloque no arranca y se declara.

E0, según la regla de aporte: la máquina emite una decisión del riel de dinero antes de la apertura del mercado objetivo y la sella, con tamaño nominal cero.

1. **Módulo propio**, `dinero/sello_dinero.py` o el nombre que el auditor prefiera, **fuera de `snapshot.py`**. Su propia tabla en la base, con las mismas propiedades del riel de medición: marca de tiempo puesta por la máquina, `available_at` que registre cuándo la fila se hizo pública, hash del insumo, `plataforma_version`, y ninguna fila reescribible después de sellada. Reusá lo que se pueda importar sin tocar los protegidos.
2. **Qué se sella:** para cada instrumento del universo operable bajo el piso decidido en D-F, la decisión del juego (comprar, vender, nada) y el tamaño nominal cero, con el insumo exacto con que se decidió. La decisión sale de `cuenta_papel` con `hasta` igual a la fecha de sello, es decir por el mismo camino que pasó el gate.
3. **`auditor-lookahead` antes del primer sello.** Exige por cada campo que su valor en t no cambie si se borra el futuro. Sin dictamen no se sella.
4. **El primer sello se ejecuta a mano en esta corrida**, fuera de la ventana y antes de la apertura del mercado objetivo, y se verifica que la fila quedó con `available_at` distinto del reloj de pared. Si la corrida cae en día sin sesión, se sella igual con la marca de que no hay sesión, porque el sellador tiene que saber decir eso.
5. **El timer** para que esto corra todas las noches se entrega como unidad de systemd propuesta en `GEMELO/propuestas/systemd/`, con su hora argumentada respecto de la ventana de sellado y de la apertura de NYSE en hora de Chile, y va a `espera_firma.md`. No se instala.
6. N, el número de filas que cierra E0, queda escrito en `regla_aporte_y_dimensionamiento.md` con la fecha, tal como Nicolás lo decidió. El contador de filas selladas del riel se publica desde el primer día, aunque sea 1.

## 6. Bloque 4. E1: la máquina envía una orden a la cuenta de práctica y lee su propia ejecución

**Condición de entrada:** credenciales y gateway respondiendo (punto 0.7). Si falta cualquiera, el adaptador se construye contra una réplica grabada de respuestas del corredor, se testea contra ella, y E1 queda como **no ejecutado**, no como fallido.

Condición de salida de E1, copiada de la regla de aporte y no reinterpretada: la máquina envía una orden y lee su propia ejecución en el mismo ciclo, sin intervención, y el registro leído coincide con el reporte oficial de la cuenta de práctica.

1. **Antes de escribir una línea:** verificá contra la documentación oficial del corredor, no contra blogs ni repositorios de terceros, cómo se conecta la ruta decidida en D-C a la cuenta de práctica, qué puerto usa, cómo se identifica una cuenta de práctica frente a una real, y qué campos devuelve una ejecución. Anotá las URL consultadas y la fecha en la bitácora.
2. **Adaptador** en `corredor/ibkr.py` (o nombre equivalente), con una interfaz mínima: conectar, enviar orden con SmartRouting (las órdenes dirigidas por API pierden Tiered; está verificado en el criterio de corredor), leer estado de orden, leer ejecuciones, leer posiciones y efectivo, desconectar. **Guardia de papel:** el adaptador se niega a conectarse si la cuenta o el puerto no son de práctica, y hay un test que lo demuestra con una cuenta simulada que finge ser real.
3. **La orden:** una sola, del instrumento más barato del universo operable, una acción, orden límite al último precio disponible o de mercado si la documentación lo recomienda para papel. Se registra: identificador de orden, instrumento, cantidad, precio de ejecución y marca de tiempo, leídos por API. Después se cierra la posición con una segunda orden del mismo modo. Dos órdenes, no más.
4. **Conciliación:** el registro leído por API se compara con el reporte oficial de la cuenta de práctica (el que el corredor genera, no el que devuelve la misma llamada). Si coinciden, E1 cumple C2. Si difieren, C2 no está cumplida aunque la llamada responda, y eso es un hallazgo y no un detalle.
5. **Escala:** la cuenta de práctica arranca con un millón simulado. Medí y declará si a esa escala la comisión es visible en el reporte. Si no lo es, E1 sirve para validar el cableado y no para medir fricción, y se escribe así. Reiniciar el capital desde el portal es acto de Nicolás; no lo intentes.
6. **Datos retrasados:** todo dato leído del corredor lleva la marca de retraso que el corredor declara, y la pantalla del bloque 5 lo muestra.
7. Dependencia: si D-C bis la autorizó, se agrega a `requirements.txt` con versión fijada y acta redactada por `escriba-decisiones`; si no, el adaptador y su cambio de `requirements.txt` quedan como parche no aplicado con test contra la réplica grabada.

## 7. Bloque 5. La pantalla: lo que la máquina decidió para la próxima apertura

Es la parte visible de la visión y por eso es donde más fácil es mentir. Regla del bloque: **cada número en pantalla lleva estatus, n donde exista, y fuente**.

1. Vista nueva en el frontend React, servida por `api/main.py`: las decisiones selladas del riel de dinero para la próxima apertura, con hora de sello, hora de apertura objetivo en hora de Chile y cuenta regresiva; el estatus de cada cifra leído del artefacto; el estado del gate de invariancia de la última corrida; y, si E1 corrió, posiciones, efectivo y últimas ejecuciones de la cuenta de práctica con su marca de retraso y la palabra PRÁCTICA visible.
2. Actualización en vivo por el mecanismo más simple que funcione (SSE o sondeo corto); no se agrega dependencia de frontend nueva sin acta.
3. `curador-epistemico` dictamina cada frase fija de la vista. Ninguna frase puede sugerir que existe una ventaja, una oportunidad rentable o un resultado. La palabra «oportunidad» no aparece salvo con el estatus al lado.
4. Test de frontend que falle si un componente muestra una cifra del riel sin estatus.

## 8. Bloque 6. README en inglés, generado por el árbitro

Decisión D-E. `README.md` pasa a inglés como portada, el actual se conserva íntegro como `README.es.md`.

1. El README inglés **se genera por la misma plantilla que el español**: cada cifra viene del árbitro, ninguna se escribe a mano. Nicolás dejó un borrador en `README_en_borrador.md` con marcadores `{{...}}` donde van las cifras; el borrador es la estructura y el tono, no la fuente de ningún número.
2. Los negativos se publican en inglés con la misma firmeza que en español: la ventaja sellada no distinguible de cero con su intervalo de clúster, la no capturabilidad, el riel de dinero sin ninguna afirmación positiva en pie.
3. `curador-epistemico` dictamina cada frase; `estadistico-adversario` verifica que cada cifra del inglés sea idéntica a la del español y a la del árbitro. Una traducción que redondea distinto es una cifra movida.
4. Enlaces internos que apuntaban a `README.md` esperando español: se revisan uno por uno.
5. `README.es.md` no se toca salvo el enlace cruzado en la primera línea.

## 9. Bloque 7. No existe

D-D decidió no reescribir el historial. Ninguna cita por SHA cambia. Si algún frente encuentra una cita por SHA que no resuelve con `git show`, eso es una errata vieja y se anota, pero no es de esta corrida.

## 10. Bloque 8. Las firmas §43 y §47, aplicadas

1. **§43**: el período de M2 es el horizonte pre-registrado de la vara. Primero se verifica si la vara tiene horizonte escrito en `dinero/preregistro_dinero.md`; si no lo tiene, la decisión no es aplicable todavía, se escribe eso en `espera_firma.md` con la pregunta exacta que falta, y no se elige un horizonte por cuenta propia. Si lo tiene, `escriba-decisiones` redacta el acta con la frase explícita de que la elección se hizo conociendo qué resultado daba cada alternativa (a 52 semanas ningún juego cruzaba el 25 %; a 156 el medio cruza y el juego por defecto no; cifras de la bitácora 11, verificar contra el artefacto), y `estadistico-adversario` dictamina si eso invalida M2 como vara pre-registrada o sólo obliga a declararlo. Se recomputa si M2 dispara en cada juego con la definición firmada y se publica con estatus.
2. **§47**: piso por posición acciones enteras, N de E0 igual a 40. Se aplican al universo operable, a `reglas.json` si el censo por presupuesto lo requiere (PROPUESTA hasta el adversario) y a `regla_aporte_y_dimensionamiento.md`, con fecha. El monto de E2 **no se fija** en esta corrida. `SMH` queda fuera por el piso: el README y la vista lo dicen en una frase, y la comparación contra `SMH` sigue existiendo como línea base sin posición.

## 11. Lo que esta corrida NO hace

- No envía ninguna orden a una cuenta que no sea de práctica, y no fondea nada.
- No aplica parches a archivos protegidos ni instala timers.
- No afirma, en ningún idioma ni pantalla, que exista una ventaja, una oportunidad rentable o un retorno esperado.
- No cablea `filtrar_sesion_coherente` al árbitro (§46 sigue esperando firma).
- No fija el monto de E2 ni toca nada del capital de terceros (§82.7).
- No firma el `motor_concat.diff`.
- No agrega fuentes de datos nuevas fuera de la lectura de la cuenta de práctica.
- No descarga nada en la ventana de sellado.

## 12. Cierre

1. `GEMELO/resultados/bitacora_12.md` por bloque: qué se hizo, qué se encontró con n e intervalo, qué dictaminó el adversario, qué quedó abierto, **errores propios detectados**, y las URL oficiales consultadas para el corredor.
2. `estado_epistemico.md` sólo con afirmaciones que pasaron por el adversario. El riel de dinero entra con su contador de filas selladas prospectivas y su estado E0/E1.
3. `espera_firma.md` y `cola_decisiones.md` actualizados sin borrar lo que sigue esperando. Lo cerrado se marca cerrado con fecha.
4. Nuevo conteo de intentos, con los dos contadores separados.
5. Acta en `DECISIONES.md`, en la sección siguiente a la última (la §84 es del 8-sep por la tarde: parche del §26 aplicado y las siete decisiones de la sección 2).
6. `ESTADO.md` dentro de sus 50 líneas, con el estado E0/E1 en una línea.
7. `guardian-constitucion` dictamina el diff completo; `director-programa` revisa alcance y revierte lo que se salió.
8. Suite completa en verde con el número final. Un bloque que la deje en rojo se revierte y se documenta.
9. Ninguna credencial en el diff. Verificalo con el escaneo de secretos del pre-commit antes de cerrar.
10. **No hagas push.**

## 13. Prioridad si el tiempo no alcanza

Bloque 1 siempre: es la deuda con el adversario y sin él nada de lo demás se puede mostrar. Después el 3, porque una fila sellada prospectiva es lo único que más cómputo no fabrica. Después el 4 y el 5 juntos, porque la pantalla sin la cuenta es decorado. El 6 es barato y se hace si queda una hora. El 2 y el 8 se reparten donde quepan. El 7 no existe.

Si una instrucción de este encargo te parece que es ella misma el defecto, no la ejecutes: anotala en la bitácora con la razón y seguí. La capa que caza esos errores no se relaja para cumplir el encargo.
