# Bitácora de la corrida 15 — noche del 29 al 30-sep-2026

**Encargo:** `~/encargo.md`, «Encargo corrida 15 (nocturna, v2)», 27.374 bytes, mtime 29-sep 21:50.
La regla de decisión de §58 antes del primer dato de madrugada, las firmas del acta §90 aplicadas,
el inventario de los ocho jobs ante un despertar, y las deudas chicas de la corrida 14.

**Horas.** Todas leídas de `date` en la máquina, nunca estimadas. Zona: Chile (UTC−3); Nueva York
va una hora atrás (UTC−4) durante toda la corrida. Arranque **21:57:45** del martes 29-sep-2026.

**Dos desvíos del encargo respecto de la máquina, declarados desde la primera línea.**

1. **El esfuerzo.** El encargo pide «Fable, esfuerzo alto». La sesión corrió con Fable 5.1 y
   esfuerzo **xhigh**, fijado por Nicolás con `/effort` antes de lanzar. No se cambió a mitad de
   sesión. Manda la máquina; es errata del encargo, no de la corrida.
2. **El nombre.** El acta §91.1 nombra el encargo `encargo_corrida_15_noche_v2.md`; el archivo
   lanzado es `~/encargo.md`, con ese título adentro. Misma pieza, nombre distinto.

---

## 0. Orientación y prerrequisitos (21:57 – 22:30)

### 0.1 Timers que disparan durante la corrida

`systemctl --user list-timers --no-pager --all`, leído a las 21:57:

| timer | próximo disparo | último |
|---|---|---|
| `mki-sonda-cierre` | mar 29 22:05 | mar 29 21:35 |
| `mki-sello-dinero` | mié 30 00:30 | mar 29 00:30 |
| `mki-noticias` | mié 30 17:50 | mar 29 17:50 |
| `mki-snapshot` | mié 30 18:15 | mar 29 18:15 |
| `mki-reporte` | mié 30 18:25 | mar 29 18:25 |
| `mki-backup` | mié 30 18:40 | mar 29 18:40 |
| `mki-vigia` | mié 30 19:00 | mar 29 19:00 |
| `mki-vigia-rechequeo` | mié 30 20:30 | mar 29 20:30 |

Durante la corrida disparan, entonces, **la sonda** (a los :05 y :35: franja de tarde hasta las
00:35 y franja de madrugada de 01:05 a 04:35) y **el sellador** (00:30). Los seis del riel de
medición ya dispararon hoy y no vuelven hasta las 17:50 del 30.

### 0.2 Árbol de git, como el encargo lo espera

`2f73eb2 Backup diario 2026-09-29` sobre `fa7b5ba` (corrida 14 y acta §90). Rama `main`. Sin
commitear: `DECISIONES.md` (+27 líneas, el acta §91 que Nicolás anexó) y `data/sonda_cierre.csv`
(+108 líneas, de la sonda). `git worktree list` mostraba sólo el árbol real.

### 0.3 Suite al abrir: los dos rojos conocidos, y nada más

Lanzada a las **22:03:51**, terminada a las **22:11:02**. `pytest tests/ -q`:
**2 failed, 896 passed, 5 skipped, 1 xfailed** en 421,39 s (7 min 01 s); 904 recolectados.
`tests/test_motor.py`: todas las funciones pasan el test de no contaminación.

Los dos rojos son los que el encargo nombra, los dos de `tests/test_readme.py`:
`test_los_dos_readme_son_lo_que_el_generador_produce` y
`test_el_contador_de_e0_del_readme_es_el_de_la_copia_versionada`. **No hubo ningún rojo
inesperado, así que la norma de §91.6 no se aplicó al abrir.**

**Error propio 1.** La suite se lanzó a las 22:03:51 creyendo que el disparo de la sonda de las
22:05 ya había pasado: no leí `date` en ese turno. Corrió encima del disparo. La sonda disparó
igual a las 22:05:00 y terminó a las 22:05:02 (`journalctl`), 2,365 s de reloj contra los 2,3 a
2,9 s de los disparos anteriores, así que no hubo daño medible. Es la regla de la memoria del
proyecto (las horas se leen, no se estiman) rota en la primera media hora.

### 0.4 Pre-mortem del director, y qué se hizo con cada instrucción marcada

Dictamen completo en `dictamen_15/director_premortem.md`. Veredicto: **ADELANTE CON TRES
INSTRUCCIONES MARCADAS** (marcó seis). Lo que se hizo con cada una:

| # | instrucción del encargo | qué se hizo |
|---|---|---|
| B1 | bloque 1.2: «cierre de NYSE + margen que el código ya use» | **No se ejecutó como está escrita.** El único margen que el código usa es el de `sesion_ya_cerro` (2 h), que es criterio de verificación; el job sella 1 h 15 min después del cierre, así que con ese margen dejaría de sellar todos los días. La guarda se escribió como `available_at > emisión`, margen cero, que es el texto literal del acta §90.1 (b): «si la sesión de `sox_fecha` no ha cerrado». Es el caso que prevé la última línea del encargo |
| B2 | regla 3 de la noche | resuelta por escrito en 0.5, con el cierre de imports pegado |
| B3 | reglas 1 y 5 contra la suite de cierre | interpretación declarada en 0.6, antes de las 00:15 |
| B4 | bloque 1.5: tocar el vigía | **va a tarjeta**, por el dictamen que el encargo le delega al director |
| B5 | bloque 0.6: «verifica contra `man systemd.timer`» | el procedimiento se escribió para que sirva bajo las dos hipótesis, y no dice «verificado contra el manual» |
| B6 | bloques 2 y 4 juntos | el backup commitea igual en un día que ya no puede sellar (bloque 4) |

### 0.5 Regla 3 de la noche: qué importan el sellador y la sonda

**Lectura elegida, por escrito antes de aplicar nada:** la regla protege a los dos jobs que
disparan esta noche, así que lo que no se aplica al árbol real es todo módulo que **ellos
importen**, directa o indirectamente. Es la lectura del acta §91.1 («ningún módulo que importen
el sellador o la sonda se aplica al árbol real»). La otra lectura posible del encargo (los
módulos que importan *al* sellador) no protege nada: que `api/main.py` importe el sellador no
cambia lo que el sellador ejecuta a las 00:30.

Cierre transitivo de imports por AST, sin ejecutar nada, incluidos los imports perezosos dentro
de funciones (22:19):

- `dinero/sello_dinero.py`, 14 módulos del repo: `backtest/__init__.py`, `backtest/datos.py`,
  `backtest/emision.py`, `backtest/inferencia.py`, `calendarios.py`, `dinero/__init__.py`,
  `dinero/contabilidad.py`, `dinero/cuenta_papel.py`, `dinero/decision.py`, `dinero/precios.py`,
  `dinero/sello_dinero.py`, `dinero/universo_dinero.py`, `motor.py`, `universo.py`.
- `GEMELO/sonda_cierre.py`: ninguno fuera de sí mismo.

**Ningún archivo que esta corrida modifica está en ese cierre**: `senales.py`, `snapshot.py`,
`backtest/linea_base.py`, `mki_backup.py`, `scripts/generar_readme.py`, `cifras.py` y
`version.py` dan «no importado». `calendarios.py` sí está en el cierre del sellador, y por eso
mismo esta corrida no lo toca.

### 0.6 Reglas 1 y 5 contra la suite: interpretación declarada antes de las 00:15

El pre-mortem encontró que tres instrucciones no se pueden cumplir a la vez sin decir antes cómo
se leen. Queda dicho acá, a las 22:30, antes de que exista ninguna fila de madrugada:

1. **Regla 1 (tramo de 00:15 a 00:50).** `tests/test_sello_dinero.py` abre la base real del
   sellador en sólo lectura. La suite tarda 7 min 01 s. **Ninguna suite se lanza después de las
   00:05**, para que ninguna esté corriendo a las 00:15, y ninguna se lanza antes de las 00:50.
