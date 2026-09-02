# La fuente canónica — expediente del Frente A (séptima corrida, 2-sep-2026)

**Qué es esto.** El planteo, medido, de una pregunta que el proyecto tiene
abierta desde que Yahoo dejó de servir la sesión del 2026-08-28: **si la
fuente puede cambiar el pasado, ¿qué garantiza un sello?** Este documento
mide cuánta historia mutó, pone las candidatas a fuente canónica una al
lado de la otra con lo que rompe cada una, y diseña la que hoy no existe.
**No elige.** La elección lleva la firma de Nicolás (§6).

**Toda cifra sale de `GEMELO/fuente_canonica.py`** (`senales.db` en
`mode=ro`, cachés no reescritas, ninguna fila tocada) y está en
`fuente_canonica.json` / `fuente_canonica_medicion.md`. Nada está cableado
en la prosa. Las contrapruebas del clasificador están en
`tests/test_fuente_canonica.py`.

> **EN DIEZ SEGUNDOS**
>
> 1. **Yahoo no reescribe la historia. La sirve con intermitencia.** Sobre
>    8 años × 27 tickers (52.507 celdas), entre el 26-ago y hoy **no cambió
>    un solo retorno diario, no retiró ninguna barra y no apareció
>    ninguna**. Cambió niveles en 1.953 celdas, **todas de un solo ticker
>    (000660.KS), reescalado proporcional por un factor constante 0,999783**
>    (`auto_adjust`), que las señales no ven. *(La primera redacción decía
>    «1.962 celdas, todas dividendos, en varios tickers» y citaba factores
>    que eran la barra viva de Tokio a medio día: lo cazó el adversario.)*
> 2. **Lo que sí hace es servir el mismo query en estados distintos.** El
>    28-ago retiró una sesión (1 fecha en 752, 0,13%). Y hay un segundo
>    fenómeno que nadie había visto: **cuatro noches de agosto (12, 14, 19,
>    20) las betas selladas sólo reproducen si el `^SOX` NO tenía la barra
>    del 31-jul**, y las noches vecinas reproducen con ella. Hipótesis
>    ejecutable (M6), desvío máximo de beta 0,25–0,27 → 0,026–0,042.
> 3. **El sello guardó datos que la fuente después no servía, y tenía
>    razón.** Las 8 predicciones del 28-ago (SOX −3,47%, hoy inexistente)
>    acertaron 8/8 el gap del 31-ago. Reconstruidas desde el Yahoo de hoy
>    dan signo contrario y fallan 8/8.
> 4. **`ESTADO.md` quedó atrás en un punto:** las 16 filas de signo contrario
>    ya no están `pendiente`. **15 están verificadas desde el sello de las
>    18:15 del 1-sep y dentro del track record vivo (n=276).** El README no
>    se mueve porque su cifra está anclada al 28-ago.
> 5. **El proyecto tiene la mitad de un sello.** Tiene *«emitido antes,
>    probado por timestamps»*; **no tiene *«reproducible después»***, porque
>    guarda derivados a dos decimales, no los insumos. La otra mitad ya
>    existe como arnés probado y no activado (`GEMELO/INSUMOS/`); cablearla
>    cuesta una llamada protegida en la ruta de sellado, **~9 MB/año
>    medidos** (130 barras consumidas) y un corte de método con fecha.
>    **Recomendación marcada como tal: construirla.** Firma de Nicolás.

---

## 1. La pregunta, bien planteada

Un sello del proyecto garantiza hoy **una** cosa, y la garantiza bien: que
la predicción fue emitida **antes** del evento, probado por `timestamp_utc`
contra la apertura UTC de la sesión objetivo. Es la regla maestra de la
Etapa 4.6, y nada de lo que sigue la toca.

Lo que **no** garantiza es que la predicción sea **reproducible después**:
que alguien, mañana, pueda volver a pedirle a la fuente los mismos insumos
y obtener la misma cifra. Son dos propiedades distintas:

