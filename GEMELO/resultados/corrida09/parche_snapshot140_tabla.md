# Parche `snapshot.py:140` como parche NO aplicado: cuantificación (corrida 09, frente 2b)

**Fecha:** 3-sep-2026, 00:30 Chile. **HEAD:** `067ce164b835554b3b7008b8fb5cedacf36b180f`.
**Estatus del parche:** PROPUESTA, no aplicado. `snapshot.py` no fue editado
(`git status --short snapshot.py` vacío; la línea 140 sigue diciendo
`proxima_sesion_despues_de(exchange, ahora_utc)`).
**Base:** `senales.db` leída en `mode=ro`, todas las filas de `senales_ticker`
con predicción (`apertura_estimada_pct` no nulo), `modelo_version = 4.6.0`,
hasta el sello del 2-sep-2026 (22:15:03 UTC). Cero intentos del DSR: no se
evalúa ninguna hipótesis sobre retornos.

## 0. Los tres entregables y cómo se verificaron

| Entregable | Estado | Verificación |
|---|---|---|
| `GEMELO/propuestas/parches/snapshot140.diff` (1,4 KB, un hunk, una expresión) | listo | `git apply --check` rc=0 y `patch -p1 --dry-run` limpio contra el `snapshot.py` de HEAD. No se aplicó. |
| `tests/test_parche_snapshot140.py` (6 tests) | VERDE con `snapshot.py` sin parchear | `python -m pytest tests/test_parche_snapshot140.py -q` → `6 passed in 3.63s`. Copia a `tmp_path`, `patch -p1` sobre la copia, `importlib` bajo `snapshot_parcheado`, `calendarios` real, `senales.DB_PATH` apuntado a una base temporal con guardia; `senales.db` real no cambió de mtime (18:15:28 del 2-sep, el sello del día). |
| esta tabla | MEDIDO | script de solo lectura sobre `senales.db` (`mode=ro`) con `backtest.linea_base.sesion_correcta` y `calendarios.apertura_utc` / `cierre_utc`. |

El agente anterior (muerto por límite de API a las 23:53) dejó el diff y el
test completos; los dos se verificaron línea a línea y se conservan sin
cambios. Lo que faltaba era esta tabla y el informe.

**Enfoque del test, en una frase:** se ejecuta `ejecutar_snapshot` ENTERA en
las dos versiones (original y copia parcheada) con el motor reemplazado por
valores fijos (sin red), el reloj de pared fijado por una subclase de
`datetime` inyectada en el módulo bajo prueba, y la base temporal; extraer
sólo la expresión habría probado el calendario, no que la línea reciba el
`available_at` que la propia función calcula en `:123-135`.

## 1. Método (MEDIDO)

Para cada una de las **295** filas con predicción 4.6.0 (todas con
`exchange`, `sesion_objetivo`, `available_at` y `timestamp_utc` no nulos: 0
inevaluables) se recomputó `sesion_correcta(exchange, available_at)` (la
fórmula que el parche instala) y se comparó con la `sesion_objetivo` sellada.
Para cada discrepancia se leyó de `verificacion_apertura` (`legacy = 0`, una
fila por predicción en los 25 casos) `acierto_gap` y `gap_pct`, y se declaró
qué habría pasado bajo el parche: (i) sesión a la que apuntaría; (ii) si esa
sesión ya había abierto al emitir (`timestamp_utc >= apertura_utc(exchange,
sesion_correcta)`), que es la regla maestra del verificador
(`senales.verificar_apertura_pendientes`) y da `no_verificable_timing`. **No
se recomputó ningún acierto contra la sesión correcta.**

## 2. Las 25 filas (MEDIDO, censo, sin intervalo porque no hay muestreo)

Columnas: emisión (`fecha`), ticker, exchange, `timestamp_utc`, `available_at`
(cierre XNYS del SOX usado), sesión sellada, sesión correcta, estado actual,
`acierto_gap`, `gap_pct` (contra la sesión sellada, el dato que hoy cuenta),
apertura UTC de la sesión correcta, y bajo el parche.

