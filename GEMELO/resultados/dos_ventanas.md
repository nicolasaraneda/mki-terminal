# La contradicción de las dos ventanas

> **Nota de proceso:** la primera versión de este documento fue revisada por
> `estadistico-adversario` y **RECHAZADA** — trataba las 248 filas selladas
> como 248 observaciones independientes, cuando en realidad son 34 fechas de
> emisión (cada una con 7-8 tickers que comparten el mismo signo, porque el
> signo del modelo en un día dado es el signo del retorno del SOX de ese
> día). Esta versión corrige eso y además encuentra, al hacerlo bien, el
> hallazgo más informativo de todo el documento (§4). Lo que sigue está
> recalculado y auto-verificado; donde una cifra viene de la revisión
> adversaria y no la reproduje yo misma, se dice así explícitamente.

El campeón muestra **+15.66 pp** con p≈0 sobre **n=14.618** en la
reconstrucción de ocho años (fuente exacta: `GEMELO/resultados/auditoria_ws3.md`,
tabla de la convención `excluir_cero`: n=14.618, modelo 70.25%, base 54.59%),
y **+6.5 pp** (exacto: +6.45 pp) con McNemar p≈0.185 sobre las **248**
predicciones selladas en vivo (`excluir_cero`, cifra vigente al 31-ago-2026).
Las dos son ciertas. Este documento hace tres cosas: computa lo que se puede
computar hoy con `evaluacion.py` sobre los datos ya sellados; diseña —sin
correrlo— un experimento que discrimine entre las dos explicaciones que
plantea el enunciado; y reporta un tercer hallazgo, no pedido pero
encontrado en el camino, que resulta ser el más importante de los tres.

