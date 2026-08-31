# Expedientes — Frente 6, lo que quedó colgando

Formato de expediente: la pregunta, las opciones reales, la evidencia
medida ahora, qué se rompe con cada opción, y una recomendación marcada
como tal. Ninguna de las decisiones de este documento se toma acá — cada
expediente termina donde empieza la firma de Nicolás.

---

## 6A. El IC del ΔMAE de WS2b y WS3 — EJECUTADO, no expediente

Esto no era una decisión pendiente, era un defecto con método conocido, así
que se ejecutó en vez de abrir expediente. Resumen (detalle completo y la
tabla de los 12 pares en la errata de `DECISIONES.md` del 31-ago-2026, y en
la bitácora de esta corrida):

Se recomputaron los 6 pares de WS2b (`GEMELO/experimento.py`) y los 6 de
WS3 (`GEMELO/ventana_larga.py`), ambos con `usar_cache=True` sobre los
datos cacheados en `GEMELO/cache/` (sin tocar ninguna base de datos), con
`inf.bootstrap_media` (la función correcta, ya construida en el WS5) en vez
de `inf.bootstrap_bloques` (la que `cl.comparar` sigue usando), y se
cruzó cada uno con `evaluacion.block_bootstrap` — una implementación
independiente, no circular — como control cruzado.

**Resultado: en los 12 pares, sin excepción, la decisión `ic_excluye_cero`
es idéntica entre la escala vieja (Sharpe), la escala corregida
(bootstrap_media) y el control cruzado.** Ninguna conclusión de WS2b ni de
WS3 cambia. Esto es exactamente lo que ya se había confirmado para los 12
pares del propio WS5 en la sección 34.9 de `DECISIONES.md` — el defecto era
real (el número impreso no era el intervalo de lo que decía ser), pero
nunca fue el tipo de defecto que cambia una decisión, porque el signo de
cada réplica de bootstrap no depende de si se divide por la desviación.

**Lo que NO se hizo:** los archivos `GEMELO/resultados/control_lineal.md`
/`.json` y `GEMELO/resultados/ventana_larga.md`/`.json` no se tocaron —
siguen publicados con el IC en escala Sharpe, con la errata en
`DECISIONES.md` apuntando a los números correctos. Es el mismo criterio que
el §34.9 ya adoptó para sí mismo: no reescribir un resultado publicado, se
documenta la corrección aparte.

**Nota metodológica declarada:** re-correr hoy no reproduce el n exacto de
los reportes originales del 26-ago (el track record sellado creció de 223 a
248 filas entretanto) — así que la comparación válida es "escala vieja vs.
nueva vs. cruzada, las tres sobre el mismo array de HOY", no "número de hoy
vs. número publicado en agosto". Esa comparación de método está limpia; una
comparación de cifra contra cifra publicada no lo estaría, y no se hizo.

---

## 6B. Lo que lleva meses abierto: abstención de sellos tardíos, `ts_emision`, y el efecto estampida

Tres preguntas relacionadas por el mismo eje (qué significa "a tiempo" para
una predicción, y qué pasa cuando algo llega tarde), empaquetadas juntas
porque comparten evidencia.

### 6B.1 — ¿Qué campo falta, y qué significa exactamente `ts_emision` hoy?

**La pregunta:** `snapshot.py` estampa `timestamp_utc` (= `ts_emision`)
ANTES de hacer el cómputo, y `creado_en = timestamp_utc` por construcción.
Ningún campo registra cuándo la fila se hizo VISIBLE — es decir, cuándo el
`commit` de esa fila realmente aterrizó y quedó consultable. Si un proceso
se congela entre estampar el timestamp y terminar de escribir (ya pasó:
el episodio del 06-ago, 44 minutos de congelamiento entre `timestamp_utc`
18:24 y el commit real ~19:08), una predicción con timestamp pre-congelamiento
podría, en teoría, terminar de escribirse DESPUÉS de que la sesión objetivo
ya abrió, y aun así pasar el chequeo de timing de la master rule porque el
chequeo mira `timestamp_utc`, no cuándo la fila se volvió visible.

**Opciones reales:**

