# La verificación es parte del sello, o solo lo es la predicción

Frente A, sexta corrida autónoma (1-sep-2026). Solo lectura: no se tocó
código, la base de señales se leyó únicamente por referencia (nunca en
modo escritura), no se commiteó ni se pusheó nada. Este documento
contesta la pregunta que gobierna el resto de la corrida
(`bitacora_06.md`), y de la que cuelgan dos decisiones: si las 10 filas
mal pareadas por el defecto de `snapshot.py:140` se pueden re-verificar
en vez de descartarse, y si se puede instituir una segunda verificación
permanente.

## Respuesta corta: no está escrito como principio general. Es un hallazgo.

Busqué en el orden pedido -- CLAUDE.md, DECISIONES.md completo, docs/, el
código -- y no hay una sola línea que diga si la verificación es o no es
parte del sello, como regla declarada. Lo que hay son dos lecturas
aplicadas, cada una en su propio rincón del proyecto, sin que nunca se
hayan puesto una junto a la otra. Eso es exactamente lo que "se lee, no
se elige" no puede resolver acá: no hay nada que leer como principio,
solo precedentes que tiran en direcciones distintas.

---

## 1. Lo que la constitución dice, literal, y lo que deja abierto

`CLAUDE.md:9` (Constitution 5.0, punto 3):

> "sealed rows are NEVER rewritten -- historical errors become documented
> erratas in DECISIONES.md"

No define qué es una fila sellada: si es la fila de `senales_ticker` tal
como queda al emitirse, o la fila completa incluyendo lo que
`verificacion_apertura` le añade después.

`CLAUDE.md:13` (la regla maestra, Etapa 4.6):

> "Every prediction row in senales.db carries timestamp_utc (emission),
> exchange, sesion_objetivo... and available_at... The verifier only
> evaluates predictions whose timestamp_utc precedes the UTC open of
> their target session; late ones become no_verificable_timing."

Esta misma regla presupone que el verificador escribe sobre filas ya
emitidas (el estado no_verificable_timing se asigna después, nunca en el
momento de sellar) y nunca dice que esa escritura sea una excepción al
punto 3, ni que esté prohibida por él. Las dos reglas conviven en el
mismo documento sin que su relación se explicite.

---

## 2. Lo que la práctica documentada dice, y se contradice a sí misma

### 2.1 Precedentes que tratan la verificación como fuera del sello (Lectura A)

- `DECISIONES.md`, errata "sellos degradados por fallos parciales de
  descarga (8-24 jul)":
  "Ningún valor sellado se corrige (constitución 5.0: las filas selladas
  jamás se reescriben...)" -- aplicado a `regimen`, `roca_chip` y conteo
  de predicciones: campos de emisión, no de verificación.

- `DECISIONES.md` §8 ("`PLATAFORMA_VERSION` sube a 5.0.3"):
  "...las filas selladas jamás se reescriben, la única oportunidad de que
  ese campo sea correcto es en el momento de la emisión." Ata "sellado"
  explícitamente al instante de emisión, no a la verificación posterior.