| Propiedad | Qué exige | ¿El proyecto la tiene? |
|---|---|---|
| **Emitida antes** | timestamps, calendario, verificador | **Sí**, desde la 4.6 |
| **Reproducible después** | una copia de los insumos tal como se consumieron | **No.** Guarda derivados a 2 decimales (`sox_usado_pct`, `beta`, `apertura_estimada_pct`), que alcanzan para *detectar* una divergencia, no para *reproducir* una corrida |

Todo lo que reconstruye al campeón —`backtest/`, `GEMELO/ventana_larga.py`,
`CONDICIONAL/`, el veredicto 5.1— vive en la segunda columna. Por eso el
28-ago los bloquea: no porque el sello esté mal, sino porque **el sello y la
reconstrucción son dos objetos distintos, y el proyecto nunca declaró cuál
manda**.

## 2. Cuánta historia mutó — medido, no estimado

Seis testigos, cada uno con su fecha de captura y su resolución. Ninguno lo
inventé: son cosas que el proyecto ya guardaba sin usarlas como testigo.

| Testigo | Qué compara | Capturado | Resolución | Resultado |
|---|---|---|---|---|
| **M1** | `GEMELO/cache/` (8 años, 8 y 27 tickers) vs la fuente hoy | 26-ago 04:22Z | cierre crudo (float32) | **0 retornos cambiados, 0 barras retiradas, 1 aparecida** (IFX.DE, una celda histórica); 1.953 niveles reescalados proporcionalmente, todos de 000660.KS, factor 0,999783; 26 tickers con 0 celdas históricas distintas |
| **M2** | `snapshots.sox_usado_pct` (26 fechas) vs `^SOX` hoy, lógica de producción | cada sello, 22:15Z | 2 decimales | **24 PARIDAD, 1 BARRA_RETIRADA (28-ago), 1 BARRA_PREVIA_RETIRADA (31-ago)** |
| **M3** | `verificacion_apertura` (276 filas) vs Open/Close hoy, lógica del verificador | cada verificación | 4 decimales | **271 PARIDAD + 5 ruido del 4º decimal. 0 aciertos cambian.** |
| **M4** | `senales_ticker` (287 filas, 38 fechas) vs `motor.prediccion_apertura_al` hoy | cada sello | 2 decimales | **197 PARIDAD, 90 DIVERGENCIA; 16 con el signo dado vuelta** |
| **M6** | hipótesis: ¿una barra ausente del `^SOX` explica una fecha? | — | — | **Sí: la del 31-jul, para las 4 fechas** (12, 14, 19, 20-ago) |
| **M5** | censo de sesiones de calendario sin barra hoy (3 años, 28 símbolos) | hoy | — | 2 para `^SOX` (2023-09-01 = borde de ventana, 2026-08-28); ARM 9 (pre-IPO); KS/TW 3–4 (feriados no modelados). **No distingue causa**: sólo M1–M4 pueden decir «estaba y ya no está» |

### 2.1 Las tres clases de mutación observadas, y una cuarta sin explicar

**(a) Reescalado proporcional.** 1.953 celdas en 7 días, **todas de un
solo ticker, 000660.KS, con factor constante 0,999783** (a 4e-7 sobre los 8
años); los otros 26 tickers tienen **0 celdas históricas distintas**. **El
retorno diario no cambia** (máximo |Δr| = 1,2e-6, ruido de float32). Es el
teorema del expediente PIT (acta §49) observado en vivo: los factores de
ajuste se cancelan en todo cociente. **Inocuo para señales; letal para
cualquiera que guarde niveles y compare niveles.** Nadie en el proyecto
guarda niveles. Bien. *(Corrección tras el dictamen: la primera versión
contaba 1.962 celdas «en varios tickers» y citaba como factores 0,9868 /
1,0148 / 0,9979 — eran la última celda de la caché, la barra de Tokio a
medio día, que dos cachés tomadas con 95 s de diferencia muestran moviéndose
(000660.KS −1000, 8035.T −70, 6857.T −10). El clasificador ahora separa la
última fecha de toda cuenta histórica, con contraprueba.)*

