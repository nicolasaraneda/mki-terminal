// Chip del régimen vigente, siempre visible en el header. Uno de los 4
// usos de cian permitidos por vista.
export function RegimeChip({ etiqueta }: { etiqueta: string | null }) {
  if (!etiqueta) {
    return (
      <span className="rounded border border-border px-2 py-0.5 text-[11px] text-text-3">
        régimen: sin datos
      </span>
    )
  }
  return (
    <span className="rounded border border-cyan-dim bg-bg-2 px-2 py-0.5 text-[11px] font-medium text-cyan">
      {etiqueta}
    </span>
  )
}
