# Pre-registro del riel de dinero

**Congelado el 7-sep-2026 (corrida 10), ANTES de mirar ningún resultado del
bloque 6.** Lo que sigue fija, por adelantado, qué autoriza pasar de papel a
plata real y qué cierra la pista. Los criterios **no se editan para que los
datos entren**: si un resultado los contradice, gana el resultado y la
corrección se documenta aparte, con fecha posterior. Es la misma regla que
gobierna `GEMELO/DISEÑO.md`.

## 1. La hipótesis

**Un movimiento en un eslabón de la cadena de semiconductores anticipa el
movimiento de otro eslabón aguas abajo, con un retardo medible del orden de
semanas.**

La razón económica por la que eso podría ocurrir —y una hipótesis sin razón
económica es minería de datos con buena presentación— es que la cadena tiene
un orden físico de causalidad: quien vende equipo de litografía cobra antes
de que la fábrica produzca la oblea, la fábrica cobra antes de que el chip se
empaquete, y el empaquetado cobra antes de que el centro de datos encienda el
servidor. Si el mercado incorpora esa secuencia con retardo —porque el dato
de pedidos de equipo se publica antes que el de ingresos de la fundición—, el
retorno del eslabón de arriba contiene información sobre el del de abajo.

**La hipótesis contraria, que es la que hay que vencer:** el sector se mueve
como un bloque, todo lo que hay es beta común, y cualquier «anticipación»
observada es la misma noticia llegando a dos precios al mismo tiempo.

## 2. Qué autoriza pasar de papel a plata real

Cuatro condiciones, **todas**, evaluadas UNA sola vez al final del período:

1. **Período mínimo: 52 semanas** de cuenta en papel corriendo hacia
   adelante, con la señal congelada al empezar y sin tocarla en el medio.
2. **La comparación es UNA y está declarada acá:** el juego que rija por
   defecto contra la línea base `SMH` (aporte fijo semanal). No se evalúan
   los tres juegos contra los dos ETF y se elige el que dio: eso son doce
   comparaciones, y la propia cuenta en papel de esta corrida midió que un
   diseño así produce un intervalo que excluye el cero en **5 de 24
   comparaciones (21 %) con una señal que no tiene ninguna información**.
   **[Cifra RETIRADA y conteo corregido — errata §6 A y §6 B, 7-sep-2026.]**
3. **La diferencia de retorno semanal medio debe tener un intervalo del 95 %
   —bootstrap circular de bloques sobre semanas, semilla declarada— que
   EXCLUYA el cero, y ser positiva.**
4. **Una sola mirada.** No se evalúa a las 26 semanas «para ver cómo va». Si
   se mira antes, el período se reinicia.

### 2.1 Qué número es eso, dicho como número

La dispersión medida de la diferencia semanal, sobre las 156 semanas de la
cuenta en papel de esta corrida (juego conservador contra `SMH`), es
**σ = 2.54 pp por semana** *(errata 8-sep-2026, §7 C: cifra RETIRADA por fuga; la v2 mide 2,336)*. Con esa dispersión, α = 0.05 y potencia 0.80, el
tamaño de efecto detectable a 52 semanas es:

| Ventaja verdadera | Semanas necesarias | Años |
|---|---:|---:|
| +0.10 pp/semana | 5054 | 97 |
| +0.25 pp/semana | 809 | 16 |
| +0.50 pp/semana | 203 | 3.9 |
| **+1.00 pp/semana** | **51** | **1.0** |

**Consecuencia, y hay que leerla completa: el criterio de 52 semanas sólo lo
pasa una ventaja de aproximadamente +1 punto porcentual por semana.** Eso son
del orden de +50 pp anuales sobre la línea base. Una ventaja de ese tamaño no
es plausible en un mercado líquido con datos públicos.

Por eso el pre-registro agrega una cláusula que normalmente no haría falta:

5. **Si el criterio se cumple, la primera reacción NO es poner plata.** Una
   ventaja lo bastante grande como para ser detectable en un año es, en este
   contexto, evidencia más fuerte de un error que de una habilidad. Antes de
   cualquier dinero real, un resultado positivo debe sobrevivir: (a) la
   auditoría de fuga temporal (`auditor-lookahead`), (b) una ablación de la
   ventana que sostiene la ventaja —del mismo tipo que R2 en
   `GEMELO/DISEÑO.md`, que hoy el propio campeón no pasa (ver §6 H)—, y (c) el
   dictamen de `estadistico-adversario`. Sólo después se discute el monto.

## 3. Qué mata la pista

El riel de dinero **se cierra** —no se sigue ajustando— si ocurre cualquiera:

- **M1.** Tras 104 semanas de papel, el intervalo de la diferencia sigue
  conteniendo el cero **y** el punto estimado es negativo. Dos años sin
  distinguirse de no decidir nada, yendo para abajo, es un resultado.
