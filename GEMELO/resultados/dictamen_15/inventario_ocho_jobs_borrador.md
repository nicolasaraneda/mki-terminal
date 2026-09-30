## <n>. Inventario de los ocho jobs ante un disparo fuera de hora, con una novena fila para el cambio de calendario de un timer (corrida 15) — funde §63

> **BORRADOR del bloque 5 de la corrida 15.** El orquestador pone el número y marca §63 como «FUNDIDA en la
> tarjeta <n> por el acta §91.5» sin borrar su texto. Sólo lectura: ningún archivo del repo se tocó, ninguna
> unidad de systemd se operó, ningún job ni test se corrió. Lecturas hechas el **29-sep-2026 entre las 22:11 y
> las 22:43 de Chile** (hora leída de `date` antes de cada consulta; la ejecución se cortó ~22:40 por cuota de
> la API y se retomó a las 23:01), sobre el árbol real en `HEAD = 2f73eb2` (`main`): **las guardas que la
> corrida 15 planifica NO estaban en ese árbol al leer**; donde se dice qué hará un job con ellas va marcado
> **PLANIFICADO en la corrida 15** y es deducción, no observación. Bases abiertas sólo con
> `sqlite3.connect('file:...?mode=ro', uri=True)`, fuera del tramo 00:15–00:50. `data/sonda_cierre.csv` y
> `data/sonda_cierre.log` se leyeron filtrados por `timestamp_utc < 2026-09-30T04:00:00Z` (acta §91.3):
> ninguna fila de madrugada existía ni se leyó (última lectura 22:27). Cada cifra lleva su fuente.

**Qué hay que decidir, en una frase.** Para cada uno de los ocho jobs, si ante un disparo fuera de su hora
**se niega**, **marca** o **sigue igual**; y qué procedimiento rige un **cambio de calendario** de un timer
instalado, que el 29-sep disparó la sonda a las 18:38:57 sin que nadie lo pidiera.

**Qué desbloquea.** Cierra §63 (fundida acá). Pone en contexto las tres guardas que la corrida 15 planifica
(§90.1 b, §90.8, y la (a) del verificador) y las dos que no toca (vigía, sonda). Da el procedimiento sin el
cual mover la hora del sellador (§58 b/c) puede quemar una sesión de N en el acto (§91.7, tercer punto).

**Cuánto cuesta decidirlo.** ~25 minutos de lectura. Nueve decisiones chicas; tres ya están firmadas
(§90.1 b, §90.6, §90.8) y acá sólo se las sitúa. **Las dos filas con más en juego son la 2 (snapshot) y la 9.**

---

### A. Los dos eventos, MEDIDOS

**A.1 El 28-sep-2026, 14:42:52 Chile (13:42 de Nueva York, NYSE abierta).** `journalctl --user`, `-o short-precise`,
las ocho unidades. Arrancaron en 59 ms, **en el orden alfabético de sus nombres de unidad** (n = 1; no se verificó
que sea regla): backup .702, noticias .704, reporte .706, sello-dinero .708, snapshot .709, sonda .710,
vigia-rechequeo .734, vigia .761.

| job | arranque → fin (journal) | qué hizo, con su fuente |
|---|---|---|
| `mki-vigia-rechequeo` | 14:42:52.734 → 14:42:53.303 | «sin alerta pendiente de hoy — nada que re-chequear» (`data/vigia.log:216-217`). Corrió **antes** de que el vigía escribiera el marcador (17:42:55.339Z). |
| `mki-backup` | 14:42:52.702 → 14:42:53.790 | commit `5321f6b` «Backup diario 2026-09-28», AuthorDate `2026-09-28T14:42:53-03:00`: **3 archivos, +340** — `sello_dinero.csv` (+33 filas del insumo 2026-09-24, timestamp 2026-09-25T03:30:04Z) y `ext_2026-09-24.{csv,meta.json}`; **ningún** `senales_*` (`git show --stat`). Es el material que el backup del viernes 25, que nunca corrió, habría commiteado. `data/backup.log:67-69`. |
| `mki-vigia` | 14:42:52.761 → 14:42:56.648 | `data/vigia.log:218-226`: **4 FALLA** (snapshot NO se selló; descarga sin snapshot; noticias NO corrió — «proceso 39845 vivo desde Mon Sep 28 14:42:51»; reporte NO hay envío) y **2 OK** («backup: commit de hoy presente» — sostenido por `5321f6b`, de 2 s antes —; «ancla temporal: sin predicciones selladas hoy que revisar»); marcador escrito; **alerta Telegram enviada 17:42:56.18Z**. |
| `mki-reporte` | 14:42:52.706 → 14:42:56.985 | `data/reporte.log:45-46`: compuesto 17:42:55.500Z, **400 caracteres**, «Reporte enviado 14:42» (17:42:56.46Z): **3,4 s antes de que el sello existiera**. |
| `mki-sonda-cierre` | 14:42:52.710 → 14:42:58.587 | **36 filas**, `timestamp_utc 2026-09-28T17:42:55.212430Z`, `hora_ny 13:42`, `sesion_ny 2026-09-28`, 35 con `es_sesion_de_hoy = 1` (CSV filtrado); `data/sonda_cierre.log:33` «13:42 NY · sesión 2026-09-28 · 35/36 · faltan: ['TOELY']». |
| `mki-sello-dinero` | 14:42:52.708 → 14:43:01.401 | `data/sello_dinero.log:441-469`: `sellada`, `fecha_insumo 2026-09-28`, `timestamp_utc 17:43:01.001Z`, `available_at 20:00Z`, **`no_verificable_timing` / `roto` / `cuenta_para_N 0`**, `insumo_completo false` (TOELY), **33 filas**, `ext_2026-09-28.csv` (sha `2e984469…`) escrito y respaldado. Base (ro): 33 filas en ese estado. |
| `mki-snapshot` | 14:42:52.709 → 14:43:30.755 (43 s, sin reintentos) | `data/snapshot.log:133-140`: **selló** `{'snapshot': True, 'predicciones': 8, 'regimen': 'Alcista · vol baja', 'roca_chip': 44, 'descarga': '28/28'}`; **envió la retractación del vigía 17:43:07.30Z** (:135-136, `_epilogo_vigia`); verificador apertura 9, puntaje 44; 8 CSV; **salud de datos OK (27 tickers)** (:140). Base (ro): `snapshots` 2026-09-28 `timestamp_utc 17:42:58.943983Z`, `sox_usado_pct −1,63`, `sox_fecha 2026-09-28`; `senales_ticker`: **24 filas con `available_at > timestamp_utc`, única fecha así en la tabla**. |
| `mki-noticias` | 14:42:52.704 → 14:45:21.298 | `data/noticias.log:120-125`: dedup (9 duplicados), **286 titulares nuevos** (17:45:19Z), «análisis falló en el lote 1: Error code: 400 … credit balance is too low», **analizados 0 de 3361, costo 0,0000 USD**; ledger `data/costos_ia.log:39` `resultado 'ok'`, `costo_usd 0.0`. |

