# Pre-registro — el juez lineal bajo D3 (novena corrida, 3-sep-2026)

**Estatus: PROPUESTA, congelado ANTES de correr `GEMELO/juez_lineal_d3.py`.**
Escrito a la 01:20 (Chile) del 3-sep-2026; `auditor-lookahead` dictamina
sobre este documento y el script antes de la primera corrida; el
`estadistico-adversario` dictamina sobre el resultado antes de que una
cifra entre a la bitácora. Ninguna cifra de este documento se edita
después de ver resultados: si el resultado contradice una expectativa, se
publica la contradicción con fecha.

## 1. Pregunta

Bajo la decisión D3 (métrica primaria del veredicto: **magnitud** —MAE
contra predecir cero, y CRPS donde haya densidad—; dirección secundaria),
¿el control lineal regularizado del pre-registro (`GEMELO/DISEÑO.md` §4.3)
supera a predecir cero, y supera al campeón 4.6.0, sobre las filas
selladas? Es el JUEZ que R1 exige antes de cualquier retador: si el lineal
no supera a predecir cero, la conclusión honesta es que los features
disponibles no traen señal de magnitud, y se publica así.

## 2. Configuraciones (declaradas; ninguna cuarta)

Las dos configuraciones agrupadas del WS2b, **sin cambios** y sin fuente
nueva (todo sale de `GEMELO/cache/`, descarga PROHIBIDA en esta corrida:
el script inutiliza `yf.download` antes de tocar nada):

| nombre | features | qué responde |
|---|---|---|
| **C1** | `sox_t`, `sox_t1` | control de INFORMACIÓN: mismo insumo que el campeón, maquinaria nueva (ridge, walk-forward expansivo, embargo 5 d) |
| **C2** | los 16 features causales de `GEMELO/features.py` disponibles hoy (SOX t y t−1, futuros ES/NQ, KRW/TWD/JPY/EURUSD, KS11/TWII/N225/GDAXI, término y cambio del VIX, ratio de crédito, régimen de vol) | ¿la información extra trae magnitud? (C2 − C1 es la pregunta) |
| CAMPEÓN | las predicciones selladas (`apertura_estimada_pct`, σ = `intervalo80_pp`/1,2816) | la vara |
| CERO | predicción 0 (sin densidad) | la vara de D3 para el MAE |
| CLIMATOLOGÍA | N(μ, σ) del gap del panel de entrenamiento hasta `fecha − embargo` (CAUSAL, recomputada por fecha de emisión) | la vara de D3 para el CRPS |

C3 (ridge por ticker) NO se corre: fue la única con p < 0,05 en el WS2b y
ese p colapsó bajo R2 (acta §32); volver a probarla sería la cuarta
variante que el DSR castiga. Si alguien la corre, N sube y se declara.

## 3. Ventana, partición, embargo (congelados)

- **Evaluación:** filas selladas 4.6.0 con `verificado_en ≤ 2026-09-02`
  (el último sello al escribir esto), convención `excluir_cero` y regla de
  deduplicación firmada (`backtest.linea_base.cargar(hasta_sello="2026-09-02", dedup=True)`).
  n esperado: el que dé la máquina (≈ 269 filas, 38 fechas); se declara
  antes de mirar y se reporta el real.
- **Entrenamiento:** panel de gaps de los 8 tickers de `MERCADOS_POR_ABRIR`
  sobre 8 años de caché, walk-forward EXPANSIVO: para cada fecha de emisión
  D se entrena con las filas cuya sesión objetivo cerró en o antes de
  D − 5 días (`cl.EMBARGO_DIAS`), `MINIMO_ENTRENAMIENTO` filas. α de la
  ridge por CV temporal dentro del entrenamiento (no cuenta al DSR).
- **R2:** la misma evaluación excluyendo las emisiones del 15 al 23-jul
  (criterio congelado, `DISEÑO.md` §6.2), aplicada TAMBIÉN a la magnitud
  (dictamen E de la octava corrida: R2 se activa sobre MAE y CRPS).