1. **No hacer nada — mantener `ts_emision` estampado antes del cómputo,
   sin campo de visibilidad.** Es el estado actual. Funciona mientras el
   tiempo entre estampar y commitear sea corto (segundos, no minutos) — que
   es el caso normal. Falla exactamente en el escenario ya documentado del
   06-ago: un congelamiento largo entre el estampado y el commit.
2. **Agregar un campo `commiteado_en` (o `visible_en`), estampado en el
   momento real del `INSERT`/`COMMIT` de sqlite, además de `timestamp_utc`.**
   La master rule seguiría usando `timestamp_utc` para decidir qué se
   predijo antes de qué evento (eso no cambia — es la semántica correcta de
   "cuándo se decidió"), pero `commiteado_en` permitiría, en auditoría,
   detectar cuándo una fila tardó sospechosamente en aterrizar, sin
   necesitar reconstruirlo desde los logs como se hizo el 06-ago.
3. **Mover el estampado de `ts_emision` a justo antes de guardar, en vez de
   antes del cómputo.** Es la propuesta que ya está escrita en
   DECISIONES.md (Etapa 5.0.1, "Preguntas abiertas para el usuario") y que
   interactúa directamente con la master rule: cambiaría qué cuenta como
   "antes del evento" para toda fila futura. Es un cambio de LÓGICA DE
   EMISIÓN, no de auditoría — toca la Regla Cero.

**Qué se rompe con cada opción:**

- Opción 1 (no hacer nada): nada se rompe hoy; el riesgo sigue latente y
  sin instrumentación — si vuelve a pasar, se reconstruye a mano desde
  logs, como el 06-ago.
- Opción 2 (campo nuevo, aditivo): no rompe nada — es una migración
  aditiva, el patrón que `_asegurar_columnas` ya usa en todo el proyecto.
  No cambia ninguna semántica de verificación existente.
- Opción 3 (mover el estampado): puede CAMBIAR qué filas pasan el chequeo
  de timing de la master rule hacia adelante — es tocar la lógica de
  emisión, prohibida para cualquier agente sin la firma de Nicolás, y ya
  está marcada así en `DECISIONES.md`.

**Recomendación, marcada como tal:** la opción 2 (campo `commiteado_en`
aditivo) es la que no compromete nada y cierra la brecha de auditoría —
es puramente aditiva, de bajo riesgo, y no interactúa con la master rule.
La opción 3 queda exactamente donde ya estaba: propuesta formal, decisión
de Nicolás, sin tocar mientras el modelo 4.6.0 siga congelado.

### 6B.2 — La regla de abstención de sellos tardíos

**Estado:** ya es una propuesta formal completa en `DECISIONES.md` (Etapa
5.0.1, "Propuesta formal: regla de abstención de sellos tardíos"), con
evidencia medida: 17 filas con salto de sesión completa entre `available_at`
y la apertura objetivo aciertan el gap 4/17 (23.5%) contra 15/15 (100%) de
las filas frescas. Explícitamente **NO implementada**, porque cambiar qué
se emite es lógica de emisión → Regla Cero → modelo 4.6.0 congelado.

**Lo único que este expediente agrega, que no estaba dicho antes:** la
razón original para no implementarla ("cambiaría el modelo congelado") no
ha cambiado, pero el contexto sí — el switch a titular único ya ocurrió, y
GEMELO 6.0.0 ya está en marcha como la vía correcta para probar reglas de
timing sin tocar el campeón (`GEMELO/DISEÑO.md` §4.2 ya la incorpora como
candidata explícita, Nivel 5). **No hay nada nuevo que decidir acá hasta
que el retador llegue a esa etapa** — este expediente confirma que la
propuesta sigue vigente, sigue con su evidencia, y sigue esperando el mismo
lugar (GEMELO, no producción) donde ya estaba destinada a probarse.

**Recomendación:** ninguna acción nueva. Cerrar este punto como "sin
cambios desde 5.0.1, la vía de prueba ya es GEMELO" en vez de dejarlo
abierto indefinidamente como si faltara algo por decidir.

### 6B.3 — El efecto estampida de `Persistent=true`

**La pregunta:** los 6 timers systemd (`mki-*.timer`) tienen
`Persistent=true` — si la máquina estuvo apagada/suspendida a la hora de
un disparo, el timer se ejecuta al volver. Si la máquina estuvo abajo
durante la ventana de VARIOS disparos seguidos (por ejemplo, apagada toda
una tarde que cruza noticias 17:50, snapshot 18:15, reporte 18:25, backup
18:40), ¿los 6 se disparan todos a la vez al reactivarse la máquina? Si sí,
¿qué pasa cuando `mki_noticias.py`, `snapshot.py` y `mki_backup.py`
corren simultáneamente sobre las mismas bases?

