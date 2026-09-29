# Dictamen del `auditor-lookahead` — el sello del 28-sep-2026 emitido con NYSE abierto

**Corrida 14, bloque 0-bis.3.** Encargo: decidir si las filas que el riel de medición selló durante
el despertar del PC son «filas inválidas que entraron como válidas», porque de eso dependía si los
bloques 2 y 3 del encargo (que publican cifras) se ejecutaban.

Transcripción por el orquestador del dictamen del agente. **El veredicto va literal.** Todo acceso a
bases fue `mode=ro`; el auditor verificó sha256 de `senales.db` y `noticias.db` idénticos antes y
después de su auditoría, incluida una corrida completa de la suite.

## VEREDICTO

```
VEREDICTO: FILAS INVÁLIDAS ENTRARON COMO VÁLIDAS
```

**Consecuencia ejecutada: los bloques 2 y 3 del encargo NO se ejecutaron.**

## Lo MEDIDO

Todos los hechos que el orquestador había levantado fueron verificados uno por uno y resultaron
verdaderos, con **una sola corrección de alcance** (abajo). Lo que el auditor agregó:

1. **El instante y la ventana.** `calendarios.cierre_utc('XNYS','2026-09-28')` = `2026-09-28T20:00:00Z`.
   El sello es `2026-09-28T17:42:58.943983Z`: **2 h 17 min 02 s ANTES del cierre**. Al momento del
   dictamen (`19:45:47Z`) ese cierre **todavía no había ocurrido**.
2. **La anomalía es única, confirmada por DOS fuentes independientes.**
   `SELECT fecha, COUNT(*) FROM senales_ticker WHERE available_at > timestamp_utc GROUP BY fecha`
   devuelve sólo `('2026-09-28', 24)`. Y el CSV versionado `git show HEAD:data/backups/senales_senales_ticker.csv`
   da **0 inversiones** antes del evento.
3. **`-1,63` no puede ser el cierre del 28-sep**, y la prueba es deductiva: un valor no puede ser el
   cierre de una sesión que no ha cerrado. El mecanismo, en tres líneas: `motor.py:43` descarga con
   `period="3y", interval="1d"` y con la sesión abierta yfinance devuelve una barra **etiquetada con
   la fecha de hoy** cuyo `Close` es el último precio negociado; `motor.py:60` recorta con
   `df[df.index.date <= fecha]`, **inclusive**, así que la barra parcial sobrevive; `motor.py:87`
   devuelve el último movimiento no-cero y su fecha índice, de donde sale `sox_fecha='2026-09-28'`.
   Ese `sox_fecha` **prueba** que la barra del 28 se usó: si hubiera sido un ffill del cierre del 25 el
   retorno habría sido 0 y la función la habría salteado.
4. **Huella empírica en disco, sin bajar nada.** Última fila de `data/sonda_cierre.csv`:
   `2026-09-28T17:42:55.212430+00:00,13:42,2026-09-28,SOXX,2026-09-28,1,560.299988,7` — el mismo
   proveedor, **3,7 s antes del sello**, ya daba `ultima_fecha_close = 2026-09-28`. La sonda que
   Nicolás instaló para medir «a qué hora existe el cierre» capturó el fenómeno en el acto.
   Corroboración segunda: `data/backups/sello_dinero_ext/ext_2026-09-28.meta.json`, congelado el mismo
   segundo, estampa `available_at_utc: "2026-09-28T20:00:00+00:00"` — la misma falsedad en el otro riel.
5. **Las 8 predicciones son exactamente `beta × (−1,63)`**, dentro del redondeo de la beta sellada:

   | ticker | beta | `beta × (−1,63)` | sellado |
   |---|---|---|---|
   | 000660.KS | 0,81 | −1,3203 | −1,32 |
   | 005930.KS | 0,59 | −0,9617 | −0,97 |
   | 2330.TW | 0,32 | −0,5216 | −0,53 |
   | 3436.T | 0,66 | −1,0758 | −1,08 |
   | 4063.T | 0,31 | −0,5053 | −0,50 |
   | 6857.T | 0,56 | −0,9128 | −0,92 |
   | 8035.T | 0,56 | −0,9128 | −0,91 |
   | IFX.DE | 0,03 | −0,0489 | −0,05 |

   **El vector completo de predicciones del día es un múltiplo escalar de UN número que ningún
   tercero puede recuperar.** Y como **las 8 betas son positivas**, si el retorno del cierre real
   tiene signo opuesto a −1,63, **las 8 direcciones predichas se invierten**.
