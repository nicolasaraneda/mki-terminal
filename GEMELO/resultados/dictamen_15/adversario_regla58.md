# Dictamen del `estadistico-adversario` sobre `GEMELO/propuestas/regla_58.md`

> Archivado por el orquestador tal como lo devolvió el agente (no escribe archivos). Lanzado a
> las 22:18 de Chile del 29-sep-2026 sobre la primera versión del documento; devuelto a las
> 22:30:52 (hora de `date` del agente). La primera parte es ese dictamen. El re-dictamen sobre la
> versión revisada va al final, con su propia hora. Qué se hizo con cada exigencia está en
> `GEMELO/resultados/bitacora_15.md`, sección 1.

---

## PRIMER DICTAMEN (sobre la versión de las 22:18)

## 1. Veredicto

**APTA CON EXIGENCIAS.** La columna vertebral es correcta y no se toca: pre-registro antes del dato, una sola lectura, la noche censurada se queda en el denominador, (c) no se autoelige, `n_X` no indica nada. Los diez bloqueantes que siguen son **grados de libertad abiertos y dos cifras que no reproduzco**, todos cerrables con texto. No propongo rediseño.

El supuesto que me pidieron demostrar **se sostiene**: con el dato ya visto se puede llegar a la opción preferida por dos caminos que el texto no cierra — (i) la **convención de estimador** con que se lee la tasa de rescate (punto contra límite inferior de Wilson) invierte el signo de la conveniencia de (b); (ii) **V2/V3 y la cláusula de concordancia sacan del denominador o bloquean la decisión justo en las noches más informativas**, y las tres salidas caen en (a).

## 2. Tabla de cifras recomputadas

Módulo: `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py` (self-test en verde, reproduce 161/238 → [61.5, 73.3] y 138/238 → [51.6, 64.1] del README).

