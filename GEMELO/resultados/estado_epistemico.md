# Qué puede afirmar MKI Terminal hoy — estado epistémico (30-sep-2026, actualizado al cierre de la corrida 15)

**Para quien pregunta «¿y esto qué demuestra?».** MKI es un experimento de
pronóstico: cada tarde, al cierre de Nueva York, un modelo congelado emite
ocho predicciones sobre cómo abrirán ocho acciones de semiconductores en
Seúl, Tokio, Taipéi y Fráncfort, las sella con marca de tiempo antes de que
esos mercados abran, y después las verifica contra lo que pasó. No mueve
dinero. Lo que sigue es cada afirmación del proyecto con su **estatus**:

| estatus | significa |
|---|---|
| **DEMOSTRADA** | verificada por un mecanismo distinto del que la produjo, o por censo (no muestra) |
| **ACOTADA** | medida con intervalo; el intervalo dice lo que se puede y lo que no |
| **CONTESTADA** | el propio proyecto la puso a prueba y la refutó |
| **RETRACTADA** | se publicó, estaba mal, y la corrección está en el ejecutable |
| **NO EVALUABLE** | los datos actuales no permiten decidirla en ninguna dirección |
| **PROPUESTA** | medida esta semana, pendiente de dictamen adversario; no es una afirmación del proyecto |

Ninguna cifra se cita de memoria: cada una tiene su archivo. Las canónicas
viven en `README.md` (inglés) y `README.es.md` (español), generados desde el árbitro; las de esta semana, en `GEMELO/resultados/`.

---

## Lo que está DEMOSTRADO

1. **Las predicciones se emiten antes del evento, y eso es verificable.** Cada
   fila lleva `timestamp_utc`, la sesión objetivo y el instante en que su
   insumo era conocible; el verificador descarta toda predicción emitida
   después de la apertura objetivo (`no_verificable_timing`), y ese descarte
   no lo hace el modelo ni el tablero. 276 verificaciones desde julio al censo
   del 1-sep (`fuente_canonica.md`); 292 al 3-sep en `senales.db`.
   *(Regla maestra de la Etapa 4.6; `senales.py`.)*
2. **La fuente de precios no reescribió un solo retorno diario en 8 años ×
   27 tickers entre el 26-ago y el 2-sep** (52.507 celdas; 1.953 niveles de
   un solo ticker reescalados por un factor constante, retorno invariante).
   *(Censo, `fuente_canonica.md` §2; verificado por otra ruta en el
   dictamen.)* Vale para ese intervalo, no para siempre.
3. **La magnitud verificada de gap y retorno es estable:** 276/276 filas
   reproducen hoy desde la fuente (5 con ruido en el 4º decimal). *(Censo, id.)*
4. **Lo que el sello guardó del 28-ago es coherente y la fuente ya no lo
   sirve:** dos sellos con 72 h de diferencia implican el mismo cierre que
   hoy no existe. *(Aritmética, acta §69.)*

## Lo que está ACOTADO

5. **Sobre ocho años reconstruidos (n = 14.618), el modelo acierta la
   dirección del gap de apertura +15,66 pp más que "siempre al alza", y la
   ventaja cae con las horas de margen: +19,1 / +16,8 / +15,4 pp en las tres
   bolsas que abren dentro de 3 h, +2,5 pp (p = 0,111) en la que abre a
   8,75 h.** *(`README.md`.)* Sin IC de clúster de día computado; reconstrucción
   sobre el caché v1, que omite toda sesión posterior a un feriado local (~4,5 %
   de las filas): recomputar mueve los doce bloques y lleva firma
   (`cifras.larga().procedencia`). Es una **reconstrucción** desde la fuente de
   hoy —no un sello— y depende de que esa fuente no mute (punto 2) y de
   una composición de universo que no se pudo verificar (punto 17).
6. **Sobre la ventana sellada —la única evidencia prospectiva— la ventaja
   no se distingue de cero.** Publicado desde el 3-sep-2026 (D1: regla de
   deduplicación firmada; errata: hasta el 2-sep era +6,5 pp sin deduplicar
   sobre n = 248, rama derogada): **+9,7 pp, n = 238, 34 días**, con **IC95 de
   clúster de día [−7,2, +26,6]**, permutación de signo por día p = 0,29,
   McNemar de filas p = 0,0455, n efectivo 67 (las ocho filas de un día
   comparten el mismo movimiento del SOX). 0 de 192 formas legítimas de medirla dan p < 0,05
   respetando el clúster — **y eso es prácticamente no informativo:** con
   verdad conocida, la nula produce «0 de 192» el 75 % de las veces y una
   ventaja verdadera de 9 pp el 47 % (cociente de verosimilitudes 1,6).
   *(Acta §61, `bifurcaciones.md`; `calibracion_instrumento.md` A2, octava
   corrida, dictamen A.)* Además, **más de la mitad de las fechas selladas
   (19 de 35) contribuyen exactamente cero** al estadístico direccional: cuando
   el SOX sube, el campeón y «siempre al alza» coinciden por construcción.
   *(`secuencial_v5.md`, dictamen F.)*
