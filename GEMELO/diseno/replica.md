# Diseño de la réplica permanente — de instrumento de transición a mecanismo

**Frente 2e · corrida 09 · escrito la madrugada del 3-sep-2026** (hora de
inicio de la sesión leída con `TZ=America/Santiago date`: mié 2-sep-2026
23:52 -04). **Documento de diseño: no escribe código, no activa nada.**
Convierte lo que hoy es el modo sombra de la Etapa 5.0.3 —pensado para una
ventana de tres noches y un switch— en un mecanismo que corra todos los
días sin fecha de corte.

**Cómo leer las marcas.** Cada afirmación lleva una de tres:

- **MEDIDO** — se leyó de un archivo del repo o de la máquina esta noche,
  con la fuente entre paréntesis. Nada de memoria.
- **PROPUESTA** — diseño nuevo de este documento. No existe, no está
  decidido, no se implementa sin firma.
- **DECISIÓN PENDIENTE** — algo que sólo Nicolás puede cerrar. Las lista
  la §8, numeradas.

**Estado real esta noche, verificado y no deducido** (skill `modo-emision`:
al modo se le pregunta, no se deduce):

- Esta máquina (PC/WSL) es el **titular**. MEDIDO: `python -c "import modo;
  print(modo.modo_actual())"` → `titular`; `modo.descripcion()` → «modo:
  TITULAR — Telegram y commits activos». (El `grep -c MKI_MODO .env` que
  pedía el encargo fue **denegado por permisos** en esta sesión; la
  respuesta canónica es la de `modo.py`, que es lo que la skill exige.)
- Los seis timers están instalados y dispararon hoy. MEDIDO: `systemctl
  --user list-timers --all` lista `mki-noticias` 17:50, `mki-snapshot`
  18:15, `mki-reporte` 18:25, `mki-backup` 18:40, `mki-vigia` 19:00,
  `mki-vigia-rechequeo` 20:30 (America/Santiago), todos con LAST =
  2026-09-02.
- El Mac quedó fuera del rol de emisor. MEDIDO: skill `modo-emision`, «El
  switch está completo. El PC Windows/WSL es el titular […] El Mac quedó
  fuera».
- La réplica **no está activada**. MEDIDO: `replica.py` cabecera («No corre
  sola: nadie la invoca todavía (ni timer, ni cron, ni `mki`)»);
  `docs/RUNBOOK_REPLICA.md` §6 («hoy no existe un timer ni un cron que
  invoque el paso 5»); `GEMELO/resultados/replica_una_pagina.md` («Nada de
  esto está activado»).
- Hay una decisión bloqueante abierta: quién gana ante divergencia.
  MEDIDO: `GEMELO/resultados/espera_firma.md` §4 (líneas 341-380) y
  `cola_decisiones.md` §1 (líneas 65-96); ambos recomiendan la opción A
  marcada como recomendación, no como decisión.

**Errata de encargo, declarada.** El encargo cita la skill
`switch-titular` en `.claude/skills/switch-titular/SKILL.md`. MEDIDO: ese
archivo **no existe** (`ls` → «No such file or directory»; `.claude/skills/`
contiene `acta-decision`, `cierre-sesion`, `cifras-canonicas`,
`estadistica-evaluacion`, `gate`, `modo-emision`). El orden del switch vive
en `.claude/skills/modo-emision/SKILL.md`, sección «El orden del switch,
como referencia histórica», y en el checklist de `docs/SOMBRA.md`. La §4 de
este documento se apoya en esas dos fuentes. No edité ninguna.

---

## 1. Objetivo y no-objetivos

### 1.1 Qué garantiza la réplica (PROPUESTA, sobre piezas MEDIDAS)

1. **Que exista una segunda cadena de sellos, independiente, para cada
   fecha hábil**, producida por otra máquina que corre el mismo commit
   sobre su propia base. MEDIDO que la pieza existe: en sombra
   «snapshot.py sella normalmente. Si la sombra no sellara no habría nada
   que comparar» (`modo.py` cabecera, «QUÉ NO CAMBIA»).
2. **Que cada fecha reciba un veredicto de comparación** entre lo que selló
   la titular y lo que selló la réplica, con vocabulario ya probado.
   MEDIDO: los cuatro veredictos son constantes en `comparar_sombra.py`
   líneas 119-122 (`PARIDAD`, `DIVERGENCIA`, `DIA_NO_COMPUTABLE`,
   `PENDIENTE_PUBLICACION`); ejercitados sobre 8 fechas sintéticas con
   cero divergencias falsas (`data/replica_ensayo/reporte_ensayo.md`,
   corrida `2026-08-31T19:13:22.862021+00:00`: 8 fechas, 7 filas de
   divergencia, `resuelto_como` NULL en todas).
3. **Que toda divergencia quede anotada como dato de auditoría**, con
   procedencia (campo, valor de cada lado, clase insumos/cómputo/
   existencia). MEDIDO: tabla `divergencias_replica` en `replica.py`,
   sólo INSERT (cabecera: «solo INSERT, nunca UPDATE ni DELETE»).
4. **Que una caída de la titular no deje el día sin sello en ninguna
   parte.** La réplica selló en su base; ese sello no es oficial (§1.2),
   pero existe, con `timestamp_utc` anterior a la apertura objetivo, y
   puede citarse como evidencia de qué habría emitido el modelo. Qué
   hacer con él es DECISIÓN PENDIENTE (§8, ítem 1: bajo la opción A, nada
   entra al track record por esa vía).
5. **Que la puesta en marcha de una máquina nueva sea reproducible desde
   el repo solo**: `scripts/restaurar_backup.py` reconstruye las bases
   desde `data/backups/*.csv` (§6).

### 1.2 Qué NO garantiza, y qué no hace nunca

- **No reescribe filas selladas.** Ni las suyas ni las de la titular. La
  comparación lee la titular por `git show origin/main:` y la local en
  `mode=ro` (MEDIDO: `comparar_sombra.py` `leer_csv_titular` y
  `leer_tabla_local`, líneas 172-190). El registro de divergencias es
  aditivo y no toca `senales.db` (MEDIDO: `replica.py`, «No escribe en
  `senales.db` ni en `noticias.db`»).
- **No emite Telegram.** En sombra, `alertas.enviar_mensaje()` —único punto
  de salida a la red— intercepta a `data/sombra_telegram.log` y devuelve
  `ok=True` a propósito (MEDIDO: `alertas.py` líneas 100-112 y `CLAUDE.md`
  §5.0.3 Fase 3).
- **No commitea ni pushea.** `mki_backup.py` retorna antes de `git add` en
  sombra (MEDIDO: `mki_backup.py` líneas 37-40) y jamás pushea en ningún
  modo (MEDIDO: línea 10, «Jamás push: publicar es un acto manual del
  usuario»).
