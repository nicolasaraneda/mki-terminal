# Dictamen del `estadistico-adversario` sobre la corrida 10

**7-sep-2026, 04:01 UTC (01:01 hora de Chile, leída de `date`).** HEAD `8dd0e0d`.
Alcance: los tres commits `e368dad`, `062287f`, `8dd0e0d`.

Todas las cifras de este dictamen se leyeron de la máquina (JSON, `cifras.py`,
git, `date`, mtimes) o se recomputaron con `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py`
y `backtest/inferencia.py`. Ninguna se citó de memoria.

Self-test del módulo, corrido antes de usarlo:

```
./venv/bin/python .claude/skills/estadistica-evaluacion/scripts/evaluacion.py
   -> TODO EN VERDE, reproduce Wilson 161/238 = [61.5, 73.3] y 138/238 = [51.6, 64.1]
```

---

## VEREDICTO

**Las seis cifras nuevas de la corrida 10 y los dos pre-registros nuevos.**

La conclusión de fondo de la corrida (nadie gana, L1 refutada, nada autoriza
nada) **se sostiene y sale reforzada** por este dictamen. Pero dos de las
cifras que la acompañan no resisten: la tasa de falsos positivos del bloque 4
está mal interpretada, y la celda superviviente de la señal larga no sobrevive
ni a la multiplicidad de su propia familia ni a la ablación que el propio
pre-registro del riel exige.

## CIFRA REPORTADA / CIFRA VERIFICADA

| # | Cifra reportada | Verificada | Comando |
|---|---|---|---|
| 1 | Mapa: 36/36 verificados, 6 representados, 2 sustituidos, 0 huecos, SMH no cabe en 500, 7 de 36 con 100 USD | **SÍ, exacta** | lectura de `dinero/resultados/universo_operable.json` |
| 2 | Comisiones 14 a 43 % del capital contra 0,4 a 0,6 % de no decidir | **SÍ**: 69,62 a 214,88 USD sobre 500 = 13,9 % a 43,0 %; SMH 3,00 = 0,60 %, XSD 2,00 = 0,40 % | lectura de `dinero/resultados/cuenta_papel.json` |
| 3 | 5 de 24 comparaciones con IC que excluye el cero | **El conteo SÍ. La interpretación NO.** 4 de esas 5 son `agresivo` contra `SMH`, todas con signo negativo | reejecución de `dinero.cuenta_papel.correr()` + `contabilidad.comparar` |
| 4 | L1 refutada; a 20 días dirección -2,339 pp [-4,522, -0,429]; L2 a 60 días +0,229 pp [+0,054, +0,424] | **SÍ, las seis celdas reproducen dígito a dígito** | reejecución de `senal_larga.evaluar` + `senal_larga_reporte.medir` |
| 5 | Potencia: sigma = 2,54 pp/semana, 52 semanas alcanzan para ~ +1,00 pp/semana | **SÍ**. sigma medido 2,5373; con ese sigma la tabla da 5054 / 809 / 203 / 51 exacta | `evaluacion.norm_ppf` + serie semanal reconstruida |
| 6 | Intentos: 3 (riel largo), 352 (asiático), 358 (veredicto 5.1) | **SÍ, los tres leídos del módulo** | `import` de los tres símbolos |
| 7 | Riel de medición: +9,7 pp, n=238, p=0,0455, IC día [-7,2, +26,6] | **SÍ** | `cifras.sellada()`, README línea 143, ESTADO.md línea 17 |

## INTERVALO

Todo lo que este dictamen afirma va con su intervalo y su método, explícito:

- Ventaja sellada del riel de medición: +9,7 pp (exacta 9,66), **IC95 de clúster
  de día [-7,2, +26,6]**, percentil de día; t de clúster [-8,1, +27,4];
  permutación de día p = 0,294; ICC 0,392, DEFF 3,55, n efectivo 67. McNemar de
  filas p = 0,0455 (chi cuadrado con corrección), exacta 0,0451 con b = 72 y
  c = 49, reproducida por `evaluacion.mcnemar_exact(72, 49) = 0.0451`.
- Señal larga: bootstrap **circular de bloques sobre fechas de emisión**,
  bloque = horizonte, 2000 réplicas, semilla 20260907, alfa 0,05. Reproducido.
- sigma semanal: 2,5373 pp/semana, **IC95 [2,1741, 2,8057]** por bootstrap
  circular de bloques (bloque 4 semanas, 5000 réplicas, semilla 20260907), que
  el pre-registro no publicó.
