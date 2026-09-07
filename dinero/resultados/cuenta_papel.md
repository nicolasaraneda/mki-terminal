# Cuenta en papel del riel de dinero — **SIMULADO**

> **SIMULADO. PROPUESTA.** Ninguna cifra de este documento es un
> resultado del proyecto, ninguna entra al README, y ninguna pasó
> todavía por `estadistico-adversario`. No hay cuenta de corredora y
> no se envió ninguna orden a ningún lado.
>
> **Lo que esta cuenta mide es FRICCIÓN, no habilidad.** La estrategia
> se alimenta de una señal SIN INFORMACIÓN —sorteada de la distribución
> histórica de retornos a 20 días hábiles de cada instrumento, con
> semilla 20260906, sin relación con lo que
> pasa después—, justamente para que lo que se lea acá sea lo que le
> cuesta a cada juego de parámetros existir. Una estrategia con señal
> de verdad tendría que superar esto ANTES de poder llamarse habilidad.

Generado por `python -m dinero.cuenta_papel` el 2026-09-07 UTC.

## Parámetros congelados antes de correr

- Ventana: **2023-09-05 a 2026-09-04** (754 días de mercado), sobre `dinero/datos/cierres_congelados.csv`. **Sin descargas.**
- Aporte: **100 USD el primer día hábil de cada semana, hasta agotar el techo de 500 USD**. Total aportado: **500 USD** en 5 aportes.
  El encargo pide 'un monto fijo cada semana', pero el presupuesto
  declarado son 100 a 500 dólares **en total**: aportar semanalmente
  durante tres años serían 15.600 dólares que no existen. El calendario
  se corta al agotar el presupuesto, y la línea base y la estrategia
  reciben **el mismo flujo de caja**, que es lo que las hace comparables.
- Universo operable: 29 instrumentos (los verificados y comprables de `docs/universo_operable.md`).
- Barrido de costo: deslizamiento de [0.0, 2.0, 5.0, 10.0] pb por lado, **más** la
  comisión fija del supuesto (mínimo 1 USD por orden, tope 1 %).

## 4a. La línea base aburrida

Comprar un ETF del sector con el aporte semanal, sin decidir nada. Si el
aporte no alcanza para una acción entera, **acumula**: es lo que haría
una persona con 100 dólares por semana frente a un ETF de más de 500.

| ETF | Deslizamiento | Órdenes | Comisiones USD | Final USD | Resultado USD | Resultado % |
|---|---:|---:|---:|---:|---:|---:|
| `SMH` | 0 pb | 3 | 3.00 | 1759.98 | +1259.98 | +252.00 % |
| `SMH` | 2 pb | 3 | 3.00 | 1759.89 | +1259.89 | +251.98 % |
| `SMH` | 5 pb | 3 | 3.00 | 1759.76 | +1259.76 | +251.95 % |
| `SMH` | 10 pb | 3 | 3.00 | 1759.54 | +1259.54 | +251.91 % |
| `XSD` | 0 pb | 2 | 2.00 | 1089.62 | +589.62 | +117.92 % |
| `XSD` | 2 pb | 2 | 2.00 | 1089.55 | +589.55 | +117.91 % |
| `XSD` | 5 pb | 2 | 2.00 | 1089.43 | +589.43 | +117.89 % |
| `XSD` | 10 pb | 2 | 2.00 | 1090.05 | +590.05 | +118.01 % |

**Por qué hay dos ETF y no uno.** `SMH` es el BENCHMARK declarado del
riel de medición (`universo.py`), y por eso está. Pero su acción cerró
por encima del techo del presupuesto el 2026-09-04, así que la línea base
con `SMH` pasa semanas acumulando antes de poder comprar la primera. `XSD`
es el único ETF sectorial verificado cuya acción cabe en 500 dólares. La
diferencia entre las dos filas **no es una diferencia de mercado: es el
costo de no poder comprar fracciones**.

## 4b/4c. Los tres juegos, contra la línea base

Los tres estaban declarados y congelados en `dinero/reglas.json` antes de
esta corrida, con su regla de derivación. Se muestran **los tres, sin
ranking y sin recomendación**: elegir uno mirando esta tabla sería elegir
la vara después de ver el tiro. El que rige por defecto lo fija una regla
escrita —el conservador—, no su resultado.

### Deslizamiento 0 pb por lado

| Juego | Órdenes | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| conservador | 227 | 125.86 | 0.00 | 1298.77 | +159.75 % | -0.190 | [-0.581, +0.188] | +0.108 | [-0.353, +0.527] |
| medio | 255 | 154.89 | 0.00 | 1183.99 | +136.80 % | -0.211 | [-0.651, +0.245] | +0.088 | [-0.397, +0.555] |
| agresivo | 355 | 214.84 | 0.00 | 693.71 | +38.74 % | -0.613 | [-1.172, -0.093] ✓ | -0.314 | [-0.999, +0.302] |

### Deslizamiento 2 pb por lado

| Juego | Órdenes | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| conservador | 227 | 125.86 | 2.79 | 1295.97 | +159.19 % | -0.191 | [-0.581, +0.187] | +0.108 | [-0.353, +0.527] |
| medio | 252 | 149.98 | 3.35 | 1355.78 | +171.16 % | -0.097 | [-0.643, +0.479] | +0.202 | [-0.321, +0.756] |
| agresivo | 358 | 214.88 | 7.30 | 680.48 | +36.10 % | -0.626 | [-1.182, -0.104] ✓ | -0.327 | [-1.000, +0.284] |

### Deslizamiento 5 pb por lado