**Evidencia medida esta noche: no existe ninguna.** Se buscó en
`DECISIONES.md`, en los 6 archivos `systemd/*.timer` y en `senales.py`/
`snapshot.py` cualquier discusión de riesgo de disparo simultáneo al
recuperarse de una caída, y no hay ninguna. Lo único documentado sobre
`Persistent=true` es que preserva el último disparo (`LAST`) a través de un
`wsl --shutdown`, validado el 14-ago — un hallazgo sobre PERSISTENCIA del
estado del timer, no sobre CONCURRENCIA de varios timers disparando juntos.
**Este expediente no encontró el riesgo documentado en ningún lado — lo
abre de cero, no lo hereda de un acta anterior.**

**Opciones reales:**

1. **No hacer nada, y confiar en que los jobs son idempotentes.**
   `ejecutar_snapshot(origen)` ya está descrito como idempotente en
   `snapshot.py`; si eso es cierto para los 6 jobs, un disparo simultáneo
   sería redundante pero no dañino. **No verificado esta noche para los 6
   jobs** — solo `snapshot.py` lo declara explícitamente.
2. **Auditar la idempotencia de los 6 jobs de forma explícita** (una
   corrida de solo lectura que dispare cada uno dos veces seguidas y
   compare el estado antes/después) antes de asumir que "no pasa nada".
3. **Agregar `RandomizedDelaySec` o una condición de bloqueo mutuo entre
   jobs** que dependan de las mismas bases, para que una recuperación tras
   caída los espacie en vez de dispararlos en el mismo segundo — esto SÍ
   toca `systemd/*.timer`, que es territorio de `ingeniero-plataforma`, no
   de este documento.

**Qué se rompe con cada opción:**

- Opción 1: si la suposición de idempotencia es falsa para algún job (por
  ejemplo, si `mki_backup.py` hiciera dos `git commit` seguidos con el
  mismo mensaje, o si `mki_noticias.py` gastara presupuesto de IA dos veces
  sobre el mismo lote), el costo aparecería silenciosamente — nadie lo
  sabría hasta verlo en `data/costos_ia.log` o en un commit duplicado.
- Opción 2: no rompe nada, es solo lectura; cuesta el tiempo de la corrida.
- Opción 3: cambia el comportamiento de los timers de producción — es
  exactamente el tipo de cambio que "cambiar el modo de emisión o tocar
  timers es operación de Nicolás, nunca de un agente" prohíbe hacer sin su
  decisión.

**Recomendación, marcada como tal:** opción 2 primero (auditar, no
implementar) — es de bajo costo, de solo lectura, y responde la pregunta
real antes de proponer cualquier cambio a los timers. Si la auditoría
encuentra un job no idempotente, ESE hallazgo es el que justificaría
escalar a la opción 3, nunca al revés.

---

## 6C. El alcance del pin de pandas con el Mac fuera

**La pregunta:** `requirements.txt` fija `pandas==3.0.3`. El pin nació, en
parte, para garantizar paridad numérica exacta entre el Mac (entonces
titular) y el PC (entonces sombra) durante la ventana de comparación —
"las dos máquinas corren pandas 3.0.3 y numpy 2.4.6 idénticos [...] con los
mismos insumos los números deben salir iguales" (`docs/SOMBRA.md`). El
switch ya ocurrió: el Mac quedó fuera, este PC es el único que emite y ya
no hay una segunda máquina con la que mantener paridad numérica cruzada.
**¿Sigue teniendo sentido el mismo pin, con el mismo alcance, ahora que la
razón de paridad cruzada que lo originó ya no aplica?**

