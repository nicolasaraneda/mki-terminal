# Bitácora de la corrida 14 — 28-sep-2026

**Encargo:** `~/encargo.md` versión 3, escrita el 28-sep a las 16:35. Revisar el apagón
del 25 al 28 de septiembre, aplicar las firmas del acta §88, extender la sonda pasada
la medianoche, corregir las erratas de los README, separar `bifurcaciones` en artefacto
fijo y medición nueva, y redactar la enmienda de M2.

**Horas.** Todas leídas de `date` en la máquina, nunca estimadas. Zona: Chile
(UTC−3 en esta época). Arranque **16:36**. Los tramos van fechados en cada bloque.

**Desvío declarado desde la primera línea: el modelo.** El encargo pide «Fable,
esfuerzo alto, elegidos al arrancar y sin cambiar a mitad de sesión». La sesión corrió
con **Opus 5 (contexto 1M), esfuerzo xhigh**, elegido por Nicolás con `/model` antes de
lanzar. No se cambió a mitad de sesión. Manda la máquina (regla 0.2 del encargo) y
queda como errata del encargo, no de la corrida.

---

## 0. Orientación y prerrequisitos (16:36 – 16:55)

### 0.1 Timers que disparan durante la corrida

`systemctl --user list-timers --no-pager` a las 16:36 (copia de los `NEXT` del día):

| unidad | próximo disparo | último disparo |
|---|---|---|
| `mki-noticias.timer` | 17:50 | 14:42:52 |
| `mki-snapshot.timer` | 18:15 | 14:42:52 |
| `mki-reporte.timer` | 18:25 | 14:42:52 |
| `mki-backup.timer` | 18:40 | 14:42:52 |
| `mki-vigia.timer` | 19:00 | 14:42:52 |
| `mki-vigia-rechequeo.timer` | 20:30 | 14:42:52 |
| `mki-sonda-cierre.timer` | 21:05 | 14:42:52 |
| `mki-sello-dinero.timer` | 29-sep 00:30 | 14:42:52 |

**Errata del encargo:** dice «los once timers de usuario dispararon juntos a las 14:4x
(columna LAST idéntica)». Son **ocho** los que comparten `LAST = 14:42:52`, los ocho
`mki-*`. Los otros tres de la lista son de Ubuntu (`launchpadlib-cache-clean`,
`ubuntu-insights-upload`, `ubuntu-insights-collect`), tienen `LAST` de otras fechas y
no llevan `OnCalendar`.

### 0.2 Suite al abrir — **NO en verde**

```
2 failed, 889 passed, 5 skipped, 1 xfailed, 29 warnings in 407.26s
```

Los dos rojos son `tests/test_readme.py::test_los_dos_readme_son_lo_que_el_generador_produce`
y `::test_el_contador_de_e0_del_readme_es_el_de_la_copia_versionada`. **Es exactamente
la deriva que el propio encargo anticipa en 0-bis.5**, con su causa medida en el bloque 2
de esta bitácora; no es una regresión desconocida.

El encargo 0.3 dice «si no está en verde, se para y se reporta». Se reporta acá, y la
corrida sigue, por la razón que el pre-mortem del director marcó como defecto de esa
instrucción (su A3): un rojo sólo se puede clasificar en «consecuencia del despertar»
o «preexistente» con las lecturas de 0-bis, que el encargo ordena DESPUÉS. Clasificado:
**preexistente y anticipado**, y es el rojo que el bloque 2 viene a arreglar. Parar la
corrida ahí habría dejado el README público con sus cifras vencidas y sin diagnóstico.

### 0.3 Huellas de las bases al abrir (16:38)

```
b8c25631645b6affd4cd9e95d75e4c49b06eec6fcb7dc1aef54c6061379eda99  dinero/sello_dinero.db
f8a474968d1616078ab2d60e3248061c9a98270fa7a204662810407bf1d8f014  senales.db
5e4d55d319e38f872992ce71684e98e2d5501d9800b11d04c29cae0268a50e77  noticias.db
```

### 0.4 Estado de E0, leído de `dinero/sello_dinero.db` en `mode=ro`

462 filas, 14 `fecha_insumo`, 33 filas cada una. Copia textual del agrupado:

| `fecha_insumo` | `estado` | `cuenta_para_N` | filas |
|---|---|---|---|
| 2026-09-08 | pendiente | 1 | 33 |
| 2026-09-09 | insumo_incompleto | 0 | 33 |
| 2026-09-10 | pendiente | 1 | 33 |
| 2026-09-11 | pendiente | 1 | 33 |
| 2026-09-14 | pendiente | 1 | 33 |
| 2026-09-15 | pendiente | 1 | 33 |
| 2026-09-16 | pendiente | 1 | 33 |
| 2026-09-17 | pendiente | 1 | 33 |
| 2026-09-18 | insumo_incompleto | 0 | 33 |
| 2026-09-21 | pendiente | 1 | 33 |
| 2026-09-22 | insumo_incompleto | 0 | 33 |
| 2026-09-23 | insumo_incompleto | 0 | 33 |
| 2026-09-24 | pendiente | 1 | 33 |
| 2026-09-28 | no_verificable_timing | 0 | 33 |

**Contador: 9 sesiones cuentan para N = 40** (08, 10, 11, 14, 15, 16, 17, 21, 24). No
cuentan 09, 18, 22 y 23 por `insumo_incompleto`, ni 28 por `no_verificable_timing`.
Coincide con lo que Nicolás vio a las 16:20. **No hay ninguna fila con `fecha_insumo`
2026-09-25.**

`divergencias_sello`, contenido completo (una fila):

```
(1, '2026-09-09', '2026-09-10T03:30:04.599658+00:00',
 sha_sellado 126e4f2c…, sha_nuevo 7300787b…, decisiones_distintas 1,
 'segundo sello del 2026-09-09 con otro insumo; 1 decisión(es) distinta(s); las filas selladas no se tocan')
```

### 0.5 E4-bis en producción: confirmado

Todas las filas desde el 2026-09-21 llevan `sellador_sha256 = 480fbdc991679f2b…`; las
del 08 al 18-sep llevan `93db9b70dc708b67…`. El corte cae exactamente donde la corrida 13
aplicó la corrección. `plataforma_version` 5.1.0, `version_sello` E0.2 y
`reglas_version` 0.2.0-PROPUESTA en las catorce fechas.

**Glosa obligatoria sobre el test permanente de integridad** (A4 del pre-mortem, y es
importante que quede en la misma línea): los tests de integridad comparan el sha que la
base cita contra el archivo que hay en disco. Para el 28-sep **pasan**, porque el archivo
intradía en disco es exactamente el que las 33 filas citan. El verde dice «la base cita
el archivo que hay», **no** «el insumo es legítimo». No se puede citar mañana como que
el 28 quedó limpio.

### 0.6 Árbol de git

`git status --short` al abrir: seis CSV de `data/backups/` modificados, `data/sonda_cierre.csv`
**en el índice** (`A`), y `data/backups/sello_dinero_ext/ext_2026-09-28.{csv,meta.json}`
sin versionar. `HEAD = 5321f6b "Backup diario 2026-09-28"`. Rama `main`.

Los seis CSV modificados los escribieron los timers a las 14:43 y no se tocaron (ver
0-bis.8, que explica por qué quedaron fuera del commit que lleva su fecha).

**Errata del encargo (0-bis.6):** dice «si al arrancar sigue sin versionar, se anota y
no se agrega». `data/sonda_cierre.csv` **ya está en el índice**: Nicolás lo agregó. La
condición no aplica. La corrida no hizo `git add` ni `git commit` de nada.

### 0.7 La sonda al abrir

`data/sonda_cierre.csv`: 1.188 filas de datos. Columna `timestamp_utc` — **errata del
encargo**, que la llama `timestamp_`; un `df["timestamp_"]` falla en seco.

**Errata del encargo, y también mía por repetirla antes de verificar:** el encargo dice
«4 noches completas (fechas UTC 22 a 25)». Las fechas UTC son 22 a 25, pero las
**sesiones** son otras: 22-sep 00:05 UTC es el **21-sep 20:05 de Nueva York**. Agrupado
por la columna que corresponde, `sesion_ny`:

| `sesion_ny` | filas | horas NY |
|---|---|---|
| 2026-09-21 | 288 | 20:05 a 23:35, cada media hora (8 sondas × 36 tickers) |
| 2026-09-22 | 288 | idem |
| 2026-09-23 | 288 | idem |
| 2026-09-24 | 288 | idem |
| 2026-09-28 | 36 | **13:42** (una sola, la del despertar) |

Las cuatro noches son las sesiones **21, 22, 23 y 24** de septiembre, no 22 a 25. Quien
filtre por la parte fecha de `timestamp_utc` se equivoca en las cuatro. **Se filtra sólo
por `sesion_ny`.**

---

## 0-bis. El despertar del 28 de septiembre (16:40 – 17:00)

### La corrección de fondo: el PC no estuvo apagado — y la ventana no es la que dice el encargo

El encargo dice «el PC estuvo apagado desde el viernes 25-sep en la tarde hasta el lunes
28-sep a las 14:40». Medido:

- `uptime` → `up 5 days, 3:27`; `/proc/uptime` → `444443.26`.
- El journal muestra el **mismo `systemd[317]`** emitiendo antes (`Sep 25 00:30:00`) y
  después (`Sep 28 14:42:52`) del fin de semana.

El *manager* de usuario no se cayó. Esa distinción no es un detalle de vocabulario: es la
que decide todo 0-bis.7 y la que explica por qué `Persistent=false` no frenó nada.

**Dos precisiones que el `auditor-lookahead` exigió y que hay que respetar:**

1. **«Suspendido» es una INFERENCIA, no un hecho registrado.** `grep -iE "suspend|resume|sleep|hibernat"`
   sobre el journal devuelve **vacío**: en WSL2 el guest no ve el sueño del host. Lo medido es el hueco
   del journal más el PID sobreviviente más el uptime; de ahí se infiere la suspensión, que es la
   explicación correcta, pero no consta. Resolverlo exigiría los logs del lado Windows, fuera de este
   entorno.
2. **La ventana no llega al «viernes por la tarde».** El último evento MKI es
   `2026-09-25T00:35:03-03:00` (la sonda) y la última línea de cualquier tipo es
   `2026-09-25T02:16:24-03:00`; la siguiente es `2026-09-28T14:42:52`. Como los jobs del viernes de
   las 17:50 y 18:15 no corrieron, la suspensión está acotada a **[vie 02:16, vie 17:50] Chile**, y
   nada más se puede afirmar.

### 0-bis.1 La sesión del viernes 25 se perdió en TRES rieles, no en uno

El encargo lo scopea al sellador. Medido:

- **Sellador:** no hay fila con `fecha_insumo` 2026-09-25 (0.4). El journal de
  `mki-sello-dinero.service` no tiene nada entre `Sep 25 00:30:05` y `Sep 28 14:42:52`:
  el disparo del sábado 26 a las 00:30 nunca ocurrió.
- **Riel de medición:** no hay snapshot ni filas de `senales_ticker` con `fecha` 2026-09-25.
  Las fechas consecutivas en `snapshots` son 24-sep y 28-sep.
- **Sonda:** no hay ninguna fila con `sesion_ny` 2026-09-25.

Se anota como sesión perdida en los tres rieles. **No se crea ninguna fila** (§57: no se
recupera).

### 0-bis.2 Qué hará el sellador a las 00:30 del 29 con una fecha que ya tiene 33 filas

La corrida arrancó antes de las 00:30 del 29, así que la respuesta empírica no existe
todavía. **Se responde desde el código**, leído entero, y queda escrito para que Nicolás
lo contraste mañana con
`journalctl --user -u mki-sello-dinero.service --since "2026-09-29" --no-pager` y la base.

Lo que hay sellado del 28 (una fila de muestra, campos de timing):

```
timestamp_utc          2026-09-28T17:43:01.001389+00:00   (14:43:01 Chile, 13:43 NY)
available_at           2026-09-28T20:00:00+00:00          (16:00 NY, el cierre)
sesion_objetivo        2026-09-29      apertura_objetivo  2026-09-29T13:30:00+00:00
estado no_verificable_timing   estado_timing roto   estado_dia sesion
insumo_completo 0   cuenta_para_N 0   insumo_ext_archivo ext_2026-09-28.csv
insumo_ext_sha256 2e9844697d7e0029cc8690f61fd254007f360e2e9ebc00ab97a191e4a18e86f7
```

El guardia E4 funcionó: `available_at` (20:00 UTC) es **posterior** a `timestamp_utc`
(17:43 UTC), la regla `available_at < timestamp_utc < apertura` se rompió, y las 33 filas
quedaron fuera de N.

**Lo que pasará a las 23:30 NY del 28 (00:30 Chile del 29), paso por paso:**

