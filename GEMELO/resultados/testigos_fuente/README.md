# Testigos de la fuente — copias preservadas de `GEMELO/cache/`

`GEMELO/cache/` está gitignorado y **se sobreescribe** en cuanto alguien
corre un módulo de GEMELO con `usar_cache=True` y el TTL (12 h) venció.
Estos cuatro archivos son las únicas fotos que existen de cómo servía Yahoo
la historia esos días, y son la base de M1 de `GEMELO/fuente_canonica.py`.
Se copian acá, comprimidos, para que un `ventana_larga.py` de rutina no
borre la evidencia. **No se editan.** El sha256 es del `.csv` en claro.

| archivo | capturado (local, UTC−4) | contenido | sha256 (16) |
|---|---|---|---|
| `cierres_03fdca36d64efb0d.csv.gz` | 2026-08-26 00:23:39 | 8 acciones objetivo, 8 años | `70249482f11e256e` |
| `cierres_853b6558513c5e9f.csv.gz` | 2026-08-26 00:22:04 | 27 tickers del universo, 8 años | `242802c423e07188` |
| `cierres_353cacd57dc25f6a.csv.gz` | 2026-09-01 09:16:41 | `^SOX`, futuros, VIX, crédito, FX, índices locales (15 series) | `013383bb609829d6` |
| `cierres_55f56647c2976497.csv.gz` | 2026-09-01 09:07:19 | 37 series (universo + FX + índices + `^SOX`) | `c908dfa6fda0c68e` |

Lo que dicen: el 26-ago la historia de 8 años era la misma que hoy en
retornos (0 cambiados); el 1-sep a las 13:07Z la barra del `^SOX` del
28-ago ya no estaba (`NaN`), y la del 31-jul sí.

**Agregado 2-sep-2026 (octava corrida, a pedido del `auditor-lookahead`):**
`gaps_03fdca36d64efb0d.csv.gz` — gaps de apertura `Open(S)/Close(S−1) − 1`
de los 8 tickers objetivo, 2018-09-04 → 2026-09-01 (15.027 filas),
capturado 2026-09-01 09:16:41 local desde `GEMELO/datos.descargar_gaps`.
Es la fuente de gaps de `GEMELO/transversal.py` y
`GEMELO/decaimiento_feriados.py`, que leen de acá y no del caché mutable.

**`gaps_v2_propio_indice.csv.gz`** (2-sep-2026 12:14, descarga fresca con
`usar_cache=False`, generador corregido `GEMELO.datos.gaps_desde_ohlc`):
15.697 filas, 2018-09-04 → 2026-09-02, sha256 `34fe61082ea58282`. Contra el
v1: **670 filas nuevas (las sesiones posteriores a un feriado local, que el
`shift(1)` sobre el índice unión borraba), 0 filas viejas perdidas, gaps
comunes idénticos** (max |dif| 9e-5). Es la fuente de `transversal.py` y
`decaimiento_feriados.py` desde esta hora; el v1 se conserva como testigo de
lo que la ventana larga publicada usó.

## Agregado el 2-sep-2026, 15:20 (octava corrida)

- `b2_nuevos_ohlc.csv.gz` — OHLC (open, close) de los seis tickers nuevos del
  Frente B2 (`0981.HK`, `1347.HK`, `ASML.AS`, `BESI.AS`, `MOSCHIP.NS`,
  `TATAELXSI.NS`), descargado a las 14:50 local (fuera de la ventana
  17:50–20:30) por `GEMELO/decaimiento_prediccion.py --medir`; sha256 del
  `.gz` `d7f213266f8823fa…` registrado en `decaimiento_prediccion.json`
  (`medicion.testigo_sha256`). `--medir` lee de aquí; `--redescargar` es
  explícito.
- **Dos convenciones de sha conviven, y se declaran:** este README cita el
  sha256 del **csv en claro** (p. ej. `gaps_v2` = `34fe61082ea58282…`); los
  candados `no_capturabilidad.lock` y `decaimiento_feriados.lock` y el JSON
  de B2 citan el sha256 del **archivo `.gz`** tal como está en disco. Los dos
  son correctos para lo que identifican; no son comparables entre sí.
