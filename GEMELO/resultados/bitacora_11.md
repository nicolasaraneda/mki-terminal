# Bitácora de la undécima corrida — validar el instrumento, reconstruir sin fuga, ejecutar seis firmas

**8-sep-2026, nocturna y sin supervisión.** Encargo: `GEMELO/resultados/encargo_corrida_11.md`
(v2, post acta §82). Arranque **00:43 hora de Chile** (leído de `date`), martes, fuera de la
ventana de sellado 17:50–20:30. HEAD al abrir: `66d1c5a`.

- Suite al abrir: **754 passed, 5 xfailed** en 336,13 s (arrancó 00:44, terminó 00:50 según `date`); `tests/test_motor.py` OK. Los 5 xfail son los declarados (2 de `test_epistemico.py`, 3 estrictos de `test_dinero.py`).
- Registro de intentos del gap asiático (`GEMELO.relevo_asiatico`): **NO se toca** (352 / 358).
- Nada se pushea. Nada se firma. Ningún archivo protegido se toca.

## Bloque 0 — la tarjeta del §42, corregida antes de que nadie la lea. **Cerrado 00:46.**

Se sacó de `espera_firma.md` §42 (columna «Consecuencia» de la opción A) la frase que
afirmaba que el signo de la conclusión ya se sabía que aguantaba y citaba el movimiento
27 % → 57 % del juego medio. Queda una nota de errata fechada 8-sep-2026 remitiendo al §82.4.
Verificado con `grep`: no queda «27 %» ni «57 %» en `espera_firma.md`. Ningún agente leyó la
tarjeta antes de la corrección (el orientador y el pre-mortem se lanzaron después).

**Nota:** las mismas cifras siguen impresas en `dinero/resultados/cuenta_papel.md` (rotuladas
RETIRADAS, con la causa) y en el encabezado de `dinero/cuenta_papel.py`. No se tocan en este
bloque: el §82.4 ordena corregir la *tarjeta*; la página retirada se reemplaza al republicar
(bloque 2).

## Pre-mortem del `director-programa`, antes del bloque 1 (00:49, hora de `date`)

Quince instrucciones marcadas. Qué se hizo con cada una, decidido ANTES de ejecutar el bloque 1:

| # | Instrucción marcada | Decisión del orquestador |
|---|---|---|
| 1 | Bloque 1: magnitudes sin declarar; sugiere anclar a +6,45/+9,66/+14,3 pp | **Acatada en la forma, no en las cifras.** Las tres magnitudes se declaran abajo antes de correr. Las sugeridas son del riel de MEDICIÓN (gap de una noche); el instrumento que el bloque 1 valida es el del riel de DINERO (ver la instrucción 16, propia), cuya unidad es pp/semana. Se anclan a la tabla §2.1 del pre-registro del riel, escrita el 7-sep antes de esta corrida. |
| 2 | Bloque 1: criterio de fallo compara puntos, no intervalos | **Acatada.** Criterio sobre intervalos de Wilson, con margen, declarado abajo. |
| 3 | Bloque 1: la suspensión tira 7, 8 y 9 que no dependen del simulador | **No acatada, con constancia.** El prompt de Nicolás dice «suspendé todo lo demás». Si el bloque 1 falla, se suspende todo y se deja anotado que 7, 8 y 9 eran ejecutables. |
| 4 | Bloque 4: segunda ruta sólo si contradice la predicción (asimétrico) | **Acatada.** Segunda ruta siempre: bootstrap de día Y t de clúster Y permutación, se publiquen como se publiquen. |
| 5 | Bloque 4: el conjunto «coherencia n=223» puede no ser «238 − 15»; el 223 es de acta | **Acatada.** Se prueba identidad de conjuntos (n y las 15 por fecha+ticker) antes de computar; si difieren, se para y se anota. |
| 6 | Tabla del §2: «se retiran las 15 filas» leída sola autoriza tocar el README | **Acatada.** Rige el texto del bloque 4: nada se cablea, ninguna cifra publicada se mueve. |
| 7 | Bloque 3: el «antes» se destruye si se mide después del 2 | **Acatada.** Se parte en 3a (medir antes, previo al bloque 2) y 3b (después). Orden efectivo: 0 → 1 → 4 → 3a → 2 → 3b → 5 → 6 → 7 → 8 → 9 → 10. |
| 8 | Bloque 2: un xfail estricto puede fallar por otra razón | **Acatada.** `--runxfail` sobre los tres antes de tocar `cuenta_papel.py`, con el mensaje en la bitácora. |
| 9 | Bloque 7: editar `.md` generados y pegar un 30 de memoria | **Acatada.** El aviso lo emite el generador con los dos números computados; los generados se regeneran. |
| 10 | Bloque 6: `available_at == timestamp_utc` tiene tres causas, y el 295 es de acta | **Acatada.** Conteo segmentado por estado/`modelo_version`/`sox_fecha`; el total se lee de la base. |
| 11 | Bloque 8: sacar el xfail presiona a reformular frases con cifra | **Acatada.** Sólo agregados de método; diff del README en la bitácora; si el regex obliga a reformular una cifra, se para. |
| 12 | Bloque 9: el guardia de razones de xfail es frente nuevo, rama lateral | **No acatada, con constancia.** El encargo lo pide explícitamente («escribí el guardia que falta») y es del mismo tipo que el detector de citas desplazadas que ya existe. Se hace al final, después del 10, y si el tiempo no alcanza queda como no iniciado. |
| 13 | Cierre 3: limpiar la cola borra el recordatorio de aplicar el §26 | **Acatada.** Los seis ítems van a una sección «firmado en §82, pendiente de ejecución» con lo que le queda a Nicolás, no se borran. |
| 14 | Cierre 7: «verde» indefinido choca con XPASS estricto del bloque 2 y el rojo del 9 | **Acatada.** Verde = sin fallos no declarados. Inventario de xfail esperados al abrir: 2 (`test_epistemico.py:572` y `:775`) más los 3 estrictos de `test_dinero.py`. |
| 15 | Regla 0.5 vs bloques 1 y 10: el censo sale a la red | **Acatada.** Todo fuera de la ventana (arranque 00:43). El segundo día de censo descarga una vez, se congela con sha256, y si la descarga falla el censo del día se declara no iniciado en vez de reintentar. |
| 16 | **Propia, no del pre-mortem:** «Corré `GEMELO/simulador/`» leído literal repite lo ya hecho | El simulador existente (`calibracion.py`, Frente A) YA corrió δ ≠ 0 para el riel de medición (A1 cobertura a 8,97 pp, A2 a 6,5 y 9 pp, A4 potencia a 5/6,3/9 pp). La mitad que falta, según el dictamen #23 del adversario de la corrida 10 (`dictamen_10/estadistico_adversario.md`), es la del **instrumento del riel de dinero**: `contabilidad.comparar` + criterio §2 del pre-registro. Se escribe un módulo nuevo en `GEMELO/simulador/` que simula ESE instrumento con ventaja conocida; no se re-corre el Frente A. |

Menores, con constancia: la advertencia del §82.4 sobre el número de operaciones se lee DESPUÉS de computar la fricción, no antes. Bloque 5: se prefiere alerta o test antes que marca en la fila (una columna nueva toca el esquema sellado). Bloque 10: el primer censo está congelado con sha256 (`cierres_congelados.meta.json`, `69ca7283…`), así que la comparación entre días es legítima.

## Bloque 1 — la mitad que falta de la calibración. Declaración previa (00:49 según `date`, antes de correr)

**Instrumento bajo prueba.** `dinero.contabilidad.comparar(valor_estrategia, valor_base, semilla)`:
diferencia de retorno semanal, IC95 por bootstrap circular de bloques de 4 semanas, 2.000 réplicas.
**Regla de decisión bajo prueba:** condición 3 del §2 del pre-registro (`dinero/preregistro_dinero.md`):
el IC excluye el cero y el punto es positivo, evaluado UNA vez a 52 semanas. Se agrega el horizonte
de 104 semanas porque M1 lo nombra. La función se llama tal cual está en el código: el instrumento
es el implementado, no una reimplementación.

**Verdad conocida.** Diferencia semanal `d_t = δ + σ·ε_t`, ε t de Student con ν = 4 estandarizada,
AR(1) ρ sobre ε (ρ = 0 base). Como `comparar` resta retornos semanales, la serie de la base es
irrelevante para el estadístico; se genera igual (retornos semanales reales de `SMH` remuestreados)
para que la función reciba lo mismo que en producción.

