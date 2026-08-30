# ⚠ ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1

Es una corrida de investigación (Etapa 6.0.0 WS5). El veredicto de
la 5.1 es el criterio **escalonado capa-contra-capa sobre B0→B5**,
con sus reglas congeladas en el GATE B, y su ejecución es **decisión
humana**. Aquí NO se calcula ni se emite juicio sobre B0→B5.

---

# ⚠ Y ESTO ES POST-HOC. Sin eufemismos.

**La hipótesis del relevo asiático se formó DESPUÉS de ver el
desglose por bolsa del WS4.** No es confirmatoria: es exploratoria.
Una hipótesis construida sobre un patrón ya visto **no se confirma
con los datos que la sugirieron**. El techo alcanzable es
«NO REFUTADA».

El pre-registro —N, configuraciones y regla de decisión— se escribió
y se dejó en el árbol **antes** de correr nada:
[`preregistro_ws5.md`](preregistro_ws5.md).

---

# La hipótesis del relevo asiático

- Generado: 2026-08-30T19:22:28.427902+00:00
- Ventana: **2018-08-28 → 2026-08-27** · 2077 fechas de emisión · 15042 filas de panel
- Corte del holdout: **2025-01-21** (1661 fechas de exploración · **416 de holdout**)

---

## VEREDICTO

# REFUTADA (ausencia)

E2 no mejora a E1 en Fráncfort: el relevo no aporta donde el mecanismo lo exige.

El criterio primario, sobre el holdout:

| par | n | acierto_a_pct | acierto_b_pct | ventaja_pp | mcnemar | mcnemar_p | mae_a | mae_b | delta_mae | ic_excluye_cero | ic_sharpe_dmae | ic_delta_mae_pp | ic_pp_excluye_cero | estrato | porcion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2 vs E1 | 393 | 53.4 | 59.0 | -5.6 | 85 vs 107 | 0.1296 | 1.3861 | 1.3513 | -0.0347 | False | [-0.1586, 0.0432] | [-0.0914, 0.0263] | False | XETR | holdout |
| E2 vs E1 | 2548 | 55.3 | 72.7 | -17.5 | 321 vs 766 | 0.0 | 1.9348 | 1.5588 | -0.376 | True | [-0.363, -0.2581] | [-0.4663, -0.2902] | True | ASIA | holdout |

---

## Lo que este experimento NO puede probar — y hay que decirlo antes

La hipótesis dice: «entre el cierre del SOX y la apertura de
Fráncfort, Asia operó una sesión entera». **Esa sesión es la del día
D+1, y NO es conocible a la emisión.**

Emisión del sistema: **2026-08-26T22:15:00+00:00** (22:15 UTC del día D). Apertura de XETR de la sesión objetivo: **2026-08-27T07:00:00+00:00**, es decir **8.75 h después**.

| serie | barra | cierre_utc | h_antes_de_la_emision | h_antes_de_apertura_XETR | conocible_a_la_emision |
|---|---|---|---|---|---|
| ^SOX | D | 2026-08-26T21:00:00+00:00 | 1.25 | 10.0 | True |
| ^SOX | D+1 | 2026-08-27T21:00:00+00:00 | -22.75 | -14.0 | False |
| ^KS11 | D | 2026-08-26T06:30:00+00:00 | 15.75 | 24.5 | True |
| ^KS11 | D+1 | 2026-08-27T06:30:00+00:00 | -8.25 | 0.5 | False |
| ^TWII | D | 2026-08-26T05:30:00+00:00 | 16.75 | 25.5 | True |
| ^TWII | D+1 | 2026-08-27T05:30:00+00:00 | -7.25 | 1.5 | False |
| ^N225 | D | 2026-08-26T06:00:00+00:00 | 16.25 | 25.0 | True |
| ^N225 | D+1 | 2026-08-27T06:00:00+00:00 | -7.75 | 1.0 | False |

Léase la columna `h_antes_de_la_emision`: **un número negativo
significa que esa barra aún no existía cuando el sistema emitió.**

De ahí salen dos hechos que cambian cómo debe leerse todo lo que
sigue:

1. **La sesión asiática fresca —la del día D+1, que cierra ~30 min
   antes de que Fráncfort abra— NO es conocible a la emisión.** El
   relato del relevo describe exactamente esa sesión. Este
   experimento **no puede** probarla sin romper la restricción de
   emisión del sistema.
2. **El insumo asiático que SÍ es conocible es el MÁS VIEJO de los
   dos.** A las 22:15 UTC del día D el `^SOX` de D tiene ~1.25 h y
   el `^KS11` de D tiene ~15.75 h. Peor: el `^KS11` de D cerró
   **antes** que el `^SOX` de D, así que reacciona al SOX de D−1 —
   que E1 ya lleva dentro como `sox_t1`.

