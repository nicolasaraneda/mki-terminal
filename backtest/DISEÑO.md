# Diseño del motor de backtest B0→B5 (Etapa 5.0 — GATE B)

**Estado: CONGELADO — aprobado en el GATE B (25-jul-2026) con tres ajustes
del usuario incorporados: veredicto escalonado por capa, benchmark SMH
obligatorio y gatillo de la Etapa 5.1 fijado.** La ejecución con veredicto
queda EXPLÍCITAMENTE diferida a la Etapa 5.1 (decisión humana).

## 1. La pregunta científica

¿La cadena de señales del MKI (contagio del SOX → betas → noticias →
cadena de valor) agrega poder predictivo REAL sobre los gaps de apertura y
retornos de sesión de las acciones no-estadounidenses del universo,
comparada con alternativas ingenuas — y sobrevive ese valor a los costos
de transacción?

El track record en vivo (N=80 al 25-jul, gap 78.5%, un solo régimen de
mercado observado) no puede responder esto solo: puede ser señal o puede
ser momentum del período. El backtest walk-forward responde con historia
más larga y con CONTROLES (los baselines B0–B5), cada uno aislando la
contribución marginal de una familia de información.

## 2. Objetivo de predicción (idéntico al experimento en vivo)

Para cada acción de `MERCADOS_POR_ABRIR` (universo.py; los ADR
`duplicado_de` excluidos) y cada emisión:

- **gap** = open(sesión objetivo) / close(sesión local anterior) − 1
  → ¿la señal EXISTE?
- **retorno de sesión** = close(obj) / close(ant) − 1 → la métrica del
  experimento en vivo (comparabilidad).
- **retorno CAPTURABLE** = close(obj) / open(obj) − 1 → **la única
  operación físicamente posible**: la emisión ocurre a las 22:15 UTC,
  cuando el cierre local anterior YA pasó — nadie puede comprar a ese
  precio. La cartera simulada entra en la subasta de APERTURA de la
  sesión objetivo y sale en la de cierre. El gap mide calidad de señal;
  el capturable mide dinero. Confundirlos es el error clásico de los
  backtests de gaps, y este diseño los separa desde la definición.

## 3. Los seis baselines (qué pregunta responde cada uno)

| # | Modelo | Predicción emitida | Pregunta que aísla |
|---|--------|--------------------|--------------------|
| B0 | Cartera equiponderada / señal nula | est = 0 para todos (cartera: long igual-peso siempre) | ¿El período regaló retornos? Piso de MAE (predecir 0) y benchmark de cartera "no hacer nada inteligente" |
| B1 | Momentum propio 20d | est = signo·escala del momentum 20d de la propia acción (parámetro de escala ajustado SOLO en ventana de entrenamiento) | ¿Basta la inercia propia, sin mirar el SOX? |
| B2 | Contagio SOX(t−1) — **el modelo de producción v4.6.0, congelado** | `motor.prediccion_apertura_al(D)`: beta rodante 120d sobre el último movimiento real del SOX, con su intervalo 80% | ¿El contagio agrega sobre B0/B1? Es EXACTAMENTE lo que corre en vivo — el backtest lo audita, no lo reinventa |
| B3 | Cuant sin noticias | Regresión lineal walk-forward sobre features de precio: beta·SOX(t−1), momentum 20d propio, momentum del índice local, régimen del SOX (dummy), z de divergencia residualizada del par | ¿Combinar las señales de PRECIO mejora al contagio solo? |
| B4 | B3 + eventos de noticias | + sentimiento por acción y por sector (con decaimiento 0.7^días y relevancia, como producción), + buzz | ¿Las noticias agregan algo que el precio no traía ya? |
| B5 | B4 + cadena de valor | + Roca→Chip (percentil), + momentum 20d de los eslabones aguas arriba de cada acción | ¿La tesis central del producto (roca→chip anticipa) agrega valor marginal medible? |

La escalera es acumulativa a propósito: la diferencia Bk − Bk−1 es la
contribución marginal de UNA familia de información. B2 no se re-ajusta ni
se "mejora": es la auditoría del modelo congelado 4.6.0.