Telegram ese día: **cuatro mensajes, tres fuera de hora en 11 s** (alerta 17:42:56.18Z, reporte 17:42:56.46Z,
retractación 17:43:07.30Z) y el reporte de las 18:25. La bitácora 14 §0-bis.9 titula «dos mensajes»: la
retractación es el tercero. **Orden de fin:** la bitácora 14 (§0-bis.8, §64, acta §89.6) dice que backup
«terminó primero»; el journal dice que **`mki-vigia-rechequeo` terminó primero (14:42:53.303) y backup segundo
(14:42:53.790)**: backup fue el primero **de los que escriben**. Errata menor, candidata.

**A.2 A la hora normal, el mismo día (todo medido).** noticias 17:50:00 → 17:52:40: 96 nuevos, la misma falla
400, 0 USD (`noticias.log:126-131`). **snapshot 18:15:00 → 18:15:14: `{'snapshot': False, 'motivo': 'ya existe
snapshot de hoy'}`**, verificador apertura 0, puntaje 4, salud: «Tokyo Electron (8035.T): salto de −80 % el
2026-09-28 — revisar split/dato corrupto» (`snapshot.log:141-147`). reporte 18:25:00 → 18:25:02: **831
caracteres**, «Reporte enviado 18:25» (`reporte.log:47-48`). backup 18:40:00: **`f7b65e0`**, 9 archivos, +813 −22,
con `ext_2026-09-28.{csv,meta.json}` y la fila de `snapshots` del 28 (`git show --stat`). vigía 19:00:00: **todo OK**,
incluido «ancla temporal: 8/8 filas con cierre del SOX» sobre las 8 filas invertidas (`vigia.log:227-234`;
`mki_vigia.py:97` prueba `av == ts`). rechequeo 20:30:00: sin marcador (`vigia.log:235-236`). sonda 21:05 → 00:35
Chile, ocho pases: 1/36 a las 20:05–21:05 NY, 35/36 de 21:35 a 23:35 NY (`sonda_cierre.log:34-41`). **sellador
00:30:00 → 00:30:04 del 29: `divergencia_registrada`, 0 filas, `decisiones_distintas 0`** (`sello_dinero.log:473-482`);
base (ro): `divergencias_sello` id 2, `fecha_insumo 2026-09-28`, `timestamp 2026-09-29T03:30:04.346Z`;
`sellos_dinero` 462 filas, 14 fechas, **9 cuentan**. La predicción de la bitácora 14 §0-bis.2 se cumplió.

**A.3 El 29-sep-2026, 18:38:57 Chile (17:38 NY, 98 min después de la campana), cambio de calendario.** Journal
(`systemd[317]`, mismo proceso, así que el orden de las marcas es el orden de emisión): `.165914` «Reload
requested from client PID 91601 ('systemctl')» · `.274150` «Reloading finished in 106 ms» · **`.327292` «Starting
mki-sonda-cierre.service»** · `.330093` «Stopped mki-sonda-cierre.timer» · `.330127` «Stopping…» · `.330264`
«Started mki-sonda-cierre.timer» · `18:38:59.973` Finished. `systemctl show`: `Persistent=no`,
`ActiveEnterTimestamp 18:38:57`. Último disparo antes del cambio: **29-sep 00:35:00** Chile (journal). Escribió
**36 filas**, `timestamp_utc 2026-09-29T21:38:57.684Z`, `hora_ny 17:38`, `sesion_ny 2026-09-29`, **35/36 con la
barra de hoy** (`sonda_cierre.log:42`); a las 20:05, 20:35 y 21:05 NY, **1/36** (`:43-45`).

**A.4 Censo, todo el journal retenido (desde 2026-08-24T23:14).** 212 arranques de `mki-*.service`; **10 fuera
del calendario instalado**: los 8 del 28-sep, el de la sonda del 29-sep, y **uno el 25-ago 19:34:41**
(`mki-vigia-rechequeo`, 2 min después de instalar los timers; compatible con un arranque manual de prueba; no
investigado). Tres activaciones de timers **sin** disparo inmediato: 25-ago 19:32:41 (instalación, sin stamp),
19-sep 22:26:43 (la sonda, primera vez), 20-sep 02:05:59 (arranque del manager, los ocho). Ninguna cambió un
calendario con historia. **n = 1 despertar, n = 1 cambio de calendario.**

