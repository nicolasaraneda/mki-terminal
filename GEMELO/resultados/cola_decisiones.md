# La cola de decisiones — todo en una pantalla

Consolida cada "decisión de Nicolás" que hoy vive repartida en
`DECISIONES.md`, `expedientes.md`, `RELEVO.md`, `REPLICA.md`, `MICRO/`,
`SECUENCIAL/`, `MICRO/`, `ESTADO.md` y los resultados de las cuatro
corridas autónomas. Ninguna se resuelve acá.

**Orden: por costo de postergarla un mes, no por tamaño del documento que
la sostiene.** Una decisión de una frase puede costar más cara de demorar
que un documento de treinta páginas que no bloquea nada.

**Actualizada:** 2-sep-2026, séptima corrida.

## Qué movió la séptima corrida (2-sep)

| | |
|---|---|
| **Abrió** | **Cuál es el campeón cuando sello y fuente discrepan, y la copia congelada de insumos** (§17). Yahoo no reescribe retornos pero sirve estados distintos; el sello tiene «emitido antes» y no «reproducible después». Arnés listo, no activado. |
| **Abrió** | **La frase de potencia del 5.1 antes del 25-oct** (§18): potencia 0,36 [0,34, 0,37] frente a 9 pp; MDE 16,6 pp [11,0, 20,3]. **Y R2 dispara sobre el ancla del 31-ago.** |
| **Midió** | **El instrumento no es subpotente estructuralmente pero responde en años**: 9 pp → ~248 días [109, 370] (jul-2027); 6,5 → ~475; 5 → ~800. Ciego a «¿persiste?» con un régimen. |
| **Propuso, con dictamen** | C-1/C-2/C-3 (§19: entran), D-1 (§20: entra como referencia, no como cota), E-1 (§21: entra condicionada), **E-2 rechazada**, y la adenda «4×» de la tesis **retirada**. |
| **Cerró** | El 92 suelto de `BANDA_N`: pinchado a su corrida sellada, con test contra el `veredicto.json`. Registro de intentos 91 → 100 (tramos TRAY y ESTIM). |
| **Cerró** | El forense de las 15 huérfanas no estaba pendiente (sexta corrida). |
| **No cerró** | El vigía «NO corrió» vs «corrió y no completó» y el timeout de `mki-noticias`: ver la bitácora 07, sección de la Fase 4. |

## Qué movió la quinta corrida, segunda tanda (1-sep)

| | |
|---|---|
| **Resolvió** | La **regla de deduplicación** (§2a): firmada, aplicada en el ejecutable, ninguna cifra publicada movida. **Su desenlace fue un tercero: p = 0,0451, que cruza α.** |
| **Abrió** | **Las 15 filas sin pareja** cuya sesión objetivo tampoco calza (§2a-ter). La firma no las previó porque nadie sabía que existían. |
| **Abrió** | **Los 5 pares de feriado real** como ítem de calendario y universo (§2a-quater), que es donde Nicolás pidió que fueran. |
| **Resolvió** | **R3 quedó LIMPIO**: las dos fugas del arnés de backtest, corregidas y con contraprueba que dispara 10/10. Es lo que desbloquea el veredicto del 25-oct. |
| **Resolvió** | El **conteo de intentos**: de un entero mágico protegido por un test a un **registro de 20 tramos con procedencia**. N = 86. |
| **Cerró** | Un **vector vivo que daba vuelta V5** (§14): `control_lineal.py` reintroducía el default de N que `backtest/inferencia.py` había quitado con acta. |
| **Cerró** | El **gatillo de la 5.1**: NO se releva, se espera al 25-oct. Holdout intacto. |
| **Dio vuelta** | La sospecha de tres corridas: **la ventaja NO está concentrada, está más dispersa que el azar** — y julio no es de otra especie (157 bloques históricos iguales o mejores). |
| **Abrió** | **B4 y B5 no son evaluables** sobre la ventana larga: sólo el 6,94% de las filas sobrevive al corte honesto de sentimiento (§15). |
| **Abrió** | Tres artefactos que quedaron **stale o trampa**: `ventana_larga.{md,json}` publicando el 91,4% ya refutado, y `referencia.py` con 189 casos contra 181 congelados (§16). |

## Qué movió la cuarta corrida (31-ago/1-sep)

| | |
|---|---|
| **Resolvió** | **α = 0.05** nominal con la banda [0.046, 0.079] publicada. Firmado. |
| **Resolvió** | **Placa: Arty A7-100T**, y la arquitectura de dos modelos (general en la A7, HFT más adelante en una KR260). Firmado. |
| **Cerró** | Las **dos afirmaciones refutadas de `RTL.md`**: errata fechada en su sitio (era el viejo §6). |
| **Cerró** | El **McNemar 0.1849 vs 0.1847**: ninguno está mal, son dos tests. Pero abre otra cosa (§3-bis). |
| **Abrió** | **La regla de deduplicación** — la más urgente de todas, y la que bloquea el pre-registro (§2a). **Firmada y aplicada el 1-sep**; abrió §2a-ter y §2a-quater. |
| **Abrió** | **La cuenta AMD** para instalar Vivado: bloquea todos los hitos del ramo (§4). |
| **Sigue** | El **MDE**: propuesto 7 pp y **retirado** por derivarse en la escala equivocada (§2b). |

## Qué movió la tercera corrida

| | |
|---|---|
| **Cerró** | La compra de datos point-in-time: **recomendación de no comprar nada, cero dólares**, con diez proveedores tasados (§9). |
| **Cerró** | La elección de placa FPGA dejó de ser una estimación: hay **síntesis real** y el campeón **no cabe** en la Go Board (§4). |
| **Destrabó** | La réplica: el ensayo general pasó con cero hallazgos y hay runbook con vuelta atrás. Sigue faltando **solo la firma** (§1). |
| **Abrió** | Una **mina en `ventana_larga.py`**: un test exige por contrato una cifra ya refutada (§5). |
| **Reemplazó** | `parche_documental.md` quedó retirado; lo sustituye `parche_honestidad.md` (§3). |

---

## 1. Activar la réplica, y con qué máquina

**Qué decidir, en una frase:** si se activa `docs/REPLICA.md` como
mecanismo permanente, qué máquina hace de réplica del PC (¿el Mac, ahora
que quedó fuera del rol de titular?), y **quién gana ante una
divergencia** — la única pregunta que el ensayo no pudo responder solo.

**Expediente:** `docs/REPLICA.md` (con §6 y §7 nuevas),
`docs/RUNBOOK_REPLICA.md` (8 pasos, vuelta atrás por paso, y una
sección 0 que lista justamente las decisiones bloqueantes),
`scripts/ensayo_replica.py` y su salida `data/replica_ensayo/reporte_ensayo.md`.