## 4. Métricas por fila y estadístico (declarados)

Para cada fila (fecha de emisión, ticker) con gap g y predicción p:

- **MAE (primaria):** m = |g| − |p − g|. Positivo = la predicción reduce el
  error absoluto frente a predecir cero.
- **CRPS (primaria donde hay densidad):** c = CRPS(clim_causal, g) −
  CRPS(N(p, σ), g). Positivo = la densidad del modelo supera a la
  climatología causal. σ del ridge = sd residual del ajuste; σ del campeón
  = intervalo sellado / 1,2816. Normal en los dos (cota optimista,
  declarada en `control_lineal.crps_normal`).
- **Dirección (secundaria):** d = acierto − base («siempre al alza», mismas
  filas, `excluir_cero`).

**Unidad de replicación: el día.** Cada media lleva IC95 por **t de
clúster** (gl = k−1, el estimador que el Frente A midió calibrado), IC95
percentil por bootstrap de día (4.000 réplicas, semilla 20260903) y p por
permutación de signo de la suma diaria (4.000, misma semilla).
Comparaciones pareadas (C2 − C1, C1 − CAMPEÓN, C2 − CAMPEÓN) sobre las filas
que AMBOS predijeron, misma maquinaria de día.

**Criterio de lectura, fijado ahora:** «supera» = el IC95 t de clúster de la
media excluye el cero Y p de día < 0,05. Un p de filas no decide nada.

## 5. Conteo de intentos para el DSR (D2, convención §28: un intento por intervalo publicado sobre retornos reales)

| bloque | intervalos | intentos |
|---|---|---|
| por configuración (C1, C2, CAMPEÓN) × (MAE, CRPS, DIR) | 9 | 9 |
| pareadas (C2−C1, C1−CAMP, C2−CAMP) × (MAE, CRPS, DIR) | 9 | 9 |
| lo mismo bajo R2 | 18 | 18 |
| **total declarado antes de correr** | | **36** |

Se cuenta hacia arriba a propósito (R2 re-testea las mismas hipótesis; se
cuenta igual). N del registro al correr: el que dé
`GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO` (286 al escribir) → 322
después de esta corrida si se ejecuta tal como está declarada.

## 6. Qué se publica pase lo que pase

Las 18 celdas (y las 18 de R2), con n, k días, punto, IC t, IC percentil,
p de día. Si C1 no supera a CERO en MAE: «los features disponibles no traen
señal de magnitud detectable con esta ventana» y el MDE de magnitud de
`potencia_por_metrica.md` al lado. Si C2 no supera a C1: «la información
extra no trae magnitud detectable». Nada de esto es el veredicto 5.1.

## 7. Lo que este diseño NO puede decir

Un régimen sellado; el campeón está en muestra (sus β se estimaron sobre
esta misma historia); la climatología causal es agrupada (no por ticker:
una climatología por ticker sería un modelo más y contaría como intento);
la normal subestima colas. Todo eso se declara al pie del informe.

## Enmienda 1 (3-sep-2026, ~12:41 Chile —hora corregida por errata: el JSON de la primera corrida dice 12:42:00—, ANTES de la primera corrida) — dictamen del `auditor-lookahead` (5.º intento; los cuatro anteriores no llegaron)

**Veredicto del auditor:** sin fuga de valor futuro demostrada; UNA fuga de
disponibilidad demostrada y UNA selección de filas estructural. Exigido y
aplicado en el script antes de correr:

1. **Caché parcial del 1-sep.** `GEMELO/cache/cierres_353cacd57dc25f6a.csv`
   se bajó el 1-sep a las 13:16 UTC: su fila `2026-09-01` tiene `^SOX`, HYG,
   LQD, KRW, JPY en NaN y barras INTRADÍA de ES, NQ, VIX, GDAXI, EURUSD, TWD.
   El sello del 1-sep (7 filas) habría entrado con features no conocibles a las
   22:15 UTC. **Se descarta toda fecha posterior a la última barra completa de
   `^SOX` en la caché cruda** (panel, features y filas selladas) y se sella la
   huella (sha256, mtime) de cada caché en `parametros`. n esperado pasa de ≈269
   a ≈262 filas, 37 días.
2. `features.construir(verificar=True)`: la guarda de conocibilidad encendida.
3. **C2 con `^VIX3M` muerto (opción b, declarada ahora):** C2 se corre tal
   cual; su rango de fechas y n van en el informe; **toda comparación con C2
   es pareada sobre filas comunes y se lee sólo sobre ese rango** (≈ fechas ≤
   24-jul, ~88 filas; bajo R2 ~44); sus celdas absolutas NO se comparan con las
   de C1/campeón. No se crea «C2 sin vix_term» (sería una cuarta
   configuración). El conteo de intentos (36) no cambia.
4. `assert` de `intervalo80_pp` sin nulos ni ceros; rango predicho por
   configuración en `parametros`; embargo declarado como días CALENDARIO.

Recomendado y aplicado: test que fija `_prohibir_descarga`
(`tests/test_juez_lineal_d3.py`). Sospechas declaradas sin demostrar: `sox_t
= 0` por ffill en feriados de NY (ninguna fecha sellada cae en uno dentro de
la ventana); las series no son point-in-time (Yahoo del 1-sep). Zonas
ciegas: la fuga por el analista (features y D3 diseñados tras ver la ventana)
queda declarada y no es auditable.

## Nota de dependencia (3-sep-2026, 12:44 —hora corregida por errata—, después de la primera corrida) — dictamen del `director-programa`

El director observó, con razón, que la vara primaria de este juez depende de
una decisión NO firmada: `espera_firma.md` §30 (¿decide «MAE contra
predecir cero», como dice D3, o «contra la climatología causal», como exige
el adversario?). El encargo 09 §3b ordenaba construir y correr el juez, y
corrió el 3-sep a las 12:58 tras el dictamen del auditor de look-ahead, con
la etiqueta **EXPLORATORIO** y **los dos denominadores publicados** (MAE
contra cero y CRPS contra la climatología causal), de modo que ninguna
firma futura obligue a re-correrlo para leer su rama. Si Nicolás firma
«cero» como decisor, este pre-registro se re-emite con fecha y el juez
cuenta bajo esa rama; si firma «climatología», ídem. Hasta la firma, sus
celdas no computan como evidencia de entrada de R1. Los 36 intentos
declarados están sumados al registro sea cual sea la firma.

## Trazabilidad (exigido por el dictamen del adversario, 12:49)

- **Una sola corrida existió antes de la Enmienda 1: ninguna.** El único
  artefacto es `corrida09/juez_lineal_d3.json` (`generado_utc`
  2026-09-03T16:42:00Z); no hubo corrida con las 269 filas ni con ninguna
  otra ventana.
- **Qué cambió después de esa corrida** (mtimes 12:43:38): en el script, sólo
  la firma de la lambda de `_prohibir_descarga` (`ttl_horas=None`, para el
  test); en este documento, la nota de dependencia del director. Los
  `parametros` del JSON muestran que el código que corrió ya contenía los
  exigidos 1, 2 y 4 del auditor.
- **Hash de commit anterior a la corrida: no existe** (pre-registro y script
  estaban untracked). La corrida queda por eso doblemente EXPLORATORIA; el
  commit de pre-registro + script + test precede a cualquier re-corrida, y la
  regeneración del informe con las exigencias del adversario (celda campeón
  sobre las filas comunes, unidad de DIR, CSV por fila, NaN → null) se hace
  con el MISMO código de hipótesis y semilla: reproduce las 36 celdas y no
  suma intentos.
