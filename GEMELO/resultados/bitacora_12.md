# Bitácora de la duodécima corrida — cerrar la 11 con el adversario, sellar la primera fila prospectiva del riel de dinero, conectar la máquina al corredor en papel

**8-sep-2026, nocturna y sin supervisión.** Encargo: `~/encargo.md` (copiado a
`GEMELO/resultados/encargo_corrida_12.md`). Arranque **23:21 hora de Chile** (leído de `date`),
martes, fuera de la ventana de sellado 17:50–20:30. HEAD al abrir: `7f4938a` (Backup diario
2026-09-08; la corrida 11 está en `82f488e`, verificado con `git log`, y el parche del §26 en
`1508fad`). Modelo: Fable, esfuerzo alto, sin cambio a mitad de sesión.

- Nada se pushea. Nada se firma. Ningún archivo protegido se toca. Ninguna orden a una cuenta que
  no sea de práctica. Ninguna credencial en logs, bitácora, tests ni artefactos.

## Bloque 0 — orientación y prerrequisitos (23:21 a __, `date`)

**Prerrequisitos (0.7), leídos de la máquina y no de las actas:**

- **Parche del §26 con guardia del §49: APLICADO.** `version.py` → `PLATAFORMA_VERSION = "5.1.0"`;
  `mki_vigia.py:79` define `chequear_ancla_temporal` y `:415` lo llama. **El bloque 3 NO queda
  suspendido.**
- **Primer sello con `plataforma_version = 5.1.0`:** existe en `snapshots`, fecha `2026-09-08`,
  `timestamp_utc = 2026-09-08T21:15:03.990649+00:00`, origen `programado`. Es el marcador del corte
  de método del §84.1. El sello anterior (2026-09-07) es 5.0.3.
- **Credenciales de cuenta de práctica del corredor: NO EXISTEN.** Buscadas por nombre (patrón
  IB / IBKR / TWS / INTERACTIVE / CORREDOR / BROKER / PAPER) en el entorno del proceso y en las
  claves de `.env`, sin imprimir ningún valor: ninguna. **El bloque 4 se construye contra réplica
  grabada y E1 queda como NO EJECUTADO.**
- **Gateway del corredor: NO RESPONDE.** Sondeo de lectura con `socket.connect`, timeout 2 s, sin
  órdenes, a 127.0.0.1 y al host de Windows (172.30.240.1) en 4001/4002/7496/7497: rechazado en
  localhost, timeout en el host. Mismo tratamiento que el punto anterior.
- Ventana de sellado: la corrida arranca a las 23:21, pasada la ventana; nada pesado ni ninguna
  descarga hasta el cierre, que se estima antes de las 17:50 del 9-sep.
- **Suite al abrir: 798 passed, 4 skipped, 1 xfailed en 370,39 s** (arrancó 23:22, terminó 23:29 según
  `date`); `tests/test_motor.py` OK. Inventario de xfail esperado, declarado ANTES de leer la
  salida: **1** (`test_epistemico.py::…comparte_sesion_objetivo…`, con predicado registrado). Los 4
  skipped son los tests que aplican los diffs del §26/§49 sobre copias y se saltan solos al
  detectar el parche aplicado (acta §84.2). **Verde = sin fallos no declarados: se cumple.**
- Orientación (`orientador`, 23:26): la corrida 11 dejó abiertos G3, G8 y el re-dictamen; el acta
  §84 (líneas 9059–9099 de `DECISIONES.md`) ya registra las siete decisiones de la tarde. **Hallazgo:**
  `GEMELO/resultados/inventario_abierto_2026-09-07.md` **no existe** en el repo (el §84.4 lo lista
  como acto pendiente de Nicolás). **Hallazgo:** `README_en_borrador.md` **no existe** ni en el repo
  ni en `~` (bloque 6, punto 1, lo da por dejado). Contadores: riel largo 3 (`dinero/registro_intentos`),
  gap asiático 352 (`GEMELO.relevo_asiatico`), veredicto 5.1 declara 358; separados.
- Registro de intentos del gap asiático: **NO se toca**.

## Pre-mortem del `director-programa`, antes del bloque 1 (23:29, hora de `date`)

Veinte instrucciones marcadas: 7 de «no ejecutar tal como están» (1, 2, 3, 4, 5, 7, 8) y 13 de
«ejecutar con anotación». Qué se hace con cada una, decidido ANTES del bloque 1:

| # | Instrucción marcada | Decisión del orquestador |
|---|---|---|
| 1 | 3.2: la señal que sale de `cuenta_papel` es `senales_sin_informacion` (ruido por diseño); E0 sellaría 40 filas de ruido como track record | **Acatada en la forma, ejecutada con etiqueta.** El §84.4.1 y 7 ordenan sellar y fijan N = 40; el encargo fija el camino. Se sella, y **cada fila lleva `senal_fuente = sorteo sin información`** y el contador publicado dice «prueba de maquinaria, no track record». La pregunta «qué señal sella E0 (la sonda, L1 refutada, o ninguna) y si las filas de la sonda cuentan para N» va a `espera_firma.md` con fecha. |
| 2 | 3.2: `hasta = fecha de sello` por `cuenta_papel` es un camino que ningún gate recorrió (membresía fija en DESDE, congelado termina el 4-sep) | **Acatada.** El sellador se construye sobre `dinero/decision.proponer_ordenes` (pura, el día es argumento), con la membresía fijada en `DESDE` (G6), la sonda con `desde=DESDE` (E3) y un congelado nuevo con sha256 como insumo declarado. El gate se corre sobre ese mismo camino (auditor, 3.3). |
| 3 | 3.1: «su propia tabla en la base» autoriza DDL sobre `senales.db` | **Acatada.** Base separada `dinero/sello_dinero.db` (gitignorada, con export CSV a `data/backups/` que el job de backup versiona). `senales.db` sólo en `mode=ro`; sha256 y mtime antes y después, en esta bitácora. |
| 4 | Bloque 4: NYSE cerrada de noche; «enviar y leer en el mismo ciclo» no puede completarse | **Acatada.** Sin credenciales ni gateway (0.7) E1 ya era NO EJECUTADO; se anota además que aun con ambos no era ejecutable de noche. La primera orden queda para una corrida en horario de mercado. |
| 5 | 6.7 / D-C bis: `ibapi` no está en el PyPI oficial; fijarlo en `requirements.txt` instala una subida de terceros con licencia no verificada | **Ejecutada con verificación previa.** Se consulta la documentación oficial (bloque 4.1) sobre cómo se distribuye y bajo qué licencia; lo que diga la fuente manda sobre la memoria del agente y sobre el encargo. Si el paquete oficial no es instalable por `pip` desde PyPI, `requirements.txt` no recibe una línea que instale otra cosa: se anota como hallazgo sobre D-C bis, no se revierte la decisión. |
| 6 | Bloque 4: la «réplica grabada» no existe; un fixture escrito desde la documentación es verificar con el mismo mecanismo | **Acatada.** El fixture se rotula «escrito desde documentación, NO evidencia de C1/C2»; E1 NO EJECUTADO; ninguna frase de pantalla lo cita como validación. |
| 7 | D-E: renombrar `README.md` mueve los guardias (`cifras.DOCUMENTOS_PUBLICADOS`, escáneres de `test_epistemico.py`, cita por línea en `bifurcaciones.py:99`) al inglés y deja el español sin guardia | **Acatada.** Antes de mover un byte se extienden los guardias a los dos archivos y se revisan las citas por línea; si no queda verde, el bloque 6 no corre. |
| 8 | 8.1: «generado por la misma plantilla» presupone un generador que no existe; y el borrador `README_en_borrador.md` tampoco existe | **Acatada.** No se afirma «generado» sobre algo que no lo fue. Si el bloque 6 corre, se escribe un generador real (plantilla con marcadores + `cifras.py`) y sólo entonces se dice generado; si no hay tiempo, no iniciado. |
| 9 | 10.1: las cifras de 52 semanas que el encargo entrega al escriba son de la cuenta v1 RETIRADA | **Acatada.** Ninguna cifra se copia del encargo: se recomputa M2 sobre la v2 a 52 y 156 semanas, con banda entre semillas, o se escribe «no computado». |
| 10 | 10.1: fijar el período conociendo qué da cada alternativa es la enmienda que el §5 del pre-registro declara ilegítima | **Ejecutada con anotación.** Se escribe como enmienda fechada con la elección declarada; M2 se publica NO LEÍBLE hasta el dictamen del adversario, que es lo que el propio §84.4.5 pide. |
| 11 | Sección 2: E0 arranca sin fijar el monto de E2, contra la regla 5.4 de la regla de aporte | **Ejecutada con anotación.** Se sella igual (decisión de Nicolás, §84.4.7) y `espera_firma.md` registra que la ventana «fijar el monto sin mirar resultados» se cierra con la primera fila. |
| 12 | 3.2 + §47: el universo operable con enteras depende del presupuesto, que no se fija | **Acatada.** El presupuesto con que se decide (techo de `reglas.json`, PROPUESTA) viaja DENTRO de la fila como parámetro declarado; la pregunta va a `espera_firma.md`. |
| 13 | 3.4 + 3.6: una fila «sin sesión» inflaría el contador de N | **Acatada.** Se sella con su marca y NO cuenta para N; escrito en `regla_aporte_y_dimensionamiento.md`. |
| 14 | 3.4: «`available_at` distinto del reloj de pared» pasa trivialmente | **Acatada.** Se verifica `available_at` contra el cierre UTC por calendario de la sesión insumo y el orden `available_at < timestamp_utc < apertura objetivo`. |
| 15 | 4.6: unificar réplicas «si ninguna cifra cambia» elige el parámetro por su efecto; el decimal que se mueva es cifra movida sola | **Acatada.** El valor único es el del árbitro (4.000, que es el publicado): `bifurcaciones` lo importa de ahí; ninguna cifra publicada se mueve; cada intervalo lleva su método; el artefacto viejo de `bifurcaciones` no se regenera y se declara. |
| 16 | 4.7: un test «antes y después» escrito después del cambio compara el código nuevo consigo mismo | **Acatada.** La salida actual se congela como fixture ANTES de editar; para `baselines.py` el criterio de aceptación es además la reproducción 21/21 de `backtest.linea_base`. |
| 17 | 3.1 vs 4 y 5: el adversario dictamina un artefacto que otros bloques mueven | **Acatada.** Las respuestas de la API se vuelcan a JSON con sha256 en el momento del dictamen; al cierre se re-verifica; lo que cambió vuelve al adversario o sale de pantalla. |
| 18 | 0.7: sondear el gateway con la librería antes de autorizarla | **Acatada (ya hecha así).** Sondeo TCP pelado con `socket`, fuera de la ventana, 23:25. |
| 19 | 0.3: «verde» sin definir | **Acatada.** Inventario de xfail esperado declarado arriba (1) antes de leer la salida. |
| 20 | 13 + 7.1: construir el panel de la cuenta de práctica con datos que no existen es decorado | **Acatada.** La vista muestra filas selladas de E0 y el estado del gate; el panel de la cuenta de práctica es un estado vacío que dice qué falta (E1 no ejecutado), sin datos de ejemplo. |

Propia, no del pre-mortem: el bloque 1.1 pide juzgar «cada cifra de `bitacora_11.md`»; el adversario
recibe la bitácora y los JSON regenerados de la corrida 11 (instrumento, cuenta v2, intervalo de
coherencia) y dictamina sobre lo que la máquina sirve hoy, no sobre lo que la bitácora recuerda.

## Bloque 1 — el hueco de la corrida 11 (23:33 a __, `date`)

**1.1 Re-dictamen del adversario:** lanzado 23:33 sobre las respuestas de la API congeladas con
sha256 en `dictamen_12/api_congelada/` (`rieles.json` 1de2a3a5…, `dinero_cuenta.json` dd265401…,
`dinero_universo.json` 9ea50aa9…), la bitácora 11 y los artefactos regenerados. Resultado abajo.

**1.2 G3, la contraprueba de la fuga de 1 día por `precios_ref` — HECHA como prueba de borde.**
`contabilidad.correr_estrategia(..., fuga_precios_ref_dias=0)` es el canal de inyección (con k > 0
`precios_ref` del día d se lee del cierre de d + k, o del último disponible si no existe: la fuga
exacta del auditor, con su caída al último cierre en la fuente truncada); `cuenta_papel.correr` y
`verificar_invariancia` lo pasan. El corte de borde **se lee de `Libro.decisiones`**: se corre la
cuenta honesta y la cuenta con fuga y se toma el primer día en que alguna decisión difiere; en ese
día el estado previo es idéntico por construcción, así que el gate cortado ahí TIENE que verla.
**Medido sobre el congelado: el borde es 2023-09-11** (juego agresivo, 5 y 10 pb: UMC 2 → 3
acciones), y `verificar_invariancia(cortes=["2023-09-11"], fuga_precios_ref_dias=1)` revienta con
`ErrorLookAhead` (test `test_G3_…dia_de_borde`). Contraprueba de la contraprueba: sin fuga el mismo
corte es INVARIANTE. La contraprueba por `fabrica_senales` queda intacta: las dos conviven.

