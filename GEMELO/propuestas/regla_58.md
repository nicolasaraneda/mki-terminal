# Regla de decisión de §58 — PROPUESTA (corrida 15, noche del 29-sep-2026)

> **Estatus: PROPUESTA. No elige nada.** Fija de antemano **cómo se va a elegir** entre las
> opciones (a), (b) y (c) de `GEMELO/resultados/espera_firma.md` §58 cuando existan noches con la
> franja de madrugada de la sonda. Firmarla es acto de Nicolás (acta §91.3). Mientras no se firme,
> rige §88.1: el sellador sigue en `Mon..Fri 23:30 America/New_York` y §57 no cambia.
>
> **Pre-registro.** Escrito el 29-sep-2026 sobre el commit `2f73eb2`, antes del primer dato de
> madrugada: el primer disparo de la franja `Tue..Sat 00..03:05,35 America/New_York` es a las
> 01:05 de Chile del 30-sep-2026 (`2026-09-30T04:05Z`). La hora y el sha256 con que quedó sellado
> están en `GEMELO/resultados/bitacora_15.md` y en la tarjeta §58; no pueden ir acá adentro porque
> el sha256 es el del archivo. Dictamen del `estadistico-adversario` en
> `GEMELO/resultados/dictamen_15/adversario_regla58.md`.
>
> **Intentos que consume: 0 en los dos registros que existen**
> (`GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO` / `backtest.veredicto_51.N_INTENTOS_51`, gap
> asiático; y `dinero/registro_intentos.py`, riel largo). No prueba ninguna hipótesis sobre
> retornos ni sobre ventaja; todo el riel de dinero sigue SIMULADO y E0 sella el sorteo sin
> información (§86.2). Queda anotado que **adoptar (b) o (c) cambia qué sesiones entran a E0**, o
> sea la definición de la muestra del riel de dinero: esa adopción, cuando ocurra, se declara en
> `dinero/registro_intentos.py` con su fecha, no ahora.

## 0. Qué se leyó para escribirla, y qué no

Insumos, todos permitidos por el encargo (sección 3): `espera_firma.md` §58; `bitacora_14.md`
1.6, 1.7, 11.2 y 11.3; `sonda_cierre_resumen.md`; el acta §88.1; el código de
`dinero/sello_dinero.py`, `GEMELO/sonda_cierre.py` y `GEMELO/sonda_cierre_resumen.py` (sólo
lectura); `dinero/sello_dinero.db` en `mode=ro` a las 22:07 de Chile; `man systemd.timer`
(systemd 259.5); y `data/sonda_cierre.csv` **filtrado por `timestamp_utc < 2026-09-30T04:00:00Z`
antes de imprimir nada**.

- **El orquestador leyó el CSV hasta la fila `2026-09-30T00:35:00Z`** (20:35 NY de la sesión del
  29-sep), a las 22:03:51 de Chile, y lo abrió una vez más a las 22:36:59 **restringido a lo
  anterior a `2026-09-29T21:00Z`**, para comprobar qué calendario de la sonda estaba instalado
  (sección 6). El `estadistico-adversario`, al dictaminar, leyó hasta la fila `01:05:00Z` (21:05
  NY, 1 de 36).
- **Ninguna fila de madrugada existía ni fue leída.** De la noche del 29-sep se vieron tres
  observaciones de tarde (20:05, 20:35 y 21:05 NY, 1 de 36 con cierre en las tres) y una fuera de
  grilla (17:38 NY, la del `restart` del timer). Ninguna entra al estadístico de la regla
  (sección 3).
- **El casillero de las 23:35 NY sí entra al estadístico, y no es de madrugada.** Se escribe a
  las `03:35Z`, que son las 00:35 de Chile: por debajo del corte de `04:00Z` que el acta §91.3
  prohíbe. Cómo se cierra ese agujero está en la sección 2, y no depende de la palabra de nadie.

Lo que se sabía al escribir, DESCRIPTIVO y sin franja de madrugada (no entra al conteo de K):

| sesión NY | 20:05–21:05 | 21:35–23:05 | 23:35 | sello de las 23:30 NY |
|---|---|---|---|---|
| 21-sep | 1/36 | 35/36 (falta TOELY) | 36/36 | `pendiente`, cuenta |
| 22-sep | 1/36 | 1/36 | 2/36 | `insumo_incompleto` (31 de 33 sin cierre) |
| 23-sep | 1/36 | 35/36 (falta TOELY) | 35/36 | `insumo_incompleto` (1 de 33) |
| 24-sep | 2/36 | 36/36 | 36/36 | `pendiente`, cuenta |
| 28-sep | 1/36 | 35/36 (falta TOELY) | 35/36 | sin segunda vía (`no_verificable_timing` a las 13:43 NY) |

Y del riel de dinero (MEDIDO, `sello_dinero.db` en `mode=ro`): **con la misma ventana que exige
V3** (`timestamp_utc` entre las 23:30:00 y las 23:34:59 NY), **11** sesiones fueron selladas por
el timer a su hora (10, 11, 14, 15, 16, 17, 18, 21, 22, 23 y 24-sep), y **3** quedaron
`insumo_incompleto` (18, 22 y 23-sep). Wilson 95 % para 3/11: **27,3 %, [9,7 · 56,6]**. Es el
único antecedente de la tasa de noche perdida a la hora actual, y su intervalo cubre desde «una
de cada diez» hasta «más de una de cada dos».

