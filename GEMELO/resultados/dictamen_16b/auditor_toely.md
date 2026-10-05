# Dictamen del `auditor-lookahead` — parche «TOELY fuera del insumo de E0» (corrida 16b)

> Transcrito por el orquestador (Fable 5.1) a las 19:44 de Chile del domingo 4-oct-2026, texto íntegro del agente
> (abierto 19:32:27, cerrado 19:39:59). **Nota del orquestador, posterior al dictamen:** la exigencia de código **B3**
> (propagar `excluidos_universo` al retorno de `sellar()`) se aplicó en el worktree a las 19:43 y el parche se regeneró:
> el sha256 del `.diff` pasa de `766afa4d…` (el que el auditor leyó) a
> `e8989db56742c593aa75c3ac3e6f0f25ec4a9dceaefd60bb8524938d6127d9b6`; `dinero/sello_dinero.py` parchado pasa de
> `f1397250…` a `cd0e70c8005143b2f6b63c62fb9e3f75b5303e083a936c98c13b86df6a8b2c25`; `reglas.json` no cambió
> (`b6080eee…`). El test de reproducción asserta la clave nueva. Suite del sellador tras B3: 73 passed, 5 skipped
> (`test_toely_fuera_insumo_e0`, `test_sello_dinero`, `test_instrumento_dinero`, `test_segundo_sello`). **B4 no se
> cumple en esta corrida:** el parche NO se aplicó al árbol real (reloj del encargo vencido); la suite real con el parche
> es parte de la receta de aplicación de Nicolás (bitácora 16b §5). B1, B2 y B5 están declaradas en el acta §96. R1 a R5
> van a la tarjeta §79 y a la corrida 16; ninguna se ejecutó (no se firma nada).

---

# Auditoría de fuga del `auditor-lookahead` sobre el parche «TOELY fuera del insumo de E0» (corrida 16b)

> Agente abierto **19:32:27** y cerrado **19:39:59** de Chile del domingo 4-oct-2026 (horas de `date`, no estimadas).
> HEAD `f5b659eb40f44e8661e41d3d0cd24e0717d52afc`. Parche `GEMELO/propuestas/parches/toely_fuera_insumo_e0_16b.diff`,
> sha256 `766afa4dd08b9c8e024a3815c367e6caadf2caca298cef549ccbbc7e248c3dce` (verificado con `sha256sum`), `git apply
> --check` sobre el árbol real **sin error**. Worktrees usados: `…/scratchpad/wt16b` (con parche) y `…/scratchpad/wt16b_head`
> (HEAD puro). Nada escrito en ningún árbol de producción; `dinero/sello_dinero.db` abierta siempre con `?mode=ro`,
> mtime `1790998205.2400458` y tamaño `536576` idénticos al abrir y al cerrar (comprobado cuatro veces).
> Ningún `--sellar` corrido; ninguna unidad de systemd tocada.

## VEREDICTO: APLICABLE CON EXIGENCIAS

**No hay fuga temporal.** El parche no toca ni un instante: `timing_ok`, `available_at`, `apertura_objetivo_utc`,
`insumo_fresco` y la regla maestra se calculan en `sellar()` **antes** de llamar a `decidir()`, y el único cambio vive
dentro de `decidir()`, tres líneas después de `universo_operable`. Tampoco hay fuga de futuro: el gate de invariancia
sigue verde con el cfg nuevo. **No hay efecto retroactivo**: `estado()` sobre la base real devuelve exactamente lo
mismo con y sin parche.

Las cinco exigencias bloqueantes son de **colisión con un pre-registro sellado** (§58) y de **auditabilidad**, no de
diseño del filtro. La más seria no está en el código: el parche **dispara la condición V4 de la regla sellada de §58**,
que §95.4 no declara.

---

## Exigencias BLOQUEANTES

### B1. El parche cierra la regla sellada de §58 por su propia cláusula V4, y el acta no lo dice

`GEMELO/propuestas/regla_58.md` (sellado 29-sep 23:08, sha `ca2ccd53…`, firmado tal cual en §93.5), §1, **V4**:

> **V4, universo estable.** Los 33 operables de esa noche son los mismos 33 de la sección 3. Si el universo cambia de
> forma **permanente**, todas las noches posteriores serían inválidas y la regla nunca llegaría a K: en ese caso **se
> cierra de inmediato** con «NO DECIDIBLE: el universo operable cambió el \<fecha\>», publica las noches válidas
> juntadas hasta ahí, y reiniciar el conteo con el universo nuevo es acto de Nicolás, con acta.

