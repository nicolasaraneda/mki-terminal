# Cuenta en papel del riel de dinero — **SIMULADO** (v2, reconstruida sin fuga)

> **SIMULADO. PROPUESTA hasta el dictamen del `estadistico-adversario` y del
> `auditor-lookahead`.** Ninguna cifra de este documento es un resultado del
> proyecto, ninguna entra al README. No hay cuenta de corredora y no se envió
> ninguna orden a ningún lado. Cero filas selladas de este riel.
>
> **Lo que esta cuenta mide es FRICCIÓN, no habilidad.** La estrategia se
> alimenta de una señal SIN INFORMACIÓN, sorteada de la distribución de
> retornos a 20 días hábiles de cada instrumento medida
> con datos **anteriores a 2023-09-05** (semilla 20260906),
> justamente para que lo que se lea acá sea lo que le cuesta a cada juego de
> parámetros existir. Una estrategia con señal de verdad tendría que superar
> esto ANTES de poder llamarse habilidad.
>
> **Versión 2, reconstruida el 8-sep-2026 (corrida 11, acta §82.4).** La v1
> del 7-sep está RETIRADA por cuatro fugas temporales demostradas (F1 a F4,
> `GEMELO/resultados/dictamen_10/auditor_lookahead.md`). Ninguna cifra de la v1
> se cita ni se compara acá. Las correcciones, en el orden que fijó el auditor:
> E1 membresía decidida con los cierres hasta 2023-09-05; E3 señal sorteada de
> datos anteriores a 2023-09-05; E4 retardo de implementación de
> 1 sesión en las DOS patas; E5 sigma del interruptor
> medida hasta 2023-09-05; E6 gate de invariancia al truncado cableado y corrido
> antes de escribir esta página.
> **Gate de invariancia:** INVARIANTE en 25 cortes por regla (una sesión de cada 30; 56266 movimientos y 56461 decisiones comparadas). **Alcance:** invariancia al truncado en 25 cortes por regla (una sesión de cada 30). Una fuga de k días sólo deja huella en los k días previos a cada corte: el poder contra fugas cortas es la probabilidad de que en esos días haya una decisión distinta. Medido por el auditor (corrida 11): una fuga de 1 día por precios_ref la veían 2 de 11 cortes. INVARIANTE no significa ausencia de fuga: significa que ninguna entró por las vías que estos cortes ven. La contraprueba de precios_ref (G3) está pendiente para la corrida 12.

Generado por `python -m dinero.cuenta_papel` el 2026-09-08 UTC.

## Parámetros congelados antes de correr

- Ventana: **2023-09-05 a 2026-09-04** (754 días de mercado), sobre `dinero/datos/cierres_congelados.csv`. **Sin descargas.**
- Aporte: **100 USD el primer día hábil de cada semana, hasta agotar el techo de 500 USD**. Total aportado: **500 USD** en 5 aportes. Es el flujo IMPLEMENTADO (errata §6 C del
  pre-registro: rige lo implementado). La línea base y la estrategia reciben
  **el mismo flujo de caja**, que es lo que las hace comparables.
- Universo operable: **33 instrumentos**, los verificados y
  comprables con 500 USD **al 2023-09-05** (E1): `AMAT`, `AMD`, `AMKR`, `AMZN`, `ASX`, `AVGO`, `CDNS`, `ENTG`, `GFS`, `GOOGL`, `GSM`, `INTC`, `KLAC`, `LIN`, `LRCX`, `META`, `MKSI`, `MSFT`, `MU`, `NVDA`, `QCOM`, `SHECY`, `SMH`, `SNPS`, `SOXX`, `TER`, `TOELY`, `TSEM`, `TSM`, `UMC`, `VRT`, `WDC`, `XSD`.
- **Parámetro de costo: el arancel publicado del insumo del §40** (`GEMELO/propuestas/insumo_40_aranceles_*.md`, arancel Pro Tiered del corredor del §40, consultado el
  7-sep-2026), **columna de acciones ENTERAS**: 0.0035 USD por
  acción, mínimo 0.35 USD por orden, tope 1.0 % del monto. La columna de fraccionarias
  (1 % del monto, mínimo 0,01) NO aplica: esta cuenta compra acciones enteras.
  Las tarifas de terceros (SEC, FINRA, compensación) no están en el modelo:
  a estos tamaños suman centavos y el insumo lo declara.