| § | cifra del documento | mi valor | ¿coincide? |
|---|---|---|---|
| 2 | Wilson x/10, las 22 celdas (0,0/27,8 … 72,2/100,0) | idénticas, 22 de 22 | **SÍ** |
| 2 | McNemar exacto b=3, c=0 → p = 0,25 | 0,250000 | **SÍ** |
| 2 | McNemar exacto b=5, c=0 → p = 0,0625 | 0,062500 | **SÍ** |
| 2 | McNemar exacto b=6, c=0 → p = 0,0313 | 0,031250 | **SÍ** |
| 2 | P(X≥3 \| n=10, p=0,25) = 0,47 | 0,4744 | **SÍ** |
| 2 | … p=0,10 → 0,07 | 0,0702 | **SÍ** |
| 2 | … p=0,40 → 0,83 | 0,8327 | **SÍ** |
| 4 | umbral = menor x/10 con Wilson inf > 10 % → 3, [10,8 · 60,3] | x=3, [10,8 · 60,3] | **SÍ** |
| 4 | con 20 noches el umbral son 5 | x=5, [11,2 · 46,9] | **SÍ** |
| 4 | 41,3 sesiones sin rescate | 31/0,75 = 41,33 | **SÍ** |
| 4 | 36,5 con rescate | 31/0,85 = 36,47 | **SÍ** (usa rescate 10 pp redondeado; con 10,78 pp exacto da 36,1) |
| 0 | Wilson 3/12 = [8,9 · 53,2] | [8,9 · 53,2] | **SÍ**, dado n=12 |
| 0 | **12 sesiones selladas por un disparo entre 23:30 y 23:38 NY** | **11** | **NO** → E1 |
| 0 | 3 `insumo_incompleto` (18, 22, 23-sep) | 3, esas tres | **SÍ** |
| 3 | 33 operables sellados | 33 tickers distintos en `sellos_dinero` | **SÍ** |
| 3 | los 3 que sobran = ARM, ASML, SNDK | 36 en la sonda − 33 sellados = {ARM, ASML, SNDK} | **SÍ** |
| 3 | SHECY y TOELY entre los 33; SMH, SOXX, XSD entre los 33 | los cinco están | **SÍ** |
| 2 | sesión nº 20 desde el 29-sep = 26-oct-2026 | `XNYS` → 2026-10-26 (lun) | **SÍ** |
| 5.2 | 4 de las 20 tienen día siguiente sin sesión | 4: 2, 9, 16 y 23-oct (viernes) | **SÍ** (12-oct Columbus es sesión) |
| 2 | cambio de hora NY el 1-nov; toda la ventana Chile = NY + 1 h | 26-oct: NY −04, Chile −03; 2-nov: NY −05 | **SÍ** |
| 0 | tabla descriptiva, 5 noches × 3 columnas (15 celdas) | reconstruida del CSV filtrado: 15 de 15 | **SÍ** |
| 0 | 29-sep: dos obs. de tarde, 1 de 36 en las dos; una fuera de grilla 17:38 NY | 20:05 → 1/36, 20:35 → 1/36; 17:38:57 NY fuera de los 16 casilleros | **SÍ** |
| 0 | 28-sep sin segunda vía, `no_verificable_timing` a las 13:43 NY | sello 13:43:01 NY (sonda 13:42:55) | **SÍ** |
| 5.2 | emisión 01:00 NY del sábado → `dia_sin_sesion` | funciones puras: `dia_en_calendario_del_exchange`=2026-10-03, `es_sesion`=False | **SÍ** |
| 6 | `man systemd.timer` documenta el disparo inmediato sólo para `Persistent=true` | cita textual verificada, systemd 259.5 | **SÍ** |
| 6 | H-A, base 29-sep 00:35 Chile + calendario nuevo → 29-sep 01:05 Chile | 01:05 (`Tue..Sat 00..03:05,35`) vs 21:05 (`Mon..Fri 20..23:05,35`); mín = **01:05** | **SÍ** |
| 6 | **con el calendario VIEJO da 21:05, futuro** | el viejo era `Mon..Fri 17..23:05,35` (git `fa7b5ba`) → **18:05 Chile, ya pasado** | **NO** → E8 |
| 6 | H-B, base 20-sep 02:05:59 → 21-sep 21:05 | con el calendario real de entonces → 21-sep **18:05**; la conclusión (ya pasado) sobrevive, la cifra no | **NO** (parcial) → E8 |
| 6 | sellador: base 29-sep 00:30 Chile + `Tue..Sat 01:00 NY` → 29-sep 02:00 Chile | 02:00 Chile | **SÍ** |
| 6 | `InactiveExitTimestamp` = 20-sep 02:05:59 | es el valor de los **siete** timers hermanos; el de la sonda ya fue sobrescrito a 29-sep 18:38:57 | **SÍ pero inferido** → E14 |
| 6 | sonda `Persistent=false`; sellador `Persistent=yes`; último disparo del sellador 29-sep 00:30 | `Persistent=no` / `yes`; `LastTriggerUSec=Tue 2026-09-29 00:30:00 -03` | **SÍ** |
| — | contador E0 = 9, faltan 31 para N=40 (implícito en §4) | `COUNT(DISTINCT fecha_insumo) WHERE cuenta_para_N=1` = 9 | **SÍ** |
| — | `divergencias_sello` = 2, máx 2026-09-28 | 2, máx 2026-09-28 | **SÍ** |
| 3 | los 9 casilleros exigidos son exactamente los que flanquean las 8 candidatas | verificado candidata por candidata: 23:35 + 8 de madrugada, ni uno de más | **SÍ** |
| 4 | 03:30 NY deja 6 h antes de las 09:30 NY; ninguna candidata en 17:50–20:30 Chile | 6 h; candidatas = 01:00–04:30 Chile | **SÍ** |

Comandos (todos con `venv/bin/python`, bases en `mode=ro`):

```
venv/bin/python .claude/skills/estadistica-evaluacion/scripts/evaluacion.py
# wilson_ci(x,10) x=0..10 ; mcnemar_exact(b,0) b=3,5,6 ; wilson_ci(3,12) ; wilson_ci(5,20)
sqlite3 'file:dinero/sello_dinero.db?mode=ro'  -> SELECT fecha_insumo, MIN(timestamp_utc), estado ... GROUP BY fecha_insumo
exchange_calendars XNYS sessions_in_range('2026-09-29','2026-12-31')[:20]
dinero.sello_dinero.{dia_en_calendario_del_exchange,es_sesion,proxima_sesion_despues_de}   # sin base, sin red
systemd-analyze calendar --base-time='2026-09-29 00:35:00' '<expr>'                        # no toca unidades
systemctl --user cat / show   +   git log -p -- GEMELO/propuestas/systemd/mki-sonda-cierre.timer
data/sonda_cierre.csv leído con filtro `timestamp_utc < 2026-09-30T04:00:00Z` aplicado ANTES de imprimir
```