**(b) Retiro de una sesión entera.** 2026-08-28, `^SOX` y 10 de 19 símbolos.
Tasa 1/752 = 0,13%, IC95 Wilson [0,02, 0,75] (acta §69). Ventana en que
desapareció, **estrechada esta noche** con dos testigos nuevos: la corrida
del backtest `20260901-061708` (fuente congelada bajada antes de las
06:17Z) ya la reconstruye sin la barra, y las cachés de las 13:07Z/13:16Z
del 1-sep tienen `^SOX` NaN ese día. Existía a las 22:15:03Z del 31-ago
(aritmética del sello). **Ventana: ≤ 8 h, no ~18 h.** Sigue sin volver al
2-sep.

**(c) Intermitencia — el hallazgo nuevo.** Las betas selladas del 12, 14, 19
y 20-ago difieren de las que el motor produce hoy en hasta 0,27 (000660.KS
sellada 0,73, hoy 1,00; 005930.KS 0,52 vs 0,77), con `n_muestra = 120` en
los dos lados y r² sellado sistemáticamente menor. Las del 13, 17, 18 y
21-ago reproducen 8/8. Ni FX caído, ni últimas barras ausentes, ni cierre
del 31-jul distinto lo explican (probado). **Quitar la barra del `^SOX` del
2026-07-31 lo explica para las cuatro fechas a la vez**, y es la única
barra de 130 que lo hace:

| fecha de sello | max \|Δbeta\| con la fuente de hoy | barra cuyo retiro mejor explica | max \|Δbeta\| sin ella |
|---|---|---|---|
| 2026-08-12 | 0,254 | **2026-07-31** | 0,035 |
| 2026-08-14 | 0,274 | **2026-07-31** | 0,036 |
| 2026-08-19 | 0,269 | **2026-07-31** | 0,042 |
| 2026-08-20 | 0,258 | **2026-07-31** | 0,026 |

El mecanismo es aritmético: sin esa barra, `ret_sox.shift(1)` aparea el
+8,19% del SOX del 30-jul con los retornos del 3-ago (000660.KS −8,79%) en
vez de con los del 31-jul, y la beta OLS se desploma. **Es hipótesis, no
hecho, y el dictamen puso la vara:** el piso de reproducción en las noches
sanas es 0,004–0,007 y el residuo de M6 es 0,026–0,042, **4 a 8 veces el
piso** — el retiro de una barra explica ~87% del desvío y deja un resto que
no es redondeo. Verificado por el adversario con el perfil completo: 31-jul
es la única de 130 con desvío ≤ 0,05 en las cuatro fechas, brecha al segundo
0,035–0,057 (`dictamen_07/verif_m6.py`). **Lo que NO se probó**, declarado:
un cierre del 31-jul *revisado* en vez de ausente; retirar dos o más barras;
perturbar otra serie que no sea `^SOX` (la acción, el índice local, el FX);
y las cuatro fechas comparten ventanas de 120 días solapadas, así que no son
cuatro votos independientes. El único testigo que la convertiría en hecho
—una copia del `^SOX` de esas noches— no existe. Eso es, en sí mismo, el
argumento de la §5.

**Consecuencia medida:** 32 filas selladas (4 fechas × 8) cuyas betas y
aperturas no reproducen desde la fuente de hoy, **sin cambio de signo en
ninguna** (|Δapertura| ≤ 0,31 pp). El vigía las dio en verde (28/28) porque
el chequeo mira si hay *alguna* barra en 7 días, no si la serie es la de
ayer.

