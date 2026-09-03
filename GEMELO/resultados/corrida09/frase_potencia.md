# La frase de potencia del 5.1, en dos versiones — con n, intervalo y fecha (encargo 09, 1b/3c)

> PROPUESTA v2 (dictamen 1b/3c aplicado: sin fecha encabezando; ancla y N declarados). Leída de `horizonte.json` (ruta 3, simulador calibrado) y de `potencia_por_metrica.json` (Frente E v2). Ancla: cadena local a `2026-08-31` con la regla de deduplicación firmada, **n = 246 en 35 días**, ventaja 9.35 pp, IC95 de día [-7.2, 26.32], cadencia 0.897 sellos/día hábil. Gatillo: 2026-10-25 (~73 días sellados).

## Versión «dirección» (V1 congelado; secundaria bajo D3)

> Con ~73 días sellados el 25-oct, la potencia para detectar una ventaja direccional verdadera de 9 pp es **0.30 [0.273, 0.33]**; de 6,5 pp, **0.18 [0.162, 0.21]** (simulador calibrado, 35 días de ancla, n = 246). Para llegar a 0,80 hacen falta **≈263 días sellados** a 9 pp (rango Monte Carlo [229, 296]; banda paramétrica de la ruta 1: 248 [109, 370]) → **2027-08-18** ['2027-06-25', '2027-10-08'], y ≈510 (MC [467, 580]; ruta 1: 475 [209, 709]) a 6,5 pp → **2028-09-06** ['2028-06-30', '2028-12-25']. Al efecto observado (z de día 1.11) son 223 días [28, '∞']. El veredicto del 25-oct sobre la dirección será, con alta probabilidad, «no distinguible de cero» aunque la ventaja exista.

## Versión «magnitud» (V1-bis propuesta; primaria bajo D3) — v2 tras el dictamen

> Con ~73 días sellados el 25-oct, la potencia para detectar que el modelo reduce el MAE del gap frente a predecir cero está en la banda **0.90 / 0.86 / 0.70** (generador de 9 pp [0.871, 0.923] / efecto observado [0.831, 0.891] / bajo R2 [0.663, 0.742]); para el CRPS frente a la climatología **0.76 [0.721, 0.795]**. Días para potencia 0,80 en MAE **al efecto observado** (+0.437 pp, IC t de clúster [-0.0872, 0.9616]: contiene el cero): **96 [20, inf] → 2026-12-01** ['2026-08-27', '∞']; bajo R2, 175 días. Si el efecto fuera el del generador de 9 pp, ≈58 días (interpolación en log(D), verificada directa 0,80–0,82; sólo Monte Carlo, sin incertidumbre paramétrica). **Ninguna fecha encabeza:** el 25-oct fija ~73 días, y lo que la muestra dice es la banda de potencia a ese horizonte; una fecha de 0,80 sólo vale condicional al tamaño del efecto, que hoy tiene un intervalo que contiene el cero.

## Lo que hay que saber al firmar

- **Ancla:** los dos instrumentos usan la cadena local a 31-ago (n = 246, +9.35 pp) y NO la ventana canónica del README (28-ago, n = 238, +9,66 pp, `cifras.sellada()`): divergencia declarada, misma regla de deduplicación, tres sellos más.
- **Registro de intentos al escribir esta frase: 310** (`GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO`; `horizonte.md` imprime el N del momento de su corrida).
- La interpolación en log(D) no estaba prefijada: lineal daría ≈61 [57, 65] (dictamen 1b); por eso el «≈58» va sin intervalo y condicional al generador.
- Los «días para 0,80» del simulador miden sólo error de Monte Carlo; la banda paramétrica (SE de día, ICC, b, c) es la de la ruta 1 de `horizonte.md`.
- Las dos versiones se publican juntas y en ese orden, sin la palabra prohibida; ninguna va al README hasta la firma.
- La magnitud contrasta CAMPEÓN contra cero/climatología: no es V2 ni V4 (retador contra campeón). Es lo que la muestra sí hace medible.
- MAE y CRPS son UNA familia (Frente E): con σ_pred ≈ sd_clim casi toda la ganancia de CRPS es la media; no son dos corroboraciones.
- La climatología y σ_pred del Frente E están estimadas EN MUESTRA (sesgo declarado allí); el juez lineal de 3b usa climatología causal.
- Extremo superior ∞ en un intervalo = el IC del efecto contiene el cero.

