// Estado vacío honesto: dice QUÉ falta y CUÁNDO/CÓMO habrá datos. Un 0/N del
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

/* ============================================================
   Skeletons (4.9 F4): pulso sutil en bg-2 con las proporciones del
   contenido real — cero saltos de layout al cargar. Nada de shimmer.
   ============================================================ */

/** Fila de StatTiles como la real: etiqueta, cifra grande, detalle. */
export function EsqueletoTiles({ n = 4 }: { n?: number }) {
  return (
    <div className="rounded-md border border-border bg-bg-1 p-4">
      <div
        className="grid grid-cols-2 gap-6 sm:grid-cols-4"
        style={{ gridTemplateColumns: `repeat(${n}, minmax(0, 1fr))` }}
      >
        {Array.from({ length: n }).map((_, i) => (
          <div key={i} className="flex flex-col gap-2">
            <div className="cargando h-3 w-20" />
            <div className="cargando h-7 w-24" />
            <div className="cargando h-3 w-28" />
          </div>
        ))}
      </div>
    </div>
  )
}

/** Card con tabla: cabecera + filas con la altura real de una fila densa. */
export function EsqueletoTabla({ filas = 8 }: { filas?: number }) {
  return (
    <div className="rounded-md border border-border bg-bg-1">
      <div className="border-b border-border px-4 py-2">
        <div className="cargando h-3.5 w-48" />
      </div>
      <div className="p-4">
        <div className="cargando mb-2 h-4 w-full" />
        {Array.from({ length: filas }).map((_, i) => (
          <div key={i} className="cargando mb-2 h-7 w-full" />
        ))}
      </div>
    </div>
  )
}

/** Card genérica con título y cuerpo de la altura del contenido real. */
export function EsqueletoCard({
  alto,
  conTitulo = true,
}: {
  alto: string
  conTitulo?: boolean
}) {
  return (
    <div className="rounded-md border border-border bg-bg-1">
      {conTitulo && (
        <div className="border-b border-border px-4 py-2">
          <div className="cargando h-3.5 w-40" />
        </div>
      )}
      <div className="p-4">
        <div className={`cargando w-full ${alto}`} />
      </div>
    </div>
  )
}

/* Error accionable (4.9 F4): causa visible + reintento — nunca una vista
   rota o en blanco. */
export function ErrorCarga({
  mensaje,
  alReintentar,
}: {
  mensaje: string
  alReintentar?: () => void
}) {
  return (
    <div className="mx-auto flex max-w-6xl items-center gap-3 rounded-md border border-neg/30 bg-bg-1 px-4 py-3">
      <div className="min-w-0 flex-1">
        <p className="text-[13px] text-text-1">No se pudieron cargar los datos</p>
        <p className="mt-1 truncate text-xs text-text-3" title={mensaje}>
          {mensaje} — ¿está corriendo la API en :8000? (uvicorn api.main:app)
        </p>
      </div>
      {alReintentar && (
        <button
          onClick={alReintentar}
          className="shrink-0 rounded border border-border bg-bg-2 px-3 py-2 text-xs text-text-2 hover:border-border-strong hover:text-text-1"
        >
          Reintentar
        </button>
      )}
    </div>
  )
}