| Juego | Órdenes | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| conservador | 227 | 125.87 | 6.99 | 1291.78 | +158.36 % | -0.193 | [-0.583, +0.186] | +0.106 | [-0.352, +0.525] |
| medio | 220 | 133.78 | 7.49 | 1769.07 | +253.81 % | +0.131 | [-0.464, +0.784] | +0.430 | [-0.167, +1.098] |
| agresivo | 357 | 214.87 | 18.26 | 669.45 | +33.89 % | -0.635 | [-1.189, -0.114] ✓ | -0.336 | [-1.008, +0.274] |

### Deslizamiento 10 pb por lado

| Juego | Órdenes | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| conservador | 133 | 69.62 | 7.25 | 2286.75 | +357.35 % | +0.271 | [-0.270, +0.833] | +0.568 | [+0.049, +1.156] ✓ |
| medio | 221 | 133.65 | 14.92 | 1754.18 | +250.84 % | +0.092 | [-0.444, +0.675] | +0.389 | [-0.178, +1.003] |
| agresivo | 357 | 214.87 | 36.51 | 651.19 | +30.24 % | -0.652 | [-1.203, -0.134] ✓ | -0.355 | [-1.028, +0.250] |

Los intervalos son **bootstrap circular de bloques sobre SEMANAS** (bloque de 4 semanas, 2000 réplicas, semilla 20260906, α = 0.05), con `backtest.inferencia.bootstrap_media`, que es el
intervalo de la MEDIA y por lo tanto está en la misma escala que el punto
estimado —la corrida 09 documentó qué pasa cuando no lo está—. La unidad
es la semana y no el día porque dos carteras que comparten instrumentos
tienen retornos diarios correlacionados, y contarlos como independientes
angostaría el intervalo sin fundamento. Un `✓` marca un intervalo que **no**
contiene el cero; sin `✓`, la diferencia **no se distingue de cero**.

## Qué de esto es un hallazgo y qué no

### 1. La comisión se come el capital. Esto SÍ es robusto.

| Juego | Órdenes (rango del barrido) | Comisiones USD | Como fracción de los 500 USD aportados |
|---|---:|---:|---:|
| conservador | 133–227 | 69.62–125.87 | **14 % – 25 %** |
| medio | 220–255 | 133.65–154.89 | **27 % – 31 %** |
| agresivo | 355–358 | 214.84–214.88 | **43 % – 43 %** |
| línea base `SMH` | 3–3 | 3.00–3.00 | 0.6 % – 0.6 % |
| línea base `XSD` | 2–2 | 2.00–2.00 | 0.4 % – 0.4 % |

Con un mínimo de 1 USD por orden y 500 dólares de capital, **rotar la
cartera cuesta entre una cuarta parte y casi la mitad del capital en
comisiones**, contra menos del uno por ciento de no decidir nada. Este
número no depende del sorteo ni del deslizamiento: depende sólo de
cuántas órdenes emite cada juego, y por eso es lo único de esta página
que se sostiene solo.

### 2. El barrido de deslizamiento NO es una curva de sensibilidad al costo.

- `conservador`: de **+158 %** a 5 pb hasta **+357 %** a 10 pb — 199 puntos porcentuales de diferencia, y órdenes 227 contra 133.
- `medio`: de **+137 %** a 0 pb hasta **+254 %** a 5 pb — 117 puntos porcentuales de diferencia, y órdenes 255 contra 220.
- `agresivo`: de **+30 %** a 10 pb hasta **+39 %** a 0 pb — 9 puntos porcentuales de diferencia, y órdenes 357 contra 355.

Diez puntos básicos por lado no pueden mover un resultado cientos de
puntos porcentuales. Lo que pasa es otra cosa, y hay que decirla: **el
deslizamiento cambia cuántas acciones enteras entran en el margen, y eso
cambia QUÉ instrumento se compra**. Con acciones enteras, 500 dólares y
una señal sin información, el resultado lo decide cuál de los
29 instrumentos tocó en el sorteo, no el costo. Las
filas del barrido **no son la misma estrategia a distinto costo: son
caminos distintos**, y compararlas entre sí sería un error.

### 3. Los `✓` de la tabla son falsos positivos POR CONSTRUCCIÓN.

De **24** comparaciones, **5** tienen un intervalo del 95 %
que excluye el cero: 21 %. Bajo una señal sin
información, la respuesta verdadera es cero en las 24, así que **todos**
esos intervalos son falsos positivos. No es un defecto del bootstrap: las
comparaciones comparten el sorteo, los instrumentos y el flujo de caja, y
nada de eso está descontado. El número sirve para una sola cosa, y es
útil: **así de fácil es que este diseño produzca un `✓` sin que haya nada**.
Cuando exista una señal de verdad, este es el ruido contra el que va a
tener que destacarse.

### 4. Lo único direccional que sí se sostiene

El juego **agresivo pierde contra la línea base `SMH` en 4 de las 4 pasadas del barrido**, con el intervalo
entero por debajo del cero. Es el único resultado consistente de la
página, y es el esperable: más órdenes sobre una señal sin información
es más comisión pagada por nada. **No hace falta una señal buena para
perder; alcanza con operar seguido.**

### 5. Lo que esta cuenta NO midió

- **Habilidad.** No hay señal. La primera señal larga es el bloque 6 y su
  resultado está en `GEMELO/preregistro/senal_larga_v1.md` y su reporte.
- **Impacto de mercado.** El deslizamiento es un supuesto lineal por lado,
  no un modelo de libro de órdenes. A 500 dólares es probablemente
  conservador; no se verificó.
- **Impuestos, retención de dividendos de ADR, ni costo de cambio de
  moneda.** Ninguno está en el modelo de costo.
- **Que los precios sean point-in-time.** Los cierres de la fuente vienen
  ajustados retroactivamente por splits y dividendos; la serie no es la
  que se veía ese día. Está declarado en el metadato del congelado.

