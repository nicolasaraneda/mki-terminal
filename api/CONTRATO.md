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