> **Consecuencia para la lectura:** lo que se prueba aquí es la
> versión **débil y compatible con el sistema** de la hipótesis:
> ¿aporta la componente idiosincrática asiática del día D algo por
> encima del SOX? Un resultado NULO refuta **esa** versión, y **no**
> refuta el mecanismo del relevo con información fresca — que
> seguiría siendo indemostrable sin mover la hora de emisión, y
> mover la hora de emisión es territorio del modelo congelado.

---

## La trampa, y cómo se evitó

Para un objetivo asiático su **propio** índice local es casi
circular: Samsung está dentro del KOSPI, TSMC dentro del TWSE. Sin
excluirlo, E2 luciría espectacular en Asia **por la razón
equivocada** y la prueba de simetría concluiría lo contrario de lo
que los datos dicen. Va como test, no como comentario.

| bolsa | indice_excluido | E2 |
|---|---|---|
| XETR | gdaxi_ret | ['ks11_ret', 'twii_ret', 'n225_ret'] |
| XKRX | ks11_ret | ['twii_ret', 'n225_ret'] |
| XTAI | twii_ret | ['ks11_ret', 'n225_ret'] |
| XTKS | n225_ret | ['ks11_ret', 'twii_ret'] |

## Parámetros sellados

| Parámetro | Valor |
|---|---|
| **N intentos declarado (DSR)** | **25** |
| Desglose | 13 acumulados hasta WS3 + 12 (E1,E2,E3 × {XETR,ASIA} × {exploración,holdout}) |
| Regla de conteo | un intento = (configuración × ventana de evaluación) con resultado reportable |
| **Convención del empate** | **excluir_cero (§2.8) — aplicada, a diferencia del WS3** |
| Embargo | 5 días |
| Ventana de entrenamiento | EXPANSIVA (todo el pasado disponible) |
| Ajuste | ridge agrupada DENTRO de la bolsa del objetivo |
| Alphas de la CV | [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0] |
| Pliegues de la CV temporal | 3 |
| Mínimo de entrenamiento | 250 filas |
| Semilla / bloque / alpha del bootstrap | 20260826 / 20 / 0.05 |
| Fracción del holdout | 0.2 (corte 2025-01-21) |
| Años de datos | 8 |

**El N sube de 13 a 25.** Doce
intentos nuevos salen de aplicar la regla congelada
**mecánicamente**: tres configuraciones × dos estratos × dos
porciones, y las doce son reportables. Contarlas de otro modo sería
elegir el N que favorece al DSR, que es justo lo que el DSR existe
para castigar. **No se probó una cuarta configuración.**

## El holdout, y su cuarentena PARCIAL

La cuarentena aquí es **procedimental**: configuraciones, regla de
decisión y N quedaron fijados antes de correr, así que no hay nada
que ajustar mirando el holdout.

**Pero está contaminado y se declara:** la observación que generó la
hipótesis —el +2.5 pp de Fráncfort del WS4— se midió sobre la
ventana **completa**, holdout incluido. El holdout está en
cuarentena frente a las decisiones de **este** experimento, no
frente al hecho que lo motivó. Llamarla completa sería mentir.

## Resultados por configuración

| config | n | acierto_pct | base_pct | ventaja_pp | mcnemar_b01 | mcnemar_b10 | mcnemar_p | mae | crps | sharpe_ls_sin_costos | dias | alpha_mediana | n_train_mediano | estrato | porcion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | 1344 | 60.4 | 54.8 | 5.6 | 226 | 151 | 0.0001 | 0.9581 | 0.7598 | 3.21 | 1344 | 100.0 | 921 | XETR | exploracion |
| E2 | 1324 | 52.5 | 54.8 | -2.3 | 103 | 134 | 0.0513 | 1.0009 | 0.7836 | 0.527 | 1324 | 1000.0 | 911 | XETR | exploracion |
| E3 | 1323 | 59.0 | 54.9 | 4.2 | 252 | 197 | 0.0108 | 0.9681 | 0.7623 | 2.959 | 1323 | 300.0 | 909 | XETR | exploracion |
| E1 | 399 | 58.6 | 55.1 | 3.5 | 73 | 59 | 0.2578 | 1.3688 | 1.0391 | 3.192 | 399 | 0.03 | 1793 | XETR | holdout |
| E2 | 393 | 53.4 | 55.2 | -1.8 | 49 | 56 | 0.5582 | 1.3861 | 1.0593 | 0.999 | 393 | 1000.0 | 1771 | XETR | holdout |
| E3 | 393 | 62.1 | 55.2 | 6.9 | 92 | 65 | 0.038 | 1.3323 | 1.011 | 3.059 | 393 | 300.0 | 1769 | XETR | holdout |
| E1 | 9595 | 72.8 | 54.1 | 18.7 | 3041 | 1249 | 0.0 | 0.8832 | 0.6667 | 10.475 | 1566 | 100.0 | 2052 | ASIA | exploracion |
| E2 | 9505 | 51.9 | 54.1 | -2.2 | 787 | 996 | 0.0 | 1.1916 | 0.8888 | 0.824 | 1557 | 1000.0 | 2028 | ASIA | exploracion |
| E3 | 9481 | 74.1 | 54.1 | 20.0 | 3118 | 1226 | 0.0 | 0.8648 | 0.653 | 10.966 | 1554 | 100.0 | 2026 | ASIA | exploracion |
| E1 | 2574 | 72.5 | 56.6 | 15.9 | 701 | 292 | 0.0 | 1.5623 | 1.1891 | 9.913 | 415 | 100.0 | 6104 | ASIA | holdout |
| E2 | 2548 | 55.3 | 56.7 | -1.4 | 113 | 149 | 0.0306 | 1.9348 | 1.4833 | 1.254 | 411 | 1000.0 | 6050 | ASIA | holdout |
| E3 | 2548 | 72.7 | 56.7 | 16.1 | 730 | 321 | 0.0 | 1.5106 | 1.1526 | 9.618 | 411 | 100.0 | 6042 | ASIA | holdout |

