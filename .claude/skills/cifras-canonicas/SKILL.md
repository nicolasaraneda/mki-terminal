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

## La ventana sellada, convención canónica `excluir_cero`

Vigente al 30-ago-2026:

| | n | Modelo | Base | Ventaja | McNemar p |
|---|---|---|---|---|---|
| `estricta` | 253 | 66.0% | 58.5% | +7.5 pp | 0.1158 |
| `verificador` | 253 | 66.0% | 60.5% | +5.5 pp | 0.2542 |
| **`excluir_cero`** | **248** | **66.1%** | **59.7%** | **+6.5 pp** | **0.1849** |

Wilson: modelo [60.0, 71.7], base [53.5, 65.6]. MAE del gap 2.98 contra 3.33
(−10.5%). Cobertura del 80%: 90.3%, ratio de ancho 1.84×. Snapshots de régimen:
39. Retorno de sesión 60.9% [54.7, 66.8]. Ventana larga sobre sellada: 59×.

**La ventaja sigue sin ser distinguible de cero.** Eso no cambió con la
composición canónica: era +6.7 pp con la base del PC sola y +6.5 pp con la
canónica.

`excluir_cero` es la convención canónica. Las otras dos se reportan como
sensibilidad, jamás como la cifra principal.

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
esta tabla exactamente: 164/248 da [60.0%, 71.7%] y 148/248 da [53.5%, 65.6%].
Si no las reproduce, el módulo se rompió.
