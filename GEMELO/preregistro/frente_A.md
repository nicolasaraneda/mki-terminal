# Pre-registro · Frente A — calibrar el instrumento contra un patrón conocido

**Escrito 2-sep-2026 11:45, antes de correr ninguna réplica.** Octava
corrida. PROPUESTA hasta el dictamen del `estadistico-adversario`.

## Hipótesis, en una frase

La maquinaria de inferencia del proyecto (IC de clúster de día, test de
permutación de signo por día, McNemar de filas, matriz de 192 celdas, DSR
con el registro de intentos) entrega lo que promete —cobertura 95%, tamaño
5%, potencia la publicada— cuando la verdad se conoce; y el estimador iid
de filas no.

## Qué se mide, con qué estadístico y con qué intervalo

Sobre un proceso generador **sintético con verdad conocida**, calibrado a
la ventana sellada (ICC, DEFF, SE de día, tasa base, tamaños de clúster,
leídos de la máquina en el momento de calibrar y sellados en el `.json`):

| pregunta | estadístico | verdad | intervalo del reporte |
|---|---|---|---|
| A1 cobertura del IC95 de clúster de día (bootstrap de días, `bifurcaciones._bootstrap_dia`) vs del IC95 iid de filas (normal sobre la diferencia pareada) | fracción de réplicas cuyo IC contiene δ verdadero | δ ∈ {0, 9 pp} | Wilson 95% sobre las réplicas |
| A2 tamaño de las 192 celdas legítimas (`bifurcaciones.aplicar` + permutación de signo por día) bajo δ = 0 | por réplica: cuántas celdas dan p < 0,05; P(al menos una) | δ = 0 | Wilson 95% |
| A3 DSR con el registro vigente (N = 100 registro / 106 veredicto) bajo la nula | P(DSR del mejor de N intentos nulos ≥ 0,95) | Sharpe verdadero 0 | Wilson 95% |
| A4 potencia frente a 9 / 6,5 / 5 pp para D ∈ {35, 73, 125, 250, 475, 803} días | fracción de réplicas con p de permutación de día < 0,05 | δ conocido | Wilson 95%; se compara con `horizonte.md` (3.000 réplicas por remuestreo de días reales) |

## Efecto que se consideraría relevante

Una desviación de cobertura o tamaño **mayor que 2 pp** respecto del
nominal, con IC que excluya el nominal, es un defecto del instrumento y va
al ejecutable. Una diferencia de potencia con `horizonte.md` mayor que lo
que los dos intervalos admiten es errata.

## Qué refutaría la hipótesis

- Cobertura del IC de día < 93% o > 97% con IC que excluya 95%.
- Tasa de celdas con p < 0,05 bajo la nula > 7% en promedio, o P(al menos
  una de 192) que no sea explicable por la correlación entre celdas
  (todas miran casi las mismas filas): se reporta la cifra y se compara con
  la observada en la ventana real (0 de 192).
- DSR ≥ 0,95 bajo la nula en más del 5% de las réplicas.

## El diseño del simulador, declarado para que el adversario lo ataque

`gap_{i,d} = μ_i + β_i·(b·S_d + c·U_d) + σ_i·ε_{i,d}`, con S_d (el
retorno del SOX que el modelo ve), U_d (un shock de día que el modelo NO
ve) y ε_{i,d} independientes, **t de Student con ν = 4** (colas). La
predicción del campeón es p_{i,d} = β_i·S_d; la baseline es «siempre al
alza». La ventaja direccional δ se fija eligiendo b por bisección hasta que
E[acierto_modelo − acierto_base] = δ (b = 0 NO es δ = 0, porque con deriva
positiva un llamado independiente del gap pierde contra «siempre al alza»;
el punto δ = 0 es donde los llamados a la baja aciertan la mitad de las
veces, que es la identidad δ = f·(2q−1) de `mde_vs_observado.md`).
Calibración: β_i, μ_i, σ_i y tamaños de clúster por fecha leídos de las
filas selladas; c y la escala de S ajustados para reproducir ICC y SE de
día. **Riesgo declarado de favorecer al proyecto:** un simulador cuyo
clúster viene sólo de S_d reproduce la mecánica exacta del campeón y podría
dar cobertura perfecta al estimador de día por construcción; por eso se
incluye U_d (dependencia que el modelo no explica) y se reporta la
sensibilidad a ν y a c.

## Partición de datos

No aplica: la verdad es sintética. Los datos reales sólo entran como
**parámetros de calibración** (`hasta_sello = 2026-08-31`, regla firmada,
`excluir_cero`), nunca como objeto de inferencia.

## Intentos del DSR

Este frente no evalúa ninguna configuración sobre datos reales: **0
intentos**. Si el adversario decide lo contrario, se registran.

## Enmienda 1 (2-sep-2026, 14:23, después del dictamen del adversario sobre la v1)

El `estadistico-adversario` dictaminó **NO SOSTIENE tal como está escrito**
(`GEMELO/resultados/dictamen_08/A.md`). Lo que este pre-registro reconoce,
con fecha posterior y sin tocar lo escrito arriba:

1. **El criterio de refutación congelado arriba SE CUMPLIÓ** para el
   estimador percentil de día: cobertura < 93% con IC que excluye 95% (la
   v1 publicaba 0,938 / 0,927 de un solo flujo de réplicas; con semilla por
   réplica y 10.000 réplicas el estimador cubre ~0,927 en las dos celdas).
   La hipótesis «el instrumento de clúster está calibrado» queda **refutada
   para ese estimador**. La v1 lo decía en la bitácora y no en el documento
   de resultados; manda el documento, y ahora lo dice.
2. **La corrección es cambiar el estimador** a la t de clúster linealizada
   con gl = k−1 (`bifurcaciones._ic_t_cluster`). Elegir el estimador
   DESPUÉS de ver la cobertura es un grado de libertad de la misma familia
   que la matriz de 192 mide: **se declara como eje en
   `bifurcaciones.NO_EJES`** («método del IC de clúster») con la cobertura
   medida de cada método, y no suma al N del DSR (no selecciona modelo).
3. La v2 entrega lo que la v1 prometía y no dio: sensibilidad a ν y a c, y
   además a la **dependencia entre días** (AR(1) en los factores de día,
   `Parametros.rho`), que la v1 asumía inexistente. Con ρ > 0 el tamaño de
   la permutación de día sube por encima de 0,05: **riesgo declarado, no
   resuelto**.
4. Seis puntos del DGP que la v1 no declaraba quedan declarados en el
   informe (cargas compartidas de U y β; sin dependencia entre días; β
   verdadera sin error de estimación; piso del 30% que ata en 2 de 8
   tickers; ICC logrado fuera de tolerancia; el código calibra sólo c, no
   la escala de S ni el SE de día como decía el §DGP de arriba).
5. El ancla de calibración es la **cadena local a 31-ago (n = 246, 35
   días)**, no la ventana canónica publicada (n = 248). Se declara.
6. A4 no es verificación independiente: es un escalar (δ·n̄·√D / sd de la
   suma por día) al que el simulador fue calibrado. Se publica la
   comparación pareada y la tercera ruta cerrada, y se declara que
   `horizonte.md` es optimista.
7. El defecto de unidades del PSR/DSR (A3) es real; `inferencia` ahora
   hace cumplir la unidad (`ErrorUnidadSharpe`), el productor entrega el
   Sharpe por período y el test recorre el repo con lista blanca.

Intentos del DSR de este frente: **0** (sin cambios).
