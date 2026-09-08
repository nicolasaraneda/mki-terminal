# Encargo corrida 11 (v2, post acta §82): validar el instrumento, reconstruir sin fuga, y ejecutar seis firmas

**Reemplaza la v1 del 7-sep.** La v1 presuponía tres firmas sin tomar. El acta
**§82** de `DECISIONES.md` tomó seis. Este encargo ejecuta lo que esas firmas
implican y no vuelve a preguntarlas.

Leé este archivo entero antes de ejecutar nada. Corrida nocturna sin
supervisión; Nicolás revisa a la mañana. **Nada se pushea.**

El orden de los bloques es estricto y la razón está escrita en cada uno. Si el
tiempo no alcanza, se cierra limpiamente lo abierto y lo restante queda como no
iniciado en la bitácora. Un frente a medias sin bitácora es peor que uno no
empezado.

---

## 0. Orientación obligatoria

1. `orientador` reconstruye el estado. Orden de lectura: **`DECISIONES.md`
   sección §82 primero**, después `ESTADO.md`,
   `GEMELO/resultados/estado_epistemico.md`,
   `GEMELO/resultados/inventario_abierto_2026-09-07.md`, `espera_firma.md`,
   `cola_decisiones.md`, `bitacora_10.md`, actas §80 y §81, y
   `GEMELO/resultados/dictamen_10/aplicacion.md`.
2. **`espera_firma.md` está desactualizado y lo declara en su primera línea.**
   Los ítems §45, §41, §55, §42, §26 y 2a-ter figuran como pendientes y **están
   firmados**. Manda el acta §82, no la cola.
3. **Toda cifra se lee de la máquina**, nunca de memoria ni de este archivo. Si
   este archivo y la máquina no coinciden, manda la máquina y se anota errata.
4. Suite completa antes de empezar; anotá el número. Si no está en verde, parás.
5. Ventana de sellado 17:50 a 20:30 hora de Chile: nada pesado.
6. El registro de intentos se incrementa por cada hipótesis probada, incluidas
   las descartadas. Recordá el §82.1: el contador de especificaciones y la
   familia de contrastes son dos cosas y ninguna reemplaza a la otra.
7. **`director-programa` corre en modo pre-mortem sobre este encargo antes del
   bloque 1** y devuelve la lista de instrucciones que podrían ser ellas mismas
   el defecto. El orquestador no ejecuta una instrucción marcada sin anotarla.

## 1. Límites duros

- **No se tocan `motor.py`, `senales.py`, `snapshot.py`, `universo.py`**, el
  modo de emisión, `.env` ni los timers. Donde un frente necesite uno de ellos,
  produce un parche **NO aplicado** con su test y lo deja en `espera_firma.md`.
  Esto incluye el parche del §26, que está firmado y **lo aplica Nicolás**.
- No se reescribe ninguna fila sellada.
- Ninguna cifra publicada se mueve sola.
- Ningún estimador puntual sin intervalo computado. Clúster de día siempre que
  haya más de un ticker por fecha.
- Todo lo nuevo se etiqueta PROPUESTA hasta el dictamen del
  `estadistico-adversario`.
- Una verificación que usa el mismo mecanismo que produjo la cifra no es
  verificación.
- La corrección va al ejecutable antes que al texto.
- **No se firma nada.** Si un frente concluye que hace falta una decisión que no
  está en el §82, la escribe en `espera_firma.md` y sigue.

## 2. Lo que el acta §82 dejó decidido

Se ejecuta, no se discute. Si algún frente encuentra que una de estas
decisiones no se sostiene, **lo escribe como hallazgo y no la revierte**.

| Acta | Decisión | Qué implica en esta corrida |
|---|---|---|
| §82.1 | Dos contadores por separado, y el aviso va también donde el 3 se publica | Bloque 7 |
| §82.2 | Parche de `snapshot.py:140` entero: aplicar, bump, guardia, conteo | Bloques 5 y 6. **La aplicación es de Nicolás** |
| §82.3 | Se retiran las 15 filas. Publicación espera al intervalo de clúster | Bloque 4 |
| §82.4 | La cuenta en papel se reconstruye (opción A) | Bloques 2 y 3 |
| §82.5 | Se declara con qué test se computó cada p, sin mover cifras | Bloque 8 |
| §82.6 | Los dos registros de intentos quedan separados. Riel integrador descartado | Nada que ejecutar. Se respeta al contar intentos |

