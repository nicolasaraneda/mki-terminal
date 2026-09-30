# Informe del implementador del bloque 1 (corrida 15) — archivado por el orquestador

> Resumen fiel del informe que devolvió el agente implementador (worktree `wt15`, HEAD `2f73eb2`),
> con las tablas y los hallazgos completos. Horas leídas de `date` por el agente: inicio 22:11:52;
> tests sobre HEAD 22:25:32; correcciones 22:26 a 22:28; árbitro antes 22:25:04 y después 22:28:44;
> corte de cuota ~22:43; reanudación 23:02:27; última corrida de tests 23:03:28 a 23:04:01. Ningún
> test entre 00:15 y 00:50. Nada tocado en el árbol real. Bases: sha256 de `senales.db`,
> `noticias.db` y `dinero/sello_dinero.db` idénticos antes y después. Evidencia en
> `evidencia/` (`pytest_HEAD.txt`, `pytest_NUEVO.txt`, `anclas_detalle.txt`, `orden.txt`,
> `compara_arbitro.py`).

## Archivos

Modificados: `senales.py` (+40), `snapshot.py` (+32), `backtest/linea_base.py` (+166),
`tests/test_autonomia.py` (+18, vecino: ver H1). Creado: `tests/test_conocibilidad.py` (28 tests).
No tocados: `motor.py`, `universo.py`, `mki_vigia.py`, `dinero/`, `GEMELO/sonda_cierre*.py`,
`data/sonda_cierre.csv`, `cifras.py`, `calendarios.py`, systemd.

## Tests de reproducción: 12 de 28 rojos sobre HEAD, 28 verdes con las correcciones

- **1.1** `test_reproduccion_el_verificador_no_verifica_una_fila_con_la_inversion`, HEAD:
  `AssertionError: la fila con available_at (2026-09-28T20:00:00+00:00) posterior a su timestamp_utc
  (2026-09-28T17:42:58.943983+00:00) quedó en estado 'verificada': el verificador la procesó como
  válida`. Complemento `test_la_guarda_compara_instantes_y_no_texto` (un `available_at` con zona
  `-04:00` ordena antes como texto y después como instante). Controles: NULL e igualdad no disparan;
  filas `verificada` o sin estado con la inversión no cambian; `_ohlc_local` no se llama.
  `test_corte_de_metodo_las_filas_del_evento_no_se_tocan`: copia de la base real a `tmp_path`,
  volcado de las filas de `2026-09-28` en `senales_ticker` y `verificacion_apertura` antes y después
  de correr el verificador nuevo con la red parcheada: `repr` idéntico; la base real con el mismo
  tamaño y mtime.
- **1.2** `test_reproduccion_no_sella_con_la_sesion_del_sox_abierta`, HEAD: `snapshot.py selló a las
  2026-09-28T17:42:58.943983+00:00 con sox_fecha=2026-09-28, cuya sesión cierra a las
  2026-09-28T20:00:00+00:00`. Con el cambio: `guardar_snapshot` no se llama y el motivo dice «no ha
  cerrado». `test_sella_a_las_1815_de_chile_del_mismo_dia` (aserción SELLA escrita antes del código,
  verde en HEAD y ahora). `test_sella_a_las_1815_de_chile_en_todos_los_husos_del_anio` (15-jul,
  15-ene, 16-mar, 5-nov). `test_el_margen_cero_nunca_frena_al_job_y_el_de_dos_horas_si`: 251 sesiones
  XNYS de 2026, holgura mínima 15 min (84 sesiones), 75 min (58), 135 min (107), 195 min (2); **con
  margen de 2 h no sellarían 142 de 251**. `test_el_motivo_nuevo_no_entra_al_bucle_de_reintentos`:
  `main()` entera con todo parcheado, una sola llamada, sin esperas. La rama del `except` y
  `sox_fecha = None` siguen sellando con `available_at == timestamp_utc`.
- **1.3** `test_reproduccion_la_medicion_deja_fuera_la_fila_con_la_inversion` (sintética) y
  `test_reproduccion_la_medicion_no_trae_filas_invertidas_de_la_base_real` (HEAD: `cargar(dedup=False)`
  entrega 8 filas con `available_at > timestamp_utc`, las del 28-sep).
  `test_la_exclusion_corre_antes_que_la_deduplicacion` (HEAD conservaba la inválida que «calza» y
  retiraba la válida). Test A: conjunto por regla igual al de `WHERE available_at > timestamp_utc`
  (24 filas, 1 fecha, 8 con verificación, pinchado al corte 2026-09-29). Test B: sintética sin
  inversiones alcanza 0. El módulo no contiene `2026-09-28` ni `28-sep`. Las ventanas congeladas
  (cortes 24-ago, 31-ago, 28-ago × dedup) son `.equals()` con y sin la regla.

