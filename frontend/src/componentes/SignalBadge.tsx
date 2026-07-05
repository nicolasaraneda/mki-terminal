import { fechaHoraChile } from '../lib/tiempo'

// Una señal con su porqué y su incertidumbre. El pie con la hora de emisión
// es OBLIGATORIO cuando existe: es la garantía anti look-ahead hecha UI.
export function SignalBadge({
  titulo,
  direccion,
  magnitud,
  porque,
  nMuestra,
  r2,
  emitidaUtc,
}: {
  titulo: string
  direccion: 'pos' | 'neg' | 'neutra'
  magnitud: string
  porque: string
  nMuestra?: number | null
  r2?: number | null
  emitidaUtc?: string | null
}) {
  const borde =
    direccion === 'pos'
      ? 'border-l-pos'
      : direccion === 'neg'
        ? 'border-l-neg'
        : 'border-l-border-strong'
  return (
    <article className={`rounded border border-border border-l-2 ${borde} bg-bg-2 px-3 py-2.5`}>
      <h3 className="text-[13px] font-medium text-text-1">{titulo}</h3>
      <p className="num mt-0.5 text-xs text-text-2">{magnitud}</p>
      <p className="mt-1 text-xs leading-relaxed text-text-3">{porque}</p>
      {(nMuestra != null || r2 != null) && (
        <p className="num mt-1 text-[11px] text-text-3">
          {nMuestra != null && `n=${nMuestra}`}
          {nMuestra != null && r2 != null && ' · '}
          {r2 != null && `R² hist=${r2.toFixed(2)}`}
        </p>
      )}
      {emitidaUtc && (
        <footer className="mt-1.5 border-t border-border pt-1.5 text-[11px] text-text-3">
          emitida {fechaHoraChile(emitidaUtc)}, antes de la apertura objetivo
        </footer>
      )}
    </article>
  )
}
