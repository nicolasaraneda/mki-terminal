# Bitácora 06 — sexta corrida autónoma, 1-sep-2026

Continuación de `bitacora_nocturna.md`, `02`, `03`, `04` y `05`. Una línea
por hito, **con hora local (Chile, UTC−4)**.

## Lo que gobierna esta corrida

**El Frente A es una pregunta constitucional y va primero porque todo lo
demás depende de su respuesta:** ¿la **verificación** es parte del sello, o
sólo lo es la **predicción**? El proyecto nunca lo escribió, y ahora dos
decisiones cuelgan de eso — si las 10 filas mal pareadas se pueden
**re-verificar** en vez de descartarse, y si se puede instituir una segunda
verificación permanente.

**La regla de deduplicación queda CONFIRMADA por Nicolás**, ahora sabiendo
que produce **p = 0,0451**, que no era ninguno de los dos desenlaces que
tenía a la vista al firmar. La confirma porque **se sostiene por el pareo
insumo↔objetivo, que es razón independiente del p**.

**Y en el mismo acto, un cambio de fondo: el estadístico principal de la
ventana sellada deja de ser el McNemar** y pasa a ser el intervalo que
respeta el clúster de día. Hoy: **+9,7 pp con IC95 [−7,2, +26,5]**, n
efectivo **67** y no 238, y **0 de 192** celdas significativas.

## Las cuatro reglas de la casa

1. Una verificación con el mismo mecanismo que produjo la cifra **no es una
   verificación**.
2. Una retractación en prosa no es una retractación: **la corrección va al
   ejecutable**.
3. **Ningún estimador puntual sin intervalo**, y el intervalo se computa.
4. **Un número retirado que sigue ofrecido en el código vuelve a circular.**

Y una regla de proceso que me gané ayer: **staging explícito por archivo,
nunca `git add -A`** — la corrida anterior barrió trabajo en curso de dos
frentes, uno en versión con bugs.

## Hitos

- **11:25** — Arranque. `HEAD=758bf07` tras cerrar el pendiente de la quinta
  corrida. **Fuera de la ventana de sellado**, así que el trabajo pesado
  entra ahora.
- **11:28** — **Frente A despachado, y va primero por diseño.** La pregunta
  constitucional: ¿la verificación es parte del sello o sólo lo es la
  predicción? Con el orden de búsqueda explícito —`CLAUDE.md`, después
  `DECISIONES.md` desde el principio, después `docs/`, después el código
  que escribe los sellos— y con la instrucción que gobierna todo:
  **si el proyecto ya lo definió, la respuesta se lee, no se elige.**
  - Le marqué la tensión que es el corazón del asunto: **el verificador ya
    actualiza filas después de la emisión** —escribe `gap_pct`,
    `acierto_gap`, `verificado_en` sobre predicciones ya emitidas—. Si eso
    no viola "las filas selladas jamás se reescriben", entonces **hay una
    distinción implícita** entre la parte inmutable y la que se completa
    después. **La pregunta es si está escrita o sólo está en los hechos.**
- **11:30** — **Frente C despachado con una restricción deliberada: hace el
  forense y NO propone ninguna regla.** Es la lección del forense anterior,
  que descubrió que los 30 duplicados eran **dos fenómenos distintos** y
  eso cambió la decisión. Con la hipótesis de Nicolás a contrastar —que
  las 15 caen en un período donde sólo el Mac registraba— **contra el
  calendario real de máquinas reconstruido desde actas y commits**, no
  desde `ESTADO.md`, que es un resumen.
- **11:35** — **Frente F despachado.** Con F1 primero, que es la pregunta
  previa: **¿por qué el vigía no vio dos incidentes que costaron 62,5 pp?**
  Si tiene un hueco de esa clase, taparlo es más barato que todo lo demás.
  Y con la restricción que hace honesta a la abstención: **se aplica sólo
  hacia adelante**, porque retirar hacia atrás dos fechas que cuestan 62,5
  pp **es la misma operación que `keep="last"` con mejor excusa**.
- **11:38** — **Frente E despachado al escriba**: el acta de tres partes
  —la confirmación, el tercer desenlace, y **la degradación del McNemar**—
  con la frase que evita el malentendido: **cruzar α no es tener
  evidencia**. Y con la cuarta regla aplicada al propio estadístico: si el
  McNemar deja de ser principal, **que no siga ofrecido como default en
  ninguna firma**.
- **11:40** — **Frente D despachado.** El banco de pruebas vale más que las
  cuatro respuestas: **es lo que va a evaluar la quinta cláusula cuando
  aparezca**. Con el aviso sobre la cláusula 3 ("preferir la que selló a
  tiempo"): es metadata **en la forma**, pero la puntualidad **puede
  correlacionar con el acierto** si un sello tardío usa datos distintos —
  y sabemos que los usa, porque ése es el defecto. **Que lo mida, no que
  lo suponga.**