**Las dos sesiones que esa ventana deja fuera, declaradas porque mueven la cifra en direcciones
opuestas.** El **8-sep** (primera fila del riel) se selló a las 23:38 NY: no es un disparo de las
23:30 y no entra; es un `pendiente`, así que incluirlo bajaría la tasa a 3/12 = 25,0 %
[8,9 · 53,2]. El **9-sep** se selló a las 20:00 NY, con el timer todavía en 21:00 de Chile: es un
`insumo_incompleto`, así que incluirlo la subiría a 4/13 = 30,8 % [12,7 · 57,6]. **Rige 3/11.**
Las tres cifras quedan escritas para que ninguna corrida posterior elija la que le convenga.

## 1. La unidad: la noche

**Noche `D`** = una sesión de XNYS, con las observaciones de la sonda que `sesion_atribuida()` le
asigna (columna `sesion_ny` = `D`), **posteriores al cierre de `D`** leído del calendario (el
filtro de la corrida 14, 1.3-bis) y **dentro de la primera noche**: entre las 20:05 NY de `D` y
las 03:35 NY del día calendario siguiente. Las observaciones atribuidas a `D` pero posteriores
(la tarde de un feriado, la madrugada siguiente a un feriado) **no entran al estadístico** y se
declaran con su hora.

**Grilla.** Dieciséis casilleros por noche: 20:05, 20:35, …, 23:35 (tarde) y 00:05, 00:35, …,
03:35 (+1 d, madrugada). Una observación ocupa el casillero `g` si su `timestamp_utc` cae en
`[g, g + 5 min)`. Toda otra observación es **fuera de grilla**: no entra al estadístico y se
declara (así quedan fuera, sin regla especial, un disparo por `restart` como el de las 17:38 NY
del 29-sep y un disparo atrasado por un despertar).

**Casilleros exigidos: nueve.** El de las 23:35 y los ocho de madrugada, que son exactamente los
que flanquean a las ocho horas candidatas (sección 3). Los siete de tarde anteriores (20:05 a
23:05) se informan, pero su falta no invalida la noche.

**Principio: ninguna noche se invalida por lo que la fuente hizo; sólo por lo que la máquina o el
instrumento no hicieron.** Cuando la máquina miró y la fuente no contestó, la noche es válida y
ese casillero cuenta como **no completo**: es lo que le habría pasado al sellador a esa hora (una
descarga vacía hace que `congelar_extension()` levante `RuntimeError` y no se selle nada,
`dinero/sello_dinero.py`). Sacar esas noches del denominador sesgaría hacia «la hora se puede
arreglar». Las cuatro condiciones de abajo invalidan por tres causas distintas y ninguna es «la
fuente falló»: V1 y V2, que la máquina no miró o no escribió; V3, que no hay segunda vía con qué
contrastar; V4, que el universo cambió.

**Una noche es VÁLIDA si cumple las cuatro condiciones.** Si falla una, no cuenta para K y se
informa con la condición que falló:

1. **V1, la máquina miró.** En cada uno de los nueve casilleros exigidos el journal
   (`journalctl --user -u mki-sonda-cierre.service`) muestra que el servicio **arrancó** dentro
   del casillero. Un casillero sin arranque es la huella de una máquina suspendida o apagada, y
   la noche es inválida. Un casillero con arranque y **sin filas** (el servicio falló, por
   ejemplo por la red) **no invalida**: cuenta como no completo y se declara «fuente
   inaccesible». **V1 depende del journal del usuario.** Medido al escribir esta regla: journal
   persistente (`/var/log/journal` existe), 665,7 MB en disco según `journalctl --disk-usage`,
   sin `SystemMaxUse` ni `MaxRetentionSec` configurados, entrada de usuario más antigua del
   24-ago-2026 (unos 36 días de profundidad) contra los unos 30 que el plazo exige. Si al
   evaluar el journal no cubre alguna noche, esa noche **no se declara inválida por defecto**:
   la presencia de filas en el CSV prueba que el servicio arrancó; sólo el caso «sin filas»
   queda indecidible sin journal, y esas noches se declaran aparte con su conteo.
2. **V2, observación entera.** En cada casillero exigido que tiene filas, hay una fila por cada
   uno de los 33 operables (sección 3); si falta la fila de algún operable, la noche es inválida.
   **Unidad declarada: `n_filas_respuesta` es `len(cierres)`, el número de filas-FECHA de la
   descarga `period=7d` de esa observación** (vale 7 en todas las observaciones medidas), no un
   conteo de tickers, y es el mismo valor en las 36 filas de la observación. Un
   `n_filas_respuesta = 0` es un **apagón total de la fuente** en ese casillero: **no invalida**,
   cuenta como no completo y se declara. Un apagón **parcial** (filas-fecha mayores que cero y
   algunos tickers vacíos) no se puede distinguir de un cierre ausente desde el CSV, y cuenta
   igual: como ausencia.
