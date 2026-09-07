# Pre-registro — señal larga v1 (riel de dinero)

**Congelado el 7-sep-2026, corrida 10, bloque 6a. Escrito y commiteado ANTES
de correr la primera especificación.** Una señal diseñada mirando su propio
resultado nace inválida; el orden no se negocia y por eso este archivo entra
al repositorio en un commit anterior al del cómputo.

## 1. La hipótesis, en términos económicos

**El retorno de un eslabón de la cadena de semiconductores anticipa el
retorno del eslabón inmediatamente aguas abajo, con un retardo del orden de
semanas.**

Por qué habría razón para que ocurra: la cadena tiene un orden físico de
facturación. El fabricante de equipo cobra cuando la fundición decide
ampliar capacidad; la fundición factura cuando produce la oblea, meses
después; el empaquetado factura después de eso; el centro de datos compra al
final. Los datos que revelan cada tramo se publican en ese mismo orden
—pedidos de equipo antes que ingresos de fundición— así que si el mercado
incorpora la secuencia con retardo, el precio de arriba contiene información
sobre el de abajo.

**La hipótesis nula económica, que es la que hay que vencer:** el sector se
mueve como un bloque; lo único que hay es beta común; y toda «anticipación»
observada es la misma noticia llegando a dos precios a la vez. La
especificación L2 existe específicamente para atacar esta alternativa.

## 2. Los horizontes

**20 y 60 días hábiles. Nada más.** No se prueba un tercer horizonte, ni
«20 y 60 y también 40 que quedó mejor».

## 3. Las tres especificaciones, declaradas por nombre antes de correr la primera

Son **tres y sólo tres**. Cada una suma al registro de intentos
(`dinero/registro_intentos.py`), hayan servido o no.

- **L1 — Contagio directo.** El retorno acumulado del eslabón de arriba en
  los últimos *h* días hábiles predice el retorno del eslabón de abajo en
  los próximos *h*. Es la forma más simple de la hipótesis y la que hay que
  descartar antes de complicar nada.
- **L2 — Impulso relativo.** Lo mismo, pero sobre el retorno de cada eslabón
  **residualizado contra la cesta del sector** (`SMH`): se le quita a cada
  eslabón el movimiento común y se pregunta si lo que queda arriba anticipa
  lo que queda abajo. Es el control de la hipótesis nula económica: si L1
  funciona y L2 no, lo que había era beta común y no cadena.
- **L3 — Dispersión entre eslabones.** La dispersión transversal entre los
  ocho eslabones hoy predice el retorno del eslabón de abajo. Prueba una
  hipótesis distinta —que la cadena se «tensa» antes de moverse— y no una
  variante de las anteriores.

**Agregación declarada por adelantado, para que no haya elección posterior:**
cada especificación produce **un** número por horizonte, agrupando los pares
adyacentes de la cadena. No se reporta el mejor par. La cadena, en orden:
materias primas → materiales y obleas → litografía y equipos → fabricación
de vanguardia → memoria → ensamblaje y prueba → diseño y EDA → demanda
final. Los eslabones se construyen como promedio equiponderado de los
instrumentos **verificados y comprables** de `docs/universo_operable.md`.

## 4. Las métricas

**Se reportan las dos, con la misma firmeza, y esta corrida NO elige cuál es
la primaria.** El encargo pide magnitud como primaria «bajo D3», pero la
enmienda V1-bis v2 que haría de la magnitud la métrica primaria **está
esperando la firma de Nicolás** (`espera_firma.md` §30) y hasta esa firma la
dirección sigue siendo bloqueante. Elegir aquí cuál manda sería resolver por
la vía del código una decisión que está declarada como humana.

- **Magnitud:** MAE del retorno predicho del eslabón de abajo, y **CRPS** de
  la densidad predictiva normal (media de la regresión, σ de los residuos),
  con `GEMELO.control_lineal.crps_normal`.
- **Dirección:** acierto de signo.

