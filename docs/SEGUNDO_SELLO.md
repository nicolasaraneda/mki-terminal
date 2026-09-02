# El segundo sello

**Diseño. Fecha: 1-sep-2026. Frente B de la sexta corrida autónoma.**
Nada de esto está activado: no corre ningún timer, no lo invoca `mki`, y
la regla que lo gobierna espera la firma de Nicolás (§9).

El arnés ejecutable vive en `GEMELO/SEGUNDO_SELLO/segundo_sello.py`, con
`tests/test_segundo_sello.py`. Este documento es el diseño; el arnés es la
contraprueba de que el diseño no es prosa.

> **Qué es, en una frase.** Volver a preguntarle a la fuente, más tarde y
> desde la misma máquina, qué sirve hoy para una fecha que ya está
> sellada — y **anotar la respuesta al lado, jamás encima**.

---

## 0. Antes de nada: la premisa del encargo está mal, y la medí

El encargo, `GEMELO/resultados/replica_una_pagina.md` y el docstring de
`GEMELO/CONDICIONAL/condicional.py` describen el incidente del 28 y el
31 de agosto como **«la fuente revisó su historia después»**, con
`dif_pp` de **3.47** y **3.49**.

Lo medí antes de citarlo, en solo lectura, el 1-sep-2026. Los tres puntos
que siguen corrigen esa frase, y el tercero es el que cambia el diseño.

**(a) Ningún precio fue revisado.** Sobre las **25 fechas selladas** que
llevan `sox_usado_pct` (la columna existe desde plataforma 5.0; la
primera es 2026-07-27), el arnés da **23 PARIDAD, 2 BARRA_RETIRADA y
CERO divergencias de valor**. La tasa de reproducción exacta es
**23/25 = 92.0%, IC95 Wilson [75.0, 97.8]**. En ninguna fecha la fuente
sirve hoy un precio distinto del que sirvió al sellar.

**(b) Lo que pasó es que la fuente RETIRÓ una sesión entera.** Hoy Yahoo
no tiene barra de `^SOX` para el **2026-08-28**, y no la tiene en ninguna
de las cuatro formas de pedirla que probé (`download` con `period`, con
`start`/`end`, con `period="1y"`, y `Ticker.history`). No es un precio
distinto: es una barra ausente. Y no es solo el `^SOX`: de 19 símbolos
del universo que revisé, **10 perdieron esa fecha** (`^SOX`, `SMH`,
`^GSPC`, `ASML`, `QCOM`, `TXN`, `ARM`, `UMC`, `BHP`, `FCX`) y **9 la
conservan** (`NVDA`, `AMD`, `INTC`, `MU`, `TSM`, `AVGO`, `MSFT`, `GOOGL`,
`META`) — **10/19 = 52.6%, IC95 [31.7, 72.7]**.

**(c) El 3.47 no es la diferencia: es un artefacto del ffill.** El
`sox_reconstruido_pct` que `condicional.py` calcula para el 28-ago es
`0.00`, y sale así porque `GEMELO/datos.py` hace ffill acotado sobre un
marco multi-ticker: el hueco se rellena con el cierre del 27 y el retorno
del 28 sale exactamente cero. Bajo la lógica de la propia producción
—`motor.prediccion_apertura_al` descarga el `^SOX` **solo**, sin ffill
cruzado— la diferencia del 28-ago no es 3.47 sino **5.80 pp**. La cifra
del 31-ago sí reproduce: **3.4914 pp**.

**Lo que la corrección NO toca.** La conclusión de la tabla «Dos
mecanismos distintos» de `replica_una_pagina.md` —que la réplica no
habría detectado esto, porque dos máquinas leyendo la misma fuente en el
mismo instante sellan el mismo dato— **sobrevive intacta y sale
reforzada**: una barra retirada tres días después es todavía menos
visible desde una segunda máquina que un precio revisado. Lo que cambia
es el nombre del fenómeno y la cifra. La fila «Ejemplo real de la OTRA
falla» de esa tabla debería decir **«la fuente retiró la sesión del
2026-08-28 para ~la mitad del universo; el sello no es reproducible, y no
por eso está mal»**, con 5.80 y 3.49 pp según qué lógica se use para
reconstruir. Esa corrección va al ejecutable y al documento; acá queda
declarada, no aplicada sobre archivos de otro frente.

### 0.1 La evidencia dura: el sello es coherente y la fuente no

Dos filas selladas con **tres días de diferencia** implican el mismo
cierre del 28-ago, y ese cierre hoy no existe en ninguna parte:

| Fila sellada | Valor | Cierre del 28-ago que implica (banda por redondeo a 2 decimales) |
|---|---|---|
| snapshot 2026-08-28, `sox_usado_pct` | −3.47 | [11469.26 , 11470.45] |
| snapshot 2026-08-31, `sox_usado_pct` | +0.57 | [11469.10 , 11470.24] |

