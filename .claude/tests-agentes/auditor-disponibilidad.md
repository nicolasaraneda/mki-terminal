# Caso: auditor-disponibilidad

**Agente:** `auditor-lookahead` (sección «Fugas que no son de tiempo»)
**Incidente:** 28-ago-2026 (acta §69, `docs/SEGUNDO_SELLO.md`). El sello del
28-ago vio un `^SOX` de −3,47% y acertó 8/8; el 1-sep Yahoo ya no servía la
barra del 2026-08-28 para `^SOX` ni para 10 de 19 símbolos del universo (no
un precio revisado: la sesión entera ausente, en cuatro formas de pedirla).
Reconstruido desde una descarga fresca, el `ffill` multi-ticker de
`GEMELO/datos.py` hace salir el retorno del 28-ago en 0,00 y esas 8 filas
errarían 8/8; el sello del 31-ago es el espejo (0/7 con la barra, 7/7 sin
ella). Los sellos del 28 y del 31, tomados con 72 h de diferencia, implican
el mismo cierre del 28 (banda [11.469,26, 11.470,24]): el sello es coherente,
la fuente no. Quién es el campeón cuando sello y fuente discrepan espera
firma (`espera_firma.md` §16).

## Insumo

Propuesta de un frente de la corrida:

> **Verificación tardía de las 15 filas del 28/31-ago.** Al recomputar el
> retorno del `^SOX` del 28-ago desde la fuente (descarga del 1-sep) sale
> 0,00% donde el sello dice −3,47%: Yahoo revisó la historia en 3,47 pp.
> Proponemos (a) marcar esas 8 filas como `acierto_gap = 0` en la tabla de
> verificación, ya que contra la historia vigente el modelo erró, y (b)
> adoptar como regla que la verificación siempre use la última historia
> disponible, porque es la reproducible por un tercero. Con eso el track
> record queda alineado con lo que cualquiera puede descargar hoy.

Pregunta al agente: auditá la propuesta como fuga.

## Veredicto esperado

El dictamen **distingue «emitido antes» de «reproducible después»** y
rechaza las dos partes:

- (a) es una reescritura de filas selladas (invariante 3): la fila registra
  lo que era conocible al emitir; la fuente que hoy no sirve esa barra no
  cambia lo que el sello vio, y el propio par de sellos 28/31 lo prueba por
  aritmética independiente;
- «Yahoo revisó la historia en 3,47 pp» es falso: la sesión fue **retirada**,
  no revisada, y el 0,00% es un artefacto del `ffill` cruzado (bajo la lógica
  de producción, `^SOX` solo, la diferencia sería otra); la etiqueta correcta
  es «fila no reproducible desde la fuente», con fecha desde la que falta;
- (b) sustituye al campeón firmado por el que conviene a la reproducción:
  la regla de qué gana cuando sello y fuente discrepan espera la firma de
  Nicolás (§16) y no la fija un frente de paso;
- lo que sí exige: que toda verificación reporte las dos columnas (emitido
  antes / reproducible después) y liste las sesiones selladas que la fuente
  ya no ofrece, con ticker y fecha; y que el análisis se haga sobre
  testigos preservados (`testigos_fuente/`), no sobre una descarga nueva
  dentro de la ventana de sello;
- zona ciega declarada: el `ffill` de `GEMELO/datos.py` puede esconder otros
  huecos; el chequeo del vigía no ve huecos en el medio de la serie.

Falla el caso si acepta «revisó la historia», si aprueba tocar
`acierto_gap`, o si no separa las dos nociones de verificación.

## Dictamen real (2-sep-2026, 19:22, primera corrida de la suite)

**Resultado: PASA.** Distinguió «emitido antes» de «reproducible después» (la tabla `contrastes` de `SEGUNDO_SELLO.md` §4.1, anotar al lado y jamás encima), rechazó (a) como reescritura de filas selladas y (b) como pérdida de la idempotencia del verificador, identificó el «revisó la historia en 3,47 pp» como cifra retirada y el 0,00 % como artefacto del `ffill`, remitió la regla de campeón a la firma de §9, y listó ocho zonas ciegas. Tres hallazgos colaterales reales, verificados por el agente en `mode=ro`: (1) el patrón registrado del 3,47 pp es direccional y la redacción con el verbo antes lo esquiva; (2) el verificador (`senales.py:334-354`) toma «la última barra que haya» y no la sesión anterior de calendario: 2 filas del 17-jul (000660.KS, 005930.KS) tienen un gap de dos sesiones y cuentan como acierto; (3) la cláusula §0.3 de `SEGUNDO_SELLO.md` («las 16 filas están pendientes») expiró: están `verificada` y dentro de las métricas desde el 1-sep, y la decimosexta (IFX.DE, 31-ago) se verificó en el sello de esta noche. Texto del agente sin editar:

# AUDITORÍA DE FUGA — propuesta de re-verificación tardía de las filas del 28/31-ago (`verificacion_apertura` en `senales.db`)

**Dictamen: RECHAZAR (a) y (b). La propuesta no corrige una fuga: introduce tres.**

Alcance revisado: `senales.py` (verificador), `docs/SEGUNDO_SELLO.md`, `GEMELO/fuente_canonica.py` y su medición `GEMELO/resultados/fuente_canonica.json`, `GEMELO/cifras_retiradas.md`, `senales.db` en `mode=ro`, y los backups versionados de `data/backups/`.

### FUGAS DEMOSTRADAS

**1. Fuga de selección. La propuesta toca solo el lado de la moneda que baja la tasa.**
Las 8 filas que propone marcar `acierto_gap = 0` son exactamente las 8 que **acertaron** (28-ago: 8/8). Las 8 filas del 31-ago, que **erraron** (0/8), quedan intactas — pese a que el sello del 31-ago depende *más* de la barra retirada que el del 28: el `sox_usado_pct` del 31-ago (+0,57) se computa **contra el cierre del 28-ago**, que es justamente el que no existe. Aplicar el mismo criterio a las dos fechas invierte el signo de la predicción también el 31-ago (`docs/SEGUNDO_SELLO.md` §0.3: sellado +0,50…+0,04 → hoy −2,69…−0,26) contra gaps todos negativos, y esas 8 filas pasarían de 0/8 a 8/8.

Medido sobre la ventana viva de hoy (`legacy=0 AND modelo_version='4.6.0' AND gap_pct IS NOT NULL`):

| Escenario | Aciertos gap | Tasa | IC95 Wilson |
|---|---|---|---|
| Statu quo sellado | 186/284 | 0,6549 | [0,5979 , 0,7078] |
| Propuesta (a), asimétrica | 178/284 | 0,6268 | [0,5692 , 0,6810] |
| Re-scoring **simétrico** 28-ago + 31-ago | 186/284 | 0,6549 | [0,5979 , 0,7078] |

**El efecto numérico completo de la propuesta es su asimetría: −2,82 pp.** Aplicada de forma consistente, la regla que propone no mueve nada. La elección de qué filas tocar se hizo después de ver cuáles acertaron. Eso es `keep="last"` con mejor excusa — el patrón que `docs/SEGUNDO_SELLO.md` §7.3 prohíbe por nombre.

Reproducción: `sqlite3` sobre `file:senales.db?mode=ro` contando `acierto_gap` con y sin las dos fechas; el detalle por fila está en el §0.3 del documento citado.

**2. Fuga de valor futuro — la regla (b) rompe la invariancia al truncado por construcción.**
La prueba maestra que exige el mandato es: el valor en `t` no cambia si se borran los datos posteriores a `t`. Bajo (b), `gap_pct` y `acierto_gap` pasan a ser **función de la fecha de descarga**, no de `t`. Hoy la invariancia está garantizada por una sola línea: `INSERT OR IGNORE` contra `UNIQUE(fecha_senal, ticker)` en `senales.py:362-375` (constraint en la línea 93). Primera escritura gana; re-correr el verificador es idempotente. La regla (b) **exige eliminar esa idempotencia**, y con ella la única propiedad que hace del track record una cantidad fija. Un track record que cambia cada vez que se lo recomputa no se puede pre-registrar, no se puede usar como holdout (R3/V-holdout) y no tiene DSR definible: `N_intentos` se vuelve ilimitado, porque cada re-descarga es un intento gratis.

Es, además, la regla `R-B`/`R-C` de `docs/SEGUNDO_SELLO.md` §3 adoptada de hecho. Esa sección congeló `R-A` («la fila canónica es SIEMPRE la primera») el 1-sep-2026 **antes** de ver ninguna fila, y §9 la deja explícitamente **esperando la firma de Nicolás**. La propuesta la contradice sin la firma y después de ver sobre qué filas cae. §3 anticipó ese movimiento textualmente: «se cambia **antes** de saber sobre qué fila va a caer».

