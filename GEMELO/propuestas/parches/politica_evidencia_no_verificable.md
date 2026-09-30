# Política de retención de la evidencia de un sello no verificable — PROPUESTA (corrida 15)

> **Estatus: PROPUESTA. Nada de esto está aplicado.** Es la política que el acta §90.6 exige
> **antes de cualquier línea de código** del parche de §62. El parche que la implementa vive al
> lado, en `GEMELO/propuestas/parches/sello_no_verificable.diff`, **NO APLICADO**: aplicarlo al
> sellador en producción exige un acta posterior de Nicolás con esta política a la vista (un
> cambio por noche al sellador, §87 pre-mortem ítem 3). `dinero/sello_dinero.py` del árbol real
> no cambió en la corrida 15.
>
> Escrita el 29-sep-2026 a las 22:32 de Chile, con el código del sellador leído y antes de
> escribir el parche. Intentos del DSR que consume: 0.

## 1. El problema, con lo que dice el código

**Medido el 28-sep-2026** (tarjeta §62, acta §89): el sellador disparó a las 13:43 de Nueva York,
con la bolsa abierta. La guarda E4 hizo lo suyo y marcó las 33 filas `no_verificable_timing`. Pero
el disparo escribió igual `ext_2026-09-28.csv`, que es una matriz de precios de media sesión, y
esas 33 filas ocuparon la fecha: el disparo bueno de las 23:30 NY encontró la fecha sellada, entró
por divergencia y escribió cero filas. **La sesión se perdió, y el archivo de evidencia de esa
fecha quedó ocupado para siempre por un insumo que E4 había rechazado.**

El acta §90.6 firmó dos cosas juntas: **(a)** que una fecha cuyas únicas filas son
`no_verificable_timing` cuente como no sellada y el disparo de las 23:30 pueda sellarla bien,
conservando las filas viejas; y **(d)** que un sello no verificable no reclame el cupo
`ext_<fecha>.csv`.

**HALLAZGO de la corrida 15, leído del código: (a) no se puede implementar como está escrita.**
La tabla `sellos_dinero` declara `UNIQUE (fecha_insumo, ticker, juego)`
(`dinero/sello_dinero.py`, en `init_db`). Las 33 filas no verificables y las 33 buenas de la
misma fecha tienen la misma terna: **no pueden convivir en esa tabla.** La tarjeta §62 ya había
preguntado «¿conviven dos sellos de la misma fecha con estados distintos?»; la respuesta del
esquema es que no. Quedan dos caminos, y elegir entre ellos es de Nicolás:

| camino | qué hace | qué cuesta |
|---|---|---|
| **M, migrar el esquema** | cambiar la restricción a una que incluya el estado | SQLite no modifica una restricción: hay que crear la tabla de nuevo, copiar las filas y borrar la vieja. Es reescribir físicamente todas las filas selladas, con los disparadores de inmutabilidad levantados mientras dura |
| **T, tabla aparte** | un disparo no verificable **no escribe en `sellos_dinero`**: deja sus filas en una tabla nueva, `intentos_no_verificables`, con las mismas columnas y la misma inmutabilidad | cambia lo que hace la guarda E4 (hoy marca la fila dentro de la tabla principal; pasaría a desviarla). Crear una tabla es aditivo: ninguna fila sellada se toca |

**El parche implementa T**, porque es el único de los dos que cumple «ninguna fila sellada se
reescribe» sin pedir una excepción. Con T, lo que el acta firmó en (a) se cumple por otro
mecanismo: la fecha queda sin sellar en `sellos_dinero`, así que el disparo de las 23:30 la sella
como cualquier otra, y `sello_previo()` no necesita distinguir estados para las fechas nuevas.
**Que el mecanismo sea otro que el firmado es exactamente lo que el acta que aplique el parche
tiene que ver y decidir.**

## 2. Qué se escribe cuando `timing_ok` es falso

Cuando la emisión no cumple `available_at < timestamp_utc < apertura objetivo`:

1. **Filas:** una por operable en `intentos_no_verificables`, con todas las columnas de un sello
   y `estado = no_verificable_timing`. Ninguna en `sellos_dinero`.
2. **Evidencia:** `dinero/datos/sello/ext_<fecha>.no_verificable.csv` y su
   `ext_<fecha>.no_verificable.meta.json`. El meta declara `"cupo_canonico": false` y guarda los
   tres instantes que prueban por qué no es verificable (`available_at`, emisión, apertura
   objetivo). Las filas citan ese archivo por nombre y por sha256.
3. **El nombre canónico queda libre.** `ext_<fecha>.csv` sólo lo escribe un sello con
   `timing_ok` verdadero.