Las bandas se solapan en **[11469.26 , 11470.24]**. Dos sellos
independientes, tomados con 72 h de diferencia, coinciden en un valor que
la fuente hoy no sirve. **La producción no vio un dato roto: vio un dato
real que la fuente después retiró.** Es la diferencia entre un incidente
de máquina y una regresión de la fuente, y este frente existe porque el
proyecto no tenía forma de distinguirlos.

### 0.2 La ventana en la que desapareció, acotada sin suponer nada

- A las **2026-08-31T22:15:03Z** la barra **existía**: el sello de ese día
  vale +0.57%, y ese número solo es computable con una barra del 28
  distinta de la del 27. (Verificación cruzada: `0.50/0.88 = 0.568` y
  `0.20/0.35 = 0.571` desde las betas selladas de `000660.KS` y
  `2330.TW`.)
- A las **2026-09-01T16:12Z** la barra **no existía** (medido, cuatro
  formas de pedirla).
- **Ventana: ≈18 horas, y el evento ocurrió ≥ 3 días de calendario
  después de que la barra naciera.**

Ese «≥ 3 días» es el único hecho que la evidencia fija sobre el
**cuándo**, y es el que gobierna la §5.

### 0.3 El costo medido, en filas

Volver a correr `motor.prediccion_apertura_al` hoy, sobre las mismas
fechas:

| Fecha de emisión | Filas | Reproduce | Qué pasa |
|---|---|---|---|
| 2026-08-27 | 8 | **8/8 exacto** (0.00 en apertura y en beta) | nada |
| 2026-08-28 | 8 | **0/8** | el signo se da vuelta: sellado −3.19…−0.32 → hoy +2.20…+0.23 |
| 2026-08-31 | 8 | **0/8** | el signo se da vuelta: sellado +0.50…+0.04 → hoy −2.69…−0.26 |

Las betas de esas dos fechas también se corren entre 0.01 y 0.04, porque
la ventana móvil de 120 días perdió una observación.

**Nada publicado se mueve.** Las 16 filas afectadas están todas en estado
`pendiente`: no entraron a la ventana sellada de **n = 248** que el
`README.md` publica. El incidente se detectó antes de que tocara una
cifra. Esta es la única razón por la que este documento puede escribirse
sin una errata adjunta.

**Pero hay una consecuencia viva, y no es chica.** Todo lo que
*reconstruye* al campeón desde el Yahoo de hoy —`backtest/`,
`GEMELO/ventana_larga.py`, `GEMELO/CONDICIONAL/condicional.py`, y
cualquier corrida futura del veredicto 5.1 cuya ventana incluya el
2026-08-28— está reconstruyendo, en esas dos fechas, **un campeón de
signo contrario al que se selló**. No es una hipótesis: es la tabla de
arriba. Queda declarado acá y no se corrige desde este frente.

### 0.4 Por qué la máquina estuvo en verde las dos noches

`snapshot.salud_descarga` pregunta, por ticker, si la serie tiene **alguna
barra en los últimos 7 días** hasta la fecha. Un hueco en el medio de la
serie es, por construcción, invisible para ese chequeo — y por lo tanto
para el vigía, que lee ese mismo resultado. `data/vigia.log` lo confirma
textualmente las dos noches: `descarga: 28/28 completa` · `todo OK — sin
alerta` el 2026-08-28T23:00Z y el 2026-08-31T23:00Z.

**La máquina no falló. El chequeo que existe no puede ver esta clase de
falla.** Eso es lo que este mecanismo agrega, y es todo lo que agrega.

---

## 1. B1 · Es aditiva, nunca correctiva

**Dónde viven las filas nuevas.** En una base propia, nueva,
`data/segundo_sello.db`, tabla `observaciones`:

```
observaciones(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  corrida            TEXT NOT NULL,   -- identifica una pasada de observación
  fecha_observada    TEXT NOT NULL,   -- la sesión sobre la que se pregunta
  ticker             TEXT NOT NULL,
  cierre             REAL,            -- lo que la fuente sirve HOY, o NULL
  hay_barra          INTEGER NOT NULL,-- si la fuente tiene barra para esa fecha
  horizonte_sesiones INTEGER,         -- a cuántas sesiones del sello se preguntó
  observado_en       TEXT NOT NULL,   -- cuándo se preguntó (UTC)
  UNIQUE (corrida, fecha_observada, ticker)
)
```

`cierre = NULL` con `hay_barra = 0` **no es** `cierre = 0`. La distinción
es el corazón del registro: el único incidente medido hasta hoy es una
barra que se fue, no un precio que cambió, y un esquema que solo guardara
precios no lo vería.

**Por qué esto no viola «las filas selladas jamás se reescriben».**

1. **No escribe un solo byte en `senales.db`.** La única vez que este
   mecanismo abre esa base es en `contrastar`, con `mode=ro`, y hay un
   test que verifica que el `mtime` de la base real no cambia.