3. **V3, segunda vía.** El sellador selló `D` con un disparo a su hora: hay filas con
   `fecha_insumo = D`, `timestamp_utc` entre las 23:30:00 y las 23:34:59 NY de `D`, y `estado` en
   {`pendiente`, `insumo_incompleto`}. **La fuente primaria es `dinero/sello_dinero.db` en
   `mode=ro`**: la fila existe desde el instante del sello y no depende de ningún otro job.
   `data/backups/sello_dinero.csv`, que el propio sellador exporta al sellar y `mki_backup.py`
   commitea a las 18:40 del día siguiente, se usa para **contrastar** que el export coincide; que
   falte el commit no invalida la noche, se declara. Es el criterio que dejó fuera al 28-sep en
   la corrida 14 (1.7): lo que volvió creíble a la sonda fue que dos vías independientes
   coincidieran ticker por ticker, y una noche sin contraparte no lo tiene.
   **Caso previsto, para que la fuente caída no salga por esta puerta.** Si el sellador
   **disparó a su hora y falló sin escribir filas** (evidenciado en `data/sello_dinero.log` y en
   `journalctl --user -u mki-sello-dinero.service` dentro de la ventana 23:30:00 a 23:34:59 NY),
   la noche **no es inválida**: se toma `A(D) = 0`, se declara «sellador sin filas: fuente caída a
   la hora actual», y se declara además que esa noche **no tiene contraste de concordancia**
   (queda fuera de los cuatro conteos de más abajo). Es la lectura fiel: a la hora actual esa
   sesión se perdió, que es exactamente lo que `A(D) = 0` significa. **Si 3 o más de las K
   noches caen en este caso, la regla no decide:** devuelve «NO DECIDIBLE: la fuente estuvo
   caída a la hora actual en <n> de <K> noches», porque con la sonda como vía única en esas
   noches la clasificación descansa en un solo instrumento. Un sellador que falló **por error de
   código y no por la fuente** (traza que no sea la de descarga vacía) sí invalida la noche, y se
   declara cuál fue.
4. **V4, universo estable.** Los 33 operables de esa noche son los mismos 33 de la sección 3. Si
   el universo cambia de forma **permanente**, todas las noches posteriores serían inválidas y
   la regla nunca llegaría a K: en ese caso **se cierra de inmediato** con «NO DECIDIBLE: el
   universo operable cambió el <fecha>», publica las noches válidas juntadas hasta ahí, y
   reiniciar el conteo con el universo nuevo es acto de Nicolás, con acta.

**Contabilidad obligatoria de lo que se quita y de lo que se declara.** El informe publica, con
su proporción y su Wilson: las noches inválidas por cada condición; los casilleros «fuente
inaccesible» y los de apagón total, con su hora; y las observaciones fuera de grilla.

**Concordancia entre las dos vías (no invalida; puede suspender la regla).** En cada noche
válida se compara el conjunto de operables sin cierre según el sello (23:30 NY) con el de la
sonda (23:35 NY). Se clasifica en cuatro:

- **iguales**;
- **aparición:** el de la sonda está contenido en el del sello (un cierre apareció en esos cinco
  minutos). Concuerda;
- **desaparición:** el de la sonda contiene estrictamente al del sello. **No es una anomalía del
  instrumento**: es el fenómeno medido en la corrida 13 y el que la sección 3 ordena contar como
  ausencia. No discorda; se informa, y la noche se clasifica con lo que el sellador vio;
- **discordante:** los dos conjuntos son incomparables (cada uno tiene un operable que el otro
  no). Ahí ninguna vía explica a la otra.

**Si 2 o más de las K noches son discordantes, la regla no decide:** devuelve «NO DECIDIBLE:
instrumento en duda» y la pregunta vuelve a Nicolás con la tabla. Se publican siempre los cuatro
conteos con su Wilson sobre K. Después de un «NO DECIDIBLE» las K noches no se descartan ni se
reutilizan en silencio: quedan publicadas con su matriz, y si Nicolás manda juntar más rige la
cláusula de segunda lectura de la sección 4.

**Noche censurada.** Un ticker que no tiene el cierre en ninguna observación hasta las 03:35 NY
queda **censurado a la derecha en 03:35**: su hora de aparición es «posterior a las 03:35», y
no se imputa. Una noche con algún operable censurado es una noche que **no estuvo completa a
ninguna hora observada**. En toda proporción de esta regla la noche censurada **se queda en el
denominador y cuenta como no completa**. Ninguna mediana de hora de aparición decide nada: la
regla usa proporciones por hora, que la censura no rompe.

## 2. Cuántas noches: K = 10, una sola lectura

**K = 10 noches válidas** con franja de madrugada. Es el extremo alto del rango que Nicolás firmó
en §88.1 («5 a 10 noches»); esta regla no propone salirse de ese rango.

**Una sola lectura.** La regla se evalúa **una vez**. No hay lecturas intermedias con poder de
decisión ni parada anticipada. Mirar el CSV antes no cambia los umbrales, que quedan fijos hoy;
cambiar un umbral después de haber mirado es una enmienda fechada que declara qué dato se había
visto.

**La primera noche candidata la decide la hora del sello, no una promesa.** El casillero de las
23:35 NY de la sesión del 29-sep se escribe a las 00:35 de Chile del 30-sep.

- Si este documento quedó sellado **antes de las 00:35 de Chile**, los nueve casilleros exigidos
  de la noche del 29-sep son posteriores al sello: **la primera noche candidata es la del
  29-sep** y el plazo máximo es la sesión número 20 contando desde esa, la del **26-oct-2026**.
- Si quedó sellado **a las 00:35 o después**, la noche del 29-sep **no cuenta para K**: la
  primera candidata es la del **30-sep** y el plazo máximo es la del **27-oct-2026**.

