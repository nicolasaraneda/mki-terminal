# Qué puede afirmar MKI Terminal hoy — estado epistémico (9-sep-2026, actualizado al cierre de la corrida 12)

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
viven en `README.md`; las de esta semana, en `GEMELO/resultados/`.

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
