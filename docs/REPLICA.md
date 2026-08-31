# Réplica de verdad — documento de diseño, no implementación

Hoy hay una sola máquina sellando (este PC, titular desde el switch
completado el 30-ago-2026), y es la máquina cuyo disco de sistema ya falló
una vez (la reactivación 5.0.3 nació de esa falla). Una réplica real no es
"correr dos veces lo mismo" — obliga a decidir, de antemano, qué pasa cuando
las dos máquinas sellan la misma fecha y difieren. El modo sombra
(`docs/SOMBRA.md`) se diseñó como un **instrumento de transición** con una
fecha de corte de switch; este documento evalúa qué hace falta para
convertirlo en un **mecanismo permanente**.

> **Principio rector:** una réplica que no puede decir qué pasa cuando
> discrepa no es una réplica, es una segunda máquina corriendo en paralelo
> sin ningún valor de auditoría. El valor de una réplica está enteramente en
> el protocolo de discrepancia, no en la redundancia de hardware.

## 1. Qué significa que dos máquinas sellen la misma fecha y difieran

Hay que distinguir tres clases de discrepancia, porque cada una tiene una
causa distinta y una respuesta distinta:

- **Discrepancia de insumos** — las dos máquinas vieron datos de mercado
  distintos al momento de sellar (ej. Yahoo publicó una revisión tardía que
  una máquina alcanzó a leer y la otra no). Esto ya tiene precedente en el
  proyecto (`descarga_ok/total/caidos` por snapshot) y NO es un error de
  ninguna de las dos — es el mundo siendo asíncrono. El comparador de
  tolerancia nivel 3 de `comparar_sombra.py` ya declara timestamps y
  metadata como "diferencias esperadas"; los insumos de mercado en sí no
  están hoy en esa lista y tendrían que estarlo si esto se vuelve
  permanente (ver §4).
- **Discrepancia de cómputo** — mismos insumos, resultado numérico distinto
  (beta, R², apertura estimada fuera de la tolerancia nivel 1, `1e-9`
  relativo). Esto SÍ es un hallazgo, nunca un ruido a ignorar: con los
  mismos datos y el mismo `motor.py` congelado (idéntico en ambas máquinas
  porque nunca se toca), un desacuerdo de cómputo solo puede venir de un
  entorno distinto — versión de pandas/numpy, orden de punto flotante, una
  dependencia no fijada. Es exactamente el tipo de cosa que el pin de
  pandas (`requirements.txt==3.0.3`, `GEMELO/resultados/expedientes.md` §6C)
  existe para prevenir.
- **Discrepancia de existencia** — una máquina selló la fecha y la otra no,
  o la selló con demora. Ya tiene los cuatro veredictos de `comparar_sombra.py`
  (`PARIDAD`, `DIVERGENCIA`, `DIA_NO_COMPUTABLE`, `PENDIENTE_PUBLICACION`) y
  ese vocabulario se hereda tal cual (§4).

## 2. Quién gana, y por qué esa regla y no otra

Esta es la pregunta que un mecanismo permanente no puede dejar abierta —
mientras fue transitorio, "el Mac es titular hasta el switch" resolvía todo
implícitamente. Sin fecha de corte, hace falta una regla explícita.

**Propuesta razonada (no la única legítima, marcada como tal — ver §5):**
designar una máquina **titular de sellado** en todo momento (hoy, este PC;
`modo.py` ya es la única fuente de verdad sobre cuál, nunca se deduce — ver
skill `modo-emision`). La fila de la titular es la que cuenta para las
métricas públicas, el reporte de Telegram y el track record — exactamente
como hoy. La réplica **nunca emite** su propia fila como si fuera la oficial,
pase lo que pase en la comparación. Esto preserva el invariante más
importante: en cualquier momento hay UNA fuente de verdad para "qué predijo
el modelo el día D", nunca dos compitiendo.

La alternativa que se descarta explícitamente y por qué: "gana la que llegó
primero" o "gana un promedio de las dos" romperían la Constitución 5.0 —
un promedio de dos filas selladas modifica lo que una de las dos selló, que
es indistinguible de reescribir una fila sellada. "Primero en llegar" haría
que la identidad de la titular dependiera de una carrera de red en vez de
una designación explícita, exactamente lo que `modo-emision` existe para
evitar ("al modo se le pregunta, no se deduce").

## 3. Qué se registra cuando difieren, para que la divergencia sea dato y no ruido

