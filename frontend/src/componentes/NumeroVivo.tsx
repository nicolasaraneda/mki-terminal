import { useEffect, useRef, useState } from 'react'

// Cifra que cuenta hacia su nuevo valor cuando CAMBIA (jamás en el primer
// render: un número sellado aparece quieto — es un registro, no un
// espectáculo) con un flash pos/neg que decae solo.
//
// Ancho estable: reserva el ancho en `ch` del string más largo visto para
// este valor (con tabular-nums todos los dígitos miden 1ch) — el count-up
// y el flash son pintura pura, cero reflow en tablas.
export function NumeroVivo({
  valor,
  formato,
  className = '',
}: {
  valor: number
  formato: (v: number) => string
  className?: string
}) {
  const [mostrado, setMostrado] = useState(valor)
  const [flash, setFlash] = useState<'pos' | 'neg' | null>(null)
  const previo = useRef(valor)
  const raf = useRef(0)

  useEffect(() => {
    const desde = previo.current
    if (valor === desde) return
    previo.current = valor
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setMostrado(valor)
      return
    }
    setFlash(valor > desde ? 'pos' : 'neg')
    const t0 = performance.now()
    const DUR = 300
    const paso = (t: number) => {
      const k = Math.min((t - t0) / DUR, 1)
      const e = 1 - Math.pow(1 - k, 3)
      setMostrado(desde + (valor - desde) * e)
      if (k < 1) raf.current = requestAnimationFrame(paso)
      else setFlash(null)
    }
    raf.current = requestAnimationFrame(paso)
    return () => cancelAnimationFrame(raf.current)
  }, [valor])

  const texto = formato(mostrado)
  const ancho = Math.max(formato(valor).length, texto.length)
  return (
    <span
      className={`num inline-block text-right ${
        flash === 'pos' ? 'flash-pos' : flash === 'neg' ? 'flash-neg' : ''
      } ${className}`}
      style={{ minWidth: `${ancho}ch` }}
    >
      {texto}
    </span>
  )
}