**Magnitudes, declaradas antes de correr:** δ ∈ {0 (nula), +0,25, +0,50, +1,00} pp/semana. Salen
de la tabla §2.1 del pre-registro (escrita el 7-sep) y no de esta corrida. NO se usa la σ = 2,54
de esa tabla: es cifra de la cuenta con fuga, RETIRADA. σ se mide acá, de los precios congelados,
como desviación de la diferencia semanal entre una cartera equiponderada de 4 instrumentos
operables sorteada y `SMH` (K = 4 es el del juego conservador), con intervalo por bootstrap de
bloques sobre semanas, y se barre en {0,5σ, σ, 2σ}.

**Réplicas:** 2.000 por celda. Semilla del estudio 20260908; semilla del bootstrap POR RÉPLICA
(lección del Frente A: re-sembrar igual condiciona todas las réplicas a una sola matriz).

**Qué se reporta por celda:** proporción de detección (IC excluye 0 y punto > 0) con Wilson 95 %;
tamaño bilateral bajo la nula (IC excluye 0, cualquier signo); cobertura del IC (contiene δ) con
Wilson; y una segunda ruta: la potencia normal cerrada Φ(δ√T/σ − 1,96) con la misma σ.

**Criterio de fallo, escrito antes:** el instrumento NO discrimina si, en la celda base
(σ medida, ρ = 0, 52 semanas), para NINGUNA de las tres magnitudes el límite inferior de Wilson de
la detección supera el límite superior de Wilson de la falsa detección bajo δ = 0. Si eso pasa,
se suspende el resto de la corrida (prompt de Nicolás) y se cierra con bitácora.

**Intentos del DSR:** 0. No se evalúa ninguna hipótesis sobre datos reales; los precios entran
sólo como parámetro de calibración (σ) y como serie de la base.

## Bloque 1 — ejecución y resultado. **Cerrado 00:57 (primera corrida); re-corrido 01:31 con las exigencias del adversario.**

Módulo nuevo `GEMELO/simulador/instrumento_dinero.py` (+ `tests/test_instrumento_dinero.py`, 7 tests
con contraprueba de «no discrimina»). Resultado en `GEMELO/resultados/instrumento_dinero.md` / `.json`.

- **Veredicto por el criterio pre-declarado: el instrumento DISCRIMINA.** Falsa detección bajo
  δ = 0 a 52 semanas 0,046 [0,038, 0,057]; detección 0,136 [0,122, 0,152] a +0,25, 0,344 [0,323,
  0,365] a +0,50, 0,790 [0,772, 0,808] a +1,00 pp/semana (2.000 réplicas por celda). El piso de
  Wilson supera el techo de la nula en las tres magnitudes. **La corrida sigue.**
- **Hallazgo que el criterio no gateaba:** bajo la nula el tamaño bilateral es 0,086 [0,074, 0,099]
  contra 0,05 y la cobertura 0,914 [0,901, 0,926] contra 0,95; con ρ = 0,2 la cobertura cae a
  0,885. Es el percentil de bloques a n = 52 (el adversario probó con ε normal: no son las colas).
  A 104 semanas, cobertura 0,933. **El instrumento discrimina pero no está calibrado a α = 0,05.**
- σ ancla medida 2,704 pp/semana, IC de la mediana entre sorteos [2,477, 2,895], banda entre
  sorteos [1,911, 4,016]; 200 carteras de 4 entre 33 operables, 156 semanas. La σ = 2,54 retirada
  no se usó.
- Segunda ruta (normal cerrada a α 0,05): 0,098 / 0,265 / 0,760, por debajo del simulador; el
  adversario mostró que la brecha es exactamente el tamaño inflado (a α = 0,086 coincide).
- Intentos del DSR: 0.

**Dictamen del `estadistico-adversario`: SOSTIENE CON EXIGENCIAS** (A1 a A7). Aplicadas en el
ejecutable y re-corrido (01:31): brazo de calibración declarado como agregado a posteriori (A1),
MDE80 en pp/semana y pp/año (A2), celda T = 156 (A3), ρ medido por AC1 (A4), potencia cerrada
al α real (A5), contraste con la σ realizada de la cuenta v2 (A6), cobertura del IC de la sd
(C4), regla de no barrer el bloque sin declararlo (A7). Las cifras finales están en el artefacto
regenerado; la decisión sobre el estimador va a `espera_firma.md` §50.

