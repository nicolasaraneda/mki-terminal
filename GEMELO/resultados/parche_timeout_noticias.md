# Parche preparado (NO aplicado) — margen de `TimeoutStartSec` de `mki-noticias.service`

**Fecha:** 2-sep-2026, ~02:00 Chile, séptima corrida autónoma. **Motivo:**
la noche del 1-sep systemd mató `mki-noticias.service` a las 18:20:00 por
`TimeoutStartSec=1800` — acta 70 de `DECISIONES.md`. Este documento junta la
evidencia, mide la causa, y prepara el cambio para que Nicolás lo aplique a
mano. No se tocó `systemd/mki-noticias.service` ni `launchd/` ni se corrió
`systemctl` con nada que no sea lectura (`show`).

---

## a) Duraciones históricas, con evidencia

Fuente: `journalctl --user -u mki-noticias.service` (start/finish/CPU/wall
por corrida — cubre desde que los timers systemd existen, 26-ago), cruzado
con `data/noticias.log` (línea `titulares nuevos guardados: N`, marca el
fin de la fase RSS+dedup) y `data/costos_ia.log` (línea `analizados X de Y
pendientes · costo`, marca el fin de la fase Haiku). **No hay
`data/noticias.log.1`** — el log no ha rotado todavía (2 MB × 2 copias,
`registro.rotar_log`), así que la ventana de evidencia por log es la misma
que la de journalctl: no hay corridas de antes del 26-ago disponibles por
ninguna de las dos fuentes locales (`journalctl --user` tampoco tiene nada
anterior — el corte es el mismo: instalación de los timers systemd).

| Fecha  | Inicio (Chile) | Fin / muerte    | Wall clock  | CPU consumida | Titulares nuevos | Analizados | Resultado |
|--------|-----------------|------------------|-------------|----------------|-------------------|------------|-----------|
| 26-ago | 17:50:00        | 18:12:08         | 22min 8.6s  | 18min 16.7s    | 309               | 308        | ok        |
| 27-ago | 17:50:00        | 18:14:37         | 24min 24.0s | 21min 20.3s    | 232               | 233        | ok        |
| 28-ago | 17:50:00        | 18:17:51         | 27min 51.0s | 25min 12.8s    | 192               | 192        | ok        |
| 31-ago | 17:50:00        | 18:18:15         | 28min 14.5s | 24min 51.7s    | 255               | 253        | ok        |
| 01-sep | 17:50:00        | **18:20:00 (killed)** | **30min 0.2s (TOPE)** | 27min 15.3s | 223 (guardados, no analizados) | 0 (nunca llegó) | **TIMEOUT** |

(29 y 30-ago son sábado/domingo — el timer es `Mon..Fri`, correctamente no
disparó.)

**Lectura:** la duración crece de forma monótona en las 5 corridas
disponibles (22:09 → 24:24 → 27:51 → 28:15 → ≥30:00), y **no** sigue al
número de titulares nuevos del día (309, 232, 192, 255, 223 — sin
relación). El "percentil" clásico de una muestra estacionaria no aplica
aquí: la serie no es estacionaria, ver (b) y (d).

## b) Dónde se va el tiempo — medido, no a ojo

Descompuse cada corrida en sus dos fases usando los timestamps de
`data/noticias.log` (inicio del job → línea "guardados" = fase RSS+dedup;
"guardados" → línea "analizados" de `data/costos_ia.log` = fase Haiku):

| Fecha  | Fase RSS+dedup (CPU+red) | Fase Haiku (red+API) |
|--------|--------------------------|------------------------|
| 26-ago | 18min 45s                | 3min 17s               |
| 27-ago | 22min 2s                 | 2min 30s                |
| 28-ago | 25min 42s                | 2min 4s                 |
| 31-ago | 25min 20s                | 2min 49s                |
| 01-sep | 27min 43s                | nunca llegó a completar (mató a mitad) |

La fase Haiku es corta, estable (2–3 min) y **no crece** con el tiempo — es
la fase RSS+dedup la que crece todos los días, y `27min 15s de CPU sobre
30min de wall clock` (acta 70) confirma que ese crecimiento es CPU, no
espera de red.

**Causa raíz, medida sin llamar a la API (solo lectura de `noticias.db`,
sin escribir nada, sin tocar la base real):** `noticias.actualizar_titulares()`
llama a `migrar_noticias_v2()` **incondicionalmente en cada corrida**, y
esa función hace deduplicación por similitud (`difflib.SequenceMatcher`,
umbral 0.85) **sobre TODO el historial de `titulares`** — no sobre una
ventana, a diferencia de la deduplicación de titulares nuevos del día (esa
sí usa una ventana de 10 días, `WHERE fecha >= datetime('now', '-10
days')`, en la misma función `actualizar_titulares`). Es O(n²) sobre `n` =
filas totales de la tabla, que crece indefinidamente.

Reproduje el bucle EXACTO de `migrar_noticias_v2` (normalización +
`SequenceMatcher` par a par) leyendo `noticias.db` en modo `?mode=ro`
(sin escribir nada, sin llamar a la API, sin tocar el archivo real):