Y §3: «**El universo que rige: los 33 operables sellados** … Entre los 33 están los dos ADR de mostrador (**SHECY y
TOELY**) y los tres ETF».

Desde la noche del 5-oct el universo del sello es 32 **de forma permanente y por firma** («sin retorno aunque la fuente
lo retome»). V4 se cumple literalmente: la regla se cierra **NO DECIDIBLE** con las noches juntadas hasta el 2-oct, que
son **4** (29-sep, 30-sep, 1-oct, 2-oct), todas con `A(D) = 0`, contra un K = 10 y un plazo del 26-oct.

§95.4 dice «La regla sellada de §58 no se edita» y anota las cuatro noches incompletas; **no declara V4**. Aplicar el
parche sin escribirlo deja el 26-oct una lectura única ejecutándose contra un universo para el que no fue sellada, o
peor, ejecutándose y devolviendo (a) sin que nadie recuerde por qué.

Además, el corte T/X de §3 pierde una de sus dos patas: «El corte entre T y X en 2 sale de la estructura del universo
(hay exactamente **dos ADR de mostrador** entre los 33, los dos candidatos conocidos a rezagarse)». Con TOELY fuera
queda uno (SHECY).

**Exigencia:** el acta que aplique 16b escribe, antes de aplicar, que el sello del 5-oct dispara V4 de `regla_58.md`,
con la fecha; que las noches válidas juntadas son 4; y que reiniciar el conteo con el universo de 32 es acto de Nicolás
con acta. La regla **no se edita** — se declara que su propia cláusula la cierra.

### B2. Con TOELY fuera, `A(D)` y `C(D,g)` de §58 dejan de medir lo mismo, y eso fuerza el resultado de la regla

`regla_58.md` §3 define las dos vías con **fuentes distintas**:
- `A(D)` = `insumo_completo` de las filas del sello → desde el 5-oct se calcula sobre **32**;
- `C(D, g)` = 1 si «en esa misma observación los **33 operables** tienen `es_sesion_de_hoy = 1`» → la sonda.

La sonda **no se entera del cambio**. `GEMELO/sonda_cierre.py:58` lee su lista de
`dinero/datos/cierres_congelados.meta.json` como texto (36 tickers); no importa `reglas.json`, no llama a
`universo_operable`, no importa nada de `dinero/`. Confirmado por código y medido en `data/sonda_cierre.csv`: en las
**6** de las 9 noches registradas el único faltante en la última observación es TOELY.

```
noches en el CSV: 9
  faltantes al cierre de la noche: ('TOELY',) -> 6 noche(s)
  faltantes al cierre de la noche: (ninguno) -> 2 noche(s)
  faltantes al cierre de la noche: (31 tickers) -> 1 noche(s)   # apagón de la fuente
faltantes por ticker: [('TOELY', 6), (los otros 31, 1 cada uno)]
```

Consecuencia mecánica, no estadística: desde el 5-oct toda noche en que sólo falte TOELY tendrá `A(D) = 1` y
`C(D, g) = 0` **en los dieciséis casilleros**. La tabla de clasificación de §3 hace clase **C** a toda noche con
`A(D) = 1`; las clases R, T y X exigen `A(D) = 0`. Entonces `R(t) = 0` para las ocho candidatas, siempre, y el umbral
base (3 de 10 rescatables) es **inalcanzable por construcción**: la regla devolvería (a) sin que ningún dato de
madrugada participe. V4 la cierra antes, pero el punto queda: **el resultado de un pre-registro sellado pasa a estar
determinado por un cambio de código, no por el dato**.

La concordancia sí sobrevive: el conjunto de la sonda `{TOELY}` contiene estrictamente al del sello `{}` → clase
**desaparición**, que §1 declara «no discorda». O sea que la inconsistencia **no dispara ninguna alarma** de la propia
regla.

**Exigencia:** el acta declara esta inconsistencia con nombre (`A` sobre 32, `C` sobre 33) y declara que la sonda
seguirá contando TOELY. §95.4 ya dice «Si la sonda toma el universo del mismo lugar que el sellador, el cambio le
llega; su código no se toca y la 16b lo declara» — la respuesta medida es **no le llega**, y la consecuencia sobre §58
es la de arriba, que el acta no previó.

### B3. La exclusión no deja rastro en el sello ni en el log: sólo se la ve por ausencia

