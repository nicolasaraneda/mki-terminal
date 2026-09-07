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
3. **La diferencia de retorno semanal medio debe tener un intervalo del 95 %
   —bootstrap circular de bloques sobre semanas, semilla declarada— que
   EXCLUYA el cero, y ser positiva.**
4. **Una sola mirada.** No se evalúa a las 26 semanas «para ver cómo va». Si
   se mira antes, el período se reinicia.

### 2.1 Qué número es eso, dicho como número

La dispersión medida de la diferencia semanal, sobre las 156 semanas de la
cuenta en papel de esta corrida (juego conservador contra `SMH`), es
**σ = 2.54 pp por semana**. Con esa dispersión, α = 0.05 y potencia 0.80, el
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
   `GEMELO/DISEÑO.md`, que hoy descalifica al propio campeón—, y (c) el
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
- Evaluar los tres juegos y reportar el mejor. La §2.2 existe exactamente
  para impedir eso, y la medición del 21 % de falsos positivos es la prueba
  de por qué.
- Convertir la magnitud en la métrica primaria si la dirección falla, o al
  revés, después de ver cuál de las dos salió mejor.
- Agregar una cuarta especificación a la señal larga sin sumarla al registro
  de intentos (`dinero/registro_intentos.py`).

Una enmienda legítima es posible y ya hay precedente en el proyecto: se
escribe con fecha posterior, dice qué cambia y por qué, **y no borra lo que
decía antes**.