**Novedad de esta corrida:** el ensayo general pasó 8 fechas sintéticas
por los tres casos —PARIDAD, DIVERGENCIA en sus cuatro sabores, y las dos
formas de "una no selló"— con **cero hallazgos y cero divergencias
falsas**. 7 filas registradas, todas con `resuelto_como IS NULL`, que es
lo correcto: el registro anota, no arbitra. Nada activado.

**Qué se bloquea mientras esté abierta:** el proyecto sigue con **una sola
máquina emitiendo, la misma cuyo disco de sistema ya falló una vez**.

**Costo de postergarla un mes:** es el único ítem de esta lista cuyo costo
de postergación no es hipotético — ya se materializó una vez. La pieza
técnica dejó de ser el cuello de botella hace dos corridas; ahora tampoco
lo es el ensayo. **Lo único que falta es la firma.**

**Recomendación, marcada como tal:** primero de la cola, por la misma
razón de siempre y con menos excusas que antes.

---

## 1-bis. El defecto que SIGUE produciendo filas duplicadas

**Qué decidir, en una frase:** si se corrige `snapshot.py` para que
`sesion_objetivo` se calcule desde `available_at` y no desde el reloj de
pared del proceso.

**El defecto, con su cita.** `snapshot.py`:140 llama a
`calendarios.proxima_sesion_despues_de(exchange, ahora_utc)`, donde
`ahora_utc` es `datetime.now(timezone.utc)` estampado en `:111` — **el
reloj de pared del momento en que corre el proceso**. Cuando el sello se
atrasa y cruza la medianoche o las 01h UTC, esa llamada salta
honestamente a la sesión siguiente porque la asiática **ya abrió**. El
resultado es una segunda predicción apuntando a la misma sesión objetivo
que la del día anterior.

**Por qué está tan arriba en la cola:** los otros ítems son decisiones
sobre datos que ya existen. **Éste sigue ocurriendo.** Cada vez que un
sello se atrase —y ya pasó al menos tres veces documentadas: 29-jul,
3-ago, y los pares de 31-jul y 5-ago— se produce una fila más con la
sesión objetivo equivocada. El track record se sigue contaminando
mientras la decisión espera.

**Qué NO se puede hacer de paso, y por qué:** `snapshot.py` está en la
ruta de sellado, que es intocable para un agente. Y hay una razón más
profunda que la regla: **cambiar cómo se calcula `sesion_objetivo` cambia
el significado de las filas futuras respecto de las ya selladas**, y las
selladas no se reescriben nunca. O sea que la corrección crea, por
construcción, un corte de método con fecha — que es exactamente la clase
de cosa que se declara antes y no se descubre después.

**Costo de postergarla un mes:** proporcional a cuántos sellos se atrasen.
No es cero y no es acotado.

**Recomendación, marcada como tal:** corregirlo, declarando el corte de
método con su fecha. Y una observación que va con la corrección: el
defecto es **invisible salvo que uno vaya a buscar duplicados por
`sesion_objetivo`**, que es lo que nadie había hecho en cinco corridas.
Convendría que el vigía o un test lo detecte solo — hay uno propuesto en
`tests/test_epistemico.py` (quinta corrida).

---

## 2. El diseño secuencial — DOS decisiones, y sin ellas no se congela

El pre-registro `GEMELO/SECUENCIAL/DISEÑO.md` sigue **NO CONGELADO**.
Fue rechazado **cuatro veces** por `estadistico-adversario`; los cuatro
rechazos fueron correctos. El α ya está firmado (§2a-bis). Lo que bloquea
ahora es **la regla de deduplicación** (§2a), que es nueva y urgente, y el
**MDE** (§2b), cuyo número propuesto quedó retirado por derivarse en la
escala equivocada.

### 2a. La regla de deduplicación — con el forense hecho, la pregunta cambió

**Actualizado 1-sep-2026, quinta corrida.** Nicolás pidió el forense del
origen antes de firmar, con el argumento correcto: *"quiero saber qué es
una fila antes de decidir"*. El forense está en
`GEMELO/resultados/dedup_opciones.md` y **cambió la pregunta**, porque los
30 duplicados **no son un fenómeno sino dos, con orígenes distintos**:

| Grupo | Sesiones | Origen, con evidencia |
|---|---|---|
| **10 pares (20 filas)** | 31-jul, 5-ago | **Defecto de la ruta de sellado.** `snapshot.py`:140 calcula `sesion_objetivo` con `ahora_utc` —el reloj de pared del proceso, estampado en `:111`— en vez de con `available_at`. Cuando el sello cruza medianoche/01h UTC, `proxima_sesion_despues_de` salta una sesión asiática **ya abierta**. Coincide con el mecanismo que la Etapa 5.0.1 ya había diagnosticado para el 29-jul y el 3-ago. |
| **5 pares (10 filas)** | 12-ago, 18-ago | **Feriados de mercado reales**, sin anomalía de reloj: XTKS cerrado el 11-ago, XKRX cerrado el 17-ago (confirmado con `exchange_calendars`). **Las dos emisiones están igualmente a tiempo.** |

**Por qué esto cambia la decisión:** una sola regla para los dos grupos
sería arbitraria por construcción. En los 10 pares de reloj hay una fila
**fuera de especificación** y otra correcta. En los 5 de feriado **ninguna
de las dos es más legítima**: el mercado no abrió, y las dos emisiones
apuntaron honestamente a la siguiente sesión que existía.

**Y hay un hecho que hay que mirar antes de firmar `keep="last"`.** El
forense lo midió: en estos 15 pares, **la fila fresca nunca discrepa de la
baseline** (10 veces coinciden en acierto, 2 en error, 3 pares aciertan
las dos), mientras **la fila vieja discrepa 12 de 15 veces — 10 a favor de
la baseline y 2 a favor del modelo**. Descartar la vieja **retira
selectivamente errores del modelo**. Eso no es un argumento contra
`keep="last"`, y se escribe como aritmética verificable y no como
sospecha: es la explicación mecánica de por qué esa rama da p = 0,032. Hay
que saberlo al firmar.

**Las tres ramas, computadas completas** (n vivo 256, `excluir_cero`):

| | `keep="first"` | `keep="last"` | sin deduplicar |
|---|---|---|---|
| n | 241 | 241 | 256 |
| ventaja | +6,64 pp | **+9,96 pp** | +6,25 pp |
| McNemar b/c | 72/56 | 70/46 | 72/56 |
| p (χ²cc / exacta) | 0,1849 / 0,1847 | **0,0327 / 0,0323** | 0,1849 / 0,1847 |

