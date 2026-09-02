# El decaimiento como teoría con predicción — Frente B (octava corrida, PROPUESTA, v2)

> **PROPUESTA. Versión 2 (2-sep-2026, 14:55), reescrita tras el dictamen del
> `estadistico-adversario`** (`dictamen_08/B.md`: NO SOSTIENE la
> interpretación de la v1; el aritmético reproducía). Pre-registro con tres
> enmiendas fechadas: `GEMELO/preregistro/frente_B.md`. Scripts:
> `GEMELO/decaimiento_feriados.py` (B1, con candado) y
> `GEMELO/decaimiento_prediccion.py` (B2, con testigo de fuente). Cifras en
> `decaimiento_feriados.{json,md}` y `decaimiento_prediccion.json`. Todo
> sobre retornos crudos —el signo del último cierre de NY anterior a la
> apertura local contra el signo del gap—, sin el motor 4.6.0. Datos: gaps
> v2, `^SOX` del testigo del 1-sep, `exchange_calendars 4.13.2`. **Prueba:
> 2024-01-08 → 2026-08-31 SIN la ventana sellada (2026-07-06 → 2026-09-02,
> derivada del backup) y con embargo de 5 sesiones en sus dos bordes** —la
> v1 declaraba esto y no lo hacía; la prueba se re-abrió UNA vez, declarada,
> con candado (`decaimiento_feriados.lock`). IC por bootstrap de fechas iid
> (pre-registrado) **y** por bloques circulares de 20 fechas (regla de la
> casa), los dos publicados.

## 0. Lo que este frente puede afirmar, por estatus (primero, para que no se lea al revés)

- **SOSTIENE (negativo):** los feriados asiáticos **no separan** disipación
  de absorción en Fráncfort (C2/C3): los IC contienen 0 y ±5 pp en las dos
  ventanas y con los dos bootstraps. Y multiplicando las fechas de feriado
  el semiancho **no baja de ~±5 pp ni a ×23** (el grupo normal también
  acota): la pregunta no se decide con este experimento natural en ningún
  horizonte razonable.
- **SOSTIENE (negativo, y más fuerte que en la v1):** Δ(h) = a·exp(−h/τ)
  **no es una ley del margen.** Predichos antes de descargar, Hong Kong
  (predicho 14,0 [11,4, 16,0], medido 4,1 [1,0, 7,4] en ajuste y 3,1 [−1,5,
  7,9] en prueba, este último contiene el cero) e India (predicho 8,6 [5,3,
  11,6], medido −13,2 [−16,9, −9,6] y −8,8 [−13,3, −4,6]) son INCOMPATIBLES
  propagando las dos incertidumbres, y **refutan cualquier curva monótona
  decreciente que pase por las anclas**, no sólo la exponencial.
- **NO SOSTIENE (retirado):** «un cierre de NY viejo vale menos en Tokio por
  el tiempo transcurrido» (C1). La condición `n_ny = 0` significa, en el
  100 % de sus fechas y en el 0 % de las normales, que **la sesión local
  anterior ya abrió y negoció con exactamente ese insumo**: C1 contrasta
  «insumo no incorporado» contra «insumo ya incorporado por el propio
  mercado», no fresco contra viejo. Ningún control de volatilidad lo toca.
- **NO SOSTIENE (retirado):** «Ámsterdam confirma que el margen explica el
  escalón Asia–Europa». Ámsterdam está al MISMO h que el ancla Fráncfort:
  la predicción es «se parecerá a Fráncfort», no una extrapolación; y son
  dos estimaciones que rozan el cero (Fráncfort 3,70 [0,15, 7,41];
  Ámsterdam prueba 4,26 [−0,29, 8,82], contiene el cero).
