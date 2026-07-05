// Tipos espejo de api/CONTRATO.md — si el contrato cambia, esto cambia con él.

export interface Meta {
  generado_en: string
  fecha_datos: string
  regimen: string | null
  modelo_version: string
  snapshot_hoy: {
    fecha: string
    origen: string
    timestamp_utc: string
    modelo_version: string
  } | null
}

export interface Sobre<T> {
  meta: Meta
  datos: T
}

export interface Regimen {
  tendencia: string
  vol: string
  etiqueta: string
  ratio_ma_pct: number
  vol_actual: number
  vol_mediana: number
}

export interface Huso {
  exchange: string
  nombre: string
  region: 'asia' | 'europa' | 'eeuu'
  sesion: string
  apertura_utc: string
  cierre_utc: string
  estado: 'abierta' | 'proxima' | 'cerrada'
  beta_contagio_promedio: number | null
  cerro_antes: string | null
  tickers: { ticker: string; nombre: string }[]
}

export interface Prediccion {
  ticker: string
  nombre: string
  mercado: string
  exchange: string
  sesion_objetivo: string | null
  apertura_objetivo_utc: string | null
  estimado_pct: number
  intervalo80_pp: number
  n_muestra: number
  beta: number
  r2_historico: number
  confianza: 'Alta' | 'Media' | 'Baja'
  zona_earnings: boolean
  dias_earnings: number | null
  sellada: boolean
  emitida_utc: string | null
  estado: string
}

export interface SenalDia {
  tipo: 'divergencia' | 'apertura' | 'sentimiento' | 'buzz'
  titulo: string
  direccion: 'pos' | 'neg' | 'neutra'
  magnitud: string
  porque: string
  n_muestra: number | null
  r2_historico: number | null
  intervalo80_pp: number | null
  emitida_utc: string | null
}

export interface TrackRecord {
  suficiente: boolean
  n: number
  minimo: number
  gap?: { pct_aciertos: number; mae_pp: number }
  retorno_sesion?: { pct_aciertos: number; mae_pp: number }
}

export interface Titular {
  titular: string
  fuente: string
  fecha: string
  url?: string | null
  sentimiento: number | null
  impacto?: string | null
  relevancia?: number | null
  tickers: string | null
  peso_temporal?: number
}

export interface DatosHoy {
  regimen: Regimen | null
  roca_chip: { valor: number; crudo_pct: number; historia: number[] } | null
  sox: {
    mov_pct: number
    fecha: string
    feriado_hoy: boolean
    fecha_reciente: string
  } | null
  sentimiento_sector: number | null
  track_record: TrackRecord
  senales_dia: SenalDia[]
  proxima_apertura: {
    exchange: string
    nombre: string
    sesion: string
    apertura_utc: string
    predicciones: Prediccion[]
  } | null
  husos: Huso[]
  resumen_ia: string | null
  noticias_top: Titular[]
}

export interface DatosAperturas {
  sox_usado: { mov_pct: number; fecha: string } | null
  ventana_betas: number
  calibracion: { suficiente: boolean; n: number; minimo: number; cobertura_pct?: number }
  predicciones: Prediccion[]
}

export interface Serie {
  fechas: string[]
  valores: number[]
}

export interface DatosSalud {
  snapshot: Meta['snapshot_hoy']
  snapshot_viejo: boolean
  edad_snapshot_horas: number | null
  salud_datos: { ok: boolean; problemas: string[]; tickers_revisados: number }
  horarios_utc: Record<string, string>[]
  versiones: { modelo: string; feature: string; universo: string }
}

export interface DatosComparador {
  base: 'usd' | 'local'
  desde: string
  series: Record<string, Serie>
  benchmark: ({ ticker: string } & Serie) | null
  tabla: {
    ticker: string
    nombre: string
    segmento: string
    ret_periodo_pct: number
    vol_anual_pct: number
    momentum_20d_pct: number
    puntaje_v0: number | null
  }[]
}

export interface DatosMercados {
  betas: {
    ticker: string
    nombre: string
    mercado: string
    exchange: string | null
    beta: number
    r2_historico: number
    n_muestra: number
  }[]
  correlaciones_desfase: {
    lags: number[]
    filas: { nombre: string; valores: (number | null)[] }[]
  }
  caso_destacado: {
    ticker: string
    nombre: string
    corr_kospi_mismo_dia: number
    corr_sox_mismo_dia: number
    corr_sox_dia_anterior: number
    n_sesiones: number
  } | null
}

export interface Divergencia {
  par: string
  grupo: string
  spread: number
  z: number
  spread_simple: number
  z_simple: number
  activa: boolean
  explicacion: string
}

export interface DatosCadena {
  niveles: {
    nivel: number
    nombre: string
    momentum_20d_pct: number
    sparkline: number[]
    tickers: { ticker: string; nombre: string }[]
  }[]
  roca_chip: {
    valor: number
    crudo_pct: number
    historia: number[]
    serie: Serie
  } | null
  divergencias: Divergencia[]
}