Todos los números de esta sección se recalcularon desde `senales.db` en
modo lectura, con la query `SELECT gap_pct, acierto_gap FROM
verificacion_apertura WHERE legacy=0 AND modelo_version='4.6.0' AND
gap_pct IS NOT NULL AND gap_pct != 0.0`: **b=72** (modelo acierta, "siempre
al alza" falla), **c=56** (al revés) — reproduce 66.1%/59.7%. El
p canónico de 0.1849 es **chi-cuadrado con corrección de continuidad**
((|16|−1)²/128 = 1.7578 → p=0.1849); `mcnemar_exact` del módulo, que usa la
binomial exacta, da **p=0.1847** — ambos redondean a 0.18, la diferencia es
de método, no un error, y se documenta acá porque la versión anterior de
este documento dijo que `mcnemar_exact` "reproduce exactamente" el 0.1849, y
no es así.

## 0. El problema de independencia que invalidó la primera versión

Las 248 filas no son 248 unidades independientes: son **34 fechas de
emisión** (2026-07-05 a 2026-08-26), con 7.3 tickers por fecha en promedio,
y dentro de una misma fecha el acierto del modelo está fuertemente
correlacionado entre tickers — el modelo predice el signo del gap con el
signo del retorno del SOX de esa noche, así que si el SOX subió, el modelo
apostó "sube" para los 7-8 tickers de esa fecha a la vez. Un bootstrap por
cluster de fecha (resampleando las 34 fechas con reemplazo, no las 248
filas; 10.000 réplicas, semilla 7, reproducido de forma independiente) da
una varianza de la ventaja pareada **3.6 veces mayor** que la que asume el
cálculo ingenuo fila-por-fila — un **DEFF (design effect) de 3.6**, en el
rango 2.5-3.6 que reportó también la revisión adversaria por un camino
distinto (bloques de 20 filas vs. cluster por fecha exacta). Eso convierte
las "248 observaciones" en algo entre **69 y 99 unidades efectivamente
independientes**. Todo el análisis de potencia de este documento tiene que
usar esa cifra, no 248.

## 1. Análisis de potencia, corregido por el clustering

Con la fórmula de Connor (1987) para el n de un McNemar pareado (p_d =
(b+c)/n = 0.5161 fijo), el n de filas IID necesario para potencia 0.80 y
α=0.05:

| Efecto a detectar | n IID necesario | n IID × DEFF (2.5–3.6) |
|---|---|---|
| +15.66 pp | 163 | **408 – 587** |
| +6.45 pp (la observada) | 971 | **2.427 – 3.495** |

Con **n=248 filas reales** (equivalentes a 69-99 filas independientes bajo
clustering), la potencia real para detectar +15.66 pp es:

| n efectivo | potencia para +15.66 pp |
|---|---|
| 69 (DEFF alto) | **43.9%** |
| 99 (DEFF bajo) | **58.5%** |
| 248 (si fueran IID — NO lo son) | 93.4% (cifra de referencia, no aplicable) |

**Esto retracta la conclusión más fuerte de la versión anterior.** Con una
potencia real de 44-59% —esencialmente una moneda al aire—, no haber visto
un resultado significativo NO es evidencia en contra de que el régimen en
vivo tenga un efecto de +15.66 pp: con esas chances, no verlo es
prácticamente tan probable como verlo. La frase "un efecto de +15.66 pp ya
se habría delatado y no lo hizo" no sobrevive la corrección — se retira.

## 2. A qué ritmo crece n, corregido

El ritmo de sellado medido por `integridad-datos` y reproducido acá de forma
independiente es de **6.53 filas/día hábil** (248 filas / 38 días hábiles
del rango 05-jul a 28-ago) — ese número está bien y no cambia. Lo que
cambia es cuántas filas hacen falta: bajo clustering, para llegar a 80% de
potencia sobre +6.45 pp hacen falta entre **2.427 y 3.495 filas totales**,
es decir **2.179 a 3.247 filas más** que las 248 actuales — no las 709 de
la versión anterior (que asumía IID).

A 6.53 filas/día hábil: entre **334 y 497 días hábiles** más, es decir
entre **467 y 696 días calendario**. Desde hoy (31-ago-2026), eso cae entre
**~11-dic-2027 y ~27-jul-2028** — no "enero-febrero de 2027". Es una
diferencia de más de un año respecto a la versión anterior de este
documento, y la causa es enteramente el clustering: cada fecha nueva de
emisión aporta ~7 filas pero solo ~1 unidad de información independiente.

**Traducción honesta: a este ritmo, la ventana sellada no va a tener
potencia estadística para resolver esta pregunta por sí sola en un plazo
razonable.** Esperar no es una estrategia — es exactamente lo que motiva
el diseño de un experimento distinto en el §4.

## 3. El intervalo correctamente calculado

El CI de Wald de la versión anterior ([-2.45, +15.36] pp) asumía filas
independientes y por lo tanto es demasiado angosto. Con el bootstrap por
cluster de fecha (mismo procedimiento del §0, reproducido de forma
independiente: percentil 2.5/97.5 sobre 10.000 réplicas, semilla 7):

**CI 95% (cluster por fecha) = [−10.04 pp, +23.67 pp]**

(la revisión adversaria, con un bootstrap de bloques de 20 filas del propio
módulo `evaluacion.py`, obtuvo un intervalo consistente, [−4.84, +22.58] pp
— más angosto que el cluster por fecha porque un bloque de 20 filas no
respeta el límite real de la correlación, que es la fecha, no un tamaño de
bloque arbitrario; el cluster por fecha es el más honesto de los tres y es
el que se adopta acá).

**Con el intervalo correcto, +15.66 pp cae CÓMODAMENTE adentro, lejos del
borde** — no "rozando por 0.3 pp" como decía la versión anterior (esa
lectura comparaba mal qué tan sensible era el número a un redondeo, y la
comparación estaba invertida: mover Δ de 6.45 a 6.5 pp mueve el borde
superior solo 0.05 pp, no 0.3 pp — el margen de 0.3 pp real viene de sumar
una sola fila más al numerador de discordancias, b=73 en vez de 72, que sí
lo empuja a 15.73 pp; esa es la única parte de la observación original que
sobrevive). La conclusión de fondo — **el intervalo sellado NO discrimina
entre las dos explicaciones** — se mantiene, y de hecho se refuerza con el
número correcto: el cero y el +15.66 pp están cómodamente adentro del mismo
intervalo al mismo tiempo.

## 4. El experimento que discrimina — rediseñado

El diseño original proponía correr `backtest/linea_base.py` restringido a
las fechas de la ventana sellada. Es un diseño inválido: `linea_base.py`
recalcula las métricas leyendo las **filas ya selladas** de `senales.db` —
correrlo sobre esas fechas reproduce, por construcción, las mismas 248
filas y el mismo +6.45 pp. No es un tercer número independiente, es el
mismo número con otro nombre. El módulo correcto para "qué hubiera dicho la
metodología de la ventana larga sobre estas fechas" es la reconstrucción de
`GEMELO/ventana_larga.py` (`backtest.baselines.B2Produccion` +
`FuenteCongelada`) — la misma maquinaria que generó el +15.66 pp de ocho
años, aplicada a un tramo específico.

**Pero incluso con el módulo correcto, la comparación "reconstrucción
restringida a esas fechas vs. sellado en vivo" ya tiene una respuesta
conocida y no sirve como discriminador**: `GEMELO/DISEÑO.md` §2.8 ya
estableció que la reconstrucción B2 reproduce las predicciones selladas
reales dentro de 0.05 pp de media (21 de 21 cifras titulares reproducidas
exactas). Es decir, ya se sabe que reconstrucción-en-esas-fechas ≈
sellado-en-esas-fechas ≈ +6.45 pp. Correr ese experimento no comprobaría
nada nuevo — comprobaría, otra vez, que el backtest reproduce la
producción, que ya está demostrado.

**El diseño corregido, congelado antes de ejecutar cualquier cosa:**
comparar la ventana sellada (34 fechas, +6.45 pp) contra el **complemento**
de la ventana larga — los ocho años MENOS esos mismos 34 días — nunca
contra el agregado completo, porque el agregado completo ya contiene a la
ventana sellada y compararla contra un conjunto que la incluye no es una
comparación independiente. El criterio de decisión se congela ACÁ, antes de
correr nada:

- Se calcula el CI 95% (bootstrap por cluster de fecha, mismo método del
  §0/§3) de la ventaja en el complemento (ocho años menos los 34 días).
- Si el punto estimado del complemento y el +6.45 pp sellado caen dentro
  del mismo intervalo combinado (misma lógica del §3): **son la misma
  distribución, medida con distinto ruido** — apoya "solo hacía falta más
  potencia".
- Si los intervalos no se solapan: **hay una diferencia real entre el
  período reciente y el resto de los ocho años** — un cambio de régimen, no
  un error de medición.
- Si el resultado es ambiguo (se solapan pero los puntos centrales están
  lejos), se declara así, sin forzar una lectura.

Esto es un intento reportable para el conteo del DSR de WS1 —
`GEMELO/DISEÑO.md` §4.2bis no tiene una excepción para "diagnóstico": la
propia regla congelada define un intento como "(configuración × ventana de
evaluación) con resultado reportable", y este lo es. El registro de
intentos hoy es N=25 (backtest B0-B5, C1-C3 sellada, C1-C3 larga, campeón
reconstruido, WS5 — ver `GEMELO/resultados/preregistro_ws5.md`); correr
esto lo sube a **N=26**, y esa cuenta se declara ANTES de correrlo, no
después. Elegir la ventana sellada precisamente porque ahí se observó la
discrepancia es selección post-hoc — se declara explícitamente como tal, es
exactamente lo que el DSR existe para penalizar, y por eso este experimento
no se corre sin que Nicolás decida gastarlo.

