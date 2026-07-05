import type { ReactNode } from 'react'

// Tarjeta base: jerarquía por fondo y borde, nunca sombra ni glow.
export function Card({
  titulo,
  accion,
  children,
  className = '',
}: {
  titulo?: string
  accion?: ReactNode
  children: ReactNode
  className?: string
}) {
  return (
    <section className={`rounded-md border border-border bg-bg-1 ${className}`}>
      {(titulo || accion) && (
        <header className="flex items-center justify-between border-b border-border px-4 py-2.5">
          {titulo && (
            <h2 className="font-display text-[13px] font-medium uppercase tracking-wider text-text-2">
              {titulo}
            </h2>
          )}
          {accion}
        </header>
      )}
      <div className="p-4">{children}</div>
    </section>
  )
}
