# Pre-registro · Frente B — el decaimiento como teoría con predicción

**Escrito 2-sep-2026 11:50, antes de mirar ningún dato de estas
preguntas.** Octava corrida. PROPUESTA hasta el dictamen. Todo el análisis
es sobre **retornos crudos** (signo del retorno del SOX de la sesión de NY
anterior contra signo del gap local), **sin pasar por el motor 4.6.0**: si
en algún punto un resultado dependiera del modelo, se detiene y se
documenta.

## Las dos explicaciones que hay que separar

Cuatro bolsas y una curva que baja con las horas de margen admiten dos
mecanismos incompatibles:

- **Disipación temporal (H_dis):** la información del cierre de NY pierde
  valor con el tiempo transcurrido, haya o no otros mercados en el medio.
- **Absorción por intermediarios (H_abs):** los mercados que abren antes
  «consumen» la información; Fráncfort ve poco porque Asia ya lo vio.

Fráncfort abre después de toda Asia, así que la curva actual no las
separa. Los feriados sí: cambian quién está en el medio y cuánto tiempo
pasa **dentro del mismo exchange**, sin cambiar nada más.

## B1 · Experimento natural de los feriados

**Definición de la distancia y del insumo (fijadas ahora):** para una
sesión local d de un exchange X, el insumo es el **último cierre de NY
estrictamente anterior a la apertura de d** (`merge_asof` hacia atrás,
excluyente); la distancia h es el tiempo entre ese cierre y la apertura de
d. En un día normal h es la de siempre (Tokio/Seúl 1,75 h desde la
emisión; Taipéi 2,75; Fráncfort 8,75). Tres condiciones que los feriados
producen:

| condición | qué cambia | H_dis predice | H_abs predice |
|---|---|---|---|
| **C1 · feriado en NY, Asia abre** (h salta de ~2 h a ~26 h, sin intermediarios) | sólo el tiempo | la ventaja cae hacia cero (h grande) | la ventaja cae (nadie tomó el relevo… pero tampoco nadie la absorbió: **H_abs predice que NO cae**, porque Asia sigue siendo la primera en ver el cierre viejo) |
| **C2 · feriado en Tokio, NY abierta: Fráncfort abre con menos intermediarios** (h igual, 8,75 h; Seúl y Taipéi siguen abiertos) | sólo los intermediarios | ventaja de Fráncfort **igual** | ventaja de Fráncfort **mayor** que en días normales |
| **C3 · feriado en Seúl o Taipéi (uno de los dos), Fráncfort abre con un intermediario menos** | idem, dosis menor | igual | mayor, con dosis |

**El contraste que decide es C2/C3**: H_dis y H_abs predicen lo mismo en
C1 en dirección (ambas: cae) y difieren en C2/C3 (H_dis: nada; H_abs:
sube). C1 sirve para medir cuánto cae con el tiempo puro, que es la forma
de la curva.

**Estadístico:** ventaja direccional del signo del SOX contra «siempre al
alza» (Δ = P(signo SOX = signo gap) − P(gap > 0), `excluir_cero`), por
condición y por exchange; **diferencia Δ(condición) − Δ(normal)** con IC95
por bootstrap de FECHAS enteras (clúster de día, 4.000 réplicas) y p por
permutación de la etiqueta de condición entre fechas (4.000).

**Efecto relevante:** una diferencia de **≥ 5 pp** entre condición y
normal. **Refutación de H_dis:** en C2/C3, Δ(Fráncfort | Asia parcialmente
cerrada) − Δ(Fráncfort | normal) ≥ 5 pp con IC que excluya el cero.
**Refutación de H_abs:** esa misma diferencia ≤ 0 con IC que excluya +5 pp.
Si el IC contiene a las dos, **no se distinguen con estos datos** y se dice
así.

**Datos (sin descarga):** gaps reconstruidos de los 8 tickers
(`GEMELO/cache/gaps_03fdca36d64efb0d.csv`, 2018-09 → 2026-09), `^SOX` de
la caché testigo del 1-sep, calendarios de `exchange_calendars` (XNYS,
XTKS, XKRX, XTAI, XETR). Los feriados de cada bolsa se toman del
calendario, no de los huecos de la fuente (la séptima corrida mostró que
la fuente tiene huecos que no son feriados).

## B2 · Predicción fuera de muestra

**Forma paramétrica, elegida ahora:** Δ(h) = a·exp(−h/τ), ajustada por
mínimos cuadrados ponderados por fechas sobre los cuatro exchanges
actuales en los **años de ajuste**, con IC de (a, τ) por bootstrap de
fechas. **Control no paramétrico:** interpolación monótona (isotónica
decreciente) entre los puntos observados; para h fuera del rango, el valor
del extremo más cercano. Se reportan las dos predicciones.

**Exchanges nuevos y sus márgenes** (hora de apertura UTC − 22:15Z de la
emisión), con los tickers de semiconductores que el auditor de datos
considere disponibles en la fuente actual:

| exchange | apertura | h | candidatos |
|---|---|---|---|
| Hong Kong (XHKG) | 01:30Z | 3,25 | 0981.HK (SMIC), 1347.HK (Hua Hong) |
| Ámsterdam (XAMS) | 07:00Z | 8,75 | ASML.AS, BESI.AS — **mismo h que Fráncfort: separa exchange de margen** |
| Bombay (XBOM/XNSE) | 03:45Z | 5,5 | los que existan (se declara si no hay ninguno de semiconductores con historia suficiente) |
| Sídney (XASX) | 00:00Z | 1,75 | probablemente ninguno de semiconductores: se declara |

**Protocolo:** (1) ajustar la curva sobre los cuatro exchanges actuales en
los años de ajuste; (2) **escribir en este archivo el número predicho con
intervalo para cada exchange nuevo ANTES de descargar** (sección «Predicciones
escritas antes», abajo, que hoy está vacía a propósito); (3) recién después
descargar (fuera de la ventana 17:50–20:30), anotar qué sesiones faltan, y
medir con el mismo estadístico y clúster de día.

**Refutación:** el valor medido cae fuera del IC95 de la predicción. Una
predicción que acierta con intervalo es el resultado más fuerte posible;
una que falla se publica igual.

## Partición de años

**Ajuste: 2018-09-01 → 2023-12-31. Prueba: 2024-01-01 → 2026-08-31.** El
mismo corte que el Frente D, por las mismas razones. B1 y la curva de B2
se estiman en el ajuste; la prueba se abre después de cerrar y auditar el
ajuste, y se reporta al lado.

## Intentos del DSR

B1: tres contrastes (C1, C2, C3) = 3. B2: una forma paramétrica + un
control = 2. **5 intentos**, declarados antes de correr.

## Predicciones escritas antes (vacío hasta ajustar la curva)

*(se completa en el paso 2, antes de cualquier descarga)*

## Enmienda 1 — 2-sep-2026 12:14: los datos, no el diseño

Al correr C1–C3 sobre los años de ajuste, la condición «feriado local
(n_ny ≥ 2)» apareció casi vacía (4 fechas en Tokio en 5 años contra 54 que
el calendario da). La causa no era el calendario: **el caché de gaps de la
ventana larga no contenía ninguna sesión posterior a un feriado local**
(`GEMELO/datos.descargar_gaps` hacía `shift(1)` sobre el índice unión de
los 8 mercados; NaN en el feriado, `dropna` en la sesión siguiente).
Corregido en el ejecutable (`gaps_desde_ohlc`, sobre el índice propio del
ticker; `tests/test_gaps_feriados.py`), gaps regenerados con descarga
fresca (`gaps_v2_propio_indice.csv.gz`: +670 filas, 0 cambiadas). B1 se
re-corre sobre el v2. **Consecuencia fuera de este frente, declarada:** las
cifras publicadas de la ventana larga (n = 14.618) se calcularon sobre
gaps que omitían esas ~4,5% de sesiones — las de dos movimientos de NY
agregados; recomputarlas mueve los doce bloques y lleva firma.

## Predicciones escritas antes — 2-sep-2026 12:21, ANTES de cualquier descarga

Ajuste sobre los años ['2018-09-01', '2023-12-31'] con los cuatro exchanges actuales: puntos XETR: Δ = 3.7 pp a h = 8.75 (1350 fechas); XKRX: Δ = 16.25 pp a h = 1.75 (1296 fechas); XTAI: Δ = 16.76 pp a h = 2.75 (1283 fechas); XTKS: Δ = 21.55 pp a h = 1.75 (1295 fechas).
Curva Δ(h) = a·exp(−h/τ): a = 28.12 pp [22.86, 36.94], τ = 4.65 h [2.87, 7.57]. cuatro exchanges, tres valores de h: la curva tiene un grado de libertad efectivo; la predicción a h=8,75 (Ámsterdam) es la que separa exchange de margen.

| exchange | h | tickers candidatos | predicción exp (IC95) | predicción isotónica (IC95) |
|---|---|---|---|---|
| XHKG | 3.25 | 0981.HK, 1347.HK | **13.98 pp** [11.36, 15.99] | 15.67 pp [12.29, 17.86] |
| XAMS | 8.75 | ASML.AS, BESI.AS | **4.29 pp** [1.71, 7.5] | 3.7 pp [0.07, 7.26] |
| XNSE | 5.5 | MOSCHIP.NS, TATAELXSI.NS | **8.62 pp** [5.27, 11.57] | 10.77 pp [8.17, 12.88] |
| XASX | 1.75 | — (ninguno de semiconductores) | **19.3 pp** [17.38, 21.39] | 18.89 pp [16.97, 21.08] |

Refutación: el Δ medido (clúster de fecha) cae fuera del IC95 de la predicción exp. Se reporta también contra el isotónico. Sesiones faltantes se anotan.

## Enmienda 2 — 2-sep-2026 12:24, tras la auditoría de fuga y ANTES de abrir la prueba