- Efecto mínimo detectable a 52 semanas: **+0,986 pp/semana, IC [+0,845, +1,090]**.
- Wilson de 5/24 suponiendo independencia (que **no** se cumple): [9,2 %, 40,5 %].
  Wilson de 1/24: [0,7 %, 20,2 %].

## DENOMINADOR

- **Riel de medición:** el denominador honesto es "siempre al alza" sobre las
  mismas 238 filas, 58,0 % [51,6, 64,1]. Correcto en README y en ESTADO.md.
- **Señal larga, dirección:** la climatología causal (signo mayoritario de la
  etiqueta **en el ajuste**) es el denominador honesto y es el que se usó.
  Correcto. No es 50 %.
- **Señal larga, magnitud:** la vara pre-registrada era "predecir cero", que
  **no es un denominador honesto en un mercado que sube**. El propio reporte lo
  reconoce y agrega la climatología causal, rotulándola POST-HOC. La rotulación
  es correcta y la dirección de la enmienda (endurecer tras un positivo) es la
  única dirección legítima. Se acepta.
- **Cuenta en papel:** el denominador declarado es SMH y XSD con aporte fijo.
  La nula que se le atribuye ("la respuesta verdadera es cero en las 24") **es
  falsa**, y de ahí sale el error del punto 3.

## ANÁLISIS DIMENSIONAL (obligatorio, mandato ampliado)

Unidad de cada argumento de cada estadístico que combina cantidades:

- Potencia: `sigma` en **pp por semana**, `delta` en **pp por semana**,
  `n` en **semanas**, `(z_alfa/2 + z_potencia)^2 = 7,848880` **adimensional**.
  Coherente. La aritmética pasa.
- MAE de la señal larga: **pp del retorno compuesto a h días hábiles**, no
  anualizado, no por día. Coherente entre modelo y varas.
- CRPS de la señal larga: **en proporción, no en pp**. El MAE se multiplica por
  100 en `medir()` y el CRPS no. La tabla publicada pone las dos columnas lado a
  lado y la de CRPS sale con la unidad vacía (`celda(..., unidad='')`). Un
  "+0,002" de CRPS son 0,2 pp. **Es un defecto dimensional real**, exigencia 12.
- Sharpe, PSR, DSR: **ninguno se computó en la corrida 10**. El pre-registro los
  declaró NO INTERPRETABLE por adelantado y cumplió. No hubo forma de repetir el
  incidente de la corrida 08.
- Comisiones: **USD sobre 156 semanas**, comparadas contra un umbral M2 definido
  sobre "el período" de 52 o 104 semanas. **Incoherencia de período**, exigencia 17.

## INTENTOS CONTADOS

Leídos del módulo, no de la prosa:

```
GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO = 352
backtest.veredicto_51.N_INTENTOS_51        = 358   (= 352 + 6)
dinero.registro_intentos.N_INTENTOS_RIEL_LARGO = 3
```

**¿Es defendible tener dos registros separados?** Sí en el principio, no en el
número.

Defendible: el DSR deflacta por la búsqueda sobre **la misma familia de
hipótesis**. El gap asiático de una noche sobre bolsas de Asia y una señal de 20
y 60 días hábiles sobre instrumentos de EE.UU. no comparten estimando, ni
horizonte, ni universo, ni etiqueta. Sumarlas produciría un DSR sin
interpretación y además movería un entero del que cuelgan doce bloques
publicados. `dinero/registro_intentos.py` declara el vínculo, no importa
`GEMELO`, y manda la decisión de fusión a firma. Eso es procedimiento correcto y
lo digo con la misma firmeza con que digo lo que sigue.

No defendible: **el 3**. La familia que efectivamente se evaluó no son 3
especificaciones, son **30 contrastes** (6 celdas por 5 intervalos cada una:
MAE contra cero, CRPS contra cero, MAE contra climatología, CRPS contra
climatología, dirección contra climatología). El resultado que se publica como
superviviente fue seleccionado como el mejor de esos 30, no de 3. Un registro
que dice 3 al lado de un 352 lee como disciplina y no lo es: **el conteo que
gobernaba la multiplicidad de esta corrida no lo lleva ninguno de los dos
registros**. Además la tercera vara (climatología) se agregó después de ver
resultados y por la convención del proyecto (regla 5: se cuentan todos, incluidos
los descartados) eso es un intento más que no está anotado.

**Este dictamen suma al registro, por la convención del §28:** las seis celdas
de la señal larga, los treinta contrastes que las acompañan, la vara
climatológica post-hoc, y las cinco hipótesis del bloque 4 que juzgué. Si el
orquestador no las anotó, quedan anotadas acá.

---

## CRITERIOS CONGELADOS, uno por línea

