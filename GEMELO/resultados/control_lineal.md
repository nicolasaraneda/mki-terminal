# ⚠ ESTO NO ES EL VEREDICTO DE LA ETAPA 5.1

Es una **corrida de investigación del control lineal del retador**
(Etapa 6.0.0 WS2b, §4.3 del pre-registro). El backtest con veredicto
del campeón es otra cosa: su gatillo sigue siendo decisión humana y
**sigue sin cumplirse** (N=228 sí, cambio de régimen no).

---

# Control lineal — el conjunto de información expandido, ¿trae señal?

- Generado: 2026-08-26T02:57:44.313484+00:00
- Filas selladas evaluadas: **223** (convención `excluir_cero (§2.8)`)
- Panel de entrenamiento: 15033 filas

## Parámetros sellados

| Parámetro | Valor |
|---|---|
| **N intentos declarado (DSR)** | **9** — 3 configuraciones (C1,C2,C3) + 6 baselines B0-B5 |
| Embargo | 5 días |
| Ventana de entrenamiento | EXPANSIVA (todo el pasado disponible) |
| Alphas de la CV | [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0] |
| Pliegues de la CV temporal | 3 |
| Mínimo de entrenamiento | 250 filas |
| Semilla del bootstrap | 20260826 |
| Bloque del bootstrap | 20 |
| Alpha del bootstrap | 0.05 |
| Años de datos | 8 |

**La búsqueda de alpha NO suma a N.** Se resuelve por CV temporal
dentro de cada ventana de entrenamiento, sin tocar jamás una fila de
evaluación. Lo que el DSR debe contar son las decisiones tomadas
MIRANDO el resultado de evaluación, y ésta no lo es.

### Alphas efectivamente elegidos por fold

```
{"C1": [100.0], "C2": [100.0], "C3": [0.03, 3.0, 10.0, 30.0, 100.0, 300.0], "CAMPEON": []}
```

## ASIMETRÍA DECLARADA — no supuesta

El retador entrena sobre **años** de historia con ventana expansiva;
el campeón usa **120 sesiones rodantes**. Es una diferencia real de
maquinaria y es **parte de lo que se está midiendo**, no un detalle
de implementación. Por eso existe C1: usa el MISMO conjunto de
información que el campeón (el SOX, t y t-1) con la maquinaria nueva.
**La comparación que responde la pregunta real es C2 contra C1**, no
C2 contra el campeón — ésta última mezcla información y maquinaria.

## Las configuraciones

- **C1** — ridge agrupado, SOLO el SOX (t y t-1) — CONTROL DE INFORMACIÓN: mismo insumo que el campeón, maquinaria nueva
- **C2** — ridge agrupado, catálogo completo (16 features)
- **C3** — ridge por ticker, catálogo completo (16 features)

## Resultados por configuración

| config | n | acierto_pct | base_pct | ventaja_pp | mcnemar_b01 | mcnemar_b10 | mcnemar_p | mae | crps | sharpe_ls_sin_costos | dias | alpha_mediana | n_train_mediano |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 215 | 67.4 | 61.4 | 6.0 | 62 | 49 | 0.2547 | 3.2146 | 2.6347 | 5.73 | 30 | 100.0 | 14855.0 |
| C2 | 215 | 70.2 | 61.4 | 8.8 | 72 | 53 | 0.1074 | 3.0587 | 2.5261 | 5.29 | 30 | 100.0 | 12731.0 |
| C3 | 215 | 72.6 | 61.4 | 11.2 | 68 | 44 | 0.0298 | 2.9444 | 2.4485 | 5.86 | 30 | 30.0 | 1578.0 |
| CAMPEON | 223 | 65.9 | 61.9 | 4.0 | 64 | 55 | 0.4633 | 3.1244 | 2.3991 | 5.491 | 31 |  |  |

La baseline «siempre al alza» sobre estas mismas filas está en la
columna `base_pct`. `sharpe_ls_sin_costos` es un proxy económico de
primera pasada (long-short equiponderado, **sin costos**): es
optimista por construcción y NO es la prueba del benchmark
obligatorio (§6.1 V6, que exige SMH y 25 pb por lado).

## Comparaciones pareadas

Sobre las filas que **ambas** configuraciones predijeron. `delta_mae`
> 0 significa que A tiene MENOS error que B; su IC sale del bootstrap
circular de bloques.

| par | n | acierto_a_pct | acierto_b_pct | ventaja_pp | mcnemar | mcnemar_p | mae_a | mae_b | delta_mae | delta_mae_ic | ic_excluye_cero |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C2 vs C1 | 215 | 70.2 | 67.4 | 2.8 | 18 vs 12 | 0.3613 | 3.0587 | 3.2146 | 0.1559 | [-0.0389, 0.4232] | False |
| C3 vs C1 | 215 | 72.6 | 67.4 | 5.1 | 27 vs 16 | 0.1273 | 2.9444 | 3.2146 | 0.2702 | [0.0665, 0.4729] | True |
| C3 vs C2 | 215 | 72.6 | 70.2 | 2.3 | 12 vs 7 | 0.3588 | 2.9444 | 3.0587 | 0.1143 | [0.0564, 0.3071] | True |
| C1 vs CAMPEON | 215 | 67.4 | 67.4 | 0.0 | 0 vs 0 | 1.0 | 3.2146 | 3.0819 | -0.1327 | [-0.3506, 0.0376] | False |
| C2 vs CAMPEON | 215 | 70.2 | 67.4 | 2.8 | 18 vs 12 | 0.3613 | 3.0587 | 3.0819 | 0.0232 | [-0.2041, 0.2418] | False |
| C3 vs CAMPEON | 215 | 72.6 | 67.4 | 5.1 | 27 vs 16 | 0.1273 | 2.9444 | 3.0819 | 0.1374 | [-0.1068, 0.3267] | False |

