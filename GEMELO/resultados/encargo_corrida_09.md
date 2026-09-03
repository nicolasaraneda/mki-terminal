# Encargo corrida 09: aplicar las decisiones, pagar la deuda postergada y abrir la ruta al veredicto

Leé este archivo entero antes de ejecutar nada. Corrida nocturna sin supervisión; Nicolás revisa a la mañana. Nada se pushea: el push lo hace Nicolás después de leer el diff.

Esta corrida tiene tres bloques con orden estricto. El bloque 1 aplica decisiones ya tomadas. El bloque 2 paga deuda que lleva meses postergada y que sostiene la visión del proyecto (respaldo restaurable, sello sin filas malas, réplica). El bloque 3 abre la ruta al veredicto con la métrica correcta. Si el tiempo no alcanza, se cierra limpiamente lo abierto y lo restante queda como no iniciado en la bitácora. Un frente a medias sin bitácora es peor que uno no empezado.

## 0. Orientación obligatoria

1. `orientador` reconstruye el estado. Orden de lectura: `ESTADO.md`, `GEMELO/resultados/estado_epistemico.md`, `espera_firma.md`, `cola_decisiones.md`, `bitacora_08.md`, acta §75 de `DECISIONES.md`, y `GEMELO/resultados/calibracion_instrumento.md`.
2. Toda cifra se lee de la máquina (módulo árbitro o README renderizado), nunca de memoria ni de este archivo. Si este archivo y la máquina no coinciden, manda la máquina y se anota errata.
3. Suite completa antes de empezar; anotá el número. Si no está en verde, parás y reportás.
4. Ventana de sellado 17:50 a 20:30 hora de Chile: nada pesado. Si un frente cae ahí, se pausa.
5. El registro de intentos del DSR se incrementa por cada hipótesis probada esta noche, incluidas las descartadas.

## 1. Límites duros

- No se tocan `motor.py`, `senales.py`, `snapshot.py`, `universo.py`, el modo de emisión, `.env` ni los timers. Donde un frente necesite tocar uno de ellos, produce un parche NO aplicado (archivo `.diff` más test que lo cubre) y lo deja en `espera_firma.md`.
- No se reescribe ninguna fila sellada. Errores históricos son erratas.
- Ninguna cifra publicada se mueve sola: si se mueve n, se mueven los doce bloques dependientes, o no se mueve.
- Ningún estimador puntual sin intervalo computado. Clúster de día siempre que haya más de un ticker por fecha.
- Todo lo nuevo se etiqueta PROPUESTA hasta el dictamen de `estadistico-adversario`.
- Una verificación que usa el mismo mecanismo que produjo la cifra no es verificación.
- La corrección va al ejecutable antes que al texto.

## 2. Decisiones de Nicolás que esta corrida aplica

Están tomadas. No se rediscuten; se ejecutan y se registran en acta.

- **D1. Rama del efecto.** La cifra publicada de la ventana sellada es la de la regla de deduplicación firmada el 1-sep (según el árbitro: n=238, +9,66 pp, con su intervalo de clúster). La convención sin deduplicar queda derogada y entra al registro de cifras retiradas. La cifra de +14,3 que está en cola no se publica: queda en cola con su etiqueta.
- **D2. Registro de intentos.** Se confirma la convención declarada en §28 de `cola_decisiones.md`. El conteo vigente (286 según la bitácora 08; verificalo) es el que usa el DSR.
- **D3. Métrica primaria.** La métrica primaria del veredicto pasa de acierto direccional a magnitud (MAE contra predecir cero, y CRPS donde haya densidad). La dirección se sigue publicando como métrica secundaria, con la misma firmeza.

## 3. Bloque 1: aplicar las decisiones (obligatorio)

### 1a. Propagar D1 por el árbitro
Cambiá la convención en el módulo árbitro, verificá que los doce bloques dependientes se mueven con ella (el test del Frente G de la corrida 08 debe cubrirlo; si no lo cubre, se completa primero), regenerá README y `estado_epistemico.md`. La cifra vieja entra a `cifras_retiradas.md` y el hook la bloquea. Acta en `DECISIONES.md`.