## 5. Lo que sí se pudo computar ahora y es el hallazgo más importante

Al descomponer la ventana sellada por sub-período —no pedido por el
enunciado, encontrado mientras se verificaba el clustering del §0— aparece
esto (recalculado y verificado de forma independiente, no es una cita de
la revisión adversaria):

| Sub-período | n | b, c | Ventaja | McNemar p |
|---|---|---|---|---|
| **15 al 23-jul-2026** (6 fechas) | 44 | 24, 6 | **+40.9 pp** | **0.0014** |
| **Resto de la ventana** (28 fechas) | 204 | 48, 50 | **−1.0 pp** | 0.9196 |
| Ventana completa | 248 | 72, 56 | +6.5 pp | 0.185 |

**La totalidad de la ventaja sellada vive en seis fechas de julio.** Fuera
de ese bloque, la ventaja del modelo sobre "siempre al alza" es
literalmente negativa e indistinguible de cero. Esto es más informativo que
las dos explicaciones que este documento se propuso discriminar: no hace
falta esperar cinco meses ni gastar un intento del DSR para saber que
**tratar el +6.45 pp como la medición de un efecto de régimen estable es
un error de lectura ya, con los datos de hoy** — sea cual sea la razón del
concentramiento (una semana de alta volatilidad donde el mecanismo de
contagio SOX→Asia/Europa funcionó con fuerza inusual, o un artefacto de
tener solo 34 fechas). Cuál de las dos es una pregunta abierta que este
documento no resuelve — requeriría revisar qué pasó en esas seis fechas
específicas (régimen de mercado, eventos de noticias) contra
`resumen_dia`, trabajo que no se hizo acá y que queda declarado como
pendiente, no como blocker de este hallazgo.

