import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useApi } from '../lib/api'
import type { DatosNoticias, Instrumento } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { NewsSentiment } from '../componentes/NewsSentiment'
import { EmptyState, ErrorCarga, EsqueletoCard, EsqueletoTabla } from '../componentes/EmptyState'

// ============================================================
// /analisis — la capa de noticias IA, servida SOLO desde el cache de
// noticias.db (la API jamás llama a Anthropic). Sentimiento por acción,
// buzz, resumen del día y titulares con matching estricto por entidad.
// ============================================================

export function Analisis() {
  const [entidad, setEntidad] = useState<string>('')
  const noticias = useApi<DatosNoticias>(
    entidad ? `/noticias?entidad=${entidad}` : '/noticias',
  )
  const universo = useApi<{ instrumentos: Instrumento[] }>('/universo')

  const acciones =
    universo.data?.datos.instrumentos.filter((i) => i.tipo === 'accion') ?? []

  if (noticias.isLoading && !noticias.data)
    return (
      <div className="mx-auto grid max-w-6xl gap-4 lg:grid-cols-3">
        <div className="grid content-start gap-4 lg:col-span-2">
          <EsqueletoCard alto="h-20" />
          <EsqueletoTabla filas={8} />
        </div>
        <div className="grid content-start gap-4">
          <EsqueletoCard alto="h-56" />
          <EsqueletoCard alto="h-24" />
        </div>
      </div>
    )
  if (noticias.error)
    return <ErrorCarga mensaje={String(noticias.error)} alReintentar={() => noticias.refetch()} />
  if (!noticias.data) return null
  const d = noticias.data.datos

  const sentimientos = Object.entries(d.sentimiento_por_ticker).sort(
    (a, b) => b[1] - a[1],
  )
  const enBuzz = Object.entries(d.buzz).filter(([, b]) => b.buzz)

  return (
    <div className="mx-auto grid max-w-6xl gap-4 lg:grid-cols-3">
      <div className="grid gap-4 lg:col-span-2">
        {d.resumen_dia && (
          <Card titulo="Resumen del día (IA, desde cache)" className="capa-1">
            <p className="text-[13px] leading-relaxed text-text-2">{d.resumen_dia}</p>
          </Card>
        )}

        <Card
          titulo="Titulares analizados"
          accion={
            <select
              value={entidad}
              onChange={(e) => setEntidad(e.target.value)}
              className="rounded border border-border bg-bg-2 px-2 py-1 text-[11px] text-text-2"
            >
              <option value="">Todas las entidades</option>
              {acciones.map((a) => (
                <option key={a.ticker} value={a.ticker}>
                  {a.nombre}
                </option>
              ))}
            </select>
          }
        >
          {d.titulares.length > 0 ? (
            <NewsSentiment titulares={d.titulares} />
          ) : (
            <EmptyState
              titulo="Sin titulares en cache para esta entidad"
              detalle="Solo se muestran titulares que mencionan a la empresa de forma inequívoca (matching estricto)."
            />
          )}
        </Card>
      </div>

      <div className="grid content-start gap-4">
        <Card titulo="Sentimiento por acción" className="capa-2">
          {sentimientos.length > 0 ? (
            <ul className="divide-y divide-border text-xs">
              {sentimientos.map(([t, s]) => (
                <li key={t} className="flex items-center justify-between py-1.5">
                  <Link to={`/detalle/${t}`} className="text-text-2 hover:text-text-1">
                    {t}
                  </Link>
                  <div className="flex items-center gap-2">
                    <div className="h-1 w-24 overflow-hidden rounded bg-bg-2">
                      <div
                        className={s >= 0 ? 'h-full bg-pos/60' : 'h-full bg-neg/60'}
                        style={{
                          width: `${Math.min(Math.abs(s) * 100, 100) / 2}%`,
                          marginLeft: s >= 0 ? '50%' : `${50 - Math.min(Math.abs(s) * 100, 100) / 2}%`,
                        }}
                      />
                    </div>
                    <span className={`num w-12 text-right ${s > 0.15 ? 'text-pos' : s < -0.15 ? 'text-neg' : 'text-text-3'}`}>
                      {s >= 0 ? '+' : ''}
                      {s.toFixed(2)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              titulo="Sin sentimiento calculado en cache"
              detalle="Se llena con el próximo análisis IA (acción manual desde el dashboard Streamlit)."
            />
          )}
          <p className="mt-2 border-t border-border pt-2 text-[11px] leading-relaxed text-text-3">
            Promedio ponderado por frescura (decaimiento temporal) y relevancia
            del titular. Solo matching estricto de entidad.
          </p>
        </Card>

        <Card titulo="Buzz — volumen inusual de noticias" className="capa-3">
          {enBuzz.length > 0 ? (
            <ul className="divide-y divide-border text-xs">
              {enBuzz.map(([t, b]) => (
                <li key={t} className="flex justify-between py-1.5">
                  <Link to={`/detalle/${t}`} className="text-text-1 hover:underline">
                    {t}
                  </Link>
                  <span className="num text-text-2">
                    {b.hoy} hoy vs {b.promedio_diario.toFixed(1)}/día
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              titulo="Ninguna acción en buzz"
              detalle="Se declara buzz solo con ≥3× el ritmo habitual y base de noticias con ≥7 días de historia."
            />
          )}
        </Card>
      </div>
    </div>
  )
}