7. **El instrumento acumula ~2 observaciones efectivas por día sellado.** Todo lo
   que sigue está calibrado sobre el ancla del 31-ago (cadena local, n = 246,
   35 días), no sobre la ventana publicada (n = 238, 34 días); el MDE a 73 días
   es de la ruta 1 (analítica).
   Detectar 9 pp con potencia 0,80 exige ~250 días sellados —ruta
   analítica 248 con IC95 paramétrico [109, 370]; simulador calibrado
   (ruta 3, 3-sep) ≈263 con rango Monte Carlo [229, 296]— (≈ ago-2027);
   6,5 pp, ≈510 (MC [467, 580]; ruta 1: 475 [209, 709]); 5 pp, ~800 [354, 1.199]. El veredicto
   programado del 25-oct llegará con ~73 días, una potencia direccional
   de **0,30 [0,27, 0,33]** a 9 pp y un efecto mínimo detectable de 16,6
   pp [11,0, 20,3]: **un resultado negativo ese día no será evidencia de
   ausencia.** *(`horizonte.md` rutas 1 y 3; dictamen 1b, novena corrida.)*
   El instrumento anterior (ruta 2, δ constante por fila) era optimista:
   contra el simulador calibrado está por encima en 23 de 28 celdas
   (+2,2 pp [1,6, 2,8]; sobre las 12 celdas de A4 +2,45 [1,64, 3,27]),
   y ya no manda. Y el tamaño del efecto del que
   dependen ya no está indeterminado por la rama: D1 fijó la regla firmada
   (+9,66 pp) como la publicada; la rama sin deduplicar (era +6,45) queda
   retirada y la de «+ coherencia» (+14,3, sin intervalo) sigue en cola sin
   publicarse. *(Dictámenes A y E, octava corrida; D1, acta §78.)*
8. **La magnitud predicha no se distingue de cero al nivel de día:** MAE del gap
   2,52 pp contra 2,98 de predecir cero (n = 238, 34 días; ganancia +0,45 pp por
   fila, IC95 t de clúster de día [−0,09, +1,00], p de día 0,10: contiene el
   cero). Parte de la mejora relativa respecto de la rama retirada —era 2,98
   contra 3,33— es que la regla saca filas con gaps enormes del 29-jul. Los
   intervalos del 80% cubren el 92,9%: son 2,19× [1,71, 2,78] más anchos de lo
   necesario. *(`cifras.sellada()`; verificado por el adversario el 3-sep,
   `enmienda_v1bis.md` §6.)*
9. **Un solo régimen de mercado en toda la ventana sellada.** Todo lo
   anterior sobre esa ventana vale para ese régimen.
9b. **El signo del SOX no compra nada en la sesión asiática, ni al derecho
   ni al revés, y eso replica fuera de muestra** (2024 → jun-2026, 643
   fechas, sin las selladas y con embargo): acierta el gap +15,6 pp [12,3,
   18,9] sobre «siempre al alza» y la sesión posterior **−2,7 [−5,5, −0,02]**;
   la cartera direccional rinde −0,114 [−0,208, −0,026] pp/día sin costos;
   la contraria que eso implica muere a 5,7 pb por lado y con DSR 0,41 a
   N = 100. Aguanta dejar-un-año-fuera, dejar-un-ticker-fuera y winsorizado.
   *Consistente con* un mecanismo estructural (la información llega después
   del cierre local); el diseño no mide horarios y no puede decir «es».
   *(`no_capturabilidad.md`, dictamen C: H1 verificado y robusto.)*
9c. **Un orden de β estimado sin el motor ordena dentro del día:** ρ̄ de
   Spearman 0,240 [0,206, 0,276] sobre 637 fechas de prueba; contra la nula
   honesta (permutar el vector β entre tickers) p = 0,005; simétrico en el
   signo del SOX; ningún ticker lo carga. **El orden del campeón no alcanza
   la vara pre-registrada** (0,18 [0,15, 0,21], contrafactual optimista) y
   en la ventana sellada no sobrevive a R2. *(`transversal.md`, dictamen D.)*

## Lo que el proyecto CONTESTÓ (puso a prueba y refutó)

10. **«La ventaja es capturable.»** No. Entrar en la apertura y salir al
    cierre **pierde 40,7% sin un solo punto básico de costo**; con 25 pb por
    lado, −95,6%, contra +137,1% de comprar el ETF del sector. El gap existe;
    el retorno de sesión no lo sigue. *(Acta §59.)*
11. **«Asia toma el relevo de Nueva York hacia Europa.»** No: el SOX pierde
    ~14 pp de ventaja al alejarse y ningún mercado intermedio lo reemplaza.
    *(`relevo_asiatico.md`, pre-registrado y refutado.)*
12. **«Se puede predecir cuándo el modelo funciona.»** Las condiciones que
    parecían predecirlo son la aritmética del propio modelo (β × movimiento
    del SOX). *(`condicional_ventana_larga.md`.)*
13. **«Un modelo con 14 features más lo mejora.»** No detectable: +2,8 pp,
    p = 0,36 sobre lo sellado; el control con la misma información acierta
    en las mismas filas. *(WS2b, `README.md`.)*
14. **«La ventaja sellada está concentrada en julio.»** Está más dispersa
    que el azar; hay 157 bloques históricos iguales o mejores que julio.
    *(Acta §64.)* Pero **R2 —el criterio de rechazo congelado— dispara**: al
    excluir el bloque 15–23 jul la ventaja sellada queda en +2,5 pp con IC95
    de día [−13,6, +19,2] (contiene el cero) sobre el ancla del 31-ago, y en
    −1,0 pp sobre la rama sin deduplicar que entonces se publicaba (n = 204 tras
    excluir el bloque; rama retirada por D1; no recomputado bajo la regla
    firmada). *(`horizonte.md`, acta §64.)* **La ventana no
    admite partirse**, en ninguna dirección.