- **M2.** El costo de operar vuelve la pregunta vacía: si la comisión
  acumulada del juego por defecto supera **el 25 % del capital aportado** en
  el período, la estrategia no puede ganar aunque la señal exista. Esta
  corrida ya midió que los tres juegos gastan entre 14 % y 43 % en
  comisiones con 500 dólares de capital: **M2 está a punto de dispararse
  antes de empezar**, y ésa es información sobre el tamaño de la cuenta, no
  sobre la señal.
- **M3.** Cualquier fuga temporal detectada en la señal larga. Sin apelación
  y sin excepción, igual que R3.
- **M4.** Si la señal larga del bloque 6 no supera ninguna de sus dos varas
  y una revisión honesta concluye que los datos disponibles no contienen
  señal a ese horizonte, el riel no tiene sobre qué operar. Se cierra o se
  reformula desde cero con hipótesis nueva y pre-registro nuevo.

## 4. El primer monto real

**Los primeros 100 a 500 dólares son costo de aprendizaje operativo, no una
apuesta con retorno esperado positivo demostrado.** Lo que se compra con ese
dinero es saber cómo se abre una cuenta desde Chile, cuánto tarda una
transferencia, qué comisión se paga de verdad contra la supuesta, cuánto se
desliza el precio de un ADR de mostrador y qué se retiene de un dividendo:
cosas que en papel no se aprenden y que el modelo de costo de esta corrida
sólo supone. **Se espera perder parte de ese dinero, y eso no refuta ni
confirma nada sobre la señal.**

Ese gasto NO está condicionado a los criterios de la §2: se puede hacer
antes, porque no es una operación con tesis. Lo que sí está condicionado es
**operar según la señal**, y **cualquier monto mayor**.

## 5. Qué haría ilegítima una enmienda a este documento

Este pre-registro queda inválido, y con él cualquier conclusión que se apoye
en él, si se toca de alguna de estas formas:

- Bajar el período de 52 semanas, ampliar α, o cambiar el bootstrap por otro
  método **después** de ver una diferencia que no alcanzó.
- Cambiar la línea base declarada (`SMH`) por otra que la estrategia sí
  supere. Si `SMH` deja de ser el benchmark del proyecto, el cambio se
  documenta **antes** de la evaluación y con su razón.
- Evaluar los tres juegos y reportar el mejor. La §2 existe exactamente
  **[cifra RETIRADA — errata §6 A, 7-sep-2026; y la §2.2 no existe, ver §6 D]**
  para impedir eso, y la medición del 21 % de falsos positivos es la prueba
  de por qué.
- Convertir la magnitud en la métrica primaria si la dirección falla, o al
  revés, después de ver cuál de las dos salió mejor.
- Agregar una cuarta especificación a la señal larga sin sumarla al registro
  de intentos (`dinero/registro_intentos.py`).

Una enmienda legítima es posible y ya hay precedente en el proyecto: se
escribe con fecha posterior, dice qué cambia y por qué, **y no borra lo que
decía antes**.

---

## 6. Errata fechada — 7-sep-2026, sesión de cierre de la corrida 10

Este documento es un pre-registro y **no se reescribe**: lo de abajo corrige,
con fecha y sin borrar, lo que quedó mal en los §2, §2.1, §3 y §5. Ninguna de
estas correcciones ablanda un criterio; **dos lo endurecen y una lo deja
explícitamente sin poder leerse**.

**A. La cifra del «21 % de falsos positivos» está RETIRADA.** La citan el §2
condición 2 y el §5. La medición decía: 5 de 24 comparaciones dan un intervalo
que excluye el cero con una señal sin información, y todas son falsos positivos
porque la respuesta verdadera es cero. Es incorrecto por tres razones que
mostró el `estadistico-adversario`: la nula no es cero (el arrastre de comisión
garantiza una diferencia verdadera negativa); cuatro de los cinco marcados son
el resultado verdadero de fricción que la propia página celebra; y las 24 no
son 24 pruebas ni hay más que un sorteo. Queda 1 de 24, el α nominal.
**Y hay una segunda razón, independiente y peor:** la cuenta en papel de la que
salía esa cifra tiene **fuga temporal demostrada** (`dictamen_10/auditor_lookahead.md`,
F1 a F4), así que ninguna de sus cifras se puede citar. **La cláusula que ese
número justificaba —una comparación declarada, una sola mirada— es correcta por
otras razones y se mantiene**: lo que se cae es la razón, no la regla.

**B. «Doce comparaciones» son SEIS.** El §2 condición 2 dice que evaluar los
tres juegos contra los dos ETF «son doce comparaciones». Son **3 × 2 = 6**. Las
24 de la cuenta en papel salen de multiplicar además por los cuatro niveles de
deslizamiento del barrido. El argumento no depende del número; el número estaba
mal.