**1.5 El gate en modo diagnóstico — HECHO.** `verificar_invariancia(..., diagnostico=True)` recorre
todos los cortes y devuelve `cortes_rotos` (corte, clave, detalle) con `resultado = "ROTA"`, sin
levantar; por defecto sigue reventando en el primero. **Medido con la fuga de 1 día sobre los diez
primeros cortes por regla: la ven 5 de 10** (2024-05-22, 07-08, 08-19, 10-01, 11-12), lo que pone
número a la medición del auditor («2 de 11 a dedo»): una fuga corta sólo se ve desde los cortes que
caen en el día siguiente a una decisión afectada. Test determinista sobre el congelado (0 < rotos < 10).
`fuga_inyectada` viaja en el resultado del gate para que un reporte nunca confunda una corrida de
contraprueba con la legítima.

**1.3 G8, `available_at` por ticker en el `.meta.json` — HECHO sin tocar ningún CSV.**
`precios.disponibilidad_por_ticker(cierres)` → por ticker `primer_cierre`, `ultimo_cierre`,
`n_cierres`, `available_at_utc` (cierre UTC por calendario XNYS de la última sesión con dato, via
`exchange_calendars` directo: `calendarios.py` es camino de sellado y `dinero/` no lo importa).
`congelar()` lo escribe en todo congelado nuevo; a los dos existentes se les agregó el campo con el
CSV intacto (sha256 verificado igual antes y después: `69ca7283…` y `4222c8ec…`). Lo que el campo
deja a la vista: **GFS empieza el 2021-10-28, ARM el 2023-09-14, SNDK el 2025-02-13** (los demás
33 desde 2018-09-05); los 36 terminan el 2026-09-04 con `available_at_utc = 2026-09-04T20:00:00Z`,
siete horas antes del `congelado_en_utc`. Test `test_G8_…` exige el campo en TODO `.meta.json`,
recomputa desde el CSV y compara, y verifica `available_at ≤ congelado_en`; contraprueba de
significado con un feriado (2026-09-07 → None, no inventa hora).

**1.4 Constancia de las objeciones 3 y 12 de la corrida 11:** la 3 (suspender 7, 8 y 9 si el
bloque 1 fallaba) nunca se activó, porque el instrumento discriminó; la 12 (el guardia de razones
de xfail como frente nuevo) quedó ejecutada y `tests/test_razones_xfail.py` existe con 4 tests.
Nada se reabre.

Tests nuevos del bloque: 6 en `tests/test_dinero.py` sección 7 (34 s). `test_dinero.py` +
`test_api.py` + `test_epistemico.py`: 78 passed, 1 xfailed.

**1.1 Re-dictamen del `estadistico-adversario` (23:37, `dictamen_12/re_dictamen_corrida_11.md`).**
Veredicto global: **las cifras re-corridas se sostienen en los artefactos y NO se sostienen en la forma
en que la API las servía.** Las 18 exigencias del dictamen 11 están aplicadas en los artefactos (verificadas
una por una); ninguna había llegado al serializador de la API. **Cuatro cifras RETIRADAS** hasta que D1–D18
estén en el ejecutable: el **12,5** pelado (fricción del juego activo: era la semilla de la página, no la
mediana de 20 semillas; sin intervalo, sin período ni denominador), el **«95 %»** del IC de la σ (cobertura
medida 0,850 a 156 semanas), el **«NO está recomputada»** del R2 en `que_lo_mata` (falso desde el 8-sep:
+2,6 pp, n=194, 28 días, t de clúster [−15,7, +20,9] que contiene el cero, permutación 0,821) y el **conteo de huecos del mapa** sin presupuesto
ni modo (a 100 USD enteras son 4 huecos y 7 alcanzables). Se sostienen sin etiqueta nueva: las cuatro cifras
del riel de medición, el tamaño bilateral y las coberturas del instrumento, ρ, el R2 de la rama de coherencia,
la negativa a llamar «falsos positivos» a los 5 ✓ de 24, `pasan_holm: []`. **Criterios congelados:** V1 NO
PASA, V3 NO PASA, V2/V4/V5/V6/V7 NO EVALUABLES, R2 SE DISPARA en las dos ramas, R3 NO CERRABLE. **Conteo de
intentos: el adversario NO acepta el 0 del bloque 4 de la corrida 11** (precedentes `COLA` y `DEUDA-2f`): piso
352 → 354 y 358 → 360.

Los siete patrones retirados entraron a `GEMELO/cifras_retiradas.md` (el hook los bloquea en `.md` y `.py`).

**Aplicación de D1–D18 (23:45 a __), en el ejecutable y no en el texto:**