`decidir()` devuelve `"excluidos_universo": excluidos` (línea 486 del archivo parchado) — y ahí muere. `sellar()` **no
lo propaga**: su dict de retorno no tiene la clave (verificado por inspección del bloque `def sellar` y confirmado con
`grep -n excluidos_universo` → una sola ocurrencia, en `decidir`). Como `main()` imprime `json.dumps(r)` de **`sellar`**
a `data/sello_dinero.log`, el log de la noche del 5-oct dirá `filas_insertadas: 32` **sin decir por qué** fueron 32. La
fila sellada tampoco lo dice: no hay columna, y `reglas_version` y `version_sello` no se mueven (ver B4).

Esto es el mismo defecto que el auditor de la corrida 15 marcó bloqueante en el parche T («la rama de rechazo no dejaba
rastro en ninguna tabla»).

Agravante medido: la exclusión es una **intersección silenciosa**, `set(tickers) & set(operables)`. Un error de tipeo
revierte el comportamiento sin ruido:

```
['TOELY']  -> excluidos ['TOELY'] n_operables 32
['TOEL']   -> excluidos []        n_operables 33
['toely']  -> excluidos []        n_operables 33
['TOELY '] -> excluidos []        n_operables 33
```

Un `'toely'` en minúsculas pierde la sesión del lunes exactamente como las seis anteriores, y nada lo nombra.

**Exigencia:** propagar `excluidos_universo` al dict de retorno de `sellar()` (una clave; sin columna nueva, sin tocar
el esquema, sin reescribir ninguna fila), para que la línea del log de cada noche declare la exclusión aplicada. Es la
diferencia entre «32 porque así se firmó» y «32 porque algo falló».

### B4. Juez de la aplicación: la suite del árbol real, porque la del worktree no puede juzgar este parche

Las dos suites completas terminaron (19:38:34 y 19:38:31) y el conjunto de rojos es **idéntico**:

| | passed | skipped | failed | errors | xpassed |
|---|---|---|---|---|---|
| `wt16b` (con parche) | **938** | 83 | 20 | 6 | 1 |
| `wt16b_head` (HEAD puro) | **929** | 82 | 20 | 6 | 1 |

Los 20 `FAILED` y los 6 `ERROR` son los **mismos nombres** en los dos (test_api 6, test_backtest 1, test_dinero 2,
test_frontend_estatus 1, test_linea_base 1, test_readme 9; errores todos de `test_cifras_arbitro`), con las mismas
causas de artefacto gitignorado ausente (`KeyError: 'mcnemar_b01'`, `assert 0 == 228`, «la corrida sellada
20260901-061708-5.1-invalidada-por-fuga no está en el repo»). **Ningún rojo aparece sólo con el parche.** La diferencia
+9 passed / +1 skipped = los 10 tests de `tests/test_toely_fuera_insumo_e0.py` (9 verdes + 1 saltado por falta de
`dinero/sello_dinero.db` en el worktree), consistente con el «8 rojos, 1 verde, 1 saltado» que el encargo midió sobre HEAD.

**Pero**: `tests/test_dinero.py::test_los_tres_endpoints_del_riel_sirven_lo_que_el_contrato_dice` y los seis de
`test_api.py` están rojos **en los dos**. O sea que la suite del worktree **no puede juzgar** si el parche rompe
`/api/dinero/sellos` ni el contrato. Esa cobertura sólo existe en el árbol real con sus artefactos.

**Exigencia:** la suite del árbol real con todas las bases decide, contrastada contra la línea base de hoy (**1032
passed, 5 skipped, 1 xfailed, 0 failed**, 19:25:16), y con el conteo de recolectados declarado (sube +10, a 1048 desde
los 1038 de la 16a). Atención a un rojo esperado y legítimo: `test_las_filas_selladas_antes_del_cambio_siguen_con_toely_y_con_la_huella_vieja`
asserta `S._sha256(U.RUTA_REGLAS) not in huellas` y en el árbol real **sin** el parche el sha actual SÍ está en las
huellas (`125a8602…`); ese test sólo puede estar verde **después** de aplicar. Si se corre la suite real antes de
aplicar, ese rojo es el test haciendo su trabajo, no una regresión.

### B5. Una fila nueva en `divergencias_sello` sobre una fecha anterior al corte publicaría un número incomparable