Los criterios V1 a V7 y R1 a R3 son del retador del **riel de medición**
(`GEMELO/DISEÑO.md` §6). La corrida 10 no corrió ningún retador contra el
campeón sobre la ventana sellada: fundó un riel distinto. Se evalúan igual, uno
por uno, y donde no aplican se dice.

- **V1 (ventaja sobre siempre al alza, McNemar p < 0,05): NO PASA.** Vara
  vigente leída de `cifras.sellada()`: +9,7 pp, McNemar de filas p = 0,0455 pero
  IC95 de clúster de día [-7,2, +26,6] y permutación de día p = 0,294. Con la
  unidad correcta (el día) sigue sin ser distinguible de cero. La corrida 10 no
  la movió y no la podía mover. V1 sigue **bloqueante** hasta que se firme
  V1-bis; `DISEÑO.md` §6 manda mientras tanto.
- **V2 (CRPS mejor que el campeón, IC de bloques que excluya el cero): NO
  EVALUABLE.** La corrida 10 computó CRPS, pero contra "predecir cero" y contra
  una climatología, sobre un estimando distinto (cadena de EE.UU. a 20 y 60 días
  hábiles). No hay comparación contra el campeón sobre el gap sellado.
- **V3 (cobertura del 80 % dentro de [76 %, 84 %]): NO EVALUABLE para un
  retador; el campeón NO PASA.** Campeón 92,9 % con ratio de ancho 2,19x
  [1,71, 2,78] sobre n = 238. La corrida 10 no produjo ningún intervalo
  predictivo calibrable: la señal larga emite media y sigma de residuos y nunca
  mide su cobertura empírica.
- **V4 (MAE del gap estrictamente menor que el del campeón, 2,52 pp sobre
  n=238, con igual o mayor cobertura de emisiones): NO EVALUABLE.** El MAE de la
  señal larga (5,3 a 19,0 pp) es de otra etiqueta y otro horizonte. Comparar
  esos dos números sería exactamente la clase de cantidad no ordenable que este
  dictamen se niega a ordenar.
- **V5 (DSR mayor o igual a 0,95 contando todos los intentos): NO EVALUABLE, y
  declarado así por adelantado.** El pre-registro §7 escribió antes de correr
  que el DSR saldría NO INTERPRETABLE (del orden de 33 observaciones no
  solapadas por par a 60 días) y cumplió: no se computó ninguno. Es la conducta
  correcta y es lo contrario del incidente del WS2b.
- **V6 (superar comprar SMH y no hacer nada, después de 25 pb por lado, con
  barrido): NO PASA, en la única lectura disponible.** Sobre una señal SIN
  información, el juego agresivo **pierde** contra SMH en las 4 pasadas del
  barrido, con el intervalo entero bajo cero (dif -0,613 a -0,652 pp/semana). No
  se barrió hasta 25 pb: el barrido llega a 10 pb. Ningún juego gana a SMH con
  intervalo que excluya el cero en ninguna pasada.
- **V7 (confirmación en el holdout en cuarentena, una sola evaluación): PASA en
  procedimiento, sobre el riel largo, NO EVALUABLE sobre el riel de medición.**
  La errata E2 reemplazó un walk-forward expansivo (que metía 36 % del último
  ajuste dentro de la prueba) por un ajuste único y una evaluación única sobre
  2023-09-05 a 2026-09-04, con embargo de 5 días más el horizonte más el
  retardo. Verifiqué `corte_de_ajuste`: purga = h + 1 + 5, correcta. La
  partición se escribió en el pre-registro commiteado en `e368dad`, anterior al
  commit del cómputo. Esa parte es fuera de muestra de verdad.
- **R1 (el control lineal regularizado le gana al modelo completo): NO EVALUABLE
  en el riel de medición.** En el riel largo no hay "modelo completo" contra el
  cual contrastar: las tres especificaciones son lineales. Nota que apunta en la
  misma dirección de R1: la única celda que sobrevive es una regresión lineal
  simple sobre un residuo, y la especificación más directa (L1) queda refutada.
- **R2 (la ventaja desaparece al excluir el bloque 1): NO EVALUABLE en el riel
  de medición; en el riel largo, DISPARA.** La corrí yo, porque el reporte
  declara que no se hizo. Sacando 2024 del período de prueba, la celda
  superviviente L2 a 60 días contra la climatología pasa de +0,229
  [+0,054, +0,424] a **+0,227 con IC [-0,011, +0,497], que contiene el cero**.
  Es la única de las cuatro ablaciones anuales que la mata, y es exactamente la
  ablación que `dinero/preregistro_dinero.md` exige antes de cualquier dinero.