2. **Regla 5 (ninguna fila de madrugada).**
   `tests/test_sonda_cierre.py::test_la_regla_nueva_reproduce_el_sesion_ny_de_todas_las_filas_ya_escritas`
   lee **todas** las filas del CSV real. Después de las 01:05 eso incluye filas de madrugada. Se
   lee así: la regla prohíbe que el contenido de una fila de madrugada llegue a un agente; la
   entrada y salida de un test no es un agente leyendo, **siempre que de ese test no se mire más
   que si pasó o falló**. Por eso toda suite posterior a las 01:05 escribe su salida a un archivo
   y de ese archivo se leen los nombres de los tests fallidos **sin su mensaje** (el mensaje de
   ese test imprime hasta tres filas).
3. **Si ese test falla**, esta corrida **no lo clasifica**: clasificarlo exige leer las filas.
   Se declara «rojo no clasificable sin violar el acta §91.3», se detiene lo que dependa de un
   verde completo, y se deja a Nicolás. No se busca otro camino para clasificarlo.
4. Todo lo demás que se lee del CSV en esta corrida pasa por un filtro
   `timestamp_utc < 2026-09-30T04:00:00Z` aplicado **antes** de imprimir. El corte es de
   instante, no de fecha: la franja de tarde de esta noche ya lleva fecha UTC del 30-sep.
5. El worktree de la corrida tiene el CSV de la sonda **de HEAD** (su última fila es del
   `2026-09-29T03:35Z`): ahí adentro no puede haber una fila de madrugada.

### 0.7 Huellas de las bases al abrir (21:59:18)

| base | sha256 |
|---|---|
| `senales.db` | `12fe11ec9e232fef9bfdbad9d5213b9c2d5734289e91251910b89814d7c44041` |
| `noticias.db` | `5c8b9f8df422cdef62a5473c95c3e8675d16506cc145ea7086df4f88b2ae84f3` |
| `dinero/sello_dinero.db` | `462c45dba62ba9fca19c81626007ed8a6f0657d9c6bbc225a94ba7531b092472` |

`alertas.db`, que `CLAUDE.md` nombra, **no existe** en esta máquina. Las tres huellas eran las
mismas a las 22:11:50, después de la suite.

### 0.8 Prerrequisitos leídos de la máquina, contra el acta §91.7

Todos leídos entre las 21:59 y las 22:08, o sea antes de las 00:15.

**Riel de dinero** (`dinero/sello_dinero.db`, `mode=ro`, 22:00 y 22:07). 462 filas en
`sellos_dinero`, 14 fechas de insumo. La fecha 2026-09-28 tiene sólo 33 filas
`no_verificable_timing`, emitidas a las 13:43 NY, `cuenta_para_N = 0`. **Contador: 9.**
`divergencias_sello`: **2** filas, máximo 2026-09-28 (la segunda es del `2026-09-29T03:30:04Z`,
0 decisiones distintas). **Coincide con el acta.**

**Riel de medición** (`senales.db`, `mode=ro`). La consulta del encargo, copia textual:

```
SELECT fecha, COUNT(*) FROM senales_ticker WHERE available_at > timestamp_utc GROUP BY fecha
('2026-09-28', 24)
```

Una sola fecha, 24 filas. De ellas 8 tienen predicción y estado `verificada`; las otras 16 no
llevan predicción y su estado es NULL. Las 24 comparten `timestamp_utc`
`2026-09-28T17:42:58.943983+00:00` y `available_at` `2026-09-28T20:00:00+00:00`.

Lo que escribió el verificador de las 18:15 del 29-sep en `verificacion_apertura` para esas
filas, copia textual (columnas: `id, fecha_senal, ticker, apertura_estimada_pct,
retorno_real_pct, acierto_direccion, error_pp, verificado_en, gap_pct, acierto_gap,
error_gap_pp, modelo_version, legacy`):

```
(422, '2026-09-28', '000660.KS', -1.32, -0.1697, 1, 1.1503, '2026-09-29T21:15:11.679258+00:00', -0.7353, 1, 0.5847, '4.6.0', 0)
(423, '2026-09-28', '005930.KS', -0.97, 0.9259, 0, 1.8959, '2026-09-29T21:15:12.057242+00:00', -1.4815, 1, 0.5115, '4.6.0', 0)
(424, '2026-09-28', '2330.TW', -0.53, 0.0, 0, 0.53, '2026-09-29T21:15:12.445617+00:00', 0.0, 0, 0.53, '4.6.0', 0)
(425, '2026-09-28', '3436.T', -1.08, 0.6623, 0, 1.7423, '2026-09-29T21:15:12.814677+00:00', 2.3179, 0, 3.3979, '4.6.0', 0)
(426, '2026-09-28', '4063.T', -0.5, -0.7767, 1, 0.2767, '2026-09-29T21:15:13.182137+00:00', -1.0701, 1, 0.5701, '4.6.0', 0)
(427, '2026-09-28', '6857.T', -0.92, 0.5336, 0, 1.4536, '2026-09-29T21:15:13.550790+00:00', 0.2668, 0, 1.1868, '4.6.0', 0)
(428, '2026-09-28', '8035.T', -0.91, 5.7445, 0, 6.6545, '2026-09-29T21:15:13.917757+00:00', 4.3658, 0, 5.2758, '4.6.0', 0)
(429, '2026-09-28', 'IFX.DE', -0.05, 4.8259, 0, 4.8759, '2026-09-29T21:15:14.284180+00:00', 2.3511, 0, 2.4011, '4.6.0', 0)
```

**Son 8, como el acta esperaba.** El log del verificador dice «9 verificadas»: la novena es una
fila del 24-sep (`verificado_en` `2026-09-29T21:15:11.311943`), no del 28. Estas ocho filas
quedan como registro histórico y fuera de toda métrica por la regla de §90.1 (d); esta corrida
no las interpreta.

**La sonda.** `systemctl --user cat mki-sonda-cierre.timer`: las dos franjas
(`Mon..Fri 20..23:05,35` y `Tue..Sat 00..03:05,35 America/New_York`) y `Persistent=false`.
**Coincide.** Su `Description=` sigue diciendo «la franja de madrugada no está instalada», y ya
lo está: es la errata que el acta §91.7 ya registra como edición manual de Nicolás. No se tocó.

**El disparo de las 18:38:57.** Ver 0.9.

**8035.T en `data/snapshot.log`.** El aviso «salto de −80 % el 2026-09-28» aparece **una sola
vez**, en la corrida de las 18:15 del 28-sep (línea 147). **No se repitió**: la corrida de las
18:15 del 29-sep dice «salud de datos: OK (27 tickers)». Lo que era, en la sección 6.4.

### 0.9 El disparo de las 18:38:57 y la hipótesis del acta §91.7

**Medido.** `journalctl --user`, 29-sep 18:38:57, los cuatro eventos en el mismo segundo:
`Starting mki-sonda-cierre.service`, `Stopped mki-sonda-cierre.timer`,
`Stopping mki-sonda-cierre.timer`, `Started mki-sonda-cierre.timer`. El servicio terminó a las
18:38:59. La unidad tiene `Persistent=no` (`systemctl --user show`).

**Contra el manual.** `man systemd.timer` (systemd 259.5-0ubuntu3.4) documenta el disparo al
activar sólo para `Persistent=true`. No dice qué instante usa de base un `restart` con
`Persistent=false`. **El manual no confirma ni refuta la hipótesis.**

**Contra lo observado.** `systemd-analyze calendar --base-time=` no toca ninguna unidad:

| base | calendario | próximo disparo calculado | a las 18:38 |
|---|---|---|---|
| último disparo, 29-sep 00:35 | nuevo (madrugada) | mar 29-sep 01:05 | ya pasado |
| último disparo, 29-sep 00:35 | viejo (sólo tarde) | mar 29-sep 21:05 | futuro |
| activación anterior, 20-sep 02:05:59 | viejo (sólo tarde) | lun 21-sep 21:05 | ya pasado |

**La hipótesis del acta (H-A, la base es el último disparo) es compatible con lo medido, y no
es la única.** Una segunda (H-B, la base es la activación anterior del timer, el
`InactiveExitTimestamp`) predice el mismo disparo. Se diferencian en lo que importa: bajo H-B
**cualquier** `restart` de un timer que lleva días activo dispara en el acto, cambie o no el
calendario. Un solo evento no las separa, y separarlas exigiría reiniciar una unidad. **Estatus:
PROPUESTA, n = 1.** El journal de usuario empieza el 24-ago y no trae ningún otro `restart` de
un timer `mki-*`: los `Stopped`/`Started` del 19 y 20-sep son reinicios del manager (cambia el
PID de `systemd`), no de un timer.