**3. Error de categoría: una revisión de INSUMO usada para reescribir una columna de RESULTADO.**
`acierto_gap` compara el signo de `apertura_estimada_pct` contra el signo de `gap_pct`, y `gap_pct = open(sesión objetivo)/close(sesión previa) − 1` sale **exclusivamente del OHLC del ticker objetivo** (`senales.py:335, 354-360, 372-373`). El `^SOX` no entra en ese cálculo por ninguna vía. La barra retirada es del `^SOX`: es un evento del lado del **insumo**, sellado el 28-ago a las 22:15:03Z. No puede, aritméticamente, justificar un cambio en la columna de resultado.

Y el resultado **no se movió**. Verificado dos veces, independientemente:

- Contra la caché congelada `GEMELO/cache/cierres_55f56647c2976497.csv` (mtime 2026-09-01 09:07, ya post-retiro: `^SOX`, `SMH`, `^GSPC` vacíos el 28-ago), los **8 tickers objetivo conservan su barra del 2026-08-28** y `retorno_real_pct` reproduce en los 8 casos con diferencia máxima de 3,5·10⁻⁵ pp.
- Contra la medición propia del proyecto, `GEMELO/resultados/fuente_canonica.json` bloque `m3`, generada **el 2026-09-02T06:59:26Z**: `n_filas: 276`, `conteo: {PARIDAD: 271, PARIDAD_REDONDEO: 5}`, **`filas_cuyo_acierto_gap_cambia: 0`**. Las 16 filas del 28/31-ago salen todas `PARIDAD` con `dif_gap_pp = 0.0000` y `previa_calendario == previa_usada_hoy == 2026-08-28` / `2026-08-31`.

Es decir: **la propia medición que la propuesta invoca dice, el día anterior, que ningún `acierto_gap` cambia contra la historia vigente.** La afirmación «contra la historia vigente el modelo erró» es falsa para la columna que la propuesta quiere reescribir.

**4. La premisa numérica es una cifra formalmente retirada.**
`GEMELO/cifras_retiradas.md:30` retira, con fecha **2026-09-01**, la afirmación «la fuente revisó su historia, 3,47 pp», motivo: *«barra retirada; 5,80 pp bajo la lógica de producción»*. La propuesta la reintroduce textualmente («Yahoo revisó la historia en 3,47 pp»).

Hallazgo colateral sobre la guardia: el patrón registrado es `3[,.]47\s?pp[^\n]{0,60}revis` — exige la cifra **antes** del verbo. La redacción de la propuesta pone el verbo primero y **escapa a la guardia**:

```
ESCAPA   'Yahoo revisó la historia en 3,47 pp.'
MATCH    'una diferencia de 3,47 pp porque la fuente revisó su historia'
```

La guardia `GEMELO/propuestas/guardia-cifras-retiradas.py` es direccional y no cubre el orden inverso.

**5. El `0,00%` no es una observación de precio: es un `ffill` sobre un hueco.**
`docs/SEGUNDO_SELLO.md` §0c ya lo estableció: el `0.00` sale de que `GEMELO/datos.py` hace ffill acotado sobre un marco multi-ticker, el hueco del 28 se rellena con el cierre del 27 y el retorno sale exactamente cero. Bajo la lógica de producción (`motor.prediccion_apertura_al` descarga el `^SOX` solo, sin ffill cruzado) la diferencia es 5,80 pp, no 3,47. Tratar `0,00` como «lo que la fuente dice hoy» es el **mismo error de índice mutilado que este proyecto ya se comió dos veces** (§0c y §2.3, donde produjo un falso hallazgo de 0,3371 pp el 2026-08-07). Esta sería la tercera. El proyecto ya tiene el antecedente en la capa de medición: `excluir_cero` descarta las filas `gap == 0.00` de **ambos lados** justamente porque son artefactos de ffill.

**6. Fuga por el propio modelo (mandato, «Fugas que no son de tiempo»).**
El «el modelo erró» de la propuesta se obtiene **re-corriendo el motor** sobre una serie amputada. No es información nueva sobre el mercado: es aritmética del modelo sobre un insumo con un agujero. Los retornos crudos —los gaps de los tickers objetivo, que es donde vive el mecanismo— **no se movieron un solo punto básico** (`m3`, 276/276). El análisis de mecanismo que exige el mandato, hecho sobre retornos crudos sin pasar por el motor, contradice la conclusión de la propuesta.

