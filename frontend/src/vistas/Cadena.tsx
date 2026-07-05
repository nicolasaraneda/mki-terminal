import { Link } from 'react-router-dom'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useApi } from '../lib/api'
import type { DatosCadena } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { Sparkline } from '../componentes/Sparkline'
import { SignalBadge } from '../componentes/SignalBadge'
import { Cargando, EmptyState, ErrorCarga } from '../componentes/EmptyState'

// ============================================================
// /cadena — la tesis del producto: roca → chip → data center.
// Momentum por eslabón, el índice Roca→Chip y las divergencias entre
// competidores directos (residualizadas: sin el arrastre de índice/moneda).
// ============================================================

const pct = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(1)}`

export function Cadena() {
  const { data, isLoading, error } = useApi<DatosCadena>('/cadena')

  if (isLoading)
    return (
      <div className="mx-auto grid max-w-6xl gap-4">
        <Cargando alto="h-40" />
        <Cargando alto="h-64" />
      </div>
    )
  if (error) return <ErrorCarga mensaje={String(error)} />
  if (!data) return null
  const d = data.datos

  const serieRoca =
    d.roca_chip?.serie.fechas.map((f, i) => ({
      fecha: f,
      valor: d.roca_chip!.serie.valores[i],
    })) ?? []

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      {/* eslabones de la cadena, de la roca al data center */}
      <Card titulo="Eslabones — momentum 20 días (USD)">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {d.niveles.map((n) => (
            <div key={n.nivel} className="rounded border border-border bg-bg-2 p-3">
              <p className="text-[11px] font-medium uppercase tracking-wider text-text-3">
                {n.nivel}. {n.nombre}
              </p>
              <p
                className={`num mt-1 text-xl ${
                  n.momentum_20d_pct >= 0 ? 'text-pos' : 'text-neg'
                }`}
              >
                {pct(n.momentum_20d_pct)}%
              </p>
              <Sparkline valores={n.sparkline} ancho={140} alto={24} />
              <p className="mt-2 text-[11px] leading-relaxed text-text-3">
                {n.tickers.map((t, i) => (
                  <span key={t.ticker}>
                    {i > 0 && ' · '}
                    <Link to={`/detalle/${t.ticker}`} className="hover:text-text-2">
                      {t.nombre}
                    </Link>
                  </span>
                ))}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Roca→Chip: serie completa */}
      <Card
        titulo="Índice Roca→Chip"
        accion={
          d.roca_chip && (
            <span className="num text-[11px] text-text-3">
              hoy: percentil {d.roca_chip.valor} · crudo {pct(d.roca_chip.crudo_pct)}%
            </span>
          )
        }
      >
        {d.roca_chip ? (
          <>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={serieRoca} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                <CartesianGrid stroke="#161b26" vertical={false} />
                <XAxis
                  dataKey="fecha"
                  tick={{ fill: '#5d6679', fontSize: 10, fontFamily: 'JetBrains Mono' }}
                  tickLine={false}
                  axisLine={{ stroke: '#222939' }}
                  minTickGap={60}
                />
                <YAxis
                  tick={{ fill: '#5d6679', fontSize: 10, fontFamily: 'JetBrains Mono' }}
                  tickLine={false}
                  axisLine={false}
                  unit="%"
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
                  formatter={(v) => [`${Number(v).toFixed(2)}%`, 'momentum 20d']}
                />
                <Area
                  type="monotone"
                  dataKey="valor"
                  stroke="#9aa3b7"
                  strokeWidth={1.25}
                  fill="rgba(154,163,183,0.08)"
                />
              </AreaChart>
            </ResponsiveContainer>
            <p className="mt-2 text-[11px] leading-relaxed text-text-3">
              Momentum 20d promedio de los eslabones (peso igual), en % — el
              percentil de hoy se calcula contra su último año.
            </p>
          </>
        ) : (
          <EmptyState titulo="Cadena sin datos suficientes (mínimo 3 eslabones)" />
        )}
      </Card>

      {/* divergencias entre competidores */}
      <Card titulo="Divergencias entre competidores directos">
        {d.divergencias.length > 0 ? (
          <>
            <div className="grid gap-3 sm:grid-cols-2">
              {d.divergencias
                .slice()
                .sort((a, b) => Math.abs(b.z) - Math.abs(a.z))
                .map((div) => (
                  <SignalBadge
                    key={div.par}
                    titulo={`${div.activa ? '● ' : ''}${div.par}`}
                    direccion={div.activa ? (div.spread >= 0 ? 'pos' : 'neg') : 'neutra'}
                    magnitud={`${div.spread >= 0 ? '+' : ''}${div.spread.toFixed(1)} pp residual (z=${div.z >= 0 ? '+' : ''}${div.z.toFixed(1)}) · simple ${div.spread_simple >= 0 ? '+' : ''}${div.spread_simple.toFixed(1)} pp (z=${div.z_simple >= 0 ? '+' : ''}${div.z_simple.toFixed(1)})`}
                    porque={div.explicacion}
                  />
                ))}
            </div>
            <p className="mt-3 border-t border-border pt-2 text-[11px] leading-relaxed text-text-3">
              Spread de momentum 20d sobre retornos residualizados (limpiados
              del índice local y la moneda de cada acción). ● = activa (|z| &gt; 2
              contra su propia historia).
            </p>
          </>
        ) : (
          <EmptyState titulo="Sin pares con historia suficiente (mínimo 120 sesiones)" />
        )}
      </Card>
    </div>
  )
}