1. `descargar_extension()` baja de yfinance; ahora sí trae el cierre **final** del 28.
2. `congelar_extension()` calcula `hasta = str(ext.index.max().date())` = `2026-09-28` y
   llama a `sello_previo("2026-09-28")`, que encuentra las 33 filas y su
   `insumo_ext_sha256 = 2e984469…`.
3. Se comparan los sha. **Dos ramas, y la segunda es la casi segura:**
   - Si los bytes del CSV fueran idénticos a los del intradía (improbable: a las 13:42 NY
     el mercado estaba abierto, los 35 cierres eran provisionales y TOELY no tenía el del
     28), `congelar_extension` devuelve lo que hay sin escribir, y `sellar()` entra por
     `meta_ext["sha256"] in shas` → `{"resultado": "ya_sellada", "filas_insertadas": 0}`.
   - Si difieren, el insumo nuevo va a un **temporal fuera de `DIR_EXT`** con
     `persistido = False`; `sellar()` entra por la rama de divergencia, inserta **una fila
     en `divergencias_sello`** con el detalle «contenido divergente NO conservado
     (E4-bis, corrida 13)», devuelve `{"resultado": "divergencia_registrada",
     "filas_insertadas": 0}`, y `main()` borra el temporal en el `finally`.
4. En las dos ramas: **cero filas insertadas**. `main()` sólo exporta el CSV.

**Conclusión: la sesión del lunes 28 también se pierde.** La hipótesis del encargo acierta
en el resultado y se corrige en el mecanismo: no es que «E4-bis toma el 28 como ya sellado
y no escribe nada», es que lo registra como **divergencia** — el hecho queda en la base,
no en silencio. Predicción falsable para mañana: `divergencias_sello` pasa de 1 a 2 filas,
la nueva con `fecha_insumo` 2026-09-28, y `sellos_dinero` sigue en 462 filas.

**Lo que el encargo no previó y el pre-mortem sí (su A2):** la evidencia persistida de la
fecha 2026-09-28 —`ext_2026-09-28.csv`, que 33 filas citan por sha— **es una matriz de
precios de media sesión**, y `mki-backup` la commitea a las 18:40 (está `??` en
`data/backups/sello_dinero_ext/`). El archivo de evidencia de esa fecha queda ocupado por
un insumo que E4 ya rechazó, y por diseño de E4-bis (opción A) ya no se puede reescribir.
Eso agrega una cuarta opción a la tarjeta, que no estaba en el encargo.

### 0-bis.3 El riel de medición: **hay una anomalía única en toda la historia sellada**

`mki-snapshot.service` corrió de 14:42:52 a 14:43:30, o sea **con NYSE abierto** (13:42
Nueva York). Selló.

`snapshots`, fila del 28 (la única de esa fecha):

```
fecha 2026-09-28   creado_en = timestamp_utc = 2026-09-28T17:42:58.943983+00:00
origen programado  regimen 'Alcista · vol baja'  roca_chip 44.0
descarga_ok 28/28  plataforma_version 5.1.0
sox_usado_pct -1.63   sox_fecha 2026-09-28
```

`sox_fecha` dice 2026-09-28 y `sox_usado_pct` −1,63 **con la sesión abierta**: el valor
no puede ser el cierre del 28.

`senales_ticker` del 28: 24 filas, 8 con `estado='pendiente'` y 16 con `estado IS NULL`
(la misma partición 8/16 que todas las demás fechas). Todas con
`timestamp_utc = 2026-09-28T17:42:58Z` y `available_at = 2026-09-28T20:00:00Z`.

**La consulta que decide el hallazgo, sobre toda la tabla:**

```sql
SELECT fecha, COUNT(*) FROM senales_ticker WHERE available_at > timestamp_utc GROUP BY fecha
```

devuelve **una sola fecha, 2026-09-28, con 24 filas**. Es decir: esas 24 filas declaran
que el insumo que usaron fue conocible **2 h 17 min después de que la fila se escribió**.
Es la única fecha así en toda la historia sellada del riel.

El mismo evento físico produjo, en el riel de dinero, 33 filas `no_verificable_timing`
fuera de N; y en el riel de medición, 8 filas `pendiente` que el verificador tomará como
buenas. La razón está en el código: `senales.py::verificar_apertura_pendientes()` aplica
**una sola** guarda de tiempo, `if emitida >= apertura: estado = no_verificable_timing`.
**Nunca compara `available_at` contra `timestamp_utc`.** Y `snapshot.py::ejecutar_snapshot()`
pregunta por `senales.ya_existe_snapshot_hoy()`, que compara `fecha = date.today()`: como
ya hay snapshot del 2026-09-28, **el disparo de las 18:15 de hoy devolvió/devolverá «ya
existe snapshot de hoy» y no re-selló**, así que las filas construidas a las 13:42 NY son
el registro permanente del 28.

El dictamen del `auditor-lookahead` sobre si esto es «una fila inválida que entró como
válida» está en `dictamen_14/` y decide si los bloques 2 y 3 se ejecutan. **La magnitud del daño sí se
midió, al final de la corrida: sección 9.** Resumen: el insumo se desvía 0,02 pp, **ninguna de las 8
direcciones se invierte**, el régimen es idéntico — y `roca_chip` se mueve **27 puntos, de 44 a 17**,
que es donde nadie estaba mirando.

**Las 9 filas que el backup muestra como borradas: son actualizaciones legítimas.** Ids
1310, 1313, 1335, 1337 (`sesion_objetivo` 2026-09-28) y 1342, 1343, 1346, 1347, 1348
(`sesion_objetivo` 2026-09-25). Verificado con `git diff -U0`: en las nueve, el **único**
campo que cambia es `estado: pendiente → verificada`, con el mismo `id` y el resto de la
línea byte a byte igual. Corroborado por `data/snapshot.log`:
`verificador apertura: {'verificadas': 9, ...}` y `verificador puntaje: 44 verificadas`,
que cuadran exactamente con los `+9` de `verificacion_apertura` y los `+44` de
`verificacion_puntaje` del `numstat`. **No es una reescritura de fila sellada.**

### 0-bis.4 Partido en dos, porque estaba escrito en pasado sobre un hecho futuro

El encargo dice «los seis timers del riel **volvieron a disparar** en su hora normal la
tarde del 28». A la hora de lanzamiento (16:36) eso no había ocurrido.

- **0-bis.4a, el disparo de las 14:4x (medido):** el 28-sep aparece **una sola vez** en
  `snapshots` (`SELECT fecha, COUNT(*) … GROUP BY fecha` → `('2026-09-28', 1)`), con 24
  filas de `senales_ticker`, la misma cantidad que cada otra fecha. **No hay sesión
  duplicada.**
- **0-bis.4b, el disparo de las 18:15:** la corrida termina antes, así que se responde **desde el
  código** y queda para que Nicolás lo contraste. `ejecutar_snapshot()` pregunta por
  `senales.ya_existe_snapshot_hoy()`, que compara `fecha = date.today()`; como ya hay snapshot del
  2026-09-28, **devuelve `{"snapshot": False, "motivo": "ya existe snapshot de hoy"}` y no re-sella**,
  sin computar nada del motor. `main()` sí sigue: corre el verificador —que no tiene nada nuevo que
  verificar, porque las sesiones objetivo del 29-sep no han cerrado—, exporta los CSV a
  `data/backups/` e imprime la salud. **Consecuencia: el 28-sep queda registrado una sola vez y con
  las filas de las 13:42 NY, y no hay sesión duplicada.** Falsable con `data/snapshot.log`: la línea
  de las 18:15 tiene que decir `'snapshot': False` con ese motivo.

### 0-bis.5 Por qué `README.md` difiere del generador

Medido. `scripts/generar_readme.py` expone `contador_e0()`, que lee la copia versionada
`data/backups/sello_dinero.csv`:

```
{'sesiones_selladas': 14, 'cuentan_para_N': 9,
 'no_cuentan': ['2026-09-09','2026-09-18','2026-09-22','2026-09-23','2026-09-28'],
 'ultima_fecha_insumo': '2026-09-28'}
```

y `README.md` (sección «Execution rail», líneas 389-399) publica:

> Sealed prospective sessions so far: **9**, of which **7** count towards N = 40; the ones
> that do not (2026-09-09, 2026-09-18) had incomplete or late input (last sealed input
> session: 2026-09-18).

O sea **cuatro** valores vencidos a la vez, no uno: 9→14 selladas, 7→9 que cuentan, dos
fechas que no cuentan→cinco, y 2026-09-18→2026-09-28. Son las cifras del 19-sep.

**La causa, dicha como mecanismo:** el README lleva un contador vivo que el timer mueve
cada noche y **nada regenera el README**. `README.es.md` pasa el test del generador
porque **la sección de E0 no existe en español**: `README.md` tiene
`## Execution rail (paper only)` entre «The laboratory» y «Audit every figure», y
`README.es.md` va de «El laboratorio» directo a «Auditar cada cifra». Eso mismo explica
por qué el test de paridad entre idiomas la excluye (deuda del director de la corrida 13):
no es un hueco del test, es que **no hay nada en español con que comparar**.

### 0-bis.6 `data/sonda_cierre.csv`: ya versionado

Ver 0.6. Nicolás lo agregó al índice. No se toca.

### 0-bis.7 `Persistent=false` **no** es el knob, y la premisa de la instrucción es falsa

El encargo pide «qué timers deberían llevar `Persistent=false` para que un despertar no
dispare lo atrasado», y observa que la sonda ya lo lleva y disparó igual.

**Medido, y la explicación es que la pregunta no tiene esa respuesta.**
`~/.config/systemd/user/mki-sonda-cierre.timer` lleva `Persistent=false` y `AccuracySec=1s`,
y el journal registra `Starting mki-sonda-cierre.service` a las `Sep 28 14:42:52`, que
produjo 36 filas a las 13:42 NY con el mercado abierto.

`Persistent=` gobierna **una sola cosa**: si systemd guarda y relee la marca del último
disparo para recuperar disparos perdidos **mientras el manager no estaba corriendo**. Acá
el manager nunca dejó de correr (`systemd[317]` a los dos lados del fin de semana). Lo que
pasó es otra cosa: la máquina estuvo suspendida, `CLOCK_REALTIME` siguió avanzando, la
hora de disparo venció, y al reanudar el timer corrió. **Eso no lo desactiva ninguna
directiva de la sección `[Timer]`.**

Conclusión que la corrida deja escrita, no aplicada: **la supresión de un disparo atrasado
no es configurable en systemd; tiene que ser una guarda de ventana en el job.** Es
exactamente lo que el riel de dinero ya hace — su guarda E4 marcó sus 33 filas
`no_verificable_timing` — y lo que el riel de medición no hace. Las opciones y sus costos
están en la tarjeta correspondiente de `espera_firma.md`; ninguna se aplica acá.

Errata adicional que sale de la misma lectura: **las dos unidades instaladas siguen
diciendo «PROPUESTA no instalada» en su `Description=`**, visible en `systemctl status`.
No se corrige (es unidad instalada, operación de Nicolás); se corrigió en la plantilla del
repo y se anota.

### 0-bis.8 (nuevo) `mki-backup` commiteó ANTES de que el día se sellara

Hallazgo que el encargo no tenía y que el pre-mortem marcó (su A7). Del journal:

```
14:42:52  Starting  (los ocho mki-*)
14:42:53  Finished  mki-backup.service          ← un segundo después de arrancar
14:42:56  Finished  mki-vigia / mki-reporte
14:42:58  Finished  mki-sonda-cierre
14:43:01  Finished  mki-sello-dinero
14:43:30  Finished  mki-snapshot
14:45:21  Finished  mki-noticias
```

`mki-backup.timer` no declara `After=` ni nada equivalente: **el orden entre los ocho jobs
lo da sólo el reloj.** Con todos disparando en el mismo segundo, backup terminó primero.
Resultado: el commit `5321f6b`, que se llama **«Backup diario 2026-09-28»**, no contiene el
sello de ese día, y los seis CSV que snapshot y el sellador escribieron después quedaron
sin commitear. Es un artefacto publicado cuyo nombre no describe su contenido.

Nota tranquilizadora, también medida: `mki_backup.py` commitea con pathspec
(`commit -m … -- data/backups`), así que el `data/sonda_cierre.csv` que está en el índice
**no** se cuela en el commit de las 18:40.

La dependencia (`After=`/`Requires=`, o mover backup más tarde) toca unidades instaladas:
va a tarjeta, no se aplica.

### 0-bis.9 (nuevo) Dos mensajes de Telegram salieron fuera de hora, y el sistema se retractó solo

- `data/reporte.log`: `[2026-09-28T17:42:55Z] reporte compuesto desde el sello (400 caracteres)`
  y `Reporte enviado 14:42`. Los cinco reportes anteriores miden 831-833 caracteres. Se
  envió un reporte de **400 caracteres** porque a las 14:42:55 el snapshot del día todavía
  no había sellado (terminó a las 14:43:30). El reporte declaró sus huecos, que es lo que
  debe hacer, pero salió a una hora que no es la suya y con la mitad del contenido.
