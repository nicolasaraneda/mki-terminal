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