## 4. Reloj de emisión y calendarios (la regla maestra, simulada)

- **Emisión simulada**: cada día hábil de Chile a las **22:15 UTC**
  (18:15 Chile, hora del job real de producción). Toda feature usa
  exclusivamente datos con fecha ≤ D (el día de emisión).
- **Sesión objetivo**: `calendarios.proxima_sesion_despues_de(exchange,
  emisión)` — la misma función del sistema en vivo, con feriados reales
  de cada bolsa (exchange-calendars). El cruce de fecha (Seúl abre
  domingo 00:00 UTC) queda cubierto por construcción.
- **available_at**: cierre UTC de la sesión XNYS cuyo SOX alimenta la
  predicción — cota inferior de conocibilidad, igual que en producción.
- **Verificación**: solo se evalúan emisiones cuya apertura objetivo es
  ESTRICTAMENTE posterior a la emisión (la regla maestra, aplicada por el
  propio framework). Sesiones sin datos en la fuente → descartadas y
  CONTADAS (como el estado sin_datos_mercado en vivo), jamás rellenadas.

## 5. Datos point-in-time (y sus límites, con nombre)

| Insumo | Fuente point-in-time | Grado |
|---|---|---|
| Precios (features y outcomes) | `motor._datos_crudos` + recorte `≤ D` — el MISMO punto único y la MISMA garantía que audita `tests/test_motor.py` | A |
| Régimen, betas, divergencias, cadena | funciones `*_al(D)` del motor congelado | A |
| Predicciones B2 desde el 05-jul-2026 | filas SELLADAS de senales.db (timestamp real de emisión) — el backtest debe REPRODUCIRLAS; si difiere, el bug es del backtest | A |
| Sentimiento desde el 05-jul-2026 | `sentimiento_ia` sellado por día en senales_ticker | A |
| Sentimiento anterior al 05-jul | noticias.db: solo titulares con fecha de publicación < emisión; PERO el análisis de IA se hizo DESPUÉS (analizado_en posterior) | **B — se declara** |
| Universo | universo.py actual aplicado hacia atrás | **B — sesgo de selección/supervivencia declarado**: el universo es el mapa de la cadena de valor (no se eligió por rendimiento), pero se fijó en 2026 sabiendo quiénes son los grandes |

Reglas de honestidad derivadas:
1. Toda salida del backtest etiqueta su período: **"grado A"** (todo
   insumo point-in-time verificable) vs **"grado B"** (algún insumo
   reconstruido). B4/B5 antes del 05-jul son grado B por el sentimiento.
2. Los precios de Yahoo son ajustados (auto_adjust): dividendos pasados
   reescriben opens/closes históricos. Gap y capturable usan open y close
   de la MISMA serie ajustada (consistentes entre sí); el sesgo residual
   se declara en el reporte de cada corrida.
3. El dry-run de humo sobre datos legacy se marca **NO-CONCLUYENTE** en
   TODA salida (archivo y consola), sin excepción.

## 6. Ventanas walk-forward

- **Profundidad total**: 3 años de datos (ANIOS_DATOS del motor).
- **Burn-in**: 250 sesiones (betas 120d + margen) — jamás se evalúa sobre
  el burn-in.
- **B2**: ventana rodante de 120 sesiones hábiles, re-estimada en CADA
  emisión (idéntico a producción; no hay nada que "entrenar").
- **B1, B3–B5**: entrenamiento rodante de **250 sesiones**, re-ajuste
  **semanal** (cada 5 emisiones; el costo computacional no justifica
  re-ajuste diario y el re-ajuste infrecuente REDUCE el riesgo de
  sobreajuste). El modelo entrenado en [D−250, D) emite para D en
  adelante. Sin túnel de hiperparámetros: coeficientes por mínimos
  cuadrados, sin regularización que exija tuning; los parámetros fijos
  (ventanas, decaimiento 0.7, umbrales de régimen) son los de producción
  y quedan CONGELADOS EN ESTE DOCUMENTO antes de ver un solo resultado.
