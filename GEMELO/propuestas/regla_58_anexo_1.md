# Anexo 1 a la regla de decisión de §58 — 29-sep-2026, después del sellado

> **Anexo fechado, con su propio sha256** (en `bitacora_15.md`, sección 1.6). `regla_58.md` quedó
> sellada a las 23:08:17 de Chile con sha256 `ca2ccd536f9d956c2b4a8404ec800341f29e4a0e1f1cd20720c08eca15b9a436`
> y **no se modifica**: lo que sigue se leyó después y no cambia ninguna regla, umbral ni definición.
> Este anexo tampoco lee filas de madrugada: sus fuentes son el journal y el manual de systemd, y el
> inventario del bloque 5 de la corrida 15, que leyó el CSV filtrado por `timestamp_utc < 2026-09-30T04:00:00Z`.

## 1. El disparo de las 18:38:57 lo produjo, por el orden del journal, la recarga y no el reinicio

El inventario de los ocho jobs (`espera_firma.md`, tarjeta de la corrida 15) leyó el journal con
`-o short-precise`: las marcas del mismo proceso `systemd[317]` son, en orden, «Reload requested from
client PID 91601 ('systemctl')» (`.165914`), «Reloading finished in 106 ms» (`.274150`), **«Starting
mki-sonda-cierre.service» (`.327292`)**, y recién después «Stopped», «Stopping» y «Started
mki-sonda-cierre.timer» (`.330093` a `.330264`). El servicio arrancó 53 ms después de la recarga y
2,8 ms **antes** de que el timer se detuviera y volviera a arrancar.

**INFERENCIA, no probada:** el disparo lo produjo el `daemon-reload`, que releyó la unidad con el
calendario nuevo y rearmó el timer desde el último disparo recordado; el `restart` llegó cuando el
servicio ya corría. El acta §91.7 y §91.8 lo atribuyen al `restart`; el orden de las líneas es más
compatible con la recarga. Distinguirlo exige probar en una unidad, que sigue prohibido.

**Lo que cambia y lo que no.** No cambia el procedimiento de la sección 6 de la regla: su paso 3 hace
las dos cosas (`daemon-reload` y `restart`) y su premisa es «dar por hecho que va a disparar al
activar», sea cual sea la orden que lo produzca. Sí cambia una lectura: **evitar el `restart` no
protegería**, porque la recarga es obligatoria para cargar una unidad editada.

## 2. El manual documenta la base «último disparo» para el rearme, y eso favorece a H-A

`man systemd.timer` (systemd 259.5), `DeferReactivation=` (añadida en la versión 257): «the default
behavior is for the timer unit to immediately trigger again once the service finishes running. This
happens because the timer schedules the next elapse based on the previous trigger time, and since
the interval is shorter than the service runtime, that elapse will be in the past, causing it to
immediately trigger once done». Es el rearme después de que el servicio termina, no una recarga ni
un reinicio, pero documenta que **la base por defecto es el disparo anterior**: la hipótesis H-A de
la regla. H-B (la base es la activación anterior de la unidad) sigue sin refutar para el caso de la
recarga. La consecuencia operativa de la regla no cambia.

## 3. La observación de las 17:38 NY del 29-sep es fuera de grilla, y el lector actual no la excluye

La regla ya lo dice (sección 1: «toda otra observación es fuera de grilla: no entra al estadístico y
se declara»). Lo que el inventario midió, calculando `sonda_cierre_resumen.resumen()` en memoria
sobre el CSV filtrado, es que **el artefacto actual `sonda_cierre_resumen.md`, si se regenerara, sí la
tomaría como aparición** («17:38» para 35 tickers), porque su filtro es «anterior al cierre», no «fuera
de grilla». El script de evaluación de la regla (sección 7) no es ese lector; y el lector va a la
corrida 16 con las deudas (3) y (4) de la sonda (acta §91.4). Hasta entonces, **no se regenera
`sonda_cierre_resumen.md`**.

Y un dato que nadie buscaba (DESCRIPTIVO, n = 1): a las 17:38 NY, 98 minutos después de la campana,
la barra fechada hoy existía para 35 de 36 tickers, y a las 20:05 NY para 1 de 36. La fuente retira
la barra intradía **después** de las 17:38 NY, no «al cerrar la sesión» como escribe la bitácora 14
(11.3): errata candidata, que va al acta §92. Es también la barra que el riel de medición lee a las
18:15 de Chile (17:15 NY); que sea el cierre liquidado o una barra provisional no se puede saber desde
el CSV, y no es pregunta de esta regla.