2. **Una observación posterior no corrige a la anterior: se suma.** Solo
   hay `INSERT OR IGNORE`. No hay una sola sentencia que actualice,
   borre, reemplace o altere el esquema — verificado por un test que mira
   los literales de cadena del AST, no la prosa.
3. **El significado de la fila sellada no cambia.** La fila del 28-ago
   sigue diciendo exactamente lo que decía: *«a las 22:15:03 UTC del
   2026-08-28 el modelo vio un SOX de −3.47% y predijo esto»*. El segundo
   sello agrega una segunda frase: *«a las 16:30 UTC del 2026-09-01 la
   fuente ya no servía la barra en la que esa frase se apoyaba»*. **Las
   dos son verdad. Ninguna corrige a la otra.**
4. **Y —esto importa— el diseño no depende de una lectura sin firmar.**
   El Frente A dejó abierto si la verificación es parte del sello
   (Lectura A) o no (Lectura B), y midió que la Lectura B ya está
   aplicada por hook sin que nadie la firmara. Como el segundo sello **no
   escribe en `senales.db` bajo ninguna circunstancia**, es compatible con
   las dos lecturas y no necesita que se resuelva ninguna. Esa
   independencia fue un requisito del diseño, no un accidente.

**Deuda declarada.** `.gitignore` excluye `*.db`, así que este registro
vive **solo en el disco de esta máquina** — que es exactamente el modo de
morir que el proyecto ya sufrió una vez. Un registro de auditoría que
depende de un SSD no es un registro de auditoría. **Falta un export
versionado** (un CSV en `data/backups/`, mismo criterio que el resto).
**No está construido**, y es trabajo mecánico una vez firmada la §9.

---

## 2. B2 · Es ciega a la primera, y acá está la contraprueba

### 2.1 Cómo se garantiza la ceguera

El mecanismo tiene tres fases, y la que **produce el número** no puede
mirar el sello:

| Fase | Qué hace | ¿Puede ver el sello? |
|---|---|---|
| `observar` | pregunta a la fuente qué sirve hoy para una lista de fechas | **NO** — recibe fechas como argumento; no abre ninguna base |
| `registrar` | inserta lo observado en su propia base | **NO** |
| `contrastar` | recién acá se abre `senales.db`, en `mode=ro` | sí, y solo después de que la observación ya está escrita |

La garantía no es una promesa: es un test sobre el **AST**. Para
`observar`, `proveedor_yahoo` e `id_corrida`, se recorre el árbol
sintáctico y se prohíbe cualquier referencia a `senales`, `snapshot`,
`motor`, `sqlite3`, `RUTA_SENALES`, `_sellado`, `contrastar` o
`leer_observaciones`. Un segundo test verifica que la firma de `observar`
no acepta ninguna ruta de base. Si mañana alguien le pasa el valor
sellado «para comparar en el momento», el test revienta con el motivo
escrito: *eso es una confirmación, no una verificación*.

La descarga está **duplicada a propósito** respecto de
`motor._datos_crudos`: si compartiera la caché en memoria del motor,
observaría el mismo objeto que la producción ya usó y no vería nada
nunca. Misma disciplina que `GEMELO/datos.py` con sus 13 feeds.

### 2.2 La contraprueba, ejecutable

Un mecanismo que nunca discrepa no verifica: confirma. `contraprueba()`
corre **dos ramas sobre la misma serie**:

- **Rama de control** — la serie que reproduce el sello, sin tocar. Debe
  dar `PARIDAD`.
- **Rama perturbada** — la misma serie con el cierre de la fecha escalado
  para mover el retorno **exactamente `perturbacion_pp` puntos**. Debe dar
  `DIVERGENCIA_DE_VALOR`, **y con la magnitud inyectada**, no con «algo
  distinto de cero».

Las dos ramas hacen falta: sin el control negativo, un mecanismo que
gritara «divergencia» siempre pasaría la prueba positiva. Los tests
recorren `±0.10`, `±0.50`, `1.00`, `2.00` y `−1.50` pp y exigen que la
magnitud reportada coincida con la inyectada dentro de 0.01 pp; y una
perturbación de `0.001` pp —por debajo de la tolerancia— debe seguir
dando `PARIDAD`, porque el sello está redondeado a dos decimales y
confundir redondeo con hallazgo es la forma barata de fabricar
divergencias.

### 2.3 La contraprueba se cobró una pieza el mismo día

La primera corrida del arnés contra la base real reportó el **2026-08-07
como divergencia de 0.3371 pp**. Era falso. La observación cubría **solo
las 25 fechas selladas**, y el 2026-08-06 no está sellado porque ese día
no hubo snapshot: el retorno derivado abarcó dos sesiones en vez de una.
**Es exactamente el mismo error de índice mutilado que produce el 3.47
por ffill** (§0c) — la misma trampa, dos veces, en dos frentes distintos.