`sellar()` compara, en la rama de segundo sello con otro insumo, `filas_prev` (las **33** de la fecha ya sellada) contra
`ahora_por_t` (las **32** de ahora): `distintas = sum(1 for (t,d,n) in filas_prev if ahora_por_t.get(t) != (d,n))`.
Para cualquier `fecha_insumo` anterior al 5-oct, TOELY cuenta como distinta por ausencia **y** los otros 32 cuentan como
distintos por el resorteo (ver P1), así que `decisiones_distintas` daría ~33 donde hoy da 0 o 1. La base real tiene
**2 divergencias** registradas, con `decisiones_distintas` 1 (9-sep) y 0 (28-sep): el campo tiene historia y se lee.
La ruta está viva (`--sin-red` con una extensión vieja, o un disparo tardío), y `divergencias_sello` **no tiene columna
`reglas_sha256`** (esquema verificado: `id, fecha_insumo, timestamp_utc, sha_sellado, sha_nuevo, decisiones_distintas,
detalle, creado_en`), así que la fila nueva no sabría decir bajo qué reglas se computó.

No viola la Constitución (es una fila nueva, no una reescritura; los triggers `sellos_dinero_inmutable_1/2` siguen en
pie, verificado en `sqlite_master`). Pero publica un número que significa otra cosa.

**Exigencia:** declararlo en el acta —`decisiones_distintas` de una fecha anterior al 5-oct computado bajo las reglas
nuevas no es comparable con los dos valores ya registrados— o, si se prefiere código, que `detalle` cite el
`reglas_sha256` vigente al computarlo. Lo mínimo aceptable es la declaración; no exijo tocar el esquema.

---

## Exigencias RECOMENDADAS

**R1. Preservar la realización del sorteo sortea el problema por cero costo, y es la opción que yo tomaría.** Medido
abajo (P1): sortear con los 33 y descartar TOELY da, en las 40 últimas sesiones del congelado, **exactamente las mismas
30 compras y el mismo conjunto de tickers** que HEAD. La lista corta da 25 y un conjunto distinto. El cambio de un
caracter (`senales_sin_informacion(hasta, operables + excluidos, …)` y filtrar después) hace la población nueva
**continuación exacta** de las 9 sesiones que ya cuentan. **Declaro el costo de recomendarlo ahora:** yo ya medí las
dos realizaciones (30 vs 25 compras), así que elegir entre ellas hoy es una elección con los dos resultados a la vista.
Es inocua porque E0 no puntúa ningún resultado (tamaño nominal cero, señal sin información, `senal_fuente` lo dice en
cada fila), pero es un grado de libertad que no existía antes de este dictamen y tiene que quedar escrito.

**R2. Mover `version_reglas`.** Hoy `reglas_version` queda en `0.2.0-PROPUESTA` y `version_sello` en `E0.2` en las dos
poblaciones. Un lector del CSV versionado no distingue las filas sin recomputar hashes. Mover `version_reglas` a
`0.3.0-PROPUESTA` **no choca** con el `E0.3` del parche T: son campos distintos en archivos distintos (`version_reglas`
vive en `reglas.json`; `VERSION_SELLO` es constante de `sello_dinero.py` y el parche T la mueve). Ningún test fija
`"0.2.0-PROPUESTA"` como literal (grep: sólo documentos de resultados ya sellados, que no se tocan). Nota: mover
`version_reglas` cambia otra vez el sha del archivo; hay que hacerlo en el mismo acto.

**R3. `estado()` y `/api/dinero/sellos` sin desglose por población.** `sesiones_selladas`, `sesiones_que_cuentan_para_N`
y `filas` se agregan sobre las dos poblaciones sin separarlas (`estado()` no agrupa por `reglas_sha256`), y `filas`
pasará a crecer de a 32 sin que nada diga por qué. Nada publicado se mueve (ver P5), así que es recomendada: un
`por_reglas_sha256: {hash: {sesiones, filas}}` aditivo en `estado()`.

**R4. Que la exclusión reviente si el ticker no está en el censo.** Complemento de B3: si un nombre declarado en
`exclusiones_insumo_e0.tickers` no aparece en `universo_operable`, hoy se ignora en silencio. Que levante `ValueError`
nombrando el ticker. El test `test_sin_la_clave_en_reglas_el_comportamiento_es_el_anterior` cubre la clave ausente, no
el nombre mal escrito.

**R5. Hecho que §95.4 cita incompleto.** El acta dice «yfinance dejó de servir TOELY desde el 25-sep». Medido en la base
real: TOELY fue **el único faltante** también el **18-sep** y el **23-sep**, antes del corte. O sea que la exclusión no
saca sólo un ticker muerto: saca un **rezagado crónico**, que es el que la regla de §58 fue sellada para medir (§3 lo
nombra). Conviene que el acta lo escriba así.

---

## Respuesta a las seis preguntas obligatorias