**Nota de lectura del CSV:** la última fila que existe bajo el corte es `2026-09-30T01:05:00Z` (21:05 NY, 1/36), una observación **posterior** a la que §0 declara como última leída (`00:35Z`). No es una discrepancia del documento: nació después de que se escribiera. La declaro para que el acta no la lea como errata.

**Análisis dimensional de cada argumento** (mandato del 2-sep): `wilson_ci(k, n)` — k y n **conteos de noches**, no proporciones; devuelve **proporciones** (las convertí a pp al imprimir). `mcnemar_exact(b, c)` — b y c **conteos de desacuerdos de noches**, no de filas-ticker. Binomiales: p **proporción por noche**, n **noches**, adimensional. Sección 4: `31` es **sesiones que faltan** (conteo), `0,25` **proporción por noche**, `41,3` y `36,5` **sesiones-calendario**; la división es conteo/adimensional → conteo, correcta. `n_filas_respuesta` **no es un conteo de tickers**: es `len(cierres)` = **filas-fecha de la descarga**, y vale **7** en las 45 observaciones bajo el corte (ver E5). Ningún Sharpe, PSR, DSR ni varianza entra a este documento, así que el incidente de la corrida 08 no tiene superficie acá.

## 3. Exigencias

### BLOQUEANTES

**E1 — El denominador del antecedente son 11 noches, no 12, y la ventana que lo define no es la ventana que la regla usa.**

*Qué dice el texto* (§0): «de las **12** sesiones selladas por un disparo entre las 23:30 y las 23:38 NY (8, 10, 11, 14, 15, 16, 17, 18, 21, 22, 23 y 24-sep), **3** quedaron `insumo_incompleto` … Wilson 95 % para 3/12: **[8,9 · 53,2] %**».

*Por qué está mal.* Medido en `dinero/sello_dinero.db` (`mode=ro`), el sello del **8-sep es 23:38:17,156 NY**: fuera de `[23:30, 23:38]` por 17 s, y **+497 s** de la grilla del timer, cuando **los once restantes caen entre +4,0 s y +5,0 s** de las 23:30:00. No es un disparo del timer de las 23:30; es la primera fila del riel. Peor: la **ventana de V3 que la propia regla define** es `[23:30:00, 23:34:59]`, y bajo ella el 8-sep tampoco entra. Las dos lecturas dan **11**. El 8-sep es un `pendiente`, así que incluirlo **baja** la tasa de 27,3 % a 25,0 % y **angosta** el intervalo: la única cifra del documento que no reproduzco es la que hace ver más benigna la hora actual. Simétricamente, el 9-sep — `insumo_incompleto` — queda fuera por el filtro (20:00:04 NY, timer viejo de 21:00 Chile): correcto, pero no está dicho que lo excluido es un incompleto, y con él serían 4/13 = 30,8 % [12,7 · 57,6]. Tres denominadores legítimos, tres tasas, ninguna convención escrita.

*Texto de reemplazo* del párrafo de §0 que empieza «Y del riel de dinero»: (incorporado en la versión revisada, sección 0.)

**E2 — El umbral de 3 está por debajo del punto de empate para TODAS las candidatas que la regla puede elegir, y el documento no cruza sus propias dos secciones.**

*Qué dice el texto.* §4: «**El umbral es el mismo en todas las ramas: 3 noches de 10** … ». §5.2: «**Con el código vigente, toda candidata de esta regla perdería todas las sesiones de viernes y de víspera de feriado** (4 de las 20 sesiones del plazo tienen un día siguiente sin sesión).»

*Por qué está mal.* Las dos son ciertas por separado y **nadie las suma**. Las ocho candidatas son 00:00 a 03:30 NY: **todas posteriores a la medianoche**, así que la pérdida de viernes se aplica a la totalidad del espacio elegible, no a un subconjunto. Con la contabilidad del propio §4 (rescate = límite inferior de Wilson de 3/10 = **10,8 pp**, unidad: proporción de noches; pérdida base 25 %; unidad de salida: **noches que cuentan por semana**):

| | noches con disparo/sem | tasa de pérdida | cuentan/sem |
|---|---|---|---|
| (a) hoy | 5 | 0,250 | **3,750** |
| (b) post-medianoche, con rescate 10,8 pp | 5 × (1 − 4/20) = **4** | 0,142 | **3,432** |