**El p va al final y como CONSECUENCIA, nunca como argumento.** El orden
correcto es: primero qué es una fila, después qué sale.

**Lo que el ORIGEN sugiere**, separado a propósito de las consecuencias:
tratar los dos grupos distinto — para los 10 pares de reloj, quedarse con
la fila que apunta a la sesión correcta; para los 5 de feriado, no hay
criterio de origen que prefiera una, así que la regla ahí es una elección
de convención y hay que declararla como tal.

**Lo que el forense NO pudo determinar:** la causa última del DarkWake que
provocó los sellos tardíos, la exactitud del calendario de
`exchange_calendars` contra una fuente externa, y el dropout parcial de
tickers del 17-ago. Los logs de esas fechas **ya rotaron y no existen**.

### 2a — ESTADO al 1-sep, tarde: FIRMADA, aplicada, y abrió DOS preguntas

**Nicolás firmó**, y su texto es el criterio: *«Los dos grupos se tratan
por separado… Grupo del defecto de `snapshot.py`: la fila válida es la que
tiene la sesión objetivo correcta según `available_at`, no la más
reciente. **El criterio es la corrección de la sesión, nunca la
frescura.** Grupo de feriados reales: las dos emisiones están igualmente a
tiempo, así que no es un problema de deduplicación… QUEDA PROHIBIDO
`keep="last"`.»*

**Aplicada en el ejecutable** (`backtest/linea_base.py`:
`deduplicar_por_sesion`, activa por defecto en `cargar()`), sin ninguna
lista de fechas: el criterio se implementa solo y separa los dos grupos
por construcción. `dedup` **dejó de ser un eje** de
`GEMELO/bifurcaciones.py` (768 → 192 celdas; **el veredicto de 0 celdas
con p < 0,05 por clúster NO cambió**).

**El desenlace fue un TERCERO, y hay que saberlo:**

| rama | n | ventaja | b/c | p exacta |
|---|---|---|---|---|
| sin deduplicar (publicado) | 248 | +6,5 pp | 72/56 | 0,1847 |
| **REGLA FIRMADA** | **238** | **+9,7 pp** | **72/49** | **0,0451** |
| `keep="last"` (prohibida) | 233 | +10,3 pp | 70/46 | 0,0323 |

La firma se tomó **conociendo 0,1847 y 0,0323**. Produjo **0,0451**, que
**cruza α = 0,05** y no era ninguno de los dos. El criterio sigue siendo
el correcto; el desenlace se declara. Mecanismo: `b` no se mueve (72), `c`
baja de 56 a 49 — de las 10 filas retiradas, **7 eran discordantes y las 7
favorecían a la baseline; ninguna al modelo**. Misma asimetría que motivó
prohibir `keep="last"`; justificación distinta (no-correspondencia
demostrable, no frescura). **Las dos cosas van juntas o no van.**

**Ninguna cifra publicada se movió.** El parche está escrito y no
aplicado: `GEMELO/resultados/parche_dedup.md`, trece bloques con
archivo:línea.

### 2a-ter. Las 15 filas SIN pareja que tampoco calzan — NUEVA, abierta

**Qué decidir, en una frase:** si además de deduplicar se retiran las
**15 filas sin pareja** cuya `sesion_objetivo` tampoco corresponde a su
`available_at`.

**Por qué es una pregunta y no un corolario.** La regla firmada **arbitra
entre dos filas que compiten** y siempre deja una. Estas 15 están **solas
y mal**: no hay hermana correcta que conservar, así que retirarlas es
**descartar sin reemplazo**, una operación distinta de la que se firmó.
La firma no las previó porque nadie sabía que existían — el forense de
anoche las buscó con `GROUP BY … HAVING COUNT>1` y por definición no
podía verlas.

**La evidencia** (recomputando `proxima_sesion_despues_de(exchange,
available_at)` sobre TODAS las filas, no sólo las duplicadas): **25 filas
no calzan**, 10 son el lado viejo de los pares ya cubiertos, y 15 no
tienen pareja:

| filas | fecha de emisión | apuntan a | debían apuntar a | por qué no hay pareja |
|---|---|---|---|---|
| 7 | 2026-08-05 | 08-07 | **08-06** | el snapshot del 08-06 tuvo caída total de datos |
| 8 | 2026-07-05 | 07-06 | **07-03** | sello manual con casi 3 días de atraso |

**El detalle que muestra el sistema funcionando:** en el caso del 5-jul la
sesión correcta (07-03) **ya había cerrado** al sellar, así que con el
ancla temporal buena esas 8 filas pasarían a `no_verificable_timing` en
vez de `verificada`. **No las descartaría un criterio nuevo: las
descartaría la regla maestra que el proyecto tiene desde la Etapa 4.6.**

**Las dos cifras, para decidir con las dos a la vista** (corte publicado,
`excluir_cero`):

| | n | ventaja | b/c | p exacta |
|---|---|---|---|---|
| regla firmada (aplicada) | 238 | +9,7 pp | 72/49 | 0,0451 |
| **+ coherencia (no aplicada)** | **223** | **+14,3 pp** | **69/37** | **0,0024** |

Otra vez el retiro es asimétrico: `c` baja de 49 a 37 y `b` sólo de 72 a
69. Con eso a la vista, y no sin eso.

**Cabo suelto anotado y no investigado:** el snapshot del **2026-08-06
perdió el 100% de sus predicciones**. Es una anomalía aparte.

**Expediente:** `GEMELO/resultados/parche_snapshot140.md` (Frente C),
`GEMELO/resultados/parche_dedup.md` §3, y
`backtest/linea_base.py:filtrar_sesion_coherente`, que computa la rama y
**no la aplica en ningún camino por defecto**.

**Costo de postergarla un mes:** bajo mientras el parche del README no se
aplique. Si se aplicara antes de decidir esto, el README publicaría +9,7
pp sabiendo que hay una rama declarada de +14,3 pp sin resolver — y eso
es peor que no publicar ninguna de las dos.

### 2a-quater. Los 5 pares de feriado real — ítem de CALENDARIO Y UNIVERSO

**Qué decidir, en una frase:** qué hace el sistema cuando emite una
predicción cuya sesión objetivo natural cae en un día con **la bolsa
cerrada**, y por lo tanto dos emisiones consecutivas apuntan legítimamente
a la misma sesión.