- Barrido de deslizamiento: [0.0, 2.0, 5.0, 10.0] pb por lado, **además** de la comisión.
- Retardo de implementación: **1 sesión** en las dos patas. Se decide con el cierre de d y se ejecuta contra el cierre de d+1; si a ese
  precio la caja no alcanza, la orden se reduce y queda contada en la columna
  «reducidas». Con retardo 1 no hay caja comprometida al decidir (lo pendiente se
  ejecuta antes de decidir el mismo día): el descuento existe en el código sólo para
  retardo > 1, y las dos patas usan la misma convención (n × precio de decisión).
- **La sonda es larga por construcción** (exigencia G5 del auditor): 57.8 % de las 24882 señales son positivas y la magnitud media es +2.20 pp, porque
  hereda la deriva anterior a 2023-09-05. Sin información sobre la dirección no es lo mismo que sin
  sesgo: lo medido es la fricción de un comprador aleatorio sesgado a largo en un mercado que subió.
- **La membresía es un corte transversal fijo al 2023-09-05**, ni futuro ni point-in-time (exigencia G6): excluye `ASML` (precio al 2023-09-05 por encima del techo), `SNDK` (sin cierre anterior a 2023-09-05 (listada después)), `ARM` (sin cierre anterior a 2023-09-05 (listada después)). Los excluidos
  rindieron en la ventana una mediana de +296.4 % contra +166.1 % de los incluidos: el sesgo va EN CONTRA de la cuenta.
  Un inversor real podía comprar las listadas después desde su listado; acá quedan vetadas tres años.
- Existe un segundo congelado (`dinero/datos/cierres_congelados_dia2.csv`, 8-sep 04:21 UTC, mismo rango):
  la cuenta recorrida contra él es bit a bit idéntica (diferencia relativa máxima 8,4e-7 en los
  precios). Es evidencia contra revisión silenciosa de la fuente en 26 horas, no en años.

## 4a. La línea base aburrida

Comprar un ETF del sector con el aporte semanal, sin decidir nada. Si el
aporte no alcanza para una acción entera, **acumula**.

| ETF | Deslizamiento | Órdenes | Comisiones USD | Final USD | Resultado USD | Resultado % |
|---|---:|---:|---:|---:|---:|---:|
| `SMH` | 0 pb | 3 | 1.05 | 1767.50 | +1267.50 | +253.50 % |
| `SMH` | 2 pb | 3 | 1.05 | 1767.42 | +1267.42 | +253.48 % |
| `SMH` | 5 pb | 3 | 1.05 | 1767.29 | +1267.29 | +253.46 % |
| `SMH` | 10 pb | 3 | 1.05 | 1767.07 | +1267.07 | +253.41 % |
| `XSD` | 0 pb | 2 | 0.70 | 1094.62 | +594.62 | +118.92 % |
| `XSD` | 2 pb | 2 | 0.70 | 1094.54 | +594.54 | +118.91 % |
| `XSD` | 5 pb | 2 | 0.70 | 1094.42 | +594.42 | +118.88 % |
| `XSD` | 10 pb | 2 | 0.70 | 1094.23 | +594.23 | +118.85 % |

`SMH` es el BENCHMARK declarado del riel de medición y por eso está; `XSD` es
el ETF sectorial cuya acción cabe en el presupuesto. La diferencia entre las
dos filas **no es una diferencia de mercado: es el costo de no poder comprar
fracciones**.

## 4b/4c. Los tres juegos, contra la línea base

Los tres estaban declarados y congelados en `dinero/reglas.json` antes de la
primera corrida, con su regla de derivación. Se muestran **los tres, sin ranking
y sin recomendación**. El que rige por defecto lo fija una regla escrita —el
conservador—, no su resultado.

### Deslizamiento 0 pb por lado

| Juego | Órdenes | Reducidas | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| conservador | 205 | 0 | 62.14 | 0.00 | 1294.33 | +158.87 % | -0.220 | [-0.632, +0.168] | +0.081 | [-0.471, +0.564] |
| medio | 447 | 1 | 138.34 | 0.00 | 1033.54 | +106.71 % | -0.342 | [-0.698, +0.024] | -0.040 | [-0.462, +0.342] |
| agresivo | 386 | 0 | 96.50 | 0.00 | 765.44 | +53.09 % | -0.583 | [-1.163, -0.013] ✓ | -0.281 | [-0.991, +0.358] |

### Deslizamiento 2 pb por lado