Toda discrepancia —de cualquiera de las tres clases del §1— se escribe a
una tabla nueva, propuesta acá y no implementada: `divergencias_replica`
(nombre a discutir), con al menos: `fecha`, `campo`, `valor_titular`,
`valor_replica`, `clase` (insumos/cómputo/existencia), `tolerancia_excedida`
(bool), `resuelto_como` (que fila prevaleció, siempre la titular por regla
del §2), `detectado_en` (timestamp). Esta tabla **nunca se usa para decidir
retroactivamente cuál fila era "la correcta"** — eso violaría el invariante
de sellos inmutables tanto como reescribir directamente. Sirve exclusivamente
de auditoría: cuántas veces difieren, en qué campos, de qué magnitud, si la
tasa de discrepancia de cómputo sube (señal de que algo del entorno se
desalineó) o si la de insumos sube (señal de que una fuente de datos se
volvió más inestable). Es el mismo espíritu que ya tiene `salud_descarga`
en `snapshots` — información sobre la calidad del proceso, nunca una
corrección de una fila ya sellada.

## 4. Qué de `comparar_sombra.py` sirve tal cual y qué habría que cambiar

**Sirve tal cual:**
- Los tres niveles de tolerancia (identidad numérica relativa 1e-9, igualdad
  exacta de campos categóricos/enteros, diferencias esperadas declaradas).
- Los cuatro veredictos (`PARIDAD`, `DIVERGENCIA`, `DIA_NO_COMPUTABLE`,
  `PENDIENTE_PUBLICACION`) y su lógica de desambiguación sin reloj (ver si
  la titular ya publicó fechas posteriores).
- El acceso de solo lectura: `git fetch` + `git show origin/main:...` para
  el lado titular (nunca `git pull`), `senales.db` en `mode=ro` para el
  lado local. Un mecanismo permanente hereda esto sin cambios — es
  exactamente lo que evita que la réplica pueda contaminar a la titular por
  accidente.
- La defensa estructural contra comparar una base consigo misma (coincidencia
  de `creado_en`+`timestamp_utc`+`plataforma_version` entre ambos lados
  refuta la comparación aunque la fecha sea posterior al corte).

**Habría que cambiar:**
- **`FECHA_CORTE` deja de tener sentido como constante fija.** Hoy es un
  valor congelado (`2026-08-24`) que existe para rechazar comparar fechas
  cuyas bases eran copia por pendrive, un problema de UNA transición
  puntual. Un mecanismo permanente no tiene "un corte": tiene un rango que
  crece cada día. La defensa estructural (coincidencia de timestamps de
  creación) ya no depende de una fecha y basta por sí sola para el caso
  permanente — proponer que el mecanismo permanente se apoye SOLO en esa
  defensa estructural, retirando la constante de fecha fija (o
  reinterpretándola como "fecha desde la que existe réplica", que se setea
  una vez al activar la réplica y nunca más se toca).
- **El overlap de fechas ya no es una anomalía transitoria a resolver una
  vez** (como fue el 26-ago con la composición canónica Mac≤25-ago/PC≥26-ago)
  — es el estado NORMAL de todos los días, siempre. La composición por
  rango de fechas fue la solución correcta para UNA transición con un
  before/after; un mecanismo permanente necesita que "titular gana siempre"
  (§2) sea la regla desde el día uno, no una composición ad hoc por rango.
- **`PENDIENTE_PUBLICACION`** asumía que la titular publica manualmente
  después de las 20:30 (el segundo movimiento del switch, `switch-titular`).
  **El push sigue siendo manual hoy** — `mki_backup.py` solo commitea,
  nunca pushea (`Jamás push`, línea 10 del propio archivo; los 6 timers
  systemd tampoco lo hacen), cadencia acordada tras la pérdida del SSD. Si
  algún día se decide automatizar el push, recién ahí `PENDIENTE_PUBLICACION`
  pasaría a ser raro en vez de esperado, y su persistencia sería en sí misma
  una señal de salud (el vigía debería poder alertar sobre él, algo que hoy
  no hace) — pero automatizar el push es, en sí, una decisión de Nicolás que
  este documento no da por hecha ni propone.
- **Nada en `SOMBRA.md` contempla ejecución indefinida** (creación de
  reportes en `data/sombra/` sin límite, crecimiento de la tabla de
  divergencias del §3, rotación de esos artefactos) — un mecanismo
  permanente necesita una política de retención, que hoy no existe ni falta
  hacía en un instrumento pensado para durar semanas.

## 5. Qué requiere firma de Nicolás

Todo lo siguiente es una decisión de Nicolás, no de este documento ni de
ningún agente:

- **Si se activa una réplica permanente en absoluto**, y con qué máquina
  (¿el Mac vuelve como réplica, ahora que quedó fuera del titular? ¿Otra
  máquina?). Es literalmente el "segundo movimiento" invertido, y cae bajo
  la misma skill `switch-titular` en espíritu aunque el sentido sea
  opuesto.