- **No sella «oficialmente».** Sus filas no entran a `origin/main`, al
  README, al reporte ni a ninguna métrica. Lo oficial es lo que publicó la
  titular (§3).
- **No cubre la falla de la fuente.** Si Yahoo retira una sesión días
  después, la retira para las dos máquinas. MEDIDO:
  `replica_una_pagina.md`, tabla «Dos mecanismos distintos» y su corrección
  del 1-sep: la sesión del 2026-08-28 desapareció de la fuente para
  cualquiera que la mire; «La réplica no habría detectado esto». Ese
  riesgo es del segundo sello (`docs/SEGUNDO_SELLO.md`), otro mecanismo.
- **No decide quién tiene razón.** El registro anota, no arbitra (§3.4).
- **No corrige la titular en caliente.** Ninguna acción automática de la
  réplica cambia lo que la titular emite esa noche (§5 es la única
  excepción, y es al revés: una máquina se calla a sí misma, nunca
  altera a la otra).

---

## 2. Roles: titular y réplica

### 2.1 Cómo se declara (MEDIDO)

El rol vive en **un solo lugar**: `modo.py`, leyendo `MKI_MODO` del entorno
tras `load_dotenv()`.

```
MKI_MODO=sombra                → sombra (réplica)
MKI_MODO ausente               → titular
MKI_MODO puesto pero ilegible  → SOMBRA, con aviso ruidoso (nunca titular)
```

MEDIDO: `modo.modo_actual()` (líneas 53-60); `valor_crudo_invalido()`
para el aviso; `descripcion()` es la primera línea de `./mki estado`
(MEDIDO: `mki` líneas 41-45, «El modo va PRIMERO y solo»).

**Vocabulario.** PROPUESTA: el rol se llama «réplica» en los documentos y
sigue llamándose `sombra` en el código y en `MKI_MODO`. No se agrega un
tercer valor reconocido (`replica`) ni se renombra: los tres puntos de
intercepción (Telegram, backup, vigía) están probados bajo el nombre
`sombra` y un alias nuevo es una forma nueva de escribirlo mal. La falla
segura ya cubre el typo, pero no hay razón para gastarla.

### 2.2 Por qué nunca se deduce (MEDIDO)

El 30-ago se comprobó que deducir el modo da respuestas opuestas: la
variable no estaba ni en el shell ni en el `.env`, el acta 37.7 afirmaba
que seguía en `sombra`, y `modo.py` respondía `titular` (skill
`modo-emision`, «La regla, que se aprendió a golpes»; `DECISIONES.md` §37.7
es la afirmación desactualizada). La asimetría de la falla segura es lo
que hace fallar la intuición: **ausente = titular, ilegible = sombra**.
Regla operativa heredada tal cual: cuando un documento y la máquina no
coinciden, **manda la máquina** y la discrepancia se registra como errata
fechada.

### 2.3 Invariante: exactamente una titular (PROPUESTA)

**En todo instante hay exactamente una máquina cuyo `modo_actual()` es
`titular` y tiene timers activos.** Cero titulares es un hueco (se pierde
un día, se recupera al siguiente); dos titulares es el peor caso (Telegram
duplicado, dos cadenas de sellos, dos backups peleando por `main` —
MEDIDO: skill `modo-emision`, «Nunca solapado»). Por eso el orden del
switch prefiere el hueco (§4) y por eso hay detección del duplicado (§5).

**Qué hace cumplir el invariante hoy:** nada automático. Lo sostiene el
procedimiento (apagar antes de encender) y la asimetría de `modo.py`. La
§5 propone la primera verificación mecánica.

**Corolario:** la réplica **no es** un titular en espera que se activa
solo. Un failover automático rompería el invariante por construcción: dos
máquinas que deciden por su cuenta «la otra se cayó, ahora emito yo» son
dos titulares en cuanto la red parpadea. La promoción de la réplica es
siempre el switch de la §4, ejecutado por Nicolás.

---

## 3. Regla de desempate cuando dos máquinas sellan y difieren

### 3.1 Qué es «diferir» (MEDIDO)

`docs/REPLICA.md` §1 distingue tres clases, y `replica._clasificar` las
implementa:

| Clase | Qué pasó | Ejemplo real o ensayado |
|---|---|---|
| **insumos** | vieron datos de mercado distintos al sellar | `sox_fecha`, `descarga_ok`, `n_muestra` distintos (`replica.CAMPOS_INSUMOS`) |
| **cómputo** | mismos insumos, número distinto fuera de `1e-9` relativo | el único caso real: **0.0001 en el R² de `6857.T` el 27-ago**, atribuido a que el Mac descargó 31 min más tarde (`DECISIONES.md` §36.2) |
| **existencia** | una selló y la otra no, o conjuntos de tickers distintos | 28-ago: el Mac no selló (§36.1); ensayo 2026-09-04 y 2026-09-05 |

Los niveles de tolerancia están declarados antes de correr
(`comparar_sombra.py` líneas 59-117): nivel 1 identidad numérica relativa
`1e-9` sobre valores ya redondeados (así que 0.01 en `beta` **es** un
hallazgo), nivel 2 igualdad exacta, nivel 3 diferencia legítima esperada
(`plataforma_version`, `timestamp_utc`, `creado_en`, `origen`, `estado`,
noticias).

### 3.2 Las tres opciones y sus consecuencias (MEDIDO: `espera_firma.md` §4, tabla)

| Opción | Qué implica | Consecuencia |
|---|---|---|
| **A. La titular gana siempre, sin excepción** | La fila de la titular es la oficial pase lo que pase. La divergencia se registra y se investiga después, nunca en caliente. | Simple, auditable, **nunca reescribe una fila sellada**. Si la titular se equivoca, la réplica lo deja documentado pero no lo corrige sola. |
| **B. Gana la de mejor salud de descarga** | La fila oficial sale de la máquina cuyos tickers bajaron completos. | Puede corregir errores reales de datos. **Decide en caliente**: elegir la fila que se sella según un criterio evaluado ese mismo día es una puerta abierta a que el criterio se ajuste al resultado. |
| **C. Divergencia = no se sella ese día** | Ninguna de las dos filas entra al track record. | Máxima pureza, peor costo: **cada problema de la réplica se vuelve un agujero del track record de la titular**. Es darle a la réplica poder de veto sobre producción. |

Consecuencias adicionales que este documento agrega (PROPUESTA, no están
en la tabla original):

- **B necesita que la réplica sea capaz de emitir**, es decir que el modo
  se resuelva *después* de comparar. Eso mueve la decisión de rol de
  `modo.py` (declaración) a un cómputo nocturno (deducción): es
  exactamente lo que la §2.2 dice que se aprendió a no hacer. Además B
  falla en el caso más frecuente: cuando las dos descargan 28/28 y
  difieren igual (el caso del 27-ago), B no tiene respuesta y cae en A o
  en C.