14b. **«La ventaja decae con las horas de margen como una ley Δ(h).»** No:
    predicha antes de descargar para tres bolsas nuevas, la curva falla en
    Hong Kong (predicho 14,0, medido 4,1) y en India (predicho 8,6, medido
    −12,7), y esos dos puntos refutan cualquier curva monótona decreciente
    por las anclas, no sólo la exponencial. Lo que mejor predice la ventaja
    por bolsa no es h sino la **tasa base** de gaps positivos (r = −0,89).
    Ámsterdam «acierta» porque está al mismo h que el ancla Fráncfort.
    *(`decaimiento_prediccion.json`, dictamen B.)*
14c. **«La no capturabilidad es asimetría de magnitud (aciertos chicos,
    errores grandes).»** No: los aciertos pierden MÁS que los errores
    (−0,12 vs −0,10 pp; diferencia −0,02 [−0,15, +0,13], contiene el cero).
    Y **no es sobrerreacción medible** respecto de la sorpresa (pendiente
    −0,03 [−0,09, +0,03]). *(Dictamen C.)*

## Lo que se RETRACTÓ

15. **«Cruzar α = 0,05 es tener evidencia.»** Un p de 0,0451 (y 0,0486 al día
    siguiente) se produjo tratando las filas como independientes; con el
    clúster de día el intervalo contiene el cero. El McNemar de filas dejó
    de ser el estadístico principal. *(Actas §61 y §70.)*
16. **«Una predicción sellada es reproducible desde la fuente.»** Nunca se
    afirmó en la portada, pero el backtest lo suponía. Es falso para 16 filas
    (la fuente retiró la sesión del 28-ago) y, en magnitud, para 32 más. El
    sello tiene **«emitido antes»** y no tiene **«reproducible después»**:
    guarda derivados, no insumos. *(`fuente_canonica.md`.)*
17. Dos cifras de auditoría —8,6% de contaminación y 91,4% de coincidencia—
    eran artefactos de una clave de join equivocada; corregidas a 0,00% y
    100% sobre 214 filas, con errata. *(`auditoria_ws3.md`, acta §68.)*
17b. **«El PSR y el DSR saturan en 1,0000 porque anualizar un Sharpe sobre
    pocos días es un artefacto.»** Falso: era un **defecto de unidades** —los
    llamadores pasaban el Sharpe anualizado a una varianza por período; el z
    quedaba inflado por √252 y bajo la nula el DSR superaba 0,95 en un cuarto
    de las réplicas. Con la unidad correcta el WS2b da DSR 0,95–0,96 y **tres
    configuraciones cruzan V5**; lo único que las separa de «V5 superado» es
    `MINIMO_DIAS_SHARPE = 60`, umbral introducido después de ver el 1,0000,
    re-justificado desde cero. Los veredictos del 5.1 sobreviven porque sus
    Sharpes son negativos, no porque el cálculo estuviera bien. Corregido en
    el ejecutable con guarda de unidad y test que recorre el repo. *(Frente A,
    dictamen A; erratas en `control_lineal.md`, `ventana_larga.md` y el 5.1.)*
17c. **Todo «IC95 de clúster de día» publicado antes del 2-sep es un nominal
    95% con cobertura real ~0,93** (percentil con 35 clústeres); la t de
    clúster con gl = k−1 cubre 0,95 y se PROPONE como estimador (cambiar la
    vara después de ver la cobertura lleva firma); el iid de
    filas cubre 0,69 —inservible—. *(`calibracion_instrumento.md` A1.)*
17d. **«Un cierre de NY viejo vale menos en Tokio por el tiempo transcurrido»
    (C1) y «la dirección replica fuera de muestra».** Retiradas: C1 contrasta
    insumo NO incorporado contra insumo YA negociado por la sesión local
    anterior (100 % vs 0 %, determinista), no fresco contra viejo; y con
    bloques de 20 días el IC de prueba contiene el cero. *(Dictamen B.)*
17e. **«El plan secuencial v5 absorbe la autocorrelación mucho mejor que el
    anterior.»** Retirada: su «tipo I 0,050» era el ajuste sobre sus propias
    trayectorias, y el eje φ nunca llegó a las contribuciones. Quinto
    rechazo; **la banda firmada [0,046, 0,079] queda intacta.** *(Dictamen F.)*

## Lo que NO ES EVALUABLE con los datos actuales

18. **Si el efecto persiste cuando cambie el régimen.** Un régimen, un
    modelo congelado: acumular días responde «¿hubo efecto en este
    régimen?», no «¿hay efecto?».
19. **Si la ventana larga sufre sesgo de supervivencia.** Ningún proveedor
    tasado vende constituyentes históricos del índice.
20. **Si la ventaja sellada existe.** Ver punto 6: no es «no», es «todavía no
    se puede saber», y el punto 7 dice cuándo.
21. **Si la ventaja de Fráncfort se disipa con el tiempo o la absorben los
    intermediarios asiáticos.** Los feriados asiáticos que lo separarían
    (C2/C3) dan IC de ±12 a ±23 pp; decidir exige ~23 veces más fechas de
    feriado: más de un siglo. *(Dictamen B: la única conclusión de B1 que
    sostiene.)*

## PROPUESTAS de esta semana (no son afirmaciones del proyecto)