De ahí sale un parámetro congelado más: **la guardia de cobertura**. Si la
observación no cubre **todas las sesiones del calendario XNYS** del rango,
el veredicto es `SIN_SEGUNDA_OBSERVACION` —una ausencia declarada— y
**nunca** una divergencia. Con la guardia puesta, el 2026-08-07 vuelve a
`PARIDAD` y el 2026-08-31 deja de leerse como «la fuente revisó el precio
del 31» para leerse por su causa real: `BARRA_RETIRADA`, sesión retirada
`2026-08-28`, par usado hoy `[2026-08-27, 2026-08-31]`.

Que el arnés se haya encontrado su propio defecto en la primera corrida
es la evidencia más fuerte que puedo ofrecer de que puede discrepar.

### 2.4 Lo que se mantiene fijo, y por qué eso NO viola la regla 1 de la casa

`contrastar` deriva su número con **la misma función de la producción**
(`motor._ultimo_mov_no_cero`, pura, sin red). Parece una violación de
«una verificación que usa el mismo mecanismo que produjo la cifra no es
una verificación» (`DECISIONES.md` §52), y no lo es, por una razón que
hay que decir explícita:

> **El objeto bajo prueba acá es el DATO, no el mecanismo.** Mantener el
> mecanismo fijo es lo que hace la diferencia *atribuible*. Si cambiaran
> los dos a la vez, una discrepancia no diría nada.

La contrapartida, que va en la §6 con todas las letras: **este mecanismo
no puede decir si el modelo está bien.** Solo si sus insumos siguen
siendo los mismos. La vara independiente que juzgaría el modelo es una
segunda fuente de precios, y `DECISIONES.md` §52 ya declaró que **esa
vara no existe en este repo** — no es una vara pendiente de instalar, es
una vara que no existe.

---

## 3. B3 · La regla canónica, congelada el 1-sep-2026, ANTES de la primera fila

> ### REGLA CANÓNICA — congelada 1-sep-2026
>
> **La fila canónica es SIEMPRE la primera. El segundo sello no produce
> una fila canónica en ningún caso —ni siquiera cuando la primera es
> demostrablemente irreproducible—. Su salida es un testigo, no un
> reemplazo.**

Está congelada acá, con fecha, antes de que el mecanismo haya escrito una
sola fila contra la base real de forma persistente. En el código, esto se
traduce en que `contrastar` devuelve `canonica = None` **en todas sus
ramas**, con un test que lo recorre.

**La regla no es una preferencia estética: es lo que la evidencia dice.**
Aplicá «gana la más reciente» a las dos fechas del §0.3 y el resultado es
que **16 predicciones selladas se reemplazan por valores de signo
contrario derivados de una serie amputada**. La observación posterior no
es la mejor: es solamente la posterior. Eso está medido, no argumentado.

### Las alternativas, con su consecuencia

| | Regla | Qué implica | Consecuencia medida |
|---|---|---|---|
| **R-A** | **La primera gana siempre** *(propuesta)* | El segundo sello registra y no decide nunca. | Preserva la constitución sin excepciones, es compatible con las dos lecturas del Frente A, y **no cierra ninguna puerta**: cualquier otra regla se puede adoptar después con el registro ya acumulado. |
| **R-B** | Gana la observación con más barras | Corregiría errores reales de dato. | En el caso medido **abstendría bien** (la posterior tiene menos barras). Pero decide en caliente sobre un criterio evaluado ese mismo día; exige que el sello hubiera guardado cierres crudos, cosa que **no hizo y no se puede agregar hacia atrás**; y **reescribe una fila sellada**, prohibido bajo *cualquiera* de las dos lecturas del Frente A. |
| **R-C** | Discrepancia ⇒ la fecha sale del track record | Máxima pureza aparente. | Habría sacado **16 filas** por un defecto de la fuente que **no afectó al sello**. Le da a un mecanismo nuevo poder de veto sobre un experimento que corre desde julio. Y las filas que saca son justo las que la fuente dañó: **es la forma de quitar los días malos, con mejor excusa**. |

**Recomendación, marcada como tal: R-A.** Es la única que no le da poder
al mecanismo nuevo sobre el experimento viejo. **Espera firma (§9).**

**Lo que la congelación implica y hay que decir ahora, no cuando duela:**
si en seis meses aparece un caso donde la primera está demostrablemente
mal y la segunda demostrablemente bien, **la regla sigue siendo R-A** y
lo que corresponde es una errata fechada en `DECISIONES.md`, no un
cambio de regla. Si eso se quisiera cambiar, se cambia **antes** de saber
sobre qué fila va a caer, y se documenta como lo que sería: mover el
criterio después de ver el dato.

---

## 4. B4 · La discrepancia es un dato, no un error

### 4.1 Qué se registra

Lo que ya está construido: la tabla `observaciones` de la §1 — una fila
por `(corrida, fecha, ticker)` con el cierre, si hay barra, el horizonte
y el instante de la pregunta. Es un registro **crudo**: no guarda
veredictos, guarda observaciones. Un veredicto se recomputa; una
observación perdida no se recupera.

