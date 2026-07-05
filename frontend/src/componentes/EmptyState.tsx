// Estado vacío honesto: dice QUÉ falta y CUÁNDO habrá datos. Un 0/N del
// track record en maduración se muestra con naturalidad, nunca se esconde.
export function EmptyState({
  titulo,
  detalle,
}: {
  titulo: string
  detalle?: string
}) {
  return (
    <div className="flex flex-col items-center gap-1 rounded border border-dashed border-border px-4 py-8 text-center">
      <p className="text-[13px] text-text-2">{titulo}</p>
      {detalle && <p className="text-xs text-text-3">{detalle}</p>}
    </div>
  )
}

export function Cargando({ alto = 'h-24' }: { alto?: string }) {
  return <div className={`cargando w-full ${alto}`} />
}

export function ErrorCarga({ mensaje }: { mensaje: string }) {
  return (
    <div className="rounded border border-neg/30 bg-bg-2 px-4 py-3 text-xs text-neg">
      {mensaje}
    </div>
  )
}
