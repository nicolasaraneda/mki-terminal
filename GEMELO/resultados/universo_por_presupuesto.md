# Universo operable por presupuesto, con acciones enteras

- Generado: 2026-09-19T20:30:33+00:00 · congelado `cierres_congelados.csv` hasta 2026-09-04 (sha256 `69ca7283ae18…`, 36 tickers) · juego `conservador` · K = 20 semillas · reglas 0.2.0-PROPUESTA
- **Estatus: PROPUESTA — insumo para la reevaluación del monto de E2 (acta §86.3); no fija ni recomienda ningún monto; hasta el dictamen del estadistico-adversario**
- **Cómo se lee:** las filas NO son pareadas ni anidadas: `universo_operable` depende del techo, así que a cada presupuesto la cuenta juega con otra membresía (columna «operables en DESDE») y, con la misma semilla, otro flujo de sorteos. La tabla no se lee en columna: comparar la fracción de congeladas entre presupuestos mezcla presupuesto, membresía y realización. Tres poblaciones y tres fechas por fila, separadas en la tabla.

- Reproducción determinista del artefacto de la corrida 12 (NO verificación independiente: misma función, mismas semillas, mismo congelado): a 500 USD `m2_periodo.json` dice 5 de 20 semillas congeladas; recomputado 5 de 20 → COINCIDE.

## A. Alcance con acciones enteras al último cierre congelado (36 verificados al 2026-09-04)

| Presupuesto | Alcanzan 1 acción entera | Cota superior nominal de posiciones (más baratas primero, sin comisión; regla que la cuenta no usa) | No alcanzan |
|---|---|---|---|
| 100 USD | **7 de 36** | 4 | AMAT, AMD, AMZN, ARM, ASML, AVGO, CDNS, ENTG, GOOGL, KLAC, LIN, LRCX, META, MKSI, MSFT, MU, NVDA, QCOM, SMH, SNDK, SNPS, SOXX, TER, TOELY, TSEM, TSM, VRT, WDC, XSD |
| 150 USD | **8 de 36** | 5 | AMAT, AMD, AMZN, ARM, ASML, AVGO, CDNS, GOOGL, KLAC, LIN, LRCX, META, MKSI, MSFT, MU, NVDA, QCOM, SMH, SNDK, SNPS, SOXX, TER, TOELY, TSEM, TSM, VRT, WDC, XSD |
| 200 USD | **11 de 36** | 6 | AMAT, AMD, AMZN, ARM, ASML, AVGO, CDNS, GOOGL, LIN, LRCX, META, MKSI, MSFT, MU, NVDA, SMH, SNDK, SNPS, SOXX, TER, TSEM, TSM, VRT, WDC, XSD |
| 250 USD | **13 de 36** | 6 | AMAT, AMD, AMZN, ARM, ASML, AVGO, CDNS, GOOGL, LIN, LRCX, META, MKSI, MSFT, MU, SMH, SNDK, SNPS, SOXX, TER, TSM, VRT, WDC, XSD |
| 300 USD | **18 de 36** | 7 | AMAT, AMD, ASML, AVGO, GOOGL, LIN, LRCX, META, MSFT, MU, SMH, SNDK, SNPS, SOXX, TER, TSM, WDC, XSD |
| 350 USD | **20 de 36** | 7 | AMAT, AMD, ASML, AVGO, LIN, META, MSFT, MU, SMH, SNDK, SNPS, SOXX, TER, TSM, WDC, XSD |
| 400 USD | **23 de 36** | 7 | AMAT, AMD, ASML, LIN, META, MSFT, MU, SMH, SNDK, SOXX, TSM, WDC, XSD |
| 450 USD | **24 de 36** | 8 | AMAT, AMD, ASML, LIN, META, MSFT, MU, SMH, SNDK, SOXX, WDC, XSD |
| 500 USD | **29 de 36** | 8 | ASML, META, MSFT, MU, SMH, SNDK, SOXX |

## B. Cuenta en papel v2, juego `conservador`, K = 20 sorteos sin información sobre UN camino de mercado (membresía fijada en DESDE = 2023-09-05, que depende del techo)

| Presupuesto | Operables en DESDE | Semillas congeladas antes de 156 sem. | Wilson 95 % (error de simulación, un solo camino) | Fricción a 156 sem., VIVAS: n · mediana [mín, máx] | Fricción a 156 sem., CONGELADAS: n · mediana [mín, máx] |
|---|---|---|---|---|---|
| 100 USD | 18 | 12 de 20 (60 %) | [39 %, 78 %] | 8 · 20.7 % [19.64, 21.16] | 12 · 10.42 % [9.77, 11.45] |
| 150 USD | 24 | 17 de 20 (85 %) | [64 %, 95 %] | 3 · 23.2 % [22.18, 23.53] | 17 · 11.92 % [0.97, 13.11] |
| 200 USD | 27 | 7 de 20 (35 %) | [18 %, 57 %] | 13 · 20.81 % [19.74, 21.38] | 7 · 11.08 % [10.32, 12.48] |
| 250 USD | 29 | 12 de 20 (60 %) | [39 %, 78 %] | 8 · 19.09 % [17.59, 19.85] | 12 · 10.3 % [7.59, 11.04] |
| 300 USD | 30 | 7 de 20 (35 %) | [18 %, 57 %] | 13 · 17.05 % [16.23, 17.99] | 7 · 9.33 % [8.86, 10.25] |
| 350 USD | 31 | 5 de 20 (25 %) | [11 %, 47 %] | 15 · 15.49 % [14.16, 16.56] | 5 · 8.99 % [8.46, 9.32] |
| 400 USD | 32 | 4 de 20 (20 %) | [8 %, 42 %] | 16 · 14.47 % [13.44, 15.43] | 4 · 7.57 % [0.5, 8.86] |
| 450 USD | 32 | 3 de 20 (15 %) | [5 %, 36 %] | 17 · 13.59 % [12.56, 14.49] | 3 · 7.16 % [5.87, 7.87] |
| 500 USD | 33 | 5 de 20 (25 %) | [11 %, 47 %] | 15 · 12.5 % [12.16, 13.1] | 5 · 6.63 % [6.26, 7.53] |