Lo que **falta construir, y espera la firma de la §9**, es la tabla de
contrastes — el equivalente exacto de lo que `replica.py` hace con las
divergencias de la réplica:

```
contrastes(
  id, fecha_sellada, corrida, horizonte_sesiones,
  veredicto,                -- PARIDAD | DIVERGENCIA_DE_VALOR | BARRA_RETIRADA
                            -- | BARRA_APARECIDA | SIN_SEGUNDA_OBSERVACION | SIN_SELLO
  final,                    -- las dos ausencias NO son finales
  sellado_pct, observado_pct, dif_pp,
  sesiones_retiradas,       -- JSON: qué sesiones desaparecieron
  par_usado_hoy,            -- JSON: [previa, movimiento] del retorno de hoy
  cobertura_verificada,     -- si se contrastó contra el calendario XNYS
  canonica,                 -- SIEMPRE NULL hasta que la §9 esté firmada
  detectado_en
)
```

`canonica` en NULL, siempre, por el mismo motivo por el que
`replica.py:resuelto_como` está en NULL: fijarlo sería implementar una
regla que nadie firmó.

### 4.2 Qué se puede aprender de la serie de discrepancias

Las cuatro cosas, en orden de lo que ya sé medir a lo que todavía no:

1. **La tasa de retiro de sesiones**, con su intervalo. Hoy: **1 fecha de
   752 sesiones XNYS** en tres años de `^SOX` = **0.13%, IC95 Wilson
   [0.02, 0.75]**. Ese denominador es lo que ancla todo lo demás.
2. **La unidad de análisis es la FECHA, no el símbolo-fecha.** El único
   evento medido golpeó **10 de 19 símbolos la misma fecha**: los
   símbolo-fecha no son independientes, y contar 10 hallazgos donde hay 1
   evento infla el n exactamente como el clúster de día infla el n de la
   ventana sellada (`condicional.py`, condición (a); ICC 0.403, DEFF 3.63
   sobre 248 filas). **Cualquier intervalo sobre esta serie se computa por
   fecha.** Queda congelado en la §7.
3. **La latencia entre el sello y el retiro**, que hoy es lo único que
   este mecanismo puede medir y nadie más puede: la escalera de horizontes
   da, por fecha, el **primer horizonte en el que se detecta**. Es una
   medición **censurada por intervalo** (sé que ocurrió entre el horizonte
   *k* y el *k+1*, no cuándo), así que el estimador correcto es una curva
   de supervivencia, **no un promedio de días**. Declarado antes de tener
   un solo dato, para que después no se publique una media.
4. **Si una barra retirada vuelve.** Hoy nadie lo sabe, y es una pregunta
   con consecuencia directa: si vuelve, `BARRA_RETIRADA` es un estado
   transitorio y la reconstrucción se cura sola; si no vuelve, el
   `^SOX` del 2026-08-28 se perdió para siempre y toda reconstrucción
   futura de esa ventana es estructuralmente distinta del sello. El
   registro aditivo contesta esta pregunta sin que nadie tenga que
   acordarse: la fila de mañana convive con la de hoy.

---

## 5. B5 · Cuándo corre — y por qué NO fijo una hora

**La evidencia no alcanza para fijar una hora, y decirlo es parte del
diseño.** Tengo **un** evento. Uno. Con n=1 no se elige una hora: se
inventa una con cara de precisa.

Pero la evidencia sí fija dos cosas, y las dos son útiles.

### 5.1 Lo que la evidencia SÍ fija: una cota inferior al horizonte

El único evento medido **era invisible a una sesión de distancia**. La
barra del 28-ago seguía ahí a las 22:15:03Z del 31-ago (§0.2). Entonces:

- Un segundo sello **a T+1 sesión** sobre el sello del 28-ago habría
  devuelto **PARIDAD** y habría declarado verificado un sello que no es
  reproducible.
- Ese mismo diseño a T+1 sobre el sello del **31-ago** sí habría
  detectado algo el 1-sep — pero **le habría puesto la fecha equivocada
  al hallazgo**, atribuyéndolo al 31 cuando el daño es del 28.

> **Un diseño de un solo horizonte, y encima corto, es el que la evidencia
> disponible refuta.** El horizonte tiene que ser **≥ 2 sesiones**, y no
> puede ser uno solo.

### 5.2 Lo que la evidencia NO fija, y no va a fijar nunca

Se podría pensar en una fase de medición que observe a varios horizontes
hasta acumular *k* eventos y ahí congelar el bueno. **Ese plan no
funciona, y lo puedo mostrar con el número.** A la tasa medida —1 evento
en 752 sesiones— acumular 5 eventos toma **unos 15 años**; con el extremo
optimista del IC95 (0.75%), **unos 3.5 años**; con el pesimista (0.02%),
más de un siglo.

