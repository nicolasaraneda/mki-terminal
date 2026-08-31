# RELEVO: protocolo del relevo de `MODELO_VERSION`

**Estado:** PRE-REGISTRO. Congelado antes de evaluar ningún relevo real, y
antes de saber si GEMELO 6.0.0 o cualquier otro retador lo cumple.
**Corrección posterior:** cualquier ajuste a este documento se agrega como
sección nueva, con fecha, al final (nunca se reescribe una sección ya
escrita). Si algo de lo fijado aquí resulta mal formulado, como pasó con el
invariante 4 del switch de sombra (DECISIONES.md §37), el patrón es el
mismo: se para, se documenta el defecto, y la corrección la firma quien
decide, no quien la encuentra.
**Fecha:** 31-ago-2026. **Campeón vigente:** modelo 4.6.0.
**Insumos:** `GEMELO/DISEÑO.md` (pre-registro del retador, criterios V1 a
V7 y R1 a R3 congelados el 25-ago), `backtest/DISEÑO.md` §11 (gatillo de la
Etapa 5.1), `backtest/inferencia.py` (WS1: PSR, DSR, bootstrap circular),
track record sellado al 30-ago (n=248, convención `excluir_cero`,
DECISIONES.md §37.5), ventana larga reconstruida (n=14.618, DECISIONES.md
§35.6).

> **Regla cero de este documento:** ningún número de aquí se movió después
> de mirar si GEMELO lo cumple. Si el resultado de un relevo futuro
> contradice una cifra de esta acta, la cifra gana y la corrección se
> documenta con fecha posterior, como cualquier otra errata del proyecto.

---

## 1. Por qué este documento existe ahora, y qué terreno es nuevo

**Hoy no existe ningún documento que especifique el mecanismo de transición
si un retador le ganara al campeón.** No es un descuido: la Constitución
5.0 de `CLAUDE.md` fija que las filas selladas nunca se reescriben y que el
versionado es dual en todas partes, y `GEMELO/DISEÑO.md` §6.3 escribió qué
pasa si nadie gana ("se publica el negativo"). Pero el caso positivo, qué
pasa si alguien sí gana, no tiene precedente escrito en este proyecto. Este
documento lo escribe antes de que haga falta, por la misma razón que
`GEMELO/DISEÑO.md` se escribió antes de construir el retador: un protocolo
de relevo redactado después de ver un resultado favorable no es un
protocolo, es una racionalización con formato de protocolo.

Se apoya en tres piezas ya construidas y no las reinventa:

1. El filtro `legacy = 0 AND modelo_version = ?` que `senales.py` aplica en
   cada consulta de métricas (líneas 441 y 493): la garantía de que dos
   `modelo_version` nunca se mezclan en un solo cálculo. El relevo la
   hereda, no la toca.
2. La maquinaria de juicio de WS1 (`backtest/inferencia.py`): PSR, DSR con
   `N_intentos` obligatorio, bootstrap circular de bloques. Cualquier
   margen que este documento fije se apoya en esas funciones, nunca en una
   cifra suelta calculada aparte.
3. La disciplina de conteo de intentos de `GEMELO/DISEÑO.md` §4.2 bis: cada
   configuración evaluada cuenta, se declara antes de correr, y no se
   cuenta a conveniencia. El relevo hereda esta disciplina explícitamente
   en la §3.

---

## 2. Cuándo se evalúa siquiera el relevo: el n mínimo

El relevo no se evalúa antes de que se cumplan ambas condiciones:

**2.1 El gatillo de la Etapa 5.1 ya tiene que estar cumplido.**
`backtest/DISEÑO.md` §11 fija: N≥150 verificaciones limpias en vivo y al
menos un cambio de régimen del SOX observado, o 3 meses de operación
continua (25-jul a 25-oct-2026), lo primero que ocurra. Evaluar un relevo
antes de eso adelantaría por la puerta de atrás un veredicto que el propio
proyecto ya declaró que requiere ese gatillo. Al 30-ago el track record
lleva 253 verificaciones limpias, así que el tramo de "150" ya se cruzó
(248 es el n bajo la convención de medición `excluir_cero`, que excluye 5
filas con `gap_pct == 0.00` — es una convención de cómputo de la ventaja,
no el conteo de verificabilidad que usa este gatillo; DECISIONES.md §37.5),
pero el cambio de régimen no ha ocurrido (una sola
etiqueta de régimen en todos los snapshots sellados, `CLAUDE.md`, Etapa
5.0, "Sealed extras"). El gatillo cuelga hoy de los 3 meses o de que el
régimen finalmente se mueva.