Ambas con intervalo de **clúster de fecha de emisión**, nunca puntual.

## 5. Las dos varas

1. **Predecir cero.** La vara de magnitud: un MAE que no le gana a decir «no
   se mueve» no es una predicción.
2. **La línea base aburrida del bloque 4a:** aporte fijo semanal a `SMH`.
   La vara económica, a la que se llega pasando la señal por
   `dinero/decision.py` y la cuenta en papel.

Para dirección se agrega la climatología del propio horizonte —la frecuencia
histórica de subidas— porque «acertar el 60 %» no dice nada si el 60 % de
los meses suben.

## 6. Qué refuta la hipótesis

- **Si L1 no le gana a predecir cero en MAE, con intervalo que excluya el
  cero, en ninguno de los dos horizontes**, la forma simple de la hipótesis
  queda refutada.
- **Si L1 gana pero L2 no**, lo que se midió fue beta común del sector, no
  transmisión por la cadena. La hipótesis, tal como está escrita en la §1,
  queda refutada igual: «el sector se mueve junto» no es «un eslabón
  anticipa al otro».
- **Si ninguna de las tres supera a ninguna de las dos varas**, la
  conclusión honesta es que los datos disponibles no traen señal larga
  detectable, y se escribe así. Eso es un resultado, no un fracaso.

## 7. Lo que este bloque NO va a poder concluir, declarado ANTES de correrlo

Esto se escribe por adelantado para que no se lea después como una excusa:

- **El DSR va a salir NO INTERPRETABLE, pase lo que pase.** El registro de
  intentos del riel largo queda en 3 con estas tres especificaciones, y las
  observaciones no solapadas a 60 días hábiles sobre 8 años son del orden de
  33 por par: no hay potencia para un Deflated Sharpe que signifique algo.
  Se reporta el número si se calcula, rotulado NO INTERPRETABLE, igual que
  el proyecto hizo en el WS2b cuando el PSR saturó en 1.0000 a 30 días.
- **Los datos NO son point-in-time.** `GEMELO/resultados/ventana_larga.md`
  ya midió la contaminación: sobre 198 filas comunes con el track record
  sellado, la reconstrucción de hoy coincide en el **91.4 %** y difiere en
  **17**, con un máximo de **31.2 pp** — y la contaminación va en dirección
  **optimista**. Todo lo que salga de acá hereda esa limitación. La ventana
  larga da potencia; sólo el sellado en vivo da validez.
- **No hay ninguna fila sellada de este riel.** El riel de medición tiene un
  track record prospectivo; el riel largo tiene cero. Nada de lo que se mida
  acá es evidencia del mismo tipo.

## 8. Procedimiento

- **Walk-forward con embargo.** Años de ajuste y prueba congelados antes de
  mirar: ajuste **2018-09-05 → 2023-09-04**, prueba **2023-09-05 →
  2026-09-04**. `EMBARGO_DIAS = 5` como en `backtest/`, ampliado al
  horizonte cuando el horizonte es mayor: las features solapan la ventana de
  la etiqueta y sin purgar el borde el resultado es fuga disfrazada.
- **`auditor-lookahead` corre ANTES de la primera medición**, no después.
- **Sólo instrumentos y datos que el proyecto ya ingiere**, desde
  `dinero/datos/cierres_congelados.csv`. Si hiciera falta una fuente nueva,
  se declara como necesidad y el bloque se detiene ahí en vez de improvisar
  una descarga.


---

## 9. ERRATA FECHADA — 7-sep-2026, tras la auditoría de fuga y ANTES de la primera medición

`auditor-lookahead` corrió sobre la implementación v1, como manda el §8, y
encontró **una fuga demostrada y tres sesgos con signo**. Las correcciones se
escriben acá, con fecha, **sin que se haya calculado un solo MAE, acierto ni
CRPS**: el orden está verificable en git —`dinero/senal_larga_reporte.py` no
se había ejecutado— y es lo que hace legítima esta enmienda. Ninguna corrección
ablanda una vara; dos de ellas la endurecen.

