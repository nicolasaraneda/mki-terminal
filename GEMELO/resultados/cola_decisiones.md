# La cola de decisiones — todo en una pantalla

Consolida cada "decisión de Nicolás" que hoy vive repartida en
`DECISIONES.md`, `expedientes.md`, `RELEVO.md`, `REPLICA.md`, `MICRO/`,
`SECUENCIAL/`, `MICRO/`, `ESTADO.md` y los resultados de las cuatro
corridas autónomas. Ninguna se resuelve acá.

**Orden: por costo de postergarla un mes, no por tamaño del documento que
la sostiene.** Una decisión de una frase puede costar más cara de demorar
que un documento de treinta páginas que no bloquea nada.

**Actualizada:** 1-sep-2026, cierre de la cuarta corrida.

## Qué movió la cuarta corrida (31-ago/1-sep)

| | |
|---|---|
| **Resolvió** | **α = 0.05** nominal con la banda [0.046, 0.079] publicada. Firmado. |
| **Resolvió** | **Placa: Arty A7-100T**, y la arquitectura de dos modelos (general en la A7, HFT más adelante en una KR260). Firmado. |
| **Cerró** | Las **dos afirmaciones refutadas de `RTL.md`**: errata fechada en su sitio (era el viejo §6). |
| **Cerró** | El **McNemar 0.1849 vs 0.1847**: ninguno está mal, son dos tests. Pero abre otra cosa (§3-bis). |
| **Abrió** | **La regla de deduplicación** — la más urgente de todas, y la que bloquea el pre-registro (§2a). |
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

## 2. El diseño secuencial — DOS decisiones, y sin ellas no se congela

El pre-registro `GEMELO/SECUENCIAL/DISEÑO.md` sigue **NO CONGELADO**.
Fue rechazado **cuatro veces** por `estadistico-adversario`; los cuatro
rechazos fueron correctos. El α ya está firmado (§2a-bis). Lo que bloquea
ahora es **la regla de deduplicación** (§2a), que es nueva y urgente, y el
**MDE** (§2b), cuyo número propuesto quedó retirado por derivarse en la
escala equivocada.

### 2a. La regla de deduplicación — la que bloquea, y es urgente

**Qué decidir:** si las predicciones que apuntan a la **misma sesión
objetivo** cuentan una vez o dos, y si cuentan una, **cuál se conserva**.

**Por qué es urgente y no puede esperar:** son **30 de 256 filas (11,7%)**,
quince pares sobre cinco sesiones, y **la elección mueve el veredicto de un
lado al otro del umbral**:

| Regla | Ventaja | b / c | McNemar p |
|---|---|---|---|
| `keep="first"` (la emisión temprana) | +6,64 pp | 72 / 56 | **0,1847** |
| `keep="last"` (la emisión tardía) | +9,96 pp | 70 / 46 | **0,0323** |
| sin deduplicar (lo que hay hoy) | +6,5 pp | 72 / 56 | 0,1849 |

**Un argumento de una palabra, hoy no declarado, decide si la ventaja del
modelo cruza p = 0.05 o no.** Mientras esté abierta, cualquier análisis de
la ventana sellada tiene un grado de libertad sin declarar — que es
exactamente lo que el pre-registro existe para cerrar.

**El argumento de cada lado, para que se decida con ellos:**
- **`keep="last"`** es defendible: la emisión tardía tiene **más
  información** y está más cerca del objetivo. Descartarla es tirar la
  mejor predicción.
- **`keep="first"`** es defendible: es la que respeta el orden temporal sin
  privilegiar nada, y **es la que está en uso de hecho**.
- **Contar las dos** también: son **dos pronósticos distintos del mismo
  evento** — una observación del resultado, dos del modelo. El modelo
  cambió de predicción entre las dos emisiones, y eso es información.

**Qué NO se puede hacer:** elegir después de ver cuál da mejor p. Por eso
el pre-registro no se congela hasta que esto esté firmado.

**Expediente:** `GEMELO/SECUENCIAL/DISEÑO.md` §A3.1.a, el cuarto dictamen
del `estadistico-adversario`, y la pregunta pendiente de `DECISIONES.md`
§33.8 (que planteaba lo mismo para 8 filas del 29-jul, sin ver que eran 30
y cinco sesiones).

**Recomendación, marcada como tal:** ninguna. Los tres argumentos son
buenos y la elección cambia una cifra publicada. Lo único que recomiendo
es **decidirla antes de la próxima mirada al track record**, y dejar la
sensibilidad de las tres opciones publicada al lado del resultado.

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

## Lo que esta lista NO incluye, a propósito

El segundo movimiento del switch (apagar los timers del Mac, quitar
`MKI_MODO` en el PC) no entra con ítem propio: ya tiene su lugar
establecido en la skill `switch-titular`, que es su propio expediente
completo. Si Nicolás quiere verlo priorizado junto con el resto, decirlo y
se agrega.
