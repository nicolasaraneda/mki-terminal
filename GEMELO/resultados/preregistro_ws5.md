# WS5 — pre-registro DECLARADO ANTES DE CORRER NADA

**Etapa 6.0.0 · WS5 · 30-ago-2026**

Este archivo se escribe y se deja en el árbol **antes** de ejecutar una sola
configuración. Lo que se mide después se mide contra esto.

---

## 1. ORIGEN: POST-HOC. Sin eufemismos.

**Esta hipótesis se formó DESPUÉS de ver el desglose por bolsa del WS4.**

El WS4 no salió a buscar el efecto asiático: apareció mientras se auditaba
otra cosa. La hipótesis del relevo es una **explicación construida sobre un
patrón ya visto**, y eso la pone en una categoría distinta de todo lo anterior
de la 6.0.0:

- El WS2b y el WS3 declararon sus configuraciones antes de mirar sus datos.
- **El WS5 no puede hacer eso.** Su pregunta nació del resultado.

Consecuencias que se asumen por escrito:

1. **Es exploratorio, no confirmatorio.** Ningún resultado de aquí puede
   leerse como "confirmado". Como mucho, "no refutado".
2. **Cuenta como intentos nuevos para el DSR** (§2).
3. **El holdout en cuarentena es la única defensa real** y aquí importa más
   que en ninguna etapa previa (§5) — y está **parcialmente contaminado**,
   lo que también se declara.

---

## 2. N PARA EL DSR — declarado antes de correr

Regla congelada en `GEMELO/DISEÑO.md` §4.2 bis: **un intento = (configuración
× ventana de evaluación) con resultado reportable.**

| Origen | Intentos |
|---|---|
| B0→B5 sobre la ventana del backtest | 6 |
| C1,C2,C3 sobre la ventana sellada (WS2b) | 3 |
| C1,C2,C3 sobre la ventana larga (WS3) | 3 |
| Campeón reconstruido sobre la ventana larga (WS3) | 1 |
| **E1,E2,E3 × {XETR, ASIA} × {exploración, holdout} (WS5)** | **12** |
| **N_WS5** | **25** |

Las doce salen de aplicar la regla **mecánicamente**, no por conveniencia:
tres configuraciones, dos estratos de evaluación, dos porciones temporales, y
las doce son reportables. Contarlas de otro modo sería elegir el N que
favorece el DSR, que es exactamente lo que el DSR existe para castigar.

**Lo que NO suma a N:**

- La búsqueda de `alpha` por CV temporal: es interna al fold y jamás mira una
  fila de evaluación (§4.2 bis).
- El desglose descriptivo por bolsa dentro de ASIA: el ajuste **tiene** que
  ser por bolsa (§4, la trampa), pero el resultado reportable es el del
  estrato. **Si alguna decisión se tomara mirando ese desglose, N sube a 31 y
  hay que decirlo.**
- La baseline "siempre al alza": es la hipótesis nula, no un modelo ajustado.

**No se añadirá una cuarta configuración.** Si se añadiera, N pasa a 33 y se
recalcula todo. Esa tentación es literalmente el sesgo que el DSR mide.

---

## 3. LAS TRES CONFIGURACIONES — declaradas antes de correr

Objetivo: el **gap de apertura**, sobre la ventana larga (~8 años).

| | Features | Papel |
|---|---|---|
| **E1** | `sox_t`, `sox_t1` | **CONTROL** — la información actual del sistema |
| **E2** | cierres asiáticos (`ks11_ret`, `twii_ret`, `n225_ret`) **menos el índice de la propia bolsa** | el relevo |
| **E3** | E1 + E2 | ambos |

Maquinaria idéntica en las tres, y la misma del WS2b/WS3: ridge en forma
cerrada, walk-forward **expansivo**, **embargo de 5 días**, `alpha` por CV
temporal dentro de cada ventana de entrenamiento, McNemar con corrección de
continuidad, MAE, CRPS normal, bootstrap **circular** de bloques.

**Convención del empate: `excluir_cero`, la congelada en §2.8** — las filas
con `gap == 0.00` se descartan de AMBOS lados. Es la que el WS3 **no aplicó**
y que le infló la ventaja en 0.24 pp (WS4, Amenaza 3). Aquí se aplica desde
la primera línea.

---

## 4. LA TRAMPA, Y CÓMO SE EVITA

**Para un objetivo asiático, su propio índice local es casi circular:**
Samsung está dentro del KOSPI, TSMC dentro del TWSE. Un `ks11_ret` como
feature de `005930.KS` no es "el relevo asiático": es una parte del propio
retorno del objetivo entrando por la puerta de atrás.