| emisión | ticker | exch | timestamp_utc | available_at | sellada | correcta | estado | ac | gap_pct | apertura correcta (UTC) | bajo el parche |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-05 | 000660.KS | XKRX | 07-05 10:06:05 | 07-02 20:00 | 07-06 | **07-03** | verificada | 0 | +1.0309 | 07-03 00:00 | `no_verificable_timing` (sesión ya CERRADA) |
| 2026-07-05 | 005930.KS | XKRX | 07-05 10:06:05 | 07-02 20:00 | 07-06 | **07-03** | verificada | 0 | +3.3926 | 07-03 00:00 | `no_verificable_timing` (cerrada) |
| 2026-07-05 | 2330.TW | XTAI | 07-05 10:06:05 | 07-02 20:00 | 07-06 | **07-03** | verificada | 0 | +0.8180 | 07-03 01:00 | `no_verificable_timing` (cerrada) |
| 2026-07-05 | 3436.T | XTKS | 07-05 10:06:05 | 07-02 20:00 | 07-06 | **07-03** | verificada | 1 | −0.1178 | 07-03 00:00 | `no_verificable_timing` (cerrada) |
| 2026-07-05 | 4063.T | XTKS | 07-05 10:06:05 | 07-02 20:00 | 07-06 | **07-03** | verificada | 0 | +1.4372 | 07-03 00:00 | `no_verificable_timing` (cerrada) |
| 2026-07-05 | 6857.T | XTKS | 07-05 10:06:05 | 07-02 20:00 | 07-06 | **07-03** | verificada | 0 | +1.7039 | 07-03 00:00 | `no_verificable_timing` (cerrada) |
| 2026-07-05 | 8035.T | XTKS | 07-05 10:06:05 | 07-02 20:00 | 07-06 | **07-03** | verificada | 0 | +1.2158 | 07-03 00:00 | `no_verificable_timing` (cerrada) |
| 2026-07-05 | IFX.DE | XETR | 07-05 10:06:05 | 07-02 20:00 | 07-06 | **07-03** | verificada | 1 | −1.6929 | 07-03 07:00 | `no_verificable_timing` (cerrada) |
| 2026-07-29 | 000660.KS | XKRX | 07-30 01:23:34 | 07-29 20:00 | 07-31 | **07-30** | verificada | 0 | +28.3661 | 07-30 00:00 | `no_verificable_timing` (abierta 1 h 23 antes) |
| 2026-07-29 | 005930.KS | XKRX | 07-30 01:23:34 | 07-29 20:00 | 07-31 | **07-30** | verificada | 0 | +24.1546 | 07-30 00:00 | `no_verificable_timing` |
| 2026-07-29 | 2330.TW | XTAI | 07-30 01:23:34 | 07-29 20:00 | 07-31 | **07-30** | verificada | 0 | +6.5760 | 07-30 01:00 | `no_verificable_timing` (abierta 23 min antes) |
| 2026-07-29 | 3436.T | XTKS | 07-30 01:23:34 | 07-29 20:00 | 07-31 | **07-30** | verificada | 0 | +17.5214 | 07-30 00:00 | `no_verificable_timing` |
| 2026-07-29 | 4063.T | XTKS | 07-30 01:23:34 | 07-29 20:00 | 07-31 | **07-30** | verificada | 0 | +2.7971 | 07-30 00:00 | `no_verificable_timing` |
| 2026-07-29 | 6857.T | XTKS | 07-30 01:23:34 | 07-29 20:00 | 07-31 | **07-30** | verificada | 0 | +16.4847 | 07-30 00:00 | `no_verificable_timing` |
| 2026-07-29 | 8035.T | XTKS | 07-30 01:23:34 | 07-29 20:00 | 07-31 | **07-30** | verificada | 0 | +13.3997 | 07-30 00:00 | `no_verificable_timing` |
| 2026-08-03 | 2330.TW | XTAI | 08-04 02:57:44 | 08-03 20:00 | 08-05 | **08-04** | verificada | 1 | +2.8017 | 08-04 01:00 | `no_verificable_timing` (abierta 1 h 57 antes) |
| 2026-08-03 | 3436.T | XTKS | 08-04 02:57:44 | 08-03 20:00 | 08-05 | **08-04** | verificada | 1 | +6.5444 | 08-04 00:00 | `no_verificable_timing` |
| 2026-08-03 | 4063.T | XTKS | 08-04 02:57:44 | 08-03 20:00 | 08-05 | **08-04** | verificada | 1 | +0.2839 | 08-04 00:00 | `no_verificable_timing` |
| 2026-08-05 | 000660.KS | XKRX | 08-06 01:38:52 | 08-05 20:00 | 08-07 | **08-06** | verificada | 0 | +1.7391 | 08-06 00:00 | `no_verificable_timing` (abierta 1 h 38 antes) |
| 2026-08-05 | 005930.KS | XKRX | 08-06 01:38:52 | 08-05 20:00 | 08-07 | **08-06** | verificada | 0 | +1.9523 | 08-06 00:00 | `no_verificable_timing` |
| 2026-08-05 | 2330.TW | XTAI | 08-06 01:38:52 | 08-05 20:00 | 08-07 | **08-06** | verificada | 0 | +1.0571 | 08-06 01:00 | `no_verificable_timing` (abierta 38 min antes) |
| 2026-08-05 | 3436.T | XTKS | 08-06 01:38:52 | 08-05 20:00 | 08-07 | **08-06** | verificada | 0 | +4.5429 | 08-06 00:00 | `no_verificable_timing` |
| 2026-08-05 | 4063.T | XTKS | 08-06 01:38:52 | 08-05 20:00 | 08-07 | **08-06** | verificada | 0 | +0.5351 | 08-06 00:00 | `no_verificable_timing` |
| 2026-08-05 | 6857.T | XTKS | 08-06 01:38:52 | 08-05 20:00 | 08-07 | **08-06** | verificada | 1 | −0.0607 | 08-06 00:00 | `no_verificable_timing` |
| 2026-08-05 | 8035.T | XTKS | 08-06 01:38:52 | 08-05 20:00 | 08-07 | **08-06** | verificada | 0 | +1.8073 | 08-06 00:00 | `no_verificable_timing` |

