# Regla de aporte y dimensionamiento del riel de dinero

**Escrito:** 7-sep-2026. **Estado:** PROPUESTA, espera firma de Nicolás.
**Se apoya en:** `REGLAS_DE_CAPITAL.md` (cero deuda, capital enteramente
discrecional, el plazo de recuperación nunca es insumo del dimensionamiento) y
en el insumo del §40 de la misma fecha.

---

## 1. La afirmación que este documento no hace

Al 7-sep-2026 el riel de dinero **no tiene ninguna ventaja medida**. L1 quedó
refutada por su propia regla pre-registrada. La celda superviviente no pasa la
corrección por multiplicidad de su familia de 30 contrastes (p de Holm 0,1740)
ni la ablación anual. La cuenta en papel está retirada por cuatro fugas
temporales demostradas. El riel tiene cero filas selladas prospectivas.

Por lo tanto **no se puede justificar ningún nivel de fricción por su
retorno esperado**, porque no hay retorno esperado medido contra el cual
compararlo. Cualquier frase de la forma "2% es aceptable porque la señal
rinde X" sería inventada. Este documento no la contiene.

## 2. Qué compra el presupuesto, entonces

La sección 10 del traspaso de la corrida 10 declara que nada del riel de
dinero es prospectivo, que todas sus cifras salen de mirar ocho años de una
vez, y que **la única defensa contra la fuga por el analista es el sellado en
vivo, y este riel no tiene ninguno**.

Eso es lo único que el presupuesto puede comprar hoy y que más cómputo no
puede fabricar: **filas selladas prospectivas en el riel de dinero**.

Bajo esa lectura, la regla de dimensionamiento no se deriva del retorno. Se
deriva de una condición mucho más débil y verificable: **que la fricción no
domine la magnitud que se intenta medir**.

## 3. Escalonamiento, con lo que desbloquea cada etapa

Ninguna etapa se salta. Cada una tiene una condición de salida escrita.

**E0. Sellado prospectivo de tamaño cero.** La máquina emite una decisión del
riel de dinero antes de la apertura del mercado objetivo y la sella, con
tamaño nominal cero. Cuesta cero pesos y cero cuenta. Condición de salida: N
filas selladas prospectivas acumuladas, con N fijado antes de empezar.

**E1. Cuenta de IBKR creada y no fondeada.** Da acceso a la cuenta de práctica
con API y datos retrasados. Cuesta cero. Condición de salida: la máquina envía
una orden y lee su propia ejecución en el mismo ciclo, sin intervención, y el
registro leído coincide con el reporte oficial de la cuenta de práctica.

**Advertencia que hay que resolver en E1:** las cuentas de práctica de IBKR
arrancan con USD 1.000.000 de capital simulado. A ese tamaño la comisión de
0,35 por orden es invisible y la cuenta **no reproduce el régimen de fricción
de este proyecto**. El capital se puede reiniciar desde el Client Portal
hasta cinco veces el valor de la cuenta de producción. Si no se puede bajar a
la escala real, E1 sirve para validar el cableado y **no** para medir
fricción, y eso queda declarado.

**E2. Dinero real, tamaño mínimo.** Sólo después de E0 y E1, y sólo con una
vara pre-registrada escrita antes. Condición de entrada, no de salida.

## 4. El presupuesto

Rango disponible declarado por Nicolás: 100 a 500 dólares, enteramente
discrecional, sin deuda, sin plazo de recuperación como insumo.

La decisión abierta es **el piso por posición**, y tiene dos opciones con
consecuencias distintas. Ninguna es recomendada acá.

| | (a) Acciones enteras | (b) Fraccionarias |
|---|---|---|
| Universo alcanzable | 7 de 36 con piso de 100 dólares; `SMH` no cabe en 500 | los 36, incluido `SMH` |
| Fricción ida y vuelta | 0,70% a 100 dólares; 0,28% a 250; 0,14% a 500 | 2,00% a cualquier tamaño |
| Número de posiciones con 500 | 2 de 250, o 5 de 100 | libre |
| Qué se pierde | el benchmark del propio proyecto queda fuera del riel de dinero | la fricción no se diluye nunca y es casi ocho veces mayor a 250 dólares |

**El hecho incómodo de la opción (a):** `SMH` es el benchmark declarado del
proyecto y no cabe. Un riel de dinero que no puede tomar posición en su propio
benchmark no puede compararse contra él con instrumentos propios.

**El hecho incómodo de la opción (b):** 2% de ida y vuelta sobre un horizonte
de semanas es una vara que la señal tiene que superar antes de que exista
cualquier resultado, y hoy no hay medición de que lo haga.

