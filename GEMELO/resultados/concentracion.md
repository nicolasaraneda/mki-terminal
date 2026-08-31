# La concentración de julio — veredicto

> **Corrección tras revisión adversaria (31-ago-2026).** La primera
> versión de este documento fue revisada por `estadistico-adversario`
> (CONFIRMADO CON RESERVAS, cuatro defectos que obligaban a corregir antes
> de publicar) y por `auditor-lookahead` (sin fuga en las condiciones
> causales, pero con un defecto más grave: el criterio de decisión de
> A4-A5 se evaluó contra un umbral distinto del que el pre-registro había
> congelado, y esa desviación —no declarada— invierte el veredicto que se
> había publicado). Esta versión corrige lo que se pudo corregir con la
> evidencia disponible y **retracta explícitamente** la parte que no se
> pudo salvar sin rehacer el análisis desde cero con código versionado.
> El detalle de cada corrección, con las dos revisiones completas, vive en
> `GEMELO/resultados/bitacora_02.md`. Nada de esto tocó `senales.db` ni
> ninguna fila sellada.

Frente A de la segunda corrida autónoma (31-ago-2026). Responde si la
ventaja del track record sellado es real y constante, o si +6.5pp es un
artefacto de que toda la ventaja vive en 6 fechas de julio de 2026.

## A1. El hallazgo se reproduce — confirmado, no refutado

Verificado por tres caminos de cómputo independientes (la corrida
anterior, uno propio, uno de `integridad-datos`) y una CUARTA vez durante
la revisión adversaria (dos agentes distintos, cada uno con su propia
consulta). Los cuatro dan exactamente lo mismo:

| | n | b | c | Ventaja | McNemar p |
|---|---|---|---|---|---|
| Bloque 15-23-jul-2026 (6 fechas) | 44 | 24 | 6 | **+40.9 pp** | 0.001 |
| Resto de la ventana (28 fechas) | 204 | 48 | 50 | **-1.0 pp** | 0.920 |
| Ventana completa | 248 | 72 | 56 | +6.5 pp | 0.185 |

Dentro del rango calendario 15-23-jul hay un hueco: el 2026-07-20 es día
hábil, y el snapshot de esa fecha SÍ existe (`roca_chip`, `origen`,
`ventana_betas` con datos), pero `regimen` quedó `NULL` y las 24 filas de
`senales_ticker` de ese día no tienen `apertura_estimada_pct`/`estado`/
`exchange` — ninguna llegó a `verificacion_apertura`. **Corrección: la
versión anterior de este documento decía "todos los campos en NULL", lo
cual es falso** — el snapshot existe, lo que falta es la predicción
direccional a nivel ticker. El "bloque de 6 fechas" son 6 fechas de
EMISIÓN efectivas, no 6 sesiones de calendario consecutivas.

## A2. Caracterización — corregida en tres puntos, con evidencia más honesta

**Por bolsa, DENTRO del bloque** (la versión anterior citó, por error, la
ventaja de la ventana COMPLETA en vez de la del bloque — quedó corregido
en `GEMELO/CONDICIONAL/verificacion_A2.py`, reproducible):

| Bolsa | n | Wilson modelo | Wilson base | Ventaja dentro | McNemar p | Ventaja fuera |
|---|---|---|---|---|---|---|
| XETR (Fráncfort) | 5 | [11.8%, 76.9%] | [11.8%, 76.9%] | +0.0 pp | 1.000 | +10.7 pp |
| XKRX (Seúl) | 10 | [72.2%, 100%] | [16.8%, 68.7%] | +60.0 pp | 0.031 | −12.0 pp |
| XTAI (Taipéi) | 5 | [23.1%, 88.2%] | [3.6%, 62.4%] | +40.0 pp | 0.625 | +0.0 pp |
| XTKS (Tokio) | 24 | [69.0%, 95.7%] | [27.9%, 64.9%] | +41.7 pp | 0.021 | +1.0 pp |

**Con los intervalos puestos, la lectura tiene que ser más modesta que en
la primera corrección de este documento.** Los intervalos de XETR y XTAI
(n=5) son enormes ([11.8%,76.9%], [23.1%,88.2%]) — un +0.0pp o un +40.0pp
sobre 5 observaciones no distingue casi nada. Además son 8 comparaciones
de McNemar por bolsa (4 bolsas × dentro/fuera) sin corrección por
multiplicidad: los dos p que parecen significativos a simple vista
(XKRX 0.031, XTKS 0.021) **no sobreviven una corrección Bonferroni ×8**
(0.25 y 0.17 respectivamente). Lo que sí se sostiene, con esa cautela: no
es cierto que "las cuatro bolsas aportan en proporciones parecidas a su
peso en la ventana completa" (la versión anterior lo afirmaba comparando
mal, contra la ventana completa en vez de contra el bloque) — Fráncfort
da +0.0pp exacto dentro del bloque contra +10.7pp fuera, una diferencia
real aunque no cuantificable con confianza a n=5. **El bloque tiene
composición distinta por bolsa que el resto de la ventana; llamarlo
"fenómeno asiático establecido" sería más de lo que n=5-24 y ocho
comparaciones sin corregir permiten afirmar.**