**Evidencia medida:** el pin tiene una SEGUNDA razón, independiente de la
paridad Mac/PC y que NO desapareció con el switch — documentada en la
Etapa 5.0.3 §3 de `DECISIONES.md` ("Deuda declarada: `pd.concat` y el
futuro pandas 4"): un upgrade a pandas 4 cambiaría el default de `sort` en
`pd.concat`, lo que podría mover las β de `motor.py` (línea 215) EN
SILENCIO — sin que el test anti-look-ahead lo detecte, porque ese test
prueba ausencia de contaminación temporal, no estabilidad numérica entre
versiones de librería. La ampliación del 30-ago identificó un tercer sitio
antes no declarado: `backtest/baselines.py` (línea 141), que alimenta las
features de los veredictos escalonados B3-B5 del backtest. Son 5 líneas en
3 archivos (`motor.py:215`, `api/main.py:666-668`, `backtest/baselines.py:141`)
de 18 sitios de `pd.concat` en todo el repo. **Ningún documento une
explícitamente las dos razones del pin (paridad cruzada + protección de
`motor.py`) en una sola frase** — son dos hilos separados que este
expediente conecta por primera vez, sin resolverlos.

**Opciones reales:**

1. **Mantener el pin exactamente como está, con el mismo alcance total.**
   La razón de paridad cruzada ya no aplica, pero la razón de protección de
   `motor.py`/`api/main.py`/`backtest/baselines.py` sigue vigente
   independientemente de cuántas máquinas emitan. El pin no distinguía
   entre las dos razones al fijarse, así que no hay nada que "reducir" sin
   antes separar qué parte del pin protege qué.
2. **Actualizar pandas, pero aislar los 5 sitios de `pd.concat` con
   `sort=False` explícito** (el comportamiento actual, hecho explícito en
   vez de depender del default) antes de subir de versión. Esto separaría
   la protección real (los 5 sitios) del pin total (toda la librería),
   permitiendo actualizar el resto del código sin riesgo para esos 5
   puntos. Requiere tocar `motor.py:215` — que está bajo la regla dura de
   "motor.py intocable" — así que esta opción, aunque técnicamente
   simple (agregar un argumento a una llamada existente, no cambiar
   lógica), cae bajo la misma restricción y no la puede ejecutar un agente
   sin decisión explícita.
3. **Escribir el test de estabilidad numérica que falta** (uno que
   verifique que los 5 sitios de `pd.concat` producen el mismo orden con
   `sort=True` y `sort=False` sobre los datos reales de hoy, documentando
   si YA son estables — en cuyo caso el pin sería más conservador de lo
   necesario — o si de verdad dependen del orden — en cuyo caso el pin
   sigue siendo la protección correcta). Esto es de solo lectura/testing,
   no toca `motor.py`, y respondería la pregunta con evidencia en vez de
   con la razón original (que ya perdió la mitad de su fundamento).

**Qué se rompe con cada opción:**

- Opción 1 (mantener): nada se rompe; el costo es mantenerse atado a
  pandas 3.0.3 indefinidamente, incluso después de que la razón de paridad
  ya no aplica — deuda técnica que crece con el tiempo sin que nadie la
  mida.
- Opción 2 (aislar y actualizar): toca `motor.py` — prohibido para
  cualquier agente sin la firma de Nicolás, aunque el cambio en sí sea
  chico.
- Opción 3 (escribir el test primero): no rompe nada, y es el único camino
  que no requiere decidir nada todavía — solo mide.

**Evidencia adicional, encontrada sin buscarla, corriendo la suite completa
esta noche:** con pandas 3.0.3 YA INSTALADO (la versión pineada, no una
hipotética 4), `python -m pytest tests/ -q` emite `Pandas4Warning` en
exactamente los 3 archivos declarados como deuda —
`motor.py:215`, `api/main.py:666-668` (tres veces) y
`backtest/baselines.py:141` — con el texto: "Sorting by default when
concatenating all DatetimeIndex is deprecated [...] pandas will respect
the default of `sort=False`". Esto confirma en vivo, sin necesidad de subir
de versión para comprobarlo, que la deuda es real y ya está advertida por
la propia librería pineada — no es una preocupación hipotética sobre una
versión futura no probada.

**Recomendación, marcada como tal:** opción 3 primero. Escribir el test de
estabilidad de los 5 sitios de `pd.concat` es de bajo riesgo, no toca
código de producción, y convierte "quizás ya no haga falta el pin tan
amplio" de una intuición en un hecho medido. Con ese test en verde o en
rojo, la decisión entre las opciones 1 y 2 deja de ser una apuesta y pasa a
ser una decisión informada — que sigue siendo de Nicolás.