Origen de los sellos: 07-05 `manual` (`plataforma_version` NULL, pre 5.0);
07-29 `programado` 5.0.0; 08-03 y 08-05 `programado` 5.0.1. Los `gap_pct` de
+13 a +28 pp del grupo 07-29 (sesión sellada 07-31, XKRX/XTKS) son los
valores que `verificacion_apertura` tiene sellados; no se investigaron aquí
(cabo suelto anotado, fuera del frente).

## 3. Totales (MEDIDO)

| | n |
|---|---|
| filas con predicción 4.6.0 auditadas | 295 (todas evaluables) |
| filas cuya `sesion_objetivo` difiere de `sesion_correcta` | **25** |
| fechas de emisión afectadas | 4 (07-05: 8, 07-29: 7, 08-03: 3, 08-05: 7) |
| exchanges afectados | XKRX 6, XTAI 4, XTKS 14, XETR 1 (XNYS: 0, abre después de cualquier hora de sello observada) |
| hoy `estado = verificada` | 25 de 25 |
| con fila en `verificacion_apertura` y `gap_pct != 0` (cuentan en `excluir_cero`) | 25 de 25 |
| `acierto_gap` sellado (contra la sesión equivocada) | 6 aciertos, 19 errores |
| bajo el parche, apuntarían a la sesión correcta | 25 de 25 |
| bajo el parche, `no_verificable_timing` (sesión correcta ya abierta al emitir) | **25 de 25** |
| de ellas, sesión correcta ya CERRADA al emitir | 8 (las del 07-05) |
| bajo el parche, verificables contra la sesión correcta | **0** |

**Qué es "en métricas" según la rama:** en la rama sin deduplicar (README
publicado) cuentan las 25. Con la regla firmada (`cargar(dedup=True)`, n=238)
ya salen las 10 del lado viejo de los pares y quedan **15** contando; con la
coherencia (`filtrar_sesion_coherente`, no aplicada, n=223) quedan 0. Es la
misma resta 238 − 223 = 15 que documenta la cola §2a-ter.