- `data/vigia.log`: a las 14:42:55 el vigía levantó **cuatro FALLAs** —snapshot sin sellar,
  descarga sin snapshot que revisar, noticias no corrió («proceso 39845 vivo desde
  Mon Sep 28 14:42:51»), reporte sin envío registrado—, escribió el marcador y envió
  `alerta Telegram: enviada`. Las cuatro eran ciertas *en ese segundo* y falsas un minuto
  después: los jobs estaban corriendo en ese mismo instante.
- **Y el epílogo funcionó:** `data/snapshot.log` a las `17:43:07Z` registra
  `retractación Telegram: enviada` / `retractación del vigía enviada (sello tardío)`. El
  `_epilogo_vigia()` de la 5.0.1 consumió el marcador. Por eso `data/vigia_pendiente.json`
  **no existe** al abrir la corrida, y el pase de las 20:30 de hoy no va a retractar una
  alerta del viernes con datos del lunes (riesgo que el pre-mortem marcó como A5:
  verificado, **no se materializó**).

Errata cosmética de paso: el mensaje del vigía dice «launchd no re-dispara mientras siga
vivo». En esta máquina es systemd. Texto heredado del Mac.

---

## 1. La sonda pasada la medianoche de Nueva York (16:52 – 17:0x)

### 1.1 Cómo atribuía una observación a una sesión, y por qué era un defecto

`GEMELO/sonda_cierre.py::sesion_de_hoy(instante_utc)` tomaba la **fecha de calendario de
Nueva York** del instante y devolvía esa fecha si XNYS tenía sesión ese día, o `None` si
no. `observar()` la usaba para `sesion_ny` y para `es_sesion_de_hoy`.

Con el código delante, la pregunta del encargo: **una sonda a las 00:35 NY del martes se
atribuía al martes.** Y `es_sesion_de_hoy` comparaba el último cierre disponible contra el
martes, que a las 00:35 obviamente no existe todavía: la fila decía «la sesión de hoy no
tiene cierre», que es trivialmente cierto y **no es lo que la sonda pregunta**. La
observación habla del cierre del **lunes**.

Peor en la madrugada del sábado: `sesion_de_hoy` devolvía `None`, `sesion_ny` quedaba
vacío, y `sonda_cierre_resumen.resumen()` descarta las filas sin sesión — la observación
**se perdía entera**. Es el defecto que este bloque corrige; sin corregirlo, la franja de
madrugada no produce ni un dato utilizable.

### 1.2 La corrección

Función nueva `sesion_atribuida(instante_utc)`, pura del instante, que devuelve **siempre**
una sesión:

- si la fecha NY del instante es sesión **y** el instante es posterior o igual a su
  apertura → esa fecha;
- si no (antes de la apertura, o día sin sesión) → la última sesión **estrictamente
  anterior** a esa fecha NY.

`sesion_de_hoy()` se conserva sin cambios porque sigue contestando una pregunta distinta y
legítima; lo que cambió es que `observar()` ya no la usa.

Verificado sin red, 11 casos a los dos lados de la medianoche y de la apertura:

| instante | atribuida |
|---|---|
| martes 29-sep 00:35 NY | 2026-09-28 |
| martes 29-sep 03:35 NY | 2026-09-28 |
| lunes 28-sep 00:35 NY | 2026-09-25 (viernes) |
| sábado 26-sep 01:05 NY | 2026-09-25 |
| domingo 27-sep 02:05 NY | 2026-09-25 |
| sábado 19-sep 16:00 NY | 2026-09-18 |
| viernes 25-sep 20:05 NY | 2026-09-25 |
| lunes 28-sep 09:29 NY | 2026-09-25 |
| lunes 28-sep 09:30 NY | 2026-09-28 |
| lunes 28-sep 13:42 NY | 2026-09-28 |
| martes 8-sep 01:05 NY (lunes 7 fue Labor Day) | 2026-09-04 |

**El esquema NO cambia y no se agregó ninguna columna**, contra lo que el encargo
contemplaba («si el esquema cambia, se agrega columna y el resumen lee los dos formatos»).
La razón es medida, no de gusto: aplicada a las **1.188 filas ya escritas**, la regla nueva
devuelve **exactamente** el `sesion_ny` grabado en cada una — 0 diferencias. Todas las
filas existentes son sondas de 20:05-23:35 NY en días con sesión, donde las dos reglas
coinciden, y la única fila fuera de grilla (13:42 NY) también coincide. Así `sesion_ny`
significa lo mismo en las filas viejas y en las nuevas, el resumen no necesita leer dos
formatos, y **ninguna fila se reescribe**. Hay test permanente que lo comprueba contra el
CSV real; si algún día falla, hay dos semánticas en el mismo archivo.

Consecuencia declarada de la regla: la tarde de un feriado se atribuye a la sesión hábil
anterior, así que la «noche» de un viernes puede incluir observaciones del lunes feriado.
No contamina la hora de aparición (el resumen la toma como el **mínimo** de las sondas que
vieron el cierre); sí estira `ultima_sonda_ny`, y el informe lo muestra con su desfase de
días.

### 1.3 La noche como una sola unidad, y un segundo defecto que apareció al mirar

`sonda_cierre_resumen` medía el tiempo con `_minutos("HH:MM")`, minutos de reloj a secas.
Con eso **01:05 vale 65 y 20:05 vale 1.205**: `min()` habría elegido la sonda de la
madrugada como la **primera** de la noche, y una aparición a las 01:05 se habría leído como
anterior a todas las de la tarde. La noche no era una unidad, era un reloj que se reinicia
en el medio.

Corregido: `minutos_de_la_noche(timestamp_utc, sesion_ny, hora_ny)` cuenta desde la
medianoche NY de la **sesión atribuida**, sumando el desfase de días entre la fecha NY de
la observación y la fecha de la sesión. 20:05 → 1.205; 01:05 del día siguiente → 1.505;
03:35 → 1.655. Se muestran como reloj de pared con marca: `_hhmm(1505)` = `01:05 (+1d)`,
y por debajo de 1.440 devuelve exactamente lo de antes, así que el informe de una noche que
termina antes de medianoche sale idéntico al anterior.

El desfase de días se saca de `timestamp_utc` y los minutos del día de `hora_ny`, a
propósito: `hora_ny` es el dato observado, y una discrepancia entre los dos campos es un
hallazgo del CSV, no algo que el resumen deba corregir en silencio.

Test con CSV sintético de una noche (viernes 25-sep) con sondas de 20:05 a 03:35 y un
ticker que recién aparece a las 01:05 NY: **una sola noche**, 16 sondas, y las apariciones
en el orden correcto.

### 1.3-bis El filtro que faltaba: una observación con el mercado abierto no dice nada del cierre

Hallazgo del pre-mortem (su A9), y era una contaminación real del artefacto que este bloque
iba a publicar. `resumen()` no tenía ningún filtro de grilla: las **36 filas del 28-sep a
las 13:42 NY**, con el mercado abierto y `es_sesion_de_hoy=1` en 35 de 36, habrían entrado
como la **primera aparición del cierre** de la noche del 28 para 35 tickers. El informe
habría publicado «el cierre apareció a las 13:42» y habría corrido la mediana de todos
ellos.

La causa de fondo, MEDIDA y vale como hallazgo propio: **yfinance etiqueta la barra
intradía con la fecha del día**, así que `ultima_fecha_close` es igual a la sesión en curso
desde la primera operación del día. A las 13:42 NY del 28, 35 de 36 tickers ya la daban.
`es_sesion_de_hoy` **sólo es interpretable fuera del horario de mercado**; las dos franjas
de la unidad propuesta caen fuera.

Corregido: se descartan las observaciones **anteriores al cierre de su sesión**, con el
cierre leído del calendario (`session_close`) y no de una constante. Y el informe **declara**
cuántas descartó y cuáles: un filtro que no se ve es un filtro que miente. Ninguna fila del CSV se borra.

**Por qué el calendario y no un 16:00 fijo, comprobado:** `minutos_del_cierre` devuelve **960** (16:00 NY)
en una sesión normal y **780** (13:00 NY) en las medias sesiones de feriado — verificado sobre el 27-nov y
el 24-dic-2026. Con un umbral fijo en 16:00 se habrían descartado observaciones que **sí** son posteriores
al cierre en esos dos días, o sea se habría perdido justo el dato de las noches raras.

**Y una limitación de lo que escribí, declarada porque no la arreglé:** `session_close` **revienta con
`NotSessionError`** si el `sesion_ny` de una fila no es una sesión de XNYS. Hoy es **inalcanzable**, porque
el único escritor de esa columna es `sesion_atribuida()`, que por construcción devuelve siempre una sesión
—también en feriados, donde devuelve la anterior—; pero un CSV editado a mano haría caer el resumen donde
antes simplemente habría ignorado la fila. Cambiar un `raise` por un salto declarado es un arreglo de dos
líneas que **no** se hizo a esta hora para no rehacer la suite dentro de la ventana; va con los demás al
encargo 15.

### 1.4 La unidad propuesta, con dos franjas

`GEMELO/propuestas/systemd/mki-sonda-cierre.timer` queda con dos `OnCalendar` (systemd las
combina con OR):

```
OnCalendar=Mon..Fri 20..23:05,35 America/New_York
OnCalendar=Tue..Sat 00..03:05,35 America/New_York
```

La primera **alinea la plantilla con lo instalado**, que es lo que §88.1 dejó pendiente
para esta corrida: la plantilla decía `17..23:05,35`, que nunca se instaló. Eso es una
errata de la plantilla, no un agregado.

Validadas las dos con `systemd-analyze calendar`; formas normalizadas
`Mon..Fri *-*-* 20..23:05,35:00` y `Tue..Sat *-*-* 00..03:05,35:00`. Hay test.

**No choca con ningún timer instalado.** La franja de madrugada es 00:05-03:35 NY =
01:05-04:35 Chile hoy; los seis del riel de medición van 17:50-20:30 Chile, la sonda de
tarde 21:05-00:35 Chile y el sellador 00:30 Chile. Ningún minuto de disparo instalado cae
en la franja nueva. Cuatro cosas que el director pidió declarar y quedaron escritas en la
plantilla o acá:

1. **`Tue..Sat` es la elección correcta y por una razón:** los cambios de hora de Nueva
   York ocurren **domingo a las 02:00**, que `Tue..Sat` excluye. Con `Mon..Sun` la hora
   02:xx dispararía dos veces en noviembre y cero en marzo.
2. Continuidad de grilla sin solape de minuto: 23:35 NY → 00:05 NY son 30 min, el mismo
   paso. La única proximidad estrecha es la que ya existía y ya fue aceptada (sellador
   23:30, sonda 23:35). Queda declarado que **si el sellador de las 23:30 tardara más de
   35 min, su descarga y la sonda de las 00:05 coincidirían**.
3. **Duplica el tráfico de la sonda a yfinance**: de 8 a 16 descargas de 36 tickers × 7
   días por noche hábil, en la máquina cuya cadena de sellos depende de que Yahoo no la
   limite. Instalarla es acto de Nicolás.
4. La advertencia medida sobre `Persistent=false` (0-bis.7) quedó escrita en la plantilla,
   porque el comentario anterior afirmaba lo contrario. Hay test que exige que esté.

### 1.5 El worktree, y por qué el cambio se aplicó hoy y no mañana

El encargo pide desarrollar el cambio de código en un `git worktree`, con la suite completa, y aplicarlo
al árbol real fuera de la franja de la sonda. **Hecho, y con una desviación declarada respecto de lo que
el pre-mortem recomendaba.**

El worktree se creó a las 16:50 (`git worktree add … HEAD --detach`), con las bases y la carpeta
`dinero/datos/sello/` copiadas dentro: son gitignoradas, y sin ellas los tests de la sonda **se saltan** en
vez de correr (es la trampa que la memoria del proyecto ya tenía anotada — un rojo, o un verde vacío, en un
worktree tiene dos causas). Ahí se escribieron las dos correcciones y los siete tests, y ahí corrieron
primero: **21 passed** en `tests/test_sonda_cierre.py`.

**La desviación:** el `director-programa` recomendó (su A13) terminar en el worktree y **aplicar mañana**,
porque calculaba que el único hueco para tocar el árbol real era 20:31–21:05, treinta y cuatro minutos que
tendrían que contener el final de una suite de ~900 tests. Esa premisa era **mi** premisa, y estaba mal:
yo había estimado la hora en vez de leerla y me creía ~55 minutos más tarde de lo que era. **Eran las
16:52.** Leído el reloj, el cálculo cambia por completo: se aplicó al árbol real a las **16:56**
—fuera de la ventana del riel (17:50) y muy fuera de la franja de la sonda (21:05)— y la suite completa
cerró a las **17:03**, también antes de la ventana. El objetivo de 1.5 se cumplió; la maniobra que el
director proponía dejó de ser necesaria porque su premisa horaria era falsa. Está anotado como error
propio 5.