**A.5 La suspensión, acotada por dos relojes (INFERENCIA con dos medidas que coinciden).** El kernel invitado
arrancó el 20-sep 02:05:59 (journal, primer mensaje de `systemd[317]`). A las 22:27:49 del 29-sep,
`CLOCK_MONOTONIC = CLOCK_BOOTTIME = 551.798,7 s` (6 d 9 h 16 min) contra **850.910 s de reloj de pared** desde ese
arranque: **3 d 11 h 05 min que ningún reloj del invitado contó** — y `BOOTTIME = MONOTONIC` dice que el invitado
no vio suspensión propia: la VM fue pausada desde afuera. Si fue una sola pausa terminada a las 14:42:52 del 28,
empezó **≈ 25-sep 03:37**. El journal del SISTEMA lo confirma por otra vía: `systemd-resolved: Clock change
detected` cada 30 s, con un único hueco mayor a 2 min entre el 20-sep y hoy, **del 2026-09-25 03:37:10 al
2026-09-28 14:42:52** (medido por el orquestador, bitácora 15 §0.10; ±30 s). La ventana «[vie 02:16, vie 17:50]»
de la corrida 14 queda superada: la pausa empezó a las **03:37 del viernes 25**. Lo que sigue sin registro es la
causa: que fue una suspensión del host es testimonio de Nicolás (acta §91.5), no un evento del journal.

---

### B. Tabla principal

| # | job (OnCalendar, `Persistent`) | 1. qué hizo el 28-sep a las 14:42 | a su hora normal | 2. guarda al cerrar la corrida 15 | 3. costo MEDIDO (n = 1) | 4. recomendación del agente |
|---|---|---|---|---|---|---|
| 1 | `mki-noticias` (`Mon..Fri 17:50 America/Santiago`, true) | RSS: 286 titulares; 1 llamada IA rechazada (400 crédito); 0 USD | 96 titulares; misma falla; 0 USD | **ninguna de ventana**; tope diario 0,50 USD con freno entre lotes + timeout de red | 0 USD, nada publicado, nada perdido | (iii) nada para la ventana; el problema del job es otro (E.1) |
| 2 | `mki-snapshot` (`Mon..Fri 18:15`, true) | **selló** 24 filas con barra intradía; `roca_chip` 44; `available_at` 2 h 17 min posterior a la emisión | «ya existe snapshot de hoy»; no re-sella | **PLANIFICADO**: (b) se niega si `available_at > emisión`; (a) verificador marca; (d) medición excluye; ancla en la emisión (§90.2) | 24 filas selladas con insumo no reproducible; sesión del 28 sin sello con cierre; publicadas por reporte y API | (i) exactamente como está firmada: sin margen, sin reloj de pared; frescura y fin de semana como decisión aparte (D) |
| 3 | `mki-reporte` (`Mon..Fri 18:25`, true) | reporte de 400 caracteres con huecos declarados, 3,4 s antes del sello | 831 caracteres desde el sello de las 13:42 NY: «sellado 14:42 Chile», SOX −1,63, Roca→Chip 44 | **ninguna**; sin anti-duplicados por diseño | 2 mensajes en Telegram: 1 de ruido, 1 con cifras de barra parcial; nada perdido | (ii) marcar: el mismo mensaje con la línea «disparo fuera de hora» |
| 4 | `mki-backup` (`Mon..Fri 18:40`, true) | commit `5321f6b` «Backup diario 2026-09-28» **sin nada del 28** | `f7b65e0`, 9 archivos, con la matriz de media sesión | **PLANIFICADO** §90.8: se niega si el snapshot del día no está sellado; fin de semana por definir | 1 commit con nombre que no describe su contenido; nada perdido | (i) como está firmada; en fin de semana la misma regla (posterga, no pierde) |
| 5 | `mki-vigia` (`Mon..Fri 19:00`, true) | 4 FALLA + 2 OK (uno sostenido por el commit prematuro); alerta enviada; retractada por snapshot.py 11 s después | todo OK, incluida el ancla temporal sobre las 8 filas invertidas | sólo exención de fin de semana; **no se toca en esta corrida** (tarjeta: `av == ts` Y `av > ts`) | 1 alerta falsa + 1 retractación; nada perdido | (ii) marcar «pase fuera de hora», en la misma tanda que `av == ts`; **no** (i): un vigía que calla por una guarda mal escrita es el peor falso negativo de la tabla |
| 6 | `mki-vigia-rechequeo` (`Mon..Fri 20:30`, true) | nada: corrió 2 s antes del marcador | nada: el marcador ya estaba consumido | por construcción sólo actúa con marcador de HOY | 0 | (ii) que el texto use la hora real y no el literal `20:30`, al tocar el vigía |
| 7 | `mki-sonda-cierre` (`Mon..Fri 20..23:05,35` + `Tue..Sat 00..03:05,35 America/New_York`, **false**) | 36 filas a las 13:42 NY, bolsa abierta; el lector las descarta y declara | 8 pases normales | job: ninguna; lector: descarta sólo «antes del cierre»; **no se toca en esta corrida** | 36 filas pre-cierre (28) descartadas + **36 post-cierre fuera de grilla (29) que el lector NO descarta** | (ii) el lector rotula y excluye «fuera de grilla», corrida 16; `regla_58.md` lo dice desde esta noche |
| 8 | `mki-sello-dinero` (`Mon..Fri 23:30 America/New_York`, true) | 33 filas `no_verificable_timing` + `ext_2026-09-28.*` de media sesión | divergencia, 0 filas, 0 decisiones distintas | E4 marca (en producción); §90.6 (a)+(d) **firmado, NO aplicado** | sesión del 28 fuera de N (9 cuentan); cupo de evidencia ocupado y versionado | (ii) tal como está firmada en §90.6; hasta aplicarla la exposición es la del 28-sep |
| 9 | cambio de calendario (`daemon-reload` + `restart`) | — | — | ninguna: **`Persistent=false` no lo impidió** (medido) | 36 filas fuera de grilla el 29-sep, que contaminan la noche del 29 en el dato de §58 | procedimiento (P1)+(P2) escrito en `systemd/INSTALACION.md`; (P0) antes de mover la hora del sellador |

