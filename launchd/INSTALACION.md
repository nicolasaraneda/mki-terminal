# Instalar el snapshot automático (macOS launchd) — paso a paso

Esto hace que tu Mac tome el snapshot diario de señales **solo**, de lunes a
viernes a las **18:15 hora de Chile** (después del cierre de Nueva York y antes
de que abra Asia), sin que tengas que abrir el dashboard.

## Instalación (una sola vez, ~2 minutos)

1. Abre la aplicación **Terminal**.

2. Copia el archivo de configuración al lugar donde macOS busca tareas
   programadas del usuario (pega esta línea completa y presiona Enter):

   ```bash
   cp /Users/nicolasaraneda/Downloads/StockScreenerMKI/launchd/com.mki.snapshot.plist ~/Library/LaunchAgents/
   ```

3. Actívalo:

   ```bash
   launchctl load ~/Library/LaunchAgents/com.mki.snapshot.plist
   ```

4. Verifica que quedó registrado (debe aparecer una línea con `com.mki.snapshot`):

   ```bash
   launchctl list | grep com.mki.snapshot
   ```

5. (Opcional) Pruébalo ahora mismo sin esperar a las 18:15:

   ```bash
   launchctl start com.mki.snapshot
   ```

   Y mira el resultado en el log:

   ```bash
   tail -20 /Users/nicolasaraneda/Downloads/StockScreenerMKI/data/snapshot.log
   ```

## Cómo desactivarlo (si algún día quieres)

```bash
launchctl unload ~/Library/LaunchAgents/com.mki.snapshot.plist
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
- **Si mueves la carpeta del proyecto**, las rutas del .plist quedan rotas:
  edita `launchd/com.mki.snapshot.plist` con las rutas nuevas y repite los
  pasos 2 y 3 (con `unload` antes del `load`).
- El registro de cada corrida queda en `data/snapshot.log`.
