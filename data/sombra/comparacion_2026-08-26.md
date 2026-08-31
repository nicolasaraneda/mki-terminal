# Comparación de sombra — 2026-08-26

- **Veredicto: DIVERGENCIA**
- Motivo: 12 hallazgo(s) de nivel 1 o 2
- Generado: 2026-08-30T18:47:28.166657+00:00
- Titular: `origin/main` = `28710b28e2cd3677dad4ff391eaf199eac991691`  ⚠ sin `git fetch` (--sin-fetch)
- Sombra: `senales.db` local, abierta en `mode=ro`
- Fecha de corte: 2026-08-24 (fechas <= corte se rechazan: bases idénticas por construcción)

## Criterio aplicado

| Nivel | Regla | Campos |
|---|---|---|
| 1 | identidad numérica, tolerancia relativa 1e-09 | snapshot: sox_usado_pct · ticker: apertura_estimada_pct, confianza_r2, beta, intervalo80_pp, puntaje_v0 |
| 2 | igualdad exacta | snapshot: regimen, roca_chip, modelo_version, feature_version, universo_version, ventana_betas, descarga_ok, descarga_total, descarga_caidos, sox_fecha · ticker: exchange, sesion_objetivo, available_at, modelo_version, n_muestra · conjunto de tickers · nº de predicciones · filas selladas |
| 3 | diferencia legítima esperada, fuera del veredicto | snapshot: plataforma_version, timestamp_utc, creado_en, origen · ticker: timestamp_utc, estado, sentimiento_ia, puntaje_ia |

Los extremos del intervalo del 80% son `apertura_estimada_pct ± intervalo80_pp`; ambos van al nivel 1, así que comparar los dos ES comparar los extremos.
Excluidos por completo: id (rowid local, sin significado compartido).

## Hallazgos de nivel 1 y 2 — 12

| Nivel | Ámbito | Clave | Campo | Titular | Sombra | Delta |
|---|---|---|---|---|---|---|
| 1 | ticker | 000660.KS | confianza_r2 | 0.2005 | 0.2004 | 0.0001 |
| 2 | ticker | 000660.KS | sesion_objetivo | 2026-08-28 | 2026-08-27 |  |
| 1 | ticker | 005930.KS | puntaje_v0 | 0.68 | 0.67 | 0.01 |
| 2 | ticker | 005930.KS | sesion_objetivo | 2026-08-28 | 2026-08-27 |  |
| 2 | ticker | 3436.T | sesion_objetivo | 2026-08-28 | 2026-08-27 |  |
| 1 | ticker | 4063.T | confianza_r2 | 0.1657 | 0.1656 | 0.0001 |
| 2 | ticker | 4063.T | sesion_objetivo | 2026-08-28 | 2026-08-27 |  |
| 2 | ticker | 6857.T | sesion_objetivo | 2026-08-28 | 2026-08-27 |  |
| 1 | ticker | 8035.T | confianza_r2 | 0.2517 | 0.2516 | 0.0001 |
| 2 | ticker | 8035.T | sesion_objetivo | 2026-08-28 | 2026-08-27 |  |
| 1 | ticker | FCX | puntaje_v0 | 0.6 | 0.62 | 0.02 |
| 1 | ticker | IFX.DE | confianza_r2 | 0.0081 | 0.008 | 0.0001 |

## Diferencias esperadas (nivel 3, informativas) — 82

No cuentan para el veredicto.