## 1.4: DETENIDO, la línea 163 no se tocó

Base real en `mode=ro`, 439 filas con `sesion_objetivo`, no legacy, `fecha <= 2026-09-29`. **33 filas
difieren entre las dos anclas, en 5 fechas.** El ancla de emisión reproduce la `sesion_objetivo`
sellada en 439 de 439; el ancla de `available_at` difiere de la sellada en esas mismas 33. En las 33,
la sesión que elige el ancla `available_at` YA HABÍA ABIERTO al instante de emisión (la regla maestra
las habría dejado `no_verificable_timing`); con el ancla de emisión son `verificada` y todas están hoy
en `verificacion_apertura`. Las 8 filas invertidas del 28-sep NO difieren. Test permanente
`test_historia_las_dos_anclas_difieren_y_por_eso_la_linea_no_se_toco` (pinchado al corte).

| fecha | tickers | timestamp_utc | available_at | sesión ancla `available_at` | ancla emisión = sellada | familia |
|---|---|---|---|---|---|---|
| 2026-07-05 | 000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T, IFX.DE | 05T10:06:05Z | 02T20:00Z | 2026-07-03 | 2026-07-06 | (B) sello manual de domingo con el SOX del jueves 2 (feriado NYSE el 3) |
| 2026-07-29 | 000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T | 30T01:23:34Z | 29T20:00Z | 2026-07-30 | 2026-07-31 | (A) sello tardío que cruzó la apertura asiática |
| 2026-08-03 | 2330.TW, 3436.T, 4063.T | 04T02:57:44Z | 03T20:00Z | 2026-08-04 | 2026-08-05 | (A) |
| 2026-08-05 | 000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T | 06T01:38:52Z | 05T20:00Z | 2026-08-06 | 2026-08-07 | (A) |
| 2026-09-07 | 000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T, IFX.DE | 07T21:15:03Z | 04T20:00Z | 2026-09-07 | 2026-09-08 | (C) feriado de NYSE (Labor Day), `sox_fecha` 4-sep |

En 29-jul, 3-ago y 5-ago IFX.DE no difiere (XETR abre 07:00 UTC, después del sello tardío); el 3-ago
sólo 4 filas tienen `sesion_objetivo`. Lectura para Nicolás, no decisión: con la guarda (b)
`available_at <= emisión` siempre, así que anclar en `available_at` ya no puede anclar en el futuro;
las dos anclas sólo difieren cuando la emisión es posterior a la apertura de la sesión que sigue a
`available_at` (sello tardío o feriado de NYSE). Ahí, ancla `available_at` = fila no verificable
(se pierde, nunca cuenta un insumo viejo); ancla emisión = fila verificable con insumo viejo y par
duplicado con la fila del día siguiente (lo que §84.1 desarmó y la deduplicación arbitra). El
comentario de `snapshot.py:151-161` no se tocó.

## Censo de consumidores de `verificacion_apertura` y `verificacion_puntaje`

**Pasan por la exclusión:** `backtest/linea_base.py::cargar()` (y todo lo que opera sobre lo que
`cargar` entrega: `sesion_correcta`, `marcar_sesion`, `deduplicar_por_sesion`,
`filtrar_sesion_coherente`, `auditar_dedup`); `salud_r2_regimen_beta` (betas sí; el conteo de
regímenes de `snapshots` no, declarado); `cifras.py::sellada()` (vía `lb.cargar`; su lectura directa
de `verificacion_apertura` es un `merge` inner contra el crudo y hereda la exclusión; sus regímenes
vienen de `snapshots`); e indirectos vía `lb.cargar`: `GEMELO/bifurcaciones.py:381`,
`GEMELO/intervalo_coherencia.py`, `GEMELO/simulador/proceso.py`, `potencia_por_metrica.py`,
`GEMELO/SECUENCIAL/autocorrelacion.py`, `GEMELO/transversal.py`, `backtest/baselines.py` y los
módulos que importan `linea_base` (declarados como «pasan si cargan por `cargar()`»).

