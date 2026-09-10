# Contrato de la API MKI Terminal (v1 — Etapa 4.7 "Fachada"; enmiendas 4.7.1 y 5.0)

API REST de **solo lectura** sobre el sistema existente. Regla cero: no
duplica ni reimplementa lógica de señales — envuelve las funciones puras de
`motor.py`, lee `senales.db`/`noticias.db` a través de los helpers de
consulta existentes, y usa `calendarios.py` para timing de sesiones. Lo único
que la API computa por sí misma es **capa de presentación** (base 100,
correlaciones para gráficos, estados abierta/cerrada de sesiones) — nunca una
señal.

- Base: `http://localhost:8000/api`
- CORS: solo orígenes localhost (Vite en 5173, Streamlit en 8501).
- Todos los endpoints son `GET`. No hay autenticación (herramienta local).
- La API **jamás** llama a la API de Anthropic ni escribe en las bases:
  el análisis IA se sirve exclusivamente desde el cache de `noticias.db`.

## Envelope común

Toda respuesta tiene esta forma:

```json
{
  "meta": {
    "generado_en": "2026-07-05T14:00:00+00:00",   // cuándo respondió la API
    "fecha_datos": "2026-07-05",                   // fecha del motor (hoy)
    "regimen": "Alcista · vol alta" | null,        // régimen vigente, siempre
    "modelo_version": "4.6.0",
    "plataforma_version": "5.0.0",                 // 5.0: versionado dual
    "snapshot_hoy": {                              // null si aún no hay
      "fecha": "2026-07-05", "origen": "programado|manual|dashboard",
      "timestamp_utc": "...", "modelo_version": "4.6.0",
      // 5.0: salud de descarga SELLADA del snapshot (null en sellos pre-5.0)
      "descarga_ok": 27, "descarga_total": 28, "descarga_caidos": "MU" | null,
      "plataforma_version": "5.0.0" | null
    }
  },
  "datos": { ... }                                 // específico del endpoint
}
```

Los campos de incertidumbre (`n_muestra`, `r2_historico`, `intervalo80_pp`)
acompañan a cada cifra de señal donde aplique — son información de primera
clase, no un tooltip.

## Endpoints

### GET /api/salud
Estado del sistema para el banner global, el footer y (desde 5.0) la vista
/salud — la sala de máquinas visible.
```json
"datos": {
  "snapshot": {...} | null,
  "snapshot_viejo": false,          // true si el último snapshot > 1 día hábil
  "edad_snapshot_horas": 3.2 | null,
  "salud_datos": {"ok": true, "problemas": [], "tickers_revisados": 27,
                   "auto_adjust": true},
  "horarios_utc": [{"exchange": "...", "proxima_sesion": "...",
                     "apertura_utc": "...", "cierre_utc": "..."}],
  "versiones": {"modelo": "4.6.0", "feature": "4.6.0", "universo": "4.6.0",
                 "plataforma": "5.0.0"},
  // ---- Enmienda 5.0 (aditiva): bloque operacional ----
  "operacion": {
    "es_dia_habil": true,           // sábado/domingo: los jobs no corren
    "jobs": [                       // los 5 jobs del día, estado según sus
                                    // artefactos (sello, ledger, logs, git)
      {"job": "noticias|snapshot|reporte|backup|vigia",
       "hora_programada": "17:50", "ok": true|false, "detalle": "...",
       "log": "data/noticias.log", "log_modificado_utc": "..." | null}
    ],
    "descarga_semana": [            // salud de descarga SELLADA, últimos 10
      {"fecha", "origen", "descarga_ok", "descarga_total", "descarga_caidos"}
    ],
    "verificaciones": {
      "estados": [{"estado", "n"}],
      "pendientes": [{"fecha", "ticker", "sesion_objetivo", "exchange"}],
      "atascadas": [{"fecha", "ticker", "sesion_objetivo", "exchange"}]
    },
    "presupuesto": {"fecha", "gasto_usd", "tope_usd", "restante_usd",
                     "agotado", "gasto_mes_usd",
                     "corridas_hoy": [{"origen", "costo_usd", "resultado", ...}]},
    "dbs": [{"nombre": "senales.db", "bytes": 147456}]
  }
}
```

