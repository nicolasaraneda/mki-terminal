# I · Enmienda a V1 — PROPUESTA con fecha, para firma (2-sep-2026)

> `GEMELO/DISEÑO.md` §6.1 está congelado: los criterios **no se editan
> para que calcen con los datos**. Esta enmienda se propone como
> **adición fechada**, no como edición del texto original, y sólo puede
> **endurecer** la vara. Pasa por `estadistico-adversario` antes de
> cualquier cosa. Intentos del DSR: 0 (no computa nada nuevo).

## 1. El texto vigente y su defecto

**V1 vigente:** «Ventaja sobre "siempre al alza" evaluada en la misma
ventana, con McNemar p < 0,05.» Vara descriptiva: n = 248, +6,5 pp,
p = 0,1849 (README; `dictamen_07/DICTAMEN.md`:374).

**El defecto no es la vara, es la unidad.** El McNemar cuenta filas
discordantes como independientes. Pero el signo del campeón es el signo
del retorno del SOX del día (WS2b: C1 y el campeón aciertan en las
MISMAS filas), así que las ~8 filas de un día comparten la misma
apuesta: la unidad de replicación es el **día**, no la fila. Medido, no
razonado:

- ICC y DEFF (`bifurcaciones.icc_y_deff`): n efectivo **~67–69** donde el
  README cuenta 248 (`ESTADO.md`, `horizonte_veredicto.md`).
- El IC95 **de día** de la ventaja sellada es [−7,2, +26,5] pp: cruza el
  cero por los dos lados; el de filas no (`estado_epistemico.md`).
- Frente A de esta corrida, con verdad conocida: el IC de día cubre
  **0,938 [0,927, 0,948]** (nominal 0,95) y el IC iid de filas cubre
  **0,69**. El instrumento de filas está mal calibrado por construcción;
  el de día casi bien.
- Bajo la nula, con 192 celdas de análisis, **P(al menos una cruza α) =
  0,25 [0,21, 0,31]** (A2): un p < 0,05 «encontrado» en una celda no
  elegida antes no es evidencia.

Un retador podría pasar el V1 vigente con p < 0,05 de filas y un IC de día
que contiene el cero. Eso sería un relevo decidido por un estadístico que
el propio proyecto ya midió como no calibrado.

## 2. La enmienda propuesta: V1-bis, que se AGREGA

> **V1-bis (2-sep-2026).** La misma ventaja, sobre las mismas filas, con
> la convención `excluir_cero` y la regla de deduplicación firmadas, en
> la **celda de análisis pre-registrada** (una, no 192), pero el p es el
> de la **permutación de signo por día** (`bifurcaciones._p_permutacion_dia`,
> ≥ 3.000 réplicas, `semilla` sellada) y se reporta junto al **IC95 de día
> por bootstrap**. Umbral: **p < 0,05** y el IC excluye el cero. Se
> reporta siempre al lado del V1 de filas; los dos números quedan, para
> siempre, uno junto al otro.

Propiedades que la hacen admisible como adición a un diseño congelado:

1. **Sólo endurece.** DEFF > 1: todo lo que pasa V1-bis pasa V1; no al
   revés. No puede favorecer a ningún retador ni al campeón.
2. **No reinterpreta el pasado.** La vara descriptiva del README no se
   toca (regla de los doce bloques). El V1 de filas se sigue publicando.
3. **No mueve el gatillo** (25-oct, `N ≥ 150` vivo o cambio de régimen o
   3 meses): cambia cómo se juzga, no cuándo.
4. **Es la misma unidad que el plan secuencial v5** (Frente F: fronteras
   por simulación con contribuciones de día). Un criterio de entrada de
   filas y un plan secuencial de días serían dos varas para lo mismo.

## 3. Lo que NO se propone, para que no se confunda

- No cambiar el umbral 0,05, ni el comparador «siempre al alza», ni la
  ventana, ni la convención.
- No editar la redacción de V1 en `DISEÑO.md` §6.1: la enmienda se escribe
  debajo, con fecha, como se hizo el 26-ago con la línea base corregida.
- No aplicar V1-bis retroactivamente a WS2b: aquel resultado ya fue
  negativo bajo V1 y bajo R2; V1-bis no lo mejora.
- No sustituir el McNemar por el test de día en `senales.py`, en el
  README ni en la UI: el track record vivo sigue reportando lo que
  reporta. **Sólo el veredicto 5.1 y el relevo usan V1-bis.**

## 4. Consecuencia declarada antes de saber si conviene

Con n efectivo ~2 observaciones por día y el horizonte medido en la
séptima corrida (9 pp → jul-2027 [dic-2026, feb-2028]), **V1-bis hace más
lejano cualquier relevo**. Es el precio de juzgar con la unidad correcta.
Si Nicolás prefiere no endurecer, la alternativa honesta no es dejar V1
como está sino **publicar junto a cada V1 el IC de día**, que ya se
computa: la vara no cambia, el lector ve la unidad.

## 5. Lo que espera la firma

1. **Adoptar V1-bis** como adición fechada a `DISEÑO.md` §6.1 (la
   skill `/acta-decision` la escribe, desde que el agente `escriba-decisiones`
   se retiró el 2-sep-2026; un test fija que el texto original de
   V1 no cambió).
2. Si no: **la alternativa del §4** (IC de día obligatorio al lado del V1).
3. Dictamen previo del `estadistico-adversario` sobre este documento.
