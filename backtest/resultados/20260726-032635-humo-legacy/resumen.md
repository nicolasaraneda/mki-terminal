# ⚠ RESULTADO NO-CONCLUYENTE (corrida de humo)

El gatillo de la Etapa 5.1 no se ha cumplido o el usuario no ha disparado la corrida con veredicto. Estos números SOLO prueban que la maquinaria funciona.

# Backtest MKI — humo-legacy · 2026-06-01 → 2026-07-18

Generado 2026-07-26T03:26:35.476591+00:00 · commit 79176cb · descartes sin datos: 4


## Baselines

| B | n | %grado B | IC medio | t(NW) | MAE gap | Sharpe LS 25pb [IC90] | acum. LS 25pb |
|---|---|---|---|---|---|---|---|
| B0 | 276 | 0.0% | 0.0 | nan | 2.754 | -6.78 None | -30.6% |
| B1 | 276 | 0.0% | -0.0696 | -0.99 | 2.782 | -2.21 None | -9.1% |
| B2 | 276 | 0.0% | 0.3144 | 2.74 | 2.482 | -6.61 None | -32.2% |
| B3 | 276 | 0.0% | 0.2765 | 2.41 | 2.46 | -7.69 None | -32.4% |
| B4 | 276 | 85.5% | 0.248 | 2.14 | 2.506 | -7.16 None | -28.3% |
| B5 | 276 | 85.5% | 0.2347 | 2.07 | 2.513 | -5.47 None | -23.4% |

**Benchmark obligatorio — comprar SMH y no hacer nada**: acumulado -7.1% · Sharpe -0.59 · MDD -16.8% — toda cartera se lee CONTRA esta línea (ajuste GATE B).


## Veredicto escalonado (capa vs capa)

| Capa | ΔIC | t(NW) | días | veredicto |
|---|---|---|---|---|
| B1 vs B0 | -0.0696 | -0.99 | 35 | no demostrado |
| B2 vs B1 | 0.384 | 2.57 | 35 | aporta |
| B3 vs B2 | -0.0379 | -2.24 | 35 | no demostrado |
| B4 vs B3 | -0.0285 | -1.33 | 35 | no demostrado |
| B5 vs B4 | -0.0133 | -0.81 | 35 | no demostrado |

## Auditoría B2 vs sellos reales
50 predicciones comparadas · diferencia media 0.053 pp · máx 0.28 pp. las diferencias reflejan deriva de datos de la fuente entre el sello y hoy (hallazgo 4.7.1), no necesariamente un bug.


---
Herramienta de análisis — no constituye asesoría financiera. Diseño congelado en backtest/DISEÑO.md.