| D | Qué | Dónde | Estado |
|---|---|---|---|
| D1 | fricción como objeto (mediana, banda, K, pb, semanas, denominador, `es_una_semilla: false`) | `api/main.py::_comisiones_juego_activo` (y cierra el tragador del bloque 2.2 con excepciones explícitas y `logging`) | aplicada; test `test_D1_…` |
| D2 | etiqueta del IC de σ leída del instrumento: «nominal 95 %, cobertura medida 0,850 [0,833, 0,865] a 156 semanas» | `api/main.py::_potencia_desde_artefacto` | aplicada |
| D3 | la σ servida y el MDE80 nunca en la misma oración; el MDE80 se cita con SU σ ancla | ídem; test `test_D3_…` | aplicada |
| D4 | `mde80(sigma, T, alpha)`; columnas al α nominal y al α real | `GEMELO/simulador/instrumento_dinero.py` | aplicada; artefacto regenerado (abajo) |
| D5 | MDE80 con banda propagada de la banda entre sorteos de σ | `mde80_con_banda` | aplicada |
| D6 | `convencion_anualizacion`: suma aritmética y capitalizado, las dos publicadas | ídem | aplicada |
| D7 | Wilson iid sobre 480 comparaciones RETIRADO; queda el conteo con la semilla como unidad y un IC t entre las 20 semillas | `cuenta_papel.barrido_semillas`; test `test_D7_…` | aplicada; artefacto regenerado |
| D8 | cada `contra.*` lleva `alpha_es: nominal`, `alpha_real_medido`, `cobertura_medida_ic_media` | `cuenta_papel.a_json` | aplicada |
| D9 | `mapa` con `presupuesto_usd`, `modo`, `al_borde`, o no se sirve | `api/main.py::_mapa_con_etiqueta`; test `test_D9_…` | aplicada |
| D10 | `dias_de_censo: 1`, `fecha_censo`, y la frase de por qué no lleva intervalo | ídem | aplicada (el `.md` del censo ya lo decía) |
| D11 | `que_lo_mata` compuesto desde `intervalo_coherencia.json` (R2 bajo la regla firmada) | `api/main.py::_que_mata_medicion`; test `test_D11_…` | aplicada |
| D12 | cobertura 80 % con Wilson (221/238 → 92,9 % [88,9, 95,5]) | `cifras.sellada` + API (quinta cifra) | aplicada |
| D13 | etiqueta de régimen: la ventana tiene «Alcista · vol alta» en 34 snapshots y 2 sin régimen sellado | `cifras.sellada` + API | aplicada; **hallazgo:** 2 snapshots de la ventana no tienen `regimen` (NULL) |
| D14 | «validado» fuera de los generadores y del pre-registro; patrón en el guardia | `api/main.py`, `cuenta_papel.py`, `instrumento_dinero.py` (no lo tenía), `preregistro_dinero.md` | aplicada |
| D15 | `senal_larga.denominadores` separa celdas (6) de contrastes (30); `k_bajo_la_nula: null` | `api/main.py`; test `test_D15_…` | aplicada en parte: la distribución de k bajo la nula NO se computó (queda en `cola_decisiones.md`) |
| D16 | Wilson de 70,9 % y 56,5 % en el artefacto de coherencia | `GEMELO/intervalo_coherencia.py`, regenerado: 70,9 [64,6, 76,4] y 56,5 [49,9, 62,8] | aplicada |
| D17 | `BLOQUE_BOOTSTRAP_SEMANAS = 4`, `REPLICAS_BOOTSTRAP = 2000`, `ALPHA = 0,05` fijados por test | `tests/test_dinero.py::test_D17_…` | aplicada |
| D18 | fila `COHER-12` (2) en `GEMELO.relevo_asiatico.REGISTRO_INTENTOS`: **352 → 354**; `veredicto_51.N_INTENTOS_PREVIO` 352 → 354 (**358 → 360**) | `GEMELO/relevo_asiatico.py`, `backtest/veredicto_51.py` | aplicada |

`api/CONTRATO.md` enmendado antes de mover los endpoints; `frontend/src/lib/tipos.ts` sigue al contrato.

## Bloque 2 — los hallazgos abiertos de la revisión del diff (23:45 a 00:05, `date`)

1. **Estatus en pantalla — HECHO.** `Card` recibe `estatus` y lo renderiza con el componente común
   `Estatus`; las cinco tarjetas de `RielDinero.tsx`, la columna y la cabecera de `Rieles.tsx` lo
   declaran. `tests/test_frontend_estatus.py` (4 tests, sin dependencia nueva: lee el TSX, como ya
   hacía la suite con la palabra prohibida) exige que TODA `<Card` de una vista del riel lo
   declare, con contraprueba; y verifica las palabras del bloque 5.3 («rentable», «retorno esperado»,
   «ganancia esperada», «confianza»; «oportunidad» sólo con estatus en la misma línea).
