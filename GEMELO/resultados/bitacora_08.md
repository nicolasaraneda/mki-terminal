# Bitácora 08 — octava corrida autónoma, 2-sep-2026

Continuación de `bitacora_07.md`. Una línea por hito, **con hora local
(Chile, UTC−4) leída de `date` en cada hito** (la séptima corrida estimó
horas y tuvo que corregirlas con errata: acá no se estima ninguna).

## Lo que gobierna esta corrida

Encargo: `encargo_corrida_08.md` (subido por Nicolás). De track record a
teoría, y el instrumento calibrado contra un patrón conocido. Protocolo por
frente empírico: pre-registro antes de mirar (`GEMELO/preregistro/`),
partición de años congelada, `auditor-lookahead` antes de abrir años de
prueba, `estadistico-adversario` antes de que una cifra entre a la
bitácora, `guardian-constitucion` sobre el diff de cada frente, corrección
al ejecutable primero. Todo lo nuevo es PROPUESTA. Cada hipótesis probada
suma un intento al registro, descartada o no.

Límites: motor, senales, snapshot, universo, modo de emisión, `.env`,
timers intocables; filas selladas jamás reescritas; ninguna cifra publicada
se mueve sola (doce bloques); ningún estimador sin intervalo computado;
nada pesado ni descargas entre 17:50 y 20:30; nada pusheado.

Y la cláusula del encargo que vale más que las otras: **si una instrucción
del encargo es ella misma el defecto, no se ejecuta; se anota con la razón
y se sigue.**

## Hitos

- **11:31** — Arranque. `HEAD=7bab569` (los cuatro commits de la séptima),
  árbol limpio. Suite completa corriendo en segundo plano; `orientador`
  despachado con el orden de lectura del §0.
- **11:31** — **Errata del encargo, anotada como manda el §0.2:** dice «el
  conteo de intentos del DSR (hoy en 86 según las actas)». **La máquina
  dice 100** (`GEMELO/relevo_asiatico.N_INTENTOS_ACUMULADO`, 23 tramos) y
  el veredicto 5.1 declara 106 (`backtest/veredicto_51.N_INTENTOS_51`).
  El 86 fue el registro del 1-sep al mediodía (acta §67); subió a 91 esa
  tarde y a 100 anoche (acta §72). Manda la máquina: esta corrida parte
  de **100** y cada hipótesis que pruebe suma desde ahí.
- **11:36** — Suite completa antes de empezar: **557 passed, 2 xfailed**,
  exit 0; `mtime` de las bases intactos. El `orientador` entregó la
  reconstrucción; dos cosas que cambian el encargo: (a) las «ocho
  decisiones de análisis» son **siete ejes vivos** (192 celdas) más la
  deduplicación, retirada como eje el 1-sep al firmarse la regla
  (`bifurcaciones.py:122-234`); (b) **el «round trip de 8,79 ms» del
  encargo NO es una medición de la FPGA**: es un `connect()` TCP p50 contra
  1.1.1.1:443 (`GEMELO/MICRO/piso_de_latencia.md:33-42`). Va al H2 con esa
  procedencia y no fusionado con las cifras RTL. Y una errata mía de anoche
  que el orientador cazó: `espera_firma.md:874` decía potencia 0,34 [0,31,
  0,37] (1.000 simulaciones) donde su expediente dice 0,36 [0,34, 0,37];
  corregida en su sitio con errata fechada (el archivo está commiteado).
- **11:37** — **Frente A.** Pre-registro escrito antes de correr nada
  (`GEMELO/preregistro/frente_A.md`). Simulador `GEMELO/simulador/proceso.py`:
  gap = μ_i + β_i(b·S_d + c·U_d) + σ_i·ε, todo t de Student ν=4; β, μ, σ
  total, tamaños de clúster y escala del SOX leídos del sello (ancla
  31-ago, n=246, 35 días); la escala idiosincrática se deriva de la
  varianza total menos la común (piso 30%); b se calibra por bisección
  para el δ pedido y c para el ICC. Calibración lograda: δ=0 → b=0,56,
  c=5,5, ICC 0,416 (real 0,39), SE de día a 35 fechas 8,2 pp (real 8,55),
  tasa base 0,577 (real 0,577), llamados a la baja 0,51 (real 0,49). La
  «verdad» de cada generador se mide a 200.000 días, no se supone igual al
  objetivo (el generador nulo da δ = 0,006).
- **11:43** — **Frente A, resultados** (`calibracion_instrumento.md`, 4
  generadores con verdad medida a 200.000 días; ICC sim 0,40–0,41 contra
  0,39 real). **A1:** el IC95 de clúster de día cubre **0,938 [0,927,
  0,948]** bajo δ=0 y **0,927 [0,915, 0,938]** bajo 9 pp — 1 a 2,3 pp por
  debajo del nominal, con IC que lo excluye: por mi propio pre-registro
  (> 2 pp) es un defecto del instrumento y va al ejecutable como
  propuesta; el IC iid de filas cubre **0,69**: inservible. **A2:** bajo
  δ=0 las 192 celdas cruzan α 10,6 veces en promedio (5,5% por celda:
  tamaño correcto), pero la mediana es **0** y el percentil 95 es 73: las
  celdas están tan correlacionadas que el «0 de 192» observado en la
  ventana real es exactamente lo que la nula produce la mitad de las
  veces. P(al menos una) = 0,25 [0,21, 0,31]. **A4:** la potencia del
  simulador reproduce la de `horizonte.md` dentro de los intervalos en las
  12 celdas comparables (9 pp a 250 días: 0,78 [0,74, 0,81] contra 0,82
  [0,81, 0,83]; la diferencia mayor es 5 pp a 250 días, IC solapados).