## Comparaciones pareadas

Sobre las filas que **ambas** configuraciones predijeron.
`delta_mae > 0` significa que A tiene MENOS error que B.

| par | n | acierto_a_pct | acierto_b_pct | ventaja_pp | mcnemar | mcnemar_p | mae_a | mae_b | delta_mae | ic_excluye_cero | ic_sharpe_dmae | ic_delta_mae_pp | ic_pp_excluye_cero | estrato | porcion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2 vs E1 | 1324 | 52.5 | 60.3 | -7.9 | 204 vs 308 | 0.0 | 1.0009 | 0.9597 | -0.0412 | True | [-0.2085, -0.0674] | [-0.0591, -0.0217] | True | XETR | exploracion |
| E3 vs E1 | 1323 | 59.0 | 60.3 | -1.3 | 150 vs 167 | 0.3688 | 0.9681 | 0.9601 | -0.0079 | False | [-0.0944, 0.0267] | [-0.0209, 0.006] | False | XETR | exploracion |
| E3 vs E2 | 1323 | 59.0 | 52.5 | 6.6 | 212 vs 125 | 0.0 | 0.9681 | 1.0015 | 0.0334 | True | [0.0653, 0.1928] | [0.0175, 0.0487] | True | XETR | exploracion |
| E2 vs E1 | 393 | 53.4 | 59.0 | -5.6 | 85 vs 107 | 0.1296 | 1.3861 | 1.3513 | -0.0347 | False | [-0.1586, 0.0432] | [-0.0914, 0.0263] | False | XETR | holdout |
| E3 vs E1 | 393 | 62.1 | 59.0 | 3.1 | 46 vs 34 | 0.2188 | 1.3323 | 1.3513 | 0.0191 | False | [-0.0508, 0.1568] | [-0.0181, 0.0584] | False | XETR | holdout |
| E3 vs E2 | 393 | 62.1 | 53.4 | 8.7 | 90 vs 56 | 0.0063 | 1.3323 | 1.3861 | 0.0538 | True | [0.0124, 0.2077] | [0.0056, 0.1128] | True | XETR | holdout |
| E2 vs E1 | 9493 | 52.0 | 72.9 | -20.9 | 1030 vs 3011 | 0.0 | 1.1909 | 0.8812 | -0.3098 | True | [-0.419, -0.3424] | [-0.338, -0.2858] | True | ASIA | exploracion |
| E3 vs E1 | 9481 | 74.1 | 72.9 | 1.2 | 442 vs 328 | 0.0 | 0.8648 | 0.8812 | 0.0164 | True | [0.0483, 0.1025] | [0.0103, 0.0228] | True | ASIA | exploracion |
| E3 vs E2 | 9481 | 74.1 | 52.0 | 22.1 | 3257 vs 1162 | 0.0 | 0.8648 | 1.1911 | 0.3263 | True | [0.3489, 0.4205] | [0.3004, 0.3545] | True | ASIA | exploracion |
| E2 vs E1 | 2548 | 55.3 | 72.7 | -17.5 | 321 vs 766 | 0.0 | 1.9348 | 1.5588 | -0.376 | True | [-0.363, -0.2581] | [-0.4663, -0.2902] | True | ASIA | holdout |
| E3 vs E1 | 2548 | 72.7 | 72.7 | 0.0 | 140 vs 140 | 1.0 | 1.5106 | 1.5588 | 0.0482 | True | [0.056, 0.1529] | [0.0247, 0.0729] | True | ASIA | holdout |
| E3 vs E2 | 2548 | 72.7 | 55.3 | 17.5 | 766 vs 321 | 0.0 | 1.5106 | 1.9348 | 0.4242 | True | [0.2977, 0.3932] | [0.3361, 0.5176] | True | ASIA | holdout |