### P1. ¿El cambio de universo altera el sorteo de E0 o su sesgo de alguna forma no declarada?

**Altera la realización, no la distribución, y no hay sesgo. Pero la magnitud no estaba declarada y es casi total.**

`contabilidad.senales_sin_informacion:283-308` crea **un solo** `np.random.default_rng(semilla)` y recorre
`for dia … for t in tickers`. Medido sobre el congelado (754 sesiones desde `CP.DESDE`):

```
orden de operables: [... 'TER', 'TOELY', 'TSEM', 'TSM', 'UMC', 'VRT', 'WDC', 'XSD']
indice de TOELY: 26 de 33
dia 2023-09-05: iguales=26 distintos=6   (los 6 posteriores a TOELY)
dia 2023-09-06: iguales=0  distintos=32
…
dia 2026-09-04: iguales=0  distintos=32
total (ticker,dia) con magnitud distinta: 24081 de 24128   (99,81 %)
A sin TOELY: media 2,190257  sd 12,555860  n 24128
B           : media 2,198614  sd 12,617822  n 24128
```

Exactamente lo que el encargo declaró: los 6 posteriores en la primera sesión, los 32 desde la segunda. Las dos
primeras cifras confirman que **la distribución por ticker y la semilla quedan intactas** (medias y sd
indistinguibles); lo que cambia es qué índice sale de `rng.choice` en cada casilla.

¿Puede favorecer el resultado de E0? **No, y la razón es estructural:** E0 no puntúa ningún resultado. El tamaño
nominal es 0, la señal es un sorteo sin información declarado en `senal_fuente` de cada fila, y lo único que E0 cuenta
es `cuenta_para_N` — que no mira ninguna decisión. No hay retorno, Sharpe ni acierto calculado sobre estas filas. Un
resorteo no puede favorecer un marcador que no existe. Lo que sí cambia son las **decisiones publicadas** en la fila:

```
HEAD   (33 sorteado, 33 decidido)         compras: 30  {AMKR, ASX, GFS, GSM, SHECY, UMC}
PARCHE (32 sorteado, 32 decidido)         compras: 25  {AMKR, ASX, GFS, GSM, INTC, SHECY, UMC}
PRESERVAR (33 sorteado, 32 decidido)      compras: 30  {AMKR, ASX, GFS, GSM, SHECY, UMC}
compras de TOELY en HEAD: 0
```

**Las 40 sesiones de prueba dicen que el 100 % del cambio de decisiones viene del resorteo, no de sacar TOELY**: TOELY
no generó ni una compra, y preservar la realización reproduce HEAD ticker por ticker. También verifiqué que
`decision.proponer_ordenes` **no reparte el presupuesto por número de tickers** (`tope_posicion_pct` del presupuesto y
los topes diario/semanal/mensual son absolutos; el orden es por `-magnitud_pp`), así que la lista más corta no
introduce ningún sesgo estructural de dimensionamiento.

**Qué se pierde con cada opción.** Con la elegida: las 9 sesiones que ya cuentan y las que vienen dejan de pertenecer a
la misma corriente de sorteo, así que la muestra de N = 40 mezcla dos realizaciones; cualquiera que mañana quiera
reproducir la serie de `senal_magnitud_pp` de las 40 necesita saber el corte y tenerlo en el hash. Con la alternativa
(sortear con 33 y descartar): no se pierde nada medible — TOELY vive en el congelado (historia anterior a `DESDE`, sha
fijo), así que su `dist[t]` existe para siempre y `MINIMO_HISTORIA_SENAL` nunca se activa; el único costo es dejar un
nombre muerto en una línea de código, con su comentario.

### P2. ¿El hash de reglas cambia? ¿Basta `reglas_sha256`? ¿Choca con el `E0.3` del parche T?

**Cambian DOS hashes, no uno, y los dos viajan en cada fila.** Medido:

```
reglas.json   actual 125a8602a684939576278093b306add6a6fa7a0157389f71a5c0029455ab9ba0
reglas.json   parche b6080eee4351ed433aeb5a124ec4603dcb3db3b3278b1791c40ee8a4ad0abc6c
sellador.py   actual 480fbdc991679f2b06340bd4609dc08b3fd8c920cc4bc5eae1d03b93a39fbeab
sellador.py   parche f13972503cccfde9add85fe52d55c071363d5f54f49f322da97d6d8cad11939f
```