**Consecuencia para §58 (b), que el acta ya anticipaba.** El sellador tiene `Persistent=yes`
(leído de la máquina), y para él el disparo al activar sí está en el manual. El procedimiento
quedó en la sección 6 de `GEMELO/propuestas/regla_58.md`, escrito para las dos hipótesis.

### 0.10 Hallazgo de paso: el journal del sistema tiene un latido, y acota la suspensión

A las 22:02:45 los tres timers consultados (`mki-sonda-cierre`, `mki-sello-dinero`,
`mki-snapshot`) mostraban el mismo `StateChangeTimestamp`: mar 29-sep 22:02:25. Esta corrida no
ejecutó ninguna orden que cambie estado (sólo `cat`, `show` y `list-timers`). El journal de
usuario no tiene nada a esa hora; **el del sistema sí** (**Error propio 2.** La primera redacción de
esta sección decía que el journal no registraba nada a esa hora: se escribió antes de mirar el journal
del sistema; corregida en su sitio antes del commit, y de ahí salió el hallazgo del latido): `systemd-resolved: Clock change
detected. Flushing caches`, a las 22:02:25 y otra vez a las 22:02:55. Los próximos disparos no
cambiaron.

**MEDIDO:** esa línea aparece **cada 30 segundos** mientras la máquina corre (2.880 el 24-sep,
que son todas las de un día entero; 2.699 el 29-sep hasta las 22:29). WSL2 resincroniza el reloj
dos veces por minuto y `systemd-resolved` lo anota. Es, sin que nadie lo haya diseñado, un
**latido de la máquina con resolución de 30 s**.

Conteo por día: 24-sep 2.880; 25-sep **435**; 26-sep **0**; 27-sep **0**; 28-sep **1.116**;
29-sep 2.699. Y desde el 20-sep a las 02:06 hay **un solo hueco mayor que dos minutos**:

```
hueco de 4985,7 min: 2026-09-25 03:37:10 -> 2026-09-28 14:42:52
```

**La máquina dejó de correr el viernes 25-sep a las 03:37:10 y volvió el lunes 28-sep a las
14:42:52, con 30 s de incertidumbre en cada extremo.** La corrida 14 sólo había podido acotar
el comienzo a [vie 02:16, vie 17:50] y escribió, con razón para lo que tenía a la vista, que
«WSL2 no registra suspend/resume». No registra el evento; registra la ausencia. Que haya sido una
suspensión y no un apagado sigue saliendo de lo que la corrida 14 midió (el mismo `systemd[317]`
a los dos lados del hueco): el latido dice **cuándo**, no **qué**.

Dos usos, los dos de esta corrida: es el instrumento con que se comprueba el punto 8 de las
reglas de la noche al cerrar (sección 9), y es un dato para el inventario de los ocho jobs.
**No se corrigió ningún documento de la corrida 14 con esto:** están commiteados, y la cota más
fina va como errata fechada en el acta §92.

---

## 1. Bloque 0: la regla de decisión de §58, escrita antes del primer dato de madrugada (21:57 – sellado)

### 1.1 Cronología, con horas de `date`

- **22:03:51** última lectura del CSV de la sonda para redactar (filtrado por
  `timestamp_utc < 2026-09-30T04:00:00Z`; última fila leída `2026-09-30T00:35:00Z`).
- **22:07:44** funciones puras del sellador evaluadas con emisiones hipotéticas pasada la
  medianoche de Nueva York (sección 1.3).
- **22:15:47** calendario de sesiones, cambios de hora, umbrales de Wilson y potencia binomial
  calculados con `evaluacion.py` (módulo de la casa; nada a mano).
- **22:18:25** primera versión de `GEMELO/propuestas/regla_58.md` escrita (363 líneas);
  `estadistico-adversario` lanzado a las 22:18 con plazo a las 23:20.
- **22:30:52** (hora del agente) primer dictamen devuelto: APTA CON EXIGENCIAS, 10 bloqueantes y 7
  recomendadas. Archivado en `dictamen_15/adversario_regla58.md`.
- **22:36:59** verificación independiente de las cifras que el dictamen corrige (Wilson 3/11,
  4/13, 5/10; cuentas de sesiones por semana) y de una exigencia que se rechazó (1.2).
- **22:40:10** versión revisada escrita (501 líneas, sha256 provisional `2c7c5b6d…`).
- **~22:40 – 23:00** **corte de cuota de la API** («session limit, resets 11pm»): los seis agentes
  vivos (adversario, bloques 1, 2, 3, 4 e inventario) murieron a mitad de trabajo. A las 23:01 se
  retomaron los seis con su contexto intacto (`SendMessage` al mismo agente). El adversario recibió
  el pedido de re-dictamen a las 23:01 con plazo a las 23:35.

### 1.2 Qué se hizo con cada exigencia del adversario

Incorporadas con su texto o su equivalente: E1 (11 sesiones, no 12: el 8-sep se selló a las
23:38 NY, fuera de la ventana que la propia regla exige en V3; 3/11 = 27,3 % [9,7 · 56,6]; las
dos sesiones excluidas declaradas con lo que harían a la cifra. **Error propio 4.** La primera
versión de la regla citó 12 sesiones donde la ventana que la propia regla exige daba 11), E2 (convención de estimador
fijada: límite inferior de Wilson; la cuenta de noches que cuentan por semana muestra que mover
todas las noches con el código vigente es neto peor al umbral de 3, y que el empate exige 18,2 pp,
o sea 5 de 10), E3 (las ocho `R(t)` y `P(t)` se publican; el Wilson de un máximo seleccionado se
rotula como cota optimista), E4 (segunda lectura declarada, umbral 5 sobre 20, sin tercera), E7
(concordancia en cuatro clases; discordante sólo si incomparables), E9 (la característica operativa
de la regla compuesta se simula antes de evaluar), E10, E11, E12, E13, E14, E15, E16.

**Tres exigencias resueltas de otro modo, declaradas al adversario en el pedido de re-dictamen:**

1. **E8, rechazada con evidencia.** El adversario calculó el contrafáctico de H-A con el
   calendario de la PLANTILLA anterior a la corrida 14 (`Mon..Fri 17..23:05,35`) y concluyó que el
   evento de las 18:38 no discrimina las hipótesis. Pero ese calendario nunca se instaló: el acta
   §88.1 dice que Nicolás instaló `20..23`, y el CSV lo confirma (del 21 al 24-sep la primera
   observación de cada noche es la de las 20:05 NY y no hay ninguna entre las 17:00 y las 19:59;
   el journal muestra el primer disparo real el 21-sep a las 21:05 Chile). Con el calendario
   instalado, bajo H-A el próximo disparo era 21:05, futuro. La sección 6 quedó con esa evidencia
   y con la consecuencia operativa más severa que el adversario pedía.
2. **E5, resuelta por principio y no por contador.** En vez de invalidar las noches con apagón
   total y contar `n_O`, la validez pasó a ser «la máquina miró» (arranque del servicio en el
   journal dentro del casillero); un casillero con arranque y sin filas, o con
   `n_filas_respuesta = 0`, cuenta como no completo, que es lo que le habría pasado al sellador.
   La noche más informativa nunca sale del denominador.
3. **E6, adoptada con una corrección de hecho.** `data/backups/sello_dinero.csv` lo escribe el
   propio sellador al sellar (`exportar_csv` en `main()`); `mki_backup.py` sólo lo commitea. La
   cadena «backup no commitea → no hay fila en el CSV» no ocurre en disco. V3 usa la base como
   fuente primaria igual.

Y una corrección aritmética al ejemplo del estimador puntual: el rescate no puede exceder la
pérdida, así que se topó en 27,3 pp (da 4,00 y el signo igual se invierte).

### 1.3 El hallazgo que cambia el tamaño de (b): pasada la medianoche, el sellador marca `dia_sin_sesion`

