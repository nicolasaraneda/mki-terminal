# Tareas automáticas de MKI Terminal (macOS launchd)

Seis jobs, de lunes a viernes, para que el sistema corra solo — el día
operativo completo, en orden:

| Job | Hora (Chile) | Qué hace | Log |
|---|---|---|---|
| `com.mki.noticias` | 17:50 | Refresca titulares RSS y los analiza con IA **bajo presupuesto** (tope en `.env`, freno duro + aviso Telegram) | `data/noticias.log` |
| `com.mki.snapshot` | 18:15 | Sella el snapshot diario (señales, régimen, predicciones, **salud de descarga**) con reintento parcial si el lote baja incompleto | `data/snapshot.log` |
| `com.mki.reporte` | 18:25 | Envía el reporte de Telegram con lo que el snapshot acaba de **sellar** — antes de que abra Asia (~20:00 Chile) | `data/reporte.log` |
| `com.mki.backup` | 18:40 | Commitea `data/backups/*.csv` si cambiaron ("Backup diario {fecha}") — solo esos paths, jamás push | `data/backup.log` |
| `com.mki.vigia` | 19:00 | Revisa que TODO lo anterior ocurrió; si algo falló, **alerta por Telegram** diciendo exactamente qué | `data/vigia.log` |
| `com.mki.vigia.rechequeo` | 20:30 | El **epílogo** de la alerta (5.0.1): si a las 19:00 el snapshot no había sellado, re-chequea — retractación "recuperado: sellado HH:MM" si ya selló, o "sigue sin sellar". Sin alerta pendiente, sale en silencio | `data/vigia.log` |

Los `.plist` de esta carpeta son **plantillas**: llevan `__MKI_DIR__` en vez
de una ruta fija, así el repo no depende de la máquina de nadie.

## Instalación (un solo comando)

```bash
zsh launchd/instalar.sh
```

El script deduce la ruta real del proyecto, genera los `.plist` finales en
`~/Library/LaunchAgents/` y los activa. Es idempotente: si ya estaban
instalados, los reinstala limpio. Al final imprime la lista de jobs
registrados (deben aparecer los 6).

## Probar un job ahora mismo (sin esperar al horario)

```bash
launchctl start com.mki.snapshot    # idempotente: si ya hay sello hoy, no duplica
launchctl start com.mki.vigia       # revisa el día y alerta si falta algo
tail -20 data/snapshot.log
tail -20 data/vigia.log
```

## Desinstalar

```bash
for j in noticias snapshot reporte backup vigia vigia.rechequeo; do
  launchctl unload ~/Library/LaunchAgents/com.mki.$j.plist
  rm ~/Library/LaunchAgents/com.mki.$j.plist
done
```

## Limitaciones conocidas (y qué hacer)

- **Si el Mac está dormido a la hora del job**, launchd lo ejecuta apenas
  despierte (mismo día). Pero ojo con el **DarkWake**: la auditoría del
  13–24 jul demostró que un despertar "a medias" (pantalla apagada, con
  batería) deja la red funcionando parcialmente y Yahoo devuelve lotes
  incompletos. Dos mitigaciones recomendadas:
  1. Mantén el Mac **enchufado** en la tarde de días hábiles.
  2. Programa un despertar COMPLETO antes del primer job (pide contraseña):
     ```bash
     sudo pmset repeat wakeorpoweron MTWRF 17:48:00
     ```
- **Si el Mac está apagado**, esa ejecución se pierde (launchd no revive el
  pasado). Red de seguridad del snapshot: al abrir el dashboard, si no
  existe el sello del día, se toma uno con origen "dashboard" y su hora
  real — el verificador de timing decide después, como siempre.
- **El reporte NO tiene anti-duplicados** (decisión 4.5: es una acción
  explícita): si además del horario lo fuerzas con `launchctl start` o el
  botón del dashboard, llega de nuevo. El snapshot y el backup sí son
  idempotentes.
- **Si mueves la carpeta del proyecto**, basta correr de nuevo
  `zsh launchd/instalar.sh` desde la ubicación nueva.
- Desde la Etapa 5.0 el sistema **nunca falla en silencio**: la salud de
  descarga queda sellada en cada snapshot y el vigía manda alerta de
  Telegram si algo del día no ocurrió.