---

### C. Fichas por job

**C.1 `mki-noticias`.** *Hizo:* lo de A.1/A.2. Interacción medida por horas: el snapshot selló a las 17:42:58Z, **antes**
de que noticias escribiera (dedup 17:43:33Z, titulares 17:45:19Z): el sello del 28 usó el caché de noticias anterior
a esa corrida. *Guarda:* ninguna de ventana; tiene el tope diario con freno entre lotes (`mki_noticias.py:91-100,
118-121`) y `socket.setdefaulttimeout(30)` (:36-37). *Costo:* 0 USD, 0 llamadas cobradas (1 intentada y rechazada);
si hubiera crédito el techo es el tope de `.env` (código, no medido). *Opciones:* (i) negarse antes de las 17:50
Chile — un despertar de la mañana no corre y el pase normal de las 17:50 sí, así que no pierde nada; una guarda mal
escrita (huso) lo apaga todos los días y lo detecta el vigía («noticias: el job NO corrió hoy»). Con la no elegida se
pierde: nada medible. (ii) marcar `fuera_de_hora` en el ledger. (iii) nada: un pase extra bajo tope. **Recomendación
del agente: (iii).** Lo que este job necesita no es una ventana: ver E.1.

**C.2 `mki-snapshot`.** *Hizo:* A.1/A.2. Hoy las 8 filas con predicción están `verificada` (verificador del 29-sep
18:15, `snapshot.log:150` `'verificadas': 9`) y hay **8 filas en `verificacion_apertura` con `fecha_senal 2026-09-28`**
(consulta ro), que es lo que la (d) planificada excluirá por regla. *Guarda hoy:* ninguna de conocibilidad ni de
ventana; sólo la idempotencia por fecha (`senales.py:181-187`, `snapshot.py:93-94`) y la regla maestra del verificador,
que compara sólo `emitida >= apertura` (`senales.py:334`). **PLANIFICADO en la corrida 15:** (b), (a), (d) y el ancla
en la emisión, tal como firmó §90.1/§90.2.
*Medido sobre la historia, para dimensionar el falso negativo de la (b):* 45 snapshots con `sox_fecha` sellado
(27-jul → 29-sep). Margen emisión − cierre de la sesión de `sox_fecha`: **negativo en 1 solo (28-sep, −137 min)**;
mínimo positivo 75,1 min (14-sep); **15 de 45 por debajo de 120 min** (todos desde el 8-sep, con Chile en UTC−3).
Calculado con `exchange_calendars`: **del 2-nov-2026 al 12-mar-2027 el margen es de 15 minutos** (18:15 Chile =
21:15 UTC contra cierre 21:00 UTC en EST); vuelve a 75 min el 15-mar y a 135 min el 5-abr-2027. Consecuencia: la (b)
**sin margen** habría rechazado exactamente 1 de 45 (el 28-sep) y cero sellos buenos; una (b) que reusara el margen
de publicación de 2 h de `calendarios.sesion_ya_cerro` (`calendarios.py:94`, default `margen_horas=2.0`) habría
rechazado 16 de 45 y **rechazaría todos los días de noviembre a marzo**: una sesión irrecuperable por día. Ese es el
costo de una guarda mal escrita en este job, y por eso la ventana de este job no puede ser de reloj de pared.
*Costo medido:* 24 filas selladas con un insumo que la fuente ya no sirve (bitácora 14 §11.3), 8 ya verificadas,
1 fila de `snapshots` con `roca_chip` 44 y régimen desde barra parcial, publicadas por el reporte de las 18:25 y por
`/` y `/cadena`; y la sesión del 28 sin sello con cierre. n = 1.
*Sobre el 44 contra 17 (PROVISIONAL, y hay un dato nuevo):* `snapshot.log:140` — el bloque de las 17:42Z, el que
selló el 44 — dice **«salud de datos: OK (27 tickers)»**; el de las 21:15Z marca 8035.T con −80 % (:146-147); el del
29-sep 21:15Z vuelve a **OK y sella `roca_chip` 50** (:149, :153). O sea que el salto **no estaba en la descarga con
la que se selló el 44** y ya no estaba el 29; el 17 se recomputó a las 20:31Z, entre esas dos lecturas. INFERENCIA:
el 17 es compatible con haberse calculado con el salto presente. Sigue PROVISIONAL: nadie releyó `roca_chip_al` del
28 con la fuente ya corregida, y este bloque no descarga.
*Opciones:* (i) negarse **[PLANIFICADO (b)]**. Con la no elegida se pierde: (ii) marcar al sellar (estado no
verificable en el sello, como E4) **sin** tocar la idempotencia deja la fecha quemada igual — el mismo problema que §62
en el otro riel —, así que (ii) sólo vale si `ya_existe_snapshot_hoy()` distingue estados; (iii) nada: cada despertar
con bolsa abierta sella 24 filas inválidas y quema la sesión. **Recomendación del agente: (i) exactamente como está
firmada — sin margen de publicación y sin ventana de reloj de pared —, y los dos huecos de D.1 y D.2 (frescura, fin
de semana) como decisión aparte con sus cuentas a la vista.**