### 1b. Horizonte y frase de potencia con la unidad correcta
Recomputá `horizonte.md` con el DSR corregido y con la potencia medida por el simulador (la bitácora 08 dice que el horizonte era optimista en +2,7 pp; verificalo con el simulador, no con la bitácora). Producí la frase de potencia del 5.1 en dos versiones, dirección y magnitud, cada una con n, intervalo y fecha estimada de veredicto. Las dos van a `espera_firma.md`; ninguna al README hasta firma.

### 1c. Enmienda V1-bis
Redactá la enmienda al pre-registro de GEMELO como documento separado (`GEMELO/preregistro/enmienda_v1bis.md`), sin tocar el original. Contenido: qué reemplaza a V1 bajo D3, por qué es legítimo si se firma antes de ver resultados del retador, qué la haría ilegítima, y qué criterios V2 a V7 quedan afectados por el cambio de métrica. El adversario dictamina si la enmienda es un cambio de vara o un cambio de pregunta.

### 1d. Arreglos menores
`CLAUDE.md` deja de describir al Mac como titular (manda la máquina). El ratio 1,84× o entra al árbitro con n e intervalo o se retira; no puede circular suelto. El hook `guardia-reglas` deja de afirmar que en el PC la rama es `migracion-wsl`.

## 4. Bloque 2: la deuda que sostiene la visión

Un instrumento de medición que no puede restaurarse desde su propio respaldo, que produce filas malas cuando el sello se atrasa, y que sella desde una sola máquina cuyo disco ya falló, no es todavía un instrumento. Estos frentes llevan meses en el backlog. Van en este orden.

### 2a. El importador de CSV: el camino de vuelta
`data/backups/*.csv` se commitea todos los días desde julio y no existe importador. Construí `snapshot_restaurar_desde_csv` (o el nombre que el auditor sugiera) fuera de `snapshot.py`, en un módulo propio. Criterio de aceptación, sin excepción: restaurar una `senales.db` vacía desde los CSV y demostrar que las filas resultantes son idénticas fila por fila a las selladas, incluida `plataforma_version` de cada snapshot. La demostración es un test que compara contra una copia de la base real, byte a byte donde aplique. Si alguna fila no es restaurable, se lista con la razón: eso es un hallazgo, no un fallo del frente.

### 2b. El parche de snapshot.py:140, como parche no aplicado
Sigue produciendo filas malas cada vez que un sello se atrasa. Producí el `.diff` con su test, más la copia de insumos que espera firma, sin aplicarlo. Cuantificá: cuántas filas malas produjo hasta hoy (con fechas), y qué habría pasado con cada una bajo el parche. Va a `espera_firma.md` con esa tabla.

### 2c. El timeout O(n²) del job de noticias
Tiene causa raíz conocida y va a volver a morir. Corregí la causa raíz en el código del job (no en el timer ni en el modo de emisión), con un test que reproduce el crecimiento cuadrático sobre entrada sintética y demuestra que ahora es lineal o mejor. Medí el tiempo antes y después sobre los datos reales.

### 2d. Las tres decisiones humanas, como tarjetas para firmar
Llevan meses abiertas porque nadie las ha puesto en un formato firmable. Para cada una escribí una tarjeta en `cola_decisiones.md`: opciones, costo medido de cada opción sobre datos reales (no estimado), recomendación del director y qué se hace el día después de la firma.
- Regla de abstención por sello tardío: cuántas filas habría abstenido hasta hoy, y cuántos aciertos y errores se habrían ido con ellas.
- Qué significa `ts_emision`: qué campos existen, qué mide cada uno, y qué campo nuevo haría visible cuándo la fila se hizo pública.
- Qué corridas perdidas se descartan en vez de ejecutarse tarde: lista de las corridas que `Persistent=true` ejecutó tarde hasta hoy y qué produjo cada una.
- Y una cuarta, de la corrida 07: cuál es el campeón cuando sello y fuente discrepan, con el caso del 28-ago como ejemplo trabajado. El sello es "emitido antes", no "reproducible después": esa separación va escrita en la tarjeta.