**C. La línea base descrita no es la implementada.** El §2 dice «línea base
`SMH` (aporte fijo semanal)». Lo implementado en
`contabilidad.calendario_aportes` es **100 USD semanales hasta agotar el techo
de 500, y después nada**: cinco aportes en 156 semanas, no un aporte semanal
perpetuo. El código lo documenta bien; este documento, que es el que gobierna,
no. **Rige lo implementado**, y cuando el riel corra hacia adelante 52 semanas
el flujo de aportes tiene que quedar declarado acá antes de empezar.

**D. Referencias colgantes.** Tres documentos citan un «§2.5» de este archivo
que **no existe** (`ESTADO.md`, el reporte de la señal larga y el encargo de la
corrida 10), y el §5 cita un «§2.2» que tampoco existe. Las secciones reales
son §1, §2, §2.1, §3, §4, §5 y esta §6. La cláusula que todos querían citar es
la del §2.1: **si el criterio se cumple, la primera reacción no es poner plata,
es sospechar un error**. Sigue vigente, y es de las mejores frases de este
documento.

**E. M2 compara un porcentaje de 156 semanas contra un umbral escrito para
52.** M2 dispara si la comisión acumulada supera el 25 % del capital aportado
«en el período», y el documento concluía que estaba «a punto de dispararse»
citando el 14 % a 43 % —cifra **RETIRADA**, ver §6 A—, que es de **156
semanas**. Medido sobre la peor ventana
móvil de 52 semanas, **ningún juego llega al 25 %** (10,1 %, 21,8 % y 14,8 %);
recién se dispara a 104 semanas y sólo para dos juegos. **M2 no se puede leer
como disparado ni como no disparado** hasta que se fije el período
explícitamente y se recompute sobre una cuenta sin fuga. Qué período rige es
decisión de Nicolás y está en `espera_firma.md`.

**F. M4 no cierra nada como está escrito.** M4 dispara si la señal larga «no
supera **ninguna** de sus dos varas». Con 30 contrastes correlacionados a
α = 0,05, esa es una barra que el ruido puro pasa la mayoría de las veces: una
cláusula que casi nunca dispara no es un criterio de rechazo. **Y hoy además no
se puede evaluar**, porque la segunda vara declarada en el pre-registro de la
señal larga —la línea base aburrida— **no se corrió**, y la cuenta en papel por
la que habría que pasarla está retirada. Reescribir M4 en términos de la
familia corregida por multiplicidad es decisión de Nicolás.

**G. La ablación tipo R2 que el §2.1 exige ya se corrió, y la señal larga no la
pasa.** Sacando 2024 del período de prueba, la única celda que ganaba sin
corregir pasa a **+0,226 pp [−0,011, +0,497]**, que contiene el cero. Se anota
acá porque este documento la exigía y quedaba pendiente.

**H. Sobre R2 en el riel de medición.** El §2.1 decía que la ablación R2 «hoy
descalifica al propio campeón». Dice más de lo que la cifra sostiene: bajo R2
la ventaja del campeón **no se distingue de cero en ninguna de las tres
convenciones de conteo**, con ningún p cerca de 0,05, y bajo la regla de
deduplicación firmada el 1-sep **no está recomputada**. «No pasa» es correcto;
«descalifica» y «la vuelve negativa», no.

---

## 7. Errata fechada, 8-sep-2026 (corrida 11, bloque 2), sobre M2 y la §2.1

Aditiva, sin borrar. La cuenta en papel se reconstruyó sin fuga (acta §82.4,
`dinero/resultados/cuenta_papel.md` v2, PROPUESTA hasta los dictámenes). Lo que
eso corrige de este documento:

**A. M2 no está «a punto de dispararse».** La banda «14 % a 43 %» del §3 y esa
frase son de la v1 RETIRADA. Con la v2, el juego por defecto (`conservador`,
5 pb) gasta en comisiones del orden del 12 % de lo aportado sobre **156
semanas** (un sorteo; la banda entre 20 semillas está en la página), la mitad
de la vara del 25 %. El juego `medio` sí la cruza, pero no es el que rige. La
reversión se documenta acá con fecha, no se absorbe en silencio.

**B. M2 sigue sin poder leerse hasta cuatro precisiones**, y son de Nicolás
(`espera_firma.md` §43): (i) la base temporal, porque 12 % es sobre 156
semanas y la §2 declara 52 (M1, 104); (ii) si el deslizamiento cuenta como
«comisión»; (iii) el intervalo por K semillas, porque el número de órdenes es
función del sorteo; (iv) la cifra sobre 52 semanas hacia adelante, que es la
única que el criterio nombra.

