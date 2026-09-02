# La autocorrelación que 35 fechas no acotan — dos salidas (Frente D, PROPUESTA)

> **PROPUESTA — sin dictamen del estadistico-adversario no entra a DISEÑO.md ni a resultados**

- Generado: 2026-09-02T06:59:53.481665+00:00 · `python GEMELO/SECUENCIAL/autocorrelacion.py`

## Salida 1 · AC1 de d_j en la ventana larga reconstruida, como prior

- Fuente: `backtest/resultados/20260901-133154-5.1-arnes-corregido-gatillo-incumplido/predicciones_B2.csv` — **518 fechas** (2024-09-02 → 2026-08-28), deduplicada por sesión objetivo, `excluir_cero`.
- AC1…AC5: [-0.042, -0.02, 0.012, -0.018, 0.051]
- **AC1 = -0.042**, EE 1/√m = 0.044, IC95 bootstrap de bloques (20): **[-0.122, 0.041]** (contiene el cero: AC1 no se distingue de 0)
- Ventana sellada, misma aritmética: AC1 = -0.176 ± 0.164 sobre 37 fechas.
- **La reconstrucción en el mismo tramo de calendario que la sellada** (desde 2026-07-05, 40 fechas): AC1 = -0.18 ± 0.158 — reproduce a la sellada donde las dos existen.
- Máximo |AC| en los rezagos 1–5: 0.051.
- α del plan bajo esta referencia (simulador del diseño, 2.000 réplicas, con el Wilson de las réplicas): {'-0.042': [0.039, 0.0314, 0.0484], '0.041': [0.0545, 0.0454, 0.0653], '0.0': [0.047, 0.0386, 0.0572]} → **rango honesto [0.031, 0.065]**. DGP del simulador del diseño: d_j discretizado (np.round(d·7/2)); el de Salida 2: normal continuo. Dos DGP.

| año | fechas | AC1 | EE |
|---|---|---|---|
| 2024 | 87 | -0.014 | 0.107 |
| 2025 | 260 | -0.08 | 0.062 |
| 2026 | 171 | -0.007 | 0.076 |

Advertencias: ventana reconstruida (B2 = motor de producción sobre Yahoo del 1-sep), no sellada; deduplicada por (ticker, sesion_objetivo) para neutralizar B-3; incluye el 28-ago reconstruido con signo contrario (1 fecha); una sola descarga congelada: ciega por construcción a la intermitencia de la fuente (M6 del Frente A); es una MEDICIÓN DE REFERENCIA con su IC, no una cota: el extremo de un IC no es una certeza.

## Salida 2 · α global del plan OBF (4 miradas) por estadístico, bajo AR(1) en d_j

- 20000 réplicas por celda (±0.003), fechas por mirada [51, 102, 152, 203], umbrales [4.048, 2.862, 2.337, 2.024]. Sin bootstrap interno: mide el estadístico, no el estimador de varianza del plan.

| φ | DIA | BLQ10 | BLQ20 | HAC5 | HAC10 |
|---|---|---|---|---|---|
| 0.0 | 0.0506 | 0.0889 | 0.1231 | 0.0635 | 0.0795 |
| 0.1 | 0.0804 | 0.0926 | 0.1245 | 0.0689 | 0.0837 |
| 0.2 | 0.1193 | 0.0957 | 0.1270 | 0.0756 | 0.0883 |
| 0.3 | 0.1708 | 0.1004 | 0.1290 | 0.0840 | 0.0935 |

**Potencia** frente a un drift de 0.18 sd por fecha:

| φ | DIA | BLQ10 | BLQ20 | HAC5 | HAC10 |
|---|---|---|---|---|---|
| 0.0 | 0.720 | 0.727 | 0.739 | 0.737 | 0.749 |
| 0.2 | 0.695 | 0.589 | 0.604 | 0.601 | 0.611 |

