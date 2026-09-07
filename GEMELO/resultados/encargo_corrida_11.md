# Encargo corrida 11: validar el instrumento, reconstruir sin fuga, y sellar la primera fila prospectiva del riel de dinero

Leé este archivo entero antes de ejecutar nada. Corrida nocturna sin
supervisión; Nicolás revisa a la mañana. **Nada se pushea**: el push lo hace
Nicolás después de leer el diff.

El orden de los bloques es estricto y la razón está escrita en cada uno. Si el
tiempo no alcanza, se cierra limpiamente lo abierto y lo restante queda como
no iniciado en la bitácora. Un frente a medias sin bitácora es peor que uno no
empezado.

---

## 0. Orientación obligatoria

1. `orientador` reconstruye el estado. Orden de lectura: `ESTADO.md`,
   `GEMELO/resultados/estado_epistemico.md`, `espera_firma.md`,
   `cola_decisiones.md`, `bitacora_10.md`, actas §80 y §81 de `DECISIONES.md`,
   `GEMELO/resultados/dictamen_10/aplicacion.md` y
   `GEMELO/resultados/calibracion_instrumento.md`.
2. **Toda cifra se lee de la máquina** (módulo árbitro o README renderizado),
   nunca de memoria ni de este archivo. Si este archivo y la máquina no
   coinciden, manda la máquina y se anota errata.
3. Suite completa antes de empezar; anotá el número. Si no está en verde,
   parás y reportás.
4. Ventana de sellado 17:50 a 20:30 hora de Chile: nada pesado.
5. El registro de intentos se incrementa por cada hipótesis probada esta
   noche, incluidas las descartadas.
6. **`director-programa` corre en modo pre-mortem sobre este encargo antes de
   ejecutar el bloque 1**, y devuelve la lista de instrucciones que podrían
   ser ellas mismas el defecto. El orquestador no ejecuta una instrucción
   marcada sin anotarla en la bitácora.

## 1. Límites duros

- No se tocan `motor.py`, `senales.py`, `snapshot.py`, `universo.py`, el modo
  de emisión, `.env` ni los timers. Donde un frente necesite tocar uno de
  ellos, produce un parche NO aplicado con su test y lo deja en
  `espera_firma.md`.
- No se reescribe ninguna fila sellada.
- Ninguna cifra publicada se mueve sola.
- Ningún estimador puntual sin intervalo computado. Clúster de día siempre que
  haya más de un ticker por fecha.
- Todo lo nuevo se etiqueta PROPUESTA hasta el dictamen del
  `estadistico-adversario`.
- Una verificación que usa el mismo mecanismo que produjo la cifra no es
  verificación.
- La corrección va al ejecutable antes que al texto.

## 2. Decisiones de Nicolás que esta corrida presupone

**Si alguna no está firmada al arrancar, el bloque que depende de ella no se
ejecuta y se anota como bloqueado.** No se ejecuta "asumiendo" una firma.

- **§26 / §1, el parche de `snapshot.py:140`**, en sus tres partes: aplicar el
  diff con bump de `PLATAFORMA_VERSION`, el guardia de la rama del `except`, y
  el tratamiento de las 15 filas en métricas. Bloquea el bloque 6.
- **§42, la cuenta en papel se reconstruye o se descarta.** Bloquea los
  bloques 3 y 4.
- **§45, el registro de intentos del riel largo pasa de 3 a 30.** Bloquea
  cualquier cómputo de DSR en ese riel.

---

## 3. Bloque 1 (PRIMERO). La mitad que falta de la calibración del instrumento

**Por qué va primero.** El proyecto tiene la regla de verificar el instrumento
contra una verdad conocida antes de creerle sobre una desconocida. La mitad
con ventaja verdadera igual a cero se corrió. **La mitad con ventaja verdadera
distinta de cero no se corrió**, y la tabla de potencia del riel de dinero es
aritmética sin validar. Reconstruir la cuenta en papel antes de esto produce
cifras que no se pueden interpretar, porque no se sabe qué hace el instrumento
cuando hay algo que detectar.

Corré `GEMELO/simulador/` con ventaja verdadera distinta de cero, en al menos
tres magnitudes declaradas antes de correr, con semilla sellada y número de
réplicas por celda declarado. Reportá, por celda, la proporción de veces que
el procedimiento detecta la ventaja, con su intervalo. Reportá también la
mitad nula en el mismo cuadro, aunque ya esté corrida, para que las dos tasas
queden en la misma tabla.

