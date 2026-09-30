# Pre-mortem del `director-programa` sobre el encargo de la corrida 15

> Archivado por el orquestador tal como lo devolvió el agente. Lanzado a las 21:58 de Chile del
> 29-sep-2026 (hora de `date`), devuelto antes de las 22:07. Sólo lectura: el agente no abrió
> ninguna base ni leyó `data/sonda_cierre.csv`. Qué hizo el orquestador con cada instrucción
> marcada está en `GEMELO/resultados/bitacora_15.md`, sección 0.4.

**Veredicto: ADELANTE CON TRES INSTRUCCIONES MARCADAS.** El encargo está bien construido y su orden de prioridad (§12) es correcto. Pero el bloque 1.2, tal como está escrito, es la instrucción más peligrosa que ha pasado por aquí: puede apagar el sellado de todos los días.

## 1. Modos de falla, por costo

**F1 — La guarda (b) deja de sellar TODOS los días (§4.2). Costo: el activo nº 1, una sesión por día, irrecuperable.**
Medido: `snapshot.py:133` fija `available_at = calendarios.cierre_utc("XNYS", sox_fecha)`. La emisión de las 18:15 Chile es **1 h 15 min** después del cierre de NYSE (18:15 Chile = 21:15 UTC hoy / 22:15 UTC en invierno; cierre 20:00 / 21:00 UTC — la brecha es la misma todo el año; `GEMELO/datos.py:74` la declara). El único margen que "el código ya usa" es `calendarios.py:94 sesion_ya_cerro(..., margen_horas=2.0)`. **Con ese margen, la guarda (b) rechaza el sello todas las noches.** Y el encargo empuja hacia él: «el margen que el código ya use para "liquidado", si existe». Peor: `GEMELO/datos.py:57-59` ya dejó escrito que ese margen de 2 h es criterio de VERIFICACIÓN, no de INSUMO, y que aplicado a insumos descalifica series legítimas. La instrucción presupone algo que el proyecto ya refutó.
*Lo que hay que hacer en su lugar:* (b) es aritméticamente idéntica a (a) aplicada al sellar. `sox_fecha` cerró al emitir **si y sólo si** `available_at <= ts_emision`. Escribirla así — mismo cálculo, margen cero, sin `sesion_ya_cerro` — hace desaparecer la pregunta del margen y garantiza que el 28-sep no sella (av > ts) y que un día normal sí.
*Señal temprana:* el test de 1.2 a las 18:15 Chile debe ser una aserción de **SELLA**, escrita antes del código, no ajustada al resultado. Y mañana 18:15: `data/snapshot.log` sin `{'snapshot': False, ...}` y el vigía de las 19:00 en silencio.

**F2 — El cierre lee filas de madrugada por la suite, y el rojo que va a aparecer no se puede clasificar (reglas 1 y 5 vs. §11.5). Costo: bloquea el cierre o rompe una regla firmada.**
`tests/test_sonda_cierre.py:122-138` lee **todas** las filas del `data/sonda_cierre.csv` real y aplica `sesion_atribuida()` a cada una. Después de las 01:05 eso son filas de madrugada: la suite de cierre viola la regla 5 de forma mecánica. Y es el test con más probabilidad de ponerse rojo esta noche — son las primeras filas post-medianoche de la historia, y su propio docstring dice «si algún día este test falla, hay filas de dos semánticas». Bajo §91.6 hay que clasificarlo, y clasificarlo exige leer filas de madrugada. Deadlock.
`tests/test_sello_dinero.py:596-598` abre `S.RUTA_DB` **real** en `solo_lectura=True`: correr la suite entre 00:15 y 00:50 viola la regla 1 al pie de la letra.
*Señal temprana:* el orquestador anota en la bitácora, ANTES de las 00:15, (a) la duración de reloj de la suite de §0.3 — la regla es que ninguna suite esté **corriendo** en el tramo, no que no se lance; el último lanzamiento es 00:15 menos esa duración; y (b) la interpretación declarada de «ningún agente lee filas de madrugada» = lectura por un agente, no E/S de un test. Si no la declara antes, la declarará a las 03:00 para poder cerrar, y eso es escribirse el permiso.

**F3 — Éxito compuesto: el README apunta al CSV y el backup deja de commitearlo (§5.1 + §7).** §90.3 manda que el README remita al CSV versionado justo cuando §90.8 instala una guarda que puede impedir su commit — y el día que la guarda (b) legítimamente no selle, las dos se disparan juntas. La ventana sin copia versionada pasa de ~25 min a ~24 h, en la máquina sin réplica cuyo SSD ya falló una vez. *Regla:* ante un no-sello declarado, `mki_backup.py` commitea igual y lo escribe en su log; nunca salta el día en silencio. §90.8 pide ORDEN, no abstención.

**F4 — La regla 3 de la noche es ambigua y decide sola el 60 % del encargo.** Medido: `GEMELO/sonda_cierre.py` **no importa nada del repo** (sólo stdlib, xcals, pandas, yfinance). `dinero/sello_dinero.py` importa `dinero.*`, `backtest.datos` (lazy, :499) y `backtest.inferencia`; **nunca** `senales`, `snapshot`, `mki_vigia`, `mki_backup` ni `backtest/linea_base`. Bajo la lectura sensata, la regla 3 no bloquea nada. Bajo la lectura literal («módulos que importan el sellador»), `api/main.py` importa `senales` (:23) y `sello_dinero` (:1354), y `scripts/generar_readme.py` importa el sellador y lo modifica el bloque 2 — o sea bloquearía las prioridades 2 y 3 enteras. *Señal temprana:* el grep de la regla 3 pegado en la bitácora con la lectura elegida, por escrito, antes de aplicar nada.

