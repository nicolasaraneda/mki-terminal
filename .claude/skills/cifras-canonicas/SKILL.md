---
name: cifras-canonicas
description: Las cifras vigentes del proyecto y de dónde salen. Úsala antes de citar cualquier número de acierto, ventaja, MAE, cobertura o n, y cada vez que una cifra publicada tenga que moverse. Incluye la convención canónica de conteo y la regla de los doce bloques.
---

# Cifras canónicas

**Ninguna cifra se cita de memoria y ninguna se clava en un documento nuevo.**
La fuente de verdad son el `README.md` y `DECISIONES.md` del repo, en ese
orden. Esta skill es un mapa de dónde mirar, más las cifras vigentes al momento
de escribirla, marcadas como tales.

Si lo que lees acá no coincide con el `README.md`, **manda el README** y esta
skill está desactualizada. Decirlo es el hallazgo.

## El hallazgo central ya no es un score

Es un mecanismo: **el efecto se disipa con la distancia**. Sobre ocho años
reconstruidos (n = 14.618), el modelo le gana a "siempre al alza" por +19.1 pp
en Tokio, +16.8 en Taipéi y +15.4 en Seúl, las tres bolsas que abren dentro de
tres horas de la emisión, y por +2.5 pp con p = 0.111 en Fráncfort, que abre
8.75 horas después.

Un artefacto estadístico no tiene por qué desvanecerse con el tiempo
transcurrido; una propagación de información sí. El contagio no se traspasa,
se apaga. Con n = 4 bolsas no se ajusta una curva: es un escalón.

## La ventana sellada, convención canónica `excluir_cero` + regla de deduplicación firmada

Vigente al 3-sep-2026 (corte pinchado 28-ago, `cifras.CORTE_README`; la
fuente es `cifras.sellada()`, que lo computa desde `senales.db`):

| | n | Modelo | Base | Ventaja | IC95 de día | McNemar p (χ²cc) |
|---|---|---|---|---|---|---|
| **`excluir_cero` + dedup firmada** | **238** | **67.6%** | **58.0%** | **+9.7 pp** | **[-7.2, +26.6]** | **0.0455** |

Wilson de filas: modelo [61.5, 73.3], base [51.6, 64.1]. Permutación de
signo por día p = 0.294; 34 días, ICC 0.39, DEFF 3.55, ~67 observaciones
efectivas. McNemar binomial exacta 0.0451 (b = 72, c = 49).
MAE del gap 2.52 contra 2.98 (−15.3%). Cobertura del 80%: 92.9%, ratio de
ancho 2.19× con IC95 de día [1.71, 2.78]. Snapshots de régimen: 39. Retorno
de sesión 62.1% [55.9, 68.0] (n = 243).

**La ventaja sigue sin ser distinguible de cero con la unidad correcta (el
día).** El McNemar de filas cruza α; el intervalo de día contiene el cero.
Los dos se publican juntos, y decide el de día (acta §61).

**Errata 3-sep-2026.** Hasta el 2-sep esta skill y el README publicaban la
rama sin deduplicar: era n = 248, +6.5 pp, p = 0.1849 (y las dos
convenciones de sensibilidad, `estricta` y `verificador`, sobre 253 filas).
Esa convención quedó derogada por la decisión D1 de Nicolás (acta §78) y
sus cifras están en `GEMELO/cifras_retiradas.md`: no se citan más.

`excluir_cero` es la convención canónica y la regla de deduplicación
firmada (`backtest.linea_base.deduplicar_por_sesion`, `dedup=True` por
defecto) es la regla de filas. `keep="last"` está PROHIBIDA. La rama «+
coherencia» (retirar además las 15 filas sin pareja, `cola_decisiones.md`
§2a-ter) sigue en cola, sin publicar.

## La regla de los doce bloques

Cuando `n` cambia, cambian todas las cifras que dependen de `n`. **Son doce
bloques y se mueven juntos.** Moverlos a medias es peor que no moverlos, porque
deja una portada internamente inconsistente, que es exactamente la clase de
desfase que este proyecto documenta como errata en vez de cometer.

Hay un script de barrido que verifica que ninguna cifra invalidada sobreviva.
Corrélo, no confíes en la revisión a ojo.

Y toda cifra de la ventana sellada declara su **procedencia**: es la cadena
canónica compuesta de dos fuentes bajo la regla de `docs/SOMBRA.md`.

## Cómo verificar una cifra

Usa la skill `estadistica-evaluacion`. Su self-test reproduce las dos Wilson de
esta tabla exactamente: 161/238 da [61.5%, 73.3%] y 138/238 da [51.6%, 64.1%].
Si no las reproduce, el módulo se rompió. Y `python -m pytest
tests/test_cifras_arbitro.py` verifica que los doce bloques coinciden con el
árbitro y que ninguna cifra retirada volvió.