## Bloque 4 — el intervalo de clúster del +14,3 pp. **Cerrado 00:57; re-corrido 01:31 con R2.**

`GEMELO/intervalo_coherencia.py` → `GEMELO/resultados/intervalo_coherencia.md` / `.json`.

- **Identidad de conjuntos:** coherencia (n = 223) ⊂ regla firmada (n = 238); los dos órdenes
  (filtro→convención, convención→filtro) dan el mismo conjunto; 15 retiradas: 8 del 2026-07-05
  (día entero) y 7 del 2026-08-05 (queda 1 fila: día mutilado). Las dos fechas eran informativas,
  Σ(modelo − base) = −4 cada una.
- **Rama de coherencia:** +14,3 pp, IC95 percentil de día [−1,4, +32,1], t de clúster [−3,5,
  +32,2], permutación de día p = 0,111, ICC 0,421, DEFF 3,71, n efectivo 60, 33 días (15
  informativos), b/c 69/37, McNemar χ²cc 0,0026, exacta 0,0024. Regla firmada al lado: +9,7 pp,
  [−7,2, +26,6], [−8,1, +27,4], p = 0,294, 34 días.
- **La predicción del §82.3 se cumple en las tres rutas: el intervalo contiene el cero.**
- **R2 (exigencia B1), computado en la misma página:** sin el 15–23 jul la rama de coherencia cae
  a +7,8 pp, percentil [−9,1, +25,6], t [−10,8, +26,5], permutación 0,433, exacta 0,1354 (n = 179,
  27 días); la regla firmada cae a +2,6 pp, p = 0,821. Las dos fechas retiradas están fuera del
  bloque de R2.
- El retiro se llevó 2 de los 6 días negativos y 0 de los 10 positivos: es el mecanismo que el
  acta escribió antes, y **+14,3 pp es otro estimando**, no «+9,7 medido mejor».
- Nada cableado; ninguna cifra publicada se movió. Intentos: 0 (si se cablea, es un intento: B5).

**Dictamen del adversario: SOSTIENE CON EXIGENCIAS** (B1 a B5), las cinco aplicadas al ejecutable.
Hallazgo de paso (§82.5): la discrepancia del p titular traspaso/espera_firma (0,0455 vs 0,0451) SÍ
es la pareja de rutas; la del último decimal del IC (26,6 vs 26,5) NO: es el número de réplicas
del bootstrap de día (4.000 en `cifras.py`, 10.000 por defecto en `bifurcaciones`).

## Bloque 3a — cobertura por causalidad ANTES de reconstruir. **Cerrado 00:57.**

Herramienta nueva `dinero/cobertura_causal.py` (definición: líneas ejecutables que ejecuta al menos
un test de invariancia al truncado QUE PASA, sobre el total; «tocada» cuenta también los que
fallan). Sin coverage.py (no está en requirements): `sys.settrace` + objetos de código.
**Antes:** `cuenta_papel.py` 344 líneas, tocadas 27 (7,8 %), **cubiertas 0 (0,0 %)**;
`contabilidad.py` 216 líneas, tocadas 151 (69,9 %), **cubiertas 0 (0,0 %)**. Los tres xfail
fallaban por su razón escrita (verificado con `--runxfail`, mensajes en la salida: F1 «la
membresía se decide con el último cierre», F2 «252 de 252 días cambian de señal», F4 «retardo
cero»). Historial en `dinero/resultados/cobertura_causal.json`.

## Bloque 2 — reconstrucción de la cuenta en papel. **Cerrado 01:08; re-corrido 01:35 con K semillas.**

Orden del auditor respetado: test de truncación primero (ya estaba), después E1, E3, E4, E5, E6,
después republicar. Ningún MAE se calculó (la cuenta no computa ninguno).

- **E1** `cuenta_papel.universo_operable(cierres, cfg, hasta=DESDE)`: membresía con los cierres
  hasta 2023-09-05 → **33 operables** (antes 29 con el último cierre; los excluidos eran los que
  más subieron).