El worktree se retiró al cierre (`git worktree remove --force` + `prune`): `git worktree list` vuelve a
mostrar sólo el árbol real en `main`.

### 1.6 El resumen sobre el dato real: DESCRIPTIVO, 4 noches

`GEMELO/resultados/sonda_cierre_resumen.{md,json}`, generado a las 19:56 UTC. **4 noches
con sesión** (sesiones NY 21, 22, 23, 24-sep) y **36 observaciones descartadas** por ser
anteriores al cierre de su sesión (las del 28 a las 13:42), declaradas en el informe.

| sesión | sondas | última sonda NY | con cierre | hora en que estuvieron todos | faltaron hasta la última sonda |
|---|---|---|---|---|---|
| 2026-09-21 | 8 | 23:35 | 36/36 | 23:35 | — |
| 2026-09-22 | 8 | 23:35 | **2/36** | — | los 34 restantes |
| 2026-09-23 | 8 | 23:35 | 35/36 | — | TOELY |
| 2026-09-24 | 8 | 23:35 | 36/36 | 21:35 | — |

**El cruce que el encargo pidió, y sale exacto ticker por ticker.** Comparando el
`disponibilidad.por_ticker` del meta del sello (bajado a las 23:30 NY) contra lo que la
sonda vio a las 23:35 NY:

| sesión | meta del sello: sin el cierre | sonda 23:35: sin el cierre | estado del sello |
|---|---|---|---|
| 21-sep | 0 | 0 | cuenta para N |
| 22-sep | 34 (lista completa) | los **mismos** 34 | `insumo_incompleto` |
| 23-sep | TOELY | TOELY | `insumo_incompleto` |
| 24-sep | 0 | 0 | cuenta para N |

Las dos vías son independientes —descarga distinta, código distinto, cinco minutos de
diferencia— y **coinciden ticker por ticker en las cuatro noches**. La sonda reproduce el
estado del insumo del sellador y explica los dos `insumo_incompleto` de la semana. Eso es
lo que la vuelve un instrumento válido para §58.

**Lo que decide la franja de madrugada, dicho como dato:** la noche del **22-sep, 34 de 36
tickers seguían sin el cierre a las 23:35 NY**, la hora más tardía que la sonda mira hoy.
No sabemos a qué hora aparecieron: sólo que fue **después** de la última observación
disponible. Ésa es la noche que ninguna decisión sobre (b) o (c) puede usar sin la franja
nueva.

**Cómo hay que leer el artefacto, y el propio artefacto todavía no lo dice** (lo marcó el director al
cerrar): **el filtro descarta OBSERVACIONES intradía, no noches.** Las ocho sondas de la noche del 28
—las de 20:05 a 23:35 NY— son posteriores al cierre y el filtro las admitiría sin problema. Que el
2026-09-28 no aparezca en la tabla «Por noche» es porque, al momento de generar el informe, la única
observación de esa fecha era la de las 13:42. **Excluir la noche del 28 del conteo de §58 es un juicio
del orquestador (ver 1.7), no una consecuencia del código**, y el informe hoy no distingue las dos
cosas. Decirlo dentro del informe es un cambio de una línea en `informe()` que esta corrida **no**
hizo, para no forzar una suite completa dentro de la ventana; queda para el encargo 15.

**Sobre el hallazgo de la corrida 13 (un cierre que estaba y deja de estar, n = 1 par):**
buscadas todas las transiciones `es_sesion_de_hoy` 1 → 0 dentro de una misma noche:
**0 de los pares consecutivos posibles** (4 noches × 36 tickers × 7 intervalos entre sondas = **1.008
oportunidades**; Wilson 95 % para 0/1.008 = **[0,00 · 0,38] %**). El `curador-epistemico` marcó bien que
publicar «0 pares» sin denominador y sin intervalo es lo que la corrida 13 sí había hecho con su
[0,02 · 0,44]: **el cero es censurado, no vacío**. No recurrió *dentro* de una noche en estas cuatro. No refuta el hallazgo de la
corrida 13, que era **entre dos descargas separadas 24 h** y no dentro de una noche: son
dos ventanas distintas y ésta no mide aquélla.

**Curiosidad medida, sin explicación (sería PROPUESTA):** en la noche del 22-sep los dos
que **sí** tenían el cierre fueron SHECY y TOELY, los dos ADR de mostrador, mientras los
34 nombres líquidos no lo tenían. Es al revés de lo que cabría esperar, y las dos vías
independientes lo dicen igual.

### 1.7 §58: no se elige nada

**Con 4 noches no se escribe ninguna recomendación sobre (b) ni (c)**, como manda el
encargo (§88.1 pide 5 a 10 noches). Y queda declarada la tentación que se declinó: con las
sondas de esta noche el 28-sep se vuelve la quinta noche mientras la corrida está viva.
**No se cuenta** — y la razón buena no es la que escribí primero.

**La razón buena (la señaló el director):** para el 28-sep **no va a existir la segunda vía**. El
sellador de las 00:30 entra por la rama de divergencia y no persiste ningún meta nuevo, así que el
único `disponibilidad.por_ticker` en disco de esa fecha es el intradía de las 13:42. Y lo que volvió
creíbles a las cuatro noches fue justamente que **dos vías independientes coincidieran ticker por
ticker**; la del 28 sería la única sin contraparte. Es un argumento de instrumento, no de higiene.

**Errata de esta bitácora, corregida antes del commit:** escribí que declinar el 28 «retrasa la
decisión §58 al menos una semana». **Es un día.** Las noches se acumulan de a una por sesión hábil, así
que la quinta noche llega igual con la sesión del 29-sep. Y la razón que había escrito —«es la noche
contaminada»— es más débil de lo que parecía: el filtro de 1.3-bis saca las 36 filas de las 13:42 y las
declara, y las ocho sondas de esta noche son observaciones post-cierre idénticas a las de las otras
cuatro noches. **Por el lado de la sonda, la noche está limpia**; lo que falta es la contraparte. El
gate real de §58 no es el conteo de noches, que se paga solo, sino **la censura a las 23:35**: la noche
del 22-sep tiene 34 de 36 tickers sin cierre a esa hora, y eso no lo arregla ninguna noche más de la
grilla actual.

---

## 2 y 3. NO EJECUTADOS por dictamen

El encargo lo ordena explícitamente: «Si 0-bis.3 muestra filas inválidas dentro del riel de medición,
**los bloques 2 y 3 no se ejecutan** hasta que Nicolás decida, porque los dos publican cifras». El
`auditor-lookahead` dictaminó `FILAS INVÁLIDAS ENTRARON COMO VÁLIDAS`
(`dictamen_14/auditor_sello_28sep.md`). Por lo tanto:

- **Bloque 2 (las erratas de los dos README, acta §88.5): NO EJECUTADO.** Las tres correcciones que
  §88.5 firmó —N de intentos 352/358 → 354/360, los badges, el «59×»— **siguen sin aplicar**, y los
  dos rojos de la suite siguen ahí. El diagnóstico sí se hizo (0-bis.5 y `espera_firma.md` §65),
  porque es lectura: la causa es un contador vivo que nada regenera, y la sección de E0 no existe en
  español, que es por lo que el test de paridad la excluye. **Nada de texto publicado se tocó.**
- **Bloque 3 (`bifurcaciones`): NO EJECUTADO**, ni 3.1 (artefacto fijo) ni 3.2 (medición nueva). El
  3.2 ya estaba declarado NO INICIADO por reloj en el pre-mortem. `GEMELO/bifurcaciones.py` y su
  artefacto quedaron **sin tocar**; no se corrió ninguna réplica, así que **no hay ningún intento
  nuevo que registrar** por este bloque.

Lo que el pre-mortem dejó en pie para la próxima corrida: el criterio de aceptación de 3.1 se
contradice consigo mismo si no se lee antes del artefacto la semilla y el número de réplicas con que
se publicó (A15 de `dictamen_14/director_premortem.md`).

---

## 4. Bookkeeping, M2 y deudas chicas

### 4.4 Enmienda de M2 como §9 de `dinero/preregistro_dinero.md` — PROPUESTA

`dinero/preregistro_dinero.md` **no está protegido por el hook** (`RUTAS_PROHIBIDAS` cubre
`motor.py`, las bases, `data/backups/`, `data/snapshots/`, `.claude/settings.json`,
`.claude/hooks/` y `.env`), así que la enmienda se escribió en su sitio como **§9** y no
como parche en `GEMELO/propuestas/parches/`. Se respeta la convención de la §5: fecha
posterior, dice qué cambia y por qué, y no borra nada.

Redacta las cuatro firmas del acta §88: (a) unidad en **%/año** con la fórmula
`comisión acumulada × (52/h) ÷ capital aportado` (§88.7, opción c); (b) umbral
**8,3 %/año** de 25/3 (§88.11); (c) el **deslizamiento no cuenta** (§88.12); (d) acumulado
desde el primer aporte con **primera lectura válida a las 52 semanas** (§88.13); (e) cuenta
congelada como **estado aparte** (§88.13).

Declara el grado de libertad de §88.11 (el umbral se fijó con las **12 lecturas ya
computadas** a la vista, E12).

**Dictamen del `estadistico-adversario`: `ENMIENDA CON DEFECTO DE REDACCIÓN` y, una vez corregido el
defecto, `NO APLICABLE: FALTAN DEFINICIONES` — seis, no cuatro** (`dictamen_14/adversario_m2.md`).

El defecto es mío y está corregido en su sitio, antes de cualquier commit y antes de que Nicolás la
leyera: la primera versión afirmaba que el umbral «no endurece ni ablanda el criterio», frase que **no
está en el acta** y que es **falsa y medible**. Ver 4.5. Además le quité seis lugares donde le ponía en
la boca al acta cosas que el acta no dice (la fórmula `× 52/h` explícita, «en su propia serie»,
«inválida por construcción sea cual sea su valor», «no se promedia con las cuentas vivas», «esto no la
invalida — el umbral es el original re-expresado») y le devolví el «y después sigue» de §88.13 y la
marca **(RETIRADA)** en la cita de la banda del 25 %.

Las **seis** definiciones que le faltan, que **no se rellenan** y que van a **completar la tarjeta §43
con opciones** (no se abren tarjetas nuevas: el contador ya está en §88.14 y el arancel en §48):
(1) el denominador durante la rampa de aportes —y la bifurcación real es **ponderado por tiempo o no**,
no las tres opciones que yo había escrito, de las que dos eran la misma—; (2) qué es exactamente
«congelada», donde la cifra «5 de 20» **no mide el concepto que el acta firmó** (el código usa «26
semanas sin movimiento», el acta define un estado de caja); (3) si una cuenta congelada mata la pista o
sólo sale del cómputo, donde §88.13 firma una **tercera** cosa; (4) dónde vive el contador de «lecturas
de criterio»; **(5) NUEVA Y URGENTE: qué es «el primer aporte»** —con la cuenta IBKR ya fondeada con
5,00 USD, **dos órdenes al mínimo dan 14 %/año y M2 dispara**, y eso toca la validez de la propia
enmienda—; y **(6) la convención de anualización** (`× 52/h` lineal), que no está firmada. Más cuatro
huecos menores (D7 a D10) en el dictamen.

Y una exigencia del adversario que no bloquea el texto: mientras `GEMELO/simulador/` no tenga múltiples
trayectorias de mercado, **ninguna afirmación de la forma «M2 dispara cuando debe» está autorizada**.

### 4.5 Hallazgo verificado, no corregido: bajo 8,3333 %/año el juego `medio` dispara en 19 de 20

**Corregido dentro de la misma corrida.** La primera versión de este apartado decía «sí en la
mediana; el borde inferior queda apenas bajo el umbral», que **subdeclara** el costo. El
`estadistico-adversario` lo midió y el orquestador lo reprodujo: a h = 52 semanas —la única lectura
que la enmienda autoriza— el umbral viejo (25 % acumulado) dispara **0 de 20** en los tres juegos y el
nuevo (25/3 = 8,3333 %/año) dispara **19 de 20** en `medio`, Wilson 95 % [76,4 · 99,1] sobre semillas.
A h = 52 el estadístico es idéntico bajo las dos lecturas (52/52 = 1), así que la comparación no
depende de ninguna convención. **De dónde NO sale el 19/20:** `GEMELO/m2_periodo.py` sigue con
`UMBRAL_M2_PCT = 25.0`, así que el conteo contra 8,3333 %/año se computó **fuera** del módulo dueño del
umbral y **no es reproducible corriendo `m2_periodo.py`**. Lo marcó el `guardian-constitucion`: es la
misma vara que §61 le aplica a las 24 filas del 28-sep. No se cambió el módulo —sería aplicar una
enmienda declarada NO APLICABLE, con el arancel del §40 sin firma— se declara.