- **NO CONCLUYENTE:** «Δ(h) es la curva de un universo atado al SOX». Al
  medirlo, lo que mejor predice Δ por exchange no es h ni la exposición al
  SOX sino la **tasa base** de gaps positivos (India 0,758, Hong Kong
  0,621–0,643, contra 0,53–0,56 en las anclas): contra un mercado que sube
  tres de cada cuatro días, «siempre al alza» es casi imbatible por
  construcción. Y XNSE tiene **un solo ticker con historia** en el ajuste.

## 1. B1 · El experimento natural de los feriados

**Partición:** ajuste 2018-09 → 2023-12 (1.381 fechas, 10.438 filas); prueba
2024-01-08 → 2026-06 (643 fechas, 4.830 filas; 8 filas por insumo rancio; la
ventana sellada excluida y embargada). Δ = acierto del signo − «siempre al
alza»; diferencia condición − normal; efecto relevante pre-declarado 5 pp.

### C1 · NY cerrada — lo que mide y lo que no

| Tokio | diferencia [IC95 fechas iid] | [IC95 bloques 20] | p perm |
|---|---|---|---|
| ajuste, sin control | **−23,4 [−40,0, −6,7]** | [−34,4, −12,5] | 0,006 |
| ajuste, \|SOX\| estandarizado por 4 estratos | **−31,0 [−49,7, −12,0]** | — | — |
| ajuste, \|SOX\| truncado simétrico (≤ p75) | −16,7 [−33,3, −0,8] | [−24,5, −8,8] | 0,077 |
| prueba, sin control | −14,3 [−31,5, +2,3] (contiene el cero) | [−24,0, −4,4] | 0,17 |
| prueba, estandarizado | −15,5 [−32,1, −1,1] | — | — |
| prueba, truncado simétrico | +0,3 [−18,9, +18,7] (contiene el cero) | [−18,3, +19,1] | 1,0 |

**Lectura.** La v1 publicaba un «control de |SOX| emparejado» que truncaba
sólo el grupo normal e invertía el desbalance; su «se reduce a la mitad» se
retira. Con el control bien especificado la caída de Tokio en el ajuste no
se reduce: se agranda. Pero **nada de esto establece decaimiento
temporal**: por la confusión estructural (100 % / 0 %), C1 mide cuánto
vale un insumo que el mercado local ya negoció, y la respuesta —en Tokio,
cerca de nada— es la lectura que la v1 rotulaba «post-hoc»: *la
información no se disipa con el reloj; se disipa cuando el propio mercado
abre*. Los cuatro C1 comparten sus fechas (ajuste: unión 46, intersección
29; prueba: la unión es el propio Tokio): **son un experimento, no cuatro**.
Fuera de muestra, el IC iid contiene el cero y el de bloques no: la
replicación depende del método de intervalo, y se dice así.

### C2 · C3 · Fráncfort con un intermediario asiático menos

| contraste | ajuste [iid] · [bloques 20] | prueba [iid] · [bloques 20] |
|---|---|---|
| C2 · sólo Tokio cerrada | −2,3 [−21,6, +16,0] · [−22,8, +15,8] | −10,9 [−31,8, +11,9] · [−25,6, +4,3] |
| C3 · sólo Seúl o sólo Taipéi | +3,6 [−11,4, +18,9] · [−5,6, +12,5] | +17,3 [−2,4, +36,7] · [+2,2, +34,9] |
| C2+C3 · dos intermediarios vs tres | +1,0 [−11,2, +12,7] · [−11,5, +12,4] | +6,6 [−9,1, +22,0] · [−5,9, +19,3] |

Todos contienen el cero y ±5 pp (C3 en prueba excluye el cero con bloques
y no con iid: un contraste de 16 sin coherencia entre ventanas). Potencia
calculada: ×10 fechas de condición → semiancho ±5,3 pp (ajuste); ×23 → ±4,9.
**No decide.**

### Feriado local · el gap agrega dos movimientos de NY