**(b) es peor.** Con la tasa corregida de E1 (27,3 %): 3,636 contra 3,341, también peor. El rescate **mínimo para empatar** es `r = (1−t)/4` = **18,8 pp** (18,2 pp con 3/11), y el menor x de 10 cuyo límite inferior de Wilson lo supera es **x = 5** (23,7 %), **no 3**.

Y acá está el grado de libertad que buscaba: con el **estimador puntual** (3/10 = 30 pp) en vez del límite inferior, (b) pasa a **4,000 contra 3,750** y gana. **El documento usa el límite inferior para justificar el umbral y nunca dice que la conveniencia de (b) se invierte según qué estimador se enchufe.** Con el dato en la mano, cualquiera elige el estimador que le da la respuesta que quiere.

*Texto de reemplazo* (incorporado en la versión revisada, sección 4: convención de límite inferior, tabla de contabilidades, umbral 5 con el código vigente y 3 sólo si el acta evita la pérdida de viernes).

**E3 — Un Wilson sobre el máximo elegido entre ocho candidatas no es un intervalo del 95 %, y la multiplicidad no está declarada.** Son **ocho** comparaciones. `R(t)` sería monótona en `t` si los cierres sólo aparecieran, pero §8.2 y el hallazgo de la corrida 13 dicen que **desaparecen**, y §3 ordena contarlos como ausentes: entonces `R(t)` **no es monótona** y el máximo sobre ocho es un máximo genuino. `R(t*)` es un **estadístico seleccionado**: su Wilson es anticonservador y su cobertura no es 95 %. El documento tampoco publica los `R(t)` de las otras siete. *Texto de agregado* (incorporado en la versión revisada, sección 4.1).

**E4 — «Una sola lectura» y «otras diez noches» se contradicen.** Es extensión de muestra **decidida después de ver el resultado**, con el mismo α y el mismo criterio de umbral. Es el mecanismo clásico por el que un resultado nulo se convierte en positivo sin que nadie mienta. *Texto de reemplazo* (incorporado: segunda lectura declarada, umbral 5 sobre 20, sin tercera lectura).

**E5 — V2 borra del denominador exactamente la noche de apagón total, y `n_filas_respuesta` no es lo que el texto insinúa.** (i) **Dimensional:** `n_filas_respuesta` es `len(cierres)` en `GEMELO/sonda_cierre.py:162` — **filas-fecha de la descarga (`period=7d`)**, no filas-ticker. Vale **7** en las 45 observaciones bajo el corte. (ii) **Sustantivo:** el apagón **total** (0 filas-fecha) SÍ es distinguible y V2 lo manda a **noche inválida**, fuera de K. El apagón **parcial** no es distinguible, V2 pasa, y la noche cuenta como incompleta. Resultado: la noche que más informa sobre la opción (b) desaparece del denominador si el corte de la fuente pegó en cualquiera de los nueve casilleros. *Texto de reemplazo:* contar `n_O` aparte con su Wilson y «NO DECIDIBLE» si `n_O ≥ 3`. (El orquestador lo resolvió de otro modo: ver re-dictamen.)

**E6 — V3 cuelga de un artefacto que un job que esta misma corrida está cambiando puede no producir.** `data/backups/sello_dinero.csv` y `mki_backup.py` (§90.8) más `snapshot.py` (§90.1 b): fuente atrasada → snapshot no sella → backup no commitea → no hay fila en el CSV → V3 falla → noche inválida. La base `dinero/sello_dinero.db` tiene la fila desde el segundo cero. *Texto de reemplazo:* la base como fuente primaria. (Incorporado, con una corrección de hecho: ver re-dictamen.)

**E7 — La concordancia castiga el fenómeno que §3 declara esperado, y con dos noches manda todo a (a).** La contención es en un solo sentido; la desaparición discordaría, y es precisamente lo que el proyecto midió (corrida 13) y lo que §3 ordena tratar como normal. *Texto de reemplazo* (incorporado: cuatro clases, discordante sólo si incomparables, los conteos con su Wilson, qué pasa después de un NO DECIDIBLE).