- **11:54** — **A3, y es el hallazgo del frente: el DSR bajo la nula pasa
  el 0,95 en el 26–29% de las réplicas con N = 100/106**, no en el 5%.
  Causa, verificada en el código y por simulación: `backtest/veredicto_51.py`
  (líneas 365 y 385–395) calcula el Sharpe **anualizado**
  (`inferencia.sharpe(s, anualizar=252)`) y lo pasa a `inferencia.psr` y
  `dsr` con n = días, cuya `var_sharpe` es **por período** (lo dice su
  propio docstring, `inferencia.py:162-165`): el z queda inflado por √252.
  Con el Sharpe por período la tasa cae a 0,001–0,002. `GEMELO/control_lineal.py:405-408`
  hace lo mismo con `sharpe_ls_sin_costos`. **La «saturación de PSR/DSR en
  1,0000 a 30 días» que el proyecto atribuyó a anualizar sobre pocos días
  (`MINIMO_DIAS_SHARPE = 60`) era este defecto de unidades.** Ningún
  veredicto sellado se da vuelta (los Sharpes del 5.1 son negativos, DSR
  0 de todas formas), pero el criterio V5 estaba mal calibrado hacia
  arriba. Es errata y va al ejecutable, con test; los artefactos sellados
  no se reescriben.
- **11:53** — **Frente D, ventana sellada y años de ajuste** (prueba NO
  abierta; `auditor-lookahead` despachado sobre `GEMELO/transversal.py`):
  sellada ρ̄ = 0,229 [0,034, 0,418], p permutación 0,0007, 35 fechas — no
  contiene el cero pero no alcanza el 0,20 relevante con el IC; ajuste
  2018–2023 ρ̄ = **0,260 [0,234, 0,284]**, p = 0,0002, 1.334 fechas, τ̄ 0,205:
  relevante. El orden de β sí tiene información transversal en el ajuste.
- **11:57** — **Corrección al ejecutable, antes que a cualquier texto** (regla
  2): `backtest/veredicto_51.py` y `GEMELO/control_lineal.py` pasan ahora el
  Sharpe por período a `psr`/`dsr`, con V y sr0 en la misma unidad, y
  siguen reportando el anualizado; `tests/test_unidades_sharpe.py` fija
  la propiedad (DSR por período ≤ 5% bajo la nula), la contraprueba (el
  anualizado ≥ 15%) y, por AST, que ningún llamador vuelva a pasar el
  anualizado. 36 tests vecinos verdes. Los artefactos sellados del 5.1 y
  del WS2b **no se reescriben**: llevan errata. `estadistico-adversario`
  despachado sobre el Frente A entero con la instrucción del encargo:
  buscar cómo el simulador podría estar construido para darle la razón al
  proyecto. Frente E (`potencia_por_metrica.py`) corriendo en segundo
  plano con el generador de 9 pp.
- **12:09** — **Frente E, resultados** (`potencia_por_metrica.md`; generador
  de 9 pp del simulador, cuya razón MAE modelo/cero 2,67/3,15 = 0,85
  reproduce la real del ancla 2,49/2,93 = 0,85 sin haberla calibrado): con
  clúster de día y el mismo test, **la magnitud (MAE contra predecir cero)
  tiene potencia 0,59 a 35 días y 0,90 a 73**, contra 0,18 y 0,31 de la
  dirección; el CRPS con la σ del intervalo sellado 0,43 y 0,76 (0,83 con
  σ calibrada). Sobre la ventana sellada, z observado: dirección 1,1, MAE
  1,7, CRPS 1,8; días para 0,80 al efecto observado (cota optimista): 229,
  95, 87. **La magnitud alcanza el 80% en ~60 días; la dirección en ~250.
  El 25-oct la dirección tendrá 0,36 y la magnitud ~0,90 de potencia.**
  Va a la frase de potencia en dos versiones (§4 del encargo) y al
  adversario.
- **12:11** — **Frente D: el `auditor-lookahead` RECHAZÓ la fila del
  ajuste** (β estimada con todo el ajuste y evaluada sobre el mismo ajuste:
  in-sample; falla la prueba maestra) y señaló que la ventana sellada está
  anidada en la prueba, que el caché de gaps no tenía testigo, que faltaba
  embargo y que `excluir_cero` no estaba declarado para la larga. Verificó
  limpio el apareo `merge_asof`, la definición de los gaps, la disyunción
  de las β y la sellada. Aplicado todo antes de abrir la prueba (enmienda
  fechada en `frente_D.md`): β causal expansiva con burn-in 250
  (`betas_causales`), embargo 5 sesiones, las 37 fechas selladas fuera de
  la prueba, gaps desde el testigo preservado (sha256 3908fdd58a71119b),
  `tests/test_transversal.py` (5, con contraprueba). Ajuste causal: ρ̄
  0,257 [0,228, 0,285]. **Prueba abierta a las 12:11: ρ̄ = 0,237 [0,201,
  0,273], p = 0,0002, 626 fechas, τ̄ 0,187 [0,158, 0,215]: relevante fuera
  de muestra.** El orden de las β tiene información transversal y el
  efecto día no la explica. Pendiente de dictamen.
- **12:12** — **Frente B1, años de ajuste** (`decaimiento_feriados.md`, sin
  motor, calendarios de `exchange_calendars`): **C1 (NY cerrada) confirma la
  caída con el tiempo en Tokio: +22,2 pp normal → −2,3 pp con el cierre
  viejo, diferencia −24,6 [−41,6, −7,9], p = 0,002**; Taipéi −18,1 [−37,3,
  +1,8]; Seúl y Fráncfort no distinguen. **C2/C3 (Fráncfort con un
  intermediario asiático menos): −2,2 [−19, +15] y −0,05 [−14,5, +14,4]:
  contienen el 0 y los 5 pp — con estos datos NO se separa disipación de
  absorción**, y hay que decirlo así: la ventaja normal de Fráncfort es de
  3,5 pp y el IC del contraste mide ±13. El contraste de feriado local
  (n_ny ≥ 2) quedó casi vacío (4 fechas en Tokio en 5 años): sospechoso,
  lo diagnostico antes de abrir la prueba.
