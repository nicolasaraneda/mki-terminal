# Pre-registro · Frente D — predicción transversal: escapar del clúster de día

**Escrito 2-sep-2026 11:45, antes de mirar ningún dato.** Octava corrida.
PROPUESTA hasta el dictamen del `estadistico-adversario`.

## Hipótesis, en una frase

Dentro de una misma fecha, el ORDEN de las predicciones del campeón
(β_i·S_d: en un día de SOX al alza, los tickers de β alta deberían gapear
más) tiene información sobre el orden de los gaps realizados — una
pregunta distinta del contagio direccional, que el efecto día cancela por
construcción.

## Estadístico exacto

- Por fecha d con k_d ≥ 4 tickers: ρ_d = correlación de Spearman entre el
  gap predicho y el gap realizado de los k_d tickers.
- Estadístico: ρ̄ = media de ρ_d sobre las fechas (cada fecha pesa 1: la
  unidad es el día).
- Variante de control, pre-declarada: τ de Kendall en vez de Spearman
  (misma pregunta, otra métrica de concordancia; se reporta, no se elige).

## Distribución nula y estimador de intervalo

- Nula: permutación de los gaps realizados DENTRO de cada fecha (4.000
  permutaciones; rompe la asociación transversal, conserva el efecto día y
  los tamaños de clúster). p bilateral de ρ̄.
- Intervalo: bootstrap de FECHAS enteras (4.000 réplicas) sobre ρ̄, IC95.
- El n efectivo es el número de fechas con k_d ≥ 4 (no el de pares
  día-ticker), y se reporta como tal.

## Tamaño de efecto relevante

ρ̄ ≥ 0,20 (con 8 tickers, un ρ de 0,2 equivale a acertar el orden de ~2
pares más de lo que da el azar). Por debajo, «no relevante aunque sea
distinto de cero».

## Qué refutaría la hipótesis

IC95 de ρ̄ que contenga el cero, o p de permutación ≥ 0,05, sobre la ventana
sellada Y sobre los años de prueba de la ventana larga. Si sólo una de las
dos lo refuta, se publican las dos con su lectura.

## Partición de datos

1. **Ventana sellada primero** (37 fechas vivas, regla firmada,
   `excluir_cero`): no hay look-ahead posible, las predicciones ya están
   selladas.
2. **Ventana larga, con partición congelada AHORA:** las predicciones
   transversales se construyen SIN el motor —sólo con el signo del retorno
   del SOX de la sesión anterior y un orden de β— a partir de los gaps
   reconstruidos (`GEMELO/cache/gaps_03fdca36d64efb0d.csv`, 8 tickers,
   2018-09 → 2026-09) y del `^SOX` de la caché testigo del 1-sep. **Años de
   ajuste: 2018-09 → 2023-12** (ahí se estima el orden de β por OLS
   gap ~ SOX(t−1) por ticker). **Años de prueba: 2024-01 → 2026-08.** Los
   años de prueba no se abren hasta cerrar el análisis sobre los de ajuste;
   el orden de β que entra a la prueba es el de los de ajuste, no el de las
   betas selladas (que se estimaron en 2026).
3. Corte elegido porque deja ~5,3 años de ajuste y ~2,7 de prueba, y porque
   2024-01 es anterior a toda emisión sellada.

## Intentos del DSR

Una configuración (Spearman) más su control (Kendall) sobre dos ventanas:
**2 intentos**, declarados antes de correr.

## Enmienda 1 — 2-sep-2026 12:11, tras la auditoría de fuga y ANTES de abrir la prueba

El `auditor-lookahead` rechazó la fila del ajuste tal como estaba (β
estimada con todo el ajuste y evaluada sobre el mismo ajuste: in-sample) y
señaló que la ventana sellada está anidada en la prueba. Cambios, todos
anteriores a abrir los años de prueba:

1. **β causal expansiva** dentro del ajuste: la predicción de la fecha d
   usa sólo fechas < d, con burn-in de 250 sesiones por ticker
   (`betas_causales`). La β que entra fija a la prueba es la del ajuste
   completo, como estaba.
2. **Embargo** de 5 sesiones al inicio de la prueba (como
   `backtest.EMBARGO_DIAS`).
3. **Las 37 fechas selladas (2026-07-05 → 2026-08-31) se excluyen de la
   prueba**: ya fueron leídas. La sellada y la prueba dejan de contarse como
   dos refutaciones independientes.