- **Corrida 15 (noche del 29 al 30-sep), sólo lo dictaminado; el resto está en `bitacora_15.md` y en las tarjetas
  §66 a §76.** Dictámenes: `estadistico-adversario` (la regla de §58, dos veces), `auditor-lookahead` (el bloque 1
  aplicado; el parche del sellador), `director-programa` (pre-mortem), `guardian-constitucion` y
  `curador-epistemico` (cierre); `dictamen_15/`.

  (i) **PROPUESTA sellada antes del dato: la regla de decisión de §58** (`GEMELO/propuestas/regla_58.md`,
  23:08:17 del 29-sep, sha256 `ca2ccd53…`, antes del primer disparo de madrugada de la sonda). Dictamen: APTA CON
  EXIGENCIAS, incorporadas; el adversario retiró dos exigencias propias como errores (E8 y el hecho de E6). Lo que
  la regla afirma con etiqueta: MEDIDO con funciones puras del sellador que toda hora candidata de (b) es posterior
  a la medianoche de Nueva York y con el código vigente pierde viernes y vísperas de feriado como
  `dia_sin_sesion`; MEDIDO que el antecedente de noche incompleta a la hora actual es 3 de 11 sesiones (Wilson 95 %
  [9,7 · 56,6]); y que con esa tasa la regla indica (b) con probabilidad 0,11 (binomial, forma cerrada). Nada de
  esto es una afirmación sobre ventaja; intentos consumidos: 0 en los dos registros.

  (ii) **MEDIDO y APLICADO (test de reproducción rojo en HEAD y verde después; dictamen del `auditor-lookahead`:
  APLICABLE CON EXIGENCIAS): las tres guardas de conocibilidad de §90.1 están aplicadas al árbol real desde las
  23:22:17 del 29-sep** (a: el
  verificador; b: `snapshot.py` se niega a sellar con la sesión del SOX abierta, margen cero; d: la capa de medición
  excluye por regla). Alcance MEDIDO: 24 filas, una fecha, 8 con verificación; ninguna cifra publicada se movió
  (árbitro idéntico antes y después, verificado clave por clave por el auditor). **Lo que las guardas NO cierran,
  MEDIDO por el auditor:** las métricas vivas de 30 días de `senales.py` (Telegram, dashboard, API) cuentan hoy 8
  de 160 filas invertidas, y `verificar_puntaje_pendientes` no aplica ni la regla maestra ni la de conocibilidad
  (tarjeta §73). **Y una precisión al acta §90.1 (b), MEDIDA con test:** la guarda no protege contra sellar con el
  SOX de una sesión anterior ya cerrada (tarjeta §72).

  (iii) **MEDIDO por censo de la base sellada: las dos anclas de `sesion_objetivo` difieren en 33 filas de 5 fechas**,
  y la premisa con que el encargo justificaba el §90.2 tiene contraejemplo en la base (`005930.KS`, 29-jul). §90.2 no
  se aplicó; DECISIÓN PENDIENTE (tarjeta §71).

  (iv) **CONTESTADO el «17» de `roca_chip` del 28-sep** que la corrida 14 dejó PROVISIONAL: era el artefacto de un
  split 5:1 de 8035.T que la fuente aplicó a medias el 28-sep (la fuente sirve `Stock Splits = 5.0` con fecha 29-sep
  y hoy la serie es consistente). El valor releído por el orquestador con la serie de hoy (39, contra 44 sellado con
  la barra intradía) es DESCRIPTIVO y sin dictamen adversario: no se asienta acá como cifra; tarjeta §68.

  (v) **PROPUESTA y parche NO APLICADO de §62** (política de retención y camino T): el hallazgo dictaminado es que la
  opción (a) firmada en §90.6 no se puede implementar por la `UNIQUE (fecha_insumo, ticker, juego)` de la tabla;
  tarjeta §75. `dinero/sello_dinero.py` del árbol real no cambió.

  (vi) Lo que la corrida 14 dejó en (i) como «PENDIENTE de Nicolás (§61)» quedó FIRMADO en el acta §90.1 y aplicado
  en (ii); las 24 filas conservan su estado y su errata fechada está en el acta §92.