**2.2 El retador necesita su propio out-of-sample intacto, con un n mínimo
propio.** No basta con que el proyecto cumpla su gatillo general: el
retador tiene que acumular, después de que su desarrollo se congeló, filas
selladas de producción que nunca vio como insumo. Propongo:

> **n ≥ 150 filas selladas out-of-sample intactas, Y ≥ 60 días de emisión
> distintos entre esas filas** (mismo n de filas que el gatillo de la 5.1,
> por consistencia; el mínimo de días es nuevo y necesario — ver por qué
> abajo).

**Por qué el mínimo de días, y no solo de filas:** las filas no son
independientes entre sí dentro de una misma fecha de emisión. Medido sobre
las 248 filas selladas del campeón hoy: 34 fechas distintas, 7.3 tickers
por fecha en promedio, y el signo de la predicción del campeón es unánime
dentro de una fecha el 100% de las veces (34 de 34) — porque el modelo
apuesta el signo del retorno del SOX de esa noche para todos los tickers a
la vez. Un bootstrap por cluster de fecha mide un efecto de diseño
(DEFF) de entre 2.5 y 3.6 sobre esa correlación intra-fecha: **150 filas
pueden ser tan pocas como ~40-60 decisiones efectivamente independientes**,
no 150. Pedir además un mínimo de días distintos es la forma barata de
evitar evaluar un relevo sobre lo que en la práctica son tres semanas de
mercado repetidas siete veces cada una.