## 3. Bloque 0. Corregir la tarjeta del §42 antes de que nadie la lea

**Primero de todo y cuesta dos minutos.** El acta §82.4 ordena sacar de la
tarjeta del §42, en `espera_firma.md`, la frase que afirma que el signo de la
conclusión ya se sabe que aguanta y que cita el movimiento de 27 % a 57 % en el
juego medio. Esas cifras son de la cuenta con las cuatro fugas y están
retiradas.

Se saca la frase, se deja nota de errata con fecha remitiendo al §82.4, y
**recién después** cualquier frente lee esa tarjeta. Si el bloque 2 la lee
antes, arranca con la respuesta escrita.

## 4. Bloque 1 (PRIMERO de los frentes). La mitad que falta de la calibración

**Por qué va primero.** La regla de la casa es verificar el instrumento contra
una verdad conocida antes de creerle sobre una desconocida. La mitad con
ventaja verdadera igual a cero se corrió. **La mitad con ventaja verdadera
distinta de cero no.** Reconstruir la cuenta antes de esto produce cifras que
no se pueden interpretar.

Corré `GEMELO/simulador/` con ventaja verdadera distinta de cero, en al menos
tres magnitudes declaradas antes de correr, con semilla sellada y número de
réplicas por celda declarado. Reportá por celda la proporción de detección con
su intervalo, y poné la mitad nula en el mismo cuadro.

**Criterio de fallo, escrito antes:** si la tasa de detección bajo ventaja
verdadera no supera a la de falsa detección bajo ventaja nula en ninguna de las
tres magnitudes, el instrumento no discrimina y **el resto de la corrida queda
suspendido**, incluida la reconstrucción. Eso es un resultado, no un fracaso, y
se publica con la misma firmeza que el contrario.

## 5. Bloque 2. Reconstrucción de la cuenta en papel

**Firmada en §82.4, opción A.** El orden lo fijó el `auditor-lookahead` y no se
altera.

1. **El test de truncación primero.** Los tres `xfail(strict=True)` de
   `tests/test_dinero.py` clavan F1, F2 y F4. Cuando se arreglen van a pasar, el
   modo estricto lo va a volver rojo, y eso obliga a sacar el marcador. Es
   intencional.
2. Las correcciones: membresía acotada por fecha (E1), sorteo desde datos
   anteriores a la ventana (E3), retardo de implementación en las **dos** patas
   (E4), sigma del interruptor sin futuro (E5), y cablear `ErrorLookAhead` al
   riel (E6).
3. Recién después republicar.

**No se calcula un solo MAE antes de que el auditor corra.**

**Parámetro de costo:** el de `GEMELO/propuestas/insumo_40_aranceles_ibkr.md`,
no un supuesto. Declarar cuál de las dos columnas se usó, enteras o
fraccionarias, porque cambia el costo por un factor de casi ocho a 250 dólares.

**Advertencia del §82.4:** si la fricción vuelve a dar del orden de la mitad
del capital, el sospechoso principal es el número de operaciones del diseño y
no el arancel. Con 0,70 dólares de ida y vuelta sobre 100 hacen falta del orden
de ochenta idas y vueltas, y el horizonte declarado es de semanas.

## 6. Bloque 3. Cobertura por causalidad de `cuenta_papel.py` y `contabilidad.py`

**Va pegado al bloque 2 y no después.** La suite verde no cubre por causalidad
ninguno de los dos, así que un verde de `pytest` hoy no es evidencia de
ausencia de fuga en ese riel. Reconstruir sin cerrar esto es repetir el error
con código nuevo.

Medí la cobertura por causalidad de los dos módulos **antes y después** de la
reconstrucción, y reportá los dos números. Los caminos que queden sin cubrir se
listan con la razón.

## 7. Bloque 4. El intervalo de clúster del +14,3 pp