MEDIDO a las 22:07:44 con las funciones puras de `dinero/sello_dinero.py` (sin base, sin red):
una emisión a la 01:00 NY del sábado 3-oct con el insumo del viernes 2-oct da `fecha_sello`
2026-10-03, `estado_dia = sin_sesion`, `estado = dia_sin_sesion`, `cuenta_para_N = 0`; lo mismo a
las 04:00 NY del sábado y la madrugada del jueves 26-nov (Thanksgiving). Una emisión a las 23:30 NY
del viernes da `sesion` y cuenta. Como las ocho horas candidatas de la regla son posteriores a la
medianoche, (b) tal como está en la tarjeta §58 («no reinicia el contador, la definición de "cuenta"
no cambia») no es sólo un cambio de hora: pierde 4 de cada 20 sesiones salvo que el acta que la
aplique resuelva los viernes. Está en la sección 5.2 de la regla y en la tarjeta.

### 1.4 Hipótesis juzgadas por el adversario, para el registro (E17)

Tres, todas sobre disponibilidad e instrumentación, ninguna sobre retornos: no suman al DSR de
ninguna familia. (H1) que 3/12 es la tasa antecedente: NO SOSTENIDA (es 3/11). (H2) que un umbral de
3 de 10 dimensiona el cambio de hora: NO SOSTENIDA con el código vigente (el empate exige 5 de 10).
(H3) que el evento de las 18:38 discrimina H-A de H-B: la rechazó por E8; con el calendario
instalado (1.2, punto 1) el contrafáctico sí las separa, pero un solo evento no verifica ninguna.

---

## 6. Bookkeeping y deudas (lo que no depende de los otros bloques, hecho en paralelo)

### 6.2 Las tres deudas chicas de la corrida 14 (acta §91.4)

- **(6) la skill `cierre-sesion`: APLICADA a las 22:26.** El «Recordatorio de estado» ya no
  describe el estado anterior al switch ni remite a `/switch-titular`: dice que el switch se
  ejecutó el 30-ago-2026, que al modo se le pregunta a `modo.py`, que mover modo o timers es de
  Nicolás, y remite a `/modo-emision`.
- **(5) la skill `gate`: NO APLICADA.** A las 22:26 la herramienta `Edit` sobre
  `.claude/skills/gate/SKILL.md` fue **denegada por el clasificador de permisos de la sesión**
  («Self-Modification»), la misma herramienta que un minuto antes había aceptado la edición de
  `cierre-sesion`. Una barrera puesta a propósito no se rodea con otra herramienta. Queda como
  propuesta instalable en `GEMELO/propuestas/skills/gate_gate_de_entorno.md`, con la línea nueva
  medida en esta máquina (`import pandas,numpy,yfinance,exchange_calendars,fastapi` corre e imprime
  `3.0.3 2.4.6`; `import scipy` e `import sklearn` dan `ModuleNotFoundError`). Tarjeta nueva.
- **(1) el «897» de `cola_decisiones.md`:** vive hoy en la línea 108 (sección de la corrida 13), no
  en la 89 que el propio documento cita. Se reemplaza al cierre por el valor que dé
  `pytest tests/ --collect-only -q` con todos los tests nuevos ya en el árbol, con errata fechada
  al lado (sección 9).

### 6.4 8035.T: era un split 5:1, el 17 era el artefacto, y el sistema no ajusta splits solo

MEDIDO a las 22:26:30, sólo lectura contra yfinance (`Ticker('8035.T').history(...)`, con
acciones corporativas): la fuente sirve **`Stock Splits = 5.0` con fecha 2026-09-29** (hora de
Tokio) y, en la misma fila, un dividendo de 384. Con eso la serie que sirve hoy es consistente:
cierre del 25-sep 11.304, del 28-sep 11.264, **−0,35 %**. El aviso «salto de −80 % el
2026-09-28» del job de las 18:15 del 28 era la fuente sirviendo, en ese momento, un lado del
split ajustado y el otro no. El 29-sep a las 18:15 la salud dio «OK (27 tickers)».

`roca_chip_al` releído a las 22:26:59 con la serie de hoy (función pura, sin base, sin
escritura), contra lo sellado:

| fecha | releído hoy | sellado | nota |
|---|---|---|---|
| 24-sep | 42 | 42 | reproduce |
| 25-sep | 45 | sin sello (suspensión) | |
| 28-sep | **39** (crudo +2,6 %) | 44 (13:42 NY, barra intradía) | la corrida 14 recomputó **17** con el artefacto |
| 29-sep | 50 | 50 | reproduce |

**DESCRIPTIVO: el 17 PROVISIONAL de la bitácora 14 (9.4) era el artefacto del split; la brecha real
entre lo sellado y lo recomputado con datos consistentes es 44 contra 39.** La fila sellada no se
toca. Y el hallazgo que va a tarjeta, no a código: `motor.py` confía en `auto_adjust=True` de la
fuente y no ajusta splits por su cuenta; `salud_datos_al` detecta el salto (umbral 0,40) y lo
escribe en el log, pero no frena ni marca el sello. `motor.py` es intocable.

### 1.5 Re-dictamen y sellado

- **23:05:16** (hora del agente) re-dictamen devuelto: APTA CON EXIGENCIAS, tres bloqueantes
  nuevas de un párrafo (E18: V3 mataba la noche de fuente caída a la hora del sellador; E19: la
  frase «el mismo umbral en todas las ramas» ya no era cierta; E20: la potencia de la rama (b)
  con umbral 5 es **0,11** a la tasa del antecedente, y había que decirlo) y dos recomendadas
  (E21: retención del journal; E22: el punto del antecedente cabe en [0,0 · 27,8], el intervalo
  no). **El adversario retiró E8 y el hecho de E6 como errores propios.**
- **23:07:25** potencia recomputada por el orquestador con la binomial y retención del journal
  medida (665,7 MB, persistente, sin límite configurado, desde el 24-ago).
- **23:07 – 23:08** las cinco exigencias incorporadas con su texto.
- **SELLADO: 2026-09-29 23:08:17 de Chile.** `sha256sum GEMELO/propuestas/regla_58.md` =
  `ca2ccd536f9d956c2b4a8404ec800341f29e4a0e1f1cd20720c08eca15b9a436` (540 líneas, 38.679
  bytes, mtime 23:08:06). **Antes de las 00:35 de Chile**, así que por la cláusula de la
  sección 2 de la propia regla la noche del 29-sep es la primera candidata y el plazo es la
  sesión del 26-oct-2026. Y antes de las 01:05: en toda la corrida no existió ninguna fila de
  madrugada al sellar (el journal muestra un solo disparo de la sonda entre las 23:00 y el
  sello, el de las 23:05, franja de tarde).
- Dictamen y re-dictamen archivados en `dictamen_15/adversario_regla58.md`. No hubo tercer
  dictamen: las tres exigencias eran de texto y se pegaron sin reinterpretar.

### 1.6 Anexo 1, después del sellado

`GEMELO/propuestas/regla_58_anexo_1.md`, escrito a las **23:13:56**, sha256
`2c9eec1de7ae5f98b4a2908312e19f9d42f7ef335520c1739abb6347118f5fc6`. La regla sellada no cambió
(sha256 idéntico al del sello, verificado en el mismo comando). Tres cosas leídas después del sello,
ninguna cambia regla, umbral ni definición: (1) por el orden del journal con precisión de
microsegundos (inventario del bloque 5), el disparo de las 18:38:57 lo produjo la **recarga** y no
el reinicio (INFERENCIA; el servicio arrancó 2,8 ms antes de que el timer se detuviera); el
procedimiento ya cubría las dos órdenes; (2) `man systemd.timer` documenta en `DeferReactivation=`
que la base por defecto del rearme es el disparo anterior, lo que favorece a H-A; (3) la observación
de las 17:38 NY del 29-sep es fuera de grilla y el lector actual `sonda_cierre_resumen.py` no la
excluiría si se regenerara el artefacto: no se regenera hasta la corrida 16. Y una errata candidata
para la bitácora 14 (11.3): la fuente retira la barra intradía después de las 17:38 NY, no «al cerrar
la sesión».

---