| Ámbito | Clave | Campo | Titular | Sombra |
|---|---|---|---|---|
| snapshot | 2026-08-26 | plataforma_version | 5.0.2 | 5.0.3 |
| snapshot | 2026-08-26 | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| snapshot | 2026-08-26 | creado_en | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | 000660.KS | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | 000660.KS | estado | pendiente | verificada |
| ticker | 000660.KS | sentimiento_ia | 0.2483185173514227 | 0.22135474605728855 |
| ticker | 000660.KS | puntaje_ia | 0.6632 | 0.6592 |
| ticker | 005930.KS | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | 005930.KS | estado | pendiente | verificada |
| ticker | 005930.KS | sentimiento_ia | 0.2673197629949233 | 0.2847759524073363 |
| ticker | 005930.KS | puntaje_ia | 0.6661 | 0.6617 |
| ticker | 2330.TW | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | 2330.TW | sentimiento_ia | 0.4842916480746855 | 0.5029039043975372 |
| ticker | 2330.TW | puntaje_ia | 0.6286 | 0.6314 |
| ticker | 3436.T | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | 3436.T | estado | pendiente | verificada |
| ticker | 3436.T | sentimiento_ia | 0.1533322908791163 | -0.03351725340094672 |
| ticker | 3436.T | puntaje_ia | 0.635 | 0.607 |
| ticker | 4063.T | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | 4063.T | estado | pendiente | verificada |
| ticker | 4063.T | sentimiento_ia | 0.236678386741463 | 0.23091322281015295 |
| ticker | 4063.T | puntaje_ia | 0.3955 | 0.3946 |
| ticker | 6857.T | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | 6857.T | estado | pendiente | verificada |
| ticker | 6857.T | sentimiento_ia | 0.192880499531884 | 0.2822850980453547 |
| ticker | 6857.T | puntaje_ia | 0.6829 | 0.6963 |
| ticker | 8035.T | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | 8035.T | estado | pendiente | verificada |
| ticker | 8035.T | sentimiento_ia | 0.3500328755113968 | 0.3400043302540415 |
| ticker | 8035.T | puntaje_ia | 0.6155 | 0.614 |
| ticker | AMD | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | AMD | sentimiento_ia | 0.3324927772407957 | 0.3247839517538743 |
| ticker | AMD | puntaje_ia | 0.6829 | 0.6817 |
| ticker | ARM | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | ARM | sentimiento_ia | 0.3893617315304822 | 0.2545458440825617 |
| ticker | ARM | puntaje_ia | 0.6074 | 0.5872 |
| ticker | ASML | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | ASML | sentimiento_ia | 0.1344778549447716 | 0.23833480564893272 |
| ticker | ASML | puntaje_ia | 0.5342 | 0.5498 |
| ticker | AVGO | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | AVGO | sentimiento_ia | 0.1736573594003806 | 0.24669770121251247 |
| ticker | AVGO | puntaje_ia | 0.309 | 0.32 |
| ticker | BHP | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | BHP | sentimiento_ia | 0.1423544092991938 | 0.13987953389724517 |
| ticker | BHP | puntaje_ia | 0.6264 | 0.626 |
| ticker | FCX | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | FCX | sentimiento_ia | 0.1443478054558633 | 0.09242771017090745 |
| ticker | FCX | puntaje_ia | 0.5917 | 0.5979 |
| ticker | GOOGL | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | GOOGL | sentimiento_ia | 0.1400576950021798 | 0.20675787314420147 |
| ticker | GOOGL | puntaje_ia | 0.395 | 0.405 |
| ticker | IFX.DE | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | IFX.DE | estado | pendiente | verificada |
| ticker | IFX.DE | sentimiento_ia | 0.5478093741802214 | 0.5255405957139906 |
| ticker | IFX.DE | puntaje_ia | 0.4842 | 0.4808 |
| ticker | INTC | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | INTC | sentimiento_ia | 0.2249216134457264 | 0.239472140144752 |
| ticker | INTC | puntaje_ia | 0.5057 | 0.5079 |
| ticker | META | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | META | sentimiento_ia | 0.1577729967264328 | 0.10446392215045121 |
| ticker | META | puntaje_ia | 0.3277 | 0.3197 |
| ticker | MSFT | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | MSFT | sentimiento_ia | 0.2255501094155472 | 0.2026614846898138 |
| ticker | MSFT | puntaje_ia | 0.6598 | 0.6564 |
| ticker | MU | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | MU | sentimiento_ia | 0.1923097289552838 | 0.22744884918823902 |
| ticker | MU | puntaje_ia | 0.7038 | 0.7091 |
| ticker | NVDA | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | NVDA | sentimiento_ia | 0.2522992937623471 | 0.3735204557700645 |
| ticker | NVDA | puntaje_ia | 0.4748 | 0.493 |
| ticker | QCOM | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | QCOM | sentimiento_ia | 0.3113980917974448 | 0.3213312334730145 |
| ticker | QCOM | puntaje_ia | 0.4067 | 0.4082 |
| ticker | TSM | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | TSM | sentimiento_ia | 0.4842916480746855 | 0.5029039043975372 |
| ticker | TSM | puntaje_ia | 0.5166 | 0.5194 |
| ticker | TXN | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | TXN | sentimiento_ia | 0.2619825496922901 | 0.27516899130897954 |
| ticker | TXN | puntaje_ia | 0.4553 | 0.4573 |
| ticker | UMC | timestamp_utc | 2026-08-27T00:05:50.336096+00:00 | 2026-08-26T22:15:07.552414+00:00 |
| ticker | UMC | sentimiento_ia | 0.212106893546118 | 0.2769827691660533 |
| ticker | UMC | puntaje_ia | 0.5668 | 0.5765 |

