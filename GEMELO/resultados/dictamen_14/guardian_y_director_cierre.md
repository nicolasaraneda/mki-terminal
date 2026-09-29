# Dictámenes de cierre de la corrida 14 — `guardian-constitucion` y `director-programa`

Transcripción por el orquestador. Los dos son solo lectura y ninguno escribió en el repo.

---

# 1. `guardian-constitucion` — el diff completo

```
DICTAMEN: OBSERVADO (= APROBADO CON OBSERVACIONES) — no RECHAZADO

Rama: main   HEAD: 5321f6b (sin commits nuevos)
18 archivos rastreados modificados + 6 rutas nuevas sin versionar
+2424 −89 en rastreados, más estado_epistemico.md (+78 −1)
Anclaje: árbol leído entre las 17:23 y las 17:35 del 28-sep-2026
```

## Observación 0, la que el guardián pidió que se lea primero: la tanda no estaba cerrada

Tomó su primer censo a las 17:23:12 y **el árbol siguió moviéndose durante todo su dictamen**:
`estado_epistemico.md` a las 17:24 (y **no estaba en el encargo que se le dio**), `adversario_m2.md` a
las 17:26, `bitacora_14.md` de 811 a 913 a 1.019 líneas entre 17:29 y 17:33, `ESTADO.md` a las 17:29, y
`DECISIONES.md` hasta las 17:34, donde el acta §89 creció 26 líneas y le apareció **§89.9-bis**, la
medición. Dos consecuencias que el guardián nombró:

1. **El encargo que se le dio estaba vencido cuando lo recibió**, y omitía
   `GEMELO/resultados/estado_epistemico.md`, que es uno de los cinco **documentos publicados**
   (`cifras.DOCUMENTOS_PUBLICADOS`). Estuvo a punto de dictaminar sin ver un cambio a un documento
   publicado; lo encontró por su cuenta con un `git diff -- '*.md'`.
2. **§89.9-bis es una medición hecha después de que se le pidiera el dictamen** y trae el hallazgo
   material más fuerte de la corrida (`roca_chip` 44 → 17).

**Su dictamen vale para el árbol de las 17:35:09 y no después; hay que volver a pedirlo sobre el árbol
final.** Norma de procedimiento que sale de ahí: **el guardián se llama después del último `Write`, no
en paralelo**, y su encargo se arma con `git status` en el momento.

Y una salvedad que corresponde: el acta cita que el `director-programa` marcó la medición como «alcance
de menos y estaba disponible», pero **un dictamen de otro agente no es autorización de Nicolás**. La
medición en sí es defendible —17:31 está fuera de la ventana prohibida, no escribió ninguna base
(verificado) y su propio texto se niega a usarla para decidir el §61— pero entró al acta después de
cerrada la tanda y por la vía de un agente. **Queda para que Nicolás la ratifique o la saque.**

## Rechazos: NINGUNO. Las cuatro reglas de rechazo automático, verificadas una por una

- **R0 — `motor.py` y la lógica de señales: INTOCADOS.** No aparece en las 24 entradas del status ni en
  el `--stat`. Tampoco el modelo 4.6.0 ni los umbrales de régimen.
- **R1 — Filas selladas: NO REESCRITAS.** `senales.py`, `snapshot.py`, `universo.py` y
  `dinero/sello_dinero.py` **no están en el diff**. Escaneo de SQL destructivo (`UPDATE `, `DELETE FROM`,
  `DROP `, `ALTER TABLE`, `.to_sql(`, `if_exists`) sobre **todas** las líneas agregadas: **0
  coincidencias**. Las tres huellas sha256 verificadas **dos veces** (17:23 y 17:35), idénticas a las de
  la apertura. Y cada escritura de datos atribuida por mtime contra el journal: 14:42:58 la sonda,
  14:43:01 el sellador, 14:43:30 el snapshot — **ninguna después de las 16:38**. *Corrección al encargo
  que se le dio: los jobs **no** corrieron a las 18:15/18:40; los ocho `mki-*` terminaron entre 14:42:53
  y 14:45:21, que es el propio incidente del despertar.*
