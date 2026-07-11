import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAperturas, useHoy, useSalud } from './lib/api'
import { CintaHusos } from './componentes/CintaHusos'
import { RegimeChip } from './componentes/RegimeChip'
import { fechaHoraChile } from './lib/tiempo'

// Navegación SIEMPRE con etiqueta de texto (anti-patrón prohibido: iconos
// solos). El orden replica el flujo del día: portal → análisis → historial.
const VISTAS = [
  { ruta: '/hoy', etiqueta: 'Hoy' },
  { ruta: '/aperturas', etiqueta: 'Aperturas' },
  { ruta: '/cadena', etiqueta: 'Cadena' },
  { ruta: '/mercados', etiqueta: 'Mercados' },
  { ruta: '/comparador', etiqueta: 'Comparador' },
  { ruta: '/analisis', etiqueta: 'Análisis IA' },
  { ruta: '/historial', etiqueta: 'Historial' },
]

export function Layout() {
  const salud = useSalud()
  const hoy = useHoy()
  const aperturas = useAperturas()
  const location = useLocation()
  const meta = salud.data?.meta
  const snapshotViejo = salud.data?.datos.snapshot_viejo ?? false

  return (
    <>
      {/* densidad tipo terminal: bajo 1024px la información no cabe con honestidad */}
      <div className="flex min-h-screen items-center justify-center p-8 lg:hidden">
        <p className="max-w-sm text-center text-[13px] leading-relaxed text-text-2">
          MKI Terminal está diseñado para pantallas de 1024px o más — la
          densidad de datos no se sacrifica. Abre esta ventana más grande o
          usa un monitor.
        </p>
      </div>
      <div className="hidden min-h-screen flex-col lg:flex">
      <header className="flex items-center gap-4 border-b border-border bg-bg-1 px-4 py-2">
        <h1 className="font-display text-[15px] font-semibold tracking-tight text-text-1">
          MKI <span className="text-text-3">Terminal</span>
        </h1>
        <RegimeChip etiqueta={meta?.regimen ?? null} />
        <div className="ml-auto flex items-center gap-3 text-[11px] text-text-3">
          {meta?.snapshot_hoy ? (
            <span className="num">
              snapshot {fechaHoraChile(meta.snapshot_hoy.timestamp_utc)} ·{' '}
              {meta.snapshot_hoy.origen}
            </span>
          ) : (
            <span>sin snapshot hoy</span>
          )}
        </div>
      </header>

      {hoy.data && (
        <CintaHusos
          husos={hoy.data.datos.husos}
          objetivo={hoy.data.datos.proxima_apertura?.exchange ?? null}
          predicciones={aperturas.data?.datos.predicciones ?? []}
        />
      )}

      {snapshotViejo && (
        <div className="border-b border-warn/25 bg-bg-1 px-4 py-1.5 text-[11px] text-warn">
          El último snapshot tiene más de un día hábil — las señales mostradas
          pueden estar desactualizadas.
        </div>
      )}

      <div className="flex flex-1">
        <nav className="w-40 shrink-0 border-r border-border bg-bg-1 py-3">
          {VISTAS.map((v) => (
            <NavLink
              key={v.ruta}
              to={v.ruta}
              className={({ isActive }) =>
                `block border-l-2 px-4 py-1.5 text-[13px] ${
                  isActive
                    ? 'border-cyan bg-bg-2 font-medium text-text-1'
                    : 'border-transparent text-text-2 hover:bg-bg-2 hover:text-text-1'
                }`
              }
            >
              {v.etiqueta}
            </NavLink>
          ))}
        </nav>

        <main className="min-w-0 flex-1 p-4">
          {/* keyed por ruta: la coreografía de entrada corre UNA vez por
              navegación; los re-renders no la re-disparan */}
          <div key={location.pathname} className="vista">
            <Outlet />
          </div>
        </main>
      </div>

      <footer className="border-t border-border px-4 py-2 text-[11px] text-text-3">
        MKI Terminal no constituye asesoría financiera. Datos: yfinance (diario).
        Último snapshot:{' '}
        <span className="num">
          {meta?.snapshot_hoy ? fechaHoraChile(meta.snapshot_hoy.timestamp_utc) : '—'}
        </span>{' '}
        · modelo v{meta?.modelo_version ?? '—'}
      </footer>
      </div>
    </>
  )
}