La hora del sello es la de la bitácora y la de la tarjeta §58. Un anexo posterior no mueve esta
cláusula: rige la hora del sello del documento.

**El instante de la única lectura** es cinco minutos después del último casillero (03:40 NY) de
la décima noche válida, o de la noche del plazo máximo si llega antes. Las dos fechas posibles
del plazo caen antes del cambio de hora de Nueva York del 1-nov-2026, así que toda la ventana
tiene Chile = NY + 1 h. **Si al llegar el plazo hay menos de 10 válidas, la regla no decide:**
devuelve «NO DECIDIBLE: faltan noches», con el conteo de válidas e inválidas y la causa de cada
inválida, y sigue (a). Extender el plazo es acto de Nicolás; si lo extiende, el acta declara
cómo se tratan las medias sesiones de NYSE (27-nov y 24-dic-2026, cierre 13:00 NY), que no caen
en el plazo actual.

**Lo que K = 10 permite distinguir, y lo que no.** Wilson 95 % para `x` noches de 10
(`evaluacion.wilson_ci`):

| x de 10 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| inferior % | 0,0 | 1,8 | 5,7 | 10,8 | 16,8 | 23,7 | 31,3 | 39,7 | 49,0 | 59,6 | 72,2 |
| superior % | 27,8 | 40,4 | 51,0 | 60,3 | 68,7 | 76,3 | 83,2 | 89,2 | 94,3 | 98,2 | 100,0 |

- **Permite** separar «casi siempre completa» (9 o 10 de 10: límite inferior 59,6 % o más) de
  «completa la mitad de las veces» (5 de 10: límite superior 76,3 %).
- **No permite** separar una tasa de 80 % de una de 95 %, ni una tasa de rescate de 10 % de una
  de 50 % (3 de 10 da [10,8 · 60,3]).
- **Cero noches incompletas en 10 no demuestra que sean raras:** 0 de 10 da [0,0 · 27,8] %, y
  el **punto** del antecedente, 3 en 11 = 27,3 %, cabe ahí adentro por medio punto porcentual
  (su intervalo, [9,7 · 56,6], no).
- **La comparación pareada tampoco alcanza significación con este K salvo un patrón extremo.**
  McNemar exacto bilateral con `b` noches rescatadas y 0 perdidas: `b = 3` da p = 0,25;
  `b = 5`, p = 0,0625; recién `b = 6` da p = 0,0313. Esta regla **no afirma significación
  estadística**: es un umbral de decisión operativa fijado de antemano, y el p de McNemar se
  informa al lado, sin decidir.
- **La regla es conservadora y tiene poca potencia, y la rama (b) mucha menos que las demás.**
  Con todas las noches incompletas rescatables, y `p` la tasa real de noche incompleta a la
  hora actual (binomial, forma cerrada):

  | `p` | P(alcanzar el umbral base, 3 de 10) | P(alcanzar el umbral de (b), 5 de 10) |
  |---|---|---|
  | 0,10 | 0,07 | 0,00 |
  | 0,25 | 0,47 | 0,08 |
  | **0,273 (el antecedente, 3/11)** | **0,54** | **0,11** |
  | 0,40 | 0,83 | 0,37 |
  | 0,50 | 0,95 | 0,62 |

  **Dicho sin adornos: con la tasa del antecedente, esta regla indica (b) con probabilidad
  0,11**, aunque mover la hora fuera lo correcto y aunque el acta resolviera la pérdida de los
  viernes. Con el umbral base la alcanza poco más de la mitad de las veces (0,54). Se acepta
  porque el error caro es cambiar una regla o un timer sin sustento, porque (a) es el estado
  firmado, y porque el umbral de 5 no es un capricho sino el punto de empate medido (sección 4):
  por debajo de él, mover la hora con el código vigente es neto negativo. **Quien lea un «sin
  indicio suficiente» tiene que leerlo como «no alcanzó», no como «no hay».**
- **Esas probabilidades son de una sola corriente Bernoulli. La característica operativa de la
  regla entera no está medida** (sección 7).

## 3. El estadístico

**El universo que rige: los 33 operables sellados, no las 36 columnas.** La extensión descarga 36
tickers; el sello decide sobre 33 (`decidir()` calcula `insumo_completo` sobre `operables`, y §57
dice «33 de 33 con cierre»). Los tres que sobran, leídos de la máquina, son **ARM, ASML y SNDK**.
Rige el de 33 porque es el que define si una sesión cuenta; una columna no operable vacía no
pierde ninguna sesión. Los 36 se informan al lado. Entre los 33 están los dos ADR de mostrador
(**SHECY y TOELY**) y los tres ETF (SMH, SOXX, XSD).

**Por noche y por ticker:** la hora NY del primer casillero en que `es_sesion_de_hoy = 1`, o
«censurado en 03:35». Se informa para los 36.

**Por noche y por casillero `g`:** `C(D, g) = 1` si **en esa misma observación** los 33 operables
tienen `es_sesion_de_hoy = 1`. No se usa «ya había aparecido antes»: el sellador sella lo que ve a
su hora, y un cierre que estuvo y dejó de estar (hallazgo de la corrida 13) tiene que contar como
ausente. Un casillero «fuente inaccesible» o de apagón total da `C = 0`.

**El resultado a la hora actual:** `A(D)` = `insumo_completo` de las filas del sello de `D`
(condición V3). Es lo que el sellador vio de verdad a las 23:30 NY, no una aproximación.

