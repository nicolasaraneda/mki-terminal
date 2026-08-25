# Tareas automáticas de MKI Terminal (Linux / WSL2, systemd de usuario)

Equivalente del `launchd/` de macOS. El Mac sigue usando `launchd/`; esta
carpeta es la del PC. **Ninguna de las dos reemplaza a la otra** — el
proyecto corre en las dos máquinas y `./mki` debe detectar cuál es cuál.

Seis jobs, de lunes a viernes, en orden del día operativo:

| Job | Hora (Chile) | Qué hace | Log |
|---|---|---|---|
| `mki-noticias` | 17:50 | Refresca titulares RSS y los analiza con IA **bajo presupuesto** | `data/noticias.log` |
| `mki-snapshot` | 18:15 | Sella el snapshot diario con reintento parcial si el lote baja incompleto | `data/snapshot.log` |
| `mki-reporte` | 18:25 | Reporte de Telegram desde lo **sellado**, antes de que abra Asia | `data/reporte.log` |
| `mki-backup` | 18:40 | Commitea `data/backups/*.csv` si cambiaron — jamás push | `data/backup.log` |
| `mki-vigia` | 19:00 | Revisa que todo lo anterior ocurrió; alerta por Telegram si no | `data/vigia.log` |
| `mki-vigia-rechequeo` | 20:30 | Epílogo de la alerta (5.0.1): retractación o confirmación | `data/vigia.log` |

Los `.service` y `.timer` son **plantillas**: llevan `__MKI_DIR__` en vez
de una ruta fija, igual que los `.plist` de launchd.

---

## Requisito previo: systemd activo en WSL2

```bash
cat /etc/wsl.conf        # debe contener:  [boot]  systemd=true
ps -p 1 -o comm=         # debe decir:     systemd
```

Si no lo está, editar `/etc/wsl.conf` y desde **Windows**:

```powershell
wsl --shutdown
```

El instalador aborta con un mensaje claro si PID 1 no es systemd.

## Instalación

```bash
bash systemd/instalar.sh                # instala o reinstala (idempotente)
bash systemd/instalar.sh --desinstalar  # quita los 6
```

Deduce la ruta del proyecto, genera los units finales en
`~/.config/systemd/user/`, hace `daemon-reload`, activa los 6 timers y
enciende `enable-linger` para el usuario. No usa sudo y no toca nada del
sistema.

Al terminar imprime `systemctl --user list-timers 'mki-*'`. **Deben
aparecer los seis, con NEXT apuntando al próximo día hábil.**

## Probar un job ahora mismo

```bash
systemctl --user start mki-snapshot.service   # idempotente: no duplica el sello del día
systemctl --user start mki-vigia.service      # revisa el día y alerta si falta algo
tail -20 data/snapshot.log
journalctl --user -u mki-snapshot.service -n 50 --no-pager
```

`systemctl --user status mki-snapshot.service` muestra el último resultado.
Ojo: **el reporte no tiene anti-duplicados** (decisión 4.5), así que
forzarlo a mano envía el mensaje de nuevo. El snapshot y el backup sí son
idempotentes.

---

## Decisiones de diseño de estos units

Los seis parámetros que siguen se validaron en producción el 14-ago-2026,
con seis disparos de seis al segundo.

- **`OnCalendar=Mon..Fri HH:MM America/Santiago`** — la zona va declarada
  en el timer, no heredada del sistema. Un cambio de zona de la VM no
  desplaza los jobs.
- **`Persistent=true`** — si la VM estaba abajo a la hora del disparo, se
  ejecuta al volver. Validado incidentalmente: tras el `wsl --shutdown`
  que hizo la instalación de Docker Desktop, los 6 timers de MKI
  conservaron su LAST mientras los de Ubuntu la perdieron.
- **`AccuracySec=1s`** — sin esto systemd agrupa disparos con holgura de
  hasta un minuto. Los jobs tienen dependencias de orden entre sí
  (snapshot 18:15 → reporte 18:25) y el margen importa.
- **`TimeoutStartSec` finito por job** — la diferencia operativa más
  importante frente a launchd, que no tiene equivalente. Es la segunda
  capa contra la herida del 03-ago, cuando un `feedparser.parse()` sin
  timeout dejó un proceso vivo cuatro días y launchd nunca re-disparó el
  label. La primera capa es `socket.setdefaulttimeout(30)` en el
  entrypoint.
- **`PYTHONUNBUFFERED=1`** — sin esto el log se escribe por bloques y un
  proceso muerto a mitad de camino no deja rastro de dónde estaba.
- **`StandardOutput=append:`** al mismo `data/*.log` de siempre, para que
  `registro.rotar_log` (copy-truncate), `./mki estado` y los chequeos del
  vigía sigan funcionando sin cambios. La salida además queda en el
  journal, que es un extra, no un reemplazo.