**C. La σ de la §2.1 (2,54 pp/semana) es cifra RETIRADA.** La v2 mide
σ = 2,336 pp/semana con intervalo [1,995, 2,669] de bootstrap de bloques de
una desviación **cuya cobertura medida es 0,850, o sea NO es un 95 %**
(`GEMELO/resultados/instrumento_dinero.md`), y el
instrumento puesto a prueba (discrimina y NO está calibrado a α = 0,05; «validado» retirado el 9-sep-2026, re-dictamen D14) da un MDE80 a 52 semanas del orden de 1 pp/semana con
la σ ancla de 2,70: la conclusión cualitativa de la §2.1 (el criterio de 52
semanas sólo lo pasa una ventaja implausible) **se mantiene**; la tabla de
semanas necesarias se recomputa con el simulador y no acá.

**D. El arancel.** La v2 usa el arancel publicado del insumo §40 (columna de
enteras), que espera firma. Los umbrales derivados de `reglas.json` cambiaron
con él por su regla (`espera_firma.md` §48).


## 8. Enmienda fechada, 9-sep-2026 (corrida 12, bloque 8): M2 no tiene unidad, y la firma §43 es NO APLICABLE

**Qué pasó.** El acta §84.4.5 firmó «el período de M2 es el horizonte pre-registrado de la vara»
(52 semanas). El `estadistico-adversario` (`GEMELO/resultados/dictamen_12/adversario_43_periodo_m2.md`)
la declaró **NO APLICABLE**: el §2 punto 1 escribe «período **mínimo**: 52 semanas de cuenta en papel
corriendo **hacia adelante**», que es un piso prospectivo sobre la DURACIÓN de la cuenta y no una ventana
de acumulación de M2; el «horizonte pre-registrado de la vara» que la firma invoca no existe escrito, y se
dispara la cláusula de escape que la propia §84.4.5 dejó («vuelve a la cola con la pregunta exacta»).

**El defecto de fondo, medido.** M2 dice «la comisión acumulada supera el 25 % del capital aportado en
el período» y el 25 % **no tiene unidad de período**. El numerador (comisión) es un flujo que crece con h;
el denominador (500 USD, cinco aportes que terminan en la semana 5) NO crece. El cociente es proporcional
a h: elegir 52 semanas en vez de 156 divide el numerador por ~3 con el umbral quieto, y el umbral se
escribió mirando una banda de 156 semanas de la cuenta v1 (RETIRADA), o sea ≈ 8,3 %/año implícitos.
Recomputado sobre la v2 sin fuga (`GEMELO/resultados/m2_periodo.md`, 20 semillas, una sola trayectoria de
mercado, deslizamiento excluido): el juego por defecto (`conservador`, `reglas.json` SIN FIRMA) gasta
**3,9 %/año [3,56, 4,58] del capital aportado** en comisiones, estable a través de 52/104/156 semanas
(4,3 y 4,1 desde 104 y 156); no cruza el 25 % acumulado en ningún horizonte (techo 13,1 % a 156). El
`medio` cruza a 156 semanas (17 de 20 semillas), pero M2 no lo nombra.

**Dos hallazgos más, del dictamen.** (i) En 5 de 20 semillas la cuenta conservadora se **congela** (sin
caja para una acción entera desde marzo/abril de 2025): acumula poca comisión por quiebra operativa, no
por baratura, y M2 la puntúa bajo por la razón equivocada. (ii) M2 excluye el deslizamiento por
decisión del módulo, no del pre-registro (§7 B (ii) sigue sin firma); con 5 pb el conservador pasa de
12,5 % a 13,9 % de vida entera.

**Qué queda en pie y qué no.** M2 **no se mata: se re-registra hacia adelante**, y hasta entonces no se
puede leer como disparada ni como no disparada (lo que ya decía el §6 E, ahora por la razón correcta: el
umbral no tiene unidad). La reescritura que el adversario propone y que espera firma (§43): M2 en
**%/año** (tasa anualizada = comisión acumulada × 52/h sobre el capital aportado), con el umbral
**re-declarado en %/año ANTES** de que corra la cuenta prospectiva y con la ventana de esa cuenta escrita
antes de su primera fila; más la **condición de supervivencia operativa**: una cuenta que no puede tomar
una posición entera está muerta y eso dispara M2 aunque su ratio sea bajo (E13). La unidad y el umbral
son de Nicolás; nada de esto se firma acá.

**Grado de libertad declarado (E12):** se computaron 12 lecturas (3 juegos × 4 períodos) y la firma
eligió 1 con los resultados a la vista. Va al registro de «lecturas de criterio» (contador distinto del
DSR; dónde vive es decisión pendiente).

---

## 9. Enmienda fechada, 28-sep-2026 (corrida 14, bloque 4.4): M2 en %/año, umbral 8,3 %/año — PROPUESTA, sin firmar