- **R2 — Sin push y sin pull: CONFIRMADO.** `git reflog` termina en el commit del job de backup;
  `.git/FETCH_HEAD` datado **8-sep-2026** (20 días): no hubo tráfico remoto. Barrido de
  `push|pull|fetch|remote|origin` en las líneas agregadas de código y scripts: **ninguna**; las únicas
  menciones son negaciones en prosa.
- **R8 — Modo y timers: INTOCADOS.** `modo_actual()` = `titular`. `.env` en 600, mtime 30-ago, no en el
  diff. **Las ocho unidades instaladas conservan sus mtimes (25-ago, 9-sep, 19-sep)**, y la instalada de
  la sonda sigue con **un solo** `OnCalendar`: la plantilla del diff vive en `GEMELO/propuestas/` y no
  está instalada.

## Observaciones

1. **La suite no está en verde, y por eso es OBSERVADO y no APROBADO liso.** Corrió los tres archivos de
   test relevantes: **2 failed, 58 passed**, y **los tests que la corrida tocó pasan todos**. Verificó que
   los rojos son preexistentes **en HEAD**, por una razón más precisa que la del encargo: el CSV *de HEAD*
   ya daba `13 / 9` contra el `9 / 7` que publica `README.md`. **Veredicto sobre la pregunta que se le
   hizo: dejar la corrida con dos rojos es aceptable y NO es una violación**, porque no son regresión,
   porque el bloque que los arreglaba está bloqueado por un dictamen **que el propio encargo ordena**, y
   porque la corrida los declara en cuatro sitios. Pero impide el aprobado liso — **y falta la advertencia
   práctica: este diff no se commitea sin `SKIP_TESTS=1`** (el hook sólo exime el commit que toca *sólo*
   `data/backups/`). *Aplicado: `bitacora_14.md` §8.5.*
2. **`estado_epistemico.md` entró sin el dictamen que el encargo exige.** El encargo condiciona la entrada
   a que el adversario lo dictamine; de los once ítems, siete están cubiertos por el `auditor-lookahead`
   (sustancia sí, letra no), uno por el `estadistico-adversario`, y **(v), (vi) y (viii) —los de la
   sonda— por ninguno**. No lo elevó a rechazo porque es puramente aditivo (una sola línea borrada en todo
   el archivo: la fecha del título) y ninguna cifra del track record se movió. *Aplicado: (v), (vi) y
   (viii) se retiraron del documento publicado y quedan completos en `bitacora_14.md`, con una línea que
   dice por qué.*
3. **El acta §89 cubre todo lo que se le pidió verificar, menos una cosa:** no declaraba la escritura en un
   documento publicado. Y verificó que no se introduce ninguna asimetría Mac/PC nueva: el único import
   nuevo es `exchange_calendars`, ya en uso.
4. **El «19 de 20» no es reproducible desde el módulo dueño del umbral:** `GEMELO/m2_periodo.py` sigue en
   `UMBRAL_M2_PCT = 25.0`, así que el conteo contra 8,3333 %/año se computó **fuera**. Es la misma vara que
   §61 le aplica a las 24 filas del 28-sep. No pidió cambiar el módulo —sería aplicar una enmienda
   declarada NO APLICABLE— sino que la no-reproducibilidad **viaje al lado del número**. *Aplicado en
   §9 del pre-registro, en `bitacora_14.md` §4.5 y en `estado_epistemico.md` (x).*
5. **Dos números sin su etiqueta completa:** la mediana «22:35» del artefacto de la sonda es sobre **2
   noches**, o sea el promedio de dos valores y **una hora que no se observó nunca**; y la plantilla del
   timer afirmaba en plano «el PC volvió de suspensión», que es una **inferencia**. *Aplicado: el descargo
   de inferencia está en la plantilla; la mediana quedó declarada en `bitacora_14.md` §8.6 y el arreglo de
   `informe()` va al encargo 15.*