**Horas candidatas para el sellador:** `t` en {00:00, 00:30, 01:00, 01:30, 02:00, 02:30, 03:00,
03:30} NY del día calendario siguiente a `D`. Cada una queda flanqueada por dos casilleros de la
sonda, 25 minutos antes y 5 minutos después. La noche `D` está **completa para `t`** si
`C(D, t − 25 min) = 1` **y** `C(D, t + 5 min) = 1`. Las candidatas van en punto y en media a
propósito: la sonda dispara a los :05 y :35 y las dos descargas nunca coinciden. No hay candidata
posterior a las 03:30 porque no habría observación después de ella. **Las ocho son posteriores a
la medianoche de Nueva York**, y eso tiene una consecuencia medida (sección 4).

**Clasificación de cada noche válida** (exhaustiva y excluyente):

| clase | definición |
|---|---|
| **C**, completa a la hora actual | `A(D) = 1` |
| **R**, rescatable moviendo la hora | `A(D) = 0` y completa para al menos una candidata `t` |
| **T**, rezagado puntual | `A(D) = 0`, no completa para ninguna `t`, y en el casillero de las 03:35 faltan **1 o 2** operables |
| **X**, fuente caída | `A(D) = 0`, no completa para ninguna `t`, y a las 03:35 faltan **3 o más** operables |

El corte entre T y X en 2 sale de la estructura del universo (hay exactamente dos ADR de
mostrador entre los 33, los dos candidatos conocidos a rezagarse), no de un dato de madrugada.

Para cada candidata `t`: `R(t)` = noches con `A = 0` completas para `t` (las que mover
**rescata**); `P(t)` = noches con `A = 1` **no** completas para `t` (las que mover **pierde**).

## 4. La regla

Con K = 10 noches válidas y concordancia suficiente (sección 1), sean `n_C`, `n_R`, `n_T`, `n_X`
los conteos por clase (`n_C + n_R + n_T + n_X = 10`). **El umbral base es 3 noches de 10**, que
es el menor conteo cuyo límite inferior de Wilson 95 % supera 10 % ([10,8 · 60,3]); rige para
(c) (`n_T ≥ 3`), para `n_X ≥ 3` y para la cláusula de «sin indicio suficiente». **La rama (b)
lleva un umbral más alto, 5 de 10, por la razón medida que sigue**, y vuelve a 3 sólo si el acta
de la sección 5, punto 2, evita la pérdida de los viernes. Los dos umbrales quedan fijos hoy.

**La convención de estimador queda fijada acá y no se cambia después: todo dimensionamiento de
esta regla usa el LÍMITE INFERIOR de Wilson, nunca el punto.** Es la elección conservadora. Con
el antecedente de 3/11 = 27,3 % y un rescate de 10,8 pp: 42,6 sesiones esperadas sin rescate
contra 37,1 con él, sobre las 31 que faltan para N = 40. Ése es el tamaño mínimo por el que se
juzgó que vale un acta. Es un juicio, fijado antes del dato.

**MEDIDO, y limita a (b) más que el umbral.** Con el código vigente, una emisión posterior a la
medianoche de Nueva York en un día sin sesión queda `dia_sin_sesion` y no cuenta (sección 5,
punto 2). Las ocho candidatas son posteriores a la medianoche, así que mover **todas** las
noches a cualquiera de ellas pierde las de viernes y víspera de feriado: 4 de las 20 sesiones
del plazo. En noches que cuentan por semana, con el límite inferior:

| qué se hace | cuenta | por semana |
|---|---|---|
| (a), como hoy | 5 × (1 − 0,273) | **3,64** |
| (b) en todas las noches, código vigente, rescate 10,8 pp | 4 × (1 − 0,273 + 0,108) | **3,34** |
| (b) de lunes a jueves y el viernes a las 23:30, rescate 10,8 pp | 4 × (1 − 0,273 + 0,108) + 1 × (1 − 0,273) | **4,07** |

**Con el umbral de 3, mover todas las noches con el código vigente es NETO PEOR que no mover
nada.** El rescate que empata es 18,2 pp, y el menor conteo cuyo límite inferior de Wilson lo
supera es **5 de 10** ([23,7 · 76,3]). Con el estimador puntual (3 de 10 = 30 pp, que ni cabe
bajo una tasa de pérdida de 27,3 pp: no se rescata más de lo que se pierde, así que valdría el
tope, 27,3 pp) la misma cuenta daría 4,00 y (b) ganaría: por eso la convención de arriba está
escrita, para que el signo de la conveniencia no dependa de qué estimador elija quien lea el
dato.

1. **(b), mover el sellador.** Sea `t*` **la más temprana de las candidatas que alcanzan el
   máximo de `R(t)` entre las que tienen `P(t) = 0`**.
   - Con **`R(t*) ≥ 5`**, la regla escribe que (b) queda indicada por su propio dimensionamiento,
     a las `t*`, aun perdiendo los viernes. La sección 5 sigue rigiendo.
   - Con **`R(t*)` igual a 3 o 4**, (b) queda indicada **sólo si el acta que responda la sección
     5, punto 2, evita la pérdida de los viernes y de las vísperas de feriado**. La regla
     entrega la tabla, las tres contabilidades de arriba recalculadas con el dato, y escribe con
     estas palabras que mover todas las noches con el código vigente es neto negativo. **La
     pregunta va a Nicolás.**
   - Se informan **`R(t)` y `P(t)` de las ocho candidatas**, no sólo de `t*`, cada una con su
     Wilson; y junto a cada `P(t) ≥ 1`, qué operable faltó y en cuál de los dos casilleros que
     flanquean a `t`, para que se vea si el veto de una candidata lo produjo una sola
     observación.
   - **`t*` es el argumento de un máximo sobre ocho comparaciones, y `R(t)` no es monótona en
     `t`** (un cierre puede dejar de estar). Por eso **el Wilson de `R(t*)/10` es el intervalo de
     un máximo seleccionado y su cobertura real es menor que 95 %:** se publica como cota
     optimista, con esta frase al lado.
   - Se informa la fracción completa a `t*` contra la fracción completa a la hora actual, cada
     una con su Wilson, y el McNemar exacto de (`R(t*)`, `P(t*)`), que no decide.
