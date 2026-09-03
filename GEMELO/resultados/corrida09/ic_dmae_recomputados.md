# IC del ΔMAE del WS2b recomputados por clúster de día — corrida 09, Frente 2f (Parte 1)

**Fecha:** 3-sep-2026 · **Estatus:** MEDIDO donde hay número; NO EVALUABLE
donde se dice · **Reproduce:** `python GEMELO/resultados/corrida09/ic_dmae_recomputar.py --hasta-sello 2026-08-24`
(sin red: bloquea `socket`, fuerza `GEMELO/cache/`, `senales.db` en `mode=ro`).
**Salidas:** `ic_dmae_recomputados.json` y `ic_dmae_filas_{C1,C2,C3,CAMPEON}.csv` (predicciones por fila, que los artefactos originales NO guardaban).

## Qué estaba mal (DECISIONES.md §34.9)

`GEMELO/control_lineal.comparar` imprimía junto a `delta_mae` (pp) el
intervalo de `inferencia.bootstrap_bloques`, que es el IC del **Sharpe** de
la diferencia (media/desv), no de la media. `control_lineal.md` (WS2b) y
`ventana_larga.md` (WS3) quedaron con ese número. Aquí se recomputa el IC
en la escala correcta y, además, con el estimador que el preámbulo de la
corrida exige cuando hay varios tickers por fecha: **bootstrap de clúster de
día** (`GEMELO.bifurcaciones._bootstrap_dia`, 4.000 réplicas, semilla
`bifurcaciones.SEMILLA`), acompañado de la t de clúster y del p bilateral
por permutación de signo por día.

## Lo que se pudo y lo que no

- **Los artefactos no guardan predicciones por fila.** Hubo que recomputar
  con `GEMELO/experimento.py` desde la caché local (`_cache_vigente`
  forzado; el TTL de 12 h había vencido).
- **Filas selladas:** `lb.cargar(hasta_sello="2026-08-24", dedup=False)` +
  `excluir_cero` reproduce EXACTAMENTE las **223** filas / 31 días del WS2b
  (rama histórica sin deduplicar, justificada: se reproduce una afirmación
  congelada el 26-ago, anterior a la firma del 1-sep).
- **C1 reproduce las 215 filas / 30 días** y `C1 vs CAMPEON` reproduce el
  punto publicado a 0,0002 pp (−0,1325 vs −0,1327; la caché de gaps es del
  1-sep, no del 26-ago).
- **C2 y C3 NO reproducen: 79 filas / 11 días (8-jul → 24-jul) en vez de 215.**
  Causa medida: en la caché de cierres del 1-sep (`cierres_353cacd57dc25f6a.csv`)
  **`^VIX3M` tiene su último dato el 2026-07-17**; con el ffill acotado a 5 d
  de `GEMELO/datos.py`, las 14 features extra quedan NaN desde el 25-jul y
  C2/C3 pierden 136 filas. No existe caché anterior con las 15 series (las del
  26-ago son de otros conjuntos de tickers) y el preámbulo prohíbe descargar.
  **Todo lo que involucra C2 o C3 queda PARCIAL (79 filas) — se publica con esa
  etiqueta, no como reemplazo del par original.** Si `^VIX3M` dejó de
  publicarse en Yahoo, cualquier re-corrida futura del WS2b/WS3 tendrá este
  mismo agujero: es un hallazgo colateral que se deja abierto.
- **WS3 (`ventana_larga.md`): NO EVALUABLE esta noche.** `ventana_larga.py:94`
  baja el OHLC del campeón con `yf.download` sin caché; no hay forma offline.

## Retador vs campeón, y entre configuraciones (ΔMAE en pp; > 0 ⇒ A tiene MENOS error que B)

