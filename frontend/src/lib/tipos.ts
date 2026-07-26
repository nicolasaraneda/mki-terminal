// Tipos espejo de api/CONTRATO.md — si el contrato cambia, esto cambia con él.

export interface Meta {
  generado_en: string
  fecha_datos: string
  regimen: string | null
  modelo_version: string
  /** 5.0: versionado dual — la plataforma evoluciona, el modelo sigue congelado */
  plataforma_version: string
  snapshot_hoy: {
    fecha: string
    origen: string
    timestamp_utc: string
    modelo_version: string
    /** 5.0: salud de descarga SELLADA (null en sellos pre-5.0) */
    descarga_ok: number | null
    descarga_total: number | null
    descarga_caidos: string | null
    plataforma_version: string | null
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
  /** derivada SOLO de R² histórico: débil <0.10 · moderada 0.10–0.25 · fuerte >0.25 */
  senal: 'fuerte' | 'moderada' | 'debil'
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
  /** 4.7.1: valor sellado del último snapshot; historia = sellos previos */
  roca_chip: { valor: number; fecha: string; historia: number[] } | null
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

export interface JobOperacion {
  job: 'noticias' | 'snapshot' | 'reporte' | 'backup' | 'vigia'
  hora_programada: string
  ok: boolean
  detalle: string
  log: string
  log_modificado_utc: string | null
}

export interface Operacion {
  es_dia_habil: boolean
  jobs: JobOperacion[]
  descarga_semana: {
    fecha: string
    origen: string
    descarga_ok: number | null
    descarga_total: number | null
    descarga_caidos: string | null
  }[]
  verificaciones: {
    estados: { Estado: string; N: number }[]
    pendientes: { fecha: string; ticker: string; sesion_objetivo: string; exchange: string }[]
    atascadas: { fecha: string; ticker: string; sesion_objetivo: string; exchange: string }[]
  }
  presupuesto: {
    fecha: string
    gasto_usd: number
    tope_usd: number
    restante_usd: number
    agotado: boolean
    gasto_mes_usd: number
    corridas_hoy: Record<string, string | number | null>[]
  }
  dbs: { nombre: string; bytes: number }[]
}

export interface DatosSalud {
  snapshot: Meta['snapshot_hoy']
  snapshot_viejo: boolean
  edad_snapshot_horas: number | null
  salud_datos: { ok: boolean; problemas: string[]; tickers_revisados: number }
  horarios_utc: Record<string, string>[]
  versiones: { modelo: string; feature: string; universo: string; plataforma: string }
  operacion: Operacion
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
    fecha: string
    /** contexto anclado a la fecha sellada (momentum 20d crudo) */
    serie: Serie | null
  } | null
  divergencias: Divergencia[]
}

export interface DatosHistorial {
  metricas: TrackRecord
  calibracion: { suficiente: boolean; n: number; minimo: number; cobertura_pct?: number }
  evolucion: Record<string, string | number | null>[]
  ultimas: Record<string, string | number | null>[]
  estados: { Estado: string; N: number }[]
  snapshots: Record<string, string | number | null>[]
  puntaje_ia: {
    suficiente: boolean
    n: number
    retorno_tercio_alto?: number
    retorno_tercio_bajo?: number
    correlacion?: number | null
  }
  primera_verificacion_posible: string | null
  pendientes_en_maduracion: number
  /** 5.0: aciertos CON su incertidumbre estadística (Wilson 95%) */
  wilson: {
    gap: { pct: number; lo_pct: number; hi_pct: number; n: number }
    retorno_sesion: { pct: number; lo_pct: number; hi_pct: number; n: number }
  } | null
  /** 5.0: cobertura empírica vs nominal (re-escala del sigma sellado) */
  calibracion_curva: { nominal_pct: number[]; real_pct: number[]; n: number } | null
  por_region: DesgloseTrackRecord[]
  por_regimen: DesgloseTrackRecord[]
}

export interface DesgloseTrackRecord {
  region?: string
  regimen?: string
  n: number
  gap_pct: number
  wilson_lo_pct: number
  wilson_hi_pct: number
  mae_gap_pp: number
}

export interface DatosNoticias {
  sentimiento_por_ticker: Record<string, number>
  buzz: Record<string, { hoy: number; promedio_diario: number; buzz: boolean }>
  resumen_dia: string | null
  titulares: Titular[]
}

export interface DatosDetalle {
  perfil: {
    ticker: string
    nombre: string
    segmento: string
    nivel: number | null
    tipo: string
    exchange: string | null
    moneda: string
    duplicado_de?: string | null
  }
  ohlc: { t: string; o: number; h: number; l: number; c: number; v: number }[]
  metricas: Record<string, string | number | null> | null
  sentimiento: number | null
  buzz: { hoy: number; promedio_diario: number; buzz: boolean } | null
  noticias: Titular[]
  senal_apertura: Prediccion | null
  correlaciones_top: { ticker: string; nombre: string; corr: number }[]
}

export interface Instrumento {
  ticker: string
  nombre: string
  segmento: string
  nivel: number | null
  tipo: string
  exchange: string | null
}