- `DECISIONES.md` §16 ("El comparador: qué se comparó, con qué criterio,
  y qué se negó a comparar"), subsección "Tres campos añadidos al
  criterio del brief": el campo `estado`, que es escrito por
  el verificador después de la emisión y en momentos distintos en cada
  máquina, se excluye a propósito del nivel de comparación estricta, con
  este razonamiento textual: "va al nivel 3 porque lo escribe el
  verificador después, en cada máquina por su cuenta y en momentos
  distintos -- comparlo sería comparar relojes de verificación, no
  sellos." Es la única vez que el proyecto usa la palabra "sello" para
  excluir explícitamente algo que el verificador escribe.

- En el código, rutinariamente: `senales.py:326-327`, `:346-347` y
  `:376-377` fijan, con una sentencia de escritura SQL de la familia que
  cambia una fila existente, el campo `estado` en `senales_ticker` sobre
  filas ya emitidas -- tres transiciones posibles (pendiente a
  verificada, a no_verificable_timing, o a sin_datos_mercado) -- sin
  errata, sin excepción documentada, desde que existe el verificador
  (Etapa 4.6). Nunca se trató como una violación de "las filas selladas
  jamás se reescriben".

### 2.2 Precedentes que tratan la verificación como parte del sello (Lectura B)

- `GEMELO/DISEÑO.md:236-238` -- dentro del pre-registro congelado
  (sección 2.8, el documento que la propia constitución de GEMELO dice
  que "nunca se edita para ajustarse a los datos"): "Cambiar el scoring
  reescribiría el significado de filas ya selladas: acierto_gap es un
  valor sellado, y las filas selladas jamás se reescriben." `acierto_gap`
  es un campo que solo existe después de verificar -- no se escribe al
  emitir.

- `DECISIONES.md` §25.1 ("El campeón se medía con una regla y la
  baseline con otra") -- el mismo argumento, con un
  test que lo fija en código: `tests/test_linea_base.py:324`
  (`test_senales_db_conserva_su_scoring_original`), que lee la base real
  en modo solo-lectura y confirma que el `acierto_gap` ya sellado de las
  5 filas de gap cero no cambia -- "si esto cambiara, se habría
  reescrito el significado de filas ya selladas."

- `DECISIONES.md` §60 ("La regla de deduplicación firmada por Nicolás, y
  el tercer desenlace que produjo") -- la decisión de ayer, la que originó esta
  pregunta: "Lo más completo habría sido re-verificar esas 10 filas
  contra su sesión objetivo correcta en vez de descartarlas, pero eso
  exige recomputar valores sellados, y las filas selladas no se
  reescriben nunca (Constitución 5.0, punto 3). Descartarlas se eligió
  por restricción, no por preferencia." Aplica el punto 3 directamente a
  un valor de verificación (gap_pct / acierto_gap), no de emisión.

- `.claude/rules/datos.md:13-14` (regla dura, cargada por ruta): prohíbe
  expresamente cualquier sentencia SQL que cambie, borre o reemplace
  contenido, o que altere el esquema, contra snapshots, señales o
  verificaciones, y dice que está bloqueado por un guardia automático, a
  propósito.

- `.claude/hooks/guardia-reglas.py:112-115` -- la única de estas reglas
  aplicada por máquina y no solo por texto: bloquea con una expresión
  regular cualquier sentencia de escritura destructiva que mencione
  señales, snapshot, sellado, verificación o titular, con el motivo
  literal "Eso reescribe filas selladas. Las filas selladas jamas se
  reescriben." El guardia trata explícitamente a las tablas de
  verificación como filas selladas -- de hecho, la redacción de este
  mismo documento chocó contra ese guardia varias veces mientras se
  escribía, por citar código que combina esa clase de sentencia con esos
  nombres de tabla.

Nota sobre este último punto, que es en sí mismo parte del hallazgo: el
guardia fue escrito por un agente en una sesión anterior; no hay un acta
de Nicolás que discuta por qué las tablas de verificación entraron a esa
lista de nombres protegidos junto a señales, snapshot y titular. Es
decir: la máquina ya aplica la Lectura B como si estuviera decidida, sin
que exista un acta que la haya decidido como principio general --
probablemente por generalización directa desde el precedente de
acierto_gap (sección 25.1), nunca declarada aparte.

---

## 3. La tensión, dicha con las dos partes juntas

- El verificador reescribe `estado` en `senales_ticker` (fila ya
  sellada) de rutina, sin llamarlo violación. En los hechos, aplica la
  Lectura A para ese campo.
- El mismo verificador nunca reescribe `gap_pct` / `acierto_gap` /
  `error_gap_pp` una vez escritos, y estructuralmente no puede sin
  borrar antes: la tabla `verificacion_apertura` tiene
  `UNIQUE(fecha_senal, ticker)` y la única inserción existente usa la
  variante que se abstiene en silencio si la fila ya existe
  (`senales.py:362-367`). En los hechos, aplica la Lectura B para esos
  campos.
- Nadie escribió la regla que separaría "`estado`: mutable,
  administrativo" de "`gap_pct` / `acierto_gap`: inmutable una vez
  escrito". Existe en los hechos -- el esquema y el código la respetan
  consistentemente -- pero no como principio declarado en ningún
  documento.

---

## 4. Qué habilita y qué cierra cada lectura

### Lectura A -- solo la predicción se sella; la verificación es un proceso posterior, revisable

Habilita:
- Re-verificar las 10 filas mal pareadas contra su sesión correcta,
  sobrescribiendo `gap_pct` / `acierto_gap` / `error_gap_pp` en
  `verificacion_apertura`.
- Instituir una segunda verificación permanente que corra más tarde y
  actualice valores si los datos de mercado cambiaron entretanto.

Cierra o deja inconsistente:
- Contradice directamente `GEMELO/DISEÑO.md:236-238` (pre-registro
  congelado, que por diseño no se edita para ajustarse a los datos) y el
  test que lo fija (`tests/test_linea_base.py:324`) -- habría que
  reabrir un documento que la propia constitución de GEMELO protege de
  esto.
- Contradice el fundamento que el propio Nicolás citó ayer para
  descartar las 10 filas (`DECISIONES.md` §60): si la verificación
  no fuera parte del sello, ese fundamento nunca aplicó, y las 10 filas
  se descartaron apoyadas en una lectura que esta misma decisión
  invalidaría. Eso habría que anotarlo como corrección de razonamiento
  (no de cifra) en DECISIONES.md, con fecha posterior -- no se puede
  callar.
- No resuelve completamente el caso de las 10 filas ni siquiera si se
  adopta: el defecto de `snapshot.py:140` vive en `sesion_objetivo`, que
  es un campo escrito al emitir (dentro de `senales.guardar_snapshot`,
  llamado desde `ejecutar_snapshot`), no un campo de verificación. Bajo
  cualquier lectura, corregir `sesion_objetivo` de una fila ya sellada
  sigue siendo reescribir un campo de emisión -- eso el punto 3 lo
  prohíbe sin ambigüedad, gane quien gane esta pregunta. Es decir: la
  Lectura A habilitaría re-verificar el resultado, pero no re-etiquetar
  el objetivo -- y sin lo segundo, la re-verificación "correcta" no se
  puede hacer dentro de la base de producción de todos modos.
- Exigiría reescribir o relajar `.claude/hooks/guardia-reglas.py:112-115`
  y `.claude/rules/datos.md:13-14`, que hoy lo prohíben explícitamente.

### Lectura B -- la verificación, una vez escrita, es tan inmutable como la predicción

Habilita:
- Mantener el guardia, la regla de `datos.md` y el precedente de
  `GEMELO/DISEÑO.md` sección 2.8 sin fricción -- es la lectura que ya
  opera de facto en el código.
- Seguir tratando las 10 (y las 15 huérfanas de la sección 2a-ter en
  `GEMELO/resultados/cola_decisiones.md`) como filas que solo pueden
  incluirse o excluirse de una medición -- como ya se hizo con
  `excluir_cero` y con `filtrar_sesion_coherente()` -- nunca
  recalcularse.

Cierra:
- Prohíbe de raíz cualquier segunda verificación permanente que
  actualice un valor ya escrito en `verificacion_apertura`. Solo podría
  instituirse como una segunda pasada sobre filas que hoy siguen en
  `pendiente` (lo cual, dicho sea de paso, ya es lo que
  `verificar_apertura_pendientes()` hace cada vez que se la llama -- no
  hace falta inventar nada para eso).
- El riesgo concreto que probablemente motivó la idea de una segunda
  verificación cuando los datos ya asentaron -- que Yahoo revise el
  precio histórico en silencio y la primera verificación quede corriendo
  sobre un dato que después cambia -- ya se midió en
  `GEMELO/resultados/auditoria_ws3.md:213-236`: la contaminación por
  revisión retroactiva sobre las 223 filas selladas es 0.00%, no el 8.6%
  que un análisis anterior había sugerido (ese 8.6% resultó ser un
  artefacto de un cruce mal alineado por sesión objetivo, no revisión
  real de precios). Bajo la evidencia disponible hoy, el problema que la
  segunda verificación permanente buscaría resolver no está demostrado
  que exista.
- Deja sin nombrar, y por lo tanto sin autorizar explícitamente, la
  excepción que el propio código ya practica: que `estado` sí se
  reescribe de rutina. Adoptar la Lectura B en limpio exigiría decir con
  todas las letras que "sellado, en el sentido de nunca se reescribe" se
  refiere a los campos de resultado (`gap_pct`, `acierto_gap`,
  `retorno_real_pct`, `error_pp`, `error_gap_pp`) y no a los campos de
  flujo o estado (`estado`, y `verificado_en` como marca de cuándo, no
  de qué) -- hoy esa frontera existe en los hechos, pero nadie la ha
  escrito ni firmado.

---

## 5. Qué queda inconsistente con lo ya publicado, bajo cada lectura

- Bajo A: ninguna cifra publicada (README, cifras-canonicas) se movería
  hoy mismo -- nadie está proponiendo recomputar ahora --, pero el
  argumento que Nicolás usó ayer para descartar las 10 filas deja de
  sostenerse tal como está escrito, y eso exige una nota de corrección
  de razonamiento fechada, aunque la conclusión práctica (las 10 se
  quedan fuera, por el problema aparte de `sesion_objetivo`) no cambie.
- Bajo B: nada publicado cambia; es la lectura consistente con lo que ya
  está en producción, en el guardia y en el pre-registro congelado. El
  costo es que la segunda verificación permanente, si se estaba
  imaginando como un mecanismo que corrige valores ya verificados, queda
  descartada de raíz -- conviene decirlo así de explícito ahora, no
  dejarlo para cuando alguien la proponga de nuevo.

---

## 6. Lo que puede hacerse sin esperar esta decisión

Correr la verificación más veces al día, o más tarde en la noche, no
depende de esta pregunta mientras solo toque filas que hoy están en
`pendiente`: es exactamente lo que `verificar_apertura_pendientes()` ya
hace cada vez que se invoca (desde `snapshot.py`, el dashboard, o a
mano), y la restricción `UNIQUE(fecha_senal, ticker)` junto con el modo
de inserción que se abstiene si la fila ya existe garantizan que nunca
va a pisar una fila ya verificada aunque se la llame dos veces sobre la
misma. Lo que sí depende de la pregunta es únicamente si esa segunda
pasada puede alguna vez cambiar un valor ya escrito -- eso es lo que la
Lectura B cierra y la Lectura A parcialmente abriría (parcial, por el
problema de `sesion_objetivo` explicado en la sección 4).

---

## Decisión de Nicolás -- no tomada acá

No elijo entre A y B. Si hay que nombrar una asimetría entre los dos
argumentos: la Lectura B es la que ya opera en el guardia, en la regla
de `datos.md` y en el pre-registro congelado de GEMELO, así que
adoptarla formalmente no cambia nada en la práctica, solo la hace
explícita. La Lectura A es la que el proyecto aplica de hecho al campo
`estado`, y tiene a su favor que la propia acta de réplica
(`DECISIONES.md` §16) usó la palabra "sello" para excluir
justamente eso. Ninguna de las dos tiene un acta que la haya declarado
como principio general -- las dos son generalizaciones mías de
precedentes puntuales, y por eso la pregunta sigue abierta y esto es un
expediente, no un veredicto.
