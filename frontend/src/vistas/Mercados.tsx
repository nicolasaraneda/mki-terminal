import { Link } from 'react-router-dom'
import { useApi } from '../lib/api'
import type { DatosMercados } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { StatTile } from '../componentes/StatTile'
import { DataTable, type Columna } from '../componentes/DataTable'
import { CorrHeatmap } from '../componentes/CorrHeatmap'
import { Cargando, EmptyState, ErrorCarga } from '../componentes/EmptyState'

// ============================================================
// /mercados — cómo viaja el contagio: betas SOX(t−1) → acción(t),
// correlaciones con desfase entre eslabones, y el caso Samsung
// (correlaciona con el KOSPI hoy, pero con el SOX de AYER).
// ============================================================

type Beta = DatosMercados['betas'][number]

export function Mercados() {
  const { data, isLoading, error } = useApi<DatosMercados>('/mercados')

  if (isLoading)
    return (
      <div className="mx-auto grid max-w-6xl gap-4">
        <Cargando alto="h-64" />
        <Cargando alto="h-40" />
      </div>
    )
  if (error) return <ErrorCarga mensaje={String(error)} />
  if (!data) return null
  const d = data.datos

  const columnas: Columna<Beta>[] = [
    {
      clave: 'accion',
      titulo: 'Acción',
      render: (b) => (
        <Link to={`/detalle/${b.ticker}`} className="hover:underline">
          <span className="text-text-1">{b.nombre}</span>{' '}
          <span className="num text-text-3">{b.ticker}</span>
        </Link>
      ),
    },
    { clave: 'mercado', titulo: 'Mercado', render: (b) => b.mercado },
    {
      clave: 'beta',
      titulo: 'β contagio',
      alinear: 'der',
      render: (b) => (
        <span className="text-text-1">{b.beta.toFixed(2)}</span>
      ),
    },
    {
      clave: 'r2',
      titulo: 'R² hist',
      alinear: 'der',
      render: (b) => b.r2_historico.toFixed(2),
    },
    { clave: 'n', titulo: 'n', alinear: 'der', render: (b) => b.n_muestra },
  ]

  return (
    <div className="mx-auto grid max-w-6xl gap-4 lg:grid-cols-2">
      <Card titulo="Betas de contagio — SOX(t−1) → acción(t)" className="capa-1">
        {d.betas.length > 0 ? (
          <>
            <DataTable columnas={columnas} filas={d.betas} clavePor={(b) => b.ticker} />
            <p className="mt-3 border-t border-border pt-2 text-[11px] leading-relaxed text-text-3">
              Cuánto del movimiento de ayer del SOX se propaga a la apertura
              de cada acción asiática/europea. β=0.90 significa: si el SOX
              cayó 1%, la acción tiende a abrir −0.90%.
            </p>
          </>
        ) : (
          <EmptyState titulo="Sin betas disponibles (mínimo 40 sesiones por acción)" />
        )}
      </Card>

      <div className="grid gap-4">
        {/* el hallazgo permanente */}
        <Card titulo="Caso: el contagio viaja con el sol" className="capa-2">
          {d.caso_destacado ? (
            <>
              <p className="mb-3 text-[13px] text-text-2">
                {d.caso_destacado.nombre} correlaciona con su índice local el
                mismo día, pero con el SOX del día <em>anterior</em>:
              </p>
              <div className="grid grid-cols-3 gap-4">
                <StatTile
                  etiqueta="vs KOSPI (mismo día)"
                  valor={d.caso_destacado.corr_kospi_mismo_dia.toFixed(2)}
                  detalle={`n=${d.caso_destacado.n_sesiones} sesiones`}
                />
                <StatTile
                  etiqueta="vs SOX (mismo día)"
                  valor={d.caso_destacado.corr_sox_mismo_dia.toFixed(2)}
                  detalle="casi nada: NY aún no abre"
                />
                <StatTile
                  etiqueta="vs SOX (día anterior)"
                  valor={d.caso_destacado.corr_sox_dia_anterior.toFixed(2)}
                  detalle="ahí está el contagio"
                />
              </div>
            </>
          ) : (
            <EmptyState titulo="Sin datos suficientes para el caso destacado" />
          )}
        </Card>

        <Card titulo="Correlación entre eslabones, con desfase" className="capa-3">
          {d.correlaciones_desfase.filas.length > 0 ? (
            <>
              <CorrHeatmap
                columnas={d.correlaciones_desfase.lags.map((l) => `lag ${l}d`)}
                filas={d.correlaciones_desfase.filas}
              />
              <p className="mt-3 border-t border-border pt-2 text-[11px] leading-relaxed text-text-3">
                ¿El movimiento de un eslabón anticipa al siguiente con días de
                desfase? Correlaciones sobre retornos diarios promedio por
                eslabón (mínimo 60 sesiones por celda).
              </p>
            </>
          ) : (
            <EmptyState titulo="Sin pares de eslabones con historia suficiente" />
          )}
        </Card>
      </div>
    </div>
  )
}
