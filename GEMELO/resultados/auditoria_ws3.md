# Auditoría adversarial del WS3 (Etapa 6.0.0 · WS4)

**Fecha:** 26-ago-2026 · **Objeto:** el hallazgo de **+15.9 pp** de ventaja
del campeón sobre la tasa base sobre 14.711 filas.

**Postura:** este trabajo no verificó que el cálculo estuviera bien. Buscó por
qué podría estar **inflado**. Un hallazgo que debilite el número vale más que
uno que lo confirme.

---

## VEREDICTO

**El +15.9 pp SOBREVIVE, con dos correcciones y una limitación estructural
que no estaba declarada.**

| | Ventaja | McNemar p |
|---|---|---|
| Publicado en WS3 | +15.90 pp | ≈0 |
| **Corregido (convención congelada §2.8)** | **+15.66 pp** | **≈0** |

La corrección es de **−0.24 pp**: real, pequeña, y no cambia la conclusión.

**Pero la ventaja NO es homogénea, y eso sí cambia cómo debe leerse:**

| Bolsa | n | Modelo | Base | Ventaja | p |
|---|---|---|---|---|---|
| XTKS (Tokio) | 7.230 | 72.9% | 53.8% | **+19.1 pp** | ≈0 |
| XTAI (Taipéi) | 1.807 | 72.0% | 55.2% | **+16.8 pp** | ≈0 |
| XKRX (Seúl) | 3.626 | 71.2% | 55.8% | **+15.4 pp** | ≈0 |
| **XETR (Fráncfort)** | **1.955** | **57.2%** | **54.7%** | **+2.5 pp** | **0.111** |

**El efecto es asiático. En Fráncfort no es distinguible de cero.** Y hay una
explicación mecánica coherente: el margen entre la emisión y la apertura es de
**1.75 h en Seúl y Tokio, 2.75 h en Taipéi y 8.75 h en Fráncfort** (medido, §5).
Cuanto más tiempo pasa, menos queda del contagio.

Dos amenazas resultaron **inofensivas y está medido**; una resultó
**NO EVALUABLE** con los datos disponibles y se declara como tal; y una
**refuta un hallazgo que el propio WS3 había publicado**.

---

## Amenaza 1 — Sesgo de supervivencia

**Qué se buscó:** que los 28 tickers de `universo.py` sean los que sobrevivieron,
aplicados hacia atrás ocho años.

**Canal de ENTRADA TARDÍA — medido, y es CERO.**

De los 27 tickers con datos, **26 tienen historia completa desde el inicio de
la ventana (2018-08-27)**. El único que empieza tarde es **ARM (2023-09-14,
su OPV)** — y ARM **no es un ticker objetivo**. Los **8 objetivos**
(005930.KS, 000660.KS, 2330.TW, 8035.T, 6857.T, IFX.DE, 4063.T, 3436.T)
**tienen historia completa en toda la ventana**.

Por tanto: **la comparación restringida a tickers de historia completa es
idéntica a la comparación completa.** No hay nada que restringir. El +15.9 pp
no debe un solo punto a entradas tardías.

**Canal de SALIDA — la cota.** Las empresas que salieron de la cadena no están
en `universo.py` y no se pueden recuperar sin una lista histórica de
constituyentes que no tenemos. Se acotó por regresión: ventaja por ticker
contra su retorno en la ventana.

- Correlación cruda (retorno, ventaja) sobre los 8: **+0.368**.
- Pero está **confundida con la bolsa**: IFX.DE es a la vez el de menor
  ventaja (+2.5 pp) y el único europeo. Quitando el confusor y ajustando solo
  sobre los 7 asiáticos: **b = +0.60 pp por unidad de log-retorno, R² = 0.051**.
  Es decir, **prácticamente plano**.
- Extrapolando a un ticker con retorno **−90%**: ventaja predicha **15.2 pp**.
- Si una fracción *f* del universo hubieran sido salidas con esa ventaja:

| f | Ventaja global estimada |
|---|---|
| 5% | 15.9 pp |
| 10% | 15.8 pp |
| 20% | 15.8 pp |
| 30% | 15.7 pp |

**Cota: menos de 0.2 pp incluso suponiendo que el 30% del universo hubieran
sido salidas.**

**⚠ La cota es frágil y hay que decirlo.** n = 7, R² = 0.05, y **todos los
retornos observados son positivos** (+105% a +5948%): predecir en −90% es
extrapolación pura. Y hay un mecanismo que la regresión **no puede capturar**:
una empresa en dificultades se **desacopla** del sector porque su noticia
idiosincrática domina, y ese es justamente el régimen donde el contagio del
SOX fallaría. **Esa parte queda NO EVALUABLE**, no acotada.

---

## Amenaza 2 — Precios ajustados retroactivamente

**Qué se buscó:** que el `open(t)` y el `close(t−1)` vinieran de bases de
ajuste distintas, o que un split cayera entre los dos.

**Resultado: INOFENSIVA, y está medido con el dato más duro disponible.**