## 3. Bloque 2: el README sin contador, badges congelados, erratas de §88.5 (22:27 – 23:02, en el worktree)

Implementado por un agente en el worktree `wt15`; informe archivado en `dictamen_15/informe_bloque2.md`.
Archivos: `scripts/generar_readme.py`, las dos plantillas, `tests/test_readme.py` (10 → 19 tests),
`docs/readme/badges_congelados.json` (nuevo), y los dos README regenerados.

- **§90.3, sin contador vivo.** El generador ya no lee `data/backups/sello_dinero.csv` (función
  `contador_e0` y constante eliminadas; nadie más las usaba, grep en todo el repo). La viñeta de E0
  en inglés dice desde cuándo (2026-09-08, el mínimo de `fecha_insumo` del CSV, atado por test), qué
  exige contar (la definición de §57, contrastada con `sello_dinero.py:555-571`), y remite al CSV
  versionado. **La mención a `/salud` que el acta §90.3 pide se QUITÓ: `/salud` no muestra el riel
  de dinero** (`api/main.py:348-420`, `frontend/src/vistas/Salud.tsx`); lo muestra la vista `/sellos`
  (`api/main.py:1352`, `SellosDinero.tsx`). Manda la máquina; apuntar a `/sellos` no está firmado y va
  como errata del acta y decisión de Nicolás. Un test exige que el generador no abra el CSV.
- **§90.4, badges congelados.** `docs/readme/badges_congelados.json` con `tests_recolectados`,
  `plataforma_version` y `leido_el`; el generador los rinde DENTRO del badge, idéntico en los dos
  idiomas (`tests-<N>%20recolectados%20al%20<fecha con guiones dobles>`), sin prosa nueva en
  español. «passing» pasó a «recolectados» porque N sale de `--collect-only` y cuenta saltados y
  xfail. Ningún test exige que N o la versión sean los vivos. **N se relee al cierre**, con todos los
  tests nuevos en el árbol real (sección 9).
- **§88.5.** 352/358 → marcadores leídos como texto de `backtest/veredicto_51.py` (hoy 354 y 360;
  el generador revienta si el literal no está). El «59×» → `{{larga_veces}}` = cociente entero de
  los dos n del árbitro (hoy 14.618 / 238 → 61): el dictamen 13 define un único valor correcto.
- Verificado: `--verificar` exit 0; 19 tests en verde; 23 contrapruebas (fuera del worktree) en
  verde; los vigilantes de `cifras.py` no chocan. La desincronización previa de `README.md` vivía
  íntegra en la viñeta reemplazada. Ninguna otra línea cambia en ningún README.
- **Lo que el README afirma y hoy no se verificó, listado y no tocado:** E1 «No practice account
  and no gateway exist yet» (el acta §91.9 dice usuario de práctica por activar); E0 «every trading
  night» (la sesión del 25-sep no tiene filas); `GEMELO/resultados/tesis.md:161` sigue diciendo «59×».

---

## 4. Bloque 4: `mki_backup.py` no se le adelanta al sello (22:32 – 23:12, en el worktree)

Implementado por un agente; informe archivado en `dictamen_15/informe_bloque4.md`. Archivos:
`mki_backup.py` (+157 líneas), `tests/test_backup_orden.py` (nuevo, 49 funciones, 83 casos al
entregar), y después dos toques del orquestador.

- **Test de reproducción, rojo en HEAD por la razón correcta** (22:32:49): con reloj a las 14:42 del
  28-sep y sin sello, HEAD hace `add`, `diff` y `commit`. Verde con el cambio (22:33:47).
- **La decisión es una función pura** (`decidir_commit(ahora_local, snapshot_sellado_hoy,
  snapshot_vivo)`), la base se lee en `mode=ro` sin importar `senales` (su `init_db()` hace DDL), el
  proceso se detecta con `pgrep -f snapshot.py` sin importar `mki_vigia`, negarse no toca el índice y
  sale con 0. El criterio para esperar un snapshot es **lunes a viernes en la fecha local**, no «día
  hábil de NYSE»: el riel sella en feriado de NYSE (hay snapshot del 7-sep, Labor Day). Un test lee
  `systemd/mki-snapshot.timer` y exige que la constante `HORA_SNAPSHOT_LOCAL` (18:15) coincida.
  14 de 14 mutantes muertos; el archivo pasa con `TZ=Pacific/Honolulu` y `TZ=Pacific/Kiritimati`.
- **Dos toques del orquestador después del informe (23:12), con sus tests:** (1) el implementador
  encontró que la rama «sellado → commitea» dejaba una carrera de 32 s (el 28-sep: emisión 14:42:58,
  proceso terminado 14:43:30; los CSV se exportan DESPUÉS del sello): se agregó la **regla 0**, con
  `snapshot.py` vivo nunca se commitea, sea el día que sea; absorbe la rama 4 y cubre también el fin
  de semana. (2) `tests/test_sombra.py::test_backup_de_titular_si_intenta_commitear` quedaba atado al
  reloj real (rojo de lunes a viernes antes de las 18:15): se fijó el caso normal de las 18:40 con
  tres `monkeypatch`, como propuso el implementador. `test_backup_orden.py` + `test_sombra.py`:
  **121 en verde**, con el reloj de Chile y con el de Honolulu.
- **Elección de agente que el acta no da, a tarjeta:** la rama 5 (día de semana, sin sello, pasadas
  las 18:15, sin proceso vivo) **commitea igual** y lo dice en el log con el prefijo «DÍA SIN SELLO»
  (`COMMITEAR_DIA_SIN_SELLO = True`, una constante con test en las dos posiciones). Y la rama 1 (fin
  de semana) commitea. Los dos costos están en la tarjeta.

---

## 5. Bloque 5: el inventario de los ocho jobs (22:11 – 23:09, sólo lectura)

Redactado por un agente como borrador de tarjeta; integrado en `espera_firma.md` como tarjeta nueva
con §63 marcada FUNDIDA (sección 7 de esta bitácora). Lo que el inventario midió y las corridas
anteriores no tenían:

- **Los ocho arrancaron en 59 ms, en orden alfabético de unidad** (n = 1). `mki-vigia-rechequeo`
  terminó primero (14:42:53.303) y el backup segundo (14:42:53.790): la bitácora 14 y el acta §89.6
  dicen «backup terminó primero»; fue el primero de los que escriben. Errata menor para el acta.
- **Telegram el 28-sep: cuatro mensajes, tres fuera de hora en 11 s** (alerta, reporte, retractación);
  la bitácora 14 dice «dos».
- **El commit `5321f6b` sostuvo el «OK backup» del vigía de las 14:42:55**, y no contenía nada del 28.
- **`mki-noticias` no analiza nada desde el 7-sep** (tarjeta §74; `data/noticias.log` y
  `data/costos_ia.log`).
- **La suspensión, por otra vía:** `CLOCK_MONOTONIC = CLOCK_BOOTTIME` = 551.798,7 s contra 850.910 s de
  pared desde el arranque del 20-sep: 3 d 11 h 05 min que ningún reloj del invitado contó, y una sola
  pausa terminada a las 14:42:52 del 28 habría empezado a las 03:37 del 25. Coincide con el latido del
  journal del sistema (0.10) al minuto. Que fue el host quien la pausó sigue siendo testimonio.
- **Novena fila:** el orden del journal apunta a la recarga y no al reinicio (anexo 1 de la regla).
- El censo del journal desde el 24-ago: 212 arranques de `mki-*`, 10 fuera de calendario (los 8 del
  28-sep, la sonda del 29, y uno de `mki-vigia-rechequeo` el 25-ago 19:34:41, no investigado).

---

## 2. Bloque 1: la regla de conocibilidad en el riel de medición (22:11 – aplicación)

Implementado por un agente en el worktree `wt15`; informe archivado en `dictamen_15/informe_bloque1.md`
(con la tabla de las 33 filas del ancla, el censo de consumidores y los siete hallazgos). Dictamen del
`auditor-lookahead` en `dictamen_15/auditor_bloque1.md`.

### 2.1 Qué se hizo, en una línea por punto