**F5 — El worktree verde por la razón equivocada (§4, §11.5).** La suite en worktree falla por artefactos gitignorados ausentes; un rojo ahí tiene dos causas. Con §91.6 recién firmada, el camino cómodo es clasificar «artefacto ausente» un rojo que es regresión en `senales.py`, y aplicarlo al camino de sellado a las 02:00 con Nicolás durmiendo. *Señal temprana:* copiar las bases al worktree ANTES, y exigir que la suite vuelva a correr **en el árbol real** después de aplicar, con el número y las tres huellas sha256.

**F6 — El bloque 0 llega al 00:55 sin adversario.** Es el riesgo más probable y el más barato: el encargo tiene válvula. *Señal temprana:* si a las 23:45 `regla_58.md` no tiene borrador completo, se manda incompleto al adversario en vez de tarde. Y ojo con la frontera: la franja de tarde de esta noche tiene timestamps del **30-sep UTC** (00:05Z–03:35Z); el corte es de timestamp (`04:00:00Z`), no de fecha. Un filtro «excluir el 30-sep» pierde la noche de hoy — es el error A10 de la corrida 14 otra vez.

**F7 — El punto 6 del bloque 0 pide una verificación que la fuente no puede dar.** `man systemd.timer` documenta `Persistent=`, no la semántica de `last_trigger` en memoria tras un `restart`. La hipótesis es plausible pero el man no la confirma ni la refuta, y probar en una unidad real está prohibido. *Salida:* el procedimiento se escribe robusto a **ambas** semánticas (hacerlo un sábado / a una hora en que un disparo inmediato no quema sesión), y la incertidumbre va rotulada. No se escriba «verificado contra el manual».

## 2. El vigía (§4.5): **VA A TARJETA**

Dos razones, la segunda decisiva. (a) Es un cambio de comportamiento en el único módulo del bloque 1 que **habla por Telegram**, la misma noche en que se instala una guarda que puede dejar de sellar; el vigía es la alarma que avisaría de F1, y no se toca la alarma la misma noche que lo vigilado (es el análogo del «un cambio por noche al sellador», §87.3). (b) Además el cambio, tal como está redactado, es una **regresión**: `mki_vigia.py:91-101` alerta hoy por `available_at == timestamp_utc` — la rama del `except` de `snapshot.py:134`, que es un defecto distinto y real. Reemplazarlo por «orden (`av <= ts`)» apaga esa detección. La tarjeta debe decir: los dos chequeos, no uno; y la errata de «launchd» viaja con ella. Con (a) y (b) aplicadas, `av > ts` ya no puede nacer, así que la urgencia es baja.

## 3. Qué cortaría

**De acuerdo con el orden de §12, con una corrección: el bloque 4 sube a la par del 2.** Es barato y cierra el agujero de réplica que F3 abre; dejarlo en el puesto 4 detrás del bloque 2 es aceptable sólo si el bloque 2 termina temprano. Primero cae el **bloque 3** (ya está último y el encargo dice no empezarlo a medias — correcto), después el **6.6 (`bifurcaciones`)**, después el **6.4 (8035.T)**, que es descriptivo y no vence. Lo que **no** se corta nunca es la suite del árbol real al cierre (§11.5): sin ella, el bloque 1 queda aplicado sin evidencia.
**Lo urgente que queda postergado por decir sí a todo esto:** la réplica (`cola_decisiones.md` §1) y las dos firmas del pre-registro secuencial (§2a-ter y el MDE) antes del **19-nov**. Van siete semanas y tres corridas seguidas consumidas por las consecuencias del despertar. Eso no necesita una corrida, necesita una firma; pedírsela a Nicolás en paralelo, no después.

## 4. Instrucciones marcadas (el orquestador no las ejecuta sin anotarlas)

| # | Instrucción | Razón |
|---|---|---|
| **B1** | §4.2 (bloque 1.2): «cierre de NYSE + margen que el código ya use» | F1. Presupone un margen que el proyecto ya refutó como criterio de insumo; con 2 h apaga el sellado diario. Reescribir como `available_at <= ts_emision`, margen cero. |
| **B2** | Regla 3 de la noche | F4. Ambigua en los dos sentidos; decide sola si el bloque 1 y el 2 se aplican. Resolver por escrito con el grep pegado. |
| **B3** | Reglas 1 y 5 vs. §11.5 | F2. La suite abre la base real del sellador y lee el CSV completo de la sonda; las tres instrucciones no pueden cumplirse a la vez sin una interpretación declarada de antemano. |
| **B4** | §4.5, el vigía | Regresión escondida en «pasa a probar orden»: apaga la detección de `av == ts`. Va a tarjeta con las dos condiciones escritas. |
| **B5** | §3 bloque 0, punto 6: «verifica contra `man systemd.timer`» | F7. El manual no puede dictaminar esa semántica y probarla está prohibido. Resultado obligatorio: PROPUESTA robusta a ambas hipótesis. |
| **B6** | §5.1 + §7 | F3. Nadie conectó que el README remite al CSV que el bloque 4 puede dejar de commitear. |

**Sobre el norte:** nada en este encargo lo mueve. Todo él es consecuencia del despertar del 28-sep — deuda, no ambición — y está bien que así sea mientras el nº 1 de la jerarquía (que el titular siga sellando) esté en juego. Justamente por eso F1 es la única línea de esta noche que puede hacer más daño que el incidente que la originó.

**Nota de máquina:** el encargo dice «esfuerzo alto»; el usuario fijó «xhigh». Manda la máquina, queda anotado. El acta §91.1 nombra `encargo_corrida_15_noche_v2.md`; el archivo lanzado es `/home/nicolasaraneda/encargo.md` — misma pieza, errata de nombre, se anota.