**C.3 `mki-reporte`.** *Hizo:* A.1/A.2. El texto no queda en ningún log en modo titular (sólo el largo), así que
el contenido se deduce del código: a las 14:42, «⚠ sin snapshot sellado hoy», «Régimen / SOX / Roca→Chip: sin sello
hoy», «Aperturas: sin predicciones selladas hoy», track record 30 d y cobertura (`alertas.py:230-231, 250, 273,
278-290`); a las 18:25, cabecera **«sellado 14:42 Chile»**, «SOX: −1.63 % (sesión del 2026-09-28)», «Roca→Chip: 44/100»,
8 predicciones «emitidas 14:42 Chile, antes de la apertura objetivo» (`:226-228, 238-239, 242, 269-271`; valores de
`snapshots`). **El mensaje publicó su propia hora de emisión.** *Guarda:* ninguna; sin anti-duplicados por diseño
(`alertas.py:305-310`). Al cerrar la corrida 15, igual; la (b) del snapshot le quita la fuente del segundo daño.
*Costo medido:* dos mensajes, uno de ruido (verdadero en ese segundo) y uno con cifras de barra parcial. Nada perdido.
*Recuperabilidad, leída del código:* `./mki reporte` reenvía el mismo día; `componer_reporte_sellado()` usa
`date.today()` y el CLI no acepta fecha (`alertas.py:220, 345-373`): pasado el día no hay reenvío de esa fecha. Un
falso negativo acá cuesta la publicación del día si nadie lo ve antes de la medianoche; el vigía lo grita a las 19:00
(`mki_vigia.py:199-213`). *Opciones:* (i) negarse antes de las 18:25 Chile — un despertar de mañana no manda nada;
uno de la tarde, después de las 18:25, manda (tardío, legítimo); mal escrita, apaga el reporte y lo detecta el vigía.
Con la no elegida se pierde: la anotación en el propio mensaje. (ii) marcar: el mismo mensaje con «disparo fuera de
hora (14:42; programado 18:25)» — **nunca pierde un envío; un error en la marca sólo etiqueta mal**. (iii) nada.
**Recomendación del agente: (ii).**

**C.4 `mki-backup`.** *Hizo:* A.1/A.2. Efecto colateral medido: el commit de las 14:42:53 hizo que el vigía de las
14:42:55 diera «OK backup: commit de hoy presente» (`vigia.log:223`; `mki_vigia.py:224-229` mira `git log -1
--format=%cs -- data/backups`): **un OK sostenido por un commit que no contenía el sello del día.** *Guarda hoy:*
ninguna (`mki_backup.py:41-49`, pathspec). **PLANIFICADO** §90.8. Un feriado de NYSE en día hábil **sí** tiene snapshot
(7-sep se selló con `sox_fecha` 4-sep: consulta ro), así que lo que §90.8 deja por definir es el fin de semana, que
hoy sólo llega por catch-up o por cambio de calendario. *Costo medido:* un commit en el historial con un nombre que
no describe su contenido; nada perdido (todo entró en `f7b65e0`). *Opciones:* (i) negarse **[PLANIFICADO]** — mal
escrita, en un día sin sello real posterga el export del sellador de esa noche al día siguiente: **posterga, no
pierde**. (ii) marcar: commitear con «Backup parcial <fecha> (antes del sello)» — artefacto mal formado pero bien
nombrado. (iii) nada. **Recomendación del agente: (i) como está firmada, con la misma regla en fin de semana (sin
snapshot ese día, no commitea; el lunes lo hace).**

**C.5 `mki-vigia`.** *Hizo:* A.1/A.2. La retractación la envió `snapshot.py` (`snapshot.py:219-231`), no el
rechequeo; su texto (deducido, `mki_vigia.py:338-344`): «recuperado: snapshot sellado (emisión 14:42, confirmada a las
14:43), descarga 28/28, predicciones 8» — retracta el conjunto consumiendo el marcador; las FALLAs de noticias y
reporte no se nombran. La alerta vivió **11,1 s**. *Guarda:* sólo la exención de fin de semana (`mki_vigia.py:405-407`).
No se toca en esta corrida. *Interacción con la (b) planificada [DEDUCIDO]:* en un próximo despertar con la bolsa
abierta el snapshot se niega, el vigía alerta «NO se selló» y deja el marcador, y la retractación recién sale cuando
el snapshot de las 18:15 sella (`_epilogo_vigia`): **la alerta falsa pasa de 11 s a ~3,5 h abierta**. Si el despertar es
después de las 18:15 con bolsa cerrada, el snapshot sella tarde y la secuencia es la del 28-sep. *Costo medido:* una
alerta falsa y una retractación; nada perdido. *Opciones:* (i) negarse a pasar lista antes de las 19:00 Chile — con la
no elegida se pierde nada medible, pero **si la guarda está mal el vigía calla, y el vigía es la alarma**; sólo
`/salud` lo cubriría. (ii) marcar: pasar lista igual y decir en la alerta «pase fuera de hora (14:42; programado
19:00): los jobs de hoy pueden no haber corrido todavía»; o evaluar cada chequeo sólo si su hora programada ya pasó
(exige duplicar seis horas en el código: dos fuentes de verdad). (iii) nada. **Recomendación del agente: (ii), en
la misma tanda que arregle `av == ts` (un solo toque al vigía); no (i).**