```
N titulares (hoy, 2-sep): 5286
N 'vistos' final (sobrevivientes tras dedup): 5246
Comparaciones SequenceMatcher realizadas: 13,822,418
Tiempo total: 1803.72 s  (30min 3.7s — SOLO esta función)
```

Y el conteo de filas totales *antes* de cada corrida (medido con
`SELECT COUNT(*) FROM titulares WHERE date(fecha) < 'AAAA-MM-DD'`):

| Fecha  | Filas totales antes de correr | Wall clock total |
|--------|-------------------------------|-------------------|
| 26-ago | 4339                           | 1328.6 s          |
| 27-ago | 4538                           | 1464.0 s          |
| 28-ago | 4729                           | 1671.1 s          |
| 31-ago | 4922                           | 1694.5 s          |
| 01-sep | 5112                           | ≥1800 s (killed)  |

`wall / N²` da 7.06e-5, 7.11e-5, 7.47e-5, 6.99e-5 — **prácticamente
constante** (±3%). Es un ajuste cuadrático casi perfecto:
`wall_s ≈ 7.16e-5 × N²`. Con N=5112 (filas antes del 1-sep) el modelo
predice 1871 s (31.2 min) — coherente con que el kill llegó a los 1800 s
todavía en la fase RSS+dedup, antes de tocar Haiku. La tabla del `noticias.db`
tiene historial desde 2025-09-09 (5286 filas hoy) — `migrar_noticias_v2`
compara cada titular contra ese año entero, todos los días, aunque sea
idempotente y no encuentre nada nuevo que borrar.

**Conclusión de (b):** el cuello de botella es CPU, es
`migrar_noticias_v2`, y **crece con el cuadrado del historial acumulado**,
no con los titulares del día. Ningún ajuste de "titulares por corrida,
lotes más grandes o paralelismo en Haiku" toca esta función — está fuera
de la fase Haiku por completo (ver alternativas en (d)).

## c) Consideraciones de ventana

- El snapshot de las 18:15 (el sello, intocable) **selló bien la noche del
  1-sep** con noticias corriendo/muriendo al lado: `data/snapshot.log`
  registra `22:15:01Z` (=18:15:01 Chile) con `descarga: 28/28` y 15
  verificaciones — sin degradación. No hay evidencia de que noticias.py
  saturando un núcleo haya afectado al snapshot esa noche; son procesos
  systemd independientes (`Type=oneshot`, sin `After=`/`Before=` entre
  ellos) y la única vía de interferencia es contención de CPU, que no se
  manifestó en un sello degradado.
- Ningún `MultipleInstances` aplica aquí — eso es de la tarea programada de
  Windows (`MKI-WSL-KeepAlive`), no de los timers systemd de Linux.
- **Restricción dura para cualquier valor nuevo:** el job arranca a las
  17:50 y `mki-backup.service` a las 18:40. Un timeout que deje terminar el
  job después de las 18:40 arriesgaría solaparlo con el backup (que si
  bien no toca los mismos archivos, es el mismo patrón de "trabajo pesado
  compitiendo por CPU en la ventana de sellado" que la propia acta 70
  señala como incumplimiento). Por eso cualquier valor propuesto debe
  garantizar que el job termine **antes de las 18:40**, con margen.

## d) El valor propuesto

**No hay un percentil clásico que aplicar** — la serie no es estacionaria
(crece con `N²`, `N` = historial acumulado, que sube ~190 titulares
netos/día hábil según los últimos 5 días). Cualquier techo fijo es, por
diseño, una carrera contra un crecimiento cuadrático: **es un parche
temporal, no una solución**, y hay que decirlo así.

Con el modelo `wall_s ≈ 7.16e-5 × N²` y crecimiento ~190 filas/día hábil,
la "vida útil" de un techo nuevo antes de volver a toparlo:

| `TimeoutStartSec` | Fila N que lo agota | Días hábiles de margen desde hoy (N=5286) |
|---|---|---|
| 2100 s (35 min) | ~5416 | ~0.7 días — **no sirve, ya casi está ahí** |
| 2400 s (40 min) | ~5790 | ~2.6 días |
| **2700 s (45 min)** | **~6141** | **~4.5 días (≈ 1 semana hábil)** |
| 3000 s (50 min) | ~6473 | ~6.2 días |
| 3600 s (60 min) | ~7091 | ~9.5 días — pero termina 18:50, **choca con el backup de 18:40** |

**Propuesto: `TimeoutStartSec=2700` (45 minutos), no más.**
Justificación:
1. Termina como muy tarde a las **18:35** — 5 minutos de margen limpio
   antes de `mki-backup.service` (18:40), respetando la restricción de (c).
2. Da ~1 semana hábil de margen real (no ilusorio: medido contra el ajuste
   cuadrático, no contra una media estacionaria que ya no describe la
   serie) — tiempo suficiente para que Nicolás evalúe y aplique la
   alternativa estructural de abajo.