6. **El retorno es de vintage mixto:** numerador = nivel intradía del 28-sep, denominador = cierre
   real del 25-sep. Además el frame que alimentó el sello se descargó en `salud_descarga`
   (`snapshot.py:99`) **antes** de estampar `ts_emision` (`snapshot.py:111-112`).
7. **Alcance mayor que 8.** Las **24** filas tienen `puntaje_v0`, `sentimiento_ia` y `puntaje_ia` no
   nulos, computados del mismo frame intradía: entran a `verificacion_puntaje` alrededor del 5-oct.
   Y la fila de `snapshots` sella `regimen` y `roca_chip` desde la barra parcial — con la
   **etiqueta de volatilidad dada vuelta** respecto del 24-sep (`vol alta` → `vol baja`), y «un cambio
   de régimen» es la mitad del gatillo de la 5.1.

**Corrección de alcance (única):** el journal **no sostiene «viernes por la tarde»**. El último evento
MKI es `2026-09-25T00:35:03-03:00` y el siguiente `2026-09-28T14:42:52`; como los jobs del viernes
17:50/18:15 no corrieron, la suspensión está acotada a **[vie 02:16, vie 17:50] Chile**. Y **no existe
ningún registro de suspend/resume**: en WSL2 el guest no ve el sueño del host, así que «suspendido y
no apagado» es una **inferencia** correcta (PID preservado + uptime), nunca un hecho registrado.

## NO hay fuga temporal

`./venv/bin/python tests/test_motor.py` → 18 OK, última línea literal: *«RESULTADO: todas las
funciones del motor pasan el test de no-contaminación (sin look-ahead bias).»*, `EXIT=0`. Y a las
17:42:58Z **no existía nada posterior a `t` que borrar**. La fila usó **MENOS** información de la que
declara: el defecto va en la dirección opuesta al look-ahead.

**Pero el verde es verde por la razón equivocada, y eso es hallazgo.** `tests/test_motor.py:43`
trunca con `df[df.index.date <= fecha]`, **inclusive**: la barra parcial de `fecha` está en AMBAS
ramas con el mismo valor y **se cancela**. El test es estructuralmente incapaz de detectar una barra
no liquidada EN `t`. Ése es el hueco exacto por el que pasó este incidente.

Un canal de look-ahead que el auditor encontró y **midió nulo en efecto**: `snapshot.py:163` elige la
sesión objetivo con `proxima_sesion_despues_de(exchange, available_at)`, o sea ancla en un instante
2 h 17 min en el futuro de la emisión. Medido con ancla=emisión vs ancla=`available_at`: **`2026-09-29`
bajo las dos para XKRX, XTKS, XTAI, XETR y XNYS**. El look-ahead existe en el mecanismo y no alteró
ninguna `sesion_objetivo` en esta fecha — coincidencia de esta fecha, no garantía.

## Por qué SÍ son inválidas

1. **El sello de conocibilidad es aritméticamente imposible.** `senales.py:7` y `:130` declaran que
   `available_at` es «cuándo era conocible la información usada», y existe para que un tercero
   verifique la conocibilidad. Acá afirma que el insumo fue conocible **después** de que la fila ya
   existía. 24/24 filas.
2. **No reproducible desde el registro sellado** (punto 5 de arriba).
3. **Inválidas según una regla que el propio proyecto ya aplica en el otro riel.**
   `dinero/sello_dinero.py:557` tiene el orden de tres términos y marcó **33/33** filas `roto` /
   `no_verificable_timing` / `cuenta_para_N=0`; `senales.py:334` tiene una sola guarda,
   `emitida >= apertura`, y las dejó `pendiente`.

## Las tres guardas que existen y no lo vieron

- **`mki_vigia.py:99`** — `de_pared = [t for t, ts, av in filas if av is None or av == ts]`: prueba
  **igualdad, no orden**. Una inversión la pasa muda. Agravado por la carrera: el vigía corrió a
  `17:42:53.372Z`, **5,6 s ANTES** de que las filas existieran, y registró «OK ancla temporal: sin
  predicciones selladas hoy que revisar» — un aprobado vacío.