- **R3 (cualquier fuga detectada): DISPARÓ en la v1, no reproducida en la v2
  publicada.** `auditor-lookahead` demostró una fuga de selección (la membresía
  de ocho años decidida con el último renglón del archivo, cambiaba el 42,9 % de
  las filas del panel) más tres sesgos con signo, y se corrigieron antes de
  computar métrica alguna. Las cifras publicadas son post-corrección. Quedan
  cuatro sesgos NO corregidos y **los cuatro empujan hacia el optimismo**:
  supervivencia, fuente no point-in-time (91,4 % de coincidencia, máximo 31,2 pp
  en el riel de medición), identidad de VRT (SPAC durante 17,8 % de la muestra,
  sigma diaria 0,59 % contra 3,86 %) y fuga por el analista. Los tres primeros
  son del mismo orden de magnitud que la mejora medida (+0,229 pp sobre 11,9).

## DICTAMEN

**NO SOSTIENE.**

Desglosado, porque un dictamen de una palabra sobre siete cifras sería
deshonesto:

- **SOSTIENE:** el mapa operable (censo exacto sobre el archivo congelado), la
  refutación de L1 por su regla pre-registrada, la aritmética de potencia, el
  costo de fricción como hallazgo robusto, el hecho de que nada de la corrida 10
  entró al README, la cita del riel de medición en ESTADO.md, y la conclusión
  general de que **nadie gana**.
- **NO SOSTIENE:** "5 de 24 (21 %) de falsos positivos" y la lectura de L2 a 60
  días como celda superviviente.
- **NO CONCLUYENTE:** todo lo demás del riel largo, por multiplicidad no
  corregida, base de bloques delgada y cero filas selladas.

---

# EXIGENCIAS

## Bloque 4, la cuenta en papel

**1. Retirar la cifra "5 de 24 (21 %) de falsos positivos".** Reejecuté la
comparación completa y las cinco marcadas son, textualmente:

```
MARCADO agresivo    vs SMH pb= 0.0  dif=-0.6128 IC=[-1.1724,-0.0930]
MARCADO agresivo    vs SMH pb= 2.0  dif=-0.6257 IC=[-1.1823,-0.1041]
MARCADO agresivo    vs SMH pb= 5.0  dif=-0.6354 IC=[-1.1892,-0.1136]
MARCADO agresivo    vs SMH pb=10.0  dif=-0.6516 IC=[-1.2034,-0.1336]
MARCADO conservador vs XSD pb=10.0  dif=+0.5683 IC=[+0.0493,+1.1564]
```

Cuatro de las cinco son `agresivo` contra `SMH` con signo negativo, o sea
**exactamente las cuatro que la §4 de la misma página llama "lo único
direccional que sí se sostiene" y "es el esperable"**. La página no puede
declarar el mismo intervalo como falso positivo en la §3 y como resultado
verdadero en la §4. Una sola comparación de las 24 (conservador contra XSD a 10
pb) es un positivo sin explicación de fricción: **1 de 24, o sea 4,2 %, que es
el alfa nominal y no dice nada**. Wilson de 1/24 = [0,7 %, 20,2 %].

**2. Corregir la nula.** "La respuesta verdadera es cero en las 24" es falso. La
estrategia y la línea base son **carteras distintas**: una tiene nombres sueltos
sorteados de 29 instrumentos, la otra un ETF; y la estrategia paga entre 70 y
215 USD de comisión sobre 500 mientras la base paga 2 o 3. El arrastre de
comisión garantiza una diferencia verdadera **negativa**, no cero. La nula
correcta es "sin habilidad", no "sin diferencia", y bajo esa nula los cuatro
intervalos negativos son detecciones verdaderas de la fricción.

**3. Las 24 no son 24 pruebas.** Los cuatro niveles de deslizamiento de
`agresivo` contra `SMH` dan -0,6128, -0,6257, -0,6354 y -0,6516: es el mismo
número cuatro veces. Las 24 comparten un solo sorteo, un solo calendario de
aportes y un solo conjunto de instrumentos. El número efectivo de comparaciones
independientes está más cerca de 6 que de 24, y ni siquiera esas 6 son
independientes. Declarar el número efectivo o no publicar una tasa.

**4. Una tasa de falso positivo necesita réplicas, y hay una.** El diseño corrió
**un** sorteo. Para afirmar "este diseño produce un tick el X % de las veces sin
que haya nada" hace falta repetir con K semillas de señal sin información y
reportar la distribución de la cuenta con su intervalo. Sin eso, "21 %" es n = 1
en la dimensión que importa.