Ambos números son una propuesta razonada, no una cifra impuesta: la palabra
final es de Nicolás. Si decide que 150 filas / 60 días es poco para una
decisión que reemplaza al campeón (una afirmación más fuerte que "el
backtest merece correrse con veredicto"), subirlo es legítimo, con la misma
condición de que se fije aquí, antes de mirar cuántas lleva GEMELO hoy.

**2.3 Ninguna de las dos condiciones se relaja porque el retador "ya casi
llega".** Evaluar con n=140 porque falta poco es exactamente el tipo de
ajuste que un pre-registro existe para impedir.

---

## 3. El margen de victoria: congelado, más estricto que ruido contra ruido

**El punto de partida que este criterio tiene que respetar:** el campeón,
hoy, no le gana a una constante con significancia. Sobre la ventana sellada
bajo la convención congelada `excluir_cero`: n=248, modelo 66.1%, "siempre
al alza" 59.7%, ventaja +6.5 pp, McNemar p=0.1849 (DECISIONES.md §37.5). Un
retador que solo empatara esa ventaja, o la superara por un margen que
tampoco fuera significativo, no estaría demostrando nada: estaría
reemplazando ruido por ruido con más pasos en el medio. Por eso el criterio
de relevo no puede ser "ganarle al campeón" a secas: tiene que ser más
exigente que la vara que el propio campeón no salta hoy.

### 3.1 Barreras de entrada del relevo (REL-V1 a REL-V4)

Todas obligatorias, evaluadas en la misma ventana out-of-sample sellada
(§4), con la maquinaria de `backtest/inferencia.py`. **REL-V1 a REL-V5 son
ADICIONALES a V1–V7 y R1–R3 de `GEMELO/DISEÑO.md` §6, que siguen vigentes
sin excepción para cualquier retador, incluidos V3 (cobertura del 80% en
[76%, 84%] — el campeón hoy está en 90.3%, ratio de ancho 1.84×), V6
(superar comprar-y-mantener SMH neto de 25 pb) y V7 (holdout confirmado en
cuarentena, evaluado una sola vez). Ningún criterio de `DISEÑO.md` §6 se
relaja por llegar a la etapa de relevo — este documento agrega barreras,
no las reemplaza.**

- **REL-V1: retador vs. campeón, no solo retador vs. baseline.** McNemar
  entre las predicciones del retador y las del campeón (no las del retador
  contra "siempre al alza") sobre las filas donde ambos emitieron,
  **p < 0.05**. Ganarle a una baseline débil sin ganarle al campeón
  directamente no cuenta (ver §8). Esta es la comparación que decide.
- **REL-V2: el retador tiene que pasar su propio V1.** Además de ganarle al
  campeón, el retador tiene que ganarle a "siempre al alza" en la misma
  ventana con McNemar p < 0.05: el mismo criterio V1 que
  `GEMELO/DISEÑO.md` §6.1 ya exige, ahora aplicado a filas de producción
  sin excepción. Un retador que le gana al campeón solo porque el campeón
  empeoró, sin ganarle él mismo a la constante, no es un reemplazo: es un
  campeón nuevo con el mismo problema.
- **REL-V3: DSR ≥ 0.95, con `N_intentos` heredado, no reiniciado en cero.**
  `N_intentos` acumulado vigente al escribir esto: **25**
  (`GEMELO/relevo_asiatico.py`, constante `N_INTENTOS_WS5`, con test que
  verifica el desglose: 6 baselines B0–B5 + 3 configs del WS2b + 3 del WS3
  + 1 campeón reconstruido + 12 del WS5). El relevo suma uno por cada
  configuración evaluada específicamente para él, a partir de ese 25 — este
  documento no repite el número aquí más allá de decir "el acumulado real",
  precisamente porque el número vigente cambia con cada corrida nueva y una
  cifra fija en esta acta envejecería mal y terminaría subestimando el
  conteo (un `N_intentos` desactualizado hace que el DSR mienta hacia
  arriba). El acumulado se lee del código en el momento de evaluar, nunca
  de una cifra congelada en este documento.
- **REL-V4: el margen mínimo, CON intervalo — el punto solo no alcanza.**
  Además de la significancia de REL-V1, la ventaja retador menos campeón en
  la ventana out-of-sample tiene que (a) ser **≥ 5 puntos porcentuales** de
  punto, Y (b) tener un **IC95 por bootstrap circular de bloques de 20
  días, semilla declarada, que excluya el cero** (misma maquinaria de
  `backtest/inferencia.py` que el resto de este documento). La condición
  (b) es la que manda: sobre las 248 filas selladas hoy, la ventaja del
  campeón sobre su propia baseline es +6.45 pp con IC95 de bootstrap de
  bloques **[−5.24, +22.58] pp — 28 puntos de ancho**. Un umbral de punto
  sobre una cantidad con esa dispersión no discrimina nada por sí solo; un
  p < 0.05 con una ventaja de 0.3 pp de punto sería igual de inútil que un
  intervalo de 28 pp de ancho que además excluye el cero por casualidad.
  Para la métrica CRPS (si el retador cambia de métrica primaria, como
  propone `GEMELO/DISEÑO.md` §3.1): mejora con IC de bootstrap de bloques
  que excluya el cero — el margen de punto exacto en escala CRPS queda SIN
  FIJAR en este documento, y por lo tanto REL-V4 no es alcanzable por la
  vía CRPS hasta que alguien lo fije con cifra explícita, antes de evaluar
  ningún retador que use esa métrica.

  *(Propuesta razonada, ancla corregida: bajo la convención canónica
  vigente `excluir_cero`, la abstención por magnitud de
  `GEMELO/DISEÑO.md` §2.4 sube la ventaja de +6.5 a +10.7 pp a umbral 0.25
  — un salto de 4.2 pp, no de 3 como decía una versión anterior de este
  párrafo que citaba la convención `estricta` ya superada por el §2.8 del
  propio DISEÑO.md. El 5 pp de arriba redondea ese 4.2 hacia arriba; sigue
  siendo propuesta, no medición, y la palabra final es de Nicolás.)*
- **REL-V5: la ventaja sobrevive el recorte de sub-período — hereda R2.**
  Se reevalúan REL-V1 y REL-V4 excluyendo el bloque de fechas de mayor
  contribución a la ventaja del retador (identificado por fecha, con el
  mismo método que `GEMELO/DISEÑO.md` §2.8.2 usa para el campeón, nunca por
  índice de fila). Si la ventaja desaparece o se invierte al excluir ese
  bloque, no hay relevo. **Precedente medido, sobre el campeón mismo:**
  excluyendo el bloque 15 al 23-jul-2026 de la propia ventana sellada, el
  campeón queda en n=204, ventaja **−1.0 pp, McNemar p=0.92** — toda su
  ventaja hoy vive en esas seis fechas. Un candidato a relevo evaluado sin
  este chequeo podría estar ganando por la misma clase de concentración
  temporal que el propio campeón tiene, y no se sabría hasta después.

### 3.2 El n mínimo de esta evaluación específica

Se aplica el n ya fijado en la §2.2. Si Nicolás decide un n distinto para
el gatillo general de la Etapa 5.1, este documento no lo hereda
automáticamente: se declara aparte, porque el relevo es una decisión más
fuerte que "correr el backtest con veredicto".

---

## 4. Qué out-of-sample está intacto hoy, y cómo se audita

**El conjunto que califica:** las filas selladas de producción (modelo
4.6.0) desde que arrancó el track record limpio, filtradas por la master
rule (`timestamp_utc` anterior a la apertura UTC de la sesión objetivo,
`legacy_pre_4.6` y `no_verificable_timing` fuera, como siempre). Califican
como out-of-sample del retador por una razón estructural, no por promesa:

- **GEMELO no puede tocar el camino de sellado, y el camino de sellado no
  importa GEMELO.** Verificado por AST:
  `tests/test_gemelo_datos.py::test_gemelo_no_importa_el_camino_de_sellado`
  (ningún archivo de `GEMELO/` importa `snapshot`, `senales`, `alertas`,
  `noticias`, `app` ni los jobs), `::test_los_modulos_estrictos_no_importan_nada_de_produccion`
  (los módulos ESTRICTOS — `datos.py`, `features.py`, `control_lineal.py` —
  no importan ni `motor` ni `universo`) y
  `tests/test_control_lineal.py::test_el_camino_de_sellado_no_importa_GEMELO`
  (la dirección que protege el sello).
- **Lo que estos tests NO prueban, y hay que decirlo con la misma claridad:**
  GEMELO SÍ tiene un camino de lectura hacia las filas selladas —
  `GEMELO/experimento.py` y `GEMELO/ventana_larga.py` importan
  `backtest.linea_base`, que abre `senales.db` en `mode=ro`, y el propio
  test de aislamiento lo EXIGE (`assert "backtest" in imp` — la lectura
  tiene que ir por la capa auditada, no que no exista). Y
  `GEMELO/ventana_larga.py` importa `motor` para reconstruir al campeón vía
  `B2Produccion`; `motor` no está en la lista de módulos prohibidos porque
  esa lista protege la dirección de escritura, no de lectura. **Por lo
  tanto el out-of-sample de este documento NO está garantizado
  estructuralmente por sí solo: la garantía real es de solo-lectura y de
  dirección de dependencia (nada de GEMELO puede escribir en el camino de
  sellado, ni el camino de sellado puede importar GEMELO), no de
  inaccesibilidad de las filas.** El chequeo de fecha de congelamiento del
  punto 2, más abajo, deja de ser un refuerzo opcional y pasa a ser la
  única prueba real de que el desarrollo del retador no usó filas
  posteriores a su propio corte — y hay que construirlo antes de evaluar
  ningún relevo, no después.

**Cómo lo comprueba un auditor en cualquier momento futuro (propuesta, nada
de esto está implementado hoy):**

1. **Correr los tres tests AST de aislamiento** (`pytest tests/ -k
   "gemelo or control_lineal or relevo_asiatico or ventana_larga"`, o el
   nombre que tengan al momento) y confirmar que siguen en verde. Si algún
   commit posterior agregó un import hacia la ruta de sellado, el
   aislamiento se rompió y el out-of-sample deja de ser válido desde ese
   commit.
2. **Un chequeo de fecha de congelamiento, propuesto y no construido:**
   registrar, al momento de congelar el desarrollo del candidato a relevo
   (el equivalente a un corte de commit), la fecha exacta de ese corte,
   igual que `CORTE_SECCION_2` ancla la §2 de `GEMELO/DISEÑO.md`
   (DECISIONES.md §36.6). Un script auditor compararía esa fecha contra el
   `timestamp_utc` de cada fila que el candidato usó en cualquier etapa de
   su desarrollo (entrenamiento, selección de hiperparámetros, elección de
   la configuración ganadora) y fallaría si alguna es posterior al corte:
   esa sería la señal de que el desarrollo "espió" hacia adelante en el
   propio out-of-sample que se usa para juzgarlo.
3. Ambos chequeos son necesarios, y ninguno por sí solo alcanza: el
   aislamiento estructural (1) prueba la dirección de dependencia (nada
   escribe hacia el sello, el sello no importa GEMELO) pero NO prueba que
   el retador no leyó filas selladas — de hecho el propio camino de lectura
   vía `backtest.linea_base` existe y está exigido por los tests. El
   chequeo de fecha (2) es el que tendría que probar que, aun teniendo ese
   camino de lectura disponible, el desarrollo no lo usó con filas
   posteriores a su propio corte. Hoy (2) no está construido, así que hoy
   no hay ninguna defensa mecánica contra el uso informal de filas
   posteriores al corte — ver riesgo 3 de la §10.

**Por qué la ventana larga reconstruida NO califica como este out-of-sample,
aunque sea estadísticamente significativa.** La ventana larga (ocho años
reconstruidos, n=14.618, +15.66 pp, DECISIONES.md §35.6) es reconstrucción
histórica: cada fila se calculó con datos que ya existían al momento de
calcularla, no fue emitida con un timestamp anterior al evento que predice.
La master rule de `CLAUDE.md` es explícita: una predicción solo es
verificable si se emitió antes del evento que intenta predecir, demostrable
por timestamp. La ventana larga no tiene eso. Sirve para el diseño del
retador y para acotar su forma funcional; no sirve como el out-of-sample
que decide un relevo.

---

## 5. Cómo se narra el cambio con el versionado dual: mapa, no PR

Si algún día se cumplen las barreras de la §3, la narración del cambio pasa
por piezas que ya existen y que este documento no modifica ahora:

| Pieza | Dónde vive | Qué cambia |
|---|---|---|
| El número de versión del modelo | `version.py`, constante `MODELO_VERSION` | Bump manual de `"4.6.0"` a la nueva versión: sigue siendo, como dice el comentario del propio archivo, "una decisión aparte (Etapa 5.1+)" |
| `PLATAFORMA_VERSION` | `version.py` | No sube por el relevo. Es un conteo independiente de infraestructura; el relevo es un cambio de modelo, no de plataforma. Si el relevo exige cambios de plataforma para sostenerlo (nuevas columnas, nuevo job), esos bumps se declaran aparte, con su propia justificación |
| El texto del reporte de Telegram | `alertas.py`, `componer_reporte_sellado()` | Tendría que declarar el corte de forma explícita, algo como: "modelo X.Y.Z activo desde DD-mmm-AAAA; serie 4.6.0 preservada como histórica, no mezclada en ninguna métrica", el mismo principio que ya aplica el reporte 2.0 (todo sale del sello, nada se rellena) |
| La vista `/historial` | `api/main.py` (`@app.get("/api/historial")`) y `frontend/src/vistas/Historial.tsx` | Tendría que mostrar ambas series rotuladas por `modelo_version`, nunca una sola línea de tiempo continua que las mezcle |
| La vista `/laboratorio` | `frontend/src/vistas/Laboratorio.tsx` | Es donde hoy vive el progreso hacia el gatillo de la 5.1; tendría que ganar una sección de progreso hacia el n mínimo de la §2.2 para el candidato a relevo, con el mismo criterio de no rellenar antes de tiempo |

Ninguno de estos archivos se toca al escribir este documento. Es un mapa de
dónde vivirá la narración si el día llega, no una implementación.

---

## 6. Las dos series, nunca mezcladas: cómo conviven

**Ninguna fila 4.6.0 se reescribe ni se borra.** Es la Constitución 5.0 de
`CLAUDE.md`, y el relevo la hereda sin excepción: el motivo de que
`senales.py` filtre toda métrica por `WHERE legacy = 0 AND modelo_version =
?` (líneas 441 y 493) es exactamente evitar que dos lógicas de señal se
promedien o se concatenen en un solo número. El relevo no cambia ese
patrón, lo usa.

**Cómo se vería una vista que muestre ambas series, propuesta:** dos
tarjetas lado a lado, nunca una sola cifra fusionada:

```
+- modelo 4.6.0 (histórico) ------+   +- modelo X.Y.Z (activo) ----------+
| n = 248, hasta DD-mmm-AAAA      |   | n = <n>, desde DD-mmm-AAAA       |
| acierto 66.1% [60.0-71.7] IC95  |   | acierto <cifra> [IC95 Wilson]    |
| vs. base 59.7% [53.5-65.6]      |   | vs. base <cifra> [IC95 Wilson]   |
| McNemar p = 0.1849              |   | McNemar p = <cifra>              |
+----------------------------------+   +-----------------------------------+
```

Es el mismo patrón que ya existe en el README para la ventana sellada y la
ventana larga: "el badge de ventaja se desdobla en dos, porque una sola
cifra ya no representa al proyecto" (DECISIONES.md §35.6). Ahí la razón es
que dos ventanas miden preguntas distintas; aquí la razón es más fuerte
todavía: son dos lógicas de señal distintas, y fusionarlas destruiría el
sentido de tener un `modelo_version` sellado por fila.

---

## 7. Cómo se revierte

**El campeón 4.6.0 nunca se borra ni se desinstala.** `motor.py` no se toca
en ningún paso de este protocolo (Regla cero, heredada de
`GEMELO/DISEÑO.md`): sigue existiendo, sigue siendo ejecutable, y sigue
pudiendo calcular `prediccion_apertura_al(fecha)` para cualquier fecha,
incluidas las posteriores al relevo (nadie le quita los datos). Eso hace
que revertir sea, en el caso técnico, tan simple como volver a apuntar
`MODELO_VERSION` a `"4.6.0"` en `version.py` y retomar el sellado con el
motor congelado: no hay que reconstruir nada porque nada se desmanteló.

**Criterio de reversión propuesto, degradación sostenida, medida con la
misma disciplina de WS1, no por impresión:**

> Se abre una revisión humana de reversión si, sobre una ventana **Y = 3
> meses de operación del retador en producción, o n ≥ 150 filas selladas
> del retador, lo que ocurra primero** (el mismo par de condiciones del
> gatillo de la §2, por consistencia), el McNemar retador vs. campeón
> resulta negativo (el campeón habría acertado más) con **p < 0.05**, o el
> DSR del retador, recalculado sobre esa ventana con el `N_intentos`
> acumulado real (nunca reiniciado), **cae por debajo de 0.95**.

(Un DSR es una probabilidad en [0,1], no un Sharpe — no se compara contra
`SR0`, que es la barra de Sharpe esperado bajo la nula; se compara contra
el umbral 0.95 de probabilidad, el mismo que exige REL-V3.)

La comparación retador vs. campeón en esta ventana es posible precisamente
porque el motor congelado sigue siendo ejecutable: se recalcula
`motor.prediccion_apertura_al(D)` para las mismas fechas que el retador
predijo en producción (dato point-in-time idéntico al que el campeón
habría usado si siguiera sellando) y se comparan ambas series sobre las
mismas filas. El campeón no necesita estar sellando para servir de
referencia, solo necesita seguir siendo ejecutable, y lo es.

**Esto se apoya en una reconstrucción del campeón — la misma clase de
evidencia que la §4 declaró insuficiente para decidir un relevo hacia
adelante.** La asimetría es real y se nombra en vez de esconderla: para
INSTALAR un retador se exige evidencia point-in-time (out-of-sample
verificable por timestamp); para REVERTIR se acepta una reconstrucción,
porque el costo de un falso negativo de reversión (dejar un modelo
degradado sellando en producción) es más alto que el costo de un falso
positivo (volver al campeón congelado, que no cuesta nada y no rompe
ninguna fila). Si esta asimetría no se acepta, la alternativa —más cara,
más lenta, y la que evita el problema del todo— es sellar ambos modelos en
paralelo durante toda la ventana de vigilancia de reversión, de forma que
la comparación también sea point-in-time; queda marcado como una opción,
no como la elegida.

**Aviso de potencia:** con 150 filas del retador (n efectivo, por el mismo
clustering intra-fecha de la §2.2, probablemente entre 40 y 60), un
McNemar retador-vs-campeón negativo con p < 0.05 requiere una degradación
grande y consistente para ser detectable — en la práctica, esta válvula de
reversión por vía estadística es débil a n mínimo, y probablemente no
dispare ante una degradación moderada. El sellado en paralelo del párrafo
anterior es la vía que sí resuelve esto, a costa de mantener dos modelos
sellando a la vez.

Este umbral es una propuesta razonada, igual que los de la §3: la palabra
final sobre el número exacto de Y y del p-valor es de Nicolás.

---

## 8. Qué NO cuenta como justificación de relevo

Declarado aquí, antes de que exista la tentación de leerlo en un resultado
favorable:

1. **Ganarle a "siempre al alza" sin ganarle al campeón directamente.** Un
   retador que supera la baseline pero no pasa REL-V1 (McNemar retador vs.
   campeón, no retador vs. baseline) no califica: puede estar ganando
   exactamente en el mismo lugar donde el campeón ya gana, sin aportar
   nada sobre él. `GEMELO/resultados/control_lineal.md` (hallazgo 1) ya
   encontró esto en el propio proyecto: C1 y el campeón aciertan las mismas
   filas (McNemar 0 vs 0);
   cualquier comparación que ignore al campeón y solo mire la baseline
   puede estar celebrando la misma información dos veces.
2. **Un resultado significativo en la ventana larga reconstruida que no se
   replica en la ventana sellada en vivo.** La ventana larga (n=14.618,
   +15.66 pp) no es track record verificable por timestamp (§4): es
   reconstrucción histórica, útil para diseñar, inválida para decidir un
   relevo por sí sola. Si el retador solo gana ahí y no en las filas
   selladas post-desarrollo, la conclusión honesta es que el resultado no
   sobrevivió el cruce a producción, no que el relevo está justificado.
3. **Un PSR o un DSR que sature en 1.0000 con pocas sesiones.** WS2b ya
   documentó el artefacto: a 30 días un Sharpe anualizado (~5.5) infla el
   PSR/DSR hasta la saturación de doble precisión, que se leería como "pasa
   V5" sin serlo, de ahí `MINIMO_DIAS_SHARPE = 60` como guarda explícita en
   vez de reportar el número saturado. El mismo precedente aplica aquí:
   ningún DSR de relevo se acepta bajo ese mínimo de días, y un DSR = 1.000
   se lee como "más allá de lo que el doble distingue" (comentario de
   cabecera de `inferencia.py`), nunca como certeza. **Aviso:**
   `MINIMO_DIAS_SHARPE = 60` vive en `GEMELO/control_lineal.py`, no en
   `backtest/inferencia.py` — quien evalúe REL-V3/REL-V5 llamando
   `inf.dsr()` o `inf.sr0_deflacionado()` directamente NO hereda esa guarda
   automáticamente y tiene que aplicarla a mano, o la guarda debe migrarse
   a `inferencia.py` antes del primer relevo evaluado.
4. **Probar variantes hasta que una gane, sin declarar el conteo de
   intentos en el DSR.** Es el sesgo exacto que el DSR existe para medir
   (`GEMELO/DISEÑO.md` §4.2 bis), y REL-V3 (§3.1) lo hereda explícitamente:
   el `N_intentos` del relevo nunca se reinicia en 1 solo porque una
   configuración "llegó" a esta etapa.

---

## 9. Qué NO se hace en este documento

- **No se toca `motor.py`, `senales.py` ni `version.py`.** Es un documento,
  no un commit de código.
- **No se evalúa si GEMELO 6.0.0 cumple estos criterios hoy**, y no hay en
  este documento ninguna frase que compare un resultado del retador contra
  un umbral de aquí. **Pero la ceguera no es total, y decirlo es más
  honesto que no decirlo:** el umbral de 5 pp de REL-V4 está anclado en un
  resultado ya medido (la abstención por magnitud del §2.4 de
  `GEMELO/DISEÑO.md`), y REL-V1 (retador vs. campeón, nunca solo vs.
  baseline) está motivado por un hallazgo ya conocido del WS2b (C1 y el
  campeón aciertan las mismas filas). Ambos criterios están informados por
  modos de falla ya observados en este proyecto — que es exactamente cómo
  se diseña un buen criterio, no un defecto — pero significa que este
  pre-registro es ciego al RESULTADO de un relevo futuro, no al historial
  del proyecto que ya existía al escribirlo.
- **No se mueve el gatillo de la Etapa 5.1** (`backtest/DISEÑO.md` §11): el
  relevo se apoya en él, no lo reemplaza ni lo adelanta.
- **No se decide aquí el n mínimo definitivo, ni el margen definitivo, ni
  la ventana de reversión definitiva.** Cada número de la §2, la §3 y la §7
  es una propuesta razonada y queda marcado como tal. La decisión final es
  de Nicolás.

---

## 10. Riesgos declarados, antes de empezar

1. **El n mínimo de la §2.2 (150) es una analogía con el gatillo de la
   5.1, no una medición propia del problema de relevo.** Reemplazar un
   campeón podría razonablemente exigir más n que "el backtest merece
   correrse con veredicto"; no hay evidencia hoy de cuál es el n correcto
   para esa pregunta específica.
2. **El margen de 5 pp de REL-V4 es una propuesta sin medición dedicada,**
   apoyada por analogía con la magnitud de la abstención por umbral de
   `GEMELO/DISEÑO.md` §2.4. Un margen mal calibrado puede ser demasiado
   laxo (deja pasar ruido) o demasiado exigente (nunca deja pasar nada,
   volviendo el relevo inalcanzable por diseño).
3. **El chequeo de fecha de congelamiento de la §4 (punto 2) no está
   construido.** Es una propuesta razonable, no un mecanismo verificado
   hoy. Hasta que se construya, la única defensa real contra la fuga
   informal es el aislamiento estructural de los tres tests AST, más
   débil que tener ambos.
4. **La comparación retador vs. campeón de la §7 asume que `motor.py`
   sigue siendo ejecutable sin cambios de entorno** (versiones de
   librerías, disponibilidad de datos de Yahoo para fechas pasadas). Si el
   entorno rota lo suficiente, recalcular el campeón para comparar puede
   dejar de producir números idénticos a los que habría sellado en vivo:
   un riesgo que ya existe hoy para cualquier reproducción histórica y que
   este documento no resuelve, solo hereda.
5. **Presión por acelerar el relevo una vez que el retador "casi" cumple.**
   Es el mismo riesgo que cualquier pre-registro nombra: la tentación de
   mover un umbral cuando el resultado está cerca es más fuerte,
   precisamente, cuando está cerca. Este documento es la defensa contra
   eso, y una defensa contra la tentación es más débil el día en que la
   tentación aparece, no antes. Queda escrito ahora porque ahora es cuando
   vale.

---

## 11. Lo primero que hay que hacer si algún día se activa este documento

**Nada, hasta que se cumplan la §2.1 y la §2.2.** Este documento no abre
ningún trabajo de construcción. Cuando ambos gatillos se cumplan, lo
primero es construir el chequeo de fecha de congelamiento propuesto en la
§4 (punto 2): sin él, el out-of-sample que decide el relevo no tiene la
segunda pierna de su verificación, y evaluar sin eso sería exactamente el
tipo de atajo que este documento existe para impedir.
