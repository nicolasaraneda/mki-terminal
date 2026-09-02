# Propuestas de la séptima corrida — Frentes C, D y E (2-sep-2026)

> **PROPUESTAS, todas.** Regla quinta de la corrida: nada de lo que sigue
> entra a una cifra publicada, a un criterio congelado (`GEMELO/DISEÑO.md`,
> `GEMELO/SECUENCIAL/DISEÑO.md`, `RELEVO.md`) ni a un documento de
> resultados sin dictamen de `estadistico-adversario`. Si el adversario
> rechaza una, se registra la propuesta y el rechazo, y se sigue. El
> dictamen va al pie (§4) cuando exista.

Cada propuesta cita el script que la produce y el `.json` con sus cifras.
Ninguna cifra está cableada en la prosa. Ninguna mueve el α firmado
(0,05 nominal con la banda [0,046, 0,079] publicada, acta §53) ni la regla
de deduplicación firmada (acta §60).

---

## C · La fragilidad de cruzar α: ¿qué estadístico principal no tiene esa propiedad?

**Script:** `GEMELO/SECUENCIAL/trayectoria.py` → `trayectoria.{json,md}`.
**Datos:** track record vivo hasta el sello del 31-ago (37 días, 261 filas),
regla firmada, `excluir_cero`; prefijos por fecha de emisión desde 10 días.

### C.0 La reformulación, que es la mitad de la respuesta

La propiedad «un día lo mueve de un lado de α al otro» **no es del
estadístico: es de la decisión binaria cerca del umbral.** Cualquier test
con umbral la tiene si el valor está cerca. Lo que sí distingue a los
candidatos es (a) cuánto se mueve por observación —y eso depende de qué se
toma como unidad—, (b) si mirar todos los días invalida la decisión
(anytime-validity), y (c) si el reporte es un número continuo o una
decisión. Los siete candidatos se evaluaron **sobre la trayectoria real**,
un prefijo por día, contando cuántas veces la decisión cambió de un día al
siguiente:

| candidato | unidad | qué reporta | cruces del umbral (10 → 37 días) | prefijos «decidiendo» | decide hoy |
|---|---|---|---|---|---|
| MCN · McNemar exacto (el degradado en la acta §61) | fila | p | **3** | 21 de 28 | sí (p = 0,0063) |
| ICD · IC95 de clúster de día (el principal desde §61) | día | intervalo | **0** | 0 | no ([−4,1, +28,3]) |
| PSD · permutación de signo por día | día | p | 0 | 0 | no (0,183) |
| TDM · t sobre medias diarias | día | p | 2 | 3 | no (0,068) |
| BAY · posterior con prior escéptica N(0, 5 pp²) | día | P(Δ>0), P(Δ>9 pp) | 0 | 0 | no (0,83 / 0,12) |
| AVS · proceso de apuestas anytime-valid (Waudby-Smith & Ramdas 2020) | día | capital K_t | 0 | 0 | no (3,0 vs 20) |
| SGN · signo de los días («10-6») | día | días +/− | 0 | 0 | no (11-6) |

**El hallazgo, corregido por el dictamen:** los seis candidatos de nivel
día cruzaron cero veces **porque nunca se acercaron al umbral** — la cuenta
de cruces confunde fragilidad con potencia. Medido en |Δz| por día (métrica
libre de potencia), el McNemar de filas salta ~1,6× más que el resto, y la
razón no es que la fila sea más ruidosa: **su escala está inflada por
√DEFF**. z_MCN / z_ICD = 1,90 contra √DEFF = 1,94 (ICC 0,42, DEFF 3,77 sobre
la ventana viva; `trayectoria.json`). Un test que rechaza a |z| > 1,96 con
un SE √3,77 veces menor que el verdadero rechaza en realidad a |z_real| >
1,01: **α real ≈ 0,31 a 5% nominal.** Ése es el número, no la cuenta de
cruces. El de nivel fila cruzó tres veces y «decide» en 21 de 28 prefijos. El día que produjo
el salto (28-ago: 8 discordantes a favor, uno de los 16 sellos que el
Frente A muestra que la fuente ya no reproduce) movió el McNemar de 0,0365
a 0,0063 y el t de medias diarias de 0,117 a 0,067; el IC de día ni se
acercó al cero.

### C.1 Los candidatos, con justificación, costo y lo que pierden