**Por qué NO es un problema de deduplicación, con la firma delante.**
Nicolás lo escribió: *«las dos emisiones están igualmente a tiempo, así
que no es un problema de deduplicación. Va a la cola como ítem de
calendario y universo, y no se resuelve acá.»* La regla firmada lo
confirma **por construcción y sin saber nada de feriados**: en estos 5
pares **las dos filas calzan** con
`proxima_sesion_despues_de(exchange, available_at)`, así que la regla se
abstiene sola y las deja enteras. Eso es evidencia de que el criterio
distingue bien, no una laguna.

**La evidencia, los 5 pares:**

| sesión objetivo | pares | tickers | emitidas | causa |
|---|---|---|---|---|
| 2026-08-12 | 4 | 3436.T, 4063.T, 6857.T, 8035.T | 10-ago y 11-ago | **XTKS cerrado el 11-ago** |
| 2026-08-18 | 1 | 005930.KS | 14-ago y 17-ago | **XKRX cerrado el 17-ago** |

Las dos filas de cada par comparten `gap_pct` idéntico —es el mismo
desenlace de mercado— y **discrepan en `acierto_gap` en los 5 pares, sin
excepción**: el modelo corrió con datos de días distintos y llegó a signos
opuestos sobre el mismo evento, las cinco veces. O sea que contarlas dos veces mete el
mismo desenlace dos veces en el denominador, con dos veredictos
contrarios que se cancelan.

**Las tres formas de tratarlo, sin recomendación** (es una decisión de
diseño del sistema, no de medición):

1. **Dejarlas las dos**, como hoy. Es honesto —las dos predicciones
   existieron— pero pesa un desenlace de mercado el doble que los demás.
2. **No emitir** cuando la sesión objetivo ya tiene una predicción viva
   para ese ticker. Toca la ruta de sellado (`snapshot.py`), o sea que es
   una decisión con corte de método y fecha.
3. **Promediar o marcar** el par en la capa de medición, sin tocar el
   sellado. Barato y reversible, pero inventa una fila que nadie emitió.

**Qué se bloquea:** nada operativo. Pero cada feriado de XTKS o XKRX que
caiga en día hábil vuelve a producir un par, así que el conteo crece
solo — es el mismo tipo de goteo que §1-bis.

**Cuánto pesa hoy:** 10 filas de 253 (4,0%).

### 2a-bis. El α declarado — RESUELTO el 31-ago

**Decidido: α = 0.05 nominal**, con la banda [0.046, 0.079] publicada como
limitación declarada y el estimador de reestimación fijado por adelantado.
Razón de Nicolás: el proyecto publica su incertidumbre en todo lo demás;
absorberla en un número más redondo sería lo contrario del estilo de la
casa. Se descartó la recomendación que el propio documento hacía (α=0.10).

**La banda que se publica**, medida con 20.000 réplicas e intervalos —
el α real del plan entero según la autocorrelación entre fechas:

| autocorrelación real | α que entrega el plan |
|---|---|
| +0.00 | 0.0458 [0.0430, 0.0488] |
| +0.10 | 0.0598 [0.0566, 0.0632] |
| +0.20 | 0.0700 [0.0665, 0.0736] |
| +0.30 | 0.0791 [0.0755, 0.0830] |

La autocorrelación medida hoy es **−0.134 ± 0.169** sobre 35 fechas: el
signo es benigno, pero los datos **no distinguen 0 de +0.2**, así que la
banda se cita entera y no se estrecha por el punto.

### 2b. El MDE — la que fija el calendario

**Qué decidir:** qué efecto mínimo se declara de interés, porque esa cifra
fija sola la fecha en que el proyecto va a saber si su ventaja es real.

**Estado: el número propuesto quedó RETIRADO.** La cuarta corrida lo
derivó de V6 y propuso 7 pp, pero el cuarto dictamen mostró que se derivó
en la escala del **retorno de sesión** cuando el endpoint congelado es
**`acierto_gap`**. Recomputado en la escala del endpoint por el script
versionado: **8,96 pp con IC95 [6,67, 11,32]**. El número que reemplaza al
7 pp **es un rango, no un punto** — que es justo lo que le faltaba.

**Lo que sí quedó establecido, y vale igual:** **V6 no puede fijar el
MDE.** Sobre la ventana sellada SMH **cayó 5,18%**, así que la tasa de
acierto necesaria para superarlo neto de 25 pb es **54,9% — por debajo del
59,7% que ya consigue la baseline**. Con un benchmark negativo la baseline
sola aprueba V6, y V6 no exige nada del modelo. Un MDE que depende de si
el benchmark subió o bajó no es un MDE.

**Expediente:** `GEMELO/SECUENCIAL/DISEÑO.md` §A3.1 y
`GEMELO/SECUENCIAL/mde_desde_v6.py`.

| Si el MDE es… | …la respuesta llega en |
|---|---|
| +10 pp | jul-2027 |
| +8 pp | ene-2028 |
| +7 pp | jun-2028 |
| +6 pp | ene-2029 |
| +5 pp (el umbral de `RELEVO.md`) | feb-2030 |

**Qué se bloquea mientras 2a y 2b estén abiertas:** el pre-registro no se
congela, y sin congelar no sirve — su valor entero es haber fijado las
reglas antes de ver los datos. `mirada.py` tiene un candado (`MDE_FIRMADO
= None`) y se niega a computar mientras siga así.

**Costo de postergarlas un mes:** hasta octubre, cero. **A partir del
2026-11-19, infinito**: llegado ese día, o el documento está congelado —y
entonces la mirada vale— o no lo está, y entonces cualquier cifra que se
mire ese día es una mirada más sin declarar, que es exactamente el pasivo
que este diseño existe para cortar.

**Hay una tercera pregunta menor, que va con estas dos:** la regla de
varianza elegida cuesta ~1,7 pp de potencia, y la corrección de N_max que
el propio diseño hizo reparaba 0,94 pp. O se recomputa N_max (más filas,
más tarde) o se declara que la potencia del plan es **~0,76 y no 0,80**.
La segunda es barata y honesta: significa que si la ventaja real es de 10
pp, el diseño la detecta tres de cada cuatro veces en vez de cuatro de
cada cinco.

**Recomendación, marcada como tal:** +10 pp, por el argumento de §A3.1 —
diseñar para +5 pp es defendible pero empuja la respuesta a 2030, y un
diseño que tarda tres años y medio tiene alta probabilidad de romperse
antes de completarse (cambio de modelo, de universo, hueco de sellado), y
un diseño que se rompe no responde nada. Pero **es una elección de valores
sobre qué ventaja valdría la pena, no un cálculo**, y por eso no la toma
un agente.

**Dato para decidir con él, incómodo y calculado:** el pasivo de haber
mirado la misma cifra cada vez que crecía, sin declararlo, es **α entre
0,09 y 0,18** — entre 1,8× y 3,6× el 0,05 que se declaró (§A1). No
invalida ninguna cifra publicada, porque ninguna cruzó nunca el umbral;
pero tres p de subgrupos **sí** cruzaron 0,05 y hubo que retractarlos.