Adicionalmente, el desglose de la ventana sellada por bolsa (recalculado,
join `verificacion_apertura`/`senales_ticker` sobre `exchange`):

| Bolsa | n sellada | Ventaja sellada | p | Ventaja ventana larga |
|---|---|---|---|---|
| XTKS (Tokio) | 128 (51.6%) | +8.6 pp | 0.21 | +19.1 pp |
| XKRX (Seúl) | 60 (24.2%) | **+0.0 pp** | 1.00 | +15.4 pp |
| XTAI (Taipéi) | 27 (10.9%) | +7.4 pp | 0.80 | +16.8 pp |
| XETR (Fráncfort) | 33 (13.3%) | **+9.1 pp** | 0.63 | +2.5 pp |

Todos los intervalos son demasiado anchos para ser concluyentes por sí
solos, pero el patrón es visible: **el orden del decaimiento con la
distancia horaria se invierte en la ventana sellada** — Fráncfort (8.75h,
el peor en ocho años) es la mejor bolsa sellada, y Seúl (1.75h, de las
mejores en ocho años) da exactamente cero. La composición por bolsa de la
ventana sellada es, según la revisión adversaria de este documento (no
reproducido por mí de forma independiente en esta pasada, cifra atribuida),
muy parecida a la de la ventana larga (dentro de 1.5 pp en las cuatro
bolsas) — así que la diferencia de mezcla de exchanges NO explica la brecha
entre +15.66 pp y +6.45 pp. Esto cierra una de las hipótesis candidatas del
chequeo secundario del §4 original sin necesidad de ejecutarlo.

## 6. El decaimiento con la distancia: pista, no explicación — y ahora con una grieta

El patrón de `GEMELO/DISEÑO.md` §2 (+19.1 pp Tokio a 1.75h, +2.5 pp p=0.111
Fráncfort a 8.75h) sigue siendo la mejor pista disponible sobre por qué el
efecto varía dentro de la ventana larga. Pero la tabla del §5 muestra que
ese orden **no se repite** en la ventana sellada — con Fráncfort mejor que
Seúl, muestras chicas e intervalos anchos de por medio. No alcanza para
refutar el mecanismo de decaimiento (los intervalos son compatibles con
cualquier orden), pero tampoco lo confirma en esta ventana, y decir
"decae con la distancia" sin decir "y en la ventana sellada el orden
observado es distinto, aunque no significativamente" sería una lectura
incompleta. El decaimiento sigue siendo un mecanismo medido y real sobre
ocho años; sobre 248 filas, hoy, no hay evidencia que lo confirme ni que lo
contradiga con ninguna confianza.
