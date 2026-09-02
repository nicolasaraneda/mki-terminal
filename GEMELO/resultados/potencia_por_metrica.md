# La métrica que maximiza información por día sellado — Frente E (PROPUESTA)

> **PROPUESTA — Frente E v2, octava corrida; reescrito tras el dictamen E (NO CONCLUYENTE sobre las cifras operativas)** · generado 2026-09-02T18:59:47.809708+00:00 · `python GEMELO/simulador/potencia_por_metrica.py`

Generador de 9 pp del Frente A (b = 1.1562, c = 4.6875, δ verdad 9.26 pp). En el simulador el mismo campeón tiene MAE 2.669 contra 3.146 de predecir cero (real sellado: 2.488 contra 2.925); σ_pred implícita del intervalo 80% sellado 4.305 pp, σ que calibraría 3.866 pp; climatología N(0.837, 4.388).

## Ventana sellada: z observado por métrica (IC de clúster de día)

| métrica | punto | IC95 (t de clúster) | z | días | días para 0,80 al efecto observado [IC; ∞ = el IC del efecto contiene el cero] |
|---|---|---|---|---|---|
| DIR | 0.0935 | [-0.0779, 0.2649] | 1.11 | 35 | **223 [28, ∞]** |
| MAE | 0.4372 | [-0.0872, 0.9616] | 1.69 | 35 | **96 [20, ∞]** |
| CRPS | 0.2916 | [-0.0443, 0.6275] | 1.76 | 35 | **88 [19, ∞]** |

## Simulador: potencia por horizonte (permutación de signo por día, α = 0,05), σ_pred del intervalo sellado

| días | DIR | MAE | CRPS |
|---|---|---|---|
| 35 | 0.18 [0.149, 0.216] | 0.586 [0.542, 0.628] | 0.426 [0.383, 0.47] |
| 73 | 0.312 [0.273, 0.354] | 0.9 [0.871, 0.923] | 0.76 [0.721, 0.795] |
| 125 | 0.48 [0.437, 0.524] | 0.986 [0.971, 0.993] | 0.926 [0.9, 0.946] |
| 250 | 0.81 [0.773, 0.842] | 1.0 [0.992, 1.0] | 0.998 [0.989, 1.0] |
| 475 | 0.962 [0.941, 0.976] | 1.0 [0.992, 1.0] | 1.0 [0.992, 1.0] |

Con la σ calibrada (lo que el modelo tendría si su intervalo no fuera 1,84× ancho):

| días | DIR | MAE | CRPS |
|---|---|---|---|
| 73 | 0.312 [0.273, 0.354] | 0.9 [0.871, 0.923] | 0.832 [0.797, 0.862] |
| 250 | 0.81 [0.773, 0.842] | 1.0 [0.992, 1.0] | 1.0 [0.992, 1.0] |


## Correcciones tras el dictamen E (2-sep)

- Ancla: cadena LOCAL a CORTE_REGLA_FIRMADA (31-ago) CON la regla de dedup firmada: +9,3 pp — NO el +6,45 pp publicado (rama sin dedup); hay una tercera rama (+14,3 pp) en cola_decisiones.md §2a-ter.
- ESTIMADAS EN MUESTRA sobre las mismas filas que puntúan (sesgo: la climatología ajustada en muestra favorece a la baseline; σ_pred sellada favorece al modelo sólo si está calibrada).
- CRPS y MAE no son métricas independientes: con σ_pred ≈ sd_clim casi toda la ganancia de CRPS es la media; se reportan como UNA familia (magnitud), no como dos corroboraciones.
- La constante μ (cero información) recupera el 7.3% de la ganancia de MAE: «predecir cero» no es la baseline pareada de «siempre al alza».
- z e IC por **t de clúster** (gl = k−1), no percentil: el percentil sub-cubre y daba un z ~9% inflado.

| métrica | punto | IC95 t de clúster | z | días para 0,80 [IC] | días al +6,45 pp publicado | R2 (sin 15–23 jul): punto · z · días [IC] |
|---|---|---|---|---|---|---|
| DIR | 0.0935 | [-0.0779, 0.2649] | 1.11 | **223 [28, ∞]** | 470 | 0.0248 · 0.29 · 2728 [42, ∞] |
| MAE | 0.4372 | [-0.0872, 0.9616] | 1.69 | **96 [20, ∞]** | — | 0.3444 · 1.14 · 175 [22, ∞] |
| CRPS | 0.2916 | [-0.0443, 0.6275] | 1.76 | **88 [19, ∞]** | — | 0.2061 · 1.07 · 200 [23, ∞] |

**Banda de sensibilidad de la potencia a 73 días (MAE / CRPS / DIR):** generador_9pp: ganancia MAE 0.4767 pp → MAE 0.9 [0.871, 0.923], CRPS 0.76, DIR 0.312; efecto_observado: ganancia MAE 0.4372 pp → MAE 0.864 [0.831, 0.891], CRPS 0.66, DIR 0.294; efecto_bajo_R2: ganancia MAE 0.3444 pp → MAE 0.704 [0.663, 0.742], CRPS 0.498, DIR 0.21
La potencia de MAE a 73 días NO es un número: es la banda generador / observado / bajo R2. R2 es criterio congelado de rechazo, no una sensibilidad opcional.

Intentos del DSR: incremento **2** (DIR es el endpoint congelado (no cuenta); la magnitud |g|−|p−g| ya está en el tramo ESTIM (no se cuenta dos veces); cuentan CRPS y su variante sigma_calibrada).