### GET /api/hoy
Todo lo que necesita la portada bento.
```json
"datos": {
  "regimen": {"tendencia", "vol", "etiqueta", "ratio_ma_pct"} | null,
  // 4.7.1: el índice es EXCLUSIVAMENTE el valor sellado del último snapshot
  // en senales.db (fecha = día del sello); "historia" son los valores
  // sellados de snapshots anteriores. La API ya no recalcula el índice en
  // vivo y el "crudo" desapareció del payload: no queda sellado en el
  // snapshot y por lo tanto no es un número mostrable (una sola fuente de
  // verdad). null si no existe ningún snapshot todavía.
  "roca_chip": {"valor": 46, "fecha": "2026-07-05", "historia": [..]} | null,
  "sox": {"mov_pct": -5.44, "fecha": "2026-07-02", "feriado_hoy": true,
           "fecha_reciente": "2026-07-03"} | null,
  "sentimiento_sector": 0.30 | null,
  "track_record": {"suficiente": false, "n": 0, "minimo": 5,
                    "gap": {...} | null, "retorno_sesion": {...} | null},
  "senales_dia": [   // máx 3, ordenadas por fuerza (misma lógica que Streamlit;
                     // familia "apertura" desde 4.7.1: R² > 0.25 y fuera de
                     // zona earnings)
    {"tipo": "divergencia|apertura|sentimiento|buzz", "titulo": "...",
     "direccion": "pos|neg|neutra", "magnitud": "...", "porque": "...",
     "n_muestra": 120 | null, "r2_historico": 0.28 | null,
     "intervalo80_pp": 2.4 | null, "emitida_utc": "..." | null}
  ],
  "proxima_apertura": {          // la sesión que abre próxima + su predicción
    "exchange": "XKRX", "nombre": "KRX (Corea)", "sesion": "2026-07-06",
    "apertura_utc": "...", "predicciones": [ ...las de ese exchange... ]
  } | null,
  "husos": [ ...ver /api/husos abajo, embebido aquí... ],
  "resumen_ia": "texto plano" | null,
  // 4.7.1: la portada solo muestra lo mejor del día — titulares con
  // relevancia ≥ 0.5; los análisis previos a la columna relevancia (NULL)
  // entran solo si el matching estricto confirma una empresa del universo
  // en el texto. /api/noticias sigue sirviendo TODO sin filtrar.
  "noticias_top": [{"titular", "fuente", "fecha", "sentimiento",
                     "relevancia", "tickers"} ...máx 5]
}
```

`husos` (la cinta): una entrada por exchange rastreado (XKRX, XTKS, XTAI,
XETR, XNYS):
```json
{"exchange": "XKRX", "nombre": "KRX · Seúl", "region": "asia|europa|eeuu",
 "sesion": "2026-07-06", "apertura_utc": "...", "cierre_utc": "...",
 "estado": "abierta|proxima|cerrada",
 "beta_contagio_promedio": 0.62 | null,     // media de betas de sus tickers
 "cerro_antes": "XNYS" | null,              // narrativa del contagio
 "tickers": [{"ticker": "005930.KS", "nombre": "Samsung Electronics"}]}
```

### GET /api/aperturas
Las predicciones **vigentes** del anticipador. Fuente primaria: las filas
selladas del snapshot de hoy en `senales.db` (con su `timestamp_utc` real de
emisión — la garantía anti look-ahead). Se complementan con la salida viva de
`motor.prediccion_apertura_al` (beta, R² histórico, zona earnings). Si aún no
hay snapshot hoy, se sirven las vivas con `"sellada": false`.

4.7.1: la etiqueta `senal` se deriva SOLO de umbrales de R² histórico:
`debil` (R² < 0.10), `moderada` (0.10–0.25), `fuerte` (> 0.25) — la
incertidumbre se comunica con muestra, R² e intervalo, nunca con etiquetas
subjetivas. La zona de earnings viaja aparte (`zona_earnings`/
`dias_earnings`) y no altera la etiqueta.
```json
"datos": {
  "sox_usado": {"mov_pct": -5.44, "fecha": "2026-07-02"},
  "ventana_betas": 120,
  "calibracion": {"suficiente": false, "n": 0, "minimo": 5,
                   "cobertura_pct": null},
  "predicciones": [
    {"ticker": "000660.KS", "nombre": "SK Hynix", "mercado": "Corea",
     "exchange": "XKRX", "sesion_objetivo": "2026-07-06",
     "apertura_objetivo_utc": "...", "estimado_pct": -4.88,
     "intervalo80_pp": 6.99, "beta": 0.90, "r2_historico": 0.28,
     "n_muestra": 120, "senal": "fuerte|moderada|debil",
     "zona_earnings": false, "dias_earnings": null,
     "sellada": true, "emitida_utc": "2026-07-05T10:06:05+00:00"}
  ]
}
```