Se despejó el cierre de referencia que el verificador usó en cada una de las
**223 filas selladas** y se comparó con la historia de hoy:

> **Desviación máxima: 0.00%. En las 223 filas.**

Los gaps sellados en julio-agosto de 2026 se reproducen **exactamente** con la
descarga de hoy. La razón es estructural: el factor de ajuste se aplica a
todos los precios anteriores a la fecha ex **por igual**, así que escala el
`open` y el `close` previo por el mismo número y **la razón se conserva**.

**Corolario incómodo:** la "contaminación por revisión del 91.4%" que el WS3
publicó **es falsa**. Ver Amenaza 7.

---

## Amenaza 3 — La tasa base

**Qué se buscó:** que el 54.2% no estuviera calculado sobre exactamente las
mismas filas que el 70.1%.

**Universo, sesiones y filtro: SIMÉTRICOS.** `cl.evaluar` deriva ambas series
del mismo `DataFrame` y de la misma columna `gap`. No hay asimetría posible ahí.

**Pero SÍ hay una asimetría, y es la de la §2.8 reintroducida.** El WS3 puntúa
al modelo con `(pred>=0)==(gap>=0)` y a la baseline con `gap > 0`. Las filas
con `gap == 0.00` exacto se le regalan al campeón y se le niegan a la
baseline — el mismo sesgo que la §2.8 congeló para la ventana sellada y que el
WS3 **nunca aplicó**.

**Magnitud medida:** 105 filas de 15.033 (**0.70%**) tienen `gap == 0.00`.

| Convención | n | Modelo | Base | Ventaja |
|---|---|---|---|---|
| `estricta` (la del WS3) | 14.711 | 70.14% | 54.25% | **+15.90 pp** |
| `verificador` (simétrica) | 14.711 | 70.14% | 54.88% | +15.27 pp |
| **`excluir_cero` (congelada §2.8)** | **14.618** | **70.25%** | **54.59%** | **+15.66 pp** |

**El WS3 infló la ventaja en 0.24 pp por no aplicar su propia convención
congelada.** Es el número corregido del veredicto.

---

## Amenaza 4 — Fuga en el camino largo

**Qué se buscó:** que truncar la entrada alterara predicciones anteriores.

**Resultado: INOFENSIVA, con contraprueba.**

- Truncar el panel en una fecha T **no altera ninguna** predicción de fecha
  < T (igualdad exacta de todo el frame).
- El emparejamiento sesión→emisión es **estrictamente anterior** en el 100% de
  los casos, y truncar el índice de features no cambia asignaciones previas.
- **Contraprueba:** con un embargo **negativo** —que hace que el entrenamiento
  incluya filas posteriores a la emisión— el mismo criterio **sí** detecta la
  diferencia. El test puede fallar, luego prueba algo.

Todo fijado en `tests/test_auditoria_ws3.py`.

---

## Amenaza 5 — Calendarios a ocho años

**Qué se buscó:** que la regla "conocible a las 22:15 UTC" no se sostuviera en
2018 igual que en 2026 (feriados, horarios de verano, cambios de sesión).

**Resultado: INOFENSIVA, y medida sobre los calendarios reales.**

Se verificaron los **15.033** pares (sesión, ticker) contra
`calendarios.apertura_utc`, que usa los calendarios históricos reales de cada
bolsa:

> **Violaciones (apertura ≤ emisión): 0.** Margen mínimo global: **1.75 h**.
> Pares con margen < 1 h: **0**.

Margen mínimo por año y bolsa — **si un horario hubiera cambiado, se vería**:

| Año | XETR | XKRX | XTAI | XTKS |
|---|---|---|---|---|
| 2018 → 2026 | 8.75 | 1.75 | 2.75 | 1.75 |

**Perfectamente estable los nueve años.** Ni el cambio de cierre del TSE
(15:00 → 15:30 JST, nov-2024) ni ningún horario de verano acercó una apertura
a la emisión.

Este cuadro es además la **explicación mecánica** del veredicto: Fráncfort
tiene 8.75 h de margen y +2.5 pp de ventaja; Tokio y Seúl tienen 1.75 h y
+19.1 / +15.4 pp.

---

## Amenaza 6 — Cambios de instrumento

**Qué se buscó:** splits, cambios de ticker y fusiones mal empalmados.

**Resultado: INOFENSIVA, y medida.**

Splits declarados por la fuente dentro de la ventana:

| Ticker | Fecha | Ratio |
|---|---|---|
| 8035.T | 2023-03-30 | 3:1 |
| 4063.T | 2023-03-30 | 5:1 |
| 6857.T | 2023-09-28 | 4:1 |

Gaps extremos (|gap| > 20 pp): **4 de 15.033 (0.03%)**, y **ninguno coincide
con una fecha de split**. Los cuatro son eventos de mercado reales
(2026-07-30 Corea +28%/+24%, 2024-08-07 3436.T −25%, 2025-04-09 IFX.DE +23%).

`auto_adjust=True` manejó los tres splits correctamente. Distribución de
|gap|: mediana 0.90 pp, p99 6.99 pp, máximo 28.37 pp.