---

## 3. Qué hacer con la lectura del track record sellado

**Qué decidir, en una frase:** si se publica el parche que declara en el
README que la ventaja sellada no se distingue de cero y que su
concentración en julio no está establecida — y, por separado, si el
criterio R2 se reformula.

**Expediente:** `GEMELO/resultados/parche_honestidad.md`, que **reemplaza
explícitamente a `parche_documental.md`** (aquel se apoyaba en el
scan-statistic que después resultó mal construido; queda retirado, no
aplicar). Contiene el texto propuesto, **los doce bloques que se mueven,
uno por uno con archivo:línea**, y el argumento de R2 con sus dos
lecturas.

**La parte delicada, escrita como está:** la ventana 15-23-jul de R2 se
eligió post-hoc y el scan-statistic corregido **no la establece como
especial**, así que R2 congela como vara permanente una ventana que no
está establecida. Pero R2 solo descarta, nunca aprueba, y bajarla justo
cuando se descubre que el campeón tampoco la pasa sería exactamente lo que
un pre-registro existe para impedir. Las dos lecturas están escritas con
su argumento; **la elección es de Nicolás**.

**Qué se bloquea:** el README y tres archivos vivos de referencia
(`cifras-canonicas`, `estadistica-evaluacion`, `estadistico-adversario.md`)
siguen citando +6,5 pp sin la advertencia. Cualquiera que lea el proyecto
hoy —incluida una sesión futura de este mismo agente— cita la cifra sin el
matiz que la vuelve honesta.

**Costo de postergarla un mes:** técnicamente cero. El costo es de
integridad pública, y se acumula.

**Recomendación:** aplicarlo es barato y no cambia ninguna cifra, solo
agrega contexto. Agrupar con §7 (las cinco preguntas del WS4): es más
barato resolver varias preguntas de reporte en una sola pasada.

---

## 3-bis. El McNemar: dos rutas, ninguna equivocada

**Qué decidir:** cuál de las tres salidas se toma ante el hecho de que el
proyecto tiene **dos árbitros** para la misma pregunta.

**El hallazgo, y no es el que se creía:** el 0.1849 del README es el **χ²
de McNemar con corrección de continuidad** (0.184898) y el 0.1847 del
módulo es la **binomial exacta** (0.184683). Mismo par (b=72, c=56), mismo
n, **métodos distintos, ninguno mal**. Verificado por varas independientes
en las dos rutas.

**No es una cifra, son cuatro**, y es una regla escrita rota: los tres p
de la ventana sellada (0.1158 / 0.2542 / 0.1849) y el de la línea base
congelada (0.4633) salen de `backtest/linea_base.py`:126, que reimplementa
McNemar a mano cuando `.claude/rules/backtest.md`:26-27 dice literal que
no se reimplemente. **Atenuante:** `linea_base.py` es del 25-ago y la
regla del 30-ago — la regla llegó después y nadie volvió a mirar el código
que ya estaba.

**Lo que traba el arreglo obvio:** `GEMELO/DISEÑO.md` §2.8 **congeló**
p = 0.4633 en un pre-registro. Migrar al árbitro la mueve a 0.4635, y un
pre-registro congelado no se toca. **Chocan dos reglas del propio
proyecto.**

**Expediente completo, con las tres opciones costeadas y el parche de los
doce bloques escrito y no aplicado:**
`GEMELO/resultados/mcnemar_dos_rutas.md`.

**Recomendación, marcada como tal: la opción A** — declarar el método al
lado de cada p y no mover ningún dígito. Ninguna conclusión cambia (el
mayor Δ es 0.0003), el χ² con corrección de continuidad no es el método
malo, y **lo que falta es una palabra, no un número**. Obliga igual a
escribir la excepción en `.claude/rules/backtest.md`: una regla con una
excepción no escrita es una regla que se vuelve a romper.

---

## 4. La cuenta AMD para Vivado — bloquea TODOS los hitos del ramo

**Qué hay que hacer, en una frase:** crear una cuenta en AMD y completar
el formulario de control de exportación, que es lo único que separa al
proyecto de tener place & route.

**Por qué es de Nicolás y no de un agente:** no es un problema técnico. El
disco alcanza (946 GB libres), la RAM alcanza, no hace falta root, y **la
licencia es gratis** — el tier BASIC cubre toda la serie 7 y cuesta $0
(las ediciones "WebPACK" y "Standard" ya no existen desde 2026.1). El
bloqueo es que todos los instaladores redirigen a
`account.amd.com/.../xef.html`: **cuenta AMD más formulario de control de
exportación. Es un acto de identidad, de la misma clase que pushear.**

**Qué se bloquea mientras esté abierta:** todo lo que necesite place &
route — **Fmax, utilización de slices, cierre de temporización y
bitstream**. Sin eso, `GEMELO/MICRO/SINTESIS_A7.md` reporta LUTs, FFs,
BRAM y DSP medidos con `yosys synth_xilinx`, y **todo lo demás queda
marcado como estimación**. Y sin bitstream no hay hito en silicio, que es
el proyecto del ramo.

**Costo de postergarla un mes:** depende del cronograma de la materia, que
este documento sigue sin conocer. **Es dato que falta, no indecisión.**

**Dos avisos verificados, para cuando se haga:** este WSL2 es Ubuntu
26.04, que **no está en la lista soportada de UG973** (22.04/24.04); y
programar por JTAG desde WSL2 exige `usbipd-win`. **Instalar Vivado del
lado Windows evita las dos cosas.**

**La placa y la arquitectura: RESUELTAS el 31-ago.** Arty A7-100T
(XC7A100TCSG324-1), y arquitectura de dos modelos — general en la A7, HFT
más adelante en una KR260. La Go Board queda cerrada con su número: el
campeón necesita 1.545 celdas y tiene 1.280.

**Lo que la síntesis ya midió, y cambia el plan:** el cuello **no es la
lógica ni la BRAM** (que sale en 0) ni la DDR3L — para la carga real no
topa ninguno, porque la plataforma emite 8 mensajes por día contra los
47,6 M/s que saturarían la memoria. El cuello, si se quiere escalar, es el
**DSP48E1 a 240 tickers**. Y la mejor mejora disponible es **gratis**: la
ingesta ancha baja la latencia de **32 a 11 ciclos** con el área *bajando*
(108 → 93 LUT6), y también bajaba en el iCE40 — **no estaba bloqueada por
espacio, sólo nadie lo había preguntado.**

