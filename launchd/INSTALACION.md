# Instalar las tareas automáticas (macOS launchd) — paso a paso

Dos tareas, de lunes a viernes, sin que tengas que abrir el dashboard:

- **com.mki.snapshot** — 18:15 hora de Chile: toma el snapshot diario de
  señales (después del cierre de Nueva York y antes de que abra Asia).
- **com.mki.reporte** — 18:25 hora de Chile: envía el reporte por Telegram
  con lo que el snapshot acaba de sellar (`python alertas.py reporte`).
  Los 10 minutos de separación dan tiempo a que el snapshot y el
  verificador terminen de escribir en senales.db.

## Instalación (una sola vez, ~2 minutos)

1. Abre la aplicación **Terminal**.

2. Copia los archivos de configuración al lugar donde macOS busca tareas
   programadas del usuario (pega estas líneas completas y presiona Enter):

   ```bash
   cp /Users/nicolasaraneda/Downloads/StockScreenerMKI/launchd/com.mki.snapshot.plist ~/Library/LaunchAgents/
   cp /Users/nicolasaraneda/Downloads/StockScreenerMKI/launchd/com.mki.reporte.plist ~/Library/LaunchAgents/
   ```

3. Actívalos:

   ```bash
   launchctl load ~/Library/LaunchAgents/com.mki.snapshot.plist
   launchctl load ~/Library/LaunchAgents/com.mki.reporte.plist
   ```

4. Verifica que quedaron registrados (deben aparecer las dos líneas):

   ```bash
   launchctl list | grep com.mki
   ```

5. (Opcional) Pruébalos ahora mismo sin esperar al horario:

   ```bash
   launchctl start com.mki.snapshot     # toma el snapshot (idempotente)
   launchctl start com.mki.reporte     # envía el reporte a Telegram AHORA
   ```

   Y mira el resultado en los logs:

   ```bash
   tail -20 /Users/nicolasaraneda/Downloads/StockScreenerMKI/data/snapshot.log
   tail -20 /Users/nicolasaraneda/Downloads/StockScreenerMKI/data/reporte.log
   ```

## Cómo desactivarlos (si algún día quieres)

```bash
launchctl unload ~/Library/LaunchAgents/com.mki.snapshot.plist
launchctl unload ~/Library/LaunchAgents/com.mki.reporte.plist
```

## Limitaciones que debes conocer

- **Si el Mac está dormido a las 18:15**, launchd ejecuta la tarea apenas
  despierte, siempre que sea el mismo día. El snapshot es idempotente: si por
  cualquier motivo corre dos veces, no duplica nada.
- **Si el Mac está apagado a las 18:15**, esa ejecución se pierde (launchd no
  "recuerda" tareas de cuando estaba apagado). Red de seguridad: al abrir el
  dashboard, si no existe el snapshot del día, se toma uno automáticamente
  (queda marcado con origen "dashboard" y su hora real de emisión — el
  verificador de timing decide después si esas predicciones son evaluables).
- **El reporte NO tiene anti-duplicados** (decisión de la Etapa 4.5: es una
  acción explícita): si además del horario lo fuerzas con `launchctl start`
  o con el botón del dashboard, recibirás el mensaje de nuevo. El snapshot
  sí es idempotente.
- **Si el Mac despierta después de las 18:25**, launchd ejecuta el reporte
  atrasado ese mismo día: llegará más tarde, pero con el contenido sellado
  del snapshot (que corre primero, a las 18:15 o al despertar).
- **Si mueves la carpeta del proyecto**, las rutas de los .plist quedan
  rotas: edítalos con las rutas nuevas y repite los pasos 2 y 3 (con
  `unload` antes del `load`).
- El registro de cada corrida queda en `data/snapshot.log` y
  `data/reporte.log`.