- **`enable-linger`** — sin esto los timers de usuario mueren al cerrar la
  sesión. Es lo que hace que el sistema corra solo.

### Los `TimeoutStartSec` son una elección, no un valor recuperado

Los valores del PC original se perdieron con el SSD. Estos son criterio
nuevo y **hay que revisarlos contra la realidad** de las primeras
corridas:

| Job | Techo | Razonamiento |
|---|---|---|
| `mki-noticias` | 1800 s | 44 feeds × 30 s de peor caso, más los lotes de Haiku. El manual del 08-ago tardó 2.5 min con 402 titulares |
| `mki-snapshot` | 1200 s | lleva reintento parcial 60/120 s adentro |
| `mki-reporte` | 300 s | Telegram fija su propio timeout de 10 s |
| `mki-backup` | 120 s | solo git local |
| `mki-vigia` | 300 s | lecturas de base + un mensaje |
| `mki-vigia-rechequeo` | 300 s | ídem |

Si algún job muere por timeout en las primeras semanas, el número está
mal, no el job. Subirlo es una decisión que va a `DECISIONES.md`.

### Lo que NO se declaró, a propósito

- **Sin `After=network-online.target`.** En units de usuario ese target no
  es confiable, y los jobs corren horas después del arranque. La
  resiliencia de red ya vive en el código: reintentos con backoff en
  snapshot y reporte, timeout global en noticias.
- **Sin `Restart=`.** Los jobs son `oneshot` y el vigía de las 19:00 es el
  mecanismo de detección de fallas del proyecto. Un reintento automático
  invisible rompería esa señal, que es justamente la que no puede mentir.
- **Sin `.wslconfig`.** Se decidió que no: con el keep-alive sosteniendo
  un proceso cliente la VM nunca entra en idle, y `vmIdleTimeout` no
  resuelve el reboot.

---

## La mitad que vive en Windows

systemd no arranca si la VM de WSL no está corriendo, y la VM no corre si
nadie la mantiene viva. Esta parte es manual, del lado Windows.

### Keep-alive de la VM

Tarea programada `MKI-WSL-KeepAlive`:

- Trigger: **At system start up**, con repetición cada 15 minutos
- LogonType **S4U** — por diseño no requiere sesión iniciada
- Acción: `wsl.exe -d Ubuntu --exec /usr/bin/sleep infinity`

Comprobación de que quedó bien:

```powershell
schtasks /query /tn MKI-WSL-KeepAlive /v /fo LIST
```

`Last Result: 267009` (`0x41301`, SCHED_S_TASK_RUNNING) es lo correcto:
significa que la tarea sigue corriendo, no que falló. Del lado Linux,
`pgrep -a "sleep infinity"` con un PID bajo confirma que arrancó junto
con la VM.

### Blindaje de energía

```powershell
powercfg /h off      # Fast Startup e hibernación fuera
powercfg /a          # <- el indicador AUTORITATIVO
```

**`powercfg /a` es la verdad, no `HiberbootEnabled`.** Ese registro es la
casilla de preferencia de la interfaz y `powercfg /h off` no lo modifica;
mirarlo a él lleva a concluir que el blindaje falló cuando sí funcionó.

Horas activas manuales **13:00–07:00** (`ActiveHoursStart=13`,
`ActiveHoursEnd=7`, `SmartActiveHoursState=0`), y **"Get me up to date" en
Off** — ese interruptor anula las horas activas y reinicia igual.

### GATE A-bis — arranque en frío

La prueba estricta, que quedó pendiente en agosto porque esa vez se
inició sesión después del boot:

1. Reiniciar el PC
2. **No iniciar sesión.** Esperar 3 minutos en la pantalla de bloqueo
3. Recién entonces entrar y mirar el `Last Run Time` de la tarea
4. En Ubuntu: `systemctl --user list-timers 'mki-*'` con los 6 vivos

Sin esto, "el sistema arranca solo" es una hipótesis, no un hecho.

---

## Limitaciones conocidas

- **Si el PC está apagado a la hora del job**, `Persistent=true` lo
  ejecuta al volver — pero puede ser al día siguiente, y una predicción
  emitida tarde cae en `no_verificable_timing` o, peor, salta una sesión.
  Ver la propuesta de regla de abstención en `DECISIONES.md`.
- **Efecto estampida:** varios días caídos disparan varias corridas al
  volver. Qué corridas perdidas se descartan en vez de ejecutarse tarde es
  una **decisión humana pendiente**, previa al switch.
- **`./mki instalar` sigue apuntando a launchd.** Portarlo con detección
  de plataforma (`uname`) es parte de la Fase 2 de la reactivación.
