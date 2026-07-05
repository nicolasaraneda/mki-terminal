// Heatmap de correlaciones como tabla coloreada por celda — denso y legible,
// sin librería: una correlación es un número, no una ilustración.
export function CorrHeatmap({
  filas,
  columnas,
}: {
  filas: { nombre: string; valores: (number | null)[] }[]
  columnas: string[]
}) {
  const color = (v: number | null) => {
    if (v == null) return 'transparent'
    const a = Math.min(Math.abs(v), 1) * 0.55
    return v >= 0 ? `rgba(52,211,153,${a})` : `rgba(248,113,113,${a})`
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-xs">
        <thead>
          <tr className="border-b border-border-strong">
            <th className="px-2 py-1.5 text-left text-[11px] font-medium uppercase tracking-wider text-text-3" />
            {columnas.map((c) => (
              <th
                key={c}
                className="num px-2 py-1.5 text-right text-[11px] font-medium text-text-3"
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((f) => (
            <tr key={f.nombre} className="border-b border-border last:border-0">
              <td className="px-2 py-1.5 text-text-2">{f.nombre}</td>
              {f.valores.map((v, i) => (
                <td
                  key={i}
                  className="num px-2 py-1.5 text-right text-text-1"
                  style={{ backgroundColor: color(v) }}
                >
                  {v == null ? '—' : v.toFixed(2)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
