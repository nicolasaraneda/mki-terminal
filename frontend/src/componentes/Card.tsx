import type { ReactNode } from 'react'
import { Estatus } from './CifraConIntervalo'

// Tarjeta base: jerarquía por fondo y borde, nunca sombra ni glow.
//
// `estatus` (corrida 12, bloque 2.1): el estatus evidencial de lo que la
// tarjeta muestra (MEDIDO, SIMULADO, PROPUESTA, RETIRADO...). Es un solo
// componente para todas las tarjetas porque la regla del proyecto —ninguna
// cifra en pantalla sin su estatus al lado— dejó de ser disciplina de quien
// escribe cada vista: tests/test_frontend_estatus.py exige que toda Card de
// una vista del riel de dinero lo declare, y acá se renderiza siempre igual.
export function Card({
  titulo,
  accion,
  estatus,
  children,
  className = '',
}: {
  titulo?: string
  accion?: ReactNode
  estatus?: string
  children: ReactNode
  className?: string
}) {
  const cabecera = titulo || accion || estatus
  return (
    <section className={`rounded-md border border-border bg-bg-1 ${className}`}>
      {cabecera && (
        <header className="flex items-center justify-between gap-3 border-b border-border px-4 py-2">
          <div className="flex flex-wrap items-baseline gap-3">
            {titulo && (
              <h2 className="font-display text-[13px] font-medium uppercase tracking-wider text-text-2">
                {titulo}
              </h2>
            )}
            {estatus && <Estatus valor={estatus} />}
          </div>
          {accion}
        </header>
      )}
      <div className="p-4">{children}</div>
    </section>
  )
}