## Lectura

**1. El campeón y C1 aciertan la dirección en las MISMAS filas** (McNemar 0 vs 0 sobre n=215). No es casualidad ni error: la predicción del campeón es βᵢ·SOX con βᵢ>0, así que su signo ES el signo del retorno del SOX — y C1, ridge agrupada sobre el mismo insumo, lo reproduce exactamente. Consecuencia: **cualquier diferencia direccional entre C2/C3 y el campeón es INFORMACIÓN, no maquinaria.** Es justo lo que C1 existía para separar.

**2. La pregunta real —C2 contra C1— no da nada.** Ventaja 2.8 pp con McNemar p=0.3613, y el IC del ΔMAE [-0.0389, 0.4232] **incluye el cero**. Con el mismo motor y la misma ventana, añadir las catorce features nuevas a las dos del SOX **no produce una mejora detectable**, ni en dirección ni en magnitud.

**3. Lo que sí mueve la aguja es la estructura por ticker, y solo en magnitud.** C3 contra C1: ΔMAE 0.2702 con IC [0.0665, 0.4729], que **excluye el cero**. En dirección, en cambio, p=0.1273: no significativo. Coincide con la §2.5 — la contribución medible está en la magnitud, no en el signo.

**4. El único p<0.05 del experimento no sobrevive a R2.** C3 contra la baseline sobre la ventana completa marca 11.2 pp con p=0.0298. Excluyendo 15–23 jul cae a 1.8 pp con p=0.8321. **La significancia venía de la misma ventana afortunada que sostiene la del campeón**, que es exactamente lo que R2 fue escrito para detectar.

**5. Bajo R2 no pasa nadie.** Pierden su ventaja al excluir esa ventana: C1, C2, CAMPEON. El campeón incluido. Ninguna configuración supera V1 (McNemar p<0.05) con R2 aplicado.

**6. El resultado es NEGATIVO, y se publica tal cual.** El §6.3 del pre-registro lo dice: un retador que no supera al campeón, y un campeón que no supera a una constante, es un resultado. No se probó una cuarta variante buscando el positivo — esa tentación es literalmente el sesgo que el DSR mide, y habría subido N a 10.

## R2 del §6.2 aplicado a cada configuración

R2 descarta a quien pierda su ventaja al excluir la ventana 2026-07-15–2026-07-23, que sostiene casi toda la ventaja del campeón (§2.2). Se aplica por FECHAS, no por índice de bloque (§2.8.2). Al propio campeón esta prueba lo deja en ventaja NEGATIVA sobre las 223 filas — es una valla que hoy nadie tenía superada.

| config | n | acierto_pct | base_pct | ventaja_pp | mcnemar_p | mae | sobrevive_R2 |
|---|---|---|---|---|---|---|---|
| C1 | 171 | 63.7 | 66.7 | -2.9 | 0.6567 | 3.4171 | False |
| C2 | 171 | 66.1 | 66.7 | -0.6 | 1.0 | 3.2462 | False |
| C3 | 171 | 68.4 | 66.7 | 1.8 | 0.8321 | 3.1406 | True |
| CAMPEON | 179 | 62.0 | 67.0 | -5.0 | 0.3964 | 3.3522 | False |

## PSR y DSR

**Aviso que manda sobre la tabla:** con menos de 60 días, un Sharpe ANUALIZADO no es una estimación sino un artefacto de multiplicar por √252, y el PSR y el DSR **saturan en 1.0000**. Un DSR de 1.000 NO significa que V5 (DSR ≥ 0.95) esté superado: significa que el instrumento no aplica a esta muestra. Por eso se reportan como NO INTERPRETABLE en vez de emitir el número.

| config | sharpe | dias | interpretable | psr_vs_cero | sr0_deflacionado | dsr | N_intentos | V_intentos |
|---|---|---|---|---|---|---|---|---|
| C1 | 5.73 | 30 | False | NO INTERPRETABLE | 0.385 | NO INTERPRETABLE | 9 | 0.0641 |
| C2 | 5.29 | 30 | False | NO INTERPRETABLE | 0.385 | NO INTERPRETABLE | 9 | 0.0641 |
| C3 | 5.86 | 30 | False | NO INTERPRETABLE | 0.385 | NO INTERPRETABLE | 9 | 0.0641 |
| CAMPEON | 5.491 | 31 | False | NO INTERPRETABLE | 0.385 | NO INTERPRETABLE | 9 | 0.0641 |

**`V_intentos` está SUBESTIMADA y por tanto el DSR es una cota
superior optimista.** Se estima con la varianza de los Sharpe
disponibles aquí; los de las seis baselines B0→B5 vienen de una
corrida legacy con bootstrap no circular y sin embargo
(DECISIONES.md §28.5), así que no se mezclan. Un V menor da un SR0
menor y un DSR más alto del que corresponde.

**El CRPS usa una predictiva NORMAL**, declarado como primera
pasada: ridge entrega punto más varianza residual. La §2.7 ya mostró
colas más gruesas que la normal en este objetivo, así que este CRPS
es una cota optimista. La densidad con colas (Student-t) es el Nivel
4 del retador, no de este control.

## Series descartadas por cobertura

| ticker | cobertura |
|---|---|
| ^VIX3M | 0.0 |

---
Herramienta de análisis — no constituye asesoría financiera.
Diseño congelado en GEMELO/DISEÑO.md. **No es el veredicto de la 5.1.**