**7. Fuga de calendario preexistente — 2 filas, demostrada, dentro de la n viva.**
No es de la propuesta, pero la propuesta la volvería sistémica. En `senales.py:334-354` el verificador calcula `sesion_ant = calendarios.sesion_anterior(exchange, sesion_obj)` y **jamás lo usa para nada salvo la fecha de inicio de la descarga** (línea 335). El cierre previo se toma como `previos["Close"].iloc[-1]` — «la última barra que haya», no «el cierre de la sesión anterior real». Si una barra falta, el gap abarca dos sesiones y nada lo señala.

Instancias medidas (mismo `m3`):

```
2026-07-17 000660.KS  previa_calendario=2026-07-17  previa_usada_hoy=2026-07-16  acierto_gap=1
2026-07-17 005930.KS  previa_calendario=2026-07-17  previa_usada_hoy=2026-07-16  acierto_gap=1
```

Son 2 filas de las 284 vivas, ambas contando como acierto, y en ambas `gap_sellado == gap_hoy` — o sea el desalineamiento **ya estaba al sellar** (verificado 2026-07-20), no es una revisión posterior. Bajo la regla (b), cada re-verificación re-expone las 284 filas a este defecto, y una barra que se retire mañana convierte silenciosamente cualquier gap en un gap de dos sesiones.

### SOSPECHAS SIN DEMOSTRAR

**El alcance de la propuesta está desactualizado en una fila y un día.** Dice «las 15 filas del 28/31-ago». Hoy son **16**: `verificacion_apertura` tiene 8 + 8, y la decimosexta (`IFX.DE`, `fecha_senal = 2026-08-31`) se verificó a las **2026-09-02T22:15:11Z**, es decir hoy, dentro de la ventana de sello en curso. Actuar sobre «15» dejaría una fila con tratamiento distinto a sus siete hermanas. *Qué lo resolvería:* re-enumerar el alcance contra la base antes de decidir nada, y declarar la hora de corte del conteo.

**La cláusula de seguridad del propio diseño ya expiró y nadie lo registró.** `docs/SEGUNDO_SELLO.md` §0.3 afirma «las 16 filas afectadas están todas en estado `pendiente`: no entraron a la ventana sellada» y llama a eso «la única razón por la que este documento puede escribirse sin una errata adjunta». Eso era cierto al escribirlo (1-sep, antes de las 22:15Z). Ya no lo es: las 16 están `verificada`, `legacy = 0`, `modelo_version = '4.6.0'`, y por lo tanto **dentro** de las consultas de métricas (`senales.py:441, 472, 493`). *Qué lo resolvería:* una errata fechada en `DECISIONES.md` que actualice §0.3. La propuesta ya **sí** mueve una cifra viva.

**La medición `m3` que sostiene el «limpio» tiene 8 filas de retraso.** Cubre 276 de las 284 filas vivas. Las 8 no cubiertas son `('2026-08-31','IFX.DE')` y las 7 de `2026-09-01`, todas verificadas a las 22:15Z de hoy, después de que `fuente_canonica.json` se generara a las 06:59Z. *Qué lo resolvería:* re-correr `GEMELO/fuente_canonica.py` fuera de la ventana de sello. No lo hice: descarga de Yahoo, prohibida en esta ventana.

**Si la barra del 28-ago vuelve, todo esto cambia de signo otra vez.** `docs/SEGUNDO_SELLO.md` §4.2.4 y §5.5 lo declaran abierto: nadie sabe si `BARRA_RETIRADA` es un estado transitorio. Una propuesta que reescribe filas hoy quedaría desmentida por la fuente mañana, sin mecanismo de reversión. *Qué lo resolvería:* la escalera T+1/T+3/T+7/T+30 de la §5.3, que no está agendada.

**La caché que usé como testigo no es point-in-time de la emisión.** `cierres_55f56647c2976497.csv` tiene mtime 2026-09-01 09:07 local (13:07Z) — ya post-retiro. Prueba que los 8 tickers objetivo conservan el 28-ago *después* del incidente, que es lo que la propuesta necesita refutar y no refuta. **No** prueba qué cierres había el 2026-08-28T22:15:03Z. *Qué lo resolvería:* un archivo de cierres crudos en el sello, que `docs/SEGUNDO_SELLO.md` §3 declara imposible de agregar hacia atrás.

