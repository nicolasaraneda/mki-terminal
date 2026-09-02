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

## El argumento que faltaba: ya no es hipotético, tiene precio medido

Hasta ahora este documento argumentaba con la pérdida del SSD — un evento,
ya pasado, que no vuelve a costar nada hoy. Hay un argumento más fuerte
porque es **recurrente y está medido en la moneda del proyecto**: el hit
rate sellado.

La descomposición del Frente D (`GEMELO/resultados/condicional_ventana_larga.md`
§3.5, commit `e900236`) parte los +6.2 pp de la ventana sellada en tres
tramos. El tramo que importa acá es **cuatro fechas de incidente de
producción** (2026-07-05, 07-29, 08-03, 08-05): **n=28 filas, acierto 32.1%
contra 82.1% de "siempre al alza", ventaja −50.0 pp, McNemar p=0.0066.**

> **Sobre el número, con todas sus letras — regla de la casa, ningún
> estimador puntual sin intervalo:** con solo **4 fechas** de cluster
> (07-05, 07-29, 08-03, 08-05), un bootstrap de bloques por fecha es
> degenerado — 4 unidades de remuestreo no producen un IC95 estable, así
> que se declara **no computable con esta n**, no se inventa uno. Lo que
> SÍ sostiene la lectura es que **una sola fecha (2026-07-29) concentra la
> mayor parte del daño** (b=1, c=7 sobre sus 8 filas, la peor proporción de
> las cuatro) y **es la única con hallazgo forense propio**: DECISIONES.md
> §32.5 la señaló por |gap| medio 4.4× el resto y 1/8 de acierto, y §33.3
> midió — con un criterio objetivo declarado antes de correrlo — que **no**
> es un sello corrupto: es una predicción emitida tarde cuya sesión
> objetivo saltó una sesión completa, con datos reales de mercado
> (+28%, +24% esa noche). Y una nota de procedencia sobre la cifra
> "dos fechas, 16 filas, −62.5 pp" que circula en `bitacora_05.md`
> (10:08, commit `758bf07`): **no reproduce contra el artefacto
> committeado** (`condicional_ventana_larga.md`/`.json`, `e900236`, que
> agrega las 4 fechas en un solo tramo de 28 filas). Coincide
> aritméticamente con dos pares posibles de dos fechas cada uno
> —(07-05+07-29) u (07-29+08-05), ambos dan exactamente −62.5 pp sobre 16
> filas porque 08-03 no aporta (b=c=0 esa fecha)— pero el archivo
> committeado no elige entre esos dos pares, y este documento no lo hace
> en su lugar: cita la cifra que el ejecutable sí produce, −50.0 pp sobre
> las 4.

**Por qué es el argumento que faltaba:** −50 pp sobre 28 filas no es un
evento único que ya pasó. Es lo que produce, de forma repetible, el mismo
mecanismo (una máquina que se vuelve a dormir a mitad de una descarga, o
un job que se cuelga y launchd no lo vuelve a disparar) cada vez que
ocurre. La pérdida del SSD argumenta "la máquina se puede caer, una vez, y
duele". Esto argumenta "la máquina se puede quedar despierta a medias, y
duele cada vez que pasa, medido en puntos porcentuales de ventaja sobre el
track record publicado".

---

## Dos mecanismos distintos — no confundirlos

Este documento (la réplica) y `docs/SEGUNDO_SELLO.md` (que otro frente está
diseñando en paralelo) atacan **fallas distintas**, y conviene decirlo
explícito para que nadie los use como si fueran intercambiables:

| | La réplica (este documento) | El segundo sello |
|---|---|---|
| **Falla que cubre** | La máquina se cae, se duerme, o queda colgada — el proceso titular deja de existir o de avanzar | Los datos no habían asentado todavía cuando se selló — la máquina funcionó perfecto, la fuente externa cambió su historia después |
| **Dónde corre** | Otra máquina (el Mac), en paralelo | La misma máquina, más tarde |
| **Qué detectan las 4 fechas de −50 pp de arriba** | Exactamente esto: 07-29 y 08-05 son sellos tardíos por el Mac re-durmiéndose a mitad de una descarga o un cómputo | Nada de esto — ahí la descarga fue completa y a tiempo cuando se pudo completar; el problema fue el reloj, no el dato |
| **Ejemplo real de la OTRA falla, medido esta semana** | — | `sox_sellado_vs_reconstruido` (`GEMELO/CONDICIONAL/condicional.py`) marcó **2026-08-28 y 2026-08-31**, con `descarga_ok=28/28` y el vigía en verde las dos noches (`data/vigia.log`). **Corrección 1-sep, ver abajo: no es que la fuente revisara un precio — retiró la sesión del 28-ago entera.** La máquina no falló. **La réplica no habría detectado esto**: una segunda máquina leyendo la misma fuente externa en el mismo instante ve el mismo dato, y cuando la sesión se retira días después, se retira para las dos |

> **Corrección 1-sep-2026 — el mecanismo no era el que decía esta tabla, y
> el número tampoco.** El diseño del segundo sello
> (`docs/SEGUNDO_SELLO.md`) fue a medir la premisa en vez de heredarla, y
> encontró otra cosa:
>
> - **Ningún precio fue revisado.** Sobre las 25 fechas selladas con
>   `sox_usado_pct`: **23 paridad, 2 barra retirada, 0 divergencias de
>   valor** (23/25 = 92,0%, IC95 Wilson [75,0, 97,8]).
> - **Yahoo retiró la sesión del 2026-08-28 completa.** No hay barra de
>   `^SOX` para esa fecha por ninguna de cuatro formas de pedirla —
>   verificado de nuevo hoy: la serie salta del 27 al 31. De 19 símbolos,
>   **10 la perdieron y 9 la conservan** (52,6%, IC95 [31,7, 72,7]).
> - **El `dif_pp` de 3,47 es un artefacto del ffill** de `GEMELO/datos.py`:
>   al rellenar el hueco, el retorno sale 0,00. Bajo la lógica de
>   producción la diferencia del 28-ago es **5,80 pp**, no 3,47. El 3,49
>   del 31-ago sí reproduce (3,4914).
> - **El sello es coherente y la fuente no.** Los sellos del 28 (−3,47%) y
>   del 31 (+0,57%), tomados con 72 h de diferencia, implican el **mismo**
>   cierre del 28-ago: bandas solapadas en **[11.469,26, 11.470,24]**, un
>   valor que hoy no existe en la fuente.
> - **Tasa base: 1 fecha en 752 sesiones XNYS de 3 años = 0,13%**, IC95
>   [0,02, 0,75]. La ventana del retiro quedó acotada en **≈18 h**, y
>   **≥3 días después** de que la barra naciera.
>
> **Por qué el vigía estuvo en verde:** `salud_descarga` sólo pregunta si
> hay alguna barra en los últimos 7 días. **Un hueco en el medio es
> estructuralmente invisible.**
>
> **La conclusión de la tabla sobrevive intacta y sale reforzada.** Sigue
> siendo una falla que la réplica no cubre, y por una razón más fuerte que
> la que decía: no es que las dos máquinas vean el mismo dato provisional
> — es que **la sesión desaparece para las dos**, tres días más tarde,
> mirando cualquiera de las dos las mire.

**La consecuencia práctica:** activar la réplica sin el segundo sello deja
sin cubrir exactamente la clase de incidente que 08-28/08-31 acaban de
mostrar en vivo; tener el segundo sello sin la réplica deja sin cubrir
exactamente la clase que costó los −50 pp de julio-agosto. **Ninguna de las
dos da redundancia contra la falla de la otra.** Son piezas del mismo
proyecto de blindaje, no versiones alternativas de la misma pieza.

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