**(d) Residual sin explicar.** 45 filas más divergen en magnitud: mediana
|Δapertura| 0,01 pp, máximo 0,31, **ninguna cambia de signo**; 30 de 45 están
en ±0,02 (redondeo a dos decimales de una beta que se movió en el tercero).
Se concentran en julio (07-08 a 07-31), **antes de que existieran
`sox_usado_pct` y `beta`** en el sello: no hay testigo, y se declara así.
IFX.DE aporta 18 de 45 (beta ~0,05–0,13, donde una centésima es un 10%).

### 2.2 Qué NO mutó

- **La capa de verificación: 276/276.** Ni un Open ni un Close de las 8
  acciones objetivo cambió en dos meses (5 filas con ±1 en el 4º decimal
  son ruido de float). El gap y el retorno sellados son reproducibles hoy.
- **FX e índices locales entre el 1-sep 13:07Z y hoy: 0 celdas.**
- **Los retornos de 8 años, 27 tickers, entre el 26-ago y hoy: 0.**

## 3. Lo que el sello guardó, y lo que valía

Las 16 emisiones del 28 y 31-ago, contra lo que pasó después:

| emisión | SOX que usó el sello | SOX que sirve hoy | signo sellado | signo hoy | acierto sellado | acierto reconstruido |
|---|---|---|---|---|---|---|
| 2026-08-28 (8 filas → sesión 31-ago) | −3,47% (28-ago, barra hoy inexistente) | +2,33% (27-ago) | − | + | **8/8** | 0/8 |
| 2026-08-31 (8 filas → sesión 1-sep) | +0,57% (31/28) | −2,92% (31/27) | + | − | **0/7** (1 pendiente) | 7/7 |

**El sello del 28-ago vio un dato real que la fuente después retiró, y
acertó con él las ocho.** Reconstruido desde hoy habría errado las ocho. El
31-ago es el espejo: el sello, con la barra del 28 presente, erró las
siete; sin ella acertaría las siete. Neto bajo «Yahoo de hoy»: **8 aciertos
perdidos, 7 ganados** — McNemar de la sustitución **b = 8, c = 7, p = 1,00**;
acierto vivo 179/276 = 64,86% [59,1, 70,2] → 178/276 = 64,49% [58,7, 69,9];
MAE 2,827 → 2,892 pp sobre esas 15 filas (2,897 si se sustituyen las 87
filas verificadas con cualquier divergencia de magnitud: dos denominadores,
declarados). **La pregunta constitucional mueve la cifra viva en una
cantidad indistinguible de cero: importa por reproducibilidad, no por el
número.** Ninguna de las dos direcciones es «la correcta»: son dos objetos
distintos, y **el proyecto tiene que decir cuál es el campeón**.

## 4. Las candidatas a fuente canónica, con lo que rompe cada una

| | Candidata | Qué es | Qué se rompe | Qué cifras publicadas cambian |
|---|---|---|---|---|
| **C1** | **Yahoo vivo** (statu quo de toda reconstrucción) | Lo que la fuente sirve cuando se le pregunta | El sello deja de ser reproducible por construcción; 16 emisiones cambian de signo; 32 cambian de magnitud; toda corrida de `backtest/`, `ventana_larga`, `CONDICIONAL` y el 5.1 reconstruye un campeón distinto del sellado, y distinto entre corridas si la fuente vuelve a cambiar de estado | **README: ninguna** (n=248 anclado al 28-ago). **Track record vivo: 15 filas cambian de acierto** (8 se pierden, 7 se ganan). MAE +0,07 pp. |
| **C2** | **La copia derivada sellada** (lo que existe hoy) | `sox_usado_pct`, `beta`, `apertura_estimada_pct`, `gap_pct`, `retorno_real_pct` a 2–4 decimales | Nada publicado; pero **no permite reconstruir**: alcanza para detectar una divergencia (lo hizo esta noche), no para re-correr. `backtest` y el 5.1 siguen dependiendo de C1 | Ninguna |
| **C3** | **Copia cruda congelada al sellar** (a construir, §5) | Los frames exactos que `_datos_crudos` devolvió en el proceso que selló, con hash | Nada hacia atrás (el cierre del 28-ago sobrevive sólo como banda implícita [11.469,26, 11.470,24]); hacia adelante, cada predicción reproducible byte a byte. Toca `snapshot.py`: corte de método con fecha | Ninguna hoy; **fija para siempre** las de mañana |
| **C4** | **Segunda fuente** | Otro proveedor | No existe en el repo (acta §52); §49 recomendó no comprar; **no resuelve cuál es canónica: suma un voto**, y necesitaría el mismo congelado que C3 | Desconocidas |
| **C5** | **Híbrida** (recomendada para el 5.1) | Para la ventana sellada, **las filas selladas SON el campeón** (no se reconstruye: se lee); para la ventana larga, Yahoo con **fecha y hash de descarga declarados** | Exige que `backtest` B2 lea `senales_ticker` donde existe en vez de recomputar; la ventana larga queda declaradamente dependiente de la fuente y fechada | Ninguna; el veredicto 5.1 sobre la ventana sellada pasa a ser **independiente de la fuente** |