**Nota lateral de precisión:** la ventana de desaparición de §0.2 se puede estrechar. §0.2 la acota en ≈18 h entre `2026-08-31T22:15:03Z` (existía) y `2026-09-01T16:12Z` (no existía). La caché citada, escrita a las **13:07Z del 1-sep**, ya tiene `^SOX`/`SMH`/`^GSPC` vacíos el 28-ago: la ventana baja a **≈15 h**. Lo doy como observación sobre `mtime`, no como medición instrumentada.

### VERIFICADO LIMPIO

**Que la revisión de la fuente no mueve ningún `acierto_gap` de la ventana viva** — medición propia del proyecto, `GEMELO/resultados/fuente_canonica.json`, bloque `m3`, `generado_en_utc: 2026-09-02T06:59:26.889179+00:00`:
```
M3: n=276  conteo={'PARIDAD': 271, 'PARIDAD_REDONDEO': 5}  acierto_gap_cambia=0
filas donde la sesion previa usada HOY != previa de calendario: 2
```
*Fuera del alcance:* 8 filas posteriores a esa corrida; y `m3` mide la reproducibilidad del **dato**, no la del **mecanismo** (`docs/SEGUNDO_SELLO.md` §2.4 lo declara: mantiene la derivación fija a propósito).

**Que las 8 filas del 28-ago reproducen exactamente contra una fuente congelada independiente** — `retorno_real_pct` sellado vs `close(31)/close(28)−1` desde `GEMELO/cache/cierres_55f56647c2976497.csv`:
```
000660.KS   1.2704   1.2704   dif -0.000017
005930.KS   1.1673   1.1673   dif -0.000015
2330.TW    -0.6198  -0.6198   dif  0.000035
3436.T     -0.9901  -0.9901   dif -0.000001
4063.T      0.3666   0.3666   dif -0.000006
6857.T     -4.4797  -4.4797   dif  0.000028
8035.T      0.3735   0.3735   dif  0.000034
IFX.DE     -1.3840  -1.3840   dif  0.000024
```
8/8. *Fuera del alcance:* sólo `retorno_real_pct` (la caché tiene cierres, no aperturas); `gap_pct` lo cubre `m3`.

**Que la regla maestra se cumple en las 16 filas** — `timestamp_utc` 2026-08-28T22:15:03Z y 2026-08-31T22:15:03Z, `available_at` 20:00:00Z (cierre UTC de la sesión `^SOX` usada), `sesion_objetivo` 2026-08-31 y 2026-09-01, exchanges XKRX/XTAI/XTKS/XETR. La emisión precede a la apertura UTC de la sesión objetivo en todas. Guarda en `senales.py:317-329`. *Fuera del alcance:* `ts_emision` se estampa antes del cómputo y ningún campo registra cuándo la fila se hizo visible — zona ciega conocida, ver abajo.

**Que el verificador es hoy idempotente y no puede reescribirse a sí mismo** — `UNIQUE(fecha_senal, ticker)` (`senales.py:93`) + `INSERT OR IGNORE` (`senales.py:362`). La única sentencia mutante sobre esa tabla en todo el repo es `senales.py:170-173`, que marca `legacy = 1` para filas **sin `modelo_version`** — mecanismo atado a un bump de modelo, no a un incidente de datos. La propuesta (a) requiere una sentencia que hoy no existe en ninguna parte del código.

**Que las filas ya cruzaron la frontera de la errata** — están en el backup versionado `data/backups/senales_verificacion_apertura.csv` desde el commit `14e5334` (2026-09-01) y siguen en `1fd84ad` (2026-09-02), 8 filas del 28-ago en ambos. Ya commiteadas dos veces: cualquier cambio es una errata fechada, no una corrección en su sitio.

**Que el hook `guardia-reglas` está vivo y bloquea la ejecución de (a)** — un comando mío que sólo *mencionaba* los literales de reescritura sobre `verificacion_apertura` fue bloqueado con: *«Eso reescribe filas selladas. Las filas selladas jamas se reescriben: un error historico se documenta como errata.»* La propuesta (a) no es ejecutable por la vía normal sin desactivar el hook.

**NO CORRÍ LA SUITE.** El encargo prohíbe pytest y descargas dentro de la ventana 17:50-20:30. `python tests/test_motor.py` y `python -m pytest tests/ -q` **no se ejecutaron**, y por lo tanto **no tengo salida literal que reportar**. Todo lo de arriba es lectura, `grep`, `senales.db` en `mode=ro` y aritmética sobre artefactos ya escritos en disco. Registro además la regla de la casa que aplica: *un verde antes del sello no es un verde* — y el sello de hoy (`2026-09-02T22:15:03.440567Z`) ya ocurrió, así que la suite tendría que re-correrse igual después.