Base real: un solo `reglas_sha256` (`125a8602…`) en las 594 filas, dos `sellador_sha256` (`93db9b70…`, `480fbdc9…`).
`sellar()` sella los dos en cada fila (`reglas_sha = _sha256(U.RUTA_REGLAS)`, `sellador_sha =
_sha256(os.path.abspath(__file__))`), y las dos columnas están en el esquema y en el CSV versionado. Como ambos
archivos están en git, el hash es **reproducible por un tercero desde el repo**, que es la vara que §95.4 pide.

**Como llave, basta: cada fila sabe a qué población pertenece y el contenido de esa población es recuperable.** Como
declaración, **no basta**: `reglas_version` y `version_sello` quedan idénticos en las dos poblaciones (R2), y ninguna
cifra agregada separa (R3).

**No choca con el parche T.** `VERSION_SELLO` no se mueve en este parche (sigue `"E0.2"`, verificado en el archivo
parchado), así que el corte de método `E0.3` de §93.7 queda libre para la noche que aplique T. Mover `version_reglas`
(R2) es otro campo en otro archivo y tampoco lo reclama.

### P3. ¿Algo más que el sellador lee el universo y cambia de comportamiento?

**No. Censo completo, y todo confirmado por ejecución o por código:**

| consumidor | lee el universo de | ¿cambia? | evidencia |
|---|---|---|---|
| `GEMELO/sonda_cierre.py` | `dinero/datos/cierres_congelados.meta.json` como texto (36 tickers) | **NO** | `RUTA_TICKERS:58`; no importa `reglas.json` ni `dinero/` |
| censo `universo_operable.json` / `dinero/mapa.py` | `CP.universo_operable` | **NO** | el filtro va *después* |
| `GEMELO/m2_periodo.py:116` | `CP.universo_operable` | **NO** | idem |
| `GEMELO/universo_por_presupuesto.py` | `CP.universo_operable` | **NO** | idem |
| `docs/universo_operable.md` («33 de 36») | el censo | **NO** | cifra intacta |
| API `/api/dinero/universo` | artefacto `universo_operable.json` | **NO** | `api/main.py:975` |
| API `/api/dinero/sellos` | `S.estado()` en `mode=ro` | **NO hoy** | medido abajo; sí crecerá de a 32 (R3) |
| `api/CONTRATO.md` | — | **NO** | `excluidos_universo` sólo existe en el retorno de `decidir()`, que la API no llama |
| `exportar_csv` | la tabla entera | **NO** | `SELECT * … ORDER BY id`, sin recomputar |
| `scripts/generar_readme.py` | sólo `N_OBJETIVO_E0` por regex (`:103`) | **NO** | es el literal 40 |
| `mki_vigia.py` | nada de `dinero/` | **NO** | grep: 0 menciones |
| frontend `SellosDinero.tsx` | la API | **NO** | sin `33` cableado |
| tests | 8 pins `== 33` → `N_OPERABLES = 32` | sí, es el parche | |

La **única** divergencia de comportamiento es la de la sonda, y no es que cambie: es que **no cambia** y por eso
divergirá del sellador (B2).

### P4. ¿Qué pasa la primera noche si TOELY reaparece? ¿Y si desaparece OTRO ticker?

**Si TOELY reaparece: no vuelve, y está probado.** `excluidos` se calcula contra `operables` (el censo), que no depende
de que haya dato: TOELY sigue en el censo con o sin cierre, así que la intersección lo saca igual.
`test_toely_presente_en_la_fuente_no_vuelve_al_universo` lo asserta con el congelado, que **sí** trae la columna, y
pasa. Cumple la firma «sin retorno aunque la fuente lo retome».

**Si desaparece otro ticker: la sesión se pierde exactamente como antes.** Cero faltantes tolerados, verificado por el
parametrizado `test_cualquier_otro_faltante_sigue_siendo_insumo_incompleto` con `('AMD',)`, `('AMD','TOELY')` y
`('KLAC','NVDA','TOELY')` → `insumo_completo is False`, `estado == insumo_incompleto`, `cuenta_para_N == 0`, y TOELY
no aparece ni como faltante. Sacar al siguiente exige **otra acta**, otro hash de reglas y **otro disparo de V4** si
§58 siguiera abierta. Riesgo residual medido: en las 9 noches de la sonda, **SHECY —el otro ADR de mostrador— no se
retrasó ni una vez**; el único episodio multi-ticker fue un apagón total de la fuente (31 de 33). n = 9 noches: poco
para afirmar que el riesgo es bajo.

### P5. ¿Hay efecto retroactivo sobre filas selladas o sobre cifras publicadas?