**Conclusión honesta: la curva de asentamiento de esta fuente no es
caracterizable desde la producción de este proyecto.** El evento es
demasiado raro. Cualquier regla de parada por conteo de eventos sería
teatro.

### 5.3 Lo que se hace entonces: no elegir

Como el horizonte no se puede elegir midiendo la distribución, se elige
para **acotar la exposición**, y la forma barata de acotarla es no elegir:

**La escalera, congelada: T+1, T+3, T+7 y T+30 sesiones.** Cada fecha
sellada se observa cuatro veces. `HORIZONTES_SESIONES = (1, 3, 7, 30)`.

- **T+1** es el control: casi siempre debería dar `PARIDAD`, y su tasa de
  paridad es el termómetro de que el mecanismo no está roto.
- **T+3** es donde cayó el único evento medido.
- **T+7** cubre una semana entera de la fuente.
- **T+30** es el que atraparía un asentamiento lento — la clase que nadie
  vio todavía y que, si existe, hoy es invisible para el proyecto entero.

**Costo:** cuatro descargas de solo lectura por fecha. Sin gasto de
Anthropic, sin salida de red hacia nadie (el segundo sello **no manda
Telegram nunca**, así que `modo.py` le es indiferente: corre igual en
titular o en sombra sin duplicar una sola voz).

### 5.4 La hora del día: 22:15 UTC, por diseño experimental

**No por intuición.** La producción sella a las 22:15 UTC. Si el segundo
sello corre a la misma hora del reloj, **la única dimensión que varía es
el horizonte**. Si corriera a otra hora, cada hallazgo tendría dos
explicaciones (pasó el tiempo / cambió el momento del día) y ninguna
sería separable. Es la misma razón por la que el nivel 3 de
`comparar_sombra.py` excluye los timestamps: comparar relojes no es
comparar sellos.

### 5.5 Lo que NO pude determinar

- **Cuándo desaparece una barra, dentro de la ventana de 18 h.** No hay
  observación intermedia. Se mediría trivialmente si el segundo sello ya
  existiera; hoy no existe, y ese es el punto.
- **Si la barra vuelve.** Hoy, 1-sep-2026, sigue ausente. Nada más.
- **Si 0.13% es la tasa de esta fuente o de este año.** Un evento no
  distingue entre «pasa cada tanto» y «Yahoo tuvo una regresión el
  1-sep-2026». Declarado como lo que es: n=1.
- **Si otras fuentes de la cadena (FX, índices locales) sufren lo mismo.**
  Solo medí el `^SOX` y 18 acciones/ETF. Los pares FX y los índices
  locales no los revisé.

---

## 6. B6 · Qué NO arregla

Sección explícita, porque la mitad del valor de un mecanismo nuevo es que
la gente sepa lo que **no** hace.

1. **No cubre la clase de falla de la réplica.** Máquina caída, dormida o
   colgada: el segundo sello vive en la misma máquina y muere con ella.
   Las cuatro fechas de incidente de producción que `replica_una_pagina.md`
   documenta (07-05, 07-29, 08-03, 08-05) **este mecanismo no las habría
   visto**. Son piezas complementarias, no alternativas.
2. **No arregla las 25 filas históricas del defecto de `snapshot.py:140`**
   (las 10 mal pareadas + las 15 huérfanas). Ese defecto vive en
   `sesion_objetivo`, que es un campo de **emisión**, escrito al sellar.
   El segundo sello no escribe en `senales.db` bajo ninguna
   circunstancia, así que no las toca ni podría. El Frente A ya midió que
   corregir ese campo está prohibido **bajo las dos lecturas**.
3. **No releva el gatillo de la Etapa 5.1.** Ni lo acerca ni lo aleja: no
   agrega filas verificadas ni cambios de régimen. Sigue siendo N≥150
   vivas + un cambio de régimen, o 3 meses, lo que llegue primero, y sigue
   siendo decisión de Nicolás.
4. **No toca el modelo.** `motor.py` intacto, `MODELO_VERSION` sigue en
   4.6.0, la regla cero se mantiene entera.
5. **No dice si el modelo está bien.** Mantiene el mecanismo fijo a
   propósito (§2.4). Solo dice si los insumos siguen siendo los mismos.
6. **No corrige un sello. Nunca.** Ni siquiera cuando el sello está
   demostrablemente construido sobre un dato que la fuente retiró — que
   es exactamente el caso del 2026-08-28, y el sello se queda igual.
7. **No detecta un valor que la fuente sirvió mal desde el principio.**
   Las dos observaciones ven el mismo número equivocado. Para eso hace
   falta una segunda **fuente**, y `DECISIONES.md` §52 ya declaró que esa
   vara no existe en este repo. `DECISIONES.md` §49 recomendó además no
   comprarla hoy, y el análisis de ese expediente **no cubre este canal**:
   su teorema es sobre factores de ajuste que se cancelan en un cociente
   `open/close`, y una sesión retirada no se cancela con nada.