- **E3** `contabilidad.senales_sin_informacion(..., desde)`: sortea de retornos anteriores a
  `desde`; revienta con menos de 60 retornos de historia.
- **E4** `RETARDO_IMPLEMENTACION = 1` en `linea_base` y `correr_estrategia`; `Movimiento` lleva
  `decidida_el` y `acciones_decididas`; `Libro.decisiones` registra toda decisión; la caja
  comprometida por órdenes pendientes se descuenta al decidir. Un test exige que el retardo sea
  el mismo de `senal_larga`.
- **E5** `derivacion.sigma_60d_pct(hasta=)`: σ de SMH hasta 2023-09-05 = 14,17 % (era 15,62 %
  sobre el archivo entero).
- **E6** `cuenta_papel.verificar_invariancia()` → `ErrorLookAhead`; cortes declarados 2024-09-04 y
  2026-03-31; compara movimientos ejecutados Y decisiones hasta el corte; `main()` lo corre antes
  de escribir. **INVARIANTE (5.066 movimientos comparados).** Contraprueba en la suite: una
  fábrica de señales que mira un día adelante hace disparar el gate.
- **Arancel:** el del insumo §40, columna de ENTERAS (0,0035 / 0,35 / 1 %), en `reglas.json`
  (0.2.0-PROPUESTA); umbrales y apagados recomputados por su regla (conservador 3,49 → 1,35 pp;
  apagado 15,6 → 14,2 %). El §40 sigue sin firma: lo firmado es reconstruir con él.
- **Resultado (v2, PROPUESTA):** fricción del juego por defecto 12,4 % de lo aportado (mediana
  sobre 20 semillas 12,4 %, banda [6,4, 13,2]); medio 26,7 % [14,6, 28,7]; agresivo 19,0 % [18,0,
  20,2]. Órdenes 210 / 436 / 373 (medianas). **La fricción la fija el número de órdenes, no el
  arancel**, leído después de computar como manda el §82.4. IC que excluyen el cero: 51 de 480
  sobre 20 semillas (0,106, Wilson [0,082, 0,137]), y NO es una tasa de falsos positivos. σ de la
  diferencia semanal (conservador vs SMH, 5 pb): 2,336 pp/semana, IC de bootstrap de la sd
  [1,995, 2,669] (cobertura de ese IC medida en el bloque 1 re-corrido). Ningún juego muestra
  ventaja positiva que excluya el cero contra SMH.
- API y frontend: `cifras_disponibles` y `potencia` se leen del artefacto (contrato enmendado);
  la vista lee la nota del JSON en vez de prosa fija sobre la v1. `npm run build` OK.
- **Ajustes a tests, declarados:** F1 apuntaba a `construir_mapa` (la función del censo, que
  mira el último cierre por diseño) y no podía pasar con ninguna corrección: ahora apunta a
  `universo_operable`; F2 pasa el archivo completo y `desde`; F4 perturba el día de ejecución y
  exige la decisión invariante. Dos tests con arancel fijo del test en vez del de `reglas.json`.

**Dictamen del adversario: SOSTIENE CON EXIGENCIAS** (C1 a C6): K = 20 semillas con banda (C1),
aritmética de primer orden corregida como cota superior con el tope del 1 % (C2), nota de
cobertura al horizonte de 156 semanas (C3), cobertura del IC de la sd en el simulador (C4),
errata fechada §7 en `preregistro_dinero.md` sobre M2 (C5), contraste de σ (C6). **M2 con la v2
no se dispara para el juego por defecto (12 % contra 25 %), pero sigue sin poder leerse** hasta
las cuatro precisiones de `espera_firma.md` §43. **Dictamen del `auditor-lookahead`:** ver la sección «Dictámenes» al final y
`dictamen_11/auditor_lookahead.md`.

## Bloque 3b — cobertura por causalidad DESPUÉS. **Cerrado 01:09.**