### GET /api/comparador?tickers=NVDA,AMD&base=usd&desde=2026-01-01
`tickers`: 2..N separados por coma (del universo). `base`: `usd` (default) |
`local`. `desde`: ISO date opcional (default: 1 año atrás; mínimo dentro de
la ventana de 3 años del motor).
```json
"datos": {
  "base": "usd", "desde": "2026-01-02",
  "series": {"NVDA": {"fechas": [...], "base100": [...]}, ...},
  "benchmark": {"ticker": "SMH", "fechas": [...], "base100": [...]},
  "tabla": [{"ticker", "nombre", "segmento", "ret_periodo_pct",
              "vol_anual_pct", "momentum_20d_pct", "puntaje_v0"}]
}
```

### GET /api/mercados
```json
"datos": {
  "betas": [ ...motor.betas_al + nombre/mercado, orden |beta| desc... ],
  "correlaciones_desfase": {      // presentación: corr entre eslabones con lag
    "lags": [5, 10, 20],
    "filas": [{"nombre": "Demanda final → Fabricación", "valores": [..]}]
  },
  "caso_destacado": {             // el hallazgo Samsung/KOSPI, permanente
    "ticker": "005930.KS", "nombre": "Samsung Electronics",
    "corr_kospi_mismo_dia": 0.91, "corr_sox_mismo_dia": 0.18,
    "corr_sox_dia_anterior": 0.36, "n_sesiones": 240
  }
}
```

### GET /api/cadena
```json
"datos": {
  "niveles": [{"nivel": 0, "nombre": "Materias primas",
                "momentum_20d_pct": -3.1, "sparkline": [..30 vals],
                "tickers": [{"ticker", "nombre"}]}],
  // 4.7.1: valor/fecha = el sello del último snapshot (igual que /api/hoy);
  // "serie" es contexto (momentum 20d crudo) calculado ANCLADO a la fecha
  // sellada — determinista entre visitas, jamás con datos posteriores al sello.
  "roca_chip": {"valor", "fecha", "serie": {"fechas", "valores"}} | null,
  "divergencias": [ ...todas, con "activa", z residual y z simple... ]
}
```

### GET /api/noticias?entidad=NVDA | sector
Sin `entidad`: panorama (sentimiento por ticker, buzz, últimos titulares,
resumen del día). Con `entidad`: solo titulares con matching estricto de esa
entidad. **Solo cache** — nunca dispara análisis nuevo.
```json
"datos": {
  "sentimiento_por_ticker": {"NVDA": 0.36, ...},
  "buzz": {"NVDA": {"hoy": 3, "promedio_diario": 1.2, "buzz": false}},
  "resumen_dia": "..." | null,
  "titulares": [{"titular", "fuente", "fecha", "url", "sentimiento",
                  "impacto", "relevancia", "tickers", "peso_temporal"}]
}
```

### GET /api/historial
```json
"datos": {
  "metricas": {"suficiente", "n", "minimo",
                "gap": {"pct_aciertos", "mae_pp"} | null,
                "retorno_sesion": {...} | null},
  "calibracion": {"suficiente", "n", "minimo", "cobertura_pct" | null},
  "evolucion": [{"fecha", "aciertos_gap_pct", "aciertos_sesion_pct", "n"}],
  "ultimas": [ ...verificaciones con sesión objetivo y emitida_utc... ],
  "estados": [{"estado": "pendiente|verificada|no_verificable_timing|
                "legacy_pre_4.6|sin_prediccion", "n": 22}],
  "snapshots": [{"fecha", "origen", "emitido_utc", "version", "ventana_betas"}],
  "puntaje_ia": {"suficiente", "n", ...} ,
  "primera_verificacion_posible": "2026-07-06",  // cuándo habrá 1er dato
  "pendientes_en_maduracion": 8,
  // ---- Enmienda 5.0 (aditiva): la incertidumbre del track record ----
  // Intervalos de Wilson al 95% sobre los aciertos (un 78.8% con n=80 se
  // muestra CON su incertidumbre estadística) — presentación pura.
  "wilson": {"gap": {"pct", "lo_pct", "hi_pct", "n"},
              "retorno_sesion": {...}} | null,
  // Curva de calibración: cobertura EMPÍRICA vs nominal. El sello guarda el
  // intervalo del 80% (±z80·sigma); las demás coberturas nominales se
  // obtienen re-escalando ese mismo sigma sellado (z_q/z80) — presentación
  // de números sellados, jamás una señal nueva.
  "calibracion_curva": {"nominal_pct": [20,40,50,60,70,80,90,95],
                         "real_pct": [...], "n": 80} | null,
  // Desglose por región (exchange) y por régimen SELLADO del día de emisión,
  // cada celda con su Wilson. La advertencia honesta va en la UI: la muestra
  // proviene casi entera de un solo régimen.
  "por_region": [{"region", "n", "gap_pct", "wilson_lo_pct", "wilson_hi_pct",
                   "mae_gap_pp"}],
  "por_regimen": [{"regimen", "n", "gap_pct", "wilson_lo_pct",
                    "wilson_hi_pct", "mae_gap_pp"}]
}
```

