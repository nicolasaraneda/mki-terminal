# Criterio de "cierre previo rancio" — DECLARADO ANTES DE CORRERLO

**Escrito el 2026-08-26, antes de calcular una sola fila.** Existe porque hay
un sesgo acechando: el campeón acertó 1 de 8 el 29-jul, así que **excluir esas
filas SUBE el 65.9% publicado**. Un criterio elegido después de ver el
resultado sería exactamente el sesgo que este proyecto existe para evitar.

## La definición

Una fila sellada tiene **cierre previo rancio** si el precio de referencia que
el verificador usó como cierre anterior difiere de la realidad según la
historia de hoy.

El verificador selló `gap_pct = open(sesión_objetivo)/close(sesión_previa) − 1`.
De ahí se despeja el cierre que efectivamente usó:

```
close_referencia_implícito = open_hoy(sesión_objetivo) / (1 + gap_sellado/100)
```

y se compara con el cierre real de la sesión previa según la historia de hoy:

```
desviación = |close_referencia_implícito / close_hoy(sesión_previa) − 1|
```

## El umbral: 5%

**Fijado antes de mirar.** Un gap genuino por encima del 5% ocurre, pero un
precio de REFERENCIA desviado más de un 5% del cierre real de esa sesión no es
un movimiento de mercado: es un dato equivocado.

## Por qué el criterio es válido pese a los precios ajustados

Yahoo reescribe la historia con dividendos y splits posteriores, pero el
factor de ajuste se aplica **a todos los precios anteriores a la fecha ex por
igual**. Un dividendo posterior al 29-jul escala tanto el `open` del 29 como
el `close` del 28 por el mismo factor, así que **la razón entre ambos se
conserva**. La desviación que este criterio mide no puede ser producida por un
ajuste posterior: solo por un dato de referencia distinto.

## Qué NO se hace con el resultado

**Nada.** No se toca ninguna fila, no se recalcula ninguna métrica publicada y
no se excluye nada. Se reporta el conteo y **su efecto sobre el número
publicado, declarado explícitamente**, para que la decisión la tome un humano.
Las filas selladas jamás se reescriben; si se confirma, es una errata
documentada.