- **C convierte el sello en condicional a un evento posterior** (la
  comparación, después de las 20:30). Contradice la regla maestra en su
  espíritu: la predicción se emite antes de la apertura objetivo y ya
  está en Telegram a las 18:25; «no se sella ese día» sólo puede
  significar «se retira después de emitida», que es un estado terminal
  nuevo, no un no-sello. Y le da a un `git fetch` fallido el poder de
  borrar un día.
- **A tiene un costo que hay que nombrar:** si la titular sella tarde o
  con descarga degradada y la réplica selló bien, la fila buena queda en
  auditoría y la mala en el track record. El proyecto ya vivió eso al
  revés (29-jul y 5-ago, sellos tardíos del Mac; `replica_una_pagina.md`
  cita el tramo de 4 fechas de incidente con n=28, 32.1% vs 82.1%,
  −50.0 pp, McNemar p=0.0066, y declara que con 4 clústeres de fecha el
  IC95 no es computable — se cita con esa reserva). A no lo evita; lo
  deja **documentado el mismo día**, que es más de lo que hay hoy.

### 3.3 Recomendación — PROPUESTA, no decisión

**A.** Es la única compatible con la Constitución 5.0 (3) tal como está
escrita, la única que no requiere deducir el rol, y la única que no cierra
puertas: B y C pueden adoptarse más adelante *con la evidencia que el
registro de A acumule*. Coincide con `docs/REPLICA.md` §2,
`replica_una_pagina.md` y `espera_firma.md` §4. Sigue siendo DECISIÓN
PENDIENTE (§8, ítem 1).

### 3.4 Cómo se registra sin arbitrar (MEDIDO + PROPUESTA)

MEDIDO: `replica.registrar_comparacion(res)` inserta una fila por hallazgo
de nivel 1/2 cuando el veredicto es `DIVERGENCIA`, cero filas en los otros
tres veredictos, una fila sintética `sello_ausente` cuando la réplica no
selló; `resuelto_como` queda **siempre NULL** («la regla del §2 de
REPLICA.md es una PROPUESTA razonada, no una decisión adoptada. Fijar ese
valor acá sería implementar el §2 como si ya estuviera resuelto»).

PROPUESTA: **aun con A firmada, `resuelto_como` sigue en NULL.** Bajo A la
resolución no es un dato por fila, es una regla estructural: lo oficial es
lo que está en `origin/main`, y la réplica nunca escribe ahí. Escribir
`'titular'` en cada fila sería redundante y, peor, crearía el hábito de
leer esa columna como si pudiera decir otra cosa. La columna se conserva
por si algún día se adopta B o C (entonces sí tendría contenido), y el
runbook ya lo dice así (`docs/RUNBOOK_REPLICA.md`, «Qué NO hace este
runbook»: «`resuelto_como` queda en NULL siempre […] la regla se aplica en
el reporte y en la operación, no reescribiendo la auditoría»).

Lo que sí agrega el registro permanente (PROPUESTA):

- **Una fila por comparación, no sólo por divergencia.** Hoy `PARIDAD`
  deja cero filas; en régimen permanente eso vuelve invisible el
  denominador («¿cuántos días se compararon?»). Propuesta: una tabla
  hermana `comparaciones_replica(fecha, veredicto, rev_titular, hostname,
  detectado_en, n_hallazgos)` —una fila por corrida— o, equivalentemente,
  seguir usando `data/sombra/veredictos.jsonl` (MEDIDO: ya existe,
  `comparar_sombra.registrar_veredicto`) como ese denominador. La segunda
  opción no requiere código nuevo.
- **Tasa de divergencia por clase, con intervalo.** Cuando se cite
  «divergen X% de los días», va con Wilson sobre días (no sobre tickers)
  y por clase; la herramienta es la de la skill `estadistica-evaluacion`.
  Ninguna cifra de ese tipo existe hoy y este documento no inventa una.

---

## 4. Transferencia de titularidad

### 4.1 El orden obligatorio (MEDIDO: skill `modo-emision`; `docs/SOMBRA.md` checklist)

```
1. Apagar los timers de la máquina que emite hoy.
2. Verificar que no emite: sin reporte de Telegram esa noche.
3. Recién ahí, poner a emitir a la otra.
4. Verificar que emite: reporte, sello nuevo, backup commiteado.
```

«Nunca solapado.» Y de `docs/SOMBRA.md`: «apagar los timers del Mac
primero, y recién entonces quitar `MKI_MODO=sombra` del PC. Nunca al revés
— el hueco es preferible al día con dos titulares.»

MEDIDO que el orden importa: componer la base canónica y cambiar el modo
fueron **dos operaciones distintas** el 30-ago (`DECISIONES.md` §37.7); el
primer movimiento se cerró sin tocar `MKI_MODO`.

### 4.2 Qué se verifica ANTES (PROPUESTA, sobre el precedente MEDIDO)

El precedente: la ventana de sombra exigía **3 días hábiles con `PARIDAD`**
y el criterio se declaró **inaplicable (racha 0/3)** porque la referencia
—el Mac— dejó de ser estable: selló 1 h 51 tarde el 26-ago, 31 min tarde
el 27, no selló el 28, selló el sábado 29 (`DECISIONES.md` §36.1-36.2). El
switch se hizo «por fundamento operativo, no por paridad alcanzada», con
un riesgo aceptado y escrito.

Para un mecanismo permanente el criterio se puede volver a aplicar, porque
ahora la réplica lleva semanas comparándose contra una titular estable
antes de que haga falta promoverla. Propuesta de precondiciones de
promoción (réplica → titular):

1. **N días hábiles consecutivos con `PARIDAD` inmediatamente anteriores
   al switch.** N = 3 es el número que el proyecto ya declaró y no cumplió;
   este documento propone **N = 5** hábiles (una semana de calendario
   completa: cubre un lunes con sesión de Seúl que abre en domingo UTC y
   un viernes, los dos bordes donde `calendarios.py` hace más trabajo).
   El valor de N es DECISIÓN PENDIENTE (§8, ítem 5). Un
   `DIA_NO_COMPUTABLE` no rompe la racha pero no suma; una `DIVERGENCIA`
   la vuelve a cero (MEDIDO: `comparar_sombra.contador`, líneas 497-540).
2. **Cero `PENDIENTE_PUBLICACION` abiertos** en el rango: si hay días sin
   resolver, la titular no pusheó y la racha no está completa.
3. **Mismo commit en las dos máquinas** (`git rev-parse HEAD` == `git
   rev-parse origin/main`, `git status --porcelain` vacío en la
   candidata; MEDIDO: `docs/RUNBOOK_REPLICA.md` §1).
4. **Última fila local de `snapshots` en la candidata con
   `plataforma_version` = la vigente** (`version.py`, MEDIDO
   `PLATAFORMA_VERSION = "5.0.3"`) — prueba de que su código es el que
   sella hoy y no un checkout viejo.