**Lo pide el §82.3 y es la condición para publicar.** La rama de coherencia
(`backtest/linea_base.filtrar_sesion_coherente`, n = 223) tiene p exacta pero
no tiene intervalo de clúster de día. Hasta que lo tenga es una consecuencia
declarada y no un argumento.

Computalo con la maquinaria que ya existe: `_grupos_por_dia`, `_bootstrap_dia`,
`_ic_t_cluster`, `_p_permutacion_dia`, `icc_y_deff`. Reportá también ICC, DEFF y
n efectivo de esa rama, y **cuántos días quedan** después del retiro.

**Pregunta pegada, que nadie contestó:** si las 15 filas retiradas constituyen
días de emisión enteros o los dejan mutilados, y si esas fechas estaban entre
los días informativos. Es el dato que decide si el retiro cambia el estadístico
de día o sólo el de fila.

**Predicción escrita antes de calcularlo, del §82.3:** es esperable que el
intervalo contenga el cero, como lo contiene el de la regla firmada. Si no lo
contiene, eso es un hallazgo y merece verificación por segunda ruta.

**Cableado:** `filtrar_sesion_coherente` sigue **sin aplicarse por defecto**
en ningún camino. Esta corrida computa la cifra; el cableado al árbitro es una
decisión aparte que no está firmada.

## 8. Bloque 5. El guardia de la rama del `except` (parche NO aplicado)

**Lo firmó el §82.2 parte (c) y no existe.** El defecto tiene una vía de
escape: en `snapshot.py`, `available_at` arranca valiendo `ts_emision` y sólo se
reemplaza dentro de un `try` cuyo `except` es `pass`. Si esa rama se toma, el
parche aplicado se comporta idéntico al defecto y no deja marca.

Producí el guardia como **parche no aplicado con su test**, en
`GEMELO/propuestas/parches/`, y dejalo en `espera_firma.md` junto al del §26
para que Nicolás aplique los dos en el mismo acto.

El guardia tiene que hacer visible el paso por esa rama: alerta del vigía, marca
en la fila, o test que lo detecte. Cuál de las tres es propuesta tuya, con la
razón.

**El mismo patrón está en `senales.py:317-319`**, donde un fallo del calendario
deja la fila pendiente para siempre en silencio. Miralo en el mismo pase y
decí si corresponde el mismo tratamiento. Son tres tragadores de excepciones en
el camino de sellado y verificación: es un patrón, no tres instancias.

## 9. Bloque 6. Cuántas filas pasaron por esa rama

**Lo firmó el §82.2 parte (d).** Contá, sobre `senales.db` en `mode=ro`, cuántas
de las 295 filas tienen `available_at` igual a su `timestamp_utc`, o sea que
nunca recibieron el cierre de NYSE.

Si son cero, el agujero del bloque 5 es teórico y se declara. Si no son cero,
hay filas con un ancla temporal de reloj de pared, que es un problema distinto
de las 25 y que nadie contó nunca. En ese caso **no lo resuelvas**: mediló,
escribí el hallazgo y dejalo a firma.

## 10. Bloque 7. El alcance del §82.1

Donde el número 3 aparezca publicado tiene que aparecer al lado que la
multiplicidad que gobierna el resultado se computa sobre 30. Empezá por
`dinero/senal_larga_reporte.py` y seguí por todo documento generado que muestre
ese contador.

**No cambia ningún cálculo.** Es texto pegado al número. Si en algún lugar
cambiar el texto obligara a cambiar un cálculo, pará y anotalo.

## 11. Bloque 8. El §82.5, declarar el método de cada p

Cada p publicada lleva al lado con qué test se computó. **Ninguna cifra se
mueve.** El README publica el χ² de McNemar con corrección de Edwards y el
árbitro devuelve la exacta; las dos son correctas y lo que falta es decirlo.

Aprovechá para **confirmar o descartar** que la discrepancia entre el traspaso
de la corrida 10 y `espera_firma.md` en el p titular y en el último decimal del
intervalo es esta misma pareja de rutas. Es hipótesis, no conclusión.

Y sacá el `xfail` de `test_epistemico.py:775` si esta declaración lo resuelve.

