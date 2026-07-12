import { useEffect, useRef } from 'react'

// Atajos globales de teclado (4.9 F3). Secuencias estilo "g luego h"
// (ventana de 1s), Cmd/Ctrl+K para el palette, ? para el mapa de atajos.
// Jamás interfiere cuando el usuario escribe en un input/select/textarea.

export const RUTAS_ATAJO: Record<string, string> = {
  h: '/hoy',
  a: '/aperturas',
  c: '/cadena',
  m: '/mercados',
  r: '/comparador',
  i: '/analisis',
  t: '/historial',
}

function escribiendo(e: KeyboardEvent): boolean {
  const t = e.target as HTMLElement | null
  return (
    t != null &&
    (t.tagName === 'INPUT' ||
      t.tagName === 'TEXTAREA' ||
      t.tagName === 'SELECT' ||
      t.isContentEditable)
  )
}

export function useAtajos({
  abrirPaleta,
  alternarAyuda,
  navegar,
  hayOverlay,
}: {
  abrirPaleta: () => void
  alternarAyuda: () => void
  navegar: (ruta: string) => void
  /** con un overlay abierto, solo vive Cmd+K (el overlay maneja su Esc) */
  hayOverlay: boolean
}) {
  const g = useRef<number | null>(null)
  const refs = useRef({ abrirPaleta, alternarAyuda, navegar, hayOverlay })
  refs.current = { abrirPaleta, alternarAyuda, navegar, hayOverlay }

  useEffect(() => {
    const alTeclear = (e: KeyboardEvent) => {
      const { abrirPaleta, alternarAyuda, navegar, hayOverlay } = refs.current
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        abrirPaleta()
        return
      }
      if (escribiendo(e) || hayOverlay || e.metaKey || e.ctrlKey || e.altKey) return
      if (e.key === '?') {
        e.preventDefault()
        alternarAyuda()
        return
      }
      const ahora = Date.now()
      if (g.current != null && ahora - g.current < 1000) {
        const ruta = RUTAS_ATAJO[e.key.toLowerCase()]
        g.current = null
        if (ruta) {
          e.preventDefault()
          navegar(ruta)
        }
        return
      }
      g.current = e.key.toLowerCase() === 'g' ? ahora : null
    }
    window.addEventListener('keydown', alTeclear)
    return () => window.removeEventListener('keydown', alTeclear)
  }, [])
}