- **Evaluación**: ~2 años de emisiones fuera de burn-in (≈500 por
  exchange × 12 acciones ≈ 5.000–6.000 pares emisión-outcome).

## 7. De la señal a la cartera (para Sharpe/MDD/turnover)

- **Construcción**: por emisión, ranking por estimado. Dos carteras por
  baseline: (a) **long-only top-3** igual peso; (b) **long-short**
  terciles extremos (long top-⅓, short bottom-⅓, igual peso, neutral en
  neto). Sin apalancamiento, sin piramidación, capital 1.0.
- **Ejecución**: entrada en la subasta de apertura de la sesión objetivo,
  salida en la de cierre (retorno capturable). Sin posiciones nocturnas:
  el sistema predice la apertura, no gestiona un portafolio.
- **Benchmark de referencia obligatorio (ajuste GATE B): buy-and-hold de
  SMH** (el BENCHMARK del universo, fuera de la cadena) sobre el mismo
  período de evaluación. TODA tabla y TODO gráfico de resultados de
  cartera lo incluye — la pregunta "¿le gana a comprar SMH y no hacer
  nada?" tiene respuesta explícita en cada corrida (retorno acumulado,
  Sharpe y MDD de SMH junto a los de cada baseline).
- **Costos (ida), caso base 25 pb por lado = 50 pb ida y vuelta**, con
  sensibilidad obligatoria a 10/25/50 pb. Fuente de la suposición:
  impuestos de transacción oficiales (Corea 0.18% a la venta desde 2024
  —FSC—; Taiwán 0.30% a la venta —Ministry of Finance—; Japón sin
  impuesto), spread mediano de large caps (1–5 pb) y comisión retail.
  25 pb por lado es deliberadamente conservador para Japón/Europa y
  apenas suficiente para las ventas en Corea/Taiwán del lado short: por
  eso el reporte muestra las TRES sensibilidades y desglosa por mercado.
  Una estrategia que solo vive con 10 pb no aprueba.

## 8. Métricas (fijadas aquí, antes de correr — sin p-hacking)

Por baseline y por período (total, por régimen del SOX, por región):

1. **Rank IC** (Spearman estimado vs gap real) por emisión; media,
   desviación, t-stat con corrección Newey-West (lag 5).
2. **Hit rate condicionado**: global y condicionado a |estimado| > 0.5%
   y > 1.0%, y por tramo de R² histórico (los cortes 0.10/0.25 de
   producción) — cada celda con su intervalo de Wilson 95%.
3. **MAE del gap** (pp) — el piso a batir es el MAE de B0 (predecir 0).
4. **Calibración**: cobertura empírica del intervalo 80% (B2+) y curva
   nominal vs real (la misma re-escala del sigma que usa /historial).
5. **Sharpe neto de costos** (retornos diarios de cartera, anualizado
   √252), con intervalo por block-bootstrap (bloques de 10 días, 2.000
   réplicas).
6. **Max drawdown** y **turnover** promedio diario.
7. **Conteo de descartes**: emisiones sin datos de outcome (el
   sin_datos_mercado del backtest) — se reportan, no se esconden.

**Criterio de lectura (pre-registrado, ajustado en el GATE B)** — en dos
niveles, ambos obligatorios en el reporte:

1. **Veredicto ESCALONADO por capa**: cada bloque se compara contra el
   anterior — B1 vs B0, B2 vs B1, B3 vs B2, B4 vs B3, B5 vs B4 — con el
   MISMO estándar: diferencia de rank IC medio evaluada sobre las series
   diarias emparejadas (test t de las diferencias con corrección
   Newey-West lag 5). Una capa "aporta" si su delta de IC es positivo con
   t > 2. El resultado es un mapa exacto de QUÉ capa agrega información y
   cuál es peso muerto — no un veredicto binario global.
