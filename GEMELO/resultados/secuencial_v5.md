# Plan secuencial v5 — características operativas simuladas (Frente F, PROPUESTA)

> **PROPUESTA — Frente F, octava corrida; pendiente de dictamen (lee los cuatro rechazos)** · generado 2026-09-02T18:45:26.293884+00:00 · `python GEMELO/simulador/secuencial_v5.py`

Pre-registro: `GEMELO/preregistro/secuencial_v5.md`. Miradas a [50, 100, 150, 200, 250] fechas selladas; gasto Lan-DeMets O'Brien-Fleming, bilateral, acumulado nominal [0.0, 0.0019, 0.0114, 0.0284, 0.05]; fronteras derivadas por simulación bajo H0 con el generador calibrado (ICC 0.3925, b = 0.5156, c = 5.5312), 20000 réplicas: **c_k = [inf, 3.147, 2.572, 2.273, 2.06]**.

## Tipo I (rechazo bajo H0), total y por mirada

| autocorrelación entre fechas φ | rechazo total | IC95 | por mirada | acumulado |
|---|---|---|---|---|
| phi_0.0_AJUSTE_no_medicion_(mismas_trayectorias_que_las_fronteras) | **0.05** | [0.047, 0.053] | [0.0, 0.0019, 0.0095, 0.017, 0.0215] | [0.0, 0.0019, 0.0114, 0.0284, 0.05] |
| phi_0.0_FUERA_DE_MUESTRA | **0.0495** | [0.047, 0.053] | por semilla: [0.0505, 0.0485] | n = 20000 |

**Referencia externa (O'Brien-Fleming K = 5, recursión de Armitage, `GEMELO/SECUENCIAL/fronteras.py`): c_k = [4.562, 3.226, 2.634, 2.281, 2.04]** contra las simuladas [inf, 3.147, 2.572, 2.273, 2.06].
- la mirada 1 tiene c = ∞ por RESOLUCIÓN, no por diseño: α₁ = 1,2e−5 sobre 20.000 réplicas son 0,2 cruces esperados → el plan tiene CUATRO miradas efectivas, no cinco; la frontera de la mirada 2 se apoya en ~38 cruces, así que los IC de tipo I y potencia son CONDICIONALES a una frontera con error de Monte Carlo no propagado; tres de las cuatro fronteras finitas quedan por DEBAJO de la referencia externa gaussiana con colas t(4).
- Estadístico: z gaussiano sobre la suma de contribuciones diarias con varianza muestral: es un estadístico NUEVO, distinto de la permutación de signo por día que gobierna la ventana sellada y que el Frente A calibró; cuenta como intento.
- Tipo I FUERA de muestra (semillas independientes, agrupado n = 20000): **0.0495** [0.047, 0.053]. La fila «AJUSTE» de arriba NO es una medición: es la definición del ajuste.

## Sensibilidad a φ, con control φ = 0 al mismo protocolo y AC1 REALIZADO

| φ | rechazo total | IC95 | AC1 realizado de las contribuciones | fracción de fechas con contribución 0 |
|---|---|---|---|---|
| phi_0.0 | 0.058 | [0.052, 0.064] | **-0.0024** | 0.536 |
| phi_0.1 | 0.0602 | [0.054, 0.066] | **-0.0009** | 0.536 |
| phi_0.2 | 0.0597 | [0.054, 0.066] | **0.0011** | 0.536 |
| phi_0.3 | 0.0563 | [0.051, 0.062] | **0.0033** | 0.535 |

**Lectura:** el AC1 realizado de las contribuciones NO sigue a φ (queda ≈ 0): el eje es inerte porque ~la mitad de las fechas contribuyen exactamente cero (modelo = baseline cuando el SOX sube). El control φ = 0 al mismo protocolo contiene a las filas φ > 0: la tabla es cuatro corridas de la misma nula, NO una medición de dependencia. El plan sigue SIN evidencia de que controla α bajo dependencia; la banda firmada [0,046, 0,079] queda intacta. En la ventana sellada: AC1 = -0.1746 y **54% de las 35 fechas contribuyen exactamente cero** — más de la mitad de las fechas selladas no aportan información al estadístico direccional, porque el campeón y la baseline coinciden por construcción cuando el SOX sube. Eso explica por qué la dirección necesita ~250 días y la magnitud ~100.

**Conclusión (dictamen F, quinto rechazo):** el plan reproduce pero se verifica contra sí mismo (rechazo #1, reintroducido); vuelve a `cola_decisiones.md`, no entra a `espera_firma.md`. Intentos: **2** (el diseño y el estadístico nuevo).

## Potencia por mirada y n esperado hasta decisión

| δ verdad | rechazo total (potencia) | IC95 | por mirada | acumulado | fechas esperadas |
|---|---|---|---|---|---|
| 9.0 pp | **0.7913** | [0.778, 0.804] | [0.0, 0.0935, 0.2607, 0.2597, 0.1772] | [0.0, 0.0935, 0.3543, 0.614, 0.7913] | 196.9 |
| 6.5 pp | **0.4988** | [0.483, 0.514] | [0.0, 0.0325, 0.1225, 0.1765, 0.1673] | [0.0, 0.0325, 0.155, 0.3315, 0.4988] | 224.1 |
| 5.0 pp | **0.3297** | [0.315, 0.344] | [0.0, 0.0152, 0.0752, 0.1115, 0.1278] | [0.0, 0.0152, 0.0905, 0.202, 0.3297] | 234.6 |

