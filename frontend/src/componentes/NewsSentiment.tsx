import type { Titular } from '../lib/tipos'

function ColorSentimiento({ valor }: { valor: number | null }) {
  if (valor == null) return <span className="text-text-3">—</span>
  const clase = valor > 0.15 ? 'text-pos' : valor < -0.15 ? 'text-neg' : 'text-text-2'
  return <span className={`num ${clase}`}>{valor >= 0 ? '+' : ''}{valor.toFixed(2)}</span>
}

// Lista de titulares con su sentimiento — texto plano, sin emojis ni tarjetas
// promocionales. La fuente y la fecha siempre visibles.
export function NewsSentiment({ titulares }: { titulares: Titular[] }) {
  return (
    <ul className="divide-y divide-border">
      {titulares.map((t, i) => (
        <li key={i} className="flex items-start justify-between gap-3 py-2">
          <div className="min-w-0">
            {t.url ? (
              <a
                href={t.url}
                target="_blank"
                rel="noreferrer"
                className="text-[13px] leading-snug text-text-1 hover:underline"
              >
                {t.titular}
              </a>
            ) : (
              <p className="text-[13px] leading-snug text-text-1">{t.titular}</p>
            )}
            <p className="mt-0.5 text-[11px] text-text-3">
              {t.fuente} · {t.fecha}
              {t.tickers ? ` · ${t.tickers}` : ''}
            </p>
          </div>
          <ColorSentimiento valor={t.sentimiento} />
        </li>
      ))}
    </ul>
  )
}
