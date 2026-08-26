# GEMELO 6.0.0 — Diseño del modelo retador

**Estado:** PRE-REGISTRO. Congelado antes del primer resultado.
**Corrección posterior:** la §2.8 (26-ago) corrige la línea base con lo
medido en el harness, y actualiza V1 y R2 en consecuencia. Las cifras de
la §2.1–§2.7 se conservan como se escribieron: se corrigen ahí, no aquí.
**Fecha:** 25-ago-2026 · **Campeón vigente:** modelo 4.6.0
**Insumos:** track record sellado al 24-ago (228 verificaciones) ·
`vcalderone/equity-direction-research` v2.1.0 (MIT)

Este documento se escribe **antes** de construir nada, en la misma tradición
que `backtest/DISEÑO.md` en el GATE B. Los criterios de victoria de la §6 se
fijan aquí y no se tocan después de ver resultados. Si el retador pierde bajo
estos criterios, pierde.

> **Regla cero:** `motor.py` y el modelo 4.6.0 no se tocan. El campeón sigue
> sellando en producción durante toda la etapa. GEMELO es un segundo motor que
> corre en paralelo y se mide contra él.

---

## 1. Por qué existe esta etapa

Porque el número que el proyecto viene publicando responde a una pregunta más
fácil que la que cree estar respondiendo.

`/historial` informa acierto de dirección del gap. Ese número, medido contra
cero, describe qué tan seguido el modelo acierta. Pero la pregunta que importa
es **cuánto mejor lo hace que no saber nada**, y en una ventana de mercado con
deriva marcada, "no saber nada" es sorprendentemente competitivo.

La §2 mide eso. El resultado reorganiza la etapa entera.

---

## 2. La línea base medida — el denominador honesto

Todo lo que sigue es cálculo directo sobre `data/backups/*.csv` al 24-ago,
uniendo `senales_senales_ticker.csv` con `senales_verificacion_apertura.csv`
por `(fecha, ticker)`. n = 228 verificaciones, todas modelo 4.6.0, ninguna
legacy.

**Estas cifras son mías, no de `/historial`.** Antes de que el retador se
construya, el harness de `backtest/` tiene que reproducirlas. Si difieren,
manda el harness y este documento se corrige.

### 2.1 El edge real

| | Acierto de gap | IC95 Wilson |
|---|---|---|
| Modelo 4.6.0 | **65.8%** (150/228) | [59.4 – 71.6] |
| "Siempre al alza", mismas filas | **60.5%** (138/228) | [54.1 – 66.6] |
| **Ventaja** | **+5.3 pp** | — |

McNemar sobre los desacuerdos: el modelo acierta donde la baseline falla 67
veces; la baseline acierta donde el modelo falla 55 veces. **p = 0.32.**

**La ventaja direccional del campeón sobre una constante no es distinguible de
cero con n=228.** No es que el modelo no sirva: es que el 65.8% publicado
convive con una tasa base del 60.5% en esta ventana, y la diferencia cabe
dentro del ruido.

Esto es exactamente para lo que `backtest/DISEÑO.md` puso B0 en la lista. La
diferencia es que ahora está medido sobre los sellos reales.

### 2.2 Dónde está la ventaja, en el tiempo

| Bloque | Desde | Hasta | n | Modelo | Siempre alza | Ventaja |
|---|---|---|---|---|---|---|
| 0 | 05-jul | 15-jul | 40 | 75.0% | 67.5% | +7.5 |
| 1 | 15-jul | 23-jul | 40 | 82.5% | 42.5% | **+40.0** |
| 2 | 24-jul | 30-jul | 40 | 57.5% | 62.5% | −5.0 |
| 3 | 31-jul | 10-ago | 40 | 67.5% | 72.5% | −5.0 |
| 4 | 10-ago | 18-ago | 40 | 62.5% | 77.5% | **−15.0** |
| 5 | 18-ago | 21-ago | 28 | 42.9% | 32.1% | +10.7 |

Casi toda la ventaja acumulada vive en el bloque 1. En los bloques 2, 3 y 4 el
modelo **pierde** contra la constante.

### 2.3 La hipótesis del punto de giro: refutada

La lectura tentadora del cuadro anterior es que el modelo sabe girar y la
métrica lo esconde. Se puede probar, y no se sostiene:

| Partición | n | Modelo | Siempre alza | Ventaja | p |
|---|---|---|---|---|---|
| SOX usado < 0 | 71 | 45.1% | 52.1% | **−7.0** | 0.63 |
| SOX usado ≥ 0 | 69 | 76.8% | 73.9% | +2.9 | 0.50 |

Cuando el insumo dice "baja" —el caso contrarian, el que justificaría la
tesis— el modelo lo hace **peor** que la constante. El +40 del bloque 1 fue
una ventana afortunada, no habilidad sistemática en los giros.

Queda anotado: la hipótesis se formuló y se refutó **antes** de diseñar nada
sobre ella.

### 2.4 La zona muerta: el hallazgo accionable

Acierto por quintil de magnitud predicha:

| Quintil de \|predicción\| | n | Acierto | Gap real medio | MAE |
|---|---|---|---|---|
| 0.01 – 0.27 pp | 47 | **44.7%** | −0.05 | 1.82 |
| 0.27 – 0.70 | 44 | 65.9% | 0.54 | 1.91 |
| 0.70 – 1.45 | 46 | 71.7% | −0.07 | 2.47 |
| 1.45 – 2.68 | 45 | **84.4%** | 1.11 | 2.58 |
| 2.68 – 6.91 | 46 | 63.0% | 5.48 | **6.51** |

El quintil más chico —el 21% de todas las predicciones— acierta **por debajo
de una moneda al aire**. Y el quintil más grande acierta razonable pero yerra
la magnitud por 6.5 pp: predice fuerte y se queda corto.

Abstenerse bajo un umbral, contra la misma baseline:

| Umbral \|pred\| | n | Modelo | Base | Ventaja | McNemar p | Descartado |
|---|---|---|---|---|---|---|
| 0.00 | 228 | 65.8% | 60.5% | +5.3 | 0.32 | 0% |
| 0.15 | 207 | 68.6% | 60.9% | +7.7 | 0.16 | 9% |
| **0.25** | 184 | **71.2%** | 63.0% | **+8.2** | 0.17 | 19% |
| 0.30 | 180 | 71.7% | 63.9% | +7.8 | 0.20 | 21% |
| 0.50 | 150 | 70.0% | 66.0% | +4.0 | 0.59 | 34% |
| 0.75 | 135 | 74.1% | 66.7% | +7.4 | 0.31 | 41% |

La ventaja sube de +5.3 a +8.2 pp descartando el 19% de las emisiones. Sigue
sin ser significativa a n=184, pero **es la única intervención medida que
mueve la aguja sin tocar el modelo**.

Es prima de la regla de abstención por sello tardío ya propuesta en
`DECISIONES.md`, pero por otra razón: aquélla se abstiene por **timing**, ésta
por **magnitud**. Son independientes y compatibles.

### 2.5 Lo que el modelo sí aporta y la baseline no puede

| Predictor | MAE del gap |
|---|---|
| Modelo 4.6.0 | **3.064 pp** |
| Predecir 0.0 | 3.423 pp |
| Predecir la media histórica | 3.395 pp |

**+10.5% sobre predecir cero.** Modesto, pero real — y "siempre al alza" ni
siquiera produce una magnitud contra la cual comparar.

Conclusión incómoda y central: **la contribución medible del campeón está más
en la magnitud que en la dirección, y la métrica que el proyecto publica mide
la dirección.**

### 2.6 El R² sellado no discrimina

Acierto por cuartil de `confianza_r2`: 64.9% · 63.2% · 66.7% · 68.4%.
Tendencia leve, no monótona, dentro del ruido.

Y entre bolsas la relación **se invierte**:

| Exchange | n | Modelo | Base | Ventaja | R² medio | MAE |
|---|---|---|---|---|---|---|
| XTKS (Tokio) | 117 | 67.5% | 61.5% | +6.0 | 0.177 | 2.72 |
| XKRX (Seúl) | 54 | 64.8% | 68.5% | **−3.7** | 0.173 | **5.30** |
| XETR (Fráncfort) | 29 | 65.5% | 55.2% | +10.3 | **0.005** | 1.90 |
| XTAI (Taipéi) | 28 | 60.7% | 46.4% | +14.3 | **0.251** | 1.40 |

