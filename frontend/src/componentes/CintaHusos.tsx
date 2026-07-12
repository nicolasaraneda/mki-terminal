import { Fragment, useEffect, useMemo, useRef, useState } from 'react'
import type { Huso, Prediccion } from '../lib/tipos'
import {
  distanciaHumana,
  horaChile,
  horaLocalExchange,
  inicioEjeGlobal,
  marcasEje,
  posAhora,
  posEnEje,
} from '../lib/tiempo'

// ============================================================
// La cinta de husos — el elemento firma del producto.
//
// Un eje de 24 horas del día global del semiconductor, que ARRANCA en el
// cierre de NY: ahí muere la sesión americana y el contagio parte a viajar
// hacia Asia (flecha magenta punteada). Un micro-carril por bolsa,
// descendiendo Asia → Europa → EE.UU. Todo en hora de Chile.
// Máx 56px; colapsada es una línea de 8px con las sesiones como segmentos.
// Presupuesto de cian: el marcador "ahora" y la próxima sesión en abrir.
//
// 4.9 F2: el marcador avanza cada 30s con transición (transform puro);
// el cruce de un borde de píldora cambia su estado en vivo (presentación
// sobre los timestamps del server) con 100ms de delay para que el marcador
// asiente primero; el tooltip suma hora local de la bolsa y qué
// predicciones apuntan a esa sesión.
// ============================================================

const CARRIL: Record<string, number> = {
  XKRX: 0,
  XTKS: 1,
  XTAI: 2,
  XETR: 3,
  XNYS: 4,
}

/* Estado efectivo entre refetches: si "ahora" cruzó el borde de la píldora,
   el estado cambia en vivo sin esperar a la API (que lo confirmará). */
function estadoEfectivo(h: Huso, ahoraMs: number): Huso['estado'] {
  const abre = new Date(h.apertura_utc).getTime()
  const cierra = new Date(h.cierre_utc).getTime()
  if (abre <= ahoraMs && ahoraMs <= cierra) return 'abierta'
  if (ahoraMs > cierra) return 'cerrada'
  return h.estado === 'abierta' ? 'proxima' : h.estado
}

