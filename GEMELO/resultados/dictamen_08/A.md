# Dictamen del `estadistico-adversario` · Frente A (simulador con verdad conocida) · 2-sep-2026

> Texto del agente, guardado tal cual por el orquestador. Sobre la **versión 1**
> de `calibracion_instrumento.md`. La v2 (misma tarde) aplica los bloqueos
> 1–8 y los exigidos 9–15; lo que la v2 NO cierra se declara en la bitácora.

## Verificación previa

`README.md` y la skill `cifras-canonicas` coinciden: `excluir_cero`, n = 248, modelo 66.1 % [60.0, 71.7], base 59.7 % [53.5, 65.6], +6.5 pp con McNemar p = 0.1849, MAE 2.98 vs 3.33, cobertura 90.3 %, ratio de ancho 1.84×. `evaluacion.py` reproduce las Wilson y da McNemar b=72, c=56 → p = 0.1847. Discrepancia menor: el self-test imprime "el campeón marca 1.77" (`evaluacion.py:357, 479, 491`) donde el README dice 1.84×. `senales.db` intacto (mtime 2026-09-01 18:15:31).

## Punto 1 — El DGP · OBSERVADO

(a) Dependencia más benigna que la real por dos vías: U entra por las MISMAS β que S (covarianza intra-día de rango 1 con las cargas que el campeón conoce); y **no hay dependencia ENTRE días**. Medido inyectando AR(1) en el factor de día (3.000 réplicas):

| ρ | cobertura percentil de día | cobertura t de clúster | tamaño de la permutación |
|---|---|---|---|
| 0.0 | 0.9310 [0.921, 0.940] | 0.9503 [0.942, 0.958] | 0.0413 [0.035, 0.049] |
| 0.2 | 0.9057 [0.895, 0.916] | 0.9277 [0.918, 0.936] | **0.0637 [0.055, 0.073]** |
| 0.4 | 0.8560 [0.843, 0.868] | 0.8827 [0.871, 0.894] | **0.1113 [0.101, 0.123]** |

ρ = 0.2 es compatible con AC1 = −0.13 ± 0.17 (`horizonte.py`). El simulador no puede detectar el único modo de fallo que los datos dejan abierto porque asume que no existe.

(b) β verdadera sin error de estimación: compone con (a). (c) ν = 4 es casi irrelevante (endpoints son signos); curtosis indefinida; la sensibilidad prometida no se entregó. (d) μ_i, β_i, σ_i y `escala_sox` estimados en muestra sobre las mismas 246 filas, sin intervalo; `escala_sox` sale de 23 fechas de 35. (e) El piso del 30 % ata en 2 de 8 tickers (2330.TW: común 2.104 > σ 1.981; 4063.T: 1.988 > 1.662): sd simulada +9.6 % y +22 %; infla la dependencia intra-día simulada; ningún test cubre el caso. (f) ICC logrado 0.4059/0.4106/0.4043/0.4094 contra objetivo 0.3925: fuera de la tolerancia 0.005; la bisección se detiene en el ruido. (g) El pre-registro dice calibrar c y la escala de S al ICC y al SE de día; el código calibra sólo c. (h) Cuatro de los siete ejes son submuestreo aleatorio bajo el simulador: A2 mide la nula intercambiable.

## Punto 2 — A1 · OBSERVADO

0.938 y 0.927 se reproducen exacto, pero son una tirada de un solo flujo: `_bootstrap_dia` re-siembra `default_rng(SEMILLA)` adentro y las 2.000 réplicas compartieron una sola matriz `idx`. Con 10.000 réplicas y semilla por réplica: percentil **0.9271 [0.922, 0.932]** y **0.9275** (las dos celdas son el mismo número); t de clúster gl = k−1 **0.9450 / 0.9470**; iid 0.6965 / 0.7005. Verdad del generador nulo: 8 medidas a 200.000 días dan sd 0.165 pp; se publica sin intervalo. La subcobertura de 2.3 pp es real (robusta a ν y a n_boot). Causa: método percentil con k = 35, no el enfoque de clúster. Percentil-t 0.9335 no arregla; BCa no probado. **Criterio congelado incumplido y no declarado:** «cobertura < 93 % con IC que excluya 95 %» se cumple; el documento de resultados no lo dice. Alcance: todo «IC de clúster de día» publicado es un nominal 95 % con cobertura real 92.7 %.

## Punto 3 — A2 · OBSERVADO

Reproducción exacta (10.57 celdas, 0.0551, P(≥1) 0.2533). Pero: P(0 de 192) = 0.7467 [0.695, 0.793], no «la mitad»; la tasa por celda sin intervalo (honesto, sobre réplicas: [0.0378, 0.0735]); y falta la alternativa: P(0 de 192) = 0.5550 bajo 6.36 pp y **0.4600** bajo 9 pp — cociente de verosimilitudes 1.6, no distingue nada.

## Punto 4 — A3 · diagnóstico VERIFICADO / corrección VERIFICADA en aritmética, OBSERVADA en estructura / relectura EXIGIDA