- **`tests/test_motor.py:43`** — ciego por construcción a este eje (arriba).
- **`descarga_ok = 28/28`** — `snapshot.py:74` usa `limite = fecha − 7 días`: sólo exige que cada
  ticker tenga *algún* dato en la última semana. El campo sellado dio una tranquilidad falsa.

## Contaminación: nada publicado, todo lo futuro

- **YA publicado, NO contaminado.** `cifras.CORTE_README = 2026-08-28`; `cifras.sellada()` da
  `hasta_sello='2026-08-28'`, `n=238`, `dias=34`. `verificacion_apertura` tiene **0** filas con
  `fecha_senal='2026-09-28'` y su máximo es `2026-09-24`; `verificacion_puntaje`, 0. El contador de
  E0 del README pone el 28 en `no_cuentan`, así que **N está protegido**.
- **El reporte de Telegram que sí salió hoy no llevó cifra intradía:** 400 caracteres contra 831-834
  de un día normal, compuesto 3,4 s **antes** de que el sello existiera. La misma carrera que cegó al
  vigía hizo honesto al reporte.
- **FUTURO, contaminado si no se bloquea:** el reporte de las **18:25** compone desde el sello que ya
  existe y publicaría `regimen`, `roca_chip` y las 8 predicciones; mañana las 8 filas entran a
  `verificacion_apertura`; ~5-oct las 24 entran a `verificacion_puntaje`; y
  `backtest/linea_base.py:209` (`sesion_correcta`) las acepta porque **el sello falso es
  auto-consistente con la `sesion_objetivo` sellada**, y por eso es invisible a ese filtro.

## Las 9 filas del diff y la no-duplicación

