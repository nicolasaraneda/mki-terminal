---
paths:
  - "systemd/**"
  - "launchd/**"
  - "scripts/**"
  - "modo.py"
  - "mki"
  - "*.service"
  - "*.timer"
---

# Reglas al tocar plataforma

- **El switch está completo: este PC es el titular**, trabaja en `main`, tiene
  los 6 timers activos y emite. El Mac quedó fuera.
- **Al modo se le pregunta a `modo.py`, no se deduce.** La falla segura no es
  simétrica: valor puesto pero ilegible da `sombra`, valor **ausente** da
  `titular`. Ver la skill `modo-emision`.
- Las actas 36 y 37 describen el estado anterior al segundo movimiento. **Donde
  un documento y la máquina no coincidan, manda la máquina**, y la discrepancia
  se registra como errata.
- Un agente **no cambia el modo, no toca timers y no edita `.env`**. Eso es
  operación de Nicolás, y no se prepara de paso dentro de otra tarea.
- Los scripts se **ramifican por `uname`**, no se reescriben a Linux-only. El
  Mac todavía puede correrlos si algún día vuelve.
- `PLATAFORMA_VERSION` 5.0.3 quedó congelada al sellar la primera fila el
  26-ago. No se cambia de paso.
- Nunca `git pull` sobre el árbol de trabajo: es el código que los timers
  ejecutan. `git fetch` y leer desde `origin/main`.
- Rama de trabajo: `main`. `migracion-wsl` está mergeada y muerta.
- Toda asimetría entre máquinas se declara en `DECISIONES.md`, aunque se decida
  no igualarla.