**Cruce con la cola de decisiones (§1-bis, §2a, §2a-ter) y con el
expediente (§4):** hoy el número **sigue siendo 25** (10 del lado viejo de
los pares de 07-31 y 08-05, 15 sin pareja de 07-05 y 08-05), ninguna fila
nueva desde el 5-ago: los 20 sellos posteriores (06-ago a 02-sep, todos
`programado`) tienen `timestamp_utc` entre 22:15 y 23:45 UTC (los más tardíos:
10-ago 23:45, 21-ago 23:41), antes de la primera apertura asiática de las
00:00 UTC, así que ninguno cruzó una sesión. Los 15 pares por `(ticker, sesion_objetivo)` son los mismos 10 del
defecto + 5 de feriado real (12-ago, 18-ago), y esos 5 no aparecen en la
lista: coincide con la cola. Los 25 siguen `verificada`; en la base no hay
hoy ninguna fila en `no_verificable_timing` (estados 4.6.0: 284 verificada,
9 pendiente, 2 sin_datos_mercado).

**Lo que la tabla corrige de la cola (§2a-ter y expediente §6):** allí se
dice que bajo el ancla correcta serían **15** las que pasan a
`no_verificable_timing` (las sin pareja). Medido, son **las 25**: las 10 del
lado viejo de los pares también se emitieron después de la apertura de su
sesión correcta (01:23 UTC contra 00:00/01:00 del 30-jul; 02:57 contra
00:00/01:00 del 4-ago). Para las cifras publicadas no cambia nada (esas 10
ya están fuera por la regla firmada), pero cambia la lectura: **el parche no
rescata ninguna de las 25 como predicción verificable**.

**Y no es casualidad, es construcción (PROPUESTA de lectura, verificable
en el código):** `sesion_objetivo` sellada es la primera sesión que abre
después de `ahora_utc`; la correcta es la primera que abre después de
`available_at`, y `timestamp_utc = ahora_utc` (`snapshot.py:111-112`, la
misma variable). Difieren si y sólo si alguna sesión abrió en
`(available_at, ahora_utc]`, y la primera de ésas es justamente la correcta,
que entonces abrió antes o en el instante de emisión: la regla maestra la
declara `no_verificable_timing`. Es decir: **toda fila que el defecto
desplaza es, bajo el ancla correcta, una emisión tardía por definición.** El
parche no cambia el conteo de aciertos hacia adelante; cambia que una
emisión tardía quede etiquetada como tal (auditable, fuera de métricas) en
vez de verificada contra una sesión que no era la suya. El test
`test_fijacion_sello_tardio_la_regla_maestra_lo_deja_fuera` fija exactamente
este efecto con el calendario real.

## 4. Qué espera firma (DECISIÓN PENDIENTE, de Nicolás)

1. **Aplicar el diff** (`git apply GEMELO/propuestas/parches/snapshot140.diff`
   desde la raíz; verificado que aplica limpio contra HEAD `067ce16`). Nada
   de esto lo hace un agente: `snapshot.py` está en la ruta de sellado.
2. **Marcar el corte de método**, una de dos: (a) bump de
   `PLATAFORMA_VERSION` en `version.py` (hoy `5.0.3`) en el mismo commit, con
   lo que cada fila de `snapshots.plataforma_version` documenta el lado del
   corte para siempre; o (b) sin bump, anotar en el acta el `timestamp_utc`
   exacto del primer sello posterior (leído de `snapshots`, no de memoria).
   Recomendación marcada como tal: (a).
3. **La copia de insumos** (`GEMELO/INSUMOS/`, probada, no activada) que la
   cola §17 recomienda activar **en el mismo bump**: sólo se referencia aquí;
   no forma parte de este diff ni de este test.
4. Correr la suite completa después de aplicar y ANTES del sello de esa
   noche (`./mki tests`); la contraprueba de `tests/test_parche_snapshot140.py`
   se salta sola con motivo cuando el parche ya está aplicado.
5. Las 25 filas selladas **no se tocan** (Constitución 5.0, punto 3). Su
   tratamiento en métricas sigue siendo la decisión abierta de la cola
   §2a-ter (las 15 sin pareja), que este frente no resuelve.

