# La réplica, en una página

Para leer en cinco minutos y decidir en el momento. El expediente largo es
`docs/REPLICA.md` + `docs/RUNBOOK_REPLICA.md`. **Nada de esto está
activado.**

---

## Qué se activa

Una **segunda máquina que sella las mismas predicciones en paralelo, sin
emitir nada**. El candidato natural es el Mac, que quedó libre tras el
switch. Corre los mismos seis jobs en `MKI_MODO=sombra`: computa, sella en
su propia base, y su única salida de red —el Telegram— escribe a un
archivo en vez de enviar. Después, una comparación diaria de lo que selló
cada una contra lo que selló la otra.

**Qué protege:** el disco de sistema del PC ya falló una vez y se llevó
cuatro commits. Hoy el proyecto tiene **una sola máquina emitiendo**, y la
única red es el backup diario a git.

---

## Qué cambia el primer día

- El Mac sella su propia fila para la fecha del día. Nadie la publica.
- Se corre a mano una comparación y sale uno de cuatro veredictos:
  **PARIDAD**, **DIVERGENCIA**, **DIA_NO_COMPUTABLE**, o
  **PENDIENTE_PUBLICACION** (este último no es final: la titular pushea
  manualmente, así que "todavía no publicó" no es "divergieron").
- **Nada cambia en producción.** El PC sigue sellando y emitiendo igual.
  El reporte de Telegram sale del PC como siempre.

## Qué cambia el primer mes

- Existe un registro diario de si las dos máquinas coinciden.
- **Y hay una cosa que hoy NO existe y hay que saberla antes de firmar:**
  la comparación **no está automatizada**. `comparar_sombra.py` se pensó
  para la ventana del switch, y `replica.py` no la invoca nadie. Sin
  construir un séptimo job, **alguien tiene que acordarse de correrla
  todos los días** — que es exactamente la clase de punto débil que este
  mecanismo existe para eliminar.
- Lo mismo con la **política de retención**: `data/sombra/` y la tabla de
  divergencias crecen sin límite hasta que se decida y se implemente.

---

## Qué se rompe si sale mal, y cómo se vuelve atrás

**El riesgo de fondo es uno solo: que la réplica emita.** Dos máquinas
mandando el reporte de Telegram duplicarían el mensaje diario y romperían
la disciplina de una sola voz.

Contra eso hay tres capas, todas ya probadas:

1. `modo.py` es el único lugar donde vive el modo, y un valor
   **puesto pero ilegible cae a SOMBRA, nunca a titular** — el error caro
   es emitir.
2. En sombra, `alertas.enviar_mensaje()` escribe a
   `data/sombra_telegram.log` y devuelve `ok=True` a propósito, para que
   el resto del sistema recorra los mismos caminos que en producción.
3. `mki_backup.py` retorna antes del `git add`: la réplica nunca toca el
   índice.

**Vuelta atrás, por paso** (está en el runbook, con su comando): apagar
los seis timers del Mac. Eso es todo — la réplica no escribe en ninguna
base de la titular, no pushea, y no participa de la ruta de sellado. El
peor caso deja archivos huérfanos en el Mac, que se borran.

**Lo que el ensayo general ya demostró:** ocho fechas sintéticas por los
tres casos —paridad, divergencia en sus cuatro sabores, y las dos formas
de "una no selló"— con **cero divergencias falsas** y cero hallazgos.

---

## Cuánto tiempo suyo cuesta

| | |
|---|---|
| Activación (pasos 1 a 5 del runbook) | **una tarde**, la mayor parte esperando a que el Mac selle una vez en frío |
| Después, por día | **dos minutos** de correr la comparación a mano… |
| …hasta que se construya el job | y ahí, **cero** |
| Construir el job + la retención | trabajo mío, no suyo, pero **no está hecho** |

---

## La única regla que necesita su firma

**Ante una divergencia, ¿quién gana?**

| Opción | Qué implica | Consecuencia |
|---|---|---|
| **A. La titular gana siempre, sin excepción** (propuesta del documento) | La fila del PC es la oficial pase lo que pase. La divergencia se registra y se investiga después, nunca en caliente. | Simple, auditable, y **nunca reescribe una fila sellada**. Si la titular se equivoca, la réplica lo deja documentado pero no lo corrige solo. |
| **B. Gana la que tenga mejor salud de descarga** | La fila oficial sale de la máquina cuyos tickers bajaron completos. | Puede corregir errores reales de datos. **Pero decide en caliente, y elegir la fila que se sella según un criterio evaluado ese mismo día es una puerta abierta a que el criterio se ajuste al resultado.** |
| **C. Divergencia = no se sella ese día** | Ninguna de las dos filas entra al track record. | Máxima pureza, **peor costo**: convierte cada problema de la réplica en un agujero del track record de la titular. Es darle a la réplica poder de veto sobre producción. |

**Recomendación, marcada como tal: la A.** Es la que preserva la regla
constitucional de que una fila sellada jamás se reescribe, y la única que
no le da a un mecanismo nuevo poder sobre el experimento que lleva
corriendo desde julio. Las otras dos se pueden adoptar más adelante con
evidencia; la A no cierra ninguna puerta.

> Las otras tres decisiones de la sección 0 del runbook (qué máquina,
> confirmar el titular en el acta, y la política de retención) son
> mecánicas una vez tomada ésta. **Ésta es la que bloquea.**