6. **§61 no decía que dos de sus cuatro opciones tocan la Constitución.** Las opciones (a) —con efecto
   retroactivo— y (c) chocan con el punto (3) de `CLAUDE.md` («las filas selladas JAMÁS se reescriben»).
   Firmar (a) retroactiva **es enmendar la constitución**, no sólo cambiar código. *Aplicado en §61 con
   esas palabras.*

## Las cinco sospechas que se le pidió mirar

- **¿Se corrigió algo publicado sin autorización? NO.** La corrección en su sitio de la §9 es
  **LEGÍTIMA**, contrastada contra la §5: no hace ninguna de las cosas que invalidan el pre-registro, el
  umbral **no se movió**, y —verificado con dureza— **`git diff HEAD -- dinero/preregistro_dinero.md`
  tiene CERO líneas borradas**: toda la §9 es adición. Está declarada en cuatro sitios. Y «la dirección de
  la corrección es la que nunca despierta sospecha: **hizo más visible el costo del criterio, no menos**».
  **La errata fechada no se debía**: la frontera es el commit y la §9 no está commiteada; si la frase
  hubiera estado en la §8, que sí lo está, entonces sí.
- **¿El acta afirma alguna firma que no exista? NO.** Los trece sub-ítems de §88 que §89 cita existen
  todos en HEAD, y toda mención a una firma remite al §88 o difiere en Nicolás. Verificó además por su
  cuenta la afirmación del §60 con `git check-ignore -v` y `git ls-files`.
- **¿Alguna tarjeta nueva borra texto viejo? NO.** Las únicas cinco líneas borradas de `espera_firma.md`
  son los cinco encabezados, cada uno reemplazado por el mismo texto más su marca, y cada tarjeta cierra
  con «Texto original conservado:».
- **¿`ESTADO.md` respeta su máximo? SÍ**, 50 líneas exactas contra el máximo de 50 que declara.
- **¿El resumen recomienda una hora para el sellador? NO.** Leído entero: sólo estatus de PROPUESTA y
  descripción.

## Verificado en verde, además

`main` en las dos máquinas. **Secretos: 0 coincidencias** de los dos patrones exactos del pre-commit sobre
un bundle de **5.950 líneas** (stageado + no stageado + los seis archivos nuevos). **Cifras que dependen de
`n`: ninguna se movió** — `README.md`, `README.es.md`, `docs/readme/` y `GEMELO/bifurcaciones.py` no están
en el diff, y los tres registros de intentos verificados **importando los módulos**: 354 / 360 / 4.
**Regla 10:** los 35 patrones de `cifras.cifras_retiradas()` sobre el bundle dan **un solo hit**, la banda
«14 % a 43 %» del pre-registro, **con su marca RETIRADA en la misma línea**; **0 en `.py`**.
**Regla 14:** donde no se podía medir, la corrida escribió «NO SE MIDIERON» en vez de suponer, y la
predicción sobre el sellador va rotulada como falsable con su falsador explícito.

Y verificó el hallazgo central **por su cuenta y por una segunda fuente**: sobre
`data/backups/senales_senales_ticker.csv` (1.375 filas), `available_at > timestamp_utc` da **24 filas,
todas del 2026-09-28, ninguna otra fecha en toda la historia**; `senales.py:334` tiene una sola guarda de
timing y nunca compara `available_at` con `timestamp_utc`; las dos expresiones de calendario normalizan a
lo que el test afirma; y el contador de E0 da 14 / 9 al dígito.

## Qué hay que revertir: NADA

Lo que pidió antes de aprobar, en orden de costo: (1) cerrar la tanda y **volver a pedir el dictamen**, y
ratificar o sacar §89.9-bis; (2) **decidir qué se hace con el `roca_chip` 44 vs 17 antes de las 18:25**;
(3) declarar el bloqueo del hook; (4) sacar de `estado_epistemico.md` los ítems sin dictamen o
conseguirles uno; (5) tres líneas de prosa (la no-reproducibilidad del 19/20, el descargo de inferencia,
y nombrar `CLAUDE.md` en §61). **Todo lo aplicable se aplicó, salvo (1) y (2), que son de Nicolás.**