- **La regla de "quién gana" del §2** — es la propuesta razonada de este
  documento, no una regla ya adoptada. Nicolás puede preferir otra (por
  ejemplo, alguna forma de arbitraje manual en casos de discrepancia de
  cómputo, en vez de "la titular gana siempre sin excepción").
- **Qué se hace operativamente cuando la tasa de discrepancia de cómputo
  (§1, segunda clase) sube** — ¿alerta del vigía? ¿pausa de la réplica hasta
  investigar? Este documento solo dice que se registra (§3), no qué acción
  automática dispara.
- **El retiro de `FECHA_CORTE` como constante fija** (§4) — es un cambio de
  diseño en un mecanismo que hoy funciona; no se toca sin decisión explícita.
- **La política de retención de `data/sombra/` y de la tabla de
  divergencias** (§4, último punto) — cuánto se guarda, por cuánto tiempo,
  si se resume periódicamente.
- **Cualquier cambio de código real** — este documento es puramente de
  diseño; nada de lo descrito acá está implementado, y no se implementa sin
  que Nicolás decida activarlo.

## 6. Ensayo general — qué se probó, con qué datos, qué mostró

Esto es un **registro de lo ya ejecutado**, distinto del §5 (que es la
lista de lo que todavía espera firma). Nada de lo que sigue activó nada:
corrió contra bases sqlite sintéticas, temporales, en un directorio
`tempfile.mkdtemp()` que se borra al final de la corrida — nunca contra
`senales.db`, `noticias.db` ni la ruta real de producción
`data/divergencias_replica.db`.

**Script:** `scripts/ensayo_replica.py` (versionado, re-ejecutable con
`python scripts/ensayo_replica.py`; el motivo de que sea un script y no
comandos sueltos de una sesión está en su propio encabezado, y en
`DECISIONES.md` §45 — un análisis completo que vivió solo en comandos
sueltos de una sesión se perdió al cerrarla).

**Qué construye:** dos fuentes sintéticas — una que hace de **titular**
(dos `DataFrame`, como si vinieran de `git show
origin/main:data/backups/*.csv`) y una que hace de **réplica** (una base
sqlite real y propia del ensayo, con tablas `snapshots` y
`senales_ticker`) — y una cadena de **8 fechas** (2026-09-01 a 2026-09-10)
que ejercitan las tres ramas del enunciado más sus sub-casos:

| Fecha | Qué ensaya | Veredicto esperado |
|---|---|---|
| 2026-09-01 | ambas sellaron e igual | `PARIDAD` |
| 2026-09-02 | mismos insumos, `beta` distinto | `DIVERGENCIA` (clase `computo`) |
| 2026-09-03 | `sox_fecha` distinto | `DIVERGENCIA` (clase `insumos`) |
| 2026-09-04 | el titular selló, la réplica no | `DIVERGENCIA` (clase `existencia`, sello ausente) |
| 2026-09-05 | ambas sellaron el snapshot igual, conjunto de tickers distinto | `DIVERGENCIA` (clase `existencia`, conjunto) |
| 2026-09-08 | el titular no selló (ni la réplica esa noche) | `DIA_NO_COMPUTABLE` |
| 2026-09-09 | ancla: el titular SÍ publicó esta fecha, por eso 09-08 es ausencia definitiva | `PARIDAD` |
| 2026-09-10 | el titular no aparece y tampoco hay fecha suya posterior | `PENDIENTE_PUBLICACION` |

**Cómo se acopla al comparador real sin tocar nada vivo:** el único punto
de acceso a datos "vivos" de `comparar_sombra.py` es
`leer_tabla_local(tabla, fecha)`, que en producción abre `senales.db` en
`mode=ro`. El ensayo reemplaza esa función, solo durante su propia
ejecución y restaurándola en un `finally`, por una versión que lee de la
base sqlite sintética de la réplica. `comparar_fecha` y
`replica.registrar_comparacion` corren exactamente igual que en
producción — es la cadena completa, no una simulación de la cadena.

**Qué mostró, con la salida real de la corrida** (íntegra en
`data/replica_ensayo/reporte_ensayo.md`, timestamp de esa corrida
`2026-08-31T19:13:22.862021+00:00`):

Caso 1 (coinciden):

```
## Caso 1 — coinciden — 2026-09-01

- Veredicto obtenido: **PARIDAD**  (esperado: PARIDAD)
- Motivo: todos los campos de nivel 1 y 2 coinciden
- Hallazgos nivel 1/2 de `comparar_fecha`: 0
- Filas insertadas por `registrar_comparacion`: 0
```

