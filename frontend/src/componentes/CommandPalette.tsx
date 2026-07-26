import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApi } from '../lib/api'
import type { Instrumento } from '../lib/tipos'

// Command palette (Cmd+K) — sobrio, cero blur ornamental. Tres grupos:
// vistas, tickers del universo (nombre o símbolo) y acciones rápidas.
// Uno de los DOS lugares con --ease-asentar (el otro: flash de números).

interface Item {
  id: string
  titulo: string
  sub?: string
  grupo: 'Vistas' | 'Tickers' | 'Acciones'
  correr: () => void
}

const VISTAS: [string, string][] = [
  ['Hoy', '/hoy'],
  ['Aperturas', '/aperturas'],
  ['Cadena', '/cadena'],
  ['Mercados', '/mercados'],
  ['Comparador', '/comparador'],
  ['Análisis IA', '/analisis'],
  ['Historial', '/historial'],
  ['Laboratorio', '/laboratorio'],
  ['Salud', '/salud'],
]

const normalizar = (s: string) =>
  s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

export function CommandPalette({
  alCerrar,
  resumenDia,
}: {
  alCerrar: () => void
  resumenDia: string | null
}) {
  const navigate = useNavigate()
  const universo = useApi<{ instrumentos: Instrumento[] }>('/universo')
  const [consulta, setConsulta] = useState('')
  const [indice, setIndice] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const [copiado, setCopiado] = useState(false)

  useEffect(() => inputRef.current?.focus(), [])

  const items = useMemo<Item[]>(() => {
    const ir = (ruta: string) => () => {
      navigate(ruta)
      alCerrar()
    }
    const base: Item[] = VISTAS.map(([n, r]) => ({
      id: r,
      titulo: n,
      sub: r,
      grupo: 'Vistas',
      correr: ir(r),
    }))
    for (const i of universo.data?.datos.instrumentos ?? []) {
      base.push({
        id: `t-${i.ticker}`,
        titulo: i.nombre,
        sub: i.ticker,
        grupo: 'Tickers',
        correr: ir(`/detalle/${i.ticker}`),
      })
    }
    if (resumenDia) {
      base.push({
        id: 'a-copiar',
        titulo: copiado ? 'Resumen copiado ✓' : 'Copiar resumen del día',
        sub: 'IA, desde cache',
        grupo: 'Acciones',
        correr: () => {
          navigator.clipboard.writeText(resumenDia).then(() => {
            setCopiado(true)
            setTimeout(alCerrar, 600)
          })
        },
      })
    }
    base.push({
      id: 'a-snapshot',
      titulo: 'Ir al último snapshot',
      sub: 'Historial → snapshots emitidos',
      grupo: 'Acciones',
      correr: ir('/historial'),
    })
    return base
  }, [universo.data, resumenDia, copiado, navigate, alCerrar])

  const filtrados = useMemo(() => {
    const q = normalizar(consulta.trim())
    if (!q) return items.filter((i) => i.grupo !== 'Tickers').slice(0, 9)
    const enTitulo = (i: Item) => normalizar(i.titulo).includes(q)
    const enSub = (i: Item) => normalizar(i.sub ?? '').includes(q)
    const coincide = items.filter((i) => enTitulo(i) || enSub(i))
    coincide.sort((a, b) => {
      const pa = normalizar(a.titulo).startsWith(q) ? 0 : 1
      const pb = normalizar(b.titulo).startsWith(q) ? 0 : 1
      return pa - pb
    })
    return coincide.slice(0, 9)
  }, [consulta, items])

  useEffect(() => setIndice(0), [consulta])

  const alTeclear = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') alCerrar()
    else if (e.key === 'ArrowDown') {
      e.preventDefault()
      setIndice((i) => Math.min(i + 1, filtrados.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setIndice((i) => Math.max(i - 1, 0))
    } else if (e.key === 'Enter' && filtrados[indice]) {
      filtrados[indice].correr()
    }
  }

  return (
    <div
      className="paleta-overlay fixed inset-0 z-50 bg-black/40"
      onClick={alCerrar}
      role="dialog"
      aria-modal="true"
      aria-label="Paleta de comandos"
    >
      <div
        className="paleta-panel mx-auto mt-[14vh] w-full max-w-lg rounded-md border border-border-strong bg-bg-1"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          value={consulta}
          onChange={(e) => setConsulta(e.target.value)}
          onKeyDown={alTeclear}
          placeholder="Vista, ticker o acción…"
          aria-label="Buscar comando"
          className="w-full border-b border-border bg-transparent px-4 py-3 text-[13px] text-text-1 outline-none placeholder:text-text-3"
        />
        <ul className="max-h-80 overflow-y-auto py-1">
          {filtrados.map((item, i) => (
            <li key={item.id}>
              <button
                onClick={item.correr}
                onMouseEnter={() => setIndice(i)}
                className={`flex w-full items-baseline justify-between px-4 py-2 text-left text-[13px] ${
                  i === indice ? 'bg-bg-2 text-text-1' : 'text-text-2'
                }`}
              >
                <span>
                  {item.titulo}
                  {item.sub && (
                    <span className="num ml-2 text-[11px] text-text-3">{item.sub}</span>
                  )}
                </span>
                <span className="text-[10px] uppercase tracking-wider text-text-3">
                  {item.grupo}
                </span>
              </button>
            </li>
          ))}
          {filtrados.length === 0 && (
            <li className="px-4 py-3 text-[12px] text-text-3">
              Nada coincide con «{consulta}» — prueba un nombre de empresa o vista.
            </li>
          )}
        </ul>
        <p className="border-t border-border px-4 py-2 text-[10px] text-text-3">
          ↑↓ navegar · Enter abrir · Esc cerrar
        </p>
      </div>
    </div>
  )
}