- **1.1 (a)** `senales.py::verificar_apertura_pendientes()` compara `available_at` y `timestamp_utc`
  como instantes con zona; si el primero es posterior, la fila `pendiente` pasa a
  `no_verificable_timing`, se cuenta en `no_verificables` y se imprime un `AVISO verificador`; NULL e
  igualdad no disparan; el test de reproducción falla en HEAD por la razón correcta; el test de corte de
  método vuelca las filas del 28-sep antes y después del verificador nuevo sobre una copia: idénticas.
- **1.2 (b)** `snapshot.py::ejecutar_snapshot()` devuelve `{'snapshot': False, 'motivo': …}` si
  `available_at > ahora_utc`, con margen cero; el motivo no entra al bucle de reintentos; la rama del
  `except` sigue sellando; 251 sesiones de 2026 barridas: con margen cero nunca frena, con 2 h frenaría
  142. **Hallazgo H0, a tarjeta §72:** una fuente atrasada (`sox_fecha` de la sesión anterior) pasa la
  guarda y sella; la consecuencia que el acta §90.1 (b) anuncia no la produce esta guarda.
- **1.3 (d)** `backtest/linea_base.py`: `sin_conocibilidad()`, `excluir_sin_conocibilidad()`,
  `filas_sin_conocibilidad()`, `auditar_conocibilidad()`, `CONOCIBILIDAD_OFICIAL = True`; `cargar()`
  la aplica ANTES de deduplicar y también las betas de `salud_r2_regimen_beta`; el informe la declara.
  Alcanza hoy 24 filas, 1 fecha, 8 con verificación; ninguna cifra publicada cambia (árbitro volcado
  antes y después: idéntico). **Censo, a tarjeta §73:** las métricas de `senales.py` que sirven al
  dashboard, la API y el Telegram no pasan por la exclusión, y `verificar_puntaje_pendientes` no tiene
  guarda.
- **1.4 (§90.2) DETENIDO.** Las dos anclas difieren en 33 filas de 5 fechas (tabla en el informe): la
  línea 163 no se tocó, como mandaba el encargo. Tarjeta §71.
- **1.5** el vigía va a tarjeta §67 (dictamen del director); los tres ejes ciegos quedaron escritos en
  el informe y en la tarjeta.
- **H1** `tests/test_autonomia.py` ganó un reloj fijo en su fixture (18 líneas aditivas): con la
  guarda (b), su frame sintético que termina hoy dejaba tres tests dependientes de la hora.

### 2.2 Suite completa en el worktree, con los bloques 1, 2 y 4 juntos

Lanzada a las **23:12:51**, terminada a las **23:19:45**: **1019 passed, 5 skipped, 1 xfailed, 0
failed** en 412,97 s. Recolectados 1025 (904 de HEAD más los tests nuevos de los tres bloques). Los
dos rojos de `test_readme.py` desaparecieron
con el bloque 2. El worktree tiene el CSV de la sonda de HEAD: ninguna fila de madrugada.

### 2.3 Dictamen del auditor y aplicación al árbol real

- **23:17:32** (hora del agente) `auditor-lookahead`: **APLICABLE CON EXIGENCIAS**
  (`dictamen_15/auditor_bloque1.md`). Las cuatro bloqueantes son de texto, no de código: B1 (no se
  puede escribir que la fuga quedó cerrada: hoy 8 de las 160 filas de la ventana de 30 días de
  `metricas_apertura` son las invertidas, y las muestran Telegram, dashboard y API), B2
  (`verificar_puntaje_pendientes` no aplica ni la regla maestra ni la de conocibilidad y escribirá las
  24 filas desde el ~5-oct: decisión de Nicolás, tarjeta §73), B3 (precisión fechada al §90.1 b, en el
  acta §92), B4 (la premisa del §90.2 en el encargo es falsa: contraejemplo `005930.KS` del 29-jul con
  `available_at <= emisión` y la sesión del ancla ya abierta; tarjeta §71). R2 (barrido de husos
  clavado a 2026) se aplicó al test antes de aplicar: 28 en verde a las 23:21:59. R1, R3, R4 y R5 van a
  las tarjetas §67, §72 y a esta bitácora (las reproducciones que fallan en HEAD por su propia aserción
  son 7 de los 12 rojos; los otros 5 fallan porque la API nueva no existe en HEAD).
- **APLICACIÓN AL ÁRBOL REAL: 2026-09-29 23:22:17 de Chile.** Copia de los quince archivos del
  worktree (`senales.py`, `snapshot.py`, `backtest/linea_base.py`, `mki_backup.py`,
  `scripts/generar_readme.py`, las dos plantillas, `badges_congelados.json`, `tests/test_readme.py`,
  `tests/test_autonomia.py`, `tests/test_sombra.py`, `tests/test_backup_orden.py`,
  `tests/test_conocibilidad.py`, `README.md`, `README.es.md`); el `git diff` de los cuatro módulos de
  código es idéntico en el worktree y en el árbol real (`diff` vacío). Fuera del tramo 00:15 a 00:50; el
  siguiente job que importa alguno de estos archivos es `mki-snapshot` a las 18:15 del 30-sep; el
  sellador y la sonda no los importan (0.5). **Éste es el corte de método del acta §90.1 (a), (b) y
  (d): rige para lo sellado desde el 30-sep-2026.** Huellas de las tres bases antes y después de la
  copia: idénticas (`12fe11ec…`, `5c8b9f8d…`, `462c45db…`).
- Suite completa en el árbol real lanzada a las 23:22 (sección 9).

---

## 7. Bloque 3: la política de retención y el parche NO APLICADO de §62 (22:32 – 23:23)

- **La política primero** (`GEMELO/propuestas/parches/politica_evidencia_no_verificable.md`, escrita por el
  orquestador a las 22:32 con el código del sellador leído y antes de cualquier línea de parche). Su
  hallazgo: **la opción (a) del acta §90.6 no se puede implementar como está firmada**, porque
  `sellos_dinero` declara `UNIQUE (fecha_insumo, ticker, juego)` y las filas no verificables y las buenas
  de una misma fecha no pueden convivir. Dos caminos, M (migrar el esquema, reescribe la tabla) y T (tabla
  aparte, aditiva); la política manda T y deja la elección al acta. Tamaños medidos: 6,7 a 9,8 KB por
  extensión, 7,1 KB por meta (**Error propio 3.** La primera versión de la política escribió esos
  tamaños estimados, sin medir; se midieron a las 22:32 y se corrigieron en su sitio); retención permanente; respaldo por `respaldar_extension` y `exportar_csv`.
- **El parche después**, por un agente en un segundo worktree (`wt15_b3`, copias de las bases), retomado
  a las 23:01 tras el corte de cuota: `sello_no_verificable.diff` (1.250 líneas) y `sello_no_verificable.md`
  en `GEMELO/propuestas/parches/`. Test de reproducción del 28-sep rojo en HEAD por su propia aserción
  (23:09: «el disparo bueno de las 23:30 NY no selló porque la fecha quedó ocupada por el intento
  intradía, resultado='divergencia_registrada'»); 50 tests del sellador en verde a las 23:22 (118 con los
  vecinos `test_dinero`, `test_sonda_cierre`, `test_frontend_estatus`). `git apply --check` limpio
  contra HEAD. **`dinero/sello_dinero.py` del árbol real: sha256 `480fbdc9…`, idéntico a HEAD, verificado
  por el orquestador a las 23:25.** El sellador real no se ejecutó.
- Cuatro decisiones del implementador dentro de T (rechazo de la evidencia canónica con timing roto al
  sellar; divergencia también con el mismo sha; dos relojes; `VERSION_SELLO` E0.3) declaradas en la tarjeta
  §75 para el acta que lo aplique. Dictamen del `auditor-lookahead` lanzado a las 23:25 (sección 7.1).

---

## 8. Bookkeeping (23:30 – 23:33)

- **23:29:33** suite completa en el árbol real después de aplicar los bloques 1, 2 y 4: **1019 passed, 5
  skipped, 1 xfailed, 0 failed** en 419,49 s; `tests/test_motor.py` sin contaminación. Huellas de las
  bases sin cambio.