5. **`data/sombra_telegram.log` de la candidata revisado**: lo que habría
   mandado es lo que la titular mandó (checklist de `docs/SOMBRA.md`,
   ítem sin marcar).

### 4.3 Qué se apaga primero y qué se enciende después (PROPUESTA de secuencia concreta)

En la titular saliente, por este orden:

1. `systemctl --user disable --now` de los seis timers (o `launchctl
   unload` en macOS). Verificar con `list-timers` que ninguno tiene NEXT.
2. **Agregar `MKI_MODO=sombra` a su `.env`** — sí, aunque los timers estén
   apagados: si alguien los reinstala por descuido, la máquina despierta
   como réplica y no como segunda titular. Es la asimetría de `modo.py`
   trabajando a favor.
3. Esperar una noche: sin reporte de Telegram desde esa máquina (paso 2
   del orden).

En la titular entrante, recién después:

4. Quitar `MKI_MODO=sombra` de su `.env`; confirmar `modo.modo_actual()`
   → `titular` **en la propia máquina**.
5. **Publicar la marca de titularidad** (§5.3): commit y push manual de
   `data/backups/titular.json` con su hostname. Es el único push del
   procedimiento y es de Nicolás. Sin este paso la detección de la §5 no
   sabe quién es la nueva titular.
6. Sus timers ya estaban instalados como réplica; no se reinstalan.
   Verificar la noche siguiente: reporte en Telegram, sello nuevo con
   `plataforma_version` vigente, commit «Backup diario {fecha}» en su
   `main`.
7. La máquina saliente, si va a ser la nueva réplica, vuelve a encender
   sus timers **sólo después** del paso 6 verificado. Con `MKI_MODO=sombra`
   ya puesto en el paso 2.

### 4.4 Vuelta atrás (PROPUESTA)

- **Antes del paso 4:** nada emitió. Reencender los timers de la saliente
  y quitar la línea del paso 2. Un día de hueco como máximo.
- **Entre 4 y 6, si la entrante no emite** (sin reporte, sin sello):
  volver a poner `MKI_MODO=sombra` en la entrante, reencender la saliente,
  quitarle la línea. El día queda sin reporte, no duplicado. Se documenta
  en `DECISIONES.md`.
- **Si en cualquier momento hubo dos reportes de Telegram:** es la falla
  que este diseño existe para impedir. Apagar timers de **las dos**,
  documentar antes de reintentar, no reintentar el mismo día (mismo
  criterio que `docs/RUNBOOK_REPLICA.md` §4, «Vuelta atrás»).
- **Datos:** nada se compone. Las dos bases quedan intactas; la cadena
  oficial es la de `origin/main`. La composición por rango de fechas del
  30-ago (`fecha <= 2026-08-25` Mac / `>= 2026-08-26` PC, §36.1) fue la
  solución para **una** transición con historia copiada; en régimen
  permanente el overlap es el estado normal y la regla A lo resuelve sin
  componer (MEDIDO: `docs/REPLICA.md` §4, «El overlap de fechas ya no es
  una anomalía transitoria»).

---

## 5. Detección de sello duplicado antes del Telegram doble

### 5.1 El problema, con la línea de tiempo (MEDIDO: `systemd/*.timer` línea 7)

```
17:50  noticias        (mki_noticias.py)          — RSS + Haiku
18:15  snapshot        (snapshot.py --origen programado) — sella
18:25  reporte         (alertas.py reporte)       — TELEGRAM
18:40  backup          (mki_backup.py)            — commit local, sin push
19:00  vigía           (mki_vigia.py)             — 5 chequeos, alerta Telegram
20:30  vigía-rechequeo (mki_vigia.py --rechequeo) — epílogo
  ?    push            manual, de Nicolás, después de las 20:30
```

Dos máquinas en `titular` producen a las 18:25 dos reportes idénticos.
**Ninguna de las dos puede saberlo por sí sola con lo que hay hoy**: el
modo es local, el push es manual (MEDIDO: `mki_backup.py` línea 10), y
`origin/main` refleja a la otra máquina con el retraso de ese push.

Esto fija el alcance honesto de cualquier detección que lea sólo
`origin/main`: **detecta a un segundo titular que ya pushó**, no a uno
que emitió por primera vez esa misma tarde. La primera línea de defensa
sigue siendo la declaración (§2) y el orden del switch (§4). La
detección es la segunda: garantiza que un error de configuración **no
sobrevive al primer push**, y que el vigía lo grita en vez de que lo
descubra alguien mirando Telegram.

### 5.2 Las señales de duplicado (PROPUESTA; cada una con lo que la sostiene)

Todas se leen con `git fetch origin --quiet` + `git show
origin/main:<ruta>`. **Nunca `git pull`, nunca `checkout`, nunca `merge`**:
el árbol de trabajo es el código que los timers ejecutan esa noche
(MEDIDO: `comparar_sombra.py` cabecera y `docs/SOMBRA.md`, «Cómo lee el
comparador»; hay un test que falla si la cadena `pull` reaparece en ese
archivo — extender el mismo test al módulo nuevo).

| # | Señal | Dónde | Qué prueba | Límite |
|---|---|---|---|---|
| S1 | **Marca de titularidad** | `origin/main:data/backups/titular.json` → `{hostname, plataforma_version, escrito_en, ultima_fecha_sellada}` | quién es la titular *publicada* | la escribe `mki_backup.py` en modo titular (§5.3); llega a `origin/main` con el push manual |
| S2 | **Fila ajena para la misma fecha** | `origin/main:data/backups/senales_snapshots.csv` tiene fila con `fecha` = hoy (o la última fecha hábil) cuyo `creado_en`/`timestamp_utc` ≠ los de la fila local | otra máquina selló esa fecha **y la publicó** | la réplica también sella, pero no publica; una fila ajena publicada sólo puede venir de una máquina en titular. Misma huella que `CAMPOS_HUELLA_COPIA` (MEDIDO, `comparar_sombra.py` línea 145), leída al revés: coincidencia = copia, diferencia en `origin/main` = segundo sellador |
| S3 | **Commit de backup ajeno** | `git log origin/main --format=%cs -- data/backups` con fecha de hoy cuando el backup local **aún no corrió** (antes de 18:40) | alguien commiteó y pushó un backup de hoy antes que esta máquina | los commits no llevan hostname; es indicio, no prueba; puede ser el push tardío de ayer por Nicolás, por eso se combina con S1 |

S1 es la que decide; S2 y S3 confirman y sirven para el caso en que la
marca no exista todavía (antes de la primera activación).

### 5.3 La marca de titularidad (PROPUESTA)