**El test formal, rehecho.** La versión anterior corrió un scan-statistic
con anchos 3 a 10 y reportó p=0.648 como si fuera el resultado que
importa. **Es un test roto**: el estadístico (diferencia de proporciones
sin estandarizar por n) hace que el máximo bajo la nula caiga casi
siempre en la ventana más angosta posible (82% de las nulas tienen su
máximo en ancho 3, con n≤30 en el 95% de los casos) — comparar el +61.5pp
observado (ancho 4) contra máximos dominados por ventanas de 3 fechas no
mide nada útil. **Se descarta esa versión.** La versión de ancho FIJO 6
(todas las ventanas comparadas tienen n≈43-46, una comparación real)
sigue siendo válida y da, reproducido de forma independiente hoy:

- **p con corrección por búsqueda (cualquier posición de 6 fechas entre
  las 34): 0.52.**
- **p SIN buscar — la posición exacta donde cayó el bloque, fijada de
  antemano: 0.04.**
- **p eligiendo 6 fechas al azar, sin exigir que sean contiguas: 0.04.**

**La lectura correcta, y es más sutil que "es azar":** la nula de este
test PERMUTA EL ORDEN de las 34 fechas, así que la ventaja total
(+6.45pp) queda fija en cada réplica — este test mide **dónde en el
tiempo se concentra la ventaja**, no si la ventaja total es cero (eso ya
lo mide el McNemar de la ventana completa, p=0.185). Y el hallazgo más
limpio de esta sección: **la contigüidad del bloque no aporta nada** — el
p de "estas 6 fechas exactas" (0.04) es prácticamente idéntico al p de
"6 fechas cualesquiera al azar, sin pedir que sean consecutivas" (0.04).
Julio no es una "racha" en el sentido de que el mercado haya entrado en
un régimen sostenido varios días seguidos — es que 6 fechas
calendario-adyacentes contienen, por la razón que sea, varias de las
fechas de mejor desempeño de toda la ventana. Solo se vuelve "sorprendente
otra vez" (p≈0.04) si uno se hubiera comprometido, ANTES de mirar los
datos, a examinar exactamente esas 6 fechas y ninguna otra — que no es lo
que ocurrió: el bloque se identificó DESPUÉS de ver que ahí había un pico
(`GEMELO/DISEÑO.md` §2.2, bloques de 40 filas, ya lo señalaba desde el
25-ago). El p=0.52 con corrección por búsqueda es el que corresponde a
cómo se llegó a esta pregunta.

**Lo que el intervalo de confianza dice, con el método correcto esta
vez.** `guardian-constitucion` encontró que el primer intento de corregir
esta cifra la remuestreaba de forma iid, fecha por fecha — exactamente la
clase de defecto que toda esta corrección viene retractando, solo que
reintroducido en el propio script de corrección. Recalculado con
`backtest.inferencia._remuestrear_circular` (la maquinaria que el propio
pre-registro exige, `GEMELO/CONDICIONAL/verificacion_A2.py`): la
diferencia bloque−resto es **+41.9pp, IC95 [−2.9pp, +86.0pp]**, 3.4% de
las réplicas ≤0. **Declarado explícitamente:** con solo 6 fechas en el
grupo del bloque, un tamaño de bloque circular mayor a 1 deja muy pocas
posiciones de inicio distintas para remuestrear, y con bloque=6 (=el
tamaño del grupo) el bootstrap degenera por completo (varianza cero, se
midió). Bloque=1 —equivalente a remuestreo del elemento individual, pero
vía la función correcta— es la única opción no degenerada para un grupo
tan chico, y es la que se reporta. **Esto sigue estando al filo de la
significancia, no es "indistinguible de cero"** — la versión anterior de
este documento sobrevendió la fuerza de la evidencia hacia el lado del
azar tanto como el README original la había vendido hacia el lado de la
ventaja constante. Los dos errores son la misma clase de error, en
direcciones opuestas.