`var_sharpe` es por período; pasarle SR·√252 con n = días infla z por √252. Simulación: anualizado 0.2648/0.2671/0.2252/0.3830 (reproduce lo publicado); por período **0.0011/0.0009/0.0009/0.0006**. Tamaño teórico gaussiano de «DSR ≥ 0.95»: 0.00143 a N = 106 (0.00678 a N = 9). Elección de V: incluyendo al ganador 0.0011; teórica 1/T 0.0014; excluyendo 0.0024; a N = 9 un factor 26. El 5.1 sobrevive **porque los Sharpes son negativos**, no por corrección. WS2b con unidad correcta: C1 DSR 0.9605, C2 0.9473, C3 0.9638, campeón 0.9565 (N = 9): tres de cuatro cruzan 0.95; la explicación «saturación» de `control_lineal.md` y `ventana_larga.md` es falsa; `MINIMO_DIAS_SHARPE = 60` queda con justificación desmentida y origen post-hoc. Defensa insuficiente: test que enumera dos rutas a mano (`calibracion.py` es un tercer llamador invisible), umbral ≤ 0.05 con 300 réplicas para una tasa de 0.001, tres `1/√252` a mano; `calibracion.py` publicaba sólo las tasas del defecto.

## Punto 5 — A4 · OBSERVADO

Simulador por debajo en 12 de 12 celdas (McNemar exacto b=12, c=0, p = 0.000488); diferencia media +2.67 pp [1.85, 3.55]. La coincidencia es de un escalar (δ·n̄·√D / sd de la suma por día: real 3.5065, simulador 3.52–3.54) al que el simulador fue calibrado; una normal cerrada reproduce `horizonte.md` (McNemar p = 0.77). Causa de la brecha: `horizonte.potencia_simulada` suma un δ constante a cada fila; el simulador lo entrega por el canal de información. **La tabla de potencia de `horizonte.md`, las fechas derivadas y la «potencia 0,36 [0,34, 0,37]» son OPTIMISTAS por ~2–5 pp.**

## Entregable

```
VEREDICTO: NO SOSTIENE tal como está escrito.
CIFRA VERIFICADA:
  A1  0.938/0.927 reproducen EXACTO; cobertura del ESTIMADOR 0.9271/0.9275; t de clúster 0.9450/0.9470.
  A2  10.57, 0.0551, P(≥1)=0.2533 exactos; NUEVO P(0 de 192)=0.7467 (δ=0), 0.5550 (6.36 pp), 0.4600 (9 pp).
  A3  anualizado 0.2648/0.2671/0.2252/0.3830; por período 0.0011/0.0009/0.0009/0.0006; teórico 0.00143 (N=106).
      WS2b con unidad correcta: C1 0.9605, C3 0.9638, CAMPEÓN 0.9565 (N=9).
  A4  simulador por debajo 12/12; diferencia media +2.67 pp [1.85, 3.55].
  R2  ancla 31-ago +9.35 → +2.48 pp, McNemar 0.0451 → 0.6752, permutación de día 0.2967 → 0.8248.
DENOMINADOR: «siempre al alza» sobre LAS MISMAS FILAS en las dos rutas y en el simulador. ADVERTENCIA:
  el ancla es la cadena LOCAL a 31-ago (n=246, 35 días), NO la ventana canónica publicada (n=248).
INTENTOS: N = 100 (registro) y 106 (5.1); Frente A suma 0 — pero la elección del estimador de IC
  DESPUÉS de ver la cobertura debe entrar como eje declarado en bifurcaciones.EJES / NO_EJES.
CRITERIOS: V1 NO PASA (+6.5 pp, p=0.1849; sobre la cadena viva n=261 el McNemar de filas da 0.0080 y
  la permutación de día 0.1830 — el DEFF de 3.56 haciendo su trabajo) · V2/V4/V6/V7/R1 NO EVALUABLE ·
  V3 NO PASA (90.3 %) · V5 NO PASA, y el instrumento estuvo mal calibrado en la dirección permisiva ·
  R2 DISPARA en las dos anclas · R3 no dispara como fuga, pero se declara la circularidad (β, μ, σ y
  escala del SOX estimados EN MUESTRA sobre las mismas 246 filas).
DICTAMEN POR PUNTO: 1 OBSERVADO · 2 OBSERVADO · 3 OBSERVADO · 4 VERIFICADO/VERIFICADO/OBSERVADO/EXIGIDA · 5 OBSERVADO
```

## Cambios exigidos

**Bloqueantes:** (1) declarar en el documento de resultados que A1 cumplió el criterio de refutación congelado; (2) rehacer A1 con semilla por réplica y ≥ 10.000 réplicas; (3) publicar la comparación de métodos y corregir a t de clúster gl = k−1, declarar percentil-t/BCa, añadir el método como eje declarado; (4) reemplazar la frase de A2 por el cociente de verosimilitudes con las tres filas y el intervalo sobre réplicas; (5) añadir a A3 la fila corregida y el tamaño teórico con la sensibilidad a V; (6) erratas fechadas en `control_lineal.md`, `ventana_larga.md`, `experimento.py:315`; re-justificar `MINIMO_DIAS_SHARPE` y declarar su origen post-hoc; (7) errata en los artefactos del 5.1 (sobreviven porque los Sharpes son negativos); (8) sustituir la afirmación de A4 por la comparación pareada, la tercera ruta y la declaración de que `horizonte.md` es optimista.

**Exigidos antes de publicar cualquier cifra derivada:** (9) declarar los seis puntos del DGP con la tabla del AR(1); (10) sensibilidad a ν y a c; (11) intervalo para `verdad_delta_pp`, `tasa_media_por_celda`, `icc_sim`, `escala_sox`; (12) endurecer `tests/test_unidades_sharpe.py` (≤ 0.01 con más réplicas; AST por todo el repo con lista blanca); (13) eliminar el `1/√252` repetido: que el productor entregue el Sharpe por período; unidad explícita o precondición en `psr`/`dsr`; (14) declarar que el ancla es la cadena local n = 246 y no la canónica; (15) corregir `evaluacion.py` (1.77 → 1.84).
