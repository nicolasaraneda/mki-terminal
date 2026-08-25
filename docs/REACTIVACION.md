# Brief de arranque para Claude Code — reactivación de mki-terminal

**Actualizado:** 25-ago-2026 17:20 Chile · **Máquina:** PC Windows / WSL2 / Ubuntu
**Repo:** `/home/nicolasaraneda/dev/mki-terminal` (ext4 nativo, NO `/mnt/c`)

Documento de handoff. Léelo junto con `CLAUDE.md` (la constitución, que
manda sobre esto) y `DECISIONES.md` (la memoria institucional).

> **Fases 0 y 1: COMPLETADAS** el 25-ago en sesión conjunta con Nicolás.
> El detalle y los hallazgos están en la §A al final. Empieza en la Fase 2.

---

## Contexto en una línea

Se perdió el SSD del sistema del PC. Con él se fueron los 4 commits
locales de la migración a Windows —**nunca pusheados**— que contenían la
traducción de los 6 jobs a systemd, el keep-alive y el modo sombra. El
repo se reclonó limpio desde GitHub. El Mac sigue vivo y sigue siendo
**titular**, sellando todas las noches.

Lo que sobrevivió es el acta de qué se construyó y por qué, en el
Proyecto de Claude. Es especificación reconstruible, no código.

## Reglas que aplican a este trabajo

Además de las 6 de `CLAUDE.md`, que mandan:

1. **`motor.py` y la lógica de señales son intocables.** Nada de este
   trabajo toca el modelo; es todo plataforma y entorno.
2. **Las filas selladas jamás se reescriben.**
3. **No pushees.** Nicolás pushea al cierre de cada sesión de trabajo,
   tras revisar el diff. Cadencia nueva, acordada a raíz de esta pérdida.
4. **El PC pushea a la rama `migracion-wsl`, no a `main`.** `main` es el
   carril del Mac, que está en producción. Si `main` avanzara con los
   scripts portados a bash, el Mac se los llevaría en su próximo pull.
5. **Toda decisión de diseño va a `DECISIONES.md`** con su porqué.

---

## ⚠ El orden importa: sombra ANTES que timers

**Corrección a la versión anterior de este brief, que los tenía al revés.**

Si los timers se instalan antes de que exista el modo sombra, el PC se
convierte esa misma noche en un **segundo titular**: manda su propio
reporte de Telegram duplicado, commitea backups y sella en paralelo con
el Mac. El modo sombra es justamente lo que intercepta Telegram y evita
el commit, y se perdió con el SSD.

```
FASE 2  Portar scripts a bash con detección de SO      → GATE 1
FASE 3  Reconstruir el modo sombra                     → sin timers todavía
FASE 4  Instalar los 6 timers + keep-alive             → GATE A-bis
FASE 5  Tres días hábiles con paridad                  → switch
```

---

## FASE 2 — Portar los scripts a bash

Tres archivos son `#!/bin/zsh` con zsh-ismos (`echo "\n..."`):
`mki`, `scripts/pre-commit`, `launchd/instalar.sh`.

**Decisión de diseño tomada, a registrar en `DECISIONES.md`:** el Mac
sigue en producción y corre estos mismos scripts. Por eso `mki` debe
**detectar la plataforma** (`uname`) y ramificar, no ser reemplazado por
una versión Linux-only:

- `./mki estado` llama `launchctl list`; en Linux debe llamar
  `systemctl --user list-timers 'mki-*'`, en macOS seguir igual.
- `./mki instalar` corre `zsh launchd/instalar.sh`; en Linux debe correr
  `bash systemd/instalar.sh`.

Esto es más conservador que reescribirlos y protege al titular.

Repetir el GATE 1 después de portar:

```bash
source venv/bin/activate
python -m pytest tests/ -q     # 70 en verde
python tests/test_motor.py     # anti-look-ahead
```

## FASE 3 — Reconstruir el modo sombra

Se perdió entero. Hay que rehacer:

- **`MKI_MODO=sombra`** — intercepta Telegram hacia
  `data/sombra_telegram.log`, sella local, el backup **no** commitea.