**5. Corregir las tres citas río abajo del número retirado.** El 21 % es
portante en `dinero/preregistro_dinero.md` §2 condición 2, en su §5, y en el
veredicto de `dinero/resultados/senal_larga_v1.md`, donde además se transporta a
un diseño distinto (30 contrastes con bloques de fecha, no 24 comparaciones con
bloques de semana). La cláusula del pre-registro que ese número justifica es
correcta por otras razones; la razón hay que cambiarla.

**6. Las cifras de fricción van con distribución, no con rango de un sorteo.**
14 % a 43 % y 0,4 % a 0,6 % son rangos sobre 12 caminos de una misma semilla, no
intervalos. Repetir sobre K semillas y publicar el intervalo. El hallazgo
cualitativo (rotar la cartera con 500 USD cuesta un orden de magnitud más que no
rotarla) sobrevive con holgura; la cifra concreta no está respaldada.

**7. La línea base descrita no es la implementada.** `preregistro_dinero.md` §2
dice "aporte fijo semanal a SMH". `contabilidad.calendario_aportes` aporta 100
USD semanales **hasta agotar los 500 y después nada**: 5 aportes en 156 semanas.
El código lo documenta bien; el pre-registro, que es el documento que gobierna,
no. Corregir la descripción en el pre-registro, con fecha, sin borrar.

## Bloque 6, la señal larga

**8. El JSON declara 24 contrastes y el código computa 30.** `a_json` escribe
`"contrastes": len(celdas) * 4`, y `medir()` produce cinco intervalos por celda
(`ic_mae`, `ic_crps`, `ic_mae_clima`, `ic_crps_clima`, `ic_dir`). 6 x 5 = 30. La
prosa del .md justifica el 24 como "3 especificaciones x 2 horizontes x 2 varas
x 2 métricas", que deja los seis contrastes de dirección fuera de su propia
cuenta de multiplicidad. Corregir a 30.

**9. Aplicar y publicar una corrección de multiplicidad. Ninguna celda
sobrevive.** Lo corrí con un bootstrap de bloques conjunto sobre las mismas
fechas, bloque = horizonte, 2000 réplicas, semilla 20260907, con p bootstrap
bilateral, Holm, y máximo studentizado tipo Romano y Wolf:

```
familia COMPLETA, m = 30 contrastes
  L2 h=60 MAE  vs cero    punto +0.2633  p_boot 0.0030  p_Holm(30) 0.0900  NO PASA
  L2 h=60 CRPS vs cero    punto +0.0018  p_boot 0.0060  p_Holm(30) 0.1740  NO PASA
  L2 h=60 MAE  vs clima   punto +0.2293  p_boot 0.0060  p_Holm(30) 0.1740  NO PASA
  L2 h=60 CRPS vs clima   punto +0.0017  p_boot 0.0060  p_Holm(30) 0.1740  NO PASA
  L1 h=20 direccion       punto -2.3387  p_boot 0.0090  p_Holm(30) 0.2340  NO PASA
```

**Ninguno de los 30 cruza alfa = 0,05 bajo ninguna corrección familiar.** Dentro
del sub-familia de h = 60 (15 contrastes), Romano y Wolf da 0,0390 para
"L2 MAE contra cero" y **0,0730 para la celda que se publicó como
superviviente** (MAE contra la climatología). O sea: la respuesta depende de
cómo se defina la familia, y **la familia que el propio pre-registro define son
tres especificaciones por dos horizontes**, que son 30 contrastes. Con esa
familia, nada pasa.

**10. La simetría vale también para el resultado negativo.** El -2,339 pp de
dirección de L1 a 20 días, que se publica "con la misma firmeza", tiene p Holm
de 0,234 y p de Romano y Wolf de 0,1425. **Bajo multiplicidad tampoco es
distinguible de cero.** La refutación de L1 no depende de ese número: depende de
la regla del §6, que solo mira MAE contra cero y se cumple sola. Pero el -2,339
no se puede seguir publicando como un hallazgo negativo firme.

**11. Reportar b, c y McNemar en toda métrica de dirección.** El reporte no
publica ninguno. Los calculé con `evaluacion.mcnemar_exact`:

```
L1 h=20: b= 64 c=184  p = 1,235e-14
L2 h=20: b=965 c=951  p = 0,7665
L2 h=60: b=771 c=671  p = 0,009109
L3 h=20, L1 h=60, L3 h=60: b = 0, c = 0, p = 1  (predicción de signo constante)
```

El caso L2 a 60 días es **el mismo síntoma que ya tiene el riel de medición**:
McNemar de filas p = 0,0091 contra un IC de clúster de fecha [-4,742, +10,226]
que contiene el cero. El reporte hizo lo correcto al no reclamar la dirección,
pero omitió publicar los dos números que muestran por qué la fila miente. La
regla del proyecto pide b, c y p siempre.