**No, y lo ejecuté.** `estado()` sobre la base real, llamada desde los dos worktrees, byte a byte igual:

```
wt16b_head : {'filas': 594, 'sesiones_selladas': 18, 'sesiones_que_cuentan_para_N': 9, 'N_objetivo': 40, 'divergencias_registradas': 2}
             ultimo reglas_sha256 125a8602a684 · version_sello E0.2 · 33 filas en el último sello
wt16b      : {'filas': 594, 'sesiones_selladas': 18, 'sesiones_que_cuentan_para_N': 9, 'N_objetivo': 40, 'divergencias_registradas': 2}
             ultimo reglas_sha256 125a8602a684 · version_sello E0.2 · 33 filas en el último sello
mtime de la base idéntico antes y después en las dos corridas
```

`exportar_csv` hace `SELECT * FROM sellos_dinero ORDER BY id` sin recomputar nada: el backup versionado
`data/backups/sello_dinero.csv` conserva las 594 filas con TOELY y con `125a8602…`. Los triggers
`sellos_dinero_inmutable_1` y `_2` siguen en `sqlite_master`. README: `scripts/generar_readme.py` lee de E0 **sólo**
`N_OBJETIVO_E0` por regex (§90.3 le quitó el contador vivo), y el parche no toca esa constante → **ninguna cifra
publicada se mueve**. La única retroactividad posible es la de B5, que es una fila *nueva*, no una reescritura.

**Lo que sí hay que escribir, porque es el precio de la no-retroactividad:** con el parche aplicado retroactivamente,
las sesiones que contarían serían **15 de 18** y no 9. TOELY es el **único** faltante en 7 sesiones selladas:

```
2026-09-18 insumo_incompleto   TOELY
2026-09-23 insumo_incompleto   TOELY
2026-09-28 no_verificable_timing  TOELY   (no contaría igual: timing roto)
2026-09-29 insumo_incompleto   TOELY
2026-09-30 insumo_incompleto   TOELY
2026-10-01 insumo_incompleto   TOELY
2026-10-02 insumo_incompleto   TOELY
```

(las otras dos incompletas, 9-sep y 22-sep, son apagones de 31 tickers y seguirían perdidas). **6 sesiones** quedan
donde están por la firma de no-retroactividad, y eso está bien: recuperarlas sería reescribir el pasado con la regla de
hoy. Pero el acta debería decir el número.

### P6. ¿La regla maestra y la ventana horaria quedan intactas?

**Sí, verificado por lectura de código y por test.** En `sellar()`, `avail`, `sesion_obj`, `apertura_obj`,
`fecha_sello`, `estado_dia`, `timing_ok = fromisoformat(avail) < ahora < apertura_obj`, `sesion_previa_a_obj` y
`insumo_fresco` se calculan **todos antes** de `dec = decidir(cierres, fecha_insumo, cfg)`. El parche no toca ninguna
de esas líneas. Un detalle que miré a propósito: `avail = max(available_at_utc de todos los tickers del meta)` y TOELY
sigue en el meta de la extensión (`descargar_extension(base_meta["tickers"])` no cambia) — como su `available_at` es
el **más viejo** (último cierre 24-sep), el `max` no se mueve. Si el excluido hubiera sido el ticker más tardío, el
`max` sí cambiaría; no es el caso, y la exclusión va después de `avail`, así que no hay forma de que el filtro adelante
`available_at`.

Prueba de conducta en verde: `test_la_ventana_horaria_sigue_mandando_con_toely_fuera` sella a las 14:00Z del 9-sep
(después de la apertura objetivo 13:30Z) con TOELY faltante → `insumo_completo is True` **y** `timing_ok is False`,
`cuenta_para_N == 0`. La completitud nueva **no rescata** un sello tardío.

Y el gate de futuro sigue en pie: `test_el_gate_de_invariancia_sigue_en_pie` corre
`verificar_invariancia_decision(base, dia, futuros=5)` sobre 2026-08-20 y 2026-06-15 → `INVARIANTE`, `cortes = 6` cada
uno. Suite del sellador con el parche: **34 passed, 5 skipped in 14.35s**
(`tests/test_toely_fuera_insumo_e0.py tests/test_sello_dinero.py`).

---

## Lo medido en la base real (`?mode=ro`, 19:34)