- **Corrida 14 (28-sep), con dictámenes del `auditor-lookahead` (el sello del 28-sep, más su complementario sobre la
  medición), del `director-programa` (pre-mortem y alcance del cierre), del `estadistico-adversario` (la
  enmienda de M2), del `guardian-constitucion` (el diff, dos veces) y del `curador-epistemico` (estos
  textos); `dictamen_14/`. **Los ítems (v), (vi) y (viii) se retiraron** —eran los de la sonda, sin
  dictamen que los cubriera— y por eso la numeración salta de (iv) a (vii) y de (vii) a (ix):**

  (i) **DEMOSTRADO por censo de la base en `mode=ro`, y confirmado por una segunda fuente independiente
  (el CSV versionado de HEAD, que da 0 inversiones antes del evento): el 2026-09-28 es la ÚNICA fecha de
  toda la historia sellada del riel de medición con `available_at > timestamp_utc`** — 24 filas cuyo sello
  declara que su insumo fue conocible 2 h 17 min DESPUÉS de que la fila se escribió. Causa: el PC volvió de
  suspensión a las 14:40 y los ocho timers dispararon juntos a las 14:42:52, así que `snapshot.py` selló a
  las 13:42 de Nueva York con NYSE abierto. **Dictamen del `auditor-lookahead`: FILAS INVÁLIDAS ENTRARON
  COMO VÁLIDAS.** Decisión de qué hacer: **PENDIENTE de Nicolás** (`espera_firma.md` §61).

  (ii) **DEMOSTRADO: no hay fuga temporal en esas filas.** `tests/test_motor.py` pasa sus 18 casos, y a las
  17:42:58Z no existía nada posterior a `t` que borrar: la fila usó MENOS información de la que declara.
  **Y DEMOSTRADO por lectura del test: su verde es ciego a este eje** — trunca con `df[df.index.date <= fecha]`,
  **inclusive**, así que la barra parcial de `t` está en las dos ramas con el mismo valor y se cancela. El
  verde sigue siendo válido para lo que mide.

  (iii) **MEDIDO: las 8 predicciones selladas de esa fecha son exactamente `beta × (−1,63)`**, donde
  −1,63 es una lectura intradía de `^SOX` que el registro etiqueta `sox_fecha = 2026-09-28`. **No son
  reproducibles por un tercero.**

  (iii-bis) **MEDIDO al cierre de la corrida (17:31 Chile, con la sesión del 28 ya cerrada): el daño es
  chico en la predicción y grande en otra cifra.** **Cubierto por el dictamen complementario del
  `auditor-lookahead`**, que lo autorizó en este documento con tres condiciones de redacción, las tres
  aplicadas abajo.

  **Lo primero, porque es el aporte más fuerte y leído al revés invierte el sentido del ítem: esta
  medición CONFIRMA la no-reproducibilidad del ítem (iii).** El dictamen original **deducía** que un
  tercero que reprodujera obtendría otro número; esta medición es ese tercero, y obtuvo **−1,61 donde el
  sello dice −1,63** y **17 donde dice 44**. La no-reproducibilidad **dejó de ser inferencia y es un
  hecho medido**, así que el veredicto se sostiene **con fuerza neta mayor**, no menor. Y el principio que
  lo ordena: **la validez de un sello no es función del tamaño del error** — el riel de dinero invalidó
  sus 33 filas por la violación de orden, sin preguntar cuánto se había desviado el insumo. Recomputado con funciones puras y sin escribir ninguna
  base: `sox_usado_pct` **−1,61** contra **−1,63** sellado (0,02 pp, **mismo signo**); **0 de 8
  direcciones invertidas**; peor diferencia entre los siete tickers sin dato marcado **0,03 pp** (el
  0,11 pp es de 8035.T y viene de su **beta reestimada**, no de la barra parcial: con 0,02 pp de desvío en
  el escalar el máximo propagable es 0,016 pp); y régimen recomputado
  **idéntico** al sellado (`Alcista · vol baja`), así que el cambio de etiqueta respecto del 24-sep es
  **real**. Las dos sospechas centrales del dictamen del auditor **no se materializaron en esta fecha** (no «quedan
  refutadas»: el mecanismo sigue ahí, porque con las 8 betas positivas un día en que la barra intradía y
  el cierre caigan a distinto lado del cero invierte las ocho a la vez).
  **Y `roca_chip` —el ratio roca→chip como percentil de su último año— pasa de 44 sellado a 17
  recomputado, 27 puntos: PROVISIONAL.** El job de las 18:15 marcó `8035.T` con un salto de **−80 %** el
  28-sep (`data/snapshot.log:147`, «revisar split/dato corrupto»); 8035.T cotiza cerca de 55.000 yenes y
  −80 % es exactamente un **split 5:1** (INFERIDO, sin el cierre a la vista). Como es eslabón de un nivel
  de tres sobre cinco de peso igual, ese solo ticker mueve el crudo de la cadena ~5,33 pp de los 6,44 pp
  observados: **explica del orden del 83 %**. El 17, los 27 puntos y la lectura «chica en el canal lineal,
  grande en el agregado» quedan **PROVISIONALES** hasta contrastar 8035.T. Lo levantó el
  `curador-epistemico`.
  **Y `roca_chip` no se publica sólo por Telegram:** `senales.historial_roca_chip(dias=365)` lee la
  columna sellada, `api/main.py` la sirve en `/` y `/cadena`, y el frontend la muestra como tarjeta hero
  con su sparkline y grafica la serie — o sea que el 44 es **un punto permanente de una serie de 365 días
  que la interfaz grafica**, y las filas selladas no se reescriben. Atenuante real: `roca_chip_al`
  recomputa desde precios, así que los percentiles futuros **no** quedan envenenados.

  **Lo que esta medición NO midió, y hay que decirlo porque si no se lee «el daño está medido»:**
  `puntaje_v0`, `puntaje_ia` y `divergencias` del 28-sep **siguen SIN MEDIR**, y `puntaje_ia` es el campo
  de las **24** filas —no de las 8— que entran a `verificacion_puntaje` alrededor del **5-oct**. Es el
  ítem con más filas en juego, y **esa diferencia ya no se puede medir nunca**: la barra parcial de las
  13:42 no existe más, así que sólo se puede medir el valor correcto.

  Salvedades: −1,61 se leyó 31 min después de la campana y **no es necesariamente el cierre liquidado**;
  es **una** fecha; la coincidencia del régimen es **evidencia débil por construcción** (etiqueta binaria,
  margen 37,5 contra 38,8); los 27 puntos son el **piso** —el crudo sellado implícito es ≈ +3 % contra el
  −2,8 % real, o sea **cambio de signo, ~5,8 pp, INFERIDO** e inmedible porque se sella el percentil y no
  el crudo—; la columna «recomputado» **no es reproducible por nadie** (se corrió sin dejar artefacto; el
  auditor verificó su coherencia interna y la aceptó por la palabra de la bitácora); y **esta medición no
  decide la regla** (retirar filas sólo si el signo salió mal sería elegir qué filas cuentan después de
  verlas — y rescatarlas porque salió chico, también).

  (iv) **MEDIDO, nada publicado contaminado:** `cifras.CORTE_README = 2026-08-28` y `verificacion_apertura`
  no tiene ninguna fila con `fecha_senal = 2026-09-28`. Lo que se verifique desde el 29, sí. Y el riel de
  dinero descartó sus 33 filas del mismo evento por su guarda E4 (`no_verificable_timing`,
  `cuenta_para_N = 0`): **el mismo evento físico, dos resultados, por una regla que un riel tiene escrita y
  el otro no.**

  **Lo que la corrida 14 midió sobre la sonda y que NO entra acá, por regla:** el cruce ticker por
  ticker contra el meta del sello en las cuatro noches, las 0 transiciones «el cierre estaba y deja de
  estar» dentro de una noche, y la equivalencia de la regla nueva de atribución sobre las 1.188 filas ya
  escritas. **Son MEDIDOS por censo y reproducibles, pero ningún dictamen los cubre**, y este documento
  es publicado: el encargo condiciona la entrada a que un dictamen lo autorice. Viven completos en
  `bitacora_14.md` (bloques 1.2 y 1.6) hasta que un dictamen los tome. Lo marcó el
  `guardian-constitucion` al cierre.

  (vii) **MEDIDO: yfinance etiqueta la barra intradía con la fecha del día.** A las 13:42 NY del 28, con el
  mercado abierto, 35 de 36 tickers ya daban `ultima_fecha_close = 2026-09-28`. Consecuencia: el campo
  `es_sesion_de_hoy` de la sonda **sólo es interpretable fuera del horario de mercado**, y el resumen ahora
  descarta y declara las observaciones anteriores al cierre de su sesión.

  (ix) **MEDIDO: `Persistent=false` no impide un disparo atrasado por suspensión.** La unidad instalada de
  la sonda lo lleva y disparó igual; `Persistent=` sólo gobierna disparos perdidos mientras el *manager* no
  corría, y el manager no se cayó. **Que la máquina estuviera suspendida y no apagada es una INFERENCIA**
  (hueco del journal + PID sobreviviente + uptime): WSL2 no registra suspend/resume, y la ventana sólo se
  puede acotar a [vie 02:16, vie 17:50] Chile.

  (x) **MEDIDO y dictaminado por el `estadistico-adversario`: el umbral de M2 firmado en §88.11
  (25/3 = 8,3333 %/año) es 156/h veces MÁS EXIGENTE que el 25 % acumulado** — 3× a las 52 semanas, que es la
  única lectura que la propia enmienda autoriza. Sobre la cuenta v2 simulada a h = 52, el umbral viejo
  dispara **0 de 20 semillas** en los tres juegos y el nuevo dispara **19 de 20** en el juego `medio`
  (Wilson 95 % [76,4 · 99,1] **sobre semillas**, una sola trayectoria de mercado). La primera versión de la
  §9 del pre-registro afirmaba que el umbral «no endurece ni ablanda el criterio»: **era falso y se corrigió
  antes de cualquier commit.** **El 19/20 se computó FUERA del módulo dueño del umbral** (`GEMELO/m2_periodo.py` sigue con
  `UMBRAL_M2_PCT = 25.0`), así que **no es reproducible corriendo ese módulo** — la misma vara que el
  §61 le aplica a las 24 filas del 28-sep. La enmienda queda **PROPUESTA y NO APLICABLE: le faltan seis
  definiciones**,
  la más urgente **qué es «el primer aporte»** (con la cuenta IBKR ya fondeada con 5,00 USD, dos órdenes al
  mínimo dan 14 %/año y M2 dispara).

  (xi) **DEMOSTRADO por censo: el riel de dinero lleva 14 sesiones selladas prospectivas por el timer, de
  las que 9 cuentan para N = 40** (no cuentan 09, 18, 22 y 23-sep por `insumo_incompleto` ni el 28 por
  `no_verificable_timing`). **La sesión del viernes 25-sep se perdió en los TRES rieles** (sellador, medición
  y sonda), y leído el código la del 28 también se pierde en el riel de dinero. E0 sella el sorteo sin
  información: **prueba de maquinaria, no track record**.

  **Registro de intentos:** gap asiático 354, veredicto 5.1 360 y riel largo 4, **los tres sin cambio** — el
  único bloque que iba a probar una hipótesis (`bifurcaciones`) no se ejecutó. **Los bloques que publican
  cifras NO se ejecutaron** por el veredicto del auditor, así que ninguna cifra publicada se movió.