| Juego | Órdenes | Reducidas | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| conservador | 208 | 0 | 62.98 | 2.81 | 1290.20 | +158.04 % | -0.222 | [-0.632, +0.166] | +0.080 | [-0.470, +0.558] |
| medio | 443 | 0 | 137.63 | 6.90 | 938.72 | +87.74 % | -0.407 | [-0.832, -0.000] ✓ | -0.105 | [-0.683, +0.388] |
| agresivo | 386 | 0 | 96.50 | 7.35 | 758.09 | +51.62 % | -0.588 | [-1.169, -0.018] ✓ | -0.287 | [-0.998, +0.352] |

### Deslizamiento 5 pb por lado

| Juego | Órdenes | Reducidas | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| conservador | 202 | 0 | 62.50 | 6.87 | 1247.81 | +149.56 % | -0.236 | [-0.580, +0.100] | +0.065 | [-0.431, +0.500] |
| medio | 415 | 0 | 129.52 | 17.05 | 1220.42 | +144.08 % | -0.245 | [-0.653, +0.153] | +0.057 | [-0.439, +0.500] |
| agresivo | 391 | 0 | 97.84 | 18.37 | 741.07 | +48.21 % | -0.602 | [-1.184, -0.027] ✓ | -0.301 | [-1.002, +0.320] |

### Deslizamiento 10 pb por lado

| Juego | Órdenes | Reducidas | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| conservador | 205 | 0 | 63.08 | 13.73 | 1241.38 | +148.28 % | -0.239 | [-0.583, +0.099] | +0.063 | [-0.432, +0.497] |
| medio | 422 | 0 | 131.16 | 34.00 | 1040.08 | +108.02 % | -0.349 | [-0.790, +0.073] | -0.047 | [-0.597, +0.415] |
| agresivo | 393 | 0 | 97.58 | 36.72 | 717.92 | +43.58 % | -0.621 | [-1.199, -0.047] ✓ | -0.320 | [-1.027, +0.300] |

Los intervalos son **bootstrap circular de bloques sobre SEMANAS** (bloque de 4 semanas, 2000 réplicas, semilla 20260906, α = 0.05), con `backtest.inferencia.bootstrap_media`. Este instrumento fue
**puesto a prueba contra una verdad conocida** en el bloque 1 de la corrida 11
(`GEMELO/resultados/instrumento_dinero.md`): **discrimina** por el criterio pre-declarado y
**NO está calibrado a α = 0,05 en ninguno de los tres horizontes** (sub-cubre bajo la nula).
Al horizonte de ESTAS comparaciones (156 semanas) la cobertura medida es 0.936 [0.925, 0.946] y el tamaño bilateral 0.064 [0.054, 0.075]: el α real de un `✓` es ≈ 0.064, no 0,05.
Un `✓` marca un intervalo que **no** contiene el cero; sin `✓`, la diferencia **no se
distingue de cero**.

## Qué de esto es un hallazgo y qué no

### 1. Cuánto cuesta rotar, con el arancel publicado

| Juego | Órdenes (rango del barrido) | Comisiones USD | Como fracción de los 500 USD aportados |
|---|---:|---:|---:|
| conservador | 202–208 | 62.14–63.08 | **12.4 % – 12.6 %** |
| medio | 415–447 | 129.52–138.34 | **25.9 % – 27.7 %** |
| agresivo | 386–393 | 96.50–97.84 | **19.3 % – 19.6 %** |
| línea base `SMH` | 3–3 | 1.05–1.05 | 0.2 % – 0.2 % |
| línea base `XSD` | 2–2 | 0.70–0.70 | 0.1 % – 0.1 % |

**Esos rangos son el mínimo y el máximo sobre los cuatro niveles de deslizamiento
de UN solo sorteo de señal: no son intervalos y no se pueden leer como tales.**
Lo que sí se sostiene es la aritmética: con el arancel del §40 cada orden de acciones
enteras cuesta como máximo 0.35 USD, así que la fracción del capital que
se va en comisiones es, como COTA SUPERIOR, el número de órdenes por 0,35 sobre lo aportado;
el tope del 1 % del monto muerde en las órdenes de menos de 35 USD y deja la cifra real
por debajo de esa cota (exigencia C2: 205 × 0,35 / 500 = 14,4 % contra 12,4 % medido).
**La fricción la fija el número de órdenes del diseño, no el arancel**; la nota del §82.4
se lee después de esta tabla, no antes.

