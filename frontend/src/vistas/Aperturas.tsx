import { Link } from 'react-router-dom'
import { useAperturas } from '../lib/api'
import { Card } from '../componentes/Card'
import { StatTile } from '../componentes/StatTile'
import { DataTable, type Columna } from '../componentes/DataTable'
import { Cargando, EmptyState, ErrorCarga } from '../componentes/EmptyState'
import { fechaCorta, fechaHoraChile, horaChile } from '../lib/tiempo'
import type { Prediccion } from '../lib/tipos'

// ============================================================
// /aperturas — el anticipador. Cada fila es una predicción con su
// incertidumbre completa y, si está sellada, su timestamp de emisión:
// la garantía anti look-ahead es texto visible, no un tooltip.
// ============================================================

const pct = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(2)}`

export function Aperturas() {
  const { data, isLoading, error } = useAperturas()

  if (isLoading)
    return (
      <div className="mx-auto grid max-w-6xl gap-4">
        <Cargando alto="h-20" />
        <Cargando alto="h-64" />
      </div>
    )
  if (error) return <ErrorCarga mensaje={String(error)} />
  if (!data) return null
  const d = data.datos

  const columnas: Columna<Prediccion>[] = [
    {
      clave: 'ticker',
      titulo: 'Acción',
      render: (p) => (
        <Link to={`/detalle/${p.ticker}`} className="hover:underline">
          <span className="text-text-1">{p.nombre}</span>{' '}
          <span className="num text-text-3">{p.ticker}</span>
        </Link>
      ),
    },
    { clave: 'mercado', titulo: 'Mercado', render: (p) => p.mercado },
    {
      clave: 'sesion',
      titulo: 'Sesión objetivo',
      render: (p) =>
        p.sesion_objetivo ? (
          <span className="num">
            {p.sesion_objetivo}
            {p.apertura_objetivo_utc && (
              <span className="text-text-3">
                {' '}
                · abre {horaChile(p.apertura_objetivo_utc)} CL
              </span>
            )}
          </span>
        ) : (
          '—'
        ),
    },
    {
      clave: 'estimado',
      titulo: 'Estimado',
      alinear: 'der',
      render: (p) => (
        <span className={p.estimado_pct >= 0 ? 'text-pos' : 'text-neg'}>
          {pct(p.estimado_pct)}%
        </span>
      ),
    },
    {
      clave: 'int80',
      titulo: '± 80%',
      alinear: 'der',
      tooltip:
        'Intervalo central del 80%: 8 de cada 10 gaps reales deberían caer dentro de estimado ± este semiancho.',
      render: (p) => `${p.intervalo80_pp.toFixed(1)} pp`,
    },
    { clave: 'beta', titulo: 'β', alinear: 'der', render: (p) => p.beta.toFixed(2) },
    {
      clave: 'r2',
      titulo: 'R² hist',
      alinear: 'der',
      render: (p) => p.r2_historico.toFixed(2),
    },
    { clave: 'n', titulo: 'n', alinear: 'der', render: (p) => p.n_muestra },
    {
      clave: 'senal',
      titulo: 'Señal',
      tooltip:
        'Derivada SOLO del R² histórico de la regresión de contagio: débil (R² < 0.10) · moderada (0.10–0.25) · fuerte (> 0.25).',
      render: (p) => (
        <span
          className={
            p.senal === 'fuerte'
              ? 'text-text-1'
              : p.senal === 'moderada'
                ? 'text-text-2'
                : 'text-text-3'
          }
        >
          {p.senal === 'debil' ? 'débil' : p.senal}
          {p.zona_earnings && (
            <span
              className="ml-1 text-warn"
              title="A menos de 5 días de resultados: el estimado no incorpora el anuncio"
            >
              · earnings {p.dias_earnings}d
            </span>
          )}
        </span>
      ),
    },
    {
      clave: 'emision',
      titulo: 'Emisión',
      render: (p) =>
        p.sellada && p.emitida_utc ? (
          <span className="num text-text-3">
            sellada {fechaHoraChile(p.emitida_utc)}
          </span>
        ) : (
          <span className="text-warn">viva (sin sellar)</span>
        ),
    },
  ]

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      <Card>
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
          <StatTile
            etiqueta="SOX usado"
            valor={d.sox_usado ? `${pct(d.sox_usado.mov_pct)}` : '—'}
            sufijo="%"
            tono={d.sox_usado ? (d.sox_usado.mov_pct >= 0 ? 'pos' : 'neg') : 'neutro'}
            detalle={
              d.sox_usado
                ? `último movimiento real · ${fechaCorta(d.sox_usado.fecha)}`
                : undefined
            }
          />
          <StatTile
            etiqueta="Ventana de betas"
            valor={d.ventana_betas}
            sufijo="sesiones"
            detalle="regresión SOX(t−1) → acción(t)"
          />
          <StatTile
            etiqueta="Calibración 80%"
            valor={
              d.calibracion.suficiente ? `${d.calibracion.cobertura_pct}%` : 'pendiente'
            }
            detalle={
              d.calibracion.suficiente
                ? `cobertura empírica · n=${d.calibracion.n}`
                : `n=${d.calibracion.n}/${d.calibracion.minimo} — sin datos suficientes`
            }
          />
          <StatTile
            etiqueta="Predicciones"
            valor={d.predicciones.length}
            detalle={`${d.predicciones.filter((p) => p.sellada).length} selladas en snapshot`}
          />
        </div>
      </Card>

      <Card titulo="Predicciones de apertura vigentes">
        {d.predicciones.length > 0 ? (
          <>
            <DataTable
              columnas={columnas}
              filas={d.predicciones}
              clavePor={(p) => p.ticker}
            />
            <p className="mt-3 border-t border-border pt-2 text-[11px] leading-relaxed text-text-3">
              Una predicción sellada quedó registrada con timestamp UTC ANTES de
              la apertura que intenta anticipar — solo esas entran al track
              record. El intervalo ±80% significa que 8 de cada 10 gaps
              deberían caer dentro; la calibración de arriba mide si eso se
              cumple en la práctica.
            </p>
          </>
        ) : (
          <EmptyState
            titulo="Sin predicciones disponibles"
            detalle="El motor no tiene betas suficientes (mínimo 40 sesiones por acción) o no hay movimiento del SOX que propagar."
          />
        )}
      </Card>
    </div>
  )
}
