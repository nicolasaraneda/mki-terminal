# El intervalo de clúster de día de la rama de coherencia — bloque 4, corrida 11 (PROPUESTA)

> **PROPUESTA — bloque 4 de la corrida 11; computado, NO cableado; ninguna cifra publicada se mueve.** Generado 2026-09-08T04:31:22.253305+00:00 por `python -m GEMELO.intervalo_coherencia`. Corte `2026-08-28`, convención `excluir_cero`, `senales.db` en `mode=ro`.
>
> **Predicción escrita antes de computar:** el intervalo de clúster de día de la rama de coherencia contiene el cero, como lo contiene el de la regla firmada (§82.3, escrito antes de computar).

## 1. Identidad de conjuntos, antes de computar nada

- Regla firmada: n = 238. Coherencia como la computa el informe de `linea_base` (filtro sobre el crudo, después la convención): n = 223. Coherencia aplicada SOBRE la regla firmada: n = 223.
- ¿Coherencia ⊂ firmada? **True**. ¿Los dos órdenes dan el mismo conjunto? **True**. Filas retiradas: **15**.
  - 2026-07-05: 8 filas (000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T, IFX.DE)
  - 2026-08-05: 7 filas (000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T)

## 2. ¿Días enteros o días mutilados? ¿Eran informativos?

| fecha | filas en la regla firmada | retiradas | quedan | ¿día entero? | Σ(modelo−base) del día | ¿informativo? |
|---|---|---|---|---|---|---|
| 2026-07-05 | 8 | 8 | 0 | sí | -4 | sí |
| 2026-08-05 | 8 | 7 | 1 | **no** | -4 | sí |

Un día informativo es uno cuya suma de (acierto del modelo − acierto de la base) no es cero: es el que mueve el estadístico de día. Si el retiro se lleva días enteros, cambia k; si los mutila, cambia el peso de un día que sigue existiendo.

## 3. Las dos ramas, con los tres estimadores de día (segunda ruta siempre)

| rama | n | días | días informativos | modelo | base | ventaja | IC95 percentil de día | IC95 t de clúster | p permutación de día | ICC | DEFF | n efectivo | b/c | McNemar χ²cc | McNemar exacta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| regla firmada (publicada) | 238 | 34 | 16 | 67.6 % | 58.0 % | **+9.7 pp** | [-7.2, 26.6] | [-8.1, 27.4] | 0.294 | 0.392 | 3.55 | 67.0 | 72/49 | 0.0455 | 0.0451 |
| + coherencia (NO aplicada) | 223 | 33 | 15 | 70.9 % | 56.5 % | **+14.3 pp** | [-1.4, 32.1] | [-3.5, 32.2] | 0.111 | 0.421 | 3.71 | 60.0 | 69/37 | 0.0026 | 0.0024 |

**Cuál de los dos IC es el calibrado** (exigencia B2): la t de clúster con gl = k−1, que el
Frente A midió con cobertura 0,949–0,951 a k = 35; el percentil de día cubre ~0,93 ahí. Acá la
rama de coherencia tiene k = 33 con 3 clúster(es) de tamaño 1 (el 2026-08-05 mutilado), fuera del
estudio de cobertura. Que el percentil «roce» −1,4 no significa nada: es el estimador que sub-cubre.

## 3b. R2 sobre las dos ramas (exigencia B1: una vara de rechazo congelada no se omite porque la rama sea PROPUESTA)

| rama | n sin 15–23 jul | días | ventaja | IC95 percentil | IC95 t de clúster | p permutación | b/c | McNemar exacta |
|---|---|---|---|---|---|---|---|---|
| regla firmada (publicada) | 194 | 28 | +2.6 pp | [-14.4, 20.5] | [-15.7, 20.9] | 0.821 | 48/43 | 0.6752 |
| + coherencia (NO aplicada) | 179 | 27 | +7.8 pp | [-9.1, 25.6] | [-10.8, 26.5] | 0.433 | 45/31 | 0.1354 |

Las dos fechas retiradas (5-jul y 5-ago) están FUERA del bloque de R2: la rama de coherencia hereda
intacta la ventana afortunada, y sin ella se apaga igual que la regla firmada.

## 3c. La asimetría del retiro, en números (exigencia B3)

Σ(modelo − base) por día en la regla firmada, ordenada: `[-8, -4, -4, -4, -4, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 4, 6, 6, 6, 6, 8, 8]`. Días negativos: 6; positivos: 10. El retiro se llevó los dos días con Σ = −4, o sea
**2 de los negativos y 0 de los positivos**. No es indicio de acomodo: es exactamente el mecanismo que el
§82.3 escribió ANTES de computar (una fila puntuada contra el día equivocado pierde contra una baseline
con deriva al alza). Consecuencia que sí hay que decir (exigencia B4): **+14,3 pp es otro estimando**, la
ventaja restringida a filas con sesión coherente, no «+9,7 medido mejor»; el movimiento entero sale de 2
días de 34.

## 4. La predicción, contra el resultado

- Percentil de día contiene el cero: **True**. t de clúster contiene el cero: **True**. Permutación de día p > 0,05: **True**.
- **La predicción se cumple en las tres rutas.** El retiro de las 15 filas mueve el punto y el McNemar de filas, no la conclusión de día: la ventaja sigue sin distinguirse de cero cuando se respeta que las filas de un día no son independientes.

**Cableado:** filtrar_sesion_coherente sigue SIN aplicarse por defecto; cablearlo es decisión aparte, no firmada. Intentos del DSR: 0: el «0» se sostiene sólo porque la
rama no está cableada ni publicada; si algún día `filtrar_sesion_coherente` pasa a aplicarse por defecto,
**es un intento** y entra a `GEMELO.relevo_asiatico` (exigencia B5).

Procedencia: backtest.linea_base.{cargar(dedup=...),filtrar_sesion_coherente,aplicar_convencion,duelo} mode=ro; GEMELO.bifurcaciones.{_bootstrap_dia,_ic_t_cluster,_p_permutacion_dia,icc_y_deff}; N_BOOT_DIA=4000, N_PERM_DIA=4000.