`cuenta_papel.py` 389 líneas, cubiertas **109 (28,0 %)**; `contabilidad.py` 278 líneas, cubiertas
**235 (84,5 %)**. Cinco tests de truncado pasan. Sin cubrir en `cuenta_papel.py`: `componer`,
`a_json`, `_resumen`, `sigma_diferencia_semanal`, `main` (composición del reporte: no transforman
datos en decisiones; el gate no los necesita). Sin cubrir en `contabilidad.py`: `comparar` y
`retornos_semanales` (los cubre el bloque 1 por otra vía: simulación con verdad conocida), y
ramas de `Libro.comprar/vender` (venta parcial, caja insuficiente) que la ventana real no ejercita.

## Bloque 5 — el guardia de la rama del `except`. **Cerrado 01:24.**

`GEMELO/propuestas/parches/guardia_ancla_temporal.diff` (NO aplicado; 103 líneas; toca
`snapshot.py`, `senales.py`, `mki_vigia.py`) + `tests/test_parche_guardia_ancla_temporal.py`
(6 tests sobre copias: los dos diffs aplican juntos, camino feliz, `cierre_utc` falla → aviso +
vigía FALLA, `sox_fecha` vacío → ídem, contraprueba de que el original calla, y el verificador
cuenta `sin_calendario`). **Propuesta: alerta del vigía más línea de log, no marca en la fila**
(razón: la evidencia ya está en la base, `available_at == timestamp_utc`; una columna es cambio
de esquema en filas selladas). El patrón de `senales.py` (fallo del calendario → pendiente para
siempre) recibe el mismo tratamiento: se cuenta y se declara, la fila sigue pendiente. Va a
`espera_firma.md` §49 junto al §26.

## Bloque 6 — cuántas filas pasaron por la rama. **Cerrado 00:58.**

`senales.db` en `mode=ro`, segmentado como pidió el pre-mortem: 327 filas con predicción
(8 `legacy_pre_4.6` con `available_at` NULL, esperable; 319 de 4.6.0: 309 verificadas, 8
pendientes, 2 `sin_datos_mercado`). **Filas con `available_at == timestamp_utc`: 0 de 319.**
Filas con `sox_fecha` vacío: 0. **El agujero del bloque 5 es teórico hoy.** Errata de cifra: el
acta §82.2 dice «295 filas»; la máquina da 319 filas 4.6.0 con predicción (309 en
`verificacion_apertura`); el 295 no coincide con ningún conteo actual.

## Bloque 7 — el alcance del §82.1. **Cerrado 01:12.**

`dinero/senal_larga_reporte.nota_dos_contadores(mult)`: el generador emite el aviso con los dos
números computados (3 de `registro_intentos`, 30 de `len(p_holm)`). Reporte regenerado: el diff
del JSON son tres claves nuevas y **ninguna celda se movió**. Ningún cálculo cambió.

## Bloque 8 — el §82.5. **Cerrado 01:16.**

README: línea de la introducción («χ² with Edwards continuity correction; exact binomial 0.0451»)
y la ventana larga («χ² con corrección de continuidad, `GEMELO/control_lineal._mcnemar`; a ese n
la exacta también es ≈ 0»). Ninguna cifra movida; el detector da 0 hallazgos; el `xfail` de
`test_epistemico.py` retirado con su historia. Hipótesis del §82.5: confirmada para el p,
descartada para el decimal del IC (ver bloque 4).

## Bloque 9 — la razón podrida y su guardia. **Cerrado 01:15.**

Razón de `test_epistemico.py::test_ninguna_prediccion_sellada_comparte_sesion_objetivo_con_otra`
reescrita: la regla está firmada y actúa al cargar; el test lee SQL directo y ve los duplicados
físicos, que no se borran porque las filas selladas no se reescriben. El test sigue rojo. Guardia
nuevo `tests/test_razones_xfail.py`: inventario de xfail por AST, registro `RAZONES` con un
predicado ejecutable por xfail (la razón de :572 → «hay duplicados físicos y `cargar()` los quita»;
la de :775 queda como historia), contraprueba y exigencia de fuente citada. Un xfail nuevo sin
predicado pone la suite en rojo.

## Bloque 10 — el mapa operable por presupuesto y modo. **Cerrado 01:26.**