### 2e. Diseño de la réplica
No código: un documento `GEMELO/diseno/replica.md` que convierta el modo sombra en mecanismo permanente. Debe contener la regla de desempate cuando dos máquinas sellan y difieren, qué máquina es titular y cómo se transfiere, cómo se detecta un sello duplicado antes de que llegue un Telegram doble, y cómo el importador de 2a participa en la puesta en marcha de la segunda máquina. Va a cola de decisiones.

### 2f. Deuda estadística y de pandas, si queda tiempo
- Los intervalos de ΔMAE de WS2b/WS3 (§34.9) están en otra escala. Recomputalos por bootstrap de bloques con clúster de día, publicá los correctos con errata al pie, y verificá si alguna conclusión cambia.
- La deuda `pd.concat` toca `motor.py`: producí el parche no aplicado con prueba byte-idéntica, como en 2b.
- Las cinco preguntas abiertas de WS4 (§33.8): respondé las que se puedan con datos; las demás quedan como tarjeta.

## 5. Bloque 3: la ruta al veredicto con la métrica correcta

Este bloque es donde el proyecto vuelve a ser ambicioso, ahora sobre una balanza calibrada.

### 3a. Reproducir la §2 del pre-registro dentro del harness
El pre-registro de GEMELO dice en su §9 que nada empieza antes que esto. Verificá si ya se hizo. Si no, hacelo: el harness de `backtest/` reproduce las cifras de la §2 (edge, bloques, quintiles, MAE, calibración) sobre los CSV actuales. Si difieren, manda el harness y el pre-registro recibe errata.

### 3b. El control lineal, primero y solo
El pre-registro dice que el control lineal regularizado es el juez. Construilo antes que cualquier retador: regresión regularizada sobre el conjunto de features causales de la §4.1 que estén disponibles hoy sin fuente nueva (SOX(t), SOX(t-1), tipos de cambio, VIX si ya se ingiere). Walk-forward con embargo, años de ajuste y prueba congelados antes de mirar, `auditor-lookahead` antes de la primera corrida. Métrica: MAE y CRPS bajo D3, dirección como secundaria. Compará contra el campeón 4.6.0 y contra predecir cero, con intervalo de clúster. Si el lineal no supera a predecir cero, la conclusión honesta es que los features disponibles no traen señal, y se publica así.

### 3c. Cuántos días sellados faltan bajo D3
Con el simulador calibrado y el DSR corregido: fecha estimada de veredicto para magnitud a 80% de potencia, con intervalo. Si es antes del 25-oct, decilo. Si no, decí cuándo.

## 6. Cierre

1. `GEMELO/resultados/bitacora_09.md` por frente: qué se hizo, qué se encontró con n e intervalo, dictamen del adversario, qué quedó abierto, errores propios.
2. `estado_epistemico.md` solo con afirmaciones que pasaron por el adversario.
3. `espera_firma.md` y `cola_decisiones.md` actualizados sin borrar lo que ya esperaba. Lo que esta corrida cerró se marca cerrado con fecha, no se borra.
4. Nuevo conteo de intentos con la lista de lo sumado.
5. Acta en `DECISIONES.md` con D1, D2, D3 aplicadas y las decisiones nuevas para Nicolás.
6. `ESTADO.md` dentro de sus 50 líneas.
7. `guardian-constitucion` dictamina el diff completo; `director-programa` verifica alcance y revierte lo que se salió.
8. Suite en verde con número final. Un frente que deja la suite en rojo se revierte y se documenta.
9. Sin push.

## 7. Lo que no se hace

- No se ejecuta la 5.1 ni se adelanta veredicto.
- No se construye el retador jerárquico (Kalman, pooling, Markov). Primero el juez lineal de 3b; el retador viene después y con V1-bis firmada.
- No se aplica ningún parche a archivos protegidos: se dejan como `.diff` con test.
- No se descarga nada en la ventana de sellado.
- No se agrega ninguna fuente de datos nueva.

Si una instrucción de este encargo te parece que es ella misma el defecto, no la ejecutes: anotala en la bitácora con la razón y seguí. La capa que caza esos errores no se relaja para cumplir el encargo.
