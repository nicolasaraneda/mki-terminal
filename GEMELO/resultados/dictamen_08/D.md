# Dictamen del `estadistico-adversario` · Frente D (predicción transversal) · 2-sep-2026

> Texto del agente, guardado por el orquestador. Sobre `transversal.py` con la
> prueba abierta (v2, 637 fechas). La Enmienda 2 de `preregistro/frente_D.md`
> y la corrida posterior aplican los bloqueantes.

**VEREDICTO juzgado:** «El modelo ordena dentro del día: ρ̄ = 0,240 fuera de muestra, p = 0,0002.»

## Cifra reportada / verificada

Sellada ρ̄ = 0,2294 (35 fechas / 259 filas, p_perm 0,0007) reproduce; ajuste causal 0,2484 (1.102 fechas) reproduce; prueba 0,2403 (637 fechas) reproduce el punto, **no el intervalo**: «0,240 [0,201, 0,273]» empareja el punto de v2 con el intervalo de v1 (626 fechas, 0,2373 [0,2007, 0,2727]); el vigente es **[0,2062, 0,2756]**. Segunda cifra que no reproduce: la Enmienda 1 del pre-registro dice «1.334 fechas» para el ajuste causal; el causal tiene **1.071** — 1.334 son las fechas de la versión in-sample que el auditor rechazó.

## Intervalo

| ventana | percentil iid (publicado) | bloques 20 | t de clúster gl = k−1 |
|---|---|---|---|
| sellada, n = 35 | [0,0345, 0,4254] | [0,1066, 0,2709] **degenerado** (2 bloques) | **[0,0252, 0,4335]** |
| sellada sin bloque 1, n = 29 | [−0,0291, 0,4024] | degenerado | **[−0,0391, 0,4189]** |
| prueba, n = 637 | [0,2045, 0,2733] | [0,2096, 0,2694] | [0,2055, 0,2751] |

Autocorrelación de ρ_d en la larga ≈ 0 (lags 1–20 entre −0,09 y +0,07): el iid no infla, pero es un hallazgo, no una licencia. **El p = 0,0007 de la sellada y su IC no dicen lo mismo:** SE nula de permutación 0,0685 → p 0,0008; SE muestral 0,1005 → z 2,28 → **p 0,0224**. Y «p = 0,0002» en ajuste y prueba es el piso de la rejilla (1/4001): se reporta «p < 0,00025».

## Denominador

El script permuta dentro del día contra ρ̄ = 0. El honesto para «el modelo ordena» es **un orden cualquiera de los mismos 8 tickers**: permutando el vector β entre tickers (2.000 réplicas) la nula tiene media 0,0009, sd **0,0978**, q2,5/97,5 = [−0,188, +0,186]; **p bilateral = 0,0025**; sólo el 1,3 % de los órdenes aleatorios supera 0,20. El hallazgo sobrevive, pero el p honesto es 12× el publicado y la SE respecto de «qué orden» es 5× la del bootstrap de fechas: **la unidad de replicación de la afirmación es el ORDENAMIENTO, y n = 1.**

## Intentos contados

D no está en `REGISTRO_INTENTOS` (N = 100). Los «2» viven en prosa y dependen de la convención: bajo ESTIM 2; bajo la de C («por estadístico publicado») **6** (ρ̄, τ̄, fracción positiva × 3 ventanas). Dos convenciones conviven en la misma bitácora: eso es el hallazgo.

## Dictamen por punto

