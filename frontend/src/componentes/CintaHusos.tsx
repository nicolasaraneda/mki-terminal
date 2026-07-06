import { Fragment, useEffect, useMemo, useState } from 'react'
import type { Huso } from '../lib/tipos'
import {
  distanciaHumana,
  horaChile,
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
// hacia Asia (flecha magenta punteada). Tres carriles descendentes:
// Asia arriba → Europa al centro → EE.UU. abajo. Todo en hora de Chile.
// Máx 56px, colapsable. Presupuesto de cian: el marcador "ahora" y la
// próxima sesión en abrir.
// ============================================================

// Un micro-carril por bolsa (no por región): las tres asiáticas transan casi
// a la misma hora y en un carril compartido se taparían entre sí. El orden
// sigue descendiendo Asia → Europa → EE.UU., que es la tesis de la cinta.
const CARRIL: Record<string, number> = {
  XKRX: 0,
  XTKS: 1,
  XTAI: 2,
  XETR: 3,
  XNYS: 4,
}

export function CintaHusos({
  husos,
  objetivo = null,
}: {
  husos: Huso[]
  /** exchange de la sesión objetivo de la predicción protagonista de /hoy:
   *  borde magenta punteado + etiqueta, conectando con "Próxima apertura" */
  objetivo?: string | null
}) {
  const [abierta, setAbierta] = useState(true)
  const [hover, setHover] = useState<Huso | null>(null)
  // re-render por minuto para que el marcador "ahora" avance
  const [, setTic] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setTic((t) => t + 1), 60_000)
    return () => clearInterval(id)
  }, [])

  const ny = husos.find((h) => h.exchange === 'XNYS')
  const inicioEje = useMemo(
    () => (ny ? inicioEjeGlobal(ny.cierre_utc) : Date.now() - 12 * 3600 * 1000),
    [ny],
  )

  if (husos.length === 0) return null

  const ahora = posAhora(inicioEje)
  const proximaAsia = husos.find(
    (h) => h.region === 'asia' && (h.estado === 'proxima' || h.estado === 'abierta'),
  )

  return (
    <div className="relative border-b border-border bg-bg-1">
      <button
        onClick={() => setAbierta(!abierta)}
        aria-expanded={abierta}
        aria-label={abierta ? 'Colapsar cinta de husos' : 'Expandir cinta de husos'}
        className="absolute right-2 top-1 z-10 rounded px-1.5 text-[10px] text-text-3 hover:bg-bg-2 hover:text-text-2"
      >
        {abierta ? '▾' : '▸ husos'}
      </button>

      {abierta && (
        <div className="relative mx-auto h-[56px] max-w-[1400px] px-4">
          {/* flecha de contagio: del cierre de NY a la próxima sesión asiática */}
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
                className="flecha-contagio"
                opacity="0.7"
                vectorEffect="non-scaling-stroke"
              />
            </svg>
          )}

          {/* carriles con bloques de sesión. La etiqueta vive FUERA de la
              píldora (al lado): dentro de 8px el texto sangraba sobre los
              bordes y los carriles asiáticos se encimaban entre sí. */}
          {husos.map((h) => {
            const ini = posEnEje(h.apertura_utc, inicioEje)
            const fin = posEnEje(h.cierre_utc, inicioEje)
            const ancho = Math.max(fin - ini, 0.012)
            const y = 2 + (CARRIL[h.exchange] ?? 4) * 8.5
            const esObjetivo = h.exchange === objetivo
            const fondo =
              h.estado === 'abierta'
                ? 'bg-bg-3'
                : h.estado === 'proxima'
                  ? 'bg-bg-2 pulso-lento'
                  : `bg-bg-2 ${esObjetivo ? '' : 'opacity-50'}`
            const borde = esObjetivo
              ? 'border border-dashed border-magenta'
              : h.estado === 'abierta'
                ? 'border border-cyan'
                : h.estado === 'proxima'
                  ? 'border border-cyan-dim'
                  : 'border border-border'
            const tinta =
              h.estado === 'abierta'
                ? 'text-text-1'
                : h.estado === 'proxima'
                  ? 'text-text-2'
                  : 'text-text-3'
            // etiqueta a la derecha de la píldora; cerca del borde derecho
            // del eje, a la izquierda — jamás fuera de la cinta
            const etiquetaPos =
              fin < 0.88
                ? { left: `calc(${fin * 100}% + 4px)` }
                : { right: `calc(${(1 - ini) * 100}% + 4px)` }
            return (
              <Fragment key={h.exchange}>
                <div
                  onMouseEnter={() => setHover(h)}
                  onMouseLeave={() => setHover(null)}
                  className={`absolute h-[8px] cursor-default rounded-sm ${borde} ${fondo}`}
                  style={{ left: `${ini * 100}%`, width: `${ancho * 100}%`, top: y }}
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

          {/* marcador "ahora" (cian, vivo) */}
          <div
            className="absolute top-1 bottom-4 w-px bg-cyan"
            style={{ left: `${ahora * 100}%` }}
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

          {/* tooltip: qué cerró antes y con qué beta viaja el contagio */}
          {hover && (
            <div
              className="pointer-events-none absolute top-[58px] z-20 w-64 rounded border border-border-strong bg-bg-3 px-3 py-2 text-[11px] leading-relaxed text-text-2"
              style={{
                left: `${Math.min(posEnEje(hover.apertura_utc, inicioEje) * 100, 75)}%`,
              }}
            >
              <p className="font-medium text-text-1">{hover.nombre}</p>
              <p className="num">
                {horaChile(hover.apertura_utc)}–{horaChile(hover.cierre_utc)} Chile ·{' '}
                {hover.estado === 'abierta'
                  ? 'en sesión'
                  : hover.estado === 'proxima'
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
            </div>
          )}
        </div>
      )}
    </div>
  )
}