- **Corrida 13 (19-sep), con dictámenes del `auditor-lookahead` (E4-bis), del `curador-epistemico` (bitácora, tarjetas,
  README inglés) y del `estadistico-adversario` (README y bloque 6); `dictamen_13/`:** (i) **DEMOSTRADO por censo de la
  base en `mode=ro`: el riel de dinero lleva 9 sesiones selladas prospectivas por el timer sin intervención humana
  (08 al 18-sep), de las que 7 cuentan para N = 40** (E0 sella el sorteo sin información: prueba de maquinaria, no
  track record, §86.2); las dos que no cuentan (09 y 18-sep) fueron `insumo_incompleto`. (ii) **DEMOSTRADO con test
  escrito antes de la corrección:** el sellador pisaba `ext_<fecha>.csv` de una fecha ya sellada cuando el timer volvía
  a disparar (el 10-sep, nueve días con el disco citando otro sha que la base); corregido (opción A: con la fecha
  sellada no se escribe ningún archivo de esa fecha), con test permanente de integridad disco = base en la suite.
  `senales.db` y `dinero/sello_dinero.db` intactas (sha256 antes = después). (iii) **MEDIDO (n = 1 par de descargas, 1
  ticker):** en dos descargas de yfinance por la misma ruta separadas 24 h, los cierres de TOELY del 08 al 15-sep
  pasaron de estar a estar vacíos; que el borrado ocurra en Yahoo y no en la ruta es PROPUESTA sin segunda vía. Con la
  definición firmada (§57) una columna vacía pierde la sesión: 1 pérdida en 9 noches (Wilson 95 % [0,02, 0,44]). La hora
  del timer se decide con el dato de la sonda (§58, sin instalar). (iv) **PROPUESTA (descriptivo, sin verdad conocida
  para este estimador):** universo operable por presupuesto con acciones enteras (`universo_por_presupuesto.md`): 7 de
  36 alcanzan una acción entera a 100 USD, 13 a 250, 29 a 500; semillas conservadoras congeladas 5 de 20 a 500 USD
  (reproducción de la corrida 12, no verificación); las filas no son pareadas. (v) **PARIDAD DEMOSTRADA por instrumento
  propio del adversario:** README.md (inglés) ≡ README.es.md ≡ árbitro, token a token; ninguna cifra movida por la
  traducción; ninguna afirmación de ventaja en ningún idioma. Erratas pendientes de Nicolás en las dos páginas (N de
  intentos 352/358 contra 354/360; «59×»; badges): `cola_decisiones.md`. **Registro de intentos:** gap asiático 354 y
  veredicto 5.1 360 sin cambio; riel largo 3 → 4 (barrido descriptivo del bloque 6).