**12. La columna de CRPS no declara su unidad y no está en la misma escala que
la de MAE.** `medir()` multiplica el MAE por 100 (pp) y deja el CRPS en
proporción. `_fila` llama a `celda(..., unidad='')` para CRPS. Un "+0,002" son
0,2 pp. Poner la unidad o llevar las dos columnas a pp.

**13. Publicar los bloques efectivos del bootstrap.** A h = 20 hay 733 fechas y
bloque 20: 36,6 bloques. **A h = 60 hay 693 fechas y bloque 60: 11,6 bloques**,
y toda la inferencia de la celda superviviente descansa sobre esos once y pico.
Un bootstrap de bloques con once bloques no tiene la cobertura que declara.
Corrí la sensibilidad al largo de bloque y el punto aguanta:

```
bloque= 20  bloques_efectivos 34.6  IC95 [+0.1124, +0.3536]  excluye 0
bloque= 60  bloques_efectivos 11.6  IC95 [+0.0543, +0.4238]  excluye 0
bloque= 90  bloques_efectivos  7.7  IC95 [+0.0372, +0.4438]  excluye 0
bloque=120  bloques_efectivos  5.8  IC95 [+0.0234, +0.4655]  excluye 0
bloque=180  bloques_efectivos  3.9  IC95 [+0.0275, +0.4477]  excluye 0
```

Esto se dice con la misma firmeza que lo negativo: **el solapamiento a 60 días
SÍ está tratado y bien**. Colapsar a media por fecha resuelve los siete pares
por fecha, y el bloque igual al horizonte cubre el solapamiento de la etiqueta.
Es una de las cosas mejor hechas de la corrida. Lo que falta es publicar cuántos
bloques quedan.

**14. Correr y publicar la ablación tipo R2, que el propio pre-registro del riel
exige y el reporte admite no haber hecho.** La corrí. Sacando un año calendario
del período de prueba a la vez, sobre la celda superviviente:

```
completo:   media +0.2293  n_fechas 693
sin 2023:   +0.2624  IC [+0.0630, +0.4855]  EXCLUYE 0   (solo 2023: n= 82, media -0.0172)
sin 2024:   +0.2265  IC [-0.0108, +0.4967]  CONTIENE 0  (solo 2024: n=252, media +0.2343)
sin 2025:   +0.2111  IC [+0.0194, +0.4181]  EXCLUYE 0   (solo 2025: n=250, media +0.2616)
sin 2026:   +0.2107  IC [+0.0330, +0.4125]  EXCLUYE 0   (solo 2026: n=109, media +0.3294)
```

**Sin 2024 el intervalo contiene el cero.** Es la misma forma exacta del R2 que
hoy descalifica al campeón del riel de medición: la significancia cabalga una
ventana. Publicarlo junto a la celda o retirar la celda.

**15. El registro de intentos del riel largo debe declarar su convención y
subir de 3.** La familia efectivamente evaluada son 30 contrastes; el resultado
publicado es el máximo sobre esos 30; y la vara climatológica es una vara
agregada después de ver resultados, que por la regla de la casa cuenta. Un
registro que no cuenta lo que gobierna la multiplicidad del resultado que
acompaña no está haciendo su trabajo, por más que la separación de familias sea
correcta.

**16. Declarar por escrito, con artefacto, que ninguna métrica se computó sobre
la v1 con fuga.** El §9 del pre-registro afirma "sin que se haya calculado un
solo MAE, acierto ni CRPS" y que "el orden está verificable en git". **En git no
lo está:** el archivo entró en `e368dad` (132 líneas, §1 a §8), pero el §9, el
código y los resultados entraron todos juntos en `062287f`. Lo que sí corrobora
son los mtimes, que contrasté:

```
GEMELO/preregistro/senal_larga_v1.md   23:39:55   (el §9)
dinero/senal_larga.py                  23:41:34
dinero/senal_larga_reporte.py          23:44:32
dinero/resultados/senal_larga_v1.json  23:44:33
```

El §9 precede al cómputo por 4,5 minutos. Es evidencia corroborante y es
mutable. **Si no se computó ninguna métrica sobre la v1, la enmienda no suma al
registro y lo acepto; si se computó alguna, suma.** Exijo que se declare cuál de
las dos, y que la próxima enmienda a un pre-registro entre en su **propio
commit, anterior al del cómputo**, que es lo que el §9 dice de sí mismo y no
cumple.

## Bloques 2 y 5, potencia y pre-registro del riel de dinero

