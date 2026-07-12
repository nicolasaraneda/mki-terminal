import { Link, useParams } from 'react-router-dom'
import { useApi } from '../lib/api'
import type { DatosDetalle } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { StatTile } from '../componentes/StatTile'
import { SignalBadge } from '../componentes/SignalBadge'
import { CandleChart } from '../componentes/CandleChart'
import { NewsSentiment } from '../componentes/NewsSentiment'
import { EmptyState, ErrorCarga, EsqueletoCard } from '../componentes/EmptyState'
import { rangoIntervalo80 } from '../lib/formato'

// ============================================================
// /detalle/:ticker — la ficha de un instrumento: velas de 1 año en moneda
// local, métricas del ranking, señal de apertura vigente (si es mercado
// por abrir), noticias con matching estricto y correlaciones principales.
// ============================================================

export function Detalle() {
  const { ticker } = useParams<{ ticker: string }>()
  const { data, isLoading, error, refetch } = useApi<DatosDetalle>(`/detalle/${ticker}`)

  if (isLoading)
    return (
      <div className="mx-auto grid max-w-6xl gap-4">
        <EsqueletoCard alto="h-8" conTitulo={false} />
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2"><EsqueletoCard alto="h-[340px]" /></div>
          <div className="grid content-start gap-4">
            <EsqueletoCard alto="h-40" />
            <EsqueletoCard alto="h-32" />
          </div>
        </div>
      </div>
    )
  if (error) return <ErrorCarga mensaje={String(error)} alReintentar={() => refetch()} />
  if (!data) return null
  const d = data.datos
  const m = d.metricas

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      {/* perfil */}
      <Card className="capa-1">
        <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
          <h1 className="font-display text-xl font-semibold text-text-1">
            {d.perfil.nombre}
          </h1>
          <span className="num text-sm text-text-3">{d.perfil.ticker}</span>
          <span className="text-xs text-text-2">{d.perfil.segmento}</span>
          <span className="num text-xs text-text-3">
            {d.perfil.exchange ?? '—'} · {d.perfil.moneda}
            {d.perfil.nivel != null && ` · eslabón ${d.perfil.nivel}`}
          </span>
          {d.perfil.duplicado_de && (
            <span className="text-xs text-warn">
              ADR — duplica a{' '}
              <Link to={`/detalle/${d.perfil.duplicado_de}`} className="underline">
                {d.perfil.duplicado_de}
              </Link>{' '}
              (fuera del ranking)
            </span>
          )}
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* velas */}
        <Card
          titulo={`Último año (${d.perfil.moneda}, diario)`}
          className="lg:col-span-2 capa-2"
        >
          {d.ohlc.length > 0 ? (
            <CandleChart velas={d.ohlc} alto={340} />
          ) : (
            <EmptyState
              titulo="Sin datos OHLC disponibles"
              detalle="Yahoo no entregó velas para este ticker — suele reaparecer al recargar más tarde."
            />
          )}
        </Card>

        <div className="grid content-start gap-4">
          {/* señal vigente si aplica */}
          {d.senal_apertura && (
            <Card titulo="Señal de apertura vigente" className="capa-2">
              <SignalBadge
                titulo={`${d.senal_apertura.estimado_pct >= 0 ? '+' : ''}${d.senal_apertura.estimado_pct.toFixed(2)}% próxima apertura`}
                direccion={d.senal_apertura.estimado_pct >= 0 ? 'pos' : 'neg'}
                magnitud={rangoIntervalo80(d.senal_apertura.estimado_pct, d.senal_apertura.intervalo80_pp)}
                porque={`β=${d.senal_apertura.beta.toFixed(2)} sobre el último movimiento real del SOX${d.senal_apertura.zona_earnings ? ` · zona de earnings (${d.senal_apertura.dias_earnings}d)` : ''}`}
                nMuestra={d.senal_apertura.n_muestra}
                r2={d.senal_apertura.r2_historico}
                emitidaUtc={d.senal_apertura.emitida_utc}
              />
            </Card>
          )}

          {/* métricas del ranking */}
          <Card titulo="Métricas (ranking v0)" className="capa-2">
            {m ? (
              <div className="grid grid-cols-2 gap-4">
                <StatTile
                  etiqueta="Puntaje v0"
                  valor={m['Puntaje v0'] != null ? Number(m['Puntaje v0']).toFixed(2) : '—'}
                  detalle="momentum + tendencia − volatilidad"
                />
                <StatTile
                  etiqueta="Retorno 6m (USD)"
                  valor={m['Retorno período %'] != null ? `${Number(m['Retorno período %']) >= 0 ? '+' : ''}${Number(m['Retorno período %']).toFixed(1)}` : '—'}
                  sufijo="%"
                  tono={Number(m['Retorno período %']) >= 0 ? 'pos' : 'neg'}
                  detalle={
                    m['Momentum 20d %'] != null
                      ? `mom. 20d ${Number(m['Momentum 20d %']) >= 0 ? '+' : ''}${Number(m['Momentum 20d %']).toFixed(1)}% · vol ${Number(m['Volatilidad anual %']).toFixed(0)}%`
                      : undefined
                  }
                />
                <StatTile
                  etiqueta="Sentimiento IA"
                  valor={
                    d.sentimiento != null
                      ? `${d.sentimiento >= 0 ? '+' : ''}${d.sentimiento.toFixed(2)}`
                      : '—'
                  }
                  tono={
                    d.sentimiento == null
                      ? 'neutro'
                      : d.sentimiento > 0.15
                        ? 'pos'
                        : d.sentimiento < -0.15
                          ? 'neg'
                          : 'neutro'
                  }
                  detalle="ponderado por frescura y relevancia"
                />
                <StatTile
                  etiqueta="Buzz"
                  valor={d.buzz ? `${d.buzz.hoy} hoy` : '—'}
                  detalle={
                    d.buzz
                      ? `${d.buzz.promedio_diario.toFixed(1)}/día habitual${d.buzz.buzz ? ' · EN BUZZ' : ''}`
                      : 'sin noticias en cache'
                  }
                />
              </div>
            ) : (
              <EmptyState titulo="Fuera del ranking (índice, FX o commodity)" />
            )}
          </Card>

          {/* correlaciones */}
          <Card titulo="Correlaciones principales (USD, diario)" className="capa-3">
            {d.correlaciones_top.length > 0 ? (
              <ul className="divide-y divide-border text-xs">
                {d.correlaciones_top.map((c) => (
                  <li key={c.ticker} className="flex justify-between py-2">
                    <Link to={`/detalle/${c.ticker}`} className="text-text-2 hover:text-text-1">
                      {c.nombre}
                    </Link>
                    <span className="num text-text-1">{c.corr.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState
                titulo="Sin correlaciones calculables"
                detalle="Requieren retornos superpuestos con el resto del universo — llegan con más historia descargada."
              />
            )}
          </Card>
        </div>
      </div>

      {/* noticias de la entidad */}
      <Card titulo="Noticias (matching estricto de entidad)" className="capa-3">
        {d.noticias.length > 0 ? (
          <NewsSentiment titulares={d.noticias} />
        ) : (
          <EmptyState
            titulo="Sin titulares que mencionen a esta empresa de forma inequívoca"
            detalle="Regla 4.6: un titular ambiguo jamás aparece en la ficha equivocada."
          />
        )}
      </Card>
    </div>
  )
}