Fráncfort tiene un R² de 0.005 —cero explicación— y saca +10.3 sobre su base.
Taipéi tiene el R² más alto y el acierto más bajo. **El R² tal como se sella
no mide calidad predictiva.** Un intervalo construido sobre él hereda el
problema.

Seúl es la única bolsa por debajo de su propia tasa base, y también la de peor
MAE.

### 2.7 Los intervalos son anchos y el régimen es una constante

**Calibración:** cobertura empírica **89.5%** contra un nominal de 80%, con un
ancho medio de 5.43 pp frente a un error absoluto medio de 3.06 pp — **1.77×
más anchos de lo necesario**. El acta anotó 87.4% en julio; la deriva
continúa.

**Régimen:** *una sola etiqueta distinta en los 35 snapshots sellados*, mientras
la volatilidad realizada del SOX a 10 días recorre de 2.23 a 4.49 — un rango de
2×. Una columna sin varianza no puede condicionar nada. El caveat del README
dice "casi entera de un solo régimen"; la medición dice que es **entera**, y
que la etiqueta no detecta la variación que sí existe.

**Estabilidad de β:** el salto medio entre días consecutivos es 0.043 sobre un
nivel medio de 0.544 — **8% del nivel, por día**. La mediana es 0.010, o sea
que casi siempre está quieto, pero el **11.3%** de los pares salta más de 0.10
y el máximo observado es 0.280. Es la firma de una ventana rodante de 120
sesiones dejando entrar y salir observaciones influyentes.

### 2.8 Corrección de la línea base — medida en el harness

**Añadida el 26-ago, después del pre-registro y en commit aparte.** La §9
ordenaba reproducir la §2 dentro de `backtest/` antes de construir nada.
Se hizo: `backtest/linea_base.py` recalcula todo desde `senales.db` en
`mode=ro`. **21 de 21 cifras titulares reproducen exactas** — n, aciertos,
McNemar, MAE, cobertura, ratio de ancho, R², zona muerta, régimen y β,
más los cuatro cortes por bolsa dígito a dígito.

Aparecieron dos problemas, y ninguno se arregla editando las cifras de
arriba: las de la §2 se quedan como se escribieron, y esta sección las
corrige con fecha posterior y a la vista.

#### 2.8.1 La convención del empate — el campeón se medía con otra regla

Hay **5 filas con `gap_pct == 0.00` exacto**. Apertura idéntica al cierre
previo es la firma del **ffill de feriados** (Supuesto #1 de `CLAUDE.md`:
"un feriado se ve como +0.00%"). Cuatro de las cinco son 2330.TW.

El verificador de producción puntúa al campeón con `>=`:

```
acierto_gap = 1 si (est_pct >= 0) == (gap >= 0)        senales.py:373
```

o sea que en esas filas **le da el acierto** a cualquier predicción ≥ 0.
La baseline de la §2.1 usaba `>` estricto, así que en esas mismas filas
**no se lo daba**. Los dos lados se estaban puntuando **con reglas
distintas, y la diferencia favorecía al campeón**. No es un error de
cálculo —las cifras reproducen— sino un sesgo de medición.

| Convención | n | Modelo | Base | Ventaja | McNemar | p |
|---|---|---|---|---|---|---|
| `estricta` — base con `>` (la de la §2.1) | 228 | 65.8% | 60.5% | +5.3 pp | 67 vs 55 | 0.3193 |
| `verificador` — base con `>=`, simétrica | 228 | 65.8% | 62.7% | +3.1 pp | 64 vs 57 | 0.5854 |
| **`excluir_cero` — fuera de ambos lados** | **223** | **65.9%** | **61.9%** | **+4.0 pp** | **64 vs 55** | **0.4633** |

**CONGELADA: `excluir_cero`.** Las filas con `gap == 0.00` se excluyen de
**ambos** lados. Razón: no son eventos de mercado, son artefactos del
ffill; el problema no es cuál de las dos reglas de empate es mejor, sino
que la apertura de un feriado no informa sobre nada. Excluir es la única
salida que no obliga a elegir a quién se le regala el empate.

**La línea base oficial pasa a: n = 223 · modelo 65.9% · base 61.9% ·
ventaja +4.0 pp · McNemar 64 vs 55, p = 0.4633.**