Y lo que el guardián dejó escrito a favor: «no tocó el camino de sellado teniendo delante un defecto grave
y una tentación evidente de arreglarlo; declinó contar el 28-sep como quinta noche cuando el reloj se lo
regalaba; y §89.9-bis se niega a usar su propia medición para decidir el §61. Las tres son exactamente la
disciplina que estas reglas existen para forzar.»

## Re-dictamen sobre el árbol congelado (pedido por él en la observación 0)

Se le volvió a pedir el dictamen a las 17:52, sobre el árbol detenido a las 17:48:11. Delta medido:
**+714 / −102 líneas**, todo prosa salvo un comentario en una plantilla **no instalada**; verificó por
mtime que los tres archivos de código y los dos de test no se tocaron después de las 17:35.

```
RE-DICTAMEN (delta): sigue OBSERVADO — «pero ya no por nada que la corrida pueda arreglar»
Rechazos: NINGUNO. Las seis observaciones aplicadas, y dos «mejor de lo que las pedí».
```

**Por qué sigue siendo OBSERVADO y no APROBADO, con sus palabras:** «Una sola razón, y **no es un defecto
de la corrida**: mi R6 exige `pytest -q` completo en verde para aprobar, y la suite sigue en 2 failed… Lo
que sí digo, y es lo importante: **ese portón no lo puede cerrar ninguna vuelta más de trabajo.** Se
cierra por **firma de Nicolás** —§65, opción (a), (b) o (c)— o no se cierra… **No pido otra vuelta. La
tanda está cerrable.**»

**Lo que cazó y se corrigió:** (1) **`noticias.db` se movió a las 17:52:39**, por el `mki-noticias` del
timer de las 17:50, así que la afirmación «las tres huellas idénticas al abrir y al cerrar» quedaba
desactualizada — corregido en §8.2 con la hora del journal, y `senales.db` y `dinero/sello_dinero.db`
siguen byte a byte en las de las 16:38. (2) **«quedan REFUTADAS» decía más que lo medido**: lo refutado es
que el riesgo se materializara **en esta fecha**, no la sospecha como riesgo, porque con las 8 betas
positivas el mecanismo sigue ahí — corregido en los cuatro documentos. (3) **Inventario que no es de esta
corrida:** `cola_decisiones.md` publica ahora **897** (línea que viene de HEAD, de la corrida 13) y
**904** (la de hoy, correcta) — el mismo patrón que §65 denuncia, ahora dentro de esa página; queda
inventariado y **no corregido de paso**.

**Su única observación nueva, y se actuó:** el portón de «sin dictamen no entra a documento publicado» se
aplicó a los tres ítems de la sonda **y no a `(iii-bis)`**, la medición del `roca_chip`, «que está en la
misma situación exacta y es más grande», y que además **llena la zona ciega #1 del propio auditor** y
cambia la base probatoria de dos de sus tres fundamentos. Su recomendación —«baratísimo y blinda §61»— era
devolverlo al `auditor-lookahead`. *Hecho: se le consultó a las 17:54 y `(iii-bis)` quedó marcado en
`estado_epistemico.md` como «a la espera de su dictamen»; si no lo cubre, sale.*

**Dos correcciones que aceptó de la corrida.** Sobre §61: «yo dije "(a) y (c) tocan la Constitución". La
versión nueva distingue bien: agregar la guarda **hacia adelante endurece la regla maestra** y es
admisible en especie; lo que toca la constitución es el **efecto retroactivo**… Esa distinción es más
precisa que mi observación y hace la tarjeta firmable sin ambigüedad. **Tomo la corrección.**» Y sobre el
retiro de los tres ítems: «lo que me convence no es el retiro, es que **el hueco se declara**… Un retiro
silencioso habría sido peor que no retirar.»

**Y ratificó que los cuatro «no hice» están bien no hechos:** cambiar `m2_periodo.py` sería aplicar una
enmienda declarada NO APLICABLE, y tocar `informe()` dentro de la ventana habría obligado a una suite que
no se puede correr. «Las dos son la elección correcta.»