- **12:14** — **Defecto de datos en la ventana larga, encontrado por el
  contraste que salió vacío:** `GEMELO/datos.descargar_gaps` hacía
  `shift(1)` sobre el índice unión de los 8 mercados; en un feriado local
  el cierre es NaN y la sesión siguiente se perdía con `dropna`. **El caché
  de gaps de la ventana larga no contenía ninguna sesión posterior a un
  feriado local** (Tokio: 4 contra 54 que da el calendario). Corregido en
  el ejecutable (`gaps_desde_ohlc` sobre el índice propio del ticker,
  `tests/test_gaps_feriados.py` con contraprueba), gaps regenerados con
  descarga fresca sin tocar el caché: **+670 filas (4,5%), 0 filas viejas
  distintas** (max |dif| 9e-5). Preservado como
  `testigos_fuente/gaps_v2_propio_indice.csv.gz` (sha256 34fe61082ea58282).
  **Consecuencia declarada, no ejecutada:** las cifras publicadas de la
  ventana larga (n = 14.618) se calcularon sin esas sesiones; recomputarlas
  mueve los doce bloques y lleva firma. El verificador de producción no
  tiene el defecto (descarga cada ticker solo). Enmiendas fechadas en los
  pre-registros de B y D.
- **12:14** — Re-corridas sobre el v2. **Frente D:** ajuste causal ρ̄ 0,248,
  prueba **0,240 [0,20, 0,27]** (637 fechas): estable. *(Errata 14:40: ese intervalo era el de la corrida v1 de 626 fechas; el de v2 es [0,206, 0,276] — dictamen D.)* **Frente B1** (ajuste,
  1.381 fechas): C1 Tokio −23,4 [−40,0, −6,7], p = 0,006 (un cierre de NY
  de 26 h vale nada en Tokio); C2/C3 siguen sin distinguir (−2,5 [−19,6,
  +15,1]; −0,4 [−15,1, +14,3]; los dos contienen el cero). **Y el contraste de feriado local, ahora
  poblado (Tokio 65, Seúl 48, Taipéi 40 fechas), dice algo que las dos
  hipótesis del pre-registro no habían formulado:** tras un feriado
  local, el ÚLTIMO cierre de NY predice igual que en un día normal (Tokio
  +23,9 vs +22,2, diferencia +1,6 [−11,3, +14,4], contiene el cero) **y el cierre ANTERIOR —de
  48 h, que en C1 valía cero— sigue prediciendo: Seúl +21,8 [+7,4, +36,0],
  p = 0,021; Tokio +14,1 [−1,6, +29,9] y Taipéi +13,2 [−5,2, +31,2], estos dos con IC que contiene el cero**. La
  información de NY no se disipa con el reloj: se disipa cuando el propio
  mercado local abre y la incorpora. Lectura post-hoc, etiquetada como
  tal; el contraste sí estaba pre-registrado. `auditor-lookahead`
  despachado sobre B1 antes de abrir la prueba.
- **12:17** — **Frente C, años de ajuste** (`no_capturabilidad.md`, sin
  motor, 10.381 filas, 1.381 fechas; pre-registro escrito a las 12:16):
  **H1 estructural, confirmada:** el backtest opera la sesión (entrada en
  la apertura, salida al cierre — `backtest/cartera.py:1-42`, verificado),
  no el gap; sobre la ventana larga el signo del SOX acierta el gap con
  ventaja **+17,3 pp [15,0, 19,7]** y la sesión con **−1,8 pp [−3,8, +0,2]**
  (contiene el cero); la cartera direccional sobre la sesión rinde
  **−0,095 pp/día [−0,15, −0,04]** y rendiría +0,73 pp/día [0,68, 0,78] si
  el gap fuera operable. **H2 (asimetría de magnitud): NO se sostiene** —
  razón |E[q|error]|/E[q|acierto] = 0,43 [0,03, 1,40]; y el dato que
  importa: **cuando el gap se acierta, la sesión va en contra** (q|acierto
  = −0,11 pp [−0,18, −0,05]). **H3: sobrerreacción**, pendiente de la sesión
  sobre el gap **−0,082 [−0,127, −0,037]** (el 8% del gap se revierte
  durante la sesión); sobre la sorpresa gap − β·SOX, −0,04 [−0,11, +0,03]
  (contiene el cero). El umbral pre-registrado de relevancia (|pendiente|
  ≥ 0,1) queda dentro del IC: acotado, no establecido. **Frase, con la
  del encargo: el gap es estructuralmente intradeable, y la sesión
  posterior revierte una parte de él.** Prueba no abierta;
  `auditor-lookahead` despachado.
- **12:18** — **Frente F** (`secuencial_v5.py`, pre-registro
  `preregistro/secuencial_v5.md` escrito a las 12:17 con la función de
  gasto fijada — Lan-DeMets O'Brien-Fleming, miradas a 50/100/150/200/250
  fechas selladas, varianza re-estimada por mirada, fronteras derivadas
  por simulación bajo H0 con el generador calibrado) corriendo en segundo
  plano: tipo I total y por mirada, sensibilidad a φ, potencia a 9/6,5/5
  pp, n esperado.