---

## Amenaza 7 — La coincidencia del 91.4%

**Qué se buscó:** que el emparejamiento (fecha, ticker) entre reconstrucción y
sellos tuviera desfase, y si las 17 discrepancias estaban de verdad
concentradas.

**Resultado: EL 91.4% ERA UN ARTEFACTO DEL JOIN. La cifra correcta es 100%.**

Las 17 filas "revisadas" no eran revisiones de Yahoo: eran filas emparejadas
con **otra sesión objetivo**.

El panel del WS3 empareja cada emisión con la **siguiente sesión de
calendario**. El verificador usa la siguiente sesión **al sello real**, y en un
**sello tardío** ésa puede saltarse una sesión completa. El 29-jul el sello
salió tarde (documentado en la auditoría de julio) y su `sesion_objetivo`
declarada es **2026-07-31**, no 07-30. El panel comparó peras con manzanas.

Alineando por `sesion_objetivo`, las **223** filas selladas reproducen con
**desviación 0.00%**.

**Consecuencia:** la sección "La contaminación por revisión, medida" del
reporte de WS3 (`ventana_larga.md`) es **incorrecta** y debe corregirse. La
contaminación por revisión retroactiva medida sobre las filas selladas es
**cero**, no 8.6%.

---

## El 29-jul: la hipótesis del WS3, REFUTADA

El criterio objetivo se declaró **antes** de correrlo, en
[`criterio_rancio_declarado.md`](criterio_rancio_declarado.md), con el sesgo
nombrado: excluir esas filas **sube** el 65.9% publicado.

**Criterio:** desviación entre el cierre de referencia implícito del sello y
el cierre real de la sesión previa según la historia de hoy. **Umbral: 5%**,
fijado antes de mirar.

> **Resultado: 0 filas de 223 superan el umbral. Máximo observado: 0.00%.**

**No hay cierres previos rancios. La hipótesis del WS3 §32.5 queda refutada,
y era mía.** Lo que ocurrió el 29-jul no es un dato corrupto: es una
**predicción emitida tarde cuya sesión objetivo saltó una sesión**, que es
exactamente el fenómeno que el acta de la 5.0.2 ya documentó y para el que ya
existe una regla de abstención **propuesta y no implementada**. Los gaps de
+28% y +24% de esa noche son **reales** y se reproducen exactamente.

**Efecto sobre el número publicado: ninguno, porque no hay nada que
excluir.** El 65.9% de la ventana sellada se mantiene tal cual.

---

## Preguntas abiertas — requieren criterio de Nicolás

1. **¿Se corrige la ventana larga a la convención congelada?** El número
   publicado del WS3 (+15.90 pp) usa la convención asimétrica; el correcto
   bajo la §2.8 es **+15.66 pp**. Corregirlo implica re-emitir
   `ventana_larga.md`. No se tocó nada.

2. **¿Se corrige la sección de "contaminación medida" del WS3?** Es
   incorrecta (Amenaza 7): dice 91.4% de coincidencia cuando la cifra real es
   100%. Está publicada en `GEMELO/resultados/ventana_larga.md` y en
   `DECISIONES.md` §32.4.

3. **¿Qué se hace con `DECISIONES.md` §32.5?** Contiene una hipótesis
   —"el 29-jul huele a sello corrupto"— que esta auditoría **refuta**. No se
   modificó ninguna conclusión existente, según la instrucción; esta sección
   queda como el registro de la refutación. La decisión de cómo reconciliar
   ambas es humana.

4. **¿Cómo se reporta el hallazgo de Fráncfort?** El efecto es asiático:
   XETR da +2.5 pp con p = 0.111. Publicar "+15.9 pp" sin ese desglose es
   promediar un efecto fuerte con uno ausente.

5. **¿Las 8 filas del 29-jul (sesión saltada) deben seguir en las métricas?**
   No son datos corruptos, pero son la clase de predicción que la regla de
   abstención propuesta habría excluido. Es la misma decisión pendiente desde
   la 5.0.2, ahora con un caso concreto dentro de las 223.

---

## Amenazas NO evaluadas o evaluadas a medias

Se declaran para que nadie las lea como cerradas.

- **Amenaza 1, canal de salida: NO EVALUABLE.** Sin una lista histórica de
  constituyentes de la cadena no se puede reconstruir el universo real de
  2018. La cota por regresión es **frágil** (n=7, R²=0.05, extrapolación fuera
  del rango observado) y **no captura** el mecanismo de desacople
  idiosincrático de una empresa en dificultades.
- **Cambios de ticker y fusiones: evaluados solo parcialmente.** Se
  verificaron splits declarados por la fuente y gaps extremos. Un cambio de
  símbolo que Yahoo hubiera empalmado silenciosamente **no dejaría rastro** en
  ninguna de las dos pruebas.
- **La ventana larga sigue sin ser point-in-time** en lo que respecta a la
  *composición* del universo, aunque sí lo sea en los precios (Amenaza 2). Son
  dos cosas distintas y solo una quedó cerrada.