### 1b. Con 20 semillas del sorteo, y con intervalo (exigencia C1)

Deslizamiento 5 pb. Banda = percentiles 2,5 y 97,5 entre semillas.

| Juego | Comisiones % del aportado, mediana | banda entre semillas | mín–máx | Órdenes, mediana | banda |
|---|---:|---|---|---:|---|
| conservador | **12.4 %** | [6.35, 13.2] | 6.3–13.2 | 210 | [110.42, 220.53] |
| medio | **26.7 %** | [14.56, 28.7] | 14.1–29.4 | 436 | [236.97, 469.65] |
| agresivo | **19.0 %** | [17.98, 20.16] | 17.7–20.2 | 373 | [348.95, 401.0] |

Comparaciones cuyo IC excluye el cero: **51 de 480** (0.106, Wilson [0.082, 0.137]) sobre 20 semillas × 24; de ellas, 9 son `agresivo` perdiendo contra `SMH`. La fracción de IC que excluyen el cero NO es una tasa de falsos positivos (la nula no es cero: hay arrastre de comisión). Es cuánto produce este diseño con una señal sin información, con la misma semilla de bootstrap en las K×24.

### 2. El barrido de deslizamiento NO es una curva de sensibilidad al costo.

- `conservador`: de **+148 %** a 10 pb hasta **+159 %** a 0 pb — 11 puntos porcentuales de diferencia, y órdenes 205 contra 205.
- `medio`: de **+88 %** a 2 pb hasta **+144 %** a 5 pb — 56 puntos porcentuales de diferencia, y órdenes 443 contra 415.
- `agresivo`: de **+44 %** a 10 pb hasta **+53 %** a 0 pb — 10 puntos porcentuales de diferencia, y órdenes 393 contra 386.

Diez puntos básicos por lado no pueden mover un resultado decenas o cientos de
puntos porcentuales. **El deslizamiento cambia cuántas acciones enteras entran en
el margen, y eso cambia QUÉ instrumento se compra**: las filas del barrido no son
la misma estrategia a distinto costo, son caminos distintos.

### 3. Los `✓` de la tabla, y por qué no son una tasa de falsos positivos

De **24** comparaciones, **5** tienen un intervalo del 95 % que
excluye el cero. Eso NO es una tasa de falsos positivos, por las tres razones que
el adversario dejó escritas en el cierre de la corrida 10: la nula no es cero (el
arrastre de comisión garantiza una diferencia verdadera negativa); un intervalo
negativo que excluye el cero es el resultado VERDADERO de la fricción; y las
24 comparaciones comparten sorteo, calendario e instrumentos. Cuánto de fácil
es que este diseño produzca un `✓` sin que haya nada se mide con K semillas: **está
medido en §1b** (20 semillas × 24 comparaciones, con Wilson), y ni siquiera eso es una
tasa de falsos positivos porque la nula no es cero.

### 4. La σ de la diferencia semanal, con intervalo

Juego por defecto (`conservador`) contra `SMH` a 5 pb, 156 semanas: **σ = 2.336 pp/semana**, intervalo bootstrap de nominal 95 % [1.9952, 2.6686] (sd (ddof=1) de la diferencia semanal, IC por bootstrap circular de bloques de 4 semanas, 2000 réplicas, semilla 20260913). Es el parámetro que la tabla de potencia del
pre-registro (§2.1) necesitaba. **Ese intervalo NO es un 95 %:** el bloque 1 midió que el
bootstrap de bloques de una desviación cubre 0.850 a 156 semanas. El punto sirve de
insumo; el intervalo no, hasta que se calibre (decisión en `espera_firma.md` §50). La tabla
de potencia NO se recomputa acá: se recomputa con el simulador validado
(`GEMELO/simulador/instrumento_dinero.py`) y es un paso aparte.

### 5. Lo que esta cuenta NO midió

- **Habilidad.** No hay señal. La primera señal larga es el bloque 6 de la
  corrida 10 y su resultado está en `dinero/resultados/senal_larga_v1.md`.
- **Impacto de mercado.** El deslizamiento es un supuesto lineal por lado.
- **Impuestos, retención de dividendos de ADR, cambio de moneda, tarifas de
  terceros ni tarifas de bolsa por venue.** Ninguno está en el modelo de costo.
- **Que los precios sean point-in-time.** Los cierres vienen ajustados
  retroactivamente; está declarado en el metadato del congelado.
- **Supervivencia.** Los instrumentos son los que existen hoy.