3. Sigue siendo "un margen de minutos, no de sobra" (la propia acta 70) —
   1.5× el techo actual, no un salto a "horas": la herida del 03-ago fue
   un proceso que quedó vivo **para siempre** sin ningún timeout
   disparándose nunca; un techo finito de 45 min sigue garantizando
   terminación, solo que un poco más tarde. No reabre esa herida.
4. **No es la solución de fondo.** Si nadie toca el código, el 2700 s se
   agota en días, y hay que volver a subirlo — una escalera sin techo.

**La alternativa real — bajar la duración, no subir el techo:**
`migrar_noticias_v2()` podría acotar su comparación a una ventana (p. ej.
90 días, o reusar los 10 días que ya usa el resto de `actualizar_titulares`
para el dedup de titulares nuevos) en vez de comparar contra el historial
completo cada vez. Con eso el costo por corrida deja de crecer sin límite:
vuelve a ser aproximadamente constante en el tiempo, y probablemente el
`TimeoutStartSec` actual de 1800 s alcanzaría de sobra.

*Riesgo de esa alternativa (por eso no se aplica acá, es de Nicolás):*
acotar la ventana significa que un titular duplicado que reaparece después
de la ventana (una fuente republica una nota vieja más de 90/10 días
después) dejaría de detectarse como duplicado y se colaría dos veces en el
análisis de sentimiento. Es un riesgo bajo (los feeds de Yahoo/Google News
no suelen republicar notas de hace meses con el mismo titular exacto) pero
es un cambio de comportamiento de `noticias.py`, y por eso queda como
propuesta, no como parche aplicado — igual que subir el timeout, es
territorio de Nicolás decidir, aunque `noticias.py` no esté en la lista de
archivos intocables de esta corrida.

*Otras alternativas descartadas explícitamente:* "menos titulares por
corrida" y "lotes de Haiku más grandes" no tocan el cuello de botella real
(la fase Haiku mide 2–3 min, estable — ver (b)); "paralelismo" en la fase
Haiku no ayuda por la misma razón, y paralelizar `migrar_noticias_v2`
(multiprocessing sobre los pares de `SequenceMatcher`) reduciría el wall
clock pero no el trabajo total, sigue creciendo con `N²`, y agrega
complejidad de concurrencia a un sistema que deliberadamente la evita en
otros lados (`DECISIONES.md`).

## e) El diff preparado (NO aplicado)

```diff
--- a/systemd/mki-noticias.service
+++ b/systemd/mki-noticias.service
@@ -8,7 +8,12 @@
 # El job termina SIEMPRE. La herida del 03-ago (feedparser sin timeout dejó
 # un proceso vivo 4 días y launchd nunca re-disparó el label) se cierra en
 # dos capas: socket.setdefaulttimeout(30) en el entrypoint, y este techo.
-TimeoutStartSec=1800
+#
+# 2-sep-2026 (acta 70 + GEMELO/resultados/parche_timeout_noticias.md): el
+# 1-sep systemd mató el job a los 1800s con migrar_noticias_v2() todavía
+# corriendo (O(n^2) sobre TODO el historial de noticias.db, medido en
+# ~7.16e-5 * N^2 segundos). 2700s da ~1 semana hábil de margen sin chocar
+# con mki-backup.service (18:40) — parche temporal, no la solución de
+# fondo. Revisar de nuevo si vuelve a matarlo.
+TimeoutStartSec=2700
 KillMode=mixed
```

`launchd/com.mki.noticias.plist` (macOS) **no tiene equivalente de
`TimeoutStartSec`** — esa asimetría ya está declarada en `DECISIONES.md`
(Etapa 5.0.3: "systemd finito, launchd sin equivalente"). No hay nada que
tocar ahí; se deja constancia de que se revisó y no aplica.

**Comandos que correría Nicolás para aplicar el cambio** (ninguno se
ejecutó en esta corrida):

```bash
# 1. Aplicar el diff de arriba a systemd/mki-noticias.service a mano, o:
#    editar la línea TimeoutStartSec=1800 -> TimeoutStartSec=2700 y agregar
#    el comentario.

# 2. Reinstalar / recargar la unit (./mki instalar copia la plantilla con
#    __MKI_DIR__ resuelto y corre daemon-reload; o a mano:)
cp systemd/mki-noticias.service ~/.config/systemd/user/mki-noticias.service
sed -i "s#__MKI_DIR__#$(pwd)#g" ~/.config/systemd/user/mki-noticias.service
systemctl --user daemon-reload

# 3. Verificar sin disparar nada (solo lectura):
systemctl --user show mki-noticias.service -p TimeoutStartUSec

# 4. Confirmar que el timer sigue igual (no se toca):
systemctl --user list-timers mki-noticias.timer
```

## Archivos de este parche

- `GEMELO/resultados/parche_timeout_noticias.md` (este archivo) — creado.
- **Ninguno** de `systemd/mki-noticias.service`, `launchd/*`, ni ningún
  timer instalado en `~/.config/systemd/user` fue editado ni recargado.
