# Sonda del cierre — a qué hora existe el cierre de hoy en yfinance

- Generado: 2026-09-28T19:56:24+00:00 · fuente: `data/sonda_cierre.csv`
- Noches con sesión: **4** · noches en que estuvieron todos antes de la última sonda: **2** · hora (NY) a la que estuvieron todos: mediana **22:35**, máxima **23:35**
- Estatus: PROPUESTA: dato de la sonda, no decisión; la hora del timer la fija Nicolás por acta (§58)
- Observaciones descartadas por ser anteriores al cierre de su sesión: **36** (2026-09-28: 13:42). No dicen a qué hora apareció el cierre: yfinance etiqueta la barra intradía con la fecha del día, así que con el mercado abierto el «cierre de hoy» ya figura. Las filas siguen en el CSV.

## Por ticker (hora de Nueva York a la que apareció el cierre de la sesión)

| ticker | noches | con cierre | sin cierre hasta la última sonda | mínima | mediana | máxima |
|---|---|---|---|---|---|---|
| AMAT | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| AMD | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| AMKR | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| AMZN | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| ARM | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| ASML | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| ASX | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| AVGO | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| CDNS | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| ENTG | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| GFS | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| GOOGL | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| GSM | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| INTC | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| KLAC | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| LIN | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| LRCX | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| META | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| MKSI | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| MSFT | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| MU | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| NVDA | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| QCOM | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| SMH | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| SNDK | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| SNPS | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| SOXX | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| TER | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| TSEM | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| TSM | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| UMC | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| VRT | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| WDC | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| XSD | 4 | 3 | 1 | 21:35 | 21:35 | 21:35 |
| TOELY | 4 | 3 | 1 | 20:05 | 23:35 | 23:35 |
| SHECY | 4 | 4 | 0 | 20:05 | 20:05 | 20:05 |

## Por noche

| sesión | sondas | última sonda (NY) | con cierre | hora en que estuvieron todos | faltaron hasta la última sonda |
|---|---|---|---|---|---|
| 2026-09-21 | 8 | 23:35 | 36/36 | 23:35 | — |
| 2026-09-22 | 8 | 23:35 | 2/36 | — | AMAT, AMD, AMKR, AMZN, ARM, ASML, ASX, AVGO, CDNS, ENTG, GFS, GOOGL, GSM, INTC, KLAC, LIN, LRCX, META, MKSI, MSFT, MU, NVDA, QCOM, SMH, SNDK, SNPS, SOXX, TER, TSEM, TSM, UMC, VRT, WDC, XSD |
| 2026-09-23 | 8 | 23:35 | 35/36 | — | TOELY |
| 2026-09-24 | 8 | 23:35 | 36/36 | 21:35 | — |

Una noche sin «hora en que estuvieron todos» es una noche en que el sellador, a cualquiera de esas horas, habría sellado `insumo_incompleto` bajo la definición firmada (§57).