El `auditor-lookahead` no encontró fuga de futuro (núcleo verificado contra
timestamps reales, prueba de truncado en tres niveles, dos contrapruebas)
y bloqueó la prueba por tres cosas, aplicadas ahora:

1. **Insumo rancio por añada de la fuente:** la serie del `^SOX` (testigo
   del 1-sep) no tiene el 28-ago ni nada posterior al 31-ago; cinco filas
   de la prueba entraban al cubo «normal» con un insumo dos sesiones más
   viejo que su etiqueta. **Regla:** una fila cuya `fecha_sox` no es la
   última sesión de NY del calendario anterior a la fecha local se excluye
   y se cuenta (`insumo_rancio`). En el ajuste, 0.
2. **C2 y C3 como estaban pre-registradas y disjuntas:** C2 = sólo Tokio
   cerrada con Seúl y Taipéi abiertos; C3 = exactamente uno de Seúl/Taipéi
   cerrado con Tokio abierta.
3. **Intentos:** el código produce 15 contrastes en B1 (4 C1 + 8 de feriado
   local + C2 + C3 + C2+C3), no 3. Se declaran **15 + 2 de B2 = 17**. Los
   dos controles nuevos de C1 (sin lunes; |SOX| emparejado) son controles
   de un mismo contraste y no suman.
4. Dos sospechas del auditor que se **reportan** sin cambiar el diseño: el
   cubo «normal» mezcla h ≈ 4 h (martes a viernes) con h ≈ 52 h (lunes), y
   los feriados de NY caen en tramos quietos (|gap| menor). Por eso C1 lleva
   los dos controles. Y la h de B2 está definida desde la emisión (22:15Z),
   no desde el cierre de NY; se deja así porque es la h del proyecto, y se
   declara la diferencia.
5. Los cuatro C1 comparten ~40 de sus fechas de condición: no son cuatro
   experimentos independientes. Se leen como uno.

## Enmienda 3 (2-sep-2026, 14:50, después del dictamen del adversario)

Dictamen: `GEMELO/resultados/dictamen_08/B.md` — **NO SOSTIENE** la
interpretación; el aritmético reproduce. Lo que este pre-registro reconoce,
con fecha, sin tocar lo escrito arriba:

1. **La fila C1 de arriba dice «qué cambia: sólo el tiempo». Es falsa, y de
   forma determinista:** `n_ny = 0` significa que ninguna sesión de NY cerró
   entre la sesión local anterior y ésta, así que **la sesión local anterior
   ya abrió y negoció con exactamente este insumo** (100 % de las fechas
   n_ny = 0 contra 0 % de las n_ny = 1, en los cuatro exchanges). C1 contrasta
   «insumo no incorporado» contra «insumo ya incorporado por el propio
   mercado», no «fresco» contra «viejo». Ningún control de volatilidad lo
   toca. La lectura que el entregable rotulaba post-hoc («no se disipa con el
   reloj sino cuando el propio mercado abre») es la única que el diseño de
   C1 admite.
2. **La higiene de partición declarada era falsa:** el entregable decía «sin
   las 37 selladas, con embargo» y el código no hacía ni lo uno ni lo otro
   (frase copiada del Frente D). Ahora `correr()` excluye la ventana sellada
   derivada del backup y la embarga 5 sesiones en los dos bordes; la prueba
   se re-abre UNA vez, declarada, con candado (`decaimiento_feriados.lock`,
   sha256 del módulo, del pre-registro y de los testigos; `--enmienda` deja
   rastro).
3. **El control de |SOX| estaba mal especificado** (truncaba sólo el grupo
   normal al p75 de la condición: invertía el desbalance). Se reemplaza por
   estandarización directa por 4 estratos de |SOX| (cortes del grupo normal)
   y truncado SIMÉTRICO; «se reduce a la mitad» se retira.
4. IC por bloques circulares de 20 fechas publicado junto al iid; McNemar
   pareado (último cierre vs anterior, mismas filas) en el feriado local;
   potencia de C2/C3 calculada (semiancho por multiplicador de fechas), no
   dicha; unión e intersección de las fechas C1.
5. **B2:** las anclas se publican con IC, tasa base y corr(gap, SOX) por
   exchange; se declara que el intervalo predicho es de CONFIANZA de la curva
   y no de PREDICCIÓN (omite la dispersión entre conjuntos de tickers), que h
   y los tickers están confundidos en el ajuste, y que XNSE tiene un solo
   ticker con historia. La medición lee de un **testigo preservado**
   (`testigos_fuente/b2_nuevos_ohlc.csv.gz`, sha256 en el JSON); la
   compatibilidad se evalúa propagando las dos incertidumbres. Ámsterdam no
   es un acierto de la curva: está al mismo h que el ancla Fráncfort.
6. **Intentos:** el 17 se retira; se cuentan por máquina como intervalos
   publicados (misma convención que C y D) y van al registro.
7. Lo que sigue en pie sin cambios: C2/C3 no separan disipación de absorción;
   Δ(h) no es una ley del margen (Hong Kong e India refutan cualquier curva
   monótona decreciente por las anclas).
