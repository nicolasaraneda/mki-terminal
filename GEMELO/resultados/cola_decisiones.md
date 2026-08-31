# La cola de decisiones — todo en una pantalla

Consolida cada "decisión de Nicolás" que hoy vive repartida en
`DECISIONES.md`, `expedientes.md`, `RELEVO.md`, `REPLICA.md`, `MICRO/`,
`SECUENCIAL/`, `ESTADO.md` y los resultados de las tres corridas
autónomas. Ninguna se resuelve acá.

**Orden: por costo de postergarla un mes, no por tamaño del documento que
la sostiene.** Una decisión de una frase puede costar más cara de demorar
que un documento de treinta páginas que no bloquea nada.

**Actualizada:** 31-ago-2026, cierre de la tercera corrida.

## Qué movió la tercera corrida

| | |
|---|---|
| **Cerró** | La compra de datos point-in-time: **recomendación de no comprar nada, cero dólares**, con diez proveedores tasados (§9). |
| **Cerró** | La elección de placa FPGA dejó de ser una estimación: hay **síntesis real** y el campeón **no cabe** en la Go Board (§4). |
| **Destrabó** | La réplica: el ensayo general pasó con cero hallazgos y hay runbook con vuelta atrás. Sigue faltando **solo la firma** (§1). |
| **Abrió** | El diseño secuencial quedó **terminado y NO congelado**: dos decisiones lo bloquean, el **α declarado** y el **MDE** (§2). |
| **Abrió** | Qué hacer con **dos afirmaciones falsas de `RTL.md`** que la síntesis refutó (§6). |
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

## 2. El diseño secuencial — DOS decisiones, y sin ellas no se congela

El pre-registro `GEMELO/SECUENCIAL/DISEÑO.md` quedó **terminado en su
aritmética y NO CONGELADO**. Fue rechazado tres veces por
`estadistico-adversario` en el mismo día; los tres rechazos fueron
correctos y están corregidos. Lo que queda no son defectos: son dos
elecciones que cambian el estándar con el que este proyecto va a juzgar su
propio modelo, y por eso no las toma un agente.

### 2a. El α declarado — la que bloquea

**Qué decidir:** si el plan declara α = 0.05 o α = 0.10.

El problema, medido: el estadístico re-estima su varianza remuestreando
fechas, y ese remuestreo es **estructuralmente ciego a la dependencia
entre fechas contiguas**. Con 20.000 réplicas e intervalos, el α real del
plan entero:

| autocorrelación real | α que entrega el plan |
|---|---|
| +0.00 | 0.0458 [0.0430, 0.0488] |
| +0.10 | 0.0598 [0.0566, 0.0632] |
| +0.20 | 0.0700 [0.0665, 0.0736] |
| +0.30 | 0.0791 [0.0755, 0.0830] |

La autocorrelación medida hoy es **−0.135 ± 0.171** sobre 34 fechas: el
signo es benigno, pero los datos **no distinguen 0 de +0.2**. Y el
proyecto tiene dos afirmaciones propias de que esa dependencia existe (el
bloque de 6 fechas de julio, y el criterio R2, que *es* una afirmación
sobre fechas contiguas).

**Recomendación, marcada como tal:** declarar **α = 0.10** y mover la
primera mirada de ~51 a ~100 fechas. Las dos hacen verdadera la promesa,
y la segunda **no cuesta alfa** (retrasar una mirada solo puede bajarlo,
regla que el propio documento ya tiene escrita) además de mejorar justo
donde el bootstrap es más débil. El argumento: esto es la primera mirada
seria a una pregunta abierta, no una presentación regulatoria, y un α de
0.10 honesto vale más que un 0.05 con letra chica.

### 2b. El MDE — la que fija el calendario

**Qué decidir:** qué efecto mínimo se declara de interés (+10 pp
propuesto, o +5 pp, o +15,66 pp), porque esa cifra fija sola la fecha en
que el proyecto va a saber si su ventaja es real.

**Expediente:** `GEMELO/SECUENCIAL/DISEÑO.md` §A3.1 (el menú con su costo
en calendario, calculado, no estimado a ojo).

| Si el MDE es… | …la respuesta llega en |
|---|---|
| +15,66 pp (el de la ventana larga) | ene-2027 |
| **+10 pp (propuesto)** | **jul-2027** |
| +6,45 pp (el punto sellado de hoy) | sep-2028 |
| +5 pp (el umbral de `RELEVO.md`) | feb-2030 |

**Qué se bloquea mientras 2a y 2b estén abiertas:** el pre-registro no se
congela, y sin congelar no sirve — su valor entero es haber fijado las
reglas antes de ver los datos. La primera mirada está escrita para el
**2026-11-19**.

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

## 3-bis. El p canónico dice 0.1849 y el módulo obligatorio dice 0.1847

**Qué decidir, en una frase:** si se corrige el McNemar p de la ventana
sellada, que está publicado como **0.1849** cuando el módulo que el propio
proyecto declara árbitro devuelve **0.1847**.