**Dónde vive la exclusión.** En la **capa de medición**
(`backtest/linea_base.py`), no en el verificador. **`senales.py` NO se
toca.** Cambiar el scoring reescribiría el significado de filas ya
selladas: `acierto_gap` es un valor sellado, y las filas selladas jamás se
reescriben. Un campeón cuyo histórico cambia de valor cuando cambiamos de
opinión sobre los empates no tiene track record.

La conclusión de la §2.1 no se mueve, se refuerza: bajo cualquiera de las
tres convenciones la ventaja del campeón sobre una constante **no es
distinguible de cero** con esta n.

#### 2.8.2 El reparto por bloques depende del orden de las filas

Los **límites** de la tabla de la §2.2 reproducen exactos: las seis
fechas y los seis n (40/40/40/40/40/28). Los **totales** reconcilian: la
partición de la §2.2 suma 150 aciertos del modelo y 138 de la base, igual
que el harness. Pero el **reparto interno no reproduce**: solo el bloque 2
coincide, y el 3 únicamente bajo un orden de filas concreto.

Se probaron cuatro órdenes —por `id` de la verificación, por
`(fecha, ticker)`, y el `merge` de los dos CSV en ambas direcciones— y
ninguno reproduce los bloques 0, 1, 4 y 5. Es la **misma partición de
filas cortada distinto**: en las fechas que caen sobre una frontera de
bloque, el orden interno decide de qué lado quedan.

**Consecuencia:** un índice de bloque no es una referencia estable y no
puede sostener un criterio. Por eso **R2 queda operacionalizado por
FECHAS**: la ventana **15–23 jul**, que sí es estable y no depende de
ningún orden. Ver §6.2.

---

## 3. Qué se concluye — las seis decisiones de diseño

Cada una responde a una medición de la §2, no a una preferencia.

1. **La métrica primaria deja de ser el acierto de dirección.** Contra una
   base que deriva, en un solo régimen, es casi no informativa (§2.1). El
   retador se juzga por **habilidad sobre la base** y por **CRPS** de la
   densidad predictiva completa.
2. **β pasa a espacio de estados.** La ventana rodante salta 8% diario y no
   entrega varianza posterior legítima (§2.7).
3. **Pooling jerárquico sobre la cadena.** Con R² ≈ 0.16 y n=120, cada β
   individual es ruido con forma de número (§2.6).
4. **El régimen pasa a estado latente.** La etiqueta actual es una constante
   (§2.7).
5. **Densidad predictiva con colas, no punto más intervalo.** Los intervalos
   sobran 77% (§2.7) y la magnitud es donde el campeón realmente aporta (§2.5).
6. **La abstención por magnitud entra en el retador.** Es la única
   intervención medida que mejora la ventaja (§2.4), y el campeón está
   congelado, así que no puede nacer ahí.

---

## 4. El retador — especificación

### 4.1 Estructura factorial

El campeón usa un factor: el SOX. El retador usa el conjunto de información
que se mueve **entre** el cierre de Nueva York y la apertura objetivo, que hoy
se descarta:

| Bloque | Regresores | Por qué |
|---|---|---|
| Contagio | SOX(t), SOX(t−1) | El README documenta 0.24 con el SOX del día y **0.38 con el del día anterior**. La estructura de rezago va explícita, no implícita en la ventana |
| Overnight US | futuros ES, NQ al momento de emisión | Se mueven después del cierre del SOX y antes de la apertura asiática. Hoy se tira |
| Divisa | USD/KRW, USD/TWD, USD/JPY, EUR/USD | El retorno en moneda local depende del tipo de cambio. Hoy no está |
| Mercado local | futuros de KOSPI, TWSE, Nikkei, DAX | Separa "gapea el mercado" de "gapean los semis" |
| Volatilidad | VIX, Δln(VIX), **VIX3M/VIX** | La estructura temporal es genuinamente prospectiva (de Calderón) |
| Crédito | ln(HYG/LQD) | Apetito por riesgo (de Calderón) |
| Noticias | sentimiento con decaimiento | `FEATURE_VERSION` ya lo anticipa |

Toda feature es **causal** y **estacionaria por construcción** — retornos,
razones, distancias; nunca niveles. La causalidad se prueba con un test de
propiedad: el valor en t debe ser invariante a borrar todo dato posterior a t.
El harness de `backtest/` ya tiene esa guarda (`ErrorLookAhead`); se extiende.

### 4.2 El modelo

