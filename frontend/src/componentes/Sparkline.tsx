// Mini-serie inline (SVG puro): tendencia de un vistazo, sin ejes ni adorno.
// Regla 4.7.1: los sparklines son CONTEXTO y van siempre en gris neutro —
// el color queda reservado para la cifra principal cuando cruza umbrales
// definidos; una mini-línea roja junto a un índice en zona neutra grita
// una alarma que los datos no dicen.
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
  return (
    <svg width={ancho} height={alto} className="block">
      <polyline
        points={puntos}
        fill="none"
        stroke="var(--color-text-3)"
        strokeWidth="1.25"
        opacity="0.9"
      />
    </svg>
  )
}