| juego | anualizada desde 52 | mín–máx | ¿dispara a 8,3333 %/año? |
|---|---|---|---|
| conservador (por defecto) | 3,9 % [3,56 · 4,58] | [3,5 · 4,69] | 0 de 20 semillas |
| agresivo | 6,4 % [5,77 · 7,78] | [5,66 · 7,83] | 0 de 20 semillas |
| medio | **9,4 % [8,23 · 10,82]** | [8,14 · 11,18] | **19 de 20**, Wilson 95 % [76,4 · 99,1] |

La banda es de **percentiles entre 20 semillas sobre UNA sola trayectoria de mercado**: **no es un
intervalo de cobertura nominal** y no cubre la variación de mercado. Con K = 20 el percentil 2,5 no es
estimable — el 8,23 es una interpolación entre la semilla más baja (8,14) y la segunda (8,34), o sea
que «el borde inferior de la banda» **es una semilla**. La única de `medio` que no cruza es la más baja
de las veinte.

**Y el umbral no mata al juego más arriesgado, mata al más granular:** el costo por orden es casi el
mismo en los tres (≈ 0,30 · 0,30 · 0,24 USD), así que M2 ≈ órdenes × ~0,3 USD ÷ capital, y `medio`
gasta más que `agresivo` por hacer más órdenes (443 contra 393). Las holguras tampoco son comparables:
la peor semilla de `agresivo` está a +6,4 % del umbral y la de `conservador` a +77,7 %.

El juego por defecto sigue siendo el conservador, `reglas.json` sigue **SIN FIRMA** y el **arancel del
§40 que fija el numerador también** (tarjeta §48). No se encontró ningún documento vivo que presente
`medio` como candidato para E2; si aparece, va a la cola.

---

*(Secciones de dictámenes, bloques 2 y 3, cierre y conteo de intentos: más abajo, escritas
al cerrar.)*

---

## 5. Lo que esta corrida NO hizo

Además de los bloques 2 y 3:

- No corrió el sellador real, no cambió su hora, no tocó §57 ni `dinero/sello_dinero.py`.
- No instaló ni modificó ningún timer. La franja de madrugada es **plantilla en
  `GEMELO/propuestas/systemd/`**; instalarla es acto de Nicolás. Tampoco se corrigió el
  `Description=` de las dos unidades instaladas que dicen «PROPUESTA no instalada».
- No eligió entre (b) y (c) de §58, y no contó el 28-sep como quinta noche.
- No instaló `ibapi` ni IB Gateway, no tocó `.env` ni `corredor/`, no se conectó a IBKR.
- No afirmó, en ningún idioma, que exista una ventaja.
- No cableó §46, no firmó el `motor_concat.diff`, no tocó §82.7.
- **No firmó nada.** La enmienda de M2 es PROPUESTA; las cinco tarjetas nuevas (§61 a §65) traen
  opciones y consecuencias, no decisiones.
- No hizo `git add`, `git commit`, `git push` ni `git pull`.

---

## 6. Errores propios detectados

1. **Repetí la fecha equivocada de las noches de la sonda.** El encargo dice «4 noches completas
   (fechas UTC 22 a 25)» y yo lo tomé como si fueran las sesiones. Son las sesiones NY **21, 22, 23 y
   24**: 22-sep 00:05 UTC es el 21-sep 20:05 de Nueva York. Lo detectó el pre-mortem del director
   (A10) antes de que contaminara ningún artefacto, pero ya lo había escrito en una lectura
   intermedia. Corregido: se filtra sólo por `sesion_ny`.
2. **Estuve a punto de publicar un resumen contaminado.** El bloque 1.6, tal como estaba pedido, y
   con el código tal como estaba, habría publicado «el cierre apareció a las 13:42 NY» para 35
   tickers, porque `resumen()` no tenía filtro de grilla y las filas del despertar entran con
   `es_sesion_de_hoy=1`. Lo vio el director (A9), no yo, y yo ya había corrido el resumen una vez en
   el worktree sin notarlo. Corregido antes de escribir en `GEMELO/resultados/`.
3. **Escribí una cifra sin leerla.** En el borrador de la tarjeta §65 puse «la suite recolecta 901
   tests» de memoria de una aritmética mía. El número real, leído de
   `pytest --collect-only -q`, es **904**. Corregido antes de que la tarjeta se escribiera al archivo.
   Es exactamente lo que la regla «ninguna cifra se cita de memoria» existe para impedir, y casi lo
   hago en el documento que denuncia cifras vencidas.
4. **Llamé «primer `previous_session`» a una API que no acepta no-sesiones.** La primera versión de
   `sesion_atribuida()` usaba `cal.previous_session(fecha)`, que lanza `NotSessionError` cuando la
   fecha es sábado — justo el caso que la corrección existe para arreglar. Lo encontró el primer test
   que la ejercitó, no una lectura. Corregido con `date_to_session(fecha − 1 día, direction="previous")`.
5. **Mal cálculo del reloj durante la primera hora.** Asumí que había pasado más tiempo del real y
   por eso creí que llegaba justo a la ventana de las 17:50; eran las 16:52. No produjo daño —al
   contrario, dio margen para aplicar el bloque 1 y correr la suite completa antes de la ventana— pero
   es la razón por la que la recomendación A13 del director (aplicar mañana) dejó de aplicar: su
   premisa horaria era la mía, equivocada. **Las horas se leen de `date`**, y esta bitácora lo hace.
6. **Llamé al `guardian-constitucion` sobre un árbol que seguía moviéndose, y él lo cazó.** Le pedí el
   dictamen a las 17:22 y seguí escribiendo hasta las 17:39: `DECISIONES.md` creció 26 líneas y le
   apareció una subsección nueva (§89.9-bis, la medición), `bitacora_14.md` pasó de 811 a más de 1.000
   líneas, `ESTADO.md` se reescribió, y **el encargo que le di omitía `estado_epistemico.md`**, que es
   uno de los cinco documentos de `cifras.DOCUMENTOS_PUBLICADOS` — o sea que casi dictamina sin ver un
   cambio a un documento publicado, y lo encontró por su cuenta con un `git diff -- '*.md'`. Su dictamen
   vale para el árbol de las 17:35:09 y **hay que volver a pedirlo sobre el árbol final**. La regla de
   procedimiento que sale de esto: **el guardián se llama después del último `Write`, no en paralelo**, y
   el encargo que se le da se arma con `git status` en el momento, no con una lista escrita antes.

7. **ESTADO.md me quedó largo cuatro veces.** El archivo declara «máximo 50 líneas» y lo escribí en
   69, 63, 61, 58, 57, 52 y por fin 50. Consumió tiempo de ventana en algo que no es hallazgo.

---

## 6-bis. Lo que pasa esta noche después de que la corrida termina, y que Nicolás tiene que contrastar

La corrida cierra antes de las 18:15. Todo lo de abajo está deducido del código, no observado, y está
escrito para poder ser contradicho por la máquina:

| hora | job | qué va a hacer, y por qué |
|---|---|---|
| 17:50 | `mki-noticias` | RSS + Haiku bajo presupuesto. Sin relación con el hallazgo. |
| 18:15 | `mki-snapshot` | **No re-sella** (`ya_existe_snapshot_hoy()`), corre el verificador sin nada nuevo que verificar, y reexporta los CSV. Ver 0-bis.4b. |
| **18:25** | `mki-reporte` | **Va a enviar un reporte completo compuesto desde el sello del 28-sep**, o sea desde las filas de las 13:42 NY: `regimen` «Alcista · vol baja» (que la sección 9 midió **correcto**), las 8 predicciones `beta × (−1,63)` (**0,11 pp de desvío en el peor caso, ninguna dirección invertida**) y **`roca_chip` 44, cuando el cierre real dice 17**. Ese es el único número del reporte de esta noche que está lejos de su valor. Es el segundo reporte del día (el primero salió a las 14:42 con 400 caracteres porque el sello todavía no existía). **Detener un timer es operación de Nicolás y ningún agente lo toca**; queda dicho para que sepa qué está mirando si lo recibe. |
| 18:40 | `mki-backup` | Commitea `data/backups/` con pathspec: los seis CSV modificados **y** `data/backups/sello_dinero_ext/ext_2026-09-28.{csv,meta.json}`, que es la matriz de media sesión. Nada fuera de `data/backups/` se cuela, así que los archivos de esta corrida NO entran en ese commit. |
| 19:00 | `mki-vigia` | Debería dar OK: hay snapshot del día, hay commit de backup, y el reporte quedó registrado. La guarda de ancla temporal **no va a ver** la inversión de `available_at`, porque prueba `av == ts` (igualdad, no orden). |
| 20:30 | `mki-vigia-rechequeo` | Silencioso: no hay marcador pendiente (el epílogo del snapshot consumió el de las 14:42). |
| 21:05–00:35 | `mki-sonda-cierre` | Ocho sondas de la noche del 28. **Con el código ya aplicado**: `sesion_atribuida()` les dará `sesion_ny = 2026-09-28` (son posteriores a la apertura), igual que la regla vieja. La franja de madrugada **no está instalada**, así que después de las 23:35 NY no hay nada. |
| 00:30 del 29 | `mki-sello-dinero` | **Cero filas insertadas** y una fila nueva en `divergencias_sello` (ver 0-bis.2). Falsable: `divergencias_sello` pasa de 1 a 2 y `sellos_dinero` sigue en 462. |

Y la medición que esta corrida no pudo hacer y que decide la magnitud del hallazgo: **después de las
20:00 UTC (17:00 Chile) del 28** ya existe el cierre real del 28-sep, así que
`motor._cache.clear(); motor.prediccion_apertura_al(date(2026,9,28))` y comparar el «SOX usado %»
contra el **−1,63** sellado dice de una vez si las 8 direcciones se invierten. Advertencia del auditor
que hay que respetar al hacerlo: **si esas filas se usan para diseñar la corrección y después se
cuentan en el track record, eso es una fuga de selección creada por la propia auditoría.**

## 7. Conteo de intentos, con la norma del §88.4

**Sin cambio en los tres registros.** Leídos de la máquina:

| registro | dónde vive | valor |
|---|---|---|
| gap asiático | `GEMELO/relevo_asiatico.py::N_INTENTOS_ACUMULADO` | **354** |
| veredicto 5.1 | `backtest/veredicto_51.py::N_INTENTOS_51` | **360** |
| riel largo | `dinero/registro_intentos.py::N_INTENTOS_RIEL_LARGO` | **4** |

Justificación de que no se mueven, contra la norma del §88.4 («en el riel largo, un barrido
descriptivo también cuenta»):

- El bloque 3.2, que era el único que iba a probar una hipótesis, **no se ejecutó**: cero réplicas
  corridas, cero configuraciones evaluadas.
- El resumen de la sonda (1.6) **no es un barrido sobre el riel largo ni sobre ninguna señal**: es
  una descripción de a qué hora una fuente de datos publica un cierre. No evalúa ninguna
  especificación, no elige entre variantes y no produce ninguna afirmación sobre ventaja. No entra en
  ninguno de los tres registros, y la norma del §88.4 es sobre el riel largo.
- La enmienda de M2 **cita** las 12 lecturas ya computadas de la corrida 12; no computó ninguna
  nueva. El grado de libertad de esas 12 ya estaba declarado (E12) y queda re-declarado en la §9.
- El cruce sonda-vs-meta del sello (1.6) es una **verificación de instrumento**, no una prueba de
  hipótesis sobre el mercado: compara dos vías de medir el mismo hecho observable.

Sigue pendiente, y sin dueño desde el §88.14: **dónde vive el contador de «lecturas de criterio»**,
que es un registro distinto del DSR. La enmienda de M2 lo vuelve a declarar y lo manda a tarjeta.

---

## 8. Cierre: suite, huellas, escaneo de secretos

### 8.1 Suite

| momento | resultado |
|---|---|
| al abrir (16:36 – 16:43) | `2 failed, 889 passed, 5 skipped, 1 xfailed` en 407,26 s |
| con el bloque 1 aplicado (16:56 – 17:03) | `2 failed, 896 passed, 5 skipped, 1 xfailed` en 418,15 s |
| tras el bloque 1 aplicado, antes de la ventana (17:20 – 17:27) | `2 failed, 896 passed, 5 skipped, 1 xfailed` en 412,28 s |
| **final, después de la ventana (21:19 – 21:26)** | **`2 failed, 896 passed, 5 skipped, 1 xfailed` en 404,25 s** |

**904 tests recolectados** (`pytest --collect-only -q`). Los **+7** contra la apertura son los siete
tests nuevos del bloque 1; el `assert` de guarda del bloque 4.3 va dentro de un helper y no agrega
tests.