| candidato | por qué tiene sentido | costo | qué pierde frente al actual (ICD) |
|---|---|---|---|
| **ICD (mantener)** | Ya es el principal (§61). Reporta un intervalo, no una decisión: «cruzar» no es su vocabulario. | ninguno | nada; es el statu quo. **Propuesta C-1: ratificarlo y declarar explícitamente que el proyecto no publica decisiones binarias sobre la ventana sellada hasta que un MDE firmado las habilite.** |
| **AVS (agregar como secundario)** | Es válido a **cualquier** instante de parada (absorbe el pasivo de miradas de `DISEÑO.md` §A1). **Y el mejor argumento, que el dictamen agregó:** sólo exige una condición de martingala, E[X_t \| pasado] ≤ μ₀, **más débil que independencia entre días** — es válido bajo exactamente la autocorrelación que el Frente D no logra acotar. | una función de 20 líneas; declarar `λ_t`, c y α antes, en `DISEÑO.md` | potencia: es conservador (hoy K = 3,0). **Propuesta C-2: ENTRA con cinco declaraciones (dictamen):** (a) su estimando es la media NO ponderada de medias diarias, distinta del cociente de sumas del ICD; (b) su σ̂² usa desviaciones respecto de la media terminal, no de las corrientes como en Waudby-Smith & Ramdas — sobreestima σ̂², achica λ, es conservador; (c) es de UNA cola mientras ICD y MCN son bilaterales; (d) λ, c = 0,5 y α se declaran antes y en `DISEÑO.md`; (e) cuenta como intento — **ya registrado** (tramo TRAY). Se publica al lado del ICD como capital acumulado, sin decidir nada hasta firma. |
| BAY | Cambia gradualmente y da la cantidad que la gente quiere leer (P(Δ > 9 pp) = 0,12). | fijar y declarar el prior antes; es un intento si se elige mirando | depende del prior; con prior plana colapsa en TDM. **No se propone como principal.** |
| TDM | Simple, la unidad correcta. | ninguno | aproximación normal con 37 días; cruzó 2 veces en la trayectoria. No aporta sobre ICD. |
| SGN | Se entiende sin aparato. | ninguno | tira la magnitud: 11-6 no distingue nada y nunca lo hará con 37 días. Sirve para la portada, no para decidir. |
| PSD | Ya existe en `bifurcaciones`. | ninguno | α empírico 0,055 [0,048, 0,064] a 35 días (Frente B, 3.000 simulaciones, semilla por réplica): bien calibrado. *(La primera versión decía 0,083 «anticonservador»: era ruido de Monte Carlo, retirado por el dictamen.)* |
| MCN (fila) | — | — | **Propuesta C-3: que el p de McNemar de filas deje de ofrecerse como salida por defecto en `duelo()`, `comparar_pareado()` y `control_lineal`**, con el motivo corregido por el dictamen: **su tamaño real es ≈ 0,31, no 0,05**, bajo el agrupamiento de día (DEFF 3,77). `b` y `c` se siguen reportando siempre; la función sigue *calculando* el p porque `LINEA_BASE_OFICIAL` congela 0,4633 (§2.8) y esa reproducción no se rompe. **Dictamen: ENTRA con el motivo cambiado.** |

**Lo que ninguna propuesta cambia:** que el dato de hoy no separa al campeón
de una constante. Un estadístico mejor no fabrica potencia. **Y C no es
rehén del Frente A** (chequeo del dictamen): sustituyendo las 15 filas del
28/31-ago por su reconstrucción, MCN p 0,0063 → 0,0080, ICD [−4,1, 28,3] →
[−4,3, 27,6], y TDM, AVS y SGN idénticos. **Dictamen: C-1 ENTRA sin
condición; C-2 y C-3 con lo dicho arriba.**

---

## D · El diseño secuencial, quinta vuelta: acotar AC1 o no necesitarla

**Script:** `GEMELO/SECUENCIAL/autocorrelacion.py` → `autocorrelacion.{json,md}`;
verificación con el simulador del propio diseño en
`autocorrelacion_alfa_plan_prior.json`.

### D.1 Salida 1 — acotar la autocorrelación con la ventana larga como prior

El campeón es un modelo determinista (β·SOX(t−1)) sobre precios. La
reconstrucción de la Etapa 5.1 (`backtest/resultados/20260901-133154-*/predicciones_B2.csv`,
B2 = motor de producción verbatim) da **518 fechas** de d_j del MISMO modelo
sobre los MISMOS mercados (sep-2024 → ago-2026), y el Frente A midió que la
fuente no cambió un retorno en esa historia. La autocorrelación de d_j es
una propiedad del par (mercado, modelo), no del acto de sellar.