Caso 2 (difieren), con procedencia completa y clase correcta en los cuatro
sub-casos ensayados:

```
## Caso 2 — difieren (cómputo) — 2026-09-02
- Veredicto obtenido: **DIVERGENCIA**  (esperado: DIVERGENCIA)
    - campo=beta clase=computo titular='0.38' sombra='0.41' resuelto_como=None

## Caso 2 — difieren (insumos) — 2026-09-03
- Veredicto obtenido: **DIVERGENCIA**  (esperado: DIVERGENCIA)
    - campo=sox_fecha clase=insumos titular='2026-09-02' sombra='2026-09-03' resuelto_como=None

## Caso 2 — difieren (existencia, sello ausente) — 2026-09-04
- Veredicto obtenido: **DIVERGENCIA**  (esperado: DIVERGENCIA)
- Motivo: el titular selló y la SOMBRA no. No es un día no computable: es
  la sombra fallando, que es justo lo que la ventana existe para detectar.
    - campo=sello_ausente clase=existencia titular=None sombra=None resuelto_como=None

## Caso 2 — difieren (existencia, conjunto de tickers) — 2026-09-05
- Veredicto obtenido: **DIVERGENCIA**  (esperado: DIVERGENCIA)
- Hallazgos nivel 1/2 de `comparar_fecha`: 4
    - campo=tickers_sellados clase=existencia titular='2 tickers' sombra='1 tickers' resuelto_como=None
    - campo=ticker_ausente_en_sombra clase=existencia titular='005930.KS' sombra=None resuelto_como=None
    - campo=numero_de_predicciones clase=existencia titular='2' sombra='1' resuelto_como=None
    - campo=filas_selladas clase=existencia titular='2' sombra='1' resuelto_como=None
```

Caso 3 (una no selló), sin ninguna fila de divergencia falsa por una
ausencia legítima:

```
## Caso 3 — no selló (DIA_NO_COMPUTABLE) — 2026-09-08
- Veredicto obtenido: **DIA_NO_COMPUTABLE**  (esperado: DIA_NO_COMPUTABLE)
- Motivo: el titular publicó sellos de fechas posteriores pero ninguno de
  esta, así que la ausencia es DEFINITIVA: no selló. Y la sombra tampoco.
  Sin sello del titular no hay contra qué comparar: día PERDIDO, no día
  bueno.
- Filas insertadas por `registrar_comparacion`: 0

## Caso 3 — no selló (PENDIENTE_PUBLICACION) — 2026-09-10
- Veredicto obtenido: **PENDIENTE_PUBLICACION**  (esperado: PENDIENTE_PUBLICACION)
- Motivo: no hay fila del titular en origin/main para esta fecha, y
  tampoco hay sellos suyos de fechas posteriores: no se puede distinguir
  'no selló' de 'selló y aún no pusheó'. NO es un día perdido — vuelve a
  correr después del push del Mac (manual, tras las 20:30) y el día se
  resuelve de verdad.
- Filas insertadas por `registrar_comparacion`: 0
```

Resumen final de la corrida:

```
## Resumen

- Fechas ensayadas: 8
- Filas totales en `divergencias_replica` (base temporal del ensayo): 7
- `resuelto_como` NULL en todas las filas: True

### Sin hallazgos

Los tres casos se comportaron exactamente como predice `docs/REPLICA.md`:
paridad sin ruido, divergencia con procedencia completa y clase correcta,
ausencia legítima sin filas falsas.
```

**Hallazgo del ensayo: ninguno.** Las tres piezas (`comparar_sombra.py`,
`replica.py`, y el diseño de `docs/REPLICA.md` §1–§3) se comportaron
exactamente como el diseño predecía, incluyendo los cuatro sub-casos de
"difieren" (cómputo, insumos, y las dos variantes de existencia) y los dos
sub-veredictos de "una no selló". El script queda versionado y
re-ejecutable — una repetición futura, tras cualquier cambio en
`comparar_sombra.py` o `replica.py`, puede volver a correrlo y comparar
contra esta misma tabla sin tener que reconstruir el escenario de memoria.

## 7. El runbook de activación

Los pasos exactos para el día que Nicolás decida activar la réplica están
en `docs/RUNBOOK_REPLICA.md`, no en este documento: este archivo es diseño
y evaluación de qué hace falta decidir (§1–§6); el runbook es
procedimiento operativo puro, con verificación paso a paso, en el mismo
espíritu que `docs/SOMBRA.md` es el procedimiento operativo del switch
titular/sombra y no su documento de diseño. Separarlos evita que una
edición operativa (agregar un paso, corregir un comando) se confunda con
una decisión de diseño nueva, y viceversa.