---

# 2. `director-programa` — alcance del cierre

**Veredicto: MOVIÓ LA AGUJA, con un déficit nombrado. Nada que revertir.**

## Los tres ítems que se le pidió mirar con desconfianza: los tres pasan

- **El filtro del resumen (A9): ADELANTE, era lo que correspondía.** «Un bloque cuyo entregable es un
  artefacto publicado **tiene** que corregir la contaminación del artefacto que va a publicar; eso no es
  un frente nuevo, es el frente pedido.» Con un apunte que hay que dejar escrito: **el filtro no excluye
  la noche del 28, excluye las observaciones intradía**; las ocho sondas post-cierre de esa noche las
  admitiría. Excluir la noche es un juicio del orquestador, no una consecuencia del código. *Aplicado en
  `bitacora_14.md` 1.6 y en la tarjeta §58.*
- **Los `assert` extra en `_camino_main`: no sobran.** El que pidió el guardián de la 13 protege contra
  *leer* la base real; `DIR_EXT` y `DIR_BACKUP_EXT` protegen contra *escribir* en evidencia sellada,
  versionada y protegida por hook. «Quitarlas sería dejar la mitad barata afuera.»
- **Documentación de más: sí, y está localizada.** **§63 es más una premisa que una tarjeta** — su
  contenido sostiene §61(b) y §62(a), y su única decisión propia es menor porque el lado lector ya está
  aplicado. Recomienda **fundirla en §61 y §62**. *Aplicado como nota en §63; fundirla es de Nicolás.*
  Y **§89.11 es un cambio de gobernanza que hay que mirar de frente**: «la corrida que quería seguir
  escribió la norma que le permitió seguir». El razonamiento es correcto y está remitido a firma, pero
  «una norma que convierte un alto duro en un juicio no debería quedar *aplicada* a la espera: **o se
  firma o se rechaza en el encargo 15**; no se deja derivar hacia la práctica».

## El déficit, y es real: la medición estaba disponible y no se había hecho

El cierre de NYSE es a las 17:00 de Chile, la suite cerró a las 17:03 y la ventana prohibida empieza a las
17:50: **hubo ~45 minutos con el dato en la mano**. Y el argumento habitual para no descargar **no
aplicaba**, porque el sello del 28 ya existía y `ya_existe_snapshot_hoy()` garantizaba que las 18:15 no lo
rehacían: no había cadena de sellos que proteger. «Esos minutos se gastaron en documentos.»
*Aplicado: la medición se hizo a las 17:31 y es la sección 9 de `bitacora_14.md` y el §89.9-bis del acta.*

Y un defecto de orden que la tarjeta §61 tenía: ponía la medición como «lo que decide la magnitud».
**«La magnitud no puede decidir la regla.** Si las filas se retiran sólo cuando el signo salió mal, eso es
elegir qué filas cuentan después de verlas — la fuga de selección que el auditor advirtió, entrando por la
puerta que la tarjeta deja abierta. La regla se firma por su mérito y después se mide el daño.»
*Aplicado: §61 ahora abre con eso.*

## Prioridad de las cinco tarjetas: tres correcciones

1. **§61 primero: de acuerdo.** Toca el activo número uno, tiene reloj (mañana 18:15 el verificador
   escribe las 8 filas) y su mecanismo sigue armado para el próximo despertar.
2. **La que cuesta más no está entre las cinco: es §58.** Medido en la propia bitácora: de 14 sesiones
   selladas, **4 se perdieron por `insumo_incompleto`** y **1 por el despertar**. La hora del sellador
   quema N **cuatro veces más rápido** que los despertares: en un mes, §58 cuesta del orden de 8 sesiones
   y §62 ~1 por evento.
3. **§65 va cuarto y se firma en la misma sentada que §61**, porque el parche de §61 toca `senales.py` y
   se escribiría contra una suite que ya tiene dos rojos.