**Sobre el dato del percentil 90 en la ventana larga que una versión
anterior de esta sección presentaba como "limpio y no explotado":**
se retira del veredicto. Sale de la reconstrucción de ocho años que la
propia §A5 declara sin reconciliar (conteos de fechas/filas
inconsistentes entre los pasos del análisis) y que nunca se guardó como
código versionado — no hay forma de reproducirlo hoy con nada que viva en
el repo, así que no puede sostener una afirmación del veredicto. Queda
como una observación hecha durante la revisión, sin el respaldo que un
número citado en un veredicto necesita.

**Es concentración de aciertos, no de magnitud** — se mide `acierto_gap`
(binario) en toda esta sección. **Corrección:** una versión anterior
decía "esto es lo correcto", lo cual entra en tensión con
`GEMELO/DISEÑO.md` §3, decisión 1, que declara que la métrica primaria
del proyecto DEJA DE SER el acierto de dirección. Ambas cosas son
ciertas a la vez sin contradecirse: el proyecto decidió que la magnitud
importa más para su métrica primaria (§3); este documento analiza
específicamente la concentración de la ventaja DIRECCIONAL publicada
(+6.5pp, que sigue siendo acierto de dirección, no magnitud) porque es
la cifra que hoy vive en el README y en los badges. No se está afirmando
que medir dirección sea "lo correcto" en general — es la cifra bajo
auditoría.

## A3. La ironía — ya estaba dicha, y sobrevive en las tres convenciones (con una corrección)

`GEMELO/DISEÑO.md` §6.2 (R2) ya registró, el 26-ago, que aplicar la misma
prueba al campeón lo descalifica — cita textual sin cambios:

> "Hallazgo del 26-ago, y no ablanda la regla: aplicada al campeón, esa
> misma prueba lo descalifica. Sin la ventana 15–23 jul queda en n = 184 ·
> modelo 62.0% · base 65.2% · ventaja −3.3 pp (p = 0.60): no pierde su
> ventaja, la vuelve negativa. [...] R2 se mantiene tal cual,
> deliberadamente."

**Corrección respecto a la versión anterior de este documento:** esa
cifra del 26-ago (n=184, −3.3pp) está bajo la convención `estricta`, no
`excluir_cero`. Comparando bien, convención por convención, 26-ago vs.
31-ago:

| Convención | 26-ago (excluyendo el bloque) | 31-ago (excluyendo el bloque) |
|---|---|---|
| `estricta` | −3.3 pp (n=184) | **+0.5 pp (n=209), p=1.000** |
| `excluir_cero` | −5.0 pp (n=179) | −1.0 pp (n=204) |
| `verificador` | −6.0 pp (n=184) | −1.9 pp (n=209) |

**"Mismo signo" —lo que decía la versión anterior— es falso bajo
`estricta`: ahí el signo cambió.** Lo que SÍ sobrevive en las tres
convenciones, sin excepción: la cifra sigue sin ser distinguible de cero
(ningún p se acerca a 0.05). Esa es la afirmación defendible, no una
"tendencia" de −3.3 a −1.0 que solo existe si se mezclan dos convenciones
distintas como si fueran la misma medición.

**Qué significa que un proyecto tenga un criterio de rechazo que su
propio campeón no pasaría, en las tres convenciones:** que el campeón,
con la vara que el propio proyecto fijó para un retador, no calificaría
hoy como una señal repetible. El proyecto ya lo sabía desde el 26-ago y
ya decidió no bajar la vara. Este documento lo actualiza, no lo
descubre.

## A4-A5. La hipótesis condicional — RETRACTADA, no confirmada ni refutada

**La versión anterior de este documento afirmó que el modelo conjunto
"habría predicho que julio fuera un bloque bajo", fallando el criterio
de victoria del pre-registro. Esa afirmación se retracta.**

`auditor-lookahead` encontró que el pre-registro (`GEMELO/CONDICIONAL/DISEÑO.md`
§4) congeló el umbral de corte "alto/bajo" como **la mediana de la
ventaja a través de TODAS las 2.076 fechas de la ventana larga**. El
análisis que se corrió usó, en cambio, la mediana calculada solo sobre
las fechas de entrenamiento agregadas en bloques de 6 (12.9) — una
desviación del criterio congelado que **nunca se declaró**, y que decide
el resultado: bajo el umbral efectivamente congelado (la mediana por
FECHA sobre toda la serie, que es exactamente 0.0 porque el 53.4% de las
fechas tiene ventaja cero), el score de julio (3.33) se clasifica como
**ALTO**, no bajo — el criterio de victoria (b) del pre-registro, leído
como se congeló, **no falla**. Bajo el umbral que efectivamente se usó,
falla. La conclusión del frente depende enteramente de cuál de los dos se
use, y la corrida no declaró que estaba usando el segundo en vez del
primero.