**E1 — La composición de los eslabones ya no se decide con el final de la
muestra.** La v1 componía cada eslabón con los instrumentos «comprables con
500 USD» según `construir_mapa`, que mira el ÚLTIMO cierre del archivo. Eso
fijaba la membresía de ocho años con el renglón del 2026-09-04, y el filtro
expulsa a los que subieron (excluidos: retorno total mediano 847 % contra
547 % de los incluidos). Medido: truncar el archivo en 2025-12-31 cambiaba el
**42,9 %** de las filas del panel, desde la primera. La membresía se decide
ahora por **cobertura ≥ 98 % del período de AJUSTE** —al principio de la
muestra, y sin mirar el nivel del precio—. Efecto sobre el §3: los eslabones
recuperan sus dominantes (Micron vuelve a `memoria`, ASML a litografía, MSFT y
META a demanda final) y salen ARM, GFS y SanDisk por no cubrir el ajuste, lo
que además elimina el quiebre de composición que ARM producía nueve días
después del inicio del período de prueba.

**E2 — «Walk-forward» del §8 se reemplaza por ajuste único.** La v1 hacía
walk-forward expansivo, que metía hasta el **36 %** del último ajuste dentro
del período de prueba, mientras el §8 declaraba ajuste y prueba congelados.
Las dos cosas no pueden ser ciertas a la vez y **gana el pre-registro**: un
ajuste sobre 2018-09-05 → (2023-09-05 menos horizonte, retardo y embargo), y
una sola evaluación sobre 2023-09-05 → 2026-09-04. Es además el protocolo más
exigente de los dos: hay un holdout de verdad, evaluado una sola vez.

**E3 — L2 estima la beta por eslabón.** La v1 usaba una beta pooleada sobre
los siete pares; los residuos seguían cargando la cesta (beta residual medida
entre −0,20 y +0,14 según eslabón), y con eso la regla del §6 —«si L1 gana y
L2 no, era beta común»— no se podía leer en ninguna de las dos direcciones.

**E4 — L3 excluye al eslabón objetivo de su propia dispersión.** La v1 lo
incluía, con correlación de hasta **+0,57** entre la dispersión y el retorno
del eslabón que L3 intenta predecir: un L3 positivo habría sido momento de la
propia serie disfrazado de «la cadena se tensa».

**E5 — Retardo de implementación de un día.** La etiqueta arrancaba en el
mismo cierre con el que se decide. Nadie ejecuta al cierre que acaba de
observar, y el auditor midió que un día de retardo mueve la etiqueta **3,6–4,0
pp de media** — del mismo orden que el umbral de señal del juego conservador
(3,49 pp). La etiqueta va ahora de t+1 a t+1+h. **Esto hace la vara más
difícil, no más fácil.**

**E6 — La dirección excluye los retornos exactamente cero.** `sign(0)==sign(0)`
contaba como acierto; el proyecto ya congeló la convención `excluir_cero` por
este mismo artefacto (`GEMELO/DISEÑO.md` §2.8).

**Lo que NO se corrigió, porque estos datos no lo permiten**, y va declarado en
el reporte: supervivencia (los 36 tickers son los que existen hoy; ninguna
deslistada, ninguna quebrada); que la fuente no es point-in-time; que `VRT`
fue un SPAC hasta feb-2020 y durante **358 sesiones (17,8 % de la muestra)** su
σ diaria fue 0,59 % contra 3,86 % después; y la fuga por el analista, que sólo
el sellado en vivo desmiente y este riel tiene **cero filas selladas**.

**Ninguna de estas correcciones suma al registro de intentos**: no son
especificaciones nuevas ni variantes probadas y descartadas. Son la misma L1,
L2 y L3 declaradas en el §3, computadas sin la fuga que las habría vuelto
ininterpretables. El registro sigue en 3.