**C.6 `mki-vigia-rechequeo`.** *Hizo:* nada, las dos veces. *Guarda:* sólo actúa con marcador de HOY
(`mki_vigia.py:289-299, 352-374`). *Costo medido:* 0. *Lo que no pasó por 27 ms [DEDUCIDO, n = 0]:* con el orden
inverso habría encontrado el marcador y, con el snapshot todavía corriendo, enviado «sigue sin sellar a las 20:30:
reintentos aún activos» a las 14:42 — la hora es el literal `HORA_RECHEQUEO` (`mki_vigia.py:46, 368-370`).
*Opciones:* (i) negarse antes de las 20:30 del día del marcador; (ii) que el texto lleve la hora real; (iii) nada.
**Recomendación del agente: (ii) al tocar el vigía; nada aparte.**

**C.7 `mki-sonda-cierre`.** *Hizo:* A.1/A.2/A.3. *Lo que el lector hace con eso, calculado en memoria con
`GEMELO.sonda_cierre_resumen.resumen()` sobre el CSV filtrado, sin escribir:* noche del 28 — descarta las 36 de las
13:42 (anteriores al cierre) y las declara; aparición 21:35 para 34 tickers, 20:05 para 1, ninguna para TOELY.
**Noche del 29 — NO descarta las 36 de las 17:38** (posteriores al cierre de las 16:00) **y les atribuye la aparición:
«17:38» para 35 tickers**, cuando a las 20:05, 20:35 y 21:05 esos mismos tickers no tenían la barra. El filtro de la
corrida 14 (`sonda_cierre_resumen.py:104-120`) cubre «antes del cierre», no «fuera de grilla»; la aparición se toma
como mínimo (`:128-130`). **Esto contamina la noche del 29 en el dato de §58 si no se filtra.** *Guarda:* ninguna en
el job (`sonda_cierre.py:180-198`). No se toca en esta corrida (primera noche de madrugada; deudas (3) y (4) a la 16).
*Costo medido:* 36 filas pre-cierre (28-sep) descartadas y declaradas; 36 post-cierre fuera de grilla (29-sep) que
entran como aparición. Nada perdido; algo agregado que hay que filtrar. n = 2 disparos. *Y un dato que nadie
buscaba (DESCRIPTIVO, n = 1):* a las 17:38 NY, 98 min después de la campana, **la barra fechada hoy existía para
35/36 y a las 20:05 no (1/36)**: la retirada de la barra intradía ocurre **después** de las 17:38 NY, no «al cerrar la
sesión» como escribe la bitácora 14 §11.3 (errata candidata). *Opciones (las de §63, actualizadas):* (i) el job se
niega fuera de grilla (minuto fuera de {05, 35} u hora fuera de las franjas) — con la no elegida se pierde la fila y
con ella la evidencia: el dato de las 17:38 no existiría. (ii) el lector rotula y excluye «fuera de grilla» además de
«antes del cierre», declarándolas — **la única que arregla lo que ya está en disco (72 filas)**. (iii) nada: cada
disparo fuera de grilla posterior al cierre entra como aparición. **Recomendación del agente: (ii), en la corrida 16
junto con las deudas (3) y (4); y que `regla_58.md` diga desde esta noche que la noche del 29 lleva una observación
fuera de grilla.**

**C.8 `mki-sello-dinero`.** *Hizo:* A.1/A.2. *Guarda:* E4 marca (`sello_dinero.py:557-564`); `sello_previo()` no
distingue estados (`:287-304`), así que la fecha queda ocupada (`:346-363, 580-602`). §62/§90.6 (a)+(d) **firmado, no
aplicado**; al cerrar la corrida 15, PROPUESTA de política y parche en worktree, aplicación por acta posterior.
*Costo medido:* sesión del 28 fuera de N (contador 9), con **0 de 33 decisiones distintas** entre la barra intradía y el
cierre (la base lo dice); cupo de evidencia `ext_2026-09-28.*` ocupado por una matriz de media sesión, versionado en
`f7b65e0`. n = 1. *Opciones:* (i) negarse antes de escribir (sin fila y sin `ext_` cuando `ahora < cierre de la sesión
de hasta`) — deja la fecha libre para las 23:30 NY; con la no elegida se pierde el rastro en la base (queda en journal
y log) y es un camino nuevo en el sellador («un cambio por noche», §87). (ii) marcar **[E4, en producción]** + §62
(a)+(d) **[firmado]** — la fecha no queda quemada y el evento queda registrado. (iii) nada: cada despertar quema una
sesión de N y un cupo de evidencia. **Recomendación del agente: (ii) tal como está firmada en §90.6; hasta que se
aplique, la exposición es exactamente la del 28-sep.**

---

### C.9 Novena fila: cambio de calendario de un timer instalado

**Hechos, MEDIDOS (A.3).** El service arrancó **53 ms después** del fin de la recarga y **2,8 ms ANTES** del
`Stopped`/`Started` del timer. **`Persistent=false` no lo impidió** (`systemctl show`: `Persistent=no`).

**Cálculo (`systemd-analyze calendar`, systemd 259.5-0ubuntu3.4, sin tocar unidades).** Base = último disparo
(2026-09-29 00:35:00 Chile) + expresión nueva `Tue..Sat 00..03:05,35 America/New_York` → próximo **2026-09-29
01:05:00 −03, «21h ago»** (pasado a las 18:38:57). Misma base + expresión vieja `Mon..Fri 20..23:05,35` → 21:05:00
(futuro). Base = 18:38:57 + expresión nueva → 30-sep 01:05:00 (futuro). **Computado desde el último disparo, el
próximo caía en el pasado; computado desde el reinicio, en el futuro. La máquina hizo lo primero.**