- **23:30:07** N releído en el árbol real con todos los tests nuevos: `pytest tests/ --collect-only -q` =
  **1025**; `PLATAFORMA_VERSION` 5.1.0; fecha 2026-09-29. `docs/readme/badges_congelados.json` actualizado
  con los tres valores juntos (932 → 1025, misma versión, misma fecha) y los dos README regenerados
  (**23:30:25**, segunda y última aplicación al árbol real de esta corrida); `--verificar` exit 0;
  `tests/test_readme.py` 19 en verde. Los badges dicen «1025 recolectados al 2026-09-29» y «5.1.0 al
  2026-09-29».
- **23:30:40** `cola_decisiones.md`: «897» reemplazado por 1025 con errata fechada al lado (deuda (1) del
  acta §91.4), sección «Qué movió la decimoquinta corrida» insertada, fecha de actualización.
- **23:31:19** `estado_epistemico.md`: encabezado al 30-sep y bloque de la corrida 15 sólo con lo
  dictaminado (la regla de §58, el bloque 1, el ancla, el parche); el «17» de `roca_chip` queda
  CONTESTADO como artefacto y el 39 releído se declara DESCRIPTIVO sin dictamen, no como cifra.
- **23:32:49** `ESTADO.md` regenerado, 50 líneas, con el crédito de la API y `verificacion_puntaje` (5-oct)
  al tope.
- `espera_firma.md`: §61 FIRMADA, §62 FIRMADA EN PARTE, §63 FUNDIDA en la 66, §64 FIRMADA, §65 FIRMADA, §58
  con la línea del sello; tarjetas nuevas §66 (inventario), §67 (vigía), §68 (8035.T), §69 (skill `gate`),
  §70 (backup), §71 (ancla), §72 (guarda b), §73 (métricas vivas y `verificacion_puntaje`), §74 (crédito
  de la API), §75 (política y parche de §62), §76 (README). Los textos anteriores no se borraron.

### 7.1 Dictamen del auditor sobre el parche, y lo que se plegó

- **23:35** (hora del agente) `auditor-lookahead`: **APLICABLE CON EXIGENCIAS**
  (`dictamen_15/auditor_parche_sello.md`). 91 tests en verde en el worktree sin ningún salto; el
  arnés `test_parches_en_worktree.py` en verde para el diff; sonda adversaria propia (intradía → noche
  → tercer disparo tardío; disparadores; cero filas rotas en la principal). Ninguna fuga temporal.
  Dos fugas de auditabilidad: **F1 (bloqueante)**, la rama de rechazo de la evidencia canónica con
  timing roto no dejaba fila en ninguna tabla; **F2**, un `.no_verificable.csv` congelado por un
  proceso que murió antes de sellar queda citado por nadie. B2 (visibilidad del intento fuera del
  log: `estado()`, API y `CONTRATO.md`) y B3 (el acta escribe que sustituye el mecanismo de §90.6 a)
  quedan para el acta que aplique.
- **23:38** el implementador del bloque 3 retomado para plegar B1, R2, R3, R4 y R5 al mismo diff con
  plazo de tests a las 00:03; la política se enmendó en §2.4 (`ya_intentada` con el mismo sha; el
  caso de B1 y su rastro). Resultado en 7.2.

### 7.2 Las cinco exigencias plegadas

- **23:42:02** (hora del agente) B1, R2, R3, R4 y R5 plegadas al mismo diff: `tests/test_sello_dinero.py`
  + `tests/test_dinero.py` **89 passed, 2 skipped** (los dos saltos son la R2: la copia de la base real
  todavía no tiene la tabla de intentos, declarado). `sello_no_verificable.diff` regenerado (1.323
  líneas, sólo `dinero/sello_dinero.py` y `tests/test_sello_dinero.py`); `git apply --check` limpio
  contra HEAD, verificado también por el orquestador contra el árbol real; `.md` con la sección
  «Exigencias del auditor plegadas». `dinero/sello_dinero.py` del árbol real: sha256 `480fbdc9…`,
  intacto. B2 y B3 quedan para el acta que aplique (tarjeta §75).

---

## 9. Cierre (23:43 del 29-sep – mañana del 30-sep)

### 9.1 Segundo corte de cuota, y la noche sin nadie

- **23:43:42** acta §92 anexada al final de `DECISIONES.md` con cuatro huecos marcados para el
  cierre (suite final, lectura de madrugada, timers, resultado). **23:44** `curador-epistemico` y
  `director-programa` lanzados sobre los textos de cierre.
- **~23:50** **segundo corte de cuota de la API** («session limit, resets 4am»): los dos agentes
  murieron al arrancar y la sesión del orquestador quedó detenida. **10:30:48 del 30-sep** la sesión
  volvió; los dos agentes se retomaron con su contexto (`SendMessage`) y la suite de cierre se lanzó
  a las 10:31. La corrida no llegó a la ventana de las 17:50 y no aplicó nada al árbol real después
  de las 23:30:25 del 29 (sección 8).
- **La noche, medida al volver (punto 8 de las reglas de la noche):** el latido del journal del
  sistema (0.10) no tiene ningún hueco mayor que 2 minutos entre las 21:57 del 29 y las 10:31 del 30
  (1.509 latidos): la máquina no se suspendió. La sonda disparó a su hora las 14 veces que le
  tocaban desde el arranque de la corrida (22:05, 22:35, 23:05, 23:35, 00:05, 00:35 y las ocho de
  madrugada 01:05 a 04:35), 0 fallos; **la franja de madrugada existe desde esta noche**. El
  sellador disparó a las 00:30:00 y terminó a las 00:30:04: selló la sesión del 29-sep como
  `insumo_incompleto`, `cuenta_para_N = 0` (leído de `data/sello_dinero.log`, no de la sonda; qué
  tickers faltaban no se miró). `dinero/sello_dinero.db` cambió a las 00:30:04 por ese sello
  (sha256 `751cca2ab8c9b3ba…`); `senales.db` y `noticias.db` conservan las huellas de apertura
  (`12fe11ec…`, `5c8b9f8d…`; mtimes 18:15:30 y 17:52:09 del 29). Ninguna fila de madrugada fue
  leída por ningún agente en toda la corrida, tampoco al volver.

### 9.2 Suite de cierre y dictámenes de cierre

- **10:31:27 → 10:38:25** suite de cierre en el árbol real, **con las filas de madrugada ya en
  `data/sonda_cierre.csv`**: salida escrita a archivo y filtrada a nombres de tests fallidos y
  totales (regla de 0.6): **1019 passed, 5 skipped, 1 xfailed, 0 failed** en 410,63 s;
  `tests/test_motor.py` sin contaminación. Ningún rojo, así que no hubo nada que clasificar bajo
  §91.6 ni ninguna fila de madrugada que mirar: `test_la_regla_nueva_reproduce_el_sesion_ny_de_todas_las_filas_ya_escritas`
  pasó sobre las primeras filas de madrugada de la historia sin que ningún agente las leyera.
- **~10:34** `director-programa` (retomado): **ADELANTE con cinco exigencias**
  (`dictamen_15/director_cierre.md`): llenar los huecos del acta con lecturas de máquina, declarar
  qué se leyó de la suite de cierre, huellas al cerrar, la regla 0 del backup como tercera elección
  con su costo medido (aplicada en §70: 6 días de sello posterior a las 18:40 en la historia, todos
  de la era del Mac, en que la regla 0 habría dejado el día sin commit), y §91.6 si la suite no daba
  0 rojos. Recomendó fundir §74, §69, §72 y §70 (anotado en la cabecera de §66 para la firma) y
  puso el «nivel 1» de mañana: el sello de las 18:15 es la primera prueba viva de la guarda (b), y
  no lanzar la corrida 16 esta noche. Aplicado en `ESTADO.md`.