**17. La tabla de potencia no la produce ningún código.** No existe script en
`dinero/` que la reproduzca: está escrita a mano en el markdown. Verifiqué la
aritmética y **pasa exacta**:

```
(z_0.975 + z_0.80)^2 = (1.959964 + 0.841621)^2 = 7.848880   [adimensional]
sigma medido (conservador vs SMH, 5 pb, 156 semanas) = 2.5373 pp/semana
  delta +0.10 -> n = 5053.9 -> 5054 semanas   (publicado 5054)
  delta +0.25 -> n =  808.6 ->  809 semanas   (publicado  809)
  delta +0.50 -> n =  202.2 ->  203 semanas   (publicado  203)
  delta +1.00 -> n =   50.5 ->   51 semanas   (publicado   51)
```

Las cuatro filas reproducen. **Exigencia: escribirla como script sellado**, que
es la regla del proyecto para toda cifra publicada.

**18. sigma = 2,54 es un punto sin intervalo, y no es un solo número.** Le puse
el intervalo que le falta, con bootstrap de bloques de 4 semanas y 5000
réplicas: **sigma = 2,5373 [2,1741, 2,8057] pp/semana**, y por lo tanto el
efecto mínimo detectable a 52 semanas es **+0,986 pp/semana [+0,845, +1,090]**.
La conclusión cualitativa del pre-registro aguanta y hay que decirlo. Pero
sigma depende del camino del barrido:

```
pb= 0.0: sigma 2.5374 -> 51 semanas para +1.00 pp/semana
pb= 2.0: sigma 2.5373 -> 51
pb= 5.0: sigma 2.5373 -> 51
pb=10.0: sigma 3.6503 -> 105
```

La propia página insiste en que las filas del barrido **son caminos distintos,
no la misma estrategia a otro costo**. Publicar 2,54 sin decir de qué camino
salió, y luego usar ese número para fijar el criterio de decisión de todo el
riel, es elegir el camino favorable. En el camino de 10 pb, 52 semanas solo
alcanzan para +1,42 pp/semana.

**19. M2 compara un porcentaje de 156 semanas contra un umbral de 52.** El
pre-registro dice "si la comisión acumulada del juego por defecto supera el 25 %
del capital aportado **en el período**" y concluye "M2 está a punto de
dispararse antes de empezar", citando el 14 a 43 %. Ese 14 a 43 % es de 156
semanas. Medí la peor ventana móvil:

```
                total 156 sem       peor 52 sem        peor 104 sem
conservador     125.87  (25.2%)     50.27  (10.1%)     91.47  (18.3%)
medio           133.78  (26.8%)    108.91  (21.8%)    133.78  (26.8%)
agresivo        214.87  (43.0%)     74.15  (14.8%)    143.90  (28.8%)
```

**Sobre la ventana de 52 semanas que la §2 declara, ningún juego llega al 25 %.**
M2 no está a punto de dispararse: se dispara recién a 104 semanas, y solo para
`medio` y `agresivo`. Fijar el período de M2 explícitamente y recalcular.

**20. M4 no puede cerrar el riel como está escrito.** M4 dispara si "la señal
larga no supera **ninguna** de sus dos varas". Con 30 contrastes correlacionados
a alfa 0,05, la probabilidad de que el ruido puro cruce al menos uno es alta
(con 30 contrastes independientes sería 0,79; con la correlación medida acá es
menor pero sigue siendo la mayoría de las veces). O sea: **M4 es una cláusula
que el ruido pasa casi siempre y por lo tanto no cierra nada.** Reescribirla en
términos de la familia corregida por multiplicidad, o M4 es decorativa.

## Verificaciones estructurales

**21. Referencias colgantes en `dinero/preregistro_dinero.md`.** Tres documentos
citan un "§2.5" que no existe (`ESTADO.md`, `dinero/senal_larga_reporte.py`
línea 356, y el encargo). El documento tiene §1, §2, §2.1, §3, §4, §5. Su propio
§5 cita un "§2.2" que tampoco existe. Es el mismo modo de falla que la memoria
del proyecto ya registró para las citas por número de línea en `DECISIONES.md`.

**22. El titular del mapa reporta la variante permisiva.** El JSON trae dos
censos: `representados 6 / sustituidos 2 / huecos 0` y
`representados_exigiendo_liquidez 5 / sustituidos 3 / huecos 0`. El titular de
ESTADO.md pone el primero adelante y el segundo entre paréntesis. Los dos están
publicados, que es lo correcto; pero la cifra que encabeza es la de la
condición más floja. Además el censo es de **un solo día** (cierres del
2026-09-04) y no declara los casos al borde: **MSFT queda fuera de "comprable
con 500 USD" por 30 centavos** (499,70 más 1,00 de comisión mínima = 500,70), y
XSD entra por 7,55. Un censo sin declarar sus casos al borde se lee como estable
y no lo es. Los que no están al borde (SMH a 567,01, ASML a 1.714,88, SNDK a
1.740,00) sí son afirmaciones robustas y se pueden publicar como tales.