**E8 — §6 afirma una discriminación entre H-A y H-B que la máquina contradice: el «21:05» no sale de ningún calendario que existiera.** El calendario **viejo** era, según `git log -p -- GEMELO/propuestas/systemd/mki-sonda-cierre.timer` (commit `fa7b5ba`), `Mon..Fri 17..23:05,35 America/New_York`. Con él, `--base-time='2026-09-29 00:35:00'` da 29-sep 18:05 Chile, ya pasado a las 18:38:57. (El orquestador la rechazó con evidencia: el calendario INSTALADO era `20..23`; ver re-dictamen.)

**E9 — Ningún umbral, ninguna afirmación de potencia y ningún intervalo de este documento se corrió contra `GEMELO/simulador/`.** Las tres binomiales SÍ se cierran analíticamente. Lo que no cierra ninguna cuenta en papel es la característica operativa de la regla COMPUESTA: máximo sobre 8 candidatas + `P(t) = 0` con tolerancia cero + umbral 3 + interruptor de concordancia + invalidación V1–V4. `GEMELO/simulador/` no tiene módulo para un instrumento Bernoulli por noche con selección sobre candidatas: hay que extenderlo. *Texto de agregado* (incorporado en la sección 7).

**E10 — El casillero de las 23:35 de la primera noche candidata es legible 25 minutos antes del sellado de este documento.** Se escribe a las 03:35Z = 00:35 de Chile, por debajo del corte de 04:00Z. La frase de §0 lo cubre por promesa, y una promesa sobre el futuro escrita en el documento que se sella no es verificable después. *Texto de reemplazo:* publicar la clasificación con y sin la noche del 29-sep. (El orquestador lo resolvió por la hora del sello: ver re-dictamen.)

### RECOMENDADAS

**E11 — V1 y V2 no borran noches al azar; declararlo en §8.** (Incorporado: limitación 8.)

**E12 — V4 permanente nunca alcanza K.** (Incorporado en V4.)

**E13 — Instante exacto de evaluación, y el plazo extendido con medias sesiones.** (Incorporado en la sección 2.)

**E14 — Provenance del `InactiveExitTimestamp`.** El `restart` de las 18:38:57 sobrescribió el valor de la sonda; `20-sep 02:05:59` es el valor que comparten los otros siete timers. (Incorporado, con el dato del journal: `Started mki-sonda-cierre.timer` el 20-sep 02:05:59.)

**E15 — `P(t) = 0` es un veto de tolerancia cero sobre una observación.** (Incorporado: se informa qué operable y en cuál casillero faltó.)

**E16 — La línea de intentos nombra sus registros.** 0 es correcto en los dos registros. (Incorporado en la cabecera.)

**E17 — Yo mismo sumo al registro de intentos, por el mandato de §28.** Hipótesis juzgadas esta noche: **(H1)** que 3/12 = 25 % es la tasa antecedente → NO SOSTENIDA (son 3/11 = 27,3 %, E1); **(H2)** que un umbral de 3 de 10 dimensiona el cambio de hora → NO SOSTENIDA para toda candidata post-medianoche con el código vigente (E2); **(H3)** que el evento de las 18:38 discrimina H-A de H-B → NO SOSTENIDA (E8). Las tres son hipótesis sobre disponibilidad e instrumentación, no sobre retornos: no suman al DSR de ninguna familia.

## 4. Lo que NO pude verificar, y por qué

1. **Nada de la franja de madrugada.** Ninguna fila con `timestamp_utc ≥ 2026-09-30T04:00:00Z` fue abierta: el filtro se aplicó dentro del código, antes de imprimir, en las tres lecturas del CSV. Nunca usé `tail` ni `cat` sobre `data/sonda_cierre.csv` ni sobre `data/sonda_cierre.log`.
2. **La promesa de §0 de no haber reabierto el CSV** entre las 22:03:51 y el sellado: es una afirmación sobre la conducta del orquestador, no reconstruible desde artefactos.
3. **H-A contra H-B, definitivamente:** separarlas exige reiniciar una unidad. Prohibido, y correctamente prohibido.
4. **La característica operativa de la regla compuesta**: no existe el módulo de simulador que la mida (E9).
5. **`n_O` (apagones totales) histórico:** en las 45 observaciones bajo el corte, `n_filas_respuesta` vale 7 en todas; nunca 0. No hay ni un apagón total en el registro.
6. **No abrí `dinero/sello_dinero.db` después de las 00:15 Chile**: todas las consultas se hicieron entre 22:20 y 22:30 Chile, siempre con `file:…?mode=ro`.
7. **No escribí ni modifiqué ningún archivo, no toqué systemd, no corrí la suite ni ningún job, no leí `.env`**, y no usé ningún SQL que no fuera `SELECT`.
8. **Cantidad que me niego a ordenar:** no afirmo si el rescate real está por encima o por debajo del punto de empate de 18,2 pp. Lo que sí afirmo es que **el umbral escrito (3) está por debajo de ese punto de empate**.