## 12. Bloque 9. La razón podrida y su guardia

`test_epistemico.py:572` justifica su marcador diciendo que la regla de
deduplicación no está congelada y remitiendo al §56 punto 1 como pendiente.
**Esa decisión se cerró el 3-sep, acta §78.** El marcador sigue bien puesto por
otro motivo: `_filas_selladas_excluir_cero()` consulta la base por SQL y no pasa
por `cargar()`, así que ve los duplicados físicos que la regla firmada no borra
porque actúa al cargar.

Corregí la razón sin ablandar el test, y escribí el guardia que falta: el
proyecto vigila que las citas por número de línea a `DECISIONES.md` no se
desplacen, **y no tiene nada que verifique que las razones de los `xfail` sigan
siendo ciertas**. Una razón de `xfail` es documentación que vive dentro del
ejecutable.

## 13. Bloque 10. Regenerar el mapa operable

`docs/universo_operable.md` se genera, no se escribe. El censo vigente asume
acciones enteras con piso de 100 dólares, y por eso da 7 de 36.

Regeneralo con **el modo de compra como parámetro explícito** (enteras y
fraccionarias) y con el presupuesto como segundo parámetro, produciendo el censo
para **100, 250, 500 y 1000 dólares**. La fricción de ida y vuelta va al lado de
cada instrumento, leída del insumo del §40.

**Por qué las cuatro cifras y no una:** el presupuesto está sin decidir
justamente porque el censo se computó para un rango que ya no es el que se
discute. La decisión se toma con la tabla a la vista, no antes.

Aprovechá el mismo pase para el segundo día de censo, con precios congelados con
fecha y sha256 como el primero. La comparación entre los dos días es el dato, no
el segundo día solo.

## 14. Lo que esta corrida NO hace

- **No sella la primera fila prospectiva del riel de dinero.** El §26 está
  firmado pero el parche **no está aplicado**, y aplicarlo es de Nicolás. Sellar
  con el camino defectuoso sería sellar con el problema que se acaba de decidir
  corregir. Entra en la corrida 12, después de que el parche y el guardia
  aterricen juntos.
- **No aplica ningún parche a los archivos protegidos.**
- **No cablea `filtrar_sesion_coherente` al árbitro.**
- **No decide el presupuesto** ni toca nada del capital de terceros.
- **No firma el `motor_concat.diff`**, que necesita prueba de identidad de
  salida antes de que nadie lo aplique.
- **No audita liquidez real**, que espera a que exista la etapa E1.

## 15. Cierre

1. `GEMELO/resultados/bitacora_11.md`: por bloque, qué se hizo, qué se encontró
   con n e intervalo, qué dictaminó el adversario, qué quedó abierto, y
   **errores propios detectados**.
2. `estado_epistemico.md` sólo con afirmaciones que pasaron por el adversario.
3. **Limpiar `espera_firma.md` y `cola_decisiones.md`**: los seis ítems del §82
   salen de la cola con referencia a su acta. Lo que sigue esperando no se
   borra. Sacá también el aviso provisorio de la primera línea.
4. Nuevo conteo de intentos con la lista de lo que se sumó, respetando el
   §82.1 y el §82.6.
5. Acta en `DECISIONES.md`, sección §83.
6. `ESTADO.md` dentro de sus 50 líneas.
7. Suite completa en verde con el número anotado. Si un bloque la dejó en rojo,
   se revierte ese bloque y se documenta.
8. `director-programa` revisa el alcance. Lo que se salió se revierte.
9. **No hagas push.**

## 16. Prioridad si el tiempo no alcanza

El más ambicioso es el bloque 2. Los más baratos son el 0, el 7 y el 8, que
juntos no llegan a una hora y ejecutan tres firmas.

Si hay que elegir: **bloque 0 siempre, después el 1, después el 4.** El bloque 1
puede suspender todo lo demás y por eso va antes que el 2. El bloque 4 es el que
destraba la publicación del README, que es el ítem 3 de la lista de urgencia de
Nicolás desde hace semanas.

Lo que quede sin empezar se anota como no iniciado, con la razón.
