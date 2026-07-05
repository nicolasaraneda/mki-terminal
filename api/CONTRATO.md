# Contrato de la API MKI Terminal (v1 — Etapa 4.7 "Fachada")

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
    "snapshot_hoy": {                              // null si aún no hay
      "fecha": "2026-07-05", "origen": "programado|manual|dashboard",
      "timestamp_utc": "...", "modelo_version": "4.6.0"
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
Estado del sistema para el banner global y el footer.
```json
"datos": {
  "snapshot": {...} | null,
  "snapshot_viejo": false,          // true si el último snapshot > 1 día hábil
  "edad_snapshot_horas": 3.2 | null,
  "salud_datos": {"ok": true, "problemas": [], "tickers_revisados": 27,
                   "auto_adjust": true},
  "horarios_utc": [{"exchange": "...", "proxima_sesion": "...",
                     "apertura_utc": "...", "cierre_utc": "..."}],
  "versiones": {"modelo": "4.6.0", "feature": "4.6.0", "universo": "4.6.0"}
}
```

### GET /api/hoy
Todo lo que necesita la portada bento.
```json
"datos": {
  "regimen": {"tendencia", "vol", "etiqueta", "ratio_ma_pct"} | null,
  "roca_chip": {"valor": 46, "crudo_pct": 4.1, "historia": [..30 vals]} | null,
  "sox": {"mov_pct": -5.44, "fecha": "2026-07-02", "feriado_hoy": true,
           "fecha_reciente": "2026-07-03"} | null,
  "sentimiento_sector": 0.30 | null,
  "track_record": {"suficiente": false, "n": 0, "minimo": 5,
                    "gap": {...} | null, "retorno_sesion": {...} | null},
  "senales_dia": [   // máx 3, ordenadas por fuerza (misma lógica que Streamlit)
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
`motor.prediccion_apertura_al` (beta, confianza, zona earnings). Si aún no
hay snapshot hoy, se sirven las vivas con `"sellada": false`.
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
     "n_muestra": 120, "confianza": "Alta|Media|Baja",
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
  "roca_chip": {"valor", "crudo_pct", "historia": [..], "serie": {"fechas", "valores"}},
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
  "pendientes_en_maduracion": 8
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
- Formato: `{"detail": "mensaje en español"}` (estándar FastAPI).

## Paridad

`tests/test_api.py` verifica que los números servidos son idénticos a los de
las funciones de `motor.py` y los helpers de `senales.py` para la misma
fecha. Si el dashboard Streamlit y la API difieren, el bug es de esta capa,
por definición.