Si no se excluye, **E2 luciría espectacular en Asia por la razón equivocada** y
la prueba de simetría concluiría lo contrario de lo que los datos dicen.

**Regla: se excluye SIEMPRE el índice de la bolsa del objetivo.**

| Bolsa del objetivo | Índice excluido | E2 efectivo |
|---|---|---|
| XKRX | `ks11_ret` | `twii_ret`, `n225_ret` |
| XTAI | `twii_ret` | `ks11_ret`, `n225_ret` |
| XTKS | `n225_ret` | `ks11_ret`, `twii_ret` |
| XETR | (`^GDAXI` no está en E2) | `ks11_ret`, `twii_ret`, `n225_ret` |

Como el conjunto excluido depende de la bolsa, **el ajuste es por bolsa**. Eso
NO es una configuración extra: es la única forma de que la regla se cumpla.

**Esto va como TEST, no como comentario.**

---

## 5. EL HOLDOUT EN CUARENTENA — y su contaminación, declarada

**Corte:** el **último 20% de las fechas de emisión** de la ventana, por orden
cronológico. Todo lo anterior es *exploración*; el holdout se lee **una sola
vez**, al final, y es el que emite el veredicto.

La cuarentena aquí es **procedimental**: las tres configuraciones, la regla de
decisión (§6) y el N (§2) quedan fijados en este archivo antes de correr, así
que no hay nada que ajustar mirando el holdout.

**CONTAMINACIÓN QUE SE DECLARA:** la observación que generó la hipótesis —el
+2.5 pp de Fráncfort del WS4— se midió sobre la **ventana completa**, holdout
incluido. El holdout está en cuarentena frente a las **decisiones de este
experimento**, no frente al hecho que lo motivó. Es una cuarentena **parcial**
y llamarla completa sería mentir.

---

## 6. LA REGLA DE DECISIÓN — declarada antes de ver un número

**Criterio primario (el que decide): E2 contra E1, pareado, en DIRECCIÓN,
sobre el HOLDOUT.**

> «E2 mejora a E1» ⟺ ventaja direccional > 0 **y** McNemar p < 0.05.

Se elige la dirección y no la magnitud porque el hallazgo que se está
explicando (+15.66 pp) es direccional. MAE, CRPS y E3 son **secundarios y no
deciden**.

| Resultado | Lectura |
|---|---|
| E2 mejora a E1 en **XETR** y **NO** en ASIA | **hipótesis del relevo NO REFUTADA** |
| E2 mejora a E1 en **las dos** | **REFUTADA** — no es relevo, es capacidad: añadir regresores mejora en todas partes |
| E2 **no** mejora a E1 en XETR | **REFUTADA** — el relevo no aporta donde debería |
| E2 no mejora en XETR pero **sí** en ASIA | **REFUTADA, y al revés de lo predicho** |

«NO REFUTADA» es el techo alcanzable. Una hipótesis post-hoc no se confirma
con los datos que la sugirieron.

---

## 7. DISPONIBILIDAD — se demuestra, no se asume

Emisión del sistema: **22:15 UTC** del día D.

Lo que hay que probar para que la relación sea causal en Fráncfort: la
apertura de XETR del día **D+1** ocurre **después** del cierre asiático del día
**D**. Va como **test** contra `calendarios.apertura_utc` (calendarios
históricos reales) y `datos.CATALOGO` (cierres sellados en WS2a), no como
afirmación.

**Y hay que medir la otra mitad**, que la hipótesis no menciona: a las 22:15
UTC del día D, el `^SOX` de D tiene 1.25 h de antigüedad y el `^KS11` de D
tiene 15.75 h. **Bajo la restricción de emisión del sistema, el insumo asiático
disponible es el MÁS VIEJO, no el más fresco.** La sesión asiática que el
relato describe —la que ocurre entre el cierre del SOX y la apertura de
Fráncfort— cierra el día D+1 y **no es conocible a la emisión**. Se medirá y
se reportará: cambia qué significa un resultado nulo.

---

## 8. LO QUE NO SE HACE

- **NO se toca `universo.py`.** Sacar IFX.DE porque aporta poco sería quitar
  el dato incómodo, y además es cambio de universo → `UNIVERSO_VERSION` →
  territorio del modelo congelado.
- **NO se toca `motor.py`, `senales.py`, `snapshot.py` ni el camino de
  sellado.**
- **NO se corre el veredicto escalonado de la 5.1.**
- **No se añade una cuarta configuración** (§2).
- **No se corrige ningún reporte previo** ni ninguna conclusión ya publicada.

---

Herramienta de análisis — no constituye asesoría financiera.
Diseño congelado en `GEMELO/DISEÑO.md`. **No es el veredicto de la 5.1.**