- **12:21** — **Frente B2, predicción fuera de muestra.** Curva ajustada
  sobre los cuatro exchanges actuales en los años de ajuste (sin motor):
  Δ(h) = a·exp(−h/τ), a = 28,1 pp [22,9, 36,9], τ = 4,65 h [2,87, 7,57];
  predicciones **escritas en el pre-registro a las 12:21 antes de
  descargar** (`decaimiento_prediccion.py --ajustar`), descarga y medición
  después (`--medir`, yfinance directo, sin caché): **1 de 3 predicciones
  cae dentro del intervalo.** Ámsterdam (ASML.AS, BESI.AS; h = 8,75, el
  mismo margen que Fráncfort): predicho 4,3 [1,7, 7,5], **medido 6,5 [3,3,
  9,8] en ajuste y 4,4 [−0,2, 9,0] en prueba (este último contiene el cero) — dentro**: la ventaja baja de
  Fráncfort es del margen, no del exchange. Hong Kong (0981.HK, 1347.HK;
  h = 3,25): predicho 14,0 [11,4, 16,0], **medido 4,1 [1,0, 7,4] / 3,1
  [−1,5, 7,9] (el de prueba contiene el cero) — fuera, muy por debajo**. India (MOSCHIP.NS, TATAELXSI.NS;
  h = 5,5): predicho 8,6 [5,3, 11,6], **medido −12,7 [−16,3, −9,1] / −9,0
  [−13,5, −4,8] — refutado con signo contrario**. Sídney: sin ticker de
  semiconductores, no se mide (declarado). **Lectura, con la misma firmeza
  que un acierto: la curva Δ(h) NO es una ley del margen temporal: vale
  dentro de la clase de exposición al SOX del universo actual (ASML/BESI
  la cumplen), y falla donde el ticker no está atado al SOX (fundiciones
  chinas, small caps indias con deriva alcista dominante).** El decaimiento
  con h y la exposición al insumo son dos factores, y el modelo de un
  factor los confunde. Pendiente de dictamen.
- **12:22** — **Frente F, resultados** (`secuencial_v5.md`; pre-registro con
  la función de gasto fijada antes): fronteras derivadas por simulación
  bajo H0 con el generador calibrado (20.000 réplicas): c = [∞, 3,15, 2,57,
  2,27, 2,06] a 50/100/150/200/250 fechas. **Tipo I total 0,050 [0,047,
  0,053] a φ = 0 (por construcción) y 0,060 / 0,060 / 0,056 a φ = 0,1 / 0,2
  / 0,3**: la varianza re-estimada por mirada sobre contribuciones diarias
  absorbe la autocorrelación mucho mejor que el plan anterior (banda
  [0,046, 0,079]). Potencia a 9 pp: **0,79 [0,78, 0,80]**, n esperado 197
  fechas; a 6,5 pp 0,50; a 5 pp 0,33 (con 250 fechas de tope: «no medible a
  este horizonte» es un desenlace posible y declarado). El plan va al
  adversario con la instrucción de leer los cuatro rechazos.
- **12:24** — **Frente B1: auditoría sin fuga (núcleo verificado contra
  timestamps reales, truncado en tres niveles, dos contrapruebas) y tres
  bloqueos aplicados antes de abrir la prueba** (enmienda 2): filas con
  insumo rancio por la añada del `^SOX` excluidas por regla (0 en ajuste, 8
  en prueba); C2/C3 disjuntas y como estaban pre-registradas; intentos
  declarados 17 (15 de B1 + 2 de B2), no 5; dos controles del auditor
  agregados a C1 (normales sin lunes; |SOX| emparejado) y dos sospechas
  reportadas (h del lunes ≈ 52 h; los cuatro C1 comparten 40 fechas: son
  un solo experimento). **Prueba abierta 12:24 (692 fechas):** C1 Tokio
  **−16,8 [−33,6, −0,7]** (replica la dirección); **con el control de
  volatilidad −8,9 [−25,1, +7,5]** — los feriados de NY caen en tramos
  quietos y eso explica cerca de la mitad de la caída, en ajuste también
  (−23,4 → −16,8 [−33,4, +0,1]). C2/C3: −10,3 [−32, +13] y +14,6 [−5,6,
  +33,8]: **no distinguen, en ajuste ni en prueba.** Y la lectura post-hoc
  del ajuste (el cierre viejo sigue prediciendo tras un feriado local)
  **no replica**: Seúl +6,4 [−17,3, +29,9], Tokio +3,1 [−14,7, +20,3]. Se
  publica como no replicado.

### 12:30 · Frente G: reglas de la casa ejecutables (verde, 5 tests)

- `cifras.py` (raíz): árbitro. `sellada()` COMPUTA la ventana sellada desde
  `senales.db` (mode=ro) vía `backtest.linea_base` en `CORTE_README =
  2026-08-28` — el instante en que el README publicó n = 248. Hallazgo al
  escribir el test: `CORTE_SECCION_2` (24-ago) da n = 223, +4,0 pp, p 0,4633 —
  el README no está en ese ancla sino en el 28-ago. Tres instantes pinchados,
  tres nombres (24-ago §2.8, 28-ago README, 31-ago regla firmada). La ventana
  larga queda CONGELADA (`Larga`) con procedencia y la advertencia del caché v1.
- `doce_bloques()` devuelve los doce fragmentos textuales que dependen de n
  (9 README, 2 skill, 1 estado_epistemico). `tests/test_cifras_arbitro.py`:
  el árbitro reproduce 248 / +6,5 / 0,1849 / 2,98 / 90,3; los doce fragmentos
  están en su archivo; n+1 mueve los doce; ninguna cifra retirada reaparece en
  un documento publicado; contraprueba (el detector caza «8,6% de contaminación»).