1. **Nula within-day — NO SOSTIENE como nula principal.** Identidad verificada exacta: ρ_d = sign(S_d)·spearman(orden β, gap) sobre las 637 fechas — **el modelo transversal es un vector fijo de 8 β más un bit por día**; la magnitud del SOX es irrelevante para ρ_d. A favor del frente: partido por signo del SOX, ρ̄ = +0,2415 [0,198, 0,285] (S=+1, n=366) y +0,2387 [0,182, 0,295] (S=−1, n=271): simétrico, descarta el artefacto de nivel.
2. **β causal ≠ motor — NO SOSTIENE «el modelo».** Ventana (expansiva/fija vs rodante 120) y regresando (gap vs cierre-a-cierre) distintos. Spearman entre el vector β sellado y el del proxy: **+0,45, p exacto 0,2675** (no distinguibles de no relacionados). El orden del CAMPEÓN en la prueba: **ρ̄ = 0,1795 [0,146, 0,213]**, bajo la vara 0,20; proxy − campeón = +0,0608 [0,025, 0,096] (excluye el cero; el contrafactual es cota optimista: esas β se estimaron en 2026).
3. **Potencia — la sellada mide bajo su umbral:** SE observada 0,1005 → MDE 80 % = **0,28**, efecto 0,23. 20/35 fechas con ρ_d > 0 = 57,1 % [40,9, 72,0] contiene 50 %. Dejar-uno-fuera (medido por mí): estable (peor prueba: sin IFX.DE 0,2053; sellada: sin 8035.T 0,1903), pero en la sellada 6 de 8 exclusiones caen bajo 0,20.
4. **IC de la sellada con pocos clústeres — OBSERVADO.** t de clúster [0,0252, 0,4335]: en el filo; el p oscila 0,0007–0,022 según la SE; **cruza el cero al quitar el bloque 1**. La misma anatomía del +6,5 pp direccional.
5. **Intentos — NO SOSTIENE** (no en la máquina; 2 vs 6 según convención).
6. **R2 sobre la sellada no calculado ni publicado** (0,1899, [−0,029, +0,402]); «ajuste causal 0,248» citado desnudo (el JSON trae [0,2202, 0,2768]); `fraccion_fechas_rho_positivo` sin intervalo; **selección ex post del universo** (los 8 tickers son la composición de 2026 aplicada a 2018); `excluir_cero` en la larga filtra sobre Y (108/15.011 filas); sesgo contra el hallazgo: `apertura_estimada_pct` sellada a 2 decimales produce empates en 6 de 35 fechas (atenúa ρ); código muerto en `transversal.py:217-218` y 16 `RuntimeWarning` por corrida.

## Criterios

V1–V4 NO EVALUABLE (sin estadístico direccional, sin CRPS, sin MAE; un rango no baja un MAE) · V5 NO EVALUABLE y bloqueado (intentos no absorbidos) · V6 NO EVALUABLE, agravado por C (el gap es intradeable) · **V7 NO PASA: la prueba larga se abrió dos veces** (12:11 v1, 12:14 v2; justificada por el defecto de datos, declarada en bitácora, no en el informe) · **R1 SE ACTIVA por análogo:** el control OLS sin motor le gana al orden del campeón (+0,0608 [0,025, 0,096]) · **R2 SE ACTIVA sobre la sellada:** 0,2294 → 0,1899, IC cruza el cero por las dos vías · R3 no activada por fuga temporal (β causal, `merge_asof` backward exclusivo, embargo, sellada excluida: verificados), pero dos sesgos de selección declarados arriba.

## Dictamen

**NO SOSTIENE** la afirmación tal como está redactada. El fenómeno **SÍ sostiene** y merece publicarse con otro título: **un orden de β estimado sin el motor ordena dentro del día (ρ̄ 0,2403 [0,2062, 0,2756], nula de etiquetas p = 0,0025, simétrico en el signo del SOX, ningún ticker lo carga); el orden del campeón no alcanza la vara pre-registrada (0,1795) y en la ventana sellada no sobrevive a R2.**

**Bloqueantes:** (1) retirar «0,240 [0,201, 0,273]»; (2) errata fechada en la Enmienda 1 (1.334 → 1.071); (3) nula de etiquetas de β como principal, within-day como sensibilidad; (4) R2 sobre la sellada calculado y publicado; (5) separar campeón de proxy en todo el texto, publicar el contrafactual 0,1795 etiquetado; (6) IC de la sellada por t de clúster, bloques 20 retirado por degenerado; (7) p de la sellada con las dos SE; «p < 0,00025» en ajuste y prueba; (8) intentos en la máquina con UNA convención para toda la corrida; (9) declarar la doble apertura en el informe.
**Exigidos:** (10) selección ex post del universo; (11) sensibilidad de `excluir_cero` en la larga; (12) dejar-uno-fuera y fracción positiva con Wilson; (13) publicar la identidad ρ_d = sign(S_d)·spearman(orden β, gap); (14) la partición por signo del SOX; (15) código muerto y `errstate`.