2. **Veredicto final**: la cadena MKI "agrega valor" si B5 (o B4) supera
   a B1 Y a B2 en rank IC con t-stat > 2, Y el Sharpe neto a 25 pb de la
   long-short es positivo con su intervalo bootstrap sobre cero, Y el
   retorno neto acumulado supera al buy-and-hold de SMH del mismo
   período (con la comparación de Sharpe y MDD al lado, porque batir a
   SMH con el triple de drawdown no es la misma victoria).

Cualquier otro resultado se publica igual, con el mismo nivel de detalle.

## 9. Arquitectura del módulo (SOLO LECTURA)

```
backtest/
  DISEÑO.md          ← este documento
  datos.py           capa point-in-time: precios/regimen/divergencias vía
                     motor (*_al), sentimiento vía senales.db sellada o
                     noticias.db con corte por fecha de publicación
  emision.py         el reloj: emisiones 22:15 UTC hábiles, sesión objetivo
                     y available_at por exchange (calendarios.py)
  baselines.py       B0..B5 — cada uno una función predecir(D) → DataFrame
                     [ticker, estimado_pct, intervalo80_pp?, grado A/B]
  cartera.py         señal → posiciones → retornos capturables netos
  metricas.py        IC, hit condicionado, MAE, calibración, Sharpe, MDD,
                     turnover, Wilson, bootstrap
  motorbt.py         loop walk-forward; único punto de entrada
  resultados/        salidas por corrida (id = timestamp + git hash):
                     resumen.md versionable + parquet/CSV gitignorados
```

- **Jamás escribe** en senales.db / noticias.db / alertas.db (conexiones
  sqlite abiertas en modo solo-lectura, `file:...?mode=ro`).
- No toca motor.py: lo IMPORTA, como el resto del sistema.
- Determinista: mismo commit + mismos datos → mismos resultados (semilla
  fija para el bootstrap).

## 10. Cómo cada decisión evita el look-ahead (mapa)

| Decisión | Garantía |
|---|---|
| Features solo ≤ D | Todo dato pasa por `_datos_crudos` + recorte, la vía ya auditada por tests/test_motor.py |
| Emisión 22:15 UTC | Reloj fijo anterior a toda apertura objetivo; el framework RECHAZA evaluar si apertura ≤ emisión (regla maestra) |
| Sesión objetivo | calendarios.py con feriados reales; nunca "el día siguiente" ingenuo |
| Noticias | Solo titulares publicados antes de la emisión; sentimiento sellado desde 05-jul; lo anterior degrada el resultado a grado B visible |
| Entrenamiento B3–B5 | Ajuste exclusivamente en [D−250, D); el modelo vigente para D se congeló antes de conocer D |
| Hiperparámetros | Congelados en este documento, antes del primer resultado |
| Test del framework | `tests/test_backtest.py` INYECTA un dato futuro en la capa de datos y verifica que el framework lo rechaza (excepción), y verifica que truncar el futuro no cambia ninguna predicción emitida |
| Universo | Sesgo de selección declarado en toda salida (no corregible, sí nombrable) |

## 11. Qué NO decide este backtest

- No sube MODELO_VERSION ni toca el motor: si B3–B5 ganan, eso alimenta
  la DECISIÓN HUMANA de una futura v5 del modelo (etapa aparte, con su
  propio track record desde cero).
- No opera dinero. No genera órdenes. El disclaimer va en cada salida.
- El dry-run de la Etapa 5.0 solo prueba que la maquinaria funciona
  (humo, NO-CONCLUYENTE); el veredicto es de la Etapa 5.1.
- **Gatillo de la Etapa 5.1 (CONGELADO en el GATE B, 25-jul-2026)**: el
  backtest queda habilitado para ejecutarse con veredicto cuando ocurra
  lo primero de:
  (a) **N ≥ 150 verificaciones limpias en vivo Y al menos un cambio de
  régimen del SOX observado** durante el track record, o
  (b) **3 meses de operación continua** del sistema autónomo
  (desde el 25-jul-2026 → 25-oct-2026).
  Cumplido el gatillo, la ejecución sigue siendo una **decisión humana
  del usuario** — el sistema jamás la dispara solo. La vista /laboratorio
  muestra el progreso hacia ambas condiciones.
