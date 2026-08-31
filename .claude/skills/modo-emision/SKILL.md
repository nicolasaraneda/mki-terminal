---
name: modo-emision
description: Cómo se determina qué máquina emite, y por qué nunca se deduce. Úsala antes de razonar sobre si esta máquina es titular o sombra, antes de tocar timers, y cada vez que un documento contradiga a la máquina. Incluye el orden del switch, que ya se ejecutó, como referencia.
---

# Modo de emisión

## La regla, que se aprendió a golpes

**Al modo se le pregunta a `modo.py`. No se deduce.**

```bash
source venv/bin/activate
python -c "import modo; print(modo.modo_actual())"
```

El 30-ago se comprobó que deducirlo da respuestas opuestas. La variable
`MKI_MODO` no estaba ni en el shell ni en el `.env`, y el acta 37.7 afirmaba
que seguía puesta en `sombra`. Las dos lecturas llevaban a estados contrarios,
y las dos estaban equivocadas: `modo.py` respondía `titular`.

La semántica de la falla segura no es simétrica y por eso la intuición falla:
un valor **puesto pero ilegible** resuelve a `sombra`, un valor **ausente**
resuelve a `titular`. Nunca asumas que "no definido" significa apagado.

## Cuando el documento y la máquina no coinciden

**Manda la máquina.** Siempre. Un acta describe el estado en el momento en que
se escribió, no el de hoy, y las actas 36 y 37 son anteriores al segundo
movimiento del switch.

La discrepancia no se interpreta ni se promedia: se registra como errata, con
la fecha, qué decía el documento, qué dice la máquina y cómo se comprobó. Ver
la skill `acta-decision`.

## El estado actual

**El switch está completo.** El PC Windows/WSL es el titular: trabaja en `main`,
tiene los 6 timers activos y emite. El Mac quedó fuera.

Las tres corridas de referencia del timer de backup fueron el 24, 25 y 27 de
agosto, todas en día hábil alrededor de las 18:40, que es su `OnCalendar`. Los
commits del 29 y 30 son manuales, fuera de calendario y de horario, hechos
durante la composición canónica.

## El orden del switch, como referencia histórica

Se conserva porque es la regla que evita el peor escenario, y sirve si alguna
vez hay que volver atrás o mover el titular otra vez:

```
1. Apagar los timers de la máquina que emite hoy.
2. Verificar que no emite: sin reporte de Telegram esa noche.
3. Recién ahí, poner a emitir a la otra.
4. Verificar que emite: reporte, sello nuevo, backup commiteado.
```

Nunca solapado. Dos emisores en paralelo producen Telegram duplicado, dos
cadenas de sellos y dos backups peleando por `main`.

## Lo que un agente no hace

No cambia el modo, no apaga ni enciende timers, no edita `.env`. Eso es
operación de Nicolás, y no se prepara "por si acaso" dentro de otra tanda. Un
agente verifica, reporta y deja el procedimiento escrito.