## 5. Declaración del corte de método, lista para acta

```
## <fecha de aplicación> — Corte de método en `sesion_objetivo` (parche snapshot.py:140)

**Qué se decidió.** `sesion_objetivo` se calcula desde `available_at` (cierre
UTC de la sesión del SOX usada) y no desde el reloj de pared del proceso.
Diff: GEMELO/propuestas/parches/snapshot140.diff, aplicado el <fecha> a
<hora Chile>. Marcador del corte: plataforma_version >= <nueva versión>
[o: primer sello con la semántica nueva, timestamp_utc = <leído de snapshots>].

**Por qué.** Medido sobre senales.db al 2-sep-2026 (n = 295 filas con
predicción 4.6.0): 25 filas selladas (4 fechas de emisión: 07-05, 07-29,
08-03, 08-05) apuntan a la sesión siguiente a la que su available_at
sostiene, porque el sello cruzó la apertura asiática o europea. Las 25 están
hoy `verificada` y cuentan en la rama publicada; bajo el ancla correcta las 25
son emisiones tardías por construcción (la sesión correcta había abierto, en
8 casos cerrado, al emitir) y la regla maestra las deja fuera de métricas
como `no_verificable_timing`. El defecto sigue activo mientras no se aplique:
cada sello que se atrase produce filas nuevas con el mismo error.

**Qué significa la columna a cada lado del corte.** ANTES: "primera sesión
del exchange cuya apertura es posterior al reloj de pared al llegar a :140";
coincide con la sesión anticipada sólo cuando el sello no cruza una apertura.
DESPUÉS: "primera sesión del exchange cuya apertura es posterior a
available_at", invariante al atraso del proceso, que es la definición que la
regla maestra de CLAUDE.md ya daba por cierta. `timestamp_utc` no cambia de
significado: sigue siendo el instante real de emisión.

**Cómo se tratan las filas de cada lado.** Ningún análisis mezcla
`sesion_objetivo` de antes y de después como la misma medida sin declararlo
(misma disciplina que entre modelo_versions). Las 25 filas viejas quedan
selladas tal cual; available_at sigue en ellas y permite recomputar la sesión
correcta (backtest/linea_base.sesion_correcta) cuando un análisis lo
necesite. Un cambio de sesión entre dos sellos que rodean el corte por la
fórmula nueva no es una anomalía de datos: es este corte operando.

**Qué se descartó y por qué.** Reescribir las 25 filas (prohibido por la
Constitución 5.0). Anclar en `timestamp_utc` en vez de `available_at`
(reproduce el defecto en el caso del 06-ago, donde el proceso se congeló
entre estampar ts y llegar a :140). Corregir el estado de las 25 a
`no_verificable_timing` (es reescritura de fila sellada; se declara en la
cola §2a-ter y en esta acta, no en el dato).

**Qué queda abierto.** Las 15 filas sin pareja en métricas (cola §2a-ter). La
copia de insumos (cola §17). Un test o chequeo del vigía que detecte solo
sesiones incoherentes en filas nuevas (propuesto en tests/test_epistemico.py,
quinta corrida).

**Cómo se revierte.** `git revert` del commit del parche y un segundo corte
declarado con la misma forma. Las filas selladas con la semántica nueva no
se reescriben tampoco.
```

## 6. Cierre del frente

- **Archivos creados/modificados por este agente:** sólo
  `GEMELO/resultados/corrida09/parche_snapshot140_tabla.md` (este archivo).
  `GEMELO/propuestas/parches/snapshot140.diff` y
  `tests/test_parche_snapshot140.py` los dejó el agente anterior; se
  verificaron y se conservan sin cambios. `snapshot.py`, `senales.db`,
  `version.py`: sin tocar.
- **Intentos del DSR consumidos:** 0.
- **Abierto:** los puntos de §4; los `gap_pct` de 13 a 28 pp del 07-29
  (anotados, no investigados).
- **Errores propios corregidos:** ninguno en este relanzamiento; el
  relanzamiento mismo existe porque el agente anterior murió sin escribir
  esta tabla.