**Lo que las candidatas no pueden arreglar, ninguna:** los 45 residuos de
julio (sin testigo) y el cierre exacto del 28-ago (retirado antes de
copiarse). Eso está perdido y se declara perdido.

## 5. ¿Debe el proyecto congelar su copia? Diseño

**Recomendación, marcada como tal: sí.** La razón no es el 28-ago. Es que
esta noche, con cuatro testigos involuntarios y una hipótesis por fuerza
bruta, el proyecto pudo *inferir* qué vio producción el 14-ago. **Con una
copia lo habría leído.** La diferencia entre inferir y leer es la
diferencia entre una hipótesis (M6) y un dato.

### 5.1 Qué se congela

**Exactamente los bytes que el proceso que selló consumió.** No una
descarga paralela (dos procesos leyendo la misma fuente en el mismo minuto
pueden recibir estados distintos: es lo que M6 sugiere que pasó). Eso
significa leer `motor._cache` —el diccionario donde `_datos_crudos` deja
cada frame— **desde dentro del proceso de `snapshot.py`, después de sellar**.

| Serie | Filas/día (3 años) | Por qué |
|---|---|---|
| 27 tickers del universo + `^SOX` + 4 pares FX | ~750 × 32 ≈ 24.000 cierres | es lo que `betas_al` y `prediccion_apertura_al` consumen |
| Open/Close de las 8 acciones objetivo (verificador) | ~8 × 30 | lo que `_ohlc_local` bajó al verificar; hoy M3 dice que es estable, pero un testigo cuesta nada |

**Formato:** un `csv.gz` por sello en `data/insumos/AAAA-MM-DD.csv.gz`
(`serie, fecha_barra, campo, valor`). **Costo medido, no estimado** (arnés
`GEMELO/INSUMOS/insumos.py`, sobre el panel real de 37 series de la caché
del 1-sep): el panel de 3 años pesa **213 KB comprimido → ~53 MB/año**
(los precios no comprimen: son ruido); las **130 barras que el modelo
consume** (ventana de betas de 120 + margen) pesan **36 KB → ~9 MB/año**.
*(La primera redacción de este párrafo decía ~60 KB / ~15 MB/año a ojo;
corregido al medirlo, y la lección es la de siempre.)* Recomendación: la
ventana consumida completa por día, **más el sha256 del panel de 3 años
entero** (sin guardarlo), que basta para detectar que la historia lejana
cambió aunque no diga dónde. Y **una columna aditiva en `snapshots`:
`insumos_sha256`**. Con eso **el sello nombra sus insumos**: cualquiera
puede verificar que el archivo es el que la fila dice, sin confiar en
nadie.