export function CintaHusos({
  husos,
  objetivo = null,
  predicciones = [],
}: {
  husos: Huso[]
  /** exchange de la sesión objetivo de la predicción protagonista de /hoy */
  objetivo?: string | null
  /** predicciones vigentes (de /api/aperturas) — alimentan tooltip y flecha */
  predicciones?: Prediccion[]
}) {
  const [abierta, setAbierta] = useState(true)
  const [hover, setHover] = useState<Huso | null>(null)
  // re-render cada 30s: el marcador avanza y los cruces de borde se detectan
  const [ahoraMs, setAhoraMs] = useState(() => Date.now())
  useEffect(() => {
    const id = setInterval(() => setAhoraMs(Date.now()), 30_000)
    return () => clearInterval(id)
  }, [])

  // ancho real del contenedor: el marcador se mueve con translateX en px
  // (compositor puro) alineado al mismo sistema de % de las píldoras
  const contRef = useRef<HTMLDivElement | null>(null)
  const [ancho, setAncho] = useState(0)
  useEffect(() => {
    const el = contRef.current
    if (!el) return
    const ro = new ResizeObserver(() => setAncho(el.clientWidth))
    ro.observe(el)
    setAncho(el.clientWidth)
    return () => ro.disconnect()
  }, [abierta])

  const ny = husos.find((h) => h.exchange === 'XNYS')
  const inicioEje = useMemo(
    () => (ny ? inicioEjeGlobal(ny.cierre_utc) : Date.now() - 12 * 3600 * 1000),
    [ny],
  )

  if (husos.length === 0) return null

  const ahora = posAhora(inicioEje)
  const proximaAsia = husos.find(
    (h) =>
      h.region === 'asia' &&
      ['proxima', 'abierta'].includes(estadoEfectivo(h, ahoraMs)),
  )
  const prediccionesDe = (h: Huso) =>
    predicciones.filter(
      (p) => p.exchange === h.exchange && p.sesion_objetivo === h.sesion,
    )
  const hayViaje = proximaAsia != null && prediccionesDe(proximaAsia).length > 0

  const segmentoColor = (h: Huso) => {
    if (h.exchange === objetivo) return 'bg-magenta'
    const est = estadoEfectivo(h, ahoraMs)
    return est === 'abierta'
      ? 'bg-cyan'
      : est === 'proxima'
        ? 'bg-cyan-dim'
        : 'bg-border-strong'
  }

  return (
    <div className="relative border-b border-border bg-bg-1">
      <button
        onClick={() => setAbierta(!abierta)}
        aria-expanded={abierta}
        aria-label={abierta ? 'Colapsar cinta de husos' : 'Expandir cinta de husos'}
        className="absolute right-2 top-1 z-10 rounded px-2 text-[10px] text-text-3 hover:bg-bg-2 hover:text-text-2"
      >
        {abierta ? '▾' : '▸ husos'}
      </button>

      {abierta ? (
        <div ref={contRef} className="relative mx-auto h-[56px] max-w-[1400px] px-4">
          {/* flecha de contagio: del cierre de NY a la próxima sesión asiática.
              El pulso de flujo SOLO cuando viajan predicciones vigentes. */}
          {proximaAsia && (
            <svg
              className="pointer-events-none absolute inset-0 h-full w-full"
              preserveAspectRatio="none"
              viewBox="0 0 100 56"
            >
              <line
                x1="0.5"
                y1="40"
                x2={posEnEje(proximaAsia.apertura_utc, inicioEje) * 100}
                y2="6"
                stroke="var(--color-magenta)"
                strokeWidth="0.35"
                strokeDasharray="1.6 1.6"
                className={hayViaje ? 'flecha-viva' : ''}
                opacity="0.7"
                vectorEffect="non-scaling-stroke"
              />
            </svg>
          )}

          {/* carriles con bloques de sesión. La etiqueta vive FUERA de la
              píldora: dentro de 8px el texto sangraba sobre los bordes. */}
          {husos.map((h) => {
            const ini = posEnEje(h.apertura_utc, inicioEje)
            const fin = posEnEje(h.cierre_utc, inicioEje)
            const anchoP = Math.max(fin - ini, 0.012)
            const y = 2 + (CARRIL[h.exchange] ?? 4) * 8.5
            const est = estadoEfectivo(h, ahoraMs)
            const esObjetivo = h.exchange === objetivo
            const fondo =
              est === 'abierta'
                ? 'bg-bg-3'
                : est === 'proxima'
                  ? 'bg-bg-2 pulso-lento'
                  : `bg-bg-2 ${esObjetivo ? '' : 'opacity-50'}`
            const borde = esObjetivo
              ? 'border border-dashed border-magenta'
              : est === 'abierta'
                ? 'border border-cyan'
                : est === 'proxima'
                  ? 'border border-cyan-dim'
                  : 'border border-border'
            const tinta =
              est === 'abierta'
                ? 'text-text-1'
                : est === 'proxima'
                  ? 'text-text-2'
                  : 'text-text-3'
            const etiquetaPos =
              fin < 0.88
                ? { left: `calc(${fin * 100}% + 4px)` }
                : { right: `calc(${(1 - ini) * 100}% + 4px)` }
            return (
              <Fragment key={h.exchange}>
                <div
                  onMouseEnter={() => setHover(h)}
                  onMouseLeave={() => setHover(null)}
                  className={`pildora-huso absolute h-[8px] cursor-default rounded-sm ${borde} ${fondo}`}
                  style={{ left: `${ini * 100}%`, width: `${anchoP * 100}%`, top: y }}
                />
                <span
                  className={`pointer-events-none absolute flex h-[8px] items-center whitespace-nowrap text-[9px] leading-none ${tinta}`}
                  style={{ top: y, ...etiquetaPos }}
                >
                  {h.nombre.split(' · ')[0]}
                  {esObjetivo && <span className="ml-1 text-magenta">objetivo</span>}
                </span>
              </Fragment>
            )
          })}

          {/* marcador "ahora" (cian, vivo): translateX puro, avanza cada 30s */}
          <div
            className="marcador-ahora absolute left-0 top-1 bottom-4 w-px bg-cyan"
            style={{ transform: `translateX(${ahora * ancho}px)` }}
          >
            <div className="absolute -top-0.5 -left-[2.5px] h-1.5 w-1.5 rounded-full bg-cyan" />
          </div>

          {/* eje: horas de Chile cada 4h, arrancando en el cierre de NY */}
          <div className="absolute inset-x-4 bottom-0.5 h-3">
            {marcasEje(inicioEje).map((m) => (
              <span
                key={m.pos}
                className="num absolute -translate-x-1/2 text-[9px] text-text-3"
                style={{ left: `${m.pos * 100}%` }}
              >
                {m.etiqueta}
              </span>
            ))}
          </div>

          {/* tooltip refinado: hora local + Chile, contagio y predicciones */}
          {hover && (
            <div
              className="tooltip-cinta pointer-events-none absolute top-[58px] z-20 w-72 rounded border border-border-strong bg-bg-3 px-3 py-2 text-[11px] leading-relaxed text-text-2"
              style={{
                left: `${Math.min(posEnEje(hover.apertura_utc, inicioEje) * 100, 72)}%`,
              }}
            >
              <p className="font-medium text-text-1">{hover.nombre}</p>
              <p className="num">
                {horaLocalExchange(hover.apertura_utc, hover.exchange)}–
                {horaLocalExchange(hover.cierre_utc, hover.exchange)} local ·{' '}
                {horaChile(hover.apertura_utc)}–{horaChile(hover.cierre_utc)} Chile
              </p>
              <p className="num text-text-3">
                {estadoEfectivo(hover, ahoraMs) === 'abierta'
                  ? 'en sesión'
                  : estadoEfectivo(hover, ahoraMs) === 'proxima'
                    ? `abre ${distanciaHumana(hover.apertura_utc)}`
                    : 'cerrada'}
              </p>
              {hover.exchange === objetivo && (
                <p className="mt-1 text-magenta">
                  Sesión objetivo de la predicción de portada.
                </p>
              )}
              {hover.cerro_antes && (
                <p className="mt-1">
                  Antes cerró {hover.cerro_antes === 'XNYS' ? 'NY (SOX)' : hover.cerro_antes}
                  {hover.beta_contagio_promedio != null && (
                    <>
                      {' '}
                      — contagio β≈
                      <span className="num text-text-1">
                        {hover.beta_contagio_promedio.toFixed(2)}
                      </span>{' '}
                      sobre sus acciones
                    </>
                  )}
                </p>
              )}
              {prediccionesDe(hover).length > 0 && (
                <p className="mt-1 border-t border-border pt-1">
                  {prediccionesDe(hover).length} predicción
                  {prediccionesDe(hover).length > 1 ? 'es' : ''} apunta
                  {prediccionesDe(hover).length > 1 ? 'n' : ''} a esta sesión:{' '}
                  <span className="num text-text-1">
                    {prediccionesDe(hover)
                      .slice(0, 3)
                      .map((p) => `${p.nombre} ${p.estimado_pct >= 0 ? '+' : ''}${p.estimado_pct.toFixed(2)}%`)
                      .join(' · ')}
                    {prediccionesDe(hover).length > 3 &&
                      ` · +${prediccionesDe(hover).length - 3} más`}
                  </span>
                </p>
              )}
            </div>
          )}
        </div>
      ) : (
        /* colapsada: línea de 8px — sesiones como segmentos + marcador */
        <div
          ref={contRef}
          role="button"
          tabIndex={0}
          aria-label="Expandir cinta de husos"
          onClick={() => setAbierta(true)}
          onKeyDown={(e) => e.key === 'Enter' && setAbierta(true)}
          className="relative mx-auto h-[8px] max-w-[1400px] cursor-pointer px-4"
        >
          {husos.map((h) => {
            const ini = posEnEje(h.apertura_utc, inicioEje)
            const fin = posEnEje(h.cierre_utc, inicioEje)
            return (
              <div
                key={h.exchange}
                className={`pildora-huso absolute top-[3px] h-[2px] rounded-full ${segmentoColor(h)}`}
                style={{
                  left: `${ini * 100}%`,
                  width: `${Math.max(fin - ini, 0.008) * 100}%`,
                }}
              />
            )
          })}
          <div
            className="marcador-ahora absolute left-0 inset-y-0 w-px bg-cyan"
            style={{ transform: `translateX(${ahora * ancho}px)` }}
          />
        </div>
      )}
    </div>
  )
}
