# Auditoría de fuga — `dinero/sello_dinero.py` (E0, sellador prospectivo) + `tests/test_sello_dinero.py`

**Fecha de `date`: 2026-09-09 00:14:34 −03 (03:14:34Z).** Rama main, árbol con cambios sin commitear.
Nada escrito en el repo: bases temporales, `data/backups/sello_dinero.csv` sin existir (verificado con `ls`).
Archivado tal cual por el orquestador; la aplicación de E1–E8 y la re-verificación están en `bitacora_12.md`, bloque 3.

## FUGAS DEMOSTRADAS

**H1 (BLOQUEANTE) — el gate que corre ANTES del sello real es VACUO.** `cortes = [d for d in cierres.index if d >= dia][:futuros+1]`; `main()` lo invoca con `dia = cierres.index.max()`, así que la lista tiene UN elemento y compara la decisión consigo misma. Reproducción: monkeypatch de `S.decidir` con la MISMA fuga que el test inyecta, gate en el último día → `{'resultado': 'INVARIANTE', 'cortes': 1}`. El test lo caza en 2026-08-20 (cortes=6) y NO en el único día que importa.

**H2 (BLOQUEANTE, fuga de disponibilidad/reproducibilidad)** — la decisión de D depende del NÚMERO de sesiones entre DESDE y D (`senales_sin_informacion` avanza un rng por sesión). Medido: precios intermedios ×1,5 → decisión idéntica; sin la sesión 2026-08-28 → 33/33 filas cambian, 2 decisiones; sin la sesión 2023-09-06 (hace 3 años) → ídem. No es fuga de futuro; ES fuga de disponibilidad: si la fuente repone una sesión, la fila deja de ser reproducible desde una descarga nueva, y el sha sólo la salva si `ext_*.csv` sobrevive — y NINGÚN job lo versionaba.

**H3 (BLOQUEANTE, calendario/disponibilidad) — publicación asincrónica.** Extensión con 2 sesiones donde sólo NVDA publica la segunda: `available_at` = el máximo, `insumo_fresco=True`, `cuenta_para_N=1`, 32 filas con precio NULL cuyo `motivo` dice «su intervalo contiene el cero». El `max` es la cota correcta para la emisión e INCORRECTA para la completitud; la fila miente sobre por qué no operó.

**H4 (BLOQUEANTE, huso/calendario)** — `fecha_sello_local` era una fecha de CHILE (`ahora.astimezone()`, TZ del proceso) contrastada contra el calendario de NUEVA YORK. Sábado 12-sep 00:30 Chile == viernes 11-sep 23:30 NY → `dia_sin_sesion`, `cuenta_para_N=0`; viernes 20:30 Chile → `pendiente`, `cuenta_para_N=1`. Misma información, mismo objetivo, distinto conteo por una hora de reloj. Bajo systemd sin TZ heredada, UTC mueve el corte otra vez.

**H5 (auditabilidad)** — un segundo sello del mismo `fecha_insumo` con OTRA extensión (otro sha, otras decisiones: KLAC 0→1) se descartaba en silencio Y `sellar` devolvía un resumen que afirmaba haber sellado con un sha ausente de la base.

**H6 (revisión silenciosa, medida, no corregida)** — un split 2:1 en la extensión desalinea `precios_ref` (NVDA 230,36 → 115,18) y mueve el dimensionamiento; membresía y señal son inmunes. El solape extensión∩congelado, única evidencia, se descartaba antes del sha.

**H7 (auditabilidad)** — la fila no sellaba: sha de `reglas.json`, `available_at` POR ticker, `riel_apagado`, nombre del archivo de extensión, huella del código del sellador.

**H8 (footgun)** — `exportar=True` por defecto con ruta fija: sellar contra una base temporal sobrescribía el CSV versionado real.

## SOSPECHAS SIN DEMOSTRAR

S1 `ts_emision` se estampa al entrar y no hay `visible_en` (Z1). S2 `estado` colapsaba `dia_sin_sesion` y `no_verificable_timing`. S3 estabilidad del orden de `tickers` si la membresía cambiara.

## VERIFICADO LIMPIO

V1 invariancia al borrado del futuro, 35 días + bordes de feriado, 5 cortes cada uno: sin fallas; con congelado+extensión: idéntica. V2 `proxima_sesion_despues_de` en los cuatro bordes (apertura exacta → siguiente; un segundo antes; fin de semana; feriado del 7-sep). V3 `available_at` es de calendario. V4 inmutabilidad (triggers). V5 aislamiento: `test_dinero.py` 40 passed; `version.py` leído por texto; api sólo llama `estado()`. V6 `test_sello_dinero.py` 11 passed, 1 skipped; `tests/test_motor.py` OK.

## ZONAS CIEGAS

Z1 sellado (`visible_en`). Z2 point-in-time (yfinance ajustado). Z3 fuga por el analista (`reglas.json`, semilla, DESDE, N=40 los fijó quien ya vio la ventana; la única defensa es el sello en vivo). Z4 fuga por el propio modelo: no aplica hoy (sorteo declarado). Z5 el camino de red no se auditó (prohibido descargar).

## VEREDICTO POR EXIGENCIA