## 5. Hora de cierre

`TZ=America/Santiago date` → **Tue Sep 29 22:30:52 -03 2026**. Dentro del plazo de las 23:20.

**Resumen para el sellado:** de 38 cifras y afirmaciones verificables del documento, **35 reproducen exactas** y **3 no** (el 12 de §0 → E1; el «21:05 con el calendario viejo» de §6 → E8; y el «21-sep 21:05» de H-B, misma causa). Los dos grados de libertad que permitirían llegar a la opción preferida con el dato ya visto son **E2** (la convención de estimador) y **E5 + E6 + E7** (tres caminos por los que la noche más informativa sale del denominador o bloquea la decisión). Cerrados con el texto propuesto, el documento es una regla y no un menú.

---

## RE-DICTAMEN (sobre la versión revisada de las 22:40, con el corte de cuota en el medio)

Pedido enviado por el orquestador a las 23:01 de Chile; devuelto a las **23:05:16** (hora de `date` del agente).

### (b) Resoluciones del orquestador distintas de mi texto

**Resolución 1 (E8): ACEPTADA. Tenía razón el orquestador y yo estaba equivocado. Retiro E8.** Verificado en el CSV bajo el corte: las noches del 21 al 24-sep tienen exactamente 8 observaciones cada una, la primera a las 20:05 NY y ninguna entre las 17:00 y las 19:59; `Mon..Fri 17..23:05,35` habría dado catorce. La máquina estaba despierta en esa franja (`mki-vigia` a las 19:00 y el re-chequeo a las 20:30), así que la ausencia no se explica por suspensión. Mi error fue tomar la plantilla del repo por la unidad instalada. El «21:05, futuro» es correcto y H-A no queda excluida. Que la consecuencia operativa severa se haya conservado igual es lo correcto.

**Resolución 2 (E5): ACEPTADA EN PRINCIPIO, mejor que mi texto, con un agujero residual (E18).** «Una noche es inválida sólo cuando la máquina no miró» evita el problema de raíz. Verificado el mecanismo: `dinero/sello_dinero.py:341` levanta `RuntimeError` con descarga vacía, así que `C = 0` es el análogo fiel. Pero si el sellador revienta a las 23:30 no hay filas, y V3 (que exige filas con `estado` en {`pendiente`, `insumo_incompleto`}) invalida igual: la misma puerta, un metro más allá.

**Resolución 3 (E6): ACEPTADA. Yo estaba equivocado en el hecho.** `exportar_csv()` (línea 640) la llama `main()` en las líneas 752 y 756: el sellador escribe el CSV, `mki_backup.py` lo commitea. Mi cadena «backup no commitea → no hay fila en el CSV» no ocurre en disco.

**Resolución 4: CORRECTA.** Rescatar no puede exceder la pérdida; topar el puntual en 27,3 pp da 4,00 y el signo se invierte igual.

### (c) Cifras nuevas: todas recomputadas con `evaluacion.py`, todas reproducen

3/11 [9,7 · 56,6]; 3/12 [8,9 · 53,2]; 4/13 [12,7 · 57,6]; 5/10 [23,7 · 76,3]; 5/20 [11,2 · 46,9]; 3/10 [10,8 · 60,3]; 0/10 [0,0 · 27,8]; (a) 3,6364; (b) todas 3,3411; (b) lun-jue + viernes 4,0684; puntual topado 4,0000; empate 18,18 pp; x = 5; 42,6 / 37,1; plazo 26-oct o 27-oct según la hora del sello; 4 viernes en los dos escenarios; las dos fechas antes del 1-nov. Lo único que no reproduce es una afirmación, no una cifra: E20.

### (a) Estado de las diez bloqueantes