**Lo que el manual documenta y lo que no (`man systemd.timer`, esta máquina).** `Persistent=` (p. 190-193): «When
the timer is activated, the service unit is triggered immediately if it would have been triggered at least once
during the time when the timer was inactive» — sólo para `true`. `OnCalendar=` (p. 106-108): un timer que venció
mientras el sistema dormía «will catch up and process all timers that triggered while the system was sleeping», y
si venció varias veces «will only result in a single service activation» — **es la premisa de §63, ahora con cita:
documentado y sin directiva que lo apague.** `DeferReactivation=` (p. 168-175): por defecto «the timer schedules
the next elapse based on the previous trigger time» y un elapse en el pasado «causing it to immediately trigger».
**No documenta** qué hace `daemon-reload` ni `restart` con un timer `Persistent=false` que cambió de calendario.

**INFERENCIA desde el orden del journal, no probada:** el disparo lo produjo la **recarga** (`daemon-reload`), que
releyó la unidad con el calendario nuevo y rearmó el timer desde el último disparo recordado; el `restart` llegó
cuando el service ya había arrancado. La hipótesis del acta §91.7/§91.8 (fue el `restart`) es compatible con el
segundo, no con el orden de las líneas. Distinguirlo exige una prueba en una unidad, prohibida en este bloque. Si
la inferencia es correcta, **evitar el `restart` no protege**: la recarga es obligatoria para cargar la unidad
editada.

**Opciones de procedimiento.** (P0) Medir la semántica —reload solo, restart, stop → editar → reload → start, con
`Persistent=` true y false— en una unidad desechable que ejecute `/bin/true`, un sábado: 15 minutos, acto de Nicolás,
fuera de esta corrida. (P1) Antes de cambiar un calendario: `systemctl --user list-timers` → columna `LAST` de esa
unidad; `systemd-analyze calendar --base-time='<LAST>' '<expresión nueva>'`; **si «From now» dice «ago», el cambio
dispara en el acto**: elegir otro momento u otra expresión, o aceptar el disparo sabiendo qué hace ese job (tabla de
abajo). (P2) Elegir el momento por job. (P3) Parar el timer antes de editar y recargar, y arrancarlo después: **no
probado**; para `true` el manual dice que al activar se dispara si hubo elapse durante la inactividad y no dice desde
qué base se computa; para `false` no dice nada. (P4) La guarda en el job (filas 1-8) es la única defensa que no
depende del procedimiento.

**Momentos en que un disparo inmediato es inocuo, por job [DEDUCIDO del código y de lo medido; n = 0 salvo donde se dice]:**
noticias: cualquiera (cuesta a lo sumo el tope). snapshot: día hábil después del sello (→ «ya existe snapshot de
hoy», **medido** 28-sep 18:15); **nunca sábado ni domingo**: sin exención de fin de semana en el código (`grep
weekday|is_session` vacío en `snapshot.py`) sellaría un snapshot con fecha sábado, `sox_fecha` viernes y objetivo
lunes, duplicando el del viernes; la (b) planificada lo deja pasar (historial: 2 de 60 snapshots en fin de semana,
4 y 5-jul, pre-4.6). reporte: después de las 18:25 (duplica el mismo texto). backup: después de las 18:40 (sin
cambios, no commitea). vigía y rechequeo: sábado o domingo (exentos) o después de su hora con el día en OK. sonda: no
hay momento inocuo hasta que el lector filtre fuera de grilla; el menos malo, un sábado de día (la fila va a la
sesión del viernes, post-cierre, y contamina esa noche). sellador: **entre las 00:35 y las 10:00 de Chile, de martes a
sábado** (fecha ya sellada → `ya_sellada` o divergencia sin pérdida); **nunca con la bolsa abierta** (E4 la marca y
quema la fecha) **ni entre el cierre y las 23:30 NY** (sellaría temprano con timing ok y lo que selle queda).

**Recomendación del agente:** (P1)+(P2) como procedimiento escrito en `systemd/INSTALACION.md`, y (P0) **antes** de
mover la hora del sellador por §58 (b)/(c), porque ahí un disparo inmediato quema una sesión de N.

---

### D. Huecos que quedan DESPUÉS de la corrida 15 [DEDUCIDOS del código; n = 0 eventos]

**D.1 Frescura.** Despertar de mañana en día hábil (antes de la apertura de NYSE, p. ej. 09:00 Chile): el snapshot se
dispara (catch-up de ayer), `date.today()` es hoy, `sox_fecha` es ayer (sesión cerrada) → la (b) pasa → sella el
snapshot de HOY con el cierre de AYER; a las 18:15 «ya existe» → **la sesión de hoy queda sellada con insumo viejo y el
verificador la acepta** (emisión antes de la apertura objetivo, `available_at < emisión`). El riel de dinero tiene
`insumo_fresco` para exactamente esto (`sello_dinero.py:559-571`); el de medición no. Cuenta histórica: **0 de 45**
snapshots con `sox_fecha ≠ fecha` en día de sesión XNYS (el único distinto, 7-sep, es feriado de NYSE). Opción posible:
negarse si hoy es sesión XNYS y `sox_fecha ≠ hoy` — cero falsos negativos históricos; un día con Yahoo atrasado dejaría
de sellar, el mismo trato que la (b).

**D.2 Fin de semana.** snapshot, reporte, backup y noticias no tienen exención de fin de semana en el código; sólo el
`Mon..Fri` del timer los frena. Un disparo inmediato en sábado (cambio de calendario, restart, o catch-up si la
máquina despierta el sábado después de perder el viernes) sella un snapshot con fecha sábado. Si el sello del viernes
existe, duplica su predicción (mismo insumo, mismo objetivo lunes); si el viernes se perdió, lo recupera con fecha
sábado (timing válido). Ningún exchange del universo abre sábado o domingo.

