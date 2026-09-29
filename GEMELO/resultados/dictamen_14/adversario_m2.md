# Dictamen del `estadistico-adversario` — la §9 de `dinero/preregistro_dinero.md`

**Corrida 14, bloque 4.4.** Encargo: dictaminar si la enmienda de M2 es aplicable tal como está
escrita o si le falta una definición; lo que falte va a tarjeta con opciones, **no se rellena**.

Transcripción por el orquestador. El adversario leyó la skill `cifras-canonicas` antes de juzgar y
corrió el self-test de `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py` en verde. No
escribió ni modificó ningún archivo del proyecto.

## VEREDICTO

```
VEREDICTO: la §9 redacta fielmente cuatro de las cinco firmas del acta §88, pero contiene
           UNA AFIRMACIÓN FALSA Y MEDIBLE («el 8,3 %/año no endurece ni ablanda el
           criterio») que no está en el acta, y le faltan seis definiciones, no cuatro.

DICTAMEN: ENMIENDA CON DEFECTO DE REDACCIÓN
          (y, una vez corregido el defecto, sigue siendo NO APLICABLE: FALTAN DEFINICIONES)
```

**Todo lo exigido se aplicó a la §9 dentro de la misma corrida, antes de cualquier commit y antes de
que Nicolás la leyera** (y la misma frase defectuosa se corrigió en `bitacora_14.md` §4.5, donde se
había propagado). La enmienda sigue siendo PROPUESTA y NO APLICABLE: las seis definiciones que faltan
son de Nicolás.

## La cifra reportada y la verificada

- **Token a token, las tres filas que la §9 citaba COINCIDEN con la fuente** y la columna es la
  correcta («anualizada desde 52»): conservador `3.9 % [3.56, 4.58]`, agresivo `6.4 % [5.77, 7.78]`,
  medio `9.4 % [8.23, 10.82]`. Medianas exactas del JSON: 3,87 / 6,44 / 9,38 → los redondeos publicados
  son correctos. 25/3 = 8,3333… verificado.
- **Lo que NO se reproduce es la frase de neutralidad.**

## El defecto: «no endurece ni ablanda» es falso, y es medible

El acta §88.11 afirma **procedencia** («8,3 %/año … es decir 25/3», «pq se deriva de mi numero
original»). La §9 la convirtió en una afirmación de **severidad**, que el acta no hace. Y es falsa:
el umbral nuevo es **156/h veces más exigente** que el 25 % acumulado en todo horizonte menor a 156
semanas. Misma cuenta, mismo *h*, umbral viejo contra nuevo (reproducido por el orquestador con el
script del adversario):

```
conservador  h= 52  vieja(>25%)  0/20   nueva(>8.333)  0/20  Wilson95 [0.0,16.1]
conservador  h=104  vieja(>25%)  0/20   nueva(>8.333)  0/20  Wilson95 [0.0,16.1]
conservador  h=156  vieja(>25%)  0/20   nueva(>8.333)  0/20  Wilson95 [0.0,16.1]
agresivo     h= 52  vieja(>25%)  0/20   nueva(>8.333)  0/20  Wilson95 [0.0,16.1]
agresivo     h=104  vieja(>25%)  0/20   nueva(>8.333)  0/20  Wilson95 [0.0,16.1]
agresivo     h=156  vieja(>25%)  0/20   nueva(>8.333)  0/20  Wilson95 [0.0,16.1]
medio        h= 52  vieja(>25%)  0/20   nueva(>8.333) 19/20  Wilson95 [76.4,99.1]
medio        h=104  vieja(>25%)  0/20   nueva(>8.333) 17/20  Wilson95 [64.0,94.8]
medio        h=156  vieja(>25%) 17/20   nueva(>8.333) 17/20  Wilson95 [64.0,94.8]
```

A h = 52 el estadístico es idéntico bajo las dos lecturas (52/52 = 1), así que la comparación no
depende de ninguna convención: **3× más duro, y `medio` pasa de 0/20 a 19/20 en la única lectura que
la propia (d) autoriza.** El endurecimiento es 1× sólo a h = 156, donde coincide por álgebra.

