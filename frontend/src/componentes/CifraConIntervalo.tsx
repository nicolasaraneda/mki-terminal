// ============================================================
// CifraConIntervalo — la regla de honestidad, hecha componente.
//
// El proyecto tiene una regla que hasta ahora vivía en la disciplina de
// quien escribía cada vista: **ningún estimador puntual se muestra sin su
// intervalo**. Acá deja de ser disciplina. Este componente no puede
// renderizar un número sin intervalo: si no lo recibe, muestra por qué
// falta en vez del número. Es la misma idea que la del resto del sistema —
// la corrección va al ejecutable, no a la prosa.
//
// Y cuando el intervalo contiene el cero, lo dice **con palabras**, no
// sólo con una banda: una banda que cruza el cero se lee como «casi
// significativo» si nadie la nombra.
// ============================================================
export function CifraConIntervalo({
  etiqueta,
  valor,
  intervalo,
  unidad = 'pp',
  tipoIntervalo,
  n,
  decimales = 2,
  faltaPorque,
}: {
  etiqueta: string
  valor: number | null | undefined
  intervalo: [number, number] | null | undefined
  unidad?: string
  tipoIntervalo?: string
  n?: number | string | null
  decimales?: number
  faltaPorque?: string
}) {
  const hay = valor != null && Number.isFinite(valor)
  const hayIC =
    intervalo != null &&
    Number.isFinite(intervalo[0]) &&
    Number.isFinite(intervalo[1])

  if (!hay || !hayIC) {
    return (
      <div className="rounded border border-border bg-bg-2 px-3 py-2">
        <div className="mini-label text-text-3">{etiqueta}</div>
        <div className="mt-1 text-[12px] leading-snug text-text-2">
          {faltaPorque ??
            (hay
              ? 'sin intervalo computado: la cifra no se muestra sola'
              : 'sin dato')}
        </div>
      </div>
    )
  }

  const cruza = intervalo[0] <= 0 && 0 <= intervalo[1]
  const signo = valor > 0 ? '+' : ''
  return (
    <div className="rounded border border-border bg-bg-2 px-3 py-2">
      <div className="mini-label text-text-3">{etiqueta}</div>
      <div className="mt-1 font-mono text-[18px] tabular-nums text-text-1">
        {signo}
        {valor.toFixed(decimales)}
        <span className="ml-1 text-[11px] text-text-3">{unidad}</span>
      </div>
      <div className="mt-0.5 font-mono text-[11px] tabular-nums text-text-2">
        [{intervalo[0] >= 0 ? '+' : ''}
        {intervalo[0].toFixed(decimales)}, {intervalo[1] >= 0 ? '+' : ''}
        {intervalo[1].toFixed(decimales)}]
        {tipoIntervalo && <span className="ml-1 text-text-3">{tipoIntervalo}</span>}
      </div>
      {n != null && (
        <div className="mt-0.5 font-mono text-[11px] tabular-nums text-text-3">
          n = {n}
        </div>
      )}
      <div className="mt-1 text-[11px] leading-snug text-text-2">
        {cruza
          ? 'El intervalo contiene el cero: la diferencia no se distingue de cero.'
          : 'El intervalo no contiene el cero.'}
      </div>
    </div>
  )
}

// Rótulo de estatus evidencial. Sin color semántico de acierto/error: un
// SIMULADO no es «malo», es otra clase de afirmación.
export function Estatus({ valor }: { valor: string }) {
  return (
    <span className="rounded border border-border bg-bg-2 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide text-text-2">
      {valor.replace('_', ' ')}
    </span>
  )
}