**Decisiones menores que quedan, todas documentadas en
`GEMELO/MICRO/PROYECTO_RAMO.md`:** el ancho de ingesta (B=4 es el punto
sensato; B=28 sólo con fuente interna desde BRAM, porque la placa expone
32 señales de Pmod y no 224); si el pipeline crece hacia el 4.6.0 completo
(**cabe**: ≈864 LUT6, 1,4% — y esa misma pieza es 309% de la Go Board
entera); y si la Go Board sigue en juego para algo.

---

## 5. La mina de `ventana_larga.py` — la única con riesgo de republicar algo falso

**Qué decidir, en una frase:** qué se hace con
`GEMELO/ventana_larga.py:314-345`, que sigue emitiendo la cifra de
contaminación del 8,6% ya refutada, y con
`tests/test_ventana_larga.py:186`, que **la exige por contrato**.

**Expediente:** `GEMELO/resultados/expediente_pit.md`, hallazgo (c);
la refutación original en `auditoria_ws3.md:213-236`.

**Por qué es una mina y no una deuda:** el test verde es lo que hace
peligroso al código. Cualquiera que re-corra el WS3 —una sesión futura, un
`pytest` de rutina que alguien lea— **republica la falsedad, y el test
confirma que está bien**. Es el único ítem de esta lista donde no hacer
nada tiene un modo de falla activo.

**Qué se bloquea:** nada, hasta que alguien re-corra el WS3.

**Costo de postergarla un mes:** bajo en probabilidad, alto en
consecuencia. No se degrada con el tiempo; espera.

**Recomendación:** corregir el código y el test juntos, en una sola pasada
y con acta. Es chico y es de la clase de arreglo que no admite quedar a
medias: dejar el código corregido con el test viejo, o al revés, es peor
que el estado actual.

---

## 6. Las dos afirmaciones de `RTL.md` — CERRADA el 31-ago

**Resuelto.** Las dos afirmaciones refutadas (la tolerancia de 0,00188 pp,
inalcanzable —medido 0,00474—, y el "100% de coincidencia" de la decisión
discreta, falso: 2 de 181) quedaron **corregidas en su sitio en `RTL.md`
con nota de errata fechada**, que es lo que corresponde a un documento
commiteado. El hallazgo conceptual quedó escrito: **lo discreto es MÁS
frágil en la frontera, no inmune** — lo contrario de lo que razonaba el
documento original.

**Y un hallazgo del mismo frente, que se registra como tal:** el encargo
pedía además corregir el encuadre de "la FPGA como motor de backtesting".
**Ese encuadre no existía**: `RTL.md`:16 dice "validado por backtest" (el
backtest valida al RTL, no al revés) y `fpga.md`:24-26 dice literal que la
ventaja del hardware "no es 'más rápido'... es determinismo". No se
fabricó una corrección donde no había nada que corregir.

---

## 7. Las cinco preguntas del WS4 (§33.8)

**Qué decidir, en una frase:** si se corrige la ventana larga a la
convención congelada, cómo se reconcilia el §32.5 refutado, cómo se
reporta Fráncfort, y si las 8 filas del 29-jul (sesión saltada) siguen en
las métricas.

**Expediente:** `DECISIONES.md` §33.8. Se solapa con §5 de esta lista.

**Costo de postergarla un mes:** bajo, con precedente — llevan abiertas
desde antes del 26-ago sin romper nada.

**Recomendación:** agruparlas con §3 y §5 en una sola pasada de reporte.

---

## 8. Los umbrales de `GEMELO/RELEVO.md`

**Qué decidir, en una frase:** si el margen mínimo de 5 pp y el n≥150
filas/60 días son los correctos.

**Expediente:** `GEMELO/RELEVO.md`. **Nota nueva:** la propuesta de
criterio R4 que vivía en `parche_documental.md` cayó junto con ese
documento; si se quiere un R4, hay que rehacerlo sobre la v2 de
`concentracion.md`.

**Qué se bloquea:** nada hoy — no hay ningún retador corriendo.

**Costo de postergarla un mes:** bajo, pero no lineal: el día que GEMELO
6.0.0 produzca un candidato serio, esto pasa de "no urgente" a
"bloqueante" de un día para el otro.

**Recomendación:** no dejarla para el mismo día que aparezca un candidato
— para entonces, un pre-registro fijado bajo presión deja de ser un
pre-registro.

---

## 9. Datos point-in-time — CERRADA con recomendación de no gastar

**Qué se recomienda, en una frase:** **no comprar nada, cero dólares.**

**Expediente:** `GEMELO/resultados/expediente_pit.md` (575 líneas, diez
proveedores con precio verificado).

**Por qué se cierra, y no es una cuestión de presupuesto:**

- La contaminación por revisión de precios **es cero, no 8,6%** — el 8,6%
  era un artefacto del join; alineando por `sesion_objetivo` la desviación
  es 0,00% sobre 223 filas.
- Y lo que sostiene la conclusión **no es la muestra, es un teorema**: el
  factor de ajuste escala `open(t)` y `close(t−1)` por igual, y el objetivo
  es un cociente. Vale para las 14.618 filas, no solo para las 223
  verificables. La verificación empírica confirma el teorema, no extrapola
  una tasa.
- Ninguna conclusión publicada depende críticamente del PIT de precios:
  para borrar los +15,66 pp haría falta que el 15,7% de las filas
  estuvieran contaminadas a favor del modelo, y la regla de tres sobre
  0/223 acota en ≤1,35% — **11,6× de holgura**.
- **Lo que sigue abierto es otra cosa** —la composición del universo, el
  sesgo de supervivencia— y **datos PIT de precios no la arreglan**.
  Ninguno de los diez proveedores vende constituyentes históricos del ^SOX.

**Qué queda como decisión y no como cierre:** aceptar la recomendación. Y
un canal residual barato: medir fechas ex de dividendos sobre la sesión
objetivo (~0,9% de filas), que es gratis y nadie midió.

---

## 10. Expedientes 6B y 6C, y si `.claude/` se versiona

Sin cambios desde la segunda corrida; se dejan agrupados porque ninguno
bloquea nada y todos son baratos.

- **6B — visibilidad de `ts_emision`** (campo `commiteado_en` aditivo,
  bajo riesgo) y **estampida de timers** (auditar idempotencia de los 6
  jobs ante un disparo simultáneo; nadie lo investigó nunca, ni se sabe si
  es un problema real). `expedientes.md` §6B.1 y §6B.3. La opción 2 del
  §6B.3 es de solo lectura y se puede hacer en cualquier sesión.