**23. Verdad conocida antes que verdad observada: no se cumplió.** Ningún
estimador de intervalo, ninguna afirmación de potencia y ningún umbral de
decisión de esta corrida se corrió contra `GEMELO/simulador/`. Verifiqué:
`grep -rn simulador dinero/` no devuelve nada, y el proyecto ya tiene
`GEMELO/simulador/potencia_por_metrica.py` y `frase_potencia.py`. Se acredita
que la cuenta en papel **es** una verificación con ventaja verdadera cero, y eso
es exactamente el espíritu de la regla, pero falta la mitad: **la corrida con
ventaja verdadera conocida y distinta de cero**, que es la que dice si el
procedimiento la encuentra. Sin esa mitad, la tabla de potencia y el criterio
del §2 son aritmética sin validar.

**24. Multiplicidad bajo la nula, con el ICC medido.** El proyecto ya tiene el
incidente del "0 de 192". La corrida 10 publica "una celda de seis" sin decir
qué produce la nula. Lo di en la exigencia 9 vía Holm y Romano y Wolf, pero la
regla pide más: la **distribución de k bajo la nula con el ICC medido**, sobre
este diseño concreto. Exigirla antes de que cualquier celda de esta familia
vuelva a aparecer en un documento.

## Lo que quedó bien y se dice con la misma firmeza

- Las seis celdas de la señal larga **reproducen dígito a dígito** desde el
  archivo congelado (sha256 `69ca7283...`, 2011 filas, 2018-09-05 a 2026-09-04).
- El intervalo de la señal larga **no es iid**: colapsa a media por fecha de
  emisión y usa bootstrap circular de bloques con bloque igual al horizonte.
  Trata el solapamiento y el clúster. Es lo correcto.
- La vara climatológica post-hoc está **rotulada como post-hoc** en el JSON y en
  el .md, y **endurece** la prueba después de un positivo, que es la única
  dirección legítima de una enmienda no pre-registrada.
- Las tres direcciones de signo constante están declaradas **métrica vacía** en
  vez de publicarse como empate en 0,000 pp. Es la lección del PSR saturado,
  aplicada.
- La errata del pre-registro es **estrictamente aditiva**: `git diff e368dad
  062287f` sobre `senal_larga_v1.md` muestra +70 líneas y **0 borradas**.
  El §8 no se tocó.
- **El README no se movió.** `git diff origin/main..main -- README.md` está
  vacío. Ninguna cifra del riel de dinero entró a la portada. Los JSON dicen
  `"estatus": "PROPUESTA"` y `"advertencia": "Ninguna cifra entra al README"`.
- **La cifra del riel de medición se cita correctamente.** `cifras.sellada()`
  devuelve n = 238, 67,6 % contra 58,0 %, ventaja 9,7 pp (exacta 9,66), IC de
  día [-7,2, +26,6], McNemar 0,0455 (exacta 0,0451, b = 72, c = 49), permutación
  de día 0,294, ICC 0,392, DEFF 3,55, n efectivo 67. README línea 143 coincide.
  ESTADO.md línea 17 coincide y además dice explícitamente que el IC contiene el
  cero. **`bitacora_10.md` no la cita**, y eso no es un error: la bitácora
  reporta lo que la corrida hizo, declara que no tocó el registro de intentos
  del gap (352 / 358) y no repite una cifra que no midió. Es la conducta
  correcta.
- Ningún criterio congelado se movió en estos tres commits. Revisé el diff de
  `DECISIONES.md`: no hay umbral desplazado, y `N_INTENTOS_ACUMULADO` y
  `N_INTENTOS_51` quedaron intactos en 352 y 358.

## La advertencia de siempre

n = 228 en un solo régimen es más chico que n = 228, y **5131 filas sobre 733
fechas son 733, no 5131**; a 60 días, con bloque 60, son once bloques y pico.
Nada de lo que se midió en el riel largo tiene una sola fila sellada. La ventana
larga da potencia; solo el sellado en vivo da validez. Cuatro sesgos declarados
y no corregidos empujan todos hacia arriba, y son del mismo orden que la única
mejora que quedó en pie antes de que la multiplicidad y la ablación se la
llevaran.