`construir_mapa(cierres, cfg, presupuesto, fraccionarias)`; `acciones_por_monto`,
`comision_usd` y `friccion_ida_y_vuelta` con el modo como argumento. Censo (enteras): 100 USD
**7 de 36**, 250 USD **13**, 500 USD **29** (`MSFT` al borde), 1000 USD **33**; fraccionarias 36
de 36 a cualquier monto con 2 % de ida y vuelta. Tabla por instrumento en
`docs/universo_operable.md`. **Segundo día de censo:** una descarga (01:21), congelada en
`dinero/datos/cierres_congelados_dia2.csv` (sha256 `4222c8ec…`), pero **termina en la misma sesión
(2026-09-04): el 7-sep fue feriado en NYSE**. Precios idénticos (diferencia relativa máxima
< 1e-6; el sha distinto es formato de punto flotante). **No cuenta como segundo día**; el
documento lo declara y el censo sigue siendo de un solo día.

## Bloque 1, re-corrida con las exigencias (01:31 a 01:36, `date`)

- **Brazo de calibración (a posteriori, declarado):** usable a α = 0,05 → **NO** en los tres
  horizontes. Tamaño bilateral 0,086 [0,074, 0,099] a 52 semanas, 0,067 [0,056, 0,078] a 104,
  0,064 [0,054, 0,075] a 156; cobertura del IC de la media 0,914 / 0,933 / 0,936.
- **Cobertura del IC de la desviación (C4): 0,783 [0,765, 0,801] a 52, 0,821 a 104, 0,850
  [0,833, 0,865] a 156.** El intervalo de σ que publica la cuenta v2 no es un 95 %: el punto
  sirve de insumo, el intervalo no. Propagado a `cuenta_papel.md` y al JSON.
- **MDE80:** 1,05 pp/semana a 52 semanas (≈ 55 pp/año), 0,74 a 104, 0,61 a 156.
- Potencia cerrada al α real coincide con la simulada (0,147 / 0,351 / 0,829 contra 0,136 /
  0,344 / 0,790): la brecha era el tamaño inflado.
- ρ medido: AC1 mediana 0,000, banda [−0,190, +0,164]; el barrido a 0,2 cubre el borde.
- σ ancla 2,704 > techo del IC de la σ realizada [1,995, 2,669]: ancla conservadora.

## Dictámenes de cierre (archivados en `GEMELO/resultados/dictamen_11/`)

- **`auditor-lookahead` sobre la reconstrucción (01:45): NO ENCONTRÓ FUGA.** 58 cortes no declarados
  y 12 perturbaciones de valor: invariante. Dos debilidades demostradas: D1, el gate con dos cortes a
  dedo era ciego a una fuga de 1 día por `precios_ref` (2 de 11 cortes la veían, 0 de los declarados);
  D2, el descuento de caja comprometida era código muerto con retardo 1 y con dos convenciones. Diez
  exigencias: **aplicadas en la corrida** G1 (alcance del gate declarado en `verificar_invariancia`
  y en el reporte), G2 (barrido de 25 cortes por regla, una sesión de cada 30; test exige ≥ 20), G4
  (convención única n × precio de decisión; frase del reporte corregida), G5 (sonda larga por
  construcción: 57,8 % de señales positivas, magnitud media +2,20 pp, declarado), G6 (membresía como
  corte transversal fijo: excluye ASML por precio y ARM / SNDK por listado posterior; excluidos
  +296 % contra incluidos +166 % de mediana: el sesgo va en contra), G7 (cortes 2020-12-31 y
  2022-12-30 en `test_senal_larga.py`), G9 (segundo congelado declarado en el reporte), G10 (suite
  final con el árbol quieto, abajo). **Pendientes para la corrida 12:** G3 (contraprueba de la fuga de
  1 día por `precios_ref`: con cortes densos sería un test no determinista y hay que diseñarlo como
  prueba de borde) y G8 (`available_at` por ticker en el `.meta.json` del congelado).
- **`estadistico-adversario` (01:30): SOSTIENE CON EXIGENCIAS en los tres artefactos; global NO
  CONCLUYENTE con un hallazgo firme** (el instrumento discrimina pero no está calibrado; la rama de
  coherencia se apaga bajo R2; la cuenta medía fricción de un sorteo). Las 18 exigencias se aplicaron
  al ejecutable y los artefactos se re-corrieron; **las cifras re-corridas no volvieron a pasar por el
  adversario** (reserva del director, impresa acá).
