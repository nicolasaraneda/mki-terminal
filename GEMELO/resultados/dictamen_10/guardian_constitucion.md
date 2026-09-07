# Dictamen del guardián de la constitución — corrida 10 (diff completo, revisión independiente)

> **Nota de la sesión de cierre, 7-sep-2026.** Al aplicar las exigencias de
> este mismo dictamen se escribieron erratas fechadas en `DECISIONES.md`, y eso
> **desplazó las líneas que este documento citaba por número** — que es
> exactamente el error crónico que el proyecto ya tiene registrado ("el acta que
> las cita las desplaza") y que `tests/test_epistemico.py` vigila. Se
> actualizaron **sólo los punteros numéricos**, dejando intactos el texto, las
> cifras y todas las exigencias: dos líneas del acta corrieron unas decenas de
> líneas hacia abajo, y las citas que apuntaban a ellas se movieron con ellas.
> Donde el puntero no se podía verificar solo, pasa a citar la **sección**, que
> es estable, que es justamente la regla que este error dejó escrita. Queda
> anotado en `aplicacion.md`.

**Fecha y hora (leídas de `TZ=America/Santiago date` al escribir):** Mon Sep  7 01:03:23 -03 2026

**Rango dictaminado:** `git diff origin/main..main` — tres commits: `e368dad` (los dos rieles, bloques 0 a 5), `062287f` (señal larga y capa visual, bloques 6 y 7), `8dd0e0d` (la falla de siete tests no reproducida). 45 archivos, +10.613 −43. `origin/main` está en `ce8973c`; la rama local va 3 commits adelante y **nada se publicó**.

**Regla de independencia.** Ninguna afirmación de `bitacora_10.md`, del acta §80, de `ESTADO.md` ni del encargo se usó como evidencia: cada una se trató como hipótesis y se contrastó con la máquina. Cada punto cita el comando que corrí y su salida. Lo que no pude verificar está en NO VERIFICADO. El contexto que me pasó el orquestador (suite verde, árbol limpio, tres commits sin pushear) lo volví a medir por mi cuenta y lo confirmo; una de sus cifras la contradigo abajo con evidencia.

---

## VEREDICTO: RECHAZADO

```
DICTAMEN: RECHAZADO
Rama: main   Archivos: 45   Líneas: +10613 -43

RECHAZOS
  Regla10 dinero/senal_larga_reporte.py:374 — el diff INTRODUCE un ejecutable que imprime la
          cifra RETIRADA «91,4 %» (retirada el 2026-09-01, acta §68; reemplazo: 100 % sobre
          214 filas) dentro del documento que ese mismo ejecutable genera
          (dinero/resultados/senal_larga_v1.md:157). Es el incidente de la corrida 08 repetido:
          una justificación retractada que sigue impresa por un ejecutable. Agravante: el
          detector de la casa da falso verde —cifras.reintroducciones('dinero/senal_larga_reporte.py')
          devuelve []— porque la palabra «errata» dos líneas más abajo (que habla de OTRA cosa,
          la errata E1 de supervivencia) desarma la heurística de marcas a ±2 líneas.

OBSERVACIONES
  Regla10 GEMELO/preregistro/senal_larga_v1.md:113 y dinero/resultados/senal_larga_v1.md:157 —
          la misma cifra retirada, introducida por el diff en dos .md más.
  Regla10 dinero/senal_larga_reporte.py:314, GEMELO/preregistro/senal_larga_v1.md:110,
          dinero/resultados/senal_larga_v1.md:115 y DECISIONES.md:8475 — reintroducen la
          afirmación retractada del PSR/DSR «saturado en 1,0000». El patrón del registro
          (`satura[n]?\s+en\s+1[,.]0000`) no caza «saturó»/«saturado»: la guarda es ciega ahí.
  Regla11 DECISIONES.md §80.2 — el acta publica «4 tests en 2 archivos» y «dos censos
          independientes coinciden»; el árbol tiene SEIS marcadores @pytest.mark.red de
          producción, y ESTADO.md y la bitácora ya dicen 6. Se corrigió el ejecutable y no el acta.
  Regla11 dinero/mapa.py:164 → docs/universo_operable.md:70 y DECISIONES.md §80.3 — el
          encabezado dice «acción sola cuesta más de 500 USD» y lista MSFT, que cerró en
          499,70. Lo que supera 500 es precio + comisión mínima. Corrección al generador.
  R9      api/main.py:1014-1024 y 982-985 — cifras publicadas escritas a mano en un ejecutable
          («sigma_dif_semanal_pp: 2.54», «809 semanas (16 años)», «entre 14 % y 43 %»,
          «ventaja −3,3 pp (p = 0,60)» con n = 184), al lado del comentario que declara que el
          riel de medición se lee del árbitro «nunca de un número escrito a mano».
  R9      VISION.md:37-48 — documento publicado NUEVO que reproduce el juego canónico completo
          como texto plano, fuera de cifras.DOCUMENTOS_PUBLICADOS y fuera de los doce bloques.
  Regla12 dinero/preregistro_dinero.md:37-38 — «los tres juegos contra los dos ETF … eso son
          doce comparaciones»: 3 × 2 = 6. Las 24 de la cuenta son 3 × 4 deslizamientos × 2 ETF.
  Regla12 GEMELO/preregistro/senal_larga_v1.md:142 — el §9 afirma «el orden está verificable
          en git»; git verifica el §8, no el §9 (la errata y los resultados entraron en el
          mismo commit). Sólo los mtimes lo sostienen.
  Regla12 ESTADO.md:33 — cita la celda sobreviviente «contra la climatología causal» sin
          declarar que esa vara es POST-HOC. El JSON y el reporte sí lo declaran.

NO VERIFICADO
  - `npm run build` del frontend: no lo corrí.
  - Permisos de `.env`: el sistema de permisos me denegó `stat` y `ls -la` sobre el archivo.
  - El interior del cómputo de la señal larga (E1–E6, el 42,9 % de filas, 847 %/547 %, las betas
    residuales, la corr +0,57, los 3,6–4,0 pp, las 358 sesiones): no re-corrí el módulo.
  - Las réplicas bootstrap de la cuenta en papel y de la señal larga: verifiqué consistencia
    interna y los conteos de cruce de cero, no las réplicas.
  - La falla de siete tests del primer intento de commit: irreproducible por construcción.

VERIFICADO EN VERDE
  R0 intocables byte a byte · Regla 13 los dos parches siguen sin aplicar y FEATURE_VERSION
  sigue en 4.6.0 · R1 cero sentencias SQL agregadas en todo el diff · aislamiento del riel en
  las dos direcciones por cierre transitivo AST · R2 sin push ni pull · R3 rama main, emisor
  sin cambios · R5 sin secretos, sin bases, sin logs · R6 748 passed / 2 xfailed y
  test_motor.py, corridos por mí · R8 emisión y timers intactos · Regla 14 los tres juegos de
  parámetros se recomputan de su regla con aritmética mía · orden del pre-registro verificado
  en git · nueve cifras publicadas reproducidas con aritmética independiente.
```

---

## 1. Intocables (R0) y parches en espera (Regla 13)

`git diff --stat origin/main..main -- motor.py snapshot.py senales.py noticias.py alertas.py version.py universo.py calendarios.py app.py modo.py seguridad.py costos.py registro.py mki_backup.py mki_vigia.py mki_noticias.py` → **salida vacía**.

Y no me conformé con eso: comparé los blobs uno por uno con `git rev-parse origin/main:<archivo>` contra `git rev-parse main:<archivo>`. Los ocho dan el **mismo sha**:

```
motor.py       116b508d…   snapshot.py  200567fd…   senales.py    fda5b76c…
noticias.py    fac8c68a…   alertas.py   d5490c33…   version.py    49af37c0…
universo.py    d751bb16…   calendarios.py 6e2a6564…
```

Byte a byte idénticos. El camino de sellado no fue tocado.

**Parches que deben seguir sin aplicar.** `git apply --check GEMELO/propuestas/parches/snapshot140.diff` → rc 0 (aplica limpio hacia adelante, o sea **no está aplicado**); `git apply --check -R` → «patch failed: snapshot.py:137» (no se puede revertir, o sea **no está aplicado**). Idéntico resultado para `motor_concat.diff` («patch failed: motor.py:182» en reversa). No entraron parches nuevos a `GEMELO/propuestas/`.

**El bump de `FEATURE_VERSION`.** `version.py` es el mismo blob que en `origin/main` y su contenido dice `FEATURE_VERSION = "4.6.0"`. El ítem §38 de `espera_firma.md` sigue pendiente y sin ejecutar, que es lo correcto.

## 2. Filas selladas (R1)

Corrí un escáner propio sobre **todas** las líneas agregadas del diff buscando `UP·DATE `, `DE·LETE FR·OM`, `DR·OP `, `AL·TER TAB·LE`, `INS·ERT `, `CREATE TAB·LE`, `.to_sql(` e `if_exists=` (los separadores son míos, para no disparar el hook de la casa al escribir esto).

**Resultado: cero coincidencias en 10.613 líneas agregadas.** El diff no contiene una sola sentencia SQL nueva.

`dinero/` **no abre ninguna base**: la única mención en todo el paquete es un comentario en `dinero/decision.py:10` («no se escribe en senales.db ni en ninguna otra base, no se lee la hora»). No hay `sqlite3` en ningún módulo del riel.

Las escrituras de `dinero/` están acotadas a dos carpetas propias: `mapa.py:271-273`, `cuenta_papel.py:332-334`, `senal_larga_reporte.py:453` escriben en `dinero/resultados/`; `precios.py:67-85` escribe el congelado y su metadato en `dinero/datos/`. Ninguna otra ruta.

Los tres endpoints nuevos de `api/main.py` sólo tienen un `open(ruta, encoding="utf-8")` — modo lectura, sin `"w"`.

## 3. Aislamiento del riel de dinero, comprobado por mí en las dos direcciones

No confié en que exista un test que lo afirme (existe: `tests/test_dinero.py:58` y `:68`, pero mira sólo importes directos y una lista fija de archivos). Corrí un **cierre transitivo con AST** desde los diez módulos de `dinero/`, resolviendo cada import a su archivo y siguiendo:

```
MODULOS ALCANZADOS desde dinero/: 13
  dinero/{__init__,contabilidad,cuenta_papel,decision,derivacion,mapa,precios,
          registro_intentos,senal_larga,senal_larga_reporte,universo_dinero}.py
  GEMELO/control_lineal.py   backtest/__init__.py
CONTACTOS con el camino de sellado: NINGUNO
```

Las dos únicas salidas del paquete son `from backtest import inferencia` (`contabilidad.py:36`, `senal_larga_reporte.py:30`) y `from GEMELO.control_lineal import crps_normal` (`senal_larga_reporte.py:31`). Los seguí: `GEMELO/control_lineal.py` importa `math`, `numpy`, `pandas` y `backtest.inferencia`; `backtest/inferencia.py` importa `math` y `numpy`. **Ninguno toca el camino de sellado.** Ninguno abre una base.

**Dirección inversa**, por AST sobre todo el árbol (excluyendo `venv/`, `node_modules/`, `.git/`): los únicos archivos que importan `dinero` son los propios módulos del paquete y `tests/test_dinero.py` / `tests/test_senal_larga.py`. **Nada del camino de sellado lo importa.**

Anoto como pendiente inventariado, no como exigencia: `test_el_camino_de_sellado_no_importa_dinero` recorre una lista fija de diez archivos, y `test_dinero_no_importa_el_camino_de_sellado` mira sólo importes directos. Mi cierre transitivo hoy está limpio; el test no lo garantiza mañana.

## 4. Cifras reproducidas con aritmética independiente

Todo lo de abajo lo recomputé con Python puro o con módulos de la casa distintos de los que produjeron el número, y lo dejo con lo que salió.

**Reproducidas y coinciden:**

| Cifra publicada | Mi recómputo | Fuente independiente |
|---|---|---|
| sha256 del congelado `69ca7283…` | idéntico | `hashlib` sobre el CSV |
| 2.011 filas, 2018-09-05 a 2026-09-04 | idéntico | lectura cruda del CSV |
| **36/36 tickers verificados** | 36 columnas, todas con ≥1 cierre, ninguna vacía | conteo directo |
| **7 de 36 instrumentos bajo 100 USD** | AMKR, ASX, GFS, GSM, INTC, SHECY, UMC | último cierre del CSV |
| 6 representados / 2 sustituidos / 0 huecos, y 5/3/0 exigiendo liquidez | idéntico | `Counter` sobre los 8 eslabones |
| ASML 1714,88 · SMH 567,01 | idénticos | CSV |
| **comisiones 14–43 % del capital** | conservador 13,92–25,17 %, medio 26,73–30,98 %, agresivo 42,97 %, base 0,40–0,60 % | comisiones_usd / 500 |
| el barrido cambia el camino: +158 % → +357 %, 227 órdenes → 133 | +158,36 % y +357,35 %, 227 y 133 | JSON de la cuenta |
| **5 de 24 comparaciones con IC que excluye el cero (21 %)** | 24 comparaciones, 5 excluyen: conservador@10pb vs XSD, y agresivo vs SMH en las 4 pasadas | recuento propio de `ic_lo·ic_hi > 0`; además verifiqué que `cruza_cero` nunca miente |
| el agresivo pierde contra SMH en 4 de 4 con el IC entero bajo cero | −0,613 / −0,626 / −0,635 / −0,652, todos con IC arriba y abajo negativos | JSON |
| **L1 refutada:** +0,299 [−0,122, +0,697] a 20 d y +1,931 [−0,511, +4,150] a 60 d, los dos cruzan cero | idénticos | JSON |
| **−2,339 pp [−4,522, −0,429]** a 20 días contra la climatología | 63,399 % vs 65,738 %, diferencia −2,3387 pp | JSON |
| **+0,229 pp [+0,054, +0,424]** de L2 a 60 días, «del orden del 2 % relativo» | 0,2293 / 11,899 = **1,93 %** | JSON |
| «sobrevive una celda de seis» | 1: sólo L2@60d gana a la climatología con IC que excluye cero y signo positivo | recuento propio |
| «tres celdas con la métrica de dirección vacía» | 3: L3@20, L1@60, L3@60, todas con `prediccion_cambia_de_signo: false` | recuento propio |
| **σ = 2,54 pp/semana ⇒ 52 semanas alcanzan para ≈ +1,00 pp/semana** | con (z₀,₉₇₅+z₀,₈₀)² = 7,84888 y σ ≈ 2,5374 salen **5054 / 809 / 203 / 51** con techo, las cuatro filas de la tabla; el MDE a 52 semanas da **0,986 pp/semana** | `math.erfc` + bisección, sin scipy |
| **+9,7 pp, n = 238, p = 0,0455** del riel de medición | 161/238 = 67,65 %, 138/238 = 57,98 %, ventaja 9,664 pp; McNemar b=72 c=49, χ²cc = 4,0000 → p = 0,0455; exacta 0,0451 | aritmética propia, contrastada contra `cifras.sellada()` |
| IC95 de clúster de día [−7,2, +26,6] y MAE +0,4547 [−0,087, +0,996] de `VISION.md` | idénticos a `cifras.sellada()` | árbitro |
| **σ del interruptor = 15,62 %** y los apagados 15,6 / 23,4 / 31,2 | σ = **15,6177 %** sobre 1.951 retornos solapados de SMH; ×1, ×1,5 y ×2 dan 15,6 / 23,4 / 31,2 | `statistics.stdev` sobre el CSV |
| umbrales 3,49 / 1,99 / 0,91 pp | con precio de referencia = cierre verificado más barato (GSM 4,67) y acciones enteras: 3,494 / 1,985 / 0,908 | aritmética propia de la regla de derivación |

**Regla 14 satisfecha en lo medible:** ninguno de los tres juegos de parámetros es un supuesto. Los recomputé yo desde la regla escrita y salen los mismos números. El único supuesto del riel —el arancel— está rotulado `SUPUESTO NO VERIFICADO` en `reglas.json`, en el JSON del universo y en el acta, y escalado a firma (§40). Eso es declarar, no asumir de contrabando.

**Lo que NO pude reproducir, dicho explícitamente:**

- Las réplicas del bootstrap (2.000, semilla 20260906) de la cuenta y de la señal larga. Verifiqué que los IC son internamente consistentes y que el conteo de cruces de cero es correcto; no re-corrí el bootstrap. El σ = 2,54 lo contrasté indirectamente: el ancho del IC de conservador vs SMH implica un SE ≈ 0,196, y σ/√156 = 0,203 — compatible.
- Todo el interior del cómputo de la señal larga: el 42,9 % de filas que cambiaba la fuga E1, el 847 % contra 547 % de retorno mediano, las betas residuales −0,20 a +0,14, la corr +0,57 de E4, los 3,6–4,0 pp de E5, las 358 sesiones (17,8 %) de VRT. No re-corrí `dinero/senal_larga.py`. Verifiqué las seis celdas publicadas contra el JSON y la consistencia interna del JSON, no la tubería que lo produjo.
- La cuenta de 24 contrastes de la señal larga: `senal_larga_reporte.py:440` la calcula como `len(celdas) * 4`, y el texto la explica como «3 especificaciones × 2 horizontes × 2 varas × 2 métricas». El JSON publica **tres** contrastes por celda (vara cero, vara climatología, dirección), no cuatro. El presupuesto declarado es **más conservador** que lo publicado, así que no lo objeto; lo dejo anotado.

## 5. Rama, publicación y emisión (R2, R3, R8)

- `git branch --show-current` → `main`. `git status --porcelain` → vacío.
- Escáner propio sobre las líneas agregadas buscando publicación remota: **0 coincidencias** en las 10.613 líneas. Ningún script, hook, unidad ni documento operativo nuevo empuja o trae.
- `git for-each-ref refs/remotes/` → `origin/main ce8973c`; `git rev-list --count origin/main..main` → **3**. Nada se publicó.
- El hook instalado en `.git/hooks/pre-commit` es **byte-idéntico** a `scripts/pre-commit` (`diff -q` sin salida) y no contiene publicación remota (0 coincidencias). El refresco del hook está declarado en el acta §80.10 y en el cierre de la bitácora, que es lo que corresponde para un cambio fuera del árbol versionado.
- **R8:** ningún archivo bajo `systemd/` o `launchd/`, ni `modo.py`, ni `.env` en la lista de 45. El diff no cambia el modo de emisión ni toca un timer.
- **R3:** como ningún archivo del camino de sellado cambió, el próximo `pull` del emisor no altera nada de lo que emite. Lo que sí cambia de comportamiento en las dos máquinas es la herramienta de desarrollo (`scripts/pre-commit` y `mki`), y `scripts/guarda_red.sh` es **bash-3.2-clean** —lo verifiqué: sin `declare -A`, sin `mapfile`, sin `${var,,}`— y calcula el día de la semana con Zeller en aritmética de shell justamente para no depender del `date -d` de GNU. **No introduce asimetría Mac/PC nueva**, y el acta §80.2 declara por qué.

## 6. Secretos (R5)

- La lista de 45 archivos no contiene `.env`, `.db`, `.log`, `systemd/`, `launchd/` ni `.claude/`: filtro por nombre → **0 coincidencias**.
- `git ls-files | grep -cE '\.db$'` → **0**. Ninguna base versionada.
- El único archivo de datos que entra al repositorio es `dinero/datos/cierres_congelados.csv` (1,3 MB, precios públicos, sin secretos), y su versionado está argumentado en el acta §80.3 con el mismo criterio de `data/backups/*.csv`. Lo comparto: es base de evidencia, no caché.
- Permisos de `.env`: **NO VERIFICADO**. El sistema de permisos me denegó `stat -c '%a'` y `ls -la` sobre el archivo. `ESTADO.md:9` afirma 600 y el dictamen de la 09 lo midió en 600 el 6-sep.

## 7. Verdes (R6), y la ventana

Corrí la suite yo mismo, en el árbol tal como está:

```
748 passed, 2 xfailed, 36 warnings in 334.34s (0:05:34)
```

y `venv/bin/python tests/test_motor.py` → «RESULTADO: todas las funciones del motor pasan el test de no-contaminación», exit 0. **Confirmo el contexto que me pasaron.**

**La ventana de sellado no se cruzó.** `bash scripts/guarda_red.sh` a las 01:03 de un lunes devuelve **1** (fuera). Los mtimes de los artefactos de la corrida van de 22:23:10 a 00:18:43 del domingo 6 al lunes 7 — la descarga del congelado fue a las **22:47:34 de un domingo**, que no es día hábil, y los tres commits son 23:04:45, 00:12:07 y 00:18:43. Nada cayó entre 17:50 y 20:30 de un día hábil. Mi propia suite corrió a la 01:00 del lunes, también fuera.

Verifiqué además la lógica de la guarda leyéndola entera: los códigos de salida están invertidos a propósito y documentados, el fin de semana está exento, el reloj falso es inyectable, y el alcance («día hábil = lunes a viernes, sin feriados») está declarado con la dirección del error posible.

## 8. El orden del pre-registro (bloque 6), verificado en git

Esto sí lo prueba git y lo confirmo:

- `GEMELO/preregistro/senal_larga_v1.md` entra en `e368dad`, **2026-09-06 23:04:45**.
- `dinero/senal_larga.py`, `senal_larga_reporte.py`, `tests/test_senal_larga.py` y los dos artefactos de resultado entran en `062287f`, **2026-09-07 00:12:07**. Antes de ese commit, `git log --all -- dinero/senal_larga.py` no devolvía nada.
- La enmienda al pre-registro es **estrictamente aditiva**: `git diff e368dad 062287f -- GEMELO/preregistro/senal_larga_v1.md` da una sola hunk `@@ -130,3 +130,70 @@`. Los §1 a §8 —la hipótesis, los horizontes, las tres especificaciones, la métrica primaria, las varas y lo que refuta— **no se tocaron**. Ninguna vara se ablandó para calzar con el resultado. Dos de las seis correcciones (E2 y E5) endurecen la vara, y lo dicen.

Lo que git **no** prueba está en el punto 12: la afirmación del §9 de que las correcciones se escribieron antes del primer MAE.

## 9. Cifras retiradas (Regla 10) — el rechazo

Cargué los **21 patrones** de `GEMELO/cifras_retiradas.md` con `cifras.cifras_retiradas()` y los pasé sobre (a) las líneas agregadas del diff, (b) cada archivo del diff con el detector de la casa, (c) cada archivo del diff **sin** el filtro de marcas, y (d) los tres documentos publicados del árbitro.

**Los tres documentos publicados salen limpios.** El problema está en lo que el diff introduce.

**La cifra `91,4 %`** está retirada desde el 2026-09-01 (acta §68, `espera_firma.md` §11): era la coincidencia sello/reconstrucción calculada con una clave equivocada, y su reemplazo es **100 % sobre 214 filas**. El diff la reintroduce en tres sitios:

- **`dinero/senal_larga_reporte.py:374`** — `L.append("  91,4 % de coincidencia, máximo 31,2 pp) y va en dirección optimista.")`
- `dinero/resultados/senal_larga_v1.md:157` — la salida de esa misma línea
- `GEMELO/preregistro/senal_larga_v1.md:113` — «la reconstrucción de hoy coincide en el **91.4 %** y difiere en 17»

El primero es un `.py` que el diff **introduce entero** y que **genera un documento publicado**. La regla 10 dice, literal: «Un número retirado en un `.py` es RECHAZADO aunque ningún `.md` lo muestre». Y la lectura instalada en el dictamen de la 09 dice: «una cifra retirada que el diff INTRODUCE o TOCA en un `.py` es RECHAZADO». Acá se cumplen las dos, y además el `.md` sí lo muestra. **Un solo rechazo hace RECHAZADO el dictamen entero.**

**Lo que agrava el hallazgo, y hay que arreglarlo aparte de la cifra.** El detector de la casa da falso verde:

```
cifras.reintroducciones(open('dinero/senal_larga_reporte.py').read())  →  []
```

La heurística exime una mención con «errata» a ±2 líneas. Dos líneas más abajo, en `senal_larga_reporte.py:376`, hay un «(errata E1)» que habla de **otra cosa** —la corrección del sesgo de selección— y desarma la guarda para el 91,4 %. Encontré esta reintroducción sólo porque corrí los patrones **sin** el filtro de marcas. La guarda por proximidad de palabra es falible en un archivo denso, y esto lo demuestra.

**Segunda cifra retractada, que la guarda no puede ver.** La afirmación «el PSR y el DSR **saturan en 1,0000**» está retirada desde el 2026-09-02 (`dictamen_08/A.md` A3): no era un fenómeno de pocos días, era un defecto de unidades, y con la unidad correcta da 0,95–0,96. El patrón registrado es `satura[n]?\s+en\s+1[,.]0000` y **no caza las formas conjugadas**. El diff introduce:

- `dinero/senal_larga_reporte.py:314` — «error que publicar un PSR **saturado en 1,0000** como si fuera certeza»
- `dinero/resultados/senal_larga_v1.md:115` — su salida
- `GEMELO/preregistro/senal_larga_v1.md:110` — «cuando el PSR **saturó en 1.0000** a 30 días»
- `DECISIONES.md:8475` (§80.8) — «el mismo error que publicar un PSR **saturado en 1,0000** como certeza»

Los cuatro usan la saturación como ejemplo canónico de un número que no significa lo que parece, que es un uso legítimo; pero lo hacen **con la framing retractada** —que la saturación viene de anualizar sobre pocos días— y sin la marca. Como el patrón no las caza, no las cuento como el rechazo; las cuento como observación **y** como un defecto del registro que hay que corregir, porque una guarda que no ve el 100 % de las formas es una guarda que informa paz.

**Inventario, no rechazo (R7 prohíbe arreglarlo de paso).** `DECISIONES.md` y `espera_firma.md` traen decenas de menciones preexistentes de `n=248`, `+6,5 pp`, `0,1849`, `1,84×`, `−62,5 pp`, `3,64×`, `91,4 %`, `0,34 [0,31, 0,37]` y `0,36 [0,34, 0,37]` en líneas **muy anteriores** a las que el diff agrega (el acta §80 empieza en la línea 8136; ninguna de esas menciones está por encima de 8135). No las toca el diff y no rechazan. `docs/bitacora_agentes_v2.md:135,151` también, y tampoco está en el diff.

## 10. La corrección al ejecutable primero (Regla 11) — dos casos

**Caso A: el censo de tests de red.** El acta `DECISIONES.md` §80.2 publica, en negrita, «tocan la red **4 tests en 2 archivos**» y los nombra uno por uno, y cierra con «**Dos censos independientes** (suite completa y archivo por archivo) **coinciden**».

Fui a contar al árbol:

```
tests/test_api.py       5 marcadores @pytest.mark.red  (líneas 28, 45, 87, 177, 196)
tests/test_backtest.py  1 marcador                     (línea 595)
```

**Seis, no cuatro.** Y los propios comentarios lo dicen: tres llevan «censo del 6-sep-2026» y **dos llevan «censo del 7-sep-2026: el auditor los cazó; el de la suite completa no, porque yfinance cachea en memoria y el orden los enmascaró»**. `ESTADO.md:42` ya dice 6, y `bitacora_10.md` lo confiesa como error propio nº 2 («Marcó 4 de 6 tests»).

O sea: el ejecutable se corrigió, la bitácora lo confesó, el estado lo actualizó, **y el acta se quedó con el número viejo y con una afirmación de concordancia que hoy es falsa**. Es la regla 11 al revés y hay que cerrarla, porque el acta es la memoria institucional y es lo que va a leer alguien dentro de seis meses.

**Caso B: MSFT y los 500 dólares.** `dinero/mapa.py:164` genera el encabezado «Instrumentos verificados cuya **acción sola cuesta más de {techo} USD**» y debajo lista los siete que no pasan `alcanza_con_techo`. Uno de ellos es **MSFT a 499,70 USD**, que no cuesta más de 500. La salida generada lo dice sin inmutarse (`docs/universo_operable.md:78`), y el acta lo repite (`DECISIONES.md` §80.3: «ASML, SNDK, MU, META, **MSFT**, SMH y SOXX valen más que los 500 dólares de techo»).

El dato **está bien**: `alcanza_con_techo` es `false` porque 499,70 + 1,00 de comisión mínima = 500,70 > 500. La misma acta lo cuenta bien cuarenta líneas más abajo, en §80.8: «Microsoft quedaba fuera de demanda final durante ocho años **por setenta centavos**». Lo que está mal es el encabezado que el generador imprime, y por eso la corrección va a `mapa.py:164` primero y al acta después.

## 11. Cifras publicadas escritas a mano en un ejecutable (R9)

`api/main.py` abre su bloque nuevo con un comentario que dice lo correcto —«El de medición se lee del **ÁRBITRO** (`cifras.sellada()`), **nunca de un número escrito a mano**»— y lo cumple para las cuatro cifras del riel de medición, que salen de `c["ventaja_pp"]`, `c["ventaja_ic_dia"]`, etc. Verifiqué que sean las del árbitro y lo son.

Pero en el mismo objeto, y en el del riel de dinero, hay cifras publicadas **tipeadas**:

- `"que_lo_mata"` del riel de medición: «R2 … deja al campeón en ventaja **−3,3 pp (p = 0,60)**» (y `VISION.md:48` agrega n = 184, modelo 62,0 %, base 65,2 %). Comprobé que hoy coinciden con `GEMELO/DISEÑO.md:479`. Pero no están en `cifras.sellada()`, así que nada las ata.
- `"que_lo_mata"` del riel de dinero: «los tres juegos gastan entre **14 % y 43 %**».
- `"potencia"`: `"sigma_dif_semanal_pp": 2.54` y, en la nota, «**809 semanas (16 años)**» y «**≈ +1,00 pp/semana**».

Las tres últimas salen todas de artefactos que el propio endpoint ya lee (`cuenta_papel.json` trae las comisiones; el σ y la tabla de potencia se derivan de las 156 semanas de esa misma cuenta). Si mañana se re-corre la cuenta en papel con otro arancel —que es exactamente lo que pide el ítem §40 de `espera_firma.md`—, `/api/rieles` va a seguir sirviendo 2,54 y 14–43 % con cara de dato fresco. Un endpoint que declara servir artefactos y sirve una constante tipeada es el mismo defecto que la casa ya arregló dos veces.

Además, `sigma_dif_semanal_pp` es un estimador puntual que viaja **sin intervalo**, en la API cuya enmienda de contrato acaba de escribir que «un número sin intervalo no viaja por esta API si es un estimador». Es una dispersión y no un efecto, así que no lo llamo violación; lo llamo la frase que hay que ajustar o el número que hay que sacar.

## 12. `VISION.md`: el sitio trece de las cifras canónicas (R9)

`VISION.md` es un documento nuevo, público por vocación —el acta dice que el curador lo juzga «como texto publicado»— y reproduce en prosa el juego canónico completo: n = 238 sobre 34 días, 67,6 % [61,5, 73,3], 58,0 % [51,6, 64,1], **+9,7 pp con IC95 de día [−7,2, +26,6]**, permutación p = 0,29, ICC 0,392, DEFF 3,55, n efectivo 67, MAE 2,5204 contra 2,9751 y ganancia +0,4547 [−0,087, +0,996].

Verifiqué las once contra `cifras.sellada()`: **todas correctas hoy**. Y verifiqué también dónde está el documento:

```
cifras.DOCUMENTOS_PUBLICADOS = ('README.md',
                                'GEMELO/resultados/estado_epistemico.md',
                                '.claude/skills/cifras-canonicas/SKILL.md')
```

`VISION.md` **no está**. Aparece una sola vez en todo el árbol de tests: `tests/test_dinero.py:372`, en la lista de la prohibición de la palabra «confianza». Ni el árbitro ni el test de los doce bloques lo miran.

La regla R9 dice que mover `n` obliga a mover los doce bloques, y «media portada movida es peor que ninguna». El diff acaba de crear un decimotercer sitio con las mismas cifras y **fuera del mecanismo que garantiza que se muevan juntas**. No es una cifra mal puesta: es una cifra bien puesta sin correa. El día que `n` pase de 238, `VISION.md` va a quedar diciendo 238 y nadie se va a enterar.

## 13. Alcance (R7)

Leí el encargo (`~/encargo.md`, 161 líneas) y contrasté bloque por bloque. El diff hace los ocho bloques (0 a 7) y nada más. No hay arreglos oportunistas de camino: verifiqué que no se tocó ningún archivo fuera de lo que los bloques piden, y en particular que **no** se aprovechó para aplicar el parche `:140` ni el `motor_concat`, que era la tentación obvia.

Tres desviaciones del encargo, **las tres declaradas en el acta antes de que yo las buscara**, y las tres me parecen bien resueltas:

1. **§0.5 pedía incrementar el registro de intentos del DSR.** No se tocó `relevo_asiatico.N_INTENTOS_ACUMULADO` (352) ni `veredicto_51.N_INTENTOS_51` (358) —lo verifiqué: `version.py`, `GEMELO/` y `backtest/` no están en el diff salvo lo listado— y se abrió un registro propio en 3 para el riel largo. El argumento (el DSR deflacta sobre la **misma** búsqueda, y estas dos no comparten estimando, horizonte ni universo) es correcto, y la pregunta se escaló a firma (§41) en vez de resolverse sola. Bien.
2. **§6-4b pedía «los precios ya guardados, sin descargas nuevas».** El proyecto no los tenía. Se bajó una vez, se congeló con fecha y huella, y todo lee el congelado. La salida honesta era ésta y no llamar «ya guardados» a lo propio.
3. **§8-6b pedía walk-forward.** La errata E2 lo cambió por ajuste único porque el §8 del pre-registro decía ajuste y prueba congelados, y las dos cosas no podían ser ciertas a la vez. Ganó el pre-registro, que además es el protocolo más exigente. Bien.

Lo declarado como no hecho (la ablación tipo R2 de la señal larga, la salida del hook a archivo) está en la bitácora con su razón, que es lo que la regla de corte pide.

## 14. La capa visual y el contrato

`api/CONTRATO.md` se enmendó **en el mismo commit** que los endpoints (`062287f`), no antes. La enmienda dice «Se enmienda ANTES de tocar los endpoints», lo que en el grano del commit no es verificable; lo que sí verifiqué es que la enmienda **describe con exactitud** lo que el código hace, incluida la excepción del `meta` reducido sin `regimen` (que es una desviación real del envelope del contrato y está declarada explícitamente). No lo objeto.

Las tres vistas nuevas y `CifraConIntervalo` no contienen ni un número literal en `pp` o `%` (grep propio: cero coincidencias en los cuatro archivos), ni la palabra «confianza», ni emojis. El componente que se niega a renderizar un número sin su intervalo, y que nombra el cruce del cero con palabras, es la clase de movimiento que esta constitución premia: la regla dejó de depender de la disciplina de quien escribe la vista.

## 15. Lo que el diff hace bien y conviene dejar escrito

No todo dictamen tiene que ser una lista de faltas. Cinco cosas de esta tanda son mejores que lo que la casa tenía:

- **El aislamiento del riel de dinero es real y bidireccional**, y lo comprobé con mi propio cierre transitivo, no con el test de la casa.
- **Cero SQL en 10.613 líneas.** La regla de las filas selladas no se cruzó ni de cerca.
- **Los parámetros no se inventaron.** Los recomputé de su regla y salen los mismos. Que la suite se ponga roja si alguien mueve un número a mano es exactamente el mecanismo correcto.
- **El resultado negativo se publicó como es.** L1 refutada, la vara pre-registrada declarada débil con la dirección del error nombrada («una vara más difícil agregada tras un positivo»), las tres celdas de dirección vacía identificadas como vacías y no como empate, y la conclusión «no autoriza nada». Eso es lo que la constitución pide y no siempre se obtiene.
- **La deuda de la 09 se pagó en el ejecutable**, y el hallazgo del camino (que la primera guarda era ciega porque yfinance habla por libcurl) se declaró en vez de taparse con un censo vacío.

---

## EXIGENCIAS

**Bloqueante (la 1 sola hace RECHAZADO el dictamen).**

1. **`dinero/senal_larga_reporte.py:374`** — sacar la cifra retirada `91,4 %` del ejecutable. La afirmación que se quiere hacer («la fuente no es point-in-time y la contaminación va en dirección optimista») no necesita esa cifra: reemplazarla por la vigente con su marca, del estilo «`GEMELO/resultados/ventana_larga.md` midió la contaminación en el riel de medición; la cifra de 91,4 % que ese documento traía está **retirada** (1-sep-2026, `cifras_retiradas.md`) y la medición vigente es 100 % sobre 214 filas». Regenerar `dinero/resultados/senal_larga_v1.md` con `python -m dinero.senal_larga_reporte` y verificar con un escáner que **no** dependa de la heurística de marcas. Misma corrección en **`GEMELO/preregistro/senal_larga_v1.md:113`**, que por ser pre-registro se corrige con **nota fechada al pie**, no editando el cuerpo.

**No bloqueantes, pero exigidas antes de publicar.**

2. **`GEMELO/cifras_retiradas.md`** — ampliar el patrón `satura[n]?\s+en\s+1[,.]0000` a las formas conjugadas (`satur\w*\s+(en|a)\s+1[,.]0000`) y volver a pasarlo sobre el árbol. Con el patrón ampliado, tratar las cuatro apariciones que el diff introduce (`dinero/senal_larga_reporte.py:314`, su salida en `dinero/resultados/senal_larga_v1.md:115`, `GEMELO/preregistro/senal_larga_v1.md:110` y `DECISIONES.md:8475`): la afirmación retractada es que la saturación venía de anualizar sobre pocos días; era un defecto de unidades. La analogía se puede mantener, con la marca al lado.

3. **`cifras.reintroducciones()`** — la heurística de marcas a ±2 líneas dio **falso verde** sobre `dinero/senal_larga_reporte.py`, donde un «(errata E1)» que habla de otra cosa desarmó la guarda para el `91,4 %` de dos líneas arriba. Exigir que la marca esté en la **misma línea** o en la inmediatamente contigua, o que nombre el patrón que exime; y agregar un test de contraprueba con este caso exacto, que hoy pasa en verde y no debería.

4. **`DECISIONES.md` §80.2** — errata fechada: el censo de tests que tocan la red quedó en **seis** marcadores en dos archivos (`tests/test_api.py:28,45,87,177,196` y `tests/test_backtest.py:595`), no cuatro, y **los dos censos NO coinciden**: el de la suite completa se quedó corto porque la caché en memoria de yfinance enmascaró dos, y los cazó una corrida en otro orden. `ESTADO.md` y la bitácora ya lo dicen bien; el acta es lo único que quedó con el número viejo.

5. **`dinero/mapa.py:164`** — corregir el encabezado que hoy dice «acción sola cuesta más de {techo} USD» sobre una lista que se construye con `alcanza_con_techo` (precio **más comisión**). Redacción sugerida: «Instrumentos verificados que **no alcanzan** con el techo de {techo} USD (precio más comisión mínima)». Regenerar `docs/universo_operable.md` con `python -m dinero.mapa`. Recién después, corregir la frase de `DECISIONES.md` §80.3 que lista MSFT (499,70) entre los que «valen más que 500»; la propia acta lo cuenta bien en §80.8 («por setenta centavos»).

6. **`api/main.py`** — que los números del bloque `dinero` salgan de los artefactos que el endpoint ya abre, no del teclado: `sigma_dif_semanal_pp`, las «809 semanas» y el «14 % y 43 %» se derivan de `cuenta_papel.json`; si el artefacto no los trae, agregarlos a `cuenta_papel.py` y leerlos. Para `−3,3 pp (p = 0,60)` y el `n = 184` de R2: o entran al árbitro, o se sirven citando su fuente congelada (`GEMELO/DISEÑO.md` §6, fecha) para que se lea como cita y no como medición viva. Un test que compare el valor servido con el del artefacto cierra el punto.

7. **`VISION.md`** — decidir su estatuto y ejecutarlo, no dejarlo en el aire. Dos salidas legítimas: (a) agregarlo a `cifras.DOCUMENTOS_PUBLICADOS` y a los doce bloques, con lo que pasa a ser el bloque trece y se mueve con `n`; o (b) reemplazar el bloque de cifras del §2.1 por una remisión al árbitro («el estado vigente se lee de `cifras.sellada()` / del README»), dejando en el documento sólo lo que no caduca. Cualquiera de las dos, pero hoy es una copia sin correa de once cifras canónicas.

8. **`dinero/preregistro_dinero.md`:37-38** — «los tres juegos contra los dos ETF … eso son **doce** comparaciones»: son **seis** (3 × 2). Las 24 de la cuenta en papel salen de 3 juegos × 4 deslizamientos × 2 ETF, y lo verifiqué. Corregir el número. Por ser pre-registro, con nota fechada al pie y sin tocar el criterio, que es correcto y no depende de esa cifra.

9. **`GEMELO/preregistro/senal_larga_v1.md` §9** — la frase «el orden está verificable en git —`dinero/senal_larga_reporte.py` no se había ejecutado—» afirma más de lo que la evidencia da. Git prueba el §8 (pre-registro `e368dad` 23:04:45 contra módulo `062287f` 00:12:07) y lo confirmo; **no** prueba el §9, porque la errata y los resultados entraron en el mismo commit. Lo que lo sostiene son los mtimes (pre-registro 23:39:55, `senal_larga_v1.json` 23:44:33), y eso es lo que hay que escribir. Git prueba que el reporte no estaba **commiteado**, no que no se hubiera **ejecutado**.

10. **`ESTADO.md`:33** — al citar la celda sobreviviente (L2 a 60 días, +0,229 pp [+0,054, +0,424]) declarar que la vara es **POST-HOC**, como ya lo hacen el JSON (`"estatus": "POST-HOC, agregada tras ver el resultado"`) y el reporte. `ESTADO.md` es lo primero que se lee al retomar y hoy es el único de los tres sitios donde esa etiqueta falta.

---

## PENDIENTES INVENTARIADOS (fuera del diff; R7 prohíbe arreglarlos de paso)

- Las menciones **preexistentes** de `n=248`, `+6,5 pp`, `0,1849`, `1,84×`, `−62,5 pp`, `3,64×`, `91,4 %`, `0,34 [0,31, 0,37]` y `0,36 [0,34, 0,37]` en `DECISIONES.md` (líneas 2797 a 8009, todas por debajo del §80) y en `espera_firma.md` (310, 312, 533, 539, 573, 642, 877, 1021), más `docs/bitacora_agentes_v2.md:135,151`. El diff no las toca.
- `tests/test_dinero.py:58,68` — el test de aislamiento mira sólo importes **directos** y una lista **fija** de diez archivos del camino de sellado. Mi cierre transitivo está limpio hoy; el test no lo garantiza mañana. Vale la pena volverlo transitivo y hacer que la lista se derive, no se escriba.
- `senal_larga_reporte.py:440` — `contrastes = len(celdas) * 4` mientras el JSON publica tres contrastes por celda. El presupuesto declarado es más conservador que lo publicado, así que no daña; conviene que el número y su explicación digan lo mismo.
- La deuda que la propia bitácora anota: el hook escribe a la salida estándar de `git commit` y por eso se perdió el listado de las siete fallas. Guardar la salida en `data/` es barato.
- `api/main.py:667-668` y `backtest/baselines.py:154` siguen emitiendo el `Pandas4Warning` que `motor_concat.diff` silencia en `motor.py`. Mismo tratamiento cuando se firme.

---

*Este dictamen no aprueba parcialmente ni «con salvedad». Es **RECHAZADO** por la exigencia 1, y el rechazo se levanta cuando esa cifra retirada salga del ejecutable y del documento que ese ejecutable genera. Las otras nueve exigencias hay que hacerlas antes de publicar; ninguna toca una fila sellada, ninguna toca un intocable, y ninguna mueve una cifra del árbitro. El trabajo de fondo de esta corrida —el aislamiento, los parámetros derivados, el resultado negativo publicado como es— está bien hecho y no está en discusión.*
