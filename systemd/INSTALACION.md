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

### ⚠ El `Last Result` de esta tarea NO se lee como en las demás

**Mira `Status: Running`, no `Last Result`.** En régimen normal esta tarea
muestra un código que parece un error y no lo es:

| Código | Significa | ¿Sano? |
|---|---|---|
| `267009` (`0x41301`, `SCHED_S_TASK_RUNNING`) | la instancia está corriendo | sí |
| **`0x800710E0`** (`-2147020576`, Win32 **4320**) | la repetición de 15 min intentó arrancar, encontró la instancia viva y **se negó a lanzar otra** | **sí** |

El `0x800710E0` es la consecuencia directa y esperada de
**`MultipleInstances=IgnoreNew`**: es literalmente lo que `IgnoreNew`
hace. Es el estado que vas a ver casi siempre, porque la instancia buena
lleva viva desde el arranque y cada repetición posterior rebota contra
ella.

**Por qué está escrito aquí:** un código hexadecimal negativo en el campo
`Last Result` se lee como avería. Quien lo vea sin este contexto va a
"arreglar" un keep-alive que funciona — y arreglarlo probablemente
signifique quitar `IgnoreNew`, que es lo único que impide acumular una
instancia de `sleep infinity` cada 15 minutos.

Del lado Linux la confirmación real: `pgrep -a "sleep infinity"` con un
**PID bajo** y una hora de arranque pegada a la del boot (`uptime -s`)
prueba que nació con la VM y no con tu sesión.

### Blindaje de energía

```powershell
powercfg /h off               # Fast Startup e hibernación fuera
powercfg /a                   # <- el indicador AUTORITATIVO
powercfg /change standby-timeout-ac 0   # <- IMPRESCINDIBLE, ver abajo
```

**`powercfg /a` es la verdad, no `HiberbootEnabled`.** Ese registro es la
casilla de preferencia de la interfaz y `powercfg /h off` no lo modifica;
mirarlo a él lleva a concluir que el blindaje falló cuando sí funcionó.

**`powercfg /h off` NO BASTA (hallazgo del 25-ago).** Esa orden desactiva
hibernación y Fast Startup, pero **deja S3 (standby) disponible**: el PC
puede dormirse por inactividad **a las 18:10**, en plena ventana de jobs, y
reproducir el patrón de DarkWake que en el Mac dejó sellos a las 21:23 y
19:40 en julio. Por eso se fija `standby-timeout-ac 0`.

Hibernación y standby son **dos blindajes distintos**, y desactivar uno no
desactiva el otro. Lee `powercfg /a` entero, no solo la línea de
hibernación. Sin el standby apagado, todo lo demás da igual: no importa
que la VM sobreviva al arranque si la máquina se duerme sola cuarenta
minutos antes del snapshot.

Horas activas manuales **13:00–07:00** (`ActiveHoursStart=13`,
`ActiveHoursEnd=7`, `SmartActiveHoursState=0`), y **"Get me up to date" en
Off** — ese interruptor anula las horas activas y reinicia igual.

### GATE A-bis — arranque en frío · **APROBADO 25-ago-2026**

La prueba estricta quedó pendiente en agosto porque esa vez se inició
sesión después del boot, y con sesión iniciada un keep-alive que en
realidad dependiera del login pasa la prueba igual.

El procedimiento:

1. Reiniciar el PC
2. **No iniciar sesión.** Esperar 3 minutos en la pantalla de bloqueo
3. Recién entonces entrar y mirar el `Status` de la tarea
4. En Ubuntu: `systemctl --user list-timers 'mki-*'` con los 6 vivos

**Resultado del 25-ago-2026 — aprobado, con esta evidencia:**

| Hecho | Evidencia |
|---|---|
| La VM arrancó sin login | `uptime -s` = `2026-08-25 20:14:12` |
| El keep-alive nació con la VM | `sleep infinity` **PID 396**, `STARTED Tue Aug 25 20:14:25` — 13 s tras el boot, PID de tres cifras |
| systemd es PID 1 | `ps -p 1 -o comm=` → `systemd` |
| Los 6 timers vivos | `systemctl --user list-timers 'mki-*'` → `6 timers listed` |
| Nadie logueado al disparar | `who` vacío |
| Disparo en hora | `mki-vigia-rechequeo.timer` → `LastTriggerUSec = Tue 2026-08-25 20:30:00 -04` |

El disparo de las 20:30, al milisegundo — **dos latencias distintas**, y
conviene compararlas por separado en corridas futuras:

```
20:30:00.156819  systemd: Starting mki-vigia-rechequeo.service   (+157 ms)
20:30:00.244073  primera línea del proceso en data/vigia.log     (+244 ms)
20:30:00.250213  systemd: Finished                               (+250 ms)
```

Los **157 ms** son latencia de systemd, holgadamente dentro del
`AccuracySec=1s` de la unit. Los **87 ms** siguientes son el arranque del
intérprete. Los **244 ms** son lo que tarda el job en dejar rastro propio:
la cifra correcta para "cuánto tarda el sistema en empezar a trabajar",
pero **no** el retraso de systemd, que es la mitad.

Con esto, "el sistema arranca solo" deja de ser hipótesis y pasa a ser
hecho medido. Detalle en `DECISIONES.md`, Etapa 5.0.3 §21.

---

## Limitaciones conocidas

- **Si el PC está apagado a la hora del job**, `Persistent=true` lo
  ejecuta al volver — pero puede ser al día siguiente, y una predicción
  emitida tarde cae en `no_verificable_timing` o, peor, salta una sesión.
  Ver la propuesta de regla de abstención en `DECISIONES.md`.
- **Efecto estampida:** varios días caídos disparan varias corridas al
  volver. Qué corridas perdidas se descartan en vez de ejecutarse tarde es
  una **decisión humana pendiente**, previa al switch.
- **El modo de la máquina no está en las units.** Los timers corren en
  sombra porque `MKI_MODO=sombra` está en `.env` y `modo.py` lo carga con
  `load_dotenv()`; las units **no** declaran `Environment=MKI_MODO`, a
  propósito (el modo vive en un solo sitio). Consecuencia operativa: quitar
  esa línea del `.env` con los timers instalados convierte a esta máquina
  en titular esa misma noche. El orden del switch está en `docs/SOMBRA.md`.