Fricción = 100 × comisiones acumuladas / capital aportado acumulado, a 156 semanas, SIN anualizar (m2_periodo.lecturas_m2). Se reporta condicionada al estado porque la mezcla es bimodal y su mediana salta de modo según quién sea mayoría; una cuenta congelada acumula poca comisión por QUIEBRA operativa, no por baratura (E4 del §43).

## Quiénes alcanzan, por presupuesto

- **100 USD:** AMKR (47.77), ASX (37.51), GFS (45.21), GSM (4.67), INTC (95.80), SHECY (18.61), UMC (20.77)
- **150 USD:** AMKR (47.77), ASX (37.51), ENTG (138.74), GFS (45.21), GSM (4.67), INTC (95.80), SHECY (18.61), UMC (20.77)
- **200 USD:** AMKR (47.77), ASX (37.51), ENTG (138.74), GFS (45.21), GSM (4.67), INTC (95.80), KLAC (185.60), QCOM (168.74), SHECY (18.61), TOELY (176.49), UMC (20.77)
- **250 USD:** AMKR (47.77), ASX (37.51), ENTG (138.74), GFS (45.21), GSM (4.67), INTC (95.80), KLAC (185.60), NVDA (230.36), QCOM (168.74), SHECY (18.61), TOELY (176.49), TSEM (222.34), UMC (20.77)
- **300 USD:** AMKR (47.77), AMZN (258.51), ARM (252.09), ASX (37.51), CDNS (292.70), ENTG (138.74), GFS (45.21), GSM (4.67), INTC (95.80), KLAC (185.60), MKSI (260.31), NVDA (230.36), QCOM (168.74), SHECY (18.61), TOELY (176.49), TSEM (222.34), UMC (20.77), VRT (280.53)
- **350 USD:** AMKR (47.77), AMZN (258.51), ARM (252.09), ASX (37.51), CDNS (292.70), ENTG (138.74), GFS (45.21), GOOGL (338.46), GSM (4.67), INTC (95.80), KLAC (185.60), LRCX (307.65), MKSI (260.31), NVDA (230.36), QCOM (168.74), SHECY (18.61), TOELY (176.49), TSEM (222.34), UMC (20.77), VRT (280.53)
- **400 USD:** AMKR (47.77), AMZN (258.51), ARM (252.09), ASX (37.51), AVGO (357.90), CDNS (292.70), ENTG (138.74), GFS (45.21), GOOGL (338.46), GSM (4.67), INTC (95.80), KLAC (185.60), LRCX (307.65), MKSI (260.31), NVDA (230.36), QCOM (168.74), SHECY (18.61), SNPS (393.84), TER (357.03), TOELY (176.49), TSEM (222.34), UMC (20.77), VRT (280.53)
- **450 USD:** AMKR (47.77), AMZN (258.51), ARM (252.09), ASX (37.51), AVGO (357.90), CDNS (292.70), ENTG (138.74), GFS (45.21), GOOGL (338.46), GSM (4.67), INTC (95.80), KLAC (185.60), LRCX (307.65), MKSI (260.31), NVDA (230.36), QCOM (168.74), SHECY (18.61), SNPS (393.84), TER (357.03), TOELY (176.49), TSEM (222.34), TSM (428.91), UMC (20.77), VRT (280.53)
- **500 USD:** AMAT (454.71), AMD (477.57), AMKR (47.77), AMZN (258.51), ARM (252.09), ASX (37.51), AVGO (357.90), CDNS (292.70), ENTG (138.74), GFS (45.21), GOOGL (338.46), GSM (4.67), INTC (95.80), KLAC (185.60), LIN (477.57), LRCX (307.65), MKSI (260.31), NVDA (230.36), QCOM (168.74), SHECY (18.61), SNPS (393.84), TER (357.03), TOELY (176.49), TSEM (222.34), TSM (428.91), UMC (20.77), VRT (280.53), WDC (467.46), XSD (491.45)

## Advertencias

- una semilla congelada acumula poca comisión por QUIEBRA operativa, no por baratura (E4 del §43)
- los cierres del congelado son ajustados retroactivamente por yfinance: no point-in-time (declarado)
- la membresía del universo se fija en DESDE (2023-09-05) para la cuenta y al último cierre para el alcance: son dos preguntas distintas y se declaran las dos

Ninguna fila de esta tabla fija el monto de E2: es el insumo de la reevaluación que el §86.3 prevé por acta. Tabla DESCRIPTIVA: no hay corrida con verdad conocida para la fracción de semillas congeladas ni para su Wilson (`instrumento_dinero.py` valida otro estimador); si alguna fila fuera a informar un umbral, el simulador se extiende primero. El barrido (9 presupuestos × 20 semillas) está declarado en `dinero/registro_intentos.py` como una hipótesis descriptiva; elegir después un presupuesto de esta tabla no es pre-especificarlo.