2. **(c), contar la sesión sin el ticker rezagado**, **no la elige esta regla**: si `n_T ≥ 3`, la
   regla **obliga a preguntarle a Nicolás** (sección 5) y entrega qué tickers faltaron, en cuántas
   noches cada uno y hasta qué hora.
3. **(a), mantener**, es el resultado en todos los demás casos, incluido `n_C = 10`. Se informa
   `n_C/10` con su Wilson y se escribe, con esas palabras, que mantener **no** es haber demostrado
   que las pérdidas son raras.
4. **`n_X ≥ 3`** no indica ninguna de las tres opciones: ni mover la hora ni sacar un ticker
   arregla una noche en que la fuente no publicó. Es un hallazgo sobre la fuente y va a tarjeta
   propia (segunda fuente, o aceptar la pérdida). Sigue (a).

**Cuando el resultado cae entre dos opciones:**

- **`R(t) ≥ 3` sólo en candidatas con `P(t) ≥ 1`** (mover rescata noches y pierde otras): (b)
  **no** queda indicada. Se entrega la tabla `R(t)`, `P(t)` por candidata y decide Nicolás.
- **`n_R ≥ 3` y `n_T ≥ 3` a la vez:** las dos ramas se cumplen y no compiten, porque arreglan
  noches distintas. Se presenta (b) con su hora y, aparte, la pregunta de (c).
- **Tres o más noches incompletas pero ninguna clase llega a 3** (por ejemplo 2 R y 1 T): sigue
  (a). La regla devuelve «sin indicio suficiente con K = 10», con los conteos y sus intervalos.
  **Juntar otras diez noches es una decisión nueva de Nicolás, con acta, y es una SEGUNDA LECTURA
  de la misma pregunta, no la primera lectura de una muestra más grande.** Si se toma: (i) se
  evalúa sobre las 20 con el umbral de 5 (límite inferior de Wilson mayor que 10 % con n = 20:
  [11,2 · 46,9]); (ii) el acta declara qué mostró la primera lectura y que la extensión se
  decidió con ese resultado a la vista; (iii) el resultado de las 20 se publica junto al de las
  10, nunca en su lugar; y (iv) el umbral de la segunda lectura no se recalcula con el dato de
  las 20. **No hay tercera lectura:** si las 20 no deciden, la regla se cierra en (a) y lo que
  siga es un diseño nuevo con su propio pre-registro.
- **Un ticker que no aparece a ninguna hora observada** en una noche la vuelve T o X según
  cuántos falten a las 03:35. Mover la hora no lo arregla y la regla no lo disfraza: esa noche
  nunca cuenta como rescatada.

**Límites que ninguna rama puede cruzar.**

- **La regla maestra.** El sello exige `available_at < timestamp_utc < apertura objetivo`, y la
  apertura objetivo es 09:30 NY del día siguiente. La candidata más tardía, 03:30 NY, deja 6 h.
  Ninguna hora posterior a las 03:30 NY es elegible por esta regla.
- **La sonda.** Una hora sólo es elegible si tiene observación después de ella.
- **El otro riel.** Ninguna candidata cae en la ventana del riel de medición (17:50 a 20:30 de
  Chile): las ocho van de la 01:00 a las 04:30 de Chile.

## 5. Lo que esta regla no decide

1. **(c) cambia una regla firmada** (§57, acta §86.1). Si `n_T ≥ 3`, la regla obliga a preguntar,
   y **no contesta**: si se adopta (c); si adoptarla **reinicia el contador** de E0; y **desde qué
   fecha rige**. Las sesiones perdidas no se recuperan en ningún caso (§86.1).
2. **(b) pasada la medianoche de Nueva York tampoco es sólo un cambio de hora. HALLAZGO, MEDIDO**
   con las funciones puras del sellador (`dia_en_calendario_del_exchange`, `es_sesion`,
   `proxima_sesion_despues_de`), sin base y sin red: el sellador deriva `fecha_sello` del día de
   Nueva York de la emisión, y si ese día no es sesión el estado es `dia_sin_sesion` y
   `cuenta_para_N = 0`. Una emisión a la 01:00 NY del **sábado** con el insumo del viernes da
   `dia_sin_sesion`; lo mismo la madrugada de un feriado. La tarjeta §58 dice que (b) «no reinicia
   el contador (la definición de "cuenta" no cambia)»: eso es cierto para una hora anterior a la
   medianoche y **no lo es para ninguna posterior**, y esta regla no tiene candidatas anteriores.
   Si (b) queda indicada, la regla obliga a preguntarle a Nicolás cómo se tratan esas noches, y
   no lo contesta. Dos caminos, ninguno elegido: dejar esas noches a las 23:30 con una segunda
   línea `OnCalendar` (sin tocar código, y esas noches no se rescatan); o que `estado_dia` mire
   la sesión del insumo y no el día de la emisión (toca `dinero/sello_dinero.py` y la definición
   de §57, con su pregunta sobre el contador).