**Por qué panel completo y no deltas.** Un delta contra «el panel de ayer»
exige que el de ayer sea íntegro, y un archivo por día es auditable solo.
15 MB/año no justifica la complejidad.

### 5.2 Dónde vive el código, y por qué toca la ruta de sellado

En `snapshot.py`, **una llamada** al final de `ejecutar_snapshot`, con la
misma disciplina que `_epilogo_vigia()`: envuelta en `try/except`, **jamás
puede romper el sello**; si falla, el vigía lo reporta al día siguiente
(«sello sin copia de insumos») y la fila queda con `insumos_sha256 = NULL`,
que es una ausencia declarada, no un cero. El módulo que escribe
(`insumos.py`, ~60 líneas) no importa nada del sellado: recibe el dict y la
fecha. `mki_backup.py` agrega `data/insumos/` a su pathspec.

**Esto es un cambio en `snapshot.py`.** Regla cero: no lo hace un agente.
Lleva **corte de método con fecha** (desde qué sello existe copia) y,
como el parche de `snapshot.py:140`, conviene que vaya con bump de
`PLATAFORMA_VERSION` para que cada fila diga de qué lado del corte está.

### 5.3 Qué cambia para el segundo sello

El diseño de `docs/SEGUNDO_SELLO.md` compara la fuente de hoy contra un
**derivado** (`sox_usado_pct`, 2 decimales, sólo `^SOX`). Con C3 compara
contra el **panel completo** y su resolución pasa de «el último retorno del
SOX» a «cada celda de cada serie». Los veredictos se enriquecen sin cambiar
de nombre: `PARIDAD`, `BARRA_RETIRADA`, `DIVERGENCIA_DE_VALOR`, y uno nuevo
que esta noche hizo falta y no existía: **`INTERMITENTE`** (la barra está
en la copia de un día y no en la de otro). La regla canónica R-A («la
primera gana siempre») **no cambia**: la copia es testigo, no reemplazo.

### 5.4 Qué cambia para el backtest y el veredicto 5.1

Hoy B2 «reproduce producción» recomputando desde Yahoo, y lo hace dentro
de 0,05 pp de media **excepto donde la fuente cambió de estado** (28-ago:
media 3,62 pp, dice el propio `resumen.md`). La forma honesta de «reproducir
producción» **es leer producción**: donde existe fila sellada, B2 la lee; el
recomputo queda para fechas anteriores al sello y para la contraprueba de
que el motor sigue siendo el mismo (test de paridad, no fuente de cifras).
Es un cambio en `backtest/baselines.py`, no en el sello, y **hace que el
veredicto 5.1 sobre la ventana sellada no dependa de qué sirva Yahoo la
mañana del 25-oct**.

### 5.5 Costo, completo

| | |
|---|---|
| Disco | **medido:** ~9 MB/año (130 barras consumidas) o ~53 MB/año (panel de 3 años); versionado en `data/backups/` vía `mki_backup` |
| Código | **ya existe como arnés no activado:** `GEMELO/INSUMOS/insumos.py` (`congelar` aditivo con sha256, `leer`, `contrastar`, `intermitencia`) + `tests/test_insumos.py` (8 contrapruebas: hash reproducible, nunca reescribe, nombra retiro / retorno cambiado / reescalado, lee la intermitencia con cinco copias, no importa ni lo importa la ruta de sellado, ningún timer ni `mki` lo invoca, costo medido). Falta sólo la llamada protegida en `snapshot.py` y la columna |
| Sello | +1 columna aditiva, +1 llamada protegida, +1 bump de plataforma |
| Riesgo | que la copia falle en silencio → lo cubre un chequeo del vigía (`insumos_sha256 IS NULL` en el sello de hoy) |
| Lo que NO compra | el pasado (nada hacia atrás); una segunda opinión sobre si el dato era *correcto* (para eso hace falta C4, y §52 dice que no existe) |

## 6. Lo que espera la firma de Nicolás