**Qué la autoriza y qué no.** El acta §88 del 19-sep-2026 firmó cuatro cosas sobre M2: §88.7 la
unidad, §88.11 el umbral, §88.12 el deslizamiento, §88.13 la ventana y las cuentas congeladas. Esta
sección **redacta** esas cuatro firmas en el lenguaje del pre-registro y **no firma ninguna**: es
PROPUESTA hasta que Nicolás la firme por acta. Es la respuesta a la cláusula de escape que la §8 dejó
abierta el 9-sep («vuelve a la cola con la pregunta exacta»). Como manda la §5, se escribe con fecha
posterior, dice qué cambia y por qué, y **no borra nada de lo anterior**.

**Nota de redacción, 28-sep, misma corrida.** La primera versión de esta §9 afirmaba que el umbral
«no endurece ni ablanda el criterio». El `estadistico-adversario` la midió y **es falsa**: ver (b).
La frase se corrigió antes de que Nicolás la leyera y antes de cualquier commit, junto con seis
lugares donde esta sección le ponía en la boca del acta cosas que el acta no dice. Todo eso queda
dicho abajo en su sitio; nada del §8 ni de lo anterior se tocó.

**Qué cambia, punto por punto.**

**(a) Unidad — §88.7, opción (c).** M2 se lee como **tasa anualizada en %/año** y no como porcentaje
acumulado sin período:

> **M2 = (comisión acumulada desde el primer aporte) × (52 / h) ÷ (capital aportado)**,
> con *h* en semanas transcurridas desde el primer aporte.

Razón, medida en la §8: el cociente acumulado es proporcional a *h* —el numerador es un flujo que
crece, el denominador son 500 USD que dejan de crecer en la semana 5—, así que un umbral sin unidad
de período no es un umbral, es una función del horizonte que se elija después. La tasa anualizada es
la única lectura invariante al período que la §8 encontró (conservador: 3,9 · 4,3 · 4,1 %/año leído
desde 52, 104 y 156 semanas), y el adversario verificó que esa estabilidad **no** es un artefacto del
congelamiento de semillas: la mediana se mueve del 4,12 (con todas) al 4,17 (sólo vivas) a h = 156.

**Lo que el acta NO firmó y esta sección declara como elección, no como firma:** §88.7 firmó «tasa
anualizada (%/año)». El **factor lineal `× 52/h`** (anualización aritmética) es una convención del
módulo (`GEMELO/m2_periodo.py`, `"convencion_anualizacion": "suma aritmética"`), no una línea del
acta. Es defendible para un ratio de costo —la alternativa geométrica no tiene sentido acá— pero es
una elección y queda declarada como tal, porque es la que produce el sesgo del párrafo siguiente.

**Sesgo declarado del factor lineal: premia a la cuenta que se murió.** Medido por el adversario
sobre las semillas del juego `medio` que se congelan, leídas a h = 52 / 104 / 156: 9,42 → 7,55 → 5,04;
9,40 → 7,03 → 4,69; 9,43 → 7,65 → 5,10. A h = 156, **17 de 17 semillas vivas cruzan el umbral y 0 de 3
congeladas lo cruzan**: el factor lineal convierte una cuenta que M2 habría matado por caro en una
cuenta que M2 declara barata, por haber dejado de operar. Es E13 del dictamen 12, ahora medido contra
este umbral. Y hay un límite estructural que hay que decir: **a h = 52 no hay ninguna semilla
congelada**, así que la única lectura que (d) autoriza es exactamente la que no puede ver este sesgo;
aparece a 104 y 156, cuando ya no hay nada que decidir.

**(b) Umbral — §88.11: 8,3 %/año.** Sale de 25/3: el 25 % original repartido en 156 semanas. La razón
de Nicolás, citada del acta: «pq se deriva de mi numero original».

**Y es un criterio más duro, no el mismo.** Esto es lo que la primera versión de esta sección decía
mal. El umbral nuevo es **156/h veces más exigente** que el 25 % acumulado en todo horizonte menor a
156 semanas: **3× a las 52 semanas**, que es justamente la primera lectura que (d) autoriza; 1,5× a
las 104; y 1× a las 156, donde coincide por álgebra (8,333 × 3 = 25). Medido sobre la cuenta v2
simulada, la misma cuenta y el mismo *h*, el umbral viejo contra el nuevo:

| juego | h = 52 | h = 104 | h = 156 |
|---|---|---|---|
| conservador | 0/20 → 0/20 | 0/20 → 0/20 | 0/20 → 0/20 |
| agresivo | 0/20 → 0/20 | 0/20 → 0/20 | 0/20 → 0/20 |
| medio | **0/20 → 19/20** | 0/20 → 17/20 | 17/20 → 17/20 |