4. **La cola se contradecía consigo misma:** declaraba §61 «lo más caro» y en la misma línea «la cola no
   se reordenó», mientras su §1 seguía diciendo «primero de la cola». *Aplicado: el orden está escrito.*

Y el traspaso tenía un defecto de jerarquía: **`ESTADO.md` no decía que a las 18:25 el reporte publica las
cifras intradía** — el único ítem con vencimiento en minutos estaba en la fila 3 de una tabla de la
sección 6-bis. *Aplicado: encabeza `ESTADO.md`.*

## ¿Movió la aguja?

«**Movió la aguja, y no por lo que los documentos enfatizan.** Lo que se ganó es un defecto de mecanismo
en el instrumento, encontrado por el instrumento… Y el subproducto es más grande que el incidente:
`tests/test_motor.py` trunca con `<= fecha`, inclusive, así que la barra parcial de `t` está en las dos
ramas y se cancela — el test maestro anti-look-ahead del proyecto tiene un eje ciego, declarado, con su
razón. Eso queda para siempre.» Lo mismo el vigía probando igualdad en vez de orden y `descarga_ok`
exigiendo sólo dato en 7 días: **tres guardas verdes por la razón equivocada, nombradas**.

«El frente del README perdió la noche, y eso es una pérdida real — pero **la prioridad del encargo estaba
mal, no la obediencia**: una página con cuatro cifras vencidas cuesta integridad; un riel que certifica
una conocibilidad imposible cuesta el activo.» Y el déficit, sin adorno: «**la noche se quedó a una
medición de ser decisiva**» — medición que después se hizo.

## Lo que el director pide para el encargo 15

**0. (De Nicolás, antes de las 18:15 del 29-sep.)** Firmar la regla del §61 y su corte de método con
fecha, y decidir explícitamente si se aplica retroactivamente a las 24 filas. Es el único vencimiento duro.
**1.** Medir el daño del 28-sep, sólo lectura, **después** de firmada la regla, y publicarlo como daño,
nunca como insumo de si las filas cuentan. *(Hecho ya, en la sección 9, y con esa salvedad escrita.)*
**2. §65 + el bloque 2** (las tres erratas de §88.5), que se desbloquea con §61 y tiene que estar antes de
escribir el parche.
**3. §58**: instalar la franja de madrugada o decidir que no. Es el ítem que más N quema, y **más noches de
la grilla actual no lo resuelven**: la noche del 22-sep está censurada a las 23:35 con 34 de 36 sin cierre.
**4. §62**, opciones (a) y (d) juntas, con la política de retención de (d) escrita antes de cualquier código.
**5. §64**, y **§63 fundido** en §61/§62.

**Y lo que queda postergado por decir sí a todo eso, que el director pidió decir en voz alta:** la réplica
(`cola_decisiones.md` §1) es el único ítem cuyo costo de postergación **ya se materializó** —el SSD falló
una vez y hoy emite una sola máquina— y arrastra una fecha: **el pre-registro secuencial necesita §2a-ter
y el MDE firmados antes del 2026-11-19**, siete semanas. «Eso no necesita una corrida, necesita una firma.
Si los encargos 15, 16 y 17 se consumen enteros en las consecuencias del despertar, el 19-nov llega con el
diseño sin congelar.» **Pedirle a Nicolás las dos firmas en paralelo al trabajo de §61, no después.**

## Y una corrección al orquestador sobre no contar el 28-sep

**Correcto, por una razón mejor, y con el costo mal declarado.** La razón buena: para el 28 **no va a
existir la segunda vía** (el sellador entra por divergencia y no persiste meta nuevo), y lo que volvió
creíbles a las cuatro noches fue que dos vías independientes coincidieran ticker por ticker. La razón
escrita —«es la noche contaminada»— es más débil: por el lado de la sonda la noche está limpia. **Y el
costo no es «al menos una semana»: es un día**, porque las noches se acumulan de a una por sesión hábil.
*Las dos cosas corregidas en `bitacora_14.md` 1.7 y en el acta §89.4.*