**D.3** La alerta del vigía con la (b): ~3,5 h abierta en vez de 11 s (C.5). **D.4** El rechequeo con el orden
inverso (C.6). **D.5** La sonda fuera de grilla post-cierre (C.7). **D.6** El sellador hasta aplicar §90.6 (C.8).
**D.7** El margen de 15 min desde el 2-nov para cualquier guarda que agregue margen (C.2).

---

### E. Hallazgos de paso, fuera del alcance, no corregidos

**E.1 `mki-noticias` no analiza nada desde el 7-sep, y todo dice «ok».** `data/noticias.log` tiene **17** líneas «análisis
falló en el lote 1: Error code: 400 … Your credit balance is too low to access the Anthropic API» (la primera en la
línea 39, `2026-09-07T20:52:21Z`); `data/costos_ia.log` líneas 25-41: **17 corridas seguidas con `analizados 0`, `costo_usd
0.0` y `resultado 'ok'`**, `pendientes_restantes` de 260 a **3.672**; la última con análisis fue el 4-sep (línea 24: 214
analizados, 0,116103 USD). El ledger dice «ok» porque `mki_noticias.py:123-128` corta el bucle en la excepción y
`:149-152` registra «ok» igual; el vigía repite «noticias: ok · 0 analizados · 0.0000 USD» (`vigia.log:230, 240`).
Consecuencia deducida, NO medida: `sentimiento_promedio_por_ticker()` alimenta el sello (`snapshot.py:180`) con análisis
de hasta el 4-sep bajo decaimiento 0,7^días y piso 0,1: los `sentimiento_ia`/`puntaje_ia` sellados desde el 7-sep se
apoyan en titulares viejos. No está en `DECISIONES.md` (grep: sólo el §79 sobre los créditos de la corrida 09). Va a
tarjeta o acta; este inventario no lo decide.

**E.2** `data/sombra_telegram.log` tiene mtime `2026-08-28 18:25:01 −04:00` (`ls --time-style=full-iso`): es del 28 de
**agosto**, el último reporte en sombra antes del switch del 30-ago (`reporte.log:5-6`). Cierra el ítem de diagnóstico
que el curador dejó en la corrida 14 («mtime de las 18:25 en una máquina titular»): mismo día, otro mes.

**E.3** El dictamen del auditor cita `mki_vigia.py:99` para `av == ts`; en el árbol actual es la línea **97**.

**E.4** Las dos unidades instaladas siguen con su `Description=` errada (`systemctl cat`): la sonda dice «la franja
de madrugada no está instalada» y el sellador «PROPUESTA no instalada». Edición manual de Nicolás (§90.9, §91.7).

---

### F. Lo que de §63 queda absorbido acá

1. Su premisa —**no hay directiva de `[Timer]` que suprima un disparo vencido durante una suspensión, y
   `Persistent=` gobierna otra cosa**— pasa a ser la premisa de las nueve filas, ahora **con cita del manual**
   (`OnCalendar=`, catch-up al reanudar con una sola activación) además de la medición del 28-sep.
2. Sus tres opciones para la sonda (guarda en el script / guarda en el lector / nada) son las (i)/(ii)/(iii) de la
   fila 7, con el dato nuevo de que el lector hoy no cubre «fuera de grilla post-cierre» (29-sep, 17:38 NY).
3. Lo que remitía a §61 y §62 quedó firmado en §90.1 y §90.6; acá sólo se sitúa.
4. Su errata de `Description=` sigue vigente (E.4).
5. Su hallazgo de que «el evento se reconstruye del hueco más el PID sobreviviente» se afina en A.5: dos relojes
   independientes acotan la pausa al viernes 25 a las 03:37, ±30 s.
Nada de §63 se pierde; el orquestador la marca FUNDIDA.

---

### G. Lo que este inventario NO midió

- **Hay un solo despertar y un solo cambio de calendario.** Ninguna tasa, ninguna extrapolación.
- **La suspensión es inferencia.** WSL2 no anota suspend/resume; lo medido son dos relojes que coinciden (A.5) y el
  hueco del journal del sistema (medido por el orquestador, bitácora 15 §0.10). La causa (suspensión del host) es
  testimonio. Los logs del lado Windows no se leyeron. El cómputo de A.5 supone una sola pausa.
- **Los textos de Telegram no existen en ningún log en modo titular**: sólo largos (`reporte.log`) y «enviada»
  (`vigia.log`, `snapshot.log`). Qué decían se deduce del código y del sello.
- **Cuál de `daemon-reload`/`restart` disparó la sonda el 29-sep**: inferido del orden de las líneas, no probado.
- **Cómo se comportan los jobs con las guardas planificadas**: deducido; el árbol leído era `2f73eb2`, sin ellas.
- **Los escenarios de la mañana y del sábado (D.1, D.2)**: deducidos, cero eventos.
- **Cuánto habría gastado noticias con crédito**: no medido.
- `puntaje_v0`, `puntaje_ia` y `divergencias` del 28-sep: siguen sin medir (bitácora 14 §9.5-bis); el 44 contra 17 de
  `roca_chip` sigue PROVISIONAL, con el dato nuevo de C.2.
- No se abrieron `noticias.db` ni `alertas.db`; no se corrió ningún job, ningún test ni ninguna función del motor;
  no se leyó `.env`; el journal del sistema no lo leyó este bloque (sólo cita el dato del orquestador).
- El arranque fuera de calendario del 25-ago (A.4) no se investigó.

**No se eligió nada.**
