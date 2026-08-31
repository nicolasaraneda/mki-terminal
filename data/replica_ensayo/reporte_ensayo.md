# Ensayo general de la réplica — Frente D

Generado: 2026-08-31T19:13:22.862021+00:00
Base sintética 'réplica' (sqlite real, temporal): /tmp/ensayo_replica_9jxbfl5g/replica_sintetica.db
Base sintética 'titular' (DataFrames, como si vinieran de `git show origin/main:...`): en memoria, construida por `construir_datos()`.
Base de divergencias del ensayo (temporal, NUNCA la de producción): /tmp/ensayo_replica_9jxbfl5g/divergencias_replica_ensayo.db

Ninguna de estas rutas es `senales.db`, `noticias.db` ni `data/divergencias_replica.db` — se crean en un directorio temporal y se borran al final de esta corrida.

## Caso 1 — coinciden — 2026-09-01

- Veredicto obtenido: **PARIDAD**  (esperado: PARIDAD)
- Motivo: todos los campos de nivel 1 y 2 coinciden
- Hallazgos nivel 1/2 de `comparar_fecha`: 0
- Filas insertadas por `registrar_comparacion`: 0

## Caso 2 — difieren (cómputo) — 2026-09-02

- Veredicto obtenido: **DIVERGENCIA**  (esperado: DIVERGENCIA)
- Motivo: 1 hallazgo(s) de nivel 1 o 2
- Hallazgos nivel 1/2 de `comparar_fecha`: 1
- Filas insertadas por `registrar_comparacion`: 1
    - campo=beta clase=computo titular='0.38' sombra='0.41' resuelto_como=None

## Caso 2 — difieren (insumos) — 2026-09-03

- Veredicto obtenido: **DIVERGENCIA**  (esperado: DIVERGENCIA)
- Motivo: 1 hallazgo(s) de nivel 1 o 2
- Hallazgos nivel 1/2 de `comparar_fecha`: 1
- Filas insertadas por `registrar_comparacion`: 1
    - campo=sox_fecha clase=insumos titular='2026-09-02' sombra='2026-09-03' resuelto_como=None

## Caso 2 — difieren (existencia, sello ausente) — 2026-09-04

- Veredicto obtenido: **DIVERGENCIA**  (esperado: DIVERGENCIA)
- Motivo: el titular selló y la SOMBRA no. No es un día no computable: es la sombra fallando, que es justo lo que la ventana existe para detectar.
- Hallazgos nivel 1/2 de `comparar_fecha`: 0
- Filas insertadas por `registrar_comparacion`: 1
    - campo=sello_ausente clase=existencia titular=None sombra=None resuelto_como=None

## Caso 2 — difieren (existencia, conjunto de tickers) — 2026-09-05

- Veredicto obtenido: **DIVERGENCIA**  (esperado: DIVERGENCIA)
- Motivo: 4 hallazgo(s) de nivel 1 o 2
- Hallazgos nivel 1/2 de `comparar_fecha`: 4
- Filas insertadas por `registrar_comparacion`: 4
    - campo=tickers_sellados clase=existencia titular='2 tickers' sombra='1 tickers' resuelto_como=None
    - campo=ticker_ausente_en_sombra clase=existencia titular='005930.KS' sombra=None resuelto_como=None
    - campo=numero_de_predicciones clase=existencia titular='2' sombra='1' resuelto_como=None
    - campo=filas_selladas clase=existencia titular='2' sombra='1' resuelto_como=None

## Caso 3 — no selló (DIA_NO_COMPUTABLE) — 2026-09-08

- Veredicto obtenido: **DIA_NO_COMPUTABLE**  (esperado: DIA_NO_COMPUTABLE)
- Motivo: el titular publicó sellos de fechas posteriores pero ninguno de esta, así que la ausencia es DEFINITIVA: no selló. Y la sombra tampoco. Sin sello del titular no hay contra qué comparar: día PERDIDO, no día bueno.
- Hallazgos nivel 1/2 de `comparar_fecha`: 0
- Filas insertadas por `registrar_comparacion`: 0

## (ancla) PARIDAD que desambigua el caso anterior — 2026-09-09

- Veredicto obtenido: **PARIDAD**  (esperado: PARIDAD)
- Motivo: todos los campos de nivel 1 y 2 coinciden
- Hallazgos nivel 1/2 de `comparar_fecha`: 0
- Filas insertadas por `registrar_comparacion`: 0

## Caso 3 — no selló (PENDIENTE_PUBLICACION) — 2026-09-10

- Veredicto obtenido: **PENDIENTE_PUBLICACION**  (esperado: PENDIENTE_PUBLICACION)
- Motivo: no hay fila del titular en origin/main para esta fecha, y tampoco hay sellos suyos de fechas posteriores: no se puede distinguir 'no selló' de 'selló y aún no pusheó'. NO es un día perdido — vuelve a correr después del push del Mac (manual, tras las 20:30) y el día se resuelve de verdad.
- Hallazgos nivel 1/2 de `comparar_fecha`: 0
- Filas insertadas por `registrar_comparacion`: 0

## Resumen

- Fechas ensayadas: 8
- Filas totales en `divergencias_replica` (base temporal del ensayo): 7
- `resuelto_como` NULL en todas las filas: True

### Sin hallazgos

Los tres casos se comportaron exactamente como predice `docs/REPLICA.md`: paridad sin ruido, divergencia con procedencia completa y clase correcta, ausencia legítima sin filas falsas.