4. `excluir_cero` se aplica también a la ventana larga (108 de 15.011
   filas, 0,7%), declarado.
5. Los gaps se leen del testigo preservado
   (`testigos_fuente/gaps_03fdca36d64efb0d.csv.gz`, sha256 3908fdd58a71119b),
   no del caché mutable. Semilla 20260902, declarada.
6. Intentos: se mantienen **2** (Spearman + control Kendall); las variantes
   de esta enmienda no son configuraciones distintas sino la corrección de
   una fuga.
7. Prueba maestra en `tests/test_transversal.py` (invariancia a truncar en
   t, con contraprueba).

Resultado del ajuste con β causal (antes de abrir la prueba): ρ̄ = 0,257
[0,228, 0,285], p = 0,0002, 1.334 fechas — sostiene lo que la versión
in-sample decía (0,260), como el auditor midió por su cuenta (0,256).

## Enmienda 2 — 2-sep-2026 12:14: corrección de datos, no de diseño

El Frente B1 descubrió que el caché de gaps omitía toda sesión posterior a
un feriado local (defecto de `GEMELO/datos.descargar_gaps`, corregido con
contraprueba en `tests/test_gaps_feriados.py`). Se regeneraron los gaps
(`testigos_fuente/gaps_v2_propio_indice.csv.gz`, sha256 34fe61082ea58282:
+670 filas, ninguna vieja distinta) y **se re-corren ajuste y prueba sobre
el v2**. No es una configuración nueva ni un intento: es el mismo
estadístico sobre el mismo diseño con los datos completos. Los dos
resultados (v1 y v2) quedan en la bitácora.

## Errata (2-sep-2026, 14:40) sobre la Enmienda 1

La Enmienda 1 dice «1.334 fechas» para el ajuste con β causal. **Es el n de
la versión in-sample que el auditor rechazó**; el ajuste causal (v1) tiene
**1.071 fechas** (ρ̄ 0,2568 sí es el causal). La enmienda es texto
pre-registrado: no se reescribe, se corrige aquí con fecha.

## Enmienda 3 (2-sep-2026, 14:40, después del dictamen del adversario; numerada 2 por error hasta las 15:20)

Dictamen: `GEMELO/resultados/dictamen_08/D.md` — **NO SOSTIENE «el modelo
ordena dentro del día»; el fenómeno SÍ sostiene con otro título.** Al
ejecutable primero (`transversal.py`, tercera corrida de la prueba, sobre
los mismos datos v2 y las mismas hipótesis):

1. **Retirado** el par «0,240 [0,201, 0,273]» (punto de v2 con intervalo de
   v1); el vigente es 0,2403 [0,2062, 0,2756], 637 fechas.
2. **Nula de etiquetas de β como principal** (permutar el vector β entre los
   8 tickers): la unidad de replicación de la afirmación es el
   ordenamiento, n = 1. La within-day queda como sensibilidad.
3. **R2 sobre la sellada**, calculado y publicado (se activa: el IC cruza el
   cero sin el bloque 15–23 jul).
4. **Campeón separado del proxy:** el orden de las β selladas se corre sobre
   la prueba como contrafactual CONTAMINADO (cota optimista); se publica la
   diferencia proxy − campeón y el Spearman entre los dos vectores de β.
   Toda frase «el modelo» sobre la ventana larga queda reescrita como «el
   proxy».
5. IC de la sellada por t de clúster (gl = k−1); bloques de 20 retirado de
   esa ventana (degenera con 2 bloques); p con las dos SE (nula de
   permutación y muestral); «p < 1/(N_PERM+1)» cuando ninguna permutación
   alcanza el observado.
6. Publicados: la identidad ρ_d = sign(S_d)·spearman(orden β, gap)
   (verificada en el propio módulo), la partición por signo del SOX,
   dejar-uno-fuera, la fracción de fechas positivas con Wilson, la
   sensibilidad de `excluir_cero` en la larga, la selección ex post del
   universo (composición de 2026 aplicada a 2018) y la **doble apertura** de
   la prueba (12:11 v1, 12:14 v2).
7. Código muerto retirado.
8. **Intentos:** se cuentan con la misma convención que C (por estadístico
   publicado, contados por máquina al cierre) y van al registro.
