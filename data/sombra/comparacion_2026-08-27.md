# Comparación de sombra — 2026-08-27

- **Veredicto: DIVERGENCIA**
- Motivo: 1 hallazgo(s) de nivel 1 o 2
- Generado: 2026-08-30T18:47:28.175533+00:00
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

## Hallazgos de nivel 1 y 2 — 1

| Nivel | Ámbito | Clave | Campo | Titular | Sombra | Delta |
|---|---|---|---|---|---|---|
| 1 | ticker | 6857.T | confianza_r2 | 0.1831 | 0.1832 | 0.0001 |

## Diferencias esperadas (nivel 3, informativas) — 75

No cuentan para el veredicto.

| Ámbito | Clave | Campo | Titular | Sombra |
|---|---|---|---|---|
| snapshot | 2026-08-27 | plataforma_version | 5.0.2 | 5.0.3 |
| snapshot | 2026-08-27 | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| snapshot | 2026-08-27 | creado_en | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | 000660.KS | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | 000660.KS | sentimiento_ia | 0.244325898093365 | 0.25402597076213257 |
| ticker | 000660.KS | puntaje_ia | 0.6766 | 0.6781 |
| ticker | 005930.KS | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | 005930.KS | sentimiento_ia | 0.2848173775295837 | 0.2774353719113466 |
| ticker | 005930.KS | puntaje_ia | 0.6687 | 0.6676 |
| ticker | 2330.TW | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | 2330.TW | sentimiento_ia | 0.5063596012629771 | 0.5103736483380096 |
| ticker | 2330.TW | puntaje_ia | 0.66 | 0.6606 |
| ticker | 3436.T | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | 3436.T | sentimiento_ia | 0.1163024177024996 | -0.0005281967730068066 |
| ticker | 3436.T | puntaje_ia | 0.6504 | 0.6329 |
| ticker | 4063.T | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | 4063.T | sentimiento_ia | 0.2210296684118673 | 0.2385665209244222 |
| ticker | 4063.T | puntaje_ia | 0.4492 | 0.4518 |
| ticker | 6857.T | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | 6857.T | sentimiento_ia | 0.2540352538422318 | 0.1314968008716004 |
| ticker | 6857.T | puntaje_ia | 0.6571 | 0.6387 |
| ticker | 8035.T | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | 8035.T | sentimiento_ia | 0.3362666958959021 | 0.381418088680856 |
| ticker | 8035.T | puntaje_ia | 0.5924 | 0.5992 |
| ticker | AMD | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | AMD | sentimiento_ia | 0.3102809654425675 | 0.3242179551709375 |
| ticker | AMD | puntaje_ia | 0.5605 | 0.5626 |
| ticker | ARM | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | ARM | sentimiento_ia | 0.3567874413172936 | 0.2910837854086997 |
| ticker | ARM | puntaje_ia | 0.5815 | 0.5717 |
| ticker | ASML | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | ASML | sentimiento_ia | 0.1702981820478859 | 0.2401213088414805 |
| ticker | ASML | puntaje_ia | 0.4625 | 0.473 |
| ticker | AVGO | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | AVGO | sentimiento_ia | 0.2094702726146871 | 0.3141313705278471 |
| ticker | AVGO | puntaje_ia | 0.3284 | 0.3441 |
| ticker | BHP | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | BHP | sentimiento_ia | 0.1590671416918727 | 0.2112212423123151 |
| ticker | BHP | puntaje_ia | 0.6429 | 0.6507 |
| ticker | FCX | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | FCX | sentimiento_ia | 0.104184341977528 | 0.13132889967603753 |
| ticker | FCX | puntaje_ia | 0.5856 | 0.5897 |
| ticker | GOOGL | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | GOOGL | sentimiento_ia | 0.165049042073115 | 0.1950760236531479 |
| ticker | GOOGL | puntaje_ia | 0.4408 | 0.4453 |
| ticker | IFX.DE | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | IFX.DE | sentimiento_ia | 0.5443442663089408 | 0.5159062325300817 |
| ticker | IFX.DE | puntaje_ia | 0.4557 | 0.4514 |
| ticker | INTC | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | INTC | sentimiento_ia | 0.2195096869102268 | 0.23527009692826806 |
| ticker | INTC | puntaje_ia | 0.5189 | 0.5213 |
| ticker | META | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | META | sentimiento_ia | 0.2206771655998741 | 0.14734352767330783 |
| ticker | META | puntaje_ia | 0.4211 | 0.4101 |
| ticker | MSFT | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | MSFT | sentimiento_ia | 0.22042677264718 | 0.280121942581782 |
| ticker | MSFT | puntaje_ia | 0.5961 | 0.605 |
| ticker | MU | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | MU | sentimiento_ia | 0.2156334177802037 | 0.28244401009512143 |
| ticker | MU | puntaje_ia | 0.6233 | 0.6334 |
| ticker | NVDA | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | NVDA | sentimiento_ia | 0.3567887547934573 | 0.4364356222745241 |
| ticker | NVDA | puntaje_ia | 0.6305 | 0.6425 |
| ticker | QCOM | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | QCOM | sentimiento_ia | 0.2862736685351786 | 0.32658471698917124 |
| ticker | QCOM | puntaje_ia | 0.4729 | 0.479 |
| ticker | TSM | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | TSM | sentimiento_ia | 0.5063596012629771 | 0.5103736483380096 |
| ticker | TSM | puntaje_ia | 0.513 | 0.5136 |
| ticker | TXN | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | TXN | sentimiento_ia | 0.2676079668392722 | 0.3171632298380428 |
| ticker | TXN | puntaje_ia | 0.4911 | 0.4986 |
| ticker | UMC | timestamp_utc | 2026-08-27T22:46:08.718646+00:00 | 2026-08-27T22:15:03.321072+00:00 |
| ticker | UMC | sentimiento_ia | 0.197373692642936 | 0.2355472732945251 |
| ticker | UMC | puntaje_ia | 0.5086 | 0.5143 |