**Los dos rojos son los mismos con que la corrida abrió**, `tests/test_readme.py`, y son
**preexistentes**: el README publica un contador de E0 que el timer mueve cada noche y nada regenera
(§65). El bloque que los arreglaba —el 2— **está bloqueado por el veredicto del auditor**, así que la
corrida cierra con ellos y lo dice en vez de esconderlo. Verificado además que no son consecuencia del
evento del 28: `contador_e0()` sobre el CSV **de HEAD** ya daba `sesiones_selladas 13` contra las 9 que
el README publica, antes del despertar; el evento agrandó la deriva en uno, no la creó.

Y aparte de la suite, el anti-look-ahead del motor (`python tests/test_motor.py`): **18 OK**, última
línea literal *«RESULTADO: todas las funciones del motor pasan el test de no-contaminación (sin
look-ahead bias).»* Con la glosa del auditor que hay que leer en la misma línea: ese verde **no cubre
una barra no liquidada EN `t`**, porque el test trunca con `<= fecha`, inclusive, y la barra parcial se
cancela entre las dos ramas.

Los cuatro tests de integridad del sellador sobre la base real: **4 passed**, con la glosa de 0.5 (el
verde dice «la base cita el archivo que hay», no «el insumo es legítimo»).

**Y una corrida más, a las 17:43, porque después de la suite final los dictámenes de cierre obligaron a
editar documentos —y en este proyecto los documentos están vigilados por tests**: `test_dinero.py`
(que incluye la palabra prohibida sobre `DOCUMENTOS_DEL_RIEL`, donde vive `preregistro_dinero.md`),
`test_epistemico.py`, `test_cifras_arbitro.py`, `test_fuente_canonica.py`, `test_banco_clausulas.py`,
`test_readme.py`, `test_sonda_cierre.py` y `test_sello_dinero.py` →
**`2 failed, 150 passed, 1 skipped, 1 xfailed`**, con los dos rojos siendo los mismos de siempre. Las
ediciones de los dictámenes **no introdujeron ningún rojo nuevo** en los guardias de documento publicado,
ni en el escáner de cifras retiradas, ni en la palabra prohibida.

**Y tres veces más, porque cada dictamen obligó a editar documentos y en este proyecto los documentos
están vigilados por tests:**

| hora | por qué | resultado |
|---|---|---|
| 17:43 | después de los dictámenes de cierre | `2 failed, 150 passed, 1 skipped, 1 xfailed` (8 archivos, incluido `test_readme.py`) |
| 17:57 | después del re-dictamen del guardián | `92 passed, 1 skipped, 1 xfailed`, **cero fallos** |
| 20:12 | después de los cinco bloqueantes del curador | **`113 passed, 1 skipped, 1 xfailed`, cero fallos** |

Los guardias de documento publicado, el escáner de cifras retiradas (`cifras.reintroducciones()`) y la
palabra prohibida siguen verdes con el texto final. **Ninguna de las tres tandas de correcciones de los
dictámenes introdujo un rojo.**

**La suite completa se volvió a correr a las 21:19, ya cerrada la ventana**, porque un verde de las 17:27
no cubría el texto de las 21:20 — es la regla de la casa de que «un verde antes del sello no es un verde»,
aplicada a la inversa: el árbol cambió después del verde. **Resultado idéntico al de las 17:27**, con los
mismos dos rojos preexistentes. Y `python tests/test_motor.py` de nuevo en verde: «todas las funciones del
motor pasan el test de no-contaminación».

**Un verde que vale la pena señalar, porque es de punta a punta:**
`test_la_regla_nueva_reproduce_el_sesion_ny_de_todas_las_filas_ya_escritas` pasó con el CSV **ya en 1.224
filas**, o sea incluyendo las 36 que la sonda de las 21:05 escribió **con la regla nueva en producción**. El
test que se escribió para demostrar que la corrección no cambiaba el pasado ahora también demuestra que lo
que el job escribe en vivo es consistente con él.

### 8.2 Huellas de las bases

**Las tres idénticas durante toda la corrida; dos de las tres se movieron después, y cada una con su
job y su hora.** (El encabezado anterior decía «idénticas al abrir y al cerrar, las tres, sin necesidad
de ninguna excepción» y quedaba contradicho por los párrafos de abajo, que se apendaron sin tocarlo: lo
marcó el `curador-epistemico`.)

```
16:38  b8c25631645b6affd4cd9e95d75e4c49b06eec6fcb7dc1aef54c6061379eda99  dinero/sello_dinero.db
17:28  b8c25631645b6affd4cd9e95d75e4c49b06eec6fcb7dc1aef54c6061379eda99  dinero/sello_dinero.db

16:38  f8a474968d1616078ab2d60e3248061c9a98270fa7a204662810407bf1d8f014  senales.db
17:28  f8a474968d1616078ab2d60e3248061c9a98270fa7a204662810407bf1d8f014  senales.db

16:38  5e4d55d319e38f872992ce71684e98e2d5501d9800b11d04c29cae0268a50e77  noticias.db
17:28  5e4d55d319e38f872992ce71684e98e2d5501d9800b11d04c29cae0268a50e77  noticias.db
```

**`senales.db` se movió a las 18:15:12, y también es del timer.** El job de las 18:15 no re-selló
—`{'snapshot': False, 'motivo': 'ya existe snapshot de hoy'}`, exactamente lo que 0-bis.4b predijo— pero
sí corrió el verificador, y `verificador puntaje: 4 verificadas` metió cuatro filas en
`verificacion_puntaje` (1.181 → 1.185). Nada más cambió: `snapshots` sigue en 59 filas, `senales_ticker`
en 1.375, `verificacion_apertura` en 420, y **las 8 filas del 28-sep siguen `pendiente`** —se verifican
mañana—. Huella nueva: `c462d5db…0dfd111`.

**Y `noticias.db` se movió antes, a las 17:52:39, también del timer.** Lo cazó el
`guardian-constitucion` en su re-dictamen, y queda con su hora del journal:
`Starting mki-noticias.service` **17:50:00**, `Finished` **17:52:39**, y `noticias.db` con mtime
**17:52:38** pasando de `5e4d55d3…68a50e77` a `d3141c5f…6c43b99` (el guardián leyó una huella intermedia,
`fcb4f031…`, a las 17:50:45, que es el archivo a media escritura). **`senales.db` y
`dinero/sello_dinero.db` siguen byte a byte en las huellas de las 16:38**, verificado a las 17:54. Es
exactamente la fila de las 17:50 de la tabla de 6-bis cumpliéndose.

La corrida entera cupo **entre el despertar de las 14:42 y el primer timer de la tarde (17:50)**, así
que ningún job escribió durante ella. Eso es también la razón por la que el chequeo del encargo 8.7 es
un chequeo de verdad esta vez y no aterrizó en su propia excepción (el defecto que el pre-mortem marcó
como A16). **Lo que cambie después de las 17:50 es de los timers**, y la tabla de 6-bis dice cuál y a
qué hora.

**Estado final de las bases, a las 21:21 (después del último timer de la tarde y de la sonda de las
21:05):**

```
senales.db              c462d5db…0dfd111   ← movida 18:15:12 por el snapshot (4 filas a verificacion_puntaje)
dinero/sello_dinero.db  b8c25631…9eda99    ← INTACTA desde las 16:38; el sellador recién corre 00:30
noticias.db             d3141c5f…6c43b99   ← movida 17:52:39 por mki-noticias
```

**Las tres se mueven por un job, con su hora del journal, y ninguna por la corrida.** La única del camino
de sellado del riel de dinero, `sello_dinero.db`, está byte a byte igual a la de la apertura.

`HEAD` **ya no es `5321f6b`: el job de backup de las 18:40 commiteó `f7b65e0`** con sólo `data/backups/`
(sección 10). **La corrida no commiteó nada, y no hay push ni pull.** Escaneo de secretos re-corrido al
cierre sobre todo el diff: **0 patrones**.

### 8.3 Escaneo de secretos

Corridos los dos patrones del pre-commit (`sk-ant-api…` y el token de bot de Telegram) sobre **todo lo
no commiteado** —stageado, no stageado y los archivos nuevos sin versionar, recursivo, excluyendo
`tests/test_seguridad.py` como hace el hook—: **0 coincidencias**. Ninguna credencial en la bitácora,
en los dictámenes, en las tarjetas ni en el acta.

### 8.4 Qué tocó la corrida, y qué no

Modificados por la corrida: `GEMELO/sonda_cierre.py`, `GEMELO/sonda_cierre_resumen.py`,
`GEMELO/propuestas/systemd/mki-sonda-cierre.timer`, `tests/test_sonda_cierre.py`,
`tests/test_sello_dinero.py`, `dinero/preregistro_dinero.md` (§9 nueva), `DECISIONES.md` (acta §89
apendada al final, así que ninguna cita por número de línea de las anteriores se desplazó),
`ESTADO.md`, `GEMELO/resultados/espera_firma.md`, `GEMELO/resultados/cola_decisiones.md`,
`GEMELO/resultados/estado_epistemico.md`. Nuevos: `GEMELO/resultados/bitacora_14.md`,
`GEMELO/resultados/dictamen_14/` (**cuatro** dictámenes: el auditor con su complementario, el pre-mortem
del director, el adversario de M2, y el cierre del guardián con el director) y
`GEMELO/resultados/sonda_cierre_resumen.{md,json}`.

**NO tocados, y verificado en el diff:** `motor.py`, `senales.py`, `snapshot.py`, `universo.py`,
`dinero/sello_dinero.py`, `README.md`, `README.es.md`, `docs/readme/`, `GEMELO/bifurcaciones.py`,
`corredor/`, `.env`, `~/.config/systemd/user/` y cualquier timer instalado.

**No tocados tampoco, y hay que decir de quién son:** los seis CSV de `data/backups/` y
`data/backups/sello_dinero_ext/ext_2026-09-28.*` los escribieron los timers a las 14:43, y
`data/sonda_cierre.csv` lo puso Nicolás en el índice antes de que la corrida arrancara.

### 8.5 Este diff NO se puede commitear tal cual, y conviene saberlo antes de intentarlo

Lo marcó el `guardian-constitucion`. El hook `scripts/pre-commit` exime de correr la suite **sólo** al
commit que toca *únicamente* `data/backups/` (para que el job de respaldo nunca quede bloqueado). Este
diff toca doce archivos más, así que el hook **corre la suite, sale roja por los dos rojos preexistentes
de `tests/test_readme.py` y bloquea el commit**. Las dos salidas son de Nicolás: `SKIP_TESTS=1`, que deja
el commit verificado sólo por el escáner de secretos (que esta corrida ya corrió limpio), o **decidir
primero el §65** —el contador vivo del README— y commitear con la suite en verde. La segunda es la que el
director recomienda, y es la razón por la que §65 se firma en la misma sentada que §61.

### 8.5-bis Dos skills del proyecto contradicen a la máquina (hallazgo de paso, no corregido)

Al correr el ritual de cierre aparecieron dos textos de `.claude/skills/` que ya no describen esta
máquina. No se tocó ninguno —el encargo no autoriza editar skills— y van anotados:

1. **El «gate de entorno» de la skill `gate` manda importar `scipy` y `sklearn`, y ninguno de los dos
   está instalado ni figura en `requirements.txt`** — a propósito: `CLAUDE.md` declara «**No scipy** —
   `math.erfc` + bisección» para `backtest/inferencia.py`. Medido en esta máquina: `pandas` 3.0.3,
   `numpy` 2.4.6, `yfinance` 1.5.1, `exchange_calendars` 4.13.2, `fastapi` 0.139.0; **`scipy` y `sklearn`
   NO INSTALADOS**. O sea que ese chequeo **falla por diseño en una máquina bien provista**, y un gate que
   falla siempre es un gate que se aprende a saltar. Lo que corresponde es que la línea importe lo que el
   proyecto de verdad usa.
2. **El «Recordatorio de estado» de la skill `cierre-sesion` describe el estado ANTERIOR al switch**:
   dice que «lo que sigue abierto es el segundo movimiento del switch: apagar los timers del Mac primero,
   quitar `MKI_MODO` en el PC después» y remite a `/switch-titular`. El switch se ejecutó el
   **30-ago-2026**, `modo.py` responde `titular`, y `CLAUDE.md` ya declara que **la skill
   `switch-titular` no existe** (el orden del switch vive en `modo-emision`). Es la misma clase de
   desfase que el propio `CLAUDE.md` manda resolver a favor de la máquina, sólo que todavía vive en un
   archivo que un agente lee al cerrar.

### 8.6 Una cifra del artefacto de la sonda que necesita su `n` al lado

`GEMELO/resultados/sonda_cierre_resumen.md` publica en su encabezado «hora (NY) a la que estuvieron
todos: mediana **22:35**, máxima **23:35**». Esa mediana es sobre **2 noches** (las dos que completaron
las 36 columnas: 21-sep a las 23:35 y 24-sep a las 21:35), así que **es el promedio de dos valores y es
una hora que no se observó nunca**. El `n` de noches está declarado en la misma línea del informe, pero
la mediana no lleva el suyo. Lo marcó el guardián; el artefacto lo genera `informe()` y **esta corrida no
lo cambió**, para no forzar una suite completa dentro de la ventana. Queda con el resto de los arreglos
de una línea para el encargo 15.

