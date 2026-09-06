# Qué se aplicó de los dos dictámenes

**6-Sep-2026 19:21** (hora de Chile, leída del reloj). Lo escribió el orquestador de la
sesión, no los dictaminadores. Los dictámenes son `guardian_constitucion.md` y
`curador_epistemico.md`; esto es sólo el registro de ejecución.

**Veredictos:** guardián **APROBADO CON EXIGENCIAS** (7). Curador **RECHAZADO**
(7 bloqueantes, 30 exigencias). Los veredictos quedan como se emitieron: aplicar
las exigencias no los convierte en aprobaciones.

## Guardián — 7 de 7 aplicadas

| # | Qué exigía | Dónde quedó |
|---|---|---|
| 1 | El ratio suelto sin marca de retiro en la docstring del árbitro | `cifras.py`, `doce_bloques`; `reintroducciones()` da `[]` |
| 2 | Commitear la corrección del censo de gap cero con errata y suite verde | `tests/test_linea_base.py` (+2 tests verdes con el mismo defecto); errata en `verificacion_arbol_skip_tests.md` y acta §79 |
| 3 | Corregir el IC del ΔMAE en el ejecutable, no en la prosa | `GEMELO/control_lineal.py`, `GEMELO/relevo_asiatico.py`, `GEMELO/experimento.py`; test cambiado de sujeto en `tests/test_relevo_asiatico.py` + uno nuevo |
| 4 | Declarar que el dedup nuevo toca un insumo sellado | `DECISIONES.md` §78.4 bis; `espera_firma.md` §38 |
| 5 | «(V1 secundaria)» contradice al agente | `DECISIONES.md` §78.1, errata fechada |
| 6 | Hito de cierre faltante en la bitácora | `bitacora_09.md`, sección del 6-sep |
| 7 | Anotación fechada bajo la línea 45 del encargo | `encargo_corrida_09.md`, sin tocar el texto de Nicolás |

**Lo que el guardián dejó como NO VERIFICADO por él, y esta sesión resolvió:**
si la suite del hook tocó la red dentro de la ventana de sellado del 3-sep. **Sí
la toca**: `motor._datos_crudos` llama a `yf.download` con caché sólo en memoria.
Regla cruzada, sin daño: el sello de las 18:15 salió 28/28 y a la hora.

**Lo que el guardián inventarió y NO se tocó** (su propia instrucción: barrido en
tanda propia): el resto de `.py` con cifras retiradas sin marca fuera de los tres
que el curador nombró, y el `Pandas4Warning` de `api/main.py` y
`backtest/baselines.py`, que espera la misma firma que `motor_concat.diff`.

## Curador — 30 de 30 aplicadas

| # | Archivo | Qué |
|---|---|---|
| 1 | `cifras.py` | `mae_ganancia_pp`, `mae_ganancia_ic_t_dia`, `mae_ganancia_p_dia`; bloque 8 extendido. Reproduce lo que midió el curador: +0,4547, [−0,087, +0,996], p 0,101 |
| 2 | `README.md` | La fila del MAE deja de decir que la magnitud aporta |
| 3 | `estado_epistemico.md` | Punto 8 reescrito, con el intervalo a la vista |
| 4, 5 | `README.md` | Las filas WS2b/WS3 y la conclusión de «Lo que la información expandida aporta» |
| 6–9 | `README.md` | El titular: el escalón es MEDIDO, el mecanismo es PROPUESTA cuya predicción falló |
| 10 | `README.md`, `estado_epistemico.md` | La ventana larga, con la advertencia del caché v1 |
| 11, 12 | `ESTADO.md` | D3 como DECISIÓN PENDIENTE; los dos dictámenes declarados |
| 13 | `estado_epistemico.md` | El encabezado de la novena corrida dice qué dictámenes faltaron |
| 14 | `GEMELO/bifurcaciones.py` | Las cadenas de salida dejan de llamar «publicada» a la rama derogada (más dos ocurrencias que el barrido encontró en el mismo archivo) |
| 15 | `GEMELO/simulador/potencia_por_metrica.py` | El ratio se computa de las filas; el literal se fue |
| 16–19, 22, 23, 27–29 | `README.md`, `ESTADO.md`, `estado_epistemico.md` | Erratas: el N del DSR, el badge, permisos, ancla de la frase de potencia, régimen, cobertura del percentil, n del holdout, días junto a n, «+ coherencia» sin intervalo |
| 20, 21, 26 | `estado_epistemico.md` | «sobre la publicada», el censo de verificaciones, la frase final |
| 24 | `bitacora_09.md`, `cifras_retiradas.md` | Marcas inline y tres patrones nuevos en el registro |
| 25 | `bitacora_09.md` | La verificación mecánica deja de presentarse como sustituto del dictamen |
| 30 | `GEMELO/SECUENCIAL/mde_vs_observado.py` | El comentario en pasado |

**O19, observación sin exigencia, también corregida:** el roadmap decía que la
auditoría adversarial «hizo dos pasadas»; van nueve corridas.

**Zonas ciegas del curador que siguen abiertas** (no las cerró esta sesión):
las cifras de WS3/WS4/WS5 no se recomputaron (exigen descarga y firma); la ruta 3
del horizonte y el tipo I de la conjunción no se relanzaron; `bifurcaciones.md`
no se regeneró tras D1; y no hay libro mayor por máquina de los 66 incrementos
del registro de intentos.

## Lo que ninguna exigencia cubre y queda para Nicolás

El conflicto de D3 —«contra predecir cero» contra la climatología causal que
exige el adversario— sigue sin resolver (`espera_firma.md` §30), y ahora también
el bump de `FEATURE_VERSION` por el dedup de noticias (§38). Nada se publicó.