| Par | n | días | ΔMAE | **IC 95% clúster de día** | IC t-clúster | p perm. día | IC publicado (escala Sharpe, ERRÓNEO) | ¿cambia el veredicto `ic_excluye_cero`? |
|---|---|---|---|---|---|---|---|---|
| C1 vs CAMPEON | 215 | 30 | −0,1325 | **[−0,324, +0,035]** | [−0,326, +0,061] | 0,184 | [−0,3506, +0,0376] | No (incluye cero en ambas) |
| C2 vs C1 (PARCIAL 79) | 79 | 11 | +0,2002 | **[−0,061, +0,432]** | [−0,088, +0,488] | 0,178 | [−0,0389, +0,4232] (sobre 215) | No (incluye cero en ambas) |
| C3 vs C1 (PARCIAL 79) | 79 | 11 | +0,3200 | **[+0,077, +0,523]** | [+0,055, +0,585] | 0,031 | [+0,0665, +0,4729] (sobre 215) | No (excluye cero en ambas) |
| C3 vs C2 (PARCIAL 79) | 79 | 11 | +0,1199 | **[+0,004, +0,244]** | [−0,024, +0,264] | 0,096 | [+0,0564, +0,3071] (sobre 215) | No por percentil; **la t de clúster lo incluye** y el p de permutación es 0,096 |
| C2 vs CAMPEON (PARCIAL 79) | 79 | 11 | +0,0303 | **[−0,387, +0,421]** | [−0,450, +0,511] | 0,876 | [−0,2041, +0,2418] (sobre 215) | No |
| C3 vs CAMPEON (PARCIAL 79) | 79 | 11 | +0,1502 | **[−0,194, +0,468]** | [−0,237, +0,537] | 0,437 | [−0,1068, +0,3267] (sobre 215) | No |

Para el par completo (C1 vs CAMPEON) se recomputó también el IC de la media
con el bootstrap de bloques de filas (`inferencia.bootstrap_media`, el que el
§34.9 introdujo): [−0,283, +0,031]. Es más angosto que el de clúster de día
porque los bloques de 20 filas mezclan días parciales; el de día es el que
respeta que las 8 filas de una fecha comparten un solo movimiento del SOX.

## Cada configuración contra «predecir cero» (ΔMAE = MAE(0) − MAE(config), pp)

| Config | n | días | MAE config | MAE cero | ΔMAE | **IC 95% clúster de día** | IC t-clúster | p perm. día |
|---|---|---|---|---|---|---|---|---|
| CAMPEON | 223 | 31 | 3,124 | 3,500 | +0,375 | **[−0,201, +0,955]** | [−0,246, +0,996] | 0,218 |
| C1 | 215 | 30 | 3,214 | 3,577 | +0,362 | **[−0,055, +0,803]** | [−0,090, +0,814] | 0,117 |
| C2 (PARCIAL 79) | 79 | 11 | 2,359 | 3,024 | +0,665 | **[+0,343, +0,987]** | [+0,283, +1,046] | 0,005 |
| C3 (PARCIAL 79) | 79 | 11 | 2,240 | 3,024 | +0,784 | **[+0,403, +1,172]** | [+0,328, +1,241] | 0,006 |

**Lectura (MEDIDO):** sobre la ventana sellada completa, **ni el campeón ni
C1 reducen el MAE frente a predecir cero de forma distinguible al nivel de
día** (los dos IC de clúster incluyen cero; el de bloques de filas para C1,
[+0,082, +0,633], sí lo excluía — otra vez la unidad de análisis cambia la
respuesta). C2/C3 sí lo excluyen, pero sobre 79 filas de 11 días del 8 al
24 de julio: **es exactamente la ventana que R2 elimina (15–23 jul)**, así
que no se lee como evidencia a favor.

## ¿Cambia alguna conclusión del WS2b?

**No.** El §34.9 ya había demostrado que `ic_excluye_cero` es invariante a la
escala, y aquí se confirma para el único par completo. Lo que sí aporta el
clúster de día es (a) intervalos **más anchos** que los de bloques de filas
en todos los casos, (b) en `C3 vs C2` el veredicto del percentil (excluye
cero) y el de la t de clúster (no lo excluye) discrepan con 11 clústeres —
el defecto del percentil con pocos clústeres que el Frente A de la octava
corrida ya midió—, y (c) sobre la ventana completa **nadie mejora a
«cero» de forma distinguible**, lo que el WS2b no había preguntado.

## Intentos del DSR consumidos por este archivo

10 intervalos publicados sobre retornos reales (6 pares + 4 «vs cero»),
de los cuales 6 son re-emisiones en escala correcta de intervalos ya
contados en el WS2b (N=9) y 4 son nuevos («vs cero»). Se declaran los 10
y la convención del §28 de la cola decide cuántos suma el registro.

---
Herramienta de análisis — no constituye asesoría financiera. **No es el
veredicto de la 5.1.**