**Expediente:** hallazgo del `estadistico-adversario` en el segundo
dictamen del diseño secuencial. `evaluacion.mcnemar_exact(72, 56)` = 0.1847;
el binomial exacto bilateral de b=72 sobre 128 discordantes es 0.184683.
El 0.1849 corresponde a la medición anterior con n=240 y se arrastró a la
de n=248.

**Dónde vive el 0.1849:** `README.md`, la skill `cifras-canonicas`, y
siete veces en `DECISIONES.md`.

**Qué se bloquea:** nada. **No cambia ninguna conclusión** — 0.18 sigue
igual de lejos de 0.05, y la ventaja sigue sin distinguirse de cero.

**Costo de postergarla un mes:** cero en sustancia. Lo que cuesta es de
principio: la regla escrita del proyecto es que **el módulo es el
árbitro**, y hoy hay una cifra publicada que el módulo no reproduce.

**Recomendación:** agruparlo con §3 — si se toca el README para el parche
de honestidad, se corrige de paso, y no antes. Es un cambio de cuarto
decimal en una cifra publicada, o sea **regla de los doce bloques**:
lleva la firma de Nicolás, no la de un agente.

---

## 4. Placa FPGA y alcance de `GEMELO/MICRO/`

**Qué decidir, en una frase:** Nandland Go Board (iCE40HX1K) o Arty
A7-100T — y si no hay presupuesto para otra placa, cuál de los cinco
sacrificios se acepta.

**Expediente:** `GEMELO/MICRO/SINTESIS.md` (nuevo), `micro/TOOLCHAIN.md`,
`micro/rtl/` (RTL completo con `make`), más `fpga.md` §5 y `RTL.md` §6.

**Novedad de esta corrida — esto dejó de ser una estimación:**

| | Medido |
|---|---|
| Campeón (F1: beta × SOX) en iCE40HX1K | **1.545 LCs contra 1.280 → NO CABE** (120,7%) |
| Solo umbral, sin multiplicar (F1SP) | 742 LCs (58,0%), Fmax 114,19 MHz — **cabe, pero no es el modelo** |
| El culpable | el multiplicador 16×16 con signo: **774 LUT4, no los 200-300 estimados** |
| En Artix-7 | 1 DSP48E1 y 0,35% de LUTs — sobra placa |
| Validación funcional | **181/181 filas selladas reales, bit a bit**, latencia 32 ciclos constante |

**Qué se bloquea mientras esté abierta:** ya no la primera línea de RTL —
está escrita y simula correcto. Lo que se bloquea es **comprar hardware y
cerrar el alcance del proyecto de la materia**.

**Costo de postergarla un mes:** depende del cronograma de la materia de
Nicolás, que este documento sigue sin conocer. **Es dato que falta, no
indecisión.**

**Recomendación, ahora sí con números:** si la Go Board ya está comprada,
la opción más limpia de las cinco documentadas es el **multiplicador
serie** — preserva la aritmética *y* el determinismo a cambio de ~16
ciclos fijos de latencia. Si se puede elegir placa, la Artix-7 quita la
restricción entera con dos órdenes de magnitud de margen.

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

## 6. Las dos afirmaciones de `RTL.md` que la síntesis refutó

**Qué decidir, en una frase:** si `RTL.md` se corrige en su sitio o se le
agrega una errata fechada, y qué tolerancia se declara en su lugar.

**Expediente:** `GEMELO/MICRO/SINTESIS.md`, sección de discrepancias.

1. **La tolerancia de 0,00188 pp es inalcanzable.** Medido: 0,00474 pp.
   Se derivó para la operación equivocada (cuantizar *un* valor, no el
   producto de *dos* cuantizados más el truncado). Ningún modo de redondeo
   la alcanza.
2. **`RTL.md` §4.4 afirma que la decisión discreta coincide 100%. Es
   falso: 2 de 181 (1,1%) deciden distinto** — puntajes a milésimas del
   umbral que la cuantización deposita del otro lado. La lección va contra
   la intuición del documento: **lo discreto es *más* frágil en la
   frontera, no inmune.**

**Qué se bloquea:** nada operativo. `RTL.md` es documento de diseño
interno, no cifra publicada.

**Costo de postergarla un mes:** bajo, pero con la misma forma que §5: el
documento se sigue citando como si fuera cierto.

**Recomendación:** `RTL.md` nunca salió del repo como cifra publicada, así
que **corregir en su sitio** (la frontera de la errata es el commit). La
tolerancia nueva sale del harness, no de una derivación a mano: 0,00474 pp
medido sobre las 181 filas.

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

## Lo que esta lista NO incluye, a propósito

El segundo movimiento del switch (apagar los timers del Mac, quitar
`MKI_MODO` en el PC) no entra con ítem propio: ya tiene su lugar
establecido en la skill `switch-titular`, que es su propio expediente
completo. Si Nicolás quiere verlo priorizado junto con el resto, decirlo y
se agrega.