`mki_backup.py`, **sólo en modo titular** (en sombra ya retorna antes de
tocar nada, MEDIDO), escribe `data/backups/titular.json` antes del `git
add` y lo incluye en el pathspec del commit «Backup diario {fecha}»:

```json
{"hostname": "<socket.gethostname()>",
 "plataforma_version": "<version.PLATAFORMA_VERSION>",
 "ultima_fecha_sellada": "<fecha del último snapshot local>",
 "escrito_en": "<UTC ISO>"}
```

Por qué en `data/backups/` y no en otra ruta: es el único directorio que
el job commitea (pathspec estricto, MEDIDO: `mki_backup.py` cabecera) y el
único que el pre-commit hook deja pasar sin correr la suite (`CLAUDE.md`,
sección Commands). Ningún otro archivo llega a `origin/main` solo.

Por qué no una columna nueva en `snapshots`: eso toca `snapshot.py` y
`senales.py`, intocables en esta corrida (preámbulo); y no hace falta —
la huella `creado_en`+`timestamp_utc` ya distingue selladores.

### 5.4 Qué hace cada máquina al detectarlo (PROPUESTA)

Módulo nuevo `guardia_titular.py` con **una** función pura,
`evaluar(hostname_local, modo_local, marca_publicada, csv_publicado,
snapshot_local) -> dict{veredicto, motivo, senales}` sin red ni
escrituras, más un envoltorio que hace el `fetch`/`show`. Tres veredictos:

| Veredicto | Condición | Acción |
|---|---|---|
| `TITULAR_CONFIRMADA` | modo local titular **y** (S1 nombra a este hostname **o** no hay marca publicada y S2 no encuentra fila ajena) | seguir |
| `SEGUNDA_TITULAR` | modo local titular **y** S1 nombra a **otro** hostname (o S2 encuentra fila ajena publicada para hoy) | **auto-degradarse para esta corrida**: el reporte de las 18:25 se escribe a `data/sombra_telegram.log` con cabecera `AUTO-DEGRADADA`, se deja el marcador `data/titular_conflicto.json`, exit 0. **No edita `.env`** (eso es de Nicolás; la degradación es del proceso, no de la configuración) |
| `SIN_EVIDENCIA` | `git fetch` falló (sin red) o modo local sombra | seguir con el modo declarado; el vigía lo anota |

Dónde se llama, en orden temporal:

1. **18:25, reporte.** `ExecStartPre` en `mki-reporte.service`, o la
   primera línea de `alertas._cli_reporte()` (MEDIDO: `alertas.py` línea
   345; ese archivo no está en la lista de intocables del preámbulo, pero
   este frente no lo toca). Si `SEGUNDA_TITULAR`: intercepta el envío.
   Es el único punto donde «detectar antes del Telegram doble» tiene
   sentido literal.
2. **19:00, vigía.** Sexto chequeo, de solo lectura: reporta
   `TITULAR_CONFIRMADA` / `SEGUNDA_TITULAR` / `SIN_EVIDENCIA`. Si hay
   marcador `titular_conflicto.json`, la alerta dice exactamente «esta
   máquina se auto-degradó a las HH:MM: `origin/main` nombra a
   `<hostname>` como titular». Va por `enviar_mensaje`, así que **si la
   máquina se degradó, la alerta también queda en el log y no en
   Telegram** — correcto: la que grita es la titular legítima, cuyo
   vigía ve la fila ajena en `origin/main` (S2) cuando la degradada
   pushee, o no ve nada si nunca pushea, que es el estado deseado.
3. **20:30, re-chequeo.** Sin cambio.
4. **21:00, séptimo job (§7).** Lee el mismo veredicto y lo deja en el
   reporte diario de comparación.

**Regla de simetría:** la titular legítima **nunca** se degrada por S2
sola. S2 sin S1 es ambigua (¿fila ajena o mi propio push de ayer visto
desde otro checkout?). Sólo S1 con hostname ajeno degrada. Por eso la
marca se publica en el paso 5 del switch antes de la primera noche
(§4.3): si la marca nombra a la máquina correcta, la única que puede
degradarse es la incorrecta.

**Caso sin marca (hoy):** hasta que exista `titular.json` en
`origin/main`, `evaluar` devuelve `TITULAR_CONFIRMADA` para la única
máquina en titular y S2 es puramente informativa. Activar la detección
sin haber publicado la marca es seguro: no degrada a nadie.

### 5.5 Qué NO hace la detección

- No apaga timers, no edita `.env`, no cambia `modo.py`.
- No decide cuál sello es oficial: eso es la §3, y la marca sólo dice
  quién *debía* emitir.
- No se ejecuta en la ruta de sellado: `snapshot.py` no la llama. Un
  fallo del `fetch` a las 18:25 no puede impedir el sello de las 18:15,
  que ya ocurrió.
- No usa Telegram como fuente (leer `getUpdates` para ver si «ya salió un
  reporte» sería una fuente de datos nueva y una salida de red nueva;
  fuera de alcance por el preámbulo y por diseño).

---

## 6. Puesta en marcha de la segunda máquina con el importador

### 6.1 Qué reconstruye (MEDIDO: `scripts/restaurar_backup.py` cabecera; `docs/RESTAURAR.md`)

`python3 scripts/restaurar_backup.py --destino DIR` reconstruye
`senales_restaurado.db` y `noticias_restaurado.db` desde los ocho CSV de
`data/backups/` (MEDIDO: `senales_snapshots`, `senales_senales_ticker`,
`senales_divergencias`, `senales_verificacion_apertura`,
`senales_verificacion_puntaje`, `noticias_titulares`, `noticias_analisis`,
`noticias_resumen_dia`). Reglas duras del importador:

- Nunca abre las bases reales en escritura; siempre a una base nueva en
  ruta temporal.
- Esquema **duplicado a propósito**, no importado de `senales.py` (para
  poder correr aunque el resto no importe limpio, y para no abrir jamás
  una conexión de escritura vía el `DB_PATH` de módulo).
- «SOLO reconstruye. No corrige, no reordena, no imputa filas faltantes.»

Para la réplica el origen es **`origin/main`**, no el árbol local: la
máquina nueva clona, y lo que hay en `data/backups/` es lo que la titular
publicó. Ese es el punto de partida correcto por definición (§3: lo
oficial es lo publicado).

### 6.2 Qué se verifica (MEDIDO + PROPUESTA)

MEDIDO, ya existe:

- `--verificar` compara la restauración contra las bases reales **por
  hash de contenido por tabla, ordenado por clave primaria**
  (`hash_tabla`, SHA-256, línea 401), no por hash de archivo (el formato
  de página de SQLite no es determinístico). En la máquina nueva no hay
  bases reales contra las que verificar, así que el hash sirve de otra
  forma: se corre **dos veces** la restauración y se exige el mismo hash
  por tabla (reproducibilidad; `tests/test_restaurar_backup.py` ya lo
  prueba).
