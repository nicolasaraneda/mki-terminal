import { useEffect } from 'react'

// Mapa de atajos (tecla ?): un overlay sobrio, mismo lenguaje que las cards.
const ATAJOS: [string, string][] = [
  ['g h', 'Hoy'],
  ['g a', 'Aperturas'],
  ['g c', 'Cadena'],
  ['g m', 'Mercados'],
  ['g r', 'Comparador'],
  ['g i', 'Análisis IA'],
  ['g t', 'Historial'],
  ['⌘K / Ctrl+K', 'Paleta de comandos'],
  ['?', 'Este mapa de atajos'],
  ['Esc', 'Cerrar overlays'],
]

export function AtajosOverlay({ alCerrar }: { alCerrar: () => void }) {
  useEffect(() => {
    const esc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' || e.key === '?') {
        e.preventDefault()
        alCerrar()
      }
    }
    window.addEventListener('keydown', esc)
    return () => window.removeEventListener('keydown', esc)
  }, [alCerrar])

  return (
    <div
      className="paleta-overlay fixed inset-0 z-50 bg-black/40"
      onClick={alCerrar}
      role="dialog"
      aria-modal="true"
      aria-label="Mapa de atajos de teclado"
    >
      <div
        className="paleta-panel mx-auto mt-[18vh] w-full max-w-sm rounded-md border border-border-strong bg-bg-1 p-4"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="font-display mb-3 text-[13px] font-medium uppercase tracking-wider text-text-2">
          Atajos de teclado
        </h2>
        <ul className="divide-y divide-border">
          {ATAJOS.map(([tecla, accion]) => (
            <li key={tecla} className="flex items-center justify-between py-1.5 text-[12px]">
              <span className="text-text-2">{accion}</span>
              <kbd className="num rounded border border-border bg-bg-2 px-1.5 py-0.5 text-[11px] text-text-1">
                {tecla}
              </kbd>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