Tres decisiones, en orden de dependencia. **Ninguna se toma acá.**

1. **¿Cuál es el campeón?** Para la ventana sellada: ¿las filas selladas
   (C2/C5) o su reconstrucción (C1)? Es la pregunta constitucional del
   Frente A de la sexta corrida vista desde el otro lado: no «qué es
   inmutable» sino «qué es *verdad* cuando la fuente y el sello discrepan».
   *Recomendación marcada: las filas selladas.* Consecuencia: B2 lee en vez
   de recomputar (§5.4); las 15 filas verificadas del 28/31-ago quedan como
   están (8/8 y 0/7).
2. **¿Se construye la copia cruda (C3)?** Toca `snapshot.py`, lleva corte de
   método y bump. *Recomendación marcada: sí, en el mismo movimiento que el
   parche de `snapshot.py:140`, que ya espera firma y ya exige el mismo
   bump.* Dos cortes de método en un solo `PLATAFORMA_VERSION` cuestan lo
   mismo que uno.
3. **¿La ventana larga se declara dependiente de la fuente y fechada?**
   Es decir: cada corrida de `ventana_larga`, `CONDICIONAL` y del 5.1 sobre
   fechas pre-sello publica **fecha y sha256 de su descarga** como
   parámetro sellado, igual que ya sella `embargo_dias` y la semilla. *Sin
   recomendación: es barato y no bloquea nada, pero es una convención de
   reporte y ésas son de Nicolás.*

## 7. Lo que este expediente NO dice

- **No dice que Yahoo sea malo.** Dice que sirve estados distintos del
  mismo query en días distintos, y que el proyecto no tenía forma de
  saberlo. Ninguna fuente gratuita promete otra cosa.
- **No dice que el 28-ago vuelva o no vuelva.** Al 2-sep sigue ausente.
- **No prueba M6.** La sostiene una única barra de 130 que explica cuatro
  fechas a la vez con residuo de centésimas. Un testigo la probaría; no
  hay testigo.
- **No mueve ninguna cifra publicada**, ni propone moverla. Regla de los
  doce bloques.
- **No cuantifica el pasado de julio** (45 filas): no hay testigo anterior
  al 27-jul.

## Procedencia

| Cifra | De dónde |
|---|---|
| 52.507 celdas, 0 retornos cambiados, 1.953 niveles reescalados de 000660.KS, factor 0,999783 | `fuente_canonica.json` → `m1.testigos[1]` (`cierres_853b6558513c5e9f.csv`, mtime 26-ago 04:22Z); verificado por otra ruta en `dictamen_07/verif_m1b.py` (52.452 pares sobre el índice propio de cada ticker) |
| 24/1/1 sobre 26 fechas de `sox_usado_pct` | `m2` |
| 271 + 5 sobre 276 verificaciones; 0 aciertos cambian | `m3` |
| 197/90 sobre 287 emisiones; 16 signos | `m4` |
| Barra 2026-07-31 y desvíos 0,254→0,035 etc. | `m6` |
| 15 verificadas del 28/31-ago, 8→0 y 0→7, 64,86%→64,49%, b=8 c=7 p=1,00, MAE 2,827→2,892 | consulta ad hoc sobre `verificacion_apertura` ⋈ `m4` (bitácora 02:06); reproducido por el adversario recomputando el motor (`dictamen_07/verif_iv.py`) |
| Ventana ≤ 8 h | `backtest/resultados/20260901-061708-*/predicciones_B2.csv` (est del 28-ago = +2,11 para 000660.KS) y `GEMELO/cache/cierres_353cacd57dc25f6a.csv` (`^SOX` NaN el 28-ago, mtime 1-sep 13:16Z) |
| Tamaños del congelado | **medidos** con `GEMELO/INSUMOS/insumos.py` sobre `GEMELO/cache/cierres_55f56647c2976497.csv` (37 series): 213.179 bytes gz para 750 barras, 36.339 para 130 |