| | fechas | AC1 | IC95 |
|---|---|---|---|
| ventana larga reconstruida (dedup por sesión, `excluir_cero`) | 518 | **−0,042** | **[−0,122, +0,041]** (bootstrap de bloques de 20) |
| por año: 2024 / 2025 / 2026 | 87 / 260 / 171 | −0,014 / −0,080 / −0,007 | ±0,11 / ±0,06 / ±0,08 |
| ventana sellada, misma aritmética | 37 | −0,176 | ±0,164 |

AC2…AC5 sobre la larga: −0,02 / +0,01 / −0,02 / +0,05. Nada por encima de
0,05 en ningún rezago ni en ningún año.

**Lo que eso hace con la banda del plan**, medido con el simulador del
propio diseño (`alfa_plan_bajo_correlacion`, 2.000 réplicas por punto):

| AC1 supuesta | α del plan (IC95 Wilson) |
|---|---|
| −0,042 (punto de la larga) | 0,039 [0,031, 0,048] |
| 0,000 | 0,047 [0,039, 0,057] |
| **+0,041 (cota superior de la larga)** | **0,0545 [0,045, 0,065]** |
| +0,30 (extremo de la banda firmada) | 0,079 (acta §53, 20.000 réplicas) |

**Propuesta D-1, tal como se formuló («cota externa», α ≈ [0,039, 0,055]):
NO ENTRA — dictamen.** Un IC95 sobre un punto estimado no es una cota, y
evaluar el α del plan exactamente en +0,041 trata el extremo de un IC como
certeza; además cada α sale de 2.000 réplicas y tiene su propio Wilson.
**Entra reescrita como MEDICIÓN DE REFERENCIA:**
- AC1 estimada sobre la reconstrucción: −0,042, IC95 [−0,122, +0,041]
  (contiene el cero: AC1 no se distingue de 0); máximo |AC| en rezagos 1–5:
  0,051 (AC5 — la primera versión decía «nada por encima de 0,05»).
- **El chequeo que decide la admisibilidad, hecho por el adversario y ahora
  en el script:** la reconstrucción restringida al mismo tramo de calendario
  que la sellada (desde 2026-07-05, 40 fechas) da **AC1 −0,180 ± 0,158**
  contra −0,176 ± 0,164 de la sellada. Donde los dos objetos existen, la
  reconstrucción reproduce el sello a 0,004.
- **Lo que la reconstrucción no puede ver:** es una sola descarga congelada,
  ciega por construcción a la intermitencia de la fuente (M6 del Frente A),
  que cae dentro de ese tramo. 40 fechas con EE 0,16 no lo resuelven: la
  objeción queda no medible, no refutada.
- **El α del plan bajo esta referencia, con las DOS fuentes de error**
  (simulador del propio diseño, 2.000 réplicas, Wilson): 0,039 [0,031, 0,048]
  a −0,042; 0,047 [0,039, 0,057] a 0; 0,0545 [0,045, 0,065] a +0,041 →
  **rango honesto [0,031, 0,065]**, no [0,039, 0,055]. Sigue por debajo del
  0,079 de la banda firmada.
- Dos DGP declarados: el simulador del diseño discretiza d_j
  (`np.round(d·7/2)`); D.2 usa normales continuas.
**La banda firmada [0,046, 0,079] no se toca ni se re-discute.**

### D.2 Salida 2 — ¿existe una familia robusta a AC1 desconocida? A estos tamaños, no

Simulador propio (AR(1) en d_j, 20.000 réplicas, sin bootstrap interno),
plan OBF de 4 miradas a 51/102/152/203 fechas, tres familias:

| φ | DIA (varianza iid) | bloques de 10 | bloques de 20 | Newey-West L=5 | Newey-West L=10 |
|---|---|---|---|---|---|
| 0,0 | 0,051 | 0,089 | 0,123 | 0,064 | 0,080 |
| 0,1 | 0,080 | 0,093 | 0,125 | 0,069 | 0,084 |
| 0,2 | 0,119 | 0,096 | 0,127 | 0,076 | 0,088 |
| 0,3 | 0,171 | 0,100 | 0,129 | 0,084 | 0,094 |

- **Los bloques como unidad aplanan la dependencia de φ pero inflan α desde
  φ = 0** (0,089 / 0,123): en la primera mirada hay 5 o 2 unidades, y un
  umbral z sobre un estadístico con 1–4 grados de libertad es
  anticonservador. Se podría corregir con cuantiles t escalados, pero eso
  cambia las fronteras OBF congeladas: **no se propone.**
- **Newey-West** reduce la pendiente (0,064 → 0,084 contra 0,051 → 0,171)
  al precio de un sesgo inicial. Es lo mejor de la tabla y sigue sin
  entregar 0,05 plano.