A h = 52 el estadístico es idéntico bajo las dos lecturas (52/52 = 1), así que la comparación no
depende de ninguna convención de anualización. **El juego `medio` pasa de no disparar nunca a disparar
en 19 de 20 semillas.** El umbral se elige más duro a propósito y queda declarado.

**Y hay que decir de dónde NO sale ese 19/20:** `GEMELO/m2_periodo.py` sigue con
`UMBRAL_M2_PCT = 25.0` y cuenta contra ese 25 %, así que el conteo contra 8,3333 %/año **se computó
fuera del módulo** que hoy es dueño del umbral. Es la misma vara que el §61 le aplica a las 24 filas del
28-sep —«no reproducible por un tercero»— y corresponde aplicársela también acá: **mientras el módulo no
lleve el umbral firmado, el 19/20 no es reproducible corriendo `m2_periodo.py`**. Cambiar el módulo sería
aplicar una enmienda que este mismo documento declara NO APLICABLE, y con el arancel del §40 sin firma
(§48), así que **no se cambió**: se declara.

**De las tres re-expresiones redondas del 25 %, la elegida es la única que mata algo:** 25/1
(25,0 %/año) y 25/2 (12,5 %/año) dan 0/20 en los tres juegos; 25/3 (8,333 %/año) da 19/20 en `medio`.
Con las 12 lecturas a la vista. Eso no lo hace ilegítimo —Nicolás puede querer un criterio 3× más
duro y lo firmó con las cifras delante— pero **es un grado de libertad con consecuencia, no un
re-expresado inerte.**

**Procedencia del 25 %, con su marca.** El 25 % se escribió dentro de la banda **«14 % a 43 %», cifra
RETIRADA por fuga temporal** (§6 A, §7 A, `dictamen_10/auditor_lookahead.md`), medida sobre 156
semanas. Este documento se contradice consigo mismo sobre a qué horizonte pertenecía el 25 % (la §6 E
dice «un umbral escrito para 52»; la §8 dice «mirando una banda de 156 semanas»), y ninguna de las
dos consta como decisión: **no se certifica ninguna**. Lo certificable es que 25/3 = 8,3333… es
aritmética correcta y que su procedencia es el horizonte de una cifra retirada.

**Precisión del número (hay que decirla porque M2 es un interruptor duro):** el umbral es
**25/3 = 8,3333…**, no 8,3 redondeado. Hoy no cambia ninguna lectura (no hay semilla en el intervalo
(8,3 · 8,3333)), pero un pre-registro tiene que decir el número exacto.

**(c) Deslizamiento — §88.12: no cuenta.** M2 se lee **sólo** de las comisiones que informa el
corredor. El deslizamiento se registra aparte y no entra en el numerador de M2. Esto cierra hacia
adelante lo que la §7 B (ii) dejó sin firma. **Advertencia: la serie separada de deslizamiento no
existe todavía**, y el acta no la nombra; que exista antes de la primera fila prospectiva es parte de
lo que falta (D7 abajo).

**(d) Ventana — §88.13.** El acumulado corre **desde el primer aporte** y se anualiza. La **primera
lectura válida es a las 52 semanas, y después sigue** (la cadencia posterior es de las definiciones
que faltan, D8). Antes de ese plazo M2 no se lee: no está disparada ni no-disparada.

**(e) Cuenta congelada — §88.13: estado aparte.** Una cuenta que se queda sin caja para comprar una
acción entera **no cuenta como M2 cumplida**: es un estado aparte **y se informa como tal**, que es la
letra del acta. Razón de Nicolás: «es la decision prudente». Nada más que eso se afirma acá: qué
consecuencia tiene ese estado es una de las definiciones que faltan (D3), y la primera versión de esta
sección agregaba «y no se promedia con las cuentas vivas», que el acta no dice y que **no tiene
referente en la cuenta prospectiva, donde hay UNA cuenta y ningún promedio**.

**Grado de libertad declarado (E12 y §88.11).** El umbral se fijó con **12 lecturas ya computadas a la
vista** (3 juegos × 4 períodos, `GEMELO/resultados/m2_periodo.md`, dictamen de la corrida 12): la firma
eligió una de doce con los resultados delante. Va al registro de «lecturas de criterio», contador
distinto del DSR, **cuyo domicilio sigue siendo decisión pendiente** (§88.14). El adversario agrega
tres lecturas más (las tres re-expresiones de (b)), que tampoco se pueden archivar mientras ese
contador no tenga sitio.

**El costo aceptado, dicho como número.** Por (d), M2 **no puede disparar durante el primer año**. Y
sobre las lecturas simuladas de la cuenta v2 sin fuga, con el umbral en 8,3333 %/año:

| juego | anualizada desde 52 semanas | mín–máx | ¿dispara? |
|---|---|---|---|
| conservador (por defecto) | 3,9 % [3,56 · 4,58] | [3,5 · 4,69] | **0 de 20 semillas** |
| agresivo | 6,4 % [5,77 · 7,78] | [5,66 · 7,83] | **0 de 20 semillas** |
| medio | 9,4 % [8,23 · 10,82] | [8,14 · 11,18] | **19 de 20 semillas**, Wilson 95 % [76,4 · 99,1] |

Cómo se lee esa banda, y es importante: son los percentiles 2,5 y 97,5 **entre 20 semillas del sorteo
sobre UNA sola trayectoria de mercado** — **no es un intervalo de cobertura nominal**, y no cubre la
variación de mercado. Con K = 20 el percentil 2,5 **no es estimable**: el 8,23 de `medio` es una
interpolación entre la semilla más baja (8,14) y la segunda (8,34), o sea que «el borde inferior de la
banda» **es una semilla**. Por eso la lectura honesta es el conteo con Wilson sobre semillas, y la
unidad de replicación es la semilla, no el mercado. La única semilla de `medio` que no cruza es la más
baja de las veinte.

**Y hay que decir por qué `agresivo` (6,4) gasta MENOS que `medio` (9,4), porque los nombres engañan.**
El costo por orden es casi el mismo en los tres juegos (≈ 0,30 · 0,30 · 0,24 USD por orden, de los
conteos de `dinero/resultados/cuenta_papel.md`), así que **M2 ≈ número de órdenes × ~0,3 USD ÷
capital**. `medio` gasta más porque hace más órdenes (443 contra 393), por ser más granular con 500
USD y acciones enteras. Consecuencia: **el umbral no mata al juego más arriesgado, mata al más
granular.** Y las holguras no son comparables: la peor semilla de `agresivo` está a +6,4 % del umbral
(7,83 contra 8,333) y la de `conservador` a +77,7 %; decir «no dispara» con la misma frase para los dos
aplana una diferencia de holgura de 12×.

El juego por defecto sigue siendo el conservador, `reglas.json` sigue **SIN FIRMA**, y **el arancel
del §40 que fija el numerador también sigue SIN FIRMA** (tarjeta §48). Todo esto es un «qué habría
pasado» sobre una cuenta simulada, no una lectura de la cuenta prospectiva, que no existe: la tabla se
cita para declarar el costo de la elección, no como resultado. Y nadie ha medido
`P(M2 dispara | tasa verdadera = 8,333 %/año)` para una cuenta leída a 52 semanas: `GEMELO/simulador/`
no tiene nada de M2 ni de comisiones, y con una sola trayectoria de mercado no se puede. **Ninguna
afirmación de la forma «M2 dispara cuando debe» está autorizada hasta que el simulador se extienda a
múltiples trayectorias.**

**Lo que esta enmienda NO define, y por lo que todavía no se puede aplicar.** Son **seis**, no cuatro:
las cuatro que esta sección ya declaraba (con el juego de opciones de la primera corregido) más dos
que el adversario encontró. Ninguna se rellena acá, y todas van a **completar la tarjeta §43**, que ya
lista los huecos sin opciones — **no se abren tarjetas nuevas**: el contador de lecturas de criterio ya
está en §88.14 y el arancel en §48.

1. **El denominador mientras los aportes no terminan.** La bifurcación real **no** es «aportado final
   contra aportado a la fecha de lectura»: bajo el calendario declarado (5 aportes que terminan en la
   semana 5) esos dos son **numéricamente idénticos** para todo h ≥ 5, y además «aportado final» no es
   computable en el momento de la lectura si los aportes siguen fluyendo. La bifurcación es
   **ponderado por tiempo o no**: con el calendario actual el factor es 1,0375 (`medio` pasa de 9,38 a
   9,73 %/año), y si el flujo prospectivo fuera sostenido 100 USD/semana durante 52 semanas el factor
   llega a **1,957 — casi 2×, más que toda la distancia entre `conservador` y `medio`**. Hay que
   declarar además que **las cifras que esta sección cita ya usan «aportado a la fecha de lectura»**
   (`GEMELO/m2_periodo.py:91`), y que la **§6 C** —declarar el flujo de aportes prospectivo antes de
   empezar— sigue sin declararse.
2. **Qué es exactamente «congelada»**, y es peor de lo que parecía. La cifra «5 de 20 congeladas» que
   la §8 cita **no mide el concepto que el acta firmó**: el código usa «26 semanas sin ningún
   movimiento» (`GEMELO/m2_periodo.py:96`), una proxy de inactividad con una constante que no aparece
   en ninguna especificación, mientras §88.13 define un **estado de caja** («sin caja para una acción
   entera»). E4 del dictamen 12 pedía **las dos** condiciones y sólo se implementó la primera; la caja
   se verificó a mano en **2 de las 5** semillas. Y `dinero/contabilidad.py:215` dice que la cuenta
   **no se detiene** por falta de caja: «si el aporte no alcanza para una acción entera, ACUMULA» —
   no existe estado terminal en el código.