- `GEMELO/cifras_retiradas.md`: 12 patrones legibles por máquina (regex) con
  contexto, fecha, acta y reemplazo. Defecto corregido en el acto: la tabla
  markdown parte en `|` y los patrones tienen alternancia `a|b` → el parser
  parte en ` | ` (pipe con espacios). Falso positivo corregido: el README
  cita el 91,4% en la línea 151 y dice «Es falsa» en la 152 → marcas de
  retiro ampliadas («es falsa», «falso», «desmont»).
- Hook: `guardia-reglas.py` se protege a sí mismo y a settings.json (sólo
  Nicolás los edita), así que la extensión vive en
  `GEMELO/propuestas/guardia-cifras-retiradas.py` NO instalada, con la
  instrucción de instalación (segundo comando en el mismo matcher: se
  extiende, no se reemplaza). Cláusula final del encargo aplicada: la
  instrucción «el hook se extiende» choca con el hook que lo prohíbe; no se
  ejecuta, se anota.

### 14:18 · Dos dictámenes, aplicados al ejecutable primero

- **Auditoría de fuga del Frente C** (con el ajuste abierto, la prueba
  cerrada): dos fugas demostradas —β in-sample en la sorpresa del ajuste
  (Δ pendiente 0,0005 contra umbral 0,10; no llega a la prueba) y **las 7
  filas del 26-ago construidas sobre una barra INTRADÍA** (testigo capturado
  a las 04:23 UTC con Asia en sesión)— y siete sospechas: `SELLADA` a mano se
  quedó dos sesiones corta (las sesiones objetivo llegan al 2-sep), sin
  embargo en el borde de la ventana sellada, terciles con cuantiles de la
  ventana analizada, sin candado de una sola apertura, bootstrap iid con
  |q| autocorrelado, H2 con el signo perdido (los aciertos TAMBIÉN pierden),
  14 intervalos publicados contra 3 intentos declarados. **Todo aplicado**
  (`frente_C.md` Enmienda 1; `tests/test_no_capturabilidad.py`, 8 tests con
  la prueba maestra de truncar y su contraprueba) y recién entonces
  **`--abrir-prueba` (14:15)**, candado escrito con sha256 del módulo y del
  pre-registro. Intentos de C: **14** (por estadístico publicado).
- **Frente C, PRUEBA (4.810 filas, 643 fechas, 2024-01-08 → 5 sesiones antes
  de la primera sesión sellada):** H1 replica —ventaja del gap +15,6 [12,3,
  18,9] pp, de la sesión **−3,0 [−5,7, −0,3]**, cartera direccional **−0,12
  [−0,22, −0,04] pp/día** con el gap «operable» valiendo +1,02 [0,85, 1,21]—.
  H2: el criterio NO APLICA en las dos ventanas (q|acierto −0,14, q|error
  −0,08: los aciertos pierden más que los errores; razón 0,60 [0,04, 2,08],
  contiene el 1). H3: pendiente sesión~sorpresa −0,036 [−0,096, +0,021]
  (contiene el cero); sesión~gap −0,052 [−0,096, −0,007], reversión que
  replica pero por debajo del 0,1 relevante; los tres terciles contienen el
  cero. Por exchange: Seúl es donde el acierto de la sesión más cae por debajo
  de «siempre al alza» (−6,7 [−11,4, −2,3] pp de acierto, no de pérdida;
  su pérdida es −0,20 pp/día); Fráncfort acierta el gap +6,2 [1,4, 11,0] y no captura nada.
  **Lo que C sostiene: la no capturabilidad es ESTRUCTURAL (H1) y replica
  fuera de muestra; no es asimetría de magnitud (H2 no aplica) ni
  sobrerreacción medible (H3 contiene el cero).**
- **Dictamen del adversario sobre el Frente A: NO SOSTIENE tal como estaba
  escrito**, con ocho bloqueos. Los que tocan código, hechos: (a)
  `_bootstrap_dia` con `semilla` inyectable (todas las réplicas de A1
  compartían UNA matriz `idx`); (b) `_ic_t_cluster` —t de clúster
  linealizada, gl = k−1— y `_t_ppf` sin scipy (t_{34;0,975} = 2,0322);
  (c) `calibracion.py` v2: A1 con cuatro estimadores y 10.000 réplicas,
  verdad medida 8 veces con intervalo, A2 bajo nula Y alternativa con
  P(0 de 192) y cociente de verosimilitudes, A3 en las dos unidades con
  tamaño teórico gaussiano y sensibilidad a V, A4 con comparación pareada
  (McNemar exacto) y tercera ruta cerrada, A5 sensibilidad a ν, c y AR(1)
  entre días (`Parametros.rho`); (d) el productor entrega el Sharpe por
  período (`inferencia.sharpe(…, anualizar=1)`, `PERIODOS_POR_ANIO`,
  `anualizar_sharpe`): fuera los tres `1/√252` a mano; (e)
  `tests/test_unidades_sharpe.py` recorre el repo con LISTA BLANCA y exige
  ≤ 0,01 a 1.000 réplicas; (f) erratas fechadas en `control_lineal.md`,
  `ventana_larga.md`, `experimento.py` y el `resumen.md` del 5.1: la
  «saturación en 1,0000» era el defecto de unidades; con la unidad
  correcta C1 0,9605, C3 0,9638, campeón 0,9565 (N = 9) **cruzan 0,95**, y
  lo único que los separa de «V5 superado» es `MINIMO_DIAS_SHARPE = 60`,
  cuyo origen post-hoc y justificación nueva quedan escritos en el propio
  comentario; los veredictos del 5.1 sobreviven **porque los Sharpes son
  negativos, no porque el cálculo estuviera bien**; (g) `evaluacion.py` de
  la skill decía 1,77 donde el README dice 1,84×. La v2 corre; el informe
  se reescribe con sus cifras y la declaración de que A1 cumplió su
  criterio congelado de refutación para el estimador percentil.

