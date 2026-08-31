# Comparación de sombra — 2026-08-28

- **Veredicto: DIA_NO_COMPUTABLE**
- Motivo: el titular publicó sellos de fechas posteriores pero ninguno de esta, así que la ausencia es DEFINITIVA: el TITULAR no selló. Un día solo cuenta si el titular selló de verdad esa noche.
- Generado: 2026-08-30T19:00:56.139512+00:00
- Titular: `origin/main` = `f72d479b6acec22ae2a0d12c26187aee1282288c`
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

## Sin comparación

el titular publicó sellos de fechas posteriores pero ninguno de esta, así que la ausencia es DEFINITIVA: el TITULAR no selló. Un día solo cuenta si el titular selló de verdad esa noche.

## Diferencias esperadas (nivel 3, informativas) — 0

No cuentan para el veredicto.