- **Corrida 12 (9-sep), con re-dictamen del `estadistico-adversario` sobre las cifras re-corridas de la 11
  («se sostienen en los artefactos y NO en la forma en que la API las servía»; cuatro cifras retiradas y
  D1–D18 aplicadas al ejecutable), dictamen del `auditor-lookahead` sobre el sellador (primero «NO SE
  SELLA», cinco fugas demostradas; tras E1–E8, «SE PUEDE SELLAR») y dictamen del adversario sobre el §43
  (NO APLICABLE); `dictamen_12/`:** (i) **DEMOSTRADO por censo: el riel de dinero tiene UNA sesión sellada
  prospectiva** (9-sep-2026 03:38 UTC, 33 filas, tamaño nominal cero, `available_at` por calendario
  anterior a la emisión y ésta anterior a la apertura objetivo; `cuenta_para_N` 1 de 40; `senales.db`
  intacta). Lo que esa fila NO es: un track record de habilidad — la señal sellada es la sonda sin
  información y la fila lo declara (`dinero/sello_dinero.db`, `data/backups/sello_dinero.csv`). E1 (cuenta
  de práctica) **NO EJECUTADO**: adaptador con guardia de papel probado contra una réplica escrita desde
  documentación, que NO es evidencia de C1/C2. (ii) **M2 no tiene unidad de período** (numerador flujo,
  denominador fijo): recomputado sobre la v2, el juego por defecto gasta 3,9 %/año [3,56, 4,58] del
  capital aportado en comisiones (tasa anualizada, estable a 52/104/156 semanas; una sola trayectoria de
  mercado, 20 sorteos, deslizamiento excluido) y no cruza el 25 % acumulado en ningún horizonte; la firma
  §84.4.5 quedó NO APLICABLE y M2 vuelve a firma (`m2_periodo.md`). (iii) Las cifras del riel que la API
  sirve ahora viajan con su cobertura medida (IC de σ: nominal 95 %, cobertura 0,850), la fricción como
  objeto (mediana 12,4 % de 20 semillas, banda [6,35, 13,2], 156 semanas sobre 500 USD), el R2 recomputado
  bajo la regla firmada (+2,6 pp, n=194, t de clúster [−15,7, +20,9], contiene el cero) y la cobertura del 80 % con Wilson
  (92,9 % [88,9, 95,5]). (iv) Hallazgo del primer sello: reajuste retroactivo de yfinance en WDC entre el 7
  y el 9-sep (dif. rel. 3,2 × 10⁻⁴), detectado y declarado, no corregido. **Registro de intentos:** gap
  asiático 352 → 354 (fila `COHER-12`, exigencia D18: la regla de filas de coherencia se evaluó y nunca se
  contó); veredicto 5.1 358 → 360; riel largo 3. Lo que nada de esto autoriza: ninguna afirmación positiva
  sobre ningún riel.

- **Corrida 11 (8-sep), con dictamen del `estadistico-adversario` («sostiene con
  exigencias» en los tres artefactos; exigencias aplicadas al ejecutable y re-corridas,
  y las cifras re-corridas NO volvieron a pasar por el adversario) y del
  `auditor-lookahead` sobre la reconstrucción («no encontré fuga», diez exigencias, ocho
  aplicadas; `dictamen_11/`):** (i) **El instrumento del riel de dinero** (`contabilidad.comparar`
  más la regla §2.3 del pre-registro) **discrimina una ventaja verdadera de cero pero no
  está calibrado a α = 0,05**: tamaño bilateral 0,086 [0,074, 0,099] y cobertura 0,914
  [0,901, 0,926] a 52 semanas (0,064 y 0,936 a 156); el bootstrap de una desviación cubre
  0,78 a 0,85; MDE80 a 52 semanas 1,05 pp/semana (≈ 55 pp/año), con σ ancla 2,704
  (`instrumento_dinero.md`). (ii) **La rama de coherencia** (n = 223, +14,3 pp, retiro
  firmado en §82.3, NO cableada) tiene IC de clúster de día que **contiene el cero en las
  tres rutas** (percentil [−1,4, +32,1]; t de clúster, el calibrado, [−3,5, +32,2];
  permutación p = 0,111) y bajo R2 cae a +7,8 pp, p = 0,433: es otro estimando, no una
  remedición de +9,7, y el movimiento sale de 2 días de 34 (`intervalo_coherencia.md`).
  (iii) **La cuenta en papel v2, reconstruida y PROPUESTA** (gate de invariancia INVARIANTE
  en 25 cortes por regla con contraprueba; cobertura causal 28 % / 84,5 %; el auditor no
  encontró fuga, y que no queden fugas no es demostrable): con señal sin información y el arancel publicado del §40, el juego por
  defecto gasta 12,4 % de lo aportado en comisiones sobre 156 semanas (mediana sobre 20
  semillas 12,4 %, banda [6,4, 13,2]), fricción que fija el número de órdenes y no el
  arancel; ningún juego muestra ventaja positiva contra SMH; σ de la diferencia semanal
  2,336 pp/semana, cuyo intervalo publicado NO es un 95 % (`cuenta_papel.md`). Lo que estas
  tres cosas NO autorizan: ninguna afirmación positiva sobre ningún riel.