**NO pasan (lectura directa; se declaran, no se tocan):** `senales.py` `metricas_apertura` (:472),
`calibracion_intervalos` (:500), `evolucion_aciertos_apertura` (:523),
`ultimas_predicciones_apertura` (:539), `verificaciones_detalle` (:562), `analisis_puntaje_ia`
(:627), consumidos por `alertas.py` (reporte Telegram, 30 días), `api/main.py` y `app.py`: **hoy las
8 filas del 28-sep cuentan en el track record de 30 días del dashboard, la API y el Telegram.**
`senales.py:424 verificar_puntaje_pendientes` (escritor de `verificacion_puntaje`): sin guarda; las 24
filas del 28-sep entrarán ~5-oct. `GEMELO/bifurcaciones.py:916` (corte publicado 28-ago, no
alcanzada hoy) y `:1186` (conteo vivo, no pasa); `GEMELO/CONDICIONAL/condicional.py:1073`,
`verificacion_A2.py:37`, `GEMELO/SECUENCIAL/mde_desde_v6.py:97` (lecturas directas vivas);
`GEMELO/fuente_canonica.py:279` (auditoría, no métrica); `micro/rtl/referencia.py:254` (vectores de
banco de pruebas). `dinero/` no lee `verificacion_*`. Sellador y sonda no importan `senales`,
`snapshot` ni `backtest.linea_base` (comprobado por importación real).

## Cifras publicadas: idénticas

Árbitro volcado antes (22:25:04, HEAD) y después (22:28:44): `cifras.sellada()` (n = 238, 34 días,
hasta 2026-08-28, +9,7 pp, IC día [−7,2, 26,6], McNemar 0,0455), `cifras.larga()`, `doce_bloques`,
`bloques_readme_en`, `duelo` y `salud_r2_regimen_beta` en los tres cortes × dedup: idénticos clave por
clave. Sólo cambian las cifras VIVAS no publicadas: n crudo 429 → 421, n oficial 409 → 402 (una de
las 8 tiene gap 0,00 y ya caía por `excluir_cero`), acierto 66,7 → 67,2 %, ventaja +12,5 → +12,9 pp,
MAE 3,0374 → 3,0557, betas 341 → 333 pares. **Dirección del efecto, declarada:** de las 7 filas
alcanzadas con gap distinto de cero el modelo acertaba 3 (42,9 %), así que la exclusión mejora las
cifras vivas del campeón; la regla se firmó por su mérito antes de mirar esto.

## Hallazgos

- **H0** la guarda (b) tal como se firmó (`available_at > emisión`, margen cero) NO produce «un día
  con la fuente atrasada deja de sellar» (§90.1 b): `test_hallazgo_una_fuente_atrasada_pasa_la_guarda_y_sella`
  (18:15 Chile del martes 29-sep con `sox_fecha` del lunes 28 → sella). Tarjeta.
- **H1** con la guarda (b), tres tests de `tests/test_autonomia.py` pasaban a depender del reloj
  (frame sintético que termina hoy: rojos desde la medianoche de Chile hasta el cierre de NYSE cada
  día hábil; 3 de 3 rojos en simulación). Arreglo aditivo: reloj de `snapshot.py` fijo a las 23:59
  UTC de hoy en la fixture `entorno`, con su docstring.
- **H2** la guarda (b) mira sólo `sox_fecha`: un despertar con la bolsa abierta en que `^SOX` aún no
  tiene barra del día pero las acciones sí sellaría `puntaje_v0`, `regimen`, `roca_chip` y
  divergencias sobre barras intradía con `available_at < emisión`. Tarjeta (inventario de §91.5).
- **H3** el censo de arriba: `verificar_puntaje_pendientes` sin guarda; las métricas de `senales.py`
  no pasan por la exclusión. Tarjeta.
- **H4** decisiones de implementación a ratificar: exclusión antes de dedup; extensión a las betas de
  `salud_r2_regimen_beta`; `cargar()` descarta `timestamp_utc` antes de devolver.
- **H5** el verificador imprime un `AVISO verificador` por fila descartada y la cuenta en
  `no_verificables`, sin contador nuevo.
- **H6** `test_el_camino_de_sellado_no_importa_GEMELO` cazó la cadena «GEMELO» en un comentario de
  `snapshot.py` (22:43); corregido (23:03).
- **H7** `tests/test_api.py::test_paridad_roca_chip_contra_snapshot` bajó de Yahoo con la caché del
  motor fría (preexistente, sin marca `red`); declarado.
- **No hecho:** la línea 163 y su comentario (1.4 detenido); `mki_vigia.py`; `cifras.py`;
  `verificar_puntaje_pendientes` y las funciones de `senales.py` del dashboard; regenerar
  `backtest/resultados/linea_base/*.md`; el fallback del dashboard (`app.py:832` ignora el dict: con
  la guarda, abrir Streamlit con la bolsa abierta ya no sella intradía y lo reintenta en cada rerun
  mientras no exista snapshot; leído, no ejecutado).