A LIMPIO (pero la guarda no corría, H1). B DEMOSTRADO (H2). C `available_at` de calendario; `max` incorrecto para completitud (H3). D LIMPIO. E MEDIDO (H6). F sin sesión no cuenta (correcto); frescura no por ticker (H3); huso equivocado (H4). G silencio (H5). H faltan campos (H7). I LIMPIO.

## EXIGENCIAS ANTES DEL PRIMER SELLO (bloqueantes)

- **E1** gate no vacuo: `cortes >= 2` o reventar. (H1)
- **E2** `cuenta_para_N` sin reloj de pared ni huso del host. (H4)
- **E3** disponibilidad POR TICKER en la fila y motivo «sin dato en el insumo»; un día incompleto no cuenta para N. (H3)
- **E4** segundo sello con otro sha → rastro explícito; `sellar` no devuelve estados de un INSERT que no ocurrió. (H5)
- **E5** versionar `ext_*.csv` + meta (o exportarlos a `data/backups/`); `exportar` no escribe el CSV real desde una base arbitraria. (H2, H8)

## PUEDEN ESPERAR

E6 sha de `reglas.json` y huella del código. E7 solape extensión∩congelado en el meta. E8 separar `estado_timing` de `estado_dia`. E9 `visible_en`.

**NO SE SELLA HASTA que E1 a E5 estén implementadas y verdes.**

---

## Re-verificación (mismo auditor, 00:33–00:47 −03, sobre E0.2)

Sin red, sin escrituras en el repo. Por exigencia, ejecutando:

- **E1 RESUELTO.** Gate en el último día → `ErrorLookAhead` «gate VACUO: sólo 1 corte(s) … (mínimo 2)». `gate_previo_al_sello` → cortes [2, 6]. **Contraprueba que faltaba:** reinyectada la misma fuga de H1, `gate_previo_al_sello` ahora la ve («la decisión de 2026-09-02 cambia según exista o no lo posterior…»); en E0.1 pasaba en silencio. Los campos nuevos de E3 no entran en `huella_decision`, pero se verificaron invariantes al truncar aparte (sólo datos ≤ día).
- **E2 RESUELTO.** Sábado 00:30 Chile (= viernes 23:30 NY) y viernes 20:30 Chile dan `fecha_sello 2026-09-11`, `sesion`, N=1 los dos; sábado 12:00 NY → `dia_sin_sesion`, N=0. `ahora_utc` naive → ValueError. Determinista desde `timestamp_utc`: reproducible por un tercero sin conocer el huso de la máquina.
- **E3 RESUELTO.** Extensión con 2 sesiones y sólo NVDA publicando la segunda: `insumo_incompleto`, N=0, `sin_dato` 32; fila AMAT con motivo «sin dato en el insumo para la sesión 2026-09-09 (último cierre: 2026-09-08)» y `available_at_ticker` propio.
- **E4 RESUELTO.** Mismo sha → `ya_sellada` sin estado ni cuenta_para_N inventados; otro sha → `divergencia_registrada` (1 decisión distinta), 33 filas intactas, 1 fila en `divergencias_sello`, tabla inmutable probada.
- **E5 RESUELTO.** Tras ~8 sellos contra bases temporales `RUTA_BACKUP_CSV` sigue sin existir; `exportar_csv(base_temporal)` sin ruta → ValueError; `respaldar_extension` copia csv + meta.
- E6/E7/E8 verificados: sha de reglas y del sellador en la fila; split 2:1 sintético detectado (`tickers_con_reajuste=['NVDA']`); `estado_timing`/`estado_dia` separados.
- Regresión: `test_sello_dinero.py` 17 passed / 1 skipped; `test_dinero.py` 40 passed (incluye el aislamiento sobre E0.2); `tests/test_motor.py` OK; barrido propio de 28 días con bordes de feriado, 5 cortes cada uno: sin fallas.

**Sigue abierto, declarado (no bloqueante):** H2 residual (la decisión depende del número de sesiones desde DESDE; mitigado por sha + respaldo, sin gate propio); Z1 (`visible_en`); Z2 (yfinance ajustado: E7 detecta, no corrige); Z3 (analista: reglas, semilla, DESDE, N = 40 fijados por quien ya vio la ventana — la única defensa es el sello en vivo).

**SE PUEDE SELLAR.**

## Primer sello (orquestador, 00:38:17 −03)

`python -m dinero.sello_dinero --sellar`: gate previo INVARIANTE ([2, 6] cortes); **aviso E7: reajuste retroactivo detectado en WDC** (dif. rel. máx. 3,2 × 10⁻⁴ sobre 29 sesiones de solape 2026-07-28 a 2026-09-04; declarado en el meta, no corregido); 33 filas selladas, `timestamp_utc 2026-09-09T03:38:17Z`, `available_at 2026-09-08T20:00:00Z` (cierre por calendario), objetivo 2026-09-09 13:30Z, `pendiente`, insumo fresco y completo, `cuenta_para_N = 1`; 0 compras (la sonda del 8-sep no cruzó el umbral en ningún instrumento). `senales.db` idéntica antes y después (sha256 `29692499…`, mtime 18:15:30 del 8-sep).