**Criterio de fallo del bloque, escrito antes:** si la tasa de detección bajo
ventaja verdadera no supera a la tasa de falsa detección bajo ventaja nula en
ninguna de las tres magnitudes, el instrumento no discrimina y **todo lo demás
de esta corrida queda suspendido**, incluida la reconstrucción. Eso sería un
resultado, no un fracaso, y se publica con la misma firmeza que el contrario.

## 4. Bloque 2. El insumo del §40, cableado

Los tres documentos escritos el 7-sep-2026 entran al repositorio como
PROPUESTA y no se modifican en esta corrida:
`criterio_corredor_prerregistro.md`, `insumo_40_aranceles_ibkr.md`,
`regla_aporte_y_dimensionamiento.md`.

Lo que sí hace esta corrida: **verificar de forma independiente** las dos
tarifas contra la fuente oficial, con fecha de consulta propia, sin usar las
cifras del documento como insumo. Si difieren, manda tu lectura y se anota
errata. Reportá también si la contradicción entre 1% y 0,5% sigue en la página
o se resolvió.

Cero intentos del DSR: no se evalúa ninguna hipótesis sobre retornos.

## 5. Bloque 3. Reconstrucción de la cuenta en papel, orden obligatorio

**Depende de la firma §42.** El orden lo fijó el `auditor-lookahead` y no se
altera.

1. **El test de truncación primero.** `tests/test_dinero.py` tiene tres
   `xfail(strict=True)` que clavan F1, F2 y F4. Hoy fallan porque las fugas
   existen. Cuando se arreglen van a pasar, el modo estricto va a volver eso
   rojo, y eso **obliga a volver a sacar el marcador**. Es intencional.
2. Las correcciones: membresía acotada por fecha, sorteo desde datos
   anteriores a la ventana, retardo de implementación en las **dos** patas de
   la comparación, sigma del interruptor sin futuro, y cablear
   `ErrorLookAhead` al riel.
3. Recién después republicar.

**No se calcula un solo MAE antes de que el auditor corra.** Es el
procedimiento que funcionó en el bloque 6 de la corrida 10 y se repite.

## 6. Bloque 4. Cobertura por causalidad de `cuenta_papel.py` y `contabilidad.py`

**Va pegado al bloque 3 y no después.** La sección 10 declara que la suite
verde no cubre por causalidad ninguno de los dos, y que un verde de `pytest`
hoy **no es evidencia de ausencia de fuga** en el riel de dinero. Reconstruir
sin cerrar esto es repetir el error con código nuevo.

Medí la cobertura por causalidad de los dos módulos, antes y después de la
reconstrucción, y reportá los dos números. Si algún camino queda sin cubrir,
se lista con la razón.

## 7. Bloque 5. Regenerar el mapa operable con el parámetro de fraccionarias

`docs/universo_operable.md` se genera, no se escribe. El censo vigente asume
compra de acciones enteras y por eso da 7 de 36 alcanzables con piso de 100
dólares, con `SMH` fuera de 500.

**El insumo del §40 cambia el censo**: con fraccionarias los 36 son
alcanzables, a 1% del valor operado por lado. Regenerá el mapa con el modo de
compra como parámetro explícito, produciendo las dos columnas, enteras y
fraccionarias, con la fricción de ida y vuelta al lado de cada instrumento.

Aprovechá el mismo pase para cerrar el segundo hueco de la sección 10:
**segundo día de censo**, con precios congelados con fecha y huella sha256
como el primero. La comparación entre los dos días es el dato, no el segundo
día solo.

**Lo que este bloque NO hace:** auditar liquidez real. Ver la sección 10 de
este encargo.

## 8. Bloque 6. La primera fila prospectiva del riel de dinero, tamaño cero

**Depende de la firma del §26**, porque toca el camino de sellado.

Este es el único hueco de la sección 10 que no se puede cerrar con más
cómputo, y el reloj corre: cada noche sin sellar es una noche que no se
recupera. Todas las cifras del riel de dinero salen hoy de mirar ocho años de
una vez, y la única defensa contra la fuga por el analista es el sellado en
vivo.

La máquina emite una decisión del riel de dinero **antes de la apertura del
mercado objetivo**, con **tamaño nominal cero**, y la sella con la misma
disciplina del riel de medición: marca de tiempo, `available_at`, sesión
objetivo anclada a `available_at` y no al reloj de pared, y sin reescritura
posterior.

