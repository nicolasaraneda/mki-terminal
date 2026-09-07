# Insumo del §40: el arancel real del corredor (IBKR), verificado

**Escrito:** 7-sep-2026. **Estado:** PROPUESTA, espera firma de Nicolás.
**Cierra el hueco declarado en la sección 10 del traspaso de la corrida 10:**
"el supuesto de costos no está contrastado contra ningún tarifario real".

**Fuente única y oficial**, consultada el 7-sep-2026:
`https://www.interactivebrokers.com/en/pricing/commissions-stocks.php`
Tabla "United States", estructura IBKR Pro.

**Sobre las cifras de este documento:** son tarifas publicadas, no
estimaciones. No llevan n ni intervalo porque no hay muestreo. Lo que sí es
variable y queda sin cuantificar está declarado en la sección 5.

---

## 1. La tabla, como está publicada

Acciones y ETF de Estados Unidos, volumen mensual menor o igual a 300.000
acciones:

| | IBKR Pro Tiered | IBKR Pro Fixed | IBKR Lite |
|---|---|---|---|
| Por acción | USD 0,0035 | USD 0,005 | USD 0,002 |
| Mínimo por orden | USD 0,35 | USD 1,00 | USD 0,003 |
| Máximo por orden | 1% del valor operado | 1% del valor operado | USD 0,00 |
| Elegibilidad | Todos | Todos | Sólo residentes de EE.UU. |
| Tarifas de terceros | Regulatorias, de bolsa, de compensación, de traspaso | Regulatorias | Regulatorias |

**IBKR Lite queda descartado por elegibilidad**, no por precio. La estructura
aplicable desde Chile es Pro, y dentro de Pro, Tiered.

## 2. Fraccionarias

De la nota 11 de la misma página: las operaciones fraccionarias están sujetas
a las mismas tarifas que las de acciones enteras, con comisión mínima de USD
0,01, y se cobra **el mayor entre 1% del valor operado y USD 0,01**.

Ejemplos que la propia página da: comprar 50% de una acción de USD 10,00
(valor operado USD 5,00) cuesta USD 0,05; comprar 5% de una acción de USD
15,00 (valor operado USD 0,75) cuesta USD 0,01.

## 3. Contradicción de la fuente, declarada

La fila de la tabla de Estados Unidos dice **máximo por orden 1% del valor
operado**. Las viñetas debajo de la misma tabla, en el mismo documento, dicen
que **las comisiones Tiered se topan en 0,5% del valor operado**.

Los dos números están en la misma página oficial y no se pueden conciliar
leyéndola. La tabla de Canadá, en cambio, dice 0,5% de forma consistente en su
propia fila, lo que sugiere que la viñeta puede estar arrastrada de otra
región, pero eso es conjetura y no se afirma.

**Supuesto adoptado para el §40: 1%**, por ser el número de la fila
correspondiente a Estados Unidos y por ser el conservador. Se registra como
discrepancia de la fuente, no como incertidumbre nuestra.

## 4. Restricción de arquitectura, no de precio

De la misma página: **las órdenes dirigidas por API no pueden usar la
estructura Tiered**; las órdenes por API con SmartRouting sí pueden usar
Tiered o Fixed.

Consecuencia directa para el bot: si el ruteo es dirigido a una bolsa
específica, la cuenta cae a Fixed, cuyo mínimo por orden es USD 1,00 en vez
de USD 0,35. A los tamaños de este proyecto eso casi triplica el piso.

**El ruteo del riel de dinero tiene que ser SmartRouting.** Esto es una
restricción de diseño y va al pre-registro, no a una nota al pie.

## 5. Tarifas de terceros, y lo que queda sin cuantificar

De la misma página, para Estados Unidos:

- SEC Transaction Fee: USD 0,0000206 por el valor agregado de las ventas.
- FINRA Trading Activity Fee: USD 0,000195 por cantidad vendida, máximo USD 9,79 por operación.
- FINRA Consolidated Audit Trail: USD 0,000003 por cantidad.
- Compensación NSCC y DTC: USD 0,00020 por acción, con máximo de 0,5% del valor operado.
- Traspaso: comisiones por 0,000175 (NYSE) y comisiones por 0,000565 (FINRA).
- **Tarifas de bolsa: varían por venue.** La página las publica en una lista
  de más de veinte enlaces por bolsa.

**Lo que no está cuantificado:** el componente de tarifa de bolsa, porque
depende de dónde ejecutó cada orden y eso no se conoce antes de ejecutar. A
los tamaños de este proyecto los otros componentes suman centavos. La cifra
de fricción de la sección 6 es correcta a primer orden y no es exacta.

## 6. La aritmética que decide el dimensionamiento

**Observación que manda:** el mínimo de USD 0,35 por orden domina hasta las
100 acciones, porque 0,0035 por 100 recién llega a 0,35. Todas las órdenes de
este proyecto van a estar muy por debajo de 100 acciones. Entonces la
comisión de acciones enteras es **0,35 por lado, plana**, sin importar el
precio de la acción ni la cantidad.

| Tamaño de la posición | Ida y vuelta, enteras | % | Ida y vuelta, fraccionarias | % |
|---|---|---|---|---|
| USD 100 | USD 0,70 | 0,70% | USD 2,00 | 2,00% |
| USD 150 | USD 0,70 | 0,47% | USD 3,00 | 2,00% |
| USD 250 | USD 0,70 | 0,28% | USD 5,00 | 2,00% |
| USD 500 | USD 0,70 | 0,14% | USD 10,00 | 2,00% |

Dos consecuencias:

1. La fricción de acciones enteras es un peaje fijo que se diluye con el
   tamaño. La de fraccionarias es proporcional y **no se diluye nunca**: 2%
   de ida y vuelta a cualquier tamaño.
2. **El cruce está en USD 35 por orden**, donde 1% iguala a 0,35. Por encima
   de 35 dólares por orden, las acciones enteras siempre cuestan menos. Por
   debajo, las fraccionarias.

## 7. Qué corrige esto del bloque 4 de la corrida 10

La cifra titular del bloque 4 después de quitar la fuga era que el juego
medio pasaba de 27% a 57% del capital en comisiones. Esa cifra está retirada
junto con la cuenta en papel y no se puede citar.

Cuando la cuenta se reconstruya, su parámetro de costo tiene que ser el de
este documento y no un supuesto. Y hay que declarar cuál de las dos columnas
de la sección 6 aplica, porque cambia el costo por un factor de casi ocho al
tamaño de 250 dólares.

**Nota de lectura sobre el 57%:** una fricción de 0,70 dólares por ida y
vuelta sobre 100 dólares consume 57% del capital recién a las 81 idas y
vueltas. Si la cuenta reconstruida vuelve a producir una cifra de ese orden,
el sospechoso principal es el número de operaciones del diseño y no el
arancel. El horizonte declarado del riel de dinero es de semanas.