### GET /api/detalle/{ticker}
```json
"datos": {
  "perfil": {"ticker", "nombre", "segmento", "nivel", "tipo", "exchange",
              "moneda", "duplicado_de" | null},
  "ohlc": [{"t": "2026-07-03", "o", "h", "l", "c", "v"}],  // 1 año, moneda local
  "metricas": {fila de motor.puntaje_v0_al} | null,
  "sentimiento": 0.36 | null, "buzz": {...} | null,
  "noticias": [ ...matching estricto... ],
  "senal_apertura": {...} | null,   // si es mercado por abrir
  "correlaciones_top": [{"ticker", "nombre", "corr"}]
}
```

## Errores

- `400` parámetros inválidos (ticker fuera del universo, base desconocida).
- `404` ticker inexistente en `/api/detalle/{ticker}`.
- Formato (enmienda 5.0 — homogéneo, con causa y código):
  `{"detail": "mensaje en español", "codigo": "parametros_invalidos" |
  "no_encontrado" | "error_interno"}`. Los 500 llevan el tipo y el mensaje
  de la causa, SIEMPRE pasados por el enmascarador de secretos.

## Paridad

`tests/test_api.py` verifica que los números servidos son idénticos a los de
las funciones de `motor.py` y los helpers de `senales.py` para la misma
fecha. Si el dashboard Streamlit y la API difieren, el bug es de esta capa,
por definición. Excepción deliberada (4.7.1): el Roca→Chip de la API es el
valor SELLADO en senales.db — su paridad se testea contra la tabla
`snapshots`, no contra el recálculo vivo del motor (que es lo que muestra
Streamlit, mantenido como fallback en vivo).

### GET /api/universo  *(añadido en F4)*
Lista plana de instrumentos seleccionables (para el comparador y navegación).
Pura exposición de `universo.UNIVERSO` — sin lógica.
```json
"datos": {
  "instrumentos": [{"ticker": "NVDA", "nombre": "NVIDIA",
                     "segmento": "EE.UU. - GPUs / IA", "nivel": null,
                     "tipo": "accion", "exchange": "XNYS"}]
}
```


---

## Enmienda 7.0.0 — el riel de dinero (corrida 10)

**Se enmienda ANTES de tocar los endpoints**, que es la regla de esta capa.

Tres endpoints nuevos, todos de **SOLO LECTURA sobre artefactos ya
generados**. No computan nada: leen los JSON que producen
`python -m dinero.mapa`, `python -m dinero.cuenta_papel` y
`python -m dinero.senal_larga_reporte`, y el árbitro `cifras.py` para el
estado del riel de medición. No tocan la red, no escriben, no llaman a
Anthropic.

**Regla de honestidad propia de estos tres**, porque sirven cifras de un riel
que no tiene ninguna fila sellada: **cada objeto lleva su `estatus`**
(`MEDIDO` | `SIMULADO` | `PROPUESTA` | `REFUTADO` | `RETIRADO` |
`DECISION_PENDIENTE`) y, cuando lleva un estimador puntual, **lleva su
intervalo en el mismo objeto**. Un número sin intervalo no viaja por esta API
si es un estimador. Los `n` van siempre.

**Enmienda del 7-sep-2026 (dictámenes de cierre de la corrida 10).** Cuatro
cosas que la primera versión prometía y no cumplía, o no había previsto:

1. **`RETIRADO` es un estatus servible.** Cuando un artefacto queda retirado,
   el endpoint **no sirve sus cifras con una advertencia al lado**: sirve el
   motivo del retiro y `cifras_disponibles: false`. Servir el número con un
   cartel es seguir haciéndolo circular.
2. **Toda cifra declara si es una DIFERENCIA.** El campo `es_diferencia` va en
   cada `CifraConIC`, más `comparar_contra` cuando corresponde. La frase «el
   intervalo no contiene el cero» sólo significa algo sobre una diferencia: un
   Wilson de una proporción no puede contener el cero nunca, y decirlo debajo
   de una tasa de acierto insinúa una significancia que no existe.
3. **El `meta` de estos tres declara el artefacto que los sirve.**
   `meta.artefacto` lleva nombre, `generado_en` (mtime del archivo) y `sha256`.
   `meta.generado_en` es la hora de la RESPUESTA, no la del dato, y estampar
   hora fresca sobre un JSON que puede tener semanas es la misma zona ciega de
   sellado que el proyecto ya conoce en producción.
4. **`/api/rieles` sirve el McNemar que este contrato prometía** y no servía:
   `mcnemar_p_filas` con su `mcnemar_caveat` (es un p de FILAS, y las filas de
   un día no son independientes: manda el IC de clúster de día).

### GET /api/dinero/universo
El mapa de la cadena a instrumentos comprables. Sirve
`dinero/resultados/universo_operable.json` tal cual, con su fuente
(archivo congelado, sha256, rango de fechas) y su resumen de eslabones
representados / sustituidos / huecos, en las dos lecturas (con y sin exigir
liquidez verificada).

### GET /api/dinero/cuenta
La cuenta en papel. Sirve `dinero/resultados/cuenta_papel.json`.
**Todo el objeto lleva `etiqueta: "SIMULADO"`** y la advertencia de que la
señal que la alimenta no tiene información: lo medido es fricción. Incluye
el barrido de deslizamiento y las comparaciones contra las dos líneas base con
su intervalo.

**Del 7 al 8-sep-2026 el artefacto estuvo `estatus: "RETIRADO"`** con el
objeto `retirado` (fecha, fuente, causa, consecuencia): tenía fuga temporal
demostrada, y `/api/rieles` no reexponía ninguna de sus cifras.

**Desde el 8-sep-2026 (corrida 11, acta §82.4) es la v2 reconstruida:**
`version: 2`, `estatus: "PROPUESTA"`, y el objeto `reconstruccion` (fecha,
acta, correcciones E1–E6, `gate_invariancia` con su resultado y cortes, y
`costo` con la fuente del arancel y la columna usada). Trae además
`sigma_dif_semanal` (σ de la diferencia semanal del juego por defecto contra
SMH, con `ic95`, `semanas` y método) y, por juego, `ordenes_reducidas_al_ejecutar`
y `comisiones_pct_del_aportado`. Si un artefacto futuro vuelve a
`estatus: "RETIRADO"`, `/api/rieles` vuelve a no reexponer sus cifras: la
regla vive en el código, no en este texto.

### GET /api/rieles
Estado de los dos rieles, uno al lado del otro. El de MEDICIÓN se lee del
árbitro `cifras.sellada()` —n, días, ventaja con su IC de clúster de día,
McNemar, cobertura— y el de DINERO del pre-registro y los artefactos. Cada
riel declara: qué mide, en qué horizonte, contra qué vara, cuánta muestra
lleva, qué le falta para veredicto y **qué lo mata**.

Enmienda 8-sep-2026 (corrida 11): en el riel de dinero, `cuenta_en_papel`
lleva `cifras_disponibles` **leído del artefacto** (falso sólo si el estatus
es RETIRADO), `version`, `reconstruccion` (fecha y resultado del gate) y
`comisiones_pct_del_aportado_juego_activo`; y `potencia` sale del
`sigma_dif_semanal` del artefacto —`sigma_dif_semanal_pp` con `intervalo`,
`tipo_intervalo`, `semanas`, `juego`, `base`— o queda `estatus: RETIRADO`
sin número si el artefacto no lo trae con intervalo.