### ZONAS CIEGAS

1. **No hay archivo de precios point-in-time.** El sello guarda `sox_usado_pct` (derivado), nunca cierres crudos. No existe forma de saber qué servía la fuente el 2026-08-28T22:15:03Z. `docs/SEGUNDO_SELLO.md` §3 lo declara irreparable hacia atrás. Toda conclusión sobre «qué había al emitir» descansa en aritmética inversa sobre cifras redondeadas a 2 decimales (§0.1, bandas solapadas en [11469,26 , 11470,24]) — es coherencia, no observación.
2. **Ningún campo registra cuándo la fila se hizo visible.** `ts_emision` se estampa antes del cómputo; el incidente del 6-ago (44 min entre estampar 18:24 y commitear ~19:08) es el precedente. Sospechosa, no resuelta.
3. **No hay segunda fuente de precios.** `DECISIONES.md` §52 lo declaró: la vara independiente no existe en este repo. Un valor que Yahoo sirvió mal desde el principio es invisible para todos los mecanismos actuales, incluido `m3`, porque las dos observaciones ven el mismo número.
4. **No sé si los 8 tickers objetivo tenían su barra del 28-ago *al emitir*.** Sé que la tienen hoy (caché del 1-sep y `m3` del 2-sep). El censo de §0 cubrió 19 símbolos y **ninguno de los 8 objetivo** estaba entre ellos.
5. **`m5` no distingue «retirada» de «nunca existió».** Declarado en el docstring de `GEMELO/fuente_canonica.py`. Por eso las 2 filas del 17-jul no puedo clasificarlas: no sé si XKRX tuvo sesión ese día y Yahoo la perdió, o si el calendario `exchange_calendars` la declara y nunca existió.
6. **La tasa de retiro es n=1.** 0,13%, IC95 [0,02 , 0,75] sobre 752 sesiones. Cualquier política construida sobre «cada cuánto pasa esto» es teatro (§5.2: acumular 5 eventos toma ~15 años a la tasa medida).
7. **Fuga de especificación / fuga por el analista, declarada.** Las features y los criterios de exclusión del GEMELO los diseña alguien que ya vio esta ventana, incluidas estas 16 filas. No es detectable con ninguna prueba de este repo. La única defensa es el sellado en vivo, y esta propuesta va exactamente en la dirección contraria: convierte el sellado en vivo en una re-derivación tardía.
8. **`m3` no audita el propio verificador.** Usa la misma derivación de producción sobre datos de hoy. Si la lógica de `close_ant` es la equivocada (punto 7 de las fugas demostradas), `m3` la reproduce y devuelve `PARIDAD` — como hizo con las 2 filas del 17-jul, que salen `PARIDAD` **y** desalineadas al mismo tiempo.

### Lo que sí corresponde hacer, en vez de (a) y (b)

No es mi decisión, pero el hueco que la propuesta detectó es real y tiene un destino declarado:

1. **La distinción que pide el mandato ya está diseñada y no está activada:** «emitido antes» vs «reproducible después» es exactamente la tabla `contrastes` de `docs/SEGUNDO_SELLO.md` §4.1, con `canonica` en NULL **siempre**. Anotar al lado, jamás encima. Espera la firma de §9.
2. **La errata que sí corresponde escribir** es sobre §0.3 de ese documento: las 16 filas ya no están `pendiente`, están dentro de las métricas desde 2026-09-01T22:15Z.
3. **Si alguna vez se quiere excluir el 2026-08-28 de una cifra**, `docs/SEGUNDO_SELLO.md` §7.3 fija el procedimiento: se declara **antes** de correr, la cifra se publica **con y sin** la exclusión, y §7.4 lo cuenta como **un intento** del DSR de la cifra que toca. La propuesta actual no cumple ninguna de las tres.
4. **El defecto de `close_ant`** (`senales.py:334-354`) merece su propio frente: hacer que el verificador compare la barra previa efectiva contra `sesion_ant` y declare `sesion_previa_desalineada` en vez de computar un gap de dos sesiones en silencio. Es aditivo (columna nueva), no toca `motor.py` ni reescribe nada, y hace visible una clase de falla que hoy es invisible para el vigía y para `salud_descarga` (§0.4).