**Nivel 1 — β variable en el tiempo.** Para cada ticker i y factor k, un
modelo de espacio de estados donde `β_ikt = β_ik,t−1 + η_ikt`, estimado con
filtro de Kalman. Sin ventana arbitraria; adaptación suave; y una varianza
posterior sobre β que sí significa algo.

**Nivel 2 — pooling jerárquico.** Los `β_ik` se agrupan por nivel de la cadena
(roca / chip / datacenter, ya declarados en `universo.py`) con priors
jerárquicos. Cada estimación se encoge hacia la media de su nivel en
proporción a su propia incertidumbre. Con n=120 y R²≈0.16 esto reduce error de
estimación sin un solo dato nuevo.

**Nivel 3 — régimen latente.** Markov-switching de 2 o 3 estados sobre
volatilidad y correlación, con los β condicionados al estado. La probabilidad
de estado es una salida del modelo, auditable, y reemplaza a la etiqueta
constante.

**Nivel 4 — densidad predictiva.** Innovaciones Student-t. La salida es una
distribución completa, no un punto con intervalo pegado. El intervalo al 80%
se lee de ella y la calibración deja de ser un parche.

**Nivel 5 — abstención.** Regla de magnitud (§2.4) más la regla de timing ya
propuesta en `DECISIONES.md`. Toda abstención se **declara** como estado
auditable propio, fuera de todas las métricas, jamás se rellena.

**Nivel 6 — ensemble.** El campeón 4.6.0 entra como componente con peso
variable en el tiempo. **No se descarta: se incorpora.**

### 4.2 bis Conteo de intentos para el DSR — declarado ANTES de correr

**Añadido el 26-ago (WS2a), antes de evaluar una sola configuración.**

**Cada configuración que se evalúe en WS2b cuenta como un intento para el
Deflated Sharpe.** No solo las que "funcionan", no solo las que se
reportan: **todas**. Una configuración es cualquier variante que se mida
contra los datos — un subconjunto distinto de features, otra
regularización, otra ventana, otro criterio de abstención.

**El número de variantes se declara ANTES de correr ninguna.** Declararlo
después es contar los intentos a conveniencia, y un DSR con el N mal
contado **miente hacia arriba**: es exactamente el sesgo que el DSR existe
para corregir, así que subestimar N no es un descuido menor sino la
inutilización del instrumento.

El conteo arrastra: los intentos de WS2b se **suman** a las seis baselines
B0→B5 que ya se evaluaron sobre los mismos folds. `sr0_deflacionado` no
tiene valor por defecto para `N_intentos` precisamente para forzar que
alguien escriba el número a mano cada vez (DECISIONES.md §26.1).

#### La regla de conteo, hecha explícita (declarada el 26-ago, antes del WS3)

**Cuenta como UN intento cada par (configuración × ventana de evaluación)
cuyo resultado sea reportable.**

Re-evaluar las mismas tres configuraciones sobre una ventana distinta
**no es gratis**: produce un segundo conjunto de resultados publicables
entre los cuales se puede elegir, y elegir entre resultados es
exactamente lo que el DSR deflacta. Una regla que contara "3
configuraciones" sin importar cuántas ventanas se prueben permitiría
buscar la ventana favorable sin coste, que es la misma trampa por otra
puerta.

**NO cuenta** la baseline "siempre al alza": no es un modelo ajustado ni
seleccionado, es la hipótesis nula contra la que se mide. Tampoco cuenta
la búsqueda interna de `alpha` por CV temporal, que se resuelve sin mirar
una sola fila de evaluación (§4.3).

Conteo al abrir el WS3, **antes de correr nada**:

| Intento | Ventana | Cuenta |
|---|---|---|
| B0–B5 | backtest walk-forward | 6 |
| C1, C2, C3 | ventana sellada (WS2b, n=223) | 3 |
| C1, C2, C3 | ventana larga (WS3) | 3 |
| Campeón reconstruido (= B2) | ventana larga (WS3) | 1 |
| **N total** | | **13** |

Ser conservador aquí es gratis: un N de más sube el umbral `SR0` y hace
al DSR más exigente. Un N de menos lo inutiliza.

### 4.3 El control lineal, obligatorio

Junto a todo lo anterior corre una regresión lineal regularizada sobre el
mismo conjunto de features. Tres afirmaciones falsables (de Calderón):