8. **No protege la verificación.** `gap_pct` y `retorno_real_pct` salen de
   la apertura y el cierre de los tickers objetivo, que este arnés no
   observa. Extenderlo ahí es posible y **está deliberadamente fuera de
   este diseño**: chocaría de frente con la pregunta A/B que el Frente A
   dejó sin firmar, y este mecanismo se diseñó para no depender de ella.
9. **No hace que el vigía vea el hueco.** El vigía queda intacto. Cablear
   el segundo sello a una alerta es otra decisión, con su propio costo
   (un sexto/séptimo job, un canal más de ruido) y no se propone acá.
10. **No da una tasa confiable de «cada cuánto pasa esto».** n=1.
11. **No se corre solo.** No hay timer, no hay cron, `mki` no lo conoce, y
    hay un test que verifica que ningún archivo de `systemd/` ni de
    `launchd/` lo menciona. Si algún día alguien lo agenda, ese test lo
    obliga a pasar por una decisión explícita.

---

## 7. B7 · El corte de método

### 7.1 Del lado de adentro — congelado antes de la primera fila

| Qué | Valor | Por qué está adentro |
|---|---|---|
| **La regla canónica** | R-A: gana siempre la primera | §3. Si se pudiera elegir mirando la discrepancia, no sería una regla. |
| **La tolerancia** | `TOLERANCIA_PP = 0.005` | Media unidad del último decimal que la producción sella (`round(..., 2)`). No es una intuición: **23 de 25 fechas reproducen con diferencia exactamente 0.00**. |
| **El vocabulario de veredictos** | 6 nombres, 4 finales | `SIN_SELLO` y `SIN_SEGUNDA_OBSERVACION` **no son finales y no son paridad**. Lección heredada de `comparar_sombra.py`: «nada = nada» nunca es paridad. |
| **La guardia de cobertura** | sin calendario completo no hay hallazgo | §2.3. Se ganó en la primera corrida, contra el propio arnés. |
| **La unidad de análisis** | la **fecha**, no el símbolo-fecha | §4.2.2. Un evento golpeó 10 símbolos: contarlos como 10 infla el n. |
| **La aditividad** | solo `INSERT`, base propia, nunca `senales.db` | §1. Verificado por test sobre el AST. |
| **La ceguera + la contraprueba** | test de AST + dos ramas | §2. Sin contraprueba el mecanismo no se activa. |
| **El horizonte mínimo** | ≥ 2 sesiones | §5.1. Derivado del dato, no elegido. |

### 7.2 Del lado de afuera — ajustable, y bajo qué condición

| Qué | Condición |
|---|---|
| **La escalera de horizontes** | **Solo aditiva.** Agregar un horizonte nunca re-etiqueta una fila existente (entra como otra `corrida`). **Quitar** uno exige un acta en `DECISIONES.md`, porque cambia qué se habría detectado. |
| **El conjunto de tickers observados** | **Solo aditivo**, mismo argumento. |
| **La tabla `contrastes` y el export versionado** | Mecánicos una vez firmada la §9. |

### 7.3 Lo que NO es ajustable nunca

- **Bajar la tolerancia después de ver una discrepancia.** Es fabricar un
  hallazgo.
- **Subirla después de ver una discrepancia.** Es taparlo.
- **Usar el segundo sello para excluir filas de una cifra publicada sin
  un criterio declarado antes.** Un filtro elegido después de ver qué
  filas saca es `keep="last"` con mejor excusa. Si alguna vez se quiere
  excluir el 2026-08-28 de una medición, **se declara antes de correrla y
  la cifra se publica con y sin la exclusión**, como ya se hizo con
  `excluir_cero`.

### 7.4 Cuántos «intentos» consume, en el sentido del DSR

- **Como registro de auditoría: CERO.** No selecciona un modelo, ni una
  configuración, ni un hiperparámetro. Observar no es intentar.
- **En el momento en que su salida se use como criterio de exclusión de
  filas para una cifra publicada: ese criterio es UN intento**, declarado
  antes de correr, y se suma al conteo de la cifra que toca — no a un
  conteo propio de este documento. (Para referencia del orden de
  magnitud: el WS2b lleva **N=9**.)
- **Si se probaran varios criterios de exclusión —«sacar la fecha», «sacar
  el símbolo», «sacar la ventana»— cuentan todos**, incluidos los
  descartados. El DSR miente si el conteo se hace a conveniencia, y este
  mecanismo, por su naturaleza de «acá hay filas raras», es una fábrica
  de tentaciones de ese tipo. Queda dicho antes de que aparezca la
  primera.

---

## 8. Qué está construido y qué no

**Construido y probado** (`GEMELO/SEGUNDO_SELLO/segundo_sello.py`,
`tests/test_segundo_sello.py`, 32 tests):

- Las tres fases: `observar` (ciega), `registrar` (aditiva), `contrastar`
  (lectura, `mode=ro`).
