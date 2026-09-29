# Pre-mortem del `director-programa` sobre el encargo 14

**Bloque 0.6.** Encargo: devolver las instrucciones del encargo que podrían ser **ellas mismas el
defecto**. El orquestador no ejecuta una instrucción marcada sin anotarla. Veredicto del director:
**PRIMERO ESTO OTRO** — «el encargo está bien construido, pero su bloque 0-bis describe un apagado que
no ocurrió, su cronograma reserva una ventana de 34 minutos que no puede alcanzar, y su bloque 1
extiende una grilla antes de arreglar el artefacto que ya está contaminado con los datos que tiene en
disco».

Transcripción por el orquestador. Se indica en cada punto **qué hizo la corrida**.

## Instrucciones marcadas como defecto

| # | Instrucción | Por qué es el defecto | Qué hizo la corrida |
|---|---|---|---|
| **A1** | 0-bis.7: «qué timers deberían llevar `Persistent=false`» | **Premisa falsa.** La unidad instalada ya lo lleva y disparó igual. `Persistent=` sólo gobierna disparos perdidos mientras el *manager* no corría; con el manager vivo y la máquina suspendida, el timerfd vence y la unidad corre al reanudar. **No hay knob de systemd que lo suprima.** | Se escribió la conclusión correcta en la plantilla y en `espera_firma.md` §63, con las tres opciones y sus costos. La instrucción no se ejecutó como estaba pedida. |
| **A2** | 0-bis.2: la hipótesis del asistente | Ancla la lectura hacia una respuesta **menos grave que la real**: no es «se toma como ya sellado», es la **rama de divergencia**. Y la consecuencia que el encargo no nombra: `ext_2026-09-28.csv`, que 33 filas citan por sha, **es una matriz de media sesión**, y E4-bis ya no permite reescribirla. | Respondido desde el código con las dos ramas. Se agregó la **cuarta opción (d)** a la tarjeta §62: que un sello no verificable no reclame el cupo de evidencia. Sin ella «la tarjeta se firma resolviendo el problema chico y deja el grande». |
| **A3** | 0.3: suite antes de 0-bis, «si no está en verde se para» | Un rojo sólo se puede clasificar con las lecturas de 0-bis, que el encargo ordena **después**. Literalmente cumplido, aborta la corrida antes de poder explicar el rojo. Y es «un verde antes del sello». | Se corrió, se reportó el número, se clasificó el rojo como **preexistente y anticipado** (0-bis.5) y se siguió. Declarado en la bitácora. |
| **A4** | 0.7: «el test de integridad tiene que pasar sobre la base real» | Está pedido **como si fuera absolución y no lo es**: para el 28 pasa porque el archivo intradía en disco es exactamente el que las 33 filas citan. El verde dice «la base cita el archivo que hay», no «el insumo es legítimo». | Los 4 tests pasan, y el verde quedó anotado **con esa glosa en la misma línea** (bitácora 0.5). |
| **A5** | 0-bis.1 scopea la pérdida del 25 al sellador | Se perdieron **tres** rieles. Y el riesgo que podía morder esa misma noche: si `data/vigia_pendiente.json` seguía abierto del viernes, el re-chequeo de las 20:30 retractaría una alerta del viernes con datos del lunes. | Verificado: se perdieron los tres. Y el marcador **no existe** — el `_epilogo_vigia()` del snapshot lo consumió a las 14:43:07 con su retractación. **El riesgo no se materializó.** |
| **A6** | 0-bis.4 escrito en pasado sobre un hecho futuro | A la hora de lanzamiento los timers de la tarde no habían disparado. | Partido en **0-bis.4a** (el disparo de las 14:4x, medido) y **0-bis.4b** (el de las 18:15, al cierre). |
| **A7** | Falta un ítem: la carrera entre `mki-backup` y los jobs que escriben sus CSV | `mki-backup.timer` no declara `After=`; el orden lo da sólo el reloj. El commit `5321f6b «Backup diario 2026-09-28»` **no contiene el sello de ese día**. | Agregado como **0-bis.8** y tarjeta §64. Verificado además que el job commitea con pathspec, así que nada fuera de `data/backups/` se cuela. |
| **A8** | 0-bis.6: condición inaplicable | `data/sonda_cierre.csv` ya está en el índice. | Anotado; la corrida no hizo `git add` ni `git commit`. |
| **A9** | **1.6 ordena producir un resumen que los datos en disco ya contaminan** | `resumen()` no tiene filtro de grilla: las 36 filas del 28 a las 13:42 NY (mercado abierto, 35/36 con `es_sesion_de_hoy=1`) entrarían como la **primera aparición del cierre** para 35 tickers. El informe publicaría «el cierre apareció a las 13:42». **Lo más accionable del bloque 1.** | **Corregido antes de correr 1.6** (bloque 1.3-bis): se descartan las observaciones anteriores al cierre de su sesión, con el cierre leído del calendario, y el informe **declara** cuántas y cuáles. |
| **A10** | 0.7 y 1.6 tratan «fechas UTC 22 a 25» como si fueran sesiones | Están **corridas un día**: 22-sep 00:05 UTC = 21-sep 20:05 NY. Las cuatro noches son las sesiones **21, 22, 23 y 24**. | Corregido y anotado como errata propia del orquestador por haberla repetido. Se filtra sólo por `sesion_ny`. |
| **A11** | 0.9 dice que la columna es `timestamp_` | Es `timestamp_utc`; un `df["timestamp_"]` falla en seco. | Anotado (y el orquestador ya se había estrellado con eso). |
| **A12** | 1.2 inventa una migración de esquema que los datos no necesitan | Ninguna fila en disco es anterior a la apertura de NY, así que la regla nueva reproduce el 100 % de los `sesion_ny` existentes. Columna nueva y lector dual son «máquina para un caso que no existe». | **Se siguió al director:** sin columna nueva, sin lector dual, y con un test permanente que demuestra la equivalencia sobre las 1.188 filas. |
| **A13** | 1.5 reserva una ventana de 34 min a la que no puede llegar | Con la franja de la sonda (21:05–00:35) y la prohibición de suites hasta las 20:31, el único hueco era 20:31–21:05, que tendría que contener el final de una suite de ~900 tests. Recomendación: terminar en worktree y aplicar mañana. | **Aquí el orquestador se desvió, con razón medida:** el director asumió que era 17:5x; eran las 16:52. Se aplicó al árbol real a las **16:56** y la suite completa cerró a las **17:03**, todo **antes** de la ventana y muy antes de la franja de la sonda. El objetivo de 1.5 se cumplió; la maniobra que el director proponía dejó de ser necesaria. |
| **A14** | 1.6: el umbral de 5 noches se cruza solo esta noche | El 28 sería la quinta noche, pero es la **contaminada** y la que el sellador marcó `no_verificable_timing`. | **Se siguió al director:** resumen descriptivo con 4 noches, **ninguna recomendación** sobre (b)/(c), y la tentación declinada queda escrita (bitácora 1.7 y §58). |
| **A15** | 3.1 tiene un criterio de aceptación que se contradice | Si el artefacto no se corrió con 4.000 réplicas, «regenerar da lo mismo con las mismas réplicas» se cumple por construcción y no prueba nada; si se corrió, ya se sabe que falla. Antes de regenerar hay que leer del artefacto la semilla y el número de réplicas. | **Irrelevante en la práctica:** el bloque 3 no se ejecutó por el veredicto del auditor. La observación queda en pie para la próxima corrida. |
| **A16** | 8.7 pide huellas sha256 «idénticas al abrir y al cerrar» de dos bases que los timers van a escribir con certeza | El chequeo aterriza siempre en su propia excepción, así que no es un chequeo. Propone huella a las 17:45 y a las 20:31, con el delta atribuible al log del job. | Aplicado: huellas al abrir, y al cerrar con el delta atribuido job por job y con su hora. |