3. **Si una cuenta congelada mata la pista o sólo sale del cómputo.** §88.13 firma una **tercera**
   cosa, ni disparada ni absuelta: «estado aparte, y se informa como tal». E13 del dictamen 12 pedía
   que **disparara** M2 («una cuenta que no puede tomar una posición entera está muerta»). La
   diferencia decide si el riel muere o se pausa, y es la pieza que debería tapar el sesgo de (a):
   sin ella, una cuenta matada por la fricción lee 5,0 %/año y sale «M2 no disparada».
4. **Dónde vive el contador de «lecturas de criterio»** (§88.14 y §8 lo dejan sin dueño). No necesita
   tarjeta nueva; necesita que §43 se complete con opciones.
5. **NUEVO Y URGENTE: qué es «el primer aporte».** Es el cero de *h* y la identidad de «capital
   aportado», y no está definido en ninguna parte. §88.10 registra la cuenta de IBKR **ya fondeada con
   5,00 USD** al 19-sep, con los 500 de E2 sin depositar. Bajo la letra de (a)+(d), en la ventana
   entre ese fondeo y E2: 1 orden al mínimo de 0,35 USD sobre 5,00 de capital da 7,0 %/año; **2
   órdenes dan 14,0 %/año y M2 DISPARA**; las mismas 5 órdenes sobre 500 USD dan 0,35 %/año. **Cien
   veces de diferencia según qué aporte cuente, y dos órdenes cierran el riel.** Además la §4 declara
   que los primeros 100-500 USD son «costo de aprendizaje operativo, no una apuesta» y **no** están
   condicionados a la §2: si sus comisiones entran al numerador, M2 mide el aprendizaje. Y toca la
   validez de esta misma enmienda: si *h* ya arrancó con el fondeo de 5,00 USD, la enmienda puede
   estar llegando tarde a su propio reloj. **Hay que definirlo antes de firmar.**
6. **NUEVO: la convención de anualización** (`× 52/h` lineal) no está firmada; ver el final de (a).

**Y cuatro huecos menores, de una línea cada uno.** (D7) **Dónde se sella la comisión del corredor y
qué pasa si falta:** `corredor/ibkr.py` lee `commissionReport` pero **no persiste nada**, y
`sellos_dinero` no tiene columna de comisión ni de ejecución, así que la serie que M2 leería **no
tiene sello** y una consulta viva a la API no es reproducible; `comision_usd` puede volver `None` sin
regla de dato faltante; el `commissionReport` de IBKR llega asíncrono y puede revisarse después, lo que
choca con la inmutabilidad de sellos; y **el alcance del numerador no coincide con el de la
calibración** — `reglas.json` declara que las tarifas de terceros (SEC, FINRA, compensación, venue)
NO están en el modelo con el que se calibró el 8,3, pero M2 se leerá de «lo que informa el corredor»,
y un numerador 10 % mayor lleva la peor semilla de `agresivo` de 7,83 a 8,61 y **la cruza**.
(D8) **La cadencia después de la semana 52, y si leer M2 cuenta como «mirada»:** un interruptor de un
solo lado leído repetidamente tiene problema de miradas múltiples, y la §2 punto 4 dice que «si se
mira antes, el período se reinicia»; falta también el orden de precedencia cuando la lectura de M2 y la
evaluación única de la §2 caen el mismo día. (D9) **Descongelamiento y *h* con el riel interrumpido:**
(e) no dice qué pasa si la cuenta se descongela, y *h* se mide en semanas de **calendario**, así que
una interrupción del riel (Gateway caído, cuenta en revisión) baja la tasa por dejar de operar igual
que el congelamiento, sin ser «sin caja para una acción entera». (D10) la precisión del umbral, ya
dicha en (b).

**Qué haría ilegítima esta enmienda.** Todo lo de la §5 sigue rigiendo sin cambios. Se agrega, para
esta enmienda en particular: mover el 8,3333 %/año **después** de ver la primera lectura de la cuenta
prospectiva, o cambiar la unidad otra vez para que un resultado que no alcanzó alcance. El umbral y la
unidad quedan fijos desde la firma de Nicolás y antes de la primera fila prospectiva; si esta enmienda
se firmara después de esa fila, deja de ser un pre-registro y hay que decirlo así. La corrección de la
frase de neutralidad **no** es una de esas formas: no ablanda ningún criterio ni mueve el umbral,
corrige una caracterización falsa del criterio, con fecha, como la propia §5 autoriza.