- **10:34:54** `curador-epistemico` (retomado): **RECHAZADO, cuatro bloqueantes**, todas de texto,
  todas aplicadas (`dictamen_15/curador_cierre.md`): (1) el README decía «every trading night» y la
  máquina no sella todas las noches (**Error propio 5.** El informe del bloque 2 ya había señalado esa
  frase como no sostenida y el orquestador la dejó pasar al regenerar) (la sesión del 25 sin filas, la del 28 fuera de hora): la viñeta
  de E0 dice ahora «on NYSE trading nights … nights get missed … and a missed night is never
  recovered», sin fechas para que no se venza sola; (2) E1 decía «No practice account … exist yet»
  y el acta §91.9 dice usuario de práctica por activar: corregido citando el acta; (3) los errores
  propios 2, 3 y 4 del acta 92.12 no estaban marcados en la bitácora: marcados en 0.10, 7 y 1.2;
  (4) dos «DEMOSTRADO» del estado epistémico pasaron a «MEDIDO y APLICADO» y «MEDIDO por censo». Y
  las recomendadas: «pausada» → «no corrió … que fuera suspensión es INFERENCIA», la holgura de 15
  min con sus fechas (2-nov-2026 a 12-mar-2027), la suite con hora, la predicción de mañana
  rotulada, los pendientes de noticias con su medida (260 → 3.672), la referencia rota a «6.5», y
  el título de la ventana larga con su denominador a la vista («61× la muestra sellada (14.618 /
  238)» en los dos idiomas; el test del cociente se ajustó). README regenerado a las **10:39:01**
  (tercera y última aplicación al árbol real, sólo documentos); `--verificar` exit 0;
  `test_readme`, `test_epistemico` y `test_cifras_arbitro`: 46 en verde. Suite completa relanzada
  a las 10:39 (resultado en 9.3).

### 9.3 Suite definitiva, huellas, secretos, y lo que queda

- **10:40:06 → 10:47:04** suite definitiva en el árbol real, con las frases del curador ya en el
  README: **1019 passed, 5 skipped, 1 xfailed, 0 failed** en 405,29 s; `tests/test_motor.py` sin
  contaminación. Salida leída sólo como nombres y totales (0.6). Recolectados: 1025.
- **Huellas al cerrar (10:47:14):** `senales.db` `12fe11ec9e232fef…` y `noticias.db`
  `5c8b9f8df422cdef…`, idénticas a las de apertura (0.7); `dinero/sello_dinero.db`
  `751cca2ab8c9b3ba…`, movida a las 00:30:04 del 30-sep por su timer (9.1). Esta corrida no escribió
  en ninguna base.
- **Escaneo de secretos** con los patrones exactos del hook de pre-commit sobre el diff completo y los
  archivos nuevos: 0. **Sin push.**
- **Qué tocó la corrida en el árbol real** (`git status`): `senales.py`, `snapshot.py`,
  `backtest/linea_base.py`, `mki_backup.py`, `scripts/generar_readme.py`, las dos plantillas del
  README, los dos README, `docs/readme/badges_congelados.json` (nuevo), `tests/test_conocibilidad.py`
  y `tests/test_backup_orden.py` (nuevos), `tests/test_readme.py`, `tests/test_autonomia.py`,
  `tests/test_sombra.py`, `.claude/skills/cierre-sesion/SKILL.md`, `DECISIONES.md` (acta §92),
  `ESTADO.md`, `GEMELO/resultados/{bitacora_15,espera_firma,cola_decisiones,estado_epistemico}.md`,
  `GEMELO/resultados/dictamen_15/` (nueva), `GEMELO/propuestas/regla_58.md` y su anexo,
  `GEMELO/propuestas/parches/{politica_evidencia_no_verificable.md,sello_no_verificable.diff,sello_no_verificable.md}`,
  `GEMELO/propuestas/skills/gate_gate_de_entorno.md`. **Y lo que tocaron los timers, no la corrida:**
  `data/sonda_cierre.csv` (la sonda), `data/backups/sello_dinero.csv` y
  `data/backups/sello_dinero_ext/ext_2026-09-29.*` (el sellador de las 00:30; los commitea el backup de
  las 18:40). **No tocó:** `motor.py`, `universo.py`, `calendarios.py`, `mki_vigia.py`,
  `dinero/sello_dinero.py` (sha256 `480fbdc9…`), la sonda, ninguna unidad de systemd, `.env`,
  `corredor/`.
- **Lo que quedó abierto** está en el acta §92.13 y en `ESTADO.md`: la firma de la regla de §58,
  las tarjetas §66 a §76 (con la fusión que recomienda el director), el crédito de la API (§74),
  la decisión sobre `verificacion_puntaje` antes del ~5-oct (§73), y el sello de hoy a las 18:15
  como primera prueba viva de la guarda (b). Los dos worktrees de la corrida se retiran al final
  (9.4). El bloque 6.6 (`bifurcaciones`) no se empezó, como el encargo preveía.

### 9.4 Worktrees retirados y guardián

- **10:47:52** `git worktree remove --force` de `wt15` y `wt15_b3` y `git worktree prune`:
  `git worktree list` vuelve a mostrar sólo el árbol real en `main`; `GEMELO/cache` del árbol real
  (que los worktrees enlazaban) intacto. Los diffs de los dos quedan en el árbol real (aplicado el
  primero; `sello_no_verificable.diff` el segundo) y las evidencias en `dictamen_15/evidencia/`.
- **10:48** `guardian-constitucion` lanzado sobre el diff completo, después del último `Write` de
  contenido; su encargo se armó con el `git status` del momento (regla que dejó el error 6 de la
  bitácora 14). Su dictamen y lo que se hizo con él, en 9.5.

### 9.5 Dictamen del guardián, y el último toque

- **10:56:11** (hora del agente) `guardian-constitucion`: **APROBADO CON EXIGENCIAS (1)**, que en su
  vocabulario es OBSERVADO y sale con la exigencia aplicada (`dictamen_15/guardian_cierre.md`). Catorce
  reglas en verde con cita, medidas por él: `motor.py` y `universo.py` intocados y sin import nuevo;
  aislamiento GEMELO ↔ sellado por grep; el único `UPDATE` nuevo idéntico al de la regla maestra y sobre
  filas `pendiente`; las 24 filas del 28-sep con su estado (16 NULL + 8 `verificada`, consultado en
  `mode=ro`); cero verbos de publicación de git en 2.480 líneas de diff; HEAD sin mover; `main`; cero
  secretos; 0 reintroducciones de cifras retiradas en todo lo que el diff toca (54 preexistentes en
  actas viejas, inventariadas, ninguna tocada); `n = 238` sin mover y las cuatro cifras movidas con
  firma; `--verificar` exit 0; `dinero/sello_dinero.py` con sha256 de HEAD; los dos sellos de la regla
  verificados por hash y hora; ninguna unidad de systemd. Corrió él mismo `test_epistemico.py` y
  `test_razones_xfail.py` después del último Write de contenido (21 passed, 1 skipped, 1 xfailed).
- **La exigencia:** la última frase del acta §92.4 («Ningún contenido nuevo en español») quedó
  falsa al aplicar la recomendada 11 del curador (el título de la ventana larga cambió en los dos
  idiomas). **Aplicada a las 10:57** con el texto exacto del guardián. Es la única edición posterior
  al dictamen, más esta sección y la nota en el acta.
- **Lectura del guardián que declara para Nicolás (R13):** los cambios aplicados a `snapshot.py` y
  `senales.py` no son «un parche» en el sentido de la regla 13 sino la ejecución directa de la firma
  §90.1 con auditor y test rojo en HEAD; si Nicolás prefiere la lectura literal (cualquier línea
  aplicada a esos archivos es rechazo), el diff es rechazado y la corrida 16 va a encontrar la misma
  pregunta.
- **Lo que el guardián no pudo verificar:** las dos suites de la noche las tomó de sus archivos por
  nombre y tamaño; el cuerpo sellado de la regla y el parche los verificó por hash y alcance, no
  afirmación por afirmación (eso es de los dictámenes archivados); las filas de la sonda y del
  sellador no las leyó; y la conducta real de hoy a las 18:15, 18:40 y 19:00, que ningún test puede
  dar: **el diff rige hoy aunque no se commitee**, porque está en el árbol de trabajo que los timers
  ejecutan.

**Cierre de la bitácora: 10:57 del 30-sep-2026.** Sin push. El commit es de Nicolás, con el diff a
la vista; el hook de pre-commit corre la suite (la última: 1019 en verde, 0 rojos) y el escaneo de
secretos (0), así que no hace falta `SKIP_TESTS`.