- **`director-programa` (revisión de alcance, 01:50): nada se revierte en bloque.** Tres
  correcciones aplicadas (nota editorial de la API, mínimo de 1 USD y falta de banda en la vista,
  motivo del segundo congelado) y una contradicción del reporte corregida en el generador. Norma
  nueva instalada de paso, y se anota como tal: **todo `xfail` nuevo exige un predicado ejecutable en
  `tests/test_razones_xfail.py`**. Saldo de gobernanza: seis firmas ejecutadas, cinco nuevas abiertas.
- **`guardian-constitucion` (01:50): OBSERVADO, ningún rechazo.** Cuatro observaciones, las cuatro
  corregidas antes del cierre: suite final en la bitácora, dictamen del auditor presente,
  `cifras_retiradas.md` con los patrones «27 % → 57 %» y «σ 2,54», errata fechada al 295 en el §82.2.
  No verificado por el sandbox: permisos 600 de `.env`.
- **`curador-epistemico`:** ver abajo.
- **`curador-epistemico` (01:56): RECHAZADO, nueve bloqueantes y siete observaciones.** Todas
  corregidas antes del cierre: el dictamen del auditor ya existe y se cita; «sin fuga» pasó a
  «PROPUESTA: INVARIANTE en 25 cortes, el auditor no encontró fuga, que no queden es
  indemostrable» (`estado_epistemico.md`, `ESTADO.md`); la cláusula sin cifra del README
  («la exacta también es ≈ 0») se cortó y dice que no se computó; la tarjeta §46 lleva R2
  pegado; el §43 marca sus cifras v1 como retiradas; «validado» pasó a «puesto a prueba …
  NO calibrado»; la contradicción del §3 de la cuenta se corrigió en el generador; el
  veredicto del bloque 1 lleva la descalibración en la misma línea; `ESTADO.md` con rótulos
  MEDIDO / PROPUESTA, horizonte de la fricción y las 8 legacy; el IC de σ rotulado «nominal
  95 %, cobertura medida 0,850» en la cuenta y en el pre-registro §7 C, con puntero fechado
  en la línea de la σ 2,54; el segundo congelado declarado como comparación trivialmente
  idéntica. Y una palabra prohibida que se coló en la vista («intervalo de confianza») la
  cazó la suite: corregida.

## Cierre (02:07, `date`)

- **Suite al cerrar, con el árbol quieto: 802 passed, 1 xfailed en 377,41 s (02:00 a 02:06);
  `tests/test_motor.py` OK.** +48 tests respecto de la apertura (7 del simulador del
  instrumento, 6 del parche del guardia, 4 del guardia de razones de xfail, 5 de la sección 6
  de `test_dinero.py` con los tres xfail estrictos retirados, más las variantes agregadas).
  Inventario de xfail esperado al cierre: **1** (`test_epistemico.py::…comparte_sesion_objetivo…`,
  con razón vigente y predicado registrado). Verde = sin fallos no declarados: se cumple.
- Ventana de sellado: no se cruzó (00:43 a 02:07, martes).
- Registro de intentos: gap asiático **352 / 358, sin cambio**; riel largo **3, sin cambio**.
  Ningún bloque evaluó una hipótesis nueva sobre datos reales: el bloque 1 es simulación con
  verdad conocida (0), el bloque 4 es el intervalo de una cifra ya declarada (0; cablearla
  sería 1), la cuenta mide fricción de una señal sin información (0). Los dos registros
  quedan separados (§82.6).
- Árbol: 28 archivos modificados y 16 nuevos, **sin commit** (la orden fue no pushear; el
  commit lo decide Nicolás a la mañana con los dictámenes a la vista). `senales.db` intacta
  (mtime 7-sep 18:15). Archivos protegidos idénticos a HEAD por sha256 (guardián).
- **Pendiente para la corrida 12:** G3 (contraprueba de la fuga de 1 día por `precios_ref`,
  como prueba de borde), G8 (`available_at` por ticker en el `.meta.json`), re-dictamen del
  adversario sobre las cifras re-corridas, y la primera fila prospectiva del riel, que espera
  al parche del §26 con su guardia. **No iniciado:** nada del encargo.
- Firmas nuevas abiertas: §46 a §50. Firmas ejecutadas: las seis del §82.