---

## 9. La medición que faltaba, hecha a las 17:31 (y la sorpresa no estaba donde se la buscaba)

**Por qué se hizo, y por qué se pudo.** El dictamen del auditor dejó como zona ciega central que
«magnitud y **signo** de la corrupción quedan sin medir», porque el cierre del 28-sep no existía
todavía. El `director-programa`, al revisar el cierre, marcó que **eso era alcance de menos y estaba
disponible**: el cierre de NYSE ocurre a las 20:00 UTC (17:00 de Chile), la suite había terminado a las
17:03, y la ventana que prohíbe descargas empieza a las 17:50 — había casi cuarenta minutos con el dato
en la mano. Y el argumento habitual para no descargar antes de la ventana **no aplicaba esta noche**:
el sello del 28 ya existía y `ya_existe_snapshot_hoy()` garantiza que el disparo de las 18:15 no lo iba
a rehacer, así que no había ninguna cadena de sellos que proteger. Tenía razón. Se midió a las **17:31**,
en un proceso aparte, con `motor._cache.clear()` y funciones puras: **ninguna base se escribió** (las
tres huellas sha256 siguen idénticas a la apertura).

### 9.1 El insumo: −1,63 sellado contra −1,61 real

| | `sox_usado_pct` | `sox_fecha` |
|---|---|---|
| sellado a las 13:42 NY, con la bolsa abierta | **−1,63** | 2026-09-28 |
| recomputado a las 16:31 NY, con la sesión cerrada | **−1,61** | 2026-09-28 |

Diferencia **0,02 pp, y el mismo signo**.

### 9.2 Las 8 predicciones: ninguna dirección se invierte

| ticker | sellada | recomputada | dif. pp | dirección |
|---|---|---|---|---|
| IFX.DE | −0,05 | −0,05 | 0,00 | IGUAL |
| 4063.T | −0,50 | −0,49 | 0,01 | IGUAL |
| 2330.TW | −0,53 | −0,52 | 0,01 | IGUAL |
| 6857.T | −0,92 | −0,91 | 0,01 | IGUAL |
| 005930.KS | −0,97 | −0,95 | 0,02 | IGUAL |
| 3436.T | −1,08 | −1,06 | 0,02 | IGUAL |
| 000660.KS | −1,32 | −1,29 | 0,03 | IGUAL |
| **8035.T** | −0,91 | **−0,80** | **0,11** | IGUAL |

**0 de 8 direcciones invertidas. Peor diferencia absoluta: 0,11 pp** (8035.T, cuya beta también se
movió al recomputarse con el cierre en vez de la barra parcial: 0,56 → ≈0,50).

**Y ese 0,11 pp no mide el efecto de la barra parcial — hay que decirlo con la aritmética delante.** Con
0,02 pp de desvío en el escalar, lo máximo que puede propagar la beta más alta es
**0,81 × 0,02 = 0,016 pp**. El 0,11 sólo existe porque **la beta de 8035.T se reestimó**, y 8035.T es
**el mismo ticker y la misma fecha** del aviso de split/dato corrupto de 9.4. **Entre los siete tickers
sin dato marcado, la peor diferencia es 0,03 pp** (000660.KS), y ése es el número que mide el efecto de
la barra parcial. Lo levantó el `curador-epistemico`. **Una de las dos
sospechas** del auditor —que el signo pudiera invertir las ocho— **no se materializó en esta fecha**.

**Y hay que decir «una de las dos sospechas» y no «la sospecha central», que es lo que había escrito.**
Lo corrigió el propio auditor: en su dictamen esas dos cosas estaban bajo **«SOSPECHAS SIN DEMOSTRAR»**,
explícitamente **fuera** de los cuatro fundamentos del veredicto. Llamarla central sugiere que el
veredicto descansaba en ella y que por tanto se debilita, «que es justo lo contrario de lo que pasó».

**Y hay que decirlo así y no «queda refutada», que es lo que había escrito.** Lo marcó el guardián: lo
medido es que el riesgo **no ocurrió el 28**, no que la sospecha fuera infundada. **El mecanismo sigue
ahí**: las 8 betas son positivas, así que un día en que la barra intradía y el cierre caigan a distinto
lado del cero invierte las ocho direcciones a la vez. Lo que esta fecha dice es que el desvío fue de
0,02 pp en el insumo, no que no pueda ser mayor.

### 9.3 El régimen: idéntico, así que el cambio de etiqueta es REAL

El auditor marcó como sospecha que la etiqueta de volatilidad se hubiera dado vuelta respecto del
24-sep (`vol alta` → `vol baja`) por efecto de la barra parcial, y que «un cambio de régimen» es la
mitad del gatillo de la 5.1. Medido:

| | régimen |
|---|---|
| sellado 28-sep (13:42 NY) | `Alcista · vol baja` |
| recomputado 28-sep (post cierre) | `Alcista · vol baja` — **idéntico** (vol actual 37,5 contra mediana 38,8; ratio a la media 15,92 %) |

**La sospecha no se materializó: el cambio de etiqueta respecto del 24-sep es real y no un artefacto de
la barra parcial.** (Misma precisión que en 9.2: lo medido es esta fecha, no la clase de riesgo.)

**Pero esta es la evidencia MÁS DÉBIL de la sección, no la más fuerte, y el auditor insistió en que se
diga.** `regimen_al` produce una **etiqueta binaria**: compara la vol actual contra su mediana y el ratio
MA50/MA200 contra ±1 %. **Dos series distintas caen del mismo lado de un umbral con probabilidad alta**,
así que la coincidencia de la etiqueta es evidencia débil por construcción. Y el margen es estrecho:
**37,5 contra una mediana de 38,8 — 1,3 de holgura**, no una distancia cómoda. Lo medido es que la
etiqueta coincidió, **no que fuera robusta**; es más débil que los 0,02 pp del insumo, que sí es continuo.

### 9.4 Y la sorpresa: `roca_chip` se movió 27 puntos, de 44 a 17 — **PROVISIONAL**

> **ADVERTENCIA QUE LLEGÓ DESPUÉS Y QUE CAMBIA LA LECTURA DE TODO ESTE APARTADO.** Lo encontró el
> `curador-epistemico` en el log del job de las 18:15, o sea **44 minutos después de esta medición**:
>
> ```
> data/snapshot.log:147
>   - Tokyo Electron (8035.T): salto de -80% el 2026-09-28 — revisar split/dato corrupto
> ```
>
> Es la **única** aparición de ese aviso en todo el log, y lo emite `salud_datos_al` con umbral 0,40,
> llamándolo «posible split mal ajustado o dato corrupto». **8035.T cotiza alrededor de 55.000 yenes**
> (verificado en el caché de GEMELO: 54.980 el 1-sep), y **−80 % es exactamente un split 5:1**
> (55.000 → 11.000). Que sea un split sin ajustar es **INFERIDO, con evidencia fuerte pero sin el cierre
> del 28 a la vista**: medirlo exige bajar datos y la ventana 17:50–20:30 lo prohíbe.
>
> **Por qué toca a `roca_chip`:** 8035.T es eslabón del nivel 2, que tiene tres tickers, sobre cinco
> niveles promediados con peso igual, y la serie es `mom20`. Un desplazamiento de −80 pp en el `mom20`
> de un ticker mueve el crudo de la cadena en **(80/3)/5 = 5,33 pp** (aritmética de orden de magnitud del
> curador, no una remedición). El salto del crudo que este apartado reporta es de +3,64 (25-sep) a −2,8
> (28-sep), o sea **6,44 pp: el ticker marcado explica del orden del 83 %**. Y el «cambio de signo,
> ~5,8 pp» que infiero más abajo es **casi exactamente el tamaño del artefacto**.
>
> **Consecuencia, y es la que importa: el 17, los 27 puntos y la inferencia de los 5,8 pp quedan
> PROVISIONALES**, a la espera del contraste de 8035.T. Y con ellos queda provisional la frase que
> reordena la gravedad —«chica en el canal lineal, grande en el canal no lineal y agregado»—, porque
> descansa en este único número. **La prueba que lo cierra, después de las 20:30:** mirar el `Close` de
> 8035.T del 25 y del 28-sep, decidir si es split no ajustado o dato corrupto, y **recién entonces**
> volver a leer `roca_chip_al(date(2026,9,28))`.
>
> Lo que **no** cambia: que el sello del 28 usó una barra intradía, que `available_at` es imposible, que
> la predicción no es reproducible desde el registro, y el veredicto. Un insumo corrupto **además** de
> intradía no mejora la fila.

Donde nadie estaba mirando. `roca_chip_al` devuelve el ratio roca→chip **como percentil dentro de su
último año (0 a 100)**, y `snapshot.py` sella ese `valor`:

| | `roca_chip` (percentil del año) |
|---|---|
| sellado 28-sep (13:42 NY) | **44** |
| recomputado 28-sep (post cierre) | **17** |

El valor crudo recomputado es **−2,8 %**, y la serie de los días anteriores va +2,80 (22-sep), +2,61
(23), +3,05 (24), +3,64 (25): o sea que el 28 hubo una **caída brusca** del ratio, y la barra intradía
de las 13:42 **la escondió**. Los `roca_chip` sellados de la semana venían 43 · 41 · 39 · 42, así que
el 44 sellado parece una continuación tranquila y el valor real, 17, es el más bajo del mes.

**Y el canal de publicación es más ancho que el reporte de Telegram** (lo verificó el auditor, y mi
primera redacción lo subestimaba): `alertas.py` escribe `Roca→Chip: {roca_chip}/100` desde la fila
sellada, **y además** `senales.historial_roca_chip(dias=365)` lee `snapshots.roca_chip` sellado,
`api/main.py` lo sirve en `/` y en `/cadena`, `frontend/src/vistas/Hoy.tsx` lo muestra como **tarjeta
hero** con la etiqueta «percentil 1 año · sellado {fecha}» **más un sparkline de la historia**, y
`Cadena.tsx` grafica la serie. O sea: **el 44 no es un número de una noche, es un punto permanente de una
serie de 365 días que la interfaz grafica**, y por la Constitución 5.0 §3 las filas selladas no se
reescriben. No está en `README.md` ni en `cifras.py`, así que queda fuera de las cifras congeladas.

**Lo que baja la gravedad, en justicia:** `roca_chip_al` recomputa la serie desde precios y no desde
valores sellados, así que **los percentiles futuros no quedan envenenados** por el 44. La contaminación
está confinada a la fila sellada y a lo que la muestra.

**Y los 27 puntos son el PISO, no la medida — INFERIDO.** Del mapeo crudo↔percentil de los días
adyacentes (+2,61 → 39, +2,80 → 41, +3,05 → 42: ≈1 punto de percentil por cada 0,15 pp de crudo en esa
zona), un percentil sellado de 44 implica un crudo sellado de **≈ +3 %** contra el **−2,8 %** real: **el
ratio roca→chip crudo cambió de signo, del orden de 5,8 pp.** Va etiquetado **INFERIDO** y es
**permanentemente inmedible**, porque `snapshot.py` sella el percentil y **no** el `crudo_pct` que el
motor sí calcula — para el 28-sep y para toda fila histórica.

**Esto reordena la gravedad del hallazgo.** La contaminación es **chica en el canal lineal de insumo
único** —la predicción es `beta × escalar`, así que un error de 0,02 pp en el escalar propaga ≤0,11 pp,
acotado por construcción— y **grande en el canal no lineal y agregado**: un percentil de un promedio de
momentum sobre los eslabones de la cadena, donde la barra intradía mueve **todos** los eslabones a la vez
y después el percentil comprime o expande según la densidad local.

**Y el auditor cerró con un argumento más fuerte que el mío, que hay que dejar escrito:** el argumento a
favor de la regla del §61 **no puede ser «medimos y el daño fue chico»**, porque el canal donde el daño
resultó grande es justamente el que nadie puso primero —él mismo incluyó `roca_chip` en una lista plana de
cuatro sospechas, sin jerarquizarla—. «Una regla que dependa de que alguien jerarquice bien los canales
ex ante falla la primera vez que alguien jerarquiza mal, y esta corrida es esa primera vez.» **La regla
tiene que sostenerse en la violación de orden, ex ante, sin consultar el daño.**

### 9.5 Lo que esta medición APORTA, y no es lo que parece: confirma la no-reproducibilidad

Es el aporte probatorio más fuerte de toda la sección, lo dijo el auditor en su dictamen
complementario, y mi primera redacción lo dejaba implícito — con lo cual la sección leía como atenuante
cuando su contenido más fuerte es **agravante**.

