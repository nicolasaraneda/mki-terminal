import { useMemo, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useApi } from '../lib/api'
import type { DatosComparador } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { DataTable, type Columna } from '../componentes/DataTable'
import { Cargando, EmptyState, ErrorCarga } from '../componentes/EmptyState'

// ============================================================
// /comparador — rendimiento base 100 de 2+ acciones del universo,
// en USD (comparable) o moneda local, contra el benchmark SMH.
// El universo se lee de la API (eslabones de /api/cadena): el frontend
// no tiene lista propia de tickers.
// ============================================================

// Paleta sobria para líneas (sin neón); el benchmark va punteado gris.
const COLORES = ['#7dd3fc', '#f9a8d4', '#86efac', '#fcd34d', '#c4b5fd', '#fda4af', '#5eead4', '#a5b4fc']

const PERIODOS = [
  { etiqueta: '3M', dias: 91 },
  { etiqueta: '6M', dias: 182 },
  { etiqueta: '1A', dias: 365 },
  { etiqueta: '2A', dias: 730 },
]

const pct = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(1)}`

export function Comparador() {
  const [seleccion, setSeleccion] = useState<string[]>(['NVDA', 'AMD', '2330.TW'])
  const [base, setBase] = useState<'usd' | 'local'>('usd')
  const [dias, setDias] = useState(365)

  const universoApi = useApi<{
    instrumentos: { ticker: string; nombre: string; segmento: string; tipo: string }[]
  }>('/universo')
  const desde = useMemo(() => {
    const f = new Date(Date.now() - dias * 24 * 3600 * 1000)
    return f.toISOString().slice(0, 10)
  }, [dias])

  const habilitado = seleccion.length >= 2
  const comparador = useApi<DatosComparador>(
    `/comparador?tickers=${seleccion.join(',')}&base=${base}&desde=${desde}`,
  )

  const universo = universoApi.data?.datos.instrumentos ?? []

  const alternar = (ticker: string) =>
    setSeleccion((s) =>
      s.includes(ticker) ? s.filter((t) => t !== ticker) : [...s, ticker],
    )

  // series {T: {fechas, valores}} → filas por fecha para Recharts
  const filasGrafico = useMemo(() => {
    if (!comparador.data) return []
    const d = comparador.data.datos
    const porFecha = new Map<string, Record<string, number | string>>()
    const agrega = (nombre: string, fechas: string[], valores: number[]) => {
      fechas.forEach((f, i) => {
        if (!porFecha.has(f)) porFecha.set(f, { fecha: f })
        porFecha.get(f)![nombre] = valores[i]
      })
    }
    Object.entries(d.series).forEach(([t, s]) => agrega(t, s.fechas, s.valores))
    if (d.benchmark) agrega(d.benchmark.ticker, d.benchmark.fechas, d.benchmark.valores)
    return [...porFecha.values()].sort((a, b) =>
      String(a.fecha).localeCompare(String(b.fecha)),
    )
  }, [comparador.data])

  type FilaTabla = DatosComparador['tabla'][number]
  const columnas: Columna<FilaTabla>[] = [
    {
      clave: 'accion',
      titulo: 'Acción',
      render: (f) => (
        <>
          <span className="text-text-1">{f.nombre}</span>{' '}
          <span className="num text-text-3">{f.ticker}</span>
        </>
      ),
    },
    { clave: 'segmento', titulo: 'Segmento', render: (f) => f.segmento },
    {
      clave: 'ret',
      titulo: 'Ret. período',
      alinear: 'der',
      render: (f) => (
        <span className={f.ret_periodo_pct >= 0 ? 'text-pos' : 'text-neg'}>
          {pct(f.ret_periodo_pct)}%
        </span>
      ),
    },
    {
      clave: 'vol',
      titulo: 'Vol. anual',
      alinear: 'der',
      render: (f) => `${f.vol_anual_pct.toFixed(1)}%`,
    },
    {
      clave: 'mom',
      titulo: 'Mom. 20d',
      alinear: 'der',
      render: (f) => (
        <span className={f.momentum_20d_pct >= 0 ? 'text-pos' : 'text-neg'}>
          {pct(f.momentum_20d_pct)}%
        </span>
      ),
    },
    {
      clave: 'puntaje',
      titulo: 'Puntaje v0',
      alinear: 'der',
      render: (f) => (f.puntaje_v0 != null ? f.puntaje_v0.toFixed(2) : '—'),
    },
  ]

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      {/* selector */}
      <Card titulo="Selección">
        {universoApi.isLoading && <Cargando alto="h-16" />}
        {universo.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {universo.map((t) => {
              const activo = seleccion.includes(t.ticker)
              return (
                <button
                  key={t.ticker}
                  onClick={() => alternar(t.ticker)}
                  aria-pressed={activo}
                  className={`rounded border px-2 py-1 text-[11px] ${
                    activo
                      ? 'border-border-strong bg-bg-3 text-text-1'
                      : 'border-border bg-bg-1 text-text-3 hover:bg-bg-2 hover:text-text-2'
                  }`}
                >
                  {t.nombre}
                </button>
              )
            })}
          </div>
        )}
        <div className="mt-3 flex items-center gap-4 border-t border-border pt-3 text-[11px]">
          <div className="flex gap-1">
            {(['usd', 'local'] as const).map((b) => (
              <button
                key={b}
                onClick={() => setBase(b)}
                aria-pressed={base === b}
                className={`rounded border px-2 py-1 ${
                  base === b
                    ? 'border-border-strong bg-bg-3 text-text-1'
                    : 'border-border text-text-3 hover:text-text-2'
                }`}
              >
                {b === 'usd' ? 'USD' : 'Moneda local'}
              </button>
            ))}
          </div>
          <div className="flex gap-1">
            {PERIODOS.map((p) => (
              <button
                key={p.etiqueta}
                onClick={() => setDias(p.dias)}
                aria-pressed={dias === p.dias}
                className={`rounded border px-2 py-1 ${
                  dias === p.dias
                    ? 'border-border-strong bg-bg-3 text-text-1'
                    : 'border-border text-text-3 hover:text-text-2'
                }`}
              >
                {p.etiqueta}
              </button>
            ))}
          </div>
          <span className="ml-auto text-text-3">
            {base === 'usd'
              ? 'USD: comparable entre bolsas — el efecto moneda está incluido'
              : 'Moneda local: lo que ve un inversionista de cada país'}
          </span>
        </div>
      </Card>

      {/* gráfico base 100 */}
      <Card titulo={`Rendimiento base 100 (${base === 'usd' ? 'USD' : 'local'})`}>
        {!habilitado ? (
          <EmptyState titulo="Selecciona al menos 2 acciones" />
        ) : comparador.isLoading ? (
          <Cargando alto="h-72" />
        ) : comparador.error ? (
          <ErrorCarga mensaje={String(comparador.error)} />
        ) : filasGrafico.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={filasGrafico} margin={{ top: 4, right: 4, bottom: 0, left: -16 }}>
              <CartesianGrid stroke="#161b26" vertical={false} />
              <XAxis
                dataKey="fecha"
                tick={{ fill: '#5d6679', fontSize: 10, fontFamily: 'JetBrains Mono' }}
                tickLine={false}
                axisLine={{ stroke: '#222939' }}
                minTickGap={70}
              />
              <YAxis
                tick={{ fill: '#5d6679', fontSize: 10, fontFamily: 'JetBrains Mono' }}
                tickLine={false}
                axisLine={false}
                domain={['auto', 'auto']}
              />
              <Tooltip
                contentStyle={{
                  background: '#1d2330',
                  border: '1px solid #303a50',
                  borderRadius: 4,
                  fontSize: 11,
                  fontFamily: 'JetBrains Mono',
                }}
                labelStyle={{ color: '#9aa3b7' }}
                formatter={(v) => Number(v).toFixed(1)}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              {seleccion.map((t, i) => (
                <Line
                  key={t}
                  type="monotone"
                  dataKey={t}
                  stroke={COLORES[i % COLORES.length]}
                  strokeWidth={1.4}
                  dot={false}
                  connectNulls
                />
              ))}
              {comparador.data?.datos.benchmark && (
                <Line
                  type="monotone"
                  dataKey={comparador.data.datos.benchmark.ticker}
                  stroke="#5d6679"
                  strokeWidth={1.2}
                  strokeDasharray="5 4"
                  dot={false}
                  connectNulls
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <EmptyState titulo="Sin datos para ese rango" />
        )}
      </Card>

      {/* métricas del período */}
      {habilitado && comparador.data && comparador.data.datos.tabla.length > 0 && (
        <Card titulo="Métricas del período">
          <DataTable
            columnas={columnas}
            filas={comparador.data.datos.tabla}
            clavePor={(f) => f.ticker}
          />
        </Card>
      )}
    </div>
  )
}