4. **Un solo intento persistido por fecha.** Si ya hay un intento no verificable de esa fecha, un
   segundo no escribe filas ni archivo: con OTRO sha deja una fila en `divergencias_sello` con los
   dos sha, como hace hoy E4-bis con un segundo sello; con el MISMO sha devuelve `ya_intentada` y
   no deja nada, simétrico con `ya_sellada` (enmienda del 29-sep a las 23:38, por la R4 del
   `auditor-lookahead`: un re-disparo en el mismo minuto roto con el mismo insumo, que es el modo de
   falla medido en §63, no debe inflar `divergencias_registradas`, el único contador que la API
   sirve como alarma). Así la evidencia de una fecha nunca pasa de un par de archivos canónicos
   más un par no verificables.
   **Caso que la primera versión no contemplaba (B1 del auditor):** evidencia congelada con nombre
   canónico (timing ok al congelar) y timing roto al sellar, porque la apertura se cruzó entre las
   dos lecturas del reloj o porque `--sin-red` levantó un canónico nunca sellado. Se RECHAZA sin
   escribir filas en las dos tablas y sin tocar el archivo, **y el rechazo deja una fila en
   `divergencias_sello`** (sha del propio insumo rechazado en las dos columnas de sha, detalle que
   lo declara con los tres instantes): ningún disparo desaparece por completo, que es la doctrina
   de E4 («un segundo sello con otro insumo no se ignora en silencio»).
5. **Un intento no verificable nunca bloquea un sello posterior, y un sello nunca se deshace
   por un intento posterior.** Si la fecha ya está sellada en `sellos_dinero` y llega un disparo
   fuera de hora, vale lo de hoy: divergencia o `ya_sellada`, cero filas, ningún archivo.

## 3. Cuánto se conserva

**Para siempre, igual que la evidencia canónica.** Las filas de `intentos_no_verificables` citan
el archivo por sha256; borrarlo dejaría filas citando un contenido que no existe, que es el
defecto que E4-bis cerró en la corrida 13.

Tamaño, medido en `dinero/datos/sello/` a las 22:32: las cuatro últimas extensiones pesan entre
6,7 y 9,8 KB y sus metas 7,1 KB cada una (la extensión crece una fila por sesión, porque trae
todo lo posterior al congelado grande). La frecuencia medida es **1 disparo fuera de hora en 14
sesiones selladas** (el del 28-sep; n = 1, sin intervalo que valga la pena escribir). Aun con uno
por semana sería del orden de 1 MB por año. No hay rotación ni borrado, y **ningún job tiene
permiso de borrar en esa carpeta**.

## 4. Quién lo respalda

`respaldar_extension()` copia el par no verificable a `data/backups/sello_dinero_ext/`, igual que
el canónico, y `exportar_csv()` exporta la tabla nueva a
`data/backups/sello_dinero_no_verificables.csv`. `mki_backup.py` los commitea por pathspec con el
resto de `data/backups/`. `dinero/datos/sello/` sigue fuera de git (acta §88.3): la copia
versionada es la única que sobrevive a un disco.

## 5. Cómo lo trata el test de integridad permanente

El test de la corrida 13 exige, para cada fecha sellada, que el archivo que la base cita exista
en las dos carpetas con el sha256 citado, y que cada fecha cite un solo insumo. Con esta política:

1. **Se verifica cada tabla contra sus propios archivos.** Las filas de `sellos_dinero` citan
   archivos canónicos; las de `intentos_no_verificables` citan archivos `.no_verificable.csv`.
   Las dos comprobaciones fallan con el mismo diagnóstico de hoy: parar y reportar, no arreglar
   el archivo.
2. **Invariante nuevo:** ninguna fila de `sellos_dinero` escrita después del corte de método cita
   un archivo `.no_verificable.csv`, y ninguna de `intentos_no_verificables` cita un canónico.
3. **«Un solo insumo por fecha» se mantiene por tabla.** Una fecha puede tener un intento no
   verificable y un sello: son dos insumos, cada uno en su tabla y con su archivo.
4. **`--sin-red` no cambia.** `es_extension_sellable()` sólo acepta `ext_YYYY-MM-DD.csv`, así que
   un archivo no verificable nunca se levanta como insumo de un sello. El parche trae el test que
   lo prueba.

## 6. Lo que esta política no arregla

1. **El 28-sep no se toca.** Sus 33 filas están en `sellos_dinero` y citan `ext_2026-09-28.csv`,
   la matriz de media sesión. Se quedan donde están, con su estado, y el archivo no se renombra:
   es evidencia sellada. Es la **única fecha anterior al corte de método** que tiene un insumo
   rechazado en el cupo canónico, y el test de integridad la declara por regla (filas
   `no_verificable_timing` en la tabla principal, anteriores al corte), sin nombrar la fecha.
   La sesión del 28 está perdida y esta política no la recupera (§86.1).
2. **No cambia qué sesión cuenta para N.** §57 queda como está.
3. **No evita el disparo fuera de hora.** Eso no es configurable en systemd (tarjeta §63); la
   política sólo hace que cueste un registro y no una sesión.
4. **No cubre un disparo con la bolsa abierta en una fecha ya sellada la noche anterior:** no
   hace falta, porque el insumo intradía lleva la fecha del día en curso, que todavía no tiene
   sello.

## 7. Lo que el acta que aplique el parche tiene que decidir

1. **El camino:** T (el del parche), M, o ninguno.
2. **El corte de método:** la fecha y hora de aplicación al árbol real, que es desde cuándo rige.
3. **Si `sello_previo()` debe además distinguir estados** para la fecha vieja. Con T no hace falta
   para ninguna fecha nueva; para el 28-sep no serviría de nada, porque la restricción `UNIQUE`
   impediría igual insertar las filas buenas.
4. **Cuándo se aplica:** un cambio por noche al sellador, lejos de las 23:30 NY.