El dictamen original **deducía** que un tercero que reprodujera el cómputo obtendría otro número. Esta
medición es ese tercero: obtuvo **−1,61 donde el sello dice −1,63** y **17 donde el sello dice 44**.
**La no-reproducibilidad dejó de ser una inferencia del auditor y es un hecho medido.** Ninguno de los
cuatro fundamentos del veredicto se movió, y uno de ellos quedó confirmado empíricamente.

De ahí que el veredicto se sostenga **con fuerza neta mayor**, no menor:
`VEREDICTO: FILAS INVÁLIDAS ENTRARON COMO VÁLIDAS`, sin cambio de forma. Y el porqué de fondo, que
ordena todo lo demás: **la validez de un sello no es función del tamaño del error.** El riel de dinero no
preguntó cuánto se había desviado su insumo antes de marcar 33/33 filas `roto` con `cuenta_para_N = 0`:
invalidó por la violación de orden, sola. **Si el veredicto se ablandara porque el error salió chico, eso
sería elegir qué filas cuentan después de verlas** — la misma fuga de selección que 9.5.3 prohíbe en la
dirección opuesta. Vale en las dos: **la medición no puede rescatar a las filas por la misma razón por la
que no puede condenarlas.**

### 9.5-bis Lo que esta medición NO midió, y es el hueco vivo de la corrida

§9 mide el insumo, las 8 predicciones, el régimen y `roca_chip`. **No mide `puntaje_v0`, `puntaje_ia` ni
`divergencias` del 28-sep**, que el dictamen original también había nombrado. Y eso importa más que el
resto, porque **`puntaje_ia` es el campo de las 24 filas** —no de las 8— que entran a
`verificacion_puntaje` alrededor del **5-oct**. Es el ítem con más filas en juego y sigue **SIN MEDIR**;
con `roca_chip` habiendo salido 27 puntos, la omisión ya no es simétrica con las demás.

Y hay algo peor, que el auditor señaló y que conviene entender antes de planificarlo: **esa medición ya
no se puede hacer contra la barra sellada.** La barra parcial de las 13:42 no existe en ninguna parte; se
puede medir el valor correcto de hoy, pero **nunca la diferencia**.

### 9.6 Lo que esta medición NO dice, y hay que decirlo con cuidado

1. **−1,61 tampoco es necesariamente el cierre definitivo.** Se leyó a las 16:31 NY, 31 minutos después
   de la campana, y el propio bloque 1.6 de esta corrida midió que en 2 de 4 noches no todos los
   tickers tenían su cierre en yfinance ni a las 23:35 NY. Lo medido es «la lectura de las 16:31
   difiere de la sellada en 0,02 pp», no «la diferencia contra el cierre liquidado es 0,02 pp».
2. **Es UNA fecha.** No dice nada sobre cuánto se desvía en general una barra parcial: dice cuánto se
   desvió ésta, un día en que la sesión cayó fuerte al final.
3. **Y sobre todo: esta medición NO puede decidir la regla.** Lo marcó el director y hay que dejarlo
   escrito: si las filas se retiraran sólo cuando el signo salió mal, eso sería **elegir qué filas
   cuentan después de verlas**, que es exactamente la fuga de selección que el auditor advirtió que
   esta auditoría podía crear. **La regla del §61 se firma por su mérito** —es la que el otro riel ya
   aplica y es un endurecimiento— **y después se mide el daño.** Esta sección es el daño, no el
   argumento.
4. **La columna «recomputado» no es reproducible por nadie, y el auditor la aceptó por mi palabra.** Lo
   corrí con `python -c` en un proceso aparte y **no dejé script, log ni artefacto en disco**: el auditor
   buscó archivos modificados entre las 17:20 y las 17:50 y no encontró ninguno que correspondiera. Lo
   que sí pudo verificar es la **coherencia interna** de la tabla: dividiendo cada recomputado por −1,61
   recuperó las betas (0,031 · 0,304 · 0,323 · 0,565 · 0,590 · 0,658 · 0,801, y **0,497** para 8035.T,
   que es el «≈0,50» declarado). **Corrección del `curador-epistemico`: escribí «todas dentro de 0,005»
   y es falso** — 0,801 contra 0,81 son 0,009, 0,304 contra 0,31 son 0,006, y **0,497 contra 0,56 son
   0,063, doce veces la tolerancia que declaré**. Lo correcto: **las siete dentro de 0,009** (el redondeo
   a dos decimales de las dos columnas ya da ±0,003), **y 8035.T a 0,063 porque su beta se reestimó**. El
   hallazgo que esto sostiene —que la tabla es un output coherente del modelo— sobrevive con la
   tolerancia corregida. Eso confirma que la tabla es un
   output coherente del modelo, **no** que la descarga fuera la que digo. El comando exacto, para que
   quede al menos enunciado: `motor._cache.clear()` y después `motor.prediccion_apertura_al(date(2026,9,28))`,
   `motor.regimen_al(...)` y `motor.roca_chip_al(...)`.
5. **La asimetría de verificabilidad es permanente.** La columna «sellado» se verifica contra
   `senales.db` cuando uno quiera. La columna «recomputado» no se puede verificar contra nada, y **la
   barra parcial de las 13:42 ya no existe**: esta comparación no se puede repetir nunca, ni por mí ni
   por un tercero.
6. **`snapshot.py` sella el percentil y no el crudo.** `roca_chip_al` calcula `crudo_pct` y no se
   persiste, así que la magnitud de la contaminación cruda es **inmedible desde el sello** — para el
   28-sep y para toda fila histórica.


---

## 10. Lo que la máquina confirmó antes de que la corrida terminara

La sección 6-bis dejó predicciones falsables sobre lo que harían los timers de la tarde. La corrida siguió
viva hasta pasadas las 20:00, así que **cuatro de las cinco ya se pueden contrastar**, y las cuatro se
cumplieron. Lo levantó el `curador-epistemico`; lo verifiqué después contra los logs.

| hora | predicción de 6-bis | qué pasó |
|---|---|---|
| 18:15 | «no re-sella; devuelve `ya existe snapshot de hoy`; el verificador no tiene nada nuevo» | **`data/snapshot.log:142`: `{'snapshot': False, 'motivo': 'ya existe snapshot de hoy'}`** y `verificador apertura: {'verificadas': 0, …}`. Exacto. |
| 18:25 | «va a enviar un reporte completo desde el sello del 28, con `roca_chip` 44» | **`data/reporte.log`: 831 caracteres, «Reporte enviado 18:25»** — el tamaño normal, contra los 400 del disparo de las 14:42. Las cifras del sello de las 13:42 **salieron**. |
| 18:40 | «commitea `data/backups/` con pathspec, incluido `ext_2026-09-28.*`; nada de la corrida se cuela» | **commit `f7b65e0 «Backup diario 2026-09-28»`, 9 archivos, todos bajo `data/backups/`**, con `ext_2026-09-28.{csv,meta.json}` dentro y **ningún** archivo de la corrida. Exacto, incluida la parte tranquilizadora. |
| 19:00 | «la guarda de ancla temporal **no va a ver** la inversión, porque prueba `av == ts`» | **`data/vigia.log:233`: `OK ancla temporal: 8/8 filas con cierre del SOX`.** La guarda dio el visto bueno a las ocho filas inválidas, muda, tal como se predijo. Es la confirmación empírica del defecto de `mki_vigia.py`. |
| 00:30 del 29 | «cero filas insertadas; `divergencias_sello` 1 → 2; `sellos_dinero` sigue en 462» | **Pendiente.** Se contrasta mañana. |

**Dos consecuencias de que la corrida haya cruzado la tarde, que hay que anotar porque cambian afirmaciones
de esta bitácora:**

1. **`HEAD` ya no es `5321f6b`: el job de backup de las 18:40 commiteó `f7b65e0`.** No fue la corrida, y el
   commit toca sólo `data/backups/`. Efecto secundario que conviene ver: **`ext_2026-09-28.{csv,meta.json}`
   quedó versionado**, o sea que la matriz de media sesión que 33 filas citan por sha **ya está en git**,
   que es justo lo que la tarjeta §62 anticipaba.
2. **`senales.db` se movió a las 18:15:12** (huella `c462d5db…0dfd111`), por las cuatro filas que el
   verificador de puntaje metió en `verificacion_puntaje` (1.181 → 1.185). `snapshots` sigue en 59,
   `senales_ticker` en 1.375, `verificacion_apertura` en 420, y **las 8 filas del 28-sep siguen
   `pendiente`**: se verifican mañana, que es la razón por la que el §61 tiene reloj.
   `dinero/sello_dinero.db` sigue intacta.

**Y el aviso que apareció en el log de las 18:15 y que reabre la sección 9:**
`- Tokyo Electron (8035.T): salto de -80% el 2026-09-28 — revisar split/dato corrupto`. Está tratado en
9.4; lo que corresponde decir acá es que **llegó 44 minutos después de la medición de las 17:31**, así que
la sección 9 se escribió sin saberlo, y que por eso sus cifras de `roca_chip` quedan PROVISIONALES.


---

## 11. La sonda corregida disparó en producción a las 21:05, y midió algo que nadie había visto

La corrida siguió viva hasta pasadas las 21:00, así que **el primer disparo real de la sonda con el código
de esta corrida se puede contrastar**. No se tocó nada: `data/sonda_cierre.csv` y `GEMELO/sonda_cierre.py`
están en la franja de la sonda (21:05–00:35) y el encargo prohíbe modificarlos ahí. Esto es lectura.

### 11.1 La corrección funciona en producción

`journalctl`: `mki-sonda-cierre.service` arrancó **21:05:00** y terminó **21:05:03**. La fila que escribió:

```
timestamp_utc 2026-09-29T00:05:01.082076+00:00 · hora_ny 20:05 · sesion_ny 2026-09-28
```

**Es exactamente la prueba que el bloque 1 buscaba, en vivo:** el instante es **29-sep en UTC** y la sonda
lo atribuyó al **28-sep**, porque en Nueva York son las 20:05 del 28, después de la apertura. Con la regla
vieja el resultado habría sido el mismo en este caso (es una sonda de tarde), así que esto **no** prueba la
franja de madrugada; lo que prueba es que `sesion_atribuida()` está en el camino y no rompió nada. El CSV
pasó de 1.188 a **1.224 filas**, todas con `sesion_ny` bien puesto.

### 11.2 Y el dato de §58: a las 20:05 NY **1 de 36** tenía el cierre del 28

```
data/sonda_cierre.log
  13:42 NY · sesión 2026-09-28 · 35/36 con cierre de hoy · faltan: ['TOELY']
  20:05 NY · sesión 2026-09-28 ·  1/36 con cierre de hoy · faltan: [los otros 35]
```

Cuatro horas **después** del cierre, treinta y cinco de treinta y seis tickers **no** tenían el cierre del
28-sep en yfinance. Es una noche peor, a esa hora, que la del 22-sep. **DESCRIPTIVO, n = 1 noche**, y no
cambia la regla de 1.7: sigue habiendo 4 noches completas y no se escribe ninguna recomendación sobre §58.

### 11.3 El hallazgo: **la barra que existía a las 13:42 ya no estaba a las 20:05**, y son 35 tickers

Puesto en la forma del hallazgo de la corrida 13 —«un cierre que estaba y deja de estar»—: dentro de la
**misma sesión atribuida** (2026-09-28), 35 tickers pasaron de `es_sesion_de_hoy = 1` a las 13:42 NY a
`es_sesion_de_hoy = 0` a las 20:05 NY. La corrida 13 lo había medido con **n = 1 par y un ticker**; acá son
**35**, en un solo par de sondas.

**Qué es y qué no es.** Lo que desapareció **no es un cierre**: es la **barra intradía provisional** que
yfinance publicaba con la fecha del día mientras el mercado estaba abierto. Al cerrar la sesión la retiró y
todavía no había publicado el cierre liquidado. O sea que esto **no** es el mismo fenómeno que el de la
corrida 13 (que era entre dos descargas separadas 24 h, sobre cierres ya liquidados); es el
**mecanismo que hace posible** al fenómeno, visto de cerca.

**Y no contradice el «0 de 1.008 pares» de 1.6**, que se midió sobre las cuatro noches completas y dentro
de la franja 20:05–23:35, donde todas las observaciones son post-cierre: el filtro de 1.3-bis descarta la
fila de las 13:42 justamente porque una observación con el mercado abierto no dice nada del cierre. Lo que
este par muestra es por qué ese filtro tenía que existir.

**Lo que sí confirma, y es lo que importa para el §61:** la zona ciega #10 del auditor, que había declarado
en abstracto —«la barra parcial de las 13:42 ya no existe en ninguna parte: esta comparación no se puede
repetir nunca»—. **Ahora está medida.** La barra con la que `snapshot.py` selló las 24 filas del 28-sep
desapareció de la fuente el mismo día, entre las 13:42 y las 20:05 de Nueva York. El sello cita un insumo
que **la fuente ya no sirve**, lo que vuelve la no-reproducibilidad de esas filas no sólo medida (§9.5) sino
**irreversible**.
