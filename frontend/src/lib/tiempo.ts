// Utilidades de tiempo de la cinta de husos. Todo se muestra en hora de
// Chile (America/Santiago) — la tesis del producto es que el día global
// del semiconductor se lee desde acá.

const ZONA_CL = 'America/Santiago'

export function horaChile(iso: string): string {
  return new Intl.DateTimeFormat('es-CL', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: ZONA_CL,
  }).format(new Date(iso))
}

/* Hora local de cada bolsa (para el tooltip de la cinta: el operador ve
   la sesión en SU hora y en la de Chile a la vez). Presentación pura. */
const TZ_EXCHANGE: Record<string, string> = {
  XKRX: 'Asia/Seoul',
  XTKS: 'Asia/Tokyo',
  XTAI: 'Asia/Taipei',
  XETR: 'Europe/Berlin',
  XNYS: 'America/New_York',
}

export function horaLocalExchange(iso: string, exchange: string): string {
  return new Intl.DateTimeFormat('es-CL', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: TZ_EXCHANGE[exchange] ?? 'UTC',
  }).format(new Date(iso))
}

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun',
               'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

export function fechaCorta(iso: string): string {
  // Una fecha sin hora (YYYY-MM-DD) es una fecha de calendario, no un
  // instante: convertirla a zona Chile la correría un día hacia atrás.
  const soloFecha = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)
  if (soloFecha) {
    return `${soloFecha[3]} ${MESES[Number(soloFecha[2]) - 1]}`
  }
  return new Intl.DateTimeFormat('es-CL', {
    day: '2-digit',
    month: 'short',
    timeZone: ZONA_CL,
  }).format(new Date(iso))
}

export function fechaHoraChile(iso: string): string {
  return `${fechaCorta(iso)} ${horaChile(iso)}`
}

/** El eje del día global ARRANCA en el cierre de NY (ADENDA de diseño):
 * ahí muere la sesión americana y el contagio parte a viajar hacia Asia.
 * Devuelve el cierre de NY más reciente que ya pasó (o el de hoy si aún
 * no ocurre, retrocedido 24h). */
export function inicioEjeGlobal(cierreNyUtc: string): number {
  const cierre = new Date(cierreNyUtc).getTime()
  const ahora = Date.now()
  let inicio = cierre
  // cierre_utc de la API es el de la PRÓXIMA sesión → retroceder días
  // hábiles hasta quedar en el pasado (fin de semana: hasta 3 saltos)
  for (let i = 0; i < 5 && inicio > ahora; i++) inicio -= 24 * 3600 * 1000
  return inicio
}

const DIA_MS = 24 * 3600 * 1000

/** Posición 0..1 de un instante dentro del eje de 24h (más allá se satura). */
export function posEnEje(iso: string, inicioEje: number): number {
  const t = new Date(iso).getTime()
  return Math.max(0, Math.min(1, (t - inicioEje) / DIA_MS))
}

/** Posición de "ahora" en el eje. Si el eje quedó viejo (fin de semana:
 * ahora > inicio+24h), se satura en 1. */
export function posAhora(inicioEje: number): number {
  return Math.max(0, Math.min(1, (Date.now() - inicioEje) / DIA_MS))
}

/** Etiquetas de hora Chile cada 4 horas a lo largo del eje. */
export function marcasEje(inicioEje: number): { pos: number; etiqueta: string }[] {
  const marcas = []
  for (let h = 0; h <= 24; h += 4) {
    const t = new Date(inicioEje + h * 3600 * 1000)
    marcas.push({ pos: h / 24, etiqueta: horaChile(t.toISOString()) })
  }
  return marcas
}

/** "en 2h 14m" / "hace 3h" para tooltips y el chip de próxima apertura. */
export function distanciaHumana(iso: string): string {
  const delta = new Date(iso).getTime() - Date.now()
  const abs = Math.abs(delta)
  const h = Math.floor(abs / 3600000)
  const m = Math.floor((abs % 3600000) / 60000)
  const cuerpo = h > 0 ? `${h}h ${m}m` : `${m}m`
  return delta >= 0 ? `en ${cuerpo}` : `hace ${cuerpo}`
}