### ⚠ Hallazgo colateral: el IC del ΔMAE venía en otra escala

`cl.comparar` —la función que el WS2b escribió y el WS3 heredó—
acompaña un `delta_mae` en **pp** con un intervalo salido de
`inf.bootstrap_bloques`, que es el IC del **Sharpe** (media/desv).
Son dos escalas distintas, y se ve a simple vista: **en 8 de los 12
pares de esta corrida el punto estimado caía FUERA de su propio
intervalo.**

**Ninguna conclusión previa cambia.** Las decisiones se tomaron con
`ic_excluye_cero`, que es **exactamente** equivalente en ambas
escalas: `sd > 0` conserva el signo réplica a réplica, así que el
evento «el cuantil α/2 está sobre cero» depende solo de la
proporción de réplicas sobre cero, y ésa es idéntica para la media
y para media/desv. Lo que estaba mal era el **número impreso**, no
el veredicto.

Aquí se publican los dos, con el nombre que dice qué es cada uno:
`ic_sharpe_dmae` (la maquinaria del WS2b/WS3, para que las cifras
sigan siendo comparables) e **`ic_delta_mae_pp`** (el intervalo de
lo que la columna dice ser, vía `inf.bootstrap_media`, que comparte
sorteo y semilla con el otro).

**No se corrigió ningún reporte anterior** — eso es criterio de
Nicolás y queda como pregunta abierta.
## Desglose por bolsa — DESCRIPTIVO, no decisorio

El ajuste **tiene** que ser por bolsa (la exclusión del índice
propio depende de ella), pero el resultado reportable es el del
estrato. Esta tabla se publica para que el lector vea la
heterogeneidad; **ninguna decisión se toma mirándola.** Si alguna se
tomara, N sube de 25 a 31 y hay que decirlo.

| par | n | acierto_a_pct | acierto_b_pct | ventaja_pp | mcnemar | mcnemar_p | mae_a | mae_b | delta_mae | ic_excluye_cero | ic_sharpe_dmae | ic_delta_mae_pp | ic_pp_excluye_cero | bolsa | porcion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2 vs E1 | 1324 | 52.5 | 60.3 | -7.9 | 204 vs 308 | 0.0 | 1.0009 | 0.9597 | -0.0412 | True | [-0.2085, -0.0674] | [-0.0591, -0.0217] | True | XETR | exploracion |
| E2 vs E1 | 393 | 53.4 | 59.0 | -5.6 | 85 vs 107 | 0.1296 | 1.3861 | 1.3513 | -0.0347 | False | [-0.1586, 0.0432] | [-0.0914, 0.0263] | False | XETR | holdout |
| E2 vs E1 | 2669 | 53.4 | 71.3 | -18.0 | 319 vs 799 | 0.0 | 0.9936 | 0.7758 | -0.2178 | True | [-0.3793, -0.2816] | [-0.2516, -0.1848] | True | XKRX | exploracion |
| E2 vs E1 | 726 | 56.3 | 73.7 | -17.4 | 82 vs 208 | 0.0 | 2.2266 | 1.8228 | -0.4037 | True | [-0.5003, -0.2707] | [-0.5381, -0.2721] | True | XKRX | holdout |
| E2 vs E1 | 1236 | 54.1 | 72.3 | -18.2 | 132 vs 357 | 0.0 | 1.0528 | 0.7666 | -0.2862 | True | [-0.5035, -0.3744] | [-0.3333, -0.2423] | True | XTAI | exploracion |
| E2 vs E1 | 360 | 58.9 | 71.1 | -12.2 | 44 vs 88 | 0.0002 | 1.2534 | 0.9438 | -0.3096 | True | [-0.4079, -0.2562] | [-0.4048, -0.2233] | True | XTAI | holdout |
| E2 vs E1 | 5588 | 50.9 | 73.7 | -22.8 | 579 vs 1855 | 0.0 | 1.3157 | 0.9568 | -0.3589 | True | [-0.4479, -0.3379] | [-0.3988, -0.3221] | True | XTKS | exploracion |
| E2 vs E1 | 1462 | 53.8 | 72.6 | -18.8 | 195 vs 470 | 0.0 | 1.9577 | 1.5791 | -0.3786 | True | [-0.355, -0.2085] | [-0.5216, -0.2507] | True | XTKS | holdout |

## Series descartadas por cobertura

| ticker | cobertura |
|---|---|
| ^VIX3M | 0.0 |

---
Herramienta de análisis — no constituye asesoría financiera.
Diseño congelado en GEMELO/DISEÑO.md. **No es el veredicto de la
5.1** y **no calcula el veredicto escalonado de B0→B5.**
**POST-HOC: exploratorio, no confirmatorio.**
