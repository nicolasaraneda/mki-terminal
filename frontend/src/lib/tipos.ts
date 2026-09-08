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

// ============================================================
// RIEL DE DINERO (Etapa 7.0.0, corrida 10). Espejo de la enmienda 7.0.0
// de api/CONTRATO.md. El frontend NO computa ninguna señal ni ningún
// intervalo: si un número difiere del de la API, el bug es de la API.
//
// Nótese que `intervalo` NO es opcional en ningún estimador de estos
// tipos. Es a propósito: un número sin intervalo no se muestra, y el
// tipo es el primer lugar donde esa regla se puede hacer cumplir.
// ============================================================
export type EstatusEvidencial =
  | 'MEDIDO'
  | 'SIMULADO'
  | 'PROPUESTA'
  | 'REFUTADO'
  | 'RETIRADO'
  | 'DECISION_PENDIENTE'

export interface CifraConIC {
  nombre: string
  valor_pct: number
  intervalo: [number, number]
  tipo_intervalo: string
  cruza_cero?: boolean
  // Una proporción con Wilson NO es una diferencia, y la frase «el
  // intervalo no contiene el cero» sólo significa algo sobre diferencias.
  // El servidor lo declara; la vista no lo adivina.
  es_diferencia?: boolean
  comparar_contra?: string | null
}

export interface InstrumentoOperable {
  ticker: string
  nombre: string
  forma: string
  rol: string
  sustituye_a: string
  diferencia: string
  liquidez_no_verificada: boolean
  verificado: boolean
  razon_no_verificado: string
  precio_usd: number | null
  fecha_precio: string | null
  alcanza_con_techo: boolean
  alcanza_con_piso: boolean
  acciones_con_techo: number
  comision_orden_minima_pct: number | null
  comision_orden_techo_pct: number | null
}

export interface EslabonOperable {
  clave: string
  nombre: string
  dominante_contexto_no_verificado: string
  obstaculo: string
  estado: 'REPRESENTADO' | 'SUSTITUIDO' | 'HUECO'
  estado_exigiendo_liquidez: 'REPRESENTADO' | 'SUSTITUIDO' | 'HUECO'
  huecos: { quien: string; clase: string; por_que: string }[]
  instrumentos: InstrumentoOperable[]
}

export interface DatosUniversoOperable {
  // El mapa como objeto del riel de dinero es SIMULADO; los precios que lo
  // sostienen son MEDIDO al día del congelado. Son dos afirmaciones y
  // llevan dos etiquetas.
  estatus: EstatusEvidencial
  estatus_de_los_precios?: string
  generado: string
  fuente: { archivo: string; sha256?: string; desde?: string; hasta?: string; filas?: number }
  presupuesto: { piso_usd: number; techo_usd: number }
  costos: Record<string, number | boolean | string | number[]>
  eslabones: EslabonOperable[]
  resumen: {
    candidatos: number
    verificados: number
    representados: number
    sustituidos: number
    huecos: number
    representados_exigiendo_liquidez: number
    sustituidos_exigiendo_liquidez: number
    huecos_exigiendo_liquidez: number
  }
}

export interface ComparacionSemanal {
  semanas: number
  dif_media_pp: number
  ic_lo: number
  ic_hi: number
  cruza_cero: boolean
  bloque_semanas: number
  replicas: number
  semilla: number
}

export interface FilaCuenta {
  etf?: string
  juego?: string
  deslizamiento_pb: number
  final_usd: number
  aportado_usd: number
  resultado_usd: number
  resultado_pct: number
  ordenes: number
  comisiones_usd: number
  deslizamiento_usd: number
  contra?: Record<string, ComparacionSemanal>
}

export interface RetiroDeCifras {
  fecha: string
  por: string
  fuente: string
  causa: string
  consecuencia: string
}

export interface DatosCuentaPapel {
  etiqueta: 'SIMULADO'
  estatus: EstatusEvidencial
  retirado?: RetiroDeCifras
  advertencia: string
  ventana: { desde: string; hasta: string; dias_de_mercado: number }
  aportado_usd: number
  aportes: number
  instrumentos_operables: number
  barrido_deslizamiento_pb: number[]
  linea_base: FilaCuenta[]
  juegos: FilaCuenta[]
  falsos_positivos: {
    comparaciones: number
    con_ic_que_excluye_cero: number
    nota: string
  }
  reconstruccion?: {
    fecha: string
    costo?: { comision_minima_usd: number; comision_por_accion_usd: number }
  }
  barrido_semillas?: {
    K: number
    deslizamiento_pb: number
    comisiones_pct_del_aportado: Record<string, { mediana: number; banda_p2_5_p97_5: [number, number] }>
  }
}

export interface Riel {
  nombre: string
  estatus: EstatusEvidencial
  que_mide: string
  horizonte: string
  vara: string
  mueve_plata: boolean
  muestra: Record<string, number | string | null>
  cifras?: CifraConIC[]
  mcnemar_p_filas?: number
  mcnemar_caveat?: string
  cobertura_80_pct?: number
  n_efectivo?: number
  icc?: number
  deff?: number
  mapa?: DatosUniversoOperable['resumen'] | null
  cuenta_en_papel?: {
    estatus?: EstatusEvidencial
    retirado?: RetiroDeCifras
    advertencia: string
    cifras_disponibles?: boolean
  } | null
  senal_larga?: {
    estatus?: EstatusEvidencial
    celdas: number
    ganan_a_la_climatologia_sin_corregir: number
    ganan_tras_multiplicidad: number
    ganan_tras_ablacion_anual: number
    L1_refutada: boolean
    contrastes: number
    segunda_vara_preregistrada_evaluada?: boolean
    pasan_holm?: string[]
    nota: string
  } | null
  potencia?: {
    sigma_dif_semanal_pp: number | null
    estatus?: EstatusEvidencial
    nota: string
  }
  falta_para_veredicto: string
  que_lo_mata: string
  procedencia?: string
}

export interface DatosRieles {
  rieles: Riel[]
  por_que_son_dos: string
}