- El último sello restaurado se imprime al final y se compara con el
  último commit «Backup diario {fecha}» (`git log --oneline -1 --
  data/backups/senales_snapshots.csv`).
- Invariante de dirección en noticias: `n_restaurado <= n_original`; al
  revés sería alarma.

PROPUESTA, para la réplica:

- **Hash por tabla de la restauración, anotado en el acta de activación**
  junto al SHA del commit de `origin/main` del que salió. Es la
  procedencia de la base de la réplica en una línea.
- **`plataforma_version` de la última fila de `snapshots` = 5.0.3**
  (invariante 4a de `DECISIONES.md` §37.2: toda fila con `fecha >=
  2026-08-26` lleva 5.0.3). Si no, el CSV es anterior al switch o el
  clon es viejo.
- **Y después de restaurar, la huella de copia hace su trabajo.** Todas
  las filas restauradas comparten `creado_en`, `timestamp_utc` y
  `plataforma_version` con las de la titular —son la misma fila—, así que
  `comparar_fecha` las rechaza como `DIA_NO_COMPUTABLE` por
  `CAMPOS_HUELLA_COPIA` **aunque no exista fecha de corte** (MEDIDO:
  `comparar_sombra.py` líneas 314-327). Esto es lo que permite retirar
  `FECHA_CORTE` en el uso permanente (`docs/REPLICA.md` §4; parámetro
  `fecha_corte=None` ya aditivo, `DECISIONES.md` §46): la fecha de
  arranque de la comparación no es una constante que alguien recuerde,
  es **el primer día en que la réplica selló por su cuenta**, y el
  comparador lo descubre solo. Propuesta: el séptimo job pasa
  `fecha_corte=None` y anota en cada reporte «fecha de restauración:
  <día>» leída del acta, como dato informativo.

### 6.3 Qué NO recupera el CSV (MEDIDO: `docs/RESTAURAR.md`, «Qué se pierde y qué no»)

| Límite | Qué pasa | Cómo lo trata el importador |
|---|---|---|
| **NULL vs `''`** | un vacío en CSV no distingue `NULL` de cadena vacía | tres columnas `TEXT NOT NULL DEFAULT ''` (`titulares.tickers`, `divergencias.explicacion`, `analisis.tickers_afectados`) se restauran como `''`; el resto como `NULL`. La primera corrida falló con `IntegrityError: NOT NULL constraint failed` — corregido en `TEXTO_DEFECTO_VACIO`; es la prueba de que la ambigüedad es real |
| **Enteros como float** | cualquier `INTEGER` con al menos un `NULL` sale como `120.0` del `to_csv` de `snapshot.py` (ya está así en los CSV versionados) | se recupera `120.0 → 120`; una fracción real en columna `INTEGER` **no se trunca**: se conserva y se reporta como hallazgo |
| **Lo sellado después del último backup commiteado** | el job es a las 18:40; una restauración pierde como mínimo el día de la caída | «No hay forma de recuperar eso desde el CSV — no existe» |
| **`sqlite_sequence`** | los `id` explícitos se preservan, pero el contador interno arranca de cero | SQLite lo recalcula al primer INSERT; «no se verificó explícitamente» — para la réplica **sí hay que verificarlo** el primer día que selle (PROPUESTA: el `id` de la primera fila nueva debe ser `max(id)+1`, sin colisión) |
| **PRAGMAs** (`user_version`, etc.) | no viven en tablas | hoy todos en valor por defecto; nada que perder |

Además, para la réplica en concreto (PROPUESTA de lectura): una
discrepancia backup-vs-viva no es necesariamente pérdida —el 31-ago se
midió una que explicaba íntegramente la composición canónica del 30-ago
(`docs/RESTAURAR.md`, clase 3). Antes de tratar una diferencia como
pérdida, revisar si el rango de fechas cae dentro de una cirugía
documentada.

### 6.4 El paso que el runbook ya tiene (MEDIDO: `docs/RUNBOOK_REPLICA.md` §1-§4)

Después de restaurar: mismo commit que la titular (§1), `MKI_MODO=sombra`
**en la réplica únicamente** y `modo_actual()` → `sombra` (§2; y
`titular` confirmado en la titular, en la propia titular), `./mki
instalar` (§3; en Linux pide confirmación antes de instalar timers,
`CLAUDE.md` §5.0.3), y una noche en frío verificando que el mensaje quedó
en `data/sombra_telegram.log` y **no** en Telegram (§4). Este documento no
repite esos pasos; los referencia.

---

## 7. Comparación diaria automatizada — el séptimo job

### 7.1 El hueco (MEDIDO)

Hoy no existe timer ni cron que compare. `comparar_sombra.py` se corre a
mano (`docs/SOMBRA.md`, «Rutina de las tres noches», paso 4);
`replica.py` «no corre sola»; `docs/RUNBOOK_REPLICA.md` §6 lo llama con
nombre: «alguien tiene que acordarse de correrlo todos los días — la misma
clase de punto débil que `docs/REPLICA.md` §4 ya señaló para
`FECHA_CORTE`». Y `replica_una_pagina.md`: «Sin construir un séptimo job,
alguien tiene que acordarse de correrla todos los días — que es
exactamente la clase de punto débil que este mecanismo existe para
eliminar.»

### 7.2 El job (PROPUESTA)

**Nombre:** `mki-comparar-replica` (`.timer` + `.service`, mismo patrón
`__MKI_DIR__` que los seis existentes; en macOS `com.mki.comparar`).

**Dónde corre:** en la **réplica**. Es la máquina que tiene la fila local
en `senales.db` y necesita la de la titular por `origin/main`; al revés no
hay nada que leer (la réplica no publica). Correrlo también en la titular
no compara nada: leería su propia historia desde `origin/main`.

**Cuándo:** `OnCalendar=Mon..Fri 21:00 America/Santiago`. Después del
re-chequeo de las 20:30 (así el marcador del vigía ya está resuelto) y
después de la hora en que el push manual «es razonablemente probable»
(`docs/RUNBOOK_REPLICA.md` §6 propone 21:00; se adopta). Si el push no
llegó, el veredicto es `PENDIENTE_PUBLICACION` y **no es final** — se
reintenta.

**Qué ejecuta:** `python comparar_replica.py` (envoltorio nuevo, delgado):

1. `fetch_titular()` — la **única** operación de red del job (MEDIDO:
   `git fetch origin --quiet`; sin `pull`).
2. `leer_csv_titular("senales_snapshots.csv")` y
   `("senales_senales_ticker.csv")` desde `origin/main`.
3. `comparar_fecha(fecha, ..., fecha_corte=None)` para: la fecha de hoy
   **y** cada fecha de `veredictos.jsonl` que siga en
   `PENDIENTE_PUBLICACION` (re-corrida automática; hoy el `--contador`
   los lista con el comando exacto, MEDIDO líneas 535-540, y una persona
   lo tipea).