- **6C — alcance del pin de pandas**: escribir el test de estabilidad de
  los sitios de `pd.concat` antes de decidir el alcance del pin.
  `expedientes.md` §6C.
- **`.claude/` versionado o local**: es una preferencia, no un riesgo.

---

## 11. `CLAUDE.md` afirma que el Mac es titular, y no lo es

**Qué decidir:** cómo se corrige la sección de la etapa 5.0.3 de
`CLAUDE.md`, que dice que el Mac "stays **titular**" y que
`MKI_MODO=sombra` vive en la línea 18 de `.env`. **Las dos son falsas
hoy** (`modo.py` → `titular` en este PC, seis timers emitiendo).

**Por qué no lo arregló un agente:** `CLAUDE.md` es el documento que
gobierna cómo trabaja el agente en cada sesión. Cambiarlo cambia el
comportamiento de todas las sesiones futuras — es una edición que se ve,
no un arreglo de paso.

**Qué se bloquea:** nada operativo, pero **toda sesión nueva arranca
leyendo que la máquina en la que corre no es la titular**, que es
exactamente la clase de desfase que el proyecto documenta como errata en
vez de cometer.

**Costo de postergarla un mes:** bajo pero acumulativo, y con precedente:
esta misma afirmación ya sobrevivió dos corridas como "errata pendiente de
registrar" en `ESTADO.md` hasta que alguien la borró sin registrarla
(§57).

**Recomendación:** corregir la sección con una nota fechada, en el mismo
movimiento en que se toque `CLAUDE.md` por cualquier otra razón.

---

## 12. Una "vara independiente" de síntesis que nadie verificó que lo sea

**Qué decidir, en una frase:** si la frase de `GEMELO/MICRO/SINTESIS_A7.md`
:538-540 —"dos métodos distintos, mismo número: eso es la vara
independiente", sobre los 0,00474 pp de error de cuantización— se sostiene
o se retracta.

**Por qué está acá:** el `guardian-constitucion` la marcó como NO
VERIFICADO en el cierre de esta corrida. Nadie comprobó si el arnés de
`SINTESIS.md` §5 (181 filas) y `medir_ancho_error.py` (189 filas) son
**familias de método realmente distintas**, o **el mismo álgebra de
cuantización recorrida dos veces** — que es precisamente el defecto que la
regla §52 acaba de nombrar, y el que ya se cobró una pieza en esta misma
corrida.

**Qué se bloquea:** nada operativo. Es una afirmación de validación en un
documento de diseño interno.

**Costo de postergarla un mes:** bajo, pero con la peor forma: **es una
afirmación de haber verificado**, y ésas se citan sin volver a mirarlas.
Viene en verde de la corrida anterior y no se reabrió de paso a propósito.

**Recomendación:** medirlo explícitamente antes de volver a citar esa
frase. Si las dos rutas comparten el álgebra, la frase se retracta como se
retractaron las otras dos de esta corrida — no es grave, es el precio de
tener la regla.

---

## 13. El hook que atajaría la clase de error que ningún test ataja

**Qué decidir, en una frase:** si se instala un hook de pre-commit que
rechace un `.md` de resultados que no cite un `.py` versionado del mismo
frente.

**De dónde sale.** El Frente F de la quinta corrida convirtió en test seis
de las siete clases de error de las cinco corridas. **La que resistió es
la raíz de la segunda corrida** (§45): el análisis completo vivió en
comandos sueltos de una sesión que se perdió, y sólo se pudo auditar
porque unos archivos intermedios sobrevivieron por casualidad en un
directorio temporal.

**Por qué ningún test lo ataja:** un test estático no puede detectar la
ausencia de un archivo que nunca se escribió. No hay nada que escanear. Y
el sustituto obvio —"toda cifra publicada nombra el script que la
produce"— o es tautológico o dispara sobre medio repo, y **un test
epistémico que grita por todo se termina desactivando**.

**Y de ahí cuelga una segunda clase**, también sin test posible:
desviarse de un criterio pre-registrado congelado sin declararlo — el
umbral del §44 congelado en 0,0 mientras el análisis usaba 12,9 de un
subconjunto de entrenamiento, del que dependía la conclusión publicada.
Detectarlo exige comparar lo que el código **usó** contra lo que el
pre-registro **congeló**, y eso sólo es posible si el análisis está
versionado. **Misma raíz.**

**Qué se bloquea:** nada hoy. Es prevención.

**Costo de postergarla un mes:** bajo pero mal distribuido — no pasa nada
hasta que pasa, y cuando pasa cuesta dos rondas de auditoría y una
retractación, que es exactamente lo que costó en agosto.

**Recomendación:** es de proceso, no técnica, y por eso el agente que lo
propuso **no lo instaló solo** — hizo bien. Un hook que rechaza commits
cambia cómo trabaja todo el mundo, y eso lleva firma.

**Un candidato menor que sí es convertible en test**, por si vale para la
próxima tanda: todo script de resultados que lea `senales.db` debe anclar
la lectura con `hasta_sello` — `mde_desde_v6.py` escribió su propio SQL
sin ancla temporal y el documento dejó de reproducir el día que se
firmaba. Es un test AST de una tarde.

---

## 14. El registro de intentos merece módulo propio — CERRADO a medias

**Qué se hizo:** el conteo dejó de ser un entero mágico. `N_INTENTOS_ACUMULADO`
se **calcula** como suma de `REGISTRO_INTENTOS`, 20 tramos con procedencia
línea a línea. **N = 86.** El test viejo **no protegía al 25 de corromperse:
lo protegía de corregirse** — es la cuarta regla de la casa en su forma más
limpia. El test nuevo fija la propiedad y trae tres contrapruebas.

**Y se cerró de paso un vector vivo que sí podía voltear un veredicto:**
`GEMELO/control_lineal.py` tenía `n_intentos` con default **9**, y
`experimento.py` lo llamaba sin pasar N — mientras `backtest/inferencia.py`
había quitado ese mismo default **a propósito, con acta (§26.1) y con test**.
`SR0(9) = 0,9986` contra `SR0(86) = 1,6266`: **regalaba 0,63 de umbral**, y a
Sharpe anualizado de 1,2-1,5 **V5 se daba vuelta de PASA a NO PASA**.
Corregido, con test que fija que la firma no pueda volver a tener default.

**Qué decidir, y es lo que queda:** si el registro se mueve a
`GEMELO/registro_intentos.py` para que `relevo_asiatico`, `control_lineal`,
`ventana_larga` y `veredicto_51` importen del mismo sitio. **Costo ~40 min y
un import nuevo en cuatro archivos.** Hay evidencia a favor: al pasar el N
explícito apareció un **import circular** que hubo que resolver con import
diferido — ese ciclo **es** el síntoma de que el registro no tiene casa.