- **El bootstrap de fechas con máximo sobre bloques (1, 5, 10) que el plan
  ya usa está entre DIA y HAC**: el simulador del diseño da 0,060 a φ = 0,1
  donde el iid puro da 0,080. El plan ya es «parcialmente robusto», y la
  acta §53 lo había notado.
- **Potencia** (drift 0,18 sd/fecha, φ = 0): 0,72 / 0,73 / 0,74 / 0,74 /
  0,75 — la robustez no cuesta potencia a φ = 0; a φ = 0,2 cuesta ~0,1.

**Conclusión de D.2, con la misma firmeza:** a 51–203 fechas **no hay
estadístico que entregue α = 0,05 plano bajo φ desconocida**. Declarar la
banda —que es lo que Nicolás firmó— era la respuesta correcta. Lo que sí se
puede es **acotar φ desde afuera** (D.1). Si el adversario rechaza D.1, D
queda como estaba: banda declarada, sin quinta versión del diseño.

---

## E · Estimandos alternativos: ¿el problema es el endpoint?

**Script:** `GEMELO/SECUENCIAL/estimandos.py` → `estimandos.{json,md}`.
**Vara común:** IC95 y z por bootstrap de fechas enteras; «días para
potencia 0,80 al efecto observado» = días × (2,80/z)². Es una **cota
inferior optimista con sesgo de ganador** (los efectos se miraron antes de
elegir): sirve para comparar estimandos entre sí, **no para prometer
fechas** — las fechas se prometen sólo con un MDE fijado antes (Frente B).

| estimando | qué mide | sellada (37 d): punto · IC95 · z · D80 | larga (518 d): punto · IC95 · z · D80 | supuestos nuevos | qué NO puede decir |
|---|---|---|---|---|---|
| **E0 dirección** (actual) | acierto de signo − "siempre al alza" | +11,9 pp · [−4,4, 28,0] · 1,41 · 146 | +13,4 pp · [9,8, 17,0] · 7,35 · 75 | ninguno | magnitud; capturabilidad |
| **E1 magnitud** | \|g\| − \|p − g\|: cuánto reduce el error L1 conocer p | +0,46 pp · [−0,01, 0,94] · 1,88 · 83 | +0,31 pp · [0,22, 0,40] · 6,97 · 84 | que el error L1 importe | dirección; capturabilidad |
| **E2 gap capturado continuo** | g·(signo p − 1): lo capturado siguiendo el signo menos lo de "siempre al alza" | +1,10 pp · [−0,03, 2,35] · 1,82 · 88 | +0,80 pp · [0,59, 1,04] · 7,11 · 80 | posición ∝ signo, sin costos | retorno de sesión (ya se sabe que no) |
| **E3 pendiente de calibración** | b en g = a + b·p | **1,42 · [0,65, 2,19] · 3,44 · 25** | 0,99 · [0,82, 1,16] · 11,3 · 32 | linealidad | dirección de un signo dado; capturabilidad |
| **E4 decaimiento (pendiente por hora)** — **RECHAZADO** | pp de ventaja por hora de margen emisión→apertura | −0,03 · [−4,3, 3,8] · 0,01 · — | −1,61 pp/h · [−2,45, −0,77] · 3,78 · 284 — **IC y z NO admisibles: unidad de replicación equivocada** | que las bolsas difieran sólo en h; **y que 4 bolsas con 2 valores de h basten para una pendiente: no bastan** | nada sobre el nivel; nada sobre captura; **nada con IC de fecha** |
| **E4' contraste Asia − Fráncfort** | diferencia de ventaja entre 1,75–2,75 h y 8,75 h | +0,5 pp · [−26, 30] · 0,04 · — | +10,8 pp · [5,0, 16,7] · 3,68 · 300 | idem | idem |

**Lecturas, cada una con su estatus:**

1. **E3 es el único estimando que hoy excluye el cero con clúster de día
   sobre la ventana sellada** (pendiente 1,42, IC [0,65, 2,19], que también
   **contiene 1**: no distingue calibrado de subconfiado). Sobre la larga,
   0,99 [0,82, 1,16]. **Propuesta E-1 — dictamen: OBSERVADO, entra sólo con
   tres condiciones:** (a) se pre-registra contra la pendiente del **control
   lineal C1**, no contra 0 — «siempre al alza» es una constante y b > 0
   sólo dice que p correlaciona con g, cosa que C1 ya hace en las mismas
   filas (WS2b); (b) las dos hipótesis (b = 0, b = 1) se separan como
   endpoints distintos; (c) la ventaja de señal que lo justifica **no existe
   en la ventana sellada** (cociente D80(E0)/D80(E3) = 5,5× con IC95 [0,7,
   1.379]: contiene 1) y sí en la larga (2,6× [1,5, 4,8]) — se cita así.
   Ya registrado como intento (tramo ESTIM).
