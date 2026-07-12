import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useApi } from '../lib/api'
import type { DatosHistorial } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { StatTile } from '../componentes/StatTile'
import { DataTable, type Columna } from '../componentes/DataTable'
import { EmptyState, ErrorCarga, EsqueletoCard, EsqueletoTabla, EsqueletoTiles } from '../componentes/EmptyState'
import { fechaCorta, fechaHoraChile } from '../lib/tiempo'

// ============================================================
// /historial — la integridad de la medición. El track record se muestra
// tal cual está: si hay 0 verificaciones, se dice cuándo puede existir la
// primera. Los estados de auditoría (legacy, no_verificable_timing) no se
// borran ni se esconden.
// ============================================================

type Fila = Record<string, string | number | null>

const num = (v: string | number | null, dec = 2) =>
  v == null ? '—' : typeof v === 'number' ? v.toFixed(dec) : v

export function Historial() {
  const { data, isLoading, error, refetch } = useApi<DatosHistorial>('/historial')

  if (isLoading)
    return (
      <div className="mx-auto grid max-w-6xl gap-4">
        <EsqueletoTiles />
        <EsqueletoCard alto="h-48" />
        <div className="grid gap-4 lg:grid-cols-2">
          <EsqueletoTabla filas={6} />
          <EsqueletoCard alto="h-64" />
        </div>
      </div>
    )
  if (error) return <ErrorCarga mensaje={String(error)} alReintentar={() => refetch()} />
  if (!data) return null
  const d = data.datos

  const columnasUltimas: Columna<Fila>[] = [
    { clave: 'Fecha', titulo: 'Señal', render: (f) => <span className="num">{f['Fecha']}</span> },
    { clave: 'Ticker', titulo: 'Ticker', render: (f) => <span className="num text-text-1">{f['Ticker']}</span> },
    {
      clave: 'est',
      titulo: 'Estimado %',
      alinear: 'der',
      render: (f) => {
        const v = f['Estimado %'] as number | null
        return v == null ? '—' : (
          <span className={v >= 0 ? 'text-pos' : 'text-neg'}>{v >= 0 ? '+' : ''}{v.toFixed(2)}</span>
        )
      },
    },
    { clave: 'gap', titulo: 'Gap real %', alinear: 'der', render: (f) => num(f['Gap real %']) },
    { clave: 'ses', titulo: 'Sesión real %', alinear: 'der', render: (f) => num(f['Sesión real %']) },
    {
      clave: 'ag',
      titulo: 'Gap ✓',
      alinear: 'der',
      render: (f) => (f['Acierto gap'] == null ? '—' : f['Acierto gap'] ? 'sí' : 'no'),
    },
    {
      clave: 'as',
      titulo: 'Sesión ✓',
      alinear: 'der',
      render: (f) => (f['Acierto sesión'] == null ? '—' : f['Acierto sesión'] ? 'sí' : 'no'),
    },
    {
      clave: 'emitida',
      titulo: 'Emitida (Chile)',
      render: (f) =>
        f['Emitida (UTC)'] ? (
          <span className="num text-text-3">{fechaHoraChile(String(f['Emitida (UTC)']))}</span>
        ) : (
          '—'
        ),
    },
  ]

  const columnasSnapshots: Columna<Fila>[] = [
    { clave: 'Fecha', titulo: 'Fecha', render: (f) => <span className="num">{f['Fecha']}</span> },
    { clave: 'Origen', titulo: 'Origen', render: (f) => f['Origen'] },
    {
      clave: 'emitido',
      titulo: 'Emitido (Chile)',
      render: (f) =>
        f['Emitido (UTC)'] ? (
          <span className="num text-text-3">{fechaHoraChile(String(f['Emitido (UTC)']))}</span>
        ) : (
          '—'
        ),
    },
    { clave: 'Versión', titulo: 'Versión', render: (f) => <span className="num">{f['Versión']}</span> },
  ]

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      {/* el estado de la medición en cifras */}
      <Card className="capa-1">
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
          <StatTile
            etiqueta="Acierto gap (30d)"
            valor={d.metricas.suficiente ? `${d.metricas.gap!.pct_aciertos}%` : `${d.metricas.n}/${d.metricas.minimo}`}
            detalle={
              d.metricas.suficiente
                ? `MAE ${d.metricas.gap!.mae_pp} pp · n=${d.metricas.n}`
                : d.primera_verificacion_posible
                  ? `en maduración — 1ª verificación posible: ${fechaCorta(d.primera_verificacion_posible)}`
                  : 'sin predicciones selladas pendientes'
            }
          />
          <StatTile
            etiqueta="Acierto sesión (30d)"
            valor={d.metricas.suficiente ? `${d.metricas.retorno_sesion!.pct_aciertos}%` : `${d.metricas.n}/${d.metricas.minimo}`}
            detalle={
              d.metricas.suficiente
                ? `MAE ${d.metricas.retorno_sesion!.mae_pp} pp`
                : `${d.pendientes_en_maduracion} predicciones madurando`
            }
          />
          <StatTile
            etiqueta="Calibración 80%"
            valor={d.calibracion.suficiente ? `${d.calibracion.cobertura_pct}%` : 'pendiente'}
            detalle={
              d.calibracion.suficiente
                ? `n=${d.calibracion.n} — ideal: 80%`
                : `n=${d.calibracion.n}/${d.calibracion.minimo}`
            }
          />
          <StatTile
            etiqueta="Puntaje IA vs ret. 5d"
            valor={d.puntaje_ia.suficiente ? (d.puntaje_ia.correlacion ?? '—') : 'pendiente'}
            detalle={
              d.puntaje_ia.suficiente
                ? `tercio alto ${d.puntaje_ia.retorno_tercio_alto}% vs bajo ${d.puntaje_ia.retorno_tercio_bajo}% · n=${d.puntaje_ia.n}`
                : `n=${d.puntaje_ia.n} verificaciones a 5 días`
            }
          />
        </div>
      </Card>

      {/* evolución de aciertos */}
      <Card titulo="Evolución de aciertos por día" className="capa-2">
        {d.evolucion.length > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={d.evolucion} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <CartesianGrid stroke="#161b26" vertical={false} />
              <XAxis
                dataKey="Fecha"
                tick={{ fill: '#5d6679', fontSize: 10, fontFamily: 'JetBrains Mono' }}
                tickLine={false}
                axisLine={{ stroke: '#222939' }}
              />
              <YAxis
                domain={[0, 100]}
                unit="%"
                tick={{ fill: '#5d6679', fontSize: 10, fontFamily: 'JetBrains Mono' }}
                tickLine={false}
                axisLine={false}
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
              />
              <Line type="monotone" dataKey="% Aciertos gap" stroke="#7dd3fc" strokeWidth={1.4} dot={{ r: 2 }} />
              <Line type="monotone" dataKey="% Aciertos sesión" stroke="#f9a8d4" strokeWidth={1.4} dot={{ r: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <EmptyState
            titulo="Aún no hay verificaciones"
            detalle={
              d.primera_verificacion_posible
                ? `La primera puede existir el ${fechaCorta(d.primera_verificacion_posible)}: cuando abra la sesión objetivo de las predicciones selladas.`
                : 'No hay predicciones selladas esperando verificación.'
            }
          />
        )}
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* últimas verificaciones */}
        <Card titulo="Últimas verificaciones" className="capa-3">
          {d.ultimas.length > 0 ? (
            <DataTable
              columnas={columnasUltimas}
              filas={d.ultimas}
              clavePor={(f) => `${f['Fecha']}-${f['Ticker']}`}
            />
          ) : (
            <EmptyState
              titulo="Sin verificaciones registradas todavía"
              detalle="La primera existirá cuando cierre la sesión objetivo de una predicción sellada y el verificador corra con datos."
            />
          )}
        </Card>

        <div className="grid gap-4">
          {/* auditoría de estados */}
          <Card titulo="Auditoría — predicciones por estado" className="capa-3">
            <ul className="divide-y divide-border text-xs">
              {d.estados.map((e) => (
                <li key={e.Estado} className="flex justify-between py-2">
                  <span className="text-text-2">{e.Estado}</span>
                  <span className="num text-text-1">{e.N}</span>
                </li>
              ))}
            </ul>
            <p className="mt-2 border-t border-border pt-2 text-[11px] leading-relaxed text-text-3">
              legacy y no_verificable_timing quedan fuera de todas las métricas,
              pero no se borran: son parte de la historia del experimento.
            </p>
          </Card>

          {/* snapshots emitidos */}
          <Card titulo="Snapshots emitidos" className="capa-3">
            {d.snapshots.length > 0 ? (
              <DataTable
                columnas={columnasSnapshots}
                filas={d.snapshots}
                clavePor={(f) => String(f['Fecha'])}
              />
            ) : (
              <EmptyState
                titulo="Sin snapshots registrados"
                detalle="El primero se sella a las 18:15 de un día hábil (launchd) o al abrir el dashboard Streamlit."
              />
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