**CONFIRMADO, no es reescritura de fila sellada.** Diff campo por campo contra
`git show HEAD:data/backups/senales_senales_ticker.csv`: 1351 → 1375 filas, **ningún id desaparecido**,
24 ids nuevos, y exactamente 9 ids preexistentes cambiados (1310, 1313, 1335, 1337, 1342, 1343, 1346,
1347, 1348) en los que **el único campo que difiere es `estado`: `pendiente` → `verificada``**.
Corresponden 1:1 a `verificacion_apertura` ids 412-420. `estado` es campo de ciclo de vida.

**El 28-sep quedó registrado UNA sola vez:** `snapshots` tiene `fecha` como PRIMARY KEY y da
`('2026-09-28', 1)`; `senales_ticker` 24 filas / 24 tickers distintos (`UNIQUE(fecha, ticker)`);
`verificacion_apertura` 420 filas / 420 pares distintos; `divergencias` 6, igual que el 21/22/23/24;
`sello_dinero` 33, igual que cada día. **Ninguna sesión duplicada.**

**Y el aguijón:** la misma idempotencia que impide el duplicado **clausura un sello correcto del
28-sep**. Ningún riel se auto-corrige; la diferencia es que la versión del riel de dinero cuenta 0.

## Zonas ciegas declaradas

1. **El cierre del 28-sep de `^SOX` no existía durante la corrida** (20:00 UTC) y bajar datos estaba
   prohibido en la ventana: **magnitud y SIGNO de la corrupción quedan sin medir**. Es la ciega
   central. La prueba que lo resuelve, después del cierre:
   `motor._cache.clear(); motor.prediccion_apertura_al(date(2026,9,28))` y comparar el «SOX usado %»
   contra el −1,63 sellado.
2. `^SOX` no está en disco con valores del 25/28-sep. El contraste de proxies del propio
   `ext_2026-09-28.csv` (SOXX −2,162 %, SMH −0,925 %, XSD −2,191 % del cierre del 25 a las 13:42 del
   28) es **consistencia, no identificación**: SOXX replica ICE Semiconductor, no PHLX SOX.
3. **Nada en `senales_ticker` registra el vintage de la barra usada.** Desde el sello solo, **no se
   puede distinguir «sellado con cierre liquidado» de «sellado con barra parcial» para NINGUNA fila
   histórica**. El único motivo por el que se pudo con el 28-sep es la inversión de `available_at`:
   una huella accidental, no un instrumento.
4. **Fuga de revisión, y no es hipotética:** el propio meta del día declara
   `"reajuste_detectado": true` en 11 tickers sobre 15 sesiones de solape, `dif_rel_max = 0.0036`
   contra `tolerancia_rel = 1e-06`, con la nota «cierres ajustados retroactivamente por yfinance: no
   point-in-time (declarado, no corregido)».
5. **Fuga de especificación, declarada por el auditor sobre sí mismo:** auditó filas de una tubería
   cuya ventana ya había visto, y llegó al diagnóstico leyendo el código **después** de conocer la
   anomalía.
6. **Advertencia prospectiva de fuga de selección:** ninguna fila del 28-sep se ha usado como
   holdout, así que nada está quemado. Pero **si estas filas se usan para diseñar la corrección y
   luego se cuentan en el track record, eso es una fuga de selección creada por esta auditoría.**

## Dos hechos con reloj que el auditor pasó a Nicolás

- El **reporte de las 18:25 Chile** publicaría las cifras intradía si el timer no se detiene.
  Detener un timer es operación de Nicolás; ningún agente lo toca.
- La medición que cuantificaría el daño sólo es posible **después de las 20:00 UTC / 17:00 Chile**.


---

# Dictamen complementario (17:55) — la medición de las 17:31 contra el veredicto

Se le devolvió la consulta cuando la zona ciega #1 quedó llena, a pedido del `guardian-constitucion`.
Solo lectura, **sin descargas** (dentro de la ventana 17:50–20:30).

```
VEREDICTO: FILAS INVÁLIDAS ENTRARON COMO VÁLIDAS
Sin cambio de forma. FUERZA NETA MAYOR que en el dictamen original.
Los bloques 2 y 3 siguen sin ejecutarse.
```

## Lo que verificó de la medición antes de opinar sobre ella

`senales.db` con **mtime `14:43:30`** y `dinero/sello_dinero.db` con **`14:43:01`**, las dos con las
huellas de la apertura: **ninguna base de sellado se escribió**. `noticias.db` con mtime `17:52:38`,
consistente con `mki-noticias`. La descripción de `roca_chip` es **literal** (`motor.py:177-194`:
`percentil = (serie.tail(252) <= serie.iloc[-1]).mean() * 100`, y `snapshot.py` sella ese `valor`). Y
verificó la **coherencia interna** de la tabla 9.2 dividiendo cada recomputado por −1,61 y recuperando las
betas: 0,031 · 0,304 · 0,323 · 0,565 · 0,590 · 0,658 · 0,801, y **0,497** para 8035.T, todas dentro de
0,005 de las selladas. «La tabla es un output coherente de `beta × sox`, no un conjunto de números
sueltos.»

## Por qué el veredicto se sostiene con MÁS fuerza

«**El veredicto nunca descansó en la severidad.**» Sus cuatro fundamentos —la imposibilidad aritmética de
`available_at`, la no-reproducibilidad, las guardas que no pueden verlo, y el estándar escrito del propio
proyecto— **no los toca la medición**. Y uno **lo confirma**: «yo había *deducido* que un tercero que
reprodujera obtendría otro número. Un tercero reprodujo y obtuvo −1,61 en vez de −1,63 y 17 en vez de 44.
**La no-reproducibilidad pasó de inferida a medida.** Ése es el aporte probatorio más fuerte de la
sección 9.» Lo que la medición cambió es el estatus de dos ítems que su dictamen puso bajo **«SOSPECHAS
SIN DEMOSTRAR»**, fuera de los fundamentos.

Y el principio que ordena todo: «**la validez de un sello no es función del tamaño del error.** El riel de
dinero no preguntó cuánto se había desviado el insumo antes de marcar 33/33 `roto`: invalidó por la
violación de orden, sola. Si mi veredicto se ablandara porque el error salió chico, eso sería exactamente
elegir qué filas cuentan después de verlas… **vale en las dos direcciones. La medición no puede rescatar a
las filas por la misma razón por la que no puede condenarlas.**»

## Las formulaciones que aceptó, y las tres correcciones que exigió

- **Sospecha 1 (signo del insumo):** «MEDIDO EN UNA FECHA, NO RESUELTO COMO RIESGO… el mecanismo que la
  produce está intacto y es estructural — las 8 betas son positivas, así que un despertar con la bolsa
  abierta en un día donde la barra parcial y el cierre caigan a distinto lado del cero **invierte las ocho
  a la vez**.»
- **Sospecha 2 (el régimen):** «MEDIDO EN UNA FECHA, y **la evidencia es más débil de lo que parece**…
  la coincidencia de una etiqueta binaria es evidencia débil por construcción… 37,5 contra 38,8, un margen
  de 1,3 sobre el umbral, no una holgura. La etiqueta coincidió; no se midió que fuera robusta.»
- **Sospecha 3, la que sigue abierta:** §9 **no mide `puntaje_v0` / `puntaje_ia` ni `divergencias`**, y
  `puntaje_ia` es el campo de las **24** filas que entran a `verificacion_puntaje` alrededor del 5-oct.
  «Es el ítem de mi lista con **más filas en juego** y sigue SIN MEDIR… es el hueco vivo de esta corrida.»
  Y ya no se puede medir la diferencia: la barra parcial de las 13:42 no existe más.
- **Correcciones a la redacción:** «la sospecha central» → **«una de las dos sospechas»** (estaban fuera
  de los fundamentos, y llamarla central sugiere que el veredicto se debilita, «que es justo lo contrario
  de lo que pasó»); el canal de publicación de `roca_chip` **no es sólo Telegram** (`api/main.py` en `/` y
  `/cadena`, la tarjeta hero de `Hoy.tsx` con su sparkline, la serie de 365 días de
  `senales.historial_roca_chip`, y `Cadena.tsx`); y los **27 puntos son el piso**: del mapeo
  percentil↔crudo de los días adyacentes, el crudo sellado implícito es ≈ **+3 %** contra el **−2,8 %**
  real, o sea **cambio de signo, ~5,8 pp — INFERIDO** y permanentemente inmedible.

**Atribución, que él mismo puso:** la medición **es de la corrida, no suya** — su dictamen nombró el campo
y el test exacto y **no lo ejecutó**. «No la reclamo como hallazgo propio: el mérito de haberla corrido es
del `director-programa` que marcó que estaba disponible.» Y entra en su dictamen como **sospecha resuelta
— CONFIRMADA, no refutada**.

**Sobre la gravedad, refinó la lectura de la corrida en vez de contradecirla:** daño chico en el canal
**lineal de insumo único** (`beta × escalar`, acotado por construcción) y grande en el canal **no lineal y
agregado** (un percentil de un promedio de momentum sobre los eslabones, donde la barra intradía los mueve
todos a la vez). Y su cierre: «el argumento a favor de la regla **no puede ser** "medimos y el daño fue
chico", porque el canal donde el daño fue grande es justamente el que nadie puso primero — **yo incluí
`roca_chip` en una lista plana de cuatro sospechas, sin jerarquizarla**. Una regla que dependa de que
alguien jerarquice bien los canales ex ante falla la primera vez que alguien jerarquiza mal, y esta corrida
es esa primera vez.»

Atenuante que puso en justicia: `roca_chip_al` recomputa desde precios, así que **los percentiles futuros
no quedan envenenados**; la contaminación está confinada a la fila sellada y a lo que la muestra.

## `(iii-bis)` en `estado_epistemico.md`: AUTORIZADO con tres condiciones

Las tres, aplicadas: que diga que la medición **confirma** la no-reproducibilidad de (iii) —«sin él, el
ítem lee como atenuante cuando su contenido más fuerte es agravante»—; que declare que `puntaje_*` y
`divergencias` **NO** fueron medidos —«un lector razonable leerá "el daño está medido"… esa lectura es
falsa en el peor sentido»—; y que el canal de publicación no se limite a Telegram.

## Zonas ciegas actualizadas

**#1 queda LLENADA con su caveat** (se midió contra un **proxy** del cierre: −1,61 a las 16:31 NY, y la
propia corrida midió que en 2 de 4 noches no todos los tickers tienen cierre ni a las 23:35). Y abrió tres:
**#9** la columna «recomputado» **no es reproducible por nadie** —no hay script ni log en disco; verificó
la coherencia interna y «acepto esos números por la palabra de la bitácora, y lo digo»—; **#10** la
asimetría es **permanente**, porque la barra parcial de las 13:42 no existe más y la comparación no se
puede repetir nunca; **#11** `snapshot.py` sella el percentil y **no** el `crudo_pct`, así que la
contaminación cruda es inmedible desde el sello, para el 28-sep y para toda fila histórica.

## Dos cosas con reloj que dejó para Nicolás

El reporte de Telegram publica **`Roca→Chip: 44/100`** cuando el cierre dice 17, y al momento de su
dictamen faltaba **media hora**. Y la medición que falta —`puntaje_v0` / `puntaje_ia` y `divergencias`,
las 24 filas— **ya no se puede hacer contra la barra sellada**: sólo se puede medir el valor correcto,
nunca la diferencia.