2. **E1 y E2 tienen ~1,3× más señal por día que E0 en la sellada y la misma
   en la larga.** No justifican cambiar el endpoint: ganan poco y cuestan
   un supuesto (L1 / posición proporcional). **No se proponen.**
3. **E4 —el decaimiento como pendiente por hora con IC— RECHAZADO por el
   dictamen, y se retira.** La unidad de replicación de un parámetro sobre
   h es la bolsa: hay cuatro, con dos valores de h. Con la bolsa como
   unidad, permutación exacta p = 0,231, **p mínimo alcanzable 1/13 =
   0,077**; bootstrap de bolsas IC95 [−5,4, −1,4], tres veces más ancho. El
   `README.md` (línea 60) ya lo decía: «con n = 4 bolsas no se puede ajustar
   una curva. Esto es un escalón». Y el orden no replica fuera de muestra:
   en la sellada la bolsa más cercana (XKRX) es la peor. **El «4× menos
   señal que el nivel» no está mal medido: está mal definido**, y por lo
   tanto no contradice la recomendación 1b de `tesis.md` (adenda reescrita).
   Lo publicable: la tabla por bolsa con Wilson por bolsa y el contraste
   Asia − Fráncfort declarado como comparación de cuatro bolsas.
4. Sobre la sellada, las bolsas dan E0 de: XTKS +14,2 pp (134 filas), XTAI
   +14,3 (28), XKRX +6,3 (64), XETR +11,4 (35) — el orden de la larga no
   aparece y, con esos tamaños, los intervalos son enormes. Consistente con
   `dos_ventanas.md` §6. *(Cifras leídas de `estimandos.json`
   `sellada.por_bolsa`; la primera redacción de esta línea las tenía de
   memoria y estaban mal — corregido antes de despachar al adversario.)*

---

## §4 · Dictamen del `estadistico-adversario` (2-sep-2026, ~02:45)

**Texto íntegro en `dictamen_07/DICTAMEN.md`; sus 16 scripts de
verificación, preservados en la misma carpeta.** Las correcciones que
exigió están aplicadas arriba en su sitio y en los ejecutables (este
documento no estaba commiteado: la frontera de la errata es el commit). El
entregable, textual:

```
DICTAMEN POR FRENTE
  A   VERIFICADO en (i), (iii) y (iv) · OBSERVADO en (ii) y en el MAE de (iv).
      Entra a documento de resultados con las correcciones en su sitio.
  B   RECHAZADO el α = 0,083 · OBSERVADO el gasto de α mal citado, la cadencia
      y la potencia sin intervalo · y R2 sin nombrar. El resto VERIFICADO.
      Entra con las tres condiciones.
  C   VERIFICADO. C-1 ENTRA sin condición. C-2 ENTRA con cinco declaraciones.
      C-3 ENTRA con el motivo cambiado (α real ≈ 0,31, no la cuenta de cruces).
  D   Salida 1 VERIFICADA como medición; D-1 NO ENTRA como «cota externa».
      Entra reescrita como medición de referencia, con el chequeo del tramo
      solapado (−0,180 ± 0,158 vs −0,176 ± 0,164) incorporado y el α en
      [0,031, 0,065]. D.2 VERIFICADO y se publica tal cual. La banda firmada
      no se toca.
  E   E-1 OBSERVADO: entra como secundario sólo pre-registrado contra la
      pendiente del control lineal, con las dos hipótesis separadas y con el
      2,6× [1,5; 4,8] de la larga como respaldo declarado.
      E-2 RECHAZADO: no entra a ningún documento de resultados con pendiente
      por hora ni con su IC. Puede publicarse la tabla por bolsa y el
      contraste Asia−Fráncfort, declarados como comparación de 4 bolsas.

DICTAMEN GLOBAL: NO CONCLUYENTE — y hacia el lado negativo.
  Nada de esta noche acerca a nadie a V1. [...] Que nadie gane sigue siendo
  el resultado. Se publica igual.
```

Criterios V1–V7 y R1–R3 según el dictamen: V1 NO PASA (vara vigente n=248,
+6,5 pp, p=0,1849; nada de esta noche la mueve); V3 NO PASA (campeón:
cobertura 90,3% fuera de [76, 84]); **R2 DISPARADO** sobre el ancla del
Frente B; R3 NO DISPARADO (todo en `mode=ro`, cachés no reescritas, corrida
del arnés corregido); el resto NO EVALUABLE. **V5 bloqueado hasta que el
registro absorbiera las configuraciones de C y E: hecho (91 → 100).**