## Dictamen sobre la franja `Tue..Sat 00..03:05,35 America/New_York` (bloque 1.4)

**No choca con nada instalado.** Leídas las 8 unidades `mki-*` de `~/.config/systemd/user/` y las 4 de
Ubuntu (que no llevan `OnCalendar`): los seis del riel van 17:50–20:30 Chile, la sonda de tarde
21:05–00:35 Chile, el sellador 00:30 Chile. La franja nueva es **01:05–04:35 Chile** hoy. Ningún
minuto de disparo instalado cae ahí.

Cuatro cosas que el director pidió declarar, y quedaron escritas en la plantilla:

1. **`Tue..Sat` es la elección correcta y hay que decir por qué:** los cambios de horario de Nueva
   York ocurren **domingo a las 02:00**, que `Tue..Sat` excluye. Con `Mon..Sun` la hora 02:xx
   dispararía **dos veces en noviembre y cero en marzo**. Anotarlo es lo que hace que la unidad
   sobreviva al 1-nov-2026.
2. Continuidad sin solape de minuto (23:35 → 00:05 son 30 min, el mismo paso). La única proximidad
   estrecha es la ya aceptada (sellador 23:30 / sonda 23:35). **Solape de ejecución posible:** si el
   sellador tardara más de 35 min, su descarga y la sonda de las 00:05 coincidirían.
3. **Duplica el tráfico de la sonda a yfinance**: de 8 a 16 descargas de 36 tickers × 7 días por
   noche hábil, en la máquina cuya cadena de sellos depende de que Yahoo no la limite.
4. La plantilla y lo instalado ya diferían en la primera línea (`17..23:05,35` vs `20..23:05,35`):
   eso es **una errata de la plantilla**, no un agregado.

## Rama lateral cómoda, que el director dijo no hacer

**Los badges (2.3).** «Es entretenido, es técnicamente interesante, toca el generador, y nadie
designó *construir la máquina*: el acta §88.5 firmó reemplazar cifras vencidas, no montar
infraestructura de badges.» La única fuente de `tests-650` es correr la suite, así que «generarlo»
obliga a que el generador corra la suite o a mantener un artefacto intermedio fresco. **Tarjeta con
tres opciones y cero código.** La corrida no escribió código de badges (y el bloque 2 quedó además
bloqueado por el auditor).

Segunda, menor: la columna nueva y el lector dual de 1.2 (A12). Misma forma.

## Orden de trabajo que el director propuso, y que se siguió

El director corrigió el tercer puesto de la prioridad §9 del encargo: «el bloque 2 es justo el que el
dictamen del `auditor-lookahead` puede bloquear, y §9 lo pone tercero sin decir qué se hace si está
bloqueado; la corrida descubriría a las 21:00 que no puede hacer lo que agendó y improvisaría». De
ahí: **el dictamen del auditor se pidió primero, no al final**, y se declaró por escrito, antes de la
ventana, qué pasaba en cada rama. Y se adelantó el **4.4 (enmienda de M2)** porque es redacción pura,
no publica cifras, no lo bloquea el auditor y tiene fecha límite real (la primera fila prospectiva).

**NO INICIADO desde ya, por reloj, según el director:** el **3.2** (medición nueva de `bifurcaciones`:
cinco compuertas secuenciales con dos idas y vueltas al adversario, que no pueden empezar antes de las
20:31 en una noche con bloqueo de `dinero/` de 00:00 a 01:00 — «no termina»).
