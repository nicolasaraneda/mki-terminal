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