**A esto se suman defectos adicionales que impiden sostener CUALQUIERA de
las dos lecturas con la confianza que un pre-registro exige:**

- El "bloque de julio" evaluado (rango calendario exacto 15-23-jul, 7
  fechas con huecos) no es una unidad de la grilla de bloques no
  solapados de 6 fechas que el propio walk-forward usó para todo lo
  demás — comparar un punto fuera de grilla contra un umbral calculado
  sobre la grilla no es una comparación válida. Sobre la grilla real, el
  bloque adyacente (23-30-jul) SÍ se predice y resulta alto; el bloque
  que contiene la mayor parte de 15-22-jul da un score bajo. El modelo no
  falla de forma pareja ni siquiera dentro de julio.
- El score de julio (3.33) se reportó sin intervalo. La dispersión de los
  residuos en el conjunto de prueba implica un margen de alrededor de
  ±20pp sobre un bloque individual — un intervalo así de ancho CONTIENE
  el umbral de 12.9, así que "predice bajo" tampoco se sostiene con la
  confianza que se le dio.
- El §9 del pre-registro exigía correr, ANTES del walk-forward, una
  prueba de invariancia a truncar en `t` para cada condición candidata.
  No se corrió en esta corrida (la corrió `auditor-lookahead`, por su
  cuenta, en la revisión, y las 5 condiciones la pasaron — pero la
  compuerta que el propio pre-registro exigía se saltó, así que el
  resultado del walk-forward no cumple su propio protocolo de aceptación
  y queda **no evaluable**, no "confirmado limpio").
- El embargo usado (3 bloques de 6 fechas, hecho a mano) no es el
  `EMBARGO_DIAS=5`/`ContextoRun` de `backtest/baselines.py` que el
  pre-registro exigía reutilizar explícitamente ("no se reimplementa
  purge ni embargo a mano"). Es más conservador en la práctica (holgura
  medida de 14 días calendario contra la ventana rodante más larga
  usada), pero es una desviación de la maquinaria pre-registrada, sin
  declarar.
- El conteo de fechas/filas de la ventana larga usado en esta corrida
  (~14.600-14.700 filas, ~2.031-2.032 fechas, con tres cifras ligeramente
  distintas entre los propios pasos intermedios del análisis) no
  reconcilia con la cifra canónica del README (n=14.618) ni con la del
  propio pre-registro (2.076 fechas). No se investigó la causa exacta —
  queda declarado como una inconsistencia sin resolver, no como un hecho
  menor.
- El análisis nunca se guardó como código versionado — vivió en comandos
  sueltos que se perdieron al cerrar la sesión que los corrió. Se
  reconstruyó lo auditable a partir de archivos intermedios que
  sobrevivieron por casualidad en una carpeta efímera. **Esto no se puede
  reparar retroactivamente**; solo se puede declarar y no repetir (el
  script de la §A2, arriba, sí quedó guardado en
  `GEMELO/CONDICIONAL/verificacion_A2.py`, precisamente por esta razón).

**Lo único que sobrevive de A4-A5, verificado independientemente por
`auditor-lookahead` reconstruyendo las series desde cero:** las cinco
condiciones candidatas medibles (volatilidad del SOX, magnitud de la
sesión de NY, dispersión asiática, distancia al cierre trimestral,
magnitud predicha del modelo) son causales y estacionarias por
construcción — no usan información posterior a la fecha de emisión, con
una prueba de invariancia a truncar que las cinco pasan (198
comparaciones, 0 fallos, con una contraprueba que confirma que el test
detecta fuga si se inyecta deliberadamente). También sobrevive, corregido:
la condición de dispersión asiática (`c3`) SÍ discrimina con IC que
excluye 0.5 (AUC≈0.67) cuando se orienta en el sentido correcto — la
versión anterior la reportó invertida (0.33) y la descartó sin intervalo,
ocultando que era, de las cinco, una de las que mejor discriminaba.

**Veredicto de A4-A5: NO EVALUABLE con el rigor que un pre-registro
exige.** Ni "la condición explica julio" ni "la condición no explica
julio" quedan establecidos — el análisis que debía decidirlo se desvió de
su propio protocolo sin declararlo, y esa desviación es la que determina
cuál de las dos lecturas parecería cierta. Rehacerlo correctamente (con
el umbral congelado, la grilla de bloques real, el embargo/splitter
pre-registrado, la compuerta de causalidad corrida ANTES, y el código
guardado en el repo) queda como trabajo pendiente, no incluido en el
alcance de esta corrida.

