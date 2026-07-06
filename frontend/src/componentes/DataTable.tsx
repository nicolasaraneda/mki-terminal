import type { ReactNode } from 'react'

export interface Columna<T> {
  clave: string
  titulo: string
  alinear?: 'izq' | 'der'
  /** aclaración de la cabecera (umbral, definición) — visible al hover */
  tooltip?: string
  render: (fila: T) => ReactNode
}

// Tabla densa estilo terminal: números monoespaciados alineados a la
// derecha, filas compactas, sin zebra — separación por borde sutil.
export function DataTable<T>({
  columnas,
  filas,
  clavePor,
  alClic,
}: {
  columnas: Columna<T>[]
  filas: T[]
  clavePor: (fila: T) => string
  alClic?: (fila: T) => void
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-xs">
        <thead>
          <tr className="border-b border-border-strong">
            {columnas.map((c) => (
              <th
                key={c.clave}
                title={c.tooltip}
                className={`px-2 py-1.5 text-[11px] font-medium uppercase tracking-wider text-text-3 ${
                  c.alinear === 'der' ? 'text-right' : 'text-left'
                } ${c.tooltip ? 'cursor-help underline decoration-dotted decoration-border-strong underline-offset-2' : ''}`}
              >
                {c.titulo}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((f) => (
            <tr
              key={clavePor(f)}
              onClick={alClic ? () => alClic(f) : undefined}
              className={`border-b border-border last:border-0 ${
                alClic ? 'cursor-pointer hover:bg-bg-2' : ''
              }`}
            >
              {columnas.map((c) => (
                <td
                  key={c.clave}
                  className={`px-2 py-1.5 ${
                    c.alinear === 'der' ? 'num text-right' : 'text-left'
                  }`}
                >
                  {c.render(f)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