3. **Extender K o el plazo.**
4. **Qué hacer con la fuente** si `n_X ≥ 3`.
5. **Nada sobre E1, E2, montos ni ventaja.**

## 6. Cómo se cambia la hora del sellador sin que dispare al instalar

Texto para Nicolás. **No se probó en ninguna unidad: PROPUESTA.** Cambiar un timer es acto suyo.

**Lo medido (n = 1 evento).** El 29-sep a las 18:38:57 de Chile, el journal muestra en el mismo
segundo `Stopped mki-sonda-cierre.timer`, `Started mki-sonda-cierre.timer` y
`Starting mki-sonda-cierre.service`: la sonda disparó en el acto del `restart`, fuera de sus dos
franjas, con `Persistent=no`.

**Lo que dice el manual, y lo que no.** `man systemd.timer` documenta el disparo inmediato sólo
para `Persistent=true`: «When the timer is activated, the service unit is triggered immediately
if it would have been triggered at least once during the time when the timer was inactive». **No
documenta qué instante usa de base un `restart` con `Persistent=false`.** El disparo de las 18:38
no sale del manual.

**Qué calendario estaba instalado antes del cambio.** Una sola línea,
`Mon..Fri 20..23:05,35 America/New_York`: es la que el acta §88.1 dice que Nicolás instaló, y el
CSV lo confirma (del 21 al 24-sep la primera observación de cada noche es la de las 20:05 NY y
no hay ninguna entre las 17:00 y las 19:59). La plantilla del repo decía `17..23:05,35` hasta la
corrida 14, y **nunca se instaló**: un contrafáctico calculado con ella no describe esta máquina.

**Dos hipótesis, las dos compatibles con lo medido, ninguna verificada:**

- **H-A (la del acta §91.7):** la base es el último disparo que el timer recuerda. Con base
  29-sep 00:35 Chile, `systemd-analyze calendar --base-time=` da 29-sep 01:05 Chile para la
  línea nueva de madrugada, ya pasado a las 18:38. Con el calendario instalado antes da 21:05,
  futuro: bajo H-A un `restart` sin cambio de calendario no habría disparado.
- **H-B:** la base es la activación anterior del timer (`InactiveExitTimestamp`). El journal
  registra `Started mki-sonda-cierre.timer` el 20-sep a las 02:05:59; el valor que la unidad
  tenía antes del `restart` ya no se puede leer de ella (el `restart` lo pisó con 18:38:57), y
  los otros siete timers `mki-*` conservan ese mismo 20-sep 02:05:59. Con esa base el próximo
  disparo calculado es 21-sep 21:05, ya pasado: bajo H-B **cualquier** `restart` de un timer que
  lleva días activo dispara en el acto, cambie o no el calendario.

Un solo evento no las separa, y separarlas exigiría reiniciar una unidad, que está prohibido.
**El procedimiento se escribe para la más severa de las dos: dar por hecho que cualquier
`restart` de un timer que lleva días activo dispara en el acto.**

**El sellador es el caso documentado.** `mki-sello-dinero.timer` tiene `Persistent=yes`: para él
el disparo al activar está en el manual. Ejemplo calculado, no ejecutado: con base en su último
disparo (29-sep 00:30 Chile) y un calendario hipotético `Tue..Sat 01:00 America/New_York`, el
próximo disparo sale 29-sep 02:00 Chile; un `restart` hecho después de esa hora dispararía en el
acto.

**Por qué importa la hora del día.** Si el sellador dispara un día hábil entre las 09:30 NY y su
hora, yfinance entrega la barra intradía con la fecha del día, la guarda E4 marca las 33 filas
`no_verificable_timing`, y el disparo bueno de la noche encuentra la fecha ya sellada y entra por
divergencia: **la sesión se pierde** (es lo que pasó el 28-sep; el parche de §62 que lo evita no
está aplicado). En cambio, un disparo en **sábado o domingo** encuentra como último insumo el
viernes, ya sellado el viernes a las 23:30: si el insumo es el mismo devuelve `ya_sellada` y no
escribe nada, y si cambió registra una fila en `divergencias_sello` y cero filas selladas. **No
quema ninguna sesión.**

**Procedimiento.**

1. **Cuándo.** Sábado o domingo, hora de Nueva York: después de las 04:00 NY del sábado (la sonda
   ya terminó su franja) y **antes de las 20:00 NY del domingo**. Nunca en día hábil.
2. **Antes, sólo lectura.**
   - `systemctl --user list-timers --no-pager` y anotar `NEXT` y `LAST` del sellador.
   - `systemctl --user show mki-sello-dinero.timer -p LastTriggerUSec -p InactiveExitTimestamp -p Persistent --no-pager`.
   - `systemd-analyze calendar --iterations=5 '<expresión nueva>'`: valida la expresión y muestra
     los cinco disparos siguientes.
   - `systemd-analyze calendar --base-time='<LastTriggerUSec>' '<expresión nueva>'` y lo mismo con
     `--base-time='<InactiveExitTimestamp>'`. **Si en cualquiera de las dos «Next elapse» es
     anterior a ahora, va a disparar al activar.** Si en las dos es posterior, igual se procede
     como si fuera a disparar.
   - Confirmar que el viernes quedó sellado: `python -m dinero.sello_dinero --estado`.
