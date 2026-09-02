# Pre-registro · Plan secuencial v5 — con características operativas SIMULADAS, no afirmadas

**Escrito 2-sep-2026 12:17, antes de simular.** Octava corrida, Frente F.
PROPUESTA hasta el dictamen del `estadistico-adversario`, que lee los
cuatro rechazos anteriores (`DECISIONES.md` §47 y §56; `GEMELO/SECUENCIAL/DISEÑO.md`
§«Lo que la v1 decía mal» y siguientes) y verifica si esta versión responde
a cada uno. **No se activa solo; si sobrevive va a `espera_firma.md`.**

## Lo que este plan NO re-discute

α = 0,05 nominal, firmado (acta §53). El MDE sigue sin firmar (`espera_firma.md`
§5): el plan se simula a **δ = 9 pp** (la relevancia derivada, `mde_vs_observado.md`)
y reporta también 6,5 y 5 pp, sin elegir.

## Diseño

- **Unidad:** la fecha sellada. Estadístico en la mirada k: Z_k =
  Σ_j S_j / √(k·s²_k), con S_j = Σ_i (acierto_modelo − acierto_base) de la
  fecha j (la «contribución por fecha» de `mirada.py`) y s²_k la varianza
  muestral de las S_j hasta la mirada k. **La varianza se re-estima en cada
  mirada con las fechas acumuladas** (rechazo #2: no se congela un DEFF).
- **Miradas en fechas FIJAS de sellado**, no en n de filas: k ∈ {50, 100,
  150, 200, 250} fechas selladas (≈ oct-2026, ene-2027, abr-2027, jun-2027,
  jul-2027 a la cadencia medida de 0,9 sellos/día hábil).
- **Función de gasto de α, elegida ahora:** Lan-DeMets con forma de
  O'Brien-Fleming, α(t) = 2 − 2Φ(z_{α/2}/√t), t = k/250, bilateral.
  Fronteras derivadas por recursión numérica (no tabla): se computan por
  simulación bajo H0 con el mismo estadístico, calibrando cada frontera para
  gastar exactamente α(t_k) − α(t_{k−1}), **con el ICC medido y con el
  proceso generador calibrado (Frente A)**, no con normales iid.
- **Futilidad:** no vinculante (informativa): potencia condicional < 0,10
  bajo la hipótesis del diseño se reporta, no detiene.
- **Regla de decisión:** rechazar H0 en la primera mirada en que |Z_k| ≥
  c_k. Al llegar a 250 fechas sin cruzar, el plan termina sin decisión
  (que es un resultado: «no medible a este horizonte»).
- **Qué se publica:** tipo I total y por mirada (simulado, con Wilson),
  potencia por mirada a 9 / 6,5 / 5 pp, n esperado hasta decisión, y la
  sensibilidad a autocorrelación entre fechas φ ∈ {0, 0,1, 0,2, 0,3} — la
  banda que la séptima corrida no pudo estrechar.

## Cómo responde a cada rechazo anterior (lo que el adversario verifica)

| rechazo | qué exigía | esta versión |
|---|---|---|
| #1 (v1→v2) | fronteras, potencia y N congelados mal | nada se congela «a mano»: fronteras, potencia y n esperado salen de la simulación con verdad conocida y quedan sellados en el `.json` con semilla |
| #2 (v2→v3) | el DEFF se mudó a un estimador que exige AC1 = 0 | la varianza se re-estima por mirada sobre fechas; y la sensibilidad a AC1 ∈ [0, 0,3] se publica con el α resultante, no se supone |
| #3 (v3→v4) | la tabla de exposición residual no reproducía; sin regla para α hasta 0,079 | la tabla se produce por el script, con semilla; la regla: el plan declara α nominal 0,05 **y** publica el α simulado bajo cada φ; si el α a φ=0,3 supera 0,08 se declara inválido a ese φ |
| #4 (v4→v5) | dedup sin decidir; razones sin IC; sin ancla temporal | la dedup está FIRMADA (acta §60) y se aplica en la carga; toda cifra lleva IC; el ancla es `CORTE_REGLA_FIRMADA` |

## Lo que sigue faltando y no lo resuelve este plan

El MDE (firma de Nicolás), y la copia de insumos (Frente A de la séptima)
que haría reproducibles las filas sobre las que el plan mira.

## Intentos del DSR

Un diseño = **1 intento** (la simulación no mira datos reales, pero el plan
sí decide sobre ellos cuando se active).