Con el ÚLTIMO cierre como insumo, Tokio y Seúl aciertan igual que un día
normal (+1,6 [−11,3, +14,4]; +2,5 [−14,3, +18,8]; los dos contienen el
cero). Con el cierre **anterior**: Seúl +21,8 [+7,4, +36,0] (p 0,020) y Tokio
+14,1 [−1,6, +29,9] (contiene el cero) en el ajuste. **El McNemar pareado que
faltaba** (último vs anterior, MISMAS filas): Tokio ajuste 76,9 % vs 63,1 %
(base 53,1 %), b = 84, c = 48, **p = 0,0023**: el cierre viejo conserva
señal sobre la base pero **pierde contra el fresco**. Fuera de muestra:
Seúl +6,4 [−16,9, +29,4], Tokio +2,3 [−15,6, +19,8] (contienen el cero);
McNemar p 0,52 y 0,13. En la prueba también aparecen contrastes con IC
fuera del cero en otras bolsas y con el otro insumo (la tabla completa está
en `decaimiento_feriados.md`): 4 de 16 sin coherencia entre bolsas ni
ventanas es el aspecto que tiene la multiplicidad. Lectura post-hoc, no
replicada, y matizada en contra por el pareado.

## 2. B2 · Predicción fuera de muestra

**Anclas (ajuste, con IC):** Tokio 21,55 [18,61, 24,46] a 1,75 h; Seúl 16,25
[13,03, 19,39] a 1,75; Taipéi 16,76 [13,17, 20,42] a 2,75; Fráncfort **3,70
[0,15, 7,41]** a 8,75. Curva: a = 28,1 pp [22,9, 36,9], τ = 4,65 h [2,87,
7,57]. **Advertencias que la v1 no llevaba:** h y el conjunto de tickers
están perfectamente confundidos (Fráncfort = 1 ticker, Taipéi = 1, Seúl = 2,
Tokio = 4); el intervalo predicho es de CONFIANZA de la curva, no de
PREDICCIÓN de un exchange nuevo (omite la dispersión entre tickers al mismo
h: DE 6,5 pp entre los ocho, Seúl 16,3 vs Tokio 21,6 al mismo h). La
medición lee de un testigo preservado (`testigos_fuente/b2_nuevos_ohlc.csv.gz`,
sha256 en el JSON): reproducible.

| exchange | h | base | corr(gap, SOX) | predicho | medido ajuste | medido prueba | compatible (ambas incertidumbres) |
|---|---|---|---|---|---|---|---|
| Ámsterdam | 8,75 | 0,56 | 0,29 | 4,3 [1,7, 7,5] | 6,2 [3,0, 9,5] | 4,3 [−0,3, 8,8] (contiene el cero) | sí — mismo h que el ancla Fráncfort |
| Hong Kong | 3,25 | 0,62 | 0,45 | 14,0 [11,4, 16,0] | 4,1 [1,0, 7,4] | 3,1 [−1,5, 7,9] (contiene el cero) | **no** (−9,9 [−13,8, −5,9]) |
| India | 5,5 | 0,76 | 0,39 | 8,6 [5,3, 11,6] | −13,2 [−16,9, −9,6] | −8,8 [−13,3, −4,6] | **no** (−21,8 [−26,6, −17,0]) |
| Sídney | 1,75 | — | — | 19,3 | sin ticker | | no medible |

## 3. Intentos del DSR

Contados por máquina como intervalos publicados: **54 en B1** (+ 12
comparaciones de B2 = 66). El «17» de la v1 se retira; la tupla va al registro.

## 4. Lo que no se hizo

- No se cambió ningún ticker candidato ni ninguna hipótesis después de medir.
- La h de B2 está definida desde la emisión (22:15Z); medida desde el cierre
  de NY es 3/4/11 h y el lunes «normal» tiene h ≈ 52 h. Se declara.
- El recompute de la ventana larga publicada (n = 14.618, sobre gaps v1 con
  sesiones post-feriado omitidas) queda para firma con su tamaño medido
  (`espera_firma.md` §24).