```
filas 594 · sesiones 18 · cuentan para N 9 · N objetivo 40 · divergencias 2
reglas_sha256 distintos:  ['125a8602a684939576278093b306add6a6fa7a0157389f71a5c0029455ab9ba0']
sellador_sha256 distintos: ['93db9b70dc70…', '480fbdc99167…']
reglas_version: ['0.2.0-PROPUESTA']   version_sello: ['E0.2']
TOELY: 18 filas, de 2026-09-08 a 2026-10-02
estados: 9 pendiente · 8 insumo_incompleto · 1 no_verificable_timing (28-sep)
divergencias: 9-sep (decisiones_distintas 1) · 28-sep (0)
triggers sellos_dinero_inmutable_1 y _2 presentes
```

Coincide con todo lo que el encargo declaró. Añado lo que no estaba: la lista exacta de las 7 sesiones con TOELY como
único faltante y las 2 con apagón de 31 (arriba, P5).

---

## Lo que NO puedo auditar con lo que hay hoy (zonas ciegas, nombradas)

1. **Fuga por el analista, declarada y sin defensa posible.** Quien eligió sacar TOELY —y quien escribe esto— ya vio
   la ventana: sabe que 6 sesiones se perdieron por él, sabe que el contador va 9 de 40 y sabe que el plazo de §58 es
   el 26-oct. El cambio **mejora mecánicamente la tasa de sesiones que cuentan** y la firma se tomó con ese hecho en la
   mano (tarjeta §77). No es un defecto del parche: es la condición de todo cambio de universo a mitad de experimento.
   La única defensa es que E0 no puntúa habilidad y que el corte está fechado y hasheado. Queda escrito.
2. **El resorteo, ahora que lo medí.** Las dos realizaciones son observables (30 vs 25 compras en 40 sesiones).
   Cualquier elección entre ellas a partir de este dictamen se hace con los dos números a la vista. Inocua hoy porque
   nada se puntúa; dejaría de serlo el día que E0 o E1 midan un resultado sobre estas decisiones.
3. **La suite del worktree no cubre `api/` ni `test_dinero.py`** (rojos en los dos árboles por artefactos gitignorados
   ausentes): la conducta del endpoint con 32 operables **no está verificada** en ningún árbol todavía. De ahí B4.
4. **La causa del hueco de TOELY no está demostrada** y no la demostré: el split 5:1 del ADR (titular de Futu del
   2-oct) es posterior al inicio del hueco (25-sep). Es una fuga de **disponibilidad** del mandato ampliado: el dato
   que existía el 24-sep al sellar ya no se puede volver a pedir, y la verificación tardía no puede reproducirlo.
   Yahoo revisa la historia sin avisar: todo lo que afirmo sobre «TOELY no tiene cierre desde el 25-sep» descansa en
   una serie descargada hoy, no en una point-in-time.
5. **Las 9 noches de la sonda son pocas** para afirmar que SHECY u otro no repetirá el patrón de TOELY. El parche no
   deja ninguna defensa contra el próximo rezagado crónico: cada uno exigirá su acta, su hash y —mientras §58 viva—
   su V4.
6. **`n_filas_respuesta` de la sonda no distingue apagón parcial de cierre ausente** (lo dice la propia `regla_58.md`
   §V2). Si la fuente devuelve filas pero con TOELY vacío por una razón distinta de «el ticker murió», la sonda y yo
   lo leemos igual. No es auditable desde el CSV.

---

## Resumen operativo

| | |
|---|---|
| Fuga temporal | **ninguna demostrada**; `decidir` es la única función tocada y el filtro va después de `universo_operable` y antes del sorteo, sin mirar ningún instante |
| Fuga de futuro | **ninguna**; gate `INVARIANTE` con 6 cortes en dos fechas, con el cfg nuevo |
| Retroactividad | **ninguna** sobre filas, `estado()`, `exportar_csv`, backup CSV ni README (ejecutado) |
| Regla maestra | **intacta** (código + test de conducta con sello tardío) |
| Bloqueantes | **B1** V4 de §58 · **B2** `A` sobre 32 vs `C` sobre 33 · **B3** la exclusión sin rastro en `sellar()`/log · **B4** la suite real como juez · **B5** `decisiones_distintas` incomparable |
| Recomendadas | **R1** preservar la realización · **R2** `version_reglas` · **R3** desglose por hash en `estado()` · **R4** reventar ante ticker desconocido · **R5** el hecho del 18 y 23-sep en el acta |

Las tres bloqueantes **de acta** (B1, B2, B5) no tocan código. Las dos **de código** son chicas: una clave en el dict de
retorno de `sellar()` (B3) y correr la suite del árbol real (B4). Ninguna cuestiona el filtro ni la firma de §95.4.