1. Si el modelo completo gana al lineal → hay estructura no lineal.
2. Si el lineal gana → la capacidad del modelo grande está ajustando ruido.
3. Si ninguno supera la baseline de la §2.1 → los features no traen señal, y
   la conclusión honesta es ésa.

---

## 5. Maquinaria de inferencia

Se incorpora de `vcalderone/equity-direction-research` (MIT, atribuido en
`DECISIONES.md` y en el encabezado de cada archivo derivado). Ninguna de estas
piezas existe hoy en MKI — verificado por grep sobre el repo.

| Pieza | Qué corrige | Referencia |
|---|---|---|
| **Deflated Sharpe Ratio** | B0→B5 son seis intentos sobre los mismos folds; el Sharpe del ganador está inflado por construcción. Barra: DSR ≥ 0.95 | Bailey & López de Prado 2014 |
| **Holdout libre de selección** | Cuarentena de datos, no solo de tiempo. Se evalúa **una vez** | López de Prado 2018 |
| **PSR + SE de Sharpe** | Un Sharpe sin barra de error es un punto disfrazado de hallazgo. Sobre ~1.000 días el SE anualizado ronda 0.5 | Lo 2002; Bailey & LdP 2012 |
| **Bootstrap de bloques** | Preserva el clustering de volatilidad que un bootstrap iid destruiría. Bloque 20 días | Politis & Romano 1994 |
| **Embargo en el walk-forward** | Purga la frontera contaminada entre train y test | López de Prado 2018 cap. 7 |
| **Importancia por permutación** | Las importancias por impureza están sesgadas con features correlacionados | Strobl et al. 2007 |
| **Vol targeting** | Separa la decisión de dirección de la de tamaño | Moreira & Muir 2017 |

**El holdout tiene una complicación propia que hay que resolver antes de
construir:** el track record vivo ya es, en cierto sentido, un holdout
perfecto — son datos que no existían cuando se escribió el código, la defensa
que el propio Calderón nombra como única contra el sesgo de especificación.
Pero se usa continuamente para monitoreo. **Qué se cuarentena y qué no es
decisión humana de Nicolás, y va escrita aquí antes de la primera corrida.**

---

## 6. Criterios de victoria — CONGELADOS

El retador reemplaza al campeón solo si cumple **todo** lo siguiente. Se fijan
ahora, sin resultados a la vista.

### 6.1 Barreras de entrada

- **V1 — Habilidad sobre la base.** Ventaja sobre "siempre al alza" evaluada
  en la misma ventana, con McNemar **p < 0.05**.

  *Actualizado el 26-ago con la línea base corregida de la §2.8.* La vara
  **descriptiva** pasa a **+4.0 pp con p = 0.4633 sobre n = 223**, bajo la
  convención `excluir_cero` congelada allí — antes se citaba +5.3 pp con
  p = 0.32, medido con reglas de empate distintas para cada lado.

  **El criterio NO se movió: sigue siendo McNemar p < 0.05.** Lo que cambió
  es la descripción de dónde está hoy el campeón, no la exigencia. Se dice
  explícitamente porque la tentación al corregir una línea base es ajustar
  de paso la barra que esa línea no alcanza: aquí no se hizo. El campeón
  sigue sin superar V1 —ahora por más margen— y el retador tendrá que
  superarla igual.
- **V2 — CRPS.** Mejora del CRPS de la densidad predictiva sobre el campeón,
  con intervalo de confianza por bootstrap de bloques que excluya el cero.
- **V3 — Calibración.** Cobertura empírica del intervalo 80% dentro de
  [76%, 84%]. El campeón está en 89.5% (§2.7).
- **V4 — Magnitud.** MAE del gap estrictamente menor que los 3.064 pp del
  campeón (§2.5), con la misma cobertura de emisiones o mayor.
- **V5 — Deflated Sharpe.** En el backtest económico, DSR ≥ 0.95 contando
  **todos** los intentos: las seis baselines B0→B5, más cada configuración del
  retador que se haya evaluado. Los intentos se cuentan honestamente o el DSR
  miente.
- **V6 — Benchmark obligatorio.** Superar comprar SMH y no hacer nada, después
  de costos de 25 pb por lado, con barrido de sensibilidad.
- **V7 — Holdout.** Confirmación en el holdout en cuarentena, evaluado una
  sola vez. **Si el walk-forward y el holdout discrepan, gana el holdout.**