### 14:19 · Frentes H e I escritos como propuestas; adversarios B, C, D, E+F despachados

- `GEMELO/propuestas/H1_sello_verificable.md` (dos mecanismos: anclaje
  externo del resumen —OpenTimestamps / RFC 3161— y copia de insumos con
  costo MEDIDO 9/53 MB/año; lo que no arregla; qué espera firma),
  `H2_preregistro_fpga.md` (una pregunta, vectores congelados por sha256,
  cota de error que exige una segunda familia de método, CUATRO criterios
  de muerte; el 8,79 ms va con su procedencia TCP), `I_enmienda_V1.md`
  (V1-bis que se AGREGA con fecha, sólo endurece, no reinterpreta; la
  alternativa si no se endurece). Índice en `cola_decisiones.md` §23–25 y
  `espera_firma.md` §22–23 (§22 es la frase de potencia en dos versiones).
- Cuatro `estadistico-adversario` en paralelo sobre B, C, D y E+F (F con
  la instrucción de leer las cuatro objeciones anteriores antes de juzgar).
  Sus dictámenes van a `GEMELO/resultados/dictamen_08/`.

### 14:50 · Dictámenes E y F; erratas de la bitácora de esta misma corrida

- **E: NO CONCLUYENTE** sobre las cifras operativas (el mecanismo —la
  dirección tira información, la magnitud rinde más por día sellado— se
  sostiene). Erratas a lo escrito arriba en las 12:09: donde dice que el
  25-oct la dirección tendrá **0,36**, ese número es de `horizonte.md`
  (optimista, dictamen A); con el simulador es **0,31 [0,27, 0,35]**. Los
  «~60 días» y «~250» que escribí no existen en ningún artefacto: el
  artefacto dice 95 y 229 (y ahora, con intervalo, [20, ∞) y [28, ∞)).
  Aplicado al ejecutable: `potencia_por_metrica.py` v2 (z por t de clúster,
  días con intervalo, días al +6,45 pp publicado, R2 sobre las tres
  métricas, banda generador/observado/R2 de la potencia a 73 días,
  constante μ, familia CRPS-MAE, intentos 2). `espera_firma.md` §22 con
  errata; la etiqueta «V4 / V2» retirada.
- **F: NO SOSTIENE — quinto rechazo.** Retracto la frase de las 12:17: «la
  varianza re-estimada por mirada absorbe la autocorrelación mucho mejor
  que el plan anterior (banda [0,046, 0,079])». Falsa por partida doble: el
  eje φ nunca llegó a las contribuciones (AC1 realizado ≈ 0) y la banda
  firmada se midió con otro plan. **La banda queda intacta.** El «tipo I
  0,050 [0,047, 0,053]» era el ajuste, no una medición. Aplicado:
  `secuencial_v5.py` v2 (α fuera de muestra con semillas independientes,
  control φ = 0 con AC1 realizado, referencia externa de Armitage, mirada 1
  declarada, estadístico declarado nuevo, intentos 2, frase de conclusión).
  Va a `cola_decisiones.md` §27, no a firma. Lo publicable: **19 de 35
  fechas selladas contribuyen exactamente cero** al estadístico direccional.
- **La contradicción que los dos dictámenes destapan y no es de E ni de F:**
  el README publica +6,45 pp (rama SIN deduplicar); la regla de dedup
  firmada el 1-sep da +9,66 pp sobre la misma ventana; y hay una tercera
  rama (+14,3 pp) en `cola_decisiones.md` §2a-ter. Toda cifra que dependa
  del tamaño del efecto (días para 0,80, MDE, n esperado) está indeterminada
  por un factor ~5 hasta que Nicolás decida la rama. Es más urgente que E y F.

### 14:45 · Frente A v2 y Frente C v2, con sus cifras

- **A v2** (`calibracion_instrumento.md`, 10.000 réplicas, semilla por
  réplica, verdad medida 8 veces con IC): A1 percentil **0,931 [0,926, 0,936]
  / 0,933**, básico 0,932 / 0,933, **t de clúster 0,949 [0,945, 0,953] /
  0,951**, iid de filas 0,689. El criterio congelado de refutación
  («< 93% con IC que excluya 95%») **NO se cumple literalmente en esta
  semilla** (0,931 y 0,933 quedan sobre 0,93 por 0,1–0,3 pp, el IC sí excluye
  0,95) y **sí se cumplía en la medición del adversario (0,927)**: un criterio
  que decide al tercer decimal según la semilla es un criterio en el filo, y
  se publica así, computado, no afirmado. Lo que no depende de la semilla:
  el percentil sub-cubre y la t de clúster corrige; el método del IC queda
  como grado de libertad declarado en `bifurcaciones.NO_EJES`. A2: P(0 de
  192) = **0,747 [0,695, 0,793]** bajo la nula, 0,63 a 6,3 pp, **0,465 a 9 pp**:
  cociente de verosimilitudes **1,6** («la mitad de las veces» de la v1 era
  falsa). A3: por período **0,0005–0,0013** contra el teórico gaussiano
  0,0016 (N = 106); el defecto anualizado 0,23–0,39; a N = 9 la elección de
  V mueve el tamaño de 0,0005 a 0,016. A4: **simulador por debajo en 12 de
  12 celdas**, McNemar exacto p = 0,0005, horizonte − simulador **+2,67 pp
  [1,84, 3,55]**: `horizonte.md` es optimista. A5: ν indiferente (percentil
  0,925–0,929 en ν = 4…30); c × 0,5 / 1,5 → ICC 0,14 / 0,59, cobertura
  estable; **AR(1) entre días: ρ = 0,2 → tamaño de la permutación 0,061
  [0,053, 0,070], ρ = 0,4 → 0,104**: riesgo declarado, no resuelto. El piso
  del 30% ata en 2330.TW y 4063.T (sd simulada +10% / +23%).