2. **Tragador `_comisiones_juego_activo` — REEMPLAZADO** junto con D1: excepciones explícitas
   (`OSError`, `KeyError`, `ValueError` al leer reglas; `KeyError`, `TypeError` por artefacto con otra
   forma) con `logging.getLogger("mki.api.dinero")`. Censo de `except Exception` fuera de `venv/`: 50
   sitios. Veredicto por familia: **camino de sellado** (`snapshot.py` ×4, `senales.py`, `mki_vigia.py` ×4,
   `mki_noticias.py` ×5, `alertas.py`, `calendarios.py` ×2, `modo.py`): protegidos o de jobs que deben
   terminar siempre, con el guardia del §49 ya aplicado donde importaba — **no se tocan** en esta
   corrida. **API** (`api/main.py` :252, :258, :302, :315, :375; `api/utilidades.py:61`): son
   presentación de calendario/salud con caída a `None`/`continue`; el :375 registra el error en el
   detalle; **veredicto: aceptables, sin quinto tragador del tipo del 969** (ninguno esconde una cifra
   del riel). **Investigación** (GEMELO/*, backtest/*, dinero/cobertura_causal.py:109 con `noqa` y
   reporte): declarados o reportan. **Hooks y tests**: fuera de alcance.
3. **Comentario del pre-registro («antes de esta corrida» → «antes de la primera corrida»)** en
   `dinero/cuenta_papel.py:8`: correcto; va al acta como errata fechada.
4. **El nombre del corredor VUELVE.** `grep -i corredor|ibkr|interactive` en `dictamen_11/` da vacío:
   el curador no lo exigió. La perífrasis la había impuesto `test_ninguna_funcion_del_riel_manda_ordenes_de_verdad`
   (prohibía las cadenas «ibkr» e «interactivebrokers» en `dinero/`). El test se reescribe: prohíbe
   HABLAR con un corredor (verbos de API, credenciales, importar `ibapi` o `corredor`), no NOMBRAR la
   fuente del arancel. `cuenta_papel.py:49` y `costo.fuente` del JSON nombran Interactive Brokers.
5. Resuelto en el bloque 1.5.
6. **Réplicas del bootstrap unificadas en el árbitro:** `bifurcaciones.N_BOOT` importa `cifras.N_BOOT_DIA`
   (4.000). **Medido:** con 4.000 el IC de día publicado es [−7,2, +26,6] (contiene el cero); con 10.000 sería [−7,2, +26,5] (contiene el cero)
   — la discrepancia era exactamente ésa. Se eligió el valor del árbitro y NO el mayor (pre-mortem 15):
   **ninguna cifra publicada se movió.** Test `test_el_numero_de_replicas_del_bootstrap_vive_en_el_arbitro`.
   El artefacto viejo de `bifurcaciones` (`bifurcaciones.md/.csv`) NO se regeneró: queda declarado que se
   produjo con 10.000 y se regenera cuando vuelva a correr.
7. **`pd.concat` fuera de `motor.py` — HECHO con fixture congelada ANTES de editar** (pre-mortem 16):
   `tests/fixtures/concat_2_7_antes.pkl` (5 avisos de pandas con el código viejo). `api/main.py` usa
   `_alinear(*series)` = `pd.concat(..., axis=1, sort=True)` en los cuatro sitios; `backtest/baselines.py:158`
   lleva `sort=True`. `tests/test_concat_fuera_de_motor.py` compara byte a byte (CSV) y con igualdad exacta:
   **idéntico**; el aviso desaparece. Los otros dos `concat` de `baselines.py` (:119 dict, :169 niveles) NO
   los marcó pandas y se dejan: tocarlos sin advertencia sería un cambio sin evidencia. `test_linea_base`
   (reproducción 21/21) en verde.
8. **Erratas de versión — HECHAS con nota fechada:** `.claude/rules/plataforma.md:26` y
   `.claude/agents/ingeniero-plataforma.md:52` remiten al §84.3 sin borrar la historia.
   `scripts/ensayo_replica.py:78`: es **dato de ensayo** (fixture sintética de un sello titular de la
   ventana de sombra) — se deja y se comenta; no se lee de `version.py` a propósito.
9. **Método de los parches:** lección escrita en `docs/manual-agentes.md` («Método de los parches no
   aplicados», 9-sep): todo parche se prueba también sobre una copia del árbol entero con la suite
   completa; los comentarios de un parche al camino de sellado no nombran `GEMELO/` ni `dinero/`. La
   automatización (`test_parches_en_worktree.py` sobre `git worktree`) queda PROPUESTA en
   `espera_firma.md`, no instalada.

## Bloque 3 — E0: la primera fila sellada prospectiva (00:05 a __, `date`)

- **Módulo propio `dinero/sello_dinero.py`, fuera de `snapshot.py`; base propia `dinero/sello_dinero.db`**
  (pre-mortem 3: `senales.db` no recibe DDL). Tabla `sellos_dinero` con `timestamp_utc` (reloj de pared de
  la emisión), `available_at` (cierre UTC por calendario XNYS de la última sesión con dato, del `.meta.json`
  de la extensión, G8), `sesion_objetivo` y `apertura_objetivo_utc`, sha256 de los DOS insumos (congelado
  grande + extensión chica `dinero/datos/sello/ext_*.csv`), `plataforma_version` (leída del texto de
  `version.py`: `dinero/` no importa el camino de sellado), `senal_fuente` (declara la sonda sin
  información), `juego`, `presupuesto_usd` (viaja dentro de la fila: pre-mortem 12), `tamano_nominal = 0`,
  `estado` (`pendiente` | `no_verificable_timing` | `dia_sin_sesion`) y `cuenta_para_N`. **Triggers
  `BEFORE UPDATE` / `BEFORE DELETE` que abortan**: la fila no se reescribe. Export CSV a `data/backups/`.
- **La decisión** (`decidir(cierres, dia)`) es función PURA del insumo ≤ día: membresía fijada en `DESDE`
  (E1/G6), sonda con `desde=DESDE` (E3), `decision.proponer_ordenes` con el cierre del día, cartera vacía
  con efectivo = techo (E0 no acumula posiciones). NO pasa por `cuenta_papel.correr` (pre-mortem 2). Gate
  propio `verificar_invariancia_decision` (insumo entero contra cortado en el día y los 5 siguientes) y
  contraprueba: una decisión que mira el cierre de mañana lo hace reventar.
- **Medido sobre el congelado (2026-09-04):** 33 operables; el juego conservador a 500 USD decide **una
  compra: GFS, 2 acciones a 45,21** (la regla la dimensiona; lo sellado es 0); 32 «nada» con motivo
  («señal +1,30 pp bajo el umbral +1,35», «su intervalo contiene el cero»…).
- Tests: `tests/test_sello_dinero.py` (14 + 1 skip hasta que exista la extensión real): available_at por
  calendario y ≠ reloj de pared; orden `available_at < timestamp_utc < apertura`; sello tardío →
  `no_verificable_timing`; sábado → `dia_sin_sesion` y NO cuenta para N (pre-mortem 13); insumo
  desactualizado no cuenta; UPDATE/DELETE abortan; idempotencia por sesión; export.
- **Timer PROPUESTO, no instalado:** `GEMELO/propuestas/systemd/mki-sello-dinero.{service,timer}`,
  `Mon..Fri 21:00 America/Santiago`, argumentado en el propio archivo (fuera de la ventana 17:50–20:30;
  ≥ 3 h después del cierre de NYSE todo el año; ≥ 12 h antes de la apertura objetivo).
- N = 40, piso enteras, «sin sesión no cuenta», monto de E2 sin fijar y la pregunta de la señal:
  escritos en `regla_aporte_y_dimensionamiento.md` §5-bis con fecha.
- `auditor-lookahead` lanzado 00:05 sobre el módulo y sus tests. **Sin dictamen no se sella.**

## Bloque 4 — E1: el adaptador al corredor, contra réplica (00:00 a 00:12, `date`)

**E1 NO EJECUTADO** (sin credenciales ni gateway, chequeo 0.7; y NYSE cerrada de noche, pre-mortem 4).
Se construyó y probó lo que se podía probar sin cuenta.

**URL oficiales consultadas (8/9-sep-2026, 23:35 a 23:50 `date`) y qué dijo cada una:**
- `https://interactivebrokers.github.io/tws-api/introduction.html` → la documentación está DEPRECADA y
  remite a IBKR Campus; los componentes se bajan de `interactivebrokers.github.io`.
- `https://interactivebrokers.github.io/` (página de descarga) → licencia **«TWS API Non-Commercial
  License»** con aceptación previa; estable API 10.45 (30-mar-2026), latest **API 10.50 (26-ago-2026)**,
  `twsapi_macunix.1050.01.zip`; **la Python API viene sólo en la latest**. Sin mención de PyPI.
- `https://pypi.org/project/ibapi/` → **9.81.1.post1, 6-dic-2020**, maintainer «freemo» (IBG LLC),
  «Other/Proprietary License (IB API Non-Commercial License or the IB API Commercial License)».
- `https://interactivebrokers.github.io/tws-api/initial_setup.html` (deprecada) → **TWS 7496 real,
  7497 práctica**; «Read Only» activado por defecto; «Enable ActiveX and Socket Clients».
- `https://interactivebrokers.github.io/tws-api/executions_commissions.html` (deprecada) →
  `reqExecutions` + `execDetails` (execId, orderId, shares, cumQty, price, exchange, side…),
  `commissionReport` (execId, commission, currency, realizedPNL); **por defecto sólo ejecuciones desde
  medianoche**.
- `https://www.ibkrguides.com/clientportal/aboutpapertradingaccounts.htm` → **USD 1.000.000** iniciales;
  reinicio desde Client Portal hasta 5× la cuenta real. Sin prefijo de cuenta ni comisiones.
- **403 a esta máquina:** `interactivebrokers.com/docs/tws-api/doc/`, `…/campus/ibkr-api-page/ib-gateway/`,
  `…/campus/trading-lessons/installing-configuring-tws-for-the-api/`,
  `…/campus/trading-lessons/accessing-the-tws-python-api-source-code/`. **404:** `ibkrguides.com/ibgateway/configapi.htm`.
- Los puertos **4001/4002 del IB Gateway** y el **prefijo «DU»** de las cuentas de práctica salen de un
  resumen de búsqueda sobre páginas de `interactivebrokers.com` (campus), no de una página leída
  entera: **DECLARADOS NO VERIFICADOS DIRECTAMENTE** en el código. La guardia los exige igual.

**Hallazgo sobre D-C bis:** `ibapi` NO es instalable con licencia verificada desde PyPI (el paquete de
PyPI tiene seis años; el oficial vigente se baja con aceptación de licencia). `requirements.txt` recibe
la versión fijada (`ibapi==10.50.1`, desde el zip oficial) **como línea comentada**, no instalable;
instalarlo es acto de Nicolás. El adaptador importa `ibapi` de forma PEREZOSA. No se revierte la decisión:
se anota (`espera_firma.md`).

**Adaptador `corredor/ibkr.py`:** interfaz mínima (conectar, enviar orden **siempre `exchange="SMART"`**,
estado, ejecuciones con comisión, posiciones y efectivo con `MarcaRetraso`, desconectar). **Guardia de
papel en código:** puerto ∉ {7497, 4002} → `ErrorCuentaNoPractica` al construir; cuenta sin prefijo `DU`
en `managedAccounts` → desconecta sin operar; ejecución de cuenta no-DU → revienta. `conciliar()` compara
lo leído por API con el reporte oficial y declara C2 «NO cumplida» ante una diferencia o una falta.
`TransporteReplica` lee `corredor/replica/respuestas_practica.json`, rotulado **«ESCRITO DESDE
DOCUMENTACIÓN, NO GRABADO: NO es evidencia de C1/C2»** (pre-mortem 6). `TransporteIbapi` deja los métodos
como `NotImplementedError` a propósito: código «que debería funcionar» sin haberlo ejecutado no se presenta
como cableado. `tests/test_corredor.py`: 14 tests (guardia con cuenta «U1234567» que finge ser real por el
puerto de práctica, sesión mixta, sin conexión no se opera, ciclo completo contra la réplica con dos
órdenes, conciliación detecta diferencia y falta, aislamiento en las dos direcciones, `ibapi` no a nivel
de módulo ni en `requirements`, ninguna credencial en `corredor/`).

**Escala (4.5):** con USD 1.000.000 simulados la comisión mínima de 0,35 USD es 3,5 × 10⁻⁷ del capital:
E1 validará cableado, no fricción. Escrito acá y en el acta; reiniciar el capital es acto de Nicolás.

**3.3 Dictamen del `auditor-lookahead` (00:14, `dictamen_12/auditor_lookahead_sello_dinero.md`): NO SE SELLA
HASTA E1–E5.** Invariancia al borrado del futuro LIMPIA (35 días + bordes de feriado, 5 cortes cada uno; con
congelado+extensión idéntica), pero cinco fugas demostradas ejecutando código: **H1** el gate que corría antes
del sello real era VACUO (en el último día hay un solo corte: comparaba la decisión consigo misma — el test lo
cazaba en 2026-08-20 y no en el único día que importa); **H2** la sonda avanza un rng por sesión, así que la
decisión depende del NÚMERO de sesiones desde DESDE (una sesión repuesta por la fuente corre el sorteo: fuga
de disponibilidad/reproducibilidad, y `ext_*.csv` no lo versionaba ningún job); **H3** publicación
asincrónica: 32 de 33 tickers sin la última sesión contaban para N y el motivo atribuía a la señal la falta de
dato; **H4** el «día» del sello salía del huso del HOST (sábado 00:30 Chile = viernes 23:30 NY: misma
información, distinto conteo); **H5** un segundo sello del mismo día con OTRA extensión se ignoraba en
silencio y `sellar` devolvía un resumen que afirmaba haber sellado. Más H6 (reajuste retroactivo mueve
`precios_ref`; el solape que lo detectaría se tiraba), H7 (faltaban sha de `reglas.json`, disponibilidad por
ticker, huella del código), H8 (`exportar=True` por defecto pisaba el CSV real desde una base temporal).

**Aplicadas E1–E8 (00:20 a 00:31), `VERSION_SELLO = E0.2`:** gate con `minimo_cortes = 2` que revienta
«VACUO», y `gate_previo_al_sello` (penúltimo día + 6 sesiones atrás; el último se declara no vigilable);
`fecha_sello` y `estado_dia` desde el calendario de Nueva York (`dia_en_calendario_del_exchange`), nunca del
host; `ultimo_cierre_ticker`/`available_at_ticker` por fila, motivo «sin dato en el insumo…», `insumo_completo`
y estado `insumo_incompleto` que NO cuenta para N; tabla inmutable `divergencias_sello` y resultados
`ya_sellada` / `divergencia_registrada` sin describir un sello que no ocurrió; `exportar_csv` exige ruta si
la base no es la real, `respaldar_extension` copia csv+meta a `data/backups/sello_dinero_ext/`;
`reglas_sha256`, `sellador_sha256`, `insumo_ext_archivo`; `solape_con_congelado` en el meta con
`reajuste_detectado`; `estado_timing` y `estado_dia` separados. Tests: 17 + 1 skip, con un test por exigencia
(E1 vacuo, E2 viernes 23:30 NY vs sábado 03:30 UTC iguales, E3 AMD/KLAC sin dato, E4 divergencia, E5
export, E7 split 2:1 detectado). **Re-verificación pedida al auditor (00:32); sin su «SE PUEDE SELLAR» no se sella.**

## Bloque 5 — la pantalla (00:05 a 00:35, `date`)

Vista `/sellos` (`frontend/src/vistas/SellosDinero.tsx`, ruta y navegación), endpoint `/api/dinero/sellos`
(contrato enmendado antes), tipos. Muestra E0 (contadores con FUENTE por celda: los conteos de
`sello_dinero.db`, el N = 40 como DECISIÓN del acta §84.4.7), E1 como estado vacío que dice qué falta (sin
datos de ejemplo, pre-mortem 20; hay test que exige `posiciones/efectivo/ejecuciones = null` mientras esté
NO EJECUTADO), el último sello con hora de emisión y apertura objetivo en hora de Chile, cuenta regresiva
computada en el navegador con leyenda («a esa hora no ocurre nada: el tamaño sellado es cero»), la tabla de
decisiones por instrumento (señal sin información en el título) y el gate de la CUENTA EN PAPEL v2 rotulado
como tal (no es el gate de E0). Sondeo cada 60 s con el `useApi` existente; sin dependencia nueva.
`npm run build` OK.

**Dictamen del `curador-epistemico` (00:17, `dictamen_12/curador_vista_sellos.md`): RECHAZADO, 4
bloqueantes, 12 correcciones.** Todo aplicado antes del cierre: (1) la fuente «sello_dinero.db» era FALSA
para el 40 → fuente por celda y `N_objetivo_fuente` desde el módulo; (2) el gate mostrado era el de la
cuenta v2 con INVARIANTE a 18px → título honesto, mismo tamaño que su alcance y `nota_e0`; (3) «la ventana
15–23 jul, que sostiene casi toda la ventaja» ordenaba cantidades que el diseño no ordena → «la ventaja de
la ventana completa no se distingue de cero, y sin esa ventana…»; (4) `estatus="MEDIDO / SIMULADO"`
inventado para una tarjeta de prosa (efecto colateral del test que exige la prop en toda Card) → `SIN
CIFRAS` explícito y el test lo admite sólo así. Correcciones: PRÁCTICA y TAMAÑO CERO fuera de la ranura de
estatus; «fuera de la ventana 17:50 a 20:30 de producción»; columnas «cierre del insumo sellado» y «banda del
sorteo»; «con cobertura medida 0,850, por debajo del 95 % nominal: el punto es utilizable, el intervalo no»;
el horizonte del `tipo_intervalo` interpolado; `dias_de_censo` derivado de las metas congeladas; fricción y
potencia con estatus SIMULADO (pasaron por el adversario); «hallazgo robusto» → «estable entre los 20
sorteos»; el chip de la columna de `Rieles` acota su alcance. Observación acatada: censo de palabras
prohibidas también sobre el JSON servido (`test_las_frases_fijas_de_la_api_del_riel_tampoco_insinuan_resultado`).

## Bloque 8 — las firmas §43 y §47 (00:10 a 00:35, `date`)

**§47 — APLICADA.** Enteras, N = 40, «sin sesión no cuenta», SMH fuera por el piso (frase en la vista y en la
API; el README lo dirá cuando el bloque 6 corra): `regla_aporte_y_dimensionamiento.md` §5-bis con fecha.

**§43 — EJECUTADA COMO ESTABA ESCRITA, Y DECLARADA NO APLICABLE.** `GEMELO/m2_periodo.py` recomputó M2
sobre la v2 (20 semillas, ninguna cifra de la v1 ni del encargo; pre-mortem 9): conservador **3,9 % a 52
semanas [3,56, 4,58], 8,6 % a 104, 12,4 % a 156 (techo 13,1 %)** — no cruza el 25 % en ningún horizonte;
medio 26,6 % a 156 (17 de 20 semillas cruzan); agresivo 18,7 %. El adversario
(`dictamen_12/adversario_43_periodo_m2.md`) reprodujo una celda exacta a mano y dictaminó **NO APLICABLE**:
el 25 % no tiene unidad de período (numerador flujo, denominador fijo en 500 USD desde la semana 5: el
cociente es proporcional a h), el «horizonte pre-registrado de la vara» que la firma invoca no existe en el
§2 (piso prospectivo de duración, no ventana de acumulación) y se dispara la cláusula de escape del propio
§84.4.5; la elección es inerte para el juego que M2 nombra y del tipo que el §5 declara ilegítimo. **Lectura
primaria honesta: la tasa anualizada**, 3,9 %/año del conservador, estable a 52/104/156. Hallazgos que el
módulo no publicaba y ahora publica (E1–E9 aplicadas, artefacto regenerado 00:33): 5 de 20 semillas
conservadoras se **congelan** (sin caja para una acción entera) y M2 las puntúa bajo por quiebra operativa;
el deslizamiento estaba excluido (con 5 pb, conservador 12,5 → 13,9 % de vida entera; medio 30,0 % a 156);
`pct_a_156` no es la cifra de vida entera (13,1 vs 13,2); una sola trayectoria de mercado (la banda entre
semillas no la cubre); 12 lecturas computadas, 1 elegida. Textos: enmienda §8 en `preregistro_dinero.md`
(E10, E13), nota fechada en el acta §84.4.5 (E11), §43 de `espera_firma.md` con la pregunta exacta (E11,
E12). Intentos del DSR: 0 (de acuerdo con el adversario); grado de libertad de criterio registrado, contador
a decidir (cola). **Un resultado negativo es un resultado: la firma §84.4.5 no se pudo ejecutar como vara.**

**3.3 bis — Re-verificación del auditor (00:33 a 00:47): E1–E5 RESUELTAS, «SE PUEDE SELLAR».** Reinyectó la
fuga de H1 y el gate previo ahora la ve; sábado 00:30 Chile y viernes 20:30 Chile cuentan igual; 32 tickers sin
dato → `insumo_incompleto`; segundo sello con otro sha → divergencia registrada; ningún CSV real tocado desde
bases temporales. Abierto y declarado: H2 residual (número de sesiones desde DESDE), Z1 (`visible_en`), Z2
(yfinance ajustado: se detecta, no se corrige), Z3 (analista). Texto completo en el dictamen.

**3.4 — EL PRIMER SELLO, a mano (00:38:17 hora de Chile, leído de `date`).** Fuera de la ventana (17:50–20:30)
y antes de la apertura objetivo (9-sep 13:30 UTC = 10:30 Chile). `python -m dinero.sello_dinero --sellar`:
descarga de la extensión (36 tickers, una sesión nueva: 2026-09-08; `ext_2026-09-08.csv`, sha256 `89a5e296…`),
gate previo INVARIANTE (penúltimo día 2 cortes; 6 sesiones atrás 6 cortes), **33 filas selladas**,
`timestamp_utc = 2026-09-09T03:38:17.156824+00:00`, `available_at = 2026-09-08T20:00:00+00:00` (cierre XNYS
por calendario: distinto del reloj de pared, verificado), `sesion_objetivo = 2026-09-09`, apertura
`2026-09-09T13:30:00+00:00`; orden `available_at < timestamp_utc < apertura` verificado; estado `pendiente`,
insumo fresco y completo (33 de 33 con cierre del 8-sep), **`cuenta_para_N = 1`: sesiones que cuentan 1 de
40**. Decisión del juego conservador a 500 USD: **0 compras, 33 «nada»** (la sonda del 8-sep no cruzó el umbral
de +1,35 pp con intervalo que excluya el cero en ningún instrumento; máxima señal +22,8 pp con banda que cruza
el cero). Sellados además: `insumo_base_sha256 69ca7283…`, `reglas_sha256 125a8602…`, `sellador_sha256
93db9b70…`, `plataforma_version 5.1.0`, `version_sello E0.2`. Export `data/backups/sello_dinero.csv` (33
filas) + `_divergencias.csv` (0) + extensión respaldada en `data/backups/sello_dinero_ext/`.
**`senales.db` idéntica antes y después** (sha256 `29692499…`, mtime 2026-09-08 18:15:30): la base del
titular no se tocó (pre-mortem 3). `test_sello_dinero.py` con la extensión real: 18 passed.

**Hallazgo del primer sello (E7): reajuste retroactivo en WDC.** El solape de 29 sesiones (2026-07-28 a
2026-09-04) entre la descarga de hoy y el congelado del 7-sep difiere en WDC con dif. rel. máx. 3,2 × 10⁻⁴
(los otros 35 tickers, idénticos a 1e-6). Es un ajuste retroactivo de yfinance entre el 7 y el 9-sep (del
tamaño de un dividendo), declarado en el `.meta.json` de la extensión y en el log del sellador; no se
corrige (la fila usa el congelado para membresía y sonda, y el cierre del 8-sep para `precios_ref`). Es
exactamente la zona ciega Z2 del auditor, ahora con un caso real medido el primer día.

## Bloque 6 — README en inglés: NO INICIADO (declarado)

`README_en_borrador.md` no existe (ni en el repo ni en `~`) y no existe ningún generador de README (el árbitro
verifica anclas contra el texto; no lo produce): las dos premisas del bloque («Nicolás dejó un borrador»,
«se genera por la misma plantilla que el español») no se cumplen en la máquina (pre-mortem 7 y 8). Hacerlo
bien exige escribir un generador con marcadores alimentado por `cifras.py`, extender `DOCUMENTOS_PUBLICADOS`
y los escáneres a los dos archivos, revisar la cita por línea de `bifurcaciones.py:99` y traducir 440 líneas
con cada negativo intacto; no cabía en la noche sin degradar el resto (prioridad 13 del encargo). D-E sigue
firmada. Nada de este bloque se tocó.

## Dictámenes de cierre (archivados en `GEMELO/resultados/dictamen_12/`)

- **`guardian-constitucion` (00:47): OBSERVADO, ningún rechazo.** Catorce reglas en verde con evidencia
  (camino de sellado byte a byte idéntico, `senales.db` con su sha, triggers probados con fila presente,
  sin push/pull/commit, `main`, acta sin borrar nada, cero cifras retiradas introducidas, `parches/`
  intacto, sin credenciales, sin «confianza», `ibapi` comentado, timer no instalado). Tres observaciones,
  las tres corregidas antes del cierre: (1) la suite previa al sello estaba ROJA por dos intervalos de esta
  bitácora que contienen el cero sin decirlo → dicho, y suite completa de cierre abajo; (2) el §85.9 prometía
  verdes sin cifra → cifra escrita; (3) los puertos 4001/4002 y el prefijo «DU» NO VERIFICADOS
  DIRECTAMENTE faltaban en la deuda de `ESTADO.md` → agregados. Inventario: reintroducciones preexistentes
  en HEAD (`DECISIONES.md`, `espera_firma.md`, `cola_decisiones.md`, `cifras.py:46,273`,
  `test_bifurcaciones.py:241,246`), fuera de alcance; y los JSON congelados de `api_congelada/` traen a
  propósito las cifras retiradas (prueba del delito).
- **`director-programa` (00:47): nada se revierte.** Las siete decisiones del §84.4: ninguna revertida
  (D-C bis anotada como hallazgo; §43 es la cláusula de escape del propio §84.4.5; D-E sigue firmada). Dos
  correcciones aplicadas: nota fechada en `bifurcaciones.md` (el comando ya no reproduce el artefacto con
  10.000) y el chequeo de vacuidad generalizado a `cuenta_papel.verificar_invariancia` (con test). Seis
  normas instaladas de paso, declaradas en el acta §85.8 bis; la inversión de orden (bloques 2 y 8 antes
  que el 6) declarada como tal. Veredicto: la corrida movió la aguja hacia `VISION.md` §2.2; lo urgente que
  posterga es de Nicolás: el timer del sellador (§53).

## Cierre (suite 00:50–00:57; esta sección escrita a las 08:57 del 9-sep tras una pausa de la sesión, `date`; nada cambió en el árbol entre medio)

- **Suite completa al cerrar, con el árbol quieto: 856 passed, 4 skipped, 1 xfailed en 402,67 s (00:50
  a 00:57); `tests/test_motor.py` OK; `npm run build` OK.** +58 tests respecto de la apertura (6 de G3/G8/
  diagnóstico, 2 de D7/D8/D17, 1 de vacuidad, 4 del concat, 6 de la API, 6 del estatus en pantalla, 14 del
  corredor, 18 del sellador, 1 de réplicas). Inventario de xfail esperado: **1**, sin cambio. Verde = sin
  fallos no declarados: se cumple. Una suite previa (00:31–00:43, antes del sello) dio 1 fallo: dos
  intervalos citados en esta bitácora sin decir que contienen el cero; corregido y verificado.
- Ventana de sellado: no se cruzó (23:21 a 00:57, martes-miércoles). Nada descargado en la ventana; una
  descarga fuera de ella (la extensión del sello, 00:38). Ninguna conexión al corredor más allá del sondeo
  TCP de lectura de las 23:25.
- Registro de intentos: gap asiático **352 → 354** (`COHER-12`, exigencia D18 del re-dictamen); veredicto
  5.1 **358 → 360**; riel largo **3, sin cambio**. Los dos registros siguen separados (§82.6). El §43 no es
  intento del DSR; es un grado de libertad de criterio (contador aparte, sin sitio todavía).
- Escaneo de secretos (patrón del pre-commit) sobre el diff completo y los archivos nuevos: 0. Ninguna
  credencial existe en la máquina.
- Árbol: 45 archivos modificados y 15 rutas nuevas, **sin commit** (el commit lo decide Nicolás a la mañana
  con los dictámenes a la vista). `senales.db` intacta (sha `29692499…`, mtime 8-sep 18:15:30). Archivos
  protegidos idénticos a HEAD (guardián). `dinero/sello_dinero.db` (gitignorada) con 33 filas; su export y
  la extensión están en `data/backups/`, que el job de backup de las 18:40 commitea.
- **Errores propios detectados:** en el acta §85.8.
- **Lo que queda para la próxima corrida:** bloque 6 (README inglés, con generador y guardias primero);
  E1 cuando exista cuenta de práctica y gateway (y en horario de mercado); la distribución de k bajo la
  nula (§56); regenerar `bifurcaciones` con 4.000 cuando toque; `visible_en` en el sellador (Z1).
- **Firmas nuevas abiertas:** §51 a §57, y §43 vuelve con la pregunta exacta. **No iniciado del
  encargo:** bloque 6 (declarado con su razón). **No hagas push:** no se hizo.
