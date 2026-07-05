// Mini-serie inline (SVG puro): tendencia de un vistazo, sin ejes ni adorno.
export function Sparkline({
  valores,
  ancho = 120,
  alto = 28,
}: {
  valores: number[]
  ancho?: number
  alto?: number
}) {
  if (valores.length < 2) return null
  const min = Math.min(...valores)
  const max = Math.max(...valores)
  const rango = max - min || 1
  const puntos = valores
    .map((v, i) => {
      const x = (i / (valores.length - 1)) * ancho
      const y = alto - 2 - ((v - min) / rango) * (alto - 4)
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
  const sube = valores[valores.length - 1] >= valores[0]
  return (
    <svg width={ancho} height={alto} className="block">
      <polyline
        points={puntos}
        fill="none"
        stroke={sube ? 'var(--color-pos)' : 'var(--color-neg)'}
        strokeWidth="1.25"
        opacity="0.8"
      />
    </svg>
  )
}