- **C v2** (`no_capturabilidad.md`, con `excluir_cero` en los dos lados y
  candado enmendado con rastro): PRUEBA 4.715 filas, 643 fechas. H1 replica:
  ventaja del gap **+15,6 [12,3, 18,9]** (McNemar b 1369, c 634), sesión
  **−2,7 [−5,5, −0,02]**, cartera **−0,114 [−0,208, −0,026] pp/día**; H2
  REFUTADA en su premisa (q|acierto −0,12, q|error −0,10; diferencia −0,02
  [−0,15, +0,13], contiene el cero; razón 0,85 [0,05, 3,5] contiene 1 y
  1,5); H3: sorpresa −0,03 [−0,09, +0,03] (contiene el cero), gap −0,047
  [−0,091, −0,0004], **todo el IC bajo 0,1 en la prueba** pero confundido con
  error de medición; terciles alto − bajo +0,01 [−0,14, +0,17]. **Costos: la
  contraria rinde +0,114 [0,03, 0,20] pp/día bruto, punto muerto 5,7 pb por
  lado, a 25 pb −0,39; DSR de la contraria 0,41 con N = 100.** Robustez:
  sin ningún año ni ningún ticker el IC de q cruza el cero; por ticker sólo
  3 de 8 excluyen el cero. **Intentos de C contados por máquina: 107
  intervalos publicados** (el 14 se retira). Lo que C sostiene: «el signo del
  SOX no compra nada en la sesión asiática, ni al derecho ni al revés, y eso
  replica fuera de muestra» — *consistente con* estructural, no «es».

### 14:57 · B, D y F re-corridos con sus dictámenes aplicados; el registro de intentos absorbe la corrida

- **D v3** (`transversal.md`): nula de etiquetas de β como principal —ρ̄
  0,2403 [0,206, 0,276], nula sd 0,100, **p = 0,005**, 1,9 % de los órdenes
  aleatorios sobre 0,20—; identidad ρ_d = sign(S)·spearman(orden β, gap)
  verificada exacta (el «modelo transversal» es 8 números y un bit por
  día); simétrico en el signo del SOX (0,242 / 0,239); **el orden del CAMPEÓN
  da 0,180 [0,146, 0,213], bajo la vara 0,20** (proxy − campeón +0,061
  [0,025, 0,096]; Spearman entre los dos vectores de β 0,45); **R2 sobre la
  sellada: 0,190, t de clúster [−0,039, +0,419], cruza el cero**; sellada
  con t de clúster [0,025, 0,434] y p 0,0007 / 0,022 según la SE; doble
  apertura declarada; universo de 2026 aplicado a 2018 declarado. Errata
  en la Enmienda 1 (1.334 → 1.071 fechas). Título honesto: **un orden de β
  sin el motor ordena dentro del día; el del campeón no alcanza la vara**.
- **F v2** (`secuencial_v5.md`): la fila «tipo I 0,050» rotulada AJUSTE (no
  medición); **α fuera de muestra 0,0495 [0,047, 0,053]** (2 semillas ×
  10.000); control φ = 0 al mismo protocolo 0,058 [0,052, 0,064] que contiene
  las filas φ > 0; **AC1 realizado de las contribuciones ≈ 0 para todo φ**
  (el eje era inerte) y **53,6 % de las fechas simuladas contribuyen
  exactamente cero** (selladas: 19 de 35); referencia externa de Armitage
  [4,56, 3,23, 2,63, 2,28, 2,04] contra las simuladas [∞, 3,15, 2,57, 2,27,
  2,06]: tres de cuatro por debajo; mirada 1 declarada inalcanzable por
  resolución; estadístico declarado nuevo. Quinto rechazo: `cola` §27.
- **B v2** (`decaimiento_teoria.md` reescrito; `decaimiento_feriados.md`,
  `decaimiento_prediccion.json` con testigo `b2_nuevos_ohlc.csv.gz`): la
  prueba ahora SÍ excluye la ventana sellada con embargo (643 fechas, 4.830
  filas; una re-apertura declarada con candado). Tokio C1 ajuste −23,4
  [−40,0, −6,7]; **estandarizado por estratos −31,0 [−49,7, −12,0]** (el
  control mal especificado de la v1 daba −16,8 y decía «a la mitad»);
  prueba −14,3 [−31,5, +2,3] iid (contiene el cero) / [−24,0, −4,4] bloques
  20. **Confusión estructural medida: 100 % / 0 %** — C1 no mide tiempo.
  McNemar pareado Tokio ajuste b 84, c 48, **p 0,0023**. C2/C3 siguen sin
  decidir y la potencia calculada dice que no decidirán (±4,9 pp a ×23).
  B2 con anclas e IC (Fráncfort 3,70 [0,15, 7,41]), tasa base y corr por
  exchange (India base 0,758, un solo ticker), Hong Kong e India
  incompatibles propagando las dos incertidumbres, Ámsterdam compatible
  al mismo h que su ancla. Los IC que contenían el cero se dicen.
- **Intentos, en la máquina:** `REGISTRO_INTENTOS` suma cinco tramos —DEC-B
  66, NOCAP-C 107, TRANSV-D 9, POT-E 2, SEC-F 2; A vale 0 y el registro no
  admite tuplas en cero, así que va como comentario— con la
  convención declarada en el propio registro y en `cola` §28: **N 100 →
  286; N del 5.1 106 → 292** (`veredicto_51.N_INTENTOS_PREVIO`).

### 15:03 · Director de programa: «movió la aguja, y se pasó de largo»