**Y una cifra publicada que no se movió:** `README.md`:253 dice **"Va en
25"** en la portada. **Regla de los doce bloques: lleva firma.**

> **Actualización 1-sep-2026 — y el argumento cambió de forma.** El banco de
> cláusulas sumó cinco tramos (C1, C2, C3a, C3b, C4) y el registro pasó de
> **86 a 91**; `veredicto_51.py` acompañó a **97**. Las cifras de arriba
> —`SR0(86) = 1,6266`, "20 tramos"— siguen siendo lo que se midió ese día y
> se dejan como están. Lo que se aprende es otra cosa: **el N subió dos veces
> en una semana**, así que clavar cualquier entero en la portada es empezar
> otra vez esta misma discusión el mes que viene. Ver la opción (d) de
> `espera_firma.md` §7: publicar la fuente y la fecha, no el número.
>
> **Y hay un arrastre que necesita ojo de Nicolás.** `veredicto_51.py`
> conserva **92 dentro de `BANDA_N`** —además de los valores nuevos— para que
> el resumen ya sellado del 5.1 siga reproduciendo. Funciona, pero la forma
> correcta es **pinchar el instante, no conservar el número suelto**, como se
> hizo con `CORTE_SECCION_2`. Queda declarado como deuda, no aplicado: tocar
> la reproducción de un resumen sellado no es movimiento de una tanda
> autónoma.

---

## 15. B4 y B5 no son evaluables sobre la ventana larga

**Qué pasó:** al corregir la fuga B-1 —el sentimiento se cortaba por fecha de
publicación y nunca miraba `analizado_en`— **sobreviven 288 de 4.152 filas, el
6,94%**. El 93,1% de las filas de B4/B5 se emite con las tres features de
noticias en la constante 0,0.

**La distinción que hay que preservar al citarlo, y no es sutil:** sus cifras
se leen como **"la capa de precios con columnas constantes"**, jamás como
**"las noticias no aportan"**. Son afirmaciones distintas y el dato sólo
sostiene la primera.

**Y el alcance real:** B0, B1, B2 y B3 no tocan sentimiento y **siguen
evaluables** sobre la ventana completa. Son **dos baselines de seis**, no el
backtest.

**Qué decidir:** si se acepta evaluar el retador con cuatro baselines sobre la
ventana larga y las seis sólo sobre el tramo con juicios reales, o si se
espera a tener sentimiento reconstruido de verdad. **No urge hasta el 25-oct.**

---

## 16. Tres artefactos que quedaron stale o son trampa

Los tres son de la misma familia —una cifra que sobrevive a su propia
refutación— y ninguno se resolvió porque los tres tocan territorio de otro.

1. **`GEMELO/resultados/ventana_larga.{md,json}` publican el 91,4%** de
   coincidencia que **ya está refutado**: con la clave correcta
   (`sesion_objetivo`, no `["fecha","ticker"]`) da **100% sobre 214 filas, 0
   diferencias**. El **ejecutable ya está corregido con errata**; los
   artefactos quedan stale hasta que alguien re-corra el módulo. **Costo: una
   corrida.** Ojo con la lectura correcta, que el frente dejó escrita: esto no
   prueba que Yahoo no revise la historia, **sólo que no la revisó en el tramo
   auditable de 2026**.
2. **`micro/rtl/referencia.py` construye 189 casos** contra los **181
   congelados** en `vectores/parametros.vh`, porque la base siguió sellando.
   **Cualquier cosa que lo toque regenera los vectores con 189 y mueve en
   silencio todas las cifras publicadas como "181 filas".** Merece un guardia
   propio o un pin explícito del N. **Nadie lo tocó.**
3. **`CLAUDE.md` sigue afirmando que el Mac es titular** (§11 de esta lista).
   Sin cambios: su edición es de Nicolás.

---

## Lo que esta lista NO incluye, a propósito

El segundo movimiento del switch (apagar los timers del Mac, quitar
`MKI_MODO` en el PC) no entra con ítem propio: ya tiene su lugar
establecido en la skill `switch-titular`, que es su propio expediente
completo. Si Nicolás quiere verlo priorizado junto con el resto, decirlo y
se agrega.

---

## 17. Cuál es el campeón cuando sello y fuente discrepan — y la copia de insumos (NUEVA, séptima corrida)

**Qué decidir, en una frase:** (a) si para la ventana sellada el campeón
son las filas selladas —y el backtest las lee en vez de recomputarlas— o su
reconstrucción desde la fuente de hoy; (b) si se activa la copia cruda de
insumos al sellar (`GEMELO/INSUMOS/`, probada, no activada), que toca
`snapshot.py` con corte de método y va con el bump del parche `:140`.

**Expediente:** `GEMELO/resultados/fuente_canonica.md` (medición M1–M6,
candidatas C1–C5, diseño), `fuente_canonica_medicion.md`, `testigos_fuente/`
(las cuatro cachés preservadas), `GEMELO/INSUMOS/insumos.py` +
`tests/test_insumos.py`. Dictamen: verificado con correcciones aplicadas.

**Qué se bloquea:** el veredicto 5.1 sobre la ventana sellada depende hoy
de qué sirva Yahoo ese día (16 signos, 32 magnitudes).

**Costo de postergarla un mes:** cada sello que pasa sin copia es una noche
más que sólo se podrá inferir (como M6) y nunca leer.

**Recomendación, marcada como tal:** (a) las filas selladas; (b) sí, en el
mismo bump que el §1-bis.

## 18. La frase de potencia del 5.1, y R2 sobre el ancla (NUEVA)

Ver `espera_firma.md` §17. Potencia 0,36 [0,34, 0,37] frente a 9 pp con ~73
días; MDE 16,6 pp [11,0, 20,3]. R2 dispara sobre el ancla del 31-ago (+2,5
pp, IC de día [−13,6, +19,2], contiene el cero). Decidir ahora si la frase
va al generador del resumen o a `DECISIONES.md`; recomendación: lo segundo.

## 19–21. Las propuestas C, D y E con dictamen (NUEVAS)

Ver `espera_firma.md` §18–§20 y `propuestas_cde.md` con el dictamen íntegro
en `dictamen_07/`. Lo que entra: C-1 sin condición, C-2 con cinco
declaraciones, C-3 con el motivo «α real ≈ 0,31», D-1 como medición de
referencia (α del plan [0,031, 0,065]; banda firmada intacta), E-1 contra
el control lineal. Lo que no entra: E-2 (pendiente por hora con IC) y la
adenda «4×» de `tesis.md`. Los intentos ya están registrados (91 → 100).