Cifras de fricción leídas del insumo del §40 del 7-sep-2026. Sin n ni
intervalo por ser tarifas. El componente de tarifas de bolsa queda sin
cuantificar.

## 5. Regla de aporte

Propuesta, para firma:

1. **Aporte único al iniciar E2.** No hay aportes periódicos ni promediado.
   Un aporte periódico convierte cualquier medición de retorno en una
   medición de aporte, y el riel de dinero existe para medir, no para
   acumular.
2. **Ningún aporte adicional mientras haya una vara pre-registrada abierta
   sin resolver.** Agregar capital en medio de un experimento cambia el
   denominador y el tamaño de posición a la vez.
3. **Ningún aporte se justifica por una pérdida.** El plazo de recuperación
   no es insumo, por `REGLAS_DE_CAPITAL.md`, y reponer para recuperar es
   exactamente eso disfrazado.
4. **El monto se fija antes de conocer el resultado de E0 y E1**, y se
   escribe en este documento con fecha. Fijarlo después es dimensionar
   mirando resultados.
5. **Todo el capital del riel es discrecional y se declara perdible en su
   totalidad.** Si el monto elegido no cumple esa condición, el monto está
   mal, no la regla.

## 5-bis. Lo firmado el 8-sep-2026 (acta §84.4) y aplicado en la corrida 12 (9-sep-2026)

- **Piso por posición: acciones ENTERAS** (§84.4.6, ítem §47 de `espera_firma.md`). `SMH`, el
  benchmark declarado, no cabe con el piso a ningún presupuesto del rango: el riel se compara
  contra él como línea base **sin poder tomar posición**, y el README y la vista lo dicen.
  Las fraccionarias se descartaron por su 2 % de ida y vuelta a cualquier tamaño.
- **N = 40 sesiones selladas prospectivas cierran E0** (§84.4.7). Fijado ANTES de la primera
  fila (la primera se selló en la corrida 12, madrugada del 9-sep-2026); no se mueve. Cuentan
  sólo las sesiones con `cuenta_para_N = 1` en `dinero/sello_dinero.db`: fila `pendiente`
  (available_at < timestamp_utc < apertura objetivo, por calendario) de un día con sesión y con
  el insumo en la sesión inmediatamente anterior a la objetivo. **Una fila sellada en día sin
  sesión se sella igual con su marca (`dia_sin_sesion`) y NO cuenta para N**; tampoco cuenta una
  `no_verificable_timing` ni una con insumo desactualizado (regla escrita el 9-sep-2026, pre-mortem
  13 de la corrida 12).
- **El monto de E2 NO se fija** en la corrida 12 (§84.4.7). Nota que hay que decir igual: la
  regla 5.4 dice que el monto se fija antes de conocer el resultado de E0; con la primera fila
  sellada, la ventana «sin mirar resultados» se cerró. Está en `espera_firma.md`.
- **Qué señal sella E0 (declarado, no decidido):** la sonda sin información de la cuenta en papel,
  por el mismo camino de piezas puras que pasó el gate (`dinero/sello_dinero.py`). Las filas prueban
  la MAQUINARIA del sellado prospectivo; el contador lo dice. Si cambia la señal (L1 refutada,
  otra, ninguna), es decisión de Nicolás (`espera_firma.md`, corrida 12) y reinicia el contador.

## 6. Lo que este documento deja abierto para tu firma

- ~~El piso por posición: opción (a) o (b) de la sección 4.~~ **Firmado el 8-sep-2026: (a), enteras** (§5-bis).
- El monto del aporte único de E2, dentro del rango de 100 a 500 (sigue abierto; ver §5-bis).
- ~~N, el número de filas selladas prospectivas que cierra E0.~~ **Firmado el 8-sep-2026: N = 40** (§5-bis).
- ~~Si `SMH` entra al riel de dinero por fraccionarias o si el riel se compara
  contra él sin poder tomarlo.~~ **Firmado el 8-sep-2026: se compara sin poder tomarlo** (§5-bis).
- **Nuevo (9-sep-2026):** qué señal sella E0 en adelante y si las filas de la sonda cuentan para N.

## 7. Nota que no es financiera y hay que decir igual

Este documento es aritmética de tarifas y disciplina de medición. No es
asesoría de inversión, no evalúa si operar es buena idea, y no afirma que
exista una oportunidad. Al día de hoy el proyecto no tiene evidencia de que
la tenga, y lo publica con la misma firmeza con que publicaría lo contrario.
