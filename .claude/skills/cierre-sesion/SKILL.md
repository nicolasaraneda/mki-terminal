---
name: cierre-sesion
description: El ritual de cierre de toda sesión de trabajo en MKI Terminal. Úsala antes de terminar cualquier tanda de cambios, siempre. Recuerda que Claude no pushea, verifica el estado del árbol y de la rama, y deja escrito lo que la próxima sesión necesita saber.
---

# Cierre de sesión

La cadencia nueva, acordada a raíz de la pérdida del SSD: **Nicolás pushea al
cierre de cada sesión, después de revisar el diff.** Nunca Claude. Cuatro
commits locales sin pushear fue exactamente lo que costó la migración entera.

## Orden

**1. Dictamen.** Corre `guardian-constitucion` sobre el diff completo. Un
RECHAZO detiene el cierre.

**2. Verdes.** Si se tocó Python, corre la skill `gate`. Sin salida literal de
pytest no hay cierre.

**3. Actas.** Toda decisión de diseño de la sesión está en `DECISIONES.md`.
Toda asimetría nueva, declarada. Toda deuda nueva, declarada. Usa
`acta-decision`.

**4. Estado del árbol.**

```bash
git branch --show-current      # main
git status --porcelain         # ni .db, ni logs, ni .env
git diff --stat HEAD
git log --oneline -5
```

**5. El commit lo prepara Claude, el push lo hace Nicolás.** Deja el commit
hecho si Nicolás lo pidió, y dile literalmente qué comando le toca a él:

```
git push origin main
```

Nunca lo corras tú. Está bloqueado por hook, y el bloqueo es a propósito.

**6. Regenerar `ESTADO.md`.** Es lo que el hook `SessionStart` imprime al
abrir la próxima sesión, y lo primero que lee el agente `orientador`. Máximo
50 líneas. No es historia: es lo que está vivo ahora. Actualiza la fase de cada
frente, el último sello, la lista de decisiones que esperan a Nicolás, y el
siguiente paso. Si un frente no se movió, no lo toques.

Regla de oro del archivo: si una línea sirve para entender el pasado pero no
cambia lo que hay que hacer mañana, va a `DECISIONES.md`, no acá.

**7. Handoff.** Escribe en dos frases qué quedó hecho, qué quedó a medias y
cuál es el siguiente paso concreto. Si la sesión avanzó una fase de la
reactivación o de la 6.0.0, propón actualizar el documento del Proyecto de
Claude: eso es lo que sobrevive a una pérdida de disco.

## Recordatorio de estado

La reactivación está completa y la composición canónica ejecutada. Lo que sigue
abierto es el **segundo movimiento del switch**: apagar los timers del Mac
primero, quitar `MKI_MODO` en el PC después. Es de Nicolás y no se prepara "por
si acaso" dentro de otra tanda. Ver `/switch-titular`.

Si la sesión movió alguna cifra publicada, verificá que se movieron **los doce
bloques** y que corriste el barrido. Ver `/cifras-canonicas`.