## A6. El veredicto, revisado

Con lo que sobrevive la auditoría (A1-A3) y sin lo que no sobrevive
(A4-A5, retractado):

1. El campeón no pasa su propio criterio R2 en ninguna de las tres
   convenciones de medición — esto es sólido, confirmado, y ya lo sabía
   el proyecto desde el 26-ago.
2. La ventana completa sigue sin ser distinguible de cero (McNemar
   p=0.185) — la evidencia más robusta y menos discutible de todo el
   documento.
3. La diferencia bloque−resto (+41.9pp) está **al filo de la
   significancia** (IC95 [−2.9, +86.0] por bootstrap circular correcto,
   3.4% de las réplicas ≤0) — ni claramente ruido, ni claramente señal.
4. El dato del "percentil 90 en la ventana larga" que una versión previa
   de este veredicto incluía **se retira**: sale de un análisis no
   reconciliado y no versionado (A5), y no puede sostener una afirmación
   del veredicto sin poder reproducirse.
5. El bloque de julio tiene, dentro de sí, una composición por bolsa
   distinta del resto de la ventana (Fráncfort en +0.0pp contra +10.7pp
   fuera del bloque) — pero con n=5-24 por bolsa y 8 comparaciones sin
   corregir por multiplicidad, esto no alcanza para afirmar "es un
   fenómeno asiático establecido"; alcanza para decir que la composición
   difiere, sin poder cuantificar cuánto con confianza.
6. La pregunta de si hay una condición identificable detrás de la
   concentración **queda abierta, no cerrada en ninguna dirección** — el
   intento de cerrarla en esta corrida no cumplió su propio protocolo y
   se retracta.

**Esto no es tan limpio como "es puro azar" (lo que decía la versión
anterior), ni tan limpio como "el modelo tiene una ventaja pequeña pero
real" (lo que dice hoy el README). Es más incómodo que cualquiera de las
dos: la evidencia disponible hoy, medida con el rigor que corresponde, no
alcanza para decidir entre esas dos lecturas — y afirmar cualquiera de
ellas con la firmeza que ya se le dio en algún momento de este proceso
(incluida la primera versión de este propio documento) es exactamente el
error que este proyecto existe para no cometer.**

## N_intentos del DSR — declarado, con el desacople frente al código señalado

La versión anterior instruía "leer `GEMELO/relevo_asiatico.py` en
cualquier evaluación futura, nunca esta cifra congelada acá" — pero
`GEMELO/relevo_asiatico.py:76` sigue en `N_INTENTOS_WS5 = 25`, sin
actualizar. Esa instrucción, tal como estaba escrita, llevaba a subcontar
por al menos 7 (los intentos de esta corrida) más los 3 scan-statistics
de la §A2 (cada uno es una configuración × ventana con resultado
reportable, y no se habían contado). `guardian-constitucion` señaló
además que los 8 McNemar por bolsa (4 bolsas × dentro/fuera del bloque,
también §A2) son igualmente configuración × ventana con resultado
reportable — dos de ellos citados como significativos para sostener una
conclusión del documento, así que cuentan sin excepción. **Declarado
explícitamente, en vez de delegado a un código que no se actualizó:** el
acumulado real después de esta corrida es de al menos
**25 + 7 + 3 + 8 = 43** intentos. Actualizar
la constante en `GEMELO/relevo_asiatico.py` de forma coordinada con su
test (`test_el_N_del_WS5_es_25_y_su_desglose_cuadra`) queda fuera del
alcance de esta corrida — es un cambio a código de producción-adyacente
que merece su propia revisión, no un ajuste de paso dentro de este
documento.

## Qué NO se hizo

No se tocó `motor.py`, `senales.py`, `snapshot.py`, `universo.py`. No se
reescribió ninguna fila sellada. No se decidió ningún cambio de reporte
ni de criterio (eso sigue siendo el Frente C, sin aplicar). No se
actualizó `GEMELO/relevo_asiatico.py`.

## Trazabilidad

A1-A3 recalculados en modo lectura contra `senales.db`, script versionado
en `GEMELO/CONDICIONAL/verificacion_A2.py` (reproducible: `python
GEMELO/CONDICIONAL/verificacion_A2.py`). A4-A5 retractado; los .pkl
intermedios que permitieron auditar el análisis original sobreviven, por
ahora, en el directorio efímero de scratchpad de la sesión — no están en
el repo y se perderán. El detalle completo de ambas revisiones
adversarias (estadístico y de fuga temporal), con todas las cifras
citadas en este documento, vive en `GEMELO/resultados/bitacora_02.md`.