4. `registrar_veredicto` (JSONL, denominador) y
   `replica.registrar_comparacion` (base de divergencias, sólo en
   `DIVERGENCIA`).
5. `guardia_titular.evaluar(...)` con los mismos datos ya traídos (§5),
   informativo.
6. Reporte en `data/sombra/comparacion_<fecha>.md` (ya existe ese
   formato, MEDIDO `componer_reporte`), y una línea en
   `data/comparar_replica.log` rotado con `registro.rotar_log`.

**Sin red salvo el fetch. Sin escrituras salvo `data/sombra/`,
`data/divergencias_replica.db` y su log.** No toca el árbol, el índice,
`senales.db` ni `.env`. Extender el test anti-`pull` al envoltorio.

### 7.3 Su alerta (PROPUESTA)

El job corre en la réplica, así que `enviar_mensaje` lo intercepta al log:
**la réplica no puede alertar por Telegram**, por diseño. Entonces la
alerta tiene dos caminos, y hay que elegir uno (§8, ítem 4):

- **(i) La titular alerta.** El vigía de la titular, en su pase de las
  19:00 del día siguiente, lee `origin/main`… pero la réplica no publica.
  Sin un canal de vuelta, la titular no puede ver el veredicto. **Este
  camino requiere que la réplica pushee algo**, aunque sea un archivo
  chico (`data/sombra/veredictos.jsonl`) a una rama propia (`replica`,
  nunca `main`). Es un push automático — hoy no existe ninguno y
  automatizar el push es una decisión que `docs/REPLICA.md` §4 dice
  explícitamente que no da por hecha.
- **(ii) La réplica alerta por un canal que no sea el reporte.** Un
  segundo bot/chat de Telegram sólo para la réplica, con un token propio,
  no interceptado por el modo sombra. Rompe la regla «`enviar_mensaje` es
  el único punto de salida» y agrega un secreto nuevo. **Se lista y se
  desaconseja.**
- **(iii) Sin alerta activa: `./mki estado` y `/salud` en la réplica
  muestran el último veredicto, y el reporte diario de comparación se
  lee cuando se abre la máquina.** Es lo que hay hoy con un timer
  encima. Elimina el «acordarse de correrlo», no el «acordarse de
  mirarlo».

**Recomendación, marcada como tal: (iii) para activar, con (i) como
segunda etapa** si Nicolás decide que la réplica pueda pushear a una rama
propia. (i) es la única que cierra el círculo —la titular grita por
Telegram si la comparación divergió o no corrió— sin un canal nuevo; su
costo es un push automático acotado a una rama que nadie mergea.

### 7.4 Cómo evita «alguien tiene que acordarse» (PROPUESTA)

- **Correrla:** el timer. Y `PENDIENTE_PUBLICACION` se re-corre solo cada
  noche hasta resolverse; nadie tipea `--fecha`.
- **Mirarla:** `./mki estado` en la réplica muestra, después del modo, la
  línea «última comparación: <fecha> · <veredicto> · racha N»; `/salud`
  la muestra como sexta tarjeta. Si el veredicto tiene más de 2 días
  hábiles, se pinta como el resto de los jobs atrasados.
- **Que no corra:** el vigía de la réplica —que ya corre a las 19:00 y
  escribe a su log— agrega el chequeo «¿existe
  `data/sombra/comparacion_<ayer>.md`?». Queda en el log de la réplica y
  en `./mki estado`; llega a Telegram sólo bajo (i).
- **Retención:** ver §8, ítem 3. Sin política, `data/sombra/` y la base
  de divergencias crecen sin límite (MEDIDO: `docs/REPLICA.md` §4,
  último punto).

---

## 8. Decisiones que van a la cola

Numeradas, cada una con opciones y recomendación **marcada como
propuesta**. Ninguna está tomada. Las 1-4 ya figuran en
`docs/RUNBOOK_REPLICA.md` §0 y `docs/REPLICA.md` §5; la 5-8 las agrega este
documento.

1. **Quién gana ante divergencia.** Opciones A (titular siempre) / B
   (mejor salud de descarga) / C (no se sella). **Recomendación: A** (§3.3).
   Bloquea todo lo demás (`espera_firma.md` §4: «Ésta es la que bloquea»).
2. **Qué máquina es réplica.** Opciones: (a) **el Mac**, que quedó libre,
   con Python 3.11.15 y launchd (`docs/RUNBOOK_REPLICA.md` §0); su
   historial en contra está medido: sellos a 21:23 y 19:40 en julio por
   re-dormirse (DarkWake, `CLAUDE.md` §5.0.1), 1 h 51 y 31 min tarde el
   26 y 27-ago, sin sello el 28, sello espurio el sábado 29 (§36.1); a
   favor, que esos sellos tardíos son **exactamente la clase de
   divergencia de existencia que el registro debe capturar**, y que una
   réplica que se duerme no le cuesta nada a la titular. (b) **Una
   tercera máquina** siempre encendida (VM, mini-PC): sin DarkWake, sin
   historial, costo de compra y de un tercer entorno que mantener
   alineado (`requirements.txt` fijado). (c) **Ninguna todavía.**
   **Recomendación: (a) con `caffeinate -dimsu` en la ventana 17:45-21:15
   como precondición operativa escrita**, y pasar a (b) si el registro
   muestra que el Mac falla como réplica con la frecuencia con que falló
   como titular — el registro es lo que permitirá decirlo con un número
   en vez de con memoria.
3. **Retención del registro de divergencias y de `data/sombra/`.**
   Opciones: (a) sin límite (hoy); (b) `data/sombra/*.md` rotados a 90
   días, `veredictos.jsonl` y `divergencias_replica.db` sin límite (son
   chicos: una fila por hallazgo, un JSON por día); (c) resumen mensual
   y borrado. **Recomendación: (b)** — los reportes en markdown son
   reconstruibles desde el JSONL y la base; el JSONL y la base son el
   dato y se conservan enteros, mismo criterio que `data/backups/`.
4. **Si se instala el séptimo job, y con qué alerta.** Opciones: no
   instalar (comparar a mano); instalar con alerta (iii) pasiva; (i) con
   push de la réplica a rama propia; (ii) canal Telegram nuevo.
   **Recomendación: instalar con (iii)**; (i) como segunda etapa y
   decisión aparte porque automatiza un push; (ii) desaconsejada.
5. **N de días con `PARIDAD` para promover la réplica a titular.**
   Opciones: 3 (el precedente, incumplido por inaplicable), 5 (semana
   hábil completa), 10. **Recomendación: 5** (§4.2).
6. **Publicar la marca de titularidad `data/backups/titular.json`.**
   Opciones: sí, escrita por `mki_backup.py` en titular; no (la detección
   de la §5 queda en S2/S3, informativa). **Recomendación: sí**, porque
   sin S1 ninguna máquina puede auto-degradarse con seguridad y la
   detección se reduce a un aviso.