- **RETIRADO en la corrida 11:** la cuenta en papel v1 (7-sep) queda reemplazada; sus
  cifras (27 % / 57 %, 14 % a 43 %, σ 2,54) siguen retiradas y no se comparan con la v2.

- **Novena corrida (3-sep), con dictamen del adversario y SIN dictamen del
  guardián ni del curador (agentes caídos por límite de API; este documento se
  publicó sin curaduría y se corrigió el 6-sep con los dos dictámenes en mano):** (i) la enmienda
  V1-bis v2 (`GEMELO/preregistro/enmienda_v1bis.md`) es un **cambio de
  pregunta, no de vara** —firmable como tal—; con verdad conocida, la
  conjunción MAE ∧ CRPS tiene tipo I 0,021 [0,014, 0,032] a 73 días, el CRPS
  contra una climatología en muestra se infla a 0,075 [0,060, 0,093] a 250
  días, y «MAE contra cero» es positivo bajo ventaja nula el 54 % [51, 57]:
  mide también la deriva del gap. (ii) La frase de potencia del 5.1 en dos
  versiones (`espera_firma.md` §29): dirección 0,30 [0,27, 0,33] a 9 pp el
  25-oct; magnitud en banda 0,90 / 0,86 / 0,70 (generador / observado / R2),
  96 [20, ∞) días al efecto observado; ninguna fecha encabeza. (iii) Sobre
  la ventana sellada al nivel de día **nadie mejora a predecir cero de forma
  distinguible**: campeón +0,375 pp [−0,201, +0,955], control lineal C1
  +0,362 [−0,055, +0,803]; cada intervalo contiene el cero
  (`corrida09/ic_dmae_recomputados.md`; el bloque
  de filas sí lo excluía: la unidad cambia la respuesta). (iv) Bajo el parche
  de `snapshot.py:140`, las 25 filas con sesión objetivo incorrecta serían
  todas `no_verificable_timing` (censo; corrige el «15» de la cola). (v)
  **El juez lineal bajo D3 (EXPLORATORIO, dictamen: cifras sostienen, lectura
  corregida, NO CONCLUYENTE):** sobre 262 filas / 37 días el control lineal
  C1 supera a predecir cero en MAE (+0,39 [+0,05, +0,73]) pero no al campeón
  sobre las mismas 254 filas (−0,17 [−0,38, +0,03], contiene el cero; allí el
  campeón supera a cero +0,56 [+0,09, +1,03]) y **no sobrevive a R2**; los 16
  features no traen magnitud detectable distinta de SOX(t, t−1).
- **Octava corrida (2-sep):** el instrumento calibrado con verdad conocida
  (`calibracion_instrumento.md` v2) y su riesgo declarado (con dependencia
  entre días ρ = 0,2 el tamaño de la permutación sube a 0,061); la frase de
  potencia en dos versiones (`espera_firma.md` §22, NO CONCLUYENTE hasta
  decidir la rama del efecto); el plan secuencial v5 (quinto rechazo, en la
  cola); el sello verificable por un tercero, el pre-registro del RTL con
  criterio de muerte y V1-bis (`GEMELO/propuestas/`); y el árbitro de cifras
  (`cifras.py`) con la regla de los doce bloques ejecutable.

- La ausencia intermitente de una barra del `^SOX` en cuatro noches de
  agosto explica las betas selladas que hoy no reproducen (hipótesis por
  fuerza bruta, única barra de 130, residuo 4–8× el piso; sin testigo
  directo). Dictamen: sigue siendo hipótesis.
- La pendiente de calibración magnitud predicha → realizada sobre lo
  sellado: 1,42 [0,65, 2,19] (contiene 1; excluye 0). Dictamen: entra sólo
  como endpoint secundario pre-registrado contra el control lineal, no
  contra cero.
- **Retirada por el dictamen:** «el decaimiento es −1,6 pp de ventaja por
  hora de margen, IC95 [−2,45, −0,77]». La unidad de replicación del
  mecanismo es la bolsa —cuatro, con dos valores de margen— y con cuatro
  bolsas no se ajusta una curva (`README.md` ya lo decía): p mínimo
  alcanzable 1/13. Queda el escalón por bolsa, no la pendiente.

---

**En una frase, para el que pregunta:** MKI demuestra que un experimento de
pronóstico puede sellarse y auditarse con rigor a costo cero; mide, sobre
ocho años reconstruidos, un escalón real entre bolsas —tres cercanas arriba, la
lejana no distinguible de cero— cuya lectura como decaimiento con el margen falló
fuera de muestra (14b); demuestra que **no** se puede
capturar entrando en la apertura, ni al derecho ni al revés, y que eso
replica fuera de muestra; y todavía **no** puede confirmar prospectivamente el fenómeno,
porque su ventana sellada es unas siete veces más corta que lo que hace
falta para ver un efecto del tamaño que importa.

*Herramienta de análisis y aprendizaje — no constituye asesoría financiera.*
