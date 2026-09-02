# Predicción transversal: ¿el orden de las β tiene información? — Frente D (PROPUESTA)

> **PROPUESTA — Frente D, octava corrida; pendiente de dictamen** · generado 2026-09-02T18:39:29.846739+00:00 · `python GEMELO/transversal.py` --abrir-prueba

Pre-registro: `GEMELO/preregistro/frente_D.md`. Unidad = la FECHA (n efectivo = fechas con ≥ 4 tickers). p por permutación dentro del día (4000), IC por bootstrap de fechas (4000). Efecto relevante pre-declarado: ρ̄ ≥ 0.2.

**Título honesto (dictamen D):** un orden de β estimado SIN el motor ordena dentro del día; el orden del CAMPEÓN no alcanza la vara pre-registrada y en la ventana sellada no sobrevive a R2. Toda fila de la ventana larga es sobre el PROXY (OLS gap ~ SOX(t−1), expansiva/fija), no sobre el modelo 4.6.0 (rodante 120, cierre-a-cierre).

| ventana | fechas (n efectivo) | ρ̄ Spearman | IC95 percentil | IC95 t de clúster | p permutación within-day / p con SE muestral | τ̄ Kendall IC95 | fechas con ρ > 0 [Wilson] |
|---|---|---|---|---|---|---|---|
| sellada (viva hasta 2026-08-31, predicción sellada) | 35 (259 filas) | **0.2294** | [0.0343, 0.4182] | [0.0252, 0.4335] | 0.0007 / 0.0224 | 0.1882 [0.0333, 0.3423] | 0.571 [0.409, 0.72] |
| larga · años de AJUSTE ('2018-09-01', '2023-12-31') (β CAUSAL expansiva, burn-in 250) | 1102 (8371 filas) | **0.2484** | [0.2202, 0.2768] | [0.2204, 0.2764] | < 0.00025 (piso de 4000 permutaciones) / 0.0 | 0.1952 [0.1724, 0.2181] | 0.7 [0.672, 0.726] |
| larga · años de PRUEBA desde 2024-01-08 (embargo 5 sesiones; β del ajuste fija; sin las fechas selladas ('2026-07-05', '2026-08-31')) | 637 (4828 filas) | **0.2403** | [0.2062, 0.2756] | [0.2055, 0.2751] | < 0.00025 (piso de 4000 permutaciones) / 0.0 | 0.1883 [0.1608, 0.2167] | 0.703 [0.667, 0.737] |

**Sellada, R2 (sin 15–23 jul):** ρ̄ 0.1899 percentil [-0.0218, 0.4084] / t de clúster [-0.0391, 0.4189] — cruza el cero: R2 SE ACTIVA. MDE al 80% con la SE muestral: 0.2813 (efecto observado 0.2294). Dejar-uno-fuera: {'sin_000660.KS': 0.2124, 'sin_005930.KS': 0.2014, 'sin_2330.TW': 0.1993, 'sin_3436.T': 0.2305, 'sin_4063.T': 0.2054, 'sin_6857.T': 0.2123, 'sin_8035.T': 0.1903, 'sin_IFX.DE': 0.2301}. el IC que vale es el de t de clúster (k = 35); el percentil sub-cubre (Frente A) y bloques de 20 degenera (2 bloques). apertura_estimada_pct está sellada a 2 decimales: empates en varias fechas atenúan ρ (sesgo CONTRA el hallazgo).

**Nula honesta (principal): etiquetas de β permutadas entre tickers** (2000 réplicas): ρ̄ observado 0.2403, nula media -0.0009, sd 0.1003, q2,5/97,5 [-0.1931, 0.1887], **p bilateral 0.005**; fracción de órdenes aleatorios sobre 0.2: 0.019. La unidad de replicación de la afirmación es el ORDENAMIENTO (n = 1); la permutación within-day es una sensibilidad de una hipótesis más débil.
**Identidad verificada:** ρ_d = sign(S_d)·spearman(orden β, gap), discrepancia máxima 0.00e+00: el «modelo transversal» es un vector de 8 β más un bit por día.
Por signo del SOX: {'sox_positivo': {'fechas': 366, 'rho_medio': 0.2415, 'ic95_aprox': [0.1978, 0.2852]}, 'sox_negativo': {'fechas': 271, 'rho_medio': 0.2387, 'ic95_aprox': [0.1822, 0.2952]}} (simétrico = no es artefacto de nivel). Dejar-uno-fuera: {'sin_000660.KS': 0.2466, 'sin_005930.KS': 0.2485, 'sin_2330.TW': 0.2423, 'sin_3436.T': 0.2607, 'sin_4063.T': 0.23, 'sin_6857.T': 0.2067, 'sin_8035.T': 0.2425, 'sin_IFX.DE': 0.2053}. Sin `excluir_cero`: {'fechas': 640, 'filas': 4857, 'rho_medio': 0.2426, 'ic95_rho': [0.2075, 0.277]}.
Aperturas de la prueba: ['12:11 (gaps v1, 626 fechas, ρ̄ 0,2373) — defecto de datos en descargar_gaps', '12:14 (gaps v2, 637 fechas) — la vigente; dos evaluaciones del holdout propio del frente, declaradas'].
**El CAMPEÓN, no el proxy:** orden de las β selladas → ρ̄ 0.1795 [0.1461, 0.212] (t de clúster [0.1462, 0.2128]), relevante: False — CONTRAFACTUAL CONTAMINADO (β selladas, estimadas en 2026): cota optimista de lo que el campeón habría hecho. Proxy − campeón: 0.0608 [0.0252, 0.0964] sobre 637 fechas. Spearman entre los dos vectores de β: 0.4524.
Universo: los 8 tickers son la composición de 2026 (universo.MERCADOS_POR_ABRIR) aplicada hacia atrás a 2018: selección ex post del corte transversal, declarada.

Orden de β en el ajuste: ['6857.T', '8035.T', '3436.T', '000660.KS', '2330.TW', '4063.T', '005930.KS', 'IFX.DE'] ({'000660.KS': 0.4312, '005930.KS': 0.2929, '2330.TW': 0.3829, '3436.T': 0.5302, '4063.T': 0.3627, '6857.T': 0.5931, '8035.T': 0.5488, 'IFX.DE': 0.1548}).
Fuentes sin motor: `GEMELO/resultados/testigos_fuente/gaps_v2_propio_indice.csv.gz` (gaps reconstruidos) y `GEMELO/resultados/testigos_fuente/cierres_353cacd57dc25f6a.csv.gz` (SOX, caché testigo).

