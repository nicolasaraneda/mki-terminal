import { NumeroVivo } from './NumeroVivo'

// Cifra grande con su incertidumbre AL LADO — nunca escondida en tooltip.
// La regla del producto: un número de señal sin muestra/R² no existe.
export function StatTile({
  etiqueta,
  valor,
  sufijo,
  detalle,
  tono = 'neutro',
  tooltip,
  valorNumerico,
  formato,
}: {
  etiqueta: string
  valor: string | number
  sufijo?: string
  /** incertidumbre o contexto: "n=120 · R²=0.28", "percentil 1 año", ... */
  detalle?: string
  /** frio/caliente: umbrales documentados del índice (ej. Roca→Chip <30 / >70) */
  tono?: 'pos' | 'neg' | 'neutro' | 'frio' | 'caliente'
  /** aclaración larga (densidad 4.6: caption extensa → tooltip) */
  tooltip?: string
  /** si se entregan, la cifra es un <NumeroVivo>: cuenta al cambiar (4.9) */
  valorNumerico?: number
  formato?: (v: number) => string
}) {
  const color =
    tono === 'pos'
      ? 'text-pos'
      : tono === 'neg'
        ? 'text-neg'
        : tono === 'frio'
          ? 'text-cyan'
          : tono === 'caliente'
            ? 'text-warn'
            : 'text-text-1'
  return (
    <div className="flex flex-col gap-1" title={tooltip}>
      <span className="text-[11px] font-medium uppercase tracking-wider text-text-3">
        {etiqueta}
      </span>
      <span className={`num text-2xl leading-none ${color}`}>
        {valorNumerico != null && formato ? (
          <NumeroVivo valor={valorNumerico} formato={formato} />
        ) : (
          valor
        )}
        {sufijo && <span className="ml-1 text-sm text-text-3">{sufijo}</span>}
      </span>
      {detalle && <span className="num text-[11px] text-text-3">{detalle}</span>}
    </div>
  )
}