Tamaño cero significa cero dinero, cero cuenta y cero orden enviada a ningún
lado. Lo que se sella es la decisión, no la posición.

**Aislamiento:** el bloque no puede tocar el camino de sellado del riel de
medición. Los tests de aislamiento en las dos direcciones que existen desde la
corrida 10 tienen que seguir verdes y se anota su número.

## 9. Cierre de la corrida

1. `GEMELO/resultados/bitacora_11.md`: por bloque, qué se hizo, qué se
   encontró con n e intervalo, qué dictaminó el adversario, qué quedó abierto,
   y **errores propios detectados**.
2. `estado_epistemico.md` sólo con afirmaciones que pasaron por el adversario.
3. `espera_firma.md` y `cola_decisiones.md` actualizados sin borrar lo que ya
   esperaba.
4. Nuevo conteo de intentos del DSR con la lista de lo que se sumó esta noche.
5. Acta en `DECISIONES.md`.
6. `ESTADO.md` dentro de sus 50 líneas.
7. Suite completa en verde con el número final anotado. Si un bloque dejó la
   suite en rojo, se revierte ese bloque y se documenta.
8. `director-programa` revisa que nada se salió del alcance. Lo que se salió
   se revierte.
9. **No hagas push.**

---

## 10. Triage de la sección 10 del traspaso: qué entra y qué espera

Escrito antes de ejecutar, con la razón de cada uno.

### Entra

| Hueco | Bloque | Razón |
|---|---|---|
| No se corrió el simulador con ventaja verdadera distinta de cero | 1 | Es la regla propia del proyecto. Sin esto, ninguna cifra de los bloques 3 y 5 es interpretable, porque no se sabe qué hace el instrumento cuando hay algo que detectar. Va primero por eso, no por importancia relativa. |
| El supuesto de costos no está contrastado contra tarifario real (§40) | 2 | Ya está resuelto fuera de la corrida y sólo falta verificación independiente. Es el bloque más barato de la noche y desbloquea el parámetro de costo del bloque 3. |
| No se reconstruyó la cuenta en papel | 3 | Bloquea tres cosas: la segunda vara, el criterio M2 y la σ de la tabla de potencia. Es el ítem más caro de postergar de los abiertos. |
| La suite verde no cubre por causalidad `cuenta_papel.py` ni `contabilidad.py` | 4 | Va pegado al 3. Reconstruir sin cerrar esto es volver a producir código cuyo verde no significa nada. |
| No se verificó el mapa operable en un segundo día | 5 | Sube de prioridad por una razón nueva: el insumo del §40 obliga a regenerar el mapa de todos modos, porque las fraccionarias cambian el censo entero. Aprovechar el mismo pase cuesta casi nada. |
| Nada del riel de dinero es prospectivo | 6 | Único hueco que no se cierra con cómputo y cuyo costo de postergar crece cada noche. Cuesta cero pesos. |

### Espera, con la razón

| Hueco | Por qué espera |
|---|---|
| No se corrió la segunda vara pre-registrada de la señal larga | Pasa por la cuenta retirada. No es que sea menos importante: es que **no se puede** hasta que el bloque 3 termine. Entra sola en la corrida 12. |
| No se midió la tasa de falsos positivos del diseño de la señal larga (K semillas) | Es del riel largo, que hoy no tiene ninguna afirmación positiva en pie. Medir la tasa de falsos positivos de un diseño cuya única afirmación ya fue refutada tiene valor metodológico y no desbloquea nada. Además el bloque 1 mide la propiedad análoga sobre el instrumento compartido, así que conviene ver ese resultado antes de gastar K semillas acá. |
| No se auditó la liquidez real de ningún instrumento | Requiere datos de volumen que el proyecto no tiene y no bloquea nada mientras no haya órdenes reales. El escalonamiento de `regla_aporte_y_dimensionamiento.md` pone las órdenes reales en la etapa E2, después de E0 y E1. Entra cuando E1 esté cerrada, no antes. Los dos miembros de los paneles que están en esa situación siguen declarados. |

### Nota sobre el orden de urgencia contra el orden de ambición

El bloque más ambicioso de esta corrida es el 3. El más urgente es el 6, que
cuesta una noche de trabajo y cero pesos. Si el tiempo no alcanza para los
dos, **se hace el 6 y se posterga el 3**, y se anota en la bitácora qué quedó
postergado por esa elección.