- **`comparar_sombra.py`** — compara los sellos de las dos máquinas.
- **`docs/SOMBRA.md`** — el checklist de switch.

**Bug conocido a corregir de entrada:** en modo sombra el vigía reporta
*"backup: sin commit hoy"* como falla, cuando no commitear es
precisamente el comportamiento correcto. Es una falsa alarma que ensucia
la señal justo en los días que hay que interpretar con cuidado.

**Cómo trae los backups del Mac** (pendiente #3 del acta): `git fetch` y
leer desde `origin/main`, **nunca** `git pull` — el árbol de trabajo es el
código que los timers ejecutan y un merge lo alteraría bajo los pies.

## FASE 4 — Los 6 timers systemd + keep-alive

**La carpeta `systemd/` ya está escrita** (6 `.service`, 6 `.timer`,
`instalar.sh` idempotente, `INSTALACION.md`). Nicolás la tiene como
tarball; si no está en el repo, pídesela. No la reinventes: está
traducida desde los `.plist` de launchd con los parámetros que quedaron
validados en producción el 14-ago.

Diseño: `OnCalendar=Mon..Fri HH:MM America/Santiago` · `Persistent=true` ·
`AccuracySec=1s` · `TimeoutStartSec` finito por job ·
`PYTHONUNBUFFERED=1` · `enable-linger` · logs a los mismos `data/*.log`.

Los `TimeoutStartSec` (1800/1200/300/120/300/300) son **elección nueva**,
no valores recuperados. Revisar contra las primeras corridas reales.

**Lado Windows** (manual, de Nicolás): tarea `MKI-WSL-KeepAlive` (At
system start up, S4U, cada 15 min, `wsl.exe -d Ubuntu --exec
/usr/bin/sleep infinity`), `powercfg /h off` verificado con `powercfg /a`
—**no** con `HiberbootEnabled`—, horas activas 13:00–07:00 y *"Get me up
to date"* en Off.

### GATE A-bis — arranque en frío

Reiniciar, **no** iniciar sesión, esperar 3 min en la pantalla de bloqueo,
y recién ahí entrar y mirar el `Last Run Time` de la tarea. Es la variante
estricta que quedó pendiente en agosto.

## FASE 5 — Tres días hábiles con paridad

El contador vuelve a cero: el día 1 (14-ago) cerró sin paridad y su
diagnóstico nunca se completó.

**Las dos trampas epistemológicas siguen vigentes:**

1. La paridad en fechas anteriores a la copia de bases no prueba nada — es
   comparar un archivo consigo mismo. Solo cuentan los sellos nuevos.
2. Un día solo cuenta si el titular selló de verdad esa noche. Si ninguna
   máquina sella, "nada = nada" da paridad trivial.

**Rutina:** Mac enchufado con `caffeinate -dimsu` entre 17:45 y 20:30 **las
tres noches**, no solo una. Push manual del Mac después de las 20:30.
Código congelado en ambas máquinas durante toda la ventana.

**Antes de arrancar la ventana, volver a copiar `senales.db` y
`noticias.db` del Mac** — la copia actual llega al 24-ago y el Mac sigue
sellando.

---

# §A — Lo que ya se hizo (25-ago) y lo que se aprendió

## Fase 0 — completada

El Mac tenía 4 commits `Backup diario` locales sin pushear (18, 19, 20 y
24 de agosto). Ya están en `origin/main`; HEAD es `6b886e5`.

Se copiaron del Mac al PC por pendrive: `senales.db`, `noticias.db` y
`data/costos_ia.log`. Verificado en destino: integridad `ok`, 35
snapshots, último sello `2026-08-24`, **228 verificaciones**, 4.109
titulares. `git status` limpio — el `.gitignore` funciona.

## Fase 1 — completada

- Repo clonado en `~/dev/mki-terminal` (convención de la máquina:
  RadarMP vive en `~/dev/radarmp`). **No** en `/home/nicolas/` como decía
  el acta — usuario y ruta nuevos. Los units usan `__MKI_DIR__`, así que
  se adaptan solos.
- venv con **Python 3.14.4**, el del sistema.
- Las 14 dependencias directas instaladas en sus versiones fijadas.
  Verificado: `3.0.3 2.4.6 1.5.1 4.13.2` — **idéntico al Mac**.
- `.env` con las 3 claves reales, `chmod 600`.
- **`.python-version` creado** declarando 3.14.4.
- **GATE 1 aprobado:** 70 tests en verde y el anti-look-ahead del motor
  limpio en las tres fechas de prueba.

## Hallazgos a registrar en `DECISIONES.md`

### 1. Asimetría de intérprete, declarada antes de ver resultados

El Mac corre **Python 3.11.15**; el PC corre **3.14.4** (es el `python3`
que trae esta Ubuntu, y era también el del PC perdido). Nunca se igualó
al titular: la migración introdujo esa diferencia desde el día uno sin
declararla.

Se decidió **no igualarla**, por tres razones: el PC perdido corrió
3.14.4 con este mismo `requirements.txt` y dejó 79 tests en verde;
las librerías que hacen el álgebra (pandas 3.0.3, numpy 2.4.6) son
idénticas en ambas máquinas; y ahora existe un control **más fuerte** que
igualar intérpretes — las dos máquinas parten de la misma `senales.db`.

Queda anotado como asimetría conocida, en la misma familia que el
`TimeoutStartSec` finito del PC frente a launchd. Si el modo sombra
vuelve a mostrar β sistemáticamente distintos, instalar `pyenv` con
3.11.15 es el siguiente experimento, ya con hipótesis formada.

### 2. `NOTICIAS_PRESUPUESTO_USD_DIA`: pendiente #2 cerrado

**Tampoco está definida en el Mac.** El acta suponía que el PC caía al
default de 0.50 mientras el Mac tenía valor propio; resulta que ambas
máquinas estaban en 0.50. **No hay nada que igualar**, y queda descartada
una de las dos causas candidatas de la divergencia del 14-ago. La otra
—el desfase de una sesión en los datos de precio, coherente con el
`N=148 vs 147`— sigue en pie y es ahora la principal.

Se dejó fuera del `.env` del PC a propósito: igualar por omisión también
es igualar.

### 3. Deuda declarada: `pd.concat` y el futuro pandas 4

La suite emite `Pandas4Warning` en `motor.py:215` —**la regresión de
betas**— y en `api/main.py:666-668`:

> *Sorting by default when concatenating all DatetimeIndex is deprecated.
> In the future, pandas will respect the default of `sort=False`.*

Hoy es inofensivo: `requirements.txt` fija `pandas==3.0.3` en ambas
máquinas y para eso existe el pin. El riesgo aparece **el día que alguien
suba pandas a 4**: el `concat` cambia su default y los β pueden moverse
en silencio, sin que ningún test lo grite.

`motor.py` es intocable, así que hacer el `sort=` explícito no es un fix
casual — es preservación del comportamiento actual y hay que demostrarla
**byte-idéntica**, como el proyecto ya hizo con las excepciones
quirúrgicas del WS2. **No es tarea de hoy.** Es deuda declarada y un
bloqueador explícito de cualquier upgrade de pandas.

---

## Pendientes de fondo que NO son de esta reactivación

Están en `DECISIONES.md` y siguen abiertos. No los resuelvas de paso.

1. **Regla de abstención de sellos tardíos** — propuesta formal, NO
   implementada. Candidata al modelo retador de la 5.1.
2. **`ts_emision` se estampa antes del cómputo:** ningún campo registra
   cuándo la fila se hizo visible. Decisión humana.
3. **La retractación no reintenta ante error de conexión.**
4. **Qué corridas perdidas se descartan** en vez de ejecutarse tarde
   (efecto estampida de `Persistent=true`). Decisión humana previa al
   switch.
5. **Contradicción del GATE 0** ("último sello 13-ago" vs el Telegram de
   esa noche).
6. **Etapa 5.1 — el veredicto del backtest.** Ver
   `claude/hallazgo-deriva-acierto-gap-2026-08-25.md`: N ya va en 228, el
   umbral de 150 quedó atrás, pero **el cambio de régimen no ha
   ocurrido** y el acierto de gap viene cayendo. Ejecución = decisión de
   Nicolás, criterios congelados en `backtest/DISEÑO.md`.