- La contraprueba de dos ramas, con la magnitud verificada.
- La guardia de cobertura contra el calendario XNYS.
- Los tests de ceguera (AST), de aditividad (AST sobre los literales SQL),
  de dirección de import (nada de la ruta de sellado lo menciona), de que
  ningún timer lo invoca, y de que `canonica` es `None` en todas las
  ramas.

**No construido, a propósito, hasta la firma:**

- La tabla `contrastes` (§4.1) — persistir un veredicto se parece
  demasiado a decidir.
- El export versionado del registro (§1, deuda declarada).
- El job que lo corra. Hoy nadie lo invoca.
- La corrección de la fila «Ejemplo real» de
  `replica_una_pagina.md` (§0) — es un archivo de otro frente.

---

## 9. Lo que espera la firma de Nicolás

**Una sola cosa bloquea, y es la de la §3:**

> **¿Se adopta R-A —la primera fila gana siempre, el segundo sello nunca
> produce una fila canónica— como regla congelada?**

Está escrita, fechada y argumentada con evidencia medida. La
recomendación es sí. Las alternativas R-B y R-C están en la tabla de la
§3 con su consecuencia medida.

**Y tres decisiones que son mecánicas una vez tomada ésa:**

1. **Si el segundo sello se activa o no.** Puede quedarse como código que
   existe y se prueba —igual que `replica.py`— indefinidamente. No hay
   urgencia: no hay ninguna cifra publicada en riesgo hoy (§0.3).
2. **Si sus hallazgos van a Telegram.** La propuesta es **que no**: el
   evento es demasiado raro (0.13%) para justificar un canal de alerta
   propio, y un canal que dispara una vez cada tres años es un canal que
   nadie recuerda leer. Alternativa: que el vigía lo mire, si algún día se
   lo cablea.
3. **La retención del registro.** `observaciones` crece a razón de
   `4 horizontes × sesiones` filas por ticker y por año — unas 1000 filas
   anuales para un solo ticker. Es despreciable, y la propuesta es **no
   borrar nada nunca**: es un registro de auditoría, y el costo de
   guardarlo es menor que el de decidir qué tirar.

**Lo que NO decido acá, y no es mío:** si la pregunta A/B del Frente A se
resuelve, y en qué sentido. Este diseño se construyó **para no
necesitarla** (§1.4), y esa independencia es deliberada.

---

## 10. Cómo se revierte

Borrar `GEMELO/SEGUNDO_SELLO/`, `tests/test_segundo_sello.py` y
`data/segundo_sello.db`. **Eso es todo.** No hay nada más que deshacer:

- `motor.py`, `snapshot.py`, `senales.py`, `universo.py`, `alertas.py`,
  `calendarios.py`, `.env`, los timers y el modo de emisión **no se
  tocaron**, ni una línea.
- Ninguna fila sellada se escribió, se movió ni se leyó fuera de
  `mode=ro`.
- Ningún archivo de otro frente se editó.
- No se commiteó ni se pusheó nada.

---

## Procedencia de cada cifra de este documento

Todo lo de abajo se midió el **1-sep-2026** en esta máquina, en solo
lectura. Nada se cita de memoria.

| Cifra | De dónde sale |
|---|---|
| 23 PARIDAD / 2 BARRA_RETIRADA / 0 divergencias de valor sobre 25 fechas | `GEMELO/SEGUNDO_SELLO/segundo_sello.py` contra `senales.db` (`mode=ro`) y Yahoo, con las 44 sesiones XNYS del 2026-07-01 al 2026-09-01 |
| 23/25 = 92.0%, IC95 [75.0, 97.8] | `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py::wilson_ci` |
| 1 fecha de 752 sesiones = 0.13%, IC95 [0.02, 0.75] | `^SOX` 3 años vs. `exchange_calendars` XNYS + `wilson_ci` |
| 10 de 19 símbolos perdieron el 2026-08-28; 52.6%, IC95 [31.7, 72.7] | descarga de 19 símbolos vs. el mismo calendario |
| Cierre implícito del 28-ago, bandas solapadas en [11469.26 , 11470.24] | aritmética sobre `sox_usado_pct` sellado (−3.47 y +0.57) y los cierres de hoy |
| 5.80 pp (28-ago) y 3.4914 pp (31-ago) | el arnés, lógica de producción |
| 3.47 pp | `GEMELO/resultados/condicional_ventana_larga.json` — artefacto del ffill (§0c) |
| 16 filas con el signo dado vuelta; 8/8 exacto el 27-ago | `motor.prediccion_apertura_al` re-corrido contra `senales_ticker` |
| n = 248 de la ventana sellada publicada | `README.md` |
| ICC 0.403, DEFF 3.63 | `GEMELO/CONDICIONAL/condicional.py`, condición (a), citando `dos_ventanas.md` §0 |
| N = 9 intentos del WS2b | `CLAUDE.md`, Etapa 6.0.0 |
| `descarga: 28/28 completa` · `todo OK — sin alerta` el 28 y el 31 | `data/vigia.log` |