### 6.2 Barreras de rechazo

El retador se descarta, sin apelación, si:

- **R1** — el control lineal le gana. Significa que la capacidad grande está
  ajustando ruido.
- **R2** — su ventaja desaparece al excluir la ventana **15–23 jul**, que
  sostiene casi toda la ventaja del campeón (§2.2). Un retador que solo
  repita esa suerte no aporta. *La regla se aplica por RANGO DE FECHAS y no
  por índice de bloque: el índice depende del orden de las filas y el rango
  no (§2.8.2).*

  **Hallazgo del 26-ago, y no ablanda la regla:** aplicada al **campeón**,
  esa misma prueba lo descalifica. Sin la ventana 15–23 jul queda en
  **n = 184 · modelo 62.0% · base 65.2% · ventaja −3.3 pp (p = 0.60)**: no
  pierde su ventaja, la vuelve **negativa**.

  **R2 se mantiene tal cual, deliberadamente.** Es una valla que hoy no pasa
  nadie, y que el titular tampoco la pase **es un resultado sobre el
  titular, no un defecto del criterio**. Bajarla para que el campeón entre
  sería exactamente lo que un pre-registro existe para impedir: mover la
  barra hasta donde ya está el que queremos aprobar. Si el retador la pasa y
  el campeón no, eso es precisamente la información que la etapa busca.
- **R3** — cualquier fuga detectada por el test de causalidad. Sin discusión y
  sin excepción.

### 6.3 Qué pasa si nadie gana

Se publica el negativo. Un retador que no supera al campeón, y un campeón que
no supera a una constante, es un resultado — y el proyecto ya tiene la
costumbre de publicar la corrida de humo marcada NO-CONCLUYENTE con su parte
incómoda a la vista.

**Un resultado negativo aquí no es un fracaso de la etapa. Es la etapa
funcionando.**

---

## 7. Qué NO se hace

- **No se toca `motor.py` ni el 4.6.0.** El campeón sigue sellando en
  producción durante toda la etapa. Sin excepciones.
- **No se reescribe ninguna fila sellada.** Si algo de esta medición revela un
  error histórico, se documenta como errata.
- **No se mueve el umbral de régimen del campeón.** Es lógica de señal.
- **No se ejecuta el backtest con veredicto por ansiedad.** El gatillo de la
  5.1 sigue siendo N ≥ 150 **y** un cambio de régimen, o 3 meses. N ya va en
  228; el cambio de régimen **no ha ocurrido** — y ahora sabemos que la
  etiqueta no podría detectarlo aunque ocurriera (§2.7). Esa contradicción se
  resuelve en el diseño del retador, no adelantando el veredicto.
- **No se cuentan los intentos a conveniencia.** Cada configuración evaluada
  entra en el DSR.

---

## 8. Riesgos declarados, antes de empezar

1. **n=228 es chico, y n=228 en un solo régimen es más chico todavía.** Toda
   la inferencia de la §5 cuantifica esa incertidumbre; ninguna la elimina.
2. **Sesgo de especificación irreducible.** Estas features las diseña alguien
   que ya vio esta ventana. La única defensa real es el sellado en vivo sobre
   datos que no existían — que el proyecto sí tiene y hay que seguir usando.
3. **Más parámetros, mismo dato.** Jerárquico + Kalman + Markov es mucha
   maquinaria sobre 228 observaciones. Por eso el control lineal de la §4.3 no
   es opcional: es el juez.
4. **La abstención regala aciertos.** El acta ya lo anotó para la regla de
   timing: el 03-ago habría abstenido 3 aciertos direccionales. Lo mismo vale
   acá. El costo se acepta explícitamente.
5. **Datos gratuitos.** Yahoo revisa la historia en silencio. Un proveedor con
   datos point-in-time es un requisito para cualquier conclusión fuerte, y hoy
   no lo hay.

---

## 9. Lo primero que hay que hacer

**Reproducir la §2 dentro del harness de `backtest/`.** Esas cifras salieron
de un análisis externo sobre los CSV de respaldo. Si el harness las reproduce,
quedan como línea base oficial y este documento se ratifica. Si no, manda el
harness y esto se corrige antes de escribir una línea del retador.

Ninguna otra cosa empieza antes que eso.