Y el grado de libertad E12 deja de ser inerte: de las tres re-expresiones redondas del 25 % —25/1 =
25,0 %/año, 25/2 = 12,5 %/año, 25/3 = 8,333 %/año— **la elegida es la única que mata algo** (0/20,
0/20, 19/20). Con 12 lecturas a la vista. No es ilegítimo —§88.11 lo declara— pero no es un
re-expresado inerte.

**Corregir esto no ablanda ningún criterio** y no mueve el umbral: corrige una caracterización falsa,
con fecha, como la §5 autoriza. El umbral se puede firmar tal cual.

## Sobre la banda y la tabla del «costo aceptado»

- La banda es p2,5–p97,5 **entre 20 semillas sobre UNA trayectoria de mercado**, y la fuente la define
  como «(no un IC de cobertura nominal)». La §9 no trasladaba ese descargo y llamaba «banda» a algo
  que se lee como un intervalo de cobertura. Faltaban también los **mín–máx**, que la fuente instruye
  leer al lado.
- **Con K = 20 el percentil 2,5 no es estimable:** el 8,23 de `medio` es una interpolación al 47,5 %
  entre la semilla más baja (8,14) y la segunda (8,34). «El borde inferior de la banda» **es una
  semilla**. El estadístico honesto es el conteo con Wilson sobre semillas.
- **La §9 subdeclaraba el costo de su propia elección**, que es el error más raro: «el borde inferior
  queda apenas bajo el umbral» sugiere ambigüedad donde la simulación da 19/20. El conteo no está en
  la fuente (`m2_periodo.py:146` cuenta contra `UMBRAL_M2_PCT = 25.0`), hubo que computarlo.
- **`agresivo` < `medio` merece una línea y es fuerte:** el costo por orden es ≈ 0,302 / 0,300 / 0,238
  USD (verificado contra los conteos de `dinero/resultados/cuenta_papel.md`: 62,00/205, 133,00/443,
  93,50/393), así que **M2 ≈ órdenes × ~0,3 USD ÷ capital**. `medio` gasta más por hacer más órdenes
  (443 contra 393), por granularidad con 500 USD y acciones enteras. **El umbral no mata al juego más
  arriesgado, mata al más granular**, y los nombres hacen suponer lo contrario. Además las holguras no
  son comparables: la peor semilla de `agresivo` está a +6,4 % del umbral y la de `conservador` a
  +77,7 % — una diferencia de 12× que la misma frase «no dispara» aplanaba.
- Faltaba declarar que **el arancel del §40 que fija el numerador sigue SIN FIRMA** (tarjeta §48).

## La fórmula: dimensionalmente correcta, definicionalmente incompleta

El análisis dimensional pasa: USD/USD × (semanas/año)/semanas = año⁻¹ → %/año, y el umbral está en la
misma unidad. No hay el error de unidades de la corrida 08. La forma equivale a un gasto en **USD por
USD-año**, que es la lectura económicamente correcta de un ratio de costo.

**Pero** esa equivalencia sólo vale si el capital es constante en [0, h], y con la rampa de aportes no
lo es: con el calendario declarado el factor ponderado-por-tiempo es 1,0375× (`medio` 9,38 → 9,73), y
si el flujo prospectivo fuera 100 USD/semana sostenido durante 52 semanas, **1,957× — casi 2×, más que
toda la distancia entre `conservador` y `medio`**.

**El factor lineal 52/h premia a la cuenta muerta**, y quedó medido: las 3 semillas de `medio` que se
congelan leen 9,42 → 7,55 → 5,04; 9,40 → 7,03 → 4,69; 9,43 → 7,65 → 5,10 a h = 52/104/156. A h = 156,
**17 de 17 vivas cruzan y 0 de 3 congeladas cruzan**. Dos matices que el adversario declaró contra su
propio hallazgo: (i) la **mediana apenas se mueve** (4,12 con todas contra 4,17 sólo vivas), así que la
estabilidad que (a) usa para justificar la unidad **sobrevive** el chequeo; (ii) el problema no es el
factor lineal en sí, sino que **la anualización aritmética no está firmada**. Y hay un límite
estructural: **a h = 52 no hay ninguna semilla congelada**, así que la única lectura que (d) autoriza
es la que no puede ver el sesgo.