E1 CERRADA; E2 CERRADA en sustancia con dos residuos (E19, E20); E3 CERRADA; E4 CERRADA; E5 CERRADA para la sonda, ABIERTA para la hora del sellador (E18); E6 CERRADA; E7 CERRADA; E8 RETIRADA (error mío); E9 CERRADA; E10 CERRADA, y mejor que mi texto (la hora del sello decide la primera noche, sin promesa). Las recomendadas E11 a E16 entraron.

### Exigencias nuevas

**E18 (BLOQUEANTE).** V3 mata la noche de apagón total en la hora del sellador, contra el principio de validez. Texto: el principio pasa a «ninguna noche se invalida por lo que la fuente hizo; sólo por lo que la máquina o el instrumento no hicieron», y V3 gana el caso previsto: si el sellador disparó a su hora y falló sin escribir filas (`data/sello_dinero.log` y `journalctl --user -u mki-sello-dinero.service` en la ventana 23:30:00 a 23:34:59 NY), la noche no es inválida: `A(D) = 0`, «sellador sin filas: fuente caída a la hora actual», sin contraste de concordancia; si 3 o más de las K noches caen ahí, NO DECIDIBLE; un sellador caído por error de código sí invalida.

**E19 (BLOQUEANTE, una línea).** «El umbral es el mismo en todas las ramas» ya no es cierto: la rama (b) lleva 5. Texto: umbral base 3 para (c), `n_X` y «sin indicio suficiente»; la rama (b) lleva 5 y vuelve a 3 sólo si el acta evita la pérdida de los viernes; los dos fijos hoy.

**E20 (BLOQUEANTE).** La sección 2 describía la potencia de un umbral que la rama (b) abandonó, y con 27,3 % el «lo más probable» era falso (P(X ≥ 3 | 10, 0,2727) = 0,5414). Recomputado: P(X ≥ 5) = 0,0016 / 0,0781 / 0,1075 / 0,3669 / 0,6230 para p = 0,10 / 0,25 / 0,2727 / 0,40 / 0,50. Con la tasa del antecedente y todas las noches rescatables, la regla indica (b) con probabilidad 0,11. Texto: la tabla de potencia con las dos columnas y la frase «quien lea un "sin indicio suficiente" tiene que leerlo como "no alcanzó", no como "no hay"»; y la limitación 5 con 0,54 y 0,11.

**E21 (RECOMENDADA).** V1 pasó a depender del journal: declarar la retención medida (journal persistente en `/var/log/journal`, sin límite configurado, entrada más antigua del 24-ago-2026, unos 36 días contra los unos 30 del plazo), y que sin journal la presencia de filas prueba el arranque.

**E22 (RECOMENDADA).** «El antecedente de 3 en 11 cabe» en [0,0 · 27,8]: cabe el punto (27,3 %), por medio punto; el intervalo no.

**E23 (para el acta).** (H1) NO SOSTENIDA, corregida a 3/11; (H2) NO SOSTENIDA, corregida a 5; (H3) SOSTENIDA por el orquestador con evidencia, mi objeción retirada y anotada como error mío. Ninguna suma al DSR.

### Veredicto

**APTA CON EXIGENCIAS**: tres bloqueantes de un párrafo (E18, E19, E20). Con esos tres párrafos incorporados, sella. Nueve de mis diez bloqueantes originales quedaron cerradas, E5 parcialmente, y dos de mis exigencias eran erróneas (E8 y el hecho de E6): retiradas, y el error es mío. Hora de cierre: **23:05:16**.

### Qué hizo el orquestador después (nota del orquestador)

E18, E19, E20, E21 y E22 incorporadas tal cual entre las 23:07 y las 23:08 (potencia recomputada por el orquestador antes de escribirla: P(X ≥ 3) 0,0702 / 0,4744 / 0,5414 / 0,8327 / 0,9453 y P(X ≥ 5) 0,0016 / 0,0781 / 0,1075 / 0,3669 / 0,6230; `journalctl --disk-usage` 665,7 MB, `/var/log/journal` existe, `SystemMaxUse` y `MaxRetentionSec` comentados en `/etc/systemd/journald.conf`, primera entrada de usuario `2026-08-24T23:14:48`). **Documento sellado a las 23:08:17 de Chile, sha256 `ca2ccd536f9d956c2b4a8404ec800341f29e4a0e1f1cd20720c08eca15b9a436`, 540 líneas, 38.679 bytes.** No hubo tercer dictamen: las tres exigencias eran de texto y se pegaron sin reinterpretar.