Enmienda 9-sep-2026 (corrida 12, re-dictamen del `estadistico-adversario`,
`GEMELO/resultados/dictamen_12/re_dictamen_corrida_11.md`, D1 a D15). Regla
ampliada del bloque: **el intervalo viaja con su cobertura medida en el
mismo objeto cuando existe, ninguna etiqueta de nivel se escribe a mano y
ningún resumen se sirve sin el presupuesto y el modo con que se computó.**
En concreto: (a) `cuenta_en_papel.comisiones_pct_del_aportado_juego_activo`
deja de ser un escalar y es un objeto `{mediana_pct, banda_p2_5_p97_5,
banda_es, K, deslizamiento_pb, semanas, denominador_usd, juego,
es_una_semilla: false, estatus}` leído de `barrido_semillas` del artefacto,
o `null`; (b) `potencia.tipo_intervalo` dice «nominal 95 %, cobertura medida
X [Wilson] a 156 semanas» leído del instrumento, y lleva
`cobertura_medida_ic_sd`, `advertencia_del_artefacto` y `mde80_bloque_1`
(con su σ ancla, banda, valor al α real y las dos convenciones de
anualización); la σ servida y el MDE80 nunca comparten oración; (c) `mapa`
lleva `presupuesto_usd`, `modo`, `al_borde`, `alcanzables`, `dias_de_censo`,
`fecha_censo`, `nota` y `estatus`, o es `null`; (d) el riel de medición lleva
`cobertura_80` `{valor_pct, intervalo (Wilson 95 %), k, n, nominal_pct}`
—también como quinta entrada de `cifras`—, `regimenes_en_ventana`,
`un_solo_regimen` y `etiqueta_regimen`; y `que_lo_mata` se compone desde
`GEMELO/resultados/intervalo_coherencia.json` (R2 bajo la regla firmada),
no a mano; (e) `senal_larga.denominadores` separa las celdas (denominador
de «ganan sin corregir») de los 30 contrastes de la familia de Holm y
declara `k_bajo_la_nula: null`.

Ninguno de los tres endpoints entra al envelope con `meta.regimen`: no
dependen del motor ni del régimen. Llevan `meta` reducido
(`generado_en`, `modelo_version`, `plataforma_version`) más `meta.artefacto`
(nombre, `generado_en` del archivo y `sha256`) cuando la respuesta sale de un
artefacto.


### GET /api/dinero/sellos  *(añadido en la corrida 12, 9-sep-2026)*
E0/E1 del riel de dinero, para la vista `/sellos`. Solo lectura:
`dinero/sello_dinero.db` en `mode=ro` (vía `dinero.sello_dinero.estado()`) y
`dinero/resultados/cuenta_papel.json` (gate de invariancia). `datos`:
`estatus` (siempre PROPUESTA), `que_es`, `senal_fuente` (declara que la sonda
no tiene información), `E0` `{estado, sesiones_selladas,
sesiones_que_cuentan_para_N, N_objetivo, filas, nota, estatus}`, `E1`
`{estado: "NO EJECUTADO" | ..., etiqueta: "PRÁCTICA", por_que, adaptador,
cuenta_practica, posiciones, efectivo, ejecuciones, marca_retraso, estatus}`
—sin datos de ejemplo jamás: si E1 no corrió, los campos son `null`—,
`ultimo_sello` (fecha_insumo, timestamp_utc, available_at, sesion_objetivo,
apertura_objetivo_utc, estado, cuenta_para_N, juego, presupuesto_usd, los dos
sha256 del insumo, plataforma_version), `decisiones_proxima_apertura` (una por
instrumento operable: ticker, decision, acciones_regla, tamano_nominal = 0,
precio_ref_usd, señal con banda, motivo), `gate_invariancia_ultima_corrida`
y la frase `smh`. La cuenta regresiva a la apertura la computa el frontend
desde `apertura_objetivo_utc`; la actualización es sondeo corto (60 s) con el
mismo `useApi`, sin dependencia nueva.

**Norma del contrato (corrida 12, declarada por el `director-programa`):** ningún
payload de `/api/rieles` ni `/api/dinero/sellos` contiene «rentable», «retorno
esperado», «ganancia esperada», «confianza» ni la frase «sostiene casi toda»
(ordena cantidades que el diseño no ordena); y mientras E1 esté NO EJECUTADO,
`E1.posiciones/efectivo/ejecuciones` son `null` (nunca datos de ejemplo).
Test: `tests/test_frontend_estatus.py::test_las_frases_fijas_de_la_api_del_riel_tampoco_insinuan_resultado`.