## Las seis definiciones que faltan

Las cuatro que el autor ya declaraba están **bien planteadas**, con un defecto en el juego de opciones
de la primera, y hay **dos más**:

1. **Denominador durante la rampa.** Dos de las tres opciones del autor eran **la misma** (aportado
   final ≡ aportado a la fecha de lectura para todo h ≥ 5 con el calendario declarado) y una no es
   computable en el momento de la lectura. La bifurcación real es **ponderado por tiempo o no**. Y
   faltaba declarar que las cifras citadas **ya usan** «aportado a la fecha de lectura»
   (`GEMELO/m2_periodo.py:91`), y que la **§6 C** (declarar el flujo prospectivo antes de empezar)
   sigue sin declararse.
2. **Qué es «congelada», y es peor:** el código usa «26 semanas sin ningún movimiento»
   (`m2_periodo.py:96`), una **proxy de inactividad** con una constante que no está en ninguna
   especificación, mientras §88.13 define un **estado de caja**. E4 del dictamen 12 pedía las dos
   condiciones y sólo se implementó la primera; la caja se verificó a mano en **2 de las 5** semillas.
   Y `dinero/contabilidad.py:215` dice que la cuenta **no se detiene** por falta de caja («ACUMULA»):
   no hay estado terminal en el código. **La cifra «5 de 20 congeladas» no mide el concepto que el
   acta firmó.**
3. **Si congelada mata o sale del cómputo.** §88.13 firma una **tercera** cosa: «estado aparte, y se
   informa como tal» — ni E13 («eso dispara M2») ni un promedio. La §9 le agregaba «no se promedia con
   las cuentas vivas», que el acta no dice y que **prospectivamente no tiene referente: hay UNA
   cuenta**. Es un concepto de la simulación de 20 semillas importado a un criterio que se leerá con
   n = 1.
4. **Domicilio del contador de «lecturas de criterio»:** ya abierto en §88.14 y en la tarjeta §43. **No
   hace falta tarjeta nueva**; hace falta completar §43 con opciones, que es lo que la §9 prometía y no
   cumplía. Tampoco tocar §23 (es H1/H2/I) y §48 (arancel) hay que **citarla**, no duplicarla.
5. **NUEVA Y URGENTE — qué es «el primer aporte».** Es el cero de *h* y la identidad del denominador,
   y no está definido. §88.10 registra la cuenta IBKR **ya fondeada con 5,00 USD**:
   ```
   capital=  5,0 USD, 1 orden al mínimo 0,35 -> M2 =  7,00 %/año
   capital=  5,0 USD, 2 órdenes             -> M2 = 14,00 %/año  DISPARA
   capital=  5,0 USD, 5 órdenes             -> M2 = 35,00 %/año  DISPARA
   capital=500,0 USD, 5 órdenes             -> M2 =  0,35 %/año
   ```
   **Dos órdenes cierran el riel.** Cien veces de diferencia según qué aporte cuente. Y la §4 declara
   los primeros 100-500 USD como «costo de aprendizaje operativo, no una apuesta», explícitamente **no**
   condicionados a la §2: si sus comisiones entran al numerador, M2 mide el aprendizaje. Además toca la
   validez de la propia enmienda: si *h* ya arrancó con ese fondeo, **puede estar llegando tarde a su
   propio reloj**.
6. **NUEVA — la convención de anualización** (`× 52/h` lineal) no está firmada: §88.7 firmó «tasa
   anualizada (%/año)» y el factor lineal es una elección de módulo.

**Y cuatro huecos menores:** (D7) dónde se sella la comisión del corredor y qué pasa si falta —
`corredor/ibkr.py` lee `commissionReport` pero **no persiste nada**, `sellos_dinero` no tiene columna
de comisión ni de ejecución, `comision_usd` puede volver `None` sin regla, el `commissionReport` llega
asíncrono y puede revisarse (choca con la inmutabilidad de sellos), y **el alcance del numerador no
coincide con el de la calibración**: `reglas.json` deja las tarifas de terceros fuera del modelo con el
que se calibró el 8,3, y un numerador 10 % mayor lleva la peor semilla de `agresivo` de 7,83 a 8,61 y
**la cruza**; la serie separada de deslizamiento que la §9 nombra **no existe**. (D8) la cadencia
después de la semana 52 y si leer M2 cuenta como «mirada» (la §2 punto 4 dice que mirar antes reinicia
el período), más el orden de precedencia cuando la lectura de M2 y la evaluación única de la §2 caen el
mismo día; y que §88.13 dice «y después sigue», que la §9 había borrado. (D9) descongelamiento, y que
*h* cuenta semanas de **calendario**, así que una interrupción del riel baja la tasa igual que el
congelamiento sin ser «sin caja para una acción entera». (D10) si el umbral es 8,3 o 25/3 = 8,3333…