3. **El cambio.** Editar la unidad instalada (o reinstalarla desde la plantilla),
   `systemctl --user daemon-reload`, `systemctl --user restart mki-sello-dinero.timer`.
4. **Después.**
   - `journalctl --user -u mki-sello-dinero.service --since '-5min' --no-pager`: ¿disparó?
   - Si disparó, el final de `data/sello_dinero.log` tiene que decir `ya_sellada` o
     `divergencia_registrada` con `filas_insertadas: 0`. Una divergencia deja una fila nueva en
     `divergencias_sello`: se declara en el acta que registre el cambio.
   - `systemctl --user list-timers --no-pager`: `NEXT` es la hora nueva.
5. **Lo que no se hace.** No se cambia en día hábil «porque faltan muchas horas». No se usa
   `systemctl --user clean --what=state` para «olvidar» el último disparo: bajo H-B no impide
   nada, y borra la marca de la que depende `Persistent=true`.
6. **Si (b) se aplica pasada la medianoche,** la expresión nueva y el tratamiento de viernes y
   vísperas de feriado salen del acta que responda el punto 2 de la sección 5, no de este
   procedimiento.

## 7. Cómo se evalúa, y quién

- La evaluación la hace un script que **todavía no existe** (la sonda no se toca esta noche,
  acta §91.4). Se escribe en una corrida posterior, se prueba con CSV sintético, y el
  `estadistico-adversario` lo revisa contra este documento **antes** de que lea el CSV real.
- **La característica operativa de la regla entera NO está simulada, y nada de ella se publica
  hasta que lo esté.** Las tres probabilidades binomiales de la sección 2 son forma cerrada y
  están verificadas. Lo que no está verificado es el comportamiento conjunto de: máximo de
  `R(t)` sobre ocho candidatas, `P(t) = 0` con tolerancia cero, umbrales 3 y 5, interruptor de
  concordancia e invalidación V1 a V4. **Antes de que exista el script de evaluación,
  `GEMELO/simulador/` se extiende con un módulo que genere noches sintéticas** (33 operables, 16
  casilleros, aparición y desaparición de cierres, apagones totales y parciales, casilleros sin
  arranque) **y mida sobre esta regla exacta:** (i) cuando ninguna hora mejora la completitud,
  la probabilidad de que la regla indique (b) o entregue `n_T ≥ 3`; (ii) con una tasa de rescate
  verdadera conocida, la potencia; (iii) la cobertura real del Wilson de `R(t*)` como máximo
  seleccionado. Los tres números van al informe **antes** de que ningún agente lea el CSV de las
  noches. El precedente del método es `GEMELO/simulador/instrumento_dinero.py`.
- El informe de la evaluación publica la matriz entera, noche × casillero, con cuántos de los 33
  operables tenían cierre y cuáles faltaban, para que cualquiera rehaga la clasificación a mano.
  También las noches inválidas con su causa, las observaciones fuera de grilla y la tabla de
  concordancia.
- Si el script y este documento discrepan, manda este documento. Si este documento resulta
  inaplicable en un caso que no previó, la regla devuelve «NO DECIDIBLE», dice por qué, y el caso
  se agrega como enmienda fechada: no se improvisa una rama.

## 8. Limitaciones declaradas

1. **Dos descargas distintas.** La sonda pide `period=7d` y el sellador `period=30d` a la misma
   fuente. La concordancia (sección 1) las contrasta sólo a las 23:30 y 23:35; en la madrugada la
   sonda es vía única.
2. **Presencia no es frescura.** `es_sesion_de_hoy = 1` dice que hay una barra con la fecha de la
   sesión, no que su valor sea el cierre liquidado (corrida 13: TOELY con el mismo cierre dos días
   seguidos).
3. **Resolución de 30 minutos.** Un cierre que aparece a las 00:10 se ve a las 00:35.
4. **Una máquina, una fuente, un mes del año.** Nada acá dice cómo se comporta la fuente en
   diciembre ni desde otra red.
5. **K = 10 tiene la potencia que dice la sección 2**, que es poca: 0,54 para el umbral base y
   **0,11 para la rama (b)** a la tasa del antecedente. La de la regla entera, con el máximo
   sobre ocho candidatas y los interruptores, no está medida.
6. **Cinco parámetros son juicio, no dato:** el umbral de 3 noches (10 % de límite inferior), el
   corte de 2 tickers entre T y X, K = 10, el umbral de 2 noches discordantes, y la tolerancia
   cero de `P(t)`. Se fijaron antes del primer dato de madrugada, y por eso mismo no se sabe si
   son los mejores.
7. **De la noche del 29-sep se vieron tres observaciones de tarde** antes de sellar (sección 0).
   No entran al estadístico, y quedan declaradas.
8. **Las noches inválidas no faltan al azar.** V1 exige nueve arranques seguidos, que dependen de
   que la máquina esté despierta; el 28-sep mostró que esa misma condición gobierna al sellador
   y a la descarga. K = 10 es una muestra condicionada a que la máquina funcionara, y la tasa que
   mide es la de esas noches, no la del riel. La dirección del sesgo es desconocida y no se
   corrige: se declara.