`dictamen_08/director.md`. Aguja: A, B, C, G y la mitad negativa de D.
Rama: F (se archiva: no hay v6), la frase de E en dos versiones, H2.
**El daño que nombra:** el registro de intentos pasó de 100 a 286 en una
tarde —bien contado, irreversible— y nadie preguntó «¿qué se rompe si esto
sale bien?»: con ese N ningún retador con Sharpe positivo pasa V5. Dos
correcciones aplicadas en el acto: la t de clúster es **PROPUESTA de
estimador** (no «el estimador desde hoy»: cambiar la vara después de ver la
cobertura lleva firma) y `MINIMO_DIAS_SHARPE` es firma. **Lo único que
sigue: decidir la rama del efecto**; hasta entonces, ningún frente empírico
nuevo ni un intervalo más. Propuestas: I adelante (después de la rama), H1
ahora no (después del 25-oct, timers de Nicolás), H2 rama (firmar los
criterios de muerte, no el frente). Nivel 1 sigue arriba: `mki-noticias`
O(n²) y `.env` 644.

### 15:03 · E v2 con sus cifras, y una errata del dictamen E

`potencia_por_metrica.md` v2: z por t de clúster (DIR 1,11, MAE 1,69, CRPS
1,76); **días para 0,80 con intervalo: 223 [28, ∞) / 96 [20, ∞) / 88 [19, ∞)**
(el extremo superior es infinito porque los tres IC del efecto contienen el
cero); DIR al +6,45 pp publicado 470; bajo R2 2.728 / 175 / 200. **Banda de
potencia de MAE a 73 días: 0,90 (generador 9 pp) / 0,86 (efecto observado) /
0,70 (bajo R2)**; DIR 0,31 / 0,29 / 0,21. Errata del dictamen E, computada:
la constante μ recupera el **7,3 %** de la ganancia de MAE, no el 93 % (el
0,405 del dictamen es lo que el modelo gana SOBRE la constante). Intentos
de E: 2. `espera_firma.md` §22 lleva la banda y la errata.

### 15:05 · Acta §75 escrita (escriba), con una errata corregida antes del commit

`DECISIONES.md` §75 (líneas 7246–7560 aprox.). El escriba escribió que C y
D reabrieron su prueba con candado: los candados están en C y **B**; D no
tiene candado y abrió tres veces (dos por el defecto de datos, una tras el
dictamen), todas declaradas. Corregido en su sitio (la frontera de la
errata es el commit). Guardián despachado sobre el diff completo; suite
completa corriendo.

### 15:08 · Suite completa en verde antes del sello de hoy

`python tests/test_motor.py` (anti-look-ahead del motor) en verde y
`python -m pytest tests/ -q`: **596 passed, 2 xfailed** en 5:08 (la corrida
partió de 557 + 2; 39 tests nuevos: simulador 11, unidades del Sharpe 6,
transversal 5, gaps/feriados 2, no capturabilidad 10, árbitro de cifras 5).
Un verde antes del sello no es un verde: el sello es a las 18:15; nada
pesado corre entre 17:50 y 20:30.

### 15:25 · Guardián: OBSERVADO, sin rechazos; once observaciones, siete aplicadas antes del commit

`dictamen_08/guardian.md`. Ninguna regla dura rota (motor/senales/snapshot/
universo/.env/timers intactos; `senales.db` mtime 2026-09-01 18:15:31;
README sin cambios; doce bloques intactos; hooks intactos; el testigo B2
descargado a las 14:50, fuera de la ventana). Aplicado en su sitio: **O1**
la justificación desmentida («saturan por anualizar») seguía viva en
`veredicto_51.py` (comentario y texto del reporte del 5.1) y en el
generador `ventana_larga.py` — reescritos, y «saturan en 1,0000» + «0,36
[0,34, 0,37]» entran a `cifras_retiradas.md`; **O2** en A3 la rama
anualizada contaba la excepción de la guarda como rechazo (un supuesto en
el lugar de un cómputo, y en la dirección favorable): ahora se COMPUTA sin
la guarda (`_dsr_sin_guarda`) y A3 se recomputó (`--solo-a3`); **O3** el
acta decía que la v2 de E estaba en curso: corregida con sus cifras; **O4**
`potencia_por_metrica.md` con etiqueta v2 y la primera tabla con el
intervalo [·, ∞); **O5** el 0,36 de §17 y de la cola marcado como retirado
(vigente 0,31 [0,27, 0,35]); **O7** la segunda «Enmienda 2» de D es la 3;
**O8** el testigo B2 indexado y las dos convenciones de sha declaradas.
**O6** no se arregla retro-escribiendo un sha que no existió: el candado de B
lleva fecha y razón sin `sha256_anterior`, y el acta lo dice. Pendientes de
Nicolás: `.env` 644 (O9), el bloque de deuda de `snapshot.py:140` que salió
de ESTADO (sigue primero en `espera_firma`), `CLAUDE.md` que aún describe
al Mac como titular (O11), y si el ratio 1,84× es el bloque trece.

### 15:31 · Commits, sin push

- `0fbfbe9` instrumento + unidades del PSR/DSR + E, F + registro de intentos
  (el hook pre-commit corrió la suite completa sobre el árbol entero: 596
  passed, 2 xfailed, 5:08).
- `f4dbaa6` Frentes B, C y D con sus testigos y candados.
- `266e4f3` árbitro de cifras, cifras retiradas, propuestas H1/H2/I.
- El cuarto commit (dictámenes, bitácora, estado epistémico, cola, espera de
  firma, ESTADO, acta §75) va con `SKIP_TESTS=1` como los dos anteriores:
  la suite ya corrió sobre este mismo árbol en el primero, y volverla a
  correr tres veces habría sido 15 minutos de CPU a las puertas de la
  ventana del sello. Nada pusheado: publicar es de Nicolás.