## Lo que la §9 le ponía en la boca al acta

Verificado línea por línea contra `DECISIONES.md` §88. **Consta en el acta:** unidad %/año opción (c);
umbral 8,3 %/año = 25/3 y su razón; deslizamiento no cuenta; acumulado desde el primer aporte con
primera lectura a las 52; congelada «no cuenta como M2 cumplida, estado aparte» y su razón; E12; el
contador sin dueño. **NO consta:** la fórmula `× 52/h` explícita; «no endurece ni ablanda» (**y es
falsa**); «en su propia serie» (artefacto inexistente); «inválida por construcción, sea cual sea su
valor» (más fuerte que el acta); «no se promedia con las cuentas vivas»; «esto no la invalida — el
umbral es el original re-expresado» (**no se sostiene**). **Omitido:** la marca «(RETIRADA)» en la cita
de la banda del 25 %, y el «y después sigue» de §88.13.

## Criterios y conteo

**V1 a V7 y R1 a R3: NO EVALUABLES** — son del retador de `GEMELO/DISEÑO.md` y este bloque no evaluó
nada del retador. **M1 a M4 (los del riel de dinero): NO EVALUABLES** — M2 es exactamente lo que esta
§9 intenta volver legible y todavía no lo logra; M4 sigue decorativa (tarjeta §44).

**Intentos de DSR: 0, sin cambio** — la nula es conocida por construcción (la señal es
`senales_sin_informacion`) y ninguna de estas cifras es tipo Sharpe. **Lecturas de criterio: 12 ya
computadas + 2 actos de firma sobre la misma pregunta + 3 re-expresiones que este dictamen computó**,
y **no se pueden archivar porque el contador sigue sin domicilio**.

## Exigencia sobre el simulador, que no bloquea el texto

`GEMELO/simulador/` no tiene nada de M2 ni de comisiones (verificado: cero coincidencias de
`comisión`/`m2` en sus seis módulos). Nadie midió `P(M2 dispara | tasa verdadera = 8,333 %/año)` para
**una** cuenta leída a 52 semanas, y con `n_historias_de_mercado: 1` no se puede. **El simulador tiene
que extenderse a múltiples trayectorias de mercado antes de que se cite cualquier tasa de error de
M2.** Esto no bloquea la enmienda; bloquea toda afirmación de la forma «M2 dispara cuando debe».

## Reproducción

```bash
cd /home/nicolasaraneda/dev/mki-terminal && source venv/bin/activate
python .claude/skills/estadistica-evaluacion/scripts/evaluacion.py          # self-test verde
python - <<'PY'
import json, numpy as np, sys
sys.path.insert(0,'.claude/skills/estadistica-evaluacion/scripts')
from evaluacion import wilson_ci
r=json.load(open('GEMELO/resultados/m2_periodo.json')); ps=r['por_semilla']; UM=25/3
for j in ('conservador','agresivo','medio'):
    for h in (52,104,156):
        va=np.array([s[j][f'pct_a_{h}_semanas'] for s in ps],float)
        vn=np.array([s[j][f'pct_anualizado_desde_{h}'] for s in ps],float)
        k=int((vn>UM).sum()); lo,hi=wilson_ci(k,len(vn))
        print(f'{j:12s} h={h:3d}  vieja(>25%) {int((va>25).sum()):2d}/20   nueva(>8.333) {k:2d}/20'
              f'  Wilson95 [{100*lo:.1f},{100*hi:.1f}]')
PY
```

Corrido por el orquestador: **reproduce exactamente** la tabla de arriba.