7. **Instalar la guardia de titular en el reporte de las 18:25.**
   Opciones: `ExecStartPre` del service (no toca `alertas.py`), primera
   línea de `_cli_reporte()` (toca `alertas.py`), o sólo en el vigía
   (detección sin auto-degradación). **Recomendación: `ExecStartPre`**,
   porque deja `alertas.py` intacto y, si el módulo nuevo falla, systemd
   registra la falla del pre-paso y el reporte no sale, que es el lado
   seguro del error.
8. **Retiro de `FECHA_CORTE` como comportamiento por defecto.** Ya en
   `docs/REPLICA.md` §5 y `DECISIONES.md` §46. Opciones: dejar el default
   y que sólo el séptimo job pase `fecha_corte=None`; cambiar el default.
   **Recomendación: la primera** — el CLI de `comparar_sombra.py` sigue
   siendo la herramienta de auditoría del switch pasado y no hay razón
   para que cambie de conducta.

Y una nota que no es decisión sino aviso: **la réplica gasta presupuesto
de IA.** MEDIDO: `mki_noticias.py` no consulta `modo` (`grep -n modo
mki_noticias.py` → sin resultados); en sombra corre RSS + Haiku igual que
la titular, con su propio tope `NOTICIAS_PRESUPUESTO_USD_DIA` leído de su
propio `.env` (default 0.50, `costos.py` línea 19). Dos máquinas = dos
topes. Si se quiere que la réplica no analice con Haiku, es un cambio en
`mki_noticias.py` que este documento no propone (las noticias son nivel 3,
diferencia esperada, y no afectan al veredicto).

---

## 9. Riesgos y qué se rompe con cada elección

| Elección | Riesgo | Qué se rompe si sale mal | Cómo se contiene |
|---|---|---|---|
| **A (titular gana)** | una fila mala de la titular queda oficial con una buena en auditoría | nada del track record; se pierde la corrección | queda documentado el mismo día; una errata fechada si corresponde |
| **B (salud de descarga)** | el rol se deduce por la noche | `modo.py` deja de ser la única fuente de verdad; dos máquinas pueden creerse titulares | no se contiene: es el escenario que la §2.2 dice que ya pasó al deducir |
| **C (no se sella)** | un `fetch` fallido o un push tardío borra un día | agujeros en el track record por causas ajenas al modelo | no se contiene sin darle a la réplica poder de veto |
| **Mac como réplica** | se duerme a mitad de la descarga | divergencias de existencia frecuentes; el registro se llena de «la réplica no selló» | `caffeinate` en la ventana; mover a tercera máquina con el número en la mano |
| **Tercera máquina** | tercer entorno a mantener alineado | divergencias de cómputo espurias por versión distinta de pandas/numpy | `requirements.txt` fijado; el nivel 1 las detecta el primer día |
| **Séptimo job en la réplica** | `git fetch` es una salida de red nueva desde la réplica | si el remoto exige credenciales interactivas, el job cuelga (el caso del 3-ago con RSS, `CLAUDE.md` §5.0.2) | `socket.setdefaulttimeout` + `timeout=` en el `subprocess`; el vigía de la réplica reporta «no corrió» |
| **Alerta (i): push automático a rama propia** | primer push no humano del proyecto | rompe «publicar es un acto manual» (Constitución 5.0 (5)) si la rama se confunde con `main` | rama fija `replica`, pathspec de un archivo, nunca `main`; y sigue siendo decisión de Nicolás |
| **Alerta (ii): segundo bot** | secreto nuevo, segundo punto de salida | `seguridad.py` y la regla del punto único quedan con una excepción | desaconsejada |
| **Marca `titular.json`** | marca desactualizada tras un switch sin push | la nueva titular se auto-degrada a sí misma: **noche sin reporte** | es el lado seguro del error (hueco, no duplicado); paso 5 del switch la publica antes de la primera noche |
| **Guardia con `ExecStartPre`** | módulo nuevo falla | el reporte no sale esa noche | vigía alerta «reporte: NO hay envío»; lado seguro |
| **Retirar `FECHA_CORTE` del default** | el CLI histórico cambia de conducta | reportes viejos de `data/sombra/` dejan de reproducir | no cambiar el default; sólo el job nuevo pasa `None` |
| **Restauración por CSV en la réplica** | NULL/`''` y `sqlite_sequence` | una fila con `''` donde la titular tiene `NULL` cae en nivel 2 como divergencia falsa | esos tres campos no están en NIVEL1/NIVEL2 (MEDIDO: listas líneas 83-96); `id` está excluido; verificar `max(id)+1` el primer día |
| **Presupuesto IA duplicado** | dos topes diarios | gasto hasta 2× el tope | tope propio en cada `.env`; o cambio en `mki_noticias.py`, no propuesto acá |
| **Detección sólo por `origin/main`** | ventana ciega hasta el primer push del segundo titular | un Telegram doble la primera noche | no se contiene con esta detección: se contiene con el orden del switch (§4) |

---

## Cierre del frente

**Archivos creados/modificados:** sólo
`/home/nicolasaraneda/dev/mki-terminal/GEMELO/diseno/replica.md` (este
archivo; el directorio `GEMELO/diseno/` existía vacío). Ningún `.py`,
ningún `.env`, ningún timer, ninguna base tocada; ninguna operación de git
que escriba.

**Intentos del DSR consumidos:** 0. No se probó ninguna hipótesis sobre
retornos ni se corrió ninguna configuración.

**Qué quedó abierto:** las ocho decisiones de la §8. Además: (a) el nombre
`guardia_titular.py` y el formato de `titular.json` son propuesta sin
prototipo — no hay test que los pruebe; (b) no se midió cuánto tarda `git
fetch` desde esta máquina (dato útil para el timeout del séptimo job; no
se ejecutó porque es red); (c) el hostname del Mac no se conoce desde acá
y la marca lo necesita.

**Errores propios:** (1) El primer comando compuesto de la sesión fue
denegado entero por incluir `grep -c MKI_MODO .env`; lo separé y usé la
lectura canónica de `modo.py` en su lugar, que es lo que la skill
`modo-emision` exige de todos modos — el encargo pedía el `grep` y no se
pudo cumplir, queda dicho arriba. (2) Busqué la skill `switch-titular` en
la ruta del encargo y no existe; usé `modo-emision` y `docs/SOMBRA.md` y
lo declaré como errata del encargo en vez de inventar la referencia. (3)
Un primer borrador mental de la §5 proponía que S2 (fila ajena en
`origin/main`) bastara para auto-degradarse; al escribir la regla de
simetría vi que S2 sola es ambigua con el propio push tardío visto desde
otro checkout y la reduje a confirmación — sólo S1 degrada.
